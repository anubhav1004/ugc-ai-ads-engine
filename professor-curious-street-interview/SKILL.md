---
name: professor-curious-street-interview
description: >
  Fully autonomous AI ad generator for Professor Curious. Produces raw-footage Hindi
  street interview clips (school kids post-exam, coaching exit, or exam-day morning).
  9:16 vertical, Azure Sora, auto-stitched MP4. Just give it a run-id and go.
---

# Professor Curious — Street Interview Ad Generator (Master Skill)

## What this produces
- Raw vlog-style Hindi street interview ads for the Professor Curious app
- 3-part structure: **establishing shot → N kid interviews → outro**
- All clips share the same vlogger, location, and shooting aesthetic for continuity
- Automatically stitched into one final merged MP4

---

## Quick start (copy-paste ready)

```bash
AZURE_OPENAI_API_KEY=<key> \
AZURE_OPENAI_ENDPOINT=<endpoint> \
AZURE_SORA_MODEL=sora-2 \
python3 /path/to/skills/professor-curious-street-interview/scripts/run.py \
  --run-id ad_v1 \
  --num-kids 3 \
  --time golden_hour \
  --seconds 8
```

---

## Arguments

| Arg | Default | Options / Notes |
|-----|---------|-----------------|
| `--run-id` | `run_001` | Unique name for this batch. Use something meaningful: `pc_exam_v3`, `batch_night_01` |
| `--num-kids` | `3` | 1–13 (however many are in the dialogue bank) |
| `--kid-ids` | random | Pick specific kids: `--kid-ids kid_09 kid_11 kid_13` |
| `--seconds` | `8` | Clip duration: `4` / `8` / `12` |
| `--time` | `golden_hour` | `golden_hour` · `night` · `early_morning` (see below) |
| `--grade` | — | `10` or `12` — uses grade-specific dialogue bank |
| `--output-dir` | `~/.openclaw/workspace/output/professor-curious-street-interview/` | Override output path |
| `--no-stitch` | false | Skip ffmpeg merge (download clips only) |

---

## Time-of-day modes

### `golden_hour` (default)
Late afternoon post-exam. School gate, kids streaming out happy/relieved.
Warm golden light, chai stall, yellow autos, parents waiting.
**Best for:** post-exam relief ads, high-energy conversions.

### `night`
~8 PM. Outside coaching institute after evening batch.
Orange street lights, neon signs, motorbikes, tired-but-chatty kids.
**Best for:** "studied late, doubts at night" angle — kid_11 (2 AM panic), kid_10 (underdog).

### `early_morning`
~6:30 AM. Exam day arrival. Pale dawn sky, mist, nervous kids, chai stall opening.
**Best for:** aspiration and dreams angle — kid_13 (doctor dream), kid_10 (small town).

---

## Dialogue banks

| File | Description | Kids |
|------|-------------|------|
| `dialogue-bank.yaml` | General (class 6–9, age 11–15) | kid_01–kid_13 |
| `dialogue-bank-10th.yaml` | Class 10 CBSE boards | kid_01–kid_05 |
| `dialogue-bank-12th.yaml` | Class 12 CBSE boards, JEE/NEET | kid_01–kid_05 |

### Kid profiles — general bank

| ID | Gender | Age | Emotion | Conversion hook |
|----|--------|-----|---------|-----------------|
| kid_01 | Boy | 13–14 | Excited happy | App cleared doubts instantly, easy paper |
| kid_02 | Girl | 12–13 | Confident relieved | Doubts cleared before exam |
| kid_03 | Girl | 13–14 | Enthusiastic giggly | Studied alone at night with app |
| kid_04 | Boy | 12–13 | Relieved proud | Night-before cramming paid off |
| kid_05 | Boy | 11–12 | Shy then happy | Mum suggested it, worked perfectly |
| kid_06 | Girl | 12–13 | Matter-of-fact smart | Faster than asking teacher |
| kid_07 | Boy | 13–14 | Proud confident | Best paper ever, step-by-step prep |
| kid_08 | Girl | 11–12 | Giggly happy | Daily revision habit, knew everything |
| **kid_09** | **Girl** | **13–14** | **Tearfully grateful** | **Failed before, Papa upset → turnaround arc** |
| **kid_10** | **Boy** | **12–13** | **Proud underdog** | **Small town, no tuition money → beat coaching kids** |
| **kid_11** | **Girl** | **13–14** | **Dramatic relief then joy** | **2 AM panic, mum asleep → app rescued her** |
| **kid_12** | **Boy** | **14–15** | **Coolly competitive** | **No coaching, topped class anyway** |
| **kid_13** | **Girl** | **12–13** | **Dreamy determined** | **Wants to be a doctor, app is her teacher** |

**Bold = high-conversion v2 batch**

---

## Recommended batch recipes

### Maximum emotion (highest conversion)
```bash
--kid-ids kid_09 kid_11 kid_13 --time golden_hour
```

### Underdog / aspiration (small-town parents angle)
```bash
--kid-ids kid_10 kid_13 --time early_morning
```

### Night study / 2 AM doubt clearing
```bash
--kid-ids kid_11 kid_04 --time night
```

### Full 5-ad high-conversion batch (v2)
Run 3 separate commands for time variety:
```bash
# Golden hour — emotional post-exam
--run-id pc_v2_golden --kid-ids kid_09 kid_12 --time golden_hour --seconds 8

# Night — coaching/study angle
--run-id pc_v2_night --kid-ids kid_11 --time night --seconds 8

# Early morning — exam day dreams
--run-id pc_v2_morning --kid-ids kid_10 kid_13 --time early_morning --seconds 8
```

### 10th Boards full batch
```bash
--run-id pc_10th_v1 --grade 10 --num-kids 5 --time golden_hour --seconds 8
```

### 12th Boards / JEE / NEET
```bash
--run-id pc_12th_v1 --grade 12 --num-kids 5 --time golden_hour --seconds 8
```

---

## Output structure

```
~/.openclaw/workspace/output/professor-curious-street-interview/<run-id>/
  clips/
    clip_01_establishing.mp4
    clip_02_kid_09.mp4
    clip_03_kid_12.mp4
    clip_04_outro.mp4
  <run-id>_merged.mp4    ← final ad
  manifest.json
```

---

## Adding new kids

Edit `references/dialogue-bank.yaml`:

```yaml
- id: kid_14
  gender: girl          # boy | girl
  age_range: "12-13"
  emotion: your_tag     # used in logs, not in prompt
  vlogger_question_hindi: "Bhaiya, ..."
  kid_response_hindi: "Haan bhaiya, ..."
  visual_action: >
    Describe exactly what the kid is doing physically —
    gestures, posture, expressions, friends in background.
    The more specific, the better Sora renders it.
```

Key principles for high-converting dialogue:
- **Specific pain point** → failing before, 2 AM panic, no money for tuition
- **Specific outcome** → topped class, parents noticed, paper felt easy
- **Indian family dynamics** → Papa upset, Mummy asleep, teacher not available
- **Aspiration hook** → doctor, engineer, college dreams
- **Social contrast** → beat kids with coaching, no tutors needed

---

## Prompt architecture

Every clip shares two locked prompts prepended to the scene:
1. **SETTINGS[time_mode]** — location, lighting, ambient crowd, technical aesthetic
2. **VLOGGER_LOCK** — consistent vlogger appearance across all clips

This creates visual continuity so the stitched video looks like one real shoot.

---

## Preconditions

- `AZURE_OPENAI_API_KEY` set
- `AZURE_OPENAI_ENDPOINT` set
- `AZURE_SORA_MODEL` set (default: `sora-2`)
- Python 3.10+ with `requests` and `pyyaml`
- `ffmpeg` available in PATH

---

## Agent behavior (for AI assistants reading this)

- Always pass `--run-id` with a meaningful descriptive name
- Default to `--num-kids 3` (~32s ad); use `--num-kids 2` for a short (~24s)
- Mix time-of-day modes across batches for creative variety
- Report each clip status as it completes — never wait silently
- If a clip fails, continue remaining clips with `--kid-ids` to skip the failed one
- After completion, report merged file path and estimated total duration
- `--seconds 8` is the standard; use `12` for extended emotional moments
