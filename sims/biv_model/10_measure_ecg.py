#!/usr/bin/env python
"""
Step 10: measure a simulated beat with the project's ecg_depth_criteria package
(code/ecg_depth_criteria, used via PYTHONPATH, version recorded in the output).

Two onset modes (study plan):
  detected : QRS onset and offsets detected from the ECG (no stimulus given)
  true     : onset = stimulus time, offset = last activation time from the simulation
The simulated ECG starts at the stimulus with no baseline before it, so PAD_MS of flat
signal (value at t = 0, i.e. 0 mV) is prepended; all reported times are shifted back so
0 ms = stimulus.

Usage: python 10_measure_ecg.py <POSTPROC_DIR> --stim-ms 0 --last-act-ms 118.6 [--region R] --out x.json
"""

import argparse
import json
import math
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# package folder: code/ecg_depth_criteria (current, 0.2.0) or e.g. code/ecg_depth_criteria_0.1.0
PKG = os.environ.get('ECG_PKG', os.path.join(REPO, 'code', 'ecg_depth_criteria'))
sys.path.insert(0, PKG)
import ecg_depth_criteria as edc                                   # noqa: E402
from ecg_depth_criteria import evaluate, from_leads, measure_beat  # noqa: E402

PAD_MS = 60          # flat 0 mV before the stimulus; the baseline window (40 ms ending 5 ms before onset) lies inside it


def clean(v):
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def main():
    p = argparse.ArgumentParser()
    p.add_argument('postproc')
    p.add_argument('--stim-ms', type=float, default=0.0)
    p.add_argument('--last-act-ms', type=float, required=True)
    p.add_argument('--region', default=None)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    leads = {}
    for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'):
        x = np.loadtxt(os.path.join(a.postproc, f'ECG_{l}.dat'))
        t, v = x[:, 0], x[:, 1]
        leads[l] = v
    dt = float(np.median(np.diff(t)))
    fs = 1000.0 / dt
    pad = int(round(PAD_MS / dt))
    leads = {k: np.concatenate([np.full(pad, v[0]), v]) for k, v in leads.items()}
    shift = PAD_MS - t[0]
    ecg = from_leads(leads)
    out = {'package_version': edc.__version__, 'fs_hz': fs, 'pad_ms': PAD_MS,
           'time_note': 'all times in ms after the stimulus (padding removed)', 'region': a.region}
    # without a stimulus the package otherwise uses the first 40 ms as baseline; with a
    # 20 ms pad that window took in the start of the QRS (bug in this script, fixed 2026-10-03)
    # plan's baseline window: 40 ms ending 5 ms before the true onset (the stimulus)
    on = a.stim_ms + shift
    bw = (on - 45.0, on - 5.0)
    out['baseline_window_ms'] = [bw[0] - shift, bw[1] - shift]
    modes = {'detected': dict(baseline_window_ms=bw),
             'true': dict(onset_ms=a.stim_ms + shift, offset_ms=a.last_act_ms + shift, baseline_window_ms=bw)}
    for name, kw in modes.items():
        m = measure_beat(ecg, fs, **kw)
        c = evaluate(m, a.region)
        m = clean(m)
        for k, v in list(m.items()):
            if k.endswith('_ms') and isinstance(v, (int, float)) and k in ('onset_ms', 'visible_onset_ms', 'offset_precordial_ms', 'offset_any_lead_ms'):
                m[k] = v - shift
        out[name] = {'measurements': m, 'criteria': clean(c)}
    json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
