#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/reaction-pipeline")
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


PRESETS: dict[str, dict] = {
    "front-selfie": {
        "pickup_generation": "prompt_plus_post",
        "format": "raw_front_phone_camera_footage",
        "test_type": "stronger_shock_then_device_pickup",
        "goal": "Create raw front-camera footage where the subject reacts with a bigger, clearer shock by the third second: eyes much wider, eyebrows lifted higher, and mouth opening wider before one hand comes toward the mouth. Only after that she grabs and lifts the same recording phone so the frame physically shifts into a natural handheld pickup.",
        "scene_style": "real raw front phone camera footage, not aesthetic",
        "camera_look": [
            "front camera selfie footage only",
            "raw phone look",
            "natural handheld imperfections",
            "no smooth rig motion",
            "tiny exposure breathing is okay"
        ],
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
        "motion": {"start": "2.2", "duration": "1.1", "mode": "logical"},
    },
    "side-table": {
        "pickup_generation": "post_only",
        "format": "raw_phone_camera_table_angle_footage",
        "test_type": "side_table_reaction_then_post_pickup",
        "goal": "Create raw phone footage where the same recording phone is resting on a study table at a slight side angle. The subject is seated at the table, reacts only to what is visible on this recording phone, turns toward this same phone, and leans forward with a bigger, clearer shock by the third second. Do not attempt to generate the pickup inside the shot. The pickup of this exact recording phone will be added later in post, so the generated clip must stay visually continuous and must never imply any second phone.",
        "scene_style": "real raw phone footage from a table view, not aesthetic",
        "camera_look": [
            "the recording device is the phone itself",
            "phone is propped on the table at a slight side angle",
            "raw phone look",
            "natural perspective from a real table setup",
            "no second phone",
            "no cinematic stabilization"
        ],
        "timeline": [
            {
                "time": "0.0-1.1",
                "beats": [
                    "the same recording phone is resting on the table and already recording",
                    "the camera sees her from a slight side angle at the desk or table",
                    "she is looking directly at the screen of this same recording phone while seated",
                    "there is no other phone in her hands or anywhere on the table",
                    "minimal movement"
                ]
            },
            {
                "time": "1.1-3.0",
                "beats": [
                    "she suddenly reacts to what she sees on the screen of this same recording phone",
                    "she turns more directly toward the recording phone",
                    "she leans forward toward this same phone on the table",
                    "eyes open much wider",
                    "eyebrows lift higher and stay raised",
                    "mouth opens noticeably wider in disbelief",
                    "one hand rises toward her mouth after the mouth opens wide",
                    "hold the wide-eyed, leaned-in shocked expression by the third second"
                ]
            },
            {
                "time": "3.0-4.0",
                "beats": [
                    "stay in the same continuous side-table recording",
                    "keep the leaned-in shocked posture readable",
                    "small natural body movement is okay",
                    "do not attempt a pickup or camera transition inside generation",
                    "do not show or imply any second phone"
                ]
            }
        ],
        "motion": {"start": "2.95", "duration": "0.85", "mode": "logical"},
    },
}


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


def build_prompt(spec: dict) -> dict:
    preset = PRESETS[spec["camera_preset"]]
    hard_rules = [
        "this recording is the phone itself",
        "there is no second phone anywhere",
        "do not show another phone in the frame",
        "do not delay the shock reaction past the third second",
        "the hand-to-mouth gesture must be visible",
        "no cinematic stabilization",
        "no fake zoom",
    ]
    priority_notes = [
        "make the facial reaction strong and readable even on mute",
        "the mouth should open wider before the hand reaches the mouth",
        "the eyes should read very wide and alert by second 3",
        "the audience must feel that the same recording phone is the only device in the shot",
    ]
    if preset["pickup_generation"] == "prompt_plus_post":
        hard_rules.append("the same phone pickup motion must happen after the shock lands")
        priority_notes.append("the pickup motion must happen after the reaction, not before")
    else:
        hard_rules.append("do not generate a phone pickup inside the clip")
        priority_notes.append("hold a visually stable continuous shot so post can add the pickup on the same frame")
    return {
        "format": preset["format"],
        "aspect_ratio": "9:16",
        "test_type": preset["test_type"],
        "hard_rules": hard_rules,
        "goal": preset["goal"],
        "scene": {
            "subject": spec["subject"],
            "appearance": spec["hair"],
            "setting": spec["room"],
            "wardrobe": spec.get("wardrobe", "simple neutral t-shirt"),
            "background_details": spec.get(
                "background_details",
                ["plain wall", "table or desk", "bed or dresser", "ordinary room details"],
            ),
            "lighting": spec.get("lighting", "soft practical room light, ordinary and unstyled"),
            "style": preset["scene_style"],
        },
        "camera": {
            "look": preset["camera_look"],
        },
        "timeline": preset["timeline"],
        "priority_notes": priority_notes,
        "audio": {
            "room_tone": "natural room tone only",
            "music": "none",
            "dialogue": "none"
        }
    }


def render_spec(spec: dict, env: dict, send_slack: bool) -> Path:
    preset = PRESETS[spec["camera_preset"]]
    run_root = ROOT / "runs" / spec["id"]
    prompts_dir = run_root / "prompts"
    assets_dir = run_root / "assets"
    output_dir = run_root / "output"
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

    prompt_path.write_text(json.dumps(build_prompt(spec), indent=2))
    make_overlay(spec["top_hook"], reaction_overlay)
    make_overlay(spec["demo_hook"], demo_overlay)

    run(
        [
            "python3",
            str(AZURE_SCRIPT),
            "--prompt-file", str(prompt_path),
            "--out", str(raw_clip),
            "--seconds", "4",
            "--size", "720x1280",
        ],
        env=env,
    )
    run(
        [
            "python3",
            str(MOTION_SCRIPT),
            "--input", str(raw_clip),
            "--output", str(motion_clip),
            "--start", preset["motion"]["start"],
            "--duration", preset["motion"]["duration"],
            "--mode", preset["motion"]["mode"],
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

    if send_slack:
        run(
            [
                "python3",
                str(SLACK_HELPER),
                "--channel-id", "C0AHDH474LX",
                "--text", f"Reaction pipeline — {spec['camera_preset']} — {spec['id']} — {spec['top_hook']}",
                "--file", str(final_music_out),
            ]
        )

    return final_music_out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to JSON file containing one spec object or a list of specs.")
    parser.add_argument("--send-slack", action="store_true")
    args = parser.parse_args()

    env = os.environ.copy()
    required = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_SORA_MODEL"]
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    spec_path = Path(args.spec).expanduser().resolve()
    payload = json.loads(spec_path.read_text())
    specs = payload if isinstance(payload, list) else [payload]
    for spec in specs:
        final_path = render_spec(spec, env, args.send_slack)
        print(final_path)


if __name__ == "__main__":
    main()
