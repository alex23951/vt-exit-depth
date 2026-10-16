"""Audit 02: independent re-implementation of the Aim 1 gates from the v5 per-site CSVs (read only).
Does not import the old gate scripts. Uses only purk_<H>_v5.csv, grid/<H>/his_T.npy / his_ecg.npy, the E-arm no-network
CSV, and the heart meshes / UVCs / surfaces."""
import json, os, sys
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
R = 'analysis/v5_adopted_2026-10-13'
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
sys.path.insert(0, 'code/ecg_depth_criteria')
from ecg_depth_criteria import measure_beat, from_leads
out = {}
def load(h):
    d = pd.read_csv(f'{R}/purk_{h}_v5.csv')
    return d[d.family != 'his'].copy(), d[d.family == 'his'].iloc[0]
def matched(d, fam, col):
    x = d[d.family == fam]
    key = ['position', 'level_z'] if fam in ('lv_free_wall', 'rv_free_wall') else ['position']
    a = x[x.depth_target == 0.9].set_index(key)[col]; b = x[x.depth_target == 0.1].set_index(key)[col]
    j = pd.concat([a.rename('d90'), b.rename('d10')], axis=1, join='inner')
    return j
def auc(pos, neg):
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    pos, neg = pos[~np.isnan(pos)], neg[~np.isnan(neg)]
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return gt / (len(pos) * len(neg))
def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return [round(100 * (c - hw), 1), round(100 * (c + hw), 1)]
def tf(s):
    return s.astype(str).str.lower().isin(['true', '1', '1.0'])
for h in HEARTS:
    d, his = load(h)
    o = {}
    # Daniels families (true onset; and det20 where present)
    fam, dp = d.family, d.depth_target
    M = {'rvot': fam == 'rvot', 'cusp': fam == 'aortic_cusp', 'summit90': (fam == 'lv_summit') & (dp == 0.9),
         'vein90': (fam == 'lv_vein_course') & (dp == 0.9), 'lvendo10': fam.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)}
    for col in ['true_mdi_daniels', 'detected_mdi_daniels', 'det20_mdi']:
        if col in d and d[col].notna().any():
            med = {k: round(float(d[m][col].median()), 3) for k, m in M.items()}
            med['n'] = {k: int(m.sum()) for k, m in M.items()}
            med['order_pass'] = bool(min(med['summit90'], med['vein90'], med['cusp']) > med['rvot'] > med['lvendo10'])
            o[f'daniels_{col}'] = med
    o['summit_cusp_true_qrs_median'] = float(d[fam.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median())
    o['summit_cusp_n'] = int(fam.isin(['lv_summit', 'aortic_cusp']).sum())
    j = matched(d, 'lv_free_wall', 'true_qrs_duration_ms')
    o['lvfw_qrs_pairs_n'] = len(j)
    o['lvfw_qrs_mean_90_10'] = [round(j.d90.mean(), 2), round(j.d10.mean(), 2)]
    o['lvfw_qrs_ratio_of_means'] = round(j.d90.mean() / j.d10.mean(), 4)
    o['lvfw_qrs_ratio_of_medians'] = round(j.d90.median() / j.d10.median(), 4)
    o['lvfw_qrs_median_pair_ratio'] = round(float((j.d90 / j.d10).median()), 4)
    o['lvfw_qrs_ratio_of_means_in_1.0785_1.1587'] = bool(206 / 191 <= j.d90.mean() / j.d10.mean() <= 219 / 189)
    rel = {}
    for k, c in (('QRS', 'true_qrs_duration_ms'), ('PdW', 'true_pseudo_delta_ms'), ('IDT', 'true_idt_v2_ms'), ('RS', 'true_srs_ms')):
        jj = matched(d, 'lv_free_wall', c)
        rel[k] = round(float((100 * (jj.d90 - jj.d10) / jj.d10).median()), 1)
        rel[k + '_median_diff_ms'] = round(float((jj.d90 - jj.d10).median()), 1)
    o['berruezo_lvfw_median_rel_pct'] = rel
    o['berruezo_pass_rule(QRS -1..25, IDT 12..86, RS 20..52, all>0)'] = bool(-1 <= rel['QRS'] <= 25 and 12 <= rel['IDT'] <= 86 and 20 <= rel['RS'] <= 52 and all(rel[k] > 0 for k in ('QRS', 'PdW', 'IDT', 'RS')))
    jr = matched(d, 'rv_free_wall', 'true_qrs_duration_ms')
    rr = float((100 * (jr.d90 - jr.d10) / jr.d10).median()); lr = rel['QRS']
    o['bazan2006_rv_lv_rel_qrs_pct'] = [round(rr, 1), lr]; o['bazan2006_pairs_rv'] = len(jr)
    o['bazan2006_pass'] = bool(-1.9 <= rr <= 6.6 and rr < lr)
    # AUC LV free wall 90 vs 10 (unpaired, all positions), true onset; also paired sign test count
    fw = d[fam == 'lv_free_wall']
    au = {}
    for k in ['true_pseudo_delta_ms', 'true_mdi_daniels', 'true_idt_v2_ms', 'true_srs_ms', 'true_qrs_duration_ms']:
        au[k] = round(auc(fw[fw.depth_target == 0.9][k], fw[fw.depth_target == 0.1][k]), 3)
        jj = matched(d, 'lv_free_wall', k)
        au[k + '_paired_up'] = f'{int((jj.d90 > jj.d10).sum())}/{len(jj)}'
    o['auc_lvfw_90v10'] = au
    # epicardial calls at 10 % among depth-truth sites
    t = d[tf(d.epi_endo_truth) & (dp == 0.1)]
    o['pdw_ge34_calls_at_10pct'] = f"{int(tf(t.true_berruezo_pdw_ge_34).sum())}/{len(t)}"
    o['pdw_ge34_recomputed_from_values'] = f"{int((t.true_pseudo_delta_ms >= 34).sum())}/{len(t)}"
    out[h] = o
# Bazan 2007 pooled over the 3 hearts (package rule true_q_lead_I, LV wall families)
allr = pd.concat([load(h)[0].assign(heart=h) for h in HEARTS])
bz = {}
for key, (reg, col) in {'basal_superior_qI': ('lv_basal_superior', 'true_q_lead_I'), 'apical_superior_qI': ('lv_apical_superior', 'true_q_lead_I'),
                        'basal_inferior_infQ': ('lv_basal_inferior', 'true_inferior_q_any'), 'apical_inferior_infQ': ('lv_apical_inferior', 'true_inferior_q_any'),
                        'basal_superior_infQ': ('lv_basal_superior', 'true_inferior_q_any')}.items():
    x = allr[(allr.bazan_region == reg) & allr.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit'])]
    a, b_ = x[x.depth_target == 0.9], x[x.depth_target == 0.1]
    k9, n9, k1, n1 = int(tf(a[col]).sum()), len(a), int(tf(b_[col]).sum()), len(b_)
    bz[key] = {'90': f'{k9}/{n9}', '10': f'{k1}/{n1}', 'pp_diff': round(100 * (k9 / n9 - k1 / n1), 1), 'ci90': wilson(k9, n9), 'ci10': wilson(k1, n1)}
    # alternative: q in lead I recomputed from saved q amplitude >= 0.05 mV
out['bazan2007_pooled'] = bz
# No-network control (E arm, control heart)
nn = pd.read_csv('analysis/v5_grid_2026-10-13/E/Y5HYEDL4/beats_nonet.csv'); d0, _ = load('Y5HYEDL4')
fams = ['lv_free_wall', 'lv_septum', 'rv_free_wall', 'rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course']
out['nonet'] = {'summit_cusp_qrs': float(nn[nn.family.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median()),
                'by_family_nonet_vs_net': {f: [float(nn[nn.family == f].true_qrs_duration_ms.median()), float(d0[d0.family == f].true_qrs_duration_ms.median())] for f in fams},
                'n_nonet': len(nn)}
out['nonet']['pass'] = bool(out['nonet']['summit_cusp_qrs'] > 193 and all(a > b for a, b in out['nonet']['by_family_nonet_vs_net'].values()))
# His beats: Durrer-type metrics, my own implementation
def his_audit(h):
    B = f'data/biv/{h}/'
    pts = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    z, phi, v, rho = (np.loadtxt(B + f'uvc/{n}.dat') for n in ('z', 'phi', 'v', 'rho')); ph = np.degrees(phi)
    rv_ = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    lv, rv, epi = rv_('lv_endo'), rv_('rv_endo'), rv_('epi')
    T = np.load(f'{R}/grid/{h}/his_T.npy').astype(float); ecg = np.load(f'{R}/grid/{h}/his_ecg.npy').astype(float)
    o = {'unactivated_nodes': int(np.isinf(T).sum()), 'T_first_myocardium_ms': round(T.min(), 1), 'T_max_ms': round(T.max(), 1),
         'span_ms': round(T.max() - T.min(), 1)}
    t0 = T[lv].min(); o['lv_endo_onset_ms'] = round(t0, 1); o['rv_endo_onset_ms'] = round(T[rv].min(), 1)
    o['latest_after_lv_onset_ms'] = round(T.max() - t0, 1)
    pb = (z >= 2 / 3) & (ph >= -150) & (ph <= -30)
    keep = lv[~pb[lv]]
    o['lv_endo_excl_posterobasal_by30_nodes_pct'] = round(100 * float((T[keep] <= t0 + 30).mean()), 1)
    o['lv_endo_all_by30_nodes_pct'] = round(100 * float((T[lv] <= t0 + 30).mean()), 1)
    tri = np.loadtxt(B + 'surfaces/lv_endo.surf', skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    ar = 0.5 * np.linalg.norm(np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]]), axis=1)
    tc = T[tri].mean(1); tri_pb = pb[tri].all(1)
    o['lv_endo_excl_posterobasal_by30_area_pct(tri)'] = round(100 * float(ar[~tri_pb][tc[~tri_pb] <= t0 + 30].sum() / ar[~tri_pb].sum()), 1)
    o['lv_endo_excl_posterobasal_by37.5_area_pct(tri)'] = round(100 * float(ar[~tri_pb][tc[~tri_pb] <= t0 + 37.5].sum() / ar[~tri_pb].sum()), 1)
    rve = epi[v[epi] == 1]
    k = rve[np.argmin(T[rve])]
    o['rv_epi_breakthrough_after_lv_onset_ms'] = round(T[k] - t0, 1); o['rv_epi_breakthrough_z_phi'] = [round(z[k], 2), round(ph[k], 0)]
    # RV epicardium restricted to RV free wall (exclude nodes within 3 mm of the LV epicardium / septal junction)
    lve = epi[v[epi] == 0]
    far = rve[cKDTree(pts[lve]).query(pts[rve])[0] > 5.0]
    k2 = far[np.argmin(T[far])]
    o['rv_freewall_epi_breakthrough_(>5mm_from_LV_epi)_ms'] = round(T[k2] - t0, 1); o['rv_fw_epi_bt_z_phi'] = [round(z[k2], 2), round(ph[k2], 0)]
    # earliest LV endocardial sites (first 5 ms) in UVC
    e5 = lv[T[lv] <= t0 + 5]
    o['lv_endo_first5ms_n_nodes'] = int(len(e5))
    # clusters by nearest Durrer target
    tg = {'high_ant_paraseptal(phi60,z0.8)': (60, 0.8), 'central_left_septum(phi0,z0.5)': (0, 0.5), 'post_paraseptal(phi-60,z0.33)': (-60, 0.33)}
    for nm, (p_, zz) in tg.items():
        dd = np.sqrt((z[lv] - zz) ** 2 + (np.angle(np.exp(1j * np.radians(ph[lv] - p_))) / np.pi) ** 2)
        n0 = lv[np.argmin(dd)]
        near = lv[np.linalg.norm(pts[lv] - pts[n0], axis=1) <= 10]
        o[f'onset_{nm}_ms_after_lv_onset'] = round(float(T[near].min() - t0), 1)
    first = lv[np.argmin(T[lv])]
    o['first_lv_endo_node_z_phi'] = [round(z[first], 2), round(ph[first], 0)]
    firstrv = rv[np.argmin(T[rv])]; o['first_rv_endo_node_z_phi'] = [round(z[firstrv], 2), round(ph[firstrv], 0)]
    last = int(np.argmax(T)); o['latest_node_z_phi_v'] = [round(z[last], 2), round(ph[last], 0), int(v[last])]
    # region of the last 5 % of nodes (node count)
    lastn = np.argsort(T)[-max(1, len(T) // 20):]
    o['last5pct_nodes_RV_frac'] = round(float((v[lastn] == 1).mean()), 2); o['last5pct_median_z'] = round(float(np.median(z[lastn])), 2)
    o['last5pct_median_phi'] = round(float(np.median(ph[lastn])), 0)
    # ECG: detected QRS and axes
    L = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, L.index(l)]), ecg[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    m = measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))
    o['detected_qrs_ms'] = m['qrs_duration_ms']; o['detected_qrs_any_lead_ms'] = m['qrs_duration_any_lead_ms']
    o['detected_onset_after_his_ms'] = m['onset_ms'] - pad
    tt = np.arange(ecg.shape[0]); msk = (tt >= T.min()) & (tt <= T.max() + 3)
    ang = np.radians([0, 60, 120, -150, -30, 90]); A = np.c_[np.cos(ang), np.sin(ang)]
    for nm, fn in (('net', lambda y: y[msk].max() + y[msk].min()), ('area', lambda y: y[msk].sum())):
        c = np.linalg.lstsq(A, np.array([fn(ecg[:, j] - ecg[0, j]) for j in range(6)]), rcond=None)[0]
        o[f'axis_{nm}_deg'] = int(round(np.degrees(np.arctan2(c[1], c[0]))))
    # Einthoven check
    o['einthoven_max_abs_I+III-II_mV'] = float(np.abs(ecg[:, 0] + ecg[:, 2] - ecg[:, 1]).max())
    o['goldberger_max_abs_aVR+aVL+aVF_mV'] = float(np.abs(ecg[:, 3] + ecg[:, 4] + ecg[:, 5]).max())
    o['limb_pp_mV'] = {l: round(float(np.ptp(ecg[msk, i])), 2) for i, l in enumerate(L)}
    if h == '6G8DD8S5':
        tr = cKDTree(pts[rv]); te = cKDTree(pts[epi])
        lvs = lv[tr.query(pts[lv])[0] < te.query(pts[lv])[0]]
        o['lbbb_lv_minus_rv_endo_onset_ms'] = round(T[lv].min() - T[rv].min(), 1)
        o['lbbb_first_lv_septal_bt_after_first_myocardium_ms'] = round(T[lvs].min() - T.min(), 1)
    return o
out['his'] = {h: his_audit(h) for h in HEARTS}
json.dump(out, open('analysis/audit_2026-10-13/a02_gates.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
