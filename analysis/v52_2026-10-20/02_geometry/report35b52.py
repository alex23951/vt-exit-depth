"""v5.2 step 2d: report 35 re-run after 2b-2d and before any beat (LOCK.md 15.2 step 2d; deviations D13, D15). Report only.

(a) and (h) at de Kerchove's six positions and (e) at the L/R commissure and the RCS, in the D15 aortic frame (geom52),
with each valve disc's thickness and two faces (2nd / 98th percentile of the disc nodes' height about its mid-plane) and,
per position, the muscle above each face on the v5.1 mesh (the existing muscle) and on the built mesh (v5.1 plus the
re-tagged crescent and sleeve elements). Same definitions as step 0's report 35 (step0_report35.py) except the frame:
heights are axial from the disc mid-plane; positions are +-10 deg windows; "muscle above a face" = the highest
ventricular-muscle element centroid within the ring radius + 6 mm of the axis, minus that face's height.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/report35b52.py [HEART ...]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402

DK = {'N/L': 0.0, 'LCS': 60.2, 'L/R': 120.4, 'RCS': 180.7, 'R/N': 241.0, 'NCS': 300.5}       # as step 0 (derived from Toh 2020)
DK_EXT = {'NCS': -0.1, 'N/L': 0.3, 'LCS': 0.5, 'L/R': 4.6, 'RCS': 2.4, 'R/N': 2.5}
WIN = 10.0


def adiff(a, b):
    return np.abs((a - b + 180) % 360 - 180)


def run(h):
    P, E, tag = G.load_full(h)
    z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
    built = tag.copy(); built[z['crescent_elements']] = 1; built[z['sleeve_elements']] = 2
    av, avr = G.aortic_frame(P, E, tag); pv, pvr = G.pulmonary_frame(P, E, tag)
    cen = P[E].mean(1)
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'frame': 'D15 (theta 0 = projected mitral-disc centroid; sense from the pulmonary-disc centroid)',
           'aortic_disc': {'thickness_mm': round(av.thickness, 2), 'faces_mm (ventricular, arterial)': [round(x, 2) for x in av.faces], 'frame_check': avr},
           'pulmonary_disc': {'thickness_mm': round(pv.thickness, 2), 'faces_mm (ventricular, arterial)': [round(x, 2) for x in pv.faces], 'frame': pvr}}
    fa, a, b = G.interfaces(E, tag)
    pair = lambda t1, t2: fa[((tag[a] == t1) & (tag[b] == t2)) | ((tag[a] == t2) & (tag[b] == t1))]
    rra = float(np.median(av.r(P[av.ring])))
    def top(tags_arr, mtags, valve, th, rmax):
        m = np.isin(tags_arr, mtags) & (valve.r(cen) < rmax) & (valve.h(cen) > -6) & (valve.h(cen) < 30) & (adiff(valve.theta(cen), th) <= WIN)
        return float(valve.h(cen[m]).max()) if m.any() else np.nan
    n15 = np.unique(pair(1, 5)); th15, h15, r15 = av.theta(P[n15]), av.h(P[n15]), av.r(P[n15])
    pos = {}
    for k, thk in DK.items():
        m = adiff(th15, thk) <= WIN
        ex, bu = top(tag, G.LV_GROUP, av, thk, rra + 6), top(built, G.LV_GROUP, av, thk, rra + 6)
        row = {'theta_deg': thk, 'boundary_nodes': int(m.sum()), 'de_Kerchove_external_junction_mm': DK_EXT[k],
               'ring_point_height_mm': round(float(av.h(P[av.ring_point(thk)])[0]), 2),
               'muscle_top_mm (existing, built)': [round(ex, 2), round(bu, 2)],
               'muscle_above_ventricular_face_mm (existing, built)': [round(ex - av.faces[0], 2), round(bu - av.faces[0], 2)],
               'muscle_above_arterial_face_mm (existing, built)': [round(ex - av.faces[1], 2), round(bu - av.faces[1], 2)]}
        if m.any():
            il, ie = np.argmin(r15[m]), np.argmax(r15[m])
            row.update({'35a_luminal_height_mm': round(float(h15[m][il]), 2), '35a_epicardial_height_mm': round(float(h15[m][ie]), 2),
                        '35h_below_valve_plane': bool(min(h15[m][il], h15[m][ie]) < 0)})
        pos[k] = row
    rec['35a_35h_aortic_positions'] = pos
    rec['35h_any_below_valve_plane'] = any(v.get('35h_below_valve_plane') for v in pos.values())
    for nm, tg in (('existing', tag), ('built', built)):
        fa2, a2, b2 = G.interfaces(E, tg)
        k25 = (np.isin(tg[a2], G.RV_GROUP) & (tg[b2] == 5)) | ((tg[a2] == 5) & np.isin(tg[b2], G.RV_GROUP))
        n25 = np.unique(fa2[k25]); th25, h25 = av.theta(P[n25]), av.h(P[n25])
        for k in ('L/R', 'RCS'):
            m = adiff(th25, DK[k]) <= WIN
            rec.setdefault('35e_rv_contact_on_aortic_root', {}).setdefault(k, {})[nm] = {
                'contact_nodes': int(m.sum()), 'max_height_above_mid_plane_mm': round(float(h25[m].max()), 2) if m.any() else None,
                'de_Kerchove_mm': DK_EXT[k]}
    rrp = float(np.median(pv.r(P[pv.ring])))
    rec['pulmonary_sinus_centres'] = {}
    for k, thc in {'posterior': 0.0, 'sinus_+120': 120.0, 'sinus_-120': 240.0}.items():
        ex, bu = top(tag, G.RV_GROUP, pv, thc, rrp + 6), top(built, G.RV_GROUP, pv, thc, rrp + 6)
        rec['pulmonary_sinus_centres'][k] = {'muscle_top_mm (existing, built)': [round(ex, 2), round(bu, 2)],
                                             'muscle_above_ventricular_face_mm (existing, built)': [round(ex - pv.faces[0], 2), round(bu - pv.faces[0], 2)],
                                             'muscle_above_arterial_face_mm (existing, built)': [round(ex - pv.faces[1], 2), round(bu - pv.faces[1], 2)]}
    G.dump(rec, os.path.join(HERE, f'report35b52_{h}.json'))
    print(h, 'aortic disc', rec['aortic_disc']['thickness_mm'], rec['aortic_disc']['faces_mm (ventricular, arterial)'],
          {k: v['muscle_above_arterial_face_mm (existing, built)'] for k, v in pos.items()}, '35h below:', rec['35h_any_below_valve_plane'], flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
