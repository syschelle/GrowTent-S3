# GrowTent-S3 adaptation from GrowTent v0.5.3

Status: **v0.2.0-beta.1 — hardware validation pending**.

## Provenance

- Upstream: `syschelle/GrowTent`, commit `55429b128be26f4f722bc67fdff3555f5f967a94` (v0.5.3).
- S3 baseline: `syschelle/GrowTent-S3`, commit `51753423f2cbfea1759207a4fa7ae309e3fbdb5d` (v0.1.3).
- Adaptation branch: `feat/adapt-growtent-v0.5.3`.
- A source version is not evidence of the firmware currently installed on a device.

## Retained S3 hardware contract

| Output | GPIO | Role | Generic toggle / name / schedule | Heater |
|---|---|---|---|---|
| 1 | 1 | Pump 1 | Rejected / fixed name / rejected | Rejected |
| 2 | 2 | Pump 2 | Rejected / fixed name / rejected | Rejected |
| 3 | 41 | Pump 3 | Rejected / fixed name / rejected | Rejected |
| 4 | 42 | Control relay | Supported | Supported |
| 5 | 45 | Control relay | Supported | Supported |
| 6 | 46 | Control relay | Supported | Supported |

This is the existing S3 repository's pin assignment, not a new measurement of the board. Verify CH1–CH6 physically before connecting loads. Relay logic remains active HIGH. I2C SDA=8, SCL=9; DS18B20=4; ultrasonic TRIG=16/ECHO=17. No GPIO23 status LED is driven on the S3. Eight internal storage slots remain for upstream structure compatibility; the public state contains six relay entries and the board count is always six.

## Imported behavior

The AsyncWebServer TCP/8080 dashboard/API, streamed UI and transport changes, German/English and light/dark UI, C/F presentation, grow diary/LittleFS handling, WiFi provisioning, OTA maintenance, Flood handling, Shelly devices including passive heatmat, energy offsets, schedules, HMAC backend grow-profile writes and current irrigation logic come from the pinned upstream source.

Hardware-specific differences:

- Pump indices are 0,1,2 (public relays 1,2,3), never 5,6,7.
- Dedicated manual pulses: `POST /pump/1/triggerPump10s`, `/pump/2/triggerPump10s`, `/pump/3/triggerPump10s`.
- Generic names, schedules, `/api/relay/N/state` and `/relay/N/toggle` are restricted to N=4,5,6. Pump paths through those APIs are rejected. Relays 7/8 do not exist.
- Enabled flags are checked at queued action application and at the central GPIO setter. Stop requests, an absent/busy relay mutex and other active/armed pumps prevent a pump from starting. Automatic watering aborts if the GPIO setter refuses an output. OFF remains permitted for disabled pumps.
- Schedules/heater never own pump outputs. Stale heater configurations pointing to pumps are disabled at boot.
- Read-only state: `/api/state`, with `/state` as an equivalent alias, both at TCP/8080. TCP/80 is provisioning only.
- OTA and generated manifest URLs point only to `syschelle/GrowTent-S3`. Never install a classic ESP32 image on this board.

## Settings and storage migration

Keep the existing `growtent` NVS namespace and setting keys. Preserve relay 4–6 names and their schedule keys, including the separate relay-6 start/end keys. Normalize empty/obsolete pump-default control labels as in the prior S3 code. Fixed Pump 1/2/3 names ignore old custom labels. Old 4/8 relay-count preferences cannot change the hardware layout. Newly introduced pump-enabled fields retain upstream defaults (true); check all three before the first use. HMAC remains disabled when no configuration exists.

Existing LittleFS is mounted without automatic formatting. There is no filesystem/partition upload in this change. Back up the diary and record all settings before flashing. No on-device NVS or diary migration has been verified here.

## Validation and release gates

See [TESTING.md](TESTING.md) for executed host tests and the still-open hardware gates. This beta must not be treated as a production hardware release. No tag, GitHub Release, firmware upload or merge is performed by preparing the pull request.

## First test and rollback

1. Disconnect pumps/heater and other loads. Save settings, diary, old S3 firmware and exact partition layout; keep USB access available.
2. Verify the old/new bootloader and partition layout. Existing S3 app-only OTA is appropriate only if partitions match and a tested recovery route exists. Cross-family migration from classic ESP32 always requires USB and a matching S3 image; OTA cannot replace the chip or partition layout.
3. Build with `python -m platformio run -e esp32-s3-relay-6ch`. Upload only after checking the selected board, serial port and GPIO contract. Do not erase or format a live device without its backup.
4. At `http://<device-ip>:8080`, record the actual version and six-output state; verify OFF at boot, every channel individually without loads, all negative pump guards, stop response, OTA maintenance and NVS/diary preservation.
5. If a gate fails, disconnect loads, restore the prior S3 image via the verified USB/app path, and restore settings/diary from backup as needed. New NVS fields are not a guarantee that downgrades will interpret all configuration identically. A complete rollback hardware test remains open.

## Decisions / remaining work

| Date | Decision | Reason |
|---|---|---|
| 2026-11-12 | Use v0.5.3 as a pinned upstream base | Current source comparison rather than guessing individual old migration patches |
| 2026-11-12 | Retain S3 version line; beta v0.2.0-beta.1 | Separate hardware/OTA channel and explicit validation stage |
| 2026-11-12 | Block generic control of pump channels | Prevent bypass of pump disable flags and irrigation safety logic |
| 2026-11-12 | Keep six physical outputs with internal eight-slot structures | Preserve upstream type layout without exposing nonexistent GPIOs |
| 2026-11-12 | Add a build/contract-test workflow on branches and PRs | Tag-only release workflow did not validate proposed adaptations |

Open: actual installed firmware, board hardware test, NVS/LittleFS preservation, Gen1/2/3 device matrix, live HMAC signing with backend, API burst/heap measurements, OTA/rollback on this board. The Sites release center is not automatically synchronized with GitHub by this firmware change.
