# GrowTent-S3

GrowTent firmware variant for the Waveshare ESP32-S3-Relay-6CH board.

This repository is intentionally separated from the classic ESP32 GrowTent firmware to keep OTA release channels safe.

## Target hardware

- Waveshare ESP32-S3-Relay-6CH
- 6 onboard relay outputs
- USB-C flashing/debugging
- LittleFS diary storage with manual repair only
- OTA updates from this repository only: `syschelle/GrowTent-S3`

## PlatformIO environment

```bash
pio run -e esp32-s3-relay-6ch
```

USB upload:

```bash
pio run -e esp32-s3-relay-6ch -t upload
```

Full erase before first installation on a new ESP32-S3 board:

```bash
pio run -e esp32-s3-relay-6ch -t erase
pio run -e esp32-s3-relay-6ch -t upload
```

## Relay pin mapping

```text
Relay 1 -> GPIO1
Relay 2 -> GPIO2
Relay 3 -> GPIO41
Relay 4 -> GPIO42
Relay 5 -> GPIO45
Relay 6 -> GPIO46
```

## Notes

- First installation on ESP32-S3 should be done via USB, not OTA from the old ESP32 firmware channel.
- OTA checks and updates point to `https://github.com/syschelle/GrowTent-S3`.
- Default relay count is 6 for this board.
- LittleFS is not formatted automatically during boot or OTA updates.
- The RGB LED on GPIO38 is not used as a normal status LED in this build.
