#!/bin/bash
# Progress of every PC job (times are the PC's clock).   Usage:  bash jobs/status.sh
REPO="$(cd "$(dirname "$0")/.." && pwd)"
source ~/venv_carputils/bin/activate
python "$REPO/sims/biv_model/jobs_2026-10-07.py" --status
