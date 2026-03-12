#!/usr/bin/env python3
"""Generate a reference-scene still with Gemini image generation."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def load_text(path: Path) -> str:
    return path.read_text().strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a reference scene image with Gemini.")
    parser.add_argument("--prompt-file", required=True, help="Path to prompt text file")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument(
        "--model",
        default="gemini-3-pro-image-preview",
        help="Gemini image model (default: gemini-3-pro-image-preview)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="9:16",
        help="Image aspect ratio such as 9:16, 4:5, or 16:9",
    )
    parser.add_argument(
        "--image-size",
        default="2K",
        help="Gemini image size: 1K, 2K, or 4K",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY is not set.")

    prompt = load_text(Path(args.prompt_file).expanduser().resolve())
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": args.aspect_ratio,
                "imageSize": args.image_size,
            },
        },
    }

    req = urllib.request.Request(
        API_URL.format(model=args.model) + f"?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error: {exc}") from exc

    candidates = response.get("candidates") or []
    if not candidates:
        raise SystemExit(f"No candidates returned: {json.dumps(response)[:1000]}")

    parts = candidates[0].get("content", {}).get("parts", [])
    image_b64 = None
    text_parts = []

    for part in parts:
        if "inlineData" in part and part["inlineData"].get("data"):
            image_b64 = part["inlineData"]["data"]
            break
        if "text" in part and part["text"]:
            text_parts.append(part["text"])

    if not image_b64:
        raise SystemExit(
            "No image data returned. Response text: "
            + " ".join(text_parts)[:1000]
        )

    out_path.write_bytes(base64.b64decode(image_b64))
    print(f"[done] Saved image: {out_path}")


if __name__ == "__main__":
    main()
