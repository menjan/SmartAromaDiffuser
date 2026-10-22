"""SmartAromaDiffuser for A326 over local Bluetooth. Config-entry domain is unchanged."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_IDLE_TIMEOUT, CONF_POLL_INTERVAL, DEFAULT_IDLE_TIMEOUT, DEFAULT_POLL_INTERVAL,
)
from .protocol import A326ConfigEntry, A326Controller

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.LIGHT, Platform.NUMBER, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: A326ConfigEntry) -> bool:
    controller = A326Controller(
        hass, entry.data["address"],
        entry.options.get(CONF_IDLE_TIMEOUT, DEFAULT_IDLE_TIMEOUT),
    )
    entry.runtime_data = controller

    async def _stop(_event) -> None:
        await controller.async_shutdown()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _stop))
    entry.async_on_unload(entry.add_update_listener(_options_updated))

    poll = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    if poll > 0:
        async def _poll(_now) -> None:
            await controller.async_refresh()

        entry.async_on_unload(async_track_time_interval(hass, _poll, timedelta(minutes=poll)))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Initial fetch is best effort and must not delay or block HA startup.
    entry.async_create_background_task(hass, controller.async_refresh(), "smartaromadiffuser_initial_refresh")
    return True


async def _options_updated(hass: HomeAssistant, entry: A326ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: A326ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        await entry.runtime_data.async_shutdown()
    return ok
