#!/usr/bin/env python3
"""Apply a raw "recording phone got picked up" motion pass to a vertical clip."""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path


def build_filter(start: float, duration: float) -> str:
    start_frame = int(round(start * 30))
    duration_frames = max(1, int(round(duration * 30)))
    end_frame = start_frame + duration_frames
    progress = (
        f"if(lte(on,{start_frame}),0,"
        f"if(gte(on,{end_frame}),1,(on-{start_frame})/{duration_frames}))"
    )
    progress_ff = progress.replace(",", r"\,")
    shake_decay = f"(1-0.45*({progress_ff}))"
    zoom = f"1+0.22*({progress_ff})"
    x = (
        f"(iw-iw/zoom)/2"
        f"+26*({progress_ff})"
        f"+10*sin((on-{start_frame})*0.9)*{shake_decay}"
    )
    y = (
        f"(ih-ih/zoom)/2"
        f"-78*({progress_ff})"
        f"+14*sin((on-{start_frame})*1.45)*{shake_decay}"
    )
    # Brief dark occlusion near pickup to fake fingers brushing the lens edge.
    occlusion_enable = f"between(t,{start + 0.02},{start + 0.30})"

    return ",".join(
        [
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=720x1280:fps=30",
            f"drawbox=x=0:y=0:w=220:h=180:color=black@0.38:t=fill:enable='{occlusion_enable}'",
        ]
    )


def build_logical_filter(start: float, duration: float) -> str:
    start_frame = int(round(start * 30))
    duration_frames = max(1, int(round(duration * 30)))
    end_frame = start_frame + duration_frames
    progress = (
        f"if(lte(on,{start_frame}),0,"
        f"if(gte(on,{end_frame}),1,(on-{start_frame})/{duration_frames}))"
    )
    progress_ff = progress.replace(",", r"\,")
    ease = f"(({progress_ff})*({progress_ff})*(3-2*({progress_ff})))"
    settle = f"if(lt({progress_ff},0.28),0,(({progress_ff})-0.28)/0.72)"
    settle_decay = f"(1-0.8*({settle}))"

    # A real pickup is mostly a lift + slight pull-in, with small natural settle after.
    zoom = f"1+0.09*({ease})"
    x = (
        f"(iw-iw/zoom)/2"
        f"+8*({ease})"
        f"+2.8*sin((on-{start_frame})*0.75)*{settle_decay}"
    )
    y = (
        f"(ih-ih/zoom)/2"
        f"-34*({ease})"
        f"+3.2*sin((on-{start_frame})*1.05)*{settle_decay}"
    )

    # Small lens-edge brush while the same recording phone is picked up.
    occlusion_enable = f"between(t,{start + 0.02},{start + min(duration * 0.22, 0.22)})"
    return ",".join(
        [
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=720x1280:fps=30",
            f"drawbox=x=0:y=0:w=140:h=110:color=black@0.22:t=fill:enable='{occlusion_enable}'",
        ]
    )


def build_aggressive_filter(start: float, duration: float) -> str:
    start_frame = int(round(start * 30))
    duration_frames = max(1, int(round(duration * 30)))
    end_frame = start_frame + duration_frames
    progress = (
        f"if(lte(on,{start_frame}),0,"
        f"if(gte(on,{end_frame}),1,(on-{start_frame})/{duration_frames}))"
    )
    progress_ff = progress.replace(",", r"\,")
    decay = f"(1-0.65*({progress_ff}))"
    zoom = f"1+0.32*({progress_ff})"
    x = (
        f"(iw-iw/zoom)/2"
        f"+42*({progress_ff})"
        f"+22*sin((on-{start_frame})*1.35)*{decay}"
    )
    y = (
        f"(ih-ih/zoom)/2"
        f"-132*({progress_ff})"
        f"+28*sin((on-{start_frame})*2.15)*{decay}"
    )
    occlusion_enable = f"between(t,{start + 0.00},{start + 0.34})"
    return ",".join(
        [
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=720x1280:fps=30",
            f"drawbox=x=0:y=0:w=280:h=240:color=black@0.48:t=fill:enable='{occlusion_enable}'",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply phone pickup motion to a generated clip.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--start", type=float, default=3.0, help="Pickup motion start time in seconds.")
    parser.add_argument("--duration", type=float, default=1.6, help="Pickup motion duration in seconds.")
    parser.add_argument("--mode", choices=["logical", "default", "aggressive"], default="logical")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.mode == "aggressive":
        vf = build_aggressive_filter(args.start, args.duration)
    elif args.mode == "default":
        vf = build_filter(args.start, args.duration)
    else:
        vf = build_logical_filter(args.start, args.duration)
    cmd = [
        "/opt/homebrew/bin/ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "copy",
        str(output_path),
    ]
    print("Running:\n" + " ".join(shlex.quote(part) for part in cmd))
    subprocess.run(cmd, check=True)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
