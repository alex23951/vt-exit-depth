#!/bin/bash
# Full per-heart pipeline (steps 1-10) for one cohort heart.
# Usage: bash sims/biv_model/run_heart.sh <HEART_ID> <RUN_DATE_PREFIX>
# Writes data/biv/<HEART>/ (git-ignored) and runs/<prefix>_<HEART>_* ; a log per step in
# runs/<prefix>_<HEART>_pipeline/. Stops at the first failing step.
set -euo pipefail
H=$1; P=$2
R=$(cd "$(dirname "$0")/../.." && pwd)
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH
export HEART=$H RUN_PREFIX=${P}_${H}_patch
L=$R/runs/${P}_${H}_pipeline; mkdir -p $L
cd $R/sims/biv_model
step() { local n=$1; shift; local s=$(date +%s); echo "[$(date +%T)] $n ..."; "$@" > $L/$n.log 2>&1; echo "[$(date +%T)] $n done ($(( $(date +%s)-s )) s)"; }
step 01_extract     python 01_extract.py
step 02_laplace     python 02_laplace.py --np 6
step 03_uvc         python 03_uvc.py
step 04_fibres      python 04_fibres.py
step 05_fastlayer   python 05_fastlayer.py
step 07_calibrate   python 07_patch_tune.py --auto
step 08a_atrialfit  python 08a_atrial_fit.py
step 08_place       python 08_torso.py place
step 08_mesh        python 08_torso.py mesh
step 08_electrodes  python 08_torso.py electrodes
step 06_fullqrs     python 06_check_run.py --tend 140 --spacedt 1 --np 6 --ID ${P}_${H}_fullqrs
step 08_leadfield   python 08_torso.py leadfield --vm $R/runs/${P}_${H}_fullqrs/vm.igb --run-id ${P}_${H}_ecg --ecg-dt 1 --tend 140
step 09_plot        python 09_plot_ecg.py $R/runs/${P}_${H}_ecg/POSTPROC_DIR $R/runs/${P}_${H}_ecg/ecg12.png --title "$H, LV free-wall endo, mid"
LAST=$(python -c "import json;print(json.load(open('$R/runs/${P}_${H}_fullqrs/summary_06.json'))['total_activation_ms'])")
step 10_measure     python 10_measure_ecg.py $R/runs/${P}_${H}_ecg/POSTPROC_DIR --stim-ms 0 --last-act-ms $LAST --out $R/runs/${P}_${H}_ecg/criteria.json
echo "[$(date +%T)] all steps done for $H"
