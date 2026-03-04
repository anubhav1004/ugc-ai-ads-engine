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
│   ├── references/
│   └── SKILL.md
├── ugc-us-college-interview/       ← US: Harvard/MIT/Stanford gate, English, social proof
│   ├── scripts/run.py
│   ├── references/
│   └── SKILL.md
├── professor-curious-street-interview/  ← PC-specific India skill (older)
│   ├── scripts/run.py
│   ├── output/                     ← Generated videos (gitignored)
│   └── SKILL.md
├── CONTEXT.md                      ← This file
└── README.md
```

---

## Slack API

**Endpoint:** `POST http://zpdev.zupay.in:8160/send` (no auth needed)
**Team channel:** `C0AHDH474LX`
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

### Session 2 — ~2026-02-25

- Built full multi-scene UGC generator with 6 scene types
- Azure Sora API integration (submit → poll → download → stitch)
- VLOGGER_LOCK continuity description for consistent character across clips
- 5 person archetypes per scene with Hindi dialogue and visual directions

### Session 1 — ~2026-02-20

- Initial concept: UGC street interview style for Professor Curious
- Reference videos collected
- Basic school-gate scene scripted
