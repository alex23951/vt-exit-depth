"""v5.2 in-heart graph tissue (step 3; R4.1-R4.2): graph51's nodal graph eikonal on the cut simulation mesh.

Mesh: data/biv/<H>/v52/biv52cut (8.2's cut; v5.1 node ids first, RV copies of split nodes appended).
Stencil per heart (params/v52_graph_factors.json, acceptance A on the slab):
  2-ring (graph51 S2, 'v51-2ring-1'): tet edges E1; node pairs at graph distance exactly 2 up to 3.5 mm (E2).
  3-ring (R4.2, 'v52-3ring-1', as slab52.SlabGraph3): E1; graph distance exactly 2 up to 5.25 mm (E2); graph distance
    exactly 3 up to 5.25 mm (E3).
  Surface-surface pairs are kept only if their midpoint lies in a tet (S2). Pairs that jump 8.2's cut
  (runs/v52_2026-10-20/02_geometry/<H>/cut52_edges_removed.npz, found by cut52.py's segment-triangle and side tests; the
  2-ring list where in_2ring, all of it for the 3-ring) are removed.
Metric (S3, nodal): M = sum over f, s, n = f x s of the fibre file of (factor x speed)^-2 a a^T, nodal volume-weighted
  means; E1 the mean of M at i, j; E2 the minimum over middle nodes k of the mean at i, j, k; E3 the mean at i, j and the
  node nearest the chord midpoint (slab52's rule). The fibre file is data/biv/<H>/v52/biv52cut.lon (step 2a).
Caches: runs/v52_2026-10-20/cache52/ (topology keyed by mesh sha256, stencil and removed-edge sha256; q keyed by topology
and fibre sha256). Speeds and factors are applied at load, never cached.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/03_speeds/graph52.py probe|build [HEART ...]
"""
import hashlib
import importlib.util
import json
import os
import resource
import sys
import time

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
spec = importlib.util.spec_from_file_location('graph51', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', 'graph51.py'))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
CACHE = os.path.join(REPO, 'runs', 'v52_2026-10-20', 'cache52')
FACTORS = json.load(open(os.path.join(REPO, 'params', 'v52_graph_factors.json')))['hearts']
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts']
RING = {h: (3 if FACTORS[h]['stencil'].startswith('v52-3ring') else 2) for h in HEARTS}
MAX_MM = {2: 3.5, 3: 5.25}


def rss_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 0)


def mesh(h):
    V = os.path.join(REPO, 'data', 'biv', h, 'v52')
    return os.path.join(V, 'biv52cut.pts'), os.path.join(V, 'biv52cut.elem'), os.path.join(V, 'biv52cut.lon')


def e3_pairs(pts, A, block=4000, rows_max=None, maxmm=5.25):
    """(i, j) with i < j at graph distance exactly 3 and |x_i - x_j| <= maxmm, by row blocks."""
    N = A.shape[0]; Ai = A.astype(np.int32)
    oi, oj = [], []
    for b0 in range(0, N if rows_max is None else rows_max, block):
        rows = np.arange(b0, min(N if rows_max is None else rows_max, b0 + block))
        R1 = Ai[rows]
        R2 = (R1 @ Ai); R2.data[:] = 1
        R3 = (R2 @ Ai).tocoo()
        r3, c3 = R3.row.astype(np.int64), R3.col.astype(np.int64)
        R12 = (R1 + R2).tocoo()
        near = np.unique(np.r_[R12.row.astype(np.int64) * N + R12.col, (rows - b0).astype(np.int64) * N + rows])
        key = r3 * N + c3
        far = ~np.isin(key, near)
        r3, c3 = r3[far] + b0, c3[far]
        m = c3 > r3
        r3, c3 = r3[m], c3[m]
        d = np.linalg.norm(pts[c3] - pts[r3], axis=1)
        k = d <= maxmm
        oi.append(r3[k].astype(np.int32)); oj.append(c3[k].astype(np.int32))
    return np.concatenate(oi), np.concatenate(oj)


def topology(h, log=print):
    pf, ef, _ = mesh(h)
    ring = RING[h]
    remf = os.path.join(REPO, 'runs', 'v52_2026-10-20', '02_geometry', h, 'cut52_edges_removed.npz')
    inp = {'heart': h, 'pts_sha256': g.sha256_file(pf), 'elem_sha256': g.sha256_file(ef), 'stencil': FACTORS[h]['stencil'], 'ring': ring,
           'max_mm': MAX_MM[ring], 'midpoint_knn': g.MID_KNN, 'removed_sha256': g.sha256_file(remf)}
    key = hashlib.sha256(json.dumps(inp, sort_keys=True).encode()).hexdigest()
    f = os.path.join(CACHE, f'topo52_{h}_{key[:16]}.npz')
    if os.path.exists(f):
        d = np.load(f)
        assert str(d['key']) == key
        return {k: d[k] for k in d.files if k not in ('key', 'info', 'inputs')}, json.loads(str(d['info'])), key
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    pts, E = g.read_pts(pf), g.read_elem(ef)
    N = len(pts)
    e1, A = g.adjacency(E, N)
    surf = g.surface_nodes(E, N)
    old = g.MAX_E2_MM; g.MAX_E2_MM = MAX_MM[ring]
    try:
        ti, tj, tk, n_dist = g.e2_triples(pts, A, log=log)
    finally:
        g.MAX_E2_MM = old
    first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
    pi, pj = ti[first].astype(np.int64), tj[first].astype(np.int64); pot = np.cumsum(first) - 1
    log(f'{h}: E1 {len(e1)}, E2 pairs {len(pi)} ({time.time() - t0:.0f} s, RSS {rss_mb()} MB)')
    a, Jinv = g.tets_inverse(pts, E)
    tree = cKDTree(pts[E].mean(1))

    def inside_ok(ii, jj):
        test = surf[ii] & surf[jj]
        ok = np.ones(len(ii), bool)
        if test.any():
            ok[np.where(test)[0]] = g.inside_mesh(0.5 * (pts[ii[test]] + pts[jj[test]]), pts, E, tree, a, Jinv)
        return ok, int(test.sum())
    k2, t2 = inside_ok(pi, pj)
    rem = np.load(remf)
    rem_keys = set((np.minimum(rem['i'], rem['j']) * N + np.maximum(rem['i'], rem['j']))[rem['in_2ring'] | (ring == 3)].tolist())
    k2 &= ~np.isin(pi * N + pj, np.fromiter(rem_keys, np.int64, len(rem_keys)))
    info = {'nodes': int(N), 'elements': int(len(E)), 'ring': ring, 'E1': int(len(e1)), 'E2_pairs_candidates': int(len(pi)),
            'E2_surface_pairs_tested': t2, 'E2_kept': int(k2.sum())}
    out = {'e1': e1.astype(np.int32)}
    newidx = np.cumsum(k2) - 1
    tri_keep = k2[pot]
    out['e2'] = np.c_[pi[k2], pj[k2]].astype(np.int32)
    out['tri_pair'] = newidx[pot[tri_keep]].astype(np.int32); out['tri_k'] = tk[tri_keep].astype(np.int32)
    del ti, tj, tk, first, pot
    if ring == 3:
        i3, j3 = e3_pairs(pts, A, maxmm=MAX_MM[3])
        i3, j3 = i3.astype(np.int64), j3.astype(np.int64)
        log(f'{h}: E3 pairs {len(i3)} ({time.time() - t0:.0f} s, RSS {rss_mb()} MB)')
        k3, t3 = inside_ok(i3, j3)
        k3 &= ~np.isin(i3 * N + j3, np.fromiter(rem_keys, np.int64, len(rem_keys)))
        ik, jk = i3[k3], j3[k3]; tp_ = cKDTree(pts); mid = np.empty(len(ik), np.int64)
        for c0 in range(0, len(ik), 2_000_000):
            mid[c0:c0 + 2_000_000] = tp_.query(0.5 * (pts[ik[c0:c0 + 2_000_000]] + pts[jk[c0:c0 + 2_000_000]]))[1]
        out['e3'] = np.c_[i3[k3], j3[k3]].astype(np.int32); out['e3_mid'] = mid.astype(np.int32)
        info.update({'E3_pairs_candidates': int(len(i3)), 'E3_surface_pairs_tested': t3, 'E3_kept': int(k3.sum())})
    info['removed_pairs_in_list'] = len(rem_keys)
    info['edges_per_node'] = round(2 * (len(e1) + len(out['e2']) + (len(out['e3']) if ring == 3 else 0)) / N, 2)
    info['build_s'] = round(time.time() - t0, 1); info['peak_rss_MB'] = rss_mb()
    np.savez(f, key=key, info=json.dumps(info), inputs=json.dumps(inp), **out)
    json.dump(inp | {'key': key, 'info': info}, open(f[:-4] + '.json', 'w'), indent=1)
    log(f'topology52 {h}: {info}')
    return out, info, key


def edge_q(h, log=print):
    topo, info, tkey = topology(h, log)
    pf, ef, lf = mesh(h)
    fsha = g.sha256_file(lf)
    key = hashlib.sha256(json.dumps({'topology': tkey, 'fibre_sha256': fsha, 'metric': 'nodal-1; E3 chord-midpoint node'}).encode()).hexdigest()
    f = os.path.join(CACHE, f'q52_{h}_{key[:16]}.npz')
    if os.path.exists(f):
        d = np.load(f)
        assert str(d['key']) == key
        return topo, info, {k: d[k] for k in d.files if k != 'key'}, {'topology_key': tkey, 'fibre_sha256': fsha, 'q_key': key}
    t0 = time.time()
    pts, E = g.read_pts(pf), g.read_elem(ef)
    Mn = g.nodal_components(pts, E, g.read_lon(lf))
    e1 = topo['e1'].astype(np.int64)
    q = {'q1': g.quad(pts[e1[:, 1]] - pts[e1[:, 0]], 0.5 * (Mn[e1[:, 0]] + Mn[e1[:, 1]])).astype(np.float32)}
    e2 = topo['e2'].astype(np.int64); tp = topo['tri_pair'].astype(np.int64); tk = topo['tri_k'].astype(np.int64)
    qt = np.empty((len(tp), 3), np.float32)
    for c0 in range(0, len(tp), 2_000_000):
        sl = slice(c0, c0 + 2_000_000)
        i, j, k = e2[tp[sl], 0], e2[tp[sl], 1], tk[sl]
        qt[sl] = g.quad(pts[j] - pts[i], (Mn[i] + Mn[j] + Mn[k]) / 3.0)
    q['qt'] = qt
    if 'e3' in topo:
        e3 = topo['e3'].astype(np.int64); m3 = topo['e3_mid'].astype(np.int64)
        q3 = np.empty((len(e3), 3), np.float32)
        for c0 in range(0, len(e3), 2_000_000):
            sl = slice(c0, c0 + 2_000_000)
            i, j, k = e3[sl, 0], e3[sl, 1], m3[sl]
            q3[sl] = g.quad(pts[j] - pts[i], (Mn[i] + Mn[j] + Mn[k]) / 3.0)
        q['q3'] = q3
    np.savez(f, key=key, **q)
    log(f'edge q52 {h}: {time.time() - t0:.0f} s')
    return topo, info, q, {'topology_key': tkey, 'fibre_sha256': fsha, 'q_key': key}


class Tissue52:
    """In-heart tissue graph of one v5.2 heart; weights for given speeds and factors (default: the heart's own)."""

    def __init__(self, h, log=print):
        self.h = h
        self.topo, self.info, self.q, self.keys = edge_q(h, log)
        tp = self.topo['tri_pair']
        self.starts = np.r_[0, np.flatnonzero(np.diff(tp)) + 1]
        assert len(self.starts) == len(self.topo['e2'])
        self.N = self.info['nodes']

    def weights(self, speeds=None, factors=None):
        speeds = speeds or SPEEDS[self.h]; factors = factors or FACTORS[self.h]['factors']
        w = np.array([1.0 / (factors[a] * speeds[a]) ** 2 for a in ('fibre', 'sheet', 'normal')])
        t1 = np.sqrt(self.q['q1'].astype(np.float64) @ w)
        t2 = np.minimum.reduceat(np.sqrt(self.q['qt'].astype(np.float64) @ w), self.starts)
        e = [self.topo['e1'], self.topo['e2']]; t = [t1, t2]
        if 'q3' in self.q:
            e.append(self.topo['e3']); t.append(np.sqrt(self.q['q3'].astype(np.float64) @ w))
        return np.concatenate(e).astype(np.int64), np.concatenate(t)

    def graph(self, speeds=None, factors=None):
        e, t = self.weights(speeds, factors)
        return csr_matrix((np.r_[t, t], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(self.N, self.N))

    @staticmethod
    def solve(G, sources, limit=np.inf):
        return dijkstra(G, directed=True, indices=np.atleast_1d(sources), limit=limit, min_only=True)


def probe(h, frac=0.05):
    pf, ef, _ = mesh(h)
    t0 = time.time()
    pts, E = g.read_pts(pf), g.read_elem(ef)
    N = len(pts); e1, A = g.adjacency(E, N)
    rows = int(frac * N)
    old = g.MAX_E2_MM; g.MAX_E2_MM = MAX_MM[RING[h]]
    try:
        ti, tj, tk, _ = g.e2_triples(pts, A, rows_max=rows)
    finally:
        g.MAX_E2_MM = old
    first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
    t1 = time.time()
    r = {'heart': h, 'ring': RING[h], 'nodes': N, 'frac_rows': frac, 'E1': int(len(e1)), 'E2_triples': int(len(ti)), 'E2_pairs': int(first.sum()), 'e2_s': round(t1 - t0, 1)}
    if RING[h] == 3:
        i3, _ = e3_pairs(pts, A, rows_max=rows)
        r.update({'E3_pairs': int(len(i3)), 'e3_s': round(time.time() - t1, 1)})
    r['peak_rss_MB'] = rss_mb()
    r['extrapolated_full'] = {k: int(v / frac) for k, v in r.items() if k in ('E2_triples', 'E2_pairs', 'E3_pairs')}
    print(json.dumps(r), flush=True)


if __name__ == '__main__':
    stage = sys.argv[1]
    for h in sys.argv[2:] or HEARTS:
        if stage == 'probe':
            probe(h)
        elif stage == 'build':
            T = Tissue52(h)
            print(h, json.dumps(T.info), flush=True)
