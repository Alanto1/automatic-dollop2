# servo_test — check 10 MG90S before any of them go into a leg

Upstream's Phase 1 checklist has one line about this: *"MG90 servos tested
quickly on a servo tester or Arduino to catch DOA units."* It is worth more
than its length. A dead servo found on the bench is a two-minute swap. The
same servo found after it is screwed into a leg shell, wired into the
harness, and buried under the top cover is an hour of disassembly.

You have 10 and need 8, so you can afford two failures — but only if you
find them now.

## Wiring

| servo wire | goes to |
|---|---|
| brown / black | **GND**, common with the board |
| red | **external 5 V** — *not* the S2 Mini's 5 V pin |
| orange / yellow | **GPIO 1** |

⚠️ **Do not power servos from the S2 Mini.** One unloaded MG90S draws
~200 mA and peaks far higher the moment it starts moving; the board's
regulator is not a servo supply. Use the Waveshare buck converter or a phone
charger.

⚠️ **Tie the external supply's ground to the board's ground.** Without a
common ground the PWM signal has no reference, and the servo twitches or
ignores you entirely. This is the most common wiring mistake on a first
servo bench rig.

## Setup

Board settings are the same ones that worked for `board_test`:

- Board: **LOLIN S2 Mini**
- **USB CDC On Boot: ENABLED** — without it Serial prints nothing

**No libraries.** This drives LEDC directly rather than pulling in
ESP32Servo, using the same `ESP_ARDUINO_VERSION_MAJOR` shim as
`board_test.ino` — which already compiles and runs on this machine. One less
thing to install, and one less thing to be subtly the wrong version of.

You *will* need ESP32Servo later, for Sesame's own
`sesame-motor-tester.ino`. Install it when you get there; it is not a
prerequisite for this sketch.

## Use

Open Serial Monitor at 115200. The servo centres on boot.

| command | does |
|---|---|
| `c` | centre at 90° and **hold** — press the horn on now |
| `s` | slow sweep 0 → 180 → 0, twice |
| `e` | endpoints: 0, 180, back to 90 |
| `<n>` | go to angle n |
| `d` | detach — shaft goes limp, safe to unplug |

Run `s` then `e` on each servo. It **passes** if:

1. it moves to every commanded angle without stalling
2. it **holds** position — no hunting, buzzing or drift
3. both endpoints are reachable and roughly symmetric about centre
4. it does not get hot after a minute of holding

Buzzing that never settles is a dying servo. Number the good ones with tape
as you go.

## Why the pulse widths matter

`MIN_PULSE 732` and `MAX_PULSE 2929` are copied from Sesame's own
`firmware/debugging-firmware/sesame-motor-tester.ino`, and they must not be
"improved".

90° here has to be the same shaft position as 90° in the real firmware. If
this sketch centres at a different pulse width than the robot later commands,
every horn you aligned against it is aligned to nothing, and the error shows
up as a robot that walks in a curve.

One thing that looks wrong and is not: **90° comes out at 1830 µs**, not the
textbook 1500 µs. That falls straight out of Sesame's band — 0° is 732 µs,
180° is 2929 µs, and the midpoint of those is 1830. If you put a scope on it
and expect 1500, you will think something is broken. Matching the robot
matters more than matching the convention.
