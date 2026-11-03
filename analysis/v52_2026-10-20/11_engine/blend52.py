"""v5.2 T1 / gate 9 ionic settings (LOCK.md 15.3 T1 and 11.4): ToR-ORd with the transmural blend realised as a per-node
interpolation between the endocardial and epicardial parameter sets in w, no mid-wall cell type, the R1.4 / R1.5 APD
target map reached with step 4's scalings: control heart GKs x 1.349859 (ENDO) / x 0.740818 (EPI) (cell52.json 'iks');
HF hearts IKs at Tomek's own value and GKr x 0.878867 (ENDO) / x 0.736025 (EPI) (D28 option (1), Alex 21 Oct 2026
17:54:10 UTC; cell52_p7.json 'a_IKr').

Model: Tomek52w.model (this folder) = 04_cells/Tomek52b.model (built-in Tomek at its defaults, checked 21 Oct) with
  - wb, a nodal parameter (openCARP adjustment, one value per node: the node's APD w, apd52.npz), default 0;
  - every celltype-dependent line rewritten as (1 - wb) x (ENDO value) + wb x (EPI value); ToR-ORd's MCELL branches are
    dropped (Jrel_inf / Jrel_infp differ only for MCELL, so they become their _b values);
  - sGKs_endo / sGKs_epi / sGKr_endo / sGKr_epi (region parameters, default 1) multiplying GKs_b and GKr_b in each set.
Checks (written to blend52.json):
  (a) identity: at wb = 0 the model must reproduce the built-in Tomek ENDO trace, at wb = 1 the EPI trace (20 beats,
      CL 1000 ms, 1 ms output; max |dVm| reported);
  (b) steady state (cell52.py's R1.1 criterion: last 10 beats' APD90 span < 0.5 ms, 200-beat chunks) at w = 0, 0.1, ...,
      1 for the control and HF settings; APD90 against the heart's R1.4 / R1.5 target at that w (apd52.npz), deviation
      reported (report only); the steady states are kept for the tissue runs' initial state (interpolated in w per node).
Usage (repo root, venv): python -B .../blend52.py build | check
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
C4 = os.path.join(REPO, 'analysis', 'v52_2026-10-20', '04_cells')
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', 'cells')
MDIR = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', 'model')
SO = os.path.join(MDIR, 'Tomek52w.so')
OUT = os.path.join(HERE, 'blend52.json')
BCL, CHUNK, MAX_BEATS = 1000.0, 200, 5000
W_GRID = [round(0.1 * k, 1) for k in range(11)]
SETTINGS = {
    'control': {'heart': 'Y5HYEDL4', 'par': {'sGKs_endo': 1.349859, 'sGKs_epi': 0.740818}},
    'HF': {'heart': '6G8DD8S5', 'par': {'sGKr_endo': 0.878867, 'sGKr_epi': 0.736025}},
}
BLEND = {   # variable: (ENDO expression, EPI expression), from the celltype branches of Tomek52b.model
    'cmdnmax': ('cmdnmax_b', '(cmdnmax_b*1.3)'),
    'GNaL': ('GNaL_b', '(GNaL_b*0.6)'),
    'delta_epi': ('1.', '(1. - (0.95/(1.+exp(((V+EKshift+70.)/5.)))))'),
    'Gto': ('Gto_b', '(Gto_b*2.)'),
    'PCa': ('PCa_b', '(PCa_b*1.2)'),
    'GKr': ('(GKr_b*sGKr_endo)', '(GKr_b*1.3*sGKr_epi)'),
    'GKs': ('(GKs_b*sGKs_endo)', '(GKs_b*1.4*sGKs_epi)'),
    'GK1': ('GK1_b', '(GK1_b*1.2)'),
    'Gncx': ('Gncx_b', '(Gncx_b*1.1)'),
    'PNaK': ('PNaK_b', '(PNaK_b*0.9)'),
    'GKb': ('GKb_b', '(GKb_b*0.6)'),
    'Jrel_inf': ('Jrel_inf_b', None),
    'Jrel_infp': ('Jrel_infp_b', None),
    'upSCale': ('1.', '1.3'),
}
NEW_PARAMS = """
# v5.2 T1 / gate 9 (blend52.py): per-node endo-epi blend in APD w, and step 4's GKs / GKr scalings per parameter set
wb = 0.0; .units(unitless); .param(); .nodal();
sGKs_endo = 1.0; .units(unitless); .param();
sGKs_epi = 1.0; .units(unitless); .param();
sGKr_endo = 1.0; .units(unitless); .param();
sGKr_epi = 1.0; .units(unitless); .param();
"""


def build():
    src = open(os.path.join(C4, 'Tomek52b.model')).read().split('\n')
    out, done = [], set()
    for line in src:
        m = re.match(r'^(\w+) = \(\(celltype==.*?\); (\.units\(.*)$', line)
        if m and m.group(1) in BLEND:
            v = m.group(1); endo, epi = BLEND[v]
            expr = endo if epi is None else f'(((1.-wb)*{endo})+(wb*{epi}))'
            out.append(f'{v} = {expr}; {m.group(2)}'); done.add(v); continue
        assert 'celltype==' not in line, line
        out.append(line)
        if line.startswith('sJrelNP = '):
            out += NEW_PARAMS.strip('\n').split('\n')
    assert done == set(BLEND), set(BLEND) - done
    txt = '\n'.join(out).replace('Tomek52b', 'Tomek52w')
    open(os.path.join(HERE, 'Tomek52w.model'), 'w').write(txt)
    os.makedirs(MDIR, exist_ok=True)
    shutil.copy(os.path.join(HERE, 'Tomek52w.model'), MDIR)
    shutil.copy(os.path.join(REPO, 'runs', 'v52_2026-10-20', '04_cells', 'model', 'param_compat_types.hpp'), MDIR)
    with open(os.path.join(MDIR, 'build.log'), 'w') as log:
        subprocess.run(['make_dynamic_model.sh', 'Tomek52w'], cwd=MDIR, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert os.path.exists(SO), 'no Tomek52w.so: see build.log'
    print('built', SO, flush=True)


def bench(tag, nbeats, imp, par, restore=None, save=None, trace_last=0):
    d = os.path.join(RUN, tag); os.makedirs(d, exist_ok=True)
    dur = nbeats * BCL
    cmd = ['bench', f'--imp={imp}', f'--imp-par={par}', f'--numstim={nbeats}', f'--bcl={BCL}', f'--duration={dur}',
           '--APstatistics', '--fout=out', '--dt-out=1', f'--start-out={dur - trace_last * BCL if trace_last else dur}']
    if imp == 'Tomek52w':
        cmd.insert(1, f'--load-module={SO}')
    if restore:
        cmd.append(f'--read-ini-file={restore}')
    if save:
        cmd += [f'--save-ini-file={save}', f'--save-ini-time={dur}']
    with open(os.path.join(d, 'bench.log'), 'w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d, check=True)
    return d


def apds(d):
    return np.loadtxt(os.path.join(d, 'out_AP_stats.dat'), comments='#', usecols=(3,), ndmin=1)


def steady(tag, par):
    apd, state, n = [], None, 0
    while n < MAX_BEATS:
        save = os.path.join(RUN, tag, f'state_{n + CHUNK}.sv')
        d = bench(f'{tag}/chunk_{n:05d}', CHUNK, 'Tomek52w', par, restore=state, save=save, trace_last=2)
        apd += list(apds(d)[3:]); n += CHUNK; state = save          # bench's first 3 beats per run use its -66 mV thresholds
        last = np.array(apd[-10:])
        if len(apd) >= 10 and np.ptp(last) < 0.5:
            break
    return np.array(apd), state, n


def target(h, w):
    a = np.load(os.path.join(REPO, 'data', 'biv', h, 'v52', 'apd52.npz'))
    o = np.argsort(a['w'])
    return float(np.interp(w, a['w'][o], a['target_apd90_ms'][o]))


def check():
    rec = {'model': os.path.relpath(os.path.join(HERE, 'Tomek52w.model'), REPO), 'so': os.path.relpath(SO, REPO), 'identity': {}, 'grid': {}}
    for ct, w in (('ENDO', 0.0), ('EPI', 1.0)):
        a = bench(f'identity/builtin_{ct}', 20, 'Tomek', f'flags={ct}', trace_last=20)
        b = bench(f'identity/blend_w{w:g}', 20, 'Tomek52w', f'wb={w}', trace_last=20)
        va, vb = (np.loadtxt(os.path.join(x, 'out.txt'))[:, 1] for x in (a, b))
        rec['identity'][ct] = {'wb': w, 'max_abs_dVm_mV': float(np.max(np.abs(va - vb))), 'samples': int(len(va))}
        print('identity', ct, rec['identity'][ct], flush=True)
    jobs = [(s, w) for s in SETTINGS for w in W_GRID]

    def one(job):
        s, w = job
        t0 = time.time()
        par = ','.join([f'wb={w}'] + [f'{k}={v}' for k, v in SETTINGS[s]['par'].items()])
        apd, state, n = steady(f'grid_{s}/w{w:.1f}', par)
        T = target(SETTINGS[s]['heart'], w)
        return s, w, {'par': par, 'beats': int(n), 'steady': bool(np.ptp(apd[-10:]) < 0.5), 'APD90_ms': round(float(apd[-1]), 3),
                      'target_ms': round(T, 3), 'deviation_ms': round(float(apd[-1]) - T, 3), 'state_file': os.path.relpath(state, REPO),
                      'wall_s': round(time.time() - t0, 1)}
    with ThreadPoolExecutor(int(os.environ.get('BLEND_JOBS', '4'))) as ex:
        for s, w, r in ex.map(one, jobs):
            rec['grid'].setdefault(s, {})[f'{w:.1f}'] = r
            print(s, w, {k: r[k] for k in ('APD90_ms', 'target_ms', 'deviation_ms', 'beats', 'steady')}, flush=True)
            json.dump(rec, open(OUT, 'w'), indent=1)
    for s in SETTINGS:
        dev = [abs(r['deviation_ms']) for r in rec['grid'][s].values()]
        rec['grid'][s + '_max_abs_deviation_ms'] = max(dev)
    json.dump(rec, open(OUT, 'w'), indent=1)
    print({s: rec['grid'][s + '_max_abs_deviation_ms'] for s in SETTINGS})


def interp_sv(f0, f1, frac, w, out):
    """The tissue runs' initial state at w: line by line linear interpolation of two grid states (wb set to w)."""
    L0, L1, o = open(f0).read().split('\n'), open(f1).read().split('\n'), []
    for a, b in zip(L0, L1):
        p, q = a.split('#'), b.split('#')
        if len(p) == 2 and p[0].strip() not in ('', '-') and len(q) == 2:
            v = float(w) if p[1].strip() == 'wb' else (1 - frac) * float(p[0]) + frac * float(q[0])
            o.append(f'{v:<20.10g}# {p[1].strip()}')
        else:
            o.append(a)
    open(out, 'w').write('\n'.join(o))


def trace_apd(d):
    import importlib.util
    sp = importlib.util.spec_from_file_location('cell52', os.path.join(C4, 'cell52.py'))
    c52 = importlib.util.module_from_spec(sp); sp.loader.exec_module(c52)
    x = np.loadtxt(os.path.join(d, 'out.txt'))
    return c52.apd90(x[:, 0], x[:, 1])[0], float(x[0, 1])


def midcheck():
    """D44 (c): at each grid midpoint, a cell started from the interpolated state against that w's own steady state:
    first-beat APD90 within 0.5 ms and resting Vm within 0.5 mV (APD90 from the 1 ms trace, cell52.apd90, both sides)."""
    rec = json.load(open(OUT))
    jobs = [(s, round(w + 0.05, 2)) for s in SETTINGS for w in W_GRID[:-1]]

    def one(job):
        s, w = job
        par = ','.join([f'wb={w}'] + [f'{k}={v}' for k, v in SETTINGS[s]['par'].items()])
        apd, state, n = steady(f'mid_{s}/own_w{w:.2f}', par)
        own_rest = read_first(state)
        own_apd, _ = trace_apd(os.path.join(RUN, f'mid_{s}/own_w{w:.2f}', f'chunk_{n - CHUNK:05d}'))
        lo, hi = f'{w - 0.05:.1f}', f'{w + 0.05:.1f}'
        g = rec['grid'][s]
        sv = os.path.join(RUN, f'mid_{s}', f'interp_w{w:.2f}.sv')
        interp_sv(os.path.join(REPO, g[lo]['state_file']), os.path.join(REPO, g[hi]['state_file']), 0.5, w, sv)
        d = bench(f'mid_{s}/interp_w{w:.2f}', 1, 'Tomek52w', par, restore=sv, trace_last=1)
        a1, v0 = trace_apd(d)
        return s, w, {'own_steady_APD90_ms (last beat, trace)': round(own_apd, 3), 'own_rest_Vm_mV': own_rest, 'own_beats': int(n),
                      'interp_first_beat_APD90_ms': round(a1, 3), 'interp_rest_Vm_mV': round(v0, 4),
                      'dAPD90_ms': round(a1 - own_apd, 3), 'dVrest_mV': round(v0 - own_rest, 4),
                      'pass': bool(abs(a1 - own_apd) <= 0.5 and abs(v0 - own_rest) <= 0.5)}
    out = {}
    with ThreadPoolExecutor(int(os.environ.get('BLEND_JOBS', '4'))) as ex:
        for s, w, r in ex.map(one, jobs):
            out.setdefault(s, {})[f'{w:.2f}'] = r
            print(s, w, r, flush=True)
    rec['midcheck_D44c'] = {'grid_spacing': 0.1, 'rule': 'first-beat APD90 within 0.5 ms and resting Vm within 0.5 mV of the own steady state', **out,
                            'all_pass': all(r['pass'] for v in out.values() for r in v.values())}
    json.dump(rec, open(OUT, 'w'), indent=1)
    print('all pass', rec['midcheck_D44c']['all_pass'])


def read_first(f):
    return float(open(f).readline().split('#')[0])


if __name__ == '__main__':
    {'build': build, 'check': check, 'midcheck': midcheck}[sys.argv[1]]()
