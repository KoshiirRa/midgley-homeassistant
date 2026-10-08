class MidgleyGasCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity_current) {
      throw new Error("Please specify entity_current (e.g. sensor.midgley_current_retail_gas_price)");
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass || !this.config) return;

    const currentEntity = this._hass.states[this.config.entity_current];
    const forecastEntity = this.config.entity_forecast ? this._hass.states[this.config.entity_forecast] : null;
    const actionEntity = this.config.entity_action ? this._hass.states[this.config.entity_action] : null;

    const currentPrice = (currentEntity && currentEntity.state && !isNaN(parseFloat(currentEntity.state)))
      ? parseFloat(currentEntity.state).toFixed(2)
      : "--.--";
    const forecastPrice = (forecastEntity && forecastEntity.state && !isNaN(parseFloat(forecastEntity.state)))
      ? parseFloat(forecastEntity.state).toFixed(2)
      : null;
    const action = actionEntity ? actionEntity.state : "NEUTRAL";

    let badgeColor = "#4caf50";
    let badgeText = "STABLE / HOLD";
    if (action === "FILL_UP_NOW") {
      badgeColor = "#f44336";
      badgeText = "🔴 FILL UP NOW";
    } else if (action === "WAIT_TO_FILL") {
      badgeColor = "#2196f3";
      badgeText = "🔵 WAIT TO FILL";
    }

    this.innerHTML = `
      <ha-card style="padding: 16px; border-radius: 12px; font-family: var(--paper-font-body1_-_font-family, sans-serif);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div style="font-size: 1.1rem; font-weight: 600; color: var(--primary-text-color);">
            ⛽ ${this.config.title || "Midgley Fuel Forecast"}
          </div>
          <span style="background-color: ${badgeColor}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
            ${badgeText}
          </span>
        </div>

        <div style="display: flex; gap: 20px; align-items: baseline; margin-top: 8px;">
          <div>
            <div style="font-size: 0.8rem; color: var(--secondary-text-color); text-transform: uppercase;">Current Pump Price</div>
            <div style="font-size: 2rem; font-weight: 700; color: var(--primary-text-color);">$${currentPrice} <span style="font-size: 1rem; font-weight: normal;">/gal</span></div>
          </div>
          ${forecastPrice ? `
          <div>
            <div style="font-size: 0.8rem; color: var(--secondary-text-color); text-transform: uppercase;">5-Day Forecast</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: var(--primary-text-color);">$${forecastPrice} <span style="font-size: 0.9rem; font-weight: normal;">/gal</span></div>
          </div>` : ''}
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 2;
  }
}

if (!customElements.get("midgley-gas-card")) {
  customElements.define("midgley-gas-card", MidgleyGasCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some(card => card.type === "midgley-gas-card")) {
  window.customCards.push({
    type: "midgley-gas-card",
    name: "Midgley Gas Card",
    preview: true,
    description: "Lovelace card for Midgley retail fuel forecasts & fill recommendations",
  });
}