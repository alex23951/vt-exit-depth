"""Read-only preview P11 (lock thread, relayed 21 Oct 2026 05:13 UTC): the 8.2 / D14 span. Report only; nothing is built.

(a) cut52's 0 % landmark against step0_report35.py's first reading of report 35 (f).
(b) step0_report35.py's heart() re-run as committed (a1b7e7c; the file is unchanged since), called from here so the
    committed report35_<H>.json is not overwritten; its 35 (f) block compared with the stored one; the height of its
    100 % point (its "pulmonary ring") in the D13 frame against the mid-plane ring.
(c) cut52's 100 % point (the D13 mid-plane ring at the posterior centre): on which surfaces it lies, its distance to the
    RV cavity surface, and the PV disc's faces.
(d) cut52's boundary (47.2 % of surface path + rise) beside the wall-only reading (47.2 % of the surface path alone):
    the height on the PV axis, the tag-1/tag-2 interface area above each (all, and within 40 mm of the RVOT axis as
    step 0 did; plus the LV-group / RV-group faces the cut splits) and v5.1's RV PMJs above each.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p11.py
"""
import importlib.util
import json
import os
import sys

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import cut52 as C52                                                                         # noqa: E402
from common import boundary_faces                                                           # noqa: E402

S0_PATH = os.path.join(G.REPO, 'analysis', 'v52_2026-10-20', '00_step0', 'step0_report35.py')
spec = importlib.util.spec_from_file_location('step0_report35', S0_PATH)
S0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S0)


def run(h):
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    P, E, tag = G.load_full(h)
    pv, _ = G.pulmonary_frame(P, E, tag)
    L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
    # (b) step 0 re-run
    r0 = S0.heart(h)
    f_new = r0['35f_infundibulum_cut']
    f_old = json.load(open(os.path.join(G.REPO, 'analysis', 'v52_2026-10-20', '00_step0', f'report35_{h}.json')))['35f_infundibulum_cut']
    v1 = list(f_new['variants'])[0]
    new1, old1 = f_new['variants'][v1], f_old['variants'][v1]
    p100s0, p0s0 = int(new1['node_100pct']), int(new1['node_0pct'])
    rec['b_step0_first_reading_rerun'] = {
        'reading': v1, 'span_mm_now': new1['posterior_span_mm'], 'span_mm_stored': old1['posterior_span_mm'],
        'whole_35f_block_identical_to_stored': json.loads(json.dumps(f_new, default=str)) == f_old,
        'TA_level_height_mm': new1['tricuspid_annulus_level_height_mm'],
        'its_100pct_point': {'full_node': p100s0, 'what': 'lowest PV disc-wall contact node on the RV cavity surface within 45 deg of the aortic side',
                             'height_D13_frame_mm (mid-plane ring = 0)': round(float(pv.h(P[p100s0])[0]), 2),
                             'theta_D13_frame_deg': round(float(pv.theta(P[[p100s0]])[0]), 1),
                             'distance_to_cut52_100pct_mm': round(float(np.linalg.norm(P[p100s0] - P[L['node_100pct (full mesh)']])), 2),
                             'distance_to_cut52_p_top_mm': round(float(np.linalg.norm(P[p100s0] - P[L['cavity_rim_node_below_the_ring (p_top)']])), 2)},
        'PV_disc_faces_D13_frame_mm (ventricular, arterial)': [round(x, 2) for x in pv.faces]}
    # (a) 0 % landmarks
    p0c = int(L['node_0pct (full mesh)'])
    rec['a_0pct_landmarks'] = {'cut52': {'full_node': p0c, 'height_mm': L['height_0pct_mm'], 'projected_from': 'the D13 mid-plane ring point at the posterior centre (cut52 100 %)'},
                               'step0_first_reading': {'full_node': p0s0, 'height_mm': round(float(pv.h(P[p0s0])[0]), 3), 'projected_from': 'step 0\'s 100 % point (b)'},
                               'same_node': p0c == p0s0, 'distance_between_mm': round(float(np.linalg.norm(P[p0c] - P[p0s0])), 2),
                               'same_TA_level_reading': 'yes: both use the TV-ring cavity node nearest the PV disc (superior annulus); heights '
                                                        f"{L['tricuspid_level_height_mm']} (cut52) and {new1['tricuspid_annulus_level_height_mm']} (step 0)"}
    # (c) the 100 % point
    rn, loc, G2 = C52.rv_cavity_graph(P, E, tag)
    p100 = int(L['node_100pct (full mesh)']); p_top = int(L['cavity_rim_node_below_the_ring (p_top)'])
    bf, own = boundary_faces(E)
    on_b = np.isin(bf, p100).any(1)
    d_rn, j_rn = cKDTree(P[rn]).query(P[p100])
    tl = np.zeros(40, bool); tl[np.unique(tag[np.where(np.isin(E, p100).any(1))[0]])] = True
    rec['c_100pct_point'] = {'full_node': p100, 'height_mm': L['height_100pct_mm'], 'tags_of_its_elements': [int(x) for x in np.where(tl)[0]],
                             'on_any_boundary_face': bool(on_b.any()), 'on_RV_cavity_surface': bool(p100 in set(rn.tolist())),
                             'nearest_RV_cavity_surface_node': {'full_node': int(rn[j_rn]), 'mm': round(float(d_rn), 2), 'height_mm': round(float(pv.h(P[rn[j_rn]])[0]), 2)},
                             'p_top (cavity rim node within 10 deg of posterior, nearest the ring point)': {'full_node': p_top, 'mm': L['span_parts_mm']['rise p_top -> mid-plane ring'], 'height_mm': L['height_p_top_mm']}}
    # (d) the two boundaries
    p0 = p0c
    d, pr = dijkstra(G2, indices=loc[p0], return_predecessors=True)
    path = [loc[p_top]]
    while path[-1] != loc[p0]:
        path.append(pr[path[-1]])
    path = rn[np.array(path[::-1])]
    sp = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[path], axis=0), axis=1))]
    surf_len = float(sp[-1]); rise = float(np.linalg.norm(P[p_top] - P[p100])); span = surf_len + rise
    pathx = np.r_[path, p100]; spx = np.r_[sp, span]

    def at(pp, ss, s_):
        i = min(max(int(np.searchsorted(ss, s_)), 1), len(ss) - 1)
        t = (s_ - ss[i - 1]) / max(ss[i] - ss[i - 1], 1e-12)
        return P[pp[i - 1]] + t * (P[pp[i]] - P[pp[i - 1]])
    Xc = at(pathx, spx, C52.SHARE * span); Xw = at(path, sp, C52.SHARE * surf_len)
    hc, hw = float(pv.h(Xc)[0]), float(pv.h(Xw)[0])
    fa, a, b = G.interfaces(E, tag)
    t12 = ((tag[a] == 1) & (tag[b] == 2)) | ((tag[a] == 2) & (tag[b] == 1))
    lvrv = (np.isin(tag[a], G.LV_GROUP) & np.isin(tag[b], G.RV_GROUP)) | (np.isin(tag[b], G.LV_GROUP) & np.isin(tag[a], G.RV_GROUP))
    fc = P[fa].mean(1); fh = pv.h(fc); near = pv.r(fc) < 40; ar = G.tri_area(P, fa)
    Pm = None
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    from common import read_pts                                                             # noqa: E402
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3
    net = np.load(os.path.join(G.REPO, 'data', 'biv', h, 'purkinje_v51', 'network_v51.npz'))
    nodes, kind, pmj = net['nodes'], net['kind'].astype(str), net['pmj']
    hp = pv.h(Pm[nodes[pmj[kind[pmj] == 'distal_rv']]])

    def above(hh):
        return {'height_on_PV_axis_mm': round(hh, 3), 'pct_of_axial_span': round(100 * (hh - L['height_0pct_mm']) / (L['height_100pct_mm'] - L['height_0pct_mm']), 1),
                'tag1_tag2_area_above_mm2': round(float(ar[t12 & (fh >= hh)].sum()), 1),
                'tag1_tag2_area_above_within_40mm_of_RVOT_axis_mm2': round(float(ar[t12 & near & (fh >= hh)].sum()), 1),
                'LV_group_RV_group_area_above_mm2 (the faces the cut splits)': round(float(ar[lvrv & (fh >= hh)].sum()), 1),
                'RV_PMJs_above': int((hp > hh).sum())}
    rec['d_boundaries'] = {'path_check': {'surface_mm': round(surf_len, 3), 'rise_mm': round(rise, 3), 'span_mm': round(span, 3), 'stored_span_mm': L['posterior_span_mm']},
                           'cut52 (47.2 % of surface + rise)': dict(distance_along_mm=round(C52.SHARE * span, 2), **above(hc)),
                           'wall-only (47.2 % of the surface path)': dict(distance_along_mm=round(C52.SHARE * surf_len, 2), **above(hw)),
                           'RV_PMJs_total': int(len(hp))}
    G.dump(rec, os.path.join(HERE, f'preview_p11_{h}.json'))
    print(h, json.dumps(rec), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
