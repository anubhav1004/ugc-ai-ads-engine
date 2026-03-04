---
name: ugc-us-college-interview
description: >
  Generate raw-footage UGC-style vlog interviews outside elite US universities (Harvard,
  MIT, Stanford, Yale, Princeton). Vlogger asks students "What did you use to get in?" —
  majority say the product, minority mention competitors (Khan Academy, Quizlet) for
  authenticity. English dialogue, 9:16 vertical, aspirational campus aesthetic, Azure Sora.
---

# UGC US College Interview Ad Generator

## Concept

**"I'm outside Harvard — let's ask students what they used to get in."**

A vlogger stands outside an elite US university gate and asks students one question:
*"What did you use to get in?"*

- **Majority say Professor Curious** — directly, clearly, by name
- **Minority mention competitors** (Khan Academy, Quizlet, Chegg) — then come around to Professor Curious
- Creates **social proof + FOMO**: if Harvard/MIT/Stanford students use it...
- Two-act clip structure: Act 1 (3-4s) the struggle → Act 2 (3-4s) Professor Curious as the answer

## Trigger examples
- "Generate a US college interview ad for Professor Curious at Harvard"
- "Make a UGC Stanford ad — students saying what got them in"
- "Run the US college interview skill, MIT scene"
- "Create a professor curious ivy league ad"

## Quick start

```bash
source ~/.env_azure
python3 ~/ugc-ai-ads-engine/ugc-us-college-interview/scripts/run.py \
  --product "Professor Curious" \
  --scene harvard \
  --run-id harvard_v1 \
  --num-people 3 \
  --seconds 8
```

## Arguments

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--product` | YES | — | Product name spoken in every interview |
| `--scene` | no | `harvard` | Campus scene — see table below |
| `--run-id` | no | `run_001` | Unique name for this batch |
| `--num-people` | no | `3` | Interview clips (1–5) |
| `--person-ids` | no | random | Pick specific people: `p01 p03` |
| `--seconds` | no | `8` | Seconds per clip (4 / 8 / 12) |
| `--output-dir` | no | `~/.openclaw/workspace/output/ugc-us-college-interview/` | Override output path |
| `--no-stitch` | no | false | Skip final ffmpeg merge |

## Scenes

| `--scene` | Campus | Setting | Tone |
|-----------|--------|---------|------|
| `harvard` | Harvard University | Johnston Gate, Cambridge MA, autumn | Competitive, aspirational, red-brick |
| `mit` | MIT | Massachusetts Ave entrance, Cambridge MA | Analytical, intense, technical |
| `stanford` | Stanford University | White Plaza / Main Quad, Palo Alto CA | Warm, open, California sun |
| `yale` | Yale University | Phelps Gate / Old Campus, New Haven CT | Literary, gothic, serious |
| `princeton` | Princeton University | Nassau Hall gate, Princeton NJ | Prestigious, historic, collegiate |
| `elite-campus` | Generic elite campus | Any top US university gate | Flexible, aspirational |

## Mix formula (per scene)

Each scene has 5 people. The default 3-person run randomly samples them:

| Person | Role |
|--------|------|
| p01 | Pure Professor Curious advocate — direct, no hesitation |
| p02 | "Tried Khan Academy / prep course → switched to Professor Curious" |
| p03 | "My friend/roommate/dorm was using Professor Curious" — social proof |
| p04 | "Quizlet for X, but Professor Curious for actual understanding" |
| p05 | Matter-of-fact certain — "easy answer, Professor Curious" |

## Output

`~/.openclaw/workspace/output/ugc-us-college-interview/<run-id>/`
- `clips/clip_01_establishing.mp4`
- `clips/clip_02_p01.mp4` ... (N interviews)
- `clips/clip_NN_outro.mp4`
- `<run-id>_merged.mp4` ← final stitched ad
- `manifest.json`

## Preconditions
- `AZURE_OPENAI_API_KEY` set (stored in `~/.env_azure`)
- `AZURE_OPENAI_ENDPOINT` set
- `AZURE_SORA_MODEL` set (default: `sora-2`)
- Python with `requests` installed
- `ffmpeg` available

## Difference from India skill (`ugc-street-interview`)

| | India (ugc-street-interview) | US (ugc-us-college-interview) |
|--|-------------------------------|-------------------------------|
| Setting | Kota coaching centres, school gates | Harvard, MIT, Stanford, Yale, Princeton |
| Language | Hindi | English |
| Angle | "Exam just happened — how did you prepare?" | "You got in — what did you use?" |
| Emotion | Raw pain, loneliness, Kota pressure | Aspiration, FOMO, social proof |
| Competitor mentions | No competitors | Yes — Khan Academy, Quizlet (minority) |
| Product position | Emotional saviour | The answer everyone smart converged on |
