"""Step 1.2 (v5.1 brief, decision G; run 16 Oct 2026): sha256 manifest of the v5 files that are not in git.

Writes manifests/v5_data_sha256.tsv (path, bytes, mtime, sha256; mtime = UTC, ns precision) and
manifests/v5_symlinks.tsv (path, target, resolved) for symbolic links, which are listed there only.
Set (Alex 16 Oct 20:46 UTC: "Also hash the big arrays you leave out of git into the v5 manifest"):
  1. everything under data/ (meshes, Laplace / UVC fields, fibres, sites, network, k files, torso, electrodes, ECG
     weights, cohort inputs)
  2. runs/ that v5 reads: v5 lead fields (2026-10-13_LF_<H>_v5), cb lead fields (2026-10-10_LF_<H>_cb, read by the
     v5 weights check), AP template runs (2026-10-02_biv_fullqrs, 2026-10-03_<H>_fullqrs), v3 His-beat runs read by
     the v3 / v5 gate tables, and the k-fit runs (2026-10-07_nofast_<H>_<3 sites>)
  3. every file of the 12-14 Oct analysis folders that is not in git (arrays, meshes, fibres, caches, weights, logs)
Usage (repo root, venv): python -B analysis/v51_2026-10-15/01_backup/make_manifest.py
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OUT = os.path.join(REPO, 'manifests')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
RUN_DIRS = ([f'runs/2026-10-13_LF_{h}_v5' for h in HEARTS] + [f'runs/2026-10-10_LF_{h}_cb' for h in HEARTS]
            + ['runs/2026-10-02_biv_fullqrs', 'runs/2026-10-03_6G8DD8S5_fullqrs', 'runs/2026-10-03_7D98EVAR_fullqrs']
            + ['runs/2026-10-08_purk_sinus5_Y5HYEDL4', 'runs/2026-10-08_purk_sinus5_Y5HYEDL4_ecg_cb']
            + [f'runs/2026-10-09_purk_sinus_{h}{s}' for h in HEARTS[1:] for s in ('', '_ecg', '_ecg_cb')]
            + [f'runs/2026-10-07_nofast_{h}_{s}' for h in HEARTS
               for s in ('lv_free_wall_phi180_z0.5_d10', 'lv_free_wall_phi180_z0.5_d90', 'rvot_septal_z_d50')])
ANALYSIS_DIRS = ['aim1_gates_2026-10-12', 'audit_2026-10-13', 'audit_addendum_2026-10-14', 'daniels_onset_2026-10-13',
                 'fibre_fix_2026-10-13', 'free_checks_2026-10-13', 'junction_tests_2026-10-12', 'monodomain_check_2026-10-12',
                 'noise_onset_2026-10-12', 'rvot_anatomy_2026-10-12', 'rvot_diag_2026-10-12', 'rvot_tests_2026-10-12',
                 'v5_adopted_2026-10-13', 'v5_grid_2026-10-13']


def mtime_iso(ns):
    s = dt.datetime.fromtimestamp(ns // 1_000_000_000, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    return f'{s}.{ns % 1_000_000_000:09d}Z'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def walk(rel):
    files, links = [], []
    for root, dirs, names in os.walk(os.path.join(REPO, rel)):
        for d in dirs:
            if os.path.islink(os.path.join(root, d)):
                links.append(os.path.relpath(os.path.join(root, d), REPO))
        for n in names:
            p = os.path.join(root, n)
            (links if os.path.islink(p) else files).append(os.path.relpath(p, REPO))
    return files, links


def main():
    files, links = [], []
    for rel in ['data'] + RUN_DIRS:
        if not os.path.isdir(os.path.join(REPO, rel)):
            sys.exit(f'missing folder {rel}')
        f, l = walk(rel); files += f; links += l
    untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '-z', '--']
                               + [f'analysis/{d}' for d in ANALYSIS_DIRS], cwd=REPO, capture_output=True, check=True).stdout
    for p in [x for x in untracked.decode().split('\0') if x]:
        (links if os.path.islink(os.path.join(REPO, p)) else files).append(p)
    files, links = sorted(set(files)), sorted(set(links))
    total = sum(os.path.getsize(os.path.join(REPO, p)) for p in files)
    print(f'{len(files)} files, {total / 1e9:.2f} GB; {len(links)} symbolic links', flush=True)
    t0 = time.time()
    with cf.ProcessPoolExecutor(3) as ex:
        digests = list(ex.map(sha256, [os.path.join(REPO, p) for p in files], chunksize=16))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'v5_data_sha256.tsv'), 'w') as fh:
        fh.write('path\tbytes\tmtime\tsha256\n')
        for p, d in zip(files, digests):
            st = os.stat(os.path.join(REPO, p))
            fh.write(f'{p}\t{st.st_size}\t{mtime_iso(st.st_mtime_ns)}\t{d}\n')
    with open(os.path.join(OUT, 'v5_symlinks.tsv'), 'w') as fh:
        fh.write('path\ttarget\tresolved\n')
        for p in links:
            a = os.path.join(REPO, p)
            fh.write(f'{p}\t{os.readlink(a)}\t{os.path.realpath(a)}\n')
    print(f'hashed in {time.time() - t0:.0f} s -> manifests/v5_data_sha256.tsv, manifests/v5_symlinks.tsv', flush=True)


if __name__ == '__main__':
    main()
