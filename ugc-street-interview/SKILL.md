---
name: ugc-street-interview
description: Generate raw-footage UGC-style post-exam street interview ads for any edtech product. Vlogger with mic interviews school kids outside exam gate, Hindi dialogue, 9:16 vlog aesthetic, Azure Sora. Supports Class 10 boards, Class 12 boards, or general exam targeting.
---

# UGC Street Interview Ad Generator

Use this skill when the user wants to generate a street interview style ad for an edtech product.

## Trigger examples
- "Generate a street interview ad for MathsGuru, Class 10"
- "Create a Professor Curious boards ad, 12th grade, 3 kids"
- "Make a UGC school interview ad for [product]"
- "Run the street interview skill for [app name]"

## What this skill does
- Establishing shot → N kid interviews → outro, all stitched into one MP4
- Hindi dialogue, 9:16 vertical, raw vlog aesthetic, outdoor school gate setting
- Product name injected into every kid's response naturally
- Grade-specific dialogue and kid ages (10th: age 15-16, 12th: age 17-18, general: age 11-14)
- Vlogger appearance locked across all clips for continuity

## Preconditions
- `AZURE_OPENAI_API_KEY` set
- `AZURE_OPENAI_ENDPOINT` set
- `AZURE_SORA_MODEL` set (default: `sora-2`)
- Python with `requests` installed
- `ffmpeg` available

## Run
```bash
AZURE_OPENAI_API_KEY=<key> \
AZURE_OPENAI_ENDPOINT=<endpoint> \
AZURE_SORA_MODEL=sora-2 \
python3 /home/node/.openclaw/workspace/skills/ugc-street-interview/scripts/run.py \
  --product "Professor Curious" \
  --grade 10 \
  --run-id pc_10th_v1 \
  --num-kids 3 \
  --seconds 8
```

## Arguments
| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--product` | YES | — | Product/app name injected into every interview response |
| `--scene` | no | `school-gate` | Scene type — see scenes table below |
| `--run-id` | no | `run_001` | Unique name for this batch |
| `--num-people` | no | `3` | Number of interview clips (1–5) |
| `--person-ids` | no | random | Pick specific interviewees: `p01 p03` |
| `--seconds` | no | `8` | Seconds per clip (4 / 8 / 12) |
| `--output-dir` | no | `~/.openclaw/workspace/output/ugc-street-interview/` | Override output path |
| `--no-stitch` | no | false | Skip final merge |

## Scenes
| `--scene` | Setting | Who's interviewed | Tone |
|-----------|---------|-------------------|------|
| `school-gate` | Outside school after exam | School kids 11-14 | Happy, relieved, excited |
| `coaching-centre` | JEE/NEET coaching gate, evening | Aspirants 17-19 | Intense, driven, honest |
| `results-day` | School on board results morning | Students + parents | Emotional, raw, overwhelmed |
| `chai-stall` | Roadside chai stall near school | Students decompressing | Casual, candid, funny |
| `college-gate` | College gate after semester exam | 18-20 yr olds | Nostalgic, confident, aspirational |
| `parent-pickup` | Parent pickup zone outside school | Parents + kids together | Warm, proud, family energy |

## Output
`~/.openclaw/workspace/output/ugc-street-interview/<run-id>/`
- `clips/clip_01_establishing.mp4`
- `clips/clip_02_k01.mp4` ... (N kids)
- `clips/clip_NN_outro.mp4`
- `<run-id>_merged.mp4` ← final ad
- `manifest.json`

## Agent behavior
- Always ask for `--product` if not provided — it's required
- Default to `--num-kids 3` and `--seconds 8` unless user specifies otherwise
- Use `--grade 10` or `--grade 12` when user mentions board exams
- Report each clip's status as it completes
- After completion, report the merged file path and estimated duration
- If a clip fails, skip and continue with remaining clips

## Kid pool sizes
- `general`: 8 kids available
- `grade 10`: 5 kids available
- `grade 12`: 5 kids available
