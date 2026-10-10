#!/usr/bin/env python
"""
Step 14 (2026-10-07): His-Purkinje network arm. Alex, 7 Oct 2026 20:40 UTC: "network run. but can you build
as realistic a purkinje network as possible". Extra arm next to the frozen fast-layer model (dated addition).

NETWORK (a graph whose nodes are endocardial mesh nodes; it has no volume in the mesh)
  His and left bundle  His point H on the LV septal endocardium just below the aortic annulus at the right
        coronary cusp (membranous septum; Elizari 2017, J Electrocardiol 50:389, doi 10.1016/j.jelectrocard.
        2017.03.004: the LBB arises from the branching portion under the membranous septum). The LBB runs
        ~10 mm down the septum (z - 0.10) to a branching point, then three insulated fascicles (no junctions)
        follow the endocardium to Durrer's three earliest LV sites (Durrer 1970, Circulation 41:899,
        doi 10.1161/01.cir.41.6.899): anterior (high anterior paraseptal, phi +60, z 0.80), septal (centre of
        the left septal surface, phi 0, z 0.50), posterior (posterior paraseptal, one third from apex to base,
        phi -60, z 0.33). Elizari: anterior and posterior divisions, a septal fascicle in some hearts.
  Right bundle  penetrates the septum from H to the nearest RV endocardial node, runs insulated down the RV
        septum to z 0.35 and crosses the cavity as a straight moderator band to the anterior RV free wall at
        z 0.35. No distal network on the RV septum above z 0.35 (Sahli Costabal 2016: RBB unbranched until the
        RV apex; Bayer 2025: only major fascicles, no junctions, on the mid-upper RV septum).
  Distal network  fractal trees (Sahli Costabal et al. 2016, J Biomech 49:2455, doi 10.1016/j.jbiomech.
        2015.12.025): branch length 8 mm (sd 0.63 mm, variance 0.4), branch angle 0.15 rad, repulsion 0.1,
        ~1 mm segments grown on the endocardial surface nodes, from each fascicle end (LV) and the moderator
        band end (RV). Colliding branches reconnect to the network they hit (Bayer et al. 2025, Front Physiol
        16:1657611, doi 10.3389/fphys.2025.1657611: distal reconnections matter for retrograde activation).
        Grown up to z 0.90 in network v3 (job 8; like the frozen fast layer) and up to the base (z <= 1.0) in v4
        (9 Oct 2026; `build --version v4`). v3 that left the base and outflow to be activated last from below, 76-90 ms after the His, and gave the
        His-driven beat a superior axis (-63 to -98 deg in all three hearts; LABNOTES 9 Oct).
  Junctions (PMJs)  distal-network nodes, terminals first, kept a minimum distance apart; the distance is set so
        there are 15 junctions per cm2 of the endocardium the distal network may cover (Bayer 2025).
SPEEDS AND DELAYS
  Purkinje conduction 2.0 m/s in every segment (Sahli Costabal 2016; Berg et al. 2023, Sci Rep 13:11788,
        doi 10.1038/s41598-023-38653-1; Choi et al. 2023, Front Cardiovasc Med 10:1158480, doi 10.3389/
        fcvm.2023.1158480: rabbit insulated fibres > 2 m/s).
  Purkinje -> muscle delay 4 ms (Berg 2023: 3-5 ms; Choi 2023, rabbit: 3.4 +- 0.8 and 7.8 +- 2.4 ms).
  Muscle -> Purkinje delay 2 ms (ASSUMPTION, not sourced: retrograde entry is driven by the large muscle
        source into a thin strand, so it is taken shorter than the anterograde delay).
COUPLING (pure eikonal; the myocardium keeps the frozen 0.6 / 0.4 / 0.48 m/s; the fast layer is OFF)
  Paced site: T0 = myocardium-only activation from the site (job 1, runs/2026-10-07_nofast_*); junction p is
  entered at T0(p) + 2 ms; Dijkstra on the network gives each node's time; every junction whose exit time
  T_P(p) + 4 ms is earlier than T0(p) becomes a timed stimulus (bins of 0.25 ms) in one more eikonal run
  together with the site itself. Iterated (couple()): the new field can enter other junctions earlier
  (smoke test 8 Oct: up to 29 ms after one pass), so passes repeat until no network node gains > 1 ms
  (max 4 runs). Junctions < 6 mm apart are also linked through the muscle at a conservative 0.4 m/s plus
  both delays, so the first pass starts close (numerical shortcut; the eikonal field decides).
  His-driven (sinus-like) beat: His at 0 ms, every junction exits at T_P(p) + 4 ms.
LBBB-LIKE HEART (6G8DD8S5, P['lbbb_cut_hearts']; Alex 9 Oct 2026): the left bundle is cut between the His and its
  branching point (no link either way); the LV fascicles keep the speeds of the same calibration rule and the LV
  distal network is intact, so the LV is reached from the RV network through the septal muscle and its junctions.
  Upadhyay et al. 2019, Circulation 139:1876, doi 10.1161/CIRCULATIONAHA.118.038648: complete block in the proximal
  left conduction system in 64 % of 72 LBBB-pattern patients (left His fibres 72 %, proximal left bundle 28 %),
  distal Purkinje recruitable by His pacing; 36 % had no discrete block (not modelled).
DURRER CALIBRATION OF THE DISTAL NETWORK (network v4; Alex said "yes" on 9 Oct 2026, 16:15 UTC)
  Durrer 1970: the LV endocardial front is nearly closed 30 ms after the first LV activity, except the posterobasal
  area; latest activation 62-80 ms. v3's distal network at the sourced 2.0 m/s activated only 48 % of the control
  heart's LV endocardium within 30 ms (latest 104 ms after LV onset), because the fractal paths are long and
  tortuous. Stage 'durrer' therefore sets ONE distal speed per heart, the lowest that activates
  P['durrer_lv_endo_pct'] = 95 % of the LV endocardial nodes within 30 ms of the first LV endocardial activation in
  the His-driven beat (combined graph, intact network for the LBBB-like heart). ASSUMPTION: 95 % is my reading of
  "nearly closed except the posterobasal area"; the speed (expected 4-5 m/s) is a calibrated value, above the
  ~2 m/s Durrer estimated from two Purkinje spikes, like the calibrated bundle speeds. The frontal axis and total
  activation are checks afterwards, not targets.
ECG: 12_eikonal.py (pseudo-Vm template, fast lead-field ECG, no-fast-layer weights, since the network has
no volume) with --stim-json; scoring by the job runner / 10_measure_ecg.py.

Usage (HEART=<id>, from sims/biv_model):
  python 14_purkinje.py build [--version v3|v4]  -> data/biv/<HEART>/purkinje/ (network.npz, summary.json, network.png)
  python 14_purkinje.py sinus --ID <run>         His-driven beat (+ ECG, Durrer checks in summary_14.json)
  python 14_purkinje.py durrer                   -> distal speed calibrated to Durrer (after build and calib; v4)
  python 14_purkinje.py calib                    -> graph_scale.json (needs the job-1-style no-layer runs of --calib-sites)
  python 14_purkinje.py site --ID <run> --site-node N [--t0-run <no-layer run folder>] [--ecg-dir D]
"""

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from common import HEART, OUT, REPO, read_elem, read_lon, read_pts, read_vtx, write_vtx

PK = os.path.join(OUT, 'purkinje')
SURF = os.path.join(OUT, 'surfaces')
B = os.path.dirname(os.path.abspath(__file__))
P = {'v_mm_per_ms': 2.0, 'd_ant_ms': 4.0, 'd_ret_ms': 2.0, 'pmj_per_cm2': 15.0,
     'branch_mm': 8.0, 'branch_sd_mm': 0.4 ** 0.5, 'angle_rad': 0.15, 'repulsion': 0.1, 'seg_mm': 1.0,
     'z_max': 0.90, 'rv_septum_z_max': 0.35, 'lbb_drop_z': 0.10, 'mb_z': 0.35, 'max_gen': 40, 'seed': 20261007,
     'divisions': {'anterior': [(60.0, 0.80), (120.0, 0.45), (120.0, 0.12)], 'septal': [(0.0, 0.50), (0.0, 0.12)],
                   'posterior': [(-60.0, 0.33), (-120.0, 0.35), (-120.0, 0.12)]},
     'bud_mm': 10.0, 'rv_apex_z': 0.12,
     'durrer_offset_ms': {'anterior': 0.0, 'septal': 2.5, 'posterior': 5.0}, 'rv_after_lv_ms': 7.5,
     'post_site_speed_mm_per_ms': None,
     'stim_bin_ms': 0.25, 'bridge_mm': 6.0, 'v_bridge_mm_per_ms': 0.4, 'couple_tol_ms': 1.0, 'max_pass': 4,
     'lbbb_cut_hearts': ['6G8DD8S5'], 'network_version': 'v3', 'durrer_lv_endo_pct': 95.0, 'durrer_window_ms': 30.0,
     'v_distal_max_mm_per_ms': 12.0}


# ------------------------------------------------------------------ geometry helpers
def load():
    pts = read_pts(os.path.join(OUT, 'bivF')) / 1e3
    U = os.path.join(OUT, 'uvc')
    z, phi, v = (np.loadtxt(os.path.join(U, n + '.dat')) for n in ('z', 'phi', 'v'))
    return pts, z, phi, v


def surf_tris(name):
    return np.loadtxt(os.path.join(SURF, name + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)


def vertex_normals(pts, tri, nodes):
    n = np.zeros((len(pts), 3))
    fn = np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]])
    for k in range(3):
        np.add.at(n, tri[:, k], fn)
    n = n[nodes]
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


def surface_graph(pts, tri):
    e = np.vstack([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]])
    e = np.unique(np.sort(e, axis=1), axis=0)
    w = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
    N = len(pts)
    g = coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(N, N)).tocsr()
    return g


def surface_path(g, a, b):
    """Shortest path a -> b along the surface edges (node ids)."""
    _, pred = dijkstra(g, indices=a, return_predecessors=True)
    path = [b]
    while path[-1] != a:
        path.append(int(pred[path[-1]]))
        if path[-1] < 0:
            raise RuntimeError('no surface path')
    return path[::-1]


def nearest(nodes, pts, x):
    return int(nodes[np.argmin(np.linalg.norm(pts[nodes] - x, axis=1))])


def uvc_node(nodes, z, phi, zt, pht):
    s = np.abs(z[nodes] - zt) * 10 + np.abs(np.angle(np.exp(1j * (phi[nodes] - np.radians(pht)))))
    return int(nodes[np.argmin(s)])


# ------------------------------------------------------------------ fractal tree on a surface
class Tree:
    def __init__(self, pts, allowed, normals, rng):
        self.pts, self.allowed, self.rng = pts, allowed, rng
        self.ts = cKDTree(pts[allowed])
        self.nrm = dict(zip(allowed.tolist(), normals))
        self.nodes, self.branch_of, self.edges, self.terminals, self.reconnect = [], [], [], [], 0
        self.index = {}

    def add(self, n, br):
        if n not in self.index:
            self.index[n] = len(self.nodes)
            self.nodes.append(n)
            self.branch_of.append(br)
        return self.index[n]

    def grow(self, roots):
        """roots: list of (start node, [unit directions]). Sahli Costabal 2016 algorithm, simplified: nodes snap
        to surface mesh nodes; repulsion = unit vector away from the nearest node of another branch (the exact
        gradient of the distance); a branch that comes within 0.75 segment of another branch joins it and stops."""
        nb = 0
        queue = []                                            # (start node, direction, own id, excluded ids)
        for n0, dirs in roots:
            self.add(n0, -1)
            ids = list(range(nb, nb + len(dirs))); nb += len(dirs)
            queue += [(n0, d, i, set(ids) | {-1}) for d, i in zip(dirs, ids)]
        for gen in range(P['max_gen']):
            if not queue:
                break
            old = np.array(self.nodes); old_br = np.array(self.branch_of)
            t_old = cKDTree(self.pts[old])
            order = self.rng.permutation(len(queue))
            new_queue, gen_nodes, gen_br = [], [], []
            for qi in order:
                n0, d, br, excl = queue[qi]
                L = max(2.0, self.rng.normal(P['branch_mm'], P['branch_sd_mm']))
                p, cur, ok = self.pts[n0], n0, True
                for _ in range(int(round(L / P['seg_mm']))):
                    dd, ii = t_old.query(p, k=min(16, len(old)))
                    grad = np.zeros(3)
                    for dist, i in zip(np.atleast_1d(dd), np.atleast_1d(ii)):
                        if old_br[i] not in excl and dist > 1e-9:
                            grad = (p - self.pts[old[i]]) / dist
                            break
                    nrm = self.nrm[cur]
                    d = d + P['repulsion'] * grad
                    d = d - (d @ nrm) * nrm
                    if np.linalg.norm(d) < 1e-9:
                        ok = False; break
                    d = d / np.linalg.norm(d)
                    _, cand = self.ts.query(p + P['seg_mm'] * d, k=6)
                    nxt = next((int(self.allowed[c]) for c in np.atleast_1d(cand)
                                if int(self.allowed[c]) != cur and (self.pts[int(self.allowed[c])] - p) @ d > 0.3 * P['seg_mm']), None)
                    if nxt is None:
                        ok = False; break
                    hit = None
                    if nxt in self.index and self.branch_of[self.index[nxt]] not in excl:
                        hit = nxt
                    else:
                        dist, i = t_old.query(self.pts[nxt])
                        if dist < 0.75 * P['seg_mm'] and old_br[i] not in excl:
                            hit = int(old[i])
                        elif gen_nodes:
                            gn = np.array(gen_nodes)
                            dg = np.linalg.norm(self.pts[gn] - self.pts[nxt], axis=1)
                            j = int(np.argmin(dg))
                            if dg[j] < 0.75 * P['seg_mm'] and gen_br[j] not in excl:
                                hit = int(gn[j])
                    if hit is not None:                   # reconnection (Bayer 2025)
                        self.edges.append((self.index[cur], self.index[hit]))
                        self.reconnect += 1
                        ok = False; break
                    self.edges.append((self.index[cur], self.add(nxt, br)))
                    gen_nodes.append(nxt); gen_br.append(br)
                    d = (self.pts[nxt] - p) / np.linalg.norm(self.pts[nxt] - p)
                    p, cur = self.pts[nxt], nxt
                if not ok:
                    self.terminals.append(cur)
                    continue
                nrm = self.nrm[cur]
                ids = [nb, nb + 1]; nb += 2
                for sgn, cid in zip((1, -1), ids):        # two children, +-angle about the surface normal
                    a = sgn * P['angle_rad']
                    dc = d * np.cos(a) + np.cross(nrm, d) * np.sin(a)
                    new_queue.append((cur, dc / np.linalg.norm(dc), cid, {cid, ids[0], ids[1], br, -1}))
            queue = new_queue
        self.terminals += [q[0] for q in queue]
        return self


# ------------------------------------------------------------------ build
def budding(pts, path):
    """Roots for distal trees along a division path: at its first node (3 branches), every P['bud_mm'] of path
    length (2 side branches) and at its end (3 branches). Returns [(node, path up to node, n branches)]."""
    out, run_ = [(path[0], path[:2][::-1] if len(path) > 1 else path, 3)], 0.0
    for i in range(1, len(path)):
        run_ += float(np.linalg.norm(pts[path[i]] - pts[path[i - 1]]))
        if i == len(path) - 1:
            out.append((path[i], path[:i + 1], 3))
        elif run_ >= P['bud_mm']:
            out.append((path[i], path[:i + 1], 2)); run_ = 0.0
    return out


def build(version='v3'):
    """v3: distal network up to z 0.90, distal 2.0 m/s (job 8). v4: up to the base, distal speed set by 'durrer'."""
    P['network_version'] = version
    P['z_max'] = {'v3': 0.90, 'v4': 1.0}[version]
    rng = np.random.default_rng(P['seed'])
    pts, z, phi, v = load()
    lv, rv, epi = (read_vtx(os.path.join(SURF, n + '.vtx')) for n in ('lv_endo', 'rv_endo', 'epi'))
    tl, tr = surf_tris('lv_endo'), surf_tris('rv_endo')
    gl, gr = surface_graph(pts, tl), surface_graph(pts, tr)
    t_epi, t_lv = cKDTree(pts[epi]), cKDTree(pts[lv])
    rv_sep = rv[t_lv.query(pts[rv])[0] < t_epi.query(pts[rv])[0]]        # RV septal surface
    rv_fw = np.setdiff1d(rv, rv_sep)
    # landmarks
    ann = np.unique(np.concatenate([read_vtx(os.path.join(SURF, 'av_rim.vtx')), read_vtx(os.path.join(SURF, 'ao_iface.vtx'))]))
    ann = ann[v[ann] == 0]
    rcc = int(ann[np.argmax(-pts[ann, 1] - pts[ann, 0])])                 # as in 11_site_grid.py
    lv_sep_hi = lv[(np.abs(np.degrees(phi[lv])) <= 45) & (z[lv] >= 0.85) & (z[lv] <= 0.92)]
    H = nearest(lv_sep_hi, pts, pts[rcc])
    Bn = uvc_node(lv, z, phi, z[H] - P['lbb_drop_z'], np.degrees(phi[H]))
    H_rv = nearest(rv, pts, pts[H])
    rbb_low = uvc_node(rv_sep, z, phi, P['mb_z'], float(np.degrees(np.angle(np.exp(1j * phi[rv_sep]).mean()))))
    band = rv_fw[np.abs(z[rv_fw] - P['mb_z']) < 0.03]
    ph_b = np.degrees(phi[band])
    mb_end = int(band[np.argmin(np.abs(ph_b - np.percentile(ph_b, 75)))])  # anterior RV free wall (q75 as in 11)
    rv_apex = uvc_node(rv_sep, z, phi, P['rv_apex_z'], float(np.degrees(phi[rbb_low])))
    # insulated proximal system: paths along the endocardium through the waypoints of each division
    prox, roots = {'lbb': surface_path(gl, H, Bn)}, {'lv': [], 'rv': []}
    for k, wps in P['divisions'].items():
        way = [Bn] + [uvc_node(lv, z, phi, zz, ph) for ph, zz in wps]
        path = [Bn]
        for u, w_ in zip(way[:-1], way[1:]):
            path += surface_path(gl, u, w_)[1:]
        k0 = path.index(way[1])                                  # Durrer site: first junction-bearing point
        prox[f'division_{k}'] = path[:k0 + 1]                    # His side of the Durrer site
        prox[f'division_{k}_post'] = path[k0:]                   # beyond it, to the papillary muscle and apex
        roots['lv'] += budding(pts, path[k0:])
    prox['rbb'] = [H, H_rv] + surface_path(gr, H_rv, rbb_low)[1:]
    prox['moderator_band'] = [rbb_low, mb_end]
    prox['rbb_apical'] = surface_path(gr, rbb_low, rv_apex)
    roots['rv'] += [(mb_end, [rbb_low, mb_end], 3)] + budding(pts, prox['rbb_apical'])[1:]
    # distal trees (one per ventricle, all roots grown together so they repel each other)
    lv_ok = lv[z[lv] <= P['z_max']]
    rv_ok = np.union1d(rv_fw[z[rv_fw] <= P['z_max']], rv_sep[z[rv_sep] <= P['rv_septum_z_max']])
    trees = {}
    for side, allowed, tri in (('lv', lv_ok, tl), ('rv', rv_ok, tr)):
        T = Tree(pts, allowed, vertex_normals(pts, tri, allowed), rng)
        r = []
        for e, path, nbr in roots[side]:
            n0 = T.nrm.get(e)
            if n0 is None:
                continue
            d = pts[path[-1]] - pts[path[-2]]
            d = d - (d @ n0) * n0; d /= np.linalg.norm(d)
            ang = (0.0, 2.1, -2.1) if nbr == 3 else (1.2, -1.2)  # ends: 3 branches 120 deg apart; along a division: 2 side branches
            r.append((e, [d * np.cos(a) + np.cross(n0, d) * np.sin(a) for a in ang]))
        trees[side] = T.grow(r)
        roots[side] = [e for e, _, _ in roots[side] if e in T.nrm]
    # one graph; proximal and distal nodes are kept apart even on the same mesh node (insulation), and are
    # joined only at the roots
    nodes, idx, kind = [], {}, []
    def add(n, k):
        if (n, k) not in idx:
            idx[(n, k)] = len(nodes); nodes.append(n); kind.append(k)
        return idx[(n, k)]
    edges, prox_edges = [], []
    cut = HEART in P['lbbb_cut_hearts']
    for name, path in prox.items():
        for a_, b_ in zip(path[:-1], path[1:]):
            prox_edges.append(((add(a_, 'proximal'), add(b_, 'proximal')), name))
    for side, T in trees.items():
        for i, j in T.edges:
            edges.append((add(T.nodes[i], 'distal_' + side), add(T.nodes[j], 'distal_' + side)))
        for e in roots[side]:
            edges.append((add(e, 'proximal'), add(e, 'distal_' + side)))
    ends = {k: prox[f'division_{k}_post'][-1] for k in P['divisions']}
    # proximal speeds anchored to Durrer 1970: the three LV sites are reached within 0-5 ms of each other and
    # the RV (moderator band end) 5-10 ms after the LV. The shortest His -> Durrer-site path runs at the
    # sourced 2.0 m/s; the others are given the speed that lands them at +offset ms (ASSUMPTION: calibrated,
    # not sourced). Distal network: 2.0 m/s everywhere.
    plen = lambda p_: float(sum(np.linalg.norm(pts[a_] - pts[b_]) for a_, b_ in zip(p_[:-1], p_[1:])))
    v0 = P['v_mm_per_ms']
    L_lbb = plen(prox['lbb'])
    to_site = {k: plen(prox[f'division_{k}']) for k in P['divisions']}
    t_D = min(L_lbb + L for L in to_site.values()) / v0
    speed = {'lbb': v0}
    for k, L in to_site.items():
        speed[f'division_{k}'] = L / (t_D + P['durrer_offset_ms'][k] - L_lbb / v0)
        speed[f'division_{k}_post'] = P['post_site_speed_mm_per_ms'] or speed[f'division_{k}']
    L_rv = plen(prox['rbb']) + plen(prox['moderator_band'])
    for k in ('rbb', 'moderator_band', 'rbb_apical'):
        speed[k] = L_rv / (t_D + P['rv_after_lv_ms'])
    # proximal links get their path's speed (a node shared by two paths keeps both links, each at its speed)
    edge_speed = np.array([speed[nm] for _, nm in prox_edges] + [v0] * len(edges))
    is_lbb = np.array([nm == 'lbb' for _, nm in prox_edges] + [False] * len(edges))
    edges = [e_ for e_, _ in prox_edges] + edges
    nodes, kind, edges = np.array(nodes), np.array(kind), np.array(edges)
    # junctions: distal nodes, terminals first, kept >= spacing apart; spacing set by bisection so that the
    # count matches 15 per cm2 of the area the distal network may cover (Bayer 2025)
    def area(tri, keep):
        t = tri[np.isin(tri, keep).all(1)]
        return 0.5 * np.linalg.norm(np.cross(pts[t[:, 1]] - pts[t[:, 0]], pts[t[:, 2]] - pts[t[:, 0]]), axis=1).sum() / 100.0
    a_lv, a_rv = area(tl, lv_ok), area(tr, rv_ok)
    term = set(trees['lv'].terminals) | set(trees['rv'].terminals)
    distal = np.where(np.char.startswith(kind, 'distal'))[0]
    order = sorted(distal, key=lambda i: (nodes[i] not in term, rng.random()))

    def pick(spacing):
        chosen, grid = [], {}
        for i in order:
            x = pts[nodes[i]]
            c = tuple((x // spacing).astype(int))
            near_ = [j for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                     for j in grid.get((c[0] + dx, c[1] + dy, c[2] + dz), [])]
            if all(np.linalg.norm(pts[nodes[j]] - x) >= spacing for j in near_):
                chosen.append(i); grid.setdefault(c, []).append(i)
        return np.array(sorted(chosen))
    target = P['pmj_per_cm2'] * (a_lv + a_rv)
    lo, hi = 0.3, 6.0
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if len(pick(mid)) < target else (mid, hi)
    spacing = 0.5 * (lo + hi)
    pmj = pick(spacing)
    # coverage
    tn = cKDTree(pts[nodes[distal]])
    cov = {s: round(float(np.median(tn.query(pts[al])[0])), 1) for s, al in (('lv', lv_ok), ('rv', rv_ok))}
    cov_max = {s: float(tn.query(pts[al])[0].max().round(1)) for s, al in (('lv', lv_ok), ('rv', rv_ok))}
    seg = np.linalg.norm(pts[nodes[edges[:, 0]]] - pts[nodes[edges[:, 1]]], axis=1)
    os.makedirs(PK, exist_ok=True)
    # LBBB-like heart: the left bundle is blocked between the His and its branching point (its links removed; nodes
    # kept, so the intact network, used only for the Durrer calibration, has the same indices); LV fascicles and LV
    # distal network intact (see docstring). The distal speed is 2.0 m/s until stage 'durrer' calibrates it.
    keep = ~is_lbb if cut else np.ones(len(edges), bool)
    common = dict(nodes=nodes, kind=kind, pmj=pmj, his=idx[(H, 'proximal')], his_rv=idx[(H_rv, 'proximal')], params=json.dumps(P))
    np.savez(os.path.join(PK, 'network.npz'), edges=edges[keep], edge_speed=edge_speed[keep], **common)
    ni = os.path.join(PK, 'network_intact.npz')
    if cut:
        np.savez(ni, edges=edges, edge_speed=edge_speed, **common)
    elif os.path.exists(ni):
        os.remove(ni)
    summ = {'heart': HEART, 'params': P, 'network_version': P['network_version'], 'lbbb_cut': cut,
            'distal_speed_m_s': None, 'nodes': int(len(nodes)), 'edges': int(keep.sum()),
            'length_mm': {k: round(float(seg[kind[edges[:, 1]] == k].sum()), 1) for k in ('proximal', 'distal_lv', 'distal_rv')},
            'proximal_mm': {k: round(float(sum(np.linalg.norm(pts[a_] - pts[b_]) for a_, b_ in zip(p_[:-1], p_[1:]))), 1)
                            for k, p_ in prox.items()},
            'branches_lv_terminals': len(trees['lv'].terminals), 'branches_rv_terminals': len(trees['rv'].terminals),
            'reconnections': {'lv': trees['lv'].reconnect, 'rv': trees['rv'].reconnect},
            'proximal_speed_m_s': {k: round(float(x), 2) for k, x in speed.items()}, 'his_to_lv_sites_ms': round(t_D, 1),
            'pmj': int(len(pmj)), 'pmj_spacing_mm': round(spacing, 2), 'pmj_lv': int(np.sum(kind[pmj] == 'distal_lv')), 'pmj_rv': int(np.sum(kind[pmj] == 'distal_rv')),
            'allowed_area_cm2': {'lv': round(a_lv, 1), 'rv': round(a_rv, 1)},
            'pmj_per_cm2_of_allowed': {'lv': round(np.sum(kind[pmj] == 'distal_lv') / a_lv, 1),
                                       'rv': round(np.sum(kind[pmj] == 'distal_rv') / a_rv, 1)},
            'gap_to_network_mm_median': cov, 'gap_to_network_mm_max': cov_max,
            'landmarks': {'his': int(H), 'his_z_phi': [round(float(z[H]), 3), round(float(np.degrees(phi[H])), 1)],
                          'lbb_branch': int(Bn), 'his_rv': int(H_rv), 'rbb_low': int(rbb_low), 'mb_end': int(mb_end),
                          'mb_length_mm': round(float(np.linalg.norm(pts[rbb_low] - pts[mb_end])), 1),
                          'fascicle_ends': {k: [int(e), round(float(z[e]), 2), round(float(np.degrees(phi[e])), 1)] for k, e in ends.items()}}}
    json.dump(summ, open(os.path.join(PK, 'summary.json'), 'w'), indent=1)
    print(json.dumps({k: summ[k] for k in summ if k != 'params'}, indent=1))


# ------------------------------------------------------------------ activation
def net_graph(net, pts):
    nodes, edges = net['nodes'], net['edges']
    spd = net['edge_speed'] if 'edge_speed' in net else np.full(len(edges), P['v_mm_per_ms'])
    w = np.maximum(np.linalg.norm(pts[nodes[edges[:, 0]]] - pts[nodes[edges[:, 1]]], axis=1), 1e-6) / spd
    e = np.sort(edges, axis=1)
    keep = e[:, 0] != e[:, 1]
    e, w = e[keep], w[keep]
    key, inv = np.unique(e, axis=0, return_inverse=True)        # duplicates would be summed by the sparse
    wm = np.full(len(key), np.inf)                               # matrix (bug in the first two beats, fixed
    np.minimum.at(wm, inv.ravel(), w)                            # 8 Oct): keep the fastest copy
    n = len(nodes)
    return coo_matrix((np.r_[wm, wm], (np.r_[key[:, 0], key[:, 1]], np.r_[key[:, 1], key[:, 0]])), shape=(n + 1, n + 1))


def hps_times(net, pts, entries, bridges=False):
    """entries: dict network index -> entry time (ms). Returns arrival time at every network node.
    Junctions closer than P['bridge_mm'] are also linked through the muscle (exit 4 ms + straight line at the
    slowest myocardial speed 0.4 m/s + entry 2 ms): a conservative shortcut so the first coupled pass is close;
    the coupling is still iterated against the real eikonal field until it stops changing (see couple())."""
    g = net_graph(net, pts).tocoo()
    n = len(net['nodes'])
    pj = net['pmj']
    pr = np.array(sorted(cKDTree(pts[net['nodes'][pj]]).query_pairs(P['bridge_mm'])))
    if bridges and len(pr):
        wb = P['d_ant_ms'] + np.linalg.norm(pts[net['nodes'][pj[pr[:, 0]]]] - pts[net['nodes'][pj[pr[:, 1]]]], axis=1) / P['v_bridge_mm_per_ms'] + P['d_ret_ms']
        g = coo_matrix((np.r_[g.data, wb, wb], (np.r_[g.row, pj[pr[:, 0]], pj[pr[:, 1]]], np.r_[g.col, pj[pr[:, 1]], pj[pr[:, 0]]])), shape=g.shape)
    src = n
    ii = np.array(list(entries.keys())); tt = np.array(list(entries.values()), dtype=float)
    off = 1e-6                                                 # zero weights are dropped by csgraph
    g = coo_matrix((np.r_[g.data, tt + off], (np.r_[g.row, np.full(len(ii), src)], np.r_[g.col, ii])), shape=g.shape).tocsr()
    return dijkstra(g, indices=src)[:-1] - off


def write_stims(run, net, t_exit, mask):
    """Junction stimuli binned to P['stim_bin_ms']; returns the stim JSON path and counts."""
    sd = os.path.join(run, 'pmj_stims'); os.makedirs(sd, exist_ok=True)
    nodes = net['nodes'][net['pmj']][mask]
    t = np.round(t_exit[mask] / P['stim_bin_ms']) * P['stim_bin_ms']
    out = []
    for k, tb in enumerate(np.unique(t)):
        f = os.path.join(sd, f'pmj_{k:04d}')
        write_vtx(f + '.vtx', nodes[t == tb])
        out.append({'vtx': f, 'start': float(tb)})
    j = os.path.join(run, 'pmj_stims.json')
    json.dump(out, open(j, 'w'))
    return j, len(out), int(mask.sum())


def igb_last(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float)


def eikonal(run_id, extra, ecg_dir, weights):
    """One openCARP eikonal run. 8 Oct: some timed-stimulus runs never converged (openCARP at 100 % CPU for hours;
    8 basal outflow / cusp / summit sites, both -dream.fim.tol 0.001 and 0.01 timed out), so one try with a 6 min
    limit (normal 1.5-3 min); on failure the caller falls back to the combined-graph field (graph_fallback).
    PURK_GRAPH_ONLY=1 skips openCARP (reruns of sites known to hang). Returns True if openCARP finished."""
    if os.environ.get('PURK_GRAPH_ONLY') == '1':
        return False
    args = [sys.executable, os.path.join(B, '12_eikonal.py'), '--mode', 'eik', '--ID', run_id, '--tend', 0, '--np', 2,
            '--no-fast-layer', '--weights', weights, '--ecg-dir', ecg_dir] + extra
    env = dict(os.environ, EIK_FIM_TOL='0.001', EIK_TIMEOUT_S='360')
    with open(os.path.join(REPO, 'runs', run_id, 'driver_12.log'), 'w') as f:
        r = subprocess.run([str(a) for a in args], cwd=B, stdout=f, stderr=subprocess.STDOUT, env=env)
    return r.returncode == 0


def graph_fallback(run_id, Tg, ecg_dir, weights, site_node):
    """Activation from the combined graph itself (graph / k matched openCARP to a median 0.24 ms on the sites that
    finished) when openCARP does not converge: same pseudo-Vm template and fast lead-field ECG as 12_eikonal.py."""
    run = os.path.join(REPO, 'runs', run_id)
    tr = os.path.join(REPO, 'runs', '2026-10-02_biv_fullqrs' if HEART == 'Y5HYEDL4' else f'2026-10-03_{HEART}_fullqrs')
    b = open(os.path.join(tr, 'vm.igb'), 'rb').read(); x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    lat0 = np.loadtxt(os.path.join(tr, 'init_acts_LATs-thresh.dat')); k = int(np.argmin(np.abs(lat0 - 60)))
    vm0 = np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[:, k].astype(float); del b
    tmpl_t = np.arange(len(vm0), dtype=float) - lat0[k]
    tend = float(min(990, max(140, np.ceil((Tg.max() + 20) / 10) * 10)))
    t = np.arange(0, tend + 0.5, 1.0)
    W = np.load(weights)['W'].astype(float)
    ecg = np.zeros((len(t), W.shape[0]))
    for i0 in range(0, len(Tg), 50000):
        sl = slice(i0, i0 + 50000)
        rel = t[:, None] - Tg[None, sl]
        ecg += np.interp(rel.ravel(), tmpl_t, vm0, left=vm0[0], right=vm0[-1]).reshape(rel.shape) @ W[:, sl].T
    os.makedirs(ecg_dir, exist_ok=True)
    for j, l in enumerate(['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']):
        np.savetxt(os.path.join(ecg_dir, f'ECG_{l}.dat'), np.c_[t, ecg[:, j]], fmt='%g %.6g')
    np.save(os.path.join(run, 'act_graph.npy'), Tg.astype(np.float32))
    json.dump({'heart': HEART, 'mode': 'graph_fallback', 'site_node': site_node, 'tend_ms': tend, 'no_fast_layer': True,
               'total_activation_ms': float(Tg.max()), 'unactivated': int(np.isinf(Tg).sum()), 'sim_wall_s': 0.0,
               'template_node': k, 'ecg_dir': ecg_dir, 'files': sorted(os.listdir(run))},
              open(os.path.join(run, 'summary_12.json'), 'w'), indent=1)



def myo_graph(pts):
    """Myocardium as a graph (cached): tet-mesh edges with the eikonal's anisotropic travel time along each edge,
    sqrt((d.f/0.6)^2 + (d.s/0.4)^2 + (d.n/0.48)^2) ms for d in mm, fibre f and sheet s of the element (fast layer
    off, as in the no-fast-layer arm); the fastest element wins on shared edges."""
    f = os.path.join(PK, 'myo_graph.npz')
    if os.path.exists(f):
        d = np.load(f)
        return d['e'].astype(np.int64), d['w'].astype(float)
    E, _ = read_elem(os.path.join(OUT, 'bivF'))
    lon = read_lon(os.path.join(OUT, 'bivF'))
    fb, sh = lon[:, :3], lon[:, 3:6]
    nm = np.cross(fb, sh)
    n = len(pts)
    keys, ws = [], []
    for a_, b_ in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        d = pts[E[:, b_]] - pts[E[:, a_]]
        t = np.sqrt((np.einsum('ij,ij->i', d, fb) / 0.6) ** 2 + (np.einsum('ij,ij->i', d, sh) / 0.4) ** 2
                    + (np.einsum('ij,ij->i', d, nm) / 0.48) ** 2)
        lo, hi = np.minimum(E[:, a_], E[:, b_]), np.maximum(E[:, a_], E[:, b_])
        keys.append(lo * n + hi); ws.append(t)
    key, inv = np.unique(np.concatenate(keys), return_inverse=True)
    w = np.full(len(key), np.inf); np.minimum.at(w, inv.ravel(), np.concatenate(ws))
    e = np.c_[key // n, key % n]
    np.savez(f, e=e.astype(np.int32), w=w.astype(np.float32))
    return e, w


def graph_scale():
    f = os.path.join(PK, 'graph_scale.json')
    return json.load(open(f))['k'] if os.path.exists(f) else 1.0


def solve_combined(net, pts, sources_myo, his=False):
    """Network + myocardium in one directed shortest-path problem: myocardial edges (times / k, k fitted so the
    graph matches openCARP's eikonal, see calib), network links, and at each junction muscle -> network
    (+2 ms) and network -> muscle (+4 ms). Returns myocardial times and network times."""
    e, w = myo_graph(pts)
    w = w / graph_scale()
    N, M = len(pts), len(net['nodes'])
    gn = net_graph(net, pts).tocoo()
    keep = (gn.row < M) & (gn.col < M)
    m = net['nodes'][net['pmj']]
    j = N + net['pmj']
    src = N + M
    rows = [e[:, 0], e[:, 1], N + gn.row[keep], m, j]
    cols = [e[:, 1], e[:, 0], N + gn.col[keep], j, m]
    data = [w, w, gn.data[keep], np.full(len(m), P['d_ret_ms']), np.full(len(m), P['d_ant_ms'])]
    if his:
        rows.append(np.array([src])); cols.append(np.array([N + int(net['his'])])); data.append(np.array([1e-6]))
    if len(sources_myo):
        k_ = np.array(sorted(sources_myo)); rows.append(np.full(len(k_), src)); cols.append(k_)
        data.append(np.array([sources_myo[x] for x in k_]) + 1e-6)
    G = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N + M + 1, N + M + 1)).tocsr()
    d = dijkstra(G, directed=True, indices=src) - 1e-6
    return d[:N], d[N:N + M]


def couple_graph(a, net, pts, site_node, T0=None):
    """One combined graph solve for the junction exit times, then one openCARP eikonal run with the site (if
    paced) and every junction whose network exit is the earliest arrival at its node (within 0.5 ms).
    Diagnostic: network times recomputed from the final openCARP field (no shortcuts) -> largest gain."""
    run = os.path.join(REPO, 'runs', a.ID); os.makedirs(run, exist_ok=True)
    ecg_dir = a.ecg_dir or os.path.join(REPO, 'runs', a.ID + '_ecg', 'POSTPROC_DIR')
    pts_um = read_pts(os.path.join(OUT, 'bivF'))
    srcs = {} if site_node is None else {int(i): 0.0 for i in np.where(np.linalg.norm(pts_um - pts_um[site_node], axis=1) < 1500)[0]}
    Tg, TP = solve_combined(net, pts, srcs, his=site_node is None)
    pn = net['nodes'][net['pmj']]
    t_out = TP[net['pmj']] + P['d_ant_ms']
    mask = t_out - Tg[pn] < 0.5
    sj, nstim, nexit = write_stims(run, net, t_out, mask)
    extra = (['--no-site-stim'] if site_node is None else ['--site-node', site_node]) + ['--stim-json', sj]
    if eikonal(a.ID, extra, ecg_dir, a.weights):
        T, field = igb_last(os.path.join(run, 'act.igb')), 'openCARP eikonal'
    else:
        graph_fallback(a.ID, Tg, ecg_dir, a.weights, site_node)
        T, field = Tg, 'combined graph (openCARP did not converge)'
    ent = dict(zip(net['pmj'].tolist(), (T[pn] + P['d_ret_ms']).tolist()))
    if site_node is None:
        ent[int(net['his'])] = 0.0
    TPc = hps_times(net, pts, ent)
    info = {'method': 'combined graph + 1 openCARP run', 'final_field': field, 'graph_scale_k': graph_scale(), 'pmj_exits': nexit, 'stim_bins': nstim,
            'recheck_max_gain_ms': round(float(np.max(TP - np.minimum(TP, TPc))), 2),
            'graph_vs_opencarp_ms_median_abs': round(float(np.median(np.abs(Tg - T))), 2),
            'graph_total_ms': round(float(Tg.max()), 1)}
    return T, TP, info


def calib(a):
    """Fit k (graph time / openCARP time) on job-1 no-fast-layer fields of a few sites."""
    pts, z, phi, v = load()
    net = dict(np.load(os.path.join(PK, 'network.npz')))
    pts_um = read_pts(os.path.join(OUT, 'bivF'))
    sites = {s_['id']: s_ for s_ in json.load(open(os.path.join(OUT, 'sites.json')))}
    e, w = myo_graph(pts)
    N = len(pts)
    out = {}
    for sid in a.calib_sites:
        node = sites[sid]['node']
        ball = np.where(np.linalg.norm(pts_um - pts_um[node], axis=1) < 1500)[0]
        G2 = coo_matrix((np.r_[w, w, np.full(len(ball), 1e-6)], (np.r_[e[:, 0], e[:, 1], np.full(len(ball), N)],
                         np.r_[e[:, 1], e[:, 0], ball])), shape=(N + 1, N + 1)).tocsr()
        Tg = dijkstra(G2, directed=True, indices=N)[:N]
        To = igb_last(os.path.join(REPO, 'runs', f'2026-10-07_nofast_{HEART}_{sid}', 'act.igb'))
        m_ = To > 20
        out[sid] = {'ratio_median': round(float(np.median(Tg[m_] / To[m_])), 4), 'ratio_p5_p95': np.percentile(Tg[m_] / To[m_], [5, 95]).round(3).tolist(),
                    'total_graph_ms': round(float(Tg.max()), 1), 'total_opencarp_ms': round(float(To.max()), 1)}
    k = float(np.median([x['ratio_median'] for x in out.values()]))
    json.dump({'k': k, 'sites': out}, open(os.path.join(PK, 'graph_scale.json'), 'w'), indent=1)
    print(json.dumps({'k': k, 'sites': out}, indent=1))


def couple(a, net, pts, T_prev, site_node):
    """Iterate network <-> myocardium: entries at T(p) + 2 ms (and the His at 0 for a His-driven beat), network
    times by Dijkstra, exits at T_P(p) + 4 ms where earlier than T(p), one eikonal run; repeat with the new field
    until no network node would be reached more than P['couple_tol_ms'] earlier (max P['max_pass'] runs)."""
    run = os.path.join(REPO, 'runs', a.ID); os.makedirs(run, exist_ok=True)
    pn = net['nodes'][net['pmj']]
    ecg_dir = a.ecg_dir or os.path.join(REPO, 'runs', a.ID + '_ecg', 'POSTPROC_DIR')
    def entries(T):
        e = {} if T is None else dict(zip(net['pmj'].tolist(), (T[pn] + P['d_ret_ms']).tolist()))
        if site_node is None:
            e[int(net['his'])] = 0.0
        return e
    TP = hps_times(net, pts, entries(T_prev))
    log = []
    for k in range(P['max_pass']):
        t_out = TP[net['pmj']] + P['d_ant_ms']
        mask = np.ones(len(t_out), bool) if T_prev is None else t_out < T_prev[pn] - 0.5 * P['stim_bin_ms']
        sj, nstim, nexit = write_stims(run, net, t_out, mask)
        extra = (['--no-site-stim'] if site_node is None else ['--site-node', site_node]) + ['--stim-json', sj]
        eikonal(a.ID, extra, ecg_dir, a.weights)
        T = igb_last(os.path.join(run, 'act.igb'))
        TP_next = hps_times(net, pts, entries(T))
        gain = float(np.max(TP - np.minimum(TP, TP_next)))
        log.append({'pass': k + 1, 'pmj_exits': nexit, 'stim_bins': nstim, 'total_activation_ms': round(float(T.max()), 2),
                    'next_pass_max_gain_ms': round(gain, 3)})
        T_prev, TP = T, np.minimum(TP, TP_next)
        if gain < P['couple_tol_ms']:
            break
    return T, TP, log


def calibrated():
    """v4 networks must be Durrer-calibrated before any beat."""
    s = json.load(open(os.path.join(PK, 'summary.json')))
    if s.get('network_version') == 'v4' and not s.get('distal_speed_m_s'):
        sys.exit(f'network v4 of {HEART} is not Durrer-calibrated yet: run 14_purkinje.py durrer')
    if not os.path.exists(os.path.join(PK, 'graph_scale.json')):
        sys.exit(f'no graph_scale.json in {PK}: run 14_purkinje.py calib first')
    return s


def lv_pct_30(T, lv):
    t1 = T[lv].min()
    return float(np.mean(T[lv] <= t1 + P['durrer_window_ms']) * 100)


def durrer(a):
    """Lowest distal-network speed giving P['durrer_lv_endo_pct'] % of the LV endocardium activated within 30 ms of the
    first LV endocardial activation in the His-driven beat (combined graph; intact network for an LBBB-like heart).
    Bisection to 0.02 m/s; writes the speed into network.npz (and network_intact.npz) and summary.json."""
    if not os.path.exists(os.path.join(PK, 'graph_scale.json')):
        sys.exit(f'no graph_scale.json in {PK}: run 14_purkinje.py calib first')
    if json.load(open(os.path.join(PK, 'summary.json'))).get('network_version') != 'v4':
        sys.exit('durrer applies to network v4 only (build --version v4)')
    pts, z, phi, v = load()
    lv, rv = (read_vtx(os.path.join(SURF, n + '.vtx')) for n in ('lv_endo', 'rv_endo'))
    fi = os.path.join(PK, 'network_intact.npz')
    src = fi if os.path.exists(fi) else os.path.join(PK, 'network.npz')
    net = dict(np.load(src))
    k_ = net['kind']
    def distal(n_):
        return np.char.startswith(k_[n_['edges'][:, 0]], 'distal') & np.char.startswith(k_[n_['edges'][:, 1]], 'distal')
    def beat(vd):
        n2 = dict(net); n2['edge_speed'] = np.where(distal(net), vd, net['edge_speed'])
        return solve_combined(n2, pts, {}, his=True)[0]
    tgt = P['durrer_lv_endo_pct']
    lo, hi = P['v_mm_per_ms'], P['v_distal_max_mm_per_ms']
    log = [(lo, round(lv_pct_30(beat(lo), lv), 1))]
    if log[0][1] >= tgt:
        vd = lo                                                  # sourced 2.0 m/s already meets the target
    else:
        log.append((hi, round(lv_pct_30(beat(hi), lv), 1)))
        if log[-1][1] < tgt:
            sys.exit(f'Durrer target not reached at {hi} m/s: {log}')
        while hi - lo > 0.02:
            mid = 0.5 * (lo + hi)
            p_ = lv_pct_30(beat(mid), lv); log.append((round(mid, 3), round(p_, 1)))
            lo, hi = (mid, hi) if p_ < tgt else (lo, mid)
        vd = round(hi, 2)
    T = beat(vd)
    t1 = T[lv].min()
    chk = {'distal_speed_m_s': vd, 'calibrated_on': os.path.basename(src), 'target_lv_endo_pct_30ms': tgt,
           'lv_endo_pct_30ms': round(lv_pct_30(T, lv), 1), 'lv_endo_first_ms': round(float(t1), 1),
           'rv_endo_first_after_lv_ms': round(float(T[rv].min() - t1), 1),
           'latest_after_lv_onset_ms': round(float(T.max() - t1), 1), 'graph_scale_k': graph_scale(),
           'bisection': log}
    for f in ('network.npz', 'network_intact.npz'):
        p_ = os.path.join(PK, f)
        if os.path.exists(p_):
            n_ = dict(np.load(p_))
            n_['edge_speed'] = np.where(distal(n_), vd, n_['edge_speed'])
            np.savez(p_, **n_)
    sp = os.path.join(PK, 'summary.json')
    s = json.load(open(sp)); s['distal_speed_m_s'] = vd; s['durrer_check'] = chk
    json.dump(s, open(sp, 'w'), indent=1)
    print(json.dumps(chk, indent=1))


def frontal_axis(ecg_dir, t_from, t_to):
    """Least-squares frontal axis over the six limb leads, from net amplitude (max + min) and from area."""
    ang = np.radians([0, 60, 120, -150, -30, 90])
    net, area = [], []
    for l in ('I', 'II', 'III', 'aVR', 'aVL', 'aVF'):
        d = np.loadtxt(os.path.join(ecg_dir, f'ECG_{l}.dat'))
        y = d[:, 1] - d[0, 1]
        m = (d[:, 0] >= t_from) & (d[:, 0] <= t_to)
        net.append(y[m].max() + y[m].min()); area.append(y[m].sum())
    A = np.c_[np.cos(ang), np.sin(ang)]
    out = {}
    for nm, val in (('net', net), ('area', area)):
        c, *_ = np.linalg.lstsq(A, np.array(val), rcond=None)
        out[f'frontal_axis_{nm}_deg'] = round(float(np.degrees(np.arctan2(c[1], c[0]))), 0)
    out['limb_net_mV'] = dict(zip(('I', 'II', 'III', 'aVR', 'aVL', 'aVF'), np.round(net, 2).tolist()))
    return out


def site(a):
    pts, z, phi, v = load()
    net = dict(np.load(os.path.join(PK, 'network.npz')))
    ns = calibrated()
    T, TP, info = couple_graph(a, net, pts, a.site_node)
    log = [info]
    run = os.path.join(REPO, 'runs', a.ID)
    s = json.load(open(os.path.join(run, 'summary_12.json')))
    s.update({'purkinje': True, 'network_version': ns.get('network_version', 'v3'), 'distal_speed_m_s': ns.get('distal_speed_m_s'),
              'lbbb_cut': ns.get('lbbb_cut', False), 'his_ms': round(float(TP[int(net['his'])]), 2), 'coupling': info,
              'pmj_exits': info['pmj_exits']})
    if a.t0_run:                     # no-network field of the same site (job 1), optional since 9 Oct: summary only
        T0 = igb_last(os.path.join(a.t0_run, 'act.igb'))
        pn = net['nodes'][net['pmj']]
        s.update({'t0_run': a.t0_run, 'first_entry_ms': round(float((T0[pn] + P['d_ret_ms']).min()), 2),
                  'total_activation_no_network_ms': round(float(T0.max()), 2)})
    json.dump(s, open(os.path.join(run, 'summary_12.json'), 'w'), indent=1)
    print(json.dumps({k: s[k] for k in ('total_activation_ms', 'total_activation_no_network_ms', 'first_entry_ms', 'his_ms',
                                        'coupling') if k in s}, indent=1))


def sinus(a):
    ns = calibrated()
    pts, z, phi, v = load()
    net = dict(np.load(os.path.join(PK, 'network.npz')))
    T, TP, info = couple_graph(a, net, pts, None)
    log = [info]
    run = os.path.join(REPO, 'runs', a.ID)
    lv, rv = (read_vtx(os.path.join(SURF, n + '.vtx')) for n in ('lv_endo', 'rv_endo'))
    t1 = T.min()
    early = lv[T[lv] <= t1 + 5]
    s = json.load(open(os.path.join(run, 'summary_12.json')))
    lvsep = lv[np.abs(np.degrees(phi[lv])) < 30]; mid = lambda x: x[(z[x] > 0.4) & (z[x] < 0.6)]
    t_epi = cKDTree(pts[read_vtx(os.path.join(SURF, 'epi.vtx'))]); t_lv = cKDTree(pts[lv])
    rvsep = rv[t_lv.query(pts[rv])[0] < t_epi.query(pts[rv])[0]]
    last = int(np.argmax(T))
    ecg_dir = a.ecg_dir or os.path.join(REPO, 'runs', a.ID + '_ecg', 'POSTPROC_DIR')
    s.update(frontal_axis(ecg_dir, t1, T.max() + 3))
    s.update({'network_version': ns.get('network_version', 'v3'), 'distal_speed_m_s': ns.get('distal_speed_m_s'), 'lbbb_cut': ns.get('lbbb_cut', False),
              'lv_endo_pct_30ms': round(lv_pct_30(T, lv), 1), 'latest_after_lv_onset_ms': round(float(T.max() - T[lv].min()), 1)})
    s.update({'his_driven': True, 'coupling': info, 'first_myocardial_ms': round(float(t1), 1), 'total_activation_ms': round(float(T.max()), 1),
              'activation_span_ms': round(float(T.max() - t1), 1),
              'lv_endo_first_ms': round(float(T[lv].min()), 1), 'rv_endo_first_ms': round(float(T[rv].min()), 1),
              'early_lv_endo_5ms_z_phi': np.round(np.c_[z[early], np.degrees(phi[early])][:: max(1, len(early) // 25)], 2).tolist(),
              'mid_septum_lv_side_ms': round(float(np.median(T[mid(lvsep)])), 1),
              'mid_septum_rv_side_ms': round(float(np.median(T[mid(rvsep)])), 1),
              'latest_node_z_phi_v': [round(float(z[last]), 2), round(float(np.degrees(phi[last])), 1), int(v[last])]})
    json.dump(s, open(os.path.join(run, 'summary_12.json'), 'w'), indent=1)
    print(json.dumps({k: v_ for k, v_ in s.items() if k not in ('files', 'early_lv_endo_5ms_z_phi')}, indent=1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['build', 'sinus', 'site', 'calib', 'durrer'])
    p.add_argument('--calib-sites', nargs='+', default=['lv_free_wall_phi180_z0.5_d10', 'lv_free_wall_phi180_z0.5_d90', 'rvot_septal_z_d50'])
    p.add_argument('--ID')
    p.add_argument('--version', default='v3', choices=['v3', 'v4'])
    p.add_argument('--site-node', type=int)
    p.add_argument('--t0-run')
    p.add_argument('--ecg-dir')
    # study lead fields before 10 Oct 2026; the study ECG is now the cb conductor: after new network beats run
    # 15_conductor.py rescore (writes runs/<run>_ecg_cb with ecgW_nofast_cb.npz)
    p.add_argument('--weights', default=os.path.join(OUT, 'ecgW_nofast.npz'))
    a = p.parse_args()
    {'build': lambda: build(a.version), 'sinus': lambda: sinus(a), 'site': lambda: site(a), 'calib': lambda: calib(a), 'durrer': lambda: durrer(a)}[a.stage]()


if __name__ == '__main__':
    main()
