"""Step 6 (v5.1 brief): the pilot grids on v5.1. Same sites.json, families and pairs as 13 Oct; v5.1 solver (heart51.Heart51:
nodal graph tissue, v5.1 network, junction 4 / 2 ms, v5.1 sigma_i ECG weights, pseudo-Vm template). Per heart: the His beat
and the 144 paced sites (network); the control heart also its 144 no-network beats (tissue only, v5.1 speeds and fibres).
Saves <site>.T.npy (float32 activation, ms) and <site>.ecg.npy (float32 (n, 12), 1 ms, t = 0 at the stimulus / His) in
runs/v51_2026-10-15/06_pilot_rerun/maps/<H>[_nonet]/, the same layout as the 14 Oct v5 maps, so the 0.4.0 rescore code runs
on them unchanged apart from paths. Resumable (skips saved beats).
Usage (repo root, venv): HEART=<H> python -B analysis/v51_2026-10-15/06_pilot_rerun/grid51.py [nonet] [--limit N]
"""
import json
import os
import resource
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
import heart51 as H51                                                   # noqa: E402


def mem_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


def main():
    h = os.environ['HEART']
    nonet = 'nonet' in sys.argv
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None
    t0 = time.time()
    H = H51.Heart51(h)
    t_setup = time.time() - t0
    d = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps', h + ('_nonet' if nonet else ''))
    os.makedirs(d, exist_ok=True)
    S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
    todo = ([] if nonet else [None]) + S
    n, times = 0, []
    for s in todo:
        sid = 'his_driven' if s is None else s['id']
        if os.path.exists(os.path.join(d, f'{sid}.ecg.npy')):
            continue
        if limit is not None and n >= limit:
            break
        if mem_mb() < 700:
            sys.exit(f'stopped: available memory {mem_mb():.0f} MB (resumable)')
        t1 = time.time()
        T = H.solve(None if s is None else int(s['node']), nonet=nonet)
        if not np.isfinite(T).all():
            sys.exit(f'{sid}: {int((~np.isfinite(T)).sum())} unactivated nodes')
        t, ecg = H.ecg(T)
        np.save(os.path.join(d, f'{sid}.T.npy'), T.astype(np.float32)); np.save(os.path.join(d, f'{sid}.ecg.npy'), ecg.astype(np.float32))
        times.append(time.time() - t1); n += 1
    out = {'heart': h, 'nonet': nonet, 'beats_done_now': n, 'setup_s': round(t_setup, 1), 'per_beat_s_median': round(float(np.median(times)), 2) if times else None,
           'wall_s': round(time.time() - t0, 1), 'peak_rss_MB': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024), 'keys': H.keys}
    print(json.dumps(out, default=str), flush=True)


if __name__ == '__main__':
    main()
