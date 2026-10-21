"""Read-only preview (b) for proposed deviation D22 (lock thread, relayed 20 Oct 2026 22:12 UTC): v5.1's own summit
construction (sims/biv_model/11_site_grid.py, v5 stand-in) with only its anchor changed to 8.3 step 1's LCA ostium.
Report only; nothing enters the manifest.

As 11_site_grid.py, on the merged mesh with the v5.2 (re-solved) UVC: candidate quarter = LV epicardial nodes (v = 0)
with sin(phi) >= 0 and z >= 0.75; B = the candidate within 9.6 +- 1 mm (straight line) of the anchor A nearest the
band's centroid; the sector = candidates within 18.9 mm of B and farther from A than B; superior = closer than the
14.0 mm GCV proxy arc (18.9 x 14.0 / 18.9), inferior-lateral beyond; one position per area mid-way radially (7.0 and
16.45 mm from B), the band node nearest that radius in the direction of the band's centroid; depths 0.1 / 0.5 / 0.75 /
0.9 counted from the endocardial end along v5.1's inward line (face normals within 4 mm, 0.2 mm marching, 0.9 mm
tolerance), no node shared with another site. A = the LCA ostium of sites52.py (aortic root outer surface, theta 56.2
deg in the D15 frame, 14.8 mm above the aortic mid-plane).
Reports: both areas non-empty and on tag 1; the sector's apex angle at B (angular extent of the sector in B's tangent
plane) and area against Kuniewicz (85.46 +- 15.94 deg; 287.38 +- 144.95 mm2); the superior area share (Kuniewicz 0.545;
v5.1's arc 0.549); moves of B and of each site from v5.1's; 8.4's straight-line distances to the tip B.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_d22.py [HEART ...]
"""
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
from common import read_elem, read_pts, read_vtx                                            # noqa: E402

BIF_D, SUMMIT_R, GCV_FRAC = 9.6, 18.9, 14.0 / 18.9
STEP, OUT_TOL = 0.2, 0.9
DEPTHS = (0.10, 0.50, 0.90, 0.75)
VARIANT = os.environ.get('D22_VARIANT', 'D22')        # 'D22' as proposed, or 'projB' (reported alternative)


def construct(h, variant=VARIANT, used=None, s52sum=None):
    """The construction; returns the record. used / s52sum: sites52.py passes its own (the build); else read from files."""
    VARIANT = variant
    B_ = os.path.join(G.REPO, 'data', 'biv', h); V = os.path.join(B_, 'v52'); S = os.path.join(V, 'surfaces')
    pts = read_pts(os.path.join(V, 'biv52')) / 1e3; E, tg = read_elem(os.path.join(V, 'biv52'))
    nod = np.fromfile(os.path.join(V, 'biv52.nod'), dtype=np.int64)
    z, phi, v = (np.loadtxt(os.path.join(V, 'uvc', n + '.dat')) for n in ('z', 'phi', 'v'))
    epi = read_vtx(os.path.join(S, 'epi.vtx'))
    s52 = {'summit_reanchored': s52sum} if s52sum is not None else json.load(open(os.path.join(HERE, f'sites52_{h}.json')))
    Afull = int(s52['summit_reanchored']['ostium_full_node'])
    Pfull, _, _ = G.load_full(h)
    A = Pfull[Afull]
    tree = cKDTree(pts)
    surf = lambda n: np.loadtxt(os.path.join(S, n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    faces = np.vstack([surf(n) for n in ('lv_endo', 'rv_endo', 'epi')])
    fx = pts[faces]; fn = np.cross(fx[:, 1] - fx[:, 0], fx[:, 2] - fx[:, 0]); t_fc = cKDTree(fx.mean(1))
    inside = lambda x: tree.query(x)[0] <= OUT_TOL

    def line(p):
        idx = t_fc.query_ball_point(pts[p], 4.0)
        nvec = fn[idx]; nvec = nvec * np.sign(nvec @ nvec[0])[:, None]
        n = nvec.sum(0); n /= np.linalg.norm(n)
        if not inside(pts[p] + 1.0 * n):
            n = -n
        s, outside, last = 0.0, 0, 0.0
        while s < 60.0:
            s += STEP
            if inside(pts[p] + s * n):
                outside, last = 0, s
            else:
                outside += 1
                if outside >= 2:
                    break
        return n, last
    cand = epi[(v[epi] == 0) & (np.sin(phi[epi]) >= 0) & (z[epi] >= 0.75)]
    band = cand[np.abs(np.linalg.norm(pts[cand] - A, axis=1) - BIF_D) < 1.0]
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'variant': VARIANT, 'anchor_A': {'full_node': Afull, 'mm': A.round(3).tolist()},
           'candidate_quarter_nodes': int(len(cand)), 'band_9.6mm_nodes': int(len(band)),
           'A_to_nearest_candidate_mm': round(float(np.linalg.norm(pts[cand] - A, axis=1).min()), 2)}
    out_json = os.path.join(HERE, f'preview_d22{"" if VARIANT == "D22" else "_" + VARIANT}_{h}.json')
    if VARIANT == 'D22':
        if not len(band):
            rec['stop'] = 'no candidate node 9.6 +- 1 mm from the anchor (D22 acceptance fails in this heart)'
            rec['_B_xyz'] = None; rec['_out_json'] = out_json
            return rec
        bif = int(band[np.argmin(np.linalg.norm(pts[band] - pts[band].mean(0), axis=1))])
    else:
        # variant "projB": B = the candidate nearest 8.3 step 2's bifurcation point (9.59 mm along the outer surface from the ostium)
        Bg = Pfull[int(s52['summit_reanchored']['bifurcation_full_node'])]
        bif = int(cand[np.argmin(np.linalg.norm(pts[cand] - Bg, axis=1))])
        rec['projB'] = {'step2_point_full_node': int(s52['summit_reanchored']['bifurcation_full_node']),
                        'projection_distance_mm': round(float(np.linalg.norm(pts[bif] - Bg)), 2)}
    Bp = pts[bif]; dAB = float(np.linalg.norm(Bp - A))
    dB = np.linalg.norm(pts[cand] - Bp, axis=1); dA = np.linalg.norm(pts[cand] - A, axis=1)
    insec = (dB <= SUMMIT_R) & (dA > dAB)
    sector, dS = cand[insec], dB[insec]
    r_gcv = SUMMIT_R * GCV_FRAC
    epi_tri = surf('epi')
    def area(nodes):
        x = pts[epi_tri[np.isin(epi_tri, nodes).all(1)]]
        return float(0.5 * np.linalg.norm(np.cross(x[:, 1] - x[:, 0], x[:, 2] - x[:, 0]), axis=1).sum())
    sup, inf = sector[dS < r_gcv], sector[dS >= r_gcv]
    a_all, a_sup, a_inf = area(sector), area(sup), area(inf)
    # apex angle: angular extent of the sector around B in B's tangent plane
    near = epi_tri[np.isin(epi_tri, [bif]).any(1)]
    nB = np.cross(pts[near[:, 1]] - pts[near[:, 0]], pts[near[:, 2]] - pts[near[:, 0]]).sum(0); nB /= np.linalg.norm(nB)
    e1 = (pts[sector] - Bp).mean(0); e1 -= (e1 @ nB) * nB; e1 /= np.linalg.norm(e1); e2 = np.cross(nB, e1)
    d = pts[sector] - Bp; ang = np.degrees(np.arctan2(d @ e2, d @ e1))
    angs = np.sort(ang); gaps = np.diff(np.r_[angs, angs[0] + 360]); extent = 360 - gaps.max()
    tag1 = np.zeros(len(pts), bool); tag1[np.unique(E[tg == 1])] = True
    rec.update({'bifurcation_B': {'node': bif, 'dist_A_mm': round(dAB, 2)},
                'sector_nodes': int(len(sector)), 'superior_nodes': int(len(sup)), 'inferior_lateral_nodes': int(len(inf)),
                'sector_area_mm2 (Kuniewicz 287.38 +- 144.95)': round(a_all, 1), 'superior_area_share (Kuniewicz 0.545; v5.1 arc 0.549)': round(a_sup / a_all, 3) if a_all else None,
                'sector_apex_angle_deg (Kuniewicz 85.46 +- 15.94)': round(float(extent), 1),
                'all_sector_nodes_on_tag1': bool(tag1[sector].all()), 'sector_nodes_not_on_tag1': int((~tag1[sector]).sum())})
    v51 = json.load(open(os.path.join(B_, 'sites.json')))
    if used is None:
        used = {int(s['node']) for s in v51} | {int(s['node']) for s in json.load(open(os.path.join(V, 'sites52.json')))['new_sites']}
    used = set(used)
    s11 = json.load(open(os.path.join(B_, 'summary_11.json')))
    b51 = int(s11['summit_v5']['bifurcation_node'])
    rec['bifurcation_B']['moved_from_v51_B_mm'] = round(float(np.linalg.norm(Bp - pts[b51])), 2)
    old = {(s['position'], s['depth_target']): s for s in v51 if s['family'] == 'lv_summit'}
    sites, pos = [], {}
    for area_nm, m in (('superior', dS < r_gcv), ('inferior_lateral', dS >= r_gcv)):
        if m.sum() == 0:
            pos[area_nm] = None; continue
        r_mid = r_gcv / 2 if area_nm == 'superior' else (r_gcv + SUMMIT_R) / 2
        bnd = sector[m][np.abs(dS[m] - r_mid) < 2.0]
        bnd = bnd if len(bnd) else sector[m]
        c = pts[bnd].mean(0)
        tgt = Bp + r_mid * (c - Bp) / np.linalg.norm(c - Bp)
        p = int(bnd[np.argmin(np.linalg.norm(pts[bnd] - tgt, axis=1))])
        n_in, T = line(p)
        po = old.get((area_nm, 0.5))
        pos[area_nm] = {'surface_node': p, 'on_tag1': bool(tag1[p]), 'dist_B_mm': round(float(np.linalg.norm(pts[p] - Bp)), 2),
                        'wall_thickness_mm': round(float(T), 2),
                        'moved_from_v51_surface_mm': round(float(np.linalg.norm(pts[p] - pts[int(po['surface_node'])])), 2) if po else None}
        for dt in DEPTHS:
            x = pts[p] + (1 - dt) * T * n_in
            node = next(int(cc) for cc in tree.query(x, k=12)[1] if int(cc) not in used)
            used.add(node)
            o = old.get((area_nm, dt))
            sites.append({'id': f'lv_summit52_{area_nm}_d{int(dt * 100)}', 'node': node, 'depth_target': dt,
                          'moved_from_v51_mm': round(float(np.linalg.norm(pts[node] - pts[int(o['node'])])), 2) if o else None,
                          'dist_to_tip_B_mm (8.4)': round(float(np.linalg.norm(pts[node] - Bp)), 2)})
    rec['positions'] = pos
    rec['sites (preview, not in the manifest)'] = sites
    rec['acceptance_both_areas_non_empty_and_on_tag1'] = bool(pos.get('superior') and pos.get('inferior_lateral') and len(sup) and len(inf)
                                                             and pos['superior']['on_tag1'] and pos['inferior_lateral']['on_tag1'])
    rec['steps_2_6_sliver (sites52)'] = {k: s52['summit_reanchored'][k] for k in ('apex_angle_deg (Kuniewicz 85.46 +- 15.94)', 'triangle_area_mm2 (Kuniewicz area 287 +- 145)', 'lcx_side_mm (G->B)')}
    rec['_B_xyz'] = Bp.tolist(); rec['_out_json'] = out_json
    return rec


def run(h):
    rec = construct(h)
    out_json = rec.pop('_out_json'); rec.pop('_B_xyz')
    G.dump(rec, out_json)
    if 'stop' in rec:
        print(h, rec['stop'], rec['A_to_nearest_candidate_mm']); return
    print(h, VARIANT, {k: rec[k] for k in ('sector_area_mm2 (Kuniewicz 287.38 +- 144.95)', 'superior_area_share (Kuniewicz 0.545; v5.1 arc 0.549)',
                                  'sector_apex_angle_deg (Kuniewicz 85.46 +- 15.94)', 'acceptance_both_areas_non_empty_and_on_tag1')},
          'B moved', rec['bifurcation_B'], flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
