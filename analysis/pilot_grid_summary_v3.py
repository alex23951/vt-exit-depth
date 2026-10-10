#!/usr/bin/env python
"""
analysis/pilot_grid_sites_v3.csv (2026-10-04): the v2 table with the re-placed sites replaced.

Sites whose node differs from data/biv/<HEART>/sites_v2.json (or whose id is new) are read from
the v3 runs (runs/2026-10-04v3_eik_<HEART>_<site>_ecg); all others from the v2 runs
(runs/2026-10-03c_eik_...). Same columns as v2 plus position_phi_final, line_rule and run_prefix.
"""

import csv
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HEARTS = ['Y5HYEDL4']
SITE_KEYS = ['id', 'family', 'name', 'level_z', 'position', 'z', 'phi_deg', 'rho', 'sep', 'v',
             'bazan_region', 'bazan_region_v1', 'level_boundary', 'depth_target', 'depth_achieved',
             'depth_achieved_mm', 'wall_thickness_mm', 'off_line_mm', 'thin_wall', 'depth_miss', 'off_line',
             'summit_area', 'dist_left_sinus_mm', 'node']


def main():
    rows, moved = [], []
    for h in HEARTS:
        d = os.path.join(REPO, 'data', 'biv', h)
        v2 = {s['id']: s for s in json.load(open(os.path.join(d, 'sites_v2.json')))}
        for s in json.load(open(os.path.join(d, 'sites.json'))):
            is_moved = s['id'] not in v2 or v2[s['id']]['node'] != s['node']
            prefix = '2026-10-04v3' if is_moved else '2026-10-03c'
            f = os.path.join(REPO, 'runs', f'{prefix}_eik_{h}_{s["id"]}_ecg', 'criteria.json')
            if not os.path.exists(f):
                continue
            c = json.load(open(f))
            r = {'heart': h, 'package_version': c.get('package_version')}
            r.update({k: s.get(k) for k in SITE_KEYS})
            for m in ('detected', 'true'):
                for k, val in c[m]['measurements'].items():
                    if not isinstance(val, (dict, list)):
                        r[f'{m}_{k}'] = val
                for k, val in c[m]['criteria'].items():
                    r[f'{m}_{k}'] = val
            r['position_phi_final'] = s['position'].replace('phi', '') if s['position'].startswith('phi') else ''
            r['line_rule'] = s.get('line_rule')
            r['run_prefix'] = prefix
            rows.append(r)
            if is_moved:
                moved.append(s['id'])
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(os.path.join(REPO, 'analysis', 'pilot_grid_sites_v3.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(json.dumps({'rows': len(rows), 'moved_sites': moved}))


if __name__ == '__main__':
    main()
