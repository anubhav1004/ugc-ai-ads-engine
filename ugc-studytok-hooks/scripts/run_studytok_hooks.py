#!/usr/bin/env python3
"""
StudyTok Snapchat-Style Hooks — Veo 3 Pipeline

Format:
  [Reaction hook 6-8s, Veo 3, Snapchat caption bar] + [Product demo ~12s, muted, no text]
  + trending audio over everything

Style reference: girl picks up phone, sees notification, jaw drop — raw TikTok draft energy
"WE ARE the phone camera" POV throughout
"""

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
    print("[warn] Pillow not found — caption overlay skipped")

# ── Config ─────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"

OUT_DIR   = Path.home() / ".openclaw/workspace/output/ugc-studytok-hooks"
AUDIO_DIR = OUT_DIR / "audio"
DEMO_DIR  = Path.home() / "Downloads"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Demo clips — 2 new demo videos, cycled across hooks
DEMO_CLIPS = [
    DEMO_DIR / "761f2bb3b84a4003a9744b4e5b45a4f2.MP4",  # 27.9s
    DEMO_DIR / "958c1b7bb7d4413d8276bfaa828a58d8.MP4",  # 24.6s
]

# Audio pool — chosen per hook based on total video length at runtime
AUDIO_POOL = {
    "short":  AUDIO_DIR / "audio_01_oh_no.mp3",    # <35s — punchy, Oh No Kreepa
    "medium": AUDIO_DIR / "audio_03_cupid.mp3",    # 35-55s — Cupid FIFTY FIFTY
    "long":   AUDIO_DIR / "audio_02_aperture.mp3", # >55s — Aperture, sustained
}

def pick_audio(reaction_secs: int, demo_secs: float) -> Path:
    total = reaction_secs + demo_secs
    if total < 35:
        return AUDIO_POOL["short"]
    elif total < 55:
        return AUDIO_POOL["medium"]
    else:
        return AUDIO_POOL["long"]

DEMO_TRIM_START = 0   # start from beginning
DEMO_TRIM_LEN   = None  # None = use full clip duration

# ── Snapchat caption overlay ───────────────────────────────────────────────────

import re

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FFFF"
    "\U00002600-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0]+",
    flags=re.UNICODE,
)

def split_runs(text: str):
    """Split text into [(segment, is_emoji), ...]"""
    runs, pos = [], 0
    for m in EMOJI_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False))
        runs.append((m.group(), True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False))
    return runs


def make_snapchat_caption(hook_id: str, caption_text: str,
                           width: int = 720, height: int = 1280) -> Path | None:
    """
    Snapchat-style caption bar slightly above center.
    Renders text with Helvetica + emoji with Apple Color Emoji side-by-side.
    """
    if not HAS_PIL:
        return None

    FONT_SIZE = 40

    def try_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return None

    font_text  = (try_font("/System/Library/Fonts/Helvetica.ttc", FONT_SIZE)
                  or try_font("/System/Library/Fonts/Arial.ttf", FONT_SIZE)
                  or ImageFont.load_default())
    font_emoji = (try_font("/System/Library/Fonts/Apple Color Emoji.ttc", FONT_SIZE)
                  or font_text)

    # --- Word-wrap on plain text, then split each line into runs ---
    img_measure  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_measure = ImageDraw.Draw(img_measure)

    def seg_width(seg: str, is_emoji: bool) -> float:
        f = font_emoji if is_emoji else font_text
        try:
            return draw_measure.textlength(seg, font=f)
        except Exception:
            bb = draw_measure.textbbox((0, 0), seg, font=f)
            return bb[2] - bb[0]

    def runs_width(runs) -> float:
        return sum(seg_width(s, e) for s, e in runs)

    max_w = width - 48
    words = caption_text.split(" ")
    line_texts = []
    current    = ""

    for word in words:
        test = (current + " " + word).strip() if current else word
        w    = runs_width(split_runs(test))
        if w > max_w and current:
            line_texts.append(current)
            current = word
        else:
            current = test
    if current:
        line_texts.append(current)

    line_runs_list = [split_runs(lt) for lt in line_texts]

    line_h = FONT_SIZE + 14
    pad_v  = 22
    bar_h  = len(line_runs_list) * line_h + pad_v * 2

    # Top-aligned — above the face (top 10% of frame)
    bar_y = int(height * 0.08)

    # --- Render ---
    img  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, bar_y, width, bar_y + bar_h], fill=(0, 0, 0, 165))

    for i, runs in enumerate(line_runs_list):
        total_w = runs_width(runs)
        x = (width - total_w) // 2
        y = bar_y + pad_v + i * line_h

        for seg, is_emoji in runs:
            if not seg:
                continue
            f = font_emoji if is_emoji else font_text
            try:
                draw.text((int(x), y), seg, font=f,
                          fill=(255, 255, 255, 255), embedded_color=is_emoji)
            except TypeError:
                draw.text((int(x), y), seg, font=f, fill=(255, 255, 255, 255))
            x += seg_width(seg, is_emoji)

    out_path = OUT_DIR / f"{hook_id}_caption.png"
    img.save(out_path, "PNG")
    print(f"  [caption] {out_path.name}")
    return out_path


# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_sora(prompt: str, seconds: int = 8) -> str:
    resp = requests.post(
        f"{BASE_URL}/videos",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(seconds)},
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"Sora submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"Sora API error: {job['error']}")
    video_id = job["id"]
    print(f"  [submit] → {video_id}")
    return video_id


def poll_sora(video_id: str) -> None:
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed [{r.status_code}]: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll] {status} {progress}%", flush=True)
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"Sora job failed: {json.dumps(data)[:400]}")


def download_sora(video_id: str, out_path: Path) -> Path:
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed [{dl.status_code}]: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ── ffmpeg helpers ─────────────────────────────────────────────────────────────

def apply_caption_overlay(reaction_mp4: Path, caption_png: Path, out_path: Path) -> Path:
    """Burn Snapchat caption PNG onto reaction video."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(reaction_mp4),
        "-i", str(caption_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-an",  # mute
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"caption overlay failed:\n{r.stderr[-400:]}")
    print(f"  [overlay] {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def trim_demo(demo_clip: Path, out_path: Path) -> Path:
    """Process demo clip — scale to 720x1280, strip audio, keep full duration."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(demo_clip),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1",
        "-an",  # mute
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"trim demo failed:\n{r.stderr[-400:]}")
    dur = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(out_path)],
        capture_output=True, text=True
    ).stdout.strip()
    print(f"  [demo] {out_path.name} ({float(dur):.1f}s, {out_path.stat().st_size // 1024} KB)")
    return out_path


def scale_reaction(reaction_mp4: Path, out_path: Path) -> Path:
    """Scale reaction clip to 720x1280, strip audio."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(reaction_mp4),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1",
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"scale reaction failed:\n{r.stderr[-400:]}")
    return out_path


def concat_and_add_audio(reaction_mp4: Path, demo_mp4: Path,
                          audio_mp3: Path, out_path: Path) -> Path:
    """
    Concatenate reaction + demo (both silent),
    then lay trending audio over the full video.
    Audio trimmed/looped to match total duration.
    """
    # Step 1: concat
    concat_path = out_path.parent / f"{out_path.stem}_concat.mp4"
    concat_list = out_path.parent / f"{out_path.stem}_concat.txt"
    concat_list.write_text(
        f"file '{reaction_mp4.resolve()}'\nfile '{demo_mp4.resolve()}'\n"
    )
    cmd1 = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an",
        str(concat_path),
    ]
    r = subprocess.run(cmd1, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"concat failed:\n{r.stderr[-400:]}")

    # Get total duration
    dur_str = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(concat_path)],
        capture_output=True, text=True
    ).stdout.strip()
    total_dur = float(dur_str) if dur_str else 20.0

    # Step 2: add audio (trim to video length, loop if shorter)
    cmd2 = [
        "ffmpeg", "-y",
        "-i", str(concat_path),
        "-stream_loop", "-1", "-i", str(audio_mp3),
        "-filter_complex",
        f"[1:a]atrim=0:{total_dur},asetpts=PTS-STARTPTS,volume=0.85[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        "-t", str(total_dur),
        str(out_path),
    ]
    r = subprocess.run(cmd2, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"audio mix failed:\n{r.stderr[-400:]}")

    concat_path.unlink(missing_ok=True)
    concat_list.unlink(missing_ok=True)
    print(f"  [final] {out_path.name} ({out_path.stat().st_size // 1024} KB, {total_dur:.1f}s)")
    return out_path


# ── Slack ──────────────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path, hook: dict) -> None:
    print(f"\n[→ Slack] {hook['id']} ...")
    r = subprocess.run([
        "curl", "-s", "-X", "POST", SLACK_URL,
        "-F", f"channel_id={SLACK_CHANNEL}",
        "-F", (
            f"text=*[STUDYTOK HOOK]* `{hook['id']}` — {hook['title']}\n"
            f"> Caption: _{hook['caption']}_\n"
            f"> Character: {hook['character']}\n"
            f"Sora 2 reaction + product demo | trending audio (auto-picked) | 9:16"
        ),
        "-F", f"file=@{video_path}",
    ], capture_output=True, text=True)
    print(f"  [slack] {r.stdout.strip() or r.stderr.strip()}")


# ── Hooks ──────────────────────────────────────────────────────────────────────

HOOKS = [
    {
        "id":        "studytok_01_exam_3hrs",
        "title":     "exam in 3 hours discovery",
        "caption":   "I have an exam in 3 hours and I just found this 😭🫣✨",
        "character": "South Asian girl, 18, late night desk",
        "demo_clip": DEMO_CLIPS[0],
        "prompt": """\
WE ARE the phone camera. 9:16 vertical. RAW FRONT-CAM FOOTAGE — grainy, flat colors, no LUT,
real phone audio hiss. Looks exactly like a TikTok draft someone never meant to post.

A South Asian girl, 18-19. Dark circles, hair in a messy bun, oversized hoodie.
Cluttered study desk late at night — desk lamp warm glow, open textbooks, empty chai cup,
highlighters everywhere. NOT model-pretty. Exhausted and real.

WE (the phone) are lying face-up flat on her desk. She is hunched over her notes, ignoring us.
We see the ceiling fan above and the top of her head.

0-2s: Her hand reaches INTO FRAME from above and grabs us — the camera LURCHES upward fast
as she picks us up. Frame jolts. Autofocus micro-pulses as it finds her face.
We settle — her face fills the frame, close, slightly below eye level.

2-5s: She glances at our screen. Reads something. Her jaw drops slowly.
Eyes go wide. One hand moves to cover her mouth. Pure disbelief — mouth open, silent.
She stares. She re-reads it. Still stunned.

5-8s: She looks directly INTO the lens — directly at us. Shakes her head slowly.
Exhausted eyes, completely blown. She exhales one slow breath. Natural blink.
No words. The face says everything.

Ambient audio only: HVAC hum, distant street, her slow exhale.""",
    },

    {
        "id":        "studytok_02_been_struggling",
        "title":     "been struggling for months",
        "caption":   "me realizing I've been struggling for MONTHS for no reason 💀😭🙏",
        "character": "White girl with freckles, 20, college library",
        "demo_clip": DEMO_CLIPS[1],
        "prompt": """\
WE ARE the phone camera. 9:16 vertical. RAW FRONT-CAM FOOTAGE — slightly washed-out whites,
natural skin tones, compressed like a TikTok draft. Real library ambience. Not cinematic.

A white girl with freckles, 20, messy brown hair loose. Oversized university sweatshirt.
College library — fluorescent light mixed with window daylight. Textbooks and notes everywhere.
No ring light. No setup. Completely candid.

WE (the phone) are propped against a stack of books on the library table, slightly tilted,
facing her. She is hunched over her notes writing, ignoring us.

0-2s: Her phone (us) buzzes — notification. The camera shakes slightly from the vibration.
She glances over at us. Picks us up — camera tilts and reframes as she lifts us.
Autofocus adjusts to her face.

2-5s: She reads something on our screen. Brow furrows — she re-reads.
Then: realization hits. Expression shifts from confusion to shock.
Hand goes to her forehead. She tilts back, mouth open, staring at the screen.

5-8s: She looks directly INTO the lens — at us. Slow headshake.
She laughs once — short, disbelieving — then back to stunned.
The face of someone who just realized this existed the whole time.
Natural blinking. Slight grip wobble. Completely real.

Library ambience: distant pages, HVAC, her short exhale-laugh.""",
    },

    {
        "id":        "studytok_03_why_no_one_told_me",
        "title":     "why did no one tell me sooner",
        "caption":   "why did NO ONE tell me about this sooner 😭🔥✨",
        "character": "Girl at kitchen table, afternoon, bright natural light",
        "demo_clip": DEMO_CLIPS[0],
        "prompt": """\
WE ARE the phone camera. 9:16 vertical. Casual handheld selfie-cam footage.
Bright afternoon natural light from a window. Warm kitchen or living room.
Candid, unscripted — looks like someone filming themselves while doing homework.

A young woman, early 20s, sitting at a table with an open notebook and pen.
Casual clothes — a t-shirt. Hair down, natural. Daytime energy, relaxed.

WE (the phone) are propped against a water bottle on the table, facing her.

0-2s: She is writing in her notebook, focused. Her phone (us) buzzes with a notification.
She reaches over and picks us up. Camera shifts and reframes to her face.

2-5s: She reads what is on our screen. Tilts her head. Reads again.
Eyebrows rise. She puts her pen down slowly. Sits up.
Expression changes from neutral to genuinely surprised.

5-8s: She looks directly into the lens — at us — and shakes her head slowly.
Laughs a little — not performing, just the natural reaction of someone
who discovered something they should have known much earlier.
Hand goes to her cheek. Looks back at screen then at us again.

Ambient: quiet room, birds outside, soft natural sounds.""",
    },

    {
        "id":        "studytok_04_paying_tutors",
        "title":     "been paying tutors when this exists",
        "caption":   "I've been paying for tutors when THIS exists 😭💀✨",
        "character": "Black girl, 20, study desk, frustrated",
        "demo_clip": DEMO_CLIPS[1],
        "prompt": """\
WE ARE the phone camera. 9:16 vertical. RAW FRONT-CAM FOOTAGE — slightly tilted imperfect angle,
natural side window light, phone quality grain. First-take TikTok energy. Not polished.

A Black girl, 20. Natural hair in a puff, earrings, comfortable hoodie.
Study desk drowning in textbooks, notebooks, printed notes. Chin resting on her hand,
staring at a page with zero energy left. Real frustration. Not styled.

WE (the phone) are propped on a textbook at the edge of the desk, slightly tilted, facing her.
She is ignoring us, tapping her pen on her notebook.

0-3s: A notification buzzes — the whole camera shakes slightly.
She looks up at us. Unlocks the screen with her thumb. Reads.

3-6s: Her entire expression changes — the frustration melts.
She sits up straight. Eyes go wide. She stares at the screen.
Looks directly at the camera (us) — completely disbelieving.

6-8s: Hand goes to her head. She looks away for a beat — then back at us.
Pure "are you KIDDING me" energy. Slow exhale. Real and unperformed.
The face of someone who just found out they've been doing it the hard way.

Ambient: quiet room, pen tapping stops, her exhale.""",
    },

    {
        "id":        "studytok_05_2am_finally",
        "title":     "2am finally get it",
        "caption":   "POV: you finally understand the thing you've been failing 🥹✨💀",
        "character": "Girl, 19, dark bedroom, 2am",
        "demo_clip": DEMO_CLIPS[1],
        "prompt": """\
WE ARE the phone camera. 9:16 vertical. 2AM RAW FRONT-CAM — extreme digital grain from near-dark,
only the cold blue-white glow of our screen lighting her face. No other light source.
Looks exactly like a phone filmed at 2am with zero lights. Real. Raw. Quiet.

A girl, 19. Lying in bed under a duvet. Hoodie on. Hair loose and messy.
No makeup. Eyes slightly puffy from hours awake. NOT pretty-lit. Actual 2am.

WE (the phone) are lying face-up flat on the duvet beside her. We see the dark ceiling.

0-2s: Her hand reaches slowly into frame — she picks us up carefully.
Camera RISES as she lifts us, settles facing her close — only our glow illuminating her face
from below. Dark room around her.

2-5s: She reads something on our screen. Scrolls slowly.
Her face is completely still. A long beat. Processing.
The glow shifts slightly as she scrolls.

5-8s: She exhales — slow, quiet. Her eyes are slightly glassy, not crying, just overwhelmed.
She looks directly INTO the lens. Slow nod. Hand moves to her chest.
The face of someone for whom something just finally made sense.
Quiet. Real. Emotional without performing.

Audio: complete silence except her slow exhale and distant building creak.""",
    },
]


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_hook(hook: dict) -> None:
    hook_id  = hook["id"]
    hook_dir = OUT_DIR / hook_id
    hook_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Hook: {hook_id}")
    print(f"Caption: {hook['caption']}")
    print(f"{'='*60}")

    # 1. Submit to Sora
    print("\n[1/5] Submitting to Sora 2 ...")
    video_id = submit_sora(hook["prompt"], seconds=8)
    poll_sora(video_id)

    # 2. Download
    reaction_raw = hook_dir / f"{hook_id}_reaction_raw.mp4"
    download_sora(video_id, reaction_raw)

    # 3. Scale reaction to 720x1280
    print("\n[2/5] Scaling reaction ...")
    reaction_scaled = hook_dir / f"{hook_id}_reaction_scaled.mp4"
    scale_reaction(reaction_raw, reaction_scaled)

    # 4. Snapchat caption overlay on reaction
    print("\n[3/5] Adding Snapchat caption ...")
    caption_png = make_snapchat_caption(hook_id, hook["caption"])
    reaction_final = hook_dir / f"{hook_id}_reaction_final.mp4"
    if caption_png:
        apply_caption_overlay(reaction_scaled, caption_png, reaction_final)
    else:
        reaction_scaled.rename(reaction_final)

    # 5. Trim demo clip
    print("\n[4/5] Trimming demo clip ...")
    demo_trimmed = hook_dir / f"{hook_id}_demo.mp4"
    trim_demo(hook["demo_clip"], demo_trimmed)  # full duration, no trim

    # 6. Concat + trending audio — chosen by total video length
    demo_dur = float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(demo_trimmed)],
        capture_output=True, text=True
    ).stdout.strip() or "0")
    audio_path = pick_audio(reaction_secs=8, demo_secs=demo_dur)
    print(f"\n[5/5] Concat + trending audio ({audio_path.stem}, total ~{8+demo_dur:.0f}s) ...")
    final_path = hook_dir / f"{hook_id}_final.mp4"
    concat_and_add_audio(reaction_final, demo_trimmed, audio_path, final_path)

    # 7. Slack
    send_to_slack(final_path, hook)
    print(f"\n✓ {hook_id} → {final_path}")


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT missing — run: source ~/.env_azure")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hooks", nargs="+", type=int,
                        help="Hook numbers 1-based (e.g. --hooks 1 2)")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        selected = HOOKS
    elif args.hooks:
        selected = [HOOKS[i - 1] for i in args.hooks]
    else:
        selected = [HOOKS[0]]

    print(f"\nRunning {len(selected)} hook(s): {[h['id'] for h in selected]}")
    print(f"Output: {OUT_DIR}\n")

    for hook in selected:
        try:
            run_hook(hook)
        except Exception as e:
            print(f"\n[ERROR] {hook['id']}: {e}")
            continue

    print("\n✓ All done.")
