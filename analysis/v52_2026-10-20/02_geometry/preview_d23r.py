"""Read-only preview for revised D23 (lock thread, relayed 20 Oct 2026 22:29 UTC): gate-5 fill on v5.1's grid rule in tiers
T2, T4, T8. Report only; nothing enters the manifest.

Pool and matching as preview_d23.py (C6 map; 11.3 item 5 within each heart and region, pooled), with the projB summit
positions (revised D22). Candidates per heart: v5.1's free-wall z levels 0.25 / 0.5 / 0.75 with the end intervals 0-0.25
and 0.75-1 (ends excluded), and v5.1's own free-wall phi values pooled over levels for that heart (Y5HYEDL4 -150, -120,
60, 120, 180; 6G8DD8S5 -120, 60, 120, 180; 7D98EVAR -135, -120, 60, 120, 180 deg; around the circle); tier Tk splits
every z interval and every phi interval into k equal parts and takes the (z, phi) combinations of those points with the
v5.1 values that are not v5.1 positions and not in an earlier tier; candidate id = order of (z, phi) within the tier.
A candidate is kept for a region if its surface node (v5.1's lv_start at (z, phi) on the v5.2 UVC) lies in that region
and it is at least 4 mm from every existing and already-added position, measured on the surface (2-ring geodesic on
the LV endocardium between surface nodes; positions that start on the epicardium (summit, vein course) are compared
with the candidate's epicardial line end on the epicardium; mine); a candidate whose 90 % or 10 % site fails 8.7
(capture >= 4 nodes on the cut mesh) is skipped and counted. Order: tiers in order, ascending id, one at a time rotating
Y5HYEDL4, 6G8DD8S5, 7D98EVAR, pairing re-run after each; a region stops at 20 matched. No cap.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_d23r.py
"""
import json
import os
import sys

import numpy as np
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import preview_d23 as D                                                                     # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402
from cut52 import adjacency                                                                 # noqa: E402

R34 = Q.S52.R34
ZLEV = [0.0, 0.25, 0.5, 0.75, 1.0]


class Capture:
    def __init__(self, h, Pm):
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
        self.Pc = read_pts(os.path.join(V, 'biv52cut')) / 1e3; Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
        self.A = adjacency(Ec, len(self.Pc)); self.tc = cKDTree(self.Pc)
        fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
        src = np.load(os.path.join(V, 'cut_dup52.npy'))
        dupof = np.full(len(Pm), -1); dupof[src[len(Pm):]] = np.arange(len(Pm), len(self.Pc))
        self.nonex = np.zeros(len(self.Pc), bool); self.nonex[fib] = True; self.nonex[dupof[fib][dupof[fib] >= 0]] = True

    def ok(self, n):
        ball = np.array(self.tc.query_ball_point(self.Pc[n], 1.5 - 1e-9))
        ex = ball[~self.nonex[ball]]
        if n not in set(ex.tolist()):
            return False
        _, lb = connected_components(self.A[ex][:, ex], directed=False)
        return int((lb == lb[np.where(ex == n)[0][0]]).sum()) >= 4


def main():
    H = {h: D.Heart(h) for h in G.HEARTS}
    out = {'lock_sha256': G.LOCK_SHA, 'phi_values_used': {}, 'tiers': {}, 'per_region': {}}
    pos, cands, SL, SE, CAP, epi_of = [], {}, {}, {}, {}, {}
    for h, Hh in H.items():
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces')
        sites = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
        Hh.used |= {int(s['node']) for s in sites}
        Hh.used |= {int(s['node']) for s in json.load(open(os.path.join(V, 'sites52.json')))['new_sites']}
        tri = lambda n: np.loadtxt(os.path.join(S, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
        SL[h], SE[h] = R34.Surf(Hh.pts, tri('lv_endo')), R34.Surf(Hh.pts, tri('epi'))
        CAP[h] = Capture(h, Hh.pts)
        posd = {}
        for s in sites:
            if s['family'] in D.FAM:
                posd.setdefault((s['family'], s['position'], s['level_z']), {})[s['depth_target']] = s
        sn = np.array([int(v[0.9]['surface_node']) for v in posd.values()])
        seg = Q.aha_labels(Hh.F, Hh.pts[sn])
        for (k, v), n, sg in zip(posd.items(), sn, seg):
            pos.append({'heart': h, 'family': k[0], 'id90': v[0.9]['id'], 'x90': Hh.pts[int(v[0.9]['node'])], 'id10': v[0.1]['id'] if 0.1 in v else None,
                        'x10': Hh.pts[int(v[0.1]['node'])] if 0.1 in v else None, 'surface_node': int(n), 'epi_start': k[0] != 'lv_free_wall',
                        'region': D.region(int(sg), float(Hh.z[n]))})
        d22 = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
        ss = {s['id']: s for s in d22['sites (preview, not in the manifest)']}
        for nm, pz in d22['positions'].items():
            n = pz['surface_node']; sg = int(Q.aha_labels(Hh.F, Hh.pts[[n]])[0])
            s9, s1 = ss[f'lv_summit52_{nm}_d90'], ss[f'lv_summit52_{nm}_d10']
            pos.append({'heart': h, 'family': 'summit_reanchored', 'id90': s9['id'] + '_' + h, 'x90': Hh.pts[s9['node']], 'id10': s1['id'] + '_' + h,
                        'x10': Hh.pts[s1['node']], 'surface_node': n, 'epi_start': True, 'region': D.region(sg, float(Hh.z[n]))})
        # candidate grid
        fw = {}
        for s in sites:
            if s['family'] == 'lv_free_wall':
                fw.setdefault(s['level_z'], set()).add(int(s['position'].replace('phi', '')))
        phis = sorted({p % 360 for v in fw.values() for p in v})
        out['phi_values_used'][h] = sorted(((p + 180) % 360) - 180 for p in phis)
        existing = {(lev, p % 360) for lev, v in fw.items() for p in v}
        seen = set(existing)
        tiers = {}
        for k in (2, 4, 8):
            zs = sorted({round(a + (b - a) * i / k, 6) for a, b in zip(ZLEV[:-1], ZLEV[1:]) for i in range(0, k + 1)} - {0.0, 1.0})
            ring = phis + [phis[0] + 360]
            ps = sorted({round((a + (b - a) * i / k) % 360, 6) for a, b in zip(ring[:-1], ring[1:]) for i in range(0, k + 1)})
            combos = [(z, p) for z in zs for p in ps if (z, p) not in seen]
            seen |= set(combos)
            tiers[f'T{k}'] = combos
        cands[h] = tiers
        out['tiers'][h] = {t: len(v) for t, v in tiers.items()}
    def matched(P):
        tot = {r: 0 for r in D.REGS}
        for h in G.HEARTS:
            for r, m in D.pair([p for p in P if p['heart'] == h]).items():
                tot[r] += m
        return tot
    count0 = matched(pos)
    out['matched_before_fill'] = count0
    out['positions_before_fill'] = {r: sum(1 for p in pos if p['region'] == r) for r in D.REGS}

    def too_close(h, c_surf, c_epi):
        """True if within 4 mm (surface) of an existing or added position of heart h."""
        Hh = H[h]
        d_endo, _ = SL[h].dist([c_surf], 2)
        d_epi = SE[h].dist([c_epi], 2)[0] if c_epi is not None else None
        for p in pos:
            if p['heart'] != h:
                continue
            n = p['surface_node']
            if p['epi_start']:
                if d_epi is not None and n in SE[h].loc and d_epi[SE[h].loc[n]] < 4.0:
                    return True
            elif n in SL[h].loc and d_endo[SL[h].loc[n]] < 4.0:
                return True
        return False
    skipped = {'8.7': [], '4mm': [], 'off_region_or_septal': 0}
    added = {r: {h: {t: 0 for t in ('T2', 'T4', 'T8')} for h in G.HEARTS} for r in D.REGS}
    final = dict(count0)
    for r in D.REGS:
        queues = {h: [(t, i, z, p) for t in ('T2', 'T4', 'T8') for i, (z, p) in enumerate(cands[h][t])] for h in G.HEARTS}
        while final[r] < 20 and any(queues.values()):
            for h in G.HEARTS:
                if final[r] >= 20:
                    break
                Hh = H[h]
                while queues[h]:
                    t, i, z, p = queues[h].pop(0)
                    sn = Hh.lv_start(z, p if p <= 180 else p - 360)
                    sg = int(Q.aha_labels(Hh.F, Hh.pts[[sn]])[0])
                    if D.region(sg, float(Hh.z[sn])) != r:
                        continue
                    n_in, T = Hh.line(sn)
                    dE, iE = Hh.t_epi_fw.query(Hh.pts[sn] + T * n_in)
                    c_epi = int(Hh.epi_fw[iE]) if dE <= 1.5 else None
                    if too_close(h, sn, c_epi):
                        skipped['4mm'].append(f'{h} {t} #{i} z {z} phi {p}'); continue
                    used0 = set(Hh.used)
                    nodes, Tw = Hh.place(sn)
                    if not (CAP[h].ok(nodes[0.9]) and CAP[h].ok(nodes[0.1])):
                        Hh.used = used0
                        skipped['8.7'].append(f'{h} {t} #{i} z {z} phi {p}'); continue
                    pos.append({'heart': h, 'family': 'gate5fill', 'id90': f'gate5fill_{h}_{t}_{i:03d}_d90', 'x90': Hh.pts[nodes[0.9]],
                                'id10': f'gate5fill_{h}_{t}_{i:03d}_d10', 'x10': Hh.pts[nodes[0.1]], 'surface_node': sn, 'epi_start': False, 'region': r,
                                'z': z, 'phi': p, 'tier': t})
                    added[r][h][t] += 1
                    final = matched(pos)
                    break
        out['per_region'][r] = {'matched_reached': final[r], 'positions_added_per_heart_and_tier': added[r],
                                'positions_added': int(sum(sum(v.values()) for v in added[r].values())), 'stays_under_20': bool(final[r] < 20)}
    out['matched_after_fill'] = final
    out['total_added_positions'] = int(sum(v['positions_added'] for v in out['per_region'].values()))
    out['total_added_beats'] = 2 * out['total_added_positions']
    out['skipped'] = {'for_8.7_capture': len(skipped['8.7']), 'for_the_4mm_rule': len(skipped['4mm']), 'list_8.7': skipped['8.7'], 'list_4mm_first_50': skipped['4mm'][:50]}
    out['added_positions'] = [{k: (v if not isinstance(v, np.ndarray) else None) for k, v in p.items() if k not in ('x90', 'x10')} for p in pos if p['family'] == 'gate5fill']
    G.dump(out, os.path.join(HERE, 'preview_d23r.json'))
    print(json.dumps({k: v for k, v in out.items() if k not in ('added_positions', 'skipped')}, indent=1, default=str)[:3500])
    print('skipped', {k: v for k, v in out['skipped'].items() if not k.startswith('list')})


if __name__ == '__main__':
    main()
