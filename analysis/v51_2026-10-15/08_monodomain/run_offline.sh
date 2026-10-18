#!/usr/bin/env bash
# Starts the 27-site monodomain beats (mono51.py run) for the hearts given, one heart after the other, detached from the
# terminal and from Claude, so the job needs no internet and keeps running if Claude's session disconnects.
# It stops at the first heart that ends with an error (memory guard, openCARP failure). Finished beats are skipped on a
# restart. Progress: bash analysis/v51_2026-10-15/08_monodomain/status_offline.sh
# Usage (from anywhere): bash ~/vt-exit-depth/analysis/v51_2026-10-15/08_monodomain/run_offline.sh Y5HYEDL4 [6G8DD8S5 7D98EVAR]
set -u
cd "$(dirname "$(readlink -f "$0")")/../../.." || exit 1
[ $# -ge 1 ] || { echo "give at least one heart, e.g. Y5HYEDL4"; exit 1; }
if pgrep -x openCARP > /dev/null; then echo "openCARP is already running; not starting a second job"; exit 1; fi
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
LOG=runs/v51_2026-10-15/08_monodomain/offline_$(date +%Y%m%d_%H%M).log
mkdir -p runs/v51_2026-10-15/08_monodomain
setsid nohup bash -c '
for H in "$@"; do
  echo "$(date "+%F %T") start $H"
  HEART=$H python -B analysis/v51_2026-10-15/08_monodomain/mono51.py run || { echo "$(date "+%F %T") $H stopped with an error"; exit 1; }
  echo "$(date "+%F %T") done $H"
done
echo "$(date "+%F %T") all done"
' _ "$@" > "$LOG" 2>&1 < /dev/null &
echo "started at $(date '+%H:%M') (process $!); log: $LOG"
