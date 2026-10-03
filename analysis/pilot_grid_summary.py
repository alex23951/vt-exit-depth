#!/usr/bin/env python
"""
Pilot eikonal-grid summary: one row per finished site (runs/2026-10-03b_eik_<HEART>_<site>_ecg
/criteria.json + data/biv/<HEART>/sites.json), written to analysis/pilot_grid_sites.csv, and the
share of sites each criterion calls epicardial, by wall depth (10 / 50 / 90 %) and onset mode,
written to analysis/pilot_grid_calls_by_depth.csv. Only sites that finished are included.

Usage: python analysis/pilot_grid_summary.py
"""

import csv
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
MEAS = ['onset_ms', 'qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_valles', 'mdi_daniels',
        'q_lead_I', 'inferior_q_all', 'inferior_axis', 'rbbb_like']
CRIT = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055',
        'valles_mdi_ge_045', 'valles_idt_ge_90', 'valles_q_lead_I', 'valles_4step']


def main():
    rows = []
    for h in HEARTS:
        sites = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
        for s in sites:
            f = os.path.join(REPO, 'runs', f'2026-10-03b_eik_{h}_{s["id"]}_ecg', 'criteria.json')
            if not os.path.exists(f):
                continue
            d = json.load(open(f))
            r = {'heart': h, 'site': s['id'], 'family': s['family'], 'sector': s['sector'],
                 'level_z': s['level_z'], 'depth_target': s['depth_target'], 'depth_actual': s.get('depth_actual'),
                 'depth_miss': s.get('depth_miss'), 'bazan_region': s['bazan_region']}
            for m in ('detected', 'true'):
                for k in MEAS:
                    r[f'{m}_{k}'] = d[m]['measurements'].get(k)
                for k, v in d[m]['criteria'].items():
                    r[f'{m}_{k}'] = v
            rows.append(r)
    if not rows:
        print('no finished sites'); return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    os.makedirs(os.path.join(REPO, 'analysis'), exist_ok=True)
    with open(os.path.join(REPO, 'analysis', 'pilot_grid_sites.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    out = []
    for h in HEARTS + ['all']:
        for depth in (0.1, 0.5, 0.9):
            sub = [r for r in rows if (h == 'all' or r['heart'] == h) and abs(r['depth_target'] - depth) < 1e-6]
            if not sub:
                continue
            for m in ('detected', 'true'):
                rec = {'heart': h, 'depth': depth, 'mode': m, 'n_sites': len(sub)}
                for c in CRIT:
                    vals = [r.get(f'{m}_{c}') for r in sub if r.get(f'{m}_{c}') is not None]
                    rec[c] = f'{sum(bool(v) for v in vals)}/{len(vals)}' if vals else 'n/a'
                for k in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_valles', 'qrs_duration_ms'):
                    vals = sorted(r[f'{m}_{k}'] for r in sub if isinstance(r.get(f'{m}_{k}'), (int, float)))
                    rec[f'median_{k}'] = round(vals[len(vals) // 2], 3) if vals else None
                out.append(rec)
    with open(os.path.join(REPO, 'analysis', 'pilot_grid_calls_by_depth.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for rec in out:
        print(json.dumps(rec))


if __name__ == '__main__':
    main()
