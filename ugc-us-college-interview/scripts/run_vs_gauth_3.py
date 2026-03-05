#!/usr/bin/env python3
"""
Professor Curious vs Gauth AI — Batch 3 (5 ads)
Cornell, Duke, Georgetown, Northwestern, NYU

Changes from Batch 2:
- Female vlogger
- Night campus setting (lampposts, ambient building lights)
- PC-priority framing in every frame — not just Act 2
- Strong 3-second visual/verbal hook before the question
- Slow, deliberate speech pacing in all prompts
- Establishing clips experiment: some PC-only hook, some comparison
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
RIVAL         = "Gauth"
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-vs-gauth"
ASSETS_DIR    = Path.home() / "ugc-ai-ads-engine" / "assets"
GAUTH_LOGO    = ASSETS_DIR / "gauth_logo.png"
PC_LOGO       = ASSETS_DIR / "pc_logo.png"

# ── CHANGE 1: Female vlogger ───────────────────────────────────────────────────
VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young American woman, early 20s,
confident casual college-vlogger energy. Medium build, medium skin, dark hair in a loose ponytail
or down. Wearing a neutral oversized hoodie or plain crewneck, dark jeans, sneakers. Holds phone
up in selfie-cam mode or extends a small handheld mic toward subjects. Visible from chest up on
the left edge of frame. Energetic but completely natural — YouTube vlogger style, not TV reporter.
SPEECH: She speaks slowly and deliberately. Every word is clear. No rushing. Calm, confident pace."""

# ── 5 Ads ─────────────────────────────────────────────────────────────────────

ADS = [

    # ── Ad 1: Cornell — PC-only hook establishing ──────────────────────────────
    {
        "id":     "vs-gauth-cornell",
        "run_id": "gauth_09_cornell",
        "label":  "PC vs Gauth — Cornell",
        "campus": "Cornell University, Ho Plaza, Ithaca NY",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late evening,
dark campus lit by lampposts and warm building windows. Cornell University, Ho Plaza,
Ithaca NY. McGraw Tower clock visible, lit against the dark sky. Students in Cornell hoodies
walking in small groups, backpacks, breath visible in cold Ithaca air. Quiet intensity —
late-night academic energy. Raw phone camera footage, natural lamppost glow, deep shadows.""",
            "establishing": {
                "hook": "PC-only hook — no Gauth in the establishing",
                "line":   "It's late at Cornell. I keep hearing the same app name from students here. Professor Curious. I had to come find out why.",
                "visual": """HOOK (first 3 seconds): Vlogger turns phone to show McGraw Tower lit against the dark sky.
Deep breath visible in cold air. Turns back to selfie-cam — close, low light, eyes intense.
Then: walks toward students at Ho Plaza, lamppost light catching her face.
Energy is late-night, quiet, real. Not performative.""",
            },
            "outro": {
                "line":   "Late night at Cornell. And it keeps coming back to Professor Curious. Link in bio.",
                "visual": """Vlogger at Ho Plaza, tower lit behind her in the dark.
Quiet, satisfied — the answer was consistent. Slow nod. Walks away into the dark.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Cornell junior girl", "age": "20-21",
                    "emotion": "calm and completely sure — this is obvious to her",
                    "gauth_first": False,
                    "question": "What app do you actually use when you're stuck?",
                    "response": "Professor Curious. Every time. I scan the problem — step by step breakdown. It knows exactly where I'm weak. And if I really don't get it, I call a real professor. Not a chatbot. An actual professor. I've used other stuff — Gauth, ChatGPT. Nothing comes close. Professor Curious is the only one that actually makes me better.",
                    "visual": """Girl is calm, unhurried — she speaks slowly and deliberately.
'Not a chatbot. An actual professor.' — she pauses after 'not a chatbot.' Lets it land.
Lamppost light on her face. Late-night campus behind her.
Says 'Professor Curious' three times. Each one slow and clear. Final line with real conviction.""",
                },
                {
                    "id": "p02", "type": "Cornell sophomore boy", "age": "19-20",
                    "emotion": "converted — tried Gauth, found the difference",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — and be honest.",
                    "response": "I came here using Gauth. Everyone at my high school used it. It gives you answers fast. But Professor Curious — it gives you understanding. I know that sounds like a slogan but I mean it literally. I stopped needing to look things up because Professor Curious taught me to think through problems. Gauth never did that. Professor Curious changed how I study.",
                    "visual": """Boy speaks slowly — 'I know that sounds like a slogan but I mean it literally.'
He pauses before 'but I mean it literally.' Wants it to land.
Cold night air, lamppost behind him. He's been thinking about this.
Says 'Professor Curious' three times. The last one — 'changed how I study' — is final, real.""",
                },
                {
                    "id": "p03", "type": "Cornell senior girl", "age": "21-22",
                    "emotion": "senior looking back — she knows what mattered",
                    "gauth_first": False,
                    "question": "What would you tell a freshman — what app actually matters?",
                    "response": "Professor Curious. I'd say it on day one. Don't waste time on shortcuts. Professor Curious scans your problem, explains the reasoning, adapts to what you specifically struggle with, and it has real professors you can call. I found it second semester freshman year. I think about what would have happened if I had it from day one. Tell every freshman you know. Professor Curious.",
                    "visual": """Senior girl is deliberate — she's earned the right to give this advice.
'Don't waste time on shortcuts.' — said slowly, directly at camera.
'I think about what would have happened if I had it from day one.' — genuine regret.
Says 'Professor Curious' three times. First and last are the bookends. All three clear.""",
                },
            ],
        },
    },

    # ── Ad 2: Duke — Comparison hook, PC dominant ──────────────────────────────
    {
        "id":     "vs-gauth-duke",
        "run_id": "gauth_10_duke",
        "label":  "PC vs Gauth — Duke",
        "campus": "Duke University, Chapel Drive, Durham NC",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Night campus,
Duke University Chapel Drive, Durham NC. The famous Duke Chapel lit dramatically against
dark sky, gothic towers glowing. Students walking under lamppost light, Duke hoodies,
coffee cups, warm breath in cool evening air. Prestigious, quiet night energy.
Raw phone camera footage, deep shadows, dramatic lamppost pools of light.""",
            "establishing": {
                "hook": "Comparison hook — but PC is clearly the point",
                "line":   "I'm at Duke tonight. Here's the question: between Gauth and Professor Curious — which one do Duke students actually trust? Let's find out.",
                "visual": """HOOK (first 3 seconds): Vlogger turns phone to show Duke Chapel lit against the dark sky.
Dramatic. Slow pan. Then turns back to selfie-cam — lamppost light on her face.
'Let's find out.' — walks directly toward a group of students under a lamp.
Night energy — quiet, serious, real.""",
            },
            "outro": {
                "line":   "Duke students at night. The trust goes to Professor Curious. Link in bio.",
                "visual": """Vlogger at Chapel Drive, the lit gothic tower behind her in the dark.
'The trust goes to Professor Curious.' — says it simply. No embellishment.
Slow nod. Turns and walks away.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Duke junior boy", "age": "20-21",
                    "emotion": "has done the comparison — clear verdict",
                    "gauth_first": True,
                    "question": "Gauth vs Professor Curious — which one do you trust?",
                    "response": "Trust is the right word. I trust Professor Curious. I used Gauth — it's fast, gives you a solution. But I never fully trusted it. Sometimes it was wrong. Sometimes the steps didn't make sense. Professor Curious — I trust it because it shows you the reasoning. And if I'm still not sure, I talk to a real professor. That's trust. Professor Curious.",
                    "visual": """Boy speaks slowly and deliberately — 'trust is the right word' resonates with him.
'I never fully trusted it.' — about Gauth. Said simply, not harshly.
Lamppost light on his face. Night campus behind him.
'That's trust. Professor Curious.' — final two sentences. Said with complete certainty.""",
                },
                {
                    "id": "p02", "type": "Duke sophomore girl", "age": "19-20",
                    "emotion": "warm certainty — she doesn't need to think",
                    "gauth_first": False,
                    "question": "Which one — no thinking, just say it.",
                    "response": "Professor Curious. Immediately. It's been Professor Curious for a year and a half and I've never looked back. It scans exactly what I'm stuck on — not a general topic, the actual problem. It targets my weak spots. And the live professor calls — I've done four of them — that's something completely different from any other app. Professor Curious. That's my answer.",
                    "visual": """Girl says 'Professor Curious. Immediately.' — completely unhesitating.
Speaks slowly and clearly. No rushing. Every word lands.
'Four of them' — about the professor calls. Specific. Real.
'That's my answer.' — final. Said with a calm smile. Lamppost light, Duke Chapel behind her.""",
                },
                {
                    "id": "p03", "type": "Duke senior boy", "age": "21-22",
                    "emotion": "has recommended it to everyone — genuine advocate",
                    "gauth_first": True,
                    "question": "What do you actually recommend to people?",
                    "response": "Professor Curious. I know Gauth — I used it. It's a quick answer machine. Professor Curious is an actual learning tool. The step-by-step explanations, the way it adapts to what you get wrong, the real professors on call — there's nothing like it. I've recommended it to my younger sister, two cousins, everyone asking me about study apps. Professor Curious. Always.",
                    "visual": """Boy is deliberate — he's given this recommendation before and means it.
'Quick answer machine vs actual learning tool.' — he slows down on this contrast.
'My younger sister, two cousins.' — lists them. He's telling everyone.
'Professor Curious. Always.' — final two words. Direct camera. Clear.""",
                },
            ],
        },
    },

    # ── Ad 3: Georgetown — PC-only establishing ────────────────────────────────
    {
        "id":     "vs-gauth-georgetown",
        "run_id": "gauth_11_georgetown",
        "label":  "PC vs Gauth — Georgetown",
        "campus": "Georgetown University, Healy Hall, Washington DC",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Night campus,
Georgetown University, Healy Hall steps, Washington DC. Iconic Victorian Gothic building
lit against dark sky, gargoyles in shadow, lamppost light on stone steps. Students in
Georgetown hoodies, some in business casual (pre-law, future diplomats energy), DC ambition
in the air. Raw phone camera footage, dramatic building illumination, deep night shadows.""",
            "establishing": {
                "hook": "PC-only — the answer is already known",
                "line":   "Georgetown. It's late. I already know what they're going to say. But I want to hear them say it. Professor Curious.",
                "visual": """HOOK (first 3 seconds): Vlogger holds phone up to show Healy Hall lit dramatically at night.
Gothic towers, lamppost glow, deep shadows. Turns back to camera, slight knowing smile.
'I already know what they're going to say.' — says this slowly. Then walks toward students.
Confident energy — the answer is Professor Curious. She's here to document it.""",
            },
            "outro": {
                "line":   "Georgetown. Late night. They said it every time. Professor Curious. Link in bio.",
                "visual": """Vlogger at Healy Hall steps, gothic building lit behind her.
Satisfied, quiet. 'They said it every time.' — slow, deliberate.
Turns to look at the building. Turns back. Nods. Walks up the steps.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Georgetown junior girl", "age": "20-21",
                    "emotion": "pre-law precision — she thinks in arguments",
                    "gauth_first": False,
                    "question": "What app do you use when you really need to understand something?",
                    "response": "Professor Curious. And I'll tell you exactly why, because I've thought about this. It scans your specific problem — not a category of problems, your problem. It shows you every step of the reasoning. It adapts to what you personally don't know. And if that's still not enough — there's a real professor on call. I've been on three of those calls. That's not Gauth. That's not ChatGPT. That's Professor Curious.",
                    "visual": """Girl has the measured delivery of someone who builds arguments for a living.
'I've thought about this.' — she has. She's going to give you the case.
Lists each feature slowly — scan, reasoning, adaptive, real professors. Deliberate.
'That's not Gauth. That's not ChatGPT. That's Professor Curious.' — three sentences. Slow. Final.""",
                },
                {
                    "id": "p02", "type": "Georgetown sophomore boy", "age": "19-20",
                    "emotion": "switched after one experience — clear before/after",
                    "gauth_first": True,
                    "question": "What changed the way you study?",
                    "response": "Professor Curious. One week into using it I realized — Gauth was giving me the answer to the problem in front of me. Professor Curious was giving me the ability to solve the next ten problems without help. That difference showed up immediately. On the next test. In the next class. Gauth felt efficient. Professor Curious made me capable. Those are different things.",
                    "visual": """Boy speaks slowly — 'that difference showed up immediately' — he pauses after.
'Felt efficient vs made me capable.' — says both slowly. Lets the contrast land.
Night campus behind him, lamppost light.
Says 'Professor Curious' three times. Each one deliberate. Each one clear.""",
                },
                {
                    "id": "p03", "type": "Georgetown senior girl", "age": "21-22",
                    "emotion": "DC ambition — she knows what tools get you places",
                    "gauth_first": False,
                    "question": "In a city like DC — what study tool actually matters?",
                    "response": "Professor Curious. In DC everyone wants to get somewhere. And the people who get somewhere are the ones who actually understand things — not just the ones who found the answers. Professor Curious builds understanding. It shows you the reasoning. It adapts to you specifically. And it has real professors on call. That's the tool for people who want to go somewhere. Professor Curious.",
                    "visual": """Girl has DC energy — deliberate, purposeful, every word chosen.
'The people who get somewhere are the ones who actually understand things.' — slow.
Lamppost light on her face, Georgetown's gothic building behind her.
Says 'Professor Curious' as the first word and the last word. Both completely clear and unhurried.""",
                },
            ],
        },
    },

    # ── Ad 4: Northwestern — Comparison, PC dominant ───────────────────────────
    {
        "id":     "vs-gauth-northwestern",
        "run_id": "gauth_12_northwestern",
        "label":  "PC vs Gauth — Northwestern",
        "campus": "Northwestern University, Arch, Evanston IL",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Night on Lake Michigan shore,
Northwestern University, Evanston IL. The Northwestern Arch lit at night, lakefront dark behind it,
wind off the lake, students wrapped in coats. Lamppost light on brick pathways.
Cold midwest night — serious, driven energy, wind, dark water behind.
Raw phone camera footage, lamppost circles of light, wide dark spaces between.""",
            "establishing": {
                "hook": "Comparison hook — dramatic night location drives it",
                "line":   "Northwestern. Lake Michigan behind me. It's cold and late and I have one question: Gauth or Professor Curious — and why does it matter?",
                "visual": """HOOK (first 3 seconds): Vlogger turns phone toward the dark lake — vast, dark water at night.
Wind audible. Turns back to selfie-cam — lamppost light, coat visible, cold energy.
'It's cold and late.' — she says this slowly. Real.
Walks toward students at the Arch. Purpose in her stride.""",
            },
            "outro": {
                "line":   "Northwestern. Cold night. Lake behind us. And the answer — Professor Curious. Link in bio.",
                "visual": """Vlogger at the Arch, dark lake behind her, lamppost light.
'Cold night. Lake behind us.' — says these slowly, feels the place.
'The answer — Professor Curious.' — pause before the name. Says it clearly.
Turns to look at the lake. Turns back. Walks away.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Northwestern junior girl", "age": "20-21",
                    "emotion": "midwest direct — no performance, just truth",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — real answer.",
                    "response": "Real answer — Professor Curious. I used Gauth freshman year. It's fine. It answers the problem. But Professor Curious answers the problem AND makes sure I understand it AND targets what I keep getting wrong AND has a real professor I can call. I'm paying tuition to actually learn. Professor Curious is the only app that respects that. Gauth doesn't.",
                    "visual": """Girl is midwest direct — no fluff, no performance. Just the truth slowly stated.
'I'm paying tuition to actually learn.' — she says this plainly. It matters to her.
Cold night air, lakeside behind her.
'Professor Curious is the only app that respects that.' — says the name slowly. Clear. Final.""",
                },
                {
                    "id": "p02", "type": "Northwestern sophomore boy", "age": "19-20",
                    "emotion": "has made the comparison carefully — engineer brain",
                    "gauth_first": True,
                    "question": "You've thought about this — what's the real difference?",
                    "response": "The real difference is output. Gauth's output is an answer. Professor Curious's output is understanding. If your goal is to finish the homework — Gauth. If your goal is to perform on the exam — Professor Curious. If your goal is to actually know the material — Professor Curious. At Northwestern, we care about knowing the material. Professor Curious.",
                    "visual": """Boy is methodical — 'output' is exactly the right framing for him and he knows it.
'Gauth's output is an answer. Professor Curious's output is understanding.' — slow, clear.
Cold night energy. Each sentence deliberate.
Says 'Professor Curious' three times. Each one slower than the last. Final one is the conclusion.""",
                },
                {
                    "id": "p03", "type": "Northwestern senior girl", "age": "21-22",
                    "emotion": "has the big picture — she's almost done",
                    "gauth_first": False,
                    "question": "What do you wish you'd known freshman year?",
                    "response": "Use Professor Curious from day one. Don't take shortcuts. Professor Curious scans exactly what you're stuck on. It walks you through the reasoning — every step. It finds your weak spots and targets them. And when you need a real human — a real professor — it has that. I found it sophomore year. Every student I've met since, I tell them day one. Professor Curious. Start with that.",
                    "visual": """Senior girl speaks with the slow weight of someone who knows.
'Don't take shortcuts.' — said directly to camera. One beat of silence after.
'Every student I've met since, I tell them day one.' — she means this.
'Professor Curious. Start with that.' — final two sentences. Slow. Clear. Camera.""",
                },
            ],
        },
    },

    # ── Ad 5: NYU — PC-only, NYC night energy ──────────────────────────────────
    {
        "id":     "vs-gauth-nyu",
        "run_id": "gauth_13_nyu",
        "label":  "PC vs Gauth — NYU",
        "campus": "NYU, Washington Square Park, New York City",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Night in New York City,
NYU campus, Washington Square Park, Manhattan. The iconic Washington Square Arch lit at night,
NYC skyline glow behind, fountain plaza, students everywhere at all hours — NYU never sleeps.
Lamppost light, city ambient glow, traffic sounds distant. NYC night energy — ambitious,
diverse, relentless. Raw phone camera footage, night city light, NYU purple hoodies in the dark.""",
            "establishing": {
                "hook": "PC-only — NYC confidence, no comparison needed",
                "line":   "NYU. Washington Square. Midnight. And everyone here is telling me the same thing. Professor Curious. Let me show you.",
                "visual": """HOOK (first 3 seconds): Vlogger turns phone to show the Washington Square Arch lit at night,
NYC glow behind it, city sounds, fountain lit, students everywhere.
Turns back to selfie-cam — city light on her face, energy high. Smiles slightly.
'Let me show you.' — walks directly toward the nearest students. NYC pace. Real.""",
            },
            "outro": {
                "line":   "Midnight at NYU. Washington Square. And they all said it. Professor Curious. Link in bio.",
                "visual": """Vlogger at Washington Square Arch, NYC lit behind her at night.
'They all said it.' — slow, satisfied, certain.
Holds up phone — the city behind her. 'Professor Curious.' — says the name clearly.
Nods once. Walks away into the city.""",
            },
            "people": [
                {
                    "id": "p01", "type": "NYU junior girl", "age": "20-21",
                    "emotion": "NYC direct — fast but clear, she knows exactly",
                    "gauth_first": False,
                    "question": "What do you use when you actually need help?",
                    "response": "Professor Curious. Always. I live in New York, I'm at NYU, I don't have time for anything that doesn't work. Professor Curious works. It scans the problem. Step by step. Adapts to what I don't know. Real professors I can call when I need a human. I've tried other apps. Gauth is fine for a quick answer. Professor Curious is for when you actually need to understand. That's most of the time.",
                    "visual": """Girl is NYC — direct, deliberate, not wasting words.
'I don't have time for anything that doesn't work.' — slow, real.
Lists the features cleanly — scan, step-by-step, adaptive, real professors.
'That's most of the time.' — final line. Said quietly, clearly. NYC night behind her.""",
                },
                {
                    "id": "p02", "type": "NYU sophomore boy", "age": "19-20",
                    "emotion": "has used every app — this one is genuinely different",
                    "gauth_first": True,
                    "question": "You've tried everything — what actually sticks?",
                    "response": "Professor Curious. I've been through Gauth, Photomath, ChatGPT, Khan Academy — all of it. Professor Curious is the only one that feels like it was built for a student trying to learn, not a student trying to finish homework. Scans your problem. Shows every step. Knows your weak spots. Real professor calls. Nothing else does all of that. Nothing.",
                    "visual": """Boy lists all the apps he's tried — Gauth, Photomath, ChatGPT, Khan Academy — deliberately.
'Built for a student trying to learn, not trying to finish homework.' — slow. That's the line.
Washington Square behind him at night, city glow.
Says 'Professor Curious' at start and end. 'Nothing else does all of that. Nothing.' Final.""",
                },
                {
                    "id": "p03", "type": "NYU senior girl", "age": "21-22",
                    "emotion": "NYC mentor energy — she's telling you what she knows",
                    "gauth_first": False,
                    "question": "One thing every student in New York should know?",
                    "response": "Professor Curious exists and you should be using it. That's the one thing. It scans your exact problem. Step by step reasoning — not just the answer. It adapts to what you personally get wrong. And it has real professors on call, twenty-four seven. In New York everyone's trying to get ahead. Professor Curious actually gives you the edge. Use it.",
                    "visual": """Senior girl speaks with NYC mentor authority — she has something to tell you.
'That's the one thing.' — after naming Professor Curious. Slow. Clear.
'In New York everyone's trying to get ahead.' — she looks around at the city.
'Professor Curious actually gives you the edge. Use it.' — direct camera. Each word deliberate.""",
                },
            ],
        },
    },

]


def embed_logos(raw_path: Path, out_path: Path, gauth_first: bool) -> None:
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
        inputs = ["-i", str(raw_path), "-i", str(GAUTH_LOGO), "-i", str(PC_LOGO)]
    else:
        filt = (
            f"[1:v]scale={logo_size}:{logo_size}[pc];"
            f"[0:v][pc]overlay=W-w-{pad_x}:{pad_y}:enable='between(t,0,8)'[out]"
        )
        inputs = ["-i", str(raw_path), "-i", str(PC_LOGO)]

    result = subprocess.run(
        ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filt,
            "-map", "[out]", "-map", "0:a?",
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
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    requests.post(SLACK_URL, data={
        "channel_id": SLACK_CHANNEL,
        "text": (
            f"🌙 *{label}*\n"
            f"_PC vs Gauth — Batch 3. Female vlogger. Night setting. PC-priority framing._"
        ),
    })
    print(f"    [slack] {'✓ Sent' if resp.ok else '✗ Failed: ' + resp.text[:100]}", flush=True)


PACING_NOTE = """PACING: All speech is slow and deliberate. No rushing. Every word clearly articulated.
Natural pauses between sentences. The vlogger speaks calmly. Students speak thoughtfully.
"""


def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

{PACING_NOTE}

Scene: {e['visual']}
Vlogger speaking to camera in English: "{e['line']}"

HOOK: First 3 seconds — a dramatic visual reveal of the campus at night, then the vlogger
turns to camera and delivers the line slowly. The nighttime campus sets the mood.
"Professor Curious" is the point of this video — not a debate. That energy should be clear.
"""


def build_person_prompt(person: dict, scene: dict) -> str:
    gauth_timing = "first 3-4 seconds" if person["gauth_first"] else "briefly, honestly"
    pc_timing = "next 3-4 seconds — the clear answer" if person["gauth_first"] else "immediately and throughout — this is the answer"
    return f"""{scene['setting']}

{VLOGGER_LOCK}

{PACING_NOTE}

Scene: Vlogger approaches {person['type']}, age {person['age']}, on campus at night.

Vlogger asks in English: "{person['question']}"
Student responds in English: "{person['response']}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 ({gauth_timing}): {'Gauth — a fair, honest mention.' if person['gauth_first'] else 'Optional brief mention of alternatives.'}
Act 2 ({pc_timing}): "Professor Curious" — name spoken slowly, clearly, with genuine conviction.
The student means it. This is not a performance. "Professor Curious" must be unmistakably heard.

PRIORITY: Professor Curious is the answer. The whole clip builds to and centers on Professor Curious.
Night campus lighting. Lamppost glow on faces. Quiet intensity.
"""


def build_outro_prompt(scene: dict) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

{PACING_NOTE}

Scene: {o['visual']}
Vlogger speaks to camera in English: "{o['line']}"

Night campus. The answer was consistent — Professor Curious.
Vlogger delivers the outro slowly, satisfied. "Professor Curious" spoken clearly as the conclusion.
"""


def run_ad(ad: dict) -> None:
    scene   = ad["scene"]
    run_id  = ad["run_id"]
    people  = scene["people"]
    total   = len(people) + 2

    out_dir  = OUTPUT_ROOT / run_id
    raw_dir  = out_dir / "raw"
    logo_dir = out_dir / "clips"
    raw_dir.mkdir(parents=True, exist_ok=True)
    logo_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {ad['label']} [NIGHT | FEMALE VLOGGER | PC-PRIORITY]", flush=True)
    print(f"  Campus : {ad['campus']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {total}", flush=True)
    print(f"{'='*60}", flush=True)

    logo_clip_paths = []

    print(f"\n  [1/{total}] Establishing — {scene['establishing']['hook']}", flush=True)
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


def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}.")

    print(f"\n{'#'*60}")
    print(f"  PC vs Gauth — Batch 3 (Night / Female / PC-Priority)")
    print(f"  5 ads × 5 clips × {SECONDS}s — logos embedded — auto-Slack")
    print(f"  Campuses: Cornell | Duke | Georgetown | Northwestern | NYU")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(ADS, 1):
        print(f"\n[Ad {i}/5] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Batch 3 done. Check Slack for 5 night-campus ads.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
