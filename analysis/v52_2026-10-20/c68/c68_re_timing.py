"""C68 (lock thread, 26 Oct 2026): RE+ timing test on the frozen v5.1 control heart. Timing only; outside the hold.

Inputs, frozen v5.1 only (never checked out in this working tree): a copy made by `git archive v5.1` plus the v5.1
monodomain check's two committed files at its last commit 6cdbabc (params/v51_mono_conductivities.json,
analysis/v51_2026-10-15/08_monodomain/mono51.py), in runs/v52_2026-10-20/c68_timing/v51_copy/, with data/ and runs/ (the v5.1
build's mesh and template run) read in place through symlinks (not versioned; read only). Y5HYEDL4's v5.1 mesh (the monodomain check's biv51), fibres and
speeds (params/v51_speeds.json: 600 / 360 / 480 mm/s as dream.vel_l / vel_t / vel_n), and from the monodomain check its
cell model (Tomek), its tuned conductivities (RE+'s diffusion term), its dt (10 us) and its stimulus (400 uA/cm3 x 1 ms
on the nodes within 1.5 mm of the site at 0 ms) and its one-way replay of v5.1's network junction exit times (mono51.py
graph_beat(): exit = network time + 4 ms where the junction sets its muscle, nodes within 1.0 mm, 0.25 ms bins).
RE+: -dream.solve 1, eikonal physics region (ptype 2) on tags 1 and 2, monodomain (-bidomain 0), no elliptic solve and
no ECG; dream.fim.tol 0.001 and dream.fim.max_iter 1e9 as v5.1's acceptance-C runs; Vm every 1 ms (-spacedt 1), act and
rpt as RE+ writes them, into a folder marked timing-only. One MPI process (mpiexec -n 1); this openCARP links no OpenMP
runtime, so one single-threaded run per stage. Nothing is tuned.
Site: the first lv_septum site of Y5HYEDL4's sites.json that is none of the 9 gate-9 check sites, not
lv_free_wall_original_d0 and none of bias_sites51.json's sites (C68 (4)).
Stages (repo root, venv; alone):  prep | run short|full [try] | check short|full [try]
  run: /usr/bin/time -v; MemAvailable every 10 s to logs/mem_<stage>.tsv; killed if MemAvailable < 1,024 MB; stopped as a
  hang if the first progress line does not come within 30 min or simulated time stops advancing for 30 min.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
H = 'Y5HYEDL4'
ROOT = os.path.join(REPO, 'runs', 'v52_2026-10-20', 'c68_timing')
COPY = os.path.join(ROOT, 'v51_copy')
LOGS = os.path.join(ROOT, 'logs')
MONO_COMMIT = '6cdbabc'
TEND = {'short': 50.0, 'full': 565.0}
MIN_MB, HANG_S = 1024, 1800
MESH = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', H, 'acceptance_c', 'mesh', 'biv51')


def git(*a, cwd=REPO):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, check=True).stdout


def tdir(stage):
    return os.path.join(ROOT, f'timing_only_{stage}')


def mem_avail_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


def c_free_bytes():
    try:
        return int(subprocess.run(['powershell.exe', '-NoProfile', '-Command', '(Get-PSDrive C).Free'], capture_output=True, timeout=30).stdout.split()[0])
    except Exception:
        return None


def prep():
    os.makedirs(LOGS, exist_ok=True)
    st = {'v52_git_status_before': git('status', '--porcelain').decode(), 'v52_head': git('rev-parse', '--short', 'HEAD').decode().strip()}
    if not os.path.exists(os.path.join(COPY, 'analysis')):
        os.makedirs(COPY, exist_ok=True)
        subprocess.run(f'git archive v5.1 | tar -x -C {COPY}', shell=True, cwd=REPO, check=True)
        for p in ('params/v51_mono_conductivities.json', 'analysis/v51_2026-10-15/08_monodomain/mono51.py'):
            os.makedirs(os.path.dirname(os.path.join(COPY, p)), exist_ok=True)
            open(os.path.join(COPY, p), 'wb').write(git('show', f'{MONO_COMMIT}:{p}'))
    for d in ('data', 'runs'):
        if not os.path.lexists(os.path.join(COPY, d)):
            os.symlink(os.path.join(REPO, d), os.path.join(COPY, d))
    st['copy'] = {'v51_tag_commit': git('rev-parse', 'v5.1^{commit}').decode().strip(), 'mono_files_from': MONO_COMMIT,
                  'data, runs': 'symlinks to the live data/ and runs/ (not versioned; read only: v5.1 data, template run, v5.1 mesh)'}
    sys.path.insert(0, os.path.join(COPY, 'analysis', 'v51_2026-10-15', '04_build'))
    sys.path.insert(0, os.path.join(COPY, 'analysis', 'v51_2026-10-15', '08_monodomain'))
    sys.modules.pop('common', None)
    import heart51 as H51
    import mono51 as M51
    assert os.path.dirname(os.path.abspath(H51.__file__)).startswith(COPY) and os.path.dirname(os.path.abspath(M51.__file__)).startswith(COPY)
    sites = json.load(open(os.path.join(REPO, 'data', 'biv', H, 'sites.json')))
    excl = {s['id'] for s in M51.check_sites(H)}
    bias = json.load(open(os.path.join(COPY, 'analysis', 'v51_2026-10-15', '08_monodomain', 'bias_sites51.json')))['hearts'][H] \
        if os.path.exists(os.path.join(COPY, 'analysis', 'v51_2026-10-15', '08_monodomain', 'bias_sites51.json')) else \
        json.load(open(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '08_monodomain', 'bias_sites51.json')))['hearts'][H]
    excl |= set(bias['check']) | set(bias['new'].values()) | set(bias['covered'].values())
    site = next(s for s in sites if s['family'] == 'lv_septum' and s['id'] not in excl)
    Hh = H51.Heart51(H)
    par = json.load(open(os.path.join(COPY, 'params', 'v51_mono_conductivities.json')))['hearts'][H]
    assert par['within_3pct']
    sp = json.load(open(os.path.join(COPY, 'params', 'v51_speeds.json')))['hearts'][H]
    T, jx, ball = M51.graph_beat(H51, Hh, int(site['node']))
    from scipy.spatial import cKDTree
    tree = cKDTree(Hh.pts_um)
    sd = os.path.join(ROOT, 'stims'); os.makedirs(sd, exist_ok=True)
    M51.vtx_write(os.path.join(sd, 'site.vtx'), ball)
    stims = [(os.path.join(sd, 'site'), 0.0)]
    jn = np.array([a for a, _ in jx]); jt = np.round(np.array([b for _, b in jx]) / M51.BIN_MS) * M51.BIN_MS
    for k, tb in enumerate(np.unique(jt)):
        wide = np.unique(np.concatenate([tree.query_ball_point(Hh.pts_um[n], M51.PMJ_R_UM) for n in jn[jt == tb]]).astype(np.int64))
        M51.vtx_write(os.path.join(sd, f'pmj_{k:04d}.vtx'), wide)
        stims.append((os.path.join(sd, f'pmj_{k:04d}'), float(tb)))
    cfg = {'heart': H, 'site': site['id'], 'site_node': int(site['node']), 'site_family': site['family'], 'excluded_sites': sorted(excl),
           'graph_total_activation_ms': round(float(T.max()), 2), 'junction_exits_replayed': len(jx), 'stimuli': len(stims),
           'site_ball_nodes': int(len(ball)), 'mesh': MESH, 'conductivities_S_m': par['conductivities_S_m'],
           'speeds_mm_s': {k: 1000.0 * sp[a] for k, a in (('l', 'fibre'), ('t', 'sheet'), ('n', 'normal'))},
           'stims': [{'vtx': v, 'start_ms': t0} for v, t0 in stims], **st}
    json.dump(cfg, open(os.path.join(ROOT, 'c68_config.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in cfg.items() if k not in ('stims', 'excluded_sites', 'v52_git_status_before')}, indent=1))


def stims_in_window(stage):
    """openCARP refuses a stimulus that does not end by tend (start + 1 ms > tend): in run (a) the junction exits after
    49 ms are left out (they cannot fire inside its 50 ms window); run (b) keeps all of them."""
    cfg = json.load(open(os.path.join(ROOT, 'c68_config.json')))
    return [s for s in cfg['stims'] if s['start_ms'] + 1.0 <= TEND[stage]], len(cfg['stims'])


def command(stage, name):
    cfg = json.load(open(os.path.join(ROOT, 'c68_config.json')))
    g, v = cfg['conductivities_S_m'], cfg['speeds_mm_s']
    stims, _ = stims_in_window(stage)
    so = ['-num_stim', len(stims)]
    for i, s in enumerate(stims):
        so += [f'-stim[{i}].crct.type', 0, f'-stim[{i}].elec.vtx_file', s['vtx'], f'-stim[{i}].ptcl.start', s['start_ms'],
               f'-stim[{i}].pulse.strength', 400.0, f'-stim[{i}].ptcl.duration', 1.0, f'-stim[{i}].ptcl.npls', 1]
    gr = ['-num_gregions', 1, '-gregion[0].num_IDs', 2, '-gregion[0].ID[0]', 1, '-gregion[0].ID[1]', 2,
          '-gregion[0].g_il', g['fibre']['gi'], '-gregion[0].g_el', g['fibre']['ge'],
          '-gregion[0].g_it', g['sheet']['gi'], '-gregion[0].g_et', g['sheet']['ge'],
          '-gregion[0].g_in', g['normal']['gi'], '-gregion[0].g_en', g['normal']['ge'],
          '-gregion[0].dream.vel_l', v['l'], '-gregion[0].dream.vel_t', v['t'], '-gregion[0].dream.vel_n', v['n']]
    return ['/usr/bin/time', '-v', 'mpiexec', '-n', 1, 'openCARP', '-meshname', MESH, '-simID', tdir(name),
            '-bidomain', 0, '-dt', 10.0, '-parab_solve', 1, '-tend', TEND[stage], '-spacedt', 1.0, '-timedt', 5.0,
            '-dream.solve', 1, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', 1000000000,
            '-num_phys_regions', 1, '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1, '-phys_region[0].ID[1]', 2,
            '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek'] + so + gr


def progress(logf):
    """Simulated times (ms) of openCARP's progress lines so far."""
    try:
        txt = open(logf, errors='replace').read()
    except OSError:
        return []
    return [float(m.group(1)) for m in re.finditer(r'^\s*(\d+\.\d+)\t[\d.]+\t', txt, re.M)]


def run(stage, tag=''):
    name = stage + (f'_try{tag}' if tag else '')        # a retry gets its own folder and logs (nothing is overwritten)
    os.makedirs(LOGS, exist_ok=True)
    out = tdir(name)
    if os.path.exists(out):
        sys.exit(f'{out} exists; stop (nothing is overwritten)')
    os.makedirs(out)
    open(os.path.join(out, 'TIMING_ONLY_README.txt'), 'w').write(
        'C68 (lock thread, 26 Oct 2026): TIMING ONLY. Nobody opens, plots, scores or compares anything in this folder, and no ECG is computed from it. '
        'Only check_counts prints NaN / unactivated counts. Delete it (keeping runs/v52_2026-10-20/c68_timing/logs/) once the timing is logged.\n')
    logf, memf = os.path.join(LOGS, f'openCARP_{name}.log'), os.path.join(LOGS, f'mem_{name}.tsv')
    env = dict(os.environ, PATH='/usr/local/lib/opencarp/lib/petsc/bin:' + os.environ.get('PATH', ''), OMP_NUM_THREADS='1')
    kept, total = stims_in_window(stage)
    rec = {'stage': stage, 'name': name, 'tend_ms': TEND[stage], 'stimuli_in_window': len(kept), 'stimuli_total': total,
           'command': [str(c) for c in command(stage, name)], 'c_free_bytes_before': c_free_bytes(),
           'start': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    json.dump(rec, open(os.path.join(LOGS, f'run_{name}.json'), 'w'), indent=1)
    t0, low, status, last_t, last_adv = time.time(), 1e9, 'ok', None, time.time()
    with open(logf, 'w') as lg, open(memf, 'w') as mf:
        mf.write('wall_s\tmem_available_mb\tsim_ms\n')
        p = subprocess.Popen(rec['command'], stdout=lg, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        while p.poll() is None:
            time.sleep(10)
            mm = mem_avail_mb(); low = min(low, mm)
            pr = progress(logf); tnow = pr[-1] if pr else None
            mf.write(f'{time.time() - t0:.0f}\t{mm:.0f}\t{tnow}\n'); mf.flush()
            if tnow != last_t:
                last_t, last_adv = tnow, time.time()
            if mm < MIN_MB:
                status = f'killed: MemAvailable {mm:.0f} MB < {MIN_MB} MB'
            elif tnow is None and time.time() - t0 > HANG_S:
                status = 'stopped as a hang: no progress line (t = 0 not passed) within 30 min'
            elif tnow is not None and time.time() - last_adv > HANG_S:
                status = f'stopped as a hang: simulated time stuck at {tnow} ms for 30 min'
            if status != 'ok':
                os.killpg(p.pid, signal.SIGKILL); p.wait(); break
        if status == 'ok' and p.returncode != 0:
            status = f'failed (exit {p.returncode})'
    rec.update({'status': status, 'wall_s': round(time.time() - t0, 1), 'min_mem_available_mb': round(low), 'end': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'c_free_bytes_after': c_free_bytes(), 'bytes_written': sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)})
    for f in ('par_stats.dat', 'IO_stats.dat', 'ODE_stats.dat', 'parameters.par'):
        if os.path.exists(os.path.join(out, f)):
            shutil.copy2(os.path.join(out, f), os.path.join(LOGS, f'{name}_{f}'))
    json.dump(rec, open(os.path.join(LOGS, f'run_{name}.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != 'command'}, indent=1))
    if status != 'ok':
        sys.exit(f'C68 {name}: {status}')


def igb(path):
    b = open(path, 'rb').read()
    hdr = b[:1024].decode('latin1')
    x = int(hdr.split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def check(stage):
    """Counts only: NaN in Vm, nodes never activated (act < 0) in the last act frame."""
    out = tdir(stage)
    res = {}
    vm = igb(os.path.join(out, 'vm.igb'))
    res['vm_frames'], res['vm_nan_values'] = int(vm.shape[0]), int(np.isnan(vm).sum())
    del vm
    for f in sorted(os.listdir(out)):
        if f.startswith('act') and f.endswith('.igb'):
            a = igb(os.path.join(out, f))[-1]
            res[f'{f}: nodes_unactivated (< 0)'] = int((a < 0).sum()); res[f'{f}: nodes'] = int(len(a)); res[f'{f}: nan'] = int(np.isnan(a).sum())
    json.dump(res, open(os.path.join(LOGS, f'check_{os.path.basename(out)}.json'), 'w'), indent=1)
    print(json.dumps(res))


if __name__ == '__main__':
    st = sys.argv[1]
    if st == 'prep':
        prep()
    elif st == 'run':
        run(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
    elif st == 'check':
        check(sys.argv[2] + (f'_try{sys.argv[3]}' if len(sys.argv) > 3 else ''))
    else:
        sys.exit('stages: prep | run short|full | check short|full')
