"""Step 1.3 (v5.1 brief, decision G; 16 Oct 2026): v5 reference beats before (pre) and after (post) the guards.

pre   the unchanged v5 code: analysis/v5_grid_2026-10-13/v5_grid.py Heart('E', H); its graph cache entry must already
      exist, so the protected cache folder is only read
post  the guarded copy analysis/v51_2026-10-15/01_backup/v5_grid_guarded.py (new cache key, k-file guard, fibre hash
      checked against manifests/v5_data_sha256.tsv); its cache is runs/v51_2026-10-15/cache/ (starts empty)
Both: junction delay 4 ms antegrade everywhere (as v5_adopted.py:127 and regen.py:17), ECG weights
analysis/v5_adopted_2026-10-13/ecgW_v5_<H>.npz. Beats: His beat; in Y5HYEDL4 also the first site of each family.
Writes only runs/v51_2026-10-15/01_backup/<mode>/<H>/ (<id>.T.npy and <id>.ecg.npy as float32, as regen.py; scores.csv).
compare   post vs pre (bit-exact arrays and scores), pre vs the 14 Oct maps (analysis/audit_addendum_2026-10-14/maps),
          His beats vs analysis/v5_adopted_2026-10-13/grid/<H>/his_*.npy, scores vs purk_<H>_v5.csv (13 Oct)
          -> analysis/v51_2026-10-15/01_backup/compare.json
Usage (repo root, venv): HEART=<H> python -B analysis/v51_2026-10-15/01_backup/beats.py pre|post ;  ... beats.py compare
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUTR = os.path.join(REPO, 'runs', 'v51_2026-10-15', '01_backup')
V5G = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13')
V5A = os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13')
MAPS = os.path.join(REPO, 'analysis', 'audit_addendum_2026-10-14', 'maps')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
Y5_SITES = ['lv_septum_phi0_z0.25_d10', 'lv_free_wall_phi60_z0.25_d10', 'rv_free_wall_q25_z0.25_d10', 'rvot_septal_z_d10',
            'aortic_cusp_rcc_z_d10', 'lv_summit_superior_z_d10', 'lv_vein_course_proximal_aiv_z_d10']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def beat_ids(h):
    return ['his_driven'] + (Y5_SITES if h == 'Y5HYEDL4' else [])


def manifest_sha(rel):
    for l in open(os.path.join(REPO, 'manifests', 'v5_data_sha256.tsv')):
        p, _, _, d = l.rstrip('\n').split('\t')
        if p == rel:
            return d
    raise KeyError(rel)


def heart(mode, h):
    if mode == 'pre':
        VG = module('vg', os.path.join(V5G, 'v5_grid.py'))
        sp = VG.speeds('E', h)
        cache = os.path.join(V5G, 'cache', f'myo_{h}_E_{sp[1]:.4f}_{sp[2]:.4f}.npz')
        if not os.path.exists(cache):
            sys.exit(f'v5 cache entry missing ({cache}); v5_grid.Heart would write into a protected folder: stop')
        H = VG.Heart('E', h)
    else:
        VG = module('vgg', os.path.join(HERE, 'v5_grid_guarded.py'))
        H = VG.Heart('E', h, expect_fibre_sha256=manifest_sha(f'analysis/v5_grid_2026-10-13/fibres_E/{h}/bivF.lon'))
    H.d_ant = np.full(len(H.net['pmj']), 4.0)
    H.W = np.load(os.path.join(V5A, f'ecgW_v5_{h}.npz'))['W'].astype(float)
    return H


def run(mode):
    h = os.environ['HEART']
    d = os.path.join(OUTR, mode, h)
    print(f'{mode} {h}: writes only {d}', flush=True)
    os.makedirs(d, exist_ok=True)
    t0 = time.time()
    H = heart(mode, h)
    print(f'  setup {time.time() - t0:.0f} s, k = {H.k}', flush=True)
    S = {s['id']: s for s in json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))}
    rows = []
    for sid in beat_ids(h):
        s = None if sid == 'his_driven' else S[sid]
        t1 = time.time()
        T = H.solve(None if s is None else int(s['node']))
        _, ecg = H.ecg(T)
        np.save(os.path.join(d, f'{sid}.T.npy'), T.astype(np.float32))
        np.save(os.path.join(d, f'{sid}.ecg.npy'), ecg.astype(np.float32))
        row = {'id': sid, 'total_activation_ms': float(T.max())}
        row.update(H.score(ecg, float(T.max()), None if s is None else s.get('bazan_region')))
        rows.append(row)
        print(f'  {sid}: {time.time() - t1:.1f} s, total activation {T.max():.1f} ms', flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(d, 'scores.csv'), index=False)
    print(f'{mode} {h}: {len(rows)} beats in {time.time() - t0:.0f} s', flush=True)


def same(a, b):
    """Exact equality of two CSV columns (NaN == NaN)."""
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b) and not (pd.api.types.is_bool_dtype(a) or pd.api.types.is_bool_dtype(b)):
        x, y = a.to_numpy(float), b.to_numpy(float)
        return bool(np.all((x == y) | (np.isnan(x) & np.isnan(y)))), float(np.nanmax(np.abs(x - y))) if np.isfinite(x - y).any() else 0.0
    txt = lambda s: ['<missing>' if pd.isna(v) else str(v) for v in s]      # pandas 3 keeps NaN through astype(str)
    return txt(a) == txt(b), None


def compare():
    rd = lambda f: pd.read_csv(f, float_precision='round_trip')
    KEY = ['total_activation_ms', 'true_qrs_duration_ms', 'true_qrs_duration_any_lead_ms', 'true_mdi_daniels', 'true_pseudo_delta_ms',
           'true_idt_v2_ms', 'true_srs_ms', 'true_q_lead_I', 'true_inferior_q_any', 'true_inferior_q_all', 'true_q_V1', 'true_q_V2',
           'detected_qrs_duration_ms', 'detected_qrs_duration_any_lead_ms', 'detected_mdi_daniels', 'detected_pseudo_delta_ms',
           'detected_idt_v2_ms', 'detected_srs_ms', 'detected_q_lead_I', 'detected_inferior_q_any']
    out = {'arrays': {}, 'scores_post_vs_pre': {}, 'scores_vs_13oct_csv': {}}
    ok = True
    for h in HEARTS:
        for sid in beat_ids(h):
            for kind in ('T', 'ecg'):
                pre = np.load(os.path.join(OUTR, 'pre', h, f'{sid}.{kind}.npy'))
                post = np.load(os.path.join(OUTR, 'post', h, f'{sid}.{kind}.npy'))
                ref14 = np.load(os.path.join(MAPS, h, f'{sid}.{kind}.npy'))
                r = {'post_eq_pre': bool(np.array_equal(post, pre)), 'pre_eq_14oct_map': bool(np.array_equal(pre, ref14))}
                if sid == 'his_driven':
                    r['pre_eq_13oct_his'] = bool(np.array_equal(pre, np.load(os.path.join(V5A, 'grid', h, f'his_{kind}.npy'))))
                out['arrays'][f'{h}/{sid}.{kind}'] = r
                ok &= all(r.values())
        pre, post = rd(os.path.join(OUTR, 'pre', h, 'scores.csv')), rd(os.path.join(OUTR, 'post', h, 'scores.csv'))
        eq = {c: same(pre[c], post[c])[0] for c in pre.columns}
        out['scores_post_vs_pre'][h] = {'columns': len(eq), 'all_equal': all(eq.values()), 'unequal': [c for c, v in eq.items() if not v]}
        ok &= all(eq.values()) and list(pre.columns) == list(post.columns)
        ref = rd(os.path.join(V5A, f'purk_{h}_v5.csv')).set_index('id').loc[pre.id]
        common = [c for c in pre.columns if c in ref.columns and c != 'id']
        res = {c: same(pre[c].reset_index(drop=True), ref[c].reset_index(drop=True)) for c in common}
        out['scores_vs_13oct_csv'][h] = {'columns_compared': len(common), 'all_equal': all(v[0] for v in res.values()),
                                         'unequal': [c for c, v in res.items() if not v[0]],
                                         'key_measures_max_abs_diff': {c: res[c][1] for c in KEY if c in res}}
        ok &= all(v[0] for v in res.values())
    out['all_pass'] = bool(ok)
    json.dump(out, open(os.path.join(HERE, 'compare.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'arrays'}, indent=1))
    print('arrays:', sum(all(v.values()) for v in out['arrays'].values()), '/', len(out['arrays']), 'identical in every comparison')
    print('ALL PASS' if ok else 'DIFFERENCES FOUND')


if __name__ == '__main__':
    compare() if sys.argv[1] == 'compare' else run(sys.argv[1])
