"""Audit 03b: junction exits (network -> muscle) in the paced v5 beats; corrects a03's exit test. Read only."""
import json
import numpy as np, pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
VG = 'analysis/v5_grid_2026-10-13'
res = {}
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    P = np.loadtxt(f'data/biv/{h}/biv.pts', skiprows=1) / 1e3; N = len(P)
    k = json.load(open(f'data/biv/{h}/purkinje/graph_scale.json'))['k']
    sp = '0.4800_0.4800' if h == 'Y5HYEDL4' else '0.3504_0.3360'
    cg = np.load(f'{VG}/cache/myo_{h}_E_{sp}.npz'); e = cg['e'].astype(np.int64); w = cg['w'].astype(float) / k
    net = dict(np.load(f'data/biv/{h}/purkinje/network.npz'))
    nodes, edges, spd = net['nodes'], net['edges'], net['edge_speed']; M = len(nodes)
    wn = np.maximum(np.linalg.norm(P[nodes[edges[:, 0]]] - P[nodes[edges[:, 1]]], axis=1), 1e-6) / spd
    ee = np.sort(edges, 1); kp = ee[:, 0] != ee[:, 1]; ee, wn = ee[kp], wn[kp]
    kk, iv = np.unique(ee, axis=0, return_inverse=True); wm = np.full(len(kk), np.inf); np.minimum.at(wm, iv.ravel(), wn)
    pmj = net['pmj']; mnode = nodes[pmj]; tj = cKDTree(P[mnode])
    S = pd.read_csv(f'data/biv/{h}/sites.csv')
    for site in ['rvot_septal_z_d10', 'lv_free_wall_phi180_z0.5_d10', 'lv_summit_superior_z_d90']:
        nd = int(S[S.id == site].node.iloc[0])
        ball = np.where(np.linalg.norm(P - P[nd], axis=1) < 1.5)[0]
        rows = [e[:, 0], e[:, 1], N + kk[:, 0], N + kk[:, 1], mnode, N + pmj, np.full(len(ball), N + M)]
        cols = [e[:, 1], e[:, 0], N + kk[:, 1], N + kk[:, 0], N + pmj, mnode, ball]
        data = [w, w, wm, wm, np.full(len(pmj), 2.0), np.full(len(pmj), 4.0), np.full(len(ball), 1e-6)]
        G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
        d = dijkstra(G, directed=True, indices=N + M) - 1e-6
        Tm, Tn = d[:N], d[N:N + M]
        ex = np.abs(Tm[mnode] - (Tn[pmj] + 4.0)) < 1e-6
        # myocardium-only time for comparison (no network)
        G0 = coo_matrix((np.r_[w, w, np.full(len(ball), 1e-6)], (np.r_[e[:, 0], e[:, 1], np.full(len(ball), N)], np.r_[e[:, 1], e[:, 0], ball])), shape=(N + 1, N + 1)).tocsr()
        T0 = dijkstra(G0, directed=True, indices=N)[:N]
        res[f'{h}_{site}'] = {'site_to_nearest_junction_mm': round(float(tj.query(P[nd])[0]), 1),
                              'first_network_entry_ms': round(float(Tn[pmj].min()), 1), 'his_ms': round(float(Tn[int(net['his'])]), 1),
                              'n_junction_exits': int(ex.sum()), 'first_exit_ms': round(float(Tm[mnode][ex].min()), 1) if ex.any() else None,
                              'frac_nodes_earlier_than_myocardium_only_by_1ms': round(float((Tm < T0 - 1).mean()), 3),
                              'total_with_net_ms': round(float(Tm.max()), 1), 'total_myocardium_only_ms': round(float(T0.max()), 1)}
json.dump(res, open('analysis/audit_2026-10-13/a03b_paced_exits.json', 'w'), indent=1)
for k_, v_ in res.items(): print(k_, v_)
