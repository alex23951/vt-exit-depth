"""27-site monodomain check on the frozen v5.1 model (Aim 1 gate 9, locked 15 Oct 2026; plan: PLAN.md in this folder).

Sites (as batch_2026-10-03 agreement_sites()): per heart the original LV mid-endocardial site of the template beat
(runs/<template>/summary_06.json site_node), LV free wall phi180 z0.5 at 50 / 90 %, septum phi0 z0.5 at 10 / 50 / 90 %,
RV free wall q50 z0.5 at 10 / 50 / 90 %.
"Eikonal" beat = the v5.1 graph beat (heart51.Heart51: nodal 2-ring tissue solver, v5.1 network, junction 4 / 2 ms,
pseudo-Vm template, v5.1 sigma_i weights); its junction exit times (network time + 4 ms, for every junction whose exit is
not later than its muscle's activation) are replayed in the monodomain beat as timed stimuli (one-way coupling, accepted
12 Oct 2026), each junction widened to the nodes within 1.0 mm and grouped in 0.25 ms bins, as the 12 Oct check.
Monodomain beat: openCARP v20, Tomek, dt 10 us, conductivities params/v51_mono_conductivities.json (step 1, tuned to the
intrinsic v5.1 speeds on a synthetic slab, mono_slab51.py; tags 1 and 2 alike, no fast layer), v5.1 fibres (mesh biv51 = biv.pts, bivF.elem, bivF_v51.lon), site
stimulus 400 uA/cm3 x 1 ms on the nodes within 1.5 mm, LAT -10 mV, Vm every 1 ms, tend = graph total activation + 30 ms
(rounded up to 10 ms). Memory guard: openCARP is stopped if MemAvailable < 900 MB. Processes: MONO_NP (default 4).
ECG of both beats: the v5.1 lead fields (data/biv/<H>/ecgW_v51.npz, sigma_i). Scoring: ecg_depth_criteria 0.4.0,
pace-map convention (stimulus onset, clean ECG); measures pseudo_delta_ms, idt_v2_ms, srs_ms and the time to the largest
precordial deflection (= mdi_daniels x (offset_any_lead_ms - onset_ms), the Daniels MDI numerator); true mode beside.
Gate: >= 90 % of the 108 site-measure pairs within 5 ms (>= 98); maximum difference reported; last activation reported.

Bias subsample (locked fallback after a fail, 15 Oct 2026: "a subsample, one site per region per heart, gives each onset
measure's eikonal-minus-monodomain bias, and onset results are reported with that bias band"; Alex 19 Oct 2026 17:44 UTC
"Yes"): regions = the 7 pilot site families. Per heart, one site per family is drawn with numpy default_rng(0) (hearts in
HEARTS order, families in BIAS_FAMILIES + COVERED order, from the sorted site ids): for the 4 families outside the 27-site
set from all the family's pilot sites (12 new beats), for the 3 covered families from that family's check sites (beats
already run). The band per onset measure (graph minus monodomain): median, IQR and range over the 21 drawn sites; the same
over all finished sites (27 + 12) beside it.

Usage (repo root, venv, PATH with openCARP's mpiexec; one beat at a time):
  HEART=<H> python -B .../mono51.py test [bias]     10 ms of the first (bias) site, junction starts squeezed into 2-8 ms
  HEART=<H> python -B .../mono51.py run [site ...]  full beats of the heart (skips finished ones)
  python -B .../mono51.py analyze                    all finished check beats -> results51.csv, gate51.json
  python -B .../mono51.py draw                       draws the bias subsample -> bias_sites51.json (once)
  HEART=<H> python -B .../mono51.py bias             the heart's 4 new bias-subsample beats (skips finished ones)
  python -B .../mono51.py analyze-bias               bias bands -> bias51.csv, bias51.json
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
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
OUTR = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'beats')
NP = int(os.environ.get('MONO_NP', '4'))
STIM_R_UM, PMJ_R_UM, BIN_MS = 1500.0, 1000.0, 0.25
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
MEASURES = ['pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 't_largest_precordial_ms']
BIAS_FAMILIES = ['rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course']      # regions outside the 27-site set
COVERED = ['lv_free_wall', 'lv_septum', 'rv_free_wall']                     # regions inside it
BIAS_FILE = os.path.join(HERE, 'bias_sites51.json')


def template_run(h):
    return os.path.join(REPO, 'runs', '2026-10-02_biv_fullqrs' if h == 'Y5HYEDL4' else f'2026-10-03_{h}_fullqrs')


def check_sites(h):
    S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
    pick = lambda fam, pos, d: next(s for s in S if s['family'] == fam and s['position'] == pos and s['level_z'] == 0.5 and int(round(s['depth_target'] * 100)) == d)
    orig = int(json.load(open(os.path.join(template_run(h), 'summary_06.json')))['site_node'])
    out = [{'id': 'lv_free_wall_original_d0', 'node': orig, 'family': 'lv_free_wall', 'depth_target': 0.0}]
    out += [pick('lv_free_wall', 'phi180', d) for d in (50, 90)]
    out += [pick('lv_septum', 'phi0', d) for d in (10, 50, 90)]
    out += [pick('rv_free_wall', 'q50', d) for d in (10, 50, 90)]
    return out


def draw_bias():
    if os.path.exists(BIAS_FILE):
        sys.exit(f'{BIAS_FILE} exists; the draw is made once')
    rng = np.random.default_rng(0)
    out = {'rule': 'numpy default_rng(0); hearts in HEARTS order; families in BIAS_FAMILIES + COVERED order; one id from the sorted candidates',
           'hearts': {}}
    for h in HEARTS:
        S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
        chk = check_sites(h)
        d = {'check': [c['id'] for c in chk], 'new': {}, 'covered': {}}
        for fam in BIAS_FAMILIES:
            ids = sorted(x['id'] for x in S if x['family'] == fam)
            d['new'][fam] = ids[int(rng.integers(len(ids)))]
        for fam in COVERED:
            ids = sorted(x['id'] for x in chk if x['family'] == fam)
            d['covered'][fam] = ids[int(rng.integers(len(ids)))]
        out['hearts'][h] = d
    json.dump(out, open(BIAS_FILE, 'w'), indent=1)
    print(json.dumps(out, indent=1))


def bias_sites(h):
    new = json.load(open(BIAS_FILE))['hearts'][h]['new']
    S = {x['id']: x for x in json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))}
    return [S[new[fam]] for fam in BIAS_FAMILIES]


def mem_avail_mb():
    for l in open('/proc/meminfo'):
        if l.startswith('MemAvailable'):
            return int(l.split()[1]) / 1024
    return 1e9


def vtx_write(f, nodes):
    with open(f, 'w') as fh:
        fh.write(f'{len(nodes)}\nintra\n')
        np.savetxt(fh, np.asarray(nodes, dtype=np.int64), fmt='%d')


def graph_beat(H51, Hh, site_node):
    """Graph beat with the network times: muscle T (N,), junction exit times for replay [(muscle node, t_exit)]."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    N, e, w, net = Hh.N, Hh.e, Hh.w, Hh.net
    rows, cols, data = [e[:, 0], e[:, 1]], [e[:, 1], e[:, 0]], [w, w]
    M = len(net['nodes'])
    gn = H51.net_graph(net, Hh.pts_um / 1e3).tocoo(); kk = (gn.row < M) & (gn.col < M)
    m = net['nodes'][net['pmj']]; j = N + net['pmj']
    rows += [N + gn.row[kk], m, j]; cols += [N + gn.col[kk], j, m]
    data += [gn.data[kk], np.full(len(m), Hh.d_ret), np.full(len(m), Hh.d_ant)]
    src = N + M
    s = np.where(np.linalg.norm(Hh.pts_um - Hh.pts_um[site_node], axis=1) < STIM_R_UM)[0]
    rows.append(np.full(len(s), src)); cols.append(s); data.append(np.full(len(s), 1e-6))
    G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
    D = dijkstra(G, directed=True, indices=src) - 1e-6
    T = D[:N]
    t_exit = D[N + net['pmj']] + Hh.d_ant
    drive = np.isfinite(t_exit) & (t_exit <= T[m] + 1e-6)          # the junction set (or tied) its muscle's time
    return T, list(zip(m[drive].tolist(), t_exit[drive].tolist())), s


def beat_dir(h, sid, test=False):
    return os.path.join(OUTR, h, sid + ('_test' if test else ''))


def run(test=False, only=None, bias=False):
    import heart51 as H51
    h = os.environ['HEART']
    Hh = H51.Heart51(h)
    par = json.load(open(os.path.join(REPO, 'params', 'v51_mono_conductivities.json')))['hearts'][h]
    if not par['within_3pct']:
        sys.exit(f'{h}: monodomain conductivities not within 3 % (step 1)')
    g = par['conductivities_S_m']
    mesh = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'acceptance_c', 'mesh', 'biv51')
    from scipy.spatial import cKDTree
    tree = cKDTree(Hh.pts_um)
    pool = bias_sites(h) if bias else check_sites(h)
    sites = pool[:1] if test else [s for s in pool if only is None or s['id'] in only]
    for s in sites:
        rd = beat_dir(h, s['id'], test)
        if not test and os.path.exists(os.path.join(rd, 'summary_mono.json')) and json.load(open(os.path.join(rd, 'summary_mono.json')))['status'] == 'ok':
            continue
        os.makedirs(rd, exist_ok=True)
        T, jx, ball = graph_beat(H51, Hh, int(s['node']))
        t, ecg = Hh.ecg(T)
        np.save(os.path.join(rd, 'graph_T.npy'), T.astype(np.float32)); np.save(os.path.join(rd, 'graph_ecg.npy'), ecg.astype(np.float32))
        tend = 10.0 if test else float(np.ceil((T.max() + 30) / 10) * 10)
        vtx_write(os.path.join(rd, 'stim.vtx'), ball)
        stims = [(os.path.join(rd, 'stim'), 0.0)]
        if jx:
            jn = np.array([a for a, _ in jx]); jt = np.round(np.array([b for _, b in jx]) / BIN_MS) * BIN_MS
            if test:
                lo, hi = jt.min(), jt.max()
                jt = 2.0 + 6.0 * (jt - lo) / max(hi - lo, 1e-9)
                jt = np.round(jt / BIN_MS) * BIN_MS
            sd = os.path.join(rd, 'pmj'); os.makedirs(sd, exist_ok=True)
            for k, tb in enumerate(np.unique(jt)):
                nodes = jn[jt == tb]
                wide = np.unique(np.concatenate([tree.query_ball_point(Hh.pts_um[n], PMJ_R_UM) for n in nodes]).astype(np.int64))
                f = os.path.join(sd, f'pmj_{k:04d}')
                vtx_write(f + '.vtx', wide)
                stims.append((f, float(tb)))
        json.dump([{'vtx': v, 'start': t0} for v, t0 in stims], open(os.path.join(rd, 'stims.json'), 'w'), indent=0)
        so = ['-num_stim', len(stims)]
        for i, (vf, t0) in enumerate(stims):
            so += [f'-stim[{i}].crct.type', 0, f'-stim[{i}].elec.vtx_file', vf, f'-stim[{i}].ptcl.start', t0,
                   f'-stim[{i}].pulse.strength', 400.0, f'-stim[{i}].ptcl.duration', 1.0, f'-stim[{i}].ptcl.npls', 1]
        gr = ['-num_gregions', 1, '-gregion[0].num_IDs', 2, '-gregion[0].ID[0]', 1, '-gregion[0].ID[1]', 2,
              '-gregion[0].g_il', g['fibre']['gi'], '-gregion[0].g_el', g['fibre']['ge'],
              '-gregion[0].g_it', g['sheet']['gi'], '-gregion[0].g_et', g['sheet']['ge'],
              '-gregion[0].g_in', g['normal']['gi'], '-gregion[0].g_en', g['normal']['ge']]
        cmd = ['mpiexec', '-n', NP, 'openCARP', '-meshname', mesh, '-simID', rd,
               '-bidomain', 0, '-dt', 10.0, '-parab_solve', 1, '-tend', tend, '-spacedt', 1.0, '-timedt', 5.0,
               '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
               '-num_LATs', 1, '-lats[0].ID', 'LATs', '-lats[0].all', 0, '-lats[0].measurand', 0,
               '-lats[0].threshold', -10, '-lats[0].method', 1] + so + gr
        t0, low, status = time.time(), 1e9, 'ok'
        with open(os.path.join(rd, 'openCARP.log'), 'w') as log:
            p = subprocess.Popen([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            while p.poll() is None:
                time.sleep(5)
                mm = mem_avail_mb(); low = min(low, mm)
                if mm < 900:
                    os.killpg(p.pid, signal.SIGTERM); status = f'stopped by memory guard ({mm:.0f} MB available)'
                    p.wait(); break
            if status == 'ok' and p.returncode != 0:
                status = f'failed (openCARP exit {p.returncode})'
        wall = time.time() - t0
        summ = {'heart': h, 'site': s['id'], 'site_node': int(s['node']), 'graph_total_activation_ms': round(float(T.max()), 2),
                'n_stimuli': len(stims), 'junction_stimuli': len(jx), 'tend_ms': tend, 'np': NP, 'wall_s': round(wall, 1),
                's_per_sim_ms': round(wall / tend, 1), 'min_mem_available_mb': round(low), 'status': status, 'test': test,
                'conductivities': g}
        json.dump(summ, open(os.path.join(rd, 'summary_mono.json'), 'w'), indent=1)
        print(json.dumps({k: v for k, v in summ.items() if k != 'conductivities'}), flush=True)
        if status != 'ok':
            sys.exit(f'{h} {s["id"]}: {status}')


def igb(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def score(ecg, last):
    from ecg_depth_criteria import from_leads, measure_beat
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, LEADS.index(l)]), ecg[:, LEADS.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    X = from_leads(leads)
    out = {}
    for mode, kw in (('pace', dict(stim_ms=float(pad))), ('true', dict(onset_ms=float(pad), offset_ms=float(last + pad)))):
        m = measure_beat(X, 1000.0, **kw)
        r = {k: float(m[k]) for k in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'qrs_duration_any_lead_ms', 'mdi_daniels')}
        r['t_largest_precordial_ms'] = float(m['mdi_daniels'] * (m['offset_any_lead_ms'] - m['onset_ms']))
        out[mode] = r
    return out


def score_site(h, s, W):
    """Scores one finished beat (graph vs monodomain); None if the beat is not finished."""
    rd = beat_dir(h, s['id'])
    f = os.path.join(rd, 'summary_mono.json')
    if not os.path.exists(f) or json.load(open(f))['status'] != 'ok':
        return None
    Tg = np.load(os.path.join(rd, 'graph_T.npy')).astype(float)
    eg = np.load(os.path.join(rd, 'graph_ecg.npy')).astype(float)
    Tm = np.loadtxt(os.path.join(rd, 'init_acts_LATs-thresh.dat'))
    vm = igb(os.path.join(rd, 'vm.igb')).astype(float)
    em = vm @ W.T
    np.save(os.path.join(rd, 'mono_ecg.npy'), em.astype(np.float32))
    ok = Tm >= 0
    sg, sm = score(eg, float(Tg.max())), score(em, float(Tm[ok].max()))
    base = {'heart': h, 'site': s['id'], 'activated_pct_mono': round(100 * float(ok.mean()), 2),
            'total_graph_ms': round(float(Tg.max()), 1), 'total_mono_ms': round(float(Tm[ok].max()), 1),
            'node_within_5ms_pct': round(100 * float((np.abs(Tm[ok] - Tg[ok]) <= 5).mean()), 1),
            'node_median_diff_ms': round(float(np.median(Tm[ok] - Tg[ok])), 2)}
    for mode in ('pace', 'true'):
        for k in MEASURES + ['qrs_duration_any_lead_ms', 'mdi_daniels']:
            base[f'{mode}_{k}_graph'] = sg[mode][k]; base[f'{mode}_{k}_mono'] = sm[mode][k]
            base[f'{mode}_{k}_diff'] = sm[mode][k] - sg[mode][k]
    return base


def analyze():
    import pandas as pd
    rows = []
    for h in HEARTS:
        W = np.load(os.path.join(REPO, 'data', 'biv', h, 'ecgW_v51.npz'))['W'].astype(float)
        for s in check_sites(h):
            r = score_site(h, s, W)
            if r is not None:
                rows.append(r)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(HERE, 'results51.csv'), index=False)
    d = np.concatenate([R[f'pace_{k}_diff'].to_numpy() for k in MEASURES]) if len(R) else np.array([])
    fin = np.isfinite(d)
    within = int((np.abs(d[fin]) <= 5).sum())
    gate = {'sites_done': int(len(R)), 'pairs': int(len(d)), 'pairs_scorable': int(fin.sum()), 'within_5ms': within,
            'pct_within': round(100 * within / max(int(fin.sum()), 1), 1), 'needed': '>= 90 % of 108 pairs (>= 98)',
            'max_abs_diff_ms': round(float(np.nanmax(np.abs(d))), 1) if fin.any() else None,
            'per_measure_within': {k: f"{int((np.abs(R[f'pace_{k}_diff']) <= 5).sum())} / {int(R[f'pace_{k}_diff'].notna().sum())}" for k in MEASURES} if len(R) else {},
            'pass': (bool(within >= 98) if len(R) == 27 else None)}
    json.dump(gate, open(os.path.join(HERE, 'gate51.json'), 'w'), indent=1)
    print(json.dumps(gate, indent=1))


def analyze_bias():
    import pandas as pd
    B = json.load(open(BIAS_FILE))['hearts']
    rows = []
    for h in HEARTS:
        W = np.load(os.path.join(REPO, 'data', 'biv', h, 'ecgW_v51.npz'))['W'].astype(float)
        drawn = set(B[h]['new'].values()) | set(B[h]['covered'].values())
        for s in check_sites(h) + bias_sites(h):
            r = score_site(h, s, W)
            if r is not None:
                r |= {'family': s['family'], 'depth_target': s['depth_target'], 'in_subsample': s['id'] in drawn,
                      'set': 'check' if s['id'] in B[h]['check'] else 'bias'}
                rows.append(r)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(HERE, 'bias51.csv'), index=False)
    band = lambda x: {'n': int(x.notna().sum()), 'median': round(float(x.median()), 1), 'iqr': [round(float(x.quantile(.25)), 1), round(float(x.quantile(.75)), 1)],
                      'range': [round(float(x.min()), 1), round(float(x.max()), 1)]}
    out = {'definition': 'eikonal (graph) minus monodomain, pace-map convention, ms', 'sites_finished': int(len(R)),
           'subsample_finished': int(R.in_subsample.sum()), 'subsample_planned': 7 * len(HEARTS), 'bands': {}}
    for k in MEASURES:
        b = -R[f'pace_{k}_diff']
        out['bands'][k] = {'subsample': band(b[R.in_subsample]), 'all_sites': band(b),
                           'per_family_median_subsample': {fam: round(float(b[R.in_subsample & (R.family == fam)].median()), 1)
                                                           for fam in BIAS_FAMILIES + COVERED if (R.in_subsample & (R.family == fam)).any()}}
    json.dump(out, open(os.path.join(HERE, 'bias51.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'test':
        run(test=True, bias=sys.argv[2:3] == ['bias'])
    elif sys.argv[1] == 'run':
        run(only=set(sys.argv[2:]) or None)
    elif sys.argv[1] == 'bias':
        run(bias=True)
    elif sys.argv[1] == 'draw':
        draw_bias()
    elif sys.argv[1] == 'analyze-bias':
        analyze_bias()
    else:
        analyze()
