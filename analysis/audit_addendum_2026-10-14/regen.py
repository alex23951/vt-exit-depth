"""Addendum 14 Oct: regenerate the v5 activation maps and per-site ECGs that the 13 Oct in-memory grid did not save.
Same code path as analysis/v5_adopted_2026-10-13/v5_adopted.py grid(): v5_grid.Heart('E', h), junction delay 4.0 ms
everywhere, ECG weights ecgW_v5_<h>.npz (saved 13 Oct v5 lead fields; nothing rebuilt). Writes only under
analysis/audit_addendum_2026-10-14/maps/<h>/: <site>.T.npy (float32 activation, ms), <site>.ecg.npy (float32 (n,12), 1 ms,
t = 0 at the stimulus / His), and repro.csv (A1: the in-memory scoring of the regenerated beat vs purk_<h>_v5.csv).
No-network control (control heart only): v5 speeds and fibres without the network, as beats_nonet.csv of arm E.
Usage: HEART=<h> python regen.py [nonet]   (resumable)"""
import csv, importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model')); sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import numpy as np, pandas as pd
def module(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
h = os.environ['HEART']; nonet = len(sys.argv) > 1 and sys.argv[1] == 'nonet'
VG = module('vg', os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'v5_grid.py'))
H = VG.Heart('E', h)
H.d_ant = np.full(len(H.net['pmj']), 4.0)
H.W = np.load(os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13', f'ecgW_v5_{h}.npz'))['W'].astype(float)
d = os.path.join(HERE, 'maps', h + ('_nonet' if nonet else '')); os.makedirs(d, exist_ok=True)
ref = pd.read_csv(os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'E', 'Y5HYEDL4', 'beats_nonet.csv')) if nonet else \
    pd.read_csv(os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13', f'purk_{h}_v5.csv'))
ref = ref.set_index('id')
S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
todo = ([] if nonet else [None]) + S
cols = ['total_activation_ms', 'true_qrs_duration_ms', 'true_qrs_duration_any_lead_ms', 'true_mdi_daniels', 'true_pseudo_delta_ms', 'true_idt_v2_ms', 'true_srs_ms',
        'true_q_lead_I', 'true_inferior_q_any', 'detected_qrs_duration_ms', 'detected_mdi_daniels']
rf = os.path.join(d, 'repro.csv'); done = set(pd.read_csv(rf).id) if os.path.exists(rf) else set()
t0 = time.time()
for s in todo:
    sid = 'his_driven' if s is None else s['id']
    if sid in done:
        continue
    if VG.mem_mb() < 700:
        sys.exit(f'stopped: available memory {VG.mem_mb():.0f} MB (resumable)')
    T = H.solve(None if s is None else int(s['node']), nonet=nonet)
    t, ecg = H.ecg(T)
    np.save(os.path.join(d, f'{sid}.T.npy'), T.astype(np.float32)); np.save(os.path.join(d, f'{sid}.ecg.npy'), ecg.astype(np.float32))
    sc = H.score(ecg, float(T.max()), None if s is None else s.get('bazan_region'))
    sc['total_activation_ms'] = float(T.max())
    row = {'id': sid}
    for c in cols:
        a, b = sc.get(c), (ref.loc[sid, c] if sid in ref.index and c in ref.columns else None)
        row[c + '_new'] = a; row[c + '_13oct'] = b
    new = not os.path.exists(rf)
    with open(rf, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(row)); (w.writeheader() if new else None); w.writerow(row)
print(f'{h}{" nonet" if nonet else ""}: done in {time.time() - t0:.0f} s', flush=True)
