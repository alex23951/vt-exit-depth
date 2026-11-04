"""D46 / D48 for the 27-site test's RE+ leg (lock thread 3 Nov 2026: D45 as adopted 13:52:08 UTC, addenda 1-3, D48
"Fit the time constant only" 15:21:51 UTC): Tomek52w's excitation threshold with the V_th margins, and the RE+ foot
current's tau_F fitted on a 200 um monodomain patch. No heart beat; nothing here reads a v5.2 heart result.

(1) threshold: per heart type (blend52.SETTINGS) at w = 0, 0.5 and 1, a single cell from blend52's CL 1000 steady state
    (bench, Tomek52w as the tissue runs use it, t1_27.SO) gets one 1 ms stimulus 1000 ms after the last beat; the weakest
    amplitude that still gives an action potential (Vm above 0 mV within 100 ms) is found by bisection to 1e-4 relative;
    the threshold is Vm at the end of that stimulus (addendum 1 item 3). Margin = V_th (-30 mV) minus the threshold.
(2) patch: a 20 x 1 x 1 mm block at 200 um (openCARP mesher, regular tets, fibres along x), pure monodomain, dt 10 us,
    Tomek52w with the heart type's factors from the steady state at that w, a planar wave along the fibre (nodes within
    0.4 mm of the x = 0 face, 400 uA/cm3 x 1 ms, as step 6). Conductivities by R4.4's flat-block rule: the fibre axis
    tuned at w = 0.5 until the LAT speed over x = 5-15 mm is within 1 % of 0.80 m/s (at most 6 rounds; LAT -10 mV,
    least squares of LAT on x), g_e / g_i held at fix 2's fibre ratio (params/v52_conductivities.json); cross-fibre
    conductivities at step 6's tuned values (they carry no current in a planar wave along x). The same conductivities
    are used at w = 0 and 1.
(3) fit (addendum 2 item 1 as corrected by addendum 3, D48): the node nearest (10, 0.5, 0.5) mm, Vm and Iion every
    solver step (openCARP trace, tracedt = dt, 12 decimals). V_rest = median Vm from 6 to 4 ms before the node's LAT
    (before the wave arrives). Window: from the foot's departure from rest (the last step at which Vm - V_rest is at
    most 0.1 % of (threshold - V_rest)) to the first step at which Vm reaches Tomek52w's excitation threshold at that
    w and heart type (from (1)). dVm/dt by central differences at every step in the window. tau_F = 1 / (least-squares
    slope through the origin of dVm/dt against Vm - V_rest); fit error = RMS residual (mV/ms), also relative to the RMS
    of dVm/dt, and the slope's standard error carried to tau_F. Check line (changes nothing): free-intercept least
    squares, slope and Vm-axis intercept. At w = 0 and 1 the w = 0.5 tau_F's error over each own window, plus each own
    tau_F for reference. The diffusion current at the node, I_diff = Cm dVm/dt + Iion (Cm = 1 uF/cm2), is kept per step.
(4) foot delay: from the eikonal time (dT = 0, Vm = V_rest), the foot alone, A_F / tau_F exp(dT / tau_F) added as
    Vm += I dt every 10 us step (openCARP's FOOT, Idiff.model 0) until Vm reaches V_th = -30 mV; with A_F = 0.91 mV
    (D48) and the fitted tau_F, and with openCARP's default tau_F 0.25 ms beside it; continuous form
    tau_F ln(1 + (V_th - V_rest) / A_F).
Alignment of dT = 0 (D45): dT = 0 is the node's eikonal activation time. With A_F at Neic 2017's 0.91 mV (D48), the
current injected from that time is the slope of an exponential foot that stands A_F above rest at the eikonal time
(Neic 2017 App. A); a through-origin slope of dVm/dt on Vm - V_rest does not depend on where dT = 0 is put.
Writes foot52.json (this folder); runs under runs/v52_2026-10-20/11_engine/foot/.
Usage (repo root, venv, PATH): python -B .../foot52.py threshold | tune | fit | all
"""
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', 'foot')
OUT = os.path.join(HERE, 'foot52.json')
sys.path.insert(0, HERE)
import blend52 as B                                                                           # noqa: E402
import t1_27 as T                                                                             # noqa: E402

SO = T.SO
V_TH, A_F, TAU_DEFAULT = -30.0, 0.91, 0.25
DT = 0.01
WS = (0.0, 0.5, 1.0)
CV_TARGET, X_LO, X_HI = 0.80, 5.0, 15.0
FIX2 = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts']
MONO = json.load(open(os.path.join(REPO, 'params', 'v52_mono_conductivities.json')))['hearts']
AXES = (('fibre', 'l'), ('sheet', 't'), ('normal', 'n'))


def rec():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def save(r):
    json.dump(r, open(OUT, 'w'), indent=1)


def par(s, w):
    return ','.join([f'wb={w}'] + [f'{k}={v}' for k, v in B.SETTINGS[s]['par'].items()])


def state(s, w):
    return os.path.join(REPO, json.load(open(B.OUT))['grid'][s][f'{w:.1f}']['state_file'])


# ---------------------------------------------------------------- (1) excitation threshold
def stim_cell(s, w, amp, d):
    os.makedirs(d, exist_ok=True)
    cmd = ['bench', f'--load-module={SO}', '--imp=Tomek52w', f'--imp-par={par(s, w)}', f'--read-ini-file={state(s, w)}',
           f'--stim-curr={amp!r}', '--stim-dur=1', '--numstim=1', '--stim-start=1', '--duration=101', f'--dt-out={DT}',
           '--fout=out', '--no-trace']
    subprocess.run(cmd, stdout=open(os.path.join(d, 'bench.log'), 'w'), stderr=subprocess.STDOUT, cwd=d, check=True)
    x = np.loadtxt(os.path.join(d, 'out.txt'))
    i_end = int(np.argmin(np.abs(x[:, 0] - 2.0))); i_on = int(np.argmin(np.abs(x[:, 0] - 1.0)))
    assert abs(x[i_end, 0] - 2.0) < 1e-6 and abs(x[i_on, 0] - 1.0) < 1e-6
    return {'amp': amp, 'Vm_at_stim_start_mV': float(x[i_on, 1]), 'Vm_at_stim_end_mV': float(x[i_end, 1]),
            'Vmax_mV': float(x[i_on:, 1].max()), 'fires': bool(x[i_on:, 1].max() > 0.0)}


def threshold_one(job):
    s, w = job
    d = os.path.join(RUN, 'threshold', f'{s}_w{w:.1f}')
    lo, hi = 0.0, 5.0
    r_hi = stim_cell(s, w, hi, d)
    while not r_hi['fires']:
        assert hi < 1e4, 'no AP up to 1e4 uA/cm2'
        lo, hi = hi, hi * 2; r_hi = stim_cell(s, w, hi, d)
    r_lo, n = None, 0
    while (hi - lo) / hi > 1e-4:
        mid = 0.5 * (lo + hi); r = stim_cell(s, w, mid, d); n += 1
        if r['fires']:
            hi, r_hi = mid, r
        else:
            lo, r_lo = mid, r
    if r_lo is None:
        r_lo = stim_cell(s, w, lo, d)
    return s, w, {'state': os.path.relpath(state(s, w), REPO), 'par': par(s, w), 'bisection_steps': n,
                  'weakest_firing': r_hi, 'strongest_silent': r_lo, 'threshold_mV': r_hi['Vm_at_stim_end_mV'],
                  'V_th_margin_mV': V_TH - r_hi['Vm_at_stim_end_mV']}


def threshold():
    r = rec(); out = {}
    with ThreadPoolExecutor(4) as ex:
        for s, w, x in ex.map(threshold_one, [(s, w) for s in B.SETTINGS for w in WS]):
            out.setdefault(s, {})[f'{w:.1f}'] = x
            print(s, w, round(x['threshold_mV'], 4), 'margin', round(x['V_th_margin_mV'], 4), 'amp', round(x['weakest_firing']['amp'], 5), flush=True)
    out['rule'] = 'Vm at the end of the weakest 1 ms stimulus giving an AP (Vm > 0 mV within 100 ms), CL 1000 steady state, bisection to 1e-4 relative'
    out['all_margins_positive'] = all(x['V_th_margin_mV'] > 0 for s in B.SETTINGS for x in out[s].values())
    r['threshold'] = out; save(r)


# ---------------------------------------------------------------- (2) patch
def mesh():
    base = os.path.join(RUN, 'patch', 'patch')
    if not os.path.exists(base + '.pts'):
        os.makedirs(os.path.dirname(base), exist_ok=True)
        subprocess.run(['mesher', '-size[0]', '2.0', '-size[1]', '0.1', '-size[2]', '0.1', '-resolution[0]', '200',
                        '-resolution[1]', '200', '-resolution[2]', '200', '-mesh', base],
                       stdout=open(base + '_mesher.log', 'w'), stderr=subprocess.STDOUT, check=True)
    P = np.loadtxt(base + '.pts', skiprows=1) / 1000.0
    P = P - P.min(axis=0)
    lon = np.loadtxt(base + '.lon', skiprows=1, max_rows=5)
    return base, P, lon


def gcond(h, gi_f):
    ratio = FIX2[h]['sigma_S_m']['fibre']['ge'] / FIX2[h]['sigma_S_m']['fibre']['gi']
    g = {'fibre': (gi_f, gi_f * ratio)}
    for a, _ in AXES[1:]:
        c = MONO[h]['conductivities_S_m'][a]; g[a] = (c['gi'], c['ge'])
    return g, ratio


def run(s, w, gi_f, label, P, base, trace_node=None, tend=30.0):
    h = B.SETTINGS[s]['heart']
    d = os.path.join(RUN, 'patch', label); os.makedirs(d, exist_ok=True)
    stim = np.where(P[:, 0] <= 0.4 + 1e-6)[0]
    with open(os.path.join(d, 'stim.vtx'), 'w') as fh:
        fh.write(f'{len(stim)}\nintra\n'); np.savetxt(fh, stim, fmt='%d')
    g, _ = gcond(h, gi_f)
    cmd = ['openCARP', '-meshname', base, '-simID', d, '-bidomain', 0, '-dt', 10, '-parab_solve', 1, '-tend', tend,
           '-spacedt', 1.0, '-timedt', 5.0, '-num_external_imp', 1, '-external_imp[0]', SO, '-num_imp_regions', 1,
           '-imp_region[0].im', 'Tomek52w', '-imp_region[0].im_param', par(s, w), '-imp_region[0].im_sv_init', state(s, w),
           '-num_stim', 1, '-stim[0].crct.type', 0, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'),
           '-stim[0].pulse.strength', 400.0, '-stim[0].ptcl.duration', 1.0, '-stim[0].ptcl.npls', 1,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0, '-lats[0].threshold', -10,
           '-lats[0].method', 1, '-num_gregions', 1, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1]
    for a, k in AXES:
        cmd += [f'-gregion[0].g_i{k}', g[a][0], f'-gregion[0].g_e{k}', g[a][1]]
    if trace_node is not None:
        cmd += ['-num_trace', 1, '-trace_node[0]', int(trace_node), '-tracedt', DT]
    t0 = time.time()
    with open(os.path.join(d, 'run.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True, cwd=d)
    act = np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat'))
    m = (P[:, 0] >= X_LO) & (P[:, 0] <= X_HI)
    unact = int(np.sum(act[m] < 0))
    v = float(1.0 / np.polyfit(P[m, 0], act[m], 1)[0]) if unact == 0 else float('nan')
    return d, act, v, {'gi_fibre': gi_f, 'ge_fibre': g['fibre'][1], 'cv_m_s': v, 'unactivated_5_15mm': unact, 'wall_s': round(time.time() - t0, 1)}


def tune_one(s):
    base, P, lon = mesh()
    gi = MONO[B.SETTINGS[s]['heart']]['conductivities_S_m']['fibre']['gi']
    hist = []
    for k in range(6):
        _, _, v, info = run(s, 0.5, gi, f'{s}_tune_r{k}', P, base)
        info['ratio_to_target'] = v / CV_TARGET; hist.append(info)
        print(s, 'round', k, round(gi, 6), round(v, 5), flush=True)
        if not np.isfinite(v):
            break
        if abs(v / CV_TARGET - 1) <= 0.01:
            break
        b = 0.5
        if len(hist) >= 2 and hist[-2]['gi_fibre'] != hist[-1]['gi_fibre']:
            bb = np.log(hist[-1]['ratio_to_target'] / hist[-2]['ratio_to_target']) / np.log(hist[-1]['gi_fibre'] / hist[-2]['gi_fibre'])
            b = float(bb) if 0.2 < bb < 1.2 else 0.5
        gi = gi * (CV_TARGET / v) ** (1 / b)
    last = hist[-1]
    return s, {'rounds': hist, 'gi_fibre': last['gi_fibre'], 'ge_fibre': last['ge_fibre'], 'cv_m_s': last['cv_m_s'],
               'within_1pct': bool(np.isfinite(last['cv_m_s']) and abs(last['cv_m_s'] / CV_TARGET - 1) <= 0.01),
               'ge_over_gi': gcond(B.SETTINGS[s]['heart'], 1.0)[1]}


def tune():
    r = rec(); base, P, lon = mesh()
    r['patch'] = {'mesh': os.path.relpath(base, REPO), 'nodes': int(len(P)), 'size_mm': [float(x) for x in P.max(axis=0)],
                  'fibre_rows_head': lon[:2].tolist(), 'resolution_um': 200}
    with ThreadPoolExecutor(2) as ex:
        for s, x in ex.map(tune_one, list(B.SETTINGS)):
            r['patch'][s] = x
    save(r)


# ---------------------------------------------------------------- (3)-(4) fit
def trace_file(d):
    f = [x for x in os.listdir(d) if x.startswith('Trace_') and x.endswith('.dat')]
    assert len(f) == 1, f
    return os.path.join(d, f[0])


def window(t, V, lat, thr):
    pre = (t >= lat - 6.0) & (t <= lat - 4.0)
    vr = float(np.median(V[pre]))
    i_end = int(np.argmax((V >= thr) & (t > lat - 4.0)))
    small = np.where(V[:i_end + 1] - vr <= 1e-3 * (thr - vr))[0]
    i_start = int(small[-1])
    return vr, i_start, i_end


def fit_one(job):
    s, w, gi_f, node, thr = job
    base, P, _ = mesh()
    d, act, v, info = run(s, w, gi_f, f'{s}_w{w:.1f}_fit', P, base, trace_node=node)
    x = np.loadtxt(trace_file(d))
    hdr = open(os.path.join(d, 'Tomek52w_trace_header.txt')).read().split() if os.path.exists(os.path.join(d, 'Tomek52w_trace_header.txt')) else []
    t, iion, V = x[:, 0], x[:, 1 + hdr.index('Iion')], x[:, 1 + hdr.index('V')]
    assert np.allclose(np.diff(t), DT, atol=1e-6), 'trace not at every solver step'
    lat = float(act[node])
    vr, i0, i1 = window(t, V, lat, thr)
    idx = np.arange(max(i0, 1), i1 + 1)
    dvdt = (V[idx + 1] - V[idx - 1]) / (2 * DT)
    X, Y = V[idx] - vr, dvdt
    slope = float(np.sum(X * Y) / np.sum(X * X))
    res = Y - slope * X
    se = float(np.sqrt(np.sum(res ** 2) / (len(X) - 1) / np.sum(X * X)))
    p = np.polyfit(X, Y, 1)
    np.savez(os.path.join(d, 'foot_node.npz'), t=t, V=V, Iion=iion, Idiff=np.r_[np.nan, (V[2:] - V[:-2]) / (2 * DT), np.nan] + iion,
             window=np.array([i0, i1]), V_rest=vr, node=node)
    return s, w, {'run': info, 'node': int(node), 'node_xyz_mm': P[node].round(4).tolist(), 'node_LAT_ms': lat, 'V_rest_mV': vr,
                  'threshold_mV': thr, 'window_start': {'t_ms': float(t[i0]), 'Vm_mV': float(V[i0])},
                  'window_end': {'t_ms': float(t[i1]), 'Vm_mV': float(V[i1])}, 'n_steps': int(len(idx)),
                  'tau_F_own_ms': 1.0 / slope, 'tau_F_own_se_ms': se / slope ** 2,
                  'fit_rms_mV_per_ms': float(np.sqrt(np.mean(res ** 2))), 'fit_rms_rel': float(np.sqrt(np.mean(res ** 2)) / np.sqrt(np.mean(Y ** 2))),
                  'free_intercept_slope_per_ms': float(p[0]), 'free_intercept_tau_ms': float(1 / p[0]),
                  'free_intercept_Vm_axis_mV': float(vr - p[1] / p[0]),
                  'dVdt_at_window_end_mV_per_ms': float(Y[-1]), 'Idiff_max_in_window_uA_cm2': float(np.max(Y + iion[idx])),
                  '_X': X.tolist(), '_Y': Y.tolist()}


def foot_delay(vr, tau, a_f=A_F):
    v, k = vr, 0
    while v < V_TH:
        v += a_f / tau * np.exp(k * DT / tau) * DT; k += 1
    return {'tau_F_ms': tau, 'A_F_mV': a_f, 'V_rest_mV': vr, 'steps': k, 'delay_ms_discrete': round(k * DT, 4),
            'delay_ms_continuous': float(tau * np.log(1 + (V_TH - vr) / a_f))}


def fit():
    r = rec(); base, P, _ = mesh()
    mid = int(np.argmin(np.sum((P - np.array([10.0, 0.5, 0.5])) ** 2, axis=1)))
    jobs = [(s, w, r['patch'][s]['gi_fibre'], mid, r['threshold'][s][f'{w:.1f}']['threshold_mV']) for s in B.SETTINGS for w in WS]
    out = {}
    with ThreadPoolExecutor(3) as ex:
        for s, w, x in ex.map(fit_one, jobs):
            out.setdefault(s, {})[f'{w:.1f}'] = x
    for s in B.SETTINGS:
        tau = out[s]['0.5']['tau_F_own_ms']
        for w in ('0.0', '1.0'):
            X, Y = np.array(out[s][w]['_X']), np.array(out[s][w]['_Y'])
            res = Y - X / tau
            out[s][w]['w0.5_tau_F_rms_mV_per_ms'] = float(np.sqrt(np.mean(res ** 2)))
            out[s][w]['w0.5_tau_F_rms_rel'] = float(np.sqrt(np.mean(res ** 2)) / np.sqrt(np.mean(Y ** 2)))
        for w in out[s]:
            out[s][w].pop('_X'); out[s][w].pop('_Y')
        vr = out[s]['0.5']['V_rest_mV']
        out[s]['tau_F_entered_ms'] = round(tau, 6)
        out[s]['foot_delay'] = {'fitted': foot_delay(vr, round(tau, 6)), 'openCARP_default_tau': foot_delay(vr, TAU_DEFAULT)}
    out['entry'] = {'Idiff.model': 0, 'A_F_mV': A_F, 'V_th_mV': V_TH, 'tau_F_ms': {B.SETTINGS[s]['heart']: out[s]['tau_F_entered_ms'] for s in B.SETTINGS},
                    'note': 'HF hearts 6G8DD8S5 and 7D98EVAR take the HF value'}
    r['fit'] = out; save(r)
    for s in B.SETTINGS:
        print(s, {w: (round(out[s][w]['tau_F_own_ms'], 5), round(out[s][w]['fit_rms_rel'], 4)) for w in ('0.0', '0.5', '1.0')},
              out[s]['foot_delay']['fitted']['delay_ms_discrete'], flush=True)


if __name__ == '__main__':
    steps = {'threshold': [threshold], 'tune': [tune], 'fit': [fit], 'all': [threshold, tune, fit]}[sys.argv[1]]
    for f in steps:
        f()
