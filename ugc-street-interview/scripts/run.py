#!/usr/bin/env python3
"""
UGC Street Interview Ad Generator
Generates raw-footage post-exam street interview ads for any edtech product.
Supports 6 distinct scene types, any product name, any grade.

Usage:
  python3 run.py --product "Professor Curious" --scene chai-stall --run-id chai_v1
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

# ── Vlogger lock — identical across every scene and every clip ────────────────

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Navy blue round-neck t-shirt,
dark jeans. Holds a small black handheld reporter mic with round black foam ball top
in his right hand. Visible from chest up on the left edge of frame, slightly low angle."""

# ── Scene configs ─────────────────────────────────────────────────────────────

SCENES = {

    # ── 1. School gate (default, existing) ────────────────────────────────────
    "school-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon golden-hour
light. Outside a busy Indian school iron gate. Dozens of school kids in white shirts and
grey pants/skirts with heavy backpacks streaming out after exams — happy, relieved, noisy.
Parents waiting, yellow auto-rickshaws and bikes parked, a chai stall in background.
Organic, slightly chaotic Indian street energy. Raw iPhone-style handheld footage,
no color grading, natural handheld shake. One continuous real shoot.""",
        "establishing": {
            "line":   "Bhai, aaj exams khatam hue hain — chalo seedha bacchon se poochte hain, kaisi rahi taiyari!",
            "visual": "Vlogger walks toward school gate in selfie-cam mode, points at kids pouring out, grins at camera, eyebrows raised, excited and spontaneous. Camera bobs with walk.",
        },
        "outro": {
            "line":   "Sunaa? Sab ek hi app ki baat kar rahe hain — {product}. Link neeche diya hai.",
            "visual": "Vlogger walks away from gate in selfie-cam, kids streaming out behind. Looks at camera, raises eyebrows, relaxed thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "school boy",  "age": "13-14", "emotion": "excited and happy",         "question": "Exam kaisa gaya?",                      "response": "Bahut achha gaya! {product} use kiya tha — jo bhi doubt aata tha, scan karo, ek dum clear. Paper easy laga!",              "visual": "Kid very excited, wide eyes, animated gestures, backpack bouncing, smiling ear to ear."},
            {"id": "p02", "type": "school girl", "age": "12-13", "emotion": "confident and relieved",     "question": "Taiyari kaise ki?",                     "response": "Bahut doubts the pehle... {product} use ki, sab clearly samjha diya. Jo bhi aaya paper mein, pata tha!",              "visual": "Girl calm and confident, adjusts bag strap, steady eye contact with vlogger."},
            {"id": "p03", "type": "school girl", "age": "13-14", "emotion": "enthusiastic and giggly",   "question": "Koi secret bataao!",                    "response": "Raat ko akele padhti thi — bas {product} thi. Jo samajh nahi aaya, woh bata deti thi. Bahut kaam aayi!",             "visual": "Girl giggles, friends giggling behind, then speaks enthusiastically counting on fingers."},
            {"id": "p04", "type": "school boy",  "age": "12-13", "emotion": "relieved and proud",        "question": "Mushkil laga paper?",                   "response": "Dar lag raha tha, but {product} pe raat bhar doubts clear kiye. Subah tak sab ready tha!",                           "visual": "Boy wipes forehead dramatically, then grins and gives big thumbs up."},
            {"id": "p05", "type": "school boy",  "age": "11-12", "emotion": "shy then happy",            "question": "Kisi app se padha kya?",                "response": "{product}. Mummy ne bataya tha. Question scan kiya — simply samjha diya. Achha gaya exam!",                         "visual": "Boy initially shy, looks down then opens up with genuine smile."},
        ],
    },

    # ── 2. Coaching centre gate ────────────────────────────────────────────────
    "coaching-centre": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7-8pm, streetlights
coming on. Outside a crowded JEE/NEET coaching centre building in an Indian city — could be
Kota or Old Rajender Nagar Delhi. Students in casual clothes (not uniforms) streaming out
with heavy bags, notes, textbooks. Tired, focused faces — dark circles, slightly dishevelled.
Auto-rickshaws waiting in a row outside. A few tea stalls with students standing and sipping.
Raw phone camera footage, no color grading, natural low-light noise visible. Feels like
one continuous shoot.""",
        "establishing": {
            "line":   "Bhai, coaching khatam hui abhi — yahan ke bacchon se poochte hain ki doubts kaise door karte hain!",
            "visual": "Vlogger walks toward the coaching centre exit as students stream out, turns selfie-cam to himself, gestures at the tired but driven students behind him, grins at camera.",
        },
        "outro": {
            "line":   "Raat ko coaching ke baad bhi yeh log padhte hain — aur {product} unka saath deta hai. Link neeche hai.",
            "visual": "Vlogger turns selfie-cam on himself outside coaching centre, students visible behind calling autos. Raises eyebrows, slow thumbs up, knowing look at camera.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "exhausted but determined",    "question": "Bhai, coaching ke baad bhi doubts reh jaate hain?",           "response": "Haan yaar, bahut. Teacher se class mein pooch nahi paate — {product} pe raat ko scan karo, turant clear ho jaata hai. Roz kaam aata hai.",      "visual": "Boy looks genuinely tired, dark circles, speaks earnestly, adjusts heavy bag on shoulder."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "focused and relieved",        "question": "NEET ki taiyari mein sabse bada problem kya hai?",            "response": "Biology mein itna content hai — yaad hi nahi rehta. {product} pe topic scan karo, simple mein samjha deta hai. Time bachta hai bahut!",        "visual": "Girl is composed, holds thick Biology textbook, speaks confidently, minimal gestures."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "honest and candid",           "question": "Kota mein ho kitne saal se? Adjust hua?",                    "response": "Dusra saal hai. Pehle bahut struggle tha — ab {product} se roz doubts clear karta hoon. Akela nahi lagta padhai mein.",                        "visual": "Boy leans against wall, very candid tone, speaks like talking to a friend, reflective."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "competitive and sharp",      "question": "Topper kaise bante hain — koi app use karte ho?",             "response": "{product}. Jab bhi concept pakka nahi hota — seedha wahan jaao. Baar baar samjhata hai jab tak clear na ho. Yahi edge hai mera.",             "visual": "Girl is sharp and direct, adjusts glasses, confident eye contact, precise hand gestures."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",             "question": "Aaj ka test kaisa gaya?",                                    "response": "Bahut achha! Chemistry ka ek concept kal raat {product} pe clear kiya tha — aaj wahi question aaya. Seriously kaam aaya.",                     "visual": "Boy breaks into a big smile, pumps fist slightly, relieved and proud post-test energy."},
        ],
    },

    # ── 3. Results day ────────────────────────────────────────────────────────
    "results-day": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Morning, bright natural light.
Outside a school on board exam results day. Chaotic, emotional scene — students clustered
in groups checking phones and printed result sheets, some crying with joy, some hugging
parents, some jumping. Parents in formal clothes standing anxiously. Teachers visible near
the gate. Notice boards with results visible in background. Raw iPhone-style footage,
no color grading, natural handheld shake. Electric emotional energy — most charged day
of these students' lives.""",
        "establishing": {
            "line":   "Bhai, aaj board results aaye hain — yahan ka maahaul dekho. Chalo kuch bacchon se baat karte hain!",
            "visual": "Vlogger walks into the emotional crowd in selfie-cam mode, visibly moved by the scene around him — students crying, parents hugging kids, gestures wide at the chaos behind him.",
        },
        "outro": {
            "line":   "Result ka din hai aaj — aur jo khush hain, unka ek common connection hai — {product}. Link neeche.",
            "visual": "Vlogger walks away from celebrating crowd in selfie-cam. Emotional scenes still visible behind. He looks at camera quietly, gives a thumbs up with a genuine smile.",
        },
        "people": [
            {"id": "p01", "type": "student boy",   "age": "16-17", "emotion": "overwhelmed with joy",    "question": "Bhai, kaisa result aaya?",                           "response": "95 percent aaya bhaiya! Mujhe khud yakeen nahi ho raha. {product} use kiya tha roz — sab doubt clear the. Mummy ko call karta hoon!",        "visual": "Boy is overwhelmed, eyes watery, breaks into huge smile mid-sentence, looks at phone result."},
            {"id": "p02", "type": "student girl",  "age": "15-16", "emotion": "crying happy tears",      "question": "Kya hua — khush ho ya rona ho raha hai?",            "response": "Khushi ke aansu hain bhaiya! Science mein 98 aaya. {product} ne itna help kiya — raat ko bhi padha ussi pe. Sab clear ho gaya tha.",          "visual": "Girl is crying happy tears, wipes eyes with dupatta, friends around her celebrating."},
            {"id": "p03", "type": "student boy",   "age": "16-17", "emotion": "proud and reflective",    "question": "Ek saal pehle kya sochte the result ke baare mein?",  "response": "Bahut dar tha. But {product} ne confidence diya — roz doubt scan karo, clear karo. Aaj result dekha toh sab mehnat ka fal mila.",            "visual": "Boy speaks reflectively, one hand on heart, genuine and measured emotion."},
            {"id": "p04", "type": "parent",        "age": "40-45", "emotion": "proud parent energy",     "question": "Uncle, bacche ka result kaisa aaya?",                "response": "Bahut achha aaya beta! Hum log bahut worried the — but inhone ek app use ki thi — {product} — roz padhte the. Sach mein kaam aayi.",           "visual": "Parent (father) beams with pride, arm around kid's shoulder, emotional but composed."},
            {"id": "p05", "type": "student girl",  "age": "15-16", "emotion": "relieved and grateful",   "question": "Sabse tough subject kaunsa tha aur kaise crack kiya?","response": "Maths bhaiya. Formulas yaad nahi rehte the. {product} pe baar baar practice kiya — step by step samjha. Aaj maths mein 92 aaya!",              "visual": "Girl holds result printout up proudly, grins wide, shows paper to camera."},
        ],
    },

    # ── 4. Chai stall ─────────────────────────────────────────────────────────
    "chai-stall": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening golden hour, warm
orange light. Small roadside chai stall right outside a school or coaching centre — a
wooden bench, a gas stove with a large chai pot, steam rising, glass cups on a tray.
Students in school uniforms or casual clothes sitting on benches sipping chai,
bags on the ground, books open, decompressing after a long day. Relaxed, intimate,
unguarded energy. Street noise in background — autos passing, distant chatter.
Raw phone camera footage, no color grading. Intimate and very authentic.""",
        "establishing": {
            "line":   "Bhai, school ke baad chai pi rahe hain yahan ke bacche — seedha inka mooh mitha karaate hain aur poochhte hain!",
            "visual": "Vlogger walks up to a chai stall where students are sitting, turns selfie-cam on himself, grins and points at the relaxed students behind him, steam from chai visible.",
        },
        "outro": {
            "line":   "Chai ki tarah {product} bhi sab ke saath hai — roz, har doubt pe. Link neeche.",
            "visual": "Vlogger holds a glass of chai toward camera with a grin, students visible on bench behind, then turns selfie-cam to himself walking away from the stall.",
        },
        "people": [
            {"id": "p01", "type": "school boy",  "age": "14-15", "emotion": "relaxed and candid",      "question": "Bhai, raat ko padhte waqt kya karte ho jab kuch samajh nahi aata?",   "response": "Pehle toh rota tha — phir {product} mila. Ab bas scan karo — woh samjha deta hai. Raat ko bhi koi problem nahi.",              "visual": "Boy sips chai casually, very relaxed, almost laughs at his own answer, completely unguarded."},
            {"id": "p02", "type": "school girl", "age": "14-15", "emotion": "honest and thoughtful",   "question": "Chai pi ke padhai kaisi lagti hai?",                                   "response": "Haan thoda relax ho jaata hai. Phir {product} kholo — ek dum focused ho jaata hai man. Doubts bhi jaldi clear hote hain chai ke baad!",  "visual": "Girl laughs softly, holds chai cup with both hands, thoughtful expression, looks at vlogger."},
            {"id": "p03", "type": "school boy",  "age": "15-16", "emotion": "funny and honest",        "question": "Yahan kya hua — class mein tha ya chai pe?",                          "response": "Chai pe tha bhaiya, class bhi chai se hi hoti thi. But {product} se sach mein padha. Usne clearly samjhaya — teacher se zyada kabhi kabhi!", "visual": "Boy grins cheekily, friends laugh behind him, very natural and funny energy at the stall."},
            {"id": "p04", "type": "school girl", "age": "13-14", "emotion": "sweet and sincere",       "question": "Aaj ka exam kaisa gaya — bata de!",                                   "response": "Achha gaya bhaiya! Kal raat ko {product} pe saare doubts clear kiye the — aaj sab aaya. Ab chai pi ke ghar jaungi khush hoke!",           "visual": "Girl beams happily, just came from exam, still in uniform, sips chai in celebration."},
            {"id": "p05", "type": "school boy",  "age": "14-15", "emotion": "passionate and gesturing","question": "Ek app suggest karo jo actually kaam aaye padhai mein!",               "response": "{product}! Seriously bhaiya — jo bhi samajh nahi aata, scan karo — instantly explain kar deta hai. Yahi pita hoon roz chai ke baad!",    "visual": "Boy gets animated, points finger up for emphasis, very passionate recommendation energy."},
        ],
    },

    # ── 5. College gate ────────────────────────────────────────────────────────
    "college-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon bright natural light.
Outside a busy Indian college main gate — large iron gate, college name board visible,
students in casual clothes (not uniforms) streaming out after semester exams. 18-20 year
olds, confident, fashion-conscious, in groups. Some on phones, some with earphones. College
canteen visible inside gate. Raw phone camera footage, no color grading, natural handheld
shake. Older, more confident energy than school — aspirational setting.""",
        "establishing": {
            "line":   "Bhai, college mein semester exams khatam hue — yahan ke bacche Class 12 ke baad aaye hain. Poochte hain ki 12th ki taiyari kaise ki thi!",
            "visual": "Vlogger stands outside college gate in selfie-cam mode, points at students streaming out confidently, grins at camera with raised eyebrows.",
        },
        "outro": {
            "line":   "College pahunch gaye yeh log — aur unhe yahan tak {product} ne bhi help kiya. School wale sun rahe ho? Link neeche.",
            "visual": "Vlogger walks away from college gate toward camera in selfie-cam. Confident older students visible behind. Smiles knowingly, slow thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "college boy",  "age": "18-19", "emotion": "nostalgic and proud",       "question": "Bhai, 12th boards ki taiyari kaise ki thi — college mein aane ke liye?",  "response": "Yaar, last 3 months bahut intense the. {product} use kiya tha — Physics aur Maths ke concepts raat ko clear karta tha. Ussi ne bachaya honestly.",    "visual": "Boy leans against college gate, reflective and proud tone, speaks candidly like reminiscing."},
            {"id": "p02", "type": "college girl", "age": "18-19", "emotion": "confident and articulate",  "question": "School ke baad college — kya fark laga?",                               "response": "Bahut fark hai confidence mein. 12th mein {product} se padha — har doubt seedha clear hota tha. Woh habit college mein bhi kaam aa rahi hai.",        "visual": "Girl is composed and articulate, gestures confidently, college lanyard visible."},
            {"id": "p03", "type": "college boy",  "age": "19-20", "emotion": "funny and self-aware",      "question": "School aur college mein kya fark hai padhai ka?",                        "response": "School mein {product} tha toh sab clear tha — college mein woh bhi nahi pata kya use karein! But 12th ke liye toh definitely recommend karunga.",   "visual": "Boy laughs at himself, very self-aware humor, friends laugh along behind him."},
            {"id": "p04", "type": "college girl", "age": "18-19", "emotion": "heartfelt and sincere",     "question": "Ek cheez jo sabse zyada kaam aayi 12th mein?",                          "response": "{product} app. Raat 12 baje bhi doubt aata tha — koi nahi hota — woh hoti thi. Usne kabhi nahi kaha kal poochh. Wahi fark hai.",                   "visual": "Girl speaks sincerely, places hand on heart briefly, genuine and moving answer."},
            {"id": "p05", "type": "college boy",  "age": "18-19", "emotion": "motivational energy",       "question": "Jo abhi 12th mein hain unhe kya bologe?",                              "response": "Ek kaam karo — {product} download karo. Seriously. Jo nahi samjha, seedha scan karo. Main yahan hoon kyunki ussi ne help kiya.",                   "visual": "Boy speaks directly to camera like giving advice, points at camera, very motivational energy."},
        ],
    },

    # ── 6. Parent pickup zone ──────────────────────────────────────────────────
    "parent-pickup": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon warm light.
Parent pickup zone outside a school — cars, scooters, and auto-rickshaws parked in a line,
Indian parents (mothers in sarees/salwar kameez, fathers on bikes in office clothes) waiting
anxiously. Kids in school uniforms running out to their parents — hugs, bags being handed
over, conversations starting immediately. Mix of relief and curiosity on parents' faces.
Raw phone camera footage, no color grading, natural handheld shake. Warm, emotional,
family-oriented energy.""",
        "establishing": {
            "line":   "Bhai, parents aa rahe hain bacchon ko lene — chalo unse poochte hain, bacchon ka exam kaisa gaya!",
            "visual": "Vlogger walks through the parent pickup area in selfie-cam mode, points at parents waiting with helmets and car keys, grins at camera, slightly chaotic but warm energy.",
        },
        "outro": {
            "line":   "Parents aur bacche — dono ki ek hi advice — {product}. Link neeche hai, ghar mein try karo aaj.",
            "visual": "Vlogger walks back toward camera in selfie-cam, parent-child pairs visible behind him chatting and walking. Warm smile, thumbs up, gentle nod.",
        },
        "people": [
            {"id": "p01", "type": "mother with child", "age": "35-40", "emotion": "proud and emotional",     "question": "Aunty, bacche ka exam kaisa gaya?",                      "response": "Bahut achha gaya beta! Yeh roz ek app use karte the — {product} — saare doubts wahan clear karte the. Mujhe toh pata bhi nahi tha kya hota hai uspe!",   "visual": "Mother beams with pride, child in uniform beside her, mom puts arm around child's shoulder."},
            {"id": "p02", "type": "father with child",  "age": "38-45", "emotion": "relieved and warm",      "question": "Uncle, bhai kaisa gaya paper?",                          "response": "Achha gaya bhai sahab. Hum log worried the — but inhone khud se padha, {product} se doubts clear kiye. Aajkal ke bacche samajhdaar hain!",              "visual": "Father claps son on the back proudly, son grins shyly, warm father-son moment."},
            {"id": "p03", "type": "school girl",        "age": "12-13", "emotion": "running to mom excited", "question": "Arre, mummy ko kya bataya result ka?",                  "response": "Mummy ko bola bahut achha gaya! {product} se raat ko sab prepare kiya tha. Ab mummy khush hain — ice cream milegi shayad!",                             "visual": "Girl runs up to mom mid-interview, both laugh, kid is in full post-exam excitement."},
            {"id": "p04", "type": "mother with child", "age": "38-42", "emotion": "curious and grateful",   "question": "Ghar mein kaise taiyari karaate hain bacchon ko?",        "response": "Yeh khud se padhte hain ab — {product} app use karte hain. Main kuch nahi karti — bas yeh app hai jo sab samjha deta hai. Bahut achha hai.",            "visual": "Mother speaks genuinely, child tugs at her hand impatiently, she laughs and continues."},
            {"id": "p05", "type": "father with child",  "age": "40-45", "emotion": "matter-of-fact proud",  "question": "Aap bacchon ki padhai mein help karte ho?",              "response": "Main toh engineer hoon — Maths aata hai. But Science aur Hindi mein {product} se hi padhte hain yeh. Main bhi kabhi kabhi dekh leta hoon — achha hai.",  "visual": "Father is matter-of-fact, slightly amused, son looks up at him proudly, real family dynamic."},
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
Camera bobs naturally. Start of a candid street vlog interview — energetic, unscripted.
"""

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: Vlogger extends mic toward {person['type']}, age {person['age']}.

Vlogger asks in Hindi: "{person['question']}"
Person responds in Hindi: "{response}"

Visual action: {person['visual']}

Person speaking animatedly in Hindi — natural Indian hand gestures, expressive face,
authentic unscripted energy. Feels like a real candid moment, not staged.
Same continuous shoot — same location, same light, same vlogger.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera: "{line}"
Knowing smile, thumbs up, eyebrows raised. End of street interview — same shoot, same vlogger.
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
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output_path)],
        capture_output=True, text=True,
    )
    list_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[:500]}")
    print(f"  [stitch] → {output_path.name}", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UGC Street Interview Ad Generator")
    parser.add_argument("--product",    required=True,                                  help="Product/app name (e.g. 'Professor Curious')")
    parser.add_argument("--scene",      default="school-gate", choices=list(SCENES),    help="Scene type (default: school-gate)")
    parser.add_argument("--run-id",     default="run_001",                              help="Unique run identifier")
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
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-interview" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    pool = scene_cfg["people"]
    if args.person_ids:
        people = [p for p in pool if p["id"] in args.person_ids][:num_people]
    else:
        people = random.sample(pool, min(num_people, len(pool)))

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
