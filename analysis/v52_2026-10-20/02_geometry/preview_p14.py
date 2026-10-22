"""Read-only preview P14 (lock thread, relayed 22 Oct 2026 18:02 UTC) for D34 (arm A41: the RVOT network). No beat, no gate
value, nothing into the manifest, no A41 network built or saved: the existing model is counted and measured.

Set-up: the merged mesh's rv_endo surface (data/biv/<H>/v52/surfaces/rv_endo.surf, the cut52 / merge52 surfaces; the cut
moves no coordinate), the step-2g network (network_v52.npz, D21 build), the D13 PV frame (geom52.pulmonary_frame on the
full cohort mesh; heights on the PV axis, mid-plane ring at 0; theta 0 at the ring's posterior centre, D32), cut52's
landmarks (D32 reading (i): the 0 % node; h0, h100, the D14 boundary). % = (h - h0) / (h100 - h0) (P6's scale).
rv_endo distance: Dijkstra over rv_endo nodes joined to their neighbours and their neighbours' neighbours by straight
chords (D23's 2-ring surface graph, step0_report34.Surf). RV PMJs = network junctions of kind distal_rv; a point is put on
rv_endo by its nearest rv_endo node (straight line).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p14.py
"""
import importlib.util
import json
import os
import sys

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import sheet52 as SH                                                                        # noqa: E402
from common import read_pts, read_vtx                                                       # noqa: E402

R34 = SH.R34
DENS = {'Y5HYEDL4': 7.6, '6G8DD8S5': 9.6, '7D98EVAR': 8.8}
P73 = {'Y5HYEDL4': 73.0, '6G8DD8S5': 73.5, '7D98EVAR': 74.0}
spec = importlib.util.spec_from_file_location('heart51', os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build', 'heart51.py'))
sys.path.insert(0, os.path.join(G.REPO, 'analysis', 'v51_2026-10-15', '04_build'))
H51 = importlib.util.module_from_spec(spec); spec.loader.exec_module(H51)


def tri_area(P, T):
    return 0.5 * np.linalg.norm(np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]), axis=1)


def stats(x):
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    return {'median': round(float(np.median(x)), 2), 'p90': round(float(np.percentile(x, 90)), 2), 'max': round(float(x.max()), 2)} if len(x) else None


def run(h):
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); S = os.path.join(V, 'surfaces')
    P = read_pts(os.path.join(V, 'biv52')) / 1e3
    Pf, Ef, tf = G.load_full(h)
    pv, _ = G.pulmonary_frame(Pf, Ef, tf)
    L = json.load(open(os.path.join(HERE, f'cut52_{h}.json')))['landmarks']
    h0, h100, hb = L['height_0pct_mm'], L['height_100pct_mm'], L['split_height_mm']
    pct = lambda x: 100 * (np.asarray(x) - h0) / (h100 - h0)
    h73 = h0 + P73[h] / 100 * (h100 - h0)
    tri = np.loadtxt(os.path.join(S, 'rv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    SF = R34.Surf(P, tri)
    rn = SF.nodes; hn = pv.h(P[rn]); th = pv.theta(P[rn])
    tc = P[tri].mean(1); htri = pv.h(tc); thtri = pv.theta(tc); atri = tri_area(P, tri) / 100.0      # cm2
    net = np.load(os.path.join(V, 'purkinje', 'network_v52.npz'))
    nodes, kind, pmj = net['nodes'], net['kind'].astype(str), net['pmj']
    rvp = nodes[pmj[kind[pmj] == 'distal_rv']]; hp = pv.h(P[rvp]); thp = pv.theta(P[rvp])
    rvd = nodes[kind == 'distal_rv']
    trn = cKDTree(P[rn])
    on = lambda X: rn[trn.query(X)[1]]
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'h0_mm': h0, 'h100_mm': h100, 'D14_boundary_mm': hb, 'h_at_%s_pct_mm' % P73[h]: round(float(h73), 3)}
    # (1)(a)-(c)
    zone_n = rn[(hn >= hb) & (hn <= 0)]
    zone_area = float(atri[(htri >= hb) & (htri <= 0)].sum())
    zone_pmj = int(((hp >= hb) & (hp <= 0)).sum())
    add = max(0, int(round(DENS[h] * zone_area)) - zone_pmj)
    rec['1a_zone'] = {'rv_endo_nodes': int(len(zone_n)), 'area_cm2': round(zone_area, 3), 'existing_RV_PMJs': zone_pmj}
    rec['1b_level_b_adds'] = {'density_per_cm2': DENS[h], 'round(density x area)': int(round(DENS[h] * zone_area)), 'adds': add}
    rec['1c_RV_PMJs_above_0pct_landmark'] = int((hp > h0).sum())
    rec['1d_step8a_plan'] = 'no step-8a plan exists yet on the PC; A19b / A20 beat lists not drawn up'
    # (2)
    t5 = np.loadtxt(os.path.join(G.REPO, 'data', 'biv', h, 'surfaces', 'rv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    P51 = np.loadtxt(os.path.join(G.REPO, 'data', 'biv', h, 'biv.pts'), skiprows=1) / 1e3
    a51 = float(tri_area(P51, t5).sum() / 100)
    lve, epi = read_vtx(os.path.join(S, 'lv_endo.vtx')), read_vtx(os.path.join(S, 'epi.vtx'))
    rv_sep = rn[cKDTree(P[lve]).query(P[rn])[0] < cKDTree(P[epi]).query(P[rn])[0]]
    dpm, dds = trn.query(P[rvp])[0], trn.query(P[rvd])[0]
    rec['2_found'] = {
        'step0_density_area': f'the whole v5.1 rv_endo surface (data/biv/{h}/surfaces/rv_endo.surf, septum included): {a51:.1f} cm2; v5.2 rv_endo (sleeve lumen added) {atri.sum():.1f} cm2',
        'rv_endo_covers': 'the whole RV cavity surface: free wall, septum and RVOT (plus, in v5.2, the sleeves\' luminal faces)',
        'rv_septal_part (rv_endo nodes nearer the LV endocardium than the epicardium), nodes / of': [int(len(rv_sep)), int(len(rn))],
        'RV_PMJs_not_on_rv_endo': int((dpm > 1e-9).sum()), 'RV_PMJ_max_distance_mm': round(float(dpm.max()), 4),
        'RV_distal_nodes_not_on_rv_endo': int((dds > 1e-9).sum()), 'RV_distal_max_distance_mm': round(float(dds.max()), 4),
        'rv_endo_area_above_0pct_cm2': round(float(atri[htri > h0].sum()), 3)}
    parts = {'0 % to boundary': (h0, hb), f'boundary to {P73[h]} %': (hb, h73), f'{P73[h]} % to ring': (h73, 0.0), 'above ring': (0.0, np.inf)}
    quads = {'q0 (-45..45, posterior)': (-45, 45), 'q90 (45..135)': (45, 135), 'q180 (135..225, anterior)': (135, 225), 'q270 (225..315)': (225, 315)}
    wrap = lambda a: (np.asarray(a) + 45) % 360 - 45
    tbl = {}
    for pn, (lo, hi) in parts.items():
        mt = (htri > lo) & (htri <= hi) if pn != '0 % to boundary' else (htri > lo) & (htri < hi)
        mp = (hp > lo) & (hp <= hi) if pn != '0 % to boundary' else (hp > lo) & (hp < hi)
        row = {'RV_PMJs': int(mp.sum()), 'area_cm2': round(float(atri[mt].sum()), 3), 'by_quadrant': {}}
        for qn, (a0, a1) in quads.items():
            qt = (wrap(thtri) >= a0) & (wrap(thtri) < a1); qp = (wrap(thp) >= a0) & (wrap(thp) < a1)
            row['by_quadrant'][qn] = {'RV_PMJs': int((mp & qp).sum()), 'area_cm2': round(float(atri[mt & qt].sum()), 3)}
        tbl[pn] = row
    rec['2_parts (heights: (lo, hi], first part (h0, boundary))'] = tbl
    dall, _ = SF.dist(on(P[rvp]), 2)
    below = rvp[hp <= h0]
    dbel, _ = SF.dist(on(P[below]), 2) if len(below) else (np.full(len(rn), np.inf), None)
    zi = SF.ids(zone_n)
    rec['2_zone_rv_endo_distance_to_nearest_RV_PMJ_mm'] = {'all_PMJs': stats(dall[zi]), 'without_PMJs_above_0pct': stats(dbel[zi])}
    # (3) sites
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    new = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
    cand = {k: v for k, v in L['candidates'].items()}
    hD6 = cand['D6 12.7 mm above 0 %']['height_above_pv_mid_plane_mm']; h373 = cand['07:30 rule 37.3 % of the span']['height_above_pv_mid_plane_mm']
    upper = rn[hn >= hb]; lower = rn[hn < hb]
    dup, _ = SF.dist(upper, 2); dlo, _ = SF.dist(lower, 2)
    sites = [s for s in v51 if s['family'] == 'rvot'] + [s for s in new if s['family'] == 'supravalvar']
    out = []
    for s in sites:
        n = int(s['node']); x = P[n]; hh = float(pv.h(x)[0]); j = SF.ids([on(x[None])[0]])[0]
        out.append({'id': s['id'], 'family': s['family'], 'depth': s.get('depth_target'), 'height_mm': round(hh, 2), 'pct': round(float(pct(hh)), 1),
                    '8.1_label (D14)': 'free-standing infundibulum' if hh >= hb else 'septal component',
                    'beside: D6 12.7 mm / 07:30 37.3 %': ['free' if hh >= hD6 else 'septal', 'free' if hh >= h373 else 'septal'],
                    'above_0pct': bool(hh > h0), 'above_boundary': bool(hh >= hb),
                    'rv_endo_mm_to_nearest_RV_PMJ': round(float(dall[j]), 2), 'rv_endo_mm_to_nearest_RV_PMJ_below_0pct': round(float(dbel[j]), 2),
                    'rv_endo_mm_to_D14_boundary (0 if on the far side)': round(float(dup[j] if hh < hb else dlo[j]), 2)})
    rec['3_sites (v5.1 RVOT family = gate 3 RVOT in Y5HYEDL4; supravalvar)'] = out
    # (4) gate-4, gate-9, gate-8 sites above h0 / in the zone
    allsites = [(s['id'], s['family'], int(s['node'])) for s in v51] + [(s['id'], s['family'], int(s['node'])) for s in new
                                                                         if s['family'] in ('cusp_crescent', 'summit_reanchored')]
    g9 = {s['id'] for s in H51_check_sites(h)}
    res4 = {'above_0pct': [], 'between_boundary_and_ring': []}
    for sid, fam, n in allsites:
        hh = float(pv.h(P[n])[0])
        tags = []
        if fam == 'rv_free_wall' and sid.endswith(('_d10', '_d90')):
            tags.append('gate-4 RV pair site')
        if sid in g9:
            tags.append('gate-9 site')
        tags.append('gate-8 family ' + fam)
        if hh > h0:
            res4['above_0pct'].append({'id': sid, 'height_mm': round(hh, 2), 'roles': tags})
        if hb <= hh <= 0:
            res4['between_boundary_and_ring'].append({'id': sid, 'height_mm': round(hh, 2), 'roles': tags})
    res4['gate8_families'] = sorted({f for _, f, _ in allsites})
    rec['4'] = res4
    # (5) network path times
    Gn = H51.net_graph(net, P).tocsr()
    M = len(nodes)
    T = dijkstra(Gn, directed=False, indices=int(net['his']))[:M]
    s14 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'purkinje', 'summary.json')))['landmarks']
    mb = np.where((nodes == s14['mb_end']) & (kind == 'proximal'))[0]
    up = pmj[(kind[pmj] == 'distal_rv')][hp >= hb]
    rec['5_network_times_ms (network graph alone; +4 ms to muscle at a junction)'] = {
        'His_to_moderator_band_free_wall_end': round(float(T[mb].min()), 2) if len(mb) else None,
        'His_to_lowest_RV_PMJ_above_boundary': round(float(T[up[np.argmin(pv.h(P[nodes[up]]))]]), 2) if len(up) else None,
        'His_to_highest_RV_PMJ_above_boundary': round(float(T[up[np.argmax(pv.h(P[nodes[up]]))]]), 2) if len(up) else None,
        'RV_PMJs_above_boundary': int(len(up))}
    # (6) quantities for the quoted rule
    zU = {u: np.loadtxt(os.path.join(G.REPO, 'data', 'biv', h, u, 'z.dat')) for u in ('uvc', 'uvc_v1') if os.path.exists(os.path.join(G.REPO, 'data', 'biv', h, u, 'z.dat'))}
    rec['6_numbers'] = {'distal_rv_nodes': int((kind == 'distal_rv').sum()), 'distal_rv_with_PMJ': int(len(rvp)),
                        'share_of_distal_rv_nodes_with_PMJ': round(len(rvp) / max(1, (kind == 'distal_rv').sum()), 3),
                        'max_UVC_z_of_distal_rv_nodes': {u: round(float(z[rvd].max()), 4) for u, z in zU.items()}}
    G.dump(rec, os.path.join(HERE, f'preview_p14_{h}.json'))
    print(h, json.dumps({k: v for k, v in rec.items() if k.startswith(('1', '5'))}), flush=True)


def H51_check_sites(h):
    """The gate-9 sites as mono51.py check_sites() picks them (its 'original' LV free-wall site is a template-run node, not
    a v5.1 site id, and is listed by its node in the report text)."""
    S = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    pick = lambda fam, pos, d: next(s for s in S if s['family'] == fam and s['position'] == pos and s['level_z'] == 0.5 and int(round(s['depth_target'] * 100)) == d)
    return [pick('lv_free_wall', 'phi180', d) for d in (50, 90)] + [pick('lv_septum', 'phi0', d) for d in (10, 50, 90)] + \
           [pick('rv_free_wall', 'q50', d) for d in (10, 50, 90)]


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
