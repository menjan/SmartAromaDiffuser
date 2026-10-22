# Changelog

## 1.0.0 — first public release

- Brand-neutral `smartaromadiffuser` integration, HACS-friendly repository layout and brand icons.
- Main power (**Hoofdschakelaar**), built-in lamp, intensity 1–5, status refresh, disconnect button and RSSI diagnostics.
- Added detailed English/Dutch installation and Bluetooth troubleshooting guides, including active ESPHome Bluetooth proxy guidance.
- Removed an inadvertently hard-coded private BLE address from the default setup form; every user must enter their own device address.
- No changes to BLE protocol, write framing, verification logic or existing schedule behavior compared with the tested v0.11 core.

**Breaking change:** migration from the former technical integration domain requires backing up, removing the old config entry and reconfiguring. See [MIGRATION.md](MIGRATION.md).
