"""Read-only preview P10 (b), (d)-(g) (lock thread, relayed 21 Oct 2026 04:55 UTC). Report only; nothing is built, no fibre
file is written. (a) is preview_p10a.py; (c) is answered from previews2_sites_<H>.json.

Fields: the converged fields of previews2_fields.py (runs/v52_2026-10-20/02_geometry/<H>/converged/); LV side = v5.1's split
(C2); elements of the merged mesh, face adjacency of the cut mesh biv52cut (the simulation mesh).
l_raw = wgt g_basal + (1 - wgt) g_ot_lv with unit gradients (g = 0 where a gradient vanishes); wgt = w_LV (D20c) or the
converged w (the re-solved w.dat that fibres_fix.py reads), element means clipped to [0, 1].
D30 as widened (proposed): trigger |l_raw| < 0.01; face fill (a pass uses only l from earlier passes; mean under 0.01 ->
the lowest-id face neighbour that had l before the pass); any element the face fill cannot reach -> l of the nearest
LV-side element with l (centroid straight line, ties to the lowest id). w for t_out = D19b's APD w (neighbour fill as P8).
(b) D29: v5.1 LV PMJs (distal_lv) on a LV-side element with D20a's b = clip((z - 0.80) / 0.20, 0, 1) (1 - w_LV) > 0
    (element means), and the highest one's height relative to the aortic-valve mid-plane (D15 frame).
(d) D22: the distance from 8.3 step 2's point (sites52 summit_reanchored bifurcation_full_node) to the nearest tag-1 node
    of the full mesh's outer surface, beside B's projection distance.
(e) D30 counts, stimulus nodes, and the angle between the filled l and grad w (the D19b APD w) on D30 elements, folded
    to 0-90 deg (90 = l in the wall).
(f) D19b guard with the three changes: steps 2 mm mean, 4 mm mean, then (ordinary elements) v5.1's n = f x s reversed
    where n . grad w < 0, or (D30 elements and elements with no v5.1 row) t_out of the nearest passing element at any
    distance; each step's vector projected perpendicular to l and used only if that length is >= 0.01; else stop.
(g) D20c after D30: l from the converged w against l from w_LV, both with D30, at the gate stimulus nodes (normalised
    mean over the node's LV-side elements).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p10.py
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
import sites52 as S52                                                                       # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402
from preview_p9 import face_adjacency                                                       # noqa: E402

FF = Q.FF
unit = PF.unit
nrm = lambda x: np.linalg.norm(x, axis=-1)


def pct(a, q):
    return round(float(np.percentile(a, q)), 2)


def d30(lraw, Af, C, ids):
    """Widened D30 (proposed). Returns l, the trigger mask and the step counts."""
    trig = nrm(lraw) < 0.01
    l = unit(lraw); l[trig] = 0.0
    have = ~trig; per_pass, fb = [], 0
    while not have.all():
        hv = have.astype(float)
        sm = Af @ (l * hv[:, None]); cnt = Af @ hv
        new = ~have & (cnt > 0)
        if not new.any():
            break
        mean = sm[new] / cnt[new][:, None]; out = unit(mean)
        newi = np.where(new)[0]
        for k in np.where(nrm(mean) < 0.01)[0]:
            i = newi[k]; row = Af.indices[Af.indptr[i]:Af.indptr[i + 1]]; row = row[have[row]]
            out[k] = l[row[np.argmin(ids[row])]]; fb += 1
        l[new] = out; have = have | new; per_pass.append(int(new.sum()))
    left = np.where(~have)[0]; near = []
    if len(left):
        src = np.where(have)[0]; tr = cKDTree(C[src])
        for i in left:
            d, j = tr.query(C[i], k=8)
            tie = j[np.isclose(d, d[0], rtol=0, atol=1e-12)]
            k_ = src[tie][np.argmin(ids[src[tie]])]
            l[i] = l[k_]; near.append(round(float(d[0]), 2))
    return l, trig, {'trigger_|l_raw|_lt_0.01': int(trig.sum()), 'of_which_|l_raw|_eq_0': int((nrm(lraw) == 0).sum()),
                     'face_fill_per_pass': per_pass, 'face_fill_total': int(sum(per_pass)), 'lowest_id_fallbacks': fb,
                     'nearest_element_last_step': int(len(left)), 'nearest_element_distances_mm': near}


def run(h):
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); cv = os.path.join(G.RUN, h, 'converged')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, _ = read_elem(os.path.join(V, 'biv52'))
    Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, np.ones(len(E) - nb, bool)]
    F = {n: np.load(os.path.join(cv, n + '.npy')) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv', 'basal', 'ot_lv', 'w_LV', 'w', 'z')}
    pe, pl, pr = (np.clip(F[n], 0, 1) for n in ('phi_epi_fix', 'phi_lv', 'phi_rv'))
    ssum = pl + pr
    ds = np.where(ssum >= 1e-9, pr / np.maximum(ssum, 1e-30), np.nan)
    pairs = np.unique(np.sort(np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    N = len(P)
    A = coo_matrix((np.ones(2 * len(pairs)), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(N, N)).tocsr()
    while np.isnan(ds).any():
        has = ~np.isnan(ds); s_ = A @ np.where(has, ds, 0.0); c_ = A @ has.astype(float)
        new = np.isnan(ds) & (c_ > 0)
        if not new.any():
            break
        ds[new] = s_[new] / c_[new]
    wn = 1 - (1 - pe) * (1 - ds)
    ix = np.where(~RV)[0]; Ex = E[ix]; nl_ = len(ix); C = P[Ex].mean(1)
    loc = np.full(len(E), -1); loc[ix] = np.arange(nl_)
    ea, eb = face_adjacency(Ec)
    m = (loc[ea] >= 0) & (loc[eb] >= 0); a_, b_ = loc[ea[m]], loc[eb[m]]
    Af = coo_matrix((np.ones(2 * len(a_)), (np.r_[a_, b_], np.r_[b_, a_])), shape=(nl_, nl_)).tocsr()
    gb, go = unit(FF.elem_grad(P, Ex, F['basal'])), unit(FF.elem_grad(P, Ex, F['ot_lv']))
    wl = np.clip(np.nanmean(F['w_LV'][Ex], 1), 0, 1); wd = np.clip(F['w'][Ex].mean(1), 0, 1)
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    # (e) D30 widened, l from w_LV
    l, trig, cnt = d30(wl[:, None] * gb + (1 - wl[:, None]) * go, Af, C, ix)
    gw = FF.elem_grad(P, Ex, wn)
    ok = nrm(gw) > 0
    ang = np.degrees(np.arccos(np.clip(np.abs(np.sum(l * unit(gw), 1)), 0, 1)))
    a_d = ang[trig & ok]
    rec['e_fibres_fix_normalises'] = ("yes: fibres_fix.py lines 142-143 take unit(grad basal) and unit(grad ot_lv / ot_rv) before the w blend "
                                      "(w = element mean of w.dat, clipped; ot_rv where d > 0.5); the blend is not renormalised there but axis() "
                                      "normalises it as e1; unit() of a zero vector returns zero (division by max(|g|, 1e-30))")
    rec['e_D30_widened'] = cnt
    rec['e_angle_l_to_grad_w_on_D30_elements_deg (folded 0-90; 90 = l in the wall)'] = {
        'n': int(len(a_d)), 'median': pct(a_d, 50), 'p5': pct(a_d, 5), 'min': round(float(a_d.min()), 2),
        'D30 elements with grad w = 0 (not counted)': int((trig & ~ok).sum()),
        'for comparison, elements outside D30': {'median': pct(ang[~trig & ok], 50), 'p5': pct(ang[~trig & ok], 5)}}
    s52 = json.load(open(os.path.join(V, 'sites52.json')))
    stim = [(x['id'], x.get('set', ''), int(x['node'])) for x in s52['capture']]
    stim += [('gate7a_' + k, 'gate7a patch centre', int(x['node'])) for k, x in s52['gate7a_patch_centres'].items()]
    sn = np.array([x[2] for x in stim])
    fn = np.unique(Ex[trig])
    dmin = cKDTree(P[fn]).query(P[sn])[0]
    rec['e_stimulus_nodes'] = {'checked': len(stim), 'inside_D30_elements (vertex of one)': [x[0] for x in stim if x[2] in set(fn.tolist())],
                               'within_2mm_of_a_D30_element_vertex': [{'id': x[0], 'mm': round(float(d), 2)} for x, d in zip(stim, dmin) if d <= 2.0]}
    # (f) D19b guard with the three changes
    tr = gw - np.sum(l * gw, 1, keepdims=True) * l
    mag = nrm(tr); med = np.median(mag); bad = mag < 0.01 * med
    t = unit(tr)
    lon = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    n51 = unit(np.cross(lon[:, :3], lon[:, 3:6]))
    has_row = ix < len(lon)
    g = {'below_1pct_median': int(bad.sum()), 'of_which_D30': int((bad & trig).sum()), 'of_which_no_v51_row': int((bad & ~has_row).sum()),
         'step1_2mm_mean': 0, 'step1_rejected_short': 0, 'step2_4mm_mean': 0, 'step2_rejected_short': 0,
         'step3_v51_n': 0, 'step3_v51_n_reversed': 0, 'step3_rejected_short': 0,
         'step3_nearest_passing_any_distance (D30 / no row)': 0, 'step3_nearest_rejected_short': 0, 'stop': 0}
    goodi = np.where(~bad)[0]; tree = cKDTree(C[goodi])
    t_new = t.copy()
    for i in np.where(bad)[0]:
        done = False
        for rad, key in ((2.0, 'step1'), (4.0, 'step2')):
            q = tree.query_ball_point(C[i], rad)
            if q:
                v = t[goodi[q]].mean(0); v = v - (v @ l[i]) * l[i]
                if np.linalg.norm(v) >= 0.01:
                    t_new[i] = unit(v); g[key + ('_2mm_mean' if rad == 2.0 else '_4mm_mean')] += 1; done = True; break
                g[key + '_rejected_short'] += 1
        if done:
            continue
        if trig[i] or not has_row[i]:
            _, j = tree.query(C[i]); v = t[goodi[j]] - (t[goodi[j]] @ l[i]) * l[i]
            if np.linalg.norm(v) >= 0.01:
                t_new[i] = unit(v); g['step3_nearest_passing_any_distance (D30 / no row)'] += 1
            else:
                g['step3_nearest_rejected_short'] += 1; g['stop'] += 1
        else:
            v = n51[ix[i]].copy()
            if v @ gw[i] < 0:
                v = -v; g['step3_v51_n_reversed'] += 1
            v = v - (v @ l[i]) * l[i]
            if np.linalg.norm(v) >= 0.01:
                t_new[i] = unit(v); g['step3_v51_n'] += 1
            else:
                g['step3_rejected_short'] += 1; g['stop'] += 1
    rec['f_D19b_guard_changed'] = g
    # (b) D29
    zE = np.clip(F['z'][Ex].mean(1), 0, 1)
    bfac = np.clip((zE - 0.80) / 0.20, 0, 1) * (1 - wl)
    eon = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(nl_), 4))), shape=(N, nl_)).tocsr()
    net = np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz'))
    nodes, kind, pmj = net['nodes'], net['kind'].astype(str), net['pmj']
    lvp = nodes[pmj[kind[pmj] == 'distal_lv']]
    bmax = np.array([bfac[eon.indices[eon.indptr[n]:eon.indptr[n + 1]]].max() if eon.indptr[n + 1] > eon.indptr[n] else 0.0 for n in lvp])
    Pf, Ef, tf = G.load_full(h)
    av, _ = G.aortic_frame(Pf, Ef, tf)
    hit = lvp[bmax > 0]
    hb = av.h(P[hit]) if len(hit) else np.zeros(0)
    rec['b_D29_LV_PMJs_on_b_gt_0'] = {'LV_PMJs': int(len(lvp)), 'on_an_LV_side_element_with_b_gt_0': int(len(hit)),
                                      'highest_height_rel_aortic_mid_plane_mm (negative = below)': round(float(hb.max()), 2) if len(hb) else None,
                                      'their_max_b': round(float(bmax.max()), 3), 'LV_PMJs_with_no_LV_side_element': int(sum(eon.indptr[n + 1] == eon.indptr[n] for n in lvp))}
    # (d) D22 step-2 point
    s52h = json.load(open(os.path.join(HERE, f'sites52_{h}.json')))['summit_reanchored']
    p2 = int(s52h['bifurcation_full_node'])
    out = S52.outer_surface(Pf, Ef); on = np.unique(out)
    tl = np.zeros((len(Pf), 30), bool); tl[Ef.ravel(), np.repeat(tf, 4)] = True
    t1 = on[tl[on, 1]]
    dd, jj = cKDTree(Pf[t1]).query(Pf[p2])
    pj = json.load(open(os.path.join(HERE, f'preview_d22_projB_{h}.json')))
    rec['d_D22_step2_point'] = {'full_node': p2, 'tags_of_its_elements': sorted(int(x) for x in np.where(tl[p2])[0]), 'on_outer_surface': bool(p2 in set(on.tolist())),
                                'to_nearest_tag1_outer_surface_node_mm': round(float(dd), 2), 'B_projection_mm (projB, candidate quarter)': pj['projB']['projection_distance_mm'],
                                'passes_1.05mm (step-2 point to nearest tag-1 epicardial node)': bool(dd <= 1.05),
                                'B_passes_1.05mm': bool(pj['projB']['projection_distance_mm'] <= 1.05)}
    # (g) D20c after D30: l from converged w against l from w_LV
    l_w, trig_w, cnt_w = d30(wd[:, None] * gb + (1 - wd[:, None]) * go, Af, C, ix)
    rows = []
    for (sid, st, n) in stim:
        ee = eon.indices[eon.indptr[n]:eon.indptr[n + 1]]
        if not len(ee):
            continue
        a1, a2 = unit(l[ee].sum(0)), unit(l_w[ee].sum(0))
        rows.append((sid, float(np.degrees(np.arccos(np.clip(a1 @ a2, -1, 1)))), round(float(F['z'][n]), 3), round(float(wl[ee].mean()), 3), round(float(wd[ee].mean()), 3)))
    an = np.array([r[1] for r in rows]); k = int(np.argmax(an))
    rec['g_D20c_after_D30'] = {'D30_with_converged_w': cnt_w, 'stimulus_nodes_with_LV_side_elements': len(rows),
                               'angle_deg': {'median': pct(an, 50), 'p95': pct(an, 95), 'max': round(float(an.max()), 2)},
                               'largest_at': {'site': rows[k][0], 'z': rows[k][2], 'w_LV': rows[k][3], 'w': rows[k][4]},
                               'sites_over_10_deg': [{'site': r[0], 'deg': round(r[1], 1), 'z': r[2], 'w_LV': r[3], 'w': r[4]} for r in sorted(rows, key=lambda r: -r[1]) if r[1] > 10]}
    G.dump(rec, os.path.join(HERE, f'preview_p10_{h}.json'))
    print(h, json.dumps({k: v for k, v in rec.items() if k != 'e_fibres_fix_normalises'}), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
