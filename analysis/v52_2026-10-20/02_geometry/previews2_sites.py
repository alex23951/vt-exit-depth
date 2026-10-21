"""Read-only previews P3 (D22 "groove sector"), P5 (D25 intramural focus) and P6 (report 34 item 16, De Almeida 2020),
lock thread request relayed 20 Oct 2026 23:13 UTC. Geometry only; no beat; nothing enters the manifest.

P3, my construction of the lock thread's description: on the full cohort mesh's outer surface (2-ring geodesics):
  B = the projB bifurcation (preview_d22_projB: the LV-epicardial candidate nearest 8.3 step 2's 9.59 mm point);
  septal margin = sites52.py's rule from B: the shortest path to the anterior interventricular groove (tag-1/tag-2
    boundary), then down the groove toward lower UVC z until 18.92 mm in all; its end SP;
  R = the geodesic distance B -> SP; the base = the geodesic circle of radius R about B;
  the groove = the left AV groove proxy (tag-1/tag-27 outer-surface boundary) and the shortest path from B to it;
  summit = the tag-1 outer-surface nodes within R of B, between the margin and the groove: the margin path, the B-to-
    groove path and the groove nodes are removed from the 1-ring graph of the disc and the summit is the component on
    the side whose angular extent at B (tangent-plane angles) is the smaller;
  GCV line = the 14.0 mm geodesic circle about B (inner = superior, outer = inferior-lateral);
  one position per part at mid-radius (7.0 mm and (14.0 + R) / 2) on the bisector of the summit's angular extent at B.
P5 (D25 as sent in C5): among the merged-mesh nodes whose straight-line distances to the LV and RV endocardial surfaces
  differ by <= 0.5 mm and whose distance to the epicardial surface exceeds both, the node nearest v5.1's septal-RVOT 10 %
  site (rvot_septal_z_d10). The cut (8.2) changes no coordinate, so the merged mesh's nodes are the cut mesh's (the RV
  copies sit at the same places).
P6: v5.1's RV network (unchanged in v5.2): heights along the pulmonary axis; percentages of the posterior span as the
  axial fraction between the 0 % landmark's height and the pulmonary mid-plane ring's (cut52 landmarks); heights above
  the tricuspid-annulus level of cut52 (the TV-ring cavity node nearest the PV disc).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/previews2_sites.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import sites52 as S52                                                                       # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

R34 = S52.R34
SP_MM, GCV_R = 18.92, 14.0


def tangent_angles(P, out, B, X):
    near = out[np.isin(out, [B]).any(1)]
    nB = np.cross(P[near[:, 1]] - P[near[:, 0]], P[near[:, 2]] - P[near[:, 0]]).sum(0); nB /= np.linalg.norm(nB)
    e1 = np.cross(nB, [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(nB, e1)
    d = X - P[B]
    return np.degrees(np.arctan2(d @ e2, d @ e1)), nB, e1, e2


def extent(ang):
    a = np.sort(ang % 360); g = np.diff(np.r_[a, a[0] + 360]); k = int(np.argmax(g))
    start = a[(k + 1) % len(a)]; ext = 360 - g[k]
    return float(ext), float((start + ext / 2) % 360)


def p3(h, P, E, tag, nod, f2m, Pm, zf, s52sites):
    out = S52.outer_surface(P, E); on = np.unique(out)
    tl = np.zeros((len(P), 30), bool); tl[E.ravel(), np.repeat(tag, 4)] = True
    groove, iv = on[tl[on, 1] & tl[on, 27]], on[tl[on, 1] & tl[on, 2]]
    SF = R34.Surf(P, out)
    pj = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
    B = int(nod[pj['bifurcation_B']['node']])
    dB, _ = SF.dist([B], 2)
    iv_star = int(iv[np.argmin(dB[SF.ids(iv)])])
    p2 = SF.path(B, iv_star, 2); s2 = S52.path_len(P, p2)
    if s2[-1] >= SP_MM:
        SP = int(p2[np.argmin(np.abs(s2 - SP_MM))])
    else:
        rem = SP_MM - s2[-1]
        band = on[cKDTree(P[iv]).query(P[on])[0] <= 1.5]
        mask = np.zeros(len(SF.nodes), bool); mask[SF.ids(band)] = True
        dg, _ = SF.dist([iv_star], 2, mask=mask)
        cand = iv[(np.abs(dg[SF.ids(iv)] - rem) <= 0.75)]
        cand = cand[np.isfinite(zf[cand])]
        SP = int(cand[np.argmin(zf[cand])])
    R = float(dB[SF.ids([SP])[0]])
    g0 = int(groove[np.argmin(dB[SF.ids(groove)])])
    margin = SF.path(B, SP, 1); bg = SF.path(B, g0, 1)
    disc = SF.nodes[(dB <= R) & tl[SF.nodes, 1]]
    keep = np.zeros(len(SF.nodes), bool); keep[SF.ids(disc)] = True
    keep[SF.ids(np.unique(np.r_[margin, bg, groove[np.isin(groove, disc)]]))] = False
    A1 = SF.A.tocoo(); km = keep[A1.row] & keep[A1.col]
    _, lab = connected_components(coo_matrix((np.ones(km.sum()), (A1.row[km], A1.col[km])), shape=A1.shape), directed=False)
    comps = [np.where(keep & (lab == k))[0] for k in np.unique(lab[keep])]
    comps = [cm for cm in comps if len(cm) >= 5]
    best, info = None, []
    for cm in comps:
        ang, nB, e1, e2 = tangent_angles(P, out, B, SF.X[cm])
        ext, mid = extent(ang)
        nodes = SF.nodes[cm]
        info.append({'nodes': int(len(cm)), 'angular_extent_deg': round(ext, 1)})
        if best is None or ext < best[1]:
            best = (nodes, ext, mid)
    rec = {'B_full_node': B, 'B_projection_mm (Euclidean, nearest candidate-quarter node to 8.3 step 2 point)': pj['projB']['projection_distance_mm'],
           'SP_full_node': SP, 'R_geodesic_B_SP_mm': round(R, 2), 'B_to_groove_mm': round(float(dB[SF.ids([g0])[0]]), 2), 'disc_tag1_nodes': int(len(disc)),
           'components_after_cutting_margin_and_groove': info}
    if best is None:
        rec['builds'] = False
        return rec, None
    reg, ext, mid = best
    dr = dB[SF.ids(reg)]
    sup, inf = reg[dr < GCV_R], reg[dr >= GCV_R]
    area = lambda nn: R34.Surf(P, out[np.isin(out, nn).all(1)]).area() if len(nn) else 0.0
    a_all, a_sup = area(reg), area(sup)
    ang, nB, e1, e2 = tangent_angles(P, out, B, P[reg])
    pos = {}
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    old = {('superior' if s['position'] == 'superior' else 'inferior_lateral'): s for s in v51 if s['family'] == 'lv_summit' and s['depth_target'] == 0.5}
    for nm, part, rmid in (('superior', sup, GCV_R / 2), ('inferior_lateral', inf, (GCV_R + R) / 2)):
        if not len(part):
            pos[nm] = None; continue
        pa, _, _, _ = tangent_angles(P, out, B, P[part])
        dpa = dB[SF.ids(part)]
        score = np.abs(dpa - rmid) / max(rmid, 1) + np.radians(np.abs((pa - mid + 180) % 360 - 180))
        p = int(part[np.argmin(score)])
        pm = int(f2m[p])
        pjp = pj['positions'].get(nm)
        pos[nm] = {'surface_node_full': p, 'surface_node': pm, 'on_tag1': bool(tl[p, 1]), 'geodesic_from_B_mm': round(float(dB[SF.ids([p])[0]]), 2),
                   'from_projB_disc_position_mm': round(float(np.linalg.norm(Pm[pm] - Pm[pjp['surface_node']])), 2) if pjp else None,
                   'from_v51_position_mm': round(float(np.linalg.norm(Pm[pm] - Pm[int(old[nm]['surface_node'])])), 2) if nm in old else None}
    rec.update({'builds': bool(len(sup) and len(inf) and all(v and v['on_tag1'] for v in pos.values())),
                'apex_angle_deg (angular extent at B; Kuniewicz 85.46 +- 15.94, range 48-125)': round(ext, 1),
                'area_mm2 (Kuniewicz 287.38 +- 144.95)': round(a_all, 1), 'superior_share (Kuniewicz 0.545)': round(a_sup / a_all, 3) if a_all else None,
                'positions': pos, 'tip_B_mm': P[B].round(3).tolist()})
    # LCC to the vein arc (8.8, Yamada 14.3 +- 3.5): the cusp52 LCC sites to the nearest 14.0 mm-circle node of the summit
    arc = reg[np.abs(dr - GCV_R) <= 0.75]
    lcc = [s for s in s52sites if s['family'] == 'cusp_crescent' and s['position'].startswith('lcc')]
    rec['LCC_to_vein_arc_mm (Yamada 14.3 +- 3.5)'] = {s['id']: round(float(np.linalg.norm(P[arc] - Pm[int(s['node'])], axis=1).min()), 2) for s in lcc} if len(arc) else None
    # projB disc (D22 as sent): angular extent at B and LCC to its arc (14.0 mm straight-line circle about its B in the disc)
    Bm = pj['bifurcation_B']['node']
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    epi = read_vtx(os.path.join(V, 'surfaces', 'epi.vtx'))
    zz, phi, vv = (np.loadtxt(os.path.join(V, 'uvc', n + '.dat')) for n in ('z', 'phi', 'v'))
    candq = epi[(vv[epi] == 0) & (np.sin(phi[epi]) >= 0) & (zz[epi] >= 0.75)]
    A = P[int(json.load(open(os.path.join(HERE, f'sites52_{h}.json')))['summit_reanchored']['ostium_full_node'])]
    dBd = np.linalg.norm(Pm[candq] - Pm[Bm], axis=1); dA = np.linalg.norm(Pm[candq] - A, axis=1)
    sec = candq[(dBd <= 18.9) & (dA > np.linalg.norm(Pm[Bm] - A))]
    arc2 = sec[np.abs(np.linalg.norm(Pm[sec] - Pm[Bm], axis=1) - 14.0) < 1.0]
    rec['projB_disc'] = {'angular_extent_at_B_deg': pj['sector_apex_angle_deg (Kuniewicz 85.46 +- 15.94)'],
                         'LCC_to_vein_arc_mm': {s['id']: round(float(np.linalg.norm(Pm[arc2] - Pm[int(s['node'])], axis=1).min()), 2) for s in lcc} if len(arc2) else None}
    # tag 27
    t3 = on[tl[on, 3] & tl[on, 27]]
    dj = cKDTree(P[t3]).query(P[groove])[0] if len(t3) else None
    rec['tag27'] = {'what': 'AV_plane (tags_lvrv.json): the atrioventricular-plane layer of the four-chamber mesh between the atrial and ventricular myocardium',
                    'why_its_tag1_edge': 'the LV (tag 1) never touches the LA (tag 3) on these meshes; its outer surface meets tag 27 along the basal epicardial edge, which is where the left AV groove (and the LCx) lies, the edge v5.1 used for its GCV proxy',
                    'tag1_tag27_edge_to_tag3_tag27_edge_mm (median, min, max)': [round(float(np.median(dj)), 2), round(float(dj.min()), 2), round(float(dj.max()), 2)] if dj is not None else None}
    return rec, P[SP]


def run(h):
    t0 = time.time()
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces')
    P, E, tag = G.load_full(h)
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3
    nod = np.fromfile(os.path.join(V, 'biv52.nod'), dtype=np.int64)
    f2m = np.full(len(P), -1, np.int64); f2m[nod] = np.arange(len(nod))
    zf = np.full(len(P), np.nan); zf[nod] = np.loadtxt(os.path.join(V, 'uvc', 'z.dat'))
    s52 = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    rec['P3_groove_sector'], SPx = p3(h, P, E, tag, nod, f2m, Pm, zf, s52)
    # P5
    lve, rve, epi = (read_vtx(os.path.join(S, n + '.vtx')) for n in ('lv_endo', 'rv_endo', 'epi'))
    dl, dr, de = (cKDTree(Pm[x]).query(Pm)[0] for x in (lve, rve, epi))
    ok = (np.abs(dl - dr) <= 0.5) & (de > dl) & (de > dr)
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    anc = int(next(s['node'] for s in v51 if s['id'] == 'rvot_septal_z_d10'))
    cand = np.where(ok)[0]
    foc = int(cand[np.argmin(np.linalg.norm(Pm[cand] - Pm[anc], axis=1))])
    pv, _ = G.pulmonary_frame(P, E, tag)
    rvn = rve[np.argmin(np.linalg.norm(Pm[rve] - Pm[foc], axis=1))]
    rec['P5_focus'] = {'anchor_v51_rvot_septal_z_d10_node': anc, 'focus_node': foc, 'candidate_nodes': int(len(cand)),
                       'distance_from_anchor_mm': round(float(np.linalg.norm(Pm[foc] - Pm[anc])), 2),
                       'dist_LV_RV_epi_mm': [round(float(dl[foc]), 2), round(float(dr[foc]), 2), round(float(de[foc]), 2)],
                       'nearest_RV_endo_node_below_PV_mid_plane_mm (Acosta 9.2 +- 7)': round(float(-pv.h(Pm[rvn])[0]), 2),
                       'distance_to_P3_SP_mm': round(float(np.linalg.norm(Pm[foc] - SPx)), 2) if SPx is not None else None}
    # P6
    net = np.load(os.path.join(G.REPO, 'data', 'biv', h, 'purkinje_v51', 'network_v51.npz'))
    nodes, kind, pmj = net['nodes'], net['kind'].astype(str), net['pmj']
    L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
    h0, h100, hTA, hs = L['height_0pct_mm'], L['height_100pct_mm'], L['tricuspid_level_height_mm'], L['split_height_mm']
    hd = pv.h(Pm[nodes[kind == 'distal_rv']]); hp = pv.h(Pm[nodes[pmj[kind[pmj] == 'distal_rv']]])
    pct = lambda x: round(float(100 * (x - h0) / (h100 - h0)), 1)
    rec['P6_RV_network_heights'] = {'heights_mm (0 % landmark, PV mid-plane ring, TA level, D14 boundary)': [h0, h100, hTA, hs],
                                    'highest_distal_rv_node': {'height_mm': round(float(hd.max()), 2), 'pct_of_posterior_span (axial)': pct(hd.max()), 'above_TA_level_mm': round(float(hd.max() - hTA), 2)},
                                    'highest_RV_PMJ': {'height_mm': round(float(hp.max()), 2), 'pct_of_posterior_span (axial)': pct(hp.max()), 'above_TA_level_mm': round(float(hp.max() - hTA), 2)},
                                    'RV_PMJs': int(len(hp)), 'RV_PMJs_above_the_0pct_landmark': int((hp > h0).sum()), 'RV_PMJs_above_the_D14_boundary': int((hp > hs).sum())}
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'previews2_sites_{h}.json'))
    r3 = rec['P3_groove_sector']
    print(h, 'P3 builds', r3.get('builds'), {k: r3.get(k) for k in ('apex_angle_deg (angular extent at B; Kuniewicz 85.46 +- 15.94, range 48-125)', 'area_mm2 (Kuniewicz 287.38 +- 144.95)', 'superior_share (Kuniewicz 0.545)', 'R_geodesic_B_SP_mm')},
          '| P5', rec['P5_focus']['distance_from_anchor_mm'], rec['P5_focus']['nearest_RV_endo_node_below_PV_mid_plane_mm (Acosta 9.2 +- 7)'], '| P6', rec['P6_RV_network_heights']['RV_PMJs_above_the_0pct_landmark'], rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
