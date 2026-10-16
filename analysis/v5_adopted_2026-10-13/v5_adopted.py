#!/usr/bin/env python
"""
Model v5, adopted 13 Oct 2026 (Alex chose "Report" at 18:13 UTC, relayed by the coordinator): v3 plus
  (a) cross-fibre (sheet) speed 0.48 m/s in all hearts (Taggart 2000)
  (b) 6G8DD8S5 and 7D98EVAR: sheet x0.73, sheet-normal x0.70 (Glukhov 2012) -> 0.60 / 0.3504 / 0.336 m/s
  (c) Doste 2019 outflow-tract fibres in all hearts (analysis/v5_grid_2026-10-13/fibres_E/<HEART>/bivF.lon)
Unchanged: network v3 as built (distal 2 m/s, junction 4 / 2 ms, no spread), cb conductor (heart at Clerc scale + blood),
T13, ecg_depth_criteria 0.3.0, site grid v5, graph scale k per heart. Frozen v3 files are only read.

The cb lead fields and the ECG weights use the fibre field (anisotropic heart conductivity along the mesh fibres), so
they are rebuilt with the v5 fibres, one heart at a time with 15_conductor.py's leadfield() (three openCARP runs of
<= 3 leads, light AMG options, 900 MB watchdog), on a v5 copy of the torso mesh whose heart-element fibres are the
v5 fibres rotated into the torso frame (R of data/torso/atria/<HEART>_to_g001_rigid.txt, as 08_torso.py place()).

Stages (HEART=<id> for the per-heart ones; venv active):
  mesh       mesh/<H>/bivF.* (v5 fibres) and torso/<H>/full_nofast_blood.* (v5 heart fibres), electrodes linked
  leadfield  runs/2026-10-13_LF_<H>_v5 (cb conductor, v5 fibres)
  weights    ecgW_v5_<H>.npz (13_fast_ecg.py weights on the v5 heart mesh and lead fields) + check vs the v3 cb weights
  grid       all 144 sites + His beat, graph-only, ECG with the v5 weights, scored as 10_measure_ecg.py -> purk_<H>_v5.csv
  gates      v3 vs v5 gate table (Durrer T window 62-100 ms, the approved one)
"""

import csv
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
VGD = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13')
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LF_RUN = '2026-10-13_LF_{}_v5'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def link(src, dst):
    if not os.path.lexists(dst):
        os.symlink(src, dst)


def mesh():
    h = os.environ['HEART']
    m = os.path.join(HERE, 'mesh', h); os.makedirs(m, exist_ok=True)
    link(os.path.realpath(hd(h, 'bivF.pts')), os.path.join(m, 'bivF.pts'))
    link(os.path.realpath(hd(h, 'bivF.elem')), os.path.join(m, 'bivF.elem'))
    lon5 = os.path.join(VGD, 'fibres_E', h, 'bivF.lon')
    link(lon5, os.path.join(m, 'bivF.lon'))
    t = os.path.join(HERE, 'torso', h); os.makedirs(t, exist_ok=True)
    for ext in ('pts', 'elem'):
        link(os.path.realpath(hd(h, 'torso', f'full_nofast_blood.{ext}')), os.path.join(t, f'full_nofast_blood.{ext}'))
    link(hd(h, 'torso', 'electrodes'), os.path.join(t, 'electrodes'))
    R = np.loadtxt(os.path.join(REPO, 'data', 'torso', 'atria', f'{h}_to_g001_rigid.txt'))[:3]
    L = pd.read_csv(lon5, sep=r'\s+', skiprows=1, header=None).to_numpy()
    Lt = np.hstack([L[:, :3] @ R.T, L[:, 3:] @ R.T])
    nh = int(open(hd(h, 'torso', 'heart.elem')).readline())
    assert nh == len(Lt), (nh, len(Lt))
    src = os.path.realpath(hd(h, 'torso', 'full_nofast_blood.lon'))
    old = pd.read_csv(src, sep=r'\s+', skiprows=1, header=None, nrows=nh).to_numpy()
    L3 = pd.read_csv(hd(h, 'bivF.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    chk = float(np.abs(old - np.hstack([L3[:, :3] @ R.T, L3[:, 3:] @ R.T])).max())   # frozen heart part = v3 fibres @ R.T
    out = os.path.join(t, 'full_nofast_blood.lon')
    with open(src) as fi, open(out, 'w') as fo:
        fo.write(fi.readline())
        np.savetxt(fo, Lt, fmt='%.5f')
        for _ in range(nh):
            fi.readline()
        for line in fi:
            fo.write(line)
    print(json.dumps({'heart': h, 'heart_elements': nh, 'v3_lon_reproduced_max_abs': round(chk, 6), 'torso_lon': out}), flush=True)


def leadfield():
    h = os.environ['HEART']
    CD = module('cd', os.path.join(B, '15_conductor.py'))
    CD.TOR = os.path.join(HERE, 'torso', h)
    CD.LF_RUN = LF_RUN.format(h)
    t0 = time.time()
    res = CD.leadfield(np_=2)
    res['wall_s_total'] = round(time.time() - t0)
    json.dump(res, open(os.path.join(HERE, f'leadfield_{h}.json'), 'w'), indent=1, default=str)
    print(json.dumps(res, default=str), flush=True)


def weights():
    h = os.environ['HEART']
    CD = module('cd', os.path.join(B, '15_conductor.py'))
    fe = CD.module('fe', '13_fast_ecg.py')
    cal, s = CD.scaled_cal()
    lf = os.path.join(REPO, 'runs', LF_RUN.format(h), 'POSTPROC_DIR')
    W = fe.weights(os.path.join(HERE, 'mesh', h, 'bivF'), lf, fe.conductivities(cal), 'm', -1.0, True)
    f = os.path.join(HERE, f'ecgW_v5_{h}.npz')
    np.savez(f, W=W.astype(np.float32), sigma='m', c=-1.0, lf_dir=lf, mesh=os.path.join(HERE, 'mesh', h, 'bivF'), nofast=True,
             conductor='cb', scale=s, fibres='v5 (Doste OT fix)')
    W3 = np.load(hd(h, 'ecgW_nofast_cb.npz'))['W'].astype(float)
    r = {l: round(float(np.corrcoef(W[i], W3[i])[0, 1]), 4) for i, l in enumerate(CD.LEADS)}
    lf3 = os.path.join(REPO, 'runs', f'2026-10-10_LF_{h}_cb', 'POSTPROC_DIR')
    rl = {}
    for l in CD.LEADS:
        a = np.fromfile(os.path.join(lf, f'LF_{l}.igb'), dtype='<f4', offset=1024)
        b = np.fromfile(os.path.join(lf3, f'LF_{l}.igb'), dtype='<f4', offset=1024)
        rl[l] = round(float(np.corrcoef(a, b)[0, 1]), 5)
    json.dump({'weights_corr_v5_vs_v3cb': r, 'leadfield_corr_v5_vs_v3cb': rl}, open(os.path.join(HERE, f'weights_check_{h}.json'), 'w'), indent=1)
    print(h, 'weights r', min(r.values()), '-', max(r.values()), '| lead fields r', min(rl.values()), '-', max(rl.values()), flush=True)


def grid():
    h = os.environ['HEART']
    VG = module('vg', os.path.join(VGD, 'v5_grid.py'))
    H = VG.Heart('E', h)                                   # E speeds (= B: v5 a + b) and v5 fibres; myocardial graph from the cache
    H.d_ant = np.full(len(H.net['pmj']), 4.0)            # v3 junctions (no spread)
    H.W = np.load(os.path.join(HERE, f'ecgW_v5_{h}.npz'))['W'].astype(float)
    d = os.path.join(HERE, 'grid', h); os.makedirs(d, exist_ok=True)
    f = os.path.join(HERE, f'purk_{h}_v5.csv')
    rows = list(csv.DictReader(open(f))) if os.path.exists(f) else []
    done = {r['id'] for r in rows}
    t0 = time.time()
    for s in [None] + json.load(open(hd(h, 'sites.json'))):
        sid = 'his_driven' if s is None else s['id']
        if sid in done:
            continue
        if VG.mem_mb() < 700:
            sys.exit(f'stopped: available memory {VG.mem_mb():.0f} MB (resumable)')
        T = H.solve(None if s is None else int(s['node']))
        t, ecg = H.ecg(T)
        if s is None:
            np.save(os.path.join(d, 'his_T.npy'), T.astype(np.float32)); np.save(os.path.join(d, 'his_ecg.npy'), ecg.astype(np.float32))
            row = {'heart': h, 'id': 'his_driven', 'family': 'his', 'method': 'graph_v5', 'total_activation_ms': float(T.max())}
            row.update(H.score(ecg, float(T.max()), None))
        else:
            row = {'heart': h, 'method': 'graph_v5', 'run': '', 'total_activation_ms': float(T.max())}
            row.update({k: v for k, v in s.items() if not isinstance(v, (list, dict))})
            row.update(H.score(ecg, float(T.max()), s.get('bazan_region')))
            if h == 'Y5HYEDL4' and (s['family'] in VG.DANIELS_FAM or s['depth_target'] == 0.1):
                row.update(H.det20(ecg))
        rows.append(row)
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(f, 'w', newline='') as fh:
            wr = csv.DictWriter(fh, fieldnames=keys); wr.writeheader(); wr.writerows(rows)
    print(f'v5 {h}: {len(rows)} beats, {time.time() - t0:.0f} s', flush=True)


def gates():
    VG = module('vg', os.path.join(VGD, 'v5_grid.py'))
    orig = VG.load_set

    def load_v5(name):
        if name != 'v5':
            return orig(name)
        out = {}
        for h in HEARTS:
            df = pd.read_csv(os.path.join(HERE, f'purk_{h}_v5.csv'))
            df = df[df.family != 'his'].copy(); df['depth_target'] = df.depth_target.astype(float)
            T = np.load(os.path.join(HERE, 'grid', h, 'his_T.npy')).astype(float)
            ecg = np.load(os.path.join(HERE, 'grid', h, 'his_ecg.npy')).astype(float)
            out[h] = (df, T, ecg)
        out['nonet'] = pd.read_csv(os.path.join(VGD, 'E', 'Y5HYEDL4', 'beats_nonet.csv'))   # v5 speeds + fibres, no network
        return out
    VG.load_set = load_v5
    cols = {n: VG.gate_column(n) for n in ('v3', 'v5')}
    G = pd.DataFrame(cols)
    for h in HEARTS:                                        # approved Durrer windows
        for n in ('v3', 'v5'):
            T = G.loc[f'His {h[:2]} T_latest_after_lv_onset_ms', n]
            G.loc[f'Durrer {h[:2]} T 62-100 ms pass', n] = bool(62 <= float(T) <= 100)
            G.loc[f'Durrer {h[:2]} RV breakthrough 20-31 ms pass', n] = bool(20 <= float(G.loc[f'His {h[:2]} c_rv_epi_breakthrough_ms', n]) <= 31)
            G.loc[f'Durrer {h[:2]} detected QRS 63-88 ms pass', n] = bool(63 <= float(G.loc[f'His {h[:2]} e_qrs_detected_ms', n]) <= 88)
    G.to_csv(os.path.join(HERE, 'gates_v3_v5.csv'))
    txt = G.to_string()
    open(os.path.join(HERE, 'gates_v3_v5.txt'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    {'mesh': mesh, 'leadfield': leadfield, 'weights': weights, 'grid': grid, 'gates': gates}[sys.argv[1]]()
