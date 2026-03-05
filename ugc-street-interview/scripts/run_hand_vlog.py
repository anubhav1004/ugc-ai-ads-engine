#!/usr/bin/env python3
"""
UGC Hand-Vlog Street Interview Ad Generator
Same emotional Kota interview format as run.py — but the vlogger is NEVER shown.
Only the vlogger's hand (holding a mic) is visible, extending from the left edge of frame.
This solves character consistency across clips since no face/body needs to match.

Usage:
  python3 run_hand_vlog.py --product "Professor Curious" --scene kota-coaching --run-id hand_v1
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
#
# This replaces the full VLOGGER_LOCK from run.py.
# By showing only the hand, Sora does not need to maintain a consistent face
# or build across clips — only the hand grip and mic need to be consistent.

HAND_LOCK = """CRITICAL VISUAL RULE — NO VLOGGER FACE OR BODY VISIBLE:
The vlogger is NEVER shown. No face, no torso, no silhouette.
The ONLY vlogger element in frame: a single hand (medium-brown skin, bare wrist, plain grip)
extending from the BOTTOM-LEFT edge of frame, holding a small black handheld reporter mic
with a round black foam ball top, pointing up toward the interview subject.
The hand enters from the left side at roughly mid-height, partially in frame.
This is the only visual cue a vlogger is present. Never break this rule.
Camera is held by an unseen operator — it frames the subject, not the vlogger."""

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
            "line":   "Bhai, Kota mein hoon abhi — coaching se nikal rahe hain yeh log. Inse poochte hain, kya chal raha hai andar se.",
            "visual": "Camera frames the coaching centre gate — silent, burdened students streaming out in the evening light. The vlogger's mic hand dips briefly into the bottom-left of frame. No vlogger face. Just the gate, the crowd, the weight of Kota. Vlogger speaks to camera in voiceover — empathetic, not entertained.",
        },
        "outro": {
            "line":   "Kota mein laakhon bacche hain — akele, thake hue, maar khate hain andar se. {product} unka ek saathi ban gaya hai. Link neeche hai.",
            "visual": "Camera slowly pans the coaching gate as last students trickle out into the dark street. Mic hand visible at bottom-left. No vlogger face. Quiet, heavy atmosphere. Voice speaks slowly — not a pitch, a truth.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "broken then hopeful",
             "question": "Bhai, sach bata — Kota mein kaisa lag raha hai?",
             "response": "Ghar se 700 kilometre dur hoon. Raat ko rota hoon akele mein — kuch samajh nahi aata, aur kisi ko bata bhi nahi sakta. Phir Professor Curious mila. Ek ek doubt uthaya usne — ruk gaya, samjhaya, choda nahi. Woh raat se neend aayi.",
             "visual": "Camera frames the boy from chest up — coaching gate behind him. Mic hand extends from bottom-left into frame toward him. Boy's jaw tightens, eyes glassy — holds back tears. Then at 'Professor Curious' his face softens completely. Says the name clearly, deliberately."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "exhausted then determined",
             "question": "Doctor banna hai — but aaj kaisi hai halat?",
             "response": "Maa ne gold becha tha mujhe Kota bhejna ke liye. Yeh soch ke raat ko uthke ro leti hoon. Lekin Professor Curious pe Biology padhti hoon — woh itna clearly samjhata hai ki lagta hai main kar sakti hoon. Yeh app meri wajah se nahi ruka kabhi.",
             "visual": "Camera faces the girl against the coaching centre wall. Mic hand visible from bottom-left pointing toward her. Voice breaks slightly mentioning her mother. She pauses, wipes the corner of her eye. Says 'Professor Curious' with full composure — a quiet strength."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw and candid",
             "question": "Kabhi laga ki chod ke chale jao?",
             "response": "Haaan yaar. Ek raat bag pack kar liya tha. Phir kuch nahi socha, Professor Curious khola, Physics ka ek chapter finish kiya. Subah tak woh bag wahan pada tha aur main padh raha tha. Woh app meri wajah nahi jaanta — lekin usne roka mujhe.",
             "visual": "Camera frames the boy — he laughs softly but there's pain behind it. Mic hand from bottom-left. Totally candid, no performance. Looks away briefly. When he says 'Professor Curious' he looks straight at the camera — grounded, grateful."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "fierce and emotional",
             "question": "Competition itna hai — tum kaise khud ko alag karti ho?",
             "response": "Roz 5 baje uthti hoon. Roz ek cheez toot ti hai andar se — rank, doubt, loneliness. Phir Professor Curious pe woh doubt solve karti hoon step by step. Woh har baar samjhata hai jab tak clear na ho jaaye. Yeh app nahi chodti main.",
             "visual": "Camera faces the girl — fierce, jaw set, eyes sharp. Mic hand from bottom-left of frame. Voice steady but emotion underneath. Says 'Professor Curious' like a fighter names their weapon — not emotional, but fierce."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",
             "question": "Aaj ka mock test kaisa gaya?",
             "response": "Pichle 3 din se ek concept tha — samajh nahi aa raha tha. Raat ko Professor Curious pe khola — 2 ghante laga ke seedha clear kar diya. Aaj wahi question aaya test mein. Aaj pehli baar laga — haan, yahan rehna sahi tha.",
             "visual": "Camera frames the boy — exhales deeply, real unperformed relief, eyes slightly wet. Mic hand from bottom-left. Says 'Professor Curious' with a slow nod. First genuine smile of the clip."},
        ],
    },

    # ── 2. School gate ────────────────────────────────────────────────────────
    "school-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon golden-hour
light. Outside a busy Indian school iron gate in Kota. Dozens of school kids in white shirts and
grey pants/skirts with heavy backpacks streaming out after exams — some happy, some anxious, noisy.
Parents waiting, yellow auto-rickshaws and bikes parked, a chai stall in background.
Organic, slightly chaotic energy. Raw iPhone-style handheld footage,
no color grading, natural handheld shake. One continuous real shoot.""",
        "establishing": {
            "line":   "Bhai, aaj exams khatam hue hain Kota mein — chalo seedha bacchon se poochte hain, kaisi rahi taiyari!",
            "visual": "Camera frames the school gate as kids pour out with heavy bags in golden-hour light. Vlogger mic hand briefly visible at bottom-left. No face. Just the gate, the kids, the noise. Voice is energetic, curious, spontaneous.",
        },
        "outro": {
            "line":   "Sunaa? Sab ek hi app ki baat kar rahe hain — Professor Curious. Link neeche diya hai.",
            "visual": "Camera frames the gate from outside — kids streaming past. Mic hand dips into bottom-left corner briefly. Warm afternoon light. Voice is relaxed, eyebrows-raised in audio tone.",
        },
        "people": [
            {"id": "p01", "type": "school boy",  "age": "13-14", "emotion": "relieved and emotional",
             "question": "Exam ke pehle dar lag raha tha?",
             "response": "Bahut dar tha bhaiya — raat ko so nahi pa raha tha, ek ek formula bhool raha tha. Phir Professor Curious pe sab clear kiya — woh samjhata hai, judge nahi karta. Aaj paper mein sab aaya. Sach mein aaya.",
             "visual": "Camera faces the kid chest-up — school gate behind. Mic hand from bottom-left. Kid's eyes go wide remembering the fear. Then visibly softens at 'Professor Curious' — says the name clearly, proudly. Relief is real."},
            {"id": "p02", "type": "school girl", "age": "12-13", "emotion": "sincere and moved",
             "question": "Ghar mein koi padhata hai kya?",
             "response": "Nahi bhaiya, Papa kaam pe hote hain raat tak. Main akeli padh ti thi — bahut mushkil tha. Phir Professor Curious use karna shuru kiya. Woh meri saari confusions door karta tha — koi bhi time pe. Main ab akeli nahi hoon padhte waqt.",
             "visual": "Camera faces the girl — quiet, sincere. Mic hand from bottom-left. Slightly teary at 'akeli.' At 'Professor Curious' she straightens — says the name clearly with a small proud smile."},
            {"id": "p03", "type": "school boy",  "age": "13-14", "emotion": "funny then sincere",
             "question": "Koi app use kiya kya — sach bata!",
             "response": "Bhaiya seedha bolunga — pehle kuch nahi karta tha, bas rota tha. Phir dost ne Professor Curious bataya. Usne ek dum simple mein samjhaya — roz use karta hoon. Aaj bahut achha gaya.",
             "visual": "Camera faces the boy — grins at first, then gets genuine. Mic hand from bottom-left. Says 'Professor Curious' looking straight at camera — slow and clear, like he wants everyone watching to remember the name."},
            {"id": "p04", "type": "school girl", "age": "13-14", "emotion": "proud and emotional",
             "question": "Mummy ko kya bologe result ka?",
             "response": "Main bolungi — Mummy, tumne jo expect kiya tha woh karke aayi hoon. Raat ko Professor Curious pe padha tha — woh samjhata tha jab koi nahi hota. Aaj sab aaya paper mein. Yehi toh chahiye tha.",
             "visual": "Camera faces the girl. Mic hand from bottom-left. Voice catches slightly at 'Mummy.' She composes herself. Says 'Professor Curious' deliberately, loud enough — like she's rehearsing telling her mother."},
            {"id": "p05", "type": "school boy",  "age": "11-12", "emotion": "shy then proud",
             "question": "Kisi app se padha kya — batao na!",
             "response": "Haan... Professor Curious. Mummy ne install kiya tha. Main bahut confuse rehta tha Maths mein — woh baar baar samjhata tha, gaali nahi deta tha... haha. Ab Maths achha lagta hai.",
             "visual": "Camera faces the boy — initially shy, looks down. Mic hand from bottom-left. Then says 'Professor Curious' clearly — small giggle at his own joke, then a real, warm smile. Completely genuine."},
        ],
    },

    # ── 3. Coaching centre ──────────────────────────────────────────────────────
    "coaching-centre": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7-8pm, streetlights
coming on. Outside a crowded JEE/NEET coaching centre building in Kota, Rajasthan. Students in
casual clothes (not uniforms) streaming out with heavy bags, notes, textbooks. Tired, focused
faces — dark circles, slightly dishevelled. Auto-rickshaws waiting in a row outside.
A few tea stalls with students standing and sipping in silence. Raw phone camera footage,
no color grading, natural low-light noise visible. The weight of Kota hangs in the air.""",
        "establishing": {
            "line":   "Kota mein hoon — coaching khatam hui. Yahan ke bacchon se poochte hain ki raat ko kya hota hai jab koi nahi hota.",
            "visual": "Camera frames the coaching centre exit — silent, burdened students trickling out under yellow streetlights. Mic hand at bottom-left of frame. No vlogger face. Empathetic voice in narration.",
        },
        "outro": {
            "line":   "Raat ko coaching ke baad bhi yeh log akele ladte hain apni padhai se — aur Professor Curious unka saathi hai. Link neeche.",
            "visual": "Camera frames students silently calling autos in the dark street outside coaching. Mic hand briefly at bottom-left. Slow, quiet voiceover.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "broken then hopeful",
             "question": "Coaching mein kitne ghante padhte ho — aur phir bhi kya hota hai?",
             "response": "12-14 ghante roz. Phir bhi raat ko teacher ka concept dimag mein nahi rehta — class mein poochh nahi paate, hazaar bacche hain. Bahut akela lagta hai. Professor Curious pe woh concepts raat ko clear karta hoon — woh rukta hai mere saath tab tak jab tak samajh na aa jaaye.",
             "visual": "Camera faces the boy — genuinely exhausted. Mic hand from bottom-left. Voice drops at 'akela.' Rallies at 'Professor Curious' — says it clearly, deliberately. Quiet resolve returns."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "focused and emotional",
             "question": "NEET clear karna hai — lekin aaj kaisi feel ho rahi hai?",
             "response": "Aaj mock mein fail hua. Ghar phone kiya — unhe bata nahi sakti kitni problem ho rahi hai, woh pehle se itna kar rahe hain mere liye. Phir Professor Curious pe Biology ka ek chapter khola — woh itna clearly samjhata hai. Raat tak confidence wapas aa gaya tha.",
             "visual": "Camera faces the girl. Mic hand from bottom-left. Voice tightens at 'ghar phone kiya.' A beat of real vulnerability. At 'Professor Curious' she steadies — looks straight at camera, says the name slowly, clearly."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw honesty",
             "question": "Kota mein kitna mushkil hai — sach mein?",
             "response": "Bahut mushkil hai bhai. Log yahan rank ke liye jeete hain — roz toot te hain. Ek raat itna bura laga ki kuch nahi karna tha. Phir Professor Curious khola, ek problem solve ki, phir ek aur — subah ho gayi thi. Woh app nahi jaanta — but usne raat nikaali meri.",
             "visual": "Camera faces the boy — looks away for a second, raw, no performance. Mic hand from bottom-left. Says 'Professor Curious' quietly but clearly. Then nods once — that's the whole truth."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "fierce",
             "question": "Topper kaisi banti ho yahan — koi secret?",
             "response": "Koi secret nahi — bas yeh ki main roti hoon, phir uthti hoon. Jo samajh nahi aata — Professor Curious pe jaati hoon. Woh tab tak samjhata hai jab tak clear na ho. Baar baar. Kabhi nahi kehta kal poochh. Yahi edge hai mera.",
             "visual": "Camera faces the girl — fierce, minimal emotion but the weight is present. Mic hand from bottom-left. Says 'Professor Curious' like naming a trusted ally — clear, loud, owns it completely."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",
             "question": "Aaj ka test kaisa gaya?",
             "response": "Chemistry ka ek concept tha — 3 din se samajh nahi aa raha tha. Raat ko Professor Curious pe 2 ghante baitha. Step by step — ruka, samjhaya. Aaj wahi question aaya. Pehli baar is saal achha feel hua Kota mein.",
             "visual": "Camera faces the boy — exhales slowly, real relief, eyes a little wet. Mic hand from bottom-left. Says 'Professor Curious' with a slow nod, completely sincere. First genuine smile in the clip."},
        ],
    },

    # ── 4. Results day ─────────────────────────────────────────────────────────
    "results-day": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Morning, bright natural light.
Outside a school in Kota on board exam results day. Chaotic, emotional scene — students clustered
in groups checking phones and printed result sheets, some crying with joy, some hugging
parents, some jumping. Parents in formal clothes standing anxiously. Teachers near the gate.
Notice boards with results visible in background. Raw iPhone-style footage,
no color grading, natural handheld shake. The most charged day of these students' lives.""",
        "establishing": {
            "line":   "Bhai, aaj board results aaye hain Kota mein — yahan ka maahaul dekho. Chalo kuch bacchon se baat karte hain!",
            "visual": "Camera pans across the emotional scene outside school — students crying, parents hugging, results in hands. Mic hand briefly visible at bottom-left. No vlogger face. Just the raw energy of results day in Kota.",
        },
        "outro": {
            "line":   "Result ka din hai aaj — aur jo khush hain, unka ek common connection hai — Professor Curious. Link neeche.",
            "visual": "Camera frames celebrating students and emotional parents outside school. Mic hand at bottom-left. Quiet, moved voiceover. A genuine thumbs up sound in voice tone.",
        },
        "people": [
            {"id": "p01", "type": "student boy",   "age": "16-17", "emotion": "overwhelmed with joy",
             "question": "Bhai, kaisa result aaya?",
             "response": "95 percent... mujhe yakeen nahi ho raha. Papa ne government job chodi thi ek baar mujhe padhaane ke liye. Aaj unhe call karta hoon. Professor Curious pe roz padhta tha — raat ko jo samajh nahi aata, woh samjha deta tha. Yahi result hai unka bhi.",
             "visual": "Camera faces the boy — overwhelmed, jaw trembles briefly, eyes wet. Mic hand from bottom-left. Mid-sentence he composes himself. Says 'Professor Curious' slowly, clearly — naming it like giving credit. Then breaks into a full smile."},
            {"id": "p02", "type": "student girl",  "age": "15-16", "emotion": "crying happy tears",
             "question": "Kya hua — khush ho ya rona ho raha hai?",
             "response": "Dono bhaiya — Science mein 98 aaya. Maa kehti thi 'beta kuch nahi hoga tere se' — not taunting, she was scared. Main bhi dara hua tha. Professor Curious ne raat ko mujhe hath tham liya jab koi nahi tha. Aaj ka result unka bhi hai.",
             "visual": "Camera faces the girl crying openly, wipes eyes. Mic hand from bottom-left. Voice breaks at 'Maa.' Then says 'Professor Curious' clearly through tears — name comes out strong. Friends around her crying too."},
            {"id": "p03", "type": "student boy",   "age": "16-17", "emotion": "proud and reflective",
             "question": "Ek saal pehle kya sochte the?",
             "response": "Sochta tha fail ho jaunga. Coaching ka pressure, ghar ki umeed — sab ek saath. Ek raat bilkul toot gaya tha. Phir Professor Curious pe ek chapter khola — aur phir ek aur. Woh raat khatam nahi hui bhi tab tak jab tak sab clear nahi hua. Woh app meri wajah se nahi thaka.",
             "visual": "Camera faces the boy — speaks quietly, one hand on heart. Mic hand from bottom-left. Looks away briefly remembering. Says 'Professor Curious' deliberately — looking at camera, slow and clear. Real gratitude."},
            {"id": "p04", "type": "parent",        "age": "40-45", "emotion": "proud, emotional parent",
             "question": "Uncle, bacche ka result kaisa aaya?",
             "response": "Bahut achha aaya beta. Main raat ko dekh ta tha — light on rehti thi kamre mein. Ek app se padhta tha — Professor Curious. Maine kabhi nahi rokey — jo concentrate kar raha tha toh hona chahiye. Aaj woh mehnat ka phal mila.",
             "visual": "Camera faces the father — arm around child's shoulder, eyes glisten. Mic hand from bottom-left. Says 'Professor Curious' carefully — like he memorized the name. Proud, composed, deeply moved."},
            {"id": "p05", "type": "student girl",  "age": "15-16", "emotion": "relieved and grateful",
             "question": "Sabse tough subject kaunsa tha aur kaise crack kiya?",
             "response": "Maths bhaiya — formulas bhool jaati thi exam pressure mein. Raat ko bahut roti thi. Professor Curious pe step by step practice kiya — woh samjhata tha, daanta nahi. Aaj Maths mein 92 aaya. Woh app nahi hoti toh yeh din nahi hota.",
             "visual": "Camera faces the girl — holds result printout up, voice shakes briefly. Mic hand from bottom-left. Says 'Professor Curious' firmly — like she's speaking to everyone still struggling. Then smiles, shows paper to camera."},
        ],
    },

    # ── 5. Chai stall ──────────────────────────────────────────────────────────
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
            "visual": "Camera frames the chai stall — students sitting in tired silence on benches, steam rising from chai pot. Mic hand briefly at bottom-left of frame. No vlogger face. Just the stall, the exhaustion, the warmth.",
        },
        "outro": {
            "line":   "Chai ki tarah Professor Curious bhi sab ke saath hai — roz, har raat, har doubt pe. Link neeche.",
            "visual": "Camera frames a glass of chai on the stall counter, students in background on the bench. Mic hand dips briefly into bottom-left. Quiet, warm voiceover.",
        },
        "people": [
            {"id": "p01", "type": "student boy",  "age": "14-15", "emotion": "exhausted and candid",
             "question": "Raat ko padhai karte waqt kya hota hai jab kuch samajh nahi aata?",
             "response": "Bhaiya sach bolunga — ek baar phone uthaya tha ghar call karne ko. Phir rakha diya — unhe pareshan nahi karna tha. Professor Curious khola uss raat. Woh samjhata raha — 2 baje tak. Socha tha quit karunga. Woh raat nahi ki.",
             "visual": "Camera faces the boy — sips chai, totally drained. Mic hand from bottom-left. Voice very quiet at 'ghar call karne ko.' Says 'Professor Curious' simply — not dramatic, just true. Stares into chai cup."},
            {"id": "p02", "type": "student girl", "age": "14-15", "emotion": "honest and raw",
             "question": "Kota mein akela feel hota hai kya?",
             "response": "Bahut. Ghar mein maa hoti thi — doubt hota toh pooch leti thi. Yahan koi nahi. Raat ko Professor Curious khola — woh samjhata hai, judge nahi karta, thakta nahi. Chai peene ke baad wahi pehli cheez kholti hoon. Woh maa ki jagah nahi le sakta — but kuch toh hai.",
             "visual": "Camera faces the girl — voice catches at 'maa.' She looks at her chai cup for a moment. Mic hand from bottom-left. Then says 'Professor Curious' clearly, steadily — not performing grief, just honest. A real, human moment."},
            {"id": "p03", "type": "student boy",  "age": "15-16", "emotion": "dark humor, then real",
             "question": "Kota mein sabse mushkil kya hai?",
             "response": "Apne aap se fight karna bhaiya. Sab se zyada yahi thakata hai. Raat ko Professor Curious se jhagada karta hoon — matlab doubts deta hoon, woh jawab deta hai. Kabhi kabhi sochta hoon woh mujhse better teacher hai than anyone I've paid fees for.",
             "visual": "Camera faces the boy — grins tiredly, dark humor but real underneath. Mic hand from bottom-left. Says 'Professor Curious' with a slight laugh that turns genuine. Points at camera — that's the truth."},
            {"id": "p04", "type": "student girl", "age": "13-14", "emotion": "sweet and vulnerable",
             "question": "Aaj ka exam kaisa gaya — sach mein bata.",
             "response": "Raat bhar roti rahi — soch rahi thi fail ho jaungi. Professor Curious pe ek ek chapter cover kiya. Subah uthke exam diya. Achha gaya bhaiya. Ab chai pi rahi hoon — pehli baar chain se.",
             "visual": "Camera faces the girl — exhales slowly, holds her chai with both hands like it's comfort. Mic hand from bottom-left. Says 'Professor Curious' quietly but clearly — peace visible on her face. First calm moment in a long time."},
            {"id": "p05", "type": "student boy",  "age": "14-15", "emotion": "passionate and grateful",
             "question": "Ek cheez recommend karo jo sach mein kaam aayi Kota mein.",
             "response": "Professor Curious. Bhaiya seedha bolunga — yeh app nahi hoti toh main yahan nahi hota abhi. Jo samajh nahi aata, scan karo — woh samjhata hai tab tak jab tak clear na ho. Kota mein yahi chahiye hota hai — koi jo chode na.",
             "visual": "Camera faces the boy — puts chai cup down, points at camera, completely earnest. Mic hand from bottom-left. Says 'Professor Curious' slowly and clearly, almost spelling it out. Full eye contact. No performance — pure sincerity."},
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
            "visual": "Camera frames college gate — confident students streaming out in afternoon light. Mic hand briefly at bottom-left. No vlogger face. Serious, empathetic audio tone.",
        },
        "outro": {
            "line":   "College pahunch gaye yeh log — Kota se lad ke. Professor Curious unka ek saathi tha. School wale sun rahe ho? Link neeche.",
            "visual": "Camera frames confident older students walking away from the college gate. Mic hand briefly at bottom-left. Slow, meaningful voiceover.",
        },
        "people": [
            {"id": "p01", "type": "college boy",  "age": "18-19", "emotion": "nostalgic and honest",
             "question": "Kota survive kiya — kaise?",
             "response": "Ek raat itna bura laga tha ki bag pack kar liya tha. Seriously. Phir Professor Curious pe Physics ka ek chapter khola — aur subah ho gayi. Yahan hoon aaj usi wajah se. Woh app jaanta nahi mujhe — but woh wahan tha uss raat.",
             "visual": "Camera faces the boy leaning against college gate — reflective. Mic hand from bottom-left. Voice goes quiet at 'bag pack kar liya.' Says 'Professor Curious' slowly, deliberately — like he wants anyone still in Kota to hear it clearly."},
            {"id": "p02", "type": "college girl", "age": "18-19", "emotion": "composed and sincere",
             "question": "Kota ke baad college — kya fark laga?",
             "response": "Confidence aaya. Kota mein roz tootha tha — roz Professor Curious pe uth ta tha. Woh app ne sikhaya ki toot ke bhi padhte rehte hain. Yahi habit college mein bhi kaam aa rahi hai. Wo app meri foundation hai.",
             "visual": "Camera faces the girl — composed but emotion present underneath. Mic hand from bottom-left. Says 'Professor Curious' with quiet pride — like naming something that shaped her. Steady eye contact."},
            {"id": "p03", "type": "college boy",  "age": "19-20", "emotion": "self-aware and real",
             "question": "Kota mein kya bachaya tumhe?",
             "response": "Seedha bolunga — Professor Curious. Raat 1 baje bhi kholta tha woh app. Woh kabhi band nahi hua, kabhi slow nahi hua. Jab sab thak jaate hain — teacher, friends — woh nahi thaka. Yahan hoon toh usi ki wajah se hoon.",
             "visual": "Camera faces the boy — candid, no bravado. Mic hand from bottom-left. Says 'Professor Curious' looking straight at camera — slowly, loudly. Not a testimonial, a fact."},
            {"id": "p04", "type": "college girl", "age": "18-19", "emotion": "heartfelt",
             "question": "Ek cheez jo sabse zyada kaam aayi Kota mein?",
             "response": "Professor Curious app. Raat 12 baje bhi doubt aata tha — koi nahi hota. Teacher so gaye, dost so gaye — woh hoti thi. Usne kabhi nahi bola kal poochh. Kabhi nahi. Yahi fark hai.",
             "visual": "Camera faces the girl — places hand on heart briefly. Mic hand from bottom-left. Says 'Professor Curious' clearly, loudly — like she wants it heard. Genuine and moving."},
            {"id": "p05", "type": "college boy",  "age": "18-19", "emotion": "direct, motivational",
             "question": "Jo abhi Kota mein hain unhe kya bologe?",
             "response": "Ek kaam karo — Professor Curious download karo. Abhi. Kota mein akela feel ho raha hai — woh wahan hai. Raat ko doubt hai — woh wahan hai. Main yahan hoon kyunki woh wahan tha jab main nahi tha.",
             "visual": "Camera faces the boy — speaks directly to camera, points finger — urgent and caring. Mic hand from bottom-left. Says 'Professor Curious' twice — slowly and clearly both times. Means every word."},
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
            "visual": "Camera frames the parent pickup area — waiting parents with helmets and car keys, kids streaming out. Mic hand briefly at bottom-left. No vlogger face. Warm, empathetic audio tone.",
        },
        "outro": {
            "line":   "Parents aur bacche — dono ki ek hi baat — Professor Curious. Link neeche hai, ghar mein try karo aaj.",
            "visual": "Camera frames parent-child pairs reuniting outside school — some emotional, some joyful. Mic hand at bottom-left. Warm, gentle voiceover.",
        },
        "people": [
            {"id": "p01", "type": "mother with child", "age": "35-40", "emotion": "proud and tearful",
             "question": "Aunty, bacche ka exam kaisa gaya?",
             "response": "Bahut achha gaya beta. Main har raat sochti thi — Kota mein akela hai, koi nahi hoga saath. Phir dekha tha — raat ko ek app use karta tha — Professor Curious — sab doubts wahan clear karta tha. Tab main ne chain li. App ne mere bacche ko akela nahi chhoda.",
             "visual": "Camera faces the mother — eyes fill. She squeezes child's shoulder. Mic hand from bottom-left. Says 'Professor Curious' slowly — like she memorized it to tell others. Raw, real parental relief."},
            {"id": "p02", "type": "father with child",  "age": "38-45", "emotion": "quiet pride",
             "question": "Uncle, Kota mein chhodna mushkil lagta hai bacche ko?",
             "response": "Bahut mushkil tha pehli baar. Ghar jaate waqt rota tha main — woh nahi, main. Phir usne bataya — Professor Curious pe padhta hoon, sab clear ho jaata hai. Tab se chinta kum hui. Woh app ne mera kaam kiya.",
             "visual": "Camera faces the father — still for a moment, the admission he cried is quiet and real. Mic hand from bottom-left. Says 'Professor Curious' with a nod — matter-of-fact, loaded with meaning. Son looks up at him."},
            {"id": "p03", "type": "school girl",        "age": "12-13", "emotion": "running to mom, emotional",
             "question": "Arre, mummy ko kya bataya result ka?",
             "response": "Mummy — bahut achha gaya! Raat bhar Professor Curious pe padha tha — woh samjha ta tha sab kuch. Aaj sab aaya! Ab ice cream do please!",
             "visual": "Camera faces the girl — runs to mom, grabs her arm, completely lit up. Mic hand from bottom-left. Says 'Professor Curious' fast and clear — owning it, then immediately back to being a happy kid asking for ice cream."},
            {"id": "p04", "type": "mother with child", "age": "38-42", "emotion": "grateful and honest",
             "question": "Ghar se Kota — kab chain milti hai aapko?",
             "response": "Jab yeh raat ko padh raha hota hai — Professor Curious pe. Main call karti hoon toh kehta hai 'Maa main theek hoon, padh raha hoon.' Tab chain aati hai. Woh app ne mujhe bhi sambhala iss saal.",
             "visual": "Camera faces the mother — laughs softly but eyes are glassy. Mic hand from bottom-left. Says 'Professor Curious' clearly, warmly — like it's a family friend. Child tugs at her hand, she laughs and looks at camera."},
            {"id": "p05", "type": "father with child",  "age": "40-45", "emotion": "real and direct",
             "question": "Aap bacchon ki padhai mein help karte ho?",
             "response": "Main engineer hoon — Maths karta hoon. But Kota mein itna competition hai — main nahi kar sakta itna. Professor Curious karta hai. Yeh wahan padhta hai — raat ko, akele — aur woh samjhata hai. Mujhe se zyada patience hai uss app mein.",
             "visual": "Camera faces the father — dry and honest, almost funny but real. Mic hand from bottom-left. Says 'Professor Curious' seriously, clearly. Son looks up at him with a grin. An earned, true endorsement."},
        ],
    },

}

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: {e['visual']}
Vlogger speaking in Hindi as voiceover (not seen): "{e['line']}"
Camera bobs naturally — handheld, organic. Start of a candid street vlog interview.
The only vlogger presence: voice and briefly the mic hand at the bottom-left edge.
"""

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: Camera frames {person['type']}, age {person['age']}.
The vlogger's hand extends a mic from the bottom-left edge of frame toward the person.
No vlogger face or body is visible — only the mic hand.

Vlogger asks in Hindi (voice only, not on camera): "{person['question']}"
Person responds in Hindi: "{response}"

Visual action: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first 3-4 seconds): Raw emotional problem — the struggle, the loneliness, the fear.
Person's face carries real weight. No solution yet. Let the pain breathe.
Act 2 (next 3-4 seconds): "{product}" is the turning point. The name is spoken clearly,
deliberately, out loud — not mumbled. A visible shift in the person's face and energy.
The name "{product}" must be unmistakably audible and visible as a spoken word.

Person speaking animatedly in Hindi — natural Indian hand gestures, expressive face,
authentic unscripted emotion. Feels like a real candid moment, not staged.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{HAND_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi as voiceover (not seen): "{line}"
Genuine conviction — not a pitch, a truth. End of street interview.
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
    parser = argparse.ArgumentParser(description="UGC Hand-Vlog Street Interview Ad Generator")
    parser.add_argument("--product",    required=True,                                  help="Product/app name")
    parser.add_argument("--scene",      default="kota-coaching", choices=list(SCENES),  help="Scene type (default: kota-coaching)")
    parser.add_argument("--run-id",     default="hand_001",                             help="Unique run identifier")
    parser.add_argument("--num-people", type=int, default=3,                            help="Number of interview clips (1-5)")
    parser.add_argument("--person-ids", nargs="*",                                      help="Specific person IDs e.g. p01 p03")
    parser.add_argument("--seconds",    type=int, default=8,                            help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",                                     help="Override output directory")
    parser.add_argument("--no-stitch",  action="store_true",                            help="Skip final ffmpeg merge")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    scene_cfg  = SCENES[args.scene]
    num_people = max(1, min(5, args.num_people))

    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-hand-vlog" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    pool = scene_cfg["people"]
    if args.person_ids:
        people = [p for p in pool if p["id"] in args.person_ids][:num_people]
    else:
        people = random.sample(pool, min(num_people, len(pool)))

    total = len(people) + 2
    print(f"\n=== UGC Hand-Vlog Street Interview ===")
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
