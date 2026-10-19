"""Decision 8 conductivity sensitivity on the frozen v5.1 model (Alex, 19 Oct 2026 17:58:45 UTC: "2" = run it now).
Sensitivity only: nothing is adopted, no v5.1 file is changed.

Sensitivity set (v5.1 brief, decision 8): fibre sigma_i 0.174, sigma_e 0.625 S/m as v5.1; in each cross-fibre direction d
sigma_e,d = 0.236 S/m, and sigma_i,d solved so that sigma_m,d / sigma_m,fibre = (v_d / 0.60)^2 as in v5.1
(sigma_m = sigma_i sigma_e / (sigma_i + sigma_e)). Brief check values: control sheet sigma_i 0.0618, normal 0.1381;
HF 0.0287, 0.0521 S/m. Blood 0.7 and torso 0.2 S/m as v5.1. v5.1 uses equal anisotropy (both scaled by (v_d / 0.60)^2).
Stages (one heart at a time, run alone; same openCARP job as conductor51.py leadfield / weights, only the heart
conductivities differ; 2 processes, light AMG options, memory watchdog at 900 MB):
  HEART=<H> python -B .../sens51.py leadfield   -> runs/v51_2026-10-15/10_conductor_sens/<H>/leadfield_sens
  HEART=<H> python -B .../sens51.py weights     -> runs/v51_2026-10-15/10_conductor_sens/<H>/ecgW_sens.npz (sigma_i source,
                                                   as v5.1), after the C9 check of the sigma_m weights against openCARP
  python -B .../sens51.py tensors               -> sigma_sens.json in this folder (the set, with the check values)
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

SIG_E_CROSS = 0.236
CHECK = {'Y5HYEDL4': {'sheet': 0.0618, 'normal': 0.1381}, '6G8DD8S5': {'sheet': 0.0287, 'normal': 0.0521}}
CHECK['7D98EVAR'] = CHECK['6G8DD8S5']
OUT = os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens')


def sigma_sens(h):
    sp = C51.SPEEDS[h]
    sm_f = C51.SIG_I * C51.SIG_E / (C51.SIG_I + C51.SIG_E)
    s = {'fibre': {'gi': C51.SIG_I, 'ge': C51.SIG_E}}
    for a in ('sheet', 'normal'):
        sm = sm_f * (sp[a] / C51.V_REF) ** 2
        s[a] = {'gi': sm * SIG_E_CROSS / (SIG_E_CROSS - sm), 'ge': SIG_E_CROSS}
        assert round(s[a]['gi'], 4) == CHECK[h][a], (h, a, s[a])
    sm = {a: s[a]['gi'] * s[a]['ge'] / (s[a]['gi'] + s[a]['ge']) for a in s}
    assert max(abs(sm[a] / sm['fibre'] - (sp[a] / C51.V_REF) ** 2) for a in s) <= 1e-9
    return s


def tensors():
    out = {'rule': __doc__.split('\n\n')[1].replace('\n', ' '), 'hearts': {h: sigma_sens(h) for h in C51.SPEEDS},
           'v51_for_comparison': {h: C51.sigma(h) for h in C51.SPEEDS}}
    json.dump(out, open(os.path.join(HERE, 'sigma_sens.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


def lf_dir(h):
    return os.path.join(OUT, h, 'leadfield_sens')


def leadfield(np_=2, min_mb=900):
    """conductor51.leadfield() with the sensitivity conductivities and its own run folder."""
    import signal
    import subprocess
    h = os.environ['HEART']
    CD = C51.biv_module('cd', '15_conductor.py', h)
    assert CD.HEART == h
    from carputils.leadfield import leadfield_setup
    sg = sigma_sens(h)
    rid = lf_dir(h)
    os.makedirs(os.path.join(rid, 'POSTPROC_DIR'), exist_ok=True)
    vm = CD.small_vm(rid)
    g = ['-num_gregions', 3, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', sg['fibre']['gi'], '-gregion[0].g_el', sg['fibre']['ge'],
         '-gregion[0].g_it', sg['sheet']['gi'], '-gregion[0].g_et', sg['sheet']['ge'],
         '-gregion[0].g_in', sg['normal']['gi'], '-gregion[0].g_en', sg['normal']['ge'],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', C51.TAG_TORSO, '-gregion[2].num_IDs', 1, '-gregion[2].ID[0]', C51.TAG_BLOOD]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', C51.G_TORSO, f'-gregion[1].g_e{k}', C51.G_TORSO, f'-gregion[2].g_i{k}', C51.G_BLOOD, f'-gregion[2].g_e{k}', C51.G_BLOOD]
    phys = ['-num_phys_regions', 2, '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', 1, '-phys_region[0].ID[0]', 1,
            '-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', 3, '-phys_region[1].ID[0]', 1, '-phys_region[1].ID[1]', C51.TAG_TORSO,
            '-phys_region[1].ID[2]', C51.TAG_BLOOD]
    stim, elec, opts = leadfield_setup(12, C51.hd(h, 'torso', 'electrodes'), lf_vmfile=vm, ecg_timedt=10)
    env = dict(os.environ, PATH='/usr/local/lib/opencarp/lib/petsc/bin:' + os.environ.get('PATH', ''))
    res = {'run': rid, 'mesh': C51.hd(h, 'torso', 'full_nofast_blood_v51'), 'sigma_S_m': sg, 'g_blood': C51.G_BLOOD, 'g_torso': C51.G_TORSO,
           'np': np_, 'started': time.strftime('%Y-%m-%d %H:%M:%S'), 'parts': {}}
    rf = os.path.join(HERE, f'leadfield_sens_{h}.json')
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        sub = os.path.join(rid, part)
        if all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            res['parts'][part] = 'exists'
            continue
        os.makedirs(sub, exist_ok=True)
        cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', C51.hd(h, 'torso', 'full_nofast_blood_v51'), '-simID', sub,
               '-bidomain', 0, '-dt', 10, '-tend', 10, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
               '-imp_region[0].num_IDs', 1, '-imp_region[0].ID[0]', 1] + g + phys \
            + CD.lead_subset(stim, elec, names) + opts + ['-ellip_options_file', C51.OPTS]
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
        print(part, r, flush=True)
        if killed or p.returncode or not all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            json.dump(res, open(rf, 'w'), indent=1, default=str)
            raise RuntimeError(json.dumps(res, default=str))
    pp = os.path.join(rid, 'POSTPROC_DIR')
    Z = {}
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        for n in names:
            b = open(os.path.join(rid, part, 'POSTPROC_DIR', f'LF_{n}.igb'), 'rb').read()
            hdr, Z[n] = b[:1024], np.frombuffer(b[1024:], dtype='<f4').copy()
            open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(b)
            e = os.path.join(rid, part, 'POSTPROC_DIR', f'ECG_{n}.dat')
            if os.path.exists(e):
                open(os.path.join(pp, f'ECG_{n}.dat'), 'w').write(open(e).read())
    for n, z in (('aVR', -(Z['I'] + Z['II']) / 2), ('aVL', Z['I'] - Z['II'] / 2), ('aVF', Z['II'] - Z['I'] / 2)):
        open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(hdr + z.astype('<f4').tobytes())
    res['lf_files'] = sorted(f for f in os.listdir(pp) if f.startswith('LF_'))
    res['finished'] = time.strftime('%Y-%m-%d %H:%M:%S')
    json.dump(res, open(rf, 'w'), indent=1, default=str)
    print(json.dumps(res, default=str), flush=True)


def weights():
    """conductor51.weights() with the sensitivity conductivities: C9 check (sigma_m weights vs openCARP's ECG of the
    lead-field runs within 0.0002 mV), then sigma_i weights to runs/.../10_conductor_sens/<H>/ecgW_sens.npz."""
    h = os.environ['HEART']
    FE = C51.biv_module('fe', '13_fast_ecg.py', h)
    sg = sigma_sens(h)
    pair = [(sg[a]['gi'], sg[a]['ge']) for a in ('fibre', 'sheet', 'normal')]
    G = {'myo': pair, 'fast': pair}
    mesh = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'acceptance_c', 'mesh', 'biv51')
    pp = os.path.join(lf_dir(h), 'POSTPROC_DIR')
    vm = FE.igb(os.path.join(lf_dir(h), 'vm_first10ms.igb'))
    out = {'heart': h, 'mesh': mesh, 'lf_dir': pp, 'sigma_S_m': sg}
    Wm = FE.weights(mesh, pp, G, 'm', -1.0, True)
    mine = FE.project(Wm, vm)
    comp = {}
    for i, l in enumerate(C51.LEADS):
        f = os.path.join(pp, f'ECG_{l}.dat')
        if os.path.exists(f):
            d = np.loadtxt(f)
            k = np.rint(d[:, 0] / 1.0).astype(int)
            ok = k < len(mine)
            comp[l] = {'max_abs_err_mV': float(np.abs(mine[k[ok], i] - d[ok, 1]).max()), 'ref_peak_mV': float(np.abs(d[ok, 1]).max())}
    err = max(c['max_abs_err_mV'] for c in comp.values())
    out['C9_sigma_m_vs_openCARP'] = comp
    out['C9_max_abs_err_mV'] = err
    out['C9_pass_0.0002mV'] = bool(err <= 0.0002)
    Wi = FE.weights(mesh, pp, G, 'i', -1.0, True)
    wf = os.path.join(OUT, h, 'ecgW_sens.npz')
    np.savez(wf, W=Wi.astype(np.float32), sigma='i', c=-1.0, lf_dir=pp, mesh=mesh, nofast=True,
             conductor='v51 sensitivity (decision 8: cross-fibre sigma_e 0.236)', ecg_source='sigma_i, as v5.1')
    W5 = np.load(C51.hd(h, 'ecgW_v51.npz'))['W'].astype(float)
    out['weights_rel_change_median'] = float(np.median(np.abs(Wi - W5)[np.abs(W5) > 1e-12] / np.abs(W5[np.abs(W5) > 1e-12])))
    out['written'] = wf
    json.dump(out, open(os.path.join(HERE, f'weights_sens_{h}.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'C9_sigma_m_vs_openCARP'}, indent=1))
    if not out['C9_pass_0.0002mV']:
        sys.exit('C9 failed')


if __name__ == '__main__':
    {'tensors': tensors, 'leadfield': leadfield, 'weights': weights}[sys.argv[1]]()
