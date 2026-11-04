"""D44 (b) (lock thread 3 Nov 2026, pc-note-d42 section 3 (b)): RE+ plane waves on step 6's flat block, per heart type,
before the first of the 27 RE+ beats. Report only; nothing here is tuned or changes a value.

Block: step 6's slab (runs/v52_2026-10-20/06_mono/slab/slab: 36 x 36 x 20 mm, jittered tets, edges about 1 mm like the
hearts; fibre x, sheet y, normal z). Settings as the 27-site RE+ beats (t1_27.command): dream.solve 1 on the whole block,
dream.fim.tol 0.001, dream.vel = params/v52_speeds.json (mm/s), (a)'s fix-2 tensor (params/v52_conductivities.json,
harmonic mean as built), FOOT with A_F 0.91 mV and the heart type's fitted tau_F (params/v52_re_foot.json; D45 / D48),
CVrest at openCARP's defaults, dt 10 us, one process. Cells: step 6's block cells, the built-in Tomek at its defaults (the
note's "step 6's block cells"; = Tomek52w at w = 0 with unit factors, blend52 identity check). One planar wave per axis
as step 6 (nodes within 1.2 mm of the low face, 400 uA/cm3 x 1 ms at t = 0; tend by step 6's rule).
Reported: (1) achieved CV per axis from Vm activation times (openCARP LAT at -10 mV, as step 6: 1 / slope of LAT on the
coordinate over x, y 6-24 mm or z 5-15 mm, nodes >= 4 mm from the lateral faces, 1 mm bin medians) against dream.vel;
(2) Vm activation time minus eikonal time (act.igb, the FIM solve at t = 0) over the block's nodes: minimum / median /
maximum, both signs (all nodes, and nodes outside the stimulus layer); (3) the maximum upstroke rate: dVm/dt per solver
step at 21 traced nodes on the axis's centre line inside the measuring range (tracedt = dt); max and median of the
per-node maxima; (4) whether CVrest and Idiff act with dream.solve = 1 (source reading, ffce195).
Writes flatre52.json (this folder); runs under runs/v52_2026-10-20/11_engine/flatre/.
Usage (repo root, venv, PATH): python -B .../flatre52.py
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLAB = os.path.join(REPO, 'runs', 'v52_2026-10-20', '06_mono', 'slab', 'slab')
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', 'flatre')
OUT = os.path.join(HERE, 'flatre52.json')
AXES = (('fibre', 'l'), ('sheet', 't'), ('normal', 'n'))
DIMS = (36.0, 36.0, 20.0)
SETS = {'control': 'Y5HYEDL4', 'HF': '6G8DD8S5'}
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts']
FIX2 = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts']
FOOT = json.load(open(os.path.join(REPO, 'params', 'v52_re_foot.json')))['hearts']
SOURCE_READING = {
    'Idiff': 'acts: with dream.solve 1 (REp) every step runs the ionics, then the foot current A_F / tau_F exp(dT / tau_F) for TA <= t <= TA + 5 ms '
             'while Vm < V_th is added as Vm += Idiff dt, then the parabolic solve (electrics_eikonal.cc solve_RD, compute_diffusion_current)',
    'CVrest': 'does not act: solve_RE runs the FIM once at t = 0 and T_R starts at -400 ms and is updated only for DREAM (solve 3), so the '
              'restitution factor returns 1 (early exit on T_R + delay == -400); defaults rho / kappa / theta / psi left as openCARP sets them',
}


def igb(f):
    hd = open(f, 'rb').read(1024).decode('latin1')
    x = int(hd.split('x:')[1].split()[0])
    return np.memmap(f, dtype='<f4', mode='r', offset=1024).reshape(-1, x)


def run_axis(job):
    s, ai, P = job
    h = SETS[s]; a, k_ = AXES[ai]
    v = SPEEDS[h][a]
    lo, hi = (6.0, 24.0) if ai < 2 else (5.0, 15.0)
    tend = float(np.ceil((hi + 2.0) / v * 1.15 + 6.0))
    d = os.path.join(RUN, f'{s}_{a}' + os.environ.get('FLAT_SUFFIX', '')); os.makedirs(d, exist_ok=True)
    stim = np.where(P[:, ai] < 1.2)[0]
    with open(os.path.join(d, 'stim.vtx'), 'w') as fh:
        fh.write(f'{len(stim)}\nintra\n'); np.savetxt(fh, stim, fmt='%d')
    others = [k for k in range(3) if k != ai]
    centre = np.array([DIMS[k] / 2 for k in range(3)])
    tr = []
    for x in np.linspace(lo, hi, 21):
        q = centre.copy(); q[ai] = x
        tr.append(int(np.argmin(np.sum((P - q) ** 2, axis=1))))
    tr = list(dict.fromkeys(tr))
    foot = FOOT[h]
    cmd = ['openCARP', '-meshname', SLAB, '-simID', d, '-bidomain', 0, '-dt', 10.0, '-parab_solve', 1, '-tend', tend,
           '-spacedt', 1.0, '-timedt', 5.0, '-dream.solve', 1, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', int(os.environ.get('FIM_MAX_ITER', '1000000000')),
           '-num_phys_regions', 1, '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', 1, '-phys_region[0].ID[0]', 1,
           '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek', '-imp_region[0].num_IDs', 1, '-imp_region[0].ID[0]', 1]
    cmd += sum(([f'-imp_region[0].dream.Idiff.{k}', foot[k]] for k in ('model', 'A_F', 'tau_F', 'V_th')), [])
    cmd += ['-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'), '-stim[0].pulse.strength', 400.0,
            '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1, '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0,
            '-lats[0].measurand', 0, '-lats[0].threshold', -10, '-lats[0].method', 1,
            '-num_gregions', 1, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1]
    for ax, k in AXES:
        g = FIX2[h]['sigma_S_m'][ax]
        cmd += [f'-gregion[0].g_i{k}', g['gi'], f'-gregion[0].g_e{k}', g['ge'], f'-gregion[0].dream.vel_{k}', 1000.0 * SPEEDS[h][ax]]
    cmd += ['-num_trace', len(tr)] + sum(([f'-trace_node[{i}]', n] for i, n in enumerate(tr)), []) + ['-tracedt', 0.01]
    t0 = time.time()
    with open(os.path.join(d, 'run.log'), 'w') as log:
        r = subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, cwd=d, env=dict(os.environ, OMP_NUM_THREADS='1'))
    wall = round(time.time() - t0, 1)
    if r.returncode:
        return s, a, {'exit': r.returncode, 'wall_s': wall}
    act = np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat'))
    eik = np.asarray(igb(os.path.join(d, 'act.igb'))[0], np.float64)
    inner = np.all([(P[:, k] >= 4.0) & (P[:, k] <= DIMS[k] - 4.0) for k in others], axis=0)
    rng = inner & (P[:, ai] >= lo) & (P[:, ai] <= hi)
    sel = rng & (act >= 0)
    cen, tb = [], []
    for b in np.arange(lo, hi, 1.0):
        m = sel & (P[:, ai] >= b) & (P[:, ai] < b + 1)
        if m.sum() >= 5:
            cen.append(np.median(P[m, ai])); tb.append(np.median(act[m]))
    cv = float(1 / np.polyfit(cen, tb, 1)[0]) if len(cen) >= 3 else float('nan')
    both = (act >= 0) & np.isfinite(eik) & (eik >= 0) & (eik < 1e6)
    out_stim = both.copy(); out_stim[stim] = False
    dd = act - eik
    def mmm(m):
        return {'n': int(m.sum()), 'min_ms': float(dd[m].min()), 'median_ms': float(np.median(dd[m])), 'max_ms': float(dd[m].max())}
    ups = []
    hdr = open(os.path.join(d, 'Tomek_trace_header.txt')).read().split()
    iv = 1 + hdr.index('V')                                                                   # column 0 is time
    for f in sorted(x for x in os.listdir(d) if x.startswith('Trace_') and x.endswith('.dat')):
        x = np.loadtxt(os.path.join(d, f))
        assert np.allclose(np.diff(x[:, 0]), 0.01, atol=1e-6)
        ups.append(float(np.max(np.diff(x[:, iv]) / 0.01)))
    return s, a, {'exit': 0, 'wall_s': wall, 'tend_ms': tend, 'nodes': int(len(P)), 'stimulus_nodes': int(len(stim)),
                  'dream_vel_m_s': v, 'cv_vm_m_s': cv, 'cv_ratio_to_dream_vel': cv / v, 'bins': len(cen), 'unactivated_in_range': int((rng & (act < 0)).sum()),
                  'unactivated_block': int((act < 0).sum()), 'vm_act_minus_eikonal_all': mmm(both), 'vm_act_minus_eikonal_outside_stimulus': mmm(out_stim),
                  'traced_nodes': len(ups), 'max_upstroke_mV_per_ms': max(ups) if ups else None,
                  'median_of_node_max_upstroke_mV_per_ms': float(np.median(ups)) if ups else None,
                  's_per_sim_ms': round(wall / tend, 2)}


def main():
    P = np.loadtxt(SLAB + '.pts', skiprows=1) / 1000.0
    jobs = [(s, ai, P) for s in SETS for ai in range(3)]
    rec = {'block': os.path.relpath(SLAB, REPO), 'source_reading_ffce195': SOURCE_READING, 'foot': {s: FOOT[h] for s, h in SETS.items()},
           'cells': 'built-in Tomek, defaults (step 6 block cells)', 'runs': {}}
    with ThreadPoolExecutor(int(os.environ.get('FLAT_LANES', '3'))) as ex:
        for s, a, r in ex.map(run_axis, jobs):
            rec['runs'].setdefault(s, {})[a] = r
            print(s, a, {k: r.get(k) for k in ('exit', 'cv_vm_m_s', 'cv_ratio_to_dream_vel', 'max_upstroke_mV_per_ms', 'wall_s')}, flush=True)
            json.dump(rec, open(OUT, 'w'), indent=1)
    json.dump(rec, open(OUT, 'w'), indent=1)


def diagnostic(s, a, max_iter):
    """One axis again with the FIM capped (diagnostic only; the 27 beats keep max_iter 1e9)."""
    os.environ['FIM_MAX_ITER'] = str(max_iter); os.environ['FLAT_SUFFIX'] = f'_fim{max_iter}'
    P = np.loadtxt(SLAB + '.pts', skiprows=1) / 1000.0
    _, _, r = run_axis((s, [x[0] for x in AXES].index(a), P))
    rec = json.load(open(OUT)); rec.setdefault('diagnostic', {})[f'{s}_{a}_fim_max_iter_{max_iter}'] = r
    json.dump(rec, open(OUT, 'w'), indent=1)
    print(json.dumps(r, indent=1))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'diagnostic':
        diagnostic(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        main()
