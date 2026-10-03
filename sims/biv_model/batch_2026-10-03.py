#!/usr/bin/env python
"""
Pilot batch driver, 2026-10-03 (Alex: "Run it all", 08:58 UTC). Detached and resumable.

Order:
  S0  site grid (11_site_grid.py) per heart, if missing
  S1  lead fields with the re-calibrated heart conductivities: normal mesh for all three
      hearts, LBBB-like mesh for 6G8DD8S5, no-fast-layer mesh for all three
  S2  eikonal grid: 99 sites x 3 hearts (6G8DD8S5 uses the LBBB-like mesh)
  S3  monodomain agreement check: 9 sites per heart (LV free wall: the original LV
      mid-endocardial site + 50 % + 90 % depth; septum and RV free wall at z 0.5,
      10 / 50 / 90 %), plus the eikonal run of each original site (not in the grid)
  S4  no-fast-layer control: eikonal, all fast layers off, 99 sites x 3 hearts
Every beat: lead-field ECG through precomputed per-heart weights (13_fast_ecg.py,
validated against openCARP to 0.0002 mV), scored with ecg_depth_criteria in both onset
modes (10_measure_ecg.py, site's Bazan region). Eikonal beats never write a Vm file;
monodomain Vm files are deleted after their ECG (activation times are kept).
S2 and S4 run NPAR eikonal sites at once (EIK_THREADS OpenMP threads each; one eikonal run
peaks at ~1.6 GB); monodomain runs one at a time.

Files: runs/batch_2026-10-03/{driver.log, progress.jsonl, status.json}; one run folder
per beat under runs/. Resume: re-launch; finished items (criteria.json present) are
skipped. Pause: create runs/batch_2026-10-03/PAUSE; the driver stops before the next run.

Launch: setsid nohup python sims/biv_model/batch_2026-10-03.py > /dev/null 2>&1 &
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import subprocess
import sys
import time
import traceback

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
RUNS = os.path.join(REPO, 'runs')
BD = os.path.join(RUNS, 'batch_2026-10-03')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LBBB = {'6G8DD8S5'}
P = '2026-10-03b'
NPAR, EIK_THREADS = 3, 2
# 2026-10-03 session: Alex needs the PC back; no new site after this time (UTC, epoch s),
# S3 (monodomain check) and S4 (no-fast-layer control) deferred to the new PC.
NO_NEW_AFTER = float(os.environ.get('NO_NEW_AFTER_EPOCH', '0')) or None
STAGES = set(os.environ.get('BATCH_STAGES', 'S0,S1,S2,S3,S4').split(','))
PY = sys.executable
os.makedirs(BD, exist_ok=True)
ENV0 = dict(os.environ)
ENV0['PATH'] = '/usr/local/lib/opencarp/lib/petsc/bin:' + ENV0.get('PATH', '')


def log(msg):
    with open(os.path.join(BD, 'driver.log'), 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')


def progress(item, status, **kw):
    with open(os.path.join(BD, 'progress.jsonl'), 'a') as f:
        f.write(json.dumps({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'item': item, 'status': status, **kw}) + '\n')


def sh(args, heart, logfile):
    env = dict(ENV0, HEART=heart)
    with open(logfile, 'w') as f:
        subprocess.run([str(a) for a in args], cwd=B, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)


def paused():
    if NO_NEW_AFTER and time.time() > NO_NEW_AFTER:
        return True
    return os.path.exists(os.path.join(BD, 'PAUSE'))


def heart_dir(h):
    return os.path.join(REPO, 'data', 'biv', h)


def template_run(h):
    return os.path.join(RUNS, '2026-10-02_biv_fullqrs' if h == 'Y5HYEDL4' else f'2026-10-03_{h}_fullqrs')


def lf_dir(h, variant):
    return os.path.join(RUNS, f'{P}_LF_{h}_{variant}', 'POSTPROC_DIR')


def wfile(h, variant):
    return os.path.join(heart_dir(h), f'ecgW_{variant}.npz')


def score(h, ecg_run, last_act, region):
    out = os.path.join(RUNS, ecg_run, 'criteria.json')
    args = [PY, '10_measure_ecg.py', os.path.join(RUNS, ecg_run, 'POSTPROC_DIR'), '--stim-ms', 0,
            '--last-act-ms', last_act, '--out', out]
    if region:
        args += ['--region', region]
    sh(args, h, os.path.join(RUNS, ecg_run, 'measure.log'))
    return out


def eik_item(h, site, variant, nofast, tag):
    rid = f'{P}_{tag}_{h}_{site["id"]}'
    ecg = rid + '_ecg'
    if os.path.exists(os.path.join(RUNS, ecg, 'criteria.json')):
        return 'skip'
    os.makedirs(os.path.join(RUNS, rid), exist_ok=True)
    lvar = 'nofast' if nofast else ('lbbb' if variant == 'lbbb' else 'normal')
    args = [PY, '12_eikonal.py', '--mode', 'eik', '--ID', rid, '--site-node', site['node'],
            '--mesh-variant', variant, '--template-run', template_run(h), '--tend', 0,   # 0 = auto length
            '--np', EIK_THREADS, '--weights', wfile(h, lvar), '--ecg-dir', os.path.join(RUNS, ecg, 'POSTPROC_DIR')]
    if nofast:
        args.append('--no-fast-layer')
    sh(args, h, os.path.join(RUNS, rid, 'driver_eik.log'))
    s = json.load(open(os.path.join(RUNS, rid, 'summary_12.json')))
    score(h, ecg, s['total_activation_ms'], site.get('bazan_region'))
    return {'run': rid, 'total_activation_ms': s['total_activation_ms'], 'sim_wall_s': s['sim_wall_s']}


def mono_item(h, site, variant):
    rid = f'{P}_mono_{h}_{site["id"]}'
    ecg = rid + '_ecg'
    if os.path.exists(os.path.join(RUNS, ecg, 'criteria.json')):
        return 'skip'
    tend = 220 if variant == 'lbbb' else 160
    os.makedirs(os.path.join(RUNS, rid), exist_ok=True)
    sh([PY, '06_check_run.py', '--tend', tend, '--spacedt', 1, '--np', 6, '--ID', rid,
        '--site-node', site['node'], '--mesh-variant', variant], h, os.path.join(RUNS, rid, 'driver_mono.log'))
    s = json.load(open(os.path.join(RUNS, rid, 'summary_06.json')))
    last = s.get('total_activation_ms', s.get('latest_activation_so_far_ms'))
    lvar = 'lbbb' if variant == 'lbbb' else 'normal'
    W = np.load(wfile(h, lvar))['W'].astype(float)
    raw = np.fromfile(os.path.join(RUNS, rid, 'vm.igb'), dtype='<f4', offset=1024)
    vm = raw.reshape(-1, W.shape[1])
    e = vm.astype(float) @ W.T
    d = os.path.join(RUNS, ecg, 'POSTPROC_DIR'); os.makedirs(d, exist_ok=True)
    tt = np.arange(e.shape[0], dtype=float)
    for j, l in enumerate(['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']):
        np.savetxt(os.path.join(d, f'ECG_{l}.dat'), np.c_[tt, e[:, j]], fmt='%g %.6g')
    del raw, vm
    os.remove(os.path.join(RUNS, rid, 'vm.igb'))
    score(h, ecg, last, site.get('bazan_region'))
    return {'run': rid, 'total_activation_ms': last, 'activated_fraction': s['activated_fraction']}


def lf_item(h, variant):
    rid = f'{P}_LF_{h}_{variant}'
    if os.path.exists(os.path.join(RUNS, rid, 'POSTPROC_DIR', 'LF_V6.igb')):
        return 'skip'
    full = {'normal': 'full', 'lbbb': 'full_lbbb', 'nofast': 'full_nofast'}[variant]
    os.makedirs(os.path.join(RUNS, rid), exist_ok=True)
    sh([PY, '08_torso.py', 'leadfield', '--vm', os.path.join(template_run(h), 'vm.igb'), '--run-id', rid,
        '--ecg-dt', 1, '--tend', 140, '--full', full], h, os.path.join(RUNS, rid, 'driver_lf.log'))
    return {'run': rid}


def w_item(h, variant):
    if os.path.exists(wfile(h, variant)):
        return 'skip'
    mesh = os.path.join(heart_dir(h), 'bivF_lbbb' if variant == 'lbbb' else 'bivF')
    args = [PY, '13_fast_ecg.py', 'weights', '--mesh', mesh, '--lf-dir', lf_dir(h, variant), '--sigma', 'm',
            '--c', -1, '--out', wfile(h, variant)]
    if variant == 'nofast':
        args.append('--nofast')
    sh(args, h, os.path.join(BD, f'weights_{h}_{variant}.log'))
    return {'weights': wfile(h, variant)}


def agreement_sites(h, sites):
    by = {s['id']: s for s in sites}
    orig = json.load(open(os.path.join(template_run(h), 'summary_06.json')))['site_node']
    def pick(fam, pos, d):
        for s in sites:
            if s['family'] == fam and s['position'] == pos and s['level_z'] == 0.5 and int(s['depth_target'] * 100) == d:
                return s
        return None
    lvfw = [s for s in sites if s['family'] == 'lv_free_wall' and s['level_z'] == 0.5]
    pos180 = 'phi180' if any(s['position'] == 'phi180' for s in lvfw) else (lvfw[0]['position'] if lvfw else None)
    out = []
    o = dict(pick('lv_free_wall', pos180, 50) or {})
    o.update({'id': 'lv_free_wall_original_d0', 'node': orig, 'depth_target': 0.0})
    out.append(o)
    out += [pick('lv_free_wall', pos180, 50), pick('lv_free_wall', pos180, 90)]
    out += [pick('lv_septum', 'phi0', d) for d in (10, 50, 90)]
    out += [pick('rv_free_wall', 'q50', d) for d in (10, 50, 90)]
    return [s for s in out if s]


FAILS = {'consecutive': 0}


def run_item(name, fn, *a):
    if paused():
        log('PAUSE file found: not starting ' + name)
        return False
    t0 = time.time()
    try:
        r = fn(*a)
        if r == 'skip':
            return
        FAILS['consecutive'] = 0
        progress(name, 'ok', wall_s=round(time.time() - t0, 1), **(r if isinstance(r, dict) else {}))
        log(f'ok   {name} ({time.time() - t0:.0f} s)')
    except Exception as e:
        progress(name, 'failed', wall_s=round(time.time() - t0, 1), error=str(e)[:300])
        FAILS['consecutive'] += 1
        if FAILS['consecutive'] >= 5:          # systematic problem: pause instead of burning through sites
            open(os.path.join(BD, 'PAUSE'), 'w').write('auto-pause after 5 consecutive failures\n')
        log(f'FAIL {name}: {e}\n{traceback.format_exc()[-1500:]}')
    return True


def run_parallel(items):
    """items: list of (name, fn, args); NPAR at a time, in order; stops submitting on PAUSE."""
    with ThreadPoolExecutor(max_workers=NPAR) as ex:
        futs = []
        for name, fn, args in items:
            if paused():
                log('PAUSE file found: no further submissions')
                break
            futs.append(ex.submit(run_item, name, fn, *args))
            while sum(not f.done() for f in futs) >= NPAR:
                time.sleep(2)
        for f in futs:
            f.result()


def stop_if_paused():
    if paused():
        status('paused')
        log('paused')
        sys.exit(0)


def status(state):
    done = fail = 0
    if os.path.exists(os.path.join(BD, 'progress.jsonl')):
        for l in open(os.path.join(BD, 'progress.jsonl')):
            j = json.loads(l)
            done += j['status'] == 'ok'
            fail += j['status'] == 'failed'
    json.dump({'state': state, 'ok': done, 'failed': fail, 'time': time.strftime('%Y-%m-%d %H:%M:%S')},
              open(os.path.join(BD, 'status.json'), 'w'), indent=1)


def main():
    log(f'driver start (pid {os.getpid()})')
    status('running')
    for h in HEARTS:                                                     # S0 / prep
        if not os.path.exists(os.path.join(heart_dir(h), 'sites.json')):
            run_item(f'S0 sites {h}', lambda h=h: (sh([PY, '11_site_grid.py'], h, os.path.join(BD, f'sites_{h}.log')), {})[1])
        need = 'full_lbbb.elem' if h in LBBB else ('full_nofast.elem' if 'S4' in STAGES else None)
        if need and not os.path.exists(os.path.join(heart_dir(h), 'torso', need)):
            run_item(f'S0 variants {h}', lambda h=h: (sh([PY, '08_torso.py', 'variants'], h, os.path.join(BD, f'variants_{h}.log')), {})[1])
    for h in HEARTS:                                                     # S1
        vs = (['lbbb'] if h in LBBB else ['normal'])
        if 'S3' in STAGES and h in LBBB:
            vs = vs + []
        if 'S4' in STAGES:
            vs = vs + (['normal'] if h in LBBB else []) + ['nofast']
        for v in vs:
            run_item(f'S1 LF {h} {v}', lf_item, h, v)
            run_item(f'S1 weights {h} {v}', w_item, h, v)
            stop_if_paused()
    sites = {h: json.load(open(os.path.join(heart_dir(h), 'sites.json'))) for h in HEARTS}
    if 'S2' in STAGES:
      run_parallel([(f'S2 eik {h} {s["id"]}', eik_item, (h, s, 'lbbb' if h in LBBB else 'normal', False, 'eik'))
                  for h in HEARTS for s in sites[h]])                    # S2
    stop_if_paused()
    status('running')
    for h in (HEARTS if 'S3' in STAGES else []):                          # S3
        var = 'lbbb' if h in LBBB else 'normal'
        ag = agreement_sites(h, sites[h])
        run_item(f'S3 eik {h} original', eik_item, h, ag[0], var, False, 'eik')
        for s in ag:
            run_item(f'S3 mono {h} {s["id"]}', mono_item, h, s, var)
            stop_if_paused()
        status('running')
    if 'S4' in STAGES:
      run_parallel([(f'S4 nofast {h} {s["id"]}', eik_item, (h, s, 'normal', True, 'nofast'))
                     for h in HEARTS for s in sites[h]])                 # S4
    stop_if_paused()
    status('stopped at deadline' if (NO_NEW_AFTER and time.time() > NO_NEW_AFTER) else 'done')
    log('driver done')


if __name__ == '__main__':
    main()
