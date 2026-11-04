#!/bin/bash
# Resume a chunk paused by pause.sh. The runner notices the pause, moves the chunk's end by the paused time and does not
# count it as a stall.
R=$(pgrep -x openCARP; pgrep -x mpiexec; pgrep -f hydra_pmi_proxy)
D=$(pgrep -f "t1_27.py night")
if [ -z "$D$R" ]; then echo "Nothing is paused or running."; exit 0; fi
[ -n "$R" ] && kill -CONT $R
[ -n "$D" ] && kill -CONT $D
echo "Resumed at $(date +%H:%M): $(echo $R | wc -w) simulation process(es) and the runner."
