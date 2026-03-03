# UGC AI Ads Engine

Generate authentic UGC-style video ads using Azure Sora. Raw footage, street interviews, Hindi scripts — no actors, no studio.

## What's in here

### `professor-curious-street-interview/`
Generates post-exam street interview ads for edtech apps.
- Vlogger with mic interviews school kids outside exam gate
- Hindi dialogue, 9:16 vertical, raw vlog aesthetic
- Supports Class 10 boards, Class 12 boards, or general
- Auto-stitches clips into a final merged MP4

**Run:**
```bash
AZURE_OPENAI_API_KEY=<key> \
AZURE_OPENAI_ENDPOINT=<endpoint> \
AZURE_SORA_MODEL=sora-2 \
python3 professor-curious-street-interview/scripts/run.py \
  --run-id ad_v1 \
  --grade 10 \
  --num-kids 3 \
  --seconds 8
```

**Grades:**
- `--grade 10` → Class 10 CBSE boards (Maths, Science, SST)
- `--grade 12` → Class 12 CBSE boards (Physics, Chemistry, JEE/NEET)
- No flag → general exam setting

## Requirements
- Python 3.11+
- `requests`, `pyyaml`
- `ffmpeg`
- Azure OpenAI access with Sora deployment

## Output
`output/<run-id>/`
- `clips/` — individual Sora-generated clips
- `<run-id>_merged.mp4` — final stitched ad
- `manifest.json` — clip metadata and video IDs
