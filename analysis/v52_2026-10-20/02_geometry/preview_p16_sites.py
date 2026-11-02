"""P16 items (1)(a), (2)(a)-(b), (2)(d), (3)(a), (5)(a)-(c), (6) and (8), read only: counts and coordinates of the built sites.

Reads the step-2 manifest (data/biv/<H>/v52/sites52.json), v5.1's sites (data/biv/<H>/sites.json), the merged and cut
meshes, the lv_endo / rv_endo surfaces, the primary network (purkinje/network_v52.npz), the v5.1 AHA labels
(analysis/v51_2026-10-15/05_aha_labels/pilot_site_labels.csv), the gate-5 position map (gate5count52.json), the 8.1 RVOT
labels (preview_p14_<H>.json) and v5.1's bias-run draw (analysis/v51_2026-10-15/08_monodomain/bias_sites51.json).
The 8.7 stimulated node set (1.5 mm ball on the cut mesh, excitable, connected to the site node) is rebuilt exactly as
sites52.py's capture() builds it, and checked against the manifest's stored counts. Nothing is written into the
manifest; no beat, no solve. Nothing is chosen: label values are matched to the six regions by the words they contain.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p16_sites.py
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402
from cut52 import adjacency                                                                 # noqa: E402
from sites52 import BALL_R, CAPTURE_MIN, RV_FAMILIES                                        # noqa: E402

V51 = os.path.join(G.REPO, 'analysis', 'v51_2026-10-15')
BINS = [0, 2, 4, 6, 10, 20, 40]
SIX = {'RVOT': ('rvot',), 'LVOT': ('lvot',), 'cusps': ('cusp',), 'summit': ('summit',),
       'free walls': ('free_wall', 'free wall'), 'septum': ('septum', 'septal')}
GATE9 = ['lv_free_wall_phi180_z0.5_d50', 'lv_free_wall_phi180_z0.5_d90', 'lv_septum_phi0_z0.5_d10', 'lv_septum_phi0_z0.5_d50',
         'lv_septum_phi0_z0.5_d90', 'rv_free_wall_q50_z0.5_d10', 'rv_free_wall_q50_z0.5_d50', 'rv_free_wall_q50_z0.5_d90']


def bins(d):
    c, _ = np.histogram(d, bins=BINS)
    return {f'{a}-{b}': int(x) for a, b, x in zip(BINS[:-1], BINS[1:], c)}


def six_of(value):
    v = str(value).lower()
    return sorted(k for k, words in SIX.items() if any(w in v for w in words))


def run(h, aha, g5, bias):
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52')
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    man = json.load(open(os.path.join(V, 'sites52.json')))
    new = man['new_sites']
    capm = {c['id']: c for c in man['capture']}
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3
    Pc = read_pts(os.path.join(V, 'biv52cut')) / 1e3; Ec, _ = read_elem(os.path.join(V, 'biv52cut'))
    dupsrc = np.load(os.path.join(V, 'cut_dup52.npy'))
    src = np.arange(len(Pc)); src[len(Pm):] = dupsrc[len(Pm):]
    dupof = np.full(len(Pm), -1); dupof[dupsrc[len(Pm):]] = np.arange(len(Pm), len(Pc))
    fib = np.load(os.path.join(V, 'fibrous_nodes52.npy'))
    nonex = np.zeros(len(Pc), bool); nonex[fib] = True; nonex[dupof[fib][dupof[fib] >= 0]] = True
    A = adjacency(Ec, len(Pc)); tc = cKDTree(Pc)
    S = os.path.join(V, 'surfaces')
    lv_endo, rv_endo = set(read_vtx(os.path.join(S, 'lv_endo.vtx')).tolist()), set(read_vtx(os.path.join(S, 'rv_endo.vtx')).tolist())
    lv_tri = np.loadtxt(os.path.join(S, 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    rv_tri = np.loadtxt(os.path.join(S, 'rv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    net = dict(np.load(os.path.join(V, 'purkinje', 'network_v52.npz')))
    kind = net['kind'].astype(str); nodes = net['nodes'].astype(np.int64).copy()
    rvn = (kind == 'distal_rv') & (dupof[np.minimum(nodes, len(Pm) - 1)] >= 0) & (nodes < len(Pm))
    nodes[rvn] = dupof[nodes[rvn]]                                  # as heart52.py couples them
    pmj_cut = set(nodes[net['pmj']].tolist())

    def stim(node, fam):
        n = int(node)
        if fam in RV_FAMILIES and dupof[n] >= 0:
            n = int(dupof[n])
        ball = np.array(tc.query_ball_point(Pc[n], BALL_R - 1e-9))
        ex = ball[~nonex[ball]]
        if n not in set(ex.tolist()):
            return np.array([], np.int64)
        _, lb = connected_components(A[ex][:, ex], directed=False)
        return ex[lb == lb[np.where(ex == n)[0][0]]]

    allsites = [dict(s, set='v51') for s in v51] + [dict(s, set='v52_new') for s in new]
    rows, mismatch = [], []
    for s in allsites:
        fam = s.get('parent_family', s['family'])
        st = stim(s['node'], fam)
        if len(st) != capm[s['id']]['stimulated']:
            mismatch.append(s['id'])
        m = set(src[st].tolist())
        if s['family'] in ('displaced_transmural', 'displaced_tangential'):
            dep = next(x['depth_target'] for x in v51 if x['id'] == s['parent'])
        else:
            dep = s.get('depth_target')
        rows.append({'id': s['id'], 'family': s['family'], 'depth': dep, 'n_stim': int(len(st)), 'valid': bool(len(st) >= CAPTURE_MIN),
                     'lv_endo_nodes': len(m & lv_endo), 'rv_endo_nodes': len(m & rv_endo),
                     'pmj_coupling_nodes': len(set(st.tolist()) & pmj_cut)})
    out = {'heart': h, 'stimulated_sets_rebuilt': len(rows), 'differ_from_manifest_counts': mismatch}

    # (5)(b), (5)(c): per family and depth label
    tab = defaultdict(lambda: {'sites': 0, 'with_lv_or_rv_endo': 0, 'with_lv_endo': 0, 'with_rv_endo': 0, 'with_pmj_coupling_node': 0})
    for r in rows:
        k = f"{'v51_paced' if r['id'] in {x['id'] for x in v51} else r['family']} | depth {r['depth']}"
        t = tab[k]; t['sites'] += 1
        t['with_lv_or_rv_endo'] += int(r['lv_endo_nodes'] + r['rv_endo_nodes'] > 0)
        t['with_lv_endo'] += int(r['lv_endo_nodes'] > 0); t['with_rv_endo'] += int(r['rv_endo_nodes'] > 0)
        t['with_pmj_coupling_node'] += int(r['pmj_coupling_nodes'] > 0)
    out['5b_5c_by_family_and_depth'] = dict(sorted(tab.items()))
    out['5c_network'] = {'pmj': int(len(net['pmj'])), 'distinct_coupling_nodes_on_cut_mesh': len(pmj_cut),
                         'rv_pmjs_moved_to_cut_copies (as heart52)': int(rvn[net['pmj']].sum())}

    # (5)(a): surfaces
    def area(tri):
        a, b, c = Pm[tri[:, 0]], Pm[tri[:, 1]], Pm[tri[:, 2]]
        return 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    lt, rt = cKDTree(Pm[sorted(lv_endo)]), cKDTree(Pm[sorted(rv_endo)])
    sep = [s for s in v51 if s['family'] == 'lv_septum']
    out['5a_surfaces'] = {'lv_endo': {'triangles': int(len(lv_tri)), 'nodes': len(lv_endo), 'area_mm2': round(float(area(lv_tri).sum()), 1)},
                          'rv_endo': {'triangles': int(len(rv_tri)), 'nodes': len(rv_endo), 'area_mm2': round(float(area(rv_tri).sum()), 1)},
                          'nodes_on_both': len(lv_endo & rv_endo),
                          'lv_septum_sites_dist_to_lv_endo_mm (median, max)': [round(float(np.median(lt.query(Pm[[s['node'] for s in sep]])[0])), 2),
                                                                                round(float(lt.query(Pm[[s['node'] for s in sep]])[0].max()), 2)],
                          'lv_septum_sites_dist_to_rv_endo_mm (median, max)': [round(float(np.median(rt.query(Pm[[s['node'] for s in sep]])[0])), 2),
                                                                                round(float(rt.query(Pm[[s['node'] for s in sep]])[0].max()), 2)]}

    # (2)(a), (2)(b): sets, stored fields, pair distances
    fams = Counter(s['family'] for s in new)
    out['2a_sets'] = {'v51_paced': 144, **dict(fams)}
    out['2a_fields_stored'] = {f: sorted(set().union(*[set(s.keys()) for s in new if s['family'] == f])) for f in fams}
    out['2a_fields_stored']['v51_paced (data/biv/<H>/sites.json)'] = sorted(v51[0].keys())
    X51 = Pm[[s['node'] for s in v51]]
    d51 = pdist(X51)
    out['2b_i_among_144'] = bins(d51)
    nn = cKDTree(X51).query(X51, k=2)[0][:, 1]
    out['2b_nn_144_mm'] = {'median': round(float(np.median(nn)), 2), 'smallest': round(float(nn.min()), 2)}
    own = [float(np.linalg.norm(Pm[s['node']] - Pm[next(x['node'] for x in v51 if x['id'] == s['parent'])]))
           for s in new if s['family'].startswith('displaced')]
    out['2b_ii_site_to_own_displaced'] = {'pairs': len(own), **bins(own)}
    Xall = Pm[[s['node'] for s in allsites]]
    out['2b_iii_all_built_sets'] = {'points': int(len(Xall)), **bins(pdist(Xall))}

    # (2)(d): labels per v5.1 site
    g5row = {}
    for r in g5['rows']:
        if r['heart'] == h:
            for k in ('site_90', 'site_10'):
                if r.get(k):
                    g5row[r[k]] = r['region_11.3']
    p14 = json.load(open(os.path.join(HERE, f'preview_p14_{h}.json')))
    l81 = {x['id']: x['8.1_label (D14)'] for x in next(v for k, v in p14.items() if k.startswith('3_sites'))}
    labels = {}
    for s in v51:
        a = aha.get((h, s['id']), {})
        labels[s['id']] = {'family': s['family'], 'name': s['name'], 'bazan_region': s.get('bazan_region'), 'bazan_region_v1': s.get('bazan_region_v1'),
                           'region_study': s.get('region_study'), 'aha_segment': a.get('aha_segment'), 'aha_number': a.get('aha_number'),
                           'gate5_region_11.3': g5row.get(s['id'], 'no region (not a gate-5 pool site)'), '8.1_label': l81.get(s['id'])}
    out['2d_labels_by_site'] = labels
    schemes = ['family', 'name', 'bazan_region', 'bazan_region_v1', 'region_study', 'aha_segment', 'gate5_region_11.3', '8.1_label']
    stating = {sc: {} for sc in schemes}
    six = {k: set() for k in SIX}
    per_site = defaultdict(set)
    for sid, lab in labels.items():
        for sc in schemes:
            v = lab[sc]
            if v is None:
                continue
            r6 = six_of(v)
            if r6:
                stating[sc].setdefault(str(v), r6)
            for k in r6:
                six[k].add(sid); per_site[sid].add(k)
    out['2d_label_values_stating_a_region'] = stating
    out['2d_six_regions'] = {k: {'count': len(v), 'ids': sorted(v)} for k, v in six.items()}
    out['2d_more_than_one'] = {s: sorted(r) for s, r in sorted(per_site.items()) if len(r) > 1}
    out['2d_none'] = sorted(set(labels) - set(per_site))

    # (6): regions the 9 gate-9 sites leave uncovered, per scheme (the template site is not a v5.1 site: no stored labels)
    unc = {}
    for sc in schemes + ['six_regions']:
        vals = (lambda sid: sorted(per_site.get(sid, []))) if sc == 'six_regions' else (lambda sid, sc=sc: [labels[sid][sc]])
        allv = Counter(v for sid in labels for v in vals(sid) if v is not None)
        cov = {v for sid in GATE9 for v in vals(sid)}
        unc[sc] = {str(v): {'candidates_v51_paced_in_ledger': sorted(sid for sid in labels if v in vals(sid))}
                   for v in sorted(allv, key=str) if v not in cov}
        for v in unc[sc]:
            unc[sc][v]['count'] = len(unc[sc][v]['candidates_v51_paced_in_ledger'])
    out['6_uncovered'] = {sc: {v: d['count'] for v, d in u.items()} for sc, u in unc.items()}
    out['6_uncovered_candidates'] = unc
    out['6_bias_sites51'] = bias['hearts'][h]
    out['8_gate9_v51_sites_present'] = {s: s in labels for s in GATE9}

    # (1)(a), (3)(a)
    out['1a_lv_free_wall_50pct'] = [{'id': s['id'], 'phi_deg': round(s['phi_deg'], 2), 'z': round(s['z'], 4), 'level_z': s['level_z'], 'position': s['position'],
                                     'depth_target': s['depth_target'], 'depth_achieved': s['depth_achieved'], 'labels': labels[s['id']],
                                     'gate5_pool_site': s['id'] in g5row, 'gate9_site': s['id'] in GATE9}
                                    for s in v51 if s['family'] == 'lv_free_wall' and s['depth_target'] == 0.5]
    out['3a_focus_node'] = next(s['node'] for s in new if s['family'] == 'intramural_focus')
    out['site_rows'] = rows
    G.dump(out, os.path.join(HERE, f'preview_p16_sites_{h}.json'))
    print(h, 'mismatch', len(mismatch), 'pairs', out['2b_i_among_144'], 'nn', out['2b_nn_144_mm'], flush=True)


if __name__ == '__main__':
    aha = {}
    with open(os.path.join(V51, '05_aha_labels', 'pilot_site_labels.csv')) as fh:
        for r in csv.DictReader(fh):
            aha[(r['heart'], r['site'])] = r
    g5 = json.load(open(os.path.join(HERE, 'gate5count52.json')))
    bias = json.load(open(os.path.join(V51, '08_monodomain', 'bias_sites51.json')))
    for h in sys.argv[1:] or G.HEARTS:
        run(h, aha, g5, bias)
