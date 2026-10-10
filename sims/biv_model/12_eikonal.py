#!/usr/bin/env python
"""
Step 12: eikonal-family activation for one site, plus a lead-field ECG.

Modes
  eik : pure eikonal (-dream.solve 0) -> activation times; a pseudo-Vm is built from a
        template action potential shifted to each node's activation time
        (template: --template-run monodomain Vm at one node, aligned at its -10 mV crossing),
        then projected with saved lead fields (openCARP experiment 4).
  re- : reaction-eikonal without diffusion (-dream.solve 2), Tomek; Vm comes from the run.
Eikonal speeds are EFFECTIVE speeds (frozen targets): fibre 0.6, sheet 0.4, sheet-normal
0.48 m/s (12.6 ms over the outer 6 mm), fast layer 2.0 m/s isotropic. Conductivities (RE-)
from the heart's calibration.json.

Usage: python 12_eikonal.py --mode eik|re- --ID <run> --tend 140 [--site-node N] [--lf-dir D]
"""

import argparse
import json
import os
import struct
import subprocess
import time

import numpy as np

from common import HEART, OUT, REPO, read_pts, read_vtx, write_vtx

MESH = os.path.join(OUT, 'bivF')
V = {'f': 600.0, 's': 400.0, 'n': 480.0, 'fast': 2000.0}   # mm/s (openCARP dream units) = 0.6 / 0.4 / 0.48 / 2.0 m/s effective


def igb_read(f):
    b = open(f, 'rb').read()
    h = b[:1024].decode('latin1')
    x = int(h.split('x:')[1].split()[0])
    return h, np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def igb_write(f, data, dt, template_header):
    """Write Vm frames using an existing openCARP IGB header (same node count, frame count
    and time step), so openCARP's reader accepts it exactly."""
    nt, nx = data.shape
    h = template_header
    if f'x:{nx} ' not in h.decode('latin1') or f't:{nt} ' not in h.decode('latin1'):
        raise ValueError('template header does not match data shape')
    with open(f, 'wb') as fh:
        fh.write(h)
        fh.write(np.ascontiguousarray(data, dtype='<f4').tobytes())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['eik', 're-'], required=True)
    p.add_argument('--ID', required=True)
    p.add_argument('--tend', type=float, default=140.0)
    p.add_argument('--site-node', type=int, default=None)
    p.add_argument('--np', type=int, default=6)
    p.add_argument('--template-run', default=None,
                   help="monodomain run of the same heart (Vm every 1 ms); default: that heart's full-QRS run")
    p.add_argument('--mesh-variant', choices=['normal', 'lbbb'], default='normal')
    p.add_argument('--weights', default=None, help='ECG weight file (13_fast_ecg.py); ECG computed in memory, no Vm file')
    p.add_argument('--ecg-dir', default=None, help='with --weights: where ECG_*.dat are written')
    p.add_argument('--no-fast-layer', action='store_true', help='fast layer gets myocardial speeds/conductivities')
    p.add_argument('--stim-json', default=None,
                   help='extra timed stimuli (14_purkinje.py): JSON list of {"vtx": file without .vtx, "start": ms}; eik mode only')
    p.add_argument('--no-site-stim', action='store_true', help='no site stimulus (His-driven beat: --stim-json only)')
    a = p.parse_args()
    global MESH
    if a.mesh_variant == 'lbbb':
        MESH = os.path.join(OUT, 'bivF_lbbb')
    if a.template_run is None:
        a.template_run = os.path.join(REPO, 'runs', '2026-10-02_biv_fullqrs' if HEART == 'Y5HYEDL4'
                                      else f'2026-10-03_{HEART}_fullqrs')
    run = os.path.join(REPO, 'runs', a.ID)
    os.makedirs(run, exist_ok=True)
    cal = json.load(open(os.path.join(OUT, 'calibration.json')))
    pts = read_pts(MESH)
    if a.site_node is None:
        a.site_node = json.load(open(os.path.join(a.template_run, 'summary_06.json')))['site_node']
    stim = np.where(np.linalg.norm(pts - pts[a.site_node], axis=1) < 1500)[0]
    write_vtx(os.path.join(run, 'stim.vtx'), stim)
    stims = [] if a.no_site_stim else [(os.path.join(run, 'stim'), 0.0)]
    if a.stim_json:                                     # 2026-10-07: Purkinje junction stimuli
        stims += [(x['vtx'], float(x['start'])) for x in json.load(open(a.stim_json))]
    stim_opts = ['-num_stim', len(stims)]
    for i, (vf, t0s) in enumerate(stims):
        stim_opts += [f'-stim[{i}].elec.vtx_file', vf, f'-stim[{i}].ptcl.start', t0s]

    gf = (cal['fibre']['gi'], cal['fibre']['ge']); gs = (cal['sheet']['gi'], cal['sheet']['ge'])
    gn = (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])
    gk = (cal['fast_layer']['2.0']['gi'], cal['fast_layer']['2.0']['ge'])
    vfast = V['fast']
    if a.no_fast_layer:
        vfast, gk = None, None
    g = ['-num_gregions', 2, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', gf[0], '-gregion[0].g_el', gf[1], '-gregion[0].g_it', gs[0], '-gregion[0].g_et', gs[1],
         '-gregion[0].g_in', gn[0], '-gregion[0].g_en', gn[1],
         '-gregion[0].dream.vel_l', V['f'], '-gregion[0].dream.vel_t', V['s'], '-gregion[0].dream.vel_n', V['n'],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2]
    if gk is None:          # no fast layer: tag 2 behaves as myocardium
        g += ['-gregion[1].g_il', gf[0], '-gregion[1].g_el', gf[1], '-gregion[1].g_it', gs[0], '-gregion[1].g_et', gs[1],
              '-gregion[1].g_in', gn[0], '-gregion[1].g_en', gn[1],
              '-gregion[1].dream.vel_l', V['f'], '-gregion[1].dream.vel_t', V['s'], '-gregion[1].dream.vel_n', V['n']]
    else:
        for k in ('l', 't', 'n'):
            g += [f'-gregion[1].g_i{k}', gk[0], f'-gregion[1].g_e{k}', gk[1], f'-gregion[1].dream.vel_{k}', vfast]
    if a.mode == 'eik':
        # pure eikonal: Eikonal physics region (ptype 2), no ionic model, activation times only
        # DREAM/eikonal physics do not support MPI: one process, OpenMP threads
        os.environ['OMP_NUM_THREADS'] = str(a.np)
        cmd = ['openCARP', '-meshname', MESH, '-simID', run,
               '-dream.solve', 0, '-dream.fim.tol', float(os.environ.get('EIK_FIM_TOL', '0.001')), '-dream.fim.max_iter', 1000000000,
               '-num_phys_regions', 1, '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', 2,
               '-phys_region[0].ID[0]', 1, '-phys_region[0].ID[1]', 2,
               ] + (['-tend', 1000.0] if a.stim_json else []) + stim_opts + g
    else:
        cmd = ['mpiexec', '-n', a.np, 'openCARP', '-meshname', MESH, '-simID', run,
               '-bidomain', 0, '-dt', 10, '-parab_solve', 1, '-tend', a.tend, '-spacedt', 1.0, '-timedt', 5.0,
               '-dream.solve', 2, '-dream.fim.max_iter', 1000000000,
               '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
               '-num_stim', 1, '-stim[0].elec.vtx_file', os.path.join(run, 'stim'), '-stim[0].ptcl.start', 0.0,
               '-stim[0].crct.type', 0, '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0] + g
    t0 = time.time()
    with open(os.path.join(run, 'openCARP.log'), 'w') as log:   # EIK_TIMEOUT_S: some timed-stimulus runs never converged (8 Oct)
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True,
                       timeout=float(os.environ['EIK_TIMEOUT_S']) if os.environ.get('EIK_TIMEOUT_S') else None)
    t_sim = time.time() - t0
    res = {'heart': HEART, 'mode': a.mode, 'site_node': a.site_node, 'tend_ms': a.tend, 'mesh_variant': a.mesh_variant,
           'no_fast_layer': a.no_fast_layer, 'sim_wall_s': round(t_sim, 1), 'files': sorted(os.listdir(run))}
    if a.mode == 'eik':
        t1 = time.time()
        _, act = igb_read(os.path.join(run, 'act.igb'))
        act = act[-1].astype(float)
        res['total_activation_ms'] = float(act.max())
        res['unactivated'] = int((act < 0).sum())
        # template AP: monodomain Vm (1 ms frames) at the node whose LAT is closest to 60 ms
        _, vm0 = igb_read(os.path.join(a.template_run, 'vm.igb'))
        lat0 = np.loadtxt(os.path.join(a.template_run, 'init_acts_LATs-thresh.dat'))
        k = int(np.argmin(np.abs(lat0 - 60)))
        tt = np.arange(vm0.shape[0], dtype=float)
        tmpl_t = tt - lat0[k]
        tmpl_v = vm0[:, k].astype(float)
        if a.tend <= 0:      # auto: cover the activation + 20 ms, in 10 ms steps, 140-990 ms
            a.tend = float(min(990, max(140, np.ceil((act.max() + 20) / 10) * 10)))
            res['tend_ms'] = a.tend
        t = np.arange(0, a.tend + 0.5, 1.0)
        if a.weights:
            # ECG = W @ Vm(t), with the pseudo-Vm built in node chunks (no Vm file written)
            W = np.load(a.weights)['W'].astype(float)
            ecg = np.zeros((len(t), W.shape[0]))
            for i0 in range(0, len(act), 50000):
                sl = slice(i0, i0 + 50000)
                rel = t[:, None] - act[None, sl]
                pvc = np.interp(rel.ravel(), tmpl_t, tmpl_v, left=tmpl_v[0], right=tmpl_v[-1]).reshape(rel.shape)
                ecg += pvc @ W[:, sl].T
            os.makedirs(a.ecg_dir, exist_ok=True)
            for j, l in enumerate(['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']):
                np.savetxt(os.path.join(a.ecg_dir, f'ECG_{l}.dat'), np.c_[t, ecg[:, j]], fmt='%g %.6g')
            res['pseudo_vm_s'] = round(time.time() - t1, 1)
            res['template_node'] = k
            res['ecg_dir'] = a.ecg_dir
            with open(os.path.join(run, 'summary_12.json'), 'w') as fh:
                json.dump(res, fh, indent=1)
            print(json.dumps(res, indent=1))
            return
        rel = t[:, None] - act[None, :]
        pv = np.interp(rel.ravel(), tmpl_t, tmpl_v, left=tmpl_v[0], right=tmpl_v[-1]).reshape(rel.shape)
        hdr = open(os.path.join(a.template_run, 'vm.igb'), 'rb').read(1024).decode('latin1')
        # same header, frame count / duration patched in place (keep 3-digit values so the
        # header layout and length are unchanged)
        nt = pv.shape[0]
        t0 = int(hdr.split(' t:')[1].split()[0]); d0 = hdr.split('dim_t:')[1].split()[0]
        if len(str(nt)) != len(str(t0)) or len(str(nt - 1)) != len(d0):
            raise ValueError('frame count must keep the template digit count (101-999 frames)')
        hdr = hdr.replace(f' t:{t0} ', f' t:{nt} ', 1).replace(f'dim_t:{d0} ', f'dim_t:{nt - 1} ', 1).encode('latin1')
        res['frames'] = nt
        igb_write(os.path.join(run, 'vm_pseudo.igb'), pv, 1.0, hdr)
        res['pseudo_vm_s'] = round(time.time() - t1, 1)
        res['template_node'] = k
    with open(os.path.join(run, 'summary_12.json'), 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
