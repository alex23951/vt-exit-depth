"""v5.2 engine test at the 27 gate-9 sites (LOCK.md 15.3 T1 / T2, 11.4): RE+ beside monodomain, run in unattended night
chunks (Alex, 3 Nov 2026 10:42 UTC: "27 first but split it into 8 hour chunks that can run overnight").
Nothing runs a beat until t1_choices.json holds Alex's dated word (released: true); `prep` and `plan` run no beat.

Sites (per heart): the 8 gate-9 sites of v5.1's check that the v5.2 manifest holds (sites52.json 'capture', same ids;
8.7's stimulated set recomputed with heart52 and checked against the manifest), plus v5.1's template site
(lv_free_wall_original_d0) by the reading in t1_choices.json ('position': the v5.2 merged-mesh node nearest the v5.1 node).
Graph beat: heart52.Heart52 (v5.2 tissue, network, 4 / 2 ms coupling); junction exit times (network time + 4 ms, where the
exit is not later than its muscle) are replayed in both engines as timed stimuli (one-way, 11.4 item 5), each widened to
the nodes within 1.0 mm on the junction's own side of the cut (connected within the ball), in 0.25 ms bins (as v5.1).
Simulation mesh: biv52cut (split across the infundibulum plane, 8.2: no current crosses) with every element that touches
a fibrous-layer node removed (8.6 non-excitable; the graph leg drops every edge touching one) and orphan nodes dropped.
Ionic: Tomek52w (blend52.py): nodal wb = the node's APD w (apd52.npz), sGKs / sGKr per heart (blend52.SETTINGS), initial
state per node interpolated in w from blend52's steady-state cells (CL 1000 ms, R1.1 criterion) - my reading, so the
beat starts where step 4's targets were measured. Tags 1, 2, 25, 28, 29 (all myocardium).
RE+ (T1): dream.solve 1 (eikonal physics region on all myocardial tags), dream.vel = v5.2 speeds (params/v52_speeds.json),
diffusion on fix 2's sigma (params/v52_conductivities.json; 15.3), dream.fim.tol 0.001, max_iter 1e9 (C68); one process.
Window R1.6: 100 ms at rest, stimulus at 100 ms, to max(graph activation + target APD90) + 50 ms (+ 20 ms margin).
Monodomain (gate 9 comparator): tuned sigma (params/v52_mono_conductivities.json, step 6, within 3 %), MONO_NP processes;
window by t1_choices.json: 'qrs' = graph total activation + 30 ms from the stimulus (v5.1's rule), 'r16' = as RE+.
Both: monodomain parabolic solve, dt 10 us, stimulus 400 uA/cm3 x 1 ms, LAT -10 mV, Vm every 1 ms.
Per beat kept: 12-lead ECG (lead-field weights ecgW_v52_c73.npz, sigma_i; Vm of a split node = mean of its copies; removed
nodes at their initial Vm), LAT map, Vm every 5 ms (float16); the raw 1 ms vm.igb is removed only if t1_choices.json
says delete_raw_vm (C: has about 22 GB free; an RE+ beat writes about 1 GB).
Memory guard: a job is stopped if MemAvailable < 900 MB. Every beat start and end is appended to LABNOTES.md.
Usage (repo root, venv, PATH with openCARP's mpiexec):
  python -B .../t1_27.py prep [HEART ...]   graph beats, meshes, stimuli, adjustments, windows -> runs/.../11_engine/<H>/
  python -B .../t1_27.py plan               the queue with estimated hours per beat and per night
  python -B .../t1_27.py night [HOURS]      one unattended chunk (default 8 h): RE+ lanes first, then monodomain beats
  python -B .../t1_27.py status             done / left
  python -B .../t1_27.py analyze            RE+ against monodomain by the gate-9 rule -> t1_results.csv, t1_summary.json
"""
import json
import os
import signal
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUNS = os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine')
CHOICES = os.path.join(HERE, 't1_choices.json')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
MEASURES = ['pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 't_largest_precordial_ms']
GATE9_V51 = ['lv_free_wall_phi180_z0.5_d50', 'lv_free_wall_phi180_z0.5_d90', 'lv_septum_phi0_z0.5_d10', 'lv_septum_phi0_z0.5_d50',
             'lv_septum_phi0_z0.5_d90', 'rv_free_wall_q50_z0.5_d10', 'rv_free_wall_q50_z0.5_d50', 'rv_free_wall_q50_z0.5_d90']
TEMPLATE = 'lv_free_wall_original_d0'
TAGS = [1, 2, 25, 28, 29]
PMJ_R_MM, BIN_MS, BASE_MS = 1.0, 0.25, 100.0
MONO_NP = int(os.environ.get('MONO_NP', '4'))
RE_LANES = int(os.environ.get('RE_LANES', '3'))
MIN_MB = 900
RATE = {'re': 27.3 * 1.15, 'mono': 14.1}         # s per simulated ms at 375,190 nodes (C68 one core x 1.15 for 3 lanes; v5.1 check, 4 processes)
sys.path.insert(0, HERE)
import blend52 as B                                                                           # noqa: E402


def hdir(h, *a):
    return os.path.join(RUNS, h, *a)


def choices():
    return json.load(open(CHOICES)) if os.path.exists(CHOICES) else {}


def mem_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


def vtx(f, nodes):
    with open(f, 'w') as fh:
        fh.write(f'{len(nodes)}\nintra\n'); np.savetxt(fh, np.asarray(nodes, np.int64), fmt='%d')


def adj(f, vals):
    with open(f, 'w') as fh:
        fh.write(f'{len(vals)}\nintra\n'); np.savetxt(fh, np.c_[np.arange(len(vals)), vals], fmt='%d %.9g')


def labnote(text):
    with open(os.path.join(REPO, 'LABNOTES.md'), 'a') as f:
        f.write(text.rstrip('\n') + '\n')


def git_ref():
    r = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return r + (' (uncommitted changes)' if dirty else '')


def read_sv(f):
    names, vals = [], []
    for l in open(f):
        p = l.split('#')
        if len(p) == 2 and p[0].strip() not in ('', '-'):
            names.append(p[1].strip()); vals.append(float(p[0]))
    return names, np.array(vals)


# ---------------------------------------------------------------- prep (no beat)
def sites(h, Hh):
    S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'v52', 'sites52.json')))
    cap = {c['id']: c for c in S['capture']}
    out = []
    for sid in GATE9_V51:
        c = cap[sid]
        st = Hh.stimulated(c['node'], c['family'])
        assert c['valid'] and len(st) == c['stimulated'], sid
        out.append({'id': sid, 'family': c['family'], 'node': int(c['node']), 'stimulated': st.tolist(), 'source': 'sites52.json capture'})
    ch = choices().get('site9')
    if ch == 'position':
        import importlib.util
        sp = importlib.util.spec_from_file_location('mono51', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '08_monodomain', 'mono51.py'))
        m51 = importlib.util.module_from_spec(sp); sp.loader.exec_module(m51)
        orig = int(json.load(open(os.path.join(m51.template_run(h), 'summary_06.json')))['site_node'])
        p51 = np.loadtxt(os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'acceptance_c', 'mesh', 'biv51.pts'), skiprows=1)[orig] / 1e3
        d = np.linalg.norm(Hh.P[:Hh.Nm] - p51, axis=1)
        n = int(np.argmin(d))
        st = Hh.stimulated(n, 'lv_free_wall')
        assert len(st), 'template site fails the 8.7 capture test'
        out.insert(0, {'id': TEMPLATE, 'family': 'lv_free_wall', 'node': n, 'stimulated': st.tolist(), 'source': f'v5.1 node {orig}, nearest v5.2 node at {d[n]:.3f} mm',
                       'v51_node': orig, 'distance_mm': float(d[n])})
    return out


def prep_heart(h):
    import heart52 as H52                                                                     # noqa: F401
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree
    t0 = time.time()
    Hh = H52.Heart52(h)
    V = os.path.join(REPO, 'data', 'biv', h, 'v52')
    os.makedirs(hdir(h, 'mesh'), exist_ok=True)
    tags = np.loadtxt(os.path.join(V, 'biv52cut.elem'), skiprows=1, usecols=5, dtype=np.int64)
    lon = np.loadtxt(os.path.join(V, 'biv52cut.lon'), skiprows=1)
    E = Hh.E
    ke = ~Hh.nonex[E].any(1)
    used = np.unique(E[ke]); keep = used                                                      # sim node -> cut node
    rem = np.full(Hh.N, -1); rem[used] = np.arange(len(used))
    base = hdir(h, 'mesh', 'sim52')
    with open(base + '.pts', 'w') as f:
        f.write(f'{len(used)}\n'); np.savetxt(f, Hh.P[used] * 1e3, fmt='%.3f')
    with open(base + '.elem', 'w') as f:
        f.write(f'{int(ke.sum())}\n'); np.savetxt(f, np.c_[rem[E[ke]], tags[ke]], fmt='Tt %d %d %d %d %d')
    with open(base + '.lon', 'w') as f:
        f.write('2\n'); np.savetxt(f, lon[ke], fmt='%.6g')
    src = np.load(os.path.join(V, 'cut_dup52.npy'))                                           # cut node -> merged node
    merged = src[keep]
    w = np.load(os.path.join(V, 'apd52.npz'))['w'][merged]
    np.savez(hdir(h, 'mesh', 'maps.npz'), keep=keep, merged=merged, w=w, Nm=Hh.Nm, Ncut=Hh.N)
    # adjustments: wb and the initial state, per setting of this heart
    setting = 'control' if h == 'Y5HYEDL4' else 'HF'
    grid = json.load(open(B.OUT))['grid'][setting]
    ws = sorted(float(k) for k in grid)
    states = [read_sv(os.path.join(REPO, grid[f'{x:.1f}']['state_file'])) for x in ws]
    names = states[0][0]
    S = np.array([s[1] for s in states])                                                      # (grid, vars)
    ad = hdir(h, 'adj'); os.makedirs(ad, exist_ok=True)
    adjs = [('Tomek52w.wb', os.path.join(ad, 'wb.adj'))]
    adj(adjs[0][1], w)
    for k, nm in enumerate(names):
        if nm in ('wb', 'Iion'):
            continue
        vals = np.interp(w, ws, S[:, k])
        var = 'Vm' if nm == 'Vm' else f'Tomek52w.{nm}'
        f = os.path.join(ad, f'{nm}.adj'); adj(f, vals); adjs.append((var, f))
    vm0 = np.interp(w, ws, S[:, names.index('Vm')])
    # sites, graph beats, stimuli
    tree = cKDTree(Hh.P)
    apd = np.load(os.path.join(V, 'apd52.npz'))['target_apd90_ms']
    beats = []
    for s in sites(h, Hh):
        bd = hdir(h, s['id']); os.makedirs(os.path.join(bd, 'stims'), exist_ok=True)
        Tm, Tn, info = Hh.solve(sources=np.asarray(s['stimulated'], np.int64))
        net = Hh.net
        m = net['nodes'][net['pmj']]; tx = Tn[net['pmj']] + H52.D_ANT
        drive = np.isfinite(tx) & (tx <= Tm[m] + 1e-6)
        np.save(os.path.join(bd, 'graph_T.npy'), Tm.astype(np.float32))
        site_sim = rem[np.asarray(s['stimulated'], np.int64)]
        assert (site_sim >= 0).all()
        vtx(os.path.join(bd, 'stims', 'site.vtx'), site_sim)
        stims = [{'vtx': os.path.join(bd, 'stims', 'site'), 'start_ms': 0.0}]
        jn, jt = m[drive], np.round(tx[drive] / BIN_MS) * BIN_MS
        for k, tb in enumerate(np.unique(jt)):
            nodes = []
            for n in jn[jt == tb]:
                ball = np.array(tree.query_ball_point(Hh.P[n], PMJ_R_MM))
                ball = ball[~Hh.nonex[ball]]
                _, lb = connected_components(Hh.A[ball][:, ball], directed=False)
                nodes.append(ball[lb == lb[np.where(ball == n)[0][0]]])
            nodes = rem[np.unique(np.concatenate(nodes))]
            vtx(os.path.join(bd, 'stims', f'pmj_{k:04d}.vtx'), nodes[nodes >= 0])
            stims.append({'vtx': os.path.join(bd, 'stims', f'pmj_{k:04d}'), 'start_ms': float(tb)})
        ex = ~Hh.nonex & np.isfinite(Tm)
        last = float(Tm[ex].max())
        rep = float(np.max(Tm[keep][np.isfinite(Tm[keep])] + apd[merged][np.isfinite(Tm[keep])]))
        win = {'re_tend_ms': float(np.ceil((BASE_MS + rep + 50.0 + 20.0) / 10) * 10), 'qrs_tend_ms': float(np.ceil((last + 30.0) / 10) * 10),
               'graph_last_activation_ms': round(last, 2), 'graph_latest_activation_plus_apd90_ms': round(rep, 2)}
        cfg = {'heart': h, 'site': s, 'graph': {**info, 'junction_exits_replayed': int(drive.sum())}, 'stims': stims, 'window': win}
        json.dump(cfg, open(os.path.join(bd, 'beat_config.json'), 'w'), indent=1)
        beats.append({'site': s['id'], 'stimuli': len(stims), **win})
        print(h, s['id'], {k: v for k, v in win.items()}, 'stimuli', len(stims), flush=True)
    rec = {'heart': h, 'setting': setting, 'sim_nodes': int(len(used)), 'sim_elements': int(ke.sum()), 'elements_removed_fibrous': int((~ke).sum()),
           'cut_nodes': int(Hh.N), 'merged_nodes': int(Hh.Nm), 'adjustments': adjs, 'vm0_range_mV': [float(vm0.min()), float(vm0.max())],
           'heart52_keys': Hh.keys, 'beats': beats, 'wall_s': round(time.time() - t0, 1)}
    json.dump(rec, open(hdir(h, 'prep.json'), 'w'), indent=1, default=str)
    np.save(hdir(h, 'mesh', 'vm0.npy'), vm0.astype(np.float32))
    print(h, 'prep done', rec['sim_nodes'], 'nodes', rec['elements_removed_fibrous'], 'elements removed', flush=True)


# ---------------------------------------------------------------- beats
def queue():
    q = []
    for h in HEARTS:
        p = hdir(h, 'prep.json')
        if not os.path.exists(p):
            continue
        P = json.load(open(p))
        scale = P['sim_nodes'] / 375190
        win = choices().get('mono_window', 'qrs')
        for b in P['beats']:
            for eng in ('re', 'mono'):
                tend = b['re_tend_ms'] if (eng == 're' or win == 'r16') else b['qrs_tend_ms']
                q.append({'id': f"{h}/{b['site']}/{eng}", 'heart': h, 'site': b['site'], 'engine': eng, 'tend_ms': tend,
                          'est_h': round(RATE[eng] * scale * tend / 3600 + 0.05, 2)})
    return q


def bdir(b):
    return hdir(b['heart'], b['site'], b['engine'])


def retry(b):
    """Not started, interrupted (still 'running' on disk) or stopped by the memory guard; a failed beat waits for a look."""
    f = os.path.join(bdir(b), 'summary.json')
    if not os.path.exists(f):
        return True
    st = json.load(open(f)).get('status', '')
    return st == 'running' or st.startswith('stopped by memory guard')


def done(b):
    f = os.path.join(bdir(b), 'summary.json')
    return os.path.exists(f) and json.load(open(f)).get('status') == 'ok'


def command(b):
    h = b['heart']
    cfg = json.load(open(hdir(h, b['site'], 'beat_config.json')))
    P = json.load(open(hdir(h, 'prep.json')))
    shift = BASE_MS if b['engine'] == 're' else 0.0
    st = [s for s in cfg['stims'] if s['start_ms'] + shift + 1.0 <= b['tend_ms']]
    so = ['-num_stim', len(st)]
    for i, s in enumerate(st):
        so += [f'-stim[{i}].crct.type', 0, f'-stim[{i}].elec.vtx_file', s['vtx'], f'-stim[{i}].ptcl.start', s['start_ms'] + shift,
               f'-stim[{i}].pulse.strength', 400.0, f'-stim[{i}].ptcl.duration', 1.0, f'-stim[{i}].ptcl.npls', 1]
    ad = ['-num_adjustments', len(P['adjustments'])]
    for i, (var, f) in enumerate(P['adjustments']):
        ad += [f'-adjustment[{i}].variable', var, f'-adjustment[{i}].file', f]
    setting = B.SETTINGS[P['setting']]['par']
    imp = ['-num_external_imp', 1, '-external_imp[0]', B.SO, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek52w',
           '-imp_region[0].im_param', ','.join(f'{k}={v}' for k, v in setting.items()), '-imp_region[0].num_IDs', len(TAGS)]
    imp += sum(([f'-imp_region[0].ID[{i}]', t] for i, t in enumerate(TAGS)), [])
    gid = ['-num_gregions', 1, '-gregion[0].num_IDs', len(TAGS)] + sum(([f'-gregion[0].ID[{i}]', t] for i, t in enumerate(TAGS)), [])
    if b['engine'] == 're':
        g = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts'][h]['sigma_S_m']
        v = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts'][h]
    else:
        g = json.load(open(os.path.join(REPO, 'params', 'v52_mono_conductivities.json')))['hearts'][h]['conductivities_S_m']
    for k, a in (('l', 'fibre'), ('t', 'sheet'), ('n', 'normal')):
        gid += [f'-gregion[0].g_i{k}', g[a]['gi'], f'-gregion[0].g_e{k}', g[a]['ge']]
        if b['engine'] == 're':
            gid += [f'-gregion[0].dream.vel_{k}', 1000.0 * v[a]]
    np_ = 1 if b['engine'] == 're' else MONO_NP
    cmd = ['/usr/bin/time', '-v', 'mpiexec', '-n', np_, 'openCARP', '-meshname', hdir(h, 'mesh', 'sim52'), '-simID', bdir(b),
           '-bidomain', 0, '-dt', 10.0, '-parab_solve', 1, '-tend', b['tend_ms'], '-spacedt', 1.0, '-timedt', 5.0,
           '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0, '-lats[0].threshold', -10, '-lats[0].method', 1]
    if b['engine'] == 're':
        cmd += ['-dream.solve', 1, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', 1000000000, '-num_phys_regions', 1,
                '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', len(TAGS)] + sum(([f'-phys_region[0].ID[{i}]', t] for i, t in enumerate(TAGS)), [])
    return [str(c) for c in cmd + imp + ad + so + gid], len(st), len(cfg['stims'])


def igb(f):
    hd = open(f, 'rb').read(1024).decode('latin1')
    x = int(hd.split('x:')[1].split()[0])
    return np.memmap(f, dtype='<f4', mode='r', offset=1024).reshape(-1, x)


def finish(b, rec):
    """ECG, LAT and 5 ms Vm from the raw output; the raw vm.igb removed only if t1_choices.json says delete_raw_vm."""
    h, d = b['heart'], bdir(b)
    M = np.load(hdir(h, 'mesh', 'maps.npz'))
    vm0 = np.load(hdir(h, 'mesh', 'vm0.npy'))
    W = np.load(os.path.join(REPO, 'data', 'biv', h, 'v52', 'ecgW_v52_c73.npz'))['W'].astype(np.float64)
    vm = igb(os.path.join(d, 'vm.igb'))
    Nm = int(M['Nm']); cnt = np.bincount(M['merged'], minlength=Nm).astype(float)
    full = np.zeros(Nm); miss = cnt == 0
    ecg = np.zeros((len(vm), 12))
    for t in range(len(vm)):
        acc = np.bincount(M['merged'], weights=vm[t].astype(np.float64), minlength=Nm)
        full[:] = np.where(miss, 0.0, acc / np.maximum(cnt, 1))
        ecg[t] = W[:, ~miss] @ full[~miss]
    rec['nan_frames'] = int(np.isnan(vm).any(1).sum())
    rec['merged_nodes_without_sim_node'] = int(miss.sum())
    lat = np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat'))
    rec['unactivated_nodes'] = int((lat < 0).sum())
    shift = BASE_MS if b['engine'] == 're' else 0.0
    rec['last_activation_ms_from_stimulus'] = round(float(lat[lat >= 0].max() - shift), 2) if (lat >= 0).any() else None
    np.savez_compressed(os.path.join(d, 'kept.npz'), ecg=ecg.astype(np.float32), leads=np.array(LEADS), lat=lat.astype(np.float32),
                        stim_ms=shift, vm5=vm[::5].astype(np.float16), vm5_dt_ms=5.0)
    rec['ecg_frames'] = int(len(ecg))
    if choices().get('delete_raw_vm') and rec['nan_frames'] == 0:
        chk = np.load(os.path.join(d, 'kept.npz'))
        if np.allclose(chk['ecg'], ecg.astype(np.float32)):
            os.remove(os.path.join(d, 'vm.igb')); rec['raw_vm_removed'] = True
    del vm
    return rec


def start(b):
    d = bdir(b)
    if os.path.exists(d):
        os.rename(d, d + time.strftime('_interrupted_%Y%m%d_%H%M%S'))
    os.makedirs(d)
    cmd, n_in, n_all = command(b)
    rec = {'beat': b['id'], 'engine': b['engine'], 'tend_ms': b['tend_ms'], 'stimuli': n_in, 'stimuli_total': n_all, 'command': cmd,
           'git': git_ref(), 'start': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'status': 'running'}
    json.dump(rec, open(os.path.join(d, 'summary.json'), 'w'), indent=1)
    log = open(os.path.join(d, 'openCARP.log'), 'w')
    env = dict(os.environ, OMP_NUM_THREADS='1')
    p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    model = 'reaction-eikonal RE+ (dream.solve 1), 1 process' if b['engine'] == 're' else f'monodomain, {MONO_NP} processes'
    labnote(f"- Beat started (2026-11-03_v52_11_t1_27), PC clock {time.strftime('%d %b %H:%M')}: {b['id']}, {model}, Tomek52w blend, "
            f"tend {b['tend_ms']:g} ms, {n_in} stimuli, estimate {b['est_h']} h, git {rec['git']}; output {os.path.relpath(d, REPO)}. Status: running.")
    return {'b': b, 'p': p, 'log': log, 'rec': rec, 't0': time.time(), 'low': 1e9}


def close(j, status):
    j['log'].close()
    b, rec = j['b'], j['rec']
    rec.update({'status': status, 'end': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'wall_s': round(time.time() - j['t0'], 1),
                'min_mem_available_mb': round(j['low'])})
    rec['s_per_sim_ms'] = round(rec['wall_s'] / b['tend_ms'], 2)
    if status == 'ok':
        try:
            rec = finish(b, rec)
            if rec['nan_frames'] or rec['unactivated_nodes']:
                rec['status'] = status = 'failed (NaN or unactivated nodes)'
        except Exception as e:                                                            # noqa: BLE001
            rec['status'] = status = f'failed in post-processing: {e!r}'
    json.dump(rec, open(os.path.join(bdir(b), 'summary.json'), 'w'), indent=1)
    labnote(f"- Beat ended, PC clock {time.strftime('%d %b %H:%M')}: {b['id']}: {status}; wall {rec['wall_s'] / 3600:.2f} h "
            f"({rec['s_per_sim_ms']} s per simulated ms), lowest MemAvailable {rec['min_mem_available_mb']} MB"
            + (f", last activation {rec.get('last_activation_ms_from_stimulus')} ms after the stimulus, unactivated {rec.get('unactivated_nodes')}" if status == 'ok' else '') + '.')


def night(hours=8.0):
    ch = choices()
    if not ch.get('released'):
        sys.exit('t1_choices.json does not hold Alex\'s release (the v5.2 beat hold stands): nothing started')
    if not os.path.exists(os.path.join(REPO, 'params', 'v52_mono_conductivities.json')):
        sys.exit('step 6 not done (params/v52_mono_conductivities.json missing): nothing started')
    t_end = time.time() + hours * 3600
    q = [b for b in queue() if not done(b)]
    labnote(f"\n### 2026-11-03_v52_11_t1_27 night chunk (PC clock {time.strftime('%d %b %H:%M')}): {len(q)} beats left, "
            f"{hours:g} h, up to {RE_LANES} RE+ lanes then monodomain on {MONO_NP} processes")
    jobs, stopped = [], False
    while True:
        now = time.time()
        for j in list(jobs):
            r = j['p'].poll()
            if r is not None:
                close(j, 'ok' if r == 0 else f'failed (exit {r})'); jobs.remove(j)
        mm = mem_mb()
        for j in jobs:
            j['low'] = min(j['low'], mm)
        if mm < MIN_MB and jobs:
            j = max(jobs, key=lambda x: x['t0'])
            os.killpg(j['p'].pid, signal.SIGTERM); j['p'].wait()
            close(j, f'stopped by memory guard ({mm:.0f} MB available)'); jobs.remove(j); stopped = True
        left = t_end - now
        running = {j['b']['id'] for j in jobs}
        todo = [b for b in q if b['id'] not in running and retry(b)]
        re_todo = [b for b in todo if b['engine'] == 're' and b['est_h'] * 3600 <= left]
        mono_todo = [b for b in todo if b['engine'] == 'mono' and b['est_h'] * 3600 <= left]
        n_re = sum(j['b']['engine'] == 're' for j in jobs)
        n_mono = sum(j['b']['engine'] == 'mono' for j in jobs)
        if not stopped and re_todo and n_mono == 0 and n_re < RE_LANES and mem_mb() > 2600:
            jobs.append(start(re_todo[0])); time.sleep(90); continue
        if not stopped and not re_todo and n_re == 0 and n_mono == 0 and mono_todo:
            jobs.append(start(mono_todo[0])); time.sleep(30); continue
        if not jobs:
            break
        time.sleep(30)
    left = [b['id'] for b in queue() if not done(b)]
    labnote(f"- Night chunk ended, PC clock {time.strftime('%d %b %H:%M')}: {len(left)} beats left" + (' (memory guard stopped a beat)' if stopped else '') + '.')
    print('night chunk ended;', len(left), 'beats left', flush=True)


def plan():
    q = queue()
    tot = {'re': sum(b['est_h'] for b in q if b['engine'] == 're'), 'mono': sum(b['est_h'] for b in q if b['engine'] == 'mono')}
    for b in q:
        print(b['id'], b['tend_ms'], b['est_h'], 'done' if done(b) else '')
    print('total hours: RE+ (per lane)', round(tot['re'], 1), 'monodomain', round(tot['mono'], 1))


def status():
    q = queue()
    for b in q:
        f = os.path.join(bdir(b), 'summary.json')
        print(b['id'], json.load(open(f))['status'] if os.path.exists(f) else 'not started')
    print(sum(done(b) for b in q), 'of', len(q), 'beats done')


def score(ecg, stim_idx):
    from ecg_depth_criteria import from_leads, measure_beat
    pad = 60
    e = ecg[stim_idx:]
    leads = {l: np.concatenate([np.full(pad, e[0, LEADS.index(l)]), e[:, LEADS.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    m = measure_beat(from_leads(leads), 1000.0, stim_ms=float(pad))
    r = {k: float(m[k]) for k in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'qrs_duration_any_lead_ms', 'mdi_daniels')}
    r['t_largest_precordial_ms'] = float(m['mdi_daniels'] * (m['offset_any_lead_ms'] - m['onset_ms']))
    return r


def analyze():
    import csv
    rows = []
    for h in HEARTS:
        if not os.path.exists(hdir(h, 'prep.json')):
            continue
        for bt in json.load(open(hdir(h, 'prep.json')))['beats']:
            k = {}
            for eng in ('re', 'mono'):
                f = os.path.join(hdir(h, bt['site'], eng), 'kept.npz')
                if os.path.exists(f) and done({'heart': h, 'site': bt['site'], 'engine': eng}):
                    z = np.load(f); k[eng] = (score(z['ecg'].astype(float), int(round(float(z['stim_ms'])))), z['lat'])
            if len(k) < 2:
                continue
            r = {'heart': h, 'site': bt['site']}
            for mname in MEASURES + ['qrs_duration_any_lead_ms']:
                r[f'{mname}_re'], r[f'{mname}_mono'] = k['re'][0][mname], k['mono'][0][mname]
                r[f'{mname}_diff'] = k['re'][0][mname] - k['mono'][0][mname]
            la, lm = k['re'][1] - BASE_MS, k['mono'][1]
            ok = (k['re'][1] >= 0) & (lm >= 0)
            r['node_median_lat_diff_ms'] = float(np.median(la[ok] - lm[ok])); r['node_within_5ms_pct'] = float(100 * np.mean(np.abs(la[ok] - lm[ok]) <= 5))
            rows.append(r)
    if not rows:
        sys.exit('no finished pair')
    with open(os.path.join(HERE, 't1_results.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    d = np.array([[r[f'{m}_diff'] for m in MEASURES] for r in rows])
    summ = {'pairs': int(d.size), 'sites': len(rows), 'within_5ms': int((np.abs(d) <= 5).sum()), 'max_abs_diff_ms': float(np.abs(d).max()),
            'misses_by_measure': {m: int((np.abs(d[:, i]) > 5).sum()) for i, m in enumerate(MEASURES)},
            'rule': 'gate-9 rule applied to RE+ against monodomain (4 measures, 5 ms; 108 pairs when all 27 sites are done); report only'}
    json.dump(summ, open(os.path.join(HERE, 't1_summary.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(REPO, 'analysis', 'v52_2026-10-20', '03_speeds'))
    a = sys.argv[1]
    if a == 'prep':
        for h in (sys.argv[2:] or HEARTS):
            sys.modules.pop('common', None)
            prep_heart(h)
    elif a == 'night':
        night(float(sys.argv[2]) if len(sys.argv) > 2 else 8.0)
    else:
        {'plan': plan, 'status': status, 'analyze': analyze}[a]()
