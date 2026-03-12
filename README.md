# UGC AI Ads Engine

Generate authentic UGC-style video ads using Azure Sora. Raw footage, street interviews — no actors, no studio.

> **Context:** See [CONTEXT.md](./CONTEXT.md) for full session history, run instructions, and where we left off.

---

## Project Areas

### Stable / Core Systems

- `ugc-street-interview/` — India Hindi street interviews
- `ugc-us-college-interview/` — US college social-proof interviews
- `ugc-studytok-hooks/` — StudyTok hook generation
- `ugc-reaction/` — reaction hook scripts and camera logic
- `ugc-livestream-call/` — split-screen call format
- `video-editor/` — post-processing tools
- `common/send_slack.py` — Slack file/message sender helper

### Research

- `research/` — product research, survey analysis, persona work, and creative strategy

### Experiments

### `experiments/`
Visible workspace for trial pipelines, prompt tests, model comparisons, and consistency
experiments before they are promoted into stable production workflows.

See:
- `experiments/README.md`
- `experiments/LATEST.md`

### `ugc-street-interview/` — India Market
Vlogger interviews students outside coaching centres and school gates in Kota.
Hindi dialogue. Emotional, raw, Kota pressure angle.

**"Exam khatam hua — Professor Curious ne help ki."**

```bash
source ~/.env_azure
python3 ugc-street-interview/scripts/run.py \
  --product "Professor Curious" \
  --scene kota-coaching \
  --run-id kota_v1 \
  --num-people 3 \
  --seconds 8
```

**Scenes:** `kota-coaching` (default), `school-gate`, `coaching-centre`, `results-day`, `chai-stall`, `college-gate`, `parent-pickup`

---

### `ugc-us-college-interview/` — US Market
Vlogger outside Harvard, MIT, Stanford, Yale, Princeton asks students:
*"What did you use to get in?"* — majority say Professor Curious.
English dialogue. Aspirational FOMO + social proof angle.

**"I'm outside Harvard. Let's ask students what they used to get in."**

```bash
source ~/.env_azure
python3 ugc-us-college-interview/scripts/run.py \
  --product "Professor Curious" \
  --scene harvard \
  --run-id harvard_v1 \
  --num-people 3 \
  --seconds 8
```

**Scenes:** `harvard` (default), `mit`, `stanford`, `yale`, `princeton`, `elite-campus`

---

### `professor-curious-street-interview/` — PC India (Grade-specific)
Original PC-specific skill. Grade-based targeting (Class 10 / Class 12 boards).

---

### `india-raw-footage/` — India Character-Consistency Lab
New India-market production scaffold for recurring-character raw phone-footage ads.
Built to support stronger continuity across multi-video campaigns using locked character
packs, format templates, setting packs, and per-campaign shot manifests.

**Current test:** `kota_boy_confession_night_01`

```bash
python3 india-raw-footage/scripts/build_run.py \
  --campaign india-raw-footage/campaigns/kota_boy_confession_night_01/brief.json
```

### `experiments/reaction-pipeline/` — Reaction Ad System
Reusable reaction-video pipeline for:
- front-selfie reactions
- side-table reactions
- same-phone pickup motion in post
- Professor Curious demo stitching
- trending-style replacement audio

Main runner:

```bash
python3 experiments/reaction-pipeline/run_reaction_pipeline.py \
  --spec experiments/reaction-pipeline/specs/front-selfie-sample.json
```

## Generated Outputs

Generated media stays local and gitignored by default:
- `output/`
- `*.mp4`
- `*.mov`

The repo tracks:
- scripts
- prompts
- manifests
- specs
- overlays
- research
- experiment structure

---

## Requirements
- Python 3.11+ with `requests` installed
- `ffmpeg`
- Azure OpenAI with Sora deployment

**Credentials:** stored in `~/.env_azure`, auto-loaded via `~/.zshrc`

## Output
`~/.openclaw/workspace/output/<skill-name>/<run-id>/`
- `clips/` — individual Sora-generated MP4s
- `<run-id>_merged.mp4` — final stitched ad
- `manifest.json`
