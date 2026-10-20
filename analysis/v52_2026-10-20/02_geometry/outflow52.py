"""v5.2 steps 2c and 2d: the aortic crescents (LOCK.md 8.5, deviations D5, D13, D15) and the pulmonary sleeves (8.6, D13),
built by re-tagging existing wall elements of the full cohort mesh (tag 5 -> 1, tag 6 -> 2); nothing is extruded.

Shared construction (mine where the lock is silent, stated so it can be checked):
  s, the distance up the root wall from the mid-plane ring: Dijkstra on the tet-edge graph of the wall and the
    ventricular muscle near the root, from the mid-plane ring nodes; an element takes the mean of its nodes.
  depth of an element below the luminal face: distance from its centroid to the nearest luminal-face node; luminal
    faces = boundary faces of the wall elements whose outward normal points toward the vessel axis (dot < -0.3).
  existing muscle at an angle: the ventricular elements within ring radius + 6 mm of the axis; the built extent at an
    angle is max(existing, structure), so wall elements are re-tagged only above the existing muscle.
Crescents (8.5): LCC lune theta 52.4-106.6 deg, peak 2.9 mm; RCC lune 135.5-206.0 deg, peak 6.4 mm; half-sine h(theta);
  RCC axial cap H(theta) = 2.4 sin(pi (theta - 135.5) / 70.5) mm above the ring (item 2b); thickness t_hinge(theta) at the
  ring tapering linearly in s to 1.0 mm at h(theta) (item 7; t_hinge = the LV muscle's radial extent at the ring
  height at that angle); the whole wall where thinner (item 8b).
Sleeves (8.6): all round the pulmonary ring, built height 4.0 mm (axial) above the mid-plane ring, existing height axial too, thickness 2.0 / 1.7 /
  1.0 mm at 25 / 50 / 75 % of the 4.0 mm, piecewise linear, the full wall at 0 %, 1.0 mm from 75 % to the end; the
  luminal-face nodes of the sleeve carry the fibrous-layer flag (non-excitable, 0.2 S/m in the lead field, 8.6).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/outflow52.py [HEART ...]
"""
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

LUNES = {'LCC': (52.4, 106.6, 2.9), 'RCC': (135.5, 206.0, 6.4)}
SLEEVE_H = 4.0
SLEEVE_T = [(0.25, 2.0), (0.50, 1.7), (0.75, 1.0)]


def wall_s(P, E, tag, valve, wall_tag, muscle_tags, rmax):
    """Distance from the mid-plane ring through the wall (tet edges) for nodes of the wall and the nearby muscle."""
    cen = P[E].mean(1)
    keep = (np.isin(tag, [wall_tag] + muscle_tags) & (valve.r(cen) < rmax) & (valve.h(cen) > -6) & (valve.h(cen) < 40))
    Ek = E[keep]
    nodes = np.unique(Ek); loc = np.full(len(P), -1); loc[nodes] = np.arange(len(nodes))
    pairs = np.unique(np.sort(np.concatenate([Ek[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    w = np.linalg.norm(P[pairs[:, 0]] - P[pairs[:, 1]], axis=1)
    Gr = coo_matrix((np.r_[w, w], (np.r_[loc[pairs[:, 0]], loc[pairs[:, 1]]], np.r_[loc[pairs[:, 1]], loc[pairs[:, 0]]])), shape=(len(nodes), len(nodes))).tocsr()
    src = loc[np.intersect1d(valve.ring, nodes)]
    d = dijkstra(Gr, indices=src, min_only=True)
    s = np.full(len(P), np.inf); s[nodes] = d
    return s


def luminal_nodes(P, E, tag, valve, wall_tag):
    bf, own = boundary_faces(E)
    m = tag[own] == wall_tag
    F, o = bf[m], own[m]
    n = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True)
    fc = P[F].mean(1); n *= np.sign(np.einsum('ij,ij->i', n, fc - P[E[o]].mean(1)))[:, None]
    d = fc - valve.c; rad = d - np.outer(d @ valve.n, valve.n); rad /= np.linalg.norm(rad, axis=1, keepdims=True)
    dot = np.einsum('ij,ij->i', n, rad)
    return np.unique(F[dot < -0.3]), np.unique(F[dot > 0.3])


def existing_profile(P, E, tag, valve, muscle_tags, rmax, s):
    """Per 5-deg bin: the highest axial height and the largest s of ventricular muscle near the ring."""
    cen = P[E].mean(1)
    ix = np.where(np.isin(tag, muscle_tags) & (valve.r(cen) < rmax) & (valve.h(cen) > -6) & (valve.h(cen) < 30))[0]
    th = valve.theta(cen[ix]); hh = valve.h(cen[ix]); se = s[E[ix]].mean(1)
    bins = np.arange(0, 360, 5.0)
    hmax = np.array([hh[(th >= b) & (th < b + 5)].max() if ((th >= b) & (th < b + 5)).any() else np.nan for b in bins])
    smax = np.array([np.nanmax(np.where(np.isfinite(se[(th >= b) & (th < b + 5)]), se[(th >= b) & (th < b + 5)], np.nan)) if ((th >= b) & (th < b + 5)).any() else np.nan for b in bins])
    return bins, hmax, smax


def crescents(P, E, tag, av):
    rr = float(np.median(av.r(P[av.ring])))
    s = wall_s(P, E, tag, av, 5, G.LV_GROUP, rr + 12)
    lum, outer = luminal_nodes(P, E, tag, av, 5)
    tl = cKDTree(P[lum])
    cen = P[E].mean(1)
    e5 = np.where(tag == 5)[0]
    th = av.theta(cen[e5]); ha = av.h(cen[e5]); se = s[E[e5]].mean(1); depth = tl.query(cen[e5])[0]
    # hinge thickness: radial extent of LV muscle at the ring height, per 5-deg bin
    lvn = np.unique(E[np.isin(tag, G.LV_GROUP)])
    lvn = lvn[(np.abs(av.h(P[lvn])) <= 1.0) & (av.r(P[lvn]) < rr + 15)]
    tln, rln = av.theta(P[lvn]), av.r(P[lvn])
    def t_hinge(t):
        k = np.abs((tln - t + 180) % 360 - 180) <= 5
        rp = av.r(P[av.ring_point(t)])[0]
        return float(np.clip(rln[k].max() - rp, 1.0, None)) if k.any() else 1.0
    out, retag = {}, []
    bins5 = (th // 5).astype(int) % 72
    ex_start = np.array([np.nanmin(np.where(bins5 == b, se, np.nan)) if (bins5 == b).any() else np.nan for b in range(72)])
    for nm, (t0, t1, hmax) in LUNES.items():
        m = (th >= t0) & (th <= t1)
        lune = hmax * np.sin(np.pi * (th - t0) / (t1 - t0))
        ok = m & (se <= lune)
        if nm == 'RCC':
            cap = 2.4 * np.sin(np.pi * (th - t0) / (t1 - t0))
            hring = np.array([av.h(P[av.ring_point(t)])[0] for t in th]) if m.any() else np.zeros(len(th))
            ok &= (ha - hring) <= cap
        th_h = {round(t, 1): t_hinge(t) for t in np.arange(t0, t1 + 0.1, 5.0)}
        def treq(t, s_, L):
            hh_ = th_h[min(th_h, key=lambda x: abs(x - t))]
            return hh_ - (hh_ - 1.0) * np.clip(s_ / max(L, 1e-9), 0, 1)
        req = np.array([treq(t, s_, L) for t, s_, L in zip(th, se, lune)]) if m.any() else np.zeros(len(th))
        ok &= depth <= req
        # max(existing, lune), both from the ring (item 9): the existing muscle's extent up the wall at an angle is where
        # the tag-5 wall begins there (the lowest s of tag-5 elements in the 5-deg bin); tag-5 elements lie above it, so
        # re-tagging those with s <= lune adds muscle only where the lune reaches beyond the existing muscle
        ids = e5[ok]
        retag.append(ids)
        rec = {'elements_retagged': int(len(ids)), 'volume_mm3': round(float(G.tet_vol(P, E[ids]).sum()), 2),
               'tag5_elements_in_angular_range_within_lune_extent (before thickness and cap)': int((m & (se <= lune)).sum()),
               'lowest_tag5_s_in_range_mm': round(float(np.nanmin(np.where(m, se, np.nan))), 2) if m.any() else None,
               'lowest_tag5_axial_height_in_range_mm': round(float(np.nanmin(np.where(m, ha, np.nan))), 2) if m.any() else None,
               'hinge_thickness_mm_by_5deg': {str(k): round(v, 2) for k, v in th_h.items()}}
        if len(ids):
            rec['35b_axial_rise_mm (max height of re-tagged elements above the ring)'] = round(float(ha[ok].max()), 2)
            rec['35b_radial_reach_mm (max r minus ring radius)'] = round(float((av.r(cen[ids]) - rr).max()), 2)
            rec['achieved_thickness_mm_max_depth'] = round(float(depth[ok].max()), 2)
            rec['elements_per_10deg'] = {int(b): int(((th[ok] >= b) & (th[ok] < b + 10)).sum()) for b in np.arange(int(t0 // 10) * 10, t1, 10)}
        else:
            rec['35b_axial_rise_mm (max height of re-tagged elements above the ring)'] = 0.0
            rec['35b_radial_reach_mm (max r minus ring radius)'] = 0.0
        out[nm] = rec
    ids = np.concatenate(retag) if retag else np.zeros(0, np.int64)
    # hard gate: nothing outside the lunes (in particular the aorto-mitral continuity and the non-coronary sinus)
    tt = av.theta(cen[ids])
    inl = np.zeros(len(ids), bool)
    for t0, t1, _ in LUNES.values():
        inl |= (tt >= t0) & (tt <= t1)
    bins, hmx, smx = existing_profile(P, E, tag, av, G.LV_GROUP, rr + 6, s)
    out['hard_gate_no_muscle_outside_the_lunes'] = bool(inl.all())
    out['existing_lv_muscle_by_5deg (max axial height mm; s where the tag-5 wall starts, mm)'] = {int(b): [None if not np.isfinite(x) else round(float(x), 2), None if not np.isfinite(y) else round(float(y), 2)] for b, x, y in zip(bins, hmx, ex_start)}
    out['luminal_faces_nodes'] = int(len(lum)); out['ring_radius_mm'] = round(rr, 2)
    out['35c_LCC_achieved_thickness_mm'] = out['LCC'].get('achieved_thickness_mm_max_depth', 0.0)
    return ids, out, s


def sleeves(P, E, tag, pv):
    rr = float(np.median(pv.r(P[pv.ring])))
    s = wall_s(P, E, tag, pv, 6, G.RV_GROUP, rr + 12)
    lum, outer = luminal_nodes(P, E, tag, pv, 6)
    tl = cKDTree(P[lum])
    cen = P[E].mean(1)
    e6 = np.where(tag == 6)[0]
    th = pv.theta(cen[e6]); depth = tl.query(cen[e6])[0]
    se = pv.h(cen[e6])                    # the sleeve is built by axial height above the mid-plane ring (8.6: "within 4.0 mm above")
    # thickness profile in s over the 4.0 mm sleeve: full wall at 0 %, 2.0 / 1.7 / 1.0 mm at 25 / 50 / 75 %, 1.0 to the end
    def treq(s_):
        f = np.clip(s_ / SLEEVE_H, 0, 1)
        return np.where(f <= 0.25, np.inf, np.interp(f, [0.25, 0.50, 0.75, 1.0], [2.0, 1.7, 1.0, 1.0]))
    bins, hmx, smx = existing_profile(P, E, tag, pv, G.RV_GROUP, rr + 6, s)
    smx = hmx                              # existing height = the highest RV-muscle centroid above the mid-plane, per 5 deg
    ex_s = smx[(th // 5).astype(int) % 72]
    # max(existing, 4.0 mm): nothing is added at an angle where existing RV muscle already reaches 4.0 mm (8.6)
    ok = (se >= 0) & (se <= SLEEVE_H) & (depth <= treq(se)) & ~(np.isfinite(ex_s) & (ex_s >= SLEEVE_H))
    ids = e6[ok]
    out = {'elements_retagged': int(len(ids)), 'volume_mm3': round(float(G.tet_vol(P, E[ids]).sum()), 2),
           'ring_radius_mm': round(rr, 2), 'luminal_faces_nodes': int(len(lum)),
           'existing_rv_muscle_by_5deg (max axial height mm)': {int(b): None if not np.isfinite(x) else round(float(x), 2) for b, x in zip(bins, hmx)}}
    sin = {'posterior': 0.0, 'sinus_+120': 120.0, 'sinus_-120': 240.0}
    per = {}
    for k, c in sin.items():
        mk = np.abs((th[ok] - c + 180) % 360 - 180) < 60
        b = int((c // 5) * 5 % 360)
        ex = smx[int(b // 5)]
        per[k] = {'elements': int(mk.sum()), 'existing_height_at_centre_mm': None if not np.isfinite(ex) else round(float(ex), 2),
                  'achieved_height_at_centre_mm (max(existing, built))': round(float(max(ex if np.isfinite(ex) else 0.0, se[ok][mk].max() if mk.any() else 0.0)), 2),
                  'thickness_at_25_50_75pct_mm (max depth of re-tagged elements in s bands of 0.5 mm)':
                      [round(float(depth[ok][mk & (np.abs(se[ok] - f * SLEEVE_H) < 0.5)].max()), 2) if (mk & (np.abs(se[ok] - f * SLEEVE_H) < 0.5)).any() else None for f in (0.25, 0.5, 0.75)]}
    out['per_sinus'] = per
    # fibrous layer: luminal-face nodes of the re-tagged elements
    fib = np.intersect1d(np.unique(E[ids]), lum) if len(ids) else np.zeros(0, np.int64)
    out['fibrous_layer_nodes'] = int(len(fib))
    # closed ring: angular coverage of the sleeve in 5-deg bins
    cov = np.unique((th[ok] // 5).astype(int)) if len(ids) else np.zeros(0)
    out['angular_bins_with_sleeve_muscle_of_72'] = int(len(cov))
    out['bins_where_existing_muscle_already_reaches_4mm'] = int(np.nansum(smx >= SLEEVE_H))
    out['ring_closed (every 5-deg bin has muscle at 4.0 mm, existing or built)'] = bool(all(((smx[i] >= SLEEVE_H) if np.isfinite(smx[i]) else False) or (i in set(cov.tolist())) for i in range(72)))
    return ids, fib, out, s


def run(hs):
    for h in hs:
        t0 = time.time()
        P, E, tag = G.load_full(h)
        av, arec = G.aortic_frame(P, E, tag)
        pv, prec = G.pulmonary_frame(P, E, tag)
        if arec['check_90_150'] != 'pass':
            print(h, 'aortic frame check FAILED: stop (8.5 item 6)'); continue
        cid, cres, s_av = crescents(P, E, tag, av)
        sid, fib, sres, s_pv = sleeves(P, E, tag, pv)
        out = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'aortic_frame_D15': arec, 'pulmonary_frame': prec,
               'crescents': cres, 'sleeves': sres, 'wall_s': round(time.time() - t0, 1)}
        os.makedirs(os.path.join(G.RUN, h), exist_ok=True)
        np.savez(os.path.join(G.RUN, h, 'outflow52.npz'), crescent_elements=cid, sleeve_elements=sid, fibrous_nodes=fib)
        G.dump(out, os.path.join(HERE, f'outflow52_{h}.json'))
        print(h, 'crescents LCC', cres['LCC']['elements_retagged'], 'RCC', cres['RCC']['elements_retagged'], 'hard gate', cres['hard_gate_no_muscle_outside_the_lunes'],
              '| sleeves', sres['elements_retagged'], 'per sinus', {k: v['elements'] for k, v in sres['per_sinus'].items()}, 'closed', sres['ring_closed (every 5-deg bin has muscle at 4.0 mm, existing or built)'],
              f"{out['wall_s']} s", flush=True)


if __name__ == '__main__':
    run(sys.argv[1:] or G.HEARTS)
