"""Audit 01: Laplace overshoot (maximum-principle violations) and mesh connectivity. Read only."""
import sys, os, json
import numpy as np
sys.path.insert(0, 'sims/biv_model')
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
out = {}
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    os.environ['HEART'] = h
    base = f'data/biv/{h}/'
    pts = np.loadtxt(base + 'biv.pts', skiprows=1)
    E = np.loadtxt(base + 'biv.elem', skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64)
    tag = E[:, 4]; E = E[:, :4]
    n = len(pts)
    # node connectivity via elements
    r = np.repeat(np.arange(len(E)), 4); c = E.ravel()
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(len(E), n))
    G = (A.T @ A)
    ncomp, lab = connected_components(G, directed=False)
    sizes = np.bincount(lab)
    # element volumes (signed), um^3 -> mm^3
    x = pts[E] / 1e3
    vol6 = np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))
    z = np.loadtxt(base + 'uvc/z.dat')
    res = {'nodes': n, 'elements': len(E), 'components': int(ncomp), 'component_sizes_top5': sorted(sizes.tolist(), reverse=True)[:5],
           'neg_volume_elements': int((vol6 < 0).sum()), 'pos_volume_elements': int((vol6 > 0).sum()),
           'zero_volume_elements(<1e-9 mm3)': int((np.abs(vol6) / 6 < 1e-9).sum()),
           'vol_mm3_min_median': [float(np.abs(vol6).min() / 6), float(np.median(np.abs(vol6)) / 6)],
           'myocardial_volume_ml_all_tags': float(np.abs(vol6).sum() / 6 / 1e3), 'fields': {}}
    edges = np.concatenate([E[:, [0, 1]], E[:, [0, 2]], E[:, [0, 3]], E[:, [1, 2]], E[:, [1, 3]], E[:, [2, 3]]])
    el = np.linalg.norm(pts[edges[:, 0]] - pts[edges[:, 1]], axis=1) / 1e3
    res['edge_mm_min_p5_median_p95_max'] = [float(v) for v in np.percentile(el, [0, 5, 50, 95, 100])]
    for f in ['zeta', 'basal', 'ot', 'w', 'phi_epi', 'phi_lv', 'phi_rv', 'v']:
        u = np.loadtxt(base + f'laplace/{f}.dat')
        bad = (u < -0.01) | (u > 1.01)
        d = {'min': float(u.min()), 'max': float(u.max()), 'n_outside_[-0.01,1.01]': int(bad.sum())}
        if bad.any():
            d['bad_components'] = sorted(set(lab[bad].tolist()))[:10]
            d['bad_in_main_component'] = int((lab[bad] == np.argmax(sizes)).sum())
            d['bad_z_range'] = [float(z[bad].min()), float(z[bad].max())]
            d['bad_nodes_first'] = np.where(bad)[0][:5].tolist()
        res['fields'][f] = d
    # which tags are in small components
    if ncomp > 1:
        main = np.argmax(sizes)
        small_nodes = lab != main
        el_small = small_nodes[E].all(1)
        res['small_component_elements'] = int(el_small.sum())
        res['small_component_tags'] = {int(t): int((tag[el_small] == t).sum()) for t in np.unique(tag[el_small])}
        res['small_component_bbox_mm'] = [(pts[small_nodes].min(0) / 1e3).round(1).tolist(), (pts[small_nodes].max(0) / 1e3).round(1).tolist()]
    out[h] = res
    print(h, json.dumps(res, indent=1), flush=True)
json.dump(out, open('analysis/audit_2026-10-13/a01_laplace_overshoot.json', 'w'), indent=1)
