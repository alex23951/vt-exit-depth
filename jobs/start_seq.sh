#!/bin/bash
# Run several PC jobs one after the other in one background session.   Usage:  bash jobs/start_seq.sh 9 10
# Same rules as start.sh: keep the Ubuntu window open, the charger in and Windows sleep off; finished sites are
# skipped when started again. Pausing one job (bash jobs/stop.sh <n>) also stops the jobs after it.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { echo "Usage: bash jobs/start_seq.sh <job> [<job> ...]   e.g. bash jobs/start_seq.sh 9 10"; exit 1; }
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
J="$REPO/sims/biv_model/jobs_2026-10-07.py"
S="seq_$(echo "$@" | tr ' ' '_')"
if tmux has-session -t "$S" 2>/dev/null; then echo "Jobs $* are already running. Progress: bash jobs/status.sh"; exit 0; fi
for N in "$@"; do python "$J" "$N" --check > /dev/null || { echo "Job $N is not ready:"; python "$J" "$N" --check; exit 1; }; done
CMD="source ~/venv_carputils/bin/activate; export PATH=/usr/local/lib/opencarp/lib/petsc/bin:\$PATH"
for N in "$@"; do
  DIR="$(python "$J" "$N" --dir)"; mkdir -p "$DIR"
  CMD="$CMD; [ -e '$DIR/../STOP_SEQ' ] || python '$J' $N >> '$DIR/console.log' 2>&1; [ -e '$DIR/PAUSE' ] && touch '$DIR/../STOP_SEQ'"
done
rm -f "$(dirname "$DIR")/STOP_SEQ"
tmux new-session -d -s "$S" -c "$REPO" "$CMD; rm -f '$(dirname "$DIR")/STOP_SEQ'"
sleep 5
echo "Jobs $* started at $(date +%H:%M), one after the other."
python "$J" --status | grep -E "^Job ($(echo "$@" | tr ' ' '|')) "
echo "Check progress any time:  bash jobs/status.sh      Pause:  bash jobs/stop.sh <job now running>"
