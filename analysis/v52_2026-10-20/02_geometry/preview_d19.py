"""Read-only preview (a) for proposed deviation D19 (lock thread, relayed 20 Oct 2026 22:11 UTC): the Laplace fields
behind the LV transmural coordinate. Report only; nothing is built on it.

openCARP's Laplace solve (experiment 2) logs only its solver choice ("using default settings -ksp_type cg -pc_type hypre
-pc_hypre_type boomeramg ..."); it prints no iteration count or residual and ignores -ellip_options_file and
PETSC_OPTIONS (tried 21 Oct 2026, nothing was printed). Its tolerance parameters are cg_tol_ellip 1e-8 on the
preconditioned residual norm (cg_norm_ellip 0) and cg_maxit_ellip 500 (defaults). So the check is done outside openCARP:
  1. the same discrete problem is assembled here (P1 tetrahedra, unit isotropic conductivity, zero flux elsewhere,
     Dirichlet 0 / 1 on the same node sets, the "1" set winning) and the residual of openCARP's stored field is computed
     on the free nodes (absolute 2-norm and relative to the right-hand side);
  2. the same problem is re-solved here to a relative residual of 1e-12 (conjugate gradients, Jacobi preconditioner),
     and compared with the stored field;
  3. for both, the nodes more than 1e-3 outside [0, 1], and where they are: in parts that join the rest only through a
     node or an edge (outside the largest face-connected element set), in poor elements (minimum dihedral angle under
     5 deg or volume under 1 % of the median), or at nodes no element uses.
Fields: phi_epi_fix, phi_lv, phi_rv on v5.1's meshes and on the merged v5.2 meshes, and w_LV (LV-side submesh).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_d19.py [HEART ...]
"""
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import cg

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import laplace52 as L52                                                                     # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402


def stiffness(P, E):
    x = P[E]
    J = np.stack([x[:, 1] - x[:, 0], x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]], axis=1)          # rows = edges
    det = np.linalg.det(J); vol = np.abs(det) / 6
    Jinv = np.linalg.inv(J)                                                                   # columns: gradients of l1..l3
    G1 = np.concatenate([-Jinv.sum(2, keepdims=True), Jinv], axis=2)                          # (n, 3, 4): grads of the 4 shape fns
    Ke = np.einsum('nki,nkj->nij', G1, G1) * vol[:, None, None]
    r = np.repeat(E, 4, axis=1).ravel(); c = np.tile(E, (1, 4)).ravel()
    N = len(P)
    return coo_matrix((Ke.ravel(), (r, c)), shape=(N, N)).tocsr(), vol


def quality(P, E):
    x = P[E]
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    nrm = [np.cross(x[:, b] - x[:, a], x[:, c] - x[:, a]) for a, b, c in faces]
    nrm = [n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30) for n in nrm]
    dmin = np.full(len(E), 180.0)
    for i in range(4):
        for j in range(i + 1, 4):
            ang = 180 - np.degrees(np.arccos(np.clip(np.abs(np.sum(nrm[i] * nrm[j], 1)), 0, 1)))
            dmin = np.minimum(dmin, np.minimum(ang, 180 - ang))
    return dmin


def weak_nodes(E, N):
    F = np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]]); F.sort(1)
    k = (F[:, 0] * N + F[:, 1]) * N + F[:, 2]; el = np.tile(np.arange(len(E)), 4)
    o = np.argsort(k, kind='stable'); ks, es = k[o], el[o]; j = np.where(ks[1:] == ks[:-1])[0]
    _, lab = connected_components(coo_matrix((np.ones(len(j)), (es[j], es[j + 1])), shape=(len(E), len(E))), directed=False)
    big = np.argmax(np.bincount(lab))
    main = np.zeros(N, bool); main[np.unique(E[lab == big])] = True
    used = np.zeros(N, bool); used[np.unique(E)] = True
    return ~main & used, ~used, int(len(np.unique(lab))), int((lab != big).sum())


def describe(x, weak, unused, poorN):
    out = (x < -1e-3) | (x > 1 + 1e-3)
    nodes = np.where(out)[0]
    rec = {'min': round(float(x.min()), 5), 'max': round(float(x.max()), 5), 'nodes_outside_by_1e-3': int(len(nodes))}
    if len(nodes):
        rec.update({'at_unused_nodes': int(unused[nodes].sum()), 'in_weakly_joined_parts': int(weak[nodes].sum()),
                    'touching_poor_elements': int(poorN[nodes].sum()),
                    'other': int((~unused[nodes] & ~weak[nodes] & ~poorN[nodes]).sum()),
                    'largest_excursion': round(float(max(x.max() - 1, -x.min())), 4)})
    return rec


def check(K, x_ref, zero, one, weak, unused, poorN):
    N = K.shape[0]
    zero = np.setdiff1d(zero, one)
    D = np.zeros(N, bool); D[zero] = True; D[one] = True
    xD = np.zeros(N); xD[one] = 1.0
    free = np.where(~D & ~unused)[0]
    Kff = K[free][:, free]; b = -(K[free][:, np.where(D)[0]] @ xD[D])
    xr = x_ref.copy()
    res_ref = Kff @ xr[free] - b
    t0 = time.time()
    dinv = 1.0 / Kff.diagonal()
    xs, info = cg(Kff, b, x0=xr[free], rtol=1e-12, maxiter=20000, M=diags(dinv))
    xc = xr.copy(); xc[free] = xs; xc[D] = xD[D]
    res_c = Kff @ xs - b
    nb = float(np.linalg.norm(b))
    return {'free_nodes': int(len(free)), 'dirichlet_nodes': int(D.sum()), 'unused_nodes': int(unused.sum()),
            'stored_field': {'residual_2norm': float(np.linalg.norm(res_ref)), 'relative_residual': float(np.linalg.norm(res_ref) / nb),
                             'max_abs_residual': float(np.abs(res_ref).max()), 'dirichlet_values_exact': bool(np.allclose(xr[D], xD[D], atol=1e-6)),
                             **describe(xr, weak, unused, poorN)},
            'converged_resolve': {'cg_info': int(info), 'relative_residual': float(np.linalg.norm(res_c) / nb), 'wall_s': round(time.time() - t0, 1),
                                  'max_abs_change_from_stored': float(np.abs(xc - xr)[~unused].max()),
                                  **describe(np.where(unused, 0.5, xc), weak, unused, poorN),
                                  'all_used_nodes_within_1e-3_of_[0,1]': bool(((xc[~unused] >= -1e-3) & (xc[~unused] <= 1 + 1e-3)).all())}}


def run(h):
    t0 = time.time()
    B = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B, 'v52')
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'opencarp_solver': 'experiment 2: PETSc CG + hypre BoomerAMG (default settings); cg_tol_ellip 1e-8 on the preconditioned residual norm, cg_maxit_ellip 500; no iteration or residual output',
           'fields': {}, 'mesh': {}}
    m = json.load(open(os.path.join(HERE, f'merge52_{h}.json')))
    V5L = os.path.join(G.REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'laplace')
    variants = [('merged_v52', os.path.join(V, 'biv52'), os.path.join(V, 'surfaces'), {n: os.path.join(V, 'laplace') for n in ('phi_lv', 'phi_rv', 'phi_epi_fix')})]
    if not m['identical_to_v51']:
        variants.insert(0, ('v51', os.path.join(B, 'biv'), os.path.join(B, 'surfaces'), {'phi_lv': os.path.join(B, 'laplace'), 'phi_rv': os.path.join(B, 'laplace'), 'phi_epi_fix': V5L}))
    else:
        rec['note'] = 'merged mesh identical to v5.1: the v5.1 and merged fields are the same files'
    probs = {'phi_lv': (['rv_endo', 'epi'], ['lv_endo']), 'phi_rv': (['lv_endo', 'epi'], ['rv_endo']), 'phi_epi_fix': (['lv_endo', 'rv_endo'], ['epi', 'AO_OUTER'])}
    for vname, mesh, surf, stored in variants:
        P = read_pts(mesh) / 1e3; E, _ = read_elem(mesh)
        weak, unused, ncomp, nweak = weak_nodes(E, len(P))
        dmin = quality(P, E)
        K, vol = stiffness(P, E)
        poor = (dmin < 5.0) | (vol < 0.01 * np.median(vol))
        poorN = np.zeros(len(P), bool); poorN[np.unique(E[poor])] = True
        rec['mesh'][vname] = {'nodes': int(len(P)), 'unused_nodes': int(unused.sum()), 'face_connected_element_sets': ncomp,
                              'elements_outside_the_largest': nweak, 'poor_elements': int(poor.sum())}
        c = L52.Ctx(h, mesh, surf, '/tmp', '/tmp', '/tmp', 1)
        for nm, (z0, z1) in probs.items():
            x = np.loadtxt(os.path.join(stored[nm], nm + '.dat'))
            rec['fields'][f'{vname}/{nm}'] = r = check(K, x, c.vset(z0), c.vset(z1), weak, unused, poorN)
            print(h, vname, nm, 'stored rel.res', f"{r['stored_field']['relative_residual']:.2e}", 'outside', r['stored_field']['nodes_outside_by_1e-3'],
                  '| converged: outside', r['converged_resolve']['nodes_outside_by_1e-3'], 'max change', f"{r['converged_resolve']['max_abs_change_from_stored']:.2e}", flush=True)
    q = os.path.join(G.RUN, h, 'q12'); sub = os.path.join(q, 'lv_sub')
    P = read_pts(sub) / 1e3; E, _ = read_elem(sub)
    weak, unused, ncomp, nweak = weak_nodes(E, len(P)); dmin = quality(P, E); K, vol = stiffness(P, E)
    poor = (dmin < 5.0) | (vol < 0.01 * np.median(vol)); poorN = np.zeros(len(P), bool); poorN[np.unique(E[poor])] = True
    zero = read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc0.vtx')); one = read_vtx(os.path.join(q, 'oc', 'w_LV', 'bc1.vtx'))
    r = check(K, np.loadtxt(os.path.join(q, 'w_LV.dat')), zero, one, weak, unused, poorN)
    x = np.loadtxt(os.path.join(q, 'w_LV.dat'))
    r['stored_within_1e-6_of_[0,1]'] = bool(x.min() >= -1e-6 and x.max() <= 1 + 1e-6)
    rec['fields']['merged_v52/w_LV (LV-side submesh)'] = r
    rec['mesh']['lv_submesh'] = {'nodes': int(len(P)), 'face_connected_element_sets': ncomp, 'elements_outside_the_largest': nweak, 'poor_elements': int(poor.sum())}
    print(h, 'w_LV stored rel.res', f"{r['stored_field']['relative_residual']:.2e}", 'range', r['stored_field']['min'], r['stored_field']['max'], flush=True)
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'preview_d19_{h}.json'))
    print(h, 'done', rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
