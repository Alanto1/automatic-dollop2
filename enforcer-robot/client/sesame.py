"""A thin client for Sesame's JSON API, with the transport kept behind a seam.

    from sesame import Sesame, FakeTransport
    bot = Sesame(FakeTransport())
    bot.stand(); bot.turn(-30); bot.walk("forward", steps=3); bot.face("smug")

The point of this file is the seam, not the commands. You will start on WiFi
because that needs no firmware change, and you will probably move to UART
later -- the two boards end up about 5cm apart on the same robot, and a
wireless hop between them is silly once they are bolted together. When that
happens, only the Transport changes; everything above it is untouched.

Which is also why FakeTransport exists: the entire behaviour layer can be
written and tested against a robot that only logs, months before a real one
walks.

⚠️ Firing is deliberately NOT in this client. The pump lives behind the
firmware interlocks in BEHAVIOURS.md, on the ESP32's own GPIO. If squirting
were a method here, anything that could reach this object could soak someone
-- including, eventually, an LLM. See LLM_VOICE.md.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

# Sesame's face names. Anything else is rejected client-side rather than
# silently ignored by the firmware, because a typo'd face is otherwise a
# very quiet bug.
FACES = {"neutral", "happy", "sad", "angry", "surprised", "sleepy", "smug", "suspicious"}

DIRECTIONS = {"forward", "back", "left", "right"}

# The mood machine speaks in moods; Sesame speaks in faces. This is the whole
# mapping, kept here so BEHAVIOURS.md has exactly one place to point at.
MOOD_FACE = {
    "chill": "neutral",
    "suspicious": "suspicious",
    "warning": "angry",
    "strike": "angry",
    "smug": "smug",
}


class Transport(Protocol):
    """Anything that can carry one JSON command and bring back a reply."""

    def send(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def close(self) -> None: ...


@dataclass
class FakeTransport:
    """Logs commands instead of sending them. The robot you have today.

    Records everything so tests can assert on the exact command sequence a
    behaviour produced -- which is the only way to test "creep forward, then
    turn, then look smug" without a robot.
    """

    log: list[dict[str, Any]] = field(default_factory=list)
    verbose: bool = True
    fail_on: set[str] = field(default_factory=set)   # command names to reject

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.log.append(payload)
        if self.verbose:
            print("  ->", json.dumps(payload))
        if payload.get("cmd") in self.fail_on:
            return {"ok": False, "error": "simulated failure"}
        return {"ok": True}

    def close(self) -> None:
        pass

    # -- helpers for tests --
    def cmds(self) -> list[str]:
        return [p.get("cmd") for p in self.log]

    def clear(self) -> None:
        self.log.clear()


@dataclass
class WiFiTransport:
    """HTTP POST to the ESP32's JSON endpoint. Where you start.

    No firmware change needed -- Sesame already serves its web UI this way.
    Uses only the standard library so the Pi Zero needs nothing extra
    installed, which matters when you have 422MB of RAM and a 512MB card.
    """

    host: str = "sesame.local"
    port: int = 80
    path: str = "/api"
    timeout: float = 1.5

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        import urllib.error
        import urllib.request

        url = "http://%s:%d%s" % (self.host, self.port, self.path)
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.URLError as e:
            # Never raise into the behaviour layer. A dropped command must
            # degrade to "that move did not happen", not crash the robot
            # mid-demo with a stack trace.
            return {"ok": False, "error": str(e)}

    def close(self) -> None:
        pass


@dataclass
class SerialTransport:
    """Newline-delimited JSON over UART. Where this ends up.

    The two boards sit ~5cm apart on the same chassis. A wire is lower
    latency, uses less power, and cannot be knocked out by venue WiFi -- and
    a competition hall is the worst 2.4GHz environment you will ever meet.
    """

    port: str = "/dev/serial0"
    baud: int = 115200
    timeout: float = 1.0

    def __post_init__(self):
        import serial  # pyserial; only needed for this transport
        self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout)

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ser.write((json.dumps(payload) + "\n").encode())
        line = self._ser.readline().decode().strip()
        try:
            return json.loads(line) if line else {"ok": False, "error": "timeout"}
        except json.JSONDecodeError:
            return {"ok": False, "error": "bad reply: %r" % line[:60]}

    def close(self) -> None:
        self._ser.close()


class Sesame:
    """Intents in, JSON out. No joint angles anywhere in this class.

    That is the architectural line from BEHAVIOURS.md: the Pi decides *what*
    at 1-2 Hz, the ESP32 decides *how* at 30-50 Hz. If this file ever grows a
    method that takes a servo angle, the motion engine has been moved to the
    wrong side of the seam and the robot will go back to looking stiff.
    """

    def __init__(self, transport: Transport, min_gap_s: float = 0.05):
        self.t = transport
        self.min_gap_s = min_gap_s
        self._last_send = 0.0
        self.failures = 0

    # -- plumbing ----------------------------------------------------------

    def _send(self, cmd: str, **args: Any) -> bool:
        # Rate-limit. The mood machine runs at 1-2 Hz but a behaviour script
        # can emit a burst, and Sesame's HTTP stack is a small ESP32.
        gap = time.monotonic() - self._last_send
        if gap < self.min_gap_s:
            time.sleep(self.min_gap_s - gap)
        self._last_send = time.monotonic()

        reply = self.t.send({"cmd": cmd, **args})
        ok = bool(reply.get("ok"))
        if not ok:
            self.failures += 1
        return ok

    def close(self) -> None:
        self.t.close()

    def __enter__(self) -> "Sesame":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- posture -----------------------------------------------------------

    def stand(self) -> bool:
        return self._send("stand")

    def sit(self) -> bool:
        return self._send("sit")

    def crouch(self) -> bool:
        return self._send("crouch")

    # -- locomotion --------------------------------------------------------

    def walk(self, direction: str = "forward", steps: int = 1) -> bool:
        if direction not in DIRECTIONS:
            raise ValueError("direction must be one of %s, got %r"
                             % (sorted(DIRECTIONS), direction))
        if steps < 1:
            raise ValueError("steps must be >= 1, got %r" % steps)
        return self._send("walk", dir=direction, steps=int(steps))

    def turn(self, degrees: float) -> bool:
        """Yaw. Negative is left, positive is right.

        Clamped rather than rejected: aiming code will hand this whatever the
        pixel-to-degree calibration produced, and a bad frame should make the
        robot turn too far, not raise inside the control loop.
        """
        deg = max(-180.0, min(180.0, float(degrees)))
        return self._send("turn", deg=round(deg, 1))

    def stop(self) -> bool:
        return self._send("stop")

    # -- expression --------------------------------------------------------

    def face(self, name: str) -> bool:
        if name not in FACES:
            raise ValueError("unknown face %r, expected one of %s"
                             % (name, sorted(FACES)))
        return self._send("face", name=name)

    def show_mood(self, mood: Any) -> bool:
        """Accepts a `Mood` enum from brain/mood.py, or its string value."""
        key = getattr(mood, "value", mood)
        return self.face(MOOD_FACE.get(key, "neutral"))

    # -- composite behaviours ----------------------------------------------
    #
    # These are the vocabulary BEHAVIOURS.md describes. They live here rather
    # than in the mood machine because they are about *the body*, and the
    # mood machine is deliberately body-agnostic.

    def perk_up(self) -> bool:
        """Noticed you. Stand tall, look suspicious."""
        return self.stand() and self.face("suspicious")

    def creep_in(self, steps: int = 2) -> bool:
        """Escalating. Crouch low and close the distance."""
        return self.crouch() and self.walk("forward", steps) and self.face("angry")

    def victory_bounce(self) -> bool:
        """Landed a hit. Gloat."""
        return self.stand() and self.face("smug")

    def back_off(self, steps: int = 2) -> bool:
        """Flee reflex, or cooldown. Retreat and reset."""
        return self.walk("back", steps) and self.stand() and self.face("neutral")
