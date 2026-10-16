"""Step 2.3 (v5.1 brief, decision H; 16 Oct 2026): bit-exact regression of ecg_depth_criteria 0.4.0 against 0.3.0.

Every saved v5 beat (analysis/audit_addendum_2026-10-14/maps: 432 sites + 3 His beats, and the 144 no-network beats),
prepared as the 14 Oct rescore (analysis/audit_addendum_2026-10-14/rescore.py prep(): 60 ms flat pad, the project's
noise code at 0.05-100 Hz with notch off, seeds 0-9) and measured in the same modes: true onset, stimulus onset and
detected onset on the clean ECG; stimulus onset with 10 uV noise for the pace-map families; detected onset with 10 uV
noise for the control heart and the His beats. Each measurement is made with the 0.3.0 copy
(runs/v51_2026-10-15/pkg_030, sha256 checked in Step 2) and with 0.4.0 under
  legacy          Settings(q_window_ms=None, recog_mv=None): every 0.3.0 output must be identical
  N 20 / 40 x CSE (recog_mv 0.02) / window only (None): identical except the q outputs listed in Q_MEAS and the
                  criteria that read them (Q_CRIT)
Only identity is asserted; no q-call comparison is computed here (Step 2.5 does that).
Writes only analysis/v51_2026-10-15/02_measure_040/regression.json and regression_report.md.
Usage (repo root, venv): python -B analysis/v51_2026-10-15/02_measure_040/regression.py [--limit N]
"""
import importlib.util
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAPS = os.path.join(REPO, 'analysis', 'audit_addendum_2026-10-14', 'maps')
PKG030 = os.path.join(REPO, 'runs', 'v51_2026-10-15', 'pkg_030', 'code', 'ecg_depth_criteria', 'ecg_depth_criteria')
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import ecg_depth_criteria as edc                                    # noqa: E402

spec = importlib.util.spec_from_file_location('edc030', os.path.join(PKG030, '__init__.py'), submodule_search_locations=[PKG030])
edc030 = importlib.util.module_from_spec(spec); sys.modules['edc030'] = edc030; spec.loader.exec_module(edc030)
assert edc030.__version__ == '0.3.0' and edc.__version__ == '0.4.0'

from scipy.signal import butter, sosfiltfilt                        # noqa: E402

FS, PADN, KEEP = 1000.0, 1000, 60
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
L8 = ['I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SOS_PLAN = butter(2, [0.05, 100.0], btype='bandpass', fs=FS, output='sos')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
PACE = ('lv_free_wall', 'rv_free_wall', 'lv_vein_course', 'lv_summit')
Q_MEAS = {'initial_polarity', 'q_lead_I', 'inferior_q_all', 'inferior_q_any', 'inferior_r_any', 'q_V1', 'q_V2', 'qs_V2',
          'q_amplitude_mv', 'q_ratio_avl_avr', 'rs_ratio_v1'}
Q_CRIT = {'valles_q_lead_I', 'valles_no_inferior_q', 'valles_4step', 'valles_4step_step', 'piers_q_I', 'piers_abs_q_inf',
          'piers_q_inf', 'yamada2010_avl_avr_gt_1_1', 'yamada2010_avl_avr_gt_1_75', 'yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75',
          'santangeli2015_avl_avr_gt_1_85', 'santangeli2015_rs_v1_gt_2', 'santangeli2015_no_q_v1', 'santangeli2015_2_of_3',
          'jauregui2012_avl_avr_lt_1_45', 'bazan2007_q_lead_I', 'bazan2007_no_inferior_q', 'bazan2007_inferior_q',
          'bazan2007_q_v2_unconfirmed', 'bazan2006_q_lead_I', 'bazan2006_qs_v2', 'bazan2006_inferior_q'}
CONFIGS = {'legacy': dict(q_window_ms=None, recog_mv=None), 'N20_cse': dict(q_window_ms=20.0, recog_mv=0.02),
           'N20_window_only': dict(q_window_ms=20.0, recog_mv=None), 'N40_cse': dict(q_window_ms=40.0, recog_mv=0.02),
           'N40_window_only': dict(q_window_ms=40.0, recog_mv=None)}


def prep(ecg, uv=0.0, seed=0):
    """As rescore.py prep() (14 Oct) for the clean and the 'plan' conditions."""
    X = np.stack([ecg[:, L12.index(l)] for l in L8]).astype(float)
    n = X.shape[1]
    if uv == 0:
        Y = np.hstack([np.repeat(X[:, :1], KEEP, 1), X])
    else:
        Z = np.hstack([np.repeat(X[:, :1], PADN, 1), X, np.repeat(X[:, -1:], PADN, 1)])
        Z = sosfiltfilt(SOS_PLAN, Z + np.random.default_rng(seed).normal(0.0, uv * 1e-3, Z.shape), axis=1)
        Y = Z[:, PADN - KEEP: PADN + n]
    return Y


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


def run_one(pkg, X, mode, last, region, settings=None):
    kw = {} if settings is None else {'settings': settings}
    L = pkg.from_leads(dict(zip(L8, X)))
    try:
        if mode == 'true':
            m = pkg.measure_beat(L, FS, onset_ms=KEEP, offset_ms=KEEP + last, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0), **kw)
        elif mode == 'stim':
            m = pkg.measure_beat(L, FS, stim_ms=KEEP, **kw)
        else:
            m = pkg.measure_beat(L, FS, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0), **kw)
    except ValueError as ex:
        return {'error': str(ex)}
    return flat({'m': m, 'c': pkg.evaluate(m, region)})


def allowed(key):
    part = key.split('.')
    return (part[0] == 'm' and part[1] in Q_MEAS) or (part[0] == 'c' and part[1] in Q_CRIT)


def main(limit=None):
    cfg = {n: edc.Settings(**kw) for n, kw in CONFIGS.items()}
    res = {n: {'measurements': 0, 'identical_030_keys': 0, 'unexpected': {}, 'allowed_keys_that_differed': set()} for n in CONFIGS}
    errors, nmeas, beats, t0 = [], 0, 0, time.time()
    for h in HEARTS:
        sites = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
        sets = [('net', os.path.join(MAPS, h), [{'id': 'his_driven', 'family': 'his'}] + sites)]
        if h == 'Y5HYEDL4':
            sets.append(('nonet', os.path.join(MAPS, h + '_nonet'), sites))
        for net, d, S in sets:
            for s in S:
                if limit is not None and beats >= limit:
                    break
                beats += 1
                ecg = np.load(os.path.join(d, s['id'] + '.ecg.npy')).astype(float)
                last = float(np.load(os.path.join(d, s['id'] + '.T.npy')).astype(float).max())
                region = s.get('bazan_region')
                jobs = [(prep(ecg), m_, f'{m_} clean') for m_ in ('true', 'stim', 'detected')]
                if net == 'net' and s['family'] in PACE:
                    jobs += [(prep(ecg, 10, k), 'stim', f'stim plan10 seed {k}') for k in range(10)]
                if h == 'Y5HYEDL4' or s['family'] == 'his':
                    jobs += [(prep(ecg, 10, k), 'detected', f'detected plan10 seed {k}') for k in range(10)]
                for X, mode, label in jobs:
                    ref = run_one(edc030, X, mode, last, region)
                    nmeas += 1
                    if 'error' in ref:
                        errors.append({'heart': h, 'network': net, 'site': s['id'], 'condition': label, 'error': ref['error']})
                    for n, st in cfg.items():
                        new = run_one(edc, X, mode, last, region, st)
                        r = res[n]; r['measurements'] += 1
                        if 'error' in ref or 'error' in new:
                            if ref.get('error') != new.get('error'):
                                r['unexpected'].setdefault('error status', []).append(f'{h}/{net}/{s["id"]} {label}')
                            else:
                                r['identical_030_keys'] += 1
                            continue
                        bad = []
                        for k, v in ref.items():
                            if k not in new:
                                bad.append(k)
                            elif not same(v, new[k]):
                                if n == 'legacy' or not allowed(k):
                                    bad.append(k)
                                else:
                                    r['allowed_keys_that_differed'].add(k)
                        if bad:
                            for k in bad:
                                r['unexpected'].setdefault(k, []).append(f'{h}/{net}/{s["id"]} {label}')
                        else:
                            r['identical_030_keys'] += 1
        print(h, f'{beats} beats, {nmeas} measurements, {time.time() - t0:.0f} s', flush=True)
    out = {'beats': beats, 'measurements_per_config': nmeas, 'wall_s': round(time.time() - t0, 1), 'unscorable_030': errors,
           'configs': {n: {'settings': CONFIGS[n], 'measurements': r['measurements'], 'pass': not r['unexpected'] and r['identical_030_keys'] == r['measurements'],
                           'unexpected_differences': {k: v[:5] + ([f'... {len(v)} in all'] if len(v) > 5 else []) for k, v in r['unexpected'].items()},
                           'allowed_keys_that_differed_count': len(r['allowed_keys_that_differed'])} for n, r in res.items()}}
    out['all_pass'] = all(c['pass'] for c in out['configs'].values())
    if limit is None:
        json.dump(out, open(os.path.join(HERE, 'regression.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'unscorable_030'}, indent=1))
    print('unscorable under 0.3.0:', len(errors))


if __name__ == '__main__':
    main(int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None)
