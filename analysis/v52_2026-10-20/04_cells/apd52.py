"""v5.2 step 4, in-heart part (R1.2-R1.5 on the hearts; no beat): the per-node repolarisation template parameters.

Per node of the merged mesh: w = D19b's APD w (fields52 w_apd, side chosen per node by d_s; adopted); the R1.4 / R1.5
target APD90 (control Y5HYEDL4: mean + 14 - 28 w; HF 6G8DD8S5, 7D98EVAR: 1.110 mean + 3.5 - 7 w; mean = R1.1's bench
mean, cell52.json); the time-stretch factor k(w) after +80 ms and the splice continuity offset (to the template's held
13.9 mV at +80 ms), linearly interpolated in w from cell52.json's 0.01-step grid (R1.2's blend APD90 per w). Copies of
nodes the cut duplicated take their original's values (same w). Checks: the blended field's endo-epi difference at the
nodes (28 / 7 ms within 0.5); the interpolated k against an exact recomputation at 20 random w; no step in w beyond the
mesh's own (largest APD step along a tet edge, and where).
Outputs: data/biv/<H>/v52/apd52.npz (w, target_apd90_ms, stretch_k, splice_offset_mV per merged node; git-ignored) and
apd52_<H>.json here.
Usage (repo root, venv): python -B analysis/v52_2026-10-20/04_cells/apd52.py [HEART ...]
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import cell52 as C                                                                          # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
SET = {'Y5HYEDL4': 'control', '6G8DD8S5': 'HF', '7D98EVAR': 'HF'}


def read_elem(f):
    return np.loadtxt(f, skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)


def run(h, rec_cell, exact):
    V = os.path.join(REPO, 'data', 'biv', h, 'v52')
    w = np.load(os.path.join(V, 'fields52', 'w_apd.npy'))
    grid = rec_cell['derive']['grid']; mean = rec_cell['derive']['mean_ms']; st = SET[h]
    gw = np.array([r['w'] for r in grid])
    gk = np.array([r[st]['stretch_factor_k'] for r in grid]); go = np.array([r['splice_offset_mV (to 13.9 at +80 ms)'] for r in grid])
    target = mean + 14 - 28 * w if st == 'control' else 1.110 * mean + 3.5 - 7 * w
    k = np.interp(w, gw, gk); off = np.interp(w, gw, go)
    out = os.path.join(V, 'apd52.npz')
    np.savez(out, w=w, target_apd90_ms=target, stretch_k=k, splice_offset_mV=off)
    E = read_elem(os.path.join(V, 'biv52.elem'))
    pairs = np.unique(np.sort(np.concatenate([E[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), 1), axis=0)
    dA = np.abs(target[pairs[:, 0]] - target[pairs[:, 1]]); i = int(np.argmax(dA))
    S = os.path.join(V, 'surfaces')
    vtx = lambda n: np.loadtxt(os.path.join(S, n + '.vtx'), skiprows=2, dtype=np.int64)
    endo = np.unique(np.r_[vtx('lv_endo'), vtx('rv_endo')]); epi = vtx('epi')
    kerr = [abs(np.interp(x, gw, gk) - ke) for x, ke in exact[st]]
    res = {'heart': h, 'set': st, 'mean_ms': mean, 'w_range': [float(w.min()), float(w.max())],
           'target_apd90_ms_range': [round(float(target.min()), 3), round(float(target.max()), 3)],
           'endo_surface_nodes_median_target_ms': round(float(np.median(target[endo])), 3), 'epi_surface_nodes_median_target_ms': round(float(np.median(target[epi])), 3),
           'endo_minus_epi_at_w0_w1_ms': round(float((mean + 14 if st == 'control' else 1.110 * mean + 3.5) - (mean - 14 if st == 'control' else 1.110 * mean - 3.5)), 3),
           'check_difference_within_0.5ms_of_target': None,
           'max_|k_interp - k_exact|_at_20_random_w': float(max(kerr)),
           'largest_APD_step_along_a_tet_edge_ms': round(float(dA[i]), 3), 'its_nodes_w': [round(float(w[pairs[i, 0]]), 3), round(float(w[pairs[i, 1]]), 3)],
           'median_APD_step_along_tet_edges_ms': round(float(np.median(dA)), 4), 'p99_APD_step_ms': round(float(np.percentile(dA, 99)), 3),
           'file': os.path.relpath(out, REPO), 'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest()}
    tgt = 28.0 if st == 'control' else 7.0
    res['check_difference_within_0.5ms_of_target'] = bool(abs(res['endo_minus_epi_at_w0_w1_ms'] - tgt) <= 0.5)
    json.dump(res, open(os.path.join(HERE, f'apd52_{h}.json'), 'w'), indent=1)
    print(h, json.dumps(res), flush=True)


def exact_k(rec_cell):
    """k recomputed exactly (cell52.derive's arithmetic) at 20 random w per set."""
    te, ve = C.last_beat(os.path.join(REPO, rec_cell['baseline']['ENDO']['trace_dir (last two beats, 1 ms)']))
    tp, vp = C.last_beat(os.path.join(REPO, rec_cell['baseline']['EPI']['trace_dir (last two beats, 1 ms)']))
    _, ue = C.apd90(te, ve); _, up = C.apd90(tp, vp)
    tt = np.arange(-20, 900, 0.01)
    Ve, Vp = np.interp(tt + ue, te, ve), np.interp(tt + up, tp, vp)
    mean = rec_cell['derive']['mean_ms']
    rng = np.random.default_rng(20261021)
    out = {'control': [], 'HF': []}
    for x in rng.random(20):
        a_b, _ = C.apd90(tt, (1 - x) * Ve + x * Vp)
        for nm, T in (('control', mean + 14 - 28 * x), ('HF', 1.110 * mean + 3.5 - 7 * x)):
            out[nm].append((x, (T - 80.0) / (a_b - 80.0)))
    return out


if __name__ == '__main__':
    rc = json.load(open(os.path.join(HERE, 'cell52.json')))
    ex = exact_k(rc)
    for h in sys.argv[1:] or HEARTS:
        run(h, rc, ex)
