"""Step 4.3 diagnostic (16-17 Oct 2026): the F01 / a03 local-CV measure on the synthetic slab (uniform fibres), applied to
the exact analytic front and to the v5.1 graph field (factors 1), for the control and the heart-failure speeds.
Writes measure_bias_check.json in this folder. Usage (repo root, venv): python -B analysis/v51_2026-10-15/04_build/measure_bias_check.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import solver51 as S, graph51 as g
P, E, ed = S.slab_mesh()
lon = np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1))
src = int(np.argmin(np.linalg.norm(P - np.array([18.0, 18.0, 10.0]), axis=1)))
x = P - P[src]; Cm = np.linalg.norm(P[E].mean(1) - P[src], axis=1); mask = (Cm > 3) & (Cm < 9)
out = {}
for nm, sp in (('control speeds', S.SPEEDS['Y5HYEDL4']), ('heart-failure speeds', S.SPEEDS['6G8DD8S5'])):
    v = np.array([sp['fibre'], sp['sheet'], sp['normal']])
    G, _ = S.slab_graph(P, E, lon, sp, {'fibre': 1.0, 'sheet': 1.0, 'normal': 1.0})
    for lab, T in (('exact analytic front', np.sqrt(np.sum((x / v) ** 2, 1))), ('graph field, factors 1', g.Tissue.solve(G, src))):
        smp = S.cv_samples(P, E, lon, T, tmin=0, tmax=1e9, mask=mask)
        out[f'{nm} | {lab}'] = {a: {'median_m_s': round(float(np.median(s)), 4), 'target_m_s': float(v[k]), 'elements': int(len(s))} for k, (a, s) in enumerate(smp.items())}
json.dump(out, open(os.path.join(HERE, 'measure_bias_check.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
