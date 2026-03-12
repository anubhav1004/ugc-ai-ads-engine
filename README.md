# UGC AI Ads Engine

This repo is the creative operating system for Professor Curious ads.

It is where we keep:
- product research
- user feedback
- ad ideas
- prompt experiments
- reaction-video systems
- India and US ad formats
- reusable generation pipelines

If you are new here, open:
- `START_HERE.md`
- `experiments/LATEST.md`
- `research/README.md`

> For detailed session history and implementation notes, see [CONTEXT.md](./CONTEXT.md).

---

## What This Repo Really Is

Think of this repo as a studio with different rooms.

| Area | What it means in plain English |
|---|---|
| `research/` | Everything we know about the product, the users, and what ads should say |
| `experiments/` | Active creative tests and prompt experiments |
| `india-raw-footage/` | The system for realistic India-style raw camera ads |
| `ugc-street-interview/` | India street interview ads |
| `ugc-us-college-interview/` | US college social-proof ads |
| `ugc-reaction/` | Reaction ad logic and camera rules |
| `video-editor/` | Post-production and finishing tools |

---

## Best Files To Open First

### If you want the latest work
- `experiments/LATEST.md`

### If you want to understand Professor Curious deeply
- `research/product/PROF_CURIOUS_CREATIVE_RESEARCH_V2_2026-03-12.md`
- `research/product/PROF_CURIOUS_PRODUCT_DOSSIER_2026-03-12.md`

### If you want to understand the raw-footage ad direction
- `india-raw-footage/README.md`

### If you want to understand the reaction-video direction
- `experiments/reaction-pipeline/README.md`

---

## Main Creative Systems

### India Street Interview
Folder:
- `ugc-street-interview/`

What it is:
- raw Hindi street-style interviews
- school gate / coaching center / Kota pressure
- emotional and social-proof driven

Example idea:
- students talking about how Professor Curious helped during exam pressure

### US College Interview
Folder:
- `ugc-us-college-interview/`

What it is:
- campus-style interviews in English
- aspirational and social-proof driven
- “What helped you get in?” style creative

### India Raw Footage
Folder:
- `india-raw-footage/`

What it is:
- a more controlled system for realistic recurring scenes
- characters, room setups, prompts, and campaign manifests
- useful when we want raw footage that still feels structured

### Reaction Pipeline
Folder:
- `experiments/reaction-pipeline/`

What it is:
- reaction-first ads
- top hook text
- same-phone pickup motion
- demo stitched after reaction
- replacement trending-style audio

---

## Research Area

Folder:
- `research/`

This is the strategic brain of the repo.

It contains:
- survey exports
- user insights
- personas
- product truths
- ad implications

This is the best place for non-technical people to start if they want to understand:
- what Professor Curious actually solves
- what users care about
- what angles are strong or weak

---

## Experiments Area

Folder:
- `experiments/`

This is where we try ideas before treating them as stable systems.

Inside it you will find:
- prompt tests
- reaction formats
- batch experiments
- temporary pipelines
- hook experiments

This is the repo’s “lab.”

---

## Important Note About Videos

The repo mostly tracks:
- prompts
- scripts
- manifests
- specs
- overlays
- research
- experiment structure

Most generated videos stay local and are intentionally not committed to Git.

Why:
- the repo stays cleaner
- the systems remain reusable
- we store the recipe, not only the baked output

---

## For Technical Use

Requirements:
- Python 3.11+
- `requests`
- `ffmpeg`
- Azure OpenAI / Sora access

Typical local output path:
- `~/.openclaw/workspace/output/<skill-name>/<run-id>/`

Typical contents:
- `clips/`
- merged video
- `manifest.json`
