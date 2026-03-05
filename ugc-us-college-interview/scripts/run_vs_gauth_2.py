#!/usr/bin/env python3
"""
Professor Curious vs Gauth AI — 5 More US College Ads (Batch 2)
Yale, Princeton, Columbia, UCLA, UPenn

Same format: logo overlays, 8s clips, auto-Slack.
Gauth logo (0-4s) → PC logo (4-8s) when Gauth mentioned first.
PC logo full clip when student goes straight to Professor Curious.
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

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young American male, early 20s,
confident casual college-vlogger energy. Medium build, medium skin, short neat hair.
Wearing a neutral grey hoodie or plain white t-shirt, dark jeans. Holds phone up in
selfie-cam mode or points a small handheld mic toward subjects. Visible from chest up
on the left edge of frame. Energetic but natural — YouTube vlogger style, not TV reporter."""

ADS = [

    # ── Ad 1: Yale ────────────────────────────────────────────────────────────
    {
        "id":     "vs-gauth-yale",
        "run_id": "gauth_04_yale",
        "label":  "PC vs Gauth — Yale",
        "campus": "Yale University, Phelps Gate, New Haven CT",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon,
gothic stone buildings, autumn leaves on cobblestones. Yale's Phelps Gate on College Street,
New Haven CT. Students in Yale hoodies and scarves walking through Old Campus.
Historic, literary, serious energy. Raw phone camera footage, moody golden-hour light.""",
            "establishing": {
                "line":   "I'm at Yale right now. Super simple question: Gauth or Professor Curious — which one do people actually use here, and why?",
                "visual": """Vlogger stands at Phelps Gate in selfie-cam, gothic stone arch behind him.
Points at two raised fingers — two options. Walks toward students streaming through.""",
            },
            "outro": {
                "line":   "Yale students. Gauth or Professor Curious. You heard it. Link in bio.",
                "visual": """Vlogger at the gate, Old Campus evening light behind him.
Simple nod — the answer came through clearly. Thumbs up. Walks in.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Yale junior girl", "age": "20-21",
                    "emotion": "literary, precise — she's thought about this",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — honest take?",
                    "response": "I used Gauth for a semester sophomore year. It solves the problem in front of you. Professor Curious solves the problem and then asks — do you actually understand this? It adapts to your gaps. It has real professors on call. For someone going to law school or grad school, that difference is everything. Professor Curious. It's not even close.",
                    "visual": """Girl is measured, precise — she's a thinker. Slight pause before answering.
'Gauth for a semester' — honest, she tried it properly.
'Do you actually understand this?' — she says this slowly. That's the insight.
'Professor Curious' — said the second time with real certainty. Final.""",
                },
                {
                    "id": "p02", "type": "Yale sophomore boy", "age": "19-20",
                    "emotion": "switched recently — still feels the contrast",
                    "gauth_first": True,
                    "question": "Which one and when did you switch?",
                    "response": "I was on Gauth all of high school. It felt efficient — get the answer, move on. Then first semester here someone showed me Professor Curious and I realized efficient isn't the same as effective. Gauth was getting me through homework. Professor Curious was getting me through exams. I've recommended it to every freshman I've met.",
                    "visual": """Boy has real energy — the contrast between 'efficient' and 'effective' is his key insight.
'Gauth was getting me through homework. Professor Curious was getting me through exams.'
He slows down on this line — it's the real distinction.
Says 'Professor Curious' clearly three times. The last one is the recommendation.""",
                },
                {
                    "id": "p03", "type": "Yale senior girl", "age": "21-22",
                    "emotion": "definitive — she knows what works",
                    "gauth_first": False,
                    "question": "Quick answer — which one?",
                    "response": "Professor Curious. Full stop. I know Gauth — I'm not dismissing it. But Professor Curious scans your specific question, walks you through it step by step, adapts to what you don't know, and if you're really stuck there's a real professor on call. It's the only app I know that does all four of those things. Professor Curious. End of conversation.",
                    "visual": """Girl says 'Professor Curious. Full stop.' immediately — zero hesitation.
Lists the four things like she's explained this before — scan, step-by-step, adaptive, real professor.
'End of conversation' — slight smile. She means it. Says the name twice, both completely clear.""",
                },
            ],
        },
    },

    # ── Ad 2: Princeton ───────────────────────────────────────────────────────
    {
        "id":     "vs-gauth-princeton",
        "run_id": "gauth_05_princeton",
        "label":  "PC vs Gauth — Princeton",
        "campus": "Princeton University, Nassau Hall gate, Princeton NJ",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Sunny autumn afternoon,
crisp light. Outside Princeton's Nassau Hall gate, Princeton NJ. Gothic and colonial
architecture, green lawns, students in Princeton orange and black. Bicycles everywhere.
Serious, prestigious campus energy. Raw phone camera footage, natural handheld shake.""",
            "establishing": {
                "line":   "Princeton. One question for students: Gauth or Professor Curious. I want real answers.",
                "visual": """Vlogger walks toward Nassau Hall in selfie-cam, historic building behind him.
Direct, confident. Points at gate — Princeton. Immediately moves toward students.""",
            },
            "outro": {
                "line":   "Princeton students. Gauth versus Professor Curious. Clear answer. Link in bio.",
                "visual": """Vlogger at Nassau Hall, late afternoon sun behind him.
Confident, simple. Raises one finger — one answer. Nods. Walks away.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Princeton junior boy", "age": "20-21",
                    "emotion": "analytical — he's compared both rigorously",
                    "gauth_first": True,
                    "question": "Gauth vs Professor Curious — what's your take?",
                    "response": "I've used both extensively. Gauth is fast — fast answer, move on. Professor Curious is thorough — it explains the reasoning, adapts to what I specifically get wrong, and if I still don't get it I can talk to a real professor. In the short term Gauth is faster. In the long term Professor Curious is smarter. For a place like this, you play the long game. Professor Curious.",
                    "visual": """Boy is analytical — 'extensively' is the right word for how he approaches things.
'Short term faster. Long term smarter.' — he lets this land. It's a real distinction.
'You play the long game' — looking around at Princeton. He knows where he is.
Says 'Professor Curious' clearly at the end — the long game answer.""",
                },
                {
                    "id": "p02", "type": "Princeton sophomore girl", "age": "19-20",
                    "emotion": "warm and completely sure",
                    "gauth_first": False,
                    "question": "Which one — and why?",
                    "response": "Professor Curious — and honestly the answer is the live professor calls. I can scan any question, get a step-by-step breakdown, and if that's not enough I call an actual professor. Gauth can't do that last part. And that last part is the thing that actually gets you unstuck. Professor Curious every time.",
                    "visual": """Girl is warm but sure — 'the live professor calls' is her reason and she means it.
'Scan any question... step-by-step... call an actual professor.' — three things, clear order.
'That's the thing that actually gets you unstuck.' — real. She's been stuck, she knows.
Says 'Professor Curious' twice. Both clearly. Smiles at the end.""",
                },
                {
                    "id": "p03", "type": "Princeton senior boy", "age": "21-22",
                    "emotion": "been the person who gives this advice",
                    "gauth_first": True,
                    "question": "What do you tell people who ask you what to use?",
                    "response": "I tell them: Gauth if you're in a rush and you just need the answer right now. Professor Curious if you actually want to learn. Most people think they just need the answer. But tests don't give you the same question twice. You need to understand the concept. Professor Curious builds that. Gauth doesn't. That's the honest answer.",
                    "visual": """Boy has given this advice before — he's the guy people ask.
'Gauth if you're in a rush.' — fair, honest. One sentence.
'Professor Curious if you actually want to learn.' — the contrast is the lesson.
'Tests don't give you the same question twice.' — that line is the point. He says it clearly.
'Professor Curious builds that. Gauth doesn't.' — final, fair, true.""",
                },
            ],
        },
    },

    # ── Ad 3: Columbia ────────────────────────────────────────────────────────
    {
        "id":     "vs-gauth-columbia",
        "run_id": "gauth_06_columbia",
        "label":  "PC vs Gauth — Columbia",
        "campus": "Columbia University, Low Library steps, New York City",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Overcast New York afternoon.
Columbia University, Low Library steps, Morningside Heights, NYC. Classic neoclassical dome
building, wide stone steps with students sitting, studying, talking. NYC energy — fast,
confident, diverse, ambitious. Raw phone camera footage, natural urban light.""",
            "establishing": {
                "line":   "Columbia University, New York City. One question: Gauth or Professor Curious — and I want the real answer.",
                "visual": """Vlogger stands at base of Low Library steps, iconic dome behind him.
NYC energy — confident, direct. Raises both hands, palms up — 'two options.'
Immediately moves toward students on the steps.""",
            },
            "outro": {
                "line":   "Columbia. New York. Gauth or Professor Curious. They told you. Link in bio.",
                "visual": """Vlogger at Low Library, NYC skyline faintly visible beyond campus.
Slight smile — NYC people give real answers. Thumbs up. Walks off down the steps.""",
            },
            "people": [
                {
                    "id": "p01", "type": "Columbia junior girl", "age": "20-21",
                    "emotion": "NYC direct — no filter, clear verdict",
                    "gauth_first": False,
                    "question": "Gauth or Professor Curious?",
                    "response": "Professor Curious. I'll tell you exactly why. It scans the actual problem — not the topic, the problem. It walks through it step by step. It adapts to what I specifically get wrong. And if I'm really stuck there are real professors I can actually talk to. I've used Gauth. It's fine. Professor Curious is another level. That's just the truth.",
                    "visual": """Girl is NYC direct — no preamble, just 'Professor Curious' and then the reasons.
Lists them fast but clearly — scan, step-by-step, adaptive, real professors.
'I've used Gauth. It's fine.' — said with a shrug. Genuine.
'Professor Curious is another level. That's just the truth.' — says the name clearly, final line.""",
                },
                {
                    "id": "p02", "type": "Columbia sophomore boy", "age": "19-20",
                    "emotion": "came in skeptical, converted",
                    "gauth_first": True,
                    "question": "You were skeptical at first — what changed?",
                    "response": "Freshman year I was fully on Gauth. Everyone at my high school used it. I thought Professor Curious was just another app. Then I actually tried it for a week and I realized — Gauth gives you answers. Professor Curious gives you understanding. That sounds cheesy but it showed up on my midterms. I don't touch Gauth anymore. Professor Curious only.",
                    "visual": """Boy is honest about his skepticism — 'just another app' is what he thought.
'I actually tried it for a week' — he gave it a real test.
'Showed up on my midterms.' — the proof. He says it simply, no drama.
'Professor Curious only.' — final, said looking directly at camera. Clear.""",
                },
                {
                    "id": "p03", "type": "Columbia senior girl", "age": "21-22",
                    "emotion": "retrospective — she's finishing up and can see the whole picture",
                    "gauth_first": True,
                    "question": "Looking back — Gauth or Professor Curious?",
                    "response": "Gauth got me through a lot of homework junior and senior year of high school. I'm not going to lie about that. But Professor Curious got me to actually understand things. And here's the real difference — Gauth helped me complete assignments. Professor Curious helped me think. Columbia tests how you think, not whether you can find an answer. Professor Curious. Every time.",
                    "visual": """Girl is retrospective — she's a senior, she can see the whole arc.
'Gauth got me through a lot of homework' — genuine credit. She's not being unfair.
'Professor Curious helped me think.' — said slowly. That's the distinction.
'Columbia tests how you think.' — looks around. She knows. 'Professor Curious' said clearly at end.""",
                },
            ],
        },
    },

    # ── Ad 4: UCLA ────────────────────────────────────────────────────────────
    {
        "id":     "vs-gauth-ucla",
        "run_id": "gauth_07_ucla",
        "label":  "PC vs Gauth — UCLA",
        "campus": "UCLA, Royce Hall, Westwood, Los Angeles CA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Bright California afternoon,
warm golden light, blue sky. UCLA campus, Royce Hall quadrangle, Westwood, Los Angeles CA.
Romanesque brick buildings, palm trees, students in UCLA gear on grass and walkways.
Warm, open, California optimism energy. Raw phone camera footage, beautiful sunny light.""",
            "establishing": {
                "line":   "UCLA. I'm asking one question: Gauth or Professor Curious — which one do you actually use and which one actually helps?",
                "visual": """Vlogger walks through Royce Hall quad in selfie-cam, iconic red brick building behind him.
California energy — warm, open, direct. Points at the campus. Goes straight toward students.""",
            },
            "outro": {
                "line":   "UCLA students. Gauth versus Professor Curious. You got the real answer. Link in bio.",
                "visual": """Vlogger faces camera, Royce Hall in warm LA afternoon light behind him.
Easy California smile — these were real, straight answers. Thumbs up. Walks off.""",
            },
            "people": [
                {
                    "id": "p01", "type": "UCLA junior boy", "age": "20-21",
                    "emotion": "warm California energy, completely converted",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — which one?",
                    "response": "Okay so I used Gauth all through high school — like religiously. And it was useful. But Professor Curious changed how I actually study. It scans the problem, it walks through every step, it knows where I'm weak and it targets that. And if I need to talk to a real professor I can. Gauth is fine. Professor Curious is a different game. Completely different.",
                    "visual": """Boy is warm, enthusiastic — 'like religiously' about Gauth in high school is honest.
'Changed how I actually study' — this is a real shift, he means it.
'A different game. Completely different.' — the repeat adds energy. He's convinced.
Says 'Professor Curious' clearly twice. Both times with real emphasis.""",
                },
                {
                    "id": "p02", "type": "UCLA sophomore girl", "age": "19-20",
                    "emotion": "practical and direct",
                    "gauth_first": False,
                    "question": "Which one — no thinking, just say it.",
                    "response": "Professor Curious. Easy. I've tried other stuff — Gauth, Photomath, ChatGPT for homework. Professor Curious is the only one that adapts to me specifically. It learns what I struggle with and hits that. And the professor calls — that's something else. I've had three sessions with real professors on there. That's not something any other app does. Professor Curious.",
                    "visual": """Girl says 'Professor Curious. Easy.' immediately — totally relaxed about it.
Lists the other apps she's tried — thorough, fair. She's compared properly.
'The professor calls — that's something else.' — says this with genuine appreciation.
'Three sessions with real professors.' — concrete, real. Says 'Professor Curious' at the end clearly.""",
                },
                {
                    "id": "p03", "type": "UCLA senior boy", "age": "21-22",
                    "emotion": "matter-of-fact — this is just the better product",
                    "gauth_first": True,
                    "question": "What's the real difference between Gauth and Professor Curious?",
                    "response": "Gauth answers your question. Professor Curious teaches you to answer the question yourself. That sounds small but it compounds. Every time Professor Curious explains something to me — with steps, with the reasoning — I can do the next similar problem without help. Gauth didn't do that. It kept me dependent. Professor Curious made me better. That's the real difference.",
                    "visual": """Boy is matter-of-fact — he's identified a real distinction and he's clean about it.
'Answers your question vs teaches you to answer the question yourself.' — says this slowly.
'It kept me dependent.' — said about Gauth. Honest assessment, no heat.
'Professor Curious made me better.' — final four words. Said directly. True.""",
                },
            ],
        },
    },

    # ── Ad 5: UPenn ───────────────────────────────────────────────────────────
    {
        "id":     "vs-gauth-upenn",
        "run_id": "gauth_08_upenn",
        "label":  "PC vs Gauth — UPenn",
        "campus": "University of Pennsylvania, College Hall, Philadelphia PA",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Crisp autumn afternoon.
University of Pennsylvania, College Hall front steps, Philadelphia PA. Classic collegiate
Gothic architecture, red brick, green lawns. Students in Penn hoodies and backpacks,
Wharton students in business casual, mix of ambitious energy. Raw phone camera footage,
natural handheld movement, clear autumn light.""",
            "establishing": {
                "line":   "UPenn. Quick question for students: Gauth or Professor Curious — which one is actually worth it?",
                "visual": """Vlogger at College Hall steps, historic building behind him.
Direct and confident. 'Which one is actually worth it?' — practical framing for a practical school.
Walks toward students immediately.""",
            },
            "outro": {
                "line":   "UPenn students. Gauth or Professor Curious. Now you know. Link in bio.",
                "visual": """Vlogger at College Hall steps, Philadelphia afternoon light.
Confident, simple. Nods once. Thumbs up. Walks up the steps.""",
            },
            "people": [
                {
                    "id": "p01", "type": "UPenn Wharton junior girl", "age": "20-21",
                    "emotion": "ROI mindset — she thinks in terms of outcomes",
                    "gauth_first": True,
                    "question": "Gauth or Professor Curious — which has better ROI?",
                    "response": "ROI question — I love it. Gauth: low time investment, you get the answer, you move on. Professor Curious: higher time investment, you understand the concept, you can apply it anywhere. On a test. In a job interview. In a consulting case. The ROI on actually understanding something is infinite. Gauth is a short-term play. Professor Curious is a long-term asset. I'm Wharton — I pick the asset.",
                    "visual": """Girl is in Wharton mode — this is literally a return on investment question and she loves it.
'Low time investment... higher time investment' — she's running the comparison.
'The ROI on actually understanding something is infinite.' — she lets this land.
'I'm Wharton — I pick the asset.' — slight smile. Says 'Professor Curious' clearly as the asset.""",
                },
                {
                    "id": "p02", "type": "UPenn junior boy", "age": "20-21",
                    "emotion": "honest comparison, real user of both",
                    "gauth_first": True,
                    "question": "You've used both — what's the real talk?",
                    "response": "Real talk? Gauth is like a shortcut. Professor Curious is like a tutor. I used Gauth for two years — got answers, passed assignments, forgot everything by the next test. Professor Curious changed that. Step-by-step breakdowns, it adapts to what I keep getting wrong, and there are real professors I can actually call. For actually learning — Professor Curious. There's nothing close.",
                    "visual": """Boy is straight — 'real talk' is the framing and he delivers it.
'Got answers, passed assignments, forgot everything.' — said simply. The pattern is the lesson.
'Professor Curious changed that.' — he straightens slightly. Real shift.
Says 'Professor Curious' clearly twice. 'There's nothing close.' — final.""",
                },
                {
                    "id": "p03", "type": "UPenn senior girl", "age": "21-22",
                    "emotion": "has recruited friends to PC — she's an advocate",
                    "gauth_first": False,
                    "question": "Which one — and have you told anyone?",
                    "response": "Professor Curious. And yes — I've told my younger brother, two cousins, three friends applying to college this year. All of them. Because Professor Curious actually teaches you. It scans your specific problem. It finds what you don't know and focuses on that. And if you need a human — a real professor — it has that too. I wouldn't recommend something this hard if it wasn't worth it. Professor Curious.",
                    "visual": """Girl is an advocate — the list of people she's told is the proof.
'My younger brother, two cousins, three friends.' — counts them out. She's serious about this.
'I wouldn't recommend something this hard if it wasn't worth it.' — honest. It takes effort.
Says 'Professor Curious' at the start and end — bookends the whole answer. Both times clear.""",
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
            f"🇺🇸 *{label}*\n"
            f"_Professor Curious vs Gauth — logo overlays. Batch 2._\n"
            f"Gauth logo (0-4s) → Professor Curious logo (4-8s)."
        ),
    })
    print(f"    [slack] {'✓ Sent' if resp.ok else '✗ Failed: ' + resp.text[:100]}", flush=True)


def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {e['visual']}
Vlogger speaking to camera in English: "{e['line']}"

HOOK: First 2 seconds — vlogger names BOTH apps clearly. The comparison is the hook.
Raw vlog energy. Students about to give real, unfiltered opinions.
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
Act 2 ({pc_timing}): "Professor Curious" — name spoken clearly, out loud, enthusiastically.
The shift in energy is visible. "Professor Curious" must be unmistakably heard.

Both app names clearly spoken as recognizable brand names.
American college student energy — casual, direct, credible.
"""


def build_outro_prompt(scene: dict) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks to camera in English: "{o['line']}"
Understated. The campus and students said everything.
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
    print(f"  {ad['label']}", flush=True)
    print(f"  Campus : {ad['campus']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {total}", flush=True)
    print(f"{'='*60}", flush=True)

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


def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}.")

    print(f"\n{'#'*60}")
    print(f"  Professor Curious vs Gauth — Batch 2")
    print(f"  5 ads × 5 clips × {SECONDS}s — logos embedded — auto-Slack")
    print(f"  Campuses: Yale | Princeton | Columbia | UCLA | UPenn")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(ADS, 1):
        print(f"\n[Ad {i}/5] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Done. Check Slack for 5 logo-embedded ads.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
