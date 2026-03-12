#!/usr/bin/env python3
"""
"क्यों नहीं हो रही पढ़ाई?" — Shame Series
5 ads built around one powerful insight:
The real reason kids stop studying is the shame of asking doubts.
When you ask, people mock you. Professor Curious never does.

Vlogger opens addressing parents directly: "Have you asked your kids what's really stopping them?"
Kids reveal: doubt पूछने पर मज़ाक उड़ता है — इसीलिए Professor Curious use करते हैं।

5 variations, 5 settings, same devastating truth.
Auto-stitches and sends to Slack after each.

Usage:
  source ~/.env_azure
  python3 run_shame_series.py
"""

import json
import os
import requests
import subprocess
import sys
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY       = os.environ.get("AZURE_OPENAI_API_KEY", "")
ENDPOINT      = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
MODEL         = os.environ.get("AZURE_SORA_MODEL", "sora-2")
BASE_URL      = f"{ENDPOINT}/openai/v1"
HEADERS       = {"api-key": API_KEY}
SLACK_URL     = "http://zpdev.zupay.in:8160/send"
SLACK_CHANNEL = "C0AHDH474LX"
PRODUCT       = "Professor Curious"
SECONDS       = 8
OUTPUT_ROOT   = Path.home() / ".openclaw" / "workspace" / "output" / "ugc-shame-series"

VLOGGER_LOCK = """CONTINUITY — SAME VLOGGER IN EVERY CLIP: Young Indian male, late 20s, slim build,
medium-brown skin, short neat black hair, clean-shaven. Navy blue round-neck t-shirt,
dark jeans. Holds a small black handheld reporter mic with round black foam ball top
in his right hand. Visible from chest up on the left edge of frame, slightly low angle."""

# ─────────────────────────────────────────────────────────────────────────────
# THE SERIES
# ─────────────────────────────────────────────────────────────────────────────

SHAME_SERIES = [

    # ── 1. CLASSROOM — Teacher embarrassed them publicly ─────────────────────
    {
        "id":     "classroom-shame",
        "run_id": "shame_01_classroom",
        "label":  "Classroom Shame (Teacher Ne Mazak Udaya)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, harsh school corridor light.
Outside a busy government school in Kota, between classes. Students in white uniforms rushing
through corridors, some sitting on stairs with books open but eyes distant.
The kind of school where 40 kids share one teacher and silence is mistaken for understanding.
Raw phone camera footage, no color grading, natural noise of a school mid-day.""",
            "establishing": {
                "line":   "क्यों नहीं हो रही पढ़ाई? यह सवाल हम बड़े हमेशा पूछते हैं। पर क्या हमने कभी बच्चों से पूछा — कि दिक्कत क्या है? आइए पूछते हैं।",
                "visual": """Vlogger stands in school corridor, students rushing past. He speaks directly to camera —
not entertainment energy, documentary energy. Serious. He turns and walks toward a group of kids
sitting quietly on stairs with books, looking like they're studying but clearly not absorbing anything.
Camera steady — this is an investigation, not a vlog.""",
            },
            "outro": {
                "line":   "बच्चा नहीं पढ़ रहा — इसलिए नहीं कि वो नहीं चाहता। इसलिए कि पूछने पर डर लगता है। Professor Curious वो डर खत्म करता है। Link नीचे।",
                "visual": """Vlogger stands alone in now-empty corridor, afternoon light slanting through windows.
Looks at camera quietly — this wasn't a fun shoot. He means this.
Slow, deliberate thumbs up. Not a pitch — a conclusion drawn from what he just heard.""",
            },
            "people": [
                {
                    "id": "p01", "type": "school boy", "age": "13-14",
                    "emotion": "humiliated memory, then quiet resolve",
                    "question": "पढ़ाई में क्या दिक्कत है — सच में बताओ?",
                    "response": "Sir से एक बार doubt पूछा था — simple सा था मेरे लिए। सर ने पूरी class के सामने बोला 'यह तो basic है, class 5 में पढ़ा था।' सब हंसे। उस दिन से हाथ नहीं उठाया। पर doubt तो रहते हैं। Professor Curious से पूछता हूं अब — वो कभी नहीं हंसा आज तक।",
                    "visual": """Boy looks down briefly — the memory is still there, still stings.
First 3-4 seconds: voice low, reliving the classroom moment. The shame is visible on his face.
At 'Professor Curious से पूछता हूं' his shoulders drop — relief, not pride.
Says the name clearly, looking at vlogger. Simple and real.""",
                },
                {
                    "id": "p02", "type": "school girl", "age": "12-13",
                    "emotion": "matter-of-fact about something that shouldn't be normal",
                    "question": "Class में doubt पूछने में डर लगता है?",
                    "response": "हां। एक बार पूछा — पीछे से तीन बच्चे हंसे। Teacher ने कुछ नहीं बोला उन्हें। मैंने decide कर लिया — class में नहीं पूछूंगी। घर आके Professor Curious खोलती हूं। वो समझाता है, मुझे stupid नहीं feel कराता। इसीलिए use करती हूं।",
                    "visual": """Girl is matter-of-fact — this is just how school works, she's accepted it. That makes it worse.
'Teacher ने कुछ नहीं बोला उन्हें' — delivered flatly, no anger. Just a fact.
At 'Professor Curious' she becomes slightly more animated — this is the part that actually works.
Says the name clearly, with the quiet confidence of someone who found a real solution.""",
                },
                {
                    "id": "p03", "type": "school boy", "age": "14-15",
                    "emotion": "angry then grateful",
                    "question": "पढ़ाई में कहां रुकते हो?",
                    "response": "Doubt पर। और doubt पूछने पर। दोनों जगह। Class में पूछो तो बच्चे बोलते हैं 'अरे इतना नहीं पता?' — जैसे तुम पहले से सब जानते हो तो school क्यों आए। Professor Curious को यह नहीं पता कि मुझे क्या नहीं आता था पहले। वो बस समझाता है। कभी judge नहीं किया।",
                    "visual": """Boy has quiet anger — 'तुम पहले से सब जानते हो तो school क्यों आए' is his impersonation of classmates, bitter.
Then genuinely softens at Professor Curious. Says the name with something close to gratitude.
'कभी judge नहीं किया' — looking straight at camera. That's the whole thing.""",
                },
            ],
        },
    },

    # ── 2. COACHING — 200 students, public shame ──────────────────────────────
    {
        "id":     "coaching-shame",
        "run_id": "shame_02_coaching",
        "label":  "Coaching Shame (200 Bachche Dekh Rahe The)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, 7pm, streetlights on.
Outside a large JEE/NEET coaching centre in Kota — hundreds of students streaming out.
The scale is overwhelming — this isn't a classroom, it's a factory. Students in rows,
competitive, tired, anonymous in the crowd. Raw phone camera footage, no color grading,
the hum of a thousand ambitions in one building.""",
            "establishing": {
                "line":   "यह Kota है। यहां एक class में 200 बच्चे हैं। एक teacher है। मैं जानना चाहता हूं — इन बच्चों से — क्या इनसे कभी पूछा गया कि पढ़ाई में दिक्कत क्या है?",
                "visual": """Vlogger stands at the coaching exit as hundreds of students pour out.
He gestures at the scale — the crowd, the building, the sheer number of kids.
Speaks to camera seriously. 'क्या इनसे कभी पूछा गया?' — a real question, not rhetorical.
He moves through the crowd to find someone willing to talk.""",
            },
            "outro": {
                "line":   "200 बच्चों के बीच एक बच्चा अकेला बैठा होता है — doubt के साथ। Professor Curious उसके साथ बैठता है। Link नीचे।",
                "visual": """Vlogger stands outside as last students leave. Building lights turning off behind him.
Looks at camera. 'अकेला बैठा होता है' — he says it like he just understood something.
Quiet thumbs up. Walks away into the dark street.""",
            },
            "people": [
                {
                    "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                    "emotion": "one specific memory that changed everything",
                    "question": "Class में doubt पूछते हो?",
                    "response": "एक बार पूछा था। 200 बच्चे थे। Sir ने answer दिया — but साथ में बोला 'यह previous class का material है।' 200 बच्चों ने मुझे देखा। उस दिन के बाद कभी नहीं पूछा। Professor Curious को नहीं पता कि मेरे साथ 199 और बच्चे हैं। वो सिर्फ मुझसे बात करता है।",
                    "visual": """Boy recounts this with painful precision — '200 बच्चे थे' is a specific number he remembers.
The silence after '200 बच्चों ने मुझे देखा' is long enough to feel the humiliation.
At 'Professor Curious को नहीं पता' he almost smiles — the privacy of it is the point.
'वो सिर्फ मुझसे बात करता है' — says it clearly, slowly. That's everything.""",
                },
                {
                    "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                    "emotion": "resigned wisdom of someone who figured out a workaround",
                    "question": "Coaching में कितना समझ आता है?",
                    "response": "Class में? 60-70 percent। बाकी doubt रह जाता है। पर class के बाद Sir के पास जाओ तो line में 50 बच्चे हैं। WhatsApp पर पूछो तो जवाब नहीं आता। Professor Curious पर पूछती हूं — instantly जवाब। और कभी नहीं लगा कि stupid question था।",
                    "visual": """Girl is practical, not emotional — she's solved this problem systematically.
Lists the failed options flatly: line of 50, no WhatsApp reply.
Says 'Professor Curious पर पूछती हूं' like the obvious solution she found.
'Stupid question था' — she says this looking directly at camera. That word 'stupid' lands.""",
                },
                {
                    "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                    "emotion": "frank and a little bitter",
                    "question": "यहां doubt clear करना possible है?",
                    "response": "Officially? हां। Actually? नहीं। Class में hand raise करो — Sir देखता है, next question पर चला जाता है। Batch system है यहां — तुम्हारा doubt उनका time नहीं है। Professor Curious का पूरा time मेरा है। वो रुकता है। वो explain करता है। वो judge नहीं करता।",
                    "visual": """Boy is frank, a little bitter about the system — not dramatic, just honest.
'तुम्हारा doubt उनका time नहीं है' is said quietly, like a truth he had to accept.
'Professor Curious का पूरा time मेरा है' — he straightens slightly when he says this.
Says the name clearly. The contrast is everything.""",
                },
            ],
        },
    },

    # ── 3. HOME — Parent said "इतना भी नहीं पता?" ───────────────────────────
    {
        "id":     "home-shame",
        "run_id": "shame_03_home",
        "label":  "Ghar Ki Sharam (Parent Ne Bola Itna Bhi Nahi Pata?)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Evening, warm indoor-outdoor light.
Outside a residential colony in Kota — student housing area, small flats, families.
Kids visible at windows with books, some sitting on colony steps after school.
The domestic Kota — the part no one talks about. Raw phone camera footage, no color grading.""",
            "establishing": {
                "line":   "क्यों नहीं हो रही पढ़ाई? Parents हमेशा सोचते हैं — बच्चा पढ़ता नहीं। पर क्या कभी पूछा — घर में पूछने पर क्या होता है? आइए जानते हैं।",
                "visual": """Vlogger stands in the colony, residential buildings behind him.
Speaks directly to camera — this one is about parents. Slightly uncomfortable energy —
he's about to say something parents don't want to hear.
Turns and approaches kids sitting on colony steps.""",
            },
            "outro": {
                "line":   "घर में भी नहीं पूछ सकते। School में भी नहीं। Professor Curious एक ऐसी जगह है जहां कोई नहीं हंसता। Link नीचे।",
                "visual": """Vlogger faces camera, colony lights coming on behind him as evening falls.
'घर में भी नहीं। School में भी नहीं।' — he says this like someone reading the full picture.
Quiet. Says 'Professor Curious' with weight. Slow nod. Walks inside.""",
            },
            "people": [
                {
                    "id": "p01", "type": "school girl", "age": "13-14",
                    "emotion": "confessing something she's never said out loud",
                    "question": "घर पर doubt पूछती हो?",
                    "response": "पहले पूछती थी। Papa से पूछा एक बार — Maths का formula समझ नहीं आया था। उन्होंने बोला 'यह class 7 का है, तुम class 9 में हो।' उस tone में — जैसे मैंने कोई गलती की हो। उस दिन से नहीं पूछती। Professor Curious से पूछती हूं। वो वही tone नहीं है।",
                    "visual": """Girl speaks quietly — this is a confession, not a complaint.
She imitates her father's tone briefly — not mean about it, just honest.
'उस दिन से नहीं पूछती' — said with a finality that's sad.
'वो वही tone नहीं है' — says this looking at the ground then up at camera. Completely real.""",
                },
                {
                    "id": "p02", "type": "school boy", "age": "14-15",
                    "emotion": "protective of his parents but telling the truth",
                    "question": "घर पर doubt किससे पूछते हो?",
                    "response": "Mummy-Papa दोनों काम करते हैं। थके होते हैं। एक बार रात को पूछा — Mummy ने frustrated होके बोला 'तुम school किसलिए जाते हो?' वो गलत नहीं थीं — थकी थीं। पर मैं भी नहीं समझा था। Professor Curious से पूछा — उसने समझाया। किसी को burden नहीं हुआ।",
                    "visual": """Boy is careful — he defends his mother even while telling the story. That's the complexity.
'वो गलत नहीं थीं — थकी थीं' is said with real understanding. He's not blaming her.
'किसी को burden नहीं हुआ' — this is the real insight. Says 'Professor Curious' gently, clearly.""",
                },
                {
                    "id": "p03", "type": "school girl", "age": "12-13",
                    "emotion": "innocent and heartbreaking",
                    "question": "पढ़ाई में कौन help करता है तुम्हें?",
                    "response": "Professor Curious। घर पर Didi हैं — पर वो अपनी पढ़ाई में busy हैं। Papa से पूछो तो वो बोलते हैं 'teacher से पूछो।' Teacher से पूछो तो बोलते हैं 'घर पर पूछो।' Professor Curious ने कभी नहीं बोला किसी और से पूछो। वो खुद बताता है।",
                    "visual": """Girl lists the loop she's stuck in with childlike matter-of-factness — Didi, Papa, Teacher, back to Papa.
'Professor Curious' is her immediate first answer — before she even explains why.
The loop she describes is devastating precisely because she describes it without self-pity.
'वो खुद बताता है' — simple, clear, final. Says the name with complete trust.""",
                },
            ],
        },
    },

    # ── 4. FRIEND GROUP — Social shame, mockery ───────────────────────────────
    {
        "id":     "friend-shame",
        "run_id": "shame_04_friends",
        "label":  "Dosto Ki Sharam (Yaar Ne Mazak Udaya)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Afternoon, bright harsh light.
School canteen area or ground outside school — kids in groups, eating, talking, laughing.
The social universe of school where who-knows-what defines everything.
Some kids on the edge of groups, slightly apart. Those are the ones we need to talk to.
Raw phone camera footage, no color grading, noisy school background.""",
            "establishing": {
                "line":   "पढ़ाई नहीं हो रही। सब बोलते हैं — बच्चा distract है, phone पर है, serious नहीं है। पर क्या किसी ने पूछा — दोस्तों के बीच क्या होता है जब कुछ समझ नहीं आता? आइए पूछते हैं।",
                "visual": """Vlogger stands at the edge of the school ground, groups of kids visible behind him.
He scans the crowd — not looking for the happy group, looking for the kid on the edge.
Speaks to camera with a quiet urgency. 'दोस्तों के बीच क्या होता है?' — he knows this is something.""",
            },
            "outro": {
                "line":   "यह नहीं पता — यह कहना आज सबसे मुश्किल बात है। Professor Curious के साथ — कोई नहीं सुनता। सिर्फ समझाता है। Link नीचे।",
                "visual": """Vlogger stands alone on the emptying school ground. Groups dispersing behind him.
'यह नहीं पता — यह कहना आज सबसे मुश्किल बात है' — he says this slowly, like a diagnosis.
Says 'Professor Curious' with quiet conviction. Turns and walks away into the school.""",
            },
            "people": [
                {
                    "id": "p01", "type": "school boy", "age": "14-15",
                    "emotion": "trying to seem unbothered but clearly bothered",
                    "question": "दोस्तों से doubt पूछते हो?",
                    "response": "पहले पूछता था। एक बार group में बोला 'यार यह formula समझ नहीं आया' — सबने एक साथ react किया 'क्या यार, इतना basic है।' Laugh track जैसा था। उस दिन से WhatsApp group में silent हूं पढ़ाई में। Professor Curious से पूछता हूं — वो अकेले में समझाता है। कोई नहीं देखता।",
                    "visual": """Boy tries to laugh it off at first — 'laugh track जैसा था' is his defense mechanism.
But the wound is visible. 'उस दिन से WhatsApp group में silent हूं' — the consequence is real.
'कोई नहीं देखता' — he says this with genuine relief. The privacy matters.
Says 'Professor Curious' clearly. The name = safety.""",
                },
                {
                    "id": "p02", "type": "school girl", "age": "13-14",
                    "emotion": "sharp and direct — she figured this out early",
                    "question": "पढ़ाई में stuck होती हो तो क्या करती हो?",
                    "response": "Professor Curious। सीधे। दोस्तों से पूछना बंद कर दिया बहुत पहले। वो judge नहीं करते जानबूझकर — पर जब तुम नहीं जानते कुछ और वो जानते हैं — तो जो face बनाते हैं — वो काफी है। Professor Curious का कोई face नहीं होता। वो बस समझाता है।",
                    "visual": """Girl answers immediately — 'Professor Curious। सीधे।' No hesitation, no story needed first.
Then explains. 'जो face बनाते हैं' — she knows exactly which face. We all do.
'Professor Curious का कोई face नहीं होता' — she says this with a small, knowing smile.
Says the name twice, both times clearly.""",
                },
                {
                    "id": "p03", "type": "school boy", "age": "15-16",
                    "emotion": "philosophical — has thought about this",
                    "question": "School में सबसे बड़ी problem क्या है पढ़ाई की?",
                    "response": "यह admit करना कि तुम नहीं जानते। यह सबसे hard है। Class में नहीं बोल सकते। Dosto को नहीं बोल सकते। Parents को नहीं बोल सकते — वो worry करेंगे। Professor Curious को बोल सकते हो। वो तुम्हारी सबसे बड़ी weakness जानता है — और कभी किसी को नहीं बताता। इसीलिए use करता हूं।",
                    "visual": """Boy is genuinely thoughtful — this is a conclusion he's arrived at over time.
'यह admit करना कि तुम नहीं जानते' — said slowly, with real weight.
The list of people you can't tell builds the isolation.
'Professor Curious को बोल सकते हो' — lands like the first door that's actually open.
Says the name clearly, deliberately. This is his real answer.""",
                },
            ],
        },
    },

    # ── 5. LATE NIGHT ALONE — No one left to ask ─────────────────────────────
    {
        "id":     "alone-shame",
        "run_id": "shame_05_alone",
        "label":  "Raat Ko Akele (Koi Nahi Tha Poochne Ko)",
        "scene": {
            "setting": """Raw handheld smartphone vlog footage, 9:16 vertical. Late night, 10:30pm.
Kota — outside a student hostel building. One or two windows still lit. A student sits on
the hostel steps, books open, phone in hand — clearly stuck and has been for a while.
The street is empty. The city has gone to sleep. This student hasn't.
Raw phone camera footage, low-light grain, intimate and very quiet.""",
            "establishing": {
                "line":   "रात के साढ़े दस बज रहे हैं। Kota में। एक बच्चा बाहर बैठा है। किताबें खुली हैं। पर पढ़ाई नहीं हो रही। मैंने सोचा — पूछते हैं। क्या दिक्कत है? किससे पूछें? क्या जवाब मिलेगा?",
                "visual": """Vlogger approaches the student from the dark street — hushed, careful.
Camera barely visible in low light. He whispers to the camera first —
'एक बच्चा बाहर बैठा है' — like he doesn't want to disturb the moment.
Sits down nearby before asking. Completely present.""",
            },
            "outro": {
                "line":   "रात को साढ़े दस बजे — कोई नहीं होता। Professor Curious होता है। हमेशा। Link नीचे।",
                "visual": """Vlogger stands alone on the empty hostel steps after the student has gone inside.
One lit window above — the student studying now.
'कोई नहीं होता। Professor Curious होता है। हमेशा।' — three sentences, three beats. Deliberate.
He looks up at the lit window once. Slow thumbs up. Walks away into the dark.""",
            },
            "people": [
                {
                    "id": "p01", "type": "JEE aspirant boy", "age": "17-18",
                    "emotion": "exhausted, running out of options, found one",
                    "question": "इतनी रात को बाहर क्यों बैठे हो?",
                    "response": "अंदर roommate सो गया। Doubt था — Physics का। उसे disturb नहीं करना था। Teacher को इस वक्त नहीं पूछ सकते। Dosto ko message किया — seen. Parents को नहीं करता — वो worry करते हैं। Professor Curious खोला। समझा दिया। अब अंदर जाऊंगा।",
                    "visual": """Boy is very tired — every person he could ask is crossed off the list.
He lists them with quiet resignation: roommate, teacher, friends (seen), parents.
At 'Professor Curious खोला' — simple, no drama. It was just the next thing.
'समझा दिया। अब अंदर जाऊंगा।' — problem solved, going to sleep. Says the name clearly.""",
                },
                {
                    "id": "p02", "type": "NEET aspirant girl", "age": "17-18",
                    "emotion": "found something that changed her nights",
                    "question": "रात को stuck होती हो तो क्या करती हो?",
                    "response": "पहले रोती थी। सच में। रात को doubt आता था, कोई नहीं होता था, तो बस रो लेती थी और सो जाती थी। फिर Professor Curious मिला। अब रोती नहीं — पूछती हूं। वो जवाब देता है। रात अब उतनी लंबी नहीं लगती।",
                    "visual": """Girl says 'पहले रोती थी' with complete calm — it was true, it's past.
The specificity of 'रो लेती थी और सो जाती थी' is devastating in its routine quality.
At 'Professor Curious मिला' — a genuine before/after on her face.
'रात अब उतनी लंबी नहीं लगती' — says this looking at the lit hostel windows.
Says 'Professor Curious' clearly. The name = the turning point of her nights.""",
                },
                {
                    "id": "p03", "type": "JEE aspirant boy", "age": "18-19",
                    "emotion": "clear-eyed, direct, distilled truth",
                    "question": "Kota में सबसे अकेला कब लगता है?",
                    "response": "जब doubt हो और कोई न हो पूछने को। Class में नहीं पूछ सकते — हंसते हैं। Coaching में नहीं पूछ सकते — time नहीं है। घर पर नहीं पूछ सकते — बताना नहीं चाहते कि struggle हो रहा है। Professor Curious एकमात्र जगह है जहां कोई नहीं हंसता, कोई नहीं थकता, और जवाब हमेशा मिलता है।",
                    "visual": """Boy is clear-eyed and direct — he's thought about this completely.
The three places he can't ask are listed without bitterness, just truth.
'Professor Curious एकमात्र जगह है' — said like a mathematical conclusion.
Says the name slowly, clearly, looking straight at the camera.
'जवाब हमेशा मिलता है' — the last line. That's all that matters at 11pm in Kota.""",
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

TONE: This is not entertainment — this is a social investigation.
The vlogger is genuinely asking a hard question that parents need to hear.
Documentary energy. First 2 seconds must feel like someone is about to reveal something true.
"""

def build_person_prompt(person: dict, scene: dict) -> str:
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: Vlogger sits or stands close to {person['type']}, age {person['age']}.

Vlogger asks in Hindi: "{person['question']}"
Person responds in Hindi: "{person['response']}"

Visual direction: {person['visual']}

CLIP PACING — TWO ACTS:
Act 1 (first 3-4 seconds): The shame — the specific moment someone mocked them for asking.
The humiliation of not knowing. Let the audience feel it. Do not rush to the solution.
Act 2 (next 3-4 seconds): "{PRODUCT}" — the place where no one laughs.
The name spoken clearly, deliberately, out loud. A visible shift — relief, not triumph.

CORE EMOTION: The shame of not knowing is real in India.
"{PRODUCT}" is the first place that treats a question as a question, not a failure.
This must be felt, not performed.
"""

def build_outro_prompt(scene: dict) -> str:
    o = scene["outro"]
    return f"""{scene['setting']}

{VLOGGER_LOCK}

Scene: {o['visual']}
Vlogger speaks in Hindi to camera: "{o['line']}"

He's not selling. He just heard something true today.
"{PRODUCT}" is the conclusion — earned, not pitched.
"""

# ── Azure Sora API (same helpers as other scripts) ────────────────────────────

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

def generate_clip(prompt: str, clip_id: str, out_path: Path) -> None:
    print(f"    [submit] {clip_id} ...", flush=True)
    video_id = submit_job(prompt, clip_id)
    print(f"    [submit] {clip_id} → {video_id}", flush=True)
    poll_job(video_id, clip_id)
    download_video(video_id, out_path)

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
    print(f"    [stitch] → {output_path.name}", flush=True)

def send_to_slack(video_path: Path, label: str, exp_id: str) -> None:
    print(f"    [slack] Sending {video_path.name} ...", flush=True)
    helper = Path(__file__).resolve().parents[2] / "common" / "send_slack.py"
    result = subprocess.run([
        "python3", str(helper),
        "--channel-id", SLACK_CHANNEL,
        "--text", f"🎬 *Shame Series — {label}* (`{exp_id}`)\n_क्यों नहीं हो रही पढ़ाई? — Doubt पूछने पर मज़ाक उड़ता है। Professor Curious नहीं उड़ाता।_",
        "--file", str(video_path),
    ], capture_output=True, text=True)
    resp = result.stdout.strip() or result.stderr.strip()
    print(f"    [slack] {'✓ Sent' if result.returncode == 0 else '✗ Failed: ' + resp[:100]}", flush=True)

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
    print(f"  Run ID : {run_id}  |  Clips: {total}", flush=True)
    print(f"{'='*60}", flush=True)

    clip_paths = []

    print(f"\n  [1/{total}] Establishing — HOOK", flush=True)
    out = clips_dir / "clip_01_establishing.mp4"
    generate_clip(build_establishing_prompt(scene), "establishing", out)
    clip_paths.append(out)

    for i, person in enumerate(people, start=2):
        print(f"\n  [{i}/{total}] {person['type']} ({person['emotion']})", flush=True)
        out = clips_dir / f"clip_{i:02d}_{person['id']}.mp4"
        generate_clip(build_person_prompt(person, scene), person["id"], out)
        clip_paths.append(out)

    print(f"\n  [{total}/{total}] Outro", flush=True)
    out = clips_dir / f"clip_{total:02d}_outro.mp4"
    generate_clip(build_outro_prompt(scene), "outro", out)
    clip_paths.append(out)

    merged = out_dir / f"{run_id}_merged.mp4"
    print(f"\n  [stitch] Merging {total} clips ...", flush=True)
    stitch_clips(clip_paths, merged)
    send_to_slack(merged, label, exp["id"])
    print(f"\n  ✓ DONE: {merged}\n", flush=True)

def main():
    if not API_KEY or not ENDPOINT:
        sys.exit("ERROR: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")

    print(f"\n{'#'*60}")
    print(f"  Shame Series — Professor Curious")
    print(f"  क्यों नहीं हो रही पढ़ाई?")
    print(f"  5 ads × 5 clips × {SECONDS}s — auto-sends to Slack")
    print(f"{'#'*60}\n")

    for i, exp in enumerate(SHAME_SERIES, 1):
        print(f"\n[Ad {i}/5] {exp['label']}", flush=True)
        try:
            run_experiment(exp)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", flush=True)

    print(f"\n{'#'*60}")
    print(f"  Shame Series complete. Check Slack.")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
