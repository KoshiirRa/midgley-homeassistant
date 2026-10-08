"""Binary sensor platform for Midgley Fuel Intelligence."""
from __future__ import annotations

from typing import Any, Dict
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_LOCALE
from .coordinator import MidgleyDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Midgley binary sensor entities."""
    coordinator: MidgleyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    locale = entry.data[CONF_LOCALE]

    async_add_entities([MidgleyFillAlertBinarySensor(coordinator, entry, locale)])


class MidgleyFillAlertBinarySensor(
    CoordinatorEntity[MidgleyDataUpdateCoordinator], BinarySensorEntity
):
    """Binary sensor indicating whether a price surge necessitates filling up now."""

    def __init__(
        self,
        coordinator: MidgleyDataUpdateCoordinator,
        entry: ConfigEntry,
        locale: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._locale = locale
        self._attr_unique_id = f"{DOMAIN}_{locale}_fill_recommendation"
        self._attr_has_entity_name = True
        self.entity_description = BinarySensorEntityDescription(
            key="should_fill",
            name="Fill Tank Advisory Alert",
            device_class=BinarySensorDeviceClass.PROBLEM,
            icon="mdi:gas-station-alert",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        locale_info = self.coordinator.data.get("locale", {})
        locale_name = locale_info.get("name", self._locale.capitalize())
        return DeviceInfo(
            identifiers={(DOMAIN, self._locale)},
            name=f"Midgley Fuel Intelligence ({locale_name})",
            manufacturer="Midgley Forecasting Engine",
            model=self.coordinator.data.get("model_version", "v1.6 Ipatieff"),
            sw_version="0.1.0",
        )

    @property
    def is_on(self) -> bool:
        """Return true if price surge warrants filling up now."""
        return bool(self.coordinator.data.get("should_fill", False))

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return attributes for automation triggers."""
        return {
            "action": self.coordinator.data.get("action"),
            "expected_change_dollars": self.coordinator.data.get("expected_change"),
            "expected_change_percent": self.coordinator.data.get("expected_pct"),
            "projected_direction": self.coordinator.data.get("direction"),
            "potential_savings": self.coordinator.data.get("potential_savings"),
        }
