"""Configure SmartAromaDiffuser on the existing BLE device."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_IDLE_TIMEOUT, CONF_POLL_INTERVAL, DEFAULT_IDLE_TIMEOUT,
    DEFAULT_POLL_INTERVAL, DOMAIN,
)


def _valid_address(address: str) -> bool:
    parts = address.split(":")
    return len(parts) == 6 and all(
        len(p) == 2 and all(c in "0123456789ABCDEF" for c in p) for p in parts
    )


class A326ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manual setup: only the Bluetooth address is needed."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return A326OptionsFlow()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            address = user_input["address"].strip().upper()
            if not _valid_address(address):
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({vol.Required("address", default=address): str}),
                    errors={"address": "invalid_address"},
                )
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"SmartAromaDiffuser ({address})", data={"address": address})
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("address"): str}),
        )


class A326OptionsFlow(config_entries.OptionsFlow):
    """Connection hold time and optional background refresh."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        opts = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_IDLE_TIMEOUT, default=opts.get(CONF_IDLE_TIMEOUT, DEFAULT_IDLE_TIMEOUT)):
                vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
            vol.Required(CONF_POLL_INTERVAL, default=opts.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)):
                vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
