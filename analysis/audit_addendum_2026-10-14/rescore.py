"""Addendum 14 Oct, part A: rescore of the QRS-based Aim 1 gates from the regenerated v5 ECGs (maps/<h>/*.ecg.npy).
Spec fixed by the cloud audit session before any result (README.md). ecg_depth_criteria 0.3.0, default Settings.
Noise: the project's only noise code (analysis/noise_onset_2026-10-12/noise_onset.py one()): white Gaussian noise per
independent lead (I, II, V1-V6), zero-phase 2nd-order Butterworth band-pass, optional 50 Hz notch (Q 30), 1000 ms flat
pads; per spec the band is set to 0.05-100 Hz with the notch off for the plan's rule (no baseline wander in that code),
0.5-150 Hz + notch for the legacy condition. Seeds 0-9 (np.random.default_rng(seed)), same in every site and heart."""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np, pandas as pd
from scipy.signal import butter, iirnotch, filtfilt, sosfiltfilt
import ecg_depth_criteria as edc
from ecg_depth_criteria import from_leads, measure_beat
FS, PADN, KEEP = 1000.0, 1000, 60
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']; L8 = ['I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SOS_PLAN = butter(2, [0.05, 100.0], btype='bandpass', fs=FS, output='sos')
SOS_OLD = butter(2, [0.5, 150.0], btype='bandpass', fs=FS, output='sos'); NB, NA = iirnotch(50.0, 30.0, fs=FS)
SEEDS = range(10)
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
OUT = os.path.join(HERE, 'rescore'); os.makedirs(OUT, exist_ok=True)
def prep(ecg, uv=0.0, seed=0, filt=None):
    X = np.stack([ecg[:, L12.index(l)] for l in L8]).astype(float)
    n = X.shape[1]
    if filt is None and uv == 0:
        Y = np.hstack([np.repeat(X[:, :1], KEEP, 1), X])
    else:
        Z = np.hstack([np.repeat(X[:, :1], PADN, 1), X, np.repeat(X[:, -1:], PADN, 1)])
        if uv: Z = Z + np.random.default_rng(seed).normal(0.0, uv * 1e-3, Z.shape)
        if filt == 'plan': Z = sosfiltfilt(SOS_PLAN, Z, axis=1)
        elif filt == 'old': Z = filtfilt(NB, NA, sosfiltfilt(SOS_OLD, Z, axis=1), axis=1)
        Y = Z[:, PADN - KEEP: PADN + n]
    return from_leads(dict(zip(L8, Y)))
def meas(X, mode, last=None):
    try:
        if mode == 'true': m = measure_beat(X, FS, onset_ms=KEEP, offset_ms=KEEP + last, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0))
        elif mode == 'stim': m = measure_beat(X, FS, stim_ms=KEEP)
        else: m = measure_beat(X, FS, baseline_window_ms=(KEEP - 45.0, KEEP - 5.0))
    except ValueError as ex:
        return {'error': str(ex)}
    return {'onset_ms': m['onset_ms'] - KEEP, 'offset_any_lead_ms': m['offset_any_lead_ms'] - KEEP, 'qrs_duration_any_lead_ms': m['qrs_duration_any_lead_ms'],
            'qrs_duration_ms': m['qrs_duration_ms'], 'mdi_daniels': m['mdi_daniels'], 'pseudo_delta_ms': m['pseudo_delta_ms'], 'idt_v2_ms': m['idt_v2_ms'],
            'srs_ms': m['srs_ms'], 'q_lead_I': bool(m['q_lead_I']), 'inferior_q_any': bool(m['inferior_q_any'])}
PACE = ('lv_free_wall', 'rv_free_wall', 'lv_vein_course', 'lv_summit')
rows = []
def add(h, net, s, mode, noise, seed, r):
    rows.append(dict(heart=h, network=net, site=s['id'], family=s['family'], depth=s['depth_target'], position=s.get('position'), level_z=s.get('level_z'),
                     bazan_region=s.get('bazan_region'), mode=mode, noise=noise, seed=seed, **r))
t0 = time.time()
for h in H:
    S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
    sets = [('net', os.path.join(HERE, 'maps', h), [{'id': 'his_driven', 'family': 'his', 'depth_target': None}] + S)]
    if h == 'Y5HYEDL4': sets.append(('nonet', os.path.join(HERE, 'maps', h + '_nonet'), S))
    for net, d, sites in sets:
        for s in sites:
            ecg = np.load(os.path.join(d, s['id'] + '.ecg.npy')).astype(float); T = np.load(os.path.join(d, s['id'] + '.T.npy')).astype(float)
            last = float(T.max()); Xc = prep(ecg)
            add(h, net, s, 'true', 'clean', -1, meas(Xc, 'true', last))
            add(h, net, s, 'stim', 'clean', -1, meas(Xc, 'stim'))
            add(h, net, s, 'detected', 'clean', -1, meas(Xc, 'detected'))
            if net == 'net' and s['family'] in PACE:
                for k in SEEDS: add(h, net, s, 'stim', 'plan10', k, meas(prep(ecg, 10, k, 'plan'), 'stim'))
            if h == 'Y5HYEDL4' or s['family'] == 'his':
                for k in SEEDS:
                    add(h, net, s, 'detected', 'plan10', k, meas(prep(ecg, 10, k, 'plan'), 'detected'))
                    add(h, net, s, 'detected', 'plan20', k, meas(prep(ecg, 20, k, 'plan'), 'detected'))
                    add(h, net, s, 'detected', 'old20_bp_notch', k, meas(prep(ecg, 20, k, 'old'), 'detected'))
        print(h, net, f'{time.time() - t0:.0f} s', flush=True)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, 'per_site.csv'), index=False)
json.dump({'package_version': edc.__version__, 'settings': 'default', 'seeds': list(SEEDS),
           'noise_plan': 'white Gaussian 10 uV RMS per independent lead before filtering (per-sample, 1 kHz), 2nd-order zero-phase Butterworth 0.05-100 Hz, notch off, no baseline wander (not in the project code)',
           'noise_old': 'white Gaussian 20 uV, 2nd-order zero-phase Butterworth 0.5-150 Hz + 50 Hz notch Q 30 (noise_onset.py)'}, open(os.path.join(OUT, 'settings.json'), 'w'), indent=1)
print('rows', len(df), 'errors', int(df['error'].notna().sum()) if 'error' in df else 0)
