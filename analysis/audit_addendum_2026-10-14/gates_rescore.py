"""Addendum part A: gate table from rescore/per_site.csv (A1 reproduction, A2 primary, A3 conditions, A4 statistics)."""
import json, math, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'rescore')
df = pd.read_csv(os.path.join(OUT, 'per_site.csv'))
if 'error' not in df: df['error'] = np.nan
ok = df['error'].isna() if 'error' in df else pd.Series(True, index=df.index)
unscorable = df[~ok][['heart', 'network', 'site', 'mode', 'noise', 'seed', 'error']]
d = df[ok].copy()
# site value = median over seeds
key = ['heart', 'network', 'site', 'family', 'depth', 'position', 'level_z', 'bazan_region', 'mode', 'noise']
num = ['onset_ms', 'offset_any_lead_ms', 'qrs_duration_any_lead_ms', 'qrs_duration_ms', 'mdi_daniels', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms']
d[['position', 'level_z', 'bazan_region']] = d[['position', 'level_z', 'bazan_region']].fillna('-')
agg = d.groupby(key, dropna=False)[num].median().reset_index()
fl = d.groupby(key, dropna=False)[['q_lead_I', 'inferior_q_any']].agg(lambda x: x.astype(str).str.lower().eq('true').mean() >= 0.5).reset_index()
agg = agg.merge(fl, on=key)
def sel(h, net, mode, noise): return agg[(agg.heart == h) & (agg.network == net) & (agg['mode'] == mode) & (agg.noise == noise)]
def pairs(x, fam, col):
    x = x[x.family == fam]; k = ['position', 'level_z']
    a = x[x.depth == 0.9].set_index(k)[col]; b = x[x.depth == 0.1].set_index(k)[col]
    return pd.concat([a.rename('a'), b.rename('b')], axis=1, join='inner').dropna()
def boot_ratio(j, n=2000, seed=0):
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(j), (n, len(j)))
    r = j.a.values[idx].mean(1) / j.b.values[idx].mean(1); return [round(float(np.percentile(r, 2.5)), 4), round(float(np.percentile(r, 97.5)), 4)]
def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd; hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return [round(100 * (c - hw), 1), round(100 * (c + hw), 1)]
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
PACE_CONDS = {'primary: stim onset, clean, QRS any lead': ('stim', 'clean', 'qrs_duration_any_lead_ms'), 'A3 stim onset, plan noise 10uV': ('stim', 'plan10', 'qrs_duration_any_lead_ms'),
              'A3 stim onset, clean, precordial offset': ('stim', 'clean', 'qrs_duration_ms'), 'A3 true (13 Oct)': ('true', 'clean', 'qrs_duration_ms')}
SPON_CONDS = {'primary: detected, plan noise 10uV, QRS any lead': ('detected', 'plan10', 'qrs_duration_any_lead_ms'), 'A3 detected clean': ('detected', 'clean', 'qrs_duration_any_lead_ms'),
              'A3 detected plan noise 20uV': ('detected', 'plan20', 'qrs_duration_any_lead_ms'), 'A3 detected 20uV 0.5-150 + notch': ('detected', 'old20_bp_notch', 'qrs_duration_any_lead_ms'),
              'A3 stim onset to ECG offset, clean': ('stim', 'clean', 'qrs_duration_any_lead_ms'), 'A3 true (13 Oct)': ('true', 'clean', 'qrs_duration_ms')}
G = {}
for cname, (mode, noise, qcol) in PACE_CONDS.items():
    g = {}
    for h in H:
        x = sel(h, 'net', mode, noise)
        if x.empty: continue
        j = pairs(x, 'lv_free_wall', qcol)
        g[f'relQRS {h[:2]} ratio of means (1.0785-1.1587)'] = round(j.a.mean() / j.b.mean(), 4) if len(j) else None
        g[f'relQRS {h[:2]} pass'] = bool(206 / 191 <= j.a.mean() / j.b.mean() <= 219 / 189) if len(j) else None
        g[f'relQRS {h[:2]} bootstrap 95% CI'] = boot_ratio(j) if len(j) else None
        jr = pairs(x, 'rv_free_wall', qcol); rr = float((100 * (jr.a - jr.b) / jr.b).median()); lr = float((100 * (j.a - j.b) / j.b).median())
        g[f'Bazan2006 {h[:2]} RV / LV median pair %'] = f'{rr:.1f} / {lr:.1f}'; g[f'Bazan2006 {h[:2]} pass'] = bool(-1.9 <= rr <= 6.6 and rr < lr)
        if h == '6G8DD8S5':
            vals = {}
            for k_, c in (('QRS', qcol), ('PdW', 'pseudo_delta_ms'), ('IDT', 'idt_v2_ms'), ('RS', 'srs_ms')):
                jj = pairs(x, 'lv_free_wall', c); vals[k_] = round(float((100 * (jj.a - jj.b) / jj.b).median()), 1)
            g['Berruezo 6G QRS/PdW/IDT/RS %'] = vals
            g['Berruezo 6G pass'] = bool(-1 <= vals['QRS'] <= 25 and 12 <= vals['IDT'] <= 86 and 20 <= vals['RS'] <= 52 and all(v > 0 for v in vals.values()))
    allx = pd.concat([sel(h, 'net', mode, noise) for h in H])
    for key_, (reg, col, bz) in {'basal superior q in I': ('lv_basal_superior', 'q_lead_I', (90, 16)), 'apical superior q in I': ('lv_apical_superior', 'q_lead_I', (88, 26)),
                                 'basal inferior Q II/III/aVF': ('lv_basal_inferior', 'inferior_q_any', (81, 37)), 'apical inferior Q II/III/aVF': ('lv_apical_inferior', 'inferior_q_any', (92, 33))}.items():
        z = allx[(allx.bazan_region == reg) & allx.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit'])]
        a, b = z[z.depth == 0.9], z[z.depth == 0.1]; k9, n9, k1, n1 = int(a[col].sum()), len(a), int(b[col].sum()), len(b)
        c9, c1 = wilson(k9, n9), wilson(k1, n1)
        g[f'Bazan2007 {key_} 90 vs 10'] = f'{k9}/{n9} vs {k1}/{n1}; CI90 {c9} CI10 {c1}; Bazan {bz[0]}/{bz[1]} in CI: {bool(c9[0] <= bz[0] <= c9[1] and c1[0] <= bz[1] <= c1[1])}; evaluable (n>=20): {n9 >= 20}'
    G['PACE ' + cname] = g
for cname, (mode, noise, qcol) in SPON_CONDS.items():
    g = {}; x = sel('Y5HYEDL4', 'net', mode, noise); nn = sel('Y5HYEDL4', 'nonet', mode, noise)
    sc = x[x.family.isin(['lv_summit', 'aortic_cusp'])][qcol]
    g['abs QRS summit+cusp median (132-193)'] = float(sc.median()); g['abs QRS pass'] = bool(132 <= sc.median() <= 193)
    g['abs QRS summit / cusp medians'] = f"{x[x.family == 'lv_summit'][qcol].median()} / {x[x.family == 'aortic_cusp'][qcol].median()}"
    M = {'summit90': (x.family == 'lv_summit') & (x.depth == 0.9), 'vein90': (x.family == 'lv_vein_course') & (x.depth == 0.9), 'cusp': x.family == 'aortic_cusp',
         'RVOT': x.family == 'rvot', 'LVendo10': x.family.isin(['lv_free_wall', 'lv_septum']) & (x.depth == 0.1)}
    md = {k_: round(float(x[m]['mdi_daniels'].median()), 3) for k_, m in M.items()}
    g['Daniels MDI summit90/vein90/cusp/RVOT/LVendo10'] = md; g['Daniels pass'] = bool(min(md['summit90'], md['vein90'], md['cusp']) > md['RVOT'] > md['LVendo10'])
    if not nn.empty:
        fams = ['lv_free_wall', 'lv_septum', 'rv_free_wall', 'rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course']
        s2 = float(nn[nn.family.isin(['lv_summit', 'aortic_cusp'])][qcol].median())
        wider = {f: [float(nn[nn.family == f][qcol].median()), float(x[x.family == f][qcol].median())] for f in fams}
        g['No-network summit+cusp median (>193)'] = s2; g['No-network wider by family [nonet, net]'] = wider
        g['No-network pass'] = bool(s2 > 193 and all(a > b for a, b in wider.values()))
    hb = sel('Y5HYEDL4', 'net', mode, noise); hb = hb[hb.family == 'his']
    if not hb.empty:
        g['Durrer (e) His QRS (63-88)'] = float(hb[qcol].iloc[0]); g['Durrer (e) pass'] = bool(63 <= hb[qcol].iloc[0] <= 88)
        g['His QRS 6G / 7D (info)'] = [float(sel(hh, 'net', mode, noise).query("family == 'his'")[qcol].iloc[0]) if not sel(hh, 'net', mode, noise).query("family == 'his'").empty else None for hh in ('6G8DD8S5', '7D98EVAR')]
    G['SPON ' + cname] = g
json.dump({'gates': G, 'unscorable': unscorable.to_dict('records')}, open(os.path.join(OUT, 'gates.json'), 'w'), indent=1, default=str)
for k, v in G.items():
    print('==', k)
    for a, b in v.items(): print('   ', a, b)
print('unscorable:', len(unscorable)); print(unscorable.head(20).to_string())
