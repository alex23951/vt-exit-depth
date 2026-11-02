"""D40 (2)'s anchor beside pose52.py's (report only; no mesh, no pose change).

D40 (2) (lock thread, 2 Nov 2026): c is 9.1's anchor, "the LA+RA surface centroid, taken as the mean of the nodes of the
cohort archive's LA_endo.surf and RA_endo.surf at the CT pose in T13". pose52.py's c is the area-weighted centroid of
the boundary faces of the cohort mesh's LA and RA elements (tags 3, 4), in the cohort frame; its CT pose adds t' to every
node (identity rotation), so the anchor in T13 is c + t'. This script reads both, in mm, per heart, and writes
anchor_d40.json. The primary pose is not changed (D40: "the primary is unchanged").
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/anchor_d40.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']


def surf_nodes(f):
    """Unique node indices of a cohort .surf file (header line, then 'Tr a b c' rows)."""
    with open(f) as fh:
        n = int(fh.readline().split()[0])
        T = np.loadtxt(fh, usecols=(1, 2, 3), dtype=np.int64, max_rows=n)
    return np.unique(T)


out = {'lock_sha256': G.LOCK_SHA, 'frame': 'cohort frame mm; CT pose in T13 = cohort + t_prime (pose52, identity rotation)'}
for h in HEARTS:
    P, E, tag = G.load_full(h)
    d = os.path.join(G.REPO, 'data', 'cohort', h, h)
    la, ra = surf_nodes(os.path.join(d, 'LA_endo.surf')), surf_nodes(os.path.join(d, 'RA_endo.surf'))
    both = np.union1d(la, ra)
    c40 = P[both].mean(0)
    pz = json.load(open(os.path.join(HERE, f'pose52_{h}.json')))
    tp = np.array(pz['t_prime_mm'])
    c52 = np.array(pz['centroid_readings']['surface_area_weighted (primary)']['c_mm'])
    out[h] = {'LA_endo_nodes': int(len(la)), 'RA_endo_nodes': int(len(ra)), 'shared_nodes': int(len(la) + len(ra) - len(both)),
              'D40_c_cohort_mm': c40.round(3).tolist(), 'D40_c_CT_pose_T13_mm': (c40 + tp).round(3).tolist(),
              'pose52_c_cohort_mm': c52.round(3).tolist(), 'pose52_c_CT_pose_T13_mm': (c52 + tp).round(3).tolist(),
              'pose52_minus_D40_mm': (c52 - c40).round(3).tolist(),
              'pose52_minus_D40_norm_mm': round(float(np.linalg.norm(c52 - c40)), 3)}
    print(h, json.dumps(out[h]))
json.dump(out, open(os.path.join(HERE, 'anchor_d40.json'), 'w'), indent=1)
