"""v5.2 step 0, report 34: conduction geometry, read only (LOCK.md section 12 item 34; 7.1, 7.2, section 11 row 7).

Geometry only: no beat is run and no result is seen. The rules of D1-D4 are placed here blind.

Operational definitions used (mine, stated so they can be checked; none changes a lock value):
  Distances along a surface: Dijkstra on the surface's 2-ring graph (each node joined to its neighbours and their neighbours by
    straight chords); the 1-ring (edge-only) value is printed beside the key lengths, since it over-estimates a geodesic.
  Left septal surface S: LV endocardial nodes whose AHA segment (v5.1 rule, 05_aha_labels/aha51.py Frame, RV insertion
    points) is septal: 2, 3, 8, 9, 14. The local short-axis frame is evaluated at the node's height rounded to 0.1 mm.
  Septal crest: the nodes of S on the boundary of the LV endocardial surface (its edges that belong to one triangle),
    i.e. the top edge of the left septal endocardium where it meets the valve rims and the aortic and AV-plane
    interfaces. Crest-to-apex length L: surface distance from the crest to the LV endocardial apex (the lowest LV
    endocardial node along the apex -> mitral-ring axis, as aha51). D1 line: the nodes of S at distance L / 3 from the
    crest (assumption 46). Septal thirds: distance to crest / L.
  His line (the base-to-apex line through the His exit): the surface shortest path from the v5.1 His node to the LV
    endocardial apex. Sheet coordinates of a node: s = arc length along the His line of its nearest line node (surface
    distance), a = surface distance to the line, signed + anterior (UVC phi larger than at the foot point).
  Envelope (7.1, D4): width W(s) = 6 + 16.6 min(s, 12.5) / 12.5 mm for 0 <= s <= 33 mm; adopted placement 17.8 / 22.6 of W
    anterior and 4.8 / 22.6 posterior of the His line; declined placement W / 2 either side of the v5.1 footprint midpoint.
  v5.1 LV septal node footprint: v5.1 network nodes (proximal LV and distal_lv) whose mesh node lies on S; per level
    s_k (2.5 mm steps and 33 mm) the nodes with |s - s_k| <= 1.25 mm.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/00_step0/step0_report34.py [HEART ...]
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SEPTAL = {2, 3, 8, 9, 14}
ANT_FW = {1, 7, 13}            # free-wall segments next to the anterior septal boundary
INF_FW = {4, 10, 15}           # free-wall segments next to the inferior (posterior) septal boundary
W0, WMAX, WIDEN, SHEET = 6.0, 22.6, 12.5, 33.0
ANT_SHARE = 17.8 / 22.6
PATCH_R = 10.0


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


AHA = module('aha51', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '05_aha_labels', 'aha51.py'))


def rd_vtx(h, n):
    return np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'surfaces', f'{n}.vtx'), skiprows=2, dtype=np.int64, ndmin=1)


def rd_surf(h, n):
    return np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'surfaces', f'{n}.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64, ndmin=2)


class Surf:
    """Triangle surface on global node ids; graphs on local ids."""
    def __init__(self, P, tri):
        self.tri = tri
        self.nodes = np.unique(tri)
        self.loc = {int(n): i for i, n in enumerate(self.nodes)}
        self.lid = np.searchsorted(self.nodes, tri)
        self.X = P[self.nodes]
        n = len(self.nodes)
        e = np.vstack([self.lid[:, [0, 1]], self.lid[:, [1, 2]], self.lid[:, [2, 0]]])
        e = np.sort(e, axis=1)
        key, cnt = np.unique(e, axis=0, return_counts=True)
        self.e1 = key
        self.boundary_edges = key[cnt == 1]
        A = coo_matrix((np.ones(len(key)), (key[:, 0], key[:, 1])), shape=(n, n)).tocsr()
        A = A + A.T
        self.A = A
        A2 = (A @ A + A).tocoo()
        m = A2.row < A2.col
        self.e2 = np.c_[A2.row[m], A2.col[m]]
        self.G1 = self._graph(self.e1)
        self.G2 = self._graph(self.e2)

    def _graph(self, e):
        w = np.linalg.norm(self.X[e[:, 0]] - self.X[e[:, 1]], axis=1)
        n = len(self.nodes)
        return coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()

    def ids(self, glob):
        return np.searchsorted(self.nodes, glob)

    def dist(self, glob_src, ring=2, mask=None, pred=False):
        G = self.G2 if ring == 2 else self.G1
        if mask is not None:                       # keep only edges between allowed local nodes
            G = G.tocoo(); k = mask[G.row] & mask[G.col]
            G = coo_matrix((G.data[k], (G.row[k], G.col[k])), shape=G.shape).tocsr()
        src = self.ids(np.atleast_1d(glob_src))
        if pred:
            return dijkstra(G, indices=src, min_only=True, return_predecessors=True)
        d, _, s = dijkstra(G, indices=src, min_only=True, return_predecessors=True)
        return d, s

    def path(self, a, b, ring=2):
        G = self.G2 if ring == 2 else self.G1
        _, pr = dijkstra(G, indices=self.ids([a])[0], return_predecessors=True)
        j = self.ids([b])[0]; out = [j]
        while out[-1] != self.ids([a])[0]:
            out.append(pr[out[-1]])
            if out[-1] < 0:
                raise RuntimeError('no path')
        return self.nodes[np.array(out[::-1])]

    def euler(self):
        V, Ed, F = len(self.nodes), len(self.e1), len(self.tri)
        b = self.boundary_edges
        nb = len(np.unique(b))
        Gb = coo_matrix((np.ones(len(b)), (b[:, 0], b[:, 1])), shape=(V, V))
        ncomp, lab = connected_components(Gb, directed=False)
        loops = len(np.unique(lab[np.unique(b)])) if len(b) else 0
        ncs, _ = connected_components(self.A, directed=False)
        chi = V - Ed + F
        e = np.vstack([self.lid[:, [0, 1]], self.lid[:, [1, 2]], self.lid[:, [2, 0]]])
        _, cnt = np.unique(np.sort(e, axis=1), axis=0, return_counts=True)
        nm = int((cnt > 2).sum())
        return {'V': V, 'E': int(Ed), 'F': int(F), 'euler_characteristic': int(chi), 'boundary_loops': int(loops),
                'surface_components': int(ncs), 'edges_in_3_or_more_triangles (pinch edges)': nm,
                'genus': (2 * ncs - loops - chi) / 2 if nm == 0 else 'not defined: the surface is not a manifold at its pinch edges'}

    def area(self, glob_keep=None):
        t = self.tri if glob_keep is None else self.tri[np.isin(self.tri, glob_keep).all(1)]
        return float(0.5 * np.linalg.norm(np.cross(self.X[np.searchsorted(self.nodes, t[:, 1])] - self.X[np.searchsorted(self.nodes, t[:, 0])],
                                                     self.X[np.searchsorted(self.nodes, t[:, 2])] - self.X[np.searchsorted(self.nodes, t[:, 0])]), axis=1).sum())


class Labeller:
    """aha51.Frame.label with the local short-axis frame cached at heights rounded to 0.1 mm."""
    def __init__(self, F):
        self.F, self.cache = F, {}

    def loc(self, a):
        k = round(a, 1)
        if k not in self.cache:
            self.cache[k] = self.F.local(k)
        return self.cache[k]

    def label(self, X):
        F = self.F
        f = float(F.f(X)); a_mm = f * F.Lax
        if f < F.cap_f:
            return 17, np.nan
        c = F.cap_f
        level = 'apical' if f < c + (1 - c) / 3 else ('mid' if f < c + 2 * (1 - c) / 3 else 'basal')
        a_use = round(a_mm, 1); loc = self.loc(a_use)
        while loc is None or np.isnan(loc[3]) or np.isnan(loc[4]):
            a_use = round(a_use - 1.0, 1)
            if a_use < 0:
                return None, np.nan
            loc = self.loc(a_use)
        c0, e1, e2, ia, ii = loc
        th = float(np.degrees(np.arctan2((X - c0) @ e2, (X - c0) @ e1)))
        if ii <= th <= ia:
            seg = 'septal' if level == 'apical' else ('anteroseptal' if th >= (ia + ii) / 2 else 'inferoseptal')
        else:
            fw = ((th - ia) % 360) / ((ii - ia) % 360)
            seg = (['anterior', 'lateral', 'inferior'][min(2, int(fw * 3))] if level == 'apical'
                   else ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))])
        return AHA.SEG_NO[(level, seg)], th


def wrapdeg(x):
    return (x + 180.0) % 360.0 - 180.0


def env(s):
    return W0 + (WMAX - W0) * np.minimum(s, WIDEN) / WIDEN


def heart(h):
    t0 = time.time()
    B = os.path.join(REPO, 'data', 'biv', h)
    P = np.loadtxt(os.path.join(B, 'biv.pts'), skiprows=1) / 1e3
    U = {n: np.loadtxt(os.path.join(B, 'uvc', f'{n}.dat')) for n in ('z', 'phi', 'v', 'rho', 'sep')}
    z, phi = U['z'], np.degrees(U['phi'])
    F = AHA.Frame(h)
    LBL = Labeller(F)
    SL = Surf(P, rd_surf(h, 'lv_endo'))
    SR = Surf(P, rd_surf(h, 'rv_endo'))
    lve, rve, epi = SL.nodes, SR.nodes, rd_vtx(h, 'epi')
    net = dict(np.load(os.path.join(B, 'purkinje_v51', 'network_v51.npz')))
    nodes, kind, E, cls, pmj = net['nodes'], net['kind'], net['edges'], net['edge_class'], net['pmj']
    lm = json.load(open(os.path.join(B, 'purkinje', 'summary.json')))['landmarks']
    n51 = json.load(open(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', f'network51_{h}.json')))
    his = int(nodes[int(net['his'])])
    assert his == lm['his']
    rbb_low, mb_end = int(lm['rbb_low']), int(lm['mb_end'])
    zphi = lambda n: [round(float(z[n]), 3), round(float(phi[n]), 1)]

    # AHA labels of every LV endocardial node
    LT = [LBL.label(P[n]) for n in lve]
    lab = np.array([x[0] or 0 for x in LT]); th_l = np.array([x[1] for x in LT], dtype=float)
    seg = dict(zip(lve.tolist(), lab.tolist()))
    S_mask = np.isin(lab, list(SEPTAL))
    S = lve[S_mask]
    apex_lv = int(lve[np.argmin(F.f(P[lve]))])

    # septal crest, crest-to-apex length, D1 line, septal thirds
    bnodes = SL.nodes[np.unique(SL.boundary_edges)]
    crest = np.intersect1d(S, bnodes)
    d_crest, _ = SL.dist(crest, 2)
    d_crest1, _ = SL.dist(crest, 1)
    L = float(d_crest[SL.ids([apex_lv])[0]]); L1 = float(d_crest1[SL.ids([apex_lv])[0]])
    dS = d_crest[SL.ids(S)]
    third = np.where(dS < L / 3, 'upper', np.where(dS < 2 * L / 3, 'middle', 'lower'))
    above = S[dS < L / 3]
    d1_line = S[np.abs(dS - L / 3) <= 0.75]
    # rim membership of the crest
    rims = {r: rd_vtx(h, r) for r in ('mv_rim', 'av_rim', 'avplane_iface', 'ao_iface', 'tv_rim', 'pv_rim', 'part_iface')}
    crest_on = {r: int(np.isin(crest, v).sum()) for r, v in rims.items()}

    # His line and sheet coordinates
    line = SL.path(his, apex_lv, 2)
    sl = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P[line], axis=0), axis=1))]
    da, src = SL.dist(line, 2)
    foot = SL.nodes[src]
    s_of_line = dict(zip(line.tolist(), sl.tolist()))
    s_all = np.array([s_of_line.get(int(f), np.nan) for f in foot])
    th_foot = th_l[src]
    a_all = da * np.sign(wrapdeg(np.nan_to_num(th_l - th_foot)) + 1e-12)
    coord = lambda n: (float(s_all[SL.ids([n])[0]]), float(a_all[SL.ids([n])[0]]))
    at_s = lambda sv: int(line[np.argmin(np.abs(sl - sv))])
    his_in_S = bool(his in set(S.tolist()))

    # fascicle endpoints (v5.1 FASCICLE ends = first distal root on each division, network51) and the code's Durrer points
    fasc = {k: int(v['mesh_node']) for k, v in n51['durrer_sites'].items()}
    code_pts = {}
    for k, wps in (('anterior', (60.0, 0.80)), ('septal', (0.0, 0.50)), ('posterior', (-60.0, 0.33))):
        sc = np.abs(z[lve] - wps[1]) * 10 + np.abs(np.radians(wrapdeg(phi[lve] - wps[0])))
        code_pts[k] = int(lve[np.argmin(sc)])

    # item 8: PMJs on trunk / fascicle nodes
    tf_nodes = np.unique(E[np.isin(cls, ['LB_TRUNK', 'FASCICLE'])])
    tf_mesh = np.unique(nodes[tf_nodes])
    pmj_mesh = nodes[pmj]
    item8 = {'pmj_graph_nodes_that_are_LB_TRUNK_or_FASCICLE_nodes': int(np.isin(pmj, tf_nodes).sum()),
             'pmj_kinds': {k: int(v) for k, v in zip(*np.unique(kind[pmj], return_counts=True))},
             'LB_TRUNK_FASCICLE_graph_nodes': int(len(tf_nodes)), 'their_mesh_nodes': int(len(tf_mesh)),
             'pmj_at_a_trunk_or_fascicle_mesh_node (a distal copy at the same mesh node)': int(np.isin(pmj_mesh, tf_mesh).sum()),
             'answer': 'no: in v5.1 junctions sit on distal-network nodes only; LB_TRUNK and FASCICLE nodes are insulated and carry none'}

    # item 4: LV junctions per AHA segment and septal third, above the D1 line; densities
    lvj = pmj[kind[pmj] == 'distal_lv']; rvj = pmj[kind[pmj] == 'distal_rv']
    lvj_m = nodes[lvj]
    jseg = np.array([seg.get(int(n), 0) for n in lvj_m])
    jS = np.isin(lvj_m, S)
    dj = d_crest[SL.ids(lvj_m[jS])]
    j_third = np.where(dj < L / 3, 'upper', np.where(dj < 2 * L / 3, 'middle', 'lower'))
    above_j = lvj_m[jS][dj < L / 3]
    a_lv, a_rv = SL.area() / 100, SR.area() / 100
    item4 = {'lv_junctions': int(len(lvj)), 'rv_junctions': int(len(rvj)),
             'lv_junctions_per_aha_segment': {int(k): int(v) for k, v in zip(*np.unique(jseg, return_counts=True))},
             'lv_septal_junctions_per_third': {k: int((j_third == k).sum()) for k in ('upper', 'middle', 'lower')},
             'lv_septal_junctions_above_D1_line': int(len(above_j)),
             'above_D1_per_aha_segment': {int(k): int(v) for k, v in zip(*np.unique([seg[int(n)] for n in above_j], return_counts=True))} if len(above_j) else {},
             'lv_endo_area_cm2': round(a_lv, 1), 'rv_endo_area_cm2': round(a_rv, 1),
             'lv_junctions_per_cm2': round(len(lvj) / a_lv, 2), 'rv_junctions_per_cm2': round(len(rvj) / a_rv, 2),
             'cross_check_UVC_z_ge_0.67_lv_septal_junctions': int((jS & (z[lvj_m] >= 0.67)).sum()),
             'cross_check_AHA_2_3_lv_junctions': int(np.isin(jseg, [2, 3]).sum())}

    # item 2 and 10: landmark heights, z = 1
    zr = {r: [round(float(np.mean(z[v])), 3), round(float(np.min(z[v])), 3), round(float(np.max(z[v])), 3)] for r, v in rims.items()}
    item2 = {'z_mean_min_max': {'mitral_annulus (mv_rim)': zr['mv_rim'], 'aortic_valve (av_rim)': zr['av_rim'],
                                'tricuspid (tv_rim)': zr['tv_rim'], 'pulmonary (pv_rim)': zr['pv_rim'],
                                'septal_crest': [round(float(np.mean(z[crest])), 3), round(float(np.min(z[crest])), 3), round(float(np.max(z[crest])), 3)],
                                'moderator_band_septal_insertion (v5.1 rbb_low)': zphi(rbb_low)},
             'axial_fraction_f_mean_min_max (aha51 frame: LV apex 0 -> mitral-ring centroid 1)': {
                 n_: [round(float(np.mean(F.f(P[v]))), 3), round(float(np.min(F.f(P[v]))), 3), round(float(np.max(F.f(P[v]))), 3)]
                 for n_, v in (('mitral_annulus', rims['mv_rim']), ('aortic_valve', rims['av_rim']), ('tricuspid', rims['tv_rim']),
                               ('pulmonary', rims['pv_rim']), ('septal_crest', crest), ('his_exit', np.array([his])),
                               ('moderator_band_septal_insertion', np.array([rbb_low])))},
             'lv_long_axis_mm (apex -> mitral-ring centroid)': round(float(F.Lax), 1),
             'septal_crest_nodes': int(len(crest)), 'crest_nodes_on_rim_or_interface': crest_on,
             'crest_to_apex_mm_2ring': round(L, 2), 'crest_to_apex_mm_1ring_edges': round(L1, 2),
             'his_to_crest_mm': round(float(d_crest[SL.ids([his])[0]]), 2)}
    item10 = {'uvc_z_definition': 'sims/biv_model/03_uvc.py: z = monotone remap of the Laplace field zeta (apex patch 0 -> every '
                                  'valve rim, the AV-plane, aortic, pulmonary and RA interfaces 1) so that its mean follows the '
                                  'normalised axial distance from the LV apex node to the MV + TV rim centroid; z = 1 exactly on '
                                  'that base set (the valve planes), not at the septal crest or the MV + TV centre',
              'z_at_septal_crest_median': round(float(np.median(z[crest])), 3), 'crest_to_apex_mm': round(L, 2),
              'D1_line_at_mm_from_crest': round(L / 3, 2),
              'D1_line_nodes': int(len(d1_line)),
              'D1_line_z_median_min_max': [round(float(np.median(z[d1_line])), 3), round(float(z[d1_line].min()), 3), round(float(z[d1_line].max()), 3)] if len(d1_line) else None,
              'left_septal_nodes': int(len(S)), 'above_D1_nodes': int(len(above)),
              'cross_check_UVC_z_ge_0.67_share_of_above': round(float((z[above] >= 0.67).mean()), 3) if len(above) else None,
              'cross_check_AHA_2_3_share_of_above': round(float(np.isin([seg[int(n)] for n in above], [2, 3]).mean()), 3) if len(above) else None}

    # item 3: sheet levels
    sd = d_crest[SL.ids(line)]
    cross = int(line[np.argmax(sd >= L / 3)]) if (sd >= L / 3).any() else None
    ring_lvl = lambda sv, msk: np.where(msk & (np.abs(s_all - sv) <= 1.25))[0]
    Sloc = np.isin(SL.nodes, S)
    r = ring_lvl(16.5, Sloc)
    amid = 0.5 * (a_all[r].min() + a_all[r].max()) if len(r) else np.nan
    midpt = int(SL.nodes[r[np.argmin(np.abs(a_all[r] - amid))]]) if len(r) else None
    dlv = np.where(kind == 'distal_lv')[0]
    sep_out = int(nodes[dlv[np.argmin(np.linalg.norm(P[nodes[dlv]] - P[midpt], axis=1))]]) if midpt is not None else None
    item3 = {'his_exit': {'node': his, 'z_phi': zphi(his), 'aha_segment': seg.get(his), 'on_left_septal_surface': his_in_S},
             'his_line_length_to_apex_mm': round(float(sl[-1]), 1),
             'line_10mm': {'node': at_s(10), 'z_phi': zphi(at_s(10))}, 'line_12.5mm': {'node': at_s(12.5), 'z_phi': zphi(at_s(12.5))},
             'line_16.5mm': {'node': at_s(16.5), 'z_phi': zphi(at_s(16.5))},
             'sheet_end_33mm': {'node': at_s(33), 'z_phi': zphi(at_s(33)), 'aha_segment': seg.get(at_s(33))},
             'D1_line_crossing_on_his_line': {'node': cross, 's_mm': round(s_of_line[cross], 1) if cross else None, 'z_phi': zphi(cross) if cross else None},
             'septal_outflow': {'mid_septal_point_at_16.5mm': midpt, 'its_z_phi': zphi(midpt) if midpt else None,
                                'nearest_v51_lv_distal_node': sep_out, 'its_z_phi': zphi(sep_out) if sep_out else None,
                                'distance_mm': round(float(np.linalg.norm(P[sep_out] - P[midpt])), 2) if sep_out else None}}

    # item 13: envelope, footprint, septal-surface extent, fascicle endpoints
    # footprint (a): the v5.1 left-bundle nodes the sheet replaces (LB_TRUNK and FASCICLE); (b): every v5.1 LV network node on S
    nf_int = os.path.join(B, 'purkinje_v51', 'network_intact_v51.npz')       # 6G8DD8S5: its cut removed the LB edges
    Ei, ci = (dict(np.load(nf_int))['edges'], dict(np.load(nf_int))['edge_class']) if os.path.exists(nf_int) else (E, cls)
    tfn = np.unique(Ei[np.isin(ci, ['LB_TRUNK', 'FASCICLE'])])
    fpa = SL.ids(np.unique(nodes[tfn][np.isin(nodes[tfn], lve)]))
    lvnet = np.where((kind == 'distal_lv') | ((kind == 'proximal') & np.isin(nodes, lve)))[0]
    fp_mesh = np.unique(nodes[lvnet][np.isin(nodes[lvnet], S)])
    fp = SL.ids(fp_mesh)
    levels = list(np.arange(0, 33, 2.5)) + [33.0]
    rows = []
    def fpr(ix, sv):
        k = ix[np.abs(s_all[ix] - sv) <= 1.25]
        lo, hi = (float(a_all[k].min()), float(a_all[k].max())) if len(k) else (np.nan, np.nan)
        return {'nodes': int(len(k)), 'a_min_max_mm': [round(lo, 2), round(hi, 2)], 'width_mm': round(hi - lo, 2), 'midpoint_a_mm': round(0.5 * (lo + hi), 2)}
    for sv in levels:
        w = env(sv); A_ad, P_ad = w * ANT_SHARE, w * (1 - ANT_SHARE)
        rS = ring_lvl(sv, Sloc)
        smin, smax = (float(a_all[rS].min()), float(a_all[rS].max())) if len(rS) else (np.nan, np.nan)
        rows.append({'s_mm': sv, 'envelope_width_mm': round(w, 2), 'adopted_ant_mm': round(A_ad, 2), 'adopted_post_mm': round(P_ad, 2),
                     'footprint_LB_TRUNK_FASCICLE': fpr(fpa, sv), 'footprint_all_v51_LV_nodes_on_septum': fpr(fp, sv),
                     'septal_surface_a_min_max_mm (nodes whose nearest line point is at this level)': [round(smin, 2), round(smax, 2)]})
    for r_ in rows:                                       # the footprint that the declined placement would centre on: (a)
        r_['footprint_midpoint_a_mm'] = r_['footprint_LB_TRUNK_FASCICLE']['midpoint_a_mm']
    # the envelope as a node set: every LV endocardial node with 0 <= s <= 33 inside the band; off-septum nodes and area
    def band_nodes(lo_fun, hi_fun):
        ok = (s_all >= 0) & (s_all <= SHEET) & np.isfinite(s_all)
        lo, hi = lo_fun(np.where(ok, s_all, 0)), hi_fun(np.where(ok, s_all, 0))
        return np.where(ok & (a_all >= lo) & (a_all <= hi))[0]
    ad = band_nodes(lambda s_: -env(s_) * (1 - ANT_SHARE), lambda s_: env(s_) * ANT_SHARE)
    mids_s = np.array([r_['s_mm'] for r_ in rows]); mids = np.array([r_['footprint_midpoint_a_mm'] for r_ in rows], dtype=float)
    okm = np.isfinite(mids)
    mid_fun = (lambda s_: np.interp(s_, mids_s[okm], mids[okm])) if okm.any() else (lambda s_: np.full_like(s_, np.nan))
    de = band_nodes(lambda s_: mid_fun(s_) - env(s_) / 2, lambda s_: mid_fun(s_) + env(s_) / 2)
    def offsept(ix):
        off = ix[~Sloc[ix]]
        tri_all = SL.lid
        keep = np.zeros(len(SL.nodes), bool); keep[ix] = True
        t_in = keep[tri_all].all(1); t_off = t_in & (~Sloc[tri_all]).any(1)
        ar = lambda m: float(0.5 * np.linalg.norm(np.cross(SL.X[tri_all[m, 1]] - SL.X[tri_all[m, 0]], SL.X[tri_all[m, 2]] - SL.X[tri_all[m, 0]]), axis=1).sum())
        segs = {int(k): int(v) for k, v in zip(*np.unique(lab[off], return_counts=True))}
        return {'envelope_nodes': int(len(ix)), 'off_septum_nodes': int(len(off)), 'off_septum_segments': segs,
                'envelope_area_mm2': round(ar(t_in), 1), 'area_touching_off_septum_nodes_mm2': round(ar(t_off), 1),
                'off_septum_s_range_mm': [round(float(s_all[off].min()), 1), round(float(s_all[off].max()), 1)] if len(off) else None,
                'off_septum_a_range_mm': [round(float(a_all[off].min()), 1), round(float(a_all[off].max()), 1)] if len(off) else None}
    env_sets = {'adopted (17.8 / 4.8 mm)': offsept(ad), 'declined (centred on the LB_TRUNK + FASCICLE footprint midpoint)': offsept(de) if okm.any() else None}
    # share of the adopted envelope below the D1 line and beyond the first 10 mm (where D1 allows junctions)
    dloc = d_crest
    keep = np.zeros(len(SL.nodes), bool); keep[ad] = True
    tri_in = keep[SL.lid].all(1)
    tri_area_ = 0.5 * np.linalg.norm(np.cross(SL.X[SL.lid[:, 1]] - SL.X[SL.lid[:, 0]], SL.X[SL.lid[:, 2]] - SL.X[SL.lid[:, 0]]), axis=1)
    tri_below = (dloc[SL.lid].mean(1) >= L / 3) & (s_all[SL.lid].mean(1) > 10.0)
    env_sets['adopted_envelope_area_where_D1_allows_junctions'] = {
        'area_mm2': round(float(tri_area_[tri_in & tri_below].sum()), 1), 'of_total_mm2': round(float(tri_area_[tri_in].sum()), 1),
        'share': round(float(tri_area_[tri_in & tri_below].sum() / max(tri_area_[tri_in].sum(), 1e-9)), 3),
        'rule': 'triangles of the envelope whose mean distance from the crest is at least L / 3 and whose mean s exceeds 10 mm'}
    def endpoint(n):
        s_, a_ = coord(n)
        out = {'node': n, 'z_phi': zphi(n), 'aha_segment': seg.get(n), 'on_left_septal_surface': bool(n in set(S.tolist())),
               's_mm': round(s_, 2), 'a_mm': round(a_, 2), 'beyond_sheet_end': bool(s_ > SHEET)}
        if s_ <= SHEET:
            w = env(s_)
            out['adopted'] = {'ant_limit': round(w * ANT_SHARE, 2), 'post_limit': round(-w * (1 - ANT_SHARE), 2),
                              'inside': bool(-w * (1 - ANT_SHARE) <= a_ <= w * ANT_SHARE),
                              'outside_by_mm': round(max(0.0, a_ - w * ANT_SHARE, -w * (1 - ANT_SHARE) - a_), 2)}
            mids = [r_['footprint_midpoint_a_mm'] for r_ in rows]
            ss = [r_['s_mm'] for r_ in rows]
            okm = [(x, y) for x, y in zip(ss, mids) if y == y]
            m = float(np.interp(s_, [x for x, _ in okm], [y for _, y in okm])) if okm else np.nan
            out['declined'] = {'midpoint_a': round(m, 2), 'limits': [round(m - w / 2, 2), round(m + w / 2, 2)],
                               'inside': bool(m - w / 2 <= a_ <= m + w / 2),
                               'outside_by_mm': round(max(0.0, a_ - (m + w / 2), (m - w / 2) - a_), 2)}
        else:
            out['adopted'] = {'inside': False, 'reason': f'beyond the 33 mm sheet end (s = {s_:.1f} mm)'}
            out['declined'] = {'inside': False, 'reason': f'beyond the 33 mm sheet end (s = {s_:.1f} mm)'}
        return out
    ep = {k: endpoint(v) for k, v in fasc.items()}
    item13 = {'his_line_nodes': int(len(line)), 'levels': rows,
              'fascicle_endpoints': ep,
              'anterior_minus_posterior_a_mm': round(ep['anterior']['a_mm'] - ep['posterior']['a_mm'], 2),
              'anterior_posterior_surface_distance_mm': round(float(SL.dist([fasc['anterior']], 2)[0][SL.ids([fasc['posterior']])[0]]), 2),
              'note_levels': 'the anterior and posterior endpoints are at different levels (s and z above), so their separation '
                             'is given as the difference in a and as the surface distance',
              'envelope_on_left_septal_surface': env_sets,
              'any_level_without_footprint (LB_TRUNK + FASCICLE)': [r_['s_mm'] for r_ in rows if r_['footprint_LB_TRUNK_FASCICLE']['nodes'] == 0],
              'footprint_nodes': {'LB_TRUNK + FASCICLE on the LV endocardium': int(len(fpa)), 'all v5.1 LV network nodes on the septum': int(len(fp_mesh))}}

    # item 14: septal boundaries and gate-7(a) patch centres; item 9: code points to centres
    lab_l = lab                                               # per local LV node
    nbr = SL.A.tocsr()
    def bset(fw):
        out = []
        for i in np.where(S_mask)[0]:
            if np.isin(lab_l[nbr.indices[nbr.indptr[i]:nbr.indptr[i + 1]]], list(fw)).any():
                out.append(i)
        return SL.nodes[np.array(out, dtype=np.int64)] if out else np.array([], dtype=np.int64)
    B_ant, B_inf = bset(ANT_FW), bset(INF_FW)
    mv = rims['mv_rim']; mvl = np.intersect1d(mv, lve)
    d_ma, _ = SL.dist(mvl, 2) if len(mvl) else (None, None)
    z_ma = float(np.median(z[mv]))
    z_post = z_ma / 3.0
    def bdesc(k):
        """UVC phi (circular mean) and AHA angle (mean, 0 = septal centre, + anterior) of boundary nodes; node nearest both."""
        if not len(k):
            return None
        pm = float(np.degrees(np.angle(np.exp(1j * np.radians(phi[k])).mean())))
        ta = th_l[SL.ids(k)]
        return {'nodes': int(len(k)), 'uvc_phi_deg': round(pm, 1), 'uvc_phi_range_deg': [round(float(phi[k].min()), 1), round(float(phi[k].max()), 1)],
                'aha_angle_deg': round(float(np.nanmean(ta)), 1), 'z_mean': round(float(z[k].mean()), 3)}
    def bphi(zv, tol=0.01):
        return {nm: bdesc(Bs[np.abs(z[Bs] - zv) <= tol]) for nm, Bs in (('anterior', B_ant), ('posterior_inferior', B_inf))}
    def bphi_ma(dv, tol=0.75):
        return {nm: bdesc(Bs[np.abs(d_ma[SL.ids(Bs)] - dv) <= tol]) for nm, Bs in (('anterior', B_ant), ('posterior_inferior', B_inf))}
    fw_ant = np.isin(lab_l, list(ANT_FW | {6, 12, 16}))       # anterior-side free wall (anterior and anterolateral)
    fw_inf = np.isin(lab_l, list(INF_FW | {5, 11, 16}))
    d_from_Bant, _ = SL.dist(B_ant, 2) if len(B_ant) else (None, None)
    d_from_Binf, _ = SL.dist(B_inf, 2) if len(B_inf) else (None, None)
    centres, stop = {}, []
    # posterior paraseptal: level z_post, inferior free-wall side, 10 mm from the inferior septal boundary
    if len(B_inf):
        c = np.where(fw_inf & (np.abs(z[SL.nodes] - z_post) <= 0.01))[0]
        if len(c):
            i = c[np.argmin(np.abs(d_from_Binf[c] - PATCH_R))]
            centres['posterior_paraseptal'] = {'node': int(SL.nodes[i]), 'z_phi': zphi(SL.nodes[i]), 'aha_segment': int(lab_l[i]), 'aha_angle_deg': round(float(th_l[i]), 1),
                                               'distance_from_boundary_mm': round(float(d_from_Binf[i]), 2), 'level_rule': f'z = z_MA / 3 = {z_post:.3f}'}
        else:
            stop.append('posterior paraseptal: no inferior free-wall node at the level')
    else:
        stop.append('inferior septal boundary not identified')
    # central: z = 0.50, midway between the anterior and posterior septal boundaries (UVC phi is distorted on the septum,
    # audit F02, so "midway" is taken as equal surface distance from the two boundary lines along the z 0.50 ring of S)
    bp50 = bphi(0.50)
    if bp50['anterior'] is not None and bp50['posterior_inferior'] is not None:
        c = np.where(S_mask & (np.abs(z[SL.nodes] - 0.50) <= 0.01))[0]
        i = c[np.argmin(np.abs(d_from_Bant[c] - d_from_Binf[c]))]
        centres['central'] = {'node': int(SL.nodes[i]), 'z_phi': zphi(SL.nodes[i]), 'aha_segment': int(lab_l[i]),
                              'aha_angle_deg': round(float(th_l[i]), 1),
                              'distance_to_anterior_and_inferior_boundaries_mm': [round(float(d_from_Bant[i]), 2), round(float(d_from_Binf[i]), 2)]}
    else:
        stop.append('septal boundary at z 0.50 not identified')
    # anterior paraseptal: 10 mm (surface) below the mitral annulus, anterior free-wall side, 10 mm from the anterior septal boundary
    if d_ma is not None and len(B_ant):
        c = np.where(fw_ant & (np.abs(d_ma - 10.0) <= 0.75))[0]
        if len(c):
            i = c[np.argmin(np.abs(d_from_Bant[c] - PATCH_R))]
            centres['anterior_paraseptal'] = {'node': int(SL.nodes[i]), 'z_phi': zphi(SL.nodes[i]), 'aha_segment': int(lab_l[i]), 'aha_angle_deg': round(float(th_l[i]), 1),
                                              'distance_from_boundary_mm': round(float(d_from_Bant[i]), 2),
                                              'distance_below_mitral_annulus_mm': round(float(d_ma[i]), 2)}
        else:
            stop.append('anterior paraseptal: no anterior free-wall node 10 mm below the mitral annulus')
    else:
        stop.append('anterior septal boundary or mitral annulus not identified')
    item14 = {'z_mitral_annulus_median': round(z_ma, 3), 'boundary_nodes': {'anterior': int(len(B_ant)), 'posterior_inferior': int(len(B_inf))},
              'boundary_phi_deg': {'z_0.33': bphi(0.33), f'z_{z_post:.3f} (= z_MA / 3)': bphi(z_post), 'z_0.50': bphi(0.50),
                                   '10mm_below_mitral_annulus': bphi_ma(10.0) if d_ma is not None else None},
              'patch_centres': centres, 'stop': stop}
    pairs = {'anterior': 'anterior_paraseptal', 'septal': 'central', 'posterior': 'posterior_paraseptal'}
    item9 = {}
    for k, cn in pairs.items():
        if cn in centres:
            a_, b_ = code_pts[k], centres[cn]['node']
            item9[k] = {'code_point_node': a_, 'z_phi': zphi(a_), 'aha_segment': seg.get(a_), 'patch': cn, 'patch_node': b_,
                        'euclid_mm': round(float(np.linalg.norm(P[a_] - P[b_])), 2),
                        'surface_mm': round(float(SL.dist([a_], 2)[0][SL.ids([b_])[0]]), 2)}
    item1 = {'fascicle_endpoints (FASCICLE ends, network51 durrer_sites)': {k: {'node': v, 'z_phi': zphi(v), 'aha_segment': seg.get(v)} for k, v in fasc.items()},
             'code_durrer_points (14_purkinje.py:93-94 divisions)': {k: {'node': v, 'z_phi': zphi(v), 'aha_segment': seg.get(v)} for k, v in code_pts.items()},
             'endpoints_equal_code_points': {k: fasc[k] == code_pts[k] for k in fasc}}

    # item 5: papillary muscles / trabeculae
    item5 = {'cohort_tags': 'tags_lvrv.json has no papillary-muscle or trabecular tag (LV, RV, LA, RA, Ao, PArt, valves, '
                            'vein rings, FEC_LV / RV / SV, BB, AV_plane)',
             'lv_endo_topology': SL.euler(), 'rv_endo_topology': SR.euler(),
             'reading': 'genus 0 means no handle: no free-running papillary muscle or trabecula bridges the cavity'}

    # items 6 and 12: moderator band
    rv_sep = rve[cKDTree(P[lve]).query(P[rve])[0] < cKDTree(P[epi]).query(P[rve])[0]]
    rv_fw = np.setdiff1d(rve, rv_sep)
    band = rv_fw[np.abs(z[rv_fw] - z[rbb_low]) <= 0.05]
    pb = phi[band]
    pmed = float(np.degrees(np.angle(np.exp(1j * np.radians(pb)).mean())))
    ant_band = band[wrapdeg(pb - pmed) > 0]
    cand = int(ant_band[np.argmin(np.linalg.norm(P[ant_band] - P[rbb_low], axis=1))]) if len(ant_band) else None
    rvd = np.where(kind == 'distal_rv')[0]
    join = int(nodes[rvd[np.argmin(np.linalg.norm(P[nodes[rvd]] - P[cand], axis=1))]]) if cand is not None else None
    # level of the insertion on the RV septum
    srs = Surf(P, rd_surf(h, 'rv_endo')[np.isin(rd_surf(h, 'rv_endo'), rv_sep).all(1)])
    rcrest = srs.nodes[np.unique(srs.boundary_edges)]
    rcrest = rcrest[z[rcrest] >= np.percentile(z[srs.nodes], 80)]
    rapex = int(srs.nodes[np.argmin(z[srs.nodes])])
    drc, _ = srs.dist(rcrest, 2)
    ins_frac = float(drc[srs.ids([rbb_low])[0]] / drc[srs.ids([rapex])[0]]) if rbb_low in srs.loc else None
    lvl = None if ins_frac is None else ('top fifth' if ins_frac < 0.2 else 'upper third' if ins_frac < 1 / 3 else 'middle third' if ins_frac < 2 / 3 else 'lower third')
    rb_edges = np.where(cls == 'RB')[0]
    mb_edge = [int(i) for i in rb_edges if {int(nodes[E[i, 0]]), int(nodes[E[i, 1]])} == {rbb_low, mb_end}]
    item6_12 = {'v51_RB': {'class_RB_edges': int(len(rb_edges)), 'arc_mm': n51['E2_segments']['RB']['arc_mm'],
                           'septal_end (rbb_low, the insertion)': {'node': rbb_low, 'z_phi': zphi(rbb_low)},
                           'class_RB_ends_at (mb_end)': {'node': mb_end, 'z_phi': zphi(mb_end), 'on_rv_free_wall': bool(mb_end in set(rv_fw.tolist()))},
                           'straight_moderator_band_edge_in_v51': bool(mb_edge), 'v51_band_length_mm': round(float(np.linalg.norm(P[rbb_low] - P[mb_end])), 2),
                           'v51_band_speed_m_s': float(net['edge_speed'][mb_edge[0]]) if mb_edge else None,
                           'v51_band_carries_pmj': bool(np.isin(np.where(nodes == mb_end)[0], pmj).any()),
                           'rule_in_v51': '14_purkinje.py build(): RB down the RV septum to z 0.35, then a straight cavity-crossing edge '
                                          'to the anterior RV free wall at z 0.35 (75th percentile of phi in the free-wall band), '
                                          'where the RV distal tree is rooted; classed RB at 1.5 m/s by network51.py'},
                'item6_insertion_to_nearest_anterior_rv_free_wall_mm': round(float(np.linalg.norm(P[cand] - P[rbb_low])), 2) if cand else None,
                'item12_candidate_end_node': {'papillary_muscle_in_mesh': False,
                                              'anterior_rv_free_wall_label_in_mesh': False,
                                              'construction_used': 'no such label exists: RV free-wall endocardium = RV endocardial nodes nearer the '
                                                                   'epicardium than the LV endocardium (as 14_purkinje.py); anterior = the half of the '
                                                                   'free-wall band (z within +-0.05 of the insertion) with phi above the band\'s circular '
                                                                   'mean; nearest such node to the insertion (inference, needs a word before step 2g)',
                                              'node': cand, 'z_phi': zphi(cand) if cand else None,
                                              'chain_length_mm (straight, cavity-crossing)': round(float(np.linalg.norm(P[cand] - P[rbb_low])), 2) if cand else None,
                                              'vs_Lee_Hur_13.6_mm_and_stop_37.8_mm': 'under 37.8 mm' if cand and np.linalg.norm(P[cand] - P[rbb_low]) <= 37.8 else 'over 37.8 mm',
                                              'nearest_v51_rv_distal_node': join,
                                              'distance_to_v51_mb_end_mm': round(float(np.linalg.norm(P[cand] - P[mb_end])), 2) if cand else None},
                'item12_insertion_level': {'rv_septal_crest_to_insertion_over_crest_to_apex': round(ins_frac, 3) if ins_frac is not None else None,
                                           'level': lvl, 'Lee_Hur_origins': 'middle 25 of 36, upper third 13.9 %, lower third 11.1 %, top fifth 5.6 %'}}

    # item 7: the z 0.9 network cap below the mitral annulus
    zcap = lve[np.abs(z[lve] - 0.90) <= 0.005]
    item7 = {'axial_mm (z_MA - 0.90) x base-apex length': round((z_ma - 0.90) * json.load(open(os.path.join(B, 'summary_03.json')))['base_minus_apex_mm'], 1),
             'surface_mm_median_from_mitral_annulus_to_z0.90_on_lv_endo': round(float(np.median(d_ma[SL.ids(zcap)])), 1) if d_ma is not None and len(zcap) else None,
             'lv_distal_nodes_above_z0.90': int((z[nodes[kind == 'distal_lv']] > 0.90).sum())}

    # item 11: Upadhyay sampling line
    item11 = {'rule': '12 points at 2 mm spacing along the His line from the sheet origin (s = 0, 2, ..., 22 mm; assumption 49)',
              'points': [{'s_mm': 2.0 * k, 'node': at_s(2.0 * k), 'z_phi': zphi(at_s(2.0 * k)), 'aha_segment': seg.get(at_s(2.0 * k)),
                          'on_left_septal_surface': bool(at_s(2.0 * k) in set(S.tolist()))} for k in range(12)]}

    # step-0 stop triggers in this report
    trig = {'fascicle_endpoint_outside_envelope (adopted placement)': [k for k in ('anterior', 'posterior') if not ep[k]['adopted']['inside']],
            'fascicle_endpoint_outside_envelope (declined placement)': [k for k in ('anterior', 'posterior') if not ep[k]['declined']['inside']],
            'envelope_off_left_septal_surface (adopted): off-septum nodes': env_sets['adopted (17.8 / 4.8 mm)']['off_septum_nodes'],
            'no_lv_septal_junction_above_D1_line': item4['lv_septal_junctions_above_D1_line'] == 0,
            'v51_trunk_fascicle_nodes_carry_no_pmj': item8['pmj_graph_nodes_that_are_LB_TRUNK_or_FASCICLE_nodes'] == 0,
            'septal_boundary_or_mitral_annulus_not_found': stop}
    return {'heart': h, 'item1': item1, 'item2': item2, 'item3': item3, 'item4': item4, 'item5': item5, 'items6_12': item6_12,
            'item7': item7, 'item8': item8, 'item9': item9, 'item10': item10, 'item11': item11, 'item13': item13, 'item14': item14,
            'stop_triggers': trig, 'wall_s': round(time.time() - t0, 1)}


def main():
    hs = sys.argv[1:] or HEARTS
    for h in hs:
        r = heart(h)
        json.dump(r, open(os.path.join(HERE, f'report34_{h}.json'), 'w'), indent=1, default=str)
        print(h, json.dumps(r['stop_triggers'], default=str), f"{r['wall_s']} s", flush=True)


if __name__ == '__main__':
    main()
