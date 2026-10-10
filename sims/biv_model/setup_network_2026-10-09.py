#!/usr/bin/env python
"""
Network prerequisites for the other two pilot hearts (9 Oct 2026; Alex chose the Purkinje network as the study's
conduction model, 15:39 UTC). Everything here is independent of the network's own parameters:

  1. no-fast-layer heart-torso mesh (08_torso.py variants), if missing
  2. no-fast-layer lead fields runs/2026-10-03b_LF_<HEART>_nofast (12 leads, 4 processes, ~14 min per heart on
     this PC) and ECG weights data/biv/<HEART>/ecgW_nofast.npz (as the control heart's, 7 Oct)
  3. three no-layer eikonal beats per heart, job-1 style (runs/2026-10-07_nofast_<HEART>_<site>, scored), at the
     sites 14_purkinje.py calib uses, then calib -> data/biv/<HEART>/purkinje/graph_scale.json

The His-driven check beat (14_purkinje.py sinus) is NOT run here: it depends on the network decisions still open
on 9 Oct (LBBB variant for 6G8DD8S5, Durrer recalibration).

Resumable: finished steps are skipped. Log: runs/jobs_2026-10-07/setup_network/driver.log (+ one log per step).
Usage (from the repo, environment as in CLAUDE.md):  python sims/biv_model/setup_network_2026-10-09.py [HEART ...]
"""

import importlib.util
import json
import os
import sys
import time

B = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('jobs', os.path.join(B, 'jobs_2026-10-07.py'))
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)
CALIB_SITES = ['lv_free_wall_phi180_z0.5_d10', 'lv_free_wall_phi180_z0.5_d90', 'rvot_septal_z_d50']


def step(b, name, fn):
    t0 = time.time()
    r = fn()
    b.log(('skip ' if r == 'skip' else 'ok   ') + f'{name} ({time.time() - t0:.0f} s)')
    b.progress(name, 'skip' if r == 'skip' else 'ok', wall_s=round(time.time() - t0, 1))


def main():
    hearts = sys.argv[1:] or ['7D98EVAR', '6G8DD8S5']
    b = jobs.batch()
    b.BD = os.path.join(jobs.JD, 'setup_network')
    os.makedirs(b.BD, exist_ok=True)
    b.NPAR = 3
    b.log(f'setup_network start (pid {os.getpid()}): {hearts}')
    for h in hearts:
        try:
            tor = os.path.join(jobs.heart_dir(h), 'torso')
            step(b, f'{h} variants', lambda: 'skip' if os.path.exists(os.path.join(tor, 'full_nofast.elem')) else
                 b.sh([b.PY, '08_torso.py', 'variants'], h, os.path.join(b.BD, f'variants_{h}.log')))
            step(b, f'{h} lead fields nofast', lambda: b.lf_item(h, 'nofast'))
            step(b, f'{h} weights nofast', lambda: b.w_item(h, 'nofast'))
            S = {s['id']: s for s in jobs.sites(h)}
            for sid in CALIB_SITES:
                step(b, f'{h} no-layer beat {sid}', lambda sid=sid: b.eik_item(h, S[sid], 'normal', True, 'nofast'))
            gs = os.path.join(jobs.heart_dir(h), 'purkinje', 'graph_scale.json')
            step(b, f'{h} calib', lambda: 'skip' if os.path.exists(gs) else
                 b.sh([b.PY, '14_purkinje.py', 'calib'], h, os.path.join(b.BD, f'calib_{h}.log')))
            b.log(f'{h} ready: k = {json.load(open(gs))["k"]:.4f}')
        except Exception as e:                       # stop this heart, try the next
            b.log(f'FAIL {h}: {e}')
            b.progress(f'{h} setup', 'failed', error=str(e)[:300])
    b.log('setup_network stop')


if __name__ == '__main__':
    main()
