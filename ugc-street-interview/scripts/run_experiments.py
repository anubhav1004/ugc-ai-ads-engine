#!/usr/bin/env python3
"""
5 Experimental UGC Ads — Professor Curious
Each ad is built around a different Kota moment with a scroll-stopping hook.

Runs all 5 sequentially, stitches each, sends to Slack automatically.

Experiments:
  1. ek-raat      — 11:30pm, one student alone outside coaching
  2. bag-pack     — Student at Kota station, bag packed, about to quit
  3. rank-wala    — AIR 89 topper cornered outside coaching
  4. pehla-din    — First day in Kota, parents just left
  5. mock-result  — Mock test results just dropped, raw real-time emotions

Usage:
  source ~/.env_azure
  python3 run_experiments.py
"""

import json
import os
import requests
import subprocess
import sys
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY   = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT  = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL     = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL  = f"{ENDPOINT}/openai/v1"
HEADERS   = {"api-key": API_KEY}

SLACK_URL    = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"

PRODUCT     = "Professor Curious"
SECONDS     = 8
OUTPUT_ROOT = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-experiments"
APP_OUTRO   = Path(__file__).parent.parent.parent / "assets" / "app_outro_india.MP4"

# ── Vlogger lock ──────────────────────────────────────────────────────────────

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Navy blue round-neck t-shirt,
dark jeans. Holds a small black handheld reporter mic with round black foam ball top
in his right hand. Visible from chest up on the left edge of frame, slightly low angle."""

# ── 5 Experimental Scenes ─────────────────────────────────────────────────────

EXPERIMENTS = [

    # ── 1. EK RAAT — 11:30pm, one student alone outside coaching ──────────────
    {
        "id":     "ek-raat",
        "run_id": "exp_01_ek_raat",
        "label":  "Ek Raat (Late Night Outside Coaching)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. 11:30pm, Kota.
Dark street outside a shuttered coaching centre — only a single tube light flickering above
the entrance. One student sits alone on the stone steps, head in hands, phone face-down beside
him. Absolute silence except for distant traffic and crickets. The weight of a hundred sleepless
nights is in every frame. Raw phone camera footage, natural grain in low light,
no color grading. Intimate, unsettling, deeply human.""",
            "establishing": {
                "line":   "Raat ke saade gyarah baj rahe hain. Coaching band ho gayi. Sab so gaye. Yeh akela bahar baitha hai. Main poochhunga kya hua.",
                "visual": """Vlogger walks slowly toward the lone student sitting on dark steps — phone in selfie cam,
barely any light. He turns camera briefly to show the empty dark street, then back to himself.
Whispers to camera — not performing, genuinely unsure what he'll find.
Approaches the student quietly. The tube light flickers above them.""",
            },
            "outro": {
                "line":   "Raat ke saade gyarah baje. Kota mein aisa hi hota hai. Professor Curious unke saath tha. Link neeche.",
                "visual": """Vlogger stands alone outside the dark coaching building, student now gone inside.
Looks at camera quietly in the dark. No big gesture — just a slow, deliberate nod.
The empty steps behind him say everything.""",
            },
            "people": [
                {
                    "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                    "emotion": "breaking down then finding resolve",
                    "question": "Bhai, raat ko bahar kyun baitha hai?",
                    "response": "Aaj mock mein 38 percentile aaya. 6 mahine ho gaye Kota mein. Ghar phone kiya — Papa ne bola 'theek hai, koshish karo.' Nahi bol paaya kuch. Bahar aa gaya. Phir Professor Curious khola — pata nahi kyun. Woh ruka mere saath. Raat bhar. Kal fir padhna hai.",
                    "visual": """Boy looks up slowly when vlogger approaches — eyes red but dry now, past crying.
Speaks in a low, flat voice for the first 3-4 seconds — zero performance, completely spent.
At 'Professor Curious khola' his jaw tightens — not happy, just resolute.
Says the name clearly, eyes steady. The kind of quiet that comes after a real decision.""",
                },
                {
                    "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                    "emotion": "confessing then composed",
                    "question": "Itni raat ko yahan kya kar rahi ho?",
                    "response": "Maa ka call aaya tha — 'kaisi ho?' Boli 'theek hoon.' Nahi thi. Andar jaake rona nahi chahti thi — roommate so rahi thi. Bahar aa gayi. Professor Curious pe Biology ka ek chapter khola. 2 ghante baad kuch clear hua. Tab andar gayi. Tab neend aayi.",
                    "visual": """Girl is sitting sideways on steps, hugging her knees. Doesn't look at vlogger immediately.
First 3-4 seconds — voice very quiet, confessional. The 'Nahi thi' lands like a stone.
At 'Professor Curious' she straightens slightly — not energized, just steadied.
Says the name once, clearly. That's enough.""",
                },
                {
                    "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                    "emotion": "fierce and hollow-eyed",
                    "question": "Rank kya hai abhi?",
                    "response": "3,847. Chahiye 500. 8 mahine baaki hain. Roz raat ko yahan baithta hoon jab sab so jaate hain — Professor Curious pe weak topics cover karta hoon. Kaafi ghante lagte hain. Lekin yahi ek cheez hai jo samjhata hai jab koi nahi hota. Chhorna nahi hai.",
                    "visual": """Boy stares at his phone screen — rank visible. Looks up at vlogger with hollow eyes.
Speaks slowly, each number landing — '3,847... chahiye 500.' Real math of Kota dreams.
At 'Professor Curious' he taps his phone — it's open right now. He's mid-session.
Completely matter-of-fact. No drama. Just the work.""",
                },
            ],
        },
    },

    # ── 2. BAG PACK — Kota station, bag packed, about to quit ─────────────────
    {
        "id":     "bag-pack",
        "run_id": "exp_02_bag_pack",
        "label":  "Bag Pack (Almost Quit Kota)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, harsh flat light.
Outside Kota Junction railway station — a student sits on a platform bench with a large packed
suitcase beside them, looking at a train ticket on their phone. Other students with bags visible
in background — some arriving, some leaving. The station has seen a thousand Kota goodbyes.
Raw phone camera footage, no color grading, station noise — announcements, wheels on platform.
The suitcase says everything before a word is spoken.""",
            "establishing": {
                "line":   "Kota Junction. Yeh student yahan bag pack karke baitha hai. Train 2 ghante mein hai. Kuch hua hai. Baat karte hain.",
                "visual": """Vlogger walks into the station and spots the student with packed suitcase — turns selfie-cam
to himself first, raises one eyebrow at camera, no words for a second. Then approaches.
The suitcase is prominently visible. Station PA in the background.""",
            },
            "outro": {
                "line":   "Woh train nahi pakdi. Professor Curious ki wajah se. Link neeche.",
                "visual": """Vlogger stands on empty platform, the student's bench now vacant — they went back.
Platform announcement in background. He looks at camera quietly, pockets one hand.
Half-smile. Slow thumbs up. Lets the empty bench tell the story.""",
            },
            "people": [
                {
                    "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                    "emotion": "raw confession — decided to stay",
                    "question": "Bag pack kiya hai — ja rahe ho?",
                    "response": "Ja raha tha. Ticket bhi book ki thi. Phir raat ko Professor Curious pe ek problem kholi — pata nahi kyun. Phir ek aur. Subah tak bag wahan pada tha, main pad raha tha. Train nikal gayi. Ticket cancel karna padega.",
                    "visual": """Boy holds up his phone — cancelled ticket visible for a second.
First half: flat, exhausted, 'Ja raha tha' with zero drama. He really was leaving.
At 'Professor Curious pe ek problem kholi' he pauses — even he doesn't fully understand why.
'Train nikal gayi' comes with a soft, disbelieving exhale. He stayed. He doesn't regret it.""",
                },
                {
                    "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                    "emotion": "matter-of-fact — third time staying",
                    "question": "Kya hua — ja rahi ho ya ruk rahi ho?",
                    "response": "Ruk rahi hoon. Teesri baar. Teeno baar jaane ki sochi. Teeno baar Professor Curious ki ek raat ne roka. Main jaanti hoon yeh strange lagta hai — ek app ne roka. But jab raat ko woh samjhata hai aur lagne lagta hai 'haan kar sakti hoon' — tab ticket cancel ho jaata hai apne aap.",
                    "visual": """Girl is completely matter-of-fact — 'teesri baar' is just a fact, not drama.
She's almost amused at herself. But the emotion is real underneath.
Says 'Professor Curious' directly, clearly — owns it without embarrassment.
The 'ticket cancel ho jaata hai apne aap' line is delivered with a quiet, knowing smile.""",
                },
                {
                    "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                    "emotion": "arriving back — came home and returned to Kota",
                    "question": "Aa rahe ho ya ja rahe ho?",
                    "response": "Wapas aa raha hoon. Ghar gaya tha — ek hafte ke liye. Wahan baith ke Professor Curious pe padha. Ghar mein zyada peaceful tha. Lekin 7 din baad laga — nahi, Kota mein rehna padega. Yahan competition hai. Wahi chahiye. Wapas aa gaya.",
                    "visual": """Boy is arriving — suitcase wheeling behind him, slightly sweaty from travel.
Different energy from the others — not broken, recalibrated.
'Wapas aa raha hoon' is said with a decisive nod.
Says 'Professor Curious pe padha' as a natural detail — it's just what he does now.""",
                },
            ],
        },
    },

    # ── 3. RANK WALA — The topper cornered outside coaching ───────────────────
    {
        "id":     "rank-wala",
        "run_id": "exp_03_rank_wala",
        "label":  "Rank Wala (The Topper's Secret)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon, golden light.
Outside a Kota JEE coaching centre, just after a batch ends. A student walks out and other
students start congratulating them — backslaps, phones out taking photos. A small crowd forms.
They just got AIR 89 in a mock test — everyone knows. Vlogger spots the commotion and moves in.
Raw phone camera footage, natural handheld shake, the buzz of student energy around one person.""",
            "establishing": {
                "line":   "Yeh wahi ladka hai jisne is coaching ka highest mock rank laaya hai is mahine — AIR 89. Sabka yahan role model hai. Bhai, 2 minute milenge?",
                "visual": """Vlogger pushes gently through the small crowd forming around the topper — selfie cam on himself
first showing the commotion, then he breaks through. The topper is surprised to be mic'd.
Vlogger points at the student excitedly to camera — 'yeh wahi hai' energy.
Other students visibly curious — some lean in to hear.""",
            },
            "outro": {
                "line":   "AIR 89. Professor Curious. Ab tum decide karo. Link neeche hai.",
                "visual": """Vlogger walks away from the dispersing crowd in selfie-cam. The topper visible behind
being congratulated again. Vlogger shakes head slowly at camera — like he can't believe
how simple the answer was. One raised eyebrow. Slow thumbs up.""",
            },
            "people": [
                {
                    "id": "p01", "type": "JEE topper boy", "age": "18-19",
                    "emotion": "humble and direct — no mystique",
                    "question": "Bhai, AIR 89 — kya kiya tune? Seedha bata.",
                    "response": "Seedha bolunga — Professor Curious. Roz ek ghanta. Consistent. Koi shortcut nahi. Jab bhi koi concept pakka nahi tha — wahan jaata tha, tab tak jab tak crystal clear na ho jaaye. Log sochte hain kuch magic hai — nahi hai. Bas yahi hai.",
                    "visual": """Boy is completely unassuming — still processing the congratulations, slightly uncomfortable with attention.
'Professor Curious' comes out immediately, no build-up. He's clearly said this before.
Speaks matter-of-factly — 'Bas yahi hai' while others crowd around him.
The contrast between the crowd's excitement and his calm delivery is everything.""",
                },
                {
                    "id": "p02", "type": "topper's roommate", "age": "18-19",
                    "emotion": "proud and revealing",
                    "question": "Tu iska roommate hai — andar se kya hota tha?",
                    "response": "Main raat ko so jaata tha, yeh Professor Curious pe rehta tha. 2 baje, 3 baje. Subah uthta toh bhi on hota phone. Main socha tha yeh pagal ho gaya. Aaj AIR 89 aaya. Ab main pagal hoon kyunki maine follow nahi kiya.",
                    "visual": """Roommate is grinning but there's real regret underneath. Points at his friend being congratulated.
'Professor Curious pe rehta tha' delivered like he's narrating something he witnessed.
The '2 baje, 3 baje' is specific — he saw this.
Last line 'ab main pagal hoon' gets a real laugh from people nearby — but he means it.""",
                },
                {
                    "id": "p03", "type": "junior aspirant girl", "age": "17-18",
                    "emotion": "aspirational and decided",
                    "question": "Yeh tujhe inspire karta hai?",
                    "response": "Bahut. Inhone bataya tha ek baar — Professor Curious use karo, consistently. Tab se roz use karti hoon. 3 mahine pehle mera rank 4,200 tha. Abhi 1,800 hai. Inhi ki wajah se aur Professor Curious ki wajah se. Yahan aana hai mujhe.",
                    "visual": """Girl looks at the topper with clear admiration — not starry-eyed, determined.
Points at herself when she gives her rank improvement — it's her work, her proof.
Says 'Professor Curious' firmly, associating it with the topper and herself equally.
End with a resolute nod toward the topper — 'yahan aana hai mujhe.' She will.""",
                },
            ],
        },
    },

    # ── 4. PEHLA DIN — First day in Kota, parents just left ──────────────────
    {
        "id":     "pehla-din",
        "run_id": "exp_04_pehla_din",
        "label":  "Pehla Din (First Day in Kota)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Morning, bright nervous light.
Kota — student housing area near coaching centres, the morning of admission day. Students
arriving with large suitcases and parents — some families just saying goodbye at the gate,
some parents helping carry bags up stairs. A mix of determination and barely-held-together
emotion. Parents trying to be strong. Students trying not to cry. Raw phone camera footage,
no color grading. The most vulnerable day in a Kota student's life.""",
            "establishing": {
                "line":   "Yeh log aaj Kota aaye hain. Pehla din hai. Parents abhi drop karke ja rahe hain. Yeh woh moment hai jo har Kota student yaad rakhta hai. Chalo baat karte hain.",
                "visual": """Vlogger stands outside a student hostel entrance, families visible coming and going.
Speaks softly to camera — this isn't a fun vlog moment, he gets it.
A parent is seen hugging their child in the blurred background.
Vlogger takes a breath and walks toward a student whose parents just drove off.""",
            },
            "outro": {
                "line":   "Pehle din. Akele. Professor Curious unke saath tha. Aur woh yahan hain. Link neeche.",
                "visual": """Vlogger stands outside the hostel in late afternoon light — same spot as establishing shot.
The street is quieter now, parents gone. Students visible at windows.
He looks at camera seriously. 'Aur woh yahan hain' — they stayed, they survived, they're here.
Simple thumbs up. Walks away slowly.""",
            },
            "people": [
                {
                    "id": "p01", "type": "boy — parents just left 10 minutes ago", "age": "17-18",
                    "emotion": "barely holding it together",
                    "question": "Pehla din hai — kaisa lag raha hai?",
                    "response": "Papa abhi gaye hain. 10 minute pehle. Bahut accha lag raha tha jab woh the — ab nahi. Dost ne phone pe bataya tha — Professor Curious install karna sabse pehle. Install kar liya. Kuch toh hai mere paas abhi. Yahi pakad ke baithta hoon aaj raat.",
                    "visual": """Boy's eyes are glassy — he's holding it. Voice is controlled but barely.
'Papa abhi gaye hain. 10 minute pehle.' — raw and quiet. The specificity of '10 minute' is real.
When he says 'Professor Curious install kar liya' he holds up his phone — it's installed.
'Yahi pakad ke baithta hoon' — the app is his anchor tonight. Says the name clearly.""",
                },
                {
                    "id": "p02", "type": "father — just dropped daughter off", "age": "42-45",
                    "emotion": "proud parent who is also breaking",
                    "question": "Uncle, beti ko chhodke ja rahe ho?",
                    "response": "Haan. Jaana padega. Beti ne phone pe dikhaaya tha — Professor Curious — kehti hai 'Papa isse padhunga, tum fikar mat karo.' Main engineer hoon — dekha, achha hai. Tab kuch chain aayi. Ab jaata hoon. Woh tayaar hai. Main bhi hoon.",
                    "visual": """Father is at the gate, car keys in hand — one foot out the door.
'Haan. Jaana padega.' is said with the weight of every parent who ever left their child in Kota.
His face when he says 'Professor Curious' — genuine trust, an engineer who evaluated the app.
'Tab kuch chain aayi' is a father giving himself permission to leave. Eyes slightly wet.""",
                },
                {
                    "id": "p03", "type": "girl — arrived alone, no parents", "age": "17-18",
                    "emotion": "quietly fierce from the start",
                    "question": "Akele aayi ho?",
                    "response": "Haan. Papa ki tabiyat theek nahi hai — woh aa nahi sake. Main khud aayi. Bag khud uthaayi. Ek cheez jo zaroor saath aayi — Professor Curious pehle se install hai phone mein. Jab koi nahi hoga — woh hoga. Bas itna kaafi hai mujhe.",
                    "visual": """Girl is standing with her own large suitcase — no one else in frame.
'Haan' is immediate, no self-pity. This is her choice, her trip, her Kota.
'Professor Curious pehle se install hai' — she planned this. The app was the first thing she packed.
The final line 'bas itna kaafi hai mujhe' is said looking straight at the camera. It is enough.""",
                },
            ],
        },
    },

    # ── 5. MOCK RESULT — Results just dropped, raw real-time emotions ──────────
    {
        "id":     "mock-result",
        "run_id": "exp_05_mock_result",
        "label":  "Mock Result (Results Just Dropped)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, harsh white light.
Outside a Kota coaching centre — mock test results just released on the app 5 minutes ago.
Students streaming out, glued to phones. Some faces lit up, some collapsed. One girl is
crying quietly in a corner. Two boys are jumping. One student sits on the ground, staring.
The full spectrum of human emotion compressed into one parking lot.
Raw phone camera footage, no color grading, natural chaos.""",
            "establishing": {
                "line":   "Mock test results abhi abhi aaye hain — 5 minute pehle. Bahar khade hain sab. Kuch ke chehere khil rahe hain. Kuch ke gir rahe hain. Seedha baat karte hain.",
                "visual": """Vlogger walks out with the students, selfie-cam on himself — eyes wide, taking in the scene.
Pans camera quickly to show the range — students jumping, one sitting on ground, phones everywhere.
Turns back to himself. 'Yeh moment hai.' Goes to find someone to talk to. Urgent energy.""",
            },
            "outro": {
                "line":   "Mock test ka din. Sab kuch real ho jaata hai. Aur jo roz Professor Curious pe padhte hain — unhe pata hota hai kal kya karna hai. Link neeche.",
                "visual": """Vlogger stands in the now-thinning parking lot. Some students still on phones behind him.
Speaks quietly — this wasn't entertainment, this was real life.
'Unhe pata hota hai kal kya karna hai' — the line of someone who's seen this work.
Slow, genuine thumbs up. No performance.""",
            },
            "people": [
                {
                    "id": "p01", "type": "boy — rank dropped badly", "age": "17-18",
                    "emotion": "devastated but not quitting",
                    "question": "Bhai, result dekha — kya aaya?",
                    "response": "19 percentile. Pichle mahine 34 tha. Gir gaya. Par main rota nahi yahan pe. Abhi ghar jaata hoon, Professor Curious pe baithta hoon — kaunse topic mein gira, wahan se dobara karta hoon. Yahi toh Kota hai. Girna, uthna, aur fir padh na.",
                    "visual": """Boy shows his phone — the number is visible. Doesn't hide it.
First 3-4 seconds: face tight, jaw set — processing the drop. No tears, no performance.
At 'Professor Curious pe baithta hoon' he puts the phone in his pocket — decided.
'Girna, uthna, aur fir padhna' is said looking straight at camera. This is Kota. He knows it.""",
                },
                {
                    "id": "p02", "type": "girl — massive rank jump", "age": "17-18",
                    "emotion": "stunned and emotional",
                    "question": "Khushi ke aansu hain ya kuch aur?",
                    "response": "Khushi ke. 3 mahine pehle 41 percentile tha mera. Aaj 91. Ek cheez badla maine — roz raat Professor Curious pe consistent padha. Sirf yahi. Maa ko call karti hoon — woh yeh din dekhna chahti thi. Unhe batana hai.",
                    "visual": """Girl is wiping eyes — genuinely overwhelmed, not performing.
'41 percentile... aaj 91' — the gap lands. She knew this moment was possible, still can't believe it.
Says 'Professor Curious' with wet eyes but a steady voice — gives it full credit, clearly.
Immediately pulls out phone to call her mom — the call is more important than the camera.""",
                },
                {
                    "id": "p03", "type": "boy — stayed flat, assessing", "age": "18-19",
                    "emotion": "calm and analytical",
                    "question": "Tera result — kaisa hai?",
                    "response": "76 percentile. Same as last month. Nahi badha. But main jaanta hoon kyun — is month Professor Curious pe consistent nahi raha. Kuch din chhodha. Wahi dikh raha hai result mein. Agle mahine consistency rakhni hai. Data bahut honest hota hai.",
                    "visual": """Boy is completely calm — this is data to him, not emotion.
'76 percentile. Same as last month. Nahi badha.' delivered with flat analytical honesty.
When he names Professor Curious as the variable — he says it like a scientist naming a factor.
'Data bahut honest hota hai' — the most Kota sentence ever said. Looks at vlogger directly.""",
                },
            ],
        },
    },

]

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {e['visual']}
Vlogger speaking in Hindi to camera: "{e['line']}"

HOOK REQUIREMENT: The first 2 seconds must make it impossible to scroll away.
The visual and the vlogger's tone must create immediate curiosity or emotional pull.
Raw, unscripted — not a produced ad. Real Kota energy.
"""

def build_person_prompt(person: dict, scene: dict) -> str:
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: Vlogger approaches {person['type']}, age {person['age']}.

Vlogger asks in Hindi: "{person['question']}"
Person responds in Hindi: "{person['response']}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first 3-4 seconds): Raw emotional truth — the struggle, the number, the moment.
Let it breathe. No solution yet. The audience must feel the weight before the release.
Act 2 (next 3-4 seconds): "{PRODUCT}" — the name spoken clearly, deliberately, out loud.
A visible shift in the person's face and energy. The name must be unmistakably audible.

Authentic Hindi dialogue, real Indian body language. Feels like a real moment, not a scene.
Same Kota location, same light, same vlogger throughout.
"""

def build_outro_prompt(scene: dict) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera: "{o['line']}"

Not a pitch. A conclusion. The vlogger has seen something real today.
The name "{PRODUCT}" is the answer — understated, earned, final.
"""

# ── Azure Sora API ─────────────────────────────────────────────────────────────

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
        progress = data.get("progress", 0)
        print(f"    [poll] {clip_id} {status} {progress}%", flush=True)
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
    all_paths = list(clip_paths)
    if APP_OUTRO.exists():
        all_paths.append(APP_OUTRO)
        print(f"    [outro]  Appending app outro", flush=True)
    else:
        print(f"    [outro]  Warning: app outro not found at {APP_OUTRO}", flush=True)

    inputs = []
    filter_parts = []
    for i, p in enumerate(all_paths):
        inputs += ["-i", str(p)]
        filter_parts.append(
            f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,"
            f"pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24[v{i}];"
        )
    n = len(all_paths)
    concat_v = "".join(f"[v{i}]" for i in range(n))
    concat_a = "".join(f"[{i}:a]" for i in range(n))
    filter_complex = "".join(filter_parts) + f"{concat_v}{concat_a}concat=n={n}:v=1:a=1[vout][aout]"

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
    print(f"    [stitch] → {output_path.name}", flush=True)

def send_to_slack(video_path: Path, label: str, exp_id: str) -> None:
    print(f"    [slack] Sending {video_path.name} ...", flush=True)
    with open(video_path, "rb") as f:
        resp = requests.post(
            SLACK_URL,
            data={"channel_id": SLACK_CHANNEL},
            files={"file": (video_path.name, f, "video/mp4")},
        )
    extra = requests.post(
        SLACK_URL,
        data={
            "channel_id": SLACK_CHANNEL,
            "text": f"🎬 *{label}* (`{exp_id}`)\nProduct: {PRODUCT} | Scene: Kota | {SECONDS}s × 5 clips = ~40s",
        },
    )
    if resp.ok:
        print(f"    [slack] ✓ Sent", flush=True)
    else:
        print(f"    [slack] ✗ Failed: {resp.text[:200]}", flush=True)

# ── Run one experiment ─────────────────────────────────────────────────────────

def run_experiment(exp: dict) -> None:
    scene    = exp["scene"]
    run_id   = exp["run_id"]
    label    = exp["label"]
    people   = scene["people"]
    total    = len(people) + 2

    out_dir   = OUTPUT_ROOT / run_id
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", flush=True)
    print(f"  {label}", flush=True)
    print(f"  Run ID : {run_id}", flush=True)
    print(f"  Clips  : {total} total  |  Output: {out_dir}", flush=True)
    print(f"{'='*60}", flush=True)

    clip_paths = []

    # Establishing
    print(f"\n  [1/{total}] Establishing — HOOK SHOT", flush=True)
    out = clips_dir / "clip_01_establishing.mp4"
    generate_clip(build_establishing_prompt(scene), "establishing", out)
    clip_paths.append(out)

    # Interviews
    for i, person in enumerate(people, start=2):
        print(f"\n  [{i}/{total}] {person['type']} ({person['emotion']})", flush=True)
        out = clips_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_clip(build_person_prompt(person, scene), person["id"], out)
        clip_paths.append(out)

    # Outro
    print(f"\n  [{total}/{total}] Outro", flush=True)
    out = clips_dir / f"clip_{total:02d}_outro.mp4"
    generate_clip(build_outro_prompt(scene), "outro", out)
    clip_paths.append(out)

    # Stitch
    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} clips ...", flush=True)
    stitch_clips(clip_paths, merged)

    # Slack
    send_to_slack(merged, label, exp["id"])

    print(f"\n  ✓ DONE: {merged}\n", flush=True)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    print(f"\n{'#'*60}")
    print(f"  UGC Experiments — Professor Curious")
    print(f"  5 ads × 5 clips × {SECONDS}s = ~40s each")
    print(f"  Each auto-sends to Slack on completion")
    print(f"{'#'*60}\n")

    for i, exp in enumerate(EXPERIMENTS, 1):
        print(f"\n[Experiment {i}/5] {exp['label']}", flush=True)
        try:
            run_experiment(exp)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)
            continue

    print(f"\n{'#'*60}")
    print(f"  All 5 experiments complete. Check Slack.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
