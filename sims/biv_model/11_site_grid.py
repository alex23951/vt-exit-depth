#!/usr/bin/env python
"""
Step 11: pre-registered exit-site grid for one heart (selection only, no simulation).

Surface positions (per heart, 33):
  LV        3 apicobasal levels (z = 0.25, 0.50, 0.75) x 6 rotational positions
            (UVC phi = 0, +-60, +-120, 180 deg; 0 = septal centre). Positions whose
            endocardial point is nearer the RV endocardium than the epicardium are septal.
  RV free wall  3 levels x 3 positions (25th / 50th / 75th percentile of the free-wall
            phi range at that level).
  RVOT      2: RV endocardium in the outflow tract (Doste weight w < 0.3), 8-15 mm below
            the pulmonary rim: septal side (nearest the aortic interface) and free-wall side
            (farthest from it).
  LV summit 2: LV epicardium 8-20 mm from the aortic interface, the most superior point
            (torso z) and the most leftward (torso x) of those.
  Aortic-cusp region 2: LV muscle at the aortic annulus (nodes on the AV rim / aortic
            interface): under the right coronary cusp = most anterior-rightward point,
            under the left coronary cusp = most leftward-posterior point (torso frame).
            The cohort meshes have no cusps; these are annular LV muscle sites.
Depths (each position): 10 %, 50 % and 90 % of wall depth. Free wall, RV, RVOT, summit
  and cusp sites use rho (0 endo -> 1 epi; summit from the epicardium inwards is the
  same scale); septal LV sites use sep (0 LV endo -> 1 RV endo). The site node is the
  node near the transmural line through the surface point (local gradient of the depth
  field) whose depth value is closest to the target.
Total 33 x 3 = 99 sites per heart. Each site records its actual depth; sites more than
0.1 from the target depth are flagged depth_miss (e.g. septal RVOT at 50 %: no epicardium).

Names come from torso directions: the site's radial direction (perpendicular to the LV
long axis) in the torso frame (LPS: +x left, -y anterior, +z superior) gives an AHA-style
sector (anterior, anterolateral, inferolateral, inferior, inferoseptal, anteroseptal).
Bazan region (ecg_depth_criteria REGIONS): basal if z >= 0.5 else apical (the z = 0.5
level is flagged level_boundary), superior if the radial direction points up (torso z > 0)
else inferior; RVOT -> rvot; summit and cusp sites -> lv_basal_superior.

Writes data/biv/<HEART>/sites.csv and sites.json.
"""

import csv
import json
import os

import numpy as np
from scipy.spatial import cKDTree

from common import HEART, OUT, REPO, read_pts, read_vtx

SURF = os.path.join(OUT, 'surfaces')
UVC = os.path.join(OUT, 'uvc')
LEVELS = (0.25, 0.50, 0.75)
LV_PHI = (0, 60, 120, 180, -120, -60)
DEPTHS = (0.10, 0.50, 0.90)
SECTORS = ['anterior', 'anterolateral', 'inferolateral', 'inferior', 'inferoseptal', 'anteroseptal']


def vtx(n):
    return read_vtx(os.path.join(SURF, n + '.vtx'))


def main():
    pts = read_pts(os.path.join(OUT, 'bivF')) / 1e3                      # mm, heart frame
    M = np.loadtxt(os.path.join(REPO, 'data', 'torso', 'atria', f'{HEART}_to_g001_rigid.txt'))
    T = pts @ M[:3].T + M[3]                                             # mm, torso frame
    z, phi, rho, sep, v = (np.loadtxt(os.path.join(UVC, n + '.dat')) for n in ('z', 'phi', 'rho', 'sep', 'v'))
    w = np.clip(np.loadtxt(os.path.join(OUT, 'laplace', 'w.dat')), 0, 1)
    lv, rv, epi = vtx('lv_endo'), vtx('rv_endo'), vtx('epi')
    tree_all = cKDTree(pts)
    t_epi, t_lv, t_rv = cKDTree(pts[epi]), cKDTree(pts[lv]), cKDTree(pts[rv])
    apex = T[vtx('apex')[0]]
    base_c = T[np.concatenate([vtx('mv_rim'), vtx('tv_rim')])].mean(0)
    ax = (base_c - apex) / np.linalg.norm(base_c - apex)
    lv_c = T[lv].mean(0)
    ant = np.array([0, -1.0, 0]); ant -= (ant @ ax) * ax; ant /= np.linalg.norm(ant)
    left = np.cross(ax, ant)
    if left[0] < 0:
        left = -left

    def radial(p):
        d = p - lv_c
        d = d - (d @ ax) * ax
        return d / max(np.linalg.norm(d), 1e-9)

    def sector(p):
        r = radial(p)
        ang = np.degrees(np.arctan2(r @ left, r @ ant)) % 360          # 0 anterior, 90 lateral
        return SECTORS[int(((ang + 30) % 360) // 60)], float(ang), float(r[2])

    def column(p_node, field, targets):
        """Nodes near the transmural line through p_node with field closest to each target."""
        cand = np.array(tree_all.query_ball_point(pts[p_node], 25.0))
        f = field[cand]
        # local gradient of the field by least squares around p_node
        near = np.array(tree_all.query_ball_point(pts[p_node], 4.0))
        A = np.c_[pts[near] - pts[p_node], np.ones(len(near))]
        g = np.linalg.lstsq(A, field[near], rcond=None)[0][:3]
        g /= max(np.linalg.norm(g), 1e-12)
        dvec = pts[cand] - pts[p_node]
        off = np.linalg.norm(dvec - np.outer(dvec @ g, g), axis=1)       # distance from the line
        out = []
        for tg in targets:
            score = np.abs(f - tg) + off / 10.0
            out.append(int(cand[np.argmin(score)]))
        return out

    sites = []

    def add(family, level, pos, p_node, depth_field_name):
        field = rho if depth_field_name == 'rho' else sep
        nodes = column(p_node, field, DEPTHS)
        for dt, n in zip(DEPTHS, nodes):
            sec, ang, up = sector(T[n])
            if family == 'rvot':
                region = 'rvot'
            elif family in ('lv_summit', 'aortic_cusp'):
                region = 'lv_basal_superior'
            else:
                ch = 'rv' if family == 'rv_free_wall' else 'lv'
                region = f"{ch}_{'basal' if z[n] >= 0.5 else 'apical'}_{'superior' if up > 0 else 'inferior'}"
            sites.append({'id': f'{family}_{pos}_z{level}_d{int(dt * 100)}', 'family': family,
                          'level_z': level, 'position': pos, 'depth_target': dt, 'depth_field': depth_field_name,
                          'node': n, 'z': float(z[n]), 'phi_deg': float(np.degrees(phi[n])),
                          'rho': float(rho[n]), 'sep': float(sep[n]),
                          'torso_mm': T[n].round(2).tolist(), 'sector': sec, 'sector_angle_deg': round(ang, 1),
                          'name': f"{family.replace('_', ' ')} {level if level != '' else ''} {sec}".strip(),
                          'bazan_region': region, 'level_boundary': bool(level == 0.5),
                          'depth_actual': float(field[n]),
                          'depth_miss': bool(abs(field[n] - dt) > 0.1)})

    # LV grid
    for lev in LEVELS:
        for ph in LV_PHI:
            score = np.abs(z[lv] - lev) * 10 + np.abs(np.angle(np.exp(1j * (phi[lv] - np.radians(ph)))))
            p = int(lv[np.argmin(score)])
            # septal only within +-60 deg of the septal centre (the distance test alone
            # misfires near the RV insertions)
            septal = abs(ph) <= 60 and t_rv.query(pts[p])[0] < t_epi.query(pts[p])[0]
            add('lv_septum' if septal else 'lv_free_wall', lev, f'phi{ph}', p, 'sep' if septal else 'rho')
    # RV free wall
    rv_fw = rv[t_epi.query(pts[rv])[0] < t_lv.query(pts[rv])[0]]
    for lev in LEVELS:
        band = rv_fw[np.abs(z[rv_fw] - lev) < 0.03]
        ph = np.degrees(phi[band])
        for q, nm in ((25, 'q25'), (50, 'q50'), (75, 'q75')):
            target = np.percentile(ph, q)
            p = int(band[np.argmin(np.abs(ph - target))])
            add('rv_free_wall', lev, nm, p, 'rho')
    # RVOT
    ao = T[np.concatenate([vtx('ao_iface'), vtx('av_rim')])]
    pv = cKDTree(pts[vtx('pv_rim')])
    d_pv = pv.query(pts[rv])[0]
    ot = rv[(w[rv] < 0.3) & (d_pv > 8) & (d_pv < 15)]
    d_ao = cKDTree(ao).query(T[ot])[0]
    add('rvot', '', 'septal', int(ot[np.argmin(d_ao)]), 'rho')
    add('rvot', '', 'free_wall', int(ot[np.argmax(d_ao)]), 'rho')
    # LV summit (epicardial reference; depth field rho runs endo 0 -> epi 1)
    d_ao_epi = cKDTree(ao).query(T[epi])[0]
    lv_epi = epi[(v[epi] == 0) & (d_ao_epi > 8) & (d_ao_epi < 20)]
    add('lv_summit', '', 'superior', int(lv_epi[np.argmax(T[lv_epi, 2])]), 'rho')
    add('lv_summit', '', 'leftward', int(lv_epi[np.argmax(T[lv_epi, 0])]), 'rho')
    # aortic-cusp region: LV muscle at the annulus
    ann = np.unique(np.concatenate([vtx('av_rim'), vtx('ao_iface')]))
    ann = ann[v[ann] == 0]
    add('aortic_cusp', '', 'rcc', int(ann[np.argmax(-T[ann, 1] - T[ann, 0])]), 'rho')
    add('aortic_cusp', '', 'lcc', int(ann[np.argmax(T[ann, 0] + T[ann, 1])]), 'rho')

    with open(os.path.join(OUT, 'sites.json'), 'w') as f:
        json.dump(sites, f, indent=1)
    keys = [k for k in sites[0] if k != 'torso_mm'] + ['x_mm', 'y_mm', 'z_mm']
    with open(os.path.join(OUT, 'sites.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        for s in sites:
            r = {k: s[k] for k in keys if k in s}
            r['x_mm'], r['y_mm'], r['z_mm'] = s['torso_mm']
            wr.writerow(r)
    fam = {}
    for s in sites:
        fam[s['family']] = fam.get(s['family'], 0) + 1
    print(json.dumps({'heart': HEART, 'sites': len(sites), 'by_family': fam}, indent=1))


if __name__ == '__main__':
    main()
