"""Decision 8 sensitivity: the Step 6 pilot beats' ECGs with the sensitivity ECG weights (sens51.py weights), for a full
Table A rerun with copies of the Step 6 scoring scripts (path changes only; copies.diff in this folder).

Activation maps are the Step 6 ones (runs/v51_2026-10-15/06_pilot_rerun/maps/<dir>/<site>.T.npy, linked, not copied);
only the weights change: ECG = 15_conductor.py ecg_of(T, t, W_sens, template) on the stored ECG's own time axis
(0, 1, ... ms, same length), float32 as stored. Check first, per heart: the same code with the v5.1 weights reproduces the
stored Step 6 ECG of the His beat (max difference reported).
Writes runs/v51_2026-10-15/10_conductor_sens/maps/<dir>/ (<site>.ecg.npy new, <site>.T.npy symlinks) and
ecg_sens51.json in this folder. Usage (repo root, venv): python -B analysis/v51_2026-10-15/10_conductor_sens/sens_ecg51.py
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
import conductor51 as C51                                             # noqa: E402

SRC = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps')
DST = os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', 'maps')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']


def ecg_chunked(T, t, W, tm, step=20000):
    ecg = np.zeros((len(t), W.shape[0]))
    for i0 in range(0, len(T), step):
        sl = slice(i0, i0 + step)
        rel = t[:, None] - T[None, sl]
        ecg += np.interp(rel.ravel(), tm.t, tm.v, left=tm.v[0], right=tm.v[-1]).reshape(rel.shape) @ W[:, sl].T
    return ecg


def main():
    out, t0 = {'hearts': {}}, time.time()
    for h in HEARTS:
        sys.modules.pop('common', None)
        CD = C51.biv_module('cd', '15_conductor.py', h)
        assert CD.HEART == h
        tm = CD.Template()
        Ws = np.load(os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', h, 'ecgW_sens.npz'))['W'].astype(float)
        W5 = np.load(C51.hd(h, 'ecgW_v51.npz'))['W'].astype(float)
        his = os.path.join(SRC, h, 'his_driven')
        st = np.load(his + '.ecg.npy').astype(float)
        chk = float(np.abs(ecg_chunked(np.load(his + '.T.npy').astype(float), np.arange(len(st), dtype=float), W5, tm) - st).max())
        assert chk < 1e-3, (h, chk)
        res = {'check_v51_weights_vs_stored_his_ecg_max_abs_mV': chk, 'dirs': {}}
        for d in sorted(x for x in os.listdir(SRC) if x == h or x.startswith(h + '_')):
            sd, dd = os.path.join(SRC, d), os.path.join(DST, d)
            os.makedirs(dd, exist_ok=True)
            n_ecg = 0
            for f in sorted(os.listdir(sd)):
                if f.endswith('.T.npy'):
                    link = os.path.join(dd, f)
                    if not os.path.lexists(link):
                        os.symlink(os.path.join(sd, f), link)
                    site = f[:-len('.T.npy')]
                    se = os.path.join(sd, site + '.ecg.npy')
                    if os.path.exists(se):
                        stored = np.load(se)
                        T = np.load(os.path.join(sd, f)).astype(float)
                        e = ecg_chunked(T, np.arange(len(stored), dtype=float), Ws, tm)
                        np.save(os.path.join(dd, site + '.ecg.npy'), e.astype(stored.dtype))
                        n_ecg += 1
            res['dirs'][d] = {'ecg_written': n_ecg}
            print(h, d, n_ecg, f'{time.time() - t0:.0f} s', flush=True)
        out['hearts'][h] = res
    out['wall_s'] = round(time.time() - t0)
    json.dump(out, open(os.path.join(HERE, 'ecg_sens51.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
