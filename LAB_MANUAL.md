# Lab Manual — 55 projects for the Elegoo Most Complete Starter Kit

A study curriculum built around the kit you own, ordered so each project
teaches something the next one assumes. Companion to [`ROADMAP.md`](ROADMAP.md).

**Written 2026-08-11. 55 projects, roughly 108 hours of bench time.**

---

## How to use this

This deliberately gives you **specifications, not sketches.**

Your roadmap's central point is that you can review code but haven't yet
written much yourself, and that only closes by facing an empty file. So
every project below tells you *what to build*, *what it should teach you*,
*how to know you're done*, and *the trap waiting for you* — and stops
there. Writing it is your half.

When you're stuck: try it, get it wrong, then ask me to review what you
wrote. Asking for a review after an honest attempt teaches you far more
than asking for the answer, and you still end up with working code.

### The order matters

Tiers 0-4 build on each other. Skipping Tier 0 and jumping to a game will
work right up until something flickers or drops inputs, and then you won't
have the concepts to diagnose it. **Tier 0 is eight projects and maybe six
hours.** Do it first.

### Marked ★

23 projects are marked ★ — those carry a concept the rest of the curriculum
leans on. If you're short on time, do the starred ones in order and treat
the others as optional practice.

---

## Before you start: three things about your specific kit

**1. Your LCD1602 has no I2C backpack.** The box says "with pin header,"
meaning bare parallel wiring — 6 Arduino pins in 4-bit mode, plus one of
your two 10K potentiometers permanently assigned to contrast. Budget for
that; most online tutorials assume the I2C version and their wiring won't
match yours.

**2. The RC522 RFID module is 3.3V, not 5V.** Its VCC goes to the 3.3V
pin. Connecting it to 5V is the most common way this module gets destroyed.

**3. Your box has a printing error worth noticing.** It lists
"104pF Ceramic Capacitor." The `104` marking means 10 × 10⁴ pF =
100,000pF = **100nF = 0.1µF** — about a thousand times larger than the box
claims. Those are your decoupling capacitors.

That last one is your own rule in action: *reality beats documentation.*
You learned it twice at component counters in Almaty. It applies to
printed labels too.

---

## Safety — read once, properly

- **Never switch mains AC with the relay.** Not supervised, not "carefully,"
  not for a demo. 220V through breadboard contacts is a genuine
  electrocution and fire risk. Switch a 9V battery circuit instead — you
  learn exactly the same thing about relays.
- **Always use a flyback diode across any motor or relay coil.** You
  already know this from the wristband. Back-EMF from a collapsing
  inductive field reaches hundreds of volts and kills boards.
- **Don't power servos or motors from the UNO's 5V pin** for anything
  sustained. The onboard regulator can't supply it; you get brownout
  resets that look like software bugs. Use the power supply module with
  external power, and tie the grounds together.
- **Disconnect power before rewiring.** Every time.
- **The 9V battery is for logic, not motors.** ~500mAh, and it sags badly
  under load.

---

## Index

**Foundations** — 8 projects

1. Blink without delay() ★
2. Serial debugging lab ★
3. Button with real debouncing
4. Toggle latch
5. Traffic light state machine ★
6. PWM fade and the gamma problem
7. Potentiometer → brightness, with map()
8. Photoresistor night light with hysteresis ★

**Sensing** — 12 projects

9. Ultrasonic tape measure ★
10. Parking sensor — your wristband in kit form ★
11. Thermistor thermometer
12. DHT11 environment reader
13. PIR intruder alarm
14. Clap-clap detector
15. Water level alarm
16. Tilt switch orientation sensor
17. Joystick reader with deadzone
18. Rotary encoder counter ★
19. GY-521 tilt angle meter
20. Motion-triggered alarm with filtering

**Display & output** — 11 projects

21. 7-segment digit driver
22. 4-digit multiplexing ★
23. 74HC595 shift register ★
24. LCD1602 first screen
25. LCD custom characters
26. LCD menu system ★
27. MAX7219 matrix and frame buffers
28. Conway's Game of Life ★
29. RGB colour mixing
30. Active vs passive buzzer
31. Melody player with a note table

**Actuators & power** — 6 projects

32. Transistor as a switch ★
33. Servo control and the 50Hz signal ★
34. L293D bidirectional motor control
35. Stepper motor precision positioning ★
36. Relay switching (low voltage only) ★
37. Power budget measurement

**Protocols** — 6 projects

38. I2C bus scanner ★
39. DS1307 real-time clock
40. IR remote decoder
41. IR universal controller
42. RFID card reader ★
43. Keypad matrix scanning

**Integration builds** — 8 projects

44. Weather station with logging
45. Reaction timer game
46. Simon says memory game ★
47. RFID door lock
48. Alarm clock
49. Digital safe
50. Radar scanner with live display ★
51. Temperature-controlled fan ★

**Wristband work** — 4 projects

52. Port HapticMapper to the ultrasonic sensor ★
53. Build the sensor-fault pattern here first ★
54. Live threshold tuner
55. Two-sensor field-of-view experiment ★

---

# Foundations

Digital I/O, analog, and the timing model everything else sits on. Do these in order — later tiers assume them.

## 1. Blink without delay() ★

`●○○○`  ·  **45 min**  ·  Parts: Red LED, 220Ω resistor, Breadboard

**Teaches:** Non-blocking timing with millis(). The single most important idea in embedded programming.

**Build it:** Blink an LED at 1Hz without ever calling delay(). Store the last-toggle time in a variable, compare against millis() in loop(), toggle when enough has passed. Then blink two LEDs at different rates from the same loop.

**Done when:** Two LEDs blink at genuinely different rates simultaneously. With delay() this is impossible — prove that to yourself by trying.

> **Watch out:** delay() stops the whole processor. Every project past Tier 0 breaks if you use it. Your wristband's pulse timing already works this way — read HapticMapper.h and see.

## 2. Serial debugging lab ★

`●○○○`  ·  **30 min**  ·  Parts: UNO only, USB cable

**Teaches:** Serial.print as your primary debugging instrument — not a print statement, an oscilloscope for variables.

**Build it:** Print a counter, a float, and the value of millis() at once, formatted readably. Then print a variable that changes and watch it in the Serial Plotter (Tools → Serial Plotter) as a live graph.

**Done when:** You can see a variable's value change over time as a graph without any extra hardware.

> **Watch out:** Serial.begin(9600) must match the monitor's baud setting or you get garbage. Printing inside a tight loop floods the buffer and slows everything down.

## 3. Button with real debouncing

`●○○○`  ·  **1 hr**  ·  Parts: Button, 10kΩ resistor, LED, 220Ω resistor

**Teaches:** Mechanical switches bounce. Inputs need pull-ups. Neither is optional.

**Build it:** Wire a button with an external pull-up, then rewire using INPUT_PULLUP instead. Count presses and print the count. Watch it jump by 3-4 per press. Now debounce it in software with a millis() timestamp.

**Done when:** One physical press produces exactly one count increment, every time, 20 presses in a row.

> **Watch out:** A floating input pin reads random noise, not 0. This is the same class of bug as your GY-53 flicker — an unconnected pin is not a zero.

## 4. Toggle latch

`●○○○`  ·  **30 min**  ·  Parts: Button, LED, 220Ω resistor

**Teaches:** Edge detection vs level reading — the difference between 'button is down' and 'button was just pressed'.

**Build it:** Press once = LED on, press again = LED off. You must track the previous button state, not just the current one.

**Done when:** The LED toggles reliably and does not flicker while you hold the button down.

> **Watch out:** If the LED strobes while held, you're reading level instead of detecting an edge.

## 5. Traffic light state machine ★

`●●○○`  ·  **1.5 hr**  ·  Parts: Red LED, Yellow LED, Green LED, 3× 220Ω resistor

**Teaches:** Finite state machines — the structural pattern behind almost all embedded firmware.

**Build it:** Full sequence with realistic timings, written as an explicit state variable plus a switch statement, using millis() only. Then add a pedestrian button that requests a stop at the next safe opportunity.

**Done when:** The pedestrian button never breaks the sequence — it queues a request rather than jumping states immediately.

> **Watch out:** If your code is a chain of if/else with delays, rewrite it. The state-machine version is longer but it's the one that survives adding features.

## 6. PWM fade and the gamma problem

`●●○○`  ·  **1 hr**  ·  Parts: LED, 220Ω resistor, UNO

**Teaches:** PWM is rapid switching, not variable voltage. And human brightness perception is non-linear.

**Build it:** Fade an LED 0→255 linearly with analogWrite. Notice it looks like it brightens fast then stalls. Now apply a gamma curve (value = 255 * pow(x/255.0, 2.2)) and compare.

**Done when:** The gamma-corrected fade looks smooth and even to your eye; the linear one visibly doesn't.

> **Watch out:** Only pins 3, 5, 6, 9, 10, 11 do PWM on an UNO. analogWrite on any other pin silently does nothing useful.

## 7. Potentiometer → brightness, with map()

`●○○○`  ·  **45 min**  ·  Parts: 10kΩ potentiometer, LED, 220Ω resistor

**Teaches:** analogRead gives 0-1023, analogWrite takes 0-255. Range mapping and integer division traps.

**Build it:** Read the pot, map to PWM, drive the LED. Print both raw and mapped values. Try the mapping by hand with division before using map().

**Done when:** Full pot rotation gives full brightness range with no dead zone at either end.

> **Watch out:** raw/4 and map(raw,0,1023,0,255) differ slightly at the top end. Integer division truncates. Print both and see.

## 8. Photoresistor night light with hysteresis ★

`●●○○`  ·  **1 hr**  ·  Parts: Photoresistor, 10kΩ resistor, LED, 220Ω resistor

**Teaches:** Voltage dividers, and why a bare threshold makes outputs chatter.

**Build it:** Divider with the LDR, read the analog value, switch an LED on below a threshold. Then shade it slowly until it sits right at the threshold — watch it flicker. Fix it with two thresholds (on below 400, off above 450).

**Done when:** Held at the boundary, the LED holds its state instead of chattering.

> **Watch out:** Hysteresis is the fix for every noisy threshold you will ever write — including your wristband's zone boundaries. Worth understanding deeply here.

---

# Sensing

Turning the physical world into numbers, and learning that raw sensor data is always messier than the datasheet implies.

## 9. Ultrasonic tape measure ★

`●●○○`  ·  **1 hr**  ·  Parts: HC-SR04 ultrasonic, Breadboard

**Teaches:** Time-of-flight ranging — the same physics as your VL53L0X, but with sound and visible timing.

**Build it:** 10µs trigger pulse, pulseIn() on echo, convert to centimetres. Derive the /58 constant yourself from the speed of sound (343 m/s) and the there-and-back path — don't just copy it.

**Done when:** Measurements match a ruler within about 1cm from 5cm to 2m.

> **Watch out:** Soft surfaces (cloth, foam) absorb the ping and return nothing. Angled surfaces reflect it away. Your ToF sensor has the same class of blind spot for different reasons.

## 10. Parking sensor — your wristband in kit form ★

`●●○○`  ·  **1.5 hr**  ·  Parts: HC-SR04 ultrasonic, Passive buzzer, LEDs

**Teaches:** Distance → zones → output pattern. This is exactly your HapticMapper architecture.

**Build it:** Map distance to four zones with different beep rates — slow, medium, fast, continuous. Keep the zone logic in a separate function with no hardware calls in it, so it's testable on its own.

**Done when:** Walking towards it produces a smooth escalation you can navigate by with your eyes closed.

> **Watch out:** You have just rebuilt your own project with a different sensor. That is the point — the logic is portable, the hardware isn't. Compare your function against HapticMapper.h.

## 11. Thermistor thermometer

`●●●○`  ·  **2 hr**  ·  Parts: Thermistor, 10kΩ resistor

**Teaches:** Real sensor maths — the Steinhart-Hart / B-parameter equation. Not every sensor is linear.

**Build it:** Voltage divider, read raw ADC, convert to resistance, then resistance to Kelvin using the B equation, then to Celsius. Print all four values so you can see each stage.

**Done when:** Reads room temperature within ~2°C, and pinching the thermistor moves it visibly.

> **Watch out:** Printing the intermediate values is the whole lesson. When the final number is wrong you need to know which conversion stage broke.

## 12. DHT11 environment reader

`●●○○`  ·  **1 hr**  ·  Parts: DHT11 module

**Teaches:** Library use, and sensors with hard timing constraints you must respect.

**Build it:** Read temperature and humidity, print both. Then deliberately poll it every 100ms and watch readings fail or repeat.

**Done when:** Stable readings at 1 Hz; you can explain why faster polling breaks it.

> **Watch out:** DHT11 needs ~1 second between reads and returns NaN if rushed. Always check whether a read succeeded before using the value — silent bad data is worse than an error.

## 13. PIR intruder alarm

`●●○○`  ·  **1 hr**  ·  Parts: HC-SR501 PIR, Active buzzer, LED

**Teaches:** Sensors with physical configuration — hardware settings that override your code.

**Build it:** Trigger a buzzer on motion. Then experiment with both onboard potentiometers (sensitivity, hold time) and the retrigger jumper, and write down what each actually does.

**Done when:** You have notes describing the effect of all three hardware settings, measured not guessed.

> **Watch out:** The HC-SR501 needs 30-60 seconds of warm-up after power-on or it fires constantly. If it 'doesn't work', wait a minute before debugging anything.

## 14. Clap-clap detector

`●●●○`  ·  **2 hr**  ·  Parts: Sound sensor module, LED, Relay (optional)

**Teaches:** Detecting a pattern in time, not just a threshold. Introduces timing windows.

**Build it:** Detect two claps within 600ms of each other and toggle an LED. One clap does nothing. Three claps should not trigger twice.

**Done when:** Reliable on double-claps, ignores single claps, ignores speech and door slams reasonably well.

> **Watch out:** The sound sensor reports loudness, not sound identity. All the intelligence has to come from your timing logic.

## 15. Water level alarm

`●○○○`  ·  **45 min**  ·  Parts: Water level sensor, Buzzer, LED

**Teaches:** Analog thresholds on a resistive sensor, and sensor degradation as a design constraint.

**Build it:** Alarm above a level you calibrate yourself. Then improve it: power the sensor from a digital pin and only turn it on for the moment of reading.

**Done when:** Works, and the sensor is powered for well under 1% of runtime.

> **Watch out:** Continuous DC across the traces electrolyses and corrodes them within days. Duty-cycling the power is a real engineering fix, not a micro-optimisation.

## 16. Tilt switch orientation sensor

`●○○○`  ·  **30 min**  ·  Parts: Tilt ball switch, 10kΩ resistor, LED

**Teaches:** Mechanical sensors are switches, with all the bouncing that implies.

**Build it:** Light an LED when tilted past the trigger angle. Print raw state and watch it bounce violently while moving.

**Done when:** Stable output during motion, achieved by debouncing rather than by holding the board still.

> **Watch out:** A rolling ball bounces far worse than a button. Longer debounce window needed — measure how much.

## 17. Joystick reader with deadzone

`●●○○`  ·  **1 hr**  ·  Parts: Joystick module

**Teaches:** Multi-channel analog input, centre calibration, and deadzones.

**Build it:** Read X, Y and the button. Print all three. Note the centre is never exactly 512 — calibrate it at startup and apply a deadzone so a released stick reads exactly zero.

**Done when:** Released joystick reports 0,0 consistently; small nudges are ignored, real movement isn't.

> **Watch out:** Every analog stick has drift. Software calibration at boot is how real controllers handle it.

## 18. Rotary encoder counter ★

`●●●○`  ·  **2.5 hr**  ·  Parts: Rotary encoder module

**Teaches:** Quadrature decoding and hardware interrupts. A genuine step up in difficulty.

**Build it:** Count up on clockwise, down on anticlockwise. First with polling in loop() — spin it fast and watch counts get lost. Then rewrite with attachInterrupt.

**Done when:** Fast spinning loses no counts, and direction is always correct.

> **Watch out:** Variables shared with an ISR must be declared volatile, or the compiler optimises away your reads. This bug is invisible and maddening.

## 19. GY-521 tilt angle meter

`●●●○`  ·  **2.5 hr**  ·  Parts: GY-521 (MPU6050)

**Teaches:** I2C sensor reading and turning raw accelerometer axes into a real angle with atan2.

**Build it:** Read all three accelerometer axes, convert to pitch and roll in degrees using atan2. Print continuously and check against a phone level app.

**Done when:** Angles match a phone's level within a few degrees through the full range.

> **Watch out:** Raw values are signed 16-bit split across two registers — you must combine high and low bytes. Get the sign handling wrong and it works for half the range only.

## 20. Motion-triggered alarm with filtering

`●●●●`  ·  **3 hr**  ·  Parts: GY-521 (MPU6050), Buzzer

**Teaches:** Signal filtering — a low-pass / complementary filter to separate real motion from noise.

**Build it:** Alarm when the board is genuinely moved, not when a truck passes. Implement a simple running average, then a complementary filter blending accelerometer and gyro.

**Done when:** Ignores tapping the table; reliably catches the board being picked up.

> **Watch out:** This is the hardest signal-processing problem in the kit and it's worth the time. Every real sensor product does some version of it.

---

# Display & output

Getting information back out. Where you learn multiplexing and that pins are a scarce resource.

## 21. 7-segment digit driver

`●●○○`  ·  **1.5 hr**  ·  Parts: 1-digit 7-segment display, 7× 220Ω resistor

**Teaches:** Lookup tables and bit patterns instead of long if/else chains.

**Build it:** Count 0-9. Encode each digit as a byte in a const array rather than writing ten separate blocks of digitalWrite.

**Done when:** All ten digits render correctly, and adding hex digits A-F takes six new array entries and no new logic.

> **Watch out:** Check whether yours is common cathode or common anode — the logic inverts. Test with a single resistor and 5V before writing any code.

## 22. 4-digit multiplexing ★

`●●●○`  ·  **2.5 hr**  ·  Parts: 4-digit 7-segment display, Resistors

**Teaches:** Persistence of vision — showing four digits with hardware that can only show one at a time.

**Build it:** Display a 4-digit number. Only one digit is lit at any instant; you cycle fast enough that the eye integrates it. Then deliberately slow the refresh to 5Hz and watch the illusion collapse.

**Done when:** Steady, flicker-free 4-digit display, and you can explain exactly why it works.

> **Watch out:** Any delay() elsewhere in your loop makes the display flicker visibly. This is where Project 1 stops being theoretical.

## 23. 74HC595 shift register ★

`●●●○`  ·  **2 hr**  ·  Parts: 74HC595 IC, 8 LEDs, 8× 220Ω resistor

**Teaches:** Trading time for pins — 3 pins driving 8 outputs. Bit manipulation in practice.

**Build it:** Drive 8 LEDs from 3 Arduino pins. Implement shiftOut yourself with digitalWrite before using the built-in, so you understand the clock/latch dance.

**Done when:** A binary counter runs across 8 LEDs, and you can explain what latch does and why it exists.

> **Watch out:** Without the latch pin you'd see the bits ripple through as they shift. Latch makes the update atomic — the same reason double-buffering exists in graphics.

## 24. LCD1602 first screen

`●●○○`  ·  **1.5 hr**  ·  Parts: LCD1602, 10kΩ potentiometer, Jumper wires

**Teaches:** Parallel display interfacing and 4-bit mode. Your LCD has no I2C backpack, so this is the wiring-heavy version.

**Build it:** Wire in 4-bit mode (RS, E, D4-D7) plus the contrast pot on V0. Print text on both lines and a live-updating counter.

**Done when:** Clear text on both rows with contrast properly adjusted.

> **Watch out:** A blank screen with faint boxes means contrast, not code — turn the pot fully through its range before suspecting anything else. This wastes hours if you don't know it.

## 25. LCD custom characters

`●●●○`  ·  **1.5 hr**  ·  Parts: LCD1602, 10kΩ potentiometer

**Teaches:** The display's character RAM — defining your own 5×8 glyphs as bitmaps.

**Build it:** Define custom glyphs (a battery icon, a degree symbol, a signal-strength bar) as byte arrays and display them. Build an animated 8-frame loading spinner.

**Done when:** A smooth animated icon on screen built entirely from characters you designed.

> **Watch out:** Only 8 custom characters can exist at once. Designing within that limit is the interesting part.

## 26. LCD menu system ★

`●●●○`  ·  **3 hr**  ·  Parts: LCD1602, 3 buttons, 10kΩ potentiometer

**Teaches:** UI state management on tiny hardware — the skill behind every device with buttons and a screen.

**Build it:** A multi-level menu: scroll items, enter a submenu, adjust a value, go back. Represent the menu as a data structure, not a nest of if statements.

**Done when:** Adding a new menu item means adding one array entry — no new control-flow code.

> **Watch out:** If adding an item requires touching the navigation logic, your data structure isn't right yet. That refactor is the lesson.

## 27. MAX7219 matrix and frame buffers

`●●●○`  ·  **2.5 hr**  ·  Parts: MAX7219 8×8 module

**Teaches:** SPI output and thinking in frame buffers rather than individual pixels.

**Build it:** Light single pixels, then draw shapes, then scroll a text message. Keep an 8-byte array as your frame buffer and push the whole thing each refresh.

**Done when:** Smoothly scrolling text, with the display logic cleanly separated from the message content.

> **Watch out:** Draw into the buffer, then send the buffer. Writing directly to the display as you compute causes tearing and makes animation hard.

## 28. Conway's Game of Life ★

`●●●●`  ·  **3 hr**  ·  Parts: MAX7219 8×8 module, Button

**Teaches:** Real algorithm work — 2D arrays, neighbour counting, and why you need two buffers.

**Build it:** Life on the 8×8 grid. Seed with a glider. Add a button to reseed randomly. Handle edges by wrapping.

**Done when:** A glider travels across the grid and wraps around correctly.

> **Watch out:** You must compute the next generation into a second array. Updating in place corrupts the neighbour counts mid-pass — a classic bug worth experiencing once.

## 29. RGB colour mixing

`●●○○`  ·  **1.5 hr**  ·  Parts: RGB LED, 3× 220Ω resistor, 2 potentiometers

**Teaches:** Three-channel PWM and colour space conversion.

**Build it:** Mix colours with pots. Then implement an HSV→RGB conversion and sweep hue smoothly through a rainbow with one variable.

**Done when:** A smooth rainbow fade driven by a single incrementing hue value.

> **Watch out:** Note whether yours is common anode or cathode — anode means 255 is off. Apply the gamma curve from Project 6 or the colours look wrong.

## 30. Active vs passive buzzer

`●○○○`  ·  **45 min**  ·  Parts: Active buzzer, Passive buzzer

**Teaches:** The difference between a component with its own oscillator and one that needs a driving signal.

**Build it:** Drive both with plain digitalWrite HIGH. One sounds, one clicks. Then drive both with tone(). Write down what happens in all four cases.

**Done when:** You can explain in one sentence why the passive buzzer can play melodies and the active one cannot.

> **Watch out:** This distinction catches almost everyone once. Ten minutes here saves an afternoon later.

## 31. Melody player with a note table

`●●○○`  ·  **2 hr**  ·  Parts: Passive buzzer

**Teaches:** Frequency, musical pitch, and non-blocking sequencing.

**Build it:** Play a recognisable tune from an array of note/duration pairs. Then rewrite so it plays without delay(), using millis() to advance notes — so an LED can blink independently while music plays.

**Done when:** Music plays and an LED blinks at an unrelated rate, simultaneously, from one loop().

> **Watch out:** The naive version with delay() is much easier. Do the hard version — this is Project 1 applied to something with real structure.

---

# Actuators & power

Making things move. Where electrical mistakes start costing money — this is the tier your wristband already lives in.

## 32. Transistor as a switch ★

`●●○○`  ·  **1.5 hr**  ·  Parts: PN2222 or S8050, 3-6V motor + fan blade, 1N4148 diode, 220Ω resistor

**Teaches:** Why a GPIO pin can't drive a motor, and how a transistor and flyback diode fix it. This is your wristband's motor circuit.

**Build it:** Drive the fan motor from a digital pin via the transistor, with the flyback diode across the motor. Then PWM the base for speed control.

**Done when:** Smooth speed control, and no resets or glitches when the motor stops.

> **Watch out:** Omit the flyback diode and the collapsing field spikes hundreds of volts, resetting or killing the board. You already built this circuit for your wristband — build it again here where breaking it is cheap.

## 33. Servo control and the 50Hz signal ★

`●●○○`  ·  **1.5 hr**  ·  Parts: SG90 servo

**Teaches:** Servos take a position command encoded as pulse width, not a voltage or a speed.

**Build it:** Sweep 0-180°. Then control the angle from a potentiometer. Then use writeMicroseconds directly and find your servo's real endpoints — they won't be exactly 1000 and 2000µs.

**Done when:** Full range without buzzing or straining at the limits.

> **Watch out:** Driving a servo from the UNO's 5V pin causes brownout resets under load. Use the power supply module with external power and a common ground.

## 34. L293D bidirectional motor control

`●●●○`  ·  **2 hr**  ·  Parts: L293D IC, 3-6V motor, External power

**Teaches:** H-bridges — how reversing a motor actually works at circuit level.

**Build it:** Forward, reverse, stop, and PWM speed in both directions. Draw the four switch states of the bridge on paper first and work out which combinations are valid.

**Done when:** Both directions at variable speed, controlled by a joystick.

> **Watch out:** There is one input combination that shorts the supply through the bridge. Find it on paper before you find it with smoke.

## 35. Stepper motor precision positioning ★

`●●●○`  ·  **2.5 hr**  ·  Parts: 28BYJ-48 stepper, ULN2003 driver board, External power

**Teaches:** Open-loop precise positioning, and step sequences.

**Build it:** Rotate exactly one revolution, then exactly 90°, then back. Work out the real steps-per-revolution for your gearing rather than trusting a forum post — mark the shaft and count.

**Done when:** Ten full revolutions land the mark back at the exact starting position.

> **Watch out:** Steppers have no position feedback. Miss steps under load and the software's idea of position silently diverges from reality — with no error raised.

## 36. Relay switching (low voltage only) ★

`●●○○`  ·  **1 hr**  ·  Parts: 5V relay module, 9V battery, Motor or lamp

**Teaches:** Isolating a control circuit from a switched load.

**Build it:** Switch a separate 9V battery circuit with the relay. Listen to the click, trace which contacts are normally-open and normally-closed with a multimeter.

**Done when:** You can predict the state of both contact pairs before energising it.

> **Watch out:** Do not switch mains AC with this. Not at your age, not on a breadboard, not supervised. 220V kills, and breadboard contacts are nowhere near rated for it. Low-voltage DC only.

## 37. Power budget measurement

`●●●○`  ·  **2 hr**  ·  Parts: Multimeter, Power supply module, 9V battery, Various loads

**Teaches:** Measuring real current draw and understanding regulator limits — directly relevant to your battery work.

**Build it:** Measure current draw of the bare UNO, then with the LCD, then with a servo moving. Calculate runtime from a 9V battery's capacity for each. Compare against your wristband's 250mAh cell.

**Done when:** A written table of measured current for five configurations, with estimated runtimes.

> **Watch out:** A 9V battery holds roughly 500mAh but delivers it poorly under load. It's fine for logic and bad for motors — this is why your wristband uses a LiPo.

---

# Protocols

I2C, SPI and IR. How chips actually talk, and how to debug them when they don't.

## 38. I2C bus scanner ★

`●●○○`  ·  **1 hr**  ·  Parts: Any I2C device (GY-521, DS1307)

**Teaches:** The diagnostic tool that would have found your GY-53 problem in 30 seconds.

**Build it:** Write a sketch that probes every address 1-127 and reports which ones acknowledge. Test with nothing connected, then one device, then two on the same bus.

**Done when:** Correctly reports the addresses of two simultaneously connected devices.

> **Watch out:** Keep this sketch forever. It's the first thing to run whenever an I2C device 'doesn't work' — it separates wiring faults from library problems instantly.

## 39. DS1307 real-time clock

`●●○○`  ·  **1.5 hr**  ·  Parts: DS1307 RTC module, Coin cell, LCD1602

**Teaches:** Timekeeping that survives power loss, and BCD encoding.

**Build it:** Set the time, display it on the LCD, then unplug the Arduino for a minute and confirm it kept time. Read the raw registers directly to see BCD encoding before using a library.

**Done when:** Time survives a full power cycle and is still correct.

> **Watch out:** Without a good coin cell it forgets on every power loss. Check the battery first if the time resets — and note the DS1307 drifts noticeably over weeks.

## 40. IR remote decoder

`●●○○`  ·  **1.5 hr**  ·  Parts: IR receiver module, Remote control

**Teaches:** Decoding a real communication protocol — NEC encoding over infrared.

**Build it:** Print the hex code of every button. Build a reference table of all of them. Then point other remotes at it (TV, air conditioner) and see what those send.

**Done when:** A complete documented code table for every button on the kit remote.

> **Watch out:** Holding a button sends a repeat code (often 0xFFFFFFFF), not the original code again. Handle that or held buttons behave strangely.

## 41. IR universal controller

`●●●○`  ·  **2.5 hr**  ·  Parts: IR receiver, Remote, LEDs, Servo, Buzzer

**Teaches:** Mapping an input protocol to actions cleanly — a dispatch table, not a giant switch.

**Build it:** Control several outputs from the remote: LEDs on/off, servo position from number keys, volume-style increment on arrows. Use a lookup structure mapping code to action.

**Done when:** Adding a new button-to-action mapping is one line of data.

> **Watch out:** IR is line-of-sight and easily swamped by sunlight or fluorescent lighting. Test in different lighting before assuming your code is wrong.

## 42. RFID card reader ★

`●●●○`  ·  **2 hr**  ·  Parts: RC522 RFID module, Cards/fobs

**Teaches:** SPI communication and reading a card's unique identifier.

**Build it:** Read and print the UID of any card presented. Build a whitelist of allowed UIDs and light a green or red LED accordingly.

**Done when:** Reliably distinguishes an allowed card from a denied one at 2-3cm range.

> **Watch out:** The RC522 is a 3.3V device. Connect VCC to 3.3V, not 5V — 5V will damage it. This is the single most common way people destroy this module.

## 43. Keypad matrix scanning

`●●●○`  ·  **2 hr**  ·  Parts: 4×4 membrane keypad

**Teaches:** How 16 buttons work over 8 wires — row/column scanning.

**Build it:** Print the pressed key. Implement the scan yourself (drive one row low, read all columns, repeat) before reaching for the Keypad library.

**Done when:** All 16 keys detected correctly, with no ghosting on single presses.

> **Watch out:** Press two keys at once and you may get a phantom third. Understanding why is understanding matrix scanning — real keyboards solve it with diodes.

---

# Integration builds

Multi-module projects. The jump from following a wiring diagram to designing a system.

## 44. Weather station with logging

`●●●○`  ·  **4 hr**  ·  Parts: DHT11, DS1307, LCD1602, Thermistor

**Teaches:** Combining sensors, display and time into a coherent product.

**Build it:** Show current temperature, humidity and time on the LCD. Track and display 24-hour min/max. Cross-check the DHT11 against your thermistor and note the disagreement.

**Done when:** Runs unattended for a full day and reports meaningful min/max values.

> **Watch out:** Two thermometers rarely agree. Deciding which to trust, and why, is real engineering — not a bug to fix.

## 45. Reaction timer game

`●●○○`  ·  **2.5 hr**  ·  Parts: LED, Button, 4-digit display, Buzzer

**Teaches:** Precise timing measurement and anti-cheat logic.

**Build it:** Random delay, LED lights, measure reaction time in milliseconds, display it. Detect pressing early and show a penalty. Track a best score.

**Done when:** Accurate to the millisecond, and pressing before the light shows a fault rather than a great score.

> **Watch out:** Use micros() if you want sub-millisecond honesty. Human reaction is 200-300ms — if you're reading 50ms, your timing has a bug.

## 46. Simon says memory game ★

`●●●○`  ·  **4 hr**  ·  Parts: 4 LEDs, 4 buttons, Passive buzzer

**Teaches:** Sequence storage, growing arrays, and full game state management.

**Build it:** Classic Simon: growing colour/tone sequence, player repeats it, speed increases with level. Each colour gets its own tone. Game over plays a losing sound and shows the level reached.

**Done when:** Playable to level 10+ without bugs, and genuinely fun.

> **Watch out:** randomSeed(analogRead(A0)) on an unconnected pin — otherwise the 'random' sequence is identical every power-up.

## 47. RFID door lock

`●●●○`  ·  **3.5 hr**  ·  Parts: RC522 RFID, SG90 servo, LCD1602, Buzzer, LEDs

**Teaches:** A complete access-control system — authenticate, actuate, log, handle failure.

**Build it:** Valid card unlocks (servo rotates) for 5 seconds then relocks. Invalid card buzzes and shows a message. Three failures in a row triggers a 30-second lockout.

**Done when:** Lockout works, and the servo returns to locked even if a card is presented during the unlock window.

> **Watch out:** Think about the failure modes: what happens on power loss mid-unlock? Real security devices must fail to a defined state — decide which, deliberately.

## 48. Alarm clock

`●●●○`  ·  **4 hr**  ·  Parts: DS1307, LCD1602, Keypad, Active buzzer

**Teaches:** Combining timekeeping, input, display and a menu into something you'd actually use.

**Build it:** Display time, set an alarm via the keypad, sound at the right moment, snooze button adds 5 minutes. Alarm state survives being set hours in advance.

**Done when:** You set it at night and it wakes you up correctly.

> **Watch out:** Handle midnight rollover and an alarm set for a time already passed today. Off-by-one errors in time logic are extremely common — test the edges deliberately.

## 49. Digital safe

`●●●○`  ·  **3.5 hr**  ·  Parts: Keypad, LCD1602, Servo, Buzzer, LEDs

**Teaches:** Input validation, state security, and deliberate failure handling.

**Build it:** PIN entry with masked display, servo latch, configurable PIN stored in EEPROM so it survives power loss, escalating lockout on repeated failures.

**Done when:** PIN survives a power cycle, and brute-forcing is meaningfully slowed by the lockout.

> **Watch out:** Storing the PIN in EEPROM as plain text is what real cheap safes do — worth noting why that's weak, even if you don't fix it here.

## 50. Radar scanner with live display ★

`●●●●`  ·  **5 hr**  ·  Parts: SG90 servo, HC-SR04 ultrasonic, USB cable

**Teaches:** Coordinating an actuator with a sensor and streaming structured data to a computer. This is Rung 4 of your roadmap.

**Build it:** Servo sweeps 0-180° while the ultrasonic measures at each step. Stream angle,distance pairs over serial as CSV. Then write a browser page using the Web Serial API that draws a live polar radar plot.

**Done when:** You wave your hand in front of it and a blip appears on screen at the right angle and range.

> **Watch out:** This is your Phase 1 graduation project. It touches actuators, sensing, serial protocol design, and front-end JavaScript. Write the browser half yourself.

## 51. Temperature-controlled fan ★

`●●●○`  ·  **2.5 hr**  ·  Parts: Thermistor, PN2222, Fan + motor, Diode, LCD1602

**Teaches:** A closed control loop with hysteresis — your first real feedback system.

**Build it:** Fan speed rises with temperature via PWM. Add hysteresis so it doesn't oscillate at the switching point. Display current temperature and fan duty on the LCD.

**Done when:** Held at the threshold temperature, fan speed is stable rather than hunting up and down.

> **Watch out:** This is Project 8's hysteresis lesson applied to a system with real physical inertia. The fan cools the thermistor, which slows the fan — that feedback loop is the interesting part.

---

# Wristband work

Projects that feed directly into the real device. Your kit is a safe test rig for firmware you don't want to debug on the finished build.

## 52. Port HapticMapper to the ultrasonic sensor ★

`●●○○`  ·  **2 hr**  ·  Parts: HC-SR04, Vibration motor or buzzer, PN2222, Diode

**Teaches:** That well-separated logic is portable across hardware — proving your own architecture decision was right.

**Build it:** Take HapticMapper.h from your repo unchanged. Feed it distances from the HC-SR04 instead of the VL53L0X. Drive a motor through the transistor circuit.

**Done when:** Your real wristband firmware logic runs on completely different sensor hardware with zero changes to HapticMapper.h.

> **Watch out:** If you had to modify HapticMapper.h to make this work, that tells you the separation wasn't as clean as intended — and exactly where to fix it.

## 53. Build the sensor-fault pattern here first ★

`●●●○`  ·  **3 hr**  ·  Parts: HC-SR04, Buzzer or motor

**Teaches:** Implementing a safety feature on disposable hardware before touching the real device.

**Build it:** This is Rung 2 of your roadmap. Add a distinct fault pattern — three rapid pulses, pause, repeat — for when the sensor fails or times out. Write the unit test first, watch it fail, then implement. Test by physically unplugging the sensor.

**Done when:** Unplugging the sensor produces a pattern clearly distinguishable from every proximity zone, and the tests pass.

> **Watch out:** Do this on the kit, then port it to the wristband. Debugging a safety feature on the device you've soldered is the wrong place to discover a logic error.

## 54. Live threshold tuner

`●●○○`  ·  **2 hr**  ·  Parts: HC-SR04, 2 potentiometers, LCD1602, Motor/buzzer

**Teaches:** Building tools for yourself — the tuning rig your simulator does in software, in hardware.

**Build it:** Two pots adjust the near and far zone thresholds live while the device runs. LCD shows current distance, active zone, and both threshold values.

**Done when:** You can find good threshold values by walking around with it, without recompiling once.

> **Watch out:** Compare the values you arrive at physically against the ones in HapticMapper.h. Reality frequently disagrees with values chosen at a desk — that's the point of building this.

## 55. Two-sensor field-of-view experiment ★

`●●●●`  ·  **4 hr**  ·  Parts: HC-SR04, SG90 servo, Notebook

**Teaches:** Investigating a documented limitation of your own project with real measurements.

**Build it:** Your README names narrow field of view as a real failure mode. Measure it: mount the sensor on the servo, sweep it, and map the actual detection cone at 0.5m, 1m and 1.5m. Chart where a chair leg or a low table goes undetected.

**Done when:** A measured diagram of the real blind spots, with distances, that you could show a judge.

> **Watch out:** This turns a stated limitation into measured evidence. For Jugend forscht that difference is enormous — anyone can list weaknesses, few quantify their own.

---

## When you finish

If you work through the starred projects you will have covered, with your
own hands: non-blocking timing, state machines, debouncing, hysteresis,
PWM, voltage dividers, sensor maths, interrupts, multiplexing, shift
registers, frame buffers, I2C, SPI, IR decoding, H-bridges, stepper
control, closed-loop feedback, and serial protocol design.

That is a genuine embedded-systems foundation, and it is more than most
first-year university electronics courses cover practically.

Then go finish the wristband.
