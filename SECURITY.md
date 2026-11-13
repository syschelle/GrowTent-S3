# Security — v0.5.10

v0.5.5 fixes status localization and asset cache versioning. Only assets requested with the matching firmware version receive immutable caching; missing or obsolete versions use no-store. Irrigation/HMAC behavior is unchanged.

The new local-plan/event APIs require the existing allowed source IPv4, enabled backend-write configuration, raw-body HMAC-SHA256, ±60-second timestamp and nonce checks. Responses are signed and bound to request method/path/nonce. A full replay window returns 429 rather than evicting live entries. GET query parameters are rejected. No signing keys are exposed in UI, logs or state.

All new HTTP mutations are queued; main-loop code verifies NVS persistence before scheduled starts and claims occurrences durably. The event queue never overwrites unacknowledged records. HMAC provides no encryption; existing general local UI/control routes are outside this HMAC channel. The local plan is disabled by default, and backend cutover is a separate, required change.

See [IRRIGATION_PLAN_API.md](IRRIGATION_PLAN_API.md) for the complete protocol and failure behavior. Real-device power-failure, timing, HTTP/HMAC and push-provider tests remain open; host tests do not establish physical safety or exactly-once push delivery.

## Existing security context

# Security — GrowTent-S3

This adaptation imports the security behavior of GrowTent v0.5.3. It is not a hardware-validated production release.

Use the controller on a trusted local network. The general dashboard/relay/pump APIs are not covered by the optional backend HMAC endpoint. Do not expose the controller directly to the Internet. Some inherited outbound HTTPS clients use `setInsecure()`; certificate validation is not provided on those paths. See the actual source before relying on transport authenticity.

The optional `PATCH /api/backend/grow-profile` path uses the inherited source-IP check, HMAC-SHA256, timestamp window, nonce/replay protection, field whitelist and atomic main-loop handoff. It is disabled by default. Never include the signing key in issues, screenshots, serial logs or test fixtures. Verify this endpoint with the real backend before enabling it in operation.

S3-specific controls reserve relays 1–3 exclusively for pumps. Generic relay controls, heater assignment and minute schedules cannot own those outputs. Disabled-pump and overlap guards apply at action application and the central GPIO setter. OFF remains allowed for disabled outputs. These software checks do not replace physical safety measures or the required disconnected-load tests.

OTA assets are isolated to `syschelle/GrowTent-S3`. No release/tag or automatic device update is created by the migration PR. Review the selected hardware, partitions and recovery image before flashing. Existing LittleFS is never automatically formatted on mount failure.

Report suspected vulnerabilities privately through the repository owner's available private channel rather than publishing keys or exploitable device details. A dedicated security contact address and supported production version policy are currently open.

## v0.5.6 local editor

GET/POST `/api/settings/irrigation-plan` uses the same trusted-LAN dashboard boundary as existing operating-setting routes, not backend HMAC authentication. Do not expose the dashboard directly to untrusted networks. POST accepts JSON with expected_revision, enabled, every_n_days and offset_after_light_on_min only. v0.5.7 accepts an optional last_run_date baseline: no future, invalid, cleared or backward dates. Rechecked on the main loop before persistence. Local and authenticated backend mutations share one queue and NVS journal; revisions prevent stale dashboard overwrites. NVS writes remain on the main loop, with persistence confirmed before reporting applied. No keys are returned. Enabling local scheduling requires a valid clock; independent backend scheduling must be disabled.

## v0.5.10 backend integration

See IRRIGATION_PLAN_API.md for protocol v2 and signed idempotent manual starts. Command claims persist before starts; unknown expired commands cannot run. Full manual cycles use the backend event stream and require a valid clock and event capacity even with scheduling disabled. Real-device power-failure, pump/phase interlock and push integration validation remain OPEN.

## v0.5.14 humidifier fan coupling

The new local dashboard GET/POST `/api/settings/humidifier-fan` endpoint shares the existing trusted-LAN boundary and is not a backend HMAC route. JSON-only mutations validate a single relay field, exclude pumps and the active local heater, queue application to the main loop and verify NVS persistence before reporting applied. No Shelly credentials are exposed. Only successful, parsed ESP switch acknowledgements can start the fan timer; an unrecognized acknowledgement cannot turn it on. Responses from an old configuration and older concurrent commands are fenced out. Minutes schedules and manual relay actions cannot override the owned relay.

The cache is refreshed at startup/assignment and hourly, including hourly retry after failures. A failed refresh retains a same-device last known duration and marks it stale. Changing the Shelly host/generation/credentials invalidates it. Unknown/disabled Auto-Off keeps the fan off. Active timers are not extended by cache refresh. Commands use a monotonic bounded deadline from HTTP request start. Reboot does not restore an active fan. Direct Shelly commands or timer edits between refreshes are outside this coupling; it is not a physical state mirror or hard real-time safety mechanism. Hardware validation remains open.
