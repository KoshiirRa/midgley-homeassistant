"""The Midgley Fuel Intelligence Home Assistant integration."""
from __future__ import annotations

import logging
from pathlib import Path
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

FRONTEND_URL = "/midgley_frontend"
CARD_FILENAME = "midgley-gas-card.js"
CARD_VERSION = "0.2.0"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the Midgley Lovelace custom card in Home Assistant frontend."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("frontend_registered"):
        return

    frontend_dir = Path(__file__).parent / "frontend"
    card_path = frontend_dir / CARD_FILENAME
    if not card_path.exists():
        _LOGGER.warning("Midgley frontend card file not found at %s", card_path)
        return

    card_url = f"{FRONTEND_URL}/{CARD_FILENAME}?v={CARD_VERSION}"

    # Register static path for serving the JS file
    try:
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths([
            StaticPathConfig(FRONTEND_URL, str(frontend_dir), cache_headers=False)
        ])
    except (ImportError, AttributeError):
        # Fallback for older Home Assistant versions
        try:
            hass.http.register_static_path(
                FRONTEND_URL,
                str(frontend_dir),
                cache_headers=False,
            )
        except Exception as err:
            _LOGGER.debug("Could not register static path via legacy API: %s", err)

    # Register with frontend so it loads automatically in Lovelace dashboards
    try:
        from homeassistant.components.frontend import add_extra_js_url
        add_extra_js_url(hass, card_url)
        _LOGGER.info("Registered Midgley custom Lovelace card: %s", card_url)
    except Exception as err:
        _LOGGER.warning("Could not automatically register extra JS url with frontend: %s", err)

    domain_data["frontend_registered"] = True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Midgley component."""
    await async_register_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Midgley from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await async_register_frontend(hass)

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
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok