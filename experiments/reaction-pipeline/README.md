# Reaction Pipeline

Reusable pipeline for Professor Curious reaction-style ads.

## What it does

This pipeline generates:
- a short reaction clip
- same-phone pickup motion in post
- a top black hook bar
- the full Professor Curious demo clip
- trending-style replacement audio

## Why it exists

The main prompt challenge was camera logic.

The validated rule is:
- the recording device is the same phone
- no second phone should appear in the frame
- pickup motion should feel physical, not fake

For `front-selfie`, the pickup can be hinted in generation and reinforced in post.

For `side-table`, the stronger path is:
- generate the seated reaction only
- add the pickup motion later in post on the same frame sequence

## Main runner

```bash
python3 experiments/reaction-pipeline/run_reaction_pipeline.py \
  --spec experiments/reaction-pipeline/specs/front-selfie-sample.json
```

## Specs

- `specs/front-selfie-sample.json`
- `specs/side-table-sample.json`
- `specs/side-table-dim-screenlight-sample.json`

## Outputs

Each run writes:
- `prompts/reaction.json`
- `assets/reaction_hook.png`
- `assets/demo_hook.png`
- `output/reaction_raw.mp4`
- `output/reaction_motion.mp4`
- `output/segment_01_reaction.mp4`
- `output/segment_02_demo.mp4`
- `output/final.mp4`
- `output/final_trending_audio.mp4`

Generated outputs remain gitignored. The pipeline source, prompts, specs, and overlays are kept in the repo.
