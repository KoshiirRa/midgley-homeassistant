# Midgley Home Assistant Agent Instructions

## 🐧 Global Dev Environment Directives (`dev-vm`)

All Antigravity agent sessions working on this repository MUST utilize the dedicated local Linux dev environment:

* **Host:** `dev-vm` (`10.42.42.54`), Ubuntu 26.04 LTS on hypervisor `LAB-HOST` (`10.42.42.26`).
* **SSH User & Host:** `marty@10.42.42.54`
* **Project Directory:** `/home/marty/projects/midgley-homeassistant`
* **Dev Offloading:** Run integration tests and validation workflows via SSH on `dev-vm`.
* **POSIX Pathing & LF:** Strictly enforce native Linux paths and LF line endings (`\n`).

## 🔗 Cross-Repository References
* **Core Forecasting Engine & Multi-Agent Backend:** [KoshiirRa/midgley](https://github.com/KoshiirRa/midgley)
* **Android Auto Companion:** [KoshiirRa/midgley-auto](https://github.com/KoshiirRa/midgley-auto)
* **Main Tracking Issue:** [midgley#20](https://github.com/KoshiirRa/midgley/issues/20)
* **Savings Advisor Spec:** [midgley#91](https://github.com/KoshiirRa/midgley/issues/91)

## 🌐 Architecture
The integration connects to Midgley via either static JSON CDN feeds (production) or dynamic FastAPI endpoints (dev/cloud).
