"""v5.2 step 2e: the new site sets against the ledger of LOCK.md 11.2a, their placement checks, capture and muscle fraction.

New sets built here (positions are mesh nodes of the merged mesh data/biv/<H>/v52/biv52, v5.1 ids kept):
  cusp_crescent (8.5 item 11b, D13, D15): 4 per heart, theta 79.5 / 93.1 (LCC) and 170.8 / 188.4 deg (RCC) in the D15
    frame; the built extent at that theta = the highest LV-muscle element centroid above the aortic mid-plane ring within
    +-2.5 deg (crescents add none, so the existing muscle, as 2c reported); the site at 50 % of it, at mid-thickness: the
    LV nodes within +-2.5 deg and +-0.5 mm of that height, the radial run from the innermost node outward until a gap
    over 1.5 mm, the node nearest the run's radial midpoint.
  supravalvar (8.6): 3 per heart at the pulmonary sinus centres (posterior 0, +-120 deg); the sleeve length = the highest
    RV-muscle (sleeve included) element centroid above the pulmonary mid-plane ring within +-2.5 deg; the site at 50 % of
    it, mid-thickness as above (radial from the pulmonary axis).
  summit_reanchored, as built (D22, ADOPTED 21 Oct 2026 05:18:22 UTC, projB + option A): v5.1's own summit construction
    (preview_d22.py, 11_site_grid.py's rules on the v5.2 UVC) with B = the candidate-quarter node nearest 8.3 step 2's
    point below, the sector = candidates within 18.9 mm of B and farther from the ostium than B, two positions, four
    depths each; these 8 sites enter the manifest (count = D24, pending). The 8.3 steps 2-6 construction below is kept
    as a report only (its triangle degenerates on these meshes, Q6b).
  summit_reanchored, 8.3 as written (report only): the LCA ostium on the aortic root's outer surface at theta 56.2 deg (D15), 14.8 mm above the
    aortic mid-plane (the tag-5 outer-surface node of largest radius within +-0.75 mm and +-3 deg); the bifurcation B at
    9.59 mm along the outer surface (2-ring geodesic) on the shortest path toward the left AV groove; the septal margin
    18.92 mm from B toward the anterior interventricular groove (shortest path to the tag-1/tag-2 boundary, then down
    it toward the apex); the base = the shortest path from that end (SP) to the left AV groove; the triangle B-SP-G closed
    by the shortest path G-B. Mesh limits (mine, reported): the mesh has no tag-1/tag-3 boundary (the LV never touches
    the LA; tag 27, the AV plane, lies between), so the left AV groove is the tag-1/tag-27 boundary on the outer surface;
    the bisector of the apex angle splits the triangle; the superior half is the one whose centroid is higher (+z: the
    CT pose has no rotation); one position per half, the epicardial node nearest the half's centroid, at v5.1's four
    depths (0.1 / 0.5 / 0.75 / 0.9 from the endocardial end along the inward normal), pending the lock thread's Q6.
  intramural (report 26, pending Q7): a mid-wall septal focus (sep 0.5) under report 34 item 14's central septal point,
    and a 3 x 3 grid at 5 mm spacing on each septal endocardium (LV, RV) centred on the endocardial node nearest it.
  gate7a_patch_centres: report 34 item 14's three centres, written into the manifest (patches for scoring, not sites).
Every site (v5.1's kept sites included) gets the 8.7 capture test on the cut mesh (biv52cut): nodes within 1.5 mm
(strict) of the site, excitable (not the sleeve fibrous layer), in the site node's connected component inside the ball
(tet edges of the cut mesh, so the infundibulum cut is not crossed); valid if >= 4 nodes. Muscle fraction = share of
4,000 uniform points of the ball that lie in a tet of the simulation mesh.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/sites52.py [HEART ...]
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
import geom52 as G                                                                          # noqa: E402
import sheet52 as S52                                                                       # noqa: E402
from common import boundary_faces, read_elem, read_pts, read_vtx                            # noqa: E402

R34 = S52.R34
CUSP = {'lcc_mid': 79.5, 'lcc_q': 93.1, 'rcc_mid': 170.8, 'rcc_q': 188.4}
SINUS = {'posterior': 0.0, 'sinus_+120': 120.0, 'sinus_-120': 240.0}
LCA_THETA, LCA_H, BIF_MM, SP_MM = 56.2, 14.8, 9.59, 18.92
DEPTHS = (0.1, 0.5, 0.75, 0.9)
BALL_R, CAPTURE_MIN = 1.5, 4
STEP, OUT_TOL = 0.2, 0.9
RV_FAMILIES = {'rv_free_wall', 'rvot', 'supravalvar', 'intramural_rv_grid'}


def radial_mid(valve, P, nodes, th_c, h_c, gap=1.5):
    th = valve.theta(P[nodes]); hh = valve.h(P[nodes]); r = valve.r(P[nodes])
    m = (np.abs((th - th_c + 180) % 360 - 180) <= 2.5) & (np.abs(hh - h_c) <= 0.5)
    if not m.any():
        return None
    rr = np.sort(r[m]); k = np.where(np.diff(rr) > gap)[0]
    r_in, r_out = rr[0], rr[k[0]] if len(k) else rr[-1]
    rm = 0.5 * (r_in + r_out)
    tgt = valve.c + h_c * valve.n + rm * (np.cos(np.radians(valve.a0 + valve.sign * th_c)) * valve.e1 + np.sin(np.radians(valve.a0 + valve.sign * th_c)) * valve.e2)
    cand = nodes[m]
    i = int(np.argmin(np.linalg.norm(P[cand] - tgt, axis=1)))
    return {'node': int(cand[i]), 'r_inner_mm': round(float(r_in), 2), 'r_outer_mm': round(float(r_out), 2), 'thickness_mm': round(float(r_out - r_in), 2),
            'target_mm': tgt.round(3).tolist(), 'node_to_target_mm': round(float(np.linalg.norm(P[cand[i]] - tgt)), 2)}


def extent(valve, P, E, mask, th_c, rmax):
    cen = P[E[mask]].mean(1)
    m = (valve.r(cen) < rmax) & (valve.h(cen) > -6) & (valve.h(cen) < 30) & (np.abs((valve.theta(cen) - th_c + 180) % 360 - 180) <= 2.5)
    return float(valve.h(cen[m]).max()) if m.any() else np.nan


def outer_surface(P, E):
    bf, own = boundary_faces(E); n = len(P)
    fe = np.vstack([np.sort(bf[:, [0, 1]], 1), np.sort(bf[:, [1, 2]], 1), np.sort(bf[:, [0, 2]], 1)]); fid = np.tile(np.arange(len(bf)), 3)
    key = fe[:, 0] * n + fe[:, 1]; o = np.argsort(key); ks = key[o]; fs = fid[o]; sm = ks[1:] == ks[:-1]
    _, lab = connected_components(coo_matrix((np.ones(sm.sum()), (fs[:-1][sm], fs[1:][sm])), shape=(len(bf), len(bf))), directed=False)
    return bf[lab == np.argmax(np.bincount(lab))]


def path_len(P, p):
    return np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[p], axis=0), axis=1))]


def depth_line(Pm, tree_m, epi_tri_m, p, epi_start, depths=DEPTHS):
    """v5.1 11_site_grid.py rule: inward wall normal (area-weighted normal of surface triangles within 4 mm), marched in
    0.2 mm steps until it leaves the tissue (nearest node > 0.9 mm for 2 steps); site for depth d at p + d' T n."""
    X = Pm[epi_tri_m]; c = X.mean(1)
    near = np.linalg.norm(c - Pm[p], axis=1) <= 4.0
    nrm = np.cross(X[near, 1] - X[near, 0], X[near, 2] - X[near, 0]).sum(0)
    # inward: toward the tissue (test both senses)
    best = None
    for sgn in (1, -1):
        n_in = sgn * nrm / np.linalg.norm(nrm)
        out, t = 0, 0.0
        while True:
            t += STEP
            d, _ = tree_m.query(Pm[p] + t * n_in)
            out = out + 1 if d > OUT_TOL else 0
            if out >= 2 or t > 40:
                break
        T = t - 2 * STEP
        if best is None or T > best[1]:
            best = (n_in, T)
    n_in, T = best
    res = []
    for dd in depths:
        frac = (1 - dd) if epi_start else dd
        tgt = Pm[p] + frac * T * n_in
        _, i = tree_m.query(tgt)
        res.append({'depth_target': dd, 'node': int(i), 'wall_thickness_mm': round(float(T), 2),
                    'depth_achieved_mm_from_start': round(float(np.dot(Pm[i] - Pm[p], n_in)), 2)})
    return res, n_in


def summit(h, P, E, tag, f2m, Pm, tree_m, epi_tri_m, av):
    out = outer_surface(P, E)
    on = np.unique(out)
    tl = np.zeros((len(P), 30), bool); tl[E.ravel(), np.repeat(tag, 4)] = True
    t5 = on[tl[on, 5]]
    hh, th, rr = av.h(P[t5]), av.theta(P[t5]), av.r(P[t5])
    for win in (3.0, 6.0):
        m = (np.abs(hh - LCA_H) <= 0.75) & (np.abs((th - LCA_THETA + 180) % 360 - 180) <= win)
        if m.any():
            break
    O = int(t5[m][np.argmax(rr[m])])
    groove, iv = on[tl[on, 1] & tl[on, 27]], on[tl[on, 1] & tl[on, 2]]
    SF = R34.Surf(P, out)
    d0, _ = SF.dist([O], 2)
    g_star = int(groove[np.argmin(d0[SF.ids(groove)])])
    p1 = SF.path(O, g_star, 2); s1 = path_len(P, p1)
    B = int(p1[np.argmin(np.abs(s1 - BIF_MM))])
    dB, _ = SF.dist([B], 2)
    iv_star = int(iv[np.argmin(dB[SF.ids(iv)])])
    p2 = SF.path(B, iv_star, 2); s2 = path_len(P, p2)
    zf = np.full(len(P), np.nan); zf[f2m >= 0] = np.loadtxt(os.path.join(G.REPO, 'data', 'biv', h, 'v52', 'uvc', 'z.dat'))[f2m[f2m >= 0]]
    if s2[-1] >= SP_MM:
        SP = int(p2[np.argmin(np.abs(s2 - SP_MM))]); lad = p2
    else:
        rem = SP_MM - s2[-1]
        # along the anterior interventricular groove (its nodes and those within 1.5 mm), toward the apex (lower UVC z)
        band = on[cKDTree(P[iv]).query(P[on])[0] <= 1.5]
        mask = np.zeros(len(SF.nodes), bool); mask[SF.ids(band)] = True
        dg, _ = SF.dist([iv_star], 2, mask=mask)
        cand = iv[np.abs(dg[SF.ids(iv)] - rem) <= 0.75]
        cand = cand[np.isfinite(zf[cand])]
        SP = int(cand[np.argmin(zf[cand])]) if len(cand) else int(iv[np.nanargmin(np.where(np.isfinite(dg[SF.ids(iv)]), np.abs(dg[SF.ids(iv)] - rem), np.inf))])
        lad = np.r_[p2, SF.path(iv_star, SP, 2)[1:]]
    dS, _ = SF.dist([SP], 2)
    G_ = int(groove[np.argmin(dS[SF.ids(groove)])])
    # boundary loops on the 1-ring graph (watertight), lengths on the 2-ring graph
    b1 = np.r_[SF.path(B, SP, 1), SF.path(SP, G_, 1)[1:], SF.path(G_, B, 1)[1:]]
    keep = np.ones(len(SF.nodes), bool); keep[SF.ids(np.unique(b1))] = False
    A1 = SF.A.tocoo(); km = keep[A1.row] & keep[A1.col]
    _, lab = connected_components(coo_matrix((np.ones(km.sum()), (A1.row[km], A1.col[km])), shape=A1.shape), directed=False)
    tri_c = (P[B] + P[SP] + P[G_]) / 3
    lv_out = keep & tl[SF.nodes, 1]
    seed = np.where(lv_out)[0][np.argmin(np.linalg.norm(SF.X[lv_out] - tri_c, axis=1))]
    reg = SF.nodes[(lab == lab[seed]) & keep]
    reg = np.union1d(reg, np.unique(b1))
    reg = reg[tl[reg, 1]]                                        # LV epicardium only
    sizes = np.bincount(lab[keep])
    area = R34.Surf(P, out[np.isin(out, reg).all(1)]).area() if len(reg) else 0.0
    # apex angle and bisector in the tangent plane at B
    nB = np.cross(P[out[np.isin(out, [B]).any(1)][:, 1]] - P[out[np.isin(out, [B]).any(1)][:, 0]],
                  P[out[np.isin(out, [B]).any(1)][:, 2]] - P[out[np.isin(out, [B]).any(1)][:, 0]]).sum(0); nB /= np.linalg.norm(nB)
    def tdir(p):
        s = path_len(P, p); q = P[p[min(np.searchsorted(s, 3.0), len(p) - 1)]] - P[B]
        q = q - (q @ nB) * nB; return q / np.linalg.norm(q)
    uL, uC = tdir(SF.path(B, SP, 2)), tdir(SF.path(B, G_, 2))
    apex_angle = float(np.degrees(np.arccos(np.clip(uL @ uC, -1, 1))))
    ub = (uL + uC) / np.linalg.norm(uL + uC)
    perp = np.cross(nB, ub)
    side = np.sign((P[reg] - P[B]) @ perp)
    lad_side = np.sign(uL @ perp)
    halves = {'lad_side': reg[side == lad_side], 'lcx_side': reg[side != lad_side]}
    zc = {k: float(P[v][:, 2].mean()) if len(v) else -np.inf for k, v in halves.items()}
    sup = max(zc, key=zc.get)
    names = {sup: 'superior', [k for k in halves if k != sup][0]: 'inferior'}
    # GCV proxy arc: the bisector from B to the base, length on the surface
    base = SF.path(SP, G_, 2)
    bproj = (P[base] - P[B]) @ perp
    jb = base[np.argmin(np.abs(bproj))]
    gcv = float(path_len(P, SF.path(B, int(jb), 2))[-1])
    pos = {}
    for k, v in halves.items():
        v_m = f2m[v]; ok = v_m >= 0
        c = P[v[ok]].mean(0)
        p = int(v[ok][np.argmin(np.linalg.norm(P[v[ok]] - c, axis=1))])
        pos[names[k]] = {'surface_node_full': p, 'surface_node': int(f2m[p]), 'half': k, 'half_nodes': int(len(v)),
                         'dist_to_B_mm': round(float(np.linalg.norm(P[p] - P[B])), 2)}
    geo = {'ostium_full_node': O, 'ostium_h_theta_r': [round(float(av.h(P[O])[0]), 2), round(float(av.theta(P[O])[0]), 1), round(float(av.r(P[O])[0]), 2)],
           'ostium_candidates_and_window_deg': [int(m.sum()), win],
           'left_AV_groove_proxy': 'tag-1 / tag-27 (AV plane) boundary on the outer surface; no tag-1 / tag-3 boundary exists',
           'ostium_to_groove_mm (2-ring)': round(float(s1[-1]), 2), 'bifurcation_full_node': B, 'B_along_path_mm': round(float(s1[np.where(p1 == B)[0][0]]), 2),
           'B_to_IV_groove_mm': round(float(s2[-1]), 2), 'SP_full_node': SP, 'septal_margin_mm (B->SP, 2-ring)': round(float(path_len(P, lad)[-1]), 2),
           'base_end_on_groove_full_node': G_, 'base_mm (SP->G)': round(float(path_len(P, base)[-1]), 2),
           'lcx_side_mm (G->B)': round(float(path_len(P, SF.path(G_, B, 2))[-1]), 2),
           'apex_angle_deg (Kuniewicz 85.46 +- 15.94)': round(apex_angle, 1), 'gcv_proxy_arc_mm (bisector B->base; v5.1 14.0)': round(gcv, 2),
           'triangle_LV_epicardial_nodes': int(len(reg)), 'triangle_area_mm2 (Kuniewicz area 287 +- 145)': round(area, 1),
           'outside_component_sizes_check': sorted(sizes.tolist(), reverse=True)[:3], 'superior_half': sup, 'positions': pos}
    sites = []
    for nm, pz in pos.items():
        res, _ = depth_line(Pm, tree_m, epi_tri_m, pz['surface_node'], True)
        for r in res:
            sites.append({'id': f'summit52_{nm}_d{int(round(r["depth_target"] * 100))}', 'family': 'summit_reanchored', 'position': nm,
                          'surface_node': pz['surface_node'], **r, 'dist_to_summit_tip_mm': round(float(np.linalg.norm(Pm[r['node']] - P[B])), 2)})
    return geo, sites, P[B]


def run(h):
    t0 = time.time()
    B_ = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B_, 'v52')
    P, E, tag = G.load_full(h)
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3; Em, tm = read_elem(os.path.join(V, 'biv52'))
    nod = np.fromfile(os.path.join(V, 'biv52.nod'), dtype=np.int64)
    f2m = np.full(len(P), -1, np.int64); f2m[nod] = np.arange(len(nod))
    z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
    tag2 = tag.copy(); tag2[z['crescent_elements']] = 1; tag2[z['sleeve_elements']] = 2
    av, _ = G.aortic_frame(P, E, tag); pv, _ = G.pulmonary_frame(P, E, tag)
    S = os.path.join(V, 'surfaces')
    epi_tri_m = np.loadtxt(os.path.join(S, 'epi.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    tree_m = cKDTree(Pm)
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    new = []
    # cusp sites
    lvm = np.isin(tag2, G.LV_GROUP); lvn = np.unique(E[lvm])
    rra = float(np.median(av.r(P[av.ring])))
    cusp = {}
    for k, thc in CUSP.items():
        H = extent(av, P, E, lvm, thc, rra + 6)
        mid = radial_mid(av, P, lvn, thc, 0.5 * H) if np.isfinite(H) else None
        cusp[k] = {'theta_deg': thc, 'built_extent_mm': round(H, 2), 'site_height_mm': round(0.5 * H, 2), **(mid or {'node': None})}
        if mid:
            new.append({'id': f'cusp52_{k}', 'family': 'cusp_crescent', 'position': k, 'node': int(f2m[mid['node']]), 'theta_deg': thc,
                        'height_mm': round(0.5 * H, 2), 'thickness_mm': mid['thickness_mm']})
    rec['cusp_crescent'] = cusp
    # supravalvar sites
    rvm = np.isin(tag2, G.RV_GROUP); rvn = np.unique(E[rvm])
    rrp = float(np.median(pv.r(P[pv.ring])))
    supra = {}
    for k, thc in SINUS.items():
        H = extent(pv, P, E, rvm, thc, rrp + 6)
        mid = radial_mid(pv, P, rvn, thc, 0.5 * H) if np.isfinite(H) else None
        supra[k] = {'theta_deg': thc, 'sleeve_length_mm': round(H, 2), 'site_height_mm': round(0.5 * H, 2), **(mid or {'node': None})}
        if mid:
            new.append({'id': f'supra52_{k}', 'family': 'supravalvar', 'position': k, 'node': int(f2m[mid['node']]), 'theta_deg': thc,
                        'height_mm': round(0.5 * H, 2), 'thickness_mm': mid['thickness_mm']})
    rec['supravalvar'] = supra
    # re-anchored summit
    geo, ssites, tip = summit(h, P, E, tag, f2m, Pm, tree_m, epi_tri_m, av)
    rec['summit_reanchored'] = geo
    v51 = json.load(open(os.path.join(B_, 'sites.json')))
    old = {(('superior' if s['position'] == 'superior' else 'inferior'), s['depth_target']): s for s in v51 if s['family'] == 'lv_summit'}
    for s in ssites:
        o = old.get((s['position'], s['depth_target']))
        s['moved_from_v51_mm'] = round(float(np.linalg.norm(Pm[s['node']] - Pm[int(o['node'])])), 2) if o else None
    # not entered in the manifest: the triangle of 8.3 steps 2-6 degenerates on these meshes (Q6b to the lock thread)
    rec['summit_reanchored']['sites_as_constructed (not in the manifest; pending Q6 / Q6b)'] = ssites
    # intramural (report 26), default pending Q7
    r34 = json.load(open(os.path.join(G.REPO, 'analysis', 'v52_2026-10-20', '00_step0', f'report34_{h}.json')))
    cen = int(r34['item14']['patch_centres']['central']['node'])
    sep = np.loadtxt(os.path.join(V, 'uvc', 'sep.dat'))
    lve, rve = read_vtx(os.path.join(S, 'lv_endo.vtx')), read_vtx(os.path.join(S, 'rv_endo.vtx'))
    # focus: along the straight line from the LV endocardial centre point to the nearest RV endocardial node, the node with sep nearest 0.5
    q = rve[np.argmin(np.linalg.norm(Pm[rve] - Pm[cen], axis=1))]
    seg = Pm[cen] + np.linspace(0, 1, 60)[:, None] * (Pm[q] - Pm[cen])
    nn = np.unique(tree_m.query(seg)[1])
    foc = int(nn[np.argmin(np.abs(sep[nn] - 0.5))])
    new.append({'id': 'intramural52_focus', 'family': 'intramural_focus', 'position': 'mid-wall septum', 'node': foc, 'sep': round(float(sep[foc]), 3)})
    for nm, surf in (('lv', 'lv_endo'), ('rv', 'rv_endo')):
        tri = np.loadtxt(os.path.join(S, surf + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
        SF = R34.Surf(Pm, tri)
        c0 = int(SF.nodes[np.argmin(np.linalg.norm(SF.X - Pm[foc], axis=1))])
        d, _ = SF.dist([c0], 2)
        zz = np.loadtxt(os.path.join(V, 'uvc', 'z.dat'))
        # two surface directions at c0: base-apex (UVC z gradient) and its perpendicular in the tangent plane
        near = SF.nodes[d <= 6.0]
        Xn = Pm[near] - Pm[c0]
        nrm = np.linalg.svd(Xn - Xn.mean(0))[2][2]
        gz = np.linalg.lstsq(Xn, zz[near] - zz[c0], rcond=None)[0]; gz -= (gz @ nrm) * nrm; gz /= np.linalg.norm(gz)
        ga = np.cross(nrm, gz)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                tgt = Pm[c0] + 5.0 * (i * gz + j * ga)
                k = int(SF.nodes[np.argmin(np.linalg.norm(SF.X - tgt, axis=1))])
                new.append({'id': f'intramural52_{nm}grid_{i + 1}{j + 1}', 'family': f'intramural_{nm}_grid', 'position': f'{i},{j}', 'node': k,
                            'surface_mm_from_centre': round(float(d[SF.ids([k])[0]]), 2)})
    # re-anchored summit sites built by D22 (ADOPTED, Alex 21 Oct 2026 05:18:22 UTC: projB + option A, v5.1's disc started
    # from the ostium anchor): preview_d22.py's construction with B = the candidate-quarter node nearest step 2's point
    # (D22's relative stop: B is no farther from that point than the nearest tag-1 epicardial node). 8 sites per heart
    # (2 positions x 4 depths); the count is D24, still pending (geometry may be built, nothing runs on it).
    import preview_d22 as D22
    used = {int(s['node']) for s in v51} | {int(s['node']) for s in new}
    d22 = D22.construct(h, 'projB', used=used, s52sum=geo)
    tip = np.array(d22.pop('_B_xyz')); d22.pop('_out_json')
    for s in d22['sites (preview, not in the manifest)']:
        pos_nm = 'superior' if '_superior_' in s['id'] else 'inferior_lateral'
        new.append({'id': s['id'], 'family': 'summit_reanchored', 'position': pos_nm, 'node': int(s['node']), 'depth_target': s['depth_target'],
                    'surface_node': d22['positions'][pos_nm]['surface_node'], 'moved_from_v51_mm': s['moved_from_v51_mm'],
                    'dist_to_tip_B_mm (8.4)': s['dist_to_tip_B_mm (8.4)'], 'construction': 'D22 projB, option A'})
    rec['summit_D22'] = {k: v for k, v in d22.items() if k != 'sites (preview, not in the manifest)'}
    rec['gate7a_patch_centres'] = r34['item14']['patch_centres']
    # ---------------- 8.7 capture and muscle fraction on every site
    Pc = read_pts(os.path.join(V, 'biv52cut')) / 1e3; Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    dupsrc = np.load(os.path.join(V, 'cut_dup52.npy'))
    dupof = np.full(len(Pm), -1); dupof[dupsrc[len(Pm):]] = np.arange(len(Pm), len(Pc))
    fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
    nonex = np.zeros(len(Pc), bool); nonex[fib] = True; nonex[dupof[fib][dupof[fib] >= 0]] = True
    from cut52 import adjacency
    A = adjacency(Ec, len(Pc))
    tc = cKDTree(Pc)
    a_, Jinv = None, None
    cen_m = Pm[Em].mean(1); tree_e = cKDTree(cen_m)
    x0 = Pm[Em[:, 0]]; J = np.stack([Pm[Em[:, 1]] - x0, Pm[Em[:, 2]] - x0, Pm[Em[:, 3]] - x0], axis=2)
    rng = np.random.default_rng(0)
    U = rng.normal(size=(4000, 3)); U /= np.linalg.norm(U, axis=1, keepdims=True); U *= BALL_R * rng.random(4000)[:, None] ** (1 / 3)
    def inside_frac(c):
        pts = c + U
        _, nb = tree_e.query(pts, k=24)
        lam = np.linalg.solve(J[nb], (pts[:, None, :] - x0[nb])[..., None])[..., 0]
        ins = (lam >= -1e-9).all(-1) & (lam.sum(-1) <= 1 + 1e-9)
        return float(ins.any(1).mean())
    def capture(node, fam):
        n = int(node)
        if fam in RV_FAMILIES and dupof[n] >= 0:
            n = int(dupof[n])
        ball = np.array(tc.query_ball_point(Pc[n], BALL_R - 1e-9))
        plain = len(ball)
        ex = ball[~nonex[ball]]
        if n not in set(ex.tolist()):
            return {'cut_node': n, 'ball_nodes': plain, 'stimulated': 0, 'valid': False, 'note': 'site node not excitable'}
        sub = A[ex][:, ex]
        _, lb = connected_components(sub, directed=False)
        st = ex[lb == lb[np.where(ex == n)[0][0]]]
        return {'cut_node': n, 'ball_nodes': plain, 'stimulated': int(len(st)), 'valid': bool(len(st) >= CAPTURE_MIN),
                'same_as_plain_ball': bool(len(st) == plain)}
    allsites = [{'id': s['id'], 'family': s['family'], 'node': int(s['node']), 'set': 'v51'} for s in v51] + [dict(s, set='v52_new') for s in new]
    cap = []
    for s in allsites:
        c = capture(s['node'], s['family'])
        c['muscle_fraction'] = round(inside_frac(Pm[s['node']]), 3)
        cap.append({'id': s['id'], 'family': s['family'], 'set': s['set'], 'node': s['node'], **c})
    rec['capture'] = {'sites': len(cap), 'invalid': [c['id'] for c in cap if not c['valid']],
                      'v51_sites_whose_stimulated_set_differs_from_the_plain_ball': [c['id'] for c in cap if c['set'] == 'v51' and not c.get('same_as_plain_ball', True)],
                      'muscle_fraction_new_sites': {c['id']: c['muscle_fraction'] for c in cap if c['set'] == 'v52_new'},
                      'muscle_fraction_v51_outflow_sites': {c['id']: c['muscle_fraction'] for c in cap if c['set'] == 'v51' and c['family'] in ('aortic_cusp', 'rvot', 'lv_summit')}}
    # ---------------- 8.4 / 8.8 reports
    pvr = read_vtx(os.path.join(S, 'pv_rim.vtx'))
    tpv = cKDTree(Pm[pvr])
    rec['8.4_dist_to_summit_tip_mm'] = {s['id']: round(float(np.linalg.norm(Pm[int(s['node'])] - tip)), 2) for s in allsites
                                        if s['family'] in ('lv_summit', 'summit_reanchored', 'aortic_cusp', 'cusp_crescent', 'lv_vein_course')}
    rec['8.8'] = {'PV_to_LCC_mm (Acosta 5 +- 3)': [round(float(tpv.query(Pm[s['node']])[0]), 2) for s in new if s['family'] == 'cusp_crescent' and s['position'].startswith('lcc')],
                  'PV_to_RCC_mm (Acosta 11 +- 5)': [round(float(tpv.query(Pm[s['node']])[0]), 2) for s in new if s['family'] == 'cusp_crescent' and s['position'].startswith('rcc')],
                  'RVOT_sites_below_PV_mm (within 10)': {s['id']: round(float(-pv.h(Pm[int(s['node'])])[0]), 2) for s in v51 if s['family'] == 'rvot'},
                  'LCC_to_summit_GCV_proxy_mm (Yamada 14.3 +- 3.5; GCV/AIV not in the mesh: the summit sites stand in)':
                      [round(float(np.linalg.norm(Pm[a['node']] - Pm[b['node']])), 2) for a in new if a['family'] == 'cusp_crescent' and a['position'].startswith('lcc')
                       for b in new if b['family'] == 'summit_reanchored' and b['depth_target'] == 0.9]}
    D = os.path.join(V, 'sites52.json')
    G.dump({'heart': h, 'lock_sha256': G.LOCK_SHA, 'new_sites': new, 'gate7a_patch_centres': rec['gate7a_patch_centres'],
            'v51_sites': 'data/biv/<H>/sites.json (kept unchanged)', 'capture': cap}, D)
    rec['files'] = {'manifest': os.path.relpath(D, G.REPO), 'sha256': G.sha256(D)}
    rec['counts'] = {f: sum(1 for s in new if s['family'] == f) for f in sorted({s['family'] for s in new})}
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'sites52_{h}.json'))
    print(h, rec['counts'], 'invalid', rec['capture']['invalid'], 'summit', {k: rec['summit_reanchored'][k] for k in ('apex_angle_deg (Kuniewicz 85.46 +- 15.94)', 'triangle_area_mm2 (Kuniewicz area 287 +- 145)', 'gcv_proxy_arc_mm (bisector B->base; v5.1 14.0)')}, rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
