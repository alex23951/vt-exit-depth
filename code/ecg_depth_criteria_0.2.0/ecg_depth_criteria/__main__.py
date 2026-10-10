"""Measure one beat from a CSV file and print the measurements and criteria as JSON.

The CSV has a header row naming the leads (at least I, II and V1-V6; missing
III, aVR, aVL and aVF are derived; a "time" column is ignored) and one row
per sample, in mV.

    python -m ecg_depth_criteria beat.csv --fs 1000 --stim-ms 40 --region lv_basal_superior
"""
import argparse
import json
import math

import numpy as np

from .criteria import REGIONS, evaluate
from .leads import from_leads
from .measure import measure_beat


def _jsonable(v):
    """NaN becomes null; numpy scalars become Python values."""
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m ecg_depth_criteria", description=__doc__.splitlines()[0])
    p.add_argument("csv")
    p.add_argument("--fs", type=float, required=True, help="sampling rate, Hz")
    p.add_argument("--stim-ms", type=float, help="pacing stimulus time; intervals then start at the stimulus")
    p.add_argument("--onset-ms", type=float, help="QRS onset, overrides detection")
    p.add_argument("--offset-ms", type=float, help="QRS offset, overrides detection")
    p.add_argument("--region", choices=REGIONS, help="pacing or exit region; adds the Bazan criteria")
    a = p.parse_args(argv)

    table = np.genfromtxt(a.csv, delimiter=",", names=True, deletechars="", autostrip=True)
    ecg = from_leads({k: table[k] for k in table.dtype.names if k.lower() != "time"})
    m = measure_beat(ecg, a.fs, stim_ms=a.stim_ms, onset_ms=a.onset_ms, offset_ms=a.offset_ms)
    print(json.dumps(_jsonable({"measurements": m, "criteria": evaluate(m, a.region)}), indent=2))


if __name__ == "__main__":
    main()
