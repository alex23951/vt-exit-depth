"""v5.2 step 2g: the conduction system (LOCK.md section 7; deviations D1, D4, D11, D12, D16; 7.8 for 6G8DD8S5).

Sheet coordinates exactly as report 34 (step 0, analysis/v52_2026-10-20/00_step0/step0_report34.py, step0_followup.py):
the His line is the 2-ring surface shortest path on the LV endocardium from the v5.1 His node to the LV endocardial apex;
s = arc length of a node's nearest line point, a = its surface distance to the line, + anterior (AHA angle). The LV
endocardium of the merged mesh is v5.1's (merge52: lv_endo unchanged in every heart), so v5.1 coordinates are used.
Left bundle sheet (7.1, D4): every LV endocardial node inside the envelope (0 <= s <= 33 mm; width 6 mm at s = 0 widening
linearly to 22.6 mm at 12.5 mm and held; 17.8 / 22.6 of it anterior and 4.8 / 22.6 posterior of the His line). Nodes =
those mesh nodes (spacing = the mesh's own edges); edges = the LV endocardial triangle edges between two sheet nodes.
Speed by the edge's mean s: 1.5 m/s (class SHEET_TRUNK) below 10 mm, 2.0 m/s (class SHEET) beyond. The v5.1 His node
joins the sheet node at its own mesh node (the origin, s = 0) by one LB_TRUNK edge at 1.5 m/s (length 0); this is the
edge 7.8 removes in 6G8DD8S5.
D11 (assumption 56): v5.1 LB_TRUNK and FASCICLE nodes inside the envelope are removed (the His node is kept); every v5.1
LB_TRUNK / FASCICLE edge from a removed node to a kept node (each fascicle path's own edge across the envelope edge) is
re-pointed to the sheet node at the removed node's mesh node (else the nearest sheet node), keeping its v5.1 class and
speed; every DISTAL edge at a removed node likewise. Everything outside the envelope is v5.1's, unchanged.
Septal outflow (7.1, assumption 31; reading B of the PC's question of 20 Oct 2026, the one that matches report 34 item
3's named nodes): one 2.0 m/s edge (class SEPTAL_OUTFLOW) from the sheet node nearest report 34's mid-septal point at
s = 16.5 mm to the v5.1 LV distal node nearest that point.
Junctions (D1, D12, assumption 46): crest-to-apex length L and distance from the septal crest as report 34; no junction
on a sheet node above the D1 line (distance < L / 3) or within the first 10 mm (s <= 10), one on every other sheet node;
v5.1 LV distal-network junctions on the left septal surface above the D1 line removed; all other v5.1 junctions kept.
Right bundle (D16): v5.1's, unchanged, its moderator-band edge included.
Outputs: data/biv/<H>/v52/purkinje/network_v52.npz (+ network_v52_intact.npz for 6G8DD8S5), same arrays as
network_v51.npz plus s_mm / a_mm of sheet nodes; sheet52_<H>.json (acceptance, reports 34 items 3b and 15) here.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/sheet52.py [HEART ...]
"""
import importlib.util
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
import geom52 as G                                                                          # noqa: E402

S0 = os.path.join(G.REPO, 'analysis', 'v52_2026-10-20', '00_step0')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


R34 = module('r34', os.path.join(S0, 'step0_report34.py'))
FU = module('fu', os.path.join(S0, 'step0_followup.py'))
TRUNK_S, V_TRUNK, V_FASC = 10.0, 1.5, 2.0
ELEM = 1.05                                    # one element (mean edge), the acceptance tolerance of 15.2 step 2g


def frame(h):
    """report 34's frame (as step0_followup.frame), plus AHA labels and the septal-crest distances."""
    B = os.path.join(G.REPO, 'data', 'biv', h)
    P = np.loadtxt(os.path.join(B, 'biv.pts'), skiprows=1) / 1e3
    F = R34.AHA.Frame(h)
    LBL = R34.Labeller(F)
    SL = R34.Surf(P, R34.rd_surf(h, 'lv_endo'))
    lve = SL.nodes
    LT = [LBL.label(P[n]) for n in lve]
    lab = np.array([x[0] or 0 for x in LT]); th_l = np.array([x[1] for x in LT], dtype=float)
    S_mask = np.isin(lab, list(R34.SEPTAL))
    apex_lv = int(lve[np.argmin(F.f(P[lve]))])
    net = dict(np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz')))
    his = int(net['nodes'][int(net['his'])])
    line = SL.path(his, apex_lv, 2)
    sl = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[line], axis=0), axis=1))]
    da, src = SL.dist(line, 2)
    s_of_line = dict(zip(line.tolist(), sl.tolist()))
    s_all = np.array([s_of_line.get(int(f), np.nan) for f in SL.nodes[src]])
    a_all = da * np.sign(R34.wrapdeg(np.nan_to_num(th_l - th_l[src])) + 1e-12)
    bnodes = SL.nodes[np.unique(SL.boundary_edges)]
    crest = np.intersect1d(lve[S_mask], bnodes)
    d_crest, _ = SL.dist(crest, 2)
    L = float(d_crest[SL.ids([apex_lv])[0]])
    return dict(P=P, SL=SL, s=s_all, a=a_all, S=S_mask, lab=lab, his=his, line=line, sl=sl, d_crest=d_crest, L=L, apex=apex_lv)


def build(h):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h)
    fr = frame(h)
    P, SL, s_all, a_all = fr['P'], fr['SL'], fr['s'], fr['a']
    r34 = json.load(open(os.path.join(S0, f'report34_{h}.json')))
    nf_int = os.path.join(B, 'purkinje_v51', 'network_intact_v51.npz')
    intact = os.path.exists(nf_int)
    net = dict(np.load(nf_int if intact else os.path.join(B, 'purkinje_v51', 'network_v51.npz')))
    net_cut = dict(np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz')))
    nodes, kind = net['nodes'].astype(np.int64), net['kind'].astype(str)
    E, cls, spd = net['edges'].astype(np.int64), net['edge_class'].astype(str), net['edge_speed'].astype(float)
    pmj, his_g, his_rv = net['pmj'].astype(np.int64), int(net['his']), int(net['his_rv'])
    params51 = json.loads(str(net['params']))
    n = len(nodes)
    assert int(nodes[his_g]) == fr['his']

    # ---------------- the sheet
    env_l = FU.inside(s_all, a_all)                                     # LV endocardial local ids inside the envelope
    e1 = SL.e1
    ke = env_l[e1[:, 0]] & env_l[e1[:, 1]]
    nL = len(SL.nodes)
    ncomp_env, lab_env = connected_components(coo_matrix((np.ones(ke.sum()), (e1[ke, 0], e1[ke, 1])), shape=(nL, nL)), directed=False)
    o_l = SL.ids([fr['his']])[0]
    # the sheet is the envelope's triangulated strip that is connected to the origin; envelope nodes joined to it only through
    # nodes outside the envelope (slivers at its jagged edge) are not part of it and are reported (construction rule, mine)
    ins_l = env_l & (lab_env == lab_env[o_l])
    islands = np.where(env_l & ~ins_l)[0]
    sh_l = np.where(ins_l)[0]
    sh_mesh = SL.nodes[sh_l]
    ke = ins_l[e1[:, 0]] & ins_l[e1[:, 1]]
    se = e1[ke]                                                          # local ids
    loc_sh = np.full(len(SL.nodes), -1); loc_sh[sh_l] = np.arange(len(sh_l))
    se_s = loc_sh[se]
    ncomp_sh, lab_sh = connected_components(coo_matrix((np.ones(len(se_s)), (se_s[:, 0], se_s[:, 1])), shape=(len(sh_l), len(sh_l))), directed=False)
    sizes_sh = np.bincount(lab_sh)
    island_rep = {'envelope_nodes': int(env_l.sum()), 'envelope_components': int(len(np.unique(lab_env[env_l]))),
                  'nodes_not_connected_to_the_origin (left out)': int(len(islands)),
                  'their_s_a_mm': [[round(float(s_all[i]), 2), round(float(a_all[i]), 2)] for i in islands]}
    s_sh, a_sh = s_all[sh_l], a_all[sh_l]
    s_edge = 0.5 * (s_sh[se_s[:, 0]] + s_sh[se_s[:, 1]])
    e_trunk = s_edge < TRUNK_S

    # ---------------- v5.1 network: what the sheet replaces (D11)
    onl = np.isin(nodes, SL.nodes)
    gl = np.full(n, -1); gl[onl] = SL.ids(nodes[onl])
    ins_g = np.zeros(n, bool); ins_g[onl] = ins_l[gl[onl]]
    tf = np.isin(cls, ['LB_TRUNK', 'FASCICLE'])
    tf_nodes = np.unique(E[tf])
    removed = np.zeros(n, bool); removed[tf_nodes] = ins_g[tf_nodes]
    removed[his_g] = False                                               # the His node is kept (HIS / RB edges)
    other_at_removed = np.unique(cls[(removed[E[:, 0]] | removed[E[:, 1]]) & ~tf])
    assert set(other_at_removed) <= {'DISTAL'}, other_at_removed
    sh_tree = cKDTree(P[sh_mesh])
    sh_of_mesh = {int(m): i for i, m in enumerate(sh_mesh)}

    def sheet_node(g):
        m = int(nodes[g])
        if m in sh_of_mesh:
            return sh_of_mesh[m], 0.0
        d, i = sh_tree.query(P[m])
        return int(i), float(d)
    # fascicle paths (as step0_followup.lb) for the D11 report
    n51 = json.load(open(os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build', f'network51_{h}.json')))
    Lr = np.linalg.norm(P[nodes[E[:, 0]]] - P[nodes[E[:, 1]]], axis=1)
    G_tf = coo_matrix((np.r_[Lr[tf], Lr[tf]], (np.r_[E[tf, 0], E[tf, 1]], np.r_[E[tf, 1], E[tf, 0]])), shape=(n, n)).tocsr()
    _, pred = dijkstra(G_tf, indices=his_g, return_predecessors=True)
    ends = {k: int(np.where((nodes == v['mesh_node']) & (kind == 'proximal'))[0][0]) for k, v in n51['durrer_sites'].items()}
    paths = {}
    for k, g in ends.items():
        p = [g]
        while p[-1] != his_g:
            p.append(int(pred[p[-1]]))
        paths[k] = p[::-1]

    # ---------------- assemble the v5.2 network: kept v5.1 nodes, then the sheet nodes
    keep = ~removed
    newid = np.full(n, -1); newid[keep] = np.arange(keep.sum())
    nk = int(keep.sum())
    sh_g = nk + np.arange(len(sh_l))                                     # graph ids of sheet nodes
    out_nodes = np.r_[nodes[keep], sh_mesh]
    out_kind = np.r_[kind[keep], np.array(['sheet'] * len(sh_l))]
    ed, ec, es = [], [], []
    both_kept = keep[E[:, 0]] & keep[E[:, 1]]
    ed.append(newid[E[both_kept]]); ec.append(cls[both_kept]); es.append(spd[both_kept])
    joins, rejoined = [], []
    one = (removed[E[:, 0]] ^ removed[E[:, 1]])                          # one end removed, one kept
    replaced_by_origin = []
    for i in np.where(one)[0]:
        a_, b_ = E[i]
        rm, kp = (a_, b_) if removed[a_] else (b_, a_)
        if kp == his_g:                       # the His's own first LB_TRUNK edge: the sheet starts here (origin edge below)
            replaced_by_origin.append([int(nodes[kp]), int(nodes[rm])])
            continue
        assert cls[i] == 'DISTAL' or not ins_g[kp], 'a trunk / fascicle edge joins a kept node inside the envelope'
        sj, dmm = sheet_node(rm)
        ed.append(np.array([[sh_g[sj], newid[kp]]])); ec.append(np.array([cls[i]])); es.append(np.array([spd[i]]))
        rec = {'v51_edge': [int(nodes[rm]), int(nodes[kp])], 'class': str(cls[i]), 'speed_m_s': float(spd[i]),
               'sheet_node_mesh': int(sh_mesh[sj]), 'sheet_node_is_the_removed_nodes_mesh_node': dmm == 0.0,
               'kept_end_mesh': int(nodes[kp]), 'kept_end_kind': str(kind[kp]),
               'length_mm': round(float(np.linalg.norm(P[sh_mesh[sj]] - P[nodes[kp]])), 3)}
        (rejoined if cls[i] == 'DISTAL' else joins).append(rec)
    # sheet edges
    ed.append(sh_g[se_s]); ec.append(np.where(e_trunk, 'SHEET_TRUNK', 'SHEET')); es.append(np.where(e_trunk, V_TRUNK, V_FASC))
    # His -> sheet origin
    org = sh_of_mesh[fr['his']]
    ed.append(np.array([[newid[his_g], sh_g[org]]])); ec.append(np.array(['LB_TRUNK'])); es.append(np.array([V_TRUNK]))
    # septal outflow (reading B)
    i3 = r34['item3']['septal_outflow']
    mid = int(i3['mid_septal_point_at_16.5mm'])
    dl = np.where(kind == 'distal_lv')[0]
    dl_near = dl[np.argmin(np.linalg.norm(P[nodes[dl]] - P[mid], axis=1))]
    assert int(nodes[dl_near]) == int(i3['nearest_v51_lv_distal_node'])
    sj_mid = sh_of_mesh.get(mid)
    if sj_mid is None:
        sj_mid = int(sh_tree.query(P[mid])[1])
    ed.append(np.array([[sh_g[sj_mid], newid[dl_near]]])); ec.append(np.array(['SEPTAL_OUTFLOW'])); es.append(np.array([V_FASC]))
    out_E = np.vstack(ed).astype(np.int64); out_cls = np.concatenate(ec).astype('<U14'); out_spd = np.concatenate(es).astype(float)
    assert (out_E >= 0).all()

    # ---------------- junctions (D1, D12)
    dcr = fr['d_crest']; Lc = fr['L']
    above_l = dcr < Lc / 3                                               # LV endocardial local ids above the D1 line
    S_l = fr['S']
    pmj_keep = []
    removed_pmj = {}
    for g in pmj:
        if removed[g]:
            raise RuntimeError('a v5.1 junction on a removed trunk / fascicle node')
        if kind[g] == 'distal_lv' and onl[g] and S_l[gl[g]] and above_l[gl[g]]:
            sg = int(fr['lab'][gl[g]])
            removed_pmj[sg] = removed_pmj.get(sg, 0) + 1
            continue
        pmj_keep.append(newid[g])
    sh_pmj = (~above_l[sh_l]) & (s_sh > TRUNK_S)
    out_pmj = np.r_[np.array(pmj_keep, np.int64), sh_g[sh_pmj]]
    his_new, his_rv_new = int(newid[his_g]), int(newid[his_rv])

    # ---------------- acceptance and reports
    N2 = len(out_nodes)
    Gu = coo_matrix((np.ones(len(out_E)), (out_E[:, 0], out_E[:, 1])), shape=(N2, N2))
    _, labN = connected_components(Gu, directed=False)
    reach = labN == labN[his_new]
    dl_new = newid[dl]
    acc = {}
    acc['origin_width_mm (target 6, +-1.05)'] = (lambda m: round(float(a_sh[m].max() - a_sh[m].min()), 2))(s_sh <= ELEM)
    acc['length_mm (max s of a sheet node; target 33, +-1.05)'] = round(float(s_sh.max()), 2)
    # width per level. s is the arc position of a node's nearest His-line NODE (report 34), so it is sampled at the line's
    # node spacing (0.7-2.2 mm) and nodes far from the line skip some line nodes: a window in s measures that sampling, not
    # the sheet. Primary measure: slabs 1.5 mm thick perpendicular to the His line's chord tangent at each level; in each
    # slab, the extents are the sheet nodes' a (surface distance to the line, the coordinate the envelope is cut in).
    Pl, slv = P[fr['line']], fr['sl']
    at = lambda v: np.array([np.interp(v, slv, Pl[:, k]) for k in range(3)])
    Xs = P[sh_mesh]
    lv, lv_s = [], []
    for sv in np.arange(12.5, 33.0 + 1e-9, 2.5):
        T = at(min(sv + 1.25, slv[-1])) - at(max(sv - 1.25, 0.0)); T /= np.linalg.norm(T)
        m = np.abs((Xs - at(sv)) @ T) <= 0.75
        lv.append({'s_mm': float(sv), 'nodes': int(m.sum()), 'width_mm': round(float(a_sh[m].max() - a_sh[m].min()), 2) if m.any() else None,
                   'anterior_mm': round(float(a_sh[m].max()), 2) if m.any() else None, 'posterior_mm': round(float(-a_sh[m].min()), 2) if m.any() else None})
        m = np.abs(s_sh - sv) <= 1.25
        lv_s.append({'s_mm': float(sv), 'nodes': int(m.sum()), 'width_mm': round(float(a_sh[m].max() - a_sh[m].min()), 2) if m.any() else None})
    acc['full_width_levels (perpendicular slabs; targets 22.6 / 17.8 / 4.8 mm, +-1.05)'] = lv
    acc['width_by_s_window_+-1.25mm (report 34 level convention; sampled by the line nodes, report only)'] = lv_s
    okw = all(x['width_mm'] is not None and abs(x['width_mm'] - 22.6) <= ELEM and abs(x['anterior_mm'] - 17.8) <= ELEM
              and abs(x['posterior_mm'] - 4.8) <= ELEM for x in lv)
    acc['checks'] = {
        'origin_width_within_one_element': abs(acc['origin_width_mm (target 6, +-1.05)'] - 6.0) <= ELEM,
        'length_within_one_element': abs(acc['length_mm (max s of a sheet node; target 33, +-1.05)'] - 33.0) <= ELEM,
        'full_width_and_extents_within_one_element_12.5_to_33mm': bool(okw),
        'one_connected_sheet': bool(ncomp_sh == 1),
        'no_pmj_in_first_10mm': bool(not (sh_pmj & (s_sh <= TRUNK_S)).any()),
        'no_pmj_on_sheet_above_D1': bool(not (sh_pmj & above_l[sh_l]).any()),
        'pmj_on_every_sheet_node_below_D1_beyond_10mm': bool(sh_pmj[(~above_l[sh_l]) & (s_sh > TRUNK_S)].all()),
        'no_pmj_on_LV_distal_nodes_above_D1_on_left_septum': bool(not any(
            out_kind[g] == 'distal_lv' and int(out_nodes[g]) in SL.loc and S_l[SL.loc[int(out_nodes[g])]] and above_l[SL.loc[int(out_nodes[g])]]
            for g in out_pmj)),
        'every_v51_LV_distal_node_reachable_from_the_His': bool(reach[dl_new].all()),
    }
    # D11: kept fascicle paths identical to v5.1 beyond the exit node
    E51 = {tuple(sorted((int(nodes[a]), int(nodes[b])))): (str(c), float(v)) for (a, b), c, v in zip(E, cls, spd)}
    Enew = {}
    for (a, b), c, v in zip(out_E, out_cls, out_spd):
        Enew.setdefault(tuple(sorted((int(out_nodes[a]), int(out_nodes[b])))), []).append((str(c), float(v)))
    fasc = {}
    for k, p in paths.items():
        io = [bool(ins_g[g]) for g in p]
        j = next((i for i, x in enumerate(io) if not x), None)
        if j is None:
            fasc[k] = {'leaves_envelope': False, 'endpoint_mesh': int(nodes[p[-1]]), 'kept_length_mm': 0.0}
            continue
        tail = p[j:]
        same = all(not removed[g] for g in tail) and all(
            (str(cls_e), float(v)) in Enew.get(tuple(sorted((int(nodes[a]), int(nodes[b])))), [])
            for a, b in zip(tail[:-1], tail[1:]) for cls_e, v in [E51[tuple(sorted((int(nodes[a]), int(nodes[b]))))]])
        jn = [x for x in joins if x['kept_end_mesh'] == int(nodes[p[j]])]
        fasc[k] = {'leaves_envelope': True, 'exit_node_mesh': int(nodes[p[j]]), 'exit_s_a_mm': [round(float(s_all[gl[p[j]]]), 2), round(float(a_all[gl[p[j]]]), 2)] if onl[p[j]] else None,
                   'last_inside_mesh': int(nodes[p[j - 1]]), 'kept_nodes': len(tail),
                   'kept_length_mm': round(float(np.linalg.norm(np.diff(P[nodes[tail]], axis=0), axis=1).sum()), 2),
                   'kept_path_identical_to_v51': bool(same), 'join_edge': jn}
    acc['checks']['kept_fascicle_paths_identical_to_v51'] = all(v.get('kept_path_identical_to_v51', True) for v in fasc.values())
    # right bundle bit-identical
    rb51 = sorted((tuple(sorted((int(nodes[a]), int(nodes[b])))), float(v)) for (a, b), c, v in zip(E, cls, spd) if c in ('RB', 'HIS'))
    rb52 = sorted((tuple(sorted((int(out_nodes[a]), int(out_nodes[b])))), float(v)) for (a, b), c, v in zip(out_E, out_cls, out_spd) if c in ('RB', 'HIS'))
    rv51 = sorted((tuple(sorted((int(nodes[a]), int(nodes[b])))), str(c), float(v)) for (a, b), c, v in zip(E, cls, spd) if kind[a] == 'distal_rv' or kind[b] == 'distal_rv')
    rv52 = sorted((tuple(sorted((int(out_nodes[a]), int(out_nodes[b])))), str(c), float(v)) for (a, b), c, v in zip(out_E, out_cls, out_spd)
                  if out_kind[a] == 'distal_rv' or out_kind[b] == 'distal_rv')
    acc['checks']['right_bundle_and_RV_network_bit_identical'] = bool(rb51 == rb52 and rv51 == rv52)
    mb = r34['items6_12']['v51_RB']
    # metrication: graph distance (sheet edges) from the origin to the two distal corners against the 2-ring surface estimate
    wsh = np.linalg.norm(P[sh_mesh[se_s[:, 0]]] - P[sh_mesh[se_s[:, 1]]], axis=1)
    Gs = coo_matrix((np.r_[wsh, wsh], (np.r_[se_s[:, 0], se_s[:, 1]], np.r_[se_s[:, 1], se_s[:, 0]])), shape=(len(sh_l), len(sh_l))).tocsr()
    dg = dijkstra(Gs, indices=org)
    d2, _ = SL.dist([fr['his']], 2)
    endm = s_sh >= s_sh.max() - ELEM
    corners = {'anterior_distal_corner': int(np.where(endm)[0][np.argmax(a_sh[endm])]), 'posterior_distal_corner': int(np.where(endm)[0][np.argmin(a_sh[endm])])}
    metr = {}
    for k, c in corners.items():
        g1, g2 = float(dg[c]), float(d2[sh_l[c]])
        metr[k] = {'mesh_node': int(sh_mesh[c]), 's_a_mm': [round(float(s_sh[c]), 2), round(float(a_sh[c]), 2)],
                   'sheet_graph_mm': round(g1, 2), 'surface_2ring_estimate_mm': round(g2, 2),
                   'straight_mm': round(float(np.linalg.norm(P[sh_mesh[c]] - P[fr['his']])), 2), 'graph_over_surface': round(g1 / g2, 3)}
    # item 3b: sheet nodes per septal third, above / below the D1 line
    thirds = np.where(dcr[sh_l] < Lc / 3, 'upper', np.where(dcr[sh_l] < 2 * Lc / 3, 'middle', 'lower'))
    item3b = {t: {'sheet_nodes': int((thirds == t).sum()), 'with_pmj': int(((thirds == t) & sh_pmj).sum())} for t in ('upper', 'middle', 'lower')}
    item3b['above_D1'] = int(above_l[sh_l].sum()); item3b['below_D1'] = int((~above_l[sh_l]).sum())
    item3b['sheet_nodes_off_the_left_septal_surface'] = int((~S_l[sh_l]).sum())
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'network_base': os.path.basename(nf_int if intact else 'network_v51.npz'),
           'sheet': {'envelope_and_islands': island_rep, 'nodes': int(len(sh_l)), 'edges': int(len(se_s)), 'trunk_edges_1.5': int(e_trunk.sum()), 'edges_2.0': int((~e_trunk).sum()),
                     'components': int(ncomp_sh), 'component_sizes': sorted(sizes_sh.tolist(), reverse=True)[:5],
                     'edge_length_mm_median_p5_p95': np.percentile(np.linalg.norm(P[sh_mesh[se_s[:, 0]]] - P[sh_mesh[se_s[:, 1]]], axis=1), [50, 5, 95]).round(3).tolist(),
                     'pmj_nodes': int(sh_pmj.sum()), 'origin_mesh_node (His exit)': fr['his']},
           'acceptance': acc, 'metrication': metr, 'item3b': item3b,
           'D1': {'crest_to_apex_mm': round(Lc, 2), 'line_mm_from_crest': round(Lc / 3, 2),
                  'v51_LV_distal_junctions_removed_per_AHA_segment': {int(k): int(v) for k, v in sorted(removed_pmj.items())},
                  'removed_total': int(sum(removed_pmj.values())), 'v51_junctions': int(len(pmj)), 'v52_junctions': int(len(out_pmj))},
           'D11_item15': {'v51_trunk_fascicle_nodes_removed': int(removed.sum()), 'fascicles': fasc, 'all_join_edges': joins,
                          'his_first_LB_TRUNK_edges_replaced_by_the_origin_edge (his, removed node)': replaced_by_origin,
                          'distal_edges_rejoined_to_the_sheet': len(rejoined), 'distal_rejoins': rejoined,
                          'septal_outflow': {'reading': 'B (report 34 item 3 mid-septal point)', 'mid_septal_point_mesh': mid,
                                             'mid_septal_point_inside_envelope': mid in sh_of_mesh, 'sheet_node_mesh': int(sh_mesh[sj_mid]),
                                             'distal_node_mesh': int(nodes[dl_near]),
                                             'length_mm': round(float(np.linalg.norm(P[sh_mesh[sj_mid]] - P[nodes[dl_near]])), 3),
                                             'reading_A_his_line_node_16.5mm': int(r34['item3']['line_16.5mm']['node']),
                                             'reading_A_length_mm': round(float(np.linalg.norm(P[int(r34['item3']['line_16.5mm']['node'])] - P[nodes[dl_near]])), 3)},
                          'lv_distal_nodes': int(len(dl)), 'lv_distal_unreachable_from_his': int((~reach[dl_new]).sum())},
           'D16_right_bundle': {'band_edge_length_mm': mb['v51_band_length_mm'], 'vs_Lee_Hur_13.6_mm': round(mb['v51_band_length_mm'] - 13.6, 2),
                                'vs_assumption_54_37.8_mm': round(mb['v51_band_length_mm'] - 37.8, 2)},
           'classes': {c: {'edges': int((out_cls == c).sum()), 'speeds_m_s': sorted(set(np.round(out_spd[out_cls == c], 4).tolist()))} for c in np.unique(out_cls)}}
    params = dict(params51, version='v52-network-1', lock_sha256=G.LOCK_SHA, sheet={'trunk_s_mm': TRUNK_S, 'v_trunk': V_TRUNK, 'v_sheet': V_FASC},
                  base=rec['network_base'], written=time.strftime('%Y-%m-%d %H:%M:%S %Z'), lbbb_cut=False)
    sa_s = np.full(N2, np.nan); sa_a = np.full(N2, np.nan); sa_s[sh_g] = s_sh; sa_a[sh_g] = a_sh
    D = os.path.join(B, 'v52', 'purkinje'); os.makedirs(D, exist_ok=True)
    arrays = dict(nodes=out_nodes, kind=out_kind, edges=out_E, edge_speed=out_spd, edge_class=out_cls, pmj=out_pmj,
                  his=np.int64(his_new), his_rv=np.int64(his_rv_new), sheet_s_mm=sa_s, sheet_a_mm=sa_a)
    if intact:
        # 7.8: only the His -> sheet-origin edge removed
        cut = (out_cls == 'LB_TRUNK') & (((out_E[:, 0] == his_new) & (out_kind[out_E[:, 1]] == 'sheet')) | ((out_E[:, 1] == his_new) & (out_kind[out_E[:, 0]] == 'sheet')))
        np.savez(os.path.join(D, 'network_v52_intact.npz'), params=json.dumps(params), **arrays)
        Ec_, keepc = out_E[~cut], ~cut
        Gc = coo_matrix((np.ones(len(Ec_)), (Ec_[:, 0], Ec_[:, 1])), shape=(N2, N2))
        _, labc = connected_components(Gc, directed=False)
        kept_tf = newid[tf_nodes[keep[tf_nodes]]]
        lvside = np.isin(out_kind, ['distal_lv', 'sheet']); lvside[kept_tf] = True; lvside[his_new] = False
        reach_c = labc == labc[his_new]
        shc = Ec_[np.isin(out_cls[keepc], ['SHEET', 'SHEET_TRUNK'])]
        ncs, _ = connected_components(coo_matrix((np.ones(len(shc)), (shc[:, 0], shc[:, 1])), shape=(N2, N2)), directed=False)
        ncs -= int(N2 - len(sh_g))                                            # isolated non-sheet nodes count as components
        rec['7.8_cut'] = {'removed_edges': [{'his_mesh': fr['his'], 'sheet_origin_mesh': int(out_nodes[b if a == his_new else a]), 'class': 'LB_TRUNK'}
                                            for a, b in out_E[cut]],
                          'lv_or_sheet_nodes_reachable_from_his': int((reach_c & lvside).sum()), 'sheet_components_after_cut': int(ncs),
                          'v51_cut_reference (network_v51.npz edges removed from the intact v5.1 network)': int(len(E) - len(net_cut['edges']))}
        rec['acceptance']['checks']['7.8_no_LV_node_reachable_from_his_after_cut'] = rec['7.8_cut']['lv_or_sheet_nodes_reachable_from_his'] == 0
        rec['acceptance']['checks']['7.8_sheet_one_component_after_cut'] = rec['7.8_cut']['sheet_components_after_cut'] == 1
        arrays.update(edges=out_E[~cut], edge_speed=out_spd[~cut], edge_class=out_cls[~cut])
        params['lbbb_cut'] = True
    np.savez(os.path.join(D, 'network_v52.npz'), params=json.dumps(params), **arrays)
    rec['files'] = {'network': os.path.relpath(os.path.join(D, 'network_v52.npz'), G.REPO), 'sha256': G.sha256(os.path.join(D, 'network_v52.npz'))}
    rec['acceptance']['all_pass'] = bool(all(rec['acceptance']['checks'].values()))
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'sheet52_{h}.json'))
    print(h, 'sheet', rec['sheet']['nodes'], 'nodes', rec['sheet']['components'], 'component(s);', json.dumps(rec['acceptance']['checks']),
          'origin', acc['origin_width_mm (target 6, +-1.05)'], 'length', acc['length_mm (max s of a sheet node; target 33, +-1.05)'], rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        build(h)
