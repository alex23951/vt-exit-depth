"""v5.1 conduction system (v5.1 brief Step 4.4, decisions E and B; audit F05, F06, F19): class-based bundle speeds and a
distal Purkinje speed set from a straight-line rule, on the unchanged v5 network topology (data/biv/<H>/purkinje/
network.npz, network v3; 6G8DD8S5 keeps its left-bundle cut, network_intact.npz used only to classify).

E1  No speed is set from a timing target or per heart. The v5 Durrer-offset calibration (sims/biv_model/14_purkinje.py
    build(), lines 331-346) is never called here; v5.1 speeds come only from CLASS_SPEED (constants, the same in every
    heart), the E4 tortuosity rule and the P5 straight-line rule.
E2  Classes, from the v5 network's insulated paths (landmarks in summary.json; v5 per-path speeds tell copies apart):
    HIS       root to the LB/RB split. The v5 root (His point under the membranous septum) IS the split: no edges.
    RB        His -> RV septum -> moderator-band insertion.
    LB_TRUNK  His -> LB branching point, plus every division edge shared by >= 2 His -> Durrer-site paths.
    FASCICLE  edges on exactly one His -> Durrer-site path (Durrer site = the division's first distal root).
    DISTAL    all else: RB apical branch, divisions beyond the Durrer sites, root links, distal trees.
E3  HIS, RB, LB_TRUNK 1.5 m/s (Kupersmith 1973); FASCICLE 2.0 m/s (FASCICLE_SPEED, Alex 15 Oct 2026 08:31:01 UTC);
    DISTAL v_edge (P5).
E4  Each non-distal segment polyline resampled at 0.5 mm; at each point the arc length s whose chord is 10 mm;
    R10 = median(s / 10 mm); R10 <= 1.10: nominal speed, else nominal x R10 (flagged). Segments with no 10 mm chord:
    arc / chord.
E5-E7 Junction delays 4 ms antegrade, 2 ms retrograde (unchanged, stored in params); 6G8DD8S5 cut unchanged; no scaling.
E8  Guard: every edge speed = its class value (x R10 if flagged) within 1e-9, else abort; run after P5 on the final
    network (all five classes).
F19 Report: exact duplicate node pairs; v5 shared division edges; de-duplication never changes a time in v5.1.
E9  Analytic His -> Durrer sites and moderator band, Durrer spread, His -> first muscle (earliest junction + 4 ms), also
    with HIS / RB / LB_TRUNK at 1.27 and 1.8 m/s. Written before any v5.1 beat.
P2-P8 Distal roots = non-distal nodes (not the His) where a DISTAL edge leaves; distal-only multi-source Dijkstra at
    v0 = 2.0 m/s; A_j = D_j / t_j over junctions with D_j >= 10 mm (LV and RV pooled); v_edge = v0 x 2.0 / median(A_j),
    rounded to 0.01 m/s; P6 same on the de-duplicated distal graph within 1 %; P7 median A_j at v_edge = 2.00 +- 0.02;
    P8 LV septal junction pairs 15-25 mm apart in one subtree, median D / |dt|.
Graphs: duplicate node pairs keep the fastest copy (as v5's net_graph); zero-length links weigh 1e-6 ms.
Outputs: data/biv/<H>/purkinje_v51/network_v51.npz (+ network_intact_v51.npz for the cut heart),
    params/params_network_<H>_v51.json, analysis/v51_2026-10-15/04_build/network51_<H>.json.
Usage (repo root, venv): HEART=<H> python -B analysis/v51_2026-10-15/04_build/network51.py build
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
VERSION = 'v51-network-1'
CLASSES = ('HIS', 'RB', 'LB_TRUNK', 'FASCICLE', 'DISTAL')
CLASS_SPEED = {'HIS': 1.5, 'RB': 1.5, 'LB_TRUNK': 1.5, 'FASCICLE': 2.0}     # m/s = mm/ms
V0 = 2.0                     # distal straight-line target and P3 trial speed (m/s)
R10_LIMIT, CHORD_MM, STEP_MM = 1.10, 10.0, 0.5
D_MIN_MM = 10.0
D_ANT, D_RET = 4.0, 2.0      # junction delays, unchanged (14_purkinje.py P['d_ant_ms'], P['d_ret_ms'])
CUT_HEARTS = ('6G8DD8S5',)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def read_pts(h):
    with open(os.path.join(REPO, 'data', 'biv', h, 'biv.pts')) as fh:
        n = int(fh.readline())
        return np.loadtxt(fh, max_rows=n) / 1e3


def graph(n, e, w, extra=None):
    """Undirected graph on n (+1 spare) nodes; duplicate pairs keep the smallest weight."""
    a = np.sort(e, axis=1)
    key, inv = np.unique(a, axis=0, return_inverse=True)
    wm = np.full(len(key), np.inf)
    np.minimum.at(wm, inv.ravel(), np.maximum(w, 1e-6))
    return coo_matrix((np.r_[wm, wm], (np.r_[key[:, 0], key[:, 1]], np.r_[key[:, 1], key[:, 0]])), shape=(n, n)).tocsr()


def path_nodes(pred, src, dst):
    out = [dst]
    while out[-1] != src:
        p = pred[out[-1]]
        if p < 0:
            raise RuntimeError(f'no path {src} -> {dst}')
        out.append(p)
    return out[::-1]


def r10(xyz):
    """E4 on a polyline (k, 3) in mm: (arc, chord, R10, method)."""
    seg = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    arc, chord = float(seg.sum()), float(np.linalg.norm(xyz[-1] - xyz[0]))
    s = np.r_[0.0, np.cumsum(seg)]
    q = np.arange(0.0, arc + 1e-9, STEP_MM)
    P = np.stack([np.interp(q, s, xyz[:, c]) for c in range(3)], 1)
    ratios = []
    for i in range(len(P)):
        d = np.r_[0.0, np.linalg.norm(P[i + 1:] - P[i], axis=1)]
        k = np.flatnonzero(d >= CHORD_MM)
        if len(k):                                 # arc at the first 10 mm chord, interpolated between resampled points
            j = k[0]
            sj = q[i + j - 1] + (CHORD_MM - d[j - 1]) / (d[j] - d[j - 1]) * (q[i + j] - q[i + j - 1])
            ratios.append((sj - q[i]) / CHORD_MM)
    if ratios:
        return arc, chord, float(np.median(ratios)), f'median over {len(ratios)} points'
    return arc, chord, arc / max(chord, 1e-9), 'arc / chord (no 10 mm chord)'


def build():
    h = os.environ['HEART']
    t0 = time.time()
    B = os.path.join(REPO, 'data', 'biv', h, 'purkinje')
    pts = read_pts(h)
    netf = os.path.join(B, 'network.npz')
    cut = h in CUT_HEARTS
    full = dict(np.load(os.path.join(B, 'network_intact.npz') if cut else netf))
    net = dict(np.load(netf))
    summ = json.load(open(os.path.join(B, 'summary.json')))
    P5 = json.loads(str(net['params']))
    assert summ['network_version'] == 'v3' and np.array_equal(full['nodes'], net['nodes']) and np.array_equal(full['pmj'], net['pmj'])
    nodes, kind = full['nodes'], full['kind']
    n = len(nodes)
    X = pts[nodes]
    E, S = full['edges'].astype(np.int64), full['edge_speed']
    L = np.linalg.norm(X[E[:, 0]] - X[E[:, 1]], axis=1)
    isprox = (kind[E[:, 0]] == 'proximal') & (kind[E[:, 1]] == 'proximal')
    prox_id = {int(m): i for i, m in enumerate(nodes) if kind[i] == 'proximal'}
    lm = summ['landmarks']
    his, Bn, mb_end = prox_id[lm['his']], prox_id[lm['lbb_branch']], prox_id[lm['mb_end']]
    assert his == int(full['his'])
    ends = {k: prox_id[v[0]] for k, v in lm['fascicle_ends'].items()}
    uniq = np.unique(S[isprox])
    near = lambda v: float(uniq[np.argmin(np.abs(uniq - v))])
    vs = {k: near(v) for k, v in summ['proximal_speed_m_s'].items()}
    # nodes carrying a root link (proximal node joined to a distal node at the same mesh node)
    link = isprox == False                                          # noqa: E712
    link &= (kind[E[:, 0]] == 'proximal') ^ (kind[E[:, 1]] == 'proximal')
    rooted = set(np.where(kind[E[link, 0]] == 'proximal', E[link, 0], E[link, 1]).tolist())

    def sub_path(a, b, speed):
        m = isprox & np.isclose(S, speed, rtol=0, atol=1e-9)
        G = graph(n, E[m], L[m])
        _, pred = dijkstra(G, indices=a, return_predecessors=True)
        return path_nodes(pred, a, b)

    pair = lambda u, v: (min(u, v), max(u, v))
    def sub_path_any(a, b, name):
        """summary.json rounds speeds to 0.01 m/s; try every stored speed that rounds to it (7D98EVAR: posterior 2.9058
        and RB 2.9101 both round to 2.91) and keep the one that joins a to b."""
        for c in sorted(uniq[np.abs(uniq - summ['proximal_speed_m_s'][name]) <= 0.0051], key=lambda v: abs(v - summ['proximal_speed_m_s'][name])):
            try:
                path = sub_path(a, b, c)
                vs[name] = float(c)
                return path
            except RuntimeError:
                continue
        raise RuntimeError(f'no {name} path')

    lbb = sub_path_any(his, Bn, 'lbb')
    rbb = sub_path_any(his, mb_end, 'rbb')
    div, site = {}, {}
    for k, e_ in ends.items():
        p = sub_path_any(Bn, e_, f'division_{k}')
        i = next(i for i, u in enumerate(p) if i > 0 and u in rooted)  # Durrer site: first distal root on the division
        div[k], site[k] = p[:i + 1], p[i]
    dpairs = {k: {pair(u, v) for u, v in zip(p[:-1], p[1:])} for k, p in div.items()}
    count = {}
    for s_ in dpairs.values():
        for q in s_:
            count[q] = count.get(q, 0) + 1
    shared = {q for q, c in count.items() if c >= 2}
    lbb_p = {pair(u, v) for u, v in zip(lbb[:-1], lbb[1:])}
    rb_p = {pair(u, v) for u, v in zip(rbb[:-1], rbb[1:])}
    cls = np.full(len(E), 'DISTAL', dtype=object)
    fasc_of = np.full(len(E), '', dtype=object)
    for i in np.where(isprox)[0]:
        q = pair(int(E[i, 0]), int(E[i, 1]))
        if q in rb_p and np.isclose(S[i], vs['rbb'], atol=1e-9):
            cls[i] = 'RB'
        elif q in lbb_p and np.isclose(S[i], vs['lbb'], atol=1e-9):
            cls[i] = 'LB_TRUNK'
        elif q in shared:
            cls[i] = 'LB_TRUNK'
        else:
            for k in div:
                if q in dpairs[k] and np.isclose(S[i], vs[f'division_{k}'], atol=1e-9):
                    cls[i], fasc_of[i] = 'FASCICLE', k
    # E4 segments: RB; LB_TRUNK = LB + the shared prefix of the divisions; one FASCICLE per division (rest of its path)
    pre = 0
    while all(len(p) > pre + 1 for p in div.values()) and len({p[pre + 1] for p in div.values()}) == 1 and \
            all(pair(p[pre], p[pre + 1]) in shared for p in div.values()):
        pre += 1
    trunk_poly = lbb + list(div['anterior'][1:pre + 1])
    segs = {'RB': ('RB', rbb), 'LB_TRUNK': ('LB_TRUNK', trunk_poly)}
    for k, p in div.items():
        segs[f'FASCICLE_{k}'] = ('FASCICLE', p[pre:])
    shared_off_prefix = len(shared - {pair(u, v) for u, v in zip(trunk_poly[:-1], trunk_poly[1:])})
    seg_out, factor = {}, {}
    for nm, (c, p) in segs.items():
        arc, chord, R, how = r10(X[p])
        flag = R > R10_LIMIT
        factor[nm] = R if flag else 1.0
        sp = CLASS_SPEED[c] * factor[nm]
        seg_out[nm] = {'class': c, 'edges': len(p) - 1, 'arc_mm': round(arc, 2), 'chord_mm': round(chord, 2), 'R10': round(R, 4),
                       'R10_method': how, 'flagged_R10_gt_1.10': bool(flag), 'nominal_m_s': CLASS_SPEED[c], 'speed_m_s': sp,
                       'transit_ms': round(arc / sp, 3)}
    seg_out['HIS'] = {'class': 'HIS', 'edges': 0, 'arc_mm': 0.0, 'note': 'the v5 network root (His point on the LV septal endocardium '
                      'below the aortic annulus at the right coronary cusp, under the membranous septum) is the LB/RB split itself'}

    def speeds(v_edge, trunk=None):
        sp = np.full(len(E), np.nan)
        for i in range(len(E)):
            c = cls[i]
            if c == 'DISTAL':
                sp[i] = v_edge
            elif c == 'FASCICLE':
                sp[i] = CLASS_SPEED['FASCICLE'] * factor[f'FASCICLE_{fasc_of[i]}']
            else:
                sp[i] = (trunk or CLASS_SPEED[c]) * factor['RB' if c == 'RB' else 'LB_TRUNK']
        return sp

    # P2-P5: distal roots, distal-only run at v0, straight-line speed
    dmask = cls == 'DISTAL'
    nd_nodes = set(E[~dmask].ravel().tolist())
    roots = sorted({int(u) for u in E[dmask].ravel() if int(u) in nd_nodes and int(u) != his})
    pmj = full['pmj']
    side = np.array(['lv' if kind[j] == 'distal_lv' else 'rv' for j in pmj])

    def distal_run(v, dedup=False):
        e, w = E[dmask], L[dmask] / v
        if dedup:
            key = np.unique(np.sort(e, axis=1), axis=0)
            e, w = key, np.linalg.norm(X[key[:, 0]] - X[key[:, 1]], axis=1) / v
        G = graph(n, e, w)
        dist, _, src = dijkstra(G, indices=roots, min_only=True, return_predecessors=True)
        t, r = dist[pmj], src[pmj]
        D = np.linalg.norm(X[pmj] - X[np.maximum(r, 0)], axis=1)
        ok = np.isfinite(t) & (r >= 0)
        return t, r, D, ok

    t0d, r0d, D, ok = distal_run(V0)
    use = ok & (D >= D_MIN_MM)
    A0 = D[use] / t0d[use]
    v_edge_raw = V0 * 2.0 / float(np.median(A0))
    v_edge = round(v_edge_raw, 2)
    t6, r6, D6, ok6 = distal_run(V0, dedup=True)
    use6 = ok6 & (D6 >= D_MIN_MM)
    v6 = V0 * 2.0 / float(np.median(D6[use6] / t6[use6]))
    p6 = abs(v6 / v_edge_raw - 1) <= 0.01
    t7, r7, D7, ok7 = distal_run(v_edge)
    use7 = ok7 & (D7 >= D_MIN_MM)
    A7 = D7[use7] / t7[use7]
    med7 = float(np.median(A7))
    p7 = abs(med7 - 2.0) <= 0.02
    pos = ok7 & (t7 > 0)
    p7rep = {'median_A_m_s': round(med7, 4), 'IQR': [round(float(np.percentile(A7, 25)), 3), round(float(np.percentile(A7, 75)), 3)],
             'LV_only_median': round(float(np.median(A7[side[use7] == 'lv'])), 3), 'RV_only_median': round(float(np.median(A7[side[use7] == 'rv'])), 3),
             'all_junction_median_no_D_filter': round(float(np.median(D7[pos] / t7[pos])), 3), 'mean': round(float(A7.mean()), 3),
             'ratio_of_sums': round(float(D7[use7].sum() / t7[use7].sum()), 3), 'junctions_used': int(use7.sum()), 'junctions_total': int(len(pmj)),
             'junctions_unreached': int((~ok7).sum())}
    # P8: LV septal junction pairs 15-25 mm apart in one subtree
    phi = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'uvc', 'phi.dat'))
    sept = ok7 & (side == 'lv') & (np.abs(np.degrees(phi[nodes[pmj]])) <= 45.0)
    rat = []
    for root in np.unique(r7[sept]):
        jj = np.where(sept & (r7 == root))[0]
        if len(jj) < 2:
            continue
        a, b = np.triu_indices(len(jj), 1)
        d = np.linalg.norm(X[pmj[jj[a]]] - X[pmj[jj[b]]], axis=1)
        dt = np.abs(t7[jj[a]] - t7[jj[b]])
        m = (d >= 15) & (d <= 25) & (dt > 1e-6)
        rat += list(d[m] / dt[m])
    p8 = {'pairs': len(rat), 'median_D_over_abs_dt_m_s': round(float(np.median(rat)), 3) if rat else None,
          'septal_rule': 'LV junctions with |UVC phi| <= 45 deg (phi centred near the septum, audit F02)'}

    # final speeds, E8 guard
    sp_full = speeds(v_edge)
    expect = {c: CLASS_SPEED.get(c) for c in CLASSES}
    for i in range(len(E)):
        c = cls[i]
        want = v_edge if c == 'DISTAL' else CLASS_SPEED[c] * factor[f'FASCICLE_{fasc_of[i]}' if c == 'FASCICLE' else ('RB' if c == 'RB' else 'LB_TRUNK')]
        if not abs(sp_full[i] - want) <= 1e-9:
            sys.exit(f'E8 guard: edge {i} class {c} speed {sp_full[i]} != {want}')
    counts = {c: int((cls == c).sum()) for c in CLASSES}
    guard = {'E8_pass': True, 'edges_per_class': counts, 'class_values_m_s': expect | {'DISTAL': v_edge},
             'R10_factors': {k: round(v, 4) for k, v in factor.items()}}

    # network as used: the cut heart drops exactly v5's cut edges (the LB, His -> branching point; 14_purkinje.py build)
    is_lbb = isprox & np.array([pair(int(a), int(b)) in lbb_p for a, b in E]) & np.isclose(S, vs['lbb'], atol=1e-9)
    idx_used = np.where(~is_lbb)[0] if cut else np.arange(len(E))
    if not (np.array_equal(E[idx_used], net['edges']) and np.array_equal(S[idx_used], net['edge_speed'])):
        sys.exit('E6: the cut edges differ from v5 network.npz')
    e6 = {'cut': cut, 'removed_edges': int(len(E) - len(idx_used)), 'removed_classes': sorted(set(cls[~np.isin(np.arange(len(E)), idx_used)])),
          'diff_vs_v5_cut': 'empty: the kept edges equal v5 network.npz edge for edge (order and v5 speeds checked)' if cut else 'n/a'}

    # E9 analytic times from the His (network only)
    def his_times(trunk):
        spd = speeds(v_edge, trunk)[idx_used]
        e = E[idx_used]
        G = graph(n, e, L[idx_used] / spd)
        return dijkstra(G, indices=his)
    e9 = {}
    for lab, tr in (('1.5 m/s (v5.1)', None), ('1.27 m/s', 1.27), ('1.8 m/s', 1.8)):
        T = his_times(tr)
        ts = {k: float(T[v]) for k, v in site.items()}
        fin = [v for v in ts.values() if np.isfinite(v)]
        e9[lab] = {'his_to_durrer_site_ms': {k: (round(v, 2) if np.isfinite(v) else 'not reached through the network (left bundle cut)') for k, v in ts.items()},
                   'his_to_moderator_band_end_ms': round(float(T[mb_end]), 2),
                   'durrer_sites_within_5ms_of_earliest': (sum(v - min(fin) <= 5.0 for v in fin) if fin else 0),
                   'durrer_spread_ms': (round(max(fin) - min(fin), 2) if fin else None),
                   'his_to_first_junction_ms': round(float(np.min(T[pmj])), 2),
                   'his_to_first_muscle_ms': round(float(np.min(T[pmj])) + D_ANT, 2),
                   'first_junction_side': side[int(np.argmin(T[pmj]))]}

    # F19: duplicates
    srt = np.sort(E, axis=1)
    key, inv, cnt = np.unique(srt, axis=0, return_inverse=True, return_counts=True)
    inv = inv.ravel()
    dup_pairs = np.where(cnt > 1)[0]
    v5_diff_speed = sum(len(np.unique(np.round(S[inv == k], 9))) > 1 for k in dup_pairs)
    v51_diff_speed = sum(len(np.unique(np.round(sp_full[inv == k], 9))) > 1 for k in dup_pairs)
    Gs = graph(n, E, L / S)                                          # v5 speeds, intact network, fastest copy kept
    Tv5 = dijkstra(Gs, indices=his)
    own = {}
    for k, p in div.items():                                           # each division on its own copies only
        t_own = sum(L[i] / S[i] for i in [next(j for j in range(len(E)) if pair(int(E[j, 0]), int(E[j, 1])) == pair(u, v)
                                                and np.isclose(S[j], vs['lbb'] if pair(u, v) in lbb_p else vs[f'division_{k}'], atol=1e-9))
                                           for u, v in zip((lbb + p[1:])[:-1], (lbb + p[1:])[1:])])
        own[k] = {'all_copies_ms': round(float(Tv5[site[k]]), 2), 'own_copies_only_ms': round(float(t_own), 2)}
    sp_used = sp_full[idx_used]
    T51 = dijkstra(graph(n, E[idx_used], L[idx_used] / sp_used), indices=his)
    ku = np.unique(np.sort(E[idx_used], axis=1), axis=0, return_index=True)[1]
    T51u = dijkstra(graph(n, E[idx_used][ku], L[idx_used][ku] / sp_used[ku]), indices=his)
    f19 = {'duplicate_node_pairs': int(len(dup_pairs)), 'v5_duplicates_with_different_speeds (shared division edges)': int(v5_diff_speed),
           'v5_exact_duplicates': int(len(dup_pairs) - v5_diff_speed), 'v51_duplicates_with_different_speeds': int(v51_diff_speed),
           'v51_max_abs_dt_ms_dedup_vs_raw (His beat, network)': float(np.nanmax(np.abs(np.where(np.isfinite(T51), T51, 0) - np.where(np.isfinite(T51u), T51u, 0)))),
           'v5_intact_his_to_durrer_site_shared_edges_fastest_vs_own_copies': own}
    if v51_diff_speed or f19['v51_max_abs_dt_ms_dedup_vs_raw (His beat, network)'] > 1e-9:
        sys.exit(f'F19: duplicates change a v5.1 time: {f19}')

    out_d = os.path.join(REPO, 'data', 'biv', h, 'purkinje_v51')
    os.makedirs(out_d, exist_ok=True)
    meta = {'version': VERSION, 'heart': h, 'source_network': os.path.relpath(netf, REPO), 'source_sha256': sha256_file(netf),
            'class_speed_m_s': CLASS_SPEED, 'v_edge_m_s': v_edge, 'R10_factors': factor, 'd_ant_ms': D_ANT, 'd_ret_ms': D_RET,
            'lbbb_cut': cut, 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    base = {k: full[k] for k in ('nodes', 'kind', 'pmj', 'his', 'his_rv')}
    f_net = os.path.join(out_d, 'network_v51.npz')
    np.savez(f_net, edges=E[idx_used], edge_speed=sp_used, edge_class=cls[idx_used].astype(str), params=json.dumps(meta), **base)
    if cut:
        np.savez(os.path.join(out_d, 'network_intact_v51.npz'), edges=E, edge_speed=sp_full, edge_class=cls.astype(str), params=json.dumps(meta), **base)
    nsha = sha256_file(f_net)
    zz = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'uvc', 'z.dat'))
    zphi = lambda u: [round(float(zz[nodes[u]]), 3), round(float(np.degrees(phi[nodes[u]])), 1)]
    report = {'heart': h, 'version': VERSION, 'network_v51': os.path.relpath(f_net, REPO), 'network_v51_sha256': nsha,
              'E1': 'no Durrer-offset calibration: speeds from CLASS_SPEED, R10 and P5 only (network51.py)',
              'E2_segments': seg_out, 'LB_shared_prefix_edges': pre, 'shared_division_edges_off_the_prefix': shared_off_prefix,
              'durrer_sites': {k: {'mesh_node': int(nodes[v]), 'uvc_z_phi': zphi(v)} for k, v in site.items()},
              'E5_E7_delays_ms': {'antegrade': D_ANT, 'retrograde': D_RET}, 'E6': e6, 'E8': guard, 'F19': f19, 'E9': e9,
              'P2_roots': [{'mesh_node': int(nodes[u]), 'classes': sorted({cls[i] for i in np.where((E == u).any(1))[0]}), 'uvc_z_phi': zphi(u)} for u in roots],
              'P3_P5': {'v0_m_s': V0, 'junctions_D_ge_10mm': int(use.sum()), 'median_A0_m_s': round(float(np.median(A0)), 4),
                        'v_edge_unrounded_m_s': round(v_edge_raw, 4), 'v_edge_m_s': v_edge, 'v_edge_gt_4.0_report': bool(v_edge > 4.0)},
              'P6': {'v_edge_dedup_unrounded_m_s': round(v6, 4), 'pass_within_1pct': bool(p6)}, 'P7': p7rep | {'pass_2.00_pm_0.02': bool(p7)},
              'P8': p8, 'wall_s': round(time.time() - t0, 1)}
    json.dump(report, open(os.path.join(HERE, f'network51_{h}.json'), 'w'), indent=1, default=str)
    par = {'heart': h, 'version': VERSION, 'network_v51_sha256': nsha, 'root_position': 'distal His: root at the LB/RB split (branching '
           'portion under the membranous septum, LV septal endocardium below the aortic annulus at the right coronary cusp)',
           'segments': seg_out, 'distal': {'class': 'DISTAL', 'edges': counts['DISTAL'], 'v_edge_m_s': v_edge},
           'junction_delays_ms': {'antegrade': D_ANT, 'retrograde': D_RET}, 'lbbb_cut': cut}
    json.dump(par, open(os.path.join(REPO, 'params', f'params_network_{h}_v51.json'), 'w'), indent=1)
    print(json.dumps({k: report[k] for k in ('E2_segments', 'P3_P5', 'P6', 'P7', 'P8', 'E9', 'E8', 'E6')}, indent=1, default=str))
    if not (p6 and p7):
        sys.exit(f'{h}: gate failed: P6 {p6}, P7 {p7}')


if __name__ == '__main__':
    {'build': build}[sys.argv[1]]()
