#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/reaction-hook-demo")
OUTPUT = ROOT / "output"
ASSETS = ROOT / "assets"

REACTION = Path(
    "/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/india-raw-footage/reaction-formats/reference-matched-sample/output/reference_matched_frontcam_reaction_json_prompt_v2_american_blonde_girl_4s_aggressive_pickup.mp4"
)
DEMO_1 = Path("/Users/anubhavmishra/Downloads/761f2bb3b84a4003a9744b4e5b45a4f2 (1).MP4")

TEXT_FONT = "/System/Library/Fonts/Helvetica.ttc"
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"

W = 720
H = 1280
BAR_Y = 220
BAR_H = 128
TEXT_SIZE = 36
EMOJI_SIZE = 32
MAX_TEXT_W = 620


def is_emoji(ch: str) -> bool:
    return ord(ch) > 0x1F000


def split_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    buff = ""
    for ch in text:
        if ch == " ":
            if buff:
                tokens.append(buff)
                buff = ""
            tokens.append(" ")
        elif is_emoji(ch):
            if buff:
                tokens.append(buff)
                buff = ""
            tokens.append(ch)
        else:
            buff += ch
    if buff:
        tokens.append(buff)
    return tokens


def token_width(draw: ImageDraw.ImageDraw, token: str, text_font, emoji_font) -> int:
    font = emoji_font if any(is_emoji(ch) for ch in token) else text_font
    bbox = draw.textbbox((0, 0), token, font=font, embedded_color=True)
    return bbox[2] - bbox[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, text_font, emoji_font) -> list[list[str]]:
    tokens = split_tokens(text)
    lines: list[list[str]] = [[]]
    line_w = 0
    for token in tokens:
        w = token_width(draw, token, text_font, emoji_font)
        if lines[-1] and line_w + w > MAX_TEXT_W and token != " ":
            lines.append([])
            line_w = 0
            if token == " ":
                continue
        lines[-1].append(token)
        line_w += w
    return [line for line in lines if line]


def draw_mixed_line(draw: ImageDraw.ImageDraw, tokens: list[str], y: int, text_font, emoji_font) -> None:
    widths = [token_width(draw, token, text_font, emoji_font) for token in tokens]
    total = sum(widths)
    x = (W - total) // 2
    for token, width in zip(tokens, widths):
        font = emoji_font if any(is_emoji(ch) for ch in token) else text_font
        draw.text((x, y), token, fill=(255, 255, 255, 255), font=font, embedded_color=True)
        x += width


def make_overlay(text: str, out_path: Path) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, BAR_Y, W, BAR_Y + BAR_H), fill=(0, 0, 0, 160))
    text_font = ImageFont.truetype(TEXT_FONT, TEXT_SIZE)
    emoji_font = ImageFont.truetype(EMOJI_FONT, EMOJI_SIZE)
    lines = wrap_text(draw, text, text_font, emoji_font)
    line_h = 42
    start_y = BAR_Y + (BAR_H - line_h * len(lines)) // 2 - 2
    for i, line in enumerate(lines):
        draw_mixed_line(draw, line, start_y + i * line_h, text_font, emoji_font)
    img.save(out_path)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def render_segment(src: Path, overlay: Path, out_path: Path, duration: float | None = None) -> None:
    cmd = [
        "/opt/homebrew/bin/ffmpeg",
        "-y",
        "-i",
        str(src),
        "-i",
        str(overlay),
    ]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += [
        "-filter_complex",
        "[0:v][1:v]overlay=0:0",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        str(out_path),
    ]
    run(cmd)


def concat_segments(parts: list[Path], out_path: Path) -> None:
    run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i",
            str(parts[0]),
            "-i",
            str(parts[1]),
            "-filter_complex",
            "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(out_path),
        ]
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    overlays = {
        "reaction": "I just found the study app everyone's gatekeeping 😳📚",
        "demo1": "This app is called Professor Curious 🤯📱",
    }
    overlay_paths = {}
    for key, text in overlays.items():
        path = ASSETS / f"{key}_hook.png"
        make_overlay(text, path)
        overlay_paths[key] = path

    reaction_out = OUTPUT / "segment_01_reaction.mp4"
    demo1_out = OUTPUT / "segment_02_demo1.mp4"
    final_out = OUTPUT / "professor_curious_reaction_plus_demo.mp4"

    render_segment(REACTION, overlay_paths["reaction"], reaction_out, 4.0)
    render_segment(DEMO_1, overlay_paths["demo1"], demo1_out, None)
    concat_segments([reaction_out, demo1_out], final_out)
    print(final_out)


if __name__ == "__main__":
    main()
