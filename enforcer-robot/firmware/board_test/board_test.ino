// Acceptance test for the ESP32-S2 Mini, before it goes anywhere near a robot.
//
// You bought three boards from a marketplace seller. Two things are worth
// knowing before you solder a harness to one:
//
//   1. Does it work at all?
//   2. Does it have the 2MB of PSRAM the listing claims? Cheap clones
//      routinely ship an S2 *without* PSRAM in a listing that promises it,
//      and nothing tells you until something fails months later. This sketch
//      writes a pattern to PSRAM and reads it back, so a lying board fails
//      here instead of on the robot.
//
// Run it on EVERY board as it arrives, label the good ones, and return the
// bad ones while the return window is still open.
//
// Arduino IDE setup for the S2 Mini:
//   Board:              "LOLIN S2 Mini"  (ESP32 boards package)
//   USB CDC On Boot:    ENABLED     <-- without this Serial prints nothing
//   PSRAM:              ENABLED     <-- without this the PSRAM test fails
//   Upload Speed:       921600
//
// To get into bootloader mode: hold 0/BOOT, tap RST, release BOOT.

#include <Wire.h>
#include <WiFi.h>

// esp_chip_info() used to arrive transitively via esp_system.h. ESP32 Arduino
// core 3.x split it into its own header, so it has to be included explicitly
// or CHIP_ESP32S2 and friends are "not declared in this scope".
#include "esp_chip_info.h"

// ---------------------------------------------------------------------------
// Pins
// ---------------------------------------------------------------------------

// Onboard LED on the LOLIN S2 Mini.
static const int LED_PIN = 15;

// Eight GPIOs standing in for the eight servos. All safe on the S2 Mini:
// not strapping pins (0, 45, 46), not USB (19, 20), not SPI flash/PSRAM
// (26-32), and 22-25 do not exist on this chip at all.
static const int SERVO_PINS[8] = {1, 2, 3, 4, 5, 6, 7, 8};

// LOLIN S2 Mini's documented I2C defaults. If your OLED does not show up,
// try 8/9 -- board variants disagree, and the scan below tells you either way.
static const int I2C_SDA = 33;
static const int I2C_SCL = 35;

// Servo timing. 50Hz, 16-bit resolution.
static const int SERVO_HZ = 50;
static const int SERVO_BITS = 16;

static int failures = 0;

static void report(const char* name, bool ok, const char* detail = "") {
  Serial.printf("[%s] %-28s %s\n", ok ? "PASS" : "FAIL", name, detail);
  if (!ok) failures++;
}

// ---------------------------------------------------------------------------

void testChipIdentity() {
  Serial.println("\n--- 1. Is this the chip you paid for? ---");

  esp_chip_info_t info;
  esp_chip_info(&info);
  Serial.printf("     model      : %d (9 = ESP32-S2)\n", info.model);
  Serial.printf("     revision   : %d\n", info.revision);
  Serial.printf("     cores      : %d  (the S2 is single-core, 1 is correct)\n",
                info.cores);
  Serial.printf("     cpu freq   : %lu MHz\n", (unsigned long)getCpuFrequencyMhz());

  report("chip is an ESP32-S2", info.model == CHIP_ESP32S2);

  // The S2 has WiFi and NO Bluetooth. A board claiming BT is not an S2.
  report("has WiFi", (info.features & CHIP_FEATURE_WIFI_BGN) != 0);
}

void testFlash() {
  Serial.println("\n--- 2. Flash ---");
  uint32_t sz = ESP.getFlashChipSize();
  Serial.printf("     flash size : %lu bytes (%.1f MB)\n",
                (unsigned long)sz, sz / 1048576.0);
  Serial.printf("     sketch free: %lu bytes\n",
                (unsigned long)ESP.getFreeSketchSpace());
  // Listing says 4MB. Anything less and the seller misdescribed it.
  report("flash >= 4MB", sz >= 4 * 1024 * 1024);
}

void testPsram() {
  Serial.println("\n--- 3. PSRAM -- the one that catches bad boards ---");

  size_t sz = ESP.getPsramSize();
  Serial.printf("     psram size : %u bytes (%.2f MB)\n",
                (unsigned)sz, sz / 1048576.0);

  if (sz == 0) {
    report("psram present", false,
           "0 bytes: either PSRAM is disabled in the IDE, or the board has none");
    return;
  }
  report("psram >= 2MB", sz >= 2 * 1024 * 1024);

  // Reporting a size proves nothing -- write a pattern and read it back.
  const size_t N = 256 * 1024;
  uint32_t* buf = (uint32_t*)ps_malloc(N);
  if (!buf) {
    report("psram allocates", false, "ps_malloc returned NULL");
    return;
  }
  const size_t words = N / sizeof(uint32_t);
  for (size_t i = 0; i < words; i++) buf[i] = (uint32_t)(i * 2654435761u);
  bool ok = true;
  size_t bad = 0;
  for (size_t i = 0; i < words; i++) {
    if (buf[i] != (uint32_t)(i * 2654435761u)) { ok = false; bad++; }
  }
  free(buf);

  char detail[64] = "";
  if (!ok) snprintf(detail, sizeof(detail), "%u words wrong of %u",
                    (unsigned)bad, (unsigned)words);
  report("psram reads back correctly", ok, detail);
}

void testLed() {
  Serial.println("\n--- 4. Onboard LED (watch the board) ---");
  pinMode(LED_PIN, OUTPUT);
  for (int i = 0; i < 6; i++) {
    digitalWrite(LED_PIN, i % 2);
    delay(150);
  }
  digitalWrite(LED_PIN, LOW);
  Serial.println("     LED should have blinked 3 times. If not, check LED_PIN.");
}

void testGpio() {
  Serial.println("\n--- 5. The 8 servo GPIOs ---");
  // Nothing is connected yet, so this only proves the pin can be driven and
  // read back -- enough to catch a dead pin or a solder bridge on the header.
  bool all = true;
  for (int i = 0; i < 8; i++) {
    int p = SERVO_PINS[i];
    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH); delayMicroseconds(50);
    bool hi = digitalRead(p);
    digitalWrite(p, LOW);  delayMicroseconds(50);
    bool lo = digitalRead(p);
    pinMode(p, INPUT);
    if (!(hi && !lo)) {
      Serial.printf("     GPIO%-2d FAILED (read %d then %d)\n", p, hi, lo);
      all = false;
    }
  }
  report("all 8 servo GPIOs toggle", all);
}

void testPwm() {
  Serial.println("\n--- 6. Eight PWM channels at once ---");
  // THE test that matters for this robot. The ESP32-S2's LEDC peripheral has
  // exactly 8 channels -- not 16 like the original ESP32 -- and Sesame needs
  // exactly 8 servos. There is no spare channel. If you later want a 9th PWM
  // output (a pump on PWM, an RGB LED), it cannot come from LEDC on this chip.
  bool all = true;
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    if (!ledcAttach(SERVO_PINS[i], SERVO_HZ, SERVO_BITS)) {
      Serial.printf("     channel for GPIO%-2d FAILED to attach\n", SERVO_PINS[i]);
      all = false;
      continue;
    }
    // 1.5ms of a 20ms period = servo centre.
    ledcWrite(SERVO_PINS[i], (uint32_t)((1.5 / 20.0) * ((1 << SERVO_BITS) - 1)));
#else
    ledcSetup(i, SERVO_HZ, SERVO_BITS);
    ledcAttachPin(SERVO_PINS[i], i);
    ledcWrite(i, (uint32_t)((1.5 / 20.0) * ((1 << SERVO_BITS) - 1)));
#endif
  }
  report("8 LEDC channels attached", all,
         all ? "1.5ms pulse on all 8 -- scope or servo-check it" : "");

  delay(500);
  for (int i = 0; i < 8; i++) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcDetach(SERVO_PINS[i]);
#else
    ledcDetachPin(SERVO_PINS[i]);
#endif
  }
}

void testI2c() {
  Serial.println("\n--- 7. I2C bus (the OLED) ---");
  Wire.begin(I2C_SDA, I2C_SCL);
  int found = 0;
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("     device at 0x%02X%s\n", a,
                    (a == 0x3C || a == 0x3D) ? "  <- SSD1306 OLED" : "");
      found++;
    }
  }
  if (found == 0) {
    Serial.println("     nothing found. Expected if the OLED is not wired yet.");
    Serial.printf("     When it is: SDA=GPIO%d SCL=GPIO%d, and it needs 3.3V + GND.\n",
                  I2C_SDA, I2C_SCL);
  }
}

void testWifi() {
  Serial.println("\n--- 8. WiFi (the link to the Pi) ---");
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  int n = WiFi.scanNetworks();
  Serial.printf("     %d networks found\n", n);
  for (int i = 0; i < n && i < 5; i++) {
    Serial.printf("       %-24s %4d dBm\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
  }
  Serial.printf("     MAC: %s\n", WiFi.macAddress().c_str());
  // Zero networks in a city means the radio or the antenna is dead.
  report("wifi radio works", n > 0, n > 0 ? "" : "0 networks -- suspect the antenna");
  WiFi.scanDelete();
}

void testHeap() {
  Serial.println("\n--- 9. Memory ---");
  Serial.printf("     free heap  : %lu bytes\n", (unsigned long)ESP.getFreeHeap());
  Serial.printf("     min free   : %lu bytes\n", (unsigned long)ESP.getMinFreeHeap());
  report("heap > 100KB free", ESP.getFreeHeap() > 100000);
}

// ---------------------------------------------------------------------------

void setup() {
  Serial.begin(115200);
  // Native USB CDC takes a moment to enumerate. Without this wait the first
  // few lines vanish and it looks like the board is dead.
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 3000) delay(10);
  delay(300);

  Serial.println("\n\n===============================================");
  Serial.println("  ESP32-S2 Mini acceptance test");
  Serial.println("===============================================");

  testChipIdentity();
  testFlash();
  testPsram();
  testLed();
  testGpio();
  testPwm();
  testI2c();
  testWifi();
  testHeap();

  Serial.println("\n===============================================");
  if (failures == 0) {
    Serial.println("  ALL CHECKS PASSED -- label this board and keep it");
  } else {
    Serial.printf("  %d CHECK(S) FAILED -- see above\n", failures);
    Serial.println("  If PSRAM failed: first re-check that PSRAM is ENABLED");
    Serial.println("  in the IDE. If it still fails, the board is misdescribed");
    Serial.println("  and you should return it.");
  }
  Serial.println("===============================================");
}

void loop() {
  // Slow heartbeat, so you can tell the board is alive and not in a boot loop.
  digitalWrite(LED_PIN, HIGH); delay(80);
  digitalWrite(LED_PIN, LOW);  delay(1920);
}
