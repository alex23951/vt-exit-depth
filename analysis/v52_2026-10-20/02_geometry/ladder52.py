"""v5.2 step 2e addition under D36 (g) and (h2): report 7's resolution ladder (all three hearts) and the control heart's
2.5 mm stimulated node sets ("stim25"). Set-up only: no beat, no solve.

D36 (g) (Alex, "Adopt all", 26 Oct 2026 22:00:57 UTC): at each of the 144 v5.1 paced sites, 8 points:
  +f (the stored fibre, as 11.2a's tangential rule and sites52.py's displaced set: column 1-3 of biv52.lon in the site
     node's element whose centroid is nearest the node) at 2, 6 and 10 mm;
  +s (the stored in-wall s, columns 4-6 of the same row: s = t_out x f where D19b's LV frame is built, v5.1's stored s,
     in its stored sense, on the RV rows v5.1 keeps; the sleeves' stored s, the pulmonary axis; the frame as built) at
     2, 4, 6 and 10 mm;
  transmural in D33's sense (the mean element gradient of D19b's APD w over the site node's elements, + where the site's
     APD w < 0.5, - where >= 0.5) at 2 mm.
Each point: a straight step from the site node, snapped to the nearest node not used by any site of the manifest (v5.1
sites, every new set sites52.py wrote, report 7's displaced points), in v5.1 site order, the steps in the order above;
whether the unsnapped point lies in a tet of the merged mesh is recorded; 8.7's capture (1.5 mm ball on the cut mesh,
excitable, connected to the site node, at least 4 nodes) against the parent family; a point that fails it is recorded,
counted and excluded, never moved; muscle fraction of its ball (4,000 points, sites52.py's draw). Written to the step-2
manifest (data/biv/<H>/v52/sites52.json) as family "ladder", with their capture rows.
D36 (h2), control heart only: each v5.1 site's base node and its three 4 mm points (report 7's transmural and fibre
points, the ladder's +s 4 mm point unless 8.7's capture excluded it) get 8.7's stimulated set with a 2.5 mm ball in place
of 1.5 mm, about the node as built (nothing moves); capture counted (at least 4 nodes); the node lists (cut-mesh ids)
written to the manifest as "stim25_sets".
The manifest as sites52.py wrote it is kept once as sites52_pre_ladder.json and every run starts from it, so a re-run
gives the same file. Run this again after any re-run of sites52.py (which rewrites sites52.json without the ladder).
Also reported (P16 (2)(b)-(c), (5)(b)-(c)): achieved distance and APD w change per step, the 8.8 placement checks that
apply to ladder points (RVOT parents: height below the pulmonary valve; aortic-cusp parents: distance to the PV rim),
endocardial and PMJ contacts of each stimulated set, and the pair-distance bins with the ladder.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/ladder52.py [HEART ...]
"""
import json
import os
import shutil
import sys
import time
from collections import defaultdict

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q12                                                                  # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402
from cut52 import adjacency                                                                 # noqa: E402
from sites52 import BALL_R, CAPTURE_MIN, RV_FAMILIES                                        # noqa: E402

CONTROL = 'Y5HYEDL4'
STEPS = (('f', 2.0), ('f', 6.0), ('f', 10.0), ('s', 2.0), ('s', 4.0), ('s', 6.0), ('s', 10.0), ('tm', 2.0))
STEP_NAME = {'f': 'fibre (+f)', 's': 'cross-fibre (+s)', 'tm': 'transmural (D33)'}
R25 = 2.5
BINS = [0, 2, 4, 6, 10, 20, 40]


def bins(d):
    c, _ = np.histogram(d, bins=BINS)
    return {f'{a}-{b}': int(x) for a, b, x in zip(BINS[:-1], BINS[1:], c)}


def angle(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))


def run(h):
    t0 = time.time()
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); F52 = os.path.join(V, 'fields52'); S = os.path.join(V, 'surfaces')
    man_f, pre_f = os.path.join(V, 'sites52.json'), os.path.join(V, 'sites52_pre_ladder.json')
    if not os.path.exists(pre_f):
        man0 = json.load(open(man_f))
        assert not any(s['family'] == 'ladder' for s in man0['new_sites']) and 'stim25_sets' not in man0, 'manifest already holds the ladder'
        shutil.copy2(man_f, pre_f)
    man = json.load(open(pre_f))
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'pre_ladder_manifest': {'path': os.path.relpath(pre_f, G.REPO), 'sha256': G.sha256(pre_f)}}
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    new = man['new_sites']
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3; Em, tm = read_elem(os.path.join(V, 'biv52'))
    wapd = np.load(os.path.join(F52, 'w_apd.npy'))
    lonv = np.loadtxt(os.path.join(V, 'biv52.lon'), skiprows=1)
    eonm = coo_matrix((np.ones(Em.size), (Em.ravel(), np.repeat(np.arange(len(Em)), 4))), shape=(len(Pm), len(Em))).tocsr()
    cen = Pm[Em].mean(1); tree_e = cKDTree(cen); tree_m = cKDTree(Pm)
    x0 = Pm[Em[:, 0]]; J = np.stack([Pm[Em[:, 1]] - x0, Pm[Em[:, 2]] - x0, Pm[Em[:, 3]] - x0], axis=2)
    print(h, 'meshes read', round(time.time() - t0, 1), 's', flush=True)

    def in_mesh(x):
        nb = tree_e.query(x, k=24)[1]
        lam = np.linalg.solve(J[nb], (x - x0[nb])[..., None])[..., 0]
        return bool(((lam >= -1e-9).all(-1) & (lam.sum(-1) <= 1 + 1e-9)).any())

    # sites52.py's muscle-fraction draw (same seed); scaled for the 2.5 mm ball
    rng = np.random.default_rng(0)
    U = rng.normal(size=(4000, 3)); U /= np.linalg.norm(U, axis=1, keepdims=True); U *= BALL_R * rng.random(4000)[:, None] ** (1 / 3)

    def inside_frac(c, r=BALL_R):
        pts = c + U * (r / BALL_R)
        _, nb = tree_e.query(pts, k=24)
        lam = np.linalg.solve(J[nb], (pts[:, None, :] - x0[nb])[..., None])[..., 0]
        return float(((lam >= -1e-9).all(-1) & (lam.sum(-1) <= 1 + 1e-9)).any(1).mean())

    # ---------------- the ladder (D36 (g))
    disp = {(s['parent'], s['family']): s for s in new if s['family'].startswith('displaced')}
    used = {int(s['node']) for s in v51} | {int(s['node']) for s in new}
    lad, dchk = [], []
    for sv in v51:
        n0 = int(sv['node']); ee = eonm.indices[eonm.indptr[n0]:eonm.indptr[n0 + 1]]
        gw = Q12.FF.elem_grad(Pm, Em[ee], wapd).mean(0)
        sense = 1.0 if wapd[n0] < 0.5 else -1.0
        en = ee[np.argmin(np.linalg.norm(cen[ee] - Pm[n0], axis=1))]
        dirs = {'tm': sense * gw / max(np.linalg.norm(gw), 1e-30),
                'f': lonv[en, :3] / np.linalg.norm(lonv[en, :3]), 's': lonv[en, 3:6] / np.linalg.norm(lonv[en, 3:6])}
        dchk.append({'id': sv['id'], 'element': int(en), 'element_tag': int(tm[en]),
                     'angle_to_report7_transmural_deg': angle(dirs['tm'], disp[(sv['id'], 'displaced_transmural')]['direction']),
                     'angle_to_report7_fibre_deg': angle(dirs['f'], disp[(sv['id'], 'displaced_tangential')]['direction']),
                     'f_dot_s': float(dirs['f'] @ dirs['s']), 's_dot_grad_w': float(dirs['s'] @ gw / max(np.linalg.norm(gw), 1e-30))})
        for k, L in STEPS:
            x = Pm[n0] + L * dirs[k]
            cand = tree_m.query(x, k=256)[1]
            node = next(int(c) for c in cand if int(c) not in used)
            used.add(node)
            ent = {'id': f"{sv['id']}_lad_{k}{int(L)}", 'family': 'ladder', 'parent': sv['id'], 'parent_family': sv['family'],
                   'parent_depth_target': sv['depth_target'], 'step': STEP_NAME[k], 'nominal_mm': L,
                   'direction': [round(float(c), 5) for c in dirs[k]], 'node': node,
                   'xyz_mm': [round(float(c), 4) for c in Pm[node]], 'unsnapped_xyz_mm': [round(float(c), 4) for c in x],
                   'point_inside_myocardium': in_mesh(x), 'snap_mm': round(float(np.linalg.norm(Pm[node] - x)), 3),
                   'moved_mm': round(float(np.linalg.norm(Pm[node] - Pm[n0])), 3),
                   'site_w_apd': round(float(wapd[n0]), 4), 'node_w_apd': round(float(wapd[node]), 4),
                   'd_w_apd': round(float(wapd[node] - wapd[n0]), 4)}
            if k == 'tm':
                ent['sense (D33)'] = int(sense)
            lad.append(ent)
    print(h, 'ladder points placed', len(lad), round(time.time() - t0, 1), 's', flush=True)
    rec['direction_checks'] = {
        'max_angle_to_report7_transmural_deg': round(max(c['angle_to_report7_transmural_deg'] for c in dchk), 4),
        'max_angle_to_report7_fibre_deg': round(max(c['angle_to_report7_fibre_deg'] for c in dchk), 4),
        'max_|f.s|': round(max(abs(c['f_dot_s']) for c in dchk), 5),
        '|s.unit(grad w)| (median, max)': [round(float(np.median([abs(c['s_dot_grad_w']) for c in dchk])), 4), round(max(abs(c['s_dot_grad_w']) for c in dchk), 4)],
        'sites_on_RV_side_rows (element tag in RV group)': sum(c['element_tag'] in G.RV_GROUP for c in dchk), 'per_site': dchk}

    # ---------------- 8.7 capture on the cut mesh
    Pc = read_pts(os.path.join(V, 'biv52cut')) / 1e3; Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    dupsrc = np.load(os.path.join(V, 'cut_dup52.npy'))
    src = np.arange(len(Pc)); src[len(Pm):] = dupsrc[len(Pm):]
    dupof = np.full(len(Pm), -1); dupof[dupsrc[len(Pm):]] = np.arange(len(Pm), len(Pc))
    fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
    nonex = np.zeros(len(Pc), bool); nonex[fib] = True; nonex[dupof[fib][dupof[fib] >= 0]] = True
    A = adjacency(Ec, len(Pc)); tc = cKDTree(Pc)

    def capture(node, fam, r=BALL_R):
        n = int(node)
        if fam in RV_FAMILIES and dupof[n] >= 0:
            n = int(dupof[n])
        ball = np.array(tc.query_ball_point(Pc[n], r - 1e-9))
        ex = ball[~nonex[ball]]
        if n not in set(ex.tolist()):
            return np.array([], np.int64), {'cut_node': n, 'ball_nodes': len(ball), 'stimulated': 0, 'valid': False, 'note': 'site node not excitable'}
        _, lb = connected_components(A[ex][:, ex], directed=False)
        st = ex[lb == lb[np.where(ex == n)[0][0]]]
        return st, {'cut_node': n, 'ball_nodes': len(ball), 'stimulated': int(len(st)), 'valid': bool(len(st) >= CAPTURE_MIN),
                    'same_as_plain_ball': bool(len(st) == len(ball))}

    # endocardial surfaces and PMJ coupling nodes (as preview_p16_sites.py: RV PMJs on cut-duplicated nodes use the RV copy)
    lv_endo, rv_endo = set(read_vtx(os.path.join(S, 'lv_endo.vtx')).tolist()), set(read_vtx(os.path.join(S, 'rv_endo.vtx')).tolist())
    net = dict(np.load(os.path.join(V, 'purkinje', 'network_v52.npz')))
    kind = net['kind'].astype(str); nodes = net['nodes'].astype(np.int64).copy()
    rvn = (kind == 'distal_rv') & (dupof[np.minimum(nodes, len(Pm) - 1)] >= 0) & (nodes < len(Pm))
    nodes[rvn] = dupof[nodes[rvn]]
    pmj_cut = set(nodes[net['pmj']].tolist())

    def contacts(st):
        m = set(src[st].tolist())
        return {'lv_endo_nodes': len(m & lv_endo), 'rv_endo_nodes': len(m & rv_endo), 'pmj_coupling_nodes': len(set(st.tolist()) & pmj_cut)}

    cap, stim15 = [], {}
    for p in lad:
        st, c = capture(p['node'], p['parent_family'])
        stim15[p['id']] = st
        c['muscle_fraction'] = round(inside_frac(Pm[p['node']]), 3)
        cap.append({'id': p['id'], 'family': 'ladder', 'set': 'v52_ladder', 'node': p['node'], **c, **contacts(st)})
    capd = {c['id']: c for c in cap}
    print(h, 'ladder capture done', round(time.time() - t0, 1), 's', flush=True)

    # ---------------- report: per step (P16 (2)(c)), by parent depth, sides, 8.8
    def summ(ps):
        mv = np.array([p['moved_mm'] for p in ps]); dw = np.array([p['d_w_apd'] for p in ps])
        return {'n': len(ps), 'achieved_mm (median, smallest, largest)': [round(float(np.median(mv)), 2), round(float(mv.min()), 2), round(float(mv.max()), 2)],
                'd_APD_w (median, largest |change|)': [round(float(np.median(dw)), 4), round(float(dw[np.argmax(np.abs(dw))]), 4)],
                'median_|d_APD_w|': round(float(np.median(np.abs(dw))), 4),
                'excluded_by_8.7_capture': sum(not capd[p['id']]['valid'] for p in ps),
                'unsnapped_point_left_myocardium': sum(not p['point_inside_myocardium'] for p in ps),
                'snap_mm (median, largest)': [round(float(np.median([p['snap_mm'] for p in ps])), 3), round(float(max(p['snap_mm'] for p in ps)), 3)]}
    steps = {f'{STEP_NAME[k]} {int(L)} mm': [p for p in lad if p['step'] == STEP_NAME[k] and p['nominal_mm'] == L] for k, L in STEPS}
    rec['per_step'] = {nm: summ(ps) for nm, ps in steps.items()}
    rec['per_step_and_parent_depth'] = {nm: {str(d): summ([p for p in ps if p['parent_depth_target'] == d]) for d in (0.1, 0.5, 0.75, 0.9)}
                                        for nm, ps in steps.items()}
    rec['per_step_and_parent_family'] = {nm: {fam: summ([p for p in ps if p['parent_family'] == fam]) for fam in sorted({p['parent_family'] for p in ps})}
                                         for nm, ps in steps.items()}
    rec['excluded_points'] = [{'id': c['id'], 'stimulated': c['stimulated'], 'note': c.get('note')} for c in cap if not c['valid']]
    elem_tags = defaultdict(set)
    for e in np.unique(np.concatenate([eonm.indices[eonm.indptr[p['node']]:eonm.indptr[p['node'] + 1]] for p in lad])):
        for n in Em[e]:
            elem_tags[int(n)].add(int(tm[e]))
    def side(fam):
        return set(G.RV_GROUP) if fam in RV_FAMILIES else set(G.LV_GROUP)
    other = [p['id'] for p in lad if not (elem_tags[p['node']] & side(p['parent_family']))]
    rec['snapped_node_touches_no_element_of_parent_side'] = {'count': len(other), 'ids': other}
    mf = np.array([c['muscle_fraction'] for c in cap])
    rec['muscle_fraction (median, p10, smallest)'] = [round(float(np.median(mf)), 3), round(float(np.percentile(mf, 10)), 3), round(float(mf.min()), 3)]
    P, E, tag = G.load_full(h)
    pv, _ = G.pulmonary_frame(P, E, tag)
    tpv = cKDTree(Pm[read_vtx(os.path.join(S, 'pv_rim.vtx'))])
    rv_lad = [p for p in lad if p['parent_family'] == 'rvot']
    below = {p['id']: round(float(-pv.h(Pm[p['node']][None])[0]), 2) for p in rv_lad}
    rec['8.8'] = {'RVOT-parent ladder points below the PV, mm (8.8: every RVOT origin within the first 10 mm below the PV)': below,
                  'RVOT-parent ladder points outside 0-10 mm below the PV': sorted(k for k, v in below.items() if not 0 <= v <= 10),
                  'aortic-cusp-parent ladder points to the PV rim, mm (8.8: PV-LCC 5 +- 3, PV-RCC 11 +- 5)':
                      {p['id']: round(float(tpv.query(Pm[p['node']])[0]), 2) for p in lad if p['parent_family'] == 'aortic_cusp'},
                  'not applicable to ladder points': 'LVOT breakout, outflow connections, LCC-GCV spacing, two apicobasal levels and nearest-sleeve checks place '
                                                     'site families, not steps from a site; none is a ladder rule'}
    del P, E, tag

    # ---------------- (h2): 2.5 mm stimulated sets, control heart only
    st25 = []
    if h == CONTROL:
        cap0 = {c['id']: c for c in man['capture']}
        for sv in v51:
            members = [('base', sv['id'], int(sv['node'])),
                       ('transmural 4 mm (report 7)', f"{sv['id']}_disp_tm", int(disp[(sv['id'], 'displaced_transmural')]['node'])),
                       ('fibre 4 mm (report 7)', f"{sv['id']}_disp_tg", int(disp[(sv['id'], 'displaced_tangential')]['node'])),
                       ('cross-fibre 4 mm (ladder)', f"{sv['id']}_lad_s4", next(p['node'] for p in lad if p['id'] == f"{sv['id']}_lad_s4"))]
            for role, pid, node in members:
                c15 = capd[pid] if role.startswith('cross') else cap0[pid]
                ent = {'id': f'{pid}_stim25', 'family': 'stim25', 'site': sv['id'], 'site_family': sv['family'], 'role': role, 'point_id': pid,
                       'node': node, 'radius_mm': R25, 'stimulated_1.5mm': c15['stimulated'], 'valid_1.5mm': c15['valid']}
                if not c15['valid']:
                    ent.update({'built': False, 'note': "excluded: the point failed 8.7's 1.5 mm capture (D36 (g)), so it has no stim25 beat"})
                    st25.append(ent); continue
                st, c = capture(node, sv['family'], R25)
                s15 = stim15[pid] if role.startswith('cross') else capture(node, sv['family'])[0]
                ent.update({'built': True, **c, 'muscle_fraction_2.5mm': round(inside_frac(Pm[node], R25), 3),
                            'contains_the_1.5mm_set': bool(set(s15.tolist()) <= set(st.tolist())), **contacts(st),
                            'stimulated_cut_nodes': [int(x) for x in np.sort(st)]})
                st25.append(ent)
        b = [x for x in st25 if x['built']]
        n25 = np.array([x['stimulated'] for x in b]); n15 = np.array([x['stimulated_1.5mm'] for x in b])
        rec['stim25'] = {'sets': len(st25), 'built': len(b), 'excluded_before_build (1.5 mm capture failed)': [x['id'] for x in st25 if not x['built']],
                         'invalid_at_2.5mm': [x['id'] for x in b if not x['valid']],
                         'stimulated_nodes_2.5mm (median, smallest, largest)': [float(np.median(n25)), int(n25.min()), int(n25.max())],
                         'stimulated_nodes_1.5mm (median)': float(np.median(n15)), 'ratio_2.5_to_1.5 (median)': round(float(np.median(n25 / n15)), 2),
                         'sets_not_containing_their_1.5mm_set': [x['id'] for x in b if not x['contains_the_1.5mm_set']],
                         'sets_smaller_than_the_plain_2.5mm_ball': sum(not x['same_as_plain_ball'] for x in b),
                         'muscle_fraction_2.5mm (median, p10, smallest)': [round(float(np.median([x['muscle_fraction_2.5mm'] for x in b])), 3),
                                                                           round(float(np.percentile([x['muscle_fraction_2.5mm'] for x in b], 10)), 3),
                                                                           round(float(min(x['muscle_fraction_2.5mm'] for x in b)), 3)],
                         'by_role': {r: {'built': sum(x['built'] for x in st25 if x['role'] == r), 'valid': sum(x.get('valid', False) for x in st25 if x['role'] == r)}
                                     for r in sorted({x['role'] for x in st25})}}
        print(h, 'stim25 sets', len(st25), round(time.time() - t0, 1), 's', flush=True)

    # ---------------- P16 (5)(b)-(c) for the ladder and stim25, by step / role and parent depth
    tab = defaultdict(lambda: {'sets': 0, 'with_lv_or_rv_endo': 0, 'with_lv_endo': 0, 'with_rv_endo': 0, 'with_pmj_coupling_node': 0})
    def add(key, c):
        t = tab[key]; t['sets'] += 1
        t['with_lv_or_rv_endo'] += int(c['lv_endo_nodes'] + c['rv_endo_nodes'] > 0)
        t['with_lv_endo'] += int(c['lv_endo_nodes'] > 0); t['with_rv_endo'] += int(c['rv_endo_nodes'] > 0)
        t['with_pmj_coupling_node'] += int(c['pmj_coupling_nodes'] > 0)
    for p in lad:
        add(f"ladder {p['step']} {int(p['nominal_mm'])} mm | parent depth {p['parent_depth_target']}", capd[p['id']])
    dep = {s['id']: s['depth_target'] for s in v51}
    for x in st25:
        if x['built']:
            add(f"stim25 {x['role']} | site depth {dep[x['site']]}", x)
    rec['5b_5c'] = dict(sorted(tab.items()))

    # ---------------- P16 (2)(b) with the ladder (coordinates of snapped nodes)
    par = {s['id']: int(s['node']) for s in v51}
    own = [float(np.linalg.norm(Pm[s['node']] - Pm[par[s['parent']]])) for s in new + lad if s['family'].startswith('displaced') or s['family'] == 'ladder']
    rec['2b_ii_site_to_own_displaced_and_ladder'] = {'pairs': len(own), **bins(own)}
    allx = Pm[[int(s['node']) for s in v51] + [int(s['node']) for s in new] + [p['node'] for p in lad]]
    rec['2b_iii_all_built_sets_with_ladder'] = {'points': int(len(allx)), **bins(pdist(allx))}

    # ---------------- write the manifest
    man['new_sites'] = new + lad
    man['capture'] = man['capture'] + cap
    man['ladder (D36 g)'] = {'rule': 'D36 (g): +f 2/6/10 mm, +s 2/4/6/10 mm, transmural (D33) 2 mm; straight step from the site node, nearest unused node in v5.1 '
                                     'site order after report 7; 8.7 capture against the parent family, failures kept, counted and excluded',
                             'points': len(lad), 'excluded_by_capture': len(rec['excluded_points']), 'script': os.path.relpath(__file__, G.REPO),
                             'pre_ladder_manifest_sha256': rec['pre_ladder_manifest']['sha256']}
    if st25:
        man['stim25_sets'] = st25
        man['stim25 (D36 h2)'] = {'rule': "D36 (h2): 8.7's stimulated set with a 2.5 mm ball about the node as built; base, report 7's 4 mm transmural and "
                                          "fibre points, the ladder's +s 4 mm point; capture counted (at least 4 nodes); node ids are biv52cut ids",
                                  'sets': len(st25), 'built': rec['stim25']['built'], 'radius_mm': R25}
    G.dump(man, man_f)
    rec['manifest'] = {'path': os.path.relpath(man_f, G.REPO), 'sha256': G.sha256(man_f)}
    rec['counts'] = {'ladder_points': len(lad), 'ladder_excluded_by_capture': len(rec['excluded_points']),
                     'ladder_beats_at_most': len(lad) - len(rec['excluded_points']), 'stim25_sets_built': rec.get('stim25', {}).get('built', 0),
                     'stim25_beats_at_most': len([x for x in st25 if x['built'] and x['valid']])}
    rec['wall_s'] = round(time.time() - t0, 1)
    G.dump(rec, os.path.join(HERE, f'ladder52_{h}.json'))
    print(h, rec['counts'], {k: v['excluded_by_8.7_capture'] for k, v in rec['per_step'].items()}, rec['wall_s'], 's', flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
