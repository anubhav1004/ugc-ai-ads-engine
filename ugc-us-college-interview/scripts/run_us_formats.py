#!/usr/bin/env python3
"""
5 US Ad Formats — Professor Curious
Tests which creative format performs best on TikTok/Instagram Reels.

Format 1: Raw Confession (Talking Head)
  - Single girl, close to camera, confessional energy, desk/bedroom
  - Emotional problem → revelation → result → CTA

Format 2: Roommate Skit (Two-Person Drama)
  - Struggling roommate + roommate with the app, 2am dorm room
  - Frustration → intervention → discovery → payoff

Format 3: Library Whisper (ASMR/Secret)
  - Girl in library, whispers to camera like sharing forbidden knowledge
  - Curiosity gap → features → proof → "don't tell everyone"

Format 4: Study Group Savior (Group Social Proof)
  - 4 students at library table, all lost → one has the app → saves everyone
  - Chaos → calm → understanding → group endorsement

Format 5: App Ranking (Direct Comparison Review)
  - Single girl at desk, tested every app, gives verdict
  - Teases comparison → ChatGPT loses → Gauth loses → PC wins clearly

Each ad:
  - 4 clips × 8s = ~32s (optimum for TikTok/Reels completion rate)
  - Custom hooks (4 variations) overlaid via Pillow
  - Gauth VS PC logos centered (for brand recognition)
  - Auto-sent to Slack
"""

import json
import os
import requests
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

API_KEY       = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT      = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL         = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL      = f"{ENDPOINT}/openai/v1"
HEADERS       = {"api-key": API_KEY}
SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-us-formats"
ASSETS_DIR    = Path.home() / "ugc-ai-ads-engine" / "assets"
GAUTH_LOGO    = ASSETS_DIR / "gauth_logo.png"
PC_LOGO       = ASSETS_DIR / "pc_logo.png"
IMPACT_FONT   = "/System/Library/Fonts/Supplemental/Impact.ttf"
ARIAL_BOLD    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
VW, VH        = 720, 1280

# ─────────────────────────────────────────────────────────────────────────────
# AD DEFINITIONS
# Each ad has: id, run_id, label, format_type, clips (4), hooks (4 variations)
# ─────────────────────────────────────────────────────────────────────────────

ADS = [

    # ── FORMAT 1: RAW CONFESSION (Talking Head) ──────────────────────────────
    {
        "id":          "fmt_01_confession",
        "run_id":      "fmt_01_confession",
        "label":       "Format 1 — Raw Confession (Talking Head)",
        "format_type": "talking_head",
        "hooks": [
            {"id": "h1", "lines": ["I went from a 40% midterm", "to an 87 on the final.", "Here's exactly how."]},
            {"id": "h2", "lines": ["The app that saved my GPA", "when nothing else worked."]},
            {"id": "h3", "lines": ["POV: being completely honest", "about how you actually passed", "your hardest class"]},
            {"id": "h4", "lines": ["Every struggling student needs", "to know about Professor Curious."]},
        ],
        "char_lock": """CONTINUITY — SAME PERSON IN ALL CLIPS: College junior girl, 20-21.
Dark hair in a messy bun or down. Natural, minimal makeup. Wearing an oversized college sweatshirt.
Sitting at her desk in her dorm/bedroom — textbooks visible behind her, warm desk lamp light.
Speaks directly to camera, no teleprompter energy — raw, real, slightly vulnerable.
She is NOT performing. She is talking to a friend. Close frame, face fills most of the shot.""",
        "clips": [
            {
                "id": "clip_01_hook",
                "desc": "HOOK — emotional problem statement, first 3 seconds must land hard",
                "prompt": """Raw smartphone camera footage, 9:16 vertical. Warm desk lamp light. College dorm room.

PERSON: College junior girl, 20-21. Dark hair messy bun. Oversized college sweatshirt.
Sitting at desk, textbooks in background. Speaking directly to camera. Very close frame.
NOT performing — talking to a friend. Raw, real, slightly vulnerable energy.

HOOK — She leans slightly forward to camera, voice low and direct:
"Okay I need to tell you something about how I actually passed Organic Chemistry.
Because the real answer is embarrassing and no one talks about it."

First 3 seconds: she looks directly at camera with a slightly uncomfortable honesty.
The admission already hooks — she clearly has something real to share.
"Organic Chemistry" spoken clearly. "Professor Curious" is the answer she hasn't said yet — but she knows it.
"""
            },
            {
                "id": "clip_02_problem",
                "desc": "THE PROBLEM — the failure, make it real and specific",
                "prompt": """Raw smartphone camera footage, 9:16 vertical. Warm desk lamp light. College dorm room.

CONTINUITY: Same girl as clip_01. Same desk, same sweatshirt. Same close frame, direct camera.

She talks about the failure. Not dramatic — just honest:
"I got a 40 on my Orgo midterm. Not like a 'bad B' 40. A literal 40 out of 100.
I had gone to every lecture. I'd used every app. ChatGPT, Gauth, Khan Academy. Nothing clicked.
I genuinely thought I was going to have to retake it."

Speaks at a natural, honest pace. Slightly embarrassed remembering it.
"ChatGPT" "Gauth" "Khan Academy" all said clearly.
The authenticity is the hook — this is a real student, not an actor.
"""
            },
            {
                "id": "clip_03_discovery",
                "desc": "THE DISCOVERY — Professor Curious revealed, features explained naturally",
                "prompt": """Raw smartphone camera footage, 9:16 vertical. Warm desk lamp light. College dorm room.

CONTINUITY: Same girl. Same desk, same sweatshirt. Same close frame, direct camera.

The turning point — she discovered Professor Curious:
"My roommate told me to try this app called Professor Curious.
I scanned my exact problem — not a topic, the actual problem I was stuck on.
It broke down every single step. It found the specific part where my reasoning was wrong.
And then — I actually called a real professor through the app. A human professor. At 11pm."

Energy shifts here — from defeated to genuine surprise at the memory.
"Professor Curious" spoken clearly and deliberately.
"A human professor. At 11pm." — pause on this. It surprised even her.
"""
            },
            {
                "id": "clip_04_result",
                "desc": "THE RESULT + CTA — the payoff, direct ask to viewer",
                "prompt": """Raw smartphone camera footage, 9:16 vertical. Warm desk lamp light. College dorm room.

CONTINUITY: Same girl. Same desk, same sweatshirt. Same close frame, direct camera.

The result and the ask — she looks directly at camera:
"I got an 87 on the final. I want to say that again. 40 on the midterm. 87 on the final.
The only thing that changed was Professor Curious.
If you're in college and you're struggling — genuinely struggling — try it.
I put the link in my bio. That's it. Professor Curious."

Delivered slowly and clearly. Not a rehearsed pitch — this is real advice from a friend.
"Professor Curious" spoken three times. Each one clear. The last one is the final word.
She looks directly into camera for the final line. No smile — just sincere.
"""
            },
        ],
    },

    # ── FORMAT 2: ROOMMATE SKIT ──────────────────────────────────────────────
    {
        "id":          "fmt_02_skit",
        "run_id":      "fmt_02_skit",
        "label":       "Format 2 — Roommate Skit (Two-Person Drama)",
        "format_type": "skit",
        "hooks": [
            {"id": "h1", "lines": ["POV: your roommate reveals", "why she never seems stressed", "anymore 👀"]},
            {"id": "h2", "lines": ["2am. She's been on this problem", "for 3 hours. I know what to do."]},
            {"id": "h3", "lines": ["The app I've been hiding", "from my roommate 😭", "(she found out)"]},
            {"id": "h4", "lines": ["When Professor Curious ends", "the study session standoff"]},
        ],
        "char_lock": """CONTINUITY — TWO CONSISTENT CHARACTERS in all clips:
ROOMMATE A (struggling): Girl, 20-21. Brown hair, ponytail. Wearing a worn college hoodie and sweats.
Tired, frustrated, hair slightly disheveled. Surrounded by textbooks and notes.
ROOMMATE B (has the app): Girl, 20-21. Dark hair down. Wearing a different hoodie, calm energy.
She's the one who's figured it out. Confident but warm — not smug.
SETTING: Shared dorm room, 2am. Two desks side by side. Warm lamp light. Textbooks everywhere.
This is a real dorm room, not a set. Raw phone-camera look. Natural, unpolished.""",
        "clips": [
            {
                "id": "clip_01_hook",
                "desc": "HOOK — Roommate A is at breaking point, Roommate B walks in",
                "prompt": """Raw smartphone footage, 9:16 vertical. Dorm room, 2am. Two desks, lamp light. Textbooks everywhere.

ROOMMATE A (brown ponytail, college hoodie, exhausted): at her desk, head down.
"I have been on this ONE problem for three hours. THREE hours."
She slumps back in chair. Looks at ceiling. Genuinely defeated.

ROOMMATE B (dark hair, calm hoodie) appears at the door, glances in.
"...Still that one problem?"

A: "Don't."

HOOK is the raw exhaustion in A's body language in the first 2 seconds.
No performance — this is a real moment between roommates at 2am.
"""
            },
            {
                "id": "clip_02_intervention",
                "desc": "Roommate B intervenes — takes phone, shows the app",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same dorm room, 2am.

ROOMMATE B (dark hair, calm) walks over to A's desk.
"Okay. Show me the problem."

A: "I've watched three YouTube videos. I've tried ChatGPT—"

B, calm: "I know. I know. Here — use Professor Curious. Just scan it."
She picks up A's phone (or her own) and demonstrates.

"Scan the problem."

A watches, skeptical but too tired to argue.
B is matter-of-fact — this is just what she does. "Professor Curious" said naturally, not like a pitch.
"""
            },
            {
                "id": "clip_03_discovery",
                "desc": "The breakdown appears — A starts understanding",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same dorm room, 2am.

Both girls looking at the phone screen. B walks A through what Professor Curious shows.
B: "See — it breaks down each step. It knows you made the wrong assumption right here."
She points at the screen.

A leans in. Something shifts — she's actually reading it now.
A: "Wait. Wait. So that's why..."

A's face — the first moment of understanding. Eyes change. The fog lifts slightly.
B: "Yeah. And if you still don't get it after this, you can literally call a real professor."
A: "Through the app?"
B: "Through the app."

The reaction — not overplayed. Real surprise, real understanding beginning.
"Professor Curious" implied throughout but not shouted. B says it once more clearly at the end.
"""
            },
            {
                "id": "clip_04_payoff",
                "desc": "THE PAYOFF — A is using it, working, final line to camera",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same dorm room, 2am. Twenty minutes later.

ROOMMATE A: Now working steadily at her desk. Not stressed. Phone beside her textbook.
She's making progress. The defeated posture from clip_01 is gone.

ROOMMATE B glances over from her desk, sees A working. Small satisfied nod.

A pauses, looks over at B:
"You've had this app for HOW long and you're only telling me now?"

B looks directly at camera — slight smirk:
"Professor Curious. Link in bio. You're welcome."

The final look to camera is the punchline — B breaks the fourth wall just slightly.
Natural, warm, real. "Professor Curious" said clearly, directly at camera, as the last thing heard.
"""
            },
        ],
    },

    # ── FORMAT 3: LIBRARY WHISPER ────────────────────────────────────────────
    {
        "id":          "fmt_03_whisper",
        "run_id":      "fmt_03_whisper",
        "label":       "Format 3 — Library Whisper (ASMR / Secret)",
        "format_type": "whisper",
        "hooks": [
            {"id": "h1", "lines": ["Okay I'm only saying this once.", "So actually pay attention."]},
            {"id": "h2", "lines": ["The study app I genuinely", "don't want everyone to know."]},
            {"id": "h3", "lines": ["POV: overhearing the most useful", "thing in the college library 📚"]},
            {"id": "h4", "lines": ["I shouldn't be telling you this.", "But it's Professor Curious."]},
        ],
        "char_lock": """CONTINUITY — SAME PERSON IN ALL CLIPS:
College girl, 20-21. Light brown hair down. Wearing a cozy knit sweater.
Sitting at a library desk, books and laptop open in front of her. Soft library lighting.
She whispers directly to camera — the phone is propped up on the desk in front of her.
The WHISPER is key — she's sharing a secret she doesn't want to spread too widely.
Tone: conspiratorial, warm, a little self-aware about how she sounds.
The library is quiet. Every so often, other students are visible in soft focus behind her.""",
        "clips": [
            {
                "id": "clip_01_hook",
                "desc": "HOOK — she leans toward camera, looks left and right, starts whispering",
                "prompt": """Raw smartphone footage, 9:16 vertical. College library. Soft warm lighting.
Books on desk, laptop open. Other students visible in soft focus behind.

GIRL (light brown hair, knit sweater): looks left, looks right, then leans toward camera.
Whispers — close to the mic:
"Okay. I need to tell you something and I need you to actually remember it.
There's a study app called Professor Curious.
And I... I genuinely don't want everyone to know about it because then everyone starts using it
and I lose my advantage. But I feel bad keeping it to myself."

First 2 seconds: the look left-right before leaning in. The anticipation is the hook.
"Professor Curious" whispered clearly but carefully — like she's protecting the secret.
Camera is stationary — she leans INTO it.
"""
            },
            {
                "id": "clip_02_features",
                "desc": "Whispering the features — what makes it different",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library desk. Same soft lighting.

GIRL (same knit sweater, same desk): still whispering, but leaning in even more now.
"So here's what it does. You scan any problem — literally any — and it doesn't just give you the answer.
It gives you the ENTIRE reasoning. Every step. And it's not generic — it finds WHERE you specifically
went wrong and explains exactly that part."

She pauses. Glances behind her to make sure no one is listening.
"I haven't had to ask anyone for help since I started using Professor Curious.
No tutors. No TA hours. Just me and the app."

Whisper pace is deliberate — slower than normal speech. Every word is clear.
"Professor Curious" said with particular care, like the name itself is valuable.
"""
            },
            {
                "id": "clip_03_real_professors",
                "desc": "Whispering about the real professor feature — most valuable secret",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library desk.

GIRL (same): leans even closer. This is the real secret:
"And — and this is the part that actually got me —
you can call a real professor. Through the app. Any time.
Not a chatbot. Not an AI trying to sound like a professor.
An actual professor who knows the subject."

She sits back slightly. Processes it herself.
"I called one at midnight before my physics final. She walked me through the whole problem set.
For free. Through Professor Curious."

The "at midnight" moment should register on her face — she still can't believe it.
"Professor Curious" said twice. Still a whisper. Every syllable clear.
"""
            },
            {
                "id": "clip_04_payoff",
                "desc": "The 'caught' moment — someone looks, she mouths the name, done",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library desk.

GIRL: finishing the whisper:
"So if you're struggling with literally anything — scan it. Professor Curious.
I'm going to be the most academically impressive person in my friend group
and it's entirely because of this one app. Link in bio. Professor Curious."

THEN: a student nearby at another table glances over — they heard something.
She looks at the camera one more time — slight, amused smile. Points at the phone screen.
Mouths: "Professor Curious." Silent. Just her lips. Then goes back to her textbook like nothing happened.

The silent mouth "Professor Curious" at the end is the punchline and the CTA.
Low energy, conspiratorial warmth throughout.
"""
            },
        ],
    },

    # ── FORMAT 4: STUDY GROUP SAVIOR ─────────────────────────────────────────
    {
        "id":          "fmt_04_group",
        "run_id":      "fmt_04_group",
        "label":       "Format 4 — Study Group Savior (Group Social Proof)",
        "format_type": "group",
        "hooks": [
            {"id": "h1", "lines": ["POV: your study group is", "absolutely cooked right now 💀"]},
            {"id": "h2", "lines": ["Nobody panic.", "We have Professor Curious."]},
            {"id": "h3", "lines": ["The moment one person", "saves four GPAs 📱"]},
            {"id": "h4", "lines": ["When Professor Curious ends", "the 2-hour group confusion"]},
        ],
        "char_lock": """CONTINUITY — 4 CONSISTENT STUDENTS at the same table in all clips:
STUDENT A (the savior): Boy, 20-21. Dark hair, calm demeanor. Maroon hoodie. Has the app.
STUDENT B: Girl, 19-20. Blonde, distressed. Light blue t-shirt. Most frustrated of the group.
STUDENT C: Girl, 20-21. Natural hair. Yellow hoodie. Second most confused.
STUDENT D: Boy, 21-22. Glasses, red hoodie. Trying to stay calm, failing.
SETTING: College library table. Large round table, books and laptops everywhere.
Warm lamppost-style library lights. Early evening. Shot from a phone propped slightly above table.
The group is REAL — not actors reading lines. Everything feels like it just happened.""",
        "clips": [
            {
                "id": "clip_01_chaos",
                "desc": "HOOK — total group chaos, everyone confused, first 3s hooks on frustration",
                "prompt": """Raw smartphone footage, 9:16 vertical. College library round table. Evening.
Four students, textbooks and laptops, warm lamp light.

STUDENT B (blonde, frustrated): "I don't understand ANYTHING on this page. Like nothing."
STUDENT D (glasses): "I've watched the lecture three times. Still lost."
STUDENT C (yellow hoodie): closes her laptop. "Okay I think we're all going to fail this exam."

Everyone looking at each other. The despair is real. This is a 9pm study session that is not going well.

STUDENT A (dark hair, calm, maroon hoodie) has been quiet. He opens his phone.
"Everyone stop. Let me try something."

First 2 seconds: the group chaos immediately tells the viewer exactly what kind of moment this is.
STUDENT A's calm vs everyone else's panic is the tension. He says NOTHING yet except "everyone stop."
"""
            },
            {
                "id": "clip_02_scan",
                "desc": "A scans the problem with Professor Curious — group watches skeptically",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library table. Same warm light.

STUDENT A holds up phone toward the textbook page. Scans the problem.
STUDENT B: "What are you doing?"
A: "Just — watch."

He opens Professor Curious. Scans the specific problem they're stuck on.
The loading moment — everyone leaning in skeptically.
A, quiet: "Professor Curious. Give it a second."

The group watches the phone. Still skeptical. Still tense.
B: "If this is just another ChatGPT thing—"
A: "It's not. Wait."

The name "Professor Curious" said clearly once. A is confident but not smug.
The group's skepticism is visible — leaning in but not convinced yet.
"""
            },
            {
                "id": "clip_03_breakthrough",
                "desc": "The breakdown appears — everyone starts understanding",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library table.

A rotates the phone so the group can see. He walks through what Professor Curious shows:
"See — it found where we went wrong. Right here. Our assumption was off."
He points. B leans way in. D takes off glasses to look closer.

Silence for 2 seconds. Everyone reading.

B: "Oh."
D: "...Oh."
C, slowly: "Oh my god. That's — that's what I was missing."

The "Oh" chain — each person landing on the understanding separately.
No celebration yet — just the quiet of four people suddenly getting it.
A: "And if you still don't get it after the breakdown, you can call a real professor."
B: "Through the app?"
A: "Through the app."

The moment of understanding is on everyone's FACE — not exaggerated. Real.
"Professor Curious" said once more. Soft, matter-of-fact.
"""
            },
            {
                "id": "clip_04_payoff",
                "desc": "PAYOFF — group working calmly, final line to camera, multiple endorsements",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same library table. 20 minutes later.

Same table, same people — but now everyone is working. The chaos is gone. Focused energy.
Textbooks open. Pencils moving. Everyone writing.

STUDENT B glances up at the phone (camera):
"Professor Curious just saved our study group. I want that on record."
STUDENT D: "Minutes of the meeting: we all downloaded Professor Curious."
STUDENT C, not looking up from her notes, just raises hand in agreement.

STUDENT A: small smile, looks at camera:
"Professor Curious. Link in my bio."

Four students endorsing it — not scripted, not loud. Just matter-of-fact relief.
"Professor Curious" said three times. Each one from a different person. Clear.
The final look to camera from A is the closing beat.
"""
            },
        ],
    },

    # ── FORMAT 5: APP RANKING / COMPARISON ───────────────────────────────────
    {
        "id":          "fmt_05_ranking",
        "run_id":      "fmt_05_ranking",
        "label":       "Format 5 — App Ranking (Direct Comparison Review)",
        "format_type": "comparison",
        "hooks": [
            {"id": "h1", "lines": ["I tested every study app", "for 2 weeks. Here's the verdict."]},
            {"id": "h2", "lines": ["ChatGPT vs Gauth vs", "Professor Curious — who wins?"]},
            {"id": "h3", "lines": ["Ranking study apps as someone", "who actually tested them all 📊"]},
            {"id": "h4", "lines": ["The comparison that changed", "how our whole dorm studies."]},
        ],
        "char_lock": """CONTINUITY — SAME PERSON IN ALL CLIPS:
College girl, 20-21. Red hair or dark auburn, down. Wearing a simple grey crew-neck sweatshirt.
Sitting at a clean desk with a ring light or bright window light. Professional-ish but still dorm energy.
She has a small whiteboard or sticky notes behind her with app names listed.
She's done the work. She's the expert now. Speaks directly to camera, measured, clear.
NOT over-the-top influencer energy — she's just a student who got nerdy about this comparison.
Each app mentioned by name, face stays neutral until Professor Curious.""",
        "clips": [
            {
                "id": "clip_01_hook",
                "desc": "HOOK — the premise, what she did, why you should care",
                "prompt": """Raw smartphone footage, 9:16 vertical. Clean desk, bright light. Whiteboard behind.
App names written on sticky notes or whiteboard: ChatGPT, Gauth, Photomath, Professor Curious.

GIRL (auburn hair, grey sweatshirt): direct to camera, measured:
"I spent two weeks using every major study app on the same problem sets.
Orgo, Calculus, Physics. Same problems. Every app. Same conditions.
I'm going to tell you exactly what each one actually does for your grade.
Starting with the ones that don't work."

First 3 seconds: the whiteboard with app names is visible — curiosity gap.
She's about to rank something. The viewer already has a reason to stay.
Neutral tone — she's going to be fair. "Professor Curious" visible on the list but not highlighted yet.
"""
            },
            {
                "id": "clip_02_losers",
                "desc": "ChatGPT and Gauth — the verdict (not great)",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same clean desk, same whiteboard.

GIRL: still measured, slightly disappointed:
"ChatGPT — I use it, I respect it. But for actual studying it gives you answers, not understanding.
I walked into two exams confident because ChatGPT said I understood it. I did not understand it.
Gauth — faster, better at math. But the steps skip things. I got caught on my exam
because Gauth skipped the exact step I needed to understand. Multiple times."

She crosses off or puts a mark next to those names on the list.
Not mean about these apps — just honest. She tried. They fell short for her purpose.
"ChatGPT" and "Gauth" said clearly and fairly. No exaggerated negativity.
"""
            },
            {
                "id": "clip_03_winner",
                "desc": "PROFESSOR CURIOUS — the clear winner, features explained as proof",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same clean desk. Same whiteboard.
But now she's circling "Professor Curious" on the list. Or putting a star next to it.

GIRL: energy shifts — this is the good part:
"Professor Curious is completely different. And I want to explain why with specifics.
It scans your exact problem — not a topic, the actual problem.
It breaks down every step AND identifies exactly where your reasoning went wrong.
Every time. On every subject I tried.
And then — I called a real professor through the app at 10pm before my Orgo exam.
She was available. She was excellent. That's not a feature that exists anywhere else."

Energy is still measured but there's genuine enthusiasm now. She found what she was looking for.
"Professor Curious" said three times. Clear, deliberate. She circles it on the board.
"""
            },
            {
                "id": "clip_04_verdict",
                "desc": "THE VERDICT — grade proof, final recommendation, CTA",
                "prompt": """Raw smartphone footage, 9:16 vertical. Same clean desk.
She holds up something — a phone screenshot, or just says the numbers.

GIRL: final verdict, direct to camera:
"Here's my result. Two weeks using Professor Curious alongside my classes.
My Orgo grade went from a 71 average to an 88 average. My Calc went up 12 points.
I know that's not all the app — I also studied harder. But the understanding improvement was Professor Curious.
There's no other app that explains the reasoning the way Professor Curious does.
It's the only one worth paying for. Professor Curious. Link in bio."

Delivers the numbers slowly — lets them land. Not fast-talking.
"Professor Curious" said four times. Each time clear. The last line looks directly at camera.
She holds up the list one more time — Professor Curious clearly marked as the winner.
"""
            },
        ],
    },

]


# ─────────────────────────────────────────────────────────────────────────────
# AZURE SORA HELPERS
# ─────────────────────────────────────────────────────────────────────────────

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
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS, timeout=30)
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
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS, timeout=120)
    if not dl.ok:
        raise RuntimeError(f"Download failed: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"    [save] {out_path.name} ({len(dl.content)//1024} KB)", flush=True)


def generate_clip(full_prompt: str, clip_id: str, out_path: Path) -> None:
    print(f"    [submit] {clip_id} ...", flush=True)
    video_id = submit_job(full_prompt, clip_id)
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


# ─────────────────────────────────────────────────────────────────────────────
# HOOK OVERLAY (Pillow — same approach as add_hooks.py, custom hooks per ad)
# ─────────────────────────────────────────────────────────────────────────────

def draw_text_with_outline(draw, text, pos, font, fill, outline, outline_width=3):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def build_overlay_png(hook_lines: list, tmp_path: Path) -> None:
    overlay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    # ── Logo layout (centered, Gauth VS PC) ──────────────────────────────────
    logo_size = 100
    gap       = 70
    total_w   = logo_size * 2 + gap
    start_x   = (VW - total_w) // 2
    gauth_x   = start_x
    pc_x      = start_x + logo_size + gap
    logo_y    = 540
    label_y   = logo_y + logo_size + 6

    gauth_img = Image.open(GAUTH_LOGO).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    overlay.paste(gauth_img, (gauth_x, logo_y), gauth_img)

    pc_img = Image.open(PC_LOGO).convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    overlay.paste(pc_img, (pc_x, logo_y), pc_img)

    try:
        vs_font    = ImageFont.truetype(IMPACT_FONT, 34)
        label_font = ImageFont.truetype(ARIAL_BOLD, 20)
    except Exception:
        vs_font    = ImageFont.load_default()
        label_font = ImageFont.load_default()

    vs_text = "VS"
    vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
    vs_w    = vs_bbox[2] - vs_bbox[0]
    vs_x    = start_x + logo_size + (gap // 2) - (vs_w // 2)
    vs_y    = logo_y + (logo_size // 2) - 17
    draw_text_with_outline(draw, vs_text, (vs_x, vs_y), vs_font, (255, 255, 255, 255), (0, 0, 0, 200), 3)

    g_lbl   = "GAUTH"
    g_bbox  = draw.textbbox((0, 0), g_lbl, font=label_font)
    g_lbl_w = g_bbox[2] - g_bbox[0]
    g_lbl_x = gauth_x + (logo_size // 2) - (g_lbl_w // 2)
    draw_text_with_outline(draw, g_lbl, (g_lbl_x, label_y), label_font, (255, 255, 255, 255), (0, 0, 0, 200), 2)

    pc_lbl   = "PROF. CURIOUS"
    pc_bbox  = draw.textbbox((0, 0), pc_lbl, font=label_font)
    pc_lbl_w = pc_bbox[2] - pc_bbox[0]
    pc_lbl_x = pc_x + (logo_size // 2) - (pc_lbl_w // 2)
    draw_text_with_outline(draw, pc_lbl, (pc_lbl_x, label_y), label_font, (255, 255, 255, 255), (0, 0, 0, 200), 2)

    # ── Hook text (top) ───────────────────────────────────────────────────────
    hook_y_starts  = [40, 105, 165]
    hook_fontsizes = [48, 40, 34]

    for i, line in enumerate(hook_lines[:3]):
        try:
            hfont = ImageFont.truetype(IMPACT_FONT, hook_fontsizes[i])
        except Exception:
            hfont = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), line, font=hfont)
        tw   = bbox[2] - bbox[0]
        tx   = (VW - tw) // 2
        ty   = hook_y_starts[i]

        pad = 10
        draw.rounded_rectangle(
            [tx - pad, ty - pad//2, tx + tw + pad, ty + (bbox[3] - bbox[1]) + pad//2],
            radius=8, fill=(0, 0, 0, 110),
        )
        draw_text_with_outline(draw, line, (tx, ty), hfont, (255, 255, 255, 255), (0, 0, 0, 220), 4)

    overlay.save(str(tmp_path), "PNG")


def apply_hook(input_path: Path, hook: dict, out_dir: Path) -> Path:
    out_path = out_dir / f"{input_path.stem}_{hook['id']}.mp4"

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_png = Path(tf.name)

    print(f"  [{hook['id']}] Building overlay ...", flush=True)
    build_overlay_png(hook["lines"], tmp_png)

    print(f"  [{hook['id']}] Compositing ...", flush=True)
    filt = "[1:v]scale=720:1280[ovr];[0:v][ovr]overlay=0:0[out]"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(tmp_png),
        "-filter_complex", filt,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    tmp_png.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-600:]}")
    print(f"  [{hook['id']}] → {out_path.name} ({out_path.stat().st_size // 1024} KB)", flush=True)
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# SLACK
# ─────────────────────────────────────────────────────────────────────────────

def send_to_slack(video_path: Path, text: str) -> None:
    print(f"  [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    requests.post(SLACK_URL, data={"channel_id": SLACK_CHANNEL, "text": text})
    print(f"  [slack] {'✓ Sent' if resp.ok else '✗ ' + resp.text[:80]}", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# RUN ONE AD
# ─────────────────────────────────────────────────────────────────────────────

def run_ad(ad: dict) -> None:
    run_id    = ad["run_id"]
    clips_cfg = ad["clips"]
    hooks_cfg = ad["hooks"]
    char_lock = ad["char_lock"]

    out_dir   = OUTPUT_ROOT / run_id
    clips_dir = out_dir / "clips"
    hooks_dir = out_dir / "hooks"
    clips_dir.mkdir(parents=True, exist_ok=True)
    hooks_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {ad['label']}", flush=True)
    print(f"  Run ID : {run_id}  |  Clips: {len(clips_cfg)}  |  Hooks: {len(hooks_cfg)}", flush=True)
    print(f"{'='*60}", flush=True)

    # ── Generate clips ────────────────────────────────────────────────────────
    clip_paths = []
    for i, clip in enumerate(clips_cfg):
        clip_num = i + 1
        print(f"\n  [{clip_num}/{len(clips_cfg)}] {clip['desc'][:60]}", flush=True)
        out = clips_dir / f"{clip['id']}.mp4"
        full_prompt = f"{char_lock}\n\n{clip['prompt']}"
        generate_clip(full_prompt, clip["id"], out)
        clip_paths.append(out)

    # ── Stitch ────────────────────────────────────────────────────────────────
    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {len(clip_paths)} clips ...", flush=True)
    stitch_clips(clip_paths, merged)

    # ── Send raw merged to Slack first ────────────────────────────────────────
    send_to_slack(
        merged,
        f"🎬 *{ad['label']}* — RAW (no hooks)\n_Format test — {ad['format_type']} style_"
    )

    # ── Apply 4 hook variations ───────────────────────────────────────────────
    print(f"\n  [hooks] Applying {len(hooks_cfg)} hook variations ...", flush=True)
    for hook in hooks_cfg:
        try:
            hook_out = apply_hook(merged, hook, hooks_dir)
            hook_text = " / ".join(hook["lines"])
            send_to_slack(
                hook_out,
                f"🪝 *{ad['label']}*\nHook: _{hook_text}_"
            )
        except Exception as e:
            print(f"  ✗ Hook {hook['id']} failed: {e}", flush=True)

    print(f"\n  ✓ DONE: {run_id} — {len(hooks_cfg)} hook variations sent to Slack\n", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
    if not GAUTH_LOGO.exists() or not PC_LOGO.exists():
        sys.exit(f"ERROR: Logos missing in {ASSETS_DIR}.")

    print(f"\n{'#'*60}")
    print(f"  US Format Test — 5 Ad Formats for Professor Curious")
    print(f"  Formats: Talking Head | Skit | Whisper | Group | Ranking")
    print(f"  Each: 4 clips × 8s + 4 hook variations → Slack")
    print(f"{'#'*60}\n")

    for i, ad in enumerate(ADS, 1):
        print(f"\n[Ad {i}/5] {ad['label']}", flush=True)
        try:
            run_ad(ad)
        except Exception as e:
            print(f"  ✗ FAILED [{ad['id']}]: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  All 5 formats done. Check Slack for raw + hook variations.")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
