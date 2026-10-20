"""v5.2 step 2b: the infundibulum cut (LOCK.md 8.2 with deviations D13 and D14, 20 Oct 2026), landmarks and split.

Landmarks on the posterior RVOT wall (8.2, assumption 32, D13; the first reading of report 35 (f)):
  100 % = the pulmonary mid-plane ring at the posterior sinus centre (the mid-plane ring is planar, so its "lowest
          posterior point" is read as its point at the posterior centre, the same point that is the posterior
          cusp-insertion nadir under D13);
  0 %   = the RV cavity node on the posterior side (within 60 deg of the posterior centre) nearest the projection of the
          100 % point along the RVOT axis (the pulmonary disc normal) down to the tricuspid-annulus level, read as the
          height of the tricuspid-ring node nearest the pulmonary ring (the superior annulus);
  span  = the surface distance between them on the RV cavity surface (2-ring graph), as report 35 (f).
Split height (D14, assumption 57): the path point at 47.2 % of the span from 0 %; its height along the RVOT axis is the
split height. The cut: every face shared by an LV-group element (tags 1, 25, 29) and an RV-group element (tags 2, 28)
whose centroid lies at or above the split height is split; below it the interface stays fused. Nodes of split faces that
are not also on a fused LV-RV face are duplicated for the RV-group elements (graph eikonal and monodomain); the lead-field
mesh keeps the original connectivity (8.2, assumption 33).
Stage "apply" (after 2c-2d): the same split on the merged mesh (data/biv/<H>/v52/biv52, sleeves and crescents included) at
the split height of the landmark stage, written as data/biv/<H>/v52/biv52cut.{pts,elem} with cut_dup52.npy (merged-mesh
node of every cut-mesh node). Checks, re-done at the end of step 2 (8.2): no node shared inside the split region; every
graph edge that would cross the cut at either stencil radius (2-ring: tet edges and graph distance 2 up to 3.5 mm; 3-ring
fallback of R4.2: graph distance 2-3 up to 5.25 mm) found by a segment-triangle test against the split faces, listed for
removal (cut52_edges_removed.npz in runs/), and the cut graph re-tested with them removed; contact areas after 2c-2d;
connectivity (components of the cut mesh and of its excitable part, and whether each holds a v5.1 network junction node).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/cut52.py landmarks|apply [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                           # noqa: E402
from common import boundary_faces                                            # noqa: E402

SHARE = 12.7 / 26.9            # D14, Jakiel 2025 Table 1 (derived 0.472)


def rv_cavity_graph(P, E, tag):
    bf, own = boundary_faces(E)
    fe = np.vstack([np.sort(bf[:, [0, 1]], 1), np.sort(bf[:, [1, 2]], 1), np.sort(bf[:, [0, 2]], 1)])
    fid = np.tile(np.arange(len(bf)), 3); key = fe[:, 0] * (1 << 21) + fe[:, 1]
    o = np.argsort(key); ks = key[o]; fs = fid[o]; sm = ks[1:] == ks[:-1]
    Gf = coo_matrix((np.ones(sm.sum()), (fs[:-1][sm], fs[1:][sm])), shape=(len(bf), len(bf)))
    _, lab = connected_components(Gf, directed=False)
    comp = [k for k in np.unique(lab) if {2, 8, 10} <= set(np.unique(tag[own[lab == k]]).tolist())]
    rvf = bf[(lab == comp[0]) & np.isin(tag[own], G.RV_GROUP + [29])]
    rn = np.unique(rvf)
    loc = np.full(len(P), -1); loc[rn] = np.arange(len(rn))
    ed = np.unique(np.sort(np.vstack([rvf[:, [0, 1]], rvf[:, [1, 2]], rvf[:, [0, 2]]]), 1), axis=0)
    A = coo_matrix((np.ones(len(ed)), (loc[ed[:, 0]], loc[ed[:, 1]])), shape=(len(rn), len(rn))).tocsr(); A = A + A.T
    A2 = (A @ A + A).tocoo(); mk = A2.row < A2.col
    e2 = np.c_[A2.row[mk], A2.col[mk]]
    w = np.linalg.norm(P[rn[e2[:, 0]]] - P[rn[e2[:, 1]]], axis=1)
    G2 = coo_matrix((np.r_[w, w], (np.r_[e2[:, 0], e2[:, 1]], np.r_[e2[:, 1], e2[:, 0]])), shape=(len(rn), len(rn))).tocsr()
    return rn, loc, G2


def landmarks(h):
    P, E, tag = G.load_full(h)
    pv, prec = G.pulmonary_frame(P, E, tag)
    rn, loc, G2 = rv_cavity_graph(P, E, tag)
    p100 = pv.ring_point(0.0)
    # the mid-plane ring lies where the disc meets the wall, inside the solid; the RV cavity surface ends at the disc's
    # ventricular face. The surface path runs to the cavity node on the disc rim nearest the 100 % point (p_top), and the
    # straight rise from there along the wall to the mid-plane ring is added to the span.
    rim = np.intersect1d(rn, pv.contact)
    rim = rim[np.abs((pv.theta(P[rim]) + 180) % 360 - 180) <= 10]
    p_top = int(rim[np.argmin(np.linalg.norm(P[rim] - P[p100], axis=1))])
    rise = float(np.linalg.norm(P[p_top] - P[p100]))
    tvn = np.intersect1d(np.unique(E[tag == 8]), rn)
    tv_sup = int(tvn[np.argmin(cKDTree(P[pv.nodes]).query(P[tvn])[0])])
    hTA = float(pv.h(P[tv_sup])[0])
    q = P[p100] - (pv.h(P[p100])[0] - hTA) * pv.n
    post_side = rn[np.abs((pv.theta(P[rn]) + 180) % 360 - 180) <= 60]
    p0 = int(post_side[np.argmin(np.linalg.norm(P[post_side] - q, axis=1))])
    d, pr = dijkstra(G2, indices=loc[p0], return_predecessors=True)
    surf_len = float(d[loc[p_top]])
    path = [loc[p_top]]
    while path[-1] != loc[p0]:
        path.append(pr[path[-1]])
    path = list(rn[np.array(path[::-1])]) + [p100]
    path = np.array(path)
    sp = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[path], axis=0), axis=1))]
    span = float(sp[-1])

    def at(s_):
        s_ = float(np.clip(s_, 0, sp[-1]))
        i = int(np.searchsorted(sp, s_))
        i = min(max(i, 1), len(sp) - 1)
        t = (s_ - sp[i - 1]) / max(sp[i] - sp[i - 1], 1e-12)
        X = P[path[i - 1]] + t * (P[path[i]] - P[path[i - 1]])
        return X, float(pv.h(X)[0])
    cand = {'D14 47.2 % of the span (primary)': SHARE * span, '07:30 rule 37.3 % of the span': 0.373 * span,
            'D6 12.7 mm above 0 %': 12.7, '15.3 mm below the ring': span - 15.3}
    heights = {}
    for k, s_ in cand.items():
        X, hh = at(s_)
        heights[k] = {'distance_from_0pct_mm': round(s_, 2), 'clipped_to_span': bool(s_ < 0 or s_ > span),
                      'height_above_pv_mid_plane_mm': round(hh, 3), 'point_mm': X.round(3).tolist()}
    rec = {'heart': h, 'pulmonary_frame': prec, 'node_100pct (full mesh)': p100, 'node_0pct (full mesh)': p0,
           'tv_superior_node': tv_sup, 'tricuspid_level_height_mm': round(hTA, 3),
           'height_100pct_mm': round(float(pv.h(P[p100])[0]), 3), 'height_0pct_mm': round(float(pv.h(P[p0])[0]), 3),
           'cavity_rim_node_below_the_ring (p_top)': p_top, 'height_p_top_mm': round(float(pv.h(P[p_top])[0]), 3),
           'span_parts_mm': {'surface path 0 % -> p_top': round(surf_len, 3), 'rise p_top -> mid-plane ring': round(rise, 3)},
           'posterior_span_mm': round(span, 3), 'span_vs_Jakiel_sd': round((span - 26.9) / 6.5, 2),
           'path_nodes': int(len(path)), 'candidates': heights,
           'split_height_mm': heights['D14 47.2 % of the span (primary)']['height_above_pv_mid_plane_mm']}
    return rec, pv


def split(Pb, Eb, tb, pv_h, hsplit):
    """Faces of the LV-group / RV-group interface at or above hsplit are split; returns the cut mesh and a report."""
    fa, a, b = G.interfaces(Eb, tb)
    lvA, rvA = np.isin(tb[a], G.LV_GROUP), np.isin(tb[a], G.RV_GROUP)
    lvB, rvB = np.isin(tb[b], G.LV_GROUP), np.isin(tb[b], G.RV_GROUP)
    lr = (lvA & rvB) | (rvA & lvB)
    F = fa[lr]
    hc = pv_h(Pb[F].mean(1))
    sp = hc >= hsplit
    Fs, Ff = F[sp], F[~sp]
    split_nodes = np.setdiff1d(np.unique(Fs), np.unique(Ff))
    front = np.intersect1d(np.unique(Fs), np.unique(Ff))
    N = len(Pb)
    dup = np.full(N, -1, np.int64); dup[split_nodes] = N + np.arange(len(split_nodes))
    Ec = Eb.copy()
    rvel = np.isin(tb, G.RV_GROUP)
    sub = Ec[rvel]
    m = dup[sub] >= 0
    sub[m] = dup[sub[m]]
    Ec[rvel] = sub
    Pc = np.vstack([Pb, Pb[split_nodes]])
    # checks: no node shared across the split faces; septal part still fused; one connected mesh
    lvn = np.unique(Ec[np.isin(tb, G.LV_GROUP)]); rvn = np.unique(Ec[rvel])
    shared = np.intersect1d(lvn, rvn)
    shared_in_split = np.intersect1d(shared, split_nodes)
    n = len(Pc)
    r = np.r_[Ec[:, 0], Ec[:, 0], Ec[:, 0]]; c = np.r_[Ec[:, 1], Ec[:, 2], Ec[:, 3]]
    ncomp, _ = connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)), directed=False)
    fa2, a2, b2 = G.interfaces(Ec, tb)
    lr2 = (np.isin(tb[a2], G.LV_GROUP) & np.isin(tb[b2], G.RV_GROUP)) | (np.isin(tb[a2], G.RV_GROUP) & np.isin(tb[b2], G.LV_GROUP))
    still = fa2[lr2]
    hst = pv_h(Pc[still].mean(1)) if len(still) else np.zeros(0)
    still_above = int((hst >= hsplit + 0.5).sum())                # beyond half an element above the split height
    front_faces = int(((hst >= hsplit) & (hst < hsplit + 0.5)).sum())  # slivers at the front, all three nodes shared
    # 2-ring check: node pairs at graph distance 2 joining an LV-only and an RV-only node through a split node
    rep = {'lv_rv_interface_faces': int(len(F)), 'lv_rv_interface_area_mm2': round(float(G.tri_area(Pb, F).sum()), 2),
           'split_faces': int(len(Fs)), 'split_area_mm2 (contact area cut)': round(float(G.tri_area(Pb, Fs).sum()), 2),
           'fused_faces_below': int(len(Ff)), 'fused_area_mm2': round(float(G.tri_area(Pb, Ff).sum()), 2),
           'duplicated_nodes': int(len(split_nodes)), 'front_nodes_kept_shared': int(len(front)),
           'interface_pairs_split': {f'{int(x)}-{int(y)}': int(k) for (x, y), k in zip(*np.unique(np.sort(np.c_[tb[a][lr][sp], tb[b][lr][sp]], 1), axis=0, return_counts=True))} if sp.any() else {},
           'check_shared_nodes_inside_split_region': int(len(shared_in_split)),
           'check_lv_rv_faces_still_shared_more_than_0.5mm_above_split_height': still_above,
           'front_faces_still_shared_within_0.5mm_of_split_height': front_faces,
           'check_septal_component_fused (faces below kept)': int(len(Ff)) > 0,
           'check_connected_components_of_cut_mesh': int(ncomp),
           'split_faces_height_range_mm': [round(float(hc[sp].min()), 2), round(float(hc[sp].max()), 2)] if sp.any() else None}
    return Pc, Ec, dup, rep


def run_landmarks(hs):
    for h in hs:
        t0 = time.time()
        rec, pv = landmarks(h)
        Pb, Eb, tb, nod = G.load_biv(h)
        P, E, tag = G.load_full(h)
        pv_h = lambda X: pv.h(X)
        out = {'landmarks': rec, 'v51_mesh': {}}
        for k, c in rec['candidates'].items():
            _, _, _, rep = split(Pb, Eb, tb, pv_h, c['height_above_pv_mid_plane_mm'])
            out['v51_mesh'][k] = {kk: rep[kk] for kk in ('split_faces', 'split_area_mm2 (contact area cut)', 'fused_area_mm2', 'duplicated_nodes')}
        _, _, _, rep = split(Pb, Eb, tb, pv_h, rec['split_height_mm'])
        out['v51_mesh_D14_cut'] = rep
        # contact of the infundibulum with the aortic root (tag 2 / tag 5, full mesh), reported before cutting
        fa, a, b = G.interfaces(E, tag)
        k25 = np.isin(tag[a], [2, 28]) & (tag[b] == 5) | (tag[a] == 5) & np.isin(tag[b], [2, 28])
        out['rv_aortic_root_contact_area_mm2 (full mesh, before 2c)'] = round(float(G.tri_area(P, fa[k25]).sum()), 2)
        out['wall_s'] = round(time.time() - t0, 1)
        G.dump(out, os.path.join(HERE, f'cut52_{h}.json'))
        L = rec
        print(h, f"span {L['posterior_span_mm']} mm, split at {L['split_height_mm']} mm (0 % at {L['height_0pct_mm']}, 100 % at {L['height_100pct_mm']}),",
              f"split {rep['split_faces']} faces / {rep['split_area_mm2 (contact area cut)']} mm2, fused {rep['fused_area_mm2']} mm2,",
              f"dup {rep['duplicated_nodes']}, components {rep['check_connected_components_of_cut_mesh']}, {out['wall_s']} s", flush=True)


def read_mesh(base):
    with open(base + '.pts') as fh:
        n = int(fh.readline()); P = np.loadtxt(fh, max_rows=n) / 1e3
    with open(base + '.elem') as fh:
        n = int(fh.readline())
        E = np.loadtxt(fh, max_rows=n, usecols=(1, 2, 3, 4, 5), dtype=np.int64)
    return P, E[:, :4], E[:, 4]


def adjacency(E, N):
    pr = np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))])
    pr.sort(axis=1)
    k = np.unique(pr[:, 0] * N + pr[:, 1])
    i, j = k // N, k % N
    return coo_matrix((np.ones(2 * len(i), bool), (np.r_[i, j], np.r_[j, i])), shape=(N, N)).tocsr()


def seg_hits(A, B, T0, T1, T2, eps=1e-9):
    """Segment AB meets triangle T (Moller-Trumbore; edges of the triangle included, the segment's own ends excluded)."""
    d = B - A; e1 = T1 - T0; e2 = T2 - T0
    p = np.cross(d, e2); det = np.einsum('ij,ij->i', e1, p)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    s = A - T0
    u = np.einsum('ij,ij->i', s, p) * inv
    q = np.cross(s, e1)
    v = np.einsum('ij,ij->i', d, q) * inv
    t = np.einsum('ij,ij->i', e2, q) * inv
    return ok & (u >= -eps) & (v >= -eps) & (u + v <= 1 + eps) & (t > 1e-6) & (t < 1 - 1e-6)


def crossing_edges(Pc, Ec, tb, Fs, crack, near_mm=6.75):
    """Graph pairs of the cut mesh (graph distance 1-3, up to 5.25 mm) near the split faces that jump the cut.

    A pair jumps the cut if (a) it joins an LV-only node to an RV-only node and one of them lies on the cut itself (a split
    node's LV copy or its RV duplicate: such a segment leaves the cut face straight into the other side, or lies in the
    cut, or has zero length between the two copies of one node), or (b) its segment meets a split face (edges included)
    away from its own ends. Shared (front) nodes are on both sides, so their pairs are tested by (b) only."""
    N = len(Pc)
    A = adjacency(Ec, N)
    lvn = np.zeros(N, bool); lvn[np.unique(Ec[np.isin(tb, G.LV_GROUP)])] = True
    rvn = np.zeros(N, bool); rvn[np.unique(Ec[np.isin(tb, G.RV_GROUP)])] = True
    cls = np.where(lvn & rvn, 2, np.where(lvn, 0, 1))
    oncut = np.zeros(N, bool); oncut[crack] = True
    S = np.unique(np.concatenate(cKDTree(Pc).query_ball_point(Pc[np.unique(Fs)], near_mm)))
    B1 = A[S].astype(np.int32)
    B2 = (B1 @ A.astype(np.int32)).astype(bool).astype(np.int32)
    B3 = (B2 @ A.astype(np.int32)).astype(bool)
    B1, B2 = B1.astype(bool), B2.astype(bool)
    c3 = B3.tocoo(); i = S[c3.row]; j = c3.col
    m = (i < j) | ~np.isin(j, S)                                      # each unordered pair once
    i, j = i[m], j[m]
    i, j = np.minimum(i, j), np.maximum(i, j)
    key = np.unique(i * N + j); i, j = key // N, key % N
    L = np.linalg.norm(Pc[i] - Pc[j], axis=1)
    keep = (L <= 5.25) & (i != j)
    i, j, L = i[keep], j[keep], L[keep]
    # graph distance: 1 (tet edge), 2, 3
    a1 = np.asarray(A[i, j]).ravel().astype(bool)
    rowpos = np.full(N, -1); rowpos[S] = np.arange(len(S))
    ri = np.where(rowpos[i] >= 0, i, j); rj = np.where(rowpos[i] >= 0, j, i)
    a2 = np.asarray(B2[rowpos[ri], rj]).ravel()
    dist = np.where(a1, 1, np.where(a2, 2, 3))
    test = ~(((cls[i] == 0) & (cls[j] == 0)) | ((cls[i] == 1) & (cls[j] == 1)))
    ti, tj = i[test], j[test]
    tree = cKDTree(Pc[Fs].mean(1))
    rad = 2.625 + float(np.max(np.linalg.norm(Pc[Fs] - Pc[Fs].mean(1)[:, None], axis=2)))
    nb = tree.query_ball_point(0.5 * (Pc[ti] + Pc[tj]), rad)
    cnt = np.array([len(x) for x in nb]); pi = np.repeat(np.arange(len(ti)), cnt)
    fi = np.concatenate([np.asarray(x, np.int64) for x in nb]) if cnt.sum() else np.zeros(0, np.int64)
    hit = np.zeros(len(ti), bool)
    for c0 in range(0, len(pi), 2_000_000):
        sl = slice(c0, c0 + 2_000_000)
        h = seg_hits(Pc[ti[pi[sl]]], Pc[tj[pi[sl]]], Pc[Fs[fi[sl], 0]], Pc[Fs[fi[sl], 1]], Pc[Fs[fi[sl], 2]])
        hit[np.unique(pi[sl][h])] = True
    opp = ((cls[ti] == 0) & (cls[tj] == 1)) | ((cls[ti] == 1) & (cls[tj] == 0))
    hit_a = opp & (oncut[ti] | oncut[tj])
    hit_b = hit.copy()
    hit = hit_a | hit_b
    di, Li = dist[test], L[test]
    ring2 = (di == 1) | ((di == 2) & (Li <= 3.5))
    ring3 = di <= 3                                                    # graph distance <= 3, <= 5.25 mm
    pair_cls = np.char.add(np.char.add(cls[ti].astype(str), '-'), cls[tj].astype(str))
    rep = {'near_nodes': int(len(S)), 'pairs_up_to_5.25mm_distance_le3': int(len(i)), 'pairs_tested (not both LV-only or both RV-only)': int(len(ti)),
           'crossing_tet_edges (must be 0)': int((hit & (di == 1)).sum()),
           'crossing_2ring_edges': int((hit & ring2).sum()), 'crossing_3ring_edges': int((hit & ring3).sum()),
           'of_which_(a)_LV_to_RV_with_an_end_on_the_cut (2-ring, 3-ring)': [int((hit_a & ring2).sum()), int((hit_a & ring3).sum())],
           'of_which_(b)_segment_meets_a_split_face (2-ring, 3-ring)': [int((hit_b & ring2).sum()), int((hit_b & ring3).sum())],
           'zero_length_pairs_between_the_two_copies_of_a_node': int((hit & (Li < 1e-9)).sum()),
           'crossing_by_side (0 LV-only, 1 RV-only, 2 shared)': {k: int(((pair_cls == k) & hit).sum()) for k in np.unique(pair_cls[hit])} if hit.any() else {}}
    rem = {'i': ti[hit], 'j': tj[hit], 'graph_distance': di[hit], 'length_mm': Li[hit], 'in_2ring': ring2[hit]}
    return rep, rem, A, cls


def detour(Pc, A, Ec, tb, Fs, dupm, split_nodes, rem, cls, sample=200, radius=30.0):
    """Shortest 2-ring path (Euclidean lengths, crossing edges removed) from LV-side split nodes to their RV duplicates."""
    N = len(Pc)
    near = np.unique(np.concatenate(cKDTree(Pc).query_ball_point(Pc[np.unique(Fs)], radius)))
    loc = np.full(N, -1); loc[near] = np.arange(len(near))
    As = A[near][:, near].tocsr().astype(np.int32)
    A2 = ((As @ As).astype(bool).astype(np.int32) - As.astype(bool).astype(np.int32)).tocoo()
    m2 = (A2.data > 0) & (A2.row < A2.col)
    e1 = np.array(sparse_triu(As)).T
    e2 = np.c_[A2.row[m2], A2.col[m2]]
    e2 = e2[np.linalg.norm(Pc[near[e2[:, 0]]] - Pc[near[e2[:, 1]]], axis=1) <= 3.5]
    e = np.vstack([e1, e2])
    rk = set(zip(np.minimum(rem['i'], rem['j']).tolist(), np.maximum(rem['i'], rem['j']).tolist()))
    gi, gj = near[e[:, 0]], near[e[:, 1]]
    keep = np.array([(min(a, b), max(a, b)) not in rk for a, b in zip(gi.tolist(), gj.tolist())])
    e = e[keep]
    w = np.linalg.norm(Pc[near[e[:, 0]]] - Pc[near[e[:, 1]]], axis=1)
    Gs = coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(len(near), len(near))).tocsr()
    rng = np.random.default_rng(0)
    sn = rng.choice(split_nodes, min(sample, len(split_nodes)), replace=False)
    d = dijkstra(Gs, indices=loc[sn])
    to = d[np.arange(len(sn)), loc[dupm[sn]]]
    fin = np.isfinite(to)
    return {'sampled_split_nodes': int(len(sn)), 'path_LV_copy_to_RV_copy_mm (straight distance 0)': {
        'min': round(float(to[fin].min()), 2) if fin.any() else None, 'median': round(float(np.median(to[fin])), 2) if fin.any() else None,
        'max': round(float(to[fin].max()), 2) if fin.any() else None}, 'no_path_within_30mm_region': int((~fin).sum()),
        'edges_removed_in_this_graph': int((~keep).sum())}


def sparse_triu(As):
    c = As.tocoo(); m = c.row < c.col
    return c.row[m], c.col[m]


def run_apply(hs):
    for h in hs:
        t0 = time.time()
        L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
        hsplit = L['split_height_mm']
        P, E, tag = G.load_full(h)
        pv, _ = G.pulmonary_frame(P, E, tag)
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
        Pm, Em, tm = read_mesh(os.path.join(V, 'biv52'))
        Pc, Ec, dup, rep = split(Pm, Em, tm, pv.h, hsplit)
        out = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'split_height_mm (landmark stage, D14)': hsplit,
               'merged_mesh': {'nodes': int(len(Pm)), 'elements': int(len(Em))}, 'cut_mesh_nodes': int(len(Pc)), 'merged_mesh_D14_cut': rep}
        # which split faces: rebuild them as in split()
        fa, a, b = G.interfaces(Em, tm)
        lr = (np.isin(tm[a], G.LV_GROUP) & np.isin(tm[b], G.RV_GROUP)) | (np.isin(tm[a], G.RV_GROUP) & np.isin(tm[b], G.LV_GROUP))
        F = fa[lr]; Fs = F[pv.h(Pm[F].mean(1)) >= hsplit]
        split_nodes = np.where(dup >= 0)[0]
        dupm = np.arange(len(Pc)); dupm[split_nodes] = dup[split_nodes]           # LV copy -> RV copy
        cr, rem, A, cls = crossing_edges(Pc, Ec, tm, Fs, np.r_[split_nodes, dup[split_nodes]])
        out['graph_edges_crossing_the_cut'] = cr
        out['detour_check'] = detour(Pc, A, Ec, tm, Fs, dupm, split_nodes, rem, cls)
        # contact areas after 2c-2d
        z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
        tag2 = tag.copy(); tag2[z['crescent_elements']] = 1; tag2[z['sleeve_elements']] = 2
        fa2, a2, b2 = G.interfaces(E, tag2)
        k25 = np.isin(tag2[a2], [2, 28]) & (tag2[b2] == 5) | (tag2[a2] == 5) & np.isin(tag2[b2], [2, 28])
        k15 = np.isin(tag2[a2], [1, 25, 29]) & (tag2[b2] == 5) | (tag2[a2] == 5) & np.isin(tag2[b2], [1, 25, 29])
        out['contact_after_2c_2d_mm2'] = {'RV-aortic root (tags 2/28 - 5)': round(float(G.tri_area(P, fa2[k25]).sum()), 2),
                                          'LV-RV interface on the merged mesh': rep['lv_rv_interface_area_mm2'],
                                          'LV-RV interface on the v5.1 mesh (landmark stage)': json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['v51_mesh_D14_cut']['lv_rv_interface_area_mm2'],
                                          'LV-aortic root (tags 1/25/29 - 5), for reference': round(float(G.tri_area(P, fa2[k15]).sum()), 2)}
        # connectivity: the cut mesh, and its excitable part (fibrous-layer nodes removed)
        N = len(Pc)
        ncomp, lab = connected_components(A, directed=False)
        fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
        fibc = np.concatenate([fib, dup[fib][dup[fib] >= 0]]) if len(fib) else fib
        keepn = np.ones(N, bool); keepn[fibc] = False
        Ax = A[keepn][:, keepn]
        nx, labx = connected_components(Ax, directed=False)
        net = np.load(os.path.join(G.REPO, 'data', 'biv', h, 'purkinje_v51', 'network_v51.npz'))
        pmj_mesh = net['nodes'][net['pmj']]
        pmj_c = np.concatenate([pmj_mesh, dup[pmj_mesh][dup[pmj_mesh] >= 0]])
        idx = np.full(N, -1); idx[np.where(keepn)[0]] = np.arange(keepn.sum())
        has = np.zeros(nx, bool); pc = idx[pmj_c]; has[labx[pc[pc >= 0]]] = True
        sizes = np.bincount(labx)
        out['connectivity'] = {'components_cut_mesh (tet edges)': int(ncomp),
                               'fibrous_layer_nodes (non-excitable, both copies)': int(len(fibc)),
                               'components_excitable': int(nx), 'component_sizes_nodes': sorted(sizes.tolist(), reverse=True)[:10],
                               'components_without_a_v51_junction_node': int((~has).sum()),
                               'nodes_in_components_without_a_junction': int(sizes[~has].sum()),
                               'acceptance (every excitable component reachable from a network junction)': bool(has.all())}
        # write the cut mesh
        with open(os.path.join(V, 'biv52cut.pts'), 'w') as fh:
            fh.write(f'{len(Pc)}\n'); np.savetxt(fh, Pc * 1e3, fmt='%.6f')
        with open(os.path.join(V, 'biv52cut.elem'), 'w') as fh:
            fh.write(f'{len(Ec)}\n'); np.savetxt(fh, np.c_[Ec, tm], fmt='Tt %d %d %d %d %d')
        src = np.arange(len(Pc)); src[len(Pm):] = split_nodes
        np.save(os.path.join(V, 'cut_dup52.npy'), src)                         # merged-mesh node of every cut-mesh node
        np.savez(os.path.join(G.RUN, h, 'cut52_edges_removed.npz'), **rem)
        out['files'] = {'cut_mesh': os.path.relpath(os.path.join(V, 'biv52cut'), G.REPO),
                        'pts_sha256': G.sha256(os.path.join(V, 'biv52cut.pts')), 'elem_sha256': G.sha256(os.path.join(V, 'biv52cut.elem')),
                        'removed_edges': os.path.relpath(os.path.join(G.RUN, h, 'cut52_edges_removed.npz'), G.REPO)}
        out['wall_s'] = round(time.time() - t0, 1)
        G.dump(out, os.path.join(HERE, f'cut52_apply_{h}.json'))
        print(h, json.dumps({k: out[k] for k in ('merged_mesh_D14_cut', 'graph_edges_crossing_the_cut', 'detour_check', 'contact_after_2c_2d_mm2', 'connectivity')}), flush=True)


if __name__ == '__main__':
    st = sys.argv[1]
    {'landmarks': run_landmarks, 'apply': run_apply}[st](sys.argv[2:] or G.HEARTS)
