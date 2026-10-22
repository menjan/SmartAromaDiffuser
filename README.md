# SmartAromaDiffuser

[**🇳🇱 Nederlandse installatiehandleiding**](docs/INSTALLATIE_NL.md) · [**English installation guide**](docs/INSTALLATION_EN.md) · [**Migrating from an older integration**](MIGRATION.md)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mennojansen84&repository=SmartAromaDiffuser&category=integration)

Community-maintained custom integration for **Home Assistant**, providing local **Bluetooth Low Energy (BLE)** control of a tested **A326-family aroma diffuser**. No cloud account needed for control. This project is unaffiliated with the device manufacturer. Not all diffusers marketed as A326 or supplied with the same app are guaranteed to share this protocol.

## Features

| Entity | What it does |
| --- | --- |
| Main power / **Hoofdschakelaar** | Turn scent diffusion on or off |
| Built-in lamp / **Ingebouwde lamp** | Turn the built-in lamp on or off |
| Scent intensity / **Geurintensiteit** | Select level 1–5 |
| Bluetooth signal / **Bluetooth signaal** | RSSI from received BLE advertisements (not active connection quality) |
| Refresh / **Status vernieuwen** | Request current status |
| Disconnect / **Verbinding verbreken** | Release the BLE connection so a phone app can connect |

**Out of scope for v1.0.0:** editing time schedules in Home Assistant; custom timing/intensity curves. Keep managing schedule times and days in the manufacturer's mobile app. Intensity changes preserve the existing schedule record where validation succeeds; if the record cannot be read and validated, no intensity update is sent. **Record your schedules and check them in the app after first testing intensity.**

## Install (HACS / Home Assistant Marketplace)

**Home Assistant 2026.10 or older:** use HACS as described below. **From Home Assistant 2026.11:** use **Settings → Marketplace** to add the GitHub project as a custom repository (a GitHub connection may be required), then install the integration. The repository files and `hacs.json` support both systems.

1. In Home Assistant, open **HACS** → menu **Custom repositories**.
2. Paste `https://github.com/mennojansen84/SmartAromaDiffuser` and select **Integration**.
3. Find and install **SmartAromaDiffuser**, then **restart Home Assistant**.
4. Go to **Settings → Devices & services → Add integration → SmartAromaDiffuser**.
5. Enter the **Bluetooth MAC address of your own diffuser** in `AA:BB:CC:DD:EE:FF` format. A connectable Home Assistant Bluetooth adapter or ESPHome Bluetooth proxy must be able to reach it.
6. Test the main switch and lamp first; only then try intensity.

For detailed Bluetooth setup, MAC address discovery, and proxy troubleshooting, see the linked [English guide](docs/INSTALLATION_EN.md) or [Dutch guide](docs/INSTALLATIE_NL.md).

### Manual installation

Copy the **folder** `custom_components/smartaromadiffuser/` from the repository into `/config/custom_components/smartaromadiffuser/` in Home Assistant. Restart Home Assistant and add the integration as described above. Do **not** copy the outer ZIP or rename the integration domain.

### Existing installation?

**Breaking change for users of the former integration domain.** Back up Home Assistant and follow [MIGRATION.md](MIGRATION.md). Removing/renaming the old folder without migrating the configuration entry is not sufficient.

## Bluetooth reliability

BLE range, walls, metal furniture, interfering radios, and competing app connections can cause intermittent errors such as **Connection lost**. If the built-in adapter is too far away, place a supported **ESPHome Bluetooth proxy** closer to the diffuser. A compact ESP32/ESP32-C3 device (including a compatible ESPHome smart plug) can work, **provided `bluetooth_proxy` supports `active: true`**. An advertisement-only scanner cannot send commands to the diffuser. A proxy can improve reception; it cannot guarantee that every disconnection disappears.

The default **Keep connection** option is 35 seconds; setting it to `0` holds the BLE connection continuously and can prevent the phone app from connecting. Use the disconnect button to give the phone app access. RSSI readings reflect **advertisements received by Home Assistant**, not a live measurement of the active GATT link. See [Bluetooth troubleshooting](docs/INSTALLATION_EN.md#bluetooth-troubleshooting).

## Compatibility and limitations

- Developed and tested against a single A326 protocol family using **EE03 writes** and **EE02 notifications**.
- Requires a working, **connectable** Home Assistant BLE adapter or an **active-connection** ESPHome Bluetooth proxy.
- One BLE client may temporarily block another (including the manufacturer's mobile app).
- BLE writes and state readback cannot eliminate all uncertain hardware outcomes. Verify physical response.
- `dashboard-voorbeeld.yaml` is an **example only**: replace its example entity IDs with your own.

## Support and contributions

Please [open a GitHub issue](https://github.com/mennojansen84/SmartAromaDiffuser/issues) and share the Home Assistant version, integration version, Bluetooth adapter/proxy type, and error **after removing MAC addresses, secrets, IP addresses and personal data** from logs.

## License

MIT — see [LICENSE](LICENSE).
