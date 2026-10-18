"""Step 6 item 4 reports (v5.1 brief; reported only, never used to retune), on the v5.1 pilot beats:
A9   Doste's 10-ms isochrone on the RV endocardium around the earliest RV endocardial node, RVOT septal and free-wall sites,
     network and tissue-only beats (the HF hearts get extra tissue-only RVOT beats here, saved in maps/<H>_nonet_rvot/).
     Operational rule (mine, inference): isochrone = RV endocardial nodes activated within 10 ms of the earliest RV
     endocardial node, connected to it on the RV endocardial surface; long axis = the RVOT axis (RV endocardial apex node,
     lowest UVC z, -> pulmonary-ring centroid) projected onto the tangent plane at the earliest node; short axis
     perpendicular in that plane; ratio = extent along / extent across; area = sum of nodal surface areas.
     Comparators: Doste 2019 1.86 +- 0.22; Acosta 2015 (clinical) 1.9 +- 1.2; expected lower (inference).
LBBB 6G8DD8S5 His beat against Strauss 2011 and the AHA/ACCF/HRS 2009 LBBB items (the other hearts beside it), from the
     His-beat ECG (clean, detected onset, 0.4.0). Operational rules (mine): QS or rS in V1 / V2 = S deeper than R and
     R <= 0.25 S; notch = a dip of >= 0.05 mV between two peaks of the same sign inside the QRS; R-peak time = QRS onset to
     the largest positive peak; q from the 0.4.0 primary initial polarity. Slurring is not scored.
HIS  His-beat QRS (spontaneous convention: detected onset, 10 uV noise, median of seeds 0-9, any lead; from
     rescore/per_site.csv) beside cohort male controls 90.3 +- 8 ms, Mason 2007 69-109 ms, Rijnbeek 2014 men 20-29 y
     80-126 ms.
Usage (repo root, venv, after grid51.py and rescore51.py): python -B analysis/v51_2026-10-15/06_pilot_rerun/reports51.py
Writes reports51.json in this folder.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
MAPS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def rd(h, n):
    return np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'surfaces', f'{n}.vtx'), skiprows=2, dtype=np.int64)


def a9(h):
    B = os.path.join(REPO, 'data', 'biv', h)
    P = np.loadtxt(os.path.join(B, 'biv.pts'), skiprows=1) / 1e3
    tri = np.loadtxt(os.path.join(B, 'surfaces', 'rv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    rv, pv = rd(h, 'rv_endo'), rd(h, 'pv_rim')
    z = np.loadtxt(os.path.join(B, 'uvc', 'z.dat'))
    ta = np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]])
    area = np.bincount(tri.ravel(), weights=np.repeat(0.5 * np.linalg.norm(ta, axis=1) / 3, 3), minlength=len(P))
    nrm = np.zeros((len(P), 3))
    for k in range(3):
        np.add.at(nrm, tri[:, k], ta)
    e = np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]])
    apex_rv = int(rv[np.argmin(z[rv])])
    axis = P[pv].mean(0) - P[apex_rv]
    S = json.load(open(os.path.join(B, 'sites.json')))
    rvot = [s for s in S if s['family'] == 'rvot']
    out = {}
    # tissue-only RVOT beats: Y5HYEDL4 from the no-network arm, HF hearts computed here
    nonet_dir = os.path.join(MAPS, h + '_nonet') if h == 'Y5HYEDL4' else os.path.join(MAPS, h + '_nonet_rvot')
    if h != 'Y5HYEDL4':
        os.makedirs(nonet_dir, exist_ok=True)
        need = [s for s in rvot if not os.path.exists(os.path.join(nonet_dir, s['id'] + '.T.npy'))]
        if need:
            import heart51 as H51
            os.environ['HEART'] = h
            H = H51.Heart51(h)
            for s in need:
                T = H.solve(int(s['node']), nonet=True)
                assert np.isfinite(T).all()
                np.save(os.path.join(nonet_dir, s['id'] + '.T.npy'), T.astype(np.float32))
    for arm, d in (('network', os.path.join(MAPS, h)), ('tissue_only', nonet_dir)):
        for s in rvot:
            T = np.load(os.path.join(d, s['id'] + '.T.npy')).astype(float)
            n0 = int(rv[np.argmin(T[rv])])
            t0 = T[n0]
            inside = np.zeros(len(P), bool); inside[rv[T[rv] <= t0 + 10.0]] = True
            ee = e[inside[e[:, 0]] & inside[e[:, 1]]]
            A = coo_matrix((np.ones(len(ee)), (ee[:, 0], ee[:, 1])), shape=(len(P), len(P)))
            _, lab = connected_components(A, directed=False)
            iso = np.where(inside & (lab == lab[n0]))[0]
            nn = nrm[n0] / np.linalg.norm(nrm[n0])
            lo = axis - (axis @ nn) * nn; lo /= np.linalg.norm(lo); sh = np.cross(nn, lo)
            u, v = (P[iso] - P[n0]) @ lo, (P[iso] - P[n0]) @ sh
            L, W = float(np.ptp(u)), float(np.ptp(v))
            out[f'{arm} {s["id"]}'] = {'earliest_rv_endo_ms': round(float(t0), 1), 'nodes': int(len(iso)), 'length_mm': round(L, 1), 'width_mm': round(W, 1),
                                       'ratio': round(L / W, 2) if W > 0 else None, 'area_mm2': round(float(area[iso].sum()), 1)}
    return out


def notches(y, sign):
    """Dips of >= 0.05 mV between two peaks of the same sign (sign +1: R peaks, -1: S troughs)."""
    x = sign * y
    pk = [i for i in range(1, len(x) - 1) if x[i] >= x[i - 1] and x[i] > x[i + 1] and x[i] > 0.05]
    n = 0
    for a, b in zip(pk[:-1], pk[1:]):
        if min(x[a], x[b]) - x[a:b + 1].min() >= 0.05:
            n += 1
    return n


def lbbb(h):
    from ecg_depth_criteria import from_leads, measure_beat
    ecg = np.load(os.path.join(MAPS, h, 'his_driven.ecg.npy')).astype(float)
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, L12.index(l)]), ecg[:, L12.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    X = from_leads(leads)
    m = measure_beat(X, 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))
    on, off = int(round(m['onset_ms'])), int(round(m['offset_any_lead_ms']))
    res = {'qrs_detected_any_lead_ms_clean': m['qrs_duration_any_lead_ms']}
    seg = {l: X[L12.index(l)][on:off + 1] - X[L12.index(l)][max(on - 5, 0)] for l in L12}
    for l in ('V1', 'V2'):
        R, Sd = float(max(seg[l].max(), 0)), float(max(-seg[l].min(), 0))
        res[f'{l}_R_S_mV'] = [round(R, 3), round(Sd, 3)]
        res[f'{l}_QS_or_rS'] = bool(Sd > R and R <= 0.25 * Sd)
    nn = {l: notches(seg[l], 1 if seg[l].max() >= -seg[l].min() else -1) for l in ('V1', 'V2', 'V5', 'V6', 'I', 'aVL')}
    res['notches_per_lead'] = nn
    res['strauss_notching_in_ge2_leads'] = bool(sum(v > 0 for v in nn.values()) >= 2)
    res['strauss_qrs_ge_140_men'] = bool(m['qrs_duration_any_lead_ms'] >= 140)
    res['strauss_qrs_ge_130_women'] = bool(m['qrs_duration_any_lead_ms'] >= 130)
    pol = m['initial_polarity']
    res['aha_no_q_in_I_V5_V6'] = bool(all(pol[l] >= 0 for l in ('I', 'V5', 'V6')))
    res['aha_R_peak_time_V5_V6_ms'] = [int(np.argmax(seg[l])) for l in ('V5', 'V6')]
    res['aha_R_peak_time_gt_60'] = bool(all(int(np.argmax(seg[l])) > 60 for l in ('V5', 'V6')))
    res['aha_qrs_ge_120'] = bool(m['qrs_duration_any_lead_ms'] >= 120)
    res['aha_notched_R_I_aVL_V5_V6'] = {l: nn.get(l, notches(seg[l], 1)) for l in ('I', 'aVL', 'V5', 'V6')}
    return res


def main():
    out = {'A9': {}, 'LBBB': {}, 'HIS_QRS': {}}
    ps = pd.read_csv(os.path.join(HERE, 'rescore', 'per_site.csv'))
    for h in HEARTS:
        out['A9'][h] = a9(h)
        out['LBBB'][h] = lbbb(h)
        x = ps[(ps.heart == h) & (ps.site == 'his_driven') & (ps['mode'] == 'detected') & (ps.noise == 'plan10')]
        out['HIS_QRS'][h] = {'spontaneous_primary_ms': float(x.qrs_duration_any_lead_ms.median()) if len(x) else None,
                             'comparators': 'cohort male controls 90.3 +- 8; Mason 2007 69-109; Rijnbeek 2014 men 20-29 y 80-126'}
        print(h, json.dumps({k: out[k][h] for k in out}, default=str)[:3000], flush=True)
    json.dump(out, open(os.path.join(HERE, 'reports51.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
