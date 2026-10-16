"""Step 4.2 (v5.1 brief, decision C with DOSTE_SCOPE = WHOLE_RV, Alex 15 Oct 2026 08:31:14 UTC): Doste 2019 RV fibres.

Everything is per element, as the v5 fibres (fibres_fix.py): nodal Laplace fields from openCARP (experiment 2, unit
isotropic conductivity, as 02_laplace.py), element values = mean of the element's nodes, gradients = the element's P1
gradient (fibres_fix.elem_grad). "Nodes" of the brief are these elements; the fibre file has one row per element.

R_field = elements on the RV side of the v5 septal split, d = phi_rv / (phi_lv + phi_rv) > 0.5 (fibres_fix.py main(),
element means of data/biv/<H>/laplace/phi_lv, phi_rv, clipped to 0-1). R_new = R_field (WHOLE_RV). Elements outside R_new
keep their v5 rows (analysis/v5_grid_2026-10-13/fibres_E/<H>/bivF.lon) character for character.
  Phi_D   whole mesh: -2 on LV endocardium, +1 on RV endocardium, 0 on the outer surface (epi + aortic-root interface minus
          endocardial nodes, the 13 Oct phi_epi_fix outer set); zero flux elsewhere (valve rings / caps). Solved as
          Phi_D = -2 u_lv + u_rv with two unit problems (u_lv: LV endo 1, RV endo + outer 0; u_rv: RV endo 1, LV endo + outer 0).
  A       RV endocardial node with the lowest UVC z, plus RV endocardial nodes within 2 mm of it.
  on the R_field submesh (zero flux at the LV interface): Psi_TV (A 0, TV ring 1), Psi_PV (A 0, PV ring 1),
          w (A + TV ring 1, PV ring 0); rings = tv_rim / pv_rim nodes in R_field.
  g = w grad Psi_TV + (1 - w) grad Psi_PV (Doste Eq. 1); l = g / |g|; t = unit(grad Phi_D - (l . grad Phi_D) l), t_out = -t,
  c = l x t_out; d = clip(1 - Phi_D, 0, 1); h = 90 (1 - d) - 25 w d (deg); f = unit(cos h c + sin h l); n = t_out; s = n x f.
  h is the standard helix angle (LV subendocardium positive), so Doste's printed RV / outflow values apply unchanged; the
  Piersanti 2021 / lifex-fiber conventions (which mirror the RV) are not used. beta = 0 and no Eq. 5 septal blend (deviations).
Stages (repo root, venv, PATH with mpiexec):
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/doste_rv.py laplace   -> runs/v51_2026-10-15/04_build/<H>/laplace/
  HEART=<H> python -B analysis/v51_2026-10-15/04_build/doste_rv.py fibres    -> runs/v51_2026-10-15/04_build/<H>/bivF_v51_candidate.lon,
                                                                                analysis/v51_2026-10-15/04_build/doste_<H>.json
The candidate fibre file is not adopted: the official v5.1 fibre file is written only after Alex's choice at STOP 4a.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))
from common import BIV, HEART, OUT, read_elem, read_pts, read_vtx, write_vtx      # noqa: E402

RUN = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', HEART)
LAPD = os.path.join(RUN, 'laplace')
V5LON = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', HEART, 'bivF.lon')
V5LAP = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', HEART, 'laplace')
SURF = os.path.join(OUT, 'surfaces')
NP = int(os.environ.get('LAP_NP', '4'))
H_ENDO, H_EPI_W = 90.0, -25.0


def surf(n):
    return read_vtx(os.path.join(SURF, n + '.vtx'))


def sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-30)


def elem_grad(pts, E, u):
    """As fibres_fix.py elem_grad (v5's method)."""
    x0 = pts[E[:, 0]]
    J = np.stack([pts[E[:, 1]] - x0, pts[E[:, 2]] - x0, pts[E[:, 3]] - x0], axis=1)
    du = np.stack([u[E[:, 1]] - u[E[:, 0]], u[E[:, 2]] - u[E[:, 0]], u[E[:, 3]] - u[E[:, 0]]], axis=1)
    return np.linalg.solve(J, du[..., None])[..., 0]


def r_field(E):
    lap = lambda n: np.loadtxt(os.path.join(OUT, 'laplace', n + '.dat'))
    plv, prv = (np.clip(lap(n)[E].mean(1), 0, 1) for n in ('phi_lv', 'phi_rv'))
    return prv / np.maximum(plv + prv, 1e-9) > 0.5


def outer_set():
    endo = np.concatenate([surf('lv_endo'), surf('rv_endo')])
    return np.unique(np.concatenate([surf('epi'), np.setdiff1d(surf('ao_iface'), endo)]))


def opencarp(mesh, name, zero, one):
    """One unit Laplace problem as 02_laplace.py solve(): zero -> 0 (ground), one -> 1; the "1" set wins on overlap."""
    zero = np.setdiff1d(zero, one)
    d = os.path.join(LAPD, name); os.makedirs(d, exist_ok=True)
    write_vtx(os.path.join(d, 'bc0.vtx'), zero); write_vtx(os.path.join(d, 'bc1.vtx'), one)
    cmd = ['mpiexec', '-n', str(NP), 'openCARP', '-experiment', 2, '-bidomain', 1, '-meshname', mesh, '-simID', d,
           '-num_gregions', 1, '-gregion[0].num_IDs', 0,
           '-gregion[0].g_il', 1, '-gregion[0].g_it', 1, '-gregion[0].g_in', 1,
           '-gregion[0].g_el', 1, '-gregion[0].g_et', 1, '-gregion[0].g_en', 1,
           '-num_stim', 2,
           '-stim[0].crct.type', 3, '-stim[0].elec.vtx_file', os.path.join(d, 'bc0'),
           '-stim[1].crct.type', 2, '-stim[1].elec.vtx_file', os.path.join(d, 'bc1'),
           '-stim[1].pulse.strength', 1.0, '-stim[1].ptcl.duration', 1.0]
    t0 = time.time()
    with open(os.path.join(d, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    out = os.path.join(LAPD, name + '.dat')
    subprocess.run(['igbextract', '-o', 'ascii', '-O', out, os.path.join(d, 'phie.igb')], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    x = np.loadtxt(out)
    if x.ndim > 1:
        x = x[-1]; np.savetxt(out, x, fmt='%.6g')
    print(f'  {name}: {time.time() - t0:.0f} s, min {x.min():.4f} max {x.max():.4f}, bc0 {len(zero)} bc1 {len(one)}', flush=True)
    return x, {'bc0': int(len(zero)), 'bc1': int(len(one)), 'min': float(x.min()), 'max': float(x.max()), 'wall_s': round(time.time() - t0, 1)}


def laplace():
    t0 = time.time()
    os.makedirs(LAPD, exist_ok=True)
    pts_um = read_pts(BIV); pts = pts_um / 1e3
    E, tag = read_elem(BIV)
    R = r_field(E)
    lv, rv, outer = surf('lv_endo'), surf('rv_endo'), outer_set()
    info = {'heart': HEART, 'R_field_elements': int(R.sum()), 'R_field_sha256': sha(R.astype(np.uint8)), 'mesh_elements': int(len(E)),
            'overlap_lv_rv_endo': int(len(np.intersect1d(lv, rv))), 'problems': {}}
    # Phi_D on the whole mesh (superposition of two unit problems)
    u_lv, info['problems']['u_lv'] = opencarp(BIV, 'u_lv', np.union1d(rv, outer), lv)
    u_rv, info['problems']['u_rv'] = opencarp(BIV, 'u_rv', np.union1d(lv, outer), rv)
    phid = -2.0 * u_lv + u_rv
    np.savetxt(os.path.join(LAPD, 'phi_D.dat'), phid, fmt='%.8g')
    # apex set A
    z = np.loadtxt(os.path.join(OUT, 'uvc', 'z.dat'))
    a0 = rv[np.argmin(z[rv])]
    A = rv[np.linalg.norm(pts[rv] - pts[a0], axis=1) <= 2.0]
    apex_lv = int(json.load(open(os.path.join(OUT, 'summary_02.json')))['apex_node'])
    tv_all, pv_all = surf('tv_rim'), surf('pv_rim')
    info['apex_A'] = {'seed_node': int(a0), 'seed_uvc_z': float(z[a0]), 'nodes': int(len(A)),
                      'distance_to_LV_apex_mm': round(float(np.linalg.norm(pts[a0] - pts[apex_lv])), 1),
                      'distance_to_TV_ring_centroid_mm': round(float(np.linalg.norm(pts[a0] - pts[tv_all].mean(0))), 1)}
    # R_field submesh
    ER = E[R]
    nodes = np.unique(ER)
    loc = np.full(len(pts), -1, np.int64); loc[nodes] = np.arange(len(nodes))
    sub = os.path.join(LAPD, 'rv_sub')
    with open(sub + '.pts', 'w') as fh:
        fh.write(f'{len(nodes)}\n'); np.savetxt(fh, pts_um[nodes], fmt='%.6f')
    with open(sub + '.elem', 'w') as fh:
        fh.write(f'{len(ER)}\n'); np.savetxt(fh, np.hstack([loc[ER], np.ones((len(ER), 1), np.int64)]), fmt='Tt %d %d %d %d %d')
    lon = open(V5LON).read().split('\n')
    rows = np.where(R)[0]
    with open(sub + '.lon', 'w') as fh:
        fh.write(lon[0] + '\n'); fh.write('\n'.join(lon[1 + i] for i in rows) + '\n')
    np.save(os.path.join(LAPD, 'rv_sub_nodes.npy'), nodes)
    inR = lambda s: loc[np.intersect1d(s, nodes)]
    tvR, pvR, AR = inR(tv_all), inR(pv_all), inR(A)
    info['rings_in_R_field'] = {'TV': int(len(tvR)), 'TV_all': int(len(tv_all)), 'PV': int(len(pvR)), 'PV_all': int(len(pv_all)),
                                'A_in_R': int(len(AR)), 'TV_PV_overlap': int(len(np.intersect1d(tvR, pvR))),
                                'A_ring_overlap': int(len(np.intersect1d(AR, np.union1d(tvR, pvR))))}
    psi_tv, info['problems']['psi_tv'] = opencarp(sub, 'psi_tv', AR, tvR)
    psi_pv, info['problems']['psi_pv'] = opencarp(sub, 'psi_pv', AR, pvR)
    w, info['problems']['w'] = opencarp(sub, 'w', pvR, np.union1d(AR, tvR))
    info['wall_s'] = round(time.time() - t0, 1)
    json.dump(info, open(os.path.join(LAPD, 'laplace_info.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in info.items() if k != 'problems'}, indent=1))


# ------------------------------------------------------------------ fibres and gates
def fold(h):
    return (h + 90.0) % 180.0 - 90.0


def face_keys(E, N):
    """Sorted face triples of every element as one int64 key each: (4 * n_elem,) keys and the element of each."""
    F = np.concatenate([E[:, [0, 1, 2]], E[:, [0, 1, 3]], E[:, [0, 2, 3]], E[:, [1, 2, 3]]])
    F.sort(axis=1)
    return F[:, 0] * N * N + F[:, 1] * N + F[:, 2], np.tile(np.arange(len(E)), 4)


def fibres():
    t0 = time.time()
    pts = read_pts(BIV) / 1e3
    E, tag = read_elem(BIV)
    N, C = len(pts), pts[E].mean(1)
    R = r_field(E); rows = np.where(R)[0]
    info = json.load(open(os.path.join(LAPD, 'laplace_info.json')))
    assert info['R_field_sha256'] == sha(R.astype(np.uint8))
    nodes = np.load(os.path.join(LAPD, 'rv_sub_nodes.npy'))
    loc = np.full(N, -1, np.int64); loc[nodes] = np.arange(len(nodes))
    ER = loc[E[R]]; P_R = pts[nodes]
    rd = lambda n: np.loadtxt(os.path.join(LAPD, n + '.dat'))
    phid = rd('phi_D'); psi_tv, psi_pv, w_n = rd('psi_tv'), rd('psi_pv'), rd('w')
    G = {}
    # guards: w clip, small gradients
    G['w_nodes_clipped'] = int(((w_n < 0) | (w_n > 1)).sum())
    w = np.clip(np.clip(w_n, 0, 1)[ER].mean(1), 0, 1)
    gtv, gpv = elem_grad(P_R, ER, psi_tv), elem_grad(P_R, ER, psi_pv)
    g = w[:, None] * gtv + (1 - w[:, None]) * gpv
    gD = elem_grad(pts, E[R], phid)
    CR = C[R]

    def repair(v, name):
        mag = np.linalg.norm(v, axis=1)
        bad = mag < 0.01 * np.median(mag)
        u = unit(v)
        if bad.any():
            tree = cKDTree(CR[~bad]); good_u = u[~bad]
            for i in np.where(bad)[0]:
                nb = tree.query_ball_point(CR[i], 2.0)
                if nb:
                    u[i] = unit(good_u[nb].mean(0))
                else:
                    u[i] = good_u[tree.query(CR[i])[1]]
                    G[f'{name}_no_neighbour_within_2mm'] = G.get(f'{name}_no_neighbour_within_2mm', 0) + 1
        G[f'{name}_below_1pct_median'] = int(bad.sum())
        return u
    l = repair(g, 'g')
    uD = repair(gD, 'grad_phi_D')
    tr = uD - np.sum(l * uD, 1, keepdims=True) * l
    t = unit(tr)
    # guard (not in the brief's rule): where grad Phi_D is (nearly) parallel to l, the transmural direction is
    # undefined; use the normalised mean of passing neighbours within 2 mm, as for small gradients
    degen = np.linalg.norm(tr, axis=1) < 0.01
    if degen.any():
        tree = cKDTree(CR[~degen]); good_t = t[~degen]
        for i in np.where(degen)[0]:
            nb = tree.query_ball_point(CR[i], 2.0)
            t[i] = unit(good_t[nb].mean(0)) if nb else good_t[tree.query(CR[i])[1]]
    G['transmural_degenerate_(grad_phi_D_parallel_to_l)'] = int(degen.sum())
    t = unit(t - np.sum(l * t, 1, keepdims=True) * l)            # exactly perpendicular to l
    t_out = -t
    c = unit(np.cross(l, t_out))
    d = np.clip(1.0 - phid[E[R]].mean(1), 0, 1)
    h_exp = H_ENDO * (1 - d) + H_EPI_W * w * d
    hr = np.radians(h_exp)
    f = unit(np.cos(hr)[:, None] * c + np.sin(hr)[:, None] * l)
    n = unit(t_out - np.sum(t_out * f, 1, keepdims=True) * f)
    s = np.cross(n, f)
    # candidate fibre file: v5 rows verbatim outside R_new
    lon = open(V5LON).read().split('\n')
    hdr, body = lon[0], lon[1:1 + len(E)]
    new_rows = [f'{a:.5f} {b:.5f} {cc:.5f} {x:.5f} {y:.5f} {zz:.5f}' for a, b, cc, x, y, zz in np.hstack([f, s])]
    for k, i in enumerate(rows):
        body[i] = new_rows[k]
    cand = os.path.join(RUN, 'bivF_v51_candidate.lon')
    with open(cand, 'w') as fh:
        fh.write(hdr + '\n' + '\n'.join(body) + '\n')
    Lw = np.loadtxt(cand, skiprows=1)
    L5 = np.loadtxt(V5LON, skiprows=1)
    fw, sw = Lw[rows, :3], Lw[rows, 3:6]
    # A1
    hm = np.degrees(np.arctan2(np.sum(fw * l, 1), np.sum(fw * c, 1)))
    dh = (hm - h_exp + 90.0) % 180.0 - 90.0
    oop = np.degrees(np.arcsin(np.clip(np.abs(np.sum(fw * t_out, 1)) / np.linalg.norm(fw, axis=1), 0, 1)))
    A1 = {'max_abs_dh_deg': float(np.abs(dh).max()), 'p99_abs_dh_deg': float(np.percentile(np.abs(dh), 99)),
          'max_out_of_plane_deg': float(oop.max()), 'p99_out_of_plane_deg': float(np.percentile(oop, 99))}
    A1['pass'] = bool(A1['max_abs_dh_deg'] <= 0.5 and A1['max_out_of_plane_deg'] <= 0.5)
    # A4
    e4 = d <= 0.02
    ang4 = np.degrees(np.arccos(np.clip(np.abs(np.sum(fw[e4] * l[e4], 1)) / np.linalg.norm(fw[e4], axis=1), 0, 1)))
    A4 = {'elements_d_le_0.02': int(e4.sum()), 'max_deg': float(ang4.max()) if len(ang4) else None,
          'p99_deg': float(np.percentile(ang4, 99)) if len(ang4) else None,
          'elements_over_0.5deg': int((ang4 > 0.5).sum()), 'pass': bool(len(ang4) and ang4.max() <= 0.5),
          'expected_by_rule_at_d_max': 'the rule gives 90 - h = d (90 + 25 w), i.e. up to 2.3 deg at d = 0.02'}
    # A5
    same_rows = all(body[i] == lon[1 + i] for i in np.where(~R)[0])
    diff = np.where(~R & np.any(Lw != L5, axis=1))[0]                 # parsed values, outside R_new
    ang5 = np.degrees(np.arccos(np.clip(np.abs(np.sum(unit(Lw[diff, :3]) * unit(L5[diff, :3]), 1)), 0, 1))) if len(diff) else np.zeros(1)
    A5 = {'elements_outside_R_new': int((~R).sum()), 'rows_identical_text': bool(same_rows), 'rows_changed': int(len(diff)),
          'max_change_deg': float(ang5.max()), 'pass': bool(same_rows and len(diff) == 0)}
    # A8: connectivity (shared faces) and orthonormality
    keys, el = face_keys(E[R], N)
    o = np.argsort(keys, kind='stable'); ks, es = keys[o], el[o]
    dup = np.where(ks[1:] == ks[:-1])[0]
    adj = coo_matrix((np.ones(len(dup)), (es[dup], es[dup + 1])), shape=(len(rows), len(rows)))
    ncomp, lab = connected_components(adj, directed=False)
    sizes = np.bincount(lab)
    ER_all = E[R]
    ne = len(ER_all)                                                  # element-node bipartite graph: node-sharing connectivity
    bip = coo_matrix((np.ones(4 * ne), (np.repeat(np.arange(ne), 4), ne + ER_all.ravel())), shape=(ne + N, ne + N))
    lab_bn = connected_components(bip, directed=False)[1]
    ncomp_node = int(len(np.unique(lab_bn[:ne])))
    small_comp = [int(k) for k in np.where(sizes < sizes.max())[0]]
    island = np.where(np.isin(lab, small_comp))[0]
    orth = {'max_abs_norm_f_minus_1': float(np.abs(np.linalg.norm(fw, axis=1) - 1).max()),
            'max_abs_norm_s_minus_1': float(np.abs(np.linalg.norm(sw, axis=1) - 1).max()),
            'max_abs_f_dot_s': float(np.abs(np.sum(fw * sw, 1)).max())}
    A8 = {'R_field_components_face_sharing': int(ncomp), 'R_field_components_node_sharing': int(ncomp_node),
          'R_new_components_face_sharing': int(ncomp), 'largest_component_elements': int(sizes.max()),
          'other_components_elements': int(sizes.sum() - sizes.max()),
          'island_elements': [{'element': int(rows[i]), 'tag': int(tag[rows[i]]), 'centroid_mm': C[rows[i]].round(1).tolist()} for i in island],
          'orthonormal_from_file': orth, 'guards': G,
          'pass': bool(ncomp == 1 and orth['max_abs_f_dot_s'] < 1e-4 and max(orth['max_abs_norm_f_minus_1'], orth['max_abs_norm_s_minus_1']) < 1e-4)}
    # ---------------- A3: sign convention at the LV-RV epicardial junctions
    epi = surf('epi')
    nodeR = np.zeros(N, bool); nodeR[E[R].ravel()] = True
    nodeL = np.zeros(N, bool); nodeL[E[~R].ravel()] = True
    z = np.loadtxt(os.path.join(OUT, 'uvc', 'z.dat')); phi = np.degrees(np.loadtxt(os.path.join(OUT, 'uvc', 'phi.dat')))
    junc = epi[nodeR[epi] & nodeL[epi] & (z[epi] > 0.1) & (z[epi] < 0.9)]
    A3 = {'junction_nodes_anterior(phi>0)': int((phi[junc] > 0).sum()), 'junction_nodes_inferior(phi<0)': int((phi[junc] < 0).sum())}
    # v5 LV frame (fibres_fix.py): l = unit grad psi (w-blend of basal and the outflow fields), t_out = grad phi_epi_fix
    lap0 = lambda nm: np.loadtxt(os.path.join(OUT, 'laplace', nm + '.dat'))
    lapE = lambda nm: np.loadtxt(os.path.join(V5LAP, nm + '.dat'))
    ok = True
    rv_epi = (d >= 0.95) & (w >= 0.7)
    mid = (d >= 0.45) & (d <= 0.55) & (w >= 0.9)
    for side, sel in (('anterior', phi[junc] > 0), ('inferior', phi[junc] < 0)):
        jt = cKDTree(pts[junc[sel]])
        near_r = rv_epi & (jt.query(CR)[0] <= 10.0)
        # LV epicardium near the junction: elements outside R with phi_epi_fix >= 0.95
        Lidx = np.where(~R)[0]
        pe = np.clip(lapE('phi_epi_fix')[E[Lidx]].mean(1), 0, 1)
        Lsel = Lidx[(pe >= 0.95) & (jt.query(C[Lidx])[0] <= 10.0)]
        EL = E[Lsel]
        wv5 = np.clip(lap0('w')[EL].mean(1), 0, 1)
        g_ot = unit(elem_grad(pts, EL, lapE('ot_lv')))           # LV side of the split: ot_lv (fibres_fix)
        gpsi = wv5[:, None] * unit(elem_grad(pts, EL, lap0('basal'))) + (1 - wv5[:, None]) * g_ot
        lL = unit(gpsi); tL = elem_grad(pts, EL, lapE('phi_epi_fix'))
        tL = unit(tL - np.sum(lL * tL, 1, keepdims=True) * lL); cL = np.cross(lL, tL)
        f5 = unit(L5[Lsel, :3])
        hL = fold(np.degrees(np.arctan2(np.sum(f5 * lL, 1), np.sum(f5 * cL, 1))))
        hR = fold(np.degrees(np.arctan2(np.sum(fw[near_r] * l[near_r], 1), np.sum(fw[near_r] * c[near_r], 1))))
        A3[side] = {'RV_epi_elements': int(near_r.sum()), 'RV_epi_h_lt_0_fraction': float(np.mean(hR < 0)) if near_r.any() else None,
                    'RV_epi_h_median': float(np.median(hR)) if near_r.any() else None,
                    'LV_epi_elements': int(len(Lsel)), 'LV_epi_h_lt_0_fraction': float(np.mean(hL < 0)) if len(Lsel) else None,
                    'LV_epi_h_median': float(np.median(hL)) if len(Lsel) else None}
        ok &= bool(near_r.any() and np.all(hR < 0) and len(Lsel) and np.median(hL) < 0)
    hmid = fold(hm[mid])
    A3['RV_body_mid_wall'] = {'elements': int(mid.sum()), 'h_gt_0_fraction': float(np.mean(hmid > 0)), 'h_median': float(np.median(hmid))}
    ok &= bool(mid.any() and np.all(hmid > 0))
    A3['pass'] = bool(ok)
    # ---------------- A2: v5 vs v5.1 vs expected, in the v5.1 frame
    h5 = fold(np.degrees(np.arctan2(np.sum(L5[rows, :3] * l, 1), np.sum(L5[rows, :3] * c, 1))))
    hn = fold(hm)
    he = fold(h_exp)
    zR = z[E[R]].mean(1)
    A_nodes = np.where(np.linalg.norm(pts - pts[info['apex_A']['seed_node']], axis=1) <= 2.0)[0]
    dset = np.concatenate([np.intersect1d(surf('tv_rim'), nodes), np.intersect1d(surf('pv_rim'), nodes), np.intersect1d(A_nodes, surf('rv_endo'))])
    far = cKDTree(pts[dset]).query(CR)[0] >= 5.0
    pvx = pts[surf('pv_rim')]; cpv = pvx.mean(0); npv = np.linalg.svd(pvx - cpv)[2][2]
    if (pts[A_nodes].mean(0) - cpv) @ npv < 0:
        npv = -npv                                              # normal from the PV plane towards the RV apex
    below = (CR - cpv) @ npv
    ao = np.concatenate([surf('ao_iface'), surf('av_rim')]); d_ao = cKDTree(pts[ao]).query(CR)[0]
    lvE, epiN = cKDTree(pts[surf('lv_endo')]), cKDTree(pts[epi])
    septal = lvE.query(CR)[0] < epiN.query(CR)[0]
    regions = {'(a) RV body free wall (w>=0.9, UVC z 0.4-0.6, >=5 mm from Dirichlet sets)': (w >= 0.9) & (zR >= 0.4) & (zR <= 0.6) & far & ~septal,
               '(a2) RV body septal side (same, septal)': (w >= 0.9) & (zR >= 0.4) & (zR <= 0.6) & far & septal,
               '(b) septal infundibulum 9.6-15.1 mm below the PV plane (<8 mm from the aortic root)': (below >= 9.6) & (below <= 15.1) & (d_ao < 8),
               '(c) free-wall infundibulum 14.2-16.6 mm below the PV plane (>20 mm from the aortic root)': (below >= 14.2) & (below <= 16.6) & (d_ao > 20),
               '(d) septal 2-4 mm below the PV plane': (below >= 2) & (below <= 4) & (d_ao < 8),
               '(d) free wall 2-4 mm below the PV plane': (below >= 2) & (below <= 4) & (d_ao > 20)}
    A2 = {}
    for rn, m in regions.items():
        cell = {'elements': int(m.sum())}
        for b0, b1 in ((0, 0.05), (0.45, 0.55), (0.95, 1.0)):
            mm = m & (d >= b0) & (d <= b1)
            cell[f'd {b0}-{b1}'] = (f'n {int(mm.sum())}: v5 {np.median(h5[mm]):+.1f}, v5.1 {np.median(hn[mm]):+.1f}, expected {np.median(he[mm]):+.1f}, '
                                   f'w {np.median(w[mm]):.2f}') if mm.any() else 'none'
        A2[rn] = cell
    sites = json.load(open(os.path.join(OUT, 'sites.json')))
    ctree = cKDTree(CR)
    A2['w at RVOT sites'] = {s['id']: round(float(w[ctree.query(pts[int(s['node'])])[1]]), 3) for s in sites if s['family'] == 'rvot'}
    # ---------------- A7: fibre angle across borders (face-adjacent element pairs)
    keysA, elA = face_keys(E, N)
    o = np.argsort(keysA, kind='stable'); ks, es = keysA[o], elA[o]
    dpair = np.where(ks[1:] == ks[:-1])[0]
    a_, b_ = es[dpair], es[dpair + 1]
    border = R[a_] != R[b_]
    jt_all = cKDTree(pts[junc])
    def ang(F, i, j):
        return np.degrees(np.arccos(np.clip(np.abs(np.sum(unit(F[i, :3]) * unit(F[j, :3]), 1)), 0, 1)))   # fibre vectors only
    within = (R[a_] == R[b_]) & R[a_]
    A7 = {}
    for nm, sel in (('R_new border (= septal interface, WHOLE_RV)', border),
                    ('R_new border within 10 mm of the epicardial junctions', border & (jt_all.query(C[a_])[0] <= 10)),
                    ('inside R_new (reference)', within)):
        cell = {'pairs': int(sel.sum())}
        for tagn, F in (('v5', L5), ('v5.1', Lw)):
            aa = ang(F, a_[sel], b_[sel])
            cell[tagn] = f'median {np.median(aa):.1f}, p95 {np.percentile(aa, 95):.1f}, max {aa.max():.1f} deg'
        A7[nm] = cell
    res = {'heart': HEART, 'R_field': {'definition': 'd = phi_rv / (phi_lv + phi_rv) > 0.5 per element (fibres_fix.py main())',
                                        'elements': int(R.sum()), 'sha256': info['R_field_sha256'],
                                        'by_tag': {int(tg): int((R & (tag == tg)).sum()) for tg in np.unique(tag)},
                                        'tag2_elements': int((tag == 2).sum()), 'tag2_outside_R_field': int(((tag == 2) & ~R).sum())},
           'laplace': {k: v for k, v in info.items() if k in ('apex_A', 'rings_in_R_field', 'problems', 'overlap_lv_rv_endo')},
           'gates': {'A1': A1, 'A3': A3, 'A4': A4, 'A5': A5, 'A8': A8}, 'A2': A2, 'A7': A7,
           'candidate_file': {'path': os.path.relpath(cand, REPO), 'sha256': hashlib.sha256(open(cand, 'rb').read()).hexdigest()},
           'wall_s': round(time.time() - t0, 1)}
    np.savez(os.path.join(RUN, 'doste_frame.npz'), rows=rows, l=l.astype(np.float32), t_out=t_out.astype(np.float32), c=c.astype(np.float32),
             d=d.astype(np.float32), w=w.astype(np.float32), h_exp=h_exp.astype(np.float32))
    json.dump(res, open(os.path.join(HERE, f'doste_{HEART}.json'), 'w'), indent=1)
    print(json.dumps(res['gates'], indent=1)); print(json.dumps(A2, indent=1)); print(json.dumps(A7, indent=1))


if __name__ == '__main__':
    {'laplace': laplace, 'fibres': fibres}[sys.argv[1]]()
