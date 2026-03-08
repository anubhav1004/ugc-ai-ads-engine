#!/usr/bin/env python3
"""
10 US Reaction Hook Clips — Professor Curious
Each clip is a standalone 12s reaction hook, front-cam, single character.
App demo will be composited on top later.
Auto-sends each to Slack as it completes.

Usage:
  python3 run_hooks_us.py
  python3 run_hooks_us.py --hooks 1 3 7   # run specific hooks only
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AJSBJU1LK"   # experimental — change to C0AHDH474LX for approved finals

OUTPUT_BASE = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-reaction-hooks-us"

# ── Hook definitions ───────────────────────────────────────────────────────────

HOOKS = [

    {
        "id": "hook_01_jaw_drop",
        "title": "The Jaw Drop",
        "character": "American girl, 18-19, light skin, blonde hair in a messy bun, oversized grey college hoodie. Sitting at a dorm room desk under a warm desk lamp. Textbook open. Holds phone front-cam, 9:16 vertical, propped against books. Late night, fairy lights in background.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Feels completely real — like a TikTok draft.

The girl is reading her textbook, frustrated. She picks up her phone and opens an app.
Reads the screen. Her face goes completely still — processing.
Then: jaw slowly drops. Eyes go wide. She looks up from the phone directly at the camera.
Mouth open, no words come out. She looks back at the phone. Back at the camera.
Holds the phone up slightly toward camera — wanting to show someone.
Shakes her head slowly in disbelief.

The whole clip is silent except for ambient dorm sounds.
TEXT OVERLAY appears at the bottom: "this app just explained in 10 seconds what my teacher couldn't in 3 weeks"

No performance. Pure genuine shock. The face does everything.""",
    },

    {
        "id": "hook_02_double_take",
        "title": "The Double-Take",
        "character": "American boy, 17-18, medium skin, dark curly hair, wearing a plain navy t-shirt. Sitting at a bedroom desk with a laptop open showing a practice test. Casual suburban bedroom — posters on wall, ring light in background. Holds phone front-cam.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Casual, unscripted energy.

The boy glances at his phone while doing homework on his laptop.
Reads something. Looks away — back to laptop.
Then — snaps back to the phone. Classic double-take.
Leans in close, squinting at the screen, pulling the phone toward his face.
Mouth forms: "wait... WAIT."
Eyes go wide. He tilts the phone slightly as if to confirm he's reading it right.
Looks directly at camera, points at the phone with one finger.
The expression: that specific face when something is too good to be real.

Completely natural. No scripted words — just the physical double-take reaction.
TEXT OVERLAY: "me realizing this app just solved the problem I've been stuck on for 3 days" """,
    },

    {
        "id": "hook_03_so_mad",
        "title": "I'm So Mad I Didn't Find This Sooner",
        "character": "American girl, 19-20, medium-light skin, straight dark hair, white t-shirt. Sitting on her dorm bed, back against the wall, knees up. Casual and direct. Holds phone front-cam like she's venting to her TikTok.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Direct to camera — no fourth wall.

She looks straight at the lens. Slight frustration on her face. Speaks:

"I spent literally two thousand dollars on SAT prep courses.
And this app — this FREE app — just explained the exact same thing
in like forty-five seconds. I'm actually so mad right now."

She holds up her phone briefly, showing the app screen.
Shakes her head. Half-laughs — the laugh of genuine disbelief.
Points at the phone: "Like WHY did nobody tell me about this."

Delivery is real — not rehearsed. She means every word.
Direct eye contact with camera the whole time. Raw.""",
    },

    {
        "id": "hook_04_comment_reply",
        "title": "Comment Reply Native",
        "character": "American girl, 18-19, light freckled skin, red hair in a ponytail, wearing a Stanford sweatshirt. Sitting at a library table with books spread out. Holds phone front-cam like she's filming a casual TikTok reply.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Completely native TikTok feel.

TEXT OVERLAY at the top of screen: "replying to @user who asked what I actually used for SATs"

She speaks casually, like she's done this a hundred times:

"Okay since everyone keeps asking — it was Professor Curious.
I know everyone says Khan Academy but honestly?
The way this app explains things is just... different.
Like actually different."

She holds the phone up showing the app for a moment.
Pulls it back. Shrugs. Smiles — warm, no-big-deal energy.

"Link is in my bio. That's literally it."

Feels 100% organic. Not an ad. A friend giving a recommendation.""",
    },

    {
        "id": "hook_05_2am_glow",
        "title": "The 2AM Glow",
        "character": "American boy, 17-18, medium brown skin, black hair, wearing a white t-shirt. Lying in bed in a dark dorm room — only the phone screen illuminating his face. 2am. Room completely dark except the phone glow.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Dark room — phone is the only light source.
The face is dramatically lit by the phone screen glow. Intimate. Raw.

He's lying in bed, clearly exhausted, phone above his face.
He opens an app. The screen glow intensifies on his face.
His eyes move slowly as he reads. Then stop. He sits up slightly.
Reads again. Nods slowly — once, twice.
He looks directly at the camera and whispers:

"Okay. This just saved my exam tomorrow."

A long beat. He looks back at the screen. Back at camera.
Exhales slowly. Lies back down — but this time the tension is gone.
He's going to be okay.

The darkness, the glow, the whisper — makes it feel like a secret being shared.""",
    },

    {
        "id": "hook_06_show_friend",
        "title": "Show Your Friend",
        "character": "American boy, 18-19, light skin, blonde hair, wearing a grey zip-up hoodie. Sitting at a shared dorm room desk. Roommate's side of the room visible in background. Holds phone front-cam, slightly wide angle to show the space.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Spontaneous, unplanned energy.

The boy is on his phone. Reads something. Immediate reaction — eyes go wide.
He spins around toward the door/roommate area (offscreen):

"Bro — BRO. Come look at this. No seriously COME LOOK AT THIS."

Turns back to camera — face is half-laughing, half-genuinely amazed.
Holds phone out toward the camera showing the screen briefly.
Pulls it back.

"This app just — okay I've been trying to understand this concept for like a WEEK.
It just explained it. Like fully explained it. In thirty seconds."

Shakes his head. That specific face: equal parts annoyed and amazed.""",
    },

    {
        "id": "hook_07_voiceless",
        "title": "Voiceless Shock",
        "character": "American girl, 16-17, light skin, dark brown hair loose, wearing a pink hoodie. Sitting at a bedroom desk in bright afternoon light. Phone held front-cam. Clean, simple background.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. COMPLETELY SILENT — no dialogue whatsoever.
Only ambient room sounds. The face tells the entire story.

She sits at her desk, neutral expression. Opens her phone.
Reads something on screen.

FACE SEQUENCE — slow, unperformed, real:
  0-3s: neutral, reading
  3-5s: eyebrows slowly rise — she's following something
  5-7s: eyes go wide — she gets it
  7-9s: hand comes up, covers mouth — genuine disbelief
  9-11s: she looks directly at camera — shakes head slowly
  11-12s: the smallest smile appears — the smile of someone who just found the answer

TEXT OVERLAYS (the only words):
  [5s] "POV: you finally understand the thing that's been failing you all year"
  [10s] "Professor Curious 👆"

No words. No voiceover. Pure face. Sound-off-friendly.""",
    },

    {
        "id": "hook_08_score_reveal",
        "title": "The Score Reveal",
        "character": "American boy, 17-18, medium skin, short dark hair, wearing a dark blue t-shirt. Standing in a bedroom, natural window light. Holds a piece of paper in one hand, phone front-cam in the other.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Confident, direct energy.

He holds up a piece of paper toward the camera.
We can clearly read: SAT SCORE — 1540. Or a test paper marked A+.
He lowers it slowly. Looks at camera. Pauses for effect.

"Three weeks ago I was scoring a 1180."

Beat. Lets it land.

"One thing changed."

He picks up his phone. Taps it once. Holds the screen slightly toward camera — Professor Curious app open.
Taps it back down.

"That's it. That's literally the whole video. Link's in the bio."

Understated. Confident. Doesn't need to perform — the score speaks.
Real paper. Real number. No exaggeration energy.""",
    },

    {
        "id": "hook_09_dont_download",
        "title": "Don't Download This",
        "character": "American girl, 19-20, medium skin, natural curly hair, wearing a black crop top. Sitting on a college dorm bed, leaning against the wall. Direct, slightly playful energy. Holds phone front-cam.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Direct eye contact from frame one.

She looks straight at the camera. Serious face. Points directly at the lens:

"Don't download Professor Curious."

Beat. Straight face.

"Seriously — don't. Because once you actually understand how to study,
you're going to be so annoyed that you wasted years being confused
when this existed the whole time."

She pauses. Lets a slow smirk appear.

"You've been warned."

She holds up her phone briefly, app visible. Sets it down. Looks away — done.

The reverse psychology delivery is completely dry and deadpan.
No winking, no breaking character. She means it as a joke but plays it straight.""",
    },

    {
        "id": "hook_10_frustrated_flip",
        "title": "Frustrated to Amazed",
        "character": "American girl, 17-18, light skin, light brown hair, wearing an oversized university sweatshirt. Sitting at a desk with textbooks and notes everywhere. Desk lamp. Late evening. Holds phone front-cam propped against books.",
        "seconds": 12,
        "prompt": """RAW FRONT-CAM FOOTAGE, 9:16 vertical. Clear emotional arc in 12 seconds.

FIRST 3 SECONDS — pure frustration:
Pen thrown down on the desk. She pushes the textbook slightly away.
Rubs her temples. Long slow exhale toward the ceiling. Slumps.

SECONDS 3-7 — discovery:
Picks up phone. Opens app. Types something. Waits.
Leans forward. Reading. Expression shifts — from defeated to focused.

SECONDS 7-10 — the flip:
Eyebrows raise. She grabs the pen back. Starts writing fast.
Stops. Looks at what she wrote. Nods — it makes sense.
Closes the textbook — deliberately, with a small confident push.

SECONDS 10-12 — direct to camera:
Looks straight at the lens.
"Why did no one tell me about this."
Not a question. A statement. The specific face of someone
who just made something hard very, very easy.""",
    },

]

# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_job(prompt: str, hook_id: str, seconds: int) -> str:
    print(f"  [submit] {hook_id} ({seconds}s) ...", flush=True)
    resp = requests.post(
        f"{BASE_URL}/videos",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(seconds)},
    )
    if not resp.ok:
        raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    video_id = job["id"]
    print(f"  [submit] {hook_id} → {video_id}", flush=True)
    return video_id

def poll_job(video_id: str, hook_id: str) -> str:
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed [{r.status_code}]: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll]   {hook_id} {status} {progress}%", flush=True)
        if status == "completed":
            return video_id
        if status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:400]}")

def download_video(video_id: str, out_path: Path) -> None:
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed [{dl.status_code}]: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save]   {out_path.name} ({len(dl.content) // 1024} KB)", flush=True)

def generate_hook(hook: dict, out_path: Path) -> None:
    full_prompt = f"{hook['character']}\n\n{hook['prompt']}"
    video_id = submit_job(full_prompt, hook["id"], hook["seconds"])
    video_id = poll_job(video_id, hook["id"])
    download_video(video_id, out_path)

def send_to_slack(video_path: Path, hook: dict) -> None:
    label = f"Hook {hook['id']} — *{hook['title']}*"
    print(f"[slack] {label}", flush=True)
    result = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", f"text=*[US REACTION HOOK]* {label}\n_{hook['prompt'][:120].strip()}..._",
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    resp = result.stdout.strip() or result.stderr.strip()
    try:
        ok = json.loads(resp).get("ok")
        print(f"  [slack] {'✓ sent' if ok else resp}", flush=True)
    except Exception:
        print(f"  [slack] {resp}", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="US Reaction Hook Generator — 10 hooks")
    parser.add_argument("--hooks", nargs="*", type=int,
                        help="Hook numbers to run e.g. --hooks 1 3 7 (default: all)")
    parser.add_argument("--no-slack", action="store_true", help="Skip Slack sends")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    selected = HOOKS
    if args.hooks:
        selected = [h for h in HOOKS if int(h["id"].split("_")[1]) in args.hooks]

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*55}")
    print(f"  US Reaction Hooks — {len(selected)} clips × 12s")
    print(f"  Output: {OUTPUT_BASE}")
    print(f"{'='*55}\n")

    results = []

    for i, hook in enumerate(selected, 1):
        print(f"\n[{i}/{len(selected)}] {hook['id']} — {hook['title']}")
        out_path = OUTPUT_BASE / f"{hook['id']}.mp4"

        try:
            generate_hook(hook, out_path)
            results.append({"hook": hook["id"], "title": hook["title"], "file": str(out_path), "status": "ok"})
            if not args.no_slack:
                send_to_slack(out_path, hook)
        except Exception as e:
            print(f"  [ERROR] {hook['id']}: {e}", flush=True)
            results.append({"hook": hook["id"], "title": hook["title"], "status": "error", "error": str(e)})

    # Summary
    print(f"\n{'='*55}")
    print(f"  DONE — {sum(1 for r in results if r['status']=='ok')}/{len(selected)} hooks generated")
    for r in results:
        status = "✓" if r["status"] == "ok" else "✗"
        print(f"  {status} {r['hook']} — {r['title']}")
    print(f"{'='*55}\n")

    (OUTPUT_BASE / "results.json").write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
