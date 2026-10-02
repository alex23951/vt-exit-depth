#!/usr/bin/env python
"""
Tune the fast endocardial layer conductivity inside the wedge so that the
MEASURED speed along the endocardium equals a target.

Measurement: endo-point stimulus at mid apex-to-base (y = 0); speed =
(15 mm - 5 mm) / (LAT at y = 15 mm - LAT at y = 5 mm), LATs averaged over the
endocardial-surface nodes (z = -5 mm) at each y. Both points lie inside the layer
(layer spans y = -20..20 mm).

Update rule: CV ~ sqrt(g), so g <- g * (target / measured)^2, with gi and ge scaled
together (fixed gi:ge ratio, as tuneCV does). Each iteration is one wedge run
(sims/wedge_aniso/run.py) with ID <prefix>_it<k>.

Usage (from runs/):
  python ../sims/wedge_aniso/tune_fast_layer.py --target 2.0 --resolution 500 \
      --tune-f T/tune_v0.6.json --tune-s T/tune_v0.4.json --tune-n T/tune_v0.45.json \
      --start T/tune_v2.0.json --prefix 2026-10-02_fastcal_500um_v2.0
"""

import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def measure(run_id):
    par = open(os.path.join(run_id, 'parameters.par')).read()
    mesh = re.search(r'meshname\s*=\s*(\S+)', par).group(1)
    pts = np.loadtxt(mesh + '.pts', skiprows=1) / 1e3
    act = np.loadtxt(os.path.join(run_id, 'init_acts_LATs-thresh.dat'))
    endo = np.abs(pts[:, 2] - pts[:, 2].min()) < 1e-3

    def lat(y):
        s = endo & (np.abs(pts[:, 1] - y) < 1e-3)
        return act[s].mean()

    t5, t15 = lat(5.0), lat(15.0)
    return 10.0 / (t15 - t5), t5, t15


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--target', type=float, required=True, help='target measured CV [m/s]')
    p.add_argument('--resolution', type=float, default=500.)
    p.add_argument('--tune-f', required=True)
    p.add_argument('--tune-s', required=True)
    p.add_argument('--tune-n', required=True)
    p.add_argument('--start', required=True, help='tuneCV-style json with starting gi/ge')
    p.add_argument('--prefix', required=True, help='run ID prefix')
    p.add_argument('--tol', type=float, default=0.01, help='relative tolerance')
    p.add_argument('--maxit', type=int, default=8)
    p.add_argument('--np', type=int, default=4)
    p.add_argument('--stim-strength', type=float, default=200.)
    a = p.parse_args()

    with open(a.start) as f:
        g = json.load(f)['results']
    gi, ge = g['gi'], g['ge']
    hist = []
    for k in range(a.maxit):
        run_id = f'{a.prefix}_it{k}'
        gfile = f'{run_id}_g.json'
        with open(gfile, 'w') as f:
            json.dump({'results': {'gi': gi, 'ge': ge},
                       'params': {'velocity': a.target, 'note': 'in-wedge tuned fast layer'}}, f, indent=1)
        cmd = [sys.executable, os.path.join(HERE, 'run.py'),
               '--resolution', str(a.resolution),
               '--tune-f', a.tune_f, '--tune-s', a.tune_s, '--tune-n', a.tune_n,
               '--tune-fast', gfile, '--stim', 'endo-point',
               '--stim-strength', str(a.stim_strength), '--duration', '25',
               '--np', str(a.np), '--ID', run_id, '--overwrite-behaviour', 'overwrite']
        with open(run_id + '.log', 'w') as log:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
        cv, t5, t15 = measure(run_id)
        if t5 < 0 or t15 < 0:
            sys.exit(f'{run_id}: no capture / no propagation to the measuring points; '
                     'try a stronger --stim-strength')
        hist.append({'it': k, 'gi': gi, 'ge': ge, 'cv': float(cv), 'lat5': float(t5), 'lat15': float(t15)})
        print(f'it{k}: gi={gi:.4f} ge={ge:.4f} -> measured {cv:.3f} m/s (LAT 5 mm {t5:.2f}, 15 mm {t15:.2f})', flush=True)
        if abs(cv - a.target) / a.target < a.tol:
            break
        f = (a.target / cv) ** 2
        gi, ge = gi * f, ge * f
    with open(f'{a.prefix}_result.json', 'w') as f:
        json.dump({'target': a.target, 'resolution': a.resolution, 'history': hist,
                   'converged': bool(abs(hist[-1]['cv'] - a.target) / a.target < a.tol),
                   'results': {'gi': hist[-1]['gi'], 'ge': hist[-1]['ge'], 'vel': hist[-1]['cv']},
                   'params': {'velocity': a.target}}, f, indent=1)


if __name__ == '__main__':
    main()
