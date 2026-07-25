// 02_motor_only.ino
//
// Bring-up test for tutorial.md's Phase 3: motor driver circuit ONLY, the
// sensor is ignored entirely (leave it wired from Phase 2 - this sketch
// just doesn't touch it). The point is isolation - a wiring mistake in
// the transistor/diode/motor circuit shows up here without the sensor's
// I2C traffic as a confounder.
//
// NOT YET FLASHED OR RUN ON REAL HARDWARE - reviewed, not compiled (no
// Arduino toolchain in the environment this was written in).
//
// Wiring:
//   board D9 -> resistor (220ohm-1k, either works) -> transistor base (2N2222)
//   Motor(+) -> board 5V
//   Motor(-) -> transistor collector
//   transistor emitter -> GND
//   1N4148 flyback diode across motor leads, cathode (banded end) to Motor(+)

namespace {
constexpr uint8_t kMotorPin = 9;
constexpr uint16_t kRampMs = 1500;  // time for one direction of the ramp
}  // namespace

void setup() {
    pinMode(kMotorPin, OUTPUT);
}

void loop() {
    // A free-running triangle wave over PWM duty: 0 -> 255 over kRampMs,
    // then 255 -> 0 over the next kRampMs, repeating - no delay(), so
    // this would compose cleanly with other work if this test ever grew
    // (it isn't meant to; it's disposable once Phase 3 passes).
    uint32_t phase = millis() % (static_cast<uint32_t>(kRampMs) * 2);
    uint8_t duty;
    if (phase < kRampMs) {
        duty = static_cast<uint8_t>((phase * 255UL) / kRampMs);
    } else {
        duty = static_cast<uint8_t>(255UL - ((phase - kRampMs) * 255UL) / kRampMs);
    }
    analogWrite(kMotorPin, duty);
}
