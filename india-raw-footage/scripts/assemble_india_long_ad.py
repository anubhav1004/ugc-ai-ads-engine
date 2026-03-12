#!/usr/bin/env python3
"""Assemble a long-form India ad from multiple clips plus the locked outro."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble long India ad.")
    parser.add_argument("--clips", nargs="+", required=True)
    parser.add_argument("--outro", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    args = parser.parse_args()

    clips = [Path(c).resolve() for c in args.clips]
    outro = Path(args.outro).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    inputs = []
    filter_parts = []
    concat_parts = []
    stream_index = 0

    all_segments = clips + [outro]
    for seg in all_segments:
        inputs.extend(["-i", str(seg)])
        filter_parts.append(
            f"[{stream_index}:v]scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
            f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v{stream_index}]"
        )
        filter_parts.append(f"[{stream_index}:a]aresample=44100[a{stream_index}]")
        concat_parts.append(f"[v{stream_index}][a{stream_index}]")
        stream_index += 1

    filter_complex = ";".join(filter_parts + [f"{''.join(concat_parts)}concat=n={len(all_segments)}:v=1:a=1[v][a]"])

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    duration = ffprobe_duration(out_path)
    print(f"[done] saved final video: {out_path} ({duration:.3f}s)")


if __name__ == "__main__":
    main()
