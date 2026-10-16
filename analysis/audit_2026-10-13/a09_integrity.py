"""Audit 09: results integrity. Numbers claimed in each analysis folder's report / LABNOTES vs recomputation from that
folder's own CSVs (read only). Claimed values typed from the reports; tolerance: 0.5 ms / 0.005 ratio-MDI / 0.01 AUC / 0.15 %."""
import json, os
import numpy as np, pandas as pd
os.chdir('/home/alex/vt-exit-depth/analysis')
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
rows = []
def chk(folder, what, claimed, got, tol):
    ok = all(abs(float(a) - float(b)) <= tol for a, b in zip(np.atleast_1d(claimed), np.atleast_1d(got)))
    rows.append({'folder': folder, 'number': what, 'claimed': claimed, 'recomputed': got, 'match': ok})
def auc(p, n):
    p = np.asarray(p, float); n = np.asarray(n, float); p, n = p[~np.isnan(p)], n[~np.isnan(n)]
    return ((p[:, None] > n[None, :]).sum() + 0.5 * (p[:, None] == n[None, :]).sum()) / (len(p) * len(n))
tf = lambda s: s.astype(str).str.lower().isin(['true', '1', '1.0'])
def lvfw(d, col, fam='lv_free_wall'):
    x = d[d.family == fam]; k = ['position', 'level_z']
    a = x[x.depth_target == 0.9].set_index(k)[col]; b = x[x.depth_target == 0.1].set_index(k)[col]
    j = pd.concat([a.rename('a'), b.rename('b')], axis=1, join='inner'); return j
# --- grids_2026-10-07 / network_three_hearts_2026-10-10 (cb)
cb = {h: pd.read_csv(f'grids_2026-10-07/purk_{h}_cb.csv') for h in H}
chk('network_three_hearts_2026-10-10', 'summit+cusp true QRS median (3 hearts)', [162.5, 134.0, 144.0], [cb[h][cb[h].family.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median() for h in H], 0.5)
chk('network_three_hearts_2026-10-10', 'summit+cusp detected QRS median', [139.5, 122.0, 121.5], [cb[h][cb[h].family.isin(['lv_summit', 'aortic_cusp'])].detected_qrs_duration_ms.median() for h in H], 0.5)
chk('network_three_hearts_2026-10-10', 'LV free wall true QRS median', [165.0, 142.0, 151.5], [cb[h][cb[h].family == 'lv_free_wall'].true_qrs_duration_ms.median() for h in H], 0.5)
chk('network_three_hearts_2026-10-10', 'LV fw 10->90 median QRS change ms', [10.5, 16, 11.5], [(lambda j: (j.a - j.b).median())(lvfw(cb[h], 'true_qrs_duration_ms')) for h in H], 0.5)
for col, cl in (('true_pseudo_delta_ms', [0.76, 0.94, 0.75]), ('true_mdi_daniels', [0.88, 0.80, 0.84]), ('true_idt_v2_ms', [0.44, 0.57, 0.34]), ('true_srs_ms', [0.49, 0.68, 0.50])):
    chk('network_three_hearts_2026-10-10', f'LV fw AUC 90 vs 10 {col}', cl, [round(auc(cb[h][(cb[h].family == 'lv_free_wall') & (cb[h].depth_target == 0.9)][col], cb[h][(cb[h].family == 'lv_free_wall') & (cb[h].depth_target == 0.1)][col]), 2) for h in H], 0.01)
chk('network_three_hearts_2026-10-10', 'RVOT true MDI median', [0.67, 0.59, 0.69], [round(cb[h][cb[h].family == 'rvot'].true_mdi_daniels.median(), 2) for h in H], 0.005)
# --- three_arms_2026-10-08
ta = pd.read_csv('three_arms_2026-10-08/sites.csv')
print('three_arms arms:', ta.arm.unique(), ta.group.unique())
arms = list(ta.arm.unique())
def tam(arm, groups, col='true_qrs_duration_ms'):
    return ta[(ta.arm == arm) & ta.group.isin(groups)][col].median()
netarm = [a for a in arms if 'net' in a.lower() or 'purk' in a.lower()][0]; layer = [a for a in arms if 'layer' in a.lower() and 'no' not in a.lower()] or [a for a in arms if 'normal' in a.lower() or 'fast' in a.lower()]
noarm = [a for a in arms if 'no' in a.lower()][0]
chk('three_arms_2026-10-08', f'summit+cusp true QRS median network / {layer[0] if layer else "?"} / {noarm}', [162.5, 123, 250], [tam(netarm, ['LV summit', 'Aortic cusp']), tam(layer[0], ['LV summit', 'Aortic cusp']) if layer else np.nan, tam(noarm, ['LV summit', 'Aortic cusp'])], 0.5)
chk('three_arms_2026-10-08', 'network LV fw / septum / RV fw / RVOT / vein course true QRS', [165, 143, 151, 146.5, 174.5], [tam(netarm, [g]) for g in ['LV free wall', 'LV septum', 'RV free wall', 'RVOT', 'LV vein course']], 0.5)
# --- nofast_vs_normal_2026-10-07
pr = pd.read_csv('nofast_vs_normal_2026-10-07/pairs.csv')
fw = pr[pr.group == 'LV free wall']
for m, cl in (('normal', [0.96, 0.94, 0.84, 0.79]), ('nofast', [0.54, 0.69, 0.49, 0.62])):
    chk('nofast_vs_normal_2026-10-07', f'{m} LV fw AUC MDI / RS / PdW / IDT', cl, [round(auc(fw[fw.depth_target == 0.9][f'{m}_true_{c}'], fw[fw.depth_target == 0.1][f'{m}_true_{c}']), 2) for c in ('mdi_daniels', 'srs_ms', 'pseudo_delta_ms', 'idt_v2_ms')], 0.01)
nf = pd.read_csv('grids_2026-10-07/nofast_Y5HYEDL4.csv'); nw = pd.read_csv('grids_2026-10-07/new_Y5HYEDL4.csv')
chk('nofast_vs_normal_2026-10-07', 'LV fw 10->90 median QRS change normal / no layer (ms)', [13.5, 4.5], [(lambda j: (j.a - j.b).median())(lvfw(nw, 'true_qrs_duration_ms')), (lambda j: (j.a - j.b).median())(lvfw(nf, 'true_qrs_duration_ms'))], 0.5)
# --- rvot_diag_2026-10-12
rd = pd.read_csv('rvot_diag_2026-10-12/sites.csv')
g = lambda h, grp, c: rd[(rd.heart == h) & (rd.group == grp)][c].median()
print('rvot_diag groups', rd.group.unique())
chk('rvot_diag_2026-10-12', 'RVOT true QRS median', [146, 140, 138], [g(h, 'rvot', 'true_qrs_ms') for h in H], 0.5)
chk('rvot_diag_2026-10-12', 'RVOT MDI true median', [0.67, 0.59, 0.69], [round(g(h, 'rvot', 'mdi_true'), 2) for h in H], 0.005)
chk('rvot_diag_2026-10-12', 'RVOT first junction ms median', [24.1, 10.9, 28.2], [g(h, 'rvot', 'first_junction_ms') for h in H], 0.15)
chk('rvot_diag_2026-10-12', 'RVOT vs cb CSV MDI (all RVOT sites)', [round(cb[h][cb[h].family == 'rvot'].true_mdi_daniels.median(), 3) for h in H], [round(g(h, 'rvot', 'mdi_true'), 3) for h in H], 0.006)
bz = pd.read_csv('rvot_diag_2026-10-12/bazan.csv'); print(bz[['heart', 'test', 'median_change_ms', 'median_change_pct']].head(6).to_string())
rvb = bz[bz.test.str.contains('2006|rv', case=False)]
chk('rvot_diag_2026-10-12', 'Bazan 2006 RV fw QRS change ms / % (from cb CSV)', [6, 4, 5, 4.1, 2.6, 3.6], [(lambda j: (j.a - j.b).median())(lvfw(cb[h], 'true_qrs_duration_ms', 'rv_free_wall')) for h in H] + [round((lambda j: (100 * (j.a - j.b) / j.b).median())(lvfw(cb[h], 'true_qrs_duration_ms', 'rv_free_wall')), 1) for h in H], 0.15)
# --- aim1_gates_2026-10-12
be = pd.read_csv('aim1_gates_2026-10-12/berruezo.csv'); be = be[be.family == 'lv_free_wall'].set_index('heart')
for c, cl in (('qrs', [6.0, 11.3, 7.7]), ('pdw', [42.6, 55.3, 31.7]), ('idt', [21.7, 26.7, 15.5]), ('srs', [16.1, 19.1, 5.4])):
    col = {'qrs': 'true_qrs_duration_ms', 'pdw': 'true_pseudo_delta_ms', 'idt': 'true_idt_v2_ms', 'srs': 'true_srs_ms'}[c]
    chk('aim1_gates_2026-10-12', f'Berruezo LV fw median rel {c} % (report / recomputed from cb CSV)', cl, [round((lambda j: (100 * (j.a - j.b) / j.b).median())(lvfw(cb[h], col)), 1) for h in H], 0.15)
nn = pd.read_csv('grids_2026-10-07/nofast_Y5HYEDL4.csv')
chk('aim1_gates_2026-10-12', 'no-network summit+cusp QRS (job 1)', 250.0, nn[nn.family.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median(), 0.5)
dj = json.load(open('aim1_gates_2026-10-12/durrer.json'))
chk('aim1_gates_2026-10-12', 'Durrer latest after LV onset (json vs LABNOTES)', 104.4, dj['T_latest_after_lv_onset_ms'], 0.05)
# --- rvot_tests_2026-10-12
fi = pd.read_csv('rvot_tests_2026-10-12/final.csv').set_index('set')
for v_ in ('V2', 'V3', 'V4'):
    b_ = pd.read_csv(f'rvot_tests_2026-10-12/{v_}/beats.csv')
    chk('rvot_tests_2026-10-12', f'{v_} RVOT MDI median (final vs beats)', float(fi.loc[v_, 'RVOT']), round(b_[b_.family == 'rvot'].mdi_daniels.median(), 3), 0.0015)
    chk('rvot_tests_2026-10-12', f'{v_} summit+cusp QRS (final vs beats)', float(fi.loc[v_, 'summit_cusp_qrs']), b_[b_.family.isin(['lv_summit', 'aortic_cusp'])].qrs_ms.median(), 0.5)
# --- noise_onset_2026-10-12
ns = pd.read_csv('noise_onset_2026-10-12/sites.csv'); ids = cb['Y5HYEDL4'][['id', 'family']]
m = ns[ns.heart == 'Y5HYEDL4'].merge(ids, on='id')
chk('noise_onset_2026-10-12', 'Y5 RVOT detected MDI at 0/10/20/40 uV', [0.685, 0.650, 0.642, 0.604], [round(m[(m.family == 'rvot') & (m.noise_uv == u)].mdi.median(), 3) for u in (0, 10, 20, 40)], 0.0015)
chk('noise_onset_2026-10-12', 'detected onset median all sites 0/10/20/40 uV', [3, 6, 9, 15.5], [ns[ns.noise_uv == u].onset_ms.median() for u in (0, 10, 20, 40)], 0.5)
# --- junction_tests_2026-10-12
js = pd.read_csv('junction_tests_2026-10-12/summary.csv').set_index('set')
for s_, cl in (('v3', 0.667), ('J1', 0.646), ('J3b', 0.782)):
    b_ = pd.read_csv(f'junction_tests_2026-10-12/{s_}/beats.csv')
    chk('junction_tests_2026-10-12', f'{s_} RVOT true MDI (LABNOTES / beats.csv)', cl, round(b_[b_.family == 'rvot'].mdi.median(), 3), 0.0015)
chk('junction_tests_2026-10-12', 'His QRS v3 / J1 (LABNOTES vs summary)', [104.2, 121.5], [float(js.loc['v3', 'his_qrs']), float(js.loc['J1', 'his_qrs'])], 0.15)
# --- rvot_anatomy
se = pd.read_csv('rvot_anatomy_2026-10-12/septal.csv')
chk('rvot_anatomy_2026-10-12', 'septal crossing Y5 (3 sites) ms', [16.2, 18.3, 16.8], se[se.heart == 'Y5HYEDL4'].lv_septum_first_ms_network.round(1).tolist(), 0.15)
chk('rvot_anatomy_2026-10-12', 'septal crossing 7D (3 sites) ms', [13.6, 14.9, 10.2], se[se.heart == '7D98EVAR'].lv_septum_first_ms_network.round(1).tolist(), 0.15)
# --- monodomain
mo = pd.read_csv('monodomain_check_2026-10-12/results.csv'); print(mo[['beat', 'model', 'qrs_ms', 'mdi', 'total_activation_ms', 'within_5ms_pct']].to_string())
chk('monodomain_check_2026-10-12', 'RVOT eik/mono MDI, QRS; LVfw eik/mono QRS; within 5 ms %', [0.560, 0.615, 150, 143, 166, 154, 84.5, 86.9], [mo.mdi[0], mo.mdi[1], mo.qrs_ms[0], mo.qrs_ms[1], mo.qrs_ms[2], mo.qrs_ms[3], mo.within_5ms_pct[1], mo.within_5ms_pct[3]], 0.005)
# --- free_checks
la = pd.read_csv('free_checks_2026-10-13/latency.csv')
r6 = la[(la.heart == '6G8DD8S5') & (la.family == 'lv_free_wall')].iloc[0]
chk('free_checks_2026-10-13', '6G LV fw rel QRS / IDT / RS % (0 -> latency)', [11.3, 20.8, 26.7, 44.0, 19.1, 33.5], [round(r6.qrs_rel_pct_0, 1), round(r6.qrs_rel_pct_lat, 1), round(r6.idt_rel_pct_0, 1), round(r6.idt_rel_pct_lat, 1), round(r6.srs_rel_pct_0, 1), round(r6.srs_rel_pct_lat, 1)], 0.15)
hj = pd.read_csv('free_checks_2026-10-13/his_junctions.csv').set_index('heart')
chk('free_checks_2026-10-13', 'junctions per cm2 of all endocardium', [10.7, 12.0, 11.2], [round(hj.loc[h, 'per_cm2_all_endo'], 1) for h in H], 0.05)
# --- fibre_fix
bf = pd.read_csv('fibre_fix_2026-10-13/beats_fix.csv')
chk('fibre_fix_2026-10-13', 'fix RVOT / cusp / LV endo 10 MDI', [0.688, 0.582, 0.342], [round(bf[bf.family == 'rvot'].mdi.median(), 3), round(bf[bf.family == 'aortic_cusp'].mdi.median(), 3), round(bf[bf.family.isin(['lv_free_wall', 'lv_septum']) & (bf.depth_target == 0.1)].mdi.median(), 3)], 0.0015)
# --- daniels_onset
ds = pd.read_csv('daniels_onset_2026-10-13/signals.csv'); ds['S'] = pd.to_numeric(ds.S, errors='coerce')
for cond, cl in zip(sorted(ds.cond.unique()), ([0.531], [0.595])):
    x = ds[(ds.cond == cond) & (ds.family == 'rvot') & (np.isclose(ds.S, 0.008))]
    per_site = x.groupby('id').mdi.median()
    chk('daniels_onset_2026-10-13', f'S=0.008 RVOT MDI cond {cond} (median of site medians / of all signals)', cl, [round(x.mdi.median(), 3)], 0.0015)
# --- v5_grid
g5 = {}
for arm, cl_r, cl_c in (('A', 0.666, 0.653), ('C', 0.669, 0.582), ('E', 0.686, 0.584)):
    b_ = pd.read_csv(f'v5_grid_2026-10-13/{arm}/Y5HYEDL4/beats.csv')
    chk('v5_grid_2026-10-13', f'arm {arm} Y5 RVOT / cusp true MDI', [cl_r, cl_c], [round(b_[b_.family == 'rvot'].true_mdi_daniels.median(), 3), round(b_[b_.family == 'aortic_cusp'].true_mdi_daniels.median(), 3)], 0.0015)
for arm, cl in (('A', 123.5), ('B', 142.0), ('C', 140.6), ('E', 140.6)):
    T = np.load(f'v5_grid_2026-10-13/{arm}/6G8DD8S5/his_T.npy').astype(float)
    chk('v5_grid_2026-10-13', f'arm {arm} 6G His QRS (span)', cl, round(T.max() - T.min(), 1), 0.15)
for arm, cl in (('A', 17.6), ('B', 7.6), ('C', 5.7), ('E', 6.1)):
    b_ = pd.read_csv(f'v5_grid_2026-10-13/{arm}/6G8DD8S5/beats.csv'); b_ = b_[b_.family != 'his']
    chk('v5_grid_2026-10-13', f'arm {arm} 6G Berruezo RS %', cl, round((lambda j: (100 * (j.a - j.b) / j.b).median())(lvfw(b_, 'true_srs_ms')), 1), 0.15)
# --- v5_adopted three_hearts results.md group medians
v5 = {h: pd.read_csv(f'v5_adopted_2026-10-13/purk_{h}_v5.csv') for h in H}
chk('v5_adopted_2026-10-13', 'LV fw true QRS median', [161.0, 154.0, 161.0], [v5[h][v5[h].family == 'lv_free_wall'].true_qrs_duration_ms.median() for h in H], 0.5)
chk('v5_adopted_2026-10-13', 'RVOT true MDI median', [0.68, 0.57, 0.69], [round(v5[h][v5[h].family == 'rvot'].true_mdi_daniels.median(), 2) for h in H], 0.005)
chk('v5_adopted_2026-10-13', 'pdw>=34 calls at 10 % (depth-truth sites)', [24, 26, 20], [int((v5[h][(v5[h].depth_target == 0.1) & tf(v5[h].epi_endo_truth)].true_pseudo_delta_ms >= 34).sum()) for h in H], 0)
chk('v5_adopted_2026-10-13', 'LV fw 10->90 median QRS change (LABNOTES +12/+22/+16)', [12, 22, 16], [(lambda j: (j.a - j.b).median())(lvfw(v5[h], 'true_qrs_duration_ms')) for h in H], 0.5)
# --- idt_v2 and pilot v4
iv = pd.read_csv('idt_v2_2026-10-07/idt_v2_sites.csv')
chk('idt_v2_2026-10-07', 'n sites IDT>=85 and all IDT >= 90 % of QRS', [23, 1], [int((iv.true_idt_v2_ms >= 85).sum()), int((iv.true_idt_index >= 0.9).all())], 0)
p4 = pd.read_csv('pilot_grid_sites_v4.csv')
for mode in ('true', 'detected'):
    got = [(lambda j: (j.a - j.b).median())(lvfw(p4, f'{mode}_{c}')) for c in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels', 'qrs_duration_ms')]
    chk('pilot grid v4 (4 Oct)', f'LV fw 10->90 median change PdW/IDT/RS/MDI/QRS ({mode} onset)', [15.5, 14.5, 20, 0.071, 13.5], [round(x, 3) for x in got], 0.5)
    got = [round(auc(p4[(p4.family == 'lv_free_wall') & (p4.depth_target == 0.9)][f'{mode}_{c}'], p4[(p4.family == 'lv_free_wall') & (p4.depth_target == 0.1)][f'{mode}_{c}']), 2) for c in ('mdi_daniels', 'srs_ms', 'pseudo_delta_ms', 'idt_v2_ms')]
    chk('pilot grid v4 (4 Oct)', f'LV fw AUC MDI/RS/PdW/IDT ({mode} onset)', [0.94, 0.91, 0.81, 0.74], got, 0.01)
df = pd.DataFrame(rows)
df.to_csv('audit_2026-10-13/a09_integrity.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90)
print(df.to_string())
print('matches', int(df.match.sum()), 'of', len(df))
