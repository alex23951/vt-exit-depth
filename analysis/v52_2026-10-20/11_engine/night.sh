#!/bin/bash
# One unattended ~8 h chunk of the 27-site engine test (t1_27.py night): RE+ beats side by side, then monodomain beats.
# Usage: bash ~/vt-exit-depth/analysis/v52_2026-10-20/11_engine/night.sh [hours, default 8]
# Leave the PC on (no sleep) and the Ubuntu window open until it ends; it stops by itself and picks up next time.
cd ~/vt-exit-depth || exit 1
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
if pgrep -x openCARP > /dev/null; then echo "openCARP is already running, so nothing was started."; exit 1; fi
mkdir -p runs/v52_2026-10-20/11_engine/logs
LOG=runs/v52_2026-10-20/11_engine/logs/night_$(date +%Y%m%d_%H%M).log
nohup python -B analysis/v52_2026-10-20/11_engine/t1_27.py night "${1:-8}" > "$LOG" 2>&1 &
sleep 5
if kill -0 $! 2> /dev/null; then
  echo "Started. It stops by itself within ${1:-8} hours. Log: ~/vt-exit-depth/$LOG"
else
  echo "It did not start:"; tail -5 "$LOG"
fi
