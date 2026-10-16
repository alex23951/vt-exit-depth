#!/usr/bin/env python
"""
RVOT anatomy and septal crossing, 12-13 Oct 2026 (coordinator brief; graph-only beats + geometry, no openCARP, no new
lead fields; frozen files only read). Run per heart: HEART=<id> python rvot_anatomy.py; then python rvot_anatomy.py report

1 Septal crossing (Betensky 2013, Circ Arrhythm Electrophysiol 6:1123, PMID 24106241: basal RV septal pacing without
  septal scar, LV transseptal time 25.7 +- 8.8 ms; > 40 ms specific for scar). Network v3 as built (6G8DD8S5 with its
  left-bundle cut), combined graph of 14_purkinje.py (graph scale k), stimulus = nodes within 1.5 mm at 0 ms.
  Sites: RV septal endocardial nodes (RV endocardium nearer the LV endocardium than the epicardium, build()'s rule) at
  UVC z 0.70 / 0.78 / 0.85, phi = the circular mean phi of the RV septal surface in that band.
  Measures: stimulus -> earliest LV septal endocardium (LV endocardium nearer the RV endocardium than the epicardium) and
  -> the LV endocardial node opposite the site (nearest LV endocardial node), with the network and myocardium-only;
  septal thickness = distance to that opposite LV node; route = network if the network field reaches the LV septum
  > 0.5 ms earlier than the myocardium-only field, else myocardium.
  RVOT septal sites (grid, z 0.98-1.0): myocardium-only time and shortest myocardial path length (tet edges) to the
  nearest LV endocardial node and to the nearest UVC v = 0 node, against the straight-line distances.
2 Anatomy in the torso (T13, frame +x left, -y anterior, +z superior; mm): RVOT site depth behind the most anterior
  epicardial point and behind the anterior skin (skin points within 15 mm in x and z), height vs V1 / V2, and how far
  RV myocardium reaches beyond the pulmonary-valve rim plane (the mesh keeps outflow muscle up to the valve planes,
  01_extract.py). T13 has no rib landmarks, so intercostal levels are not available.
Output: <HEART>.json in this folder; report: report.txt, septal.csv, anatomy.csv
"""

import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']


def heart_run(h):
    sys.path.insert(0, B)
    import numpy as np
    import pandas as pd
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    from scipy.spatial import cKDTree
    spec = importlib.util.spec_from_file_location('pk', os.path.join(B, '14_purkinje.py'))
    PK = importlib.util.module_from_spec(spec); spec.loader.exec_module(PK)
    OUT = os.path.join(REPO, 'data', 'biv', h)
    pts, z, phi, v = PK.load()
    ph = np.degrees(phi)
    N = len(pts)
    rd = lambda n: np.loadtxt(os.path.join(OUT, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    t_epi, t_lv, t_rv = cKDTree(pts[epi]), cKDTree(pts[lv]), cKDTree(pts[rv])
    rv_sep = rv[t_lv.query(pts[rv])[0] < t_epi.query(pts[rv])[0]]
    lv_sep = lv[t_rv.query(pts[lv])[0] < t_epi.query(pts[lv])[0]]
    net = dict(np.load(os.path.join(OUT, 'purkinje', 'network.npz')))
    e, w = PK.myo_graph(pts)
    k = PK.graph_scale()
    MT = coo_matrix((np.r_[w, w] / k, (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(N, N)).tocsr()
    L = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
    ML = coo_matrix((np.r_[L, L], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(N, N)).tocsr()
    pts_um = pts * 1e3
    stim = lambda n: np.where(np.linalg.norm(pts_um - pts_um[n], axis=1) < 1500)[0]
    out = {'heart': h, 'septal': [], 'rvot': []}
    for zz in (0.70, 0.78, 0.85):
        band = rv_sep[np.abs(z[rv_sep] - zz) < 0.02]
        pm = float(np.degrees(np.angle(np.exp(1j * phi[band]).mean())))
        dd = np.abs(z[band] - zz) * 50 + np.abs(np.angle(np.exp(1j * np.radians(ph[band] - pm)))) * 20
        s = int(band[np.argmin(dd)])
        src = {int(i): 0.0 for i in stim(s)}
        T, TP = PK.solve_combined(net, pts, src)
        Tm = dijkstra(MT, indices=list(src))  .min(0)
        opp = int(lv[t_lv.query(pts[s])[1]])
        r = {'site_node': s, 'z': round(float(z[s]), 3), 'phi_deg': round(float(ph[s]), 1),
             'septal_thickness_mm': round(float(np.linalg.norm(pts[s] - pts[opp])), 1),
             'lv_septum_first_ms_network': round(float(T[lv_sep].min()), 1), 'lv_septum_first_ms_myocardium_only': round(float(Tm[lv_sep].min()), 1),
             'lv_opposite_ms_network': round(float(T[opp]), 1), 'lv_opposite_ms_myocardium_only': round(float(Tm[opp]), 1),
             'his_ms': round(float(TP[int(net['his'])]), 1), 'first_lv_junction_ms': None}
        lvj = net['pmj'][net['kind'][net['pmj']] == 'distal_lv']
        r['first_lv_network_node_ms'] = round(float(TP[lvj].min()), 1) if len(lvj) else None
        r['route'] = 'network' if T[lv_sep].min() < Tm[lv_sep].min() - 0.5 else 'myocardium'
        out['septal'].append(r)
    sites = json.load(open(os.path.join(OUT, 'sites.json')))
    lv0 = np.where(v == 0)[0]
    for s in [x for x in sites if x['family'] == 'rvot']:
        n = int(s['node'])
        Tm = dijkstra(MT, indices=n)
        Lm = dijkstra(ML, indices=n)
        il = lv[np.argmin(Tm[lv])]; iv = lv0[np.argmin(Tm[lv0])]
        out['rvot'].append({'id': s['id'], 'z': round(float(z[n]), 3), 'to_lv_endo_ms': round(float(Tm[il]), 1),
                            'to_lv_endo_path_mm': round(float(Lm[lv].min()), 1), 'to_lv_endo_straight_mm': round(float(t_lv.query(pts[n])[0]), 1),
                            'to_v0_ms': round(float(Tm[iv]), 1), 'to_v0_path_mm': round(float(Lm[lv0].min()), 1),
                            'to_v0_straight_mm': round(float(cKDTree(pts[lv0]).query(pts[n])[0]), 1)})
    # anatomy in the torso frame
    tor = os.path.join(OUT, 'torso')
    P = pd.read_csv(os.path.join(tor, 'heart.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    skin = pd.read_csv(os.path.join(tor, 'torso_skin.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    full_el = json.load(open(os.path.join(tor, 'summary_08.json')))['electrodes']
    fp = pd.read_csv(os.path.join(tor, 'full.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    el = {k_: fp[full_el[k_]['node']] for k_ in ('V1', 'V2')}
    front = P[epi][np.argmin(P[epi][:, 1])]
    rim = P[rd('pv_rim')]; c = rim.mean(0); nrm = np.linalg.svd(rim - c)[2][-1]
    apex = P[rd('apex')].mean(0); nrm = nrm if nrm @ (apex - c) > 0 else -nrm
    rvn = np.where(v == 1)[0]
    beyond = (P[rvn] - c) @ nrm
    anat = []
    for s in [x for x in sites if x['family'] == 'rvot' and x['depth_target'] in (0.1, 0.9)]:
        x = P[int(s['node'])]
        cyl = skin[(np.abs(skin[:, 0] - x[0]) < 15) & (np.abs(skin[:, 2] - x[2]) < 15)]
        ant = cyl[np.argmin(cyl[:, 1])] if len(cyl) else None
        anat.append({'id': s['id'], 'behind_front_epi_mm': round(float(x[1] - front[1]), 1),
                     'behind_skin_mm': round(float(x[1] - ant[1]), 1) if ant is not None else None,
                     'dz_V1_mm': round(float(x[2] - el['V1'][2]), 1), 'dz_V2_mm': round(float(x[2] - el['V2'][2]), 1),
                     'below_pv_plane_mm': round(float((x - c) @ nrm), 1)})
    out['anatomy'] = anat
    out['heart_front'] = {'y_mm': round(float(front[1]), 1), 'z_mm': round(float(front[2]), 1)}
    out['skin_ahead_of_front_mm'] = None
    out['rv_muscle_beyond_pv_plane_mm_max'] = round(float(-beyond.min()), 1)
    out['pv_rim_planarity_mm_rms'] = round(float(np.sqrt(np.mean(((rim - c) @ nrm) ** 2))), 2)
    json.dump(out, open(os.path.join(HERE, f'{h}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


def report():
    import pandas as pd
    D = {h: json.load(open(os.path.join(HERE, f'{h}.json'))) for h in HEARTS}
    S = pd.DataFrame([dict(heart=h, **r) for h, d in D.items() for r in d['septal']])
    R = pd.DataFrame([dict(heart=h, **r) for h, d in D.items() for r in d['rvot']])
    A = pd.DataFrame([dict(heart=h, **r) for h, d in D.items() for r in d['anatomy']])
    S.to_csv(os.path.join(HERE, 'septal.csv'), index=False)
    R.to_csv(os.path.join(HERE, 'rvot_paths.csv'), index=False)
    A.to_csv(os.path.join(HERE, 'anatomy.csv'), index=False)
    txt = (S.to_string(index=False) + '\n\n' + R.to_string(index=False) + '\n\n' + A.to_string(index=False) + '\n\n' +
           '\n'.join(f"{h}: RV muscle beyond the PV-rim plane max {d['rv_muscle_beyond_pv_plane_mm_max']} mm, rim planarity "
                     f"{d['pv_rim_planarity_mm_rms']} mm rms" for h, d in D.items()))
    open(os.path.join(HERE, 'report.txt'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        report()
    else:
        heart_run(os.environ['HEART'])
