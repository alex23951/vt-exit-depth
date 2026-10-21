"""Read-only preview P8 (lock thread, relayed 21 Oct 2026 02:34 UTC). Report only; nothing is built.

(a) P1 (e) and (f) again on the converged fields (runs/v52_2026-10-20/02_geometry/<H>/converged/) with the revised D19b:
    d_s at nodes with phi_lv + phi_rv < 1e-9 = the mean of d_s over the node's edge neighbours that have a value, repeated
    outward until every such node has one; the guard's last step = v5.1's stored transmural direction of the element,
    n = f x s from bivF_v51.lon (fibres_fix.py's frame column e2, the orthogonalised transmural gradient bislerped between
    grad phi_lv, grad phi_rv and grad phi_epi_fix), re-projected perpendicular to l and renormalised; stop only if that
    is under 1 % after projection. l per C8 (grad ot_lv on every LV-side element) and D20c (w_LV in place of w.dat).
(b) D25: the focus's AHA segment and z on converged UVC (aha51 frame with the groove from the converged v).
(d) D29: 6G8DD8S5's RV PMJs above the pulmonary mid-plane ring and the surfaces they lie on.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p8.py
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import previews2_fields as PF                                                               # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

FF = Q.FF
unit = PF.unit


def run(h):
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); cv = os.path.join(G.RUN, h, 'converged'); S = os.path.join(V, 'surfaces')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, _ = read_elem(os.path.join(V, 'biv52'))
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, np.ones(len(E) - nb, bool)]; LVs = ~RV
    F = {n: np.load(os.path.join(cv, n + '.npy')) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv', 'basal', 'ot_lv', 'w_LV')}
    pe, pl, pr = (np.clip(F[n], 0, 1) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv'))
    ssum = pl + pr
    ds = np.where(ssum >= 1e-9, pr / np.maximum(ssum, 1e-30), np.nan)
    # neighbour fill, repeated outward
    pairs = np.unique(np.sort(np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    N = len(P)
    A = coo_matrix((np.ones(2 * len(pairs)), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(N, N)).tocsr()
    todo0 = int(np.isnan(ds).sum()); passes = 0
    while np.isnan(ds).any():
        has = ~np.isnan(ds)
        s_ = A @ np.where(has, ds, 0.0); c_ = A @ has.astype(float)
        new = np.isnan(ds) & (c_ > 0)
        if not new.any():
            break
        ds[new] = s_[new] / c_[new]; passes += 1
    left = int(np.isnan(ds).sum())
    w_apd = np.where(ds <= 0.5, 1 - (1 - pe) * (1 - ds), 1 - (1 - pe) * ds)
    # edges of elements on both sides of v5.1's split
    Ff = np.concatenate([E[:nb][:, [0, 1, 2]], E[:nb][:, [0, 1, 3]], E[:nb][:, [0, 2, 3]], E[:nb][:, [1, 2, 3]]]); Ff.sort(1)
    kf = (Ff[:, 0] * N + Ff[:, 1]) * N + Ff[:, 2]; el = np.tile(np.arange(nb), 4)
    o = np.argsort(kf, kind='stable'); ks, es = kf[o], el[o]; j = np.where(ks[1:] == ks[:-1])[0]
    ea, eb = es[j], es[j + 1]; cr = RV[ea] != RV[eb]
    elems = np.unique(np.r_[ea[cr], eb[cr]])
    ed = np.unique(np.sort(np.concatenate([E[elems][:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    dw = np.abs(w_apd[ed[:, 0]] - w_apd[ed[:, 1]]); k_ = int(np.argmax(dw)); mid = 0.5 * (P[ed[k_, 0]] + P[ed[k_, 1]])
    Pf, Ef, tf = G.load_full(h)
    pv, _ = G.pulmonary_frame(Pf, Ef, tf); av, _ = G.aortic_frame(Pf, Ef, tf)
    z_cv = np.load(os.path.join(cv, 'z.npy'))
    rec = {'heart': h, 'a_D19b_fill': {'nodes_with_phi_lv_plus_phi_rv_lt_1e-9': todo0, 'passes': passes, 'left_unfilled': left},
           'a_APD_w_step_along_split_edges': {'edges': int(len(ed)), 'median': round(float(np.median(dw)), 4), 'p99': round(float(np.percentile(dw, 99)), 4),
                                              'max': round(float(dw.max()), 4),
                                              'largest_at': {'z': round(float(z_cv[ed[k_]].mean()), 3), 'height_above_AV_mid_plane_mm': round(float(av.h(mid)[0]), 1),
                                                             'height_above_PV_mid_plane_mm': round(float(pv.h(mid)[0]), 1), 'd_s': [round(float(ds[x]), 3) for x in ed[k_]],
                                                             'phi_epi_fix': [round(float(pe[x]), 3) for x in ed[k_]], 'w_apd': [round(float(w_apd[x]), 3) for x in ed[k_]]}}}
    # frame with l per C8 (ot_lv everywhere on the LV side) and D20c (w_LV)
    ix = np.where(LVs)[0]; Ex = E[ix]
    wl = np.clip(np.nanmean(F['w_LV'][Ex], 1), 0, 1)
    l = unit(wl[:, None] * unit(FF.elem_grad(P, Ex, F['basal'])) + (1 - wl[:, None]) * unit(FF.elem_grad(P, Ex, F['ot_lv'])))
    wn = 1 - (1 - pe) * (1 - ds)
    gw = FF.elem_grad(P, Ex, wn)
    tr = gw - np.sum(l * gw, 1, keepdims=True) * l
    mag = np.linalg.norm(tr, axis=1); med = np.median(mag)
    bad = mag < 0.01 * med
    t = unit(tr); C = P[Ex].mean(1)
    lon = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    n51 = unit(np.cross(lon[:, :3], lon[:, 3:6]))
    g = {'below_1pct_median': int(bad.sum()), 'filled_2mm': 0, 'filled_4mm': 0, 'fallback_v51_n': 0, 'stop (fallback also under 1 %)': 0}
    if bad.any():
        tree = cKDTree(C[~bad]); good = t[~bad]
        for i in np.where(bad)[0]:
            done = False
            for rad, key in ((2.0, 'filled_2mm'), (4.0, 'filled_4mm')):
                nb_ = tree.query_ball_point(C[i], rad)
                if nb_:
                    m_ = good[nb_].mean(0); m_ -= (m_ @ l[i]) * l[i]
                    t[i] = unit(m_); g[key] += 1; done = True; break
            if not done:
                e = ix[i]
                v = n51[e] if e < nb else np.zeros(3)
                v = v - (v @ l[i]) * l[i]
                if np.linalg.norm(v) < 0.01:
                    g['stop (fallback also under 1 %)'] += 1
                else:
                    t[i] = unit(v); g['fallback_v51_n'] += 1
    cc = unit(np.cross(l, t)); al = np.radians(66 - 107 * wn[Ex].mean(1))
    f = unit(np.cos(al)[:, None] * cc + np.sin(al)[:, None] * l); s = t; n_ = np.cross(f, s)
    rec['a_guard'] = g
    rec['a_orthonormality'] = {'max_|f|-1': float(np.abs(np.linalg.norm(f, axis=1) - 1).max()), 'max_|s|-1': float(np.abs(np.linalg.norm(s, axis=1) - 1).max()),
                               'max_|f.s|': float(np.abs(np.sum(f * s, 1)).max()), 'max_|n|-1': float(np.abs(np.linalg.norm(n_, axis=1) - 1).max()),
                               'max_|l.s|': float(np.abs(np.sum(l * s, 1)).max())}
    rec['a_stored_transmural_vector'] = ('n = f x s of data/biv/<H>/fibres_v51/bivF_v51.lon (the .lon holds the fibre f and the sheet s; s is the in-wall '
                                         'cross-fibre column, so the transmural direction is the sheet normal). For LV-side elements fibres_fix.py built it as '
                                         'column e2 of its frame: grad phi_lv, grad phi_rv and grad phi_epi_fix, each orthogonalised to l, bislerped by d and '
                                         'by phi_epi_fix, so yes, from transmural gradients (rotated with the fibre about e2, which leaves e2 unchanged)')
    # (b) D25 focus on converged UVC
    s52 = json.load(open(os.path.join(HERE, f'previews2_sites_{h}.json')))
    foc = int(s52['P5_focus']['focus_node'])
    v_cv = np.load(os.path.join(cv, 'v_uvc.npy'))
    seg = int(PF.frame_labels(h, P, v_cv, P[[foc]])[0])
    rec['b_D25_focus'] = {'node': foc, 'AHA_segment': seg, 'z_converged': round(float(z_cv[foc]), 4), 'in_AHA_2': seg == 2}
    # (d) D29: RV PMJs above the PV mid-plane ring
    net = np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz'))
    nodes, kind, pmj = net['nodes'], net['kind'].astype(str), net['pmj']
    rp = nodes[pmj[kind[pmj] == 'distal_rv']]
    hh = pv.h(P[rp]); up = rp[hh > 0]
    surfs = {}
    for fn in sorted(os.listdir(S)):
        if fn.endswith('.vtx'):
            vv = set(read_vtx(os.path.join(S, fn)).tolist())
            c = sum(1 for n in up if int(n) in vv)
            if c:
                surfs[fn[:-4]] = c
    rec['d_D29_RV_PMJs_above_PV_mid_plane'] = {'count': int(len(up)), 'heights_mm': [round(float(x), 2) for x in sorted(hh[hh > 0])],
                                               'on_surfaces (v5.2 surface files)': surfs,
                                               'angles_in_pulmonary_frame_deg': [round(float(x), 1) for x in pv.theta(P[up])]}
    G.dump(rec, os.path.join(HERE, f'preview_p8_{h}.json'))
    print(h, json.dumps({k: v for k, v in rec.items() if k != 'a_stored_transmural_vector'}), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
