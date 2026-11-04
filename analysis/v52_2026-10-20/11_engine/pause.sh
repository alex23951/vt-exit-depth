#!/bin/bash
# Pause a running night chunk (t1_27.py night and its openCARP runs) without losing any progress; resume with resume.sh.
# The runs keep their memory while paused. Do not shut down or restart Ubuntu/Windows while paused.
D=$(pgrep -f "t1_27.py night")
R=$(pgrep -x openCARP; pgrep -x mpiexec; pgrep -f hydra_pmi_proxy)
if [ -z "$D$R" ]; then echo "Nothing is running, so nothing was paused."; exit 0; fi
[ -n "$D" ] && kill -STOP $D
[ -n "$R" ] && kill -STOP $R
echo "Paused at $(date +%H:%M): $(echo $R | wc -w) simulation process(es) and the runner. Resume with:"
echo "  bash ~/vt-exit-depth/analysis/v52_2026-10-20/11_engine/resume.sh"
