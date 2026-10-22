"""A326 master power as a HA switch."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .entity import A326Entity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([A326MasterSwitch(entry.runtime_data, entry.data["address"])])


class A326MasterSwitch(A326Entity, SwitchEntity):
    _attr_name = "Hoofdschakelaar"
    _attr_icon = "mdi:power"

    def __init__(self, controller, address):
        super().__init__(controller, address, "master")

    @property
    def is_on(self):
        return self.controller.states["master"]

    async def async_turn_on(self, **kwargs):
        await self.controller.send("master", True)

    async def async_turn_off(self, **kwargs):
        await self.controller.send("master", False)
