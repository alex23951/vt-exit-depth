"""Step 6: Table A (Aim 1 gates) for v5.1, beside the 13 Oct / 14 Oct / v5-0.4.0 columns of the brief (Step 7 layout).
Inputs (all produced by the Step 6 scripts): rescore/gates.json (gates51.py: 14 Oct gate rules, conditions primary and
A3, 0.4.0 package defaults = primary q rule), rules_gates.json (report040_51.py: Bazan 2007 under the primary rule and every
named sensitivity, 13 Oct Newcombe rule), the v5.1 His beats (maps/<H>/his_driven: Durrer (a)-(c) and T with
v5_grid_guarded.his_metrics, checked equal to Step 4.6), pilot_site_labels.csv (Step 5: AHA / body-label version of
Bazan 2007, printed beside, not evaluable below 20 positions).
Verdict differing from 13 Oct = "dated correction (v5.1 rebuild, decisions A-H, 15 Oct 2026)"; a verdict that differs
between the primary convention and any other computed condition / q rule is flagged convention-dependent.
Usage (repo root, venv): python -B analysis/v51_2026-10-15/10_conductor_sens/tableA51.py   -> tableA51.json, tableA51.md
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAPS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', 'maps')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
PACE_P = 'PACE primary: stim onset, clean, QRS any lead'
SPON_P = 'SPON primary: detected, plan noise 10uV, QRS any lead'
CORR = 'dated correction (v5.1 rebuild, decisions A-H, 15 Oct 2026)'
# Brief Table A, prefilled columns (13 Oct v5 true mode 0.3.0 | 14 Oct v5 surface ECG 0.3.0 | v5 0.4.0)
PRE = {
    '1': ('159.0 PASS', '137.0 PASS', '137.0 PASS (inputs unchanged)'),
    '2a': ('1.0712 FAIL', '1.0586 FAIL (CI 1.000-1.124)', 'as 14 Oct'),
    '2b': ('1.1371 PASS', '1.1840 FAIL (CI 1.167-1.199)', 'as 14 Oct'),
    '2c': ('1.0930 PASS', '1.1147 PASS (CI 1.062-1.160)', 'as 14 Oct'),
    '3': ('.542, .458, .587, .679, .348 FAIL', '.621, .497, .616, .689, .360 FAIL', 'as 14 Oct'),
    '4': ('4.2/8.0, 4.1/14.7, 4.0/10.3 PASS', '3.9/6.1, 3.5/18.7, 4.3/12.9 PASS', 'as 14 Oct'),
    '5': ('4/21 vs 3/21 FAIL', '4/21 vs 3/21 FAIL', 'FAIL (primary and every sensitivity)'),
    '6': ('14.7/60.6/31.6/7.6 % FAIL', '18.7/60.6/31.6/7.6 % FAIL', 'as 14 Oct'),
    '7': ('T 100.8; (a) 0/2.7/5.0 (calibrated); (b) 66.8 %; (c) 15.1; (e) 94 FAIL', '(e) 94.5 FAIL', 'as 14 Oct'),
    '8': ('240.0 PASS', '220.25 PASS (7/7)', 'as 14 Oct'),
    '9': ('not evaluable', 'not evaluable', 'not run'),
}
V13 = {'1': 'PASS', '2a': 'FAIL', '2b': 'PASS', '2c': 'PASS', '3': 'FAIL', '4': 'PASS', '5': 'FAIL', '6': 'FAIL', '7': 'FAIL', '8': 'PASS', '9': 'not evaluable'}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def pf(b):
    return 'PASS' if b else 'FAIL'


def main():
    G = json.load(open(os.path.join(HERE, 'rescore', 'gates.json')))
    gates, unscorable = G['gates'], G['unscorable']
    R = json.load(open(os.path.join(HERE, 'rules_gates.json')))
    P, S = gates[PACE_P], gates[SPON_P]
    pace_conds = {k: v for k, v in gates.items() if k.startswith('PACE')}
    spon_conds = {k: v for k, v in gates.items() if k.startswith('SPON')}
    rows = {}

    def dep(key, conds):
        vals = {c: v.get(key) for c, v in conds.items() if v.get(key) is not None}
        return len(set(map(bool, vals.values()))) > 1, vals

    # 1 absolute QRS
    cd, vv = dep('abs QRS pass', spon_conds)
    rows['1'] = (f"{S['abs QRS summit+cusp median (132-193)']:.1f}", pf(S['abs QRS pass']), cd,
                 f"true mode {spon_conds['SPON A3 true (13 Oct)']['abs QRS summit+cusp median (132-193)']:.1f}; summit / cusp {S['abs QRS summit / cusp medians']}")
    # 2 relative QRS
    for g_, h in (('2a', 'Y5HYEDL4'), ('2b', '6G8DD8S5'), ('2c', '7D98EVAR')):
        k = f'relQRS {h[:2]} pass'
        cd, vv = dep(k, pace_conds)
        rows[g_] = (f"{P[f'relQRS {h[:2]} ratio of means (1.0785-1.1587)']:.4f} (CI {P[f'relQRS {h[:2]} bootstrap 95% CI'][0]:.3f}-{P[f'relQRS {h[:2]} bootstrap 95% CI'][1]:.3f})",
                    pf(P[k]), cd, f"true mode {pace_conds['PACE A3 true (13 Oct)'][f'relQRS {h[:2]} ratio of means (1.0785-1.1587)']:.4f}")
    # 3 Daniels
    cd, vv = dep('Daniels pass', spon_conds)
    md = S['Daniels MDI summit90/vein90/cusp/RVOT/LVendo10']
    rows['3'] = (', '.join(f'{md[k]:.3f}' for k in ('summit90', 'vein90', 'cusp', 'RVOT', 'LVendo10')), pf(S['Daniels pass']), cd,
                 'true mode ' + ', '.join(f"{spon_conds['SPON A3 true (13 Oct)']['Daniels MDI summit90/vein90/cusp/RVOT/LVendo10'][k]:.3f}" for k in ('summit90', 'vein90', 'cusp', 'RVOT', 'LVendo10')))
    # 4 Bazan 2006 RV (all hearts)
    ok4 = all(P[f'Bazan2006 {h[:2]} pass'] for h in HEARTS)
    cds = [dep(f'Bazan2006 {h[:2]} pass', pace_conds)[0] for h in HEARTS]
    rows['4'] = (', '.join(P[f'Bazan2006 {h[:2]} RV / LV median pair %'] for h in HEARTS), pf(ok4), any(cds),
                 'true mode ' + ', '.join(pace_conds['PACE A3 true (13 Oct)'][f'Bazan2006 {h[:2]} RV / LV median pair %'] for h in HEARTS))
    # 5 Bazan 2007 (13 Oct Newcombe rule, basal superior q in I), primary and sensitivities
    kp = 'Bazan2007 | 14 Oct pace-map convention (stimulus onset, clean) | primary'
    f5 = R[kp]['basal superior: q in I']
    verdicts = {k: v['basal superior: q in I']['verdict'] for k, v in R.items() if k.startswith('Bazan2007')}
    v5 = 'PASS' if f5['verdict'].startswith('PASS') else ('not evaluable' if 'not evaluable' in f5['verdict'] else 'FAIL')
    cd5 = len({('PASS' if x.startswith('PASS') else 'FAIL') for x in verdicts.values()}) > 1
    # AHA / body-label version beside (decision F reading)
    lab = pd.read_csv(os.path.join(HERE, '..', '05_aha_labels', 'pilot_site_labels.csv'))
    pm = pd.read_csv(os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', 'rules', 'per_measurement.csv'))
    pm = pm[(pm.network == 'net') & (pm['mode'] == 'stim') & (pm.noise == 'clean') & (pm.rule == 'primary')]
    pm = pm.merge(lab[['heart', 'site', 'body_bazan_region']], on=['heart', 'site'])
    z = pm[pm.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit']) & (pm.body_bazan_region == 'lv_basal_superior')]
    a, b = z[z.depth == 0.9], z[z.depth == 0.1]
    body = f"{int(a.q_lead_I.astype(str).str.lower().eq('true').sum())}/{len(a)} vs {int(b.q_lead_I.astype(str).str.lower().eq('true').sum())}/{len(b)} ({'not evaluable, < 20 positions' if len(a) < 20 else 'evaluable'})"
    rows['5'] = (f"{f5['k90']}/{f5['n90']} vs {f5['k10']}/{f5['n10']}, diff {f5['diff_pp']} pp (CI {f5['ci_pp'][0]} to {f5['ci_pp'][1]}) vs Bazan +{f5['bazan_pp']}",
                 v5, cd5, f"{sum(x.startswith('FAIL') for x in verdicts.values())} of {len(verdicts)} rule x convention combinations FAIL (primary, N20, window only, no window, wave 0.10 mV and 0.3.0; true mode, 14 Oct pace-map convention, 10 uV noise); AHA / body labels, basal superior: {body}")
    # 6 Berruezo (6G8DD8S5)
    cd, vv = dep('Berruezo 6G pass', pace_conds)
    bz = P['Berruezo 6G QRS/PdW/IDT/RS %']
    rows['6'] = (f"{bz['QRS']}/{bz['PdW']}/{bz['IDT']}/{bz['RS']} %", pf(P['Berruezo 6G pass']), cd,
                 f"true mode {pace_conds['PACE A3 true (13 Oct)']['Berruezo 6G QRS/PdW/IDT/RS %']}; caveat: Berruezo's baseline QRS 194 +- 19 ms; no stimulus latency in the model")
    # 7 Durrer (control His beat)
    VG = module('vg', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'v5_grid_guarded.py'))
    os.environ['HEART'] = 'Y5HYEDL4'
    T = np.load(os.path.join(MAPS, 'Y5HYEDL4', 'his_driven.T.npy')).astype(float)
    ecg = np.load(os.path.join(MAPS, 'Y5HYEDL4', 'his_driven.ecg.npy')).astype(float)
    hm = VG.his_metrics('Y5HYEDL4', T, ecg)
    ref = json.load(open(os.path.join(HERE, '..', '04_build', 'his51_Y5HYEDL4.json')))['metrics']
    his_equal = all(hm[k] == ref[k] for k in hm)
    a_ = [hm[f'a_onset_{k}_ms'] for k in ('ant', 'sep', 'post')]
    n5 = sum(x - min(a_) <= 5.0 for x in a_)
    e_qrs = S['Durrer (e) His QRS (63-88)']
    parts = {'T 62-100': 62 <= hm['qrs_true_span_ms'] <= 100, '(a) >= 2 within 5 ms': n5 >= 2, '(b) >= 90 % by 37.5 ms': hm['b_lv37_pct'] >= 90,
             '(c) 20-31 ms': 20 <= hm['c_rv_epi_breakthrough_ms'] <= 31, '(e) 63-88 ms': bool(S['Durrer (e) pass'])}
    # convention dependence: T and (a)-(c) come from the activation map (one value); only (e) has conventions
    cd = all(v for k, v in parts.items() if k != '(e) 63-88 ms') and dep('Durrer (e) pass', spon_conds)[0]
    rows['7'] = (f"T {hm['qrs_true_span_ms']}; (a) {'/'.join(str(x) for x in a_)} ({n5} of 3 within 5 ms, uncalibrated); (b) {hm['b_lv37_pct']} % at 37.5 ms ({hm['b_lv30_pct']} % at 30); "
                 f"(c) {hm['c_rv_epi_breakthrough_ms']}; (d) last 5 % in Durrer areas {hm['d_last5_in_durrer_areas_pct']} %; (e) {e_qrs}",
                 pf(all(parts.values())), cd, 'parts: ' + ', '.join(f'{k} {pf(v)}' for k, v in parts.items()) + f"; His beat equal to Step 4.6: {his_equal}")
    # 8 No-network control
    cd, vv = dep('No-network pass', spon_conds)
    wd = S['No-network wider by family [nonet, net]']
    rows['8'] = (f"{S['No-network summit+cusp median (>193)']:.2f} ({sum(a > b for a, b in wd.values())}/7 wider)", pf(S['No-network pass']), cd,
                 f"true mode {spon_conds['SPON A3 true (13 Oct)']['No-network summit+cusp median (>193)']:.2f}")
    # 9 monodomain
    rows['9'] = ('not run', 'not evaluable', False, 'locked: 27 sites, 5 ms, >= 90 % of 108 pairs; runs on the frozen model before the OSF registration (Alex, 17 Oct)')
    names = {'1': 'Absolute paced QRS, summit + cusp (control)', '2a': 'Relative QRS Y5HYEDL4', '2b': 'Relative QRS 6G8DD8S5', '2c': 'Relative QRS 7D98EVAR',
             '3': 'Daniels order (control)', '4': 'Bazan 2006 RV (all)', '5': 'Bazan 2007 region Q (pooled)', '6': 'Berruezo (6G8DD8S5)',
             '7': 'Durrer (control, His beat)', '8': 'No-network control', '9': 'Monodomain agreement'}
    md_ = ['| # | Gate | 13 Oct v5 (true, 0.3.0) | 14 Oct v5 (surface ECG, 0.3.0) | v5, 0.4.0 | v5.1 primary | v5.1 verdict | Changed? | Convention-dependent? | Notes |',
           '|---|---|---|---|---|---|---|---|---|---|']
    tally = {'PASS': 0, 'FAIL': 0, 'not evaluable': 0}
    out = {}
    g2 = 'PASS' if all(rows[k][1] == 'PASS' for k in ('2a', '2b', '2c')) else 'FAIL'      # gate 2 counts once (13 Oct tally)
    for g_ in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
        tally[g2 if g_ == '2' else rows[g_][1]] += 1
    for g_ in ('1', '2a', '2b', '2c', '3', '4', '5', '6', '7', '8', '9'):
        val, ver, cdep, note = rows[g_]
        changed = ver != V13[g_]
        md_.append(f"| {g_} | {names[g_]} | {PRE[g_][0]} | {PRE[g_][1]} | {PRE[g_][2]} | {val} | {ver} | {CORR if changed else 'no'} | {'yes' if cdep else 'no'} | {note} |")
        out[g_] = {'gate': names[g_], 'v51_primary': val, 'verdict': ver, 'changed_vs_13_Oct': changed, 'convention_dependent': bool(cdep), 'notes': note}
    md_.append(f"| | Tally (pass / fail / not evaluable; gate 2 counted once, failing if any heart fails) | 3 / 5 / 1 | 3 / 5 / 1 | 3 / 5 / 1 | | {tally['PASS']} / {tally['FAIL']} / {tally['not evaluable']} | | | |")
    json.dump({'table_A': out, 'tally': tally, 'unscorable': unscorable, 'his_beat_equal_step_4_6': his_equal, 'his_metrics': hm}, open(os.path.join(HERE, 'tableA51.json'), 'w'), indent=1, default=str)
    open(os.path.join(HERE, 'tableA51.md'), 'w').write('\n'.join(md_) + '\n')
    print('\n'.join(md_))
    print('unscorable rows:', len(unscorable), '| His beat equal to 4.6:', his_equal)


if __name__ == '__main__':
    main()
