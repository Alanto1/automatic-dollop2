# client/ — talking to Sesame

```bash
./tests/run_tests.sh          # 13/13 tests passed, no robot needed
```

```python
from sesame import Sesame, FakeTransport
with Sesame(FakeTransport()) as bot:
    bot.perk_up()
    bot.creep_in(steps=2)
    bot.show_mood(Mood.SMUG)
```

## The point is the seam, not the commands

You will start on **WiFi**, because Sesame already serves JSON that way and
it needs no firmware change. You will probably end on **UART**, because the
two boards end up ~5 cm apart on the same chassis and a wireless hop between
them is silly once they are bolted together — and a competition hall is the
worst 2.4 GHz environment you will ever meet.

When that happens, only the `Transport` changes. Everything above it —
every behaviour, every test — is untouched. That is why `FakeTransport`
exists: the whole behaviour layer gets written and tested against a robot
that only logs, months before a real one walks.

```
  your behaviour code
        │
     Sesame          intents: stand / walk / turn / face
        │
    Transport        ← the seam. swap this, nothing else
     ╱    │    ╲
 Fake   WiFi  Serial
```

## Intents, never joint angles

`Sesame` has no method that takes a servo angle, and it must never grow one.
The Pi decides **what** at 1–2 Hz; the ESP32 decides **how** at 30–50 Hz. Put
interpolation on the Pi side of this seam and the robot goes straight back to
looking stiff — see `motion/`.

## Two deliberate design choices

**Failures are counted, not raised.** A dropped command means "that move did
not happen", not a stack trace in the middle of a demo. But a *composite*
stops at the first failure: if `crouch` failed the robot is in an unknown
posture, and walking anyway is how a quadruped falls off a desk.

**There is no `fire()` method, and there must never be one.** The pump lives
behind the five firmware interlocks in `BEHAVIOURS.md`, on the ESP32's own
GPIO. If squirting were reachable from this object, anything holding a
reference could soak someone — including, eventually, an LLM (`LLM_VOICE.md`).
There is a test asserting the method does not exist.
