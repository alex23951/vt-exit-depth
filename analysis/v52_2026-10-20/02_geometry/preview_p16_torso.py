"""P16 (4)(a), read only: edge lengths of the heart-torso mesh the v5.1 lead fields were solved on (no v5.2 torso exists yet).

Mesh: data/biv/<H>/torso/full_nofast_blood_v51 (08_torso.py meshtool generate, skin resampled to 8 mm; blood retagged
101 by conductor51.py). Per element the mean of its 6 edge lengths, for torso + blood elements (tags 100, 101): all, near
the heart (centroid within 5 mm of a heart node, tags 1 and 2), far (over 20 mm), and within 10 mm of each electrode
node (data/biv/<H>/torso/electrodes). Nothing is built or solved.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p16_torso.py
"""
import glob
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def pct(x):
    return [round(float(v), 2) for v in np.percentile(x, [5, 50, 95])] if len(x) else None


def run(h):
    T = os.path.join(G.REPO, 'data', 'biv', h, 'torso')
    P = read_pts(os.path.join(T, 'full_nofast_blood_v51')) / 1e3
    E, tag = read_elem(os.path.join(T, 'full_nofast_blood_v51'))
    edge = np.mean([np.linalg.norm(P[E[:, a]] - P[E[:, b]], axis=1) for a, b in PAIRS], axis=0)
    hn = np.unique(E[np.isin(tag, [1, 2])]); th = cKDTree(P[hn])
    tor = np.isin(tag, [100, 101]); cen = P[E[tor]].mean(1); et = edge[tor]
    dh = th.query(cen, distance_upper_bound=25.0)[0]
    out = {'heart': h, 'nodes': int(len(P)), 'elements': int(len(E)), 'tags': {int(t): int((tag == t).sum()) for t in np.unique(tag)},
           'torso_and_blood_edge_mm_p5_p50_p95': pct(et), 'near_heart_lt5mm': pct(et[dh < 5]), 'far_gt20mm': pct(et[~(dh < 20)]),
           'heart_edge_mm_p5_p50_p95': pct(edge[np.isin(tag, [1, 2])]), 'electrodes_within_10mm': {}}
    tc = cKDTree(cen)
    for f in sorted(glob.glob(os.path.join(T, 'electrodes', '*.vtx'))):
        n = read_vtx(f)
        j = tc.query_ball_point(P[n[0]], 10.0)
        out['electrodes_within_10mm'][os.path.basename(f)[:-4]] = {'elements': len(j), 'edge_mm_median': round(float(np.median(et[j])), 2) if j else None}
    print(out, flush=True)
    return out


if __name__ == '__main__':
    G.dump({h: run(h) for h in (sys.argv[1:] or G.HEARTS)}, os.path.join(HERE, 'preview_p16_torso.json'))
