#!/usr/bin/env python3
"""Generate a single Sora clip via Azure OpenAI video endpoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def request_json(url: str, headers: dict, payload: dict | None = None, method: str = "GET") -> dict:
    req = urllib.request.Request(
        url,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {body}") from exc


def request_bytes(url: str, headers: dict) -> bytes:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {body}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Sora clip using Azure OpenAI.")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seconds", required=True, help="Clip duration in seconds")
    parser.add_argument("--size", default="720x1280")
    parser.add_argument("--poll-interval", type=int, default=15)
    parser.add_argument("--input-reference", default="", help="Optional reference image for character consistency")
    args = parser.parse_args()

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    model = os.environ.get("AZURE_SORA_MODEL", "sora-2")
    if not api_key or not endpoint:
        sys.exit("ERROR: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set.")

    prompt = Path(args.prompt_file).expanduser().resolve().read_text().strip()
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {"api-key": api_key}
    base_url = f"{endpoint}/openai/v1"

    print("[submit] creating video job...", flush=True)
    if args.input_reference:
        ref_path = Path(args.input_reference).expanduser().resolve()
        with open(ref_path, "rb") as ref_file:
            import requests

            submit_resp = requests.post(
                f"{base_url}/videos",
                headers=headers,
                data={
                    "model": model,
                    "prompt": prompt,
                    "size": args.size,
                    "seconds": str(args.seconds),
                },
                files={
                    "input_reference": (ref_path.name, ref_file, "image/png"),
                },
                timeout=300,
            )
        if not submit_resp.ok:
            raise SystemExit(f"HTTP {submit_resp.status_code}: {submit_resp.text}")
        submit = submit_resp.json()
    else:
        headers["Content-Type"] = "application/json"
        payload = {
            "model": model,
            "prompt": prompt,
            "size": args.size,
            "seconds": str(args.seconds),
        }
        submit = request_json(f"{base_url}/videos", headers, payload, "POST")
    video_id = submit["id"]
    print(f"[submit] video_id={video_id}", flush=True)

    while True:
        time.sleep(args.poll_interval)
        status = request_json(f"{base_url}/videos/{video_id}", {"api-key": api_key})
        state = status.get("status", "unknown")
        progress = status.get("progress", 0)
        print(f"[poll] status={state} progress={progress}", flush=True)
        if state == "completed":
            break
        if state == "failed":
            raise SystemExit(f"Video job failed: {json.dumps(status)[:1200]}")

    print("[download] fetching video bytes...", flush=True)
    video_bytes = request_bytes(f"{base_url}/videos/{video_id}/content", {"api-key": api_key})
    out_path.write_bytes(video_bytes)
    print(f"[done] saved clip: {out_path}", flush=True)


if __name__ == "__main__":
    main()
