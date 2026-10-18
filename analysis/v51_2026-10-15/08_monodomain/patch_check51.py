"""In-wall speeds of the graph model and of the two monodomain calibrations, measured the same way on Y5HYEDL4's LV
free-wall patch (27-site monodomain check, step 1; information for Alex's choice of calibration, nothing is tuned here).

Measure = mono_cal51.py speeds() / transit() (the 07_patch_tune measure of 3 Oct): ball of 1.5 mm at the mid-wall node
nearest the patch centre; fibre and in-wall cross-fibre speed = 1 / slope of activation time vs distance for the nodes at
the same depth (|rho - rho_site| < 0.04), 3-10 mm away, within 20 deg of the site's fibre / sheet axis (2 mm bins,
medians); transit = mean time 1 mm minus 7 mm below the epicardium with the whole patch endocardium activated at once.
- graph: the v5.1 tissue graph (heart51.Heart51, tissue only, no network) on the whole heart, read on the patch nodes;
- monodomain, wall-tuned: calibration_Y5HYEDL4.json round 4 (measured there, not rerun);
- monodomain, flat-tuned: params/v51_mono_conductivities.json (mono_slab51.py), run here on the patch
  (runs/v51_2026-10-15/08_monodomain/patch_check/Y5HYEDL4/).
Usage (repo root, venv, PATH with openCARP's mpiexec): python -B analysis/v51_2026-10-15/08_monodomain/patch_check51.py
Writes patch_check51.json in this folder.
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

H = 'Y5HYEDL4'
os.environ['HEART'] = H
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
import mono_cal51 as MC                                                # noqa: E402

MC.RUNS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'patch_check', H)


def geometry():
    pts = np.loadtxt(MC.PATCH + '.pts', skiprows=1)
    nodes = np.load(os.path.join(MC.PD, 'patch_lvfw_nodes.npy'))
    rho = np.loadtxt(os.path.join(MC.UVC, 'rho.dat'))[nodes]
    c = pts.mean(0)
    cand = np.where(np.abs(rho - 0.5) < 0.05)[0]
    site = cand[np.argmin(np.linalg.norm(pts[cand] - c, axis=1))]
    E = np.loadtxt(MC.PATCH + '.elem', skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    lon = np.loadtxt(MC.PATCH + '.lon', skiprows=1)
    touch = np.where((E == site).any(1))[0]
    f = lon[touch, :3].copy(); sv = lon[touch, 3:].copy()
    f[(f @ f[0]) < 0] *= -1; sv[(sv @ sv[0]) < 0] *= -1
    f = f.mean(0); f /= np.linalg.norm(f); sv = sv.mean(0); sv /= np.linalg.norm(sv)
    return pts, nodes, rho, site, f, sv


def in_wall(act, pts, rho, site, f, sv):
    """mono_cal51.speeds() measurement on given activation times."""
    d = pts - pts[site]
    r = np.linalg.norm(d, axis=1) / 1e3
    u = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    same = (np.abs(rho - rho[site]) < 0.04) & (r >= 3) & (r < 10) & (act >= 0)
    out = {}
    for name, ax in (('fibre', f), ('sheet', sv)):
        sel = same & (np.abs(u @ ax) > np.cos(np.radians(20)))
        cen, tb = [], []
        for b0 in np.arange(3, 10.01, 2.0)[:-1]:
            m = sel & (r >= b0) & (r < b0 + 2)
            if m.sum() >= 3:
                cen.append(b0 + 1); tb.append(np.median(act[m]))
        out[name] = float(1 / np.polyfit(cen, tb, 1)[0]) if len(cen) >= 2 else float('nan')
        out[f'n_{name}'] = int(sel.sum())
    return out


def transit_of(act, pts):
    epi = MC.vtx_read(os.path.join(MC.PD, 'patch_lvfw_epi.vtx'))
    dep = cKDTree(pts[epi]).query(pts)[0] / 1e3
    o = {dmm: float(act[(np.abs(dep - dmm) < 0.25) & (act >= 0)].mean()) for dmm in (1.0, 7.0)}
    return o[1.0] - o[7.0]


def main():
    pts, nodes, rho, site, f, sv = geometry()
    out = {'heart': H, 'site_patch_node': int(site), 'site_heart_node': int(nodes[site])}
    import heart51 as H51
    Hh = H51.Heart51(H)
    Tg = Hh.solve(int(nodes[site]), nonet=True)[nodes]
    G = coo_matrix((np.r_[Hh.w, Hh.w], (np.r_[Hh.e[:, 0], Hh.e[:, 1]], np.r_[Hh.e[:, 1], Hh.e[:, 0]])), shape=(Hh.N, Hh.N)).tocsr()
    endo = MC.vtx_read(os.path.join(MC.PD, 'patch_lvfw_lv_endo.vtx'))
    Tt = dijkstra(G, directed=False, indices=nodes[endo], min_only=True)[nodes]
    out['graph'] = in_wall(Tg, pts, rho, site, f, sv) | {'transit_ms': transit_of(Tt, pts)}
    del Hh, G
    print('graph', out['graph'], flush=True)
    wall = json.load(open(os.path.join(HERE, 'calibration_Y5HYEDL4.json')))['history'][-1]
    out['mono_wall_tuned'] = {'conductivities_gi': {a: v[0] for a, v in wall['g'].items()},
                              **{k: wall['measured'][k] for k in ('fibre', 'n_fibre', 'sheet', 'n_sheet', 'transit_ms')}}
    par = json.load(open(os.path.join(REPO, 'params', 'v51_mono_conductivities.json')))['hearts'][H]['conductivities_S_m']
    g = {a: (par[a]['gi'], par[a]['ge']) for a in ('fibre', 'sheet', 'normal')}
    s = MC.speeds(g, '_flat')
    t = MC.transit(g, '_flat')
    out['mono_flat_tuned'] = {'conductivities_gi': {a: v[0] for a, v in g.items()}, **s, **t}
    out['transit_target_ms'] = MC.TARGET['transit_ms']
    json.dump(out, open(os.path.join(HERE, 'patch_check51.json'), 'w'), indent=1)
    for k in ('graph', 'mono_wall_tuned', 'mono_flat_tuned'):
        print(k, {a: round(out[k][a], 3) for a in ('fibre', 'sheet', 'transit_ms')}, flush=True)


if __name__ == '__main__':
    main()
