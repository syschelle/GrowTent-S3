# Security — GrowTent-S3

This adaptation imports the security behavior of GrowTent v0.5.3. It is not a hardware-validated production release.

Use the controller on a trusted local network. The general dashboard/relay/pump APIs are not covered by the optional backend HMAC endpoint. Do not expose the controller directly to the Internet. Some inherited outbound HTTPS clients use `setInsecure()`; certificate validation is not provided on those paths. See the actual source before relying on transport authenticity.

The optional `PATCH /api/backend/grow-profile` path uses the inherited source-IP check, HMAC-SHA256, timestamp window, nonce/replay protection, field whitelist and atomic main-loop handoff. It is disabled by default. Never include the signing key in issues, screenshots, serial logs or test fixtures. Verify this endpoint with the real backend before enabling it in operation.

S3-specific controls reserve relays 1–3 exclusively for pumps. Generic relay controls, heater assignment and minute schedules cannot own those outputs. Disabled-pump and overlap guards apply at action application and the central GPIO setter. OFF remains allowed for disabled outputs. These software checks do not replace physical safety measures or the required disconnected-load tests.

OTA assets are isolated to `syschelle/GrowTent-S3`. No release/tag or automatic device update is created by the migration PR. Review the selected hardware, partitions and recovery image before flashing. Existing LittleFS is never automatically formatted on mount failure.

Report suspected vulnerabilities privately through the repository owner's available private channel rather than publishing keys or exploitable device details. A dedicated security contact address and supported production version policy are currently open.
