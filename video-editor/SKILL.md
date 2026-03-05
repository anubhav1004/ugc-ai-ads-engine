# Video Editor Skill

Post-processing pipeline for AI-generated UGC ads.
Turns raw Sora clips into polished, publish-ready ads.

---

## What It Does

| Step | What's Applied |
|------|---------------|
| Color grade | Warm/cinematic/cool tone via `colorbalance` + `eq` |
| Vignette | Subtle darkened edges for cinematic feel |
| Hook text | Big white text on establishing shot (first 3s) |
| CTA text | "Download Professor Curious" overlaid on outro |
| Logo bug | Small PC logo pinned bottom-right on every clip |
| Transitions | Cross-fade between clips (`xfade` + `acrossfade`) |
| End card | Optional 2.5s black card with logo + product name |
| Audio | Loudnorm to –16 LUFS, 48kHz AAC |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `edit.py` | Edit a single run directory |
| `edit_batch.py` | Edit all existing runs at once |

---

## Usage

### Single run
```bash
python3 ~/ugc-ai-ads-engine/video-editor/scripts/edit.py \
  --run-dir ~/.openclaw/workspace/output/ugc-experiments/exp_01_ek_raat \
  --hook-text "Raat ke 11 baje. Akela." \
  --logo ~/ugc-ai-ads-engine/assets/pc_logo.png \
  --style warm \
  --transition fade \
  --end-card \
  --send-slack
```

### All experimental ads
```bash
python3 ~/ugc-ai-ads-engine/video-editor/scripts/edit_batch.py \
  --output-root ~/.openclaw/workspace/output/ugc-experiments \
  --logo ~/ugc-ai-ads-engine/assets/pc_logo.png \
  --style warm \
  --end-card \
  --send-slack
```

### Specific runs
```bash
python3 ~/ugc-ai-ads-engine/video-editor/scripts/edit_batch.py \
  --dirs exp_01_ek_raat exp_02_bag_pack exp_03_rank_wala \
  --style cinematic \
  --transition wipeleft \
  --end-card
```

---

## Style Options

| Style | Best For |
|-------|---------|
| `warm` | India/Kota emotional ads — golden, human |
| `cinematic` | Dramatic moments — desaturated, filmic |
| `cool` | US college ads — crisp, aspirational |
| `neutral` | Minimal touch, preserve Sora's look |

---

## Transition Options (xfade)

`fade` (default) | `wipeleft` | `slideleft` | `circlecrop` | `dissolve` | `diagtl` | `pixelize`

---

## Output

Edited video lands next to the merged video:
```
~/.openclaw/workspace/output/<series>/<run-id>/
├── clips/                  ← raw Sora clips
├── processed/              ← graded + overlaid clips (intermediate)
├── <run-id>_merged.mp4     ← raw stitch (old)
└── <run-id>_edited.mp4     ← ✅ polished output (new)
```

---

## Hook Text Ideas

| Scene | Suggested Hook Text |
|-------|-------------------|
| ek-raat (11pm alone) | `Raat ke 11 baje. Akela.` |
| bag-pack (quitting Kota) | `Bag pack kar liya. Ghar jaana tha.` |
| rank-wala (AIR 89) | `AIR 89 wala student kya use karta tha?` |
| pehla-din (first day) | `Kota ka pehla din. Parents abhi gaye.` |
| mock-result (results day) | `Mock results aaye. Reactions real hain.` |
