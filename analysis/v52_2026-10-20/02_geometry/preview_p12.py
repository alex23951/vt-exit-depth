"""Read-only preview P12 (b) and (c) (lock thread, relayed 21 Oct 2026 08:30 UTC). Report only; nothing is built.
(a) is answered from the code of preview_p8/p9/p10.py (no run).

(b) D29 on v5.2's LV network as built in 2g (data/biv/<H>/v52/purkinje/network_v52.npz, the D21 rebuild of 21 Oct):
    LV junctions (kinds distal_lv and sheet) that are a vertex of a LV-side element (v5.1's split) with D20a's
    b = clip((z - 0.80) / 0.20, 0, 1)(1 - w_LV) > 0 (element means of the converged z and w_LV); P10 (b)'s v5.1 junctions
    with b > 0 that D1 removed; for the v5.2 junctions with b > 0 their heights relative to the aortic-valve mid-plane
    (D15 frame) in 2 mm bins, the largest b, and their AHA segments (aha51 frame, groove from the converged v; septal =
    2, 3, 8, 9, 14).
(c) D32: cut52's projection to the 0 % level; the 0 % and 100 % heights and the axial percentages; the area the cut
    splits on the merged mesh (the simulation mesh) and on the v5.1 / full mesh, above cut52's and the wall-only boundary.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p12.py
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import cut52 as C52                                                                         # noqa: E402
import previews2_fields as PF                                                               # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402

SEPTAL = {2, 3, 8, 9, 14}


def run(h):
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); cv = os.path.join(G.RUN, h, 'converged')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, tb = read_elem(os.path.join(V, 'biv52'))
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, np.ones(len(E) - nb, bool)]
    ix = np.where(~RV)[0]; Ex = E[ix]
    z = np.load(os.path.join(cv, 'z.npy')); wLV = np.load(os.path.join(cv, 'w_LV.npy')); vcv = np.load(os.path.join(cv, 'v_uvc.npy'))
    b = np.clip((np.clip(z[Ex].mean(1), 0, 1) - 0.80) / 0.20, 0, 1) * (1 - np.clip(np.nanmean(wLV[Ex], 1), 0, 1))
    N = len(P)
    eon = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(len(Ex)), 4))), shape=(N, len(Ex))).tocsr()
    bmax = lambda n: float(b[eon.indices[eon.indptr[n]:eon.indptr[n + 1]]].max()) if eon.indptr[n + 1] > eon.indptr[n] else 0.0
    Pf, Ef, tf = G.load_full(h)
    av, _ = G.aortic_frame(Pf, Ef, tf)
    pv, _ = G.pulmonary_frame(Pf, Ef, tf)
    # (b)
    n52 = np.load(os.path.join(V, 'purkinje', 'network_v52.npz'))
    nodes, kind, pmj = n52['nodes'], n52['kind'].astype(str), n52['pmj']
    lvj = nodes[pmj[np.isin(kind[pmj], ['distal_lv', 'sheet'])]]
    n51 = np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz'))
    j51 = n51['nodes'][n51['pmj'][n51['kind'].astype(str)[n51['pmj']] == 'distal_lv']]
    b52 = np.array([bmax(int(n)) for n in lvj]); b51 = np.array([bmax(int(n)) for n in j51])
    hit = lvj[b52 > 0]; hit51 = j51[b51 > 0]
    hh = av.h(P[hit]) if len(hit) else np.zeros(0)
    edges = np.arange(0, 22, 2.0)
    below = -hh
    bins = {f'{int(lo)}-{int(lo + 2)} mm below': int(((below >= lo) & (below < lo + 2)).sum()) for lo in edges[:-1]}
    bins['>= 20 mm below'] = int((below >= 20).sum()); bins['above the mid-plane'] = int((below < 0).sum())
    seg = np.asarray(PF.frame_labels(h, P, vcv, P[hit])).astype(int) if len(hit) else np.zeros(0, int)
    rec['b_D29_v52_network'] = {
        'network_sha256': G.sha256(os.path.join(V, 'purkinje', 'network_v52.npz')),
        'v52_LV_junctions (distal_lv + sheet)': int(len(lvj)), 'on_LV_side_elements_with_b_gt_0': int(len(hit)),
        'of_which_sheet_junctions': int(np.isin(hit, nodes[pmj[kind[pmj] == 'sheet']]).sum()),
        'P10b_v51_junctions_with_b_gt_0': int(len(hit51)), 'of_those_removed_by_D1 (not a v5.2 junction)': int((~np.isin(hit51, lvj)).sum()),
        'highest_height_rel_aortic_mid_plane_mm (negative = below)': round(float(hh.max()), 2) if len(hh) else None,
        'heights_below_mid_plane_2mm_bins': bins, 'largest_b': round(float(b52.max()), 3),
        'AHA_segments': {str(k): int((seg == k).sum()) for k in np.unique(seg)},
        'septal (2, 3, 8, 9, 14)': int(np.isin(seg, list(SEPTAL)).sum()), 'free_wall': int((~np.isin(seg, list(SEPTAL)) & (seg != 17)).sum()),
        'apex_17': int((seg == 17).sum())}
    # (c)
    L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
    p100, p0 = int(L['node_100pct (full mesh)']), int(L['node_0pct (full mesh)'])
    hTA = L['tricuspid_level_height_mm']
    q = Pf[p100] - (pv.h(Pf[p100])[0] - hTA) * pv.n
    rn, loc, G2 = C52.rv_cavity_graph(Pf, Ef, tf)
    dq, jq = cKDTree(Pf[rn]).query(q)
    cen = Pf[Ef].mean(1); cand = cKDTree(cen).query(q, k=64)[1]
    q_tag = None
    for e in cand:
        X = Pf[Ef[e]]; Tm = (X[1:] - X[0]).T
        lam = np.linalg.solve(Tm, q - X[0])
        if (lam >= -1e-9).all() and lam.sum() <= 1 + 1e-9:
            q_tag = int(tf[e]); break
    h0, h100 = L['height_0pct_mm'], L['height_100pct_mm']
    p11 = json.load(open(os.path.join(HERE, f'preview_p11_{h}.json')))['d_boundaries']
    hc = p11['cut52 (47.2 % of surface + rise)']['height_on_PV_axis_mm']; hw = p11['wall-only (47.2 % of the surface path)']['height_on_PV_axis_mm']
    pct = lambda x, top: round(100 * (x - h0) / (top - h0), 2)
    # split areas: merged mesh (what biv52cut splits) and the v5.1 elements of it / the full mesh
    fa, a, bb = G.interfaces(E, tb)
    lr = (np.isin(tb[a], G.LV_GROUP) & np.isin(tb[bb], G.RV_GROUP)) | (np.isin(tb[a], G.RV_GROUP) & np.isin(tb[bb], G.LV_GROUP))
    F = fa[lr]; Fh = pv.h(P[F].mean(1)); Fa = G.tri_area(P, F)
    new_el = (a[lr] >= nb) | (bb[lr] >= nb)
    fa_f, af, bf = G.interfaces(Ef, tf)
    lrf = (np.isin(tf[af], G.LV_GROUP) & np.isin(tf[bf], G.RV_GROUP)) | (np.isin(tf[af], G.RV_GROUP) & np.isin(tf[bf], G.LV_GROUP))
    Ffl = fa_f[lrf]; Ffh = pv.h(Pf[Ffl].mean(1)); Ffa = G.tri_area(Pf, Ffl)

    def areas(hs):
        m = Fh >= hs
        return {'merged_mesh_split_area_mm2 (biv52cut)': round(float(Fa[m].sum()), 1),
                'of_which_faces_of_elements_added_in_v52 (sleeves, crescents)': round(float(Fa[m & new_el].sum()), 1),
                'v51_elements_only_mm2': round(float(Fa[m & ~new_el].sum()), 1),
                'full_cohort_mesh_mm2 (P11 d)': round(float(Ffa[Ffh >= hs].sum()), 1)}
    rec['c_D32'] = {
        'projection_to_0pct': {'direction': "the PV disc normal (pv.n, the RVOT axis): q = 100 % point - (h(100 %) - h_TA) pv.n, i.e. straight down the PV axis to the TV-ring node's height; the 0 % node is then the posterior (within 60 deg) RV cavity node nearest q",
                               'q_height_mm': round(float(pv.h(q)[0]), 3), 'TA_level_mm': hTA, 'q_to_0pct_node_mm': round(float(np.linalg.norm(Pf[p0] - q)), 2),
                               '0pct_node_height_mm': h0, '0pct_above_TA_level_mm': round(h0 - hTA, 2),
                               'q_inside_element_of_tag (None = outside the mesh, e.g. cavity blood)': q_tag, 'q_to_nearest_RV_cavity_node_any_side_mm': round(float(dq), 2), 'that_node_height_mm': round(float(pv.h(Pf[rn[jq]])[0]), 2)},
        'heights_mm': {'0pct': h0, '100pct (mid-plane ring point, not exactly 0)': h100, 'axial_span (100pct - 0pct)': round(h100 - h0, 3)},
        'axial_pct': {'cut52_boundary': {'height_mm': hc, 'of_span_to_100pct_point': pct(hc, h100), 'of_span_to_mid_plane_0': pct(hc, 0.0)},
                      'wall_only_boundary': {'height_mm': hw, 'of_span_to_100pct_point': pct(hw, h100), 'of_span_to_mid_plane_0': pct(hw, 0.0)}},
        'split_area_above': {'cut52_boundary': areas(hc), 'wall_only_boundary': areas(hw)},
        'stored_cut52_apply_split_area_mm2': json.load(open(os.path.join(HERE, f'cut52_apply_{h}.json')))['merged_mesh_D14_cut']['split_area_mm2 (contact area cut)']}
    G.dump(rec, os.path.join(HERE, f'preview_p12_{h}.json'))
    print(h, json.dumps(rec), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
