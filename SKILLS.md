# UGC AI Ads Engine — All Skills & Video Formats

> Complete reference for every video creation style built for Professor Curious.
> Last updated: 2026-03-08

---

## Overview

| # | Skill / Format | Market | Model | Scripts | Status |
|---|---------------|--------|-------|---------|--------|
| 1 | India Street Interview | India | Sora 2 | 4 scripts | ✅ Built & tested |
| 2 | US College Interview | US | Sora 2 | 7+ scripts | ✅ Built & tested |
| 3 | Reaction Hooks (Sora) | US | Sora 2 | 2 scripts | ✅ Built & tested |
| 4 | StudyTok Hooks | Any | Sora 2 | 2 scripts | ✅ Built & tested |
| 5 | Livestream Call Format | US | Veo 3 | 1 script | 🔨 Built, not tested |
| 6 | Video Editor (Post-processing) | Any | ffmpeg | 2 scripts | ✅ Built & tested |
| 7 | Professor Curious Street (older) | India | Sora 2 | 1 script | ✅ Older version |

---

## 1. India Street Interview

**Folder:** `ugc-street-interview/`
**Concept:** Raw handheld street vlog. Young Indian male vlogger outside Kota coaching centres, interviewing JEE/NEET students. Two-act structure: Act 1 emotional pain → Act 2 Professor Curious as turning point.

### Scripts

#### `run.py` — Core flexible runner
```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-street-interview/scripts/run.py \
  --product "Professor Curious" --scene kota-coaching --run-id kota_v1
```

**Args:**
- `--scene` — scene type (default: `kota-coaching`)
- `--num-people` — 1–5 interview clips
- `--seconds` — 4, 8, or 12s per clip
- `--person-ids` — pick specific people e.g. `p01 p03`
- `--no-stitch` — skip merge

**Output:** `~/.openclaw/workspace/output/ugc-street-interview/<run-id>/<run-id>_merged.mp4`

**7 Scenes:**

| Scene | Setting | Mood |
|-------|---------|------|
| `kota-coaching` *(default)* | Coaching gate, 7–8pm, streetlights | Quiet desperation, heavy bags, dark circles |
| `school-gate` | School gate post-exam | Chaotic, kids streaming out |
| `coaching-centre` | Same energy as kota-coaching (alt prompts) | Evening, tired faces, chai stalls |
| `results-day` | Board results morning | Crying, jumping, parents hugging |
| `chai-stall` | Roadside chai stall after coaching | Intimate, decompressing, steam rising |
| `college-gate` | Kota veterans now in college | Reflective, earned confidence |
| `parent-pickup` | Parent pickup zone, families | Warm, fathers crying, mothers proud |

Each scene has **5 pre-written people** with specific: type, age, emotion, Hindi question, Hindi response, visual direction.

---

#### `run_experiments.py` — 5 high-concept Kota moments (auto-sends to Slack)
```bash
python3 ~/ugc-ai-ads-engine/ugc-street-interview/scripts/run_experiments.py
```

Each experiment has its own unique scroll-stopping hook:

| ID | Hook | Setting |
|----|------|---------|
| `exp_01_ek_raat` | 11:30pm, one student alone on dark steps outside shuttered coaching | Night street, single flickering tube light |
| `exp_02_bag_pack` | Bag packed at Kota station, train in 2 hours, almost quit | Kota Junction railway platform |
| `exp_03_rank_wala` | AIR 89 mock topper surrounded by crowd | Golden hour outside coaching, small crowd forms |
| `exp_04_pehla_din` | First day in Kota — parents just drove off 10 minutes ago | Student hostel morning, families saying goodbye |
| `exp_05_mock_result` | Mock test results dropped 5 minutes ago — full emotional spectrum | Harsh afternoon, students on phones, one sitting on ground |

**Format:** 5 clips (establishing + 3 interviews + outro) × 8s = ~40s each. Auto-stitches + sends to Slack.

---

#### `run_shame_series.py` — 5 shame-angle ads (auto-sends to Slack)
```bash
python3 ~/ugc-ai-ads-engine/ugc-street-interview/scripts/run_shame_series.py
```

**Core insight:** "The real reason kids stop studying is shame of asking doubts. When you ask, teachers mock you. Professor Curious never does."

**Vlogger addresses parents:** "क्यों नहीं हो रही पढ़ाई? Have you asked your kids what's really stopping them?"

| ID | Setting | Core moment |
|----|---------|-------------|
| `shame_01_classroom` | School corridor | Teacher humiliated boy in front of class — he never raised his hand again |
| `shame_02_coaching` | Kota coaching, 200 students | One doubt question, 200 kids stared — never asked again |
| `shame_03_home` | Home setting | Parents compare to neighbours' kids every time they ask for help |
| `shame_04_friends` | Friend group | Friends mocked the "easy" doubt — now studies alone silently |
| `shame_05_alone` | Alone at night | No one to ask — teacher asleep, friends asleep, Professor Curious isn't |

**Format:** 5 clips × 8s = ~40s each. Auto-stitches + sends to Slack.

---

#### `run_hand_vlog.py` — Hand-only vlogger variant
**Problem:** Sora can't maintain vlogger face consistency across clips.
**Solution:** Only the vlogger's hand (holding mic) is shown at bottom-left edge of frame. No face, no torso — voice-only host.

```bash
python3 ~/ugc-ai-ads-engine/ugc-street-interview/scripts/run_hand_vlog.py
```

---

### Creative Rules (non-negotiable)
1. **Professor Curious always named clearly** — spoken out loud, unmistakably, not mumbled
2. **Two-act structure** — Act 1 (3–4s) raw emotional pain, Act 2 (3–4s) PC as turning point
3. **All India scenes set in Kota, Rajasthan** — explicitly in every prompt
4. **VLOGGER_LOCK** — same character description in every clip prompt (slim Indian male, navy t-shirt, black reporter mic)
5. **Hook in first 2 seconds** — establishing shot must be scroll-stopping

### Known Issues
- `run.py` stitch uses `-c copy` — no 96kHz audio fix (Slack may not play)
- `run.py` doesn't auto-send to Slack
- Sora face consistency across clips is imperfect — VLOGGER_LOCK helps but doesn't guarantee

---

## 2. US College Interview

**Folder:** `ugc-us-college-interview/`
**Concept:** Vlogger outside elite US universities asking "What did you use to get into Harvard?" Most students name Professor Curious. Some mention Khan/Quizlet first, then come around (authenticity play). FOMO social proof angle.

### Scripts

#### `run.py` — Core flexible runner
```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-us-college-interview/scripts/run.py \
  --product "Professor Curious" --scene harvard --run-id harvard_v1
```

**6 Scenes:**

| Scene | Location | Vibe |
|-------|----------|------|
| `harvard` *(default)* | Johnston Gate, Cambridge MA, autumn | Prestigious, emotional, golden leaves |
| `mit` | Massachusetts Ave entrance | Analytical, intense, problem-solvers |
| `stanford` | White Plaza, California | Warm, casual, West Coast optimism |
| `yale` | Phelps Gate, gothic architecture | Literary, reflective, thoughtful |
| `princeton` | Nassau Hall gate | Historic, formal, legacy-aware |
| `elite-campus` | Generic elite university | Flexible, no specific institution |

**5 person archetypes per scene:**
- p01: Pure PC advocate
- p02: "Tried Khan Academy → switched to Professor Curious"
- p03: Social proof — "my whole dorm used it"
- p04: "Quizlet for vocab, but PC for understanding"
- p05: Matter-of-fact — "easy answer"

---

#### `run_comparison.py` — 5 vs-competitor ads
5 ads directly positioning PC against specific competitors:

| ID | Competitor | Angle |
|----|-----------|-------|
| `us_cmp_01_vs_khan` | Khan Academy | "Khan explains at you. PC explains with you." |
| `us_cmp_02_vs_chegg` | Chegg | "Chegg gives you the answer. PC makes you understand." |
| `us_cmp_03_vs_chatgpt` | ChatGPT | "ChatGPT makes stuff up. PC is built for learning." |
| `us_cmp_04_vs_tutors` | Private tutors | "$80/hr vs free. Same result." |
| `us_cmp_05_vs_quizlet` | Quizlet | "Quizlet helps you memorize. PC helps you understand." |

---

#### `run_vs_gauth.py` / `run_vs_gauth_2/3/3b.py` — Gauth vs PC (logo overlays)
3 ads at MIT, Stanford, Harvard with logo bug overlay (Gauth logo vs PC logo).

---

#### Helper scripts
- `run_us_formats.py` — additional US format variants
- `run_street_direct.py` — direct street style for US
- `run_hand_vlog.py` — hand-only vlogger, US campus
- `add_hooks.py` / `add_hooks_text_only.py` — hook variations
- `rerun_gauth_02.py`, `recover_street_05.py`, `redo_comparison_hooks.py` — targeted reruns

---

### Assets
```
~/ugc-ai-ads-engine/assets/
├── pc_logo.png      ← 512×512 Professor Curious (from App Store)
└── gauth_logo.png   ← 512×512 Gauth (from App Store)
```

---

## 3. Reaction Hooks (Sora)

**Folder:** `ugc-reaction/`
**Concept:** Selfie-cam reaction video. WE ARE the phone camera. Girl picks up phone, sees Professor Curious notification, jaw drop shock. Raw TikTok draft style.

### Key POV rule
> The recording camera IS the phone being picked up. The FRAME must physically move — lurch, tilt, spin. Do NOT show a person looking at a separate phone.

### Scripts

#### `run_hooks_us.py` — 10 US Sora reaction hooks
```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-reaction/scripts/run_hooks_us.py
```

10 hooks across varied settings and emotions (library, coffee shop, dorm, etc.).

#### `run_veo_hooks.py` — 5 Veo 3 reaction hooks (Gemini pipeline)
Character-consistent pipeline: nano-banana-pro portrait → Veo 3 video.

```bash
python3 ~/ugc-ai-ads-engine/ugc-reaction/scripts/run_veo_hooks.py
```

> **Note:** Sora blocks realistic human images (`people-in-user-uploads` policy). Use Veo 3 for character-consistent video.

#### `run_reaction.py` — 4-clip sequential reaction format

#### `test_consistent_char.py` — Character consistency test

**Output:** `~/.openclaw/workspace/output/ugc-sora-hooks/` and `ugc-veo-hooks/`

---

### Prompt engineering rules (Sora reaction)
- `"WE ARE the phone camera"` — sets POV
- Beat-by-beat timing: `0-2s: ... 2-4s: ...`
- Camera motion explicit per beat: lurch, tilt, spin, autofocus pulse
- `"iPhone 15 Pro front camera in selfie mode"`
- `"no makeup, messy hair, not model-pretty"`
- `"flat colors no LUT"`, `"raw phone audio background hiss"`

---

## 4. StudyTok Hooks

**Folder:** `ugc-studytok-hooks/`
**Concept:** Snapchat/TikTok style. Sora 2 reaction clip → Snapchat-style caption overlay → full Professor Curious demo video (muted) → trending audio → Slack.

### Scripts

#### `run_studytok_hooks.py` — Full pipeline (5 hooks)
```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-studytok-hooks/scripts/run_studytok_hooks.py
```

**Pipeline:**
1. Generate 8s reaction clip via Sora 2
2. Scale to 720×1280
3. Add Snapchat-style caption bar (top 8% of frame, dark semi-transparent, white text + emoji)
4. Append full demo video (muted)
5. Add trending audio over the whole thing
6. Send to Slack

**Demo clips used:**
- `761f2bb3b84a4003a9744b4e5b45a4f2.MP4` (27.9s)
- `958c1b7bb7d4413d8276bfaa828a58d8.MP4` (24.6s)

**Audio pool (dynamic by total video length):**
| Length | Audio |
|--------|-------|
| < 35s | `audio_01_oh_no.mp3` — Oh No by Kreepa |
| 35–55s | `audio_03_cupid.mp3` — Cupid by FIFTY FIFTY |
| > 55s | `audio_02_aperture.mp3` — Harry Styles Aperture |

**Caption rules:**
- Position: top 8% of frame (`bar_y = int(height * 0.08)`)
- Font: SF Pro / Helvetica for text, **Apple Color Emoji** for emoji
- Background: dark semi-transparent bar full width

---

#### `run_reaction_experiments.py` — 8 pure reaction experiments
No caption, no demo, no stitch. Just the raw Sora reaction clip to test settings and motion.

```bash
python3 ~/ugc-ai-ads-engine/ugc-studytok-hooks/scripts/run_reaction_experiments.py
```

| # | Setting | Motion |
|---|---------|--------|
| exp_01 | Cafe golden hour | Face-down on table → flipped & lifted, frame spins |
| exp_02 | Car parked afternoon | Cupholder → snatched, frame tilts hard sideways |
| exp_03 | Bathroom mirror morning | Propped on sink → grabbed mid-toothbrush, lurches up |
| exp_04 | Bed morning sun | Face-up on bed → arm from duvet grabs it, dark then emerges |
| exp_05 | Kitchen coffee | Counter → one-handed flip, spins ceiling→face |
| exp_06 | Balcony wind | On railing, buzzes → snatched, frame swings wildly |
| exp_07 | Reading chair lamp | Armrest → both hands, frame rises slowly |
| exp_08 | Sidewalk walking | Mid-stride walk bounce → sudden dead stop |

**Output:** `~/.openclaw/workspace/output/ugc-reaction-experiments/`

---

## 5. Livestream Call Format

**Folder:** `ugc-livestream-call/`
**Concept:** Split-screen 9:16 Omegle/OnlyFans-style call. Streamer on top, Harvard student on bottom. Student casually reveals Professor Curious as their study secret.

### Script

#### `run_call_hooks.py`
```bash
python3 ~/ugc-ai-ads-engine/ugc-livestream-call/scripts/run_call_hooks.py
```

**Pipeline:**
1. Generate streamer clip (Veo 3)
2. Generate student clip (Veo 3)
3. Composite with ffmpeg `vstack` → 9:16 split-screen
4. Add Pillow UI overlay (call interface, usernames, timer)

---

## 6. Video Editor (Post-processing)

**Folder:** `video-editor/`
**Concept:** Apply cinematic post-processing to any generated run.

### Scripts

#### `edit.py` — Edit a single run
```bash
python3 ~/ugc-ai-ads-engine/video-editor/scripts/edit.py \
  --run-dir ~/.openclaw/workspace/output/ugc-experiments/exp_01_ek_raat \
  --hook-text "Raat ke 11 baje. Akela." \
  --logo ~/ugc-ai-ads-engine/assets/pc_logo.png \
  --style warm --transition fade --end-card --send-slack
```

**Features:**
- Color grading: `warm` / `cinematic` / `cool` / `neutral`
- Vignette effect
- Hook text overlay on establishing shot (first 3s, big bold text via Pillow)
- CTA text on outro ("Download Professor Curious")
- Logo bug (bottom-right corner, persistent)
- Cross-fade transitions between clips (0.3s xfade + acrossfade)
- Optional 2.5s branded end card
- Audio normalization (loudnorm –16 LUFS)

#### `edit_batch.py` — Edit all runs at once

---

## 7. Professor Curious Street Interview (older)

**Folder:** `professor-curious-street-interview/`
**Concept:** PC-specific India street interview, grade-based emotional hooks. Earlier version of skill 1.

```bash
python3 ~/ugc-ai-ads-engine/professor-curious-street-interview/scripts/run.py
```

---

## Output Directory Structure

```
~/.openclaw/workspace/output/
├── ugc-street-interview/<run-id>/
│   ├── clips/
│   └── <run-id>_merged.mp4
├── ugc-experiments/
│   ├── exp_01_ek_raat/
│   ├── exp_02_bag_pack/
│   ├── exp_03_rank_wala/
│   ├── exp_04_pehla_din/
│   └── exp_05_mock_result/
├── ugc-shame-series/
│   ├── shame_01_classroom/
│   ├── shame_02_coaching/
│   ├── shame_03_home/
│   ├── shame_04_friends/
│   └── shame_05_alone/
├── ugc-vs-gauth/
│   ├── gauth_01_mit/
│   ├── gauth_02_stanford/
│   └── gauth_03_harvard/
├── ugc-us-comparison/
│   ├── us_cmp_01_vs_khan/
│   ├── us_cmp_02_vs_chegg/
│   ├── us_cmp_03_vs_chatgpt/
│   ├── us_cmp_04_vs_tutors/
│   └── us_cmp_05_vs_quizlet/
├── ugc-sora-hooks/             ← Reaction hooks (Sora)
├── ugc-veo-hooks/              ← Reaction hooks (Veo 3)
├── ugc-reaction-experiments/   ← 8 raw reaction experiments
└── ugc-studytok-hooks/
    ├── demo/                   ← Demo video clips
    └── audio/                  ← Trending audio files
```

---

## Credentials

```bash
source ~/.env_azure   # loads everything below

AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://oai-swedencen-dummy.openai.azure.com/
AZURE_SORA_MODEL=sora-2
GEMINI_API_KEY=...
```

---

## Slack

```bash
# Experimental (all iterations)
curl -X POST http://zpdev.zupay.in:8160/send \
  -F "channel_id=C0AHDH474LX" \
  -F "text=description" \
  -F "file=@/path/to/video.mp4"
```

| Channel | ID | Use |
|---------|-----|-----|
| Main / approved | `C0AHDH474LX` | Only when Anubhav explicitly approves |
| exp-ai-ads-videos | `C0AJSBJU1LK` | Experimental (bot not yet invited — use main for now) |

---

## Critical Rules Across All Skills

1. **Always `source ~/.env_azure` before running any script**
2. **Sora audio fix** — all stitch commands must use `-c:a aac -ar 48000 -b:a 128k` or Slack won't play the video
3. **Sora blocks realistic human images** — never use `input_reference` with real photos; use Veo 3 instead
4. **WE ARE the phone camera** — for reaction videos, the frame IS the phone being picked up
5. **Professor Curious name spoken clearly** — every interview clip, unmistakably out loud
6. **Two-act structure** — Act 1 pain (3–4s), Act 2 PC turning point (3–4s)
7. **All India = Kota** — every India setting must reference Kota, Rajasthan explicitly
