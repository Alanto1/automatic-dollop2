# Module Reference — every part in the Elegoo kit

What each component *is*, how it actually works, what every pin does, and
the specific way it bites you. Companion to [`LAB_MANUAL.md`](LAB_MANUAL.md)
and [`ROADMAP.md`](ROADMAP.md).

**42 module types, 219 individual pieces.**

---

## The four that can destroy hardware (or you)

Read these before wiring anything.

| Part | The mistake | What happens |
|---|---|---|
| **5V Relay** | Switching mains AC | Electrocution and fire. Breadboard contacts are nowhere near rated for 220V. Switch a 9V circuit instead. |
| **RC522 RFID** | VCC to 5V | Destroys the module silently. It is a 3.3V part. |
| **Diode Rectifier** | Fitted backwards | Dead short across the supply, instantly. Banded end goes to positive. |
| **Electrolytic caps** | Fitted backwards | Heats up and bursts. The stripe marks negative. |

---

# The board and the bench

The controller, the things you plug it into, and how power gets around.

## UNO R3 Controller Board

An ATmega328P microcontroller on a board with USB, a voltage regulator, and pin headers.

**How it works:** A single-core 8-bit CPU at 16MHz with 32KB of flash for your program, 2KB of SRAM for variables, and 1KB of EEPROM that survives power loss. It runs your loop() forever, doing exactly one thing at a time. There is no operating system and no multitasking — that's why non-blocking timing matters so much.

| Pin | What it does |
|---|---|
| `D0-D13` | Digital in/out. D0 and D1 are also the USB serial line — avoid using them. |
| `D3, D5, D6, D9, D10, D11` | The only PWM-capable pins. analogWrite() on any other pin does nothing useful. |
| `A0-A5` | Analog inputs, 10-bit: readings come back 0-1023. Also usable as plain digital pins. |
| `A4 / A5` | Double as the I2C bus (SDA / SCL). Every I2C device shares these two. |
| `D10-D13` | Double as the SPI bus (SS, MOSI, MISO, SCK). |
| `5V / 3.3V / GND` | Power out. The 3.3V rail is weak — about 50mA. |
| `VIN` | Raw input if you feed it 7-12V; the onboard regulator makes 5V from it. |

**You talk to it with:** USB serial at 9600 baud by default  ·  **Voltage:** 5V logic

> **Watch out:** Each pin sources at most 40mA, and the whole chip about 200mA total. A motor wants ten times that. This single fact is why transistors, drivers and external power exist in this kit.

*Used in lab manual projects: #1, #2, #3*

## 830 Tie-Point Breadboard

A solderless grid for building circuits by pushing wires into holes.

**How it works:** Two long rails down each edge are connected end-to-end for power and ground. The main field is in strips of five holes: each group of five is connected to each other, but not across the central gully. That gully is exactly the width of a DIP chip so its two rows of legs land on separate strips.

| Pin | What it does |
|---|---|
| `Red/blue rails` | Continuous along the length. Some boards break in the middle — check with a multimeter before trusting them. |
| `Main field` | Columns of 5 holes, connected vertically within each half. |
| `Centre gully` | Separates left and right halves. DIP chips straddle it. |

**You talk to it with:** n/a  ·  **Voltage:** n/a

> **Watch out:** A tired breadboard develops loose contacts that create intermittent faults which look exactly like software bugs. If a working circuit goes flaky, move it to a fresh area of the board before debugging code.

*Used in lab manual projects: #1*

## Power Supply Module

A small board that clips onto the breadboard rails and feeds them regulated 3.3V or 5V.

**How it works:** Takes 6.5-12V into its barrel jack and runs it through onboard linear regulators. Jumpers select 3.3V or 5V independently for each side's rail. This is how you power motors and servos without dragging down the UNO's own regulator.

| Pin | What it does |
|---|---|
| `Barrel jack` | 6.5-12V DC input. Your 9V adapter fits it. |
| `Jumpers` | One per rail: 3.3V, 5V, or OFF. |
| `Rail pins` | Push straight into the breadboard power rails. |

**You talk to it with:** n/a  ·  **Voltage:** 3.3V or 5V out

> **Watch out:** You must connect this module's ground to the Arduino's ground. Two power sources with no common ground means the signals have no shared reference, and nothing works — this catches almost everyone the first time.

*Used in lab manual projects: #33, #34, #35, #37*

## Prototype Expansion Module

A shield that stacks on the UNO with a small breadboard on top.

**How it works:** Passes every UNO pin up to its own headers and gives you a mini solderless area right above the board. No active circuitry — pure convenience for keeping a build compact.

| Pin | What it does |
|---|---|
| `All UNO pins` | Duplicated on the shield headers. |
| `Mini breadboard` | Adhesive-backed, sits on top. |

**You talk to it with:** n/a  ·  **Voltage:** 5V

> **Watch out:** Its breadboard area is small. Good for tidying a finished build, cramped for developing one — use the 830-point board while you're still experimenting.

## 9V Battery + Adapter — ×2

Two ways to run the board without a computer attached.

**How it works:** Both feed the UNO's onboard regulator, which drops the input to 5V and dissipates the difference as heat. The 9V battery holds roughly 500mAh but has high internal resistance, so its voltage sags under load.

| Pin | What it does |
|---|---|
| `Snap connector` | Goes to the barrel jack via the included clip. |
| `9V 1A adapter` | Mains-powered, far better for anything sustained. |

**You talk to it with:** n/a  ·  **Voltage:** 9V in, 5V regulated

> **Watch out:** Fine for logic and LEDs, poor for motors. Add a servo and the sag causes brownout resets that look like random crashes. Your wristband uses a LiPo for exactly this reason.

*Used in lab manual projects: #36, #37*

---

# Things that light up

From a single LED to a 16-character display. Ordered by how many pins they cost you.

## LED (Red, Yellow, Blue, Green, White) — ×25

A diode that emits light in one direction only.

**How it works:** Current flows one way and produces photons. The forward voltage differs by colour because it's set by the semiconductor's band gap: red and yellow around 2.0V, green about 2.2V, blue and white around 3.0-3.2V. Everything above that voltage has to be dropped by a resistor or the LED destroys itself.

| Pin | What it does |
|---|---|
| `Long leg` | Anode, positive, goes toward 5V. |
| `Short leg / flat spot on the rim` | Cathode, negative, goes toward ground. |

**You talk to it with:** digitalWrite() or analogWrite() for brightness  ·  **Voltage:** ~2.0-3.2V forward

> **Watch out:** Never connect one directly across 5V. Work out the resistor: R = (5V − Vf) ÷ 0.02A. For a red LED that's (5 − 2) ÷ 0.02 = 150Ω, so the common 220Ω is a safe choice. Blue and white need less resistance for the same brightness because they drop more voltage themselves.

*Used in lab manual projects: #1, #5, #6, #7*

## RGB LED — ×2

Three LEDs — red, green, blue — in one package sharing a common leg.

**How it works:** Drive each colour with its own PWM channel and the eye blends them. Full brightness on all three gives white; varying the ratios gives any hue.

| Pin | What it does |
|---|---|
| `Longest leg` | The common pin — either anode (to 5V) or cathode (to GND) depending on the type. |
| `Other three` | Red, green, blue, each through its own resistor. |

**You talk to it with:** Three analogWrite() calls on PWM pins  ·  **Voltage:** 5V through resistors

> **Watch out:** If yours is common anode, the logic inverts: 255 means off and 0 means fully on. Test with a single resistor before writing code. Each colour also needs its own resistor — one shared resistor makes brightness change as you mix colours.

*Used in lab manual projects: #29*

## 1-Digit 7-Segment Display

Eight LEDs arranged as a figure-eight plus a decimal point.

**How it works:** Segments are labelled a-g clockwise from the top, plus dp. Every digit is just a pattern of which segments are lit. All eight share one common pin, so the whole display is either common-cathode or common-anode.

| Pin | What it does |
|---|---|
| `a-g, dp` | One pin per segment, each needs its own resistor. |
| `Common (2 pins)` | Both middle pins are the same net — to GND for common cathode, to 5V for common anode. |

**You talk to it with:** 8 digital pins, or drive it from a 74HC595  ·  **Voltage:** 5V through resistors

> **Watch out:** Encode the digits as a lookup table of bytes rather than writing ten blocks of digitalWrite. Adding hex digits A-F then costs six array entries instead of six new code blocks.

*Used in lab manual projects: #21, #23*

## 4-Digit 7-Segment Display

Four of the above sharing one set of segment pins.

**How it works:** All four digits' segment pins are wired together; each digit has its own common pin. You can only light one digit at a time — so you light digit 1, then 2, then 3, then 4, cycling hundreds of times per second. Your eye integrates it into a steady four-digit number. That trick is called multiplexing.

| Pin | What it does |
|---|---|
| `8 segment pins` | a-g plus dp, shared across all four digits. |
| `4 digit pins` | One common per digit, enabled one at a time. |

**You talk to it with:** 12 digital pins, or a 74HC595 for the segments  ·  **Voltage:** 5V through resistors

> **Watch out:** Any delay() elsewhere in your program freezes the refresh cycle and the display visibly flickers. This is where non-blocking timing stops being an abstract principle.

*Used in lab manual projects: #22, #45*

## MAX7219 Module

An 8×8 LED matrix with a dedicated driver chip that does the multiplexing for you.

**How it works:** 64 LEDs would need 16 pins and constant CPU attention. The MAX7219 handles all the scanning, current limiting and brightness control in hardware; you just shift it 8 bytes over three wires and it maintains the image on its own.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V. |
| `DIN` | Data in. |
| `CS` | Chip select — latches the transfer. |
| `CLK` | Clock. |

**You talk to it with:** SPI-like, 3 wires. Library: LedControl or MD_MAX72XX  ·  **Voltage:** 5V

> **Watch out:** Keep an 8-byte array as your frame buffer, draw into that, then push the whole buffer. Writing to the display as you compute causes tearing and makes animation much harder than it needs to be.

*Used in lab manual projects: #27, #28*

## LCD1602 Module

A 16-character, 2-line text display driven by the classic HD44780 controller.

**How it works:** It holds its own character RAM and a font table, so you send it text and it keeps displaying it with no further attention. In 4-bit mode you send each byte as two nibbles, which halves the pins needed from 11 to 6.

| Pin | What it does |
|---|---|
| `VSS / VDD` | GND and 5V. |
| `V0` | Contrast — must go to a potentiometer wiper, not to power. |
| `RS` | Register select: command or character. |
| `RW` | Read/write — tie to GND for write-only. |
| `E` | Enable — the strobe that clocks data in. |
| `D4-D7` | Data lines used in 4-bit mode. D0-D3 stay unconnected. |
| `A / K` | Backlight anode and cathode. |

**You talk to it with:** 6 digital pins. Library: LiquidCrystal  ·  **Voltage:** 5V

> **Watch out:** Yours has plain pin headers and no I2C backpack, so most online tutorials won't match your wiring. And a screen showing faint boxes or nothing at all is almost always contrast, not code — sweep the pot through its whole range before suspecting anything else.

*Used in lab manual projects: #24, #25, #26, #44, #48, #49*

---

# Things that make noise

Two buzzers that look almost identical and behave completely differently.

## Active Buzzer

A buzzer with an oscillator built in — apply DC and it sounds.

**How it works:** Contains a piezo element plus a small driving circuit. Give it voltage and it produces one fixed frequency. You control whether it sounds, not what note it plays.

| Pin | What it does |
|---|---|
| `+` | To a digital pin (or a transistor for volume). |
| `−` | To GND. |

**You talk to it with:** digitalWrite() HIGH or LOW  ·  **Voltage:** 5V

> **Watch out:** Usually the taller one, fully sealed with a sticker on top, and it has polarity. Trying to play a melody on it produces one note at one pitch, no matter what your code does.

*Used in lab manual projects: #13, #48*

## Passive Buzzer

A bare piezo element with no oscillator — you supply the frequency.

**How it works:** A piezo disc flexes once per cycle of the signal you feed it. Feed it a 440Hz square wave and it plays A. That's why it can play melodies and the active one cannot.

| Pin | What it does |
|---|---|
| `+ / signal` | To a PWM-capable digital pin. |
| `−` | To GND. |

**You talk to it with:** tone(pin, frequency) and noTone(pin)  ·  **Voltage:** 5V

> **Watch out:** Usually shorter, and you can see the green PCB on its underside. tone() uses a hardware timer that conflicts with analogWrite() on pins 3 and 11 — if PWM stops working while sound plays, that's why.

*Used in lab manual projects: #10, #30, #31, #46*

---

# Things that move

Every one of these needs more current than a GPIO pin can give. That constraint shapes all the wiring.

## SG90 Servo Motor

A geared motor that holds a commanded angle rather than spinning freely.

**How it works:** Inside is a DC motor, a gear train, a potentiometer reading the output shaft, and a control circuit. You send a pulse every 20ms; the pulse width sets the target angle, and the internal loop drives the motor until the pot agrees. About 1ms is one end, 2ms the other.

| Pin | What it does |
|---|---|
| `Brown / black` | GND. |
| `Red` | 5V power. |
| `Orange / yellow` | Signal — the pulse train. |

**You talk to it with:** Servo library: attach(), write(angle), writeMicroseconds()  ·  **Voltage:** 4.8-6V

> **Watch out:** Stall current is around 700mA — far past what the UNO's 5V pin can give. Power it from the power supply module with a shared ground, or it browns out the board and resets it mid-move.

*Used in lab manual projects: #33, #47, #50, #55*

## Stepper Motor (28BYJ-48)

A motor that moves in discrete steps instead of spinning continuously.

**How it works:** Four coils energise in sequence, dragging a magnetised rotor one step at a time. A 64:1 reduction gearbox on the output makes it slow but precise and reasonably strong — roughly 2048 steps per output revolution in full-step mode, 4096 in half-step.

| Pin | What it does |
|---|---|
| `5-pin connector` | Plugs directly into the ULN2003 board. Four coil wires plus a common. |

**You talk to it with:** Always through the ULN2003. Library: Stepper or AccelStepper  ·  **Voltage:** 5V

> **Watch out:** It is open-loop: nothing tells the Arduino where the shaft actually is. Miss steps under load and your code's idea of position silently drifts from reality, with no error raised anywhere.

*Used in lab manual projects: #35*

## ULN2003 Driver Module

The current amplifier that sits between the Arduino and the stepper.

**How it works:** An array of seven Darlington transistor pairs. Each takes a weak logic input and switches a much larger current to ground. It also contains the flyback diodes the coils need, which is why this board can drive an inductive load safely straight out of the box.

| Pin | What it does |
|---|---|
| `IN1-IN4` | From four Arduino digital pins. |
| `5V / GND` | Motor power — use external supply for sustained running. |
| `White socket` | The stepper plugs in here. |

**You talk to it with:** Four digital pins, driven in sequence  ·  **Voltage:** 5V

> **Watch out:** The four onboard LEDs mirror the coil states. If your sequence is wrong the motor buzzes and vibrates instead of turning — watch the LEDs chase in order to confirm your step pattern before blaming the motor.

*Used in lab manual projects: #35*

## DC Motor + Fan Blade

A small brushed motor, 3-6V, with a push-fit propeller.

**How it works:** Brushes commutate current through the rotor windings as it spins. It draws a large current spike on startup and generates a damaging voltage spike when switched off, because a collapsing magnetic field resists the change.

| Pin | What it does |
|---|---|
| `Two leads` | No polarity requirement — swapping them reverses direction. |

**You talk to it with:** Through a transistor (on/off, PWM) or an L293D (bidirectional)  ·  **Voltage:** 3-6V

> **Watch out:** Never wire it straight to a GPIO pin. It needs more current than the pin can source, and without a flyback diode across it the switch-off spike reaches hundreds of volts and destroys whatever is driving it.

*Used in lab manual projects: #32, #34, #51*

## 5V Relay Module

> ⚠️ **Handle with care — see the gotcha below.**

An electrically operated mechanical switch, isolated from your logic.

**How it works:** A small coil pulls a metal armature across, physically moving contacts. Because the moving contacts touch nothing electrically connected to the coil, the switched circuit is completely isolated from the Arduino — that's the whole point of a relay.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V for the coil circuit. |
| `IN` | Control signal from a digital pin. |
| `COM` | Common contact. |
| `NO` | Normally open — closed only when energised. |
| `NC` | Normally closed — open only when energised. |

**You talk to it with:** digitalWrite() (many modules are active-LOW)  ·  **Voltage:** 5V coil

> **Watch out:** Do not switch mains AC with this, on a breadboard, at your age, supervised or not. 220V is lethal and breadboard contacts are nowhere near rated for it. Switch a 9V battery circuit — it teaches you exactly the same thing about relays.

*Used in lab manual projects: #36*

---

# Sensors

Turning heat, light, sound, distance and motion into numbers.

## HC-SR04 Ultrasonic Sensor

Measures distance by timing an echo — sonar, essentially.

**How it works:** You pulse Trig high for 10µs. It emits eight 40kHz clicks and raises Echo. Echo stays high for exactly as long as the sound takes to travel out and back. Sound covers 343m per second, so distance in cm is the microsecond count divided by 58 — that constant is 34300 cm/s, halved for the round trip, converted to microseconds.

| Pin | What it does |
|---|---|
| `VCC` | 5V. |
| `Trig` | Output from Arduino — the 10µs start pulse. |
| `Echo` | Input to Arduino — its HIGH duration is your measurement. |
| `GND` | Ground. |

**You talk to it with:** digitalWrite() to trigger, pulseIn() to measure  ·  **Voltage:** 5V

> **Watch out:** Soft surfaces absorb the ping and angled ones deflect it, so both return nothing at all. Its cone is roughly 15°, so it misses anything off-axis — the same class of blind spot your wristband's ToF sensor has, for different physical reasons.

*Used in lab manual projects: #9, #10, #50, #52, #53, #54, #55*

## DHT11 Temperature & Humidity

A combined thermometer and hygrometer on one wire.

**How it works:** A thermistor plus a capacitive humidity element, read by a tiny onboard chip that spits the result out as a 40-bit packet on a single data line using its own timing protocol.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V. |
| `DATA` | One digital pin, needs a pull-up (usually already on the module). |

**You talk to it with:** Library: DHT — the bit timing is too tight to do by hand  ·  **Voltage:** 3-5V

> **Watch out:** Maximum one reading per second; poll faster and it returns stale values or NaN. Always check whether the read succeeded before using the number — silently wrong data is worse than an error.

*Used in lab manual projects: #12, #44*

## HC-SR501 PIR Motion Sensor

Detects a warm body moving through its field of view.

**How it works:** A pyroelectric sensor under a faceted plastic lens. It doesn't see heat — it sees heat *changing*. The lens splits the view into zones, and a person crossing between zones causes a swing the chip reports as motion. Standing perfectly still makes you invisible to it.

| Pin | What it does |
|---|---|
| `VCC` | 5-20V. |
| `OUT` | Goes HIGH on detection — 3.3V logic, still fine for the UNO. |
| `GND` | Ground. |
| `Two potentiometers` | Sensitivity (range, ~3-7m) and how long OUT stays high (5s-300s). |
| `Jumper` | H = retriggerable, L = single-shot. |

**You talk to it with:** digitalRead()  ·  **Voltage:** 5V

> **Watch out:** It needs 30-60 seconds after power-on to stabilise, and fires constantly until it does. If it 'doesn't work', wait a full minute before you debug anything. Its hardware pots also override your code entirely.

*Used in lab manual projects: #13*

## Sound Sensor Module

An electret microphone with an amplifier and a comparator.

**How it works:** The mic produces a tiny signal; the amp raises it; the comparator flips a digital output when it crosses a threshold you set with the onboard pot. The analog output gives you the actual level.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V. |
| `AO` | Analog level — use this if you want to measure loudness. |
| `DO` | Digital, HIGH past the pot's threshold. |

**You talk to it with:** analogRead() or digitalRead()  ·  **Voltage:** 5V

> **Watch out:** It reports loudness only. It has no idea what made the sound. Every bit of intelligence — a clap versus a door slam — has to come from your own timing logic.

*Used in lab manual projects: #14*

## Water Level Detection Sensor

A comb of exposed traces that reads how deep it is submerged.

**How it works:** Interleaved conductive traces. Water bridges them, and the more of the comb is covered, the lower the resistance between the two combs. Read as an analog voltage.

| Pin | What it does |
|---|---|
| `+ / −` | Power — ideally from a digital pin, not a permanent rail. |
| `S` | Analog signal out. |

**You talk to it with:** analogRead()  ·  **Voltage:** 5V

> **Watch out:** Continuous DC across the traces electrolyses them and they corrode within days. Power the sensor from a digital pin and switch it on only for the moment you take a reading — a genuine design fix, not a micro-optimisation.

*Used in lab manual projects: #15*

## Thermistor

A resistor whose resistance falls sharply as it gets hotter.

**How it works:** An NTC type, nominally 10kΩ at 25°C. The relationship is exponential, not linear, so converting resistance to temperature needs the B-parameter equation — real sensor maths rather than a simple map().

| Pin | What it does |
|---|---|
| `Two legs` | No polarity. Use it as the top or bottom half of a divider with a 10kΩ resistor. |

**You talk to it with:** analogRead(), then convert to resistance, then to Kelvin  ·  **Voltage:** 5V through a divider

> **Watch out:** Print the raw ADC value, the calculated resistance, and the final temperature separately. When the number is wrong you need to know which conversion stage broke — and one of them usually has.

*Used in lab manual projects: #11, #44, #51*

## Photoresistor (LDR) — ×2

A resistor that conducts better in bright light.

**How it works:** A cadmium sulphide film whose resistance drops as photons free charge carriers — from hundreds of kΩ in darkness to a few kΩ in bright light. It's a resistor, not a voltage source, so it only becomes readable inside a divider.

| Pin | What it does |
|---|---|
| `Two legs` | No polarity. Pair with a 10kΩ resistor to form a divider. |

**You talk to it with:** analogRead() on the divider's midpoint  ·  **Voltage:** 5V through a divider

> **Watch out:** A single threshold makes the output chatter when the light sits right at the boundary. Two thresholds — one to switch on, a different one to switch off — is hysteresis, and it's the fix for every noisy threshold you will ever write, including your wristband's zone edges.

*Used in lab manual projects: #8*

## GY-521 (MPU-6050)

A 6-axis motion tracker: 3-axis accelerometer plus 3-axis gyroscope.

**How it works:** Microscopic silicon structures deflect under acceleration and under rotation, and the chip measures the resulting capacitance changes. The accelerometer senses gravity, so at rest you can compute tilt from which way 'down' points, using atan2 on two axes.

| Pin | What it does |
|---|---|
| `VCC / GND` | Most breakouts accept 5V and regulate it down onboard. |
| `SCL / SDA` | I2C — A5 and A4. |
| `AD0` | Address select: low = 0x68, high = 0x69. |
| `INT` | Optional interrupt output. |

**You talk to it with:** I2C at address 0x68. Library: MPU6050 or Wire directly  ·  **Voltage:** 3.3-5V

> **Watch out:** Readings are signed 16-bit values split across two registers, so you must combine a high and a low byte and preserve the sign. Get that wrong and it appears to work for half the range and wrap bizarrely for the other half.

*Used in lab manual projects: #19, #20*

## Tilt Ball Switch

A metal ball in a tube that bridges two contacts when tipped.

**How it works:** Purely mechanical. Tilt past the trigger angle and the ball rolls onto both contacts, closing the circuit. It's a switch, not a sensor — there's no angle measurement, only open or closed.

| Pin | What it does |
|---|---|
| `Two legs` | No polarity. Wire like a button, with a pull-up. |

**You talk to it with:** digitalRead() with INPUT_PULLUP  ·  **Voltage:** 5V

> **Watch out:** A rolling ball bounces far worse than a button spring — you'll see dozens of transitions per movement. It needs a longer debounce window than a tactile switch; measure how much rather than guessing.

*Used in lab manual projects: #16*

---

# Human input

Buttons, knobs, sticks and remotes — everything a person touches.

## Push Button (tactile) — ×5

A momentary switch: connected while held, open when released.

**How it works:** Four legs, but only two circuits. The pins on each side are permanently joined internally; pressing bridges the two sides. Straddle the breadboard's centre gully and the internal pairs land on separate strips.

| Pin | What it does |
|---|---|
| `Pins 1 & 2` | Permanently connected to each other. |
| `Pins 3 & 4` | Permanently connected to each other. |
| `Pressing` | Joins the 1-2 pair to the 3-4 pair. |

**You talk to it with:** digitalRead(), ideally with INPUT_PULLUP  ·  **Voltage:** 5V

> **Watch out:** Two things bite here. First, a pin with nothing connected floats and reads random noise, not zero — use INPUT_PULLUP. Second, the contacts physically bounce, so one press registers three or four times until you debounce it in software.

*Used in lab manual projects: #3, #4, #5, #45, #46*

## Potentiometer 10K — ×2

A knob that outputs a voltage between 0 and 5V.

**How it works:** A resistive track with a wiper sliding along it — a voltage divider you can adjust by hand. The wiper's position sets what fraction of the supply appears on the middle pin.

| Pin | What it does |
|---|---|
| `Outer pin 1` | 5V. |
| `Middle (wiper)` | To an analog input. |
| `Outer pin 2` | GND. Swap the outer two to reverse the direction. |

**You talk to it with:** analogRead() → 0-1023  ·  **Voltage:** 5V

> **Watch out:** One of your two is effectively spoken for as the LCD's contrast control, since your display has no I2C backpack. Plan around having just one free for input.

*Used in lab manual projects: #7, #24, #29, #54*

## Joystick Module

Two potentiometers at right angles, plus a push switch under the cap.

**How it works:** Pushing the stick rotates one pot for X and another for Y. Both centre-spring back to roughly the middle of their range. Pressing straight down closes a momentary switch.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V. |
| `VRx / VRy` | Analog X and Y. |
| `SW` | Button — needs INPUT_PULLUP, reads LOW when pressed. |

**You talk to it with:** Two analogRead() plus one digitalRead()  ·  **Voltage:** 5V

> **Watch out:** Centre is never exactly 512, and it drifts. Calibrate at startup by sampling the resting position, then apply a deadzone so a released stick reads exactly zero — this is how real controllers handle it.

*Used in lab manual projects: #17, #34*

## Rotary Encoder Module

A knob that spins endlessly and reports movement rather than position.

**How it works:** Two switches offset inside so their signals are a quarter-cycle apart — quadrature. Which one changes first tells you the direction. Unlike a pot it has no endpoints, so you track a running count instead of reading an absolute value.

| Pin | What it does |
|---|---|
| `CLK` | Channel A. |
| `DT` | Channel B — its state at CLK's edge gives you direction. |
| `SW` | The built-in push button. |
| `+ / GND` | 5V. |

**You talk to it with:** digitalRead() polling, or attachInterrupt() for reliability  ·  **Voltage:** 5V

> **Watch out:** Polling in loop() loses counts when you spin it fast. The interrupt version is the real answer — and any variable shared with an interrupt handler must be declared volatile, or the compiler optimises your reads away and the bug becomes invisible.

*Used in lab manual projects: #18*

## 4×4 Membrane Keypad

Sixteen buttons behind a flat plastic sheet, on eight wires.

**How it works:** The keys sit at the crossings of four rows and four columns. To find a press you drive one row at a time and read all four columns; a key at that intersection connects them. Sixteen buttons on eight wires instead of sixteen.

| Pin | What it does |
|---|---|
| `8-pin ribbon` | Four rows then four columns — check which end is which by testing continuity. |

**You talk to it with:** 8 digital pins. Library: Keypad, or scan it yourself  ·  **Voltage:** 5V

> **Watch out:** Press three keys forming a rectangle and a phantom fourth appears — the matrix cannot tell the difference. Real keyboards fix this with a diode per key; understanding why is understanding matrix scanning.

*Used in lab manual projects: #43, #48, #49*

## IR Receiver + Remote Control — ×2

A demodulator chip that decodes flashes of infrared light from the handset.

**How it works:** The remote's LED flashes a 38kHz carrier, switched on and off in patterns that encode each button. The receiver strips out the carrier and hands you the raw bit pattern; a library turns that into a number. The carrier exists so sunlight and room lighting don't swamp the signal.

| Pin | What it does |
|---|---|
| `OUT` | To any digital pin. |
| `GND` | Ground. |
| `VCC` | 5V. Note this order differs between modules — check the silkscreen. |

**You talk to it with:** Library: IRremote  ·  **Voltage:** 5V

> **Watch out:** Holding a button sends a short repeat code rather than the original code again — often 0xFFFFFFFF. Handle that case or held buttons behave very strangely. It's also line-of-sight and confused by bright sunlight.

*Used in lab manual projects: #40, #41*

---

# Chips and comms modules

Bare ICs and the boards that speak a real protocol.

## 74HC595 Shift Register

Turns three Arduino pins into eight outputs.

**How it works:** Two stages. A shift register accepts bits one at a time on each clock pulse, sliding them along a queue of eight. A separate storage register copies all eight to the output pins at once when you pulse the latch. That two-stage design is why the outputs don't visibly ripple while you're loading them.

| Pin | What it does |
|---|---|
| `DS (14)` | Serial data in. |
| `SHCP (11)` | Shift clock — one pulse per bit. |
| `STCP (12)` | Latch — copies the eight bits to the outputs. |
| `OE (13)` | Output enable, active low — tie to GND. |
| `MR (10)` | Master reset, active low — tie to 5V. |
| `Q0-Q7` | The eight outputs. |
| `Q7' (9)` | Overflow out, for daisy-chaining more registers. |

**You talk to it with:** shiftOut(), or write the clock/latch sequence yourself  ·  **Voltage:** 5V

> **Watch out:** Forgetting to tie OE low and MR high is the classic failure — the chip appears completely dead with no other symptom. Write your own shiftOut with digitalWrite once before using the built-in; the latch only makes sense once you've seen what happens without it.

*Used in lab manual projects: #23*

## L293D Motor Driver

A dual H-bridge — lets you run two motors forwards and backwards.

**How it works:** An H-bridge is four switches around the motor. Close the top-left and bottom-right and current flows one way; close the opposite pair and it flows the other way, reversing the motor. The chip contains two of these plus the clamp diodes.

| Pin | What it does |
|---|---|
| `VCC1 (16)` | Logic supply, 5V. |
| `VCC2 (8)` | Motor supply — can be higher than 5V. |
| `EN1 (1), EN2 (9)` | Enable each bridge. PWM here controls speed. |
| `IN1-IN4` | Direction inputs, two per motor. |
| `OUT1-OUT4` | To the motors. |
| `GND (4,5,12,13)` | All four to ground — they also sink heat. |

**You talk to it with:** Two direction pins plus one PWM enable per motor  ·  **Voltage:** 5V logic, up to 36V motor

> **Watch out:** Closing both switches on the same side shorts the supply straight through the bridge. Draw the four switch states on paper and find the forbidden combination there, rather than finding it with smoke. It also drops about 2V, so a 6V supply delivers roughly 4V to the motor.

*Used in lab manual projects: #34*

## RC522 RFID Module

> ⚠️ **Handle with care — see the gotcha below.**

Reads the ID of cards and fobs held near it.

**How it works:** It energises a 13.56MHz field. A passive card has no battery — it harvests power from that field, wakes up, and replies with its unique ID and whatever is in its memory sectors. Range is a few centimetres because the coupling is inductive.

| Pin | What it does |
|---|---|
| `3.3V` | Power — 3.3V only. |
| `RST` | Reset. |
| `GND` | Ground. |
| `IRQ` | Interrupt, usually unused. |
| `MISO / MOSI / SCK` | SPI data lines — D12, D11, D13. |
| `SDA (SS)` | Chip select — D10. |

**You talk to it with:** SPI. Library: MFRC522  ·  **Voltage:** 3.3V ONLY

> **Watch out:** Connecting VCC to 5V destroys it. This is by far the most common way this module dies, and there is no warning — it simply stops working. The SPI signal pins tolerate 5V logic from the UNO; the power pin does not.

*Used in lab manual projects: #42, #47*

## DS1307 RTC Module

A clock that keeps running when the Arduino is switched off.

**How it works:** A dedicated timekeeping chip with a 32.768kHz crystal — a frequency chosen because it's 2^15, so a 15-stage binary divider yields exactly one pulse per second. A coin cell keeps it running through power loss. It stores time in BCD, where each digit occupies four bits.

| Pin | What it does |
|---|---|
| `VCC / GND` | 5V. |
| `SDA / SCL` | I2C — A4 and A5. |
| `SQW` | Optional square wave output. |
| `Coin cell` | CR2032 backup. |

**You talk to it with:** I2C at address 0x68. Library: RTClib  ·  **Voltage:** 5V

> **Watch out:** Without a healthy coin cell it forgets the time on every power cycle — check the battery before debugging code. It also isn't temperature compensated, so expect it to drift by seconds per week.

*Used in lab manual projects: #39, #44, #48*

---

# Passives

The unglamorous parts. Getting these wrong is what actually destroys hardware.

## Resistors (assorted, 120pcs) — ×120

Components that limit current. The most-used part in the kit.

**How it works:** Ohm's law: current equals voltage divided by resistance. Colour bands encode the value — first two bands are digits, third is the number of zeros, fourth is tolerance. Red-red-brown is 220Ω; brown-black-orange is 10kΩ.

| Pin | What it does |
|---|---|
| `220Ω` | LED current limiting — red, red, brown. |
| `1kΩ` | Transistor base resistors — brown, black, red. |
| `10kΩ` | Pull-ups and voltage dividers — brown, black, orange. |

**You talk to it with:** n/a  ·  **Voltage:** n/a

> **Watch out:** There's no polarity and no way to tell a 220Ω from a 10kΩ at a glance — the bands are the only marking. Sort them into labelled bags on day one, or you'll spend the whole project squinting at colour codes.

*Used in lab manual projects: #1, #3, #6*

## NPN Transistors (PN2222, S8050) — ×10

An electrically controlled switch — a small current lets a much larger one flow.

**How it works:** A small current into the base allows a much larger current from collector to emitter. That's how a 20mA pin controls a 200mA motor. The base resistor exists to limit the pin's current; without it the base-emitter junction looks nearly like a short circuit to the pin.

| Pin | What it does |
|---|---|
| `Flat face toward you, legs down` | Left = Emitter, middle = Base, right = Collector, for both of these parts. |
| `Emitter` | To GND. |
| `Base` | To the Arduino pin through ~220Ω-1kΩ. |
| `Collector` | To the load's negative side. |

**You talk to it with:** digitalWrite() or analogWrite() on the base resistor  ·  **Voltage:** 5V logic

> **Watch out:** Pinouts genuinely vary between packages and manufacturers — your own project README warns about exactly this. Confirm with a multimeter's diode-test mode before wiring: from the base you should read a diode drop to both other legs.

*Used in lab manual projects: #32, #51*

## Diode Rectifier — ×5

> ⚠️ **Handle with care — see the gotcha below.**

A one-way valve for current. Its main job here is protecting against motor kickback.

**How it works:** When you switch off an inductive load, its magnetic field collapses and generates a large reverse voltage spike — hundreds of volts from a small motor. Wire the diode backwards across the load and that spike gets a harmless loop to circulate in instead of destroying your transistor.

| Pin | What it does |
|---|---|
| `Banded end` | Cathode. It goes to the positive side of the motor. |
| `Plain end` | Anode, to the negative side, where the transistor connects. |

**You talk to it with:** n/a  ·  **Voltage:** n/a

> **Watch out:** Fit it backwards and you create a dead short across your power supply the moment you power up. Banded end toward positive — check it twice, because this mistake is instant and smoky.

*Used in lab manual projects: #32, #34, #51*

## Electrolytic Capacitors (100µF, 10µF) — ×4

> ⚠️ **Handle with care — see the gotcha below.**

Small energy reservoirs that smooth out sudden current demands.

**How it works:** Stores charge and releases it fast. Put one across the power rails and it supplies the brief surge when a motor starts, instead of that surge dragging the whole rail down and resetting the Arduino.

| Pin | What it does |
|---|---|
| `Long leg` | Positive. |
| `Stripe on the can` | Marks the negative leg. |

**You talk to it with:** n/a  ·  **Voltage:** Check the rated voltage on the can

> **Watch out:** These are polarised. Fitting one backwards makes it heat up and eventually burst — genuinely, with a bang and a smell. The stripe always marks negative.

*Used in lab manual projects: #37*

## Ceramic Capacitors (104, 22pF) — ×10

Small non-polarised capacitors, mostly used to clean up noise.

**How it works:** A 0.1µF part next to a chip's power pins supplies the tiny high-speed current spikes the chip needs as it switches, which the wiring is too slow to deliver. That's decoupling, and it's why nearly every digital board is covered in them.

| Pin | What it does |
|---|---|
| `Two legs` | No polarity — fit either way round. |

**You talk to it with:** n/a  ·  **Voltage:** n/a

> **Watch out:** Your box says '104pF' and that's a printing error. The 104 marking means 10 × 10⁴ pF = 100,000pF = 100nF = 0.1µF — about a thousand times what the label claims. The 22pF ones really are 22pF.

---

