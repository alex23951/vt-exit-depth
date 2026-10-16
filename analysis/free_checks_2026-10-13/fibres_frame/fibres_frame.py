#!/usr/bin/env python
"""
Frame-exact fibre check at the RVOT and RV free-wall sites, 13 Oct 2026 (coordinator brief 00:12 UTC; read only).

For the elements around each site node (RVOT 10 / 50 / 75 / 90 %, RV free wall 10 / 50 / 90 %) in all three hearts:
  - recompute 04_fibres.py's own frame and fibre with its functions (elem_grad, axis, orient, bislerp) and check that the
    stored bivF.lon fibre is reproduced;
  - measure the stored fibre in the rule's outward frame: e1 = unit(gpsi) (longitudinal: w grad psi_basal + (1 - w)
    grad psi_OT), e2 = grad phi_epi orthogonalised (outward transmural), e0 = e1 x e2 (circumferential): helix angle
    alpha = atan2(f.e1, f.e0) folded to (-90, 90] (0 = circumferential, +-90 = along e1), out-of-plane = asin|f.e2|;
  - the rule's intended angle at that element, alpha_int = a_endo(w) (1 - phi_epi) + a_epi(w) phi_epi, with a_endo(w) =
    60 w + 90 (1 - w), a_epi(w) = -60 w; Doste 2019 targets in the outflow tract: endo 90 (along the OT axis), epi 0;
  - frame diagnostics: angle between e1 and the geometric outflow axis (pulmonary-rim normal, used in the first check),
    between the endocardial transmural direction the rule uses (-grad phi_lv or +grad phi_rv, by d) and grad phi_epi,
    and the septal split d, w, phi_epi at the element.
Output: fibres_frame.csv, summary.txt (this folder).
"""

import importlib.util
import json
import os
import sys

os.environ.setdefault('HEART', 'Y5HYEDL4')
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402

spec = importlib.util.spec_from_file_location('fib', os.path.join(B, '04_fibres.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def fold(a):
    a = (a + 90) % 180 - 90
    return np.where(a == -90, 90, a)


rows = []
for h in HEARTS:
    pts = pd.read_csv(hd(h, 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    E = pd.read_csv(hd(h, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    lon = pd.read_csv(hd(h, 'bivF.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    lap = {n: np.loadtxt(hd(h, 'laplace', n + '.dat')) for n in ('w', 'phi_lv', 'phi_rv', 'phi_epi', 'basal', 'ot')}
    rim = pts[np.loadtxt(hd(h, 'surfaces', 'pv_rim.vtx'), skiprows=2, dtype=np.int64)]
    ax = np.linalg.svd(rim - rim.mean(0))[2][-1]
    S = json.load(open(hd(h, 'sites.json')))
    sel = [s for s in S if (s['family'] == 'rvot') or (s['family'] == 'rv_free_wall' and s['depth_target'] in (0.1, 0.5, 0.9))]
    for s in sel:
        ids = np.where((E == int(s['node'])).any(1))[0]
        Es = E[ids]
        em = lambda u: u[Es].mean(1)
        w = np.clip(em(lap['w']), 0, 1)
        plv, prv, pepi = (np.clip(em(lap[n]), 0, 1) for n in ('phi_lv', 'phi_rv', 'phi_epi'))
        d = prv / np.maximum(plv + prv, 1e-9)
        g = {n: F.elem_grad(pts, Es, lap[n]) for n in ('basal', 'ot', 'phi_lv', 'phi_rv', 'phi_epi')}
        gpsi = w[:, None] * F.unit(g['basal']) + (1 - w[:, None]) * F.unit(g['ot'])
        a_endo = np.radians(F.A_ENDO * w + F.A_OT_ENDO * (1 - w)); a_epi = np.radians(F.A_EPI * w + F.A_OT_EPI * (1 - w))
        a_s = a_endo * (1 - d) - a_endo * d
        a_w = a_endo * (1 - pepi) + a_epi * pepi
        Q_lv = F.orient(F.axis(gpsi, -g['phi_lv']), a_s); Q_rv = F.orient(F.axis(gpsi, g['phi_rv']), a_s)
        Q = F.bislerp(F.bislerp(Q_lv, Q_rv, d), F.orient(F.axis(gpsi, g['phi_epi']), a_w), pepi)
        f_rule = F.unit(Q[:, :, 0])
        f = F.unit(lon[ids, :3])
        fr = F.axis(gpsi, g['phi_epi'])                                    # columns e0, e1, e2 (outward)
        e0, e1, e2 = fr[:, :, 0], fr[:, :, 1], fr[:, :, 2]
        alpha = fold(np.degrees(np.arctan2(np.sum(f * e1, 1), np.sum(f * e0, 1))))
        oop = np.degrees(np.arcsin(np.clip(np.abs(np.sum(f * e2, 1)), 0, 1)))
        a_int = fold(np.degrees(a_endo) * (1 - pepi) + np.degrees(a_epi) * pepi)
        tm_endo = np.where(d[:, None] > 0.5, F.unit(g['phi_rv']), -F.unit(g['phi_lv']))   # rule's endo transmural axis
        rows.append({'heart': h, 'id': s['id'], 'family': s['family'], 'depth': s['depth_target'], 'n_elem': len(ids),
                     'w': float(np.median(w)), 'phi_epi': float(np.median(pepi)), 'd': float(np.median(d)),
                     'reproduced_deg': float(np.median(np.degrees(np.arccos(np.clip(np.abs(np.sum(f * f_rule, 1)), 0, 1))))),
                     'alpha_deg': float(np.median(alpha)), 'alpha_intended_deg': float(np.median(a_int)),
                     'alpha_minus_intended': float(np.median(fold(alpha - a_int))), 'out_of_plane_deg': float(np.median(oop)),
                     'e1_vs_pv_axis_deg': float(np.median(np.degrees(np.arccos(np.clip(np.abs(F.unit(gpsi) @ ax), 0, 1))))),
                     'endo_vs_epi_transmural_deg': float(np.median(np.degrees(np.arccos(np.clip(np.sum(tm_endo * F.unit(g['phi_epi']), 1), -1, 1))))),
                     'grad_ot_vs_basal_deg': float(np.median(np.degrees(np.arccos(np.clip(np.abs(np.sum(F.unit(g['ot']) * F.unit(g['basal']), 1)), 0, 1)))))})
D = pd.DataFrame(rows).round(1)
D.to_csv(os.path.join(HERE, 'fibres_frame.csv'), index=False)
G = D.groupby(['heart', 'family', 'depth'])[['w', 'phi_epi', 'd', 'reproduced_deg', 'alpha_deg', 'alpha_intended_deg', 'alpha_minus_intended',
                                             'out_of_plane_deg', 'e1_vs_pv_axis_deg', 'endo_vs_epi_transmural_deg', 'grad_ot_vs_basal_deg']].median().round(1)
txt = G.to_string()
open(os.path.join(HERE, 'summary.txt'), 'w').write(txt + '\n')
print(txt)
