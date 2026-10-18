"""Monodomain conductivities for the v5.1 speeds (27-site monodomain check, step 1; Alex 18 Oct 2026 20:51:05 UTC "Yes").

Method = sims/biv_model/07_patch_tune.py --myo / --myo-refine and its transit run (3 Oct 2026), copied with these changes:
- targets: fibre 0.60 m/s, in-wall cross-fibre (sheet) 0.36 m/s (HF 0.26), transmural (sheet-normal) 0.48 m/s (HF 0.336),
  the last as the transit time from 7 mm to 1 mm below the epicardium with the whole patch endocardium stimulated:
  6 mm / v_n = 12.5 ms (HF 17.857 ms) (params/v51_speeds.json);
- the patch mesh carries the v5.1 fibres (runs/v51_2026-10-15/08_monodomain/patch/<H>/patch51.*; pts / elem / vtx are links
  to data/biv/<H>/patch_lvfw.*; v5.1 vs the patch's own fibres: median 0.3-1.1 deg);
- no fast layer: tag-2 elements get the myocardial fibre / sheet / normal conductivities, as in the network-arm beats
  (12_eikonal.py --no-fast-layer rule, as the 12 Oct monodomain check);
- start from each heart's calibration.json (read only) with gi and ge of a direction scaled together (anisotropy ratio
  kept); each round corrects every direction by (target / measured)^(1 / b), b = 0.5 (fit from the last two rounds once
  they exist), until all three are within 3 % (the 3 Oct tolerance), at most 5 rounds;
- nothing is written into data/: results in params/v51_mono_conductivities.json and
  analysis/v51_2026-10-15/08_monodomain/calibration_<H>.json; runs in runs/v51_2026-10-15/08_monodomain/cal/<H>/.
Speed measures as 07: mid-wall stimulus (1.5 mm ball) at the patch centre, nodes at the same depth (|rho - rho_site| < 0.04)
3-10 mm away within 20 deg of the local fibre / sheet axis, speed = 1 / slope of LAT vs distance (2 mm bins, medians).
Model: monodomain, Tomek, dt 10 us, stimulus 400 uA/cm3 x 1 ms, LAT -10 mV.
Usage (repo root, venv, PATH with openCARP's mpiexec): HEART=<H> python -B analysis/v51_2026-10-15/08_monodomain/mono_cal51.py
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
H = os.environ['HEART']
SP = json.load(open(os.path.join(REPO, 'params', 'v51_speeds.json')))['hearts'][H]
PATCH = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'patch', H, 'patch51')
PD = os.path.dirname(PATCH)
RUNS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'cal', H)
UVC = os.path.join(REPO, 'data', 'biv', H, 'uvc')
TARGET = {'fibre': SP['fibre'], 'sheet': SP['sheet'], 'transit_ms': 6.0 / SP['normal']}
NP = 6
LOGF = os.path.join(HERE, f'calibration_{H}.json')


def vtx_read(f):
    return np.loadtxt(f, skiprows=2, dtype=np.int64, ndmin=1)


def vtx_write(f, nodes):
    with open(f, 'w') as fh:
        fh.write(f'{len(nodes)}\nintra\n')
        np.savetxt(fh, np.asarray(nodes, dtype=np.int64), fmt='%d')


def run(label, g, stim_nodes, tend):
    d = os.path.join(RUNS, label)
    os.makedirs(d, exist_ok=True)
    vtx_write(os.path.join(d, 'stim.vtx'), stim_nodes)
    gr = ['-num_gregions', 1, '-gregion[0].num_IDs', 2, '-gregion[0].ID[0]', 1, '-gregion[0].ID[1]', 2,
          '-gregion[0].g_il', g['fibre'][0], '-gregion[0].g_el', g['fibre'][1],
          '-gregion[0].g_it', g['sheet'][0], '-gregion[0].g_et', g['sheet'][1],
          '-gregion[0].g_in', g['normal'][0], '-gregion[0].g_en', g['normal'][1]]
    cmd = ['mpiexec', '-n', NP, 'openCARP', '-meshname', PATCH, '-simID', d,
           '-bidomain', 0, '-dt', 10, '-parab_solve', 1, '-tend', tend,
           '-spacedt', min(5.0, tend), '-timedt', min(5.0, tend),
           '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'),
           '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
           '-lats[0].threshold', -10, '-lats[0].method', 1] + gr
    t0 = time.time()
    with open(os.path.join(d, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    return np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat')), round(time.time() - t0, 1)


def speeds(g, k):
    pts = np.loadtxt(PATCH + '.pts', skiprows=1)
    nodes = np.load(os.path.join(PD, 'patch_lvfw_nodes.npy'))
    rho = np.loadtxt(os.path.join(UVC, 'rho.dat'))[nodes]
    c = pts.mean(0)
    cand = np.where(np.abs(rho - 0.5) < 0.05)[0]
    site = cand[np.argmin(np.linalg.norm(pts[cand] - c, axis=1))]
    stim = np.where(np.linalg.norm(pts - pts[site], axis=1) < 1500)[0]
    E = np.loadtxt(PATCH + '.elem', skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    lon = np.loadtxt(PATCH + '.lon', skiprows=1)
    touch = np.where((E == site).any(1))[0]
    f = lon[touch, :3].copy(); sv = lon[touch, 3:].copy()
    f[(f @ f[0]) < 0] *= -1; sv[(sv @ sv[0]) < 0] *= -1
    f = f.mean(0); f /= np.linalg.norm(f); sv = sv.mean(0); sv /= np.linalg.norm(sv)
    act, wall = run(f'round{k}_speed', g, stim, 25.0)
    d = pts - pts[site]
    r = np.linalg.norm(d, axis=1) / 1e3
    u = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    same = (np.abs(rho - rho[site]) < 0.04) & (r >= 3) & (r < 10) & (act >= 0)
    out = {'speed_run_wall_s': wall}
    for name, ax in (('fibre', f), ('sheet', sv)):
        sel = same & (np.abs(u @ ax) > np.cos(np.radians(20)))
        cen, tb = [], []
        for b0 in np.arange(3, 10.01, 2.0)[:-1]:
            m = sel & (r >= b0) & (r < b0 + 2)
            if m.sum() >= 3:
                cen.append(b0 + 1); tb.append(np.median(act[m]))
        out[name] = float(1 / np.polyfit(cen, tb, 1)[0]) if len(cen) >= 2 else float('nan')
        out[f'n_{name}'] = int(sel.sum())
    return out


def transit(g, k):
    pts = np.loadtxt(PATCH + '.pts', skiprows=1)
    endo = vtx_read(os.path.join(PD, 'patch_lvfw_lv_endo.vtx'))
    epi = vtx_read(os.path.join(PD, 'patch_lvfw_epi.vtx'))
    act, wall = run(f'round{k}_transit', g, endo, 40.0)
    dep = cKDTree(pts[epi]).query(pts)[0] / 1e3
    o = {}
    for dmm in (1.0, 7.0):
        s = (np.abs(dep - dmm) < 0.25) & (act >= 0)
        o[dmm] = float(act[s].mean()) if s.any() else np.nan
    return {'transit_ms': o[1.0] - o[7.0], 'transit_run_wall_s': wall, 'unactivated': int((act < 0).sum())}


def main():
    cal = json.load(open(os.path.join(REPO, 'data', 'biv', H, 'calibration.json')))
    g = {'fibre': (cal['fibre']['gi'], cal['fibre']['ge']), 'sheet': (cal['sheet']['gi'], cal['sheet']['ge']),
         'normal': (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])}
    # first guess: speed ~ g^0.5 from the 3 Oct targets (fibre 0.60, sheet 0.40, transit 12.6 ms)
    g['sheet'] = tuple(x * (TARGET['sheet'] / 0.40) ** 2 for x in g['sheet'])
    g['normal'] = tuple(x * (12.6 / TARGET['transit_ms']) ** 2 for x in g['normal'])
    hist = []
    for k in range(5):
        m = speeds(g, k) | transit(g, k)
        ratio = {'fibre': m['fibre'] / TARGET['fibre'], 'sheet': m['sheet'] / TARGET['sheet'], 'normal': TARGET['transit_ms'] / m['transit_ms']}
        hist.append({'round': k, 'g': {a: list(v) for a, v in g.items()}, 'measured': m, 'speed_ratio_measured_over_target': ratio})
        json.dump({'heart': H, 'targets': TARGET, 'history': hist}, open(LOGF, 'w'), indent=1)
        print(H, 'round', k, {a: round(v, 4) for a, v in ratio.items()}, m, flush=True)
        if all(abs(r - 1) <= 0.03 for r in ratio.values()):
            break
        new = {}
        for a in ('fibre', 'sheet', 'normal'):
            b = 0.5
            if len(hist) >= 2:
                g0, g1 = hist[-2]['g'][a][0], hist[-1]['g'][a][0]
                r0, r1 = hist[-2]['speed_ratio_measured_over_target'][a], hist[-1]['speed_ratio_measured_over_target'][a]
                if g0 != g1 and r0 > 0 and r1 > 0:
                    bb = np.log(r1 / r0) / np.log(g1 / g0)
                    b = float(bb) if 0.2 < bb < 1.0 else 0.5
            fac = (1.0 / ratio[a]) ** (1 / b)
            new[a] = (g[a][0] * fac, g[a][1] * fac)
        g = new
    ok = all(abs(r - 1) <= 0.03 for r in hist[-1]['speed_ratio_measured_over_target'].values())
    res = {'heart': H, 'targets': TARGET, 'within_3pct': bool(ok), 'rounds': len(hist),
           'conductivities_S_m': {a: {'gi': v[0], 'ge': v[1]} for a, v in (hist[-1]['g']).items()},
           'measured': hist[-1]['measured'], 'history': hist, 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    json.dump(res, open(LOGF, 'w'), indent=1)
    pf = os.path.join(REPO, 'params', 'v51_mono_conductivities.json')
    allp = json.load(open(pf)) if os.path.exists(pf) else {'method': __doc__.split('\n')[0], 'hearts': {}}
    allp['hearts'][H] = {k: res[k] for k in ('targets', 'within_3pct', 'rounds', 'conductivities_S_m', 'measured', 'written')}
    json.dump(allp, open(pf, 'w'), indent=1)
    print(json.dumps({k: res[k] for k in ('within_3pct', 'rounds', 'conductivities_S_m', 'measured')}, indent=1))
    if not ok:
        sys.exit(f'{H}: not within 3 % after {len(hist)} rounds')


if __name__ == '__main__':
    main()
