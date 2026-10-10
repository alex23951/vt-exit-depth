#!/usr/bin/env python
"""
Step 11 (v2, 2026-10-03; v5, 2026-10-07): pre-registered exit-site grid for one heart (selection only).

v5 changes (Alex's answers of 4 Oct 2026, "all recommended" 22:22 UTC; summit numbers from
Kuniewicz et al. 2023, Folia Morphol 82:291-299, Table 1):
  - a 75 % depth target at every position (placed after all other sites, so the 10 / 50 / 90 %
    nodes of unchanged positions stay the same as in v3);
  - LV summit stand-in rebuilt around a left-main bifurcation proxy (see "LV summit" below);
  - Daniels-territory positions (family lv_vein_course): proximal AIV and two basal-ring (GCV)
    positions, plus a vein-adjacent flag for every site (coronary-vein proxies below);
  - aortic-cusp sites get their own study region (region_study = aortic_cusp, epi_endo_truth =
    False); their bazan_region is unchanged so the package scores them as before;
  - the phi -150 positions are named "mid inferolateral" and "basal inferolateral".

Surface positions (33 per heart; 99 sites with 3 depths):
  LV            3 levels (z = 0.25 / 0.50 / 0.75) x 6 rotational positions (UVC phi = 0, +-60,
                +-120, 180 deg; phi 0 = direction of the RV cavity = septal centre, +90 = anterior).
                Positions within +-60 deg whose endocardial point is nearer the RV endocardium
                than the epicardium are septal (wall = septum, LV endo -> RV endo).
  RV free wall  3 levels x 3 positions (25th / 50th / 75th percentile of the free-wall phi range).
  RVOT          2: RV endocardium in the outflow tract (Doste weight w < 0.3), 8-15 mm below the
                pulmonary rim, septal side (nearest the aortic interface) and free-wall side.
  LV summit     2: one in the superior and one in the inferior/lateral area (see below).
  Aortic-cusp region 2: LV muscle at the aortic annulus under the right / left coronary cusp
                (most anterior-rightward / most leftward-posterior annulus point; the meshes have
                no cusps, so these are annular LV muscle sites).

Depth placement (v2; v3 2026-10-04 adds the free-wall rule below): from the surface point p, a line is cast along the inward wall normal
(area-weighted normal of the surface triangles within 4 mm of p) and marched in 0.2 mm steps
until it leaves the tissue (nearest mesh node > 0.9 mm away for 2 steps). Its length is the
local wall thickness T (mm). The site for target depth d (fraction from the endocardium; for
the summit, which starts on the epicardium, d is still counted from the endocardial end) is the
nearest mesh node to p + d T n not already used by another site, so no two sites share a node.
v3 inferolateral rule (Alex's pending choice, coordinator 2026-10-04: options a + d): apical
(z 0.25) keeps phi -120 with the re-aimed line below; mid and basal step phi laterally from -120
in 15 deg steps (-135, -150, -165) to the first phi whose straight line from the LV endocardium
ends on the LV free-wall epicardium (v = 0), with wall thickness inside the range of the heart's
other LV free-wall positions and the 50 % point at mid-wall (rho 0.3-0.7); stop if none passes.
Depth tolerance 0.05.
v3 rule: for LV free-wall positions, if the normal line does not end on the LV free-wall
epicardium (v = 0) - in Y5HYEDL4 the inferolateral line ran into the inferior septum - the
line is re-aimed at the nearest LV free-wall epicardial node whose straight segment stays in
the tissue and on the LV side; T is that segment's length. Septal lines are checked to end on
the RV endocardium (reported only). line_rule records which rule each site used.
Achieved depth = projection of that node on the line, as a fraction and in mm; the node's
distance from the line is recorded too. Flags (sites are kept, not hidden):
  thin_wall      T < 3 mean edge lengths: 10 / 50 / 90 % cannot be resolved on this mesh
  depth_miss     achieved depth more than 0.15 from the target
  off_line       node more than 1.5 mm from the line

LV summit (Yamada et al. 2010, Circ Arrhythm Electrophysiol 3:616): LV epicardium near the
left main bifurcation, bounded by an arc from the LAD (above the first septal perforator) to
the LCx; the great cardiac vein (GCV) bisects it into a superior (inaccessible) and an
inferior/lateral (accessible) area. The meshes have no coronary vessels, so this script uses a
PROXY. v5 (2026-10-07) replaces v2's unsourced 30 / 15 mm with Kuniewicz 2023 Table 1 means:
  A  left-coronary-sinus proxy = the most leftward-posterior point of the aortic annulus (same
     point as the aortic-cusp LCC site; the meshes have no cusps or sinuses)
  candidate quarter  LV epicardium (v = 0), anterior/lateral half (sin phi >= 0), z >= 0.75
  B  bifurcation proxy: candidate node BIF_D = 9.6 mm (+-1) from A (ostium-bifurcation 9.59 mm),
     the one nearest the centroid of that band (ASSUMPTION: the left main's direction is not
     known on these meshes, so B is the middle of the band)
  summit sector  candidate nodes within SUMMIT_R = 18.9 mm of B (bifurcation-first septal
     18.92 mm) and distal to the bifurcation (farther from A than B is). The quarter's own
     edges then bound it like the two arteries: the LV-RV epicardial junction (AIV/LAD side) and
     the basal edge (AV groove/LCx side). A flat 85.46 deg wedge (Kuniewicz bifurcation angle) of
     18.9 mm would be 266 mm2 (Kuniewicz area 287 +- 145 mm2); the mesh area is reported in
     summary_11.json. ASSUMPTION, checked on Y5HYEDL4 on 7 Oct: a +-42.5 deg cut around the A->B
     line gave 50 mm2 (A->B runs along the base); the disc without the distal rule gave 548 mm2
     and put the superior site 3.9 mm from the annulus.
  GCV proxy arc  14.0 mm from B (= 18.9 x 0.741), which splits a flat sector in the mean
     superior:inferior area ratio 145.6:121.7 (the arc shape is an ASSUMPTION)
  sensitivity  summit_r13.7 / _r18.9 / _r24.1 per site (+-1 SD radius, arc scaled the same way)
  one position per area, mid-way radially (7.0 mm and 16.45 mm from B, +-2 mm): the band node
  nearest the point at that radius in the direction of the band's centroid; with the distal rule
  the superior site sits farther from A than B, off the annulus (dist_annulus_mm is recorded).
Each site also gets its straight-line distance to A ("distance to the left sinus") and to B.

Coronary-vein proxies (v5, for Daniels 2006: all 12 epicardial cases were perivascular, AIV-GCV
junction 3, proximal AIV 4, GCV 2, MCV 3) on the epicardium, no vessels in the meshes:
  AIV / MCV  LV epicardial nodes within 2 mm of RV epicardium, anterior (sin phi > 0) /
             posterior (sin phi < 0) interventricular groove
  GCV        LV epicardium 4-6 mm below the basal epicardial edge (AV-plane interface), i.e.
             along the left AV groove, plus the summit GCV arc (14.0 +- 1 mm from B)
  vein_adjacent  the position's epicardial end lies within VEIN_ADJ_MM = 5 mm of a vein proxy
             (ASSUMPTION: Daniels gives no distance; vein_dist_mm is kept so it can be changed)
  lv_vein_course positions (epicardial start, depth still counted from the endocardial end):
             proximal_aiv (AIV proxy at z 0.75), basal_ring_anterolateral / basal_ring_lateral
             (GCV band nearest phi 120 / 180).

Names come from the UVCs (anatomical, not torso axes): LV 0 septal, +60 anteroseptal,
+120 anterolateral, 180 lateral, -120 inferolateral, -60 inferoseptal; RV free wall
anterior (phi > 20), inferior (phi < -20), otherwise lateral; level apical / mid / basal.
Bazan region (UVC, from the surface point so the three depths of a position share it):
basal if z >= 0.5 else apical (the z = 0.5 level is flagged
level_boundary); superior if sin(phi) >= 0 (anterior half incl. septal centre and lateral),
else inferior; RVOT -> rvot; summit and cusp sites -> lv_basal_superior. The v1 (torso-axis)
region is kept as bazan_region_v1 for comparison.

Writes data/biv/<HEART>/sites.json / sites.csv (v1 kept as sites_v1.json).
"""

import csv
import json
import os

import numpy as np
from scipy.spatial import cKDTree

from common import HEART, OUT, REPO, read_elem, read_pts, read_vtx

SURF = os.path.join(OUT, 'surfaces')
UVC = os.path.join(OUT, 'uvc')
LEVELS = (0.25, 0.50, 0.75)
LV_PHI = (0, 60, 120, 180, -120, -60)
LV_NAMES = {0: 'septal', 60: 'anteroseptal', 120: 'anterolateral', 180: 'lateral',
            -120: 'inferolateral', -60: 'inferoseptal'}
DEPTHS = (0.10, 0.50, 0.90)            # placed first at every position (v3 nodes unchanged)
DEPTH_75 = 0.75                         # v5: placed in a second pass after all other sites
BIF_D, SUMMIT_R = 9.6, 18.9              # mm (Kuniewicz 2023 Table 1 means)
SUMMIT_R_ALL = (13.7, 18.9, 24.1)       # +-1 SD sensitivity radii
GCV_FRAC = 14.0 / 18.9                  # GCV proxy arc radius / summit radius
VEIN_ADJ_MM, GROOVE_MM = 5.0, 2.0       # vein-adjacent distance; LV-RV epicardial junction width
GCV_BAND = (4.0, 6.0)                   # mm below the basal epicardial edge
STEP, OUT_TOL = 0.2, 0.9                # mm
DEPTH_TOL = 0.05                        # v3: achieved depth within 0.05 of target (mesh limit ~1 mm elements)
INFLAT_STEPS = (-120, -135, -150, -165) # v3: inferolateral search at mid / basal level


def vtx(n):
    return read_vtx(os.path.join(SURF, n + '.vtx'))


def surf(n):
    return np.loadtxt(os.path.join(SURF, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)


def main():
    pts = read_pts(os.path.join(OUT, 'bivF')) / 1e3                      # mm, heart frame (CT, LPS)
    E, _ = read_elem(os.path.join(OUT, 'bivF'))
    h = float(np.mean(np.linalg.norm(pts[E[:, 0]] - pts[E[:, 1]], axis=1)))   # mean edge (sample)
    z, phi, rho, sep, v = (np.loadtxt(os.path.join(UVC, n + '.dat')) for n in ('z', 'phi', 'rho', 'sep', 'v'))
    w = np.clip(np.loadtxt(os.path.join(OUT, 'laplace', 'w.dat')), 0, 1)
    lv, rv, epi = vtx('lv_endo'), vtx('rv_endo'), vtx('epi')
    tree = cKDTree(pts)
    t_epi, t_lv, t_rv = cKDTree(pts[epi]), cKDTree(pts[lv]), cKDTree(pts[rv])
    old = {s['id']: s for s in json.load(open(os.path.join(OUT, 'sites_v1.json')))} \
        if os.path.exists(os.path.join(OUT, 'sites_v1.json')) else {}

    # area-weighted face normals of every boundary surface, keyed by face centroid
    faces = np.vstack([surf(n) for n in ('lv_endo', 'rv_endo', 'epi')])
    fx = pts[faces]
    fn = np.cross(fx[:, 1] - fx[:, 0], fx[:, 2] - fx[:, 0])               # length = 2 area
    fc = fx.mean(1)
    t_fc = cKDTree(fc)

    def inside(x):
        return tree.query(x)[0] <= OUT_TOL

    def line(p):
        """Inward unit normal at node p and wall thickness along it."""
        idx = t_fc.query_ball_point(pts[p], 4.0)
        nvec = fn[idx]
        nvec = nvec * np.sign(nvec @ nvec[0])[:, None]                   # consistent orientation
        n = nvec.sum(0); n /= np.linalg.norm(n)
        if not inside(pts[p] + 1.0 * n):                                 # point inwards
            n = -n
        s, outside = 0.0, 0
        last = 0.0
        while s < 60.0:
            s += STEP
            if inside(pts[p] + s * n):
                outside, last = 0, s
            else:
                outside += 1
                if outside >= 2:
                    break
        return n, last

    used = set()
    sites = []

    def anat_name(family, level, pos, p):
        lev = '' if level == '' else ('apical' if level < 0.35 else 'mid' if level < 0.65 else 'basal')
        if family == 'lv_free_wall' and pos in ('phi-135', 'phi-150', 'phi-165'):
            seg = 'inferolateral'                               # v5: stepped-out inferolateral positions
        elif family in ('lv_free_wall', 'lv_septum') and int(pos.replace('phi', '')) in LV_NAMES:
            seg = LV_NAMES[int(pos.replace('phi', ''))]
        elif family in ('lv_free_wall', 'lv_septum'):          # shifted position: name from its phi
            ph = np.degrees(phi[p])
            seg = ('septal' if abs(ph) < 30 else 'anteroseptal' if 30 <= ph < 90 else
                   'anterolateral' if 90 <= ph < 150 else 'inferoseptal' if -90 < ph <= -30 else
                   'inferolateral' if -150 < ph <= -90 else 'lateral')
        elif family == 'rv_free_wall':
            ph = np.degrees(phi[p])
            seg = 'anterior' if ph > 20 else 'inferior' if ph < -20 else 'lateral'
        else:
            seg = pos.replace('_', ' ')
        return ' '.join(x for x in (lev, seg, family.replace('_', ' ')) if x)

    def region(family, n):
        if family == 'rvot':
            return 'rvot'
        if family in ('lv_summit', 'aortic_cusp'):
            return 'lv_basal_superior'
        ch = 'rv' if family == 'rv_free_wall' else 'lv'
        return f"{ch}_{'basal' if z[n] >= 0.5 else 'apical'}_{'superior' if np.sin(phi[n]) >= 0 else 'inferior'}"

    epi_fw = epi[v[epi] == 0]                                           # LV free-wall epicardium
    t_epi_fw = cKDTree(pts[epi_fw])
    crossings = []

    def ends_on_lv_epi(p, n_in, T):
        """True if the through-wall line from p ends on the LV free-wall epicardium (v = 0)."""
        end = pts[p] + T * n_in
        d_epi, i = t_epi_fw.query(end)
        return d_epi <= 1.5 and v[epi_fw[i]] == 0

    def free_wall_line(p):
        """v3 rule for LV free-wall positions whose normal line crosses into the septum:
        aim at the nearest LV free-wall epicardial node (v = 0) whose straight segment from p
        stays inside the tissue and on the LV side (v = 0 at the sampled points)."""
        d, idx = t_epi_fw.query(pts[p], k=200)
        for dd, i in zip(d, idx):
            q = epi_fw[i]
            seg = pts[p] + np.linspace(0, 1, max(3, int(dd / STEP)))[:, None] * (pts[q] - pts[p])
            dist, nn = tree.query(seg)
            if (dist <= OUT_TOL).all() and (v[nn] == 0).all():
                return (pts[q] - pts[p]) / dd, float(dd)
        return None, None

    positions = []

    def epi_end(p, n_in, T, epi_start):
        """Epicardial node of the position: p itself, or the end of its through-wall line."""
        if epi_start:
            return int(p)
        d, i = t_epi.query(pts[p] + T * n_in)
        return int(epi[i]) if d <= 1.5 else None

    def position_info(e):
        """Summit and vein-proxy labels of a position, from its epicardial node e."""
        out = {'epi_end_node': e, 'vein_dist_mm': None, 'vein_nearest': None, 'vein_adjacent': False,
               'dist_bifurcation_mm': None}
        out.update({f'summit_r{r}': '' for r in SUMMIT_R_ALL})
        if e is None:
            return out
        dv = {k: float(t.query(pts[e])[0]) for k, t in vein_trees.items()}
        k = min(dv, key=dv.get)
        out.update({'vein_dist_mm': round(dv[k], 1), 'vein_nearest': k, 'vein_adjacent': bool(dv[k] <= VEIN_ADJ_MM),
                    'dist_bifurcation_mm': round(float(np.linalg.norm(pts[e] - B)), 1)})
        for r in SUMMIT_R_ALL:
            out[f'summit_r{r}'] = summit_area(e, r)
        return out

    def add(family, level, pos, p, epi_start=False, extra=None, forced=None):
        n_in, T = line(p)
        rule = 'normal'
        if forced is not None:
            n_in, T, rule = forced
        elif family == 'lv_free_wall' and not ends_on_lv_epi(p, n_in, T):
            crossings.append(f'{family}_{pos}_z{level}')
            n2, T2 = free_wall_line(p)
            if n2 is not None:
                n_in, T, rule = n2, T2, 'to_lv_free_wall_epi'
            else:
                rule = 'normal_crossing_unresolved'
        if family == 'lv_septum':
            end = pts[p] + T * n_in
            if t_rv.query(end)[0] > 1.5:
                crossings.append(f'{family}_{pos}_z{level} (septal line does not end on RV endo)')
        extra = dict(extra or {}, **position_info(epi_end(p, n_in, T, epi_start)))
        positions.append((len(positions), family, level, pos, p, epi_start, extra, n_in, T, rule))
        place(positions[-1], DEPTHS)

    def place(P, depths):
        idx, family, level, pos, p, epi_start, extra, n_in, T, rule = P
        for dt in depths:
            frac_from_p = (1 - dt) if epi_start else dt
            x = pts[p] + frac_from_p * T * n_in
            cand = tree.query(x, k=12)[1]
            node = next(int(c) for c in cand if int(c) not in used)
            used.add(node)
            proj = float((pts[node] - pts[p]) @ n_in)
            off = float(np.linalg.norm((pts[node] - pts[p]) - proj * n_in))
            ach = (1 - proj / T) if epi_start else proj / T if T > 0 else float('nan')
            sid = f'{family}_{pos}_z{level}_d{int(dt * 100)}'
            s = {'id': sid, 'family': family, 'level_z': level, 'position': pos,
                 'name': anat_name(family, level, pos, p), 'depth_target': dt,
                 'depth_achieved': round(float(ach), 3), 'depth_achieved_mm': round(float(ach * T), 2),
                 'wall_thickness_mm': round(float(T), 2), 'off_line_mm': round(off, 2), 'line_rule': rule,
                 'thin_wall': bool(T < 3 * h), 'depth_miss': bool(abs(ach - dt) > DEPTH_TOL),
                 'off_line': bool(off > 1.5), 'node': node, 'surface_node': int(p),
                 'z': float(z[node]), 'phi_deg': float(np.degrees(phi[node])), 'rho': float(rho[node]),
                 'sep': float(sep[node]), 'v': float(v[node]),
                 'bazan_region': region(family, p), 'level_boundary': bool(level == 0.5),
                 'bazan_region_v1': old.get(sid, {}).get('bazan_region'),
                 'region_study': {'aortic_cusp': 'aortic_cusp', 'lv_summit': 'lv_summit', 'rvot': 'rvot',
                                  'lv_vein_course': 'lv_vein_course'}.get(family, region(family, p)),
                 'epi_endo_truth': family != 'aortic_cusp',
                 'dist_left_sinus_mm': round(float(np.linalg.norm(pts[node] - A)), 1),
                 'pos_index': idx}
            s.update(extra or {})
            sites.append(s)

    # left-coronary-sinus proxy A (needed for every site's distance)
    ann = np.unique(np.concatenate([vtx('av_rim'), vtx('ao_iface')]))
    ann = ann[v[ann] == 0]
    lcc = int(ann[np.argmax(pts[ann, 0] + pts[ann, 1])])                 # LPS: +x left, +y posterior
    rcc = int(ann[np.argmax(-pts[ann, 1] - pts[ann, 0])])                # anterior, rightward
    A = pts[lcc]

    # v5 LV summit stand-in (Kuniewicz 2023): bifurcation proxy B and the summit sector
    cand = epi[(v[epi] == 0) & (np.sin(phi[epi]) >= 0) & (z[epi] >= 0.75)]   # candidate quarter
    cand_set = set(cand.tolist())
    band = cand[np.abs(np.linalg.norm(pts[cand] - A, axis=1) - BIF_D) < 1.0]
    if len(band) == 0:
        raise SystemExit('no candidate node 9.6 mm from the left-sinus proxy')
    bif = int(band[np.argmin(np.linalg.norm(pts[band] - pts[band].mean(0), axis=1))])
    B = pts[bif]
    d_AB = float(np.linalg.norm(B - A))

    def summit_area(e, r):
        """'' outside the summit sector of radius r, else 'superior' / 'inferior_lateral'."""
        if e not in cand_set:
            return ''
        d = float(np.linalg.norm(pts[e] - B))
        if d > r or np.linalg.norm(pts[e] - A) <= d_AB:                  # distal to the bifurcation only
            return ''
        return 'superior' if d < r * GCV_FRAC else 'inferior_lateral'

    # v5 coronary-vein proxies on the epicardium
    lv_epi, rv_epi = epi[v[epi] == 0], epi[v[epi] == 1]
    groove = lv_epi[cKDTree(pts[rv_epi]).query(pts[lv_epi])[0] <= GROOVE_MM]
    base_edge = np.intersect1d(np.intersect1d(vtx('avplane_iface'), epi), lv_epi)
    d_edge = cKDTree(pts[base_edge]).query(pts[lv_epi])[0]
    gcv = lv_epi[(d_edge >= GCV_BAND[0]) & (d_edge <= GCV_BAND[1])]
    gcv = np.setdiff1d(gcv, groove)
    d_cand = np.linalg.norm(pts[cand] - B, axis=1)
    arc = np.array([c for c, d in zip(cand, d_cand) if abs(d - SUMMIT_R * GCV_FRAC) < 1.0
                    and summit_area(int(c), SUMMIT_R)], dtype=np.int64)
    veins = {'aiv': groove[np.sin(phi[groove]) > 0], 'mcv': groove[np.sin(phi[groove]) < 0],
             'gcv_av_groove': gcv, 'gcv_summit_arc': arc}
    vein_trees = {k: cKDTree(pts[x]) for k, x in veins.items() if len(x)}

    def lv_start(lev, ph):
        score = np.abs(z[lv] - lev) * 10 + np.abs(np.angle(np.exp(1j * (phi[lv] - np.radians(ph)))))
        return int(lv[np.argmin(score)])

    def candidate_line(p):
        n_in, T = line(p)
        if ends_on_lv_epi(p, n_in, T):
            return n_in, T, 'normal'
        n2, T2 = free_wall_line(p)
        return (n2, T2, 'to_lv_free_wall_epi') if n2 is not None else (None, None, None)

    # thickness range of the other LV free-wall positions (all but phi -120), for the v3 search
    other_T = []
    for lev in LEVELS:
        for ph in LV_PHI:
            if ph == -120:
                continue
            p = lv_start(lev, ph)
            if not (abs(ph) <= 60 and t_rv.query(pts[p])[0] < t_epi.query(pts[p])[0]):
                other_T.append(line(p)[1])
    T_lo, T_hi = min(other_T), max(other_T)
    inflat_log = []

    for lev in LEVELS:                                                   # LV
        for ph in LV_PHI:
            if ph == -120 and lev != 0.25:
                # v3 inferolateral rule (mid / basal): step phi laterally to the first position
                # whose straight line ends on the LV free-wall epicardium with a wall thickness
                # inside the other free-wall positions' range and a mid-wall 50 % point
                chosen = None
                for ph2 in INFLAT_STEPS:
                    p = lv_start(lev, ph2)
                    n_in, T, rule = candidate_line(p)
                    ok = n_in is not None and T_lo <= T <= T_hi
                    mid_rho = float(rho[tree.query(pts[p] + 0.5 * T * n_in)[1]]) if n_in is not None else None
                    ok = ok and mid_rho is not None and 0.3 <= mid_rho <= 0.7
                    inflat_log.append({'level': lev, 'phi_try': ph2, 'wall_mm': None if T is None else round(T, 2),
                                       'rule': rule, 'mid_rho': None if mid_rho is None else round(mid_rho, 3), 'pass': bool(ok)})
                    if ok:
                        chosen = (ph2, p, n_in, T, rule)
                        break
                if chosen is None:
                    raise SystemExit(f'v3 inferolateral search failed at z {lev}: {inflat_log}')
                ph2, p, n_in, T, rule = chosen
                add('lv_free_wall', lev, f'phi{ph2}', p, forced=(n_in, T, rule))
                continue
            p = lv_start(lev, ph)
            septal = abs(ph) <= 60 and t_rv.query(pts[p])[0] < t_epi.query(pts[p])[0]
            add('lv_septum' if septal else 'lv_free_wall', lev, f'phi{ph}', p)
    rv_fw = rv[t_epi.query(pts[rv])[0] < t_lv.query(pts[rv])[0]]          # RV free wall
    for lev in LEVELS:
        band = rv_fw[np.abs(z[rv_fw] - lev) < 0.03]
        ph = np.degrees(phi[band])
        for q in (25, 50, 75):
            p = int(band[np.argmin(np.abs(ph - np.percentile(ph, q)))])
            add('rv_free_wall', lev, f'q{q}', p)
    ao = pts[np.concatenate([vtx('ao_iface'), vtx('av_rim')])]           # RVOT
    d_pv = cKDTree(pts[vtx('pv_rim')]).query(pts[rv])[0]
    ot = rv[(w[rv] < 0.3) & (d_pv > 8) & (d_pv < 15)]
    d_ao = cKDTree(ao).query(pts[ot])[0]
    add('rvot', '', 'septal', int(ot[np.argmin(d_ao)]))
    add('rvot', '', 'free_wall', int(ot[np.argmax(d_ao)]))
    add('aortic_cusp', '', 'rcc', rcc)                                   # aortic-cusp region
    add('aortic_cusp', '', 'lcc', lcc)
    # LV summit (v5 stand-in, Kuniewicz 2023; see docstring)
    t_ann = cKDTree(pts[np.concatenate([vtx('av_rim'), vtx('ao_iface')])])
    epi_tri = surf('epi')

    def sector_area(r):
        sec = np.array([c for c in cand if summit_area(int(c), r)], dtype=np.int64)
        x = pts[epi_tri[np.isin(epi_tri, sec).all(1)]]
        return sec, float(0.5 * np.linalg.norm(np.cross(x[:, 1] - x[:, 0], x[:, 2] - x[:, 0]), axis=1).sum())

    sector, area_mm2 = sector_area(SUMMIT_R)
    dS = np.linalg.norm(pts[sector] - B, axis=1)
    r_gcv = SUMMIT_R * GCV_FRAC
    summit_info = {'summit_region_nodes': int(len(sector)), 'summit_area_mm2': round(area_mm2, 1)}
    for area, m in (('superior', dS < r_gcv), ('inferior_lateral', dS >= r_gcv)):
        if m.sum() == 0:
            print(f'WARNING: empty summit {area} area'); continue
        # mid-way through the area radially from B (7.0 or 16.45 mm): the band node nearest the
        # point r_mid from B in the direction of the band's centroid (the centroid of a curved
        # band lies nearer B, which put the inferior site on the GCV arc on the first try)
        r_mid = r_gcv / 2 if area == 'superior' else (r_gcv + SUMMIT_R) / 2
        band = sector[m][np.abs(dS[m] - r_mid) < 2.0]
        band = band if len(band) else sector[m]
        c = pts[band].mean(0)
        tgt = B + r_mid * (c - B) / np.linalg.norm(c - B)
        p = int(band[np.argmin(np.linalg.norm(pts[band] - tgt, axis=1))])
        add('lv_summit', '', area, p, epi_start=True,
            extra={'summit_area': area, 'summit_area_nodes': int(m.sum()),
                   'dist_annulus_mm': round(float(t_ann.query(pts[p])[0]), 1), **summit_info})
    # Daniels territory (v5): proximal AIV and the basal ring along the GCV proxy
    aiv = veins['aiv']
    near = aiv[np.abs(z[aiv] - 0.75) < 0.02]
    near = near if len(near) else aiv[[int(np.argmin(np.abs(z[aiv] - 0.75)))]]
    p = int(near[np.argmin(np.linalg.norm(pts[near] - pts[near].mean(0), axis=1))])
    add('lv_vein_course', '', 'proximal_aiv', p, epi_start=True, extra={'vein_course': 'aiv'})
    for nm, ph in (('basal_ring_anterolateral', 120), ('basal_ring_lateral', 180)):
        p = int(gcv[np.argmin(np.abs(np.angle(np.exp(1j * (phi[gcv] - np.radians(ph))))))])
        add('lv_vein_course', '', nm, p, epi_start=True, extra={'vein_course': 'gcv_av_groove'})
    for P in list(positions):                                           # v5: 75 % pass
        place(P, (DEPTH_75,))
    sites.sort(key=lambda s: (s['pos_index'], s['depth_target']))

    with open(os.path.join(OUT, 'sites.json'), 'w') as f:
        json.dump(sites, f, indent=1)
    keys = list(dict.fromkeys(k for s in sites for k in s))
    with open(os.path.join(OUT, 'sites.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=keys); wr.writeheader(); wr.writerows(sites)
    fam = {}
    for s in sites:
        fam[s['family']] = fam.get(s['family'], 0) + 1
    summ = {'heart': HEART, 'sites': len(sites), 'unique_nodes': len({s['node'] for s in sites}),
            'by_family': fam, 'mean_edge_mm': round(h, 3),
            'thin_wall': [s['id'] for s in sites if s['thin_wall']],
            'depth_miss': [s['id'] for s in sites if s['depth_miss']],
            'off_line': [s['id'] for s in sites if s['off_line']],
            'crossings_detected': crossings,
            'inferolateral_search': inflat_log, 'other_free_wall_T_range_mm': [round(T_lo, 2), round(T_hi, 2)],
            'line_rule_changed': sorted({s['id'].rsplit('_d', 1)[0] for s in sites if s.get('line_rule') != 'normal'}),
            'bazan_changed': [(s['id'], s['bazan_region_v1'], s['bazan_region']) for s in sites
                              if s['bazan_region_v1'] and s['bazan_region_v1'] != s['bazan_region']],
            'summit_v5': {'bifurcation_node': bif, 'bif_dist_left_sinus_mm': round(float(np.linalg.norm(B - A)), 2),
                          'bif_z': round(float(z[bif]), 3), 'bif_phi_deg': round(float(np.degrees(phi[bif])), 1),
                          'candidate_nodes': int(len(cand)),
                          'sector_area_mm2': {str(r): round(sector_area(r)[1], 1) for r in SUMMIT_R_ALL},
                          'gcv_arc_mm': round(r_gcv, 2),
                          'sites': {s['position']: {'dist_bifurcation_mm': s['dist_bifurcation_mm'],
                                                    'dist_left_sinus_mm': s['dist_left_sinus_mm'],
                                                    'dist_annulus_mm': s['dist_annulus_mm'], 'wall_mm': s['wall_thickness_mm']}
                                    for s in sites if s['family'] == 'lv_summit' and s['depth_target'] == 0.5}},
            'vein_proxy_nodes': {k: int(len(x)) for k, x in veins.items()},
            'vein_adjacent_positions': sorted({s['id'].rsplit('_d', 1)[0] + f" ({s['vein_nearest']} {s['vein_dist_mm']} mm)"
                                               for s in sites if s['vein_adjacent']}),
            'vein_course_sites': {s['position']: {'wall_mm': s['wall_thickness_mm'], 'z': round(s['z'], 2),
                                                  'phi_deg': round(s['phi_deg'], 1), 'bazan_region': s['bazan_region'],
                                                  'summit_r18.9': s['summit_r18.9']}
                                  for s in sites if s['family'] == 'lv_vein_course' and s['depth_target'] == 0.5}}
    json.dump(summ, open(os.path.join(OUT, 'summary_11.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
