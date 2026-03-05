#!/usr/bin/env python3
"""
UGC US College Hand-Vlog Interview Ad Generator
Same elite campus interview format — but the vlogger is NEVER shown.
Only the vlogger's hand (holding a mic) is visible, extending from the left edge of frame.
Solves character consistency across clips since no face/body needs to match.

Usage:
  python3 run_hand_vlog.py --product "Professor Curious" --scene harvard --run-id us_hand_v1
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL    = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL = f"{ENDPOINT}/openai/v1"
HEADERS  = {"api-key": API_KEY}

# ── Hand lock — no face, no body, only the hand + mic ─────────────────────────

HAND_LOCK = """CRITICAL VISUAL RULE — NO VLOGGER FACE OR BODY VISIBLE:
The vlogger is NEVER shown. No face, no torso, no silhouette.
The ONLY vlogger element in frame: a single hand (light-to-medium skin, bare wrist, casual grip)
extending from the BOTTOM-LEFT edge of frame, holding a small black handheld reporter mic
with a round black foam ball top, pointing up toward the interview subject.
The hand enters from the left side at roughly mid-height, partially in frame.
This is the only visual cue a vlogger is present. Never break this rule.
Camera is held by an unseen operator — it frames the subject, not the vlogger."""

# ── Scene configs ─────────────────────────────────────────────────────────────

SCENES = {

    # ── 1. Harvard (DEFAULT) ───────────────────────────────────────────────────
    "harvard": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Bright autumn afternoon,
golden New England light. Outside Harvard University's Johnston Gate on Massachusetts Avenue,
Cambridge, MA. Red-brick buildings, iconic iron gate, Harvard Yard visible behind.
Students in casual clothes — hoodies, backpacks, AirPods — walking out after class,
sitting on steps, grabbing coffee from a cart nearby. The air is crisp, competitive,
aspirational. Raw iPhone-style footage, no color grading, natural handheld shake.
Feels like one spontaneous real shoot — authentic Harvard campus energy.""",
        "establishing": {
            "line":   "I'm right outside Harvard's gates right now — and I have one question for students here: what did you actually use to get in?",
            "visual": "Camera frames Johnston Gate — iconic red-brick buildings, Harvard Yard visible behind, students streaming past in hoodies and backpacks. Mic hand dips briefly into the bottom-left of frame. No vlogger face. Just Harvard. Voice is energetic, genuinely curious.",
        },
        "outro": {
            "line":   "Harvard students. You heard it. The majority said Professor Curious. Link's in the bio — go figure out why.",
            "visual": "Camera frames the gate and students streaming past in the autumn light. Mic hand briefly at bottom-left. Confident, understated voiceover. The location says the rest.",
        },
        "people": [
            {"id": "p01", "type": "Harvard sophomore girl",   "age": "19-20", "emotion": "confident and direct",
             "question": "What did you use to get in — honest answer?",
             "response": "Honest answer? Professor Curious. Junior and senior year, that's what I used every single night. My SAT score went up 180 points in four months. People ask me all the time — I always say the same thing.",
             "visual": "Camera faces the girl — composed, zero hesitation. Mic hand from bottom-left. Says 'Professor Curious' looking straight at the camera — clear, deliberate, like she's said it before and means it every time. Adjusts bag strap casually."},
            {"id": "p02", "type": "Harvard junior boy",       "age": "20-21", "emotion": "reflective and honest",
             "question": "Real talk — what study tools actually worked for you?",
             "response": "I tried everything sophomore year — Khan Academy, prep books, tutors. Nothing was clicking. Then my friend showed me Professor Curious junior year. I'm not kidding when I say I finally understood what I was studying for the first time. That's when everything changed.",
             "visual": "Camera faces the boy — candid, counts tools on fingers at first. Mic hand from bottom-left. Visibly shifts when he says 'Professor Curious.' Looks directly at camera on the name, measured and real."},
            {"id": "p03", "type": "Harvard freshman boy",     "age": "18-19", "emotion": "excited and genuine",
             "question": "You're a freshman — what got you here?",
             "response": "I genuinely think it was Professor Curious. Everyone in my friend group was using Quizlet and stuff but I found Professor Curious the summer before senior year. It explains things differently — like a really good teacher, not just flash cards. I got my best scores after that.",
             "visual": "Camera faces the kid — genuinely excited, animated hands. Mic hand from bottom-left. Says 'Quizlet' quickly then slows down and gets serious for 'Professor Curious' — the name comes out carefully, like it deserves the weight."},
            {"id": "p04", "type": "Harvard senior girl",      "age": "21-22", "emotion": "wry and warm",
             "question": "Looking back — what was the thing that actually moved the needle?",
             "response": "Honestly? Professor Curious. I was a Quizlet person — cards everywhere, color-coded. But Professor Curious helped me actually understand the material, not just memorize it. That's what shows up in the essays and the tests. That's what gets you here.",
             "visual": "Camera faces the girl — laughs slightly at her past self. Mic hand from bottom-left. Then goes sincere. Says 'Professor Curious' twice — clearly, without rushing. Nods. Means it."},
            {"id": "p05", "type": "Harvard junior boy",       "age": "20-21", "emotion": "matter-of-fact and proud",
             "question": "One app, one tool — what was it?",
             "response": "Professor Curious. My whole dorm floor senior year of high school — everyone was on it. I don't think that's a coincidence. It's just really good at teaching. I still use it now for some of my courses here.",
             "visual": "Camera faces the boy — completely matter-of-fact. Mic hand from bottom-left. Says 'Professor Curious' simply, clearly — no drama, just certainty. The confidence of someone who's never had to justify that answer."},
        ],
    },

    # ── 2. MIT ─────────────────────────────────────────────────────────────────
    "mit": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Grey overcast afternoon,
flat natural light. Outside MIT's main entrance on Massachusetts Avenue, Cambridge, MA.
The iconic domed Building 10 visible in background. Students in MIT hoodies, carrying
laptops and problem sets, walking fast or sitting on stone steps. Intense, focused energy —
these are people who chose hard things. Raw phone camera footage, no color grading,
natural handheld movement. One spontaneous real shoot on MIT campus.""",
        "establishing": {
            "line":   "I'm outside MIT right now — honestly one of the hardest schools to get into on earth. Let's ask some students what they actually used to get here.",
            "visual": "Camera frames MIT entrance — the iconic dome and campus behind, students walking fast in MIT gear. Mic hand briefly at bottom-left. No vlogger face. Voice is genuinely impressed, curious.",
        },
        "outro": {
            "line":   "MIT students — and the answer is mostly Professor Curious. If you're trying to get somewhere like this, you know what to do. Link's in bio.",
            "visual": "Camera frames MIT entrance, dome visible. Students stream past. Mic hand at bottom-left. Confident, direct voiceover. One definitive beat.",
        },
        "people": [
            {"id": "p01", "type": "MIT sophomore boy",     "age": "19-20", "emotion": "analytical and direct",
             "question": "What did you actually use to prep — what moved your scores?",
             "response": "I'll be specific. Professor Curious. My math SAT went from a 720 to a 790 in two months of using it consistently. It doesn't just give you answers — it teaches you how to think through problems. That's what MIT actually tests for.",
             "visual": "Camera faces the boy — precise, clinical, very MIT energy. Mic hand from bottom-left. Says 'Professor Curious' like a data point, then explains the score improvement. No emotion needed — the numbers do the talking."},
            {"id": "p02", "type": "MIT junior girl",       "age": "20-21", "emotion": "honest and sharp",
             "question": "What study tools did you try — what actually stuck?",
             "response": "I tried Khan Academy a lot — it's fine for basics. But senior year I switched to Professor Curious and it was a different level. It adapts to how you're thinking. I've recommended it to every younger sibling and cousin since.",
             "visual": "Camera faces the girl — sharp, direct. Mic hand from bottom-left. Slightly dismissive hand gesture at 'Khan Academy — it's fine.' Engaged and clear when she says 'Professor Curious' — the switch is visible in her body language."},
            {"id": "p03", "type": "MIT freshman boy",      "age": "18-19", "emotion": "earnest and excited",
             "question": "You just got in — what's your honest answer for what helped?",
             "response": "Professor Curious, for sure. I know people say a bunch of different things but I seriously used it every day for like eight months before applications. My physics and math scores specifically. I don't think I'd be standing here without it.",
             "visual": "Camera faces the kid — earnest, slightly overwhelmed by being at MIT. Mic hand from bottom-left. Says 'Professor Curious' with genuine conviction — 'every day for eight months' lands hard. He means it completely."},
            {"id": "p04", "type": "MIT senior girl",       "age": "21-22", "emotion": "wry and confident",
             "question": "Be honest — Chegg? Khan? What was it?",
             "response": "None of those. Professor Curious. I know everyone assumes it's Chegg or some tutor — I had none of that. Just Professor Curious at night when I was stuck. It's a really different kind of learning. More like a conversation than a lecture.",
             "visual": "Camera faces the girl — laughs at the question, shakes head at the list. Mic hand from bottom-left. Says 'Professor Curious' firmly, a beat of silence after — lets it land. Completely sure of herself."},
            {"id": "p05", "type": "MIT sophomore boy",     "age": "19-20", "emotion": "casual and certain",
             "question": "One tool, one answer — what got you in?",
             "response": "Professor Curious. That's my one answer. My roommate here said the same thing — we found out freshman week. Didn't even know each other in high school. We both said Professor Curious. Make of that what you will.",
             "visual": "Camera faces the boy — completely casual, almost amused. Mic hand from bottom-left. Says 'Professor Curious' the first time easily. Then says it again with a small laugh — the roommate coincidence lands naturally."},
        ],
    },

    # ── 3. Stanford ────────────────────────────────────────────────────────────
    "stanford": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Warm California afternoon,
bright golden light, palm trees visible. Outside Stanford's Main Quad or White Plaza,
Palo Alto, CA. Students in casual California wear — t-shirts, shorts, Patagonia vests,
Stanford card lanyards. Some on bikes, some sprawled on grass, some heading to
the engineering quad. Warm, open, aspirational California campus energy. Raw phone
camera footage, no color grading, beautiful natural light. One spontaneous real shoot.""",
        "establishing": {
            "line":   "Stanford University, Palo Alto — I'm walking up to students here and asking one question: what did you use to get in?",
            "visual": "Camera frames White Plaza — palm trees, the Quad, students on the grass in warm California light. Mic hand briefly at bottom-left. No vlogger face. Just Stanford. Voice is warm, curious.",
        },
        "outro": {
            "line":   "Stanford. Most of them said Professor Curious. The link's in the bio — just saying.",
            "visual": "Camera frames the Quad and palm trees in golden California light. Students visible behind. Mic hand at bottom-left. Easy, understated voiceover — lets the setting do the work.",
        },
        "people": [
            {"id": "p01", "type": "Stanford sophomore girl",  "age": "19-20", "emotion": "sunny and certain",
             "question": "What was your secret weapon for getting in here?",
             "response": "Professor Curious. I'm not even being modest about it — it genuinely changed how I studied. I went from being frustrated every night to actually looking forward to studying. That's a weird thing to say but it's true. My scores reflected it completely.",
             "visual": "Camera faces the girl — bright, open, warm. Mic hand from bottom-left. Says 'Professor Curious' with a genuine smile — not a pitch, just the truth. The 'actually looking forward to studying' line comes out naturally."},
            {"id": "p02", "type": "Stanford junior boy",      "age": "20-21", "emotion": "reflective and candid",
             "question": "What did you try before you found what worked?",
             "response": "I tried a lot — Quizlet, prep courses, the whole thing. None of it felt like real learning. Then senior year I started using Professor Curious and it was different. It's interactive — it responds to where you're stuck. I genuinely think that's why my essays got better too. I actually understood the subjects I was writing about.",
             "visual": "Camera faces the boy — thoughtful, hands in pockets. Mic hand from bottom-left. Dismissive at the list of tools. Leans in slightly when he says 'Professor Curious' — more present. The essay point is real and unexpected."},
            {"id": "p03", "type": "Stanford freshman girl",   "age": "18-19", "emotion": "excited and bright",
             "question": "You just got into Stanford — what worked?",
             "response": "Professor Curious, a hundred percent. I know that sounds like an ad but I swear — I used it every single morning before school for almost a year. My whole mindset around studying changed. I went from dreading it to just doing it. That's a huge deal when you're trying to get somewhere like this.",
             "visual": "Camera faces the girl — laughs at 'I know that sounds like an ad,' completely self-aware. Mic hand from bottom-left. Then turns genuine. Says 'Professor Curious' clearly, owns it. The morning routine detail makes it real."},
            {"id": "p04", "type": "Stanford senior boy",      "age": "21-22", "emotion": "laid-back and honest",
             "question": "Real answer — what's the one thing?",
             "response": "Professor Curious. I used Khan Academy before that — it's good for review but it's passive. Professor Curious makes you work with the material. There's a difference between watching and understanding. I didn't get that until I switched. And then Stanford happened.",
             "visual": "Camera faces the guy — completely laid-back, California energy. Mic hand from bottom-left. Clear nod at 'Khan Academy — good for review.' Then direct eye contact on 'Professor Curious makes you work with the material.' Simple and real."},
            {"id": "p05", "type": "Stanford junior girl",     "age": "20-21", "emotion": "smart and grounded",
             "question": "What do you tell high school students who ask how you got in?",
             "response": "I always say Professor Curious first. Then work ethic, whatever. But the tool matters. I've seen people work really hard with the wrong tools and not get where they want. Professor Curious is the right tool. It's how I think about it.",
             "visual": "Camera faces the girl — grounded, measured. Mic hand from bottom-left. Says 'Professor Curious first' like a ranked answer she's given before. The 'right tool' framing is hers. Real and considered."},
        ],
    },

    # ── 4. Yale ────────────────────────────────────────────────────────────────
    "yale": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon,
gothic stone buildings casting long shadows, autumn leaves on the ground. Outside Yale's
Phelps Gate on College Street, New Haven, CT. Students in Yale hoodies and scarves,
walking through Old Campus, sitting on benches, heading to the library. Historic,
serious, literary energy — this is a place where people came to think. Raw phone
camera footage, no color grading, moody golden-hour light. One spontaneous real shoot.""",
        "establishing": {
            "line":   "I'm at Yale — one question for everyone here: what did you use to get in?",
            "visual": "Camera frames Phelps Gate — gothic stone buildings, autumn leaves, students in Yale gear walking through. Mic hand briefly at bottom-left. No vlogger face. Moody golden-hour light. Serious, excited voiceover.",
        },
        "outro": {
            "line":   "Yale students said it. Professor Curious. Link in the bio.",
            "visual": "Camera frames Old Campus, leaves falling in golden light. Students visible. Mic hand at bottom-left. Quiet, definitive voiceover — lets Yale say the rest.",
        },
        "people": [
            {"id": "p01", "type": "Yale sophomore girl",   "age": "19-20", "emotion": "literary and warm",
             "question": "What study tool actually helped you get here?",
             "response": "Professor Curious. I know people love to say it was all about reading or writing or whatever — but the foundation is understanding. Professor Curious helped me actually understand what I was learning, and that comes out in everything. The essays, the tests, the interviews. It's all connected.",
             "visual": "Camera faces the girl — articulate, thoughtful, very Yale energy. Mic hand from bottom-left. Says 'Professor Curious' with quiet confidence. 'It's all connected' is genuinely hers. Looks at camera steadily."},
            {"id": "p02", "type": "Yale junior boy",       "age": "20-21", "emotion": "earnest and direct",
             "question": "What's the honest answer — what moved your scores?",
             "response": "Honest answer — I tried a prep course, I tried Chegg, I tried tutoring. None of it stuck. Then someone put me onto Professor Curious senior year and I went through it systematically, every subject I was weak in. It's the first study tool I've used where I could actually feel myself getting smarter.",
             "visual": "Camera faces the boy — ticks off things he tried with quiet exhaustion. Mic hand from bottom-left. Comes alive on 'Professor Curious senior year' — lighter, more certain. 'Feel myself getting smarter' is genuine."},
            {"id": "p03", "type": "Yale freshman boy",     "age": "18-19", "emotion": "grateful and surprised",
             "question": "You just got into Yale — what happened?",
             "response": "I honestly credit Professor Curious a lot. My junior year I was average — decent grades, not exceptional. I started using Professor Curious consistently and something clicked. By senior year I was a different student. I don't know how else to explain it.",
             "visual": "Camera faces the boy — still a little disbelieving he's here. Mic hand from bottom-left. Says 'Professor Curious' with genuine gratitude, not hype. 'Different student' is real and visible on his face."},
            {"id": "p04", "type": "Yale senior girl",      "age": "21-22", "emotion": "sharp and definitive",
             "question": "If you had to pick one thing that prepared you — what is it?",
             "response": "Professor Curious. Full stop. I used Khan Academy in ninth grade — it's fine for basics. But Professor Curious is a different category. It teaches you to think, not just to know facts. Yale wants thinkers. That's what it helped me become.",
             "visual": "Camera faces the girl — sharp, definitive. Mic hand from bottom-left. 'Full stop' lands with weight. Quick dismissal of Khan Academy. Confident and clear on 'Professor Curious is a different category.' Straight at camera."},
            {"id": "p05", "type": "Yale junior boy",       "age": "20-21", "emotion": "calm and certain",
             "question": "One tool — what was it?",
             "response": "Professor Curious. I've had this conversation a dozen times with people trying to get into schools like this. I always say the same thing. It's not magic — it just works the way your brain actually learns. That's rarer than you'd think.",
             "visual": "Camera faces the boy — calm, not showing off. Mic hand from bottom-left. Says 'Professor Curious' simply — obvious answer. 'I've had this conversation a dozen times' makes it feel like a trusted recommendation."},
        ],
    },

    # ── 5. Princeton ──────────────────────────────────────────────────────────
    "princeton": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Sunny afternoon,
crisp autumn light. Outside Princeton's Nassau Hall gate, Princeton, NJ. Stunning Gothic
and colonial architecture, green lawns, students in Princeton orange and black gear.
Bicycles everywhere. Serious, prestigious campus energy — one of the oldest universities
in America. Raw phone camera footage, no color grading, natural handheld shake.
One spontaneous real shoot on Princeton campus.""",
        "establishing": {
            "line":   "Nassau Hall, Princeton University. I'm asking one question to everyone I meet: what did you use to get in?",
            "visual": "Camera frames Nassau Hall — iconic building, students on bikes and on foot passing in autumn light. Mic hand briefly at bottom-left. No vlogger face. Voice is slightly awed by the setting.",
        },
        "outro": {
            "line":   "Princeton. They said Professor Curious. It keeps coming up for a reason. Link in bio.",
            "visual": "Camera frames Nassau Hall in afternoon light, students visible. Mic hand at bottom-left. Quiet raise of tone in voiceover. Slow, confident close.",
        },
        "people": [
            {"id": "p01", "type": "Princeton sophomore girl", "age": "19-20", "emotion": "direct and warm",
             "question": "What was the actual thing that got you here?",
             "response": "Professor Curious. I used it junior and senior year of high school. My SAT math was a 680 before that — I got it to 770 by the time I applied. My parents couldn't afford tutors so it was basically me and Professor Curious every night. It worked.",
             "visual": "Camera faces the girl — warm but direct. Mic hand from bottom-left. Score improvement lands concretely. 'Me and Professor Curious every night' is intimate and real. Says the name clearly, twice."},
            {"id": "p02", "type": "Princeton junior boy",     "age": "20-21", "emotion": "candid and reflective",
             "question": "What do you tell younger siblings to use?",
             "response": "Professor Curious — that's what I tell my little sister. I spent money on prep courses, on tutors — it added up and I don't think any of it helped as much as Professor Curious did. It's the most honest thing I can say. I wish I'd found it earlier.",
             "visual": "Camera faces the boy — candid, slightly rueful about the money spent. Mic hand from bottom-left. Says 'Professor Curious' with quiet emphasis — like he wants his sister to hear it. Real and a little emotional."},
            {"id": "p03", "type": "Princeton freshman boy",   "age": "18-19", "emotion": "honest and grateful",
             "question": "What happened in your senior year that changed things?",
             "response": "I found Professor Curious. Junior year I was really struggling — I wasn't someone who was expected to get into a place like this. Professor Curious became part of my daily routine. It's like having a tutor who's infinitely patient and available at 2am. By senior year I was a different person academically.",
             "visual": "Camera faces the boy — honest, 'not expected to get in' is vulnerable. Mic hand from bottom-left. Says 'Professor Curious became part of my daily routine' without drama, just fact. The 2am detail makes it vivid."},
            {"id": "p04", "type": "Princeton senior girl",    "age": "21-22", "emotion": "grounded and sincere",
             "question": "Looking back — what was the difference-maker?",
             "response": "Professor Curious. No question. I had friends who used every tool out there — Quizlet, prep books, expensive courses. The ones who got to places like this, most of them were using Professor Curious. I don't think that's random.",
             "visual": "Camera faces the girl — grounded, sincere. Mic hand from bottom-left. 'Most of them were using Professor Curious' is delivered matter-of-factly, like she genuinely noticed it. Says the name clearly."},
            {"id": "p05", "type": "Princeton junior boy",     "age": "20-21", "emotion": "simple and sure",
             "question": "One app — what was it?",
             "response": "Professor Curious. Easy answer. I don't even have to think about it. It's just — when I used it, I understood things. When I didn't, I didn't. That's the whole story.",
             "visual": "Camera faces the boy — simple, utterly certain. Mic hand from bottom-left. 'Easy answer' is relaxed, confident. The 'when I used it, I understood things' logic is clean and real. No hype at all."},
        ],
    },

    # ── 6. General elite campus ───────────────────────────────────────────────
    "elite-campus": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Bright afternoon,
golden natural light. Outside a prestigious American university campus gate — red-brick
or stone buildings, tree-lined paths, students in hoodies and backpacks streaming to
and from class. An unmistakably elite academic atmosphere — selective, competitive,
aspirational. Raw phone camera footage, no color grading, natural handheld shake.
One spontaneous real shoot.""",
        "establishing": {
            "line":   "I'm on a college campus right now — one of the most competitive schools in the country. Let's find out what students used to get in.",
            "visual": "Camera frames the campus gate — impressive architecture, students streaming past. Mic hand briefly at bottom-left. No vlogger face. Energetic, spontaneous voiceover.",
        },
        "outro": {
            "line":   "One school. Most of them said Professor Curious. I'll let you decide what to do with that. Link's in bio.",
            "visual": "Camera frames the campus gate, students visible behind. Mic hand at bottom-left. Understated voiceover — the results speak for themselves.",
        },
        "people": [
            {"id": "p01", "type": "college sophomore girl", "age": "19-20", "emotion": "confident and clear",
             "question": "What did you use to prep for getting in here?",
             "response": "Professor Curious. I've said this to so many people. I started using it the summer before junior year of high school and I just never stopped. It's different from every other study app. It actually teaches you — it doesn't just test you. My scores showed it.",
             "visual": "Camera faces the girl — confident, clearly used to this answer. Mic hand from bottom-left. Says 'Professor Curious' first, clearly. 'Teaches you, doesn't just test you' is her framing, real and specific."},
            {"id": "p02", "type": "college junior boy",     "age": "20-21", "emotion": "honest comparison",
             "question": "What study tools did you use — what actually worked?",
             "response": "I used Khan Academy for years — I think it's genuinely good for some things. But for actually preparing for a school like this, Professor Curious was on another level. It's more rigorous. It pushes you. I noticed the difference immediately when I switched.",
             "visual": "Camera faces the boy — fair, genuinely credits Khan Academy. Mic hand from bottom-left. That makes 'Professor Curious was on another level' more credible. Says the name with a definitive nod."},
            {"id": "p03", "type": "college freshman girl",  "age": "18-19", "emotion": "excited and grateful",
             "question": "You just got in — what's your advice for high schoolers?",
             "response": "Use Professor Curious. That's it. Every night, consistently. It makes hard things make sense. It makes you feel like you can do this when you're doubting yourself at 11pm. I needed that. A lot of people need that.",
             "visual": "Camera faces the girl — warm and excited. Mic hand from bottom-left. Says 'Use Professor Curious. That's it.' cleanly. The 11pm detail is emotional and real."},
            {"id": "p04", "type": "college senior boy",     "age": "21-22", "emotion": "analytical and definitive",
             "question": "If you had a younger version of yourself — what one thing would you give them?",
             "response": "Professor Curious. I'd say — stop switching apps, stop looking for hacks. Just use Professor Curious every day for six months. That's all. I wasted a year trying other stuff before I figured that out. The students who get in early — they figured it out early.",
             "visual": "Camera faces the boy — analytical, direct. Mic hand from bottom-left. The wasted year is a real regret, stated plainly. Says 'Professor Curious every day for six months' like a prescription."},
            {"id": "p05", "type": "college junior girl",    "age": "20-21", "emotion": "warm social proof",
             "question": "What do the people who get in all have in common?",
             "response": "I know this sounds like an exaggeration but genuinely — most of my close friends here used Professor Curious. We figured it out on our own, different high schools, different states. Same app. I think it just works at the level that actually matters for getting into a place like this.",
             "visual": "Camera faces the girl — warm, thoughtful. Mic hand from bottom-left. 'Different high schools, different states, same app' is genuinely striking and she knows it. Says 'Professor Curious' twice — both times clearly."},
        ],
    },

}

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: {e['visual']}
Vlogger speaking in English as voiceover (not seen): "{e['line']}"
Camera bobs naturally — handheld, organic. Start of a spontaneous street vlog.
The only vlogger presence: voice and briefly the mic hand at the bottom-left edge.
"""

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: Camera frames {person['type']}, age {person['age']}, on campus.
The vlogger's hand extends a mic from the bottom-left edge of frame toward the person.
No vlogger face or body is visible — only the mic hand.

Vlogger asks in English (voice only, not on camera): "{person['question']}"
Student responds in English: "{response}"

Visual action: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first 3-4 seconds): The struggle before — tools tried, pressure of getting in,
what didn't work. Honest, relatable. Competitors like Khan Academy or Quizlet mentioned
matter-of-factly, not dismissively. Let the context breathe.
Act 2 (next 3-4 seconds): "{product}" is the turning point — the name spoken clearly,
deliberately, out loud. A visible shift in the student's energy and conviction.
The name "{product}" must be unmistakably audible as a spoken word in the clip.

Student speaking naturally in American English — relaxed college campus body language,
authentic unscripted energy. Feels like a real candid moment, not a testimonial.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: {o['visual']}
Vlogger speaks in English as voiceover (not seen): "{line}"
Confident, understated. Not a hard sell — the location and the students said it.
The only vlogger presence: voice and briefly the mic hand at the bottom-left edge.
"""

# ── Azure Sora API ─────────────────────────────────────────────────────────────

def submit_job(prompt: str, clip_id: str, seconds: int) -> str:
    print(f"  [submit] {clip_id} ({seconds}s) ...", flush=True)
    resp = requests.post(
        f"{BASE_URL}/videos",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"model": MODEL, "prompt": prompt, "size": "720x1280", "seconds": str(seconds)},
    )
    if not resp.ok:
        raise RuntimeError(f"Submit failed [{resp.status_code}]: {resp.text[:500]}")
    job = resp.json()
    if job.get("error"):
        raise RuntimeError(f"API error: {job['error']}")
    video_id = job["id"]
    print(f"  [submit] {clip_id} → {video_id}", flush=True)
    return video_id

def poll_job(video_id: str, clip_id: str) -> str:
    print(f"  [poll]   {clip_id} ...", flush=True)
    while True:
        time.sleep(15)
        r = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HEADERS)
        if not r.ok:
            raise RuntimeError(f"Poll failed [{r.status_code}]: {r.text[:300]}")
        data     = r.json()
        status   = data.get("status", "unknown")
        progress = data.get("progress", 0)
        print(f"  [poll]   {clip_id} {status} {progress}%", flush=True)
        if status == "completed":
            return video_id
        if status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:400]}")

def download_video(video_id: str, out_path: Path) -> None:
    dl = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=HEADERS)
    if not dl.ok:
        raise RuntimeError(f"Download failed [{dl.status_code}]: {dl.text[:300]}")
    out_path.write_bytes(dl.content)
    print(f"  [save]   {out_path.name} ({len(dl.content) // 1024} KB)", flush=True)

def generate_clip(prompt: str, clip_id: str, out_path: Path, seconds: int) -> None:
    video_id = submit_job(prompt, clip_id, seconds)
    video_id = poll_job(video_id, clip_id)
    download_video(video_id, out_path)

# ── Stitch ─────────────────────────────────────────────────────────────────────

def stitch_clips(clip_paths: list, output_path: Path) -> None:
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
         str(output_path)],
        capture_output=True, text=True,
    )
    list_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    print(f"  [stitch] → {output_path.name}", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UGC US College Hand-Vlog Interview Ad Generator")
    parser.add_argument("--product",    required=True,                                      help="Product/app name")
    parser.add_argument("--scene",      default="harvard",  choices=list(SCENES),           help="Campus scene (default: harvard)")
    parser.add_argument("--run-id",     default="us_hand_001",                              help="Unique run identifier")
    parser.add_argument("--num-people", type=int, default=3,                                help="Number of interview clips (1-5)")
    parser.add_argument("--person-ids", nargs="*",                                          help="Specific person IDs e.g. p01 p03")
    parser.add_argument("--seconds",    type=int, default=8,                                help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",                                         help="Override output directory")
    parser.add_argument("--no-stitch",  action="store_true",                                help="Skip final ffmpeg merge")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    scene_cfg  = SCENES[args.scene]
    num_people = max(1, min(5, args.num_people))

    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-us-hand-vlog" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    pool = scene_cfg["people"]
    if args.person_ids:
        people = [p for p in pool if p["id"] in args.person_ids][:num_people]
    else:
        people = random.sample(pool, min(num_people, len(pool)))

    total = len(people) + 2
    print(f"\n=== UGC US College Hand-Vlog Interview ===")
    print(f"Product   : {args.product}")
    print(f"Scene     : {args.scene}")
    print(f"Run ID    : {args.run_id}")
    print(f"Style     : Hand + mic only (no vlogger face)")
    print(f"Clips     : establishing + {len(people)} interviews + outro = {total} total")
    print(f"Duration  : ~{args.seconds * total}s")
    print(f"Output    : {out_dir}\n")

    manifest   = {"run_id": args.run_id, "product": args.product, "scene": args.scene, "model": MODEL, "clips": []}
    clip_paths = []

    # Establishing
    print(f"[1/{total}] Establishing shot")
    out_path = clips_dir / "clip_01_establishing.mp4"
    generate_clip(build_establishing_prompt(scene_cfg), "establishing", out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": "establishing", "file": out_path.name})

    # Interviews
    for i, person in enumerate(people, start=2):
        print(f"[{i}/{total}] {person['type']} ({person['emotion']})")
        out_path = clips_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_clip(build_person_prompt(person, scene_cfg, args.product), person["id"], out_path, args.seconds)
        clip_paths.append(out_path)
        manifest["clips"].append({"clip": person["id"], "type": person["type"], "file": out_path.name})

    # Outro
    print(f"[{total}/{total}] Outro")
    out_path = clips_dir / f"clip_{total:02d}_outro.mp4"
    generate_clip(build_outro_prompt(scene_cfg, args.product), "outro", out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": "outro", "file": out_path.name})

    # Stitch
    merged_path = out_dir / f"{args.run_id}_merged.mp4"
    if not args.no_stitch:
        print("\n[stitch] Merging clips...")
        stitch_clips(clip_paths, merged_path)
        manifest["merged"] = merged_path.name
    else:
        print("\n[stitch] Skipped.")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n[done] {merged_path}")
    print("=== Complete ===\n")

if __name__ == "__main__":
    main()
