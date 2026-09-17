// Is the pin actually being driven? Answer without typing anything.
//
// motor_test.ino only pulses a pin after you send it a command. That makes
// two very different faults look identical: a pin that cannot drive, and a
// command that never arrived. This sketch removes the second one -- it needs
// no serial input at all. Flash it, plug in USB, and it drives the pin
// forever on its own.
//
// --- HOW TO READ IT ----------------------------------------------------
//
// Multimeter on V(DC), 20V range. BLACK probe on GND, RED probe on the pin
// under test (GPIO 1 by default -- the servo's yellow wire).
//
// It runs two phases, on a loop, announcing each one over serial:
//
//   PHASE 1, 5 seconds: a plain 1kHz square wave, 50% duty.
//     Meter should read about 1.6V. This tests the GPIO itself and does
//     NOT involve LEDC. A servo ignores it and stays limp -- that is fine
//     and expected, we are only asking whether the pin can go high.
//
//   PHASE 2, 12 seconds: real servo pulses, 50Hz, sweeping 60-120 degrees.
//     Meter should read about 0.25-0.35V. This tests LEDC. A working servo
//     visibly moves back and forth every second.
//
// --- WHAT THE RESULT MEANS ---------------------------------------------
//
//   1.6V then 0.3V   Pin and LEDC are both fine, and motor_test's problem
//                    was that your command never reached the board. The
//                    servo should be moving in phase 2. If it is not, the
//                    servo is faulty -- swap it.
//
//   1.6V then 0.0V   The GPIO works but LEDC does not. Firmware problem,
//                    not wiring. Tell me and I will change how it drives.
//
//   0.0V then 0.0V   The pin never goes high at all. Either GPIO 1 is
//                    damaged or your probe is not on the pin you think.
//                    Change PIN below to 2 and reflash: if GPIO 2 gives
//                    1.6V, GPIO 1 is dead and we remap R1.
//
// The serial output is a convenience, not a requirement. Everything above
// is readable on the meter alone.
//
// Arduino IDE:
//   Board:              "LOLIN S2 Mini"
//   USB CDC On Boot:    ENABLED

#include <Arduino.h>

// The pin under test. GPIO 1 is R1. Change to 2 to test R2's pin, etc.
static const int PIN = 1;

// Same band as motor_test.ino and Sesame's firmware. 90 degrees is 1830us.
static const int SERVO_HZ = 50;
static const int SERVO_BITS = 14;
static const int MIN_PULSE = 732;
static const int MAX_PULSE = 2929;

static void servoWrite(int deg) {
  int us = MIN_PULSE + (int)((long)(MAX_PULSE - MIN_PULSE) * deg / 180);
  uint32_t duty = (uint32_t)((us / 20000.0) * ((1 << SERVO_BITS) - 1));
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PIN, duty);
#else
  ledcWrite(0, duty);
#endif
  Serial.printf("  %3d deg = %4dus, duty %u\n", deg, us, (unsigned)duty);
}

// Phase 1: no LEDC, no timers, just the GPIO going up and down. If this
// reads 0V the pin itself is the problem and nothing else matters.
static void squareWave(unsigned long ms) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcDetach(PIN);
#else
  ledcDetachPin(PIN);
#endif
  pinMode(PIN, OUTPUT);
  unsigned long t0 = millis();
  while (millis() - t0 < ms) {
    digitalWrite(PIN, HIGH);
    delayMicroseconds(500);
    digitalWrite(PIN, LOW);
    delayMicroseconds(500);
  }
  digitalWrite(PIN, LOW);
}

void setup() {
  // Park every servo pin first: uploading soft-resets the CPU but not LEDC,
  // so a pin the previous sketch left pulsing goes on pulsing and will be
  // blamed on wiring. Only PIN gets driven from here on.
  static const int ALL[8] = {1, 2, 4, 6, 8, 10, 13, 14};
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(ALL[i]);
#else
    ledcDetachPin(ALL[i]);
#endif
    pinMode(ALL[i], INPUT);
  }

  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}

  Serial.println("---------------------------------------");
  Serial.printf("  pin probe: GPIO %d, no input needed\n", PIN);
  Serial.println("---------------------------------------");
  Serial.println("Meter on V(DC) 20V. BLACK on GND, RED on the pin.");
  Serial.println("Phase 1 should read ~1.6V, phase 2 ~0.3V.");
}

void loop() {
  Serial.println();
  Serial.printf("PHASE 1: 1kHz square wave on GPIO %d, 5 seconds.\n", PIN);
  Serial.println("  Expect ~1.6V. Servo stays limp -- that is correct.");
  squareWave(5000);

  Serial.printf("PHASE 2: servo pulses on GPIO %d, 12 seconds.\n", PIN);
  Serial.println("  Expect ~0.3V. A working servo moves every second.");
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(PIN, SERVO_HZ, SERVO_BITS);
#else
  ledcSetup(0, SERVO_HZ, SERVO_BITS);
  ledcAttachPin(PIN, 0);
#endif
  for (int i = 0; i < 6; i++) {
    servoWrite(i % 2 ? 120 : 60);
    delay(2000);
  }
}
