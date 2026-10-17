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
                           python -B analysis/v51_2026-10-15/04_build/acceptance_c.py compare             (all hearts)
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
    mesh = mesh51(h)
    sites = {s['id']: s for s in S.sites(h)}
    status_f = os.path.join(rundir(h), 'status.json')
    status = json.load(open(status_f)) if os.path.exists(status_f) else {}
    for sid in SITES:
        if status.get(sid, {}).get('outcome') == 'ok':
            continue
        d = rundir(h, sid); os.makedirs(d, exist_ok=True)
        g_vtx = os.path.join(d, 'stim.vtx')
        with open(g_vtx, 'w') as fh:
            fh.write(f"1\nintra\n{int(sites[sid]['node'])}\n")
        cmd = ['openCARP', '-meshname', mesh, '-simID', d, '-dream.solve', 0, '-dream.fim.tol', 0.001, '-dream.fim.max_iter', 1000000000,
               '-num_phys_regions', 1, '-phys_region[0].ptype', 2, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1,
               '-phys_region[0].ID[1]', 2, '-num_stim', 1, '-stim[0].elec.vtx_file', os.path.join(d, 'stim'), '-stim[0].ptcl.start', 0.0] + greg
        env = dict(os.environ, OMP_NUM_THREADS=OMP)
        t0 = time.time()
        try:
            with open(os.path.join(d, 'openCARP.log'), 'w') as log:
                subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=CAP_S, env=env)
        except subprocess.TimeoutExpired:
            status[sid] = {'outcome': 'hit the 20-minute cap', 'wall_s': round(time.time() - t0, 1)}
            json.dump(status, open(status_f, 'w'), indent=1)
            print(f'{h} {sid}: HIT THE 20-MINUTE CAP; batch stopped', flush=True)
            sys.exit(3)
        except subprocess.CalledProcessError as ex:
            status[sid] = {'outcome': f'failed ({ex.returncode})', 'wall_s': round(time.time() - t0, 1)}
            json.dump(status, open(status_f, 'w'), indent=1)
            print(f'{h} {sid}: openCARP failed ({ex.returncode}); batch stopped', flush=True)
            sys.exit(4)
        act = igb_last(os.path.join(d, 'act.igb'))
        status[sid] = {'outcome': 'ok', 'wall_s': round(time.time() - t0, 1), 'total_activation_ms': round(float(act.max()), 2),
                       'unactivated_minus1': int((act < 0).sum())}
        json.dump(status, open(status_f, 'w'), indent=1)
        print(f"{h} {sid}: {status[sid]['wall_s']} s, total {status[sid]['total_activation_ms']} ms, unactivated {status[sid]['unactivated_minus1']}", flush=True)


def compare():
    hearts = sys.argv[2:] or S.HEARTS
    out = {'gates': 'median |dt| <= 1 ms; p95 |dt| <= 2 % of openCARP total; total within +-2 %; no -1 in act', 'hearts': {}}
    for h in hearts:
        lonf = S.lon51(h)
        tis = g.Tissue(h, lonf)
        G = tis.graph(S.SPEEDS[h], S.load_factors(h, lonf))
        P, E = S.mesh(h)
        lon = g.read_lon(lonf)
        sites = {s['id']: s for s in S.sites(h)}
        status = json.load(open(os.path.join(rundir(h), 'status.json')))
        res, npass = {}, 0
        for sid in SITES:
            st = status.get(sid, {}).get('outcome', 'not run (batch stopped earlier)')
            if st != 'ok':
                res[sid] = {'openCARP_outcome': st, 'pass': None}
                print(h, sid, st, flush=True)
                continue
            To = igb_last(os.path.join(rundir(h, sid), 'act.igb'))
            Tg = g.Tissue.solve(G, int(sites[sid]['node']))
            ok = To >= 0
            dt = np.abs(Tg[ok] - To[ok])
            tot_o, tot_g = float(To[ok].max()), float(Tg.max())
            r = {'median_abs_dt_ms': round(float(np.median(dt)), 3), 'p95_abs_dt_ms': round(float(np.percentile(dt, 95)), 3),
                 'p95_pct_of_total': round(float(100 * np.percentile(dt, 95) / tot_o), 2), 'total_openCARP_ms': round(tot_o, 2),
                 'total_graph_ms': round(tot_g, 2), 'total_ratio': round(tot_g / tot_o, 4), 'mean_dt_graph_minus_openCARP_ms': round(float(np.mean(Tg[ok] - To[ok])), 3),
                 'unactivated_minus1': int((~ok).sum()), 'openCARP_wall_s': status[sid]['wall_s']}
            r['pass'] = bool(r['median_abs_dt_ms'] <= 1.0 and r['p95_pct_of_total'] <= 2.0 and abs(r['total_ratio'] - 1) <= 0.02 and r['unactivated_minus1'] == 0)
            npass += r['pass']
            so = S.cv_samples(P, E, lon, To); sg = S.cv_samples(P, E, lon, Tg)
            r['F01_measure_m_s'] = {a: {'openCARP': round(float(np.median(so[a])), 3) if len(so[a]) else None,
                                        'graph': round(float(np.median(sg[a])), 3) if len(sg[a]) else None} for a in S.AXES}
            res[sid] = r
            print(h, sid, {k: r[k] for k in ('median_abs_dt_ms', 'p95_pct_of_total', 'total_ratio', 'unactivated_minus1', 'pass')}, flush=True)
        nrun = sum(1 for r in res.values() if r['pass'] is not None)
        out['hearts'][h] = {'sites': res, 'sites_passing': f'{npass} / {nrun} compared ({len(SITES)} planned)', 'factors': S.load_factors(h, lonf), 'speeds_m_s': S.SPEEDS[h]}
    json.dump(out, open(os.path.join(HERE, 'acceptance_c.json' if not sys.argv[2:] else f"acceptance_c_{'_'.join(hearts)}.json"), 'w'), indent=1)
    print({h: v['sites_passing'] for h, v in out['hearts'].items()})


if __name__ == '__main__':
    {'run': run, 'compare': compare}[sys.argv[1]]()
