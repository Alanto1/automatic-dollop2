// obstacle_haptic.ino
//
// Hardware glue for the obstacle-detection wristband: polls a VL53L0X
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
// Requires the "VL53L0X" Arduino library by Pololu (Library Manager ->
// search "VL53L0X" by Pololu) - NOT the VL53L1X library this file used
// before. See PURCHASE_LIST.md: no walk-in Almaty store stocks a VL53L1X
// as of this writing, so this targets the VL53L0X actually on shelves
// (e.g. a GY-53 board). The VL53L0X library's API is simpler than
// VL53L1X's - no distance-mode setting, and
// readRangeContinuousMillimeters() blocks (up to the timeout below) until
// a fresh reading is ready rather than offering a separate non-blocking
// "is data ready" check - so this loop is simpler than a VL53L1X version
// would be too, not just swapped in place.
//
// Wiring (see ../../README.md for the full BOM + diagram):
//   VL53L0X  VIN  -> Nano 5V   (breakout has its own onboard regulation)
//   VL53L0X  GND  -> Nano GND
//   VL53L0X  SDA  -> Nano A4
//   VL53L0X  SCL  -> Nano A5
//   VL53L0X  PS   -> GND       <-- REQUIRED on a GY-53. Read the note below.
//   Motor driver transistor base -> Nano D9, through a resistor (220ohm-1k, either works)
//
// *** THE GY-53 IS NOT A BARE VL53L0X BREAKOUT. ***
// It carries its own onboard MCU between you and the sensor chip, and its
// PS pin picks which of two mutually exclusive modes that MCU runs in:
//   PS = 1 (pulled high on-board, the FACTORY DEFAULT)
//       UART/serial mode. The onboard MCU owns the sensor chip and streams
//       distance over TX/RX + PWM. I2C DOES NOT WORK AT ALL in this mode -
//       this library will never find the sensor, no matter how correct
//       VIN/GND/SDA/SCL are.
//   PS = 0 (wired to GND)
//       I2C mode. The onboard MCU steps back and you address the VL53L0X
//       chip directly, which is what this library expects.
// So PS -> GND is a required connection, not an optional extra pin.
// Confirmed against the GY-53 manual, which states the module "defaults to
// serial port mode... PS port is pulled high". This cost a full debugging
// session to find, because every symptom (init() failing, an I2C scan
// finding nothing at any address, SDA/SCL flickering seemingly at random)
// looks exactly like a wiring fault. The "random" SDA/SCL activity is in
// fact the onboard MCU doing its OWN I2C traffic to the sensor chip while
// in UART mode - real traffic, just not yours.
//
// Set DEBUG_SERIAL to 1 to print live distance/zone/motor readings at
// 115200 baud while tuning HapticMapper's thresholds. Leave it at 0 for
// normal use - Serial calls cost real time on every loop iteration and
// aren't needed once thresholds are dialed in.
#define DEBUG_SERIAL 0

#include <Wire.h>
#include <VL53L0X.h>
#include "HapticMapper.h"

namespace {
constexpr uint8_t kMotorPin = 9;           // PWM-capable pin driving the motor transistor
constexpr uint16_t kSensorPeriodMs = 50;   // continuous-ranging period passed to the sensor
constexpr uint32_t kDebugPrintIntervalMs = 250;
}  // namespace

VL53L0X sensor;
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
    Wire.setClock(400000);  // VL53L0X supports I2C fast mode

    sensor.setTimeout(500);
    if (!sensor.init()) {
#if DEBUG_SERIAL
        Serial.println("Failed to detect/init VL53L0X - check wiring");
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

    // Sensor left on its DEFAULT measurement profile deliberately.
    //
    // The default reliably reaches roughly 1.2m, and HapticMapper's far
    // threshold is now 1000mm, so the entire useful range sits inside it
    // with margin to spare. The default profile is also the more accurate
    // and noise-immune of the two, which is what you want on a wrist.
    //
    // An earlier revision enabled the Pololu long-range preset here
    // (setSignalRateLimit(0.1) plus longer VCSEL pre-range/final-range
    // periods) because the far threshold was 1800mm and the default
    // profile couldn't see that far. Those thresholds have since been
    // tightened, so that preset now buys reach nobody needs at the cost of
    // more spurious readings. If kFarThresholdMm ever goes back above
    // ~1100mm, restore it - the sensor config and the thresholds have to
    // move together, or the far zone silently becomes "sensor can't see
    // that far" rather than "nothing is there".
    sensor.startContinuous(kSensorPeriodMs);
}

void loop() {
    // Blocks (up to the timeout set above) until the next reading is
    // ready, so this loop runs at roughly the sensor's own
    // kSensorPeriodMs cadence rather than "as fast as possible" - plenty
    // fast next to pulse timings measured in hundreds of milliseconds.
    uint16_t reading = sensor.readRangeContinuousMillimeters();
    // On a timeout, fail toward "no vibration" rather than trusting a
    // stale or garbage reading - same fail-safe direction as
    // HapticMapper's own kMinValidMm handling.
    lastDistanceMm = sensor.timeoutOccurred() ? HapticMapper::kFarThresholdMm : reading;

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
