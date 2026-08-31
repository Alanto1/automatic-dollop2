# TikTok — "AI Spider Robot" build short

**Length:** ~26s spoken (30s hard cap with room for pauses)
**Face:** none — hands, close-ups, top-down and floor-level POV only
**Voice:** AI TTS. Paste the block below straight into the voice tool.

---

## 1. Voiceover — paste-ready

> This spider robot has no remote. It decides where to walk on its own.
>
> Twelve servos. Three joints per leg. One board doing all the math.
>
> A camera looks for open floor, and the code solves every leg angle in real time.
>
> No pre-recorded walk cycle — it re-plans each step.
>
> First test, it face-planted. Twenty tweaks later — it walks.
>
> Part two, I teach it to hunt. Follow so you don't miss it.

73 words. At a normal TTS pace (~2.9 words/sec) that lands at 25–26 seconds,
leaving a beat of silence between lines. If your read comes out long, cut
"No pre-recorded walk cycle — it re-plans each step." first — it is the only
line the video still works without.

---

## 2. Scenario — shot by shot

| Time | Voiceover | What's on screen (no face) | On-screen text |
|---|---|---|---|
| 0:00–0:04 | "This spider robot has no remote. It decides where to walk on its own." | Floor-level shot, robot walks straight at the lens, legs filling frame. Cut on the 3rd step. | `no remote. no joystick.` |
| 0:04–0:09 | "Twelve servos. Three joints per leg. One board doing all the math." | Fast cuts: servo horn snapping into a bracket, a leg being screwed on, the board's LED blinking. Hands only. | `12 servos` → `3 joints / leg` |
| 0:09–0:16 | "A camera looks for open floor, and the code solves every leg angle in real time." | Split moment: robot's camera view (or a phone taped to it) then the same floor from the side. Overlay your terminal/serial output scrolling. | `it sees the floor` |
| 0:16–0:20 | "No pre-recorded walk cycle — it re-plans each step." | Top-down of the robot stepping over a shoe / cable / book. Slow-mo the leg lift. | `it re-plans every step` |
| 0:20–0:25 | "First test, it face-planted. Twenty tweaks later — it walks." | The fail clip, full speed, no edit. Hard cut to the clean walk. | `attempt 1` → `attempt 20` |
| 0:25–0:29 | "Part two, I teach it to hunt. Follow so you don't miss it." | Robot walks out of frame toward the camera, or freezes with legs coiled. | `part 2 →` |

**Editing rules that carry this:** every cut on a beat, nothing held longer
than 2.5s, and the fail clip is the retention hook — do not clean it up or
speed it up. Keep the servo whine in the audio bed under the music; that
sound is half the appeal of a walking robot.

---

## 3. Caption + hashtags

> I built a spider robot that decides its own steps. Attempt 1 vs attempt 20 👇
>
> #robotics #arduino #hexapod #diyrobot #engineering #3dprinting #buildinpublic #ai

---

## 4. Honesty check before you post

Only say the lines you can actually show. If the build does not yet have a
camera picking a path, cut the "camera looks for open floor" line and replace
it with what it really does — e.g. "An ultrasonic sensor watches for walls,
and the code solves every leg angle in real time." Overclaiming the AI part
is the one thing the robotics side of TikTok reliably calls out in the
comments, and a real inverse-kinematics gait is already impressive on its own.

**Swap-in lines if the spec differs:**
- Servo count other than 12 → "Eighteen servos. Three joints per leg."
- No vision, distance sensor only → "A distance sensor feels for walls, and the code solves every leg angle in real time."
- Remote-driven, autonomous gait only → drop line 1 and open with "Nothing here is a pre-recorded walk cycle. It solves every step live."
