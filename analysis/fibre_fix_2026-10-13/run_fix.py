#!/usr/bin/env python
"""
Fibre-fix test, control heart Y5HYEDL4, 13 Oct 2026 (exploratory; frozen files untouched). After laplace_fix.py and
fibres_fix.py (this folder):
  frame   fibre angles at the RVOT and RV free-wall sites in the FIXED rule's own frame (as fibres_frame.py), with the
          Doste 2019 OT targets (endo 90 = along the outflow axis, epi 0 = circumferential)
  beats   myocardial graph rebuilt from the fixed fibres (same 0.6 / 0.4 / 0.48 m/s, same graph scale k 1.0685, fitted
          on the old fibres); network v3 as built; graph-only beats scored as analysis/junction_tests_2026-10-12
          (true onset; detected onset after 20 uV noise + 0.5-150 Hz + 50 Hz notch, 20 realisations); ECG with the
          existing cb weights (lead fields and ECG weights NOT rebuilt for the new fibres). Sites: RVOT 8, aortic cusp 8
          (the grid has no pulmonary-cusp sites), summit 8, vein course 12, LV endocardium 10 % (free wall + septum) 18,
          His beat. v3 comparison: analysis/junction_tests_2026-10-12/v3/beats.csv (same pipeline, frozen fibres).
Usage: python run_fix.py frame | beats | summary
"""

import importlib.util
import json
import os
import sys

os.environ['HEART'] = 'Y5HYEDL4'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


OUT = os.path.join(REPO, 'data', 'biv', 'Y5HYEDL4')
LAPF = os.path.join(HERE, 'laplace')


def lap(n):
    f = os.path.join(LAPF, n + '.dat')
    return np.loadtxt(f if os.path.exists(f) else os.path.join(OUT, 'laplace', n + '.dat'))


def frame():
    F = module('fib', os.path.join(B, '04_fibres.py'))
    pts = pd.read_csv(os.path.join(OUT, 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    E = pd.read_csv(os.path.join(OUT, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    rows = []
    for tag, lonf, ot_mode, epi in (('v3', os.path.join(OUT, 'bivF.lon'), 'ot', 'phi_epi'), ('fix', os.path.join(HERE, 'bivF.lon'), 'split', 'phi_epi_fix')):
        lon = pd.read_csv(lonf, sep=r'\s+', skiprows=1, header=None).to_numpy()
        L = {n: lap(n) for n in ('w', 'phi_lv', 'phi_rv', epi, 'basal', 'ot', 'ot_rv', 'ot_lv') if n in ('w', 'phi_lv', 'phi_rv', epi, 'basal', 'ot') or ot_mode == 'split'}
        rim = pts[np.loadtxt(os.path.join(OUT, 'surfaces', 'pv_rim.vtx'), skiprows=2, dtype=np.int64)]
        ax = np.linalg.svd(rim - rim.mean(0))[2][-1]
        for s in [x for x in json.load(open(os.path.join(OUT, 'sites.json'))) if x['family'] == 'rvot' or (x['family'] == 'rv_free_wall' and x['depth_target'] in (0.1, 0.5, 0.9))]:
            ids = np.where((E == int(s['node'])).any(1))[0]; Es = E[ids]
            em = lambda u: u[Es].mean(1)
            w = np.clip(em(L['w']), 0, 1); plv, prv, pepi = (np.clip(em(L[n]), 0, 1) for n in ('phi_lv', 'phi_rv', epi))
            d = prv / np.maximum(plv + prv, 1e-9)
            gb = F.unit(F.elem_grad(pts, Es, L['basal']))
            if ot_mode == 'split':
                go = np.where((d > 0.5)[:, None], F.unit(F.elem_grad(pts, Es, L['ot_rv'])), F.unit(F.elem_grad(pts, Es, L['ot_lv'])))
            else:
                go = F.unit(F.elem_grad(pts, Es, L['ot']))
            gpsi = w[:, None] * gb + (1 - w[:, None]) * go
            fr = F.axis(gpsi, F.elem_grad(pts, Es, L[epi]))
            f = F.unit(lon[ids, :3])
            al = np.degrees(np.arctan2(np.sum(f * fr[:, :, 1], 1), np.sum(f * fr[:, :, 0], 1)))
            al = (al + 90) % 180 - 90
            rows.append({'set': tag, 'id': s['id'], 'family': s['family'], 'depth': s['depth_target'], 'w': float(np.median(w)),
                         'phi_epi': float(np.median(pepi)), 'd': float(np.median(d)), 'alpha_deg': float(np.median(al)),
                         'out_of_plane_deg': float(np.median(np.degrees(np.arcsin(np.clip(np.abs(np.sum(f * fr[:, :, 2], 1)), 0, 1))))),
                         'e1_vs_pv_axis_deg': float(np.median(np.degrees(np.arccos(np.clip(np.abs(F.unit(gpsi) @ ax), 0, 1)))))})
    D = pd.DataFrame(rows).round(1)
    D.to_csv(os.path.join(HERE, 'frame.csv'), index=False)
    D['pos'] = D.id.str.replace(r'_z_d\d+$|_z\d\.\d+_d\d+$', '', regex=True)
    print(D.pivot_table(index=['family', 'pos', 'depth'], columns='set', values=['phi_epi', 'alpha_deg', 'e1_vs_pv_axis_deg', 'out_of_plane_deg']).round(1).to_string())


def beats():
    jt = module('jt', os.path.join(REPO, 'analysis', 'junction_tests_2026-10-12', 'junction_tests.py'))
    from scipy.sparse import coo_matrix
    PK = jt.PK
    E = pd.read_csv(os.path.join(OUT, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    lon = pd.read_csv(os.path.join(HERE, 'bivF.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    pts, N = jt.PTS, jt.N
    fb, sh = lon[:, :3], lon[:, 3:6]; nm = np.cross(fb, sh)
    keys, ws = [], []
    for a_, b_ in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):         # PK.myo_graph rule, new fibres
        dv = pts[E[:, b_]] - pts[E[:, a_]]
        t = np.sqrt((np.einsum('ij,ij->i', dv, fb) / 0.6) ** 2 + (np.einsum('ij,ij->i', dv, sh) / 0.4) ** 2 + (np.einsum('ij,ij->i', dv, nm) / 0.48) ** 2)
        lo, hi = np.minimum(E[:, a_], E[:, b_]), np.maximum(E[:, a_], E[:, b_])
        keys.append(lo * N + hi); ws.append(t)
    key, inv = np.unique(np.concatenate(keys), return_inverse=True)
    w = np.full(len(key), np.inf); np.minimum.at(w, inv.ravel(), np.concatenate(ws))
    e = np.c_[key // N, key % N]
    np.savez(os.path.join(HERE, 'myo_graph_fix.npz'), e=e.astype(np.int32), w=w.astype(np.float32))
    jt.E_, jt.W_ = e.astype(np.int64), w / PK.graph_scale()
    jt.MYO = coo_matrix((np.r_[jt.W_, jt.W_], (np.r_[jt.E_[:, 0], jt.E_[:, 1]], np.r_[jt.E_[:, 1], jt.E_[:, 0]])), shape=(N + 1, N + 1)).tocsr()
    cfg = jt.SETS['v3']; net = jt.network(cfg)
    S = [s for s in jt.sites() if s['family'] in ('rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course') or s['depth_target'] == 0.1]
    rows = [jt.beat(net, cfg, s) for s in S]
    his = jt.beat(net, cfg, None)
    T, _ = jt.solve(net, cfg, None)                                        # His ECG: detected QRS (noise-free) and axis
    t = np.arange(0, float(min(990, max(140, np.ceil((T.max() + 20) / 10) * 10))) + 0.5, 1.0)
    ecg = jt.CD.ecg_of(T, t, jt.WECG, jt.TM)
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, jt.LEADS.index(l)]), ecg[:, jt.LEADS.index(l)]]) for l in ('I', 'II', *jt.PRE)}
    his['qrs_detected'] = jt.measure_beat(jt.from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))['qrs_duration_ms']
    ang = np.radians([0, 60, 120, -150, -30, 90]); msk = (t >= T.min()) & (t <= T.max() + 3)
    A = np.c_[np.cos(ang), np.sin(ang)]
    for nmz, fn in (('net', lambda y: y[msk].max() + y[msk].min()), ('area', lambda y: y[msk].sum())):
        c = np.linalg.lstsq(A, np.array([fn(ecg[:, j] - ecg[0, j]) for j in range(6)]), rcond=None)[0]
        his[f'axis_{nmz}'] = int(round(float(np.degrees(np.arctan2(c[1], c[0])))))
    rows.append(his)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, 'beats_fix.csv'), index=False)
    print(f'{len(rows)} beats', flush=True)


def summary():
    out = []
    for name, f in (('v3', os.path.join(REPO, 'analysis', 'junction_tests_2026-10-12', 'v3', 'beats.csv')), ('fix', os.path.join(HERE, 'beats_fix.csv'))):
        b = pd.read_csv(f)
        h = b[b.family == 'his'].iloc[0]
        b = b[b.family != 'his'].copy(); b['depth_target'] = b.depth_target.astype(float)
        fam, dp = b.family, b.depth_target
        M = {'RVOT': fam == 'rvot', 'cusp': fam == 'aortic_cusp', 'summit90': (fam == 'lv_summit') & (dp == 0.9),
             'vein90': (fam == 'lv_vein_course') & (dp == 0.9), 'LVendo10': fam.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)}
        r = {'set': name}
        for mode, col in (('true', 'mdi'), ('det20', 'd_mdi')):
            md = {k: float(b[m][col].median()) for k, m in M.items()}
            r.update({f'{mode}_{k}': round(v, 3) for k, v in md.items()})
            r[f'{mode}_order_pass'] = bool(min(md['summit90'], md['vein90'], md['cusp']) > md['RVOT'] > md['LVendo10'])
        x = b[M['RVOT']]
        r.update({'RVOT_pdw_true': x.pdw.median(), 'RVOT_pdw_det20': x.d_pdw.median(), 'RVOT_tmax_true': x.tmax.median(),
                  'RVOT_tmax_det20_from_onset': x.d_tmax_from_onset.median(), 'RVOT_qrs_true': x.qrs.median(), 'RVOT_qrs_det20': x.d_qrs.median(),
                  'RVOT_t10': x.t10.median(), 'RVOT_t50': x.t50.median(),
                  'summit_cusp_qrs_true': b[fam.isin(['lv_summit', 'aortic_cusp'])].qrs.median()})
        r.update({'his_hv_ms': h['hv_ms'], 'his_qrs_true': h['qrs'], 'his_latest_after_lv_onset': h['latest_after_lv_onset'],
                  'his_lv30_pct': h['lv30'], 'his_lv37_pct': h['lv37'], 'his_rv_breakthrough': h['rv_breakthrough_after_lv_onset'],
                  'his_qrs_detected': h.get('qrs_detected', 96.0 if name == 'v3' else None),
                  'his_axis_net_area': f"{h.get('axis_net', 64)} / {h.get('axis_area', -46)}"})
        out.append(r)
    S = pd.DataFrame(out).set_index('set').T
    S.to_csv(os.path.join(HERE, 'summary.csv'))
    open(os.path.join(HERE, 'summary.txt'), 'w').write(S.to_string() + '\n')
    print(S.to_string())


if __name__ == '__main__':
    {'frame': frame, 'beats': beats, 'summary': summary}[sys.argv[1]]()
