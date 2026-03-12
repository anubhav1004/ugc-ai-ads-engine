# Latest Experiment Index

If someone opens the repo and asks, “What should I look at first?”, this is the answer.

## 1. Best Current Reaction System

Open:
- `experiments/reaction-pipeline/`

What it does:
- creates short reaction videos
- adds the top hook text
- applies same-phone pickup motion
- stitches the Professor Curious demo
- adds replacement trending-style audio

Best files:
- `experiments/reaction-pipeline/README.md`
- `experiments/reaction-pipeline/specs/front-selfie-sample.json`
- `experiments/reaction-pipeline/specs/side-table-sample.json`
- `experiments/reaction-pipeline/specs/side-table-dim-screenlight-sample.json`

Latest run folders:
- `experiments/reaction-pipeline/runs/side_table_sample_01/`
- `experiments/reaction-pipeline/runs/side_table_dim_screenlight_01/`

## 2. Reaction Hook Demo

Open:
- `experiments/reaction-hook-demo/`

What it is:
- a simple reaction-plus-demo format
- hook bar on top
- demo stitched after the reaction

Main file:
- `experiments/reaction-hook-demo/build_professor_curious_hook_demo.py`

## 3. Reaction Ad Batches

Open:
- `experiments/reaction-ads/`
- `experiments/reaction-ads-v2/`

What they are:
- batch-generated variations of the same reaction format
- different looks, hook lines, and prompt variants

Main files:
- `experiments/reaction-ads/build_batch.py`
- `experiments/reaction-ads-v2/build_batch.py`

## 4. India Raw-Footage Prompt Tests

Open:
- `experiments/india-raw-footage/`

What it is:
- India-specific ad ideation space
- prompt-test folders for new ad stories
- interview and confession angles

Best folders:
- `experiments/india-raw-footage/prompt-tests/doubt-mazak-street-interview/`
- `experiments/india-raw-footage/prompt-tests/school-corridor-confession/`
- `experiments/india-raw-footage/prompt-tests/ai-impact-summit-explainer/`

## 5. What Is Stored Here vs What Stays Local

The repo stores:
- prompts
- specs
- scripts
- overlays
- manifests
- research

Most final generated videos stay local and are usually gitignored.

So this file is the map to the systems, not a gallery of every output file.
