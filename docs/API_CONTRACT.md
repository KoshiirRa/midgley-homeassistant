# Midgley Home Assistant API Contract

This document specifies the REST & Static JSON API contract between the midgley-homeassistant integration and midgley backend data providers.

---

## 🌐 3-Tier Gateway Architecture

The integration supports three configurable gateway tiers:

1. **Production CDN (Default):** https://koshiirra.github.io/midgley/ (Static JSON Mode with client-side spatial resolution)
2. **Dwarvenbard Cloud Gateway:** https://local-dev.dwarvenbard.com/ (Dynamic REST Mode)
3. **Dev VM Local LAN Gateway:** http://10.42.42.54:8000/ (Dynamic REST Mode)

---

## 📡 Endpoints Consumed

### 1. Static Combined Feed (Production CDN)
- **HTTP Method:** GET
- **URL Pattern:** https://koshiirra.github.io/midgley/api/v1/combined_{locale}.json
- **Supported Locales:** 
ational, 	ulsa, oakland, 
ewark, cincinnati, greenville, charlotte, port_st_lucie, ayarea
- *Note:* In Static CDN Mode, the client-side esolver.py engine automatically maps user GPS coordinates or ZIP codes to the optimal regional feed completely offline.

### 2. Dynamic Combined Endpoint (Cloud / Dev Gateway)
- **HTTP Method:** GET
- **Path:** /api/v1/combined
- **Query Parameters:**
  - lat (float, optional): Latitude coordinate (e.g. 36.1540)
  - lon (float, optional): Longitude coordinate (e.g. -95.9928)
  - zip_code (string, optional): 5-digit US ZIP code (e.g. 74103)
  - locale (string, optional, default 
ational): e.g. 	ulsa

### 3. Location Resolution Endpoint
- **HTTP Method:** GET
- **Path:** /api/v1/locations/resolve
- **Query Parameters:**
  - lat (float, optional): Latitude coordinate
  - lon (float, optional): Longitude coordinate
  - zip_code (string, optional): 5-digit US ZIP code
- **Response Schema:**
  `json
  {
     status: success,
    query_type: coordinates,
    lat: 36.1540,
    lon: -95.9928,
    distance_to_hub_miles: 0.0,
    nearest_hub: tulsa,
    resolution_tier: METRO_CLUSTER_HIT,
    is_metro_cluster_hit: true,
    locale_code: tulsa,
    region_id: Tulsa_OK,
    name: Tulsa Metro Area, OK",
 "state": "OK",
 "padd_region": "PADD 2,
    state_tax_rate_per_gal: 0.19
  }
  `

---

## 🏷️ Entity & Sensor Output Contract

| Entity ID | Type | Description |
| :--- | :--- | :--- |
| sensor.midgley_<entry_id>_current_price | Sensor (monetary) | Current observed retail pump price ($/gal). |
| sensor.midgley_<entry_id>_predicted_price_5d | Sensor (monetary) | 5-day ML predicted retail price ($/gal). |
| sensor.midgley_<entry_id>_expected_change | Sensor (monetary) | Delta over 5-day horizon ($/gal). |
| sensor.midgley_<entry_id>_direction | Sensor (state) | UP, DOWN, or FLAT. |
| sensor.midgley_<entry_id>_action | Sensor (state) | FILL_UP_NOW, WAIT_TO_FILL, or NEUTRAL. |
| sensor.midgley_<entry_id>_potential_savings | Sensor (monetary) | Estimated tank fill-up dollar savings. |
| inary_sensor.midgley_<entry_id>_fill_recommendation | Binary Sensor | on when price surge warrants filling up now. |
