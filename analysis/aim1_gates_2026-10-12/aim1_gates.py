#!/usr/bin/env python
"""
Aim 1 gate desk checks, 12 Oct 2026 (gate rules approved by Alex 18:27 UTC, relayed by the coordinator; the rules
draft itself was not readable from the PC, so windows below are those given in the coordinator's brief or, where
marked, Durrer values already in LABNOTES). Existing network-v3 beats only: no new beats, no lead fields.

  1 durrer     control heart, His-driven beat 2026-10-08_purk_sinus5_Y5HYEDL4 (openCARP eikonal field, cb ECG)
  2 bazan07    Q waves 90 vs 10 % depth, 3 hearts, thresholds 0.05 / 0.10 mV, old (study) and cb lead fields
  3 berruezo   LV free wall 90 vs 10 % at matched positions; vein-course values; wall thickness
  4 bazan06    RV free wall 90 vs 10 %; RV wall thickness; distance to the RV network
  5 nonet      no-network control (job 1, control heart): true QRS per family; outflow MDI old LF and cb rescore
Definitions: times "after LV onset" = after the first LV endocardial activation (Durrer's reference, as in the 9 Oct
notes). Q wave = the first deflection beyond +/- threshold after the stimulus (true onset) is negative, the
ecg_depth_criteria 0.3.0 rule (its threshold is 0.05 mV); inferior leads III = II - I and aVF = II - I/2 as the package
derives them. UVC regions: basal z >= 2/3; LV posterobasal = LV (v 0), z >= 2/3, phi -150..-30 deg (inferoseptal to
inferolateral); LV posterolateral = LV, z >= 2/3, |phi| > 150; RV posterobasal = RV (v 1), z >= 2/3, phi < -20
(inferior, the RV site-grid naming); pulmonary conus = RV within 20 mm of the pulmonary-valve rim; RV A-V sulcus = RV
within 10 mm of the tricuspid rim (conus and sulcus take priority, in that order).

Output: this folder (durrer.json, bazan07_sites.csv, bazan07_summary.csv, berruezo.csv, bazan06.csv, nonet.csv,
report.txt). Run: source ~/venv_carputils/bin/activate; python analysis/aim1_gates_2026-10-12/aim1_gates.py
"""

import json
import math
import os
import sys

os.environ['HEART'] = 'Y5HYEDL4'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
B = os.path.join(REPO, 'sims', 'biv_model')
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))

import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402
from scipy.spatial import cKDTree                                   # noqa: E402
from ecg_depth_criteria import from_leads, measure_beat             # noqa: E402

RUNS = os.path.join(REPO, 'runs')
GRID = os.path.join(REPO, 'analysis', 'grids_2026-10-07')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LV_WALL = ['lv_free_wall', 'lv_vein_course', 'lv_summit']
REPORT = []


def say(s=''):
    print(s)
    REPORT.append(str(s))


def hd(h):
    return os.path.join(REPO, 'data', 'biv', h)


def vtx(h, n):
    return np.loadtxt(os.path.join(hd(h), 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)


def igb_last(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[-1].astype(float)


def read_ecg(d):
    return {l: np.loadtxt(os.path.join(d, f'ECG_{l}.dat'))[:, 1] for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}


def score(E, last_ms=None):
    """10_measure_ecg.py in process: true mode if last_ms is given, else detected mode."""
    pad = 60
    leads = {k: np.concatenate([np.full(pad, v[0]), v]) for k, v in E.items()}
    kw = dict(baseline_window_ms=(pad - 45.0, pad - 5.0))
    if last_ms is not None:
        kw.update(onset_ms=pad, offset_ms=last_ms + pad)
    return measure_beat(from_leads(leads), 1000.0, **kw)


def wilson(k, n, z=1.96):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * (c - h)), round(100 * (c + h)))


# ------------------------------------------------------------------ 1 Durrer
def durrer():
    h = 'Y5HYEDL4'
    run = '2026-10-08_purk_sinus5_Y5HYEDL4'
    T = igb_last(os.path.join(RUNS, run, 'act.igb'))
    pts = pd.read_csv(os.path.join(hd(h), 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    U = os.path.join(hd(h), 'uvc')
    z, phi, v = (np.loadtxt(os.path.join(U, n + '.dat')) for n in ('z', 'phi', 'v'))
    ph = np.degrees(phi)
    lv, rv, epi = vtx(h, 'lv_endo'), vtx(h, 'rv_endo'), vtx(h, 'epi')
    el = pd.read_csv(os.path.join(hd(h), 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    a, b_, c, d = (pts[el[:, k]] for k in range(4))
    vol = np.abs(np.einsum('ij,ij->i', np.cross(b_ - a, c - a), d - a)) / 6
    nvol = np.bincount(el.ravel(), weights=np.repeat(vol / 4, 4), minlength=len(pts))
    tri = np.loadtxt(os.path.join(hd(h), 'surfaces', 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    ta = 0.5 * np.linalg.norm(np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]]), axis=1)
    narea = np.bincount(tri.ravel(), weights=np.repeat(ta / 3, 3), minlength=len(pts))
    t0 = float(T[lv].min())
    out = {'reference': 'times after the first LV endocardial activation (LV onset)', 'lv_onset_ms_after_his': round(t0, 1),
           'T_latest_after_lv_onset_ms': round(float(T.max() - t0), 1), 'T_window': '62-80 ms (Durrer, as in LABNOTES 9 Oct)'}
    # (a) first 5 ms vs Durrer's three areas (targets of 14_purkinje.py P['divisions'])
    early = lv[T[lv] <= t0 + 5]
    tg = {'high anterior paraseptal': (60.0, 0.80), 'central left septum': (0.0, 0.50), 'posterior paraseptal 1/3': (-60.0, 0.33)}
    tnode = {}
    for k, (p_, zz) in tg.items():
        dd = (z[lv] - zz) ** 2 + (np.radians(np.angle(np.exp(1j * (phi[lv] - np.radians(p_))), deg=True)) / np.pi) ** 2
        tnode[k] = int(lv[np.argmin(dd)])
    dist = np.stack([np.linalg.norm(pts[early] - pts[n], axis=1) for n in tnode.values()], 1)
    near = dist.min(1)
    out['a_first5ms'] = {'n_nodes': int(len(early)), 'area_cm2': round(float(narea[early].sum() / 100), 2),
                         'pct_area_within_15mm_of_a_Durrer_area': round(100 * float(narea[early][near <= 15].sum() / narea[early].sum()), 1),
                         'per_area': {k: {'onset_after_lv_onset_ms': round(float(T[lv][np.linalg.norm(pts[lv] - pts[n], axis=1) <= 10].min() - t0), 1),
                                          'pct_of_first5ms_area_nearest': round(100 * float(narea[early][(np.argmin(dist, 1) == i) & (near <= 15)].sum() / narea[early].sum()), 1)}
                                      for i, (k, n) in enumerate(tnode.items())},
                         'outside_15mm_z_phi_examples': np.round(np.c_[z[early][near > 15], ph[early][near > 15]][::max(1, int((near > 15).sum() // 8))], 2).tolist()}
    # (b) LV endocardium outside the posterobasal region active by 30 / 37.5 ms
    pb = (z >= 2 / 3) & (ph >= -150) & (ph <= -30)
    keep = lv[~pb[lv]]
    out['b_lv_endo_outside_posterobasal_pct'] = {f'{t}ms': round(100 * float(narea[keep][T[keep] <= t0 + t].sum() / narea[keep].sum()), 1) for t in (30, 37.5)}
    out['b_definition'] = 'posterobasal LV = UVC z >= 2/3 and phi -150..-30 deg; area-weighted LV endocardial nodes'
    # (c) first RV epicardial breakthrough
    rve = epi[v[epi] == 1]
    i = int(rve[np.argmin(T[rve])])
    mb = json.load(open(os.path.join(hd(h), 'purkinje', 'summary.json')))['landmarks']['mb_end']
    out['c_rv_epi_breakthrough'] = {'after_lv_onset_ms': round(float(T[i] - t0), 1), 'z': round(float(z[i]), 2), 'phi_deg': round(float(ph[i]), 0),
                                    'dist_to_moderator_band_insertion_mm': round(float(np.linalg.norm(pts[i] - pts[mb])), 1),
                                    'window': '20-31 ms, anterior RV pretrabecular area'}
    # (d) last 5 % of the volume
    o = np.argsort(T)
    cw = np.cumsum(nvol[o]) / nvol.sum()
    last = o[cw > 0.95]
    dpv = cKDTree(pts[vtx(h, 'pv_rim')]).query(pts[last])[0]
    dtv = cKDTree(pts[vtx(h, 'tv_rim')]).query(pts[last])[0]
    zl, pl, vl = z[last], ph[last], v[last]
    reg = np.full(len(last), 'other', dtype=object)
    for name, m in [('LV posterolateral', (vl == 0) & (zl >= 2 / 3) & (np.abs(pl) > 150)),
                    ('LV posterobasal', (vl == 0) & (zl >= 2 / 3) & (pl >= -150) & (pl <= -30)),
                    ('RV posterobasal', (vl == 1) & (zl >= 2 / 3) & (pl < -20)),
                    ('RV A-V sulcus', (vl == 1) & (dtv <= 10)),
                    ('pulmonary conus', (vl == 1) & (dpv <= 20))]:
        reg[m] = name                                      # later assignments win: conus, then sulcus
    w = nvol[last]
    out['d_last5pct_volume'] = {'starts_after_lv_onset_ms': round(float(T[last].min() - t0), 1),
                                'pct_by_region': {r: round(100 * float(w[reg == r].sum() / w.sum()), 1) for r in pd.unique(reg)},
                                'other_median_z_phi_v': [round(float(np.median(zl[reg == 'other'])), 2) if (reg == 'other').any() else None,
                                                         round(float(np.median(pl[reg == 'other'])), 0) if (reg == 'other').any() else None]}
    # (e) His-beat QRS at detected onset
    out['e_detected_qrs_ms'] = {c: score(read_ecg(os.path.join(RUNS, run + s, 'POSTPROC_DIR')))['qrs_duration_ms']
                                for c, s in (('cb', '_ecg_cb'), ('study', '_ecg'))}
    out['e_window'] = '63-88 ms'
    json.dump(out, open(os.path.join(HERE, 'durrer.json'), 'w'), indent=1)
    say('## 1 Durrer (control heart, His-driven beat)')
    say(json.dumps(out, indent=1))


# ------------------------------------------------------------------ 2 Bazan 2007
def first_wave_sign(x, n_end, thr):
    y = x[:n_end + 1] - x[0]
    lab = np.where(y >= thr, 1, np.where(y <= -thr, -1, 0))
    nz = np.nonzero(lab)[0]
    return int(lab[nz[0]]) if len(nz) else 0


BAZAN = {'apical_superior q_I': (88, 26), 'basal_superior q_I': (90, 16), 'basal_inferior q_inf': (81, 37),
         'apical_inferior q_inf': (92, 33), 'basal_superior q_inf': (None, None)}


def bazan07():
    rows = []
    for h in HEARTS:
        df = pd.read_csv(os.path.join(GRID, f'purk_{h}_cb.csv'))
        df = df[df.family.isin(LV_WALL) & df.depth_target.isin([0.1, 0.9])]
        for _, r in df.iterrows():
            n_end = int(round(r['total_activation_ms']))
            row = {'heart': h, 'id': r['id'], 'family': r['family'], 'position': f"{r['position']}_z{r['level_z']}" if r['family'] == 'lv_free_wall' else r['position'],
                   'name': r['name'], 'region': r['bazan_region'], 'depth': r['depth_target'], 'uvc_z': round(r['z'], 2), 'phi_deg': round(r['phi_deg'])}
            for cond, suf in (('cb', '_ecg_cb'), ('study', '_ecg')):
                E = read_ecg(os.path.join(RUNS, r['run'] + suf, 'POSTPROC_DIR'))
                I, II = E['I'], E['II']
                for thr in (0.05, 0.10):
                    t = f'{cond}_{int(thr * 100):02d}'
                    row[f'qI_{t}'] = first_wave_sign(I, n_end, thr) < 0
                    row[f'qinf_{t}'] = any(first_wave_sign(x, n_end, thr) < 0 for x in (II, II - I, II - I / 2))
            row['pkg_qI_cb'], row['pkg_qinf_cb'] = bool(r['true_q_lead_I']), bool(r['true_inferior_q_any'])
            rows.append(row)
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, 'bazan07_sites.csv'), index=False)
    chk = (D.qI_cb_05 == D.pkg_qI_cb).mean(), (D.qinf_cb_05 == D.pkg_qinf_cb).mean()
    say(f'\n## 2 Bazan 2007 (check: my 0.05 mV cb calls equal the package calls at {100 * chk[0]:.0f} % (q I) / {100 * chk[1]:.0f} % (inferior) of {len(D)} beats)')
    S = []
    for key, (b90, b10) in BAZAN.items():
        reg, feat = key.split()
        col = 'qI' if feat == 'q_I' else 'qinf'
        for scope, fams in (('LV wall (fw+vein+summit)', LV_WALL), ('LV free wall only', ['lv_free_wall'])):
            d = D[(D.region == 'lv_' + reg) & D.family.isin(fams)]
            pos = sorted({(x.heart[:2], x.position) for _, x in d.iterrows()})
            for cond in ('cb', 'study'):
                for thr in ('05', '10'):
                    c = f'{col}_{cond}_{thr}'
                    per = {hh: f"{int(d[(d.heart == hh) & (d.depth == 0.9)][c].sum())}/{int(((d.heart == hh) & (d.depth == 0.9)).sum())} vs "
                               f"{int(d[(d.heart == hh) & (d.depth == 0.1)][c].sum())}/{int(((d.heart == hh) & (d.depth == 0.1)).sum())}" for hh in HEARTS}
                    k90, n90 = int(d[d.depth == 0.9][c].sum()), int((d.depth == 0.9).sum())
                    k10, n10 = int(d[d.depth == 0.1][c].sum()), int((d.depth == 0.1).sum())
                    ci90, ci10 = wilson(k90, n90), wilson(k10, n10)
                    S.append({'region_feature': key, 'scope': scope, 'conductor': cond, 'thr_mV': float('0.' + thr),
                              'positions_pooled': len(pos), **{f'{hh}_90_vs_10': per[hh] for hh in HEARTS},
                              'pooled_90': f'{k90}/{n90}', 'pct90': round(100 * k90 / n90) if n90 else None, 'ci90': ci90,
                              'pooled_10': f'{k10}/{n10}', 'pct10': round(100 * k10 / n10) if n10 else None, 'ci10': ci10,
                              'bazan_90_10': f'{b90}/{b10}' if b90 else 'absence at epi (no %)',
                              'bazan_in_ci': (ci90[0] <= b90 <= ci90[1] and ci10[0] <= b10 <= ci10[1]) if b90 and n90 else None,
                              'positions': '; '.join(f'{a} {b}' for a, b in pos)})
    S = pd.DataFrame(S)
    S.to_csv(os.path.join(HERE, 'bazan07_summary.csv'), index=False)
    say(S[['region_feature', 'scope', 'conductor', 'thr_mV', 'positions_pooled', 'pooled_90', 'ci90', 'pooled_10', 'ci10', 'bazan_90_10', 'bazan_in_ci']].to_string(index=False))
    for key in BAZAN:
        for scope in ('LV wall (fw+vein+summit)', 'LV free wall only'):
            r = S[(S.region_feature == key) & (S.scope == scope)].iloc[0]
            say(f'  positions {key} [{scope}]: {r.positions}')


# ------------------------------------------------------------------ 3 Berruezo, 4 Bazan 2006
MEAS = {'qrs': 'true_qrs_duration_ms', 'pdw': 'true_pseudo_delta_ms', 'idt': 'true_idt_v2_ms', 'srs': 'true_srs_ms'}


def pairs(df, fam):
    d = df[df.family == fam]
    key = ['position', 'level_z'] if fam in ('lv_free_wall', 'rv_free_wall') else ['position']
    a = d[d.depth_target == 0.9].set_index(key)
    b = d[d.depth_target == 0.1].set_index(key)
    return a.join(b, lsuffix='_90', rsuffix='_10', how='inner')


def berruezo_bazan06():
    rows, rows6 = [], []
    for h in HEARTS:
        df = pd.read_csv(os.path.join(GRID, f'purk_{h}_cb.csv'))
        for fam in ('lv_free_wall', 'lv_vein_course'):
            p = pairs(df, fam)
            r = {'heart': h, 'family': fam, 'n_pairs': len(p)}
            for k, c in MEAS.items():
                rel = 100 * (p[c + '_90'] - p[c + '_10']) / p[c + '_10']
                r[f'{k}_rel_median_pct'] = round(float(rel.median()), 1)
                r[f'{k}_pos_pairs'] = f'{int((rel > 0).sum())}/{int(rel.notna().sum())}'
                r[f'{k}_90_median'] = float(p[c + '_90'].median())
                r[f'{k}_10_median'] = float(p[c + '_10'].median())
            r['wall_mm_median'] = round(float(p['wall_thickness_mm_90'].median()), 1)
            r['wall_mm_range'] = f"{p['wall_thickness_mm_90'].min():.1f}-{p['wall_thickness_mm_90'].max():.1f}"
            rows.append(r)
        # Bazan 2006 RV free wall
        p = pairs(df, 'rv_free_wall')
        rel = 100 * (p['true_qrs_duration_ms_90'] - p['true_qrs_duration_ms_10']) / p['true_qrs_duration_ms_10']
        lvp = pairs(df, 'lv_free_wall')
        lvrel = 100 * (lvp['true_qrs_duration_ms_90'] - lvp['true_qrs_duration_ms_10']) / lvp['true_qrs_duration_ms_10']
        net = dict(np.load(os.path.join(hd(h), 'purkinje', 'network.npz')))
        pts = pd.read_csv(os.path.join(hd(h), 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
        rvd = net['nodes'][net['kind'] == 'distal_rv']
        rvj = net['nodes'][net['pmj'][net['kind'][net['pmj']] == 'distal_rv']]
        sn = p['surface_node_90'].astype(int).values
        dn = cKDTree(pts[rvd]).query(pts[sn])[0]
        dj = cKDTree(pts[rvj]).query(pts[sn])[0]
        rows6.append({'heart': h, 'n_pairs': len(p), 'rv_qrs_rel_median_pct': round(float(rel.median()), 1),
                      'rv_range_pct': f'{rel.min():.1f} to {rel.max():.1f}', 'lv_fw_qrs_rel_median_pct': round(float(lvrel.median()), 1),
                      'gate_-1.9_to_6.6': bool(-1.9 <= rel.median() <= 6.6), 'below_lv': bool(rel.median() < lvrel.median()),
                      'rv_wall_mm_median': round(float(p['wall_thickness_mm_90'].median()), 1),
                      'rv_wall_mm_range': f"{p['wall_thickness_mm_90'].min():.1f}-{p['wall_thickness_mm_90'].max():.1f}",
                      'dist_to_rv_network_mm_median_max': f'{np.median(dn):.1f} / {dn.max():.1f}',
                      'dist_to_rv_junction_mm_median_max': f'{np.median(dj):.1f} / {dj.max():.1f}',
                      'positions_z': sorted(set(p.index.get_level_values('level_z').astype(str)))})
    Bq = pd.DataFrame(rows)
    Bq.to_csv(os.path.join(HERE, 'berruezo.csv'), index=False)
    say('\n## 3 Berruezo (true onset): median over matched pairs of (90-10)/10 %')
    say(Bq.to_string(index=False))
    B6 = pd.DataFrame(rows6)
    B6.to_csv(os.path.join(HERE, 'bazan06.csv'), index=False)
    say('\n## 4 Bazan 2006 RV free wall (true onset)')
    say(B6.to_string(index=False))


# ------------------------------------------------------------------ 5 no-network control
def nonet():
    h = 'Y5HYEDL4'
    nn = pd.read_csv(os.path.join(GRID, f'nofast_{h}.csv'))
    pk = pd.read_csv(os.path.join(GRID, f'purk_{h}_cb.csv'))
    rows = []
    fams = ['lv_free_wall', 'lv_septum', 'rv_free_wall', 'rvot', 'aortic_cusp', 'lv_summit', 'lv_vein_course']
    for f in fams + ['summit+cusp']:
        sel = (lambda d: d.family.isin(['lv_summit', 'aortic_cusp'])) if f == 'summit+cusp' else (lambda d, f=f: d.family == f)
        a, b = nn[sel(nn)].true_qrs_duration_ms, pk[sel(pk)].true_qrs_duration_ms
        rows.append({'family': f, 'n': len(a), 'qrs_no_network_median': float(a.median()), 'qrs_network_median': float(b.median()),
                     'wider_without_network': bool(a.median() > b.median())})
    Q = pd.DataFrame(rows)
    # outflow / cusp / summit MDI without the network: old lead fields (job-1 CSV) and a cb rescore of the saved activation
    import importlib.util
    spec = importlib.util.spec_from_file_location('conductor', os.path.join(B, '15_conductor.py'))
    cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)
    W = np.load(os.path.join(hd(h), 'ecgW_nofast_cb.npz'))['W'].astype(float)
    tm = cd.Template()
    mrows = []
    for _, r in nn[nn.family.isin(['rvot', 'aortic_cusp', 'lv_summit'])].iterrows():
        T = igb_last(os.path.join(RUNS, r['run'], 'act.igb'))
        t = np.loadtxt(os.path.join(RUNS, r['run'] + '_ecg', 'POSTPROC_DIR', 'ECG_I.dat'))[:, 0]
        e = cd.ecg_of(T, t, W, tm)
        E = {l: e[:, cd.LEADS.index(l)] for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
        m = score(E, float(T.max()))
        mrows.append({'family': r['family'], 'id': r['id'], 'mdi_old': r['true_mdi_daniels'], 'mdi_cb': m['mdi_daniels'],
                      'qrs_cb': m['qrs_duration_ms'], 'qrs_csv': r['true_qrs_duration_ms']})
    M = pd.DataFrame(mrows)
    M.to_csv(os.path.join(HERE, 'nonet_mdi_sites.csv'), index=False)
    for f in ('rvot', 'aortic_cusp', 'lv_summit'):
        m = M[M.family == f]
        net = pk[pk.family == f].true_mdi_daniels.median()
        Q.loc[Q.family == f, 'mdi_no_network_old'] = round(float(m.mdi_old.median()), 3)
        Q.loc[Q.family == f, 'mdi_no_network_cb'] = round(float(m.mdi_cb.median()), 3)
        Q.loc[Q.family == f, 'mdi_network_cb'] = round(float(net), 3)
    Q.to_csv(os.path.join(HERE, 'nonet.csv'), index=False)
    say('\n## 5 No-network control (control heart, job 1, true onset; QRS = activation, lead-field independent)')
    say(Q.to_string(index=False))
    say(f'  cb rescore check: QRS equal to the job-1 CSV at {int((M.qrs_cb == M.qrs_csv).sum())}/{len(M)} sites')


if __name__ == '__main__':
    durrer()
    bazan07()
    berruezo_bazan06()
    nonet()
    open(os.path.join(HERE, 'report.txt'), 'w').write('\n'.join(REPORT) + '\n')
