#!/usr/bin/env python3
"""
STREET INTERVIEW STYLE 1 — Classic Vlogger Format
====================================================
The original format: vlogger (navy t-shirt, foam-ball mic) is visible throughout
ALL clips — establishing, every interview, and outro. Raw, intimate, consistent
character presence. Clips default to 12 seconds.

Usage:
  python3 run_style1.py --product "Professor Curious" --scene kota-coaching --run-id kota_v1
  python3 run_style1.py --product "Professor Curious" --scene kota-coaching --run-id kota_v2 --vlogger-gender female
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

# ── Vlogger lock — identical across every scene and every clip ────────────────

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Navy blue round-neck t-shirt,
dark jeans. Holds a small black handheld reporter mic with round black foam ball top
in his right hand. Visible from chest up on the left edge of frame, slightly low angle."""

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
            "line":   "Bhai, abhi Kota mein hoon — shaam ke saat baj rahe hain, coaching centre se nikal rahe hain yeh bacche. Inka chehra dekho — aankhon ke neeche kaale daag, haath mein do do kilo ke notes, kapde mein thakaawat. Yeh log ghar se 500, 700, 1000 kilometre door hain. Inke parents ghar pe ek ek raat jaag ke paise jod rahe hain — koi zameen bech raha hai, koi gold bech rahi hai. Sirf ek umeed pe — ki yeh baccha set ho jaayega. Aaj main seedha inse poochuunga — sach mein kya chal raha hai andar se, koi script nahi, koi filter nahi.",
            "visual": "Vlogger walks toward the coaching centre exit in selfie-cam, silent heavy-burdened students streaming out behind him. He slows, looks at camera with real weight — not entertained, genuinely moved. Points at students behind him mid-sentence. Camera bobs with his walk.",
        },
        "outro": {
            "line":   "Yaar, in bacchon se milke aaj kuch alag hi feel hua. Kota mein laakhon bacche hain — akele, thake hue, raat ko chup chap rote hain. Ghar ko keh nahi sakte. Teacher ke paas time nahi. Dost bhi wahi halat mein hain. Tab ek cheez kaam aati hai — Professor Curious. Yeh app inke paas hoti hai — raat ke 1 baje, 2 baje — doubt uthao, woh wahan hai. Judges nahi karta. Thakata nahi. Jaata nahi. Agar tumhara baccha Kota mein hai — ya koi bhi padh raha hai — link neeche diya hai. Abhi download karwao. Seedha.",
            "visual": "Vlogger turns selfie-cam on himself outside coaching centre, students silently walking away behind him. Eyes slightly watery, voice deliberate. Slow thumbs up at the end — not a gimmick, means it.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "broken then hopeful",
             "question": "Bhai, sach bata — Kota mein kaisa lag raha hai?",
             "response": "Bhaiya, ghar se 700 kilometre door hoon. Pehli baar akele reh raha hoon — koi nahi hai. Raat ko ek concept samajh nahi aata, class mein poochh nahi sakta — 200 bacche hain, teacher ke paas waqt nahi. Ghar phone karta hoon — papa poochte hain kaisa hai — kehta hoon 'theek hoon.' Sach nahi bolta. Unhe pareshan nahi karna. Ek raat bahut bura laga — bas leta tha andheron mein. Phir Professor Curious khola — ek doubt dala, woh ruka, samjhaya, nahi gaya jab tak clear nahi hua. Ek aur doubt diya — phir samjhaya. Puri raat. Subah uthke dekha — woh concept crystal clear tha. Tab se roz karta hoon. Jab bhi toot ta hoon — Professor Curious wahan hai.",
             "visual": "Boy's jaw tightens at first, voice goes quiet mentioning home. Eyes glass over — holds back tears. Then at 'Professor Curious' his face softens completely. Speaks the name clearly, slowly. A real turning point visible on his face."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "exhausted then determined",
             "question": "Doctor banna hai — but aaj kaisi hai halat?",
             "response": "Bhaiya, maa ne gold becha tha mujhe Kota bhejna ke liye. Woh sona jo unki shaadi ka tha. Yeh soch ke roz raat ko aankh khul jaati hai — 3 baje, 4 baje — andheron mein baithke roti hoon. Kisi ko nahi bata sakti — maa ko toh bilkul nahi. Woh itna kar rahi hain mere liye. NEET mein Biology hai — Genetics, Physiology — itna hai ki dimag ghoom jaata hai. Phir Professor Curious pe khol ti hoon — woh samjhata hai, ek ek step, baar baar, kabhi nahi kehta 'kal poochh.' Mujhe lagta tha main nahi kar sakti. Professor Curious ne woh soch badli. Aaj main karungi — maa ke liye.",
             "visual": "Girl's voice breaks slightly mentioning her mother and the gold. She pauses, composure slips briefly — then she straightens. At 'Professor Curious' speaks with full quiet conviction. A real turning point on her face."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw and candid",
             "question": "Kabhi laga ki sab chod ke chale jao?",
             "response": "Haan bhaiya. Ek raat seriously bag pack kar liya tha — pura. Socha subah nikal jaaunga. Koi ko bata bhi nahi tha. Bas itna bura laga tha andar se — rank nahi aa raha, concept samajh nahi aa raha, akela feel ho raha tha. Tab kuch nahi socha — bas Professor Curious khola. Physics ka ek chapter. Phir ek aur. Phir ek aur. Raat bhar padhta raha — kabhi gaya hi nahi soone. Subah tak bag wahan pada tha aur main padh raha tha. Professor Curious nahi hota toh main yahan nahi hota aaj. Woh app jaanta nahi mujhe — lekin usne roka mujhe uss raat. Seedha.",
             "visual": "Boy laughs softly at first — there's real pain behind it, no performance. Looks away briefly remembering that night. When he says 'Professor Curious' he looks straight at camera — grounded, grateful, completely sincere."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "fierce and emotional",
             "question": "Competition itna bada hai — tum kaise khud ko alag karti ho?",
             "response": "Roz 5 baje uthti hoon. Sone se pehle raat ko 12 baje tak padhti hoon. Roz kuch toot ta hai andar se — rank list aati hai, naam neeche hota hai, kuch samajh nahi aata, loneliness aati hai. Main roti hoon — phir uthti hoon. Jo concept clear nahi hota, Professor Curious pe jaati hoon. Woh tab tak samjhata hai jab tak clear na ho jaaye — baar baar, step by step, bina daante, bina thake. Yeh meri edge hai — yeh app nahi chodti main. Jitne bacche yahan hain, sabke paas same coaching hai, same books hain — Professor Curious meri wajah se alag hoon main.",
             "visual": "Girl is fierce — jaw set, eyes sharp and intense. Voice very steady but the weight is present underneath. Says 'Professor Curious' like a fighter names their weapon — not emotional, but owned completely."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",
             "question": "Aaj ka mock test kaisa gaya?",
             "response": "Bhaiya pichle teen din se ek concept tha — Organic Chemistry ka — dimag mein ghus hi nahi raha tha. Class mein poochha tha — teacher ne samjhaya tha, phir bhi clear nahi hua. Raat ko Professor Curious pe baitha — do ghante laga diye. Woh step by step lete gaye — ek ek reaction, ek ek mechanism, ruka nahi jab tak main nahi bola ki samajh aaya. Subah uthke exam diya. Bhaiya, wahi question aaya test mein. Seedha. Main ruka — smile aa gayi mujhe exam hall mein. Pehli baar is saal laga — haan, sahi kiya Kota aakar. Professor Curious ne yeh din diya mujhe.",
             "visual": "Boy exhales deeply — real unperformed relief. Eyes slightly wet, slow smile spreading. Says 'Professor Curious' with a deliberate nod — like he means every syllable. First genuine full smile of the clip."},
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
            "line":   "Bhai, Kota mein school gate pe hoon — abhi abhi exams khatam hue hain. Yeh bacche dekho — kuch khush hain, kuch ka chehra bata raha hai kya hua andar. Inke haath mein question papers hain, kuch roo rahe hain, kuch dost se chipke hain. Yeh woh umar hai jahan ek number se poori zindagi badal jaati hai — yahan Kota mein toh aur bhi zyada. Bacchon ke parents bahar khade hain — unki aankhen dekho, woh tension dekho. Chalo main seedha inse poochhta hoon — sach mein kya hua aaj, koi polish nahi.",
            "visual": "Vlogger walks toward school gate in selfie-cam mode, points at kids pouring out, looks empathetically at anxious parents, camera bobs with walk.",
        },
        "outro": {
            "line":   "Bhai, yeh bacche jo abhi gate se nikal rahe hain — yeh woh umar hai jab ek doubt clear na ho toh poori subject se nafrat ho jaati hai. Aur yahan Kota mein competition itna hai ki ghar pe baat bhi nahi ho pati. Professor Curious yahi karta hai — roz raat ko jo samajh nahi aaya, woh clear karta hai. Judge nahi karta, daanta nahi karta. In bacchon ka saathi hai. Link neeche hai — abhi download karwao, sirf ek try karo.",
            "visual": "Vlogger walks away from gate in selfie-cam, kids streaming out behind. Looks at camera, eyebrows raised, genuine thumbs up.",
        },
        "people": [
            {"id": "p01", "type": "school boy",  "age": "13-14", "emotion": "relieved and emotional",
             "question": "Exam ke pehle dar lag raha tha?",
             "response": "Bhaiya bahut dar tha — raat ko so nahi pa raha tha, seriously. Ek ek formula bhool raha tha, ek ek chapter ghoomta tha dimag mein. Papa ko bol nahi sakta tha — woh pehle se tension mein hain mere liye. Toh main akela baitha tha — phir Professor Curious khola. Woh samjhata tha, baar baar, jab tak main nahi bola 'haan clear hua.' Kabhi nahi bola 'kab tak poochhega.' Kabhi nahi bola 'baar baar mat poochh.' Raat bhar karta raha. Aaj paper mein jo bhi aaya — sab tha wahan. Sab. Ek bhi question aisa nahi tha jo nahi aata tha. Professor Curious ki wajah se. Sach mein.",
             "visual": "Kid's eyes go wide remembering the fear. Then visibly softens at 'Professor Curious' — says the name clearly, slowly, proudly. Relief is completely real."},
            {"id": "p02", "type": "school girl", "age": "12-13", "emotion": "sincere and moved",
             "question": "Ghar mein koi padhata hai kya?",
             "response": "Nahi bhaiya, Papa kaam pe hote hain raat tak — woh late aate hain. Mummy ko science nahi aati. Main akeli baithti thi raat ko — samajh nahi aata tha, koi nahi hota poochhne ko. Bahut akela lagta tha — honestly. Phir mummy ne Professor Curious install kiya tha phone mein. Pehle mujhe lagta tha yeh app hi hai kya kar legi — phir try kiya. Bhaiya, woh samjhata tha, meri speed pe, meri language mein, jab bhi poochha. Koi judgment nahi. Koi irritation nahi. Aaj exam mein woh cheez aayi jo main samajh hi nahi pa rahi thi pehle. Ab akeli nahi hoon padhte waqt. Professor Curious hai mere saath.",
             "visual": "Girl is quiet, sincere. Slightly teary at 'akeli.' At 'Professor Curious' she straightens — says the name clearly with a small proud smile."},
            {"id": "p03", "type": "school boy",  "age": "13-14", "emotion": "funny then sincere",
             "question": "Koi app use kiya kya — sach bata!",
             "response": "Bhaiya seedha bolunga — pehle main kuch nahi karta tha. Bas rota tha aur so jaata tha. Padhai se dartaath — seriously. Phir dost ne Professor Curious bataya — mujhe laga fake hai. Try kiya. Bhaiya — woh itna simple samjhata hai. Concepts jo textbook mein mile nahi aate, woh seedha explain karta hai — baar baar, same doubt pe, kabhi bore nahi hota. Pehle din se roz use karta hoon. Koi bhi time — subah, raat, bheech exam se pehle — woh available hai. Aaj bahut achha gaya paper. Maa ko bolunga aaj — Professor Curious ki wajah se.",
             "visual": "Boy grins at first, then gets completely genuine. Says 'Professor Curious' looking straight at camera — slow and clear, like he wants everyone watching to remember the name."},
            {"id": "p04", "type": "school girl", "age": "13-14", "emotion": "proud and emotional",
             "question": "Mummy ko kya bologe result ka?",
             "response": "Main bolungi — Mummy, tumne jo umeed rakhi thi woh karke aayi hoon. Raat ko Professor Curious pe padha tha — bahut raat tak. Mummy kehti thi phone rakh do beta — main kehti thi bas thodi der. Woh samjhata tha jab koi nahi hota, ek ek step, bina daante. Aaj paper mein jo kuch bhi aaya — sab aaya. Science, Maths — sab clear tha. Mummy ke aankhon mein aaj jo khushi hogi na — Professor Curious ki wajah se hogi. Main keh dungi unhe. Seedha. Aaj raat ko saath baithke bataungi unhe — yeh app download karaaungi inhe bhi.",
             "visual": "Girl's voice catches slightly at 'Mummy.' Composes herself. Says 'Professor Curious' deliberately, loud enough — like she's rehearsing what she'll tell her mother tonight."},
            {"id": "p05", "type": "school boy",  "age": "11-12", "emotion": "shy then proud",
             "question": "Kisi app se padha kya — batao na!",
             "response": "Haan bhaiya — Professor Curious. Mummy ne install kiya tha. Pehle main bahut confuse rehta tha Maths mein — fractions, decimals — dimag mein ghoomta rehta tha sab. Teacher class mein samjhate hain — main peechhe baithta hoon, seedh se nahi aata. Toh ghar aake Professor Curious pe same cheez poochh ta tha. Woh baar baar samjhata tha, gaali nahi deta tha... haha. Seedha seedha bolun toh — ab Maths achha lagta hai. Pehle kabhi nahi lagta tha. Yeh baat main sach bol raha hoon. Professor Curious ne Maths se dosti karaai meri.",
             "visual": "Boy initially shy, looks down. Then says 'Professor Curious' clearly — small giggle at his own joke about being scolded, then a real warm full smile."},
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
            "line":   "Bhai, Kota mein hoon abhi — coaching centre ke baahir. Shaam ke saat baj rahe hain. Yeh bacche abhi abhi nikal rahe hain — 10, 12, 14 ghante padh ke. Inke haath mein notes hain, aankhon mein ek khaas qisam ki thakaawat hai — woh thakaawat jo sirf Kota deta hai. Yeh log ghar se kosi door hain — akele kamron mein, koi nahi. Raat ko jab koi concept clear nahi hota — tab kya karte hain? Yahi main aaj poochhna chahta hoon. Seedha, bina filter ke.",
            "visual": "Vlogger walks toward the coaching centre exit as silent burdened students stream out, turns selfie-cam to himself, gestures quietly at the exhausted students behind him. Empathetic, not entertained.",
        },
        "outro": {
            "line":   "Bhai, aaj yahan aake ek cheez bahut clearly samajh aayi — Kota mein padhai karne wale yeh bacche roz ladte hain. Raat ko coach so jaate hain, ghar wale far hain, dost usi halat mein hain. Tab ek cheez hai jo nahi jaati — Professor Curious. Raat ke 2 baje bhi, Sunday ko bhi, exam ke ek ghante pehle bhi — woh wahan hai. Agar tumhara koi Kota mein hai ya koi bhi padh raha hai — link neeche hai, ekdum seedha.",
            "visual": "Vlogger turns selfie-cam on himself outside coaching centre, students silently calling autos behind him. Serious, knowing look. Slow thumbs up — felt, not performed.",
        },
        "people": [
            {"id": "p01", "type": "JEE aspirant boy",  "age": "17-18", "emotion": "broken then hopeful",
             "question": "Coaching mein kitne ghante padhte ho — aur phir bhi kya hota hai?",
             "response": "Bhaiya roz 12 se 14 ghante padh ta hoon — honestly. Subah 6 baje uthke coaching, phir raat 10 tak. Phir bhi hota yeh hai ki raat ko ek concept dimag mein nahi rehta. Class mein poochh nahi paata — 200 bacche hain, teacher ko time nahi. Akela baithta hoon room mein — kisi ko poochh nahi sakta. Ghar wale phone karte hain — 'kaisa hai?' — 'theek hoon' kehta hoon. Sach bol nahi sakta. Phir Professor Curious pe woh concept dalta hoon. Woh rukta hai mere saath — tab tak jab tak bilkul clear na ho. Kabhi nahi uthta beech mein. Kota mein yahi chahiye hota hai — koi jo chode na.",
             "visual": "Boy looks genuinely exhausted. Voice drops quietly at 'akela baithta hoon.' Rallies at 'Professor Curious' — says it clearly, deliberately. A quiet resolve returns to his face."},
            {"id": "p02", "type": "NEET aspirant girl", "age": "17-18", "emotion": "focused and emotional",
             "question": "NEET clear karna hai — lekin aaj kaisi feel ho rahi hai?",
             "response": "Aaj mock mein bahut bura score aaya. Bahut bura. Ghar phone kiya — lekin unhe bata nahi sakti kitna problem ho raha hai — woh pehle se itna kar rahe hain mere liye, maa ne gold becha tha mujhe yahan bhejna ke liye. Toh main chup rahi. Rona bhi andar andar kiya. Phir Professor Curious pe Biology ka ek chapter khola — woh itna seedha samjhata hai, step by step, koi jaldi nahi, koi judgment nahi. Raat tak ek ek topic clear hua. Subah uthke laga — haan, kar sakti hoon. Professor Curious ne woh raat nikaali meri.",
             "visual": "Girl's voice tightens at 'ghar phone kiya.' A beat of real vulnerability. At 'Professor Curious' she steadies, looks straight at camera — says the name slowly, clearly, like it means something real."},
            {"id": "p03", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "raw honesty",
             "question": "Kota mein kitna mushkil hai — sach mein?",
             "response": "Bhaiya bahut mushkil hai — log yahan rank ke liye jeete hain. Roz toot te hain. Ek raat itna bura laga ki kuch bhi nahi karna tha — seriously, kuch bhi nahi. Phir woh raat kuch aur bhi ho sakta tha. Lekin kuch nahi kiya — bas Professor Curious khola. Ek problem solve ki. Phir ek aur. Phir ek aur. Raat bhar. Subah hua toh main theek tha. Woh app nahi jaanta mujhe — mere naam ka nahi jaanta — lekin usne woh raat paar karayi meri. Yeh main bahut seriously bol raha hoon.",
             "visual": "Boy looks away for a second — raw, no performance, a heaviness in the pause. Says 'Professor Curious' quietly but clearly, looking straight to camera. Then nods once — that's the whole truth."},
            {"id": "p04", "type": "NEET aspirant girl", "age": "17-18", "emotion": "fierce",
             "question": "Topper kaisi banti ho yahan — koi secret?",
             "response": "Koi secret nahi bhaiya — bas yeh ki main roti hoon, phir uthti hoon. Roz. Roz kuch toot ta hai — rank nahi aati, concept clear nahi hota, dost ki rank zyada hoti hai — toh roti hoon. Phir uthti hoon. Jo samajh nahi aata — Professor Curious pe jaati hoon. Woh tab tak samjhata hai jab tak clear na ho — baar baar, bina thake, bina judge kiye, kabhi nahi kehta 'kal poochh.' Yahi edge hai mera Kota mein. Sab ke paas same books hain, same coaching hai — Professor Curious meri wajah se alag hoon main.",
             "visual": "Girl is fierce — jaw set, eyes sharp. Says 'Professor Curious' like naming a trusted weapon — clear, loud, completely owns it."},
            {"id": "p05", "type": "JEE aspirant boy",  "age": "18-19", "emotion": "deeply relieved",
             "question": "Aaj ka test kaisa gaya?",
             "response": "Bhaiya, Chemistry ka ek concept tha — teen din se dimag mein nahi ghus raha tha. Coordination compounds — puri sheet bhar ke notes likhe, phir bhi nahi hua. Raat ko Professor Curious pe baitha — do ghante. Step by step lete gaya woh — ek ek cheez, ruka, poocha 'samajh aaya?', nahi bola toh aur samjhaya. Aaj usi se question aaya — seedha. Exam hall mein hath ruka tha — phir samjha, seedha likha. Pehli baar is saal feel hua — Kota aana sahi tha. Professor Curious ne yeh din diya.",
             "visual": "Boy exhales slowly — real relief, eyes a little wet. Says 'Professor Curious' with a slow nod, completely sincere. First genuine smile of the clip."},
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
            "line":   "Bhai, Kota mein board results aaye hain aaj — yahan ka maahaul dekho. Kuch roo rahe hain — khushi mein, kuch dard mein. Yeh woh bachche hain jo mahino se ghar nahi gaye, jinhone raat raat jaag ke padha, jinhone poori zindagi ek number pe laga di. Aaj pata chala kya hua. Ek baap wahan baitha hai — aankhon mein aansu aa rahe hain. Ek ladki apni maa ko hug kar rahi hai — kuch keh nahi pa rahi. Yeh Kota ki sabse bhari subah hai. Main aaj inse seedha poochhta hoon.",
            "visual": "Vlogger walks into the emotional crowd in selfie-cam mode, visibly moved — students crying, parents hugging kids. He gestures wide at the chaos behind him, voice slightly unsteady.",
        },
        "outro": {
            "line":   "Bhai, aaj yahan itna kuch dekha — ek baap roya, ek ladki ne maa ko hug kiya aur kuch bola nahi. Yeh sab mahino ki mehnat ka din hai. Aur jo log khush hain — ek cheez common hai unme — Professor Curious. Raat raat ko padhe, doubts clear kiye, akele baithe — lekin akele nahi the. Woh app wahan thi. Agar tumhara baccha bhi padh raha hai — link neeche diya hai. Ek baar try karwao.",
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
            "line":   "Bhai, Kota mein coaching ke baad yahan chai stall pe aa gaya hoon. Raat ke aath baj rahe hain — yeh bacche thake hue yahan baithke chai pi rahe hain. Yeh scene roz hota hai Kota mein — 12 ghante padh ke, thak ke, ek cup chai aur phir wapas room pe. Akele kamron mein — phir raat ko woh doubts jo class mein nahi poochhe, woh faces dekhte hain aankh band karke. Main aaj seedha poochhta hoon — yeh log jab akele hote hain raat ko, kya karte hain.",
            "visual": "Vlogger walks up to a chai stall where students sit in tired silence, turns selfie-cam on himself, points quietly at the exhausted students behind him. Steam from chai visible. Empathetic tone.",
        },
        "outro": {
            "line":   "Yaar, chai ki tarah — garm, aasaan, hamesha wahan — Professor Curious bhi aise hi hai. Roz raat ko yeh bacche chai peeke wapas jaate hain, aur phir akele baithte hain apne doubts ke saath. Tab Professor Curious wahan hota hai — raat ke 1 baje bhi, exam ke din bhi. Kota mein aise hi bachche survive karte hain. Link neeche hai.",
            "visual": "Vlogger holds a glass of chai toward camera with a quiet nod, students visible on bench behind. Then turns selfie-cam to himself walking away from the stall.",
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
            "line":   "Bhai, college gate pe hoon Kota mein — yeh woh bacche hain jo Kota survive kar chuke hain. Yeh JEE, NEET, woh sab lad ke aaye hain. Ek waqt tha jab yeh bhi wahi chhote kamron mein akele baithe the — raat ko rote the, doubts lete the, khud se ladte the. Aaj yahan hain. Main aaj inse poochhta hoon — actually kya hua tha Kota mein, kya kaam aaya, kya nahi aaya. Seedha, unki zubaani.",
            "visual": "Vlogger stands outside college gate in selfie-cam mode, points at students confidently streaming out, serious and empathetic look at camera.",
        },
        "outro": {
            "line":   "Bhai, yeh bacche Kota se lad ke yahan aaye hain. Inki kahaniyan sunaai — raat ko toot na, phir uthna, Professor Curious pe padh na, subah uthke exam dena. Yahi cycle thi inki. Professor Curious unka ek khamosh saathi tha — judge nahi kiya, thaka nahi, choda nahi. Jo abhi padh rahe hain — link neeche hai. Abhi.",
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
            "line":   "Bhai, Kota mein school pickup zone pe hoon. Yeh parents dekho — office se seedha aayen hain, kuch mums saree mein hain, kuch dads helmet utaar ke khade hain. Yeh sab ghar se nikal ke yahan aaye hain sirf ek baar bacche ka chehra dekhne ke liye. Poora saal yahan door door se dekhte hain — phone pe sunate hain 'theek hoon' — but aaj seedha dekhenge. Main aaj inse aur bacchon se poochhta hoon — ghar mein kya hota hai roz, kaise chalta hai sab.",
            "visual": "Vlogger walks through the parent pickup area in selfie-cam mode, points at waiting parents with helmets and car keys — empathetic, warm tone.",
        },
        "outro": {
            "line":   "Bhai, aaj yahan parents aur bacchon dono se baat ki. Ek cheez jo baar baar aaya — Professor Curious. Maa ne bola, bete ne bola, beti ne bola. Yeh app raat ko tab wahan hoti hai jab koi nahi hota — doubt clear karta hai, judge nahi karta, thakta nahi. Ghar mein koi padh raha hai — link neeche diya hai. Ek baar try karwao aaj.",
            "visual": "Vlogger walks back toward camera in selfie-cam, parent-child pairs visible behind him with emotional reunions. Warm smile, genuine thumbs up.",
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
Vlogger speaks directly to camera in Hindi. Full continuous monologue — dense, no pauses,
fills every second: "{e['line']}"

DURATION RULE: Vlogger speaks NON-STOP for the ENTIRE clip duration. Every second has
dialogue. No silent standing. No blank pauses. Voice carries throughout — energetic, urgent,
empathetic. Camera bobs naturally with his movement. Raw street vlog energy.
"""

def build_person_prompt(person: dict, scene: dict, product: str) -> str:
    response = person["response"].format(product=product)
    return f"""{scene['setting']}

INTERVIEW SUBJECT ONLY — CLOSE PORTRAIT:
The vlogger is completely off-camera. Only the {person['type']} is visible.
Subject fills 85% of the 9:16 frame — tight portrait from chest up.
Mic enters from the left edge of frame (vlogger's arm only, if visible at all).
Subject speaks directly and animatedly — natural Indian hand gestures, expressive face.
Background: the scene setting, slightly blurred, alive with people and movement.

The subject's question is asked by the vlogger off-screen: "{person['question']}"
Subject responds in Hindi: "{response}"

Visual action: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first half): Raw emotional problem — the struggle, the loneliness, the fear.
Subject's face carries real weight. Voice slightly unsteady. Let the pain breathe.
Act 2 (second half): "{product}" is the turning point. The name spoken CLEARLY and LOUDLY —
not mumbled, not rushed. A visible shift in the subject's face and energy at that moment.

DURATION RULE: Subject speaks CONTINUOUSLY for the ENTIRE clip. Dense, fast, emotional Hindi
dialogue from first frame to last. No gaps. No silence. Every second has words.
Natural Indian speech rhythm — overlapping thoughts, sentence fragments, genuine emotion.
Feels like a real candid street interview — unscripted, raw, completely authentic.
"""

def build_outro_prompt(scene: dict, product: str) -> str:
    o = scene["outro"]
    line = o["line"].format(product=product)
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera — continuous, dense monologue: "{line}"

DURATION RULE: Vlogger speaks NON-STOP for the ENTIRE clip. No silent pauses. No blank
standing. Genuine conviction — not a pitch. Thumbs up, eyebrows raised, eyes earnest.
End of street interview — same vlogger, same location, same continuous shoot.
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
