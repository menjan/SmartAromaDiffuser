# SmartAromaDiffuser v1.0.0

First public release for a tested A326-family Bluetooth aroma diffuser in Home Assistant.

- On/off main switch, built-in lamp and scent intensity 1–5
- Local Bluetooth control with a simple interface; no Home Assistant time-schedule editor
- Status refresh, release-connection button and Bluetooth advertisement RSSI diagnostics
- Dutch and English installation instructions, plus troubleshooting and optional ESPHome active Bluetooth proxy guidance
- Removed device-specific MAC address from the configuration form (enter your own)

**Important:** this release uses the new `smartaromadiffuser` domain. Existing users of older domain names must follow [migration guide](https://github.com/mennojansen84/SmartAromaDiffuser/blob/main/MIGRATION.md), back up Home Assistant and check entity IDs and automation references.

The BLE protocol command implementation is unchanged from the previously tested v0.11 core. Verify on your own hardware before depending on automation.
