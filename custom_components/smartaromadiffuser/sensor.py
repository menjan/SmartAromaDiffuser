"""Passive BLE RSSI diagnostics for A326 diffusers."""
from __future__ import annotations

import time

from homeassistant.components import bluetooth
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import callback
from homeassistant.util import dt as dt_util

from .entity import A326Entity

MIN_DELTA_DBM = 3
MAX_SILENCE_S = 60


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([A326SignalSensor(entry.runtime_data, entry.data["address"])])


class A326SignalSensor(A326Entity, SensorEntity):
    """Signal from advertisements only; throttled so the recorder is not flooded."""

    _attr_name = "Bluetooth signaal"
    _attr_icon = "mdi:bluetooth"
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH

    def __init__(self, controller, address):
        super().__init__(controller, address, "rssi")
        self._address = address
        self._attr_native_value = None
        self._last_seen = None
        self._last_write = 0.0

    @property
    def extra_state_attributes(self):
        return {"address": self._address, "last_advertisement": self._last_seen}

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        @callback
        def _update(info, _change) -> None:
            now = time.monotonic()
            self._last_seen = dt_util.utcnow().isoformat()
            old = self._attr_native_value
            if old is not None and abs(info.rssi - old) < MIN_DELTA_DBM and now - self._last_write < MAX_SILENCE_S:
                return
            self._attr_native_value = info.rssi
            self._last_write = now
            self.async_write_ha_state()

        self.async_on_remove(
            bluetooth.async_register_callback(
                self.hass, _update, {"address": self._address},
                bluetooth.BluetoothScanningMode.PASSIVE,
            )
        )
