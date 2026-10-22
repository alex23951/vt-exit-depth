"""Read-only preview P13 (lock thread, relayed 21 Oct 2026 18:55 UTC) for the proposed D33 (report 7's transmural step).
No beat; nothing enters the manifest.

For each v5.1 site, the transmural direction is sites52.py's: the mean element gradient of D19b's APD w (fields52 w_apd)
over the site node's elements, normalised. Two rules for the 4 mm step:
  'as built'  + sense everywhere (the manifest's displaced_transmural sites);
  'proposed'  + sense where the site node's APD w < 0.5, - sense where it is >= 0.5.
Each point is snapped as sites52.py does: the nearest node not used by another site, assigning in v5.1 site order with
the tangential site of each v5.1 site after its transmural one (tangential points as built), starting from every
manifest node except the displaced set. Reports: points outside the myocardium; for the snapped sites the median and
p10 of the move and the count under 3 mm; by depth label and family; sites with APD w within 0.05 of 0.5; for septal
sites (family lv_septum and the rvot_septal sites) the steps whose snapped node lies on the other side of d_s = 0.5.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/02_geometry/preview_p13.py
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom52 as G                                                                          # noqa: E402
import q12measure52 as Q12                                                                  # noqa: E402
from common import read_elem, read_pts                                                      # noqa: E402


def summ(mv, out):
    mv = np.asarray(mv); out = np.asarray(out)
    if not len(mv):
        return None
    return {'n': int(len(mv)), 'outside': int(out.sum()), 'moved_median_mm': round(float(np.median(mv)), 2),
            'moved_p10_mm': round(float(np.percentile(mv, 10)), 2), 'moved_lt_3mm': int((mv < 3).sum())}


def run(h):
    V = os.path.join(G.REPO, 'data', 'biv', h, 'v52'); F52 = os.path.join(V, 'fields52')
    Pm = read_pts(os.path.join(V, 'biv52')) / 1e3; Em, _ = read_elem(os.path.join(V, 'biv52'))
    wapd, ds = np.load(os.path.join(F52, 'w_apd.npy')), np.load(os.path.join(F52, 'd_s.npy'))
    lonv = np.loadtxt(os.path.join(V, 'biv52.lon'), skiprows=1)
    eonm = coo_matrix((np.ones(Em.size), (Em.ravel(), np.repeat(np.arange(len(Em)), 4))), shape=(len(Pm), len(Em))).tocsr()
    cen_all = Pm[Em].mean(1); tree_c = cKDTree(cen_all); tree_m = cKDTree(Pm)

    def in_mesh(x):
        for e in tree_c.query(x, k=24)[1]:
            X = Pm[Em[e]]; lam = np.linalg.solve((X[1:] - X[0]).T, x - X[0])
            if (lam >= -1e-9).all() and lam.sum() <= 1 + 1e-9:
                return True
        return False
    v51 = json.load(open(os.path.join(G.REPO, 'data', 'biv', h, 'sites.json')))
    man = json.load(open(os.path.join(V, 'sites52.json')))['new_sites']
    base_used = {int(x['node']) for x in v51} | {int(x['node']) for x in man if not x['family'].startswith('displaced')}
    built = {x['parent']: x for x in man if x['family'] == 'displaced_transmural'}
    rec = {'heart': h, 'lock_sha256': G.LOCK_SHA}
    rows = {}
    for rule in ('as built', 'proposed'):
        used = set(base_used); out = []
        for sv in v51:
            n0 = int(sv['node']); ee = eonm.indices[eonm.indptr[n0]:eonm.indptr[n0 + 1]]
            gw = Q12.FF.elem_grad(Pm, Em[ee], wapd).mean(0); dtm = gw / max(np.linalg.norm(gw), 1e-30)
            sgn = 1.0 if (rule == 'as built' or wapd[n0] < 0.5) else -1.0
            en = ee[np.argmin(np.linalg.norm(cen_all[ee] - Pm[n0], axis=1))]
            dtg = lonv[en, :3] / np.linalg.norm(lonv[en, :3])
            for kind, dv in (('tm', sgn * dtm), ('tg', dtg)):
                x = Pm[n0] + 4.0 * dv
                node = next(int(c) for c in tree_m.query(x, k=48)[1] if int(c) not in used)
                used.add(node)
                if kind == 'tm':
                    out.append({'id': sv['id'], 'family': sv['family'], 'depth': sv['depth_target'], 'w_apd': float(wapd[n0]), 'sign': sgn,
                                'outside': not in_mesh(x), 'moved': float(np.linalg.norm(Pm[node] - Pm[n0])), 'node': node,
                                'ds0': float(ds[n0]), 'ds1': float(ds[node])})
        rows[rule] = out
        if rule == 'as built':
            rec['as_built_nodes_match_manifest'] = all(built[o['id']]['node'] == o['node'] for o in out)
    for rule, out in rows.items():
        mv = [o['moved'] for o in out]; ou = [o['outside'] for o in out]
        r = {'all': summ(mv, ou), 'by_depth': {}, 'by_family': {}, 'minus_sense_steps': int(sum(o['sign'] < 0 for o in out))}
        for d in (0.1, 0.5, 0.75, 0.9):
            sel = [o for o in out if o['depth'] == d]
            r['by_depth'][str(d)] = summ([o['moved'] for o in sel], [o['outside'] for o in sel])
        for fam in sorted({o['family'] for o in out}):
            sel = [o for o in out if o['family'] == fam]
            r['by_family'][fam] = summ([o['moved'] for o in sel], [o['outside'] for o in sel])
        sep = [o for o in out if o['family'] == 'lv_septum' or 'septal' in o['id']]
        r['septal_sites'] = {'n': len(sep), 'steps_crossing_d_s_0.5 (site node vs snapped node)': int(sum((o['ds0'] - 0.5) * (o['ds1'] - 0.5) < 0 for o in sep)),
                             'of_which_lv_septum': int(sum((o['ds0'] - 0.5) * (o['ds1'] - 0.5) < 0 for o in sep if o['family'] == 'lv_septum'))}
        rec[rule] = r
    w = np.array([o['w_apd'] for o in rows['as built']])
    rec['sites_with_APD_w_within_0.05_of_0.5'] = int((np.abs(w - 0.5) <= 0.05).sum())
    rec['sites_with_APD_w_ge_0.5 (minus sense under the proposal)'] = int((w >= 0.5).sum())
    G.dump(rec, os.path.join(HERE, f'preview_p13_{h}.json'))
    if os.environ.get('P13_SAVE_NODES') == '1':                                              # added 22 Oct: node lists for the D33 check
        G.dump({r: {o['id']: o['node'] for o in out} for r, out in rows.items()}, os.path.join(G.RUN, f'preview_p13_nodes_{h}.json'))
    print(h, json.dumps({k: (v['all'] if isinstance(v, dict) and 'all' in v else v) for k, v in rec.items()}), flush=True)


if __name__ == '__main__':
    for h in sys.argv[1:] or G.HEARTS:
        run(h)
