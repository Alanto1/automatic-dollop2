// obstacle_haptic.ino
//
// Hardware glue for the obstacle-detection wristband: polls a VL53L1X
// time-of-flight sensor over I2C, hands each reading to HapticMapper (see
// HapticMapper.h - all the actual distance -> vibration decision logic
// lives there, not here), and drives the vibration motor's PWM pin
// accordingly.
//
// NOT YET FLASHED OR RUN ON REAL HARDWARE - this environment has no
// Arduino toolchain/board attached. HapticMapper.h's logic is desktop
// tested (see ../tests/); this file has only been reviewed, not compiled.
// Compile with the Arduino IDE/CLI once the board is in hand, and treat
// the first flash as a fresh bring-up, not a "should just work".
//
// Requires the "VL53L1X" Arduino library by Pololu (Library Manager ->
// search "VL53L1X" by Pololu). Any VL53L1X breakout wired the standard
// I2C way (VIN/GND/SDA/SCL) should work with it, regardless of who
// silkscreened the board.
//
// Wiring (see ../../README.md for the full BOM + diagram):
//   VL53L1X  VIN  -> Nano 5V   (breakout has its own onboard regulation)
//   VL53L1X  GND  -> Nano GND
//   VL53L1X  SDA  -> Nano A4
//   VL53L1X  SCL  -> Nano A5
//   Motor driver transistor base -> Nano D9, through a 220ohm resistor
//
// Set DEBUG_SERIAL to 1 to print live distance/zone/motor readings at
// 115200 baud while tuning HapticMapper's thresholds. Leave it at 0 for
// normal use - Serial calls cost real time on every loop iteration and
// aren't needed once thresholds are dialed in.
#define DEBUG_SERIAL 0

#include <Wire.h>
#include <VL53L1X.h>
#include "HapticMapper.h"

namespace {
constexpr uint8_t kMotorPin = 9;           // PWM-capable pin driving the motor transistor
constexpr uint16_t kSensorPeriodMs = 60;   // ~16Hz continuous ranging
constexpr uint32_t kDebugPrintIntervalMs = 250;
}  // namespace

VL53L1X sensor;
HapticMapper mapper;

// Safe default: motor off until the first real sensor reading comes in.
uint16_t lastDistanceMm = HapticMapper::kFarThresholdMm;

#if DEBUG_SERIAL
uint32_t lastDebugPrintMs = 0;
#endif

void setup() {
    pinMode(kMotorPin, OUTPUT);

#if DEBUG_SERIAL
    Serial.begin(115200);
#endif

    Wire.begin();
    Wire.setClock(400000);  // VL53L1X supports I2C fast mode

    sensor.setTimeout(500);
    if (!sensor.init()) {
#if DEBUG_SERIAL
        Serial.println("Failed to detect/init VL53L1X - check wiring");
#endif
        // Halt rather than pretend to work: a wristband that silently
        // reports "all clear" with a dead sensor is worse than one that
        // visibly does nothing. There's no distinct "sensor fault" haptic
        // pattern in v1 (would need its own design + tests, not just a
        // reuse of the proximity pulses) - that's a real gap, not a
        // solved problem. See README.md's failure-modes section.
        while (true) {
        }
    }

    sensor.setDistanceMode(VL53L1X::Long);
    sensor.setMeasurementTimingBudget(50000);  // microseconds
    sensor.startContinuous(kSensorPeriodMs);
}

void loop() {
    if (sensor.dataReady()) {
        uint16_t reading = sensor.read();
        // On a timeout, fail toward "no vibration" rather than trusting
        // a stale or garbage reading - same fail-safe direction as
        // HapticMapper's own kMinValidMm handling.
        lastDistanceMm = sensor.timeoutOccurred() ? HapticMapper::kFarThresholdMm : reading;
    }

    // Recompute every loop iteration (not just on a fresh sensor reading)
    // so pulse timing stays smooth between the ~60ms sensor updates.
    HapticMapper::MotorCommand cmd = mapper.update(lastDistanceMm, millis());
    analogWrite(kMotorPin, cmd.motorOn ? cmd.pwmDuty : 0);

#if DEBUG_SERIAL
    uint32_t now = millis();
    if (now - lastDebugPrintMs >= kDebugPrintIntervalMs) {
        lastDebugPrintMs = now;
        Serial.print("distance_mm=");
        Serial.print(lastDistanceMm);
        Serial.print(" zone=");
        Serial.print(static_cast<int>(mapper.classify(lastDistanceMm)));
        Serial.print(" motorOn=");
        Serial.print(cmd.motorOn);
        Serial.print(" duty=");
        Serial.println(cmd.pwmDuty);
    }
#endif
}
