"""SmartAromaDiffuser local BLE protocol for A326 (v0.11).

Protocol reference: user-provided Android HCI log, 2026-10-19.
EE03 is written, EE02 notifies. The device generates its own notification
packet number; never compare it with the host's outgoing number.

Verification improvements vs 0.10:
* app-captured status sequence: DP query followed by clock-sync then status dump
* never replay a possibly executed write on a broken connection
* ignore late disconnection callbacks from previous BLE clients
* serialize writes; validate echo and readback without changing program times
* rate-limit slider changes, and refuse intensity writes without fresh, valid DP17

Behavior:
* reuse the BLE link for a configurable idle time (default 35 seconds)
* serialize commands, and never blindly replay writes after a disconnect
* coalesce quick intensity changes; no schedules displayed or created in HA
* support explicit disconnect so the official app can connect
"""
from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient
from bleak_retry_connector import establish_connection
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_IDLE_TIMEOUT

_LOGGER = logging.getLogger(__name__)

WRITE_UUID = "0000ee03-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ee02-0000-1000-8000-00805f9b34fb"
HANDSHAKE = bytes.fromhex("01 00 0d af 00 05 01 38 38 38 38")
HANDSHAKE_REPLY = bytes.fromhex("01 00 0d 11 a1")
MASTER = bytes.fromhex("01 00 01 01")
LIGHT = bytes.fromhex("01 00 0b af 00 02 01")
PERIOD_MARKER = bytes.fromhex("17 af 00 22")
GRADE_POSITIONS = (15, 21, 27, 33)

CONNECT_TIMEOUT = 25
SLIDER_SETTLE_SECONDS = 0.35



class A326Error(HomeAssistantError):
    """Protocol-level failure that must not be retried."""


def parse_periods(snapshot: bytes) -> bytes | None:
    """Extract current 40-byte DP17 command without modifying schedule fields."""
    marker = snapshot.find(PERIOD_MARKER)
    if marker < 0 or len(snapshot) - marker < 38:
        return None
    raw = b"\x01\x00" + snapshot[marker:marker + 38]
    if len(raw) != 40 or raw[:6] != b"\x01\x00\x17\xaf\x00\x22" or raw[9] != 4:
        return None
    for start in (10, 16, 22, 28):
        if not (raw[start + 1] < 24
                and raw[start + 2] < 60 and raw[start + 3] < 24
                and raw[start + 4] < 60 and 1 <= raw[start + 5] <= 5):
            return None
    return raw


def intensity_of(raw: bytes) -> int | None:
    grades = {raw[pos] for pos in GRADE_POSITIONS}
    return grades.pop() if len(grades) == 1 else None


def with_intensity(raw: bytes, intensity: int) -> bytes:
    if not isinstance(intensity, int) or not 1 <= intensity <= 5:
        raise ValueError("Intensiteit moet een geheel getal van 1 t/m 5 zijn")
    if parse_periods(raw[2:]) != raw:
        raise ValueError("Ongeldige of onvolledige tijdschema-gegevens")
    changed = bytearray(raw)
    for pos in GRADE_POSITIONS:
        changed[pos] = intensity
    return bytes(changed)


def state_from_snapshot(snapshot: bytes) -> dict[str, bool | None]:
    result = {"master": None, "light": None}
    if snapshot.startswith(b"\x00\x0b\x00\x01\x01") and len(snapshot) > 5 and snapshot[5] in (0, 1):
        result["master"] = bool(snapshot[5])
    needle = b"\x0b\xaf\x00\x02\x01"
    off = snapshot.find(needle)
    if off >= 0 and len(snapshot) > off + len(needle) and snapshot[off + len(needle)] in (0, 1):
        result["light"] = bool(snapshot[off + len(needle)])
    return result


class A326Controller:
    """Serialize BLE operations, keep a short-lived session, read back state."""

    def __init__(self, hass, address: str, idle_timeout: int = DEFAULT_IDLE_TIMEOUT) -> None:
        self.hass = hass
        self.address = address
        self.lock = asyncio.Lock()
        self.states: dict[str, bool | int | None] = {"master": None, "light": None, "intensity": None}
        self._idle_timeout = idle_timeout
        self._client: BleakClient | None = None
        self._writer = None
        self._notify_queue: asyncio.Queue = asyncio.Queue()
        self._snapshots: dict[int, bytearray] = {}
        self._snapshot_event = asyncio.Event()
        self._snapshot: bytes | None = None
        self._snapshot_id: int | None = None
        self._sequence = 1
        self._idle_handle = None
        self._queued_operations = 0
        self._listeners: set = set()
        self._intensity_target: int | None = None

    # ------------------------------------------------------------------ misc
    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected and self._writer is not None)

    def subscribe(self, callback):
        self._listeners.add(callback)
        return lambda: self._listeners.discard(callback)

    def _notify_entities(self) -> None:
        for callback in list(self._listeners):
            callback()

    def update_options(self, idle_timeout: int) -> None:
        self._idle_timeout = idle_timeout
        if self.connected and not self.lock.locked():
            self._schedule_idle()

    def _ble_device(self):
        return bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)

    # ------------------------------------------------------------ callbacks
    def _disconnected(self, client) -> None:
        # A delayed callback for an old client must never invalidate the new link.
        if client is not self._client:
            return
        self._writer = None
        self._client = None
        self.states = {"master": None, "light": None, "intensity": None}
        self._notify_entities()
        _LOGGER.debug("SmartAromaDiffuser: Bluetooth-verbinding verbroken")

    def _received(self, _char, data) -> None:
        packet = bytes(data)
        _LOGGER.debug("SAD EE02 received: %s", packet.hex(" "))
        self._notify_queue.put_nowait(packet)
        if len(packet) < 2:
            return
        msgid, part = packet[:2]
        if part == 1:
            self._snapshots[msgid] = bytearray(packet[2:])
        elif msgid in self._snapshots and 1 < part <= 64:
            self._snapshots[msgid].extend(packet[2:])
        else:
            return
        current = bytes(self._snapshots[msgid])
        if current.startswith(b"\x00\x0b") and parse_periods(current):
            self._snapshot = current
            self._snapshot_id = msgid
            self._snapshot_event.set()
        if len(self._snapshots) > 12:
            self._snapshots = {msgid: self._snapshots[msgid]}

    async def _wait_echo(self, expected: bytes, timeout: float) -> None:
        """Match only an EXACT reply payload, never the unrelated device packet ID."""
        async with asyncio.timeout(timeout):
            while True:
                pkt = await self._notify_queue.get()
                # Packet: device-number, fragment 1, 0x00, original payload.
                if len(pkt) >= 3 and pkt[1:3] == b"\x01\x00" and pkt[3:] == expected:
                    return

    # ----------------------------------------------------------- idle logic
    def _cancel_idle(self) -> None:
        if self._idle_handle:
            self._idle_handle.cancel()
            self._idle_handle = None

    def _schedule_idle(self) -> None:
        self._cancel_idle()
        if self._idle_timeout <= 0 or not self.connected:
            return  # 0 = keep the connection permanently
        self._idle_handle = asyncio.get_running_loop().call_later(
            self._idle_timeout, self._idle_callback
        )

    def _idle_callback(self) -> None:
        self._idle_handle = None
        if self.lock.locked() or self._queued_operations:
            return  # an operation is active or queued; it reschedules the timer
        self.hass.async_create_background_task(self._idle_close(), "smartaromadiffuser_idle_close")

    async def _idle_close(self) -> None:
        async with self.lock:
            if self._idle_handle is not None or self._queued_operations:
                return  # activity happened or a new command is queued
            _LOGGER.debug("SAD: inactief, verbinding wordt gesloten")
            await self._close()

    async def _close(self) -> None:
        self._cancel_idle()
        client = self._client
        self._client = None
        self._writer = None
        if client is not None:
            try:
                if client.is_connected:
                    await asyncio.wait_for(client.disconnect(), timeout=5)
            except Exception:  # noqa: BLE001
                _LOGGER.debug("SAD disconnect mislukt", exc_info=True)

    def _drain(self) -> None:
        while not self._notify_queue.empty():
            self._notify_queue.get_nowait()

    def _next_seq(self) -> int:
        value = self._sequence
        self._sequence = 1 if value >= 254 else value + 1
        return value

    # ----------------------------------------------------------- connection
    async def _connect(self) -> None:
        if self.connected:
            return
        await self._close()
        device = self._ble_device()
        if device is None:
            raise A326Error("A326 niet bereikbaar via Bluetooth")
        client = await asyncio.wait_for(
            establish_connection(
                BleakClient, device, "SmartAromaDiffuser A326",
                disconnected_callback=self._disconnected,
                max_attempts=2,
                ble_device_callback=self._ble_device,
            ),
            timeout=CONNECT_TIMEOUT,
        )
        self._client = client
        try:
            chars = {c.uuid.lower(): c for svc in client.services for c in svc.characteristics}
            writer, notifier = chars.get(WRITE_UUID), chars.get(NOTIFY_UUID)
            if (not writer or not notifier
                    or "write" not in writer.properties or "notify" not in notifier.properties):
                raise A326Error("EE03/EE02 Bluetooth-kanalen niet beschikbaar")
            self._notify_queue = asyncio.Queue()
            self._snapshots.clear()
            await client.start_notify(notifier, self._received)
            self._drain()
            await client.write_gatt_char(writer, b"\x01\x01\xff" + HANDSHAKE, response=True)
            await self._wait_echo(HANDSHAKE_REPLY, 4.5)
            self._writer = writer
            self._sequence = 2
            _LOGGER.debug("SAD BLE handshake geslaagd")
        except Exception:
            await self._close()
            raise

    async def _run(self, op):
        """Serialize requests, reconnect before the write, never replay a write."""
        self._queued_operations += 1
        try:
            async with self.lock:
                self._cancel_idle()
                try:
                    await self._connect()
                    return await op()
                except HomeAssistantError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    _LOGGER.debug("SAD opdracht mislukt", exc_info=True)
                    # The write may have taken effect: don't repeat blindly.
                    await self._close()
                    raise HomeAssistantError(
                        f"SmartAromaDiffuser: {str(exc) or type(exc).__name__}"
                    ) from exc
                finally:
                    self._schedule_idle()
        finally:
            self._queued_operations -= 1

    # ------------------------------------------------------------ operations
    async def _request_snapshot(self, timeout: float = 5.0) -> bytes:
        """Obtain a complete DP17 record using the sequence in the Android HCI log.

        The 3-byte DP query by itself gets a short reply; the official app also
        syncs the clock, after which the device emits the multi-part dump.
        """
        self._snapshot_event.clear()
        self._snapshot = None
        self._snapshot_id = None
        self._snapshots.clear()
        self._drain()

        # App trace: query (02 01 00), clock command, then the status fragments.
        seq = self._next_seq()
        await self._client.write_gatt_char(self._writer, bytes((seq, 1, 0)), response=True)

        now = dt_util.now()
        if not 2000 <= now.year <= 2255:
            raise A326Error("Ongeldig systeemjaar voor A326-kloksynchronisatie")
        clock = bytes((
            1, 0, 0x0A, 0xAF, 0, 7,
            now.year - 2000, now.month, now.day,
            now.isoweekday(), now.hour, now.minute, now.second,
        ))
        # The dump can arrive even if the clock echo was lost; do not require it.
        await self._send_command(clock, timeout=2.5)
        try:
            await asyncio.wait_for(self._snapshot_event.wait(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise A326Error("Geen volledige status van A326; instellingen niet gewijzigd") from exc

        snapshot = self._snapshot
        if snapshot is None:
            raise A326Error("A326-status ontbreekt")
        raw = parse_periods(snapshot)
        if raw is None:
            raise A326Error("Onvolledige A326-programmagegevens")
        for key, value in state_from_snapshot(snapshot).items():
            if value is not None:
                self.states[key] = value
        self.states["intensity"] = intensity_of(raw)
        self._notify_entities()
        return raw

    async def _send_command(self, raw: bytes, timeout: float = 2.5) -> bool:
        self._drain()
        seq = self._next_seq()
        await self._client.write_gatt_char(self._writer, bytes((seq, 1, 255)) + raw, response=True)
        try:
            await self._wait_echo(raw, timeout)
            return True
        except TimeoutError:
            _LOGGER.debug("SAD write response ontvangen, maar BLE-notificatie ontbreekt")
            return False

    async def async_refresh(self, raise_errors: bool = False) -> None:
        async def op():
            await self._request_snapshot()

        try:
            await self._run(op)
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("SAD status niet beschikbaar: %s", exc)
            if raise_errors:
                raise

    async def async_disconnect(self) -> None:
        """Release BLE for the official app and invalidate our cached UI state."""
        async with self.lock:
            await self._close()
            self.states = {"master": None, "light": None, "intensity": None}
            self._notify_entities()

    async def send(self, kind: str, value: bool) -> None:
        if kind not in ("master", "light"):
            raise A326Error("Ongeldige bediening")
        raw = (MASTER if kind == "master" else LIGHT) + bytes((int(value),))

        async def op():
            if await self._send_command(raw):
                # Device returned the exact command contents on EE02.
                self.states[kind] = bool(value)
                self._notify_entities()
                return
            # If the ACK was missed, do not send the command again.
            # Query the actual state; if that fails, state is unknown.
            try:
                await self._request_snapshot(timeout=4.0)
                if self.states[kind] is bool(value):
                    return
            except Exception as exc:  # noqa: BLE001
                _LOGGER.debug("A326 readback na ontbrekend ACK mislukt: %s", exc)
            self.states[kind] = None
            self._notify_entities()
            raise A326Error("Opdracht niet bevestigd; controleer het apparaat, herhaal niet blind")

        await self._run(op)

    async def set_intensity(self, level: int) -> None:
        """Read current four periods and ONLY replace their grade bytes."""
        level = int(level)
        if level not in range(1, 6):
            raise A326Error("Intensiteit moet van 1 t/m 5 zijn")
        self._intensity_target = level  # newest request wins (slider drags)
        # Let rapid slider changes settle *before* taking the BLE operation lock.
        await asyncio.sleep(SLIDER_SETTLE_SECONDS)
        if self._intensity_target != level:
            return

        async def op():
            if self._intensity_target != level:
                return  # superseded while waiting for the lock
            # Always reread before modifying persistent device programming.
            # Never use a cached program: it could have changed in another app.
            try:
                baseline = await self._request_snapshot(timeout=5)
            except Exception as exc:  # noqa: BLE001
                raise A326Error(
                    "Kan opgeslagen programma niet uitlezen; intensiteit NIET gewijzigd"
                ) from exc
            try:
                modified = with_intensity(baseline, level)
            except ValueError as exc:
                raise A326Error(str(exc)) from exc
            if modified == baseline:
                self.states["intensity"] = level
                self._notify_entities()
                return
            self._drain()
            seq = self._next_seq()
            frames = [
                bytes((seq, 1, 255)) + modified[:17],
                bytes((seq, 2)) + modified[17:35],
                bytes((seq, 3)) + modified[35:],
            ]
            for frame in frames:
                await self._client.write_gatt_char(self._writer, frame, response=True)
            # Device echoes this multipart command; read back the full record.
            try:
                updated = await self._request_snapshot(timeout=5)
            except Exception as exc:  # noqa: BLE001
                self.states["intensity"] = None
                self._notify_entities()
                raise A326Error("Wijziging mogelijk uitgevoerd, maar niet gecontroleerd; controleer de app") from exc
            if updated != modified:
                raise A326Error("Uitlezing wijkt af na instellen; controleer de vier tijdsblokken")
            self.states["intensity"] = level
            self._notify_entities()

        await self._run(op)

    async def async_shutdown(self) -> None:
        self._cancel_idle()
        async with self.lock:
            await self._close()


type A326ConfigEntry = ConfigEntry[A326Controller]
