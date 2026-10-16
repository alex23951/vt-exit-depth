"""Audit 04: anatomy of the three hearts from the saved meshes (read only). Coordinates mm (cohort um / 1000).
Cavity volumes: endocardial surface (oriented away from the owning tet = into the cavity, then flipped) closed by
centroid fans over each boundary loop (valve openings). Wall thickness: nearest-surface distance from endocardial
nodes (to the epicardium for free walls, to the opposite endocardium for the septum). Torso frame: x @ R.T + t
(08_torso.py; +x left, -y anterior, +z superior)."""
import json, os, sys
import numpy as np, pandas as pd
from scipy.spatial import cKDTree, ConvexHull
from scipy.sparse.csgraph import connected_components
import scipy.sparse as sp
sys.path.insert(0, 'sims/biv_model')
from common import boundary_faces, face_key
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
def vtx(h, n):
    f = f'data/biv/{h}/surfaces/{n}.vtx'
    return np.loadtxt(f, skiprows=2, dtype=np.int64, ndmin=1) if os.path.exists(f) else np.array([], np.int64)
def surf(h, n): return np.loadtxt(f'data/biv/{h}/surfaces/{n}.surf', skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
def plane(X):
    c = X.mean(0); u, s, vt = np.linalg.svd(X - c); n = vt[2]
    return c, n, vt[:2], float(np.sqrt(np.mean(((X - c) @ n) ** 2)))
def ring_d(X):
    c, n, ax, rms = plane(X); Y = (X - c) @ ax.T; r = np.linalg.norm(Y, axis=1)
    ext = [float(np.ptp(Y[:, 0])), float(np.ptp(Y[:, 1]))]
    return {'mean_diameter_mm': round(2 * r.mean(), 1), 'max_min_extent_mm': [round(max(ext), 1), round(min(ext), 1)], 'plane_rms_mm': round(rms, 2)}, c, n
def eqd(P2):
    if len(P2) < 4: return None
    return round(float(2 * np.sqrt(ConvexHull(P2).volume / np.pi)), 1)
def read_vtk_poly(f):
    L = open(f).read().split('\n'); i = [k for k, l in enumerate(L) if l.startswith('POINTS')][0]; n = int(L[i].split()[1])
    tok, j = [], i + 1
    while len(tok) < 3 * n: tok += L[j].split(); j += 1
    P = np.array(tok[:3 * n], float).reshape(-1, 3)
    k = [m for m, l in enumerate(L) if l.startswith('POLYGONS')][0]; nt = int(L[k].split()[1]); tri = []; j = k + 1
    while len(tri) < nt:
        v = L[j].split()
        if v: tri.append([int(x) for x in v[1:4]])
        j += 1
    return P, np.array(tri)
skinP, skinT = read_vtk_poly('data/torso/torsoModels/T_13_torso_coarse_surface.vtk')
bc = np.array([(a, b, 1 - a - b) for a in np.linspace(0, 1, 13) for b in np.linspace(0, 1, 13) if a + b <= 1 + 1e-9])
skin = np.concatenate([bc @ skinP[t] for t in skinT]); t_skin = cKDTree(skin)
el = np.loadtxt('data/torso/torsoModels/T_13_electrodes.csv', delimiter=',', skiprows=1)
ELN = ['RA', 'LA', 'LL', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'RL']; ELP = dict(zip(ELN, el))
OUT = {}
for h in HEARTS:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    Ee = np.loadtxt(B + 'biv.elem', skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64); E, tag = Ee[:, :4], Ee[:, 4]
    z, phi, rho, v = (np.loadtxt(B + f'uvc/{n}.dat') for n in ('z', 'phi', 'rho', 'v')); ph = np.degrees(phi)
    w = np.clip(np.loadtxt(B + 'laplace/w.dat'), 0, 1)
    M = np.loadtxt(f'data/torso/atria/{h}_to_g001_rigid.txt'); Rm, tv = M[:3], M[3]
    TF = lambda X: X @ Rm.T + tv
    o = {'rigid_R_det': round(float(np.linalg.det(Rm)), 6), 'rigid_rotation_deg': round(float(np.degrees(np.arccos(np.clip((np.trace(Rm) - 1) / 2, -1, 1)))), 1)}
    x = P[E]; vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    vt = {int(t): round(float(vol[tag == t].sum() / 1e3), 1) for t in np.unique(tag)}
    lvm = vol[np.isin(tag, [1, 25, 29])].sum() / 1e3; rvm = vol[np.isin(tag, [2, 28])].sum() / 1e3
    o['myo_volume_ml_by_tag'] = vt; o['LV_myo_ml(1+25+29)'] = round(lvm, 1); o['LV_mass_g(x1.05)'] = round(lvm * 1.05, 1)
    o['RV_myo_ml(2+28)'] = round(rvm, 1); o['RV_mass_g(x1.05)'] = round(rvm * 1.05, 1); o['total_myo_ml'] = round(vol.sum() / 1e3, 1)
    # tags vs UVC v: how much septum is tagged LV
    # cavity volumes
    bf, own = boundary_faces(E); bkey = face_key(bf); order = np.argsort(bkey); bk_s = bkey[order]
    def cavity(sname):
        F = surf(h, sname); k = face_key(F); pos = np.searchsorted(bk_s, k); ok = bk_s[np.minimum(pos, len(bk_s) - 1)] == k
        F = F[ok]; ow = own[order[pos[ok]]]
        fourth = np.array([[n for n in E[e] if n not in f][0] for e, f in zip(ow, F)])
        c = P[F].mean(1); nrm = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
        flip = np.sum(nrm * (P[fourth] - c), 1) < 0     # want normal pointing into the myocardium (out of the cavity)
        F[flip] = F[flip][:, [0, 2, 1]]
        ed = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        key = np.minimum(ed[:, 0], ed[:, 1]) * 10 ** 7 + np.maximum(ed[:, 0], ed[:, 1])
        u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        be = ed[cnt[inv] == 1]; nonman = int((cnt > 2).sum())
        nodes_b = np.unique(be); idx = {n: i for i, n in enumerate(nodes_b)}
        A = sp.coo_matrix((np.ones(len(be)), ([idx[a] for a in be[:, 0]], [idx[b] for b in be[:, 1]])), shape=(len(nodes_b),) * 2)
        nl, lab = connected_components(A, directed=False)
        caps, loops = [], []
        for L in range(nl):
            nb = nodes_b[lab == L]; C = P[nb].mean(0)
            sel = np.isin(be[:, 0], nb)
            per = float(np.linalg.norm(P[be[sel, 0]] - P[be[sel, 1]], axis=1).sum())
            rims = {}
            for rn in ('mv_rim', 'av_rim', 'tv_rim', 'pv_rim', 'avplane_iface', 'ao_iface', 'part_iface'):
                rv_ = vtx(h, rn)
                if len(rv_): rims[rn] = int(np.isin(nb, rv_).sum())
            loops.append({'perimeter_mm': round(per, 1), 'nodes': int(len(nb)), 'rim_overlap_nodes': {k_: v_ for k_, v_ in rims.items() if v_}})
            for a, b in be[sel]: caps.append((P[b], P[a], C))
        tri = [P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]]
        Vs = np.einsum('ij,ij->i', tri[0], np.cross(tri[1], tri[2])).sum() / 6
        cp = np.array(caps); Vc = np.einsum('ij,ij->i', cp[:, 0], np.cross(cp[:, 1], cp[:, 2])).sum() / 6 if len(cp) else 0
        return {'volume_ml': round(float(-(Vs + Vc) / 1e3), 1), 'faces': int(len(F)), 'boundary_loops': loops, 'nonmanifold_edges': nonman}
    o['LV_cavity'] = cavity('lv_endo'); o['RV_cavity'] = cavity('rv_endo')
    o['authors_mech_t0_volume_ml'] = {s: float(open(f'data/cohort/{h}/{h}/mechanics/{s}_endo.vol.dat').readline().split()[1]) / 1000 if False else float(open(f'data/cohort/{h}/{h}/mechanics/{s}_endo.vol.dat').readline().split()[1]) for s in ('lv', 'rv')}
    # wall thickness (nearest surface)
    lv, rv, epi = vtx(h, 'lv_endo'), vtx(h, 'rv_endo'), vtx(h, 'epi')
    te, tl, tr = cKDTree(P[epi]), cKDTree(P[lv]), cKDTree(P[rv])
    dle, dlr = te.query(P[lv])[0], tr.query(P[lv])[0]
    dre, drl = te.query(P[rv])[0], tl.query(P[rv])[0]
    sepL = dlr < dle; fwR = dre < drl
    zl, pl = z[lv], ph[lv]
    def med(m, d):
        return [round(float(np.median(d[m])), 1), int(m.sum())] if m.any() else None
    lev = {'base': (0.70, 0.85), 'mid': (0.45, 0.60), 'apex': (0.15, 0.30)}
    wt = {}
    for ln, (a, b) in lev.items():
        mz = (zl >= a) & (zl <= b)
        wt[f'LV_anterior_{ln}'] = med(mz & ~sepL & (pl >= 60) & (pl <= 120), dle)
        wt[f'LV_lateral_{ln}'] = med(mz & ~sepL & (np.abs(pl) >= 150), dle)
        wt[f'LV_inferior_{ln}'] = med(mz & ~sepL & (pl >= -120) & (pl <= -60), dle)
        if ln != 'apex': wt[f'septum_{ln}'] = med(mz & sepL, dlr)
    wt['LV_apex(z<0.08)'] = med(zl < 0.08, dle)
    zr = z[rv]
    wt['RV_free_wall_mid'] = med(fwR & (zr >= 0.45) & (zr <= 0.6), dre)
    wt['RV_free_wall_base'] = med(fwR & (zr >= 0.7) & (zr <= 0.85), dre)
    # RVOT walls: RV endo nodes w<0.3, 5-15 mm below the PV rim
    pvr = vtx(h, 'pv_rim'); avr = vtx(h, 'av_rim')
    dpv = cKDTree(P[pvr]).query(P[rv])[0]
    rvot = (w[rv] < 0.3) & (dpv > 5) & (dpv < 15)
    other = np.unique(np.concatenate([lv, vtx(h, 'ao_iface'), vtx(h, 'avplane_iface')]))
    d_other = cKDTree(P[other]).query(P[rv])[0]
    sept = rvot & (d_other < dre); fwo = rvot & ~sept
    wt['RVOT_septal(to LV endo / aortic iface)'] = med(sept, d_other)
    wt['RVOT_free_wall(to epi)'] = med(fwo, dre)
    o['wall_thickness_mm_[median,n]'] = wt
    # valves
    av, cav, nav = ring_d(P[avr]); pv, cpv, npv = ring_d(P[pvr]); mv, cmv, nmv = ring_d(P[vtx(h, 'mv_rim')]); tvd, ctv, ntv = ring_d(P[vtx(h, 'tv_rim')])
    lvc, rvc = P[lv].mean(0), P[rv].mean(0)
    if (lvc - cav) @ nav > 0: nav = -nav          # normals point to the arteries
    if (rvc - cpv) @ npv > 0: npv = -npv
    if (lvc - cmv) @ nmv > 0: nmv = -nmv
    o['valve_annulus'] = {'aortic': av, 'pulmonary': pv, 'mitral': mv, 'tricuspid': tvd}
    # LV long axis and short axis
    apex = int(json.load(open(B + 'summary_02.json'))['apex_node'])
    ax = (P[apex] - cmv) / np.linalg.norm(P[apex] - cmv)
    endo_apex = lv[np.argmax((P[lv] - cmv) @ ax)]
    o['LV_long_axis_mm'] = {'epi_apex_to_MV_centroid': round(float(np.linalg.norm(P[apex] - cmv)), 1),
                            'endo_apex_to_MV_plane': round(float(abs((P[endo_apex] - cmv) @ nmv)), 1),
                            'endo_apex_to_MV_centroid': round(float(np.linalg.norm(P[endo_apex] - cmv)), 1)}
    e1 = rvc - cmv; e1 = e1 - (e1 @ ax) * ax; e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
    sa = {}
    for dmm in (15, 25, 35):
        s_ = (P[lv] - cmv) @ ax; m = np.abs(s_ - dmm) < 1.0
        Y = np.c_[(P[lv][m] - cmv) @ e1, (P[lv][m] - cmv) @ e2]
        sa[f'{dmm}mm_below_MV'] = {'equiv_diameter_mm': eqd(Y), 'septal_lateral_width_mm': round(float(np.ptp(Y[:, 0])), 1) if len(Y) else None}
    o['LV_short_axis'] = sa
    # RVOT diameter 10 mm below the PV plane
    s_ = (P[rv] - cpv) @ npv; rr = np.linalg.norm((P[rv] - cpv) - np.outer(s_, npv), axis=1)
    m = (np.abs(s_ + 10) < 1.0) & (rr < 25)
    a1, a2 = np.linalg.svd(np.eye(3) - np.outer(npv, npv))[0][:, :2].T
    Y = np.c_[(P[rv][m] - cpv) @ a1, (P[rv][m] - cpv) @ a2]
    o['RVOT_diameter_10mm_below_PV_mm'] = {'equiv': eqd(Y), 'n_nodes': int(m.sum())}
    tvr = vtx(h, 'tv_rim')
    o['infundibulum_proxy_mm'] = {'min_TV_rim_to_PV_rim': round(float(cKDTree(P[tvr]).query(P[pvr])[0].min()), 1),
                                  'TV_centroid_to_PV_centroid': round(float(np.linalg.norm(ctv - cpv)), 1),
                                  'min_MV_rim_to_AV_rim(aorto-mitral)': round(float(cKDTree(P[vtx(h, 'mv_rim')]).query(P[avr])[0].min()), 1)}
    Tav, Tpv = TF(cav), TF(cpv); nav_t, npv_t = nav @ Rm.T, npv @ Rm.T
    o['PV_vs_AV'] = {'PV_minus_AV_superior_torso_mm': round(float(Tpv[2] - Tav[2]), 1), 'PV_minus_AV_anterior_torso_mm': round(float(-(Tpv[1] - Tav[1])), 1),
                     'PV_minus_AV_left_torso_mm': round(float(Tpv[0] - Tav[0]), 1), 'centroid_distance_mm': round(float(np.linalg.norm(cpv - cav)), 1),
                     'angle_between_valve_plane_normals_deg': round(float(np.degrees(np.arccos(np.clip(nav @ npv, -1, 1)))), 1)}
    def ot_axis(ring_c, nrm, endo):
        s_ = (P[endo] - ring_c) @ nrm; rr = np.linalg.norm((P[endo] - ring_c) - np.outer(s_, nrm), axis=1)
        m = (s_ < -15) & (s_ > -25) & (rr < 20)
        a = ring_c - P[endo][m].mean(0); return a / np.linalg.norm(a)
    lvot, rvot_ax = ot_axis(cav, nav, lv), ot_axis(cpv, npv, rv)
    o['LVOT_RVOT_axis_angle_deg(15-25mm below valve -> valve centre)'] = round(float(np.degrees(np.arccos(np.clip(lvot @ rvot_ax, -1, 1)))), 1)
    # muscle above valve planes
    def above(ring_c, nrm, rad):
        s_ = (P - ring_c) @ nrm; rr = np.linalg.norm((P - ring_c) - np.outer(s_, nrm), axis=1)
        m = (rr < rad + 10)
        ec = P[E].mean(1); se = (ec - ring_c) @ nrm; re_ = np.linalg.norm((ec - ring_c) - np.outer(se, nrm), axis=1)
        me = (re_ < rad + 10) & (se > 1.0)
        return {'max_height_above_plane_mm': round(float(s_[m].max()), 1), 'nodes_gt_1mm': int((m & (s_ > 1)).sum()), 'nodes_gt_3mm': int((m & (s_ > 3)).sum()),
                'muscle_volume_gt_1mm_ml': round(float(vol[me].sum() / 1e3), 2), 'tags_of_that_muscle': {int(t): int((tag[me] == t).sum()) for t in np.unique(tag[me])}}
    o['muscle_above_AV_plane'] = above(cav, nav, av['mean_diameter_mm'] / 2)
    o['muscle_above_PV_plane'] = above(cpv, npv, pv['mean_diameter_mm'] / 2)
    # sites: cusps, summit, RVOT, vein course
    S = pd.read_csv(B + 'sites.csv')
    sites = {}
    for _, s in S[S.family.isin(['aortic_cusp', 'lv_summit', 'rvot', 'lv_vein_course'])].iterrows():
        n = int(s.node); X = P[n]
        sites[s.id] = {'wall_mm(site grid)': s.wall_thickness_mm, 'depth_target': s.depth_target, 'depth_achieved': s.depth_achieved,
                       'height_vs_AV_plane_mm(+ = aortic side)': round(float((X - cav) @ nav), 1), 'height_vs_PV_plane_mm': round(float((X - cpv) @ npv), 1),
                       'dist_AV_rim_mm': round(float(cKDTree(P[avr]).query(X)[0]), 1), 'dist_PV_rim_mm': round(float(cKDTree(P[pvr]).query(X)[0]), 1),
                       'tag': int(np.bincount(tag[np.any(E == n, axis=1)]).argmax()), 'v': int(v[n]), 'z': round(float(z[n]), 3), 'phi': round(float(ph[n]), 1),
                       'dist_left_sinus_mm': s.dist_left_sinus_mm}
    o['sites_outflow_summit_vein'] = sites
    # torso placement
    Ttot = TF(P); ax_t = ax @ Rm.T            # base -> apex in torso frame
    o['LV_long_axis_torso'] = {'unit_base_to_apex(x left,y post,z sup)': ax_t.round(3).tolist(),
                               'frontal_angle_deg(0=left horizontal,+90=inferior)': round(float(np.degrees(np.arctan2(-ax_t[2], ax_t[0]))), 1),
                               'anterior_tilt_out_of_frontal_deg': round(float(np.degrees(np.arcsin(-ax_t[1]))), 1),
                               'angle_from_sagittal_plane_deg': round(float(np.degrees(np.arcsin(abs(ax_t[0])))), 1),
                               'horizontal_plane_angle_deg(0=left,+90=anterior)': round(float(np.degrees(np.arctan2(-ax_t[1], ax_t[0]))), 1)}
    ep_t = Ttot[epi]; d_sk = t_skin.query(ep_t)[0]
    ant = ep_t[np.argmin(ep_t[:, 1])]
    o['heart_in_torso'] = {'min_epicardium_to_skin_mm': round(float(d_sk.min()), 1), 'most_anterior_epi_point_torso': ant.round(1).tolist(),
                           'most_anterior_epi_to_skin_mm': round(float(t_skin.query(ant)[0]), 1),
                           'heart_bbox_torso_mm': [Ttot.min(0).round(1).tolist(), Ttot.max(0).round(1).tolist()],
                           'AV_centroid_torso': Tav.round(1).tolist(), 'PV_centroid_torso': Tpv.round(1).tolist(),
                           'apex_torso': TF(P[apex]).round(1).tolist()}
    rvs = S[S.family == 'rvot']
    o['heart_in_torso']['rvot_sites'] = {r.id: {'z_minus_V1_mm': round(float(TF(P[int(r.node)])[2] - ELP['V1'][2]), 1), 'z_minus_V2_mm': round(float(TF(P[int(r.node)])[2] - ELP['V2'][2]), 1),
                                                'dist_V1_mm': round(float(np.linalg.norm(TF(P[int(r.node)]) - ELP['V1'])), 1), 'dist_V2_mm': round(float(np.linalg.norm(TF(P[int(r.node)]) - ELP['V2'])), 1),
                                                'to_skin_mm': round(float(t_skin.query(TF(P[int(r.node)]))[0]), 1)} for _, r in rvs[rvs.depth_target == 0.5].iterrows()}
    # phi orientation check in body frame: LV epi nodes at phi ~ +90 vs -90 (free wall), z 0.4-0.7
    lve = epi[v[epi] == 0]
    sel = lambda p0: lve[(np.abs(np.angle(np.exp(1j * np.radians(ph[lve] - p0)))) < np.radians(20)) & (z[lve] > 0.4) & (z[lve] < 0.7)]
    a90, m90 = TF(P[sel(90)]).mean(0), TF(P[sel(-90)]).mean(0)
    s0 = TF(P[sel(0)]).mean(0) if len(sel(0)) else None
    o['phi_orientation_check_torso'] = {'phi+90_minus_phi-90 (x left, y post, z sup)': (a90 - m90).round(1).tolist(),
                                        'reading': 'phi +90 is anterior/superior if y<0 and/or z>0'}
    # summit
    s11 = json.load(open(B + 'summary_11.json'))
    o['summit_v5_summary_11'] = s11.get('summit_v5'); o['vein_course_summary_11'] = s11.get('vein_course_sites')
    o['site_grid_flags'] = {k_: s11.get(k_) for k_ in ('thin_wall', 'depth_miss', 'off_line', 'crossings_detected', 'line_rule_changed', 'other_free_wall_T_range_mm')}
    OUT[h] = o
    print(h, 'done', flush=True)
# chest at V1/V2 level
zV = (ELP['V1'][2] + ELP['V2'][2]) / 2
sl = skin[np.abs(skin[:, 2] - zV) < 5]
OUT['T13_chest_at_V1V2_level'] = {'z_mm': round(float(zV), 1), 'width_x_mm': round(float(np.ptp(sl[:, 0])), 1), 'depth_y_mm': round(float(np.ptp(sl[:, 1])), 1),
                                  'V1_V2_to_skin_mm': [round(float(t_skin.query(ELP['V1'])[0]), 1), round(float(t_skin.query(ELP['V2'])[0]), 1)],
                                  'V4_minus_V2_z_mm': round(float(ELP['V4'][2] - ELP['V2'][2]), 1), 'V1_V2_x_mm': [round(float(ELP['V1'][0]), 1), round(float(ELP['V2'][0]), 1)],
                                  'shoulder_midline_x_mm': round(float((ELP['RA'][0] + ELP['LA'][0]) / 2), 1)}
json.dump(OUT, open('analysis/audit_2026-10-13/a04_anatomy.json', 'w'), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str)[:3000])
