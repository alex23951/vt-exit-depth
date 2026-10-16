#!/usr/bin/env python
"""
Noise and filtering vs detected-onset measures, 12 Oct 2026 (coordinator brief; read only: existing network-v3 cb ECGs of
the 432 grid sites, no new beats, no lead fields).

Why: clinical PVC origins precede the visible QRS onset by 22-41 ms (RVOT about 24 ms, Bogun 2008); our ECGs are
noise-free and unfiltered, so the detected onset sits a few ms after the stimulus.

Per site and noise level (0, 10, 20, 40 uV RMS; 20 seeded realisations, 1 for 0 uV):
  1 trace = runs/<run>_ecg_cb/POSTPROC_DIR, 1 kHz, starting at the stimulus; padded with its value at the stimulus,
    PAD_PRE = 1000 ms before and PAD_POST = 1000 ms after (flat baseline, so the filter has room)
  2 white Gaussian noise, independently in each recorded independent lead (I, II, V1-V6); III, aVR, aVL, aVF are derived
    from the noisy I and II by the package (from_leads), as an electrocardiograph does
  3 Zheng-style filtering (ASSUMPTION on the order: the brief gives only the bands): 2nd-order Butterworth band-pass
    0.5-150 Hz plus a 50 Hz IIR notch (Q 30), both zero-phase (sosfiltfilt / filtfilt)
  4 cut to 60 ms before the stimulus .. end of the trace; ecg_depth_criteria 0.3.0, DETECTED onset, baseline window =
    the plan's 40 ms ending 5 ms before the stimulus (as 10_measure_ecg.py)
Per site: median over realisations of onset - stimulus, QRS, pseudo-delta, MDI (Daniels), time from detected onset to
the largest precordial deflection (= MDI x any-lead QRS, the package's own definition).

Usage: python noise_onset.py time | run [workers]      Output: this folder (sites.csv, summary.csv, report.txt)
"""

import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.signal import butter, iirnotch, filtfilt, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
from ecg_depth_criteria import from_leads, measure_beat     # noqa: E402

RUNS = os.path.join(REPO, 'runs')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LEADS = ['I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
LEVELS_UV = [0, 10, 20, 40]
NREAL = 20
FS = 1000.0
PAD_PRE, PAD_POST, KEEP_PRE = 1000, 1000, 60
SOS = butter(2, [0.5, 150.0], btype='bandpass', fs=FS, output='sos')
NB, NA = iirnotch(50.0, 30.0, fs=FS)


def load(run):
    d = os.path.join(RUNS, run + '_ecg_cb', 'POSTPROC_DIR')
    X = np.stack([np.loadtxt(os.path.join(d, f'ECG_{l}.dat'))[:, 1] for l in LEADS])
    return np.hstack([np.repeat(X[:, :1], PAD_PRE, 1), X, np.repeat(X[:, -1:], PAD_POST, 1)]), X.shape[1]


def one(X, n, level_uv, seed):
    Y = X + (np.random.default_rng(seed).normal(0.0, level_uv * 1e-3, X.shape) if level_uv else 0.0)
    Y = filtfilt(NB, NA, sosfiltfilt(SOS, Y, axis=1), axis=1)
    Y = Y[:, PAD_PRE - KEEP_PRE: PAD_PRE + n]
    m = measure_beat(from_leads(dict(zip(LEADS, Y))), FS, baseline_window_ms=(KEEP_PRE - 45.0, KEEP_PRE - 5.0))
    on = m['onset_ms'] - KEEP_PRE
    return (on, m['qrs_duration_ms'], m['pseudo_delta_ms'], m['mdi_daniels'], m['mdi_daniels'] * m['qrs_duration_any_lead_ms'],
            m['qrs_duration_any_lead_ms'])


def site(args):
    h, run, sid = args
    X, n = load(run)
    out = []
    for lv in LEVELS_UV:
        R = np.array([one(X, n, lv, 1000 * k + 7) for k in range(1 if lv == 0 else NREAL)], dtype=float)
        med = np.nanmedian(R, axis=0)
        out.append({'heart': h, 'id': sid, 'noise_uv': lv, 'onset_ms': med[0], 'qrs_ms': med[1], 'pdw_ms': med[2],
                    'mdi': med[3], 't_largest_from_onset_ms': med[4], 'qrs_any_ms': med[5],
                    'onset_iqr_ms': float(np.subtract(*np.nanpercentile(R[:, 0], [75, 25]))) if len(R) > 1 else 0.0})
    return out


def items():
    out = []
    for h in HEARTS:
        df = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}_cb.csv'))
        out += [(h, r['run'], r['id']) for _, r in df.iterrows()]
    return out


def fam_masks(d):
    f, dp = d['family'], d['depth_target']
    return {'RVOT': f == 'rvot', 'aortic cusp': f == 'aortic_cusp', 'summit 90': (f == 'lv_summit') & (dp == 0.9),
            'vein 90': (f == 'lv_vein_course') & (dp == 0.9), 'LV endo 10': f.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1),
            'LV fw 10': (f == 'lv_free_wall') & (dp == 0.1), 'LV fw 90': (f == 'lv_free_wall') & (dp == 0.9)}


def summarise(S):
    meta = pd.concat([pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}_cb.csv'))[
        ['heart', 'id', 'family', 'position', 'level_z', 'depth_target']] for h in HEARTS])
    D = S.merge(meta, on=['heart', 'id'])
    rows, lines = [], []
    for h in HEARTS:
        for lv in LEVELS_UV:
            d = D[(D.heart == h) & (D.noise_uv == lv)]
            M = fam_masks(d)
            for fam, m in M.items():
                x = d[m]
                rows.append({'heart': h, 'noise_uv': lv, 'family': fam, 'n': len(x),
                             **{k: round(float(x[k].median()), 3 if k == 'mdi' else 1) for k in
                                ('onset_ms', 'qrs_ms', 'pdw_ms', 'mdi', 't_largest_from_onset_ms')}})
            md = {k: float(d[M[k]].mdi.median()) for k in ('RVOT', 'aortic cusp', 'summit 90', 'vein 90', 'LV endo 10')}
            fw = d[d.family == 'lv_free_wall']
            p = fw[fw.depth_target == 0.9].set_index(['position', 'level_z']).qrs_ms.to_frame('q90').join(
                fw[fw.depth_target == 0.1].set_index(['position', 'level_z']).qrs_ms.to_frame('q10'))
            order = min(md['summit 90'], md['vein 90'], md['aortic cusp']) > md['RVOT'] > md['LV endo 10']
            lines.append(f"{h} {lv:>2} uV: Daniels order {'PASS' if order else 'fail'} (summit {md['summit 90']:.3f}, vein {md['vein 90']:.3f}, "
                         f"cusp {md['aortic cusp']:.3f}, RVOT {md['RVOT']:.3f}, LV endo {md['LV endo 10']:.3f}); LV fw QRS 90/10 ratio medians "
                         f"{p.q90.median() / p.q10.median():.4f}, means {p.q90.mean() / p.q10.mean():.4f} (206/191 = 1.0785)")
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(HERE, 'summary.csv'), index=False)
    zheng = {'RVOT': ((0.36, 0.49), (26, 54), (133, 164)), 'aortic cusp': ((0.45, 0.60), (42, 74), (128, 148))}
    for fam, (mi, pd_, q) in zheng.items():
        for h in HEARTS:
            for lv in LEVELS_UV:
                r = T[(T.heart == h) & (T.noise_uv == lv) & (T.family == fam)].iloc[0]
                inn = lambda v, rg: 'in' if rg[0] <= v <= rg[1] else ('above' if v > rg[1] else 'below')
                lines.append(f'Zheng {fam} {h} {lv:>2} uV: MDI {r.mdi:.3f} {inn(r.mdi, mi)}, PdW {r.pdw_ms:.0f} {inn(r.pdw_ms, pd_)}, '
                             f'QRS {r.qrs_ms:.0f} {inn(r.qrs_ms, q)}')
    txt = T.to_string(index=False) + '\n\n' + '\n'.join(lines) + '\n'
    open(os.path.join(HERE, 'report.txt'), 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    if sys.argv[1] == 'time':
        it = items()[:2]
        t0 = time.time(); site(it[0]); site(it[1])
        per = (time.time() - t0) / 2
        print(f'{per:.1f} s per site (61 scorings); 432 sites ~{432 * per / 60:.1f} min on 1 process')
    else:
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        t0 = time.time()
        with Pool(nw) as p:
            res = p.map(site, items(), chunksize=4)
        S = pd.DataFrame([r for x in res for r in x])
        S.to_csv(os.path.join(HERE, 'sites.csv'), index=False)
        print(f'{len(S)} rows, {time.time() - t0:.0f} s')
        summarise(S)
