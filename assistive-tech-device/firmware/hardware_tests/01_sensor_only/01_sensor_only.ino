// 01_sensor_only.ino
//
// Bring-up test for tutorial.md's Phase 2: VL53L0X sensor ONLY, no motor
// circuit involved. The point is isolation - if this works, the sensor,
// its wiring, and the I2C bus are all fine, so any problem found later
// (Phase 3 onward) isn't this.
//
// NOT YET FLASHED OR RUN ON REAL HARDWARE - reviewed, not compiled (no
// Arduino toolchain in the environment this was written in).
//
// Requires the "VL53L0X" Arduino library by Pololu (Library Manager ->
// search "VL53L0X" by Pololu - NOT VL53L1X).
//
// Wiring:
//   VL53L0X VIN -> board 5V (or 3V3 - check your breakout's rating)
//   VL53L0X GND -> board GND
//   VL53L0X SDA -> board A4 (Nano) / SDA
//   VL53L0X SCL -> board A5 (Nano) / SCL
//
// After uploading: Tools -> Serial Monitor, 115200 baud.

#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

void setup() {
    Serial.begin(115200);
    Wire.begin();

    sensor.setTimeout(500);
    if (!sensor.init()) {
        // Matches the exact wording tutorial.md's Phase 2 tells you to
        // expect if wiring is wrong - keep this string in sync if it
        // ever changes.
        Serial.println("Failed to detect VL53L0X sensor - check wiring");
        while (true) {
        }
    }

    sensor.startContinuous();
}

void loop() {
    uint16_t reading = sensor.readRangeContinuousMillimeters();
    Serial.print("distance_mm=");
    if (sensor.timeoutOccurred()) {
        Serial.println("TIMEOUT");
    } else {
        Serial.println(reading);
    }
}
