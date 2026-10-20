"""Read-only preview (c) for proposed deviation D23 (lock thread, relayed 20 Oct 2026 22:12 UTC): the gate-5 recount as
matched positions (11.3 item 5) after C6, with the re-anchored summit positions, and D23's fill candidates. Report only;
nothing enters the manifest.

Pool (11.3 item 3): v5.1's LV free-wall, vein-course and summit positions plus the re-anchored summit positions. Two
summit scenarios, because D22 as proposed builds no bifurcation in 6G8DD8S5 and 7D98EVAR (preview_d22.py):
  'D22'   the D22 positions where they exist (Y5HYEDL4 only);
  'projB' the reported alternative (B projected onto the candidate quarter), all three hearts.
Region map: 11.3 item 2 with C6 (AHA 16 apical lateral = apical superior), at each position's surface node, v5.2 z.
Matching (11.3 item 5): per heart and region, each 90 % site in ascending site-id order takes the unused 10 % site of the
same region whose straight-line distance is nearest 18 mm inside 13-23 mm; the count is the 90 % sites with a partner,
pooled over the hearts.
D23 candidates, per heart: v5.1's own grid rule (lv_start at (z level, phi) on the LV endocardium, v5.1's transmural line,
the 10 % and 90 % depths), tier 1 at phi halfway between v5.1's neighbouring free-wall phi values on each v5.1 level,
tier 2 a quarter and three quarters of the way, tier 3 at the levels halfway between v5.1's (0.375, 0.625) with the phi
values v5.1 used on the two neighbouring levels; kept only if inside a gated region and not within 1.05 mm of an existing
position's surface node; candidate id = order (tier, level, phi). Fill: per region short of 20, one candidate at a time
in ascending id, rotating Y5HYEDL4, 6G8DD8S5, 7D98EVAR, re-pairing after each, until 20 or the candidates run out.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_d23.py
"""
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_pts, read_vtx                                                       # noqa: E402

FAM = ('lv_free_wall', 'lv_vein_course', 'lv_summit')
SUP, INF = {1, 7, 13, 6, 12, 16}, {4, 10, 15, 5, 11}
REGS = ['basal_superior', 'apical_superior', 'basal_inferior', 'apical_inferior']
LEVELS = (0.25, 0.50, 0.75)
STEP, OUT_TOL = 0.2, 0.9


def region(seg, z):
    if seg in SUP:
        return 'basal_superior' if z >= 0.55 else 'apical_superior'
    if seg in INF:
        return 'basal_inferior' if z >= 0.55 else 'apical_inferior'
    return None


class Heart:
    def __init__(self, h):
        self.h = h
        V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces')
        self.pts = read_pts(os.path.join(V, 'biv52')) / 1e3
        self.z, self.phi, self.v = (np.loadtxt(os.path.join(V, 'uvc', n + '.dat')) for n in ('z', 'phi', 'v'))
        self.lv, self.epi = read_vtx(os.path.join(S, 'lv_endo.vtx')), read_vtx(os.path.join(S, 'epi.vtx'))
        self.tree = cKDTree(self.pts)
        surf = lambda n: np.loadtxt(os.path.join(S, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
        fx = self.pts[np.vstack([surf(n) for n in ('lv_endo', 'rv_endo', 'epi')])]
        self.fn = np.cross(fx[:, 1] - fx[:, 0], fx[:, 2] - fx[:, 0]); self.t_fc = cKDTree(fx.mean(1))
        self.epi_fw = self.epi[self.v[self.epi] == 0]; self.t_epi_fw = cKDTree(self.pts[self.epi_fw])
        self.F = Q.AHA.Frame(h)
        self.used = set()

    def inside(self, x):
        return self.tree.query(x)[0] <= OUT_TOL

    def line(self, p):
        idx = self.t_fc.query_ball_point(self.pts[p], 4.0)
        nv = self.fn[idx]; nv = nv * np.sign(nv @ nv[0])[:, None]
        n = nv.sum(0); n /= np.linalg.norm(n)
        if not self.inside(self.pts[p] + n):
            n = -n
        s, out, last = 0.0, 0, 0.0
        while s < 60:
            s += STEP
            if self.inside(self.pts[p] + s * n):
                out, last = 0, s
            else:
                out += 1
                if out >= 2:
                    break
        return n, last

    def free_wall_line(self, p):
        d, idx = self.t_epi_fw.query(self.pts[p], k=200)
        for dd, i in zip(d, idx):
            q = self.epi_fw[i]
            seg = self.pts[p] + np.linspace(0, 1, max(3, int(dd / STEP)))[:, None] * (self.pts[q] - self.pts[p])
            dist, nn = self.tree.query(seg)
            if (dist <= OUT_TOL).all() and (self.v[nn] == 0).all():
                return (self.pts[q] - self.pts[p]) / dd, float(dd)
        return None, None

    def lv_start(self, lev, ph):
        score = np.abs(self.z[self.lv] - lev) * 10 + np.abs(np.angle(np.exp(1j * (self.phi[self.lv] - np.radians(ph)))))
        return int(self.lv[np.argmin(score)])

    def place(self, p):
        n_in, T = self.line(p)
        end = self.pts[p] + T * n_in
        d_epi, i = self.t_epi_fw.query(end)
        if not (d_epi <= 1.5 and self.v[self.epi_fw[i]] == 0):
            n2, T2 = self.free_wall_line(p)
            if n2 is not None:
                n_in, T = n2, T2
        out = {}
        for dt in (0.1, 0.9):
            node = next(int(c) for c in self.tree.query(self.pts[p] + dt * T * n_in, k=12)[1] if int(c) not in self.used)
            self.used.add(node); out[dt] = node
        return out, T


def pair(pos):
    """pos: list of dicts with region, id90, n90, id10, n10, pts. Returns matched 90 % ids per region."""
    res = {}
    for r in REGS:
        P = [p for p in pos if p['region'] == r]
        tens = sorted([(p['id10'], p['x10']) for p in P if p['id10']], key=lambda t: t[0])
        used = set(); m = 0
        for p in sorted(P, key=lambda t: t['id90']):
            best, bd = None, None
            for tid, x in tens:
                if tid in used:
                    continue
                d = float(np.linalg.norm(p['x90'] - x))
                if 13.0 <= d <= 23.0 and (bd is None or abs(d - 18) < abs(bd - 18)):
                    best, bd = tid, d
            if best:
                used.add(best); m += 1
        res[r] = m
    return res


def main():
    H = {h: Heart(h) for h in G.HEARTS}
    out = {'lock_sha256': G.LOCK_SHA, 'scenarios': {}}
    base_pos, cands = {}, {}
    for h, Hh in H.items():
        sites = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
        Hh.used |= {int(s['node']) for s in sites}
        Hh.used |= {int(s['node']) for s in json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'v52', 'sites52.json')))['new_sites']}
        posd = {}
        for s in sites:
            if s['family'] in FAM:
                posd.setdefault((s['family'], s['position'], s['level_z']), {})[s['depth_target']] = s
        rows = []
        sn = np.array([int(v[0.9]['surface_node']) for v in posd.values()])
        seg = Q.aha_labels(Hh.F, Hh.pts[sn])
        for (k, v), n, sg in zip(posd.items(), sn, seg):
            rows.append({'heart': h, 'family': k[0], 'id90': v[0.9]['id'], 'x90': Hh.pts[int(v[0.9]['node'])],
                         'id10': v[0.1]['id'] if 0.1 in v else None, 'x10': Hh.pts[int(v[0.1]['node'])] if 0.1 in v else None,
                         'surface_node': int(n), 'region': region(int(sg), float(Hh.z[n]))})
        base_pos[h] = rows
        # D23 candidates
        fw = {}
        for s in sites:
            if s['family'] == 'lv_free_wall':
                fw.setdefault(s['level_z'], set()).add(int(s['position'].replace('phi', '')))
        clist = []
        for lev in LEVELS:
            ph = sorted({(p % 360) for p in fw[lev]})
            pairs_ = list(zip(ph[:-1], ph[1:]))
            for a, b in pairs_:
                clist.append((1, lev, (a + b) / 2))
        for lev in LEVELS:
            ph = sorted({(p % 360) for p in fw[lev]})
            for a, b in zip(ph[:-1], ph[1:]):
                clist += [(2, lev, a + (b - a) / 4), (2, lev, a + 3 * (b - a) / 4)]
        for lo, hi in ((0.25, 0.5), (0.5, 0.75)):
            for p in sorted({(x % 360) for x in fw[lo] | fw[hi]}):
                clist.append((3, (lo + hi) / 2, p))
        clist = sorted(clist)
        existing = np.array([r['surface_node'] for r in rows])
        cc = []
        for cid, (tier, lev, ph) in enumerate(clist):
            p = Hh.lv_start(lev, ph if ph <= 180 else ph - 360)
            if np.linalg.norm(Hh.pts[existing] - Hh.pts[p], axis=1).min() <= 1.05:
                cc.append({'cid': cid, 'tier': tier, 'z_level': lev, 'phi': ph, 'surface_node': p, 'kept': False, 'why': 'coincident'}); continue
            sg = int(Q.aha_labels(Hh.F, Hh.pts[[p]])[0]); rg = region(sg, float(Hh.z[p]))
            if rg is None:
                cc.append({'cid': cid, 'tier': tier, 'z_level': lev, 'phi': ph, 'surface_node': p, 'aha': sg, 'kept': False, 'why': 'no gated region'}); continue
            nodes, T = Hh.place(p)
            cc.append({'cid': cid, 'tier': tier, 'z_level': lev, 'phi': ph, 'surface_node': p, 'aha': sg, 'region': rg, 'kept': True,
                       'wall_mm': round(T, 2), 'n90': nodes[0.9], 'n10': nodes[0.1],
                       'id90': f'gate5fill_{h}_c{cid:02d}_d90', 'id10': f'gate5fill_{h}_c{cid:02d}_d10'})
        cands[h] = cc
    # summit scenarios
    for scen in ('D22', 'projB'):
        pos = []
        for h, Hh in H.items():
            pos += base_pos[h]
            f = os.path.join(HERE, f'preview_d22{"" if scen == "D22" else "_projB"}_{h}.json')
            d = json.load(open(f))
            if 'stop' in d:
                continue
            sites = {s['id']: s for s in d['sites (preview, not in the manifest)']}
            for nm, pz in d['positions'].items():
                if not pz:
                    continue
                n = pz['surface_node']
                sg = int(Q.aha_labels(Hh.F, Hh.pts[[n]])[0])
                s9, s1 = sites[f'lv_summit52_{nm}_d90'], sites[f'lv_summit52_{nm}_d10']
                pos.append({'heart': h, 'family': 'summit_reanchored', 'id90': s9['id'] + '_' + h, 'x90': Hh.pts[s9['node']],
                            'id10': s1['id'] + '_' + h, 'x10': Hh.pts[s1['node']], 'surface_node': n, 'region': region(sg, float(Hh.z[n]))})
        def per_heart(P):
            tot = {r: 0 for r in REGS}
            for h in G.HEARTS:
                for r, m in pair([p for p in P if p['heart'] == h]).items():
                    tot[r] += m
            return tot
        count0 = per_heart(pos)
        positions_by_region = {r: sum(1 for p in pos if p['region'] == r) for r in REGS}
        added = {r: [] for r in REGS}; final = dict(count0); ran_out = {}
        P = list(pos)
        for r in REGS:
            queues = {h: [c for c in cands[h] if c.get('kept') and c['region'] == r] for h in G.HEARTS}
            while final[r] < 20 and any(queues.values()):
                for h in G.HEARTS:
                    if final[r] >= 20 or not queues[h]:
                        continue
                    c = queues[h].pop(0)
                    P.append({'heart': h, 'family': 'gate5fill', 'id90': c['id90'], 'x90': H[h].pts[c['n90']], 'id10': c['id10'],
                              'x10': H[h].pts[c['n10']], 'surface_node': c['surface_node'], 'region': r})
                    added[r].append(c['id90'].replace('_d90', ''))
                    final = per_heart(P)
            ran_out[r] = bool(final[r] < 20)
        out['scenarios'][scen] = {'positions_by_region (before matching)': positions_by_region,
                                  'matched_count_before_fill': count0, 'additions_per_region': {r: len(v) for r, v in added.items()},
                                  'added_positions': added, 'matched_count_after_fill': final,
                                  'regions_that_run_out (stay under 20)': [r for r, v in ran_out.items() if v],
                                  'added_beats': 2 * sum(len(v) for v in added.values())}
    out['candidates'] = {h: [{k: v for k, v in c.items() if k not in ('n90', 'n10')} for c in cc] for h, cc in cands.items()}
    out['candidates_kept_per_region'] = {h: {r: sum(1 for c in cc if c.get('kept') and c['region'] == r) for r in REGS} for h, cc in cands.items()}
    G.dump(out, os.path.join(HERE, 'preview_d23.json'))
    print(json.dumps({k: v for k, v in out.items() if k != 'candidates'}, indent=1, default=str)[:4000])


if __name__ == '__main__':
    main()
