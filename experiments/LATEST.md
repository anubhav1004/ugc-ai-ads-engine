# Latest Experiment Index

This file points to the latest active experiment systems in the repo.

## Reaction Pipeline

Location:
- `experiments/reaction-pipeline/`

Purpose:
- generate reaction-first UGC ads
- apply validated same-phone pickup motion in post
- add top hook overlay
- stitch the Professor Curious demo
- replace original audio with the trending-style bed

Main runner:
- `experiments/reaction-pipeline/run_reaction_pipeline.py`

Current presets:
- `front-selfie`
- `side-table`

Current sample specs:
- `experiments/reaction-pipeline/specs/front-selfie-sample.json`
- `experiments/reaction-pipeline/specs/side-table-sample.json`
- `experiments/reaction-pipeline/specs/side-table-dim-screenlight-sample.json`

Latest generated runs:
- `experiments/reaction-pipeline/runs/side_table_sample_01/`
- `experiments/reaction-pipeline/runs/side_table_dim_screenlight_01/`

## Reaction Hook Demo

Location:
- `experiments/reaction-hook-demo/`

Purpose:
- single reaction clip + Snapchat-style hook bar + full Professor Curious demo + trending-style audio

Main builder:
- `experiments/reaction-hook-demo/build_professor_curious_hook_demo.py`

## Reaction Ad Batches

Locations:
- `experiments/reaction-ads/`
- `experiments/reaction-ads-v2/`

Purpose:
- batch American-character reaction ads with different appearances, hooks, and the same demo structure

Main batch scripts:
- `experiments/reaction-ads/build_batch.py`
- `experiments/reaction-ads-v2/build_batch.py`

## India Raw-Footage Prompt Tests

Location:
- `experiments/india-raw-footage/`

Purpose:
- India-market UGC concept tests
- interview formats
- reaction-format tests
- raw-footage prompt experiments

Prompt-test folders:
- `experiments/india-raw-footage/prompt-tests/doubt-mazak-street-interview/`
- `experiments/india-raw-footage/prompt-tests/school-corridor-confession/`
- `experiments/india-raw-footage/prompt-tests/ai-impact-summit-explainer/`

## Notes On Generated Outputs

Generated MP4 outputs remain gitignored by design.

The repo stores:
- runners
- specs
- prompts
- overlays
- research
- manifests

The actual generated video outputs remain present in the local workspace under the corresponding `output/` folders.
