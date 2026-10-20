"""v5.2 step 3, synthetic-slab part (LOCK.md 5.3 R4.1, R4.2; allowed before step 2 ends by clarification C7, 20 Oct 2026).

R4.1: the graph eikonal factors refitted on v5.1's synthetic slab (option 1: solver51.py calibrate(), 36 x 36 x 20 mm
jittered grid, seed 0, nodal metric S3, 2-ring stencil) at the v5.2 speeds (params/v52_speeds.json), then acceptance A
on a fresh slab (seed 1) with v5.1's tolerances: principal +-1.5 %, rays +-3 %, rotating wall +-2 %, the rotating wall
using the v5.2 LV profile (+66 deg at the fired face to -41 deg at 10 mm, linear: R5.1's alpha(w) = 66 - 107 w).
Everything except the speeds and the wall profile is solver51.py's code, called unchanged.
R4.2: if A fails with the 2-ring stencil, the 3-ring stencil is used and A retested; if that fails too, stop and report.
Outputs: slab52.json here; params/v52_graph_factors.json (written only if A passes).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/03_speeds/slab52.py
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
B51 = os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build')
sys.path.insert(0, B51)
spec = importlib.util.spec_from_file_location('solver51', os.path.join(B51, 'solver51.py'))
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
g = S.g
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts']
LOCK_SHA = '08ea65d3cda1adac9dcb1935a9000f32bbe093fc65e1e2e52ed8556373a1980b'
A0, A1 = 66.0, -41.0


def acceptance_A52(speeds, factors, seed=1):
    """solver51.acceptance_A with the rotating wall's profile set to the v5.2 LV helix (+66 -> -41 deg over 10 mm)."""
    res = S.acceptance_A(speeds, factors, seed=seed)           # principal and rays as v5.1 (its rotating wall is +60 -> -60)
    res['rotating_wall_v51_profile_(report)'] = res.pop('rotating_wall_transmural_arrival_over_z_over_vn')
    res.pop('rotating_pass_2pct')
    Pw, Ew, _ = S.slab_mesh(Lz=10.0, seed=seed)
    zc = Pw[Ew].mean(1)[:, 2]
    th = np.radians(A0 + (A1 - A0) * np.clip(zc / 10.0, 0, 1))
    lonw = np.c_[np.cos(th), np.sin(th), np.zeros(len(Ew)), -np.sin(th), np.cos(th), np.zeros(len(Ew))]
    SW = S.SlabGraph(Pw, Ew, lonw, 'nodal')
    endo = np.where(Pw[:, 2] <= 1e-9)[0]
    T2 = g.Tissue.solve(SW.graph(speeds, factors), endo)
    trans = {}
    for z in (2.5, 5.0, 7.5, 10.0):
        m = (np.abs(Pw[:, 2] - z) < 0.4) & (np.abs(Pw[:, 0] - 18) < 10) & (np.abs(Pw[:, 1] - 18) < 10)
        trans[f'z {z:.1f} mm'] = {'ratio': round(float(np.median(T2[m] * speeds['normal'] / Pw[m, 2])), 4), 'nodes': int(m.sum())}
    res['rotating_wall_v52_profile'] = {'profile_deg': [A0, A1], 'transmural_arrival_over_z_over_vn': trans}
    res['rotating_pass_2pct'] = bool(all(abs(c['ratio'] - 1) <= 0.02 for c in trans.values()))
    res['pass'] = bool(res['principal_pass_1.5pct'] and res['rays_pass_3pct'] and res['rotating_pass_2pct'])
    return res


class SlabGraph3:
    """R4.2 3-ring stencil on the slab: tet edges (E1), node pairs at graph distance 2 or 3 up to 5.25 mm (E2, E3), the
    S2 midpoint-inside test for surface-surface pairs. Metric (nodal, S3): E1 the mean of the two nodal M; E2 the minimum
    over middle nodes k of the mean of M at i, j, k (S3 as written); E3 (S3 says nothing; mine) the mean of M at i, j and
    the node nearest the chord midpoint."""

    def __init__(self, P, E, lon, metric='nodal'):
        from scipy.sparse import triu
        from scipy.spatial import cKDTree
        N = len(P)
        e1, A = g.adjacency(E, N)
        surf = g.surface_nodes(E, N)
        Mn = g.nodal_components(P, E, lon)
        self.q1 = g.quad(P[e1[:, 1]] - P[e1[:, 0]], 0.5 * (Mn[e1[:, 0]] + Mn[e1[:, 1]]))
        old = g.MAX_E2_MM; g.MAX_E2_MM = 5.25
        try:
            ti, tj, tk, _ = g.e2_triples(P, A)
        finally:
            g.MAX_E2_MM = old
        first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
        pi, pj = ti[first].astype(np.int64), tj[first].astype(np.int64); pot = np.cumsum(first) - 1
        Ai = A.astype(np.int32)
        A3 = triu(((Ai @ Ai).astype(bool).astype(np.int32) @ Ai).astype(bool), k=1).tocoo()
        i3, j3 = A3.row.astype(np.int64), A3.col.astype(np.int64)
        A2 = (Ai @ Ai).astype(bool)
        not12 = ~np.asarray(A[i3, j3]).ravel().astype(bool) & ~np.asarray(A2[i3, j3]).ravel().astype(bool)
        i3, j3 = i3[not12], j3[not12]
        L3 = np.linalg.norm(P[j3] - P[i3], axis=1); k3 = L3 <= 5.25
        i3, j3 = i3[k3], j3[k3]
        a, Jinv = g.tets_inverse(P, E); tree = cKDTree(P[E].mean(1))
        def inside_ok(ii, jj):
            test = surf[ii] & surf[jj]
            ok = np.ones(len(ii), bool)
            if test.any():
                ok[np.where(test)[0]] = g.inside_mesh(0.5 * (P[ii[test]] + P[jj[test]]), P, E, tree, a, Jinv)
            return ok
        k2 = inside_ok(pi, pj); k3 = inside_ok(i3, j3)
        ok = k2[pot]
        ii, jj, kk = ti[ok].astype(np.int64), tj[ok].astype(np.int64), tk[ok].astype(np.int64)
        self.qt = g.quad(P[jj] - P[ii], (Mn[ii] + Mn[jj] + Mn[kk]) / 3.0)
        newpair = (np.cumsum(k2) - 1)[pot[ok]]
        self.starts = np.r_[0, np.flatnonzero(np.diff(newpair)) + 1]
        i3, j3 = i3[k3], j3[k3]
        c = cKDTree(P).query(0.5 * (P[i3] + P[j3]))[1]
        self.q3 = g.quad(P[j3] - P[i3], (Mn[i3] + Mn[j3] + Mn[c]) / 3.0)
        self.e = np.r_[e1, np.c_[pi[k2], pj[k2]], np.c_[i3, j3]].astype(np.int64)
        self.N = N
        self.counts = {'E1': int(len(e1)), 'E2_le_5.25mm': int(k2.sum()), 'E3_le_5.25mm': int(len(i3)),
                       'E2_rejected_midpoint': int((~k2).sum()), 'E3_rejected_midpoint': int((~k3).sum())}

    def graph(self, speeds, factors):
        from scipy.sparse import csr_matrix
        w = np.array([1.0 / (factors[x] * speeds[x]) ** 2 for x in ('fibre', 'sheet', 'normal')])
        t = np.r_[np.sqrt(self.q1 @ w), np.minimum.reduceat(np.sqrt(self.qt @ w), self.starts), np.sqrt(self.q3 @ w)]
        e = self.e
        return csr_matrix((np.r_[t, t], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(self.N, self.N))


def fallback_3ring(sp):
    """R4.2: refit and acceptance A with the 3-ring stencil (solver51's calibrate / acceptance code with SlabGraph3)."""
    orig = S.SlabGraph
    S.SlabGraph = SlabGraph3
    try:
        f, conv, hist, mesh_info = S.calibrate(sp)
        acc = acceptance_A52(sp, f)
    finally:
        S.SlabGraph = orig
    return f, conv, hist, mesh_info, acc


def main():
    t0 = time.time()
    out = {'lock_sha256': LOCK_SHA, 'speeds_file': 'params/v52_speeds.json',
           'speeds_sha256': hashlib.sha256(open(os.path.join(REPO, 'params', 'v52_speeds.json'), 'rb').read()).hexdigest(),
           'stencil': g.STENCIL_VERSION, 'metric': 'nodal (S3, v5.1)', 'sets': {}}
    done = {}
    for h, sp in SPEEDS.items():
        key = json.dumps(sp, sort_keys=True)
        if key not in done:
            t1 = time.time()
            f, conv, hist, mesh_info = S.calibrate(sp)
            acc = acceptance_A52(sp, f)
            done[key] = {'speeds_m_s': sp, 'factors': f, 'converged_within_0.5pct': conv, 'iterations': len(hist), 'calibration_slab': mesh_info,
                         'calibration_history': hist, 'acceptance_A_fresh_mesh': acc, 'wall_s': round(time.time() - t1, 1)}
            print(key, 'factors', {a: round(v, 4) for a, v in f.items()}, 'conv', conv, '| A principal',
                  {a: acc['principal'][a]['ratio_to_target'] for a in S.AXES}, 'rays worst', acc['rays_worst_abs_dev'],
                  'rotating', {k: c['ratio'] for k, c in acc['rotating_wall_v52_profile']['transmural_arrival_over_z_over_vn'].items()},
                  'PASS' if acc['pass'] else 'FAIL', flush=True)
        out['sets'].setdefault(key, done[key])
        out['sets'][key].setdefault('hearts', []).append(h)
    out['all_pass_2ring'] = bool(all(v['acceptance_A_fresh_mesh']['pass'] for v in out['sets'].values()))
    out['R4.2_fallback_needed'] = not out['all_pass_2ring']
    for key, v in out['sets'].items():
        if v['acceptance_A_fresh_mesh']['pass']:
            v['stencil_used'] = '2-ring'
            continue
        t1 = time.time()
        f, conv, hist, mesh_info, acc = fallback_3ring(v['speeds_m_s'])
        v['R4.2_3ring'] = {'factors': f, 'converged_within_0.5pct': conv, 'iterations': len(hist), 'calibration_slab': mesh_info,
                           'calibration_history': hist, 'acceptance_A_fresh_mesh': acc, 'wall_s': round(time.time() - t1, 1)}
        v['stencil_used'] = '3-ring' if acc['pass'] else 'none: R4.2 fails too (stop and report)'
        print(key, '3-ring factors', {a: round(x, 4) for a, x in f.items()}, 'conv', conv, '| A principal',
              {a: acc['principal'][a]['ratio_to_target'] for a in S.AXES}, 'rays worst', acc['rays_worst_abs_dev'],
              'rotating', {k: c['ratio'] for k, c in acc['rotating_wall_v52_profile']['transmural_arrival_over_z_over_vn'].items()},
              'PASS' if acc['pass'] else 'FAIL', flush=True)
    out['all_pass'] = bool(all(v['stencil_used'] in ('2-ring', '3-ring') for v in out['sets'].values()))
    out['wall_s'] = round(time.time() - t0, 1); out['peak_rss_MB'] = S.rss_mb()
    json.dump(out, open(os.path.join(HERE, 'slab52.json'), 'w'), indent=1)
    if out['all_pass']:
        def entry(sp):
            v = out['sets'][json.dumps(sp, sort_keys=True)]
            three = v['stencil_used'] == '3-ring'
            return {'factors': v['R4.2_3ring']['factors'] if three else v['factors'], 'speeds_m_s': sp,
                    'stencil': 'v52-3ring-1 (R4.2: graph distance <= 3, edges <= 5.25 mm)' if three else g.STENCIL_VERSION,
                    'metric': g.METRIC_NODAL, 'acceptance_A_pass': True}
        fac = {'version': 'v52-factors-1 (slab calibration, nodal metric; 3-ring where R4.2 applied)', 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
               'method': 'solver51.calibrate() at the v5.2 speeds; acceptance A (solver51.acceptance_A, rotating wall at the v5.2 LV profile); R4.2 3-ring where the 2-ring failed',
               'hearts': {h: entry(sp) for h, sp in SPEEDS.items()}}
        json.dump(fac, open(os.path.join(REPO, 'params', 'v52_graph_factors.json'), 'w'), indent=1)
    out['wall_s'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, 'slab52.json'), 'w'), indent=1)
    print('all pass:', out['all_pass'], {k: v['stencil_used'] for k, v in out['sets'].items()}, out['wall_s'], 's', flush=True)


if __name__ == '__main__':
    main()
