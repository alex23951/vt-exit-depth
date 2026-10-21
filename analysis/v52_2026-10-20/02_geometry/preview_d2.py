"""Read-only preview P1 (d2) (lock thread, relayed 21 Oct 2026 02:13 UTC): on the LV side, the angle between l built by
fibres_fix.py's rule with w.dat (02_laplace's Doste weight, both ventricles) and the same rule with w_LV (the LV-only
weight) in its place; converged fields of previews2_fields.py; over LV-side elements and at the gate-1, 3, 5 and 8
stimulus nodes (v5.1 sites of the LV families, the cusp52 sites, the projB summit sites). Report only.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_d2.py
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402

FF = Q.FF
unit = lambda v: v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-30)
out = {'lock_sha256': G.LOCK_SHA}
for h in G.HEARTS:
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); cv = os.path.join(G.RUN, h, 'converged')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, _ = read_elem(os.path.join(V, 'biv52'))
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv, prv = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv, E[:nb]) / np.maximum(em(plv, E[:nb]) + em(prv, E[:nb]), 1e-9)
    LV = np.r_[d51 <= 0.5, np.zeros(len(E) - nb, bool)]
    ix = np.where(LV)[0]; Ex = E[ix]
    F = {n: np.load(os.path.join(cv, n + '.npy')) for n in ('w', 'basal', 'ot_lv', 'ot_rv', 'phi_lv', 'phi_rv', 'w_LV')}
    d = em(F['phi_rv'], Ex) / np.maximum(em(F['phi_lv'], Ex) + em(F['phi_rv'], Ex), 1e-9)
    gb = unit(FF.elem_grad(P, Ex, F['basal']))
    got = np.where((d > 0.5)[:, None], unit(FF.elem_grad(P, Ex, F['ot_rv'])), unit(FF.elem_grad(P, Ex, F['ot_lv'])))
    w1 = em(F['w'], Ex); w2 = np.clip(np.nanmean(F['w_LV'][Ex], 1), 0, 1)
    l1 = unit(w1[:, None] * gb + (1 - w1[:, None]) * got); l2 = unit(w2[:, None] * gb + (1 - w2[:, None]) * got)
    ang = np.degrees(np.arccos(np.clip(np.abs(np.sum(l1 * l2, 1)), 0, 1)))
    eon = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(len(Ex)), 4))), shape=(len(P), len(Ex))).tocsr()
    v51 = json.load(open(os.path.join(B, 'sites.json')))
    s52 = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
    pj = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
    fams = {'lv_free_wall', 'lv_septum', 'lv_vein_course', 'lv_summit', 'aortic_cusp'}
    nodes = [(s['id'], int(s['node'])) for s in v51 if s['family'] in fams] + [(s['id'], int(s['node'])) for s in s52 if s['family'] == 'cusp_crescent'] + \
            [(s['id'], int(s['node'])) for s in pj['sites (preview, not in the manifest)']]
    site_ang = {}
    for sid, n in nodes:
        ee = eon.indices[eon.indptr[n]:eon.indptr[n + 1]]
        if len(ee):
            site_ang[sid] = round(float(ang[ee].mean()), 2)
    sa = np.array(list(site_ang.values()))
    top = sorted(site_ang.items(), key=lambda kv: -kv[1])[:5]
    out[h] = {'LV_side_elements': int(len(ix)), 'angle_deg_median_p95_max': [round(float(np.median(ang)), 3), round(float(np.percentile(ang, 95)), 3), round(float(ang.max()), 2)],
              'elements_over_5deg': int((ang > 5).sum()), 'stimulus_nodes': len(sa),
              'at_stimulus_nodes_median_p95_max': [round(float(np.median(sa)), 3), round(float(np.percentile(sa, 95)), 3), round(float(sa.max()), 2)], 'largest_at': top}
    print(h, out[h], flush=True)
G.dump(out, os.path.join(HERE, 'preview_d2.json'))
