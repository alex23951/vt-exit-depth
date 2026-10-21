"""v5.2 step 2e: gate 5's fill (D23, adopted 21 Oct 2026 17:52:13 UTC; C65: v5.1's grid rule as previewed in P10 (a)).

The construction of preview_p10a.py (P10 (a)) with D26 (AHA 16 apical superior, rule 'C6') and the lock's pool (v5.1
free-wall and vein-course positions plus the D22 summit positions; v5.1's summit positions in the 4 mm list, which P10 (a)
showed changes nothing), on the converged fields of fields52.py (z, v; UVC phi geometric): tiers T2 / T4 / T8, the
rotation Y5HYEDL4, 6G8DD8S5, 7D98EVAR, regions basal superior, apical superior, basal inferior, apical inferior, each to
its first count of 20 matched 90 % positions (11.3 item 5's pairing); the 1.05 mm nominal-point rule; the 4 mm spacing;
8.7's capture on both sites; sites placed by v5.1's grid rule (geometric line, 10 % / 90 % fractions; re-aim on v = 0).
Nodes already used by any manifest site other than the report-7 displaced set are not reused (the displaced set is
built after the fill and avoids the fill's nodes).
Outputs: data/biv/<H>/v52/gate5fill52.json (each heart's fill sites, ids after every existing id in the order added) and
gate5fill52.json here (candidate list with outcomes in order, counts, composition, the realised ledger total).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/gate5fill52.py
"""
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import preview_d23 as D                                                                     # noqa: E402
import preview_d23r as DR                                                                   # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_vtx                                                                 # noqa: E402

AHA = Q.AHA
R34 = Q.S52.R34
SUP, INF = {1, 7, 13, 6, 12}, {4, 10, 15, 5, 11}
REGS = D.REGS
EXIST = 'keep'
ORDER = os.environ.get('G5_ORDER', 'record')
# 'record': D23's "fill sites take ids after every existing id, in the order added" (pairing order: existing ids, then fill
# sites in the order added); 'p10a': P10 (a)'s string ids, under which 'gate5fill_...' sorted before the 'lv_...' ids.
SORTKEY = (lambda s: (1, s['order'], '') if s.get('origin') == 'gate5fill' else (0, 0, s['id'])) if ORDER == 'record' else (lambda s: s['id'])
POOL_FAM = ('lv_free_wall', 'lv_vein_course')          # item 5: v5.1's lv_summit not pooled


def aha_fw(F, X):
    """Q.aha_labels plus the free-wall fraction fw (0 at the anterior insertion, 1 at the inferior) for each point."""
    f = F.f(X); seg = np.zeros(len(X), int); fwv = np.full(len(X), np.nan)
    c = F.cap_f
    lev = np.where(f < c + (1 - c) / 3, 'apical', np.where(f < c + 2 * (1 - c) / 3, 'mid', 'basal'))
    a = np.round(f * F.Lax, 1); cache = {}
    for av in np.unique(a[f >= c]):
        a_use = av; loc = F.local(a_use)
        while loc is None or np.isnan(loc[3]) or np.isnan(loc[4]):
            a_use = round(a_use - 1.0, 1)
            if a_use < 0:
                loc = None; break
            loc = F.local(a_use)
        cache[av] = loc
    seg[f < c] = 17
    for i in np.where(f >= c)[0]:
        loc = cache[a[i]]
        if loc is None:
            continue
        c0, e1, e2, ia, ii = loc
        th = float(np.degrees(np.arctan2((X[i] - c0) @ e2, (X[i] - c0) @ e1)))
        if ii <= th <= ia:
            s = 'septal' if lev[i] == 'apical' else ('anteroseptal' if th >= (ia + ii) / 2 else 'inferoseptal')
        else:
            fw = ((th - ia) % 360) / ((ii - ia) % 360); fwv[i] = fw
            s = (['anterior', 'lateral', 'inferior'][min(2, int(fw * 3))] if lev[i] == 'apical'
                 else ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))])
        seg[i] = AHA.SEG_NO[(lev[i], s)]
    return seg, fwv


def region(seg, fw, z, rule):
    if seg == 16:
        sup = True if rule == 'C6' else bool(fw < 0.5)
        return ('basal_' if z >= 0.55 else 'apical_') + ('superior' if sup else 'inferior')
    if seg in SUP:
        return 'basal_superior' if z >= 0.55 else 'apical_superior'
    if seg in INF:
        return 'basal_inferior' if z >= 0.55 else 'apical_inferior'
    return None


def pair_sites(sites):
    """sites: dicts with heart, id, depth (0.9 / 0.1), x, region, origin. Item 5 per heart and region."""
    tot = {r: 0 for r in REGS}; comp = {r: {} for r in REGS}
    for h in G.HEARTS:
        for r in REGS:
            nine = sorted([s for s in sites if s['heart'] == h and s['region'] == r and s['depth'] == 0.9], key=SORTKEY)
            ten = sorted([s for s in sites if s['heart'] == h and s['region'] == r and s['depth'] == 0.1], key=SORTKEY)
            used = set()
            for s9 in nine:
                best, bd = None, None
                for s1 in ten:
                    if s1['id'] in used:
                        continue
                    d = float(np.linalg.norm(s9['x'] - s1['x']))
                    if 13.0 <= d <= 23.0 and (bd is None or abs(d - 18) < abs(bd - 18)):
                        best, bd = s1['id'], d
                if best:
                    used.add(best); tot[r] += 1; comp[r][s9['origin']] = comp[r].get(s9['origin'], 0) + 1
    return tot, comp


def main():
    H = {h: D.Heart(h) for h in G.HEARTS}
    out = {'lock_sha256': G.LOCK_SHA, 'P4a_order_used_by_preview_d23r': {
        'candidate_id': 'per heart and tier, the index in the list of new (z, phi) combinations ordered by z then phi (degrees 0-360)',
        'tiers': 'per region: T2 first, then T4, then T8; the tiers run per region across the hearts (each heart has one queue per region, holding its T2, T4, T8 candidates in that order)',
        'rotation': 'Y5HYEDL4, 6G8DD8S5, 7D98EVAR in turn; a heart whose queue for the region is empty is skipped; within a turn a heart takes its next candidate that passes (candidates failing a rule are consumed and counted)',
        'region_order': 'basal superior, apical superior, basal inferior, apical inferior',
        'existing_for_4mm': "every position of that heart in the pool (v5.1 free wall, vein course, the projB summit positions), v5.1's summit positions if P10A_EXIST=keep, and every position already added for any region",
        '2_ring_geodesic': "Dijkstra on the surface's 2-ring graph (each node joined to its neighbours and to their neighbours by straight chords, step0_report34.Surf), so slightly shorter than the 1-ring edge path and close to the true geodesic"},
        'mitral_annulus_z (report 34 item 2)': 1.0, 'rules': {}}
    for h, Hh in H.items():
        cv = os.path.join(G.REPO, 'data', 'biv', h, 'v52', 'fields52')
        Hh.z = np.load(os.path.join(cv, 'z.npy')); Hh.v = np.load(os.path.join(cv, 'v_uvc.npy'))
        Hh.epi_fw = Hh.epi[Hh.v[Hh.epi] == 0]; Hh.t_epi_fw = cKDTree(Hh.pts[Hh.epi_fw])
        F = Hh.F
        n51 = len(F.P); v = Hh.v[:n51]
        lve, rve = F.epi[v[F.epi] == 0], F.epi[v[F.epi] == 1]
        F.groove = lve[cKDTree(F.P[rve]).query(F.P[lve])[0] <= 2.0]
    for rule in ('C6',):
        for Hh in H.values():
            Hh.used = set()
        sites, cands, SL, SE, CAP, lvtri, posn = [], {}, {}, {}, {}, {}, []
        drops = {'nominal_point_off_by_more_than_1.05mm_or_outside': 0, 'above_mitral_annulus': 0}
        for h, Hh in H.items():
            V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces')
            v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
            Hh.used |= {int(s['node']) for s in v51}
            Hh.used |= {int(s['node']) for s in json.load(open(os.path.join(V, 'sites52.json')))['new_sites'] if not s['family'].startswith('displaced') and s['family'] != 'gate5fill'}
            tri = lambda n: np.loadtxt(os.path.join(S, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
            lvtri[h] = tri('lv_endo')
            SL[h], SE[h] = R34.Surf(Hh.pts, lvtri[h]), R34.Surf(Hh.pts, tri('epi'))
            CAP[h] = DR.Capture(h, Hh.pts)
            pool = [s for s in v51 if s['family'] in POOL_FAM and s['depth_target'] in (0.9, 0.1)]
            pj = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
            man = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
            msum = {x['id']: x for x in man if x['family'] == 'summit_reanchored'}
            assert {x['id']: int(x['node']) for x in pj['sites (preview, not in the manifest)']} == {k: int(v['node']) for k, v in msum.items()}
            for s in msum.values():
                if s['depth_target'] in (0.9, 0.1):
                    pool.append({'id': s['id'] + '_' + h, 'node': s['node'], 'depth_target': s['depth_target'], 'family': 'summit_reanchored'})
            nodes = np.array([int(s['node']) for s in pool])
            seg, fw = aha_fw(Hh.F, Hh.pts[nodes])
            for s, n, sg, f_ in zip(pool, nodes, seg, fw):
                sites.append({'heart': h, 'id': s['id'], 'depth': s['depth_target'], 'x': Hh.pts[n], 'origin': s['family'],
                              'region': region(int(sg), f_, float(Hh.z[n]), rule)})
            for s in v51:
                if s['family'] in D.FAM and (EXIST == 'keep' or s['family'] != 'lv_summit'):
                    posn.append({'heart': h, 'surface_node': int(s['surface_node']), 'epi_start': s['family'] != 'lv_free_wall'})
            for s in pj['sites (preview, not in the manifest)']:
                pass
            for nm, pz in pj['positions'].items():
                posn.append({'heart': h, 'surface_node': pz['surface_node'], 'epi_start': True})
            fwz = {}
            for s in v51:
                if s['family'] == 'lv_free_wall':
                    fwz.setdefault(s['level_z'], set()).add(int(s['position'].replace('phi', '')))
            phis = sorted({p % 360 for vv in fwz.values() for p in vv})
            seen = {(lev, p % 360) for lev, vv in fwz.items() for p in vv}
            tiers = []
            for k in (2, 4, 8):
                zs = sorted({round(a + (b - a) * i / k, 6) for a, b in zip(DR.ZLEV[:-1], DR.ZLEV[1:]) for i in range(0, k + 1)} - {0.0, 1.0})
                ring = phis + [phis[0] + 360]
                ps = sorted({round((a + (b - a) * i / k) % 360, 6) for a, b in zip(ring[:-1], ring[1:]) for i in range(0, k + 1)})
                combos = [(z, p) for z in zs for p in ps if (z, p) not in seen]
                seen |= set(combos)
                tiers += [(f'T{k}', i, z, p) for i, (z, p) in enumerate(combos)]
            cands[h] = tiers
        count0, comp0 = pair_sites(sites)
        res = {'matched_before_fill': count0, 'matched_composition_before_fill': comp0}

        def nominal(h, z0, p0):
            Hh = H[h]; T = lvtri[h]
            zt, pt = Hh.z[T], np.degrees(Hh.phi[T])
            pt = (pt - p0 + 180) % 360 - 180
            zt = zt - z0
            m = (zt.min(1) <= 0) & (zt.max(1) >= 0) & (pt.min(1) <= 0) & (pt.max(1) >= 0)
            best = None
            for t in np.where(m)[0]:
                A2 = np.array([[pt[t, 1] - pt[t, 0], pt[t, 2] - pt[t, 0]], [zt[t, 1] - zt[t, 0], zt[t, 2] - zt[t, 0]]])
                if abs(np.linalg.det(A2)) < 1e-14:
                    continue
                l1, l2 = np.linalg.solve(A2, -np.array([pt[t, 0], zt[t, 0]]))
                if l1 >= -1e-9 and l2 >= -1e-9 and l1 + l2 <= 1 + 1e-9:
                    X = (1 - l1 - l2) * Hh.pts[T[t, 0]] + l1 * Hh.pts[T[t, 1]] + l2 * Hh.pts[T[t, 2]]
                    if best is None:
                        best = X
            return best

        def too_close(h, c_surf, c_epi):
            d_endo, _ = SL[h].dist([c_surf], 2)
            d_epi = SE[h].dist([c_epi], 2)[0] if c_epi is not None else None
            for p in posn:
                if p['heart'] != h:
                    continue
                n = p['surface_node']
                if p['epi_start']:
                    if d_epi is not None and n in SE[h].loc and d_epi[SE[h].loc[n]] < 4.0:
                        return True
                elif n in SL[h].loc and d_endo[SL[h].loc[n]] < 4.0:
                    return True
            return False
        added = {r: {h: {t: 0 for t in ('T2', 'T4', 'T8')} for h in G.HEARTS} for r in REGS}
        log, fill_sites, n_order = [], {h: [] for h in G.HEARTS}, 0
        skipped = {'8.7': 0, '4mm': 0}
        final = dict(count0)
        cand_region_cache = {}
        for r in REGS:
            queues = {h: list(cands[h]) for h in G.HEARTS}
            while final[r] < 20 and any(queues.values()):
                for h in G.HEARTS:
                    if final[r] >= 20:
                        break
                    Hh = H[h]
                    while queues[h]:
                        t, i, z, p = queues[h].pop(0)
                        key = (h, t, i)
                        if key not in cand_region_cache:
                            X = nominal(h, z, p) if z <= 1.0 else None
                            if X is None:
                                cand_region_cache[key] = ('drop', None); drops['nominal_point_off_by_more_than_1.05mm_or_outside'] += 1
                                log.append({'region_turn': r, 'heart': h, 'tier': t, 'cand': i, 'z': z, 'phi_deg': p, 'outcome': 'dropped: no LV-endocardial triangle holds the nominal point'}); continue
                            dn = np.linalg.norm(Hh.pts[Hh.lv] - X, axis=1); k = int(np.argmin(dn))
                            if dn[k] > 1.05:
                                cand_region_cache[key] = ('drop', None); drops['nominal_point_off_by_more_than_1.05mm_or_outside'] += 1
                                log.append({'region_turn': r, 'heart': h, 'tier': t, 'cand': i, 'z': z, 'phi_deg': p, 'outcome': f'dropped: nearest LV-endocardial node {dn[k]:.2f} mm from the nominal point'}); continue
                            sn = int(Hh.lv[k])
                            sg, f_ = aha_fw(Hh.F, Hh.pts[[sn]])
                            cand_region_cache[key] = (region(int(sg[0]), f_[0], float(Hh.z[sn]), rule), sn)
                        rg, sn = cand_region_cache[key]
                        if rg != r:
                            continue
                        n_in, T = Hh.line(sn)
                        dE, iE = Hh.t_epi_fw.query(Hh.pts[sn] + T * n_in)
                        c_epi = int(Hh.epi_fw[iE]) if dE <= 1.5 else None
                        if too_close(h, sn, c_epi):
                            skipped['4mm'] += 1
                            log.append({'region_turn': r, 'heart': h, 'tier': t, 'cand': i, 'z': z, 'phi_deg': p, 'surface_node': sn, 'outcome': 'used up: within 4 mm of an existing position'}); continue
                        used0 = set(Hh.used)
                        nodes, Tw = Hh.place(sn)
                        if not (CAP[h].ok(nodes[0.9]) and CAP[h].ok(nodes[0.1])):
                            Hh.used = used0; skipped['8.7'] += 1
                            log.append({'region_turn': r, 'heart': h, 'tier': t, 'cand': i, 'z': z, 'phi_deg': p, 'surface_node': sn, 'outcome': 'used up: 8.7 capture failed'}); continue
                        n_order += 1
                        log.append({'region_turn': r, 'heart': h, 'tier': t, 'cand': i, 'z': z, 'phi_deg': p, 'surface_node': sn, 'outcome': f'added (order {n_order})',
                                    'wall_mm': round(float(Tw), 2), 'nodes': {'d90': int(nodes[0.9]), 'd10': int(nodes[0.1])}})
                        for dd in (0.9, 0.1):
                            n = nodes[dd]; sg2, f2 = aha_fw(Hh.F, Hh.pts[[n]])
                            rg2 = region(int(sg2[0]), f2[0], float(Hh.z[n]), rule)
                            sid = f'gate5fill52_{n_order:03d}_d{int(dd * 100)}'
                            sites.append({'heart': h, 'id': sid if ORDER == 'record' else f'gate5fill_{h}_{t}_{i:03d}_d{int(dd * 100)}', 'depth': dd, 'x': Hh.pts[n], 'origin': 'gate5fill',
                                          'region': rg2, 'order': n_order})
                            fill_sites[h].append({'id': sid, 'family': 'gate5fill', 'node': int(n), 'depth_target': dd, 'order_added': n_order, 'tier': t, 'candidate': i,
                                                  'nominal_z_phi': [z, p], 'surface_node': sn, 'wall_thickness_mm': round(float(Tw), 2), 'region_filled': r,
                                                  'region_of_site': rg2, 'aha_segment': int(sg2[0])})
                        posn.append({'heart': h, 'surface_node': sn, 'epi_start': False})
                        added[r][h][t] += 1
                        final, _ = pair_sites(sites)
                        break
        final, comp = pair_sites(sites)
        res.update({'matched_after_fill': final, 'matched_composition_after_fill': comp,
                    'positions_added_per_region': {r: int(sum(sum(v.values()) for v in added[r].values())) for r in REGS},
                    'positions_added_per_region_heart_tier': added, 'total_added_positions': int(sum(sum(sum(v.values()) for v in added[r].values()) for r in REGS)),
                    'regions_staying_under_20': [r for r in REGS if final[r] < 20], 'dropped': drops, 'skipped': skipped})
        res['total_added_beats'] = 2 * res['total_added_positions']
        out['rules'][rule] = res
        print(rule, json.dumps({k: v for k, v in res.items() if k != 'positions_added_per_region_heart_tier'}), flush=True)
    out['pool_reading'] = 'lock (item 5): v5.1 lv_free_wall + lv_vein_course + D22 summit; v5.1 lv_summit not pooled'
    out['existing_for_4mm_v51_summit'] = EXIST
    out['pairing_order'] = ORDER
    res = out['rules']['C6']
    res['candidate_log_in_order'] = log
    res['realised_ledger_total'] = {'base_with_D24 (record D24)': 1600, 'minus_the_old_fill_row': 12, 'fill_beats': res['total_added_beats'],
                                    'total': 1600 - 12 + res['total_added_beats'], 'before_the_RE+-only_CL600_subset': 1600 - 12 + res['total_added_beats'] - 27}
    if os.environ.get('G5_WRITE', '0') == '1':
        for h in G.HEARTS:
            G.dump({'heart': h, 'lock_sha256': G.LOCK_SHA, 'rule': 'D23 (adopted) with C65, D26, D22 option A; gate5fill52.py', 'pairing_order': ORDER,
                    'sites': fill_sites[h]}, os.path.join(G.REPO, 'data', 'biv', h, 'v52', 'gate5fill52.json'))
        G.dump(out, os.path.join(HERE, 'gate5fill52.json'))
    else:
        G.dump(out, os.path.join(G.RUN, f'gate5fill52_trial_{ORDER}.json'))


if __name__ == '__main__':
    main()
