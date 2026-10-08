"""Sensor platform for Midgley Fuel Intelligence."""
from __future__ import annotations

from typing import Any, Dict, Optional
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_LOCALE
from .coordinator import MidgleyDataUpdateCoordinator

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="current_price",
        name="Current Retail Gas Price",
        native_unit_of_measurement="$/gal",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gas-station",
    ),
    SensorEntityDescription(
        key="predicted_price_5d",
        name="5-Day Forecast Gas Price",
        native_unit_of_measurement="$/gal",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-line",
    ),
    SensorEntityDescription(
        key="expected_change",
        name="Expected Price Delta",
        native_unit_of_measurement="$/gal",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:delta",
    ),
    SensorEntityDescription(
        key="direction",
        name="Forecast Trend Direction",
        icon="mdi:trending-neutral",
    ),
    SensorEntityDescription(
        key="action",
        name="Fill-Up Recommendation",
        icon="mdi:car-clock",
    ),
    SensorEntityDescription(
        key="potential_savings",
        name="Potential Fill-Up Savings",
        native_unit_of_measurement="$",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:cash-multiple",
    ),
    SensorEntityDescription(
        key="lower_95ci",
        name="Prediction Lower 95% CI",
        native_unit_of_measurement="$/gal",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:arrow-down-bold",
    ),
    SensorEntityDescription(
        key="upper_95ci",
        name="Prediction Upper 95% CI",
        native_unit_of_measurement="$/gal",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:arrow-up-bold",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Midgley sensor entities."""
    coordinator: MidgleyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    locale = entry.data[CONF_LOCALE]

    entities = [
        MidgleySensor(coordinator, entry, description, locale)
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class MidgleySensor(CoordinatorEntity[MidgleyDataUpdateCoordinator], SensorEntity):
    """Representation of a Midgley sensor."""

    def __init__(
        self,
        coordinator: MidgleyDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
        locale: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._locale = locale
        self._attr_unique_id = f"{DOMAIN}_{locale}_{description.key}"
        self._attr_has_entity_name = True

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
    def native_value(self) -> Any:
        """Return state of sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs: Dict[str, Any] = {
            "locale": self._locale,
            "target_date": self.coordinator.data.get("target_date"),
            "model_version": self.coordinator.data.get("model_version"),
        }
        if self.entity_description.key == "predicted_price_5d":
            attrs["day_1_price"] = self.coordinator.data.get("day_1_price")
            attrs["day_2_price"] = self.coordinator.data.get("day_2_price")
            attrs["day_3_price"] = self.coordinator.data.get("day_3_price")
            attrs["day_4_price"] = self.coordinator.data.get("day_4_price")
            attrs["day_5_price"] = self.coordinator.data.get("day_5_price")
        elif self.entity_description.key == "action":
            attrs["key_drivers"] = self.coordinator.data.get("key_drivers")
        return attrs
