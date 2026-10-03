#!/usr/bin/env python
"""
Step 5b: LBBB-like variant (frozen definition: "LV activated without left-sided fast-layer
entry"). Every fast-layer element (tag 2) that touches the LV endocardium, which includes
the left septal surface, gets myocardial properties (tag 1); the RV-side layer stays fast.
(Cohort tag 29, FEC_SV, lines the RV side of the septum in these meshes: 6G8DD8S5 check
2026-10-03, 100 % of its elements touch the RV endocardium, 0 % the LV.)

Writes data/biv/<HEART>/bivF_lbbb.{elem,pts,lon} (pts/lon symlinked to bivF) and
summary_05b.json. Used for 6G8DD8S5 (the HF wide-QRS heart) in the site grid.
"""

import json
import os

import numpy as np

from common import OUT, read_elem, read_pts, read_vtx


def main():
    base = os.path.join(OUT, 'bivF')
    pts = read_pts(base)
    E, tag = read_elem(base)
    lv = np.zeros(len(pts), bool)
    lv[read_vtx(os.path.join(OUT, 'surfaces', 'lv_endo.vtx'))] = True
    left = (tag == 2) & lv[E].any(1)
    new = tag.copy()
    new[left] = 1
    out = os.path.join(OUT, 'bivF_lbbb')
    with open(out + '.elem', 'w') as f:
        f.write(f'{len(E)}\n')
        np.savetxt(f, np.hstack([E, new[:, None]]), fmt='Tt %d %d %d %d %d')
    for ext in ('pts', 'lon'):
        if not os.path.exists(f'{out}.{ext}'):
            os.symlink(f'bivF.{ext}', f'{out}.{ext}')
    s = {'fast_elements_before': int((tag == 2).sum()), 'set_to_myocardium_lv_side': int(left.sum()),
         'fast_elements_after_rv_side': int((new == 2).sum())}
    json.dump(s, open(os.path.join(OUT, 'summary_05b.json'), 'w'), indent=1)
    print(json.dumps(s))


if __name__ == '__main__':
    main()
