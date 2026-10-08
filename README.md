# Midgley Fuel Intelligence for Home Assistant (`midgley-homeassistant`)

[![HACS Validation](https://github.com/KoshiirRa/midgley-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/KoshiirRa/midgley-homeassistant/actions/workflows/validate.yml)
[![HACS Default](https://img.shields.io/badge/HACS-Custom_Integration-orange.svg)](https://hacs.xyz)

Home Assistant integration and Lovelace dashboard card for [Midgley](https://github.com/KoshiirRa/midgley) — the multi-agent retail unleaded fuel forecasting framework.

---

## ✨ Features

- **Freeform Location & Auto GPS Resolution:** Automatically uses your Home Assistant home coordinates (`latitude`, `longitude`) or any 5-digit US ZIP code to resolve to the nearest refining hub and PADD market.
- **5-Day ML Trend Forecasts:** Directional trajectory (`UP`, `DOWN`, `FLAT`) and confidence intervals ($/gal).
- **Smart Fill-Up Advisor:** Actionable guidance (`🔴 FILL UP NOW` vs `🔵 WAIT TO FILL`) calculating expected savings based on your vehicle's tank size.
- **Automations Ready:** `binary_sensor.midgley_fill_recommendation` turns `on` prior to weekend or supply-chain price surges to ping your phone before prices spike.
- **Lovelace Custom Card:** High-contrast dashboard card (`midgley-gas-card.js`) with status pill and price differentials.
- **Zero-Cloud Dependency (Static CDN):** By default, runs 100% off static GitHub Pages JSON feeds with client-side spatial resolution—zero infrastructure cost or API key requirement.

---

## 📦 Installation via HACS

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the three dots (top right) > **Custom repositories**.
3. Add repository URL: `https://github.com/KoshiirRa/midgley-homeassistant` with category **Integration**.
4. Click **Download**, then restart Home Assistant.
5. In **Settings** > **Devices & Services**, click **Add Integration** and search for **Midgley Fuel Intelligence**.
6. The setup flow will automatically detect your Home Assistant coordinates!

---

## 📊 Dashboard Lovelace Card

Add the card resource under **Settings** > **Dashboards** > **Resources**:
- URL: `/local/midgley-gas-card.js`
- Type: `JavaScript Module`

Example Lovelace Card YAML:
```yaml
type: custom:midgley-gas-card
title: Local Gas Advisor
entity_current: sensor.midgley_current_retail_gas_price
entity_forecast: sensor.midgley_5_day_forecast_gas_price
entity_action: sensor.midgley_fill_up_recommendation
```

---

## 🤖 Example Automation

Notify mobile devices when a gas price surge is predicted:

```yaml
alias: "Midgley: Alert to Fill Gas Tank Before Surge"
description: "Alerts drivers when fuel prices are predicted to rise sharply."
trigger:
  - platform: state
    entity_id: binary_sensor.midgley_fill_tank_advisory_alert
    to: "on"
action:
  - service: notify.notify
    data:
      title: "⛽ Gas Price Surge Warning"
      message: >
        Gas prices are projected to rise in the next 48 hours. Fill up today to save approximately
        ${{ states('sensor.midgley_potential_fill_up_savings') }} on a full tank.
```

---

## 🔗 Cross-References

- **Main Forecasting Engine:** [KoshiirRa/midgley](https://github.com/KoshiirRa/midgley)
- **Android Auto Assistant:** [KoshiirRa/midgley-auto](https://github.com/KoshiirRa/midgley-auto)
- **Tracking Issue:** [midgley#20](https://github.com/KoshiirRa/midgley/issues/20)
