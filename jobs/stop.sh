#!/bin/bash
# Pause a PC job: the beats already running finish, then it stops.   Usage:  bash jobs/stop.sh <job number>
REPO="$(cd "$(dirname "$0")/.." && pwd)"
source ~/venv_carputils/bin/activate
DIR="$(python "$REPO/sims/biv_model/jobs_2026-10-07.py" "$1" --dir)" || exit 1
touch "$DIR/PAUSE"
echo "Job $1 will stop once the beats now running finish (a few minutes for a grid, up to ~45 min for a monodomain beat)."
echo "Resume later with:  bash jobs/start.sh $1   (finished sites are skipped)"
