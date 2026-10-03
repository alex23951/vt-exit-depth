#!/usr/bin/env python
"""
Step 8a: rigid placement of a cohort heart in the torso frame by matching its own
atria (four-chamber mesh tags 3 = LA, 4 = RA) to one statistical-shape-model atrial
geometry that sits inside the Bender 2026 torsos (data/torso/atria/g001.vtk).

Trimmed ICP (90 %), 60 iterations, 8000 random points from each cloud (seed 0), started
from a centroid match. Coordinates in mm (cohort um / 1000). Writes
data/torso/atria/<HEART>_to_g001_rigid.txt (rows 1-3 R, row 4 t; x_torso = x @ R.T + t)
and prints rotation, translation and residuals.
"""

import json
import os

import numpy as np
from scipy.spatial import cKDTree

from common import HEART, REPO, SRC_MESH, read_elem, read_pts

ATRIA = os.path.join(REPO, 'data', 'torso', 'atria', 'g001.vtk')


def vtk_points(f):
    L = open(f).read().split('\n')
    i = [k for k, l in enumerate(L) if l.startswith('POINTS')][0]
    n = int(L[i].split()[1])
    tok, j = [], i + 1
    while len(tok) < 3 * n:
        tok += L[j].split(); j += 1
    return np.array(tok[:3 * n], float).reshape(-1, 3)


def main():
    A = vtk_points(ATRIA)
    P = read_pts(SRC_MESH) / 1e3
    E, tag = read_elem(SRC_MESH)
    B = P[np.unique(E[np.isin(tag, [3, 4])])]
    rng = np.random.default_rng(0)
    B = B[rng.choice(len(B), min(8000, len(B)), replace=False)]
    As = A[rng.choice(len(A), 8000, replace=False)]
    tree = cKDTree(As)
    R, t = np.eye(3), As.mean(0) - B.mean(0)
    for _ in range(60):
        X = B @ R.T + t
        d, i = tree.query(X)
        keep = d < np.percentile(d, 90)
        Xk, Yk = X[keep], As[i[keep]]
        U, S, Vt = np.linalg.svd((Xk - Xk.mean(0)).T @ (Yk - Yk.mean(0)))
        D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
        dR = Vt.T @ D @ U.T
        R = dR @ R
        t = dR @ t + Yk.mean(0) - dR @ Xk.mean(0)
    X = B @ R.T + t
    d1, _ = tree.query(X)
    d2, _ = cKDTree(X).query(As)
    out = os.path.join(REPO, 'data', 'torso', 'atria', f'{HEART}_to_g001_rigid.txt')
    np.savetxt(out, np.vstack([R, t]), header='rows 1-3: R (applied as x_mm @ R.T + t), row 4: t [mm]; heart coords in mm (cohort um / 1000)')
    res = {'heart': HEART, 'rotation_deg': float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))),
           'translation_mm': t.round(1).tolist(),
           'ours_to_theirs_median_p90_mm': [float(np.median(d1)), float(np.percentile(d1, 90))],
           'theirs_to_ours_median_p90_mm': [float(np.median(d2)), float(np.percentile(d2, 90))], 'file': out}
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
