"""D37 (3) (lock thread, 2 Nov 2026): regression of ecg_depth_criteria 0.4.1 against 0.4.0 on saved v5.1 beats, and
v5.1 rescored with 0.4.1 (report only; a v5.1 sensitivity, it changes no v5.1 verdict and no v5.2 value).

Beats, and no others: (a) the 579-beat core in runs/v51_2026-10-15/06_pilot_rerun/maps, prepared and measured by the
method of 06_pilot_rerun/rescore51.py (prep() and meas()), in every (heart, network, site, mode, noise, seed) row that
its per_site.csv holds; (b) the gate-9 check's 27 site pairs in runs/v51_2026-10-15/08_monodomain/beats, both legs, by
the method of mono51.py score_site() and score(): graph leg from graph_ecg.npy, monodomain leg vm.igb x ecgW_v51.npz's W
in float64 (mono_ecg.npy, float32, where vm.igb is gone, listed); leads I, II, V1-V6, 60-sample pad of the first sample;
pace mode stim_ms 60, true mode onset 60 ms and offset at the leg's last activation + 60 ms.
0.4.1 is code/ecg_depth_criteria imported by name from the checkout; 0.4.0 is `git archive 53bab54
code/ecg_depth_criteria` unpacked in the run folder and loaded by importlib as edc040. Each side calls its own module's
from_leads, measure_beat and evaluate; the outputs compared are measure_beat's and evaluate's, flattened as
02_measure_040/regression.py run_one() flattens them, with each site's bazan_region from sites.json (None if absent).
Nothing here imports or runs rescore51.py, gates51.py or mono51.py, and nothing is written under analysis/v51_2026-10-15
or runs/v51_2026-10-15 (checked by git status before and after). Stored v5.1 values are read as committed at 53bab54.
Pass: every output other than srs_ms, srs_lead, srs_index and berruezo_srs_ge_121 identical in every beat and mode; no
srs_ms shorter under 0.4.1; srs_ms NaN (srs_lead None) in the same beats and modes; the notched-S positive control gives
100 ms in V4 under 0.4.0 and 105 ms in V3 under 0.4.1. Gate 9 recounts use D38 (1): |difference| <= 5 ms + 1e-9 ms.
Usage (repo root, venv, alone): python -B analysis/v52_2026-10-20/d37/regression041.py <commit of D37 (1)>
"""
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
import subprocess
import sys
import tarfile
import time

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, iirnotch, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', 'd37_regression')
MAPS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps')
BEATS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '08_monodomain', 'beats')
V51 = '53bab54'
BEFORE = {'README.md': 'dac2a49cc3efe1047a186fccd549042a9a94e7a08c860c001e397c16965f1818',
          'ecg_depth_criteria/__init__.py': 'e50afeab2b340d27619a4f62366caeded04b35f49d7a1b04207a81347d337e12',
          'ecg_depth_criteria/measure.py': '11d2d29f1bb4e7e9334f357465ae71379b1e3d96d02d544e3764b10b4727e58e',
          'pyproject.toml': 'eb1b804da409c8a0b4f4b44b51f52bf57fb7c792ceaae5140b649ae65d1ea809',
          'tests/test_summit_prisco.py': '2843018d269ac69198b447ea0fe1db28d4234f63e6d17e120bcb8b05a3255de9'}
SRS_KEYS = {'m.srs_ms', 'm.srs_lead', 'm.srs_index'}
FS, PADN, KEEP = 1000.0, 1000, 60
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
L8 = ['I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SOS_PLAN = butter(2, [0.05, 100.0], btype='bandpass', fs=FS, output='sos')
SOS_OLD = butter(2, [0.5, 150.0], btype='bandpass', fs=FS, output='sos'); NB, NA = iirnotch(50.0, 30.0, fs=FS)
NOISE = {'clean': (0, None), 'plan10': (10, 'plan'), 'plan20': (20, 'plan'), 'old20_bp_notch': (20, 'old')}
MEASURES = ['pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 't_largest_precordial_ms']
TOL9 = 5.0 + 1e-9


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


def flat(d, pre=''):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, f'{pre}{k}.'))
        else:
            out[pre + k] = v
    return out


def same(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    return type(a) == type(b) and a == b


def isnan(v):
    return isinstance(v, float) and math.isnan(v)


def prep(ecg, uv=0.0, seed=0, filt=None):
    """rescore51.py prep(), returning the 8 x n array (each package forms its own leads)."""
    X = np.stack([ecg[:, L12.index(l)] for l in L8]).astype(float)
    n = X.shape[1]
    if filt is None and uv == 0:
        return np.hstack([np.repeat(X[:, :1], KEEP, 1), X])
    Z = np.hstack([np.repeat(X[:, :1], PADN, 1), X, np.repeat(X[:, -1:], PADN, 1)])
    if uv:
        Z = Z + np.random.default_rng(seed).normal(0.0, uv * 1e-3, Z.shape)
    if filt == 'plan':
        Z = sosfiltfilt(SOS_PLAN, Z, axis=1)
    elif filt == 'old':
        Z = filtfilt(NB, NA, sosfiltfilt(SOS_OLD, Z, axis=1), axis=1)
    return Z[:, PADN - KEEP: PADN + n]


def measure_core(pkg, Y, mode, last, region):
    """rescore51.py meas() with the package passed in: the flattened outputs, and per_site.csv's row fields."""
    L = pkg.from_leads(dict(zip(L8, Y)))
    try:
        if mode == 'true':
            m = pkg.measure_beat(L, FS, onset_ms=KEEP, offset_ms=KEEP + last, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0))
        elif mode == 'stim':
            m = pkg.measure_beat(L, FS, stim_ms=KEEP)
        else:
            m = pkg.measure_beat(L, FS, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0))
    except ValueError as ex:
        return {'error': str(ex)}, {'error': str(ex)}
    row = {'onset_ms': m['onset_ms'] - KEEP, 'offset_any_lead_ms': m['offset_any_lead_ms'] - KEEP, 'qrs_duration_any_lead_ms': m['qrs_duration_any_lead_ms'],
           'qrs_duration_ms': m['qrs_duration_ms'], 'mdi_daniels': m['mdi_daniels'], 'pseudo_delta_ms': m['pseudo_delta_ms'], 'idt_v2_ms': m['idt_v2_ms'],
           'srs_ms': m['srs_ms'], 'q_lead_I': bool(m['q_lead_I']), 'inferior_q_any': bool(m['inferior_q_any'])}
    return flat({'m': m, 'c': pkg.evaluate(m, region)}), row


def measure_mono(pkg, ecg, last, region):
    """mono51.py score() with the package passed in: pace and true modes; flattened outputs and results51's fields."""
    pad = 60
    leads = {l: np.concatenate([np.full(pad, ecg[0, L12.index(l)]), ecg[:, L12.index(l)]]) for l in L8}
    X = pkg.from_leads(leads)
    outf, outr = {}, {}
    for mode, kw in (('pace', dict(stim_ms=float(pad))), ('true', dict(onset_ms=float(pad), offset_ms=float(last + pad)))):
        m = pkg.measure_beat(X, 1000.0, **kw)
        r = {k: float(m[k]) for k in ('pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'qrs_duration_any_lead_ms', 'mdi_daniels')}
        r['t_largest_precordial_ms'] = float(m['mdi_daniels'] * (m['offset_any_lead_ms'] - m['onset_ms']))
        outf[mode] = flat({'m': m, 'c': pkg.evaluate(m, region)}); outr[mode] = r
    return outf, outr


def igb(f):
    b = open(f, 'rb').read()
    x = int(b[:1024].decode('latin1').split('x:')[1].split()[0])
    return np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)


def compare(f40, f41):
    """Regression checks for one measurement: (keys outside the shortest-RS set that differ, srs pair)."""
    bad = []
    if ('error' in f40) or ('error' in f41):
        return ([] if f40 == f41 else ['error']), None
    for k in set(f40) | set(f41):
        if k in SRS_KEYS or k.split('.')[:2] == ['c', 'berruezo_srs_ge_121']:
            continue
        if k not in f40 or k not in f41 or not same(f40[k], f41[k]):
            bad.append(k)
    return bad, (f40['m.srs_ms'], f41['m.srs_ms'], f40['m.srs_lead'], f41['m.srs_lead'])


def stored_equal(stored, ours):
    """Stored CSV value (parsed exactly) against a recomputed one: NaN equals NaN, booleans as bool(value)."""
    if isinstance(ours, bool):
        return (stored == 'True') if isinstance(stored, str) else bool(stored) == ours
    if stored is None or (isinstance(stored, float) and math.isnan(stored)):
        return ours is None or (isinstance(ours, float) and math.isnan(ours))
    return float(stored) == float(ours)


def main(commit1):
    t0 = time.time()
    os.makedirs(RUN, exist_ok=True)
    rep = {'rule': 'D37 (3), lock thread, 2 Nov 2026; gate 9 counted by D38 (1)', 'D37_1_commit': commit1, 'v51_commit': V51}
    # ---- tree checks
    st51 = git('status', '--porcelain', '--', 'analysis/v51_2026-10-15').decode()
    pk1 = git('diff', '--name-only', commit1, 'HEAD', '--', 'code/ecg_depth_criteria').decode() + git('status', '--porcelain', '--', 'code/ecg_depth_criteria').decode()
    rep['git_status_v51_before'] = st51; rep['package_unchanged_since_D37_1'] = (pk1 == '')
    if st51 or pk1:
        sys.exit(f'stop and report: v5.1 tree status {st51!r} / package changes since {commit1} {pk1!r}')
    # ---- the two packages
    sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
    import ecg_depth_criteria as edc041                                                      # noqa: E402
    pkgdir = os.path.join(RUN, 'pkg_040')
    if not os.path.exists(os.path.join(pkgdir, 'code', 'ecg_depth_criteria')):
        tarfile.open(fileobj=io.BytesIO(git('archive', V51, 'code/ecg_depth_criteria'))).extractall(pkgdir, filter='data')
    root40 = os.path.join(pkgdir, 'code', 'ecg_depth_criteria')
    files40 = {}
    for dp, _, fs in os.walk(root40):
        for f in sorted(fs):
            p = os.path.join(dp, f); files40[os.path.relpath(p, root40)] = sha(open(p, 'rb').read())
    rep['pkg_040_files_sha256'] = files40
    bad_before = {k: files40.get(k) for k, v in BEFORE.items() if files40.get(k) != v}
    if bad_before:
        sys.exit(f'stop and report: 0.4.0 copy differs from D37 Hashes (before): {bad_before}')
    spec = importlib.util.spec_from_file_location('edc040', os.path.join(root40, 'ecg_depth_criteria', '__init__.py'),
                                                  submodule_search_locations=[os.path.join(root40, 'ecg_depth_criteria')])
    edc040 = importlib.util.module_from_spec(spec); sys.modules['edc040'] = edc040; spec.loader.exec_module(edc040)
    if not (edc040.__version__ == '0.4.0' and edc041.__version__ == '0.4.1'):
        sys.exit(f'stop and report: versions {edc040.__version__} / {edc041.__version__}')
    P = {'0.4.0': edc040, '0.4.1': edc041}
    rep['versions'] = {k: v.__version__ for k, v in P.items()}
    # ---- positive control: test_notched_s.py's first beat
    sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria', 'tests'))
    import synthetic as S                                                                    # noqa: E402
    o = S.ONSET
    v4 = [(o, 0), (o + 60, 0.2), (o + 85, 0.9), (o + 100, -0.4), (o + 112, -0.03), (o + 125, -0.9), (o + 150, 0)]
    ctl = {v: (lambda m: [m['srs_lead'], round(float(m['srs_ms']), 2)])(p.measure_beat(S.beat(V4=v4), S.FS, stim_ms=o)) for v, p in P.items()}
    rep['positive_control'] = {'got': ctl, 'expected': {'0.4.0': ['V4', 100.0], '0.4.1': ['V3', 105.0]},
                               'pass': ctl['0.4.0'][0] == 'V4' and abs(ctl['0.4.0'][1] - 100) <= 0.5 and ctl['0.4.1'][0] == 'V3' and abs(ctl['0.4.1'][1] - 105) <= 0.5}
    # ---- (a) the core beats, every per_site.csv row
    ps = pd.read_csv(io.BytesIO(git('show', f'{V51}:analysis/v51_2026-10-15/06_pilot_rerun/rescore/per_site.csv')), float_precision='round_trip')
    sites = {h: {s['id']: s for s in json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))} for h in ps.heart.unique()}
    regress = {'measurements': 0, 'other_keys_differ': [], 'srs_shorter_041': [], 'nan_pattern_differs': [], 'version_rows_wrong': 0}
    repro = {'per_site_rows': int(len(ps)), 'rows_not_reproduced': []}
    changed, rows041 = [], []
    fo = gzip.open(os.path.join(RUN, 'core_measurements.jsonl.gz'), 'wt')
    beats = ps.groupby(['heart', 'network', 'site'], sort=False)
    rep['core_beats'] = int(beats.ngroups)
    for (h, net, sid), g in beats:
        d = os.path.join(MAPS, h if net == 'net' else f'{h}_{net}')
        ecg = np.load(os.path.join(d, sid + '.ecg.npy')).astype(float)
        last = float(np.load(os.path.join(d, sid + '.T.npy')).astype(float).max())
        region = sites[h].get(sid, {}).get('bazan_region')
        Ycache = {}
        for i, r in g.iterrows():
            seed = int(r['seed']); key = (r['noise'], seed)
            if key not in Ycache:
                uv, filt = NOISE[r['noise']]
                Ycache[key] = prep(ecg, uv, max(seed, 0), filt)
            res = {v: measure_core(p, Ycache[key], r['mode'], last, region) for v, p in P.items()}
            for v in P:
                if P[v].__version__ != v:
                    sys.exit(f'stop and report: a {v} row was scored by {P[v].__version__}')
                vals = {k: (x.item() if hasattr(x, 'item') else x) for k, x in res[v][0].items()}
                fo.write(json.dumps({'version': P[v].__version__, 'heart': h, 'network': net, 'site': sid, 'mode': r['mode'], 'noise': r['noise'],
                                     'seed': seed, **{k: (None if isnan(x) else x) for k, x in vals.items() if isinstance(x, (int, float, str, bool, type(None)))}}) + '\n')
            regress['measurements'] += 1
            bad, sp = compare(res['0.4.0'][0], res['0.4.1'][0])
            tag = [h, net, sid, r['mode'], r['noise'], seed]
            if bad:
                regress['other_keys_differ'].append(tag + [sorted(bad)[:5]])
            if sp is not None:
                a, b = float(sp[0]), float(sp[1])
                if isnan(a) != isnan(b) or ((sp[2] is None) != (sp[3] is None)):
                    regress['nan_pattern_differs'].append(tag)
                elif not isnan(a) and b < a:
                    regress['srs_shorter_041'].append(tag + [a, b])
                elif not isnan(a) and b != a:
                    changed.append(dict(zip(['heart', 'network', 'site', 'mode', 'noise', 'seed'], tag), srs_040=a, srs_041=b, lead_040=sp[2], lead_041=sp[3]))
            row40 = res['0.4.0'][1]
            stored = {k: (None if pd.isna(r[k]) else r[k]) for k in row40 if k in r.index}
            if 'error' in row40:
                ok = 'error' in r.index and isinstance(r['error'], str) and r['error'] == row40['error']
            else:
                ok = all(stored_equal(r[k], row40[k]) for k in row40) and (pd.isna(r['error']) if 'error' in r.index else True)
            if not ok:
                repro['rows_not_reproduced'].append(tag + [{k: [stored.get(k), row40.get(k)] for k in row40 if k in stored and not stored_equal(r[k], row40[k])}])
            rows041.append({**{c: r[c] for c in ['heart', 'network', 'site', 'family', 'depth', 'position', 'level_z', 'bazan_region', 'mode', 'noise', 'seed']},
                            **res['0.4.1'][1], '_reproduced_040': ok})
    fo.close()
    # gate 6's RS term (gates51.py: site value = median over seeds; LV free wall 90 % vs 10 % pairs; median %)
    def berruezo(df, mode, noise, col):
        x = df[(df.heart == '6G8DD8S5') & (df.network == 'net') & (df['mode'] == mode) & (df.noise == noise)].copy()
        if 'error' in x:
            x = x[x['error'].isna()]
        x[['position', 'level_z']] = x[['position', 'level_z']].fillna('-')
        x = x.groupby(['site', 'family', 'depth', 'position', 'level_z'], dropna=False)[col].median().reset_index()
        x = x[x.family == 'lv_free_wall']
        a = x[x.depth == 0.9].set_index(['position', 'level_z'])[col]; b = x[x.depth == 0.1].set_index(['position', 'level_z'])[col]
        j = pd.concat([a.rename('a'), b.rename('b')], axis=1, join='inner').dropna()
        return round(float((100 * (j.a - j.b) / j.b).median()), 1), int(len(j))
    R41 = pd.DataFrame(rows041)
    psr = ps.merge(R41[['heart', 'network', 'site', 'mode', 'noise', 'seed', '_reproduced_040']], on=['heart', 'network', 'site', 'mode', 'noise', 'seed'])
    g6 = {}
    for cond, (mode, noise) in {'primary: stim onset, clean': ('stim', 'clean'), 'A3 stim onset, plan noise 10uV': ('stim', 'plan10'), 'A3 true (13 Oct)': ('true', 'clean')}.items():
        g6[cond] = {'v51_stored_040': berruezo(ps, mode, noise, 'srs_ms'),
                    'rerun_040_reproduced_rows_only': berruezo(psr[psr._reproduced_040], mode, noise, 'srs_ms'),
                    'rescored_041_reproduced_rows_only': berruezo(R41[R41._reproduced_040], mode, noise, 'srs_ms')}
    rep['gate6_berruezo_6G_RS_pct (value, pairs)'] = g6
    # ---- (b) gate 9's 27 site pairs
    r51 = pd.read_csv(io.BytesIO(git('show', f'{V51}:analysis/v51_2026-10-15/08_monodomain/results51.csv')), float_precision='round_trip')
    g51 = json.loads(git('show', f'{V51}:analysis/v51_2026-10-15/08_monodomain/gate51.json'))
    mono_rows, fallback, notrep = [], [], []
    for _, r in r51.iterrows():
        h, sid = r['heart'], r['site']
        rd = os.path.join(BEATS, h, sid)
        Tg = np.load(os.path.join(rd, 'graph_T.npy')).astype(float)
        eg = np.load(os.path.join(rd, 'graph_ecg.npy')).astype(float)
        Tm = np.loadtxt(os.path.join(rd, 'init_acts_LATs-thresh.dat')); ok = Tm >= 0
        if os.path.exists(os.path.join(rd, 'vm.igb')):
            W = np.load(os.path.join(REPO, 'data', 'biv', h, 'ecgW_v51.npz'))['W'].astype(float)
            em = igb(os.path.join(rd, 'vm.igb')).astype(float) @ W.T
            del W
        else:
            em = np.load(os.path.join(rd, 'mono_ecg.npy')).astype(float); fallback.append([h, sid])
        region = sites.get(h, {}).get(sid, {}).get('bazan_region') if h in sites else None
        legs = {}
        for leg, e, last in (('graph', eg, float(Tg.max())), ('mono', em, float(Tm[ok].max()))):
            legs[leg] = {v: measure_mono(p, e, last, region) for v, p in P.items()}
        row = {'heart': h, 'site': sid}
        rr = True
        for mode in ('pace', 'true'):
            for leg in ('graph', 'mono'):
                regress['measurements'] += 1
                bad, sp = compare(legs[leg]['0.4.0'][0][mode], legs[leg]['0.4.1'][0][mode])
                tag = [h, 'gate9', sid, f'{mode} {leg}', 'clean', -1]
                if bad:
                    regress['other_keys_differ'].append(tag + [sorted(bad)[:5]])
                a, b = float(sp[0]), float(sp[1])
                if isnan(a) != isnan(b):
                    regress['nan_pattern_differs'].append(tag)
                elif not isnan(a) and b < a:
                    regress['srs_shorter_041'].append(tag + [a, b])
                elif not isnan(a) and b != a:
                    changed.append(dict(zip(['heart', 'network', 'site', 'mode', 'noise', 'seed'], tag), srs_040=a, srs_041=b, lead_040=sp[2], lead_041=sp[3]))
            for k in MEASURES + ['qrs_duration_any_lead_ms', 'mdi_daniels']:
                g40, m40 = legs['graph']['0.4.0'][1][mode][k], legs['mono']['0.4.0'][1][mode][k]
                for col, val in ((f'{mode}_{k}_graph', g40), (f'{mode}_{k}_mono', m40), (f'{mode}_{k}_diff', m40 - g40)):
                    if not stored_equal(r[col], val):
                        rr = False; notrep.append([h, sid, col, r[col], val])
                for v in P:
                    row[f'{mode}_{k}_diff_{v}'] = legs['mono'][v][1][mode][k] - legs['graph'][v][1][mode][k]
        row['reproduced_040'] = rr
        mono_rows.append(row)
    M = pd.DataFrame(mono_rows)
    use = M[M.reproduced_040]
    def count9(df, v, tol):
        d = np.concatenate([df[f'pace_{k}_diff_{v}'].to_numpy() for k in MEASURES]); f = np.isfinite(d)
        return int((np.abs(d[f]) <= tol).sum()), int(f.sum())
    def c70(df, v):
        out = {}
        for k in MEASURES:
            per = {}
            for h, x in df.groupby('heart'):
                d = x[f'pace_{k}_diff_{v}']
                per[h] = {'earlier': int((d < -1e-9).sum()), 'equal': int((d.abs() <= 1e-9).sum()), 'later': int((d > 1e-9).sum()), 'median_ms': float(d.median())}
            out[k] = per
        med = {k: float(df[f'pace_{k}_diff_{v}'].median()) for k in MEASURES}
        pooled = {h: int(sum(((x[f'pace_{k}_diff_{v}'] - med[k]).abs() <= TOL9).sum() for k in MEASURES)) for h, x in df.groupby('heart')}
        out['pooled_median_removed_within (D38 rule)'] = {'per_heart': pooled, 'all': int(sum(pooled.values())), 'medians_removed_ms': med}
        return out
    rep['gate9'] = {'v51_stored_gate51_json': {'within_5ms': g51['within_5ms'], 'pairs_scorable': g51['pairs_scorable'], 'max_abs_diff_ms': g51['max_abs_diff_ms']},
                    'sites_reproduced_040': int(M.reproduced_040.sum()), 'sites': int(len(M)), 'float32_fallback_sites': fallback,
                    'values_not_reproduced_040': notrep[:200],
                    'rerun_040 (floating point <= 5, as v5.1 counted)': count9(use, '0.4.0', 5.0),
                    'rerun_040 (D38 rule)': count9(use, '0.4.0', TOL9), 'rescored_041 (D38 rule)': count9(use, '0.4.1', TOL9),
                    'C70_reports_040': c70(use, '0.4.0'), 'C70_reports_041': c70(use, '0.4.1')}
    rep['regression'] = {**{k: (v if not isinstance(v, list) else v[:200]) for k, v in regress.items()},
                         'counts': {k: len(v) for k, v in regress.items() if isinstance(v, list)}}
    rep['reproduction_core'] = {'per_site_rows': repro['per_site_rows'], 'rows_not_reproduced': len(repro['rows_not_reproduced']),
                                'examples': repro['rows_not_reproduced'][:50]}
    C = pd.DataFrame(changed)
    if len(C):
        C.to_csv(os.path.join(HERE, 'srs_changed_041.csv'), index=False)
        rep['srs_changed'] = {f'{h} {m}': {'n': int(len(x)), 'median_ms': float((x.srs_041 - x.srs_040).median()), 'max_ms': float((x.srs_041 - x.srs_040).max())}
                              for (h, m), x in C.groupby(['heart', 'mode'])}
    rep['regression_pass'] = bool(rep['positive_control']['pass'] and not regress['other_keys_differ'] and not regress['srs_shorter_041'] and not regress['nan_pattern_differs'])
    st51b = git('status', '--porcelain', '--', 'analysis/v51_2026-10-15').decode()
    rep['git_status_v51_after'] = st51b
    rep['wall_s'] = round(time.time() - t0)
    json.dump(rep, open(os.path.join(HERE, 'regression041.json'), 'w'), indent=1, default=str)
    print(json.dumps({k: rep[k] for k in ('versions', 'positive_control', 'core_beats', 'regression_pass', 'reproduction_core', 'gate6_berruezo_6G_RS_pct (value, pairs)', 'wall_s')}, indent=1, default=str))
    if st51b:
        sys.exit(f'stop and report: the v5.1 tree changed during the run: {st51b!r}')


if __name__ == '__main__':
    main(sys.argv[1])
