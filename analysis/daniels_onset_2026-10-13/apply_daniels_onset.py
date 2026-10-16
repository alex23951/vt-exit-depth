#!/usr/bin/env python
"""
Daniels-onset MDI (rapid_onset.py, coordinator's frozen rule) on the control heart's saved network-v3 cb beats,
13 Oct 2026. SENSITIVITY only; read only.

Beats: Y5HYEDL4 runs/<run>_ecg_cb of RVOT (8), aortic cusp (8; the grid has no pulmonary-cusp sites), summit 90 % (2),
vein course 90 % (3), LV endocardium 10 % (free wall + septum, 18).
Conditions: (a) noise-free, zero-phase 2nd-order Butterworth 150 Hz low-pass; (b) 20 uV white noise in I, II, V1-V6 +
0.5-150 Hz band-pass + 50 Hz notch, the same 20 seeded realisations as analysis/noise_onset_2026-10-12 (noise_onset.one).
Per signal: measure_beat (ecg_depth_criteria 0.3.0, detected mode, plan baseline window) gives onset_ms and
offset_any_lead_ms; rapid_onset_mdi then gets the 12 leads (III, aVR, aVL, aVF derived from I and II) with the same
baseline window, at S = 0, 0.004, 0.006, 0.008, 0.009 mV/ms and S = 5.6 % of the signal's own peak 12-lead slope
(same 4 ms smoothing, within onset..offset).
Output: signals.csv (one row per beat x realisation x S), summary.csv, report.txt.
"""

import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
sys.path.insert(0, HERE)
from ecg_depth_criteria import from_leads, measure_beat          # noqa: E402
from scipy.signal import butter, sosfiltfilt                       # noqa: E402
import rapid_onset as RO                                            # noqa: E402

spec = importlib.util.spec_from_file_location('no', os.path.join(REPO, 'analysis', 'noise_onset_2026-10-12', 'noise_onset.py'))
NO = importlib.util.module_from_spec(spec); spec.loader.exec_module(NO)
LP = butter(2, 150.0, btype='lowpass', fs=1000.0, output='sos')
S_LIST = [0.0, 0.004, 0.006, 0.008, 0.009, 'rel5.6%']
KP = NO.KEEP_PRE
BASE = (KP - 45, KP - 5)


def twelve(Y8):
    I, II = Y8[0], Y8[1]
    return np.stack([I, II, II - I, -(I + II) / 2, I - II / 2, II - I / 2, *Y8[2:]])


def score(Y8, rows, meta):
    m = measure_beat(from_leads(dict(zip(NO.LEADS, Y8))), 1000.0, baseline_window_ms=BASE)
    on, off = int(round(m['onset_ms'])), int(round(m['offset_any_lead_ms']))
    X = twelve(Y8)
    Xb = X - np.median(X[:, BASE[0]:BASE[1]], axis=1, keepdims=True)
    pk = float((np.abs(np.gradient(RO._smooth(Xb, 1000.0, RO.SMOOTH_MS), axis=1))[:, on:off + 1]).max())
    for S in S_LIST:
        s = 0.056 * pk if S == 'rel5.6%' else S
        r = RO.rapid_onset_mdi(X, 1000.0, on, off, S=s, baseline=BASE)
        rows.append(dict(meta, S=S, S_mV_ms=round(s, 4), pkg_onset_ms=on - KP, pkg_mdi=m['mdi_daniels'], found=r['found'],
                         shift_ms=r['shift_ms'], mdi=r['mdi'], qrs_ms=r['qrs_ms'], peak_slope=round(pk, 4)))


def main():
    df = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', 'purk_Y5HYEDL4_cb.csv'))
    f, dp = df.family, df.depth_target
    fam = pd.Series(None, index=df.index, dtype=object)
    fam[f == 'rvot'] = 'RVOT'; fam[f == 'aortic_cusp'] = 'cusp'
    fam[(f == 'lv_summit') & (dp == 0.9)] = 'summit90'; fam[(f == 'lv_vein_course') & (dp == 0.9)] = 'vein90'
    fam[f.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)] = 'LVendo10'
    df['fam'] = fam
    rows = []
    for _, r in df[df.fam.notna()].iterrows():
        X, n = NO.load(r['run'])                                   # 8 leads, padded 1 s each side
        Ya = sosfiltfilt(LP, X, axis=1)[:, NO.PAD_PRE - KP: NO.PAD_PRE + n]
        score(Ya, rows, {'id': r['id'], 'family': r['fam'], 'cond': 'a_noisefree_lp150', 'real': 0})
        for k in range(NO.NREAL):
            Y = X + np.random.default_rng(1000 * k + 7).normal(0.0, 20 * 1e-3, X.shape)
            Y = NO.filtfilt(NO.NB, NO.NA, NO.sosfiltfilt(NO.SOS, Y, axis=1), axis=1)[:, NO.PAD_PRE - KP: NO.PAD_PRE + n]
            score(Y, rows, {'id': r['id'], 'family': r['fam'], 'cond': 'b_20uV_bp_notch', 'real': k})
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'signals.csv'), index=False)
    q = lambda x, p: float(np.percentile(x, p))
    out = []
    for (cond, S, fm), g in D.groupby(['cond', 'S', 'family'], sort=False):
        out.append({'cond': cond, 'S': S, 'family': fm, 'n_signals': len(g), 'mdi_median': round(g.mdi.median(), 3),
                    'mdi_iqr': f'{q(g.mdi, 25):.3f}-{q(g.mdi, 75):.3f}', 'pkg_mdi_median': round(g.pkg_mdi.median(), 3),
                    'not_found_pct': round(100 * (~g.found).mean(), 1), 'shift_median': q(g.shift_ms, 50),
                    'shift_p90': q(g.shift_ms, 90), 'shift_max': float(g.shift_ms.max()), 'qrs_median': g.qrs_ms.median(),
                    'S_mV_ms_median': round(g.S_mV_ms.median(), 4)})
    T = pd.DataFrame(out)
    T.to_csv(os.path.join(HERE, 'summary.csv'), index=False)
    lines = []
    for cond in T.cond.unique():
        for S in S_LIST:
            t = T[(T.cond == cond) & (T.S == S)].set_index('family')
            md = t.mdi_median
            order = min(md['summit90'], md['vein90'], md['cusp']) > md['RVOT'] > md['LVendo10']
            lines.append(f'{cond} S={S}: Daniels order {"PASS" if order else "fail"} (RVOT {md["RVOT"]:.3f}, cusp {md["cusp"]:.3f}, '
                         f'summit90 {md["summit90"]:.3f}, vein90 {md["vein90"]:.3f}, LV endo {md["LVendo10"]:.3f})')
    txt = T.to_string(index=False) + '\n\n' + '\n'.join(lines) + '\n'
    open(os.path.join(HERE, 'report.txt'), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
