# T-Embed CC1101 — Beginner Setup & First Projects

A step-by-step, safe walkthrough for a first-time owner of the **LilyGo T-Embed
CC1101**, from unboxing to your first projects with **Bruce** firmware. Every
project here is on hardware **you own** — see [../ETHICS_AND_LEGAL.md](../ETHICS_AND_LEGAL.md).

Device page: [../devices/lilygo-t-embed-cc1101.md](../devices/lilygo-t-embed-cc1101.md)

---

## Step 0 — The rule that never changes
Bruce includes **jamming / deauth** features. Using those — or replaying/cloning
anything — against devices, cards, or networks you **don't own** is **illegal**
in nearly every country, even as a joke. Keep everything to **your own** gear and
you're completely fine. (If you're a minor, show a parent what you're building.)

## Step 1 — Inspect the box
- [ ] Confirm you have the **board**, the **antenna**, and (optional) a **microSD**.
- [ ] **Screw the antenna** onto the SMA connector — finger-tight, don't force it.
      Sub-GHz barely works without it.
- [ ] Peel the protective film off the screen.

## Step 2 — First power-on
- [ ] Charge it over USB-C for a bit.
- [ ] Power on — it boots the **stock/demo firmware** LilyGo shipped.
- [ ] Just confirm the **screen lights up** and the **rotary wheel + buttons** work.
      You'll replace this firmware next, so ignore what the demo does.

## Step 3 — Gear you need to flash (where beginners get stuck)
- [ ] A **desktop/laptop** (not a phone).
- [ ] **Chrome or Edge** browser.
- [ ] A **USB-C _data_ cable** — many cables are **charge-only** and silently fail.
      If the board isn't detected, swap the cable first.

## Step 4 — Flash Bruce
1. Open Chrome/Edge → **https://flash.pingequa.com/devices/t-embed-bruce**
2. Plug the board in with the data cable.
3. Select the **T-Embed CC1101** variant (not the plain T-Embed).
4. **Connect** → pick the serial port → **Install / Flash**.
5. Wait ~2–3 minutes. **Don't unplug.**
6. **Won't connect?** Hold **BOOT**, tap **RESET**, release **BOOT**, retry Connect
   (forces flash mode).

Board reboots into **Bruce** when done. 🎉

- Bruce project: https://github.com/pr3y/Bruce

## Step 5 — First-time setup in Bruce
- [ ] Set the **clock / RTC** (Settings) so captures are timestamped.
- [ ] Set your **Sub-GHz region** (EU) in Settings.
- [ ] microSD: **format it FAT32** on your PC first, then insert. Bruce saves
      captures/files to it. A genuine **16–32 GB** card is ideal (bigger works too).
- [ ] Scroll every menu with the wheel for 5 minutes to learn the layout.

## Step 6 — First safe projects (on your OWN stuff), in order
1. **IR remote** — learn your TV/AC remote, then replay it. Easiest first win.
2. **WiFi scan** — list nearby networks (just looking is fine).
3. **BLE scan** — list nearby Bluetooth devices.
4. **NFC read** — scan one of your own blank/NFC tags, view its data.
5. **Sub-GHz** — capture *your own* garage/doorbell remote, replay to yourself.

## Step 7 — Updates & trying other firmware
- Re-flash the newer Bruce build (repeat Step 4) when you want new features.
- Want **Marauder** (deeper WiFi) or **CapibaraZero** (Flipper-style)? Just reflash,
  or set up **M5Stick Launcher** for dual-boot once you're comfortable.
  See [firmware-guide.md](firmware-guide.md).

## Troubleshooting quick table
| Problem | Fix |
|---|---|
| Board not detected when flashing | Use a **data** USB-C cable; try BOOT+RESET flash mode |
| Sub-GHz does nothing | Antenna not attached / wrong region setting |
| SD card not recognised | Reformat **FAT32**, use a genuine 16–32 GB card |
| Bruce feels buggy | Re-flash the latest stable release |
| Bricked / weird boot | Re-flash via the browser flasher — it recovers the board |
