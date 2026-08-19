# Six circuits, built from first principles

Step-by-step builds with the circuit explained before it is wired. Companion
to [`MODULE_REFERENCE.md`](MODULE_REFERENCE.md), [`LAB_MANUAL.md`](LAB_MANUAL.md)
and [`ROADMAP.md`](ROADMAP.md).

Chosen because each one teaches something the rest of the kit reuses. Roughly
12 hours total.

**Wire with the USB unplugged, every time.** Plug in only once the wiring is
done and checked.

---

## 1. Driving a motor with a transistor

*~90 min · lab manual #32 · this is your wristband's motor circuit*

### The idea

An Arduino pin supplies about 20mA safely, 40mA absolute maximum. The kit's
motor wants 150-250mA running, more at startup. Connect it directly and you
get a twitching motor, a dead pin, or both.

So the pin doesn't power the motor — it *controls* something that does.

**The base resistor.** The base-emitter junction is a forward-biased diode:
~0.7V drop, then it conducts freely. Without a resistor the pin sees nearly a
short. With 220Ω, base current is (5 − 0.7) ÷ 220 = **19.5mA**, and a
transistor with gain ~100 passes 200mA+ at the collector.

**The flyback diode.** A motor is a coil, and a coil resists sudden current
changes. Switch it off and the collapsing field generates a reverse spike of
hundreds of volts. The diode sits backwards across the motor — invisible in
normal running, but it gives that spike a harmless loop instead of letting it
punch through your transistor.

```
   +5V rail ─────┬───────────────┬─────────────
                 │               │
              [MOTOR]         [DIODE]   band (cathode) toward +5V
                 │               │
                 ├───────────────┘
                 │
                 C
   D9 ──[220Ω]── B    PN2222     flat face toward you, legs down:
                 E                        E   B   C
                 │
   GND rail ─────┴───────────────────────────────
```

### Wiring

1. USB unplugged. Transistor in the breadboard, **flat face toward you**.
   Left = emitter, middle = base, right = collector.
2. Emitter → ground rail.
3. 220Ω from **D9** to the base.
4. One motor lead → **+5V rail**; the other → collector.
5. Diode across the motor leads, **banded end on the +5V side**.
6. Arduino 5V → + rail, GND → − rail.
7. Check the diode band again, then plug in.

> ⚠️ Fitted backwards, the diode is a permanent short across your supply from
> the instant you power up.

### Code

```cpp
const int MOTOR_PIN = 9;   // must be PWM-capable

void setup() {
  pinMode(MOTOR_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // Watch closely: nothing moves for the first part of this range, then it
  // suddenly starts. Below that threshold there isn't enough torque to
  // overcome static friction.
  for (int duty = 0; duty <= 255; duty++) {
    analogWrite(MOTOR_PIN, duty);
    Serial.println(duty);
    delay(20);
  }
  for (int duty = 255; duty >= 0; duty--) {
    analogWrite(MOTOR_PIN, duty);
    delay(20);
  }
}
```

### Test

1. Motor ramps up and back down repeatedly.
2. Note the number where it **first starts turning** — your minimum useful duty.
3. Note where it **stops** on the way down. It's lower. A spinning motor needs
   less torque than a stationary one — mechanical hysteresis, the same shape of
   problem as the sensor hysteresis in project #8.

| Symptom | Cause |
|---|---|
| Nothing at all | Transistor pinout wrong. Multimeter diode test: from the base you should read a drop to *both* other legs. |
| Board resets on start | Inrush dragging the rail down. Add a 100µF cap across the rails (stripe to ground). |
| Weak, buzzes | Motor wired between the pin and collector instead of +5V and collector. |
| Instantly hot, smell | Diode backwards. Unplug now. |
| No speed control | Not a PWM pin. Only 3, 5, 6, 9, 10, 11. |

**Extend it:** add a pot on A0 for speed, then use your measured minimum duty
to `map()` the knob onto *useful* duty only — so the bottom of the range is the
slowest speed that actually turns, not a dead zone.

---

## 2. Ultrasonic parking sensor

*~90 min · lab manual #9, #10 · your wristband in kit form*

### The idea

Raise `Trig` for 10µs; the module emits eight 40kHz clicks and raises `Echo`.
`Echo` stays high exactly as long as the sound takes to fly out and back.

Sound travels 343 m/s = 0.343 mm/µs, and covers the distance twice:

```
distance_mm = microseconds × 0.343 ÷ 2 = microseconds × 0.1715
```

Derive that rather than copying the "divide by 58" everyone quotes — 58 is the
same number rearranged for centimetres.

The second half is the interesting half: turning continuous distance into
**zones**, each with its own beep pattern. That is exactly what
`HapticMapper.h` does in your real project.

```
   UNO                        HC-SR04
   5V  ───────────────────────  VCC
   D10 ──── 10µs pulse out ───  Trig
   D11 ──── HIGH for flight ──  Echo
   GND ───────────────────────  GND

   D8  ──── [passive buzzer] ──── GND
```

### Wiring

1. `VCC` → 5V, `GND` → GND.
2. `Trig` → D10, `Echo` → D11.
3. Passive buzzer + → D8, − → GND. (The shorter one, green PCB visible underneath.)

### Code

```cpp
// Note the zone logic is a separate function touching no hardware — the same
// separation as HapticMapper.h. That's what makes it testable and portable.

const int TRIG = 10, ECHO = 11, BUZZER = 8;

long readDistanceMm() {
  digitalWrite(TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);   // the start pulse
  digitalWrite(TRIG, LOW);

  // 30ms timeout ≈ 5m. Without it, a missing echo blocks for a full second.
  unsigned long us = pulseIn(ECHO, HIGH, 30000UL);
  if (us == 0) return -1;

  return (long)(us * 343UL / 2000UL);   // µs -> mm
}

// Zone -> gap between beeps in ms. 0 = silent, -1 = continuous.
int beepGapFor(long mm) {
  if (mm < 0 || mm >= 1000) return 0;     // far, or no reading
  if (mm >= 600)            return 400;   // medium
  if (mm >= 250)            return 150;   // near
  return -1;                              // critical
}

unsigned long lastBeep = 0;
bool beeping = false;

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  Serial.begin(9600);
}

void loop() {
  long mm  = readDistanceMm();
  int  gap = beepGapFor(mm);
  Serial.println(mm);

  if (gap == 0) {
    noTone(BUZZER); beeping = false;
  } else if (gap < 0) {
    tone(BUZZER, 2000); beeping = true;
  } else {
    unsigned long now = millis();          // no delay() anywhere
    if (now - lastBeep >= (unsigned long)gap) {
      lastBeep = now;
      beeping = !beeping;
      if (beeping) tone(BUZZER, 2000); else noTone(BUZZER);
    }
  }
  delay(50);   // the sensor needs a breather between pings
}
```

### Test

1. Serial Plotter: move your hand in. The line should fall smoothly.
2. Check against a ruler at 10cm, 50cm, 1m.
3. Close your eyes and stop your hand 20cm away using only sound. That's the
   real test — the same one your wristband has to pass.

| Symptom | Cause |
|---|---|
| Always −1 | Trig/Echo swapped, or Echo declared as OUTPUT. |
| Wildly unstable | Soft or angled surface. Try a flat wall. Check the 50ms gap. |
| Reads ~0 constantly | Something inside the 2cm minimum range. |
| Buzzer only clicks | You're using the active buzzer. Swap it. |

**Extend it:** add the *fault pattern* your wristband README says is missing.
Right now −1 produces silence, indistinguishable from "nothing ahead". Make a
failed reading beep three times rapidly, pause, repeat. Unplug the sensor
mid-run and confirm you can hear the difference. That's Rung 2 of your roadmap,
done where debugging is cheap.

---

## 3. Eight LEDs from three pins — the 74HC595

*~2 hrs · lab manual #23*

### The idea

Instead of eight bits down eight wires simultaneously, send them one at a time
down one wire and let the chip reassemble them. Two stages:

- The **shift register** is a queue of eight slots. Each clock pulse slides
  everything along one place and drops your new bit in front.
- The **storage register** is a separate snapshot that drives the output pins.
  It updates only when you pulse the **latch**.

Without that second stage you'd watch the bits ripple across the LEDs as they
shift through. The latch makes the update atomic — all eight pins change at
once. Same idea as double-buffering in graphics.

```
  D11 data  ──►┌─────────────────────────────────┐
  D8  clock ──►│ 1  0  1  1  0  0  1  0          │  SHIFT REGISTER
               └──┬──┬──┬──┬──┬──┬──┬──┬─────────┘  (slides right)
                  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼            all 8 at once,
               ┌─────────────────────────────────┐  on latch pulse
  D12 latch ──►│ STORAGE REGISTER — drives pins  │
               └──┬──┬──┬──┬──┬──┬──┬──┬─────────┘
                  ○  ○  ○  ○  ○  ○  ○  ○   Q0..Q7, each via its own 220Ω
```

### Wiring

1. Straddle the chip across the centre gully. The notch marks pin 1; numbering
   runs anticlockwise from there.
2. Pin 16 (VCC) → 5V. Pin 8 (GND) → GND.
3. **Pin 13 (OE) → GND** and **pin 10 (MR) → 5V.** Miss these and the chip
   appears completely dead with no other clue.
4. Pin 14 (DS, data) → D11. Pin 11 (shift clock) → D8. Pin 12 (latch) → D12.
5. Outputs Q0–Q7 are pins **15, 1, 2, 3, 4, 5, 6, 7** — Q0 is pin 15, then it
   jumps to pin 1. Each through its own 220Ω to an LED, then ground.

### Code

```cpp
// Write shiftOut yourself before using the built-in. The clock and latch
// sequence only makes sense once you have typed it out.

const int DATA = 11, CLOCK = 8, LATCH = 12;

void writeByte(byte value) {
  digitalWrite(LATCH, LOW);            // freeze the outputs

  for (int i = 7; i >= 0; i--) {       // most significant bit first
    digitalWrite(DATA, (value >> i) & 1);
    digitalWrite(CLOCK, HIGH);         // rising edge shifts this bit in
    digitalWrite(CLOCK, LOW);
  }

  digitalWrite(LATCH, HIGH);           // copy all 8 to the pins at once
}

void setup() {
  pinMode(DATA, OUTPUT);
  pinMode(CLOCK, OUTPUT);
  pinMode(LATCH, OUTPUT);
}

void loop() {
  for (int n = 0; n < 256; n++) { writeByte(n); delay(120); }
}
```

### Test

1. LEDs count in binary 0–255. The rightmost toggles every step, the next every
   two — that halving pattern confirms your bit order.
2. Then the experiment that teaches the lesson: **move
   `digitalWrite(LATCH, HIGH)` inside the for-loop** so it latches after every
   bit. Re-upload. The pattern now visibly crawls. Put it back.

| Symptom | Cause |
|---|---|
| Nothing lights | OE (13) not to GND, or MR (10) not to 5V. The number one cause. |
| All on permanently | OE floating, or LEDs wired to 5V rather than the outputs. |
| Counts backwards | Q0–Q7 reversed, or your loop counts up. Either fix works. |
| Random flicker | Chip not straddling the gully — one row of legs sharing a strip. |

**Extend it:** drive the 1-digit 7-segment display from the register instead —
it also needs 8 lines, so it's a drop-in swap. You'll need a lookup table
mapping each digit to the byte that lights the right segments.

---

## 4. The LCD1602, wired the hard way

*~90 min · lab manual #24*

### The idea

The display carries an HD44780 controller with its own character memory — send
it bytes and it holds the image with no further attention.

In **4-bit mode** each byte goes as two halves, costing a little time and saving
four pins.

The trap is `V0`, the contrast pin. It is not power and not data: it expects an
*adjustable voltage*, which means a potentiometer wired as a divider with its
**wiper** on V0. Get this wrong and the display is blank or shows solid blocks
while perfectly correct code runs behind it.

```
   UNO                       LCD1602
   D12 ─────────────────────  RS
   D11 ─────────────────────  E
   D5  ─────────────────────  D4
   D4  ─────────────────────  D5
   D3  ─────────────────────  D6
   D2  ─────────────────────  D7
   GND ─────────────────────  RW, VSS
   5V  ─────────────────────  VDD

   5V ──[ 10kΩ pot ]── GND
             │
           wiper ─────────────  V0      ← contrast
```

Note the crossover: Arduino D5 goes to LCD D4, D4 to D5. Follow the list, not
your intuition.

### Wiring

1. `VSS` → GND, `VDD` → 5V, `RW` → GND (you only ever write).
2. Pot outer legs to 5V and GND; **middle leg → V0**.
3. `RS` → D12, `E` → D11.
4. `D4`→D5, `D5`→D4, `D6`→D3, `D7`→D2.
5. `A` → 5V through 220Ω, `K` → GND (the backlight).
6. LCD pins D0–D3 stay unconnected.

### Code

```cpp
// Constructor order is fixed and unforgiving:
// LiquidCrystal(RS, E, D4, D5, D6, D7)

#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  lcd.begin(16, 2);
  lcd.print("Hello, Almaty");
}

void loop() {
  lcd.setCursor(0, 1);          // column 0, row 1 (the second row)
  lcd.print(millis() / 1000);
  lcd.print("s   ");            // trailing spaces wipe the old digits
  delay(200);
}
```

> **Before concluding the code is broken:** turn the contrast pot slowly
> through its *entire* range. Blank screens and solid blocks are both contrast
> symptoms. This wastes more beginner evenings than anything else in the kit.

### Test

1. Sweep the pot until text is crisp.
2. Row 2 counts seconds.
3. Delete the trailing spaces from `"s   "` and re-upload. Watch 9 → 10 → 100:
   old digits stay on screen. The display never clears what you don't
   explicitly overwrite.

| Symptom | Cause |
|---|---|
| Blank, backlight on | Contrast. Sweep the pot fully first. |
| Top row solid blocks | Contrast too high, or never initialised — check RS and E. |
| Garbled characters | D4–D7 in the wrong order, or a loose data wire. |
| Nothing, no backlight | VDD/VSS swapped, or backlight resistor missing. |
| Displays then freezes | RW floating instead of tied to GND. |

**Extend it:** combine with tutorial 2 — live distance on row 1, zone name on
row 2. You'll hit a real problem: updating the LCD is slow and doing it every
loop makes the sensor sluggish. Fix it by only rewriting when the value
*changes*. That instinct is the foundation of every UI you'll build.

---

## 5. Servo control, and the common-ground rule

*~90 min · lab manual #33*

### The idea

A servo is a closed loop in a box: motor, gears, a pot reading the shaft, and a
chip comparing that pot against your command. You give it a *position*, not a
speed, and it drives itself there and holds.

The command is a pulse every 20ms — roughly 1ms for one extreme, 2ms for the
other. The `Servo` library generates it.

The lesson here is power. An SG90 pulls ~700mA stalled, several times what the
UNO's regulator supplies. You don't get an error — the 5V rail sags, the
processor browns out and resets, and it looks exactly like a random software
crash. So the servo gets its own supply.

Which leads to the rule that catches everyone once: **two supplies must share a
ground.** A voltage is a *difference between two points*. Without a shared
reference, your "5V signal" is 5V relative to a ground the servo has never
heard of, and it means nothing.

```
   UNO  D9 ──────── signal ─────────►  SG90 orange
                                        
   Power module 5V ─── power ────────►  SG90 red

   UNO GND ───┬──────────────────────►  SG90 brown
              │
   Module GND ┴   ← common ground. Without this, nothing works.
```

### Wiring

1. Power supply module on the rails, jumpers to **5V**, 9V adapter in its jack.
2. Servo **red** → + rail (from the module, *not* the Arduino's 5V pin).
3. Servo **brown/black** → − rail.
4. Servo **orange** → D9.
5. **Arduino GND → − rail.** This is the step people skip. Don't.
6. Joystick: VCC → 5V, GND → GND, VRx → A0.

### Code

```cpp
#include <Servo.h>

Servo servo;
const int JOY_X = A0;

int centre = 512;   // measured at startup; it's never exactly 512

void setup() {
  servo.attach(9);
  Serial.begin(9600);
  delay(200);
  centre = analogRead(JOY_X);      // calibrate — hands off the stick!
}

void loop() {
  int raw    = analogRead(JOY_X);
  int offset = raw - centre;

  if (abs(offset) < 15) offset = 0;             // deadzone

  int angle = constrain(map(offset, -512, 512, 0, 180), 0, 180);

  servo.write(angle);
  Serial.println(angle);
  delay(15);                                    // let the servo move
}
```

### Test

1. Hands off the stick during power-up — that's when it calibrates.
2. Servo tracks the stick, sits still when released. If it creeps, widen the
   deadzone.
3. Then the diagnostic experiment: **disconnect the Arduino's GND from the
   rail** while everything else stays wired. The servo twitches, jitters, or
   ignores you. Reconnect. You've now seen what a missing common ground looks
   like — remember the symptom, you'll meet it again.

| Symptom | Cause |
|---|---|
| Board resets when servo moves | Servo on the UNO's 5V pin. That's what this tutorial is about. |
| Random twitching | No common ground between the supplies. |
| Buzzes at the ends | Commanded past its mechanical limit. Try 10–170. |
| Drifts when untouched | Deadzone too small, or it calibrated while you held the stick. |

**Extend it:** use `writeMicroseconds()` and find your servo's real endpoints —
they won't be exactly 1000 and 2000µs. Then remap `write()` using your measured
values so 0° and 180° hit true limits without straining. Cheap servos vary a
lot between units.

---

## 6. Radar scanner — the capstone

*~5 hrs · lab manual #50 · Rung 4 of your roadmap*

### The idea

Mount the ultrasonic sensor on the servo, sweep 180°, measure at each angle.
You now have angle-and-distance pairs — polar coordinates, which is exactly
what a radar display shows.

The interesting engineering problem is the **seam between the halves**. You
design a format the Arduino speaks and the browser understands. Keep it boring
and line-based:

```
37,412
38,405
39,1150
```

Angle, comma, millimetres, newline. Trivially parsable, and you can read it
with your own eyes in the Serial Monitor when something breaks. That property
is worth more than compactness.

```
  [servo] ──sets angle──┐
                        ├──►[UNO]──USB serial──►[browser page]
  [HC-SR04] ─measures───┘      "38,405\n"        parse → polar plot
```

The browser uses the **Web Serial API** — Chromium-based browsers only, and it
needs a real user click to open the port.

### Wiring

1. Build tutorial 5's servo circuit, external supply and common ground included.
2. Build tutorial 2's ultrasonic wiring: Trig → D10, Echo → D11.
3. Tape or glue the HC-SR04 to the servo horn, facing out. Turn it by hand
   through the full range first to check it can't snag its own wires.

### Arduino side

```cpp
#include <Servo.h>

Servo servo;
const int TRIG = 10, ECHO = 11;

long readDistanceMm() {
  digitalWrite(TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  unsigned long us = pulseIn(ECHO, HIGH, 30000UL);
  return us == 0 ? -1 : (long)(us * 343UL / 2000UL);
}

void setup() {
  servo.attach(9);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  Serial.begin(115200);        // faster than 9600 — we send a lot of lines
}

void sweep(int from, int to, int step) {
  for (int a = from; a != to; a += step) {
    servo.write(a);
    delay(30);                 // let it arrive before measuring
    long mm = readDistanceMm();
    Serial.print(a); Serial.print(','); Serial.println(mm);
  }
}

void loop() {
  sweep(10, 170, 2);
  sweep(170, 10, -2);
}
```

### Browser side — connection given, drawing is yours

Web Serial's setup is API friction rather than anything conceptual, so here it
is. What you do with each reading is the actual project.

```html
<button id="connect">Connect to Arduino</button>
<canvas id="radar" width="600" height="340"></canvas>

<script>
const canvas = document.getElementById('radar');
const ctx = canvas.getContext('2d');

document.getElementById('connect').addEventListener('click', async () => {
  // Must be triggered by a real click — a page cannot do this on its own.
  const port = await navigator.serial.requestPort();
  await port.open({ baudRate: 115200 });

  // Bytes arrive in arbitrary chunks, NOT one line at a time.
  // So we buffer and split on newlines ourselves.
  const reader = port.readable
    .pipeThrough(new TextDecoderStream())
    .getReader();

  let buffer = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;

    let nl;
    while ((nl = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, nl).trim();
      buffer = buffer.slice(nl + 1);

      const [angle, mm] = line.split(',').map(Number);
      if (!isNaN(angle) && !isNaN(mm)) plot(angle, mm);   // ← YOU WRITE THIS
    }
  }
});

function plot(angle, mm) {
  // Your job. Things to work out:
  //  - mm === -1 means no echo. Draw nothing, or draw it differently?
  //  - Polar to screen x/y. Canvas y grows downward, and 0° should point
  //    somewhere sensible.
  //  - Old readings should fade rather than vanish or pile up forever.
  //  - Pick a max range and scale distances to fit the canvas.
}
</script>
```

> **One port at a time.** The Arduino IDE's Serial Monitor holds the port
> exclusively. Close it before connecting from the browser, or `port.open()`
> fails with a confusing error unrelated to your code.

### Test, in this order

1. Upload. Serial Monitor at **115200**, confirm clean `angle,distance` lines.
   Fix problems here before touching the browser — half the system at a time.
2. Close the Serial Monitor. Open your page, click connect, pick the port.
3. Temporary `console.log(angle, mm)` inside `plot()` — confirm numbers arrive.
4. Only now write the drawing. Wave your hand at the sweeping sensor; a blip
   should appear at the right angle and range.

| Symptom | Cause |
|---|---|
| `navigator.serial` undefined | Not a Chromium browser, or not on https/localhost. |
| `port.open()` fails | Serial Monitor still holding the port. |
| Garbled text | Baud mismatch — both sides 115200. |
| Readings arrive in bursts, some split | You're assuming one `read()` = one line. That's what the buffer loop is for. |
| Distances jump mid-sweep | Measuring while still moving. Increase the delay after `servo.write()`. |
| Servo stutters | Underpowered supply — back to tutorial 5. |

**Extend it, two directions.** *One:* the sensor's cone is ~15° wide, so a
narrow object smears across several degrees — detect and collapse those into
single objects. *Two:* this rig is exactly what lab manual #55 needs to measure
your wristband's real field of view. Log a full sweep and chart where a chair
leg stops being detected. That turns a limitation your README currently only
asserts into measured evidence.

---

## What these six cover

Current limiting, transistor switching, inductive kickback, time-of-flight
ranging, non-blocking timing, serial-to-parallel conversion, latching, parallel
display interfacing, closed-loop position control, power domains, common
grounds, and protocol design across a hardware/software boundary.

Everything else in the 55-project lab manual is a recombination of those ideas.
Once these six are solid, the rest is variation rather than new territory.
