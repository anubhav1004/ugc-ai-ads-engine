#!/usr/bin/env python3
"""
UGC Reaction Hooks — Gemini Pipeline
Step 1: Generate character portrait with nano-banana-pro (Gemini 3 Pro Image)
Step 2: Generate reaction video with Veo 3 (image-to-video, 9:16)
Step 3: Send to Slack
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────

GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_BASE  = "https://generativelanguage.googleapis.com/v1beta"
IMAGE_MODEL  = "nano-banana-pro-preview"
VIDEO_MODEL  = "veo-3.0-generate-001"

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AJSBJU1LK"   # experimental — change to C0AHDH474LX for approved finals

OUT_DIR = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-veo-hooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Character ─────────────────────────────────────────────────────────────────

CHARACTER_PROMPT = """Photorealistic portrait photograph of a young American woman, 18-19 years old.
Light skin with faint freckles, straight auburn hair just past shoulders with a slight wave,
green-hazel eyes, small upturned nose, natural minimal makeup.
Wearing an oversized grey college hoodie. Neutral relaxed expression, slight 3/4 angle.
Upper body visible. Clean light background. Soft natural indoor lighting.
High quality DSLR-style portrait. Vertical 9:16 orientation."""

CHARACTER_DNA = """young American woman, 18-19, auburn hair just past shoulders,
green-hazel eyes, light skin with faint freckles, grey college hoodie"""

# ── Hooks ─────────────────────────────────────────────────────────────────────

HOOKS = [
    {
        "id": "hook_01_jaw_drop",
        "title": "The Jaw Drop",
        "prompt": f"""Vertical 9:16 selfie-style phone video. She is holding the phone at arm's length — her arm and hand are visible at the bottom of frame. Selfie perspective, chest-up close framing. Natural handheld motion with slight shake and occasional micro-reframing, the kind you get holding a phone for a long time. Slightly grainy, looks filmed on a phone, not cinematic.

{CHARACTER_DNA}. She's sitting at a college library desk, soft afternoon window light. Textbooks open in front of her. She looks frustrated, distracted. She blinks naturally. Slight shifts in posture — not still.

She glances down at something on her phone (a different app — not the camera). Her eyes scan the screen. She blinks. Then she goes completely still — processing what she just read. A beat. Then her jaw slowly drops. Eyes widen. She looks up and directly into the front camera — pure stunned silence. Mouth open. No words. She shakes her head slowly in disbelief, looks back at the screen, then back at the camera. Natural breathing visible. Small involuntary exhale.

Audio: quiet library ambiance — distant page turning, faint HVAC hum. No music. No voiceover. The silence makes the reaction louder.""",
    },
    {
        "id": "hook_02_double_take",
        "title": "The Double Take",
        "prompt": f"""Vertical 9:16 selfie-style phone video. She is holding the phone at arm's length — arm visible at bottom of frame. Selfie perspective, chest-up. Natural handheld shake — slight drift, small reframes as her grip shifts. Slightly grainy phone quality.

{CHARACTER_DNA}. College dorm room, desk lamp warm light, evening. She's writing notes in a notebook, phone propped up recording. She glances at her phone screen casually — then instantly does a sharp double-take. Looks back at her notebook. Looks back at phone. Leans in closer, squinting. Sits back. Blinks several times. Expression goes from confused to shocked — eyebrows up, mouth slightly open. She stares directly into camera for a long beat. Then a slow, disbelieving smile creeps across her face. She shakes her head like she can't believe it.

Natural micro-expressions throughout — slight brow furrows, jaw shifts, swallowing. Not performing. Reacting.

Audio: quiet dorm room — faint music through walls, pen tapping, then silence as she processes.""",
    },
    {
        "id": "hook_03_show_friend",
        "title": "Show the Friend",
        "prompt": f"""Vertical 9:16 selfie-style phone video. She holds the phone at arm's length — arm visible. Handheld, slight natural shake and drift. Phone-camera quality, slightly grainy, compressed like a TikTok draft.

{CHARACTER_DNA}. College common room, overhead fluorescent mixed with natural light from windows. Casual — hair slightly messy, hoodie on.

She's on her phone, scrolling. Her eyes widen suddenly. She does a sharp inhale — grabs the arm of someone sitting next to her off-camera, pulls them toward the screen urgently. Points at her phone. Mouths "look at this." The person reacts off-camera. She looks at the camera — huge eyes, mouth open — like she's confirming that yes, this is real. Looks back at phone. Taps the screen a few times. Looks back into camera and slowly shakes her head.

Visible pulse of excitement in her movements. Natural blinks. Slight camera shake as she moves and gestures.

Audio: common room noise — distant chatter, chair scraping. Her sudden sharp inhale is audible. No music.""",
    },
    {
        "id": "hook_04_2am_glow",
        "title": "The 2AM Glow",
        "prompt": f"""Vertical 9:16 selfie-style phone video. She holds the phone at arm's length — arm visible. Handheld, very slight shake — she's tired, movements slower. Phone grainy in low light, digital noise visible. Feels like 2am. Looks exactly like a real phone recording.

{CHARACTER_DNA}. Dark room — only the cold blue-white glow of a phone screen lighting her face from below and in front. Late night study session. She looks exhausted — eyes slightly puffy, hair loosely tied.

She taps her phone screen to open an app. Reads. Her face changes. The exhaustion disappears — replaced by something she wasn't expecting. Eyes slowly widen in the dark. She exhales — a slow, quiet breath that she didn't plan. Looks directly into the camera. Long pause. The phone glow catches the slight moisture in her eyes — not crying, just overwhelmed. She shakes her head slowly. Looks back down at the screen. Then back at camera.

Audio: complete silence except her slow exhale and the faint creak of the building. No music.""",
    },
    {
        "id": "hook_05_score_reveal",
        "title": "The Score Reveal",
        "prompt": f"""Vertical 9:16 selfie-style phone video. She holds the phone at arm's length recording herself — arm and grip visible. Natural handheld camera motion — small unconscious movements. Slightly grainy, phone-camera quality, real aspect ratio. Looks completely candid.

{CHARACTER_DNA}. Bright study space — late afternoon natural light. She's been waiting for this.

She opens her phone and navigates to a results page. Her jaw is tight — biting her lip nervously. She blinks. The screen loads. Her eyes scan the results. One beat. Two beats. Then — eyebrows shoot up all at once. Her hand goes involuntarily to her mouth. She looks up at the camera — stunned, eyes filling slightly. She looks back at the phone screen. Scrolls. Looks up again — slow nod. This is real.

Natural micro-movements throughout — the slight tremble of the phone in her hand, involuntary swallow, the way she blinks rapidly when processing.

Audio: ambient study space sounds — distant keyboard clatter, air conditioning. Her sharp intake of breath when she sees the score is audible.""",
    },
]

# ── Step 1: Generate character image ──────────────────────────────────────────

def generate_character_image(hook_id: str) -> Path:
    print(f"\n[1/3] Generating character with {IMAGE_MODEL} ...")
    out_path = OUT_DIR / f"{hook_id}_character.jpg"

    resp = requests.post(
        f"{GEMINI_BASE}/models/{IMAGE_MODEL}:generateContent?key={GEMINI_KEY}",
        json={
            "contents": [{"parts": [{"text": CHARACTER_PROMPT}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        },
    )
    if not resp.ok:
        raise RuntimeError(f"Image gen failed [{resp.status_code}]: {resp.text[:500]}")

    parts = resp.json()["candidates"][0]["content"]["parts"]
    img_part = next((p for p in parts if "inlineData" in p), None)
    if not img_part:
        raise RuntimeError("No image in Gemini response")

    img_bytes = base64.b64decode(img_part["inlineData"]["data"])
    out_path.write_bytes(img_bytes)
    print(f"  [save] {out_path.name} ({len(img_bytes) // 1024} KB)")
    return out_path


# ── Step 2: Submit to Veo 3 (image-to-video) ──────────────────────────────────

def submit_veo(char_image: Path, prompt: str) -> str:
    print(f"\n[2/3] Submitting to Veo 3 ...")

    img_bytes = char_image.read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode()

    # Try image-to-video first
    resp = requests.post(
        f"{GEMINI_BASE}/models/{VIDEO_MODEL}:predictLongRunning?key={GEMINI_KEY}",
        json={
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": img_b64,
                    "mimeType": "image/jpeg",
                },
            }],
            "parameters": {
                "aspectRatio": "9:16",
                "durationSeconds": 8,
                "sampleCount": 1,
            }
        },
    )

    if not resp.ok:
        # Fallback: text-to-video
        print(f"  image-to-video failed ({resp.status_code}): {resp.text[:300]}")
        print(f"  Falling back to text-to-video ...")
        resp = requests.post(
            f"{GEMINI_BASE}/models/{VIDEO_MODEL}:predictLongRunning?key={GEMINI_KEY}",
            json={
                "instances": [{"prompt": prompt}],
                "parameters": {
                    "aspectRatio": "9:16",
                    "durationSeconds": 8,
                    "sampleCount": 1,
                }
            },
        )
        if not resp.ok:
            raise RuntimeError(f"Veo 3 submit failed [{resp.status_code}]: {resp.text[:500]}")

    op_name = resp.json()["name"]
    print(f"  [submit] → {op_name}")
    return op_name


# ── Poll + download ────────────────────────────────────────────────────────────

def poll_and_download(op_name: str, hook_id: str) -> Path:
    out_path = OUT_DIR / f"{hook_id}.mp4"
    print(f"  [poll] waiting ...")
    while True:
        time.sleep(10)
        r = requests.get(f"{GEMINI_BASE}/{op_name}?key={GEMINI_KEY}")
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:300]}")
        data = r.json()
        done = data.get("done", False)
        print(f"  [poll] done={done}", flush=True)
        if done:
            break

    response = data.get("response", {})

    # Format 1: generateVideoResponse with URI
    gen_resp = response.get("generateVideoResponse", {})
    samples = gen_resp.get("generatedSamples", [])
    if samples:
        video_uri = samples[0].get("video", {}).get("uri", "")
        if video_uri:
            dl = requests.get(f"{video_uri}&key={GEMINI_KEY}")
            if not dl.ok:
                raise RuntimeError(f"Video download failed: {dl.text[:300]}")
            out_path.write_bytes(dl.content)
            print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
            return out_path

    # Format 2: predictions with base64
    predictions = response.get("predictions", [])
    if not predictions:
        raise RuntimeError(f"No video in response: {json.dumps(data)[:400]}")

    video_b64 = predictions[0].get("bytesBase64Encoded", "")
    if not video_b64:
        video_b64 = predictions[0].get("video", {}).get("bytesBase64Encoded", "")
    if not video_b64:
        raise RuntimeError(f"No video bytes in predictions: {json.dumps(predictions[0])[:400]}")

    out_path.write_bytes(base64.b64decode(video_b64))
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── Slack ──────────────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path, hook: dict) -> None:
    print(f"\n[3/3] Sending to Slack ...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", f"text=*[VEO HOOK]* {hook['id']} — {hook['title']}\nGemini nano-banana-pro character + Veo 3 video (9:16)",
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {result.stdout.strip() or result.stderr.strip()}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not GEMINI_KEY:
        sys.exit("ERROR: source ~/.env_azure first (GEMINI_API_KEY missing)")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hooks", nargs="+", type=int, help="Hook numbers (1-based, e.g. --hooks 1 3)")
    parser.add_argument("--all", action="store_true", help="Run all 5 hooks")
    args = parser.parse_args()

    if args.all:
        selected = HOOKS
    elif args.hooks:
        selected = [HOOKS[i - 1] for i in args.hooks]
    else:
        selected = [HOOKS[0]]  # default: hook 1 only

    print(f"Running {len(selected)} hook(s): {[h['id'] for h in selected]}")

    for hook in selected:
        print(f"\n{'='*60}")
        print(f"Hook: {hook['id']} — {hook['title']}")
        print(f"{'='*60}")
        try:
            char_img = generate_character_image(hook["id"])
            op_name  = submit_veo(char_img, hook["prompt"])
            video    = poll_and_download(op_name, hook["id"])
            send_to_slack(video, hook)
            print(f"\n✓ Done: {video}")
        except Exception as e:
            print(f"\n[ERROR] {hook['id']}: {e}")
            continue

    print("\n✓ All done.")
