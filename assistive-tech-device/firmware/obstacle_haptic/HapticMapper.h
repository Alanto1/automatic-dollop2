#pragma once

// <stdint.h>, NOT <cstdint>. Desktop g++ ships both, but AVR-GCC (what the
// Arduino IDE uses for the Nano's ATmega328P) only has the C header - so
// <cstdint> compiles fine for firmware/tests/ and then fails with "fatal
// error: cstdint: No such file or directory" the moment you build for the
// board. The unqualified uint8_t/uint16_t/uint32_t names used below work
// with this header on both toolchains. Don't "modernize" this back.
#include <stdint.h>

// Pure distance -> haptic feedback mapping logic for the obstacle-detection
// wristband. No Arduino, no sensor library, no hardware dependency at all -
// that's deliberate, so this one header can be compiled and unit-tested on
// a desktop (see firmware/tests/) and ported line-for-line to JS for the
// browser simulator (firmware/simulator/haptic_simulator.html).
//
// obstacle_haptic.ino owns everything hardware-shaped: reading the VL53L0X,
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
    // A reading >= kFarThresholdMm is treated as "no obstacle", so that
    // constant is the main knob for "how close does something have to be
    // before the wristband reacts at all". Lower it to make the device
    // quieter and more local; raise it to react earlier.
    //
    // These were deliberately tightened from an earlier 1800/1000/400 set,
    // which reacted to almost anything down a corridor and buzzed close to
    // constantly indoors. At 1000mm the device stays silent until something
    // is within about arm's reach.
    //
    // A useful side effect of staying at/below 1000mm: it's comfortably
    // inside the VL53L0X's *default* measurement profile (good to roughly
    // 1.2m), so obstacle_haptic.ino no longer needs the long-range sensor
    // preset, which bought reach at the cost of noise immunity. If these
    // ever go back above ~1100mm, re-read that note in the .ino - the
    // sensor config has to move with them.
    //
    // Keep them strictly descending; the simulator enforces the same
    // ordering, and classify() below assumes it.
    static constexpr uint16_t kFarThresholdMm = 1000;
    static constexpr uint16_t kMediumThresholdMm = 600;
    static constexpr uint16_t kNearThresholdMm = 250;

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
    // Each case rebuilds a PulseTiming from the constants' individual
    // fields rather than returning the constant object itself. This is
    // defensive, not a fix for an observed failure: returning `kMediumPulse`
    // directly copies the object, which can ODR-use it, and pre-C++17 that
    // needs an out-of-class definition the header doesn't provide. In
    // practice desktop g++ links it fine even at -std=c++11 (checked), so
    // this may be unnecessary on AVR too - it's just cheap insurance in the
    // form that's guaranteed portable, since reading `.onMs`/`.offMs` as
    // constant expressions is never an ODR-use.
    PulseTiming pulseForZone(Zone zone) const {
        switch (zone) {
            case Zone::Medium: return PulseTiming{kMediumPulse.onMs, kMediumPulse.offMs};
            case Zone::Near: return PulseTiming{kNearPulse.onMs, kNearPulse.offMs};
            case Zone::Critical: return PulseTiming{kCriticalPulse.onMs, kCriticalPulse.offMs};
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
