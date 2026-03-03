#!/usr/bin/env python3
"""
Professor Curious — Street Interview Ad Generator
Generates raw-footage-style school street interview clips via Azure Sora API.
Clips: establishing shot + N kid interviews + outro → stitched final video.
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

# ── Prompt builders ────────────────────────────────────────────────────────────

# Every clip shares these locked elements for visual continuity
SETTING_LOCK = """
Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon natural daylight,
warm golden-hour light, slightly hazy. Outside a busy Indian school iron gate. Dozens
of Indian school kids in white shirts and grey pants or skirts with heavy backpacks
streaming out through the gate after exams — visibly happy, relieved, noisy.
Parents waiting outside, yellow auto-rickshaws and bikes parked on the street,
a chai stall visible in the far background. Organic, slightly chaotic Indian street
energy. Absolutely no color grading, no cinematic lighting, no stabilization —
raw iPhone-style handheld footage with natural subtle shake and slight exposure
variation. Feels like one continuous real shoot, not staged.
""".strip()

# Vlogger appearance locked identically across all clips
VLOGGER_LOCK = """
CONTINUITY — SAME PERSON IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Wearing a navy blue
round-neck t-shirt, dark jeans. Holds a small black handheld reporter mic with
a round black foam ball top firmly in his right hand. Positioned on the left
edge of frame, visible from chest up, shot from a slightly low angle.
""".strip()


def build_establishing_prompt(visual_action: str) -> str:
    return f"""{SETTING_LOCK}

{VLOGGER_LOCK}

Scene: {visual_action}
The vlogger is speaking in Hindi directly to camera, mouth moving expressively.
Camera bobs slightly as he walks. Kids in uniforms visibly pouring out behind him.
Start of a street vlog interview segment — energetic, spontaneous, unscripted feel.
"""


def build_kid_prompt(kid: dict) -> str:
    gender_word  = "boy" if kid["gender"] == "boy" else "girl"
    age          = kid["age_range"]
    visual       = kid["visual_action"].strip()
    question_hi  = kid["vlogger_question_hindi"].strip()
    response_hi  = kid["kid_response_hindi"].strip()

    return f"""{SETTING_LOCK}

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


def build_outro_prompt(visual_action: str, line_hindi: str) -> str:
    return f"""{SETTING_LOCK}

{VLOGGER_LOCK}

Scene: {visual_action}
Vlogger speaks in Hindi to camera: "{line_hindi}"
Mouth moving, eyebrows raised, knowing smile, thumbs up. School gate and streaming
kids visible behind him. Natural motion blur from walking. End of street interview —
same continuous shoot, same vlogger, same location.
"""


# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_job(prompt: str, clip_id: str, seconds: int = 8) -> str:
    print(f"  [submit] {clip_id} ({seconds}s) ...", flush=True)
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
    if not resp.ok:
        raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    video_id = job["id"]
    print(f"  [submit] {clip_id} → video_id={video_id}", flush=True)
    return video_id


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
    parser.add_argument("--run-id",     default="run_001",      help="Unique run identifier")
    parser.add_argument("--num-kids",   type=int, default=3,    help="Number of kid interview clips (1-8)")
    parser.add_argument("--kid-ids",    nargs="*",              help="Specific kid IDs from dialogue bank (optional)")
    parser.add_argument("--seconds",    type=int, default=8,    help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",             help="Override output directory")
    parser.add_argument("--no-stitch",  action="store_true",    help="Skip final stitching step")
    parser.add_argument("--grade",      choices=["10", "12"],   help="Board grade — uses dialogue-bank-10th.yaml or dialogue-bank-12th.yaml")
    args = parser.parse_args()

    # Validate
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

    num_kids = max(1, min(8, args.num_kids))

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

    print(f"\n=== Professor Curious Street Interview ===")
    print(f"Run ID    : {args.run_id}")
    print(f"Clips     : establishing + {len(kids)} kids + outro = {len(kids) + 2} total")
    print(f"Duration  : ~{args.seconds}s per clip → ~{args.seconds * (len(kids) + 2)}s total")
    print(f"Output    : {out_dir}")
    print()

    manifest = {
        "run_id":   args.run_id,
        "model":    MODEL,
        "endpoint": ENDPOINT,
        "clips":    [],
    }

    clip_paths = []

    # ── Clip 1: Establishing shot ──────────────────────────────────────────────
    print("[1/{}] Establishing shot".format(len(kids) + 2))
    clip_id  = "establishing"
    out_path = clips_dir / f"clip_01_{clip_id}.mp4"
    prompt   = build_establishing_prompt(db["establishing_shot"]["visual_action"])
    generate_clip(prompt, clip_id, out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": clip_id, "file": out_path.name, "seconds": args.seconds})

    # ── Kid clips ─────────────────────────────────────────────────────────────
    for i, kid in enumerate(kids, start=2):
        label = f"[{i}/{len(kids) + 2}] Kid: {kid['id']} ({kid['emotion']})"
        print(label)
        clip_id  = kid["id"]
        out_path = clips_dir / f"clip_{i:02d}_{clip_id}.mp4"
        prompt   = build_kid_prompt(kid)
        generate_clip(prompt, clip_id, out_path, args.seconds)
        clip_paths.append(out_path)
        manifest["clips"].append({"clip": clip_id, "kid": kid, "file": out_path.name, "seconds": args.seconds})

    # ── Outro ─────────────────────────────────────────────────────────────────
    outro_idx = len(kids) + 2
    print(f"[{outro_idx}/{outro_idx}] Outro")
    clip_id  = "outro"
    out_path = clips_dir / f"clip_{outro_idx:02d}_{clip_id}.mp4"
    prompt   = build_outro_prompt(db["outro"]["visual_action"], db["outro"]["vlogger_line_hindi"])
    generate_clip(prompt, clip_id, out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": clip_id, "file": out_path.name, "seconds": args.seconds})

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
