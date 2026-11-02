"""C66's check of tag 26 (read only, the cohort mesh): do its elements lie in the atrial wall (next to tags 3 or 4, in no
cavity)? Per heart: element count and volume; connected regions (shared nodes) and whether each touches tag 3 and tag 4;
the distance of each element centroid to the nearest tag-3/4 node; on which boundary surfaces its faces lie (outer =
epicardium and great vessels, LA / RA = the atrial cavity surfaces); the tags it shares interior faces with.
conductor52.py build also counts tag-26 centroids inside the chamber surfaces (0 means in no cavity).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/05_conductor/tag26_c66.py [HEART ...]
"""
import json
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import conductor52 as C                                                                     # noqa: E402

G = C.G


def run(h):
    P, E, tag = G.load_full(h)
    e26 = np.where(tag == 26)[0]
    n_of = E[e26]
    A = coo_matrix((np.ones(n_of.size), (np.repeat(np.arange(len(e26)), 4), n_of.ravel())), shape=(len(e26), len(P))).tocsr()
    nc, lab = connected_components(A @ A.T, directed=False)
    nodes_of = {t: np.unique(E[tag == t]) for t in (3, 4)}
    near = {t: np.zeros(len(P), bool) for t in (3, 4)}
    for t in (3, 4):
        near[t][nodes_of[t]] = True
    regions = [{'elements': int((lab == k).sum()), 'touches_tag_3': bool(near[3][n_of[lab == k]].any()),
                'touches_tag_4': bool(near[4][n_of[lab == k]].any())} for k in range(nc)]
    d = cKDTree(P[np.concatenate([nodes_of[3], nodes_of[4]])]).query(P[n_of].mean(1))[0]
    x = P[n_of]
    vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    F, own = C.oriented_boundary(P, E)
    fl = C.face_components(F)
    size = Counter(fl.tolist())
    outer = max(size, key=size.get)
    name = {}
    for L in size:
        t = set(tag[own[fl == L]].tolist())
        name[L] = 'outer' if L == outer else 'void' if size[L] <= 20 else 'LA' if (3 in t and 4 not in t) else 'RA' if (4 in t and 3 not in t) \
            else 'LV' if 9 in t else 'RV' if 10 in t else f'other_{L}'
    on = Counter(name[L] for L in fl[tag[own] == 26])
    f = np.sort(np.concatenate([E[:, [1, 2, 3]], E[:, [0, 2, 3]], E[:, [0, 1, 3]], E[:, [0, 1, 2]]]), axis=1)
    o = np.tile(np.arange(len(E)), 4)
    N = len(P)
    g = pd.DataFrame({'a': f[:, 0] * N + f[:, 1], 'b': f[:, 2], 't': tag[o]}).groupby(['a', 'b'])['t'].agg(['min', 'max', 'count'])
    pair = g[(g['count'] == 2) & ((g['min'] == 26) ^ (g['max'] == 26))]
    other = np.where(pair['min'] == 26, pair['max'], pair['min'])
    out = {'heart': h, 'elements': int(len(e26)), 'volume_ml': round(float(vol.sum() / 1e3), 2), 'regions': regions,
           'every_region_touches_tag_3_or_4': all(r['touches_tag_3'] or r['touches_tag_4'] for r in regions),
           'elements_sharing_a_node_with_tag_3_or_4': int((near[3] | near[4])[n_of].any(1).sum()),
           'centroid_to_nearest_tag_3_4_node_mm (median, p95, max)': [round(float(np.median(d)), 2), round(float(np.percentile(d, 95)), 2), round(float(d.max()), 2)],
           'boundary_faces_by_surface': dict(on), 'interior_faces_shared_with_tags': {int(k): int(v) for k, v in Counter(other.tolist()).items()}}
    out['reading'] = ('one or two connected regions, each touching tag 3 and/or 4, with faces on the outer (epicardial) surface and on '
                      'the LA and RA cavity surfaces: a full-thickness part of the atrial walls, bordered by tags 3 and 4 and the vein '
                      'rings. Element by element, most tag-26 elements share no node with tags 3 or 4 (the region is wider than a '
                      'bundle: up to about 20 mm from the nearest tag-3/4 node).')
    return out


if __name__ == '__main__':
    res = {h: run(h) for h in (sys.argv[1:] or G.HEARTS)}
    G.dump(res, os.path.join(HERE, 'tag26_c66.json'))
    for h, r in res.items():
        print(h, {k: v for k, v in r.items() if k not in ('reading', 'heart')})
