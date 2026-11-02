"""P16 (1)(c), read only: heart-to-skin clearance in A37's four KIT shapes (and T13), at the CT pose and at A33's poses.

Geometry only: node coordinates against each shape's skin surface (data/torso/torsoModels/T_<nn>_torso_coarse_surface.vtk).
No mesh is built and nothing is solved. Nothing is chosen.
Placement (P15's reading, R-M8): each heart keeps its CT-pose coordinates in the shared torso frame, x + t' (pose52.py,
identity rotation), in every shape; no registration or scaling. Node sets: (a) the v5.2 simulation mesh (ventricles and
sleeves, biv52) and (b) every node of the cohort mesh (atria, valves, vessel stubs and the closed cavity surfaces that
bound the blood), as 9.1's acceptance and pose52.py use them. Clearance is signed: negative = outside the skin.
Poses (A33, 9.4 (ii)): -10 / +10 deg about each torso axis (x left, y posterior, z superior; T13's frame) and -10 / +10 mm
along each. Pivot: the ventricular centroid = mean of the biv52 node coordinates (ventricles and sleeves) at the CT pose
(no other pivot is coded: no A33 code exists). Combined pose: worst clearance anywhere within +-10 deg about and +-10 mm
along every axis (rotation R = Rz Ry Rx about the pivot, then translation), by a 3^3 rotation x 3^3 translation grid (-10, 0, +10 on each axis) on
the candidate nodes, then bounded L-BFGS-B from the 3 worst grid poses, and the result re-checked on every boundary node.
Candidate nodes: the convex-hull vertices of the boundary nodes plus the 3,000 boundary nodes nearest the skin at the CT
pose. Inside/outside by generalised winding number (pose52.winding).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p16_clearance.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull, cKDTree
from scipy.spatial.transform import Rotation

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import boundary_faces                                                           # noqa: E402
from pose52 import read_vtk_polydata, skin_distance, winding                                # noqa: E402

TM = os.path.join(G.REPO, 'data', 'torso', 'torsoModels')
SHAPES = ['T_24', 'T_20', 'T_17', 'T_01', 'T_13']
LIMIT = 5.0


def signed(X, S, tri, d=None, check=None):
    """Signed clearance; winding checked on `check` (indices) only, others taken as inside."""
    d = skin_distance(X, S, tri) if d is None else d
    out = d.copy()
    idx = np.arange(len(X)) if check is None else check
    for c0 in range(0, len(idx), 200):
        j = idx[c0:c0 + 200]
        w = winding(X[j], S, tri)
        out[j[w < 0.5]] *= -1
    return out


def pose(X, piv, ang, tr):
    R = Rotation.from_euler('xyz', ang, degrees=True).as_matrix()
    return (X - piv) @ R.T + piv + tr


def run(h):
    t0 = time.time()
    P, E, tag = G.load_full(h)
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    with open(os.path.join(V, 'biv52.pts')) as fh:
        n = int(fh.readline()); Pm = np.loadtxt(fh, max_rows=n) / 1e3
    Em = np.loadtxt(os.path.join(V, 'biv52.elem'), skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    tp =np.array(json.load(open(os.path.join(HERE, f'pose52_{h}.json')))['t_prime_mm'])
    bf_a = np.unique(boundary_faces(E)[0]); bf_s = np.unique(boundary_faces(Em)[0])
    Xa, Xs = P[bf_a] + tp, Pm[bf_s] + tp
    piv = Pm.mean(0) + tp
    res = {'heart': h, 'pivot_ventricular_centroid_mm': piv.round(2).tolist(), 'boundary_nodes': {'cohort': int(len(Xa)), 'v52_sim': int(len(Xs))},
           'shapes': {}}
    X = np.vstack([Xs, Xa]); src = np.r_[np.zeros(len(Xs), int), np.ones(len(Xa), int)]
    hull = np.unique(ConvexHull(X).simplices)
    for sh in SHAPES:
        S, tri = read_vtk_polydata(os.path.join(TM, f'{sh}_torso_coarse_surface.vtk'))
        d0 = skin_distance(X, S, tri)
        near = np.argsort(d0)[:3000]
        chk = np.unique(np.r_[hull, near])
        s0 = signed(X, S, tri, d0, check=np.unique(np.r_[chk, np.where(d0 < 15)[0]]))
        out = {'skin_triangles': int(len(tri)),
               'ct_pose': {'min_mm_v52_sim': round(float(s0[src == 0].min()), 2), 'min_mm_cohort': round(float(s0[src == 1].min()), 2),
                           'nodes_outside_skin': int((s0 < 0).sum()), 'nodes_under_5mm': int((s0 < LIMIT).sum())}}
        C = X[chk]
        def clr(p, full=False):
            """full: signed minimum over every boundary node; else unsigned minimum over the candidates (search only)."""
            Y = pose(X if full else C, piv, p[:3], p[3:])
            dd = skin_distance(Y, S, tri)
            if not full:
                return float(dd.min())
            o = np.argsort(dd)[:3000]
            return float(signed(Y, S, tri, dd, check=np.unique(np.r_[hull, o, np.where(dd < 15)[0]])).min())
        print(h, sh, 'ct pose done', f'{time.time() - t0:.0f}s', flush=True)
        fixed = {}
        for ax, nm in enumerate('xyz'):
            for sg in (-1, 1):
                a = np.zeros(3); a[ax] = 10 * sg
                fixed[f'rot_{nm}_{sg * 10:+d}deg'] = round(clr(np.r_[a, 0, 0, 0], full=True), 2)
                tvec = np.zeros(3); tvec[ax] = 10 * sg
                fixed[f'trans_{nm}_{sg * 10:+d}mm'] = round(clr(np.r_[0, 0, 0, tvec], full=True), 2)
        out['a33_fixed_poses_min_mm'] = fixed
        out['a33_fixed_poses_under_5mm'] = [k for k, v in fixed.items() if v < LIMIT]
        print(h, sh, 'fixed poses done', f'{time.time() - t0:.0f}s', flush=True)
        grid = []
        for ax_ in (-10, 0, 10):
            for ay in (-10, 0, 10):
                for az in (-10, 0, 10):
                    R = Rotation.from_euler('xyz', [ax_, ay, az], degrees=True).as_matrix()
                    Y0 = (C - piv) @ R.T + piv
                    for tx in (-10, 0, 10):
                        for ty in (-10, 0, 10):
                            for tz in (-10, 0, 10):
                                grid.append(([ax_, ay, az, tx, ty, tz], float(skin_distance(Y0 + [tx, ty, tz], S, tri).min())))
        grid.sort(key=lambda g: g[1])
        best = None
        for p0, _ in grid[:3]:
            r = minimize(lambda p: clr(p), np.array(p0, float), method='L-BFGS-B', bounds=[(-10, 10)] * 6, options={'maxiter': 60})
            if best is None or r.fun < best[1]:
                best = (r.x, r.fun)
        full = clr(best[0], full=True)
        out['combined_worst'] = {'pose_deg_xyz_mm_xyz': np.round(best[0], 2).tolist(), 'min_mm_candidates': round(float(best[1]), 2),
                                 'min_mm_all_boundary_nodes': round(full, 2), 'grid_worst_unsigned_mm': round(grid[0][1], 2)}
        res['shapes'][sh] = out
        print(h, sh, out['ct_pose'], 'fixed<5:', out['a33_fixed_poses_under_5mm'], 'combined', out['combined_worst']['min_mm_all_boundary_nodes'],
              f'{time.time() - t0:.0f}s', flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    G.dump(res, os.path.join(HERE, f'preview_p16_clearance_{h}.json'))


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
