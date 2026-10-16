"""Addendum part B: Taggart-style apparent conduction speed on the LV free-wall epicardium (spec in README.md, fixed before
any result). Grid: 2 rows x 4 electrodes, 5 mm apart along the long axis (-7.5, -2.5, +2.5, +7.5 mm) and rows at -5 / +5 mm,
long axis = local epicardial fibre (v5 fibres) projected onto the tangent plane, centre on the LV free-wall epicardium at
UVC z 0.5, middle of the free-wall arc between the RV insertion lines; electrodes snapped to the nearest LV epicardial node.
Activation = regenerated v5 activation maps (maps/<h>/<site>.T.npy). Fit t = t0 + gx x + gy y (x long, y short, mm, ms)."""
import json, os
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'taggart'); os.makedirs(OUT, exist_ok=True)
un = lambda a: a / np.linalg.norm(a)
RES, ELEC = {}, []
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    B = os.path.join(REPO, 'data', 'biv', h)
    P = np.loadtxt(os.path.join(B, 'biv.pts'), skiprows=1) / 1e3
    E = np.loadtxt(os.path.join(B, 'biv.elem'), skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    rd = lambda n: np.loadtxt(os.path.join(B, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    tri = np.loadtxt(os.path.join(B, 'surfaces', 'epi.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    z = np.loadtxt(os.path.join(B, 'uvc', 'z.dat')); v = np.loadtxt(os.path.join(B, 'uvc', 'v.dat'))
    lon = pd.read_csv(os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'bivF.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()[:, :3]
    nrm = np.zeros((len(P), 3)); fn = np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]])
    for k in range(3): np.add.at(nrm, tri[:, k], fn)
    lve, rve = epi[v[epi] == 0], epi[v[epi] == 1]; tlve = cKDTree(P[lve])
    groove = lve[cKDTree(P[rve]).query(P[lve])[0] <= 2.0]
    apex = P[int(json.load(open(os.path.join(B, 'summary_02.json')))['apex_node'])]; cmv = P[rd('mv_rim')].mean(0); ax = un(cmv - apex)
    node2el = {}
    def centre_at(zz):
        band = lve[np.abs(z[lve] - zz) < 0.02]; c = P[lv[np.abs(z[lv] - zz) < 0.02]].mean(0)
        e1 = P[rv[np.abs(z[rv] - zz) < 0.04]].mean(0) - c; e1 -= (e1 @ ax) * ax; e1 = un(e1); e2 = np.cross(ax, e1)
        ang = lambda Y: np.degrees(np.arctan2((Y - c) @ e2, (Y - c) @ e1))
        g = groove[np.abs(z[groove] - zz) < 0.04]; ga = ang(P[g]); ia, ii = np.median(ga[ga > 0]), np.median(ga[ga < 0])
        mid = ia + ((ii - ia) % 360) / 2                    # middle of the free-wall arc (going away from the septum)
        a_b = ang(P[band]); dlt = np.abs(np.angle(np.exp(1j * np.radians(a_b - mid))))
        return int(band[np.argmin(dlt)]), float(ia), float(ii), float(((mid + 180) % 360) - 180)
    def frame(n0):
        nn = un(nrm[n0]); els = np.where(np.any(E == n0, axis=1))[0]
        f = lon[els]; f = f * np.sign(f @ f[0])[:, None]; f = f.mean(0); u = un(f - (f @ nn) * nn); w = np.cross(nn, u)
        return nn, u, w
    def grid(n0):
        nn, u, w = frame(n0); pts = []
        for y in (-5.0, 5.0):
            for x in (-7.5, -2.5, 2.5, 7.5):
                q = P[n0] + x * u + y * w; k = int(lve[tlve.query(q)[1]]); pts.append((x, y, k))
        return pts, u, w, nn
    zc_primary = 0.5
    n0, ia, ii, mid = centre_at(zc_primary)
    # basal / apical centres: 10 mm along the surface apex->base direction (projected LV axis)
    nn0 = un(nrm[n0]); ab = un(ax - (ax @ nn0) * nn0)
    centres = {'primary': n0, 'basal_1cm': int(lve[tlve.query(P[n0] + 10 * ab)[1]]), 'apical_1cm': int(lve[tlve.query(P[n0] - 10 * ab)[1]])}
    S = pd.DataFrame(json.load(open(os.path.join(B, 'sites.json'))))
    cand = S[S.family.isin(['rv_free_wall', 'rvot'])]
    out = {'centre_uvc_z': round(float(z[n0]), 3), 'insertions_deg(ant,inf)': [round(ia), round(ii)], 'free_wall_middle_deg': round(mid)}
    for cname, cn in centres.items():
        pts, u, w, nn = grid(cn)
        XY = np.array([[np.dot(P[k] - P[cn], u), np.dot(P[k] - P[cn], w)] for _, _, k in pts])
        for (x, y, k), (xa, ya) in zip(pts, XY):
            ELEC.append({'heart': h, 'grid': cname, 'x_nominal_mm': x, 'y_nominal_mm': y, 'node': k, 'x_actual_mm': round(xa, 2), 'y_actual_mm': round(ya, 2),
                         'snap_offset_mm': round(float(np.linalg.norm(P[k] - (P[cn] + x * u + y * w))), 2), 'uvc_z': round(float(z[k]), 3)})
        A = np.c_[np.ones(8), XY]
        res = []
        for net, dmap, cands in (('net', os.path.join(HERE, 'maps', h), cand), ('nonet', os.path.join(HERE, 'maps', h + '_nonet'), cand if h == 'Y5HYEDL4' else cand.iloc[:0])):
            for _, s in cands.iterrows():
                f = os.path.join(dmap, s['id'] + '.T.npy')
                if not os.path.exists(f): continue
                T = np.load(f).astype(float); t = T[[k for _, _, k in pts]]
                c, *_ = np.linalg.lstsq(A, t, rcond=None); gx, gy = c[1], c[2]
                th = float(np.degrees(np.arctan2(gy, gx))); a_long = min(abs(th), 180 - abs(th)); a_short = abs(90 - a_long)
                tt = t.reshape(2, 4)
                res.append({'network': net, 'site': s['id'], 'depth': s['depth_target'], 'times_ms': t.round(2).tolist(), 'gx_ms_per_mm': round(gx, 4), 'gy_ms_per_mm': round(gy, 4),
                            'wavefront_dir_deg_from_long_axis': round(th, 1), 'angle_to_long_axis': round(a_long, 1), 'angle_to_short_axis': round(a_short, 1),
                            'v_long_1/gx': round(1 / abs(gx), 3) if gx else None, 'v_short_1/gy': round(1 / abs(gy), 3) if gy else None, 'v_1/|g|': round(1 / float(np.hypot(gx, gy)), 3),
                            'two_point_long_m_s': round(15.0 / float(np.mean(np.abs(tt[:, 3] - tt[:, 0]))), 3) if np.mean(np.abs(tt[:, 3] - tt[:, 0])) > 0 else None,
                            'two_point_trans_m_s': round(10.0 / float(np.mean(np.abs(tt[1] - tt[0]))), 3) if np.mean(np.abs(tt[1] - tt[0])) > 0 else None,
                            'fit_rms_ms': round(float(np.sqrt(np.mean((A @ c - t) ** 2))), 3)})
        R = pd.DataFrame(res)
        R.to_csv(os.path.join(OUT, f'beats_{h}_{cname}.csv'), index=False)
        pick = {}
        for net in R.network.unique() if len(R) else []:
            Rn = R[R.network == net]
            for run, col in (('longitudinal', 'angle_to_long_axis'), ('transverse', 'angle_to_short_axis')):
                Rs = Rn.assign(pref=(Rn.depth != 0.9).astype(int)).sort_values([col, 'pref'])
                b = Rs.iloc[0]
                pick[f'{net} {run}'] = {'site': b.site, 'depth': b.depth, 'angle_deg': b[col], 'accepted(<=20deg)': bool(b[col] <= 20),
                                        'apparent_speed_m_s(primary)': b['v_long_1/gx'] if run == 'longitudinal' else b['v_short_1/gy'],
                                        '1/|g|': b['v_1/|g|'], 'wavefront_dir_deg': b['wavefront_dir_deg_from_long_axis'],
                                        'two_point_m_s': b['two_point_long_m_s'] if run == 'longitudinal' else b['two_point_trans_m_s'], 'fit_rms_ms': b['fit_rms_ms']}
        out[cname] = pick
    RES[h] = out
    print(h, json.dumps(out, indent=1, default=str), flush=True)
pd.DataFrame(ELEC).to_csv(os.path.join(OUT, 'electrodes.csv'), index=False)
json.dump(RES, open(os.path.join(OUT, 'speeds.json'), 'w'), indent=1, default=str)
