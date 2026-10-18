"""Audit 11: LV wall thickness by AHA-style segments (Cerqueira 2002, anchored to the RV insertion points), replacing the
UVC-phi bins of a04 (UVC phi is distorted: see a05). Levels by fraction of the apex->MV-centroid axis: basal 0.65-0.80,
mid 0.40-0.55, apical 0.15-0.30, apex cap < 0.08. Thickness = nearest-surface distance (free wall: to epicardium;
septum: to RV endocardium). Also cusp / summit site heights relative to the aortic-valve plane (from a04). Read only."""
import json
import numpy as np
from scipy.spatial import cKDTree
a4 = json.load(open('analysis/audit_2026-10-13/a04_anatomy.json'))
OUT = {}
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    lv, rv, epi, mv = rd('lv_endo'), rd('rv_endo'), rd('epi'), rd('mv_rim')
    v = np.loadtxt(B + 'uvc/v.dat'); R = np.loadtxt(f'data/torso/atria/{h}_to_g001_rigid.txt')[:3]
    apex = P[int(json.load(open(B + 'summary_02.json'))['apex_node'])]; cmv = P[mv].mean(0)
    L = np.linalg.norm(cmv - apex); ax = (cmv - apex) / L
    proj = lambda u: (u - (u @ ax) * ax) / np.linalg.norm(u - (u @ ax) * ax)
    ant_h = R.T @ np.array([0, -1.0, 0])
    te, tr = cKDTree(P[epi]), cKDTree(P[rv])
    lve, rve = epi[v[epi] == 0], epi[v[epi] == 1]
    groove = lve[cKDTree(P[rve]).query(P[lve])[0] <= 2.0]
    fr = lambda X: ((X - apex) @ ax) / L
    res = {}
    for lev, (a, b) in (('basal', (0.65, 0.80)), ('mid', (0.40, 0.55)), ('apical', (0.15, 0.30))):
        sl = lv[(fr(P[lv]) >= a) & (fr(P[lv]) < b)]
        c = P[sl].mean(0)
        slr = rv[(fr(P[rv]) >= a) & (fr(P[rv]) < b)]
        e1 = proj(P[slr].mean(0) - c); e2 = np.cross(ax, e1)
        if proj(ant_h) @ e2 < 0: e2 = -e2
        ang = lambda Y: np.degrees(np.arctan2((Y - c) @ e2, (Y - c) @ e1))
        gs = groove[(fr(P[groove]) >= a - 0.03) & (fr(P[groove]) < b + 0.03)]
        ga = ang(P[gs]); ia, ii = float(np.median(ga[ga > 0])), float(np.median(ga[ga < 0]))
        th = ang(P[sl])
        sept = (th >= ii) & (th <= ia)
        fw = ((th - ia) % 360) / ((ii - ia) % 360)
        dsep = tr.query(P[sl])[0]; dfw = te.query(P[sl])[0]
        segs = {}
        if lev == 'apical':
            segs['septal'] = sept; segs['anterior'] = ~sept & (fw < 1 / 3); segs['lateral'] = ~sept & (fw >= 1 / 3) & (fw < 2 / 3); segs['inferior'] = ~sept & (fw >= 2 / 3)
        else:
            mid_s = (ia + ii) / 2
            segs['anteroseptal'] = sept & (th >= mid_s); segs['inferoseptal'] = sept & (th < mid_s)
            for k, name in enumerate(['anterior', 'anterolateral', 'inferolateral', 'inferior']):
                segs[name] = ~sept & (fw >= k / 4) & (fw < (k + 1) / 4)
        res[lev] = {'insertions_deg(ant,inf)': [round(ia), round(ii)], 'septal_arc_deg': round(ia - ii)}
        for name, m in segs.items():
            d = np.where(sept, dsep, dfw)[m]
            res[lev][name] = [round(float(np.median(d)), 1), int(m.sum())] if m.any() else None
    cap = lv[fr(P[lv]) < 0.08]
    res['apex_cap(<0.08)'] = [round(float(np.median(te.query(P[cap])[0])), 1), int(len(cap))] if len(cap) else None
    sites = a4[h]['sites_outflow_summit_vein']
    res['cusp_summit_sites'] = {k: {kk: s[kk] for kk in ('wall_mm(site grid)', 'depth_achieved', 'height_vs_AV_plane_mm(+ = aortic side)', 'dist_AV_rim_mm', 'tag')} for k, s in sites.items() if ('cusp' in k or 'summit' in k)}
    OUT[h] = res
    print(h, json.dumps({k: v_ for k, v_ in res.items() if k != 'cusp_summit_sites'}))
json.dump(OUT, open('analysis/audit_2026-10-13/a11_aha_thickness.json', 'w'), indent=1)
for h in OUT:
    print(h, {k: (v_['height_vs_AV_plane_mm(+ = aortic side)'], v_['wall_mm(site grid)']) for k, v_ in OUT[h]['cusp_summit_sites'].items() if k.endswith('d50') or k.endswith('d10')})
