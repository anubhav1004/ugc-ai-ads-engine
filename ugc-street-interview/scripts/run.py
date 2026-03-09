#!/usr/bin/env python3
"""
UGC Street Interview Ad Generator — VIRAL VERSION
Kota Factory-energy dialogues. Scroll-stopping hooks. 92% mute-optimised.
New vlogger: linen shirt, lav mic, AirPods. Modern Indian creator aesthetic.

Usage:
  python3 run.py --product "Professor Curious" --scene kota-coaching --run-id kota_v2
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

# ── Vlogger lock — VIRAL VERSION ──────────────────────────────────────────────

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP:
Young Indian male, late 20s, lean build, medium-brown skin. Short black hair, slightly
tousled — not salon-neat, not messy. Clean-shaven. Wearing an oversized off-white linen
shirt worn open over a plain white fitted tee. Relaxed dark chinos. Clean white sneakers.
A small wireless clip-on lavalier mic clipped to his shirt collar — NOT a foam-ball
reporter mic. One AirPod dangling casually from his left ear. Thin silver ring on his
right hand. He looks like a real 5M-subscriber Indian creator — authentic, not a TV anchor.

FACE RULE — CRITICAL:
- Establishing shot ONLY: vlogger face visible in selfie-cam mode.
- ALL interview clips: vlogger face is NOT shown. Only a hand holding a small
  wireless clip-on lav mic extended from the LEFT edge of frame toward the subject.
  The mic is small, modern, black — barely visible. The subject fills 80% of frame.
  Vlogger is off-camera. His voice is heard but his face is never shown again.
- Outro: vlogger face returns briefly."""

# ── VIRAL HOOK RULE (baked into every establishing prompt) ────────────────────

HOOK_RULE = """VIRAL HOOK — FIRST 2 SECONDS (NON-NEGOTIABLE):
92% of viewers watch on MUTE. The VISUAL in the first 2 seconds must make them stop.
DO NOT open with the vlogger walking toward camera. That is not a hook.
The first frame must show something unexpected, emotional, or unresolved —
a face, a number, a suitcase, a hand gesture, an overheard moment.
The viewer must think "wait, what is happening here?" before a single word is spoken."""

# ── Scene configs — VIRAL VERSION ─────────────────────────────────────────────

SCENES = {

    # ── 1. Kota coaching centre gate (DEFAULT) ─────────────────────────────────
    "kota-coaching": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7:30pm, Kota.
Outside the exit gate of a JEE/NEET coaching centre — the kind of place where 1.5 lakh
dreams live in 12 square kilometres. Students in casual clothes pouring out — heavy bags,
thick marked-up notes, hollow eyes with dark circles. No one is smiling. Auto-rickshaws
wait in a patient line. A chai stall with no seats left. The air feels compressed — you
can feel the weight of every parent's sacrifice in every face that walks past.
Raw phone camera footage, flat colours no LUT, natural low-light grain. Real Kota.""",

        "establishing": {
            "line":   "Yeh woh jagah hai... jahan India ke sabse bade sapne rehte hain. Aur sabse zyada toot te hain. Main seedha inse poochhne wala hoon.",
            "visual": """HOOK — first 2 seconds: CLOSE-UP on a student's hands clutching a marked-up notebook,
knuckles slightly white. Camera holds for 1 full second — no talking, just that image.
Then vlogger voice comes in quietly. Camera slowly pulls back to reveal vlogger already
standing at the coaching gate, students streaming past him like water around a stone.
He doesn't look at the students excitedly. He looks at the camera — serious, like a
documentary filmmaker who just witnessed something. He points slowly at the crowd behind
him. No grin. No hype. Just the weight of the place.""",
        },

        "outro": {
            "line":   "Kota mein laakhon bacche hain — akele, raat ko, koi nahi hota. Professor Curious unka woh saathi hai jo kabhi nahi jaata. Link neeche hai.",
            "visual": """Vlogger stands alone outside the now-empty coaching gate, streetlight behind him.
Students have dispersed. He looks directly at camera — no performance, no thumbs up gimmick.
Just a long pause, then a slow deliberate nod. Eyes slightly wet — he means it.
Says the name 'Professor Curious' like he witnessed something today that earned that mention.""",
        },

        "people": [
            {
                "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                "emotion": "hollow — past crying, into resolve",
                "question": "Bhai... andar se kaisa chal raha hai? Sach mein.",
                "response": "47 mock diye hain. 47. Ek bhi 70 percentile nahi gayi. Papa ne apni ghadi bech di thi mujhe yahan bhejna ke liye — 1998 wali. Woh baat nahi karte usski. Main karta hoon. Raat ko Professor Curious kholta hoon — woh ruk jaata hai mere saath. Jab tak samajh nahi aata. Kabhi nahi bola 'kal aao'. Yahi ek cheez hai jo main le ke jaaunga Kota se.",
                "visual": """Boy is not performing sadness — he's past that. Eyes dry but hollow.
'47' comes out flat, like a number he's memorised. '1998 wali ghadi' — voice drops here,
one single beat of real emotion, then he pulls it back immediately.
At 'Professor Curious' he taps his phone in his pocket — it's there right now.
Says the name slowly, clearly, like it's the one honest thing in a dishonest year.""",
            },
            {
                "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                "emotion": "fierce and fractured",
                "question": "Doctor banna hai — ghar mein kya hua iss ke liye?",
                "response": "Maa ne mangalsutra rakh diya tha. Woh nahi bataati — mujhe pata chala baad mein. Main yeh soch ke raat ko uth jaati hoon. Phir Professor Curious pe Biology kholti hoon. Raat 2 baje bhi. Woh samjhata hai — baar baar, bina thake. Main nahi haar sakti. Woh mangalsutra waapis laana hai mujhe.",
                "visual": """Girl's jaw is set — fierce, not sad. She's turned the grief into fuel.
'Mangalsutra rakh diya' — she says it factually, but her eyes go somewhere else for one beat.
Then snaps back. At 'Professor Curious' she's completely present — says the name clearly,
chin up. The last line 'waapis laana hai' is not for the camera. It's her own reminder.""",
            },
            {
                "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                "emotion": "dark humour hiding real pain",
                "question": "Kabhi laga ki sab chod ke chale jao?",
                "response": "Haan. Ek raat bag pack bhi kar liya tha. Station tak bhi gaya. Phir train miss ho gayi — literally. Platform number galat tha. Wapas aaya. Kamre mein baitha. Pata nahi kyun Professor Curious khola. Ek problem solve ki. Phir ek aur. Subah ho gayi. Woh galat platform shayad sahi tha.",
                "visual": """Boy grins at 'train miss ho gayi' — not performed, genuinely darkly funny to him now.
The grin fades immediately at 'pata nahi kyun Professor Curious khola' — he doesn't know why either.
That uncertainty is real. Says the name clearly looking slightly away — not at camera, not at vlogger.
The last line 'shayad sahi tha' lands quietly. He half-smiles. Looks at camera.""",
            },
            {
                "id": "p04", "type": "father — just dropped son off", "age": "42-46",
                "emotion": "quiet devastation he's trying to hide",
                "question": "Uncle, bacche ko chhodke jaate waqt... kaisa lagta hai?",
                "response": "Main car mein baithke rota hoon. Woh nahi dekh ta. Main rukta hoon thodi der bahar — phir jaata hoon. Iss baar usne bataya — Professor Curious pe padhta hoon raat ko, sab clear ho jaata hai. Tab kuch... tab thoda chain aaya. Tab gaya. Woh app ne mujhe bhi kuch diya.",
                "visual": """Father speaks quietly, looking slightly away from camera — this isn't easy to say.
'Main car mein baithke rota hoon' — said flatly, matter-of-factly, which makes it devastating.
At 'Professor Curious' something visibly shifts in his face — not happiness, but relief.
'Woh app ne mujhe bhi kuch diya' — he means it. He looks at camera briefly. Looks away again.""",
            },
            {
                "id": "p05", "type": "NEET aspirant girl", "age": "17-18",
                "emotion": "composed — she's made peace with Kota",
                "question": "Tum thakti nahi kya — roz yahi sab?",
                "response": "Thakaana band kar diya hai. Roz ek kaam karta hoon — raat ko Professor Curious pe ek topic. Sirf ek. Khatam karo, soo jao. Subah phir. Kota mein survive karna hai toh system banana padta hai. Woh app mera system hai.",
                "visual": """Girl is calm — not numb, just organised. No dramatic emotion here, which is its own kind of power.
Speaks in short, clean sentences — Kota has stripped everything extra away.
Says 'Professor Curious' like she's naming a piece of equipment she trusts completely.
'Woh app mera system hai' — looks straight at camera. No smile needed. It's just true.""",
            },
        ],
    },

    # ── 2. School gate ────────────────────────────────────────────────────────
    "school-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon, Kota.
Outside a government school iron gate — post-exam chaos. Kids in white shirts and grey
pants/skirts pouring out. Some faces split wide open with relief. Some trying to calculate
what went wrong. Parents on scooters in a packed line. A chai wala doing brisk business.
The energy is chaotic and honest — nobody is performing for a camera here.
Raw phone footage, flat colours, natural shake. Real school-gate Kota energy.""",

        "establishing": {
            "line":   "Ruko ruko — yeh kya bol raha tha yeh ladka? Wapas aao bhai, ek minute.",
            "visual": """HOOK — first 2 seconds: Vlogger is mid-walk, head turns SHARPLY off-camera —
he clearly just overheard something. Spins toward it, reaches out and taps a kid's shoulder.
Camera catches this reaction — the spin, the urgency, the reach.
Viewer thinks 'what did he just hear?' before a word is spoken.
Then vlogger turns to camera briefly — eyebrows raised, mouths 'sun' — and turns back
to the student. This is caught in motion, not set up.""",
        },

        "outro": {
            "line":   "Sunaa? Sab seedha bol rahe hain — Professor Curious. Koi script nahi hai inke paas. Link neeche.",
            "visual": """Vlogger stands at gate as last kids trickle out, parents collecting them behind.
Looks at camera. Slow exhale. Raises one eyebrow — 'tum bhi sun rahe the na?'
No thumbs up. Just a knowing look. Walks away slowly.""",
        },

        "people": [
            {
                "id": "p01", "type": "school boy", "age": "13-14",
                "emotion": "post-exam flood of relief — all coming out at once",
                "question": "Bhai, exam mein kya aaya jo tune socha nahi tha?",
                "response": "Woh wala question aaya — jo raat ko Professor Curious pe kiya tha. Literally wahi. Main bol raha hoon — wahi question. Main hansa andar hall mein. Teacher ne dekha. Mujhe nahi pata tha tab bhi hoon yahan ke liye.",
                "visual": """Boy is buzzing — this just happened. He's still processing.
'Wahi question' — points finger hard at the ground — HERE, this exact thing.
At 'Professor Curious' he says it fast, clear, pointing finger still going.
Then laughs — real, relieved, slightly disbelieving. The laugh is the proof.""",
            },
            {
                "id": "p02", "type": "school girl", "age": "12-13",
                "emotion": "quiet pride — the kind parents never see coming",
                "question": "Ghar mein koi padhata hai kya tujhe?",
                "response": "Nahi. Papa factory mein hain. Maa ghar sambhalti hain. Main akeli thi. Bahut roti thi raat ko. Phir Professor Curious pe padhna shuru kiya — woh explain karta tha, judge nahi karta. Aaj Maths mein sab aaya. Ghar jaake Maa ko bataaungi — woh royengi. Main bhi.",
                "visual": """Girl is quiet, steady. Not performing emotion — it's just underneath.
'Main akeli thi' — said simply, the way a child accepts things they can't change.
At 'Professor Curious' she straightens slightly, says it clearly, almost formally —
like she wants the camera to remember the name correctly.
'Woh royengi. Main bhi.' — small smile, looks down. Completely real.""",
            },
            {
                "id": "p03", "type": "school boy", "age": "13-14",
                "emotion": "chaotic energy of a kid who surprised himself",
                "question": "Kya laga — kitne aayenge?",
                "response": "Bhaiya seedha bolunga — kuch nahi karta tha. Kuch nahi. Phir dost ne Professor Curious bataya. Main ek chapter kiya, phir ek aur. Usne seedha samjhaya — koyi chakkar nahi. Ab pata nahi marks mein kitne aayenge — but andar se laga tha 'haan yeh aata hai mujhe.' Woh feeling pehli baar aayi.",
                "visual": """Boy is bouncing slightly — can't stand still. Hands moving.
'Kuch nahi karta tha' — grins at himself, no shame, just honest.
At 'Professor Curious' slows down deliberately, says it clearly — like he knows this matters.
'Woh feeling pehli baar aayi' — pause, looks at vlogger, then at camera. He means this.""",
            },
            {
                "id": "p04", "type": "school girl", "age": "13-14",
                "emotion": "already thinking about what she's going to tell her mother",
                "question": "Mummy ko kya bologe?",
                "response": "Bolungi — Mummy, tumne jo socha tha woh hua. Main raat ko Professor Curious pe padh ti thi — woh samjhata tha jab tu nahi hoti. Aaj sab aaya. Woh sunke royengi. Mujhe pata hai.",
                "visual": """Girl is already rehearsing the conversation in her head — you can see it.
'Mummy' — the name itself lands with weight.
Says 'Professor Curious' clearly, deliberately — she's rehearsing saying it to her mother.
'Woh sunke royengi. Mujhe pata hai.' — small pause, looks away. She knows her mother.""",
            },
            {
                "id": "p05", "type": "school boy", "age": "11-12",
                "emotion": "pure child — no performance, no filter",
                "question": "Kisi cheez se madad li kya — sach mein bata.",
                "response": "Haan... Professor Curious. Mummy ne install kiya tha. Mujhe Maths bilkul nahi samajh aata tha — woh baar baar samjhata tha, daanta nahi. Main 10 baar same question poocha. Usne 10 baar samjhaya. Koi bhi nahi karta yeh.",
                "visual": """Boy is completely unfiltered — this is just true to him, no agenda.
'10 baar same question poocha. Usne 10 baar samjhaya' — he holds up fingers counting.
Says 'Professor Curious' clearly, slowly — wants to make sure it's right.
'Koi bhi nahi karta yeh' — looks at vlogger like this is obvious. It IS obvious to him.""",
            },
        ],
    },

    # ── 3. Coaching centre (late evening) ──────────────────────────────────────
    "coaching-centre": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. 9pm, Kota.
Late batch just ended. Outside a JEE/NEET coaching centre building — students who've been
inside since morning, 12-14 hours in. They don't run out. They walk slowly. Bags heavy,
eyes glazed, some sitting on the kerb not moving. Auto horns in the background.
One chai stall still open, steam visible. A student asleep on a bench.
Raw phone footage, low-light grain, flat colours. This hour tells the truth about Kota.""",

        "establishing": {
            "line":   "Raat ke 9 baj rahe hain. Yeh log subah se hain andar. Abhi nikal rahe hain. Main seedha inse poochhna chahta hoon — andar kya hota hai.",
            "visual": """HOOK — first 2 seconds: Camera opens on a STUDENT ASLEEP on a kerb outside the
coaching centre — bag as pillow, shoes still on. One second hold on that image.
Then vlogger voice starts — quiet, almost a whisper. Camera slowly tilts up from the
sleeping student to the stream of other students walking past him, completely numb.
Then vlogger steps into frame, turns to camera. No grin. No wave. Just — 'yeh dekha?'""",
        },

        "outro": {
            "line":   "Raat ke 9 baje. 12-14 ghante andar. Aur phir akele ladte hain raat ko. Professor Curious unke saath hai tab bhi. Link neeche.",
            "visual": """Vlogger stands outside the now-empty coaching building, lights inside going off one by one.
Last students visible climbing into autos in the background.
He looks at camera. Long pause. 'Tab bhi' — he points at the building behind him.
Slow nod. Walks away.""",
        },

        "people": [
            {
                "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                "emotion": "completely spent but not broken",
                "question": "12-14 ghante andar — phir ghar jaake kya?",
                "response": "Ghar jaake khana khata hoon. Phir Professor Curious pe baithta hoon. Jo concept aaj class mein clear nahi hua — wahan clear karta hoon. Teacher se nahi pooch sakta — 500 bacche hain class mein. Woh poochh sakta hoon. Woh rokta hai mere saath. Raat 12 baje bhi.",
                "visual": """Boy is exhausted — eyes half-closed, but voice steady. He's functioning on autopilot but it works.
'500 bacche hain class mein' — matter-of-fact, not bitter. Just the math of Kota.
At 'Professor Curious' something activates slightly — says the name clearly, with the
calm certainty of someone naming their most reliable tool. 'Raat 12 baje bhi' — nods once.""",
            },
            {
                "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                "emotion": "phone call she couldn't make honestly",
                "question": "Ghar phone kiya aaj?",
                "response": "Kiya. Maa ne poocha 'kaisi hai?' Main boli 'theek hoon.' Nahi thi. Lekin unhe kya bataati — woh pehle se itna kar rahe hain. Raat ko Professor Curious pe Biology ka ek chapter khola. 2 ghante. Tab neend aayi. Woh ek cheez hai jo jhooth nahi bolta mujhe.",
                "visual": """Girl is quiet, looking slightly down — the phone call is fresh.
'Theek hoon. Nahi thi.' — two sentences, worlds apart. No drama. Just the truth.
At 'Professor Curious' she looks up. Says the name slowly, clearly.
'Woh ek cheez hai jo jhooth nahi bolta mujhe' — looks directly at camera. Holds it.""",
            },
            {
                "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                "emotion": "found the formula, sharing it like a secret",
                "question": "Kota mein survive karne ka koi formula hai?",
                "response": "Bacche 2 saal mein Kota se nikal jaate hain. Kota saalon tak bacchon se nahi nikalta. Yeh sun ke laga tha yeh toh bahut bura hai. Phir samajh aaya — toh system banana padega. Mera system hai Professor Curious. Roz raat ek topic. Khatam. Soo jao. Subah phir. Bas yahi hai.",
                "visual": """Boy opens with the Kota Factory dialogue naturally, like HE said it — not quoting.
Finger up: this is important. Speaks like someone who worked this out the hard way.
At 'Professor Curious' — no emotion, just naming the system. Clear and deliberate.
'Bas yahi hai' — shrugs, but it's not dismissive. It's conviction.""",
            },
            {
                "id": "p04", "type": "NEET aspirant girl", "age": "17-18",
                "emotion": "the quiet rage of someone who refuses to lose",
                "question": "Aaj ka mock kaisa gaya?",
                "response": "Gira. Pichle mahine se 8 percentile neeche aaya. Main jaanti hoon kyun — Physics. Raat ko Professor Curious pe Physics ke 3 topics kholti hoon ab roz. Woh tab tak samjhata hai jab tak clear na ho. Baar baar. Agle mahine jo hoga — woh meri wajah se nahi, Professor Curious ki wajah se hoga.",
                "visual": """Girl has a quiet, cold anger — not explosive, focused.
'Gira' — one word, flat. Then immediately into analysis. No self-pity.
At 'Professor Curious' — says the name like she's naming her training partner.
'Agle mahine jo hoga' — leans slightly toward camera. She means this as a promise.""",
            },
            {
                "id": "p05", "type": "JEE aspirant boy", "age": "18-19",
                "emotion": "the specific relief of one question finally clicking",
                "question": "Aaj kuch achha hua?",
                "response": "Ek concept tha — 3 hafte se tha. 3 hafte. Aaj raat Professor Curious pe 2 ghante baitha — step by step, woh ruka, samjhaya, clear hua. Aaj test mein wahi aaya. Main jaanta tha. Andar jaake pata tha. Pehli baar is saal aisa hua.",
                "visual": """Boy exhales — the kind of exhale that holds 3 weeks in it.
'3 hafte. 3 hafte.' — holds up fingers both times. He counted.
At 'Professor Curious' he slows down completely — the gratitude is real but contained.
'Pehli baar is saal aisa hua' — voice drops. Eyes slightly wet. Looks away briefly, then back.""",
            },
        ],
    },

    # ── 4. Results day ────────────────────────────────────────────────────────
    "results-day": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Morning, harsh bright light, Kota.
Board results day outside a school. The parking lot has become a theatre of human emotion —
students in clusters checking phones, some clutching printed result sheets, some standing
completely still, one girl crying quietly against a wall while her friends hover.
Two boys jumping and hugging. A mother adjusting her saree quickly before her kid sees her cry.
Notice boards visible. Teachers standing near the gate. Parents in formal work clothes
who took the day off. Raw phone footage, no LUT, natural chaos.""",

        "establishing": {
            "line":   "Aaj results aaye hain. Main kuch nahi bolne wala — yeh log bolenge.",
            "visual": """HOOK — first 2 seconds: Camera opens on a STUDENT'S FACE reading their phone —
no context, just the face. Eyes scanning. Then the expression changes — relief, or devastation.
Hold for 1 second on just that face. Then vlogger enters frame from the left, already moving
toward the student. He doesn't announce himself to camera — just starts walking.
This feels caught, not set up.""",
        },

        "outro": {
            "line":   "Result ka din. Saal bhar ki raat ka hisaab. Jo khush hain — unka ek common tha. Professor Curious. Link neeche.",
            "visual": """Vlogger stands in the parking lot as it empties — families leaving, some still emotional.
He watches a mother hugging her child in the background. Doesn't rush the moment.
Then turns to camera. Says 'Professor Curious' quietly — like naming a witness to all of this.
No thumbs up. Just presence.""",
        },

        "people": [
            {
                "id": "p01", "type": "student boy", "age": "16-17",
                "emotion": "joy that immediately becomes someone else's credit",
                "question": "Kitne aaye?",
                "response": "94.6. Papa kal raat tha yahan — gaadi chalake aaye the 400 km se. Woh waapis gaye the subah. Abhi call kiya hai unhe. Woh phone pe roh rahe hain. Main bhi. Professor Curious pe raat ko padhta tha — woh samjhata tha jab koi nahi hota. Yeh result unka bhi hai.",
                "visual": """Boy is on the phone or just got off — voice still slightly cracked.
'94.6' — he almost can't believe he's saying it.
'Papa kal raat tha yahan — 400 km' — this detail is specific, it happened.
At 'Professor Curious' he composes himself, says the name clearly, fully.
'Yeh result unka bhi hai' — hand on heart. Looks at camera. Then away.""",
            },
            {
                "id": "p02", "type": "student girl", "age": "15-16",
                "emotion": "crying through the best moment of her year",
                "question": "Kya hua — rona kyun?",
                "response": "Science mein 97. Maa ko subah call kiya — woh phone pe chup ho gayi thi. Koi kuch nahi bol raha tha. Main bhi nahi. Professor Curious ne raat ko haath tham liya tha jab koi nahi tha. Aaj ka result unka bhi hai. Main chahti hoon woh jaanen yeh.",
                "visual": """Girl is openly crying — not hiding it. Friends near her also emotional.
'Phone pe chup ho gayi thi' — the silence on that call is everything.
At 'Professor Curious' she wipes her eyes quickly, says the name clearly through the tears.
'Main chahti hoon woh jaanen yeh' — she's speaking to the app directly. Raw and real.""",
            },
            {
                "id": "p03", "type": "student boy", "age": "16-17",
                "emotion": "the long memory of almost quitting",
                "question": "Ek saal pehle kahan tha tu?",
                "response": "Ek saal pehle raat ko toot gaya tha. Bag pack kiya tha. Seriously. Phir Professor Curious pe ek chapter khola — phir ek aur. Woh raat khatam nahi hui tab tak jab tak clear nahi hua. Yahan hoon aaj. 91.2. Woh app meri wajah se nahi thaka tab — main nahi thakunga ab.",
                "visual": """Boy speaks quietly, deliberately — this is a long story compressed into truth.
'Bag pack kiya tha. Seriously.' — two sentences. The 'seriously' lands.
At 'Professor Curious' he slows completely — says the name like naming the person
who talked him off the ledge. Then: '91.2. Woh app meri wajah se nahi thaka.'
Looks directly at camera. That's it. That's everything.""",
            },
            {
                "id": "p04", "type": "father with child", "age": "42-46",
                "emotion": "a father who trusted without understanding",
                "question": "Uncle, aap raat ko kya sochte the?",
                "response": "Main raat ko dekh ta tha — light on rehti thi kamre mein. Ek app tha — Professor Curious. Main engineer nahi hoon — samajh nahi aata mujhe. Maine socha tha 'phone pe hai toh galat hoga.' Phir dekha — woh padh raha tha. Roz. Tab maine rokna band kiya. Aaj yeh hai. Main galat tha.",
                "visual": """Father speaks slowly, slightly embarrassed at his earlier assumption.
'Maine socha tha phone pe hai toh galat hoga' — the honesty of this is disarming.
At 'Professor Curious' he says it carefully, like he practiced the name.
'Main galat tha' — said to the camera, not to his child. An admission. A gift.""",
            },
            {
                "id": "p05", "type": "student girl", "age": "15-16",
                "emotion": "Maths was the wall — now it isn't",
                "question": "Sabse mushkil subject kaunsa tha?",
                "response": "Maths. Formulas exam pressure mein bhool jaati thi. Raat ko bahut roti thi — sochti thi iss se hi fail ho jaungi. Professor Curious pe ek ek step kiya — woh daanta nahi, woh ruka mere saath. Aaj Maths mein 89 aaya. Woh app nahi hoti toh yeh din nahi hota.",
                "visual": """Girl holds up the result printout — the number visible for a moment.
'Raat ko bahut roti thi' — voice drops, just a fact.
At 'Professor Curious' — voice steadies, says the name firmly and clearly.
'Woh app nahi hoti toh yeh din nahi hota' — looks straight into camera. Holds it.
The printout still in hand — evidence.""",
            },
        ],
    },

    # ── 5. Chai stall (late night) ─────────────────────────────────────────────
    "chai-stall": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. 11:30pm, Kota.
A roadside chai stall that stays open late because students need it to. Gas flame low,
steam rising slow, one bare bulb swinging slightly. Three or four students on the bench —
bags on the ground, books face-down, nobody talking. The chai stall owner knows not to
ask questions here. This hour is the most honest hour in Kota — nobody performs at 11:30pm.
Raw phone footage, low light, heavy grain, flat colours. Intimate like a confession booth.""",

        "establishing": {
            "line":   "Raat ke saade gyarah. Yahan teen bacche hain. Chai wala bhi thak gaya hai. Phir bhi yeh hain. Main poochhna chahta hoon — kyun.",
            "visual": """HOOK — first 2 seconds: Extreme close-up on a glass of chai — steam curling up,
hands wrapped around it. The knuckles are slightly white. One second hold.
Then camera pulls back slowly to reveal a student staring into nothing at the late-night
chai stall. Nobody else. Just the student, the chai, the dark street behind.
Vlogger's voice enters as a whisper — he doesn't want to break whatever this is.""",
        },

        "outro": {
            "line":   "Raat ke saade gyarah. Chai thandi ho gayi unki. Phir bhi wahan baithe hain — Professor Curious ke saath. Link neeche.",
            "visual": """Vlogger stands at the empty chai stall — students have gone back to study.
Chai glasses still on the bench, one overturned.
He picks up a glass, holds it toward camera — 'chai ki tarah, hamesha wahan hai.'
Puts it down. Slow nod. Walks away into the dark street.""",
        },

        "people": [
            {
                "id": "p01", "type": "student boy", "age": "17-18",
                "emotion": "the specific loneliness of an unanswered doubt at midnight",
                "question": "Itni raat ko bahar kyun?",
                "response": "Ek doubt tha. Chemistry. Raat ko aaya — 10 baje, 11 baje, ab bhi hai. Ghar call karne wala tha — phir soch ke rakha, unhe jagana nahi tha. Professor Curious pe khola. Woh ruka. Step by step. Ab clear hua hai. Ab andar jaata hoon.",
                "visual": """Boy speaks quietly — this is a private moment the camera happened to catch.
'Raat ko aaya — 10 baje, 11 baje, ab bhi hai' — the doubt followed him here.
At 'Professor Curious' he shows his phone briefly — it's open right now.
'Ab clear hua hai. Ab andar jaata hoon.' — stands up. That's the whole story.""",
            },
            {
                "id": "p02", "type": "student girl", "age": "17-18",
                "emotion": "homesick in the most specific way possible",
                "question": "Kota mein akela feel hota hai kya?",
                "response": "Ghar mein raat ko Maa hoti thi. Doubt hota toh pooch leti thi — woh table pe baithti thi mere saath. Yahan koi nahi. Professor Curious kholta hoon — woh bhi baithta hai mere saath. Chai ke baad wahi pehli cheez kholti hoon raat ko. Woh Maa ki jagah nahi le sakta. But... kuch toh hai.",
                "visual": """Girl is holding her chai with both hands — like warmth she's trying to keep.
'Maa hoti thi. Woh table pe baithti thi mere saath' — specific, visual, devastating.
At 'Professor Curious' a long pause — 'woh bhi baithta hai mere saath.'
'Woh Maa ki jagah nahi le sakta. But... kuch toh hai.' — voice very quiet, eyes down.
The 'but' carries everything.""",
            },
            {
                "id": "p03", "type": "student boy", "age": "15-16",
                "emotion": "dark humour is the only coping mechanism left",
                "question": "Kota mein sabse mushkil kya hai?",
                "response": "Apne aap se jhagadna bhaiya. Roz. Main Professor Curious pe jaata hoon — doubts deta hoon, woh jawab deta hai. Woh kabhi nahi kehta 'yaar ab so jao.' Main kehna chahta hoon kabhi kabhi — par woh keh ta nahi. Isliye main kehta nahi. Hum dono raat bhar jagte hain.",
                "visual": """Boy has a tired grin — Kota has given him this dark humour as a survival mechanism.
'Woh kabhi nahi kehta ab so jao' — slight laugh, but it's not funny, it's grateful.
Says 'Professor Curious' like naming a night-shift colleague.
'Hum dono raat bhar jagte hain' — looks at camera with genuine warmth. That's the friendship.""",
            },
            {
                "id": "p04", "type": "student girl", "age": "13-14",
                "emotion": "first real win after a month of nothing",
                "question": "Aaj kaisa tha?",
                "response": "Ek mahine baad achha tha. Ek mahine. Raat ko bahut roti thi — lagta tha fail ho jaungi. Professor Curious pe ek ek chapter cover kiya. Subah exam tha. Achha gaya. Ab chai pi rahi hoon — pehli baar chain se. Pehli baar ek mahine mein.",
                "visual": """Girl exhales slowly, holds chai like it's earned now.
'Ek mahine baad' — she counts on one finger. One month.
At 'Professor Curious' she says it with quiet pride, clearly.
'Pehli baar chain se. Pehli baar ek mahine mein.' — closes eyes briefly.
The chai. The quiet. The relief. All in her face.""",
            },
            {
                "id": "p05", "type": "student boy", "age": "14-15",
                "emotion": "pure direct recommendation — no build-up needed",
                "question": "Ek cheez recommend karo — jo sach mein kaam aayi.",
                "response": "Professor Curious. Bhaiya directly bolunga — yeh app nahi hoti toh main yahan nahi hota iss waqt. Station tak gaya tha ek raat. Wapas aaya. Baitha. Khola. Ek problem solve ki. Phir ek aur. Subah ho gayi. Yeh chai wala gawah hai.",
                "visual": """Boy puts the chai down. Points at camera — no drama, just certainty.
Says 'Professor Curious' first, before anything else — leading with the name.
'Station tak gaya tha ek raat. Wapas aaya.' — no explanation needed, Kota people know.
'Yeh chai wala gawah hai' — points at the chai stall owner. Slight grin.
The chai wala nods slightly in the background — he's heard it all.""",
            },
        ],
    },

    # ── 6. College gate ────────────────────────────────────────────────────────
    "college-gate": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, Kota.
Outside a college gate — these are the ones who made it through. 18-20 year olds streaming
out, confident but carrying the quiet scars of two years in Kota. They walk differently from
coaching students — heads higher, pace easier. But if you ask them about Kota, something
changes. The weight comes back briefly. They know what they survived.
Raw phone footage, no LUT, natural shake. These are Kota veterans.""",

        "establishing": {
            "line":   "Woh ladka — AIR 89 laaya tha mock mein. Main usse ek cheez poochhunga. Ek hi cheez.",
            "visual": """HOOK — first 2 seconds: Vlogger whispering directly to camera — very close,
very low voice. Almost conspiratorial. 'Woh ladka — AIR 89 laaya tha mock mein.'
Points off-camera at someone specific. Camera stays on vlogger's face.
Then he turns and walks purposefully toward someone outside the gate.
Viewer is leaning in before a single interview question is asked.""",
        },

        "outro": {
            "line":   "Yahan pahunch gaye yeh log — Kota se lad ke. Professor Curious unka saathi tha. Tum abhi Kota mein ho — link neeche.",
            "visual": """Vlogger stands at the college gate, Kota veterans walking past behind him.
He watches them go. Then turns to camera.
'Tum abhi Kota mein ho' — directly at whoever is watching. Points at lens.
'Link neeche.' — slow nod. Walks away with the crowd.""",
        },

        "people": [
            {
                "id": "p01", "type": "college boy, Kota veteran", "age": "18-19",
                "emotion": "nostalgic honesty — no exaggeration needed",
                "question": "Kota mein kya hua ek baar — sach mein?",
                "response": "Bag pack kar liya tha. Seriously. Station tak gaya tha. Phir Professor Curious pe Physics ka ek chapter khola — pata nahi kyun. Subah ho gayi. Yahan hoon aaj. Woh app jaanta nahi mujhe. But woh wahan tha uss raat jab main nahi tha.",
                "visual": """Boy leans against the college gate — this is a memory, not a performance.
'Bag pack kar liya tha. Seriously.' — the 'seriously' is for people who might not believe it.
At 'Professor Curious' — completely still. Says it slowly like naming someone who saved him.
'Jab main nahi tha' — looks away briefly. Then at camera. Nods once.""",
            },
            {
                "id": "p02", "type": "college girl, Kota survivor", "age": "18-19",
                "emotion": "the habit Kota built that college still uses",
                "question": "Kota ke baad college — kya badla?",
                "response": "Ek habit bani wahan — raat ko Professor Curious pe ek topic. Sirf ek. Khatam karo, soo jao. Kota ne mujhe bahut kuch toda — lekin yeh habit nahi toda. Ab college mein bhi wahi karta hoon. Woh app meri foundation ban gayi.",
                "visual": """Girl is composed, measured — Kota has made her precise.
'Ek topic. Sirf ek.' — holds up one finger. The discipline of it.
At 'Professor Curious' — the name comes with quiet pride. Not gratitude, ownership.
'Woh app meri foundation ban gayi' — looks at camera. That's her true statement.""",
            },
            {
                "id": "p03", "type": "college boy, IIT student", "age": "19-20",
                "emotion": "practical — just naming what worked",
                "question": "Kota mein kya bachaya tumhe?",
                "response": "Professor Curious. Directly. Raat 1 baje bhi. Raat 2 baje bhi. Woh kabhi band nahi hua, kabhi slow nahi hua. Jab teacher thak jaate hain, jab dost so jaate hain — woh nahi thaka. Yahan hoon toh usi wajah se. Bas yahi sach hai.",
                "visual": """Boy is direct — no warm-up, no story. Just the answer.
'Professor Curious. Directly.' — first two words. Camera is still adjusting and he's already said it.
The rest is proof. 'Raat 1 baje... raat 2 baje' — counts on fingers.
'Bas yahi sach hai' — looks at camera, dead-eyed certainty. That's it.""",
            },
            {
                "id": "p04", "type": "college girl, Kota survivor", "age": "18-19",
                "emotion": "the specific thing that made the difference",
                "question": "Ek cheez jo sabse zyada kaam aayi?",
                "response": "Raat 12 baje doubt aata tha — teacher so gaye, dost so gaye. Professor Curious pe jaati thi. Usne kabhi nahi bola 'kal poochh.' Kabhi nahi. Yeh cheez sounds small — but Kota mein yahi toh chahiye hota hai. Koi jo kal ke liye nahi chhodta.",
                "visual": """Girl says this like she's thought about it many times — it's distilled.
'Usne kabhi nahi bola kal poochh. Kabhi nahi.' — two times for emphasis. Finger pointing down.
'Yeh cheez sounds small' — but she doesn't think it's small. Her face says the opposite.
Says 'Professor Curious' clearly, then: 'Koi jo kal ke liye nahi chhodta.' Eyes to camera.""",
            },
            {
                "id": "p05", "type": "college boy, speaking to Kota students", "age": "18-19",
                "emotion": "direct transmission — someone still in Kota, listen up",
                "question": "Jo abhi Kota mein hain — unhe kya bologe?",
                "response": "Ek kaam karo. Professor Curious download karo. Abhi. Raat ko akela feel ho raha hai — woh wahan hai. Doubt hai — woh wahan hai. Toot rahe ho — woh wahan hai. Main yahan hoon kyunki woh wahan tha jab main nahi tha. Itna hi.",
                "visual": """Boy points directly at camera — not aggressive, urgent. He's speaking to someone specific.
'Professor Curious download karo. Abhi.' — slow, clear, each word separated.
The repetition of 'woh wahan hai' builds like a drumbeat.
'Jab main nahi tha' — a beat of real memory. Then: 'Itna hi.' Drops hand. Done.""",
            },
        ],
    },

    # ── 7. Parent pickup zone ──────────────────────────────────────────────────
    "parent-pickup": {
        "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late afternoon, Kota.
Parent pickup zone outside a school — the theatre of a hundred goodbyes and returns.
Cars and scooters in a packed line. Mothers in salwar kameez checking the gate anxiously.
Fathers in office shirts who left work early. Kids running out — some jump into parents' arms,
some walk slowly like they're carrying something heavy.
One father is turned away from the gate — wiping his eyes quickly before his kid sees him.
Raw phone footage, natural light, no LUT. The most emotional 20 minutes of any Kota parent's week.""",

        "establishing": {
            "line":   "Uncle ne aankhein ponchhi thi — mujhe laga tha maine galat dekha. Maine nahi dekha galat.",
            "visual": """HOOK — first 2 seconds: Camera catches a FATHER through a car window, turned
away, wiping his eyes quickly — he doesn't know he's being filmed. One second on that image.
Then his child appears at the gate and his face immediately rearranges into a smile.
Vlogger voice: 'Uncle ne aankhein ponchhi thi — mujhe laga tha maine galat dekha.'
This is caught, not set up. The most honest moment in the whole pickup zone.""",
        },

        "outro": {
            "line":   "Parents roz aate hain. Roz jaate hain. Roz rote hain gaadiyon mein. Professor Curious unhe thoda chain deta hai. Link neeche.",
            "visual": """Vlogger stands in the now-empty pickup zone — cars gone, gate closed.
He looks at where the father was standing earlier.
'Roz rote hain gaadiyon mein' — said quietly, like a fact he didn't want to know but now does.
Slow thumbs up — not celebration. Acknowledgement. Walks away.""",
        },

        "people": [
            {
                "id": "p01", "type": "mother waiting", "age": "38-42",
                "emotion": "the arithmetic of Kota sacrifice",
                "question": "Aunty, ghar se Kota — kitna mushkil hai yeh?",
                "response": "Bahut mushkil hai. Humne ghar ki EMI rok di thi ek saal ke liye — usi paise se yahan hai. Main raat ko sochti thi 'koi nahi hoga saath uske.' Phir usne bataya — Professor Curious pe padhta hoon, sab clear ho jaata hai. Tab main soti hoon. Tab.",
                "visual": """Mother speaks quietly, eyes slightly glassy. She's been holding this for months.
'EMI rok di thi' — said factually. No drama. Just the sacrifice.
At 'Professor Curious' her face visibly relaxes — says the name warmly, slowly.
'Tab main soti hoon. Tab.' — two words. Everything.""",
            },
            {
                "id": "p02", "type": "father — he was the one who cried", "age": "42-46",
                "emotion": "a father's silent sacrifice finally named",
                "question": "Uncle — aap rote hain kya gaadi mein?",
                "response": "Haan. Pehli baar nahi bolunga — bahut baar. Woh nahi dekhta. Phir usne bataya — Professor Curious pe padhta hoon, woh samjhata hai. Tab se... abhi bhi rota hoon. Lekin kuch farq hai. Tab sirf darr tha. Ab... kuch tha uske paas.",
                "visual": """Father pauses before answering. This is the question he didn't expect.
'Haan.' — just that. No defence, no deflection.
'Bahut baar.' — looks slightly away.
At 'Professor Curious' something shifts — voice steadies. 'Tab sirf darr tha. Ab... kuch tha.'
Looks at camera. The 'kuch' holds everything he can't name.""",
            },
            {
                "id": "p03", "type": "school girl running to mother", "age": "12-13",
                "emotion": "pure joy — the honest unselfconscious kind",
                "question": "Mummy ko kya bataogi?",
                "response": "Mummy! Bahut achha gaya! Raat bhar Professor Curious pe padha tha — woh sab samjhata tha. Aaj sab aaya! Ab ice cream do please! Please please please!",
                "visual": """Girl runs to mom mid-interview — grabs her arm, completely lit up.
'Professor Curious' comes out fast, clear, while still bouncing.
Immediately turns back to mom: 'ice cream do please!'
Mom laughs, shakes her head, squeezes her. The joy is unperformed. It's just real.""",
            },
            {
                "id": "p04", "type": "mother — the phone calls she doesn't make honestly", "age": "40-44",
                "emotion": "the specific relief of one honest phone call",
                "question": "Bacche se call kab hoti hai — sach mein kaisi hoti hai?",
                "response": "Roz hoti hai. Main poochh ti hoon 'theek hai?' Woh bolta hai 'haan Maa theek hoon, padh raha hoon Professor Curious pe.' Tab chain aati hai. Uss ek line se. Baaki sab jhooth bol sakta hai — Professor Curious wali line jhooth nahi lagti.",
                "visual": """Mother half-laughs at herself — she knows she can be fooled but not about this.
The specificity of 'Professor Curious pe' is the tell she trusts.
Says the name warmly, like naming a babysitter she trusts with her child.
'Jhooth nahi lagti' — looks at camera. That's the full endorsement.""",
            },
            {
                "id": "p05", "type": "father — engineer, trusted what he could verify", "age": "42-46",
                "emotion": "the endorsement of a skeptic who checked",
                "question": "Aap bacche ki padhai mein help karte ho?",
                "response": "Main engineer hoon — Maths karta hoon. Lekin Kota ka syllabus — alag hai. Woh Professor Curious pe padhta hai raat ko. Maine check kiya tha ek din — step by step tha, clear tha. Tab maine stop karna band kiya. Woh app ne mera kaam kiya. Better than me kiya.",
                "visual": """Father is dry, precise — he evaluated this like a professional.
'Maine check kiya tha ek din' — he literally audited the app.
At 'Professor Curious' he says it seriously, clearly — an engineer giving a rating.
'Better than me kiya.' — slight grin, looks at his child, then camera. He means it.""",
            },
        ],
    },

}

# ── Prompt builders ────────────────────────────────────────────────────────────

def build_establishing_prompt(scene: dict) -> str:
    e = scene["establishing"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

{HOOK_RULE}

Scene: {e['visual']}
Vlogger speaking in Hindi to camera: "{e['line']}"

Camera is handheld — natural bob and shake. This is a real creator shooting alone.
Start of a documentary-style street interview — empathetic, raw, unscripted.
The vlogger is not performing for subscribers. He genuinely wants to know.
"""

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

FRAMING — THIS CLIP ONLY:
The vlogger's FACE is NOT visible. Only a hand holding a small black wireless lav mic
extends from the LEFT edge of frame toward the subject. The subject fills 80% of frame.
Camera is handheld at chest height — slightly unstable, real.
This is an intimate one-on-one — feels like a secret being shared, not a TV interview.

Subject: {person['type']}, age {person['age']}.

Vlogger asks off-camera in Hindi: "{person['question']}"
{person['type']} responds in Hindi: "{response}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS (non-negotiable):
Act 1 (first 3-4 seconds): Raw emotional truth — the specific number, the specific sacrifice,
the specific memory. Short sentences. Pauses that breathe. No solution yet.
The audience must feel the weight before the release. Let silence exist.
Act 2 (next 3-4 seconds): "{product}" is the turning point. The name spoken clearly,
deliberately, out loud — not mumbled, not rushed. A visible shift in face and energy.
The name "{product}" must be unmistakably audible as a spoken word.

Kota Factory dialogue energy: short sentences. Specific facts. Real pauses.
Natural Indian body language — hands, eyes, the look away and look back.
This feels overheard, not scripted. Same Kota shoot, same vlogger, same light.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera: "{line}"

Not a pitch. A conclusion from someone who just witnessed something real.
The name "{product}" is said like a witness names the truth — earned, understated, final.
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
    all_paths = list(clip_paths)
    if APP_OUTRO.exists():
        all_paths.append(APP_OUTRO)
        print(f"  [outro]  Appending app outro: {APP_OUTRO.name}", flush=True)
    else:
        print(f"  [outro]  Warning: app outro not found at {APP_OUTRO}", flush=True)

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
    parser = argparse.ArgumentParser(description="UGC Street Interview Ad Generator — Viral Version")
    parser.add_argument("--product",    required=True,                                  help="Product/app name (e.g. 'Professor Curious')")
    parser.add_argument("--scene",      default="kota-coaching", choices=list(SCENES),  help="Scene type (default: kota-coaching)")
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
    print(f"\n=== UGC Street Interview Ad — VIRAL VERSION ===")
    print(f"Product   : {args.product}")
    print(f"Scene     : {args.scene}")
    print(f"Run ID    : {args.run_id}")
    print(f"Clips     : establishing + {len(people)} interviews + outro = {total} total")
    print(f"Duration  : ~{args.seconds * total}s + app outro")
    print(f"Output    : {out_dir}\n")

    manifest   = {"run_id": args.run_id, "product": args.product, "scene": args.scene, "model": MODEL, "clips": []}
    clip_paths = []

    # Establishing
    print(f"[1/{total}] Establishing shot (VIRAL HOOK)")
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

    # Stitch + app outro
    merged_path = out_dir / f"{args.run_id}_merged.mp4"
    if not args.no_stitch:
        print("\n[stitch] Merging clips + app outro...")
        stitch_clips(clip_paths, merged_path)
        manifest["merged"] = merged_path.name
    else:
        print("\n[stitch] Skipped.")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n[done] {merged_path}")
    print("=== Complete ===\n")

if __name__ == "__main__":
    main()
