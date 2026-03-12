#!/usr/bin/env python3
"""Compile an India raw-footage campaign brief into a shot manifest and prompt pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def rel_json(base: Path, rel_path: str) -> dict:
    return load_json((base / rel_path).resolve())


def validate_campaign(campaign: dict, defaults: dict, shot_plan: list[dict]) -> dict:
    target_duration = campaign["target_duration_seconds"]
    allowed_durations = defaults["duration_presets_seconds"]
    if target_duration not in allowed_durations:
        raise ValueError(
            f"Invalid target_duration_seconds={target_duration}. "
            f"Allowed: {allowed_durations}"
        )

    valid_aspects = set(defaults["aspect_ratio_presets"].values())
    requested_aspects = campaign["target_aspect_ratios"]
    invalid_aspects = [aspect for aspect in requested_aspects if aspect not in valid_aspects]
    if invalid_aspects:
        raise ValueError(
            f"Invalid target_aspect_ratios={invalid_aspects}. "
            f"Allowed: {sorted(valid_aspects)}"
        )

    outro = defaults["india_outro"]
    content_duration = sum(shot["duration_seconds"] for shot in shot_plan)
    total_with_outro = content_duration + outro["duration_seconds"]

    if total_with_outro > target_duration:
        raise ValueError(
            "Generated content plus locked India outro exceeds target duration. "
            f"Content={content_duration}s, outro={outro['duration_seconds']}s, "
            f"target={target_duration}s"
        )

    return {
        "content_duration_seconds": content_duration,
        "outro_duration_seconds": outro["duration_seconds"],
        "target_duration_seconds": target_duration,
        "remaining_optional_seconds": round(target_duration - total_with_outro, 3),
    }


def apply_shot_overrides(shot_plan: list[dict], overrides: dict | None) -> list[dict]:
    if not overrides:
        return [dict(shot) for shot in shot_plan]

    adjusted = []
    for shot in shot_plan:
        current = dict(shot)
        if shot["shot_id"] in overrides:
            current["duration_seconds"] = overrides[shot["shot_id"]]
        adjusted.append(current)
    return adjusted


def build_prompt(campaign: dict, character: dict, fmt: dict, setting: dict, shot: dict) -> str:
    dialog = campaign["dialogue_seed"]
    intent = campaign["creative_intent"]
    char_lock = character["identity_lock"]
    perf_lock = character["performance_lock"]
    cam_lock = character["camera_lock"]

    if shot["role"] == "hook":
        spoken_line = dialog["hook_line"]
    elif shot["role"] == "body":
        spoken_line = dialog["body_line"]
    else:
        spoken_line = dialog["close_line"]

    return f"""Generate a raw India-market phone video.

Campaign: {campaign['campaign_id']}
Market: {campaign['market']}
Product: {campaign['product']}
Format: {fmt['label']}
Shot: {shot['shot_id']} ({shot['role']})
Duration: {shot['duration_seconds']} seconds

SETTING
{setting['setting_prompt']}

CHARACTER LOCK
- Label: {character['label']}
- Age band: {character['age_band']}
- Gender presentation: {char_lock['gender_presentation']}
- Skin tone: {char_lock['skin_tone']}
- Hair: {char_lock['hair']}
- Build: {char_lock['build']}
- Wardrobe: {char_lock['wardrobe']}

PERFORMANCE LOCK
- Speaking style: {perf_lock['speaking_style']}
- Energy: {perf_lock['energy']}
- Emotional beat: {shot['beat']}

CAMERA LOCK
- Style: {cam_lock['style']}
- Framing: {cam_lock['framing']}
- Movement: {cam_lock['movement']}
- Image quality: {cam_lock['image_quality']}
- Shot note: {shot['camera_note']}

CREATIVE INTENT
- Audience: {intent['audience']}
- Pain: {intent['pain']}
- Proof: {intent['proof']}
- Tone: {intent['tone']}

DIALOGUE
The student speaks naturally in Hinglish to the camera:
"{spoken_line}"

RAWNESS RULES
- This must look like real phone footage, not an ad shoot.
- Keep the room ordinary and believable.
- Do not glamorize the student.
- Do not make body language too polished.
- Keep a local India student reality.

AUDIO
- Prefer native scene audio and spoken dialogue.
- Keep background sound subtle: {", ".join(setting['ambient_audio'])}.

DIALOGUE DELIVERY RULE
- Spoken delivery quality is critical.
- The line must sound naturally said by a real Indian student, not recited.
- Keep pauses, hesitations, and stress believable.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a raw-footage campaign manifest.")
    parser.add_argument("--campaign", required=True, help="Path to campaign brief.json")
    args = parser.parse_args()

    campaign_path = Path(args.campaign).expanduser().resolve()
    campaign_dir = campaign_path.parent
    campaign = load_json(campaign_path)
    defaults = load_json((campaign_dir / "../../india_defaults.json").resolve())
    character = rel_json(campaign_dir, campaign["character_ref"])
    fmt = rel_json(campaign_dir, campaign["format_ref"])
    setting = rel_json(campaign_dir, campaign["setting_ref"])
    effective_shot_plan = apply_shot_overrides(
        fmt["shot_plan"], campaign.get("shot_duration_overrides")
    )
    duration_plan = validate_campaign(campaign, defaults, effective_shot_plan)

    build_dir = campaign_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
      "campaign_id": campaign["campaign_id"],
      "market": campaign["market"],
      "product": campaign["product"],
      "character_id": character["id"],
      "format_id": fmt["id"],
      "setting_id": setting["id"],
      "target_duration_seconds": campaign["target_duration_seconds"],
      "target_aspect_ratios": campaign["target_aspect_ratios"],
      "generation_preferences": campaign["generation_preferences"],
      "duration_plan": duration_plan,
      "india_defaults": {
          "outro_asset_path": defaults["india_outro"]["asset_path"],
          "outro_locked": defaults["india_outro"]["policy"]["required_for_all_india_ads"],
          "outro_audio_edit_allowed": defaults["india_outro"]["policy"]["audio_edit_allowed"],
          "outro_timing_change_allowed": defaults["india_outro"]["policy"]["timing_change_allowed"]
      },
      "shots": [],
    }

    for shot in effective_shot_plan:
        prompt_text = build_prompt(campaign, character, fmt, setting, shot)
        prompt_file = build_dir / f"{shot['shot_id']}_prompt.txt"
        prompt_file.write_text(prompt_text)
        manifest["shots"].append(
            {
                "shot_id": shot["shot_id"],
                "role": shot["role"],
                "duration_seconds": shot["duration_seconds"],
                "prompt_file": prompt_file.name,
            }
        )

    (build_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[done] Built manifest: {build_dir / 'run_manifest.json'}")


if __name__ == "__main__":
    main()
