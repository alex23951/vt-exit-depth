#!/usr/bin/env python
"""
Junction / refractoriness sensitivity tests on the control heart Y5HYEDL4, 12 Oct 2026 (coordinator brief after Alex,
21:42 UTC). EXPLORATORY: frozen network, site and calibration files are only read; results go to this folder.

Graph-only beats as analysis/rvot_tests_2026-10-12 (combined myocardium + network shortest path of 14_purkinje.py,
graph scale k, pseudo-Vm template, cb ECG weights), on the frozen v3 network. Checked first: the combined graph already
has direction-dependent junction delays (muscle -> network d_ret, network -> muscle d_ant: v3 2 / 4 ms); network links
are undirected; v3 is not a tree (312 independent loops from 553 LV + 353 RV distal reconnections).

Sets:
  v3   frozen: junction 4 ms antegrade / 2 ms retrograde, proximal speeds as built (2.0-3.36 m/s)
  J1   junction 5 ms antegrade / 3 ms retrograde (Choi 2023, Joyner 1985; Behradfar 2014, Jabbour 2025);
       every proximal link (His, bundles, fascicles) 1.7 m/s (Serban 2025); distal 2.0 m/s unchanged
  J2   J1 + no retrograde entry at junctions within 3 mm of the stimulus node (Bayer 2026)
  J3a / J3b  J2 + network refractory for ectopic beats until 28 / 56 ms after the stimulus (Bayer 2025: Purkinje AP
       ~56 ms longer than myocardial): an arrival before that is blocked, not delayed. Because times increase along any
       path, this equals removing the retrograde entry of every junction whose myocardium-only activation + d_ret is
       earlier than the limit (the muscle there fires once); later entries elsewhere stay possible. His beat unaffected.
Scoring: true onset (stimulus, last activation) and detected onset after 20 uV white noise (20 seeded realisations,
median) + 0.5-150 Hz zero-phase band-pass + 50 Hz notch, as analysis/noise_onset_2026-10-12.

Usage: python junction_tests.py time | run <set> | summary          Output: <set>/beats.csv, summary.csv, summary.txt
"""

import csv
import importlib.util
import json
import os
import re
import sys
import time

os.environ['HEART'] = 'Y5HYEDL4'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))

import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402
from scipy.sparse import coo_matrix                                 # noqa: E402
from scipy.sparse.csgraph import dijkstra                           # noqa: E402
from ecg_depth_criteria import from_leads, measure_beat             # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


PK = module('pk', os.path.join(B, '14_purkinje.py'))                 # read only (PK folder = frozen network)
CD = module('cd', os.path.join(B, '15_conductor.py'))
NO = module('no', os.path.join(REPO, 'analysis', 'noise_onset_2026-10-12', 'noise_onset.py'))
OUT = os.path.join(REPO, 'data', 'biv', 'Y5HYEDL4')
PTS, Z, PHI, V = PK.load()
PH = np.degrees(PHI)
PTS_UM = PTS * 1e3
E_, W_ = PK.myo_graph(PTS)
W_ = W_ / PK.graph_scale()
N = len(PTS)
MYO = coo_matrix((np.r_[W_, W_], (np.r_[E_[:, 0], E_[:, 1]], np.r_[E_[:, 1], E_[:, 0]])), shape=(N + 1, N + 1)).tocsr()
NET0 = dict(np.load(os.path.join(OUT, 'purkinje', 'network.npz')))
WECG = np.load(os.path.join(OUT, 'ecgW_nofast_cb.npz'))['W'].astype(float)
TM = CD.Template()
LEADS = CD.LEADS
PRE = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SETS = {'v3': dict(d_ant=4.0, d_ret=2.0, prox=None, near_mm=0.0, refr=0.0),
        'J1': dict(d_ant=5.0, d_ret=3.0, prox=1.7, near_mm=0.0, refr=0.0),
        'J2': dict(d_ant=5.0, d_ret=3.0, prox=1.7, near_mm=3.0, refr=0.0),
        'J3a': dict(d_ant=5.0, d_ret=3.0, prox=1.7, near_mm=3.0, refr=28.0),
        'J3b': dict(d_ant=5.0, d_ret=3.0, prox=1.7, near_mm=3.0, refr=56.0)}
rd = lambda n: np.loadtxt(os.path.join(OUT, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
LV, EPI = rd('lv_endo'), rd('epi')
el = pd.read_csv(os.path.join(OUT, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
a_, b_, c_, d_ = (PTS[el[:, k]] for k in range(4))
NVOL = np.bincount(el.ravel(), weights=np.repeat(np.abs(np.einsum('ij,ij->i', np.cross(b_ - a_, c_ - a_), d_ - a_)) / 24, 4), minlength=N)
tri = np.loadtxt(os.path.join(OUT, 'surfaces', 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
ta = 0.5 * np.linalg.norm(np.cross(PTS[tri[:, 1]] - PTS[tri[:, 0]], PTS[tri[:, 2]] - PTS[tri[:, 0]]), axis=1)
NAREA = np.bincount(tri.ravel(), weights=np.repeat(ta / 3, 3), minlength=N)
LVK = LV[~((Z >= 2 / 3) & (PH >= -150) & (PH <= -30))[LV]]
RVE = EPI[V[EPI] == 1]


def network(cfg):
    net = dict(NET0)
    if cfg['prox']:
        k = net['kind']
        pe = (k[net['edges'][:, 0]] == 'proximal') & (k[net['edges'][:, 1]] == 'proximal')
        sp = net['edge_speed'].copy(); sp[pe] = cfg['prox']
        net['edge_speed'] = sp
    return net


def solve(net, cfg, site_node=None):
    M = len(net['nodes'])
    gn = PK.net_graph(net, PTS).tocoo()
    k = (gn.row < M) & (gn.col < M)
    m = net['nodes'][net['pmj']]
    j = N + net['pmj']
    src = N + M
    ret_ok = np.ones(len(m), bool)
    srcs = None
    if site_node is not None:
        srcs = np.where(np.linalg.norm(PTS_UM - PTS_UM[site_node], axis=1) < 1500)[0]
        if cfg['near_mm']:
            ret_ok &= np.linalg.norm(PTS[m] - PTS[site_node], axis=1) > cfg['near_mm']
        if cfg['refr']:                                    # myocardium-only field decides which entries are blocked
            g = MYO.tocoo()
            G0 = coo_matrix((np.r_[g.data, np.full(len(srcs), 1e-6)], (np.r_[g.row, np.full(len(srcs), N)], np.r_[g.col, srcs])),
                            shape=(N + 1, N + 1)).tocsr()
            Tm = dijkstra(G0, directed=True, indices=N)[:N] - 1e-6
            ret_ok &= Tm[m] + cfg['d_ret'] >= cfg['refr']
    rows = [E_[:, 0], E_[:, 1], N + gn.row[k], m[ret_ok], j]
    cols = [E_[:, 1], E_[:, 0], N + gn.col[k], j[ret_ok], m]
    data = [W_, W_, gn.data[k], np.full(int(ret_ok.sum()), cfg['d_ret']), np.full(len(m), cfg['d_ant'])]
    if site_node is None:
        rows.append(np.array([src])); cols.append(np.array([N + int(net['his'])])); data.append(np.array([1e-6]))
    else:
        rows.append(np.full(len(srcs), src)); cols.append(srcs); data.append(np.full(len(srcs), 1e-6))
    G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
    d = dijkstra(G, directed=True, indices=src) - 1e-6
    return d[:N], int((~ret_ok).sum())


def frac_time(T, f):
    o = np.argsort(T)
    return float(T[o][np.searchsorted(np.cumsum(NVOL[o]) / NVOL.sum(), f)])


def true_scores(t, ecg, last):
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, LEADS.index(l)]), ecg[:, LEADS.index(l)]]) for l in ('I', 'II', *PRE)}
    m = measure_beat(from_leads(leads), 1000.0, onset_ms=pad, offset_ms=last + pad, baseline_window_ms=(pad - 45.0, pad - 5.0))
    n = int(round(last))
    tmax = min(int(np.argmax(np.abs(ecg[:n + 1, LEADS.index(k)] - ecg[0, LEADS.index(k)]))) for k in PRE)
    return {'qrs': m['qrs_duration_ms'], 'mdi': m['mdi_daniels'], 'pdw': m['pseudo_delta_ms'], 'tmax': tmax}


def detected_scores(ecg):
    X = np.stack([ecg[:, LEADS.index(l)] for l in NO.LEADS])
    X = np.hstack([np.repeat(X[:, :1], NO.PAD_PRE, 1), X, np.repeat(X[:, -1:], NO.PAD_POST, 1)])
    R = np.array([NO.one(X, ecg.shape[0], 20, 1000 * k + 7) for k in range(NO.NREAL)], dtype=float)
    md = np.nanmedian(R, axis=0)
    return {'d_onset': md[0], 'd_qrs': md[1], 'd_pdw': md[2], 'd_mdi': md[3], 'd_tmax_from_onset': md[4]}


def sites():
    S = json.load(open(os.path.join(OUT, 'sites.json')))
    return [s for s in S if s['family'] in ('rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course') or
            (s['family'] == 'lv_free_wall' and s['depth_target'] in (0.1, 0.9)) or
            (s['family'] == 'lv_septum' and s['depth_target'] == 0.1)]


def beat(net, cfg, s):
    T, nblock = solve(net, cfg, None if s is None else int(s['node']))
    tend = float(min(990, max(140, np.ceil((T.max() + 20) / 10) * 10)))
    t = np.arange(0, tend + 0.5, 1.0)
    ecg = CD.ecg_of(T, t, WECG, TM)
    r = {'id': 'his_driven' if s is None else s['id'], 'family': 'his' if s is None else s['family'],
         'depth_target': '' if s is None else s['depth_target'], 'blocked_entries': nblock,
         'total_activation_ms': round(float(T.max()), 2), 't10': round(frac_time(T, 0.1), 1), 't50': round(frac_time(T, 0.5), 1)}
    if s is None:
        t0 = float(T[LV].min())
        r.update({'hv_ms': round(float(T.min()), 1), 'qrs': round(float(T.max() - T.min()), 1),
                  'latest_after_lv_onset': round(float(T.max() - t0), 1),
                  'lv30': round(100 * float(NAREA[LVK][T[LVK] <= t0 + 30].sum() / NAREA[LVK].sum()), 1),
                  'lv37': round(100 * float(NAREA[LVK][T[LVK] <= t0 + 37.5].sum() / NAREA[LVK].sum()), 1),
                  'rv_breakthrough_after_lv_onset': round(float(T[RVE].min() - t0), 1)})
        return r
    r.update(true_scores(t, ecg, float(T.max())))
    r.update(detected_scores(ecg))
    return r


def run(name):
    cfg = SETS[name]
    net = network(cfg)
    d = os.path.join(HERE, name); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, 'beats.csv')
    rows = list(csv.DictReader(open(f))) if os.path.exists(f) else []
    done = {r['id'] for r in rows}
    S = sites() + ([None] if name in ('v3', 'J1') else [])     # His beat: J2 / J3 equal J1 (no paced site)
    t0 = time.time()
    for s in S:
        if ('his_driven' if s is None else s['id']) in done:
            continue
        rows.append(beat(net, cfg, s))
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(f, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(f'{name}: {len(rows)} beats, {time.time() - t0:.0f} s', flush=True)


def summary():
    out, his = [], {}
    for name in SETS:
        f = os.path.join(HERE, name, 'beats.csv')
        if not os.path.exists(f):
            continue
        b = pd.read_csv(f)
        h = b[b.family == 'his']
        if len(h):
            his[name] = h.iloc[0]
        b = b[b.family != 'his'].copy()
        b['depth_target'] = b['depth_target'].astype(float)
        fam, dp = b.family, b.depth_target
        M = {'RVOT': fam == 'rvot', 'cusp': fam == 'aortic_cusp', 'summit90': (fam == 'lv_summit') & (dp == 0.9),
             'vein90': (fam == 'lv_vein_course') & (dp == 0.9), 'LVendo10': fam.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)}
        r = {'set': name}
        for mode, col in (('true', 'mdi'), ('det20', 'd_mdi')):
            md = {k: float(b[m][col].median()) for k, m in M.items()}
            r.update({f'{mode}_{k}': round(v, 3) for k, v in md.items()})
            r[f'{mode}_order'] = bool(min(md['summit90'], md['vein90'], md['cusp']) > md['RVOT'] > md['LVendo10'])
        for fk, m in (('RVOT', M['RVOT']), ('cusp', M['cusp'])):
            x = b[m]
            r.update({f'{fk}_t10': x.t10.median(), f'{fk}_t50': x.t50.median(), f'{fk}_tmax': x.tmax.median(), f'{fk}_qrs': x.qrs.median(),
                      f'{fk}_pdw': x.pdw.median(), f'{fk}_d_onset': x.d_onset.median(), f'{fk}_d_qrs': x.d_qrs.median(),
                      f'{fk}_d_pdw': x.d_pdw.median(), f'{fk}_d_tmax': x.d_tmax_from_onset.median()})
        sc = fam.isin(['lv_summit', 'aortic_cusp'])
        r['summit_cusp_qrs'], r['summit_cusp_d_qrs'] = b[sc].qrs.median(), b[sc].d_qrs.median()
        fw = b[fam == 'lv_free_wall'].copy()
        fw['pos'] = fw['id'].map(lambda i: re.sub(r'_d\d+$', '', i))
        for mode, col in (('true', 'qrs'), ('det20', 'd_qrs')):
            p = fw[fw.depth_target == 0.9].set_index('pos')[col].to_frame('a').join(fw[fw.depth_target == 0.1].set_index('pos')[col].to_frame('b'))
            r[f'{mode}_fw_ratio_medians'] = round(float(p.a.median() / p.b.median()), 4)
            r[f'{mode}_fw_ratio_means'] = round(float(p.a.mean() / p.b.mean()), 4)
            r[f'{mode}_fw_pair_pct'] = round(float((100 * (p.a - p.b) / p.b).median()), 1)
        hh = his.get(name if name in ('v3', 'J1') else 'J1')
        if hh is not None:
            r.update({f'his_{k}': hh[k] for k in ('hv_ms', 'qrs', 'latest_after_lv_onset', 'lv30', 'lv37', 'rv_breakthrough_after_lv_onset')})
        r['rvot_blocked_entries_median'] = b[M['RVOT']].blocked_entries.median()
        out.append(r)
    S = pd.DataFrame(out)
    S.to_csv(os.path.join(HERE, 'summary.csv'), index=False)
    txt = S.set_index('set').T.to_string()
    open(os.path.join(HERE, 'summary.txt'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    if sys.argv[1] == 'time':
        S = [s for s in sites() if s['family'] == 'rvot'][:2]
        for nm in ('v3', 'J3b'):
            t0 = time.time(); beat(network(SETS[nm]), SETS[nm], S[0]); print(nm, f'{time.time() - t0:.1f} s per beat', flush=True)
    elif sys.argv[1] == 'run':
        for nm in sys.argv[2:]:
            run(nm)
    else:
        summary()
