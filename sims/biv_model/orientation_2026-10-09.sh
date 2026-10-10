#!/bin/bash
# Heart-orientation sensitivity of the ECG (9 Oct 2026, Alex "go"): control heart rotated in the frontal plane,
# new torso mesh, electrodes, no-layer lead fields and ECG weights per orientation. Usage: bash orientation_2026-10-09.sh 20 -20
set -e
cd "$(dirname "$0")"
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
export HEART=Y5HYEDL4
for A in "$@"; do
  export TORSO_ROT_FRONTAL_DEG=$A TORSO_SUFFIX="_rot$A"
  L=../../runs/2026-10-09_orient; mkdir -p $L
  T=../../data/biv/$HEART/torso_rot$A
  RID=2026-10-09_LF_${HEART}_nofast_rot$A
  W=../../data/biv/$HEART/ecgW_nofast_rot$A.npz
  echo "$(date +%T) rot $A start"
  [ -e $T/full.elem ] || { python 08_torso.py place > $L/place_$A.log 2>&1; python 08_torso.py mesh > $L/mesh_$A.log 2>&1; }
  [ -e $T/electrodes/V6.vtx ] || python 08_torso.py electrodes > $L/electrodes_$A.log 2>&1
  [ -e $T/full_nofast.elem ] || python 08_torso.py variants > $L/variants_$A.log 2>&1
  [ -e ../../runs/$RID/POSTPROC_DIR/LF_V6.igb ] || python 08_torso.py leadfield --vm ../../runs/2026-10-02_biv_fullqrs/vm.igb --run-id $RID --ecg-dt 1 --tend 140 --full full_nofast > $L/leadfield_$A.log 2>&1
  [ -e $W ] || python 13_fast_ecg.py weights --mesh ../../data/biv/$HEART/bivF --lf-dir ../../runs/$RID/POSTPROC_DIR --sigma m --c -1 --out $W --nofast > $L/weights_$A.log 2>&1
  echo "$(date +%T) rot $A done"
done
