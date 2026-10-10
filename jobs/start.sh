#!/bin/bash
# Start (or resume) one PC job in the background.   Usage:  bash jobs/start.sh <job number 1-10>
# The job keeps running after you close this tab, but keep the Ubuntu window open, the charger in
# and Windows sleep off. Finished sites are skipped when a job is started again.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
N="$1"; shift
if [ -z "$N" ]; then echo "Usage: bash jobs/start.sh <job number 1-10>"; exit 1; fi
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
J="$REPO/sims/biv_model/jobs_2026-10-07.py"
if tmux has-session -t "job$N" 2>/dev/null; then echo "Job $N is already running. Progress: bash jobs/status.sh"; exit 0; fi
python "$J" "$N" --check || exit 1
DIR="$(python "$J" "$N" --dir)"; mkdir -p "$DIR"
tmux new-session -d -s "job$N" -c "$REPO" \
  "source ~/venv_carputils/bin/activate; export PATH=/usr/local/lib/opencarp/lib/petsc/bin:\$PATH; python '$J' $N $* >> '$DIR/console.log' 2>&1"
sleep 5
echo "Job $N started at $(date +%H:%M)."
python "$J" --status | grep "^Job $N "
echo "Check progress any time:  bash jobs/status.sh      Pause:  bash jobs/stop.sh $N"
