#!/usr/bin/env python3
"""
US Comparison Series — Professor Curious vs The Competition
5 ads, each built around one direct comparison at an elite US campus.

Professor Curious: scan any question → instant step-by-step explanation
+ live 1:1 real professor calls + adaptive to your weak areas.
Tagline: "#1 Homework Help Prof"

Ad 1: vs Khan Academy  — passive video vs your actual question
Ad 2: vs Chegg         — copying answers vs actual understanding
Ad 3: vs ChatGPT       — feeling smart vs being smart
Ad 4: vs Tutors        — $120/hr + scheduling vs 24/7 real professors
Ad 5: vs Quizlet       — memorizing vs understanding

Vlogger at elite US campuses, students making sharp, specific comparisons.
Auto-stitches and sends to Slack after each.

Usage:
  source ~/.env_azure
  python3 run_comparison.py
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
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-us-comparison"

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young American male, early 20s,
confident casual college-vlogger energy. Medium build, medium skin, short neat hair.
Wearing a neutral grey hoodie or plain white t-shirt, dark jeans. Holds phone up in
selfie-cam mode or points a small handheld mic toward subjects. Visible from chest up
on the left edge of frame. Energetic but natural — YouTube vlogger style, not TV reporter."""

# ── The 5 Comparison Ads ──────────────────────────────────────────────────────

COMPARISON_SERIES = [

    # ── 1. Professor Curious vs Khan Academy ──────────────────────────────────
    {
        "id":       "vs-khan",
        "run_id":   "us_cmp_01_vs_khan",
        "label":    "Professor Curious vs Khan Academy",
        "rival":    "Khan Academy",
        "campus":   "Harvard University, Johnston Gate, Cambridge MA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Crisp autumn afternoon,
golden New England light. Outside Harvard's Johnston Gate on Massachusetts Avenue.
Red-brick buildings, Harvard Yard visible behind. Students in hoodies and backpacks
streaming out, some with coffee, some on phones. Competitive, aspirational energy.
Raw iPhone footage, no color grading, natural handheld shake.""",
            "establishing": {
                "line":   "I'm outside Harvard right now. One question: what's the actual difference between Professor Curious and Khan Academy? Because everyone has an opinion on this.",
                "visual": """Vlogger walks toward Johnston Gate in selfie-cam, turns to show the iconic gate behind him.
Raises an eyebrow at camera — 'everyone has an opinion on this' energy.
Confident, a little provocative. Walks straight toward students to get the real answer.""",
            },
            "outro": {
                "line":   "Harvard students. Khan Academy vs Professor Curious. You heard the difference. Link in bio.",
                "visual": """Vlogger faces camera at the gate, students dispersing behind him.
Shrugs — the answer was clear. Slow, confident thumbs up. Lets it land.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Harvard junior girl", "age": "20-21",
                    "emotion": "precise and a little impatient — this is obvious to her",
                    "question": "Khan Academy vs Professor Curious — real difference?",
                    "response": "Khan Academy gives you a video about the topic. Professor Curious scans your exact question and explains that specific problem. That's a completely different thing. I spent two hours watching Khan Academy videos on integration and still missed the question. Took a photo on Professor Curious — understood it in four minutes. That's the difference.",
                    "visual": """Girl is precise — she's made this comparison herself and has a clear verdict.
'Two hours... four minutes' — she lets those numbers sit. They do the work.
Says 'Professor Curious' the second time slowly, clearly — that's the answer.
No drama, just evidence. Very Harvard.""",
                },
                {
                    "id": "p02", "type": "Harvard sophomore boy", "age": "19-20",
                    "emotion": "fair but definitive",
                    "question": "You used both — what's the actual gap?",
                    "response": "Khan Academy is amazing for building a foundation — I mean that genuinely. But when you're stuck on a specific problem at 11pm and you need that specific thing explained, Khan Academy can't do that. Professor Curious can. You scan it. It walks you through it. That's when I switched. That specific use case.",
                    "visual": """Boy is genuinely fair — credits Khan Academy, means it. That makes the comparison more credible.
'That specific use case' is said like an engineer identifying a gap.
Says 'Professor Curious' clearly in the middle — not at the end as an afterthought, mid-explanation.
Nods once. That's his verdict.""",
                },
                {
                    "id": "p03", "type": "Harvard senior girl", "age": "21-22",
                    "emotion": "sharp and slightly funny",
                    "question": "One line — what's the difference?",
                    "response": "Khan Academy teaches the subject. Professor Curious teaches you. There's a gap between those two sentences and it's the size of an SAT score. I figured that out junior year of high school and I've been telling everyone since.",
                    "visual": """Girl delivers 'Khan Academy teaches the subject. Professor Curious teaches you.' with a slight pause between.
Lets the line breathe — it's a real distinction.
'The size of an SAT score' — small laugh, but she means it completely.
Says 'Professor Curious' in the middle of the insight, clear and deliberate.""",
                },
            ],
        },
    },

    # ── 2. Professor Curious vs Chegg ─────────────────────────────────────────
    {
        "id":       "vs-chegg",
        "run_id":   "us_cmp_02_vs_chegg",
        "label":    "Professor Curious vs Chegg",
        "rival":    "Chegg",
        "campus":   "MIT, Massachusetts Avenue entrance, Cambridge MA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Grey overcast afternoon,
flat natural light. Outside MIT's main entrance on Massachusetts Avenue, Cambridge MA.
Iconic domed Building 10 visible in background. Students in MIT hoodies, carrying
laptops and problem sets — focused, fast-walking, driven. Raw phone camera footage,
no color grading, natural handheld movement.""",
            "establishing": {
                "line":   "MIT campus. I want to ask students something direct: what's the difference between using Chegg and using Professor Curious? Because I think people conflate them. They shouldn't.",
                "visual": """Vlogger walks through MIT entrance in selfie-cam, dome visible behind him.
Tone is direct, almost journalistic. 'People conflate them. They shouldn't.' — he means this.
Points at MIT students walking past. Goes to find someone to talk to.""",
            },
            "outro": {
                "line":   "Chegg gives you the answer. Professor Curious gives you the understanding. MIT students know which one actually matters. Link in bio.",
                "visual": """Vlogger at MIT entrance, dome behind him in fading afternoon light.
'Chegg gives you the answer. Professor Curious gives you the understanding.'
Says it slowly, clearly — two different products, two different outcomes.
Raises one eyebrow. Walks away.""",
            },
            "people": [
                {
                    "id": "p01", "type": "MIT sophomore boy", "age": "19-20",
                    "emotion": "analytical — this is a systems problem to him",
                    "question": "Chegg vs Professor Curious — what's the actual difference?",
                    "response": "Chegg optimizes for getting the answer. Professor Curious optimizes for getting the understanding. Those are different objective functions. I used Chegg freshman year of high school — got answers, didn't learn anything, failed the test. Professor Curious explains the reasoning. That's what shows up on exams. That's what got me here.",
                    "visual": """Boy is analytical — 'different objective functions' is MIT-speak and he means it.
'Failed the test' — he says it plainly, no shame. Data point.
At 'Professor Curious explains the reasoning' he becomes more present — this matters.
Says the name clearly. 'That's what got me here.' Final. True.""",
                },
                {
                    "id": "p02", "type": "MIT junior girl", "age": "20-21",
                    "emotion": "blunt and honest — she did both, she knows",
                    "question": "Did you use Chegg? Be honest.",
                    "response": "Yeah, in high school. A lot of people do. And I'll tell you exactly what happened — I understood nothing and felt like I understood everything. That's the dangerous part. Professor Curious doesn't give you the answer first. It walks you through the logic. You actually have to engage. That's uncomfortable but that's learning.",
                    "visual": """Girl says 'yeah' with zero shame — honest and direct.
'I understood nothing and felt like I understood everything' — she says this slowly. It lands.
'That's the dangerous part' — genuine warning, not a pitch.
Says 'Professor Curious' clearly. 'That's uncomfortable but that's learning.' Last line is the truth.""",
                },
                {
                    "id": "p03", "type": "MIT senior boy", "age": "21-22",
                    "emotion": "matter-of-fact, seen the consequences",
                    "question": "What do you tell freshman who are tempted by Chegg?",
                    "response": "I tell them: Chegg is a photocopy machine. Professor Curious is a professor. One gives you a copy of someone else's work. The other teaches you to do the work. MIT can tell the difference in the first midterm. So can Harvard. So can every school that matters. Use Professor Curious.",
                    "visual": """Boy is matter-of-fact — 'photocopy machine vs professor' is his analogy and it's clean.
Delivers it without drama, like explaining something obvious.
Says 'Professor Curious' twice — first as contrast, second as direct instruction.
The last line 'Use Professor Curious' is said looking directly at camera. A recommendation.""",
                },
            ],
        },
    },

    # ── 3. Professor Curious vs ChatGPT ──────────────────────────────────────
    {
        "id":       "vs-chatgpt",
        "run_id":   "us_cmp_03_vs_chatgpt",
        "label":    "Professor Curious vs ChatGPT",
        "rival":    "ChatGPT",
        "campus":   "Stanford University, White Plaza, Palo Alto CA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Warm California afternoon,
bright golden light, palm trees. Stanford's White Plaza, Palo Alto CA. Students in casual
California wear — t-shirts, Patagonia vests, Stanford lanyards. Some on bikes, some on grass,
startup energy meets academic energy. Raw phone camera footage, no color grading, beautiful warm light.""",
            "establishing": {
                "line":   "Stanford. Everyone here uses AI. So I want to ask the honest question: what's the difference between just asking ChatGPT and using Professor Curious? Is there one?",
                "visual": """Vlogger walks through White Plaza, palm trees and the Quad visible behind.
Tone is genuinely curious — not baiting, actually asking. 'Is there one?' — real question.
Students on grass and walking past. He moves toward a group to find out.""",
            },
            "outro": {
                "line":   "ChatGPT made them feel like they understood. Professor Curious made them actually understand. Stanford students noticed the difference. Link in bio.",
                "visual": """Vlogger faces camera, Quad in warm California light behind him.
'Feel like they understood... actually understand.' — he says both clearly, distinctly.
Small, knowing nod. Thumbs up. Walks off into the sun.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Stanford junior boy", "age": "20-21",
                    "emotion": "thoughtful — he's a CS student who has thought about this",
                    "question": "ChatGPT vs Professor Curious — honest take?",
                    "response": "ChatGPT will give you a confident answer. Whether it's right is another question. Professor Curious is built specifically for students — it scans your actual question, walks you through the steps, and if you're still lost you can get on a call with a real professor. ChatGPT can't do that last part. And that last part is sometimes the only thing that works.",
                    "visual": """Boy is thoughtful, CS-student energy — he's evaluated this technically.
'ChatGPT will give you a confident answer. Whether it's right is another question.' — wry, knowing.
At 'scans your actual question' he gestures like he's holding a phone up to a problem.
'A real professor' — says this with emphasis. Says 'Professor Curious' clearly both times.""",
                },
                {
                    "id": "p02", "type": "Stanford sophomore girl", "age": "19-20",
                    "emotion": "personal — she has a specific story",
                    "question": "Did you ever get burned by ChatGPT for studying?",
                    "response": "Junior year of high school. Chemistry. ChatGPT explained it beautifully — I felt totally prepared. Got to the test, something was off in the explanation, I'd learned it wrong. Professor Curious doesn't do that. It's built for students, it's checked, it walks you through the actual steps. And you can verify with a real professor. I don't use ChatGPT for studying anymore.",
                    "visual": """Girl is candid — this happened, it mattered, she changed.
'Explained it beautifully — I felt totally prepared' is delivered with irony. She knows now.
At 'Professor Curious doesn't do that' she straightens, more direct. Says the name clearly.
'I don't use ChatGPT for studying anymore.' Final. Simple. Earned.""",
                },
                {
                    "id": "p03", "type": "Stanford senior boy", "age": "21-22",
                    "emotion": "clear-eyed and practical",
                    "question": "One thing Professor Curious does that ChatGPT can't?",
                    "response": "Scans your question from a photo. Gives you a step-by-step breakdown designed for a student, not a general user. And puts you on a call with an actual professor if you need it. ChatGPT is a general intelligence. Professor Curious is a specialized education tool. For getting into and succeeding at a place like this — specialized wins every time.",
                    "visual": """Boy lists the three things specifically — one, two, three. Clear.
'General intelligence vs specialized education tool' — he says this like someone who understands the distinction.
Says 'Professor Curious' in the middle as the subject of his explanation, clearly and directly.
'Specialized wins every time' — the conclusion. He means it.""",
                },
            ],
        },
    },

    # ── 4. Professor Curious vs Expensive Tutors ──────────────────────────────
    {
        "id":       "vs-tutors",
        "run_id":   "us_cmp_04_vs_tutors",
        "label":    "Professor Curious vs Expensive Tutors",
        "rival":    "Private Tutors",
        "campus":   "Yale University, Phelps Gate, New Haven CT",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon,
gothic stone buildings, autumn leaves on ground. Yale's Phelps Gate on College Street,
New Haven CT. Students in Yale hoodies and scarves, walking through Old Campus.
Historic, serious, literary energy. Raw phone camera footage, moody golden-hour light.""",
            "establishing": {
                "line":   "Yale. I want to talk about the tutoring industrial complex for a second. Because not everyone can afford $120 an hour. I want to ask students — what did Professor Curious do that a tutor couldn't, or wouldn't?",
                "visual": """Vlogger stands at Phelps Gate, gothic buildings behind him.
'Tutoring industrial complex' — he says this pointedly. This is a real issue he's raising.
Tone is slightly serious — access and cost matter. He walks toward students.""",
            },
            "outro": {
                "line":   "Real professors. Available 24/7. A fraction of the cost. Professor Curious. Link in bio.",
                "visual": """Vlogger at the gate, Old Campus lit in evening light behind him.
Says the four lines like a list — deliberate, clear, each one landing.
No smile needed. The facts are the pitch. Slow nod. Walks in.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Yale sophomore girl", "age": "19-20",
                    "emotion": "honest about financial reality",
                    "question": "Did tutors play a role for you getting in — honest?",
                    "response": "My family couldn't do the $150 an hour tutor thing. I watched friends do it — they had someone available whenever, explaining things patiently, one on one. I found Professor Curious sophomore year and that's exactly what it is. You scan the question, you get a step-by-step breakdown, and if you need to you get on a call with a real professor. Same thing. Fraction of the price. I'm here.",
                    "visual": """Girl is honest — not bitter, just real about the financial gap.
'$150 an hour tutor thing' — she says it knowing what that means for some families.
At 'Professor Curious' she straightens slightly — this is her equalizer.
'Same thing. Fraction of the price. I'm here.' — delivered simply, powerfully. She made it.""",
                },
                {
                    "id": "p02", "type": "Yale junior boy", "age": "20-21",
                    "emotion": "comparing the experience directly",
                    "question": "What does Professor Curious do differently from a tutor?",
                    "response": "A tutor has limited availability, you have to schedule, and honestly — if you ask the same question three times you can see them getting frustrated. Professor Curious doesn't get frustrated. It doesn't run out of time. You can ask the same question ten ways and it will explain it ten ways. And if you need a live person, there's a real professor on call. That's actually better than most tutors I've had.",
                    "visual": """Boy is comparing directly — he's had tutors, he knows.
'You can see them getting frustrated' — specific, true, slightly uncomfortable to admit.
At 'Professor Curious doesn't get frustrated' he relaxes — relief in the observation.
'Real professor on call' — says this clearly. 'Better than most tutors I've had.' He means it.""",
                },
                {
                    "id": "p03", "type": "Yale senior girl", "age": "21-22",
                    "emotion": "access and equity — this matters to her",
                    "question": "What does it mean that Professor Curious is accessible to everyone?",
                    "response": "It means the kid whose parents can't spend $10,000 on SAT prep gets the same quality of help as the kid who can. Professor Curious gives you a real professor, step-by-step explanations, and it adapts to your weak areas. That used to cost thousands. Now it doesn't. That changes who gets to be in places like this.",
                    "visual": """Girl is measured and sincere — this is about equity, not just a product preference.
'$10,000 on SAT prep' — she names the real number. Some people know this number very well.
At 'Professor Curious gives you a real professor' she's clear and direct — says the name fully.
'That changes who gets to be in places like this.' — looks around at Yale. She knows.""",
                },
            ],
        },
    },

    # ── 5. Professor Curious vs Quizlet ──────────────────────────────────────
    {
        "id":       "vs-quizlet",
        "run_id":   "us_cmp_05_vs_quizlet",
        "label":    "Professor Curious vs Quizlet",
        "rival":    "Quizlet",
        "campus":   "Princeton University, Nassau Hall gate, Princeton NJ",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Sunny afternoon,
crisp autumn light. Outside Princeton's Nassau Hall gate, Princeton NJ. Stunning Gothic
and colonial architecture, green lawns, students in Princeton orange and black gear.
Bicycles everywhere. Serious, prestigious campus energy. Raw phone camera footage,
no color grading, natural handheld shake.""",
            "establishing": {
                "line":   "Princeton. I want to ask about something everyone uses but maybe misunderstands: Quizlet. Is memorizing the same as understanding? And what does Professor Curious do differently? Let's find out.",
                "visual": """Vlogger walks toward Nassau Hall gate in selfie-cam, iconic building visible behind.
'Is memorizing the same as understanding?' — he poses it as a real question, not rhetorical.
Slightly academic energy — this is Princeton after all. He approaches students directly.""",
            },
            "outro": {
                "line":   "Quizlet tests what you've memorized. Professor Curious builds what you understand. Princeton students know which one gets you here. Link in bio.",
                "visual": """Vlogger at Nassau Hall, late afternoon light on the historic building behind him.
Says the two sentences slowly — 'memorized... understand' — lets the distinction land.
'Princeton students know which one gets you here.' — quiet, confident.
One raised eyebrow. Walks away toward the building.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Princeton sophomore girl", "age": "19-20",
                    "emotion": "had an insight — the distinction changed her studying",
                    "question": "Quizlet vs Professor Curious — what's the real difference?",
                    "response": "Quizlet is for memorizing. Professor Curious is for understanding. I used to think those were the same thing. They're not. I could pass a Quizlet test on the French Revolution and not be able to write an essay about it. Professor Curious explains the why — the connections, the reasoning. That's what Princeton actually tests. That's what every college actually tests.",
                    "visual": """Girl is articulate — she's had this insight and it changed her.
'I used to think those were the same thing. They're not.' — said with real conviction.
The French Revolution example is specific and vivid.
Says 'Professor Curious' clearly — it's the thing that showed her the difference.
'That's what every college actually tests.' — broad, confident, true.""",
                },
                {
                    "id": "p02", "type": "Princeton junior boy", "age": "20-21",
                    "emotion": "practical and direct",
                    "question": "When does Quizlet fail you?",
                    "response": "When the question is slightly different from the flashcard. Quizlet prepares you for the exact question. Real exams don't ask exact questions — they ask variations. Professor Curious teaches you the concept so any variation of the question is answerable. I used Quizlet for years. Switched to Professor Curious before my SATs. 1520 to 1570. That's the gap.",
                    "visual": """Boy is practical — the 'slightly different from the flashcard' observation is real and sharp.
Score improvement: '1520 to 1570' — said matter-of-factly. Real numbers.
Says 'Professor Curious' clearly in the middle — the switch that made the difference.
'That's the gap.' Two words. Walks away confident.""",
                },
                {
                    "id": "p03", "type": "Princeton senior girl", "age": "21-22",
                    "emotion": "retrospective — she figured this out the hard way",
                    "question": "What do you wish you'd known earlier about how to study?",
                    "response": "That memorizing and understanding are different skills. I was a Quizlet power user — decks for everything, color coded, perfect recall. And then I'd hit a question that asked me to apply the concept and I'd freeze. Professor Curious fixes that. It doesn't just tell you what — it tells you why and how. I found it junior year. I think about what would have happened if I'd found it freshman year.",
                    "visual": """Girl is retrospective — genuinely thinking about what she would have done differently.
'Quizlet power user' — she almost laughs at her past self. She really was.
'I'd freeze' — said simply, the honesty of it.
Says 'Professor Curious' clearly. 'What would have happened if I'd found it freshman year.'
That last sentence is directed at every high schooler watching. She knows it.""",
                },
            ],
        },
    },

]

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict, rival: str) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {e['visual']}
Vlogger speaking to camera in English: "{e['line']}"

TONE: Direct, confident, a little journalistic. This is a real comparison, not a dismissal.
The rival app ({rival}) is named fairly — students will feel the comparison is honest.
HOOK: First 2 seconds must create immediate curiosity. The comparison question is the hook.
Raw vlog energy — unscripted, on campus, real.
"""

def build_person_prompt(person: dict, scene: dict, rival: str) -> str:
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: Vlogger approaches {person['type']}, age {person['age']}, on campus.

Vlogger asks in English: "{person['question']}"
Student responds in English: "{person['response']}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first 3-4 seconds): The honest assessment of {rival} — fair, specific, not dismissive.
The student has used both. They know both. This credibility is essential.
Act 2 (next 3-4 seconds): "{PRODUCT}" — the specific thing it does differently.
The name spoken clearly, deliberately. A visible shift to conviction.

KEY: The comparison must feel fair. Students who still use {rival} should nod along, not feel attacked.
The "{PRODUCT}" advantage must be specific — scan technology, step-by-step, real professors, adaptive.
American college student energy — relaxed, direct, no performance.
"""

def build_outro_prompt(scene: dict, rival: str) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks to camera in English: "{o['line']}"

The comparison is made. "{PRODUCT}" won on specifics, not hype.
Understated confidence. The campus behind him says everything about who agrees.
"""

# ── Azure Sora + Slack helpers (identical to other scripts) ───────────────────

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
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    print(f"    [stitch] → {output_path.name}", flush=True)

def send_to_slack(video_path: Path, label: str, rival: str) -> None:
    print(f"    [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    requests.post(SLACK_URL, data={
        "channel_id": SLACK_CHANNEL,
        "text": f"🇺🇸 *US Comparison — {label}*\n_Professor Curious vs {rival} — Elite campus students explain the difference._",
    })
    print(f"    [slack] {'✓ Sent' if resp.ok else '✗ Failed: ' + resp.text[:100]}", flush=True)

def run_ad(ad: dict) -> None:
    scene   = ad["scene"]
    run_id  = ad["run_id"]
    rival   = ad["rival"]
    people  = scene["people"]
    total   = len(people) + 2

    out_dir   = OUTPUT_ROOT / run_id
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {ad['label']}", flush=True)
    print(f"  Campus : {ad['campus']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {total}", flush=True)
    print(f"{'='*60}", flush=True)

    clip_paths = []

    print(f"\n  [1/{total}] Establishing — COMPARISON HOOK", flush=True)
    out = clips_dir / "clip_01_establishing.mp4"
    generate_clip(build_establishing_prompt(scene, rival), "establishing", out)
    clip_paths.append(out)

    for i, person in enumerate(people, start=2):
        print(f"\n  [{i}/{total}] {person['type']} ({person['emotion']})", flush=True)
        out = clips_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_clip(build_person_prompt(person, scene, rival), person["id"], out)
        clip_paths.append(out)

    print(f"\n  [{total}/{total}] Outro", flush=True)
    out = clips_dir / f"clip_{total:02d}_outro.mp4"
    generate_clip(build_outro_prompt(scene, rival), "outro", out)
    clip_paths.append(out)

    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} clips ...", flush=True)
    stitch_clips(clip_paths, merged)
    send_to_slack(merged, ad["label"], rival)
    print(f"\n  ✓ DONE: {merged}\n", flush=True)

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    print(f"\n{'#'*60}")
    print(f"  US Comparison Series — Professor Curious")
    print(f"  5 ads × 5 clips × {SECONDS}s — auto-sends to Slack")
    print(f"  Rivals: Khan Academy | Chegg | ChatGPT | Tutors | Quizlet")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(COMPARISON_SERIES, 1):
        print(f"\n[Ad {i}/5] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  US Comparison Series complete. Check Slack.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
