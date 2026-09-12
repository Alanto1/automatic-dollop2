// Move all eight servos from the serial monitor. No libraries.
//
// This is a drop-in replacement for Sesame's own motor tester, which is
// vendored one folder over in ../sesame-motor-tester/. Same commands, same
// pins, same pulse widths -- the only difference is that upstream's needs
// the ESP32Servo library and this one drives LEDC directly.
//
// Use whichever compiles. If ESP32Servo installs cleanly, upstream's is the
// canonical one and is what its build guide refers to. If it does not --
// which happens with a sketchbook on a non-ASCII path, or under OneDrive --
// use this and lose nothing.
//
// They live in SEPARATE FOLDERS on purpose. The Arduino IDE compiles every
// .ino in a folder as one program, so two sketches side by side means two
// setup()s and two loop()s and a build that cannot succeed.
//
// --- WHAT TO DO WITH IT -----------------------------------------------
//
//   1. Flash it. Nothing moves: motors stay limp until commanded, and any
//      pin left pulsing by a previous sketch is parked on boot.
//   2. Serial monitor at 115200. The line-ending dropdown does not matter;
//      this sketch accepts a command with or without a newline.
//   3. Send  all,90
//   4. NOW plug in motor 0. It should whir to position and hold.
//   5. Plug in motors 1..7, ONE AT A TIME, watching each.
//
// If you cannot tell whether a servo moved at all, send  sweep,0  instead:
// four moves through most of the travel, a second apart. That is impossible
// to miss, and a servo that does nothing during a sweep is not being driven.
//
// Plugging them in one at a time is the whole point. A servo that goes to
// the wrong joint, or fights its own end stop, is obvious when it is the
// only thing that just moved and invisible when eight move at once.
//
//   motor  joint  GPIO
//     0     R1      1     right hip
//     1     R2      2     right hip
//     2     L1      4     left hip
//     3     L2      6     left hip
//     4     R4      8     right lower leg
//     5     R3     10     right lower leg
//     6     L3     13     left lower leg
//     7     L4     14     left lower leg
//
// The legs are NOT in alphabetical order: R4 is motor 4, R3 is motor 5.
//
// --- BEFORE YOU START --------------------------------------------------
//
// Every motor shaft must spin FREELY. If the hip joints are already pressed
// onto their shafts and the M2.5 centre screws are not in, pull them off.
// Upstream flags this as a caution rather than a tip: a joint that cannot
// reach the commanded angle stalls the servo, and a stalled MG90S strips its
// gears in seconds.
//
// Arduino IDE:
//   Board:              "LOLIN S2 Mini"
//   USB CDC On Boot:    ENABLED     <-- without this Serial prints nothing

#include <Arduino.h>

// Sesame's pin map, from servoPins[8] in its firmware. Do not reorder.
static const int SERVO_PINS[8] = {1, 2, 4, 6, 8, 10, 13, 14};
static const char *JOINTS[8]   = {"R1", "R2", "L1", "L2", "R4", "R3", "L3", "L4"};

// 14 bits, not 16: the ESP32-S2's LEDC timers cap there. The S2 also has
// exactly 8 channels, which is why all 8 are spoken for and the pump gets a
// series resistor rather than PWM. board_test.ino has the detail.
static const int SERVO_HZ = 50;
static const int SERVO_BITS = 14;

// Sesame's pulse band. 90 degrees lands on 1830us, not the conventional
// 1500 -- that is the midpoint of 732..2929 and it is correct. Changing
// these means every horn aligned against this sketch is aligned to nothing.
static const int MIN_PULSE = 732;
static const int MAX_PULSE = 2929;

static bool attached[8] = {false, false, false, false, false, false, false, false};
static int  lastAngle[8];

static void attachOne(int id) {
  if (attached[id]) return;
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(SERVO_PINS[id], SERVO_HZ, SERVO_BITS);
#else
  ledcSetup(id, SERVO_HZ, SERVO_BITS);
  ledcAttachPin(SERVO_PINS[id], id);
#endif
  attached[id] = true;
}

static void writeAngle(int id, int deg) {
  deg = constrain(deg, 0, 180);
  attachOne(id);
  int us = MIN_PULSE + (int)((long)(MAX_PULSE - MIN_PULSE) * deg / 180);
  uint32_t duty = (uint32_t)((us / 20000.0) * ((1 << SERVO_BITS) - 1));
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(SERVO_PINS[id], duty);
#else
  ledcWrite(id, duty);
#endif
  lastAngle[id] = deg;
  Serial.printf("OK: motor %d (%s, GPIO %-2d) -> %3d deg  (%dus)\n",
                id, JOINTS[id], SERVO_PINS[id], deg, us);
}

static void stopAll() {
  for (int i = 0; i < 8; i++) {
    if (!attached[i]) continue;
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(SERVO_PINS[i]);
#else
    ledcDetachPin(SERVO_PINS[i]);
#endif
    attached[i] = false;
  }
  Serial.println("OK: all motors detached. Shafts are limp; safe to unplug.");
}

static void report() {
  Serial.println("  motor joint gpio  state");
  for (int i = 0; i < 8; i++) {
    if (attached[i]) {
      Serial.printf("    %d    %-3s   %-2d   holding %d deg\n",
                    i, JOINTS[i], SERVO_PINS[i], lastAngle[i]);
    } else {
      Serial.printf("    %d    %-3s   %-2d   limp\n", i, JOINTS[i], SERVO_PINS[i]);
    }
  }
}

// Big obvious motion on one motor. If you cannot tell whether a servo is
// alive, this is the command to send: three moves, a second apart, through
// most of the travel. A servo that is powered and wired WILL be visible.
static void sweep(int id) {
  Serial.printf("Sweeping motor %d (%s, GPIO %d). Watch it.\n",
                id, JOINTS[id], SERVO_PINS[id]);
  const int stops[] = {90, 30, 150, 90};
  for (unsigned i = 0; i < sizeof(stops) / sizeof(stops[0]); i++) {
    writeAngle(id, stops[i]);
    delay(900);
  }
  Serial.println("Sweep done. It is still attached and holding 90.");
  Serial.println("Try to turn the horn with your fingers: it should push back.");
}

static void menu() {
  Serial.println();
  Serial.println("  id,angle   one motor      e.g.  0,90");
  Serial.println("  all,angle  every motor    e.g.  all,90");
  Serial.println("  sweep,id   big visible move, one motor   e.g.  sweep,0");
  Serial.println("  stop       detach all, shafts go limp");
  Serial.println("  list       what is attached and where");
  Serial.println();
}

// Uploading a sketch only soft-resets the CPU. The LEDC peripheral is NOT
// reset, and neither is the GPIO matrix routing its output, so a pin left
// pulsing by the PREVIOUS sketch keeps pulsing into this one -- a servo that
// holds position on a pin this sketch has not touched, which is impossible to
// tell from a bridged signal trace. Park all eight before doing anything.
static void parkAll() {
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(SERVO_PINS[i]);
#else
    ledcDetachPin(SERVO_PINS[i]);
#endif
    pinMode(SERVO_PINS[i], INPUT);
    attached[i] = false;
  }
}

void setup() {
  parkAll();

  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}

  Serial.println("-----------------------------------");
  Serial.println("  Sesame motor tester (no libraries)");
  Serial.println("-----------------------------------");
  Serial.printf("pins %d %d %d %d %d %d %d %d, %d-bit, %d-%dus\n",
                SERVO_PINS[0], SERVO_PINS[1], SERVO_PINS[2], SERVO_PINS[3],
                SERVO_PINS[4], SERVO_PINS[5], SERVO_PINS[6], SERVO_PINS[7],
                SERVO_BITS, MIN_PULSE, MAX_PULSE);
  Serial.println();
  Serial.println("Motors are LIMP. Nothing is driven until you command it.");
  Serial.println();
  Serial.println("Send 'all,90' FIRST, then plug motors in ONE AT A TIME.");
  Serial.println("Watch each one land before you plug in the next: a servo in");
  Serial.println("the wrong slot is obvious alone and invisible in a crowd.");
  menu();
}

// Collect characters ourselves instead of readStringUntil('\n').
//
// The Serial Monitor's line-ending dropdown decides whether a newline is ever
// sent at all, and on "No Line Ending" it is not. readStringUntil would then
// block forever: you type 0,90, press enter, and the board never sees a
// complete line. No echo, no pulse, no movement, and no way to tell that from
// a dead servo. So: dispatch on \n, on \r, OR after 150ms of silence with
// something in the buffer. Every dropdown setting now works.
static String buf;
static unsigned long lastChar = 0;

static void handle(String in);

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (buf.length()) { handle(buf); buf = ""; }
    } else {
      buf += c;
    }
    lastChar = millis();
  }
  if (buf.length() && millis() - lastChar > 150) {
    handle(buf);
    buf = "";
  }
}

static void handle(String in) {
  in.trim();
  if (!in.length()) return;

  if (in.equalsIgnoreCase("stop")) { stopAll(); return; }
  if (in.equalsIgnoreCase("list")) { report(); return; }

  int comma = in.indexOf(',');
  if (comma < 0) {
    Serial.println("Error: use 'id,angle', 'all,angle', 'sweep,id', 'stop' or 'list'.");
    menu();
    return;
  }

  String cmd = in.substring(0, comma);
  int angle = in.substring(comma + 1).toInt();

  if (cmd.equalsIgnoreCase("sweep")) {
    if (angle < 0 || angle > 7) {
      Serial.println("Error: motor id must be 0-7.");
      return;
    }
    sweep(angle);
    return;
  }

  if (cmd.equalsIgnoreCase("all")) {
    for (int i = 0; i < 8; i++) writeAngle(i, angle);
    return;
  }

  int id = cmd.toInt();
  if (id == 0 && cmd.charAt(0) != '0') {
    Serial.println("Error: motor id must be 0-7.");
    return;
  }
  if (id < 0 || id > 7) {
    Serial.println("Error: motor id must be 0-7.");
    return;
  }
  writeAngle(id, angle);
}
