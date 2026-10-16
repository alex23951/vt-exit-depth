"""Step 3 (v5.1 brief, decision D; 16 Oct 2026): stimulus-size and retrograde-delay check on v5. Reported only, never
used to retune; v5.1 keeps the 1.5 mm ball and the 2 ms retrograde delay.

Solver: the guarded v5 copy (analysis/v51_2026-10-15/01_backup/v5_grid_guarded.py, Heart('E'), junction antegrade 4 ms
as v5_adopted.py:127), with solve_ext() = Heart.solve() plus two switches that default to v5:
  stim   'ball' (v5: every node within 1.5 mm of the site node, t = 0) or 'node' (the site node only)
  d_ret  muscle -> Purkinje delay, 2.0 ms (v5) or 4.0 ms (Arm R; top of Behradfar 2014's physiological 2-4 ms)
The graph cache (runs/v51_2026-10-15/cache) holds only the tissue graph; neither switch enters it.
Beats: Arm S (stim 'node'): RV free wall 10 % and 90 % (3 hearts) + Y5HYEDL4 aortic cusps (all depths); Arm R (d_ret 4):
LV free wall 10 % and 90 % (3 hearts); repro: the first RV free-wall 10 % site of each heart with the defaults, which must
equal the saved 14 Oct beat (analysis/audit_addendum_2026-10-14/maps) bit-exactly, as must solve_ext() vs Heart.solve().
Stages (repo root, venv):
  HEART=<H> python -B analysis/v51_2026-10-15/03_stimulus_check/stim_check.py run   -> runs/v51_2026-10-15/03_stimulus_check/<arm>/<H>/
  python -B analysis/v51_2026-10-15/03_stimulus_check/stim_check.py score           -> this folder (beats.csv, report.md, report.json)
"""
import importlib.util
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUTR = os.path.join(REPO, 'runs', 'v51_2026-10-15', '03_stimulus_check')
MAPS = os.path.join(REPO, 'analysis', 'audit_addendum_2026-10-14', 'maps')
V5A = os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '02_measure_040'))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def sites(h):
    return json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))


def plan(h):
    S = sites(h)
    rv = [s for s in S if s['family'] == 'rv_free_wall' and s['depth_target'] in (0.1, 0.9)]
    lv = [s for s in S if s['family'] == 'lv_free_wall' and s['depth_target'] in (0.1, 0.9)]
    cusp = [s for s in S if s['family'] == 'aortic_cusp'] if h == 'Y5HYEDL4' else []
    return {'repro': rv[:1], 'S': rv + cusp, 'R': lv}


def solve_ext(H, site_node=None, nonet=False, stim='ball', d_ret=2.0):
    """Heart.solve() of v5_grid_guarded.py with the two switches; returns times of all N + M nodes (myocardium, network)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    N, e, w = H.N, H.e, H.w
    rows, cols, data = [e[:, 0], e[:, 1]], [e[:, 1], e[:, 0]], [w, w]
    if nonet:
        M = 0
    else:
        net = H.net; M = len(net['nodes'])
        gn = H.PK.net_graph(net, H.pts).tocoo(); kk = (gn.row < M) & (gn.col < M)
        m = net['nodes'][net['pmj']]; j = N + net['pmj']
        rows += [N + gn.row[kk], m, j]; cols += [N + gn.col[kk], j, m]
        data += [gn.data[kk], np.full(len(m), d_ret), H.d_ant]
    src = N + M
    if site_node is None:
        rows.append(np.array([src])); cols.append(np.array([N + int(H.net['his'])])); data.append(np.array([1e-6]))
    else:
        if stim == 'ball':
            pu = H.pts * 1e3
            s = np.where(np.linalg.norm(pu - pu[site_node], axis=1) < 1500)[0]
        elif stim == 'node':
            s = np.array([int(site_node)])
        else:
            raise ValueError(stim)
        rows.append(np.full(len(s), src)); cols.append(s); data.append(np.full(len(s), 1e-6))
    G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
    return dijkstra(G, directed=True, indices=src) - 1e-6


def run():
    h = os.environ['HEART']
    print(f'run {h}: writes only {OUTR}/<arm>/{h}', flush=True)
    t0 = time.time()
    VG = module('vgg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'v5_grid_guarded.py'))
    BT = module('bt', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'beats.py'))
    H = VG.Heart('E', h, expect_fibre_sha256=BT.manifest_sha(f'analysis/v5_grid_2026-10-13/fibres_E/{h}/bivF.lon'))
    H.d_ant = np.full(len(H.net['pmj']), 4.0)
    H.W = np.load(os.path.join(V5A, f'ecgW_v5_{h}.npz'))['W'].astype(float)
    print(f'  setup {time.time() - t0:.0f} s', flush=True)
    pmj_muscle = H.net['nodes'][H.net['pmj']]
    arms = {'repro': dict(stim='ball', d_ret=2.0), 'S': dict(stim='node', d_ret=2.0), 'R': dict(stim='ball', d_ret=4.0)}
    for arm, beats in plan(h).items():
        d = os.path.join(OUTR, arm, h); os.makedirs(d, exist_ok=True)
        info = []
        for s in beats:
            t1 = time.time()
            full = solve_ext(H, int(s['node']), **arms[arm])
            T = full[:H.N]
            _, ecg = H.ecg(T)
            np.save(os.path.join(d, f"{s['id']}.T.npy"), T.astype(np.float32))
            np.save(os.path.join(d, f"{s['id']}.ecg.npy"), ecg.astype(np.float32))
            r = {'id': s['id'], 'arm': arm, **arms[arm], 'total_activation_ms': float(T.max()), 'unactivated': int(np.isinf(T).sum()),
                 'first_junction_muscle_ms': float(T[pmj_muscle].min()), 'network_first_ms': float(full[H.N:-1].min()), 'solve_s': round(time.time() - t1, 1)}
            if arm == 'repro':
                ref_T = np.load(os.path.join(MAPS, h, f"{s['id']}.T.npy")); ref_E = np.load(os.path.join(MAPS, h, f"{s['id']}.ecg.npy"))
                r['repro_T_equal_14oct'] = bool(np.array_equal(T.astype(np.float32), ref_T))
                r['repro_ecg_equal_14oct'] = bool(np.array_equal(ecg.astype(np.float32), ref_E))
                r['solve_ext_equals_Heart_solve'] = bool(np.array_equal(T, H.solve(int(s['node']))))
                r['network_first_equals_junction_plus_2ms'] = bool(math.isclose(r['network_first_ms'], r['first_junction_muscle_ms'] + 2.0, abs_tol=1e-9))
            info.append(r)
            print(f"  {arm} {s['id']}: {r['solve_s']} s, total {r['total_activation_ms']:.1f} ms", flush=True)
        json.dump(info, open(os.path.join(d, 'beats.json'), 'w'), indent=1)
    print(f'run {h}: {time.time() - t0:.0f} s', flush=True)


def verify():
    """Fresh solves of three beats per heart (repro, one Arm S, one Arm R): the first network activation equals the
    earliest junction muscle time + the retrograde delay, and the beats equal the saved maps."""
    h = os.environ['HEART']
    VG = module('vgg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'v5_grid_guarded.py'))
    BT = module('bt', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'beats.py'))
    H = VG.Heart('E', h, expect_fibre_sha256=BT.manifest_sha(f'analysis/v5_grid_2026-10-13/fibres_E/{h}/bivF.lon'))
    H.d_ant = np.full(len(H.net['pmj']), 4.0)
    pmj_muscle = H.net['nodes'][H.net['pmj']]
    P = plan(h); out = []
    for arm, s, kw in (('repro', P['repro'][0], dict(stim='ball', d_ret=2.0)), ('S', P['S'][1], dict(stim='node', d_ret=2.0)),
                       ('R', P['R'][0], dict(stim='ball', d_ret=4.0))):
        full = solve_ext(H, int(s['node']), **kw)
        T = full[:H.N]; netT = full[H.N:-1]
        out.append({'heart': h, 'arm': arm, 'site': s['id'], 'network_first_ms': float(netT.min()),
                    'junction_plus_delay_ms': float(T[pmj_muscle].min()) + kw['d_ret'],
                    'equal': bool(math.isclose(float(netT.min()), float(T[pmj_muscle].min()) + kw['d_ret'], abs_tol=1e-9)),
                    'map_equals_saved': bool(np.array_equal(T.astype(np.float32), np.load(os.path.join(OUTR, arm, h, f"{s['id']}.T.npy"))))})
        print(out[-1], flush=True)
    json.dump(out, open(os.path.join(OUTR, f'verify_{h}.json'), 'w'), indent=1)


# ------------------------------------------------------------------ scoring and report
def measure_all(R, ecg, last, family):
    """14 Oct conventions (regression.py prep): true mode and stimulus onset (clean); detected onset + 10 uV plan noise,
    seeds 0-9, median (cusp sites, for the spontaneous Daniels / absolute-QRS comparators). Both packages."""
    out = {}
    for pkg_name, pkg in (('030', R.edc030), ('040', R.edc)):
        for mode in ('true', 'stim'):
            m = R.run_one(pkg, R.prep(ecg), mode, last, None)
            for k in ('m.qrs_duration_ms', 'm.qrs_duration_any_lead_ms', 'm.pseudo_delta_ms', 'm.idt_v2_ms', 'm.srs_ms', 'm.mdi_daniels'):
                out[f'{pkg_name}_{mode}_{k[2:]}'] = m.get(k, np.nan)
        if family == 'aortic_cusp':
            vals = [R.run_one(pkg, R.prep(ecg, 10, k), 'detected', last, None) for k in range(10)]
            for k in ('m.qrs_duration_any_lead_ms', 'm.mdi_daniels'):
                out[f'{pkg_name}_det10_{k[2:]}'] = float(np.nanmedian([v.get(k, np.nan) for v in vals]))
    return out


def score():
    import nanstats as ns
    R = module('reg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '02_measure_040', 'regression.py'))
    rows = []
    for h in HEARTS:
        meta = {s['id']: s for s in sites(h)}
        for arm, beats in plan(h).items():
            info = {r['id']: r for r in json.load(open(os.path.join(OUTR, arm, h, 'beats.json')))}
            for s in beats:
                sid = s['id']
                new_T = np.load(os.path.join(OUTR, arm, h, f'{sid}.T.npy')); new_E = np.load(os.path.join(OUTR, arm, h, f'{sid}.ecg.npy'))
                v5_T = np.load(os.path.join(MAPS, h, f'{sid}.T.npy')); v5_E = np.load(os.path.join(MAPS, h, f'{sid}.ecg.npy'))
                pm = np.load(os.path.join(REPO, 'data', 'biv', h, 'purkinje', 'network.npz'))
                pmj_muscle = pm['nodes'][pm['pmj']]
                base = {'heart': h, 'arm': arm, 'site': sid, 'family': s['family'], 'depth': s['depth_target'], 'position': s.get('position'),
                        'level_z': s.get('level_z'), 'T_differs_from_v5': not np.array_equal(new_T, v5_T),
                        'max_abs_dT_ms': float(np.max(np.abs(new_T.astype(float) - v5_T.astype(float)))),
                        'new_total_ms': info[sid]['total_activation_ms'], 'v5_total_ms': float(v5_T.max()),
                        # network first active = earliest junction muscle time + retrograde delay (checked by the verify stage);
                        # the network_first_ms of the run's beats.json is not used: it included the source node (fixed 16 Oct)
                        'new_network_first_ms': float(new_T[pmj_muscle].astype(float).min()) + info[sid]['d_ret'],
                        'v5_network_first_ms': float(v5_T[pmj_muscle].astype(float).min()) + 2.0}
                for tag, E, T in (('new', new_E, new_T), ('v5', v5_E, v5_T)):
                    for k, v in measure_all(R, E.astype(float), float(T.max()), s['family']).items():
                        base[f'{tag}_{k}'] = v
                rows.append(base)
        print(h, 'scored', flush=True)
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'beats.csv'), index=False)
    # the two packages agree on these measures (Step 2.3); check here too
    pk = [c for c in D.columns if c.startswith('new_030_') or c.startswith('v5_030_')]
    same = all(np.array_equal(D[c].to_numpy(float), D[c.replace('_030_', '_040_')].to_numpy(float), equal_nan=True) for c in pk)
    report(D, ns, same)


def pairs(D, arm, fam, col):
    x = D[(D.arm == arm) & (D.family == fam)]
    a = x[x.depth == 0.9].set_index(['position', 'level_z'])[col]; b = x[x.depth == 0.1].set_index(['position', 'level_z'])[col]
    j = pd.concat([a.rename('a'), b.rename('b')], axis=1, join='inner')
    return j.a.tolist(), j.b.tolist()


def report(D, ns, same):
    J, L = {}, []
    conv = {'true mode (13 Oct)': ('true', 'qrs_duration_ms'), '14 Oct pace-map convention (stimulus onset, QRS any lead)': ('stim', 'qrs_duration_any_lead_ms')}
    rep = D[D.arm == 'repro']
    J['repro'] = {'v5 defaults equal the saved 14 Oct beats (T and ECG)': bool((~rep.T_differs_from_v5).all()), 'beats': len(rep)}
    J['packages 0.3.0 and 0.4.0 identical on these measures'] = bool(same)
    J['unactivated nodes'] = 0  # filled below from beats.json
    un = 0
    for h in HEARTS:
        for arm in ('repro', 'S', 'R'):
            un += sum(r['unactivated'] for r in json.load(open(os.path.join(OUTR, arm, h, 'beats.json'))))
            if arm == 'repro':
                J[f'repro {h}'] = {k: v for k, v in json.load(open(os.path.join(OUTR, arm, h, 'beats.json')))[0].items() if k.startswith(('repro', 'solve_ext', 'network_first_equals'))}
    J['unactivated nodes'] = un
    rd = lambda v, n=1: None if v is None else round(v, n)
    # ---------------- Arm S
    S = {}
    for cname, (mode, qcol) in conv.items():
        for h in HEARTS:
            x = D[D.heart == h]
            cell = {}
            for tag in ('v5', 'new'):
                a, b = pairs(x, 'S', 'rv_free_wall', f'{tag}_040_{mode}_{qcol}')
                rel = [100 * (p - q) / q for p, q in zip(*ns.paired(a, b)[:2])]
                cell[f'{tag} RV median pair %'] = rd(ns.scored_median(rel)[0])
            la, lb = pairs(x, 'R', 'lv_free_wall', f'v5_040_{mode}_{qcol}')
            lv = ns.scored_median([100 * (p - q) / q for p, q in zip(*ns.paired(la, lb)[:2])])[0]
            cell['LV median pair % (v5)'] = rd(lv)
            cell['Bazan 2006 gate (-1.9 to 6.6, below LV): v5 / Arm S'] = ' / '.join(
                str(bool(-1.9 <= cell[f'{t} RV median pair %'] <= 6.6 and cell[f'{t} RV median pair %'] < lv)) for t in ('v5', 'new'))
            for k, nm in (('qrs', qcol), ('pdw', 'pseudo_delta_ms'), ('mdi', 'mdi_daniels'), ('idt', 'idt_v2_ms'), ('rs', 'srs_ms')):
                for tag in ('v5', 'new'):
                    a, b = pairs(x, 'S', 'rv_free_wall', f'{tag}_040_{mode}_{nm}')
                    pa, pb, n, dr = ns.paired(a, b)
                    dd = [p - q for p, q in zip(pa, pb)]
                    cell[f'RV 90-10 {k} median diff {tag}'] = f'{ns.scored_median(dd)[0]:+.3f}' if k == 'mdi' else f'{ns.scored_median(dd)[0]:+.1f}'
                    if dr:
                        cell[f'RV 90-10 {k} median diff {tag}'] += f' ({dr} pairs unscorable)'
            S[f'{cname} | {h}'] = cell
    c = D[(D.arm == 'S') & (D.family == 'aortic_cusp')]
    cusp = {}
    for tag in ('v5', 'new'):
        cusp[tag] = {'true QRS median': rd(c[f'{tag}_040_true_qrs_duration_ms'].median()), 'true MDI median': rd(c[f'{tag}_040_true_mdi_daniels'].median(), 3),
                     'stim QRS-any median': rd(c[f'{tag}_040_stim_qrs_duration_any_lead_ms'].median()),
                     'detected 10 uV QRS-any median (median of 10 seeds per site)': rd(c[f'{tag}_040_det10_qrs_duration_any_lead_ms'].median()),
                     'detected 10 uV MDI median (Daniels, 14 Oct convention)': rd(c[f'{tag}_040_det10_mdi_daniels'].median(), 3)}
    # Daniels order with the cusp median replaced (other families: v5 values of record, 13 Oct true / 14 Oct convention)
    other = {'true (13 Oct)': {'summit90': 0.542, 'vein90': 0.458, 'RVOT': 0.679, 'LVendo10': 0.348},
             '14 Oct convention': {'summit90': 0.621, 'vein90': 0.497, 'RVOT': 0.689, 'LVendo10': 0.360}}
    dan = {}
    for cname, key in (('true (13 Oct)', 'true MDI median'), ('14 Oct convention', 'detected 10 uV MDI median (Daniels, 14 Oct convention)')):
        for tag in ('v5', 'new'):
            o = other[cname]; cu = cusp[tag][key]
            ok = min(o['summit90'], o['vein90'], cu) > o['RVOT'] > o['LVendo10']
            dan[f'{cname} | {tag}'] = f"summit90 {o['summit90']}, vein90 {o['vein90']}, cusp {cu}, RVOT {o['RVOT']}, LVendo10 {o['LVendo10']}: {'PASS' if ok else 'FAIL'}"
    J['Arm S (single-node stimulus)'] = {'RV free wall': S, 'Y5HYEDL4 cusps': cusp, 'Daniels order with Arm S cusps': dan}
    # ---------------- Arm R
    RR = {}
    for cname, (mode, qcol) in conv.items():
        for h in HEARTS:
            x = D[D.heart == h]
            cell = {}
            for tag in ('v5', 'new'):
                a, b = pairs(x, 'R', 'lv_free_wall', f'{tag}_040_{mode}_{qcol}')
                r_, n, _ = ns.ratio_of_means(a, b)
                ci = ns.bootstrap_ratio_of_means(a, b)
                cell[f'relative QRS ratio of means {tag}'] = f'{r_:.4f} (CI {ci[0]:.3f}-{ci[1]:.3f}; {"PASS" if 206 / 191 <= r_ <= 219 / 189 else "FAIL"})'
                for k, nm in (('pdw', 'pseudo_delta_ms'), ('mdi', 'mdi_daniels'), ('idt', 'idt_v2_ms'), ('rs', 'srs_ms')):
                    a, b = pairs(x, 'R', 'lv_free_wall', f'{tag}_040_{mode}_{nm}')
                    up, n, dr = ns.up_count(b, a)                  # 10 % -> 90 %: up when the 90 % value is higher
                    au = ns.auc_scored(a, b)['auc']
                    cell[f'{k} up {tag}'] = f'{up}/{n}' + (f' ({dr} unscorable)' if dr else '')
                    cell[f'{k} AUC {tag}'] = rd(au, 2)
            RR[f'{cname} | {h}'] = cell
    lv10 = D[(D.arm == 'R') & (D.depth == 0.1)]
    ent = {h: {'v5 network first (median, range) ms': f"{g.v5_network_first_ms.median():.1f} ({g.v5_network_first_ms.min():.1f}-{g.v5_network_first_ms.max():.1f})",
               'Arm R network first (median, range) ms': f"{g.new_network_first_ms.median():.1f} ({g.new_network_first_ms.min():.1f}-{g.new_network_first_ms.max():.1f})"}
           for h, g in lv10.groupby('heart')}
    ar = D[D.arm == 'R']
    J['Arm R (retrograde 4 ms)'] = {'LV free wall': RR, 'first network entry at 10 % sites': ent,
                                    'beats differing from v5 (activation map)': f'{int(ar.T_differs_from_v5.sum())} / {len(ar)}',
                                    'max |dT| median / max ms': f'{ar.max_abs_dT_ms.median():.2f} / {ar.max_abs_dT_ms.max():.2f}'}
    sa = D[D.arm == 'S']
    J['Arm S beats differing from v5'] = f'{int(sa.T_differs_from_v5.sum())} / {len(sa)}'
    json.dump(J, open(os.path.join(HERE, 'report.json'), 'w'), indent=1, default=str)
    L.append('# Step 3: stimulus-size and retrograde-delay check on v5 (decision D; reported only, no verdict changes)\n')
    L.append(f"Reproduction (v5 defaults vs the saved 14 Oct beats, 3 hearts): {J['repro']}; unactivated nodes in all beats: {un}; "
             f"0.3.0 and 0.4.0 identical on these measures: {same}.\n")
    for sec in ('Arm S (single-node stimulus)', 'Arm R (retrograde 4 ms)'):
        L.append(f'## {sec}\n')
        L.append('```'); L.append(json.dumps(J[sec], indent=1, default=str)); L.append('```\n')
    L.append(f"Arm S beats differing from v5: {J['Arm S beats differing from v5']}\n")
    open(os.path.join(HERE, 'report.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    {'run': run, 'verify': verify, 'score': score}[sys.argv[1]]()
