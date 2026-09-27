// Find the Stand pose for walk.ino in one flash.
//
// All eight servos hold at once. Pick a joint with 1-8, nudge it with + and -,
// and the other seven stay put. Press p and it prints a STAND[] line ready to
// paste into walk.ino.
//
// Put the robot's body on a box or roll of tape first, legs hanging free.
// 'h' snaps all eight to their starting values at once, and you want no
// weight on the legs when that happens.
//
//   h        hold -- take all eight
//   1-8      pick a joint (motor order, printed as you pick)
//   + / -    nudge 1
//   > / <    nudge 5
//   ?        show all eight
//   p        print the STAND[] line
//   l        limp all eight

#include <Arduino.h>

//                                0=R1 1=R2 2=L1 3=L2 4=R4 5=R3 6=L3 7=L4
static const int   PINS[8] = {    1,   2,   4,   6,   8,  10,  13,  14 };
static const char *NAME[8] = { "R1","R2","L1","L2","R4","R3","L3","L4" };
static const int   LO[8]   = {   45,   5,   5,   0,   0,   0,   0,   0 };
static const int   HI[8]   = {  155, 130, 150, 130, 155, 155, 155, 155 };

// Starting guesses: the middle of each measured range.
static int pos[8] = { 100, 68, 78, 65, 78, 78, 78, 78 };

static int  sel  = 0;
static bool live = false;

static void write1(int m) {
  pos[m] = constrain(pos[m], LO[m], HI[m]);
  if (!live) return;
  int us = 732 + (int)((2197L * pos[m]) / 180);
  uint32_t duty = (uint32_t)((long)us * 16383L / 20000L);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PINS[m], duty);
#else
  ledcWrite(m, duty);
#endif
}

static void holdAll() {
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(PINS[i], 50, 14);
#else
    ledcSetup(i, 50, 14);
    ledcAttachPin(PINS[i], i);
#endif
  }
  live = true;
  for (int i = 0; i < 8; i++) write1(i);
  Serial.println("  holding all eight.");
}

static void limpAll() {
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(PINS[i]);
#else
    ledcDetachPin(PINS[i]);
#endif
    pinMode(PINS[i], INPUT);
  }
  live = false;
  Serial.println("  LIMP -- all eight free.");
}

static void showOne() {
  Serial.printf("  %s = %3d   (range %d-%d)\n", NAME[sel], pos[sel], LO[sel], HI[sel]);
}

static void showAll() {
  Serial.println();
  for (int i = 0; i < 8; i++)
    Serial.printf("  %d  %s  %3d%s\n", i + 1, NAME[i], pos[i], i == sel ? "   <" : "");
  Serial.println();
}

static void printStand() {
  Serial.print("\n  static int STAND[8] = { ");
  for (int i = 0; i < 8; i++) Serial.printf("%3d%s", pos[i], i < 7 ? ", " : " ");
  Serial.println("};\n  //                     R1   R2   L1   L2   R4   R3   L3   L4\n");
}

static void menu() {
  Serial.println("\n  h hold all   l limp all   1-8 pick joint");
  Serial.println("  + / - nudge 1   > / < nudge 5   ? show all   p print STAND[]");
  Serial.println("  1=R1 2=R2 3=L1 4=L2 5=R4 6=R3 7=L3 8=L4\n");
}

void setup() {
  for (int i = 0; i < 8; i++) {          // LEDC survives a reflash
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(PINS[i]);
#else
    ledcDetachPin(PINS[i]);
#endif
    pinMode(PINS[i], INPUT);
  }
  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}
  Serial.println("\n  stand finder -- all LIMP. Body on a box, legs free, then press h.");
  menu();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= '1' && c <= '8') { sel = c - '1'; showOne(); continue; }
    switch (c) {
      case 'h': case 'H': holdAll();                         break;
      case 'l': case 'L': limpAll();                         break;
      case '+': case '=': pos[sel] += 1; write1(sel); showOne(); break;
      case '-':           pos[sel] -= 1; write1(sel); showOne(); break;
      case '>':           pos[sel] += 5; write1(sel); showOne(); break;
      case '<':           pos[sel] -= 5; write1(sel); showOne(); break;
      case '?':           showAll();                         break;
      case 'p': case 'P': printStand();                      break;
      default: break;
    }
  }
}
