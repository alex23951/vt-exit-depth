#!/usr/bin/env python
"""
Step 4: rule-based fibres (frozen rule 2026-10-02) with the Doste 2019 outflow-tract rule.

Bayer et al. 2012 LDRB, per element:
  d    = phi_rv / (phi_lv + phi_rv)                       (septal depth, LV -> RV)
  Q_lv = orient(axis(grad psi, -grad phi_lv), a_s(d), 0)
  Q_rv = orient(axis(grad psi,  grad phi_rv), a_s(d), 0)
  Q_endo = bislerp(Q_lv, Q_rv, d)
  Q_epi  = orient(axis(grad psi, grad phi_epi), a_w(phi_epi), 0)
  Q      = bislerp(Q_endo, Q_epi, phi_epi)
  a_s(d) = a_endo (1 - d) - a_endo d ;  a_w(e) = a_endo (1 - e) + a_epi e
  axis(u, v): e1 = u/|u| (longitudinal), e2 = v orthogonalised (transmural), e0 = e1 x e2
  orient(Q, a, b) = Q R_e2(a) R_e0(b);  fibre = column 0, sheet = column 1, normal = column 2.
Frozen angles: a_endo = +60, a_epi = -60 deg; sheet angle b = 0, which here makes the
sheet-normal transmural (sheets parallel to the wall, Alex's option (a)).

Doste et al. 2019 outflow-tract extension:
  grad psi = w grad psi_basal + (1 - w) grad psi_OT   (w: 1 = ventricle body, 0 = OT valves)
  a_endo(w) = 60 w + 90 (1 - w)   (OT endo 90 deg = longitudinal)
  a_epi(w)  = -60 w + 0 (1 - w)   (OT epi 0 deg = circumferential)
  sheet angle 0 in the OT as well (Doste: beta_OT = 0).
  Linear blending in w along the shorter path (60 -> 90, -60 -> 0).

Writes data/biv/<HEART>/bivF.{pts,elem,lon} (pts/elem symlinked to biv) and summary_04.json
with the angle difference from the cohort's own fibres (biv.lon).
"""

import json
import os

import numpy as np

from common import BIV, OUT, read_elem, read_lon, read_pts

LAP = os.path.join(OUT, 'laplace')
A_ENDO, A_EPI = 60.0, -60.0
A_OT_ENDO, A_OT_EPI = 90.0, 0.0


def lap(n):
    return np.loadtxt(os.path.join(LAP, n + '.dat'))


def elem_grad(pts, E, u):
    x0 = pts[E[:, 0]]
    J = np.stack([pts[E[:, 1]] - x0, pts[E[:, 2]] - x0, pts[E[:, 3]] - x0], axis=1)   # rows = edges
    du = np.stack([u[E[:, 1]] - u[E[:, 0]], u[E[:, 2]] - u[E[:, 0]], u[E[:, 3]] - u[E[:, 0]]], axis=1)
    return np.linalg.solve(J, du[..., None])[..., 0]


def unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-30)


def axis(u, v):
    e1 = unit(u)
    e2 = unit(v - np.sum(e1 * v, -1, keepdims=True) * e1)
    e0 = np.cross(e1, e2)
    return np.stack([e0, e1, e2], axis=-1)                       # columns


def orient(Q, a):
    """Rotate about column 2 (transmural) by angle a (rad); sheet angle 0."""
    c, s = np.cos(a), np.sin(a)
    R = np.zeros((len(a), 3, 3))
    R[:, 0, 0], R[:, 0, 1], R[:, 1, 0], R[:, 1, 1], R[:, 2, 2] = c, -s, s, c, 1
    return Q @ R


def rot2quat(R):
    """Rotation matrices (n,3,3) -> quaternions (n,4) [w,x,y,z]."""
    t = np.trace(R, axis1=1, axis2=2)
    q = np.zeros((len(R), 4))
    w = np.sqrt(np.maximum(0, 1 + t)) / 2
    x = np.sqrt(np.maximum(0, 1 + R[:, 0, 0] - R[:, 1, 1] - R[:, 2, 2])) / 2
    y = np.sqrt(np.maximum(0, 1 - R[:, 0, 0] + R[:, 1, 1] - R[:, 2, 2])) / 2
    z = np.sqrt(np.maximum(0, 1 - R[:, 0, 0] - R[:, 1, 1] + R[:, 2, 2])) / 2
    x = np.copysign(x, R[:, 2, 1] - R[:, 1, 2])
    y = np.copysign(y, R[:, 0, 2] - R[:, 2, 0])
    z = np.copysign(z, R[:, 1, 0] - R[:, 0, 1])
    q[:, 0], q[:, 1], q[:, 2], q[:, 3] = w, x, y, z
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def quat2rot(q):
    w, x, y, z = q.T
    return np.stack([
        np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], -1),
        np.stack([2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], -1),
        np.stack([2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)], -1)], 1)


def qmul(a, b):
    aw, ax, ay, az = a.T
    bw, bx, by, bz = b.T
    return np.stack([aw * bw - ax * bx - ay * by - az * bz, aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw], -1)


def bislerp(Qa, Qb, t):
    """Bayer 2012 bislerp: slerp to the closest of the axis-flip-equivalent rotations."""
    qa, qb = rot2quat(Qa), rot2quat(Qb)
    flips = [np.array([1, 0, 0, 0.]), np.array([0, 1, 0, 0.]), np.array([0, 0, 1, 0.]), np.array([0, 0, 0, 1.])]
    cands = np.stack([qmul(qa, np.broadcast_to(f, qa.shape)) for f in flips], 1)     # (n,4,4)
    dots = np.abs(np.einsum('nkq,nq->nk', cands, qb))
    k = np.argmax(dots, 1)
    qm = cands[np.arange(len(qa)), k]
    d = np.einsum('nq,nq->n', qm, qb)
    qm[d < 0] *= -1
    d = np.abs(d)
    th = np.arccos(np.clip(d, -1, 1))
    small = th < 1e-6
    st = np.where(small, 1, np.sin(th))
    wa = np.where(small, 1 - t, np.sin((1 - t) * th) / st)
    wb = np.where(small, t, np.sin(t * th) / st)
    q = wa[:, None] * qm + wb[:, None] * qb
    return quat2rot(q / np.linalg.norm(q, axis=1, keepdims=True))


def main():
    pts = read_pts(BIV)
    E, tag = read_elem(BIV)
    em = lambda u: u[E].mean(1)
    w = np.clip(em(lap('w')), 0, 1)
    plv, prv, pepi = (np.clip(em(lap(n)), 0, 1) for n in ('phi_lv', 'phi_rv', 'phi_epi'))
    d = prv / np.maximum(plv + prv, 1e-9)
    g = {n: elem_grad(pts, E, lap(n)) for n in ('basal', 'ot', 'phi_lv', 'phi_rv', 'phi_epi')}
    gpsi = w[:, None] * unit(g['basal']) + (1 - w[:, None]) * unit(g['ot'])

    a_endo = np.radians(A_ENDO * w + A_OT_ENDO * (1 - w))
    a_epi = np.radians(A_EPI * w + A_OT_EPI * (1 - w))
    a_s = a_endo * (1 - d) - a_endo * d
    a_w = a_endo * (1 - pepi) + a_epi * pepi

    Q_lv = orient(axis(gpsi, -g['phi_lv']), a_s)
    Q_rv = orient(axis(gpsi, g['phi_rv']), a_s)
    Q_endo = bislerp(Q_lv, Q_rv, d)
    Q_epi = orient(axis(gpsi, g['phi_epi']), a_w)
    Q = bislerp(Q_endo, Q_epi, pepi)
    f, s = unit(Q[:, :, 0]), unit(Q[:, :, 1])

    out = os.path.join(OUT, 'bivF')
    for ext in ('pts', 'elem'):
        if not os.path.exists(f'{out}.{ext}'):
            os.symlink(os.path.basename(BIV) + '.' + ext, f'{out}.{ext}')
    with open(out + '.lon', 'w') as fh:
        fh.write('2\n')
        np.savetxt(fh, np.hstack([f, s]), fmt='%.5f')

    # comparison with the cohort's own fibres (axial: 0-90 deg)
    lon0 = read_lon(BIV)
    f0 = unit(lon0[:, :3])
    ang = np.degrees(np.arccos(np.clip(np.abs(np.sum(f * f0, 1)), 0, 1)))
    ot = w < 0.5
    nanfrac = float(np.isnan(f).any(1).mean())
    summ = {'elements': int(len(E)), 'nan_fraction': nanfrac,
            'ot_elements_w_lt_0.5': int(ot.sum()),
            'fibre_angle_vs_cohort_deg': {
                'all_median': float(np.nanmedian(ang)), 'all_mean': float(np.nanmean(ang)),
                'body_median': float(np.nanmedian(ang[~ot])), 'ot_median': float(np.nanmedian(ang[ot])),
                'frac_lt_20deg': float(np.nanmean(ang < 20))},
            'sheet_normal_vs_transmural_median_deg': float(np.nanmedian(np.degrees(np.arccos(np.clip(
                np.abs(np.sum(np.cross(f, s) * unit(g['phi_epi']), 1)), 0, 1)))[pepi > 0.2]))}
    with open(os.path.join(OUT, 'summary_04.json'), 'w') as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
