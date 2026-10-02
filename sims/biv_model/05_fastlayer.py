#!/usr/bin/env python
"""
Step 5: fast endocardial layer (frozen definition 2026-10-02).

Layer = the endocardial element layer of LV, RV and septum (every element with at least
one node on the LV or RV endocardial surface, i.e. one element ~1 mm thick on this mesh),
restricted to 10 % <= z <= 90 % apex-to-base (element mean of the step-3 z coordinate).

Writes data/biv/<HEART>/bivF.elem with tags 1 = myocardium, 2 = fast layer
(replacing the symlink from step 4) and summary_05.json, including overlap with the
cohort's own fast-layer labels (tags 25, 28, 29).
"""

import json
import os

import numpy as np

from common import BIV, OUT, read_elem, read_pts, read_vtx

SURF = os.path.join(OUT, 'surfaces')
Z_LO, Z_HI = 0.10, 0.90


def main():
    pts = read_pts(BIV)
    E, tag = read_elem(BIV)
    z = np.loadtxt(os.path.join(OUT, 'uvc', 'z.dat'))
    endo = np.zeros(len(pts), bool)
    for n in ('lv_endo', 'rv_endo'):
        endo[read_vtx(os.path.join(SURF, n + '.vtx'))] = True
    touch = endo[E].any(1)
    ze = z[E].mean(1)
    fast = touch & (ze >= Z_LO) & (ze <= Z_HI)
    newtag = np.where(fast, 2, 1)

    out = os.path.join(OUT, 'bivF.elem')
    if os.path.islink(out):
        os.remove(out)
    with open(out, 'w') as fh:
        fh.write(f'{len(E)}\n')
        np.savetxt(fh, np.hstack([E, newtag[:, None]]), fmt='Tt %d %d %d %d %d')

    # mean layer thickness ~ layer volume / endocardial area within the z band
    x = pts[E] / 1e3
    vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    area = 0.0
    for n in ('lv_endo', 'rv_endo'):
        t = np.loadtxt(os.path.join(SURF, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
        y = pts[t] / 1e3
        a = 0.5 * np.linalg.norm(np.cross(y[:, 1] - y[:, 0], y[:, 2] - y[:, 0]), axis=1)
        zt = z[t].mean(1)
        area += a[(zt >= Z_LO) & (zt <= Z_HI)].sum()
    coh = np.isin(tag, [25, 28, 29])
    summ = {'fast_elements': int(fast.sum()), 'fraction_of_elements': float(fast.mean()),
            'fast_volume_ml': float(vol[fast].sum() / 1e3), 'endo_area_cm2_in_band': float(area / 100),
            'mean_thickness_mm': float(vol[fast].sum() / area),
            'cohort_fast_elements': int(coh.sum()),
            'overlap_jaccard': float((fast & coh).sum() / (fast | coh).sum()),
            'ours_inside_cohort_layer': float((fast & coh).sum() / fast.sum()),
            'cohort_inside_ours': float((fast & coh).sum() / coh.sum()),
            'cohort_layer_z_range_elements_5_95pct': np.percentile(ze[coh], [5, 95]).round(3).tolist()}
    with open(os.path.join(OUT, 'summary_05.json'), 'w') as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
