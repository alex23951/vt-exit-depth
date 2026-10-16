# Step 1: decision G (backup, tag, manifest, guards, push)

PC clock 2026-10-16 22:48-23:05 CEST (UTC 20:48-21:05). Alex: "Go for Step 1 ... Also hash the big arrays you leave out
of git into the v5 manifest" (16 Oct 20:46 UTC).

## Commits and tag

| Commit | Content |
|---|---|
| ad63ed7 | "v5 as adopted 13 Oct 2026 (work of 12-14 Oct, previously uncommitted)": 305 files staged by name: LABNOTES.md and the scripts and CSV / JSON / MD / TXT / LOG files of <= 1 MB of the 14 untracked 12-14 Oct analysis folders |
| b3bce5c | manifests/v5_data_sha256.tsv, manifests/v5_symlinks.tsv, make_manifest.py, check_v5_files.py, Step 0 README. **Tag `v5`** (annotated) |
| (next) | guards: sims/biv_model/14_purkinje.py, this folder's v5_grid_guarded.py (+ .diff), test_guards.py, beats.py, compare.json, this README |

Left out of git (all hashed in the manifest): arrays (.npy / .npz), meshes, fibre files (.lon), Laplace fields (.dat, .vtx, .par),
caches, ECG weights, analysis/rvot_diag_2026-10-12/median_v1v6_rvot_vs_lvendo10.png (374 kB), analysis/audit_addendum_2026-10-14/rescore/per_site.csv (2.3 MB),
and 12 openCARP.log files (their build line contains the openCARP repository access token; no tracked file and no past commit contains it).
Also left untracked: chain2.log (13 Oct launch error), ecg_depth_criteria.zip (0.1.0) and its Zone.Identifier.

## Manifest

`manifests/v5_data_sha256.tsv` (path, bytes, mtime UTC with ns, sha256), sha256 `342388bae79537218a43a47d8bb3f43ae44c53827169f30aaac0b13a3a09e0f6`:
3,484 files, 22.73 GB, hashed in 40 s (3 processes; one 607 MB file alone: 2.0 s, 305 MB/s). Set: all of data/; the runs v5 reads
(v5 and cb lead fields, AP template runs, v3 His-beat runs, the k-fit runs); every 12-14 Oct analysis file not in git.
`manifests/v5_symlinks.tsv` (sha256 `cd5d0ec2a70561d8ab1d2868884aabda849229d2c86183f6bbf71349a6167d75`): 39 links (path, target, resolved).
Check at every STOP: `python -B analysis/v51_2026-10-15/01_backup/check_v5_files.py [--full]` -> "v5 files unchanged: yes/no".

## Guards (audit F20)

The original analysis/v5_grid_2026-10-13/v5_grid.py is in a protected folder (read-only), so guard (a) lives in the copy
`v5_grid_guarded.py` (original sha256 c290bd3b613dbcf157b67c1512ef2891e479ef50122e938c43b9760c1d2a9c96; `v5_grid_guarded.diff`).
Changes in the copy:
- paths: reads the protected folder (fibres_E, arm outputs); writes only under runs/v51_2026-10-15/ (01_backup/, cache/).
- (a) cache key = sha256 of every input of the cached myocardial graph: heart, biv.elem / bivF.pts / fibre-file sha256, the three speeds, edge-rule version.
  Cache file `runs/v51_2026-10-15/cache/myo_<H>_<key[:16]>.npz` (+ .json with the inputs); key stored in the file and checked on load.
  `Heart(arm, h, expect_fibre_sha256=...)` stops if the fibre file differs. Added check: HEART in the environment must equal the heart argument
  (k, the mesh and the AP template are read from it; F20).
- Same result: a freshly built graph is rounded to float32 before use, as in every v5 beat that loaded the cache (13 Oct adopted grid,
  14 Oct regen). Without it a first build gives float64 travel times (F20: 6e-8 relative) and the beat would not be bit-identical.
- (b) sims/biv_model/14_purkinje.py `graph_scale(path=None)`: stops (FileNotFoundError) if the k file is missing instead of returning k = 1.0;
  logs the file's sha256 once per process (stderr). k file sha256: Y5HYEDL4 714f7543...fa82, 6G8DD8S5 207d1b7b...5958, 7D98EVAR c49dcb74...d377.
  (14_purkinje.py before: sha256 2a9b5d6aa32c919d4b24995fbab2521e0554f96969fb794f702a00022e478ee6.)

## Acceptance

| Check | Result |
|---|---|
| Guard tests (`test_guards.py`, pytest 9.1.1): k file missing -> stops; k present -> logs sha256; wrong expected fibre sha256 -> stops; HEART mismatch -> stops; new key misses all 8 old cache entries and changes with each speed and the fibre file (3 hearts) | 7 / 7 PASS |
| New key misses every old cache entry | PASS (new names myo_Y5HYEDL4_7acd5e2759e981c5, myo_6G8DD8S5_ae33debdc9759b1a, myo_7D98EVAR_3ba2e1b8a6dc5b0a; old names carry no hash) |
| Beats (3 His + 7 Y5HYEDL4 paced, first site of each family): post-guard (fresh cache build) vs pre-guard, activation maps and ECGs | 20 / 20 arrays bit-identical |
| Second guarded run (cache hit), Y5HYEDL4 | 16 / 16 arrays and scores bit-identical |
| Pre-guard beats vs the 14 Oct saved maps / ECGs (analysis/audit_addendum_2026-10-14/maps) | 20 / 20 bit-identical |
| His beats vs the 13 Oct arrays (analysis/v5_adopted_2026-10-13/grid/<H>/his_*.npy) | 6 / 6 bit-identical |
| Scores vs 13 Oct purk_<H>_v5.csv (216 / 154 / 154 columns incl. total activation, QRS, MDI, pseudo-delta, IDT, RS, q flags, both onsets) | all equal, differences 0.0 |
| Scores post vs pre (all columns) | all equal |

Run times: pre 41 s for 10 beats (peak RSS 0.69 GB); post with cache build 170 s (peak 1.26 GB per heart, build 30-43 s).
Arrays: runs/v51_2026-10-15/01_backup/{pre,post,post_cached}/<H>/; comparison: compare.json.
A `__pycache__` folder appeared in this folder from a `py_compile` syntax check (it ignores -B); left in place (git-ignored).
