"""v5.2 beat driver on the graph engine (no ECG yet): graph52's in-heart tissue on the cut mesh, v5.2's conduction system
(data/biv/<H>/v52/purkinje/network_v52.npz, D21 build) and v5.1's coupling (heart51.couple's one-pass Dijkstra:
network -> muscle at every junction with the antegrade delay 4 ms, muscle -> network with the retrograde delay 2 ms, 7.3).
Differences from heart51, all from the v5.2 lock and step 2:
  - the tissue is graph52.Tissue52 on biv52cut (2-ring control, 3-ring HF; cut pairs removed; biv52cut.lon fibres);
  - the fibrous layer of the sleeves (fibrous_nodes52.npy and their RV copies) is non-excitable: every tissue edge that
    touches one is dropped (8.6);
  - RV junctions on nodes the cut duplicated couple to the RV copy (the RV elements' node), all others to the node itself;
  - a paced site stimulates 8.7's set: the excitable nodes within 1.5 mm (strict) of the site node (its RV copy for RV
    families) in the site node's connected component inside the ball (tet edges of the cut mesh), as sites52.py's
    capture test; the His beat fires the network's His.
The retrogradely entered junctions are counted per beat (7.3).
Usage: imported (Heart52); nothing runs on import. `python -B .../heart52.py check HEART` prints the set-up keys only.
"""
import importlib.util
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import graph52 as G52                                                                       # noqa: E402

g = G52.g
spec = importlib.util.spec_from_file_location('heart51', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', 'heart51.py'))
H51 = importlib.util.module_from_spec(spec); sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build')); spec.loader.exec_module(H51)

D_ANT, D_RET, BALL_MM, CAPTURE_MIN = 4.0, 2.0, 1.5, 4
RV_FAMILIES = {'rv_free_wall', 'rvot', 'supravalvar', 'intramural_rv_grid'}


class Heart52:
    def __init__(self, h, log=print):
        self.h = h
        V = os.path.join(REPO, 'data', 'biv', h, 'v52')
        pf, ef, _ = G52.mesh(h)
        self.P = g.read_pts(pf); self.E = g.read_elem(ef); self.N = len(self.P)
        self.Nm = len(g.read_pts(os.path.join(V, 'biv52.pts')))
        src = np.load(os.path.join(V, 'cut_dup52.npy'))
        self.dupof = np.full(self.Nm, -1); self.dupof[src[self.Nm:]] = np.arange(self.Nm, self.N)
        fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
        self.nonex = np.zeros(self.N, bool); self.nonex[fib] = True; self.nonex[self.dupof[fib][self.dupof[fib] >= 0]] = True
        tis = G52.Tissue52(h, log)
        e, w = tis.weights()
        keep = ~(self.nonex[e[:, 0]] | self.nonex[e[:, 1]])
        self.e, self.w = e[keep], w[keep]
        self.edges_dropped_fibrous = int((~keep).sum())
        nf = os.path.join(V, 'purkinje', 'network_v52.npz')
        net = dict(np.load(nf))
        kind = net['kind'].astype(str)
        nodes = net['nodes'].astype(np.int64).copy()
        rvn = (kind == 'distal_rv') & (self.dupof[np.minimum(nodes, self.Nm - 1)] >= 0) & (nodes < self.Nm)
        nodes[rvn] = self.dupof[nodes[rvn]]
        net['nodes'] = nodes
        self.net = net
        self.rv_junction_nodes_on_copies = int(rvn[net['pmj']].sum())
        self.A = None
        self.keys = {'tissue': tis.keys, 'factors': G52.FACTORS[h]['factors'], 'speeds': G52.SPEEDS[h], 'stencil': G52.FACTORS[h]['stencil'],
                     'network_sha256': g.sha256_file(nf), 'edges_dropped_fibrous': self.edges_dropped_fibrous,
                     'rv_junctions_on_cut_copies': self.rv_junction_nodes_on_copies}

    def stimulated(self, node, family):
        """8.7's stimulated set (as sites52.py capture())."""
        n = int(node)
        if family in RV_FAMILIES and n < self.Nm and self.dupof[n] >= 0:
            n = int(self.dupof[n])
        if self.A is None:
            r = np.r_[self.E[:, 0], self.E[:, 0], self.E[:, 0], self.E[:, 1], self.E[:, 1], self.E[:, 2]]
            c = np.r_[self.E[:, 1], self.E[:, 2], self.E[:, 3], self.E[:, 2], self.E[:, 3], self.E[:, 3]]
            self.A = coo_matrix((np.ones(len(r)), (r, c)), shape=(self.N, self.N)).tocsr(); self.A = self.A + self.A.T
            self.tree = cKDTree(self.P)
        ball = np.array(self.tree.query_ball_point(self.P[n], BALL_MM - 1e-9))
        ex = ball[~self.nonex[ball]]
        if n not in set(ex.tolist()):
            return np.zeros(0, np.int64)
        _, lb = connected_components(self.A[ex][:, ex], directed=False)
        st = ex[lb == lb[np.where(ex == n)[0][0]]]
        return st if len(st) >= CAPTURE_MIN else np.zeros(0, np.int64)

    def solve(self, sources=None, his=False):
        """Activation times (ms) of every cut-mesh node, the network node times, and the retrograde junction count."""
        N, net = self.N, self.net
        M = len(net['nodes'])
        rows, cols, data = [self.e[:, 0], self.e[:, 1]], [self.e[:, 1], self.e[:, 0]], [self.w, self.w]
        gn = H51.net_graph(net, self.P).tocoo(); kk = (gn.row < M) & (gn.col < M)
        m = net['nodes'][net['pmj']]; j = N + net['pmj']
        rows += [N + gn.row[kk], m, j]; cols += [N + gn.col[kk], j, m]
        data += [gn.data[kk], np.full(len(m), D_RET), np.full(len(m), D_ANT)]
        src = N + M
        if his:
            s = np.array([N + int(net['his'])])
        else:
            s = np.asarray(sources, np.int64)
        rows.append(np.full(len(s), src)); cols.append(s); data.append(np.full(len(s), 1e-6))
        Gc = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
        T = dijkstra(Gc, directed=True, indices=src) - 1e-6
        Tm, Tn = T[:N], T[N:N + M]
        retro = int(np.sum(np.isclose(Tn[net['pmj']], Tm[m] + D_RET, atol=1e-9, rtol=0) & (Tm[m] + D_RET <= Tn[net['pmj']] + 1e-9)))
        unact = int((np.isinf(Tm) & ~self.nonex).sum())
        return Tm, Tn, {'retrograde_junctions': retro, 'unactivated_excitable_nodes': unact}


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        Hh = Heart52(sys.argv[2])
        print(json.dumps(Hh.keys, default=str), flush=True)
