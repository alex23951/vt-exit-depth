"""v5.2 step 6 (LOCK.md 11.4 item 3): the Niederer 2011 N-version benchmark, once, on this openCARP.

Niederer et al. 2011 (Phil Trans R Soc A 369:4331; project library niederer2011.pdf), tables 1-3 as the paper states them:
3 x 7 x 20 mm slab, fibres along the 20 mm axis, transversely isotropic monodomain; ten Tusscher & Panfilov 2006 epicardial
cell (openCARP tenTusscherPanfilov, flags EPI) from the paper's Table 2 initial state; stimulus 2 ms at 50 000 uA/cm^3 on a
1.5 x 1.5 x 1.5 mm cube at one corner; surface-to-volume 140 mm^-1 (0.14 um^-1); Cm 1 uF/cm^2 (openCARP's); sigma_i 0.17 /
0.019, sigma_e 0.62 / 0.24 S/m (monodomain sigma = sigma_i sigma_e / (sigma_i + sigma_e)); zero-flux boundaries;
dx 0.1 mm, dt 0.005 ms; activation time = first upward crossing of 0 mV (the paper's metric).
Acceptance (11.4 item 3): the last activation inside the published across-code range 37.8-48.7 ms; where it sits against
the 42.5-43 ms gold standard is reported. Stop rule: outside the range, stop and report before any gate-9 beat.
Mesh: openCARP mesher, tets, 0.1 mm (x = fibre axis 20 mm, y 7 mm, z 3 mm).
Writes niederer52.json here; runs under runs/v52_2026-10-20/06_mono/niederer/.
Usage (repo root, venv, PATH with openCARP's mpiexec): python -B analysis/v52_2026-10-20/06_mono/niederer52.py
"""
import json
import os
import subprocess
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '06_mono', 'niederer')
NP = int(os.environ.get('MONO_NP', '6'))
TEND = 80.0
TABLE2 = {   # Niederer 2011 Table 2 (membrane potential -85.23 mV; the text layer drops the minus sign)
    'Vm': -85.23, 'Xr1': 0.00621, 'Xr2': 0.4712, 'Xs': 0.0095, 'M': 0.00172, 'H': 0.7444, 'J': 0.7045, 'D': 3.373e-5,
    'F': 0.7888, 'F2': 0.9755, 'FCaSS': 0.9953, 'S': 0.999998, 'R': 2.42e-8, 'Cai': 0.000126, 'CaSR': 3.64, 'CaSS': 0.00036,
    'R_': 0.9073, 'Nai': 8.604, 'Ki': 136.89}


def sh(cmd, log, cwd=None):
    with open(log, 'w') as f:
        subprocess.run([str(c) for c in cmd], stdout=f, stderr=subprocess.STDOUT, check=True, cwd=cwd)


def main():
    os.makedirs(RUN, exist_ok=True)
    t0 = time.time()
    mesh = os.path.join(RUN, 'slab')
    sh(['mesher', '-size[0]', 2.0, '-size[1]', 0.7, '-size[2]', 0.3, '-resolution[0]', 100, '-resolution[1]', 100, '-resolution[2]', 100,
        '-Elem3D', 0, '-mesh', mesh], os.path.join(RUN, 'mesher.log'))
    P = np.loadtxt(mesh + '.pts', skiprows=1) / 1e3                                              # mm
    lon = np.loadtxt(mesh + '.lon', skiprows=1, max_rows=5)
    lo, hi = P.min(0), P.max(0)
    rec = {'nodes': int(len(P)), 'extent_mm': (hi - lo).round(4).tolist(), 'lon_first_rows': lon.tolist()}
    assert np.allclose(hi - lo, [20.0, 7.0, 3.0], atol=1e-3), rec
    assert np.allclose(np.atleast_2d(lon)[:, :3], [1, 0, 0]), 'fibres not along the 20 mm axis'
    stim = np.where(np.all(P - lo <= 1.5 + 1e-6, axis=1))[0]
    with open(os.path.join(RUN, 'stim.vtx'), 'w') as f:
        f.write(f'{len(stim)}\nintra\n'); np.savetxt(f, stim, fmt='%d')
    # initial state: bench's EPI state file at t = 0 with Table 2's values put in by name
    sv = os.path.join(RUN, 'tnnp_epi_default.sv')
    sh(['bench', '--imp=tenTusscherPanfilov', '--imp-par=flags=EPI', '--duration=0', f'--save-ini-file={sv}', '--save-ini-time=0'],
       os.path.join(RUN, 'bench_sv.log'), cwd=RUN)
    out, seen = [], set()
    for l in open(sv):
        p = l.rstrip('\n').split('#')
        name = p[1].strip() if len(p) == 2 else None
        if name in TABLE2:
            out.append(f'{TABLE2[name]:<20.10g}# {name}'); seen.add(name)
        else:
            out.append(l.rstrip('\n'))
    assert seen == set(TABLE2), set(TABLE2) - seen
    svt = os.path.join(RUN, 'tnnp_epi_table2.sv')
    open(svt, 'w').write('\n'.join(out) + '\n')
    cmd = ['mpiexec', '-n', NP, 'openCARP', '-meshname', mesh, '-simID', os.path.join(RUN, 'sim'), '-bidomain', 0, '-dt', 5.0,
           '-parab_solve', 1, '-tend', TEND, '-spacedt', TEND, '-timedt', 5.0,
           '-num_imp_regions', 1, '-imp_region[0].im', 'tenTusscherPanfilov', '-imp_region[0].im_param', 'flags=EPI',
           '-imp_region[0].im_sv_init', svt, '-imp_region[0].cellSurfVolRatio', 0.14,
           '-num_gregions', 1, '-gregion[0].g_il', 0.17, '-gregion[0].g_it', 0.019, '-gregion[0].g_in', 0.019,
           '-gregion[0].g_el', 0.62, '-gregion[0].g_et', 0.24, '-gregion[0].g_en', 0.24,
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(RUN, 'stim'), '-stim[0].ptcl.start', 0.0,
           '-stim[0].pulse.strength', 50000.0, '-stim[0].ptcl.duration', 2.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0, '-lats[0].threshold', 0.0, '-lats[0].method', 1]
    t1 = time.time()
    sh(['/usr/bin/time', '-v'] + cmd, os.path.join(RUN, 'openCARP.log'))
    act = np.loadtxt(os.path.join(RUN, 'sim', 'init_acts_LATs-thresh.dat'))
    far = int(np.argmax(np.linalg.norm(P - lo, axis=1)))
    last = float(act.max())
    rec.update({'stim_nodes': int(len(stim)), 'np': NP, 'dt_ms': 0.005, 'dx_mm': 0.1, 'tend_ms': TEND,
                'unactivated_nodes': int((act < 0).sum()), 'last_activation_ms': round(last, 3),
                'activation_at_far_corner_ms': round(float(act[far]), 3),
                'accept_37.8_48.7': bool(37.8 <= last <= 48.7 and (act >= 0).all()),
                'vs_gold_standard_42.5_43_ms': round(last - 42.75, 3),
                'wall_s_sim': round(time.time() - t1, 1), 'wall_s_total': round(time.time() - t0, 1)})
    json.dump(rec, open(os.path.join(HERE, 'niederer52.json'), 'w'), indent=1)
    print(json.dumps(rec, indent=1))
    if not rec['accept_37.8_48.7']:
        raise SystemExit('Niederer benchmark outside 37.8-48.7 ms: stop and report before any gate-9 beat (11.4 item 3)')


if __name__ == '__main__':
    main()
