"""Audit 05: are the LV site names / Bazan regions where the names say? (read only)
For each LV-side site: direction from the LV cavity centre of its level (slab +-2 mm along the apex->MV-centroid axis),
in the short-axis plane. References: septal centre (RV endocardial slab centroid), torso superior (+z) and anterior (-y)
projected into the plane (heart frame via R^T), and the two RV insertion lines (LV epicardial nodes within 2 mm of the RV
epicardium, split by side). AHA-style label (Cerqueira 2002): septum = arc between the insertions through the septal
centre (2 equal parts: anteroseptal / inferoseptal); free wall = the other arc in 4 equal parts (anterior, anterolateral,
inferolateral, inferior)."""
import json
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
OUT = {}
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    lv, rv, epi, mv = rd('lv_endo'), rd('rv_endo'), rd('epi'), rd('mv_rim')
    v = np.loadtxt(B + 'uvc/v.dat')
    R = np.loadtxt(f'data/torso/atria/{h}_to_g001_rigid.txt')[:3]
    apex = int(json.load(open(B + 'summary_02.json'))['apex_node'])
    cmv = P[mv].mean(0); ax = (cmv - P[apex]) / np.linalg.norm(cmv - P[apex])        # apex -> base
    sup_h, ant_h = R.T @ np.array([0, 0, 1.0]), R.T @ np.array([0, -1.0, 0])
    proj = lambda u: (u - (u @ ax) * ax) / np.linalg.norm(u - (u @ ax) * ax)
    lve, rve = epi[v[epi] == 0], epi[v[epi] == 1]
    groove = lve[cKDTree(P[rve]).query(P[lve])[0] <= 2.0]
    S = pd.read_csv(B + 'sites.csv')
    S = S[S.family.isin(['lv_free_wall', 'lv_septum', 'lv_summit', 'lv_vein_course', 'aortic_cusp']) & (S.depth_target == 0.5)]
    rows = []
    for _, s in S.iterrows():
        X = P[int(s.epi_end_node)] if s.family in ('lv_summit', 'lv_vein_course') and not np.isnan(s.epi_end_node) else P[int(s.node)]
        a_ = (X - P[apex]) @ ax
        sl = lv[np.abs((P[lv] - P[apex]) @ ax - a_) < 2.0]
        if len(sl) < 10:
            continue
        c = P[sl].mean(0)
        slr = rv[np.abs((P[rv] - P[apex]) @ ax - a_) < 3.0]
        e1 = proj(P[slr].mean(0) - c) if len(slr) > 10 else proj(np.array(P[rv].mean(0) - c))
        e2 = np.cross(ax, e1)
        if proj(ant_h) @ e2 < 0: e2 = -e2                 # +angle towards anterior
        ang = lambda Y: np.degrees(np.arctan2((Y - c) @ e2, (Y - c) @ e1))
        th = float(ang(X))
        gs = groove[np.abs((P[groove] - P[apex]) @ ax - a_) < 3.0]
        ga = ang(P[gs]) if len(gs) else np.array([])
        ins_a = float(np.median(ga[ga > 0])) if (ga > 0).any() else np.nan     # anterior insertion
        ins_i = float(np.median(ga[ga < 0])) if (ga < 0).any() else np.nan     # inferior insertion
        if np.isnan(ins_a) or np.isnan(ins_i):
            aha = 'n/a (no insertion at this level)'
        elif ins_i <= th <= ins_a:
            aha = 'anteroseptal' if th >= (ins_a + ins_i) / 2 else 'inferoseptal'
        else:
            fw = ((th - ins_a) % 360) / ((ins_i - ins_a) % 360)               # 0 at anterior insertion -> 1 at inferior insertion
            aha = ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))]
        dsup = float(proj(sup_h) @ proj(X - c))
        rows.append({'id': s.id, 'name': s['name'], 'uvc_phi': round(s.phi_deg, 0), 'bazan_region(UVC)': s.bazan_region,
                     'angle_from_septal_centre_deg(+ant)': round(th, 0), 'ant_insertion_deg': round(ins_a, 0), 'inf_insertion_deg': round(ins_i, 0),
                     'AHA_like_label': aha, 'cos_to_body_superior': round(dsup, 2), 'body_superior_half': dsup > 0})
    df = pd.DataFrame(rows)
    df.to_csv(f'analysis/audit_2026-10-13/a05_site_labels_{h}.csv', index=False)
    sup_uvc = df['bazan_region(UVC)'].str.contains('superior')
    OUT[h] = {'n_positions': len(df), 'bazan_superior_UVC_vs_body_superior_disagree': int((sup_uvc != df.body_superior_half).sum()),
              'disagreeing': df[sup_uvc != df.body_superior_half][['id', 'uvc_phi', 'bazan_region(UVC)', 'cos_to_body_superior', 'AHA_like_label']].to_dict('records'),
              'name_vs_AHA': df[['id', 'name', 'uvc_phi', 'angle_from_septal_centre_deg(+ant)', 'AHA_like_label', 'bazan_region(UVC)', 'cos_to_body_superior']].to_dict('records')}
    print(h); print(df[['id', 'uvc_phi', 'angle_from_septal_centre_deg(+ant)', 'ant_insertion_deg', 'inf_insertion_deg', 'AHA_like_label', 'bazan_region(UVC)', 'cos_to_body_superior']].to_string())
json.dump(OUT, open('analysis/audit_2026-10-13/a05_site_labels.json', 'w'), indent=1, default=str)
