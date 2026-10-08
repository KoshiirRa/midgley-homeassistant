# Midgley Home Assistant API Contract

This document specifies the REST & Static JSON API contract between the `midgley-homeassistant` integration and `midgley` backend data providers.

---

## 🌐 3-Tier Gateway Architecture

The integration supports three configurable gateway tiers:

1. **Production CDN (Default):** `https://koshiirra.github.io/midgley/` (Static JSON Mode)
2. **Dwarvenbard Cloud Gateway:** `https://local-dev.dwarvenbard.com/` (Dynamic REST Mode)
3. **Dev VM Local LAN Gateway:** `http://10.42.42.54:8000/` (Dynamic REST Mode)

---

## 📡 Endpoints Consumed

### 1. Static Combined Feed (Production CDN)
- **HTTP Method:** `GET`
- **URL Pattern:** `https://koshiirra.github.io/midgley/api/v1/combined_{locale}.json`
- **Supported Locales:** `national`, `tulsa`, `oakland`, `newark`, `cincinnati`, `greenville`, `charlotte`, `port_st_lucie`, `bayarea`

### 2. Dynamic Combined Endpoint (Cloud / Dev Gateway)
- **HTTP Method:** `GET`
- **Path:** `/api/v1/combined`
- **Query Parameters:**
  - `locale` (string, optional, default `national`): e.g. `tulsa`
  - `zip_code` (string, optional): 5-digit US ZIP code

---

## 🏷️ Entity & Sensor Output Contract

| Entity ID | Type | Description |
| :--- | :--- | :--- |
| `sensor.midgley_<locale>_current_price` | Sensor (monetary) | Current observed retail pump price ($/gal). |
| `sensor.midgley_<locale>_predicted_price_5d` | Sensor (monetary) | 5-day ML predicted retail price ($/gal). |
| `sensor.midgley_<locale>_expected_change` | Sensor (monetary) | Delta over 5-day horizon ($/gal). |
| `sensor.midgley_<locale>_direction` | Sensor (state) | `UP`, `DOWN`, or `FLAT`. |
| `sensor.midgley_<locale>_action` | Sensor (state) | `FILL_UP_NOW`, `WAIT_TO_FILL`, or `NEUTRAL`. |
| `sensor.midgley_<locale>_potential_savings` | Sensor (monetary) | Estimated tank fill-up dollar savings. |
| `binary_sensor.midgley_<locale>_fill_recommendation` | Binary Sensor | `on` when price surge warrants filling up now. |
