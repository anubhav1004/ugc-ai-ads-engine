#!/usr/bin/env python3
"""
UGC Reaction Ad Generator — Professor Curious
Person on front cam, reacting to discovering the app.
No vlogger. No interview. Just one student, their phone, their face.

Format: 4-clip sequential reaction
  Clip 1 (frustration)  — student stuck, late night, front cam
  Clip 2 (discovery)    — opens Professor Curious, types question
  Clip 3 (reaction)     — face as the explanation appears. jaw drop.
  Clip 4 (direct cam)   — looks at camera, addresses viewer directly

Usage:
  python3 run_reaction.py --product "Professor Curious" --run-id reaction_v1
  python3 run_reaction.py --scene us-college --run-id reaction_us_v1
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

# ── Scene configs ─────────────────────────────────────────────────────────────

SCENES = {

    # ── India: Kota hostel room, JEE aspirant ─────────────────────────────────
    "india-hostel": {
        "character": "Indian boy, 17-18 years old, medium-brown skin, tired face with dark circles, "
                     "wearing a plain white cotton t-shirt. Short slightly messy hair. "
                     "Sitting at a small wooden study desk in a Kota hostel room — "
                     "a single desk lamp on, thick JEE notes and textbooks piled around him, "
                     "a glass of water, an empty chai cup. It's 1am. The room is bare and slightly "
                     "lonely — one motivational poster half-peeling off the wall behind him. "
                     "He holds his phone pointed at himself — front camera, 9:16 vertical, "
                     "slightly low angle like he's propped it against his books.",

        "clips": [
            {
                "id": "frustration",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. Feels like a private moment — not filmed for anyone.

The boy is staring at an open Physics textbook, pen in hand. He tries to write something,
scratches it out. Rubs his eyes with both hands slowly. Leans back in the chair and
exhales a long, defeated breath toward the ceiling. Looks back down at the book —
completely lost. He closes the book, opens it again. Puts his pen down.
His jaw is tight. He's been at this for hours.

NO speaking. Just the face, the silence, the weight of 1am in Kota.
The desk lamp casts a warm, lonely glow on his tired face.
Feels completely real — like someone accidentally left their phone recording.""",
            },
            {
                "id": "discovery",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. Continuous from previous moment.

The boy picks up his phone (the same phone recording him — camera stays on his face).
He opens an app. We see the phone screen reflected faintly in his eyes and on his face
as he types his question into Professor Curious.
He types slowly at first — then faster as he finds the question.
His expression: tired but a flicker of something — hope? desperation?
He hits send/enter and waits.
He looks at the screen. Then his eyes go still — something is appearing.

NO speaking. Just his face watching the screen, changing.""",
            },
            {
                "id": "reaction",
                "seconds": 8,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. THIS IS THE KEY CLIP — the emotional core.

The boy is reading the Professor Curious explanation on his phone.
His face goes through a real, unperformed sequence:
  — First: eyes narrow, concentrating hard
  — Then: eyebrows lift slightly — he's following it
  — Then: a small involuntary breath out — he gets it
  — Then: he reads it again to make sure — nods slowly
  — Then: the faintest smile. Not a big smile. The smile of someone who
    finally understood something they've been fighting for hours.
He mouths "ohhh" silently. Shakes his head slightly — half disbelief, half relief.

NO dialogue. His face says everything. The desk lamp. The quiet hostel room.
This is the most honest 6 seconds in the entire ad.""",
            },
            {
                "id": "direct",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. He sets the phone down propped against the books,
so we see him from slightly further — face and shoulders, desk in frame.

He looks directly at the camera — at the viewer. Speaks in Hindi, quietly,
like he doesn't want to wake his roommate:

"Yaar... Professor Curious. Seriously. Raat ke 1 baj rahe hain —
aur is app ne woh samjhaya jo 3 din se samajh nahi aa raha tha.
Link bio mein hai."

He holds up his phone screen toward the camera — showing the Professor Curious app —
then puts it down. Nods once. Goes back to studying.

Feels like he filmed this for his friends. Not for an ad.""",
            },
        ],
    },

    # ── India: School girl, bedroom, board exam prep ──────────────────────────
    "india-bedroom": {
        "character": "Indian girl, 15-16 years old, medium-brown skin, hair in a loose bun, "
                     "wearing a light blue cotton kurta. Sitting cross-legged on her bed, "
                     "a printed study sheet in her lap, a notebook open beside her. "
                     "Bedroom is a middle-class Indian home — a small study table in background, "
                     "a few trophies on a shelf, posters of the solar system. "
                     "It's evening, warm tubelight. She holds her phone in front of her, "
                     "front camera, 9:16 vertical, like she's about to send a voice note to a friend.",

        "clips": [
            {
                "id": "frustration",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

The girl is looking at her Maths study sheet, mouthing something silently — trying to
remember a formula. She writes it, looks at it, crosses it out.
Taps her pen against her lip, staring at nothing.
Sighs and drops the sheet on the bed.
Picks her phone up — scrolls for a second like she's going to text someone for help.
Then stops. Thinks. Sets the phone down again. Torn.

No speaking. Just her frustrated, tired face in warm tubelight.""",
            },
            {
                "id": "discovery",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

She picks up the phone again — this time opens Professor Curious instead.
Types her Maths question. Holds the phone up to photograph the textbook problem.
Waits. Her eyes on the screen, biting her lower lip slightly.
The screen glows on her face as the explanation starts appearing.
She leans in — closer to the screen — reading.

No speaking. Just her face, the phone glow, the anticipation.""",
            },
            {
                "id": "reaction",
                "seconds": 8,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. THE emotional moment.

She reads the Professor Curious explanation. Her face:
  — Eyebrows furrow first — concentrating
  — Then they slowly rise — she's following the logic
  — Then her mouth opens slightly — "oh wait"
  — She grabs her notebook and starts writing fast — copying the method
  — Pauses — checks the screen again — continues writing
  — She puts the pen down and looks up, eyes bright
  — A small laugh of relief escapes her — she covers her mouth with her hand

She gets it. After days of not getting it, she gets it.
No performing — this is what understanding looks like on a face.""",
            },
            {
                "id": "direct",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

She holds the phone up, looking directly at camera. Speaks in Hindi,
still a little glowing from her realisation:

"Yaar sun — Professor Curious try karo seriously.
Main pichle 2 din se ek concept pe stuck thi —
usne 2 minute mein samjha diya. Bilkul simple.
Link neeche diya hai."

She shows her notebook to the camera — the method she just understood,
the working is clear. Then smiles at camera. Genuinely.

Like she filmed this for her best friend. Warm, real, not an ad.""",
            },
        ],
    },

    # ── US: College student, dorm room, SAT/college prep ─────────────────────
    "us-college": {
        "character": "American girl, 17-18, light skin, hair in a messy ponytail, "
                     "wearing an oversized university hoodie. Sitting at a dorm room desk, "
                     "laptop open showing a practice test, highlighters and Post-its scattered. "
                     "It's late — a string of fairy lights the only warm light. "
                     "AirPods in one ear, pulled half out. Holds phone front-cam, 9:16 vertical, "
                     "propped against her laptop — like she's FaceTiming herself while studying.",

        "clips": [
            {
                "id": "frustration",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

She stares at a practice test question on her laptop. Reads it again.
Types something — deletes it. Pushes her laptop slightly away.
Leans back in the chair, arms crossed, staring at the ceiling fairy lights.
Pulls the AirPod out of her ear.
Looks back at the screen. Still lost.
She picks up her phone — starts to text someone, then stops.

No speaking. Just the face. The fatigue. The 11pm dorm room.""",
            },
            {
                "id": "discovery",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

She opens Professor Curious on her phone. Types her question —
actually photographs the laptop screen with it.
Waits, thumb hovering over the screen.
The explanation starts loading. Her eyes scan it.
She sits forward in the chair — closer to the screen.
Pulls the other AirPod out too. Full attention.

No speaking. The fairy lights, the phone glow, her face changing.""",
            },
            {
                "id": "reaction",
                "seconds": 8,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical. The reaction.

She reads the Professor Curious explanation carefully. Her face:
  — Eyes move left to right, focused — she's reading
  — She stops — rereads one line — nods slowly
  — Picks up her highlighter and highlights something on her paper
  — Puts it down — goes back to the phone — reads one more thing
  — Sits back — a long slow exhale
  — Then she laughs softly to herself — shakes her head
  — Looks almost annoyed at how clear it suddenly is

That specific laugh when something that felt impossible becomes obvious.
Completely real. Unperformed.""",
            },
            {
                "id": "direct",
                "seconds": 4,
                "prompt": """{character}

RAW FRONT-CAM FOOTAGE, 9:16 vertical.

She picks up her phone and looks straight at camera. Speaks in English,
casual and direct, like a TikTok she's sending her study group:

"Okay so — Professor Curious. I've been stuck on this for like two hours.
It just — explained it. Like actually explained it.
If you're studying for SAT or APs or whatever, link's in my bio.
Genuinely."

She turns the phone to show the app screen briefly — Professor Curious open,
the explanation still on screen. Then back to her face.
Small shrug — like it's just obvious.""",
            },
        ],
    },

}

# ── Prompt builder ─────────────────────────────────────────────────────────────

def build_prompt(clip: dict, character: str) -> str:
    return clip["prompt"].format(character=character)

# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_job(prompt: str, clip_id: str, seconds: int) -> str:
    print(f"  [submit] {clip_id} ({seconds}s) ...", flush=True)
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
    print(f"  [submit] {clip_id} → {video_id}", flush=True)
    return video_id

def poll_job(video_id: str, clip_id: str) -> str:
    print(f"  [poll]   {clip_id} ...", flush=True)
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed [{r.status_code}]: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll]   {clip_id} {status} {progress}%", flush=True)
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

def generate_clip(prompt: str, clip_id: str, out_path: Path, seconds: int) -> None:
    video_id = submit_job(prompt, clip_id, seconds)
    video_id = poll_job(video_id, clip_id)
    download_video(video_id, out_path)

# ── Stitch ─────────────────────────────────────────────────────────────────────

def stitch_clips(clip_paths: list, output_path: Path) -> None:
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
         str(output_path)],
        capture_output=True, text=True,
    )
    list_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    print(f"  [stitch] → {output_path.name}", flush=True)

def send_to_slack(video_path: Path, label: str) -> None:
    print(f"[slack] Sending: {label}")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", f"text=*[REACTION]* {label}",
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {result.stdout.strip() or result.stderr.strip()}")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UGC Reaction Ad Generator")
    parser.add_argument("--product",     default="Professor Curious",   help="App name")
    parser.add_argument("--scene",       default="india-hostel",
                        choices=list(SCENES),
                        help="Scene (default: india-hostel)")
    parser.add_argument("--run-id",      default="reaction_v1",         help="Unique run ID")
    parser.add_argument("--output-dir",  default="",                    help="Override output dir")
    parser.add_argument("--no-stitch",   action="store_true",           help="Skip merge")
    parser.add_argument("--send-slack",  action="store_true",           help="Auto-send to Slack")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    scene = SCENES[args.scene]

    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-reaction" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    clips    = scene["clips"]
    char     = scene["character"]
    total    = len(clips)

    print(f"\n=== UGC Reaction Ad ===")
    print(f"Product  : {args.product}")
    print(f"Scene    : {args.scene}")
    print(f"Run ID   : {args.run_id}")
    print(f"Clips    : {total} (frustration → discovery → reaction → direct)")
    total_secs = sum(c["seconds"] for c in clips)
    print(f"Duration : ~{total_secs}s")
    print(f"Output   : {out_dir}\n")

    manifest   = {"run_id": args.run_id, "scene": args.scene, "clips": []}
    clip_paths = []

    for i, clip in enumerate(clips, start=1):
        print(f"[{i}/{total}] {clip['id']}")
        out_path = clips_dir / f"clip_{i:02d}_{clip['id']}.mp4"
        prompt   = build_prompt(clip, char)
        generate_clip(prompt, clip["id"], out_path, clip["seconds"])
        clip_paths.append(out_path)
        manifest["clips"].append({"clip": clip["id"], "file": out_path.name})

    merged_path = out_dir / f"{args.run_id}_merged.mp4"
    if not args.no_stitch:
        print("\n[stitch] Merging clips...")
        stitch_clips(clip_paths, merged_path)
        manifest["merged"] = merged_path.name
    else:
        print("\n[stitch] Skipped.")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n[done] {merged_path}")
    print("=== Complete ===\n")

    if args.send_slack:
        label = f"{args.run_id} | {args.scene} | ~{total_secs}s reaction ad"
        send_to_slack(merged_path, label)

if __name__ == "__main__":
    main()
