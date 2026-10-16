#!/usr/bin/env python
"""
GUARDED COPY (16 Oct 2026, v5.1 brief Step 1.3, decision G) of analysis/v5_grid_2026-10-13/v5_grid.py
(sha256 c290bd3b613dbcf157b67c1512ef2891e479ef50122e938c43b9760c1d2a9c96, read-only; diff in this folder's README).
Changes, nothing else:
  paths   reads the protected folder (V5G: fibres_E, arm outputs); its own outputs go to runs/v51_2026-10-15/01_backup/;
          graph cache in runs/v51_2026-10-15/cache/ (the old cache folder is never read or written)
  guard a the graph cache key is the sha256 of every input of the cached object (heart, biv.elem, bivF.pts and fibre
          file sha256, the three speeds, edge-rule version); the key and inputs are stored in the cache file and checked
          on load; Heart(..., expect_fibre_sha256=...) stops if the fibre file's sha256 differs; HEART in the
          environment must equal the heart argument (k, mesh and AP template are read from it)
  same    a freshly built graph is rounded to float32 before use, as every v5 beat that loaded the cache (v5 adopted
          13 Oct, regen 14 Oct); without this a first build in the same process gave float64 times (F20, 6e-8)
  guard b k comes from sims/biv_model/14_purkinje.py graph_scale(), which now stops if the k file is missing
Original docstring follows.

v5 realism test grid, 13 Oct 2026 (Alex "go" 16:48 UTC on the coordinator's card; brief 22:47 UTC 12 Oct + 16:48 UTC 13 Oct).
EXPLORATORY: frozen v3 files are only read; everything new is under analysis/v5_grid_2026-10-13/.

Graph-only beats (combined myocardium + network shortest path of 14_purkinje.py, each heart's frozen graph scale k fitted
for the v3 speeds), network v3 as built (6G8DD8S5 with its complete left intrahisian cut), pseudo-Vm template and cb ECG
weights (15_conductor.py; lead fields and weights NOT rebuilt for arm E's fibres), scored with ecg_depth_criteria 0.3.0
as 10_measure_ecg.py (detected and true onset, site's Bazan region); all 144 sites per heart + the His beat.
Arms (myocardial speeds fibre / sheet / sheet-normal, m/s):
  A  0.60 / 0.48 / 0.48 everywhere (Taggart 2000: transverse 48 cm/s)
  B  A; in 6G8DD8S5 and 7D98EVAR sheet x0.73 and sheet-normal x0.70 (0.60 / 0.3504 / 0.336) (Glukhov 2012)
  C  B + per-junction antegrade delay ~ N(4.85, 1.55) ms truncated to 2-13 ms (Joyner 1985; Choi 2023), retrograde
     2 ms unchanged; seed 20261013 per heart (values saved)
  E  C + the outflow-tract fibre fix of analysis/fibre_fix_2026-10-13 (per-tract apex-to-outflow fields; aortic-root
     interface as epicardium) recomputed for each heart into fibres_E/<HEART>/
  (D dropped: the 6G8DD8S5 cut is already a complete left intrahisian block.)
No-network control: control heart, arms A (= B = C speeds there) and E fibres, every site without the network.
Detected onset with 20 uV noise + 0.5-150 Hz + notch (20 realisations, analysis/noise_onset_2026-10-12) for the control
heart's Daniels families.

Usage (venv; PATH with mpiexec for `fibres`):
  HEART=<H> python v5_grid.py fibres            arm-E fibres for one heart
  HEART=<H> python v5_grid.py run <arm> [nonet] beats for one heart and arm (resumable)
  python v5_grid.py gates                        gate table v3 / A / B / C / E
"""

import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
V5G = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13')          # protected: read only
OUTR = os.path.join(REPO, 'runs', 'v51_2026-10-15', '01_backup')
CACHE = os.path.join(REPO, 'runs', 'v51_2026-10-15', 'cache')
EDGE_RULE = 'tet-edges-v5: unique tet edges, t = |(d.f/v_f, d.s/v_s, d.n/v_n)|, fastest element wins, float32'
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
HF = {'6G8DD8S5', '7D98EVAR'}
ARMS = ['A', 'B', 'C', 'E']
SEED = 20261013
RUNS = os.path.join(REPO, 'runs')
DANIELS_FAM = ('rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def speeds(arm, h):
    s, n = 0.48, 0.48
    if arm in ('B', 'C', 'E') and h in HF:
        s, n = s * 0.73, n * 0.70
    return 0.60, s, n


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def cache_inputs(h, lonf, sp):
    """Every input of the cached myocardial graph, and the key (sha256 of their JSON)."""
    inp = {'heart': h, 'elem_sha256': sha256(hd(h, 'biv.elem')), 'pts_sha256': sha256(os.path.realpath(hd(h, 'bivF.pts'))),
           'fibre_file': os.path.relpath(os.path.realpath(lonf), REPO), 'fibre_sha256': sha256(lonf),
           'speeds_f_s_n_m_s': [repr(float(x)) for x in sp], 'edge_rule': EDGE_RULE}
    return inp, hashlib.sha256(json.dumps(inp, sort_keys=True).encode()).hexdigest()


def mem_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


# ------------------------------------------------------------------ arm-E fibres
def fibres():
    h = os.environ['HEART']
    d = os.path.join(OUTR, 'fibres_E', h); os.makedirs(d, exist_ok=True)
    fx = os.path.join(REPO, 'analysis', 'fibre_fix_2026-10-13')
    L = module('lapfix', os.path.join(fx, 'laplace_fix.py'))
    L.LAP = os.path.join(d, 'laplace')
    sys.argv = ['laplace_fix.py', '--np', os.environ.get('LAP_NP', '2')]
    L.main()
    F = module('fibfix', os.path.join(fx, 'fibres_fix.py'))
    F.HERE, F.LAP_FIX = d, os.path.join(d, 'laplace')
    F.main()


# ------------------------------------------------------------------ beats
class Heart:
    def __init__(self, arm, h, expect_fibre_sha256=None):
        if os.environ.get('HEART') != h:
            raise ValueError(f"HEART in the environment ({os.environ.get('HEART')}) is not {h}: k, mesh and template would be another heart's")
        self.h, self.arm = h, arm
        lonf = os.path.join(V5G, 'fibres_E', h, 'bivF.lon') if arm == 'E' else hd(h, 'bivF.lon')
        self.fibre_sha256 = sha256(lonf)
        if expect_fibre_sha256 is not None and self.fibre_sha256 != expect_fibre_sha256:
            raise ValueError(f'fibre file {lonf}: sha256 {self.fibre_sha256} is not the expected {expect_fibre_sha256}')
        self.PK = module('pk', os.path.join(B, '14_purkinje.py'))
        self.CD = module('cd', os.path.join(B, '15_conductor.py'))
        self.JOBS = module('jobs', os.path.join(B, 'jobs_2026-10-07.py'))
        self.NO = module('no', os.path.join(REPO, 'analysis', 'noise_onset_2026-10-12', 'noise_onset.py'))
        from ecg_depth_criteria import evaluate, from_leads, measure_beat
        import ecg_depth_criteria as edc
        self.evaluate, self.from_leads, self.measure_beat, self.ver = evaluate, from_leads, measure_beat, edc.__version__
        self.pts, z, phi, v = self.PK.load()
        self.N = len(self.pts)
        self.net = dict(np.load(hd(h, 'purkinje', 'network.npz')))
        self.k = self.PK.graph_scale()
        self.e, self.w = self.myo(lonf, speeds(arm, h))
        self.W = np.load(hd(h, 'ecgW_nofast_cb.npz'))['W'].astype(float)
        self.TM = self.CD.Template()
        M = len(self.net['pmj'])
        if arm in ('C', 'E'):
            rng = np.random.default_rng(SEED)
            x = rng.normal(4.85, 1.55, M)
            while ((x < 2) | (x > 13)).any():
                bad = (x < 2) | (x > 13); x[bad] = rng.normal(4.85, 1.55, int(bad.sum()))
            self.d_ant = x
        else:
            self.d_ant = np.full(M, 4.0)

    def myo(self, lonf, sp):
        inp, key = cache_inputs(self.h, lonf, sp)
        self.cache_key, self.cache_inputs = key, inp
        f = os.path.join(CACHE, f'myo_{self.h}_{key[:16]}.npz'); os.makedirs(os.path.dirname(f), exist_ok=True)
        if os.path.exists(f):
            d = np.load(f)
            if str(d['key']) != key:
                raise ValueError(f'cache file {f} holds key {d["key"]}, not {key}')
            return d['e'].astype(np.int64), d['w'].astype(float) / self.k
        E = pd.read_csv(hd(self.h, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
        lon = pd.read_csv(lonf, sep=r'\s+', skiprows=1, header=None).to_numpy()
        fb, sh = lon[:, :3], lon[:, 3:6]; nm = np.cross(fb, sh)
        N, P = self.N, self.pts
        keys, ws = [], []
        for a_, b_ in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):       # PK.myo_graph rule with the arm's speeds
            dv = P[E[:, b_]] - P[E[:, a_]]
            t = np.sqrt((np.einsum('ij,ij->i', dv, fb) / sp[0]) ** 2 + (np.einsum('ij,ij->i', dv, sh) / sp[1]) ** 2 + (np.einsum('ij,ij->i', dv, nm) / sp[2]) ** 2)
            lo, hi = np.minimum(E[:, a_], E[:, b_]), np.maximum(E[:, a_], E[:, b_])
            keys.append(lo * N + hi); ws.append(t)
        key, inv = np.unique(np.concatenate(keys), return_inverse=True)
        w = np.full(len(key), np.inf); np.minimum.at(w, inv.ravel(), np.concatenate(ws))
        e = np.c_[key // N, key % N]
        np.savez(f, e=e.astype(np.int32), w=w.astype(np.float32), key=self.cache_key, inputs=json.dumps(self.cache_inputs))
        json.dump(self.cache_inputs | {'key': self.cache_key}, open(f[:-4] + '.json', 'w'), indent=1)
        return e.astype(np.int64), w.astype(np.float32).astype(float) / self.k

    def solve(self, site_node=None, nonet=False):
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import dijkstra
        N, e, w = self.N, self.e, self.w
        rows, cols, data = [e[:, 0], e[:, 1]], [e[:, 1], e[:, 0]], [w, w]
        if nonet:
            M = 0
        else:
            net = self.net; M = len(net['nodes'])
            gn = self.PK.net_graph(net, self.pts).tocoo(); kk = (gn.row < M) & (gn.col < M)
            m = net['nodes'][net['pmj']]; j = N + net['pmj']
            rows += [N + gn.row[kk], m, j]; cols += [N + gn.col[kk], j, m]
            data += [gn.data[kk], np.full(len(m), 2.0), self.d_ant]
        src = N + M
        if site_node is None:
            rows.append(np.array([src])); cols.append(np.array([N + int(self.net['his'])])); data.append(np.array([1e-6]))
        else:
            pu = self.pts * 1e3
            s = np.where(np.linalg.norm(pu - pu[site_node], axis=1) < 1500)[0]
            rows.append(np.full(len(s), src)); cols.append(s); data.append(np.full(len(s), 1e-6))
        G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
        return (dijkstra(G, directed=True, indices=src) - 1e-6)[:N]

    def ecg(self, T):
        tend = float(min(990, max(140, np.ceil((T.max() + 20) / 10) * 10)))
        t = np.arange(0, tend + 0.5, 1.0)
        return t, self.CD.ecg_of(T, t, self.W, self.TM)

    def score(self, ecg, last, region):
        L = self.CD.LEADS; pad = 60
        leads = {l: np.concatenate([np.full(pad, ecg[0, L.index(l)]), ecg[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
        bw = (pad - 45.0, pad - 5.0)
        out = {'package_version': self.ver}
        for name, kw in (('detected', dict(baseline_window_ms=bw)), ('true', dict(onset_ms=pad, offset_ms=last + pad, baseline_window_ms=bw))):
            m = self.measure_beat(self.from_leads(leads), 1000.0, **kw)
            c = self.evaluate(m, region) if region else {}
            m = {k: (v - pad if k in ('onset_ms', 'visible_onset_ms', 'offset_precordial_ms', 'offset_any_lead_ms') and isinstance(v, (int, float)) else v)
                 for k, v in m.items()}
            out[name] = {'measurements': m, 'criteria': c}
        return self.JOBS.flatten(json.loads(json.dumps(out, default=lambda o: o.item() if hasattr(o, 'item') else (o.tolist() if hasattr(o, 'tolist') else str(o)))))

    def det20(self, ecg):
        NO = self.NO
        X = np.stack([ecg[:, self.CD.LEADS.index(l)] for l in NO.LEADS])
        X = np.hstack([np.repeat(X[:, :1], NO.PAD_PRE, 1), X, np.repeat(X[:, -1:], NO.PAD_POST, 1)])
        R = np.array([NO.one(X, ecg.shape[0], 20, 1000 * k + 7) for k in range(NO.NREAL)], dtype=float)
        md = np.nanmedian(R, axis=0)
        return {'det20_onset_ms': md[0], 'det20_qrs_ms': md[1], 'det20_pdw_ms': md[2], 'det20_mdi': md[3], 'det20_tmax_from_onset_ms': md[4]}


def run(arm, nonet=False):
    h = os.environ['HEART']
    H = Heart(arm, h)
    d = os.path.join(OUTR, arm, h); os.makedirs(d, exist_ok=True)
    json.dump({'arm': arm, 'heart': h, 'speeds_f_s_n': speeds(arm, h), 'graph_scale_k': H.k, 'd_ret_ms': 2.0,
               'd_ant': 'N(4.85, 1.55) truncated 2-13, seed %d' % SEED if arm in ('C', 'E') else 4.0,
               'fibres': 'fibres_E (outflow fix)' if arm == 'E' else 'frozen bivF.lon', 'lead_fields': 'cb, not rebuilt'},
              open(os.path.join(d, 'config.json'), 'w'), indent=1)
    if arm in ('C', 'E'):
        np.save(os.path.join(d, 'd_ant_per_junction.npy'), H.d_ant)
    f = os.path.join(d, 'beats_nonet.csv' if nonet else 'beats.csv')
    rows = list(csv.DictReader(open(f))) if os.path.exists(f) else []
    done = {r['id'] for r in rows}
    S = json.load(open(hd(h, 'sites.json')))
    todo = ([] if nonet else [None]) + S
    t0 = time.time()
    for s in todo:
        sid = 'his_driven' if s is None else s['id']
        if sid in done:
            continue
        if mem_mb() < 700:
            sys.exit(f'stopped: available memory {mem_mb():.0f} MB (resumable)')
        T = H.solve(None if s is None else int(s['node']), nonet=nonet)
        t, ecg = H.ecg(T)
        if s is None:
            np.save(os.path.join(d, 'his_T.npy'), T.astype(np.float32))
            np.save(os.path.join(d, 'his_ecg.npy'), ecg.astype(np.float32))
            row = {'id': 'his_driven', 'family': 'his', 'total_activation_ms': float(T.max()), 'first_myocardium_ms': float(T.min())}
            row.update(H.score(ecg, float(T.max()), None))
        else:
            row = {k: v for k, v in s.items() if not isinstance(v, (list, dict))}
            row['total_activation_ms'] = float(T.max())
            row.update(H.score(ecg, float(T.max()), s.get('bazan_region')))
            if h == 'Y5HYEDL4' and not nonet and (s['family'] in DANIELS_FAM or s['depth_target'] == 0.1):
                row.update(H.det20(ecg))
        rows.append(row)
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(f, 'w', newline='') as fh:
            wr = csv.DictWriter(fh, fieldnames=keys); wr.writeheader(); wr.writerows(rows)
    print(f'{arm} {h}{" nonet" if nonet else ""}: {len(rows)} beats, {time.time() - t0:.0f} s', flush=True)


# ------------------------------------------------------------------ gates
def b(x):
    return str(x).strip().lower() in ('true', '1', '1.0')


def wilson(k, n, z=1.96):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return (100 * (c - hw), 100 * (c + hw))


def pairs(df, fam):
    d = df[df.family == fam]
    key = ['position', 'level_z'] if fam in ('lv_free_wall', 'rv_free_wall') else ['position']
    a = d[d.depth_target == 0.9].set_index(key); c = d[d.depth_target == 0.1].set_index(key)
    return a.join(c, lsuffix='_90', rsuffix='_10', how='inner')


def rel(p, col):
    return 100 * (p[col + '_90'] - p[col + '_10']) / p[col + '_10']


def his_metrics(h, T, ecg):
    from scipy.spatial import cKDTree
    from ecg_depth_criteria import from_leads, measure_beat
    pts = pd.read_csv(hd(h, 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    z, phi, v = (np.loadtxt(hd(h, 'uvc', n + '.dat')) for n in ('z', 'phi', 'v')); ph = np.degrees(phi)
    rd = lambda n: np.loadtxt(hd(h, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    t0 = float(T[lv].min())
    tri = np.loadtxt(hd(h, 'surfaces', 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    ta = 0.5 * np.linalg.norm(np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]]), axis=1)
    na = np.bincount(tri.ravel(), weights=np.repeat(ta / 3, 3), minlength=len(pts))
    keep = lv[~((z >= 2 / 3) & (ph >= -150) & (ph <= -30))[lv]]
    out = {'qrs_true_span_ms': round(float(T.max() - T.min()), 1), 'his_to_first_myocardium_ms': round(float(T.min()), 1),
           'T_latest_after_lv_onset_ms': round(float(T.max() - t0), 1),
           'b_lv30_pct': round(100 * float(na[keep][T[keep] <= t0 + 30].sum() / na[keep].sum()), 1),
           'b_lv37_pct': round(100 * float(na[keep][T[keep] <= t0 + 37.5].sum() / na[keep].sum()), 1),
           'c_rv_epi_breakthrough_ms': round(float(T[epi[v[epi] == 1]].min() - t0), 1)}
    tg = {'ant': (60.0, 0.80), 'sep': (0.0, 0.50), 'post': (-60.0, 0.33)}
    for k, (p_, zz) in tg.items():
        dd = (z[lv] - zz) ** 2 + (np.abs(np.angle(np.exp(1j * np.radians(ph[lv] - p_)))) / np.pi) ** 2
        n = int(lv[np.argmin(dd)])
        out[f'a_onset_{k}_ms'] = round(float(T[lv][np.linalg.norm(pts[lv] - pts[n], axis=1) <= 10].min() - t0), 1)
    el = pd.read_csv(hd(h, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    a_, b_, c_, d_ = (pts[el[:, k]] for k in range(4))
    nvol = np.bincount(el.ravel(), weights=np.repeat(np.abs(np.einsum('ij,ij->i', np.cross(b_ - a_, c_ - a_), d_ - a_)) / 24, 4), minlength=len(pts))
    o = np.argsort(T); last = o[np.cumsum(nvol[o]) / nvol.sum() > 0.95]
    dpv = cKDTree(pts[rd('pv_rim')]).query(pts[last])[0]; dtv = cKDTree(pts[rd('tv_rim')]).query(pts[last])[0]
    zl, pl, vl, wl = z[last], ph[last], v[last], nvol[last]
    lst = ((vl == 0) & (zl >= 2 / 3) & ((np.abs(pl) > 150) | ((pl >= -150) & (pl <= -30)))) | ((vl == 1) & (((zl >= 2 / 3) & (pl < -20)) | (dtv <= 10) | (dpv <= 20)))
    out['d_last5_in_durrer_areas_pct'] = round(100 * float(wl[lst].sum() / wl.sum()), 1)
    pad = 60; L = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    leads = {l: np.concatenate([np.full(pad, ecg[0, L.index(l)]), ecg[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    out['e_qrs_detected_ms'] = measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))['qrs_duration_ms']
    t = np.arange(ecg.shape[0], dtype=float); msk = (t >= T.min()) & (t <= T.max() + 3)
    ang = np.radians([0, 60, 120, -150, -30, 90]); A = np.c_[np.cos(ang), np.sin(ang)]
    for nm_, fn in (('net', lambda y: y[msk].max() + y[msk].min()), ('area', lambda y: y[msk].sum())):
        cc = np.linalg.lstsq(A, np.array([fn(ecg[:, j] - ecg[0, j]) for j in range(6)]), rcond=None)[0]
        out[f'axis_{nm_}_deg'] = int(round(float(np.degrees(np.arctan2(cc[1], cc[0])))))
    if h == '6G8DD8S5':
        t_rv, t_epi = cKDTree(pts[rv]), cKDTree(pts[epi])
        lvs = lv[t_rv.query(pts[lv])[0] < t_epi.query(pts[lv])[0]]
        out.update({'lbbb_lv_minus_rv_onset_ms': round(float(T[lv].min() - T[rv].min()), 1),
                    'lbbb_first_lv_septal_breakthrough_ms': round(float(T[lvs].min() - T.min()), 1)})
    return out


def load_set(name):
    """{heart: (sites df, His T, His ECG (n, 12)), 'nonet': df} for v3 (stored) or an arm."""
    out = {}
    for h in HEARTS:
        if name == 'v3':
            df = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}_cb.csv'))
            run = {'Y5HYEDL4': '2026-10-08_purk_sinus5_Y5HYEDL4'}.get(h, f'2026-10-09_purk_sinus_{h}')
            bb = open(os.path.join(RUNS, run, 'act.igb'), 'rb').read(); x = int(bb[:1024].decode('latin1').split('x:')[1].split()[0])
            T = np.frombuffer(bb[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float)
            dd = os.path.join(RUNS, run + '_ecg_cb', 'POSTPROC_DIR')
            ecg = np.stack([np.loadtxt(os.path.join(dd, f'ECG_{l}.dat'))[:, 1] for l in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']], 1)
            det = pd.read_csv(os.path.join(REPO, 'analysis', 'junction_tests_2026-10-12', 'v3', 'beats.csv')) if h == 'Y5HYEDL4' else None
            if det is not None:
                df = df.merge(det[['id', 'd_mdi']].rename(columns={'d_mdi': 'det20_mdi'}), on='id', how='left')
        else:
            arm = 'A' if (name == 'B' and h not in HF) else name
            f = os.path.join(V5G, arm, h, 'beats.csv')
            if not os.path.exists(f):
                continue
            df = pd.read_csv(f)
            df = df[df.family != 'his']
            T = np.load(os.path.join(V5G, arm, h, 'his_T.npy')).astype(float)
            ecg = np.load(os.path.join(V5G, arm, h, 'his_ecg.npy')).astype(float)
        df = df.copy(); df['depth_target'] = df.depth_target.astype(float)
        out[h] = (df, T, ecg)
    if name == 'v3':
        out['nonet'] = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', 'nofast_Y5HYEDL4.csv'))
    else:
        f = os.path.join(V5G, 'E' if name == 'E' else 'A', 'Y5HYEDL4', 'beats_nonet.csv')
        out['nonet'] = pd.read_csv(f) if os.path.exists(f) else None
    return out


def gate_column(name):
    S = load_set(name)
    g = {}
    for h in HEARTS:
        if h not in S:
            continue
        df, T, ecg = S[h]
        hm = his_metrics(h, T, ecg)
        for k_, v_ in hm.items():
            g[f'His {h[:2]} {k_}'] = v_
        p = pairs(df, 'rv_free_wall'); pl = pairs(df, 'lv_free_wall')
        rr, lr = rel(p, 'true_qrs_duration_ms').median(), rel(pl, 'true_qrs_duration_ms').median()
        g[f'Bazan2006 {h[:2]} RV / LV rel QRS %'] = f'{rr:.1f} / {lr:.1f}'
        g[f'Bazan2006 {h[:2]} pass (-1.9..6.6, < LV)'] = bool(-1.9 <= rr <= 6.6 and rr < lr)
        g[f'LV fw QRS 90/10 {h[:2]} medians / means'] = f"{pl.true_qrs_duration_ms_90.median() / pl.true_qrs_duration_ms_10.median():.4f} / {pl.true_qrs_duration_ms_90.mean() / pl.true_qrs_duration_ms_10.mean():.4f}"
        g[f'summit+cusp QRS {h[:2]}'] = float(df[df.family.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median())
        if h == '6G8DD8S5':
            vals = {k_: rel(pl, c).median() for k_, c in (('QRS', 'true_qrs_duration_ms'), ('PdW', 'true_pseudo_delta_ms'), ('IDT', 'true_idt_v2_ms'), ('RS', 'true_srs_ms'))}
            g['Berruezo 6G QRS / PdW / IDT / RS %'] = ' / '.join(f'{v:.1f}' for v in vals.values())
            g['Berruezo 6G pass'] = bool(-1 <= vals['QRS'] <= 25 and 12 <= vals['IDT'] <= 86 and 20 <= vals['RS'] <= 52 and all(v > 0 for v in vals.values()))
        if h == 'Y5HYEDL4':
            fam, dp = df.family, df.depth_target
            M = {'RVOT': fam == 'rvot', 'cusp': fam == 'aortic_cusp', 'summit90': (fam == 'lv_summit') & (dp == 0.9),
                 'vein90': (fam == 'lv_vein_course') & (dp == 0.9), 'LVendo10': fam.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)}
            for mode, col in (('true', 'true_mdi_daniels'), ('det20', 'det20_mdi')):
                if col not in df:
                    continue
                md = {k_: float(df[m][col].median()) for k_, m in M.items()}
                g[f'Daniels {mode} RVOT/cusp/summit90/vein90/LVendo10'] = ' / '.join(f'{md[k_]:.3f}' for k_ in M)
                g[f'Daniels {mode} pass'] = bool(min(md['summit90'], md['vein90'], md['cusp']) > md['RVOT'] > md['LVendo10'])
            nn = S.get('nonet')
            if nn is not None:
                fams = ['lv_free_wall', 'lv_septum', 'rv_free_wall', 'rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course']
                wider = all(nn[nn.family == f_].true_qrs_duration_ms.median() > df[df.family == f_].true_qrs_duration_ms.median() for f_ in fams)
                sc = float(nn[nn.family.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median())
                g['No-network summit+cusp QRS / wider all families'] = f'{sc:.1f} / {wider}'
                g['No-network pass'] = bool(sc > 193 and wider)
    # Bazan 2007, pooled (package rule, true onset, LV wall families)
    allr = pd.concat([S[h][0].assign(heart=h) for h in HEARTS if h in S])
    for key, (reg, col, sign, bz) in {'apical_superior qI': ('lv_apical_superior', 'true_q_lead_I', 1, (88, 26)),
                                      'basal_superior qI': ('lv_basal_superior', 'true_q_lead_I', 1, (90, 16)),
                                      'basal_inferior qinf': ('lv_basal_inferior', 'true_inferior_q_any', 1, (81, 37)),
                                      'apical_inferior qinf': ('lv_apical_inferior', 'true_inferior_q_any', 1, (92, 33)),
                                      'basal_superior qinf (less at epi)': ('lv_basal_superior', 'true_inferior_q_any', -1, None)}.items():
        d = allr[(allr.bazan_region == reg) & allr.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit'])]
        k9, n9 = int(d[d.depth_target == 0.9][col].map(b).sum()), int((d.depth_target == 0.9).sum())
        k1, n1 = int(d[d.depth_target == 0.1][col].map(b).sum()), int((d.depth_target == 0.1).sum())
        ok_dir = (k9 / n9 > k1 / n1) if sign > 0 else (k9 / n9 < k1 / n1)
        inci = None
        if bz:
            c9, c1 = wilson(k9, n9), wilson(k1, n1)
            inci = c9[0] <= bz[0] <= c9[1] and c1[0] <= bz[1] <= c1[1]
        g[f'Bazan2007 {key} 90 vs 10 (n pos)'] = f'{k9}/{n9} vs {k1}/{n1} ({n9})'
        g[f'Bazan2007 {key} direction / Bazan in CI'] = f'{ok_dir} / {inci}'
    return g


def gates():
    cols = {}
    for name in ['v3'] + ARMS:
        try:
            cols[name] = gate_column(name)
        except Exception as ex:                                  # an arm not run yet
            print(f'{name}: not available ({ex})', flush=True)
    G = pd.DataFrame(cols)
    G.to_csv(os.path.join(OUTR, 'gates.csv'))
    txt = G.to_string()
    open(os.path.join(OUTR, 'gates.txt'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'fibres':
        fibres()
    elif cmd == 'run':
        run(sys.argv[2], nonet=len(sys.argv) > 3 and sys.argv[3] == 'nonet')
    elif cmd == 'gates':
        gates()
