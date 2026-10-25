"""v5.2 arm A41 (build answers D34, ADOPTED: Alex, "Both levels", 25 Oct 2026 21:26:55 UTC): the RVOT network on either side
of the primary, built as set-up beside the primary network (which stays unchanged). No beat.

Text: relock4-build-answers-2026-10-20.md (sha256 60f01c99...), D34, section 13 row A41 (arm cell, quoted in the docstring
of build() below). Set-up as P14: the merged mesh's rv_endo surface (data/biv/<H>/v52/surfaces/rv_endo.surf); the step-2g
network (data/biv/<H>/v52/purkinje/network_v52.npz); the D13 PV frame on the full cohort mesh (heights on the PV axis,
mid-plane ring at 0; theta 0 at D32's posterior centre); cut52's stored landmarks (h0, h100, the D14 boundary).
rv_endo distance = D23's: Dijkstra over rv_endo nodes, each joined to its neighbours and their neighbours by straight
chords (step0_report34.Surf, 2-ring).
Outputs: data/biv/<H>/v52/purkinje/network_v52_A41a.npz and network_v52_A41b.npz (same arrays as network_v52.npz, plus an
'A41_level' provenance string; level (b) adds 'A41_new_node' flags and 'A41_edge_time_ms'), arm41_<H>.json here (as-built report).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/arm41.py [HEART ...]
"""
import hashlib
import importlib.util
import json
import os
import sys

import numpy as np
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import sheet52 as SH                                                                        # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402

R34 = SH.R34
DENS = {'Y5HYEDL4': 7.6, '6G8DD8S5': 9.6, '7D98EVAR': 8.8}           # step 0's printed v5.1 RV density, used as written
P73 = {'Y5HYEDL4': 73.0, '6G8DD8S5': 73.5, '7D98EVAR': 74.0}
V_DISTAL = 2.0                                                      # mm/ms, the lock's straight-line distal speed
spec = importlib.util.spec_from_file_location('heart51', os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build', 'heart51.py'))
sys.path.insert(0, os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build'))
H51 = importlib.util.module_from_spec(spec); spec.loader.exec_module(H51)


def tri_area(P, T):
    return 0.5 * np.linalg.norm(np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]), axis=1)


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return {'median': round(float(np.median(x)), 2), 'p90': round(float(np.percentile(x, 90)), 2), 'max': round(float(x.max()), 2)} if len(x) else None


def sha(f):
    return hashlib.sha256(open(f, 'rb').read()).hexdigest()


def build(h):
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'rule': 'D34 (adopted 25 Oct 2026 21:26:55 UTC), section 13 row A41; record relock4 sha256 60f01c99...'}
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces'); PK = os.path.join(V, 'purkinje')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3
    E, tg = read_elem(os.path.join(V, 'biv52'))
    nb = len(read_elem(os.path.join(G.REPO, 'data', 'biv', h, 'biv'))[0])
    Pf, Ef, tf = G.load_full(h)
    pv, _ = G.pulmonary_frame(Pf, Ef, tf)
    L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
    h0, h100, hb = L['height_0pct_mm'], L['height_100pct_mm'], L['split_height_mm']
    h73 = h0 + P73[h] / 100 * (h100 - h0)
    rec['frame'] = {'h0_mm': h0, 'h100_mm': h100, 'D14_boundary_mm': hb, f'h_at_{P73[h]}pct_mm': round(float(h73), 3), 'ring_mm': 0.0}
    tri = np.loadtxt(os.path.join(S, 'rv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    SF = R34.Surf(P, tri)
    rn = SF.nodes; hn = pv.h(P[rn])
    tc = P[tri].mean(1); htri = pv.h(tc); atri = tri_area(P, tri) / 100.0
    wrap = lambda a: (np.asarray(a) + 45) % 360 - 45
    thtri = wrap(pv.theta(tc))
    nf = os.path.join(PK, 'network_v52.npz')
    net = {k: v for k, v in np.load(nf).items()}
    rec['primary_network'] = {'file': os.path.relpath(nf, G.REPO), 'sha256': sha(nf)}
    nodes, kind, pmj = net['nodes'].astype(np.int64), net['kind'].astype(str), net['pmj'].astype(np.int64)
    rvpmj = pmj[kind[pmj] == 'distal_rv']
    hp = pv.h(P[nodes[rvpmj]])
    trn = cKDTree(P[rn])
    on_rv = lambda m: rn[trn.query(P[np.atleast_1d(m)])[1]]          # nearest rv_endo node (merged id)

    parts = [('0 % landmark to boundary', lambda x: (x > h0) & (x < hb)), (f'boundary to {P73[h]} %', lambda x: (x >= hb) & (x <= h73)),
             (f'{P73[h]} % to ring', lambda x: (x > h73) & (x <= 0.0)), ('above ring', lambda x: x > 0.0)]
    quads = [('q0 (-45..45, posterior)', -45, 45), ('q90 (45..135)', 45, 135), ('q180 (135..225, anterior)', 135, 225), ('q270 (225..315)', 225, 315)]

    def by_part(hts, ths):
        out = {}
        for pn, f in parts:
            m = f(hts)
            out[pn] = {'count': int(m.sum()), 'by_quadrant': {qn: int((m & (ths >= a0) & (ths < a1)).sum()) for qn, a0, a1 in quads}}
        return out
    # ---------------------------------------------------------------- level (a) Remove
    rem = rvpmj[hp > h0]
    pmj_a = np.setdiff1d(pmj, rem)
    net_a = dict(net); net_a['pmj'] = pmj_a
    prov = lambda lv: np.array(json.dumps({'arm': 'A41', 'level': lv, 'rule': rec['rule'], 'source_network_sha256': rec['primary_network']['sha256'],
                                           'note': 'params is the primary\'s, unchanged; in level (b) the added DISTAL edges store edge_speed = straight length / '
                                                   '(D23 rv_endo distance / 2.0 mm/ms), so length / speed is the edge\'s time'}))
    net_a['A41_level'] = prov('a (Remove)')
    fa = os.path.join(PK, 'network_v52_A41a.npz'); np.savez(fa, **net_a)
    rec['level_a_remove'] = {'built': True, 'RV_PMJs_removed': int(len(rem)), 'nodes_and_edges_kept': True,
                             'removed_by_part': by_part(pv.h(P[nodes[rem]]), wrap(pv.theta(P[nodes[rem]]))),
                             'PMJs_primary_then_a': [int(len(pmj)), int(len(pmj_a))], 'file': os.path.relpath(fa, G.REPO), 'sha256': sha(fa)}
    # ---------------------------------------------------------------- level (b) Extend
    zone = (hn >= hb) & (hn <= 0.0)
    zone_nodes = rn[zone]
    zone_area = float(atri[(htri >= hb) & (htri <= 0.0)].sum())
    # sleeve-only rv_endo nodes (every element touching them is an appended sleeve element): nothing is built in the sleeves
    sleeve_el = np.r_[np.zeros(nb, bool), tg[nb:] == 2]
    touch_all = np.bincount(E.ravel(), minlength=len(P)); touch_sl = np.bincount(E[sleeve_el].ravel(), minlength=len(P))
    sleeve_only = (touch_all > 0) & (touch_all == touch_sl)
    cand = zone_nodes[~sleeve_only[zone_nodes]]
    # reachability: every zone node reachable from the network (RV DISTAL nodes) by D23's rv_endo distance
    rvd_idx = np.where(kind == 'distal_rv')[0]
    rvd_mesh = nodes[rvd_idx]
    d_net, _ = SF.dist(np.unique(on_rv(rvd_mesh)), 2)
    unreach = zone_nodes[~np.isfinite(d_net[SF.ids(zone_nodes)])]
    rec['level_b_extend'] = {'zone_rv_endo_nodes': int(len(zone_nodes)), 'zone_sleeve_only_nodes (not built on)': int((sleeve_only[zone_nodes]).sum()),
                             'zone_area_cm2': round(zone_area, 4), 'reachability_check': {'zone_nodes_unreachable': int(len(unreach)), 'pass': bool(len(unreach) == 0)}}
    if len(unreach):
        rec['level_b_extend'].update({'built': False, 'not run': f'{len(unreach)} zone nodes cannot be reached from the network by D23 rv_endo distance'})
        return rec, None
    target_raw = DENS[h] * zone_area
    target = int(np.floor(target_raw + 0.5))
    in_zone = lambda x: (x >= hb) & (x <= 0.0)
    count = int(in_zone(hp).sum())
    rec['level_b_extend'].update({'density_per_cm2 (step 0, as written)': DENS[h], 'target_before_rounding': round(target_raw, 3), 'target': target,
                                  'existing_zone_RV_PMJs': count})
    # farthest-point placement
    pos_existing = np.unique(on_rv(nodes[rvpmj]))                    # a PMJ sits at its Purkinje node's nearest rv_endo node
    D, _ = SF.dist(pos_existing, 2)
    D = D.copy()
    cand_local = SF.ids(cand)
    chosen, margins = [], []
    while count < target:
        dc = D[cand_local]
        mx = dc.max()
        if not np.isfinite(mx) or mx <= 0:
            rec['level_b_extend'].update({'built': False, 'not run': 'no zone node left with a positive finite distance before the target was reached'})
            return rec, None
        best = cand[dc == mx].min()                                  # ties to the lowest node id
        margins.append(float(mx - np.sort(dc)[-2]) if len(dc) > 1 else np.inf)   # best against second best (0 = exact tie)
        chosen.append(int(best))
        dn, _ = SF.dist([int(best)], 2)
        D = np.minimum(D, dn)
        count += 1
    # place PMJs: on a v5.1 RV DISTAL node without a PMJ whose nearest rv_endo node is the chosen node, else a new node
    has_pmj = np.zeros(len(nodes), bool); has_pmj[pmj] = True
    near_rv = on_rv(rvd_mesh)                                        # nearest rv_endo node of each primary RV DISTAL node
    new_nodes, pmj_on_existing = [], []
    for c in chosen:
        cand_ex = rvd_idx[(near_rv == c) & ~has_pmj[rvd_idx]]
        if len(cand_ex):
            g = int(cand_ex.min())                                   # the lower Purkinje-network node id
            pmj_on_existing.append(g); has_pmj[g] = True
        else:
            new_nodes.append(c)
    # join new nodes in rising PV-axis height (ties lowest node id) to the nearest RV DISTAL node (primary's, or new already joined)
    order = sorted(new_nodes, key=lambda m: (float(pv.h(P[[m]])[0]), m))
    prim_mesh = {}
    for g_ in rvd_idx:                                               # mesh node -> lower network id among the primary's RV DISTAL nodes
        m_ = int(nodes[g_])
        if m_ not in prim_mesh or g_ < prim_mesh[m_]:
            prim_mesh[m_] = int(g_)
    cand_join = dict(prim_mesh)                                      # mesh node -> network id
    nn0 = len(nodes)
    add_nodes, add_edges, add_time, add_len_rv, add_len_straight, new_ids = [], [], [], [], [], {}
    for m in order:
        dm, _ = SF.dist([m], 2)
        cm = np.array(sorted(cand_join))
        dcm = dm[SF.ids(on_rv(cm))]
        mn = dcm.min()
        tgt_mesh = int(cm[dcm == mn].min())                          # ties to the lowest node id
        gid = nn0 + len(add_nodes)
        add_nodes.append(m); new_ids[m] = gid
        add_edges.append((cand_join[tgt_mesh], gid)); add_time.append(float(mn) / V_DISTAL)
        add_len_rv.append(float(mn)); add_len_straight.append(float(np.linalg.norm(P[m] - P[tgt_mesh])))
        cand_join[m] = gid
    # assemble level (b)
    net_b = dict(net); net_b['A41_level'] = prov('b (Extend)')
    net_b['nodes'] = np.r_[nodes, np.array(add_nodes, np.int64)]
    net_b['kind'] = np.r_[kind, np.array(['distal_rv'] * len(add_nodes))].astype(net['kind'].dtype)
    for k in ('sheet_s_mm', 'sheet_a_mm'):
        if k in net:
            net_b[k] = np.r_[net[k], np.full(len(add_nodes), np.nan)]
    ae = np.array(add_edges, np.int64).reshape(-1, 2)
    st = np.array(add_len_straight); tt = np.array(add_time)
    spd = np.where(tt > 0, st / np.maximum(tt, 1e-12), V_DISTAL)      # encoded so that H51.net_graph's length / speed = the edge's time
    net_b['edges'] = np.r_[net['edges'], ae]
    net_b['edge_speed'] = np.r_[net['edge_speed'], spd]
    net_b['edge_class'] = np.r_[net['edge_class'], np.array(['DISTAL'] * len(ae))].astype(net['edge_class'].dtype)
    net_b['pmj'] = np.sort(np.r_[pmj, np.array(pmj_on_existing, np.int64), np.array([new_ids[m] for m in add_nodes], np.int64)])
    net_b['A41_new_node'] = np.r_[np.zeros(len(nodes), bool), np.ones(len(add_nodes), bool)]
    net_b['A41_edge_time_ms'] = np.r_[np.full(len(net['edges']), np.nan), tt]
    fb = os.path.join(PK, 'network_v52_A41b.npz'); np.savez(fb, **net_b)
    # checks: encoded times, PMJ counts, nothing above the ring or in the sleeves, everything fed from the His
    gb = H51.net_graph(net_b, P).tocsr()
    w_chk = np.array([gb[a, b] for a, b in ae]) if len(ae) else np.zeros(0)
    Tb = dijkstra(gb, directed=False, indices=int(net_b['his']))[:len(net_b['nodes'])]
    added_pmj_nodes = np.r_[np.array(pmj_on_existing, np.int64), np.array([new_ids[m] for m in add_nodes], np.int64)]
    hadd = pv.h(P[net_b['nodes'][added_pmj_nodes]]) if len(added_pmj_nodes) else np.zeros(0)
    s14 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'purkinje', 'summary.json')))['landmarks']
    mbn = np.where((net_b['nodes'] == s14['mb_end']) & (net_b['kind'].astype(str) == 'proximal'))[0]
    Tmb = dijkstra(gb, directed=False, indices=int(mbn.min()))[:len(net_b['nodes'])] if len(mbn) else None
    sp_mb, sp_rows = [], []
    for g_ in added_pmj_nodes:
        dstr = float(np.linalg.norm(P[net_b['nodes'][g_]] - P[s14['mb_end']]))
        sp_mb.append(dstr / Tmb[g_] if Tmb is not None and Tmb[g_] > 0 else np.nan)
        sp_rows.append([int(net_b['nodes'][g_]), int(g_), round(dstr, 3), round(float(Tmb[g_]), 3) if Tmb is not None else None, round(sp_mb[-1], 4)])
    sp_a = np.asarray(sp_mb, float); sp_f = sp_a[np.isfinite(sp_a)]
    # zone distances under each level
    def zone_dist(pmj_set):
        pos = np.unique(on_rv(net_b['nodes'][pmj_set]))
        d_, _ = SF.dist(pos, 2)
        return stats(d_[SF.ids(zone_nodes)])
    rv_p = pmj[kind[pmj] == 'distal_rv']; rv_a = pmj_a[kind[pmj_a] == 'distal_rv']
    kb = net_b['kind'].astype(str); rv_b = net_b['pmj'][kb[net_b['pmj']] == 'distal_rv']
    zcount_b = int(in_zone(pv.h(P[net_b['nodes'][rv_b]])).sum())
    dens_0b = (rec['level_a_remove']['removed_by_part']['0 % landmark to boundary']['count'],
               float(atri[(htri > h0) & (htri < hb)].sum()))
    rec['level_b_extend'].update({
        'built': True, 'positions_chosen': len(chosen), 'PMJ_on_existing_v51_DISTAL_nodes': len(pmj_on_existing), 'new_DISTAL_nodes': len(add_nodes),
        'zone_RV_PMJs_after': zcount_b, 'zone_density_after_per_cm2': round(zcount_b / zone_area, 3),
        'beside: 0 % landmark to boundary, primary (PMJs, cm2, per cm2)': [dens_0b[0], round(dens_0b[1], 3), round(dens_0b[0] / dens_0b[1], 3)],
        'added_by_part': by_part(hadd, wrap(pv.theta(P[net_b['nodes'][added_pmj_nodes]]))) if len(added_pmj_nodes) else None,
        'added_edges': int(len(ae)), 'added_edges_total_rv_endo_length_mm': round(float(sum(add_len_rv)), 3),
        'added_edges_total_straight_length_mm': round(float(sum(add_len_straight)), 3),
        'added_edge_time_check_max_abs_err_ms': float(np.max(np.abs(w_chk - tt))) if len(ae) else 0.0,
        'added_nodes_above_ring': int((pv.h(P[np.array(add_nodes, np.int64)]) > 0).sum()) if add_nodes else 0,
        'added_nodes_in_sleeves': int(sleeve_only[np.array(add_nodes, np.int64)].sum()) if add_nodes else 0,
        'added_PMJ_nodes_reached_from_His': bool(np.all(np.isfinite(Tb[added_pmj_nodes]))) if len(added_pmj_nodes) else True,
        'straight_line_speed_mb_end_to_added_PMJ_m_s (against 2.0)': dict(stats(sp_mb) or {}, min=round(float(sp_f.min()), 2) if len(sp_f) else None,
                                                                          n_ge_2=int((sp_f >= V_DISTAL).sum()), n_lt_2=int((sp_f < V_DISTAL).sum()),
                                                                          n_non_finite=int((~np.isfinite(sp_a)).sum())),
        'speed_rows (mesh node, network id, straight mm from mb_end, network ms from mb_end, m/s)': sp_rows,
        'placement_smallest_margin_best_vs_second_mm (step, 1-based)': [round(float(min(margins)), 6), int(np.argmin(margins)) + 1] if margins else None,
        'file': os.path.relpath(fb, G.REPO), 'sha256': sha(fb),
        'chosen_positions_in_order': chosen,
        'joins_in_order (new mesh node, joined to network id, rv_endo mm, time ms)': [[int(m), int(a), round(l_, 3), round(t_, 4)]
                                                                                    for m, (a, _), l_, t_ in zip(add_nodes, add_edges, add_len_rv, add_time)]})
    rec['zone_rv_endo_distance_to_nearest_RV_PMJ_mm'] = {'primary': zone_dist(rv_p), 'level_a': zone_dist(rv_a), 'level_b': zone_dist(rv_b)}
    rec['level_a_remove']['RV_PMJs_above_0pct_after'] = int((pv.h(P[nodes[rv_a]]) > h0).sum())
    return rec, net_b


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        r, _ = build(h)
        G.dump(r, os.path.join(HERE, f'arm41_{h}.json'))
        print(h, json.dumps({k: v for k, v in r.items() if k in ('level_a_remove', 'level_b_extend')}, default=str)[:1500], flush=True)
