#!/usr/bin/env python3
"""
UGC Livestream Call Format — Veo 3 Pipeline
Format: Viral 1:1 streamer call — Harvard student casually reveals Professor Curious
Style: Omegle/creator livestream screen recording, split-screen 9:16
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[warn] Pillow not found — UI overlay will be skipped")

# ── Config ─────────────────────────────────────────────────────────────────────

GEMINI_KEY  = os.environ.get("GEMINI_API_KEY", "")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
VIDEO_MODEL = "veo-3.0-generate-001"

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"  # working channel

OUT_DIR = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-call-hooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── UI Overlay (Pillow) ────────────────────────────────────────────────────────

def make_ui_overlay(hook_id: str, streamer_name: str = "@sarah_streams",
                    viewer_count: str = "2.4K", student_label: str = "Harvard University") -> Path | None:
    """Generate PNG overlay: LIVE badge, viewer count, divider, fake scrolling chat."""
    if not HAS_PIL:
        return None

    W, H = 1080, 1920
    mid  = H // 2

    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Font loading — fallback gracefully
    def load_font(size):
        for path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    f_lg   = load_font(36)
    f_md   = load_font(26)
    f_sm   = load_font(22)
    f_chat = load_font(21)

    # ── Top section (streamer) ────────────────────────────────────────────────

    # Semi-transparent top bar (context for streamer section)
    draw.rectangle([0, 0, W, 90], fill=(0, 0, 0, 120))

    # Red LIVE dot
    draw.ellipse([18, 24, 42, 48], fill=(235, 50, 50, 240))

    # LIVE text
    draw.text((52, 20), "LIVE", font=f_lg, fill=(255, 255, 255, 240))

    # Viewer count
    draw.text((130, 26), f"  👁  {viewer_count} watching", font=f_md, fill=(220, 220, 220, 200))

    # Streamer handle
    draw.text((18, 56), streamer_name, font=f_sm, fill=(180, 180, 180, 200))

    # ── Divider ───────────────────────────────────────────────────────────────

    draw.rectangle([0, mid - 3, W, mid + 3], fill=(30, 30, 30, 230))

    # ── Bottom section (student / caller) ────────────────────────────────────

    # Thin top bar on student section
    draw.rectangle([0, mid, W, mid + 64], fill=(0, 0, 0, 110))

    # Call icon + label
    draw.text((18, mid + 16), f"📞  {student_label}", font=f_md, fill=(200, 200, 200, 200))

    # Student name bottom-left
    draw.rectangle([0, H - 80, W, H], fill=(0, 0, 0, 120))
    draw.text((18, H - 58), student_label, font=f_sm, fill=(255, 255, 255, 180))

    # ── Fake chat (right side, bottom half) ───────────────────────────────────

    chat_messages = [
        ("user123",       "omg wait 👀"),
        ("prep_ananya",   "harvard??"),
        ("studygrind_rk", "whats the app"),
        ("janelle_xo",    "PROFESSOR CURIOUS?"),
        ("emmah.k",       "need this rn 🙏"),
        ("coachingkid",   "🔥🔥🔥"),
        ("ravi_prep",     "LINK???"),
        ("tanya.reads",   "downloading now"),
        ("priya_neet",    "does it work for science"),
        ("lex_student",   "omg yes it does"),
    ]

    # Right-side chat area
    chat_x  = W - 340
    chat_y0 = mid + 80

    # Slight dark bg behind chat for readability
    draw.rectangle([chat_x - 10, chat_y0 - 8, W, H - 90], fill=(0, 0, 0, 80))

    for i, (uname, msg) in enumerate(chat_messages):
        y = chat_y0 + i * 38
        if y > H - 100:
            break
        # Username in slightly brighter color
        draw.text((chat_x, y), f"{uname}:", font=f_sm, fill=(160, 200, 255, 220))
        draw.text((chat_x, y + 18), msg, font=f_chat, fill=(240, 240, 240, 200))

    out_path = OUT_DIR / f"{hook_id}_ui.png"
    img.save(out_path, "PNG")
    print(f"  [ui] {out_path.name}")
    return out_path


# ── Veo 3 helpers ──────────────────────────────────────────────────────────────

def submit_veo(prompt: str, aspect: str = "16:9", duration: int = 8) -> str:
    resp = requests.post(
        f"{GEMINI_BASE}/models/{VIDEO_MODEL}:predictLongRunning?key={GEMINI_KEY}",
        json={
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": aspect,
                "durationSeconds": duration,
                "sampleCount": 1,
            },
        },
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"Veo submit failed [{resp.status_code}]: {resp.text[:500]}")
    op_name = resp.json()["name"]
    print(f"  [submit] → {op_name}")
    return op_name


def poll_and_download(op_name: str, out_path: Path) -> Path:
    print(f"  [poll] waiting for {out_path.name} ...")
    while True:
        time.sleep(12)
        r = requests.get(f"{GEMINI_BASE}/{op_name}?key={GEMINI_KEY}", timeout=30)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:300]}")
        data = r.json()
        done = data.get("done", False)
        print(f"  [poll] done={done}", flush=True)
        if done:
            break

    response = data.get("response", {})

    # Format 1: URI
    gen_resp = response.get("generateVideoResponse", {})
    samples  = gen_resp.get("generatedSamples", [])
    if samples:
        uri = samples[0].get("video", {}).get("uri", "")
        if uri:
            dl = requests.get(f"{uri}&key={GEMINI_KEY}", timeout=120)
            if not dl.ok:
                raise RuntimeError(f"Download failed: {dl.text[:300]}")
            out_path.write_bytes(dl.content)
            print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
            return out_path

    # Format 2: base64
    preds = response.get("predictions", [])
    if not preds:
        raise RuntimeError(f"No video in response: {json.dumps(data)[:400]}")
    b64 = preds[0].get("bytesBase64Encoded", "") or \
          preds[0].get("video", {}).get("bytesBase64Encoded", "")
    if not b64:
        raise RuntimeError(f"No video bytes: {json.dumps(preds[0])[:400]}")
    out_path.write_bytes(base64.b64decode(b64))
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── Composite helpers ──────────────────────────────────────────────────────────

def composite_split_screen(streamer_mp4: Path, student_mp4: Path, out_path: Path) -> Path:
    """
    Stack streamer (top) + student (bottom) → 1080x1920 (9:16).
    Each input is 16:9 → scaled & cropped to 1080x960.
    """
    vf = (
        "[0:v]scale=1920:1080,crop=1080:960:420:60,setsar=1,fps=24[top];"
        "[1:v]scale=1920:1080,crop=1080:960:420:60,setsar=1,fps=24[bot];"
        "[top][bot]vstack=inputs=2[v]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(streamer_mp4),
        "-i", str(student_mp4),
        "-filter_complex", vf,
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        "-shortest",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg composite failed:\n{r.stderr[-600:]}")
    print(f"  [composite] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def apply_ui_overlay(video_path: Path, ui_png: Path, out_path: Path) -> Path:
    """Overlay the UI PNG on top of the composited video."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(ui_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr[-400:]}")
    print(f"  [overlay] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── Slack ──────────────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path, hook: dict) -> None:
    print(f"\n[→ Slack] {hook['id']} ...")
    r = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", (
            f"text=*[CALL FORMAT]* `{hook['id']}` — {hook['title']}\n"
            f"> {hook['angle']}\n"
            f"Veo 3 | 9:16 | split-screen livestream call style | Professor Curious"
        ),
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {r.stdout.strip() or r.stderr.strip()}")


# ── Hooks ──────────────────────────────────────────────────────────────────────

HOOKS = [
    {
        "id":    "call_01_wait_harvard",
        "title": "wait you go to HARVARD??",
        "angle": "Streamer stumbles on Harvard student — casual reveal of Professor Curious",
        "streamer_name":  "@sarah_streams",
        "student_label":  "Harvard University 🎓",
        "viewer_count":   "2.4K",

        "streamer_prompt": """\
Vertical 9:16 selfie-cam video of a young woman, early 20s, in her bedroom at night.
Ring light illuminating her face. iPhone front-camera quality — slightly grainy, natural skin.
She's looking at a laptop screen to her left (off-camera), squinting. She mouths something,
then her eyes go wide. She whips back to face the camera — mouth drops open in total shock.
She leans forward, pointing at the screen, gesturing like she cannot believe what she's seeing.
She shakes her head slowly, eyes enormous, mouthing "oh my GOD." One hand covers her mouth.
Natural handheld camera drift. No makeup, messy hair tied back. Hoodie. Completely real UGC energy.
NOT model-looking. Real person reacting to something genuinely shocking.""",

        "student_prompt": """\
Vertical 9:16 video of a young man, 21, in a Harvard dorm room. Harvard crimson pennant
on the wall behind him. Desk lamp, stacked textbooks, laptop open. Standard FaceTime call quality.
He's looking into the camera and talking calmly — relaxed, slightly amused smile.
He gestures with one hand while he speaks, like explaining something obvious.
He glances down at his phone briefly, taps it, then looks back up at the camera.
Nods confidently. Not boasting — just genuinely matter-of-fact. Completely natural.
He mouths clearly: "Professor Curious. It solves any doubt — any subject, instantly.
My whole dorm uses it." He shrugs like it's the most normal thing in the world.""",
    },

    {
        "id":    "call_02_3am_chill",
        "title": "3am and you're NOT stressed??",
        "angle": "Exhausted streamer meets Harvard pre-med who has it figured out",
        "streamer_name":  "@midnight_study",
        "student_label":  "Harvard Pre-Med 📚",
        "viewer_count":   "1.8K",

        "streamer_prompt": """\
Vertical 9:16 selfie-cam video of a young woman, 20, at 3am. She's at her study desk —
dark room, only her laptop and a small lamp lighting her face with a blue-white glow.
She looks genuinely exhausted — puffy eyes, hair messy, hoodie. She glances at the camera,
then does a double-take at the laptop screen. She leans in closer, disbelieving.
She looks straight into the camera with wide exhausted eyes and slowly mouths
"how are you NOT stressed right now??" pointing off-screen at the other person.
She exhales slowly. Pure UGC realism — grainy, tired, real.""",

        "student_prompt": """\
Vertical 9:16 FaceTime-style video of a young woman, 22, Harvard pre-med student.
Late night — warm desk lamp. She looks slightly tired but calm, composed.
She's smiling gently at the camera, shaking her head like she understands.
She picks up her phone, shows the screen to the camera (we see the glow, not the content).
She puts it back down, looks up and says clearly: "I just ask Professor Curious.
Any topic — biology, chemistry, physics, math — it just explains it instantly.
I haven't panicked about studying since I found it." Calm nod. Natural eye contact.
Completely believable. Not performative — just honest.""",
    },

    {
        "id":    "call_03_my_chat_wants_to_know",
        "title": "my chat is LOSING IT rn",
        "angle": "Streamer reads out her chat asking about Professor Curious",
        "streamer_name":  "@lexie.live",
        "student_label":  "Harvard CS 💻",
        "viewer_count":   "5.1K",

        "streamer_prompt": """\
Vertical 9:16 selfie-cam, young woman 23, casual living room, ring light, laptop setup.
She's looking slightly left at her screen where the chat is. Her eyes are scanning fast,
reading the comments. She starts laughing — a real surprised laugh. She looks directly
into the camera and points at the screen: "okay my CHAT is asking — what app is that,
what app is that, everyone wants to know." She turns back to look at the laptop
(the student's side) expectantly, eyebrows raised. High energy. Natural, slightly chaotic.
Real streamer energy — not scripted.""",

        "student_prompt": """\
Vertical 9:16 video call quality, young man 20, Harvard computer science dorm room.
Multiple monitors visible behind him. He's slightly amused by the chaos, laughing a bit.
He leans toward the camera and says clearly, slowly, like spelling it out:
"Professor Curious. P-R-O-F-E-S-S-O-R C-U-R-I-O-U-S." He holds up one finger.
"It's an AI that solves any doubt. Any subject. Like actually any subject — I've tested it."
He gestures naturally, completely confident. Then he laughs and says "tell your chat
to download it." Completely natural, unscripted energy. Smart, calm, real.""",
    },

    {
        "id":    "call_04_every_subject",
        "title": "wait — EVERY subject??",
        "angle": "Skeptical streamer can't believe one app works for everything",
        "streamer_name":  "@study.with.me",
        "student_label":  "Harvard Engineering 🔬",
        "viewer_count":   "3.2K",

        "streamer_prompt": """\
Vertical 9:16 selfie-cam, young woman 21, bright study room setup, afternoon light.
She has an expression of total disbelief — eyebrows raised, head tilted, squinting slightly.
She holds up her hand like she's stopping something: "wait — EVERY subject?
Like science AND math AND English?" She looks at the camera to share the moment with
her viewers, then back at the laptop. She repeats the gesture — genuinely baffled, not acting.
She's half-laughing because it sounds too good. Natural, slightly suspicious, real.
The camera sways slightly from her movement. iPhone grainy quality.""",

        "student_prompt": """\
Vertical 9:16 FaceTime-quality video, young man 22, Harvard engineering student.
Relaxed in his dorm room chair, Harvard hoodie. He nods slowly when he hears the question.
He holds up fingers one by one: "physics — yeah. organic chemistry — yeah.
calculus — definitely. even essay writing — it explains the logic, not just gives an answer."
He leans in slightly: "Professor Curious doesn't give you the answer and leave.
It actually teaches you. That's why it works for every subject." He sits back.
Completely convinced, completely natural. Not selling it — just stating facts.""",
    },

    {
        "id":    "call_05_dorm_secret",
        "title": "this is literally the dorm secret",
        "angle": "Harvard student reveals it's common knowledge — streamer shocked everyone knew but her",
        "streamer_name":  "@emma.studies",
        "student_label":  "Harvard Yard 🏛️",
        "viewer_count":   "4.7K",

        "streamer_prompt": """\
Vertical 9:16 selfie-cam, young woman 22, cozy bedroom night setup, fairy lights background.
She is completely stunned — jaw literally dropped. She looks at the camera, then at the laptop,
then back at the camera. She holds both hands up: "wait so EVERYONE at Harvard knows about this
and I'm only finding out NOW??" She laughs, shaking her head in disbelief.
She grabs her phone from off-screen and looks at it, then straight at the camera with
the most exasperated face. "I have been suffering this entire semester." Completely real,
totally relatable, not performed. Natural UGC selfie quality.""",

        "student_prompt": """\
Vertical 9:16 video call, young woman 20, Harvard dorm, casual. She's laughing genuinely.
"Yeah it's kind of just... common knowledge here? Like people just use Professor Curious."
She shrugs — "it's the AI that actually teaches you, not just gives answers.
Any subject. Any question. You get it instantly." She tilts her head:
"I thought everyone knew about it." She looks warmly at the camera — not bragging,
just surprised it's news. Completely natural laugh. Real warmth. Smart, approachable,
the kind of person you'd trust immediately.""",
    },
]


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_hook(hook: dict) -> None:
    hook_id  = hook["id"]
    hook_dir = OUT_DIR / hook_id
    hook_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Hook: {hook_id} — {hook['title']}")
    print(f"{'='*60}")

    # ── Step 1: Submit both clips to Veo 3 simultaneously ─────────────────────
    print("\n[1/4] Submitting both clips to Veo 3 ...")
    streamer_op = submit_veo(hook["streamer_prompt"], aspect="9:16", duration=8)
    student_op  = submit_veo(hook["student_prompt"],  aspect="9:16", duration=8)

    # ── Step 2: Download both (poll in alternation) ───────────────────────────
    print("\n[2/4] Downloading clips ...")

    streamer_path = hook_dir / f"{hook_id}_streamer.mp4"
    student_path  = hook_dir / f"{hook_id}_student.mp4"

    # Poll both — poll alternately to avoid double-sleeping
    streamer_done = False
    student_done  = False
    streamer_data = None
    student_data  = None

    while not (streamer_done and student_done):
        time.sleep(12)
        if not streamer_done:
            r = requests.get(f"{GEMINI_BASE}/{streamer_op}?key={GEMINI_KEY}", timeout=30)
            if r.ok and r.json().get("done"):
                streamer_done = True
                streamer_data = r.json()
                print(f"  [poll] streamer done ✓")
            else:
                print(f"  [poll] streamer pending ...")

        if not student_done:
            r = requests.get(f"{GEMINI_BASE}/{student_op}?key={GEMINI_KEY}", timeout=30)
            if r.ok and r.json().get("done"):
                student_done = True
                student_data = r.json()
                print(f"  [poll] student done ✓")
            else:
                print(f"  [poll] student pending ...")

    def save_video(data: dict, out_path: Path) -> Path:
        response = data.get("response", {})
        gen_resp = response.get("generateVideoResponse", {})
        samples  = gen_resp.get("generatedSamples", [])
        if samples:
            uri = samples[0].get("video", {}).get("uri", "")
            if uri:
                dl = requests.get(f"{uri}&key={GEMINI_KEY}", timeout=120)
                out_path.write_bytes(dl.content)
                print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
                return out_path
        preds = response.get("predictions", [])
        if preds:
            b64 = preds[0].get("bytesBase64Encoded", "") or \
                  preds[0].get("video", {}).get("bytesBase64Encoded", "")
            if b64:
                out_path.write_bytes(base64.b64decode(b64))
                print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
                return out_path
        raise RuntimeError(f"No video in response: {json.dumps(data)[:400]}")

    save_video(streamer_data, streamer_path)
    save_video(student_data,  student_path)

    # ── Step 3: Composite split-screen ────────────────────────────────────────
    print("\n[3/4] Compositing split-screen ...")
    composite_path = hook_dir / f"{hook_id}_composite.mp4"
    composite_split_screen(streamer_path, student_path, composite_path)

    # ── Step 4: UI overlay ────────────────────────────────────────────────────
    final_path = hook_dir / f"{hook_id}_final.mp4"
    ui_png = make_ui_overlay(
        hook_id        = hook_id,
        streamer_name  = hook["streamer_name"],
        viewer_count   = hook["viewer_count"],
        student_label  = hook["student_label"],
    )
    if ui_png:
        print("\n[4/4] Applying UI overlay ...")
        apply_ui_overlay(composite_path, ui_png, final_path)
    else:
        # No Pillow — use composite as final
        composite_path.rename(final_path)

    # ── Done — send to Slack ──────────────────────────────────────────────────
    send_to_slack(final_path, hook)
    print(f"\n✓ {hook_id} → {final_path}")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not GEMINI_KEY:
        sys.exit("ERROR: GEMINI_API_KEY missing — run: source ~/.env_azure")

    import argparse
    parser = argparse.ArgumentParser(description="UGC Livestream Call Format — Veo 3")
    parser.add_argument("--hooks", nargs="+", type=int,
                        help="Hook numbers to run (1-based). e.g. --hooks 1 3")
    parser.add_argument("--all", action="store_true", help="Run all 5 hooks")
    args = parser.parse_args()

    if args.all:
        selected = HOOKS
    elif args.hooks:
        selected = [HOOKS[i - 1] for i in args.hooks]
    else:
        selected = [HOOKS[0]]  # default: hook 1 only

    print(f"\nRunning {len(selected)} hook(s): {[h['id'] for h in selected]}")
    print(f"Output: {OUT_DIR}\n")

    for hook in selected:
        try:
            run_hook(hook)
        except Exception as e:
            print(f"\n[ERROR] {hook['id']}: {e}")
            continue

    print("\n✓ All done.")
