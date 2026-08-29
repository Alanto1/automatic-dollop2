// Bench-test one MG90S at a time, before any of them go into a leg.
//
// Two jobs, and they are the two that cost a day if skipped:
//
//   1. Catch DOA servos. Sesame's own Phase 1 checklist says to test every
//      MG90S on a tester before assembly. A dead servo found here is a
//      two-minute swap; found after it is screwed into a leg shell and
//      wired into the harness, it is an hour of disassembly.
//
//   2. Centre a servo and HOLD it there while you press its horn on. This
//      is the single most repeated warning in the build: centre every servo
//      before installing a single horn. A horn pressed on at 30 degrees off
//      gives you a leg with 30 degrees less travel on one side, and you do
//      not find out until the robot walks in a curve.
//
// The pulse constants below are Sesame's, copied from
// firmware/debugging-firmware/sesame-motor-tester.ino. They must match: 90
// degrees here has to be the same shaft position as 90 degrees in the real
// firmware, or every horn you align with this sketch is aligned to nothing.
//
// Arduino IDE setup for the S2 Mini:
//   Board:              "LOLIN S2 Mini"  (ESP32 boards package)
//   USB CDC On Boot:    ENABLED     <-- without this Serial prints nothing
//   Library:            "ESP32Servo" by Kevin Harrington (Library Manager)
//
// WIRING -- read this before plugging anything in:
//
//   servo brown/black  -> GND        (common with the board's GND)
//   servo red          -> EXTERNAL 5V, *not* the S2 Mini's 5V pin
//   servo orange/yellow-> GPIO 1
//
// One unloaded MG90S pulls ~200mA and peaks far higher the instant it
// starts moving. The S2 Mini's regulator is not a servo supply. Use the
// Waveshare buck converter or a phone charger, and tie its ground to the
// board's ground -- without the common ground the signal has no reference
// and the servo will twitch or ignore you.

#include <Arduino.h>
#include <ESP32Servo.h>

// Sesame's motor 0 pin, so this bench rig matches the real harness.
const int SERVO_PIN = 1;

// Sesame's pulse width limits. Do not "improve" these -- see the header.
const int MIN_PULSE = 732;
const int MAX_PULSE = 2929;

const int CENTRE = 90;

Servo servo;
bool attached = false;

void attachIfNeeded() {
  if (!attached) {
    servo.attach(SERVO_PIN, MIN_PULSE, MAX_PULSE);
    attached = true;
  }
}

void go(int deg, const char *what) {
  deg = constrain(deg, 0, 180);
  attachIfNeeded();
  servo.write(deg);
  Serial.printf("  -> %d deg   %s\n", deg, what);
}

void menu() {
  Serial.println();
  Serial.println("  c        centre at 90 and HOLD -- press the horn on now");
  Serial.println("  s        slow sweep 0 -> 180 -> 0, twice");
  Serial.println("  e        endpoints: 0, 180, back to 90");
  Serial.println("  <n>      go to angle n (0-180)");
  Serial.println("  d        detach (shaft goes limp, safe to unplug)");
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}

  Serial.println("-----------------------------------");
  Serial.println("  MG90S bench tester");
  Serial.println("-----------------------------------");
  Serial.printf("signal on GPIO %d, pulses %d-%dus (Sesame's)\n",
                SERVO_PIN, MIN_PULSE, MAX_PULSE);
  Serial.println();
  Serial.println("A servo PASSES if all four are true:");
  Serial.println("  1. it moves to every commanded angle without stalling");
  Serial.println("  2. it HOLDS position -- no hunting, buzzing or drift");
  Serial.println("  3. both endpoints are reachable and roughly symmetric");
  Serial.println("  4. it does not get hot after a minute of holding");
  Serial.println();
  Serial.println("Any buzzing that never settles is a dead or dying servo.");
  Serial.println("Number the good ones with tape as you go -- you need 8.");
  menu();

  go(CENTRE, "centred on boot");
}

void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (!cmd.length()) return;

  if (cmd == "c") {
    go(CENTRE, "HOLDING -- press the horn on now, short side into the joint");
  } else if (cmd == "d") {
    servo.detach();
    attached = false;
    Serial.println("  -> detached. Shaft is limp; safe to unplug.");
  } else if (cmd == "s") {
    attachIfNeeded();
    Serial.println("  sweeping -- watch for stalls, buzzing and dead spots");
    for (int pass = 0; pass < 2; pass++) {
      for (int d = 0; d <= 180; d += 2) { servo.write(d); delay(15); }
      for (int d = 180; d >= 0; d -= 2) { servo.write(d); delay(15); }
    }
    go(CENTRE, "sweep done, back to centre");
  } else if (cmd == "e") {
    go(0, "low endpoint");   delay(700);
    go(180, "high endpoint"); delay(700);
    go(CENTRE, "back to centre -- were both ends equally far from here?");
  } else {
    int deg = cmd.toInt();
    if (deg == 0 && cmd != "0") {
      Serial.printf("  ? '%s'\n", cmd.c_str());
      menu();
    } else {
      go(deg, "");
    }
  }
}
