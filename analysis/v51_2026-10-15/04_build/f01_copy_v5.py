"""Audit 03: realised conduction speeds (local CV = 1/|grad T| by propagation direction relative to fibre / sheet /
sheet-normal) on (a) the v5 combined-graph field without the network and (b) saved openCARP eikonal fields (v3 speeds);
plus network sanity of three paced v5 beats per heart and lon unit/orthogonality checks. Read only."""
import json, os, sys
import numpy as np, pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
VG = 'analysis/v5_grid_2026-10-13'
def rd_pts(h): return np.loadtxt(f'data/biv/{h}/biv.pts', skiprows=1) / 1e3
def rd_elem(h): return np.loadtxt(f'data/biv/{h}/biv.elem', skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
def rd_lon(f): return pd.read_csv(f, sep=r'\s+', skiprows=1, header=None).to_numpy()
def igb_last(f):
    b = open(f, 'rb').read(); x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float)
def egrad(P, E, u):
    x0 = P[E[:, 0]]; J = np.stack([P[E[:, 1]] - x0, P[E[:, 2]] - x0, P[E[:, 3]] - x0], 1)
    du = np.stack([u[E[:, 1]] - u[E[:, 0]], u[E[:, 2]] - u[E[:, 0]], u[E[:, 3]] - u[E[:, 0]]], 1)
    return np.linalg.solve(J, du[..., None])[..., 0]
def cv_by_dir(P, E, lon, T, tmin=8, tmax=80, cos_thr=0.95):
    g = egrad(P, E, T); te = T[E].mean(1)
    ok = np.isfinite(g).all(1) & (te > tmin) & (te < tmax)
    gn = np.linalg.norm(g, axis=1); ok &= gn > 1e-6
    u = g[ok] / gn[ok][:, None]; cv = 1 / gn[ok]
    f = lon[ok, :3]; s = lon[ok, 3:6]; f = f / np.linalg.norm(f, axis=1)[:, None]; s = s / np.linalg.norm(s, axis=1)[:, None]; n = np.cross(f, s)
    out = {}
    for nm, ax in (('fibre', f), ('sheet', s), ('normal', n)):
        c = np.abs(np.sum(u * ax, 1)); m = c > cos_thr
        out[nm] = {'median_m_s': round(float(np.median(cv[m])), 3) if m.any() else None, 'p25_p75': np.percentile(cv[m], [25, 75]).round(3).tolist() if m.any() else None, 'n_elem': int(m.sum())}
    return out
res = {'lon_checks': {}, 'speeds': {}, 'paced': {}}
for h in HEARTS:
    P = rd_pts(h); E = rd_elem(h); N = len(P)
    lon5 = rd_lon(f'{VG}/fibres_E/{h}/bivF.lon'); lon3 = rd_lon(f'data/biv/{h}/bivF.lon')
    for nm, L in (('v5', lon5), ('v3', lon3)):
        f, s = L[:, :3], L[:, 3:6]
        res['lon_checks'][f'{h}_{nm}'] = {'fibre_norm_min_max': [float(np.linalg.norm(f, axis=1).min()), float(np.linalg.norm(f, axis=1).max())],
                                         'sheet_norm_min_max': [float(np.linalg.norm(s, axis=1).min()), float(np.linalg.norm(s, axis=1).max())],
                                         'abs_dot_f_s_max': float(np.abs(np.sum(f * s, 1)).max()), 'abs_dot_f_s_p99': float(np.percentile(np.abs(np.sum(f * s, 1)), 99)),
                                         'nan': int(np.isnan(L).any(1).sum())}
    # v5 myocardial graph (cache) / k
    k = json.load(open(f'data/biv/{h}/purkinje/graph_scale.json'))['k']
    sp = '0.4800_0.4800' if h == 'Y5HYEDL4' else '0.3504_0.3360'
    cg = np.load(f'{VG}/cache/myo_{h}_E_{sp}.npz'); e = cg['e'].astype(np.int64); w = cg['w'].astype(float) / k
    S = pd.read_csv(f'data/biv/{h}/sites.csv')
    def solve_myo(node, e=e, w=w):
        ball = np.where(np.linalg.norm(P - P[node], axis=1) < 1.5)[0]
        G = coo_matrix((np.r_[w, w, np.full(len(ball), 1e-6)], (np.r_[e[:, 0], e[:, 1], np.full(len(ball), N)], np.r_[e[:, 1], e[:, 0], ball])), shape=(N + 1, N + 1)).tocsr()
        return dijkstra(G, directed=True, indices=N)[:N] - 1e-6
    node = int(S[S.id == 'lv_free_wall_phi180_z0.5_d50'].node.iloc[0])
    T5 = solve_myo(node)
    res['speeds'][f'{h}_v5_graph_nonet_lvfw_phi180_z0.5_d50'] = cv_by_dir(P, E, lon5, T5)
    # v3 graph with v3 speeds (rebuilt here, frozen fibres) to compare with openCARP on the same site
    lon = lon3; fb, sh = lon[:, :3], lon[:, 3:6]; nmv = np.cross(fb, sh)
    keys, ws = [], []
    for a_, b_ in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        dv = P[E[:, b_]] - P[E[:, a_]]
        t = np.sqrt((np.einsum('ij,ij->i', dv, fb) / 0.6) ** 2 + (np.einsum('ij,ij->i', dv, sh) / 0.4) ** 2 + (np.einsum('ij,ij->i', dv, nmv) / 0.48) ** 2)
        lo, hi = np.minimum(E[:, a_], E[:, b_]), np.maximum(E[:, a_], E[:, b_]); keys.append(lo * N + hi); ws.append(t)
    key, inv = np.unique(np.concatenate(keys), return_inverse=True); w3 = np.full(len(key), np.inf); np.minimum.at(w3, inv.ravel(), np.concatenate(ws))
    e3 = np.c_[key // N, key % N]
    for site in ['lv_free_wall_phi180_z0.5_d10', 'lv_free_wall_phi180_z0.5_d90', 'rvot_septal_z_d50']:
        run = f'runs/2026-10-07_nofast_{h}_{site}'
        if not os.path.exists(run + '/act.igb'):
            continue
        To = igb_last(run + '/act.igb')
        nd = int(S[S.id == site].node.iloc[0])
        Tg3 = solve_myo(nd, e3, w3 / k)
        res['speeds'][f'{h}_v3_openCARP_nonet_{site}'] = cv_by_dir(P, E, lon3, To)
        res['speeds'][f'{h}_v3_graph/k_nonet_{site}'] = cv_by_dir(P, E, lon3, Tg3)
        m = To > 20
        res['speeds'][f'{h}_v3_graph_vs_openCARP_{site}'] = {'median_ratio_graph/k_over_openCARP': round(float(np.median(Tg3[m] / To[m])), 4),
                                                            'median_abs_diff_ms': round(float(np.median(np.abs(Tg3 - To))), 2), 'total_openCARP': round(float(To.max()), 1), 'total_graph': round(float(Tg3.max()), 1)}
    # paced v5 beats with network: first capture, His time, latest region
    net = dict(np.load(f'data/biv/{h}/purkinje/network.npz'))
    nodes, edges, spd = net['nodes'], net['edges'], net['edge_speed']; M = len(nodes)
    wn = np.maximum(np.linalg.norm(P[nodes[edges[:, 0]]] - P[nodes[edges[:, 1]]], axis=1), 1e-6) / spd
    ee = np.sort(edges, 1); kp = ee[:, 0] != ee[:, 1]; ee, wn = ee[kp], wn[kp]
    kk, iv = np.unique(ee, axis=0, return_inverse=True); wm = np.full(len(kk), np.inf); np.minimum.at(wm, iv.ravel(), wn)
    pmj = net['pmj']; mnode = nodes[pmj]
    z = np.loadtxt(f'data/biv/{h}/uvc/z.dat'); ph = np.degrees(np.loadtxt(f'data/biv/{h}/uvc/phi.dat')); v = np.loadtxt(f'data/biv/{h}/uvc/v.dat')
    csv5 = pd.read_csv(f'analysis/v5_adopted_2026-10-13/purk_{h}_v5.csv')
    for site in ['rvot_septal_z_d10', 'lv_free_wall_phi180_z0.5_d10', 'lv_summit_superior_z_d90', 'lv_summit_inferior_lateral_z_d90']:
        if site not in set(S.id):
            continue
        nd = int(S[S.id == site].node.iloc[0])
        ball = np.where(np.linalg.norm(P - P[nd], axis=1) < 1.5)[0]
        rows = [e[:, 0], e[:, 1], N + kk[:, 0], N + kk[:, 1], mnode, N + pmj, np.full(len(ball), N + M)]
        cols = [e[:, 1], e[:, 0], N + kk[:, 1], N + kk[:, 0], N + pmj, mnode, ball]
        data = [w, w, wm, wm, np.full(len(pmj), 2.0), np.full(len(pmj), 4.0), np.full(len(ball), 1e-6)]
        G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
        d = dijkstra(G, directed=True, indices=N + M) - 1e-6
        Tm, Tn = d[:N], d[N:N + M]
        first_entry = float(Tn[pmj].min())
        exits = Tn[pmj] + 4.0 < Tm[mnode] - 0.01
        last = int(np.argmax(Tm))
        lastn = np.argsort(Tm)[-len(Tm) // 20:]
        stored = float(csv5[csv5.id == site].total_activation_ms.iloc[0]) if site in set(csv5.id) else None
        res['paced'][f'{h}_{site}'] = {'total_ms': round(float(Tm.max()), 1), 'stored_csv_total_ms': stored, 'unactivated': int(np.isinf(Tm).sum()),
                                       'first_network_entry_ms': round(first_entry, 1), 'his_ms': round(float(Tn[int(net['his'])]), 1),
                                       'first_network_exit_ms': round(float((Tn[pmj] + 4.0)[exits].min()), 1) if exits.any() else None,
                                       'n_junction_exits': int(exits.sum()), 'n_junctions': int(len(pmj)),
                                       'latest_node_z_phi_v': [round(z[last], 2), round(ph[last], 0), int(v[last])],
                                       'last5pct_RV_frac': round(float((v[lastn] == 1).mean()), 2), 'last5pct_median_z_phi': [round(float(np.median(z[lastn])), 2), round(float(np.median(ph[lastn])), 0)],
                                       't10_t50_t90_nodes_ms': np.percentile(Tm, [10, 50, 90]).round(1).tolist()}
    print(h, 'done', flush=True)
json.dump(res, open('analysis/v51_2026-10-15/04_build/f01_copy_v5.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
