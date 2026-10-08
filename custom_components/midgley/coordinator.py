"""DataUpdateCoordinator for Midgley Fuel Intelligence."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_FLAT,
    ACTION_FILL_NOW,
    ACTION_WAIT_TO_FILL,
    ACTION_NEUTRAL,
    LOCATION_MODE_HA,
    LOCATION_MODE_ZIP,
    LOCATION_MODE_GPS,
)
from .resolver import resolve_coordinates, resolve_zip

_LOGGER = logging.getLogger(__name__)


class MidgleyDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching Midgley fuel forecast data."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        location_mode: str,
        locale: str,
        tank_capacity: float,
        zip_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> None:
        """Initialize the coordinator."""
        self.location_mode = location_mode
        self.base_url = base_url.rstrip("/")
        self.locale = locale
        self.tank_capacity = tank_capacity
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{locale}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from Midgley API or CDN feed with freeform location support."""
        is_static_cdn = any(
            host in self.base_url
            for host in ("github.io", "github.com", "raw.githubusercontent.com")
        )

        resolved_meta: Dict[str, Any] = {}
        target_locale = self.locale

        # 1. Resolve freeform location if applicable
        if self.location_mode in (LOCATION_MODE_HA, LOCATION_MODE_GPS) and self.latitude is not None and self.longitude is not None:
            resolved_meta = resolve_coordinates(self.latitude, self.longitude)
            if is_static_cdn:
                target_locale = resolved_meta.get("locale_code", "national")
        elif self.location_mode == LOCATION_MODE_ZIP and self.zip_code:
            resolved_meta = resolve_zip(self.zip_code)
            if is_static_cdn:
                target_locale = resolved_meta.get("locale_code", "national")

        # 2. Build Request URL & Params
        if is_static_cdn:
            url = f"{self.base_url}/api/v1/combined_{target_locale}.json"
            params = None
        else:
            url = f"{self.base_url}/api/v1/combined"
            params = {}
            if self.location_mode in (LOCATION_MODE_HA, LOCATION_MODE_GPS) and self.latitude is not None and self.longitude is not None:
                params["lat"] = str(self.latitude)
                params["lon"] = str(self.longitude)
            elif self.location_mode == LOCATION_MODE_ZIP and self.zip_code:
                params["zip_code"] = str(self.zip_code)
            else:
                params["locale"] = target_locale

        try:
            async with self._session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Midgley endpoint returned HTTP {resp.status} for {url}")
                data = await resp.json()
        except Exception as err:
            if self.data:
                _LOGGER.warning("Error fetching Midgley data (%s); preserving cached state", err)
                return self.data
            raise UpdateFailed(f"Error communicating with Midgley API: {err}") from err

        # Process payload
        live = data.get("live_lookup", {})
        forecast = data.get("forecast", {})
        locale_meta = data.get("locale", {})
        server_res = data.get("location_resolution") or data.get("zip_code_resolution")

        if server_res:
            resolved_meta.update(server_res)

        current_price = live.get("current_price_per_gal")
        predicted_price = forecast.get("predicted_price_per_gal", current_price)
        expected_change = forecast.get("expected_change_dollars", 0.0)
        expected_pct = forecast.get("expected_change_percent", 0.0)
        direction = forecast.get("projected_direction", DIRECTION_FLAT)

        if expected_pct >= 2.5 or expected_change >= 0.08 or direction == DIRECTION_UP:
            action = ACTION_FILL_NOW
            should_fill = True
        elif expected_pct <= -2.0 or expected_change <= -0.06 or direction == DIRECTION_DOWN:
            action = ACTION_WAIT_TO_FILL
            should_fill = False
        else:
            action = ACTION_NEUTRAL
            should_fill = False

        potential_savings = abs(expected_change * self.tank_capacity)

        # Friendly display name
        display_name = locale_meta.get("name", target_locale.capitalize())
        if resolved_meta.get("distance_miles") is not None:
            dist = resolved_meta["distance_miles"]
            display_name = f"{display_name} ({dist} mi away)"

        return {
            "raw": data,
            "locale": locale_meta,
            "resolved_meta": resolved_meta,
            "display_name": display_name,
            "current_price": current_price,
            "predicted_price_5d": predicted_price,
            "expected_change": round(expected_change, 3),
            "expected_pct": round(expected_pct, 2),
            "direction": direction,
            "action": action,
            "should_fill": should_fill,
            "potential_savings": round(potential_savings, 2),
            "lower_95ci": forecast.get("prediction_lower_95ci"),
            "upper_95ci": forecast.get("prediction_upper_95ci"),
            "target_date": forecast.get("target_date"),
            "model_version": forecast.get("model_version", "v1.6 Ipatieff"),
            "day_1_price": forecast.get("day_1_price"),
            "day_2_price": forecast.get("day_2_price"),
            "day_3_price": forecast.get("day_3_price"),
            "day_4_price": forecast.get("day_4_price"),
            "day_5_price": forecast.get("day_5_price"),
            "key_drivers": data.get("key_drivers", []),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
