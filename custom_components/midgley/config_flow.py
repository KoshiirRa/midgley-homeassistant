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
    CONF_LOCATION_MODE,
    CONF_LOCALE,
    CONF_ZIP_CODE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_TANK_CAPACITY,
    DEFAULT_GATEWAY_TIER,
    DEFAULT_LOCATION_MODE,
    DEFAULT_LOCALE,
    DEFAULT_TANK_CAPACITY,
    GATEWAY_URLS,
    LOCATION_MODE_HA,
    LOCATION_MODE_ZIP,
    LOCATION_MODE_GPS,
    LOCATION_MODE_METRO,
    SUPPORTED_LOCALES,
    TIER_CUSTOM,
)
from .resolver import resolve_coordinates, resolve_zip


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

            mode = user_input.get(CONF_LOCATION_MODE, DEFAULT_LOCATION_MODE)
            lat = user_input.get(CONF_LATITUDE)
            lon = user_input.get(CONF_LONGITUDE)
            zip_code = user_input.get(CONF_ZIP_CODE)
            locale = user_input.get(CONF_LOCALE, DEFAULT_LOCALE)

            # Determine title & unique id
            if mode == LOCATION_MODE_HA:
                lat = self.hass.config.latitude
                lon = self.hass.config.longitude
                resolved = resolve_coordinates(lat, lon)
                locale = resolved.get("locale_code", "national")
                title = f"Midgley ({self.hass.config.location_name or resolved.get('name', 'Home')})"
                unique_id = f"{DOMAIN}_ha_{round(lat, 2)}_{round(lon, 2)}"
            elif mode == LOCATION_MODE_GPS and lat is not None and lon is not None:
                resolved = resolve_coordinates(lat, lon)
                locale = resolved.get("locale_code", "national")
                title = f"Midgley ({resolved.get('name', f'{lat},{lon}')})"
                unique_id = f"{DOMAIN}_gps_{round(lat, 2)}_{round(lon, 2)}"
            elif mode == LOCATION_MODE_ZIP and zip_code:
                resolved = resolve_zip(zip_code)
                locale = resolved.get("locale_code", "national")
                title = f"Midgley (ZIP {zip_code})"
                unique_id = f"{DOMAIN}_zip_{zip_code}"
            else:
                title = f"Midgley ({SUPPORTED_LOCALES.get(locale, locale.capitalize())})"
                unique_id = f"{DOMAIN}_metro_{locale}"

            if not errors:
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_GATEWAY_TIER: tier,
                        CONF_BASE_URL: base_url,
                        CONF_LOCATION_MODE: mode,
                        CONF_LOCALE: locale,
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                        CONF_ZIP_CODE: zip_code,
                        CONF_TANK_CAPACITY: user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                    },
                )

        # Default coordinates from Home Assistant system configuration
        ha_lat = getattr(self.hass.config, "latitude", 36.1540)
        ha_lon = getattr(self.hass.config, "longitude", -95.9928)

        schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION_MODE, default=LOCATION_MODE_HA): vol.In(
                    {
                        LOCATION_MODE_HA: f"Auto: Use Home Assistant Location ({round(ha_lat, 3)}, {round(ha_lon, 3)})",
                        LOCATION_MODE_ZIP: "Enter 5-Digit US ZIP Code",
                        LOCATION_MODE_GPS: "Custom GPS Coordinates (Latitude, Longitude)",
                        LOCATION_MODE_METRO: "Select Predefined Metro Area",
                    }
                ),
                vol.Optional(CONF_ZIP_CODE, default=""): str,
                vol.Optional(CONF_LATITUDE, default=ha_lat): vol.Coerce(float),
                vol.Optional(CONF_LONGITUDE, default=ha_lon): vol.Coerce(float),
                vol.Optional(CONF_LOCALE, default=DEFAULT_LOCALE): vol.In(SUPPORTED_LOCALES),
                vol.Required(CONF_GATEWAY_TIER, default=DEFAULT_GATEWAY_TIER): vol.In(
                    {
                        "production": "Production CDN (Zero-cost, 100% SLA GitHub Pages)",
                        "dwarvenbard": "Dwarvenbard Cloud Gateway (Staging)",
                        "dev_vm": "Dev VM Local LAN (10.42.42.54:8000)",
                        "custom": "Custom URL",
                    }
                ),
                vol.Optional(CONF_BASE_URL, default=""): str,
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
