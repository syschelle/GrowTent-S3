# GrowTent-S3 v0.2.0-beta.1

## Release summary

Adapt the Waveshare ESP32-S3-Relay-6CH firmware to the pinned GrowTent v0.5.3 codebase. This is a validation beta, not a confirmed production hardware release.

## Changes

- Import AsyncWebServer TCP/8080, current UI, grow diary/LittleFS, Shelly/energy/schedules/heatmat, Flood support, HMAC backend writes and OTA maintenance from upstream.
- Preserve S3 pins and six-output layout: fixed Pump 1–3 on relays 1–3; manual controls, schedules and heater on relays 4–6.
- Reject generic pump controls and keep disabled/overlapping pumps from energizing in the central GPIO setter.
- Preserve separate relay-6 NVS scheduling keys, normalize legacy names and reject old 4/8 relay count choices.
- Adapt dashboard labels, status polling, operating settings and relay-6 controls.
- Keep S3-only firmware/manifest URLs and add build/contract-test CI.

## Compatibility

S3 hardware only. PlatformIO environment `esp32-s3-relay-6ch`, espressif32 6.11.0, board `esp32-s3-devkitc-1`. Dashboard and APIs use TCP/8080; `/api/state` and `/state` return the same state. Relays 7–8 are absent. Read `MIGRATION.md`, `TESTING.md` and `SECURITY.md` before testing. Hardware, OTA, persistence and rollback gates remain open. Do not flash the classic ESP32 binary.
