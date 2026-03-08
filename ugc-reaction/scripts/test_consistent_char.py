#!/usr/bin/env python3
"""
Test: consistent character via gpt-image-1.5 + Sora input_reference
Step 1: Generate character portrait with gpt-image-1.5
Step 2: Resize to 720x1280 (Sora video size)
Step 3: Submit to Sora with input_reference (multipart)
Step 4: Download + send to Slack
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY      = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT     = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL        = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL     = f"{ENDPOINT}/openai/v1"
HEADERS      = {"api-key": API_KEY}
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "nano-banana-pro-preview"

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AJSBJU1LK"   # experimental — change to C0AHDH474LX for approved finals

OUT_DIR = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-consistent-test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Character definition ───────────────────────────────────────────────────────

CHARACTER_PROMPT = """Photorealistic portrait of a young American woman, 18-19 years old,
light skin with faint freckles, straight auburn hair just past shoulders with a slight wave,
green-hazel eyes, small upturned nose, natural minimal makeup.
Wearing an oversized grey college hoodie. Neutral relaxed expression, slight 3/4 angle.
Upper body visible. Clean light background. Soft natural indoor lighting.
High quality realistic photograph. Vertical 9:16 portrait orientation."""

CHARACTER_DNA = """Young American woman, 18-19, light skin with faint freckles,
straight auburn hair just past shoulders, green-hazel eyes, small upturned nose,
wearing an oversized grey college hoodie."""

# ── Hook prompt ───────────────────────────────────────────────────────────────

HOOK_PROMPT = f"""RAW FRONT-CAM FOOTAGE, 9:16 vertical. College library study room,
afternoon light through windows. Textbook and laptop on desk.

The student ({CHARACTER_DNA}) is studying, looking frustrated at her textbook.
She picks up her phone and opens an app. Reads the screen carefully.
Her expression freezes — processing what she just read.
Then: jaw slowly drops. Eyes go wide. She looks up from phone directly at camera.
Mouth open in silent disbelief. She looks back at phone then back at camera.
Holds the phone up slightly toward camera as if to show someone.
Shakes her head slowly in disbelief.

No performance. Pure genuine shock. Feels completely real — like a TikTok draft.
The face does everything. Silent except ambient library sounds."""

# ── Step 1: Generate character image with gpt-image-1.5 ───────────────────────

def generate_character_image() -> Path:
    import base64
    print(f"\n[1/4] Generating character with {GEMINI_MODEL} ...")
    out_path = OUT_DIR / "character_reference.png"

    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}",
        json={
            "contents": [{"parts": [{"text": CHARACTER_PROMPT}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        },
    )
    if not resp.ok:
        raise RuntimeError(f"Gemini image gen failed [{resp.status_code}]: {resp.text[:500]}")

    data = resp.json()
    parts = data["candidates"][0]["content"]["parts"]
    img_part = next((p for p in parts if "inlineData" in p), None)
    if not img_part:
        raise RuntimeError(f"No image in response: {data}")

    out_path.write_bytes(base64.b64decode(img_part["inlineData"]["data"]))
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── Step 2: Crop face out + resize to 720x1280 ────────────────────────────────

def resize_to_sora(img_path: Path) -> Path:
    print("\n[2/4] Resizing to 720x1280 for Sora ...")
    out_path = OUT_DIR / "character_720x1280.png"
    img = Image.open(img_path).convert("RGB")
    img = img.resize((720, 1280), Image.LANCZOS)
    img.save(str(out_path), "PNG")
    print(f"  [save] {out_path.name} (720x1280)")
    return out_path


# ── Step 3: Submit to Sora with input_reference (multipart) ───────────────────

def submit_sora_with_reference(ref_image: Path) -> str:
    print("\n[3/4] Submitting to Sora with input_reference ...")
    with open(ref_image, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/videos",
            headers=HEADERS,   # NO Content-Type here — requests sets it for multipart
            data={
                "model": MODEL,
                "prompt": HOOK_PROMPT,
                "size": "720x1280",
                "seconds": "8",
            },
            files={
                "input_reference": ("character_720x1280.png", f, "image/png"),
            },
        )

    if not resp.ok:
        raise RuntimeError(f"Sora submit failed [{resp.status_code}]: {resp.text[:600]}")

    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")

    video_id = job["id"]
    print(f"  [submit] → {video_id}")
    return video_id


def poll_and_download(video_id: str) -> Path:
    out_path = OUT_DIR / "consistent_test.mp4"
    print(f"  [poll] waiting for {video_id} ...")
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll] {status} {progress}%", flush=True)
        if status == "completed":
            break
        if status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:400]}")

    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── Step 4: Slack ──────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path) -> None:
    print("\n[4/4] Sending to Slack ...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", "text=*[CONSISTENT CHAR TEST]* hook_01_jaw_drop with gpt-image-1.5 reference\nSame character locked via input_reference — checking face consistency.",
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {result.stdout.strip() or result.stderr.strip()}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: source ~/.env_azure first")
    if not GEMINI_KEY:
        sys.exit("ERROR: GEMINI_API_KEY not set — source ~/.env_azure first")

    try:
        char_img   = generate_character_image()
        resized    = resize_to_sora(char_img)
        video_id   = submit_sora_with_reference(resized)
        video_path = poll_and_download(video_id)
        send_to_slack(video_path)
        print(f"\n✓ Done: {video_path}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
