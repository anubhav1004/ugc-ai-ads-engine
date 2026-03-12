#!/usr/bin/env python3
"""Send a message and/or file to the team Slack bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests


DEFAULT_ENDPOINT = "http://zpdev.zupay.in:8160/send"
DEFAULT_CHANNEL = "C0AHDH474LX"


def main() -> None:
    parser = argparse.ArgumentParser(description="Send text and/or a file to Slack via bridge API.")
    parser.add_argument("--channel-id", default=DEFAULT_CHANNEL)
    parser.add_argument("--text", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    args = parser.parse_args()

    if not args.text and not args.file:
        raise SystemExit("At least one of --text or --file is required.")

    data = {"channel_id": args.channel_id}
    if args.text:
        data["text"] = args.text

    files = None
    if args.file:
        file_path = Path(args.file).expanduser().resolve()
        if not file_path.exists():
            raise SystemExit(f"File not found: {file_path}")
        files = {"file": (file_path.name, file_path.open("rb"))}

    try:
        resp = requests.post(args.endpoint, data=data, files=files, timeout=300)
    finally:
        if files:
            files["file"][1].close()

    body = resp.text.strip()
    if resp.ok:
        print(body)
        return

    try:
        parsed = resp.json()
        body = json.dumps(parsed, ensure_ascii=True)
    except Exception:
        pass
    raise SystemExit(f"HTTP {resp.status_code}: {body[:1000]}")


if __name__ == "__main__":
    main()
