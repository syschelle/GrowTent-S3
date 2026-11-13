# Testing — v0.5.7

## Local plan status UI

`node tests/test_local_plan_ui.mjs` parses the shipped JavaScript and exercises its renderer with the production translation dictionary: German/English loading, disabled, ready, blocked, stale, missing metadata and failed-fetch states. It checks language/fetch hooks and firmware-versioned asset URLs. Full firmware compilation runs in CI. Browser/device update verification remains open.

## Local irrigation plan

`python tests/test_irrigation_plan.py` passes host policy/integration checks: civil dates and leap days, recurrence, no catch-up/grace boundary, already-claimed dates, drying/busy/invalid clock, Gen1 weekday rules, Gen2 weekday lists/ranges/names, ambiguous/unsupported schedules, replay saturation without eviction and DST calendar behavior. Wiring checks verify dry-phase/start ownership guards, factory reset, main-loop persistence and lifecycle hooks. Tests exercise the production policy header rather than a separate reimplementation.

The production JSON schedule parser is additionally compiled and executed with ArduinoJson after the CI build: enabled/disabled Gen1 rules, weekly ON/OFF times, Gen2/3 jobs, malformed/ambiguous/solar/paginated responses and switch-id filtering.

CI also runs the actual full board build. See current pull-request checks for the authoritative compile result. Existing S3 host mapping tests, where present, remain required.

### Hardware and integration gates (OPEN)

- Signed raw-byte request/response canonicalization with real backend client; wrong key/IP/timestamp/nonce, replay saturation, revision retries and ACK validation.
- NVS power cut before/after occurrence claim, queued update and ACK; restart-interrupted event, no duplicate start; full/corrupt flash fails closed.
- Gen1/2/3 real-device schedules, weekly differences, enabled/empty/unsupported schedules, same-IP configuration edits, device replacement and timeout/cache behavior.
- Phase change from dashboard and backend, same-loop start conflict, drying during pulse/pause, manual cycle denial and allowed maintenance pulse.
- NTP missing/recovery, timezone agreement, midnight/DST delay, missed days and backward clock changes without catch-up.
- Event queue fills during backend outage; no unacknowledged loss, reserved finish space, no false completion, backend deduplication/notification behavior after reconnection.
- Board relay ON/OFF mapping, disabled pumps, overlap, Flood, OTA interruption and rollback to the previous firmware with local scheduling explicitly disabled.

No backend code was changed; end-to-end event ingestion and push delivery cannot be validated until its later integration.

## Prior checks and board reference

# Testing — GrowTent-S3 v0.5.3

## Executed locally

- `python tests/test_s3_contract.py`: five regression groups pass. Compiles and executes the actual `setRelay` implementation with mocked GPIO/FreeRTOS; covers disabled pumps, OFF after disable, stop latch, overlap with active/armed pumps, unavailable mutex and invalid outputs. Also checks actual browser function behavior for 4/5/6-only control, six unique output elements, fixed pump names, no pump schedules and S3 API/NVS/OTA mapping guards.
- Inline JavaScript syntax check and shell syntax checks are included in the host suite.
- Full PlatformIO S3 build: **PASS in GitHub Actions** for migration commit `0483c2e13c5de60c8c6feda880562245f0215153`, run [43268951794](https://github.com/syschelle/GrowTent-S3/actions/runs/43268951794). Firmware image created for `esp32s3`; RAM 56,116 / 327,680 bytes (17.1%), flash 1,694,077 / 1,966,080 bytes (86.2%). Subsequent commits run the same checks again; use the current PR checks as the authoritative head result. The local dependency registry returned intermittent 403 errors; the independent Actions build completed with the tracked configuration.

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

## v0.5.6 editor coverage

`node tests/test_local_plan_editor.mjs` exercises the shipped renderer/save functions with a mock DOM/HTTP transport: history display, no synthetic date, unsaved edits, revision conflicts, invalid bounds, persistence acknowledgement, stale polling responses, language and network errors. Contract checks cover queue/auth separation and absence of flash writes in Async callbacks. Full board builds and schedule parser tests run in CI. Hardware/reboot, simultaneous real backend writes and browser checks remain OPEN.

## v0.5.7 date/layout coverage

The editor test covers the native date input, unknown history, preserving unsaved dates, date bounds, full-width tile ordering, and confirmation/error states. The production C++ historyDateAllowed policy is tested for unknown, same-day, advancing, future, erased and backward history. Both request acceptance and main-loop apply use it. Hardware history import and restart checks remain OPEN.
