# GrowTent-S3

> ⚡ Smart, adaptive grow tent controller for ESP32-S3 6-channel relay boards with real-time climate stabilization and OTA updates

GrowTent-S3 is the ESP32-S3 version of the GrowTent controller firmware. It is based on the same web UI, automation logic, OTA flow, HAP/HomeKit integration and sensor handling as the classic GrowTent project, but is prepared for the **Waveshare ESP32-S3-Relay-6CH** hardware.

GrowTent reads temperature and humidity, computes VPD (Vapor Pressure Deficit), controls relays and Shelly devices, and provides a German/English web interface for monitoring and configuration. The system is designed for **stable long-term operation** and **minimal manual intervention**.

> **Important:** This repository is the firmware channel for ESP32-S3 relay hardware only. Classic ESP32 boards should use the original `syschelle/GrowTent` repository.

---

## 🚀 Features

- **ESP32-S3 web interface** for live status and configuration
- **Adaptive sensor smoothing (EMA)**
  - dynamic smoothing based on real-time changes
  - fast response to environmental shifts (e.g. opening tent/window)
  - stable readings in steady conditions
- **Raw vs smoothed sensor values**
  - full transparency for debugging and tuning
- **Stable VPD calculation**
  - based on smoothed values
  - reduces oscillation in control loops
- **6-channel relay board support** for Waveshare ESP32-S3-Relay-6CH
- **Relay scheduling** (minute-based within each hour)
- **Conditional relay logic** (e.g. based on light state)
- **Shelly integration**
  - Main power
  - Grow light
  - Humidifier
  - Heater
  - Fan / exhaust use cases through available relay or Shelly outputs
- **Heater control by temperature**
  - ESP relay or Shelly device
- **Irrigation support**
  - optional use of available relay channels for pump or watering actions
- **Tank level monitoring (HC-SR04)**
  - distance-based water level detection
  - usable for irrigation safety (empty tank protection)
- **Grow Diary**
  - diary storage via LittleFS
  - manual storage repair, no automatic formatting during boot/OTA
- **Built-in log buffer**
- **History and averages**
- **OTA update from GitHub Release binary**
- **Designed for stability**
  - optimized for unattended operation
  - separated OTA release channel for ESP32-S3 hardware

---

## 🌡️ Adaptive Climate Smoothing

The system uses an **adaptive exponential moving average (EMA)** to balance
stability and responsiveness of sensor readings.

### How it works

- Raw sensor values are read from the BME280
- The system calculates the difference between consecutive readings
- Based on this delta, a dynamic smoothing factor (`alpha`) is applied:
  - small changes → strong smoothing
  - large changes → fast reaction

### Example

- Stable environment → smooth values  
- Opening a window → immediate response  

### Benefits

- Reduced sensor noise  
- Stable VPD calculation  
- Faster reaction to real changes  
- Improved control behavior  

---

## Hardware

- Waveshare ESP32-S3-Relay-6CH board
- ESP32-S3 microcontroller
- 6 onboard relay channels
- Adafruit BME280 (I2C at default address `0x76`)
- DS18B20 temperature sensor support
- HC-SR04 sensor support
- Power supply appropriate for the relay board and connected loads
- Shelly devices (Gen1/Gen2/Gen3 depending on endpoint support)

### Default sensor and relay configuration in code

- BME I2C address: `0x76` (`BME_ADDR`)
- I2C SDA: `GPIO8`
- I2C SCL: `GPIO9`
- DS18B20 sensor pin: `GPIO4`
- Relay count: `6` active onboard relays
- Internal compatibility array remains sized for up to 8 relays, but relay 7/8 are disabled on the S3 6CH board

### ESP32-S3 Relay 6CH pin mapping

| Relay | Board channel | GPIO | Firmware role |
|---:|---|---:|---|
| 1 | CH1 | GPIO1 | Pump 1 |
| 2 | CH2 | GPIO2 | Pump 2 |
| 3 | CH3 | GPIO41 | Pump 3 |
| 4 | CH4 | GPIO42 | General relay |
| 5 | CH5 | GPIO45 | General relay |
| 6 | CH6 | GPIO46 | General relay |

The fixed S3 role layout is:

- Pump 1 → Relay 1
- Pump 2 → Relay 2
- Pump 3 → Relay 3
- General relay control, heating selection and minute scheduling → Relays 4–6

Disabled / not connected in this firmware build:

| Relay | GPIO |
|---:|---:|
| 7 | `-1` |
| 8 | `-1` |

### Wiring notes

- Connect BME280 SDA / SCL to the configured I2C pins (`GPIO8` / `GPIO9` by default).
- Make sure external sensors and the ESP32-S3 board share a common ground where required.
- Respect relay board voltage/current limits and electrical safety requirements.
- Do not OTA-update a classic ESP32 board into this S3 firmware channel.
- First installation on ESP32-S3 hardware should be done via USB with full erase/upload.

---

## Defaults & Constants

- AP SSID: `new growtent`
- AP password: `GT-12$34`
- Measurement interval: `30000 ms` (30 seconds)
- Default NTP server: `de.pool.ntp.org`
- Default timezone is stored as a POSIX-style timezone string and is configurable via the web UI
- Default language: `de` (German)
- Default theme: `light`
- Default units: `metric`
- Default time format: `24h`
- Default VPD targets (per phase): `{ 0.0, 0.8, 1.2, 1.4, 1.0 }`
- Phase names: `["", "Vegetative", "Flowering", "Drying"]`
- OTA release channel: `syschelle/GrowTent-S3`
- Firmware binary: `https://github.com/syschelle/GrowTent-S3/releases/latest/download/firmware.bin`

Preferences keys stored in NVS:

- `ssid` / `password` (WiFi)
- `boxName`
- `lang`
- `theme`
- `unit`
- `timeFmt`
- `ntpSrv`
- Relay names and relay settings
- Grow/run settings

Namespace: `growtent`

---

## Web UI

The web frontend is embedded in program memory and served by the ESP32-S3:

- Main page: `/` (index)
- Stylesheet: `/style.css`
- JavaScript: `/script.js`
- i18n manifest and language JSONs are served from memory
- Factory reset endpoint available via `POST /factory-reset` (form in UI)

UI highlights:

- Gauges for Temperature, Humidity and VPD
- Settings page for language, theme, date/time format, temperature unit, and NTP/timezone configuration
- Relay configuration and relay scheduling
- Shelly configuration
- System log page
- Grow Diary
- Status page
- OTA update page

The S3 version keeps the same UI concept and screenshots as the classic GrowTent project.

<img width="1702" height="1124" alt="GrowTent web UI" src="https://github.com/user-attachments/assets/5439fcfe-d08a-42a5-b105-eb2148a9d6f3" />

Languages provided (i18n):

- German (`de`)
- English (`en`)

---

## VPD Calculation

VPD (kPa) is calculated from the measured temperature (°C) and relative humidity (%) using saturation vapor pressure (svp) approximation:

```text
svp = 0.6108 * exp((17.27 * T) / (T + 237.3))
VPD = svp - (RH / 100) * svp
```

Values are updated by a background task and stored in:

- `lastTemperature`
- `lastHumidity`
- `lastVPD`

---

## Software / Libraries

- Arduino framework for ESP32-S3
- Wire (I2C)
- Adafruit_BME280
- Preferences (NVS)
- Adafruit Sensor (sensor abstraction)
- LittleFS
- ArduinoJson
- OneWire
- DallasTemperature

PlatformIO installs the required libraries from `platformio.ini`.

---

## Project Structure

- `src/main.cpp`  
  Web routes, setup, loop, initialization, OTA routes
- `src/function.h`  
  Core logic, control handlers, API builders, settings handlers
- `src/runtime.h`  
  Preferences load and HTML placeholder rendering
- `src/java_script.h`  
  Frontend behavior, status polling, UI updates
- `src/index_html.h`  
  Embedded web page template
- `src/style_css.h`  
  Embedded styles
- `src/task_Check_Sensor.h`  
  Sensor/control task
- `src/task_CheckShellyStatus.h`  
  Shelly poll task
- `src/task_Watering.h`  
  Irrigation task
- `src/ota.cpp`  
  GitHub OTA check and firmware download logic
- `.github/workflows/release-firmware.yml`  
  GitHub Actions release build workflow

All web UI assets are embedded as string literals (`PROGMEM`) and served by the device.

---

## Build & Flash

This repository uses a dedicated PlatformIO environment for the ESP32-S3 relay board:

```ini
[env:esp32-s3-relay-6ch]
```

### First installation on ESP32-S3 hardware

For a new ESP32-S3 board or when moving from a different firmware family, use USB and perform a full erase/upload:

```bash
pio run -e esp32-s3-relay-6ch -t erase
pio run -e esp32-s3-relay-6ch -t upload
```

This is important because OTA updates normally replace only the application firmware, not the bootloader or partition table.

### Normal local build

```bash
pio run -e esp32-s3-relay-6ch
```

### USB upload

```bash
pio run -e esp32-s3-relay-6ch -t upload
```

### Firmware binary location

After a successful build, the firmware binary is generated here:

```text
.pio/build/esp32-s3-relay-6ch/firmware.bin
```

---

## OTA Updates

OTA updates are loaded from this repository's GitHub Release binary:

```text
https://github.com/syschelle/GrowTent-S3/releases/latest/download/firmware.bin
```

The classic ESP32 firmware and the ESP32-S3 firmware intentionally use different repositories and release channels.

Do **not** point an ESP32-S3 device to the classic ESP32 `GrowTent` release channel, and do **not** point a classic ESP32 device to this `GrowTent-S3` release channel.

---

## Configuration & Tuning

- WiFi: You can set the device to Station mode or keep it in AP mode for direct connection.
- NTP and timezone: Set the NTP server and POSIX timezone string via the web UI.
- Relay behavior: Relays are initialized as outputs and default to OFF at startup.
- Relay names and relay behavior are configurable in the UI.
- Shelly devices can be used alongside the onboard relays.
- LittleFS is not formatted automatically during boot or OTA updates.

---

## API Endpoints

### Core

- `GET /api/state`  
  Unified state payload for frontend and external integrations.

### Control

- `POST /relay/{4..6}/toggle`  
  Generic relay toggle endpoints. In 6CH mode, relays 1..3 are reserved for pumps.
- `POST /pump/{1..3}/triggerPump10s`  
  Pump pulse endpoints for Pump 1..3.
- `POST /startWatering`
- `POST /pingTank`

### Shelly

- `POST /shelly/main/toggle`
- `POST /shelly/light/toggle`
- `POST /shelly/humidifier/toggle`
- `POST /shelly/heater/toggle`
- `POST /api/shelly/reset-energy`

### Scheduling / Settings

- `POST /api/relay/schedule/save-all`
- `POST /savesettings`
- `POST /saverunsettings`
- `POST /saveshellysettings`
- `POST /savemessagesettings`

### Diary / Filesystem

- `GET /api/diary/list`
- `POST /api/diary/add`
- `POST /api/diary/clear`
- `GET /api/fs/status`
- Manual repair is confirmation-protected and does not run automatically.

### Logs

- `GET /api/logbuffer`
- `POST /api/logbuffer/clear`
- `GET /log`

### OTA

- `GET /api/ota/check`
- `POST /api/ota/update`  
  Triggers OTA update from the configured firmware URL.

---

## ⚙️ Configuration

- WiFi: AP or Station mode
- NTP + timezone configurable via UI
- Relay logic configurable via UI
- Shelly integration configurable via UI
- Grow/run settings configurable via UI

---

## 🧪 Troubleshooting

- BME280 not found → check wiring, power and I2C address.
- Relays not switching → check the S3 relay GPIO mapping and relay board power.
- No UI → connect to AP:
  - SSID: `new growtent`
  - Password: `GT-12$34`
- LittleFS mount failed → use the manual **Clear diary / repair storage** action. The firmware does not auto-format LittleFS.
- New ESP32-S3 board does not boot correctly → perform USB erase + upload once before using OTA.
- Wrong OTA channel → verify that the firmware URL points to `syschelle/GrowTent-S3`.

---

## Release workflow

Create a release by pushing a version tag:

```bash
git add -A
git commit -m "Use relays 1-3 for pumps and 4-6 for control"
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions builds the firmware and uploads `firmware.bin` to the release.

---

## Repository split

- `syschelle/GrowTent`  
  Classic ESP32 board firmware
- `syschelle/GrowTent-S3`  
  ESP32-S3 Relay 6CH firmware

This split prevents accidental OTA cross-updates between incompatible ESP32 families.

---

## Contributing

Contributions, bug reports and improvements are welcome. Please open issues or pull requests describing the change and rationale.

---

## License

Apache-2.0

---
