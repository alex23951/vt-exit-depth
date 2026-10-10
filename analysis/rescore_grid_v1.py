#!/usr/bin/env python
"""Re-score the 108 eikonal-grid ECGs of the first grid run (runs/2026-10-03b_eik_*_ecg) with
ecg_depth_criteria 0.1.0 and 0.2.0, using the v1 site regions (sites_v1.json) and each run's
activation range. Writes criteria_v010.json and criteria_v020.json next to the original
criteria.json (which is kept)."""
import json, os, subprocess, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKGS = {'v010': os.path.join(REPO, 'code', 'ecg_depth_criteria_0.1.0'), 'v020': os.path.join(REPO, 'code', 'ecg_depth_criteria')}
n = 0
for h in ('Y5HYEDL4', '6G8DD8S5', '7D98EVAR'):
    sites = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites_v1.json')))
    for s in sites:
        ecg = os.path.join(REPO, 'runs', f'2026-10-03b_eik_{h}_{s["id"]}_ecg')
        run = os.path.join(REPO, 'runs', f'2026-10-03b_eik_{h}_{s["id"]}')
        if not os.path.exists(os.path.join(ecg, 'criteria.json')):
            continue
        last = json.load(open(os.path.join(run, 'summary_12.json')))['total_activation_ms']
        for tag, pkg in PKGS.items():
            args = [sys.executable, os.path.join(REPO, 'sims', 'biv_model', '10_measure_ecg.py'), os.path.join(ecg, 'POSTPROC_DIR'),
                    '--stim-ms', '0', '--last-act-ms', str(last), '--out', os.path.join(ecg, f'criteria_{tag}.json')]
            if s.get('bazan_region'):
                args += ['--region', s['bazan_region']]
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, ECG_PKG=pkg))
        n += 1
print('re-scored', n, 'sites with 0.1.0 and 0.2.0')
