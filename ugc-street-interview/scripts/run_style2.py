#!/usr/bin/env python3
"""
STREET INTERVIEW STYLE 2 — Narrative Arc Format
==================================================
New format: vlogger appears ONLY in establishing shot and outro. Interview clips
show subject only (no vlogger in frame). 5 clips follow a narrative arc:
  p01 = introduction (opens with product name)
  p02 = feature expansion
  p03 = transformation
  p04 = emotional connection
  p05 = call to action
Soul-destroying 2-line hook using real Kota suicide statistics. Clips default to 12s.

Usage:
  python3 run_style2.py --product "Professor Curious" --scene kota-coaching --run-id kota_v1
  python3 run_style2.py --product "Professor Curious" --scene doubt-fear --run-id doubt_v1 --vlogger-gender female
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

API_KEY   = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT  = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL     = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL  = f"{ENDPOINT}/openai/v1"
HEADERS   = {"api-key": API_KEY}

# App outro clip — appended to every final merged video
APP_OUTRO = Path(__file__).parent.parent.parent / "assets" / "app_outro_india.MP4"

# ── Vlogger lock — used ONLY in establishing shot and outro ──────────────────

VLOGGER_LOCK_MALE = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Navy blue round-neck t-shirt,
dark jeans. Holds a small black handheld reporter mic with round black foam ball top
in his right hand. Visible from chest up on the left edge of frame, slightly low angle."""

VLOGGER_LOCK_FEMALE = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian female, mid 20s, slim build,
medium-brown skin, long black hair pulled back in a loose ponytail — a few strands loose
at the front, natural and unstyled. No heavy makeup — just kajal, natural look. Wearing
a plain dusty-rose kurta over dark straight-fit jeans. Small gold studs, no other jewellery.
Holds a small black handheld reporter mic with round black foam ball top in her right hand.
Visible from chest up on the left edge of frame, slightly low angle. Warm, empathetic energy —
like a journalist who genuinely cares, not an influencer performing concern."""

VLOGGER_LOCK = VLOGGER_LOCK_MALE  # default; overridden by --vlogger-gender

# ── Subject-only lock — used for ALL interview clips (vlogger NOT visible) ───

SUBJECT_ONLY_LOCK = """INTERVIEW SUBJECT — VLOGGER IS NOT IN FRAME AT ALL:
The vlogger is completely off-camera. ONLY the subject is visible — close portrait,
subject fills 85% of the 9:16 frame. Subject speaks directly toward camera (slightly
off-axis, as if answering someone just off-frame to the left). No mic, no vlogger hand,
no reporter equipment visible. Raw handheld phone footage — slight natural shake,
real ambient noise, no color grading. Kota location visible in background behind subject."""

# ── Scene configs ─────────────────────────────────────────────────────────────

SCENES = {

    # ── 1. Kota coaching centre gate (DEFAULT) ─────────────────────────────────
    "kota-coaching": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7-8pm, streetlights
coming on. Outside a crowded JEE/NEET coaching centre in Kota, Rajasthan — the coaching
capital of India. Students in casual clothes (not uniforms) streaming out with heavy bags,
thick notes, textbooks. Tired, hollow-eyed faces — dark circles, slightly dishevelled,
visibly under pressure. Auto-rickshaws waiting in a row. Small chai stalls with students
standing silently or scrolling phones. The weight of lakhs of dreams is palpable in
every face. Raw phone camera footage, no color grading, natural low-light noise visible.
Feels like one continuous real shoot — Kota's quiet desperation and fierce ambition.""",
        "establishing": {
            "line":   "Bhai — tumhara baccha Kota mein hai. Woh tumhein bol raha hai 'Main theek hoon.' Woh theek nahi hai. 2023 mein yahan 29 bacchon ne apni zindagi khatam ki — har 12 din mein ek. Aur unke parents ko pata hi nahi tha. Main aaj seedha inse poochh raha hoon.",
            "visual": "Vlogger walks slowly toward camera in selfie-cam — not fast and energetic, heavy. Students stream out silently behind him, exhausted. He speaks the first two lines looking dead into the lens — voice low, serious, not performing grief. On the statistics line, he pauses one beat — lets it land. Then: 'Main aaj seedha inse poochh raha hoon.' Camera bobs as he turns toward the students.",
        },
        "outro": {
            "line":   "Bhai, yeh sab real hain. Yeh log jhooth nahi bolte — Kota mein jhooth bolne ki energy nahi hoti. Laakhon bacche yahan hain — akele, thake, andar se toot rahe hain. Aur {product} unka saathi ban gaya hai. Raat ko, jab koi nahi hota — woh hota hai. Link neeche hai. Apne bacche ke liye dekh lo.",
            "visual": "Vlogger turns selfie-cam on himself outside coaching centre, students silently walking past behind him. Speaks fast and directly — no performance, completely genuine. Eyes slightly wet. Points at camera on last line. Slow deliberate thumbs up at the very end.",
        },
        "people": [
            # ── CLIP 1: App Introduction — name it, explain it, plant the seed ──
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "earnest and direct",
             "narrative_role": "introduction",
             "question": "Bhai, yahan sab koi ek app ki baat kar rahe hain — kaunsa app hai yeh?",
             "response": "Professor Curious. — Yeh ek app hai. Download karo. Doubt aaya — open karo, step by step samjhata hai, raat 2 baje bhi. Coaching mein teacher ke paas time nahi — 200 bacche hain class mein. Yeh app rukta hai mere saath jab tak clear na ho. Professor Curious. Yeh naam yaad rakh lo.",
             "visual": "Boy opens his mouth and the very first sound is 'Professor Curious' — two clear words, spoken slowly, directly at camera. Then he immediately explains it's an app. Points slightly on the first 'Professor Curious,' then again at the end on the repeat. Face calm and certain — he is not selling, he is informing. Last shot: eyes to lens, slow nod."},

            # ── CLIP 2: What it actually does — specific, feature-driven ────────
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "explaining with conviction",
             "narrative_role": "feature_expansion",
             "question": "Yeh app kya karta hai exactly — bata na properly.",
             "response": "Baar baar pooch sakti hoon — kabhi nahi kehta 'yeh toh basic hai' ya 'kal poochho.' Raat ko 1 baje Biology ka concept atka — yeh app tha. Step by step. Jab tak clear nahi hua, nahi choda. Coaching mein 200 bacche hain — wahan yeh nahi milta. Iss app mein milta hai.",
             "visual": "Girl speaks fast with real conviction — this is firsthand knowledge, not an ad. Hand gestures emphasize each point. At 'baar baar' she taps her palm. At 'step by step' she slows down briefly — that's the key thing. Eyes direct, no emotional wavering. Pure utility pitch from someone who lived it."},

            # ── CLIP 3: Emotional transformation — before/after, social proof ──
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw transformation",
             "narrative_role": "transformation",
             "question": "Pehle kaisa tha yahan — aur ab kya fark aaya?",
             "response": "Pehle bahut mazak hota tha — doston mein, 'yaar tu clear nahi karega.' Bahut bura lagta tha andar se. Phir iss app se roz ek ek concept clear kiya. Ek mahina. Do mahina. Aaj jo log mazak uthate the, mujhse poochh rahe hain — 'kaise padh raha hai?' App ne sirf doubts nahi, confidence diya. Yeh bahut badi baat hai.",
             "visual": "Boy speaks with a quiet intensity — 'mazak hota tha' lands heavy, he doesn't exaggerate it. Then a visible shift when he talks about the change — sits a little straighter. At 'mujhse poochh rahe hain' a small, earned smile. Last line delivered looking straight at camera — 'yeh bahut badi baat hai.' He means it."},

            # ── CLIP 4: Deep emotional connection — the human relationship ─────
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "quietly moved, grateful",
             "narrative_role": "emotional_connection",
             "question": "Ghar waalon ko pata hai — Kota mein tum kitna struggle kar rahi ho?",
             "response": "Papa roz phone karte hain — 'kaisi hai beta?' Main kehti hoon 'theek hoon.' Sach nahi bolta. Raat ko roti hoon — phir iss app ko khol leti hoon. Yeh app sunti nahi, samjhti nahi — lekin samjha deti hai. Bahut thankful hoon. Yahan jo doston ko nahi bata sakti — andar ka dard — woh iss app ke saath nikal jaata hai. Meri sabse quiet saathi hai yeh.",
             "visual": "Girl's voice drops at 'Papa roz phone karte hain' — she's back home for a second. Small pause. Then she looks up. At 'bahut thankful hoon' her voice catches — just for a beat — then she composes herself. Last line said softly, looking slightly away and then back. This is the most human clip in the whole video."},

            # ── CLIP 5: Direct CTA — viewer addressed, urgency, close ──────────
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "direct and urgent",
             "narrative_role": "call_to_action",
             "question": "Jo abhi yeh video dekh raha hai — unhe kya bologe?",
             "response": "Download karo. Professor Curious. Abhi. Seriously. Akela feel ho raha hai — yeh app hai. Raat ko doubt hai — yeh app hai. Main yahan hoon kyunki iss app ne uss raat roka jab jaana chahta tha. Neeche link dekh rahe ho — ek baar click karo. Bas ek baar.",
             "visual": "Boy leans slightly toward camera — urgent, caring, not aggressive. Points at camera on 'download karo.' Repeats 'Professor Curious' clearly, slowly. On 'uss raat' his expression clouds briefly — that night was real. Then snaps back to direct eye contact on 'neeche link.' Last words 'ek baar' — he holds up one finger. Completely real."},
        ],
    },

    # ── 2. Kota coaching centre — DAYTIME (rattle & crowd, for female vlogger) ─
    "kota-coaching-day": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Daytime, 10-11am, harsh bright
Indian summer sun — strong shadows, dust in the air. Outside a crowded JEE/NEET coaching centre
in Kota, Rajasthan. Students rushing between coaching shifts — backpacks, thick notes clutched,
water bottles, phones. Auto-rickshaws honking constantly in a line, dust rising from road.
A chai stall packed with standing students eating quickly before the next class.
Groups of students in twos and threes, talking fast, stressed, some silent staring at phones.
The relentless noise and scale of Kota in full daylight — not evening's quiet despair, but
morning's grinding pressure. Raw phone camera footage, no color grading, harsh natural sunlight.
Real ambient city noise — horns, voices, rattling autorickshaws. One continuous unedited shoot.""",
        "establishing": {
            "line":   "Ruk jao ek second. Yeh baccha jo tumhare ghar mein hai — Kota mein hai — woh tumhein roz bolega 'Main theek hoon.' Woh theek nahi hai. 2023 mein yahan 29 bacchon ne apni zindagi khatam ki. Unke parents ko pata hi nahi tha. Main aaj seedha inse poochh ti hoon.",
            "visual": "Female vlogger stands in the middle of the rattling, noisy Kota street in selfie-cam — autos honking, students rushing around her. She does NOT move. She speaks the first two sentences completely still, eyes locked on lens — voice quiet but cuts through the noise. On the statistics: slight pause, jaw set. Then she turns and starts walking toward students — 'Main aaj seedha inse poochh ti hoon.' The crowd noise rises as she moves.",
        },
        "outro": {
            "line":   "Yeh sab real hain. Yeh bacche jhooth nahi bolta — Kota mein jhooth bolne ki energy nahi hoti. Laakhon bacche yahan hain — akele, ghar se door, andar se toot rahe hain. Aur {product} unka saathi ban gaya hai. Raat ko, jab koi nahi hota — woh hoti hai. Link neeche hai. Apne bacche ke liye. Abhi dekho.",
            "visual": "Female vlogger turns selfie-cam back on herself — daytime sun behind her, students rushing past in background. Speaks fast and directly — no performance, completely genuine. Voice slightly caught on 'apne bacche ke liye.' Points at camera on 'abhi dekho.' Deliberate thumbs up at the very end.",
        },
        "people": [
            # ── CLIP 1: App Introduction — name it, explain it ─────────────────
            {"id": "p01", "type": "NEET aspirant girl", "age": "17-18", "emotion": "clear and direct",
             "narrative_role": "introduction",
             "question": "Yahan sab koi ek app ki baat kar rahe hain — kaunsa app hai yeh?",
             "response": "Professor Curious. — Yeh ek app hai. Download karo. Doubt aaya — open karo, step by step samjhata hai, raat 2 baje bhi. Coaching mein teacher ke paas time nahi — 200 bacche hain class mein. Yeh app rukta hai mere saath jab tak clear na ho. Professor Curious. Yeh naam yaad rakh lo.",
             "visual": "Girl opens her mouth and the very first sound is 'Professor Curious' — two clear words, directly at camera, slightly raised voice over the street noise. Then immediately explains it's an app. Taps phone in her hand when she says 'download karo.' Repeats 'Professor Curious' at the end, slowly — making sure the name lands above the ambient noise. Confident, not emotional."},

            # ── CLIP 2: What it does ────────────────────────────────────────────
            {"id": "p02", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "explaining with conviction",
             "narrative_role": "feature_expansion",
             "question": "Yeh app kya karta hai exactly — seedha bata.",
             "response": "Baar baar pooch sakta hoon — kabhi nahi kehta 'yeh basic hai' ya 'kal poochho.' Raat 1 baje Physics atka — yeh app tha. Step by step. Jab tak clear nahi hua, nahi choda. Coaching mein 200 bacche hain — wahan yeh nahi milta. Iss app mein milta hai.",
             "visual": "Boy speaks over the daytime street noise — fast, matter-of-fact, firsthand. Taps palm on 'baar baar.' On 'step by step' he slows briefly. Eyes direct, no wavering. Street chaos visible and audible behind him — this feels like a stolen 30 seconds between classes."},

            # ── CLIP 3: Transformation ──────────────────────────────────────────
            {"id": "p03", "type": "NEET aspirant girl", "age": "18-19", "emotion": "quiet earned pride",
             "narrative_role": "transformation",
             "question": "Kota se pehle aur ab — kya fark aaya?",
             "response": "Pehle bahut mazak hota tha — 'tu doctor nahi banega.' Bahut bura lagta tha. Phir iss app se roz ek ek chapter. Ek mahina. Do mahina. Aaj mock mein rank aayi — woh log ab mujhse notes maangne aate hain. App ne sirf doubts nahi, confidence diya. Yeh bahut badi cheez hai.",
             "visual": "Girl speaks with quiet intensity in the busy daytime crowd. 'Mazak hota tha' is said almost to herself — not for effect. Then a visible straightening when she talks about the change. Small real smile on 'notes maangne aate hain.' Last line to camera — 'yeh bahut badi cheez hai' — absolutely meant."},

            # ── CLIP 4: Emotional connection ───────────────────────────────────
            {"id": "p04", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "quietly moved, honest",
             "narrative_role": "emotional_connection",
             "question": "Ghar waalon ko pata hai kitna struggle hai yahan?",
             "response": "Papa roz phone karte hain — 'kaisa hai beta?' Main kehta hoon 'theek hoon.' Sach nahi bolta. Unhe pata nahi. Raat ko rota hoon — phir iss app ko kholna ta hoon. Woh nahi samjhta — but samjha deta hai. Bahut thankful hoon. Yahan jo kisi ko nahi bata sakta — iss app se thoda nikal jaata hai.",
             "visual": "Boy's voice drops at 'Papa roz phone karte hain' — he goes home for one second, even in the noisy daytime street. The crowd noise continues around him. At 'bahut thankful hoon' his voice barely catches — just a fraction. Last line said quietly, looking slightly past camera — then back. The most human clip in the video."},

            # ── CLIP 5: CTA ────────────────────────────────────────────────────
            {"id": "p05", "type": "NEET aspirant girl", "age": "18-19", "emotion": "direct, urgent, warm",
             "narrative_role": "call_to_action",
             "question": "Jo yeh video dekh raha hai — unhe kya bolegi?",
             "response": "Download karo. Professor Curious. Abhi. Sach mein. Akela feel ho raha hai — yeh app hai. Raat ko doubt hai — yeh app hai. Main yahan hoon kyunki iss app ne uss raat roka jab jaana chahti thi. Neeche link dekh rahi ho — ek baar click karo. Bas.",
             "visual": "Girl points directly at camera — not aggressive, urgent and caring. Says 'Professor Curious' slowly and clearly above the street noise — two deliberate words. On 'uss raat' her expression clouds for a beat — that night was real. Snaps back to direct eye contact. Holds up one finger on 'ek baar.' Completely authentic."},
        ],
    },

    # ── 3. Doubt fear — generic Indian school, any city (UNIVERSAL FORMAT) ────
    "doubt-fear": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, 3-4pm, warm natural light.
Outside a typical Indian school gate in a regular city or town — NOT Kota, not a coaching centre.
Students in school uniforms (white shirts, grey pants or skirts) streaming out with backpacks.
Auto-rickshaws and parents on scooters waiting outside. Normal Indian school chaos — 13-16 year olds,
laughing, rushing, some quiet. Canteen or chai stall nearby. This is EVERY school in EVERY Indian city.
Raw phone camera footage, no color grading, natural handheld shake. Feels like any school, any child.
The universality is the point — this could be YOUR child's school.""",
        "establishing": {
            "line":   "Ek second ruko. Kya aapke bacche school mein doubt poochne se darte hain? Kyun darte hain? Kyunki baaki bacche unka mazak udaate hain. Kyunki teacher bhi kabhi kabhi udaate hain. Yeh sharm — yahi cheez unhe peeche rakh ti hai. Main aaj seedha inse poochh raha hoon.",
            "visual": "Vlogger stands outside school gate in selfie-cam as uniformed students stream out behind. Speaks the first two sentences slowly and directly — not loud, not performing. The question 'Kya aapke bacche school mein doubt poochne se darte hain?' is asked to the viewer, not to the crowd. A beat of silence after the shame line. Then he turns and moves toward students.",
        },
        "outro": {
            "line":   "Tumne suna inhe? Doubt poochna chahte the — par darte the. Raat ko akele suljhate the. Ek app ne yeh badla — {product}. Ab poochh te hain. Bina sharm ke. Raat ko, akele, jab tak clear na ho. Link neeche hai. Apne bacche ke liye — aaj hi try karo.",
            "visual": "Vlogger turns selfie-cam back on himself — school gate visible behind, last students leaving. Speaks fast and direct — no performance. On 'apne bacche ke liye' his voice softens just slightly. Points at camera. Deliberate thumbs up at the end.",
        },
        "people": [
            # ── CLIP 1: App Introduction ────────────────────────────────────────
            {"id": "p01", "type": "school boy",  "age": "14-15", "emotion": "direct and clear",
             "narrative_role": "introduction",
             "question": "Yahan sab ek app ki baat kar rahe hain — kaunsa app hai yeh?",
             "response": "Professor Curious. — Yeh ek app hai. Doubt aaya — open karo, seedha poochho, koi nahi dekhta. Koi mazak nahi udaata. Step by step samjhata hai jab tak clear na ho. Class mein poochh ne mein dar lagta tha — ab iss app pe poochh ta hoon. Professor Curious. Yeh naam yaad rakh lo.",
             "visual": "Boy opens his mouth and the very first sound out is 'Professor Curious' — clearly, to camera. Then immediately explains it's an app. Calm, direct — not emotional, informational. Points on the first 'Professor Curious,' slow repeat at the end. Clean, confident school-age kid talking straight."},

            # ── CLIP 2: Feature expansion ──────────────────────────────────────
            {"id": "p02", "type": "school girl", "age": "13-14", "emotion": "relieved and explaining",
             "narrative_role": "feature_expansion",
             "question": "Yeh app kya karta hai exactly?",
             "response": "Baar baar pooch sakti hoon — kabhi nahi kehta 'yeh toh simple hai' ya 'phir poochho.' Raat ko Maths ka ek step nahi samjha — yeh app tha. Step by step. Jab tak clear nahi hua, nahi gaya. Class mein kabhi poochh nahi paati thi — sab hanste the. Iss app mein koi nahi hota dekhne wala.",
             "visual": "Girl speaks fast with real relief — like she's describing something that genuinely changed her daily life. Taps palm on 'baar baar.' Slight wince on 'sab hanste the' — that memory is real. Then lighter: 'koi nahi hota dekhne wala.' Eyes direct, no drama."},

            # ── CLIP 3: Transformation ─────────────────────────────────────────
            {"id": "p03", "type": "school boy",  "age": "15-16", "emotion": "quiet earned confidence",
             "narrative_role": "transformation",
             "question": "Pehle class mein kaisa tha — aur ab kya fark hai?",
             "response": "Pehle kabhi haath nahi uthata tha. Kabhi. Dar lagta tha — sab dekhenge, koi hansega, teacher bura bolega. Phir iss app se raat ko concepts clear kiye. Ek mahina. Ab class mein haath uthata hoon. Sir ne ek baar bola — 'yeh baccha pehle kahan tha?' Yeh sunke kuch alag hi laga.",
             "visual": "Boy speaks with a quiet intensity. 'Kabhi haath nahi uthata tha' — said with the weight of years of silence. Small real smile at 'ab class mein haath uthata hoon.' At 'sir ne bola' — a visible, earned pride. Last line to camera — he means it. No exaggeration needed."},

            # ── CLIP 4: Emotional connection ───────────────────────────────────
            {"id": "p04", "type": "school girl", "age": "14-15", "emotion": "honest and moved",
             "narrative_role": "emotional_connection",
             "question": "Ghar mein doubt aaye toh kya karte the pehle?",
             "response": "Pehle raat ko bas roti thi — Maths nahi aata tha, Papa kaam pe hote the, Maa padhni nahi. Kisi ko poochh nahi sakti thi. Teacher se dar — classmates se sharm. Phir iss app ko khola. Raat ko, akele — koi nahi dekhta, koi nahi hansata. Bahut thankful hoon. Akeli nahi hoon padhte waqt ab.",
             "visual": "Girl's voice drops at 'raat ko bas roti thi' — completely real, no performance. She's back in that room for a second. At 'koi nahi dekhta, koi nahi hansata' — visible relief on her face. 'Bahut thankful hoon' said softly, eyes a little bright. Last line — she means it. Parents watching will feel this."},

            # ── CLIP 5: CTA ────────────────────────────────────────────────────
            {"id": "p05", "type": "school boy",  "age": "14-15", "emotion": "direct, warm, urgent",
             "narrative_role": "call_to_action",
             "question": "Jo yeh video dekh raha hai — parents ya bacche — unhe kya bologe?",
             "response": "Ek kaam karo — Professor Curious download karo. Abhi. Agar tumhara baccha class mein haath nahi uthata — yeh app hai. Agar raat ko akele struggle kar raha hai — yeh app hai. Koi judge nahi karta, koi mazak nahi udaata, kabhi nahi kehta kal poochho. Neeche link hai. Bas ek baar.",
             "visual": "Boy speaks directly to camera — the most direct clip in the video. Points finger on 'download karo.' Slow and clear on 'Professor Curious.' On 'koi judge nahi karta' — a slight nod, he knows this is the thing. Holds up one finger on 'ek baar.' Completely real, zero performance."},
        ],
    },

    # ── 4. School gate ────────────────────────────────────────────────────────
    "school-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon golden-hour
light. Outside a busy Indian school iron gate in Kota. Dozens of school kids in white shirts and
grey pants/skirts with heavy backpacks streaming out after exams — some happy, some anxious, noisy.
Parents waiting, yellow auto-rickshaws and bikes parked, a chai stall in background.
Organic, slightly chaotic energy. Raw iPhone-style handheld footage,
no color grading, natural handheld shake. One continuous real shoot.""",
        "establishing": {
            "line":   "Bhai, aaj exams khatam hue hain Kota mein — chalo seedha bacchon se poochte hain, kaisi rahi taiyari!",
            "visual": "Vlogger walks toward school gate in selfie-cam mode, points at kids pouring out, grins at camera, eyebrows raised, excited and spontaneous. Camera bobs with walk.",
        },
        "outro": {
            "line":   "Sunaa? Sab ek hi app ki baat kar rahe hain — Professor Curious. Link neeche diya hai.",
            "visual": "Vlogger walks away from gate in selfie-cam, kids streaming out behind. Looks at camera, raises eyebrows, relaxed thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "school boy",  "age": "13-14", "emotion": "relieved and emotional",
             "question": "Exam ke pehle dar lag raha tha?",
             "response": "Bahut dar tha bhaiya — raat ko so nahi pa raha tha, ek ek formula bhool raha tha. Phir Professor Curious pe sab clear kiya — woh samjhata hai, judge nahi karta. Aaj paper mein sab aaya. Sach mein aaya.",
             "visual": "Kid's eyes go wide remembering the fear. Then visibly softens at 'Professor Curious' — says the name clearly, proudly. Relief is real."},
            {"id": "p02", "type": "school girl", "age": "12-13", "emotion": "sincere and moved",
             "question": "Ghar mein koi padhata hai kya?",
             "response": "Nahi bhaiya, Papa kaam pe hote hain raat tak. Main akeli padh ti thi — bahut mushkil tha. Phir Professor Curious use karna shuru kiya. Woh meri saari confusions door karta tha — koi bhi time pe. Main ab akeli nahi hoon padhte waqt.",
             "visual": "Girl is quiet, sincere. Slightly teary at 'akeli.' At 'Professor Curious' she straightens — says the name clearly with a small proud smile."},
            {"id": "p03", "type": "school boy",  "age": "13-14", "emotion": "funny then sincere",
             "question": "Koi app use kiya kya — sach bata!",
             "response": "Bhaiya seedha bolunga — pehle kuch nahi karta tha, bas rota tha. Phir dost ne Professor Curious bataya. Usne ek dum simple mein samjhaya — roz use karta hoon. Aaj bahut achha gaya.",
             "visual": "Boy grins at first, then gets genuine. Says 'Professor Curious' looking straight at camera — slow and clear, like he wants everyone watching to remember the name."},
            {"id": "p04", "type": "school girl", "age": "13-14", "emotion": "proud and emotional",
             "question": "Mummy ko kya bologe result ka?",
             "response": "Main bolungi — Mummy, tumne jo expect kiya tha woh karke aayi hoon. Raat ko Professor Curious pe padha tha — woh samjhata tha jab koi nahi hota. Aaj sab aaya paper mein. Yehi toh chahiye tha.",
             "visual": "Girl's voice catches slightly at 'Mummy.' Composes herself. Says 'Professor Curious' deliberately, loud enough — like she's rehearsing telling her mother."},
            {"id": "p05", "type": "school boy",  "age": "11-12", "emotion": "shy then proud",
             "question": "Kisi app se padha kya — batao na!",
             "response": "Haan... Professor Curious. Mummy ne install kiya tha. Main bahut confuse rehta tha Maths mein — woh baar baar samjhata tha, gaali nahi deta tha... haha. Ab Maths achha lagta hai.",
             "visual": "Boy initially shy, looks down. Then says 'Professor Curious' clearly — small giggle at his own joke, then a real, warm smile. Completely genuine."},
        ],
    },

    # ── 3. Coaching centre gate (non-Kota) ─────────────────────────────────────
    "coaching-centre": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7-8pm, streetlights
coming on. Outside a crowded JEE/NEET coaching centre building in Kota, Rajasthan. Students in
casual clothes (not uniforms) streaming out with heavy bags, notes, textbooks. Tired, focused
faces — dark circles, slightly dishevelled. Auto-rickshaws waiting in a row outside.
A few tea stalls with students standing and sipping in silence. Raw phone camera footage,
no color grading, natural low-light noise visible. The weight of Kota hangs in the air.""",
        "establishing": {
            "line":   "Kota mein hoon — coaching khatam hui. Yahan ke bacchon se poochte hain ki raat ko kya hota hai jab koi nahi hota.",
            "visual": "Vlogger walks toward the coaching centre exit as silent, burdened students stream out, turns selfie-cam to himself, empathetic not entertained, gestures quietly at the students behind him.",
        },
        "outro": {
            "line":   "Raat ko coaching ke baad bhi yeh log akele ladte hain apni padhai se — aur Professor Curious unka saathi hai. Link neeche.",
            "visual": "Vlogger turns selfie-cam on himself outside coaching centre, students silently calling autos behind him. Serious, knowing look. Slow thumbs up — felt, not performed.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "broken then hopeful",
             "question": "Coaching mein kitne ghante padhte ho — aur phir bhi kya hota hai?",
             "response": "12-14 ghante roz. Phir bhi raat ko teacher ka concept dimag mein nahi rehta — class mein poochh nahi paate, hazaar bacche hain. Bahut akela lagta hai. Professor Curious pe woh concepts raat ko clear karta hoon — woh rukta hai mere saath tab tak jab tak samajh na aa jaaye.",
             "visual": "Boy looks genuinely exhausted. Voice drops at 'akela.' Rallies at 'Professor Curious' — says it clearly, deliberately. A quiet resolve returns to his face."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "focused and emotional",
             "question": "NEET clear karna hai — lekin aaj kaisi feel ho rahi hai?",
             "response": "Aaj mock mein fail hua. Ghar phone kiya — unhe bata nahi sakti kitni problem ho rahi hai, woh pehle se itna kar rahe hain mere liye. Phir Professor Curious pe Biology ka ek chapter khola — woh itna clearly samjhata hai. Raat tak confidence wapas aa gaya tha.",
             "visual": "Girl's voice tightens at 'ghar phone kiya.' A beat of real vulnerability. At 'Professor Curious' she steadies, looks straight at camera. Says the name slowly, clearly — like it means something."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw honesty",
             "question": "Kota mein kitna mushkil hai — sach mein?",
             "response": "Bahut mushkil hai bhai. Log yahan rank ke liye jeete hain — roz toot te hain. Ek raat itna bura laga ki kuch nahi karna tha. Phir Professor Curious khola, ek problem solve ki, phir ek aur — subah ho gayi thi. Woh app nahi jaanta — but usne raat nikaali meri.",
             "visual": "Boy looks away for a second — raw, no performance. Says 'Professor Curious' quietly but clearly, looking straight to camera. Then nods once — that's the whole truth."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "fierce",
             "question": "Topper kaisi banti ho yahan — koi secret?",
             "response": "Koi secret nahi — bas yeh ki main roti hoon, phir uthti hoon. Jo samajh nahi aata — Professor Curious pe jaati hoon. Woh tab tak samjhata hai jab tak clear na ho. Baar baar. Kabhi nahi kehta kal poochh. Yahi edge hai mera.",
             "visual": "Girl is fierce, minimal emotion but the weight is present. Says 'Professor Curious' like naming a trusted ally — clear, loud, owns it completely."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",
             "question": "Aaj ka test kaisa gaya?",
             "response": "Chemistry ka ek concept tha — 3 din se samajh nahi aa raha tha. Raat ko Professor Curious pe 2 ghante baitha. Step by step — ruka, samjhaya. Aaj wahi question aaya. Pehli baar is saal achha feel hua Kota mein.",
             "visual": "Boy exhales slowly — real relief, eyes a little wet. Says 'Professor Curious' with a slow nod, completely sincere. First genuine smile in the clip."},
        ],
    },

    # ── 4. Results day ────────────────────────────────────────────────────────
    "results-day": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Morning, bright natural light.
Outside a school in Kota on board exam results day. Chaotic, emotional scene — students clustered
in groups checking phones and printed result sheets, some crying with joy, some hugging
parents, some jumping. Parents in formal clothes standing anxiously. Teachers near the gate.
Notice boards with results visible in background. Raw iPhone-style footage,
no color grading, natural handheld shake. The most charged day of these students' lives.""",
        "establishing": {
            "line":   "Bhai, aaj board results aaye hain Kota mein — yahan ka maahaul dekho. Chalo kuch bacchon se baat karte hain!",
            "visual": "Vlogger walks into the emotional crowd in selfie-cam mode, visibly moved — students crying, parents hugging kids. He gestures wide at the chaos behind him, voice slightly unsteady.",
        },
        "outro": {
            "line":   "Result ka din hai aaj — aur jo khush hain, unka ek common connection hai — Professor Curious. Link neeche.",
            "visual": "Vlogger walks away from celebrating crowd in selfie-cam. Emotional scenes still visible behind. He looks at camera quietly, gives a thumbs up with a genuine smile — moved by what he witnessed.",
        },
        "people": [
            {"id": "p01", "type": "student boy",   "age": "16-17", "emotion": "overwhelmed with joy",
             "question": "Bhai, kaisa result aaya?",
             "response": "95 percent... mujhe yakeen nahi ho raha. Papa ne government job chodi thi ek baar mujhe padhaane ke liye. Aaj unhe call karta hoon. Professor Curious pe roz padhta tha — raat ko jo samajh nahi aata, woh samjha deta tha. Yahi result hai unka bhi.",
             "visual": "Boy is overwhelmed — jaw trembles briefly, eyes wet. Mid-sentence he composes himself. Says 'Professor Curious' slowly, clearly — naming it like he's giving credit. Then breaks into a full smile."},
            {"id": "p02", "type": "student girl",  "age": "15-16", "emotion": "crying happy tears",
             "question": "Kya hua — khush ho ya rona ho raha hai?",
             "response": "Dono bhaiya — Science mein 98 aaya. Maa kehti thi 'beta kuch nahi hoga tere se' — not taunting, she was scared. Main bhi dara hua tha. Professor Curious ne raat ko mujhe hath tham liya jab koi nahi tha. Aaj ka result unka bhi hai.",
             "visual": "Girl crying openly, wipes eyes. Voice breaks at 'Maa.' Then says 'Professor Curious' clearly through tears — the name comes out strong, not soft. Friends around her crying too."},
            {"id": "p03", "type": "student boy",   "age": "16-17", "emotion": "proud and reflective",
             "question": "Ek saal pehle kya sochte the?",
             "response": "Sochta tha fail ho jaunga. Coaching ka pressure, ghar ki umeed — sab ek saath. Ek raat bilkul toot gaya tha. Phir Professor Curious pe ek chapter khola — aur phir ek aur. Woh raat khatam nahi hui bhi tab tak jab tak sab clear nahi hua. Woh app meri wajah se nahi thaka.",
             "visual": "Boy speaks quietly, one hand on heart. Looks away briefly remembering. Says 'Professor Curious' deliberately — looking at camera, slow and clear. Real gratitude."},
            {"id": "p04", "type": "parent",        "age": "40-45", "emotion": "proud, emotional parent",
             "question": "Uncle, bacche ka result kaisa aaya?",
             "response": "Bahut achha aaya beta. Main raat ko dekh ta tha — light on rehti thi kamre mein. Ek app se padhta tha — Professor Curious. Maine kabhi nahi rokey — jo concentrate kar raha tha toh hona chahiye. Aaj woh mehnat ka phal mila.",
             "visual": "Father's eyes glisten. Arm around child's shoulder. Says 'Professor Curious' carefully — like he memorized the name. Proud, composed, deeply moved."},
            {"id": "p05", "type": "student girl",  "age": "15-16", "emotion": "relieved and grateful",
             "question": "Sabse tough subject kaunsa tha aur kaise crack kiya?",
             "response": "Maths bhaiya — formulas bhool jaati thi exam pressure mein. Raat ko bahut roti thi. Professor Curious pe step by step practice kiya — woh samjhata tha, daanta nahi. Aaj Maths mein 92 aaya. Woh app nahi hoti toh yeh din nahi hota.",
             "visual": "Girl holds result printout up, voice shakes briefly. Says 'Professor Curious' firmly, clearly — like she's speaking to everyone who's still struggling. Then smiles, shows paper to camera."},
        ],
    },

    # ── 5. Chai stall ─────────────────────────────────────────────────────────
    "chai-stall": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening golden hour, warm
orange light. Small roadside chai stall right outside a coaching centre in Kota — a
wooden bench, a gas stove with a large chai pot, steam rising, glass cups on a tray.
Students in casual clothes sitting on benches sipping chai, bags on the ground,
books open, decompressing after a long day. Exhausted, slightly numb faces.
Street noise in background — autos passing, distant chatter.
Raw phone camera footage, no color grading. Intimate, very authentic Kota atmosphere.""",
        "establishing": {
            "line":   "Kota mein coaching ke baad yahan chai pi rahe hain bacche — seedha inse poochte hain, kya chal raha hai andar se.",
            "visual": "Vlogger walks up to a chai stall where students sit in tired silence, turns selfie-cam on himself, points quietly at the exhausted students behind him, steam from chai visible. Empathetic tone, not entertained.",
        },
        "outro": {
            "line":   "Chai ki tarah Professor Curious bhi sab ke saath hai — roz, har raat, har doubt pe. Link neeche.",
            "visual": "Vlogger holds a glass of chai toward camera with a quiet nod, students visible on bench behind, then turns selfie-cam to himself walking away from the stall.",
        },
        "people": [
            {"id": "p01", "type": "student boy",  "age": "14-15", "emotion": "exhausted and candid",
             "question": "Raat ko padhai karte waqt kya hota hai jab kuch samajh nahi aata?",
             "response": "Bhaiya sach bolunga — ek baar phone uthaya tha ghar call karne ko. Phir rakha diya — unhe pareshan nahi karna tha. Professor Curious khola uss raat. Woh samjhata raha — 2 baje tak. Socha tha quit karunga. Woh raat nahi ki.",
             "visual": "Boy sips chai, totally drained. Voice very quiet at 'ghar call karne ko.' Says 'Professor Curious' simply — not dramatic, just true. Stares into chai cup."},
            {"id": "p02", "type": "student girl", "age": "14-15", "emotion": "honest and raw",
             "question": "Kota mein akela feel hota hai kya?",
             "response": "Bahut. Ghar mein maa hoti thi — doubt hota toh pooch leti thi. Yahan koi nahi. Raat ko Professor Curious khola — woh samjhata hai, judge nahi karta, thakta nahi. Chai peene ke baad wahi pehli cheez kholti hoon. Woh maa ki jagah nahi le sakta — but kuch toh hai.",
             "visual": "Girl's voice catches at 'maa.' She looks at her chai cup for a moment. Then says 'Professor Curious' clearly, steadily — not performing grief, just honest. A real, human moment."},
            {"id": "p03", "type": "student boy",  "age": "15-16", "emotion": "dark humor, then real",
             "question": "Kota mein sabse mushkil kya hai?",
             "response": "Apne aap se fight karna bhaiya. Sab se zyada yahi thakata hai. Raat ko Professor Curious se jhagada karta hoon — matlab doubts deta hoon, woh jawab deta hai. Kabhi kabhi sochta hoon woh mujhse better teacher hai than anyone I've paid fees for.",
             "visual": "Boy grins tiredly — dark humor but real underneath. Says 'Professor Curious' with a slight laugh that turns genuine. Points at camera — that's the truth."},
            {"id": "p04", "type": "student girl", "age": "13-14", "emotion": "sweet and vulnerable",
             "question": "Aaj ka exam kaisa gaya — sach mein bata.",
             "response": "Raat bhar roti rahi — soch rahi thi fail ho jaungi. Professor Curious pe ek ek chapter cover kiya. Subah uthke exam diya. Achha gaya bhaiya. Ab chai pi rahi hoon — pehli baar chain se.",
             "visual": "Girl exhales slowly, holds her chai with both hands like it's a comfort. Says 'Professor Curious' quietly but clearly — peace visible on her face. First calm moment in a long time."},
            {"id": "p05", "type": "student boy",  "age": "14-15", "emotion": "passionate and grateful",
             "question": "Ek cheez recommend karo jo sach mein kaam aayi Kota mein.",
             "response": "Professor Curious. Bhaiya seedha bolunga — yeh app nahi hoti toh main yahan nahi hota abhi. Jo samajh nahi aata, scan karo — woh samjhata hai tab tak jab tak clear na ho. Kota mein yahi chahiye hota hai — koi jo chode na.",
             "visual": "Boy puts chai cup down, points at camera — completely earnest. Says 'Professor Curious' slowly and clearly, almost spelling it out. Full eye contact. No performance — pure sincerity."},
        ],
    },

    # ── 6. College gate ────────────────────────────────────────────────────────
    "college-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon bright natural light.
Outside a busy Indian college main gate in Kota. Students in casual clothes streaming out after
semester exams — 18-20 year olds, many Kota veterans now in college, confident but carrying
the scars of their coaching days. Some on phones, some with earphones. Raw phone camera
footage, no color grading, natural handheld shake. Aspirational but layered with history.""",
        "establishing": {
            "line":   "Bhai, college ke baahir hoon Kota mein — yahan ke bacche Kota ke veteran hain. Poochte hain ki kaise survive kiya unhone.",
            "visual": "Vlogger stands outside college gate in selfie-cam mode, points at students confidently streaming out, serious and empathetic look at camera.",
        },
        "outro": {
            "line":   "College pahunch gaye yeh log — Kota se lad ke. Professor Curious unka ek saathi tha. School wale sun rahe ho? Link neeche.",
            "visual": "Vlogger walks away from college gate toward camera in selfie-cam. Confident older students visible behind. Slow nod, meaningful thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "college boy",  "age": "18-19", "emotion": "nostalgic and honest",
             "question": "Kota survive kiya — kaise?",
             "response": "Ek raat itna bura laga tha ki bag pack kar liya tha. Seriously. Phir Professor Curious pe Physics ka ek chapter khola — aur subah ho gayi. Yahan hoon aaj usi wajah se. Woh app jaanta nahi mujhe — but woh wahan tha uss raat.",
             "visual": "Boy leans against college gate, reflective. Voice goes quiet at 'bag pack kar liya.' Says 'Professor Curious' slowly, deliberately — like he wants anyone still in Kota to hear it clearly."},
            {"id": "p02", "type": "college girl", "age": "18-19", "emotion": "composed and sincere",
             "question": "Kota ke baad college — kya fark laga?",
             "response": "Confidence aaya. Kota mein roz tootha tha — roz Professor Curious pe uth ta tha. Woh app ne sikhaya ki toot ke bhi padhte rehte hain. Yahi habit college mein bhi kaam aa rahi hai. Wo app meri foundation hai.",
             "visual": "Girl is composed but emotion is present underneath. Says 'Professor Curious' with quiet pride — like naming something that shaped her. Steady eye contact."},
            {"id": "p03", "type": "college boy",  "age": "19-20", "emotion": "self-aware and real",
             "question": "Kota mein kya bachaya tumhe?",
             "response": "Seedha bolunga — Professor Curious. Raat 1 baje bhi kholta tha woh app. Woh kabhi band nahi hua, kabhi slow nahi hua. Jab sab thak jaate hain — teacher, friends — woh nahi thaka. Yahan hoon toh usi ki wajah se hoon.",
             "visual": "Boy is candid, no bravado. Says 'Professor Curious' looking straight at camera — slowly, loudly. Not a testimonial, a fact."},
            {"id": "p04", "type": "college girl", "age": "18-19", "emotion": "heartfelt",
             "question": "Ek cheez jo sabse zyada kaam aayi Kota mein?",
             "response": "Professor Curious app. Raat 12 baje bhi doubt aata tha — koi nahi hota. Teacher so gaye, dost so gaye — woh hoti thi. Usne kabhi nahi bola kal poochh. Kabhi nahi. Yahi fark hai.",
             "visual": "Girl places hand on heart briefly. Says 'Professor Curious' clearly, loudly — like she wants it heard. Genuine and moving. Doesn't need to dramatize it."},
            {"id": "p05", "type": "college boy",  "age": "18-19", "emotion": "direct, motivational",
             "question": "Jo abhi Kota mein hain unhe kya bologe?",
             "response": "Ek kaam karo — Professor Curious download karo. Abhi. Kota mein akela feel ho raha hai — woh wahan hai. Raat ko doubt hai — woh wahan hai. Main yahan hoon kyunki woh wahan tha jab main nahi tha.",
             "visual": "Boy speaks directly to camera, points finger — not aggressive, urgent and caring. Says 'Professor Curious' twice — slowly and clearly both times. Means every word."},
        ],
    },

    # ── 7. Parent pickup zone ──────────────────────────────────────────────────
    "parent-pickup": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon warm light.
Parent pickup zone outside a school in Kota — cars, scooters, and auto-rickshaws in a line,
Indian parents (mothers in sarees/salwar kameez, fathers in office clothes) waiting anxiously.
Kids in school uniforms running out to their parents — hugs, bags handed over.
Mix of relief and emotion on parents' faces. Raw phone camera footage, no color grading,
natural handheld shake. Warm, emotional, family energy charged with Kota's intensity.""",
        "establishing": {
            "line":   "Kota mein parents aa rahe hain bacchon ko lene — chalo unse poochte hain, kya chal raha hai ghar mein.",
            "visual": "Vlogger walks through the parent pickup area in selfie-cam mode, points at waiting parents with helmets and car keys — empathetic, warm tone.",
        },
        "outro": {
            "line":   "Parents aur bacche — dono ki ek hi baat — Professor Curious. Link neeche hai, ghar mein try karo aaj.",
            "visual": "Vlogger walks back toward camera in selfie-cam, parent-child pairs visible behind him, some emotional reunions. Warm smile, gentle thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "mother with child", "age": "35-40", "emotion": "proud and tearful",
             "question": "Aunty, bacche ka exam kaisa gaya?",
             "response": "Bahut achha gaya beta. Main har raat sochti thi — Kota mein akela hai, koi nahi hoga saath. Phir dekha tha — raat ko ek app use karta tha — Professor Curious — sab doubts wahan clear karta tha. Tab main ne chain li. App ne mere bacche ko akela nahi chhoda.",
             "visual": "Mother's eyes fill. She squeezes child's shoulder. Says 'Professor Curious' slowly — like she memorized it to tell others. Raw, real parental relief."},
            {"id": "p02", "type": "father with child",  "age": "38-45", "emotion": "quiet pride",
             "question": "Uncle, Kota mein chhodna mushkil lagta hai bacche ko?",
             "response": "Bahut mushkil tha pehli baar. Ghar jaate waqt rota tha main — woh nahi, main. Phir usne bataya — Professor Curious pe padhta hoon, sab clear ho jaata hai. Tab se chinta kum hui. Woh app ne mera kaam kiya.",
             "visual": "Father is still for a moment — the admission that HE cried is quiet and real. Says 'Professor Curious' with a nod — matter-of-fact, but loaded with meaning. Son looks up at him."},
            {"id": "p03", "type": "school girl",        "age": "12-13", "emotion": "running to mom, emotional",
             "question": "Arre, mummy ko kya bataya result ka?",
             "response": "Mummy — bahut achha gaya! Raat bhar Professor Curious pe padha tha — woh samjha ta tha sab kuch. Aaj sab aaya! Ab ice cream do please!",
             "visual": "Girl runs to mom mid-interview, grabs her arm, completely lit up. Says 'Professor Curious' fast and clear — owning it, then immediately back to being a happy kid asking for ice cream."},
            {"id": "p04", "type": "mother with child", "age": "38-42", "emotion": "grateful and honest",
             "question": "Ghar se Kota — kab chain milti hai aapko?",
             "response": "Jab yeh raat ko padh raha hota hai — Professor Curious pe. Main call karti hoon toh kehta hai 'Maa main theek hoon, padh raha hoon.' Tab chain aati hai. Woh app ne mujhe bhi sambhala iss saal.",
             "visual": "Mother laughs softly but eyes are glassy. Says 'Professor Curious' clearly, warmly — like it's a family friend. Child tugs at her hand, she laughs and looks at camera."},
            {"id": "p05", "type": "father with child",  "age": "40-45", "emotion": "real and direct",
             "question": "Aap bacchon ki padhai mein help karte ho?",
             "response": "Main engineer hoon — Maths karta hoon. But Kota mein itna competition hai — main nahi kar sakta itna. Professor Curious karta hai. Yeh wahan padhta hai — raat ko, akele — aur woh samjhata hai. Mujhe se zyada patience hai uss app mein.",
             "visual": "Father is dry and honest — almost funny but real. Says 'Professor Curious' seriously, clearly. Son looks up at him with a grin. An earned, true endorsement."},
        ],
    },

}

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {e['visual']}
Vlogger speaking in Hindi to camera: "{e['line']}"

PACING — CRITICAL: Vlogger speaks FAST and CONTINUOUSLY — rapid delivery, short breath pauses only.
Every second of the 8s clip has dialogue happening. No long silences or dead air.
Camera bobs naturally with his walk. Start of a candid street vlog — empathetic, urgent, unscripted.
"""

NARRATIVE_ROLE_CONTEXT = {
    "introduction": (
        "NARRATIVE ROLE — CLIP 1 OF 5 (APP INTRODUCTION):\n"
        "⚠️ HARD RULE: The subject's VERY FIRST WORDS — before anything else — must be '{product}'\n"
        "The clip opens with the subject saying '{product}' as the opening two syllables. Not after context. Not mid-sentence. FIRST.\n"
        "Then they immediately explain it is an APP. The name '{product}' is spoken again at the very end.\n"
        "The viewer must leave this clip knowing exactly what the app is called and that it exists."
    ),
    "feature_expansion": (
        "NARRATIVE ROLE — CLIP 2 OF 5 (WHAT IT DOES):\n"
        "Viewer already heard the app name. This clip explains HOW it works — specific, functional.\n"
        "Subject refers to 'yeh app' (this app) rather than repeating the full name.\n"
        "Focus: availability, patience, step-by-step — things no tutor or coaching can offer."
    ),
    "transformation": (
        "NARRATIVE ROLE — CLIP 3 OF 5 (BEFORE vs AFTER):\n"
        "Viewer knows what the app is and what it does. Now show the TRANSFORMATION it caused.\n"
        "Subject talks about who they were before vs who they are now because of 'iss app.'\n"
        "Emotional arc: embarrassment/struggle → quiet pride. Social proof is powerful here."
    ),
    "emotional_connection": (
        "NARRATIVE ROLE — CLIP 4 OF 5 (HUMAN CONNECTION):\n"
        "The deepest, most human clip. Subject reveals what the app means emotionally — not features.\n"
        "'Iss app ne saath diya jab koi nahi tha.' The app as a companion, not a tool.\n"
        "Gratitude, warmth, vulnerability. This is the clip that makes parents want to download it."
    ),
    "call_to_action": (
        "NARRATIVE ROLE — CLIP 5 OF 5 (CALL TO ACTION):\n"
        "Final clip. Subject speaks DIRECTLY to the viewer watching this video.\n"
        "Says '{product}' clearly one more time. Tells them: download it, try it, it worked for me.\n"
        "Urgency without pressure. Authentic recommendation from a peer, not an ad."
    ),
}

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    role_key  = person.get("narrative_role", "")
    role_ctx  = NARRATIVE_ROLE_CONTEXT.get(role_key, "").format(product=product)
    return f"""{scene['setting']}

{SUBJECT_ONLY_LOCK}

{person['type']}, age {person['age']}, answers a question they were just asked off-camera.

The off-camera question (just asked, not shown): "{person['question']}"
Subject's response in Hindi: "{response}"

Visual action: {person['visual']}

{role_ctx}

CLIP PACING — TWO ACTS, FAST DELIVERY:
Act 1 (first 3-4 seconds): Raw emotional truth — the struggle, pressure, loneliness, fear.
Short fast sentences. Real pain on the face. No pause-and-breathe acting — quick, clipped, urgent.
Act 2 (next 3-4 seconds): The emotional shift — {product}, gratitude, resolve, or direct CTA.
The app name (when used) MUST be audible — spoken clearly, deliberately, not mumbled.

DENSITY: Subject speaks continuously through most of the 8 seconds — minimal dead air.
Natural Indian hand gestures, expressive face, authentic emotion. Completely candid — not staged.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera: "{line}"

PACING: Fast and direct — vlogger speaks continuously, rapid delivery, short pauses only.
Genuine conviction — not a sales pitch, a real conclusion to what he just witnessed.
Thumbs up at the end. End of street interview — same shoot, same vlogger, same Kota.
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
    # Append app outro if it exists
    all_paths = list(clip_paths)
    if APP_OUTRO.exists():
        all_paths.append(APP_OUTRO)
        print(f"  [outro]  Appending app outro: {APP_OUTRO.name}", flush=True)
    else:
        print(f"  [outro]  Warning: app outro not found at {APP_OUTRO}", flush=True)

    # Build ffmpeg filter for scale + concat (handles different resolutions)
    inputs = []
    filter_parts = []
    for i, p in enumerate(all_paths):
        inputs += ["-i", str(p)]
        filter_parts.append(
            f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,"
            f"pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24[v{i}];"
        )
    n = len(all_paths)
    concat_inputs = "".join(f"[v{i}][{i}:a]" for i in range(n))
    filter_complex = "".join(filter_parts) + f"{concat_inputs}concat=n={n}:v=1:a=1[vout][aout]"

    result = subprocess.run(
        ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-c:a", "aac", "-ar", "48000", "-b:a", "128k",
            str(output_path),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    print(f"  [stitch] → {output_path.name}", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UGC Street Interview Ad Generator")
    parser.add_argument("--product",    required=True,                                  help="Product/app name (e.g. 'Professor Curious')")
    parser.add_argument("--scene",      default="kota-coaching", choices=list(SCENES),  help="Scene type (default: kota-coaching)")
    parser.add_argument("--run-id",     default="run_001",                              help="Unique run identifier")
    parser.add_argument("--num-people", type=int, default=5,                            help="Number of interview clips (1-5)")
    parser.add_argument("--person-ids", nargs="*",                                      help="Specific person IDs e.g. p01 p03")
    parser.add_argument("--seconds",    type=int, default=12,                           help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",                                     help="Override output directory")
    parser.add_argument("--no-stitch",      action="store_true",                        help="Skip final ffmpeg merge")
    parser.add_argument("--vlogger-gender", default="male", choices=["male", "female"], help="Vlogger gender (default: male)")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    # Set vlogger lock globally based on gender flag
    global VLOGGER_LOCK
    VLOGGER_LOCK = VLOGGER_LOCK_FEMALE if args.vlogger_gender == "female" else VLOGGER_LOCK_MALE

    scene_cfg  = SCENES[args.scene]
    num_people = max(1, min(5, args.num_people))

    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-interview" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    pool = scene_cfg["people"]
    if args.person_ids:
        people = [p for p in pool if p["id"] in args.person_ids][:num_people]
    else:
        # Preserve narrative order — clips build a logical story (intro → features → transformation → emotion → CTA)
        people = pool[:num_people]

    total = len(people) + 2
    print(f"\n=== UGC Street Interview Ad ===")
    print(f"Product   : {args.product}")
    print(f"Scene     : {args.scene}")
    print(f"Run ID    : {args.run_id}")
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
