#!/usr/bin/env python3
"""Recovery: generate street_05_evening_commons from scratch (clip 1 stuck in previous run)."""

import json, os, requests, subprocess, sys, time
from pathlib import Path

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}
SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
SECONDS  = 8
OUTPUT_ROOT = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-us-direct"

SETTING = """Raw handheld smartphone vlog footage, 9:16 vertical.
Early evening, blue-hour light, warm artificial lights starting to come on. Campus common area —
outdoor seating, a few food trucks, string lights. Students transitioning from day to night:
some still in afternoon clothes (tank tops, shorts), some in light hoodies. Campus life peak hour.
Not a specific university — could be any American college commons at dinner time.
Raw phone camera footage, mix of blue hour sky and warm artificial light, real campus energy."""

VLOGGER = """Young American woman, early 20s. Wearing a strappy tank top tucked into jeans, light jacket open.
Hair down. Energetic early-evening vibe. String lights visible behind her. Warm and confident."""

PACING = """PACING: All speech is natural and unhurried. Clear, distinct words.
No rushing. Real conversation energy — not a scripted ad, an actual interaction."""

PEOPLE = [
    {
        "id": "p01", "clip_type": "cold_open",
        "person": "College girl, 20-21, sitting at outdoor table, tank top, plate of food in front of her, phone beside it",
        "question": "I'm asking people — what's the study app everyone's using?",
        "response": "Professor Curious. Hands down. I got a 94 on my last chem exam after failing the one before. I credit Professor Curious completely. Scan the problem, understand it, done.",
        "visual": "Girl answers between bites — unfiltered, direct. '94 after failing' — real number, real shift. She means it. Says 'Professor Curious' clearly twice. Evening commons behind her.",
    },
    {
        "id": "p02", "clip_type": "gauth_reaction",
        "person": "College boy, 19-20, getting food from truck, casual t-shirt, easy manner",
        "question": "Hey, study app question — what do you use?",
        "gauth_response": "Gauth. It's quick, gets the answer.",
        "vlogger_reaction": "I hear you but — have you actually used Professor Curious? It's a completely different thing. You should switch.",
        "person_reaction": "People say that a lot. Okay, tell me what's actually different about it.",
        "visual": "Boy answers while waiting for food — 'quick, gets the answer.' Vlogger steps in — 'have you used Professor Curious?' He turns to face her properly. 'Tell me what's different.' Genuine curiosity — this is a real conversation starting. Natural, unscripted feel.",
    },
    {
        "id": "p03", "clip_type": "normal_pc",
        "person": "College girl, 19-20, hoodie over tank top, evening chill, sitting on steps near commons",
        "question": "Gauth or Professor Curious?",
        "response": "Professor Curious. I tried Gauth freshman year. Professor Curious is what I use now. The step-by-step is better, it adapts to me, and I can talk to a real professor. It's better in every way.",
        "visual": "Girl is direct, not over-explaining. 'Better in every way' — said simply, not exaggerated. Evening light warm on her face. String lights behind her. Says 'Professor Curious' twice. Clear.",
    },
    {
        "id": "p04", "clip_type": "normal_pc",
        "person": "College girl, 20-21, walking through commons with friends, light tank top, laughing, stops to answer",
        "question": "Quick one — what study app?",
        "response": "Professor Curious, obviously. We were literally just talking about it. My whole friend group switched this semester.",
        "visual": "Girl turns from her friends, answers easily — 'obviously.' 'Literally just talking about it' — timing is perfect. Friends in background nod. Warm evening commons behind them.",
    },
    {
        "id": "p05", "clip_type": "normal_pc_wrap",
        "person": "College boy, 21-22, leaning against wall near string lights, relaxed, confident evening energy",
        "question": "Last one — what's the answer? Professor Curious or Gauth?",
        "response": "Professor Curious. Every single person you ask is going to say Professor Curious. Because it actually works. That's the only reason. It works.",
        "visual": "Boy is relaxed, certain — 'every single person you ask.' He knows. String lights warm behind him. 'Because it actually works. That's the only reason.' Delivered slowly, clearly. Vlogger nods at camera — that's the end.",
    },
]


def build_prompt(p, idx):
    if idx == 0:
        return f"""{SETTING}\nVLOGGER: {VLOGGER}\n{PACING}\nCOLD OPEN — NO INTRO. The video starts already in the middle of the interaction.\nScene: Vlogger extends phone toward {p['person']}.\nVlogger asks: "{p['question']}"\nPerson responds: "{p['response']}"\nVisual: {p['visual']}\n"Professor Curious" is spoken clearly and naturally as the answer.\n"""
    elif p["clip_type"] == "gauth_reaction":
        return f"""{SETTING}\nVLOGGER: {VLOGGER}\n{PACING}\nScene: Vlogger approaches {p['person']}.\nTHREE-BEAT STRUCTURE in one 8-second clip:\nBeat 1 (0-3s): Vlogger asks: "{p['question']}"\nPerson answers: "{p['gauth_response']}"\nBeat 2 (3-6s): Vlogger reacts: "{p['vlogger_reaction']}"\nBeat 3 (6-8s): Person: "{p['person_reaction']}"\nVisual: {p['visual']}\n"Professor Curious" said clearly by vlogger in Beat 2.\n"""
    elif p["clip_type"] == "normal_pc_wrap":
        return f"""{SETTING}\nVLOGGER: {VLOGGER}\n{PACING}\nScene: Vlogger extends phone toward {p['person']}.\nVlogger asks: "{p['question']}"\nPerson responds: "{p['response']}"\nVisual: {p['visual']}\nFINAL CLIP — vlogger has a natural end moment after the answer. "Professor Curious" is the last thing heard.\n"""
    else:
        return f"""{SETTING}\nVLOGGER: {VLOGGER}\n{PACING}\nScene: Vlogger extends phone toward {p['person']}.\nVlogger asks: "{p['question']}"\nPerson responds: "{p['response']}"\nVisual: {p['visual']}\n"Professor Curious" is spoken clearly. Casual, real, no performance.\n"""


def submit_job(prompt):
    resp = requests.post(f"{BASE_URL}/videos", headers={**HEADERS, "Content-Type": "application/json"},
                         json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(SECONDS)})
    if not resp.ok:
        raise RuntimeError(f"Submit failed: {resp.text[:400]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    return job["id"]

def poll_job(video_id, clip_id):
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS, timeout=30)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.text[:200]}")
        data = r.json()
        status = data.get("status", "unknown")
        print(f"    [poll] {clip_id} {status} {data.get('progress', 0)}%", flush=True)
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"Job failed")

def download_video(video_id, out_path):
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS, timeout=120)
    if not dl.ok:
        raise RuntimeError(f"Download failed: {dl.text[:200]}")
    out_path.write_bytes(dl.content)
    print(f"    [save] {out_path.name} ({len(dl.content)//1024} KB)", flush=True)

def generate_clip(prompt, clip_id, out_path):
    print(f"    [submit] {clip_id} ...", flush=True)
    vid = submit_job(prompt)
    print(f"    [submit] {clip_id} → {vid}", flush=True)
    poll_job(vid, clip_id)
    download_video(vid, out_path)

def stitch_clips(clip_paths, output_path):
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-ar", "48000", "-b:a", "128k", str(output_path)],
        capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    if r.returncode != 0:
        raise RuntimeError(f"Stitch failed:\n{r.stderr[-400:]}")
    print(f"    [stitch] → {output_path.name}", flush=True)

def send_to_slack(video_path, label):
    print(f"    [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(SLACK_URL, data={"channel_id": SLACK_CHANNEL},
                             files={"file": (video_path.name, f, "video/mp4")})
    requests.post(SLACK_URL, data={"channel_id": SLACK_CHANNEL,
        "text": f"🎬 *{label}*\n_Street Direct format — cold open, no intro, Gauth reaction moment, casual campus._"})
    print(f"    [slack] {'✓ Sent' if resp.ok else '✗ ' + resp.text[:80]}", flush=True)


def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Missing Azure credentials.")

    run_id    = "street_05_evening_commons"
    out_dir   = OUTPUT_ROOT / run_id
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'#'*60}")
    print(f"  Street Direct 05 — Campus Commons, Evening (Recovery)")
    print(f"  5 clips from scratch — auto-Slack")
    print(f"{'#'*60}\n")

    clip_paths = []
    for i, p in enumerate(PEOPLE):
        clip_num = i + 1
        label = "COLD OPEN" if i == 0 else ("GAUTH REACTION" if p["clip_type"] == "gauth_reaction" else ("WRAP" if p["clip_type"] == "normal_pc_wrap" else "PC"))
        print(f"\n  [{clip_num}/5] {p['person'][:50]} — [{label}]", flush=True)
        out = clips_dir / f"clip_{clip_num:02d}_{p['id']}.mp4"
        generate_clip(build_prompt(p, i), p["id"], out)
        clip_paths.append(out)

    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging 5 clips ...", flush=True)
    stitch_clips(clip_paths, merged)
    send_to_slack(merged, "Street Direct 05 — Campus Commons, Evening")
    print(f"\n  ✓ DONE: {merged}\n", flush=True)

    print(f"\n{'#'*60}")
    print(f"  street_05 done. Sent to Slack.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
