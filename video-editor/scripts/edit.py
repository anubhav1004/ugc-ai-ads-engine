#!/usr/bin/env python3
"""
UGC Video Editor — Post-processing for AI-generated ads.

Turns raw Sora clips into polished UGC ads:
  - Warm cinematic color grading
  - Vignette
  - Cross-fade transitions between clips (xfade)
  - Hook text on establishing shot (first 3s)
  - CTA text on outro
  - App logo bug in corner
  - Optional 2.5s end card
  - Audio normalization (loudnorm)

Usage:
  python3 edit.py --run-dir ~/.openclaw/workspace/output/ugc-experiments/exp_01_ek_raat
  python3 edit.py --run-dir <dir> --hook-text "Raat ke 11 baje. Akela." --style cinematic
  python3 edit.py --run-dir <dir> --logo ~/ugc-ai-ads-engine/assets/pc_logo.png --end-card --send-slack
  python3 edit.py --run-dir <dir> --transition wipeleft --no-cta
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Constants ─────────────────────────────────────────────────────────────────

SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
FADE_DUR      = 0.3  # seconds for cross-fade / acrossfade

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",       # macOS (punchy, UGC-style)
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",   # macOS
    "/System/Library/Fonts/Helvetica.ttc",                 # macOS
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",     # Ubuntu
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Ubuntu
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",      # Ubuntu
]

STYLE_GRADES = {
    # Warm, golden hour feel — best for India/Kota emotional ads
    "warm": (
        "colorbalance=rs=0.08:gs=0.03:bs=-0.08:rm=0.04:gm=0:bm=-0.04,"
        "eq=contrast=1.1:brightness=0.01:saturation=0.88"
    ),
    # Desaturated, filmic — good for dramatic moments
    "cinematic": (
        "colorbalance=rs=0.05:gs=0:bs=-0.08:rm=0.03:gm=0:bm=-0.03,"
        "eq=contrast=1.15:brightness=-0.01:saturation=0.72"
    ),
    # Cool blue tones — good for US college ads
    "cool": (
        "colorbalance=rs=-0.05:gs=0:bs=0.08:rm=-0.03:gm=0:bm=0.04,"
        "eq=contrast=1.08:brightness=0:saturation=0.85"
    ),
    # Minimal touch — just slight contrast bump
    "neutral": "eq=contrast=1.05:brightness=0:saturation=0.95",
}

# ── Utilities ─────────────────────────────────────────────────────────────────

def run_cmd(cmd: list, label: str = "") -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\n[ERROR] {label}")
        print(result.stderr[-1000:])
        sys.exit(1)
    if label:
        print(f"  ✓ {label}", flush=True)


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def load_pil_font(size: int) -> ImageFont.FreeTypeFont:
    """Load best available bold font for Pillow at given size."""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_video_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) of video via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    w, h = result.stdout.strip().split(",")
    return int(w), int(h)


def create_text_overlay(
    text: str,
    video_w: int,
    video_h: int,
    y_ratio: float,
    font_size: int,
    tmp_dir: Path,
    tag: str = "",
) -> Path:
    """
    Create a transparent PNG (video_w x video_h) with styled text at y_ratio.
    Returns the PNG path.
    """
    img  = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = load_pil_font(font_size)

    # Measure text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (video_w - tw) // 2
    y = int(video_h * y_ratio)

    # Semi-transparent black pill behind text
    pad = 18
    draw.rounded_rectangle(
        [x - pad, y - pad, x + tw + pad, y + th + pad],
        radius=10,
        fill=(0, 0, 0, 150),
    )
    # White text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    name = tag if tag else f"{hash(text) & 0xFFFFFF:06x}"
    out = tmp_dir / f"overlay_{name}.png"
    img.save(str(out))
    return out


# ── Pass 1: Per-clip processing ───────────────────────────────────────────────

def process_clip(
    in_path: Path,
    out_path: Path,
    grade: str,
    clip_type: str,
    hook_text: str,
    cta_text: str,
    logo_path: Path | None,
    tmp_dir: Path,
) -> None:
    """
    Per-clip: color grade + vignette + Pillow text overlays + logo bug.
    Uses filter_complex to chain all operations in one ffmpeg pass.
    """
    video_w, video_h = get_video_dimensions(in_path)

    # --- Build inputs list and collect overlay PNGs ---
    extra_inputs = []  # list of Path

    # Text overlays: (png_path, enable_expr)
    text_overlays = []

    if clip_type == "establishing" and hook_text:
        png = create_text_overlay(
            hook_text, video_w, video_h,
            y_ratio=0.10, font_size=int(video_h * 0.042),
            tmp_dir=tmp_dir, tag="hook",
        )
        text_overlays.append((png, "between(t,0,3)"))

    if clip_type == "outro" and cta_text:
        png = create_text_overlay(
            cta_text, video_w, video_h,
            y_ratio=0.80, font_size=int(video_h * 0.033),
            tmp_dir=tmp_dir, tag="cta",
        )
        text_overlays.append((png, "1"))  # always visible

    for png, _ in text_overlays:
        extra_inputs.append(png)

    has_logo = logo_path and logo_path.exists()
    if has_logo:
        extra_inputs.append(logo_path)

    # --- Build filter_complex ---
    filters = []
    # Index 0 = video clip. Extra inputs start at index 1.
    overlay_input_base = 1

    # Step 1: color grade + vignette
    filters.append(f"[0:v]{grade},vignette=PI/5[graded0]")
    current = "graded0"

    # Step 2: text overlays
    for i, (_, enable_expr) in enumerate(text_overlays):
        inp_idx = overlay_input_base + i
        out_tag = f"txt{i}"
        filters.append(
            f"[{current}][{inp_idx}:v]overlay=0:0:enable='{enable_expr}'[{out_tag}]"
        )
        current = out_tag

    # Step 3: logo bug (bottom-right, small)
    if has_logo:
        logo_idx = overlay_input_base + len(text_overlays)
        logo_size = max(60, video_w // 10)  # ~10% of width
        logo_margin = 14
        filters.append(f"[{logo_idx}:v]scale={logo_size}:{logo_size}[logo_s]")
        filters.append(
            f"[{current}][logo_s]overlay=W-w-{logo_margin}:H-w-{logo_margin}[final]"
        )
        current = "final"

    fc = ";".join(filters)

    cmd = ["ffmpeg", "-y", "-i", str(in_path)]
    for p in extra_inputs:
        cmd += ["-i", str(p)]

    cmd += [
        "-filter_complex", fc,
        "-map", f"[{current}]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out_path),
    ]

    run_cmd(cmd, f"grade+overlay: {in_path.name}")


# ── End card ──────────────────────────────────────────────────────────────────

def create_end_card(
    out_path: Path,
    product_name: str,
    logo_path: Path | None,
    video_w: int,
    video_h: int,
    tmp_dir: Path,
    duration: float = 2.5,
) -> None:
    """Generate a black end card with product name + store line via Pillow overlay."""
    # Create the card as a PNG using Pillow
    card = Image.new("RGB", (video_w, video_h), (13, 13, 13))
    draw = ImageDraw.Draw(card)

    name_font  = load_pil_font(int(video_h * 0.048))
    store_font = load_pil_font(int(video_h * 0.025))

    # Product name — centered, ~48% down
    nbbox = draw.textbbox((0, 0), product_name, font=name_font)
    nw = nbbox[2] - nbbox[0]
    nh = nbbox[3] - nbbox[1]
    draw.text(((video_w - nw) // 2, int(video_h * 0.48)), product_name, font=name_font, fill=(255, 255, 255))

    # Store line — centered, ~60% down
    store_text = "App Store  ·  Google Play"
    sbbox = draw.textbbox((0, 0), store_text, font=store_font)
    sw = sbbox[2] - sbbox[0]
    draw.text(((video_w - sw) // 2, int(video_h * 0.60)), store_text, font=store_font, fill=(200, 200, 200))

    # Paste logo if available (~26% down, centered)
    if logo_path and logo_path.exists():
        logo_size = int(video_w * 0.22)
        logo_img  = Image.open(str(logo_path)).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
        paste_x   = (video_w - logo_size) // 2
        paste_y   = int(video_h * 0.26)
        card.paste(logo_img, (paste_x, paste_y), mask=logo_img)

    card_png = tmp_dir / "end_card.png"
    card.save(str(card_png))

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(card_png),
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        "-vf", "fps=24",
        str(out_path),
    ]

    run_cmd(cmd, f"end card ({duration}s)")


# ── Pass 2: Xfade stitch + audio normalize ────────────────────────────────────

def xfade_pair(
    in_a: Path, in_b: Path, out: Path,
    transition: str, offset: float,
) -> None:
    """Xfade two clips: video xfade + audio acrossfade in a single pass.
    Normalizes timebase to 24fps to avoid timebase mismatch errors.
    """
    fc = (
        # Normalize both inputs to 24fps (fixes timebase mismatch after multiple xfades)
        f"[0:v]fps=24[v0];[1:v]fps=24[v1];"
        f"[v0][v1]xfade=transition={transition}:duration={FADE_DUR}:offset={offset:.3f}[vout];"
        f"[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];"
        f"[a0][a1]acrossfade=d={FADE_DUR}[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_a), "-i", str(in_b),
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out),
    ]
    run_cmd(cmd, f"xfade: {in_a.name} → {in_b.name}")


def xfade_stitch(
    clip_paths: list,
    durations: list,
    output_path: Path,
    transition: str = "fade",
) -> None:
    """
    Stitch clips with xfade transitions using pairwise merge.
    Each step: (accumulated_result + next_clip) → new result.
    Final step: apply loudnorm.
    """
    n = len(clip_paths)

    if n == 1:
        cmd = [
            "ffmpeg", "-y", "-i", str(clip_paths[0]),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
            str(output_path),
        ]
        run_cmd(cmd, "single clip → output")
        return

    tmp_dir = output_path.parent / "xfade_tmp"
    tmp_dir.mkdir(exist_ok=True)

    current_path = clip_paths[0]
    current_dur  = durations[0]

    for i in range(1, n):
        next_path = clip_paths[i]
        offset    = max(0.0, current_dur - FADE_DUR)
        is_last   = (i == n - 1)

        if is_last:
            # Final merge goes directly to output
            out = output_path
        else:
            out = tmp_dir / f"stage_{i:02d}.mp4"

        xfade_pair(current_path, next_path, out, transition, offset)

        # Update current duration for next iteration
        current_dur  = ffprobe_duration(out)
        current_path = out

    # Apply loudnorm as a final single pass (copy video, re-encode audio)
    loudnorm_out = output_path.parent / f"{output_path.stem}_ln.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", str(output_path),
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(loudnorm_out),
    ]
    run_cmd(cmd, "loudnorm pass")
    loudnorm_out.replace(output_path)

    print(f"  ✓ stitch complete: {output_path.name}")


# ── Orchestrator ──────────────────────────────────────────────────────────────

def infer_clip_type(filename: str) -> str:
    """Infer clip type from filename convention (clip_01_establishing.mp4 etc.)."""
    stem = Path(filename).stem.lower()
    if "establishing" in stem:
        return "establishing"
    if "outro" in stem:
        return "outro"
    # person clips: clip_02_p01 etc.
    for part in stem.split("_"):
        if part.startswith("p") and part[1:].isdigit():
            return part
    return "person"


def load_manifest(run_dir: Path) -> tuple[dict, list]:
    """
    Load manifest.json if present, otherwise infer from clips/ directory.
    Returns (manifest_dict, ordered_list_of_(clip_type, clip_path)).
    """
    clips_dir = run_dir / "clips"
    manifest_path = run_dir / "manifest.json"

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        ordered = []
        for entry in manifest.get("clips", []):
            clip_file = clips_dir / entry["file"]
            if clip_file.exists():
                ordered.append((entry.get("clip", "unknown"), clip_file))
            else:
                print(f"  [WARN] Missing clip: {entry['file']}")
        return manifest, ordered

    # Fallback: scan clips/ directory, sort by name
    if not clips_dir.is_dir():
        sys.exit(f"[ERROR] No clips/ directory in {run_dir}")

    clip_files = sorted(clips_dir.glob("*.mp4"))
    if not clip_files:
        sys.exit(f"[ERROR] No .mp4 files in {clips_dir}")

    print(f"  [info] No manifest.json — inferring {len(clip_files)} clips from clips/ directory")
    ordered = [(infer_clip_type(p.name), p) for p in clip_files]
    manifest = {"run_id": run_dir.name, "product": "Professor Curious"}
    return manifest, ordered


def edit_run(args) -> Path:
    run_dir = Path(args.run_dir).expanduser().resolve()

    grade     = STYLE_GRADES.get(args.style, STYLE_GRADES["warm"])
    logo_path = Path(args.logo).expanduser() if args.logo else None
    cta_text  = "" if args.no_cta else args.cta_text

    manifest, ordered = load_manifest(run_dir)
    run_id = manifest.get("run_id", run_dir.name)

    print(f"\n{'='*55}")
    print(f"  UGC Video Editor")
    print(f"  Run     : {run_id}")
    print(f"  Style   : {args.style}")
    print(f"  Trans   : {args.transition}")
    print(f"  Logo    : {logo_path.name if logo_path and logo_path.exists() else 'none'}")
    print(f"  Hook    : {args.hook_text or '(none)'}")
    print(f"  CTA     : {cta_text or '(none)'}")
    print(f"  End card: {'yes' if args.end_card else 'no'}")
    print(f"{'='*55}\n")

    if not ordered:
        sys.exit("[ERROR] No clips found.")

    print(f"[1/3] Per-clip processing ({len(ordered)} clips)...")
    processed_dir = run_dir / "processed"
    tmp_dir       = run_dir / "tmp"
    processed_dir.mkdir(exist_ok=True)
    tmp_dir.mkdir(exist_ok=True)

    # Get video dimensions from first clip
    first_clip = ordered[0][1]
    video_w, video_h = get_video_dimensions(first_clip)

    processed = []
    for clip_type, clip_path in ordered:
        out = processed_dir / clip_path.name
        process_clip(
            in_path=clip_path,
            out_path=out,
            grade=grade,
            clip_type=clip_type,
            hook_text=args.hook_text,
            cta_text=cta_text,
            logo_path=logo_path,
            tmp_dir=tmp_dir,
        )
        processed.append(out)

    # Optionally append end card
    if args.end_card:
        end_card_path = processed_dir / "end_card.mp4"
        print("\n[2/3] Creating end card...")
        product = manifest.get("product", "Professor Curious")
        create_end_card(end_card_path, product, logo_path, video_w, video_h, tmp_dir)
        processed.append(end_card_path)
    else:
        print("\n[2/3] Skipping end card.")

    # Get durations for xfade offset calculation
    durations = [ffprobe_duration(p) for p in processed]

    print(f"\n[3/3] Stitching with '{args.transition}' transitions...")
    edited_path = run_dir / f"{run_id}_edited.mp4"
    xfade_stitch(processed, durations, edited_path, args.transition)

    print(f"\n{'='*55}")
    print(f"  DONE: {edited_path}")
    print(f"{'='*55}\n")

    return edited_path


# ── Slack ─────────────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path, label: str) -> None:
    print(f"[slack] Sending: {label}")
    helper = Path(__file__).resolve().parents[2] / "common" / "send_slack.py"
    result = subprocess.run([
        "python3", str(helper),
        "--channel-id", SLACK_CHANNEL,
        "--text", f"*[EDITED]* {label}",
        "--file", str(video_path),
    ], capture_output=True, text=True)
    resp = result.stdout.strip() or result.stderr.strip()
    print(f"  [slack] {resp}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UGC Video Post-Processing Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--run-dir",    required=True,
                        help="Run directory (contains manifest.json + clips/)")
    parser.add_argument("--hook-text",  default="",
                        help="Big text overlay on establishing shot (first 3s)")
    parser.add_argument("--cta-text",   default="Download Professor Curious",
                        help="CTA text overlaid on outro clip")
    parser.add_argument("--no-cta",     action="store_true",
                        help="Disable CTA text on outro")
    parser.add_argument("--logo",       default="",
                        help="Path to logo PNG for persistent corner bug")
    parser.add_argument("--style",      default="warm",
                        choices=list(STYLE_GRADES),
                        help="Color grade style (default: warm)")
    parser.add_argument("--transition", default="fade",
                        help="xfade transition type: fade, wipeleft, slideleft, "
                             "circlecrop, diagtl, dissolve (default: fade)")
    parser.add_argument("--end-card",   action="store_true",
                        help="Append a 2.5s branded end card")
    parser.add_argument("--send-slack", action="store_true",
                        help="Send edited video to Slack when done")
    args = parser.parse_args()

    edited_path = edit_run(args)

    if args.send_slack:
        label = f"{Path(args.run_dir).name} — {args.style} grade, {args.transition} transitions"
        send_to_slack(edited_path, label)


if __name__ == "__main__":
    main()
