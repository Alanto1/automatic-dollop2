// The easy way to find the Stand pose. Four keys, all legs move together.
//
// Put the robot's body on a box BEFORE plugging in -- it grabs all eight
// servos the moment it boots.
//
//   d   legs down   (feet go down -- keep pressing until it stands)
//   u   legs up
//   f   hips forward
//   b   hips back
//   x   let go, everything limp
//
// Type a letter and press Enter. "dddd" + Enter moves four steps at once.
// It prints the STAND line after every move; copy the last one into walk.ino.

#include <Arduino.h>

//                  R1   R2   L1   L2   R4   R3   L3   L4
const int PINS[8] = { 1,   2,   4,   6,   8,  10,  13,  14};
const int LO[8]   = {45,   5,   5,   0,   0,   0,   0,   0};
const int HI[8]   = {155,130, 150, 130, 155, 155, 155, 155};
const int MID[8]  = {100, 68,  78,  65,  78,  78,  78,  78};
// Which way is "forward" for each hip and "up" for each knee. Same as walk.ino.
const int DIR[8]  = { +1, -1,  -1,  +1,  +1,  -1,  +1,  -1};

const int STEP = 3;
int height = 0;     // bigger = feet higher
int reach  = 0;     // bigger = hips further forward

int value(int m) {
  int v = (m < 4) ? MID[m] + DIR[m] * reach     // hips
                  : MID[m] + DIR[m] * height;   // knees
  return constrain(v, LO[m], HI[m]);
}

void writeAll() {
  for (int m = 0; m < 8; m++) {
    int us = 732 + (int)((2197L * value(m)) / 180);
    uint32_t duty = (uint32_t)((long)us * 16383L / 20000L);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcWrite(PINS[m], duty);
#else
    ledcWrite(m, duty);
#endif
  }
  Serial.print("  static int STAND[8] = { ");
  for (int m = 0; m < 8; m++) Serial.printf("%d%s", value(m), m < 7 ? ", " : " ");
  Serial.println("};");
}

void setup() {
  for (int m = 0; m < 8; m++) {          // clear anything left from the last sketch
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(PINS[m]);
    ledcAttach(PINS[m], 50, 14);
#else
    ledcDetachPin(PINS[m]);
    ledcSetup(m, 50, 14);
    ledcAttachPin(PINS[m], m);
#endif
  }
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n  d = legs down   u = legs up   f = hips forward   b = hips back   x = let go\n");
  writeAll();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if      (c == 'd') { height -= STEP; writeAll(); }
    else if (c == 'u') { height += STEP; writeAll(); }
    else if (c == 'f') { reach  += STEP; writeAll(); }
    else if (c == 'b') { reach  -= STEP; writeAll(); }
    else if (c == 'x') {
      for (int m = 0; m < 8; m++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
        ledcDetach(PINS[m]);
#else
        ledcDetachPin(PINS[m]);
#endif
        pinMode(PINS[m], INPUT);
      }
      Serial.println("  let go.");
    }
  }
}
