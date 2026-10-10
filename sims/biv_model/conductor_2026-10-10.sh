#!/bin/bash
# Realistic volume conductor (15_conductor.py, Alex "Yes" 10 Oct 2026): per heart, one step at a time.
# Usage: bash conductor_2026-10-10.sh Y5HYEDL4 7D98EVAR 6G8DD8S5   (logs runs/2026-10-10_cb/)
cd "$(dirname "$0")"
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
L=../../runs/2026-10-10_cb; mkdir -p $L
for H in "$@"; do
  export HEART=$H
  for S in blood leadfield weights check rescore csv; do
    if [ $S = blood ] && [ -e ../../data/biv/$H/torso/full_nofast_blood.elem ]; then echo "$(date +%T) $H blood exists, skipped"; continue; fi
    if [ $S = leadfield ] && [ -e ../../runs/2026-10-10_LF_${H}_cb/POSTPROC_DIR/LF_V6.igb ]; then echo "$(date +%T) $H leadfield exists, skipped"; continue; fi
    echo "$(date +%T) $H $S start"
    python 15_conductor.py $S > $L/${S}_$H.log 2>&1 || { echo "$(date +%T) $H $S FAILED (see $L/${S}_$H.log)"; exit 1; }
    echo "$(date +%T) $H $S done"
  done
done
echo "$(date +%T) all done"
