"""Constants for the Midgley Fuel Intelligence integration."""
from datetime import timedelta

DOMAIN = "midgley"

CONF_GATEWAY_TIER = "gateway_tier"
CONF_BASE_URL = "base_url"
CONF_LOCATION_MODE = "location_mode"
CONF_LOCALE = "locale"
CONF_ZIP_CODE = "zip_code"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_TANK_CAPACITY = "tank_capacity"

LOCATION_MODE_HA = "home_assistant"
LOCATION_MODE_ZIP = "zip_code"
LOCATION_MODE_GPS = "gps_coordinates"
LOCATION_MODE_METRO = "predefined_metro"

TIER_PRODUCTION = "production"
TIER_DWARVENBARD = "dwarvenbard"
TIER_DEV_VM = "dev_vm"
TIER_CUSTOM = "custom"

GATEWAY_URLS = {
    TIER_PRODUCTION: "https://koshiirra.github.io/midgley",
    TIER_DWARVENBARD: "https://local-dev.dwarvenbard.com",
    TIER_DEV_VM: "http://10.42.42.54:8000",
}

DEFAULT_GATEWAY_TIER = TIER_PRODUCTION
DEFAULT_LOCATION_MODE = LOCATION_MODE_HA
DEFAULT_LOCALE = "national"
DEFAULT_TANK_CAPACITY = 15.0
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

SUPPORTED_LOCALES = {
    "national": "National Wholesale / US Average",
    "tulsa": "Tulsa Metro Area, OK",
    "oakland": "Oakland / East Bay, CA",
    "newark": "Newark Metro Area, NJ / NY Harbor",
    "cincinnati": "Cincinnati Tri-State Hub, OH/KY/IN",
    "greenville": "Greenville-Spartanburg, SC (Colonial Pipeline)",
    "charlotte": "Charlotte Metro Area, NC",
    "port_st_lucie": "Port St. Lucie / Treasure Coast, FL",
    "bayarea": "San Francisco Bay Area, CA",
}

DIRECTION_UP = "UP"
DIRECTION_DOWN = "DOWN"
DIRECTION_FLAT = "FLAT"

ACTION_FILL_NOW = "FILL_UP_NOW"
ACTION_WAIT_TO_FILL = "WAIT_TO_FILL"
ACTION_NEUTRAL = "NEUTRAL"
