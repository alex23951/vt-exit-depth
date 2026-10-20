"""v5.2 step 2f: heart pose in the T13 torso (LOCK.md 9.1, the pose card "CT pose") and the T13 electrode report (9.4).

Pose (9.1): rotation fixed at the identity; translation t' = R c + t - c, so that the LA+RA surface centroid c lands where
v5.1's rigid atrial fit (data/torso/atria/<H>_to_g001_rigid.txt, x' = R x + t, 08a_atrial_fit.py) put it. c (mine,
reading "LA+RA surface centroid"): the area-weighted centroid of the boundary surface of the cohort mesh's LA and RA
elements (tags 3, 4). Two other readings are reported beside it with the translation each would give: the mean of all
LA+RA nodes (the point cloud the v5.1 fit used) and the mean of the LA+RA surface nodes. Nothing is chosen by the result.
Acceptance (9.1): no node outside the T13 skin (data/torso/torsoModels/T_13_torso_coarse_surface.vtk, the surface v5.1
meshed from) and at least 5 mm from it, for (a) the v5.2 simulation mesh (ventricles and sleeves) and (b) every node of
the cohort mesh (atria, valves, vessel stubs and the closed cavity surfaces that bound the blood); else stop and report.
Reports: the 4x4 transform; every electrode's distance to the nearest myocardium (v5.2 simulation mesh), in both poses;
the orientation of the long and short axes in torso coordinates, CT pose against v5.1 pose (report only); and the 9.4
forward check of the T13 electrodes against Kligfield's landmark rules, as far as a skin-only torso allows (report only).
Torso frame (08_torso.py): +x left, -y anterior, +z superior; mm.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/pose52.py [HEART ...]
"""
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import boundary_faces, read_vtx                                                 # noqa: E402

T13 = os.path.join(G.REPO, 'data', 'torso', 'torsoModels', 'T_13')
ELEC = ['RA', 'LA', 'LL', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'RL']
CLEAR_MM = 5.0


def read_vtk_polydata(f):
    """As sims/biv_model/08_torso.py."""
    L = open(f).read().split('\n')
    i = [k for k, l in enumerate(L) if l.startswith('POINTS')][0]
    n = int(L[i].split()[1])
    tok, j = [], i + 1
    while len(tok) < 3 * n:
        tok += L[j].split(); j += 1
    P = np.array(tok[:3 * n], float).reshape(-1, 3)
    k = [m for m, l in enumerate(L) if l.startswith('POLYGONS')][0]
    nt = int(L[k].split()[1]); tri = []; j = k + 1
    while len(tri) < nt:
        v = L[j].split()
        if v:
            tri.append([int(x) for x in v[1:4]])
        j += 1
    return P, np.array(tri)


def point_tri_dist(p, a, b, c):
    """Distance from points p to triangles (a, b, c), row-wise (Ericson, Real-Time Collision Detection 5.1.5)."""
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = np.einsum('ij,ij->i', ab, ap), np.einsum('ij,ij->i', ac, ap)
    bp = p - b; d3, d4 = np.einsum('ij,ij->i', ab, bp), np.einsum('ij,ij->i', ac, bp)
    cp = p - c; d5, d6 = np.einsum('ij,ij->i', ab, cp), np.einsum('ij,ij->i', ac, cp)
    va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
    q = np.empty_like(p)
    den = va + vb + vc; den = np.where(np.abs(den) < 1e-30, 1e-30, den)
    v, w = vb / den, vc / den
    q[:] = a + ab * v[:, None] + ac * w[:, None]
    m = (d1 <= 0) & (d2 <= 0); q[m] = a[m]
    m = (d3 >= 0) & (d4 <= d3); q[m] = b[m]
    m = (d6 >= 0) & (d5 <= d6); q[m] = c[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.where(d1 - d3 == 0, 1, d1 - d3); q[m] = (a + ab * t[:, None])[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.where(d2 - d6 == 0, 1, d2 - d6); q[m] = (a + ac * t[:, None])[m]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
    t = (d4 - d3) / np.where((d4 - d3) + (d5 - d6) == 0, 1, (d4 - d3) + (d5 - d6)); q[m] = (b + (c - b) * t[:, None])[m]
    return np.linalg.norm(p - q, axis=1)


def skin_distance(X, S, tri, k=24, chunk=50000):
    """Exact distance to the skin surface, over the k triangles with the nearest centroids (coarse skin: checked below)."""
    tc = S[tri].mean(1); tree = cKDTree(tc)
    out = np.empty(len(X))
    for c0 in range(0, len(X), chunk):
        x = X[c0:c0 + chunk]
        _, nb = tree.query(x, k=k)
        a, b, c = S[tri[nb, 0]], S[tri[nb, 1]], S[tri[nb, 2]]
        d = point_tri_dist(np.repeat(x, k, 0), a.reshape(-1, 3), b.reshape(-1, 3), c.reshape(-1, 3)).reshape(-1, k)
        out[c0:c0 + chunk] = d.min(1)
    return out


def winding(X, S, tri):
    """Generalised winding number (van Oosterom-Strackee solid angles / 4 pi): about 1 inside a closed surface, 0 outside."""
    a, b, c = S[tri[:, 0]][None] - X[:, None], S[tri[:, 1]][None] - X[:, None], S[tri[:, 2]][None] - X[:, None]
    la, lb, lc = (np.linalg.norm(v, axis=2) for v in (a, b, c))
    num = np.einsum('ijk,ijk->ij', a, np.cross(b, c))
    den = la * lb * lc + np.einsum('ijk,ijk->ij', a, b) * lc + np.einsum('ijk,ijk->ij', b, c) * la + np.einsum('ijk,ijk->ij', c, a) * lb
    return 2 * np.arctan2(num, den).sum(1) / (4 * np.pi)


def la_ra_centroids(P, E, tag):
    sel = np.isin(tag, [3, 4])
    bf, _ = boundary_faces(E[sel])
    A = G.tri_area(P, bf); fc = P[bf].mean(1)
    return {'surface_area_weighted (primary)': (A[:, None] * fc).sum(0) / A.sum(),
            'all_LA_RA_nodes (v5.1 fit point cloud)': P[np.unique(E[sel])].mean(0),
            'LA_RA_surface_nodes': P[np.unique(bf)].mean(0)}, int(len(bf))


def axes(Pm, h):
    S = os.path.join(G.REPO, 'data', 'biv', h, 'v52', 'surfaces')
    apex = Pm[read_vtx(os.path.join(S, 'apex.vtx'))[0]]
    base = Pm[np.concatenate([read_vtx(os.path.join(S, f + '.vtx')) for f in ('mv_rim', 'tv_rim')])].mean(0)
    L = (base - apex) / np.linalg.norm(base - apex)
    rv = Pm[read_vtx(os.path.join(S, 'rv_endo.vtx'))].mean(0)
    e1 = (rv - apex) - ((rv - apex) @ L) * L; e1 /= np.linalg.norm(e1)
    return L, e1


def describe(L, e1):
    """Torso frame +x left, -y anterior, +z superior. Long axis = apex -> base; reported as apex direction (base -> apex)."""
    ap = -L
    frontal = np.degrees(np.arctan2(-ap[2], ap[0]))         # frontal-plane angle of the apex direction below horizontal, towards the left
    elev = np.degrees(np.arcsin(-ap[1]))                    # anterior tilt of the apex direction (+ = apex anterior)
    horiz = np.degrees(np.arctan2(-ap[1], ap[0]))           # horizontal-plane angle from leftward towards anterior
    return {'apex_direction_unit': ap.round(4).tolist(), 'frontal_plane_deg (apex below the left horizontal)': round(float(frontal), 1),
            'anterior_tilt_deg': round(float(elev), 1), 'horizontal_plane_deg (left towards anterior)': round(float(horiz), 1),
            'short_axis_to_RV_unit': e1.round(4).tolist()}


def ang(u, v):
    return round(float(np.degrees(np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1)))), 2)


def forward_check(el, S):
    e = dict(zip(ELEC, el))
    z = lambda k: float(e[k][2])
    # midline: halfway between the skin's left and right edges within 10 mm of the V1/V2 height (T13 has no sternum)
    zz = 0.5 * (z('V1') + z('V2'))
    band = S[np.abs(S[:, 2] - zz) <= 10.0]
    mid_x = float(0.5 * (band[:, 0].min() + band[:, 0].max()))
    v24 = 0.5 * (e['V2'] + e['V4'])
    zmax, zmin = float(S[:, 2].max()), float(S[:, 2].min())
    return {'midline_x_mm (halfway between the skin edges at the V1-V2 height)': round(mid_x, 1),
            'V1-V2 separation mm': round(float(np.linalg.norm(e['V1'] - e['V2'])), 1),
            'V1, V2 lateral offset from the midline mm (parasternal: right, left)': [round(float(e['V1'][0] - mid_x), 1), round(float(e['V2'][0] - mid_x), 1)],
            'V1 - V2 height mm (level: 0)': round(z('V1') - z('V2'), 1),
            'V2 - V4 height mm (one intercostal space; T13 has no ribs)': round(z('V2') - z('V4'), 1),
            'V3 distance from the V2-V4 midpoint mm (0 = midpoint)': round(float(np.linalg.norm(e['V3'] - v24)), 1),
            'V5 - V4, V6 - V4 height mm (same horizontal plane: 0)': [round(z('V5') - z('V4'), 1), round(z('V6') - z('V4'), 1)],
            'RA, LA height below the torso top mm (infraclavicular; clavicles not in T13)': [round(zmax - z('RA'), 1), round(zmax - z('LA'), 1)],
            'RA, LA lateral position x mm': [round(float(e['RA'][0]), 1), round(float(e['LA'][0]), 1)],
            'LL height above the torso bottom mm (costal margin and iliac crest not in T13)': round(z('LL') - zmin, 1),
            'torso_z_range_mm': [round(zmin, 1), round(zmax, 1)],
            'note': 'report only; the primary electrodes are not moved (9.4)'}


def run(h):
    t0 = time.time()
    P, E, tag = G.load_full(h)
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    with open(os.path.join(V, 'biv52.pts')) as fh:
        n = int(fh.readline()); Pm = np.loadtxt(fh, max_rows=n) / 1e3
    M = np.loadtxt(os.path.join(G.REPO, 'data', 'torso', 'atria', f'{h}_to_g001_rigid.txt'))
    R, t = M[:3], M[3]
    cs, nf = la_ra_centroids(P, E, tag)
    c = cs['surface_area_weighted (primary)']
    tp = R @ c + t - c
    T4 = np.eye(4); T4[:3, 3] = tp
    alt = {k: {'c_mm': v.round(3).tolist(), 't_prime_mm': (R @ v + t - v).round(3).tolist(),
               'difference_from_primary_mm': round(float(np.linalg.norm((R @ v + t - v) - tp)), 3)} for k, v in cs.items()}
    S, tri = read_vtk_polydata(T13 + '_torso_coarse_surface.vtk')
    el = np.loadtxt(T13 + '_electrodes.csv', delimiter=',', skiprows=1)
    Xs = Pm + tp                                   # v5.2 simulation mesh (ventricles + sleeves), CT pose
    Xa = P + tp                                    # every cohort node (atria, valves, vessels, cavity surfaces)
    ds, da = skin_distance(Xs, S, tri), skin_distance(Xa, S, tri)
    # exactness of the k-nearest-centroid search: brute force on the 2,000 closest nodes
    o = np.argsort(da)[:2000]
    brute = np.array([point_tri_dist(np.repeat(x[None], len(tri), 0), S[tri[:, 0]], S[tri[:, 1]], S[tri[:, 2]]).min() for x in Xa[o]])
    wn = winding(np.vstack([Xs.mean(0), Xa.mean(0), Xa[o[:200]]]), S, tri)
    inside = bool((wn > 0.5).all())
    Pm51 = Pm @ R.T + t
    d51 = skin_distance(Pm51, S, tri)
    tree52, tree51 = cKDTree(Xs), cKDTree(Pm51)
    elec = {k: {'v52_CT_pose_mm': round(float(tree52.query(x)[0]), 1), 'v51_pose_mm': round(float(tree51.query(x)[0]), 1)} for k, x in zip(ELEC, el)}
    L, e1 = axes(Pm, h)
    L51, e151 = L @ R.T, e1 @ R.T
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA,
           'pose_4x4 (x_torso_mm = x_heart_mm + t_prime; rotation identity)': T4.round(6).tolist(),
           't_prime_mm': tp.round(3).tolist(), 'v51_R_rotation_deg': round(float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))), 2),
           'v51_t_mm': t.round(3).tolist(), 'LA_RA_surface_faces': nf, 'centroid_readings': alt,
           'centroid_lands_where_v51_put_it_mm (check 0)': round(float(np.linalg.norm((c + tp) - (R @ c + t))), 9),
           'shift_of_the_ventricles_vs_v51_pose_mm (median node)': round(float(np.median(np.linalg.norm(Xs - Pm51, axis=1))), 1),
           'clearance': {'skin_surface': os.path.relpath(T13 + '_torso_coarse_surface.vtk', G.REPO), 'skin_triangles': int(len(tri)),
                         'min_mm_simulation_mesh (ventricles + sleeves)': round(float(ds.min()), 2),
                         'min_mm_all_cohort_nodes (atria, valves, vessels, cavity surfaces)': round(float(da.min()), 2),
                         'nearest_search_exact_on_2000_closest (max |k-nearest - brute force| mm)': float(np.abs(brute - da[o]).max()),
                         'winding_number_heart_centroids_and_200_closest (min, max)': [round(float(wn.min()), 4), round(float(wn.max()), 4)],
                         'all_inside': inside, 'required_mm': CLEAR_MM,
                         'pass': bool(inside and ds.min() >= CLEAR_MM and da.min() >= CLEAR_MM),
                         'v51_pose_min_mm_simulation_mesh (report)': round(float(d51.min()), 2),
                         'closest_simulation_node_torso_mm': Xs[np.argmin(ds)].round(1).tolist()},
           'electrode_to_nearest_myocardium_mm': elec,
           'orientation (report only, never used to choose the pose)': {
               'CT_pose': describe(L, e1), 'v51_pose': describe(L51, e151),
               'long_axis_angle_between_poses_deg': ang(L, L51), 'short_axis_angle_between_poses_deg': ang(e1, e151)},
           'forward_check_T13_electrodes (9.4, report only)': forward_check(el, S),
           'wall_s': None}
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'pose52_{h}.json'))
    print(h, 't_prime', rec['t_prime_mm'], 'clearance', {k: v for k, v in rec['clearance'].items() if k.startswith(('min', 'all', 'pass', 'v51'))},
          'alt diffs', [v['difference_from_primary_mm'] for v in alt.values()], rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
