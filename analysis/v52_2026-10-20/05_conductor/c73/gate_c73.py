"""C73 (4)'s gate before a heart's lead fields: read conductor52_<H>_c73.json and clearance_d40_<H>_c73.json.

Passes when, for both great vessels, the C73 surface matched C73's table (the build stops otherwise) and, for all six
cavities, R3.2's gated checks pass as in the step-5 builds: closed and consistently oriented (pinch edges counted as
passing), blood within +-2 % of the enclosed volume, >= 95 % of the luminal faces bordering blood (C73: the vessel's
sheet less the disc's distal faces); D40 (1)'s 12 mm check passes. "No blood outside" and the volumes are reported
(sampled torso volume inside and blood volume outside each surface), as in v5.1's C8 and the step-5 builds.
usage: HEART=<H> python -B gate_c73.py ; exit status 1 if the heart stops.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
h = os.environ['HEART']
rep = json.load(open(os.path.join(HERE, '..', f'conductor52_{h}_c73.json')))
cl = json.load(open(os.path.join(HERE, '..', f'clearance_d40_{h}_c73.json')))
g = rep['R3.1_R3.2']
fails = []
for nm, v in g.items():
    r = v['R3.2']
    for k in ('closed_and_consistent (pinch edges counted as passing)', 'blood_within_2pct', 'ge_95pct'):
        if not r[k]:
            fails.append(f'{nm}: {k}')
    print(h, nm, {k: r[k] for k in r if 'faces' not in k or 'frac' in k}, v.get('rim_cap_C69', {}).get('blood_centroids_beyond_plane_within_ring (C69)', ''))
for nm in ('aortic_root', 'pulmonary_artery'):
    if g[nm]['surface']['C73_match_at_CT_pose']['unpaired_directed_edges'] != 0:
        fails.append(f'{nm}: unpaired directed edge')
if not cl['pass']:
    fails.append('D40 (1) 12 mm check')
out = {'heart': h, 'pass': not fails, 'fails': fails}
json.dump(out, open(os.path.join(HERE, f'gate_c73_{h}.json'), 'w'), indent=1)
print(out)
sys.exit(0 if not fails else 1)
