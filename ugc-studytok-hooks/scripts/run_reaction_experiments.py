#!/usr/bin/env python3
"""
Raw TikTok Reaction Experiments — Sora 2
Pure reaction clips only. No demo, no caption, no stitching.
Goal: find the best motion styles, settings, expressions for Professor Curious hooks.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── Config ─────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"

OUT_DIR = Path.home() / ".openclaw/workspace/output/ugc-reaction-experiments"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Sora ───────────────────────────────────────────────────────────────────────

def submit_sora(prompt: str, seconds: int = 8) -> str:
    resp = requests.post(
        f"{BASE_URL}/videos",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(seconds)},
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    vid = job["id"]
    print(f"  [submit] → {vid}")
    return vid

def poll_sora(video_id: str) -> None:
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:300]}")
        data   = r.json()
        status = data.get("status", "unknown")
        prog   = data.get("progress", 0)
        print(f"  [poll] {status} {prog}%", flush=True)
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"Failed: {json.dumps(data.get('error', {}))}")

def download_sora(video_id: str, out_path: Path) -> Path:
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path

def send_to_slack(video_path: Path, exp: dict) -> None:
    r = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", (
            f"text=*[REACTION EXP]* `{exp['id']}`\n"
            f"*Setting:* {exp['setting']}\n"
            f"*Motion:* {exp['motion']}\n"
            f"*Expression:* {exp['expression']}"
        ),
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {r.stdout.strip() or r.stderr.strip()}")

# ── Experiments ────────────────────────────────────────────────────────────────


EXPERIMENTS = [

    {
        "id":         "exp_01_cafe_golden",
        "setting":    "Cafe window seat, golden hour",
        "motion":     "Camera face-down on table → flipped and lifted, frame spins",
        "expression": "Slow jaw drop, looks out window, back at lens",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA ITSELF IS THE PHONE BEING PICKED UP.
There is no other phone. This camera IS the phone. When the person picks up the phone, THE FRAME MOVES.

The video begins with the camera face-down on a wooden cafe table. We see only darkness.

Setting: golden hour cafe. Warm late afternoon light from a large window. Low background murmur.
Iced coffee and open laptop on the table beside us.

0-0.5s: Darkness. Camera is face-down.

0.5-1.5s: A hand reaches under the camera and FLIPS IT face-up — the frame SPINS 180 degrees fast,
a flash of ceiling, then SWINGS and JOLTS upward as she lifts us off the table.
Frame shakes from the grab. Autofocus frantically pulses. We are now facing her.
She is in her early 20s. Casual. Golden light on her face. She holds us loosely —
the frame drifts slightly in her grip.

1.5-4s: She looks down at this camera screen (slightly downward toward the lens).
Reads something. Her eyes go still. Slowly looks out the window — processing.
Golden light catches her face in profile.

4-7s: She looks back DIRECTLY INTO THIS LENS. Jaw slowly drops.
Blinks. Looks at screen. Headshake. Hand rises to her cheek.

7-8s: She exhales quietly. Eyes wide on the screen. Frame sways in her loose grip.
Warm golden light. Real.

Audio: cafe murmur, distant espresso machine, her quiet exhale.""",
    },

    {
        "id":         "exp_02_car_afternoon",
        "setting":    "Car parked, afternoon sun",
        "motion":     "Camera in cupholder → snatched, frame tilts hard sideways",
        "expression": "Leans back into headrest, hand covers mouth",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS THE PHONE SITTING IN THE CUPHOLDER. When grabbed, THE FRAME PHYSICALLY MOVES.
No other phone exists. The camera IS the phone.

The video begins with the camera in a car's center cupholder, screen facing up.
We see the car ceiling, windshield edge, afternoon light.

Setting: parked car, afternoon sun slanting through windshield, slightly overexposed.
Driver in their early 20s, seatbelt still on, just arrived.

0-1s: Camera sits in cupholder. A hand reaches in from the left.
Fingers grip around the camera — the frame LURCHES AND TILTS HARD sideways as it is lifted out.
Frame swings and settles facing the driver. Afternoon sun cuts across their face.
Autofocus hunts and locks.

1-4s: They look down at this camera's screen. Start reading. Expression shifts. They re-read.

4-6.5s: Hand slowly rises to cover their mouth.
They lean their head back against the headrest. Eyes on screen, then up to THIS LENS directly.
Afternoon sun rim-lights their hair from the windshield.

6.5-8s: Slow exhale. Eyes close for one beat. Open again. Still staring at this lens.
The face of someone who needed to find this.

Audio: car interior — faint AC hum, distant traffic, their slow exhale.""",
    },

    {
        "id":         "exp_03_bathroom_mirror",
        "setting":    "Bathroom sink, morning, mirror behind",
        "motion":     "Camera propped on sink → picked up mid-toothbrush, frame lurches up",
        "expression": "Freezes mid-brush, pulls toothbrush out, stares into lens",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS THE PHONE PROPPED ON THE BATHROOM SINK.
When picked up, THE FRAME PHYSICALLY LIFTS AND MOVES. No other phone.

The video begins with the camera propped on the edge of the bathroom sink, tilted slightly upward.
We see the bathroom mirror, morning light, a person brushing their teeth.

Setting: bathroom morning. Warm overhead light and natural window light. Mirror behind the person.

0-2s: They brush their teeth, barely noticing the camera. They glance at the screen.
Keep brushing. Glance again. Stop.

2-4s: Completely still mid-brush. Eyes locked on this camera's screen.
Toothbrush still in mouth. Slowly — they pull it out. Never look away from the screen.

4s: They reach down and PICK UP THIS CAMERA from the sink edge —
THE FRAME LURCHES UPWARD FAST, tilts, autofocus adjusts. Now held up close to their face.

4-7s: They stare directly INTO THIS LENS. Mouth slightly open. Eyes wide. Not styled.
Morning face — unguarded. Mirror still visible behind them showing the back of their head.

7-8s: Slow exhale through the nose. Head shake. Back to the screen, then to the lens.

Audio: bathroom — faint drip, morning quiet, toothbrush sound stopping, exhale.""",
    },

    {
        "id":         "exp_04_bed_morning_sun",
        "setting":    "Bed, soft morning sunlight through curtains",
        "motion":     "Camera face-up on bed → arm from under duvet grabs it, frame goes dark then emerges",
        "expression": "Groggy → reading → bolts upright fast, frame jolts",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS LYING FACE-UP ON THE BED. The arm that grabs it picks up THIS CAMERA.
THE FRAME PHYSICALLY MOVES. No other phone.

The video begins with the camera lying face-up on a bed. We see the ceiling.
Soft morning light through curtain gaps. Duvet edge. Pillow. Total morning calm.

Setting: morning bedroom, warm golden light filtering through curtains.

0-2s: A bare arm slowly emerges from under the duvet.
Fingers find the camera and grip it — THE FRAME LURCHES AND TILTS WILDLY as it is dragged
under the duvet — a beat of warm fabric darkness — then pulled back out into morning light.
We settle facing a face barely awake. Eyes half-open. Morning hair everywhere.

2-4s: They look down at this camera's screen. Slow blink. Reading slowly. Not registering.
They re-read. Eyes open slightly more.

4-7s: Eyes SNAP open. They sit up in bed fast —
THE FRAME JOLTS UPWARD with the sudden movement, shaking.
They hold this camera at arm's length, staring at the screen.
Then directly INTO THIS LENS. Mouth opens. Silently: "wait."

7-8s: They slowly lower back onto the pillow, holding the camera above their face.
We look down at them. Morning light. Pure disbelief.

Audio: morning birds, duvet rustle, their sharp inhale.""",
    },

    {
        "id":         "exp_05_kitchen_coffee",
        "setting":    "Kitchen counter, morning, coffee mug in hand",
        "motion":     "Camera face-down on counter → flipped one-handed, frame spins to ceiling then face",
        "expression": "Coffee mug freezes mid-air, almost drops it, grabs counter edge",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS LYING FACE-DOWN ON THE KITCHEN COUNTER. When flipped, THE FRAME SPINS.
No other phone. This camera IS the phone.

The video begins in total darkness — camera is face-down on the counter.

Setting: kitchen morning. Cool overhead light, warm window light. Lived-in kitchen.
Plant on windowsill. Coffee mug. Real.

0s: Complete darkness.

0.5-1.5s: A hand reaches in and FLIPS the camera face-up in one fast motion —
THE FRAME SPINS 180 DEGREES — a flash of ceiling — then settles hard, facing up.
Frame shakes from the impact. Autofocus pulses. A face looks down at us.
They are in their early 20s, morning clothes, coffee mug in their other hand.

1.5-4s: They look down at this camera's screen. Still sleepy. Reading. Eyes wake up fast.
The coffee mug in their other hand slowly lowers as they read.

4-6s: Mug nearly tips — they catch it. Set it down hard — clunk.
Free hand grabs the counter edge. They lean down close to this camera's screen.
Face gets close to the lens — eyes wide open now.

6-8s: They pick up this camera from the counter — THE FRAME RISES to face level.
Staring directly INTO THIS LENS. Morning window light behind them.
This was not what they expected at this hour.

Audio: fridge hum, birds, the mug clunk, sharp inhale.""",
    },

    {
        "id":         "exp_06_balcony_wind",
        "setting":    "Balcony railing, outdoor daylight, wind",
        "motion":     "Camera on railing buzzes → snatched fast, frame swings wildly through air",
        "expression": "Wind in hair, hand covers mouth, looks away then into lens",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS SITTING ON A BALCONY RAILING. When grabbed, THE FRAME SWINGS THROUGH THE AIR.
No other phone. This camera IS the phone.

The video begins with the camera on the flat top of a balcony railing, screen facing up.
We see open sky, rooftops, and the railing edge. A person is leaning on the railing beside us.

Setting: balcony, bright natural daylight, slight wind. City or neighbourhood behind.

0-1s: THE CAMERA VIBRATES — the whole frame shudders from a notification.
The person's hand SNATCHES the camera off the railing —
THE FRAME SWINGS WILDLY THROUGH THE AIR — spinning, tilting — before stabilizing facing them.
They are in their early 20s. Wind already moving their hair. Outdoor light — honest, no filter.

1-4s: They look at this camera's screen. Squinting slightly from the light.
Wind moves hair across their face — they push it away impatiently. Expression shifts fast.

4-6.5s: Free hand rises slowly to cover their mouth. Eyes wide.
They look away — over the balcony into the distance. Needing a moment.
Then back at this lens. Wind still in their hair.

6.5-8s: Directly INTO THIS LENS. Slow headshake. Sky and rooftops behind them.
Completely real. No flattery.

Audio: wind, distant city sounds, birds, muffled exhale through their hand.""",
    },

    {
        "id":         "exp_07_reading_chair",
        "setting":    "Armchair, warm lamp, evening",
        "motion":     "Camera face-down on armrest → grabbed with both hands, frame rises slowly",
        "expression": "Book slides off lap unnoticed, mouth opens in slow O, sinks into chair",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS LYING FACE-DOWN ON THE ARMREST. When picked up, THE FRAME RISES.
No other phone. This camera IS the phone.

The video begins in darkness — camera face-down on a chair armrest. Just fabric warmth.

Setting: cozy armchair, warm amber lamp light, evening. Book open in their lap. Mug on side table.

0-1s: Darkness. Then a hand lifts the camera off the armrest —
THE FRAME TILTS AND RISES — a flash of ceiling — settles facing them.
They are in their early 20s, legs tucked into the chair, book in their other hand.
Warm amber lamp light on their face. Relaxed evening.

1-3s: They glance at this camera's screen. Back to book. Back to screen.
Both hands on the camera now. Book slides slowly off their lap to the floor. They don't notice.

3-6s: Reading. Expression going from curious to wide-eyed.
Mouth forms a slow silent O — involuntary.
They look DIRECTLY INTO THIS LENS. Back to screen. Back to lens.
Frame sways gently in their grip. Warm amber light.

6-8s: Very slow exhale. They sink back into the chair, holding this camera up.
The book on the floor. The mug cooling. Eyes on this lens.
Something just changed.

Audio: lamp hum, the book hitting the floor, deep quiet, their slow exhale.""",
    },

    {
        "id":         "exp_08_walking_stops",
        "setting":    "Sidewalk, walking, mid-stride",
        "motion":     "Camera already in hand while walking, full walking bounce → sudden dead stop",
        "expression": "Mouth drops mid-walk, backs to wall, slides slightly down it",
        "prompt": """\
THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. 9:16 vertical.
THE CAMERA IS ALREADY IN THEIR HAND AS THEY WALK. THE FRAME BOUNCES WITH EVERY STEP.
This is the camera moving. No other phone. This camera IS the phone being carried.

The video begins with the camera already in their hand — being carried as they walk.
THE FRAME BOUNCES RHYTHMICALLY with each step. Natural gait motion. Real walking footage.
We see their face intermittently as they glance down at this lens while walking.

Setting: sidewalk, mid-morning, slightly overcast. Headphones around neck. Casual pace.

0-2s: Frame bouncing with their steps — up, down, slight sway. Real walking motion.
They glance at this camera's screen between looking ahead.
Then they look at the screen properly. Walking pace slows. The bounce changes.

2-3.5s: They stop. Mid-stride. One foot still slightly raised.
THE FRAME STABILIZES — the sudden stillness after the motion is dramatic.
They stand frozen on the pavement. Background continues moving behind them.

3.5-6s: They step slowly backward two steps. Their back meets a wall.
They lean against it. This camera held still against their chest, screen facing them.
Expression: shut down. Processing. Fixed on this screen.

6-8s: They look UP from the screen — DIRECTLY INTO THIS LENS.
One arm drops to their side. This camera close to their face with the other hand.
Someone walks past behind them. They don't register it.

Audio: footsteps stopping, street ambient, distant voices, breath catching.""",
    },

]

# ── Main ───────────────────────────────────────────────────────────────────────

def run_experiment(exp: dict) -> None:
    print(f"\n{'='*60}")
    print(f"Exp: {exp['id']}")
    print(f"Setting: {exp['setting']}")
    print(f"Motion:  {exp['motion']}")
    print(f"{'='*60}")

    out_path = OUT_DIR / f"{exp['id']}.mp4"

    video_id = submit_sora(exp["prompt"], seconds=8)
    poll_sora(video_id)
    download_sora(video_id, out_path)
    send_to_slack(out_path, exp)
    print(f"✓ {exp['id']} → {out_path}")


if __name__ == "__main__":
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: source ~/.env_azure first")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--exps", nargs="+", type=int, help="Experiment numbers 1-based")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        selected = EXPERIMENTS
    elif args.exps:
        selected = [EXPERIMENTS[i - 1] for i in args.exps]
    else:
        selected = EXPERIMENTS[:3]  # default: first 3

    print(f"\nRunning {len(selected)} experiment(s): {[e['id'] for e in selected]}")
    print(f"Output: {OUT_DIR}\n")

    for exp in selected:
        try:
            run_experiment(exp)
        except Exception as e:
            print(f"\n[ERROR] {exp['id']}: {e}")
            continue

    print("\n✓ All done.")
