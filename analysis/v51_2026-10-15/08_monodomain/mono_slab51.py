"""Monodomain conductivities for the intrinsic v5.1 speeds on a synthetic slab (27-site monodomain check, step 1, method 2).

Why (LABNOTES 18 Oct 2026, 2026-10-18_v51_08_monocal): the patch method (07_patch_tune) measures an apparent in-wall
cross-fibre speed in a wall with rotating fibres; it has a floor near 0.37 m/s, so 0.36 (control) is borderline and the
HF 0.26 m/s cannot be reached. The v5.1 graph solver was calibrated to intrinsic speeds on a synthetic slab (Alex, 17 Oct,
option 1); the monodomain conductivities are calibrated the same way, so both models share the intrinsic tissue speeds.

Slab: solver51.slab_mesh(seed 0): 36 x 36 x 20 mm jittered grid (h 0.85 mm), Delaunay, tets with an edge > 1.75 mm
dropped (edges mean ~1.03 mm, like the hearts); uniform fibres: fibre x, sheet y, normal z.
Tets are oriented positively. Numerics as mono51.py beats (monodomain, Tomek, dt 10 us, Crank-Nicolson, LAT -10 mV).
Measure: planar wave per direction (the nodes within 1.2 mm of the low face stimulated, 400 uA/cm3 x 1 ms); speed = 1 /
slope of LAT vs the coordinate over x, y 6-24 mm or z 5-15 mm, nodes >= 4 mm from the lateral faces, 1 mm bins (medians
of coordinate and LAT). gi and ge of a direction scaled together with ge / gi = 0.625 / 0.174 (as every heart
calibration.json). Start: control = the last patch round for Y5HYEDL4 (calibration_Y5HYEDL4.json round 4, so the first
slab round also shows the patch-vs-slab difference at equal conductivities); HF = the control result x (v_HF / v_ctrl)^2.
Each round corrects gi_a by (target / measured)^(1 / b) (b = 0.5, then fitted from the last two rounds), until all three
are within 1 %, at most 6 rounds. Speed sets: control 0.60 / 0.36 / 0.48 m/s (Y5HYEDL4); HF 0.60 / 0.26 / 0.336
(6G8DD8S5, 7D98EVAR).
Writes params/v51_mono_conductivities.json (per heart) and slab_calibration51.json here; runs under
runs/v51_2026-10-15/08_monodomain/slab/.
Usage (repo root, venv, PATH with openCARP's mpiexec): python -B analysis/v51_2026-10-15/08_monodomain/mono_slab51.py
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
import solver51 as S                                                   # noqa: E402

RUNS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'slab')
RATIO = 0.625 / 0.174
NP = 6
AXES = ('fibre', 'sheet', 'normal')
DIMS = (36.0, 36.0, 20.0)


def write_mesh(P, E):
    x0 = P[E[:, 0]]
    neg = np.einsum('ij,ij->i', P[E[:, 1]] - x0, np.cross(P[E[:, 2]] - x0, P[E[:, 3]] - x0)) < 0
    E = E.copy(); E[neg, 2], E[neg, 3] = E[neg, 3], E[neg, 2].copy()
    os.makedirs(RUNS, exist_ok=True)
    base = os.path.join(RUNS, 'slab')
    with open(base + '.pts', 'w') as f:
        f.write(f'{len(P)}\n'); np.savetxt(f, P * 1e3, fmt='%.3f')
    with open(base + '.elem', 'w') as f:
        f.write(f'{len(E)}\n'); np.savetxt(f, np.c_[E, np.ones(len(E), np.int64)], fmt='Tt %d %d %d %d %d')
    with open(base + '.lon', 'w') as f:
        f.write('2\n'); np.savetxt(f, np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1)), fmt='%.1f')
    return base


def run(mesh, label, g, stim, tend):
    d = os.path.join(RUNS, label)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'stim.vtx'), 'w') as fh:
        fh.write(f'{len(stim)}\nintra\n'); np.savetxt(fh, stim, fmt='%d')
    gr = ['-num_gregions', 1, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1]
    for k, a in zip(('l', 't', 'n'), AXES):
        gr += [f'-gregion[0].g_i{k}', g[a], f'-gregion[0].g_e{k}', g[a] * RATIO]
    cmd = ['mpiexec', '-n', NP, 'openCARP', '-meshname', mesh, '-simID', d, '-bidomain', 0, '-dt', 10, '-parab_solve', 1,
           '-tend', tend, '-spacedt', tend, '-timedt', 5.0, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'),
           '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
           '-lats[0].threshold', -10, '-lats[0].method', 1] + gr
    t0 = time.time()
    with open(os.path.join(d, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    return np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat')), round(time.time() - t0, 1)


def planar_speed(mesh, P, g, ai, v_target, tag):
    stim = np.where(P[:, ai] < 1.2)[0]
    lo, hi = (6.0, 24.0) if ai < 2 else (5.0, 15.0)
    tend = float(np.ceil((hi + 2.0) / v_target * 1.15 + 6.0))
    act, wall = run(mesh, f'{tag}_{AXES[ai]}', g, stim, tend)
    others = [k for k in range(3) if k != ai]
    inner = np.all([(P[:, k] >= 4.0) & (P[:, k] <= DIMS[k] - 4.0) for k in others], axis=0)
    rng = inner & (P[:, ai] >= lo) & (P[:, ai] <= hi)
    sel = rng & (act >= 0)
    cen, tb = [], []
    for b in np.arange(lo, hi, 1.0):
        m = sel & (P[:, ai] >= b) & (P[:, ai] < b + 1)
        if m.sum() >= 5:
            cen.append(np.median(P[m, ai])); tb.append(np.median(act[m]))
    v = float(1 / np.polyfit(cen, tb, 1)[0])
    return v, {'n': int(sel.sum()), 'bins': len(cen), 'wall_s': wall, 'tend_ms': tend, 'unactivated_in_range': int((rng & (act < 0)).sum())}


def calibrate(mesh, P, speeds, start, name):
    g = dict(start)
    hist = []
    for k in range(6):
        meas, info = {}, {}
        for ai, a in enumerate(AXES):
            meas[a], info[a] = planar_speed(mesh, P, g, ai, speeds[a], f'{name}_r{k}')
        ratio = {a: meas[a] / speeds[a] for a in AXES}
        hist.append({'round': k, 'gi': dict(g), 'measured_m_s': meas, 'ratio': ratio, 'runs': info})
        print(name, 'round', k, {a: round(r, 4) for a, r in ratio.items()}, {a: round(v, 4) for a, v in meas.items()}, flush=True)
        if all(abs(r - 1) <= 0.01 for r in ratio.values()):
            break
        new = {}
        for a in AXES:
            b = 0.5
            if len(hist) >= 2:
                g0, g1 = hist[-2]['gi'][a], hist[-1]['gi'][a]
                r0, r1 = hist[-2]['ratio'][a], hist[-1]['ratio'][a]
                if g0 != g1 and r0 > 0 and r1 > 0:
                    bb = np.log(r1 / r0) / np.log(g1 / g0)
                    b = float(bb) if 0.2 < bb < 1.2 else 0.5
            new[a] = g[a] * (1.0 / ratio[a]) ** (1 / b)
        g = new
    last = hist[-1]['ratio'].values()
    return {'speeds_m_s': speeds, 'within_1pct': bool(all(abs(r - 1) <= 0.01 for r in last)), 'within_3pct': bool(all(abs(r - 1) <= 0.03 for r in last)),
            'rounds': len(hist), 'gi': hist[-1]['gi'], 'history': hist}


def edge_mean(P, E):
    return float(np.mean([np.linalg.norm(P[E[:, a]] - P[E[:, b]], axis=1).mean() for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]))


def main():
    P, E, ed = S.slab_mesh(seed=0)
    mesh = write_mesh(P, E)
    pp = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'patch', 'Y5HYEDL4', 'patch51')
    patch_edge = edge_mean(np.loadtxt(pp + '.pts', skiprows=1) / 1e3, np.loadtxt(pp + '.elem', skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64))
    info = {'nodes': int(len(P)), 'tets': int(len(E)), 'edge_mean_mm': round(edge_mean(P, E), 3), 'edge_max_mm': round(float(ed.max()), 3),
            'heart_patch_edge_mean_mm_Y5HYEDL4': round(patch_edge, 3)}
    print('slab', info, flush=True)
    pr = json.load(open(os.path.join(HERE, 'calibration_Y5HYEDL4.json')))['history'][-1]
    out = {'slab': info, 'start_control': f"calibration_Y5HYEDL4.json round {pr['round']} (patch method)", 'sets': {}}
    sets = {'control': S.SPEEDS['Y5HYEDL4'], 'HF': S.SPEEDS['6G8DD8S5']}
    assert S.SPEEDS['6G8DD8S5'] == S.SPEEDS['7D98EVAR']
    start = {a: pr['g'][a][0] for a in AXES}
    for name, sp in sets.items():
        if name == 'HF':
            c = out['sets']['control']
            start = {a: c['gi'][a] * (sp[a] / c['speeds_m_s'][a]) ** 2 for a in AXES}
        out['sets'][name] = calibrate(mesh, P, sp, start, name)
        json.dump(out, open(os.path.join(HERE, 'slab_calibration51.json'), 'w'), indent=1)
    pf = os.path.join(REPO, 'params', 'v51_mono_conductivities.json')
    old = json.load(open(pf)) if os.path.exists(pf) else None
    par = {'method': 'monodomain conductivities calibrated to the intrinsic v5.1 speeds on a synthetic slab (mono_slab51.py, slab_calibration51.json); planar waves, target within 1 %',
           'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'slab': info, 'hearts': {},
           'superseded_patch_method': {'note': 'mono_cal51.py on the LV free-wall patch, Y5HYEDL4 only; the in-wall cross-fibre speed stayed at 0.373-0.378 m/s (target 0.36); not used', 'content': old}}
    for h in ('Y5HYEDL4', '6G8DD8S5', '7D98EVAR'):
        r = out['sets']['control' if h == 'Y5HYEDL4' else 'HF']
        par['hearts'][h] = {'speed_set': 'control' if h == 'Y5HYEDL4' else 'HF', 'speeds_m_s': r['speeds_m_s'], 'within_3pct': r['within_3pct'],
                            'within_1pct': r['within_1pct'], 'rounds': r['rounds'],
                            'conductivities_S_m': {a: {'gi': r['gi'][a], 'ge': r['gi'][a] * RATIO} for a in AXES},
                            'measured_m_s': r['history'][-1]['measured_m_s']}
    json.dump(par, open(pf, 'w'), indent=1)
    print(json.dumps({n: {k: v for k, v in r.items() if k != 'history'} for n, r in out['sets'].items()}, indent=1))


if __name__ == '__main__':
    main()
