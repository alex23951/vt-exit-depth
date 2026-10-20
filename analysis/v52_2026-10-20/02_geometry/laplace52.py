"""v5.2 steps 2c-2d: UVC and transmural fields re-solved on the merged mesh (LOCK.md 8.5 item 8b, 8.6).

"The UVC and transmural w are re-solved on the merged mesh (the same Laplace solves v5.1 used)". The same solves, in
v5.1's order, with v5.1's boundary sets and openCARP settings (experiment 2, unit isotropic conductivity):
  1. sims/biv_model/02_laplace.py   zeta, basal, ot, w, phi_epi, phi_lv, phi_rv, v
  2. sims/biv_model/03_uvc.py       z (remapped zeta), z_laplace, rho, sep, v, phi
  3. analysis/fibre_fix_2026-10-13/laplace_fix.py   ot_rv, ot_lv, phi_epi_fix (v5.1's LV fibre fields)
  4. analysis/v51_2026-10-15/04_build/doste_rv.py laplace   u_lv, u_rv, phi_D = -2 u_lv + u_rv (whole mesh; RV transmural
     d = 1 - phi_D), the apex set A from the new z, and on the RV-side submesh (d = phi_rv / (phi_lv + phi_rv) > 0.5 per
     element) psi_tv, psi_pv and Doste's w
The code of each is copied here with paths as arguments (mesh, surfaces, output); nothing else changed. The conductor is
the merged mesh WITHOUT the infundibulum cut: the cut is an activation-engine treatment (8.2), and these are coordinate
fields. Fibres play no part in an isotropic solve, so the mesh's .lon is a placeholder (every row 1 0 0 0 1 0).

Y5HYEDL4's merged mesh is v5.1's mesh (merge52: identical), so its v5.2 fields ARE v5.1's: they are copied unchanged into
data/biv/Y5HYEDL4/v52/, and the re-solve runs on it only as a reproducibility check of this script (fields compared with
v5.1's files, never used). For 6G8DD8S5 and 7D98EVAR the re-solved fields are the v5.2 fields, compared with v5.1's on
the v5.1 nodes (report only).
Outputs: data/biv/<H>/v52/laplace/*.dat, data/biv/<H>/v52/uvc/*.dat, laplace52_<H>.json here; openCARP folders (logs carry
a token, never commit) under runs/v52_2026-10-20/02_geometry/<H>/laplace/.
Usage (repo root, venv, PATH with mpiexec): python -B analysis/v52_2026-10-20/02_geometry/laplace52.py HEART [--np 4]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import read_elem, read_pts, read_vtx, write_vtx                                 # noqa: E402

BASE = ['mv_rim', 'tv_rim', 'av_rim', 'pv_rim', 'avplane_iface', 'ao_iface', 'part_iface', 'ra_iface']
P02 = {
    'zeta': (['APEX'], BASE),
    'basal': (['APEX'], ['mv_rim', 'tv_rim', 'avplane_iface', 'ra_iface']),
    'ot': (['APEX'], ['av_rim', 'pv_rim', 'ao_iface', 'part_iface']),
    'w': (['av_rim', 'pv_rim', 'ao_iface', 'part_iface'], ['APEX', 'mv_rim', 'tv_rim', 'avplane_iface', 'ra_iface']),
    'phi_epi': (['lv_endo', 'rv_endo'], ['epi']),
    'phi_lv': (['rv_endo', 'epi'], ['lv_endo']),
    'phi_rv': (['lv_endo', 'epi'], ['rv_endo']),
    'v': (['lv_endo'], ['rv_endo']),
}
PFIX = {'ot_rv': (['APEX'], ['pv_rim', 'part_iface']), 'ot_lv': (['APEX'], ['av_rim', 'ao_iface']),
        'phi_epi_fix': (['lv_endo', 'rv_endo'], ['epi', 'AO_OUTER'])}
DOSTE_WHOLE = ('u_lv', 'u_rv', 'phi_D')
DOSTE_SUB = ('psi_tv', 'psi_pv', 'w')


class Ctx:
    def __init__(self, h, mesh, surf, lap, uvc, ocdir, np_):
        self.h, self.mesh, self.surf, self.lap, self.uvc, self.oc, self.np = h, mesh, surf, lap, uvc, ocdir, np_
        for d in (lap, uvc, ocdir):
            os.makedirs(d, exist_ok=True)

    def vtx(self, n):
        return read_vtx(os.path.join(self.surf, n + '.vtx'))

    def vset(self, names):
        out = []
        for n in names:
            if n == 'AO_OUTER':
                endo = np.concatenate([self.vtx('lv_endo'), self.vtx('rv_endo')])
                out.append(np.setdiff1d(self.vtx('ao_iface'), endo))
            elif n == 'APEX':
                out.append(self.vtx('apex_patch'))
            elif os.path.exists(os.path.join(self.surf, n + '.vtx')):
                out.append(self.vtx(n))
        return np.unique(np.concatenate(out))

    def solve(self, name, zero, one, mesh=None, out=None):
        """02_laplace.py solve() / doste_rv.py opencarp(): zero -> 0 (ground), one -> 1; the "1" set wins on overlap."""
        zero = np.setdiff1d(zero, one)
        d = os.path.join(self.oc, name); os.makedirs(d, exist_ok=True)
        write_vtx(os.path.join(d, 'bc0.vtx'), zero); write_vtx(os.path.join(d, 'bc1.vtx'), one)
        cmd = ['mpiexec', '-n', str(self.np), 'openCARP', '-experiment', 2, '-bidomain', 1, '-meshname', mesh or self.mesh,
               '-simID', d, '-num_gregions', 1, '-gregion[0].num_IDs', 0,
               '-gregion[0].g_il', 1, '-gregion[0].g_it', 1, '-gregion[0].g_in', 1,
               '-gregion[0].g_el', 1, '-gregion[0].g_et', 1, '-gregion[0].g_en', 1,
               '-num_stim', 2,
               '-stim[0].crct.type', 3, '-stim[0].elec.vtx_file', os.path.join(d, 'bc0'),
               '-stim[1].crct.type', 2, '-stim[1].elec.vtx_file', os.path.join(d, 'bc1'),
               '-stim[1].pulse.strength', 1.0, '-stim[1].ptcl.duration', 1.0]
        t0 = time.time()
        with open(os.path.join(d, 'openCARP.log'), 'w') as log:
            subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
        f = os.path.join(out or self.lap, name + '.dat')
        subprocess.run(['igbextract', '-o', 'ascii', '-O', f, os.path.join(d, 'phie.igb')], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        x = np.loadtxt(f)
        if x.ndim > 1:
            x = x[-1]
        np.savetxt(f, x, fmt='%.6g')
        rec = {'n_bc0': int(len(zero)), 'n_bc1': int(len(one)), 'min': float(x.min()), 'max': float(x.max()), 'n': int(len(x)),
               'wall_s': round(time.time() - t0, 1)}
        print(f'  {name}: {rec}', flush=True)
        return x, rec


def placeholder_mesh(src_base, dst_dir, n_elem):
    """Mesh base for the isotropic solves: links to the .pts/.elem and a placeholder .lon."""
    os.makedirs(dst_dir, exist_ok=True)
    b = os.path.join(dst_dir, os.path.basename(src_base))
    for ext in ('.pts', '.elem'):
        if os.path.lexists(b + ext):
            os.remove(b + ext)
        os.symlink(os.path.abspath(src_base + ext), b + ext)
    with open(b + '.lon', 'w') as fh:
        fh.write('2\n'); fh.write('1 0 0 0 1 0\n' * n_elem)
    return b


def uvc(c, pts, E, tag):
    """sims/biv_model/03_uvc.py main(), paths as arguments (code unchanged)."""
    lap = lambda n: np.loadtxt(os.path.join(c.lap, n + '.dat'))
    apex = pts[c.vtx('apex')[0]]
    base_c = pts[np.concatenate([c.vtx(f) for f in ('mv_rim', 'tv_rim')])].mean(0)
    axis = (base_c - apex) / np.linalg.norm(base_c - apex)
    s = np.clip((pts - apex) @ axis / np.linalg.norm(base_c - apex), 0, 1)
    zl = np.clip(lap('zeta'), 0, 1)
    q = np.quantile(zl, np.linspace(0, 1, 201))
    q = np.unique(q)
    idx = np.clip(np.searchsorted(q, zl, side='right') - 1, 0, len(q) - 2)
    centre = np.array([zl[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    target = np.array([s[idx == i].mean() if (idx == i).any() else np.nan for i in range(len(q) - 1)])
    ok = ~np.isnan(centre)
    centre, target = centre[ok], np.maximum.accumulate(target[ok])
    xs = np.concatenate([[0.0], centre, [1.0]])
    ys = np.concatenate([[0.0], target, [1.0]])
    ys = np.maximum.accumulate(ys)
    ys = (ys - ys[0]) / (ys[-1] - ys[0])
    z = np.interp(zl, xs, ys)
    rho = np.clip(lap('phi_epi'), 0, 1)
    plv, prv = np.clip(lap('phi_lv'), 0, 1), np.clip(lap('phi_rv'), 0, 1)
    sep = prv / np.maximum(plv + prv, 1e-9)
    v = (lap('v') > 0.5).astype(float)
    rv_c = pts[c.vtx('rv_endo')].mean(0)

    def perp(x):
        return x - np.outer(x @ axis, axis) if x.ndim > 1 else x - (x @ axis) * axis
    e1 = perp(rv_c - apex); e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    ao_c = pts[np.concatenate([c.vtx(f) for f in ('av_rim', 'ao_iface')])].mean(0)
    if perp(ao_c - apex) @ e2 < 0:
        e2 = -e2
    r = perp(pts - apex)
    phi = np.arctan2(r @ e2, r @ e1)
    for n, x in (('z', z), ('z_laplace', zl), ('rho', rho), ('sep', sep), ('v', v), ('phi', phi)):
        np.savetxt(os.path.join(c.uvc, n + '.dat'), x, fmt='%.6g')
    return {'corr_z_vs_axial_distance': float(np.corrcoef(z, s)[0, 1]), 'z_deciles': np.percentile(z, np.arange(10, 100, 10)).round(3).tolist()}


def doste(c, pts_um, E):
    """doste_rv.py laplace(), paths as arguments; the submesh .lon is the placeholder (isotropic)."""
    pts = pts_um / 1e3
    lap = lambda n: np.loadtxt(os.path.join(c.lap, n + '.dat'))
    plv, prv = (np.clip(lap(n)[E].mean(1), 0, 1) for n in ('phi_lv', 'phi_rv'))
    R = prv / np.maximum(plv + prv, 1e-9) > 0.5
    lv, rv = c.vtx('lv_endo'), c.vtx('rv_endo')
    endo = np.concatenate([lv, rv])
    outer = np.unique(np.concatenate([c.vtx('epi'), np.setdiff1d(c.vtx('ao_iface'), endo)]))
    info = {'R_field_elements': int(R.sum()), 'problems': {}}
    u_lv, info['problems']['u_lv'] = c.solve('u_lv', np.union1d(rv, outer), lv)
    u_rv, info['problems']['u_rv'] = c.solve('u_rv', np.union1d(lv, outer), rv)
    np.savetxt(os.path.join(c.lap, 'phi_D.dat'), -2.0 * u_lv + u_rv, fmt='%.8g')
    z = np.loadtxt(os.path.join(c.uvc, 'z.dat'))
    a0 = rv[np.argmin(z[rv])]
    A = rv[np.linalg.norm(pts[rv] - pts[a0], axis=1) <= 2.0]
    info['apex_A'] = {'seed_node': int(a0), 'seed_uvc_z': float(z[a0]), 'nodes': int(len(A))}
    ER = E[R]
    nodes = np.unique(ER)
    loc = np.full(len(pts), -1, np.int64); loc[nodes] = np.arange(len(nodes))
    sub = os.path.join(c.oc, 'rv_sub')
    with open(sub + '.pts', 'w') as fh:
        fh.write(f'{len(nodes)}\n'); np.savetxt(fh, pts_um[nodes], fmt='%.6f')
    with open(sub + '.elem', 'w') as fh:
        fh.write(f'{len(ER)}\n'); np.savetxt(fh, np.hstack([loc[ER], np.ones((len(ER), 1), np.int64)]), fmt='Tt %d %d %d %d %d')
    with open(sub + '.lon', 'w') as fh:
        fh.write('2\n'); fh.write('1 0 0 0 1 0\n' * len(ER))
    np.save(os.path.join(c.lap, 'rv_sub_nodes.npy'), nodes)
    np.save(os.path.join(c.lap, 'R_field.npy'), R)
    inR = lambda s: loc[np.intersect1d(s, nodes)]
    tvR, pvR, AR = inR(c.vtx('tv_rim')), inR(c.vtx('pv_rim')), inR(A)
    info['rings_in_R_field'] = {'TV': int(len(tvR)), 'PV': int(len(pvR)), 'A_in_R': int(len(AR))}
    sd = os.path.join(c.lap, 'rv_sub'); os.makedirs(sd, exist_ok=True)
    for n, zero, one in (('psi_tv', AR, tvR), ('psi_pv', AR, pvR), ('w', pvR, np.union1d(AR, tvR))):
        _, info['problems'][n] = c.solve('sub_' + n, zero, one, mesh=sub, out=sd)
        os.replace(os.path.join(sd, 'sub_' + n + '.dat'), os.path.join(sd, n + '.dat'))
    return info, R


def v51_paths(h):
    B = os.path.join(G.REPO, 'data', 'biv', h)
    V5L = os.path.join(G.REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'laplace')       # read only
    D = os.path.join(G.REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'laplace')
    p = {f'laplace/{n}': os.path.join(B, 'laplace', n + '.dat') for n in P02}
    p.update({f'uvc/{n}': os.path.join(B, 'uvc', n + '.dat') for n in ('z', 'z_laplace', 'rho', 'sep', 'v', 'phi')})
    p.update({f'laplace/{n}': os.path.join(V5L, n + '.dat') for n in PFIX})
    p.update({f'laplace/{n}': os.path.join(D, n + '.dat') for n in DOSTE_WHOLE})
    p.update({f'laplace/rv_sub/{n}': os.path.join(D, n + '.dat') for n in DOSTE_SUB})
    p['laplace/rv_sub_nodes.npy'] = os.path.join(D, 'rv_sub_nodes.npy')
    return p


def compare(new_root, h, n_old):
    out = {}
    for k, f51 in v51_paths(h).items():
        if k.endswith('.npy'):
            a, b = np.load(f51), np.load(os.path.join(new_root, k))
            out[k] = {'identical': bool(np.array_equal(a, b))}
            continue
        a = np.loadtxt(f51); b = np.loadtxt(os.path.join(new_root, k + '.dat'))
        if k.startswith('laplace/rv_sub/'):
            out[k] = {'n_v51': int(len(a)), 'n_v52': int(len(b))}
            if len(a) != len(b):
                continue
            d = np.abs(a - b)
        else:
            d = np.abs(a[:n_old] - b[:n_old])
        if k == 'uvc/phi':
            d = np.abs((d + np.pi) % (2 * np.pi) - np.pi)
        out[k] = {**out.get(k, {}), 'max_abs_diff': float(d.max()), 'p99_abs_diff': float(np.percentile(d, 99)),
                  'median_abs_diff': float(np.median(d))}
    return out


def run(h, np_):
    t0 = time.time()
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    m = json.load(open(os.path.join(HERE, f'merge52_{h}.json')))
    repro = m['identical_to_v51']
    RUNH = os.path.join(G.RUN, h)
    root = os.path.join(RUNH, 'laplace_repro') if repro else V
    mesh = placeholder_mesh(os.path.join(V, 'biv52'), os.path.join(RUNH, 'lapmesh'), m['elements'])
    c = Ctx(h, mesh, os.path.join(V, 'surfaces'), os.path.join(root, 'laplace'), os.path.join(root, 'uvc'),
            os.path.join(RUNH, 'laplace'), np_)
    pts_um = read_pts(os.path.join(V, 'biv52')); E, tag = read_elem(os.path.join(V, 'biv52'))
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'mesh': os.path.relpath(os.path.join(V, 'biv52'), G.REPO),
           'mesh_identical_to_v51': repro, 'conductor': 'merged mesh, uncut (8.2: the cut is an activation-engine treatment)',
           'np': np_, 'problems': {}}
    print(h, 'merged mesh', m['nodes'], 'nodes', m['elements'], 'elements', '(reproducibility check)' if repro else '', flush=True)
    for n, (z0, z1) in P02.items():
        _, rec['problems'][n] = c.solve(n, c.vset(z0), c.vset(z1))
    rec['uvc'] = uvc(c, pts_um, E, tag)
    for n, (z0, z1) in PFIX.items():
        _, rec['problems'][n] = c.solve(n, c.vset(z0), c.vset(z1))
    info, R = doste(c, pts_um, E)
    rec['doste'] = info
    nb = m['v51_elements']
    R51 = None
    D51 = os.path.join(G.REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'laplace', 'laplace_info.json')
    plv51, prv51 = (np.clip(np.loadtxt(os.path.join(G.REPO, 'data', 'biv', h, 'laplace', n + '.dat'))[E[:nb]].mean(1), 0, 1) for n in ('phi_lv', 'phi_rv'))
    R51 = prv51 / np.maximum(plv51 + prv51, 1e-9) > 0.5
    sha = hashlib.sha256(np.ascontiguousarray(R51.astype(np.uint8)).tobytes()).hexdigest()
    rec['R_field_vs_v51'] = {'v51_R_field_sha256_matches_v51_record': sha == json.load(open(D51))['R_field_sha256'],
                             'v51_elements_RV_side_v51': int(R51.sum()), 'v51_elements_RV_side_re_solved': int(R[:nb].sum()),
                             'v51_elements_LV_to_RV': int((~R51 & R[:nb]).sum()), 'v51_elements_RV_to_LV': int((R51 & ~R[:nb]).sum()),
                             'added_elements_RV_side': int(R[nb:].sum()), 'added_elements': int(len(E) - nb)}
    rec['vs_v51_on_v51_nodes'] = compare(root, h, m['v51_nodes'])
    if repro:
        # v5.2 fields of an unchanged mesh are v5.1's: copied unchanged (the re-solve above is the check only)
        for k, f51 in v51_paths(h).items():
            dst = os.path.join(V, k + ('' if k.endswith('.npy') else '.dat'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(f51, dst)
        np.save(os.path.join(V, 'laplace', 'R_field.npy'), R51)
        rec['v52_fields'] = 'v5.1 files copied unchanged into data/biv/<H>/v52/{laplace,uvc} (mesh identical)'
    else:
        rec['v52_fields'] = 're-solved on the merged mesh (this run)'
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'laplace52_{h}.json'))
    worst = max((v.get('max_abs_diff', 0) for k, v in rec['vs_v51_on_v51_nodes'].items() if k != 'uvc/phi'), default=0)
    print(h, 'done', rec['wall_s'], 's; largest |field change| on v5.1 nodes (not phi):', round(worst, 6),
          '; R_field', rec['R_field_vs_v51'], flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('hearts', nargs='*', default=G.HEARTS)
    ap.add_argument('--np', type=int, default=4)
    a = ap.parse_args()
    for h in a.hearts:
        run(h, a.np)
