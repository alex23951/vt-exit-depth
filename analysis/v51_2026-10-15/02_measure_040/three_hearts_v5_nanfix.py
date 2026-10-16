#!/usr/bin/env python
"""
NaN-FIX COPY (16 Oct 2026, v5.1 brief Step 2, decision H) of analysis/v5_adopted_2026-10-13/three_hearts_v5.py
(sha256 b9517484dd29af896fdf916ae9fbf4ac887437b7de2cceb1365051e1855c26ec; diff beside this file).
Changed: paths (REPO, OUT) and the aggregation only: f() / med() / auc() use nanstats.py (NaN left out and counted,
never a loss), paired changes drop the whole pair, call counts print k / n scored (m unscorable).
Original docstring follows.
COPY for model v5 (13 Oct 2026; analysis/v5_adopted_2026-10-13): reads purk_<HEART>_v5.csv (graph-only v5 grid),
writes to analysis/v5_adopted_2026-10-13/three_hearts/. Original docstring follows.
Network arm on the three pilot hearts (10 Oct 2026): the 144 v5 sites per heart with the His-Purkinje network v3
(jobs 8-10), ECG with the cb volume conductor (heart at Clerc scale + cavity blood; analysis/grids_2026-10-07/
purk_<HEART>_cb.csv), ecg_depth_criteria 0.3.0, both onset modes.
  Y5HYEDL4  control
  6G8DD8S5  heart failure, wide QRS (LBBB-like: proximal left-bundle cut)
  7D98EVAR  heart failure, narrow QRS
Pilot hearts: descriptive only, no confirmatory statistics. Prints the tables of results.md (same layout as
analysis/three_arms_2026_10_08.py, arms replaced by hearts) and writes sites.csv (one row per heart and site).
"""

import csv
import math
import os
import sys
import statistics as st

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nanstats as ns  # noqa: E402
G = os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13')
OUT = os.path.join(REPO, 'analysis', 'v51_2026-10-15', '02_measure_040', 'three_hearts_v5')
HEARTS = {'Y5HYEDL4': 'control', '6G8DD8S5': 'HF wide QRS (LBBB)', '7D98EVAR': 'HF narrow QRS'}
GROUP = {'lv_free_wall': 'LV free wall', 'lv_septum': 'LV septum', 'rv_free_wall': 'RV free wall', 'rvot': 'RVOT',
         'aortic_cusp': 'Aortic cusp', 'lv_summit': 'LV summit', 'lv_vein_course': 'LV vein course'}
MEAS = ['qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels']
CALLS = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055', 'valles_q_lead_I']


def f(x):
    return ns.num(x)


def med(xs, nd=3):
    return ns.fmt_median(xs, nd)


def auc(pos, neg):
    return ns.fmt_auc(pos, neg, 2)


def dep(r):
    return int(round(float(r['depth_target']) * 100))


def main():
    D = {h: [r for r in csv.DictReader(open(os.path.join(G, f'purk_{h}_v5.csv'))) if r['family'] != 'his'] for h in HEARTS}
    for h, R in D.items():
        print(f'{h} ({HEARTS[h]}): {len(R)} sites, criteria file {R[0].get("criteria_file", "graph_v5 in-memory scoring")}')
    os.makedirs(OUT, exist_ok=True)
    cols = [f'{m}_{k}' for m in ('true', 'detected') for k in MEAS] + [f'true_{c}' for c in CALLS]
    with open(os.path.join(OUT, 'sites.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['heart', 'id', 'name', 'group', 'depth_target', 'depth_achieved', 'epi_endo_truth'] + cols)
        for h, R in D.items():
            for r in R:
                w.writerow([h, r['id'], r['name'], GROUP[r['family']], r['depth_target'], r['depth_achieved'], r['epi_endo_truth']]
                           + [r.get(c) for c in cols])

    for mode in ('true', 'detected'):
        print(f'\n## {mode} onset, medians Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR, by group')
        print('group | n per heart | QRS | pseudo-delta | IDT V2 | shortest RS | MDI')
        for fam, g in GROUP.items():
            cells = [' / '.join(str(med([f(r[f'{mode}_{k}']) for r in D[h] if r['family'] == fam], 2 if k == 'mdi_daniels' else 1))
                                for h in HEARTS) for k in MEAS]
            print(f"{g} | {sum(r['family'] == fam for r in D['Y5HYEDL4'])} | " + ' | '.join(cells))

    print('\n## LV free wall, same position 10 % -> 90 % (true onset): median change (n up / n), AUC 90 vs 10; QRS 10 -> 90 %')
    for h, R in D.items():
        fw = [r for r in R if r['family'] == 'lv_free_wall']
        pos = sorted({(r['level_z'], r['position']) for r in fw})
        out = []
        for k in MEAS:
            ch, nd_ = [], 0
            for p in pos:
                x = {dep(r): f(r[f'true_{k}']) for r in fw if (r['level_z'], r['position']) == p}
                if 10 in x and 90 in x:
                    if math.isnan(x[10]) or math.isnan(x[90]):
                        nd_ += 1
                    else:
                        ch.append(x[90] - x[10])
            out.append(f"{k} {med(ch, 3)} ({sum(c > 0 for c in ch)}/{len(ch)}{f', {nd_} pairs unscorable' if nd_ else ''}, AUC "
                       f"{auc([f(r[f'true_{k}']) for r in fw if dep(r) == 90], [f(r[f'true_{k}']) for r in fw if dep(r) == 10])})")
        q10 = round(ns.scored_median([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 10])[0], 1)
        q90 = round(ns.scored_median([f(r['true_qrs_duration_ms']) for r in fw if dep(r) == 90])[0], 1)
        print(f'{h}: ' + '; '.join(out) + f'; QRS {q10} -> {q90} ({round(100 * (q90 - q10) / q10, 1)} %)')

    print('\n## All sites with a depth truth (cusps out): AUC 90 % vs 10 % and 90 % vs 50 %, true / detected onset')
    for h, R in D.items():
        T = [r for r in R if r['epi_endo_truth'] == 'True']
        for lo in (10, 50):
            print(f'{h} 90 vs {lo}: ' + '; '.join(
                f"{k} {auc([f(r['true_' + k]) for r in T if dep(r) == 90], [f(r['true_' + k]) for r in T if dep(r) == lo])} / "
                f"{auc([f(r['detected_' + k]) for r in T if dep(r) == 90], [f(r['detected_' + k]) for r in T if dep(r) == lo])}" for k in MEAS))

    print('\n## Daniels order, precordial MDI medians (Daniels 2006: LV epicardial perivascular 0.61 > ASOV 0.46 > RVOT 0.40 > LV endo 0.34)')
    for mode in ('true', 'detected'):
        for h, R in D.items():
            m = lambda sel: med([f(r[f'{mode}_mdi_daniels']) for r in R if sel(r)], 2)
            print(f"{mode} {h}: summit 90 % {m(lambda r: r['family'] == 'lv_summit' and dep(r) == 90)}, vein course 90 % "
                  f"{m(lambda r: r['family'] == 'lv_vein_course' and dep(r) == 90)}, cusp {m(lambda r: r['family'] == 'aortic_cusp')}, "
                  f"RVOT {m(lambda r: r['family'] == 'rvot')}, LV endo 10 % {m(lambda r: r['family'] in ('lv_free_wall', 'lv_septum') and dep(r) == 10)}")

    print('\n## Absolute QRS (decision 7: median at LV summit + aortic cusp within 132-193 ms in control hearts; idiopathic VAs 147-175 ms)')
    for mode in ('true', 'detected'):
        print(mode + ': ' + '; '.join(f"{h} {med([f(r[f'{mode}_qrs_duration_ms']) for r in R if r['family'] in ('lv_summit', 'aortic_cusp')], 1)}"
                                      for h, R in D.items()))

    print('\n## Epicardial calls (true onset), sites with a depth truth, by target depth: Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR')
    for d in (10, 50, 75, 90):
        n = [sum(dep(r) == d and r['epi_endo_truth'] == 'True' for r in D[h]) for h in HEARTS]
        cells = [c + ' ' + ' | '.join(ns.fmt_rate([r['true_' + c] for r in D[h] if dep(r) == d and r['epi_endo_truth'] == 'True'])
                                      for h in HEARTS) for c in CALLS]
        print(f"{d} % (n {' | '.join(map(str, n))}): " + '; '.join(cells))


if __name__ == '__main__':
    main()
