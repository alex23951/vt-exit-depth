#!/bin/bash
# Run one lead-field job with a memory watchdog: if available memory falls below MIN_MB, kill openCARP / mpiexec
# (after the 10 Oct 00:16 out-of-memory crash). Usage: bash run_guarded.sh <args for lf_run.py>
MIN_MB=${MIN_MB:-900}
cd "$(dirname "$0")"
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
python lf_run.py "$@" &
PID=$!
PEAK=0
while kill -0 $PID 2>/dev/null; do
  AV=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  USED=$(( $(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo) - AV ))
  [ $USED -gt $PEAK ] && PEAK=$USED
  if [ "$AV" -lt "$MIN_MB" ]; then
    echo "$(date +%T) WATCHDOG: MemAvailable ${AV} MB < ${MIN_MB} MB, killing openCARP"
    pkill -x openCARP; pkill -x mpiexec; pkill -x hydra_pmi_proxy
    break
  fi
  sleep 2
done
wait $PID; RC=$?
echo "$(date +%T) exit $RC, peak used ${PEAK} MB"
exit $RC
