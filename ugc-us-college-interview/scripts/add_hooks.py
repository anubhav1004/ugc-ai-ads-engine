#!/usr/bin/env python3
"""
Add Instagram/TikTok-style text hooks + centered VS logo overlay to a video.

Strategy:
  1. Use Pillow to render a 720x1280 RGBA overlay PNG (text + logos)
  2. Use ffmpeg to composite the overlay onto the video

Layout:
  - TOP: Bold hook text (2-3 lines, white, black outline, Impact font)
  - MIDDLE: [GAUTH logo] VS [PC logo] — centered horizontally

Creates 3-4 hook variations from a single input video. Sends each to Slack.

Usage:
  python3 add_hooks.py <input_video.mp4>
  python3 add_hooks.py  (auto-picks latest street_direct merged video)
"""

import requests
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
ASSETS_DIR    = Path.home() / "ugc-ai-ads-engine" / "assets"
GAUTH_LOGO    = ASSETS_DIR / "gauth_logo.png"
PC_LOGO       = ASSETS_DIR / "pc_logo.png"
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-hooks"

IMPACT_FONT   = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BOLD    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# Video dimensions (portrait)
VW, VH = 720, 1280

# ── Hook variations ────────────────────────────────────────────────────────────
# Each hook is a list of text lines (max 3) shown at the top of the frame
# Style: Instagram/TikTok — curiosity-gap, POV, or pattern-interrupt formats

HOOKS = [
    {
        "id":    "hook_01_asked",
        "lines": [
            "I asked 50 college students:",
            "Gauth or Professor Curious?",
            "One app won every single time",
        ],
        "label": "Hook 1 — I asked format",
    },
    {
        "id":    "hook_02_pov",
        "lines": [
            "POV: random college students",
            "get asked which study app",
            "they actually use",
        ],
        "label": "Hook 2 — POV format",
    },
    {
        "id":    "hook_03_comparison",
        "lines": [
            "Gauth vs Professor Curious",
            "Real students. No script.",
            "Watch till the end",
        ],
        "label": "Hook 3 — Comparison format",
    },
    {
        "id":    "hook_04_switching",
        "lines": [
            "Everyone's switching from Gauth",
            "to this one study app",
            "and I had to find out why",
        ],
        "label": "Hook 4 — FOMO / switching format",
    },
]

# ── Pillow overlay builder ─────────────────────────────────────────────────────

def draw_text_with_outline(draw, text, pos, font, fill, outline, outline_width=3):
    """Draw text with a solid outline (stroke) for readability."""
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build_overlay_png(hook_lines: list, tmp_path: Path) -> None:
    """
    Create a 720x1280 RGBA PNG overlay:
    - Top: hook text lines (Impact, white + black outline)
    - Middle (y≈560): Gauth logo | VS | PC logo — centered
    """
    overlay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    # ── Logo layout ───────────────────────────────────────────────────────────
    logo_size = 100
    gap       = 70           # horizontal gap between logos (for VS text)
    total_w   = logo_size * 2 + gap
    start_x   = (VW - total_w) // 2   # 225
    gauth_x   = start_x
    pc_x      = start_x + logo_size + gap
    logo_y    = 540
    label_y   = logo_y + logo_size + 6

    # Gauth logo
    gauth_img = Image.open(GAUTH_LOGO).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    overlay.paste(gauth_img, (gauth_x, logo_y), gauth_img)

    # PC logo
    pc_img = Image.open(PC_LOGO).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    overlay.paste(pc_img, (pc_x, logo_y), pc_img)

    # VS text — centered between logos
    try:
        vs_font    = ImageFont.truetype(IMPACT_FONT, 34)
        label_font = ImageFont.truetype(ARIAL_BOLD, 20)
    except Exception:
        vs_font    = ImageFont.load_default()
        label_font = ImageFont.load_default()

    vs_text = "VS"
    vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
    vs_w    = vs_bbox[2] - vs_bbox[0]
    vs_x    = start_x + logo_size + (gap // 2) - (vs_w // 2)
    vs_y    = logo_y + (logo_size // 2) - 17
    draw_text_with_outline(draw, vs_text, (vs_x, vs_y), vs_font, (255, 255, 255, 255), (0, 0, 0, 200), 3)

    # "GAUTH" label
    g_lbl    = "GAUTH"
    g_bbox   = draw.textbbox((0, 0), g_lbl, font=label_font)
    g_lbl_w  = g_bbox[2] - g_bbox[0]
    g_lbl_x  = gauth_x + (logo_size // 2) - (g_lbl_w // 2)
    draw_text_with_outline(draw, g_lbl, (g_lbl_x, label_y), label_font, (255, 255, 255, 255), (0, 0, 0, 200), 2)

    # "PROF. CURIOUS" label
    pc_lbl   = "PROF. CURIOUS"
    pc_bbox  = draw.textbbox((0, 0), pc_lbl, font=label_font)
    pc_lbl_w = pc_bbox[2] - pc_bbox[0]
    pc_lbl_x = pc_x + (logo_size // 2) - (pc_lbl_w // 2)
    draw_text_with_outline(draw, pc_lbl, (pc_lbl_x, label_y), label_font, (255, 255, 255, 255), (0, 0, 0, 200), 2)

    # ── Hook text (top) ───────────────────────────────────────────────────────
    hook_y_starts  = [40, 100, 155]
    hook_fontsizes = [52, 44, 38]

    for i, line in enumerate(hook_lines[:3]):
        try:
            hfont = ImageFont.truetype(IMPACT_FONT, hook_fontsizes[i])
        except Exception:
            hfont = ImageFont.load_default()

        bbox  = draw.textbbox((0, 0), line, font=hfont)
        tw    = bbox[2] - bbox[0]
        tx    = (VW - tw) // 2
        ty    = hook_y_starts[i]

        # Semi-transparent dark pill behind text
        pad = 10
        draw.rounded_rectangle(
            [tx - pad, ty - pad//2, tx + tw + pad, ty + (bbox[3] - bbox[1]) + pad//2],
            radius=8,
            fill=(0, 0, 0, 100),
        )
        draw_text_with_outline(draw, line, (tx, ty), hfont, (255, 255, 255, 255), (0, 0, 0, 220), 4)

    overlay.save(str(tmp_path), "PNG")


def apply_hook(input_path: Path, hook: dict, out_dir: Path) -> Path:
    out_path = out_dir / f"{input_path.stem}_{hook['id']}.mp4"

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_png = Path(tf.name)

    print(f"  [{hook['id']}] Building overlay PNG...", flush=True)
    build_overlay_png(hook["lines"], tmp_png)

    print(f"  [{hook['id']}] Compositing...", flush=True)
    filt = "[1:v]scale=720:1280[ovr];[0:v][ovr]overlay=0:0[out]"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(tmp_png),
        "-filter_complex", filt,
        "-map", "[out]",
        "-map", "0:a?",
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


def send_to_slack(video_path: Path, label: str, hook_label: str) -> None:
    print(f"  [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    requests.post(SLACK_URL, data={
        "channel_id": SLACK_CHANNEL,
        "text": (
            f"🎬 *{label}*\n"
            f"_{hook_label}_\n"
            f"Centre: Gauth VS Professor Curious logos. Top: Instagram-style text hook."
        ),
    })
    print(f"  [slack] {'✓ Sent' if resp.ok else '✗ ' + resp.text[:100]}", flush=True)


def find_latest_merged() -> Path:
    """Auto-find the most recently created merged video in street-direct output."""
    root = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-us-direct"
    videos = sorted(root.rglob("*_merged.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not videos:
        raise FileNotFoundError(f"No merged videos found in {root}")
    return videos[0]


def main():
    # ── Pick input video ─────────────────────────────────────────────
    if len(sys.argv) > 1:
        input_video = Path(sys.argv[1])
    else:
        input_video = find_latest_merged()

    if not input_video.exists():
        sys.exit(f"ERROR: Video not found: {input_video}")

    print(f"\n{'#'*60}")
    print(f"  Hook Overlay Generator")
    print(f"  Input : {input_video.name}")
    print(f"  Hooks : {len(HOOKS)} variations")
    print(f"  Layout: Gauth VS Prof. Curious logo (centre) + hook text (top)")
    print(f"{'#'*60}\n")

    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}")

    out_dir = OUTPUT_ROOT / input_video.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    label = input_video.stem.replace("_", " ").replace("merged", "").strip()

    for hook in HOOKS:
        try:
            out = apply_hook(input_video, hook, out_dir)
            send_to_slack(out, label, hook["label"])
        except Exception as e:
            print(f"  ✗ FAILED {hook['id']}: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Done. {len(HOOKS)} hook variations sent to Slack.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
