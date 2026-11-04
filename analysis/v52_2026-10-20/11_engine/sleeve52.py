"""D44 (d) (lock thread 3 Nov 2026, Alex "Adopt both" 13:13:21 UTC; D47 for every v5.2 monodomain beat): keep every
element of the HF hearts' sleeves and make the fibrous-layer nodes non-excitable by a nodal factor on INa, INaL and ICaL.

Model: Tomek52w.model (this folder) with one nodal parameter fexc (default 1; an openCARP adjustment sets it per node:
0 at heart52's non-excitable nodes, 1 elsewhere, as wb is set), multiplying
  - INa at its definition (so Iion and the Na balance both see it),
  - INaL at its definition,
  - PCa, the L-type channel's permeability, so ICaL_ss / ICaL_i and the same channel's Na and K components (ICaNa,
    ICaK: PCaNa = 0.00125 PCa, PCaK = 3.574e-4 PCa, PCap = 1.1 PCa) and the Ca fluxes and Jrel trigger that use them.
    Reading (reported to the lock thread): "ICaL" is taken as ToR-ORd's L-type channel, whose ICaNa and ICaK are the
    same channel's monovalent currents; a non-myocyte node has no L-type channel.
The model name stays Tomek52w, so every existing adjustment and setting carries over. Build as ftz52.py: limpet's
make_dynamic_model.sh in runs/.../11_engine/model_fexc (generated sources, its own -O0 library), then the generated
sources copied to model_fexc_O2_ftz with ftz52's flush-to-zero guard and compiled with the same gcc line and -O2.
Checks (D44 (d)): (1) fexc = 1: single cells, CL 1000 ms, 20 beats, w = 0 / 0.5 / 1, control and HF factors, from the
default state and from blend52's steady state, against the tissue build so far (model_O2_ftz) and the -O0 build behind
blend52's checks (model): max |dVm| (1 ms traces) and max |dAPD90|; identity against the built-in Tomek at w 0 / 1.
(2) fexc = 0: from the same steady states, one 1 ms stimulus at twice the normal cell's threshold amplitude at that w and
heart type (foot52.json 'threshold'): no action potential (Vm stays below 0 mV for 100 ms); peak Vm reported.
bench reads a state file by position and fexc adds a line, so every steady state given to this build is first rewritten
in its order by variable name (convert_sv), with fexc set (1 for check 1, 0 for check 2); the tissue runs set both wb and
fexc by named adjustments, so they are not affected.
Usage (repo root, venv, PATH): python -B .../sleeve52.py build | check
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
ENG = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine')
GEN, DST = os.path.join(ENG, 'model_fexc'), os.path.join(ENG, 'model_fexc_O2_ftz')
OUT = os.path.join(HERE, 'sleeve52_check.json')
RUN = os.path.join(ENG, 'cells', 'fexc_check')
sys.path.insert(0, HERE)
import blend52 as B                                                                           # noqa: E402
import ftz52 as F                                                                             # noqa: E402

EDITS = [   # (pattern line start, old text, new text): each must match exactly once
    ('wb = 0.0; .units(unitless); .param(); .nodal();',
     'wb = 0.0; .units(unitless); .param(); .nodal();\n'
     '# v5.2 D44 (d) (sleeve52.py): nodal excitability factor on INa, INaL and the L-type channel (PCa), 0 at fibrous-layer nodes\n'
     'fexc = 1.0; .units(unitless); .param(); .nodal();'),
    ('INa = (GNa*(V - ENa)*', 'INa = (fexc*GNa*(V - ENa)*'),
    ('INaL = (GNaL*(V - ENa)*', 'INaL = (fexc*GNaL*(V - ENa)*'),
    ('PCa = (((1.-wb)*PCa_b)+(wb*(PCa_b*1.2)));', 'PCa = (fexc*(((1.-wb)*PCa_b)+(wb*(PCa_b*1.2))));'),
]


def sha(f):
    return F.sha(f)


def build():
    src = open(os.path.join(HERE, 'Tomek52w.model')).read()
    for old, new in EDITS:
        assert src.count(old) == 1, old
        src = src.replace(old, new)
    os.makedirs(GEN, exist_ok=True)
    open(os.path.join(GEN, 'Tomek52w.model'), 'w').write(src)
    shutil.copy(os.path.join(F.OLD, 'param_compat_types.hpp'), GEN)
    with open(os.path.join(GEN, 'build.log'), 'w') as log:
        subprocess.run(['make_dynamic_model.sh', 'Tomek52w'], cwd=GEN, stdout=log, stderr=subprocess.STDOUT, check=True)
    line = [l for l in open(os.path.join(GEN, 'build.log')) if l.startswith('/usr/bin/gcc ')][0].strip()
    os.makedirs(DST, exist_ok=True)
    for f in F.FILES:
        shutil.copy(os.path.join(GEN, f), DST)
    shutil.copy(os.path.join(GEN, 'Tomek52w.model'), DST)
    cc = open(os.path.join(DST, 'Tomek52w.cc')).read()
    assert cc.count(F.HEAD) == 1 and 'ftz52' not in cc
    open(os.path.join(DST, 'Tomek52w.cc'), 'w').write('#include <xmmintrin.h>   // ftz52.py\n' + cc.replace(F.HEAD, F.HEAD + F.GUARD))
    cmd = line.replace(GEN + '/', DST + '/').replace('-I' + GEN + ' ', '-I' + DST + ' ')
    assert GEN + '/' not in cmd and '-I' + GEN + ' ' not in cmd
    cmd = cmd.replace('/usr/bin/gcc ', '/usr/bin/gcc -O2 ', 1)
    with open(os.path.join(DST, 'build_O2_ftz.log'), 'w') as log:
        log.write(f'$ {cmd}\n'); log.flush()
        subprocess.run(cmd, shell=True, cwd=DST, stdout=log, stderr=subprocess.STDOUT, check=True)
    gen_cc = open(os.path.join(GEN, 'Tomek52w.cc')).read()
    rec = {'model': os.path.relpath(os.path.join(DST, 'Tomek52w.model'), REPO), 'model_sha256': sha(os.path.join(DST, 'Tomek52w.model')),
           'edits': [e[1] for e in EDITS], 'gcc': cmd, 'so': os.path.relpath(os.path.join(DST, 'Tomek52w.so'), REPO),
           'so_sha256': sha(os.path.join(DST, 'Tomek52w.so')), 'O0_so_sha256': sha(os.path.join(GEN, 'Tomek52w.so')),
           'fexc_uses_in_generated_cc': len(re.findall(r'\bfexc\b', gen_cc)),
           'diff_model_vs_Tomek52w': subprocess.run(['diff', os.path.join(HERE, 'Tomek52w.model'), os.path.join(DST, 'Tomek52w.model')],
                                                    capture_output=True, text=True).stdout}
    json.dump({'build': rec}, open(OUT, 'w'), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != 'gcc'}, indent=1))


def layout():
    """The new build's state-file order (bench reads a state file by position, and fexc adds a line)."""
    d = os.path.join(RUN, 'layout'); os.makedirs(d, exist_ok=True)
    subprocess.run(['bench', f'--load-module={os.path.join(DST, "Tomek52w.so")}', '--imp=Tomek52w', '--duration=1', '--save-ini-file=new.sv',
                    '--save-ini-time=1', '--no-trace'], stdout=open(os.path.join(d, 'bench.log'), 'w'), stderr=subprocess.STDOUT, cwd=d, check=True)
    return [l.split('#')[-1].strip() if '#' in l else None for l in open(os.path.join(d, 'new.sv')).read().split('\n')], open(os.path.join(d, 'new.sv')).read().split('\n')


def convert_sv(old, fexc, out):
    """blend52's steady state rewritten in the new build's order by variable name, fexc set; every other value as written."""
    names, lines = layout()
    val = {l.split('#')[-1].strip(): l.split('#')[0].strip() for l in open(old).read().split('\n') if '#' in l}
    o = []
    for n, l in zip(names, lines):
        if n is None:
            o.append(l)
        elif n == 'fexc':
            o.append(f'{fexc:<20g}# fexc')
        else:
            o.append(f'{val[n]:<20s}# {n}')
    assert set(val) | {'fexc'} == {n for n in names if n}
    open(out, 'w').write('\n'.join(o))
    return out


def compare(a, b):
    """ftz52.compare, with the end states matched by variable name (fexc adds a line to this build's state file)."""
    r = F.compare(a, b)
    sa, sb = ({l.split('#')[-1].strip(): l.split('#')[0].strip() for l in open(os.path.join(x, 'end.sv')) if '#' in l} for x in (a, b))
    r['end_state_lines_differing'] = [f'{k}: {sa[k]} vs {sb[k]}' for k in sorted(set(sa) & set(sb)) if sa[k] != sb[k]]
    r['end_state_only_in_first'] = sorted(set(sa) - set(sb))
    return r


def silent_one(job):
    s, w, amp = job
    d = os.path.join(RUN, f'fexc0_{s}_w{w:.1f}'); os.makedirs(d, exist_ok=True)
    par = ','.join([f'wb={w}', 'fexc=0'] + [f'{k}={v}' for k, v in B.SETTINGS[s]['par'].items()])
    st = convert_sv(os.path.join(REPO, json.load(open(B.OUT))['grid'][s][f'{w:.1f}']['state_file']), 0, os.path.join(d, 'start_fexc0.sv'))
    cmd = ['bench', f'--load-module={os.path.join(DST, "Tomek52w.so")}', '--imp=Tomek52w', f'--imp-par={par}', f'--read-ini-file={st}',
           f'--stim-curr={amp!r}', '--stim-dur=1', '--numstim=1', '--stim-start=1', '--duration=101', '--dt-out=0.01', '--fout=out', '--no-trace']
    subprocess.run(cmd, stdout=open(os.path.join(d, 'bench.log'), 'w'), stderr=subprocess.STDOUT, cwd=d, check=True)
    x = np.loadtxt(os.path.join(d, 'out.txt'))
    on = x[:, 0] >= 1.0
    return s, w, {'stim_uA_cm2': amp, 'Vmax_mV': float(x[on, 1].max()), 't_Vmax_ms': float(x[on, 0][np.argmax(x[on, 1])]),
                  'Vm_end_100ms_mV': float(x[-1, 1]), 'fires': bool(x[on, 1].max() > 0.0)}


def check():
    rec = json.load(open(OUT))
    grid = json.load(open(B.OUT))['grid']
    thr = json.load(open(os.path.join(HERE, 'foot52.json')))['threshold']
    so = {'fexc1': os.path.join(DST, 'Tomek52w.so'), 'ftz': os.path.join(F.DST, 'Tomek52w.so'), 'O0': os.path.join(F.OLD, 'Tomek52w.so')}
    F.RUN = RUN
    jobs = []
    for s in B.SETTINGS:
        for w in (0.0, 0.5, 1.0):
            par = ','.join([f'wb={w}'] + [f'{k}={v}' for k, v in B.SETTINGS[s]['par'].items()])
            st = os.path.join(REPO, grid[s][f'{w:.1f}']['state_file'])
            os.makedirs(os.path.join(RUN, 'starts'), exist_ok=True)
            st1 = convert_sv(st, 1, os.path.join(RUN, 'starts', f'{s}_w{w:.1f}_fexc1.sv'))
            for k in so:
                jobs.append((f'{s}_w{w:.1f}_default_{k}', so[k], 'Tomek52w', par, None))
            jobs.append((f'{s}_w{w:.1f}_steady_fexc1', so['fexc1'], 'Tomek52w', par, st1))
            jobs.append((f'{s}_w{w:.1f}_steady_ftz', so['ftz'], 'Tomek52w', par, st))
    for ct, w in (('ENDO', 0.0), ('EPI', 1.0)):
        jobs.append((f'identity_builtin_{ct}', None, 'Tomek', f'flags={ct}', None))
        jobs.append((f'identity_fexc1_w{w:g}', so['fexc1'], 'Tomek52w', f'wb={w}', None))
    with ThreadPoolExecutor(4) as ex:
        res = dict(zip([j[0] for j in jobs], ex.map(lambda j: F.bench(j[0], j[1], j[2], j[3], j[4]), jobs)))
    pairs = {}
    for s in B.SETTINGS:
        for w in ('0.0', '0.5', '1.0'):
            for start, ref in (('default', 'ftz'), ('default', 'O0'), ('steady', 'ftz')):
                pairs[f'{s}_w{w}_{start}: fexc=1 vs {ref}'] = compare(res[f'{s}_w{w}_{start}_fexc1'][0], res[f'{s}_w{w}_{start}_{ref}'][0])
    for ct, w in (('ENDO', '0'), ('EPI', '1')):
        pairs[f'identity {ct}: fexc=1 w{w} vs built-in'] = compare(res[f'identity_fexc1_w{w}'][0], res[f'identity_builtin_{ct}'][0])
    tissue = [v for k, v in pairs.items() if 'identity' not in k]
    c1 = {'pairs': pairs, 'max_abs_dVm_mV': max(v['max_abs_dVm_mV'] for v in tissue), 'max_abs_dAPD90_ms': max(v['max_abs_dAPD90_ms'] for v in tissue),
          'identity_max_abs_dVm_mV': {k: v['max_abs_dVm_mV'] for k, v in pairs.items() if 'identity' in k},
          'end_state_lines_differing_tissue_pairs': sorted({x for v in tissue for x in v['end_state_lines_differing']})}
    jobs2 = [(s, w, 2.0 * thr[s][f'{w:.1f}']['weakest_firing']['amp']) for s in B.SETTINGS for w in (0.0, 0.5, 1.0)]
    c2 = {}
    with ThreadPoolExecutor(4) as ex:
        for s, w, r in ex.map(silent_one, jobs2):
            c2.setdefault(s, {})[f'{w:.1f}'] = r
    c2['any_fires'] = any(r['fires'] for s in B.SETTINGS for r in c2[s].values())
    rec['check1_fexc1'] = c1; rec['check2_fexc0'] = c2
    json.dump(rec, open(OUT, 'w'), indent=1)
    for k, v in pairs.items():
        print(k, v['max_abs_dVm_mV'], v['max_abs_dAPD90_ms'], flush=True)
    print('check 1 max |dVm|', c1['max_abs_dVm_mV'], 'max |dAPD90|', c1['max_abs_dAPD90_ms'], 'state lines differing', c1['end_state_lines_differing_tissue_pairs'])
    print('check 2', {s: {w: (round(r['Vmax_mV'], 3), r['fires']) for w, r in c2[s].items()} for s in B.SETTINGS}, 'any fires', c2['any_fires'])


if __name__ == '__main__':
    {'build': build, 'check': check}[sys.argv[1]]()
