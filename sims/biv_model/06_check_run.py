#!/usr/bin/env python
"""
Step 6: check run. Monodomain, Tomek, frozen 1 mm parameters, activation from one
LV endocardial point at mid-level (z ~ 0.5) on the LV free wall (opposite the septum).

Frozen 1 mm conductivities (gi / ge, S/m; LABNOTES 2026-10-02 PARAMETERS FROZEN):
  myocardium fibre 0.5606 / 2.0138, sheet 0.3368 / 1.2096, sheet-normal 0.3843 / 1.3805
  fast layer (tag 2, isotropic, measured 2.0 m/s) 4.6205 / 16.5972
Stimulus 400 uA/cm3 x 1 ms on nodes within 1.5 mm of the chosen point; dt 10 us;
LAT threshold -10 mV.

Usage (from repo root): python sims/biv_model/06_check_run.py --tend 160 --np 6 --ID <run id>
Output in runs/<ID>; summary in runs/<ID>/summary_06.json.
"""

import argparse
import json
import os
import subprocess

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra

from common import OUT, REPO, read_pts, read_vtx, write_vtx

MESH = os.path.join(OUT, 'bivF')
SURF = os.path.join(OUT, 'surfaces')
UVC = os.path.join(OUT, 'uvc')
G = {'f': (0.5606, 2.0138), 's': (0.3368, 1.2096), 'n': (0.3843, 1.3805), 'fast': (4.6205, 16.5972)}
_cal = os.path.join(OUT, 'calibration.json')
if os.path.exists(_cal):                     # per-heart calibration (07_patch_tune.py --auto) is the default
    _c = json.load(open(_cal))
    G['n'] = (_c['sheet_normal']['gi'], _c['sheet_normal']['ge'])
    G['fast'] = (_c['fast_layer']['2.0']['gi'], _c['fast_layer']['2.0']['ge'])
    G['f'] = (_c['fibre']['gi'], _c['fibre']['ge'])
    G['s'] = (_c['sheet']['gi'], _c['sheet']['ge'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tend', type=float, default=160.)
    p.add_argument('--np', type=int, default=6)
    p.add_argument('--ID', required=True)
    p.add_argument('--dt', type=float, default=10.)
    p.add_argument('--site-node', type=int, default=None, help='stimulus site (default: LV free wall, z 0.5)')
    p.add_argument('--mesh-variant', choices=['normal', 'lbbb'], default='normal')
    p.add_argument('--spacedt', type=float, default=5.0, help='Vm output interval [ms]')
    p.add_argument('--g-fast', type=float, nargs=2, default=None, help='override fast-layer gi ge')
    p.add_argument('--g-n', type=float, nargs=2, default=None, help='override sheet-normal gi ge')
    a = p.parse_args()
    if a.g_fast:
        G['fast'] = tuple(a.g_fast)
    if a.g_n:
        G['n'] = tuple(a.g_n)
    global MESH
    if a.mesh_variant == 'lbbb':
        MESH = os.path.join(OUT, 'bivF_lbbb')
    run = os.path.join(REPO, 'runs', a.ID)
    os.makedirs(run, exist_ok=True)

    pts = read_pts(MESH)
    z, phi, v = (np.loadtxt(os.path.join(UVC, n + '.dat')) for n in ('z', 'phi', 'v'))
    lv = read_vtx(os.path.join(SURF, 'lv_endo.vtx'))
    # LV free wall, mid-level: z closest to 0.5 and phi closest to pi (opposite septum)
    score = np.abs(z[lv] - 0.5) * 10 + (np.pi - np.abs(phi[lv]))
    site = int(lv[np.argmin(score)]) if a.site_node is None else int(a.site_node)
    stim_nodes = np.where(np.linalg.norm(pts - pts[site], axis=1) < 1500)[0]
    write_vtx(os.path.join(run, 'stim.vtx'), stim_nodes)

    g = ['-num_gregions', 2,
         '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', G['f'][0], '-gregion[0].g_el', G['f'][1],
         '-gregion[0].g_it', G['s'][0], '-gregion[0].g_et', G['s'][1],
         '-gregion[0].g_in', G['n'][0], '-gregion[0].g_en', G['n'][1],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', G['fast'][0], f'-gregion[1].g_e{k}', G['fast'][1]]
    cmd = ['mpiexec', '-n', a.np, 'openCARP', '-meshname', MESH, '-simID', run,
           '-bidomain', 0, '-dt', a.dt, '-parab_solve', 1, '-tend', a.tend,
           '-spacedt', min(a.spacedt, a.tend), '-timedt', min(5.0, a.tend),
           '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(run, 'stim'),
           '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
           '-lats[0].threshold', -10, '-lats[0].method', 1] + g
    with open(os.path.join(run, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)

    act = np.loadtxt(os.path.join(run, 'init_acts_LATs-thresh.dat'))
    E = np.loadtxt(MESH + '.elem', skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64)
    fast_nodes = np.zeros(len(pts), bool)
    fast_nodes[np.unique(E[E[:, 4] == 2, :4])] = True
    res = {'site_node': site, 'site_mm': (pts[site] / 1e3).round(2).tolist(),
           'site_z': float(z[site]), 'site_phi_deg': float(np.degrees(phi[site])),
           'stim_nodes': int(len(stim_nodes)), 'tend_ms': a.tend,
           'activated_fraction': float((act >= 0).mean())}
    if (act >= 0).mean() > 0.999:
        res['total_activation_ms'] = float(act.max())
    else:
        res['latest_activation_so_far_ms'] = float(act.max())

    # speed along the LV endocardium within the fast layer: geodesic distance on the
    # LV endocardial surface vs LAT, robust slope over 10-40 mm from the site
    tri = np.loadtxt(os.path.join(SURF, 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    ed = np.vstack([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [0, 2]]])
    w = np.linalg.norm(pts[ed[:, 0]] - pts[ed[:, 1]], axis=1) / 1e3
    A = sp.coo_matrix((w, (ed[:, 0], ed[:, 1])), shape=(len(pts), len(pts))).tocsr()
    dist = dijkstra(A, directed=False, indices=site)
    sel = np.isfinite(dist) & (dist > 10) & (dist < 40) & fast_nodes & (act >= 0)
    # straight-line distance (as in the wedge); surface-edge paths on this rough CT
    # endocardium are ~2x longer (2026-10-02_biv_check36 gave a spurious 4.0 m/s)
    eu = np.linalg.norm(pts - pts[site], axis=1) / 1e3
    lvm = np.zeros(len(pts), bool)
    lvm[lv] = True
    sel2 = lvm & fast_nodes & (act >= 0) & (eu >= 5) & (eu < 25)
    if sel2.sum() > 50:
        bins = np.arange(5, 25.01, 2.5)
        tb = [np.median(act[sel2 & (eu >= b0) & (eu < b0 + 2.5)]) for b0 in bins[:-1]]
        res['endo_speed_straightline_5_25mm_m_per_s'] = float(1 / np.polyfit(bins[:-1] + 1.25, tb, 1)[0])
    res['g_fast'] = list(G['fast'])
    res['g_n'] = list(G['n'])
    if sel.sum() > 50:
        # speed = median of distance increments per time over distance bins
        bins = np.arange(10, 41, 2.5)
        tb = [np.median(act[sel & (dist >= b0) & (dist < b0 + 2.5)]) for b0 in bins[:-1]]
        slope = np.polyfit(bins[:-1] + 1.25, tb, 1)[0]          # ms per mm
        res['endo_speed_surface_path_m_per_s_NOT_comparable'] = float(1 / slope)
        res['endo_speed_n_nodes'] = int(sel.sum())
    # transmural time on the LV free wall: epi node minus nearest LV endo node, mid z band
    epi = read_vtx(os.path.join(SURF, 'epi.vtx'))
    epi_fw = epi[(v[epi] == 0) & (np.abs(phi[epi]) > np.radians(90)) & (z[epi] > 0.3) & (z[epi] < 0.7)]
    from scipy.spatial import cKDTree
    tree = cKDTree(pts[lv])
    dd, ii = tree.query(pts[epi_fw])
    tt = act[epi_fw] - act[lv[ii]]
    # only wall within 20 mm (geodesic, along the endocardium) of the pacing site, so a
    # short run (< total activation) still gives complete endo -> epi pairs
    ok = (act[epi_fw] >= 0) & (act[lv[ii]] >= 0) & (dist[lv[ii]] < 20)
    res['transmural_pairs'] = int(ok.sum())
    res['lv_freewall_transmural_ms_median_p10_p90'] = np.percentile(tt[ok], [50, 10, 90]).round(2).tolist() if ok.any() else None
    res['lv_freewall_thickness_mm_median'] = float(np.median(dd[ok]) / 1e3) if ok.any() else None
    res['epi_breakthrough_first_ms'] = float(act[epi][act[epi] >= 0].min()) if (act[epi] >= 0).any() else None
    with open(os.path.join(run, 'summary_06.json'), 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
