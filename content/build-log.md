# Build log — the format

One file that is both the record and the posting queue. Each session you fill
five fields while the soldering iron cools. Those five fields *are* the
voiceover — one line each — so writing the log writes the video.

**The rule: five lines, about fourteen words each.** That is ~70 words, ~25
seconds spoken, which fits a 30s post with pauses. No hook, no call to
action, no "wait for it". The specificity is the hook.

| Field | Becomes | Line |
|---|---|---|
| Where it stood | the catch-up | "Last time it had legs but no idea how to use them." |
| What I tried | the substance | "Today I wrote the inverse kinematics." |
| What broke | the honest middle | "The front left servo hit its limit and it face-planted." |
| Where it stands now | the payoff | "Clamped the range. Tried again. It walks." |
| Next | the flat ending | "That's tomorrow's problem." |

### Why this reads as natural

- **Start mid-thought.** "Spider robot, day six" — not "You won't believe…".
- **Say the real number.** Ten centimetres of drift, 140 degrees, six legs.
  Numbers are what make it sound like a log instead of an ad.
- **Keep the failure at full speed.** Don't restage it, don't caption it
  "FAIL". It happened; say it in one sentence and move on.
- **End flat.** "That's tomorrow's problem" outperforms "FOLLOW FOR PART 2",
  because the series itself is the reason to come back.
- **Film while you build, not after.** One clip per beat, phone propped
  vertical, hands only. Re-staged footage is what makes a build video feel
  like an ad.

### Feeding it to the AI voice

Paste the five lines with a blank line between each — most TTS tools read
that as a breath. Replace em dashes with periods; some readers stumble on
them. Pick the most conversational voice available and slow it slightly;
the default TikTok voice reads a log like a news bulletin.

---

## Log 001 — Spider robot: first walk

**Where it stood:** six legs assembled, no gait code
**Tried:** inverse kinematics for one leg, mirrored to all six
**Broke:** front-left servo hit its limit, whole robot face-planted
**Stands at:** walks two metres, drifts ~10 cm right
**Next:** trim the drift
**Clips:** faceplant (full speed), clean walk, close-up of the leg lift

### Voiceover — paste-ready

> Spider robot, day six. Last time it had legs but no idea how to use them.
>
> Today I wrote the inverse kinematics. Give it a foot position, it solves the three joint angles.
>
> Mirrored it to all six legs. First run, the front left servo hit its limit and the whole thing face-planted.
>
> Clamped the range. Tried again. It walks.
>
> Drifts about ten centimetres right over two metres. That's tomorrow's problem.

71 words, ~25s spoken.

### Shots

| Time | Line | On screen |
|---|---|---|
| 0:00–0:05 | day six / last time | Static shot of the robot sitting still, legs splayed. Title card `LOG 001`. |
| 0:05–0:11 | inverse kinematics | Screen recording of the solver output, or one leg moving to a point you tap. |
| 0:11–0:19 | mirrored / face-planted | The fail clip. Full speed, uncut, sound on. |
| 0:19–0:23 | clamped / it walks | The walk, floor level, let it run the full two metres. |
| 0:23–0:28 | drifts / tomorrow's problem | Top-down showing the drift, or a tape mark on the floor. |

---

## Log 002 — (template, copy this block)

**Where it stood:**
**Tried:**
**Broke:**
**Stands at:**
**Next:**
**Clips:**

### Voiceover

>
>
>
>
>

---

*A one-off, higher-energy cut — for a launch or a "here's the whole build"
post — lives in `tiktok-spider-robot-script.md`. Use that format rarely;
this one is the series.*
