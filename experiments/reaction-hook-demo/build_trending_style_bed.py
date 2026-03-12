#!/usr/bin/env python3
from __future__ import annotations

import math
import wave
from pathlib import Path


SR = 48000
DURATION = 31.9
OUT = Path("/Users/anubhavmishra/Desktop/ugc-ai-ads-engine/experiments/reaction-hook-demo/assets/trending_style_bed.wav")


def clamp(v: float) -> int:
    v = max(-1.0, min(1.0, v))
    return int(v * 32767)


def env_exp(t: float, decay: float) -> float:
    return math.exp(-t / decay) if t >= 0 else 0.0


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpm = 104.0
    beat = 60.0 / bpm
    eighth = beat / 2

    with wave.open(str(OUT), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SR)

        for n in range(int(DURATION * SR)):
            t = n / SR
            bar_pos = t % (beat * 4)
            mix = 0.0

            # Sub bass pulse on downbeats/eighths.
            bass_gate = 1.0 if (bar_pos % beat) < 0.18 else 0.0
            bass = 0.18 * bass_gate * math.sin(2 * math.pi * 52 * t)
            bass += 0.08 * bass_gate * math.sin(2 * math.pi * 104 * t)

            # Kick on beats 1 and 3.
            kick = 0.0
            for hit in (0.0, beat * 2):
                dt = bar_pos - hit
                if 0 <= dt < 0.18:
                    kick += 0.9 * env_exp(dt, 0.045) * math.sin(2 * math.pi * (110 - 70 * dt / 0.18) * dt)

            # Snare on beats 2 and 4.
            snare = 0.0
            for hit in (beat, beat * 3):
                dt = bar_pos - hit
                if 0 <= dt < 0.16:
                    noise = math.sin(2 * math.pi * 1800 * t) + math.sin(2 * math.pi * 2400 * t)
                    snare += 0.12 * env_exp(dt, 0.035) * noise

            # Closed hats on eighths.
            hats = 0.0
            dt = bar_pos % eighth
            if dt < 0.045:
                noise = math.sin(2 * math.pi * 4200 * t) + math.sin(2 * math.pi * 6200 * t)
                hats += 0.05 * env_exp(dt, 0.012) * noise

            # Simple pluck lead after the first 4s so the demo section lifts.
            lead = 0.0
            if t > 4:
                notes = [392.0, 440.0, 523.25, 440.0]
                note = notes[int((t - 4) / beat) % len(notes)]
                note_dt = (t - 4) % beat
                if note_dt < 0.26:
                    lead += 0.10 * env_exp(note_dt, 0.11) * math.sin(2 * math.pi * note * t)

            mix = bass + kick + snare + hats + lead
            # Soft limiter.
            mix = math.tanh(mix * 1.35) * 0.48
            sample = clamp(mix)
            wav.writeframesraw(sample.to_bytes(2, "little", signed=True) * 2)

    print(OUT)


if __name__ == "__main__":
    main()
