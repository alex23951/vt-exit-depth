"""STOP check (v5.1 brief 1.1): are the v5 files unchanged?

Compares every file of manifests/v5_data_sha256.tsv with its recorded size and mtime (and, with --full, its sha256),
every link of manifests/v5_symlinks.tsv with its recorded target, and runs `git status` on the protected folders.
Prints "v5 files unchanged: yes" or "no" with the differences. Read only.
Usage (repo root, venv): python -B analysis/v51_2026-10-15/01_backup/check_v5_files.py [--full]
"""
import concurrent.futures as cf
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
from make_manifest import mtime_iso, sha256  # noqa: E402

PROTECTED = ['analysis/v5_grid_2026-10-13', 'analysis/v5_adopted_2026-10-13', 'analysis/audit_2026-10-13',
             'analysis/audit_addendum_2026-10-14']


def main(full):
    t0 = time.time()
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(REPO, 'manifests', 'v5_data_sha256.tsv'))][1:]
    bad = []
    for p, size, mt, _ in rows:
        a = os.path.join(REPO, p)
        if not os.path.exists(a):
            bad.append(f'missing {p}'); continue
        st = os.stat(a)
        if str(st.st_size) != size or mtime_iso(st.st_mtime_ns) != mt:
            bad.append(f'size/mtime {p}: {st.st_size} {mtime_iso(st.st_mtime_ns)} (manifest {size} {mt})')
    if full:
        with cf.ProcessPoolExecutor(3) as ex:
            dig = list(ex.map(sha256, [os.path.join(REPO, r[0]) for r in rows], chunksize=16))
        bad += [f'sha256 {r[0]}' for r, d in zip(rows, dig) if d != r[3]]
    for p, target, _ in [l.rstrip('\n').split('\t') for l in open(os.path.join(REPO, 'manifests', 'v5_symlinks.tsv'))][1:]:
        a = os.path.join(REPO, p)
        if not os.path.islink(a) or os.readlink(a) != target:
            bad.append(f'link {p}')
    gs = subprocess.run(['git', 'status', '--porcelain', '--'] + PROTECTED, cwd=REPO, capture_output=True, text=True, check=True).stdout
    tracked_changes = [l for l in gs.splitlines() if not l.startswith('??')]
    bad += [f'git: {l}' for l in tracked_changes]
    untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '-z', '--'] + PROTECTED, cwd=REPO,
                               capture_output=True, check=True).stdout.decode().split('\0')
    listed = {r[0] for r in rows} | {l.split('\t')[0] for l in open(os.path.join(REPO, 'manifests', 'v5_symlinks.tsv'))}
    extra = [p for p in untracked if p and p not in listed]
    bad += [f'new untracked in a protected folder: {p}' for p in extra]
    print(f'{len(rows)} files ({"size, mtime, sha256" if full else "size, mtime"}), protected-folder git status checked, {time.time() - t0:.0f} s')
    print('v5 files unchanged:', 'yes' if not bad else 'no')
    for b in bad[:50]:
        print('  ', b)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main('--full' in sys.argv))
