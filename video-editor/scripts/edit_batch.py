#!/usr/bin/env python3
"""
Batch Editor — Edit all existing UGC ad runs at once.

Finds all run directories under ~/.openclaw/workspace/output/ that have a
manifest.json + clips/ folder and runs edit.py on each.

Usage:
  python3 edit_batch.py                              # edit everything, warm grade
  python3 edit_batch.py --style cinematic --end-card --send-slack
  python3 edit_batch.py --dirs exp_01_ek_raat exp_02_bag_pack  # specific runs
  python3 edit_batch.py --output-root ~/.openclaw/workspace/output/ugc-experiments
"""

import argparse
import subprocess
import sys
from pathlib import Path

EDIT_SCRIPT   = Path(__file__).parent / "edit.py"
DEFAULT_ROOT  = Path.home() / ".openclaw" / "workspace" / "output"
DEFAULT_LOGO  = Path.home() / "ugc-ai-ads-engine" / "assets" / "pc_logo.png"


def find_run_dirs(root: Path) -> list[Path]:
    """Recursively find all dirs that have manifest.json + clips/ subdir."""
    runs = []
    for manifest in sorted(root.rglob("manifest.json")):
        run_dir = manifest.parent
        if (run_dir / "clips").is_dir():
            runs.append(run_dir)
    return runs


def main():
    parser = argparse.ArgumentParser(description="Batch UGC Video Editor")
    parser.add_argument("--output-root", default=str(DEFAULT_ROOT),
                        help="Root directory to search for run dirs")
    parser.add_argument("--dirs",        nargs="*",
                        help="Specific run directory names to process")
    parser.add_argument("--style",       default="warm",
                        choices=["warm", "cinematic", "cool", "neutral"])
    parser.add_argument("--transition",  default="fade")
    parser.add_argument("--logo",        default=str(DEFAULT_LOGO),
                        help="Logo PNG path")
    parser.add_argument("--end-card",    action="store_true")
    parser.add_argument("--send-slack",  action="store_true")
    parser.add_argument("--cta-text",    default="Download Professor Curious")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip runs that already have an _edited.mp4")
    args = parser.parse_args()

    root = Path(args.output_root).expanduser()
    all_runs = find_run_dirs(root)

    if args.dirs:
        all_runs = [r for r in all_runs if r.name in args.dirs]

    if not all_runs:
        sys.exit(f"[ERROR] No run dirs found under {root}")

    print(f"\nFound {len(all_runs)} run(s) to edit:\n")
    for r in all_runs:
        print(f"  {r}")

    ok = 0
    failed = []

    for run_dir in all_runs:
        # Skip if already edited
        edited_files = list(run_dir.glob("*_edited.mp4"))
        if args.skip_existing and edited_files:
            print(f"\n[skip] {run_dir.name} (already has {edited_files[0].name})")
            ok += 1
            continue

        print(f"\n{'─'*55}")
        print(f"Editing: {run_dir.name}")
        print(f"{'─'*55}")

        cmd = [
            sys.executable, str(EDIT_SCRIPT),
            "--run-dir",    str(run_dir),
            "--style",      args.style,
            "--transition", args.transition,
            "--cta-text",   args.cta_text,
        ]
        if args.logo and Path(args.logo).expanduser().exists():
            cmd += ["--logo", str(Path(args.logo).expanduser())]
        if args.end_card:
            cmd.append("--end-card")
        if args.send_slack:
            cmd.append("--send-slack")

        result = subprocess.run(cmd)
        if result.returncode == 0:
            ok += 1
        else:
            failed.append(run_dir.name)
            print(f"  [ERROR] Failed: {run_dir.name}")

    print(f"\n{'='*55}")
    print(f"  Batch complete: {ok} edited, {len(failed)} failed")
    if failed:
        print(f"  Failed: {', '.join(failed)}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
