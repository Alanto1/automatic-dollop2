// Bench test for the pump driver. No libraries, no servos, no robot logic.
//
// Wire the driver first -- see ../PUMP_AND_CLIFF.md. Then:
//
//   a          arm / disarm. Starts DISARMED: nothing fires until you arm it.
//   f          fire 200 ms
//   <number>   fire that many ms, e.g. 150   (clamped to 50..300)
//   m          MEASURE run: 2 seconds, so a multimeter has time to settle.
//              Read the voltage across the pump terminals while it runs.
//
// ⚠️ THE PUMP MUST BE UNDER WATER for every test. It is lubricated and cooled
//    by the water it moves; run dry it wears out in seconds.
//
// ⚠️ Pull the disable jumper and nothing can fire, whatever this code says.
//    That jumper is interlock 5 and it is the one that does not trust software.
//
// Board: LOLIN S2 Mini, USB CDC On Boot: Enabled.

#include <Arduino.h>

static const int PUMP_PIN = 11;            // -> 100 ohm -> IRLZ44N gate
static const int MAX_MS = 300;             // a squirt, not a jet (BEHAVIOURS.md)
static const int MIN_MS = 50;
static const int MEASURE_MS = 2000;        // long enough for a meter to read
static const unsigned long COOLDOWN_MS = 1000;

static const int SERVO_PINS[8] = {1, 2, 4, 6, 8, 10, 13, 14};

static bool armed = false;
static unsigned long lastFire = 0;

static void pump(bool on) { digitalWrite(PUMP_PIN, on ? HIGH : LOW); }

static bool ready() {
  if (!armed) { Serial.println("  DISARMED -- press a to arm"); return false; }
  if (millis() - lastFire < COOLDOWN_MS) { Serial.println("  cooling down, wait a second"); return false; }
  return true;
}

static void fire(int ms) {
  if (!ready()) return;
  ms = constrain(ms, MIN_MS, MAX_MS);
  pump(true);
  delay(ms);                 // blocking on purpose: the pump CANNOT be left on
  pump(false);
  lastFire = millis();
  Serial.printf("  fired %d ms\n", ms);
}

static void measure() {
  if (!ready()) return;
  Serial.println("  MEASURE: pump on for 2 s. Read the volts across the pump NOW.");
  pump(true);
  delay(MEASURE_MS);
  pump(false);
  lastFire = millis();
  Serial.println("  off. Aim for about 3.0 V across the pump (2.7 - 3.3 is fine).");
  Serial.println("  Higher -> more resistance.  Lower -> less. See PUMP_AND_CLIFF.md.");
}

void setup() {
  // Pump OFF before anything else. The 10k gate pull-down covers the moment
  // between power-on and this line; this covers everything after it.
  digitalWrite(PUMP_PIN, LOW);
  pinMode(PUMP_PIN, OUTPUT);
  pump(false);

  // LEDC survives a reflash: if the last sketch was walking, its servo pulses
  // would still be running. Stop them.
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(SERVO_PINS[i]);
#else
    ledcDetachPin(SERVO_PINS[i]);
#endif
    pinMode(SERVO_PINS[i], INPUT);
  }

  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}
  Serial.println("\n  pump test -- GPIO 11. DISARMED.");
  Serial.println("  a arm/disarm   f fire 200ms   <number> fire that many ms   m 2 s measure run");
  Serial.println("  Pump under water for every test.\n");
}

void loop() {
  static long num = -1;
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= '0' && c <= '9') { num = (num < 0 ? 0 : num) * 10 + (c - '0'); continue; }
    if (num >= 0) { fire((int)num); num = -1; if (c == '\n' || c == '\r') continue; }
    if (c == 'a' || c == 'A') {
      armed = !armed;
      Serial.println(armed ? "  ARMED" : "  disarmed");
    }
    if (c == 'f' || c == 'F') fire(200);
    if (c == 'm' || c == 'M') measure();
  }
}
