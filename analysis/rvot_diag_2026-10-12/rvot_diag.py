#!/usr/bin/env python
"""
RVOT MDI desk check, 12 Oct 2026 (coordinator brief from the project thread; analysis only: no new beats,
no lead fields, nothing deleted).

Why: Daniels' MDI order fails in all three hearts because the paced RVOT MDI is too high (cb, true onset
0.59-0.69 vs Daniels 2006 0.40 and Zheng 2020 real RVOT PVCs 0.415 scored with ecg_depth_criteria 0.3.0).
This script asks where the late largest precordial deflection comes from: which lead, how late, the site's
position against the pulmonary valve and the V1-V2 electrodes, and how fast the beat recruits the network
and the muscle.

Inputs (network v3, cb conductor, as the study uses since 10 Oct):
  analysis/grids_2026-10-07/purk_<HEART>_cb.csv, runs/<run>_ecg_cb/POSTPROC_DIR/ECG_*.dat,
  runs/<run>/act.igb (act_graph.npy for graph-fallback sites, same rule as 15_conductor.py),
  runs/<run>/pmj_stims.json, data/biv/<HEART>/{torso/full.pts, torso/heart.elem, torso/summary_08.json,
  surfaces/pv_rim.vtx, surfaces/apex.vtx, purkinje/network.npz, sites.json}

Per-lead timing replicates ecg_depth_criteria 0.3.0, true-onset mode: baseline = ECG at the stimulus,
window = stimulus .. last activation (true QRS), largest |deflection| per lead; MDI = earliest of V1-V6 / QRS.
The script checks its MDI against the CSV's true_mdi_daniels.

Output: analysis/rvot_diag_2026-10-12/{per_lead.csv, sites.csv, lead_summary.csv, bazan.csv,
mono_estimate.csv, report.txt, median_v1v6_rvot_vs_lvendo10.png}

Run: source ~/venv_carputils/bin/activate; python analysis/rvot_diag_2026-10-12/rvot_diag.py  (~1-2 min)
"""

import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUNS = os.path.join(REPO, 'runs')
OUT = os.path.dirname(os.path.abspath(__file__))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
PRE = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6']
GROUPS = {'rvot': 'RVOT', 'cusp': 'aortic cusp', 'lvfw10': 'LV free wall 10 %'}
D_RET_MS = 2.0                       # muscle -> Purkinje delay of 14_purkinje.py (P['d_ret_ms'])
MONO_S_PER_MS = 2400.0 / 140.0       # monodomain wall time, 6 cores: 2026-10-02_biv_fullqrs (LABNOTES)
REPORT = []


def say(s=''):
    print(s)
    REPORT.append(s)


def group(r):
    if r['family'] == 'rvot':
        return 'rvot'
    if r['family'] == 'aortic_cusp':
        return 'cusp'
    if r['family'] == 'lv_free_wall' and abs(r['depth_target'] - 0.1) < 1e-6:
        return 'lvfw10'
    return None


def read_table(f, skip, cols):
    return pd.read_csv(f, sep=r'\s+', skiprows=skip, header=None, usecols=cols, engine='c').to_numpy()


def read_vtx(f):
    return np.loadtxt(f, skiprows=2, dtype=np.int64)


def activation(run):
    s = json.load(open(os.path.join(RUNS, run, 'summary_12.json')))
    if s.get('mode') == 'graph_fallback':
        return np.load(os.path.join(RUNS, run, 'act_graph.npy')).astype(float), 'graph'
    b = open(os.path.join(RUNS, run, 'act.igb'), 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float), 'openCARP'


def ecg(run):
    d = os.path.join(RUNS, run + '_ecg_cb', 'POSTPROC_DIR')
    return {k: np.loadtxt(os.path.join(d, f'ECG_{k}.dat'))[:, 1] for k in PRE}


def heart_geometry(h):
    hd = os.path.join(REPO, 'data', 'biv', h)
    full = read_table(os.path.join(hd, 'torso', 'full.pts'), 1, [0, 1, 2]) / 1e3        # mm, torso frame
    el = read_table(os.path.join(hd, 'torso', 'heart.elem'), 1, [1, 2, 3, 4]).astype(np.int64)
    n_heart = int(open(os.path.join(hd, 'torso', 'heart.pts')).readline())
    P = full[:n_heart]                     # heart nodes come first, same order (08_torso.py checks this)
    a, b, c, d = (P[el[:, k]] for k in range(4))
    vol = np.abs(np.einsum('ij,ij->i', np.cross(b - a, c - a), d - a)) / 6.0
    nvol = np.bincount(el.ravel(), weights=np.repeat(vol / 4.0, 4), minlength=n_heart)
    rim = P[read_vtx(os.path.join(hd, 'surfaces', 'pv_rim.vtx'))]
    cen = rim.mean(0)
    nrm = np.linalg.svd(rim - cen)[2][-1]
    apex = P[read_vtx(os.path.join(hd, 'surfaces', 'apex.vtx'))].mean(0)
    if nrm @ (apex - cen) < 0:
        nrm = -nrm                         # + = from the valve plane towards the apex
    el8 = json.load(open(os.path.join(hd, 'torso', 'summary_08.json')))['electrodes']
    elec = {k: full[el8[k]['node']] for k in ('V1', 'V2')}
    net = dict(np.load(os.path.join(hd, 'purkinje', 'network.npz')))
    pmj = net['nodes'][net['pmj']]
    return dict(P=P, nvol=nvol, pv_c=cen, pv_n=nrm, rim=rim, elec=elec, pmj=pmj, n=n_heart)


def frac_time(act, w, f):
    ok = np.isfinite(act) & (act >= 0) & (act < 1e4)
    o = np.argsort(act[ok])
    cw = np.cumsum(w[ok][o]) / w[ok].sum()
    return float(act[ok][o][np.searchsorted(cw, f)])


def med(x):
    x = pd.to_numeric(pd.Series(x), errors='coerce').dropna()
    return float(x.median()) if len(x) else math.nan


def main():
    lead_rows, site_rows, waves = [], [], {}
    for h in HEARTS:
        g = heart_geometry(h)
        df = pd.read_csv(os.path.join(REPO, 'analysis', 'grids_2026-10-07', f'purk_{h}_cb.csv'))
        df['grp'] = [group(r) for _, r in df.iterrows()]
        for _, r in df[df['grp'].notna()].iterrows():
            E = ecg(r['run'])
            qrs = int(r['true_qrs_duration_ms'])
            best = (math.inf, None)
            for k in PRE:
                x = E[k] - E[k][0]
                seg = x[:qrs + 1]
                i = int(np.argmax(np.abs(seg)))
                lead_rows.append({'heart': h, 'group': r['grp'], 'id': r['id'], 'position': r['position'],
                                  'depth_target': r['depth_target'], 'lead': k, 't_max_ms': i,
                                  'sign': '+' if seg[i] > 0 else '-', 'amp_mV': round(float(seg[i]), 3),
                                  'peak_to_peak_mV': round(float(seg.max() - seg.min()), 3)})
                if i / qrs < best[0]:
                    best = (i / qrs, k, i)
                waves.setdefault((h, r['grp']), {}).setdefault(k, []).append(x)
            act, field = activation(r['run'])
            node = int(r['node'])
            xs = g['P'][node]
            stims = os.path.join(RUNS, r['run'], 'pmj_stims.json')
            exit_ms = min(s['start'] for s in json.load(open(stims))) if os.path.exists(stims) else math.nan
            row = {'heart': h, 'group': r['grp'], 'id': r['id'], 'position': r['position'],
                   'level_z': r['level_z'], 'depth_target': r['depth_target'], 'uvc_z': round(r['z'], 3),
                   'phi_deg': round(r['phi_deg'], 1), 'field': field,
                   'true_qrs_ms': qrs, 'detected_qrs_ms': r['detected_qrs_duration_ms'],
                   'pseudo_delta_true_ms': r['true_pseudo_delta_ms'], 'pseudo_delta_true_lead': r['true_pseudo_delta_lead'],
                   'pseudo_delta_detected_ms': r['detected_pseudo_delta_ms'],
                   'mdi_true': round(r['true_mdi_daniels'], 3), 'mdi_true_lead': r['true_mdi_daniels_lead'],
                   'mdi_detected': round(r['detected_mdi_daniels'], 3), 'mdi_detected_lead': r['detected_mdi_daniels_lead'],
                   'mdi_check': round(best[0], 3), 'mdi_check_lead': best[1], 't_largest_precordial_ms': best[2],
                   'pv_plane_mm': round(float((xs - g['pv_c']) @ g['pv_n']), 1),
                   'pv_rim_nearest_mm': round(float(np.linalg.norm(g['rim'] - xs, axis=1).min()), 1),
                   'first_junction_ms': round(float(act[g['pmj']].min()), 1),
                   'network_entry_ms': round(float(act[g['pmj']].min()) + D_RET_MS, 1),
                   'first_network_exit_ms': exit_ms,
                   't10_volume_ms': round(frac_time(act, g['nvol'], 0.10), 1),
                   't50_volume_ms': round(frac_time(act, g['nvol'], 0.50), 1),
                   'total_activation_ms': round(float(act[np.isfinite(act) & (act < 1e4)].max()), 1)}
            for k in ('V1', 'V2'):
                row[f'{k}_dz_mm'] = round(float(xs[2] - g['elec'][k][2]), 1)       # + = site above the electrode
                row[f'{k}_dist_mm'] = round(float(np.linalg.norm(xs - g['elec'][k])), 1)
            site_rows.append(row)
        say(f'{h}: electrodes (torso frame mm, +z superior) V1 {np.round(g["elec"]["V1"], 1).tolist()}, '
            f'V2 {np.round(g["elec"]["V2"], 1).tolist()}; PV-rim centre {np.round(g["pv_c"], 1).tolist()}')
        bazan(h, df)
        mono(h, df)
        del g
    L = pd.DataFrame(lead_rows)
    S = pd.DataFrame(site_rows)
    L.to_csv(os.path.join(OUT, 'per_lead.csv'), index=False)
    S.to_csv(os.path.join(OUT, 'sites.csv'), index=False)
    bad = S[(S['mdi_check'] - S['mdi_true']).abs() > 0.006]
    say(f'MDI check against the CSV: {len(S) - len(bad)}/{len(S)} sites agree to 0.006 '
        f'(mismatches: {bad[["heart", "id", "mdi_true", "mdi_check"]].values.tolist()})')

    ls = (L.groupby(['heart', 'group', 'lead'])
           .agg(t_max_median_ms=('t_max_ms', 'median'), positive_n=('sign', lambda s: int((s == '+').sum())),
                n=('sign', 'size'), amp_median_mV=('amp_mV', 'median'))
           .reset_index())
    ls.to_csv(os.path.join(OUT, 'lead_summary.csv'), index=False)
    say('\nPer lead, median time from the stimulus to the largest deflection (ms), sign count (+/n), median amplitude (mV):')
    for h in HEARTS:
        for gk in GROUPS:
            t = ls[(ls.heart == h) & (ls.group == gk)].set_index('lead')
            say(f'  {h} {GROUPS[gk]:<18}' + '  '.join(f'{k} {t.loc[k, "t_max_median_ms"]:.0f} '
                f'{t.loc[k, "positive_n"]}/{t.loc[k, "n"]}+ {t.loc[k, "amp_median_mV"]:+.2f}' for k in PRE))
    say('\nPer group medians: true QRS, pseudo-delta true / detected, MDI true (lead counts), t largest precordial,'
        ' first junction, first network exit, t10 / t50 volume, PV plane (+ below), V1 / V2 dz (+ site above):')
    for h in HEARTS:
        for gk in GROUPS:
            t = S[(S.heart == h) & (S.group == gk)]
            leads = t['mdi_true_lead'].value_counts().to_dict()
            say(f'  {h} {GROUPS[gk]:<18} n {len(t)}: QRS {med(t.true_qrs_ms):.0f}, PdW {med(t.pseudo_delta_true_ms):.0f}/'
                f'{med(t.pseudo_delta_detected_ms):.0f}, MDI {med(t.mdi_true):.2f} {leads}, tmax {med(t.t_largest_precordial_ms):.0f}, '
                f'junction {med(t.first_junction_ms):.1f}, exit {med(t.first_network_exit_ms):.1f}, '
                f't10/t50 {med(t.t10_volume_ms):.0f}/{med(t.t50_volume_ms):.0f}, PV {med(t.pv_plane_mm):+.1f}, '
                f'dz V1/V2 {med(t.V1_dz_mm):+.0f}/{med(t.V2_dz_mm):+.0f}, dist {med(t.V1_dist_mm):.0f}/{med(t.V2_dist_mm):.0f}')
    say('\nRVOT sites one by one:')
    for _, s in S[S.group == 'rvot'].iterrows():
        say(f'  {s.heart} {s.id:<22} z {s.uvc_z:.2f} PV {s.pv_plane_mm:+5.1f} (rim {s.pv_rim_nearest_mm:4.1f}) '
            f'junction {s.first_junction_ms:5.1f} exit {s.first_network_exit_ms:5.1f} t10/t50 {s.t10_volume_ms:3.0f}/{s.t50_volume_ms:3.0f} '
            f'QRS {s.true_qrs_ms} PdW {s.pseudo_delta_true_ms:.0f}/{s.pseudo_delta_detected_ms:.0f} MDI {s.mdi_true:.2f} '
            f'{s.mdi_true_lead} tmax {s.t_largest_precordial_ms} dzV1/V2 {s.V1_dz_mm:+.0f}/{s.V2_dz_mm:+.0f} [{s.field}]')
    figure(waves, S)
    open(os.path.join(OUT, 'report.txt'), 'w').write('\n'.join(REPORT) + '\n')


BAZ = []


def bazan(h, df):
    rv = df[df.family == 'rv_free_wall']
    p = rv.pivot_table(index=['position', 'level_z'], columns='depth_target',
                       values=['true_qrs_duration_ms', 'detected_qrs_duration_ms'])
    for mode in ('true', 'detected'):
        a, b = p[(f'{mode}_qrs_duration_ms', 0.9)], p[(f'{mode}_qrs_duration_ms', 0.1)]
        BAZ.append({'heart': h, 'test': f'Bazan2006 RV free wall QRS 90 vs 10 % ({mode})', 'n_pairs': len(a),
                    'median_change_ms': float((a - b).median()), 'median_change_pct': float(((a - b) / b * 100).median()),
                    'range_ms': f'{(a - b).min():.0f} to {(a - b).max():.0f}'})
    fam = ['lv_free_wall', 'lv_vein_course', 'lv_summit']             # LV wall sites with an endo / epi depth axis
    for region, col, label in (('lv_basal_superior', 'q_lead_I', 'q in lead I'),
                               ('lv_basal_inferior', 'inferior_q_any', 'Q in II, III or aVF')):
        t = df[(df.bazan_region == region) & df.family.isin(fam)]
        for mode in ('true', 'detected'):
            c = {d: (int(t[t.depth_target == d][f'{mode}_{col}'].astype(bool).sum()), int((t.depth_target == d).sum()))
                 for d in (0.9, 0.1)}
            BAZ.append({'heart': h, 'test': f'Bazan2007 {region} {label} ({mode})',
                        'n_pairs': c[0.9][1], 'd90': f'{c[0.9][0]}/{c[0.9][1]}', 'd10': f'{c[0.1][0]}/{c[0.1][1]}'})


MONO = []


def mono(h, df):
    """PC time of the 27-beat monodomain agreement check if it were run with the network (estimate only)."""
    hd = os.path.join(REPO, 'data', 'biv', h)
    n = int(open(os.path.join(hd, 'biv.pts')).readline())
    n0 = int(open(os.path.join(REPO, 'data', 'biv', 'Y5HYEDL4', 'biv.pts')).readline())
    pick = [('lv_free_wall', 'phi180', 0.5), ('lv_free_wall', 'phi180', 0.9)] + \
           [('lv_septum', 'phi0', d) for d in (0.1, 0.5, 0.9)] + [('rv_free_wall', 'q50', d) for d in (0.1, 0.5, 0.9)]
    ta = []
    for fam, pos, d in pick:
        t = df[(df.family == fam) & (df.position == pos) & (df.level_z == 0.5) & ((df.depth_target - d).abs() < 1e-6)]
        ta.append(float(t.total_activation_ms.iloc[0]))
    ta = [float(np.median(ta[:2]))] + ta       # original LV endocardial site: no network beat yet; LV free wall median
    tend = [max(160.0, math.ceil((x + 20) / 10) * 10) for x in ta]
    s = [MONO_S_PER_MS * x * n / n0 for x in tend]
    MONO.append({'heart': h, 'beats': len(ta), 'tend_ms': '/'.join(f'{x:.0f}' for x in tend),
                 'est_hours': round(sum(s) / 3600, 1), 'nodes': n})


def figure(waves, S):
    col = {'rvot': '#2a78d6', 'lvfw10': '#eb6834'}
    fig, ax = plt.subplots(3, 6, figsize=(15, 7.5), sharex=True)
    for i, h in enumerate(HEARTS):
        for j, k in enumerate(PRE):
            a = ax[i, j]
            for gk in ('rvot', 'lvfw10'):
                X = waves[(h, gk)][k]
                m = min(len(x) for x in X)
                Y = np.array([x[:m] for x in X])
                t = np.arange(m)
                a.fill_between(t, *np.percentile(Y, [25, 75], axis=0), color=col[gk], alpha=0.15, lw=0)
                a.plot(t, np.median(Y, axis=0), color=col[gk], lw=2,
                       label=f'{GROUPS[gk]} (n {len(X)})' if (i, j) == (0, 0) else None)
                tm = med(S[(S.heart == h) & (S.group == gk)].true_qrs_ms)
                a.axvline(tm, color=col[gk], lw=1, ls=':')
            a.axhline(0, color='#888', lw=0.6)
            a.set_xlim(0, 220)
            a.spines[['top', 'right']].set_visible(False)
            a.tick_params(labelsize=8, colors='#555')
            if i == 0:
                a.set_title(k, fontsize=11)
            if j == 0:
                a.set_ylabel(f'{h}\nmV', fontsize=9)
            if i == 2:
                a.set_xlabel('ms after stimulus', fontsize=8)
    fig.legend(loc='upper right', fontsize=9, frameon=False)
    fig.suptitle('Median precordial ECG, paced RVOT vs LV free-wall endocardium (10 %), network v3, cb conductor '
                 '(band = IQR, dotted = median true QRS end)', fontsize=10, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUT, 'median_v1v6_rvot_vs_lvendo10.png'), dpi=130)


if __name__ == '__main__':
    main()
    B = pd.DataFrame(BAZ)
    B.to_csv(os.path.join(OUT, 'bazan.csv'), index=False)
    M = pd.DataFrame(MONO)
    M.to_csv(os.path.join(OUT, 'mono_estimate.csv'), index=False)
    REPORT.append('\n' + B.to_string(index=False) + '\n\n' + M.to_string(index=False))
    print('\n' + B.to_string(index=False) + '\n\n' + M.to_string(index=False))
    open(os.path.join(OUT, 'report.txt'), 'w').write('\n'.join(REPORT) + '\n')
