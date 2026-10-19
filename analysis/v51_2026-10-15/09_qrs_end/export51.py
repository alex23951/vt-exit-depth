"""Export for the QRS-end hand reading (19 Oct 2026, read-only; brief PC-EXPORT-BRIEF from the cloud thread "QRS end
measurement problem", Alex tapped "Calibrate" 19 Oct 2026 07:06:54 UTC). No simulation; no v5.1 file is changed.

Beats (v5.1 network beats, runs/v51_2026-10-15/06_pilot_rerun/maps): the control heart's (Y5HYEDL4) 16 LV summit and
aortic-cusp beats behind gate 1, plus its 10 LV free-wall 10 % / 90 % pairs (20 beats) = 36; filled to 40 with 4 other
paced network beats (any heart, His beats excluded, only beats that have all three Step 6 scorings used in the key) drawn
with numpy default_rng(0) from the sorted pool; the 40 are then
shuffled with a fresh default_rng(0) and named M01 ... M40.
ECG: recomputed from the beat's activation map with the same weights and template as Step 6 (data/biv/<H>/ecgW_v51.npz,
15_conductor.py Template / ecg_of; chunked, checked against the stored Step 6 ECG), from -100 to 450 ms (1 ms sampling,
stimulus at 0). The model has no T wave: its template runs from 60 ms before to 80 ms after each node's activation and is
then held, so the trace is flat from about 80 ms after the last activation. Clean (no noise added). Before the stimulus the trace repeats
its value at 0 ms, as the Step 6 scoring padded it (the template's pre-activation foot would otherwise put a slow drift
before the stimulus); that value is subtracted per lead, so every lead starts at 0 mV.
Key (kept on the PC, not posted): analysis/v51_2026-10-15/09_qrs_end/key_model_beats_40.csv: Step 6 0.4.0 values from
06_pilot_rerun/rescore/per_site.csv (detected onset, primary 10 uV noise = median of seeds 0-9, and clean), offsets (any
lead; precordial = onset + qrs_duration_ms), QRS durations, true activation end (latest node) and true QRS (true mode),
plus the 0.4.0 detected values on the exported trace itself. All in ms from the stimulus.
Outputs: runs/v51_2026-10-15/09_qrs_end/export/M01.csv ... M40.csv and runs/v51_2026-10-15/09_qrs_end/qrs_end_model_beats_40.zip.
Usage (repo root, venv): python -B analysis/v51_2026-10-15/09_qrs_end/export51.py
"""
import json
import os
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import conductor51 as C51                                             # noqa: E402
from ecg_depth_criteria import from_leads, measure_beat               # noqa: E402

MAPS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps')
OUT = os.path.join(REPO, 'runs', 'v51_2026-10-15', '09_qrs_end')
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
PRE, POST = 100, 450
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SCORED = [('detected', 'plan10'), ('detected', 'clean'), ('true', 'clean')]   # Step 6 scorings in the key


def ecg_chunked(T, t, W, tm, step=20000):
    """15_conductor.py ecg_of with smaller chunks (memory: a monodomain run shares the PC)."""
    ecg = np.zeros((len(t), W.shape[0]))
    for i0 in range(0, len(T), step):
        sl = slice(i0, i0 + step)
        rel = t[:, None] - T[None, sl]
        ecg += np.interp(rel.ravel(), tm.t, tm.v, left=tm.v[0], right=tm.v[-1]).reshape(rel.shape) @ W[:, sl].T
    return ecg


def pick():
    ps = pd.read_csv(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '06_pilot_rerun', 'rescore', 'per_site.csv'))
    y = ps[(ps.heart == 'Y5HYEDL4') & (ps.network == 'net')]
    target = sorted(y[y.family.isin(['lv_summit', 'aortic_cusp'])].site.unique())
    fw = sorted(y[(y.family == 'lv_free_wall') & y.depth.isin([0.1, 0.9])].site.unique())
    pairs = sorted({s.rsplit('_d', 1)[0] for s in fw})
    assert all(f'{p}_d10' in fw and f'{p}_d90' in fw for p in pairs) and len(target) + 2 * len(pairs) <= 40
    chosen = [('Y5HYEDL4', s, 'target') for s in target] + [('Y5HYEDL4', f'{p}_d{d}', 'contrast') for p in pairs for d in (10, 90)]
    net = ps[ps.network == 'net']
    have = [set(map(tuple, net[(net['mode'] == m) & (net.noise == n)][['heart', 'site']].values)) for m, n in SCORED]
    pool = sorted((h, s) for h, s in set.intersection(*have)
                  if s != 'his_driven' and (h, s) not in {(a, b) for a, b, _ in chosen})
    rng = np.random.default_rng(0)
    fill = [pool[i] for i in rng.choice(len(pool), 40 - len(chosen), replace=False)]
    chosen += [(h, s, 'fill') for h, s in fill]
    order = np.random.default_rng(0).permutation(len(chosen))
    return ps, [chosen[i] for i in order]


def rule(ecg):
    leads = {l: ecg[:, L12.index(l)] for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    m = measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(PRE - 45.0, PRE - 5.0))
    return {'export_detected_clean_onset_ms': m['onset_ms'] - PRE, 'export_detected_clean_offset_any_lead_ms': m['offset_any_lead_ms'] - PRE,
            'export_detected_clean_qrs_any_lead_ms': m['qrs_duration_any_lead_ms'], 'export_detected_clean_qrs_precordial_ms': m['qrs_duration_ms']}


def main():
    ps, beats = pick()
    os.makedirs(os.path.join(OUT, 'export'), exist_ok=True)
    sites = {h: {s['id']: s for s in json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))} for h in HEARTS}
    agg = ps[ps.network == 'net'].groupby(['heart', 'site', 'mode', 'noise'])[['onset_ms', 'offset_any_lead_ms', 'qrs_duration_any_lead_ms', 'qrs_duration_ms']].median()
    t = np.arange(-PRE, POST + 1, dtype=float)
    rows, cache = [], {}
    for k, (h, s, role) in enumerate(beats):
        name = f'M{k + 1:02d}'
        if h not in cache:
            cache.clear()
            sys.modules.pop('common', None)                            # 15_conductor.py takes HEART from sims/biv_model/common.py
            CD = C51.biv_module('cd', '15_conductor.py', h)
            assert CD.HEART == h, (CD.HEART, h)
            cache[h] = (np.load(os.path.join(REPO, 'data', 'biv', h, 'ecgW_v51.npz'))['W'].astype(float), CD.Template())
        W, tm = cache[h]
        T = np.load(os.path.join(MAPS, h, s + '.T.npy')).astype(float)
        post = ecg_chunked(T, t[PRE:], W, tm)
        stored = np.load(os.path.join(MAPS, h, s + '.ecg.npy')).astype(float)
        dev = float(np.abs(post[:len(stored)] - stored).max())
        assert dev < 1e-3, (h, s, dev)
        base = post[0].copy()
        ecg = np.vstack([np.tile(base, (PRE, 1)), post]) - base          # Step 6 convention: the trace before 0 repeats t = 0
        pd.DataFrame(np.c_[t, ecg], columns=['time_ms'] + L12).to_csv(os.path.join(OUT, 'export', name + '.csv'), index=False, float_format='%.5f')
        si = sites[h].get(s, {})
        r = {'name': name, 'heart': h, 'site': s, 'role': role, 'family': si.get('family'), 'depth_target': si.get('depth_target'),
             'true_activation_end_ms': round(float(T.max()), 2), 'max_dev_vs_stored_step6_ecg_mV': dev, 'level_at_0ms_removed_mV_max_abs': float(np.abs(base).max())}
        for mode, noise, tag in (('detected', 'plan10', 'step6_detected_noise10'), ('detected', 'clean', 'step6_detected_clean'), ('true', 'clean', 'step6_true')):
            a = agg.loc[(h, s, mode, noise)]
            r[f'{tag}_onset_ms'] = a.onset_ms
            r[f'{tag}_offset_any_lead_ms'] = a.offset_any_lead_ms
            r[f'{tag}_offset_precordial_ms'] = a.onset_ms + a.qrs_duration_ms
            r[f'{tag}_qrs_any_lead_ms'] = a.qrs_duration_any_lead_ms
            r[f'{tag}_qrs_precordial_ms'] = a.qrs_duration_ms
        r |= rule(ecg)
        rows.append(r)
        print(name, h, s, role, 'dev', f'{dev:.1e}', 'true end', r['true_activation_end_ms'], 'step6 QRS', r['step6_detected_noise10_qrs_any_lead_ms'], flush=True)
    key = pd.DataFrame(rows)
    key.to_csv(os.path.join(HERE, 'key_model_beats_40.csv'), index=False)
    zf = os.path.join(OUT, 'qrs_end_model_beats_40.zip')
    with zipfile.ZipFile(zf, 'w', zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            z.write(os.path.join(OUT, 'export', r['name'] + '.csv'), r['name'] + '.csv')
    print('roles', key.role.value_counts().to_dict(), 'zip', zf, os.path.getsize(zf))


if __name__ == '__main__':
    main()
