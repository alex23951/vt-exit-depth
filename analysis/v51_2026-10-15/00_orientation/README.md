# Step 0: orientation and read-only checks (v5.1 brief)

PC clock 2026-10-16 22:34-22:50 CEST (UTC 20:34-20:50). Read-only: this README is the only file written.
Git HEAD 47808c6 (uncommitted changes, see 1).

## 0. Leftovers of the earlier PC session (stopped 20:30:54 UTC)

- Commits after 47808c6: **none**. Tags: none. Stash: empty. Remote: none. Branch: master only.
- Files created or modified since 2026-10-16 20:00 UTC (`find . -path ./.git -prune -o -newer <20:00 UTC ref>`): **only `LABNOTES.md`** (mtime 22:30:17 CEST).
  The earlier session appended 23 lines (now lines 1034-1056) at 20:30:05 UTC, in one `cat >> LABNOTES.md` call:
  1. `### 2026-10-13/14 deep audit, PC half` (entry written afterwards)
  2. `### 2026-10-14_audit_addendum_regen` (entry written afterwards)
  3. `## 2026-10-16 22:30 PC time (UTC 20:30): CORRECTIONS after the deep audit ...` (announces the unapproved "v6" plan and folders)
  4. `#### Note 2026-10-16 22:30 PC time: dated correction of a measurement mismatch` (6G8DD8S5 relative QRS PASS -> FAIL under the pace-map convention, 1.1840; absolute summit + cusp QRS convention-dependent)
  Its only other action after that was a read-only `sed -n` of 14_purkinje.py. Nothing reverted, deleted or moved.
- v6 folders: none (`analysis/v6_*`, `data/biv/*/purkinje_v6`: absent). `analysis/v51_2026-10-15/` and `runs/v51_2026-10-15/` did not exist before this README.
- Running jobs: no openCARP, mpiexec or study python process. The stopped session's Claude process is still alive and idle
  (PID 589, started 19:42 CEST, no child processes); left as is.
- Also present: a saved handoff from 10 Oct (`.claude/handoff/active.md`, superseded by this brief; not acted on).

## 1. Git and machine

| Check | Value | As expected? |
|---|---|---|
| `git log -1` | 47808c6 "Network v3, cb conductor, three-heart grids and analyses (4-10 Oct 2026)" | yes |
| `git status --short` | `M LABNOTES.md`; untracked: 14 analysis folders (aim1_gates_2026-10-12 ... v5_grid_2026-10-13), `chain2.log`, `ecg_depth_criteria.zip`, `ecg_depth_criteria.zip:Zone.Identifier` | yes |
| `git remote -v`, `git tag`, `git stash list` | empty, empty, empty | yes |
| Disk | `/` 1007 G, 921 G free (the repo, data/ and runs/ live here); `/mnt/c` 476 G, 54 G free (89 % used) | C: nearly full, but nothing in this job writes to C: |
| Sizes | data 18 G, runs 4.5 G, analysis 3.1 G, code 452 K, sims 704 K | |
| Memory | 7,881 MB total, 7,035 MB available, swap 2,048 MB unused; 8 CPUs | |
| Top memory users | two Claude processes (269 MB, 234 MB), `claude remote-control` (160 MB) | |
| openCARP | `GIT tag: latest`, `GIT hash: ffce19513ca9...` | yes (ffce195) |
| Python | venv_carputils: numpy 2.5.3, scipy 1.18.1, pandas 3.0.6. **pytest is not installed** (venv or system); 0.1.0-0.3.0 tests were never run on the PC (LABNOTES l.377, 503, 530) | mismatch: Step 2 needs pytest |
| Git credentials | no credential helper, no `~/.ssh`, no `gh` | push will need authentication (Step 1.4) |

Untracked analysis folders that are not covered by `.gitignore` (which ignores only `runs/`, `*.igb`, `__pycache__/`, `data/`, `.claude/handoff/`):
audit_addendum_2026-10-14 821 M (580 files > 1 MB: the 14 Oct maps), v5_adopted_2026-10-13 1.6 G (torso copy, ECG weights),
v5_grid_2026-10-13 552 M (cache 215 M, fibres_E 318 M), fibre_fix_2026-10-13 136 M; the other ten folders are 36 K-2.7 M with no file over 1 MB.
Step 1 must stage by name and leave these arrays out.

## 2. ecg_depth_criteria

`code/ecg_depth_criteria` is 0.3.0 (`__init__.py:8 __version__ = "0.3.0"`); sha256 prefixes all match the brief:
`__init__` ed55943a6bec, `__main__` 7f68169e25c7, criteria 2b5318351346, fiducials 71ba77507e2c, leads 1a71b3c4c2c8, measure a228be4ec965.
Unchanged since 47808c6 (`git status` clean for code/). Repo-root `ecg_depth_criteria.zip` contains `__version__ = "0.1.0"` (as the audit, F31).
Tests: tests/test_measure.py, test_criteria.py, test_summit_prisco.py, synthetic.py (import pytest).

## 3. v5 scripts, data and where each writes

| Script | Reads | Writes |
|---|---|---|
| sims/biv_model/14_purkinje.py | data/biv/H/{bivF.*, uvc, surfaces, sites.json, purkinje/} | data/biv/H/purkinje/{network.npz, network_intact.npz (6G), summary.json, graph_scale.json, myo_graph.npz}, runs/ |
| sims/biv_model/15_conductor.py | data/biv/H/{calibration.json, torso/}, runs/<template>/vm.igb | data/biv/H/torso/full_nofast_blood.*, runs/2026-10-10_LF_H_cb, data/biv/H/ecgW_nofast_cb.npz |
| analysis/fibre_fix_2026-10-13/{laplace_fix.py, fibres_fix.py, run_fix.py} | data/biv/H laplace, uvc, mesh | own folder (laplace/, bivF.lon, summaries); redirected by v5_grid `fibres` into fibres_E/H |
| analysis/v5_grid_2026-10-13/v5_grid.py | data/biv/H, fibres_E/H/bivF.lon, ecgW_nofast_cb.npz, noise_onset_2026-10-12 | fibres_E/H/, cache/myo_H_<fib>_<s>_<n>.npz, <arm>/H/{beats.csv, beats_nonet.csv, his_T.npy, his_ecg.npy, config.json, d_ant_per_junction.npy}, gates.csv/txt |
| analysis/v5_adopted_2026-10-13/v5_adopted.py | v5_grid (Heart('E')), fibres_E, torso | mesh/H (links), torso/H/full_nofast_blood.lon (1.6 G total), runs/2026-10-13_LF_H_v5, ecgW_v5_H.npz, weights_check_H.json, leadfield_H.json, purk_H_v5.csv, grid/H/his_{T,ecg}.npy, gates_v3_v5.csv/txt |
| analysis/v5_adopted_2026-10-13/three_hearts_v5.py | purk_H_v5.csv | three_hearts/{results.md, sites.csv} |
| analysis/v5_adopted_2026-10-13/followup.py | purk_H_v5.csv, grid/H | gates_followup.md |
| analysis/network_three_hearts_2026_10_10.py | grids_2026-10-07 *_cb.csv | analysis/network_three_hearts_2026-10-10/ |
| analysis/aim1_gates_2026-10-12/aim1_gates.py | v3 grids | its folder (bazan06/07, berruezo, durrer, nonet, report.txt) |
| analysis/audit_2026-10-13/a01-a11 | read-only on data and CSVs | own folder (json/csv) |
| analysis/audit_addendum_2026-10-14/regen.py | v5_grid Heart('E'), ecgW_v5_H.npz | maps/H/<site>.{T,ecg}.npy, repro.csv |
| .../rescore.py, gates_rescore.py | maps/ | rescore/{per_site.csv, gates.json, gates.txt, settings.json, a1_repro.json} |
| .../taggart.py | maps/ | taggart/{beats_*.csv, electrodes.csv, speeds.json} |

Audit scripts behind the brief's numbers:
- **F01** (realised speeds): `analysis/audit_2026-10-13/a03_speeds_activation.py`. v5 graph/k, no network, site `lv_free_wall_phi180_z0.5_d50` in each heart:
  Y5HYEDL4 0.564 / 0.489 / 0.485, 6G8DD8S5 0.501 / 0.364 / 0.350, 7D98EVAR 0.503 / 0.366 / 0.351 m/s (fibre / sheet / normal; a03_speeds_activation.json).
  The v3 openCARP-vs-graph comparison uses `lv_free_wall_phi180_z0.5_d10`, `_d90`, `rvot_septal_z_d50` (the k-fit sites). Paced network sanity: a03b_paced_exits.py.
- **AHA segments**: `a11_aha_thickness.py` (Cerqueira 2002, anchored to the RV insertion points). Site labels / body regions: a05_site_labels.py, a06_sites_bazan.py.
- **Cavity volumes**: `a04_anatomy.py` (`cavity()`): LV 172.0 / 157.8 / 172.8 mL, RV 197.9 / 107.2 / 122.5 mL (Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR; printed with a negative sign, orientation). The HF RV surfaces have 15 and 11 non-manifold edges (relevant to C6).

Graph cache (`analysis/v5_grid_2026-10-13/cache/`): **tissue only** (unique tet edges `e` int32, unscaled travel time `w` float32; no network or junction edges; k is applied after loading).
Key = file name `myo_<heart>_<'E' or 'v3'>_<sheet>_<normal>.npz` (v5_grid.py:120): no fibre speed, no fibre-file hash, no k. Eight entries, 26.2-29.5 MB each, 215 MB in all.
A second, older cache is `data/biv/H/purkinje/myo_graph.npz` (14_purkinje.myo_graph(); v3 speeds, frozen fibres; fixed name, no key).
k files: data/biv/H/purkinje/graph_scale.json: k = 1.0685 / 1.0658 / 1.0682 (fitted 8-9 Oct on v3).

v5 data files (manifest in Step 1): per heart data/biv/H/{biv.pts, biv.elem, bivF.elem, bivF.lon (v3), uvc/, laplace/, surfaces/, sites.json, calibration.json, purkinje/{network.npz, network_intact.npz, graph_scale.json}, torso/{full_nofast_blood.*, electrodes}};
analysis/v5_grid_2026-10-13/fibres_E/H/ (v5 fibres); analysis/v5_adopted_2026-10-13/{torso/H, mesh/H, ecgW_v5_H.npz}; runs/2026-10-13_LF_H_v5; AP template runs/2026-10-02_biv_fullqrs/vm.igb (Y5HYEDL4), runs/2026-10-03_H_fullqrs/vm.igb (HF); data/torso (T13, electrodes); data/cohort.

## 4. File:line references in Steps 1-4 (all confirmed unless marked)

| Reference | Quote | Status |
|---|---|---|
| v5_grid.py 62-66 (speeds) | `def speeds(arm, h):` / `s, n = 0.48, 0.48` / `s, n = s * 0.73, n * 0.70` | confirmed |
| v5_grid.py 101-104 (load, k) | `self.net = dict(np.load(hd(h, 'purkinje', 'network.npz')))` / `self.k = self.PK.graph_scale()` | confirmed (103-104) |
| v5_grid.py 119-123 (cache key) | `tag = f"{'E' if 'fibres_E' in lonf else 'v3'}_{sp[1]:.4f}_{sp[2]:.4f}"` / `if os.path.exists(f): ... d['w'].astype(float) / self.k` | confirmed (120-123) |
| v5_grid.py 119-138 (graph metric) | `t = np.sqrt((... dv, fb) / sp[0]) ** 2 + (... dv, sh) / sp[1]) ** 2 + (... dv, nm) / sp[2]) ** 2)` (131); `return e.astype(np.int64), w / self.k` (138) | confirmed |
| v5_grid.py 152 (junction delays) | `data += [gn.data[kk], np.full(len(m), 2.0), self.d_ant]` | confirmed |
| v5_grid.py 157-159 (stimulus ball) | `s = np.where(np.linalg.norm(pu - pu[site_node], axis=1) < 1500)[0]` | confirmed |
| 14_purkinje.py 34-35 | `Muscle -> Purkinje delay 2 ms (ASSUMPTION, not sourced: ...` | confirmed |
| 14_purkinje.py 89 | `P = {'v_mm_per_ms': 2.0, 'd_ant_ms': 4.0, 'd_ret_ms': 2.0, ...` | confirmed |
| 14_purkinje.py 331-346 (Durrer-offset calibration) | `# proximal speeds anchored to Durrer 1970 ...` (331); `speed[f'division_{k}'] = L / (t_D + P['durrer_offset_ms'][k] - L_lbb / v0)` (342); `speed[k] = L_rv / (t_D + P['rv_after_lv_ms'])` (346) | confirmed |
| 14_purkinje.py 542-544 (k file) | `def graph_scale():` / `f = os.path.join(PK, 'graph_scale.json')` / `return json.load(open(f))['k'] if os.path.exists(f) else 1.0` | confirmed |
| 14_purkinje.py 561 | `data = [w, w, gn.data[keep], np.full(len(m), P['d_ret_ms']), np.full(len(m), P['d_ant_ms'])]` | confirmed |
| 14_purkinje.py 425-427 (net_graph duplicates) | `key, inv = np.unique(e, axis=0, return_inverse=True)  # duplicates would be summed ... keep the fastest copy` | confirmed (relevant to F19) |
| 15_conductor.py 95-130 (blood) | `enc &= np.maximum.accumulate(wall, axis=ax) & ...` (111); `inside = Delaunay(Ph[np.unique(np.concatenate([lv, rv]))]).find_simplex(g) >= 0` (114) | confirmed |
| three_hearts_v5.py 29-45 (NaN) | `return float(x)` (31: 'nan' becomes NaN, not None); `xs = [x for x in xs if x is not None]` (37); `(p > q) + 0.5 * (p == q)` (45) | confirmed: NaN is kept by med() and counts as a loss in auc() |
| network_three_hearts_2026_10_10.py | same f/med/auc at lines 27-43 (two lines earlier) | confirmed |
| measure.py ~104-105 | `lead_waves = {k: waves(x[i], on, end, cfg.wave_mv) ...}` / `polarity = {k: (w[0].sign if w else 0) ...}` | confirmed (104-105) |
| measure.py ~195 | `q = float(-min(groups[0][1])) if groups and groups[0][0] < 0 else 0.0` | confirmed (195) |
| measure.py ~265-283 | `"q_lead_I": polarity["I"] < 0,` (265) ... `"q_V1": polarity["V1"] < 0,` (271); `"rs_ratio_v1": ... (0.0 if q_mv["V1"] > 0 else NAN)` (283) | confirmed |
| fiducials.py Settings | `noise_sd: float = 5.0` (22), `wave_mv: float = 0.05` (24) | confirmed |
| 02_laplace.py TV/PV sets | `BASE = ['mv_rim', 'tv_rim', 'av_rim', 'pv_rim', ...]` (37); `'ot': (['APEX'], ['av_rim', 'pv_rim', 'ao_iface', 'part_iface'])` (41) | confirmed |

Mismatches and things to settle before the step that needs them (reported, nothing changed):
1. **v5 junction delay depends on an override.** `v5_grid.Heart('E', h)` builds arm C/E's random antegrade delays N(4.85, 1.55) (v5_grid.py:110-115). v5 as adopted sets them back to 4.0 ms after construction (v5_adopted.py:127, regen.py:17). Any Step 1.3 / Step 3 rerun must do the same, or it is not v5.
2. **Heart from the environment.** k (`graph_scale()`), `PK.load()` and the AP template (`15_conductor.template_run()`) take the heart from the environment variable `HEART`, the rest from the argument `h` (F20); the guards should also check that they agree.
3. **ECG weights use sigma_m, not sigma_i.** v5_adopted.py:107 calls `fe.weights(..., fe.conductivities(cal), 'm', -1.0, True)`; 13_fast_ecg.py:50 `return gi if sigma == 'i' else gi * ge / (gi + ge)`. The brief's 4.5 says "confirm ECG weights use sigma_i" and C5 says "ECG source term (sigma_i)", while C5's assertion uses sigma_m. To settle before Step 4.5.
4. **No discrete "RV-myocardium label" in the septal split.** fibres_fix.py / 04_fibres.py split on the continuous `d = phi_rv / (phi_lv + phi_rv)` per element (RV side d > 0.5). The mesh's element tags give a candidate RV myocardium (tag 2: 61.0 / 37.6 / 46.0 mL; tags 1, 25, 28, 29 the rest). R_field (4.2 item 1) needs one of the two; proposal at STOP 4a.
5. Current cb conductivities (S/m, sigma_i / sigma_e): Y5HYEDL4 fibre 0.174 / 0.625, sheet 0.0592 / 0.2124, normal 0.0725 / 0.2606 (s = 4.084); 6G8DD8S5 sheet 0.0722 / 0.2592, normal 0.0760 / 0.2731 (s = 3.865); 7D98EVAR sheet 0.0614 / 0.2206, normal 0.0712 / 0.2558 (s = 4.196). (Step 4.5 "first" item, given here for reference.)
6. openCARP eikonal takes separate fibre / sheet / normal speeds: 12_eikonal.py:99 `'-gregion[0].dream.vel_l', V['f'], '-gregion[0].dream.vel_t', V['s'], '-gregion[0].dream.vel_n', V['n']` (mm/s units).

## 5. Answers to item 6

- **Stimulus size: radius 1.5 mm.** Every node within 1.5 mm of the site node is fired at t = 0 (v5_grid.py:157-158, `< 1500` um; same in 14_purkinje.py:579 and calib 613): a ball 3 mm across.
- **fs of the saved ECGs: 1 kHz.** v5_grid.py:165 `t = np.arange(0, tend + 0.5, 1.0)` (ms); scoring calls `measure_beat(..., 1000.0)` after padding 60 ms of the first value in front (pad = 60, baseline window 15-55 ms of the padded trace).
- **14 Oct maps and ECGs: saved.** `analysis/audit_addendum_2026-10-14/maps/<H>/<site>.T.npy` (float32 activation per node, ms) and `<site>.ecg.npy` (float32 (n, 12), 1 ms, t = 0 at the stimulus or His), 145 per heart (144 sites + his_driven) and 144 in `maps/Y5HYEDL4_nonet/`: 579 beats, 818 MB, with repro.csv (bit-exact vs 13 Oct).
- **Disk sizes.** One heart's v5 lead fields: run folder runs/2026-10-13_LF_H_v5 42-47 MB (12 x 1.5 MB LF_*.igb = 18 MB); ECG weights ecgW_v5_H.npz 16-18 MB; the v5 torso copy analysis/v5_adopted_2026-10-13/torso/ 1.6 GB for three hearts. One activation map 1.35-1.50 MB (337,505-375,672 nodes); one ECG 7-10 kB. 579 maps ~ 0.85 GB.
