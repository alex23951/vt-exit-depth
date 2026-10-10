#!/usr/bin/env python
"""
Step 15 (10 Oct 2026; Alex "Yes", 09:10 UTC): realistic volume conductor for the lead-field ECG ("cb" = Clerc + blood).

Why (LABNOTES 9-10 Oct, superior-axis thread): the study's lead fields used the heart conductivities tuned for the
monodomain conduction velocity at ~1 mm (calibration.json, 3.9-4.2x Clerc 1976: a numerical compensation, not tissue
values) and torso conductivity (0.2 S/m) inside the ventricular cavities. On the control heart that made the His-driven
normal beat's frontal axis -98 deg; with the heart at Clerc scale and blood at 0.7 S/m it is +64 deg, and the paced
outflow / cusp / summit axes stay inferior.

Conductor cb:
  heart   every g_i and g_e of calibration.json divided by s = g_e,fibre / 0.625, so the fibre values equal
          Clerc 1976 (0.174 / 0.625 S/m); sheet and sheet-normal keep the calibrated anisotropy. s = 4.08 / 4.20 / 3.86
          (Y5HYEDL4 / 7D98EVAR / 6G8DD8S5).
  blood   torso elements inside the ventricular cavities, tag 101, 0.7 S/m (Geddes & Baker 1967; Keller et al. 2010).
  torso   0.2 S/m, T13 electrodes, no fast layer (network arm): unchanged.
  source  the ECG source term (K in 13_fast_ecg.py, monodomain-equivalent sigma) uses the same scaled conductivities,
          so amplitudes are consistent with the conductor (1/s of the calibrated-source amplitude).
Activation, network, template beat and scoring are unchanged: only the ECG weights W change.

Stages (HEART=<id>, run from sims/biv_model; one at a time, PC otherwise idle: full-torso openCARP needs ~6.4 GB):
  blood      torso/full_nofast -> torso/full_nofast_blood.elem (+ .pts / .lon links): 1 mm voxels, wall = heart
             nodes and element centroids closed by one voxel; cavity = non-wall voxels inside the convex hull of the
             endocardial nodes with wall in all six axis directions (blood at the valve openings stays torso)
  leadfield  12-lead lead fields -> runs/2026-10-10_LF_<HEART>_cb/POSTPROC_DIR, in three runs of <= 3 leads (2 processes;
             a 12-lead run needs > 7 GB; aVR / aVL / aVF derived from I and II); elliptic solver
             analysis/axis_2026-10-10/ellip_amg_light.opts, validated against the study's lead fields to < 1e-7;
             openCARP is stopped if available memory falls below 900 MB)
  weights    -> data/biv/<HEART>/ecgW_nofast_cb.npz
  check      the rescoring path with the OLD weights must reproduce the stored ECG of 3 finished sites
  rescore    every finished network-grid site (jobs 8-10) and the His-driven beat: ECG from the saved activation map
             (same pseudo-Vm template and time axis) -> runs/<run>_ecg_cb/POSTPROC_DIR, scored by 10_measure_ecg.py
             with the same arguments -> runs/<run>_ecg_cb/criteria.json (resumable); normal-beat axes ->
             runs/<sinus run>_ecg_cb/axis.json
  csv        -> analysis/grids_2026-10-07/purk_<HEART>_cb.csv (same columns as purk_<HEART>.csv + conductor)
"""

import argparse
import csv
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time

import numpy as np
from scipy import ndimage
from scipy.spatial import Delaunay

from common import HEART, OUT, REPO, read_elem, read_pts, read_vtx

B = os.path.dirname(os.path.abspath(__file__))
TOR = os.path.join(OUT, 'torso')
RUNS = os.path.join(REPO, 'runs')
LF_RUN = f'2026-10-10_LF_{HEART}_cb'
WFILE = os.path.join(OUT, 'ecgW_nofast_cb.npz')
OPTS = os.path.join(REPO, 'analysis', 'axis_2026-10-10', 'ellip_amg_light.opts')
G_BLOOD, G_TORSO, TAG_BLOOD = 0.7, 0.2, 101
CLERC_GE_FIBRE = 0.625
JOB = {'Y5HYEDL4': 8, '6G8DD8S5': 9, '7D98EVAR': 10}[HEART]
SINUS = '2026-10-08_purk_sinus5_Y5HYEDL4' if HEART == 'Y5HYEDL4' else f'2026-10-09_purk_sinus_{HEART}'
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def module(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(B, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scaled_cal():
    cal = json.load(open(os.path.join(OUT, 'calibration.json')))
    s = cal['fibre']['ge'] / CLERC_GE_FIBRE
    out = json.loads(json.dumps(cal))
    for k in ('fibre', 'sheet', 'sheet_normal'):
        out[k]['gi'] = cal[k]['gi'] / s
        out[k]['ge'] = cal[k]['ge'] / s
    return out, s


def template_run():
    return os.path.join(RUNS, '2026-10-02_biv_fullqrs' if HEART == 'Y5HYEDL4' else f'2026-10-03_{HEART}_fullqrs')   # as batch_2026-10-03


def igb_all(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


# ------------------------------------------------------------------ blood
def blood():
    P = read_pts(os.path.join(TOR, 'full')) / 1e3
    E, tag = read_elem(os.path.join(TOR, 'full_nofast'))
    nh = int(open(os.path.join(OUT, 'bivF.pts')).readline())
    Ph = P[:nh]
    heart_el = tag != 100
    lv, rv = (read_vtx(os.path.join(OUT, 'surfaces', n + '.vtx')) for n in ('lv_endo', 'rv_endo'))
    lo = Ph.min(0) - 3; h = 1.0
    shape = tuple(int(x) for x in np.ceil((Ph.max(0) + 3 - lo) / h).astype(int) + 1)
    idx = lambda X: np.floor((X - lo) / h).astype(int)
    wall = np.zeros(shape, bool)
    for X in (Ph, P[E[heart_el]].mean(1)):
        i = idx(X); wall[i[:, 0], i[:, 1], i[:, 2]] = True
    wall = ndimage.binary_closing(wall, iterations=1) | wall
    enc = ~wall
    for ax in range(3):
        enc &= np.maximum.accumulate(wall, axis=ax) & np.flip(np.maximum.accumulate(np.flip(wall, ax), axis=ax), ax)
    cand = np.flatnonzero(enc.ravel())
    g = np.stack(np.unravel_index(cand, shape), 1) * h + lo + h / 2
    inside = Delaunay(Ph[np.unique(np.concatenate([lv, rv]))]).find_simplex(g) >= 0
    cav = np.zeros(enc.size, bool); cav[cand[inside]] = True; cav = cav.reshape(shape)
    tor = np.flatnonzero(~heart_el)
    i = idx(P[E[tor]].mean(1))
    ok = np.all((i >= 0) & (i < np.array(shape)), axis=1)
    bl = np.zeros(len(tor), bool); bl[ok] = cav[i[ok, 0], i[ok, 1], i[ok, 2]]
    new = tag.copy(); new[tor[bl]] = TAG_BLOOD
    x = P[E[tor[bl]]]
    vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    base = os.path.join(TOR, 'full_nofast_blood')
    with open(base + '.elem', 'w') as f:
        f.write(f'{len(E)}\n')
        np.savetxt(f, np.hstack([E, new[:, None]]), fmt='Tt %d %d %d %d %d')
    for ext in ('pts', 'lon'):
        if not os.path.exists(f'{base}.{ext}'):
            os.symlink(f'full.{ext}', f'{base}.{ext}')
    return {'blood_elements': int(bl.sum()), 'blood_ml': round(float(vol.sum() / 1e3), 1), 'voxels': list(shape)}


# ------------------------------------------------------------------ lead fields
def small_vm(run_dir):
    """First 10 ms of the heart's template beat (keeps openCARP's Vm projection small)."""
    out = os.path.join(run_dir, 'vm_first10ms.igb')
    src = os.path.join(template_run(), 'vm.igb')
    x = int(open(src, 'rb').read(1024).decode('latin1').split('x:')[1].split()[0])
    b = open(src, 'rb').read(1024 + 11 * x * 4)
    hd = b[:1024].decode('latin1')
    t0 = hd.split(' t:')[1].split()[0]; d0 = hd.split('dim_t:')[1].split()[0]
    hd = hd.replace(f' t:{t0} ', ' t:11 ', 1).replace(f'dim_t:{d0} ', 'dim_t:10 ', 1)
    hd = (hd + ' ' * 1024)[:1024].encode('latin1')
    open(out, 'wb').write(hd + b[1024:])
    return out


def lead_subset(stim, elec, names):
    """Keep only the stimuli (electrode terms) of the leads in names from leadfield_setup's 12-lead lists, renumbered."""
    d = {}
    for lst in (stim[2:], elec):
        for k, v in zip(lst[::2], lst[1::2]):
            i, key = k[len('-stim['):].split('].', 1)
            d.setdefault(int(i), {})[key] = v
    keep = [d[i] for i in sorted(d) if d[i]['name'] in names]
    out = ['-num_stim', len(keep)]
    for j, e in enumerate(keep):
        out += [x for key, v in e.items() for x in (f'-stim[{j}].{key}', v)]
    return out


def leadfield(np_=2, min_mb=900):
    """12-lead lead fields in three openCARP runs of <= 3 leads (I-III, V1-V3, V4-V6): memory grows with the number of
    leads and a 12-lead run tripped the 900 MB watchdog after 4 leads (~7 GB). aVR, aVL, aVF are linear combinations of
    I and II (aVR = -(I + II) / 2, aVL = I - II / 2, aVF = II - I / 2, up to a constant that the stiffness removes)."""
    from carputils.leadfield import leadfield_setup
    cal, s = scaled_cal()
    rid = os.path.join(RUNS, LF_RUN)
    os.makedirs(os.path.join(rid, 'POSTPROC_DIR'), exist_ok=True)
    vm = small_vm(rid)
    fast = (cal['fast_layer']['2.0']['gi'], cal['fast_layer']['2.0']['ge'])      # tag 2: empty in full_nofast_blood
    g = ['-num_gregions', 4, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', cal['fibre']['gi'], '-gregion[0].g_el', cal['fibre']['ge'],
         '-gregion[0].g_it', cal['sheet']['gi'], '-gregion[0].g_et', cal['sheet']['ge'],
         '-gregion[0].g_in', cal['sheet_normal']['gi'], '-gregion[0].g_en', cal['sheet_normal']['ge'],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2, '-gregion[2].num_IDs', 1, '-gregion[2].ID[0]', 100,
         '-gregion[3].num_IDs', 1, '-gregion[3].ID[0]', TAG_BLOOD]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', fast[0], f'-gregion[1].g_e{k}', fast[1], f'-gregion[2].g_i{k}', G_TORSO,
              f'-gregion[2].g_e{k}', G_TORSO, f'-gregion[3].g_i{k}', G_BLOOD, f'-gregion[3].g_e{k}', G_BLOOD]
    phys = ['-num_phys_regions', 2, '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1,
            '-phys_region[0].ID[1]', 2, '-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', 4, '-phys_region[1].ID[0]', 1,
            '-phys_region[1].ID[1]', 2, '-phys_region[1].ID[2]', 100, '-phys_region[1].ID[3]', TAG_BLOOD]
    stim, elec, opts = leadfield_setup(12, os.path.join(TOR, 'electrodes'), lf_vmfile=vm, ecg_timedt=10)
    env = dict(os.environ, PATH='/usr/local/lib/opencarp/lib/petsc/bin:' + os.environ.get('PATH', ''))
    res = {'run': rid, 'scale': s, 'g_blood': G_BLOOD, 'np': np_, 'parts': {}}
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        sub = os.path.join(rid, part)
        if all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            res['parts'][part] = 'exists'
            continue
        os.makedirs(sub, exist_ok=True)
        cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', os.path.join(TOR, 'full_nofast_blood'), '-simID', sub,
               '-bidomain', 0, '-dt', 10, '-tend', 10, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
               '-imp_region[0].num_IDs', 2, '-imp_region[0].ID[0]', 1, '-imp_region[0].ID[1]', 2] + g + phys \
            + lead_subset(stim, elec, names) + opts + ['-ellip_options_file', OPTS]
        t0, peak, killed = time.time(), 0, False
        with open(os.path.join(sub, 'openCARP.log'), 'w') as log:
            p = subprocess.Popen([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            while p.poll() is None:
                mi = dict(l.split(':') for l in open('/proc/meminfo').read().splitlines() if ':' in l)
                av = int(mi['MemAvailable'].split()[0]) // 1024; peak = max(peak, int(mi['MemTotal'].split()[0]) // 1024 - av)
                if av < min_mb:
                    os.killpg(p.pid, signal.SIGKILL); killed = True
                    break
                time.sleep(2)
            p.wait()
        r = {'wall_s': round(time.time() - t0), 'peak_used_mb': peak, 'watchdog_killed': killed, 'returncode': p.returncode}
        res['parts'][part] = r
        if killed or p.returncode or not all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            raise RuntimeError(json.dumps(res))
    pp = os.path.join(rid, 'POSTPROC_DIR')
    Z = {}
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        for n in names:
            f = os.path.join(rid, part, 'POSTPROC_DIR', f'LF_{n}.igb')
            b = open(f, 'rb').read()
            hdr, Z[n] = b[:1024], np.frombuffer(b[1024:], dtype='<f4').copy()
            open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(b)
    for n, z in (('aVR', -(Z['I'] + Z['II']) / 2), ('aVL', Z['I'] - Z['II'] / 2), ('aVF', Z['II'] - Z['I'] / 2)):
        open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(hdr + z.astype('<f4').tobytes())
    res['lf_files'] = sorted(f for f in os.listdir(pp) if f.startswith('LF_'))
    return res


# ------------------------------------------------------------------ weights / ECG
def weights():
    fe = module('fe', '13_fast_ecg.py')
    cal, s = scaled_cal()
    lf = os.path.join(RUNS, LF_RUN, 'POSTPROC_DIR')
    W = fe.weights(os.path.join(OUT, 'bivF'), lf, fe.conductivities(cal), 'm', -1.0, True)
    np.savez(WFILE, W=W.astype(np.float32), sigma='m', c=-1.0, lf_dir=lf, mesh=os.path.join(OUT, 'bivF'), nofast=True,
             conductor='cb', scale=s, g_blood=G_BLOOD)
    return {'written': WFILE, 'shape': list(W.shape), 'scale': s}


class Template:
    def __init__(self):
        tr = template_run()
        lat0 = np.loadtxt(os.path.join(tr, 'init_acts_LATs-thresh.dat'))
        self.k = int(np.argmin(np.abs(lat0 - 60)))
        self.v = igb_all(os.path.join(tr, 'vm.igb'))[:, self.k].astype(float)
        self.t = np.arange(len(self.v), dtype=float) - lat0[self.k]


def activation(run):
    s = json.load(open(os.path.join(RUNS, run, 'summary_12.json')))
    if s.get('mode') == 'graph_fallback':
        return np.load(os.path.join(RUNS, run, 'act_graph.npy')).astype(float), s
    return igb_all(os.path.join(RUNS, run, 'act.igb'))[-1].astype(float), s


def ecg_of(T, t, W, tm):
    ecg = np.zeros((len(t), W.shape[0]))
    for i0 in range(0, len(T), 50000):
        sl = slice(i0, i0 + 50000)
        rel = t[:, None] - T[None, sl]
        ecg += np.interp(rel.ravel(), tm.t, tm.v, left=tm.v[0], right=tm.v[-1]).reshape(rel.shape) @ W[:, sl].T
    return ecg


def stored_t(run):
    return np.loadtxt(os.path.join(RUNS, run + '_ecg', 'POSTPROC_DIR', 'ECG_I.dat'))[:, 0]


def write_ecg(d, t, ecg):
    os.makedirs(d, exist_ok=True)
    for j, l in enumerate(LEADS):
        np.savetxt(os.path.join(d, f'ECG_{l}.dat'), np.c_[t, ecg[:, j]], fmt='%g %.6g')


def grid_sites():
    jobs = module('jobs', 'jobs_2026-10-07.py')
    return jobs, [(s, rid) for _, _, _, s, _, rid in jobs.plan(JOB) if jobs.done(rid)]


def check():
    _, items = grid_sites()
    W = np.load(os.path.join(OUT, 'ecgW_nofast.npz'))['W'].astype(float)
    tm, out = Template(), {}
    for s, rid in items[:3]:
        T, _ = activation(rid)
        t = stored_t(rid)
        ref = np.stack([np.loadtxt(os.path.join(RUNS, rid + '_ecg', 'POSTPROC_DIR', f'ECG_{l}.dat'))[:, 1] for l in LEADS], 1)
        out[s['id']] = round(float(np.abs(ecg_of(T, t, W, tm) - ref).max()), 6)
    if max(out.values()) > 1e-3:
        raise RuntimeError(f'rescoring path does not reproduce the stored ECG: {out}')
    return {'max_abs_diff_mV_vs_stored_ecg': out}


def frontal_axis(d, t0, t1):
    ang = np.radians([0, 60, 120, -150, -30, 90])
    net, area = [], []
    for l in LEADS[:6]:
        x = np.loadtxt(os.path.join(d, f'ECG_{l}.dat'))
        y = x[:, 1] - x[0, 1]; m = (x[:, 0] >= t0) & (x[:, 0] <= t1)
        net.append(y[m].max() + y[m].min()); area.append(y[m].sum())
    A = np.c_[np.cos(ang), np.sin(ang)]
    out = {}
    for nm, val in (('net', net), ('area', area)):
        c, *_ = np.linalg.lstsq(A, np.array(val), rcond=None)
        out[f'frontal_axis_{nm}_deg'] = int(round(float(np.degrees(np.arctan2(c[1], c[0])))))
    out['limb_net_mV'] = dict(zip(LEADS[:6], np.round(net, 3).tolist()))
    return out


def rescore():
    jobs, items = grid_sites()
    W = np.load(WFILE)['W'].astype(float)
    tm = Template()
    env = dict(os.environ, HEART=HEART, ECG_PKG=os.path.join(REPO, 'code', 'ecg_depth_criteria'))
    t0, n_new = time.time(), 0
    # His-driven normal beat: axis with the old and the new conductor
    T, sm = activation(SINUS)
    t = stored_t(SINUS)
    d = os.path.join(RUNS, SINUS + '_ecg_cb', 'POSTPROC_DIR')
    write_ecg(d, t, ecg_of(T, t, W, tm))
    ax = {'run': SINUS, 'study': frontal_axis(os.path.join(RUNS, SINUS + '_ecg', 'POSTPROC_DIR'), T.min(), T.max() + 3),
          'cb': frontal_axis(d, T.min(), T.max() + 3)}
    json.dump(ax, open(os.path.join(RUNS, SINUS + '_ecg_cb', 'axis.json'), 'w'), indent=1)
    for s, rid in items:
        out = os.path.join(RUNS, rid + '_ecg_cb', 'criteria.json')
        if os.path.exists(out):
            continue
        T, sm = activation(rid)
        t = stored_t(rid)
        d = os.path.join(RUNS, rid + '_ecg_cb', 'POSTPROC_DIR')
        write_ecg(d, t, ecg_of(T, t, W, tm))
        args = [sys.executable, '10_measure_ecg.py', d, '--stim-ms', 0, '--last-act-ms', sm['total_activation_ms'], '--out', out]
        if s.get('bazan_region'):
            args += ['--region', s['bazan_region']]
        with open(os.path.join(RUNS, rid + '_ecg_cb', 'measure.log'), 'w') as f:
            subprocess.run([str(a) for a in args], cwd=B, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
        n_new += 1
    return {'sites': len(items), 'scored_now': n_new, 'wall_s': round(time.time() - t0), 'normal_beat_axis': ax}


def write_csv():
    jobs, items = grid_sites()
    rows = []
    for s, rid in items:
        cf = os.path.join(RUNS, rid + '_ecg_cb', 'criteria.json')
        if not os.path.exists(cf):
            continue
        sm = json.load(open(os.path.join(RUNS, rid, 'summary_12.json')))
        row = {'heart': HEART, 'method': 'purk', 'conductor': 'cb', 'run': rid, 'criteria_file': rid + '_ecg_cb/criteria.json',
               'total_activation_ms': sm.get('total_activation_ms'), 'sim_wall_s': sm.get('sim_wall_s')}
        row.update(s)
        row.update(jobs.flatten(json.load(open(cf))))
        rows.append(row)
    path = os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{HEART}_cb.csv')
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    return {'csv': path, 'rows': len(rows)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['blood', 'leadfield', 'weights', 'check', 'rescore', 'csv'])
    a = p.parse_args()
    res = {'blood': blood, 'leadfield': leadfield, 'weights': weights, 'check': check, 'rescore': rescore, 'csv': write_csv}[a.stage]()
    log = os.path.join(TOR, 'summary_15.json')
    allr = json.load(open(log)) if os.path.exists(log) else {}
    allr[a.stage] = res
    json.dump(allr, open(log, 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
