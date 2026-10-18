"""Step 4.3 acceptance C (v5.1 brief; Alex 17 Oct 2026 06:20:06 UTC "Go for acceptance C and S13. Stop and tell me if any
openCARP run hits the 20-minute cap."): openCARP eikonal reference vs the v5.1 graph solver, tissue only.

openCARP v20 (ffce195), as sims/biv_model/12_eikonal.py --mode eik --no-fast-layer: -dream.solve 0 (FIM), tol 0.001,
max_iter 1e9, one process with 6 OpenMP threads; v5.1 speeds WITHOUT graph factors (params/v51_speeds.json) on both
element tags; v5.1 fibres (data/biv/<H>/fibres_v51/bivF_v51.lon); mesh bivF (same tets as biv.elem); single-node stimulus
at the site node; no network. Cap 20 min per run: a run that hits it stops the batch (exit code 3).
Graph: graph51 Tissue with the slab-calibrated factors (params/v51_graph_factors.json), same single node, no limit.
Gates per site: median |dt| <= 1 ms; p95 |dt| <= 2 % of the openCARP total activation; total activation within +-2 %;
no -1 (unactivated) in act.
Sites (12 per heart): LV free wall phi180 z0.5 at 10 / 90 %; septum phi0 at z0.5 and z0.25 (apical), 50 %; RV free wall q50
z0.5 at 10 / 90 %; septal and free-wall RVOT 50 %; RCC and LCC cusps 50 %; summit superior and inferior-lateral 50 %.
Stages (repo root, venv):  HEART=<H> python -B analysis/v51_2026-10-15/04_build/acceptance_c.py run   (openCARP)
                           HEART=<H> python -B analysis/v51_2026-10-15/04_build/acceptance_c.py retry (capped sites, once)
                           python -B analysis/v51_2026-10-15/04_build/acceptance_c.py compare             (all hearts)
18 Oct 2026 (Alex's "go", 12:03 UTC, on the decisions of 17 Oct 07:58 UTC): 'run' now skips a site that hit the cap, so
the remaining sites run; 'retry' runs each capped site once more with dream.fim.max_iter raised from 1e9 to 2147483647 (the
largest value of openCARP's int parameter) into <site>/retry/, and a second cap is recorded as openCARP non-convergence.
'compare' takes the graph metric ('nodal' as 17 Oct, or 'element') and writes acceptance_c_<metric>_<date>.json.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import graph51 as g                                                    # noqa: E402
import solver51 as S                                                   # noqa: E402

SITES = ['lv_free_wall_phi180_z0.5_d10', 'lv_free_wall_phi180_z0.5_d90', 'lv_septum_phi0_z0.5_d50', 'lv_septum_phi0_z0.25_d50',
         'rv_free_wall_q50_z0.5_d10', 'rv_free_wall_q50_z0.5_d90', 'rvot_septal_z_d50', 'rvot_free_wall_z_d50',
         'aortic_cusp_rcc_z_d50', 'aortic_cusp_lcc_z_d50', 'lv_summit_superior_z_d50', 'lv_summit_inferior_lateral_z_d50']
CAP_S = 1200.0
OMP = '6'
MAX_ITER = 1000000000
MAX_ITER_RETRY = 2147483647
RETRY_SITES = {'7D98EVAR': ['lv_free_wall_phi180_z0.5_d90']}     # the site Alex's retry decision names (17 Oct 07:58 UTC)


def rundir(h, site=None):
    d = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'acceptance_c')
    return d if site is None else os.path.join(d, site)


def igb_last(f):
    b = open(f, 'rb').read(); x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float)


def mesh51(h):
    d = os.path.join(rundir(h), 'mesh'); os.makedirs(d, exist_ok=True)
    B = os.path.join(REPO, 'data', 'biv', h)
    for ext, src in (('pts', os.path.realpath(os.path.join(B, 'bivF.pts'))), ('elem', os.path.join(B, 'bivF.elem')),
                     ('lon', os.path.join(B, 'fibres_v51', 'bivF_v51.lon'))):
        dst = os.path.join(d, f'biv51.{ext}')
        if not os.path.lexists(dst):
            os.symlink(src, dst)
    return os.path.join(d, 'biv51')


def run():
    h = os.environ['HEART']
    mesh, greg, sites = setup(h)
    status_f = os.path.join(rundir(h), 'status.json')
    status = json.load(open(status_f)) if os.path.exists(status_f) else {}
    for sid in SITES:
        st = status.get(sid, {}).get('outcome', '')
        if st.startswith('ok') or 'cap' in st or 'non-convergence' in st:
            continue                                # capped sites: 'retry' stage
        status[sid] = one_run(h, sid, rundir(h, sid), mesh, greg, sites, MAX_ITER)
        json.dump(status, open(status_f, 'w'), indent=1)
        print(f"{h} {sid}: {status[sid]}", flush=True)
        if status[sid]['outcome'] != 'ok':
            print(f'{h} {sid}: batch stopped', flush=True)
            sys.exit(3 if 'cap' in status[sid]['outcome'] else 4)


def one_run(h, sid, d, mesh, greg, sites, max_iter, cap_s=CAP_S):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'stim.vtx'), 'w') as fh:
        fh.write(f"1\nintra\n{int(sites[sid]['node'])}\n")
    cmd = ['openCARP', '-meshname', mesh, '-simID', d, '-dream.solve', 0, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', max_iter,
           '-num_phys_regions', 1, '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1,
           '-phys_region[0].ID[1]', 2, '-num_stim', 1, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'), '-stim[0].ptcl.start', 0.0] + greg
    env = dict(os.environ, OMP_NUM_THREADS=OMP)
    t0 = time.time()
    try:
        with open(os.path.join(d, 'openCARP.log'), 'w') as log:
            subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=cap_s, env=env)
    except subprocess.TimeoutExpired:
        return {'outcome': 'hit the 20-minute cap', 'wall_s': round(time.time() - t0, 1), 'max_iter': max_iter}
    except subprocess.CalledProcessError as ex:
        return {'outcome': f'failed ({ex.returncode})', 'wall_s': round(time.time() - t0, 1), 'max_iter': max_iter}
    act = igb_last(os.path.join(d, 'act.igb'))
    return {'outcome': 'ok', 'wall_s': round(time.time() - t0, 1), 'total_activation_ms': round(float(act.max()), 2),
            'unactivated_minus1': int((act < 0).sum()), 'max_iter': max_iter}


def setup(h):
    sp = S.SPEEDS[h]
    cal = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'calibration.json')))
    gf, gs, gn = ((cal[k]['gi'], cal[k]['ge']) for k in ('fibre', 'sheet', 'sheet_normal'))
    v = {k: 1000.0 * sp[a] for k, a in (('l', 'fibre'), ('t', 'sheet'), ('n', 'normal'))}       # mm/s
    greg = ['-num_gregions', 2]
    for r, tg in ((0, 1), (1, 2)):
        greg += [f'-gregion[{r}].num_IDs', 1, f'-gregion[{r}].ID[0]', tg,
                 f'-gregion[{r}].g_il', gf[0], f'-gregion[{r}].g_el', gf[1], f'-gregion[{r}].g_it', gs[0], f'-gregion[{r}].g_et', gs[1],
                 f'-gregion[{r}].g_in', gn[0], f'-gregion[{r}].g_en', gn[1],
                 f'-gregion[{r}].dream.vel_l', v['l'], f'-gregion[{r}].dream.vel_t', v['t'], f'-gregion[{r}].dream.vel_n', v['n']]
    return mesh51(h), greg, {s['id']: s for s in S.sites(h)}


def retry():
    """Each capped site once more, max_iter MAX_ITER_RETRY, output in <site>/retry/ (the first try's files stay)."""
    h = os.environ['HEART']
    mesh, greg, sites = setup(h)
    status_f = os.path.join(rundir(h), 'status.json')
    status = json.load(open(status_f))
    other = [sid for sid in SITES if 'cap' in status.get(sid, {}).get('outcome', '') and sid not in RETRY_SITES.get(h, [])]
    if other:
        sys.exit(f'{h}: {other} hit the cap in this batch; batch stopped, nothing retried (tell Alex)')
    for sid in RETRY_SITES.get(h, []):
        st = status.get(sid, {})
        if 'cap' not in st.get('outcome', '') or 'retry' in st:
            continue
        r = one_run(h, sid, os.path.join(rundir(h, sid), 'retry'), mesh, greg, sites, MAX_ITER_RETRY)
        st['retry'] = r
        if r['outcome'] == 'ok':
            st['outcome'], st['act_dir'] = 'ok (retry)', 'retry'
        elif 'cap' in r['outcome']:
            st['outcome'] = 'openCARP non-convergence (20-minute cap hit twice)'
        status[sid] = st
        json.dump(status, open(status_f, 'w'), indent=1)
        print(f'{h} {sid} retry: {r}', flush=True)


def run_nocap():
    """Alex 18 Oct 2026 12:59:10 UTC: "Nodal is good. Drop any caps or limits." No time cap: the unrun sites first
    (max_iter 1e9, as every other run), then each capped site once more (max_iter 2147483647, into <site>/retry/). A run
    that fails is recorded and the batch goes on."""
    h = os.environ['HEART']
    mesh, greg, sites = setup(h)
    status_f = os.path.join(rundir(h), 'status.json')
    status = json.load(open(status_f)) if os.path.exists(status_f) else {}
    unrun = [sid for sid in SITES if not status.get(sid, {}).get('outcome', '').startswith('ok') and 'cap' not in status.get(sid, {}).get('outcome', '')]
    capped = [sid for sid in SITES if 'cap' in status.get(sid, {}).get('outcome', '') and 'retry' not in status[sid]]
    for sid in unrun:
        status[sid] = one_run(h, sid, rundir(h, sid), mesh, greg, sites, MAX_ITER, cap_s=None) | {'cap': 'none (Alex 18 Oct 12:59 UTC)'}
        json.dump(status, open(status_f, 'w'), indent=1)
        print(f"{h} {sid}: {status[sid]}", flush=True)
    for sid in capped:
        st = status[sid]
        r = one_run(h, sid, os.path.join(rundir(h, sid), 'retry'), mesh, greg, sites, MAX_ITER_RETRY, cap_s=None) | {'cap': 'none (Alex 18 Oct 12:59 UTC)'}
        st['retry'] = r
        if r['outcome'] == 'ok':
            st['outcome'], st['act_dir'] = 'ok (retry)', 'retry'
        status[sid] = st
        json.dump(status, open(status_f, 'w'), indent=1)
        print(f'{h} {sid} retry: {r}', flush=True)


def compare():
    """python -B acceptance_c.py compare <metric> [hearts]: metric 'nodal' (S3 as briefed, 17 Oct factors) or 'element'
    (graph51.METRIC_ELEMENT, params/v51_graph_factors_element.json). Writes acceptance_c_<metric>_<date>.json; the
    17 Oct acceptance_c.json stays as it is."""
    metric = sys.argv[2]
    hearts = sys.argv[3:] or S.HEARTS
    out = {'gates': 'median |dt| <= 1 ms; p95 |dt| <= 2 % of openCARP total; total within +-2 %; no -1 in act', 'metric': metric,
           'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'hearts': {}}
    for h in hearts:
        t0 = time.time()
        lonf = S.lon51(h)
        tis = g.Tissue(h, lonf, metric=metric)
        fac = S.load_factors(h, lonf, metric)
        G = tis.graph(S.SPEEDS[h], fac)
        P, E = S.mesh(h)
        lon = g.read_lon(lonf)
        sites = {s['id']: s for s in S.sites(h)}
        status = json.load(open(os.path.join(rundir(h), 'status.json')))
        res, npass = {}, 0
        for sid in SITES:
            st = status.get(sid, {}).get('outcome', 'not run (batch stopped earlier)')
            if not st.startswith('ok'):
                res[sid] = {'openCARP_outcome': st, 'pass': None}
                print(h, sid, st, flush=True)
                continue
            sub = status[sid].get('act_dir', '')
            To = igb_last(os.path.join(rundir(h, sid), sub, 'act.igb'))
            Tg = g.Tissue.solve(G, int(sites[sid]['node']))
            ok = To >= 0
            dt = np.abs(Tg[ok] - To[ok])
            tot_o, tot_g = float(To[ok].max()), float(Tg.max())
            r = {'median_abs_dt_ms': round(float(np.median(dt)), 3), 'p95_abs_dt_ms': round(float(np.percentile(dt, 95)), 3),
                 'p95_pct_of_total': round(float(100 * np.percentile(dt, 95) / tot_o), 2), 'total_openCARP_ms': round(tot_o, 2),
                 'total_graph_ms': round(tot_g, 2), 'total_ratio': round(tot_g / tot_o, 4), 'mean_dt_graph_minus_openCARP_ms': round(float(np.mean(Tg[ok] - To[ok])), 3),
                 'unactivated_minus1': int((~ok).sum()), 'openCARP_wall_s': (status[sid].get('retry') if sub else status[sid])['wall_s'],
                 'openCARP_run': 'retry (max_iter 2147483647)' if sub else 'first try'}
            r['pass'] = bool(r['median_abs_dt_ms'] <= 1.0 and r['p95_pct_of_total'] <= 2.0 and abs(r['total_ratio'] - 1) <= 0.02 and r['unactivated_minus1'] == 0)
            npass += r['pass']
            so = S.cv_samples(P, E, lon, To); sg = S.cv_samples(P, E, lon, Tg)
            r['F01_measure_m_s'] = {a: {'openCARP': round(float(np.median(so[a])), 3) if len(so[a]) else None,
                                        'graph': round(float(np.median(sg[a])), 3) if len(sg[a]) else None} for a in S.AXES}
            res[sid] = r
            print(h, sid, {k: r[k] for k in ('median_abs_dt_ms', 'p95_pct_of_total', 'total_ratio', 'mean_dt_graph_minus_openCARP_ms', 'pass')}, flush=True)
        done = [r for r in res.values() if r['pass'] is not None]
        summ = {k: [round(min(r[k] for r in done), 4), round(max(r[k] for r in done), 4)] for k in
                ('median_abs_dt_ms', 'p95_pct_of_total', 'total_ratio', 'mean_dt_graph_minus_openCARP_ms')} if done else {}
        out['hearts'][h] = {'sites': res, 'sites_passing': f'{npass} / {len(done)} compared ({len(SITES)} planned)', 'range_over_sites': summ,
                            'factors': fac, 'speeds_m_s': S.SPEEDS[h], 'solver_keys': tis.keys, 'wall_s': round(time.time() - t0, 1)}
        print(h, out['hearts'][h]['sites_passing'], summ, flush=True)
    tag = f"{metric}_{time.strftime('%Y-%m-%d')}" + ('' if not sys.argv[3:] else '_' + '_'.join(hearts))
    json.dump(out, open(os.path.join(HERE, f'acceptance_c_{tag}.json'), 'w'), indent=1)
    print({h: v['sites_passing'] for h, v in out['hearts'].items()})


if __name__ == '__main__':
    {'run': run, 'retry': retry, 'run_nocap': run_nocap, 'compare': compare}[sys.argv[1]]()
