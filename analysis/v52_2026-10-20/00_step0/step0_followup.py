"""v5.2 step 0 follow-up (read only), asked by the lock thread through the coordinator, 20 Oct 2026 17:28 UTC.

1. Left-bundle topology against the adopted envelope (17.8 mm anterior / 4.8 mm posterior of the His line, 33 mm long,
   widening to full width by 12.5 mm), in report 34's sheet coordinates (s, a):
   a. each v5.1 fascicle (anterior, septal, posterior): where its path from the His first leaves the envelope, the path
      length beyond, and whether its endpoint is inside;
   b. the LB_TRUNK / FASCICLE nodes where a DISTAL edge joins (inside or outside the envelope, on which fascicle);
   c. components of the LV network with LB_TRUNK and FASCICLE nodes and edges removed, and the LV distal nodes not
      reachable from the His in two builds, "Nearest node" and "Keep tails" (6G8DD8S5 before its LBBB cut).
   The sheet is modelled for reachability as one connected set reached from the His (it is built that way, 7.1), joined to
   the network only where each build says.
2. Aortic angle frame (report 35's frame: valve-disc mid-plane, root axis = disc normal, theta = 0 at the aortic-ring node
   nearest the mitral disc): angles of the mitral- and pulmonary-disc centroids, the arc of the aortic ring within 1.05 mm
   of the mitral ring, and the arc where RV muscle touches the aortic root within 3 mm above the mid-plane.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/00_step0/step0_followup.py
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
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


R34 = module('r34', os.path.join(HERE, 'step0_report34.py'))
R35 = module('r35', os.path.join(HERE, 'step0_report35.py'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
MEAN_EDGE = 1.05


def frame(h):
    """Report 34's sheet frame for one heart: (s, a) of every LV endocardial node, S mask, the His node."""
    B = os.path.join(REPO, 'data', 'biv', h)
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
    return P, SL, s_all, a_all, S_mask, his


def inside(s, a):
    w = R34.env(np.clip(s, 0, None))
    return (s >= 0) & (s <= R34.SHEET) & (a >= -w * (1 - R34.ANT_SHARE)) & (a <= w * R34.ANT_SHARE)


def graph(n, e):
    return coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr()


def lb(h):
    B = os.path.join(REPO, 'data', 'biv', h)
    P, SL, s_all, a_all, S_mask, his_mesh = frame(h)
    nf = os.path.join(B, 'purkinje_v51', 'network_intact_v51.npz')
    intact = os.path.exists(nf)
    net = dict(np.load(nf if intact else os.path.join(B, 'purkinje_v51', 'network_v51.npz')))
    nodes, kind, E, cls = net['nodes'], net['kind'], net['edges'].astype(np.int64), net['edge_class']
    n = len(nodes)
    his = int(net['his'])
    n51 = json.load(open(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', f'network51_{h}.json')))
    r34 = json.load(open(os.path.join(HERE, f'report34_{h}.json')))
    onl = np.isin(nodes, SL.nodes)
    sa = lambda g: (float(s_all[SL.ids([nodes[g]])[0]]), float(a_all[SL.ids([nodes[g]])[0]])) if onl[g] else (np.nan, np.nan)
    ins = np.zeros(n, bool)
    for g in np.where(onl)[0]:
        s_, a_ = sa(g); ins[g] = bool(inside(np.array(s_), np.array(a_)))
    L = np.linalg.norm(P[nodes[E[:, 0]]] - P[nodes[E[:, 1]]], axis=1)
    tf = np.isin(cls, ['LB_TRUNK', 'FASCICLE'])
    G_tf = coo_matrix((np.r_[L[tf], L[tf]], (np.r_[E[tf, 0], E[tf, 1]], np.r_[E[tf, 1], E[tf, 0]])), shape=(n, n)).tocsr()
    _, pred = dijkstra(G_tf, indices=his, return_predecessors=True)
    end = {k: int(np.where((nodes == v['mesh_node']) & (kind == 'proximal'))[0][0]) for k, v in n51['durrer_sites'].items()}
    paths, out1 = {}, {}
    for k, g_end in end.items():
        p = [g_end]
        while p[-1] != his:
            p.append(int(pred[p[-1]]))
            if p[-1] < 0:
                raise RuntimeError(f'{h} {k}: no LB path')
        p = p[::-1]; paths[k] = p
        arc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[nodes[p]], axis=0), axis=1))]
        io = [bool(ins[g]) for g in p]
        j = next((i for i, x in enumerate(io) if not x), None)
        rec = {'path_nodes': len(p), 'path_length_mm': round(float(arc[-1]), 2), 'endpoint_mesh_node': int(nodes[g_end]),
               'endpoint_s_a_mm': [round(x, 2) for x in sa(g_end)], 'endpoint_inside_envelope': bool(ins[g_end])}
        if j is None:
            rec['leaves_envelope'] = False
        else:
            rec.update({'leaves_envelope': True, 'first_outside_mesh_node': int(nodes[p[j]]), 'first_outside_s_a_mm': [round(x, 2) for x in sa(p[j])],
                        'last_inside_mesh_node': int(nodes[p[j - 1]]) if j > 0 else None,
                        'last_inside_s_a_mm': [round(x, 2) for x in sa(p[j - 1])] if j > 0 else None,
                        'path_length_beyond_first_outside_mm': round(float(arc[-1] - arc[j]), 2),
                        'path_length_beyond_last_inside_mm': round(float(arc[-1] - arc[j - 1]), 2) if j > 0 else None,
                        'returns_inside_later': bool(any(io[j:]))})
        out1[k] = rec
    # which fascicle each trunk / fascicle node belongs to
    tf_nodes = np.unique(E[tf])
    on = {}
    for k, p in paths.items():
        for g in p:
            on.setdefault(g, set()).add(k)
    trunk = set.intersection(*[set(p) for p in paths.values()])
    # 1b: DISTAL edges joining a trunk / fascicle node
    dist = cls == 'DISTAL'
    jn = sorted({int(g) for g in E[dist].ravel() if g in set(tf_nodes.tolist())})
    rows = []
    for g in jn:
        lbl = 'trunk (shared by all three)' if g in trunk else '+'.join(sorted(on.get(g, {'?'})))
        nd = [int(x) for x in E[dist & ((E[:, 0] == g) | (E[:, 1] == g))].ravel() if x != g]
        rows.append({'mesh_node': int(nodes[g]), 'on': lbl, 's_a_mm': [round(x, 2) for x in sa(g)], 'inside_envelope': bool(ins[g]),
                     'distal_neighbours': len(nd), 'neighbour_kinds': sorted({str(kind[x]) for x in nd}),
                     'is_fascicle_endpoint': g in end.values()})
    by = {}
    for r in rows:
        by.setdefault(r['on'], {'inside': 0, 'outside': 0})['inside' if r['inside_envelope'] else 'outside'] += 1
    out_b = {'count': len(rows), 'inside': sum(r['inside_envelope'] for r in rows), 'outside': sum(not r['inside_envelope'] for r in rows),
             'by_fascicle': by, 'nodes': rows,
             'note': 'graph nodes, not mesh nodes: the 18 / 8 / 13 of report 34 item 8 were distal junctions sharing a mesh node with a '
                     'trunk or fascicle node, a different count'}
    # 1c: LV network without trunk and fascicle
    lv_side = (kind == 'distal_lv') | ((kind == 'proximal') & onl)
    keepn = lv_side & ~np.isin(np.arange(n), tf_nodes)
    ke = keepn[E[:, 0]] & keepn[E[:, 1]]
    Gk = graph(n, E[ke])
    nc, lab = connected_components(Gk + Gk.T, directed=False)
    comps = {}
    for c_ in np.unique(lab[keepn]):
        m = keepn & (lab == c_)
        comps[int(c_)] = {'nodes': int(m.sum()), 'distal_lv': int((m & (kind == 'distal_lv')).sum()),
                          'proximal_kind (DISTAL-class division paths)': int((m & (kind == 'proximal')).sum())}
    comp_list = sorted(comps.values(), key=lambda x: -x['nodes'])
    dl = np.where(kind == 'distal_lv')[0]
    dl_in = dl[ins[dl]]
    def reach(attach_nodes):
        """LV distal nodes reachable: every residual component touching an attachment node."""
        ok = set(int(lab[g]) for g in attach_nodes if keepn[g])
        r_ = np.isin(lab, list(ok)) & keepn
        return int((~r_[dl]).sum()), int(r_[dl].sum())
    # (i) Nearest node
    att, att_info = [], {}
    for k, g_end in end.items():
        x = P[nodes[g_end]]
        if not len(dl_in):
            continue
        j = dl_in[np.argmin(np.linalg.norm(P[nodes[dl_in]] - x, axis=1))]
        att.append(int(j)); att_info[k] = {'attach_mesh_node': int(nodes[j]), 'euclid_mm_from_old_endpoint': round(float(np.linalg.norm(P[nodes[j]] - x)), 2),
                                           'attach_s_a_mm': [round(v, 2) for v in sa(j)]}
    mid = r34['item3']['septal_outflow']['mid_septal_point_at_16.5mm']
    jm = dl_in[np.argmin(np.linalg.norm(P[nodes[dl_in]] - P[mid], axis=1))]
    un_i, re_i = reach(att)
    att_7 = [att_info['anterior'], att_info['posterior']]
    un_i7, re_i7 = reach([att[list(end).index('anterior')], att[list(end).index('posterior')], int(jm)])
    # (ii) Keep tails
    tail_nodes = set()
    for k, p in paths.items():
        io = [bool(ins[g]) for g in p]
        j = next((i for i, x in enumerate(io) if not x), None)
        if j is not None:
            tail_nodes |= set(p[j:])
    tail_nodes -= {g for g in tail_nodes if ins[g]}
    # residual graph for (ii): LV-side nodes minus trunk / fascicle nodes inside the envelope (tails kept)
    keep2 = lv_side & ~(np.isin(np.arange(n), tf_nodes) & ins)
    ke2 = keep2[E[:, 0]] & keep2[E[:, 1]]
    G2 = graph(n, E[ke2]); nc2, lab2 = connected_components(G2 + G2.T, directed=False)
    seeds = [g for g in tail_nodes]                                    # tails are joined to the sheet
    inside_join = [int(x) for g in tf_nodes if ins[g] for x in E[dist & ((E[:, 0] == g) | (E[:, 1] == g))].ravel() if x != g and keep2[x]]
    ok2 = set(int(lab2[g]) for g in seeds + inside_join if keep2[g])
    r2 = np.isin(lab2, list(ok2)) & keep2
    un_ii = int((~r2[dl]).sum())
    r2s = r2 | np.isin(lab2, [int(lab2[jm])]) & keep2
    out_c = {'network_used': 'network_intact_v51.npz (before the LBBB cut)' if intact else 'network_v51.npz',
             'lv_distal_nodes': int(len(dl)), 'lv_distal_nodes_inside_envelope': int(len(dl_in)),
             'components_without_trunk_and_fascicles': len(comp_list), 'component_sizes': comp_list,
             'nearest_node': {'rule': 'each of the three old endpoints joined to the v5.1 LV distal node nearest it (Euclidean) inside the '
                                      'envelope; all trunk and fascicle nodes removed', 'attachments': att_info,
                              'lv_distal_nodes_not_reachable': un_i, 'reachable': re_i,
                              'variant_septal_outflow_by_7.1 (anterior and posterior as above, septal at the mid-septal point at 16.5 mm)':
                                  {'septal_attach_mesh_node': int(nodes[jm]), 'not_reachable': un_i7}},
             'keep_tails': {'rule': 'trunk and fascicle nodes inside the envelope replaced by the sheet; the paths beyond kept and joined '
                                    'to the sheet where they leave; distal edges that met a trunk or fascicle node inside the envelope '
                                    'joined to the sheet', 'tail_nodes_kept': len(tail_nodes),
                            'distal_edges_rejoined_inside': len(inside_join),
                            'lv_distal_nodes_not_reachable': un_ii,
                            'with_the_7.1_septal_outflow_added': int((~r2s[dl]).sum())}}
    return {'1a_fascicles': out1, '1b_distal_joins': out_b, '1c_reachability': out_c}


def arc(th):
    """Smallest arc covering a set of angles (deg): start, end, extent, midpoint."""
    t = np.sort(np.mod(th, 360.0))
    if not len(t):
        return None
    g = np.diff(np.r_[t, t[0] + 360.0])
    k = int(np.argmax(g))
    start, ext = t[(k + 1) % len(t)], 360.0 - g[k]
    return {'start_deg': round(float(start), 1), 'end_deg': round(float((start + ext) % 360), 1), 'extent_deg': round(float(ext), 1),
            'midpoint_deg': round(float((start + ext / 2) % 360), 1), 'nodes': int(len(t))}


def both(f):
    """The same quantity in the + sense and the - sense (theta- = 360 - theta+)."""
    if f is None:
        return None
    if isinstance(f, (float, np.floating)):
        return {'+': round(float(f) % 360, 1), '-': round(float(-f) % 360, 1)}
    flip = {'start_deg': f['end_deg'], 'end_deg': f['start_deg']}
    m = dict(f); m2 = dict(f)
    m2.update({'start_deg': round((360 - flip['start_deg']) % 360, 1), 'end_deg': round((360 - flip['end_deg']) % 360, 1),
               'midpoint_deg': round((360 - f['midpoint_deg']) % 360, 1)})
    return {'+': m, '-': m2}


def aortic(h):
    P, E, tag = R35.load(h)
    fa, t1, t2 = R35.interfaces(E, tag)
    av = R35.Valve(P, E, tag, 9, [1, 5, 25, 29], 5)
    mvn = np.unique(E[tag == 7])
    th0 = int(av.ring[np.argmin(cKDTree(P[mvn]).query(P[av.ring])[0])])
    av.set_frame(th0, 1)
    pv_c = P[np.unique(E[tag == 10])].mean(0); mv_c = P[mvn].mean(0)
    # mitral ring: MV-disc nodes shared with any other tag
    other = np.unique(E[tag != 7])
    mring = np.intersect1d(mvn, other)
    d_am = cKDTree(P[mring]).query(P[av.ring])[0]
    near = av.ring[d_am <= MEAN_EDGE]
    rv5 = fa[((t1 == 2) & (t2 == 5))]
    nn = np.unique(rv5)
    hh = av.h(P[nn])
    band = nn[(hh >= 0) & (hh <= 3.0)]
    out = {'frame': 'theta measured about the root axis (AV-disc normal) in the AV-disc mid-plane from the ring node nearest the mitral '
                    'disc (node %d); + and - are the two senses' % th0,
           '2a_mitral_disc_centroid_deg': both(float(av.theta(mv_c)[0])),
           '2b_pulmonary_disc_centroid_deg': both(float(av.theta(pv_c)[0])),
           '2c_aortic_ring_within_1.05mm_of_the_mitral_ring': both(arc(av.theta(P[near]))) if len(near) else
                {'none': True, 'closest_mm': round(float(d_am.min()), 2), 'arc_within_2.1mm': both(arc(av.theta(P[av.ring[d_am <= 2 * MEAN_EDGE]]))) if (d_am <= 2 * MEAN_EDGE).any() else None,
                 'extra_arc_within_closest_plus_1.05mm': both(arc(av.theta(P[av.ring[d_am <= d_am.min() + MEAN_EDGE]])))},
           'mitral_ring_nodes': int(len(mring)), 'aortic_ring_nodes': int(len(av.ring)),
           '2d_rv_on_aortic_root_0_to_3mm_above_mid_plane': both(arc(av.theta(P[band]))) if len(band) else
                {'none': True, 'lowest_contact_height_mm': round(float(hh.min()), 2) if len(hh) else None,
                 'arc_of_lowest_3mm_of_contact': both(arc(av.theta(P[nn[hh <= hh.min() + 3.0]]))) if len(hh) else None},
           'extra_rv_on_aortic_root_0_to_6mm': both(arc(av.theta(P[nn[(hh >= 0) & (hh <= 6.0)]]))) if ((hh >= 0) & (hh <= 6.0)).any() else None,
           'extra_mitral_centroid_to_pulmonary_centroid_deg (shorter way round)': round(float(abs(((av.theta(pv_c)[0] - av.theta(mv_c)[0]) + 180) % 360 - 180)), 1),
           'rv_aortic_contact_nodes_all_heights': int(len(nn)),
           'for_reference_pv_nearest_ring_node_deg': both(float(av.theta(P[int(av.ring[np.argmin(cKDTree(P[np.unique(E[tag == 10])]).query(P[av.ring])[0])])])[0]))}
    return out


def main():
    t0 = time.time()
    res = {'written': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    for h in HEARTS:
        res[h] = {'left_bundle': lb(h), 'aortic_frame': aortic(h)}
        print(h, f'{time.time() - t0:.0f} s', flush=True)
        json.dump(res, open(os.path.join(HERE, 'followup.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
