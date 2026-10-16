#!/usr/bin/env python
"""
Extra measures for the RVOT variant tests (12 Oct 2026, coordinator brief after Alex's "go"), run after rvot_tests.py:
per set (v3 graph, V1-V4): His-driven beat (true and detected-onset QRS, latest activation after LV onset, % of LV
endocardium outside the posterobasal region active by 30 / 37.5 ms, first RV epicardial breakthrough, frontal axis) and,
at the 8 RVOT sites, the times when 10 % and 50 % of the ventricular volume are active and the time to the largest
precordial deflection (true window, as analysis/rvot_diag_2026-10-12). LV free-wall QRS 90 / 10 % as ratio of medians,
ratio of means and median per-pair % from <set>/beats.csv. Definitions as analysis/aim1_gates_2026-10-12/aim1_gates.py.
Re-solves only the His beat and the RVOT beats (graph-only, ~3 s each). Output: extras.csv, final.csv, final.txt.
"""

import importlib.util
import json
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rvot_tests', os.path.join(HERE, 'rvot_tests.py'))
rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
from ecg_depth_criteria import from_leads, measure_beat     # noqa: E402  (path set by rvot_tests)

OUT, PTS, Z, V = rt.OUT, rt.PTS, rt.Z, rt.V
PH = np.degrees(rt.PHI)
rd = lambda n: np.loadtxt(os.path.join(OUT, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
LV, EPI = rd('lv_endo'), rd('epi')
el = pd.read_csv(os.path.join(OUT, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
a, b, c, d = (PTS[el[:, k]] for k in range(4))
NVOL = np.bincount(el.ravel(), weights=np.repeat(np.abs(np.einsum('ij,ij->i', np.cross(b - a, c - a), d - a)) / 24, 4), minlength=len(PTS))
tri = np.loadtxt(os.path.join(OUT, 'surfaces', 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
ta = 0.5 * np.linalg.norm(np.cross(PTS[tri[:, 1]] - PTS[tri[:, 0]], PTS[tri[:, 2]] - PTS[tri[:, 0]]), axis=1)
NAREA = np.bincount(tri.ravel(), weights=np.repeat(ta / 3, 3), minlength=len(PTS))
PB = (Z >= 2 / 3) & (PH >= -150) & (PH <= -30)
LVK = LV[~PB[LV]]
RVE = EPI[V[EPI] == 1]
PRE = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def frac_time(T, f):
    o = np.argsort(T)
    return float(T[o][np.searchsorted(np.cumsum(NVOL[o]) / NVOL.sum(), f)])


def detected_qrs(ecg):
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, rt.LEADS.index(l)]), ecg[:, rt.LEADS.index(l)]]) for l in ('I', 'II', *PRE)}
    return measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))['qrs_duration_ms']


rows = []
for s in ('v3', 'V1', 'V2', 'V3', 'V4'):
    net = rt.network(s)
    r = {'set': s}
    if s != 'V1':                                  # V1 uses the v3 network: His beat identical to v3
        T, _ = rt.solve(net, None)
        t, ecg = rt.ecg_of(T)
        t0 = float(T[LV].min())
        r.update({'his_qrs_true': round(float(T.max() - T.min()), 1), 'his_qrs_detected': detected_qrs(ecg),
                  'his_latest_after_lv_onset': round(float(T.max() - t0), 1),
                  'lv_endo_30ms_pct': round(100 * float(NAREA[LVK][T[LVK] <= t0 + 30].sum() / NAREA[LVK].sum()), 1),
                  'lv_endo_37.5ms_pct': round(100 * float(NAREA[LVK][T[LVK] <= t0 + 37.5].sum() / NAREA[LVK].sum()), 1),
                  'rv_epi_breakthrough_ms': round(float(T[RVE].min() - t0), 1)})
        r['axis_net'], r['axis_area'] = rt.axis(t, ecg, T.min(), T.max() + 3)
    S = rt.moved_rvot() if s == 'V1' else [x for x in rt.sites() if x['family'] == 'rvot']
    t10, t50, tmax = [], [], []
    for x in S:
        T, _ = rt.solve(net, int(x['node']))
        t, ecg = rt.ecg_of(T)
        n = int(round(T.max()))
        tm = min(int(np.argmax(np.abs(ecg[:n + 1, rt.LEADS.index(k)] - ecg[0, rt.LEADS.index(k)]))) for k in PRE)
        t10.append(frac_time(T, 0.10)); t50.append(frac_time(T, 0.50)); tmax.append(tm)
    r.update({'rvot_t10_ms': round(float(np.median(t10)), 1), 'rvot_t50_ms': round(float(np.median(t50)), 1),
              'rvot_tmax_ms': float(np.median(tmax))})
    f = os.path.join(HERE, s, 'beats.csv')
    if os.path.exists(f):                          # LV free wall 90 / 10 % from the variant's own beats
        bt = pd.read_csv(f)
        fw = bt[bt.family == 'lv_free_wall'].copy()
        fw['pos'] = fw['id'].map(lambda i: re.sub(r'_d\d+$', '', i))
        p = fw[fw.depth_target == 0.9].set_index('pos').qrs_ms.to_frame('q90').join(fw[fw.depth_target == 0.1].set_index('pos').qrs_ms.to_frame('q10'))
        r.update({'fw_ratio_medians': round(float(p.q90.median() / p.q10.median()), 4), 'fw_ratio_means': round(float(p.q90.mean() / p.q10.mean()), 4),
                  'fw_pair_median_pct': round(float((100 * (p.q90 - p.q10) / p.q10).median()), 1)})
    rows.append(r)
    print(r, flush=True)
X = pd.DataFrame(rows)
X.to_csv(os.path.join(HERE, 'extras.csv'), index=False)
S = pd.read_csv(os.path.join(HERE, 'summary.csv'))
S['set'] = S['set'].str.replace(' graph', '', regex=False)
F = S.merge(X, on='set', how='outer')
F.to_csv(os.path.join(HERE, 'final.csv'), index=False)
open(os.path.join(HERE, 'final.txt'), 'w').write(F.T.to_string() + '\n')
print(F.T.to_string())
