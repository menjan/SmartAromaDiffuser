"""A326 ambient lamp as a HA light."""
from __future__ import annotations

from homeassistant.components.light import ColorMode, LightEntity

from .entity import A326Entity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([A326AmbientLight(entry.runtime_data, entry.data["address"])])


class A326AmbientLight(A326Entity, LightEntity):
    _attr_name = "Ingebouwde lamp"
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, controller, address):
        super().__init__(controller, address, "ambient")

    @property
    def is_on(self):
        return self.controller.states["light"]

    async def async_turn_on(self, **kwargs):
        await self.controller.send("light", True)

    async def async_turn_off(self, **kwargs):
        await self.controller.send("light", False)
