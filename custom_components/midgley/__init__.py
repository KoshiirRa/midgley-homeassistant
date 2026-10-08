"""The Midgley Fuel Intelligence Home Assistant integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_LOCATION_MODE,
    CONF_LOCALE,
    CONF_TANK_CAPACITY,
    CONF_ZIP_CODE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DEFAULT_LOCATION_MODE,
    DEFAULT_LOCALE,
    DEFAULT_TANK_CAPACITY,
)
from .coordinator import MidgleyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Midgley from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = MidgleyDataUpdateCoordinator(
        hass=hass,
        base_url=entry.data[CONF_BASE_URL],
        location_mode=entry.data.get(CONF_LOCATION_MODE, DEFAULT_LOCATION_MODE),
        locale=entry.data.get(CONF_LOCALE, DEFAULT_LOCALE),
        tank_capacity=entry.data.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
        zip_code=entry.data.get(CONF_ZIP_CODE),
        latitude=entry.data.get(CONF_LATITUDE),
        longitude=entry.data.get(CONF_LONGITUDE),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Midgley config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
