"""Tomek52w speed fix (4 Nov 2026): subnormal numbers treated as zero inside the ionic model's compute only.

Cause (LABNOTES 2026-11-04_v52_11_speed): at rest the ICaL gate d sits at the subnormal 1.5316e-322 in every w-grid steady
state, so every v5.2 tissue run starts with it at every resting node, and the products with d run on the CPU's slow
subnormal path (Tomek52w 58.7 s per simulated ms at 375,000 cells against 16.6 s/ms with d = 0).
Build: model_O2's generated Tomek52w.cc / _dyn.cc / .h unchanged except that compute_Tomek52w_cpu sets the SSE control
word's flush-to-zero and denormals-are-zero bits (0x8040) on entry and restores the caller's word on exit (a scope guard,
so it is restored on any exit); same gcc line and -O2 as model_O2 (the recipe is first checked by rebuilding model_O2's
.so unpatched and comparing bytes). Only the ionic model's arithmetic changes: values below 2.2e-308 become 0.
Check (lock rule (1), coordinator relay 4 Nov 09:48 UTC): single cells, CL 1000 ms, 20 beats, w = 0, 0.5 and 1, control
and HF factors (blend52.SETTINGS), from the default state and from blend52's steady state at that w (the tissue start);
the fix against model_O2 (the tissue build so far) and model (-O0, the build behind blend52's checks); identity at
w = 0 / 1 against the built-in Tomek ENDO / EPI as blend52_O2check.json did. Max |dVm| from the 1 ms traces (9 digits),
max |dAPD90| from bench's AP statistics, and the final state files compared line by line.
Usage (repo root, venv): python -B .../ftz52.py build | check | speed
"""
import hashlib
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
SRC, OLD, DST = (os.path.join(ENG, d) for d in ('model_O2', 'model', 'model_O2_ftz'))
RUN = os.path.join(ENG, 'cells', 'ftz_check')
OUT = os.path.join(HERE, 'ftz52_check.json')
sys.path.insert(0, HERE)
import blend52 as B                                                                           # noqa: E402

FILES = ['Tomek52w.cc', 'Tomek52w.h', 'Tomek52w_dyn.cc', 'param_compat_types.hpp']
HEAD = 'void compute_Tomek52w_cpu(node_index_t start, node_index_t end, IonIfBase& imp_base, GlobalData_t **impdata )\n{\n'
GUARD = ('  // ftz52.py: inside this compute, subnormal numbers are treated as zero (SSE flush-to-zero and denormals-are-zero);\n'
         '  // the caller\'s control word is restored on every exit\n'
         '  struct Ftz52Guard { unsigned int saved; Ftz52Guard() : saved(_mm_getcsr()) { _mm_setcsr(saved | 0x8040u); }\n'
         '                      ~Ftz52Guard() { _mm_setcsr(saved); } } ftz52_guard;\n')


def sha(f):
    return hashlib.sha256(open(f, 'rb').read()).hexdigest()


def gcc_line(folder):
    """model/build.log's gcc line with -O2, every path in model/ moved to folder."""
    line = [l for l in open(os.path.join(OLD, 'build.log')) if l.startswith('/usr/bin/gcc ')][0].strip()
    line = line.replace(OLD + '/', folder + '/').replace('-I' + OLD + ' ', '-I' + folder + ' ')
    assert OLD + '/' not in line and '-I' + OLD + ' ' not in line
    return line.replace('/usr/bin/gcc ', '/usr/bin/gcc -O2 ', 1)


def compile_in(folder, log):
    cmd = gcc_line(folder)
    log.write(f'$ {cmd}\n'); log.flush()
    subprocess.run(cmd, shell=True, cwd=folder, stdout=log, stderr=subprocess.STDOUT, check=True)
    return cmd


def build():
    rec = {'source': os.path.relpath(SRC, REPO), 'source_sha256': {f: sha(os.path.join(SRC, f)) for f in FILES}}
    assert all(sha(os.path.join(SRC, f)) == sha(os.path.join(OLD, f)) for f in FILES[:3]), 'model_O2 sources differ from model/'
    re_dir = os.path.join(DST, 'recipe_check')
    os.makedirs(re_dir, exist_ok=True)
    with open(os.path.join(DST, 'build_ftz.log'), 'w') as log:
        for f in FILES:
            shutil.copy(os.path.join(SRC, f), re_dir)
        rec['recipe_cmd'] = compile_in(re_dir, log)
        rec['recipe_so_sha256'] = sha(os.path.join(re_dir, 'Tomek52w.so'))
        rec['model_O2_so_sha256'] = sha(os.path.join(SRC, 'Tomek52w.so'))
        rec['recipe_reproduces_model_O2_bytes'] = rec['recipe_so_sha256'] == rec['model_O2_so_sha256']
        for f in FILES:
            shutil.copy(os.path.join(SRC, f), DST)
        cc = open(os.path.join(DST, 'Tomek52w.cc')).read()
        assert cc.count(HEAD) == 1 and 'ftz52' not in cc
        cc = '#include <xmmintrin.h>   // ftz52.py\n' + cc.replace(HEAD, HEAD + GUARD)
        open(os.path.join(DST, 'Tomek52w.cc'), 'w').write(cc)
        rec['patched_cc_sha256'] = sha(os.path.join(DST, 'Tomek52w.cc'))
        rec['cmd'] = compile_in(DST, log)
        rec['so_sha256'] = sha(os.path.join(DST, 'Tomek52w.so'))
    d = subprocess.run(['diff', os.path.join(SRC, 'Tomek52w.cc'), os.path.join(DST, 'Tomek52w.cc')], capture_output=True, text=True).stdout
    rec['diff_vs_model_O2_cc'] = d
    json.dump({'build': rec}, open(OUT, 'w'), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k not in ('recipe_cmd', 'cmd')}, indent=1))


def bench(tag, so, imp, par, restore=None, nbeats=20):
    d = os.path.join(RUN, tag); os.makedirs(d, exist_ok=True)
    dur = nbeats * B.BCL
    cmd = ['bench', f'--imp={imp}', f'--imp-par={par}', f'--numstim={nbeats}', f'--bcl={B.BCL}', f'--duration={dur}',
           '--APstatistics', '--fout=out', '--dt-out=1', '--start-out=0', '--save-ini-file=end.sv', f'--save-ini-time={dur}']
    if so:
        cmd.insert(1, f'--load-module={so}')
    if restore:
        cmd.append(f'--read-ini-file={restore}')
    t0 = time.time()
    with open(os.path.join(d, 'bench.log'), 'w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d, check=True)
    return d, round(time.time() - t0, 1)


def compare(a, b):
    va, vb = (np.loadtxt(os.path.join(x, 'out.txt'))[:, 1] for x in (a, b))
    pa, pb = (np.loadtxt(os.path.join(x, 'out_AP_stats.dat'), comments='#', usecols=(3,), ndmin=1) for x in (a, b))
    la, lb = (open(os.path.join(x, 'end.sv')).read().split('\n') for x in (a, b))
    return {'samples': int(len(va)), 'max_abs_dVm_mV': float(np.max(np.abs(va - vb))), 'beats': int(len(pa)),
            'max_abs_dAPD90_ms': float(np.max(np.abs(pa - pb))) if len(pa) == len(pb) else None,
            'end_state_lines_differing': [x.split('#')[-1].strip() + f': {x.split("#")[0].strip()} vs {y.split("#")[0].strip()}'
                                          for x, y in zip(la, lb) if x != y]}


def check():
    rec = json.load(open(OUT)) if os.path.exists(OUT) else {}
    grid = json.load(open(B.OUT))['grid']
    so = {'ftz': os.path.join(DST, 'Tomek52w.so'), 'O2': os.path.join(SRC, 'Tomek52w.so'), 'O0': os.path.join(OLD, 'Tomek52w.so')}
    jobs = []
    for s in B.SETTINGS:
        for w in (0.0, 0.5, 1.0):
            par = ','.join([f'wb={w}'] + [f'{k}={v}' for k, v in B.SETTINGS[s]['par'].items()])
            st = os.path.join(REPO, grid[s][f'{w:.1f}']['state_file'])
            for build_ in so:
                jobs.append((f'{s}_w{w:.1f}_default_{build_}', so[build_], 'Tomek52w', par, None))
            for build_ in ('ftz', 'O2'):
                jobs.append((f'{s}_w{w:.1f}_steady_{build_}', so[build_], 'Tomek52w', par, st))
    for ct, w in (('ENDO', 0.0), ('EPI', 1.0)):
        jobs.append((f'identity_builtin_{ct}', None, 'Tomek', f'flags={ct}', None))
        jobs.append((f'identity_ftz_w{w:g}', so['ftz'], 'Tomek52w', f'wb={w}', None))
    with ThreadPoolExecutor(int(os.environ.get('BLEND_JOBS', '4'))) as ex:
        res = dict(zip([j[0] for j in jobs], ex.map(lambda j: bench(j[0], j[1], j[2], j[3], j[4]), jobs)))
    out = {'so_sha256': {k: sha(v) for k, v in so.items()}, 'wall_s': {k: v[1] for k, v in res.items()}, 'pairs': {}}
    for s in B.SETTINGS:
        for w in ('0.0', '0.5', '1.0'):
            for start, ref in (('default', 'O2'), ('default', 'O0'), ('steady', 'O2')):
                out['pairs'][f'{s}_w{w}_{start}: ftz vs {ref}'] = compare(res[f'{s}_w{w}_{start}_ftz'][0], res[f'{s}_w{w}_{start}_{ref}'][0])
    for ct, w in (('ENDO', '0'), ('EPI', '1')):
        out['pairs'][f'identity {ct}: ftz w{w} vs built-in'] = compare(res[f'identity_ftz_w{w}'][0], res[f'identity_builtin_{ct}'][0])
    tissue = [v for k, v in out['pairs'].items() if 'identity' not in k]
    out['max_abs_dVm_mV_vs_tissue_builds'] = max(v['max_abs_dVm_mV'] for v in tissue)
    out['max_abs_dAPD90_ms_vs_tissue_builds'] = max(v['max_abs_dAPD90_ms'] for v in tissue)
    out['identity_max_abs_dVm_mV'] = {k: v['max_abs_dVm_mV'] for k, v in out['pairs'].items() if 'identity' in k}
    rec['check'] = out
    json.dump(rec, open(OUT, 'w'), indent=1)
    for k, v in out['pairs'].items():
        print(k, v['max_abs_dVm_mV'], v['max_abs_dAPD90_ms'], len(v['end_state_lines_differing']), flush=True)
    print('max |dVm| vs tissue builds', out['max_abs_dVm_mV_vs_tissue_builds'], 'max |dAPD90|', out['max_abs_dAPD90_ms_vs_tissue_builds'])


def speed():
    """375,000 cells x 2 ms from the control w = 0.5 steady state, no stimulus in the window (the tissue start)."""
    rec = json.load(open(OUT))
    d = os.path.join(ENG, 'speed'); st = os.path.join(d, 'st_sub.sv')
    par = 'sGKs_endo=1.349859,sGKs_epi=0.740818,wb=0.5'
    r = {}
    for k, so in (('ftz', os.path.join(DST, 'Tomek52w.so')),):
        with open(os.path.join(d, f'r_{k}.txt'), 'w') as log:
            subprocess.run(['bench', f'--load-module={so}', '-I', 'Tomek52w', f'--imp-par={par}', '-R', st, '-n', '375000', '-a', '2',
                            '-i', '10000', '--no-trace'], stdout=log, stderr=subprocess.STDOUT, cwd=d, check=True)
        r[k] = float(re.search(r'main loop time\s+([\d.]+)', open(os.path.join(d, f'r_{k}.txt')).read()).group(1))
    for k in ('sub', 'd0'):
        r[{'sub': 'O2', 'd0': 'O2_d_set_0'}[k]] = float(re.search(r'main loop time\s+([\d.]+)', open(os.path.join(d, f'r_{k}.txt')).read()).group(1))
    rec['speed_375k_cells_2ms_s'] = r
    json.dump(rec, open(OUT, 'w'), indent=1)
    print(r)


def read_igb(f):
    raw = open(f, 'rb').read()
    hdr = raw[:1024].decode('latin1')
    n = int(re.search(r'x:(\d+)', hdr).group(1))
    return np.frombuffer(raw[1024:], np.float32).reshape(-1, n)


def tissue():
    """Step 6's flat block (not a heart): monodomain, one process, control factors at w = 0.5 from the w = 0.5 steady
    state, step 6's control fibre-axis stimulus and conductivities, 30 ms; once per library, every Vm frame compared."""
    rec = json.load(open(OUT))
    slab = os.path.join(REPO, 'runs', 'v52_2026-10-20', '06_mono', 'slab')
    ref = os.path.join(slab, 'control_r0_fibre', 'parameters.par')
    g = {l.split('=')[0].strip(): l.split('=')[1].strip() for l in open(ref) if l.startswith('gregion[0].')}
    st = os.path.join(REPO, json.load(open(B.OUT))['grid']['control']['0.5']['state_file'])
    par = 'wb=0.5,' + ','.join(f'{k}={v}' for k, v in B.SETTINGS['control']['par'].items())
    procs, out = {}, {}
    for k, so in (('O2', os.path.join(SRC, 'Tomek52w.so')), ('ftz', os.path.join(DST, 'Tomek52w.so'))):
        d = os.path.join(ENG, 'speed', f'slab_{k}')
        cmd = ['openCARP', '-meshname', os.path.join(slab, 'slab'), '-simID', d, '-bidomain', '0', '-dt', '10', '-parab_solve', '1',
               '-tend', '30', '-spacedt', '1', '-timedt', '5', '-num_external_imp', '1', '-external_imp[0]', so,
               '-num_imp_regions', '1', '-imp_region[0].im', 'Tomek52w', '-imp_region[0].im_param', par, '-imp_region[0].im_sv_init', st,
               '-num_stim', '1', '-stim[0].crct.type', '0', '-stim[0].elec.vtx_file', os.path.join(slab, 'control_r0_fibre', 'stim'),
               '-stim[0].pulse.strength', '400.0', '-stim[0].ptcl.duration', '1.0', '-stim[0].ptcl.npls', '1',
               '-num_gregions', '1', '-gregion[0].num_IDs', '1', '-gregion[0].ID[0]', '1']
        for a in ('g_il', 'g_el', 'g_it', 'g_et', 'g_in', 'g_en'):
            cmd += [f'-gregion[0].{a}', g[f'gregion[0].{a}']]
        os.makedirs(d, exist_ok=True)
        procs[k] = (subprocess.Popen(cmd, stdout=open(os.path.join(d, 'run.log'), 'w'), stderr=subprocess.STDOUT, cwd=d), d, time.time())
    for k, (p, d, t0) in procs.items():
        out[k] = {'exit': p.wait(), 'wall_s': round(time.time() - t0, 1), 'dir': os.path.relpath(d, REPO)}
    a, b = (read_igb(os.path.join(REPO, out[k]['dir'], 'vm.igb')) for k in ('O2', 'ftz'))
    out['frames'] = [int(len(a)), int(len(b))]
    out['nodes'] = int(a.shape[1])
    out['bitwise_identical_vm'] = bool(a.shape == b.shape and np.array_equal(a.view(np.uint32), b.view(np.uint32)))
    out['max_abs_dVm_mV'] = float(np.max(np.abs(a.astype(np.float64) - b))) if a.shape == b.shape else None
    out['frames_differing'] = int(np.sum(np.any(a != b, axis=1))) if a.shape == b.shape else None
    out['vm_max_mV_last_frame_O2'] = float(a[-1].max())     # flat block, not a heart: a sanity check that the wave ran
    rec['tissue_flat_block'] = out
    json.dump(rec, open(OUT, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    {'build': build, 'check': check, 'speed': speed, 'tissue': tissue}[sys.argv[1]]()
