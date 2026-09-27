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
//   f   check each hip points FORWARD in turn (robot on a box)
//   s   stand -- ease into STAND[] and hold
//   w   walk forward        r   walk backward
//   a   steer left          d   steer right      (trim while it walks)
//   z   raise left side     c   raise right side (level it)
//   u   lift feet higher    j   lift feet lower
//   q   slower              e   faster
//   k   longer steps        i   shorter steps
//   x   stop and go limp
//
// a/d/z/c print the current trim and lean. Once it walks straight and level,
// send those two numbers back so they can be written in as defaults.
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

// Found with stand_easy: hips at their range midpoints, all four knees 39
// steps down from the middle, each in its own direction. The mirror-image
// 39 / 117 pairs are the knee directions in DIR[] confirming themselves.
static int STAND[8] = { 100,  68,  78,  65,  39, 117,  39, 117 };

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
static const int SIDE[4] = {+1, +1, -1, -1};  // right, right, left, left
static const int LEG_OF[8] = {0, 1, 2, 3, 1, 0, 2, 3};   // motor -> leg

// Flips the whole robot's idea of forward in one place, so DIR[] can stay a
// record of what was measured on each joint. Set it from the 'f' check, not
// from watching the walk: a gait with the wrong swing order drifts in
// directions that have nothing to do with this sign.
static const int FORWARD_SIGN = +1;

// The FRONT of the robot is the R1 / L1 end, so the legs are:
//     R1+R3 front-right    L1+L3 front-left
//     R2+R4 rear-right     L2+L4 rear-left
//
// When each leg swings, as a fraction of the cycle. This is the lateral-
// sequence crawl -- rear-left, front-left, rear-right, front-right -- which
// is the statically most stable order for a quadruped: each rear foot lands
// under the body just before the front foot on the same side lifts.
//
// The first version guessed the front and got it wrong, which lifted the feet
// in a circle round the body. That rotates the robot, tilts it, and makes
// backward not the mirror of forward -- all three were seen.
//                               R1     R2     L1     L2
static const float PHASE[4] = {0.75f, 0.50f, 0.25f, 0.00f};

// Speed is stride over cycle time: 2*SWING of hip travel per CYCLE_MS.
//
// First walk was at SWING 18 / CYCLE 3000 and it walked, slowly. SWING 28 is
// checked against STAND: every hip stays inside its measured range at full
// swing (tightest is L2 at 37-93 of 0-130). Do not take CYCLE_MS much below
// ~1200 -- swing is a quarter of the cycle, and under ~300ms an MG90S cannot
// lift, swing and land, so feet drag and it gets slower, not faster.
static int         swingAmt = 28;      // hip travel either side of stand (k / i live)
static int         liftAmt  = 25;      // knee travel during swing   (u / j live)
static int         cycleMs  = 2000;    // one full gait cycle        (q / e live)
static const int   STEP_MS  = 20;

static bool  attached = false;
static int   cur[8];
static int   walkDir = +1;    // +1 forward, -1 backward: runs the cycle in reverse
static float trim    = 0.0f;  // + lengthens the right-side stride: steers left
static int   lean    = 0;     // + raises the right side of the body

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

// Lean is split across both sides -- half the feet on one side go down, half
// on the other go up -- so levelling the body does not change its height.
static int kneeLean(int m) {
  return (int)(DIR[m] * (-SIDE[LEG_OF[m]] * lean * 0.5f));
}

static int standTarget(int m) {
  return (m < 4) ? STAND[m] : STAND[m] + kneeLean(m);
}

// Ease into the stand pose over a second. Never snap eight servos at once
// with the robot's weight on them.
static void stand() {
  attachAll();
  int from[8];
  for (int i = 0; i < 8; i++) from[i] = cur[i] ? cur[i] : standTarget(i);
  for (int s = 0; s <= 50; s++) {
    for (int i = 0; i < 8; i++)
      put(i, from[i] + (standTarget(i) - from[i]) * s / 50);
    delay(20);
  }
  Serial.println("  standing.");
}

static void gaitStep(float t) {
  for (int leg = 0; leg < 4; leg++) {
    float u = t - PHASE[leg];
    while (u < 0.0f) u += 1.0f;

    // Steering: one side takes a longer stride than the other.
    float stride = swingAmt * (1.0f + SIDE[leg] * trim);

    float hipOff, lift;
    if (u < 0.25f) {                     // swing: foot in the air, going forward
      float k = u / 0.25f;
      lift   = liftAmt * sinf(k * PI);   // up and back down within the phase
      hipOff = -stride + 2.0f * stride * k;
    } else {                             // stance: foot planted, pushing back
      float k = (u - 0.25f) / 0.75f;
      lift   = 0.0f;
      hipOff = stride - 2.0f * stride * k;
    }

    int h = HIP[leg], n = KNEE[leg];
    put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * hipOff));
    put(n, STAND[n] + (int)(DIR[n] * lift) + kneeLean(n));
  }
}

// Swing each hip forward on its own and hold it, so a wrong direction is
// obvious and attributable. Robot on a box, legs hanging: the feet must be
// free to move.
static void forwardCheck() {
  stand();
  Serial.println("\n  Each hip in turn should point toward the R1/L1 end (the front).");
  for (int leg = 0; leg < 4; leg++) {
    int h = HIP[leg];
    Serial.printf("  %s ...\n", NAME[h]);
    for (int k = 0; k <= 25; k++) {
      put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * swingAmt * k / 25)); delay(20);
    }
    delay(1500);
    for (int k = 25; k >= 0; k--) {
      put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * swingAmt * k / 25)); delay(20);
    }
    delay(500);
  }
  Serial.println("  done. Any that swung toward the BACK has its DIR flipped.\n");
}

static void menu() {
  Serial.println("\n  f check each hip's forward direction (robot on a box)");
  Serial.println("  s stand    w forward    r backward    x stop / limp");
  Serial.println("  a steer left    d steer right");
  Serial.println("  z raise left side    c raise right side");
  Serial.println("  u lift feet higher   j lift feet lower");
  Serial.println("  q slower             e faster");
  Serial.println("  k longer steps       i shorter steps\n");
}

static void showTrim() {
  Serial.printf("  trim %+.2f   lean %+d   lift %d   stride %d   cycle %d ms\n",
                trim, lean, liftAmt, swingAmt, cycleMs);
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
    if (c == 'w' || c == 'W') { if (!attached) stand(); walkDir = +1;
                                walking = true; Serial.println("  walking forward."); }
    if (c == 'r' || c == 'R') { if (!attached) stand(); walkDir = -1;
                                walking = true; Serial.println("  walking backward."); }
    if (c == 'x' || c == 'X') { walking = false; limp(); }
    if (c == 'f' || c == 'F') { walking = false; forwardCheck(); }

    bool retrim = false;
    if (c == 'a' || c == 'A') { trim += 0.05f; retrim = true; }
    if (c == 'd' || c == 'D') { trim -= 0.05f; retrim = true; }
    if (c == 'z' || c == 'Z') { lean -= 2;     retrim = true; }
    if (c == 'c' || c == 'C') { lean += 2;     retrim = true; }
    if (c == 'u' || c == 'U') { liftAmt += 5;  retrim = true; }
    if (c == 'j' || c == 'J') { liftAmt -= 5;  retrim = true; }
    if (c == 'q' || c == 'Q') { cycleMs += 250; retrim = true; }
    if (c == 'e' || c == 'E') { cycleMs -= 250; retrim = true; }
    if (c == 'k' || c == 'K') { swingAmt += 2; retrim = true; }
    if (c == 'i' || c == 'I') { swingAmt -= 2; retrim = true; }
    if (retrim) {
      trim = constrain(trim, -0.4f, 0.4f);
      lean = constrain(lean, -20, 20);
      liftAmt = constrain(liftAmt, 10, 50);
      cycleMs = constrain(cycleMs, 1200, 8000);   // below ~1200 the feet cannot keep up
      // Capped at 34. Past that, a front leg at the back of its stroke and the
      // rear leg on the same side at the front of its stroke point at almost
      // the same spot -- and in the lateral sequence that is the exact moment
      // the rear leg lands, so they meet.
      swingAmt = constrain(swingAmt, 12, 34);
      showTrim();
      if (attached && !walking)          // standing: show the new lean at once
        for (int i = 0; i < 8; i++) put(i, standTarget(i));
    }
  }

  if (!walking) return;

  // Backward is the forward cycle run in reverse. That also reverses the
  // swing order, which is exactly right: walking backward, the old front legs
  // are the new rear legs. Negating the hip offsets instead would keep the
  // forward swing order, and a gait whose order does not match its direction
  // drifts sideways.
  static float t = 0.0f;
  t += walkDir * (float)STEP_MS / cycleMs;
  if (t >= 1.0f) t -= 1.0f;
  if (t <  0.0f) t += 1.0f;
  gaitStep(t);
  delay(STEP_MS);
}
