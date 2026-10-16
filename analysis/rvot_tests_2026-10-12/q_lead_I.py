#!/usr/bin/env python
"""
Lead I initial deflection at the basal superior LV sites, existing network-v3 beats only (12 Oct 2026, read only).

Sites per heart: bazan_region lv_basal_superior, families lv_free_wall / lv_vein_course / lv_summit (septum and cusps
left out, as in analysis/rvot_diag_2026-10-12), depth 10 % and 90 % (7 + 7).
Per site and conductor (study lead fields runs/<run>_ecg, cb runs/<run>_ecg_cb): lead I, baseline = value at the stimulus,
first 40 ms after the stimulus: the first wave beyond +/- 0.05 mV (the package's wave threshold; q_lead_I in
ecg_depth_criteria 0.3.0 = first such wave negative, true onset), its sign, peak amplitude and peak time; also the
largest negative and positive value in the 40 ms, and the package's true-onset q_lead_I call from the grid CSVs.

Output: q_lead_I_sites.csv, q_lead_I_summary.txt in this folder.
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RUNS = os.path.join(REPO, 'runs')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
FAM = ['lv_free_wall', 'lv_vein_course', 'lv_summit']
THR, WIN = 0.05, 40


def first_wave(y):
    lab = np.where(y >= THR, 1, np.where(y <= -THR, -1, 0))
    nz = np.nonzero(lab)[0]
    if not len(nz):
        return 0, np.nan, np.nan
    a, s = nz[0], lab[nz[0]]
    b = a
    while b < len(y) and lab[b] == s:
        b += 1
    p = a + int(np.argmax(y[a:b]) if s > 0 else np.argmin(y[a:b]))
    return int(s), round(float(y[p]), 3), int(p)


rows = []
for h in HEARTS:
    old = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}.csv')).set_index('id')
    cb = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}_cb.csv'))
    sel = cb[(cb.bazan_region == 'lv_basal_superior') & cb.family.isin(FAM) & cb.depth_target.isin([0.1, 0.9])]
    for _, r in sel.iterrows():
        row = {'heart': h, 'id': r['id'], 'name': r['name'], 'family': r['family'], 'depth': r['depth_target'],
               'uvc_z': round(r['z'], 2), 'phi_deg': round(r['phi_deg'], 0)}
        for tag, suf, call in (('study', '_ecg', old.loc[r['id'], 'true_q_lead_I']), ('cb', '_ecg_cb', r['true_q_lead_I'])):
            x = np.loadtxt(os.path.join(RUNS, r['run'] + suf, 'POSTPROC_DIR', 'ECG_I.dat'))[:, 1]
            y = x[:WIN + 1] - x[0]
            s, a, t = first_wave(y)
            row.update({f'{tag}_first_sign': {1: '+', -1: '-', 0: 'none'}[s], f'{tag}_first_mV': a, f'{tag}_first_ms': t,
                        f'{tag}_min40_mV': round(float(y.min()), 3), f'{tag}_max40_mV': round(float(y.max()), 3),
                        f'{tag}_q_lead_I_call': bool(call)})
        rows.append(row)
D = pd.DataFrame(rows)
D.to_csv(os.path.join(HERE, 'q_lead_I_sites.csv'), index=False)
out = []
for h in HEARTS:
    for d in (0.9, 0.1):
        t = D[(D.heart == h) & (D.depth == d)]
        f = lambda c, v: int((t[c] == v).sum())
        out.append(f'{h} d{int(d * 100)} n {len(t)}: first wave in 40 ms study -/+/none {f("study_first_sign", "-")}/{f("study_first_sign", "+")}/'
                   f'{f("study_first_sign", "none")}, cb {f("cb_first_sign", "-")}/{f("cb_first_sign", "+")}/{f("cb_first_sign", "none")}; '
                   f'q call study {int(t.study_q_lead_I_call.sum())}, cb {int(t.cb_q_lead_I_call.sum())}; '
                   f'median first amp study {t.study_first_mV.median():+.2f}, cb {t.cb_first_mV.median():+.2f} mV; '
                   f'median min40 study {t.study_min40_mV.median():+.3f}, cb {t.cb_min40_mV.median():+.3f}')
out.append('\nPositions (depth 90 % rows): ' + '; '.join(
    f'{r.heart[:2]} {r["name"]} z {r.uvc_z} phi {r.phi_deg:.0f}' for _, r in D[D.depth == 0.9].iterrows()))
open(os.path.join(HERE, 'q_lead_I_summary.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
print(D[['heart', 'id', 'depth', 'study_first_sign', 'study_first_mV', 'study_first_ms', 'cb_first_sign', 'cb_first_mV', 'cb_first_ms',
         'study_q_lead_I_call', 'cb_q_lead_I_call']].to_string(index=False))
