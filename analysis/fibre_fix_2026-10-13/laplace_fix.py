#!/usr/bin/env python
"""
COPY of sims/biv_model/02_laplace.py for the exploratory fibre fix (13 Oct 2026, coordinator brief 00:15 UTC);
the frozen file is untouched. Changes: output to analysis/fibre_fix_2026-10-13/laplace; only three new problems:
  ot_rv        apex 0 -> PV rim + pulmonary-artery interface 1   (RV apico-outflow direction)
  ot_lv        apex 0 -> AV rim + aortic interface 1             (LV apico-outflow direction)
  phi_epi_fix  LV + RV endo 0 -> epi + aortic-root interface (minus endocardial nodes) 1
               (the septal infundibulum's outer side is the aortic-root interface, ao_iface)
Apex files are read, not rewritten. Original docstring follows.
Step 2: Laplace solves in openCARP (experiment 2) on the ventricular mesh.

Each problem fixes phi = 0 on one vertex set and phi = 1 on another (isotropic unit
conductivity, zero-flux elsewhere). Results: data/biv/<HEART>/laplace/<name>.dat (nodal).

Problems (surfaces from step 1; "base" = all valve rims + AV-plane / aortic / pulmonary
/ atrial interfaces, "apex" = all nodes within APEX_R mm of the epicardial LV apex point;
a single-node Dirichlet condition in 3D gives a degenerate field, ~1 everywhere):
  zeta     apex 0 -> base 1                      apex-to-base coordinate (UVC-style)
  basal    apex 0 -> MV, TV rims (+AV plane) 1  Doste 2019 apico-basal direction
  ot       apex 0 -> AV, PV rims (+Ao, PArt) 1  Doste 2019 apico-outflow direction
  w        AV, PV rims 0 -> apex, MV, TV 1        Doste 2019 intra-ventricular weight (0 = OT)
  phi_epi  LV+RV endo 0 -> epi 1                  Bayer 2012 / transmural coordinate
  phi_lv   RV endo + epi 0 -> LV endo 1           Bayer 2012
  phi_rv   LV endo + epi 0 -> RV endo 1           Bayer 2012
  v        LV endo 0 -> RV endo 1                 LV/RV coordinate
Where a node is in both sets, the "1" set wins (only rim-edge nodes).

Usage: python 02_laplace.py [--np 6] [--only name1,name2]
"""

import argparse
import json
import os
import subprocess

import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'sims', 'biv_model'))
from common import BIV, OUT, read_pts, read_vtx, write_vtx

SURF = os.path.join(OUT, 'surfaces')
APEX_R = 5.0   # mm
LAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'laplace')

BASE = ['mv_rim', 'tv_rim', 'av_rim', 'pv_rim', 'avplane_iface', 'ao_iface', 'part_iface', 'ra_iface']
PROBLEMS = {
    'zeta': (['APEX'], BASE),
    'basal': (['APEX'], ['mv_rim', 'tv_rim', 'avplane_iface', 'ra_iface']),
    'ot': (['APEX'], ['av_rim', 'pv_rim', 'ao_iface', 'part_iface']),
    'w': (['av_rim', 'pv_rim', 'ao_iface', 'part_iface'], ['APEX', 'mv_rim', 'tv_rim', 'avplane_iface', 'ra_iface']),
    'phi_epi': (['lv_endo', 'rv_endo'], ['epi']),
    'phi_lv': (['rv_endo', 'epi'], ['lv_endo']),
    'phi_rv': (['lv_endo', 'epi'], ['rv_endo']),
    'v': (['lv_endo'], ['rv_endo']),
}
PROBLEMS = {'ot_rv': (['APEX'], ['pv_rim', 'part_iface']), 'ot_lv': (['APEX'], ['av_rim', 'ao_iface']),
            'phi_epi_fix': (['lv_endo', 'rv_endo'], ['epi', 'AO_OUTER'])}


def find_apex():
    """LV apex: epicardial node farthest from the mitral-rim centroid along the LV long axis."""
    pts = read_pts(BIV)
    mv = pts[read_vtx(os.path.join(SURF, 'mv_rim.vtx'))].mean(0)
    lv = pts[read_vtx(os.path.join(SURF, 'lv_endo.vtx'))]
    # LV long axis: from MV centroid towards the LV endocardial point farthest from it
    far = lv[np.argmax(np.linalg.norm(lv - mv, axis=1))]
    axis = (far - mv) / np.linalg.norm(far - mv)
    epi = read_vtx(os.path.join(SURF, 'epi.vtx'))
    apex = epi[np.argmax((pts[epi] - mv) @ axis)]
    return int(apex), pts[apex], axis


def vset(names, apex):
    out = []
    for n in names:
        if n == 'AO_OUTER':
            endo = np.concatenate([read_vtx(os.path.join(SURF, k + '.vtx')) for k in ('lv_endo', 'rv_endo')])
            out.append(np.setdiff1d(read_vtx(os.path.join(SURF, 'ao_iface.vtx')), endo))
        elif n == 'APEX':
            out.append(read_vtx(os.path.join(SURF, 'apex_patch.vtx')))
        elif os.path.exists(os.path.join(SURF, n + '.vtx')):
            out.append(read_vtx(os.path.join(SURF, n + '.vtx')))
    return np.unique(np.concatenate(out))


def solve(name, zero, one, np_):
    zero = np.setdiff1d(zero, one)
    d = os.path.join(LAP, name)
    os.makedirs(d, exist_ok=True)
    write_vtx(os.path.join(d, 'bc0.vtx'), zero)
    write_vtx(os.path.join(d, 'bc1.vtx'), one)
    cmd = ['mpiexec', '-n', str(np_), 'openCARP',
           '-experiment', 2, '-bidomain', 1, '-meshname', BIV, '-simID', d,
           '-num_gregions', 1, '-gregion[0].num_IDs', 0,
           '-gregion[0].g_il', 1, '-gregion[0].g_it', 1, '-gregion[0].g_in', 1,
           '-gregion[0].g_el', 1, '-gregion[0].g_et', 1, '-gregion[0].g_en', 1,
           '-num_stim', 2,
           '-stim[0].crct.type', 3, '-stim[0].elec.vtx_file', os.path.join(d, 'bc0'),
           '-stim[1].crct.type', 2, '-stim[1].elec.vtx_file', os.path.join(d, 'bc1'),
           '-stim[1].pulse.strength', 1.0, '-stim[1].ptcl.duration', 1.0]
    with open(os.path.join(d, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run(['igbextract', '-o', 'ascii', '-O', os.path.join(LAP, name + '.dat'),
                    os.path.join(d, 'phie.igb')], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    x = np.loadtxt(os.path.join(LAP, name + '.dat'))
    if x.ndim > 1:                     # one row per time slice; keep the last
        x = x[-1]
        np.savetxt(os.path.join(LAP, name + '.dat'), x, fmt='%.6g')
    return x


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--np', type=int, default=6)
    a = p.parse_args()
    os.makedirs(LAP, exist_ok=True)
    summ = {}
    for n, (z, o) in PROBLEMS.items():
        z, o = vset(z, None), vset(o, None)
        x = solve(n, z, o, a.np)
        summ[n] = {'n_bc0': int(len(np.setdiff1d(z, o))), 'n_bc1': int(len(o)), 'min': float(x.min()), 'max': float(x.max())}
        print(n, summ[n], flush=True)
    json.dump(summ, open(os.path.join(LAP, 'summary_laplace_fix.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
