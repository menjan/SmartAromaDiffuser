"""Shared base entity: one device_info, no polling, push updates from the controller."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .protocol import A326Controller


def device_info(address: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, address)},
        connections={(CONNECTION_BLUETOOTH, address)},
        name="SmartAromaDiffuser A326",
        manufacturer="A326 OEM",
        model="A326",
    )


class A326Entity(Entity):
    """Base class. unique_id = f"{address}_{suffix}" (unchanged from 0.9)."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, controller: A326Controller, address: str, suffix: str) -> None:
        self.controller = controller
        self._attr_unique_id = f"{address}_{suffix}"
        self._attr_device_info = device_info(address)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self.controller.subscribe(self.async_write_ha_state))
