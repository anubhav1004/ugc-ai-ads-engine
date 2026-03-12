#!/usr/bin/env python3
"""Generate a single Veo clip from a reference image and prompt."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests


GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
VIDEO_MODEL = "veo-3.0-generate-001"


def submit_veo(prompt: str, ref_image: Path, aspect: str, duration: int, api_key: str) -> str:
    img_b64 = base64.b64encode(ref_image.read_bytes()).decode()
    resp = requests.post(
        f"{GEMINI_BASE}/models/{VIDEO_MODEL}:predictLongRunning?key={api_key}",
        json={
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": img_b64,
                    "mimeType": "image/png",
                },
            }],
            "parameters": {
                "aspectRatio": aspect,
                "durationSeconds": duration,
                "sampleCount": 1,
            },
        },
        timeout=300,
    )
    if not resp.ok:
        raise SystemExit(f"Veo submit failed [{resp.status_code}]: {resp.text[:1200]}")
    return resp.json()["name"]


def poll_and_download(op_name: str, out_path: Path, api_key: str) -> None:
    while True:
        time.sleep(10)
        r = requests.get(f"{GEMINI_BASE}/{op_name}?key={api_key}", timeout=60)
        if not r.ok:
            raise SystemExit(f"Veo poll failed [{r.status_code}]: {r.text[:800]}")
        data = r.json()
        done = data.get("done", False)
        print(f"[poll] done={done}", flush=True)
        if not done:
            continue

        response = data.get("response", {})
        gen_resp = response.get("generateVideoResponse", {})
        samples = gen_resp.get("generatedSamples", [])
        if samples:
            uri = samples[0].get("video", {}).get("uri", "")
            if uri:
                dl = requests.get(f"{uri}&key={api_key}", timeout=300)
                if not dl.ok:
                    raise SystemExit(f"Veo download failed [{dl.status_code}]: {dl.text[:800]}")
                out_path.write_bytes(dl.content)
                return

        predictions = response.get("predictions", [])
        if not predictions:
            raise SystemExit(f"No Veo video payload: {json.dumps(data)[:1200]}")
        video_b64 = predictions[0].get("bytesBase64Encoded", "")
        if not video_b64:
            video_b64 = predictions[0].get("video", {}).get("bytesBase64Encoded", "")
        if not video_b64:
            raise SystemExit(f"No Veo video bytes: {json.dumps(predictions[0])[:1200]}")
        out_path.write_bytes(base64.b64decode(video_b64))
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Veo clip from reference image.")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--reference-image", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--duration", type=int, default=8)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY is not set.")

    prompt = Path(args.prompt_file).expanduser().resolve().read_text().strip()
    ref_image = Path(args.reference_image).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("[submit] creating Veo job...", flush=True)
    op_name = submit_veo(prompt, ref_image, args.aspect_ratio, args.duration, api_key)
    print(f"[submit] operation={op_name}", flush=True)
    poll_and_download(op_name, out_path, api_key)
    print(f"[done] saved clip: {out_path}", flush=True)


if __name__ == "__main__":
    main()
