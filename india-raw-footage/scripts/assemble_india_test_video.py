#!/usr/bin/env python3
"""Assemble a first India test ad around the locked outro asset."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble India test video.")
    parser.add_argument("--shot-1", required=True)
    parser.add_argument("--shot-2", default="")
    parser.add_argument("--bridge-image", required=True)
    parser.add_argument("--outro", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--target-seconds", type=float, default=20.0)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    args = parser.parse_args()

    shot_1 = Path(args.shot_1).resolve()
    shot_2 = Path(args.shot_2).resolve() if args.shot_2 else None
    bridge_image = Path(args.bridge_image).resolve()
    outro = Path(args.outro).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    d1 = ffprobe_duration(shot_1)
    d2 = ffprobe_duration(shot_2) if shot_2 else 0.0
    d_outro = ffprobe_duration(outro)
    bridge_seconds = round(args.target_seconds - d1 - d2 - d_outro, 3)
    if bridge_seconds < 0:
        sys.exit(
            f"Negative bridge duration. shot1={d1:.3f}, shot2={d2:.3f}, outro={d_outro:.3f}, "
            f"target={args.target_seconds:.3f}"
        )

    if shot_2:
        filter_complex = (
            f"[0:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v0];"
            f"[1:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v1];"
            f"[2:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v2];"
            f"[3:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v3];"
            f"[0:a]aresample=44100[a0];"
            f"[1:a]aresample=44100[a1];"
            f"[4:a]atrim=duration={bridge_seconds},aresample=44100[a2];"
            f"[3:a]aresample=44100[a3];"
            f"[v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[v][a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(shot_1),
            "-i", str(shot_2),
            "-loop", "1", "-t", str(bridge_seconds), "-i", str(bridge_image),
            "-i", str(outro),
            "-f", "lavfi", "-t", str(bridge_seconds), "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            str(out_path),
        ]
    else:
        filter_complex = (
            f"[0:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v0];"
            f"[1:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v1];"
            f"[2:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v2];"
            f"[0:a]aresample=44100[a0];"
            f"[3:a]atrim=duration={bridge_seconds},aresample=44100[a1];"
            f"[2:a]aresample=44100[a2];"
            f"[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(shot_1),
            "-loop", "1", "-t", str(bridge_seconds), "-i", str(bridge_image),
            "-i", str(outro),
            "-f", "lavfi", "-t", str(bridge_seconds), "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            str(out_path),
        ]

    print(f"[assemble] bridge_seconds={bridge_seconds:.3f}", flush=True)
    subprocess.run(cmd, check=True)
    print(f"[done] saved final video: {out_path}", flush=True)


if __name__ == "__main__":
    main()
