// Read and calibrate the four TCRT5000 cliff sensors. No libraries.
//
// Wire them first -- see ../PUMP_AND_CLIFF.md. Then:
//
//   v   live view on / off (on at start): one line every 0.3 s
//   d   record DESK   -- robot standing on your desk, all four sensors over it
//   e   record EDGE   -- lift the robot ~10 cm, or hold each sensor out past
//                        the desk edge, so nothing is under them
//   p   print the threshold line for walk.ino (needs d and e first)
//
// What the numbers mean (12-bit, 0..4095):
//   desk under the sensor -> IR bounces back -> LOW reading
//   nothing under it      -> no reflection   -> HIGH reading
// The threshold is set halfway between the two, per sensor, on YOUR desk.
// A dark matte desk reflects much less than a white one; that is why this is
// measured rather than guessed.
//
// Board: LOLIN S2 Mini, USB CDC On Boot: Enabled.

#include <Arduino.h>

// ADC1 only (GPIO 1-10): ADC2 is unusable while WiFi is up on the S2.
static const int   PIN[4]  = {3, 5, 7, 9};
static const char *NAME[4] = {"front-left", "front-right", "back-left", "back-right"};
static const int   SERVO_PINS[8] = {1, 2, 4, 6, 8, 10, 13, 14};

static int  desk[4], edge[4];
static bool haveDesk = false, haveEdge = false, live = true;

static int readAvg(int pin, int n) {
  long sum = 0;
  for (int i = 0; i < n; i++) { sum += analogRead(pin); delay(2); }
  return (int)(sum / n);
}

static void record(int *dst, const char *what) {
  Serial.printf("  recording %s ...\n", what);
  for (int i = 0; i < 4; i++) dst[i] = readAvg(PIN[i], 100);
  for (int i = 0; i < 4; i++) Serial.printf("    %-12s %4d\n", NAME[i], dst[i]);
}

static void printThresholds() {
  if (!haveDesk || !haveEdge) { Serial.println("  record d (desk) and e (edge) first"); return; }
  bool bad = false;
  int th[4];
  for (int i = 0; i < 4; i++) {
    th[i] = (desk[i] + edge[i]) / 2;
    int margin = edge[i] - desk[i];
    Serial.printf("  %-12s desk %4d  edge %4d  gap %4d  threshold %4d%s\n",
                  NAME[i], desk[i], edge[i], margin, th[i],
                  margin < 400 ? "   <-- TOO CLOSE" : "");
    if (margin < 400) bad = true;
  }
  Serial.println("\n  Paste this into walk.ino, over the existing line:\n");
  Serial.printf("  static const int   CLIFF_THRESH[4] = {%d, %d, %d, %d};\n\n",
                th[0], th[1], th[2], th[3]);
  if (bad) {
    Serial.println("  ⚠️ A sensor with a gap under ~400 cannot tell desk from edge reliably.");
    Serial.println("     Lower it closer to the desk (aim 2-5 mm), check its wiring, or");
    Serial.println("     suspect a dark matte desk -- try it on paper to confirm.");
  }
}

void setup() {
  for (int i = 0; i < 8; i++) {          // LEDC survives a reflash: stop servos
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(SERVO_PINS[i]);
#else
    ledcDetachPin(SERVO_PINS[i]);
#endif
    pinMode(SERVO_PINS[i], INPUT);
  }
  analogReadResolution(12);                // 0..4095 on every core version

  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}
  Serial.println("\n  cliff sensor test -- GPIO 3 5 7 9");
  Serial.println("  v live on/off   d record desk   e record edge   p print thresholds\n");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'v' || c == 'V') live = !live;
    if (c == 'd' || c == 'D') { record(desk, "DESK"); haveDesk = true; }
    if (c == 'e' || c == 'E') { record(edge, "EDGE"); haveEdge = true; }
    if (c == 'p' || c == 'P') printThresholds();
  }

  static unsigned long last = 0;
  if (live && millis() - last > 300) {
    last = millis();
    Serial.print(" ");
    for (int i = 0; i < 4; i++) {
      int v = analogRead(PIN[i]);
      // a crude bar so you can SEE a sensor move from across the desk
      char bar[11]; int n = v * 10 / 4096;
      for (int k = 0; k < 10; k++) bar[k] = k < n ? '#' : '.';
      bar[10] = 0;
      Serial.printf(" %s %4d %s |", NAME[i], v, bar);
    }
    Serial.println();
  }
}
