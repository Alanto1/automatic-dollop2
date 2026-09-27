// A crawl gait on the measured joint ranges. No libraries.
//
// This is a bridge, not a replacement for stock Sesame firmware. Upstream's
// gait is tuned to these exact link lengths and has been walked by more than
// one robot; this one has not. Use it to see the thing move, then go and do
// the real calibration.
//
// --- YOU MUST FILL IN STAND[] FIRST ------------------------------------
//
// STAND[] is the pose where the robot rests on all four feet, bearing its
// own weight, legs splayed evenly. Everything below is computed as an offset
// from it, so if STAND is wrong the gait is wrong and no amount of tuning
// the other numbers will save it.
//
// Find it with the jog tool, one joint at a time, robot on the desk:
//   - knees first: lower each until the foot takes weight
//   - then hips: splay the legs evenly, looking down from above
//   - write each number into STAND[] below
//
// --- WHAT IT DOES ------------------------------------------------------
//
// A crawl: one foot in the air at a time, three always planted. That is the
// gait for a robot that cannot catch itself -- a trot is faster and needs
// the machine to tolerate two-foot support, which MG90S servos and a PLA
// frame do not do gracefully.
//
// Per leg, per cycle: knee lifts, hip swings forward, knee lowers, then the
// hip pushes back through the remaining three quarters. That last part is
// stance, and it is what actually moves the robot.
//
//   s   stand -- ease into STAND[] and hold
//   w   walk
//   x   stop and go limp
//
// ⚠️ Eight servos moving at once is the largest load this robot has drawn.
// If the board resets mid-gait, that is a brownout, not a bug: the legs will
// all jump back to STAND. Slow the gait down or improve the power path.

#include <Arduino.h>

// Motor order is Sesame's, and it is NOT grouped by leg.
//   0=R1  1=R2  2=L1  3=L2  4=R4  5=R3  6=L3  7=L4
static const int PINS[8] = {1, 2, 4, 6, 8, 10, 13, 14};
static const char *NAME[8] = {"R1", "R2", "L1", "L2", "R4", "R3", "L3", "L4"};

// Measured safe travel. Nothing is ever commanded outside these.
static const int LO[8] = { 45,   5,   5,   0,   0,   0,   0,   0 };
static const int HI[8] = {155, 130, 150, 130, 155, 155, 155, 155 };

// >>> FILL THESE IN. Placeholders are range midpoints and will NOT stand. <<<
static int STAND[8] = { 100,  68,  78,  65,  78,  78,  78,  78 };

// Which way each joint moves the leg where we want it.
//   hips  (0-3): +1 if a BIGGER number swings the leg FORWARD
//   knees (4-7): +1 if a BIGGER number RAISES the foot
// From the measured table: R3 and L4 have 0 at the top, R4 and L3 at the
// bottom. R1's direction was never established -- flip it if leg R1 walks
// backwards while the others walk forwards.
static const int DIR[8] = {
  +1,   // R1  hip   <- UNVERIFIED, flip if wrong
  -1,   // R2  hip   5 = front, so forward is downward
  -1,   // L1  hip   5 = front
  +1,   // L2  hip   0 = left, 130 = front
  +1,   // R4  knee  0 = bottom, so up is upward
  -1,   // R3  knee  0 = top
  +1,   // L3  knee  0 = bottom
  -1,   // L4  knee  0 = top
};

// One leg is a hip and a knee, and they are not adjacent motor numbers.
static const int HIP[4]  = {0, 1, 2, 3};      // R1  R2  L1  L2
static const int KNEE[4] = {5, 4, 6, 7};      // R3  R4  L3  L4

// When each leg swings, as a fraction of the cycle. Consecutive swings must
// not be adjacent legs or the support triangle collapses under the robot.
static const float PHASE[4] = {0.50f, 0.25f, 0.75f, 0.00f};

static const int   LIFT     = 25;      // knee travel during swing
static const int   SWING    = 18;      // hip travel either side of stand
static const int   CYCLE_MS = 3000;    // one full gait cycle
static const int   STEP_MS  = 20;

static bool attached = false;
static int  cur[8];

static void attachAll() {
  if (attached) return;
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(PINS[i], 50, 14);
#else
    ledcSetup(i, 50, 14);
    ledcAttachPin(PINS[i], i);
#endif
  }
  attached = true;
}

static void put(int m, int v) {
  v = constrain(v, LO[m], HI[m]);
  int us = 732 + (int)((2197L * v) / 180);
  uint32_t duty = (uint32_t)((long)us * 16383L / 20000L);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PINS[m], duty);
#else
  ledcWrite(m, duty);
#endif
  cur[m] = v;
}

static void limp() {
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(PINS[i]);
#else
    ledcDetachPin(PINS[i]);
#endif
    pinMode(PINS[i], INPUT);
  }
  attached = false;
  Serial.println("  LIMP -- all eight free.");
}

// Ease into the stand pose over a second. Never snap eight servos at once
// with the robot's weight on them.
static void stand() {
  attachAll();
  int from[8];
  for (int i = 0; i < 8; i++) from[i] = cur[i] ? cur[i] : STAND[i];
  for (int s = 0; s <= 50; s++) {
    for (int i = 0; i < 8; i++)
      put(i, from[i] + (STAND[i] - from[i]) * s / 50);
    delay(20);
  }
  Serial.println("  standing.");
}

static void gaitStep(float t) {
  for (int leg = 0; leg < 4; leg++) {
    float u = t - PHASE[leg];
    while (u < 0.0f) u += 1.0f;

    float hipOff, lift;
    if (u < 0.25f) {                     // swing: foot in the air, going forward
      float k = u / 0.25f;
      lift   = LIFT * sinf(k * PI);      // up and back down within the phase
      hipOff = -SWING + 2.0f * SWING * k;
    } else {                             // stance: foot planted, pushing back
      float k = (u - 0.25f) / 0.75f;
      lift   = 0.0f;
      hipOff = SWING - 2.0f * SWING * k;
    }

    int h = HIP[leg], n = KNEE[leg];
    put(h, STAND[h] + (int)(DIR[h] * hipOff));
    put(n, STAND[n] + (int)(DIR[n] * lift));
  }
}

static void menu() {
  Serial.println("\n  s  stand and hold");
  Serial.println("  w  walk");
  Serial.println("  x  stop, go limp\n");
}

static bool walking = false;

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

  Serial.println("\n  crawl gait -- all eight LIMP until you press s");
  Serial.println("  Fill in STAND[] before expecting this to work.");
  menu();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 's' || c == 'S') { walking = false; stand(); }
    if (c == 'w' || c == 'W') { if (!attached) stand();
                                walking = true; Serial.println("  walking."); }
    if (c == 'x' || c == 'X') { walking = false; limp(); }
  }

  if (!walking) return;

  static float t = 0.0f;
  t += (float)STEP_MS / CYCLE_MS;
  if (t >= 1.0f) t -= 1.0f;
  gaitStep(t);
  delay(STEP_MS);
}
