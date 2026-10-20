"""v5.2 step 2a, read-only measurements asked by the lock thread for questions Q1 (LV transmural coordinate) and Q2 (the
R5.2 outflow region), relayed by the coordinator 20 Oct 2026 21:45 UTC. Nothing is simulated; no fibre file is written.

Conventions (as v5.1's fibres_fix.py / doste_rv.py): element value = clip(mean of the element's nodal values, 0, 1);
gradients = the element's P1 gradient; d = phi_rv / (phi_lv + phi_rv); v5.1's LV frame axis(u, v): e1 = unit(u)
(longitudinal), e2 = v orthogonalised (transmural), e0 = e1 x e2 (circumferential); a fibre at angle a is
cos(a) e0 + sin(a) e1 (v5.1's sign: +60 deg at the LV endocardium).
Regions (clarification C2): RV region = v5.1's R_field (d > 0.5 on v5.1's fields, sha256-checked) plus the sleeves; LV
side = every other element of the merged mesh. v5.2 LV quantities use the re-solved fields (data/biv/<H>/v52).
The v5.2 R5.1 fibre here: w = 1 - phi_lv, alpha = 66 - 107 w, in axis(gpsi, grad w) with gpsi v5.1's longitudinal
field (w_doste grad basal + (1 - w_doste) grad ot_lv, unit vectors) on the re-solved fields.
R5.2 blend tested here: b = clamp((z - 0.80) / 0.20, 0, 1) (1 - w_ot); alpha = (1 - b) alpha_R5.1 + b alpha_OT,
alpha_OT = 90 (1 - w) + 0 w (Doste: 90 deg endocardial, 0 deg epicardial); mask (b) of the PC's Q2: b = clamp(...) where
w_ot < 0.5, else 0.
Usage (repo root, venv, PATH with mpiexec): python -B analysis/v52_2026-10-20/02_geometry/q12measure52.py [HEART ...]
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import laplace52 as L52                                                                     # noqa: E402
import sheet52 as S52                                                                       # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

FF = S52.module('ff', os.path.join(G.REPO, 'analysis', 'fibre_fix_2026-10-13', 'fibres_fix.py'))
AHA = S52.R34.AHA


def sha(f):
    return G.sha256(f)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-30)


def stats(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return {'n': int(len(x)), 'median': round(float(np.median(x)), 4), 'p95': round(float(np.percentile(x, 95)), 4),
            'max': round(float(x.max()), 4)} if len(x) else {'n': 0}


def face_pairs(E):
    F = np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]]); F.sort(1)
    N = int(E.max()) + 1
    k = (F[:, 0] * N + F[:, 1]) * N + F[:, 2]
    el = np.tile(np.arange(len(E)), 4)
    o = np.argsort(k, kind='stable'); ks, es = k[o], el[o]
    j = np.where(ks[1:] == ks[:-1])[0]
    return es[j], es[j + 1]


def line_angle(a, b):
    return np.degrees(np.arccos(np.clip(np.abs(np.sum(unit(a) * unit(b), -1)), 0, 1)))


def aha_labels(F, X):
    """aha51.Frame.label, vectorised over points by height (the local frame cached at heights rounded to 0.1 mm)."""
    f = F.f(X); out = np.zeros(len(X), int)
    c = F.cap_f
    lev = np.where(f < c + (1 - c) / 3, 'apical', np.where(f < c + 2 * (1 - c) / 3, 'mid', 'basal'))
    a = np.round(f * F.Lax, 1)
    cache = {}
    for av in np.unique(a[f >= c]):
        a_use = av; loc = F.local(a_use)
        while loc is None or np.isnan(loc[3]) or np.isnan(loc[4]):
            a_use = round(a_use - 1.0, 1)
            if a_use < 0:
                loc = None; break
            loc = F.local(a_use)
        cache[av] = loc
    out[f < c] = 17
    for i in np.where(f >= c)[0]:
        loc = cache[a[i]]
        if loc is None:
            continue
        c0, e1, e2, ia, ii = loc
        th = float(np.degrees(np.arctan2((X[i] - c0) @ e2, (X[i] - c0) @ e1)))
        if ii <= th <= ia:
            seg = 'septal' if lev[i] == 'apical' else ('anteroseptal' if th >= (ia + ii) / 2 else 'inferoseptal')
        else:
            fw = ((th - ia) % 360) / ((ii - ia) % 360)
            seg = (['anterior', 'lateral', 'inferior'][min(2, int(fw * 3))] if lev[i] == 'apical'
                   else ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))])
        out[i] = AHA.SEG_NO[(lev[i], seg)]
    return out


def run(h, np_=4):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52')
    V5L = os.path.join(G.REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'laplace')
    D51 = os.path.join(G.REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'laplace')
    P51 = read_pts(os.path.join(B, 'biv')) / 1e3; E51, t51 = read_elem(os.path.join(B, 'biv'))
    P = read_pts(os.path.join(V, 'biv52')) / 1e3; E, tg = read_elem(os.path.join(V, 'biv52'))
    nb = len(E51)
    f51 = lambda n, d=os.path.join(B, 'laplace'): np.loadtxt(os.path.join(d, n + '.dat'))
    f52 = lambda n: np.loadtxt(os.path.join(V, 'laplace', n + '.dat'))
    em = lambda u, EE: np.clip(u[EE].mean(1), 0, 1)
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    # regions (C2)
    R51 = em(f51('phi_rv'), E51) / np.maximum(em(f51('phi_lv'), E51) + em(f51('phi_rv'), E51), 1e-9) > 0.5
    shaR = hashlib.sha256(np.ascontiguousarray(R51.astype(np.uint8)).tobytes()).hexdigest()
    assert shaR == json.load(open(os.path.join(D51, 'laplace_info.json')))['R_field_sha256']
    RV = np.r_[R51, np.ones(len(E) - nb, bool)]                          # sleeves are RV region
    LVs = ~RV
    assert not (RV & LVs).any() and (RV | LVs).all()
    rec['regions'] = {'R_field_sha256': shaR, 'RV_region_elements': int(RV.sum()), 'LV_side_elements': int(LVs.sum()),
                      'partition_assertion': 'pass'}
    # moved elements (re-solved d > 0.5 but LV side) and their w
    Rnew = np.load(os.path.join(V, 'laplace', 'R_field.npy'))
    moved = np.where(LVs & Rnew)[0]
    w52 = 1 - em(f52('phi_lv'), E)
    rec['moved_elements_w_(1-phi_lv)_range'] = {'elements': int(len(moved)), **({'min': round(float(w52[moved].min()), 3), 'median': round(float(np.median(w52[moved])), 3),
                                               'max': round(float(w52[moved].max()), 3)} if len(moved) else {})}
    # 1. phi sum
    item1 = {}
    for nm, (PP, EE, lv_, fl) in {'v51': (P51, E51, ~R51, lambda n: f51(n, V5L) if n == 'phi_epi_fix' else f51(n)),
                                 'merged_v52': (P, E, LVs, f52)}.items():
        ssum = fl('phi_epi_fix') + fl('phi_lv') + fl('phi_rv')
        lvn = np.unique(EE[lv_])
        dev = np.abs(ssum[lvn] - 1)
        big = lvn[dev > 1e-3]
        S = os.path.join(B, 'surfaces') if nm == 'v51' else os.path.join(V, 'surfaces')
        ao = read_vtx(os.path.join(S, 'ao_iface.vtx'))
        dao = cKDTree(PP[ao]).query(PP[big])[0] if len(big) else np.zeros(0)
        eps = np.abs(em(fl('phi_epi_fix'), EE[lv_]) + em(fl('phi_lv'), EE[lv_]) + em(fl('phi_rv'), EE[lv_]) - 1)
        item1[nm] = {'nodal_max_abs_sum_minus_1': round(float(dev.max()), 4), 'nodes_over_1e-3': int(len(big)), 'of_LV_side_nodes': int(len(lvn)),
                     'their_distance_to_ao_iface_mm (median, p95, max)': [round(float(np.median(dao)), 2), round(float(np.percentile(dao, 95)), 2), round(float(dao.max()), 2)] if len(big) else None,
                     'element_max_abs_sum_minus_1': round(float(eps.max()), 4), 'elements_over_1e-3': int((eps > 1e-3).sum())}
    rec['item1_phi_sum'] = item1
    # 2. v5.1 LV fibres: inputs and regeneration
    files = {'w (Doste weight)': os.path.join(B, 'laplace', 'w.dat'), 'basal': os.path.join(B, 'laplace', 'basal.dat'),
             'ot_lv': os.path.join(V5L, 'ot_lv.dat'), 'ot_rv': os.path.join(V5L, 'ot_rv.dat'), 'phi_epi_fix': os.path.join(V5L, 'phi_epi_fix.dat'),
             'phi_lv': os.path.join(B, 'laplace', 'phi_lv.dat'), 'phi_rv': os.path.join(B, 'laplace', 'phi_rv.dat')}
    lon51 = np.loadtxt(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), skiprows=1)
    lv51 = np.where(~R51)[0]
    ld = {k: np.loadtxt(v) for k, v in files.items()}
    E_ = E51[lv51]
    wv = em(ld['w (Doste weight)'], E_)
    plv, prv, pepi = em(ld['phi_lv'], E_), em(ld['phi_rv'], E_), em(ld['phi_epi_fix'], E_)
    d_ = prv / np.maximum(plv + prv, 1e-9)
    gr = {n: FF.elem_grad(P51, E_, ld[n]) for n in ('basal', 'ot_rv', 'ot_lv', 'phi_lv', 'phi_rv', 'phi_epi_fix')}
    g_ot = np.where((d_ > 0.5)[:, None], unit(gr['ot_rv']), unit(gr['ot_lv']))
    gpsi = wv[:, None] * unit(gr['basal']) + (1 - wv[:, None]) * g_ot
    a_endo = np.radians(FF.A_ENDO * wv + FF.A_OT_ENDO * (1 - wv)); a_epi = np.radians(FF.A_EPI * wv + FF.A_OT_EPI * (1 - wv))
    a_s = a_endo * (1 - d_) - a_endo * d_; a_w = a_endo * (1 - pepi) + a_epi * pepi
    Q = FF.bislerp(FF.bislerp(FF.orient(FF.axis(gpsi, -gr['phi_lv']), a_s), FF.orient(FF.axis(gpsi, gr['phi_rv']), a_s), d_),
                   FF.orient(FF.axis(gpsi, gr['phi_epi_fix']), a_w), pepi)
    fr = unit(Q[:, :, 0])
    ang_reg = line_angle(fr, lon51[lv51, :3])
    rec['item2_v51_LV_fibres'] = {
        'generator': 'analysis/fibre_fix_2026-10-13/fibres_fix.py main() (v5 LDRB with the Doste outflow extension), rows kept in v5.1 outside R_field',
        'longitudinal_field': 'gpsi = w unit(grad basal) + (1 - w) unit(grad ot_lv) on the LV side (unit(grad ot_rv) where d > 0.5): a w_ot-blended l (Doste 2019 Eq. 1), not Bayer apex-base grad psi alone',
        'transmural_fields': 'bislerp of axis(gpsi, -grad phi_lv) / axis(gpsi, grad phi_rv) by d, then with axis(gpsi, grad phi_epi_fix) by phi_epi_fix',
        'files_sha256': {k: {'path': os.path.relpath(v, G.REPO), 'sha256': sha(v)} for k, v in files.items()},
        'stored_file': {'path': os.path.relpath(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'), G.REPO), 'sha256': sha(os.path.join(B, 'fibres_v51', 'bivF_v51.lon'))},
        'regeneration_angle_deg_LV_side': stats(ang_reg), 'regenerates_within_0.01_deg': bool(np.nanmax(ang_reg) <= 0.01),
        'elements_over_0.01_deg': int((ang_reg > 0.01).sum()), 'elements_over_1_deg': int((ang_reg > 1).sum()),
        'elements_over_0.01_deg_their_d_phi_epi_fix_w (median)': [round(float(np.median(d_[ang_reg > 0.01])), 3), round(float(np.median(pepi[ang_reg > 0.01])), 3),
                                                                  round(float(np.median(wv[ang_reg > 0.01])), 3)] if (ang_reg > 0.01).any() else None}
    # v5.2 R5.1 frame and fibre on the LV side (re-solved fields)
    ix = np.where(LVs)[0]; Ex = E[ix]
    L5 = {n: f52(n) for n in ('w', 'basal', 'ot_lv', 'phi_lv', 'phi_rv', 'phi_epi_fix', 'phi_D')}
    wd = em(L5['w'], Ex)
    gpsi52 = wd[:, None] * unit(FF.elem_grad(P, Ex, L5['basal'])) + (1 - wd[:, None]) * unit(FF.elem_grad(P, Ex, L5['ot_lv']))
    wl = 1 - em(L5['phi_lv'], Ex)
    Qf = FF.axis(gpsi52, -FF.elem_grad(P, Ex, L5['phi_lv']))            # grad w = -grad phi_lv
    e0, e1 = Qf[:, :, 0], Qf[:, :, 1]
    al = np.radians(66 - 107 * wl)
    fv52 = unit(np.cos(al)[:, None] * e0 + np.sin(al)[:, None] * e1)
    d52 = em(L5['phi_rv'], Ex) / np.maximum(em(L5['phi_lv'], Ex) + em(L5['phi_rv'], Ex), 1e-9)
    pe52 = em(L5['phi_epi_fix'], Ex)
    z52 = np.clip(np.loadtxt(os.path.join(V, 'uvc', 'z.dat'))[Ex].mean(1), 0, 1)
    pos = np.full(len(E), -1); pos[ix] = np.arange(len(ix))
    # 3. across the split
    a_, b_ = face_pairs(E[:nb])
    cross = R51[a_] != R51[b_]
    lvE = np.where(R51[a_[cross]], b_[cross], a_[cross]); rvE = np.where(R51[a_[cross]], a_[cross], b_[cross])
    dD = np.clip(1 - L5['phi_D'][E[rvE]].mean(1), 0, 1)
    w_lv = 1 - em(L5['phi_lv'], E[lvE])
    w_rv_alt = 1 - em(L5['phi_rv'], E[rvE])
    lon51m = np.vstack([lon51, np.tile([1.0, 0, 0, 0, 1, 0], (len(E) - nb, 1))])
    rec['item3_across_v51_split'] = {'face_pairs': int(cross.sum()),
                                     '(a) |w_LV (1 - phi_lv) - d_D RV (clip(1 - Phi_D))|': stats(np.abs(w_lv - dD)),
                                     '(b) |w_LV (1 - phi_lv) - (1 - phi_rv) RV|': stats(np.abs(w_lv - w_rv_alt)),
                                     '(c) fibre line angle, v5.2 LV (R5.1) vs v5.1 RV, deg': stats(line_angle(fv52[pos[lvE]], lon51m[rvE, :3])),
                                     '(c, reference) v5.1 LV vs v5.1 RV, deg': stats(line_angle(lon51m[lvE, :3], lon51m[rvE, :3]))}
    # 4. counts by d and phi_epi band; angle v5.2 vs v5.1 stored by d band
    old = ix < nb
    ang52_51 = np.full(len(ix), np.nan); ang52_51[old] = line_angle(fv52[old], lon51[ix[old], :3])
    dbands = [(0, 0.05), (0.05, 0.2), (0.2, 0.35), (0.35, 0.5), (0.5, 1.0)]
    pbands = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    rec['item4'] = {}
    for lo, hi in dbands:
        m = (d52 >= lo) & ((d52 < hi) if hi < 1 else (d52 <= hi))
        rec['item4'][f'd {lo}-{hi}'] = {'elements': int(m.sum()),
                                        'by_phi_epi_fix_band': {f'{a}-{b}': int((m & (pe52 >= a) & ((pe52 < b) if b < 1 else (pe52 <= b))).sum()) for a, b in pbands},
                                        'median_angle_v52_R5.1_vs_v51_stored_deg': round(float(np.nanmedian(ang52_51[m])), 2) if m.any() else None}
    # 5. sign check
    m5 = (wl < 0.1) & (d52 < 0.05) & (z52 < 0.80) & old
    h52 = np.degrees(np.arctan2(np.sum(fv52 * e1, 1), np.sum(fv52 * e0, 1)))
    h52 = (h52 + 90) % 180 - 90
    m9 = (wl > 0.9) & (d52 < 0.05)
    rec['item5_sign'] = {'free_wall_endo (w<0.1, d<0.05, z<0.80) elements': int(m5.sum()),
                         'median_acos|f52.f51|_deg': round(float(np.median(ang52_51[m5])), 2),
                         'epi (w>0.9, d<0.05) elements': int(m9.sum()), 'share_v52_h_lt_0': round(float(np.mean(h52[m9] < 0)), 4)}
    # 6. LV-only Doste weight w_LV on the LV-side submesh (zero flux at the septal split and everywhere else)
    lvn = np.unique(E[LVs]); loc = np.full(len(P), -1); loc[lvn] = np.arange(len(lvn))
    sub = os.path.join(G.RUN, h, 'q12', 'lv_sub'); os.makedirs(os.path.dirname(sub), exist_ok=True)
    with open(sub + '.pts', 'w') as fh:
        fh.write(f'{len(lvn)}\n'); np.savetxt(fh, P[lvn] * 1e3, fmt='%.6f')
    with open(sub + '.elem', 'w') as fh:
        fh.write(f'{int(LVs.sum())}\n'); np.savetxt(fh, np.c_[loc[E[LVs]], np.ones(int(LVs.sum()), np.int64)], fmt='Tt %d %d %d %d %d')
    with open(sub + '.lon', 'w') as fh:
        fh.write('2\n'); fh.write('1 0 0 0 1 0\n' * int(LVs.sum()))
    S = os.path.join(V, 'surfaces')
    inL = lambda n: loc[np.intersect1d(read_vtx(os.path.join(S, n + '.vtx')), lvn)]
    one = np.union1d(inL('apex_patch'), inL('mv_rim')); zero = inL('av_rim')
    c = L52.Ctx(h, sub, S, os.path.join(G.RUN, h, 'q12'), os.path.join(G.RUN, h, 'q12'), os.path.join(G.RUN, h, 'q12', 'oc'), np_)
    wLV_sub, info6 = c.solve('w_LV', zero, one, mesh=sub, out=os.path.join(G.RUN, h, 'q12'))
    wLV = np.full(len(P), np.nan); wLV[lvn] = wLV_sub
    zN = np.loadtxt(os.path.join(V, 'uvc', 'z.dat'))
    hi = lvn[zN[lvn] >= 0.80]
    dw = np.abs(wLV[hi] - L5['w'][hi]); dwc = np.abs(wLV[hi] - np.clip(L5['w'][hi], 0, 1))
    rec['item6_w_LV'] = {'solve': info6, 'bc1 (apex set + mitral rim, LV side)': int(len(one)), 'bc0 (aortic rim, LV side)': int(len(zero)),
                         'z>=0.80_nodes': int(len(hi)), 'max_abs_wLV_minus_w.dat': round(float(dw.max()), 4), 'median_abs_wLV_minus_w.dat': round(float(np.median(dw)), 4),
                         'w.dat_range_on_these_nodes': [round(float(L5['w'][hi].min()), 3), round(float(L5['w'][hi].max()), 3)],
                         'max_abs_wLV_minus_clip(w.dat,0,1)': round(float(dwc.max()), 4), 'median_abs_wLV_minus_clip(w.dat,0,1)': round(float(np.median(dwc)), 4)}
    # 7. z of the LV-side aortic-rim nodes
    avn = np.intersect1d(read_vtx(os.path.join(S, 'av_rim.vtx')), lvn)
    rec['item7_z_aortic_rim_LV_side'] = {'nodes': int(len(avn)), 'min': round(float(zN[avn].min()), 4), 'median': round(float(np.median(zN[avn])), 4), 'max': round(float(zN[avn].max()), 4)}
    # 8. blend weight b under option (a) and mask (b), for w_ot = w_LV and w.dat
    F = AHA.Frame(h)
    zb = np.clip((z52 - 0.80) / 0.20, 0, 1)
    pa, pb_ = face_pairs(Ex)
    item8 = {}
    seg_cache = None
    for wname, wn in (('w_LV', wLV), ('w.dat', L5['w'])):
        wo = np.clip(np.nanmean(wn[Ex], 1), 0, 1)
        for mname, b in (('option (a): b = zb (1 - w_ot)', zb * (1 - wo)), ('mask (b): b = zb where w_ot < 0.5', np.where(wo < 0.5, zb, 0.0))):
            al_b = (1 - b) * (66 - 107 * wl) + b * (90 * (1 - wl))
            fb = unit(np.cos(np.radians(al_b))[:, None] * e0 + np.sin(np.radians(al_b))[:, None] * e1)
            pos_b = b > 0
            if seg_cache is None:
                seg_cache = {}
            key = np.where(pos_b)[0]
            todo = np.setdiff1d(key, np.array(list(seg_cache.keys()), dtype=np.int64))
            if len(todo):
                lab = aha_labels(F, P[Ex[todo]].mean(1))
                seg_cache.update(dict(zip(todo.tolist(), lab.tolist())))
            segs = np.array([seg_cache[int(k)] for k in key]) if len(key) else np.zeros(0, int)
            bins_ = [(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0001)]
            cnt = {int(s): {f'{lo}-{min(hi, 1)}': int(((segs == s) & (b[key] > lo) & (b[key] <= hi)).sum()) for lo, hi in bins_} for s in np.unique(segs)}
            inv = np.full(len(P), np.nan)
            # b on aortic-rim nodes: mean b of the LV-side elements at each rim node
            rim_b = []
            nb_el = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(len(Ex)), 4))), shape=(len(P), len(Ex))).tocsr()
            for n in avn:
                ee = nb_el.indices[nb_el.indptr[n]:nb_el.indptr[n + 1]]
                rim_b.append(float(b[ee].mean()) if len(ee) else np.nan)
            near = (b[pa] > 0) | (b[pb_] > 0)
            stp = line_angle(fb[pa[near]], fb[pb_[near]])
            stp0 = line_angle(fv52[pa[near]], fv52[pb_[near]])
            item8[f'{wname} | {mname}'] = {'elements_b_gt_0': int(pos_b.sum()), 'by_AHA_segment_and_b_bin': cnt,
                                          'b_on_aortic_rim_nodes (min, median, max)': [round(float(np.nanmin(rim_b)), 3), round(float(np.nanmedian(rim_b)), 3), round(float(np.nanmax(rim_b)), 3)] if rim_b else None,
                                          'neighbour_angle_step_deg where b > 0 (max, p99.9, p99)': [round(float(stp.max()), 2), round(float(np.percentile(stp, 99.9)), 2), round(float(np.percentile(stp, 99)), 2)] if len(stp) else None,
                                          'same pairs under R5.1 alone (max, p99.9, p99)': [round(float(stp0.max()), 2), round(float(np.percentile(stp0, 99.9)), 2), round(float(np.percentile(stp0, 99)), 2)] if len(stp0) else None,
                                          'pairs, and pairs over 30 deg (blend, R5.1 alone)': [int(len(stp)), int((stp > 30).sum()), int((stp0 > 30).sum())],
                                          'largest increase of the step over R5.1 alone, deg': round(float((stp - stp0).max()), 2) if len(stp) else None}
    rec['item8_blend'] = item8
    # 8 (sites): v5.1 gate sites with b > 0 (the v5.2 site sets come with 2e)
    sites = json.load(open(os.path.join(B, 'sites.json')))
    elem_of_node = coo_matrix((np.ones(Ex.size), (Ex.ravel(), np.repeat(np.arange(len(Ex)), 4))), shape=(len(P), len(Ex))).tocsr()
    srows = []
    wo_l = np.clip(np.nanmean(wLV[Ex], 1), 0, 1); wo_d = np.clip(np.nanmean(L5['w'][Ex], 1), 0, 1)
    for s in sites:
        n = int(s['node']); ee = elem_of_node.indices[elem_of_node.indptr[n]:elem_of_node.indptr[n + 1]]
        if not len(ee):
            continue
        bl, bd = float((zb[ee] * (1 - wo_l[ee])).mean()), float((zb[ee] * (1 - wo_d[ee])).mean())
        if max(bl, bd) > 0:
            ww = float(wl[ee].mean())
            srows.append({'site': s['id'], 'family': s['family'], 'w_(1-phi_lv)': round(ww, 3), 'b_wLV': round(bl, 3), 'b_wdat': round(bd, 3),
                          'alpha_R5.1_deg': round(66 - 107 * ww, 1), 'alpha_blend_wLV_deg': round((1 - bl) * (66 - 107 * ww) + bl * 90 * (1 - ww), 1),
                          'alpha_blend_wdat_deg': round((1 - bd) * (66 - 107 * ww) + bd * 90 * (1 - ww), 1)})
    rec['item8_v51_sites_with_b_gt_0'] = srows
    rec['item8_gate5_eligible_v51_summit_site_with_b_gt_0'] = any(r['family'] == 'lv_summit' for r in srows)
    # 9. free wall: w vs normalised distance depth
    lve, epi = read_vtx(os.path.join(S, 'lv_endo.vtx')), read_vtx(os.path.join(S, 'epi.vtx'))
    fwn = np.unique(Ex[(d52 < 0.05)])
    dl_, de_ = cKDTree(P[lve]).query(P[fwn])[0], cKDTree(P[epi]).query(P[fwn])[0]
    nd = dl_ / np.maximum(dl_ + de_, 1e-9)
    wn = 1 - np.clip(L5['phi_lv'][fwn], 0, 1)
    rec['item9_free_wall_|w - normalised distance depth|'] = stats(np.abs(wn - nd))
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'q12measure52_{h}.json'))
    print(h, 'done', rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
