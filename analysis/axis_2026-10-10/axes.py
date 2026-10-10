"""Frontal QRS axis (least squares over the limb leads, net amplitude and area, as 14_purkinje.frontal_axis) of the
network-v3 normal beat and 7 paced sites of the control heart, for several lead-field sets (10 Oct 2026).
ECG = W @ pseudo-Vm (template beat shifted to each node's activation time), W from 13_fast_ecg.py weights
(sigma m, c -1, no fast layer; the source term keeps the study's calibrated conductivities).
Limb leads only (I, II, III lead fields; aVR, aVL, aVF derived), so LF_CONFIG=3 runs work.
Usage: python axes.py name=<LF POSTPROC_DIR> [name=<dir> ...]  -> axes.json, axes.md here"""
import importlib.util
import json
import os
import sys

import numpy as np

B = '/home/alex/vt-exit-depth/sims/biv_model'
sys.path.insert(0, B)
from common import OUT, REPO  # noqa: E402

spec = importlib.util.spec_from_file_location('fe', os.path.join(B, '13_fast_ecg.py'))
fe = importlib.util.module_from_spec(spec); spec.loader.exec_module(fe)
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(REPO, 'runs')
ANG = np.radians([0, 60, 120, -150, -30, 90])
BEATS = {'normal beat (His, network v3)': '2026-10-08_purk_sinus5_Y5HYEDL4'}
for s in ('rvot_septal_z_d50', 'rvot_free_wall_z_d50', 'aortic_cusp_rcc_z_d50', 'aortic_cusp_lcc_z_d50',
          'lv_summit_superior_z_d50', 'lv_free_wall_phi180_z0.5_d50', 'rv_free_wall_q50_z0.5_d50'):
    BEATS[s] = f'2026-10-07_purk_Y5HYEDL4_{s}'


def igb_all(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def act(run):
    s = json.load(open(os.path.join(R, run, 'summary_12.json')))
    if s.get('mode') == 'graph_fallback':
        return np.load(os.path.join(R, run, 'act_graph.npy')).astype(float)
    return igb_all(os.path.join(R, run, 'act.igb'))[-1].astype(float)


def axis(ecg, t, t0, t1):
    y = ecg[:, :6] - ecg[0, :6]
    m = (t >= t0) & (t <= t1)
    A = np.c_[np.cos(ANG), np.sin(ANG)]
    out = {}
    for nm, val in (('net', y[m].max(0) + y[m].min(0)), ('area', y[m].sum(0))):
        c, *_ = np.linalg.lstsq(A, val, rcond=None)
        out[nm] = int(round(float(np.degrees(np.arctan2(c[1], c[0])))))
    out['limb_net_mV'] = dict(zip(fe.LEADS[:6], np.round(y[m].max(0) + y[m].min(0), 2).tolist()))
    return out


cal = json.load(open(os.path.join(OUT, 'calibration.json')))
K = fe.stiffness(os.path.join(OUT, 'bivF'), fe.conductivities(cal), 'm', nofast=True)    # source term, as ecgW_nofast
Ws = {}
for kv in sys.argv[1:]:                  # limb leads only: I, II, III from LF files; aVR, aVL, aVF derived
    name, d = kv.split('=', 1)
    w = {l: -(K @ igb_all(os.path.join(d, f'LF_{l}.igb'))[-1].astype(float)) for l in ('I', 'II', 'III')}
    w['aVR'] = -(w['I'] + w['II']) / 2; w['aVL'] = (w['I'] - w['III']) / 2; w['aVF'] = (w['II'] + w['III']) / 2
    Ws[name] = np.stack([w[l] for l in fe.LEADS[:6]]).astype(np.float32)
del K
tr = os.path.join(R, '2026-10-02_biv_fullqrs')
lat0 = np.loadtxt(os.path.join(tr, 'init_acts_LATs-thresh.dat')); k = int(np.argmin(np.abs(lat0 - 60)))
v0 = igb_all(os.path.join(tr, 'vm.igb'))[:, k].astype(float); tt = np.arange(len(v0), dtype=float) - lat0[k]
res = {}
for name, run in BEATS.items():
    T = act(run)
    t = np.arange(0, np.ceil(T.max() + 20) + 0.5, 1.0)
    ecg = {n: np.zeros((len(t), 6)) for n in Ws}
    for i0 in range(0, len(T), 50000):
        sl = slice(i0, i0 + 50000)
        vm = np.interp((t[:, None] - T[None, sl]).ravel(), tt, v0).reshape(len(t), -1).astype(np.float32)
        for n, W in Ws.items():
            ecg[n] += vm @ W[:, sl].T
    res[name] = {n: axis(e, t, T.min(), T.max() + 3) for n, e in ecg.items()}
    print(name, {n: (a['net'], a['area']) for n, a in res[name].items()}, flush=True)
json.dump(res, open(os.path.join(HERE, 'axes.json'), 'w'), indent=1)
with open(os.path.join(HERE, 'axes.md'), 'w') as f:
    f.write('| beat | ' + ' | '.join(f'{n} net / area' for n in Ws) + ' |\n|---|' + '---|' * len(Ws) + '\n')
    for name in res:
        f.write(f'| {name} | ' + ' | '.join(f"{res[name][n]['net']} / {res[name][n]['area']}" for n in Ws) + ' |\n')
