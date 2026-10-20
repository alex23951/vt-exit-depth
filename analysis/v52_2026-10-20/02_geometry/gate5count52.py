"""v5.2 step 2e: the gate-5 position count per region (LOCK.md 11.3 items 1-4), before any beat.

Region map (11.3 item 2): AHA segment of the position (aha51 Frame, as report 34) and the v5.2 UVC z (re-solved fields),
both at the position's surface node (v5.1's 'surface_node', the point its depths share): superior = AHA anterior (1, 7,
13) + anterolateral (6, 12); inferior = AHA inferior (4, 10, 15) + inferolateral (5, 11); basal = z >= 0.55, apical =
z < 0.55; apex = AHA 17; septal segments (2, 3, 8, 9, 14) and apical lateral (16) take no region (16 is neither
anterolateral nor inferolateral in the 16-segment model: recorded, mine).
Eligible (11.3 item 3): LV free-wall, vein-course and summit positions (v5.1's pool) plus the re-anchored summit
positions (11.2a), which are pending the lock thread's Q6 / Q6b and so are counted separately when built.
A position = one surface location with its 90 % and 10 % sites. Counts pooled over the three hearts, as v5.1 scored it.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/gate5count52.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_pts                                                                 # noqa: E402

FAM = ('lv_free_wall', 'lv_vein_course', 'lv_summit')
SUP, INF = {1, 7, 13, 6, 12}, {4, 10, 15, 5, 11}


def region(seg, z):
    if seg == 17:
        return 'apex'
    if seg in SUP:
        return 'basal_superior' if z >= 0.55 else 'apical_superior'
    if seg in INF:
        return 'basal_inferior' if z >= 0.55 else 'apical_inferior'
    return None


def main():
    rows = []
    for h in G.HEARTS:
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
        P = read_pts(os.path.join(V, 'biv52')) / 1e3
        z = np.loadtxt(os.path.join(V, 'uvc', 'z.dat'))
        sites = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
        pos = {}
        for s in sites:
            if s['family'] in FAM:
                pos.setdefault((s['family'], s['position'], s['level_z']), {})[s['depth_target']] = s
        F = Q.AHA.Frame(h)
        keys = list(pos)
        sn = np.array([int(pos[k][0.9]['surface_node']) for k in keys])
        seg = Q.aha_labels(F, P[sn])
        for k, n, sg in zip(keys, sn, seg):
            d90, d10 = pos[k].get(0.9), pos[k].get(0.1)
            rows.append({'heart': h, 'family': k[0], 'position': k[1], 'level_z': k[2], 'surface_node': int(n), 'aha': int(sg),
                         'z_v52': round(float(z[n]), 3), 'region_11.3': region(int(sg), float(z[n])),
                         'v51_bazan_region': d90['bazan_region'], 'has_90_and_10': bool(d90 and d10), 'site_90': d90['id'], 'site_10': d10['id'] if d10 else None})
    regs = ['basal_superior', 'apical_superior', 'basal_inferior', 'apical_inferior', 'apex']
    cnt = {r: sum(1 for x in rows if x['region_11.3'] == r and x['has_90_and_10']) for r in regs}
    per = {h: {r: sum(1 for x in rows if x['heart'] == h and x['region_11.3'] == r) for r in regs} for h in G.HEARTS}
    v51 = {r: sum(1 for x in rows if x['v51_bazan_region'] == 'lv_' + r) for r in regs[:4]}
    gated = regs[:4]                                     # the four Bazan 2007 regions scored by gate 5 (v5.1 gates51.py)
    rec = {'lock_sha256': G.LOCK_SHA, 'positions': len(rows), 'pooled_count_per_region (11.3 map)': cnt, 'per_heart': per,
           'unassigned (septal or apical lateral)': sum(1 for x in rows if x['region_11.3'] is None),
           'v51_bazan_region_count_for_reference': v51,
           'regions_under_20 (gated)': [r for r in gated if cnt[r] < 20],
           'fill_rule_needed': bool(any(cnt[r] < 20 for r in gated)),
           'note': 're-anchored summit positions (2 per heart) not yet included: pending Q6 / Q6b', 'rows': rows}
    G.dump(rec, os.path.join(HERE, 'gate5count52.json'))
    print(json.dumps({k: v for k, v in rec.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
