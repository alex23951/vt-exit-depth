#!/usr/bin/env python
"""
Step 1: extract the ventricular myocardium and its boundary surfaces.

- meshtool extract mesh, tags 1, 2, 25, 28, 29 (LV, RV, fast endocardial LV/RV/septum).
  Outflow-tract muscle stays in LV/RV up to the valve planes (no cutting).
- Every boundary face of the ventricular mesh is classified by what lies on the
  other side in the four-chamber mesh: a valve plane (MV 7, TV 8, AV 9, PV 10), the
  atrioventricular plane (27), aortic / pulmonary wall (5, 6), atria (3, 4), or
  nothing (free surface). Free faces are split into LV endo, RV endo and epicardium
  with the authors' LV_endo.surf / RV_endo.surf / epicardium_for_sim.surf.
- Writes biv.{pts,elem,lon,nod,eidx} and surfaces/<name>.{surf,vtx} in data/biv/<HEART>/,
  plus summary_01.json.
"""

import json
import os
import subprocess

import numpy as np

from common import (BIV, OUT, SRC, SRC_MESH, TAG_NAMES, VENT_TAGS, boundary_faces, face_key,
                    read_elem, read_pts, read_surf, tet_faces, write_surf, write_vtx)


def main():
    os.makedirs(os.path.join(OUT, 'surfaces'), exist_ok=True)
    subprocess.run(['meshtool', 'extract', 'mesh', f'-msh={SRC_MESH}',
                    '-tags=' + ','.join(map(str, VENT_TAGS)), f'-submsh={BIV}',
                    '-ifmt=carp_bin', '-ofmt=carp_txt'], check=True, stdout=subprocess.DEVNULL)

    nod = np.fromfile(BIV + '.nod', dtype=np.int64)         # submesh node -> full mesh node (binary int64)
    pts = read_pts(BIV)
    E, tag = read_elem(BIV)
    Ef, tagf = read_elem(SRC_MESH)

    bf, _ = boundary_faces(E)                                # submesh numbering
    bf_full = nod[bf]                                        # full numbering

    # neighbour tag across each boundary face (from non-ventricular full-mesh elements)
    other = ~np.isin(tagf, VENT_TAGS)
    of, oown = tet_faces(Ef[other])
    okey = face_key(of)
    order = np.argsort(okey)
    okey_s, otag_s = okey[order], tagf[other][oown][order]
    k = face_key(bf_full)
    pos = np.searchsorted(okey_s, k)
    pos[pos >= len(okey_s)] = 0
    hit = okey_s[pos] == k
    ntag = np.where(hit, otag_s[pos], 0)

    # free surface split with the authors' surfaces (full numbering)
    def keyset(name):
        return set(face_key(read_surf(os.path.join(SRC, name))).tolist())
    lv, rv, epi = keyset('LV_endo.surf'), keyset('RV_endo.surf'), keyset('epicardium_for_sim.surf')
    free = ntag == 0
    cls = np.full(len(bf), 'unassigned', dtype=object)
    kk = k.tolist()
    for i in np.where(free)[0]:
        cls[i] = 'lv_endo' if kk[i] in lv else 'rv_endo' if kk[i] in rv else 'epi' if kk[i] in epi else 'epi_extra'
    # free faces outside the authors' three surfaces all lie on the epicardial side
    # (checked 2026-10-02: none touch LV/RV endo nodes), so they are epicardium too
    n_extra = int((cls == 'epi_extra').sum())
    cls[cls == 'epi_extra'] = 'epi'
    names = {7: 'mv_rim', 8: 'tv_rim', 9: 'av_rim', 10: 'pv_rim', 27: 'avplane_iface',
             5: 'ao_iface', 6: 'part_iface', 3: 'la_iface', 4: 'ra_iface'}
    for t, n in names.items():
        cls[ntag == t] = n
    other_tags = sorted(set(ntag[~free].tolist()) - set(names))
    for t in other_tags:
        cls[ntag == t] = f'tag{t}_iface'

    summary = {'nodes': int(len(pts)), 'elements': int(len(E)),
               'elements_by_tag': {TAG_NAMES[int(t)]: int((tag == t).sum()) for t in np.unique(tag)},
               'bbox_mm': [(pts.min(0) / 1e3).round(1).tolist(), (pts.max(0) / 1e3).round(1).tolist()],
               'boundary_faces': int(len(bf)), 'epi_faces_not_in_author_surface': n_extra,
               'surfaces': {}}
    for n in sorted(set(cls.tolist())):
        tri = bf[cls == n]
        write_surf(os.path.join(OUT, 'surfaces', n + '.surf'), tri)
        write_vtx(os.path.join(OUT, 'surfaces', n + '.vtx'), tri.ravel())
        summary['surfaces'][n] = {'faces': int(len(tri)), 'nodes': int(len(np.unique(tri)))}
    with open(os.path.join(OUT, 'summary_01.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
