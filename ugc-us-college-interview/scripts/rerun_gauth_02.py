#!/usr/bin/env python3
"""
Rerun gauth_02_stanford only (failed mid-run due to DNS error).
Identical logic to run_vs_gauth.py for the Stanford ad.
"""

import json
import os
import requests
import subprocess
import sys
import time
from pathlib import Path

API_KEY       = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT      = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL         = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL      = f"{ENDPOINT}/openai/v1"
HEADERS       = {"api-key": API_KEY}
SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
PRODUCT       = "Professor Curious"
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-vs-gauth"
ASSETS_DIR    = Path.home() / "ugc-ai-ads-engine" / "assets"
GAUTH_LOGO    = ASSETS_DIR / "gauth_logo.png"
PC_LOGO       = ASSETS_DIR / "pc_logo.png"

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young American male, early 20s,
confident casual college-vlogger energy. Medium build, medium skin, short neat hair.
Wearing a neutral grey hoodie or plain white t-shirt, dark jeans. Holds phone up in
selfie-cam mode or points a small handheld mic toward subjects. Visible from chest up
on the left edge of frame. Energetic but natural — YouTube vlogger style, not TV reporter."""

AD = {
    "id":     "vs-gauth-stanford",
    "run_id": "gauth_02_stanford",
    "label":  "PC vs Gauth — Stanford",
    "campus": "Stanford University, White Plaza, Palo Alto CA",
    "scene": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Warm California afternoon,
bright golden light, palm trees. Stanford's White Plaza, Palo Alto CA. Students in casual
California wear — t-shirts, Patagonia vests, Stanford lanyards. Warm, open,
startup-meets-academic energy. Raw phone camera footage, no color grading, beautiful warm light.""",
        "establishing": {
            "line":   "Stanford. I'm asking students one thing: if you had to choose — Gauth or Professor Curious — and you had to say why. Let's go.",
            "visual": """Vlogger walks through White Plaza, palm trees visible.
Casual, warm California energy — this isn't a debate, it's a real question.
Points at students on the grass. Walks toward them with purpose.""",
        },
        "outro": {
            "line":   "Stanford. Gauth versus Professor Curious. The answer was pretty clear. Link's in bio.",
            "visual": """Vlogger faces camera, Quad in warm afternoon light behind him.
Shrugs expressively — the results spoke for themselves. Easy smile. Thumbs up.""",
        },
        "people": [
            {
                "id": "p01", "type": "Stanford junior girl", "age": "20-21",
                "emotion": "warm and completely certain",
                "gauth_first": False,
                "question": "Gauth or Professor Curious?",
                "response": "Professor Curious — and it's not even a question for me. I love that it scans your exact problem, not just the topic. And the adaptation — it figures out what I don't know and focuses on that. I've recommended it to everyone. My little sister, my cousin, three friends from high school. Gauth I used once. Professor Curious is my daily thing.",
                "visual": """Girl is warm, genuine — this is an enthusiastic endorsement.
'Not even a question for me' — relaxed, certain.
Lists the specific features of PC — scan, adaptation — she's noticed them.
'Gauth I used once. Professor Curious is my daily thing.' — says 'Professor Curious' clearly, finally.""",
            },
            {
                "id": "p02", "type": "Stanford sophomore boy", "age": "19-20",
                "emotion": "analytical but enthusiastic",
                "gauth_first": True,
                "question": "You've tried both — what's the verdict?",
                "response": "Gauth solves the problem. Professor Curious solves the problem and makes sure you don't have the same problem again. It adapts. It tracks your weak areas. It brings in real professors when the AI isn't enough. That compound effect — over weeks and months — that's enormous. That's the difference between a 1450 and a 1550 on the SAT.",
                "visual": """Boy is analytical — he's thought through the compound effect argument.
'Gauth solves the problem.' — fair, single beat. Then immediately: 'Professor Curious...'
The SAT score gap: '1450 to 1550' — concrete, real. That's the kind of number that lands.
Says 'Professor Curious' three times — naturally, not forced. Each time clearly.""",
            },
            {
                "id": "p03", "type": "Stanford senior girl", "age": "21-22",
                "emotion": "definitive — she doesn't need to think",
                "gauth_first": False,
                "question": "Quick answer — which one?",
                "response": "Professor Curious. Definitely. Oh my god, definitely Professor Curious. I don't even — Gauth is fine, I'm not going to be mean about it. But Professor Curious has actual professors you can call. It's personalized. It's like having a really smart study partner who knows exactly where you're weak and won't let you move on until you've got it. It's completely different.",
                "visual": """Girl laughs at how easy this question is for her — 'Oh my god, definitely.'
The energy is high, genuine — she almost can't believe she's being asked.
'I'm not going to be mean about it' — slight laugh, then back.
'Professor Curious' said three times with escalating certainty. Completely real.""",
            },
        ],
    },
}


def embed_logos(raw_path: Path, out_path: Path, gauth_first: bool) -> None:
    logo_size = 130
    pad = 20
    if gauth_first:
        filt = (
            f"[1:v]scale={logo_size}:{logo_size}[gauth];"
            f"[2:v]scale={logo_size}:{logo_size}[pc];"
            f"[0:v][gauth]overlay=W-w-{pad}:{pad}:enable='between(t,0,4)'[v1];"
            f"[v1][pc]overlay=W-w-{pad}:{pad}:enable='between(t,4,8)'[out]"
        )
        inputs = ["-i", str(raw_path), "-i", str(GAUTH_LOGO), "-i", str(PC_LOGO)]
    else:
        filt = (
            f"[1:v]scale={logo_size}:{logo_size}[pc];"
            f"[0:v][pc]overlay=W-w-{pad}:{pad}:enable='between(t,0,8)'[out]"
        )
        inputs = ["-i", str(raw_path), "-i", str(PC_LOGO)]

    result = subprocess.run(
        ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filt,
            "-map", "[out]",
            "-map", "0:a?",
            "-c:v", "libx264", "-crf", "20",
            "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
            str(out_path),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Logo overlay failed:\n{result.stderr[-500:]}")
    print(f"    [logo] → {out_path.name} ({out_path.stat().st_size//1024} KB)", flush=True)


def stitch_clips(clip_paths: list, output_path: Path) -> None:
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:v", "libx264", "-crf", "20",
         "-c:a", "aac", "-ar", "48000", "-b:a", "128k", str(output_path)],
        capture_output=True, text=True,
    )
    list_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"Stitch failed:\n{result.stderr[-500:]}")
    print(f"    [stitch] → {output_path.name}", flush=True)


def submit_job(prompt: str, clip_id: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/videos",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(SECONDS)},
    )
    if not resp.ok:
        raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    return job["id"]


def poll_job(video_id: str, clip_id: str) -> None:
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:300]}")
        data = r.json()
        status = data.get("status", "unknown")
        print(f"    [poll] {clip_id} {status} {data.get('progress', 0)}%", flush=True)
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:400]}")


def download_video(video_id: str, out_path: Path) -> None:
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"    [save] {out_path.name} ({len(dl.content)//1024} KB)", flush=True)


def generate_raw_clip(prompt: str, clip_id: str, out_path: Path) -> None:
    print(f"    [submit] {clip_id} ...", flush=True)
    video_id = submit_job(prompt, clip_id)
    print(f"    [submit] {clip_id} → {video_id}", flush=True)
    poll_job(video_id, clip_id)
    download_video(video_id, out_path)


def send_to_slack(video_path: Path, label: str) -> None:
    print(f"    [slack] Sending {video_path.name} ...", flush=True)
    helper = Path(__file__).resolve().parents[2] / "common" / "send_slack.py"
    result = subprocess.run([
        "python3", str(helper),
        "--channel-id", SLACK_CHANNEL,
        "--text", (
            f"🇺🇸 *{label}*\n"
            f"_Professor Curious vs Gauth — with logo overlays._\n"
            f"Gauth logo appears when Gauth mentioned → Professor Curious logo on the answer."
        ),
        "--file", str(video_path),
    ], capture_output=True, text=True)
    resp = result.stdout.strip() or result.stderr.strip()
    print(f"    [slack] {'✓ Sent' if result.returncode == 0 else '✗ Failed: ' + resp[:100]}", flush=True)


def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {e['visual']}
Vlogger speaking to camera in English: "{e['line']}"

HOOK: First 2 seconds — the vlogger names BOTH apps clearly. The comparison is the hook.
Raw vlog energy, direct. Students are about to give real opinions.
"""


def build_person_prompt(person: dict, scene: dict) -> str:
    gauth_timing = "first 3-4 seconds" if person["gauth_first"] else "briefly, as a fair comparison"
    pc_timing = "next 3-4 seconds (the clear winner)" if person["gauth_first"] else "immediately and throughout"
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: Vlogger approaches {person['type']}, age {person['age']}, on campus.

Vlogger asks in English: "{person['question']}"
Student responds in English: "{person['response']}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 ({gauth_timing}): Gauth — fair mention, honest assessment. Not dismissive.
Act 2 ({pc_timing}): "Professor Curious" — the name spoken clearly, out loud, enthusiastically.
The shift in energy is visible. "Professor Curious" must be unmistakably heard.

Both app names must be clearly spoken as recognizable brand names.
American college student energy — casual, direct, credible.
"""


def build_outro_prompt(scene: dict) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks to camera in English: "{o['line']}"
Understated. The campus and the students said everything.
"""


def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}.")

    ad     = AD
    scene  = ad["scene"]
    run_id = ad["run_id"]
    people = scene["people"]
    total  = len(people) + 2

    out_dir  = OUTPUT_ROOT / run_id
    raw_dir  = out_dir / "raw"
    logo_dir = out_dir / "clips"
    raw_dir.mkdir(parents=True, exist_ok=True)
    logo_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  RERUN: {ad['label']}")
    print(f"  Campus : {ad['campus']}")
    print(f"  Run ID : {run_id}  |  Clips: {total}")
    print(f"{'='*60}")

    logo_clip_paths = []

    print(f"\n  [1/{total}] Establishing", flush=True)
    raw  = raw_dir / "clip_01_establishing.mp4"
    generate_raw_clip(build_establishing_prompt(scene), "establishing", raw)
    logo = logo_dir / "clip_01_establishing.mp4"
    embed_logos(raw, logo, gauth_first=False)
    logo_clip_paths.append(logo)

    for i, person in enumerate(people, start=2):
        print(f"\n  [{i}/{total}] {person['type']} (gauth_first={person['gauth_first']})", flush=True)
        raw  = raw_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_raw_clip(build_person_prompt(person, scene), person["id"], raw)
        logo = logo_dir / f"clip_{i:02d}_{person['id']}.mp4"
        embed_logos(raw, logo, gauth_first=person["gauth_first"])
        logo_clip_paths.append(logo)

    print(f"\n  [{total}/{total}] Outro", flush=True)
    raw  = raw_dir / f"clip_{total:02d}_outro.mp4"
    generate_raw_clip(build_outro_prompt(scene), "outro", raw)
    logo = logo_dir / f"clip_{total:02d}_outro.mp4"
    embed_logos(raw, logo, gauth_first=False)
    logo_clip_paths.append(logo)

    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} logo-embedded clips ...", flush=True)
    stitch_clips(logo_clip_paths, merged)
    send_to_slack(merged, ad["label"])
    print(f"\n  ✓ DONE: {merged}\n", flush=True)


if __name__ == "__main__":
    main()
