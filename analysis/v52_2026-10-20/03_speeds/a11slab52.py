"""v5.2 arm A11 (Caldwell 2009 speeds): R4.1's slab refit and acceptance A before any A11 beat (C67 (5); stencil by R-L9,
adopted for A11 by D36 (e), Alex "Adopt all", 26 Oct 2026 22:00:57 UTC). Set-up only: no heart beat.

Speeds (section 13's A11 row, C67 (5)): control 0.80 / 0.24 / 0.34, HF 0.80 / 0.173 / 0.235 m/s (fibre / in-wall
cross-fibre / transmural); network speeds unchanged (R4.5).
R-L9: each heart starts on its primary's stencil (params/v52_graph_factors.json: control 2-ring, HF 3-ring) at A11's
speeds and changes stencil only if acceptance A fails on it (control -> 3-ring, R4.2; HF -> 2-ring, R-L9's reading);
if acceptance A fails on both, stop and report (R4.2; 15.1), with no region or per-heart factors.
Everything else is slab52.py's code, called unchanged: solver51.calibrate() (36 x 36 x 20 mm slab, seed 0, nodal
metric), acceptance_A52() (fresh slab, seed 1; principal +-1.5 %, rays +-3 %, rotating wall +-2 % on the v5.2 LV
profile), fallback_3ring() (SlabGraph3).
Outputs: a11slab52.json here; params/v52_graph_factors_A11.json (written only if every heart passes on a stencil).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/03_speeds/a11slab52.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slab52 as SL                                                                         # noqa: E402

S, g, REPO = SL.S, SL.g, SL.REPO
A11 = {'Y5HYEDL4': {'fibre': 0.80, 'sheet': 0.24, 'normal': 0.34},
       '6G8DD8S5': {'fibre': 0.80, 'sheet': 0.173, 'normal': 0.235},
       '7D98EVAR': {'fibre': 0.80, 'sheet': 0.173, 'normal': 0.235}}
THREE = 'v52-3ring-1 (R4.2: graph distance <= 3, edges <= 5.25 mm)'


def fit(sp, stencil):
    t1 = time.time()
    if stencil == '2-ring':
        f, conv, hist, mesh_info = S.calibrate(sp)
        acc = SL.acceptance_A52(sp, f)
    else:
        f, conv, hist, mesh_info, acc = SL.fallback_3ring(sp)
    r = {'stencil': stencil, 'factors': f, 'converged_within_0.5pct': conv, 'iterations': len(hist), 'calibration_slab': mesh_info,
         'calibration_history': hist, 'acceptance_A_fresh_mesh': acc, 'pass': bool(acc['pass']),
         'wall_s': round(time.time() - t1, 1), 'process_peak_rss_MB_so_far': S.rss_mb()}
    print(json.dumps(sp, sort_keys=True), stencil, 'factors', {a: round(v, 4) for a, v in f.items()}, 'conv', conv, '| A principal',
          {a: acc['principal'][a]['ratio_to_target'] for a in S.AXES}, 'rays worst', acc['rays_worst_abs_dev'],
          'rotating', {k: c['ratio'] for k, c in acc['rotating_wall_v52_profile']['transmural_arrival_over_z_over_vn'].items()},
          'PASS' if acc['pass'] else 'FAIL', r['wall_s'], 's', flush=True)
    return r


def main():
    t0 = time.time()
    prim = json.load(open(os.path.join(REPO, 'params', 'v52_graph_factors.json')))['hearts']
    out = {'lock_sha256': SL.LOCK_SHA, 'arm': 'A11', 'speeds_m_s': A11, 'rule': 'C67 (5), R-L9 (D36 (e))',
           'primary_stencils': {h: prim[h]['stencil'] for h in A11}, 'hearts': {}}
    done = {}
    for h, sp in A11.items():
        first = '3-ring' if prim[h]['stencil'] == THREE else '2-ring'
        order = [first, '2-ring' if first == '3-ring' else '3-ring']
        tries = []
        for st in order:
            key = (json.dumps(sp, sort_keys=True), st)
            if key not in done:
                done[key] = fit(sp, st)
            tries.append(done[key])
            if done[key]['pass']:
                break
        ok = next((t for t in tries if t['pass']), None)
        out['hearts'][h] = {'speeds_m_s': sp, 'tried_in_order': [t['stencil'] for t in tries],
                            'stencil_passed': ok['stencil'] if ok else 'none: acceptance A fails on both stencils (stop and report, R4.2)',
                            'tries': tries}
    out['all_pass'] = all(v['stencil_passed'] in ('2-ring', '3-ring') for v in out['hearts'].values())
    out['wall_s'] = round(time.time() - t0, 1); out['peak_rss_MB'] = S.rss_mb()
    json.dump(out, open(os.path.join(HERE, 'a11slab52.json'), 'w'), indent=1)
    if out['all_pass']:
        def entry(h):
            t = next(t for t in out['hearts'][h]['tries'] if t['pass'])
            return {'factors': t['factors'], 'speeds_m_s': A11[h], 'stencil': THREE if t['stencil'] == '3-ring' else g.STENCIL_VERSION,
                    'metric': g.METRIC_NODAL, 'acceptance_A_pass': True}
        fac = {'version': 'v52-A11-factors-1 (slab calibration, nodal metric; stencil by R-L9)', 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
               'method': "slab52.py's calibrate / acceptance A at A11's Caldwell speeds (C67 (5)); each heart on its primary's stencil first, the other only if A fails (R-L9)",
               'hearts': {h: entry(h) for h in A11}}
        json.dump(fac, open(os.path.join(REPO, 'params', 'v52_graph_factors_A11.json'), 'w'), indent=1)
    print('all pass:', out['all_pass'], {h: v['stencil_passed'] for h, v in out['hearts'].items()}, out['wall_s'], 's', 'peak', out['peak_rss_MB'], 'MB', flush=True)


if __name__ == '__main__':
    main()
