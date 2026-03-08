# UGC AI Ads Engine — Session Context

> This file is the source of truth for project state, decisions, and where we left off.
> Updated after every session. Pull this to resume with full context.

---

## Project Overview

Generates UGC-style street interview videos using **Azure Sora (sora-2)** via the Azure OpenAI API.
Target product: **Professor Curious** (edtech app for Indian students).
Output: 9:16 vertical MP4 clips, stitched into one merged video.

---

## Repo Structure

```
ugc-ai-ads-engine/
├── ugc-street-interview/           ← India: Kota coaching/school gate, Hindi, emotional
│   ├── scripts/run.py
│   ├── scripts/run_experiments.py  ← 5 India Kota hooks
│   ├── references/
│   └── SKILL.md
├── ugc-us-college-interview/       ← US: Harvard/MIT/Stanford gate, English, social proof
│   ├── scripts/run.py
│   ├── references/
│   └── SKILL.md
├── ugc-studytok-hooks/             ← StudyTok: Sora reaction + demo + trending audio
│   └── scripts/
│       ├── run_studytok_hooks.py   ← Main pipeline: 5 hooks with caption, demo, audio
│       └── run_reaction_experiments.py ← 8 pure reaction experiments (varied settings)
├── ugc-livestream-call/            ← Split-screen call format (Veo 3)
│   └── scripts/run_call_hooks.py
├── ugc-reaction/                   ← Reaction hooks (Sora US + Veo 3)
│   └── scripts/
│       ├── run_hooks_us.py         ← 10 Sora US hooks
│       └── run_veo_hooks.py        ← 5 Veo 3 hooks (Gemini pipeline)
├── professor-curious-street-interview/  ← PC-specific India skill (older)
│   ├── scripts/run.py
│   ├── output/                     ← Generated videos (gitignored)
│   └── SKILL.md
├── video-editor/                   ← Post-processing: color grade, transitions, text
│   └── scripts/
│       ├── edit.py
│       └── edit_batch.py
├── assets/
│   ├── pc_logo.png
│   └── gauth_logo.png
├── CONTEXT.md                      ← This file
└── README.md
```

---

## Slack API

**Endpoint:** `POST http://zpdev.zupay.in:8160/send` (no auth needed)
**Main/approved channel:** `C0AHDH474LX` — only send here when Anubhav explicitly approves a final ad
**Experimental channel:** `C0AJSBJU1LK` — all experiments, tests, iterations go here by default
**Content-Type:** `multipart/form-data`

**Parameters:**
- `channel_id` (required) — use `C0AHDH474LX` for team channel
- `text` (optional) — message text
- `file` (optional) — any file type; at least one of text/file required

**Send a video:**
```bash
curl -X POST http://zpdev.zupay.in:8160/send \
  -F "channel_id=C0AHDH474LX" \
  -F "text=<description>" \
  -F "file=@/path/to/video.mp4"
```

**Send text only:**
```bash
curl -X POST http://zpdev.zupay.in:8160/send \
  -F "channel_id=C0AHDH474LX" \
  -F "text=Hello"
```

---

## Credentials (stored locally only — NEVER commit)

Stored in `~/.env_azure`, sourced in `~/.zshrc`:
```
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_ENDPOINT=https://oai-swedencen-dummy.openai.azure.com/
AZURE_SORA_MODEL=sora-2
```

To load in any shell: `source ~/.env_azure`

---

## How to Run

```bash
source ~/.env_azure
cd ~/ugc-ai-ads-engine/ugc-street-interview/scripts

# Default (Kota coaching scene, 3 people, 8s per clip)
python3 run.py --product "Professor Curious" --run-id kota_v1

# Full options
python3 run.py \
  --product "Professor Curious" \
  --scene kota-coaching \
  --run-id kota_v2 \
  --num-people 3 \
  --seconds 8
```

Output lands in: `~/.openclaw/workspace/output/ugc-street-interview/<run-id>/`

---

## Available Scenes

| Scene | Description |
|-------|-------------|
| `kota-coaching` | **DEFAULT** — Kota coaching centre gate, evening |
| `school-gate` | School gate post-exam, Kota |
| `coaching-centre` | Coaching centre (Kota explicit) |
| `results-day` | Board results day outside school, Kota |
| `chai-stall` | Roadside chai stall outside coaching, Kota |
| `college-gate` | College gate, Kota veterans |
| `parent-pickup` | Parent pickup zone, Kota |

---

## Skills Overview

| Skill | Market | Language | Angle | Default Scene |
|-------|--------|----------|-------|---------------|
| `ugc-street-interview` | India | Hindi | Post-exam, raw emotion, Kota pressure | `kota-coaching` |
| `ugc-us-college-interview` | US | English | "What got you into Harvard/MIT/Stanford?" | `harvard` |
| `professor-curious-street-interview` | India | Hindi | PC-specific (older, grade-based) | school gate |

---

## Session Log

### Session 8 — 2026-03-08

**New formats built:**

#### 1. StudyTok Hooks (`ugc-studytok-hooks/`)
Snapchat-style TikTok reaction hooks: Sora 2 reaction clip → caption overlay → full demo video (muted) → trending audio → Slack.

**Script:** `ugc-studytok-hooks/scripts/run_studytok_hooks.py`

Key config:
- Demo clips: `761f2bb3b84a4003a9744b4e5b45a4f2.MP4` (27.9s) + `958c1b7bb7d4413d8276bfaa828a58d8.MP4` (24.6s) in `~/.openclaw/workspace/output/ugc-studytok-hooks/demo/`
- Audio pool (dynamic selection by total video length):
  - Short (<35s): `audio_01_oh_no.mp3` — Oh No by Kreepa
  - Medium (35-55s): `audio_03_cupid.mp3` — Cupid by FIFTY FIFTY
  - Long (>55s): `audio_02_aperture.mp3` — Harry Styles Aperture
- Caption: dark semi-transparent bar, white text, positioned at TOP 8% of frame (`bar_y = int(height * 0.08)`)
- Emoji rendering: Apple Color Emoji font at `/System/Library/Fonts/Apple Color Emoji.ttc`, split text into runs, render with `embedded_color=True`
- Sora API: `POST {ENDPOINT}/openai/v1/videos`, `size=720x1280`, poll until completed, download via `/content`

**5 hooks generated:** library, cafe, bedroom, gym, walking — all sent to Slack ✓

#### 2. Livestream Call Format (`ugc-livestream-call/`)
Split-screen 9:16 Omegle/call style: streamer (top) + Harvard student (bottom), reveals Professor Curious.

**Script:** `ugc-livestream-call/scripts/run_call_hooks.py`
- Uses Veo 3 for both sides, composites with ffmpeg vstack
- Adds Pillow UI overlay (call UI, usernames, timer)

#### 3. Reaction Experiments (`ugc-studytok-hooks/scripts/run_reaction_experiments.py`)
8 pure reaction clips (no caption/demo/stitch) — varied settings and motions.

**Critical POV fix discovered this session:**
> The recording camera IS the phone being picked up. The FRAME must physically move.
> Key prompt pattern: "THIS IS A FIRST-PERSON PHONE CAMERA VIDEO. THE CAMERA ITSELF IS THE PHONE BEING PICKED UP. There is no other phone. When the person picks up the phone, THE FRAME MOVES."
> Frame must spin/lurch/tilt — not show a person looking at a separate phone.

**8 experiments completed and sent to Slack:**
| # | Setting | Motion |
|---|---------|--------|
| 01 | Cafe golden hour | Face-down → flipped & lifted, frame spins |
| 02 | Car parked afternoon | Cupholder → snatched, frame tilts hard |
| 03 | Bathroom mirror | Propped on sink → grabbed mid-toothbrush, lurches up |
| 04 | Bed morning sun | Face-up on bed → arm from duvet grabs it, dark then emerges |
| 05 | Kitchen coffee | Counter → one-handed flip, spins ceiling→face |
| 06 | Balcony wind | Railing buzzes → snatched, frame swings wildly |
| 07 | Reading chair | Armrest → both hands, frame rises slowly |
| 08 | Walking stops | Mid-stride walk bounce → dead stop |

**Output:** `~/.openclaw/workspace/output/ugc-reaction-experiments/`

**Fixes this session:**
- Caption was covering face at 42% → moved to top 8%
- Emoji showing as square boxes → Apple Color Emoji font + split_runs() per segment
- Audio hardcoded → dynamic selection by total video length
- Demo video updated to new clips (27.9s + 24.6s)
- C0AJSBJU1LK returns channel_not_found (bot not invited) — experiments went to C0AHDH474LX

**Pending:**
- Evaluate which of the 8 reaction experiments worked best → iterate on winners
- Get correct channel ID for `exp-ai-ads-videos` or invite bot to C0AJSBJU1LK

---

### Session 3 — 2026-03-04

**Changes applied to `ugc-street-interview/scripts/run.py`:**

1. **Professor Curious always named clearly** — every person response says the name explicitly, out loud. Prompt instructs the name must be "unmistakably audible and visible."

2. **Two-act clip structure (3-4s + 3-4s)** — Act 1: raw emotional problem (loneliness, fear, failure). Act 2: "Professor Curious" as the turning point. Explicitly instructed in `build_person_prompt`.

3. **Emotional, raw dialogue** — All 35 person responses rewritten. Stories: mothers selling gold, fathers crying at drop-off, packing bags to quit Kota, calling home then not, crying alone at 2am.

4. **All scenes set in Kota** — New default scene `kota-coaching` added. All other scene settings updated to reference Kota, Rajasthan explicitly. Establishing/outro lines all mention Kota.

**Status:** Script updated. Kota_v1 run submitted to Azure Sora (in progress at session end).

---

### Session 3 (continued) — 2026-03-04: US College Interview Skill

**New skill created: `ugc-us-college-interview/`**

**Concept:** Vlogger outside elite US universities asks "What did you use to get in?"
- Majority of students say Professor Curious by name, clearly
- Minority mention Khan Academy / Quizlet first → come around to Professor Curious (creates authenticity)
- Two-act structure: Act 1 (3-4s) struggle/tools tried → Act 2 (3-4s) Professor Curious as the answer
- Aspirational FOMO play: "Harvard students use it" social proof

**Scenes built (6 total):**
- `harvard` (DEFAULT) — Johnston Gate, Cambridge MA, autumn
- `mit` — Massachusetts Ave entrance, analytical/intense
- `stanford` — White Plaza, warm California campus
- `yale` — Phelps Gate, gothic literary energy
- `princeton` — Nassau Hall gate, historic/prestigious
- `elite-campus` — Generic elite university, flexible

**Mix formula per scene (5 people):**
- p01: Pure PC advocate
- p02: "Tried Khan Academy → switched to Professor Curious"
- p03: Social proof — "my whole dorm used Professor Curious"
- p04: "Quizlet for vocab, but Professor Curious for understanding"
- p05: Matter-of-fact — "easy answer"

**To run:**
```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-us-college-interview/scripts/run.py \
  --product "Professor Curious" --scene harvard --run-id harvard_v1
```

**Status:** Built and committed. Ready to run.

---

### Session 7 — 2026-03-06

**New format: Reaction hooks (UGC selfie-cam style)**

**Pipeline 1: Sora text-to-video (no reference image)**
- `ugc-reaction/scripts/` — all reaction scripts
- Key learning: Sora's `input_reference` hard-blocks ANY realistic human image (`people-in-user-uploads` policy). Only anime/illustrated style passes.
- Solution: text-only prompts with detailed selfie-cam direction

**Pipeline 2: Gemini (nano-banana-pro + Veo 3)**
- `ugc-reaction/scripts/run_veo_hooks.py`
- nano-banana-pro (`models/nano-banana-pro-preview`) = Gemini 3 Pro Image — generates realistic portraits
- Veo 3 (`veo-3.0-generate-001`) — image-to-video, 9:16, 8s
- GEMINI_API_KEY saved to `~/.env_azure`
- Veo 3 response format: `response.generateVideoResponse.generatedSamples[0].video.uri` — download with `?key=` appended
- Remove `enhancePrompt` — not supported by Veo 3

**Prompt engineering for realistic UGC:**
- Key phrase: `"WE ARE the phone camera"` — sets POV correctly
- Beat-by-beat timing: `0-2s: ... 2-4s: ... 4-6s: ...`
- Camera motion must be explicit: pick-up lurch, grip tightens on shock, exhale dips frame, pulling closer tightens shot
- Imperfections = realism: `"autofocus micro-pulses"`, `"flat colors no LUT"`, `"raw phone audio background hiss"`
- Specific device: `"iPhone 15 Pro front camera in selfie mode"`
- Character NOT model-pretty: `"no makeup, messy hair, not model-pretty"`

**Angle variants tested (sent to experimental Slack):**
- `angle_A_low` — phone flat on desk looking up, pick-up lurch
- `angle_B_high` — phone lifted high looking down, swing motion
- `angle_C_mirror` — ultra close chest-level, grip reaction jolts
- `angle_D_tilted` — bed/casual tilt (moderation blocked)
- Best versions: `v2_angle_A/B/C` with full camera motion per beat

**Slack channels:**
- Experimental: `C0AJSBJU1LK` — ALL iterations go here
- Main/approved: `C0AHDH474LX` — only when Anubhav explicitly approves

**Available Gemini models on key:**
- Image: `nano-banana-pro-preview` (Gemini 3 Pro Image), `imagen-4.0-generate-001`, `imagen-4.0-ultra-generate-001`
- Video: `veo-3.0-generate-001`, `veo-3.1-generate-preview`, `veo-3.0-fast-generate-001`

**Scripts:**
| Script | Purpose |
|--------|---------|
| `ugc-reaction/scripts/run_veo_hooks.py` | Gemini pipeline: nano-banana-pro + Veo 3, 5 hooks |
| `ugc-reaction/scripts/run_hooks_us.py` | Sora 10 US hooks |
| `ugc-reaction/scripts/run_reaction.py` | Sequential 4-clip reaction format |
| `ugc-reaction/scripts/test_consistent_char.py` | Character consistency test |

**Output:** `~/.openclaw/workspace/output/ugc-veo-hooks/` and `ugc-sora-hooks/`

**Pending:** Pick best camera angle from v2 angle tests → lock in → rebuild all 5 hooks with that angle

---

### Session 6 — 2026-03-06

**New format: Hand-only vlogger (`run_hand_vlog.py`)**

Problem: Sora cannot maintain character consistency across clips (face/body shifts).
Solution: Only the vlogger's hand (holding mic) is shown at the bottom-left edge of frame.
No face, no torso — vlogger is voice-only. Sora only needs to render a hand grip.

**Script:** `ugc-street-interview/scripts/run_hand_vlog.py`
- `HAND_LOCK` replaces `VLOGGER_LOCK` — hand + mic only, bottom-left edge, no face/body
- All establishing/outro visuals rewritten (no selfie-cam references)
- Output to `ugc-hand-vlog/<run-id>/`

**hand_v1:** 5 clips × 8s, kota-coaching, 22MB — sent to Slack ✓
Subjects: NEET girl (gold sold), JEE boy (bag pack night), NEET girl (fierce topper)

**Logo fix (all 3 Gauth scripts):** size 130→85px, y-pos 20→100px (below face area)

---

### Session 5 — 2026-03-06

**New skill: `video-editor/`**

Built a proper post-processing pipeline for UGC ads. Current editing was just `ffmpeg -f concat -c copy` — zero editing.

**`video-editor/scripts/edit.py`** — edit a single run:
- Color grading: warm/cinematic/cool/neutral (colorbalance + eq)
- Vignette effect
- Hook text on establishing shot (big text, first 3s) via Pillow PNG → ffmpeg overlay
- CTA text on outro ("Download Professor Curious")
- App logo bug (bottom-right corner, persistent)
- Cross-fade transitions between clips (pairwise xfade + acrossfade, 0.3s)
- Optional 2.5s branded end card (Pillow-generated PNG → looped video)
- Audio normalization (loudnorm –16 LUFS)
- Fallback: no manifest.json → infers clip types from filenames

**`video-editor/scripts/edit_batch.py`** — edit all runs at once

**Known issues fixed:**
- drawtext not available in this ffmpeg (no libfreetype) → use Pillow for text
- xfade timebase mismatch after multiple pairwise merges → normalize with fps=24 + aresample=48000 before each xfade

**Usage:**
```bash
python3 ~/ugc-ai-ads-engine/video-editor/scripts/edit.py \
  --run-dir ~/.openclaw/workspace/output/ugc-experiments/exp_01_ek_raat \
  --hook-text "Raat ke 11 baje. Akela." \
  --logo ~/ugc-ai-ads-engine/assets/pc_logo.png \
  --style warm --transition fade --end-card --send-slack
```

**Test:** exp_01_ek_raat_edited.mp4 (41s, 720x1280, H.264) sent to Slack ✓

---

### Session 4 — 2026-03-04 (continued)

**New scripts added to `ugc-us-college-interview/scripts/`:**

| Script | Ads | Status |
|--------|-----|--------|
| `run_experiments.py` | 5 India experimental hooks (ek-raat, bag-pack, rank-wala, pehla-din, mock-result) | ✓ DONE, sent to Slack |
| `run_shame_series.py` | 5 India shame series (क्यों नहीं हो रही पढ़ाई?) | ✓ DONE, sent to Slack |
| `run_comparison.py` | 5 US comparison ads (vs Khan/Chegg/ChatGPT/Tutors/Quizlet) | ✓ DONE, sent to Slack |
| `run_vs_gauth.py` | 3 US Gauth vs PC ads with logo overlays | ✓ DONE (mit+stanford+harvard), sent to Slack |
| `rerun_gauth_02.py` | Targeted rerun for gauth_02_stanford (DNS fail recovery) | helper script, kept in repo |

**Critical audio fix — PERMANENT RULE:**
> Sora generates 96kHz AAC audio. Slack cannot play it.
> ALL stitch/merge commands must use: `-c:a aac -ar 48000 -b:a 128k`
> This is applied in: run_vs_gauth.py, run_comparison.py, rerun_gauth_02.py, and all future scripts.
> Also embed_logos() must include `-map 0:a? -c:a aac -ar 48000 -b:a 128k`

**Output directories:**
```
~/.openclaw/workspace/output/
├── ugc-street-interview/kota_v1/          ← kota_v1_merged.mp4
├── ugc-experiments/exp_01_ek_raat/        ← exp_01_ek_raat_merged.mp4
├── ugc-experiments/exp_02_bag_pack/       ← exp_02_bag_pack_merged.mp4
├── ugc-experiments/exp_03_rank_wala/      ← exp_03_rank_wala_merged.mp4
├── ugc-experiments/exp_04_pehla_din/      ← exp_04_pehla_din_merged.mp4
├── ugc-experiments/exp_05_mock_result/    ← exp_05_mock_result_merged.mp4
├── ugc-shame-series/shame_01_classroom/   ← shame_01_classroom_merged.mp4
├── ugc-shame-series/shame_02_coaching/    ← shame_02_coaching_merged.mp4
├── ugc-shame-series/shame_03_home/        ← shame_03_home_merged.mp4
├── ugc-shame-series/shame_04_friends/     ← shame_04_friends_merged.mp4
├── ugc-shame-series/shame_05_alone/       ← shame_05_alone_merged.mp4
├── ugc-vs-gauth/gauth_01_mit/             ← gauth_01_mit_merged.mp4
├── ugc-vs-gauth/gauth_02_stanford/        ← gauth_02_stanford_merged.mp4
├── ugc-vs-gauth/gauth_03_harvard/         ← gauth_03_harvard_merged.mp4
├── ugc-us-comparison/us_cmp_01_vs_khan/   ← us_cmp_01_vs_khan_merged.mp4
├── ugc-us-comparison/us_cmp_02_vs_chegg/  ← us_cmp_02_vs_chegg_merged.mp4
├── ugc-us-comparison/us_cmp_03_vs_chatgpt/← us_cmp_03_vs_chatgpt_merged.mp4
├── ugc-us-comparison/us_cmp_04_vs_tutors/ ← us_cmp_04_vs_tutors_merged.mp4
└── ugc-us-comparison/us_cmp_05_vs_quizlet/← us_cmp_05_vs_quizlet_merged.mp4
```

**Logo assets:**
```
~/ugc-ai-ads-engine/assets/
├── gauth_logo.png   ← 512x512 from App Store
└── pc_logo.png      ← 512x512 from App Store (iTunes API)
```

**Total videos sent to Slack:** 19 (11 India + 3 Gauth + 5 US comparison)

---

### Session 2 — ~2026-02-25

- Built full multi-scene UGC generator with 6 scene types
- Azure Sora API integration (submit → poll → download → stitch)
- VLOGGER_LOCK continuity description for consistent character across clips
- 5 person archetypes per scene with Hindi dialogue and visual directions

### Session 1 — ~2026-02-20

- Initial concept: UGC street interview style for Professor Curious
- Reference videos collected
- Basic school-gate scene scripted
