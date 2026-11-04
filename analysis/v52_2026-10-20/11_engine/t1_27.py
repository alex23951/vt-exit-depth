"""v5.2 engine test at the 27 gate-9 sites (LOCK.md 15.3 T1 / T2, 11.4): RE+ beside monodomain, run in unattended night
chunks (Alex, 3 Nov 2026 10:42 UTC: "27 first but split it into 8 hour chunks that can run overnight").
Nothing runs a beat until t1_choices.json holds Alex's dated word (released: true); `prep` and `plan` run no beat.

Sites (per heart): the 8 gate-9 sites of v5.1's check that the v5.2 manifest holds (sites52.json 'capture', same ids;
8.7's stimulated set recomputed with heart52 and checked against the manifest), plus v5.1's template site
(lv_free_wall_original_d0) by the reading in t1_choices.json ('position': the v5.2 merged-mesh node nearest the v5.1 node).
Graph beat: heart52.Heart52 (v5.2 tissue, network, 4 / 2 ms coupling); junction exit times (network time + 4 ms, where the
exit is not later than its muscle) are replayed in both engines as timed stimuli (one-way, 11.4 item 5), each widened to
the nodes within 1.0 mm on the junction's own side of the cut (connected within the ball), in 0.25 ms bins (as v5.1).
Simulation mesh: biv52cut (split across the infundibulum plane, 8.2: no current crosses), every element kept (D44 (d), 4 Nov;
the HF preps of 3 Nov removed every element touching a fibrous-layer node and are superseded); the fibrous-layer nodes
(8.6 non-excitable; the graph leg drops every edge touching one) are made non-excitable by Tomek52w's nodal factor fexc = 0
on INa, INaL and the L-type channel (sleeve52.py), set by adjustment; they are not counted as unactivated nodes.
Ionic: Tomek52w (blend52.py): nodal wb = the node's APD w (apd52.npz), sGKs / sGKr per heart (blend52.SETTINGS), initial
state per node interpolated in w from blend52's steady-state cells (CL 1000 ms, R1.1 criterion) - my reading, so the
beat starts where step 4's targets were measured. Tags 1, 2, 25, 28, 29 (all myocardium).
RE+ (T1): dream.solve 1 (eikonal physics region on all myocardial tags), dream.vel = v5.2 speeds (params/v52_speeds.json),
foot current FOOT (Idiff.model 0) with A_F 0.91 mV and the fitted tau_F per heart type (params/v52_re_foot.json; D45, D48),
diffusion on fix 2's sigma (params/v52_conductivities.json; 15.3), dream.fim.tol 0.001, max_iter 1000 (D50, 4 Nov; was 1e9, C68) with D50's rerun check; one process.
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
  python -B .../t1_27.py check6 [ENGINE]    check 6 from kept raw files of finished beats that predate it (counts only)
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
FIM_MAX_ITER = 1000                                     # D50 (Alex "Cap at 1000 with a check", 4 Nov 2026 11:47:56 UTC); was 1e9 (C68)
FIM_CHECK = (1001, 1002, 1003)                          # D50's check when the t = 0 solve ends at the cap with a non-empty list
SO = os.path.join(RUNS, 'model_fexc_O2_ftz', 'Tomek52w.so')   # Tomek52w + D44 (d)'s nodal factor fexc (sleeve52.py), gcc -O2,
# subnormals as zero inside the model (ftz52.py, 4 Nov); fexc = 1 traces identical to model_O2_ftz and -O0 (sleeve52_check.json),
# model_O2_ftz's identical to model_O2 (ftz52_check.json, flat-block frames bitwise identical; blend52_O2check.json)
RATE = {'re': 25.0 * 1.15, 'mono': 26.25 * 1.1}  # s per simulated ms at 375,190 nodes: RE+ test 4 Nov with model_fexc_O2_ftz (one core, last 5 ms
# block 24.4 s/ms beside one flat-block run; x 1.15 for lanes); monodomain test 3 Nov on model_O2 (4 processes, +10 %; kept, conservative)
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
    ke = np.ones(len(E), bool)                                                                # D44 (d): every element kept
    used = np.unique(E[ke]); keep = used                                                      # sim node -> cut node
    flag = Hh.nonex[used]                                                                     # fibrous-layer nodes: fexc = 0
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
    np.savez(hdir(h, 'mesh', 'maps.npz'), keep=keep, merged=merged, w=w, Nm=Hh.Nm, Ncut=Hh.N, flagged=np.where(flag)[0])
    # adjustments: wb and the initial state, per setting of this heart
    setting = 'control' if h == 'Y5HYEDL4' else 'HF'
    grid = json.load(open(B.OUT))['grid'][setting]
    ws = sorted(float(k) for k in grid)
    states = [read_sv(os.path.join(REPO, grid[f'{x:.1f}']['state_file'])) for x in ws]
    names = states[0][0]
    S = np.array([s[1] for s in states])                                                      # (grid, vars)
    ad = hdir(h, 'adj'); os.makedirs(ad, exist_ok=True)
    adjs = [('Tomek52w.wb', os.path.join(ad, 'wb.adj')), ('Tomek52w.fexc', os.path.join(ad, 'fexc.adj'))]
    adj(adjs[0][1], w)
    adj(adjs[1][1], np.where(flag, 0.0, 1.0))
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
        print(h, s['id'], 'stimuli', len(stims), 'unactivated excitable', info['unactivated_excitable_nodes'], flush=True)   # counts only (lock thread)
    rec = {'heart': h, 'setting': setting, 'sim_nodes': int(len(used)), 'sim_elements': int(ke.sum()), 'elements_removed_fibrous': int((~ke).sum()),
           'flagged_nodes_fexc0': int(flag.sum()), 'flagged_elements_kept': int(Hh.nonex[E].any(1).sum()),
           'cut_nodes': int(Hh.N), 'merged_nodes': int(Hh.Nm), 'adjustments': adjs, 'vm0_range_mV': [float(vm0.min()), float(vm0.max())],
           'heart52_keys': Hh.keys, 'beats': beats, 'wall_s': round(time.time() - t0, 1)}
    json.dump(rec, open(hdir(h, 'prep.json'), 'w'), indent=1, default=str)
    np.save(hdir(h, 'mesh', 'vm0.npy'), vm0.astype(np.float32))
    print(h, 'prep done', rec['sim_nodes'], 'nodes', rec['elements_removed_fibrous'], 'elements removed', rec['flagged_nodes_fexc0'], 'flagged nodes', flush=True)


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
                if not released(h, eng):
                    continue
                tend = b['re_tend_ms'] if (eng == 're' or win == 'r16') else b['qrs_tend_ms']
                q.append({'id': f"{h}/{b['site']}/{eng}", 'heart': h, 'site': b['site'], 'engine': eng, 'tend_ms': tend,
                          'est_h': round(RATE[eng] * scale * tend / 3600 + 0.05, 2)})
    return q


def released(h, eng):
    """t1_choices.json 'release' lists '<HEART>/<engine>' items the lock thread's conditions allow (note of 3 Nov 13:35 UTC)."""
    ch = choices()
    return bool(ch.get('released')) and f'{h}/{eng}' in ch.get('release', [])


def c_free_gb():
    import shutil
    return shutil.disk_usage('/mnt/c').free / 1e9


def bdir(b):
    return b.get('dir') or hdir(b['heart'], b['site'], b['engine'])


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
    ad += ['-adjustment[0].dump', 1]                                                          # wb as openCARP applied it, kept for a check
    setting = B.SETTINGS[P['setting']]['par']
    imp = ['-num_external_imp', 1, '-external_imp[0]', SO, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek52w',
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
        cmd += ['-dream.solve', 1, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', FIM_MAX_ITER, '-output_level', 2, '-num_phys_regions', 1,
                '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', len(TAGS)] + sum(([f'-phys_region[0].ID[{i}]', t] for i, t in enumerate(TAGS)), [])
        foot = json.load(open(os.path.join(REPO, 'params', 'v52_re_foot.json')))['hearts'][h]     # D45 / D48 (foot52.py), fixed
        imp += sum(([f'-imp_region[0].dream.Idiff.{k}', foot[k]] for k in ('model', 'A_F', 'tau_F', 'V_th')), [])
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
    W = np.load(hdir(h, 'mesh', 'ecgW_split.npz'))['W'].astype(np.float64)              # D43: per copy, ecgsplit52.py
    vm = igb(os.path.join(d, 'vm.igb'))
    assert vm.shape[1] == W.shape[1]
    Nm = int(M['Nm'])
    ecg = np.concatenate([np.asarray(vm[i:i + 50], np.float64) @ W.T for i in range(0, len(vm), 50)])
    I, II = ecg[:, LEADS.index('I')], ecg[:, LEADS.index('II')]
    elec = np.c_[-(I + II) / 3, (2 * I - II) / 3, (2 * II - I) / 3, ecg[:, [LEADS.index(f'V{k}') for k in range(1, 7)]]]
    cfg = json.load(open(hdir(h, b['site'], 'beat_config.json')))
    site = np.loadtxt(cfg['stims'][0]['vtx'] + '.vtx', skiprows=2, dtype=np.int64, ndmin=1)
    xyz = np.loadtxt(hdir(h, 'mesh', 'sim52.pts'), skiprows=1)[site]
    rec['nan_frames'] = int(np.isnan(vm).any(1).sum())
    lat = np.loadtxt(os.path.join(d, 'init_acts_LATs-thresh.dat'))
    flag = np.zeros(vm.shape[1], bool)
    if 'flagged' in M.files:
        flag[M['flagged']] = True
    rec['unactivated_nodes'] = int(((lat < 0) & ~flag).sum())                                   # excitable nodes only (D44 (d))
    rec['flagged_nodes'] = int(flag.sum())
    shift = BASE_MS if b['engine'] == 're' else 0.0
    if b['engine'] == 'mono':
        ex = lat[~flag]
        rec['own_last_activation_inside_window'] = bool((ex >= 0).all() and ex.max() < b['tend_ms'])   # check 5 (b), a count
    c6 = check6(vm, b['tend_ms'])
    if b['engine'] == 're':
        f = os.path.join(d, 'act.igb')
        c6['eikonal_ms'] = np.asarray(igb(f)[0], np.float32) if os.path.exists(f) else np.full(vm.shape[1], np.nan, np.float32)
        rep_t = c6['repol_ms'][~flag]
        rec['own_latest_repol_plus_50_inside_window'] = bool(np.isfinite(rep_t).all() and np.nanmax(rep_t) + 50.0 <= b['tend_ms'])   # check 5 (a)
        rest = np.asarray(vm[:int(BASE_MS) + 1], np.float64)                                    # check 4 (T2 values: kept, not printed)
        c6['check4'] = np.array([np.abs(rest[-1] - rest[0]).max(), np.sqrt(np.mean((rest[-1] - rest[0]) ** 2)), np.abs(np.diff(rest, axis=0)).max()])
        if flag.any():                                                                          # addenda 2-3 item 4: counts only
            rec['flagged_vm_above_every_excitable'] = int((c6['vmax_mV'][flag] > c6['vmax_mV'][~flag].max()).sum())
            rec['flagged_driven_again'] = 'not measured (Vm and Idiff are written every 1 ms; the build cannot count it per step)'
    if b['engine'] == 're':                                                                     # lock note 4 Nov section 2: counts
        rec['fim_t0_iterations'], rec['fim_t0_active_list_at_exit'] = fim_counts(d)
        if rec['fim_t0_active_list_at_exit'] is None or rec['fim_t0_active_list_at_exit'] > 0:   # D50: ended at the cap
            chk = fim_rerun(b, d)
            rec['fim_check'] = chk
            rec['fim_check_max_abs_diff_ms'] = max(x['max_abs_diff_ms'] for x in chk.values())
            rec['fim_check_failed'] = bool(rec['fim_check_max_abs_diff_ms'] > 0.01)
    cls = node_classes(h, b['site'], len(flag))
    rec['check6_by_class'] = {k: {'ead': int((c6['ead'] & ~flag & (cls == i)).sum()),
                                  'repolarised_in_window': int((np.isfinite(c6['apd90_ms']) & ~flag & (cls == i)).sum()),
                                  'nodes': int((~flag & (cls == i)).sum())} for i, k in enumerate(CLASSES)}
    rec['ead_flagged_excitable_nodes'] = int(c6['ead'][~flag].sum())
    rec['no_repolarisation_in_window_excitable_nodes'] = int((~np.isfinite(c6['apd90_ms']))[~flag].sum())
    rec['last_activation_ms_from_stimulus'] = round(float(lat[lat >= 0].max() - shift), 2) if (lat >= 0).any() else None
    split = np.where(np.bincount(M['merged'], minlength=Nm)[M['merged']] > 1)[0]               # sim nodes whose merged node is split
    np.savez_compressed(os.path.join(d, 'kept.npz'), ecg=ecg.astype(np.float32), leads=np.array(LEADS), lat=lat.astype(np.float32),
                        electrodes=elec.astype(np.float32), electrode_names=np.array(['RA', 'LA', 'LL', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']),
                        electrode_reference='Wilson central terminal (RA + LA + LL) / 3', site_nodes=site, site_xyz_um=xyz,
                        stim_ms=shift, vm5=vm[::5].astype(np.float16), vm5_dt_ms=5.0, ecg_rule='D43: per copy, element by element on the split mesh',
                        split_sim_nodes=split, split_merged_nodes=M['merged'][split], vm_split_1ms=np.asarray(vm[:, split], np.float32),
                        check6=np.array(1), flagged=np.where(flag)[0], **{f'c6_{k}': v for k, v in c6.items()})
    rec['split_copies_kept'] = int(len(split))
    rec['ecg_frames'] = int(len(ecg))
    ch = choices()
    if b['engine'] in ch.get('delete_raw_vm_engines', []) and rec['nan_frames'] == 0 and not b.get('test'):
        chk = np.load(os.path.join(d, 'kept.npz'))
        if (np.allclose(chk['ecg'], ecg.astype(np.float32)) and chk['vm_split_1ms'].shape == (len(vm), len(split))
                and 'check6' in chk.files):                                                # section 4 check 6's per-node values (not built yet)
            os.remove(os.path.join(d, 'vm.igb')); rec['raw_vm_removed'] = True
    del vm
    return rec


CLASSES = ('stimulus_or_junction_exit', 'within_1mm', 'surface', 'other')


def node_classes(h, site, n):
    """Lock note of 4 Nov, section 3: 0 = a node of any stimulus set of the beat (the site set and the junction-exit replay
    sets), 1 = within 1 mm of one, 2 = on the simulation mesh's surface, 3 = other (first class that applies)."""
    from scipy.spatial import cKDTree
    sf = hdir(h, 'mesh', 'surface_nodes.npy')
    if not os.path.exists(sf):
        E = np.loadtxt(hdir(h, 'mesh', 'sim52.elem'), skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
        F = np.sort(np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]]), axis=1)
        u, c = np.unique(F, axis=0, return_counts=True)
        np.save(sf, np.unique(u[c == 1]))
    P = np.loadtxt(hdir(h, 'mesh', 'sim52.pts'), skiprows=1) / 1000.0
    cfg = json.load(open(hdir(h, site, 'beat_config.json')))
    st = np.unique(np.concatenate([np.loadtxt(x['vtx'] + '.vtx', skiprows=2, dtype=np.int64, ndmin=1) for x in cfg['stims']]))
    cls = np.full(n, 3, np.int8)
    cls[np.load(sf)] = 2
    near = np.unique(np.concatenate([np.asarray(x, np.int64) for x in cKDTree(P).query_ball_point(P[st], 1.0)] or [np.zeros(0, np.int64)]))
    cls[near] = 1
    cls[st] = 0
    return cls


def fim_counts(d, log_name='openCARP.log'):
    """t = 0 FIM iterations (eik_stats.dat, 'its') and the active-list size at exit (openCARP.log, output_level 2)."""
    its = act = None
    f = os.path.join(d, 'eik_stats.dat')
    if os.path.exists(f):
        rows = [l.split() for l in open(f) if l.strip() and l.split()[0].replace('.', '', 1).isdigit()]
        if rows:
            its = int(rows[0][3])
    lf = os.path.join(d, log_name)
    for l in (open(lf, errors='replace') if os.path.exists(lf) else []):
        if l.startswith('active list:'):
            act = int(l.split()[2]); break
    return its, act


def act0(f):
    """The t = 0 FIM activation times (act.igb frame 0; -1 = not reached)."""
    return np.asarray(igb(f)[0], np.float64)


def fim_diff(a, r):
    reach = (a >= 0) & (r >= 0)
    if ((a >= 0) != (r >= 0)).any():
        return float('inf')
    return float(np.abs(a[reach] - r[reach]).max()) if reach.any() else 0.0


def solve_t0(c, rd, n, log_name='openCARP.log', timeout_s=7200):
    """Run an openCARP RE command (its own tend and stimuli, so the parser's checks and the FIM's sources are the beat's)
    only through its t = 0 solve: an eikonal state checkpoint at the first step (-num_tsav 1 -tsav[0] 0.01; written
    with fclose, unlike the buffered act.igb) gives every node's activation time; then the run is stopped.
    Returns (state, activation times with -1 for unreached, as act.igb)."""
    os.makedirs(rd, exist_ok=True)
    c = list(c) + ['-num_tsav', '1', '-tsav[0]', '0.01', '-write_statef', os.path.join(rd, 'state')]
    log = open(os.path.join(rd, log_name), 'w')
    p = subprocess.Popen(c, stdout=log, stderr=subprocess.STDOUT, env=dict(os.environ, OMP_NUM_THREADS='1'), start_new_session=True, cwd=rd)
    t0, last, st = time.time(), -1, 'timeout'
    while time.time() - t0 < timeout_s:
        time.sleep(2)
        f = [x for x in os.listdir(rd) if x.startswith('state') and x.endswith('.roe.dat')]
        if f:
            sz = os.path.getsize(os.path.join(rd, f[0]))
            if sz == last and sz > 0:
                st = 'stopped after the t = 0 solve'; break
            last = sz
        if p.poll() is not None:
            st = f'exit {p.returncode}'; break
    if p.poll() is None:
        os.killpg(p.pid, signal.SIGTERM); p.wait()
    log.close()
    f = [x for x in os.listdir(rd) if x.startswith('state') and x.endswith('.roe.dat')]
    if not f:
        return st, None
    ta = np.loadtxt(os.path.join(rd, f[0]), usecols=3, converters={3: lambda x: float(x)})
    for x in os.listdir(rd):                                                                  # the ionic state dump is large and not needed
        if x.startswith('state') and x.endswith('.roe'):
            os.remove(os.path.join(rd, x))
    return st, np.where(np.isfinite(ta), ta, -1.0)


def fim_rerun(b, d, iters=FIM_CHECK):
    """D50's check: the beat's own t = 0 solve rerun alone (same command, inputs and thread count, stopped once the t = 0
    solve is written) at each max_iter; the largest |activation time difference| against the beat's own act.igb (counts)."""
    cmd, _, _ = command(b)
    ref = act0(os.path.join(d, 'act.igb'))
    out = {}
    for it in iters:
        rd = os.path.join(d, f'fim_check_{it}')
        c = list(cmd)
        for k, v in (('-simID', rd), ('-dream.fim.max_iter', str(it))):
            c[c.index(k) + 1] = v
        st, ta = solve_t0(c, rd, len(ref))
        its, act = fim_counts(rd)
        out[str(it)] = {'run': st, 'iterations': its, 'active_list_at_exit': act,
                        'max_abs_diff_ms': fim_diff(ta, ref) if ta is not None and len(ta) == len(ref) else float('inf')}
    return out


def check6(vm, tend, chunk=20000):
    """Section 4 check 6, per node from the 1 ms Vm (frame k = k ms of simulated time): the upstroke time at 1 ms (the
    frame ending the largest 1 ms rise), APD90 by cell52.apd90's rule (90 % of the beat's amplitude, last up-crossing
    before the peak, first down-crossing after it, linear interpolation; nan if there is none inside the window) with its
    repolarisation time, the peak Vm, and P7's EAD flag (dV/dt > +0.05 mV/ms for >= 2 ms between the peak + 20 ms and the
    APD90 crossing while V > -60 mV; cell52_p7.events). Values are kept, never printed (reading hold); counts only."""
    T, n = vm.shape
    out = {k: np.full(n, np.nan, np.float32) for k in ('upstroke_1ms_ms', 'apd90_ms', 'repol_ms', 'vmax_mV')}
    out['ead'] = np.zeros(n, bool)
    k = np.arange(T - 1)[:, None]
    for s in range(0, n, chunk):
        V = np.asarray(vm[:, s:s + chunk], np.float64); c = V.shape[1]; cols = np.arange(c)
        dV = np.diff(V, axis=0)
        ip = np.argmax(V, axis=0); vmax = V[ip, cols]
        vmin = np.where(ip > 0, np.min(np.where(np.arange(T)[:, None] < np.maximum(ip, 1), V, np.inf), axis=0), V[0])
        thr = vmax - 0.9 * (vmax - vmin)
        upc = (V[:-1] < thr) & (V[1:] >= thr) & (k < ip)
        dnc = (V[:-1] > thr) & (V[1:] <= thr) & (k > ip)
        hu, hd = upc.any(0), dnc.any(0)
        i = (T - 2) - np.argmax(upc[::-1], axis=0); j = np.argmax(dnc, axis=0)
        ta = i + (thr - V[i, cols]) / np.where(hu, V[i + 1, cols] - V[i, cols], 1.0)
        tr = j + (thr - V[j, cols]) / np.where(hd, V[j + 1, cols] - V[j, cols], 1.0)
        ok = hu & hd
        up = (k > ip + 20) & (k < np.where(hd, j, -1)) & (V[:-1] > -60.0) & (dV > 0.05)
        out['ead'][s:s + c] = ok & (up[:-1] & up[1:]).any(0)
        out['upstroke_1ms_ms'][s:s + c] = np.argmax(dV, axis=0) + 1.0
        out['apd90_ms'][s:s + c] = np.where(ok, tr - ta, np.nan)
        out['repol_ms'][s:s + c] = np.where(ok, tr, np.nan)
        out['vmax_mV'][s:s + c] = vmax
    return out


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
            elif rec.get('fim_check_failed'):
                rec['status'] = status = 'failed (t = 0 FIM at the cap moved by more than 0.01 ms at 1001-1003: numerical failure, D50 / D42 (1))'
            elif rec.get('flagged_vm_above_every_excitable'):
                rec['status'] = status = 'failed (a flagged node above every excitable node: numerical failure, addendum 2 item 4)'
        except Exception as e:                                                            # noqa: BLE001
            rec['status'] = status = f'failed in post-processing: {e!r}'
    json.dump(rec, open(os.path.join(bdir(b), 'summary.json'), 'w'), indent=1)
    labnote(f"- Beat ended, PC clock {time.strftime('%d %b %H:%M')}: {b['id']}: {status}; wall {rec['wall_s'] / 3600:.2f} h "
            f"({rec['s_per_sim_ms']} s per simulated ms), lowest MemAvailable {rec['min_mem_available_mb']} MB"
            + (f", unactivated nodes {rec.get('unactivated_nodes')}, NaN frames {rec.get('nan_frames')}" if 'nan_frames' in rec else '')
            + (f", EAD-flagged nodes {rec.get('ead_flagged_excitable_nodes')}" if b['engine'] == 're' and 'ead_flagged_excitable_nodes' in rec else '')
            + (f", t = 0 FIM {rec.get('fim_t0_iterations')} iterations, active list at exit {rec.get('fim_t0_active_list_at_exit')}" if b['engine'] == 're' and 'nan_frames' in rec else '')
            + (f" (D50 check at 1001-1003: largest difference {rec['fim_check_max_abs_diff_ms']:.4g} ms)" if 'fim_check_max_abs_diff_ms' in rec else '')
            + (', check 6 by class (EAD / repolarised in window): ' + '; '.join(f"{k} {v['ead']} / {v['repolarised_in_window']}" for k, v in rec['check6_by_class'].items())
               if 'check6_by_class' in rec else '')
            + (f", flagged nodes {rec['flagged_nodes']} (above every excitable node: {rec.get('flagged_vm_above_every_excitable', 'n/a')}; driven again: not measured)"
               if rec.get('flagged_nodes') else '') + '.')
    return rec['status']


def night(hours=8.0):
    """One chunk. Lock thread's rules (note of 3 Nov 13:35 UTC, section 1): nothing else runs; a beat that fails (exit,
    NaN, unactivated excitable nodes, no log progress for 30 min) starts no new beat in its lane, keeps its raw file and
    waits for a report; a memory kill is re-run in the next chunk with one RE+ lane fewer; no beat starts if C: would fall
    below 10 GB."""
    ch = choices()
    if not ch.get('released') or not ch.get('release'):
        sys.exit('t1_choices.json releases no beat (the lock thread\'s conditions are not all logged): nothing started')
    if not os.path.exists(os.path.join(REPO, 'params', 'v52_mono_conductivities.json')):
        sys.exit('step 6 not done (params/v52_mono_conductivities.json missing): nothing started')
    t_end = time.time() + hours * 3600
    q = [b for b in queue() if not done(b)]
    lanes = int(ch.get('re_lanes', RE_LANES))
    labnote(f"\n### 2026-11-03_v52_11_t1_27 night chunk (PC clock {time.strftime('%d %b %H:%M')}): {len(q)} released beats left "
            f"({', '.join(ch['release'])}), {hours:g} h, up to {lanes} RE+ lanes, then monodomain on {MONO_NP} processes; C: {c_free_gb():.1f} GB free")
    jobs, stopped, mono_ok, notes = [], False, True, []
    last = time.time()
    while True:
        now = time.time()
        gap = now - last
        if gap > 300:                                     # the chunk was paused (pause.sh) or the PC slept: not a stall
            t_end += gap
            for j in jobs:
                j['resumed'] = now
            labnote(f"- Chunk resumed, PC clock {time.strftime('%d %b %H:%M')}: paused for about {gap / 60:.0f} min; chunk end moved by that, "
                    f"stall clocks of the {len(jobs)} running beats restarted (nothing else changes).")
        last = now
        for j in list(jobs):
            r = j['p'].poll()
            if r is not None:
                st = close(j, 'ok' if r == 0 else f'failed (exit {r})'); jobs.remove(j)
                if st != 'ok':
                    if j['b']['engine'] == 're':
                        lanes -= 1
                    else:
                        mono_ok = False
            elif now - max(j['t0'], j.get('resumed', 0.0), os.path.getmtime(os.path.join(bdir(j['b']), 'openCARP.log'))) > 1800:
                os.killpg(j['p'].pid, signal.SIGTERM); j['p'].wait(); close(j, 'failed (no progress for 30 min)'); jobs.remove(j)
                if j['b']['engine'] == 're':
                    lanes -= 1
                else:
                    mono_ok = False
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
        nxt = re_todo[0] if (re_todo and lanes > 0) else (mono_todo[0] if (mono_todo and mono_ok) else None)
        if nxt is not None and not stopped:
            need = nxt['tend_ms'] * 1.51e-3 * 1.1                                           # GB, C68's 1.51 MB per ms, +10 %
            if c_free_gb() - need < 10.0:
                notes.append(f"C: {c_free_gb():.1f} GB free, {nxt['id']} needs about {need:.1f} GB: no beat started (10 GB floor)")
                stopped = True
            elif nxt['engine'] == 're' and n_mono == 0 and n_re < lanes and mem_mb() > 2600:
                jobs.append(start(nxt)); time.sleep(90); continue
            elif nxt['engine'] == 'mono' and n_re == 0 and n_mono == 0:
                jobs.append(start(nxt)); time.sleep(30); continue
        if not jobs:
            break
        time.sleep(30)
    left = [b['id'] for b in queue() if not done(b)]
    labnote(f"- Night chunk ended, PC clock {time.strftime('%d %b %H:%M')}: {len(left)} released beats left; C: {c_free_gb():.1f} GB free"
            + (' (memory guard stopped a beat)' if stopped else '') + ('; ' + '; '.join(notes) if notes else '') + '.')
    print('night chunk ended;', len(left), 'beats left', flush=True)


def check6_kept(eng='mono'):
    """Check 6 from the kept raw files of finished beats that predate it (the control heart's 9 monodomain beats of 3-4 Nov):
    per-node values into <beat>/check6.npz; counts only printed and returned."""
    out = {}
    for b in [x for h in HEARTS if os.path.exists(hdir(h, 'prep.json')) for x in _all_beats(h)]:
        if b['engine'] != eng or not done(b) or not os.path.exists(os.path.join(bdir(b), 'vm.igb')):
            continue
        f = os.path.join(bdir(b), 'check6.npz')
        M = np.load(hdir(b['heart'], 'mesh', 'maps.npz'))
        vm = igb(os.path.join(bdir(b), 'vm.igb'))
        flag = np.zeros(vm.shape[1], bool)
        if 'flagged' in M.files:
            flag[M['flagged']] = True
        if os.path.exists(f):
            z = np.load(f); c6 = {k[3:]: z[k] for k in z.files if k.startswith('c6_')}
        else:
            c6 = check6(vm, b['tend_ms'])
            np.savez_compressed(f, flagged=np.where(flag)[0], **{f'c6_{k}': v for k, v in c6.items()})
        cls = node_classes(b['heart'], b['site'], len(flag))
        out[b['id']] = {'frames': int(vm.shape[0]), 'ead_flagged_excitable_nodes': int(c6['ead'][~flag].sum()),
                        'by_class': {k: {'ead': int((c6['ead'] & ~flag & (cls == i)).sum()),
                                         'repolarised_in_window': int((np.isfinite(c6['apd90_ms']) & ~flag & (cls == i)).sum()),
                                         'nodes': int((~flag & (cls == i)).sum())} for i, k in enumerate(CLASSES)},
                        'no_repolarisation_in_window_excitable_nodes': int((~np.isfinite(c6['apd90_ms']))[~flag].sum()),
                        'excitable_nodes': int((~flag).sum())}
        print(b['id'], out[b['id']], flush=True)
        del vm
    return out


def _all_beats(h):
    P = json.load(open(hdir(h, 'prep.json')))
    win = choices().get('mono_window', 'qrs')
    return [{'id': f"{h}/{x['site']}/{eng}", 'heart': h, 'site': x['site'], 'engine': eng,
             'tend_ms': x['re_tend_ms'] if (eng == 're' or win == 'r16') else x['qrs_tend_ms']} for x in P['beats'] for eng in ('re', 'mono')]


def test(h, site, eng, tend):
    """A short beat into <site>/<engine>_test (raw output kept), to check the set-up before the first night."""
    b = {'id': f'{h}/{site}/{eng}_test', 'heart': h, 'site': site, 'engine': eng, 'tend_ms': float(tend), 'est_h': 0.0, 'test': True,
         'dir': hdir(h, site, f'{eng}_test')}
    j = start(b)
    while j['p'].poll() is None:
        time.sleep(5); mm = mem_mb(); j['low'] = min(j['low'], mm)
        if mm < MIN_MB:
            os.killpg(j['p'].pid, signal.SIGTERM); j['p'].wait(); close(j, f'stopped by memory guard ({mm:.0f} MB available)'); return
    close(j, 'ok' if j['p'].returncode == 0 else f"failed (exit {j['p'].returncode})")
    print(json.dumps({k: v for k, v in json.load(open(os.path.join(bdir(b), 'summary.json'))).items() if k != 'command'}, indent=1))


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
    elif a == 'test':
        test(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif a == 'check6':
        print(json.dumps(check6_kept(sys.argv[2] if len(sys.argv) > 2 else 'mono'), indent=1))
    elif a == 'night':
        night(float(sys.argv[2]) if len(sys.argv) > 2 else 8.0)
    else:
        {'plan': plan, 'status': status, 'analyze': analyze}[a]()
