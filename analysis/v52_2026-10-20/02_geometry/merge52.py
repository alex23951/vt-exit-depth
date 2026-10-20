"""v5.2 step 2c-2d: the merged simulation mesh (v5.1 ventricles + re-tagged outflow muscle) and its surfaces.

Node and element order: the v5.1 biv mesh first, unchanged (same ids), then the re-tagged full-mesh elements (crescents
as tag 1, sleeves as tag 2) and their new nodes, appended in full-mesh order. So every v5.1 node id, site, network node
and surface keeps its meaning.
Surfaces: as sims/biv_model/01_extract.py on the merged element set (neighbour tag across each boundary face; free faces
split with the cohort's LV_endo / RV_endo / epicardium surfaces, the rest epicardium), with one addition: free faces of
re-tagged sleeve or crescent elements that face their vessel's lumen (outward normal toward the vessel axis) are luminal,
so they join rv_endo (sleeves) or lv_endo (crescents), not the epicardium (mine; v5.1 had no such faces).
Outputs (data, git-ignored): data/biv/<H>/v52/biv52.{pts,elem,nod}, surfaces/*.{surf,vtx}, merge52_<H>.json here.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/merge52.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                           # noqa: E402
from common import boundary_faces, face_key, read_surf, tet_faces, write_surf, write_vtx    # noqa: E402

NAMES = {7: 'mv_rim', 8: 'tv_rim', 9: 'av_rim', 10: 'pv_rim', 27: 'avplane_iface', 5: 'ao_iface', 6: 'part_iface', 3: 'la_iface', 4: 'ra_iface'}


def out_dir(h):
    return os.path.join(G.REPO, 'data', 'biv', h, 'v52')


def merge(h):
    t0 = time.time()
    P, E, tag = G.load_full(h)
    Pb, Eb, tb, nod = G.load_biv(h)
    z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
    cid, sid, fib_full = z['crescent_elements'], z['sleeve_elements'], z['fibrous_nodes']
    vent = np.where(np.isin(tag, G.VENT))[0]
    new = np.sort(np.concatenate([cid, sid]))
    newtag = np.where(np.isin(new, cid), 1, 2)
    allel = np.concatenate([vent, new])
    tag_m = np.concatenate([tag[vent], newtag])
    new_nodes = np.setdiff1d(np.unique(E[new]), nod) if len(new) else np.zeros(0, np.int64)
    nod_m = np.concatenate([nod, new_nodes])
    f2m = np.full(len(P), -1, np.int64); f2m[nod_m] = np.arange(len(nod_m))
    Em = f2m[E[allel]]
    assert (Em >= 0).all() and np.array_equal(Em[:len(Eb)], Eb), 'v5.1 part changed'
    Pm = P[nod_m]
    # surfaces (01_extract logic on the merged set)
    inm = np.zeros(len(E), bool); inm[allel] = True
    bf_m, own_m = boundary_faces(Em)
    bf_full = nod_m[bf_m]
    other = ~inm
    of, oown = tet_faces(E[other])
    okey = face_key(of); order = np.argsort(okey); okey_s = okey[order]; otag_s = tag[other][oown][order]
    k = face_key(bf_full); pos = np.searchsorted(okey_s, k); pos[pos >= len(okey_s)] = 0
    hit = okey_s[pos] == k
    ntag = np.where(hit, otag_s[pos], 0)
    SRC = os.path.join(G.REPO, 'data', 'cohort', h, h)
    keyset = lambda n: set(face_key(read_surf(os.path.join(SRC, n))).tolist())
    lvs, rvs, epis = keyset('LV_endo.surf'), keyset('RV_endo.surf'), keyset('epicardium_for_sim.surf')
    cls = np.full(len(bf_m), 'epi', dtype=object)
    kk = k.tolist()
    free = ntag == 0
    for i in np.where(free)[0]:
        cls[i] = 'lv_endo' if kk[i] in lvs else 'rv_endo' if kk[i] in rvs else 'epi'
    for t, n in NAMES.items():
        cls[ntag == t] = n
    for t in sorted(set(ntag[~free].tolist()) - set(NAMES)):
        cls[ntag == t] = f'tag{t}_iface'
    # luminal free faces of re-tagged elements
    lum_added = {'rv_endo': 0, 'lv_endo': 0}
    if len(new):
        av, _ = G.aortic_frame(P, E, tag); pv, _ = G.pulmonary_frame(P, E, tag)
        onew = own_m >= len(vent)
        for i in np.where(free & onew)[0]:
            f = Pm[bf_m[i]]; fc = f.mean(0)
            nrm = np.cross(f[1] - f[0], f[2] - f[0]); nrm /= np.linalg.norm(nrm)
            tc = Pm[Em[own_m[i]]].mean(0)
            if nrm @ (fc - tc) < 0:
                nrm = -nrm
            sleeve = tag_m[own_m[i]] == 2
            vv = pv if sleeve else av
            d = fc - vv.c; rad = d - (d @ vv.n) * vv.n; rad /= np.linalg.norm(rad)
            if nrm @ rad < -0.3:
                cls[i] = 'rv_endo' if sleeve else 'lv_endo'
                lum_added['rv_endo' if sleeve else 'lv_endo'] += 1
    D = out_dir(h); os.makedirs(os.path.join(D, 'surfaces'), exist_ok=True)
    with open(os.path.join(D, 'biv52.pts'), 'w') as fh:
        fh.write(f'{len(Pm)}\n'); np.savetxt(fh, Pm * 1e3, fmt='%.6f')
    with open(os.path.join(D, 'biv52.elem'), 'w') as fh:
        fh.write(f'{len(Em)}\n'); np.savetxt(fh, np.c_[Em, tag_m], fmt='Tt %d %d %d %d %d')
    nod_m.astype(np.int64).tofile(os.path.join(D, 'biv52.nod'))
    surf = {}
    for n in sorted(set(cls.tolist())):
        tri = bf_m[cls == n]
        write_surf(os.path.join(D, 'surfaces', n + '.surf'), tri)
        write_vtx(os.path.join(D, 'surfaces', n + '.vtx'), tri.ravel())
        surf[n] = {'faces': int(len(tri)), 'nodes': int(len(np.unique(tri)))}
    # the v5.1 apex patch and apex node keep their ids
    for n in ('apex', 'apex_patch'):
        src = os.path.join(G.REPO, 'data', 'biv', h, 'surfaces', n + '.vtx')
        open(os.path.join(D, 'surfaces', n + '.vtx'), 'w').write(open(src).read())
    fib_m = f2m[fib_full] if len(fib_full) else np.zeros(0, np.int64)
    np.save(os.path.join(D, 'fibrous_nodes52.npy'), fib_m)
    # v5.1 surfaces unchanged for old faces?
    old = {}
    for n in ('lv_endo', 'rv_endo', 'epi'):
        a = set(face_key(read_surf(os.path.join(G.REPO, 'data', 'biv', h, 'surfaces', n + '.surf'))).tolist())
        b = set(face_key(read_surf(os.path.join(D, 'surfaces', n + '.surf'))).tolist())
        old[n] = {'v51_faces': len(a), 'v52_faces': len(b), 'v51_faces_kept': len(a & b), 'added': len(b - a), 'removed': len(a - b)}
    rec = {'heart': h, 'v51_nodes': int(len(Pb)), 'v51_elements': int(len(Eb)), 'nodes': int(len(Pm)), 'elements': int(len(Em)),
           'added_elements': {'crescent (tag 1)': int(len(cid)), 'sleeve (tag 2)': int(len(sid))}, 'added_nodes': int(len(new_nodes)),
           'added_volume_mm3': round(float(G.tet_vol(P, E[new]).sum()), 2) if len(new) else 0.0,
           'surfaces': surf, 'luminal_faces_of_added_elements': lum_added, 'surface_change_vs_v51': old,
           'fibrous_layer_nodes': int(len(fib_m)), 'identical_to_v51': bool(len(new) == 0),
           'pts_sha256': G.sha256(os.path.join(D, 'biv52.pts')), 'elem_sha256': G.sha256(os.path.join(D, 'biv52.elem')),
           'wall_s': round(time.time() - t0, 1)}
    G.dump(rec, os.path.join(HERE, f'merge52_{h}.json'))
    print(h, f"nodes {rec['v51_nodes']} -> {rec['nodes']}, elements {rec['v51_elements']} -> {rec['elements']}, added {rec['added_elements']},",
          f"surface changes {[(n, v['added'], v['removed']) for n, v in old.items()]}, {rec['wall_s']} s", flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        merge(h)
