# Creative Dashboard

This is the fastest way to understand the repo as a creative workspace.

Use this file as the front door.

## What This Repo Does

This repo helps create Professor Curious ads by combining:
- product research
- user feedback
- ad concepts
- prompt experiments
- reaction-video systems
- India and US UGC formats

It is best understood as a creative studio, not just a codebase.

## Best Places To Start

### If you want the simplest overview
- `START_HERE.md`

### If you want to understand the product before making ads
- `research/README.md`
- `research/product/PROF_CURIOUS_CREATIVE_RESEARCH_V2_2026-03-12.md`

### If you want to see the latest active systems
- `experiments/LATEST.md`

### If you want to understand the strongest current reaction-video system
- `experiments/reaction-pipeline/README.md`

### If you want to understand India raw-footage work
- `india-raw-footage/README.md`

## Current Best Systems

| System | What it is | Where to open | Status |
|---|---|---|---|
| Reaction Pipeline | Short reaction ads with top hook, same-phone pickup motion, Professor Curious demo, replacement audio | `experiments/reaction-pipeline/` | Best current reaction system |
| India Raw Footage | More controlled India-style raw camera ads with characters, rooms, formats, and campaign briefs | `india-raw-footage/` | Main India raw-footage build area |
| India Street Interview | Hindi interview-style social-proof ads | `ugc-street-interview/` | Stable core format |
| US College Interview | English campus-style social-proof ads | `ugc-us-college-interview/` | Stable core format |
| Research | Product understanding, persona work, user feedback, creative strategy | `research/` | Strategic source of truth |

## What Is Stable vs Experimental

### Stable or core direction
- `ugc-street-interview/`
- `ugc-us-college-interview/`
- `ugc-reaction/`
- `video-editor/`
- `research/`

### Experimental or evolving
- `experiments/reaction-pipeline/`
- `experiments/reaction-ads/`
- `experiments/reaction-ads-v2/`
- `experiments/india-raw-footage/`
- `india-raw-footage/`

## Best Current Creative Territories

These are the strongest ad directions based on the current product research.

### 1. Confusion -> explanation -> relief
The product works best when the ad starts with a real stuck moment and then proves clarity.

### 2. Reaction + demo
Short reaction first, then immediate app proof.

### 3. “It actually explains it”
This is stronger than generic “AI study app” messaging.

### 4. Private help without judgment
Strong emotional angle, especially for students who avoid asking publicly.

### 5. India raw-footage realism
Phone-camera-feeling ads in believable rooms and situations.

## Best Research Files

If someone wants to understand the product properly, these are the most valuable files.

### Product understanding
- `research/product/PROF_CURIOUS_CREATIVE_RESEARCH_V2_2026-03-12.md`
- `research/product/PROF_CURIOUS_PRODUCT_DOSSIER_2026-03-12.md`

### User feedback
- `research/user-feedback/INSIGHTS_2026-03-12.md`
- `research/user-feedback/USER_RESEARCH_QUESTIONS.md`
- `research/user-feedback/prof-curious-user-feedback-2026-03-08.csv`

## Current Reaction Work

Best folder:
- `experiments/reaction-pipeline/`

What it currently supports:
- front-selfie reaction
- side-table reaction
- same-phone pickup motion
- top black hook bar
- full Professor Curious demo stitch
- replacement trending-style audio

Best files to review:
- `experiments/reaction-pipeline/specs/front-selfie-sample.json`
- `experiments/reaction-pipeline/specs/side-table-sample.json`
- `experiments/reaction-pipeline/specs/side-table-dim-screenlight-sample.json`

## Current India Work

### Core India format
- `ugc-street-interview/`

### Raw-footage system
- `india-raw-footage/`

### India prompt tests
- `experiments/india-raw-footage/prompt-tests/doubt-mazak-street-interview/`
- `experiments/india-raw-footage/prompt-tests/school-corridor-confession/`
- `experiments/india-raw-footage/prompt-tests/ai-impact-summit-explainer/`

## How To Navigate As A Non-Technical Person

If you want to:

### Understand the product
Open:
- `research/README.md`
- `research/product/PROF_CURIOUS_CREATIVE_RESEARCH_V2_2026-03-12.md`

### Understand what we are building now
Open:
- `experiments/LATEST.md`
- `CREATIVE_DASHBOARD.md`

### Understand the ad systems
Open:
- `experiments/reaction-pipeline/README.md`
- `india-raw-footage/README.md`

### Understand recent project history
Open:
- `CONTEXT.md`

## Important Repo Rule

The repo mostly stores:
- prompts
- scripts
- specs
- overlays
- research
- manifests

Most generated video files stay local and are usually not committed into Git.

So the repo is mainly:
- the system
- the structure
- the thinking

not just the exported media.

## Best Mental Model

If you only remember one thing, remember this:

`research tells us what to say`

`experiments help us test how to say it`

`the production folders help us turn the winning ideas into repeatable ad systems`
