---
name: professor-curious-street-interview
description: Generate raw-footage-style Hindi street interview ad clips for Professor Curious app. School kids outside exam, vlog format, 9:16, Azure Sora. Auto-stitches into a final merged video.
---

# Professor Curious — Street Interview Ad Generator

Use this skill when the user wants to generate street interview ad videos for Professor Curious.

## What this skill does
- Generates 3-part clip structure: establishing shot → N kid interviews → outro
- All clips: raw vlog aesthetic, 9:16, outdoor school gate, Hindi interview style
- Kids randomly selected from a dialogue bank (8 unique kid profiles)
- Submits all clips to Azure Sora API, polls until done, downloads each
- Stitches all clips into one merged MP4 via ffmpeg

## Preconditions
- `AZURE_OPENAI_API_KEY` is set
- `AZURE_OPENAI_ENDPOINT` is set
- `AZURE_SORA_MODEL` is set (default: `sora-2`)
- Python with `requests` and `pyyaml` installed
- `ffmpeg` available

## Run
```bash
AZURE_OPENAI_API_KEY=<key> \
AZURE_OPENAI_ENDPOINT=<endpoint> \
AZURE_SORA_MODEL=sora-2 \
python3 /home/node/.openclaw/workspace/skills/professor-curious-street-interview/scripts/run.py \
  --run-id ad_v1 \
  --num-kids 3 \
  --seconds 8
```

## Arguments
| Arg | Default | Description |
|-----|---------|-------------|
| `--run-id` | `run_001` | Unique name for this batch |
| `--num-kids` | `3` | How many kid interview clips (1–8) |
| `--kid-ids` | random | Pick specific kids by ID (e.g. `kid_01 kid_04`) |
| `--seconds` | `8` | Seconds per clip (4 / 8 / 12) |
| `--output-dir` | `~/.openclaw/workspace/output/professor-curious-street-interview/` | Override output path |
| `--no-stitch` | false | Skip final ffmpeg merge |

## Output
`~/.openclaw/workspace/output/professor-curious-street-interview/<run-id>/`

Files:
- `clips/clip_01_establishing.mp4`
- `clips/clip_02_kid_01.mp4` ... (N kids)
- `clips/clip_NN_outro.mp4`
- `<run-id>_merged.mp4` ← final ad
- `manifest.json`

## Dialogue bank
Edit `references/dialogue-bank.yaml` to add/modify kid responses, vlogger lines, or kid emotions.
Current kids: `kid_01` through `kid_08` (boy/girl mix, varied emotions).

## Agent behavior
- Always pass `--run-id` with a meaningful name (e.g. `ad_batch_01`, `pc_exam_v2`)
- Default to `--num-kids 3` for a ~32s ad; use `--num-kids 2` for a ~24s short
- Report each clip's status as it completes — do not wait silently
- If a clip fails, report the error and continue with remaining clips using `--kid-ids` to skip the failed one
- After completion, report the merged file path and total duration estimate
