"""Audit 06: site grid achieved vs target depth, wall thickness, chamber / surface checks, stimulus-ball reach;
Bazan 2007 region test re-scored with body-superior regions (a05) as a sensitivity. Read only."""
import json
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
OUT = {}
allq = []
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    Ee = np.loadtxt(B + 'biv.elem', skiprows=1, usecols=(1, 2, 3, 4, 5), dtype=np.int64); E, tag = Ee[:, :4], Ee[:, 4]
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    tl, tr, te = cKDTree(P[lv]), cKDTree(P[rv]), cKDTree(P[epi])
    S = pd.read_csv(B + 'sites.csv')
    node_tags = {}
    for n in S.node:
        node_tags[n] = sorted(set(tag[np.any(E == n, axis=1)].tolist()))
    S['dev'] = (S.depth_achieved - S.depth_target).abs()
    S['d_lv'] = tl.query(P[S.node])[0]; S['d_rv'] = tr.query(P[S.node])[0]; S['d_epi'] = te.query(P[S.node])[0]
    S['ball_reaches_endo'] = np.minimum(S.d_lv, S.d_rv) < 1.5; S['ball_reaches_epi'] = S.d_epi < 1.5
    S['tags'] = S.node.map(node_tags)
    fam = {}
    for f, g in S.groupby('family'):
        fam[f] = {'n': len(g), 'max_abs_depth_dev': round(g.dev.max(), 3), 'n_dev_gt_0.05': int((g.dev > 0.05).sum()), 'n_dev_gt_0.15': int((g.dev > 0.15).sum()),
                  'wall_mm_min_median_max': [round(g.wall_thickness_mm.min(), 1), round(g.wall_thickness_mm.median(), 1), round(g.wall_thickness_mm.max(), 1)],
                  'thin_wall_flags': int(g.thin_wall.sum()), 'off_line_flags': int(g.off_line.sum()),
                  'ball_reaches_endo_by_depth': {str(d): int(x.ball_reaches_endo.sum()) for d, x in g.groupby('depth_target')},
                  'ball_reaches_epi_by_depth': {str(d): int(x.ball_reaches_epi.sum()) for d, x in g.groupby('depth_target')},
                  'n_depth_order_violations': int(sum(1 for _, x in g.groupby(['position', 'level_z'], dropna=False) if not np.all(np.diff(x.sort_values('depth_target').depth_achieved_mm.values) > 0)))}
    lvfam = S.family.isin(['lv_free_wall', 'lv_septum', 'lv_summit', 'lv_vein_course', 'aortic_cusp'])
    wrong = S[(lvfam & S.tags.map(lambda t: all(x in (2, 28) for x in t))) | (S.family.isin(['rv_free_wall', 'rvot']) & S.tags.map(lambda t: all(x in (1, 25, 29) for x in t)))]
    worst = S.sort_values('dev', ascending=False).head(8)[['id', 'depth_target', 'depth_achieved', 'wall_thickness_mm', 'line_rule']]
    OUT[h] = {'families': fam, 'sites_whose_node_is_only_in_other_chamber_tags': wrong[['id', 'tags', 'v']].to_dict('records'),
              'worst_depth_deviation': worst.to_dict('records'),
              'v5_75pct_targets_dev': round(S[S.depth_target == 0.75].dev.max(), 3)}
    # Bazan 2007 sensitivity: body-superior regions from a05 (by position, 50 % site)
    lab = pd.read_csv(f'analysis/audit_2026-10-13/a05_site_labels_{h}.csv')
    pos_sup = {i.rsplit('_d', 1)[0]: bool(b) for i, b in zip(lab.id, lab.body_superior_half)}
    d5 = pd.read_csv(f'analysis/v5_adopted_2026-10-13/purk_{h}_v5.csv'); d5 = d5[d5.family != 'his']
    d5['pos'] = d5.id.str.rsplit('_d', n=1).str[0]
    d5['body_sup'] = d5.pos.map(pos_sup)
    d5['heart'] = h
    allq.append(d5)
json.dump(OUT, open('analysis/audit_2026-10-13/a06_sites.json', 'w'), indent=1, default=str)
for h, o in OUT.items():
    print('==', h)
    for f, x in o['families'].items(): print('  ', f, x)
    print('  wrong chamber:', o['sites_whose_node_is_only_in_other_chamber_tags'])
    print('  worst:', o['worst_depth_deviation'][:4])
A = pd.concat(allq)
tf = lambda s: s.astype(str).str.lower().isin(['true', '1', '1.0'])
wall = A.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit']) & A.body_sup.notna()
basal = A.bazan_region.str.contains('basal')
res = {}
for nm, m in (('basal_superior_UVC', A.bazan_region.eq('lv_basal_superior')), ('basal_superior_BODY', basal & A.body_sup.eq(True)),
              ('basal_inferior_UVC', A.bazan_region.eq('lv_basal_inferior')), ('basal_inferior_BODY', basal & A.body_sup.eq(False))):
    x = A[wall & m]
    k9 = int(tf(x[x.depth_target == 0.9].true_q_lead_I).sum()); n9 = int((x.depth_target == 0.9).sum())
    k1 = int(tf(x[x.depth_target == 0.1].true_q_lead_I).sum()); n1 = int((x.depth_target == 0.1).sum())
    i9 = int(tf(x[x.depth_target == 0.9].true_inferior_q_any).sum()); i1 = int(tf(x[x.depth_target == 0.1].true_inferior_q_any).sum())
    res[nm] = {'q_lead_I 90 vs 10': f'{k9}/{n9} vs {k1}/{n1}', 'inferior_Q 90 vs 10': f'{i9}/{n9} vs {i1}/{n1}'}
print(json.dumps(res, indent=1))
json.dump(res, open('analysis/audit_2026-10-13/a06_bazan07_body_regions.json', 'w'), indent=1)
