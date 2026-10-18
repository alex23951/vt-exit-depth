"""Step 2.5 report (v5.1 brief, decision H; 16 Oct 2026): 0.3.0 vs 0.4.0 q calls on the saved v5 beats, read-only.

Input: runs/v51_2026-10-15/02_measure_040/per_measurement.csv (rescore_040.py; sha256 checked against rescore_040.json).
Writes in this folder: q_changes.csv (every changed q / initial-r call, with its cause), per_site.csv (true and stimulus
onset, clean ECG, 0.3.0 and primary), gates_040.json, q_report.md.
Bazan 2007 gate = the 13 Oct rule (analysis/v5_adopted_2026-10-13/followup.py section 3: pooled LV free wall, vein-course
and summit positions of the three hearts, 90 % vs 10 % depth, difference with Newcombe's hybrid-score 95 % CI, consistent
if Bazan's difference lies inside it, not evaluable below 20 positions), q at 0.05 mV (the package call).
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), '02_measure_040'))
import nanstats as ns                                                   # noqa: E402

PM = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'rules', 'per_measurement.csv')   # Step 6 copy: path changes only
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
FLAG_LEADS = {'q_lead_I': ['I'], 'inferior_q_all': ['II', 'III', 'aVF'], 'inferior_q_any': ['II', 'III', 'aVF'],
              'inferior_r_any': ['II', 'III', 'aVF'], 'q_V1': ['V1'], 'q_V2': ['V2'], 'qs_V2': ['V2']}
RULES = ['030', 'primary', 'N20', 'window_only', 'no_window', 'wave010']
BAZAN = [('basal superior: q in I', 'lv_basal_superior', 'q_lead_I', False, 74), ('basal superior: no Q in II/III/aVF', 'lv_basal_superior', 'inferior_q_any', True, None),
         ('apical superior: q in I', 'lv_apical_superior', 'q_lead_I', False, 62), ('basal inferior: Q in II/III/aVF', 'lv_basal_inferior', 'inferior_q_any', False, 44),
         ('apical inferior: Q in II/III/aVF', 'lv_apical_inferior', 'inferior_q_any', False, 59)]
CORR = 'dated correction (measurement rule, decision H with CSE recognition, 15 Oct 2026)'


def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return c - hw, c + hw


def newcombe(k1, n1, k2, n2):
    """As followup.py (13 Oct): difference p1 - p2, Newcombe hybrid-score 95 % CI (method 10)."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def bazan07(d):
    """Gate 5 per feature on one rule x condition (rows of the three hearts, network beats)."""
    D = d[d.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit']) & d.depth.isin([0.1, 0.9])]
    out = {}
    for name, reg, col, negate, bz in BAZAN:
        x = D[D.bazan_region == reg]
        f = x[col].map(ns.flag)
        call = f.map(lambda v: None if v is None else (not v if negate else v))
        a, b = call[x.depth == 0.9], call[x.depth == 0.1]
        k9, n9, u9 = ns.rate(a); k1, n1, u1 = ns.rate(b)
        df_, lo, hi = newcombe(k9, n9, k1, n1) if n9 and n1 else (math.nan, math.nan, math.nan)
        if n9 < 20:
            verdict = 'not evaluable (< 20 positions)'
        elif bz is None:
            verdict = 'direction ' + ('as Bazan (more at epi)' if df_ > 0 else 'opposite to Bazan') + '; no Bazan % to compare'
        else:
            verdict = 'PASS (Bazan inside CI)' if lo * 100 <= bz <= hi * 100 else 'FAIL (Bazan outside CI)'
        out[name] = {'k90': k9, 'n90': n9, 'k10': k1, 'n10': n1, 'unscorable': u9 + u1, 'diff_pp': round(100 * df_, 1),
                     'ci_pp': [round(100 * lo, 1), round(100 * hi, 1)], 'bazan_pp': bz, 'verdict': verdict}
    return out


def cause(r030, rwo, rp, lead):
    p0, pw, pp = r030[f'pol_{lead}'], rwo[f'pol_{lead}'], rp[f'pol_{lead}']
    if p0 != pw:
        return f'window: first 0.05 mV wave ({p0:+d}) starts {rwo[f"start_{lead}"]:.0f} ms after the visible onset (> 40)'
    if pw != pp:
        sp, sw = int(rp[f'sign_{lead}']), int(rwo[f'sign_{lead}'])
        st = rp[f'start_{lead}']
        if sp != sw:
            return f'recognition: an earlier {"+" if sp > 0 else "-"} deflection (>= threshold for >= 6 ms, from {st:.0f} ms) comes first'
        if pp == 0 and st <= 40:
            return 'recognition: the first deflection turns back before reaching 0.05 mV'
        return f'recognition: first deflection from {st:.0f} ms (other)'
    return 'no change in this lead'


def main():
    sha = hashlib.sha256(open(PM, 'rb').read()).hexdigest()
    assert sha == json.load(open(os.path.join(HERE, 'rescore040_51.json')))['sha256'], 'per_measurement.csv changed'
    d = pd.read_csv(PM, low_memory=False, float_precision='round_trip')
    d['position'] = d.position.fillna('-'); d['level_z'] = d.level_z.fillna(-1); d['bazan_region'] = d.bazan_region.fillna('-')
    key = ['heart', 'network', 'site']
    clean = d[d.noise == 'clean']
    G, L = {}, []

    # ---------------------------------------------------------------- 1 Bazan 2007 under each rule and condition
    for mode, label in (('true', 'true mode (13 Oct)'), ('stim', '14 Oct pace-map convention (stimulus onset, clean)')):
        for rule in RULES:
            x = clean[(clean['mode'] == mode) & (clean.rule == rule) & (clean.network == 'net')]
            G[f'Bazan2007 | {label} | {rule}'] = bazan07(x)
    for rule in ('030', 'primary'):                               # 10 uV noise: majority over seeds 0-9 per site
        x = d[(d['mode'] == 'stim') & (d.noise == 'plan10') & (d.rule == rule) & (d.network == 'net')]
        agg = x.groupby(key + ['family', 'depth', 'bazan_region'])[['q_lead_I', 'inferior_q_any']].agg(lambda v: v.map(ns.flag).mean() >= 0.5).reset_index()
        G[f'Bazan2007 | stimulus onset, 10 uV noise (majority of 10 seeds) | {rule}'] = bazan07(agg)

    # ---------------------------------------------------------------- 2 changed calls 0.3.0 -> primary, with causes
    rows = []
    for mode in ('true', 'stim', 'detected'):
        x = clean[clean['mode'] == mode]
        by = {r: x[x.rule == r].set_index(key) for r in ('030', 'window_only', 'primary')}
        for idx in by['030'].index:
            a, w, p = by['030'].loc[idx], by['window_only'].loc[idx], by['primary'].loc[idx]
            for flag, leads in FLAG_LEADS.items():
                if ns.flag(a[flag]) != ns.flag(p[flag]):
                    ch = [l for l in leads if a[f'pol_{l}'] != p[f'pol_{l}']]
                    rows.append({'heart': idx[0], 'network': idx[1], 'site': idx[2], 'family': a.family, 'depth': a.depth, 'bazan_region': a.bazan_region,
                                 'mode': mode, 'call': flag, 'v030': ns.flag(a[flag]), 'v040': ns.flag(p[flag]), 'window_only': ns.flag(w[flag]),
                                 'leads': ' '.join(f'{l} {int(a[f"pol_{l}"]):+d}/{int(w[f"pol_{l}"]):+d}/{int(p[f"pol_{l}"]):+d}' for l in ch),
                                 'cause': '; '.join(f'{l}: {cause(a, w, p, l)}' for l in ch)})
    Q = pd.DataFrame(rows)
    Q.to_csv(os.path.join(HERE, 'rules_q_changes.csv'), index=False)
    G['changed calls 0.3.0 -> 0.4.0 (clean ECG)'] = {f'{m} / {c}': f"{int(((Q['mode'] == m) & (Q.call == c)).sum())} ({int(((Q['mode'] == m) & (Q.call == c) & (Q.v040 == False)).sum())} lost, {int(((Q['mode'] == m) & (Q.call == c) & (Q.v040 == True)).sum())} new)"
                                                       for m in ('true', 'stim', 'detected') for c in FLAG_LEADS} if len(Q) else {}
    G['causes (lead level, clean ECG)'] = Q.cause.str.split('; ').explode().str.replace(r'\d+ ms', 'N ms', regex=True).str.replace(r'^\w+: ', '', regex=True).str.replace(r'\([+-]\d\)', '(s)', regex=True).value_counts().to_dict() if len(Q) else {}

    # ---------------------------------------------------------------- 3 initial_start_ms per heart and region (primary)
    st = {}
    for mode in ('stim', 'true'):
        x = clean[(clean['mode'] == mode) & (clean.rule == 'primary') & (clean.network == 'net') & (clean.family != 'his')]
        x = x.assign(region=np.where(x.bazan_region != '-', x.bazan_region, x.family))
        for (h, reg), g in x.groupby(['heart', 'region']):
            cell = {}
            for l in ('I', 'II', 'III', 'aVF', 'aVL', 'aVR', 'V1', 'V2'):
                v = g[f'start_{l}'].astype(float)
                k = v.dropna()
                cell[l] = (f'{k.median():.1f} [{k.quantile(.25):.1f}-{k.quantile(.75):.1f}], max {k.max():.1f}, > 40 ms {int((k > 40).sum())}/{len(k)}' + (f', none {int(v.isna().sum())}' if v.isna().any() else '')) if len(k) else 'none'
            st[f'{mode} | {h} | {reg} (n {len(g)})'] = cell
    G['initial_start_ms (primary; median [IQR], ms after the visible onset)'] = st

    # ---------------------------------------------------------------- 4 visible onset - stimulus (stimulus mode)
    x = clean[(clean['mode'] == 'stim') & (clean.rule == 'primary')]
    vs = {}
    for (h, net, fam, dep), g in x.groupby(['heart', 'network', 'family', 'depth'], dropna=False):
        v = g.visible_onset_ms.astype(float)
        vs[f'{h} | {net} | {fam} | {dep}'] = f'median {v.median():.1f}, range {v.min():.1f}-{v.max():.1f} (n {len(v)})'
    G['visible onset - stimulus, ms (clean ECG)'] = vs

    # ---------------------------------------------------------------- 5 summit / cusp: Q ratio, R/S V1, Santangeli no q V1
    sc = []
    for mode in ('true', 'stim', 'detected'):
        x = clean[(clean['mode'] == mode) & clean.family.isin(['lv_summit', 'aortic_cusp'])]
        a, p = x[x.rule == '030'].set_index(key), x[x.rule == 'primary'].set_index(key)
        for idx in a.index:
            for c in ('q_ratio_avl_avr', 'rs_ratio_v1', 'santangeli2015_no_q_v1'):
                u, v = a.loc[idx, c], p.loc[idx, c]
                if not ((pd.isna(u) and pd.isna(v)) or (str(u) == str(v))):
                    sc.append(f'{mode} | {idx[0]} | {idx[1]} | {idx[2]} | {c}: {u} -> {v}')
    G['summit / cusp sites with a changed Q ratio, R/S V1 or Santangeli no-q-V1'] = sc

    # ---------------------------------------------------------------- 6 polarity-0 leads
    p0 = {}
    for mode in ('true', 'stim', 'detected'):
        for rule in ('030', 'window_only', 'N20', 'primary'):
            x = clean[(clean['mode'] == mode) & (clean.rule == rule)]
            p0[f'{mode} | {rule}'] = {l: int((x[f'pol_{l}'] == 0).sum()) for l in LEADS} | {'beats': len(x)}
    G['leads with polarity 0 (neither q nor initial r), clean ECG'] = p0

    # ---------------------------------------------------------------- 7 per-site table (analysis copy, smaller)
    cols = key + ['family', 'depth', 'position', 'level_z', 'bazan_region', 'mode', 'rule', 'visible_onset_ms', 'q_anchor_ms', 'q_lead_I', 'inferior_q_all',
                  'inferior_q_any', 'inferior_r_any', 'q_V1', 'q_V2', 'qs_V2', 'q_ratio_avl_avr', 'rs_ratio_v1', 'santangeli2015_no_q_v1', 'reason'] + \
           [f'pol_{l}' for l in LEADS] + [f'start_{l}' for l in ('I', 'II', 'III', 'aVF', 'aVL', 'aVR', 'V1', 'V2')]
    PS = clean[clean['mode'].isin(['true', 'stim']) & clean.rule.isin(['030', 'primary'])][cols]
    PS.to_csv(os.path.join(HERE, 'rules_per_site.csv'), index=False)
    G['per_site.csv'] = {'rows': len(PS), 'bytes': os.path.getsize(os.path.join(HERE, 'rules_per_site.csv'))}
    G['unscorable'] = {'rows': int((d.reason == 'onset_not_before_offset').sum()), 'note': '0 unscorable, none left out' if not (d.reason == 'onset_not_before_offset').any() else 'see per_measurement.csv'}
    G['input'] = {'file': os.path.relpath(PM, REPO), 'sha256': sha}
    json.dump(G, open(os.path.join(HERE, 'rules_gates.json'), 'w'), indent=1, default=str)

    # ---------------------------------------------------------------- report
    L.append('# Step 2.5: ecg_depth_criteria 0.3.0 vs 0.4.0 on the saved v5 beats (read-only)\n')
    L.append(f'Input {os.path.relpath(PM, REPO)} (sha256 {sha[:16]}...). Rules: 030; primary (N 40 ms + CSE); sensitivities N20, window_only, no_window, wave010.\n')
    L.append('## Gate 5: Bazan 2007 region Q (13 Oct rule: pooled positions, 90 % vs 10 %, Newcombe 95 % CI vs Bazan difference)\n')
    L.append('| condition | rule | basal superior q in I | basal superior no inferior Q | apical superior q in I | basal inferior Q | apical inferior Q |')
    L.append('|---|---|---|---|---|---|---|')
    for k, v in G.items():
        if k.startswith('Bazan2007'):
            _, cond, rule = [s.strip() for s in k.split('|')]
            cells = [f"{c['k90']}/{c['n90']} vs {c['k10']}/{c['n10']}, {c['diff_pp']:+.0f} ({c['ci_pp'][0]:+.0f} to {c['ci_pp'][1]:+.0f}){' [' + str(c['unscorable']) + ' unscorable]' if c['unscorable'] else ''}: {c['verdict']}" for c in v.values()]
            L.append(f'| {cond} | {rule} | ' + ' | '.join(cells) + ' |')
    L.append('\n## Changed q / initial-r calls, 0.3.0 -> 0.4.0 primary (clean ECG; per site and mode; details in q_changes.csv)\n')
    for k, v in G['changed calls 0.3.0 -> 0.4.0 (clean ECG)'].items():
        L.append(f'- {k}: {v}')
    L.append('\nCauses (lead level; window = first 0.05 mV wave after 40 ms; recognition = CSE step):\n')
    for k, v in G['causes (lead level, clean ECG)'].items():
        L.append(f'- {v} x {k}')
    L.append('\n## Summit / cusp sites with a changed Q ratio aVL/aVR, R/S V1 or Santangeli no-q-V1\n')
    L += [f'- {s}' for s in sc] or ['- none']
    L.append('\n## Leads with polarity 0 (neither), clean ECG, 579 beats per cell\n')
    L.append('| mode / rule | ' + ' | '.join(LEADS) + ' |'); L.append('|---|' + '---|' * len(LEADS))
    for k, v in p0.items():
        L.append(f'| {k} | ' + ' | '.join(str(v[l]) for l in LEADS) + ' |')
    L.append('\n## initial_start_ms and visible onset - stimulus: see gates_040.json (per heart and region / family and depth)\n')
    open(os.path.join(HERE, 'rules_q_report.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
