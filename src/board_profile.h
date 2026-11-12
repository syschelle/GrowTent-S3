#pragma once
// Waveshare ESP32-S3-Relay-6CH. Keep hardware policy in one host-testable header.
constexpr int BOARD_RELAY_COUNT = 6;
constexpr int CONTROL_RELAY_FIRST_IDX = 3;
constexpr int CONTROL_RELAY_LAST_IDX = 5;
constexpr int BOARD_RELAY_PINS[BOARD_RELAY_COUNT] = {1, 2, 41, 42, 45, 46};
constexpr bool isControlRelayIndex(int idx) { return idx >= 3 && idx <= 5; }
constexpr bool isPumpRelayIndex(int idx) { return idx >= 0 && idx <= 2; }
constexpr int pumpSlotForRelay(int idx) { return isPumpRelayIndex(idx) ? idx : -1; }
constexpr bool isValidBoardRelayCount(int count) { return count == BOARD_RELAY_COUNT; }
constexpr bool isValidBoardHeatingRelay(int relay) { return relay >= 4 && relay <= 6; }
