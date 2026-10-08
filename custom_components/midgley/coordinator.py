"""DataUpdateCoordinator for Midgley Fuel Intelligence."""
from __future__ import annotations

import logging
from typing import Any, Dict
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
)

_LOGGER = logging.getLogger(__name__)


class MidgleyDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching Midgley fuel forecast data."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        locale: str,
        tank_capacity: float,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{locale}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.base_url = base_url.rstrip("/")
        self.locale = locale
        self.tank_capacity = tank_capacity
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from Midgley API or CDN feed."""
        is_static_cdn = any(
            host in self.base_url
            for host in ("github.io", "github.com", "raw.githubusercontent.com")
        )

        if is_static_cdn:
            url = f"{self.base_url}/api/v1/combined_{self.locale}.json"
            params = None
        else:
            url = f"{self.base_url}/api/v1/combined"
            params = {"locale": self.locale}

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

        # Process and enrich payload
        live = data.get("live_lookup", {})
        forecast = data.get("forecast", {})
        locale_meta = data.get("locale", {})

        current_price = live.get("current_price_per_gal")
        predicted_price = forecast.get("predicted_price_per_gal", current_price)
        expected_change = forecast.get("expected_change_dollars", 0.0)
        expected_pct = forecast.get("expected_change_percent", 0.0)
        direction = forecast.get("projected_direction", DIRECTION_FLAT)

        # Smart Fill-Up Advisor Rule:
        # If price projected to surge (+2.5% or >$0.08) -> FILL_UP_NOW
        # If price projected to drop (-2.0% or <-$0.06) -> WAIT_TO_FILL
        # Otherwise -> NEUTRAL
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

        return {
            "raw": data,
            "locale": locale_meta,
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
