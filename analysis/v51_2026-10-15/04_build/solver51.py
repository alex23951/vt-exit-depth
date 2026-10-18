"""Step 4.3 driver (v5.1 brief, decision C; F01): stencil build, factor fit, acceptance A (synthetic slab), B (held-out
regions), S13 (refit at v5 speeds). Uses graph51.py. Writes analysis/v51_2026-10-15/04_build/solver51_<stage>_<H>.json,
params/v51_graph_factors.json (fit), runs/v51_2026-10-15/cache51/ (caches).
Usage (repo root, venv):
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/solver51.py build     topology + q (v5.1 fibres) + one-beat timing
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/solver51.py fit       S5 factors (v5.1 speeds, v5.1 fibres)
  python -B analysis/v51_2026-10-15/04_build/solver51.py slab                 acceptance A
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/solver51.py heldout   acceptance B
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/solver51.py s13       S13 refit at v5 speeds (v5 fibres) + F01 copy
  python -B analysis/v51_2026-10-15/04_build/solver51.py calib_element        18 Oct 2026: slab calibration + acceptance A with the
                                                                               element-wise metric (graph51.METRIC_ELEMENT); writes
                                                                               params/v51_graph_factors_element.json
"""
import json
import os
import resource
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import graph51 as g                                                    # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v51_speeds.json')))['hearts']
V5_SPEEDS = {'Y5HYEDL4': {'fibre': 0.60, 'sheet': 0.48, 'normal': 0.48}}
V5_SPEEDS.update({h: {'fibre': 0.60, 'sheet': 0.48 * 0.73, 'normal': 0.48 * 0.70} for h in ('6G8DD8S5', '7D98EVAR')})
FACTORS = os.path.join(REPO, 'params', 'v51_graph_factors.json')
FACTORS_ELEMENT = os.path.join(REPO, 'params', 'v51_graph_factors_element.json')
LIMIT_MS = 90.0                   # Dijkstra stops beyond this (CV measured on elements with mean T 8-80 ms, as a03)


def lon51(h):
    return os.path.join(REPO, 'data', 'biv', h, 'fibres_v51', 'bivF_v51.lon')


def lon5(h):
    return os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'bivF.lon')


def rss_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 0)


def sites(h):
    return json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))


# ------------------------------------------------------------------ CV measurement: copy of a03 (audit F01 script)
def egrad(P, E, u):
    """As analysis/audit_2026-10-13/a03_speeds_activation.py egrad()."""
    x0 = P[E[:, 0]]; J = np.stack([P[E[:, 1]] - x0, P[E[:, 2]] - x0, P[E[:, 3]] - x0], 1)
    du = np.stack([u[E[:, 1]] - u[E[:, 0]], u[E[:, 2]] - u[E[:, 0]], u[E[:, 3]] - u[E[:, 0]]], 1)
    with np.errstate(invalid='ignore'):
        return np.linalg.solve(J, du[..., None])[..., 0]


def cv_samples(P, E, lon, T, tmin=8, tmax=80, cos_thr=0.95, mask=None):
    """As a03 cv_by_dir(), returning the per-direction CV samples (local CV = 1 / |grad T|, direction within acos 0.95 of the
    fibre / sheet / sheet-normal axis); optional element mask (held-out regions)."""
    with np.errstate(invalid='ignore'):
        te = T[E].mean(1)
    ok = np.isfinite(te) & (te > tmin) & (te < tmax)
    if mask is not None:
        ok &= mask
    idx = np.where(ok)[0]
    gr = egrad(P, E[idx], T)
    good = np.isfinite(gr).all(1); gn = np.linalg.norm(gr, axis=1); good &= gn > 1e-6
    idx, gr, gn = idx[good], gr[good], gn[good]
    u = gr / gn[:, None]; cv = 1 / gn
    f = lon[idx, :3]; s = lon[idx, 3:6]
    f = f / np.linalg.norm(f, axis=1)[:, None]; s = s / np.linalg.norm(s, axis=1)[:, None]; n = np.cross(f, s)
    return {nm: cv[np.abs(np.sum(u * ax, 1)) > cos_thr] for nm, ax in (('fibre', f), ('sheet', s), ('normal', n))}


def realised(T_list, P, E, lon, mask_list=None):
    pooled = {a: [] for a in ('fibre', 'sheet', 'normal')}
    per = []
    for k, T in enumerate(T_list):
        smp = cv_samples(P, E, lon, T, mask=None if mask_list is None else mask_list[k])
        per.append({a: (float(np.median(v)) if len(v) else None, int(len(v))) for a, v in smp.items()})
        for a in pooled:
            pooled[a].append(smp[a])
    med = {a: float(np.median(np.concatenate(v))) if sum(len(x) for x in v) else None for a, v in pooled.items()}
    n = {a: int(sum(len(x) for x in v)) for a, v in pooled.items()}
    return med, n, per


def mesh(h):
    B = os.path.join(REPO, 'data', 'biv', h)
    return g.read_pts(os.path.join(B, 'biv.pts')), g.read_elem(os.path.join(B, 'biv.elem'))


# ------------------------------------------------------------------ stages
def build():
    h = os.environ['HEART']
    t0 = time.time()
    tis = g.Tissue(h, lon51(h))
    t1 = time.time()
    S = [s for s in sites(h) if s['family'] == 'lv_free_wall' and s['depth_target'] == 0.5]
    G = tis.graph(SPEEDS[h], {'fibre': 1.0, 'sheet': 1.0, 'normal': 1.0})
    t2 = time.time()
    Tl = g.Tissue.solve(G, int(S[0]['node']), limit=LIMIT_MS); t3 = time.time()
    Tf = g.Tissue.solve(G, int(S[0]['node'])); t4 = time.time()
    out = {'heart': h, 'topology': tis.info, 'keys': tis.keys, 'tissue_load_or_build_s': round(t1 - t0, 1), 'graph_assembly_s': round(t2 - t1, 1),
           'one_beat_limit_90ms_s': round(t3 - t2, 1), 'one_beat_full_s': round(t4 - t3, 1), 'full_beat_total_activation_ms': round(float(Tf.max()), 1),
           'unactivated_nodes': int(np.isinf(Tf).sum()), 'peak_rss_MB': rss_mb(), 'site': S[0]['id']}
    json.dump(out, open(os.path.join(HERE, f'solver51_build_{h}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


def fit_factors(h, lonf, speeds, tol=0.005, max_iter=10, log=print):
    tis = g.Tissue(h, lonf, log)
    P, E = mesh(h)
    lon = g.read_lon(lonf)
    S = [s for s in sites(h) if s['family'] == 'lv_free_wall' and s['depth_target'] == 0.5]
    f = {'fibre': 1.0, 'sheet': 1.0, 'normal': 1.0}
    hist = []
    for it in range(max_iter):
        t0 = time.time()
        G = tis.graph(speeds, f)
        T_list = [g.Tissue.solve(G, int(s['node']), limit=LIMIT_MS) for s in S]
        med, n, per = realised(T_list, P, E, lon)
        ratio = {a: med[a] / speeds[a] for a in f}
        hist.append({'iteration': it, 'factors': dict(f), 'measured_m_s': med, 'n_elements': n, 'ratio_measured_over_target': ratio,
                     'per_site': per, 'iter_s': round(time.time() - t0, 1)})
        log(f'  {h} it {it}: f {f} -> measured {med} ratio {ratio} ({time.time() - t0:.0f} s)')
        if all(abs(r - 1) <= tol for r in ratio.values()):
            break
        f = {a: f[a] / ratio[a] for a in f}
    return tis, f, hist, all(abs(r - 1) <= tol for r in hist[-1]['ratio_measured_over_target'].values())


def fit():
    h = os.environ['HEART']
    t0 = time.time()
    tis, f, hist, ok = fit_factors(h, lon51(h), SPEEDS[h])
    entry = {'heart': h, 'factors': hist[-1]['factors'], 'converged_within_0.5pct': ok, 'speeds_m_s': SPEEDS[h], 'stencil': g.STENCIL_VERSION,
             'fibre_file': os.path.relpath(lon51(h), REPO), 'fibre_sha256': tis.keys['fibre_sha256'], 'topology_key': tis.keys['topology_key'],
             'fit_sites': 'lv_free_wall 50 % depth, single-node stimulus, tissue only', 'measure': 'a03 cv_by_dir (median of pooled elements, T 8-80 ms)',
             'iterations': len(hist), 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    allf = json.load(open(FACTORS)) if os.path.exists(FACTORS) else {'version': 'v51-factors-1', 'hearts': {}}
    allf['hearts'][h] = entry
    json.dump(allf, open(FACTORS, 'w'), indent=1)
    json.dump({'entry': entry, 'history': hist, 'wall_s': round(time.time() - t0, 1), 'peak_rss_MB': rss_mb()},
              open(os.path.join(HERE, f'solver51_fit_{h}.json'), 'w'), indent=1)
    print(json.dumps(entry, indent=1))


def load_factors(h, lonf, metric='nodal'):
    """The solver stops if the factor file is missing or any hash / setting differs."""
    ff = FACTORS if metric == 'nodal' else FACTORS_ELEMENT
    want = g.METRIC_NODAL if metric == 'nodal' else g.METRIC_ELEMENT
    if not os.path.exists(ff):
        raise FileNotFoundError(f'{ff} missing')
    e = json.load(open(ff))['hearts'].get(h)
    if e is None:
        raise KeyError(f'no factors for {h}')
    if e['fibre_sha256'] != g.sha256_file(lonf) or e['stencil'] != g.STENCIL_VERSION or e['speeds_m_s'] != SPEEDS[h] \
            or e.get('metric', g.METRIC_NODAL) != want:
        raise ValueError(f'factors for {h} were fitted for other fibres, stencil, speeds or metric')
    return e['factors']


# ------------------------------------------------------------------ acceptance A: synthetic slab
def slab_mesh(Lx=36.0, Ly=36.0, Lz=20.0, h=0.85, jitter=0.25, seed=0, max_edge=1.75):
    from scipy.spatial import Delaunay
    rng = np.random.default_rng(seed)
    gx, gy, gz = (np.linspace(0.0, L, int(round(L / h)) + 1) for L in (Lx, Ly, Lz))   # exact extents (arange stopped one step short)
    X = np.stack(np.meshgrid(gx, gy, gz, indexing='ij'), -1).reshape(-1, 3)
    inner = (X > 1e-9).all(1) & (X < np.array([Lx, Ly, Lz]) - 1e-9).all(1)
    X[inner] += rng.uniform(-jitter * h, jitter * h, (inner.sum(), 3))
    E = Delaunay(X).simplices.astype(np.int64)
    ed = np.stack([np.linalg.norm(X[E[:, a]] - X[E[:, b]], axis=1) for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))], 1)
    x0 = X[E[:, 0]]
    vol = np.abs(np.einsum('ij,ij->i', X[E[:, 1]] - x0, np.cross(X[E[:, 2]] - x0, X[E[:, 3]] - x0))) / 6
    keep = (ed.max(1) <= max_edge) & (vol > 1e-6)
    E = E[keep]
    used = np.unique(E); remap = np.full(len(X), -1); remap[used] = np.arange(len(used))
    return X[used], remap[E], ed[keep]


def slab_graph(P, E, lon, speeds, factors):
    N = len(P)
    e1, A = g.adjacency(E, N)
    surf = g.surface_nodes(E, N)
    ti, tj, tk, _ = g.e2_triples(P, A)
    first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
    pi, pj = ti[first], tj[first]; pot = np.cumsum(first) - 1
    test = surf[pi] & surf[pj]
    a, Jinv = g.tets_inverse(P, E)
    from scipy.spatial import cKDTree
    ins = g.inside_mesh(0.5 * (P[pi[test]] + P[pj[test]]), P, E, cKDTree(P[E].mean(1)), a, Jinv)
    keep = np.ones(len(pi), bool); keep[np.where(test)[0][~ins]] = False
    Mn = g.nodal_components(P, E, lon)
    w = np.array([1.0 / (factors[x] * speeds[x]) ** 2 for x in ('fibre', 'sheet', 'normal')])
    t1 = np.sqrt(g.quad(P[e1[:, 1]] - P[e1[:, 0]], 0.5 * (Mn[e1[:, 0]] + Mn[e1[:, 1]])) @ w)
    tk_ok = keep[pot]
    ii, jj, kk = ti[tk_ok].astype(np.int64), tj[tk_ok].astype(np.int64), tk[tk_ok].astype(np.int64)
    tt = np.sqrt(g.quad(P[jj] - P[ii], (Mn[ii] + Mn[jj] + Mn[kk]) / 3.0) @ w)
    newpair = (np.cumsum(keep) - 1)[pot[tk_ok]]
    starts = np.r_[0, np.flatnonzero(np.diff(newpair)) + 1]
    t2 = np.minimum.reduceat(tt, starts)
    e = np.r_[e1, np.c_[pi[keep], pj[keep]]].astype(np.int64)
    t = np.r_[t1, t2]
    from scipy.sparse import csr_matrix
    return csr_matrix((np.r_[t, t], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(N, N)), {'E1': int(len(e1)), 'E2': int(keep.sum())}


def slab_test(speeds, factors):
    P, E, ed = slab_mesh()
    c = np.array([18.0, 18.0, 10.0])
    lon = np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1))                     # fibre x, sheet y, normal z
    G, cnt = slab_graph(P, E, lon, speeds, factors)
    src = int(np.argmin(np.linalg.norm(P - c, axis=1)))
    T = g.Tissue.solve(G, src)
    x = P - P[src]; r = np.linalg.norm(x, axis=1)
    v = np.array([speeds['fibre'], speeds['sheet'], speeds['normal']])
    Tex = np.sqrt(np.sum((x / v) ** 2, 1))
    res = {'mesh': {'nodes': int(len(P)), 'tets': int(len(E)), 'edge_mean_mm': round(float(ed.mean()), 3), 'edge_max_mm': round(float(ed.max()), 3)}, 'graph': cnt}
    # principal speeds: nodes within 1 mm of an axis line, 6-14 mm (x, y) or 4-8 mm (z) from the source
    prin = {}
    for ai, nm in enumerate(('fibre', 'sheet', 'normal')):
        others = [k for k in range(3) if k != ai]
        lo, hi = (4.0, 8.0) if ai == 2 else (6.0, 14.0)
        m = (np.linalg.norm(x[:, others], axis=1) < 1.0) & (np.abs(x[:, ai]) >= lo) & (np.abs(x[:, ai]) <= hi)
        sp = np.abs(x[m, ai]) / T[m]
        prin[nm] = {'speed_m_s': round(float(np.median(sp)), 4), 'ratio_to_target': round(float(np.median(sp) / v[ai]), 4), 'nodes': int(m.sum())}
    res['principal'] = prin
    res['principal_pass_1.5pct'] = bool(all(abs(p['ratio_to_target'] - 1) <= 0.015 for p in prin.values()))
    # ray speeds |x| / t vs exact |x| / T in 15 deg bins of each principal plane
    rays, worst = {}, 0.0
    for nm, (a1, a2, a3) in {'fibre-sheet (xy)': (0, 1, 2), 'fibre-normal (xz)': (0, 2, 1), 'sheet-normal (yz)': (1, 2, 0)}.items():
        m = (np.abs(x[:, a3]) < 1.0) & (r >= 4.0) & (r <= 9.0)
        ang = np.degrees(np.arctan2(np.abs(x[m, a2]), np.abs(x[m, a1])))
        ratio = Tex[m] / T[m]
        cell = {}
        for b0 in range(0, 90, 15):
            mm = (ang >= b0) & (ang < b0 + 15)
            if mm.any():
                q = float(np.median(ratio[mm])); cell[f'{b0}-{b0 + 15}'] = round(q, 4); worst = max(worst, abs(q - 1))
        rays[nm] = cell
    res['ray_speed_ratio_graph_over_exact'] = rays
    res['ray_worst_abs_dev'] = round(worst, 4); res['ray_pass_3pct'] = bool(worst <= 0.03)
    # a03-style local CV on the slab (same measure as the heart fit), elements 3-9 mm from the source
    smp = cv_samples(P, E, lon, T, tmin=0, tmax=1e9, mask=(np.linalg.norm(P[E].mean(1) - P[src], axis=1) > 3) & (np.linalg.norm(P[E].mean(1) - P[src], axis=1) < 9))
    res['a03_local_cv_m_s'] = {nm: round(float(np.median(vv)), 4) if len(vv) else None for nm, vv in smp.items()}
    # rotating fibres: +60 to -60 deg across z 0-20 mm (10 mm wall: z 5-15), endocardial face (z = 5) fired
    th = np.radians(60 - 120 * np.clip((P[E].mean(1)[:, 2] - 5.0) / 10.0, 0, 1))
    lon2 = np.c_[np.cos(th), np.sin(th), np.zeros(len(E)), -np.sin(th), np.cos(th), np.zeros(len(E))]
    G2, _ = slab_graph(P, E, lon2, speeds, factors)
    endo = np.where(np.abs(P[:, 2] - 5.0) < 0.5)[0]
    T2 = g.Tissue.solve(G2, endo)
    zf = P[:, 2]
    trans = {}
    for z in (7.5, 10.0, 12.5, 15.0):
        m = (np.abs(zf - z) < 0.4) & (np.abs(P[:, 0] - 18) < 10) & (np.abs(P[:, 1] - 18) < 10)
        pred = (zf[m] - 5.0) / speeds['normal']
        trans[f'z {z - 5:.1f} mm'] = round(float(np.median(T2[m] / pred)), 4)
    res['rotating_fibres_transmural_ratio_graph_over_z_over_vn'] = trans
    res['rotating_pass_2pct'] = bool(all(abs(q - 1) <= 0.02 for q in trans.values()))
    return res


def slab():
    out = {}
    allf = json.load(open(FACTORS))['hearts'] if os.path.exists(FACTORS) else {}
    for h in HEARTS:
        fac = allf.get(h, {}).get('factors')
        conds = {'factors 1 (stencil alone)': {'fibre': 1.0, 'sheet': 1.0, 'normal': 1.0}}
        if fac:
            conds['fitted factors'] = fac
        for cn, f in conds.items():
            t0 = time.time()
            out[f'{h} speeds | {cn}'] = slab_test(SPEEDS[h], f) | {'factors': f, 'wall_s': round(time.time() - t0, 1)}
            print(h, cn, json.dumps({k: v for k, v in out[f'{h} speeds | {cn}'].items() if k in ('principal', 'ray_worst_abs_dev', 'a03_local_cv_m_s', 'rotating_fibres_transmural_ratio_graph_over_z_over_vn')}), flush=True)
    json.dump(out, open(os.path.join(HERE, 'solver51_slab.json'), 'w'), indent=1)


# ------------------------------------------------------------------ option 1 (Alex, 17 Oct 2026 04:06:56 UTC): slab calibration
class SlabGraph:
    """Slab stencil and edge q prepared once (graph51 rules); weights for any speeds and factors. metric 'nodal' or 'element'."""

    def __init__(self, P, E, lon, metric='nodal'):
        from scipy.spatial import cKDTree
        N = len(P)
        e1, A = g.adjacency(E, N)
        surf = g.surface_nodes(E, N)
        ti, tj, tk, _ = g.e2_triples(P, A)
        first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
        pi, pj = ti[first], tj[first]; pot = np.cumsum(first) - 1
        test = surf[pi] & surf[pj]
        a, Jinv = g.tets_inverse(P, E)
        ins = g.inside_mesh(0.5 * (P[pi[test]] + P[pj[test]]), P, E, cKDTree(P[E].mean(1)), a, Jinv)
        keep = np.ones(len(pi), bool); keep[np.where(test)[0][~ins]] = False
        self.metric = metric
        self.e = np.r_[e1, np.c_[pi[keep], pj[keep]]].astype(np.int64)
        self.N = N
        self.counts = {'E1': int(len(e1)), 'E2': int(keep.sum()), 'E2_rejected_midpoint': int((~ins).sum())}
        if metric == 'element':
            self.q1p, self.starts1, self.q2, einfo = g.element_edge_q(P, E, lon, e1, np.c_[pi[keep], pj[keep]])
            self.counts |= einfo
            return
        Mn = g.nodal_components(P, E, lon)
        self.q1 = g.quad(P[e1[:, 1]] - P[e1[:, 0]], 0.5 * (Mn[e1[:, 0]] + Mn[e1[:, 1]]))
        ok = keep[pot]
        ii, jj, kk = ti[ok].astype(np.int64), tj[ok].astype(np.int64), tk[ok].astype(np.int64)
        self.qt = g.quad(P[jj] - P[ii], (Mn[ii] + Mn[jj] + Mn[kk]) / 3.0)
        newpair = (np.cumsum(keep) - 1)[pot[ok]]
        self.starts = np.r_[0, np.flatnonzero(np.diff(newpair)) + 1]

    def graph(self, speeds, factors):
        from scipy.sparse import csr_matrix
        w = np.array([1.0 / (factors[x] * speeds[x]) ** 2 for x in ('fibre', 'sheet', 'normal')])
        if self.metric == 'element':
            t = np.r_[g.element_weights(self.q1p, self.starts1, self.q2, w)]
        else:
            t = np.r_[np.sqrt(self.q1 @ w), np.minimum.reduceat(np.sqrt(self.qt @ w), self.starts)]
        e = self.e
        return csr_matrix((np.r_[t, t], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(self.N, self.N))


AXES = ('fibre', 'sheet', 'normal')


def principal_speeds(P, T, src, speeds):
    """Arrival-time speeds along the three axes (fibre x, sheet y, normal z): nodes within 1 mm of the axis line,
    6-14 mm (x, y) or 4-8 mm (z) from the source; median |x_a| / t."""
    x = P - P[src]
    out = {}
    for ai, nm in enumerate(AXES):
        others = [k for k in range(3) if k != ai]
        lo, hi = (4.0, 8.0) if ai == 2 else (6.0, 14.0)
        m = (np.linalg.norm(x[:, others], axis=1) < 1.0) & (np.abs(x[:, ai]) >= lo) & (np.abs(x[:, ai]) <= hi)
        sp = float(np.median(np.abs(x[m, ai]) / T[m]))
        out[nm] = {'speed_m_s': sp, 'ratio_to_target': sp / speeds[nm], 'nodes': int(m.sum())}
    return out


def calibrate(speeds, seed=0, tol=0.005, max_iter=12, metric='nodal'):
    P, E, ed = slab_mesh(seed=seed)
    lon = np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1))
    SG = SlabGraph(P, E, lon, metric)
    src = int(np.argmin(np.linalg.norm(P - np.array([18.0, 18.0, 10.0]), axis=1)))
    f = {a: 1.0 for a in AXES}
    hist = []
    for it in range(max_iter):
        T = g.Tissue.solve(SG.graph(speeds, f), src)
        pr = principal_speeds(P, T, src, speeds)
        hist.append({'iteration': it, 'factors': dict(f), 'principal': pr})
        if all(abs(pr[a]['ratio_to_target'] - 1) <= tol for a in AXES):
            break
        f = {a: f[a] / pr[a]['ratio_to_target'] for a in AXES}
    conv = all(abs(hist[-1]['principal'][a]['ratio_to_target'] - 1) <= tol for a in AXES)
    return hist[-1]['factors'], conv, hist, {'seed': seed, 'nodes': int(len(P)), 'tets': int(len(E)),
                                              'edge_mean_mm': round(float(ed.mean()), 3), 'edge_max_mm': round(float(ed.max()), 3)} | SG.counts


def acceptance_A(speeds, factors, seed=1, metric='nodal'):
    """Acceptance A on a fresh slab mesh (seed differs from the calibration slab)."""
    P, E, ed = slab_mesh(seed=seed)
    lon = np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1))
    SG = SlabGraph(P, E, lon, metric)
    src = int(np.argmin(np.linalg.norm(P - np.array([18.0, 18.0, 10.0]), axis=1)))
    T = g.Tissue.solve(SG.graph(speeds, factors), src)
    res = {'mesh': {'seed': seed, 'nodes': int(len(P)), 'tets': int(len(E)), 'edge_mean_mm': round(float(ed.mean()), 3),
                    'edge_max_mm': round(float(ed.max()), 3)} | SG.counts}
    pr = principal_speeds(P, T, src, speeds)
    res['principal'] = {a: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()} for a, d in pr.items()}
    res['principal_pass_1.5pct'] = bool(all(abs(pr[a]['ratio_to_target'] - 1) <= 0.015 for a in AXES))
    x = P - P[src]; r = np.linalg.norm(x, axis=1)
    v = np.array([speeds[a] for a in AXES])
    Tex = np.sqrt(np.sum((x / v) ** 2, 1))
    rays, worst = {}, 0.0
    for nm, (a1, a2, a3) in {'fibre-sheet (xy)': (0, 1, 2), 'fibre-normal (xz)': (0, 2, 1), 'sheet-normal (yz)': (1, 2, 0)}.items():
        m = (np.abs(x[:, a3]) < 1.0) & (r >= 4.0) & (r <= 9.0)
        ang = np.degrees(np.arctan2(np.abs(x[m, a2]), np.abs(x[m, a1])))
        ratio = Tex[m] / T[m]                                           # (|x| / t) / (|x| / T) = T / t
        cell = {}
        for b0 in range(0, 90, 15):
            mm = (ang >= b0) & (ang < b0 + 15)
            if mm.any():
                q = float(np.median(ratio[mm])); cell[f'{b0}-{b0 + 15} deg'] = {'ratio': round(q, 4), 'nodes': int(mm.sum())}
                worst = max(worst, abs(q - 1))
        rays[nm] = cell
    res['rays_graph_speed_over_exact'] = rays
    res['rays_worst_abs_dev'] = round(worst, 4); res['rays_pass_3pct'] = bool(worst <= 0.03)
    # rotating fibres: a 36 x 36 x 10 mm wall, fibres +60 deg (z = 0) to -60 deg (z = 10) about z, endocardial face z = 0 fired
    Pw, Ew, _ = slab_mesh(Lz=10.0, seed=seed)
    zc = Pw[Ew].mean(1)[:, 2]
    th = np.radians(60.0 - 120.0 * np.clip(zc / 10.0, 0, 1))
    lonw = np.c_[np.cos(th), np.sin(th), np.zeros(len(Ew)), -np.sin(th), np.cos(th), np.zeros(len(Ew))]
    SW = SlabGraph(Pw, Ew, lonw, metric)
    endo = np.where(Pw[:, 2] <= 1e-9)[0]
    T2 = g.Tissue.solve(SW.graph(speeds, factors), endo)
    trans = {}
    for z in (2.5, 5.0, 7.5, 10.0):
        m = (np.abs(Pw[:, 2] - z) < 0.4) & (np.abs(Pw[:, 0] - 18) < 10) & (np.abs(Pw[:, 1] - 18) < 10)
        trans[f'z {z:.1f} mm'] = {'ratio': round(float(np.median(T2[m] * speeds['normal'] / Pw[m, 2])), 4), 'nodes': int(m.sum())}
    res['rotating_wall_transmural_arrival_over_z_over_vn'] = trans
    res['rotating_pass_2pct'] = bool(all(abs(c['ratio'] - 1) <= 0.02 for c in trans.values()))
    res['pass'] = bool(res['principal_pass_1.5pct'] and res['rays_pass_3pct'] and res['rotating_pass_2pct'])
    return res


def calib():
    out = {'method': 'factors calibrated on a synthetic slab (Alex 17 Oct 2026 04:06:56 UTC, option 1): 36 x 36 x 20 mm, jittered grid '
                     '(h 0.85 mm, jitter 0.25 h, seed 0), Delaunay, tets with an edge > 1.75 mm dropped; uniform fibres (x), sheet (y), normal (z); '
                     'point source at the centre; along-axis arrival speeds; f_a <- f_a target_a / measured_a until all within 0.5 %. '
                     'Acceptance A on a fresh mesh (seed 1) and a fresh 10 mm rotating-fibre wall (seed 1).', 'hearts': {}}
    done = {}
    for h in HEARTS:
        key = json.dumps(SPEEDS[h], sort_keys=True)
        t0 = time.time()
        if key not in done:
            f, conv, hist, mesh_info = calibrate(SPEEDS[h])
            acc = acceptance_A(SPEEDS[h], f)
            done[key] = (f, conv, hist, mesh_info, acc)
        f, conv, hist, mesh_info, acc = done[key]
        out['hearts'][h] = {'speeds_m_s': SPEEDS[h], 'factors': f, 'converged_within_0.5pct': conv, 'iterations': len(hist),
                            'calibration_slab': mesh_info, 'calibration_history': hist, 'acceptance_A_fresh_mesh': acc, 'wall_s': round(time.time() - t0, 1)}
        print(h, 'factors', {a: round(v, 4) for a, v in f.items()}, 'converged', conv, 'iterations', len(hist),
              '| A: principal', {a: acc['principal'][a]['ratio_to_target'] for a in AXES}, 'rays worst', acc['rays_worst_abs_dev'],
              'rotating', {k: c['ratio'] for k, c in acc['rotating_wall_transmural_arrival_over_z_over_vn'].items()}, 'PASS' if acc['pass'] else 'FAIL', flush=True)
    json.dump(out, open(os.path.join(HERE, 'solver51_slab_calibration.json'), 'w'), indent=1)


def calib_element():
    """18 Oct 2026 (Alex's decision of 17 Oct 07:58 UTC: test element-wise tensors, recalibrate on the slab, rerun
    acceptance A): the calib() procedure with graph51.METRIC_ELEMENT; writes the factors to FACTORS_ELEMENT."""
    t_all = time.time()
    out = {'method': 'as solver51_slab_calibration.json, with the element-wise metric ' + g.METRIC_ELEMENT +
                     ' (graph51.py docstring): element tensors, E1 min over the tets sharing the edge, E2 sum over three thirds',
           'hearts': {}}
    done = {}
    for h in HEARTS:
        key = json.dumps(SPEEDS[h], sort_keys=True)
        t0 = time.time()
        if key not in done:
            f, conv, hist, mesh_info = calibrate(SPEEDS[h], metric='element')
            acc = acceptance_A(SPEEDS[h], f, metric='element')
            done[key] = (f, conv, hist, mesh_info, acc)
        f, conv, hist, mesh_info, acc = done[key]
        out['hearts'][h] = {'speeds_m_s': SPEEDS[h], 'factors': f, 'converged_within_0.5pct': conv, 'iterations': len(hist),
                            'calibration_slab': mesh_info, 'calibration_history': hist, 'acceptance_A_fresh_mesh': acc, 'wall_s': round(time.time() - t0, 1)}
        print(h, 'factors', {a: round(v, 4) for a, v in f.items()}, 'converged', conv, 'iterations', len(hist),
              '| A: principal', {a: acc['principal'][a]['ratio_to_target'] for a in AXES}, 'rays worst', acc['rays_worst_abs_dev'],
              'rotating', {k: c['ratio'] for k, c in acc['rotating_wall_transmural_arrival_over_z_over_vn'].items()}, 'PASS' if acc['pass'] else 'FAIL', flush=True)
    out['wall_s'] = round(time.time() - t_all, 1); out['peak_rss_MB'] = rss_mb()
    json.dump(out, open(os.path.join(HERE, 'solver51_slab_calibration_element.json'), 'w'), indent=1)
    fac = {'version': 'v51-factors-3 (element-wise metric, slab calibration)', 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
           'decision': "Alex 17 Oct 2026 07:58 UTC ('Adopt all': test element-wise tensors first, recalibrate on the slab, rerun acceptance A); "
                       "go 18 Oct 2026 12:03:13 UTC", 'method': out['method'], 'hearts': {}}
    for h in HEARTS:
        r = out['hearts'][h]
        fac['hearts'][h] = {'factors': r['factors'], 'speeds_m_s': SPEEDS[h], 'stencil': g.STENCIL_VERSION, 'metric': g.METRIC_ELEMENT,
                            'fibre_file': os.path.relpath(lon51(h), REPO), 'fibre_sha256': g.sha256_file(lon51(h)),
                            'calibration_converged_within_0.5pct': r['converged_within_0.5pct'], 'calibration_iterations': r['iterations'],
                            'acceptance_A_pass': r['acceptance_A_fresh_mesh']['pass']}
    json.dump(fac, open(FACTORS_ELEMENT, 'w'), indent=1)


# ------------------------------------------------------------------ S13 (report): v5 speeds and fibres with the v5.1 stencil
def s13():
    """Slab-calibrated factors at the v5 speeds, the v5.1 2-ring solver on the v5 fibres, then the F01 measurement as the
    audit's a03 (1.5 mm ball at lv_free_wall_phi180_z0.5_d50, tissue only, cv_by_dir T 8-80 ms) beside the audit's v5 values."""
    f01 = json.load(open(os.path.join(HERE, 'f01_copy_v5.json')))['speeds']
    out, cal = {}, {}
    for h in HEARTS:
        sp = V5_SPEEDS[h]; key = json.dumps(sp, sort_keys=True)
        if key not in cal:
            f, conv, hist, info = calibrate(sp)
            cal[key] = (f, conv, len(hist))
        f, conv, nit = cal[key]
        tis = g.Tissue(h, lon5(h))
        P, E = mesh(h)
        lon = g.read_lon(lon5(h))
        node = int([s for s in sites(h) if s['id'] == 'lv_free_wall_phi180_z0.5_d50'][0]['node'])
        ball = np.where(np.linalg.norm(P - P[node], axis=1) < 1.5)[0]
        res = {'v5_speeds_m_s': sp, 'slab_factors_at_v5_speeds': f, 'slab_converged': conv, 'slab_iterations': nit}
        for lab, fac in (('v5.1 stencil, factors 1', {a: 1.0 for a in AXES}), ('v5.1 stencil, slab factors', f)):
            T = g.Tissue.solve(tis.graph(sp, fac), ball)
            smp = cv_samples(P, E, lon, T)
            res[lab] = {a: round(float(np.median(smp[a])), 3) for a in AXES}
        v5 = f01[f'{h}_v5_graph_nonet_lvfw_phi180_z0.5_d50']
        res['v5 solver (audit F01, k)'] = {a: v5[a]['median_m_s'] for a in AXES}
        out[h] = res
        print(h, json.dumps(res), flush=True)
    json.dump(out, open(os.path.join(HERE, 'solver51_s13.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'build': build, 'fit': fit, 'slab': slab, 'calib': calib, 'calib_element': calib_element, 's13': s13}[sys.argv[1]]()
