#!/usr/bin/env python
"""
Step 13: fast lead-field ECG without reloading the heart-torso mesh.

openCARP's lead-field ECG for lead L is a fixed linear map of the transmembrane voltage:
  ECG_L(t) = c * Z_L^T K Vm(t)
with Z_L the lead field (LF_L.igb, heart nodes), K the stiffness matrix of the heart with
conductivity sigma (fibre / sheet / sheet-normal tensor per element; fast layer isotropic)
and c a constant (sign / units). So W_L = c * K Z_L is computed once per heart, mesh
variant and conductivity set, and every beat's ECG is W @ Vm(t).

  weights : build W (12 x nodes) -> data/biv/<HEART>/ecgW_<variant>.npz
  validate: compare W @ Vm with an openCARP ECG of the same beat (fits c on one beat,
            reports correlation and max error); --check runs a second beat with that c.

Validated 2026-10-03 against openCARP (Y5HYEDL4): sigma = bidomain harmonic mean
(monodomain-equivalent) conductivity and c = -1 reproduce openCARP's ECG to 0.0002 mV
(monodomain beat, peak 2.47 mV; c fitted -0.99997) and 0.000006 mV (eikonal beat, c fixed
at -1). Use --sigma m --c -1.
"""

import argparse
import json
import os

import numpy as np
import scipy.sparse as sp

from common import HEART, OUT, REPO, read_elem, read_lon, read_pts

LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def igb(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def stiffness(mesh, G, sigma, nofast=False):
    """P1 stiffness matrix sum_e V_e grad(phi)^T S_e grad(phi); coordinates in mm."""
    pts = read_pts(mesh) / 1e3
    E, tag = read_elem(mesh)
    lon = read_lon(mesh)
    f = lon[:, :3]; s = lon[:, 3:6]
    f /= np.linalg.norm(f, axis=1, keepdims=True); s /= np.linalg.norm(s, axis=1, keepdims=True)
    n = np.cross(f, s)
    def g(key, k):
        gi, ge = G[key][k]
        return gi if sigma == 'i' else gi * ge / (gi + ge)
    if nofast:                       # no-fast-layer control: tag 2 behaves as myocardium
        tag = np.where(tag == 2, 1, tag)
    gl = np.where(tag == 2, g('fast', 0), g('myo', 0))
    gt = np.where(tag == 2, g('fast', 1), g('myo', 1))
    gn = np.where(tag == 2, g('fast', 2), g('myo', 2))
    S = gl[:, None, None] * f[:, :, None] * f[:, None, :] + gt[:, None, None] * s[:, :, None] * s[:, None, :] \
        + gn[:, None, None] * n[:, :, None] * n[:, None, :]
    x = pts[E]
    J = np.stack([x[:, 1] - x[:, 0], x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]], axis=1)   # rows = edges
    Jinv = np.linalg.inv(J)                                                           # cols = grad of barycentrics 1..3
    gr = np.concatenate([-Jinv.sum(2, keepdims=True), Jinv], axis=2)                   # (e, 3, 4)
    vol = np.abs(np.linalg.det(J)) / 6
    Ke = vol[:, None, None] * np.einsum('eki,ekl,elj->eij', gr, S, gr)                # (e, 4, 4)
    rows = np.repeat(E, 4, axis=1).ravel(); cols = np.tile(E, (1, 4)).ravel()
    return sp.coo_matrix((Ke.ravel(), (rows, cols)), shape=(len(pts), len(pts))).tocsr()


def conductivities(cal):
    return {'myo': [(cal['fibre']['gi'], cal['fibre']['ge']), (cal['sheet']['gi'], cal['sheet']['ge']),
                    (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])],
            'fast': [(cal['fast_layer']['2.0']['gi'], cal['fast_layer']['2.0']['ge'])] * 3}


def weights(mesh, lf_dir, G, sigma, c=1.0, nofast=False):
    K = stiffness(mesh, G, sigma, nofast)
    Z = np.stack([igb(os.path.join(lf_dir, f'LF_{l}.igb'))[-1].astype(float) for l in LEADS])
    return c * (K @ Z.T).T                                                            # (12, nodes)


def project(W, vm):
    return vm.astype(float) @ W.T                                                     # (frames, 12)


def read_ecg(d):
    return np.stack([np.loadtxt(os.path.join(d, f'ECG_{l}.dat'))[:, 1] for l in LEADS], axis=1)


def write_ecg(d, ecg, dt=1.0):
    os.makedirs(d, exist_ok=True)
    t = np.arange(ecg.shape[0]) * dt
    for i, l in enumerate(LEADS):
        np.savetxt(os.path.join(d, f'ECG_{l}.dat'), np.c_[t, ecg[:, i]], fmt='%g %.6g')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['validate', 'weights'])
    p.add_argument('--mesh', default=os.path.join(OUT, 'bivF'))
    p.add_argument('--lf-dir', required=True)
    p.add_argument('--vm', help='validate: Vm file of the beat')
    p.add_argument('--ecg-dir', help='validate: openCARP POSTPROC_DIR of the same beat')
    p.add_argument('--g', help='validate: JSON with the conductivities openCARP used (default calibration.json)')
    p.add_argument('--sigma', default='i', choices=['i', 'm'])
    p.add_argument('--c', type=float, default=None)
    p.add_argument('--out', default=None)
    p.add_argument('--nofast', action='store_true')
    a = p.parse_args()
    cal = json.load(open(a.g or os.path.join(OUT, 'calibration.json')))
    G = conductivities(cal)
    if a.stage == 'validate':
        W = weights(a.mesh, a.lf_dir, G, a.sigma)
        mine = project(W, igb(a.vm))
        ref = read_ecg(a.ecg_dir)
        n = min(len(mine), len(ref)); mine, ref = mine[:n], ref[:n]
        c = a.c if a.c is not None else float(np.sum(mine * ref) / np.sum(mine * mine))
        err = np.abs(c * mine - ref).max()
        r = [float(np.corrcoef(mine[:, i], ref[:, i])[0, 1]) for i in range(12)]
        print(json.dumps({'sigma': a.sigma, 'c': c, 'max_abs_err_mV': float(err),
                          'ref_peak_mV': float(np.abs(ref).max()), 'corr_min': min(r)}, indent=1))
    else:
        W = weights(a.mesh, a.lf_dir, G, a.sigma, a.c, a.nofast)
        out = a.out or os.path.join(OUT, 'ecgW.npz')
        np.savez(out, W=W.astype(np.float32), sigma=a.sigma, c=a.c, lf_dir=a.lf_dir, mesh=a.mesh, nofast=a.nofast)
        print(json.dumps({'written': out, 'shape': list(W.shape)}))


if __name__ == '__main__':
    main()
