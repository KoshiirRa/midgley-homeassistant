"""Config flow for Midgley Fuel Intelligence integration."""
from __future__ import annotations

import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_GATEWAY_TIER,
    CONF_BASE_URL,
    CONF_LOCALE,
    CONF_TANK_CAPACITY,
    DEFAULT_GATEWAY_TIER,
    DEFAULT_LOCALE,
    DEFAULT_TANK_CAPACITY,
    GATEWAY_URLS,
    SUPPORTED_LOCALES,
    TIER_CUSTOM,
)


class MidgleyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Midgley."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            tier = user_input.get(CONF_GATEWAY_TIER, DEFAULT_GATEWAY_TIER)
            if tier == TIER_CUSTOM:
                base_url = user_input.get(CONF_BASE_URL, "").strip()
                if not base_url:
                    errors[CONF_BASE_URL] = "empty_url"
            else:
                base_url = GATEWAY_URLS.get(tier, GATEWAY_URLS[DEFAULT_GATEWAY_TIER])

            if not errors:
                locale = user_input.get(CONF_LOCALE, DEFAULT_LOCALE)
                title = f"Midgley ({SUPPORTED_LOCALES.get(locale, locale.capitalize())})"
                
                await self.async_set_unique_id(f"{DOMAIN}_{locale}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_GATEWAY_TIER: tier,
                        CONF_BASE_URL: base_url,
                        CONF_LOCALE: locale,
                        CONF_TANK_CAPACITY: user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_GATEWAY_TIER, default=DEFAULT_GATEWAY_TIER): vol.In(
                    {
                        "production": "Production CDN (Zero-cost, 100% SLA GitHub Pages)",
                        "dwarvenbard": "Dwarvenbard Cloud Gateway (Staging)",
                        "dev_vm": "Dev VM Local LAN (10.42.42.54:8000)",
                        "custom": "Custom URL",
                    }
                ),
                vol.Optional(CONF_BASE_URL, default=""): str,
                vol.Required(CONF_LOCALE, default=DEFAULT_LOCALE): vol.In(SUPPORTED_LOCALES),
                vol.Optional(CONF_TANK_CAPACITY, default=DEFAULT_TANK_CAPACITY): vol.Coerce(float),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get options flow handler."""
        return MidgleyOptionsFlowHandler(config_entry)


class MidgleyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Midgley."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.data
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_TANK_CAPACITY,
                    default=current.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                ): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
