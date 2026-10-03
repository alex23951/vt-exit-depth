#!/usr/bin/env python
"""
Step 7: implement the frozen measured targets on the heart mesh, using a full-thickness
LV free-wall patch of the pilot heart (same mesh, fibres and fast-layer construction).

Patch: elements with LV side (v = 0 at all nodes), |phi| >= 120 deg (free wall, away from
the septum) and 0.25 <= z <= 0.75 (element mean), full wall thickness.

Measurements (straight-line distance, as in the wedge; the CT endocardium is rough, so
paths along the surface are ~2x longer than the distance the wave front covers):
  speed    : stimulus at the patch's central LV-endocardial node; speed = slope of
             distance vs LAT (median per 2.5 mm bin) for fast-layer LV-endo nodes 5-15 mm away.
  transit  : whole patch LV endocardium stimulated at once; transit = LAT(1 mm below epi)
             - LAT(7 mm below epi), nodes in 0.5 mm bands of distance-to-epicardium.

Modes:
  --fast-scan f1,f2,f3       fast-layer conductivity scale factors (x 4.6205/16.5972) -> speed
  --fit                      fit log(speed) = a + b log(g) on the scan, print g for 1.5/2.0/3.0
  --fast-g gi                one speed run at gi (ge scaled with the same ratio)
  --transit gi --gn gn       one transit run with fast layer gi and sheet-normal gi gn
  --auto                     full per-heart calibration (pipeline step): fast-layer scan at
                             0.5/1/2 x the wedge value, power-law fit, one confirmation run each
                             for 1.5/2.0/3.0 m/s; then sheet-normal scan at 0.62/0.78/1.0 x the
                             wedge value with the 2.0 m/s layer, fit, one confirmation for 12.6 ms.
                             Writes data/biv/<HEART>/calibration.json (the values every later
                             run of this heart uses). Runtime ~12-15 min (patch runs ~45-90 s).
"""

import argparse
import json
import os
import subprocess

import numpy as np
from scipy.spatial import cKDTree

from common import OUT, REPO, read_elem, read_lon, read_pts, read_vtx, write_vtx

SURF = os.path.join(OUT, 'surfaces')
UVC = os.path.join(OUT, 'uvc')
PATCH = os.path.join(OUT, 'patch_lvfw')
G_F, G_S, G_N = (0.5606, 2.0138), (0.3368, 1.2096), (0.3843, 1.3805)
G_FAST = (4.6205, 16.5972)
R_FAST = G_FAST[1] / G_FAST[0]
R_N = G_N[1] / G_N[0]
LOG = os.path.join(OUT, 'patch_runs.json')
RUN_PREFIX = os.environ.get('RUN_PREFIX', '2026-10-02_patch')      # run folder prefix under runs/
SPEED_TARGETS = (1.5, 2.0, 3.0)
TRANSIT_TARGET = 12.6


def build_patch():
    if os.path.exists(PATCH + '.elem'):
        return
    pts = read_pts(os.path.join(OUT, 'bivF'))
    E, tag = read_elem(os.path.join(OUT, 'bivF'))
    lon = read_lon(os.path.join(OUT, 'bivF'))
    z, phi, v = (np.loadtxt(os.path.join(UVC, n + '.dat')) for n in ('z', 'phi', 'v'))
    ze = z[E].mean(1)
    pe = np.abs(np.angle(np.exp(1j * phi[E]).mean(1)))
    keep = (v[E].max(1) == 0) & (pe >= np.radians(120)) & (ze >= 0.25) & (ze <= 0.75)
    Ek = E[keep]
    nodes = np.unique(Ek)
    new = -np.ones(len(pts), np.int64)
    new[nodes] = np.arange(len(nodes))
    np.savetxt(PATCH + '.pts', pts[nodes], fmt='%.3f', header=str(len(nodes)), comments='')
    with open(PATCH + '.elem', 'w') as f:
        f.write(f'{len(Ek)}\n')
        np.savetxt(f, np.hstack([new[Ek], tag[keep][:, None]]), fmt='Tt %d %d %d %d %d')
    with open(PATCH + '.lon', 'w') as f:
        f.write('2\n')
        np.savetxt(f, lon[keep], fmt='%.5f')
    np.save(PATCH + '_nodes.npy', nodes)
    # patch LV endo and epi nodes (old surfaces restricted to patch)
    for n in ('lv_endo', 'epi'):
        s = read_vtx(os.path.join(SURF, n + '.vtx'))
        s = new[s[new[s] >= 0]]
        write_vtx(PATCH + f'_{n}.vtx', s)
    print(f'patch: {len(nodes)} nodes, {len(Ek)} elements, fast {int((tag[keep] == 2).sum())}')


CUR_F, CUR_S = G_F, G_S          # fibre / sheet (gi, ge) used by run(); set by myo calibration


def run(label, gfast, gn, stim_nodes, tend, np_=6, gf=None, gs=None):
    gf = gf or CUR_F
    gs = gs or CUR_S
    rid = f'{RUN_PREFIX}_{label}'
    d = os.path.join(REPO, 'runs', rid)
    os.makedirs(d, exist_ok=True)
    write_vtx(os.path.join(d, 'stim.vtx'), stim_nodes)
    g = ['-num_gregions', 2, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', gf[0], '-gregion[0].g_el', gf[1],
         '-gregion[0].g_it', gs[0], '-gregion[0].g_et', gs[1],
         '-gregion[0].g_in', gn[0], '-gregion[0].g_en', gn[1],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', gfast[0], f'-gregion[1].g_e{k}', gfast[1]]
    cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', PATCH, '-simID', d,
           '-bidomain', 0, '-dt', 10, '-parab_solve', 1, '-tend', tend,
           '-spacedt', min(5.0, tend), '-timedt', min(5.0, tend),
           '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'),
           '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
           '-lats[0].threshold', -10, '-lats[0].method', 1] + g
    with open(os.path.join(d, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    return rid, np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat'))


def speed_run(gi):
    pts = np.loadtxt(PATCH + '.pts', skiprows=1)
    E = np.loadtxt(PATCH + '.elem', skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64)
    endo = read_vtx(PATCH + '_lv_endo.vtx')
    c = pts[endo].mean(0)
    site = endo[np.argmin(np.linalg.norm(pts[endo] - c, axis=1))]
    stim = np.where(np.linalg.norm(pts - pts[site], axis=1) < 1500)[0]
    rid, act = run(f'speed_g{gi:.4f}', (gi, gi * R_FAST), G_N, stim, 15.0)
    fn = np.zeros(len(pts), bool)
    fn[np.unique(E[E[:, 4] == 2, :4])] = True
    m = np.zeros(len(pts), bool)
    m[endo] = True
    eu = np.linalg.norm(pts - pts[site], axis=1) / 1e3
    sel = m & fn & (act >= 0) & (eu >= 5) & (eu < 15)
    bins = np.arange(5, 15.01, 2.5)
    tb = np.array([np.median(act[sel & (eu >= b) & (eu < b + 2.5)]) for b in bins[:-1]])
    sp = float(1 / np.polyfit(bins[:-1] + 1.25, tb, 1)[0])
    return {'run': rid, 'gi_fast': gi, 'ge_fast': gi * R_FAST, 'speed_m_s': sp, 'n_nodes': int(sel.sum()),
            'site_to_patch_edge_mm': None}


def transit_run(gi, gn):
    pts = np.loadtxt(PATCH + '.pts', skiprows=1)
    endo = read_vtx(PATCH + '_lv_endo.vtx')
    epi = read_vtx(PATCH + '_epi.vtx')
    rid, act = run(f'transit_g{gi:.4f}_gn{gn:.4f}', (gi, gi * R_FAST), (gn, gn * R_N), endo, 35.0)
    dep = cKDTree(pts[epi]).query(pts)[0] / 1e3
    out = {}
    for dmm in (1.0, 7.0):
        s = (np.abs(dep - dmm) < 0.25) & (act >= 0)
        out[dmm] = (float(act[s].mean()) if s.any() else np.nan, int(s.sum()))
    return {'run': rid, 'gi_fast': gi, 'gi_n': gn, 'ge_n': gn * R_N,
            'transit_ms': out[1.0][0] - out[7.0][0], 'n_1mm': out[1.0][1], 'n_7mm': out[7.0][1],
            'unactivated': int((act < 0).sum())}


def log(entry):
    allr = json.load(open(LOG)) if os.path.exists(LOG) else []
    allr.append(entry)
    json.dump(allr, open(LOG, 'w'), indent=1)
    print(json.dumps(entry), flush=True)


def powerfit(x, y):
    b, a = np.polyfit(np.log(x), np.log(y), 1)
    return a, b


def auto():
    build_patch()
    scan = [speed_run(G_FAST[0] * f) for f in (0.5, 1.0, 2.0)]
    for e in scan:
        log(e)
    a, b = powerfit([e['gi_fast'] for e in scan], [e['speed_m_s'] for e in scan])
    fast = {}
    for v in SPEED_TARGETS:
        gi = float(np.exp((np.log(v) - a) / b))
        e = speed_run(gi)
        log(e)
        fast[str(v)] = {'gi': gi, 'ge': gi * R_FAST, 'measured_m_s': e['speed_m_s']}
    g2 = fast['2.0']['gi']
    tr = [transit_run(g2, G_N[0] * f) for f in (0.62, 0.78, 1.0)]
    for e in tr:
        log(e)
    a2, b2 = powerfit([e['gi_n'] for e in tr], [e['transit_ms'] for e in tr])
    gn = float(np.exp((np.log(TRANSIT_TARGET) - a2) / b2))
    e = transit_run(g2, gn)
    log(e)
    cal = {'heart': os.path.basename(OUT), 'method': '07_patch_tune.py --auto (LV free-wall patch)',
           'fast_layer': fast,
           'sheet_normal': {'gi': gn, 'ge': gn * R_N, 'transit_ms': e['transit_ms'], 'target_ms': TRANSIT_TARGET},
           'fibre': {'gi': G_F[0], 'ge': G_F[1]}, 'sheet': {'gi': G_S[0], 'ge': G_S[1]},
           'fits': {'speed': {'a': a, 'b': b}, 'transit': {'a': a2, 'b': b2}}}
    ok = all(abs(fast[k]['measured_m_s'] / float(k) - 1) < 0.03 for k in fast) and \
        abs(e['transit_ms'] / TRANSIT_TARGET - 1) < 0.03
    cal['within_3pct'] = bool(ok)
    json.dump(cal, open(os.path.join(OUT, 'calibration.json'), 'w'), indent=1)
    print(json.dumps(cal, indent=1))


def myo_speed_run(gf, gs, gn):
    """Fibre and in-wall cross-fibre (= sheet, sheets parallel to the wall) speeds:
    mid-wall stimulus at the patch centre, fast layer given the sheet conductivity
    isotropically (so it is not fast), nodes at the same depth (|rho - rho_site| < 0.04)
    3-10 mm away whose direction from the site is within 20 deg of the local fibre or of
    the local sheet axis; speed = 1 / slope of LAT vs distance (2 mm bins, medians)."""
    pts = np.loadtxt(PATCH + '.pts', skiprows=1)
    nodes = np.load(PATCH + '_nodes.npy')
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
    rid, act = run(f'myo_f{gf[0]:.4f}_s{gs[0]:.4f}', (gs[0], gs[1]), gn, stim, 25.0, gf=gf, gs=gs)
    d = pts - pts[site]
    r = np.linalg.norm(d, axis=1) / 1e3
    u = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    same = (np.abs(rho - rho[site]) < 0.04) & (r >= 3) & (r < 10) & (act >= 0)
    out = {'run': rid, 'gi_f': gf[0], 'gi_s': gs[0]}
    for name, ax in (('fibre', f), ('sheet', sv)):
        sel = same & (np.abs(u @ ax) > np.cos(np.radians(20)))
        bins = np.arange(3, 10.01, 2.0)
        cen, tb = [], []
        for b0 in bins[:-1]:
            m = sel & (r >= b0) & (r < b0 + 2)
            if m.sum() >= 3:
                cen.append(b0 + 1); tb.append(np.median(act[m]))
        out[f'v_{name}_m_s'] = float(1 / np.polyfit(cen, tb, 1)[0]) if len(cen) >= 2 else float('nan')
        out[f'n_{name}'] = int(sel.sum())
    return out


def myo_calibrate():
    """Fibre / sheet conductivities to measured 0.6 / 0.4 m/s on this heart's patch; then
    re-check sheet-normal transit (12.6 ms) and fast-layer speed (2.0 m/s) and correct each
    once if more than 3 % off. Updates calibration.json (old values kept under 'history')."""
    global CUR_F, CUR_S
    build_patch()
    cal = json.load(open(os.path.join(OUT, 'calibration.json')))
    gn = (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])
    rf, rs = G_F[1] / G_F[0], G_S[1] / G_S[0]
    scan = []
    for k in (0.7, 0.85, 1.0):
        e = myo_speed_run((G_F[0] * k, G_F[1] * k), (G_S[0] * k, G_S[1] * k), gn)
        log(e); scan.append(e)
    af, bf = powerfit([e['gi_f'] for e in scan], [e['v_fibre_m_s'] for e in scan])
    as_, bs = powerfit([e['gi_s'] for e in scan], [e['v_sheet_m_s'] for e in scan])
    gif = float(np.exp((np.log(0.6) - af) / bf)); gis = float(np.exp((np.log(0.4) - as_) / bs))
    CUR_F, CUR_S = (gif, gif * rf), (gis, gis * rs)
    conf = myo_speed_run(CUR_F, CUR_S, gn); log(conf)
    g2 = cal['fast_layer']['2.0']['gi']
    tr = transit_run(g2, gn[0]); log(tr)
    if abs(tr['transit_ms'] / TRANSIT_TARGET - 1) > 0.03:
        bt = cal.get('fits', {}).get('transit', {}).get('b', -0.58)
        gnn = gn[0] * (TRANSIT_TARGET / tr['transit_ms']) ** (1 / bt)
        gn = (gnn, gnn * R_N)
        tr = transit_run(g2, gn[0]); log(tr)
    sp = speed_run(g2); log(sp)
    fast = cal['fast_layer']
    if abs(sp['speed_m_s'] / 2.0 - 1) > 0.03:
        b = cal.get('fits', {}).get('speed', {}).get('b', 0.538)
        fac = (2.0 / sp['speed_m_s']) ** (1 / b)
        fast = {k: {'gi': v['gi'] * fac, 'ge': v['ge'] * fac, 'measured_m_s': None} for k, v in fast.items()}
        sp = speed_run(fast['2.0']['gi']); log(sp)
        fast['2.0']['measured_m_s'] = sp['speed_m_s']
    hist = cal.get('history', [])
    hist.append({k: cal[k] for k in ('fibre', 'sheet', 'sheet_normal', 'fast_layer')})
    cal.update({'fibre': {'gi': CUR_F[0], 'ge': CUR_F[1], 'measured_m_s': conf['v_fibre_m_s']},
                'sheet': {'gi': CUR_S[0], 'ge': CUR_S[1], 'measured_m_s': conf['v_sheet_m_s']},
                'sheet_normal': {'gi': gn[0], 'ge': gn[1], 'transit_ms': tr['transit_ms'], 'target_ms': TRANSIT_TARGET},
                'fast_layer': fast, 'fast_check_m_s': sp['speed_m_s'], 'history': hist,
                'myo_fits': {'fibre': {'a': af, 'b': bf}, 'sheet': {'a': as_, 'b': bs}},
                'method_myo': '07_patch_tune.py --myo (2026-10-03)'})
    json.dump(cal, open(os.path.join(OUT, 'calibration.json'), 'w'), indent=1)
    print(json.dumps({k: cal[k] for k in ('fibre', 'sheet', 'sheet_normal')} | {'fast_check_m_s': sp['speed_m_s']}, indent=1))


def myo_refine(rounds=2):
    """Correct fibre / sheet separately from the last confirmation (speed ~ g^b, b from the
    myo fits), confirm, until both are within 3 %; then re-check transit and fast layer."""
    global CUR_F, CUR_S
    build_patch()
    cal = json.load(open(os.path.join(OUT, 'calibration.json')))
    gn = (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])
    CUR_F = (cal['fibre']['gi'], cal['fibre']['ge']); CUR_S = (cal['sheet']['gi'], cal['sheet']['ge'])
    vf, vs = cal['fibre']['measured_m_s'], cal['sheet']['measured_m_s']
    bf, bs = cal['myo_fits']['fibre']['b'], cal['myo_fits']['sheet']['b']
    bf = bf if 0.2 < bf < 1.0 else 0.5
    bs = bs if 0.2 < bs < 1.0 else 0.5
    for _ in range(rounds):
        if abs(vf / 0.6 - 1) < 0.03 and abs(vs / 0.4 - 1) < 0.03:
            break
        kf, ks = (0.6 / vf) ** (1 / bf), (0.4 / vs) ** (1 / bs)
        CUR_F = (CUR_F[0] * kf, CUR_F[1] * kf); CUR_S = (CUR_S[0] * ks, CUR_S[1] * ks)
        e = myo_speed_run(CUR_F, CUR_S, gn); log(e)
        vf, vs = e['v_fibre_m_s'], e['v_sheet_m_s']
    tr = transit_run(cal['fast_layer']['2.0']['gi'], gn[0]); log(tr)
    sp = speed_run(cal['fast_layer']['2.0']['gi']); log(sp)
    cal['history'].append({k: cal[k] for k in ('fibre', 'sheet')})
    cal['fibre'] = {'gi': CUR_F[0], 'ge': CUR_F[1], 'measured_m_s': vf}
    cal['sheet'] = {'gi': CUR_S[0], 'ge': CUR_S[1], 'measured_m_s': vs}
    cal['sheet_normal']['transit_ms'] = tr['transit_ms']
    cal['fast_check_m_s'] = sp['speed_m_s']
    cal['myo_within_3pct'] = bool(abs(vf / 0.6 - 1) < 0.03 and abs(vs / 0.4 - 1) < 0.03)
    json.dump(cal, open(os.path.join(OUT, 'calibration.json'), 'w'), indent=1)
    print(json.dumps({'fibre': cal['fibre'], 'sheet': cal['sheet'], 'transit_ms': tr['transit_ms'],
                      'fast_m_s': sp['speed_m_s'], 'within_3pct': cal['myo_within_3pct']}, indent=1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--myo-refine', action='store_true')
    p.add_argument('--myo', action='store_true', help='fibre/sheet calibration to measured 0.6/0.4 m/s')
    p.add_argument('--auto', action='store_true')
    p.add_argument('--fast-scan', default='')
    p.add_argument('--fit', action='store_true')
    p.add_argument('--fast-g', type=float, nargs='*', default=[])
    p.add_argument('--transit', type=float, default=None)
    p.add_argument('--gn', type=float, nargs='*', default=[G_N[0]])
    a = p.parse_args()
    if a.auto:
        auto()
        return
    if a.myo:
        myo_calibrate()
        return
    if a.myo_refine:
        myo_refine()
        return
    build_patch()
    for f in [float(x) for x in a.fast_scan.split(',') if x]:
        log(speed_run(G_FAST[0] * f))
    for gi in a.fast_g:
        log(speed_run(gi))
    if a.fit:
        r = [e for e in json.load(open(LOG)) if 'speed_m_s' in e]
        g = np.array([e['gi_fast'] for e in r]); s = np.array([e['speed_m_s'] for e in r])
        b, la = np.polyfit(np.log(g), np.log(s), 1)
        fit = {'fit': 'speed = exp(a) * gi^b', 'a': float(la), 'b': float(b),
               'gi_for': {str(v): float(np.exp((np.log(v) - la) / b)) for v in (1.5, 2.0, 3.0)}}
        print(json.dumps(fit), flush=True)
        json.dump(fit, open(os.path.join(OUT, 'patch_fast_fit.json'), 'w'), indent=1)
    if a.transit is not None:
        for gn in a.gn:
            log(transit_run(a.transit, gn))


if __name__ == '__main__':
    main()
