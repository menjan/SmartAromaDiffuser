# Install SmartAromaDiffuser in Home Assistant

This integration controls a compatible A326-family diffuser locally by Bluetooth Low Energy (BLE). It requires a Bluetooth adapter or ESPHome proxy that supports **active connections**.

## 1. Check Bluetooth access

- Go to **Settings → Devices & services** in Home Assistant. Confirm Bluetooth is available.
- Make sure the diffuser has power and is within Bluetooth range.
- If using ESPHome, confirm the device is online, adopted in Home Assistant, and offers a **connectable Bluetooth proxy**.

## 2. Install the integration

**Home Assistant 2026.10 or older:** install through HACS below. **From Home Assistant 2026.11:** open **Settings → Marketplace**, add this project as a *custom repository* (GitHub connection may be required), then install SmartAromaDiffuser. The same repository structure supports both.

**HACS custom repository (2026.10 or older)**

1. Install HACS if necessary using [its official instructions](https://hacs.xyz/).
2. Open **HACS → Custom repositories**. Enter `https://github.com/mennojansen84/SmartAromaDiffuser` and choose **Integration**.
3. Find and install **SmartAromaDiffuser**. Restart Home Assistant.

**Manual alternative:** download the repository ZIP, extract it and copy the `custom_components/smartaromadiffuser` folder to `/config/custom_components/smartaromadiffuser` in Home Assistant. Restart.

## 3. Find your diffuser's BLE MAC address

The setup form asks for a 6-octet BLE address such as `AA:BB:CC:DD:EE:FF`. Do **not** reuse an address from screenshots or another person's configuration. Check Home Assistant Bluetooth device information/diagnostics (UI varies by release) or use a phone-based BLE scanner such as nRF Connect near the powered-on diffuser, identifying the correct device carefully. Disconnect the manufacturer's app first if it holds the BLE connection. Addresses can be randomized on some devices.

## 4. Add SmartAromaDiffuser

1. **Settings → Devices & services → Add integration → SmartAromaDiffuser**.
2. Type the BLE address and finish setup.
3. Test the main switch and ambient lamp first.
4. **Record your original schedules** in the manufacturer's app before testing intensity 1–5. Verify schedules remain unchanged afterward.

Home Assistant does **not** edit schedules or custom timing curves in this release.

## Bluetooth troubleshooting

**`Connection lost`, intermittent commands or unavailable device**

1. Confirm the diffuser is powered and in range. Close the manufacturer's app or disconnect its active BLE session.
2. Use the **Refresh status** button and inspect **Settings → System → Logs** if necessary.
3. Confirm the Home Assistant adapter or ESPHome proxy is online. The **RSSI sensor is calculated from BLE advertisements**, so `0`, `unknown` or no recent advertising updates do not prove that an active GATT connection exists or that the link is healthy.
4. If distance/interference remains a problem, consider a compatible ESPHome **ESP32 or ESP32-C3 Bluetooth proxy placed closer to the diffuser** (a supported ESPHome smart plug may serve this purpose). It **must enable active GATT connections**, not just forwarding BLE advertisements.
5. An ESPHome configuration with an already correct device-specific setup typically needs the following components:

```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: true
```

This is **not a complete device firmware configuration**. Do not flash generic firmware onto a mains-powered smart plug. Keep the board's correct wiring, relay controls and safety configuration. See [ESPHome's Bluetooth Proxy documentation](https://esphome.io/components/bluetooth_proxy/). A nearby proxy can improve reliability but cannot guarantee that BLE will never disconnect.

**The phone app cannot connect:** press **Disconnect** in HA or wait for the **Keep connection** timeout (default 35 s). Setting the option to `0` can hold the connection indefinitely. Integration **Configure** options also include an optional poll interval.

## Upgrading older installations

The integration domain changed for v1.0.0. Make a full Home Assistant backup and follow [MIGRATION.md](../MIGRATION.md) to avoid losing references to entity IDs.

## Reporting a bug

Include your Home Assistant version, integration version, Bluetooth adapter/proxy details and relevant errors in a GitHub Issue. Remove MAC addresses, IP addresses, tokens and other private data from any log.
