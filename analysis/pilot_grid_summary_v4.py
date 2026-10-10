#!/usr/bin/env python
"""
analysis/pilot_grid_sites_v4.csv (2026-10-04): every v3 site re-scored with ecg_depth_criteria
0.3.0 (default settings) from the saved ECG traces, both onset modes, same baseline window and
true-mode fiducials as before (sims/biv_model/10_measure_ecg.py).

Columns: all v3 columns, package_version = 0.3.0, plus per onset mode (true_ / detected_
prefixes, as in v2 / v3): q_ratio_avl_avr, r_ratio_iii_ii, rs_ratio_v1, q_V1, the six
prisco_*_mv_s scalars, per-lead q/r/s amplitudes (q_amp_<lead>, r_amp_<lead>, s_amp_<lead>)
and every criterion evaluate() returns (incl. the yamada2010_ / santangeli2015_ / jauregui2012_
and prisco2024_ keys). Infinite ratios are written as inf.
Also checks that every column 0.2.0 produced is identical between v3 and v4.
"""

import csv
import json
import math
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKG = os.path.join(REPO, 'code', 'ecg_depth_criteria')        # 0.3.0
MEASURE = os.path.join(REPO, 'sims', 'biv_model', '10_measure_ecg.py')
NEW_SCALARS = ['q_ratio_avl_avr', 'r_ratio_iii_ii', 'rs_ratio_v1', 'q_V1', 'prisco_initial_mv_s',
               'prisco_initial_limb_mv_s', 'prisco_initial_precordial_mv_s', 'prisco_average_mv_s',
               'prisco_average_limb_mv_s', 'prisco_average_precordial_mv_s']
AMPS = {'q_amplitude_mv': 'q_amp', 'r_amplitude_mv': 'r_amp', 's_amplitude_mv': 's_amp'}


def fmt(v):
    if isinstance(v, float) and math.isinf(v):
        return 'inf' if v > 0 else '-inf'
    return v


def main():
    v3 = list(csv.DictReader(open(os.path.join(REPO, 'analysis', 'pilot_grid_sites_v3.csv'))))
    rows, mism = [], []
    for r in v3:
        h, sid, prefix = r['heart'], r['id'], r['run_prefix']
        run = os.path.join(REPO, 'runs', f'{prefix}_eik_{h}_{sid}')
        ecg = run + '_ecg'
        last = json.load(open(os.path.join(run, 'summary_12.json')))['total_activation_ms']
        out = os.path.join(ecg, 'criteria_v030.json')
        args = [sys.executable, MEASURE, os.path.join(ecg, 'POSTPROC_DIR'), '--stim-ms', '0',
                '--last-act-ms', str(last), '--out', out]
        if r['bazan_region']:
            args += ['--region', r['bazan_region']]
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, ECG_PKG=PKG))
        d = json.load(open(out))
        n = dict(r)
        n['package_version'] = d['package_version']
        for m in ('detected', 'true'):
            meas, crit = d[m]['measurements'], d[m]['criteria']
            for k, val in meas.items():
                if k in AMPS:
                    for lead, a in val.items():
                        n[f'{m}_{AMPS[k]}_{lead}'] = fmt(a)
                elif not isinstance(val, (dict, list)):
                    n[f'{m}_{k}'] = fmt(val)
            for k, val in crit.items():
                n[f'{m}_{k}'] = fmt(val)
        # compare every column that v3 (0.2.0) already had
        for k, old in r.items():
            if k == 'package_version':
                continue
            new = n.get(k)
            if str(new if new is not None else '') != str(old):
                try:
                    if old != '' and new is not None and abs(float(new) - float(old)) < 1e-9:
                        continue
                except (TypeError, ValueError):
                    pass
                mism.append((sid, k, old, new))
        rows.append(n)
    keys = list(dict.fromkeys(k for x in rows for k in x))
    path = os.path.join(REPO, 'analysis', 'pilot_grid_sites_v4.csv')
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    new_cols = [k for k in keys if k not in v3[0]]
    print(json.dumps({'rows': len(rows), 'columns': len(keys), 'new_columns': len(new_cols),
                      'bytes': os.path.getsize(path), 'old_column_mismatches': len(mism),
                      'mismatch_examples': mism[:15],
                      'new_criterion_columns': sorted({k.split('_', 1)[1] for k in new_cols
                                                       if k.split('_', 1)[1].startswith(('yamada', 'santangeli', 'jauregui', 'prisco2024'))})},
                     indent=1))


if __name__ == '__main__':
    main()
