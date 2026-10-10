#!/usr/bin/env python
"""
No-fast-layer control (job 1, 7 Oct 2026) against the normal-layer grid, control heart Y5HYEDL4.

Inputs (both scored with ecg_depth_criteria 0.3.0, both onset modes):
  analysis/grids_2026-10-07/nofast_Y5HYEDL4.csv  144 v5 sites, fast layer given myocardial speeds
  analysis/grids_2026-10-07/new_Y5HYEDL4.csv     normal layer: 93 unchanged v3 sites + new v5 sites run so far
Pairs = same site id and node in both. Writes analysis/nofast_vs_normal_2026-10-07/pairs.csv and
prints the tables used in the results note (medians; one heart, descriptive only).
"""

import csv
import os
import statistics as st

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
G = os.path.join(REPO, 'analysis', 'grids_2026-10-07')
OUT = os.path.join(REPO, 'analysis', 'nofast_vs_normal_2026-10-07')
GROUP = {'lv_free_wall': 'LV free wall', 'lv_septum': 'LV septum', 'rv_free_wall': 'RV free wall', 'rvot': 'RVOT',
         'aortic_cusp': 'Aortic cusp', 'lv_summit': 'LV summit', 'lv_vein_course': 'LV vein course'}
MEAS = ['qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels']
CALLS = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055']


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None


def auc(pos, neg):
    pos, neg = [x for x in pos if x is not None], [x for x in neg if x is not None]
    if not pos or not neg:
        return None
    s = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return round(s / (len(pos) * len(neg)), 2)


def load(name):
    return {r['id']: r for r in csv.DictReader(open(os.path.join(G, name)))}


def dep(r):
    return int(round(float(r['depth_target']) * 100))


def main():
    nf, nl = load('nofast_Y5HYEDL4.csv'), load('new_Y5HYEDL4.csv')
    pairs = [(i, nl[i], nf[i]) for i in nf if i in nl and nl[i]['node'] == nf[i]['node']]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'pairs.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        cols = [f'{m}_{k}' for m in ('true', 'detected') for k in MEAS]
        w.writerow(['id', 'name', 'group', 'depth_target'] + [f'normal_{c}' for c in cols] + [f'nofast_{c}' for c in cols])
        for i, a, b in pairs:
            w.writerow([i, b['name'], GROUP[b['family']], b['depth_target']] + [a[c] for c in cols] + [b[c] for c in cols])
    print(f'pairs: {len(pairs)} of {len(nf)} no-fast-layer sites')

    for mode in ('true', 'detected'):
        print(f'\n## {mode} onset: medians normal -> no fast layer (paired sites), by group')
        print('group | n | QRS | pseudo-delta | IDT V2 | shortest RS | MDI (Daniels)')
        for g in GROUP.values():
            P = [(a, b) for _, a, b in pairs if GROUP[b['family']] == g]
            if not P:
                continue
            cells = [f"{med([f(a[f'{mode}_{k}']) for a, _ in P])} -> {med([f(b[f'{mode}_{k}']) for _, b in P])}" for k in MEAS]
            print(f'{g} | {len(P)} | ' + ' | '.join(cells))

    for mode in ('true', 'detected'):
        print(f'\n## {mode} onset: no-fast-layer medians, ALL 144 sites, by group and depth (QRS / MDI)')
        for g in GROUP.values():
            row = []
            for d in (10, 50, 75, 90):
                R = [r for r in nf.values() if GROUP[r['family']] == g and dep(r) == d]
                row.append(f"{d}%: {med([f(r[f'{mode}_qrs_duration_ms']) for r in R])} / {med([f(r[f'{mode}_mdi_daniels']) for r in R])}")
            print(f'{g}: ' + '; '.join(row))

    print('\n## Daniels order (precordial MDI, median): summit/vein course 90% > cusp >= RVOT > LV endo 10%')
    for mode in ('true', 'detected'):
        for lab, D, src in (('normal', nl, 'normal'), ('no fast layer', nf, 'nofast')):
            def m(sel):
                return med([f(r[f'{mode}_mdi_daniels']) for r in D.values() if sel(r)])
            print(f"{mode} {lab}: summit 90% {m(lambda r: r['family'] == 'lv_summit' and dep(r) == 90)}, "
                  f"vein course 90% {m(lambda r: r['family'] == 'lv_vein_course' and dep(r) == 90)}, "
                  f"cusp {m(lambda r: r['family'] == 'aortic_cusp')}, RVOT {m(lambda r: r['family'] == 'rvot')}, "
                  f"RVOT 10% {m(lambda r: r['family'] == 'rvot' and dep(r) == 10)}, "
                  f"LV endo 10% {m(lambda r: r['family'] in ('lv_free_wall', 'lv_septum') and dep(r) == 10)}"
                  + ('  (normal: new summit/vein sites not run yet)' if src == 'normal' else ''))

    print('\n## LV free wall, same position 10% -> 90% (true onset): median change, n up, AUC 90 vs 10')
    for lab, D in (('normal', nl), ('no fast layer', nf)):
        fw = [r for r in D.values() if r['family'] == 'lv_free_wall']
        pos = sorted({(r['level_z'], r['position']) for r in fw})
        out = []
        for k in MEAS:
            ch = []
            for p in pos:
                x = {dep(r): f(r[f'true_{k}']) for r in fw if (r['level_z'], r['position']) == p}
                if x.get(10) is not None and x.get(90) is not None:
                    ch.append(x[90] - x[10])
            hi = [f(r[f'true_{k}']) for r in fw if dep(r) == 90]
            lo = [f(r[f'true_{k}']) for r in fw if dep(r) == 10]
            out.append(f'{k} {med(ch)} ({sum(c > 0 for c in ch)}/{len(ch)} up, AUC {auc(hi, lo)})')
        q10 = med([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 10])
        q90 = med([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 90])
        print(f'{lab}: ' + '; '.join(out) + f'; QRS 10% {q10} -> 90% {q90} (+{round(100 * (q90 - q10) / q10, 1)}%)')

    print('\n## Epicardial calls (true / detected), paired sites, by target depth: normal -> no fast layer')
    for d in (10, 50, 90):
        P = [(a, b) for _, a, b in pairs if dep(b) == d and b['epi_endo_truth'] == 'True']
        cells = []
        for c in CALLS:
            n = lambda D, m: sum(D[f'{m}_{c}'] == 'True' for D in D)
            cells.append(f"{c} {n([a for a, _ in P], 'true')}/{n([a for a, _ in P], 'detected')} -> "
                         f"{n([b for _, b in P], 'true')}/{n([b for _, b in P], 'detected')}")
        print(f'{d}% (n {len(P)}): ' + '; '.join(cells))

    print('\n## Absolute QRS (decision 7: median at LV summit + aortic cusp sites within 132-193 ms)')
    for mode in ('true', 'detected'):
        for lab, D in (('normal', nl), ('no fast layer', nf)):
            R = [f(r[f'{mode}_qrs_duration_ms']) for r in D.values() if r['family'] in ('lv_summit', 'aortic_cusp')]
            print(f'{mode} {lab}: median {med(R)} ms (n {len([x for x in R if x is not None])}), range {min(x for x in R if x is not None)}-{max(x for x in R if x is not None)}')
    print('\ntotal activation, ms (median, range): normal',
          med([f(r['total_activation_ms']) for r in nl.values()]), 'no fast layer', med([f(r['total_activation_ms']) for r in nf.values()]),
          min(f(r['total_activation_ms']) for r in nf.values()), max(f(r['total_activation_ms']) for r in nf.values()))


if __name__ == '__main__':
    main()
