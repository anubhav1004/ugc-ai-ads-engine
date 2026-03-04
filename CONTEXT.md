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
├── ugc-street-interview/
│   ├── scripts/run.py          ← Main generator script
│   ├── references/             ← Reference videos/images
│   └── SKILL.md
├── professor-curious-street-interview/
│   ├── scripts/run.py
│   ├── output/                 ← Generated videos (gitignored)
│   └── SKILL.md
├── CONTEXT.md                  ← This file
└── README.md
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

## Session Log

### Session 3 — 2026-03-04

**Changes applied to `ugc-street-interview/scripts/run.py`:**

1. **Professor Curious always named clearly** — every person response says the name explicitly, out loud. Prompt instructs the name must be "unmistakably audible and visible."

2. **Two-act clip structure (3-4s + 3-4s)** — Act 1: raw emotional problem (loneliness, fear, failure). Act 2: "Professor Curious" as the turning point. Explicitly instructed in `build_person_prompt`.

3. **Emotional, raw dialogue** — All 35 person responses rewritten. Stories: mothers selling gold, fathers crying at drop-off, packing bags to quit Kota, calling home then not, crying alone at 2am.

4. **All scenes set in Kota** — New default scene `kota-coaching` added. All other scene settings updated to reference Kota, Rajasthan explicitly. Establishing/outro lines all mention Kota.

**Status:** Script updated. Ready to run. Credentials saved locally.

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
