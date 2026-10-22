"""Diagnostic buttons: release the BLE connection (for the official app) / refresh state."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .entity import A326Entity


async def async_setup_entry(hass, entry, async_add_entities):
    controller, address = entry.runtime_data, entry.data["address"]
    async_add_entities([A326DisconnectButton(controller, address), A326RefreshButton(controller, address)])


class A326DisconnectButton(A326Entity, ButtonEntity):
    _attr_name = "Verbinding verbreken"
    _attr_icon = "mdi:bluetooth-off"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, controller, address):
        super().__init__(controller, address, "disconnect")

    async def async_press(self) -> None:
        await self.controller.async_disconnect()


class A326RefreshButton(A326Entity, ButtonEntity):
    _attr_name = "Status vernieuwen"
    _attr_icon = "mdi:refresh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, controller, address):
        super().__init__(controller, address, "refresh")

    async def async_press(self) -> None:
        await self.controller.async_refresh(raise_errors=True)
