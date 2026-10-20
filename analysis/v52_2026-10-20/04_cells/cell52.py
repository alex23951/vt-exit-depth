"""v5.2 step 4, single-cell part (LOCK.md 2.1 R1.1-R1.5, 15.2 step 4, 15.3 T1; allowed early by clarification C7).

R1.1: openCARP's Tomek (ToR-ORd) model in bench, ENDO and EPI, CL 1000 ms, paced until APD90 changes by less than 0.5 ms
over the last 10 beats (max - min of the last 10 beats' APD90 < 0.5 ms; bench's APD90 = repolarisation to 90 % of the
beat's amplitude, its --APstatistics); each type's APD90 and its last two beats at 1 ms.
R1.2-R1.5 (cell-level quantities only; the in-heart checks wait for step 2): on a w grid (0 to 1 in 0.01), the blended
trace (1 - w) endo + w epi aligned at the upstroke (bench's activation time), its APD90, the target maps (control
mean + 14 - 28 w; HF 1.110 mean + 3.5 - 7 w, mean = (APD90_endo + APD90_epi) / 2), the time-stretch factor after +80 ms
k(w) = (target - 80) / (APD90_blend - 80) and its check on the stretched trace, and the splice offset that brings the
trace's value at +80 ms to the template's held 13.9 mV (R1.2).
15.3 T1 (RE+): IKs conductance scalings (GKs_b of a copy of Tomek.model with GKs_b exposed as a parameter, compiled with
make_dynamic_model.sh; at the default value it reproduces the built-in Tomek trace exactly) that bring each type's
steady-state APD90 to its target at w = 0 (endo) and w = 1 (epi): HF 1.110 mean + 3.5 / - 3.5 ms (15.3's named HF
factors); control mean + 14 / - 14 ms (my reading of 15.3's "the R1.4 APD target map" for the RE+ cells; reported).
Each scaling by the secant method on log(scale), every evaluation restarted from that type's baseline steady state and
paced to the same steady-state criterion; tolerance 0.25 ms.
Outputs: analysis/v52_2026-10-20/04_cells/cell52.json; traces and states under runs/v52_2026-10-20/04_cells/.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/04_cells/cell52.py [baseline|derive|iks|all]
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '04_cells')
MODEL = os.path.join(RUN, 'model', 'Tomek52.so')
LOCK_SHA = '08ea65d3cda1adac9dcb1935a9000f32bbe093fc65e1e2e52ed8556373a1980b'
BCL = 1000.0
CHUNK = 200                       # beats per chunk
MAX_BEATS = 5000
HOLD = 13.9                       # mV, v5.1 template's held value (LOCK.md 2, R1.2)
GKS_B = 0.0011
OUT = os.path.join(HERE, 'cell52.json')


def bench(tag, flags, nbeats, restore=None, save=None, gks=None, trace_last=0):
    d = os.path.join(RUN, tag); os.makedirs(d, exist_ok=True)
    dur = nbeats * BCL
    par = f'flags={flags}' + (f',GKs_b={gks:.10g}' if gks is not None else '')
    cmd = ['bench', '--imp=' + ('Tomek52' if gks is not None else 'Tomek'), f'--imp-par={par}', f'--numstim={nbeats}', f'--bcl={BCL}',
           f'--duration={dur}', '--APstatistics', '--fout=out', '--dt-out=1']
    if gks is not None:
        cmd.insert(1, f'--load-module={MODEL}')
    if trace_last:
        cmd.append(f'--start-out={dur - trace_last * BCL}')
    else:
        cmd += [f'--start-out={dur}']
    if restore:
        cmd.append(f'--read-ini-file={restore}')
    if save:
        cmd += [f'--save-ini-file={save}', f'--save-ini-time={dur}']
    with open(os.path.join(d, 'bench.log'), 'w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d)
    st = np.loadtxt(os.path.join(d, 'out_AP_stats.dat'), comments='#', usecols=(3, 9))       # APD(n), tAct
    return st, d


def steady(tag, flags, gks=None, restore=None):
    """Pace in chunks until the last 10 beats' APD90 span < 0.5 ms; returns (APD90 per beat, final state file, trace dir)."""
    apd, state, n = [], restore, 0
    while n < MAX_BEATS:
        save = os.path.join(RUN, tag, f'state_{n + CHUNK}.sv')
        st, d = bench(f'{tag}/chunk_{n:05d}', flags, CHUNK, restore=state, save=save, gks=gks, trace_last=2)
        # bench measures each run's first 3 beats with its uncalibrated -66 mV thresholds ("Measuring AP parameters for
        # calibration"), so those 3 values are dropped; its stats also omit each run's final beat
        apd += list(st[3:, 0]); n += CHUNK; state = save
        last = np.array(apd[-10:])
        if len(apd) >= 10 and last.max() - last.min() < 0.5:
            return np.array(apd), state, d, n
    return np.array(apd), state, d, n


def trace(d):
    x = np.loadtxt(os.path.join(d, 'out.txt'))
    return x[:, 0], x[:, 1]


def apd90(t, v):
    """bench's definition: threshold = 90 % repolarisation of the beat's amplitude (Vmax - Vrest); activation = its up-crossing,
    repolarisation = its first down-crossing after the peak (linear interpolation); returns (APD90, activation time)."""
    ip = int(np.argmax(v))
    vmax, vmin = v[ip], v[:max(1, ip)].min()
    thr = vmax - 0.9 * (vmax - vmin)
    up = np.where((v[:-1] < thr) & (v[1:] >= thr) & (np.arange(len(v) - 1) < ip))[0]
    dn = np.where((v[:-1] > thr) & (v[1:] <= thr) & (np.arange(len(v) - 1) > ip))[0]
    if not len(up) or not len(dn):
        return np.nan, np.nan
    i, j = up[-1], dn[0]
    ta = t[i] + (thr - v[i]) * (t[i + 1] - t[i]) / (v[i + 1] - v[i])
    tr = t[j] + (thr - v[j]) * (t[j + 1] - t[j]) / (v[j + 1] - v[j])
    return tr - ta, ta


def baseline(rec):
    for ct in ('ENDO', 'EPI'):
        t0 = time.time()
        apd, state, d, n = steady(f'baseline_{ct}', ct)
        last = apd[-10:]
        t, v = trace(d)
        rec.setdefault('baseline', {})[ct] = {'beats': int(n), 'steady_state_met': bool(last.max() - last.min() < 0.5),
                                              'last10_APD90_span_ms': round(float(last.max() - last.min()), 4),
                                              'APD90_ms (bench, last beat)': round(float(apd[-1]), 3),
                                              'first_window_meeting_the_criterion (index in the kept-beat series)': int(next(i for i in range(9, len(apd)) if np.ptp(apd[i - 9:i + 1]) < 0.5) + 1),
                                              'state_file': os.path.relpath(state, REPO), 'trace_dir (last two beats, 1 ms)': os.path.relpath(d, REPO),
                                              'wall_s': round(time.time() - t0, 1)}
        print(ct, rec['baseline'][ct], flush=True)


def last_beat(d):
    t, v = trace(d)
    m = t >= t[0] + BCL                                       # the final beat of the two
    return t[m] - t[m][0], v[m]


def derive(rec):
    te, ve = last_beat(os.path.join(REPO, rec['baseline']['ENDO']['trace_dir (last two beats, 1 ms)']))
    tp, vp = last_beat(os.path.join(REPO, rec['baseline']['EPI']['trace_dir (last two beats, 1 ms)']))
    ae, ue = apd90(te, ve); ap, up = apd90(tp, vp)
    # align at the upstroke on a 0.01 ms grid
    tt = np.arange(-20, 900, 0.01)
    Ve, Vp = np.interp(tt + ue, te, ve), np.interp(tt + up, tp, vp)
    a_endo, a_epi = rec['baseline']['ENDO']['APD90_ms (bench, last beat)'], rec['baseline']['EPI']['APD90_ms (bench, last beat)']
    mean = 0.5 * (a_endo + a_epi)
    out = {'APD90_endo_bench_ms': a_endo, 'APD90_epi_bench_ms': a_epi, 'APD90_endo_minus_epi_ms': round(a_endo - a_epi, 3),
           'APD90_from_trace_ms (endo, epi; my measure)': [round(ae, 3), round(ap, 3)], 'mean_ms': round(mean, 3),
           'tomek_figure_reading_sanity (290 / 258 ms, about 32 ms)': 'reported beside, never used', 'grid': []}
    for w in np.round(np.arange(0, 1.0001, 0.01), 2):
        V = (1 - w) * Ve + w * Vp
        a_b, _ = apd90(tt, V)
        row = {'w': float(w), 'APD90_blend_ms': round(float(a_b), 3), 'V_at_80ms_mV': round(float(np.interp(80.0, tt, V)), 4),
               'splice_offset_mV (to 13.9 at +80 ms)': round(float(HOLD - np.interp(80.0, tt, V)), 4)}
        for nm, T in (('control', mean + 14 - 28 * w), ('HF', 1.110 * mean + 3.5 - 7 * w)):
            k = (T - 80.0) / (a_b - 80.0)
            ts = np.where(tt <= 80, tt, 80 + (tt - 80) / k)          # stretched trace: V'(80 + k s) = V(80 + s)
            Vs = np.interp(tt, np.where(tt <= 80, tt, 80 + (tt - 80) * k), V)
            a_s, _ = apd90(tt, Vs)
            row[nm] = {'target_ms': round(float(T), 3), 'stretch_factor_k': round(float(k), 6), 'APD90_after_stretch_ms': round(float(a_s), 3),
                       'check_within_0.5ms': bool(abs(a_s - T) <= 0.5)}
        out['grid'].append(row)
    g = out['grid']
    out['checks'] = {'control_endo_minus_epi_after_stretch_ms': round(g[0]['control']['APD90_after_stretch_ms'] - g[-1]['control']['APD90_after_stretch_ms'], 3),
                     'HF_endo_minus_epi_after_stretch_ms': round(g[0]['HF']['APD90_after_stretch_ms'] - g[-1]['HF']['APD90_after_stretch_ms'], 3),
                     'every_w_within_0.5ms_of_target': bool(all(r[c]['check_within_0.5ms'] for r in g for c in ('control', 'HF'))),
                     'control_scale_of_the_transmural_difference (28 / own)': round(28.0 / (a_endo - a_epi), 4)}
    rec['derive'] = out
    print('derive', {k: v for k, v in out.items() if k != 'grid'}, flush=True)


def iks(rec):
    mean = rec['derive']['mean_ms']
    targets = {('ENDO', 'control'): mean + 14, ('EPI', 'control'): mean - 14, ('ENDO', 'HF'): 1.110 * mean + 3.5, ('EPI', 'HF'): 1.110 * mean - 3.5}
    res = {}
    for (ct, nm), T in targets.items():
        t0 = time.time()
        base = os.path.join(REPO, rec['baseline'][ct]['state_file'])
        hist = []

        def f(logs):
            s = float(np.exp(logs))
            apd, state, d, n = steady(f'iks_{ct}_{nm}/s{s:.6f}', ct, gks=GKS_B * s, restore=base)
            hist.append({'scale': round(s, 6), 'APD90_ms': round(float(apd[-1]), 3), 'beats': int(n),
                         'steady': bool(np.ptp(apd[-10:]) < 0.5)})
            print(ct, nm, hist[-1], flush=True)
            return float(apd[-1]) - T
        x0, x1 = 0.0, (-0.3 if T > rec['baseline'][ct]['APD90_ms (bench, last beat)'] else 0.3)
        f0, f1 = f(x0), f(x1)
        for _ in range(10):
            if abs(f1) <= 0.25:
                break
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0) if f1 != f0 else x1 + 0.1
            x0, f0, x1 = x1, f1, x2
            f1 = f(x1)
        res[f'{ct} {nm}'] = {'target_ms': round(T, 3), 'GKs_scale': round(float(np.exp(x1)), 6), 'GKs_b': GKS_B * float(np.exp(x1)),
                             'achieved_APD90_ms': round(T + f1, 3), 'within_0.25ms': bool(abs(f1) <= 0.25), 'evaluations': hist,
                             'wall_s': round(time.time() - t0, 1)}
    rec['iks'] = res


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    rec = json.load(open(OUT)) if os.path.exists(OUT) else {'lock_sha256': LOCK_SHA, 'model': 'openCARP Tomek (bench, build ffce195)',
                                                             'CL_ms': BCL, 'criterion': 'max - min of the last 10 beats APD90 < 0.5 ms'}
    if stage in ('baseline', 'all'):
        baseline(rec); json.dump(rec, open(OUT, 'w'), indent=1)
    if stage in ('derive', 'all'):
        derive(rec); json.dump(rec, open(OUT, 'w'), indent=1)
    if stage in ('iks', 'all'):
        iks(rec); json.dump(rec, open(OUT, 'w'), indent=1)


if __name__ == '__main__':
    main()
