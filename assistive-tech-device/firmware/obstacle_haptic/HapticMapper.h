#pragma once

#include <cstdint>

// Pure distance -> haptic feedback mapping logic for the obstacle-detection
// wristband. No Arduino, no sensor library, no hardware dependency at all -
// that's deliberate, so this one header can be compiled and unit-tested on
// a desktop (see firmware/tests/) and ported line-for-line to JS for the
// browser simulator (firmware/simulator/haptic_simulator.html).
//
// obstacle_haptic.ino owns everything hardware-shaped: reading the VL53L1X,
// deciding what distance to hand in on a sensor error/timeout, and turning
// update()'s MotorCommand into an analogWrite() call. This class just
// answers "given a distance and a clock reading, should the motor be on
// right now, and how strong?"
class HapticMapper {
public:
    enum class Zone : uint8_t {
        Far,      // no obstacle in range - motor off
        Medium,   // obstacle ahead, plenty of time to react - slow pulse
        Near,     // obstacle getting close - faster pulse
        Critical  // obstacle very close - continuous vibration
    };

    struct MotorCommand {
        bool motorOn;
        uint8_t pwmDuty;  // 0-255; meaningful only when motorOn is true
    };

    struct PulseTiming {
        uint16_t onMs;
        uint16_t offMs;  // 0 means "continuous" (never turns off)
    };

    // --- Distance thresholds (millimeters) ---
    // A reading >= kFarThresholdMm is treated as "no obstacle". This sits
    // at the VL53L0X's 2000mm ceiling, not just inside the VL53L1X's
    // 4000mm one - see README.md's sensor-substitution note for why that
    // matters if a VL53L0X ever ends up on the board instead.
    static constexpr uint16_t kFarThresholdMm = 2000;
    static constexpr uint16_t kMediumThresholdMm = 1000;
    static constexpr uint16_t kNearThresholdMm = 400;

    // Readings below this are treated as sensor noise/error rather than
    // "an obstacle is touching the sensor" (a real obstacle can't produce
    // a near-zero ToF reading in normal use). This is a deliberately
    // conservative choice - it fails toward "no vibration", not toward a
    // false alarm. See README.md's failure-modes section: that's a
    // tradeoff, not a safety guarantee.
    static constexpr uint16_t kMinValidMm = 10;

    static constexpr PulseTiming kMediumPulse{120, 400};
    static constexpr PulseTiming kNearPulse{120, 150};
    static constexpr PulseTiming kCriticalPulse{255, 0};

    static constexpr uint8_t kMediumDuty = 140;
    static constexpr uint8_t kNearDuty = 200;
    static constexpr uint8_t kCriticalDuty = 255;

    Zone classify(uint16_t distanceMm) const {
        if (distanceMm < kMinValidMm) return Zone::Far;
        if (distanceMm >= kFarThresholdMm) return Zone::Far;
        if (distanceMm >= kMediumThresholdMm) return Zone::Medium;
        if (distanceMm >= kNearThresholdMm) return Zone::Near;
        return Zone::Critical;
    }

    // nowMs must come from a single free-running monotonic clock (Arduino's
    // millis(), or the simulator's performance.now()). Call this on every
    // sensor poll (~16Hz in the .ino) with the latest reading and time -
    // pulse phase is tracked internally between calls.
    MotorCommand update(uint16_t distanceMm, uint32_t nowMs) {
        Zone zone = classify(distanceMm);

        if (!hasEnteredZone_ || zone != lastZone_) {
            // Entering a zone (including re-entering the same one after a
            // gap) always restarts its pulse from "on" - see the
            // ZoneTransition test in firmware/tests/. Without this, an
            // obstacle that suddenly gets much closer mid-pulse could
            // start out in that new zone's *off* phase, delaying the
            // stronger warning by up to a full cycle.
            lastZone_ = zone;
            zoneEnteredAtMs_ = nowMs;
            hasEnteredZone_ = true;
        }

        if (zone == Zone::Far) {
            return MotorCommand{false, 0};
        }

        PulseTiming timing = pulseForZone(zone);
        uint8_t duty = dutyForZone(zone);

        if (timing.offMs == 0) {
            return MotorCommand{true, duty};
        }

        // Unsigned subtraction wraps correctly even across millis()
        // rollover (~49 days), as long as less than that has elapsed
        // since zoneEnteredAtMs_ - fine for a dwell time measured in
        // pulse cycles, not days.
        uint32_t elapsed = nowMs - zoneEnteredAtMs_;
        uint32_t cycleMs = static_cast<uint32_t>(timing.onMs) + timing.offMs;
        uint32_t phase = elapsed % cycleMs;
        bool on = phase < timing.onMs;

        return MotorCommand{on, static_cast<uint8_t>(on ? duty : 0)};
    }

private:
    PulseTiming pulseForZone(Zone zone) const {
        switch (zone) {
            case Zone::Medium: return kMediumPulse;
            case Zone::Near: return kNearPulse;
            case Zone::Critical: return kCriticalPulse;
            default: return PulseTiming{0, 0};
        }
    }

    uint8_t dutyForZone(Zone zone) const {
        switch (zone) {
            case Zone::Medium: return kMediumDuty;
            case Zone::Near: return kNearDuty;
            case Zone::Critical: return kCriticalDuty;
            default: return 0;
        }
    }

    Zone lastZone_ = Zone::Far;
    uint32_t zoneEnteredAtMs_ = 0;
    bool hasEnteredZone_ = false;
};
