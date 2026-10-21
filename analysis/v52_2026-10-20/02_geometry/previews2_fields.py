"""Read-only previews P1 (D19a / D19b fields and frame) and P2 (D20 outflow-angle sign), lock thread request relayed
20 Oct 2026 23:13 UTC. Geometry and fibres only; no beat; nothing is built from them.

P1 (b): every Laplace field of the v5.2 build re-solved on the merged mesh (same mesh, same boundary sets, 02_laplace.py's
precedence: a node in both Dirichlet sets takes the "1" value, solve(): zero = setdiff(zero, one)), here in Python (P1
tetrahedra, unit isotropic conductivity; CG with a Jacobi preconditioner, scipy's stopping test on the unpreconditioned
residual ||r||2 <= rtol ||b||2) from the stored field, to rtol 1e-10 and then on to 1e-12. UVC z is re-mapped from the
converged zeta by 03_uvc.py's rule; UVC v re-thresholded from the converged v field; UVC phi is geometric (no Laplace).
w_LV on the LV-side submesh likewise. Converged fields saved as runs/v52_2026-10-20/02_geometry/<H>/converged/*.npy.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/previews2_fields.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import cg
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import laplace52 as L52                                                                     # noqa: E402
import preview_d19 as D19                                                                   # noqa: E402
import preview_d23 as D23                                                                   # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

FF = Q.FF
AHA = Q.AHA


def solve(K, x0, zero, one, rtol):
    N = K.shape[0]
    zero = np.setdiff1d(zero, one)
    D = np.zeros(N, bool); D[zero] = True; D[one] = True
    xD = np.zeros(N); xD[one] = 1.0
    free = np.where(~D)[0]
    Kff = K[free][:, free]; b = -(K[free][:, np.where(D)[0]] @ xD[D])
    xs, info = cg(Kff, b, x0=x0[free], rtol=rtol, maxiter=50000, M=diags(1.0 / Kff.diagonal()))
    x = x0.copy(); x[free] = xs; x[D] = xD[D]
    return x, float(np.linalg.norm(Kff @ xs - b) / np.linalg.norm(b)), int(info)


def zmap(zeta, pts, apex, base_c):
    """sims/biv_model/03_uvc.py's monotone remap of zeta."""
    axis = (base_c - apex) / np.linalg.norm(base_c - apex)
    s = np.clip((pts - apex) @ axis / np.linalg.norm(base_c - apex), 0, 1)
    zl = np.clip(zeta, 0, 1)
    q = np.unique(np.quantile(zl, np.linspace(0, 1, 201)))
    idx = np.clip(np.searchsorted(q, zl, side='right') - 1, 0, len(q) - 2)
    centre = np.array([zl[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    target = np.array([s[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    ok = ~np.isnan(centre)
    centre, target = centre[ok], np.maximum.accumulate(target[ok])
    xs = np.concatenate([[0.0], centre, [1.0]]); ys = np.maximum.accumulate(np.concatenate([[0.0], target, [1.0]]))
    ys = (ys - ys[0]) / (ys[-1] - ys[0])
    return np.interp(zl, xs, ys)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-30)


def frame_labels(h, pts, vfield, X):
    """AHA labels with the aha51 frame's RV-insertion groove taken from the given UVC v field."""
    F = AHA.Frame(h)
    n51 = len(F.P)
    v = vfield[:n51]
    lve, rve = F.epi[v[F.epi] == 0], F.epi[v[F.epi] == 1]
    F.groove = lve[cKDTree(F.P[rve]).query(F.P[lve])[0] <= 2.0]
    return Q.aha_labels(F, X)


def run(h):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); S = os.path.join(V, 'surfaces')
    CV = os.path.join(G.RUN, h, 'converged'); os.makedirs(CV, exist_ok=True)
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, tg = read_elem(os.path.join(V, 'biv52'))
    K, _ = D19.stiffness(P, E)
    c = L52.Ctx(h, os.path.join(V, 'biv52'), S, '/tmp', '/tmp', '/tmp', 1)
    lv, rv = c.vtx('lv_endo'), c.vtx('rv_endo')
    outer = np.unique(np.concatenate([c.vtx('epi'), np.setdiff1d(c.vtx('ao_iface'), np.concatenate([lv, rv]))]))
    probs = {n: (c.vset(z0), c.vset(z1)) for n, (z0, z1) in {**L52.P02, **L52.PFIX}.items()}
    probs['u_lv'] = (np.union1d(rv, outer), lv); probs['u_rv'] = (np.union1d(lv, outer), rv)
    stored = {n: np.loadtxt(os.path.join(V, 'laplace', n + '.dat')) for n in probs}
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    d51 = em(np.loadtxt(os.path.join(B, 'laplace', 'phi_rv.dat')), E[:nb]) / np.maximum(em(np.loadtxt(os.path.join(B, 'laplace', 'phi_lv.dat')), E[:nb]) + em(np.loadtxt(os.path.join(B, 'laplace', 'phi_rv.dat')), E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, np.ones(len(E) - nb, bool)]; LVs = ~RV
    lvn = np.unique(E[LVs])
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'precedence': "02_laplace.py solve(): zero = setdiff(zero, one), so a node in both Dirichlet sets takes 1",
           'solver': 'scipy CG, Jacobi preconditioner, unpreconditioned relative residual ||r||2 / ||b||2', 'fields': {}}
    conv = {}
    for n, (z0, z1) in probs.items():
        x10, r10, i10 = solve(K, stored[n], z0, z1, 1e-10)
        x12, r12, i12 = solve(K, x10, z0, z1, 1e-12)
        conv[n] = x10
        np.save(os.path.join(CV, n + '.npy'), x10)
        out = lambda x: int(((x < -1e-3) | (x > 1 + 1e-3)).sum())
        rec['fields'][n] = {'relres_1e-10_solve': r10, 'relres_1e-12_solve': r12, 'cg_info': [i10, i12],
                            'max_nodal_change_1e-10_vs_1e-12': float(np.abs(x12 - x10).max()),
                            'max_nodal_change_stored_vs_converged': float(np.abs(x10 - stored[n]).max()),
                            'nodes_outside_by_1e-3 (stored, converged)': [out(stored[n]), out(x10)],
                            'largest_excursion (stored, converged)': [round(float(max(stored[n].max() - 1, -stored[n].min(), 0)), 5), round(float(max(x10.max() - 1, -x10.min(), 0)), 6)]}
        print(h, n, f'{r10:.1e}', rec['fields'][n]['nodes_outside_by_1e-3 (stored, converged)'], flush=True)
    # w_LV
    q = os.path.join(G.RUN, h, 'q12'); sub = os.path.join(q, 'lv_sub')
    Ps = read_pts(sub) / 1e3; Es, _ = read_elem(sub); Ks, _ = D19.stiffness(Ps, Es)
    wst = np.loadtxt(os.path.join(q, 'w_LV.dat'))
    z0, z1 = read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc0.vtx')), read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc1.vtx'))
    w10, r10, _ = solve(Ks, wst, z0, z1, 1e-10); w12, r12, _ = solve(Ks, w10, z0, z1, 1e-12)
    lvsub_nodes = np.unique(E[LVs])
    wLV = np.full(len(P), np.nan); wLV[lvsub_nodes] = w10
    np.save(os.path.join(CV, 'w_LV.npy'), wLV)
    rec['fields']['w_LV (LV-side submesh)'] = {'relres_1e-10_solve': r10, 'relres_1e-12_solve': r12, 'max_nodal_change_1e-10_vs_1e-12': float(np.abs(w12 - w10).max()),
                                              'max_nodal_change_stored_vs_converged': float(np.abs(w10 - wst).max()),
                                              'range_converged': [float(w10.min()), float(w10.max())], 'within_1e-6_of_[0,1]': bool(w10.min() >= -1e-6 and w10.max() <= 1 + 1e-6)}
    # UVC
    apex = P[c.vtx('apex')[0]]; base_c = P[np.concatenate([c.vtx('mv_rim'), c.vtx('tv_rim')])].mean(0)
    z_st = np.loadtxt(os.path.join(V, 'uvc', 'z.dat')); z_cv = zmap(conv['zeta'], P, apex, base_c)
    v_st = np.loadtxt(os.path.join(V, 'uvc', 'v.dat')); v_cv = (conv['v'] > 0.5).astype(float)
    phi = np.loadtxt(os.path.join(V, 'uvc', 'phi.dat'))
    np.save(os.path.join(CV, 'z.npy'), z_cv); np.save(os.path.join(CV, 'v_uvc.npy'), v_cv)
    rec['uvc'] = {'z_max_abs_change': float(np.abs(z_cv - z_st).max()), 'z_p99_abs_change': float(np.percentile(np.abs(z_cv - z_st), 99)),
                  'v_nodes_changing_side': int((v_cv != v_st).sum()), 'phi': 'geometric (03_uvc.py: apex, MV+TV centroid, RV-endocardium centroid, aortic centroid); unchanged'}
    # phi sum shares on LV-side nodes
    for nm, pe in (('phi_epi_fix', 'phi_epi_fix'), ('phi_epi (plain)', 'phi_epi')):
        for lab, F_ in (('stored', stored), ('converged', conv)):
            s_ = np.abs(F_[pe][lvn] + F_['phi_lv'][lvn] + F_['phi_rv'][lvn] - 1)
            rec.setdefault('phi_sum_share_LV_side_nodes_over_1e-6', {}).setdefault(nm, {})[lab] = round(float((s_ > 1e-6).mean()), 4)
    rec['phi_epi_fix_definition'] = ('laplace_fix.py: the same Laplace problem as phi_epi (LV + RV endocardium 0 -> epicardium 1) with the aortic-root '
                                     'interface (ao_iface minus endocardial nodes) added to the "1" set; it is a boundary-set change, not a post-process, '
                                     'so re-solving the same problem re-applies it')
    # (a) consumers
    rec['P1a_fields_and_consumers'] = {
        'zeta -> UVC z (03_uvc remap)': ['R5.2 / D20 r(z) (z >= 0.80)', '11.3 item 2 basal z >= 0.55', 'summit candidate quarter z >= 0.75 (D22)', 'D23 candidates lv_start(z, phi)', 'v5.1 site placement and the D3 patch centres (report 34, placed on v5.1 z: fixed)'],
        'v -> UVC v': ['summit candidate quarter v = 0 (D22)', 'D23 epicardial line end (v = 0)', 'aha51 frame RV-insertion groove (v5.1 v.dat: AHA segments, 11.3 item 2)'],
        'UVC phi (geometric)': ['summit quarter sin(phi) >= 0', 'D23 candidates', 'lv_start'],
        'basal, ot_lv, ot_rv, w': ["l (fibres_fix.py: w unit(grad basal) + (1 - w) unit(grad ot); ot_rv where the element's d > 0.5) for R5.1-R5.3 and D19's frame"],
        'phi_epi_fix, phi_lv, phi_rv': ['D19 LV w (R5.1 helix, R1.3 APD blend)', 'D19b d_s and the RV APD coordinate', 'v5.1 split (R_field, from v5.1 files; fixed)'],
        'w_LV (LV-side submesh)': ['D20 b'],
        'phi_epi (plain), sep, rho': ['reports only (site rho / sep)'],
        'u_lv, u_rv (phi_D), RV-submesh psi_tv / psi_pv / w': ['not consumed in v5.2 (RV fibres are v5.1 rows; RV APD by D19b)']}
    # (c) labels of positions and candidates: stored vs converged
    v51 = json.load(open(os.path.join(B, 'sites.json')))
    pts_list = {('v51_position', s['family'], s['position'], str(s['level_z'])): int(s['surface_node']) for s in v51}
    d23 = json.load(open(os.path.join(HERE, 'preview_d23r.json')))
    for a in d23['added_positions']:
        if a['heart'] == h:
            pts_list[('d23_candidate', a['id90'])] = int(a['surface_node'])
    s52 = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
    for s in s52:
        pts_list[('new_site', s['id'])] = int(s['node'])
    pj = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
    for s in pj['sites (preview, not in the manifest)']:
        pts_list[('summit_projB', s['id'])] = int(s['node'])
    keys = list(pts_list); nodes = np.array([pts_list[k] for k in keys])
    seg_st = frame_labels(h, P, v_st, P[nodes]); seg_cv = frame_labels(h, P, v_cv, P[nodes])
    reg = lambda sg, z: D23.region(int(sg), float(z))
    ch = {'items': len(keys), 'gate5_region': 0, 'AHA_segment': 0, 'z_0.55': 0, 'z_0.75': 0, 'z_0.80': 0, 'examples': []}
    for k, n, a1, a2 in zip(keys, nodes, seg_st, seg_cv):
        r1, r2 = reg(a1, z_st[n]), reg(a2, z_cv[n])
        flags = {'gate5_region': r1 != r2, 'AHA_segment': a1 != a2, 'z_0.55': (z_st[n] >= 0.55) != (z_cv[n] >= 0.55),
                 'z_0.75': (z_st[n] >= 0.75) != (z_cv[n] >= 0.75), 'z_0.80': (z_st[n] >= 0.80) != (z_cv[n] >= 0.80)}
        for f_, v_ in flags.items():
            ch[f_] += int(v_)
        if any(flags.values()) and len(ch['examples']) < 10:
            ch['examples'].append({'item': ' '.join(k), 'z': [round(float(z_st[n]), 4), round(float(z_cv[n]), 4)], 'aha': [int(a1), int(a2)]})
    rec['P1c_label_changes_stored_vs_converged'] = ch
    # (d) l from converged vs stored fields (fibres_fix rule) on the LV side
    ix = np.where(LVs)[0]; Ex = E[ix]
    def l_of(Fd):
        w = em(Fd['w'], Ex); d = em(Fd['phi_rv'], Ex) / np.maximum(em(Fd['phi_lv'], Ex) + em(Fd['phi_rv'], Ex), 1e-9)
        g_ot = np.where((d > 0.5)[:, None], unit(FF.elem_grad(P, Ex, Fd['ot_rv'])), unit(FF.elem_grad(P, Ex, Fd['ot_lv'])))
        return unit(w[:, None] * unit(FF.elem_grad(P, Ex, Fd['basal'])) + (1 - w[:, None]) * g_ot), d
    l_st, d_st = l_of(stored); l_cv, d_cv = l_of(conv)
    a_l = np.degrees(np.arccos(np.clip(np.abs(np.sum(l_st * l_cv, 1)), 0, 1)))
    rec['P1d_l_angle_converged_vs_stored_deg'] = {'median': round(float(np.median(a_l)), 4), 'p95': round(float(np.percentile(a_l, 95)), 4), 'max': round(float(a_l.max()), 3),
                                                  'LV_side_elements_where_d_gt_0.5_(ot_rv used by the literal rule)': int((d_cv > 0.5).sum())}
    # (e) D19b nodal APD coordinate
    pe, pl, pr = (np.clip(conv[n], 0, 1) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv'))
    ssum = pl + pr
    lvnode = np.zeros(len(P), bool); lvnode[np.unique(E[LVs])] = True
    rvonly = ~lvnode
    ds = np.where(ssum < 1e-9, np.where(rvonly, 1.0, 0.0), pr / np.maximum(ssum, 1e-30))
    w_apd = np.where(ds <= 0.5, 1 - (1 - pe) * (1 - ds), 1 - (1 - pe) * ds)
    np.save(os.path.join(CV, 'w_apd_D19b.npy'), w_apd)
    # edges of elements on either side of v5.1's split that touch the split (face pairs across it)
    Ff = np.concatenate([E[:nb][:, [0, 1, 2]], E[:nb][:, [0, 1, 3]], E[:nb][:, [0, 2, 3]], E[:nb][:, [1, 2, 3]]]); Ff.sort(1)
    N = len(P); kf = (Ff[:, 0] * N + Ff[:, 1]) * N + Ff[:, 2]; el = np.tile(np.arange(nb), 4)
    o = np.argsort(kf, kind='stable'); ks, es = kf[o], el[o]; j = np.where(ks[1:] == ks[:-1])[0]
    ea, eb = es[j], es[j + 1]; cr = RV[ea] != RV[eb]
    elems = np.unique(np.r_[ea[cr], eb[cr]])
    ed = np.unique(np.sort(np.concatenate([E[elems][:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    dw = np.abs(w_apd[ed[:, 0]] - w_apd[ed[:, 1]])
    k_ = int(np.argmax(dw)); mid = 0.5 * (P[ed[k_, 0]] + P[ed[k_, 1]])
    sw = (ds[ed[:, 0]] <= 0.5) != (ds[ed[:, 1]] <= 0.5)
    pv, _ = G.pulmonary_frame(*G.load_full(h)); av, _ = G.aortic_frame(*G.load_full(h))
    rec['P1e_D19b_APD_w_along_edges_at_the_split'] = {'edges': int(len(ed)), 'max': round(float(dw.max()), 4), 'p99': round(float(np.percentile(dw, 99)), 4),
                                                      'median': round(float(np.median(dw)), 4),
                                                      'edges_where_the_formula_switches': int(sw.sum()), 'max_on_switching_edges': round(float(dw[sw].max()), 4) if sw.any() else None,
                                                      'largest_at': {'edge_nodes': ed[k_].tolist(), 'z': round(float(z_cv[ed[k_]].mean()), 3),
                                                                     'height_above_PV_mid_plane_mm': round(float(pv.h(mid)[0]), 1), 'height_above_AV_mid_plane_mm': round(float(av.h(mid)[0]), 1),
                                                                     'd_s': [round(float(ds[x]), 3) for x in ed[k_]], 'phi_epi_fix': [round(float(pe[x]), 3) for x in ed[k_]]},
                                                      'nodes_with_phi_lv_plus_phi_rv_lt_1e-9': int((ssum < 1e-9).sum())}
    # (f) D19 LV frame on converged fields, guard, orthonormality
    wn = 1 - (1 - pe) * (1 - ds)
    gw = FF.elem_grad(P, Ex, wn)
    tr = gw - np.sum(l_cv * gw, 1, keepdims=True) * l_cv
    mag = np.linalg.norm(tr, axis=1)
    bad = mag < 0.01 * np.median(mag)
    t = unit(tr)
    C = P[Ex].mean(1)
    guarded = {'below_1pct_median': int(bad.sum()), 'filled_2mm': 0, 'filled_4mm': 0, 'unfilled (stop)': 0}
    if bad.any():
        tree = cKDTree(C[~bad]); good = t[~bad]
        for i in np.where(bad)[0]:
            for rad, key in ((2.0, 'filled_2mm'), (4.0, 'filled_4mm')):
                nb_ = tree.query_ball_point(C[i], rad)
                if nb_:
                    m_ = good[nb_].mean(0); m_ -= (m_ @ l_cv[i]) * l_cv[i]
                    t[i] = unit(m_); guarded[key] += 1; break
            else:
                guarded['unfilled (stop)'] += 1
    cc = unit(np.cross(l_cv, t))
    wel = wn[Ex].mean(1); al = np.radians(66 - 107 * wel)
    f = unit(np.cos(al)[:, None] * cc + np.sin(al)[:, None] * l_cv)
    s = t; n_ = np.cross(f, s)
    orth = {'max_|f|-1': float(np.abs(np.linalg.norm(f, axis=1) - 1).max()), 'max_|s|-1': float(np.abs(np.linalg.norm(s, axis=1) - 1).max()),
            'max_|f.s|': float(np.abs(np.sum(f * s, 1)).max()), 'max_|n|-1': float(np.abs(np.linalg.norm(n_, axis=1) - 1).max()),
            'max_|l.t_out|': float(np.abs(np.sum(l_cv * t, 1)).max())}
    rec['P1f_D19_frame'] = {'guard': guarded, 'orthonormality': orth}
    # P2 (a): v5.1's stored RV fibres just below the PV, helix in the D19 frame (l by fibres_fix's rule, t_out from the RV APD w)
    lon51 = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    iR = np.where(RV[:nb])[0]; ER = E[iR]
    wdR = em(conv['w'], ER); dR = em(conv['phi_rv'], ER) / np.maximum(em(conv['phi_lv'], ER) + em(conv['phi_rv'], ER), 1e-9)
    lR = unit(wdR[:, None] * unit(FF.elem_grad(P, ER, conv['basal'])) + (1 - wdR[:, None]) * np.where((dR > 0.5)[:, None], unit(FF.elem_grad(P, ER, conv['ot_rv'])), unit(FF.elem_grad(P, ER, conv['ot_lv']))))
    gR = FF.elem_grad(P, ER, w_apd); tR = unit(gR - np.sum(lR * gR, 1, keepdims=True) * lR); cR = np.cross(lR, tR)
    fR = unit(lon51[iR, :3])
    hR = np.degrees(np.arctan2(np.sum(fR * lR, 1), np.sum(fR * cR, 1))); hR = (hR + 90) % 180 - 90
    depth = w_apd[ER].mean(1)
    hb = pv.h(P[ER].mean(1))
    m = (depth >= 0.4) & (depth <= 0.6) & (1 - wdR > 0.9) & (hb < 0)
    rec['P2a'] = {'rule_in_code': ("v5.1's RV rows are doste_rv.py's (not fibres_fix.py): h = 90 (1 - d) - 25 w d in the standard helix convention "
                                   "(LV subendocardium positive, t_out outward), so +90 at the RV endocardium in the outflow (w = 0); fibres_fix.py "
                                   "(v5's rule, still v5.1's LV side) gives a_s(d) = a_endo (1 - d) - a_endo d, i.e. -a_endo (-90 in the outflow) at d = 1, "
                                   "in its own frame axis(gpsi, grad phi_rv), whose transmural axis points into the RV"),
                  'elements (RV region, D19b APD w 0.4-0.6, outflow weight 1 - w_doste > 0.9, below the PV mid-plane)': int(m.sum()),
                  'v51_stored_RV_helix_median_deg (D19 frame: l fibres_fix rule, t_out = grad of the D19b APD w)': round(float(np.median(hR[m])), 1) if m.any() else None,
                  'p10_p90': [round(float(np.percentile(hR[m], 10)), 1), round(float(np.percentile(hR[m], 90)), 1)] if m.any() else None}
    # P2 (b): helix at gate-1/3/5/8 stimulus nodes under +90 and -90
    zE = np.clip(z_cv[Ex].mean(1), 0, 1); wl_e = np.clip(np.nanmean(wLV[Ex], 1), 0, 1)
    b = np.clip((zE - 0.80) / 0.20, 0, 1) * (1 - wl_e)
    a51 = 66 - 107 * wel
    ap = (1 - b) * a51 + b * 90 * (1 - wel); am = (1 - b) * a51 - b * 90 * (1 - wel)
    eon = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(len(Ex)), 4))), shape=(len(P), len(Ex))).tocsr()
    rows = []
    gate_fams = {'lv_free_wall', 'lv_septum', 'lv_vein_course', 'lv_summit', 'aortic_cusp'}
    nodes2 = [(s['id'], int(s['node'])) for s in v51 if s['family'] in gate_fams] + [(s['id'], int(s['node'])) for s in s52 if s['family'] == 'cusp_crescent'] + \
             [(s['id'], int(s['node'])) for s in pj['sites (preview, not in the manifest)']]
    for sid, n in nodes2:
        ee = eon.indices[eon.indptr[n]:eon.indptr[n + 1]]
        if len(ee) and b[ee].mean() > 0:
            rows.append({'site': sid, 'b': round(float(b[ee].mean()), 3), 'helix_plus90': round(float(ap[ee].mean()), 1), 'helix_minus90': round(float(am[ee].mean()), 1)})
    dif = np.array([abs(r['helix_plus90'] - r['helix_minus90']) for r in rows]) if rows else np.zeros(0)
    rec['P2b'] = {'stimulus_nodes_with_b_gt_0': len(rows), 'median_helix_plus90': round(float(np.median([r['helix_plus90'] for r in rows])), 1) if rows else None,
                  'median_helix_minus90': round(float(np.median([r['helix_minus90'] for r in rows])), 1) if rows else None,
                  'median_abs_difference_deg': round(float(np.median(dif)), 1) if rows else None, 'largest_abs_difference_deg': round(float(dif.max()), 1) if rows else None,
                  'largest_at': rows[int(np.argmax(dif))]['site'] if rows else None, 'rows': rows,
                  'note': 'b and w on the converged fields (D19 w, D20 b with converged w_LV and z)'}
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'previews2_fields_{h}.json'))
    print(h, 'done', rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
