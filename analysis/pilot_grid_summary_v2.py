#!/usr/bin/env python
"""
Pilot grid tables (v2, 2026-10-03).

1. analysis/pilot_grid_sites_v2.csv: one row per finished site of the v2 grid
   (runs/2026-10-03c_eik_<HEART>_<site>_ecg/criteria.json, scored with ecg_depth_criteria 0.2.0)
   with the site's UVCs, family, anatomical name, Bazan region (v2 and v1), target and achieved
   depth (fraction and mm), wall thickness, flags, summit area, distance to the left-sinus proxy,
   and every measurement and criterion call in both onset modes.
2. analysis/pilot_grid_v1_rescored.csv: the 108 first-run sites (v1 placement) with the main
   measurements and calls from 0.1.0 and 0.2.0 side by side, to separate the code change
   (IDT rule) from the placement change.
3. analysis/pilot_grid_v2_calls_by_depth.csv: share of sites called epicardial per criterion,
   by target depth and onset mode (v2 grid, 0.2.0).
"""

import csv
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SITE_KEYS = ['id', 'family', 'name', 'level_z', 'position', 'z', 'phi_deg', 'rho', 'sep', 'v',
             'bazan_region', 'bazan_region_v1', 'level_boundary', 'depth_target', 'depth_achieved',
             'depth_achieved_mm', 'wall_thickness_mm', 'off_line_mm', 'thin_wall', 'depth_miss', 'off_line',
             'summit_area', 'dist_left_sinus_mm', 'node']
MAIN = ['onset_ms', 'qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_valles', 'mdi_daniels',
        'q_lead_I', 'inferior_q_all']
CRIT = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055',
        'valles_mdi_ge_045', 'valles_idt_ge_90', 'valles_q_lead_I', 'valles_4step']


def write(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def main():
    out = os.path.join(REPO, 'analysis')
    rows = []
    for h in HEARTS:
        fs = os.path.join(REPO, 'data', 'biv', h, 'sites.json')
        if not os.path.exists(fs):
            continue
        for s in json.load(open(fs)):
            f = os.path.join(REPO, 'runs', f'2026-10-03c_eik_{h}_{s["id"]}_ecg', 'criteria.json')
            if not os.path.exists(f):
                continue
            d = json.load(open(f))
            r = {'heart': h, 'package_version': d.get('package_version')}
            r.update({k: s.get(k) for k in SITE_KEYS})
            for m in ('detected', 'true'):
                for k, v in d[m]['measurements'].items():
                    if not isinstance(v, (dict, list)):
                        r[f'{m}_{k}'] = v
                for k, v in d[m]['criteria'].items():
                    r[f'{m}_{k}'] = v
            rows.append(r)
    if rows:
        write(os.path.join(out, 'pilot_grid_sites_v2.csv'), rows)
        agg = []
        for depth in (0.1, 0.5, 0.9):
            sub = [r for r in rows if abs(r['depth_target'] - depth) < 1e-6]
            for m in ('detected', 'true'):
                rec = {'depth': depth, 'mode': m, 'n_sites': len(sub)}
                for c in CRIT:
                    vals = [r.get(f'{m}_{c}') for r in sub if r.get(f'{m}_{c}') is not None]
                    rec[c] = f'{sum(bool(v) for v in vals)}/{len(vals)}' if vals else 'n/a'
                for k in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_valles', 'qrs_duration_ms'):
                    vals = sorted(r[f'{m}_{k}'] for r in sub if isinstance(r.get(f'{m}_{k}'), (int, float)))
                    rec[f'median_{k}'] = round(vals[len(vals) // 2], 3) if vals else None
                agg.append(rec)
        write(os.path.join(out, 'pilot_grid_v2_calls_by_depth.csv'), agg)
    old = []
    for h in HEARTS:
        fs = os.path.join(REPO, 'data', 'biv', h, 'sites_v1.json')
        if not os.path.exists(fs):
            continue
        for s in json.load(open(fs)):
            e = os.path.join(REPO, 'runs', f'2026-10-03b_eik_{h}_{s["id"]}_ecg')
            if not os.path.exists(os.path.join(e, 'criteria_v020.json')):
                continue
            r = {'heart': h, 'site': s['id'], 'family': s['family'], 'depth_target': s['depth_target'],
                 'depth_actual_v1': s.get('depth_actual'), 'bazan_region_v1': s['bazan_region']}
            for tag in ('v010', 'v020'):
                d = json.load(open(os.path.join(e, f'criteria_{tag}.json')))
                for m in ('detected', 'true'):
                    for k in MAIN:
                        r[f'{tag}_{m}_{k}'] = d[m]['measurements'].get(k)
                    for c in CRIT:
                        r[f'{tag}_{m}_{c}'] = d[m]['criteria'].get(c)
            old.append(r)
    if old:
        write(os.path.join(out, 'pilot_grid_v1_rescored.csv'), old)
    print(json.dumps({'v2_sites': len(rows), 'v1_rescored_sites': len(old)}))


if __name__ == '__main__':
    main()
