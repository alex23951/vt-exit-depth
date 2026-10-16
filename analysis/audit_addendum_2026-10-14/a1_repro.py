"""Addendum A1: reproduction check. (1) every regenerated beat's in-memory true-mode scoring (same code as 13 Oct) vs the
13 Oct CSV values; (2) every gate recomputed in true mode from the regenerated beats vs the 13 Oct outcome table
(tolerance 0.5 ms; 0.001 for ratios and MDI); same verdicts. Writes rescore/a1_repro.json."""
import json, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
out = {'per_site': {}, 'gates': {}}
tf = lambda s: s.astype(str).str.lower().isin(['true', '1', '1.0'])
new = {}
for h in H + ['Y5HYEDL4_nonet']:
    r = pd.read_csv(os.path.join(HERE, 'maps', h, 'repro.csv'))
    hh = h.split('_')[0]
    S = pd.DataFrame(json.load(open(os.path.join(REPO, 'data', 'biv', hh, 'sites.json'))))
    r = r.merge(S[['id', 'family', 'depth_target', 'position', 'level_z', 'bazan_region']], on='id', how='left')
    r.loc[r.id == 'his_driven', 'family'] = 'his'
    cmp = {}
    for c in ['total_activation_ms', 'true_qrs_duration_ms', 'true_mdi_daniels', 'true_pseudo_delta_ms', 'true_idt_v2_ms', 'true_srs_ms', 'detected_qrs_duration_ms', 'detected_mdi_daniels']:
        a, b = pd.to_numeric(r[c + '_new'], errors='coerce'), pd.to_numeric(r[c + '_13oct'], errors='coerce')
        m = a.notna() & b.notna()
        if m.any():
            cmp[c] = {'n': int(m.sum()), 'max_abs_diff': float((a[m] - b[m]).abs().max()), 'n_nan_mismatch': int((a.isna() != b.isna()).sum())}
    for c in ['true_q_lead_I', 'true_inferior_q_any']:
        if r[c + '_13oct'].notna().any():
            cmp[c] = {'mismatches': int((tf(r[c + '_new']) != tf(r[c + '_13oct'])).sum())}
    out['per_site'][h] = cmp
    new[h] = r
def pairs(d, fam, col):
    x = d[d.family == fam]; k = ['position', 'level_z']
    a = x[x.depth_target == 0.9].set_index(k)[col]; b = x[x.depth_target == 0.1].set_index(k)[col]
    return pd.concat([a.rename('a'), b.rename('b')], axis=1, join='inner').astype(float)
g13 = json.load(open(os.path.join(REPO, 'analysis', 'audit_2026-10-13', 'a02_gates.json')))
G = {}
for h in H:
    d = new[h].copy()
    for c in d.columns:
        if c.endswith('_new'): d[c[:-4]] = d[c]
    d = d[d.family != 'his']
    for c in ['true_qrs_duration_ms', 'true_mdi_daniels', 'true_pseudo_delta_ms', 'true_idt_v2_ms', 'true_srs_ms']: d[c] = pd.to_numeric(d[c], errors='coerce')
    o13 = g13[h]
    f, dp = d.family, d.depth_target
    M = {'rvot': f == 'rvot', 'cusp': f == 'aortic_cusp', 'summit90': (f == 'lv_summit') & (dp == 0.9), 'vein90': (f == 'lv_vein_course') & (dp == 0.9), 'lvendo10': f.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)}
    for k, m in M.items(): G[f'{h} Daniels {k}'] = (round(float(d[m].true_mdi_daniels.median()), 3), o13['daniels_true_mdi_daniels'][k], 0.001)
    G[f'{h} summit+cusp QRS'] = (float(d[f.isin(['lv_summit', 'aortic_cusp'])].true_qrs_duration_ms.median()), o13['summit_cusp_true_qrs_median'], 0.5)
    j = pairs(d, 'lv_free_wall', 'true_qrs_duration_ms')
    G[f'{h} relQRS ratio of means'] = (round(j.a.mean() / j.b.mean(), 4), o13['lvfw_qrs_ratio_of_means'], 0.001)
    for k, c in (('QRS', 'true_qrs_duration_ms'), ('PdW', 'true_pseudo_delta_ms'), ('IDT', 'true_idt_v2_ms'), ('RS', 'true_srs_ms')):
        jj = pairs(d, 'lv_free_wall', c); G[f'{h} Berruezo {k} %'] = (round(float((100 * (jj.a - jj.b) / jj.b).median()), 1), o13['berruezo_lvfw_median_rel_pct'][k], 0.15)
    jr = pairs(d, 'rv_free_wall', 'true_qrs_duration_ms')
    G[f'{h} Bazan06 RV %'] = (round(float((100 * (jr.a - jr.b) / jr.b).median()), 1), o13['bazan2006_rv_lv_rel_qrs_pct'][0], 0.15)
# Bazan 2007 pooled basal superior q in I
allr = pd.concat([new[h].assign(heart=h) for h in H]); allr = allr[allr.family != 'his']
z = allr[(allr.bazan_region == 'lv_basal_superior') & allr.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit'])]
G['Bazan07 basal superior q I 90'] = (int(tf(z[z.depth_target == 0.9].true_q_lead_I_new).sum()), 4, 0)
G['Bazan07 basal superior q I 10'] = (int(tf(z[z.depth_target == 0.1].true_q_lead_I_new).sum()), 3, 0)
# no-network (lead-field independent: total activation)
nn = new['Y5HYEDL4_nonet']; nn['true_qrs'] = pd.to_numeric(nn.true_qrs_duration_ms_new, errors='coerce')
G['nonet summit+cusp QRS'] = (float(nn[nn.family.isin(['lv_summit', 'aortic_cusp'])].true_qrs.median()), g13['nonet']['summit_cusp_qrs'], 0.5)
# His beats: Durrer metrics from the regenerated His activation + ECG
from scipy.spatial import cKDTree
for h in H:
    T = np.load(os.path.join(HERE, 'maps', h, 'his_driven.T.npy')).astype(float); T13 = np.load(os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13', 'grid', h, 'his_T.npy')).astype(float)
    G[f'{h} His activation max |diff| vs saved his_T'] = (float(np.abs(T - T13).max()), 0.0, 0.01)
    e = np.load(os.path.join(HERE, 'maps', h, 'his_driven.ecg.npy')).astype(float); e13 = np.load(os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13', 'grid', h, 'his_ecg.npy')).astype(float)
    G[f'{h} His ECG max |diff| vs saved his_ecg (mV)'] = (float(np.abs(e - e13).max()), 0.0, 1e-4)
    r = new[h][new[h].id == 'his_driven'].iloc[0]
    G[f'{h} His detected QRS'] = (float(r.detected_qrs_duration_ms_new), g13['his'][h]['detected_qrs_ms'], 0.5)
    G[f'{h} His span'] = (round(T.max() - T.min(), 1), g13['his'][h]['span_ms'], 0.5)
out['gates'] = {k: {'regenerated': a, '13oct': b, 'match': bool(abs(float(a) - float(b)) <= tol)} for k, (a, b, tol) in G.items()}
out['all_gate_values_match'] = all(v['match'] for v in out['gates'].values())
os.makedirs(os.path.join(HERE, 'rescore'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, 'rescore', 'a1_repro.json'), 'w'), indent=1, default=str)
print(json.dumps(out['per_site'], indent=1)); print('gates match:', out['all_gate_values_match'])
for k, v in out['gates'].items():
    if not v['match']: print('MISMATCH', k, v)
