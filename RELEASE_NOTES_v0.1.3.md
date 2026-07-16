## v0.1.3 – Relay names and S3 board label

### Changed
- Changed the board selection label from `6x S3` to `ESP32-S3-Relay-6Ch`.
- Relay 4–6 now use the default names `Relay 4`, `Relay 5` and `Relay 6`.
- Legacy default names such as `Pump 1` / `Pumpe 1` on Relay 4, `Pump 2` / `Pumpe 2` on Relay 5 and `Pump 3` / `Pumpe 3` on Relay 6 are automatically replaced with the correct relay names.
- Empty names for Relay 4–6 now fall back to their numbered default names.
- Other custom names for Relay 4–6 remain configurable and are preserved.
