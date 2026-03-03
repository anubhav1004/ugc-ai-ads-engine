#!/usr/bin/env python3
"""
UGC Street Interview Ad Generator
Generates raw-footage post-exam street interview ads for any edtech product.
Clips: establishing shot + N kid interviews + outro → stitched final video.

Usage:
  python3 run.py --product "Professor Curious" --grade 10 --run-id ad_v1 --num-kids 3
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

SKILL_DIR = Path(__file__).parent.parent

# ── Kid templates (grade-specific, product name injected at runtime) ──────────

KID_TEMPLATES = {
    "general": [
        {
            "id": "k01", "gender": "boy", "age_range": "13-14",
            "emotion": "excited and happy",
            "question": "Exam kaisa gaya?",
            "response": "Bahut achha gaya bhaiya! Maine {product} use kiya tha — jo bhi doubt aata tha, scan karo, ek dum clear ho jaata tha. Paper easy laga!",
            "visual": "Kid very excited, wide eyes, animated hand gestures, backpack bouncing, smiling ear to ear.",
        },
        {
            "id": "k02", "gender": "girl", "age_range": "12-13",
            "emotion": "confident and relieved",
            "question": "Taiyari kaise ki?",
            "response": "Exam se pehle bahut doubts the... {product} use ki, usne sab clearly samjha diya. Paper mein jo bhi aaya, pehle se pata tha!",
            "visual": "Girl calm and confident, smiles and nods, adjusts bag strap, steady eye contact.",
        },
        {
            "id": "k03", "gender": "girl", "age_range": "13-14",
            "emotion": "enthusiastic and giggly",
            "question": "Koi secret bataao preparation ka!",
            "response": "Haan bhaiya! Raat ko bhi akele padhti thi — koi teacher nahi — bas {product} thi. Jo bhi samajh nahi aaya, woh bata deti thi. Bahut kaam aayi!",
            "visual": "Girl giggles first, friends giggling behind her, then speaks enthusiastically, counts on fingers.",
        },
        {
            "id": "k04", "gender": "boy", "age_range": "12-13",
            "emotion": "relieved and proud",
            "question": "Mushkil laga paper?",
            "response": "Pehle dar lag raha tha, but {product} pe raat bhar doubts clear kiye — subah tak sab ready tha. Paper mein sab aaya!",
            "visual": "Boy wipes forehead dramatically, then grins and thumbs up. Proud posture.",
        },
        {
            "id": "k05", "gender": "boy", "age_range": "11-12",
            "emotion": "shy then happy",
            "question": "Kisi app se padha kya?",
            "response": "Haan... {product}. Mummy ne bataya tha. Maine scan kiya apna question — usne simple mein samjha diya. Achha gaya exam!",
            "visual": "Boy initially shy, looks down then up, opens up with genuine smile, soft voice then confident nod.",
        },
        {
            "id": "k06", "gender": "girl", "age_range": "12-13",
            "emotion": "matter-of-fact and smart",
            "question": "Koi app use ki kya?",
            "response": "{product}. Teacher se poochne mein time lagta hai — yahan bas scan karo, turant answer. Bohot time bachaa mera!",
            "visual": "Girl composed and articulate, pushes glasses, precise hand gestures, very matter-of-fact.",
        },
        {
            "id": "k07", "gender": "boy", "age_range": "13-14",
            "emotion": "proud and confident",
            "question": "Best exam kab hua tumhara?",
            "response": "Aaj! Kyunki is baar {product} se properly prepare kiya — har concept step by step, kuch bhi miss nahi hua!",
            "visual": "Boy stands straight, very confident posture, smiles broadly, points finger upward for emphasis.",
        },
        {
            "id": "k08", "gender": "girl", "age_range": "11-12",
            "emotion": "giggly and happy",
            "question": "Secret bata do — exam easy kaise kiya?",
            "response": "{product}! Main daily use karti thi — lagta tha jaise revision chal raha ho. Aaj sab pehle se pata tha!",
            "visual": "Girl giggles covering mouth, friends also laughing, then speaks enthusiastically, bouncing on heels.",
        },
    ],
    "10": [
        {
            "id": "k01", "gender": "boy", "age_range": "15-16",
            "emotion": "relieved and proud",
            "question": "Boards kaisa gaya — Maths?",
            "response": "Bahut achha gaya! Main roz {product} pe practice karta tha — jo bhi step samajh nahi aata, turant clear ho jaata tha. Aaj sab sahi se aaya!",
            "visual": "Boy wipes forehead dramatically then huge grin. Counts on fingers. Other Class 10 students celebrating.",
        },
        {
            "id": "k02", "gender": "girl", "age_range": "15-16",
            "emotion": "confident and happy",
            "question": "Boards ki tension thi? Taiyari kaise ki?",
            "response": "Bahut tension thi — pehle boards jo hai. But {product} ne bahut help kiya. Science mein concepts the — usne ekdum clearly samjha diya. Marks pakke aane chahiye!",
            "visual": "Girl smiles warmly, pushes hair back, friends behind her giving thumbs up, school bag with keychains.",
        },
        {
            "id": "k03", "gender": "boy", "age_range": "15-16",
            "emotion": "excited and energetic",
            "question": "Boards mein itna confidence kahan se aaya?",
            "response": "{product} bhaiya! Social Science ke itne chapters the — scan karo question, ek dum clearly samjha deta hai. Raat ko bhi padhta tha. Aaj paper easy laga!",
            "visual": "Boy energetic, speaks fast, big gestures, bumps fist with friend walking past, genuine post-exam relief.",
        },
        {
            "id": "k04", "gender": "girl", "age_range": "15-16",
            "emotion": "emotional and happy",
            "question": "10th boards ke liye kitne mahine se taiyari?",
            "response": "6 mahine se bhaiya... last month {product} se padha toh bahut kuch clear hua. English grammar mein dikkat aati thi — usne simple mein explain kiya. Aaj achha gaya!",
            "visual": "Girl slightly emotional but happy, eyes bright, clasps hands, very heartfelt and genuine.",
        },
        {
            "id": "k05", "gender": "boy", "age_range": "15-16",
            "emotion": "matter-of-fact and smart",
            "question": "Koi app use ki kya boards ke liye?",
            "response": "{product}. Maths ke theorems samajh nahi aaye the school mein — uspe ek dum clear ho gaye. Teacher se baar baar poochne mein sharam aati hai — yahan akele samajh sakte ho.",
            "visual": "Boy composed and analytical, adjusts spectacles, precise gestures, confident eye contact with vlogger.",
        },
    ],
    "12": [
        {
            "id": "k01", "gender": "boy", "age_range": "17-18",
            "emotion": "deeply relieved and emotional",
            "question": "Kaisa gaya — Physics?",
            "response": "Yaar... bahut achha gaya. {product} pe roz numerical practice kiye, concepts clear kiye. Aaj paper dekha toh sab aaya. Maa ko abhi call karunga!",
            "visual": "Boy visibly emotional, eyes slightly watery, deep breath then huge smile. Voice slightly shaky with relief.",
        },
        {
            "id": "k02", "gender": "girl", "age_range": "17-18",
            "emotion": "confident and composed",
            "question": "Chemistry kaisi gayi? NEET ki bhi preparation hai?",
            "response": "Haan NEET bhi dena hai. Chemistry mein Organic bahut difficult hota hai — {product} pe topic-wise scan kiya, pattern se samjha diya. Aaj Organic mein full marks aane chahiye!",
            "visual": "Girl calm and precise, adjusts dupatta, very composed for someone who just gave 12th boards.",
        },
        {
            "id": "k03", "gender": "boy", "age_range": "17-18",
            "emotion": "exhausted but happy",
            "question": "JEE aur 12th boards saath kaise manage kiya?",
            "response": "Bhai, bahut mushkil tha. Coaching ke baad raat ko {product} pe doubts clear karta tha — koi wait nahi, turant answer milta tha. Ussi ne bachaya honestly!",
            "visual": "Boy genuinely tired, dark circles, leans against wall, backpack on ground. Very honest exhausted-student energy.",
        },
        {
            "id": "k04", "gender": "girl", "age_range": "17-18",
            "emotion": "joyful and jumping",
            "question": "Accounts ka paper kaisa gaya?",
            "response": "Accounts mein balance sheet ki entries confuse karti thi — {product} pe step by step samjha, practice kiya. Aaj sab set tha! Bahut khushi ho rahi hai!",
            "visual": "Girl overjoyed, claps hands, friends cheering. Speaks fast, points to herself proudly. Completely real joy.",
        },
        {
            "id": "k05", "gender": "boy", "age_range": "17-18",
            "emotion": "reflective and sincere",
            "question": "Boards ke liye ek cheez jo sabse zyada kaam aayi?",
            "response": "{product}. Raat 11 baje bhi doubt aata tha — koi teacher nahi hota. Woh app thi. Usne kabhi hua nahi kaha — bas samjhata raha. Maths aur Physics dono clear ho gaye.",
            "visual": "Boy reflective, slightly slower pace, genuine eye contact with vlogger. Measured, moved. Nods slowly at end.",
        },
    ],
}

ESTABLISHING_TEMPLATES = {
    "general": {
        "line":   "Bhai, aaj exams khatam hue hain — chalo seedha bacchon se poochte hain, kaisi rahi taiyari!",
        "visual": "Vlogger walks energetically toward the school gate in selfie-cam mode, points at the crowd of kids pouring out behind him, grins wide at camera, eyebrows raised.",
    },
    "10": {
        "line":   "Bhai, aaj Class 10 ke board exams khatam hue hain — chalo dekhte hain bacchon ka kya haal hai!",
        "visual": "Vlogger walks toward school gate in selfie-cam mode, points at crowd of relieved Class 10 students (15-16 years old) pouring out, grins at camera, excited and spontaneous.",
    },
    "12": {
        "line":   "Bhai, aaj Class 12 ke boards khatam hue hain — yaar, inke chehre dekho. Chalo poochte hain!",
        "visual": "Vlogger walks toward gate, gestures at older students (17-18) — some hugging, some on phones, all drained but relieved. Slightly overwhelmed by the energy around him.",
    },
}

OUTRO_TEMPLATES = {
    "general": {
        "line":   "Sunaa? Sab ek hi app ki baat kar rahe hain — {product}. Link neeche diya hai, dekh lo khud.",
        "visual": "Vlogger switches to selfie-cam, walks away from school gate, kids still streaming out behind him. Looks into camera, raises eyebrows knowingly, relaxed thumbs up, slight grin.",
    },
    "10": {
        "line":   "Sunaa? 10th boards ke baad yahi baat kar rahe hain sab — {product}. Link neeche hai.",
        "visual": "Vlogger turns selfie-cam on himself walking away. Older students behind him. Looks into camera, raises eyebrows, thumbs up with confident grin.",
    },
    "12": {
        "line":   "12th boards ke baad yahi bol rahe hain sab — {product}. Tumhara bhi college dream clear karna ho toh link neeche hai.",
        "visual": "Vlogger walks toward camera in selfie-cam mode. Older students celebrating in background. Knowing smile and slow thumbs up, slightly exhausted himself.",
    },
}

# ── Prompt builders ────────────────────────────────────────────────────────────

def setting_lock(grade: str) -> str:
    if grade == "12":
        students_desc = "older Indian students (17-18 years old) in white shirts and grey/navy trousers or salwar, some in casual clothes"
        crowd_energy  = "more intense relief — students hugging, calling parents, some emotional"
    elif grade == "10":
        students_desc = "Indian school students (15-16 years old) in white shirts and grey pants or skirts with heavy backpacks"
        crowd_energy  = "visibly happy and relieved, high energy, some celebrating"
    else:
        students_desc = "Indian school kids in white shirts and grey pants or skirts with heavy backpacks"
        crowd_energy  = "visibly happy, relieved, noisy"

    return f"""Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon natural daylight,
warm golden-hour light, slightly hazy. Outside a busy Indian school iron gate. Dozens of
{students_desc} streaming out through the gate after exams — {crowd_energy}.
Parents waiting outside, yellow auto-rickshaws and bikes parked on the street,
a chai stall visible in the far background. Organic, slightly chaotic Indian street energy.
Absolutely no color grading, no cinematic lighting, no stabilization — raw iPhone-style
handheld footage with natural subtle shake. Feels like one continuous real shoot, not staged."""


VLOGGER_LOCK = """CONTINUITY — SAME PERSON IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Wearing a navy blue
round-neck t-shirt, dark jeans. Holds a small black handheld reporter mic with
a round black foam ball top firmly in his right hand. Positioned on the left
edge of frame, visible from chest up, shot from a slightly low angle."""


def build_establishing_prompt(grade: str) -> str:
    t = ESTABLISHING_TEMPLATES.get(grade, ESTABLISHING_TEMPLATES["general"])
    return f"""{setting_lock(grade)}

{VLOGGER_LOCK}

Scene: {t['visual']}
Vlogger speaking in Hindi to camera, mouth moving expressively. Camera bobs with his walk.
Start of a street vlog interview — energetic, spontaneous, unscripted feel.
"""


def build_kid_prompt(kid: dict, grade: str, product: str) -> str:
    response = kid["response"].format(product=product)
    question = kid["question"]
    return f"""{setting_lock(grade)}

{VLOGGER_LOCK}

Scene: Vlogger holds mic toward an Indian school {kid['gender']}, age {kid['age_range']},
school uniform, heavy backpack on.

Vlogger asks in Hindi: "{question}"
Kid responds in Hindi: "{response}"

Visual action: {kid['visual']}

Kid speaking animatedly in Hindi — mouth moving, natural Indian hand gestures, expressive face.
Conversation feels genuine and unscripted. Other uniformed students walk past in background.
This is the same continuous shoot — same location, same light, same vlogger outfit.
"""


def build_outro_prompt(grade: str, product: str) -> str:
    t = OUTRO_TEMPLATES.get(grade, OUTRO_TEMPLATES["general"])
    line = t["line"].format(product=product)
    return f"""{setting_lock(grade)}

{VLOGGER_LOCK}

Scene: {t['visual']}
Vlogger speaks in Hindi to camera: "{line}"
Eyebrows raised, knowing smile, thumbs up. School gate and streaming kids visible behind.
End of street interview — same continuous shoot, same vlogger, same location.
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
    parser.add_argument("--product",    required=True,              help="Product/app name (e.g. 'Professor Curious')")
    parser.add_argument("--run-id",     default="run_001",          help="Unique run identifier")
    parser.add_argument("--grade",      choices=["10", "12"],       help="Board grade for targeted dialogue (10 or 12)")
    parser.add_argument("--num-kids",   type=int, default=3,        help="Number of kid interview clips (1-5)")
    parser.add_argument("--kid-ids",    nargs="*",                  help="Specific kid IDs to use (e.g. k01 k03)")
    parser.add_argument("--seconds",    type=int, default=8,        help="Seconds per clip (4/8/12)")
    parser.add_argument("--output-dir", default="",                 help="Override output directory")
    parser.add_argument("--no-stitch",  action="store_true",        help="Skip final ffmpeg merge")
    args = parser.parse_args()

    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

    grade    = args.grade or "general"
    num_kids = max(1, min(5, args.num_kids))

    # Output dir
    if args.output_dir:
        out_dir = Path(args.output_dir) / args.run_id
    else:
        out_dir = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-street-interview" / args.run_id

    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    # Pick kids
    pool = KID_TEMPLATES.get(grade, KID_TEMPLATES["general"])
    if args.kid_ids:
        kids = [k for k in pool if k["id"] in args.kid_ids][:num_kids]
    else:
        kids = random.sample(pool, min(num_kids, len(pool)))

    total = len(kids) + 2
    print(f"\n=== UGC Street Interview Ad ===")
    print(f"Product   : {args.product}")
    print(f"Grade     : {grade}")
    print(f"Run ID    : {args.run_id}")
    print(f"Clips     : establishing + {len(kids)} kids + outro = {total} total")
    print(f"Duration  : ~{args.seconds * total}s total")
    print(f"Output    : {out_dir}\n")

    manifest  = {"run_id": args.run_id, "product": args.product, "grade": grade, "model": MODEL, "clips": []}
    clip_paths = []

    # Establishing
    print(f"[1/{total}] Establishing shot")
    out_path = clips_dir / "clip_01_establishing.mp4"
    generate_clip(build_establishing_prompt(grade), "establishing", out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": "establishing", "file": out_path.name})

    # Kids
    for i, kid in enumerate(kids, start=2):
        print(f"[{i}/{total}] Kid: {kid['id']} ({kid['emotion']})")
        out_path = clips_dir / f"clip_{i:02d}_{kid['id']}.mp4"
        generate_clip(build_kid_prompt(kid, grade, args.product), kid["id"], out_path, args.seconds)
        clip_paths.append(out_path)
        manifest["clips"].append({"clip": kid["id"], "emotion": kid["emotion"], "file": out_path.name})

    # Outro
    print(f"[{total}/{total}] Outro")
    out_path = clips_dir / f"clip_{total:02d}_outro.mp4"
    generate_clip(build_outro_prompt(grade, args.product), "outro", out_path, args.seconds)
    clip_paths.append(out_path)
    manifest["clips"].append({"clip": "outro", "file": out_path.name})

    # Stitch
    merged_path = out_dir / f"{args.run_id}_merged.mp4"
    if not args.no_stitch:
        print("\n[stitch] Merging all clips...")
        stitch_clips(clip_paths, merged_path)
        manifest["merged"] = merged_path.name
    else:
        print("\n[stitch] Skipped.")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n[done] Final video : {merged_path}")
    print(f"[done] Manifest    : {out_dir}/manifest.json")
    print("\n=== Complete ===\n")


if __name__ == "__main__":
    main()
