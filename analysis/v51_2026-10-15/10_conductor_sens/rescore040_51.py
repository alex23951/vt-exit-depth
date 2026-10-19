"""Step 2.5 (v5.1 brief, decision H; 16 Oct 2026): read-only rescore of the saved v5 beats, 0.3.0 and 0.4.0 side by side.

COPY-BASED on analysis/audit_addendum_2026-10-14/rescore.py (14 Oct; its prep() and the three measurement modes, same
noise code and seeds). Beats: analysis/audit_addendum_2026-10-14/maps (432 sites + 3 His beats; 144 no-network beats).
Rules (q / initial r):
  030          the 0.3.0 copy (runs/v51_2026-10-15/pkg_030), defaults
  primary      0.4.0, Q_WINDOW_MS = 40 ms (Alex 15 Oct 08:30:47 UTC) + CSE recognition recog_mv 0.02 (Alex "Make primary",
               08:31:22 UTC); passed explicitly, so this script does not depend on the package defaults
  N20          sensitivity: the other N (20 ms), CSE recognition
  window_only  sensitivity: 40 ms window on the first 0.05 mV wave, no recognition step
  no_window    sensitivity: 0.4.0 with the window and recognition off (= the 0.3.0 rule)
  wave010      sensitivity: primary with wave_mv 0.10 mV
Conditions: true / stimulus / detected onset on the clean ECG (every rule); stimulus onset + 10 uV plan noise, seeds 0-9,
for the pace-map families, and detected onset + 10 uV plan noise, seeds 0-9, for the control heart and the His beats
(030 and primary). Unscorable beats are caught: every measure NaN, reason onset_not_before_offset.
Writes runs/v51_2026-10-15/02_measure_040/per_measurement.csv (all rows) and its sha256 into
analysis/v51_2026-10-15/02_measure_040/rescore_040.json. Read-only on every v5 file.
Usage (repo root, venv): python -B analysis/v51_2026-10-15/02_measure_040/rescore_040.py
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), '02_measure_040'))
import regression as R                                                  # noqa: E402  (both packages, prep(), FS / KEEP)
R.MAPS = os.path.join(R.REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', 'maps')   # Step 6 copy: path changes only

REPO = R.REPO
OUTR = os.path.join(REPO, 'runs', 'v51_2026-10-15', '10_conductor_sens', 'rules')
LEADS = R.L12
RULES = {'030': None, 'primary': dict(q_window_ms=40.0, recog_mv=0.02), 'N20': dict(q_window_ms=20.0, recog_mv=0.02),
         'window_only': dict(q_window_ms=40.0, recog_mv=None), 'no_window': dict(q_window_ms=None, recog_mv=None),
         'wave010': dict(q_window_ms=40.0, recog_mv=0.02, wave_mv=0.10)}
NOISY_RULES = ('030', 'primary')
FLAGS = ['q_lead_I', 'inferior_q_all', 'inferior_q_any', 'inferior_r_any', 'q_V1', 'q_V2', 'qs_V2']
NUMS = ['onset_ms', 'visible_onset_ms', 'q_anchor_ms', 'qrs_duration_any_lead_ms', 'q_ratio_avl_avr', 'rs_ratio_v1']
CRIT = ['valles_q_lead_I', 'valles_no_inferior_q', 'valles_4step', 'santangeli2015_no_q_v1', 'santangeli2015_2_of_3',
        'yamada2010_avl_avr_gt_1_1', 'jauregui2012_avl_avr_lt_1_45', 'bazan2007_q_lead_I', 'bazan2007_no_inferior_q',
        'bazan2007_inferior_q', 'bazan2006_q_lead_I', 'bazan2006_qs_v2', 'bazan2006_inferior_q']


def measure(rule, X, mode, last, region):
    pkg = R.edc030 if rule == '030' else R.edc
    kw = {} if RULES[rule] is None else {'settings': R.edc.Settings(**RULES[rule])}
    L = pkg.from_leads(dict(zip(R.L8, X)))
    try:
        if mode == 'true':
            m = pkg.measure_beat(L, R.FS, onset_ms=R.KEEP, offset_ms=R.KEEP + last, baseline_window_ms=(R.KEEP - 45.0, R.KEEP - 5.0), **kw)
        elif mode == 'stim':
            m = pkg.measure_beat(L, R.FS, stim_ms=R.KEEP, **kw)
        else:
            m = pkg.measure_beat(L, R.FS, baseline_window_ms=(R.KEEP - 45.0, R.KEEP - 5.0), **kw)
    except ValueError:
        return {'reason': 'onset_not_before_offset'}
    c = pkg.evaluate(m, region)
    row = {k: (m.get(k, np.nan) - R.KEEP if k in ('onset_ms', 'visible_onset_ms', 'q_anchor_ms') else m.get(k, np.nan)) for k in NUMS}
    row.update({k: bool(m[k]) for k in FLAGS})
    row.update({k: c.get(k) for k in CRIT})
    for l in LEADS:
        row[f'pol_{l}'] = m['initial_polarity'][l]
        row[f'qamp_{l}'] = m['q_amplitude_mv'][l]
        row[f'sign_{l}'] = m.get('initial_sign', {}).get(l, np.nan)
        row[f'start_{l}'] = m.get('initial_start_ms', {}).get(l, np.nan)
    why = []
    if np.isnan(row['q_ratio_avl_avr']):
        why.append('q_ratio_avl_avr 0/0 (no Q in aVL or aVR)')
    if np.isnan(row['rs_ratio_v1']):
        why.append('rs_ratio_v1: no wave in V1')
    row['reason'] = '; '.join(why)
    return row


def main():
    os.makedirs(OUTR, exist_ok=True)
    rows, t0 = [], time.time()
    for h in R.HEARTS:
        sites = R.json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
        sets = [('net', os.path.join(R.MAPS, h), [{'id': 'his_driven', 'family': 'his', 'depth_target': None}] + sites)]
        if h == 'Y5HYEDL4':
            sets.append(('nonet', os.path.join(R.MAPS, h + '_nonet'), sites))
        for net, d, S in sets:
            for s in S:
                ecg = np.load(os.path.join(d, s['id'] + '.ecg.npy')).astype(float)
                last = float(np.load(os.path.join(d, s['id'] + '.T.npy')).astype(float).max())
                region = s.get('bazan_region')
                base = dict(heart=h, network=net, site=s['id'], family=s['family'], depth=s.get('depth_target'), position=s.get('position'),
                            level_z=s.get('level_z'), bazan_region=region)
                jobs = [(R.prep(ecg), m_, 'clean', -1, list(RULES)) for m_ in ('true', 'stim', 'detected')]
                if net == 'net' and s['family'] in R.PACE:
                    jobs += [(R.prep(ecg, 10, k), 'stim', 'plan10', k, NOISY_RULES) for k in range(10)]
                if h == 'Y5HYEDL4' or s['family'] == 'his':
                    jobs += [(R.prep(ecg, 10, k), 'detected', 'plan10', k, NOISY_RULES) for k in range(10)]
                for X, mode, noise, seed, rules in jobs:
                    for rule in rules:
                        rows.append({**base, 'mode': mode, 'noise': noise, 'seed': seed, 'rule': rule, **measure(rule, X, mode, last, region)})
            print(h, net, len(rows), f'{time.time() - t0:.0f} s', flush=True)
    df = pd.DataFrame(rows)
    f = os.path.join(OUTR, 'per_measurement.csv')
    df.to_csv(f, index=False)
    sha = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    info = {'rows': len(df), 'unscorable_rows': int((df.reason == 'onset_not_before_offset').sum()), 'wall_s': round(time.time() - t0, 1),
            'file': os.path.relpath(f, REPO), 'bytes': os.path.getsize(f), 'sha256': sha, 'rules': RULES,
            'packages': {'030': R.edc030.__version__, '040': R.edc.__version__}}
    json.dump(info, open(os.path.join(HERE, 'rescore040_51.json'), 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main()
