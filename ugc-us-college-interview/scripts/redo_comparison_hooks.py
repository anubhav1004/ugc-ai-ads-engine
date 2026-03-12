#!/usr/bin/env python3
"""
Redo comparison series hook overlays — text only, correct rival names, NO logos.

Fixes: us_cmp_01_vs_khan through us_cmp_05_vs_quizlet had Gauth logo incorrectly applied.
This version applies text-only hooks with each video's actual rival mentioned.
"""

import requests
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
IMPACT_FONT   = "/System/Library/Fonts/Supplemental/Impact.ttf"
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-us-comparison"
VW, VH        = 720, 1280

# Correct rival-specific hook text per video
COMPARISON_HOOKS = {
    "us_cmp_01_vs_khan": {
        "label": "PC vs Khan Academy",
        "hooks": [
            {"id": "h1", "lines": ["Khan Academy or Professor Curious?", "We asked real students.", "The answer surprised us."]},
            {"id": "h2", "lines": ["POV: comparing every free", "study app as a college junior"]},
            {"id": "h3", "lines": ["Khan Academy vs Professor Curious", "Real students. No script.", "Watch till the end."]},
            {"id": "h4", "lines": ["Why students are switching", "from Khan Academy to this app"]},
        ],
    },
    "us_cmp_02_vs_chegg": {
        "label": "PC vs Chegg",
        "hooks": [
            {"id": "h1", "lines": ["Chegg or Professor Curious?", "We asked 50 college students.", "One won every time."]},
            {"id": "h2", "lines": ["POV: paying $20/month for Chegg", "when this exists for free"]},
            {"id": "h3", "lines": ["Chegg vs Professor Curious", "Students had a clear answer.", "Watch till the end."]},
            {"id": "h4", "lines": ["Everyone's cancelling Chegg", "for this one study app", "and I had to find out why"]},
        ],
    },
    "us_cmp_03_vs_chatgpt": {
        "label": "PC vs ChatGPT",
        "hooks": [
            {"id": "h1", "lines": ["ChatGPT or Professor Curious?", "One gives answers.", "One gives understanding."]},
            {"id": "h2", "lines": ["POV: failing exams despite", "using ChatGPT every night"]},
            {"id": "h3", "lines": ["ChatGPT vs Professor Curious", "Which one actually teaches you?", "Real students. Real answers."]},
            {"id": "h4", "lines": ["Why top students switched", "from ChatGPT to Professor Curious"]},
        ],
    },
    "us_cmp_04_vs_tutors": {
        "label": "PC vs Private Tutors",
        "hooks": [
            {"id": "h1", "lines": ["$80/hr tutor or Professor Curious?", "Students had a clear answer.", "Watch till the end."]},
            {"id": "h2", "lines": ["POV: your parents pay $80/hr", "when this app costs nothing"]},
            {"id": "h3", "lines": ["Private tutors vs Professor Curious", "Real students. Honest opinions.", "You'll be surprised."]},
            {"id": "h4", "lines": ["The app that replaced", "a $300/month private tutor", "for college students"]},
        ],
    },
    "us_cmp_05_vs_quizlet": {
        "label": "PC vs Quizlet",
        "hooks": [
            {"id": "h1", "lines": ["Quizlet or Professor Curious?", "One helps you remember.", "The other makes you understand."]},
            {"id": "h2", "lines": ["POV: realizing Quizlet", "never actually taught you anything"]},
            {"id": "h3", "lines": ["Quizlet vs Professor Curious", "Students knew the difference.", "Watch till the end."]},
            {"id": "h4", "lines": ["Why students stopped using Quizlet", "and switched to Professor Curious"]},
        ],
    },
}


def draw_text_with_outline(draw, text, pos, font, fill, outline, outline_width=3):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build_text_overlay(hook_lines: list, tmp_path: Path) -> None:
    """Text only — no logos, no VS graphic."""
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
        draw_text_with_outline(draw, line, (tx, ty), hfont,
                               (255, 255, 255, 255), (0, 0, 0, 220), 4)

    overlay.save(str(tmp_path), "PNG")


def apply_hook(input_path: Path, hook: dict, out_dir: Path) -> Path:
    out_path = out_dir / f"{input_path.stem}_{hook['id']}.mp4"
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_png = Path(tf.name)

    build_text_overlay(hook["lines"], tmp_png)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path), "-i", str(tmp_png),
        "-filter_complex", "[1:v]scale=720:1280[ovr];[0:v][ovr]overlay=0:0[out]",
        "-map", "[out]", "-map", "0:a?",
        "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    tmp_png.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-400:]}")
    print(f"  [{hook['id']}] → {out_path.name} ({out_path.stat().st_size // 1024} KB)", flush=True)
    return out_path


def send_to_slack(video_path: Path, text: str) -> None:
    print(f"  [slack] Sending {video_path.name} ...", flush=True)
    helper = Path(__file__).resolve().parents[2] / "common" / "send_slack.py"
    result = subprocess.run([
        "python3", str(helper),
        "--channel-id", SLACK_CHANNEL,
        "--text", text,
        "--file", str(video_path),
    ], capture_output=True, text=True)
    resp = result.stdout.strip() or result.stderr.strip()
    print(f"  [slack] {'✓ Sent' if result.returncode == 0 else '✗ ' + resp[:80]}", flush=True)


def main():
    print(f"\n{'#'*60}")
    print(f"  Redo: Comparison Series — text-only hooks, correct rival names")
    print(f"  No logos. No Gauth VS PC overlay.")
    print(f"{'#'*60}\n")

    for run_id, cfg in COMPARISON_HOOKS.items():
        merged = OUTPUT_ROOT / run_id / f"{run_id}_merged.mp4"
        if not merged.exists():
            print(f"  ✗ Missing: {merged}", flush=True)
            continue

        out_dir = OUTPUT_ROOT / run_id / "hooks_fixed"
        out_dir.mkdir(exist_ok=True)

        print(f"\n[{cfg['label']}]", flush=True)
        print(f"  Input: {merged.name}", flush=True)

        for hook in cfg["hooks"]:
            try:
                out = apply_hook(merged, hook, out_dir)
                hook_text = " / ".join(hook["lines"])
                send_to_slack(
                    out,
                    f"🎬 *{cfg['label']}* (fixed — text only, no Gauth logo)\nHook: _{hook_text}_"
                )
            except Exception as e:
                print(f"  ✗ {hook['id']} failed: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Done. All comparison series resent with correct hooks.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
