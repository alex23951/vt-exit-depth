#!/usr/bin/env python
"""
Monodomain check of two network-v3 beats on the control heart Y5HYEDL4 (Alex "Go", 22:17 UTC 12 Oct 2026, relayed by
the coordinator; up to ~3 h of PC). New script: frozen files are only read.

Question: does a monodomain beat (real reaction-diffusion Vm, no single-template pseudo-Vm) remove the late synchronous
burst that makes the paced RVOT MDI ~0.56-0.67 (clinical ~0.40)?

Beats (eikonal network-v3 runs of job 8, openCARP fields):
  rvot   rvot_septal_z_d50                  (septal RVOT, MDI 0.56 cb true onset)
  lvfw   lv_free_wall_phi180_z0.5_d10      (LV endocardium 10 %, comparison)
Monodomain settings = the frozen pilot (06_check_run.py): Tomek, dt 10 us, heart-mesh calibrated conductivities
(calibration.json), stimulus 400 uA/cm3 x 1 ms on nodes within 1.5 mm of the site, LAT threshold -10 mV, Vm every 1 ms;
6 processes. Fast layer OFF as in the network arm: tag-2 elements get the myocardial fibre / sheet / normal
conductivities (12_eikonal.py --no-fast-layer rule).
Network coupling: one-way replay (accepted by gate rule 8): every junction stimulus time of the eikonal beat
(runs/<run>/pmj_stims.json) becomes a timed stimulus; ASSUMPTION: each junction node is widened to the nodes within 1.0
mm so a monodomain stimulus can capture (the eikonal used the node itself); same 400 uA/cm3 x 1 ms. Capture is checked
afterwards (LAT at junction nodes minus their stimulus time).
ECG: Vm x cb weights (data/biv/Y5HYEDL4/ecgW_nofast_cb.npz, as 15_conductor.py rescore); scored with ecg_depth_criteria
0.3.0 at true onset (stimulus, last activation). Comparison with the eikonal beat: share of nodes within 5 ms, time to
10 / 50 / 90 % of the ventricular volume, total activation, QRS, MDI, time to the largest precordial deflection,
pseudo-delta.
Memory guard: openCARP is stopped (its own process group only) if MemAvailable < 900 MB.

Usage (venv active, PATH with openCARP's mpiexec):
  python mono_check.py test rvot         10 ms run to measure s per simulated ms
  python mono_check.py run rvot|lvfw     full run (tend = eikonal total activation + 30 ms)
  python mono_check.py analyze           comparison table -> results.csv / results.txt
"""

import json
import os
import signal
import subprocess
import sys
import time

os.environ['HEART'] = 'Y5HYEDL4'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np                                                  # noqa: E402
from common import OUT, read_pts, write_vtx                        # noqa: E402

RUNS = os.path.join(REPO, 'runs')
MESH = os.path.join(OUT, 'bivF')
BEATS = {'rvot': 'rvot_septal_z_d50', 'lvfw': 'lv_free_wall_phi180_z0.5_d10'}
NP, STIM_R_UM, PMJ_R_UM = int(os.environ.get('MONO_NP', '6')), 1500.0, 1000.0   # MONO_NP: fewer processes = less memory
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def eik_run(b):
    return f'2026-10-07_purk_Y5HYEDL4_{BEATS[b]}'


def mono_id(b, test=False):
    return f'2026-10-12_mono_purk_Y5HYEDL4_{BEATS[b]}' + ('_test' if test else '')


def mem_avail_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


def cmd(b, run, tend, test=False):
    cal = json.load(open(os.path.join(OUT, 'calibration.json')))
    gf = (cal['fibre']['gi'], cal['fibre']['ge']); gs = (cal['sheet']['gi'], cal['sheet']['ge'])
    gn = (cal['sheet_normal']['gi'], cal['sheet_normal']['ge'])
    pts = read_pts(MESH)
    s = json.load(open(os.path.join(RUNS, eik_run(b), 'summary_12.json')))
    site = int(s['site_node'])
    write_vtx(os.path.join(run, 'stim.vtx'), np.where(np.linalg.norm(pts - pts[site], axis=1) < STIM_R_UM)[0])
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    stims = [(os.path.join(run, 'stim'), 0.0)]
    sd = os.path.join(run, 'pmj_stims_wide'); os.makedirs(sd, exist_ok=True)
    js = json.load(open(os.path.join(RUNS, eik_run(b), 'pmj_stims.json')))
    lo, hi = min(x['start'] for x in js), max(x['start'] for x in js)
    for k, x in enumerate(js):
        if test:     # timing test only: openCARP needs start <= tend, so squeeze the starts into 2-8 ms (same stimulus count)
            x = dict(x, start=2.0 + 6.0 * (x['start'] - lo) / max(hi - lo, 1e-9))
        nodes = np.loadtxt(x['vtx'] + '.vtx', skiprows=2, dtype=np.int64, ndmin=1)
        wide = np.unique(np.concatenate([tree.query_ball_point(pts[n], PMJ_R_UM) for n in nodes]).astype(np.int64))
        f = os.path.join(sd, f'pmj_{k:04d}')
        write_vtx(f + '.vtx', wide)
        stims.append((f, float(x['start'])))
    so = ['-num_stim', len(stims)]
    for i, (vf, t0) in enumerate(stims):
        so += [f'-stim[{i}].crct.type', 0, f'-stim[{i}].elec.vtx_file', vf, f'-stim[{i}].ptcl.start', t0,
               f'-stim[{i}].pulse.strength', 400.0, f'-stim[{i}].ptcl.duration', 1.0, f'-stim[{i}].ptcl.npls', 1]
    g = ['-num_gregions', 1, '-gregion[0].num_IDs', 2, '-gregion[0].ID[0]', 1, '-gregion[0].ID[1]', 2,
         '-gregion[0].g_il', gf[0], '-gregion[0].g_el', gf[1], '-gregion[0].g_it', gs[0], '-gregion[0].g_et', gs[1],
         '-gregion[0].g_in', gn[0], '-gregion[0].g_en', gn[1]]
    c = ['mpiexec', '-n', NP, 'openCARP', '-meshname', MESH, '-simID', run,
         '-bidomain', 0, '-dt', 10.0, '-parab_solve', 1, '-tend', tend, '-spacedt', 1.0, '-timedt', 5.0,
         '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
         '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
         '-lats[0].threshold', -10, '-lats[0].method', 1] + so + g
    return [str(x) for x in c], site, len(stims)


def run(b, test=False):
    rid = mono_id(b, test)
    rd = os.path.join(RUNS, rid); os.makedirs(rd, exist_ok=True)
    ta = json.load(open(os.path.join(RUNS, eik_run(b), 'summary_12.json')))['total_activation_ms']
    tend = 10.0 if test else float(np.ceil((ta + 30) / 10) * 10)
    c, site, ns = cmd(b, rd, tend, test)
    t0, low = time.time(), 1e9
    with open(os.path.join(rd, 'openCARP.log'), 'w') as log:
        p = subprocess.Popen(c, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        status = 'ok'
        while p.poll() is None:
            time.sleep(5)
            m = mem_avail_mb(); low = min(low, m)
            if m < 900:
                os.killpg(p.pid, signal.SIGTERM); status = f'stopped by memory guard ({m:.0f} MB available)'
                p.wait(); break
        if status == 'ok' and p.returncode != 0:
            status = f'failed (openCARP exit {p.returncode})'
    wall = time.time() - t0
    s = {'beat': b, 'eikonal_run': eik_run(b), 'site_node': site, 'n_stimuli': ns, 'tend_ms': tend, 'np': NP,
         'wall_s': round(wall, 1), 's_per_sim_ms': round(wall / tend, 1), 'min_mem_available_mb': round(low), 'status': status}
    json.dump(s, open(os.path.join(rd, 'summary_mono.json'), 'w'), indent=1)
    print(json.dumps(s, indent=1), flush=True)


def igb(f):
    b = open(f, 'rb').read()
    h = b[:1024].decode('latin1')
    x = int(h.split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def frac_times(T, nvol):
    o = np.argsort(T)
    cw = np.cumsum(nvol[o]) / nvol.sum()
    return [round(float(T[o][np.searchsorted(cw, f)]), 1) for f in (0.1, 0.5, 0.9)]


def score(ecg, last):
    from ecg_depth_criteria import from_leads, measure_beat
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, LEADS.index(l)]), ecg[:, LEADS.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    m = measure_beat(from_leads(leads), 1000.0, onset_ms=pad, offset_ms=last + pad, baseline_window_ms=(pad - 45.0, pad - 5.0))
    n = int(round(last))
    tmax = min(int(np.argmax(np.abs(ecg[:n + 1, LEADS.index(k)] - ecg[0, LEADS.index(k)]))) for k in ('V1', 'V2', 'V3', 'V4', 'V5', 'V6'))
    return {'qrs_ms': m['qrs_duration_ms'], 'mdi': round(m['mdi_daniels'], 3), 'mdi_lead': m['mdi_daniels_lead'],
            't_largest_ms': tmax, 'pseudo_delta_ms': m['pseudo_delta_ms']}


def analyze():
    import pandas as pd
    pts = read_pts(MESH) / 1e3
    el = pd.read_csv(MESH + '.elem', sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    a, b_, c, d = (pts[el[:, k]] for k in range(4))
    nvol = np.bincount(el.ravel(), weights=np.repeat(np.abs(np.einsum('ij,ij->i', np.cross(b_ - a, c - a), d - a)) / 24, 4), minlength=len(pts))
    W = np.load(os.path.join(OUT, 'ecgW_nofast_cb.npz'))['W'].astype(float)
    net = dict(np.load(os.path.join(OUT, 'purkinje', 'network.npz')))
    rows = []
    for bk in BEATS:
        rd = os.path.join(RUNS, mono_id(bk))
        if not os.path.exists(os.path.join(rd, 'init_acts_LATs-thresh.dat')):
            continue
        Tm = np.loadtxt(os.path.join(rd, 'init_acts_LATs-thresh.dat'))
        Te = igb(os.path.join(RUNS, eik_run(bk), 'act.igb'))[-1].astype(float)
        ok = Tm >= 0
        vm = igb(os.path.join(rd, 'vm.igb')).astype(float)
        ecg_m = vm @ W.T
        d = os.path.join(RUNS, mono_id(bk) + '_ecg_cb', 'POSTPROC_DIR'); os.makedirs(d, exist_ok=True)
        for j, l in enumerate(LEADS):
            np.savetxt(os.path.join(d, f'ECG_{l}.dat'), np.c_[np.arange(len(ecg_m)), ecg_m[:, j]], fmt='%g %.6g')
        ecg_e = np.stack([np.loadtxt(os.path.join(RUNS, eik_run(bk) + '_ecg_cb', 'POSTPROC_DIR', f'ECG_{l}.dat'))[:, 1] for l in LEADS], 1)
        # junction capture: LAT at the junction nodes vs their stimulus time
        st = json.load(open(os.path.join(RUNS, eik_run(bk), 'pmj_stims.json')))
        lag = []
        for x in st:
            nn = np.loadtxt(x['vtx'] + '.vtx', skiprows=2, dtype=np.int64, ndmin=1)
            lag += list(Tm[nn] - x['start'])
        lag = np.array(lag)
        for name, T, ecg in (('eikonal', Te, ecg_e), ('monodomain', np.where(ok, Tm, np.nan), ecg_m)):
            Tv = np.nan_to_num(T, nan=1e9)
            r = {'beat': bk, 'model': name, 'activated_pct': round(100 * float(np.isfinite(T).mean()), 2),
                 'total_activation_ms': round(float(np.nanmax(T)), 1)}
            r['t10_ms'], r['t50_ms'], r['t90_ms'] = frac_times(Tv, nvol)
            r.update(score(ecg, float(np.nanmax(T))))
            if name == 'monodomain':
                dif = Tm[ok] - Te[ok]
                r.update({'within_5ms_pct': round(100 * float((np.abs(dif) <= 5).mean()), 1),
                          'median_diff_ms': round(float(np.median(dif)), 2),
                          'junction_capture_lag_median_ms': round(float(np.median(lag)), 2),
                          'junction_capture_lag_p95_ms': round(float(np.percentile(lag, 95)), 2)})
            rows.append(r)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(HERE, 'results.csv'), index=False)
    txt = R.to_string(index=False)
    open(os.path.join(HERE, 'results.txt'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    if sys.argv[1] == 'test':
        run(sys.argv[2], test=True)
    elif sys.argv[1] == 'run':
        run(sys.argv[2])
    else:
        analyze()
