#!/usr/bin/env python
"""
Step 3: universal-ventricular-style coordinates from the step-2 Laplace fields.

Method (Bayer et al. 2018 UVC idea, with outflow tracts handled by putting all four
valve rims and the aortic / pulmonary interfaces in the base boundary, as in
Doste et al. 2019, so the outflow tracts run up to apex-to-base = 1 at their valves):

  z    apex-to-base, 0 = apex, 1 = base/valves. The raw Laplace field (zeta) bunches
       towards the base in a cone-shaped ventricle, so it is remapped monotonically
       (ordering kept) so that its mean follows normalised distance along the LV long
       axis (apex point -> MV/TV rim centroid). Raw field kept as z_laplace.
  rho  transmural, 0 = endocardium (LV or RV), 1 = epicardium (phi_epi).
  sep  septal position, 0 = LV endo, 1 = RV endo: phi_rv / (phi_lv + phi_rv); used for
       depth inside the septum, where rho has no epicardium.
  v    ventricle, 0 = LV, 1 = RV (Laplace LV endo -> RV endo, thresholded at 0.5).
  phi  rotational, radians in (-pi, pi], angle around the LV long axis; 0 = direction
       from the LV axis to the RV endocardial centroid (septum), +pi/2 = anterior.

Writes data/biv/<HEART>/uvc/<name>.dat (nodal) and summary_03.json.
"""

import json
import os

import numpy as np

from common import BIV, OUT, read_elem, read_pts, read_vtx

LAP = os.path.join(OUT, 'laplace')
SURF = os.path.join(OUT, 'surfaces')
UVC = os.path.join(OUT, 'uvc')


def lap(n):
    return np.loadtxt(os.path.join(LAP, n + '.dat'))


def main():
    os.makedirs(UVC, exist_ok=True)
    pts = read_pts(BIV)
    E, tag = read_elem(BIV)
    apex = pts[read_vtx(os.path.join(SURF, 'apex.vtx'))[0]]
    base_c = pts[np.concatenate([read_vtx(os.path.join(SURF, f)) for f in ('mv_rim.vtx', 'tv_rim.vtx')])].mean(0)
    axis = (base_c - apex) / np.linalg.norm(base_c - apex)
    s = np.clip((pts - apex) @ axis / np.linalg.norm(base_c - apex), 0, 1)   # normalised axial distance

    zl = np.clip(lap('zeta'), 0, 1)
    # monotone remap: mean axial distance per zeta-quantile bin, made non-decreasing
    q = np.quantile(zl, np.linspace(0, 1, 201))
    q = np.unique(q)
    idx = np.clip(np.searchsorted(q, zl, side='right') - 1, 0, len(q) - 2)
    centre = np.array([zl[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    target = np.array([s[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    ok = ~np.isnan(centre)
    centre, target = centre[ok], np.maximum.accumulate(target[ok])
    xs = np.concatenate([[0.0], centre, [1.0]])
    ys = np.concatenate([[0.0], target, [1.0]])
    ys = np.maximum.accumulate(ys)
    ys = (ys - ys[0]) / (ys[-1] - ys[0])
    z = np.interp(zl, xs, ys)

    rho = np.clip(lap('phi_epi'), 0, 1)
    plv, prv = np.clip(lap('phi_lv'), 0, 1), np.clip(lap('phi_rv'), 0, 1)
    sep = prv / np.maximum(plv + prv, 1e-9)
    v = (lap('v') > 0.5).astype(float)

    rv_c = pts[read_vtx(os.path.join(SURF, 'rv_endo.vtx'))].mean(0)
    def perp(x):
        return x - np.outer(x @ axis, axis) if x.ndim > 1 else x - (x @ axis) * axis
    e1 = perp(rv_c - apex); e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    ant = np.array([0, -1.0, 0])                   # LPS frame: -y is anterior
    if e2 @ ant < 0:
        e2 = -e2
    r = perp(pts - apex)
    phi = np.arctan2(r @ e2, r @ e1)

    for n, x in (('z', z), ('z_laplace', zl), ('rho', rho), ('sep', sep), ('v', v), ('phi', phi)):
        np.savetxt(os.path.join(UVC, n + '.dat'), x, fmt='%.6g')

    # sanity checks
    lvtag = np.isin(tag, [1, 25, 29])
    node_lv = np.zeros(len(pts), bool)
    node_lv[np.unique(E[lvtag])] = True
    node_rvonly = np.zeros(len(pts), bool)
    node_rvonly[np.unique(E[~lvtag])] = True
    node_rvonly &= ~node_lv
    chk = {
        'ranges': {n: [float(x.min()), float(x.max())] for n, x in
                   (('z', z), ('z_laplace', zl), ('rho', rho), ('sep', sep), ('v', v), ('phi', phi))},
        'z_deciles': np.percentile(z, np.arange(10, 100, 10)).round(3).tolist(),
        'z_laplace_deciles': np.percentile(zl, np.arange(10, 100, 10)).round(3).tolist(),
        'corr_z_vs_axial_distance': float(np.corrcoef(z, s)[0, 1]),
        'corr_z_laplace_vs_axial_distance': float(np.corrcoef(zl, s)[0, 1]),
        'rho_on_endo_mean': float(rho[np.unique(np.concatenate([read_vtx(os.path.join(SURF, f)) for f in ('lv_endo.vtx', 'rv_endo.vtx')]))].mean()),
        'rho_on_epi_mean': float(rho[read_vtx(os.path.join(SURF, 'epi.vtx'))].mean()),
        'v_agrees_with_tags_LVside': float((v[node_lv] == 0).mean()),
        'v_agrees_with_tags_RVonly': float((v[node_rvonly] == 1).mean()),
        'phi_at_rv_centroid_dir_deg': 0.0,
        'base_minus_apex_mm': float(np.linalg.norm(base_c - apex) / 1e3),
    }
    with open(os.path.join(OUT, 'summary_03.json'), 'w') as f:
        json.dump(chk, f, indent=1)
    print(json.dumps(chk, indent=1))


if __name__ == '__main__':
    main()
