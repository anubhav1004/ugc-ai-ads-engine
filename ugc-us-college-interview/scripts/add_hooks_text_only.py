#!/usr/bin/env python3
"""
Apply text-only hook overlays to videos — NO logo overlay.
Hook text at top only. Clean video with just the Instagram-style text.

Usage:
  python3 add_hooks_text_only.py <video.mp4> [custom_hooks_json]

If no argument, auto-picks latest merged video in ugc-us-formats output.
"""

import requests
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
IMPACT_FONT   = "/System/Library/Fonts/Supplemental/Impact.ttf"
VW, VH        = 720, 1280

# Default hook variations (used when no custom hooks provided)
DEFAULT_HOOKS = [
    {"id": "h1_asked",    "lines": ["I asked 50 college students:", "Gauth or Professor Curious?", "One app won every single time"]},
    {"id": "h2_pov",      "lines": ["POV: random college students", "get asked which study app", "they actually use"]},
    {"id": "h3_compare",  "lines": ["Gauth vs Professor Curious", "Real students. No script.", "Watch till the end"]},
    {"id": "h4_switch",   "lines": ["Everyone's switching from Gauth", "to this one study app", "and I had to find out why"]},
]

# Per-format custom hooks (keyed by run_id) — used when processing format videos
FORMAT_HOOKS = {
    "fmt_01_confession": [
        {"id": "h1", "lines": ["I went from a 40% midterm", "to an 87 on the final.", "Here's exactly how."]},
        {"id": "h2", "lines": ["The app that saved my GPA", "when nothing else worked."]},
        {"id": "h3", "lines": ["POV: being completely honest", "about how you actually passed", "your hardest class"]},
        {"id": "h4", "lines": ["Every struggling student needs", "to know about Professor Curious."]},
    ],
    "fmt_02_skit": [
        {"id": "h1", "lines": ["POV: your roommate reveals", "why she never seems stressed", "anymore"]},
        {"id": "h2", "lines": ["2am. She's been on this problem", "for 3 hours. I know what to do."]},
        {"id": "h3", "lines": ["The app I've been hiding", "from my roommate", "(she found out)"]},
        {"id": "h4", "lines": ["When Professor Curious ends", "the study session standoff"]},
    ],
    "fmt_03_whisper": [
        {"id": "h1", "lines": ["Okay I'm only saying this once.", "So actually pay attention."]},
        {"id": "h2", "lines": ["The study app I genuinely", "don't want everyone to know."]},
        {"id": "h3", "lines": ["POV: overhearing the most useful", "thing in the college library"]},
        {"id": "h4", "lines": ["I shouldn't be telling you this.", "But it's Professor Curious."]},
    ],
    "fmt_04_group": [
        {"id": "h1", "lines": ["POV: your study group is", "absolutely cooked right now"]},
        {"id": "h2", "lines": ["Nobody panic.", "We have Professor Curious."]},
        {"id": "h3", "lines": ["The moment one person", "saves four GPAs"]},
        {"id": "h4", "lines": ["When Professor Curious ends", "the 2-hour group confusion"]},
    ],
    "fmt_05_ranking": [
        {"id": "h1", "lines": ["I tested every study app", "for 2 weeks. Here's the verdict."]},
        {"id": "h2", "lines": ["ChatGPT vs Gauth vs", "Professor Curious — who wins?"]},
        {"id": "h3", "lines": ["Ranking study apps as someone", "who actually tested them all"]},
        {"id": "h4", "lines": ["The comparison that changed", "how our whole dorm studies."]},
    ],
}


def draw_text_with_outline(draw, text, pos, font, fill, outline, outline_width=3):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build_text_only_overlay(hook_lines: list, tmp_path: Path) -> None:
    """Render ONLY the text hook — no logos, no VS, nothing else."""
    overlay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    hook_y_starts  = [40, 105, 165]
    hook_fontsizes = [52, 44, 38]

    for i, line in enumerate(hook_lines[:3]):
        try:
            hfont = ImageFont.truetype(IMPACT_FONT, hook_fontsizes[i])
        except Exception:
            hfont = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), line, font=hfont)
        tw   = bbox[2] - bbox[0]
        tx   = (VW - tw) // 2
        ty   = hook_y_starts[i]

        pad = 10
        draw.rounded_rectangle(
            [tx - pad, ty - pad//2, tx + tw + pad, ty + (bbox[3] - bbox[1]) + pad//2],
            radius=8, fill=(0, 0, 0, 110),
        )
        draw_text_with_outline(draw, line, (tx, ty), hfont, (255, 255, 255, 255), (0, 0, 0, 220), 4)

    overlay.save(str(tmp_path), "PNG")


def apply_hook(input_path: Path, hook: dict, out_dir: Path) -> Path:
    out_path = out_dir / f"{input_path.stem}_{hook['id']}.mp4"

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_png = Path(tf.name)

    print(f"  [{hook['id']}] Building overlay ...", flush=True)
    build_text_only_overlay(hook["lines"], tmp_png)

    filt = "[1:v]scale=720:1280[ovr];[0:v][ovr]overlay=0:0[out]"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(tmp_png),
        "-filter_complex", filt,
        "-map", "[out]", "-map", "0:a?",
        "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    tmp_png.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-600:]}")
    print(f"  [{hook['id']}] → {out_path.name} ({out_path.stat().st_size // 1024} KB)", flush=True)
    return out_path


def send_to_slack(video_path: Path, text: str) -> None:
    print(f"  [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    requests.post(SLACK_URL, data={"channel_id": SLACK_CHANNEL, "text": text})
    print(f"  [slack] {'✓ Sent' if resp.ok else '✗ ' + resp.text[:80]}", flush=True)


def process_video(video_path: Path) -> None:
    run_id   = video_path.parent.name
    hooks    = FORMAT_HOOKS.get(run_id, DEFAULT_HOOKS)
    out_dir  = video_path.parent / "hooks_text_only"
    out_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  Text-only hooks: {video_path.name}", flush=True)
    print(f"  Hooks: {len(hooks)} variations  |  No logo overlay", flush=True)
    print(f"{'='*60}", flush=True)

    for hook in hooks:
        try:
            out = apply_hook(video_path, hook, out_dir)
            hook_text = " / ".join(hook["lines"])
            send_to_slack(out, f"🎬 *{run_id}* — text hook only (no logo)\nHook: _{hook_text}_")
        except Exception as e:
            print(f"  ✗ Hook {hook['id']} failed: {e}", flush=True)


def main():
    if len(sys.argv) > 1:
        videos = [Path(sys.argv[1])]
    else:
        # Auto-process all 5 format merged videos
        out_root = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-us-formats"
        videos = sorted(out_root.glob("*/fmt_*_merged.mp4"))
        if not videos:
            sys.exit(f"No format merged videos found in {out_root}")

    print(f"\n{'#'*60}")
    print(f"  Text-Only Hook Overlays (no logo)")
    print(f"  {len(videos)} video(s) × 4 hooks each")
    print(f"{'#'*60}\n")

    for v in videos:
        if not v.exists():
            print(f"  ✗ Missing: {v}", flush=True)
            continue
        try:
            process_video(v)
        except Exception as e:
            print(f"  ✗ FAILED {v.name}: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Done. Text-only versions sent to Slack.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
