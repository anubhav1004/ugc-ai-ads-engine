## India Raw Footage Pipeline

This folder is the first character-consistency production scaffold for India-market ads.

It is intentionally separate from the existing generators so we can test a new workflow
without rewriting the current repo structure.

### Goal

Produce raw phone-camera style India ads with tighter recurring-character continuity.

### Production Model

1. Define a locked character pack.
2. Define a reusable raw-footage format template.
3. Define a setting pack.
4. Define a campaign brief for one ad.
5. Apply India-wide production defaults.
6. Compile the brief into a shot manifest and prompt pack.
7. Generate clips with Sora and/or Veo.
8. Stitch and edit using the shared editor.

### Why this exists

The current India generators are strong on emotional prompting, but they do not yet have
a dedicated character-consistency pipeline. This scaffold adds that layer.

### India-wide constraints

These are enforced through `india_defaults.json`.

- Duration presets: `20`, `30`, `40`, `50`, `60` seconds
- Export aspect ratios: `9:16`, `4:5`, `16:9`
- Every India ad must use the same locked outro asset
- The India outro audio and timing must not be changed
- Dialogue delivery quality is treated as a top-level constraint, not a nice-to-have

### Current Test

`campaigns/kota_boy_confession_night_01/`

This is the first single-video test:
- format: kid-to-camera confession
- character: Kota boy
- setting: hostel night room
- style: handheld front-camera realism
- audio: model-native audio preferred, no ElevenLabs required by default

### Folder Layout

```text
india-raw-footage/
├── campaigns/
├── characters/
├── formats/
├── settings/
└── scripts/
```

### Build the test manifest

```bash
python3 india-raw-footage/scripts/build_run.py \
  --campaign india-raw-footage/campaigns/kota_boy_confession_night_01/brief.json
```

The script writes:
- `build/run_manifest.json`
- `build/shot_01_prompt.txt`
- `build/shot_02_prompt.txt`
- `build/shot_03_prompt.txt`

These files are the source of truth for generation and later editing.
