"""v5.2 step 2 (D19a, D19b; adopted 21 Oct 2026): the converged fields every later v5.2 rule reads.

D19a (Alex, card 1, 17:52:13 UTC): every Laplace and UVC field of the build re-solved on the merged mesh
(data/biv/<H>/v52/biv52) with the stored fields' boundary sets and 02_laplace.py's precedence (a node in both Dirichlet
sets takes 1), linear tetrahedra, unit isotropic conductivity, CG with a Jacobi preconditioner, to an unpreconditioned
relative residual ||r||2 / ||b||2 <= 1e-10 and on to 1e-12 (the same solver as preview P1, previews2_fields.py).
Acceptance: every field within 0.01 of [0, 1] before the clip, and the largest nodal change between the 1e-10 and 1e-12
solves under 1e-6; otherwise stop. Then clipped to [0, 1]. w_LV (D20a) on the LV-side submesh of q12measure52.py.
UVC: z = 03_uvc.py's remap of the clipped zeta; v = (v field > 0.5); phi geometric (copied); rho = phi_epi and
sep = phi_rv / (phi_lv + phi_rv) for reports.
D19b: d_s = phi_rv / (phi_lv + phi_rv); where phi_lv + phi_rv < 1e-9, the mean of d_s over the node's edge neighbours
that have a value from the solve or an earlier pass (each pass uses only earlier values), repeated until every node
has one. LV fibres w (nodal) = 1 - (1 - phi_epi_fix)(1 - d_s). APD w (R1.3, side per node): 1 - (1 - phi_epi_fix)(1 -
d_s) where d_s <= 0.5, 1 - (1 - phi_epi_fix) d_s where d_s > 0.5.
Outputs: data/biv/<H>/v52/fields52/*.npy (git-ignored) and fields52_<H>.json here (sha256 of every field, residuals,
acceptance, reports).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/fields52.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import laplace52 as L52                                                                     # noqa: E402
import preview_d19 as D19                                                                   # noqa: E402
import previews2_fields as PF                                                               # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

TOL_RANGE, TOL_CHANGE = 0.01, 1e-6


def sha_arr(x):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def run(h):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52'); S = os.path.join(V, 'surfaces')
    OUT = os.path.join(V, 'fields52'); os.makedirs(OUT, exist_ok=True)
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
    plv51, prv51 = (np.loadtxt(os.path.join(B, 'laplace', n + '.dat')) for n in ('phi_lv', 'phi_rv'))
    d51 = em(prv51, E[:nb]) / np.maximum(em(plv51, E[:nb]) + em(prv51, E[:nb]), 1e-9)
    RV = np.r_[d51 > 0.5, tg[nb:] == 2]                                   # C2: v5.1 split; appended sleeves (tag 2) RV, crescents (tag 1) LV
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'rule': 'D19a / D19b (adopted 21 Oct 2026); see the docstring',
           'precedence': 'a node in both Dirichlet sets takes 1 (02_laplace.py solve(): zero = setdiff(zero, one))',
           'solver': 'scipy CG, Jacobi preconditioner, unpreconditioned relative residual ||r||2 / ||b||2; 1e-10 then 1e-12',
           'fields': {}, 'files': {}}
    conv, stop = {}, []

    def accept(n, x10, x12, r10, r12, st=None):
        exc = float(max(x10.max() - 1, -x10.min(), 0))
        chg = float(np.abs(x12 - x10).max())
        r = {'relres_1e-10_solve': r10, 'relres_1e-12_solve': r12, 'max_nodal_change_1e-10_vs_1e-12': chg,
             'largest_excursion_outside_[0,1]_before_clip': round(exc, 6), 'nodes_outside_by_1e-3_before_clip': int(((x10 < -1e-3) | (x10 > 1 + 1e-3)).sum()),
             'pass': bool(exc <= TOL_RANGE and chg < TOL_CHANGE)}
        if st is not None:
            r['max_nodal_change_stored_vs_converged'] = float(np.abs(x10 - st).max())
            r['stored_nodes_outside_by_1e-3'] = int(((st < -1e-3) | (st > 1 + 1e-3)).sum())
        if not r['pass']:
            stop.append(n)
        return r
    for n, (z0, z1) in probs.items():
        x10, r10, _ = PF.solve(K, stored[n], z0, z1, 1e-10)
        x12, r12, _ = PF.solve(K, x10, z0, z1, 1e-12)
        rec['fields'][n] = accept(n, x10, x12, r10, r12, stored[n])
        conv[n] = np.clip(x10, 0, 1)
        print(h, n, f'{r10:.1e}', rec['fields'][n]['pass'], flush=True)
    # w_LV on the LV-side submesh (q12measure52.py's submesh and boundary sets)
    q = os.path.join(G.RUN, h, 'q12'); sub = os.path.join(q, 'lv_sub')
    Ps = read_pts(sub) / 1e3; Es, _ = read_elem(sub); Ks, _ = D19.stiffness(Ps, Es)
    wst = np.loadtxt(os.path.join(q, 'w_LV.dat'))
    z0, z1 = read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc0.vtx')), read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc1.vtx'))
    w10, r10, _ = PF.solve(Ks, wst, z0, z1, 1e-10); w12, r12, _ = PF.solve(Ks, w10, z0, z1, 1e-12)
    lvsub_nodes = np.unique(E[~RV])
    assert len(lvsub_nodes) == len(Ps) and np.allclose(P[lvsub_nodes], Ps), 'LV-side submesh does not match the merged mesh'
    rec['fields']['w_LV'] = accept('w_LV', w10, w12, r10, r12, wst)
    rec['fields']['w_LV']['submesh_nodes'] = int(len(Ps))
    wLV = np.full(len(P), np.nan); wLV[lvsub_nodes] = np.clip(w10, 0, 1); conv['w_LV'] = wLV
    if stop:
        rec['STOP'] = f'D19a acceptance failed for {stop}'
        G.dump(rec, os.path.join(HERE, f'fields52_{h}.json')); print(h, rec['STOP'], flush=True)
        sys.exit(1)
    # UVC
    apex = P[c.vtx('apex')[0]]; base_c = P[np.concatenate([c.vtx('mv_rim'), c.vtx('tv_rim')])].mean(0)
    conv['z'] = PF.zmap(conv['zeta'], P, apex, base_c)
    conv['v_uvc'] = (conv['v'] > 0.5).astype(float)
    conv['phi_uvc'] = np.loadtxt(os.path.join(V, 'uvc', 'phi.dat'))
    conv['rho'] = conv['phi_epi'].copy()
    pl, pr, pe = conv['phi_lv'], conv['phi_rv'], conv['phi_epi_fix']
    conv['sep'] = pr / np.maximum(pl + pr, 1e-9)
    z_st, v_st = np.loadtxt(os.path.join(V, 'uvc', 'z.dat')), np.loadtxt(os.path.join(V, 'uvc', 'v.dat'))
    rec['uvc'] = {'z_max_abs_change_from_stored': float(np.abs(conv['z'] - z_st).max()), 'v_nodes_changing_side': int((conv['v_uvc'] != v_st).sum()),
                  'phi': 'geometric (03_uvc.py), copied from uvc/phi.dat'}
    # D19b: d_s with the fill, LV fibres w, APD w
    ssum = pl + pr
    ds = np.where(ssum >= 1e-9, pr / np.maximum(ssum, 1e-30), np.nan)
    pairs = np.unique(np.sort(np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    N = len(P)
    A = coo_matrix((np.ones(2 * len(pairs)), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(N, N)).tocsr()
    todo, passes = int(np.isnan(ds).sum()), []
    while np.isnan(ds).any():
        has = ~np.isnan(ds)
        s_ = A @ np.where(has, ds, 0.0); c_ = A @ has.astype(float)
        new = np.isnan(ds) & (c_ > 0)
        if not new.any():
            break
        ds[new] = s_[new] / c_[new]; passes.append(int(new.sum()))
    if np.isnan(ds).any():
        rec['STOP'] = f'D19b fill left {int(np.isnan(ds).sum())} nodes without d_s'
        G.dump(rec, os.path.join(HERE, f'fields52_{h}.json')); print(h, rec['STOP'], flush=True)
        sys.exit(1)
    conv['d_s'] = ds
    conv['w_lvfib'] = 1 - (1 - pe) * (1 - ds)
    conv['w_apd'] = np.where(ds <= 0.5, 1 - (1 - pe) * (1 - ds), 1 - (1 - pe) * ds)
    lvn = np.unique(E[~RV])
    rec['D19b'] = {'nodes_with_phi_lv_plus_phi_rv_lt_1e-9': todo, 'fill_passes': len(passes), 'filled_per_pass': passes,
                   'LV_side_nodes_with_|phi_epi_fix + phi_lv + phi_rv - 1| > 1e-6 (share)': round(float((np.abs(pe[lvn] + pl[lvn] + pr[lvn] - 1) > 1e-6).mean()), 4),
                   'w_apd_range': [float(conv['w_apd'].min()), float(conv['w_apd'].max())]}
    names = ['zeta', 'z', 'v', 'v_uvc', 'phi_uvc', 'basal', 'ot', 'ot_lv', 'ot_rv', 'w', 'phi_epi', 'phi_epi_fix', 'phi_lv', 'phi_rv', 'u_lv', 'u_rv',
             'w_LV', 'rho', 'sep', 'd_s', 'w_lvfib', 'w_apd']
    for n in names:
        x = np.asarray(conv[n], dtype=np.float64)
        np.save(os.path.join(OUT, n + '.npy'), x)
        rec['files'][n] = {'path': os.path.relpath(os.path.join(OUT, n + '.npy'), G.REPO), 'sha256_of_array': sha_arr(x)}
    rec['LV_side'] = 'C2: v5.1 split (d = phi_rv / (phi_lv + phi_rv) > 0.5 on v5.1 phi files, element means) for old elements; appended tag 2 (sleeves) RV, tag 1 (crescents) LV'
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'fields52_{h}.json'))
    print(h, 'ok', rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
