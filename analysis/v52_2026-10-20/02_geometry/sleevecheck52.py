"""v5.2 step 2d acceptance (LOCK.md 8.6, 15.2 step 2d): the sleeve thickness profile and built heights, measured.

The thickness rule is 2.0 / 1.7 / 1.0 mm at 25 / 50 / 75 % of the 4.0 mm sleeve (heights 1.0 / 2.0 / 3.0 mm above the
pulmonary mid-plane ring), the whole wall where the tag-6 wall is thinner (8.6), tolerance one element (1.05 mm).
Measured per 5-deg bin that carries sleeve muscle, in 1 mm height bands centred on those heights:
  achieved thickness = the largest distance from the lumen (nearest luminal-face node of the pulmonary wall) of any node
    of a re-tagged element in the band (nodes, not centroids: a centroid sits about half an element inside);
  local wall = the same for every node of the original tag-6 wall in the band;
  expected = min(rule, local wall); a band passes if |achieved - expected| <= 1.05 mm.
Built height: per sinus centre (pulmonary frame, posterior 0 deg, +-120 deg) and per bin, max(existing, 4.0 mm) against
the achieved height (highest node of RV muscle, existing or re-tagged, above the mid-plane ring).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/sleevecheck52.py [HEART ...]
"""
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import outflow52 as O                                                                       # noqa: E402

RULE = {0.25: 2.0, 0.50: 1.7, 0.75: 1.0}
TOL = 1.05


def run(h):
    P, E, tag = G.load_full(h)
    pv, _ = G.pulmonary_frame(P, E, tag)
    z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
    sid = z['sleeve_elements']
    lum, _ = O.luminal_nodes(P, E, tag, pv, 6)
    tl = cKDTree(P[lum])
    rr = float(np.median(pv.r(P[pv.ring])))
    e6 = np.where(tag == 6)[0]
    # nodes of the original wall and of the sleeve, with depth, height and angle
    n6 = np.unique(E[e6]); d6 = tl.query(P[n6])[0]; h6 = pv.h(P[n6]); t6 = pv.theta(P[n6])
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'sleeve_elements': int(len(sid)), 'bands': [], 'per_sinus': {}}
    if len(sid):
        ns = np.unique(E[sid]); ds = tl.query(P[ns])[0]; hs = pv.h(P[ns]); ts = pv.theta(P[ns])
        bins = np.unique((pv.theta(P[E[sid]].mean(1)) // 5).astype(int))
        for b in bins:
            ib6 = (t6 >= 5 * b) & (t6 < 5 * b + 5); ibs = (ts >= 5 * b) & (ts < 5 * b + 5)
            for f, rule in RULE.items():
                hc = f * O.SLEEVE_H
                m6, ms = ib6 & (np.abs(h6 - hc) <= 0.5), ibs & (np.abs(hs - hc) <= 0.5)
                if not ms.any():
                    rec['bands'].append({'bin_deg': 5 * int(b), 'fraction': f, 'sleeve_nodes': 0}); continue
                wall = float(d6[m6].max()) if m6.any() else np.nan
                ach = float(ds[ms].max())
                exp_ = min(rule, wall) if np.isfinite(wall) else rule
                rec['bands'].append({'bin_deg': 5 * int(b), 'fraction': f, 'rule_mm': rule, 'local_wall_mm': round(wall, 2),
                                     'expected_mm': round(exp_, 2), 'achieved_mm': round(ach, 2), 'pass': bool(abs(ach - exp_) <= TOL)})
    ev = [b for b in rec['bands'] if 'pass' in b]
    rec['bands_evaluated'] = len(ev)
    rec['bands_pass'] = int(sum(b['pass'] for b in ev))
    rec['thickness_acceptance'] = bool(all(b['pass'] for b in ev))
    rec['failing_bands'] = [b for b in ev if not b['pass']]
    # built height per sinus centre and per bin: highest RV-muscle node (existing or re-tagged) above the ring
    musc = np.isin(tag, G.RV_GROUP)
    if len(sid):
        musc = musc.copy(); musc[sid] = True
    cen = P[E].mean(1)
    im = np.where(musc & (pv.r(cen) < rr + 6) & (pv.h(cen) > -6) & (pv.h(cen) < 30))[0]
    nm = np.unique(E[im]); hm, tm = pv.h(P[nm]), pv.theta(P[nm])
    im0 = np.where(np.isin(tag, G.RV_GROUP) & (pv.r(cen) < rr + 6) & (pv.h(cen) > -6) & (pv.h(cen) < 30))[0]
    n0 = np.unique(E[im0]); h0, t0 = pv.h(P[n0]), pv.theta(P[n0])
    for k, c in {'posterior': 0.0, 'sinus_+120': 120.0, 'sinus_-120': 240.0}.items():
        a = np.abs((tm - c + 180) % 360 - 180) <= 2.5; a0 = np.abs((t0 - c + 180) % 360 - 180) <= 2.5
        ex = float(h0[a0].max()) if a0.any() else np.nan
        got = float(hm[a].max()) if a.any() else np.nan
        rec['per_sinus'][k] = {'nadir': 'mid-plane ring point at the sinus centre (D13)', 'ring_node': pv.ring_point(c),
                               'existing_height_mm (highest RV node, +-2.5 deg)': round(ex, 2), 'rule_max(existing, 4.0)_mm': round(max(ex, O.SLEEVE_H), 2),
                               'achieved_height_mm': round(got, 2), 'within_one_element': bool(abs(got - max(ex, O.SLEEVE_H)) <= TOL)}
    short = []
    for b in range(72):
        a = (tm >= 5 * b) & (tm < 5 * b + 5)
        if not a.any() or hm[a].max() < O.SLEEVE_H - TOL:
            short.append(5 * b)
    rec['bins_where_achieved_height_is_below_4.0_minus_one_element'] = short
    rec['built_height_acceptance'] = bool(not short and all(v['within_one_element'] for v in rec['per_sinus'].values()))
    G.dump(rec, os.path.join(HERE, f'sleevecheck52_{h}.json'))
    print(h, 'thickness bands', rec['bands_pass'], '/', rec['bands_evaluated'], 'pass:', rec['thickness_acceptance'],
          '| per sinus', {k: (v['rule_max(existing, 4.0)_mm'], v['achieved_height_mm']) for k, v in rec['per_sinus'].items()},
          '| bins short of 4.0 mm:', short, flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
