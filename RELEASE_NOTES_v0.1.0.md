## v0.1.0 – Initial ESP32-S3 Relay 6CH Build

This is the first dedicated GrowTent-S3 release for the Waveshare ESP32-S3-Relay-6CH board.

### Changed
- Added a dedicated PlatformIO environment for the ESP32-S3 Relay 6CH board.
- Updated the onboard relay GPIO mapping for the Waveshare 6-channel relay hardware.
- Changed the default relay count to 6.
- Reserved the first three relays for watering pumps:
  - Pump 1 → Relay 1
  - Pump 2 → Relay 2
  - Pump 3 → Relay 3
- Kept relays 4..6 available for generic switching, minute scheduling and ESP relay heating selection.
- Added schedule persistence and API state reporting for Relay 6.
- Updated OTA checks and firmware download URLs to use the new `syschelle/GrowTent-S3` repository.
- Updated the GitHub Actions release workflow to build the ESP32-S3 firmware artifact.
- Kept LittleFS OTA-safe: no automatic filesystem formatting during boot or OTA update.

### Hardware mapping
- Relay 1: GPIO1 – Pump 1
- Relay 2: GPIO2 – Pump 2
- Relay 3: GPIO41 – Pump 3
- Relay 4: GPIO42 – general relay
- Relay 5: GPIO45 – general relay
- Relay 6: GPIO46 – general relay

### Installation note
The first installation on an ESP32-S3 board should be done via USB with a full erase and upload. Do not OTA-update an old classic ESP32 board directly into this S3 firmware channel.
