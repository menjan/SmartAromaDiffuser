"""Scent intensity (1-5) for SmartAromaDiffuser."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode

from .entity import A326Entity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([A326Intensity(entry.runtime_data, entry.data["address"])])


class A326Intensity(A326Entity, NumberEntity):
    _attr_name = "Geurintensiteit"
    _attr_icon = "mdi:tune"
    _attr_native_min_value = 1
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, controller, address):
        super().__init__(controller, address, "intensity")

    @property
    def native_value(self):
        return self.controller.states["intensity"]

    async def async_set_native_value(self, value: float) -> None:
        await self.controller.set_intensity(round(value))
