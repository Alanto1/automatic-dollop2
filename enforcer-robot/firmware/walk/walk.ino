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
//   f   check each hip in turn and FIX any that go backwards (robot on a box)
//   s   stand -- ease into STAND[] and hold
//   w   walk forward        r   walk backward
//   <   turn left           >   turn right       (on the spot)
//   ,   slide left          .   slide right      (sideways, no turning)
//   a   steer left          d   steer right      (trim while it walks)
//   z   raise left side     c   raise right side (level it)
//   u   lift feet higher    j   lift feet lower
//   q   slower              e   faster
//   t   stand taller        b   stand lower      (clear an edge with the body)
//   g   switch crawl <-> trot   -- trot is roughly 3x faster, less stable
//   k   longer steps        i   shorter steps
//   v   flip R1's direction -- the one hip never measured
//   1-4 pick a hip (R1 R2 L1 L2), + / - turn it, p prints the STAND[] line.
//       Pose by eye while it stands: front legs angled forward, rear legs
//       angled back, an X from above.
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

// Knees found with stand_easy: all four 39 steps down from the middle, each in
// its own direction -- the 39 / 117 pairs are DIR[] confirming itself.
// Hips posed by eye on the robot (1-4, + / -) into an even X: front legs
// angled forward, rear legs angled back. The first hip values were range
// midpoints, which splayed the legs so their pushes came out sideways.
static int STAND[8] = {  85,  62,  75,  74,  39, 117,  39, 117 };

// Which way each joint moves the leg where we want it.
//   hips  (0-3): +1 if a BIGGER number swings the leg FORWARD
//   knees (4-7): +1 if a BIGGER number RAISES the foot
// From the measured table: R3 and L4 have 0 at the top, R4 and L3 at the
// bottom. R1's direction was never established -- flip it if leg R1 walks
// backwards while the others walk forwards.
// Not const: the 'f' check flips any hip the user says went the wrong way,
// and 'v' flips R1 by hand. All four hips were CONFIRMED by the 'f' check on
// the robot, R1 included -- none needed flipping.
static int DIR[8] = {
  +1,   // R1  hip   confirmed by the 'f' check
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
// Which side of the robot each leg is on -- measured, not taken from the
// names. The REAR legs are on the opposite sides from their letters: the R2
// servo drives the back-LEFT leg and L2 the back-RIGHT. Walking straight
// could not show this (every leg pushes the same way); turning could, and
// did -- it slid sideways until the rear pair was swapped, then it spun.
//                               R1   R2   L1   L2
static const int SIDE[4]    = {+1,  -1,  -1,  +1};   // + right, - left
// The two diagonals: front-right + back-left against front-left + back-right.
// Opposing these is what makes the robot slide sideways -- see strafeMode.
static const int DIAG[4]    = {+1,  +1,  -1,  -1};
static const int LEG_OF[8] = {0, 1, 2, 3, 1, 0, 2, 3};   // motor -> leg

// Flips the whole robot's idea of forward in one place, so DIR[] can stay a
// record of what was measured on each joint. Set it from the 'f' check, not
// from watching the walk: a gait with the wrong swing order drifts in
// directions that have nothing to do with this sign.
static const int FORWARD_SIGN = +1;

// The FRONT of the robot is the R1 / L1 end, and the layout -- measured -- is:
//
//            FRONT
//      L1+L3      R1+R3
//        [   body   ]
//      R2+R4      L2+L4
//            BACK
//
// When each leg swings, as a fraction of the cycle. This is the lateral-
// sequence crawl -- rear-left, front-left, rear-right, front-right -- the
// statically most stable order for a quadruped: each rear foot lands under
// the body just before the front foot on the same side lifts.
//
// History: the first version guessed the front wrong and lifted the feet in a
// circle round the body (rotated, tilted, reverse not a mirror). The second
// assumed R2 was back-right, which made the order rear-right, front-left,
// rear-left, front-right -- a diagonal sequence. It walked, but with less
// margin; this is the order the measured layout actually calls for.
//                               R1     R2     L1     L2
static const float PHASE[4] = {0.75f, 0.00f, 0.25f, 0.50f};

// Speed is stride over cycle time: 2*SWING of hip travel per CYCLE_MS.
//
// First walk was at SWING 18 / CYCLE 3000 and it walked, slowly. SWING 28 is
// checked against STAND: every hip stays inside its measured range at full
// swing (tightest is L2 at 37-93 of 0-130). Do not take CYCLE_MS much below
// ~1200 -- swing is a quarter of the cycle, and under ~300ms an MG90S cannot
// lift, swing and land, so feet drag and it gets slower, not faster.
static int         swingAmt = 28;      // hip travel either side of stand (k / i live)
static int         liftAmt  = 35;      // knee travel during swing   (u / j live)
                                       // 25 walked the desk; 35 so the step
                                       // clears a 10mm mat edge
static int         cycleMs  = 1500;    // one full gait cycle        (q / e live)
static int         heightOff = 0;      // + stands taller, feet pushed down (t / b live)

// Two gaits. The crawl lifts one foot at a time -- three always down, so it
// cannot fall over, but it is slow: each foot gets only a quarter of the cycle
// to swing, which puts a floor of ~1200ms on the cycle. The trot swings the
// diagonal pairs together (front-right + back-left, then front-left +
// back-right): half the cycle to swing, so the cycle can drop to ~600ms, and
// each foot pushes for a larger share of the time. Roughly three times the
// speed, at the price of standing on two feet while the other two swing.
static bool        trot     = false;   // 'g' switches
                                       // 1500 tuned on the robot: fastest it
                                       // walks cleanly with lift 25
static const int   STEP_MS  = 20;

static bool  attached = false;
static int   cur[8];
static int   walkDir = +1;    // +1 forward, -1 backward: runs the cycle in reverse
static float trim    = 0.0f;  // + lengthens the right-side stride: steers left
static int   lean    = 0;     // + raises the right side of the body
static int   selHip  = 0;     // hip being posed with 1-4 and + / -  (0 = R1)
static int   turnMode = 0;    // 0 straight, -1 turn left, +1 turn right (on the spot)
// Measured: 90 degrees in ~5 s in the crawl at a 1500ms cycle and stride 28,
// so ~27 degrees per cycle. Aiming will need this; re-measure after changing
// gait, stride or cycle.

// Sliding sideways -- kept on purpose. It is what the first turning attempt
// actually did: opposing one diagonal pair against the other cancels the
// fore-aft pushes and adds the sideways ones, so the robot crabs. It uses
// DIAG[], so it is independent of the side table.
static int   strafeMode = 0;  // 0 off, -1 slide left, +1 slide right

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
  // lean: half the feet on one side down, the other side up -- height kept.
  // heightOff: every foot down together -- the body rises.
  return (int)(DIR[m] * (-SIDE[LEG_OF[m]] * lean * 0.5f - heightOff));
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

// 0 below e0, 1 above e1, a smooth S between. Used to shape the swing.
static float smoothBetween(float e0, float e1, float x) {
  float k = (x - e0) / (e1 - e0);
  if (k < 0.0f) k = 0.0f;
  if (k > 1.0f) k = 1.0f;
  return k * k * (3.0f - 2.0f * k);
}

static void gaitStep(float t) {
  // Swing takes this share of the cycle; the rest is stance.
  const float sf = trot ? 0.5f : 0.25f;
  for (int leg = 0; leg < 4; leg++) {
    // Trot: the two diagonals, half a cycle apart. Crawl: one at a time.
    float ph = trot ? (DIAG[leg] > 0 ? 0.0f : 0.5f) : PHASE[leg];
    float u = t - ph;
    while (u < 0.0f) u += 1.0f;

    // Steering: one side takes a longer stride than the other. Trim corrects a
    // straight walk, so it is left out while turning on the spot.
    bool straight = (turnMode == 0 && strafeMode == 0);
    float stride = swingAmt * (straight ? (1.0f + SIDE[leg] * trim) : 1.0f);

    // Turning on the spot: one side walks forward and the other backward.
    // With the legs splayed on the diagonals, each foot's swing already runs
    // roughly round the body, so this spins it rather than walking it off.
    // turnMode +1 (right): left legs forward, right legs back -> clockwise.
    float sideFactor = 1.0f;
    if (turnMode)   sideFactor = (float)(-turnMode   * SIDE[leg]);
    if (strafeMode) sideFactor = (float)(-strafeMode * DIAG[leg]);   // the crab

    float hipOff, lift;
    if (u < sf) {
      // Swing: UP, then ACROSS, then DOWN -- a step over, not a scuff. The
      // first version lifted in a sine arc while the hip moved the whole time,
      // so the foot was low at both ends of the swing and moving forward while
      // low: exactly when it meets the edge of a mat. Now the foot is fully up
      // before it travels and fully across before it comes down.
      float k = u / sf;
      lift   = liftAmt * fminf(smoothBetween(0.0f, 0.3f, k),
                               1.0f - smoothBetween(0.7f, 1.0f, k));
      hipOff = -stride + 2.0f * stride * smoothBetween(0.15f, 0.85f, k);
    } else {                             // stance: foot planted, pushing back
      float k = (u - sf) / (1.0f - sf);
      lift   = 0.0f;
      hipOff = stride - 2.0f * stride * k;
    }

    int h = HIP[leg], n = KNEE[leg];
    put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * sideFactor * hipOff));
    put(n, STAND[n] + (int)(DIR[n] * lift) + kneeLean(n));
  }
}

// Swing each hip forward on its own, hold it, and ASK. A 'n' flips that hip's
// DIR on the spot, so the check fixes what it finds rather than reporting it.
// Robot on a box, legs hanging: the feet must be free to move.
//
// Why this matters more than it looks: the legs stand splayed in an X, so each
// foot pushes diagonally. When all four agree, the sideways parts cancel and
// the robot goes straight. When one DIAGONAL pair disagrees with the other,
// the fore-aft parts cancel and the sideways parts add -- and the robot crabs
// sideways, one way on 'w' and the other on 'r'. That was seen.
static char waitAnswer() {
  while (true) {
    while (!Serial.available()) delay(10);
    char c = Serial.read();
    if (c == 'y' || c == 'Y') return 'y';
    if (c == 'n' || c == 'N') return 'n';
    if (c == 's' || c == 'S') return 's';
  }
}

static void forwardCheck() {
  stand();
  Serial.println("\n  Each hip swings on its own. For each, answer:");
  Serial.println("  did the FOOT move toward the FRONT (the R1 / L1 end)?");
  Serial.println("    y = yes    n = no, it went toward the back    s = straight sideways\n");
  for (int leg = 0; leg < 4; leg++) {
    int h = HIP[leg];
    for (int k = 0; k <= 25; k++) {
      put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * swingAmt * k / 25)); delay(20);
    }
    Serial.printf("  %s  -- toward the front?  y / n / s  ", NAME[h]);
    char a = waitAnswer();
    if (a == 'n') {
      DIR[h] = -DIR[h];
      Serial.printf("flipped, now %+d\n", DIR[h]);
    } else if (a == 's') {
      Serial.println("sideways -- this leg points along the body; tell me which");
    } else {
      Serial.println("ok");
    }
    for (int k = 25; k >= 0; k--) {
      put(h, STAND[h] + (int)(DIR[h] * FORWARD_SIGN * swingAmt * k / 25)); delay(20);
    }
    delay(300);
  }
  Serial.printf("\n  hips now:  R1 %+d   R2 %+d   L1 %+d   L2 %+d\n",
                DIR[0], DIR[1], DIR[2], DIR[3]);
  Serial.println("  Send me that line. Then set it down: s, then w.\n");
}

static void menu() {
  Serial.println("\n  f check each hip and fix any that go backwards (robot on a box)");
  Serial.println("  s stand    w forward    r backward    x stop / limp");
  Serial.println("  < turn left on the spot    > turn right on the spot");
  Serial.println("  , slide left sideways      . slide right sideways");
  Serial.println("  a steer left    d steer right");
  Serial.println("  z raise left side    c raise right side");
  Serial.println("  u lift feet higher   j lift feet lower");
  Serial.println("  q slower             e faster");
  Serial.println("  t stand taller       b stand lower      g crawl <-> TROT (fast)");
  Serial.println("  k longer steps       i shorter steps");
  Serial.println("  v flip R1's direction (the one never measured)");
  Serial.println("  1 2 3 4  pick hip R1 R2 L1 L2   + / -  turn it   p  print pose\n");
}

// Print the stand pose so it can be written back into STAND[], and warn about
// any hip posed so close to a limit that the gait's stride will get cut short
// on one side -- which walks crooked, because that leg pushes less.
static void showStand() {
  Serial.print("  static int STAND[8] = { ");
  for (int i = 0; i < 8; i++) Serial.printf("%d%s", STAND[i], i < 7 ? ", " : " ");
  Serial.println("};");
  for (int h = 0; h < 4; h++)
    if (STAND[h] - LO[h] < swingAmt || HI[h] - STAND[h] < swingAmt)
      Serial.printf("  (%s is near its limit -- its steps will be cut short)\n", NAME[h]);
}

static void showTrim() {
  Serial.printf("  %s   trim %+.2f   lean %+d   height %+d   lift %d   stride %d   cycle %d ms\n",
                trot ? "TROT " : "crawl", trim, lean, heightOff, liftAmt, swingAmt, cycleMs);
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
    if (c == 'w' || c == 'W') { if (!attached) stand(); walkDir = +1; turnMode = 0; strafeMode = 0;
                                walking = true; Serial.println("  walking forward."); }
    if (c == 'r' || c == 'R') { if (!attached) stand(); walkDir = -1; turnMode = 0; strafeMode = 0;
                                walking = true; Serial.println("  walking backward."); }
    if (c == '<')             { if (!attached) stand(); walkDir = +1; turnMode = -1; strafeMode = 0;
                                walking = true; Serial.println("  turning left."); }
    if (c == '>')             { if (!attached) stand(); walkDir = +1; turnMode = +1; strafeMode = 0;
                                walking = true; Serial.println("  turning right."); }
    if (c == ',')             { if (!attached) stand(); walkDir = +1; turnMode = 0; strafeMode = -1;
                                walking = true; Serial.println("  sliding left."); }
    if (c == '.')             { if (!attached) stand(); walkDir = +1; turnMode = 0; strafeMode = +1;
                                walking = true; Serial.println("  sliding right."); }
    if (c == 'x' || c == 'X') { walking = false; limp(); }
    if (c == 'f' || c == 'F') { walking = false; forwardCheck(); }
    if (c >= '1' && c <= '4') { selHip = c - '1';
                                Serial.printf("  posing %s   (stand %d)\n", NAME[selHip], STAND[selHip]); }
    if (c == '+' || c == '=' || c == '-') {
      STAND[selHip] = constrain(STAND[selHip] + (c == '-' ? -3 : 3), LO[selHip], HI[selHip]);
      if (attached && !walking) put(selHip, STAND[selHip]);   // see it move now
      Serial.printf("  %s stand = %d\n", NAME[selHip], STAND[selHip]);
    }
    if (c == 'p' || c == 'P') showStand();
    if (c == 'v' || c == 'V') { DIR[0] = -DIR[0];
                                Serial.printf("  R1 direction is now %+d\n", DIR[0]); }

    bool retrim = false;
    if (c == 'a' || c == 'A') { trim += 0.05f; retrim = true; }
    if (c == 'd' || c == 'D') { trim -= 0.05f; retrim = true; }
    if (c == 'z' || c == 'Z') { lean -= 2;     retrim = true; }
    if (c == 'c' || c == 'C') { lean += 2;     retrim = true; }
    if (c == 'u' || c == 'U') { liftAmt += 5;  retrim = true; }
    if (c == 'j' || c == 'J') { liftAmt -= 5;  retrim = true; }
    if (c == 'q' || c == 'Q') { cycleMs += (trot ? 100 : 250); retrim = true; }
    if (c == 'e' || c == 'E') { cycleMs -= (trot ? 100 : 250); retrim = true; }
    if (c == 't' || c == 'T') { heightOff += 3; retrim = true; }
    if (c == 'b' || c == 'B') { heightOff -= 3; retrim = true; }
    if (c == 'g' || c == 'G') { trot = !trot;
                                cycleMs = trot ? 800 : 1500;   // each gait's own starting pace
                                retrim = true; }
    if (c == 'k' || c == 'K') { swingAmt += 2; retrim = true; }
    if (c == 'i' || c == 'I') { swingAmt -= 2; retrim = true; }
    if (retrim) {
      trim = constrain(trim, -0.4f, 0.4f);
      lean = constrain(lean, -20, 20);
      liftAmt = constrain(liftAmt, 10, 60);
      heightOff = constrain(heightOff, -15, 30);
      // Swing is a quarter of a crawl cycle and half a trot cycle, and it
      // needs ~300ms for an MG90S to lift, cross and land. Hence the floors.
      cycleMs = constrain(cycleMs, trot ? 600 : 1200, 8000);
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
