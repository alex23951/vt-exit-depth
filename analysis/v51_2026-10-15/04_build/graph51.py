"""v5.1 myocardial graph solver (v5.1 brief Step 4.3, decision C; audit F01). Replaces v5's single graph scale k.

S2 stencil: E1 = unique tet edges; E2 = node pairs at graph distance exactly 2 ((A @ A)_ij > 0 and A_ij = 0, from the
   boolean adjacency, no numeric subtraction), kept if |x_i - x_j| <= 3.5 mm and, when i and j are both surface nodes,
   their midpoint lies in a tet of the (all-myocardial) heart mesh. Tissue graph = E1 u E2.
S3 metric: M = sum_a (f_a v_a)^-2 a a^T over the fibre, sheet and normal (= f x s) vectors of the fibre file; nodal M = the
   volume-weighted mean of the element M of the node's tets; an edge uses the mean of nodal M at i and j (E1) or at i, j and
   the middle node k (E2; k with A_ik = A_kj = 1 giving the smallest t_ij); t_ij = sqrt(d^T M d), d = x_j - x_i.
   Because M is linear in the three (f_a v_a)^-2, every edge stores q_a = d^T Mbar_a d (Mbar_a = mean of nodal a a^T),
   and t = sqrt(sum_a q_a / (f_a v_a)^2); the E2 minimum over k is taken for the speeds and factors in use.
Caches (runs/v51_2026-10-15/cache51/): topology keyed by heart, mesh sha256, stencil version and filter settings; edge q
   keyed by the topology key + fibre-file sha256. Speeds and factors are never cached (applied at load).
"""
import hashlib
import json
import os
import time

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CACHE = os.path.join(REPO, 'runs', 'v51_2026-10-15', 'cache51')
STENCIL_VERSION = 'v51-2ring-1'
MAX_E2_MM = 3.5
MID_KNN = 32                     # tets (nearest centroids) searched for an E2 midpoint
BARY_EPS = 1e-9


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def read_pts(f):
    with open(f) as fh:
        n = int(fh.readline())
        return np.loadtxt(fh, max_rows=n) / 1e3                     # um -> mm


def read_elem(f):
    with open(f) as fh:
        n = int(fh.readline())
        return np.loadtxt(fh, usecols=(1, 2, 3, 4), dtype=np.int64, max_rows=n)


def read_lon(f):
    return np.loadtxt(f, skiprows=1)


# ------------------------------------------------------------------ topology
def adjacency(E, N):
    pairs = np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))])
    pairs.sort(axis=1)
    key = np.unique(pairs[:, 0] * N + pairs[:, 1])
    e1 = np.c_[key // N, key % N]
    A = coo_matrix((np.ones(2 * len(e1), bool), (np.r_[e1[:, 0], e1[:, 1]], np.r_[e1[:, 1], e1[:, 0]])), shape=(N, N)).tocsr()
    A.sort_indices()
    return e1, A


def surface_nodes(E, N):
    F = np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]])
    F.sort(axis=1)
    k = F[:, 0] * N * N + F[:, 1] * N + F[:, 2]
    u, c = np.unique(k, return_counts=True)
    b = u[c == 1]
    m = np.zeros(N, bool)
    m[np.unique(np.c_[b // (N * N), (b // N) % N, b % N])] = True
    return m


def e2_triples(pts, A, block=20000, log=print, rows_max=None):
    """All (i, j, k) with i < j, A_ik = A_kj = 1, A_ij = 0, |x_i - x_j| <= MAX_E2_MM. Sorted by (i, j)."""
    N = A.shape[0]
    ip, ix = A.indptr, A.indices
    deg = np.diff(ip)
    dkey = np.sort((np.repeat(np.arange(N), deg) * N + ix))       # directed 1-ring keys
    out_i, out_j, out_k = [], [], []
    n_dist = 0
    for b0 in range(0, N if rows_max is None else rows_max, block):
        rows = np.arange(b0, min(N if rows_max is None else rows_max, b0 + block))
        ik_i = np.repeat(rows, deg[rows]); ik_k = ix[ip[rows[0]]:ip[rows[-1] + 1]].astype(np.int64)
        cnt = deg[ik_k]
        tri_i = np.repeat(ik_i, cnt); tri_k = np.repeat(ik_k, cnt)
        starts = ip[ik_k]
        offs = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        tri_j = ix[np.repeat(starts, cnt) + offs]
        m = tri_j > tri_i
        tri_i, tri_j, tri_k = tri_i[m], tri_j[m], tri_k[m]
        key = tri_i * N + tri_j
        pos = np.searchsorted(dkey, key); pos[pos >= len(dkey)] = 0
        not1 = dkey[pos] != key                                     # graph distance exactly 2
        tri_i, tri_j, tri_k = tri_i[not1], tri_j[not1], tri_k[not1]
        dist = np.linalg.norm(pts[tri_j] - pts[tri_i], axis=1)
        ok = dist <= MAX_E2_MM
        n_dist += int((~ok).sum())
        out_i.append(tri_i[ok].astype(np.int32)); out_j.append(tri_j[ok].astype(np.int32)); out_k.append(tri_k[ok].astype(np.int32))
    i = np.concatenate(out_i); j = np.concatenate(out_j); k = np.concatenate(out_k)
    o = np.lexsort((k, j, i))
    return i[o], j[o], k[o], n_dist


def tets_inverse(pts, E):
    a = pts[E[:, 0]]
    J = np.stack([pts[E[:, 1]] - a, pts[E[:, 2]] - a, pts[E[:, 3]] - a], axis=2)        # columns = edges
    return a, np.linalg.inv(J)


def inside_mesh(p, pts, E, tree, a, Jinv, knn=MID_KNN, chunk=40000):
    """True where point p lies in a tet among its knn nearest-centroid tets (barycentric test)."""
    res = np.zeros(len(p), bool)
    for c0 in range(0, len(p), chunk):
        q = p[c0:c0 + chunk]
        _, nb = tree.query(q, k=knn)
        lam = np.einsum('nkij,nkj->nki', Jinv[nb], q[:, None, :] - a[nb])
        ins = (lam >= -BARY_EPS).all(-1) & (lam.sum(-1) <= 1 + BARY_EPS)
        res[c0:c0 + chunk] = ins.any(1)
    return res


def topology(h, log=print):
    """Cached E1, E2 pairs and E2 middle-node triples for heart h."""
    B = os.path.join(REPO, 'data', 'biv', h)
    pf, ef = os.path.join(B, 'biv.pts'), os.path.join(B, 'biv.elem')
    inp = {'heart': h, 'pts_sha256': sha256_file(pf), 'elem_sha256': sha256_file(ef), 'stencil': STENCIL_VERSION,
           'max_e2_mm': MAX_E2_MM, 'midpoint_knn': MID_KNN, 'bary_eps': BARY_EPS}
    key = hashlib.sha256(json.dumps(inp, sort_keys=True).encode()).hexdigest()
    f = os.path.join(CACHE, f'topo_{h}_{key[:16]}.npz')
    if os.path.exists(f):
        d = np.load(f)
        assert str(d['key']) == key
        return {k: d[k] for k in d.files}, json.loads(str(d['info'])), key
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    pts, E = read_pts(pf), read_elem(ef)
    N = len(pts)
    e1, A = adjacency(E, N)
    surf = surface_nodes(E, N)
    ti, tj, tk, n_dist = e2_triples(pts, A, log=log)
    first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
    pair_i, pair_j = ti[first], tj[first]
    pair_of_tri = np.cumsum(first) - 1
    # midpoint test for surface-surface pairs
    test = surf[pair_i] & surf[pair_j]
    a, Jinv = tets_inverse(pts, E)
    tree = cKDTree(pts[E].mean(1))
    ins = inside_mesh(0.5 * (pts[pair_i[test]] + pts[pair_j[test]]), pts, E, tree, a, Jinv)
    keep = np.ones(len(pair_i), bool); keep[np.where(test)[0][~ins]] = False
    # validation: interior pairs (not both surface) should all lie inside
    rng = np.random.default_rng(0)
    inter = np.where(~test)[0]; smp = rng.choice(inter, min(20000, len(inter)), replace=False)
    ins_v = inside_mesh(0.5 * (pts[pair_i[smp]] + pts[pair_j[smp]]), pts, E, tree, a, Jinv)
    newidx = np.cumsum(keep) - 1
    tri_keep = keep[pair_of_tri]
    out = {'e1': e1.astype(np.int32), 'e2': np.c_[pair_i[keep], pair_j[keep]].astype(np.int32),
           'tri_pair': newidx[pair_of_tri[tri_keep]].astype(np.int32), 'tri_k': tk[tri_keep].astype(np.int32)}
    info = {'nodes': int(N), 'elements': int(len(E)), 'E1': int(len(e1)), 'E2_candidates_after_distance': int(len(pair_i)),
            'E2_rejected_distance_gt_3.5mm_triples': int(n_dist), 'E2_tested_surface_pairs': int(test.sum()),
            'E2_rejected_midpoint_outside': int((~ins).sum()), 'E2': int(keep.sum()), 'E2_triples': int(tri_keep.sum()),
            'edges_per_node_E1': round(2 * len(e1) / N, 2), 'edges_per_node_E1uE2': round(2 * (len(e1) + keep.sum()) / N, 2),
            'interior_midpoint_validation_inside_fraction': float(ins_v.mean()), 'surface_nodes': int(surf.sum()),
            'build_s': round(time.time() - t0, 1)}
    np.savez(f, key=key, info=json.dumps(info), inputs=json.dumps(inp), **out)
    json.dump(inp | {'key': key, 'info': info}, open(f[:-4] + '.json', 'w'), indent=1)
    log(f'topology {h}: {info}')
    return out, info, key


# ------------------------------------------------------------------ metric
def nodal_components(pts, E, lon):
    """(N, 3, 6) volume-weighted nodal means of a a^T (a = fibre, sheet, normal), as xx yy zz xy xz yz."""
    f = lon[:, :3] / np.linalg.norm(lon[:, :3], axis=1, keepdims=True)
    s = lon[:, 3:6] / np.linalg.norm(lon[:, 3:6], axis=1, keepdims=True)
    n = np.cross(f, s); n /= np.linalg.norm(n, axis=1, keepdims=True)
    x0 = pts[E[:, 0]]
    vol = np.abs(np.einsum('ij,ij->i', pts[E[:, 1]] - x0, np.cross(pts[E[:, 2]] - x0, pts[E[:, 3]] - x0))) / 6
    N = len(pts)
    out = np.zeros((N, 3, 6))
    wsum = np.bincount(E.ravel(), weights=np.repeat(vol, 4), minlength=N)
    for ai, v in enumerate((f, s, n)):
        comp = np.stack([v[:, 0] ** 2, v[:, 1] ** 2, v[:, 2] ** 2, v[:, 0] * v[:, 1], v[:, 0] * v[:, 2], v[:, 1] * v[:, 2]], 1) * vol[:, None]
        for c in range(6):
            out[:, ai, c] = np.bincount(E.ravel(), weights=np.repeat(comp[:, c], 4), minlength=N) / wsum
    return out


def quad(d, Mc):
    """d^T M d for M given as (n, 3, 6) components -> (n, 3)."""
    dx, dy, dz = d[:, 0:1], d[:, 1:2], d[:, 2:3]
    return (dx * dx * Mc[:, :, 0] + dy * dy * Mc[:, :, 1] + dz * dz * Mc[:, :, 2]
            + 2 * (dx * dy * Mc[:, :, 3] + dx * dz * Mc[:, :, 4] + dy * dz * Mc[:, :, 5]))


def edge_q(h, lonf, log=print):
    """Cached q (n_edges, 3) for E1 and for every E2 triple, for the fibre file lonf."""
    topo, info, tkey = topology(h, log)
    fsha = sha256_file(lonf)
    key = hashlib.sha256(json.dumps({'topology': tkey, 'fibre_sha256': fsha, 'metric': 'nodal volume-weighted a a^T, mean over i, j (, k)'}).encode()).hexdigest()
    f = os.path.join(CACHE, f'q_{h}_{key[:16]}.npz')
    if os.path.exists(f):
        d = np.load(f)
        assert str(d['key']) == key
        return topo, info, d['q1'], d['qt'], {'topology_key': tkey, 'fibre_sha256': fsha, 'q_key': key}
    t0 = time.time()
    B = os.path.join(REPO, 'data', 'biv', h)
    pts, E = read_pts(os.path.join(B, 'biv.pts')), read_elem(os.path.join(B, 'biv.elem'))
    Mn = nodal_components(pts, E, read_lon(lonf))
    e1 = topo['e1'].astype(np.int64)
    q1 = (quad(pts[e1[:, 1]] - pts[e1[:, 0]], 0.5 * (Mn[e1[:, 0]] + Mn[e1[:, 1]]))).astype(np.float32)
    e2 = topo['e2'].astype(np.int64); tp = topo['tri_pair'].astype(np.int64); tk = topo['tri_k'].astype(np.int64)
    qt = np.empty((len(tp), 3), np.float32)
    for c0 in range(0, len(tp), 2_000_000):
        sl = slice(c0, c0 + 2_000_000)
        i, j, k = e2[tp[sl], 0], e2[tp[sl], 1], tk[sl]
        qt[sl] = quad(pts[j] - pts[i], (Mn[i] + Mn[j] + Mn[k]) / 3.0)
    np.savez(f, key=key, q1=q1, qt=qt)
    log(f'edge q {h}: {time.time() - t0:.0f} s')
    return topo, info, q1, qt, {'topology_key': tkey, 'fibre_sha256': fsha, 'q_key': key}


class Tissue:
    """Tissue graph of one heart for one fibre file; weights for given speeds and factors."""

    def __init__(self, h, lonf, log=print):
        self.h, self.lonf = h, lonf
        self.topo, self.info, self.q1, self.qt, self.keys = edge_q(h, lonf, log)
        self.N = self.info['nodes']
        tp = self.topo['tri_pair']
        self.starts = np.r_[0, np.flatnonzero(np.diff(tp)) + 1]
        assert len(self.starts) == len(self.topo['e2'])

    def weights(self, speeds, factors):
        w = np.array([1.0 / (factors[a] * speeds[a]) ** 2 for a in ('fibre', 'sheet', 'normal')])
        t1 = np.sqrt(self.q1.astype(np.float64) @ w)
        tt = np.sqrt(self.qt.astype(np.float64) @ w)
        t2 = np.minimum.reduceat(tt, self.starts)
        e = np.r_[self.topo['e1'], self.topo['e2']].astype(np.int64)
        return e, np.r_[t1, t2]

    def graph(self, speeds, factors):
        e, t = self.weights(speeds, factors)
        N = self.N
        G = csr_matrix((np.r_[t, t], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(N, N))
        return G

    @staticmethod
    def solve(G, sources, limit=np.inf):
        """Tissue-only activation from source nodes at t = 0."""
        T = dijkstra(G, directed=True, indices=np.atleast_1d(sources), limit=limit, min_only=True)
        return T


def probe(h, frac=0.1, log=print):
    """Subset run (brief: subset first): E2 triples for the first frac of node rows, with time and peak RSS."""
    import resource
    B = os.path.join(REPO, 'data', 'biv', h)
    t0 = time.time()
    pts, E = read_pts(os.path.join(B, 'biv.pts')), read_elem(os.path.join(B, 'biv.elem'))
    N = len(pts)
    e1, A = adjacency(E, N)
    t1 = time.time()
    ti, tj, tk, nd = e2_triples(pts, A, rows_max=int(frac * N))
    first = np.r_[True, (ti[1:] != ti[:-1]) | (tj[1:] != tj[:-1])]
    return {'heart': h, 'frac_rows': frac, 'nodes': N, 'E1': int(len(e1)), 'adjacency_s': round(t1 - t0, 1),
            'triples': int(len(ti)), 'pairs': int(first.sum()), 'rejected_distance_triples': int(nd), 'triples_s': round(time.time() - t1, 1),
            'peak_rss_MB': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 0)}
