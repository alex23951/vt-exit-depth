"""Step 4.5 C9 report (not gated): the acceptance C activation maps, openCARP and the adopted nodal graph solver, through the
v5.1 lead fields (data/biv/<H>/ecgW_v51.npz, sigma_i source) and the v5 action-potential template (Tomek, 15_conductor.py
Template), scored side by side with ecg_depth_criteria 0.4.0 in the pace-map convention (stimulus onset, clean ECG,
default baseline; QRS = qrs_duration_any_lead_ms) and in true mode (onset 0, offset = last activation).
Tissue only, single-node stimulus, as acceptance C. ECGs saved in runs/v51_2026-10-15/04_build/<H>/ecg_side/.
Usage (repo root, venv): HEART=<H> python -B analysis/v51_2026-10-15/04_build/ecg_side.py
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import acceptance_c as AC                                              # noqa: E402
import conductor51 as C51                                              # noqa: E402
import graph51 as g                                                    # noqa: E402
import solver51 as S                                                   # noqa: E402
from ecg_depth_criteria import from_leads, measure_beat               # noqa: E402
import ecg_depth_criteria as edc                                       # noqa: E402

KEYS = ['qrs_duration_any_lead_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels', 'q_lead_I', 'inferior_q_any']
PAD = 60


def score(ecg, last):
    L = C51.LEADS
    leads = {l: np.concatenate([np.full(PAD, ecg[0, L.index(l)]), ecg[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    X = from_leads(leads)
    out = {}
    for mode, kw in (('pace', dict(stim_ms=float(PAD))), ('true', dict(onset_ms=float(PAD), offset_ms=float(last + PAD)))):
        m = measure_beat(X, 1000.0, **kw)
        out[mode] = {k: (float(m[k]) if isinstance(m.get(k), (int, float, np.floating, np.integer, bool, np.bool_)) else m.get(k)) for k in KEYS}
    return out


def main():
    h = os.environ['HEART']
    CD = C51.biv_module('cd', '15_conductor.py', h)
    TM = CD.Template()
    W = np.load(os.path.join(REPO, 'data', 'biv', h, 'ecgW_v51.npz'))['W'].astype(float)
    lonf = S.lon51(h)
    G = g.Tissue(h, lonf).graph(S.SPEEDS[h], S.load_factors(h, lonf))
    sites = {s['id']: s for s in S.sites(h)}
    status = json.load(open(os.path.join(AC.rundir(h), 'status.json')))
    od = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'ecg_side'); os.makedirs(od, exist_ok=True)
    rows = []
    for sid in AC.SITES:
        st = status.get(sid, {})
        if not st.get('outcome', '').startswith('ok'):
            rows.append({'heart': h, 'site': sid, 'solver': 'openCARP', 'note': st.get('outcome', 'not run')})
            continue
        To = AC.igb_last(os.path.join(AC.rundir(h, sid), st.get('act_dir', ''), 'act.igb'))
        Tg = g.Tissue.solve(G, int(sites[sid]['node']))
        for lab, T in (('openCARP', To), ('graph_nodal', Tg)):
            tend = float(min(990, max(140, np.ceil((T.max() + 20) / 10) * 10)))
            t = np.arange(0, tend + 0.5, 1.0)
            ecg = CD.ecg_of(T, t, W, TM)
            np.save(os.path.join(od, f'{sid}.{lab}.ecg.npy'), ecg.astype(np.float32))
            sc = score(ecg, float(T.max()))
            r = {'heart': h, 'site': sid, 'solver': lab, 'total_activation_ms': round(float(T.max()), 2),
                 'peak_abs_mV': round(float(np.abs(ecg).max()), 3)}
            for mode, d in sc.items():
                r.update({f'{mode}_{k}': v for k, v in d.items()})
            rows.append(r)
        print(h, sid, {k: (rows[-2].get(k), rows[-1].get(k)) for k in ('pace_qrs_duration_any_lead_ms', 'pace_pseudo_delta_ms', 'pace_idt_v2_ms', 'pace_srs_ms', 'pace_mdi_daniels')}, flush=True)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    f = os.path.join(HERE, f'ecg_side_{h}.csv')
    with open(f, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print('wrote', f, 'package', edc.__version__)


if __name__ == '__main__':
    main()
