"""v5.2 step 0: can the cohort surfaces be capped as R3.1 says? (LOCK.md 15.2 step 0, R3.1), read only.

For the LA (tag 3), RA (4), aortic root (5) and pulmonary artery (6) of each heart, on the full cohort mesh:
  1. Boundary components of the mesh: which cavity surfaces are already closed (each edge in two faces) and what they hold.
  2. Vein rings: on each atrial cavity surface, the loops where atrial-wall faces meet vein-wall faces (tags 11-17), the
     place a vein cap would sit; each loop is checked to be a simple closed curve.
  3. A voxel flood fill (0.75 mm) of each cavity from a seed inside it, with the great vessels capped at their cut ends by
     the convex hull of their wall nodes; leak = the fill reaching the grid edge or exceeding 1 L. LV and RV are filled the
     same way as a control against the v5.1 C6 volumes and the cohort's dataset_info.csv volumes.
Nothing is built or adopted here; step 5 builds the surfaces with the R3.2 gates.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/00_step0/step0_cavities.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import Delaunay

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))
from common import boundary_faces                                           # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
H_VOX = 0.75
VEINS = {11: 'LSPV', 12: 'LIPV', 13: 'RSPV', 14: 'RIPV', 15: 'LAA', 16: 'SVC', 17: 'IVC'}


def load(h):
    base = os.path.join(REPO, 'data', 'cohort', h, h, 'myocardium_AV_FEC_BB_lvrv')
    E = pd.read_csv(base + '.elem', sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).to_numpy()
    P = pd.read_csv(base + '.pts', sep=' ', skiprows=1, header=None).to_numpy() / 1e3
    return P, E[:, :4].astype(np.int64), E[:, 4].astype(np.int64)


def components(bf):
    fe = np.vstack([np.sort(bf[:, [0, 1]], 1), np.sort(bf[:, [1, 2]], 1), np.sort(bf[:, [0, 2]], 1)])
    fid = np.tile(np.arange(len(bf)), 3); key = fe[:, 0] * (1 << 21) + fe[:, 1]
    o = np.argsort(key); ks = key[o]; fs = fid[o]; sm = ks[1:] == ks[:-1]
    G = coo_matrix((np.ones(sm.sum()), (fs[:-1][sm], fs[1:][sm])), shape=(len(bf), len(bf)))
    _, lab = connected_components(G, directed=False)
    return lab


def edge_counts(F):
    e = np.vstack([np.sort(F[:, [0, 1]], 1), np.sort(F[:, [1, 2]], 1), np.sort(F[:, [0, 2]], 1)])
    _, c = np.unique(e, axis=0, return_counts=True)
    return {'edges': int(len(c)), 'in_1_face': int((c == 1).sum()), 'in_2_faces': int((c == 2).sum()), 'in_3plus_faces': int((c > 2).sum())}


def loops(F_a, F_b):
    """Edges shared by a face of set a and a face of set b; their loops and whether each is a simple cycle."""
    ea = np.vstack([np.sort(F_a[:, [0, 1]], 1), np.sort(F_a[:, [1, 2]], 1), np.sort(F_a[:, [0, 2]], 1)])
    eb = np.vstack([np.sort(F_b[:, [0, 1]], 1), np.sort(F_b[:, [1, 2]], 1), np.sort(F_b[:, [0, 2]], 1)])
    ka = set((ea[:, 0] * (1 << 21) + ea[:, 1]).tolist()); kb = (eb[:, 0] * (1 << 21) + eb[:, 1])
    m = np.array([k in ka for k in kb.tolist()])
    E = np.unique(eb[m], axis=0)
    if not len(E):
        return []
    nodes = np.unique(E); loc = {int(n): i for i, n in enumerate(nodes)}
    r = np.array([loc[int(a)] for a in E[:, 0]]); c = np.array([loc[int(b)] for b in E[:, 1]])
    G = coo_matrix((np.ones(len(r)), (r, c)), shape=(len(nodes), len(nodes)))
    nc, lab = connected_components(G, directed=False)
    deg = np.bincount(np.r_[r, c], minlength=len(nodes))
    return [{'nodes': int((lab == k).sum()), 'simple_cycle': bool((deg[lab == k] == 2).all())} for k in range(nc)]


def voxelise(P, E, lo, shape):
    solid = np.zeros(shape, bool)
    W = [np.eye(4)[i] for i in range(4)] + [np.full(4, 0.25)]
    W += [0.5 * (np.eye(4)[i] + np.eye(4)[j]) for i in range(4) for j in range(i + 1, 4)]
    W += [(np.ones(4) - np.eye(4)[i]) / 3 for i in range(4)]
    for i0 in range(0, len(E), 400000):
        X = P[E[i0:i0 + 400000]]                                   # (k, 4, 3)
        for w in W:
            Y = np.einsum('j,kjd->kd', w, X)
            ix = np.floor((Y - lo) / H_VOX).astype(int)
            ok = np.all((ix >= 0) & (ix < np.array(shape)), 1)
            solid[ix[ok, 0], ix[ok, 1], ix[ok, 2]] = True
    return ndimage.binary_closing(solid, iterations=1) | solid


def flood(solid, lo, seed, allowed=None):
    free = ~solid if allowed is None else (~solid & allowed)
    s = tuple(np.floor((seed - lo) / H_VOX).astype(int))
    if not free[s]:
        return None, 'seed in solid'
    lab, _ = ndimage.label(free)
    m = lab == lab[s]
    edge = m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any() or m[:, :, 0].any() or m[:, :, -1].any()
    vol = float(m.sum() * H_VOX ** 3 / 1000.0)
    return {'volume_ml': round(vol, 1), 'touches_grid_edge': bool(edge), 'leak': bool(edge or vol > 1000)}, m


def heart(h, info):
    t0 = time.time()
    P, E, tag = load(h)
    bf, own = boundary_faces(E)
    lab = components(bf)
    comp = {}
    for k in np.unique(lab):
        tt = set(np.unique(tag[own[lab == k]]).tolist())
        comp[int(k)] = tt
    def find(req):
        ks = [k for k, tt in comp.items() if req <= tt]
        return max(ks, key=lambda k: (lab == k).sum()) if ks else None
    cav = {'LV': find({1, 7, 9}), 'RV': find({2, 8, 10}), 'LA': find({3, 7}), 'RA': find({4, 8})}
    outer = max(comp, key=lambda k: (lab == k).sum())
    res = {'boundary_components': {int(k): {'faces': int((lab == k).sum()), 'tags': sorted(comp[k])} for k in comp if (lab == k).sum() > 10},
           'outer_component_holds_the_great-vessel_lumens': bool({5, 6, 9, 10} <= comp[outer])}
    # 1-2: closedness and vein-ring loops
    for nm, k in cav.items():
        F = bf[lab == k]
        r = {'component': k, 'faces': int(len(F)), 'edge_use': edge_counts(F), 'closed': edge_counts(F)['in_1_face'] == 0}
        if nm in ('LA', 'RA'):
            wall = [3, 26] if nm == 'LA' else [4, 26]
            Fw = F[np.isin(tag[own[lab == k]], wall)]
            r['veins_on_cavity_surface'] = {}
            for vt, vn in VEINS.items():
                Fv = F[tag[own[lab == k]] == vt]
                if len(Fv):
                    r['veins_on_cavity_surface'][vn] = {'faces': int(len(Fv)), 'ostium_loops': loops(Fw, Fv)}
        res[nm] = r
    # 3: voxel fills
    lo = P.min(0) - 5; shape = tuple(np.ceil((P.max(0) + 5 - lo) / H_VOX).astype(int) + 1)
    solid = voxelise(P, E, lo, shape)
    res['voxel'] = {'size_mm': H_VOX, 'grid': list(shape), 'solid_fraction': round(float(solid.mean()), 3)}
    g = np.stack(np.meshgrid(*[lo[d] + H_VOX * (np.arange(shape[d]) + 0.5) for d in range(3)], indexing='ij'), -1)
    fills = {}
    for nm, k in cav.items():
        F = bf[lab == k]; ow = own[lab == k]
        wall = {'LV': [1, 25, 29], 'RV': [2, 28, 29], 'LA': [3], 'RA': [4]}[nm]
        sel = np.where(np.isin(tag[ow], wall))[0]
        C = P[F[sel]].mean(1)
        n = np.cross(P[F[sel, 1]] - P[F[sel, 0]], P[F[sel, 2]] - P[F[sel, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True)
        tc = P[E[ow[sel]]].mean(1)
        n *= np.sign(np.einsum('ij,ij->i', n, C - tc))[:, None]                 # away from the owning tet = into the cavity
        order = np.argsort(np.linalg.norm(C - C.mean(0), axis=1))
        out = None
        for i in order[:200]:
            seed = C[i] + 3.0 * n[i]
            out, m = flood(solid, lo, seed)
            if out is not None:
                out['seed_mm'] = seed.round(1).tolist()
                break
        fills[nm] = out
    for nm, vtag, wtag in (('aortic_root', 9, 5), ('pulmonary_artery', 10, 6)):
        X = P[np.unique(E[tag == vtag])]; c = X.mean(0)
        _, _, vt = np.linalg.svd(X - c, full_matrices=False); nrm = vt[2]
        Wn = P[np.unique(E[tag == wtag])]
        if (Wn.mean(0) - c) @ nrm < 0:
            nrm = -nrm
        half = float(np.percentile((X - c) @ nrm, 98))
        hull = Delaunay(np.vstack([Wn, X]))
        allowed = (hull.find_simplex(g.reshape(-1, 3)) >= 0).reshape(shape)
        out, m = flood(solid, lo, c + nrm * (half + 4.0), allowed)
        if out is not None:
            out['cap'] = 'cut end closed by the convex hull of the vessel-wall and valve-disc nodes'
            out['seed_mm'] = (c + nrm * (half + 4.0)).round(1).tolist()
            out['wall_length_above_disc_mm'] = round(float(((Wn - c) @ nrm).max()), 1)
        fills[nm] = out
    res['fills'] = fills
    ref = {'LV': 'Vol_LV', 'RV': 'Vol_RV', 'LA': 'Vol_LA', 'RA': 'Vol_RA'}
    res['dataset_info_volumes_ml'] = {k: info.get(v) for k, v in ref.items()}
    res['v51_C6_cavity_ml'] = {'Y5HYEDL4': (172.0, 197.9), '6G8DD8S5': (157.8, 107.2), '7D98EVAR': (172.8, 122.5)}[h]
    res['wall_s'] = round(time.time() - t0, 1)
    return res


def main():
    di = pd.read_csv(os.path.join(REPO, 'runs', 'v52_2026-10-20', '00_step0', 'dataset_info.csv'))
    out = {}
    for h in (sys.argv[1:] or HEARTS):
        row = di[di.apply(lambda r: h in ' '.join(map(str, r.values)), axis=1)]
        info = {c: float(row.iloc[0][c]) for c in ('Vol_LV', 'Vol_RV', 'Vol_LA', 'Vol_RA')} if len(row) else {}
        out[h] = heart(h, info)
        print(h, json.dumps(out[h]['fills']), out[h]['wall_s'], flush=True)
        json.dump(out, open(os.path.join(HERE, 'cavities.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
