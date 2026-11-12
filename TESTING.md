# Testing — GrowTent-S3 v0.2.0-beta.1

## Executed locally

- `python tests/test_s3_contract.py`: four regression groups pass. Compiles and executes the actual `setRelay` implementation with mocked GPIO/FreeRTOS; covers disabled pumps, OFF after disable, stop latch, overlap with active/armed pumps, unavailable mutex and invalid outputs. Also checks actual browser function behavior for 4/5/6-only control, six unique output elements, fixed pump names, no pump schedules and S3 API/NVS/OTA mapping guards.
- Inline JavaScript syntax check and shell syntax checks are included in the host suite.
- Full PlatformIO build: pending; update this result after the actual build completes.

Mocks do not verify electrical behavior, FreeRTOS timing, HTTP transport on ESP hardware or long-term concurrency. Existing upstream networking/security behavior was imported; it is not independently certified by these host tests.

## Reproduce

```bash
python -m pip install platformio==6.2.0
python tests/test_s3_contract.py
python -m platformio run -e esp32-s3-relay-6ch
```

Requires Python 3, Node.js and g++. `.github/workflows/build.yml` performs these checks and uploads the test firmware as an Actions artifact; the tag workflow is reserved for releases.

## Hardware gates — all OPEN until evidence is recorded

| Area | Required evidence |
|---|---|
| Boot/output mapping | CH1–CH6 pins, active polarity, all OFF at boot/reset, no phantom channels |
| S3 pump separation | Fixed names; relay 1–3 generic/schedule/heater writes rejected; disabled pump pulse and automatic start blocked; OFF always possible |
| Irrigation | Sequential enabled pumps only, no overlap, prompt stop during pulse/pause, config edits blocked while busy, auto-off and Flood behavior |
| Persistence | Existing relay 4–6 names and all three separate schedules preserved; new defaults reviewed; restart and power-cycle |
| Sensors | BME280 SDA8/SCL9, DS18B20 GPIO4, HC-SR04 GPIO16/17 and actual wiring verified |
| Async API | `/api/state` and `/state` equivalent, six outputs, queued request IDs apply, deterministic errors; TCP/80 provisioning only |
| Burst/stability | Run read-only stress below; retain response timings, curl failures, heap/minimum allocation and serial logs |
| Shelly | Gen1 `/status` + `/relay/0`; Gen2/3 `/rpc/Switch.*?id=0`; model/firmware versions, offline/auth errors; heatmat stays passive |
| Energy/schedules | Wh/kWh, offsetWh/reset/new grow/reboot; `/rpc/Schedule.List` empty/multiple/unsupported responses and timezone |
| HMAC | Valid PATCH `/api/backend/grow-profile`; bad signature, wrong IP, stale timestamp, reused nonce, field/date validation, concurrent dashboard writes; no secret exposure |
| LittleFS | Mount existing filesystem without format; diary read/write/restart, backup and manual recovery |
| OTA | Correct S3 repository, manifest/version, test diagnostics, task quiescence and outputs OFF, matching partitions, post-update version/settings |
| Rollback | Restore prior S3 image/configuration/diary over verified USB route; check outputs before reconnecting loads |

Read-only transport diagnostic (curl, jq, bash):

```bash
bash tests/test_async_transport_stress.sh <device-ip>
```

OTA transport diagnostic, no flashing; explicit exclusive mode reboots the device:

```bash
bash tests/test_ota_transport.sh <device-ip> --normal
# Only on a prepared test device: --exclusive or --both
```

The large classic ESP32 mutation suite is not copied blindly: it assumes 4/8 outputs and different pump/control numbers. The focused S3 suite covers the adapted contract; complete on-device migration gates are still required.
