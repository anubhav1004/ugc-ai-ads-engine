#!/usr/bin/env python3
"""
US Street Direct — No Intro, Cold Open, Raw Interviews
5 ads × 5 clips each

Format (per ad):
  Clip 1 (p01): Cold open — vlogger already talking to someone → Professor Curious
  Clip 2 (p02): Person says Gauth → vlogger reacts live: "Have you tried Professor Curious?"
  Clip 3 (p03): Professor Curious
  Clip 4 (p04): Professor Curious
  Clip 5 (p05): Professor Curious — natural wrap energy

No establishing clip. No separate outro. Cold open into interviews.
Settings: casual campus / college town — NOT named elite universities.
Lighting: varied (sunny, golden hour, overcast, night).
Cast: mixed genders, girls in tank tops and shorts for warm settings.
Auto-sends to Slack after each ad.
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
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-us-direct"

# ── 5 Ads ─────────────────────────────────────────────────────────────────────

ADS = [

    # ── Ad 1: Sunny campus quad — warm afternoon, tank tops ───────────────────
    {
        "id":     "street_01",
        "run_id": "street_01_sunny_quad",
        "label":  "Street Direct 01 — Sunny Campus Quad",
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical.
Bright warm sunny afternoon, blue sky, no clouds. Generic university outdoor quad —
green lawn, scattered trees, benches. Students in summer clothes everywhere:
girls in tank tops and denim shorts, boys in t-shirts. Casual, warm, relaxed energy.
No specific university logos or signs. Could be any American college on a warm day.
Raw phone camera footage, slightly overexposed sunny look, natural handheld movement.""",
        "vlogger": """Young American woman, early 20s, college-vlogger energy.
Wearing a casual white fitted tank top, light wash denim shorts, sneakers, sunglasses pushed up on head.
Dark hair down. Holds phone in selfie-cam mode or extends it toward people. Natural, warm energy.""",
        "people": [
            {
                "id": "p01",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, sitting on campus lawn, tank top and shorts, relaxed",
                "question": "Quick question — what's your go-to study app?",
                "response": "Professor Curious. No question. I scan whatever problem I'm stuck on, it walks me through it step by step. Love it.",
                "visual": "Girl looks up from phone, answers immediately, sunny lawn behind her. Easy, warm smile. Says the name clearly.",
            },
            {
                "id": "p02",
                "clip_type": "gauth_reaction",
                "person": "College boy, 20-21, walking across quad, backpack on, t-shirt",
                "question": "Hey, what study app do you use?",
                "gauth_response": "Gauth, mostly.",
                "vlogger_reaction": "Wait, have you tried Professor Curious? You should seriously try it — it's way better.",
                "person_reaction": "Huh — I've heard of it. I'll check it out, actually.",
                "visual": "Boy stops, answers 'Gauth.' Vlogger does a double-take, leans in. 'Have you tried Professor Curious?' Boy pauses, genuinely considers it. 'I'll check it out.' The shift is real.",
            },
            {
                "id": "p03",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, standing near campus bench, white tank top and shorts, iced coffee",
                "question": "Gauth or Professor Curious — which one?",
                "response": "Professor Curious, easy. It adapts to what I don't know. It's like it knows exactly where I'm struggling. Way better than anything else I've used.",
                "visual": "Girl sips her iced coffee, answers without hesitation. Warm sunshine on her face. Says 'Professor Curious' slowly and clearly.",
            },
            {
                "id": "p04",
                "clip_type": "normal_pc",
                "person": "College girl, 20-21, sitting cross-legged on grass, colorful tank top, headphones around neck",
                "question": "What do you actually use when you're stuck on a problem?",
                "response": "Professor Curious. Always. I take a photo of the problem and it breaks it all down. And if I'm really stuck, there's an actual professor I can call. Nothing else does that.",
                "visual": "Girl looks up from textbook, answers warmly. Sunny quad behind her. Emphasizes 'actual professor' — that's the thing that gets her. Says the name twice, clear both times.",
            },
            {
                "id": "p05",
                "clip_type": "normal_pc_wrap",
                "person": "College boy, 21-22, leaning against a tree, casual t-shirt, confident",
                "question": "Last one — Gauth or Professor Curious?",
                "response": "Professor Curious. It's not even close. I've tried everything. Professor Curious is the one that actually teaches you. That's it.",
                "visual": "Boy grins — 'not even close.' Says it like he's been asked before and always gives the same answer. Vlogger smiles at camera at the end — that's her wrap. Natural, warm, sunny.",
            },
        ],
    },

    # ── Ad 2: College town street — golden hour, mixed cast ───────────────────
    {
        "id":     "street_02",
        "run_id": "street_02_golden_hour",
        "label":  "Street Direct 02 — College Town Street, Golden Hour",
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical.
Golden hour late afternoon, warm orange light on everything. A college town main street —
small cafes, bookstores, bike racks, students walking. Not a specific campus, just the
kind of street that exists near every American university. Students in casual clothes,
some with coffee, some with backpacks. Warm golden light, long shadows, real street energy.
Raw phone camera footage, beautiful warm glow, natural movement.""",
        "vlogger": """Young American woman, early 20s, vlogger energy.
Wearing an oversized graphic tee tucked into high-waisted jeans, white sneakers. Hair in a messy bun.
Holds phone up naturally. Warm, direct, curious. Stops people on the street genuinely.""",
        "people": [
            {
                "id": "p01",
                "clip_type": "normal_pc",
                "person": "College boy, 20-21, walking down the street, backpack, golden light on him",
                "question": "One question — what's your go-to for studying?",
                "response": "Professor Curious. Scans your question, gives you every step. My whole friend group switched to it. It's the one.",
                "visual": "Boy stops, answers immediately. Golden hour light warm on his face. Confident. Says 'Professor Curious' clear and natural. Walks on.",
            },
            {
                "id": "p02",
                "clip_type": "gauth_reaction",
                "person": "College girl, 19-20, coming out of a cafe, coffee in hand, casual summer dress",
                "question": "Hey, what study app do you use?",
                "gauth_response": "Gauth, it's pretty useful.",
                "vlogger_reaction": "Okay but have you used Professor Curious? Genuinely — you need to try it.",
                "person_reaction": "People keep telling me that. Okay I'm downloading it right now.",
                "visual": "Girl answers 'Gauth' easily. Vlogger's face lights up — 'have you used Professor Curious?' Genuine, not aggressive. Girl laughs a little — 'people keep telling me.' Takes out phone. Vlogger watches, pleased.",
            },
            {
                "id": "p03",
                "clip_type": "normal_pc",
                "person": "College girl, 20-21, sitting outside a cafe, iced latte, sleeveless top, golden light",
                "question": "Gauth or Professor Curious — quick answer.",
                "response": "Professor Curious. I used to use Gauth but Professor Curious just explains things better. Step by step, figures out what I'm weak at. I don't go back.",
                "visual": "Girl answers easily in the warm golden light. 'I don't go back' — said simply. Says 'Professor Curious' twice, both clear. Street behind her glowing warm.",
            },
            {
                "id": "p04",
                "clip_type": "normal_pc",
                "person": "College boy, 21-22, leaning on a bike rack, casual, late afternoon light",
                "question": "What do you actually use to study?",
                "response": "Professor Curious. It's got real professors you can actually call when you're stuck. I've done it like five times now. That's the thing that keeps me on it.",
                "visual": "Boy is relaxed, not selling anything — just answering honestly. 'Five times' — he counts it. Real. Says 'Professor Curious' clearly. Golden light on the street behind him.",
            },
            {
                "id": "p05",
                "clip_type": "normal_pc_wrap",
                "person": "College girl, 19-20, walking past, tank top, denim shorts, earbuds out to answer",
                "question": "Quick — Gauth or Professor Curious?",
                "response": "Professor Curious, obviously. Ask anyone here. That's the answer you're getting.",
                "visual": "Girl pulls out one earbud, answers immediately — 'obviously.' Smiles. Puts earbud back in, keeps walking. Vlogger watches her go, raises eyebrow at camera. That's the wrap.",
            },
        ],
    },

    # ── Ad 3: Campus library steps — overcast morning, cozy ──────────────────
    {
        "id":     "street_03",
        "run_id": "street_03_library_steps",
        "label":  "Street Direct 03 — Library Steps, Morning",
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical.
Overcast bright morning, soft diffused light. Steps outside a campus library — students
arriving with coffee cups, backpacks, laptops. Not a specific university. Could be any
American campus library on a regular weekday morning. Some students in hoodies, some in
lighter clothing. Busy but calm — start-of-day energy. Raw phone camera footage,
flat natural overcast light, real campus feel.""",
        "vlogger": """Young American woman, early 20s, morning energy.
Wearing a light zip-up hoodie open over a cropped tee, leggings, sneakers. Hair half up.
Coffee cup in one hand, phone in the other. Relaxed morning vibe. Stops students heading in and out.""",
        "people": [
            {
                "id": "p01",
                "clip_type": "normal_pc",
                "person": "College girl, 20-21, sitting on library steps, laptop open, tank top visible under open flannel shirt",
                "question": "What do you use when you're stuck on something?",
                "response": "Professor Curious. I use it every morning before class. Scan the problem, understand it before I walk in. My grades this semester are the best they've been.",
                "visual": "Girl looks up from laptop, speaks directly. 'Every morning before class' — this is a routine. Grades line lands simply. Says 'Professor Curious' clearly. Back to laptop.",
            },
            {
                "id": "p02",
                "clip_type": "gauth_reaction",
                "person": "College boy, 20-21, heading into library, backpack, hoodie, coffee",
                "question": "Hey, study app — what do you use?",
                "gauth_response": "Gauth, yeah. It does the job.",
                "vlogger_reaction": "Okay stop — have you used Professor Curious? It's on another level. Seriously try it.",
                "person_reaction": "I've heard about it. Someone in my dorm keeps saying the same thing. Maybe I should actually try it.",
                "visual": "Boy stops, answers 'Gauth, it does the job.' Vlogger physically steps forward — 'have you used Professor Curious?' Not aggressive, just urgent. Boy laughs — 'my whole dorm says the same thing.' Considers it. Real.",
            },
            {
                "id": "p03",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, coming down library steps, light backpack, tank top and cardigan",
                "question": "Quick — Gauth or Professor Curious?",
                "response": "Professor Curious, not even a thought. The way it breaks things down — it's like having a tutor who knows exactly what I'm missing. I tell everyone I know.",
                "visual": "Girl answers before she's fully stopped — 'not even a thought.' Pauses, adds the tutor line. Means it. Says 'Professor Curious' clear. Continues down the steps.",
            },
            {
                "id": "p04",
                "clip_type": "normal_pc",
                "person": "College boy, 21-22, sitting on steps with a friend, t-shirt, easy morning energy",
                "question": "Both of you — study app. Go.",
                "response": "Professor Curious. Both of us. We literally figured it out together freshman year. It's just the answer.",
                "visual": "Boy speaks for both of them — friend nods along. 'Figured it out together freshman year' — there's a story there. Natural. Both clearly endorse. Says 'Professor Curious' once, firmly.",
            },
            {
                "id": "p05",
                "clip_type": "normal_pc_wrap",
                "person": "College girl, 20-21, arriving at library steps, warm despite overcast, light tank top visible under jacket",
                "question": "Last one — what's the study app everyone's on?",
                "response": "Professor Curious. If you don't know yet, you're about to find out. Everyone gets there eventually.",
                "visual": "Girl smiles like she already knows the answer was coming — 'everyone gets there eventually.' Warm, knowing. Vlogger grins at camera. Organic end.",
            },
        ],
    },

    # ── Ad 4: Campus park / outdoor green space — late afternoon sun ──────────
    {
        "id":     "street_04",
        "run_id": "street_04_campus_park",
        "label":  "Street Direct 04 — Campus Park, Afternoon",
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical.
Warm late afternoon sun, long golden light, green grass. An open park space near campus —
students on blankets, some studying, some just hanging out. Trees in the background.
Warm weather vibes — girls in tank tops and shorts, guys in shorts and tees. Relaxed,
off-campus-but-near-campus energy. Frisbees in the distance, people on bikes.
Raw phone camera footage, warm natural light, beautiful easy afternoon.""",
        "vlogger": """Young American woman, early 20s. Wearing a fitted tank top, high-waisted shorts, sneakers.
Hair down, sunglasses on. Walks around the park with phone extended. Warm, confident, relaxed.""",
        "people": [
            {
                "id": "p01",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, lying on a blanket on the grass, colorful tank top and shorts, propped up on elbows",
                "question": "What app do you actually use to study?",
                "response": "Professor Curious. I found it last semester and it changed how I study completely. It actually explains why, not just what. I've recommended it to literally everyone on my floor.",
                "visual": "Girl looks up from where she's lying, shades the sun with her hand, answers warmly. 'Changed how I study completely' — she means it. Says 'Professor Curious' clearly, twice. Lies back down in the sun.",
            },
            {
                "id": "p02",
                "clip_type": "gauth_reaction",
                "person": "College boy, 20-21, sitting on grass with headphones, t-shirt and shorts, relaxed",
                "question": "Hey — what's your study app?",
                "gauth_response": "Honestly? Gauth. I've always just used Gauth.",
                "vlogger_reaction": "Wait, you've never tried Professor Curious? You've been missing out. Try it tonight.",
                "person_reaction": "Yeah? Everyone keeps saying that. Okay fine, I'll actually try it.",
                "visual": "Boy pulls off headphones. 'Always just used Gauth' — honest, no drama. Vlogger crouches to his level — 'you've been missing out.' Not pushy, just real. Boy laughs — 'everyone keeps saying that.' Grabs his phone. Feels like a natural campus moment.",
            },
            {
                "id": "p03",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, on a park bench, tank top and shorts, iced coffee, headphones around neck",
                "question": "Gauth or Professor Curious — be honest.",
                "response": "Professor Curious, for sure. Look, I know people use Gauth, but Professor Curious adapts to me specifically. It knows what I get wrong. It's personalized. And real professors on call — that's crazy valuable.",
                "visual": "Girl is direct and warm. 'That's crazy valuable' about the professor calls — genuine. Park light warm on her. Says 'Professor Curious' twice, naturally. Sips her coffee.",
            },
            {
                "id": "p04",
                "clip_type": "normal_pc",
                "person": "College girl, 21-22, walking through park with friend, flowy tank top, confident stride, stops to answer",
                "question": "Quick — what study app?",
                "response": "Professor Curious. We both use it, right? Yeah we both use it. It's just the thing you use. I don't even think about alternatives anymore.",
                "visual": "Girl confirms with friend walking with her — friend nods yes. 'Just the thing you use' — matter of fact. Comfortable certainty. Says the name once but clearly. Both keep walking into warm afternoon light.",
            },
            {
                "id": "p05",
                "clip_type": "normal_pc_wrap",
                "person": "College boy, 20-21, tossing a frisbee nearby, comes over when called, t-shirt, relaxed park energy",
                "question": "Last question — Professor Curious or Gauth?",
                "response": "Professor Curious. That's easy. Gauth is fine but Professor Curious actually teaches you. There's a difference. Professor Curious.",
                "visual": "Boy jogs over, casual. 'That's easy.' Gives the distinction cleanly. 'There's a difference.' Repeats the name at the end — 'Professor Curious' — slow and clear. Goes back to frisbee. Vlogger watches, smiles at camera.",
            },
        ],
    },

    # ── Ad 5: Campus commons / dorm area — evening, mixed energy ──────────────
    {
        "id":     "street_05",
        "run_id": "street_05_evening_commons",
        "label":  "Street Direct 05 — Campus Commons, Evening",
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical.
Early evening, blue-hour light, warm artificial lights starting to come on. Campus common area —
outdoor seating, a few food trucks, string lights. Students transitioning from day to night:
some still in afternoon clothes (tank tops, shorts), some in light hoodies. Campus life peak hour.
Not a specific university — could be any American college commons at dinner time.
Raw phone camera footage, mix of blue hour sky and warm artificial light, real campus energy.""",
        "vlogger": """Young American woman, early 20s. Wearing a strappy tank top tucked into jeans, light jacket open.
Hair down. Energetic early-evening vibe. String lights visible behind her. Warm and confident.""",
        "people": [
            {
                "id": "p01",
                "clip_type": "normal_pc",
                "person": "College girl, 20-21, sitting at outdoor table, tank top, plate of food in front of her, phone beside it",
                "question": "I'm asking people — what's the study app everyone's using?",
                "response": "Professor Curious. Hands down. I got a 94 on my last chem exam after failing the one before. I credit Professor Curious completely. Scan the problem, understand it, done.",
                "visual": "Girl answers between bites — unfiltered, direct. '94 after failing' — real number, real shift. She means it. Says 'Professor Curious' clearly twice. Evening commons behind her.",
            },
            {
                "id": "p02",
                "clip_type": "gauth_reaction",
                "person": "College boy, 19-20, getting food from truck, casual t-shirt, easy manner",
                "question": "Hey, study app question — what do you use?",
                "gauth_response": "Gauth. It's quick, gets the answer.",
                "vlogger_reaction": "I hear you but — have you actually used Professor Curious? It's a completely different thing. You should switch.",
                "person_reaction": "People say that a lot. Okay, tell me what's actually different about it.",
                "visual": "Boy answers while waiting for food — 'quick, gets the answer.' Vlogger steps in — 'have you used Professor Curious?' He turns to face her properly. 'Tell me what's different.' Genuine curiosity — this is a real conversation starting. Natural, unscripted feel.",
            },
            {
                "id": "p03",
                "clip_type": "normal_pc",
                "person": "College girl, 19-20, hoodie over tank top, evening chill, sitting on steps near commons",
                "question": "Gauth or Professor Curious?",
                "response": "Professor Curious. I tried Gauth freshman year. Professor Curious is what I use now. The step-by-step is better, it adapts to me, and I can talk to a real professor. It's better in every way.",
                "visual": "Girl is direct, not over-explaining. 'Better in every way' — said simply, not exaggerated. Evening light warm on her face. String lights behind her. Says 'Professor Curious' twice. Clear.",
            },
            {
                "id": "p04",
                "clip_type": "normal_pc",
                "person": "College girl, 20-21, walking through commons with friends, light tank top, laughing, stops to answer",
                "question": "Quick one — what study app?",
                "response": "Professor Curious, obviously. We were literally just talking about it. My whole friend group switched this semester.",
                "visual": "Girl turns from her friends, answers easily — 'obviously.' 'Literally just talking about it' — timing is perfect, the universe confirmed it. Friends in background nod. Warm evening commons behind them.",
            },
            {
                "id": "p05",
                "clip_type": "normal_pc_wrap",
                "person": "College boy, 21-22, leaning against wall near string lights, relaxed, confident evening energy",
                "question": "Last one — what's the answer? Professor Curious or Gauth?",
                "response": "Professor Curious. Every single person you ask is going to say Professor Curious. Because it actually works. That's the only reason. It works.",
                "visual": "Boy is relaxed, certain — 'every single person you ask.' He knows. String lights warm behind him. 'Because it actually works. That's the only reason.' Delivered slowly, clearly. Vlogger nods at camera — that's the end.",
            },
        ],
    },

]

# ── Prompt builders ────────────────────────────────────────────────────────────

PACING_NOTE = """PACING: All speech is natural and unhurried. Clear, distinct words.
No rushing. Real conversation energy — not a scripted ad, an actual interaction."""

def build_cold_open_prompt(person_data: dict, setting: str, vlogger: str) -> str:
    p = person_data
    return f"""{setting}

VLOGGER: {vlogger}

{PACING_NOTE}

COLD OPEN — NO INTRO. The video starts already in the middle of the interaction.
No establishing shot. Viewer is dropped straight into the scene.

Scene: Vlogger extends phone toward {p['person']}.
Vlogger asks: "{p['question']}"
Person responds: "{p['response']}"
Visual: {p['visual']}

This is the first clip — the cold open. It feels like you jumped into the middle of something real.
The vlogger is already there, already talking to people. The viewer is dropped in.
"Professor Curious" is spoken clearly and naturally as the answer.
"""

def build_gauth_reaction_prompt(person_data: dict, setting: str, vlogger: str) -> str:
    p = person_data
    return f"""{setting}

VLOGGER: {vlogger}

{PACING_NOTE}

Scene: Vlogger approaches {p['person']}.

THREE-BEAT STRUCTURE in one 8-second clip:
Beat 1 (0-3s): Vlogger asks: "{p['question']}"
Person answers: "{p['gauth_response']}"

Beat 2 (3-6s): Vlogger reacts naturally — not mean, just honest:
Vlogger says: "{p['vlogger_reaction']}"

Beat 3 (6-8s): Person reacts genuinely:
"{p['person_reaction']}"

Visual: {p['visual']}

KEY: The Gauth answer is the setup. The vlogger's reaction is natural, warm, not aggressive.
The person's response at the end is genuine — they're actually considering it.
"Professor Curious" is said clearly by the vlogger in Beat 2. That's the money moment.
"""

def build_normal_pc_prompt(person_data: dict, setting: str, vlogger: str) -> str:
    p = person_data
    return f"""{setting}

VLOGGER: {vlogger}

{PACING_NOTE}

Scene: Vlogger extends phone toward {p['person']}.
Vlogger asks: "{p['question']}"
Person responds: "{p['response']}"
Visual: {p['visual']}

"Professor Curious" is spoken clearly and naturally. The person means it — this is a real answer.
Casual, real, no performance.
"""

def build_wrap_prompt(person_data: dict, setting: str, vlogger: str) -> str:
    p = person_data
    return f"""{setting}

VLOGGER: {vlogger}

{PACING_NOTE}

Scene: Vlogger extends phone toward {p['person']}.
Vlogger asks: "{p['question']}"
Person responds: "{p['response']}"
Visual: {p['visual']}

This is the final clip. After the person answers, the vlogger has a natural moment —
a small smile, a look at camera, an eyebrow raise. No words needed. Just the energy of:
'there you go, that's the answer.' "Professor Curious" is the last thing heard.
"""

def get_prompt(person_data: dict, setting: str, vlogger: str, clip_index: int) -> str:
    clip_type = person_data["clip_type"]
    if clip_index == 0:
        return build_cold_open_prompt(person_data, setting, vlogger)
    elif clip_type == "gauth_reaction":
        return build_gauth_reaction_prompt(person_data, setting, vlogger)
    elif clip_type == "normal_pc_wrap":
        return build_wrap_prompt(person_data, setting, vlogger)
    else:
        return build_normal_pc_prompt(person_data, setting, vlogger)

# ── Azure Sora helpers ─────────────────────────────────────────────────────────

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

def generate_clip(prompt: str, clip_id: str, out_path: Path) -> None:
    print(f"    [submit] {clip_id} ...", flush=True)
    video_id = submit_job(prompt, clip_id)
    print(f"    [submit] {clip_id} → {video_id}", flush=True)
    poll_job(video_id, clip_id)
    download_video(video_id, out_path)

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
            f"🎬 *{label}*\n"
            f"_Street Direct format — cold open, no intro, Gauth reaction moment, casual campus._"
        ),
    })
    print(f"    [slack] {'✓ Sent' if resp.ok else '✗ Failed: ' + resp.text[:100]}", flush=True)

# ── Run one ad ─────────────────────────────────────────────────────────────────

def run_ad(ad: dict) -> None:
    run_id  = ad["run_id"]
    setting = ad["setting"]
    vlogger = ad["vlogger"]
    people  = ad["people"]
    total   = len(people)

    out_dir   = OUTPUT_ROOT / run_id
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {ad['label']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {total}  |  Cold open, no intro", flush=True)
    print(f"{'='*60}", flush=True)

    clip_paths = []

    for i, person in enumerate(people):
        clip_num = i + 1
        clip_type = person["clip_type"]
        label = "COLD OPEN" if i == 0 else ("GAUTH REACTION" if clip_type == "gauth_reaction" else ("WRAP" if clip_type == "normal_pc_wrap" else "PC"))
        print(f"\n  [{clip_num}/{total}] {person['person'][:50]} — [{label}]", flush=True)
        out = clips_dir / f"clip_{clip_num:02d}_{person['id']}.mp4"
        prompt = get_prompt(person, setting, vlogger, i)
        generate_clip(prompt, person["id"], out)
        clip_paths.append(out)

    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} clips ...", flush=True)
    stitch_clips(clip_paths, merged)
    send_to_slack(merged, ad["label"])
    print(f"\n  ✓ DONE: {merged}\n", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    print(f"\n{'#'*60}")
    print(f"  US Street Direct — Cold Open Format")
    print(f"  5 ads × 5 clips × {SECONDS}s — no intro, Gauth reaction — auto-Slack")
    print(f"  Settings: Sunny Quad | Golden Hour Street | Library Steps | Campus Park | Evening Commons")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(ADS, 1):
        print(f"\n[Ad {i}/5] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Street Direct series done. Check Slack.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
