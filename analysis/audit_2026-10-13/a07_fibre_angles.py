"""Audit 07: fibre angles of the v5 fibre field (fibres_E) and the frozen v3 field, sampled by region (read only).
Local frame per element: transmural t = unit grad(phi_epi) (septum: grad(sep), LV -> RV), longitudinal l = apex->base axis
(outflow regions: the valve axis, PV / AV normal pointing to the artery) projected into the wall plane, circumferential
c = l x t (the 04_fibres.py convention). Helix angle = atan2(f.l, f.c) of the fibre projected into the wall plane
(+ = right-handed, expected +60 endo -> -60 epi in the body; Doste: OT endo +-90 = along the outflow axis, epi 0 =
circumferential). Out-of-plane angle = asin(|f.t|). 5 elements per region and depth band (rho 0-0.15 / 0.4-0.6 / 0.85-1),
nearest to a regional anchor."""
import json, sys
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
sys.path.insert(0, 'sims/biv_model')
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
def egrad(P, E, u):
    x0 = P[E[:, 0]]; J = np.stack([P[E[:, 1]] - x0, P[E[:, 2]] - x0, P[E[:, 3]] - x0], 1)
    du = np.stack([u[E[:, 1]] - u[E[:, 0]], u[E[:, 2]] - u[E[:, 0]], u[E[:, 3]] - u[E[:, 0]]], 1)
    return np.linalg.solve(J, du[..., None])[..., 0]
un = lambda a: a / np.linalg.norm(a, axis=-1, keepdims=True)
OUT = {}
for h in H:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    E = np.loadtxt(B + 'biv.elem', skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    C = P[E].mean(1)
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    z, phi, rho, sep, v = (np.loadtxt(B + f'uvc/{n}.dat') for n in ('z', 'phi', 'rho', 'sep', 'v'))
    w = np.clip(np.loadtxt(B + 'laplace/w.dat'), 0, 1)
    ze, phe, rhoe, sepe, ve, we = (x[E].mean(1) for x in (z, np.degrees(phi), rho, sep, v, w))
    pe = np.loadtxt('analysis/v5_grid_2026-10-13/fibres_E/' + h + '/laplace/phi_epi_fix.dat') if False else None
    g_epi = un(egrad(P, E, np.loadtxt(B + 'laplace/phi_epi.dat'))); g_sep = un(egrad(P, E, sep))
    apex = P[int(json.load(open(B + 'summary_02.json'))['apex_node'])]
    cmv = P[rd('mv_rim')].mean(0); ax = un(cmv - apex)
    def vnormal(name, cav):
        X = P[rd(name)]; c = X.mean(0); n = np.linalg.svd(X - c)[2][2]
        return c, (n if (c - cav) @ n > 0 else -n)
    cpv, npv = vnormal('pv_rim', P[rd('rv_endo')].mean(0)); cav_, nav = vnormal('av_rim', P[rd('lv_endo')].mean(0))
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    te, tl, tr = cKDTree(P[epi]), cKDTree(P[lv]), cKDTree(P[rv])
    d_pv = cKDTree(P[rd('pv_rim')]).query(C)[0]; d_av = cKDTree(P[rd('av_rim')]).query(C)[0]
    ao = np.concatenate([rd('ao_iface'), rd('av_rim')]); d_ao = cKDTree(P[ao]).query(C)[0]
    regions = {
        'LV_free_wall_mid(phi120,z0.5)': ((ve < 0.5) & (np.abs(ze - 0.5) < 0.05) & (np.abs(((phe - 120 + 180) % 360) - 180) < 15), 'rho', ax),
        'septum_mid(phi-30,z0.5)': ((np.abs(ze - 0.5) < 0.05) & (np.abs(((phe + 30 + 180) % 360) - 180) < 15) & (sepe > 0.02) & (sepe < 0.98) & (rhoe < 0.3), 'sep', ax),
        'RV_free_wall_mid': ((ve > 0.5) & (np.abs(ze - 0.5) < 0.05) & (te.query(C)[0] < tl.query(C)[0]) & (we > 0.6), 'rho', ax),
        'RVOT_septal(w<0.3, 8-15 mm below PV, near aortic root)': ((we < 0.3) & (ve > 0.5) & (d_pv > 8) & (d_pv < 15) & (d_ao < 8), 'rho', npv),
        'RVOT_free_wall(w<0.3, 8-15 mm below PV, far from aorta)': ((we < 0.3) & (ve > 0.5) & (d_pv > 8) & (d_pv < 15) & (d_ao > 20), 'rho', npv),
        'LVOT/summit(LV, 5-15 mm from AV rim, anterior-lateral)': ((ve < 0.5) & (d_av > 5) & (d_av < 15) & (np.sin(np.radians(phe)) > 0.3), 'rho', nav)}
    res = {}
    for fname, lonf in (('v5', f'analysis/v5_grid_2026-10-13/fibres_E/{h}/bivF.lon'), ('v3', B + 'bivF.lon')):
        L = pd.read_csv(lonf, sep=r'\s+', skiprows=1, header=None).to_numpy(); F = un(L[:, :3])
        for rn, (m, tsrc, lax) in regions.items():
            idx_all = np.where(m)[0]
            if len(idx_all) == 0:
                res[f'{fname} {rn}'] = 'no elements'; continue
            depth = rhoe if tsrc == 'rho' else sepe
            T = g_epi if tsrc == 'rho' else g_sep
            out = {}
            anchor = C[idx_all].mean(0)
            for band, (a, b) in (('endo', (0, 0.15)), ('mid', (0.4, 0.6)), ('epi', (0.85, 1.0))):
                ii = idx_all[(depth[idx_all] >= a) & (depth[idx_all] <= b)]
                if len(ii) == 0:
                    out[band] = None; continue
                ii = ii[np.argsort(np.linalg.norm(C[ii] - anchor, axis=1))[:5]]
                t = T[ii]; l = lax - (t @ lax)[:, None] * t; l = un(l); c = np.cross(l, t)
                f = F[ii]; fp = f - (np.sum(f * t, 1))[:, None] * t
                hel = np.degrees(np.arctan2(np.sum(fp * l, 1), np.sum(fp * c, 1)))
                hel = (hel + 90) % 180 - 90          # fibres are axial: fold to -90..90
                oop = np.degrees(np.arcsin(np.clip(np.abs(np.sum(f * t, 1)), 0, 1)))
                out[band] = {'helix_deg': hel.round(0).tolist(), 'out_of_plane_deg': oop.round(0).tolist()}
            res[f'{fname} {rn}'] = out
    OUT[h] = res
    print(h)
    for k, x in res.items():
        print('  ', k, {b: (y['helix_deg'] if y else None) for b, y in x.items()} if isinstance(x, dict) else x)
json.dump(OUT, open('analysis/audit_2026-10-13/a07_fibre_angles.json', 'w'), indent=1)
