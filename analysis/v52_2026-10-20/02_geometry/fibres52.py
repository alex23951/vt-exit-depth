"""v5.2 step 2a on the merged mesh: fix 5 fibres (LOCK.md section 6, R5.1-R5.3) with the adopted deviations
D19b (frame and guard), D20a, D20b (+90), D20c, D30 (with its added step), D31 and C2 (21 Oct 2026; records
relock4-build-answers-2026-10-20.md, sha256 ec3ea789...).

Regions (C2): old elements by v5.1's split R_field (d = phi_rv / (phi_lv + phi_rv) > 0.5 on v5.1's phi files, element
means; sha256 checked against doste_<H>.json); appended sleeve elements (tag 2) RV; appended crescent elements (tag 1, none
are built in these hearts) LV.
RV side: old elements copy v5.1's rows of bivF_v51.lon as text (bit-identical); sleeves circumferential (8.6): f = the
direction around the pulmonary axis, s = the pulmonary axis, n = f x s (radial).
LV side, on the converged fields of fields52.py (D19a):
  l = w_LV unit(grad basal) + (1 - w_LV) unit(grad ot_lv) (D20c; D31: the ot_lv branch on every LV-side element; w_LV
    element mean), normalised;
  D30: where that blend is under 0.01 long, l = the normalised mean l of face-adjacent LV-side elements of the cut mesh
    that have one (passes using only earlier values; under 0.01 -> the lowest-id such neighbour); elements no face path
    reaches take l of the nearest LV-side element with l (centroid, ties to the lowest id);
  w = nodal LV fibres w, 1 - (1 - phi_epi_fix)(1 - d_s), element w = mean of nodal w; M = median over LV-side elements
    of |grad w - (l . grad w) l| with the D30-filled l (used for every 1 % test below);
  D30's added step: in a D30 element with |grad w| >= 0.01 M, l is projected perpendicular to grad w and renormalised
    (so t_out = unit(grad w)); a projection under 0.01 keeps the filled l and goes to the guard; D30 elements with
    |grad w| < 0.01 M keep the filled l and go to the guard;
  t_out = normalise(grad w - (l . grad w) l); guard where that length is under 0.01 M (and the D30 elements above):
    the mean t_out of passing elements within 2 mm, then 4 mm (centroids, straight line), projected perpendicular to l;
    then v5.1's n = f x s of bivF_v51.lon, reversed where n . grad w < 0 (or, where |grad w| < 0.01 M, where it opposes
    the t_out of the nearest passing element), projected; on D30 elements and elements with no v5.1 row, the t_out of the
    nearest passing element at any distance instead of v5.1's n; each step used only if its projected length is >= 0.01;
    stop if the last step fails;
  c = l x t_out; alpha = (1 - b) (66 - 107 w) + b (+90 (1 - w)) with b = clamp((z - 0.80) / 0.20, 0, 1) (1 - w_LV)
    (element means; D20a, D20b); f = normalise(cos(alpha) c + sin(alpha) l); s = t_out x f; n = f x s (= t_out).
Outputs: data/biv/<H>/v52/biv52.lon and biv52cut.lon (same element order; header 2; LV and sleeve rows %.7f, RV rows
v5.1's text), fibres52_<H>.json here (acceptance R5.3, the D19b / D20 / D30 / D31 counts and reports).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/fibres52.py [HEART ...]
"""
import hashlib
import io
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q                                                                    # noqa: E402
import previews2_fields as PF                                                               # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402
from preview_p9 import face_adjacency                                                       # noqa: E402

FF = Q.FF
nrm = lambda x: np.linalg.norm(x, axis=-1)


def unit(v):
    return v / np.maximum(nrm(v)[..., None], 1e-30)


def line_angle(a, b):
    return np.degrees(np.arccos(np.clip(np.abs(np.sum(unit(a) * unit(b), -1)), 0, 1)))


def pstats(x):
    x = np.asarray(x)
    if not len(x):
        return None
    return {'n': int(len(x)), 'median': round(float(np.median(x)), 3), 'p95': round(float(np.percentile(x, 95)), 3),
            'p99': round(float(np.percentile(x, 99)), 3), 'max': round(float(x.max()), 3)}


def run(h):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); FD = os.path.join(V, 'fields52'); S = os.path.join(V, 'surfaces')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, tg = read_elem(os.path.join(V, 'biv52'))
    Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    nb = len(read_elem(os.path.join(B, 'biv'))[0])
    fl = lambda n: np.load(os.path.join(FD, n + '.npy'))
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'fields': json.load(open(os.path.join(HERE, f'fields52_{h}.json')))['files']}
    # ---------------- regions (C2)
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    Rf = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9) > 0.5
    sha_R = hashlib.sha256(np.ascontiguousarray(Rf.astype(np.uint8)).tobytes()).hexdigest()
    sha_51 = json.load(open(os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build', f'doste_{h}.json')))['R_field']['sha256']
    assert sha_R == sha_51, 'R_field differs from v5.1'
    sleeve = np.r_[np.zeros(nb, bool), tg[nb:] == 2]; cresc = np.r_[np.zeros(nb, bool), tg[nb:] == 1]
    RV = np.r_[Rf, tg[nb:] == 2]; LV = ~RV
    assert not (RV & LV).any() and (RV | LV).all()
    rec['regions'] = {'R_field_sha256 (= v5.1 doste)': sha_R, 'old_RV': int(Rf.sum()), 'old_LV': int((~Rf).sum()), 'sleeve': int(sleeve.sum()), 'crescent': int(cresc.sum())}
    ix = np.where(LV)[0]; Ex = E[ix]; nl = len(ix); C = P[Ex].mean(1)
    loc = np.full(len(E), -1); loc[ix] = np.arange(nl)
    # ---------------- fields (D19a)
    basal, otl, otr = fl('basal'), fl('ot_lv'), fl('ot_rv')
    wLV, z, pe, pl, pr, wn = fl('w_LV'), fl('z'), fl('phi_epi_fix'), fl('phi_lv'), fl('phi_rv'), fl('w_lvfib')
    wl = np.clip(np.nanmean(wLV[Ex], 1), 0, 1)
    assert not np.isnan(wl).any()
    # ---------------- l (D20c, D31)
    ub, uo = unit(FF.elem_grad(P, Ex, basal)), unit(FF.elem_grad(P, Ex, otl))
    lraw = wl[:, None] * ub + (1 - wl[:, None]) * uo
    de = em(pr, Ex) / np.maximum(em(pl, Ex) + em(pr, Ex), 1e-9)
    moved = (ix < nb) & (de > 0.5)
    if moved.any():
        alt = wl[moved, None] * ub[moved] + (1 - wl[moved, None]) * unit(FF.elem_grad(P, Ex[moved], otr))
        rec['D31'] = {'moved_elements (LV side by C2, converged d > 0.5)': int(moved.sum()),
                      'angle_l_otlv_vs_l_otrv_deg (vectors)': pstats(np.degrees(np.arccos(np.clip(np.sum(unit(lraw[moved]) * unit(alt), 1), -1, 1))))}
    else:
        rec['D31'] = {'moved_elements (LV side by C2, converged d > 0.5)': 0}
    # ---------------- D30
    trig = nrm(lraw) < 0.01
    l = unit(lraw); l[trig] = 0.0
    ea, eb = face_adjacency(Ec)
    m = (loc[ea] >= 0) & (loc[eb] >= 0); a_, b_ = loc[ea[m]], loc[eb[m]]
    Af = coo_matrix((np.ones(2 * len(a_)), (np.r_[a_, b_], np.r_[b_, a_])), shape=(nl, nl)).tocsr()
    have = ~trig; per_pass, fb = [], 0
    while not have.all():
        hv = have.astype(float)
        sm = Af @ (l * hv[:, None]); cnt = Af @ hv
        new = ~have & (cnt > 0)
        if not new.any():
            break
        mean = sm[new] / cnt[new][:, None]; out = unit(mean); newi = np.where(new)[0]
        for k in np.where(nrm(mean) < 0.01)[0]:
            i = newi[k]; row = Af.indices[Af.indptr[i]:Af.indptr[i + 1]]; row = row[have[row]]
            out[k] = l[row[np.argmin(ix[row])]]; fb += 1
        l[new] = out; have = have | new; per_pass.append(int(new.sum()))
    left = np.where(~have)[0]; near_d = []
    if len(left):
        src = np.where(have)[0]; tr_ = cKDTree(C[src])
        for i in left:
            d, j = tr_.query(C[i], k=8)
            tie = j[np.isclose(d, d[0], rtol=0, atol=1e-12)]
            k_ = src[tie][np.argmin(ix[src[tie]])]
            l[i] = l[k_]; near_d.append(round(float(d[0]), 2))
    D30 = {'trigger_|l_raw|_lt_0.01': int(trig.sum()), 'of_which_exactly_0': int((nrm(lraw) == 0).sum()), 'face_fill_per_pass': per_pass,
           'face_fill_total': int(sum(per_pass)), 'lowest_id_fallbacks': fb, 'nearest_element_last_step': int(len(left)), 'nearest_element_distances_mm': near_d}
    # ---------------- w, the guard median, D30's added step
    gw = FF.elem_grad(P, Ex, wn)
    tr = gw - np.sum(l * gw, 1, keepdims=True) * l
    M = float(np.median(nrm(tr)))
    gwn = nrm(gw)
    ang_before = 90 - line_angle(l, gw)                                  # tilt of the would-be t_out from grad w
    big = trig & (gwn >= 0.01 * M)
    lp = l - np.sum(l * unit(gw), 1, keepdims=True) * unit(gw)
    short = big & (nrm(lp) < 0.01)
    proj = big & ~short
    l[proj] = unit(lp[proj])
    tr = gw - np.sum(l * gw, 1, keepdims=True) * l
    mag = nrm(tr)
    M_after = float(np.median(mag))
    guard = (mag < 0.01 * M) | (trig & ~proj)
    D30.update({'guard_median_M (D30-filled l)': M, 'median_after_added_step': M_after,
                'added_step_projected': int(proj.sum()), 'added_step_short_projection_to_guard': int(short.sum()),
                'D30_with_|grad_w|_lt_0.01M_to_guard': int((trig & (gwn < 0.01 * M)).sum()),
                'tilt_before_step_deg (90 - angle(l, grad w)) on D30 elements': pstats(ang_before[trig & (gwn > 0)])})
    # ---------------- the guard (D19b)
    t = unit(tr); t[guard] = 0.0
    lon51 = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    f51, s51 = unit(lon51[:, :3]), unit(lon51[:, 3:6]); n51 = unit(np.cross(f51, s51))
    passing = np.where(~guard)[0]; tpass = cKDTree(C[passing]); tp = t[passing]
    norow = ix >= nb
    g = {'elements_under_1pct (or sent by D30)': int(guard.sum()), 'of_which_D30': int((guard & trig).sum()), 'of_which_no_v51_row': int((guard & norow).sum()),
         'step1_2mm': 0, 'step2_4mm': 0, 'step3_v51_n': 0, 'step3_v51_n_reversed': 0, 'step3_nearest_passing (D30 / no row)': 0,
         'rejected_short': {'step1': 0, 'step2': 0, 'step3': 0}, 'stop': 0, 'step_use_on_D30': {}, 'step_use_on_crescent': {}}
    stops = []
    for i in np.where(guard)[0]:
        done = None
        for rad, key in ((2.0, 'step1_2mm'), (4.0, 'step2_4mm')):
            q = tpass.query_ball_point(C[i], rad)
            if q:
                v = tp[q].mean(0); v = v - (v @ l[i]) * l[i]
                if np.linalg.norm(v) >= 0.01:
                    t[i] = unit(v); done = key; break
                g['rejected_short']['step1' if rad == 2.0 else 'step2'] += 1
        if done is None:
            if trig[i] or norow[i]:
                _, j = tpass.query(C[i]); v = tp[j] - (tp[j] @ l[i]) * l[i]; key = 'step3_nearest_passing (D30 / no row)'
            else:
                v = n51[ix[i]].copy()
                ref = gw[i] if gwn[i] >= 0.01 * M else tp[tpass.query(C[i])[1]]
                if v @ ref < 0:
                    v = -v; g['step3_v51_n_reversed'] += 1
                v = v - (v @ l[i]) * l[i]; key = 'step3_v51_n'
            if np.linalg.norm(v) >= 0.01:
                t[i] = unit(v); done = key
            else:
                g['rejected_short']['step3'] += 1; g['stop'] += 1; stops.append(int(ix[i]))
        if done:
            g[done] += 1
            if trig[i]:
                g['step_use_on_D30'][done] = g['step_use_on_D30'].get(done, 0) + 1
            if cresc[ix[i]]:
                g['step_use_on_crescent'][done] = g['step_use_on_crescent'].get(done, 0) + 1
    rec['D19b_guard'] = g
    if stops:
        rec['STOP'] = f'D19b guard: {len(stops)} elements with no usable t_out'
        G.dump(rec, os.path.join(HERE, f'fibres52_{h}.json')); print(h, rec['STOP'], flush=True); sys.exit(1)
    kept = trig & ~proj
    D30['tilt_of_t_out_from_grad_w_on_D30_elements_kept_with_filled_l_deg'] = pstats(line_angle(t[kept & (gwn > 0)], gw[kept & (gwn > 0)])) if (kept & (gwn > 0)).any() else None
    rec['D30'] = D30
    # ---------------- helix, outflow blend, frame
    we = wn[Ex].mean(1); ze = np.clip(z[Ex].mean(1), 0, 1)
    b = np.clip((ze - 0.80) / 0.20, 0, 1) * (1 - wl)
    a51 = 66 - 107 * we

    def frame(sign):
        al = np.radians((1 - b) * a51 + b * sign * 90 * (1 - we))
        c = unit(np.cross(l, t))
        f = unit(np.cos(al)[:, None] * c + np.sin(al)[:, None] * l)
        s = unit(np.cross(t, f))
        return f, s, np.cross(f, s), c
    f, s, n, c = frame(+1)
    # ---------------- sleeves (8.6): circumferential
    Pf, Ef, tf = G.load_full(h)
    pv, _ = G.pulmonary_frame(Pf, Ef, tf)
    isl = np.where(sleeve)[0]
    if len(isl):
        Cs = P[E[isl]].mean(1); r = Cs - pv.c; r -= np.outer(r @ pv.n, pv.n)
        fs = unit(np.cross(pv.n, r)); ss = np.tile(pv.n, (len(isl), 1)); ns = np.cross(fs, ss)
    # ---------------- write the .lon
    with open(os.path.join(B, 'fibres_v51', 'bivF_v51.lon')) as fh:
        hdr = fh.readline(); lines51 = fh.read().splitlines()
    assert len(lines51) == nb
    out_lines = [None] * len(E)
    for e in np.where(Rf)[0]:
        out_lines[e] = lines51[e]
    def fmt(F_, S_):
        buf = io.StringIO(); np.savetxt(buf, np.hstack([F_, S_]), fmt='%.7f'); return buf.getvalue().splitlines()
    for e, L_ in zip(ix, fmt(f, s)):
        out_lines[e] = L_
    if len(isl):
        for e, L_ in zip(isl, fmt(fs, ss)):
            out_lines[e] = L_
    assert all(x is not None for x in out_lines)
    txt = hdr + '\n'.join(out_lines) + '\n'
    for nm in ('biv52.lon', 'biv52cut.lon'):
        with open(os.path.join(V, nm), 'w') as fh:
            fh.write(txt)
    rec['files'] = {nm: {'path': os.path.relpath(os.path.join(V, nm), G.REPO), 'sha256': G.sha256(os.path.join(V, nm))} for nm in ('biv52.lon', 'biv52cut.lon')}
    # ---------------- acceptance R5.3 (and D19b's)
    lon = np.loadtxt(os.path.join(V, 'biv52.lon'), skiprows=1)
    fw, sw = lon[:, :3], lon[:, 3:6]; nw = np.cross(fw, sw)
    acc = {}
    # (1) LV free-wall angles at w = 0.1 / 0.5 / 0.9, b = 0, element d_s < 0.05; helix in the frame (c, l) of the grad w
    dse = fl('d_s')[Ex].mean(1)
    fwall = (b == 0) & (dse < 0.05)
    t_ind = unit(gw - np.sum(l * gw, 1, keepdims=True) * l); c_ind = unit(np.cross(l, t_ind))
    hel = np.degrees(np.arctan2(np.sum(f * l, 1), np.sum(f * c_ind, 1)))
    lev = {}
    for wv, tgt in ((0.1, 55.3), (0.5, 12.5), (0.9, -30.3)):
        mm = fwall & (np.abs(we - wv) <= 0.01) & ~guard
        lev[str(wv)] = {'target_deg': tgt, 'elements': int(mm.sum()), 'median_helix_deg': round(float(np.median(hel[mm])), 3),
                        'max_|helix - (66 - 107 w)|_deg': round(float(np.abs(hel[mm] - (66 - 107 * we[mm])).max()), 6),
                        'median_w_minus_phi_epi': round(float(np.median((we - pe[Ex].mean(1))[mm])), 4),
                        'max_w_minus_phi_epi': round(float((we - pe[Ex].mean(1))[mm].max()), 4)}
        lev[str(wv)]['pass'] = abs(lev[str(wv)]['median_helix_deg'] - tgt) <= 0.5
    acc['R5.3_free_wall_angles'] = lev
    # (2) RV region bit-identical to v5.1
    with open(os.path.join(V, 'biv52.lon')) as fh:
        fh.readline(); new_lines = fh.read().splitlines()
    acc['R5.3_RV_rows_bit_identical_to_v51'] = bool(all(new_lines[e] == lines51[e] for e in np.where(Rf)[0]))
    # (3) frames orthonormal (computed and as written), non-zero
    def ortho(F_, S_, N_):
        return {'min_norm': float(min(nrm(F_).min(), nrm(S_).min(), nrm(N_).min())), 'max_|norm-1|': float(max(np.abs(nrm(F_) - 1).max(), np.abs(nrm(S_) - 1).max(), np.abs(nrm(N_) - 1).max())),
                'max_|f.s|': float(np.abs(np.sum(F_ * S_, 1)).max()), 'max_|f.n|': float(np.abs(np.sum(F_ * N_, 1)).max()), 'max_|s.n|': float(np.abs(np.sum(S_ * N_, 1)).max())}
    acc['R5.3_orthonormal_LV_computed'] = ortho(f, s, n)
    acc['R5.3_orthonormal_LV_as_written'] = ortho(fw[ix], sw[ix], nw[ix])
    acc['R5.3_orthonormal_sleeve_as_written'] = ortho(fw[isl], sw[isl], nw[isl]) if len(isl) else None
    acc['n_equals_t_out_LV (max |n - t_out|)'] = float(nrm(n - t).max())
    acc['max_|l.t_out|'] = float(np.abs(np.sum(l * t, 1)).max())
    okc = acc['R5.3_orthonormal_LV_computed']
    acc['orthonormal_within_1e-6'] = bool(okc['min_norm'] > 0.5 and okc['max_|norm-1|'] <= 1e-6 and max(okc['max_|f.s|'], okc['max_|f.n|'], okc['max_|s.n|']) <= 1e-6)
    # (4) one connected fibre field (v5.1 A8: corner-sharing)
    nz = nrm(fw) > 0.5
    r_ = np.repeat(np.arange(len(E)), 4); cc_ = E.ravel() + len(E)            # element-node bipartite graph
    Nt = len(E) + len(P)
    _, labc = connected_components(coo_matrix((np.ones(len(r_)), (r_, cc_)), shape=(Nt, Nt)), directed=False)
    ncomp = int(len(np.unique(labc[:len(E)])))
    acc['R5.3_one_connected_fibre_field'] = {'elements_with_a_fibre': int(nz.sum()), 'of': int(len(E)), 'node_sharing_components': int(ncomp), 'pass': bool(nz.all() and ncomp == 1)}
    acc['all_pass'] = bool(all(v['pass'] for v in lev.values()) and acc['R5.3_RV_rows_bit_identical_to_v51'] and acc['orthonormal_within_1e-6']
                           and acc['R5.3_one_connected_fibre_field']['pass'])
    # D20a checks
    avr = read_vtx(os.path.join(S, 'av_rim.vtx')); avr = np.intersect1d(avr, np.unique(Ex))
    nod_b = np.clip((z - 0.80) / 0.20, 0, 1) * (1 - wLV)
    acc['D20a_checks'] = {'aortic_rim_LV_nodes': int(len(avr)), 'min_nodal_b_on_aortic_rim': round(float(np.nanmin(nod_b[avr])), 6) if len(avr) else None,
                          'elements_b_gt_0': int((b > 0).sum()), 'elements_b_gt_0_with_z_lt_0.80': int(((b > 0) & (ze < 0.80)).sum())}
    acc['D19b_sign_check'] = {'median_line_angle_f52_f51_deg_at_w_lt_0.1 (old LV elements)': round(float(np.median(line_angle(f[(we < 0.1) & (ix < nb)], f51[ix[(we < 0.1) & (ix < nb)]]))), 3),
                              'share_helix_lt_0_at_w_gt_0.9': round(float((hel[we > 0.9] < 0).mean()), 4)}
    rec['acceptance'] = acc
    # ---------------- reports
    rep = {}
    oldlv = ix < nb
    bands = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.01)]
    ang51 = line_angle(f[oldlv], f51[ix[oldlv]])
    rep['line_angle_v52_vs_v51_LV_by_w_band_deg'] = {f'{a}-{bb}': pstats(ang51[(we[oldlv] >= a) & (we[oldlv] < bb)]) for a, bb in bands}
    rep['C2_moved_elements_w_range'] = [round(float(we[moved].min()), 3), round(float(we[moved].max()), 3)] if moved.any() else None
    # neighbour steps on face-adjacent LV-side pairs: R5.1 alone, as built (D20a +90), v5.1 stored
    fa_, fb_ = loc[ea[m]], loc[eb[m]]
    keep_old = (ix[fa_] < nb) & (ix[fb_] < nb)
    al0 = np.radians(a51); c0 = unit(np.cross(l, t)); f0 = unit(np.cos(al0)[:, None] * c0 + np.sin(al0)[:, None] * l)
    def steps(F_):
        a = line_angle(F_[fa_], F_[fb_]); return {'pairs_over_30deg': int((a > 30).sum()), 'p99_deg': round(float(np.percentile(a, 99)), 2)}
    f51l = np.zeros_like(f); f51l[oldlv] = f51[ix[oldlv]]
    rep['D20a_neighbour_steps (face-adjacent LV-side pairs)'] = {'R5.1_alone': steps(f0), 'as_built (D20a, +90)': steps(f),
                                                                 'v51_stored (old-element pairs)': {'pairs_over_30deg': int((line_angle(f51l[fa_[keep_old]], f51l[fb_[keep_old]]) > 30).sum())}}
    # steps across v5.1's split: face pairs LV-side / RV-side old elements
    fa2, fb2 = face_adjacency(E)                                         # physical neighbours (merged mesh)
    lr = ((loc[fa2] >= 0) & Rf[np.minimum(fb2, nb - 1)] & (fb2 < nb)) | ((loc[fb2] >= 0) & Rf[np.minimum(fa2, nb - 1)] & (fa2 < nb))
    lvE = np.where(loc[fa2] >= 0, fa2, fb2)[lr]; rvE = np.where(loc[fa2] >= 0, fb2, fa2)[lr]
    fm, _, _, _ = frame(-1)
    rep['split_line_angle_step_deg'] = {'v52_LV_vs_v51_RV (all pairs)': pstats(line_angle(f[loc[lvE]], f51[rvE])),
                                        'v51_own_LV_vs_RV': pstats(line_angle(f51[lvE[lvE < nb]], f51[rvE[lvE < nb]])),
                                        'D20b: where b > 0.5, +90': pstats(line_angle(f[loc[lvE]][b[loc[lvE]] > 0.5], f51[rvE][b[loc[lvE]] > 0.5])),
                                        'D20b: where b > 0.5, -90': pstats(line_angle(fm[loc[lvE]][b[loc[lvE]] > 0.5], f51[rvE][b[loc[lvE]] > 0.5]))}
    wapd = fl('w_apd')
    ee_ = np.unique(np.r_[lvE, rvE])
    edp = np.unique(np.sort(np.concatenate([E[ee_][:, [a, bb]] for a, bb in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    rep['APD_w_step_along_split_edges'] = pstats(np.abs(wapd[edp[:, 0]] - wapd[edp[:, 1]]))
    # stimulus nodes: b and helix (mean over the node's LV-side elements)
    s52 = json.load(open(os.path.join(V, 'sites52.json')))
    eon = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(nl), 4))), shape=(len(P), nl)).tocsr()
    rows = []
    for x in s52['capture']:
        nd = int(x['node']); ee = eon.indices[eon.indptr[nd]:eon.indptr[nd + 1]]
        if len(ee):
            rows.append({'id': x['id'], 'set': x['set'], 'b': round(float(b[ee].mean()), 3), 'helix_deg': round(float(hel[ee].mean()), 2), 'w': round(float(we[ee].mean()), 3)})
    rep['stimulus_nodes_b_and_helix'] = rows
    # R5.4: signed helix per region, v5.2 against the cohort's own fibres (biv.lon) in the same frame
    lonc = np.loadtxt(os.path.join(B, 'biv.lon'), skiprows=1)
    fc = unit(lonc[ix[oldlv], :3])
    hc = np.degrees(np.arctan2(np.sum(fc * l[oldlv], 1), np.sum(fc * c_ind[oldlv], 1))); hc = (hc + 90) % 180 - 90
    h52 = (hel[oldlv] + 90) % 180 - 90
    sep_ = dse[oldlv] > 0.25
    reg = {}
    for nmr, mk in (('LV free wall', ~sep_), ('LV septum (d_s > 0.25)', sep_)):
        for a, bb in ((0, 0.2), (0.4, 0.6), (0.8, 1.01)):
            mm = mk & (we[oldlv] >= a) & (we[oldlv] < bb)
            reg[f'{nmr}, w {a}-{bb}'] = {'v52_median_helix': round(float(np.median(h52[mm])), 1), 'cohort_median_helix': round(float(np.median(hc[mm])), 1), 'elements': int(mm.sum())}
    rep['R5.4_signed_helix_vs_cohort_fibres'] = reg
    # D19a v5.1 limitation: fibres_fix.py's rule on converged fields against v5.1's stored LV rows (old LV elements)
    Eo = E[:nb][~Rf]
    wd = np.clip(fl('w')[Eo].mean(1), 0, 1); plo, pro, peo = (np.clip(fl(nm_)[Eo].mean(1), 0, 1) for nm_ in ('phi_lv', 'phi_rv', 'phi_epi_fix'))
    do = pro / np.maximum(plo + pro, 1e-9)
    gg = {nm_: FF.elem_grad(P, Eo, fl(nm_)) for nm_ in ('basal', 'ot_rv', 'ot_lv', 'phi_lv', 'phi_rv', 'phi_epi_fix')}
    g_ot = np.where((do > 0.5)[:, None], FF.unit(gg['ot_rv']), FF.unit(gg['ot_lv']))
    gpsi = wd[:, None] * FF.unit(gg['basal']) + (1 - wd[:, None]) * g_ot
    a_endo = np.radians(60 * wd + 90 * (1 - wd)); a_epi = np.radians(-60 * wd)
    a_s = a_endo * (1 - do) - a_endo * do; a_w = a_endo * (1 - peo) + a_epi * peo
    Qe = FF.bislerp(FF.orient(FF.axis(gpsi, -gg['phi_lv']), a_s), FF.orient(FF.axis(gpsi, gg['phi_rv']), a_s), do)
    Qx = FF.bislerp(Qe, FF.orient(FF.axis(gpsi, gg['phi_epi_fix']), a_w), peo)
    fff = FF.unit(Qx[:, :, 0])
    dlim = line_angle(fff, f51[:nb][~Rf])
    rep['D19a_v51_limitation: old LV elements where v5.1 stored f differs > 1 deg from its own rule on converged fields'] = {'elements': int((dlim > 1).sum()), 'of': int((~Rf).sum()), 'angle_deg': pstats(dlim)}
    rec['reports'] = rep
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'fibres52_{h}.json'))
    print(h, 'all_pass', acc['all_pass'], 'D30', {k: D30[k] for k in ('trigger_|l_raw|_lt_0.01', 'added_step_projected', 'nearest_element_last_step')},
          'guard', {k: g[k] for k in ('elements_under_1pct (or sent by D30)', 'step1_2mm', 'step2_4mm', 'step3_v51_n', 'step3_nearest_passing (D30 / no row)', 'stop')}, rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
