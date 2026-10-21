"""Read-only preview P9 (lock thread, relayed 21 Oct 2026 02:44 UTC). Report only; nothing is built, no fibre file is written.

Frame as corrected by the lock thread (still proposed): on LV-side elements l per C8 and D20c, t_out per D19b (guard: 2 mm,
4 mm, v5.1's stored n), c = unit(l x t_out), f = cos(alpha) c + sin(alpha) l with alpha = 66 - 107 w, and then
s = unit(t_out x f) (in-wall, cross-fibre) and n = f x s (= t_out, transmural), v5.1's convention (.lon holds f and s).
(a) which .lon axis carries section 5's transmural speed (written into the JSON from the code cited there); n = t_out
    checked numerically; the angle between v5.2's transmural axis n and v5.1's n = f x s of bivF_v51.lon on LV-side
    elements (axis angle, sign ignored).
(b) D30 (proposed) for the elements where l is undefined (|l| before normalising < 1e-9: both gradients vanish):
    l = the normalised mean of l over face-adjacent LV-side elements that already have one (face adjacency of the cut
    mesh biv52cut, the simulation mesh; a pass uses only values from earlier passes; the original elements count as
    pass 0); where that mean is under 0.01 in length, l = l of the lowest-id face neighbour that had one before the
    pass. Then t_out, c, f, s and n as everywhere else. Reports: elements per pass, fallbacks, the gate stimulus nodes
    (sites52.json capture list: v5.1's 144 sites and v5.2's 26 new ones; gate 7a patch centres) inside the filled
    elements (a vertex of one) or within 2 mm of a vertex of one, and orthonormality after.
(c) D25 (proposed, revised): in each heart the qualifying node of P5's set in AHA segment 2 (aha51 frame, groove from
    the converged v) nearest v5.1's septal-RVOT 10 % site (rvot_septal_z_d10); its distances and heights as in P5.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p9.py
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

AXES = {
    'v5.1 graph eikonal': 'n = f x s: analysis/v51_2026-10-15/04_build/graph51.py S3 metric, M = sum over fibre, sheet and normal (= f x s) of '
                          '(factor x speed)^-2 a a^T; the "normal" speed is 0.48 (Y5HYEDL4) / 0.336 m/s (params/v51_speeds.json, v51_graph_factors.json)',
    'v5.1 openCARP eikonal (acceptance C)': 'n = f x s: acceptance_c.py setup(), dream.vel_n = the "normal" speed and g_in / g_en = calibration "sheet_normal"; '
                                            "openCARP's own help: g_it 'sheet direction (transversal)', g_in 'sheet-normal direction (normal)'",
    'v5.1 monodomain': 'n = f x s: 08_monodomain/mono51.py lines 184-185 (g_in / g_en = the "normal" set) and mono_cal51.py (that set tuned to the 6 mm '
                       'transit at the normal speed)',
    'v5.2 graph eikonal (step 3, written)': 'n = f x s: params/v52_speeds.json "normal" (sheet normal) = 0.48 / 0.336 m/s; slab52.py acceptance A measured it so',
    'v5.2 openCARP eikonal and monodomain (not yet written)': 'planned as v5.1: vel_n and g_in / g_en on the sheet normal, so the transmural speed on n',
    'RV side (C2)': "fibres copied from v5.1's file, so transmural on n as in v5.1",
}


def face_adjacency(E):
    """Element pairs sharing a face (each pair once)."""
    Ff = np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]]); Ff.sort(1)
    el = np.tile(np.arange(len(E)), 4)
    o = np.lexsort((Ff[:, 2], Ff[:, 1], Ff[:, 0])); Fs, es = Ff[o], el[o]
    j = np.where((Fs[1:] == Fs[:-1]).all(1))[0]
    return es[j], es[j + 1]


def stats_deg(a):
    return {'median': round(float(np.median(a)), 2), 'p95': round(float(np.percentile(a, 95)), 2), 'max': round(float(a.max()), 2), 'n': int(len(a))}


def run(h):
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); cv = os.path.join(G.RUN, h, 'converged'); S = os.path.join(V, 'surfaces')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, _ = read_elem(os.path.join(V, 'biv52'))
    Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    assert len(Ec) == len(E)
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, np.ones(len(E) - nb, bool)]; LVs = ~RV
    F = {n: np.load(os.path.join(cv, n + '.npy')) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv', 'basal', 'ot_lv', 'w_LV', 'z', 'v_uvc')}
    pe, pl, pr = (np.clip(F[n], 0, 1) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv'))
    ssum = pl + pr
    ds = np.where(ssum >= 1e-9, pr / np.maximum(ssum, 1e-30), np.nan)
    pairs = np.unique(np.sort(np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    N = len(P)
    A = coo_matrix((np.ones(2 * len(pairs)), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(N, N)).tocsr()
    while np.isnan(ds).any():                                                               # D19b neighbour fill (as P8)
        has = ~np.isnan(ds)
        s_ = A @ np.where(has, ds, 0.0); c_ = A @ has.astype(float)
        new = np.isnan(ds) & (c_ > 0)
        if not new.any():
            break
        ds[new] = s_[new] / c_[new]
    assert not np.isnan(ds).any()
    wn = 1 - (1 - pe) * (1 - ds)
    ix = np.where(LVs)[0]; Ex = E[ix]; nl_ = len(ix)
    wl = np.clip(np.nanmean(F['w_LV'][Ex], 1), 0, 1)
    gb, go = FF.elem_grad(P, Ex, F['basal']), FF.elem_grad(P, Ex, F['ot_lv'])
    lraw = wl[:, None] * unit(gb) + (1 - wl[:, None]) * unit(go)
    nlr = np.linalg.norm(lraw, axis=1)
    zb, zo = np.linalg.norm(gb, axis=1) == 0, np.linalg.norm(go, axis=1) == 0
    undef = nlr < 1e-9
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA,
           'b_D30_undefined_l': {'elements_|l|_lt_1e-9': int(undef.sum()), 'of_which_exactly_0': int((nlr == 0).sum()),
                                 'cause': {'both gradients zero': int((undef & zb & zo).sum()),
                                           'grad basal zero and w_LV = 1 (all weight on it)': int((undef & zb & ~zo & (wl == 1)).sum()),
                                           'grad ot_lv zero and w_LV = 0 (all weight on it)': int((undef & zo & ~zb & (wl == 0)).sum()),
                                           'other': int((undef & ~(zb & zo) & ~(zb & ~zo & (wl == 1)) & ~(zo & ~zb & (wl == 0))).sum())},
                                 'elements_1e-9_le_|l|_lt_0.01 (not filled; normalised as computed)': int(((nlr >= 1e-9) & (nlr < 0.01)).sum())}}
    # D30 fill on the cut mesh's face adjacency among LV-side elements
    loc = np.full(len(E), -1); loc[ix] = np.arange(nl_)
    ea, eb = face_adjacency(Ec)
    m = (loc[ea] >= 0) & (loc[eb] >= 0); a_, b_ = loc[ea[m]], loc[eb[m]]
    Af = coo_matrix((np.ones(2 * len(a_)), (np.r_[a_, b_], np.r_[b_, a_])), shape=(nl_, nl_)).tocsr()
    def pairs_touching(EE):
        pa, pb = face_adjacency(EE)
        k = (loc[pa] >= 0) & (loc[pb] >= 0); pa, pb = loc[pa[k]], loc[pb[k]]
        k = undef[pa] | undef[pb]
        return set(zip(np.minimum(pa, pb)[k].tolist(), np.maximum(pa, pb)[k].tolist()))
    rec['b_D30_undefined_l']['face_pairs_touching_them_that_differ_between_merged_and_cut_mesh'] = len(pairs_touching(E) ^ pairs_touching(Ec))
    l = unit(lraw); l[undef] = 0.0
    have = ~undef; per_pass, fallback = [], 0
    while not have.all():
        hv = have.astype(float)
        sm = Af @ (l * hv[:, None]); cnt = Af @ hv
        new = ~have & (cnt > 0)
        if not new.any():
            break
        mean = sm[new] / cnt[new][:, None]; nm = np.linalg.norm(mean, axis=1)
        out = unit(mean)
        for k in np.where(nm < 0.01)[0]:
            i = np.where(new)[0][k]
            row = Af.indices[Af.indptr[i]:Af.indptr[i + 1]]
            row = row[have[row]]
            out[k] = l[row.min()]; fallback += 1
        l[new] = out; have = have | new; per_pass.append(int(new.sum()))
    rec['b_D30_undefined_l'].update({'elements_filled_per_pass': per_pass, 'left_unfilled': int((~have).sum()), 'lowest_id_fallbacks': fallback})
    left = np.where(~have)[0]
    if len(left):
        ea_all, eb_all = face_adjacency(Ec)
        lset = set(ix[left].tolist())
        det = []
        for e in ix[left]:
            fn_ = np.r_[eb_all[ea_all == e], ea_all[eb_all == e]]
            det.append({'element': int(e), 'z': round(float(F['z'][E[e]].mean()), 3),
                        'face_neighbours': int(len(fn_)), 'of_which_LV_side': int(sum(loc[x] >= 0 for x in fn_)),
                        'of_which_LV_side_with_l': int(sum(loc[x] >= 0 and have[loc[x]] for x in fn_)),
                        'of_which_RV_side': int(sum(loc[x] < 0 for x in fn_)),
                        'LV_face_neighbours_also_left': int(sum(int(x) in lset for x in fn_))})
        # for the lock thread's choice only: what an edge/corner neighbourhood or the nearest element would offer
        Cl = P[Ex[have]].mean(1); tr_ = cKDTree(Cl)
        nodeset = [set(Ec[e].tolist()) for e in ix[left]]
        cand_ = np.where(np.isin(Ec[ix], np.unique(Ec[ix[left]])).any(1) & have)[0]
        for k_, e in enumerate(ix[left]):
            share = [c_ for c_ in cand_ if nodeset[k_] & set(Ec[ix[c_]].tolist())]
            det[k_]['LV_side_elements_with_l_sharing_a_node'] = int(len(share))
            det[k_]['nearest_LV_side_element_with_l_centroid_mm'] = round(float(tr_.query(P[E[e]].mean(0))[0]), 2)
        rec['b_D30_undefined_l']['left_unfilled_detail (no face path to an LV-side element with l)'] = det
    filled = np.where(undef)[0]
    # D19b t_out with the guard (as P8), on the D30 l
    gw = FF.elem_grad(P, Ex, wn)
    tr = gw - np.sum(l * gw, 1, keepdims=True) * l
    mag = np.linalg.norm(tr, axis=1); med = np.median(mag); bad = mag < 0.01 * med
    t = unit(tr); C = P[Ex].mean(1)
    lon = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    f51, s51 = unit(lon[:, :3]), unit(lon[:, 3:6]); n51 = unit(np.cross(f51, s51))
    g = {'below_1pct_median': int(bad.sum()), 'filled_2mm': 0, 'filled_4mm': 0, 'fallback_v51_n': 0, 'stop (fallback also under 1 %)': 0,
         'D30_elements_among_below_1pct': int(bad[filled].sum())}
    if bad.any():
        tree = cKDTree(C[~bad]); good = t[~bad]
        for i in np.where(bad)[0]:
            done = False
            for rad, key in ((2.0, 'filled_2mm'), (4.0, 'filled_4mm')):
                q = tree.query_ball_point(C[i], rad)
                if q:
                    v = good[q].mean(0); v -= (v @ l[i]) * l[i]
                    t[i] = unit(v); g[key] += 1; done = True; break
            if not done:
                v = n51[ix[i]] - (n51[ix[i]] @ l[i]) * l[i]
                if np.linalg.norm(v) < 0.01:
                    g['stop (fallback also under 1 %)'] += 1
                else:
                    t[i] = unit(v); g['fallback_v51_n'] += 1
    rec['b_D19b_guard_with_D30_l'] = g
    c = unit(np.cross(l, t)); al = np.radians(66 - 107 * wn[Ex].mean(1))
    f = unit(np.cos(al)[:, None] * c + np.sin(al)[:, None] * l)
    s = unit(np.cross(t, f)); n = np.cross(f, s)
    nrm = lambda x: np.linalg.norm(x, axis=1)
    rec['b_orthonormality_after_all'] = {'zero_f_s_n_elements (= the unfilled l)': int((nrm(f) == 0).sum())}
    f, s, n, l, t = (x[have] for x in (f, s, n, l, t))
    rec['b_orthonormality_after (excluding the unfilled)'] = {'min_|f|': float(nrm(f).min()), 'min_|s|': float(nrm(s).min()), 'min_|n|': float(nrm(n).min()),
                                     'max_||f|-1|': float(np.abs(nrm(f) - 1).max()), 'max_||s|-1|': float(np.abs(nrm(s) - 1).max()), 'max_||n|-1|': float(np.abs(nrm(n) - 1).max()),
                                     'max_|f.s|': float(np.abs(np.sum(f * s, 1)).max()), 'max_|f.n|': float(np.abs(np.sum(f * n, 1)).max()),
                                     'max_|s.n|': float(np.abs(np.sum(s * n, 1)).max()), 'max_|l.t_out|': float(np.abs(np.sum(l * t, 1)).max()),
                                     'min_|l|': float(nrm(l).min())}
    # (a) n = t_out, and the angle to v5.1's transmural axis
    ang = lambda u, v: np.degrees(np.arccos(np.clip(np.abs(np.sum(u * v, 1)), 0, 1)))
    hv_ = have
    a51 = ang(n, n51[ix][hv_]); keep = ~undef[hv_]; badh = bad[hv_]
    rec['a_axis'] = AXES
    rec['a_n_equals_t_out'] = {'max_|n - t_out|': float(nrm(n - t).max()), 'min_n.t_out': float(np.sum(n * t, 1).min())}
    rec['a_angle_v52_n_to_v51_n_deg'] = {'all LV-side elements': stats_deg(a51), 'excluding the D30 elements': stats_deg(a51[keep]),
                                         'D30 elements filled (v5.1 rows arbitrary there)': stats_deg(a51[undef[hv_]]),
                                         'excluding D30 and guard-filled elements': stats_deg(a51[keep & ~badh]),
                                         'elements_over_10_deg (excl. D30)': int((a51[keep] > 10).sum()), 'elements_over_30_deg (excl. D30)': int((a51[keep] > 30).sum())}
    rec['a_for_contrast_angle_v52_n_to_v51_s_deg (what s = t_out would have swapped)'] = stats_deg(ang(n, s51[ix][hv_])[keep])
    # (b) gate stimulus nodes near the D30 elements
    s52 = json.load(open(os.path.join(V, 'sites52.json')))
    stim = [(x['id'], x.get('set', ''), int(x['node']), bool(x.get('valid', True))) for x in s52['capture']]
    stim += [('gate7a_' + k, 'gate7a patch centre', int(x['node']), True) for k, x in s52['gate7a_patch_centres'].items()]
    fn = np.unique(Ex[filled])
    dmin = cKDTree(P[fn]).query(P[[x[2] for x in stim]])[0] if len(fn) else np.full(len(stim), np.inf)
    infn = set(fn.tolist())
    rec['b_stimulus_nodes'] = {'checked': len(stim),
                               'inside_D30_elements (vertex of one)': [x[0] for x in stim if x[2] in infn],
                               'within_2mm_of_a_D30_element_vertex': [{'id': x[0], 'set': x[1], 'valid': x[3], 'mm': round(float(d), 2)} for x, d in zip(stim, dmin) if d <= 2.0],
                               'nearest_mm': round(float(dmin.min()), 2), 'nearest_id': stim[int(np.argmin(dmin))][0]}
    # where the D30 elements are
    Pf, Ef, tf = G.load_full(h)
    av, _ = G.aortic_frame(Pf, Ef, tf)
    zc = F['z'][Ex[filled]].mean(1)
    rec['b_D30_elements_where'] = {'z_ge_0.95': int((zc >= 0.95).sum()), 'z_le_0.05': int((zc <= 0.05).sum()), 'other': int(((zc > 0.05) & (zc < 0.95)).sum())}
    # (c) D25 revised
    lve, rve, epi = (read_vtx(os.path.join(S, x + '.vtx')) for x in ('lv_endo', 'rv_endo', 'epi'))
    dl, dr, de = (cKDTree(P[x]).query(P)[0] for x in (lve, rve, epi))
    ok = (np.abs(dl - dr) <= 0.5) & (de > dl) & (de > dr)
    v51 = json.load(open(os.path.join(B, 'sites.json')))
    anc = int(next(x['node'] for x in v51 if x['id'] == 'rvot_septal_z_d10'))
    cand = np.where(ok)[0]
    seg = np.asarray(PF.frame_labels(h, P, F['v_uvc'], P[cand])).astype(int)
    c2 = cand[seg == 2]
    p5 = json.load(open(os.path.join(HERE, f'previews2_sites_{h}.json')))
    old = int(p5['P5_focus']['focus_node'])
    r = {'qualifying_nodes': int(len(cand)), 'in_AHA_2': int(len(c2)), 'segments_of_qualifying_nodes': {str(k): int((seg == k).sum()) for k in np.unique(seg)},
         'P5_focus_node': old, 'anchor_node (v5.1 rvot_septal_z_d10)': anc}
    if len(c2):
        foc = int(c2[np.argmin(np.linalg.norm(P[c2] - P[anc], axis=1))])
        pv, _ = G.pulmonary_frame(Pf, Ef, tf)
        rvn = rve[np.argmin(np.linalg.norm(P[rve] - P[foc], axis=1))]
        SPx = Pf[int(p5['P3_groove_sector']['SP_full_node'])] if p5['P3_groove_sector'].get('SP_full_node') is not None else None
        r.update({'focus_node': foc, 'same_as_P5_focus': foc == old, 'AHA_segment': int(PF.frame_labels(h, P, F['v_uvc'], P[[foc]])[0]),
                  'distance_from_anchor_mm': round(float(np.linalg.norm(P[foc] - P[anc])), 2), 'z_converged': round(float(F['z'][foc]), 4),
                  'dist_LV_endo_RV_endo_epi_mm': [round(float(dl[foc]), 2), round(float(dr[foc]), 2), round(float(de[foc]), 2)],
                  'nearest_RV_endo_node_below_PV_mid_plane_mm': round(float(-pv.h(P[rvn])[0]), 2),
                  'distance_to_P3_SP_mm': round(float(np.linalg.norm(P[foc] - SPx)), 2) if SPx is not None else None,
                  'distance_from_P5_focus_mm': round(float(np.linalg.norm(P[foc] - P[old])), 2)})
    else:
        r['stop'] = 'AHA 2 has no qualifying node'
    rec['c_D25_revised'] = r
    G.dump(rec, os.path.join(HERE, f'preview_p9_{h}.json'))
    print(h, json.dumps({k: v for k, v in rec.items() if k != 'a_axis'}), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
