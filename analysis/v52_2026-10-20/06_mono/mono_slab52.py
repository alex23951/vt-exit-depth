"""v5.2 step 6 (LOCK.md R4.4), first part: monodomain conductivities tuned on a flat block with straight fibres to the
v5.2 speeds, at the hearts' element size (the gate-9 ladder sizes 1.0 / 0.5 / 0.2 mm come later, with T2b).

Block and numerics as v5.1's flat-block tuning (mono_slab51.py, Alex 18 Oct 2026): solver51.slab_mesh(seed 0), 36 x 36 x
20 mm jittered grid (h 0.85 mm, edges ~1.03 mm like the hearts), fibre x, sheet y, normal z; openCARP monodomain, Tomek,
dt 10 us, LAT -10 mV; planar wave per axis (nodes within 1.2 mm of the low face, 400 uA/cm3 x 1 ms); speed = 1 / slope of
LAT against the coordinate over x, y 6-24 mm or z 5-15 mm, nodes >= 4 mm from the lateral faces, 1 mm bins.
v5.2 changes, from R4.4: targets params/v52_speeds.json (control 0.80 / 0.23 / 0.48 m/s; HF 0.80 / 0.167 / 0.336); the
sigma_i / sigma_e ratio held per axis at fix 2's values (params/v52_conductivities.json, R2.1-R2.2); acceptance within 3 %
on all three axes (iterated toward 1 %, at most 6 rounds, as v5.1); if 0.167 m/s cannot be reached or conduction blocks:
stop and report. Starting values only (R4.4 allows tuneCV for these; this uses v5.1's flat-block result instead): v5.1's
tuned bulk sigma per axis x (v5.2 speed / v5.1 speed)^2, split into sigma_i and sigma_e at the v5.2 ratio.
Writes params/v52_mono_conductivities.json (only if every set is within 3 %) and slab_mono52.json here; runs under
runs/v52_2026-10-20/06_mono/slab/.
Usage (repo root, venv, PATH with openCARP's mpiexec): python -B analysis/v52_2026-10-20/06_mono/mono_slab52.py
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

RUNS = os.path.join(REPO, 'runs', 'v52_2026-10-20', '06_mono', 'slab')
NP = int(os.environ.get('MONO_NP', '6'))
AXES = ('fibre', 'sheet', 'normal')
DIMS = (36.0, 36.0, 20.0)
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts']
FIX2 = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts']
V51 = json.load(open(os.path.join(REPO, 'params', 'v51_mono_conductivities.json')))['hearts']
SETS = {'control': 'Y5HYEDL4', 'HF': '6G8DD8S5'}                       # 7D98EVAR shares the HF set (asserted below)


def bulk(gi, ge):
    return gi * ge / (gi + ge)


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


def run(mesh, label, gi, ratio, stim, tend):
    d = os.path.join(RUNS, label)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'stim.vtx'), 'w') as fh:
        fh.write(f'{len(stim)}\nintra\n'); np.savetxt(fh, stim, fmt='%d')
    gr = ['-num_gregions', 1, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1]
    for k, a in zip(('l', 't', 'n'), AXES):
        gr += [f'-gregion[0].g_i{k}', gi[a], f'-gregion[0].g_e{k}', gi[a] * ratio[a]]
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


def planar_speed(mesh, P, gi, ratio, ai, v_target, tag):
    stim = np.where(P[:, ai] < 1.2)[0]
    lo, hi = (6.0, 24.0) if ai < 2 else (5.0, 15.0)
    tend = float(np.ceil((hi + 2.0) / v_target * 1.15 + 6.0))
    act, wall = run(mesh, f'{tag}_{AXES[ai]}', gi, ratio, stim, tend)
    others = [k for k in range(3) if k != ai]
    inner = np.all([(P[:, k] >= 4.0) & (P[:, k] <= DIMS[k] - 4.0) for k in others], axis=0)
    rng = inner & (P[:, ai] >= lo) & (P[:, ai] <= hi)
    sel = rng & (act >= 0)
    cen, tb = [], []
    for b in np.arange(lo, hi, 1.0):
        m = sel & (P[:, ai] >= b) & (P[:, ai] < b + 1)
        if m.sum() >= 5:
            cen.append(np.median(P[m, ai])); tb.append(np.median(act[m]))
    blocked = int((rng & (act < 0)).sum())
    v = float(1 / np.polyfit(cen, tb, 1)[0]) if len(cen) >= 3 else float('nan')
    return v, {'n': int(sel.sum()), 'bins': len(cen), 'wall_s': wall, 'tend_ms': tend, 'unactivated_in_range': blocked}


def calibrate(mesh, P, speeds, ratio, start, name):
    gi = dict(start)
    hist = []
    for k in range(6):
        meas, info = {}, {}
        for ai, a in enumerate(AXES):
            meas[a], info[a] = planar_speed(mesh, P, gi, ratio, ai, speeds[a], f'{name}_r{k}')
        ratio_v = {a: meas[a] / speeds[a] for a in AXES}
        hist.append({'round': k, 'gi': dict(gi), 'ge': {a: gi[a] * ratio[a] for a in AXES}, 'measured_m_s': meas, 'ratio': ratio_v, 'runs': info})
        print(name, 'round', k, {a: round(r, 4) for a, r in ratio_v.items()}, {a: round(v, 4) for a, v in meas.items()}, flush=True)
        if any(info[a]['unactivated_in_range'] for a in AXES) or not all(np.isfinite(list(meas.values()))):
            hist[-1]['stop'] = 'conduction block or no measurable wave (R4.4: stop and report)'
            break
        if all(abs(r - 1) <= 0.01 for r in ratio_v.values()):
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
            new[a] = gi[a] * (1.0 / ratio_v[a]) ** (1 / b)
        gi = new
    last = hist[-1]
    ok = 'stop' not in last
    return {'speeds_m_s': speeds, 'ratio_ge_over_gi': ratio, 'start_gi': start, 'stop': last.get('stop'),
            'within_1pct': bool(ok and all(abs(r - 1) <= 0.01 for r in last['ratio'].values())),
            'within_3pct': bool(ok and all(abs(r - 1) <= 0.03 for r in last['ratio'].values())),
            'rounds': len(hist), 'gi': last['gi'], 'ge': last['ge'], 'measured_m_s': last['measured_m_s'], 'history': hist}


def edge_mean(P, E):
    return float(np.mean([np.linalg.norm(P[E[:, a]] - P[E[:, b]], axis=1).mean() for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]))


def main():
    assert SPEEDS['6G8DD8S5'] == SPEEDS['7D98EVAR'] and FIX2['6G8DD8S5']['sigma_S_m'] == FIX2['7D98EVAR']['sigma_S_m']
    P, E, ed = S.slab_mesh(seed=0)
    mesh = write_mesh(P, E)
    info = {'nodes': int(len(P)), 'tets': int(len(E)), 'edge_mean_mm': round(edge_mean(P, E), 3), 'edge_max_mm': round(float(ed.max()), 3)}
    print('slab', info, flush=True)
    out = {'lock_sha256': '08ea65d3cda1adac9dcb1935a9000f32bbe093fc65e1e2e52ed8556373a1980b', 'slab': info, 'np': NP, 'sets': {}}
    for name, h in SETS.items():
        sp = SPEEDS[h]; f2 = FIX2[h]['sigma_S_m']; old = V51[h]
        ratio = {a: f2[a]['ge'] / f2[a]['gi'] for a in AXES}
        start = {}
        for a in AXES:
            c = old['conductivities_S_m'][a]
            sm = bulk(c['gi'], c['ge']) * (sp[a] / old['speeds_m_s'][a]) ** 2
            start[a] = sm * (1 + ratio[a]) / ratio[a]
        out['sets'][name] = calibrate(mesh, P, sp, ratio, start, name)
        json.dump(out, open(os.path.join(HERE, 'slab_mono52.json'), 'w'), indent=1)
    if not all(r['within_3pct'] for r in out['sets'].values()):
        sys.exit('not within 3 % on every axis: params not written (R4.4: stop and report)')
    par = {'method': 'v5.2 step 6 (R4.4): flat block, straight fibres, planar waves, within 3 % (mono_slab52.py, slab_mono52.json)',
           'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'slab': info, 'hearts': {}}
    for h in ('Y5HYEDL4', '6G8DD8S5', '7D98EVAR'):
        r = out['sets']['control' if h == 'Y5HYEDL4' else 'HF']
        par['hearts'][h] = {'speed_set': 'control' if h == 'Y5HYEDL4' else 'HF', 'speeds_m_s': r['speeds_m_s'], 'within_3pct': r['within_3pct'],
                            'within_1pct': r['within_1pct'], 'rounds': r['rounds'], 'measured_m_s': r['measured_m_s'],
                            'conductivities_S_m': {a: {'gi': r['gi'][a], 'ge': r['ge'][a]} for a in AXES}}
    json.dump(par, open(os.path.join(REPO, 'params', 'v52_mono_conductivities.json'), 'w'), indent=1)
    print(json.dumps({n: {k: v for k, v in r.items() if k != 'history'} for n, r in out['sets'].items()}, indent=1))


if __name__ == '__main__':
    main()
