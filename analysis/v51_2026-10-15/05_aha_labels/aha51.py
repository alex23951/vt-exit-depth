"""Step 5 (v5.1 brief; decision F): AHA-segment labels for the pilot sites (read only) and a placement rule for study hearts
(geometry-only dry run). Based on the 14 Oct audit's a05_site_labels.py and a11_aha_thickness.py (copies beside this file;
sha256 of the originals in audit_originals.sha256): same frame and insertion rule, applied to every pilot site.

Frame (as a05): long axis = apex node (summary_02.json) -> mitral-ring centroid; f = fraction along it (apex 0, MV 1).
At a site's height (for sites above the last height with an LV slab and both insertions, i.e. on the AV ring, the frame
of that last height, noted per site): LV cavity centre c = centroid of LV endocardial nodes within 2 mm of that height; e1 = towards the RV
endocardial nodes within 3 mm (septal centre); e2 = long axis x e1, signed towards the body's anterior (-y torso, R^T);
angle 0 = septal centre, + = anterior. RV insertions: LV epicardial nodes within 2 mm of the RV epicardium, within 3 mm of
that height, median angle of the + side (anterior insertion) and of the - side (inferior insertion).
AHA segments (Cerqueira 2002): levels by f, thirds of the apex -> MV axis (apical < 1/3, mid < 2/3, basal >= 2/3) with an
apex cap f < 0.08 (segment 17; the cap limit as a11); septum = arc between the insertions (basal / mid: anteroseptal /
inferoseptal halves; apical: septal); free wall = the other arc, 4 equal parts at basal / mid (anterior, anterolateral,
inferolateral, inferior) and 3 at apical (anterior, lateral, inferior). Thirds and the apex cap are my reading (inference).
Body-defined Bazan region: superior if the site direction from c has a positive component along the body's superior (+z
torso, R^T) projected into the short-axis plane, else inferior; basal if f >= 0.5, else apical (inference).
Site position: the site node (summit and vein-course sites: their epicardial end node, as a05). Tissue label: the element
tags of the site node in biv.elem.

Usage (repo root, venv): python -B analysis/v51_2026-10-15/05_aha_labels/aha51.py
Writes: pilot_site_labels.csv, insertions.json, placement_dry_run.csv, summary.json in this folder. Reads only.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LV_FAM = ['lv_free_wall', 'lv_septum', 'lv_summit', 'lv_vein_course', 'aortic_cusp']
SEG_NO = {('basal', 'anterior'): 1, ('basal', 'anteroseptal'): 2, ('basal', 'inferoseptal'): 3, ('basal', 'inferior'): 4,
          ('basal', 'inferolateral'): 5, ('basal', 'anterolateral'): 6, ('mid', 'anterior'): 7, ('mid', 'anteroseptal'): 8,
          ('mid', 'inferoseptal'): 9, ('mid', 'inferior'): 10, ('mid', 'inferolateral'): 11, ('mid', 'anterolateral'): 12,
          ('apical', 'anterior'): 13, ('apical', 'septal'): 14, ('apical', 'inferior'): 15, ('apical', 'lateral'): 16, ('apex', 'apex'): 17}
DEPTHS = (0.1, 0.5, 0.75, 0.9)
FLAGS = {('6G8DD8S5', 'rv_free_wall_q75_z0.25'), ('7D98EVAR', 'rv_free_wall_q25_z0.25')}


class Frame:
    def __init__(self, h):
        B = os.path.join(REPO, 'data', 'biv', h)
        self.P = np.loadtxt(os.path.join(B, 'biv.pts'), skiprows=1) / 1e3
        rd = lambda n: np.loadtxt(os.path.join(B, 'surfaces', f'{n}.vtx'), skiprows=2, dtype=np.int64)
        self.lv, self.rv, self.epi, mv = rd('lv_endo'), rd('rv_endo'), rd('epi'), rd('mv_rim')
        v = np.loadtxt(os.path.join(B, 'uvc', 'v.dat'))
        R = np.loadtxt(os.path.join(REPO, 'data', 'torso', 'atria', f'{h}_to_g001_rigid.txt'))[:3]
        self.apex = self.P[int(json.load(open(os.path.join(B, 'summary_02.json')))['apex_node'])]
        cmv = self.P[mv].mean(0)
        self.Lax = float(np.linalg.norm(cmv - self.apex)); self.ax = (cmv - self.apex) / self.Lax
        self.sup, self.ant = R.T @ np.array([0, 0, 1.0]), R.T @ np.array([0, -1.0, 0])
        lve, rve = self.epi[v[self.epi] == 0], self.epi[v[self.epi] == 1]
        self.groove = lve[cKDTree(self.P[rve]).query(self.P[lve])[0] <= 2.0]

    def proj(self, u):
        w = u - (u @ self.ax) * self.ax
        return w / np.linalg.norm(w)

    def f(self, X):
        return ((X - self.apex) @ self.ax) / self.Lax

    def local(self, a_mm):
        """Short-axis frame at height a_mm above the apex: c, e1, e2, insertion angles (ant, inf)."""
        P, ax = self.P, self.ax
        h_ = lambda idx: (P[idx] - self.apex) @ ax
        sl = self.lv[np.abs(h_(self.lv) - a_mm) < 2.0]
        if len(sl) < 10:
            return None
        c = P[sl].mean(0)
        slr = self.rv[np.abs(h_(self.rv) - a_mm) < 3.0]
        e1 = self.proj(P[slr].mean(0) - c) if len(slr) > 10 else self.proj(P[self.rv].mean(0) - c)
        e2 = np.cross(ax, e1)
        if self.proj(self.ant) @ e2 < 0:
            e2 = -e2
        gs = self.groove[np.abs(h_(self.groove) - a_mm) < 3.0]
        ga = np.degrees(np.arctan2((P[gs] - c) @ e2, (P[gs] - c) @ e1)) if len(gs) else np.array([])
        ia = float(np.median(ga[ga > 0])) if (ga > 0).any() else np.nan
        ii = float(np.median(ga[ga < 0])) if (ga < 0).any() else np.nan
        return c, e1, e2, ia, ii

    def label(self, X):
        f = float(self.f(X))
        a_mm = f * self.Lax
        loc = self.local(a_mm)
        if f < 0.08:
            return {'f': f, 'level': 'apex', 'segment': 'apex', 'aha': 17, 'angle': np.nan, 'ins_ant': np.nan, 'ins_inf': np.nan,
                    'body_superior': self.body_sup(X, loc), 'note': ''}
        level = 'apical' if f < 1 / 3 else ('mid' if f < 2 / 3 else 'basal')
        note, a_use = '', a_mm
        while loc is None or np.isnan(loc[3]) or np.isnan(loc[4]):      # above the last height with an LV slab and both
            a_use -= 1.0                                                  # insertions (AV-ring sites): that height's frame
            if a_use < 0:
                return {'f': f, 'level': level, 'segment': 'n/a', 'aha': None, 'angle': np.nan, 'ins_ant': np.nan, 'ins_inf': np.nan,
                        'body_superior': self.body_sup(X, None), 'note': 'no frame'}
            loc = self.local(a_use)
            note = f'frame from {a_mm - a_use:.0f} mm lower (no LV slab or RV insertion at the site height)'
        c, e1, e2, ia, ii = loc
        th = float(np.degrees(np.arctan2((X - c) @ e2, (X - c) @ e1)))
        if ii <= th <= ia:
            seg = 'septal' if level == 'apical' else ('anteroseptal' if th >= (ia + ii) / 2 else 'inferoseptal')
        else:
            fw = ((th - ia) % 360) / ((ii - ia) % 360)
            seg = (['anterior', 'lateral', 'inferior'][min(2, int(fw * 3))] if level == 'apical'
                   else ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))])
        return {'f': f, 'level': level, 'segment': seg, 'aha': SEG_NO[(level, seg)], 'angle': th, 'ins_ant': ia, 'ins_inf': ii,
                'body_superior': self.body_sup(X, loc), 'note': note}

    def body_sup(self, X, loc):
        c = loc[0] if loc is not None else self.apex + (float(self.f(X)) * self.Lax) * self.ax
        return bool(self.proj(self.sup) @ self.proj(X - c) > 0)


def main():
    rows, ins_out, place, summ = [], {}, [], {}
    for h in HEARTS:
        F = Frame(h)
        B = os.path.join(REPO, 'data', 'biv', h)
        S = pd.read_csv(os.path.join(B, 'sites.csv'))
        Ee = np.loadtxt(os.path.join(B, 'biv.elem'), skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64)
        tags = {}
        need = set(S.node.astype(int))
        for k in range(4):
            m = np.isin(Ee[:, k], list(need))
            for n_, t_ in zip(Ee[m, k], Ee[m, 4]):
                tags.setdefault(int(n_), set()).add(int(t_))
        # insertion points per level (band centres as a11: basal 0.725, mid 0.475, apical 0.225)
        ins_out[h] = {}
        for lev, fc in (('basal', 0.725), ('mid', 0.475), ('apical', 0.225)):
            c, e1, e2, ia, ii = F.local(fc * F.Lax)
            pt = lambda a: (c + 20.0 * (np.cos(np.radians(a)) * e1 + np.sin(np.radians(a)) * e2)).round(2).tolist()
            ins_out[h][lev] = {'f': fc, 'anterior_insertion_deg': round(ia, 1), 'inferior_insertion_deg': round(ii, 1),
                               'septal_arc_deg': round(ia - ii, 1), 'cavity_centre_mm': c.round(2).tolist(),
                               'anterior_insertion_dir_20mm': pt(ia), 'inferior_insertion_dir_20mm': pt(ii)}
        for _, s in S.iterrows():
            lvf = s.family in LV_FAM
            use_epi = s.family in ('lv_summit', 'lv_vein_course') and not pd.isna(s.epi_end_node)
            X = F.P[int(s.epi_end_node)] if use_epi else F.P[int(s.node)]
            r = {'heart': h, 'site': s.id, 'family': s.family, 'old_name': s['name'], 'old_bazan_region': s.bazan_region,
                 'depth_target': s.depth_target, 'tissue_tags': ' '.join(str(t) for t in sorted(tags.get(int(s.node), []))),
                 'flag_lv_tagged_rv_site': (h, s.id.rsplit('_d', 1)[0]) in FLAGS}
            lab = F.label(X)
            r.update({'f_apex_to_mv': round(lab['f'], 3), 'aha_level': lab['level'],
                      'aha_segment': (lab['segment'] if lvf else 'n/a (RV family)'), 'aha_number': (lab['aha'] if lvf else None),
                      'angle_from_septal_centre_deg': round(lab['angle'], 1) if lab['angle'] == lab['angle'] else None,
                      'body_bazan_region': f"lv_{'basal' if lab['f'] >= 0.5 else 'apical'}_{'superior' if lab['body_superior'] else 'inferior'}" if lvf else 'n/a',
                      'position_used': 'epicardial end node' if use_epi else 'site node',
                      'aortic_root_site': s.family == 'aortic_cusp', 'note': lab['note']})
            rows.append(r)
        # placement dry run: AHA segment centres x pilot depths; endocardial point at the centre angle and level,
        # transmural line to the nearest epicardial node (free wall) or RV endocardial node (septum)
        te, tr, tl = cKDTree(F.P[F.epi]), cKDTree(F.P[F.rv]), cKDTree(F.P[F.lv])
        tall = cKDTree(F.P)
        old = S[S.family.isin(LV_FAM)]
        oldX = F.P[old.node.astype(int).values]
        for (lev, seg), num in SEG_NO.items():
            if lev == 'apex':
                fc, ang = 0.04, None
            else:
                fc = {'apical': (0.08 + 1 / 3) / 2, 'mid': 0.5, 'basal': (2 / 3 + 0.9) / 2}[lev]
            if lev != 'apex':
                loc = F.local(fc * F.Lax)
                if loc is None:
                    continue
                c, e1, e2, ia, ii = loc
                arc_s, arc_f = ia - ii, (ii - ia) % 360
            if lev == 'apex':                                  # segment 17: the LV endocardial apex (lowest LV endocardial node)
                pass
            else:
                if seg in ('anteroseptal', 'inferoseptal', 'septal'):
                    a0 = {'anteroseptal': ii + 0.75 * arc_s, 'inferoseptal': ii + 0.25 * arc_s, 'septal': ii + 0.5 * arc_s}[seg]
                else:
                    parts = ['anterior', 'lateral', 'inferior'] if lev == 'apical' else ['anterior', 'anterolateral', 'inferolateral', 'inferior']
                    k = parts.index(seg); a0 = ia + (k + 0.5) * arc_f / len(parts)
                d = np.cos(np.radians(a0)) * e1 + np.sin(np.radians(a0)) * e2
            # endocardial node: LV endocardial node closest to the ray from c in direction d (within the level slab)
            if lev == 'apex':
                n0 = int(F.lv[np.argmin(F.f(F.P[F.lv]))])
            else:
                cand = F.lv[np.abs(F.f(F.P[F.lv]) - fc) < 0.03]
                rel = F.P[cand] - c
                off = np.linalg.norm(rel - np.outer(rel @ d, d), axis=1) + 1e3 * (rel @ d < 0)
                n0 = int(cand[np.argmin(off)])
            sept = seg in ('anteroseptal', 'inferoseptal', 'septal')
            n1 = int(F.rv[tr.query(F.P[n0])[1]]) if sept else int(F.epi[te.query(F.P[n0])[1]])
            wall = float(np.linalg.norm(F.P[n1] - F.P[n0]))
            for dep in DEPTHS:
                X = F.P[n0] + dep * (F.P[n1] - F.P[n0])
                node = int(tall.query(X)[1])
                lab = F.label(F.P[node])
                dist_old = float(np.min(np.linalg.norm(oldX - F.P[node], axis=1)))
                place.append({'heart': h, 'aha_number': num, 'aha_level': lev, 'aha_segment': seg, 'depth_target': dep,
                              'node': node, 'wall_mm': round(wall, 1), 'line_to': 'RV endocardium' if sept else 'epicardium',
                              'label_check_segment': lab['aha'], 'body_bazan_region': f"lv_{'basal' if lab['f'] >= 0.5 else 'apical'}_{'superior' if lab['body_superior'] else 'inferior'}",
                              'dist_to_nearest_old_lv_site_mm': round(dist_old, 1)})
        D = pd.DataFrame([r for r in rows if r['heart'] == h])
        lvD = D[D.family.isin(LV_FAM)]
        summ[h] = {'lv_sites': int(len(lvD)), 'lv_sites_with_one_segment': int(lvD.aha_number.notna().sum()),
                   'segments_used': {int(k): int(v) for k, v in lvD.aha_number.value_counts().sort_index().items()},
                   'old_vs_body_bazan_disagree': int((lvD[lvD.family != 'aortic_cusp'].old_bazan_region != lvD[lvD.family != 'aortic_cusp'].body_bazan_region).sum()),
                   'flags': D[D.flag_lv_tagged_rv_site][['site', 'tissue_tags']].to_dict('records')}
        print(h, json.dumps(summ[h]), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, 'pilot_site_labels.csv'), index=False)
    pd.DataFrame(place).to_csv(os.path.join(HERE, 'placement_dry_run.csv'), index=False)
    json.dump(ins_out, open(os.path.join(HERE, 'insertions.json'), 'w'), indent=1)
    json.dump(summ, open(os.path.join(HERE, 'summary.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
