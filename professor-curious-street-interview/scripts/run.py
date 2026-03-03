#!/usr/bin/env python3
"""
Professor Curious — Street Interview Ad Generator
Generates raw-footage-style school street interview clips via Azure Sora API.
Clips: establishing shot + N kid interviews + outro → stitched final video.

Time-of-day modes: golden_hour (post-exam) | night (coaching exit) | early_morning (exam day arrival)
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}

SKILL_DIR    = Path(__file__).parent.parent
DIALOGUE_DB  = SKILL_DIR / "references" / "dialogue-bank.yaml"

# ── Time-of-day settings ───────────────────────────────────────────────────────

SETTINGS = {
    "golden_hour": """
Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon natural daylight,
warm golden-hour light, slightly hazy. Outside a busy Indian school iron gate. Dozens
of Indian school kids in white shirts and grey pants or skirts with heavy backpacks
streaming out through the gate after exams — visibly happy, relieved, noisy.
Parents waiting outside, yellow auto-rickshaws and bikes parked on the street,
a chai stall visible in the far background. Organic, slightly chaotic Indian street
energy. Absolutely no color grading, no cinematic lighting, no stabilization —
raw iPhone-style handheld footage with natural subtle shake and slight exposure
variation. Feels like one continuous real shoot, not staged.
""".strip(),

    "night": """
Raw handheld smartphone vlog footage, 9:16 vertical. Night time, approximately 8 PM.
Outside a busy Indian coaching institute building under warm orange street lights.
Indian school kids in uniforms and casual clothes emerging after an evening coaching
batch — tired, chatty, bags heavy. Lit chai stall at the corner, motorbikes and
scooters parked along the road, neon shop signs and headlights in the background.
Natural grain in low light, slight handheld shake — no artificial lighting, no
stabilization. Real street night energy, completely authentic, not staged.
""".strip(),

    "early_morning": """
Raw handheld smartphone vlog footage, 9:16 vertical. Early morning, approximately
6:30 AM. Pale golden-pink dawn sky, light mist in the air. Outside an Indian school
iron gate on exam day. Kids in crisp white uniforms arriving with heavy backpacks —
some looking nervous, some revising from notebooks at the gate. Parents on scooters
and bikes dropping off children. A chai stall just opening, steam rising from cups.
Cool blue-gold morning light, no stabilization, natural iPhone-style shake and
slight exposure variation. Feels like the start of a high-stakes exam morning —
quiet focused energy, not staged.
""".strip(),
}

# Per-time establishing + outro lines (used when not reading from YAML)
TIME_SCRIPTS = {
    "golden_hour": {
        "establishing_vlogger": "Bhai, aaj exams khatam hue hain — chalo seedha bacchon se poochte hain, kaisi rahi taiyari!",
        "establishing_action": (
            "Vlogger walks energetically toward the school gate in selfie-cam mode, "
            "points at the crowd of kids pouring out behind him, grins wide at camera, "
            "eyebrows raised, excited and spontaneous."
        ),
        "outro_vlogger": "Sunaa bhai? Ye bacche Professor Curious ki baat kar rahe hain — koi bhi nahi chod raha! Link neeche diya hai, dekh lo khud.",
        "outro_action": (
            "Vlogger switches to selfie-cam and walks away from the school gate, "
            "kids still streaming out in the background. He looks directly into camera, "
            "raises eyebrows knowingly, gives a relaxed thumbs up, slight grin."
        ),
    },
    "night": {
        "establishing_vlogger": "Bhai, coaching khatam hua abhi — raat ke 8 baj rahe hain, bacchon se poochte hain kya chal raha hai taiyari mein!",
        "establishing_action": (
            "Vlogger walks toward the coaching institute gate in selfie-cam mode under orange "
            "street lights at night, gestures at kids streaming out with heavy bags, grinning "
            "at camera, energy still high despite the late hour. Chai stall glowing behind him."
        ),
        "outro_vlogger": "Raat ko bhi yahi kar rahe hain — Professor Curious. Neend ke pehle ek baar zaroor dekho, link neeche hai.",
        "outro_action": (
            "Vlogger turns to selfie-cam under the street light, coaching building lit up behind him, "
            "kids dispersing in the background. Relaxed knowing smile, thumbs up into camera. "
            "Real night street energy — orange glow, neon signs, motorbikes."
        ),
    },
    "early_morning": {
        "establishing_vlogger": "Bhai, aaj exam hai — subah subah school gate pe aa gaya main. Dekho bacchon ka kya haal hai!",
        "establishing_action": (
            "Vlogger walks toward the school gate in selfie-cam mode in early morning dawn light, "
            "points at kids arriving with heavy bags and nervous faces, grins at camera with raised "
            "eyebrows, excited morning energy. Mist visible, pale pink sky behind the school building."
        ),
        "outro_vlogger": "Exam day ki subah — aur sab ek hi app ki baat kar rahe hain. Professor Curious. Download karo, link neeche hai.",
        "outro_action": (
            "Vlogger switches to selfie-cam in the pale dawn light, school gate and arriving kids "
            "in background. Looks directly into camera with a knowing confident smile, gives thumbs up. "
            "Morning mist, cool light, chai stall steam visible in the background."
        ),
    },
}

# Vlogger appearance locked identically across all clips and all time modes
VLOGGER_LOCK = """
CONTINUITY — SAME PERSON IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Wearing a navy blue
round-neck t-shirt, dark jeans. Holds a small black handheld reporter mic with
a round black foam ball top firmly in his right hand. Positioned on the left
edge of frame, visible from chest up, shot from a slightly low angle.
""".strip()


# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(visual_action: str, setting: str, vlogger_line: str) -> str:
    return f"""{SETTINGS[setting]}

{VLOGGER_LOCK}

Scene: {visual_action}
The vlogger is speaking in Hindi directly to camera: "{vlogger_line}"
Mouth moving expressively. Camera bobs slightly as he walks.
Start of a street vlog interview segment — energetic, spontaneous, unscripted feel.
"""


def build_kid_prompt(kid: dict, setting: str) -> str:
    gender_word  = "boy" if kid["gender"] == "boy" else "girl"
    age          = kid["age_range"]
    visual       = kid["visual_action"].strip()
    question_hi  = kid["vlogger_question_hindi"].strip()
    response_hi  = kid["kid_response_hindi"].strip()

    return f"""{SETTINGS[setting]}

{VLOGGER_LOCK}

Scene: Vlogger holds mic toward an Indian school {gender_word}, age {age},
wearing a white school shirt and grey pants/skirt, heavy backpack on.

Vlogger asks in Hindi: "{question_hi}"

Kid responds in Hindi: "{response_hi}"

Visual action: {visual}

The kid is speaking animatedly in Hindi — mouth moving, natural Indian hand gestures,
expressive face. The conversation feels genuine and unscripted. Other uniformed kids
walk past in the background, a few glance at the camera. Candid street interview energy.
This is the same continuous shoot as the previous clip — same location, same light,
same vlogger outfit.
"""


def build_outro_prompt(visual_action: str, line_hindi: str, setting: str) -> str:
    return f"""{SETTINGS[setting]}

{VLOGGER_LOCK}

Scene: {visual_action}
Vlogger speaks in Hindi to camera: "{line_hindi}"
Mouth moving, eyebrows raised, knowing smile, thumbs up.
Natural motion blur from walking. End of street interview —
same continuous shoot, same vlogger, same location, same time of day.
"""


# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_job(prompt: str, clip_id: str, seconds: int = 8, max_retries: int = 5) -> str:
    print(f"  [submit] {clip_id} ({seconds}s) ...", flush=True)
    for attempt in range(1, max_retries + 1):
        resp = requests.post(
            f"{BASE_URL}/videos",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={
                "model":   MODEL,
                "prompt":  prompt,
                "size":    "720x1280",
                "seconds": str(seconds),
            },
        )
        if resp.status_code == 429:
            wait = 30 * attempt
            print(f"  [submit] {clip_id} → 429 too many tasks, waiting {wait}s (attempt {attempt}/{max_retries})", flush=True)
            time.sleep(wait)
            continue
        if not resp.ok:
            raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
        job = resp.json()
        if job.get("error"):
            raise RuntimeError(f"API error: {job['error']}")
        video_id = job["id"]
        print(f"  [submit] {clip_id} → video_id={video_id}", flush=True)
        return video_id
    raise RuntimeError(f"Submit failed after {max_retries} retries (persistent 429)")


def poll_job(video_id: str, clip_id: str, poll_interval: int = 15) -> str:
    print(f"  [poll]   {clip_id} id={video_id} ...", flush=True)
    while True:
        time.sleep(poll_interval)
        r = requests.get(
            f"{BASE_URL}/videos/{video_id}",
            headers=HEADERS,
        )
        if not r.ok:
            raise RuntimeError(f"Poll failed [{r.status_code}]: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll]   {clip_id} status={status} {progress}%", flush=True)
        if status == "completed":
            return video_id
        if status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:400]}")


def download_video(video_id: str, out_path: Path) -> None:
    dl = requests.get(
        f"{BASE_URL}/videos/{video_id}/content",
        headers=HEADERS,
    )
    if not dl.ok:
        raise RuntimeError(f"Download failed [{dl.status_code}]: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save]   {out_path.name} ({len(dl.content) // 1024} KB)", flush=True)


def generate_clip(prompt: str, clip_id: str, out_path: Path, seconds: int = 8) -> Path:
    video_id = submit_job(prompt, clip_id, seconds)
    video_id = poll_job(video_id, clip_id)
    download_video(video_id, out_path)
    return out_path


# ── Stitch ─────────────────────────────────────────────────────────────────────

def stitch_clips(clip_paths: list[Path], output_path: Path) -> None:
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    list_file.unlink(missing_ok=True)
    print(f"  [stitch] → {output_path.name}", flush=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Professor Curious street interview ad generator")
    parser.add_argument("--run-id",     default="run_001",           help="Unique run identifier")
    parser.add_argument("--num-kids",   type=int, default=3,         help="Number of kid interview clips (1–8)")
    parser.add_argument("--kid-ids",    nargs="*",                   help="Specific kid IDs from dialogue bank (optional)")
    parser.add_argument("--seconds",    type=int, default=8,         help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",                  help="Override output directory")
    parser.add_argument("--no-stitch",  action="store_true",         help="Skip final stitching step")
    parser.add_argument("--grade",      choices=["10", "12"],        help="Board grade — uses dialogue-bank-10th.yaml or dialogue-bank-12th.yaml")
    parser.add_argument("--time",       default="golden_hour",
                        choices=["golden_hour", "night", "early_morning"],
                        help="Time of day for the shoot (default: golden_hour)")
    parser.add_argument("--hook",          default="default",
                        help="Hook variant from dialogue bank hook_variants section (default: uses establishing_shot + outro from YAML)")
    parser.add_argument("--intro-seconds", type=int, default=4,
                        help="Seconds for establishing + outro clips (default: 4 — keeps focus on kids)")
    args = parser.parse_args()

    # Validate
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

    num_kids = max(1, args.num_kids)
    tod      = args.time
    ts       = TIME_SCRIPTS[tod]
    hook     = args.hook

    # Output directory
    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / \
                  "professor-curious-street-interview" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    # Load dialogue bank (grade-specific or default)
    if args.grade:
        db_path = SKILL_DIR / "references" / f"dialogue-bank-{args.grade}th.yaml"
    else:
        db_path = DIALOGUE_DB
    db = yaml.safe_load(db_path.read_text())
    all_kids = db["kids"]

    if args.kid_ids:
        kids = [k for k in all_kids if k["id"] in args.kid_ids]
        if not kids:
            sys.exit(f"ERROR: None of the specified kid IDs found: {args.kid_ids}")
    else:
        kids = random.sample(all_kids, min(num_kids, len(all_kids)))

    kids = kids[:num_kids]

    intro_secs = args.intro_seconds

    print(f"\n=== Professor Curious Street Interview ===")
    print(f"Run ID    : {args.run_id}")
    print(f"Time mode : {tod}")
    print(f"Hook      : {hook}")
    print(f"Intro/outro: {intro_secs}s | Kids: {args.seconds}s")
    total_secs = intro_secs * 2 + args.seconds * len(kids)
    print(f"Clips     : establishing + {len(kids)} kids + outro = {len(kids) + 2} total")
    print(f"Duration  : {intro_secs}s intro/outro + {args.seconds}s x {len(kids)} kids → ~{total_secs}s total")
    print(f"Output    : {out_dir}")
    print()

    manifest = {
        "run_id":    args.run_id,
        "time_mode": tod,
        "hook":      hook,
        "model":     MODEL,
        "endpoint":  ENDPOINT,
        "clips":     [],
    }

    clip_paths = []

    # ── Clip 1: Establishing shot ──────────────────────────────────────────────
    print("[1/{}] Establishing shot ({} / hook={})".format(len(kids) + 2, tod, hook))
    clip_id  = "establishing"
    out_path = clips_dir / f"clip_01_{clip_id}.mp4"
    # Hook variant overrides establishing/outro; TIME_SCRIPTS override YAML for non-golden_hour
    hook_data = db.get("hook_variants", {}).get(hook)
    if hook_data:
        e_action  = hook_data["establishing"]["visual_action"]
        e_vlogger = hook_data["establishing"]["vlogger_line_hindi"]
    elif tod == "golden_hour" and "establishing_shot" in db:
        e_action  = db["establishing_shot"]["visual_action"]
        e_vlogger = db["establishing_shot"]["vlogger_line_hindi"]
    else:
        e_action  = ts["establishing_action"]
        e_vlogger = ts["establishing_vlogger"]
    prompt = build_establishing_prompt(e_action, tod, e_vlogger)
    generate_clip(prompt, clip_id, out_path, intro_secs)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": clip_id, "file": out_path.name, "seconds": intro_secs})

    # ── Kid clips ─────────────────────────────────────────────────────────────
    for i, kid in enumerate(kids, start=2):
        label = f"[{i}/{len(kids) + 2}] Kid: {kid['id']} ({kid['emotion']})"
        print(label)
        clip_id  = kid["id"]
        out_path = clips_dir / f"clip_{i:02d}_{clip_id}.mp4"
        prompt   = build_kid_prompt(kid, tod)
        generate_clip(prompt, clip_id, out_path, args.seconds)
        clip_paths.append(out_path)
        manifest["clips"].append({"clip": clip_id, "kid": kid, "file": out_path.name, "seconds": args.seconds})

    # ── Outro ─────────────────────────────────────────────────────────────────
    outro_idx = len(kids) + 2
    print(f"[{outro_idx}/{outro_idx}] Outro ({tod} / hook={hook})")
    clip_id  = "outro"
    out_path = clips_dir / f"clip_{outro_idx:02d}_{clip_id}.mp4"
    if hook_data:
        o_action  = hook_data["outro"]["visual_action"]
        o_vlogger = hook_data["outro"]["vlogger_line_hindi"]
    elif tod == "golden_hour" and "outro" in db:
        o_action  = db["outro"]["visual_action"]
        o_vlogger = db["outro"]["vlogger_line_hindi"]
    else:
        o_action  = ts["outro_action"]
        o_vlogger = ts["outro_vlogger"]
    prompt = build_outro_prompt(o_action, o_vlogger, tod)
    generate_clip(prompt, clip_id, out_path, intro_secs)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": clip_id, "file": out_path.name, "seconds": intro_secs})

    # ── Stitch ────────────────────────────────────────────────────────────────
    merged_path = out_dir / f"{args.run_id}_merged.mp4"
    if not args.no_stitch:
        print("\n[stitch] Merging all clips...")
        stitch_clips(clip_paths, merged_path)
        manifest["merged"] = merged_path.name
    else:
        print("\n[stitch] Skipped (--no-stitch).")

    # ── Manifest ──────────────────────────────────────────────────────────────
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"\n[done] Manifest: {manifest_path}")

    if not args.no_stitch:
        print(f"[done] Final video: {merged_path}")

    print("\n=== Complete ===\n")


if __name__ == "__main__":
    main()
