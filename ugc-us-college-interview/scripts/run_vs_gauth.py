#!/usr/bin/env python3
"""
Professor Curious vs Gauth AI — 3 US College Ads with Logo Overlays

Format: Vlogger asks students "What do you use?"
- Some mention Gauth → GAUTH logo appears on screen (Act 1, 0-4s)
- Most say Professor Curious enthusiastically → PC logo appears (Act 2, 4-8s)
- Logos embedded directly into the video via ffmpeg overlay

Logos:
  Gauth: assets/gauth_logo.png (512x512, App Store icon)
  Prof Curious: assets/pc_logo.png (512x512, App Store icon)

Overlay layout: top-right corner, 130px, with label text below logo.
Auto-sends to Slack after each ad.

Usage:
  source ~/.env_azure
  python3 run_vs_gauth.py
"""

import json
import os
import requests
import subprocess
import sys
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY       = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT      = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL         = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL      = f"{ENDPOINT}/openai/v1"
HEADERS       = {"api-key": API_KEY}
SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
PRODUCT       = "Professor Curious"
RIVAL         = "Gauth"
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

# ── 3 Ads ─────────────────────────────────────────────────────────────────────

ADS = [

    # ── Ad 1: MIT — The direct showdown ──────────────────────────────────────
    {
        "id":     "vs-gauth-mit",
        "run_id": "gauth_01_mit",
        "label":  "PC vs Gauth — MIT",
        "campus": "MIT, Massachusetts Avenue entrance, Cambridge MA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Grey overcast afternoon,
flat natural light. Outside MIT's main entrance on Massachusetts Avenue, Cambridge MA.
Iconic domed Building 10 visible in background. Students in MIT hoodies carrying laptops,
problem sets, walking fast. Intense, competitive, results-driven energy.
Raw phone camera footage, no color grading, natural handheld movement.""",
            "establishing": {
                "line":   "I'm at MIT right now. Super simple question for students: Gauth or Professor Curious — which one do you actually use?",
                "visual": """Vlogger walks toward MIT entrance in selfie-cam, dome visible behind.
Holds up two fingers — 'two options.' Direct energy, gets straight to the comparison.
Points at students walking out — moves toward them immediately.""",
            },
            "outro": {
                "line":   "MIT students. Gauth or Professor Curious. You heard what they said. Link in bio.",
                "visual": """Vlogger faces camera, MIT dome behind him. Arms crossed, slight smile.
Lets the silence do the work. Slow thumbs up. Walks off.""",
            },
            "people": [
                {
                    "id": "p01", "type": "MIT sophomore boy", "age": "19-20",
                    "emotion": "tried both, has a clear verdict",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — which one?",
                    "response": "I tried Gauth first — it's fast, gives you a solution. But Professor Curious actually explains the reasoning step by step. And when I'm really stuck I can get on a call with a real professor. Gauth can't do that. For actually learning the material — Professor Curious. It's not close.",
                    "visual": """Boy is measured — he's used both, this is a real comparison.
Slight nod at 'Gauth — it's fast' — genuine credit.
Then more animated at 'Professor Curious actually explains the reasoning.'
'Real professor' — says this with weight. 'It's not close' — final, certain. Says both names clearly.""",
                },
                {
                    "id": "p02", "type": "MIT junior girl", "age": "20-21",
                    "emotion": "zero hesitation — this is obvious",
                    "gauth_first": False,
                    "question": "What do you use — Gauth or Professor Curious?",
                    "response": "Professor Curious. Hundred percent. I know people use Gauth — it's fine for quick answers. But Professor Curious adapts to where I'm actually weak. It knows what I struggle with. It gives me targeted practice. And the live professor calls — that's a completely different level. Professor Curious, always.",
                    "visual": """Girl answers before the question is finished — 'Professor Curious. Hundred percent.'
Zero hesitation. Says it the first time clearly and emphatically.
Explains Gauth fairly — 'fine for quick answers' — but immediately returns.
'Professor Curious, always.' — second mention, end of clip, equally clear.""",
                },
                {
                    "id": "p03", "type": "MIT freshman boy", "age": "18-19",
                    "emotion": "enthusiastic, converted from Gauth",
                    "gauth_first": True,
                    "question": "Which one — and why did you switch?",
                    "response": "I came in using Gauth from high school. Everyone uses it. Then someone showed me Professor Curious and I realized — Gauth was giving me answers. Professor Curious was teaching me. Those are different things. I haven't opened Gauth since. Professor Curious every day.",
                    "visual": """Boy has real energy — he's a convert and means it.
'Gauth was giving me answers. Professor Curious was teaching me.' — says this slowly, lets it land.
'Haven't opened Gauth since' — said without drama, just fact.
'Professor Curious every day' — says the name twice in the final seconds, clear both times.""",
                },
            ],
        },
    },

    # ── Ad 2: Stanford — The emotional endorsement ───────────────────────────
    {
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
    },

    # ── Ad 3: Harvard — The peer pressure angle ───────────────────────────────
    {
        "id":     "vs-gauth-harvard",
        "run_id": "gauth_03_harvard",
        "label":  "PC vs Gauth — Harvard",
        "campus": "Harvard University, Johnston Gate, Cambridge MA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Bright autumn afternoon,
golden New England light. Outside Harvard's Johnston Gate, Massachusetts Avenue.
Red-brick buildings, Harvard Yard visible behind. Students in hoodies with coffee,
backpacks, AirPods — competitive, aspirational energy.
Raw iPhone footage, no color grading, natural handheld shake.""",
            "establishing": {
                "line":   "Harvard. I want to find out — in this building, on this campus — are people using Gauth or Professor Curious? And what do they think of the other one?",
                "visual": """Vlogger walks toward Johnston Gate in selfie-cam, iconic gate behind him.
Points at the gate — Harvard. The comparison here matters.
Curious, direct energy. He knows he'll get strong opinions.""",
            },
            "outro": {
                "line":   "Harvard students have a preference. It's Professor Curious. The link's in bio.",
                "visual": """Vlogger stands at Johnston Gate, Harvard Yard behind him, late afternoon light.
States it simply — no embellishment needed. The location does the work.
Slow nod. Thumbs up. Walks through the gate.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Harvard junior boy", "age": "20-21",
                    "emotion": "calm and completely sure",
                    "gauth_first": True,
                    "question": "Gauth vs Professor Curious — honest?",
                    "response": "Honest answer — I used Gauth in sophomore year of high school. It was my go-to for quick math. Then someone on my floor freshman year here told me to try Professor Curious. It scans your question, walks you through it, adapts to your weak spots, and if you need to, you call a real professor. I've used it every day since. Gauth hasn't been opened in two years.",
                    "visual": """Boy is calm and completely sure — this is just his experience.
'Gauth — my go-to for quick math' — fair, specific, honest.
The turn to Professor Curious comes naturally — a friend showed him, then he tried it.
'Every day since. Gauth hasn't been opened in two years.' — said without drama. Just true.""",
                },
                {
                    "id": "p02", "type": "Harvard sophomore girl", "age": "19-20",
                    "emotion": "surprised by her own certainty",
                    "gauth_first": False,
                    "question": "Which one — no thinking, just say it.",
                    "response": "Professor Curious. Instantly. I didn't even have to think. That's kind of interesting actually — I've been using it so consistently that it's just the answer. I know Gauth exists, I know people use it, but for me Professor Curious is just — it's what I use. The live professor calls especially. That's something else entirely.",
                    "visual": """Girl says 'Professor Curious. Instantly.' — actually amused at how fast it came out.
'I didn't even have to think' — she's genuinely observing her own certainty.
The 'live professor calls' point is said with real emphasis — that's her differentiator.
Says 'Professor Curious' naturally three times, each clear. Never forced.""",
                },
                {
                    "id": "p03", "type": "Harvard senior boy", "age": "21-22",
                    "emotion": "authoritative — he's given this answer many times",
                    "gauth_first": True,
                    "question": "What do you tell people who ask you about study apps?",
                    "response": "I say: try Gauth if you want quick answers. Use Professor Curious if you want to actually learn. Most people who ask me are trying to get somewhere — a school, a test score, a grade. For that, you need to learn, not just answer. Professor Curious is the only app I know that does both — explains it AND has real professors on call AND adapts to you. That's the one.",
                    "visual": """Boy is authoritative — he's given this speech before, he's refined it.
'Try Gauth if you want quick answers. Use Professor Curious if you want to actually learn.'
This line is delivered slowly, clearly — a real distinction he means.
'That's the one.' — the final two words. Points at camera. Says 'Professor Curious' clearly twice.""",
                },
            ],
        },
    },

]

# ── Logo overlay ──────────────────────────────────────────────────────────────

def embed_logos(raw_path: Path, out_path: Path, gauth_first: bool) -> None:
    """
    Overlay logos on a clip.
    gauth_first=True:  Gauth logo (0-4s) → PC logo (4-8s)
    gauth_first=False: PC logo full clip (0-8s) — person went straight to PC
    Logo: top-right corner, 130px, with app name label below it.
    """
    logo_size = 85
    pad_x = 16
    pad_y = 100  # pushed down from top so it doesn't overlap faces

    if gauth_first:
        filt = (
            f"[1:v]scale={logo_size}:{logo_size}[gauth];"
            f"[2:v]scale={logo_size}:{logo_size}[pc];"
            f"[0:v][gauth]overlay=W-w-{pad_x}:{pad_y}:enable='between(t,0,4)'[v1];"
            f"[v1][pc]overlay=W-w-{pad_x}:{pad_y}:enable='between(t,4,8)'[out]"
        )
        inputs = [
            "-i", str(raw_path),
            "-i", str(GAUTH_LOGO),
            "-i", str(PC_LOGO),
        ]
    else:
        filt = (
            f"[1:v]scale={logo_size}:{logo_size}[pc];"
            f"[0:v][pc]overlay=W-w-{pad_x}:{pad_y}:enable='between(t,0,8)'[out]"
        )
        inputs = [
            "-i", str(raw_path),
            "-i", str(PC_LOGO),
        ]

    result = subprocess.run(
        ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filt,
            "-map", "[out]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-crf", "20",
            "-c:a", "aac",
            "-ar", "48000",
            "-b:a", "128k",
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

# ── Azure Sora API ─────────────────────────────────────────────────────────────

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

# ── Prompt builders ────────────────────────────────────────────────────────────

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

# ── Run one ad ─────────────────────────────────────────────────────────────────

def run_ad(ad: dict) -> None:
    scene   = ad["scene"]
    run_id  = ad["run_id"]
    people  = scene["people"]
    total   = len(people) + 2

    out_dir    = OUTPUT_ROOT / run_id
    raw_dir    = out_dir / "raw"
    logo_dir   = out_dir / "clips"
    raw_dir.mkdir(parents=True, exist_ok=True)
    logo_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {ad['label']}", flush=True)
    print(f"  Campus : {ad['campus']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {total}", flush=True)
    print(f"{'='*60}", flush=True)

    logo_clip_paths = []

    # Establishing — PC logo full clip
    print(f"\n  [1/{total}] Establishing", flush=True)
    raw = raw_dir / "clip_01_establishing.mp4"
    generate_raw_clip(build_establishing_prompt(scene), "establishing", raw)
    logo = logo_dir / "clip_01_establishing.mp4"
    embed_logos(raw, logo, gauth_first=False)
    logo_clip_paths.append(logo)

    # Interviews
    for i, person in enumerate(people, start=2):
        print(f"\n  [{i}/{total}] {person['type']} (gauth_first={person['gauth_first']})", flush=True)
        raw = raw_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_raw_clip(build_person_prompt(person, scene), person["id"], raw)
        logo = logo_dir / f"clip_{i:02d}_{person['id']}.mp4"
        embed_logos(raw, logo, gauth_first=person["gauth_first"])
        logo_clip_paths.append(logo)

    # Outro — PC logo full clip
    print(f"\n  [{total}/{total}] Outro", flush=True)
    raw = raw_dir / f"clip_{total:02d}_outro.mp4"
    generate_raw_clip(build_outro_prompt(scene), "outro", raw)
    logo = logo_dir / f"clip_{total:02d}_outro.mp4"
    embed_logos(raw, logo, gauth_first=False)
    logo_clip_paths.append(logo)

    # Stitch logo-embedded clips
    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} logo-embedded clips ...", flush=True)
    stitch_clips(logo_clip_paths, merged)

    send_to_slack(merged, ad["label"])
    print(f"\n  ✓ DONE: {merged}\n", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}. Need gauth_logo.png and pc_logo.png.")

    print(f"\n{'#'*60}")
    print(f"  Professor Curious vs Gauth — US College Series")
    print(f"  3 ads × 5 clips × {SECONDS}s — logos embedded — auto-Slack")
    print(f"  Logos: {GAUTH_LOGO.name} + {PC_LOGO.name}")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(ADS, 1):
        print(f"\n[Ad {i}/3] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Done. Check Slack for 3 logo-embedded ads.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
