"""Read-only preview P7 (lock thread, relayed 21 Oct 2026 02:13 UTC): single cells at CL 1000 ms (and CL 600 ms), R1.1's
steady-state criterion; nothing is adopted.

Model: runs/v52_2026-10-20/04_cells/model/Tomek52b.model = openCARP's Tomek.model with GKr_b, GKs_b, GNaL_b, thL, Gto_b,
GK1_b, PNaK_b, Gncx_b exposed and four scale parameters added (sJup on the SERCA uptake terms Jupnp and Jupp, sJleak on
the leak JleaK, sCaMKa on CaMKa = CaMKb + CaMKt where it sets the phosphorylated fractions (the CaMKt equation keeps its
own (CaMKb + CaMKt)), sJrelNP on Cajsr_half in the non-phosphorylated release Jrel_inf_b only); at the defaults it
reproduces the built-in Tomek trace exactly (checked: max |Vm difference| 0.0 mV over 20 beats).
(a) GKr scale per cell type to reach the HF targets (288.61 ms ENDO, 281.61 ms EPI) with IKs at its control value; secant
    on log(scale), each evaluation restarted from the baseline CL 1000 steady state; then CL 600 from that state.
(b) Gomez 2014 (PLoS One 9:e106602, Table 1, ORd column) applied to ToR-ORd: INaL x1.80 (GNaL_b), tau_hL x1.80 (thL;
    thLp = 3 thL follows, as in ORd), Ito x0.40 (Gto_b), IK1 x0.68 (GK1_b), INaK x0.70 (PNaK_b), INab x1.00, INCX x1.75
    (Gncx_b: both INaCa_i and INaCa_ss), Jup (SERCA) x0.50 (sJup on the uptake terms, not the leak; ToR-ORd's Jup_b
    multiplies uptake minus leak), Jleak x1.30 (sJleak), CaMKa x1.50 (sCaMKa), the Ca sensitivity of Jrel,NP,inf x0.80
    (sJrelNP). The paper's Methods give no equation for that last factor; two readings are run: 'threshold x0.8' (Cajsr_half
    x 0.8, release more Ca-sensitive) and 'threshold / 0.8' (x 1.25, less sensitive). IKs and IKr unchanged.
Afterdepolarisations (mine): on each of the last two beats (1 ms trace), an EAD = dV/dt > +0.05 mV/ms for >= 2 ms between
the AP peak + 20 ms and the APD90 crossing while V > -60 mV; a failure to repolarise = no APD90 crossing before the next
stimulus; a DAD = V rising > 5 mV above the diastolic minimum after repolarisation and before the next stimulus.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/04_cells/cell52_p7.py
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cell52 as C                                                                          # noqa: E402

RUN = os.path.join(C.RUN, 'p7')
MODEL = os.path.join(C.RUN, 'model', 'Tomek52b.so')
BASE = {'GKr_b': 0.0321, 'GKs_b': 0.0011, 'GNaL_b': 0.0279, 'thL': 200.0, 'Gto_b': 0.16, 'GK1_b': 0.6992, 'PNaK_b': 15.4509, 'Gncx_b': 0.0034}
GOMEZ = {'GNaL_b': 1.80, 'thL': 1.80, 'Gto_b': 0.40, 'GK1_b': 0.68, 'PNaK_b': 0.70, 'Gncx_b': 1.75, 'sJup': 0.50, 'sJleak': 1.30, 'sCaMKa': 1.50}
OUT = os.path.join(HERE, 'cell52_p7.json')


def run_b(tag, flags, nbeats, bcl, params, restore=None, save=None):
    d = os.path.join(RUN, tag); os.makedirs(d, exist_ok=True)
    dur = nbeats * bcl
    par = ','.join([f'flags={flags}'] + [f'{k}={v:.10g}' for k, v in params.items()])
    cmd = ['bench', f'--load-module={MODEL}', '--imp=Tomek52b', f'--imp-par={par}', f'--numstim={nbeats}', f'--bcl={bcl}', f'--duration={dur}',
           '--APstatistics', '--fout=out', '--dt-out=1', f'--start-out={dur - 2 * bcl}']
    if restore:
        cmd.append(f'--read-ini-file={restore}')
    if save:
        cmd += [f'--save-ini-file={save}', f'--save-ini-time={dur}']
    with open(os.path.join(d, 'bench.log'), 'w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d)
    st = np.loadtxt(os.path.join(d, 'out_AP_stats.dat'), comments='#', usecols=(3, 9), ndmin=2)
    return st, d


def steady(tag, flags, bcl, params, restore):
    apd, state, n = [], restore, 0
    while n < 3000:
        save = os.path.join(RUN, tag, f'state_{n + 200}.sv')
        st, d = run_b(f'{tag}/chunk_{n:05d}', flags, 200, bcl, params, restore=state, save=save)
        apd += list(st[3:, 0]); n += 200; state = save
        if len(apd) >= 10 and np.ptp(apd[-10:]) < 0.5:
            return np.array(apd), state, d, n, True
    return np.array(apd), state, d, n, bool(len(apd) >= 10 and np.ptp(apd[-10:]) < 0.5)


def events(d, bcl):
    x = np.loadtxt(os.path.join(d, 'out.txt')); t, v = x[:, 0], x[:, 1]
    res = []
    for k in range(2):
        m = (t >= t[0] + k * bcl) & (t < t[0] + (k + 1) * bcl)
        tt, vv = t[m] - t[m][0], v[m]
        ip = int(np.argmax(vv)); vmin = vv[:max(1, ip)].min(); thr = vv[ip] - 0.9 * (vv[ip] - vmin)
        dn = np.where((vv[:-1] > thr) & (vv[1:] <= thr) & (np.arange(len(vv) - 1) > ip))[0]
        rep = int(dn[0]) if len(dn) else None
        dv = np.diff(vv)
        ead = False
        if rep is not None:
            seg = (np.arange(len(dv)) > ip + 20) & (np.arange(len(dv)) < rep) & (vv[:-1] > -60)
            up = seg & (dv > 0.05)
            run_ = 0
            for u in up:
                run_ = run_ + 1 if u else 0
                if run_ >= 2:
                    ead = True; break
        dad = False
        if rep is not None:
            after = vv[rep:]
            if len(after) > 5:
                mn = after.min(); im = int(np.argmin(after))
                dad = bool((after[im:] - mn).max() > 5.0)
        res.append({'EAD': bool(ead), 'failure_to_repolarise': rep is None, 'DAD': dad})
    return {'EAD_any': any(r['EAD'] for r in res), 'failure_any': any(r['failure_to_repolarise'] for r in res), 'DAD_any': any(r['DAD'] for r in res)}


def main():
    t0 = time.time()
    c52 = json.load(open(C.OUT))
    mean = c52['derive']['mean_ms']
    targets = {'ENDO': 1.110 * mean + 3.5, 'EPI': 1.110 * mean - 3.5}
    rec = {'lock_sha256': C.LOCK_SHA, 'model': 'Tomek52b (see docstring)', 'targets_ms': {k: round(v, 3) for k, v in targets.items()}, 'a_IKr': {}, 'b_Gomez2014': {}}
    base_state = {ct: os.path.join(C.REPO, c52['baseline'][ct]['state_file']) for ct in ('ENDO', 'EPI')}
    # (a)
    for ct, T in targets.items():
        hist = []

        def f(x):
            s = float(np.exp(x))
            apd, state, d, n, ok = steady(f'a_{ct}/s{s:.6f}', ct, 1000.0, {'GKr_b': BASE['GKr_b'] * s}, base_state[ct])
            hist.append({'GKr_scale': round(s, 6), 'APD90_ms': round(float(apd[-1]), 3), 'beats': n, 'steady': ok, 'state': state, 'dir': d})
            print('a', ct, {k: v for k, v in hist[-1].items() if k not in ('state', 'dir')}, flush=True)
            return float(apd[-1]) - T
        x0, x1 = 0.0, -0.3
        f0, f1 = f(x0), f(x1)
        for _ in range(12):
            if abs(f1) <= 0.25:
                break
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0) if f1 != f0 else x1 - 0.2
            x2 = max(x2, -6.0)
            x0, f0, x1 = x1, f1, x2
            f1 = f(x1)
        best = hist[-1]
        ev1000 = events(best['dir'], 1000.0)
        s = best['GKr_scale']
        apd6, st6, d6, n6, ok6 = steady(f'a_{ct}/cl600_s{s:.6f}', ct, 600.0, {'GKr_b': BASE['GKr_b'] * s}, best['state'])
        ev600 = events(d6, 600.0)
        rec['a_IKr'][ct] = {'target_ms': round(T, 3), 'GKr_scale': s, 'APD90_CL1000_ms': best['APD90_ms'], 'within_0.25ms': bool(abs(f1) <= 0.25),
                            'steady_CL1000': best['steady'], 'afterdepolarisations_CL1000': ev1000,
                            'APD90_CL600_ms': round(float(apd6[-1]), 3), 'steady_CL600': ok6, 'afterdepolarisations_CL600': ev600,
                            'evaluations': [{k: v for k, v in hh.items() if k not in ('state', 'dir')} for hh in hist]}
    # (b)
    for reading, fac in (('threshold x0.8', 0.8), ('threshold / 0.8', 1 / 0.8)):
        r = {}
        for ct in ('ENDO', 'EPI'):
            params = {k: BASE[k] * v for k, v in GOMEZ.items() if k in BASE}
            params.update({k: v for k, v in GOMEZ.items() if k not in BASE})
            params['sJrelNP'] = fac
            apd, state, d, n, ok = steady(f'b_{reading.replace(" ", "_").replace("/", "div")}_{ct}/cl1000', ct, 1000.0, params, base_state[ct])
            ev = events(d, 1000.0)
            apd6, st6, d6, n6, ok6 = steady(f'b_{reading.replace(" ", "_").replace("/", "div")}_{ct}/cl600', ct, 600.0, params, state)
            ev6 = events(d6, 600.0)
            r[ct] = {'APD90_CL1000_ms': round(float(apd[-1]), 3), 'beats': n, 'steady_CL1000': ok, 'afterdepolarisations_CL1000': ev,
                     'APD90_CL600_ms': round(float(apd6[-1]), 3), 'steady_CL600': ok6, 'afterdepolarisations_CL600': ev6}
            print('b', reading, ct, r[ct], flush=True)
        m1000 = 0.5 * (r['ENDO']['APD90_CL1000_ms'] + r['EPI']['APD90_CL1000_ms'])
        r['mean_CL1000_ms (target 1.110 x 256.855 = 285.11)'] = round(m1000, 3)
        r['endo_minus_epi_CL1000_ms (target 7)'] = round(r['ENDO']['APD90_CL1000_ms'] - r['EPI']['APD90_CL1000_ms'], 3)
        r['mean_ratio_to_control'] = round(m1000 / mean, 4)
        rec['b_Gomez2014'][reading] = r
    rec['mapping_notes'] = ['INab x1.00: no change', 'Jup x0.50 scales the SERCA uptake terms only; ToR-ORd computes Jup = Jup_b ((1 - f) Jupnp + f Jupp - Jleak), so the leak is scaled separately (x1.30)',
                            'CaMKa x1.50: the active-CaMK variable that sets the phosphorylated fractions; the CaMKt rate equation uses CaMKb + CaMKt directly and is not scaled',
                            'Jrel,NP,inf Ca sensitivity x0.80: ToR-ORd uses Cajsr_half = 1.7 mM (ORd 1.5 mM); the factor is applied to Cajsr_half in the NP term only; its direction is not stated in the paper, both readings reported',
                            'tau_hL x1.80: thL; ToR-ORd ties thLp = 3 thL as ORd does']
    rec['wall_s'] = round(time.time() - t0, 1)
    json.dump(rec, open(OUT, 'w'), indent=1)
    print('done', rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    main()
