#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/reaction-ads-v2")
VARIANTS = ROOT / "variants.json"
AZURE_SCRIPT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/india-raw-footage/scripts/generate_azure_sora_clip.py")
MOTION_SCRIPT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/india-raw-footage/scripts/apply_phone_pickup_motion.py")
SLACK_HELPER = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/common/send_slack.py")
DEMO = Path("/Users/anubhavmishra/Downloads/761f2bb3b84a4003a9744b4e5b45a4f2 (1).MP4")
MUSIC_BED = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/reaction-hook-demo/assets/trending_style_bed.wav")

TEXT_FONT = "/System/Library/Fonts/Helvetica.ttc"
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
W = 720
H = 1280
BAR_Y = 220
BAR_H = 128
TEXT_SIZE = 36
EMOJI_SIZE = 32
MAX_TEXT_W = 620


def run(cmd: list[str], env: dict | None = None) -> None:
    subprocess.run(cmd, check=True, env=env)


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


def draw_line(draw: ImageDraw.ImageDraw, tokens: list[str], y: int, text_font, emoji_font) -> None:
    widths = [token_width(draw, token, text_font, emoji_font) for token in tokens]
    x = (W - sum(widths)) // 2
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
        draw_line(draw, line, start_y + i * line_h, text_font, emoji_font)
    img.save(out_path)


def write_prompt(variant: dict, out_path: Path) -> None:
    prompt = {
        "format": "raw_front_phone_camera_footage",
        "aspect_ratio": "9:16",
        "test_type": "stronger_shock_then_device_pickup",
        "hard_rules": [
            "this recording is the phone itself",
            "there is no second phone anywhere",
            "the front camera of this same phone is already recording",
            "do not show another phone in her hand",
            "do not delay the shock reaction past the third second",
            "the hand-to-mouth gesture must be visible",
            "the phone pickup motion must happen after the shock lands",
            "no cinematic stabilization",
            "no fake zoom"
        ],
        "goal": "Create raw front-camera footage where the subject reacts with a bigger, clearer shock by the third second: eyes much wider, eyebrows lifted higher, and mouth opening wider before one hand comes toward the mouth. Only after that she grabs and lifts the same recording phone so the frame physically shifts into a natural handheld pickup.",
        "scene": {
            "subject": variant["subject"],
            "appearance": variant["hair"],
            "setting": variant["room"],
            "wardrobe": "simple neutral t-shirt",
            "background_details": [
                "plain wall",
                "bed",
                "dresser",
                "slightly open door"
            ],
            "lighting": "soft practical room light, ordinary and unstyled",
            "style": "real raw front phone camera footage, not aesthetic"
        },
        "camera": {
            "lens_state": "front camera selfie footage only",
            "look": [
                "raw phone look",
                "natural handheld imperfections",
                "no smooth rig motion",
                "tiny exposure breathing is okay"
            ]
        },
        "timeline": [
            {
                "time": "0.0-1.1",
                "beats": [
                    "the phone is resting and already recording from the front camera",
                    "medium close framing",
                    "she reads something on this phone screen",
                    "minimal movement"
                ]
            },
            {
                "time": "1.1-3.0",
                "beats": [
                    "the shock reaction clearly builds and lands within this window",
                    "eyes open much wider than before",
                    "eyebrows lift higher and stay raised",
                    "mouth opens noticeably wider in disbelief",
                    "the reaction should feel bigger and easier to read even on mute",
                    "one hand clearly comes up and covers part of her mouth only after the mouth opens wide",
                    "hold the wide-eyed, open-mouth shocked expression by the third second"
                ]
            },
            {
                "time": "3.0-4.0",
                "beats": [
                    "only now she reaches toward the lens and grabs this same recording phone",
                    "fingers briefly cover part of the lens edge",
                    "the frame jolts slightly because the recording phone is being picked up",
                    "the angle changes from resting to handheld"
                ]
            }
        ],
        "priority_notes": [
            "make the facial reaction stronger than previous versions",
            "the mouth should open wider before the hand reaches the mouth",
            "the eyes should read very wide and alert by second 3",
            "the pickup motion must happen after the reaction, not before",
            "the audience must feel that the recording phone itself gets picked up"
        ],
        "audio": {
            "room_tone": "natural room tone only",
            "music": "none",
            "dialogue": "none"
        }
    }
    out_path.write_text(json.dumps(prompt, indent=2))


def render_variant(variant: dict, env: dict) -> Path:
    variant_dir = ROOT / variant["id"]
    prompts_dir = variant_dir / "prompts"
    assets_dir = variant_dir / "assets"
    output_dir = variant_dir / "output"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = prompts_dir / "reaction.json"
    raw_clip = output_dir / "reaction_raw.mp4"
    motion_clip = output_dir / "reaction_motion.mp4"
    reaction_overlay = assets_dir / "reaction_hook.png"
    demo_overlay = assets_dir / "demo_hook.png"
    reaction_segment = output_dir / "segment_01_reaction.mp4"
    demo_segment = output_dir / "segment_02_demo.mp4"
    final_out = output_dir / "final.mp4"
    final_music_out = output_dir / "final_trending_audio.mp4"

    write_prompt(variant, prompt_path)
    make_overlay(variant["top_hook"], reaction_overlay)
    make_overlay(variant["demo_hook"], demo_overlay)

    run(
        [
            "python3",
            str(AZURE_SCRIPT),
            "--prompt-file", str(prompt_path),
            "--out", str(raw_clip),
            "--seconds", "4",
            "--size", "720x1280"
        ],
        env=env,
    )
    run(
        [
            "python3",
            str(MOTION_SCRIPT),
            "--input", str(raw_clip),
            "--output", str(motion_clip),
            "--start", "2.2",
            "--duration", "1.1",
            "--mode", "logical"
        ]
    )
    run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i", str(motion_clip),
            "-i", str(reaction_overlay),
            "-t", "4.0",
            "-filter_complex", "[0:v][1:v]overlay=0:0",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-an",
            str(reaction_segment),
        ]
    )
    run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i", str(DEMO),
            "-i", str(demo_overlay),
            "-filter_complex", "[0:v][1:v]overlay=0:0",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "48000",
            str(demo_segment),
        ]
    )
    run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i", str(reaction_segment),
            "-i", str(demo_segment),
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            str(final_out),
        ]
    )
    run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i", str(final_out),
            "-i", str(MUSIC_BED),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(final_music_out),
        ]
    )
    return final_music_out


def send_to_slack(video_path: Path, label: str) -> None:
    run(
        [
            "python3",
            str(SLACK_HELPER),
            "--channel-id", "C0AHDH474LX",
            "--text", label,
            "--file", str(video_path),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--send-slack", action="store_true")
    args = parser.parse_args()

    env = os.environ.copy()
    required = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_SORA_MODEL"]
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    ROOT.mkdir(parents=True, exist_ok=True)
    variants = json.loads(VARIANTS.read_text())
    for variant in variants[args.start : args.start + args.limit]:
        final_path = render_variant(variant, env)
        print(final_path)
        if args.send_slack:
            send_to_slack(
                final_path,
                f"Reaction ads v2 — {variant['id']} — {variant['top_hook']}",
            )


if __name__ == "__main__":
    main()
