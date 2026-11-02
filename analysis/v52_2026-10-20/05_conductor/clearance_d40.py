"""D40 (1) on step 5's meshes: no node of the heart mesh as step 5 builds it (every tag, with blood and sleeves) within
12 mm of its torso's skin, or outside it, at the primary pose (D40, lock thread, 2 Nov 2026; 9.1's stop rule).

Heart mesh = every node of an element whose tag is not the torso's (100), in data/biv/<H>/v52/torso52/heart_torso52.
Distances, exact over the 24 triangles with the nearest centroids (pose52.skin_distance): (a) to the T13 skin surface
pose52 used (T_13_torso_coarse_surface.vtk, the surface v5.1 meshed from); (b) to the resampled skin that bounds the
step-5 mesh (torso52/skin). Inside: winding number of the 200 closest nodes about (a). Writes clearance_d40_<H>.json.
Usage (repo root, venv): HEART=<H> python -B analysis/v52_2026-10-20/05_conductor/clearance_d40.py
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import conductor52 as C                                                                     # noqa: E402

FLOOR_MM = 12.0


def surf(base):
    """A carp triangle mesh ('Tr a b c tag' rows), in mm."""
    P = C.read_pts(base) / 1e3
    with open(base + '.elem') as fh:
        n = int(fh.readline())
        T = np.loadtxt(fh, usecols=(1, 2, 3), dtype=np.int64, max_rows=n)
    return P, T


h = os.environ['HEART']
t0 = time.time()
Pf, Ef, tf = C.read_carp(C.tdir(h, 'heart_torso52'))
hn = np.unique(Ef[tf != C.TAG_TORSO]); X = Pf[hn]
del Ef
S, tri = C.PO.read_vtk_polydata(C.T13 + '_torso_coarse_surface.vtk')
Sr, trir = surf(C.tdir(h, 'skin'))
da, dr = C.PO.skin_distance(X, S, tri), C.PO.skin_distance(X, Sr, trir)
o = np.argsort(da)[:200]
wn = C.PO.winding(X[o], S, tri)
tag_at = {}
for d, nm in ((da, 'T13_coarse_skin'), (dr, 'resampled_skin_of_the_step5_mesh')):
    k = int(np.argmin(d))
    tag_at[nm] = {'min_mm': round(float(d.min()), 2), 'node': int(hn[k]), 'node_torso_mm': X[k].round(1).tolist(),
                  'nodes_under_floor': int((d < FLOOR_MM).sum())}
out = {'heart': h, 'lock_sha256': C.G.LOCK_SHA, 'rule': 'D40 (1), lock thread, 2 Nov 2026: 12 mm floor at the primary pose',
       'mesh': C.tdir(h, 'heart_torso52.elem'), 'elem_sha256': C.G.sha256(C.tdir(h, 'heart_torso52.elem')),
       'heart_mesh_nodes (every non-torso tag)': int(len(hn)), 'clearance': tag_at,
       'winding_200_closest (min, max)': [round(float(wn.min()), 4), round(float(wn.max()), 4)],
       'all_inside': bool((wn > 0.5).all()), 'floor_mm': FLOOR_MM,
       'pass': bool((wn > 0.5).all() and da.min() >= FLOOR_MM and dr.min() >= FLOOR_MM),
       'wall_s': round(time.time() - t0), 'python_peak_rss_MB': C.peak_mb()}
C.G.dump(out, os.path.join(HERE, f'clearance_d40_{h}.json'))
print(out)
if not out['pass']:
    sys.exit(f'{h}: D40 (1) 12 mm floor not met at the primary pose; stop and report (9.1)')
