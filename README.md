# UGC AI Ads Engine

Generate authentic UGC-style video ads using Azure Sora. Raw footage, street interviews — no actors, no studio.

> **Context:** See [CONTEXT.md](./CONTEXT.md) for full session history, run instructions, and where we left off.

---

## Skills

### `ugc-street-interview/` — India Market
Vlogger interviews students outside coaching centres and school gates in Kota.
Hindi dialogue. Emotional, raw, Kota pressure angle.

**"Exam khatam hua — Professor Curious ne help ki."**

```bash
source ~/.env_azure
python3 ugc-street-interview/scripts/run.py \
  --product "Professor Curious" \
  --scene kota-coaching \
  --run-id kota_v1 \
  --num-people 3 \
  --seconds 8
```

**Scenes:** `kota-coaching` (default), `school-gate`, `coaching-centre`, `results-day`, `chai-stall`, `college-gate`, `parent-pickup`

---

### `ugc-us-college-interview/` — US Market
Vlogger outside Harvard, MIT, Stanford, Yale, Princeton asks students:
*"What did you use to get in?"* — majority say Professor Curious.
English dialogue. Aspirational FOMO + social proof angle.

**"I'm outside Harvard. Let's ask students what they used to get in."**

```bash
source ~/.env_azure
python3 ugc-us-college-interview/scripts/run.py \
  --product "Professor Curious" \
  --scene harvard \
  --run-id harvard_v1 \
  --num-people 3 \
  --seconds 8
```

**Scenes:** `harvard` (default), `mit`, `stanford`, `yale`, `princeton`, `elite-campus`

---

### `professor-curious-street-interview/` — PC India (Grade-specific)
Original PC-specific skill. Grade-based targeting (Class 10 / Class 12 boards).

---

## Requirements
- Python 3.11+ with `requests` installed
- `ffmpeg`
- Azure OpenAI with Sora deployment

**Credentials:** stored in `~/.env_azure`, auto-loaded via `~/.zshrc`

## Output
`~/.openclaw/workspace/output/<skill-name>/<run-id>/`
- `clips/` — individual Sora-generated MP4s
- `<run-id>_merged.mp4` — final stitched ad
- `manifest.json`
