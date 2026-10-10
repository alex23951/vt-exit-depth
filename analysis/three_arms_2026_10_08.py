#!/usr/bin/env python
"""
Control heart Y5HYEDL4, the same 144 v5 sites under three conduction models (pure eikonal, ecg_depth_criteria
0.3.0, both onset modes):
  layer    frozen 2.0 m/s fast endocardial layer     analysis/grids_2026-10-07/new_Y5HYEDL4.csv (jobs 2 + v3 runs)
  network  His-Purkinje network (14_purkinje.py)     analysis/grids_2026-10-07/purk_Y5HYEDL4.csv (job 8)
  nolayer  no fast conduction at all                 analysis/grids_2026-10-07/nofast_Y5HYEDL4.csv (job 1)
Prints the tables for the results note (medians; one heart, descriptive only) and writes
analysis/three_arms_2026-10-08/sites.csv (one row per site and arm, key measurements).
"""

import csv
import os
import statistics as st

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
G = os.path.join(REPO, 'analysis', 'grids_2026-10-07')
OUT = os.path.join(REPO, 'analysis', 'three_arms_2026-10-08')
ARMS = {'layer': 'new_Y5HYEDL4.csv', 'network': 'purk_Y5HYEDL4.csv', 'nolayer': 'nofast_Y5HYEDL4.csv'}
GROUP = {'lv_free_wall': 'LV free wall', 'lv_septum': 'LV septum', 'rv_free_wall': 'RV free wall', 'rvot': 'RVOT',
         'aortic_cusp': 'Aortic cusp', 'lv_summit': 'LV summit', 'lv_vein_course': 'LV vein course'}
MEAS = ['qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels']
CALLS = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055']


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def med(xs, nd=3):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), nd) if xs else None


def auc(pos, neg):
    pos, neg = [x for x in pos if x is not None], [x for x in neg if x is not None]
    if not pos or not neg:
        return None
    return round(sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg)), 2)


def dep(r):
    return int(round(float(r['depth_target']) * 100))


def main():
    D = {a: {r['id']: r for r in csv.DictReader(open(os.path.join(G, fn)))} for a, fn in ARMS.items()}
    ids = [i for i in D['nolayer'] if all(i in D[a] and D[a][i]['node'] == D['nolayer'][i]['node'] for a in ARMS)]
    print(f'sites in all three arms: {len(ids)}')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'sites.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        cols = [f'{m}_{k}' for m in ('true', 'detected') for k in MEAS]
        w.writerow(['id', 'name', 'group', 'depth_target', 'arm'] + cols)
        for i in ids:
            for a in ARMS:
                r = D[a][i]
                w.writerow([i, r['name'], GROUP[r['family']], r['depth_target'], a] + [r[c] for c in cols])

    for mode in ('true', 'detected'):
        print(f'\n## {mode} onset, medians layer / network / no layer, by group')
        print('group | n | QRS | pseudo-delta | IDT V2 | shortest RS | MDI')
        for g in GROUP.values():
            I = [i for i in ids if GROUP[D['nolayer'][i]['family']] == g]
            cells = [' / '.join(str(med([f(D[a][i][f'{mode}_{k}']) for i in I], 2 if k == 'mdi_daniels' else 1)) for a in ARMS) for k in MEAS]
            print(f'{g} | {len(I)} | ' + ' | '.join(cells))

    print('\n## LV free wall, same position 10 % -> 90 % (true onset): median change (n up / n), AUC 90 vs 10')
    for a in ARMS:
        fw = [D[a][i] for i in ids if D[a][i]['family'] == 'lv_free_wall']
        pos = sorted({(r['level_z'], r['position']) for r in fw})
        out = []
        for k in MEAS:
            ch = []
            for p in pos:
                x = {dep(r): f(r[f'true_{k}']) for r in fw if (r['level_z'], r['position']) == p}
                if x.get(10) is not None and x.get(90) is not None:
                    ch.append(x[90] - x[10])
            out.append(f"{k} {med(ch, 3)} ({sum(c > 0 for c in ch)}/{len(ch)}, AUC {auc([f(r[f'true_{k}']) for r in fw if dep(r) == 90], [f(r[f'true_{k}']) for r in fw if dep(r) == 10])})")
        q10 = med([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 10], 1)
        q90 = med([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 90], 1)
        print(f'{a}: ' + '; '.join(out) + f'; QRS {q10} -> {q90} ({round(100 * (q90 - q10) / q10, 1)} %)')

    print('\n## All sites with a depth truth (cusps out): AUC 90 % vs 10 %, true / detected onset')
    for a in ARMS:
        R = [D[a][i] for i in ids if D[a][i]['epi_endo_truth'] == 'True']
        print(a + ': ' + '; '.join(f"{k} {auc([f(r['true_' + k]) for r in R if dep(r) == 90], [f(r['true_' + k]) for r in R if dep(r) == 10])} / "
                                   f"{auc([f(r['detected_' + k]) for r in R if dep(r) == 90], [f(r['detected_' + k]) for r in R if dep(r) == 10])}" for k in MEAS))

    print('\n## Daniels order, precordial MDI medians (Daniels 2006: LV epicardial perivascular 0.61 > ASOV 0.46 > RVOT 0.40 > LV endo 0.34)')
    for mode in ('true', 'detected'):
        for a in ARMS:
            m = lambda sel: med([f(D[a][i][f'{mode}_mdi_daniels']) for i in ids if sel(D[a][i])], 2)
            print(f"{mode} {a}: summit 90 % {m(lambda r: r['family'] == 'lv_summit' and dep(r) == 90)}, vein course 90 % "
                  f"{m(lambda r: r['family'] == 'lv_vein_course' and dep(r) == 90)}, cusp {m(lambda r: r['family'] == 'aortic_cusp')}, "
                  f"RVOT {m(lambda r: r['family'] == 'rvot')}, LV endo 10 % {m(lambda r: r['family'] in ('lv_free_wall', 'lv_septum') and dep(r) == 10)}")

    print('\n## Absolute QRS (decision 7: median at LV summit + aortic cusp within 132-193 ms; idiopathic VAs 147-175 ms)')
    for mode in ('true', 'detected'):
        print(mode + ': ' + '; '.join(f"{a} {med([f(D[a][i][f'{mode}_qrs_duration_ms']) for i in ids if D[a][i]['family'] in ('lv_summit', 'aortic_cusp')], 1)}" for a in ARMS))

    print('\n## Epicardial calls, true / detected onset, sites with a depth truth, by target depth')
    for d in (10, 50, 75, 90):
        cells = []
        for c in CALLS:
            cells.append(c + ' ' + ' | '.join(f"{sum(D[a][i]['true_' + c] == 'True' for i in ids if dep(D[a][i]) == d and D[a][i]['epi_endo_truth'] == 'True')}/"
                                              f"{sum(D[a][i]['detected_' + c] == 'True' for i in ids if dep(D[a][i]) == d and D[a][i]['epi_endo_truth'] == 'True')}" for a in ARMS))
        print(f"{d} % (n {sum(dep(D['nolayer'][i]) == d and D['nolayer'][i]['epi_endo_truth'] == 'True' for i in ids)}; layer | network | no layer): " + '; '.join(cells))


if __name__ == '__main__':
    main()
