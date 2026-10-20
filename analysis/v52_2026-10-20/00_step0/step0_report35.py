"""v5.2 step 0, report 35 and the outflow items of step 0, read only (LOCK.md 15.2 step 0; section 12 item 35; 8.2, 8.5, 8.6).

On the full cohort mesh (data/cohort/<H>/<H>/myocardium_AV_FEC_BB_lvrv, all tags), geometry only, before any beat.

Operational definitions (mine, stated so they can be checked; none changes a lock value):
  Aortic valve plane: the mid-plane of the AV valve-disc elements (tag 9; the mesh's valves are solid discs about 6 mm
    thick), from a principal-component fit; normal n_av points to the aortic wall (tag 5) side. Root axis = n_av through the
    disc centroid. Heights are axial (along n_av) from that plane.
  Aortic valve-plane ring: the nodes the disc shares with the wall around it (tag 1 or tag 5); at an angle theta, the ring
    point is the ring node at that angle (within 5 deg) nearest the mid-plane.
  Angular frame (8.5 item 6): theta in the valve plane about the root axis; theta = 0 at the ring point nearest the mitral
    valve disc (tag 7); the sense of increasing theta is the one that puts the ring point nearest the pulmonary valve disc
    (tag 10) inside 90-150 deg (both senses are reported).
  de Kerchove's six positions (theta, derived from Toh's frame: commissures at the interleaflet-triangle centres, sinus
    midpoints half-way between): N/L 0, LCS 60.2, L/R 120.4, RCS 180.7, R/N 241.0, NCS 300.5 deg; a window of +-10 deg.
  Pulmonary side: the same with the PV disc (tag 10), n_pv to the pulmonary artery (tag 6); sinus centres: posterior at the
    PV ring point nearest the aortic wall (tag 5), the others at +-120 deg (8.6), sectors of +-60 deg.
  Ventricular muscle: tags 1, 2, 25, 28, 29 (the v5.1 simulation mesh).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/00_step0/step0_report35.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))
from common import boundary_faces, face_key, tet_faces                       # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
VENT = [1, 2, 25, 28, 29]
DK = {'N/L': 0.0, 'LCS': 60.2, 'L/R': 120.4, 'RCS': 180.7, 'R/N': 241.0, 'NCS': 300.5}       # derived from Toh 2020
DK_EXT = {'NCS': -0.1, 'N/L': 0.3, 'LCS': 0.5, 'L/R': 4.6, 'RCS': 2.4, 'R/N': 2.5}        # de Kerchove Table 1, mm
WIN = 10.0
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '00_step0')


def load(h):
    base = os.path.join(REPO, 'data', 'cohort', h, h, 'myocardium_AV_FEC_BB_lvrv')
    E = pd.read_csv(base + '.elem', sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).to_numpy()
    P = pd.read_csv(base + '.pts', sep=' ', skiprows=1, header=None).to_numpy() / 1e3
    return P, E[:, :4].astype(np.int64), E[:, 4].astype(np.int64)


def interfaces(E, tag):
    """Shared faces between elements of different tags: (faces (k,3), tag_a, tag_b) with tag_a < tag_b."""
    f, own = tet_faces(E)
    k = face_key(f)
    o = np.argsort(k, kind='stable'); ks = k[o]
    j = np.where(ks[1:] == ks[:-1])[0]
    a, b = own[o][j], own[o][j + 1]
    ta, tb = tag[a], tag[b]
    m = ta != tb
    fa = f[o][j][m]; t1, t2 = np.minimum(ta[m], tb[m]), np.maximum(ta[m], tb[m])
    return fa, t1, t2


def tri_area(P, F):
    return 0.5 * np.linalg.norm(np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]]), axis=1)


class Valve:
    def __init__(self, P, E, tag, vtag, wall_tag, side_tag):
        self.nodes = np.unique(E[tag == vtag])
        X = P[self.nodes]
        self.c = X.mean(0)
        _, s, vt = np.linalg.svd(X - self.c, full_matrices=False)
        n = vt[2]
        wc = P[np.unique(E[tag == side_tag])].mean(0)
        self.n = n if (wc - self.c) @ n > 0 else -n
        self.thickness = float(np.percentile((X - self.c) @ self.n, 98) - np.percentile((X - self.c) @ self.n, 2))
        e1 = np.cross(self.n, [1.0, 0, 0]); e1 /= np.linalg.norm(e1)
        self.e1, self.e2 = e1, np.cross(self.n, e1)
        wall_nodes = np.unique(E[np.isin(tag, wall_tag)])
        self.ring = np.intersect1d(self.nodes, wall_nodes)
        self.P = P

    def h(self, X):
        return (np.atleast_2d(X) - self.c) @ self.n

    def r(self, X):
        d = np.atleast_2d(X) - self.c
        return np.linalg.norm(d - np.outer(d @ self.n, self.n), axis=1)

    def ang_raw(self, X):
        d = np.atleast_2d(X) - self.c
        return np.degrees(np.arctan2(d @ self.e2, d @ self.e1))

    def set_frame(self, theta0_node, sign):
        self.a0, self.sign = float(self.ang_raw(self.P[theta0_node])[0]), sign

    def theta(self, X):
        return (self.sign * (self.ang_raw(X) - self.a0)) % 360.0

    def ring_point(self, th, win=5.0):
        t = self.theta(self.P[self.ring])
        d = np.abs((t - th + 180) % 360 - 180)
        k = self.ring[d <= win]
        if not len(k):
            k = self.ring[np.argsort(d)[:5]]
        return int(k[np.argmin(np.abs(self.h(self.P[k])))])


def adiff(a, b):
    return np.abs((a - b + 180) % 360 - 180)


def heart(h):
    t0 = time.time()
    P, E, tag = load(h)
    fa, t1, t2 = interfaces(E, tag)
    pair = lambda a, b: fa[(t1 == min(a, b)) & (t2 == max(a, b))]
    av = Valve(P, E, tag, 9, [1, 5, 25, 29], 5)
    pv = Valve(P, E, tag, 10, [2, 6, 28], 6)
    mv_nodes = np.unique(E[tag == 7]); pvn = pv.nodes
    # aortic angular frame
    th0 = int(av.ring[np.argmin(cKDTree(P[mv_nodes]).query(P[av.ring])[0])])
    ppv = int(av.ring[np.argmin(cKDTree(P[pvn]).query(P[av.ring])[0])])
    chk = {}
    for sgn in (1, -1):
        av.set_frame(th0, sgn)
        chk[sgn] = float(av.theta(P[ppv])[0])
    ok = [s for s in (1, -1) if 90 <= chk[s] <= 150]
    ppc = int(av.ring[np.argmin(np.linalg.norm(P[av.ring] - pv.c, axis=1))])          # reading 2: nearest the PV disc centroid
    chk2 = {}
    for sgn in (1, -1):
        av.set_frame(th0, sgn)
        chk2[sgn] = float(av.theta(P[ppc])[0])
    frame = {'theta0_ring_node (nearest the mitral disc)': th0, 'ring_node_nearest_pulmonary_valve': ppv,
             'angle_to_pv_nearest_point_deg': {'+': round(chk[1], 1), '-': round(chk[-1], 1)},
             'reading_2_ring_node_nearest_the_pv_disc_centroid': ppc,
             'reading_2_angle_deg': {'+': round(chk2[1], 1), '-': round(chk2[-1], 1)},
             'reading_2_check_90_150': 'pass' if any(90 <= chk2[s_] <= 150 for s_ in (1, -1)) else 'fail in both senses',
             'sense_used': ('+' if ok[0] == 1 else '-') if ok else None,
             'check_90_150': 'pass' if ok else 'FAIL in both senses (8.5 item 6 stop rule, step 2c)'}
    av.set_frame(th0, ok[0] if ok else 1)
    out = {'heart': h, 'aortic_valve': {'disc_thickness_mm': round(av.thickness, 2), 'ring_nodes': int(len(av.ring)),
                                        'ring_height_range_mm': [round(float(av.h(P[av.ring]).min()), 2), round(float(av.h(P[av.ring]).max()), 2)],
                                        'ring_radius_median_mm': round(float(np.median(av.r(P[av.ring]))), 1), 'frame': frame},
           'pulmonary_valve': {'disc_thickness_mm': round(pv.thickness, 2), 'ring_nodes': int(len(pv.ring)),
                               'ring_radius_median_mm': round(float(np.median(pv.r(P[pv.ring]))), 1)}}
    # interface areas
    out['interface_area_mm2'] = {f'{a}-{b}': round(float(tri_area(P, pair(a, b)).sum()), 1)
                                 for a, b in ((1, 5), (2, 5), (1, 9), (5, 9), (2, 6), (2, 10), (6, 10), (3, 5), (4, 5), (5, 27), (5, 6), (1, 2))}

    # (a) and (h): tag-1/tag-5 boundary at the six positions, luminal and epicardial ends
    f15 = pair(1, 5)
    n15 = np.unique(f15)
    th15, h15, r15 = av.theta(P[n15]), av.h(P[n15]), av.r(P[n15])
    pos = {}
    for k, thk in DK.items():
        m = adiff(th15, thk) <= WIN
        rp = av.ring_point(thk)
        h_ring = float(av.h(P[rp])[0])
        if m.any():
            il, ie = np.argmin(r15[m]), np.argmax(r15[m])
            lum, epi = float(h15[m][il]), float(h15[m][ie])
            pos[k] = {'theta_deg': thk, 'boundary_nodes': int(m.sum()),
                      'luminal_height_above_valve_plane_mm': round(lum, 2), 'epicardial_height_above_valve_plane_mm': round(epi, 2),
                      'max_height_above_valve_plane_mm': round(float(h15[m].max()), 2), 'min_height_above_valve_plane_mm': round(float(h15[m].min()), 2),
                      'ring_point_height_mm': round(h_ring, 2),
                      'luminal_height_above_ring_mm': round(lum - h_ring, 2), 'epicardial_height_above_ring_mm': round(epi - h_ring, 2),
                      'de_Kerchove_external_junction_mm': DK_EXT[k],
                      'below_valve_plane': bool(min(lum, epi) < 0)}
        else:
            near = {}
            for tt in (2, 3, 4, 27, 6, 9):
                ff = pair(5, tt)
                if len(ff):
                    nn = np.unique(ff)
                    mm = (adiff(av.theta(P[nn]), thk) <= WIN) & (np.abs(av.h(P[nn])) < 15)
                    near[int(tt)] = int(mm.sum())
            pos[k] = {'theta_deg': thk, 'boundary_nodes': 0, 'note': 'no tag-1/tag-5 boundary within +-10 deg',
                      'tag5_meets_here (nodes within 15 mm of the plane)': near, 'ring_point_height_mm': round(h_ring, 2),
                      'de_Kerchove_external_junction_mm': DK_EXT[k], 'below_valve_plane': None}
    out['35a_35h_tag1_tag5_boundary'] = pos
    out['35h_precondition_8.5_item9'] = {'any_position_below_valve_plane': any(v.get('below_valve_plane') for v in pos.values()),
                                         'positions_below': [k for k, v in pos.items() if v.get('below_valve_plane')],
                                         'positions_without_boundary': [k for k, v in pos.items() if v['boundary_nodes'] == 0]}
    # muscle above the aortic valve plane, per sinus (L 0-120.4, R 120.4-241, N 241-360)
    vm = np.isin(tag, VENT)
    cen0 = P[E].mean(1)
    def profile(valve, mtags, rmax, sectors):
        """Per 5-deg bin: the highest centroid of the given muscle tags within rmax of the valve axis (h > -5 mm)."""
        ix = np.where(np.isin(tag, mtags) & (valve.r(cen0) < rmax) & (valve.h(cen0) > -5) & (valve.h(cen0) < 30))[0]
        th = valve.theta(cen0[ix]); hh = valve.h(cen0[ix])
        bins = np.arange(0, 360, 5.0)
        prof = np.array([hh[(th >= b) & (th < b + 5)].max() if ((th >= b) & (th < b + 5)).any() else np.nan for b in bins])
        out = {}
        for k, (lo, hi) in sectors.items():
            m = np.array([(lo <= b < hi) if lo < hi else (b >= lo or b < hi) for b in bins])
            v = prof[m]
            mid = (lo + (hi - lo) / 2) % 360 if lo < hi else ((lo + (hi + 360 - lo) / 2) % 360)
            out[k] = {'per_5deg_bin_max_height_above_valve_plane_mm_min_median_max': [round(float(np.nanmin(v)), 2), round(float(np.nanmedian(v)), 2), round(float(np.nanmax(v)), 2)] if np.isfinite(v).any() else None,
                      'at_sector_midline_mm': round(float(prof[int(mid // 5)]), 2) if np.isfinite(prof[int(mid // 5)]) else None,
                      'empty_bins': int(np.isnan(v).sum())}
        return out, prof
    lv_prof, lvp = profile(av, [1, 25, 29], float(np.median(av.r(P[av.ring]))) + 6.0, {'L (0-120.4)': (0, 120.4), 'R (120.4-241)': (120.4, 241.0), 'N (241-360)': (241.0, 360.0)})
    out['existing_lv_muscle_above_aortic_valve_plane_by_sinus'] = {'rule': 'LV muscle tags 1, 25, 29 within the ring radius + 6 mm of the root axis; '
                                                                          'per 5-deg bin the highest element centroid above the valve mid-plane; the disc '
                                                                          f'half-thickness is {av.thickness / 2:.2f} mm, so heights up to that are muscle beside the disc',
                                                                  'sinuses': lv_prof,
                                                                  'theta_where_existing_exceeds_2.4mm_in_the_RCC_lune_135.5_206': int(np.nansum((lvp[27:42] > 2.4))),
                                                                  'profile_5deg_bins': [None if not np.isfinite(x) else round(float(x), 2) for x in lvp]}
    cen = P[E].mean(1)
    near_root = (av.r(cen) < 25) & (np.abs(av.h(cen)) < 25)
    vol = lambda ix: float(np.abs(np.einsum('ij,ij->i', P[E[ix, 1]] - P[E[ix, 0]], np.cross(P[E[ix, 2]] - P[E[ix, 0]], P[E[ix, 3]] - P[E[ix, 0]]))).sum() / 6)
    above = np.where(vm & near_root & (av.h(cen) > 0))[0]
    tha = av.theta(cen[above])
    sin = {'L': (0, 120.4), 'R': (120.4, 241.0), 'N': (241.0, 360.0)}
    ma = {}
    for k, (lo, hi) in sin.items():
        m = (tha >= lo) & (tha < hi)
        ix = above[m]
        ma[k] = {'elements': int(len(ix)), 'volume_mm3': round(vol(ix), 1) if len(ix) else 0.0,
                 'max_height_above_valve_plane_mm': round(float(av.h(cen[ix]).max()), 2) if len(ix) else 0.0,
                 'tags': {int(t): int(c) for t, c in zip(*np.unique(tag[ix], return_counts=True))}}
    out['muscle_above_aortic_valve_plane'] = ma
    # (e): RV-infundibulum contact on the aortic root at L/R and RCS
    f25 = pair(2, 5); n25 = np.unique(f25)
    th25, h25 = av.theta(P[n25]), av.h(P[n25])
    e = {}
    for k in ('L/R', 'RCS'):
        m = adiff(th25, DK[k]) <= WIN
        rp = av.ring_point(DK[k])
        e[k] = {'contact_nodes': int(m.sum()), 'max_height_above_valve_plane_mm': round(float(h25[m].max()), 2) if m.any() else None,
                'max_height_above_ring_mm': round(float(h25[m].max() - av.h(P[rp])[0]), 2) if m.any() else None,
                'de_Kerchove_mm': DK_EXT[k]}
    out['35e_rv_contact_on_aortic_root'] = e
    # (d): wall thickness 20 mm above the valves
    def wall20(valve, wtag):
        ix = np.unique(E[tag == wtag])
        hh = valve.h(P[ix]); m = np.abs(hh - 20.0) <= 1.0
        if m.sum() < 20:
            return {'nodes_in_slab': int(m.sum()), 'note': 'the vessel ends below 20 mm', 'vessel_max_height_mm': round(float(hh.max()), 1)}
        X = P[ix[m]]
        c = X.mean(0); d = X - c; d -= np.outer(d @ valve.n, valve.n)
        rr = np.linalg.norm(d, axis=1); aa = np.degrees(np.arctan2(d @ valve.e2, d @ valve.e1))
        th = [float(rr[(aa >= a) & (aa < a + 15)].max() - rr[(aa >= a) & (aa < a + 15)].min()) for a in range(-180, 180, 15) if ((aa >= a) & (aa < a + 15)).sum() >= 3]
        return {'nodes_in_slab': int(m.sum()), 'thickness_mm_median_min_max_over_15deg_sectors': [round(float(np.median(th)), 2), round(float(np.min(th)), 2), round(float(np.max(th)), 2)],
                'vessel_max_height_mm': round(float(hh.max()), 1)}
    out['35d_wall_thickness_20mm_above_valve'] = {'aorta (Hasdemir 1.6 +- 0.4 mm)': wall20(av, 5), 'pulmonary artery (Hasdemir 1.01 +- 0.4 mm)': wall20(pv, 6),
                                                  'label': 'a comparison of construction constants (aorta and pulmonary artery are 2 mm distance-map shells)'}
    # pulmonary side: sinus frame, muscle above the PV plane per sinus
    ao_nodes = np.unique(E[tag == 5])
    post = int(pv.ring[np.argmin(cKDTree(P[ao_nodes]).query(P[pv.ring])[0])])
    pv.set_frame(post, 1)
    above_p = np.where(vm & (pv.r(cen) < 30) & (np.abs(pv.h(cen)) < 25) & (pv.h(cen) > 0))[0]
    thp = pv.theta(cen[above_p])
    mp = {}
    for k, cth in (('posterior', 0.0), ('sinus_at_+120', 120.0), ('sinus_at_-120', 240.0)):
        m = adiff(thp, cth) < 60
        ix = above_p[m]
        ring_k = pv.ring[adiff(pv.theta(P[pv.ring]), cth) < 60]
        nadir = float(pv.h(P[ring_k]).min()) if len(ring_k) else 0.0
        mp[k] = {'elements': int(len(ix)), 'volume_mm3': round(vol(ix), 1) if len(ix) else 0.0,
                 'max_height_above_valve_plane_mm': round(float(pv.h(cen[ix]).max()), 2) if len(ix) else 0.0,
                 'lowest_ring_point_height_mm (nadir proxy)': round(nadir, 2),
                 'max_height_above_nadir_proxy_mm': round(float(pv.h(cen[ix]).max()) - nadir, 2) if len(ix) else None}
    rv_prof, rvp = profile(pv, [2, 28], float(np.median(pv.r(P[pv.ring]))) + 6.0, {'posterior (300-60)': (300.0, 60.0), '+120 (60-180)': (60.0, 180.0), '-120 (180-300)': (180.0, 300.0)})
    ring_lo = {k: round(float(pv.h(P[pv.ring[adiff(pv.theta(P[pv.ring]), c_) < 60]]).min()), 2) for k, c_ in (('posterior (300-60)', 0.0), ('+120 (60-180)', 120.0), ('-120 (180-300)', 240.0))}
    out['muscle_above_pulmonary_valve_plane'] = {'posterior_sinus_centre_ring_node (nearest the aortic wall)': post, 'sinuses (wide selection, r < 30 mm)': mp,
                                                 'existing_rv_muscle_by_sinus (ring radius + 6 mm)': rv_prof, 'lowest_ring_point_per_sinus_mm (nadir proxy)': ring_lo,
                                                 'disc_half_thickness_mm': round(pv.thickness / 2, 2),
                                                 'profile_5deg_bins': [None if not np.isfinite(x) else round(float(x), 2) for x in rvp]}

    # (f) infundibulum cut candidates on the posterior RVOT wall
    bf, own = boundary_faces(E)
    rv_cav = bf[np.isin(tag[own], [2, 28, 29, 1])]                    # cavity faces are filtered below by component
    # RV cavity surface: the boundary component holding the TV and PV disc faces with RV muscle
    fe = np.vstack([np.sort(bf[:, [0, 1]], 1), np.sort(bf[:, [1, 2]], 1), np.sort(bf[:, [0, 2]], 1)])
    fid = np.tile(np.arange(len(bf)), 3); key = fe[:, 0] * (1 << 21) + fe[:, 1]
    o = np.argsort(key); ks = key[o]; fs = fid[o]; sm = ks[1:] == ks[:-1]
    G = coo_matrix((np.ones(sm.sum()), (fs[:-1][sm], fs[1:][sm])), shape=(len(bf), len(bf)))
    nc, lab = connected_components(G, directed=False)
    comp_tags = {k: set(np.unique(tag[own[lab == k]]).tolist()) for k in range(nc)}
    rvk = [k for k in range(nc) if {2, 8, 10} <= comp_tags[k]]
    rvf = bf[(lab == rvk[0]) & np.isin(tag[own], [2, 28, 29])] if rvk else np.zeros((0, 3), np.int64)
    f = {}
    if len(rvf):
        rn = np.unique(rvf)
        loc = np.full(len(P), -1); loc[rn] = np.arange(len(rn))
        ed = np.vstack([rvf[:, [0, 1]], rvf[:, [1, 2]], rvf[:, [0, 2]]])
        ed = np.unique(np.sort(ed, 1), axis=0)
        A = coo_matrix((np.ones(len(ed)), (loc[ed[:, 0]], loc[ed[:, 1]])), shape=(len(rn), len(rn))).tocsr(); A = A + A.T
        A2 = (A @ A + A).tocoo(); mk = A2.row < A2.col
        e2 = np.c_[A2.row[mk], A2.col[mk]]
        w = np.linalg.norm(P[rn[e2[:, 0]]] - P[rn[e2[:, 1]]], axis=1)
        G2 = coo_matrix((np.r_[w, w], (np.r_[e2[:, 0], e2[:, 1]], np.r_[e2[:, 1], e2[:, 0]])), shape=(len(rn), len(rn))).tocsr()
        # 100 %: the PV ring's posterior aspect (ring nodes on the RV cavity within 45 deg of the aortic side); its lowest point
        prc = np.intersect1d(pv.ring, rn)
        tpr = pv.theta(P[prc])
        asp = prc[adiff(tpr, 0.0) <= 45]
        p100 = int(asp[np.argmin(pv.h(P[asp]))])
        tvn = np.unique(E[tag == 8])
        tvr = np.intersect1d(tvn, rn)
        variants = {'TV ring node nearest the PV ring (superior tricuspid annulus)': float(pv.h(P[tvr[np.argmin(cKDTree(P[pvn]).query(P[tvr])[0])]])[0]),
                    'TV ring centroid': float(pv.h(P[tvr].mean(0))[0]),
                    'highest TV ring node along the RVOT axis': float(pv.h(P[tvr]).max())}
        res = {}
        for vname, hTA in variants.items():
            q = P[p100] - (pv.h(P[p100])[0] - hTA) * pv.n
            # the 0 % point: the RV cavity node nearest the projection, on the posterior side (theta within 60 deg)
            post_side = rn[(adiff(pv.theta(P[rn]), 0.0) <= 60)]
            p0 = int(post_side[np.argmin(np.linalg.norm(P[post_side] - q, axis=1))])
            d, pr = dijkstra(G2, indices=loc[p0], return_predecessors=True)
            span = float(d[loc[p100]])
            path = [loc[p100]]
            while path[-1] != loc[p0] and pr[path[-1]] >= 0:
                path.append(pr[path[-1]])
            path = rn[np.array(path[::-1])]
            sp = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[path], axis=0), axis=1))]
            pt = lambda s_: int(path[np.argmin(np.abs(sp - s_))])
            cands = {'37.3 % of the span (07:30 rule)': 0.373 * span, '12.7 mm above 0 % (D6, primary)': 12.7, '15.3 mm below the ring': span - 15.3}
            res[vname] = {'tricuspid_annulus_level_height_mm': round(hTA, 2), 'node_0pct': p0, 'node_100pct': p100,
                          'posterior_span_mm': round(span, 2), 'vs_Jakiel_26.9_pm_6.5_mm': 'inside' if 20.4 <= span <= 33.4 else 'outside',
                          'candidates': {k: {'distance_from_0pct_mm': round(v, 2), 'node': pt(v), 'height_above_pv_plane_mm': round(float(pv.h(P[pt(v)])[0]), 2)} for k, v in cands.items()},
                          'gap_12.7mm_minus_37.3pct_mm': round(12.7 - 0.373 * span, 2)}
        f = {'definition': '0 % = the RV cavity node on the posterior wall nearest the projection, along the RVOT axis (PV disc normal), '
                           'of the lowest PV-ring point of its posterior aspect (within 45 deg of the aortic side) down to the tricuspid-'
                           'annulus level; 100 % = that ring point; span = surface distance (2-ring) between them. Three readings of '
                           '"the tricuspid-annulus level" are given; the first is used for the contact areas below',
             'variants': res}
        # contact areas above the D6 split height (fused below 12.7 mm above 0 %, split above), primary variant
        prim = res[list(variants)[0]]
        hsplit = prim['candidates']['12.7 mm above 0 % (D6, primary)']['height_above_pv_plane_mm']
        f12 = pair(1, 2)
        hc = pv.h(P[f12].mean(1))
        nearr = (pv.r(P[f12].mean(1)) < 40)
        f['contact_area_mm2'] = {'tag2_tag5 (infundibulum on the aortic root), all heights': round(float(tri_area(P, pair(2, 5)).sum()), 1),
                                 'tag1_tag2 above the D6 split height (within 40 mm of the RVOT axis)': round(float(tri_area(P, f12[nearr & (hc >= hsplit)]).sum()), 1),
                                 'tag1_tag2 above the 37.3 % height': round(float(tri_area(P, f12[nearr & (hc >= prim['candidates']['37.3 % of the span (07:30 rule)']['height_above_pv_plane_mm'])]).sum()), 1),
                                 'split_height_above_pv_plane_mm': hsplit}
    out['35f_infundibulum_cut'] = f
    # (g) and the supraventricular crest: shortest RV-cavity path from the TV ring to the PV ring, and the wall along it
    g = {}
    if len(rvf):
        src = loc[np.intersect1d(np.unique(E[tag == 8]), rn)]
        dd, pr2, sr = dijkstra(G2, indices=src, min_only=True, return_predecessors=True)
        tgt = loc[np.intersect1d(pv.ring, rn)]
        j = tgt[np.argmin(dd[tgt])]
        pth = [j]
        while pr2[pth[-1]] >= 0:
            pth.append(pr2[pth[-1]])
        pth = rn[np.array(pth[::-1])]
        outer = np.unique(bf[lab != rvk[0]])
        to = cKDTree(P[outer])
        thick = to.query(P[pth])[0]
        g = {'tv_to_pv_ring_surface_distance_mm': round(float(dd[j]), 2), 'path_nodes': int(len(pth)),
             'wall_thickness_along_path_mm (nearest non-RV-cavity boundary)': {'at_tv_end': round(float(thick[0]), 2), 'median': round(float(np.median(thick)), 2),
                                                                               'max': round(float(thick.max()), 2), 'at_pv_end': round(float(thick[-1]), 2)},
             'Jakiel': 'origin 12.3 +- 2.9 mm, termination 9.2 +- 1.9 mm',
             'tag': 'no supraventricular-crest or septoparietal-band tag in tags_lvrv.json'}
    out['35g_supraventricular_crest'] = g
    out['35b_35c'] = 'after steps 2c-2d (no lune is built at step 0)'
    out['wall_s'] = round(time.time() - t0, 1)
    return out


def main():
    for h in (sys.argv[1:] or HEARTS):
        r = heart(h)
        json.dump(r, open(os.path.join(HERE, f'report35_{h}.json'), 'w'), indent=1, default=str)
        print(h, json.dumps(r['35h_precondition_8.5_item9']), r['aortic_valve']['frame']['check_90_150'], f"{r['wall_s']} s", flush=True)


if __name__ == '__main__':
    main()
