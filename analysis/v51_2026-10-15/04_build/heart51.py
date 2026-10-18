"""v5.1 beat solver (v5.1 brief Step 4.6 onwards): the adopted nodal graph tissue solver (graph51, slab factors), the v5.1
conduction system (network51) and the v5.1 ECG weights (conductor51, sigma_i source), coupled as v5 (v5_grid.py
Heart.solve, one Dijkstra pass): network -> muscle at every junction with the antegrade delay 4 ms, muscle -> network with
the retrograde delay 2 ms; a paced site fires every node within 1.5 mm at t = 0; the His beat fires the network's His.
The solver stops if the v5.1 network, graph factors or weights do not match their recorded hashes and settings.

Usage (repo root, venv):
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/heart51.py check   coupling code vs the v5 solver (v5 tissue and
                                                                           network fed in): must be bit-identical
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/heart51.py his     the v5.1 His beat (Step 4.6)
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import conductor51 as C51                                             # noqa: E402
import graph51 as g                                                    # noqa: E402
import solver51 as S                                                   # noqa: E402

D_ANT, D_RET, BALL_UM = 4.0, 2.0, 1500.0
OUT = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build')


def sha256(f):
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def net_graph(net, pts):
    """As 14_purkinje.py net_graph(): network edges, duplicate pairs keep the fastest copy; (n + 1) x (n + 1)."""
    nodes, edges = net['nodes'], net['edges']
    w = np.maximum(np.linalg.norm(pts[nodes[edges[:, 0]]] - pts[nodes[edges[:, 1]]], axis=1), 1e-6) / net['edge_speed']
    e = np.sort(edges, axis=1)
    keep = e[:, 0] != e[:, 1]
    e, w = e[keep], w[keep]
    key, inv = np.unique(e, axis=0, return_inverse=True)
    wm = np.full(len(key), np.inf)
    np.minimum.at(wm, inv.ravel(), w)
    n = len(nodes)
    return coo_matrix((np.r_[wm, wm], (np.r_[key[:, 0], key[:, 1]], np.r_[key[:, 1], key[:, 0]])), shape=(n + 1, n + 1))


def couple(N, e, w, net, pts_um, site_node=None, d_ant=D_ANT, d_ret=D_RET):
    """v5 coupling (v5_grid.py Heart.solve) on any tissue edge list: returns muscle activation times (N,)."""
    rows, cols, data = [e[:, 0], e[:, 1]], [e[:, 1], e[:, 0]], [w, w]
    M = len(net['nodes'])
    gn = net_graph(net, pts_um / 1e3).tocoo(); kk = (gn.row < M) & (gn.col < M)
    m = net['nodes'][net['pmj']]; j = N + net['pmj']
    da = d_ant if np.ndim(d_ant) else np.full(len(m), d_ant)
    rows += [N + gn.row[kk], m, j]; cols += [N + gn.col[kk], j, m]
    data += [gn.data[kk], np.full(len(m), d_ret), da]
    src = N + M
    if site_node is None:
        rows.append(np.array([src])); cols.append(np.array([N + int(net['his'])])); data.append(np.array([1e-6]))
    else:
        s = np.where(np.linalg.norm(pts_um - pts_um[site_node], axis=1) < BALL_UM)[0]
        rows.append(np.full(len(s), src)); cols.append(s); data.append(np.full(len(s), 1e-6))
    G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
    return (dijkstra(G, directed=True, indices=src) - 1e-6)[:N]


class Heart51:
    def __init__(self, h):
        if os.environ.get('HEART') != h:
            raise ValueError('HEART must equal the heart (template and modules read it)')
        self.h = h
        B = os.path.join(REPO, 'data', 'biv', h)
        self.pts_um = g.read_pts(os.path.join(B, 'biv.pts')) * 1e3
        self.N = len(self.pts_um)
        lonf = S.lon51(h)
        tis = g.Tissue(h, lonf, metric='nodal')
        self.factors = S.load_factors(h, lonf, 'nodal')
        self.e, self.w = tis.weights(S.SPEEDS[h], self.factors)
        par = json.load(open(os.path.join(REPO, 'params', f'params_network_{h}_v51.json')))
        nf = os.path.join(B, 'purkinje_v51', 'network_v51.npz')
        if sha256(nf) != par['network_v51_sha256']:
            raise ValueError(f'{nf} does not match params_network_{h}_v51.json')
        self.net = dict(np.load(nf))
        self.d_ant, self.d_ret = par['junction_delays_ms']['antegrade'], par['junction_delays_ms']['retrograde']
        assert (self.d_ant, self.d_ret) == (D_ANT, D_RET)
        wz = np.load(os.path.join(B, 'ecgW_v51.npz'))
        assert str(wz['sigma']) == 'i' and float(wz['c']) == -1.0
        self.W = wz['W'].astype(float)
        self.CD = C51.biv_module('cd', '15_conductor.py', h)
        self.TM = self.CD.Template()
        self.keys = {'tissue': tis.keys, 'factors': self.factors, 'network_sha256': par['network_v51_sha256'],
                     'weights_sha256': sha256(os.path.join(B, 'ecgW_v51.npz'))}

    def solve(self, site_node=None):
        return couple(self.N, self.e, self.w, self.net, self.pts_um, site_node, self.d_ant, self.d_ret)

    def ecg(self, T):
        tend = float(min(990, max(140, np.ceil((T.max() + 20) / 10) * 10)))
        t = np.arange(0, tend + 0.5, 1.0)
        return t, self.CD.ecg_of(T, t, self.W, self.TM)


def check():
    """The coupling code must reproduce the v5 solver bit for bit when fed v5's tissue graph and network (His beat and
    one paced site)."""
    h = os.environ['HEART']
    VG = module('vg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'v5_grid_guarded.py'))
    H = VG.Heart('E', h)
    H.d_ant = np.full(len(H.net['pmj']), 4.0)
    site = [s for s in S.sites(h) if s['id'] == 'lv_free_wall_phi180_z0.5_d10'][0]
    out = {}
    for lab, sn in (('his', None), (site['id'], int(site['node']))):
        a = H.solve(sn)
        b = couple(H.N, H.e, H.w, H.net, H.pts * 1e3, sn, H.d_ant, 2.0)
        out[lab] = float(np.abs(a - b).max())
    print(h, 'max |v5 solver - heart51 coupling| (ms):', out)
    if max(out.values()) != 0.0:
        sys.exit('coupling check failed')


def his():
    h = os.environ['HEART']
    t0 = time.time()
    H = Heart51(h)
    T = H.solve(None)
    t, ecg = H.ecg(T)
    d = os.path.join(OUT, h, 'his51'); os.makedirs(d, exist_ok=True)
    np.save(os.path.join(d, 'his_T.npy'), T.astype(np.float32)); np.save(os.path.join(d, 'his_ecg.npy'), ecg.astype(np.float32))
    VG = module('vg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'v5_grid_guarded.py'))
    m = VG.his_metrics(h, T, ecg)
    # His -> detected QRS onset; QRS any lead; C10 voltages
    from ecg_depth_criteria import from_leads, measure_beat
    pad = 60; L = C51.LEADS
    leads = {l: np.concatenate([np.full(pad, ecg[0, L.index(l)]), ecg[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    mb = measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))
    m['his_to_detected_qrs_onset_ms'] = round(float(mb['onset_ms']) - pad, 1)
    m['qrs_detected_any_lead_ms'] = mb.get('qrs_duration_any_lead_ms')
    base = ecg[0]
    msk = (t >= T.min()) & (t <= T.max() + 3)
    rs = {}
    for l in ('V1', 'V2', 'V3', 'V4', 'V5', 'V6'):
        y = ecg[msk, L.index(l)] - base[L.index(l)]
        rs[l] = {'R_mV': round(float(max(y.max(), 0)), 3), 'S_mV': round(float(max(-y.min(), 0)), 3),
                 'R_over_S': round(float(max(y.max(), 0) / max(-y.min(), 1e-9)), 2)}
    m['C10_R_S'] = rs
    m['C10_sokolow_lyon_mV'] = round(rs['V1']['S_mV'] + max(rs['V5']['R_mV'], rs['V6']['R_mV']), 3)
    ang = np.radians([0, 60, 120, -150, -30, 90]); A = np.c_[np.cos(ang), np.sin(ang)]
    cc = np.linalg.lstsq(A, np.array([(ecg[msk, j] - base[j]).max() + (ecg[msk, j] - base[j]).min() for j in range(6)]), rcond=None)[0]
    m['C10_frontal_net_magnitude_mV'] = round(float(np.hypot(*cc)), 3)
    lvn = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'surfaces', 'lv_endo.vtx'), skiprows=2, dtype=np.int64)
    rvn = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'surfaces', 'rv_endo.vtx'), skiprows=2, dtype=np.int64)
    m['first_rv_endo_after_lv_onset_ms'] = round(float(T[rvn].min() - T[lvn].min()), 1)
    a = [m[f'a_onset_{k}_ms'] for k in ('ant', 'sep', 'post')]
    m['a_areas_within_5ms_of_earliest'] = int(sum(x - min(a) <= 5.0 for x in a))
    m['a_spread_ms'] = round(max(a) - min(a), 1)
    res = {'heart': h, 'metrics': m, 'keys': H.keys, 'unactivated_nodes': int(np.isinf(T).sum()), 'wall_s': round(time.time() - t0, 1)}
    json.dump(res, open(os.path.join(HERE, f'his51_{h}.json'), 'w'), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == '__main__':
    {'check': check, 'his': his}[sys.argv[1]]()
