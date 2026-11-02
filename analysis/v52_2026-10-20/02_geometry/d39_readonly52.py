"""D39's two read-only items (lock thread, 2 Nov 2026; pc-note-d39-2026-11-02.md section 4), labelled
"D39 read-only (proposed entry)". Geometry only: no beat, activation or lead-field value.

(a) D39 (1) (e): P16 report 2's checks for its findings 2 and 3 (ladder52.py), applied to report 7's 864 displaced points
    (sites52.json, families displaced_transmural and displaced_tangential, 144 + 144 per heart):
    finding 2, a step meant to stay in the wall that moves partly across it: |d . unit grad APD w| > 0.3, d the point's
      stored unit step direction and grad APD w D33's mean element gradient at the parent site node. Report 7 has no
      cross-fibre (+s) step, so the check is applied to its in-wall steps, the fibre (+f) points; its transmural points
      move along grad APD w by D33 and are not in-wall steps (reported, not flagged). unit grad APD w is read as the
      parent's transmural point's stored direction, which is D33's (sense x unit gradient; ladder52.py recomputed it
      within 0.0005 deg); where that direction is zero (finding 1's site) the check is undefined and reported so.
    finding 3: the snapped node touches no element of its parent's ventricle (ladder52.py's rule: biv52 elements round
      the node, LV group tags 1, 25, 29 or RV group tags 2, 28, the side by the parent family as sites52.RV_FAMILIES).
    Counts per heart, by parent family, with the flagged ids.
(b) D39 (3) (8): each site's region by family and id (not the stored labels): rvot -> RVOT; aortic_cusp, cusp_crescent ->
    cusps; lv_summit, summit_reanchored and lv_vein_course ids with proximal_aiv -> summit; other lv_vein_course,
    lv_free_wall, gate5fill -> LV free wall; rv_free_wall -> RV free wall; lv_septum and report 26's focus
    (intramural_focus) and grid points -> septum; supravalvar -> supravalvar (its own region, described only). Displaced
    and ladder points take their parent's region. LVOT: no site. Every v5.1 site (sites.json) and every point of
    sites52.json's new_sites; counts per heart by region and by family. Report 26's grids are placed from the focus beat
    and are not in the manifest yet.
Writes d39_readonly52.json and d39_regions52.csv (one row per site or point) beside this script.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/d39_readonly52.py
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import read_elem                                                                # noqa: E402
from sites52 import RV_FAMILIES                                                             # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
THR = 0.3


def region(fam, sid):
    if fam == 'rvot':
        return 'RVOT'
    if fam in ('aortic_cusp', 'cusp_crescent'):
        return 'cusps'
    if fam in ('lv_summit', 'summit_reanchored') or (fam == 'lv_vein_course' and 'proximal_aiv' in sid):
        return 'summit'
    if fam in ('lv_vein_course', 'lv_free_wall', 'gate5fill'):
        return 'LV free wall'
    if fam == 'rv_free_wall':
        return 'RV free wall'
    if fam in ('lv_septum', 'intramural_focus', 'intramural_lv_grid', 'intramural_rv_grid'):
        return 'septum'
    if fam == 'supravalvar':
        return 'supravalvar'
    return None


def main():
    t0 = time.time()
    out = {'rule': 'D39 read-only (proposed entry): D39 (1) (e) and (3) (8), lock thread, 2 Nov 2026', 'lock_sha256': G.LOCK_SHA,
           'threshold_finding2': THR, 'hearts': {}}
    rows = []
    for h in HEARTS:
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
        v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
        man = json.load(open(os.path.join(V, 'sites52.json')))
        new = man['new_sites']
        fam51 = {s['id']: s['family'] for s in v51}
        reg = {}
        for s in v51:
            reg[s['id']] = region(s['family'], s['id'])
        for s in new:
            if s['family'] in ('displaced_transmural', 'displaced_tangential', 'ladder'):
                reg[s['id']] = reg[s['parent']]
            else:
                reg[s['id']] = region(s['family'], s['id'])
        unmapped = [k for k, v in reg.items() if v is None]
        if unmapped:
            sys.exit(f'{h}: sites with no region under D39 (3) (8): {unmapped[:10]}; stop and report')
        for s in v51:
            rows.append({'heart': h, 'id': s['id'], 'family': s['family'], 'parent': '', 'parent_family': '', 'region': reg[s['id']]})
        for s in new:
            rows.append({'heart': h, 'id': s['id'], 'family': s['family'], 'parent': s.get('parent', ''),
                         'parent_family': s.get('parent_family', ''), 'region': reg[s['id']]})
        hr = {'manifest_sha256': G.sha256(os.path.join(V, 'sites52.json')), 'v51_sites_sha256': G.sha256(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json'))}
        cnt = defaultdict(Counter)
        for s in v51:
            cnt['v51 sites'][reg[s['id']]] += 1
        for s in new:
            cnt[s['family']][reg[s['id']]] += 1
        hr['region_counts_by_family'] = {f: dict(sorted(c.items())) for f, c in cnt.items()}
        tot = Counter()
        for c in cnt.values():
            tot.update(c)
        hr['region_counts_all'] = dict(sorted(tot.items()))
        hr['LVOT'] = 'no site (D39 (3) (8))'
        hr['report26_grids'] = 'placed from the focus beat (D25); not in the manifest yet; region septum when built'
        # ---- (a) report 7's displaced points
        disp = [s for s in new if s['family'] in ('displaced_transmural', 'displaced_tangential')]
        tmdir = {s['parent']: np.array(s['direction'], float) for s in disp if s['family'] == 'displaced_transmural'}
        Em, tm = read_elem(os.path.join(V, 'biv52'))
        nodes = np.array([s['node'] for s in disp], np.int64)
        touch = defaultdict(set)
        sel = np.isin(Em, nodes).any(1)
        for e, t in zip(Em[sel], tm[sel]):
            for n in e:
                touch[int(n)].add(int(t))
        pts, f2, f3, undef = [], [], [], []
        for s in disp:
            g = tmdir[s['parent']]
            ng = np.linalg.norm(g)
            dot = None if ng < 1e-12 else float(abs(np.array(s['direction'], float) @ g) / ng)
            side = set(G.RV_GROUP) if s['parent_family'] in RV_FAMILIES else set(G.LV_GROUP)
            other = not (touch[int(s['node'])] & side)
            fl2 = bool(s['family'] == 'displaced_tangential' and dot is not None and dot > THR)
            if s['family'] == 'displaced_tangential' and dot is None:
                undef.append(s['id'])
            if fl2:
                f2.append(s['id'])
            if other:
                f3.append(s['id'])
            pts.append({'id': s['id'], 'family': s['family'], 'parent_family': s['parent_family'],
                        '|d.unit_grad_w|': None if dot is None else round(dot, 4), 'finding2_flag': fl2, 'finding3_flag': bool(other),
                        'node_element_tags': sorted(touch[int(s['node'])])})
        for r in rows:
            if r['heart'] == h:
                p = next((q for q in pts if q['id'] == r['id']), None)
                r['abs_d_dot_unit_grad_w'] = p['|d.unit_grad_w|'] if p else None
                r['finding2_flag'] = p['finding2_flag'] if p else None
                r['finding3_flag'] = p['finding3_flag'] if p else None
        def by_fam(ids):
            fam = {q['id']: (q['family'], q['parent_family']) for q in pts}
            c = defaultdict(Counter)
            for i in ids:
                c[fam[i][0]][fam[i][1]] += 1
            return {k: dict(sorted(v.items())) for k, v in c.items()}
        tg = [q for q in pts if q['family'] == 'displaced_tangential' and q['|d.unit_grad_w|'] is not None]
        tmv = [q for q in pts if q['family'] == 'displaced_transmural' and q['|d.unit_grad_w|'] is not None]
        hr['report7_points'] = {
            'points': len(pts), 'by_family': dict(Counter(q['family'] for q in pts)),
            'finding2 (fibre points with |f . unit grad APD w| > 0.3)': {'count': len(f2), 'by_family_and_parent_family': by_fam(f2), 'ids': f2},
            'finding2_undefined (parent has no APD w gradient: finding 1)': undef,
            '|f . unit grad w| over fibre points (median, p90, max)': [round(float(np.median([q['|d.unit_grad_w|'] for q in tg])), 4),
                                                                      round(float(np.percentile([q['|d.unit_grad_w|'] for q in tg], 90)), 4),
                                                                      round(float(max(q['|d.unit_grad_w|'] for q in tg)), 4)],
            'transmural points |d . unit grad w| (min, max; 1 by D33, not flagged)': [round(min(q['|d.unit_grad_w|'] for q in tmv), 4), round(max(q['|d.unit_grad_w|'] for q in tmv), 4)],
            'finding3 (snapped node touches no element of the parent ventricle)': {'count': len(f3), 'by_family_and_parent_family': by_fam(f3), 'ids': f3},
            'flagged_by_either': len(set(f2) | set(f3))}
        out['hearts'][h] = hr
        print(h, 'regions', hr['region_counts_all'], 'finding2', len(f2), 'finding3', len(f3), 'undefined', undef, round(time.time() - t0, 1), 's', flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, 'd39_regions52.csv'), index=False)
    out['csv'] = {'path': 'analysis/v52_2026-10-20/02_geometry/d39_regions52.csv', 'rows': int(len(df)), 'sha256': G.sha256(os.path.join(HERE, 'd39_regions52.csv'))}
    out['wall_s'] = round(time.time() - t0, 1)
    G.dump(out, os.path.join(HERE, 'd39_readonly52.json'))


if __name__ == '__main__':
    main()
