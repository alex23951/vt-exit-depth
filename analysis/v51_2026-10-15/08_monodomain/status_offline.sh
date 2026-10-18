#!/usr/bin/env bash
# Plain-language progress of the 27-site monodomain beats (works offline).
# Usage: bash ~/vt-exit-depth/analysis/v51_2026-10-15/08_monodomain/status_offline.sh
cd "$(dirname "$(readlink -f "$0")")/../../.." || exit 1
python3 - <<'EOF'
import glob, json, os, subprocess, time
B = 'runs/v51_2026-10-15/08_monodomain/beats'
for h in ('Y5HYEDL4', '6G8DD8S5', '7D98EVAR'):
    done, bad = 0, []
    for f in glob.glob(os.path.join(B, h, '*', 'summary_mono.json')):
        if f.split(os.sep)[-2].endswith('_test'):
            continue
        s = json.load(open(f))
        if s['status'] == 'ok':
            done += 1
        else:
            bad.append(f"{s['site']}: {s['status']}")
    print(f"{h}: {done} of 9 beats finished" + (f"; problems: {bad}" if bad else ''))
run = subprocess.run(['pgrep', '-a', 'openCARP'], capture_output=True, text=True).stdout.strip().splitlines()
sims = sorted({a.split('-simID ')[1].split()[0] for a in run if '-simID ' in a})
for d in sims:
    started = os.path.getmtime(os.path.join(d, 'stims.json')) if os.path.exists(os.path.join(d, 'stims.json')) else None
    print('running now:', os.path.relpath(d, B), '(started ' + time.strftime('%H:%M', time.localtime(started)) + ')' if started else '')
if not sims:
    print('no beat is running now')
logs = sorted(glob.glob('runs/v51_2026-10-15/08_monodomain/offline_*.log'))
if logs:
    last = [l for l in open(logs[-1]).read().splitlines() if l[:2] == '20']
    print('last job event:', last[-1] if last else '(none yet)')
EOF
