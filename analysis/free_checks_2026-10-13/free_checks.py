#!/usr/bin/env python
"""
Read-only checks on saved network-v3 beats, 13 Oct 2026 (coordinator brief 22:47 UTC 12 Oct; nothing frozen changes).

  1 his       His beats: His -> earliest myocardium; junctions built / used, per cm2 endocardium and per cm3 myocardium
  2 qsweep    Bazan 2007 q-wave gates over q threshold 0.02 / 0.05 / 0.1 / 0.2 mV x duration rule (none / >= 10 ms) x
              band (none, Bazan 0.05-100 Hz, ours 0.5-150 Hz + 50 Hz notch; zero-phase 2nd-order Butterworth, an
              assumption) x noise (0, 20 uV; 20 realisations, call = majority); true onset (stimulus), cb ECGs
  3 fibres    fibre directions at the RVOT sites vs the outflow axis (pulmonary-valve rim normal) and at RV free-wall
              sites vs the long axis; compared with what 04_fibres.py's Doste 2019 blend gives at the site's w
  5 latency   stimulus latency +17 ms (sites < 75 % depth) / +34 ms (>= 75 %, incl. vein-course 90 %) (Herweg 2010)
              added to every onset-referenced interval (QRS onset at the stimulus, as Bazan 2007)
  6 lbbb      6G8DD8S5: is the left-bundle cut a complete left intrahisian block (LV tree unreachable from the His,
              intact for retrograde entry)? and its His beat: LV - RV onset, first LV septal breakthrough, endocardial
              spans, QRS (true / detected) and frontal axis vs the cohort group mean 144.7 +- 13.3 ms
(4, MDI under Daniels's onset rule calibrated on Zheng's real ECGs, is not run: those ECGs are not on the PC.)
Output: this folder (*.csv, report.txt). Run: python free_checks.py [his qsweep fibres latency lbbb]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402
from scipy.signal import butter, iirnotch, sosfiltfilt, filtfilt    # noqa: E402
from scipy.spatial import cKDTree                                   # noqa: E402

RUNS = os.path.join(REPO, 'runs')
GRID = os.path.join(REPO, 'analysis', 'grids_2026-10-07')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SINUS = {'Y5HYEDL4': '2026-10-08_purk_sinus5_Y5HYEDL4', '6G8DD8S5': '2026-10-09_purk_sinus_6G8DD8S5',
         '7D98EVAR': '2026-10-09_purk_sinus_7D98EVAR'}
REPORT = []


def say(s=''):
    print(s, flush=True)
    REPORT.append(str(s))


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def pts_of(h):
    return pd.read_csv(hd(h, 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3


def vtx(h, n):
    return np.loadtxt(hd(h, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)


def surf_area(h, n, P):
    t = np.loadtxt(hd(h, 'surfaces', n + '.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    return 0.5 * np.linalg.norm(np.cross(P[t[:, 1]] - P[t[:, 0]], P[t[:, 2]] - P[t[:, 0]]), axis=1).sum() / 100.0


def elems(h):
    return pd.read_csv(hd(h, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()


def activation(run):
    s = json.load(open(os.path.join(RUNS, run, 'summary_12.json')))
    if s.get('mode') == 'graph_fallback':
        return np.load(os.path.join(RUNS, run, 'act_graph.npy')).astype(float), s
    b = open(os.path.join(RUNS, run, 'act.igb'), 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float), s


def ecg(run, suf='_ecg_cb', leads=('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')):
    d = os.path.join(RUNS, run + suf, 'POSTPROC_DIR')
    return {l: np.loadtxt(os.path.join(d, f'ECG_{l}.dat'))[:, 1] for l in leads}


# ------------------------------------------------------------------ 1
def his():
    rows = []
    for h in HEARTS:
        P = pts_of(h)
        el = elems(h)
        a, b, c, d = (P[el[:, k]] for k in range(4))
        vol = float(np.abs(np.einsum('ij,ij->i', np.cross(b - a, c - a), d - a)).sum() / 6 / 1000)
        endo = surf_area(h, 'lv_endo', P) + surf_area(h, 'rv_endo', P)
        net = dict(np.load(hd(h, 'purkinje', 'network.npz')))
        sm = json.load(open(hd(h, 'purkinje', 'summary.json')))
        T, s = activation(SINUS[h])
        n = len(net['pmj'])
        rows.append({'heart': h, 'his_to_first_myocardium_ms': round(float(T.min()), 1), 'junctions_built': n,
                     'junctions_exiting_in_his_beat': s.get('coupling', {}).get('pmj_exits'),
                     'per_cm2_allowed_endo': round(n / (sm['allowed_area_cm2']['lv'] + sm['allowed_area_cm2']['rv']), 1),
                     'per_cm2_all_endo': round(n / endo, 1), 'per_cm3_myocardium': round(n / vol, 1),
                     'endo_area_cm2': round(endo, 1), 'myocardium_cm3': round(vol, 1)})
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'his_junctions.csv'), index=False)
    say('## 1 His beat and junctions'); say(D.to_string(index=False))


# ------------------------------------------------------------------ 2
SOS_OURS = butter(2, [0.5, 150.0], btype='bandpass', fs=1000.0, output='sos')
NB, NA = iirnotch(50.0, 30.0, fs=1000.0)
SOS_BAZAN = butter(2, [0.05, 100.0], btype='bandpass', fs=1000.0, output='sos')
REGIONS = {'apical_superior q_I': ('lv_apical_superior', 'I', +1), 'basal_superior q_I': ('lv_basal_superior', 'I', +1),
           'basal_inferior q_inf': ('lv_basal_inferior', 'inf', +1), 'apical_inferior q_inf': ('lv_apical_inferior', 'inf', +1),
           'basal_superior q_inf': ('lv_basal_superior', 'inf', -1)}
BAZAN = {'apical_superior q_I': (88, 26), 'basal_superior q_I': (90, 16), 'basal_inferior q_inf': (81, 37),
         'apical_inferior q_inf': (92, 33), 'basal_superior q_inf': (None, None)}


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - hw), 100 * (c + hw))


def q_call(y, n_end, thr, dur):
    """First wave beyond +/- thr after the stimulus is negative (and, with dur, its negative excursion lasts >= dur ms)."""
    y = y[:n_end + 1] - y[0]
    lab = np.where(y >= thr, 1, np.where(y <= -thr, -1, 0))
    nz = np.nonzero(lab)[0]
    if not len(nz) or lab[nz[0]] > 0:
        return False
    if not dur:
        return True
    i = nz[0]
    a = i
    while a > 0 and y[a - 1] < 0:
        a -= 1
    b = i
    while b < len(y) - 1 and y[b + 1] < 0:
        b += 1
    return (b - a + 1) >= dur


def qsweep():
    sites = []
    for h in HEARTS:
        df = pd.read_csv(os.path.join(GRID, f'purk_{h}_cb.csv'))
        df = df[df.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit']) & df.depth_target.isin([0.1, 0.9])]
        for _, r in df.iterrows():
            E = ecg(r['run'])
            sites.append((h, r['id'], r['family'], r['bazan_region'], r['depth_target'], int(round(r['total_activation_ms'])),
                          np.stack([E['I'], E['II']])))
    rng = np.random.default_rng(20261013)
    configs = [(thr, dur, band, nz) for thr in (0.02, 0.05, 0.1, 0.2) for dur in (0, 10)
               for band in ('none', 'bazan', 'ours') for nz in (0, 20) if not (band == 'none' and nz)]
    rows = []
    for h, sid, fam, reg, dep, n_end, X in sites:
        pad = 1000
        Xp = np.hstack([np.repeat(X[:, :1], pad, 1), X, np.repeat(X[:, -1:], pad, 1)])
        noisy = {0: [Xp]}
        noisy[20] = [Xp + rng.normal(0, 0.020, Xp.shape) for _ in range(20)]
        filt = {}
        for nzl, L in noisy.items():
            for band in ('none', 'bazan', 'ours'):
                if band == 'none':
                    filt[(band, nzl)] = [x[:, pad:] for x in L]
                elif band == 'bazan':
                    filt[(band, nzl)] = [sosfiltfilt(SOS_BAZAN, x, axis=1)[:, pad:] for x in L]
                else:
                    filt[(band, nzl)] = [filtfilt(NB, NA, sosfiltfilt(SOS_OURS, x, axis=1), axis=1)[:, pad:] for x in L]
        for thr, dur, band, nzl in configs:
            cI, cF = [], []
            for x in filt[(band, nzl)]:
                I, II = x[0], x[1]
                cI.append(q_call(I, n_end, thr, dur))
                cF.append(any(q_call(y, n_end, thr, dur) for y in (II, II - I, II - I / 2)))
            rows.append({'heart': h, 'id': sid, 'family': fam, 'region': reg, 'depth': dep, 'thr': thr, 'dur': dur,
                         'band': band, 'noise': nzl, 'qI': np.mean(cI) >= 0.5, 'qinf': np.mean(cF) >= 0.5})
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'qsweep_sites.csv'), index=False)
    ref = D[(D.thr == 0.05) & (D.dur == 0) & (D.band == 'none') & (D.noise == 0)].set_index(['heart', 'id'])
    out = []
    for key, (reg, lead, sign) in REGIONS.items():
        col = 'qI' if lead == 'I' else 'qinf'
        for scope, fams in (('LV wall', ['lv_free_wall', 'lv_vein_course', 'lv_summit']), ('free wall', ['lv_free_wall'])):
            for cfg, g in D[(D.region == reg) & D.family.isin(fams)].groupby(['thr', 'dur', 'band', 'noise']):
                k90, n90 = int(g[g.depth == 0.9][col].sum()), int((g.depth == 0.9).sum())
                k10, n10 = int(g[g.depth == 0.1][col].sum()), int((g.depth == 0.1).sum())
                flips = int((g.set_index(['heart', 'id'])[col] != ref.loc[g.set_index(['heart', 'id']).index, col]).sum())
                direction = (k90 / n90 > k10 / n10) if sign > 0 else (k90 / n90 < k10 / n10)
                b90, b10 = BAZAN[key]
                c90, c10 = wilson(k90, n90), wilson(k10, n10)
                inci = (c90[0] <= b90 <= c90[1] and c10[0] <= b10 <= c10[1]) if b90 else None
                out.append({'region_feature': key, 'scope': scope, 'thr': cfg[0], 'dur': cfg[1], 'band': cfg[2], 'noise': cfg[3],
                            'n_pos': n90, 'd90': f'{k90}/{n90}', 'd10': f'{k10}/{n10}', 'flips_vs_ref': flips,
                            'direction_ok': bool(direction), 'bazan_in_ci': inci})
    S = pd.DataFrame(out)
    S.to_csv(os.path.join(HERE, 'qsweep_summary.csv'), index=False)
    say('\n## 2 Bazan 2007 q sweep (cb, true onset; ref = 0.05 mV, no duration, unfiltered, no noise)')
    for (key, scope), g in S.groupby(['region_feature', 'scope'], sort=False):
        r = g[(g.thr == 0.05) & (g.dur == 0) & (g.band == 'none') & (g.noise == 0)].iloc[0]
        say(f'{key} [{scope}] n {r.n_pos}: ref {r.d90} vs {r.d10}, direction ok in {int(g.direction_ok.sum())}/{len(g)} configs, '
            f'Bazan in CI in {int((g.bazan_in_ci == True).sum())}/{len(g)}, flips vs ref median {g.flips_vs_ref.median():.0f} '
            f'(max {g.flips_vs_ref.max()}) of {2 * r.n_pos}; range 90 % {g.d90.min()}..{g.d90.max()}, 10 % {g.d10.min()}..{g.d10.max()}')


# ------------------------------------------------------------------ 3
def fibres():
    rows = []
    for h in HEARTS:
        P = pts_of(h)
        E = pd.read_csv(hd(h, 'bivF.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
        lon = pd.read_csv(hd(h, 'bivF.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()
        w = np.clip(np.loadtxt(hd(h, 'laplace', 'w.dat')), 0, 1)
        rim = P[vtx(h, 'pv_rim')]; c = rim.mean(0); ax = np.linalg.svd(rim - c)[2][-1]
        apex = P[vtx(h, 'apex')].mean(0)
        ax = ax if ax @ (c - apex) > 0 else -ax                        # outflow axis, towards the valve
        base = P[np.concatenate([vtx(h, 'mv_rim'), vtx(h, 'tv_rim')])].mean(0)
        la = (base - apex) / np.linalg.norm(base - apex)               # long axis apex -> base
        S = json.load(open(hd(h, 'sites.json')))
        for s in [x for x in S if x['family'] in ('rvot', 'rv_free_wall') and x['depth_target'] in (0.1, 0.9)]:
            n = int(s['node'])
            sn = int(s['surface_node'])
            far = [x for x in S if x.get('surface_node') == sn and x['depth_target'] == 0.9][0]['node']
            tm = P[int(far)] - P[sn]; tm /= np.linalg.norm(tm)               # transmural direction of the position
            ids = np.where((E == n).any(1))[0]
            f = lon[ids, :3]; f = f * np.sign(f @ f[0])[:, None]; f = f.mean(0); f /= np.linalg.norm(f)
            ref = ax if s['family'] == 'rvot' else la
            ft = f - (f @ tm) * tm; ft /= np.linalg.norm(ft)
            rt = ref - (ref @ tm) * tm; rt /= np.linalg.norm(rt)
            ang = float(np.degrees(np.arccos(min(1.0, abs(ft @ rt)))))      # 0 = along the axis, 90 = circumferential
            wn = float(w[n])
            if s['family'] == 'rvot':                                    # 04_fibres.py blend: angle from circumferential
                a_rule = (60 * wn + 90 * (1 - wn)) if s['depth_target'] < 0.5 else (-60 * wn)
            else:
                a_rule = 60.0 if s['depth_target'] < 0.5 else -60.0
            exp_from_axis = 90 - abs(a_rule)
            rows.append({'heart': h, 'id': s['id'], 'family': s['family'], 'depth': s['depth_target'], 'w': round(wn, 2),
                         'angle_from_axis_deg': round(ang, 1), 'rule_angle_from_axis_deg': round(exp_from_axis, 1),
                         'doste_target_from_axis_deg': (0.0 if s['depth_target'] < 0.5 else 90.0) if s['family'] == 'rvot' else None,
                         'fibre_out_of_wall_deg': round(float(np.degrees(np.arcsin(min(1.0, abs(f @ tm))))), 1)})
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'fibres.csv'), index=False)
    say('\n## 3 Fibres (angle in the wall plane from the outflow axis for RVOT, from the long axis for RV free wall; 0 = along, 90 = circumferential)')
    say(D.groupby(['heart', 'family', 'depth'])[['w', 'angle_from_axis_deg', 'rule_angle_from_axis_deg', 'fibre_out_of_wall_deg']].median().round(1).to_string())


# ------------------------------------------------------------------ 5
def latency():
    rows = []
    for h in HEARTS:
        df = pd.read_csv(os.path.join(GRID, f'purk_{h}_cb.csv'))
        lat = np.where(df.depth_target >= 0.75, 34.0, 17.0)
        for k, c in (('qrs', 'true_qrs_duration_ms'), ('pdw', 'true_pseudo_delta_ms'), ('idt', 'true_idt_v2_ms'), ('srs', 'true_srs_ms')):
            df[f'{k}_0'] = df[c]; df[f'{k}_lat'] = df[c] + lat
        for fam in ('lv_free_wall', 'rv_free_wall', 'lv_vein_course'):
            d = df[df.family == fam]
            key = ['position', 'level_z'] if fam != 'lv_vein_course' else ['position']
            a = d[d.depth_target == 0.9].set_index(key); b = d[d.depth_target == 0.1].set_index(key)
            p = a.join(b, lsuffix='_90', rsuffix='_10', how='inner')
            r = {'heart': h, 'family': fam, 'pairs': len(p)}
            for k in ('qrs', 'pdw', 'idt', 'srs'):
                for m in ('0', 'lat'):
                    rel = 100 * (p[f'{k}_{m}_90'] - p[f'{k}_{m}_10']) / p[f'{k}_{m}_10']
                    r[f'{k}_rel_pct_{m}'] = round(float(rel.median()), 1)
                    r[f'{k}_90_{m}'] = float(p[f'{k}_{m}_90'].median()); r[f'{k}_10_{m}'] = float(p[f'{k}_{m}_10'].median())
            r['qrs_ratio_means_0'] = round(float(p.qrs_0_90.mean() / p.qrs_0_10.mean()), 4)
            r['qrs_ratio_means_lat'] = round(float(p.qrs_lat_90.mean() / p.qrs_lat_10.mean()), 4)
            rows.append(r)
        sc = df[df.family.isin(['lv_summit', 'aortic_cusp'])]
        rows.append({'heart': h, 'family': 'summit+cusp', 'pairs': len(sc), 'qrs_10_0': float(sc.qrs_0.median()), 'qrs_10_lat': float(sc.qrs_lat.median())})
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'latency.csv'), index=False)
    say('\n## 5 Stimulus latency (+17 ms < 75 % depth, +34 ms >= 75 %), true onset at the stimulus')
    say(D.to_string(index=False))


# ------------------------------------------------------------------ 6
def lbbb():
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import breadth_first_order
    h = '6G8DD8S5'
    net = dict(np.load(hd(h, 'purkinje', 'network.npz')))
    M = len(net['nodes'])
    e = net['edges']
    g = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(M, M))
    reach = breadth_first_order(g + g.T, int(net['his']), directed=False, return_predecessors=False)
    k = net['kind']
    lvd = np.where(k == 'distal_lv')[0]
    lv_prox = [i for i in range(M) if k[i] == 'proximal']
    # LV tree intact: all LV distal nodes connected among themselves and to the LV fascicles?
    sub = np.isin(e, np.where((k == 'distal_lv') | (k == 'proximal'))[0]).all(1)
    reach_lv = breadth_first_order(g + g.T, int(lvd[0]), directed=False, return_predecessors=False)
    P = pts_of(h)
    T, s = activation(SINUS[h])
    lv, rv, epi = vtx(h, 'lv_endo'), vtx(h, 'rv_endo'), vtx(h, 'epi')
    t_rv, t_epi = cKDTree(P[rv]), cKDTree(P[epi])
    lv_sep = lv[t_rv.query(P[lv])[0] < t_epi.query(P[lv])[0]]
    sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
    from ecg_depth_criteria import from_leads, measure_beat
    E = ecg(SINUS[h]); pad = 60
    leads = {l: np.concatenate([np.full(pad, v[0]), v]) for l, v in E.items()}
    m = measure_beat(from_leads(leads), 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))
    ax = json.load(open(os.path.join(RUNS, SINUS[h] + '_ecg_cb', 'axis.json')))['cb']
    t_on = float(T.min())
    res = {'lv_distal_nodes': int(len(lvd)), 'lv_distal_reachable_from_his': int(np.isin(lvd, reach).sum()),
           'lv_tree_connected_nodes_from_one_lv_node': int(len(np.intersect1d(reach_lv, np.where((k == 'distal_lv'))[0]))),
           'lbbb_cut_flag': json.load(open(hd(h, 'purkinje', 'summary.json'))).get('lbbb_cut'),
           'first_myocardium_after_his_ms': round(t_on, 1),
           'lv_minus_rv_endo_onset_ms': round(float(T[lv].min() - T[rv].min()), 1),
           'first_lv_septal_breakthrough_after_qrs_onset_ms': round(float(T[lv_sep].min() - t_on), 1),
           'lv_endo_span_ms': round(float(T[lv].max() - T[lv].min()), 1), 'rv_endo_span_ms': round(float(T[rv].max() - T[rv].min()), 1),
           'qrs_true_span_ms': round(float(T.max() - t_on), 1), 'qrs_detected_cb_ms': m['qrs_duration_ms'],
           'frontal_axis_cb_net_area_deg': [ax['frontal_axis_net_deg'], ax['frontal_axis_area_deg']],
           'cohort_group_qrs_ms': '144.7 +- 13.3 (Solis-Lemus 2026, Table 1, as relayed)', 'derval_2017_lv_septal_breakthrough_ms': '38 +- 15'}
    json.dump(res, open(os.path.join(HERE, 'lbbb_6G8DD8S5.json'), 'w'), indent=1)
    say('\n## 6 6G8DD8S5 left-bundle cut and His beat'); say(json.dumps(res, indent=1))


if __name__ == '__main__':
    todo = sys.argv[1:] or ['his', 'qsweep', 'fibres', 'latency', 'lbbb']
    for t in todo:
        globals()[t]()
    with open(os.path.join(HERE, 'report.txt'), 'a') as f:
        f.write('\n'.join(REPORT) + '\n')
