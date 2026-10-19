#!/usr/bin/env bash
# Plain-language progress of the 27-site monodomain beats (works offline).
# Usage: bash ~/vt-exit-depth/analysis/v51_2026-10-15/08_monodomain/status_offline.sh
cd "$(dirname "$(readlink -f "$0")")/../../.." || exit 1
python3 - <<'EOF'
import glob, json, os, subprocess, time
B = 'runs/v51_2026-10-15/08_monodomain/beats'
BF = 'analysis/v51_2026-10-15/08_monodomain/bias_sites51.json'
bias = json.load(open(BF))['hearts'] if os.path.exists(BF) else {}
tot_b, done_b = 0, 0
for h in ('Y5HYEDL4', '6G8DD8S5', '7D98EVAR'):
    new = set(bias.get(h, {}).get('new', {}).values())
    done, bad, db = 0, [], 0
    for f in glob.glob(os.path.join(B, h, '*', 'summary_mono.json')):
        if f.split(os.sep)[-2].endswith('_test'):
            continue
        s = json.load(open(f))
        if s['status'] != 'ok':
            bad.append(f"{s['site']}: {s['status']}")
        elif s['site'] in new:
            db += 1
        else:
            done += 1
    tot_b += len(new); done_b += db
    print(f"{h}: {done} of 9 check beats finished" + (f", {db} of {len(new)} bias-subsample beats" if new else '') + (f"; problems: {bad}" if bad else ''))
if bias:
    print(f"bias subsample: {done_b} of {tot_b} beats finished")
run = subprocess.run(['pgrep', '-a', 'openCARP'], capture_output=True, text=True).stdout.strip().splitlines()
sims = sorted({a.split('-simID ')[1].split()[0] for a in run if '-simID ' in a})
for d in sims:
    started = os.path.getmtime(os.path.join(d, 'stims.json')) if os.path.exists(os.path.join(d, 'stims.json')) else None
    print('running now:', os.path.relpath(d, B), '(started ' + time.strftime('%H:%M', time.localtime(started)) + ')' if started else '')
if not sims:
    print('no beat is running now')
logs = sorted(glob.glob('runs/v51_2026-10-15/08_monodomain/offline_*.log'), key=os.path.getmtime)
if logs:
    last = [l for l in open(logs[-1]).read().splitlines() if l[:2] == '20']
    print('last job event:', last[-1] if last else '(none yet)')
EOF
