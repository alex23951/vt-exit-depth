# v5.1 brief as received on the PC (verbatim copy of the coordinator relay, 16 Oct 2026 20:33 UTC)

Saved by Claude on the PC so later sessions have the exact rules. Source: the restart relay approved by Alex (card "Restart the PC session with the v5.1 brief?", 16 Oct 2026 20:30:49 UTC).

---
Brief from the cloud session of this thread ("Deep audit"). Alex chose to restart the PC session with it: "Restart" on the card "Restart the PC session with the v5.1 brief?" at 20:30:49 UTC on 16 Oct 2026. The message above ("repo is private pc is connected") is Alex's; the brief below the line is the whole task. Work through it in order, starting with Step 0 now (read-only, no OK needed), and post each STOP report in this thread.

Before this session, an earlier PC session announced its own correction plan at about 20:27 UTC on 16 Oct 2026 and called the result "v6" (Purkinje docstring edits, an analysis-helper NaN fix, a network-length fix, cache and k-file guards, moving ecg_depth_criteria.zip out of the repo root, local commits, possibly a short openCARP run, v6 folders). Alex did not approve that plan, and it was stopped at 20:30:54 UTC. In Step 0, also list every commit after 47808c6, every file created or modified since 16 Oct 2026 20:00 UTC (`find . -newermt "2026-10-16 20:00 UTC"`, excluding .git), any v6 folders, and any openCARP or python processes still running. Revert, delete or move nothing: report it at STOP 0 and wait for Alex.

Alex's answers the brief needs, quoted from this thread with their UTC times (section 1.2; repeat them back in your first post so Alex can object):
- `{{Q_WINDOW_MS}}` = 40 ms: Alex tapped "40 ms" on the card "Set the q-wave initial window for the rescore and Aim 2?" at 08:30:47 UTC on 15 Oct 2026.
- `{{FASCICLE_SPEED}}` = 2.0 m/s: Alex tapped "2.0 m/s" on the card "Set the left fascicle speed in the v5.1 conduction system?" at 08:31:01 UTC on 15 Oct 2026.
- `{{DOSTE_SCOPE}}` = `WHOLE_RV`: Alex tapped "Whole RV" on the card "Apply Doste's RV fibre rule to the whole RV or only the RVOT free wall?" at 08:31:14 UTC on 15 Oct 2026.
- CSE recognition as the primary q rule (already written into Step 2): Alex tapped "Make primary" on the card "Make the noise-aware CSE check the primary q-wave rule?" at 08:31:22 UTC on 15 Oct 2026.
- Step 1.4 repository: Alex posted "https://github.com/alex23951/vt-exit-depth.git" at 13:00:14 UTC on 16 Oct 2026, tapped "Make private" on the card "Make the vt-exit-depth repo private before the code push?" at 13:03:46 UTC, then wrote "repo is private pc is connected" at 20:25:52 UTC on 16 Oct 2026. Step 1.4's request for the URL and the private confirmation is therefore already met: do not ask again; push once Step 1 items 1-3 pass (branch and tags, no force).

Notes: the brief was written on 15 Oct; keep its folder and file names (v51_2026-10-15) as written, while LABNOTES entries carry the real date. Alex's local time is UTC+2; give times from the PC clock.

---

# PC brief: model v5.1 rebuild (Alex's decisions of 15 Oct 2026)

For the Claude Code session on Alex's PC (WSL Ubuntu, `/home/alex/vt-exit-depth`), written in the cloud on 15 Oct 2026. You cannot see the cloud files, so everything you need is here. Three values still on decision cards to Alex are in double braces (1.2).

**Summary**
1. On 15 Oct 2026 Alex answered audit cards A-H (05:18-05:19 UTC) and accepted corrections 4-9 (05:23); this brief carries them out in order.
2. Protect v5 (G): commit, tag `v5`, hash manifest of git-ignored data, cache-key and k-file guards, push to a private remote Alex creates.
3. ecg_depth_criteria 0.4.0 with an initial q window and NaN handling; read-only v5 rescore (H). A ~130-beat stimulus-size and retrograde-delay check on v5, reported only (D).
4. Build v5.1 (C with A, B, E): cross-fibre 0.36 m/s (HF 0.26), distal Purkinje 2 m/s straight-line, fixed human bundle speeds, fixed solver, Doste RV fibres, consistent conductivities, full blood fill, each gated; AHA-segment site labels (F).
5. Rerun the pilot grids on v5.1; rescore every Aim 1 gate as a dated correction beside the 13 Oct verdicts, which stay on record; log all in LABNOTES.md. Nothing is tuned to pass.

---

## 1. Rules for the whole job

### 1.1 Standing rules
- No `rm -rf` or other recursive delete; give Alex the command. Use `python -B`; tests: `PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -p no:cacheprovider`; if a cache folder appears anyway, leave it and tell Alex.
- A run expected to take over 10 min: post the estimate, wait for Alex's OK at run time; give Alex's local time (PC clock).
- Nothing is tuned to pass an Aim 1 check: no speed, delay, angle, conductivity, stimulus, threshold or window changes because of a result here.
- Every model or measurement-code change is a dated deviation in LABNOTES.md (append only).
- Protected, never overwritten: `analysis/v5_grid_2026-10-13/`, `analysis/v5_adopted_2026-10-13/`, `analysis/audit_2026-10-13/`, `analysis/audit_addendum_2026-10-14/` and every v5 data file (all manifest entries). New outputs: `analysis/v51_2026-10-15/<step>/`; new model data files carry `v51` in their names, beside v5's.
- Scripts in protected folders are read-only: to rerun or fix one, copy it to the step folder, change only paths (NaN fix: also aggregation), record the original's sha256 and the diff. Before running any existing script, print its output paths; none may point into a protected folder or a v5 data file.
- From STOP 1 on, at every STOP check size and mtime of each file in `manifests/v5_data_sha256.tsv` (full sha256 at STOP 4e and the final STOP) and `git status` the protected folders; report "v5 files unchanged: yes/no".
- The 13 Oct verdicts (3 pass, 5 fail, 1 not evaluable) stay on record; every rescore is a dated correction beside them.
- Memory (7.7 GB, 8 cores): lead-field builds have crashed WSL (v5 peak 6.8 GB): one heart at a time, nothing else heavy, 13 Oct light AMG options and watchdog. Unmeasured heavy jobs: subset first (a slab or 10 % of a heart) under `/usr/bin/time -v`; keep extrapolated peak RSS under 5 GB; work in blocks. `free -m` first; stop if under 1.5 GB is free.
- Disk: C: is nearly full: check `df -h /mnt/c` and state sizes before large writes. Activation maps, ECG arrays, caches, .npy/.npz/.igb/.dat go under `runs/v51_2026-10-15/<step>/` (git-ignored); `analysis/` keeps CSV/MD and the arrays' sha256.
- Git: stage by name (never `git add -A`, `git add .`, `git commit -a`); show `git diff --cached --stat` before committing; ask before staging a binary or a file over 1 MB. Never `git checkout`/`restore`/`stash`/`reset`/`clean` the working tree, force-push, delete remote refs, or pull/merge/rebase.
- Install no packages (ask). Create no repository on GitHub or any host (no `gh repo create`, no web/API calls); the only remote change is `git remote add origin <URL>` in Step 1, with Alex's URL.

### 1.2 Placeholders
| Placeholder | Recommended | Alternative | Only these wait for it |
|---|---|---|---|
| `{{Q_WINDOW_MS}}` | 40 ms | 20 ms | 2.4-2.6, Step 6 scoring |
| `{{FASCICLE_SPEED}}` | 2.0 m/s (Durrer 1970) | 1.5 m/s, as His and bundles | E3, E8, E9, 4.6-4.7, Step 6 |
| `{{DOSTE_SCOPE}}` | `WHOLE_RV`: Doste 2019 as published (changes every RV site and the His beat) | `RVOT_FREE_WALL_ONLY` | 4.2 steps 7-10 and gates; 4.3 S5 and A-C; 4.5 tensors, lead fields; 4.6-4.7; Step 6 |

Your copy keeps the `{{...}}` text. A fork is decided only when Alex posts the value here (e.g. "Q_WINDOW_MS = 40 ms") or a message here quotes Alex's card answer with its UTC time; repeat it back in your next post so Alex can object. Until then do what does not depend on it, post what waits, and wait. Never default to the Recommended column or use a value you inferred or any agent stated without Alex's quoted answer. Record each value with source and time in LABNOTES before first use. The q rule's CSE recognition is not a placeholder: Alex already chose it ("Make primary" on "Make the noise-aware CSE check the primary q-wave rule?", 15 Oct 2026 08:31:22 UTC), and Step 2 carries it.

### 1.3 If a verification gate fails
Stop, post the numbers, wait. Fix a clear implementation bug (sign convention, index, duplicate edge) only if the fix restores the rule exactly as written here; log it. Never adjust a physiological parameter, tolerance, window or threshold to pass a gate. Named fallbacks (3-ring stencil, openCARP for tissue-only fields, torso remesh) are Alex's decision.

### 1.4 STOP points
At each STOP post: what you did; each acceptance check with value and PASS/FAIL; files written (full paths); "v5 files unchanged"; anything unexpected or inferred; the next step, its time and whether it needs Alex's OK. Then wait (except STOP 1).

---

## 2. Reference facts

**Hearts.** Y5HYEDL4 control, male. 6G8DD8S5 heart failure (HF), wide QRS (LBBB-like, proximal left-bundle cut). 7D98EVAR HF, narrow QRS.

**v5 (adopted 13 Oct).** Speeds fibre/sheet/normal 0.60/0.48/0.48 m/s (control), 0.60/0.35/0.336 (HF); one graph-solver factor k (1.066-1.069, fitted on v3; F01). Bundles tuned per heart to Durrer offsets, 1.75-3.36 m/s. Distal Purkinje 2.0 m/s per edge (1.0-1.1 straight-line; path ratio 1.79/1.94/1.80). cb lead fields: fibre σi 0.174, σe 0.625 S/m, cross-fibre tuned for 0.40 m/s; blood 0.7 S/m in 70/56/70 % of cavity volume; torso 0.2. ecg_depth_criteria 0.3.0 (47808c6), defaults.

**Decisions 4-9 (05:23 UTC).** 4, 5 relative-QRS and His-QRS fails kept (Bazan CI printed); 6 Berruezo kept with Strauss/AHA LBBB check and population caveat; 7 synthetic scar in >= 10 study hearts (no PC work now); 8 conductivity sensitivity, cost first; 9 monodomain gate locked (27 sites, 5 ms), bias-band fallback.

**Measurement convention for every primary gate value (fixed 14 Oct, before results).**
- Pace-map comparators (Bazan 2006 RV, relative QRS, Bazan 2007 region Q, Berruezo): `measure_beat(ecg, fs, stim_ms=<site stimulus time>)`, clean ECG, default baseline (40 ms before the stimulus), QRS = `qrs_duration_any_lead_ms`.
- Spontaneous comparators (absolute QRS at summit + cusp, Daniels order, no-network control, Durrer (e) His-beat QRS): detected onset, `baseline_window_ms` = 40 ms ending 5 ms before the true onset, the project's noise code at 0.05-100 Hz with notch off, 10 µV white noise per lead, seeds 0-9, site value = median of 10; QRS = `qrs_duration_any_lead_ms`, MDI = `mdi_daniels`.
- True mode beside (onset_ms = first activation, offset_ms = last). Unscorable sites (onset not before offset) are counted, listed, left out.

---

## Step 0. Orientation and read-only checks

**Goal.** Know code, data, disk and memory state before changing anything (read-only).
1. `git status --short`, `git log --oneline -5` (expect last commit 47808c6, 10 Oct), `git remote -v` (expect none), `git tag`, `git stash list`.
2. `df -h / /mnt/c`, `du -sh data runs analysis`, `free -m`, `nproc`, top memory users. Confirm openCARP reports hash ffce195.
3. Locate every v5 script (sims/biv_model/, fibres_fix.py, v5_grid.py, v5_adopted.py, three_hearts_v5.py, network_three_hearts, gate, audit a01-a11, rescore, Taggart) and data file, and where each writes; name the audit scripts behind F01 (with sites), AHA segments and cavity volumes; what the graph cache stores (tissue only, or network/junction edges too), its key and size.
4. File:line references in Steps 1-4 come from the 14 Oct audit and may have drifted: confirm each (quote 1-3 lines), plus the q code at measure.py ~104-105, ~195, ~265-283.
5. Verify `code/ecg_depth_criteria` is 0.3.0 (sha256 prefixes): `__init__` ed55943a6bec, `__main__` 7f68169e25c7, criteria 2b5318351346, fiducials 71ba77507e2c, leads 1a71b3c4c2c8, measure a228be4ec965. (The repo-root ecg_depth_criteria.zip is 0.1.0.)
6. Answer: is the 1.5 mm stimulus a radius or a diameter? fs of the saved ECGs (assumed 1 kHz)? Were per-site ECGs or activation maps from the 14 Oct recompute saved? Disk size of one heart's v5 lead fields and of one activation map?

**Outputs.** `analysis/v51_2026-10-15/00_orientation/README.md`. **Acceptance.** Report every mismatch with the audit; change nothing. **Time.** About 10 min; no OK needed. **STOP 0.**

---

## Step 1. Decision G: backup, tag, manifest, guards, push

**Goal.** Commit and tag v5, hash its git-ignored inputs, guard audit F20's two latent risks, copy the code off the PC.
1. Review untracked and modified files with sizes; `data/` and `runs/` stay out (git-ignored). Commit the 12-14 Oct work as it is (v5 code, LABNOTES.md, analysis scripts, small CSV/JSON/MD outputs of the 13 and 14 Oct folders), staged by name: "v5 as adopted 13 Oct 2026 (work of 12-14 Oct, previously uncommitted)".
2. `manifests/v5_data_sha256.tsv` (path, bytes, mtime, sha256) of every git-ignored file v5 reads or produced (per heart mesh, Laplace/UVC fields, fibres, sites.json, network.npz, k file, lead fields, tensors, AP template, `data/cohort/` inputs; T13 torso, electrodes; ignored outputs of the 13 and 14 Oct folders). Time one large file; ask if hashing exceeds 10 min. Commit; `git tag -a v5 -m "Model v5 as adopted 13 Oct 2026; data hashes in manifests/v5_data_sha256.tsv"`.
3. Before the guards, run the three His beats and one paced beat per site family in Y5HYEDL4; save activation times and ECGs in `runs/v51_2026-10-15/01_backup/pre/`. Guards, separate commit after the tag: (a) the graph cache key includes the fibre-file sha256 and every other input of the cached object (v5_grid.py 101-123); (b) the solver stops with an error if the k file is missing, instead of silently using k = 1.0 (14_purkinje.py 542-544), and logs the k file's hash. Never delete or move old cache entries.
4. Push: ask Alex to create an empty private repository (no README, licence or .gitignore), send its URL and confirm it is private; never create one. Then `git remote add origin <URL>`; push branch and tags. If authentication is needed, give Alex the commands; never put a token in the thread. If a push is rejected, stop and post the error. Data stays local.
5. LABNOTES dated entry: hashes, tag, manifest sha256, guards, push (decision G, 15 Oct 2026 05:18-05:19 UTC).

**Acceptance.** With guards on, the new key misses every old cache entry. Rerun the item-3 beats: equal to `pre/`; His beats equal the saved ones; each paced beat's total activation, QRS, MDI, pseudo-delta, IDT, RS and q flags equal the 14 Oct saved ECGs/maps (Step 0), else the per-site CSV in `analysis/audit_addendum_2026-10-14/` (13 Oct CSV for true mode); all differences 0.0. Each guard fires in a test call (nonexistent k path; wrong expected fibre hash), never by touching real data files.
**Outputs.** commits, tag `v5`, manifest, `analysis/v51_2026-10-15/01_backup/README.md`.
**Time.** Minutes; hashing timed first. **STOP 1 does not wait:** post the report, ask for the URL, start Step 2 (which ends at STOP 2 and waits). Push as soon as Alex gives the URL, between steps; post one line when done.

---

## Step 2. Decision H: ecg_depth_criteria 0.4.0, then read-only rescore of v5

**Goal.** q calls get Alex's initial window and the CSE recognition rule; NaN is never a loss; saved v5 beats rescored read-only.

**Primary rule (decision H, a window plus NaN handling, with CSE recognition: Alex chose "Make primary" on the card "Make the noise-aware CSE check the primary q-wave rule?" at 08:31:22 UTC on 15 Oct 2026).** Waves stay as in 0.3.0 (runs beyond ±wave_mv, 0.05 mV) for every other measure. For q and initial r, the lead's first recognised deflection decides: the first excursion beyond ±thr_k lasting >= 6 ms from QRS onset, thr_k = min(wave_mv, max(0.02 mV, 5 × the lead's baseline SD)) (CSE limits, Kligfield 2007 p1310). A q is called only if that deflection is negative, starts within `{{Q_WINDOW_MS}}` of the detected QRS onset (`visible_onset`, never the stimulus, in every mode) and reaches −wave_mv before the lead crosses +thr_k. "Initial positive deflection" (no inferior q) = the same with the signs reversed. Otherwise polarity 0 (neither): a later first deflection, or one that turns back before reaching ±wave_mv. Q amplitude (aVL/aVR, V1) = depth of that deflection's extreme if polarity < 0, else 0.
**Named sensitivities (reported, never primary):** the other N; window only (the lead's first 0.05 mV wave, negative and starting within N, with no recognition step); no window (0.3.0); wave_mv 0.10 mV.

**Code** (0.3.0 line numbers; confirm first).
- Version 0.4.0; `Settings(q_window_ms=None, recog_mv=None)` reproduces 0.3.0 bit-exactly. `fiducials.Settings`: `q_window_ms: float | None = None` (TODO naming Q_WINDOW_MS; set only in 2.4); `q_anchor = 'visible'` ('onset' = stimulus or given onset, sensitivity only); `recog_mv: float | None = None` (primary: 0.02, set in 2.4; None gives window only); `recog_ms = 6.0`. `__post_init__` validates all four (ValueError; 0 < recog_mv < wave_mv).
- `measure_beat` after `lead_waves` (~104): t0 = visible_onset if q_anchor == 'visible' else on. Window only (recog_mv None, a sensitivity): keep line 105; if q_window_ms is set, polarity[k] = 0 unless lead_waves[k][0].start − t0 <= idx(q_window_ms). CSE (recog_mv set, the primary): the primary rule above from i0 = min(on, t0) (run >= max(1, idx(recog_ms)) samples; SD from the baseline window, 0 if under 3 samples; multiplier = existing noise_sd, 5.0); polarity[k] = its sign if it starts within N and reaches wave_mv before crossing back past ∓thr_k, else 0; Q = depth of its extreme.
- q_lead_I, inferior_q_all/any, inferior_r_any, q_V1, q_V2 (~265-271) read the new polarity; qs_V2 = polarity['V2'] < 0 and all V2 waves negative. `amplitudes` (~195): q as in 0.3.0 but 0.0 unless polarity[k] < 0. New outputs: `q_anchor_ms`; per lead `initial_start_ms` (first wave start − t0, NaN if none), `initial_sign`.
- README: new q row; "Changes in 0.4.0" (decision H, 15 Oct 2026, with CSE recognition primary by Alex's choice at 08:31:22 UTC; IEC 60601-2-25 leaves the initial isoelectric segment out of wave durations; why N, from section 8; the sensitivities).
- 0.3.0 side by side: `mkdir -p runs/v51_2026-10-15/pkg_030 && git archive 47808c6 code/ecg_depth_criteria | tar -x -C runs/v51_2026-10-15/pkg_030`; check its six hashes (Step 0 item 5); import it by path.

**Tests** (`tests/test_q_window.py`; `tests/synthetic.py` beats: FS 2000 Hz, onset o = 50 ms, other leads deflecting from o so visible_onset = o; until 2.4 pass q_window_ms = 20 and 40 and recog_mv = 0.02 or None explicitly): (a) lead I flat to o+50, then steeply to −0.5 mV: no q at 20 or 40, q with no window; (b) flat to o+15, beyond −0.05 mV within 2 ms: q at 20 and 40; (c) 0.03 mV × 10 ms initial r, deep S from o+12: q under window only (as 0.3.0), none under the primary CSE rule; (d) slow QS from onset: q, Q = QS depth; (e) stimulus 20 ms before o, initial q at o: q; (f) notched q never turning positive: one q, deepest point; (g) q_window_ms=None passes every 0.3.0 test; (h) seed 21 (assumed cloud construction): `synthetic.beat(I=[(o,0),(o+30,0.10),(o+60,-0.6),(o+120,0.3),(o+170,0)])` plus `np.random.default_rng(21).normal(0, 0.020, (8, n))` mV on the 8 independent leads: 0.3.0 gives q_lead_I True, the primary CSE rule must give False, window only reported (expected True); if 0.3.0 is not True, report and rely on (i); (i) false-q rate in an isoelectric lead <= 1 % over 400 `synthetic.noise` draws at 10 µV, CSE primary and window only.

**NaN** (three_hearts_v5.py 29-45, network_three_hearts_2026_10_10.py, gate scripts; copies per 1.1; first confirm their median/AUC code and that NaN comparisons become AUC losses, audit F17):
- `scored(v)`: None → NaN; drop NaN only (keep ±inf); return kept values, n_total, n_unscorable. `scored_median` → (median, n_scored, n_unscorable); "not evaluable" if n_scored = 0, never "nan".
- `auc_scored(pos, neg)`: unpaired Mann-Whitney, higher = epicardial, NaN dropped per group, AUC = mean(1[p>n] + 0.5·1[p==n]) over scored cross-pairs; return n used and dropped sites.
- Paired statistics (up-counts, paired differences, ratio of group means, bootstrap) drop the whole pair; denominator = scored pairs. Criterion rates leave None out of both; print "k / n_scored (m unscorable)".
- Unscorable beat: catch the ValueError; all measures NaN, reason `onset_not_before_offset`. Other NaNs carry their reason (e.g. idt_v2_ms "no R in V2", ratios "0/0").
- Gate tables add n_scored/n_total per heart × family × depth, the unscorable list, "k unscorable, left out", and counts by depth (reported only).
- Test: one injected NaN gives the median of the rest and hand-checked AUC/up-counts; the 6G LV-septum IDT median prints a number plus "(k unscorable)".

**Order and acceptance.**
- 2.1 implement; 2.2 tests pass.
- 2.3 regression on every saved v5 beat (432 + His): with q_window_ms=None, outputs equal the 0.3.0 copy bit-exactly. At q_window_ms = 20 and 40, each with recog_mv = 0.02 and None, all outputs are bit-identical except initial_polarity, q_lead_I, inferior_q_all/any, inferior_r_any, q_V1, q_V2, qs_V2, q_amplitude_mv, q_ratio_avl_avr, rs_ratio_v1 (reads Q in V1), the new initial_* outputs and criteria reading them (e.g. Vallès, Piers, Bazan q items, Santangeli). Assert identity only: compute and post no 0.3.0-vs-0.4.0 q-call comparison on v5 beats, at any window, until the value is recorded.
- 2.4 (needs `{{Q_WINDOW_MS}}`, recorded as in 1.2) set the defaults (q_window_ms = N; recog_mv = 0.02, Alex's CSE choice of 08:31:22 UTC, logged with that time), rerun the tests, commit, tag `ecg_depth_criteria-0.4.0`, per-module sha256 into `manifests/v51_data_sha256.tsv`. N never changes after.
- 2.5 Read-only rescore of v5, 0.3.0 and 0.4.0 side by side, true mode and 14 Oct convention; Bazan 2007 also under each sensitivity. Report each changed q or initial-r call with its cause; initial_start_ms per heart and region; visible_onset − stimulus per site; summit/cusp sites whose q_ratio_avl_avr, rs_ratio_v1 or santangeli2015_no_q_v1 change; polarity-0 leads; false-q and false-initial-r rates at 10 and 20 µV (400 draws; isoelectric lead, 0.10 mV initial-r beat), CSE primary and window only. List scripts with private q logic (e.g. the 13 Oct Bazan sweep); Step 6 calls the package only.
- 2.6 LABNOTES deviation (decision H, with CSE recognition primary per Alex's card answer of 08:31:22 UTC). A verdict differing from 13 Oct is printed as "dated correction (measurement rule, decision H with CSE recognition, 15 Oct 2026)" beside the 13 Oct verdict.

**Outputs.** `analysis/v51_2026-10-15/02_measure_040/` (regression report, per-site CSV, q-change list, gate table, noise table).
**Time.** Time 10 beats, extrapolate, ask if over 10 min. If the 14 Oct ECGs are not saved, recomputing 432 + 144 beats took 19 min with 2 processes: needs OK. **STOP 2.**

---

## Step 3. Decision D: stimulus-size and retrograde-delay check on v5 (reported only)

**Goal.** How much do the 1.5 mm ball stimulus (from 75/90 % depth it reaches the RV epicardium and spans the cusp walls) and the unsourced 2 ms retrograde delay shape depth results? Never used to retune; v5.1 keeps both.
**Design** (inference: the card fixed only "about 130 beats, reported"). Post the exact beat list and wait for Alex's go; the run (under 10 min) needs no separate OK.
- Arm S: single-node stimulus (node nearest the site point) instead of the ball: RV free wall 9 positions × 10 % and 90 % × 3 hearts (54 beats), Y5HYEDL4 cusp sites at every depth (about 8; count from sites.json).
- Arm R: 4 ms muscle-to-Purkinje delay (top of Behradfar 2014's physiological 2-4 ms; v5's 2 ms is the bottom): LV free wall 10 positions × 10 % and 90 % × 3 hearts (60 beats).
- Both are parameters defaulting to v5; one v5 beat with defaults reproduces bit-exactly. If the cache holds anything either affects, put both in the key or use a new empty cache folder under `runs/v51_2026-10-15/03_stimulus_check/`. Every Arm R beat with a retrograde entry must differ from its v5 beat.

**Report** vs the same v5 beats (true mode and 14 Oct convention; 0.3.0, and 0.4.0 once tagged). Arm S: Bazan 2006 RV median per-pair % per heart beside its LV difference; RV 90-10 paired differences (QRS, pseudo-delta, MDI, IDT, shortest RS); cusp QRS, MDI, aortic-sinus median in the Daniels order. Arm R: relative QRS ratio of means, paired up-counts and AUCs (pseudo-delta, MDI, IDT, RS), first network entry at 10 % sites. No verdict changes.
**Outputs.** `analysis/v51_2026-10-15/03_stimulus_check/`. **Time.** 576 v5 beats took 19 min with 2 processes, so about 4-5 min plus scoring (estimate); ask if over 10 min. **STOP 3.**

---

## Step 4. Decision C: build v5.1 (with A, B, E)

Card estimate: about 1-1.5 h of PC time plus the openCARP reference runs. Outputs: `analysis/v51_2026-10-15/04_build/` and `v51` data files beside v5's.

### 4.0 Predictions, timestamped before any v5.1 beat (inference; never tuned to)
`04_build/predictions.md`: PRED-1 His to first muscle about 23-25 ms (Y5HYEDL4), 22-24 (7D98EVAR), 40-50 (6G8DD8S5, RV first), still 10-30 ms short of human HV 35-55. PRED-2 Durrer (a): spread above 5 ms likely, fewer than 2 areas within 5 ms (fail) possible, in at least one heart. PRED-3 RV epicardial breakthrough about 30-36 ms after LV onset (window 20-31); first RV endocardium 20-26 ms after LV onset (Durrer 5-10). PRED-4 LV endocardium by 37.5 ms: direction unpredictable; His-beat and paced QRS widen somewhat. All assume fascicles at 2.0 m/s; E9 (4.4) supersedes them.

### 4.1 Speeds (decision A)
fibre/sheet/sheet-normal (m/s): Y5HYEDL4 0.60/0.36/0.48; 6G8DD8S5 and 7D98EVAR 0.60/0.26/0.336 (0.36 × 0.73 = 0.2628, rounded to 0.26 by decision A: use 0.26 everywhere; sheet-normal unchanged, 0.48 × 0.70). One file (e.g. `params/v51_speeds.json`) read by solver and conductor.

### 4.2 Doste RV fibres (`{{DOSTE_SCOPE}}` needed from step 7)
First: measure v5's stored fibres in the frame (l, t_out, c) below (expect about +64-66°/−42 to −46° in the RV body, 81/−16 at the RVOT free wall); confirm 02_laplace.py's TV/PV boundary sets and that v5's LV outflow treatment stays unchanged.
1. R_field = nodes with the RV-myocardium label fibres_fix.py / 04_fibres.py use for the septal split (name the array, record its sha256); steps 2-6 run on it under both options. R_new = nodes rewritten in steps 7-10: R_field if `WHOLE_RV`; if `RVOT_FREE_WALL_ONLY`, the RVOT free wall only (propose the set, from an existing label or the 13 Oct per-tract outflow field, at STOP 4a before writing fibres; the septal RVOT keeps its v5 fix). Nodes outside R_new keep v5's fibre, sheet and normal vectors exactly.
2. Φ_D on the whole biventricular myocardium: Laplace, −2 on LV endocardium, +1 on RV endocardium, 0 on every outer surface (including the outer infundibulum and the 13 Oct septal-infundibulum aortic-root interface), zero flux on valve rings/caps.
3. Apex set A = the RV endocardial node with the lowest UVC apico-basal coordinate plus RV endocardial nodes within 2 mm; report its distance to the LV apex and the tricuspid-ring centroid.
4. On R_field (zero flux at the LV interface): Ψ_TV = 0 on A, 1 on the tricuspid ring; Ψ_PV = 0 on A, 1 on the pulmonary ring; w = 1 on A and the tricuspid ring, 0 on the pulmonary ring. Clip w to [0, 1] (report count); gradients by v5's method.
5. g = w·∇Ψ_TV + (1−w)·∇Ψ_PV (unnormalised, Doste Eq. 1); l = g/|g|, apex to valves. Where |g| or |∇Φ_D| < 1 % of its median over R_field, use the normalised mean of passing neighbours within 2 mm; report counts.
6. t = normalise(∇Φ_D − (l·∇Φ_D)l) (into the cavity); t_out = −t; c = l × t_out; d = clip(1 − Φ_D, 0, 1), d = 1 at RV-label nodes past the septal border.
7. h = h_endo(1−d) + h_epi(w)·d, h_endo = +90° at every w (never −90), h_epi(w) = −25°·w. Expected at d = 0/0.5/1: w = 1 +90/+32.5/−25; w = 0.3 +90/+41.25/−7.5; w = 0 +90/+45/0.
8. On R_new: f = normalise(cos h·c + sin h·l); no Bayer bislerp. Docstring: h here is the standard helix angle (LV subendocardium positive), so Doste's printed RV/outflow values apply unchanged; do not copy Piersanti 2021 / lifex-fiber conventions (they mirror the RV).
9. β = 0 (Doste's RV epi +20° has no fixable sign) and no Eq. 5 septal blend (no α_septal published): both deviations; the angle may jump at the septal border.
10. n = normalise(t_out − (t_out·f)f); s = n × f (or v5's sign convention). Write new v5.1 fibre files; their sha256 goes in the cache key and manifest.

Gates: **A1** on R_new: h = atan2(f·l, f·c); Δh = ((h − h_exp(w, d) + 90) mod 180) − 90 (±90° are the same fibre); |Δh| <= 0.5° and |asin(f·t_out)| <= 0.5° at every node (report max, p99). **A3** (`WHOLE_RV`), before any beat: RV epicardial nodes (d >= 0.95, w >= 0.7) within 10 mm of the anterior and inferior LV-RV epicardial junctions have h < 0 (as the adjacent LV epicardium in its own outward frame) and RV-body mid-wall h > 0; else fix the sign convention only. Under `RVOT_FREE_WALL_ONLY`, instead report epicardial h on R_new (about −7.5° at w = 0.3) beside v5 across its border, and A3 and A2(a) on the unchanged v5 vectors, ungated. **A4** R_new nodes with d <= 0.02: acos(|f·l|) <= 0.5°. **A5** nodes outside R_new: 0 changed, max change 0.000°. **A8** R_field and R_new each one connected component; (f, s, n) orthonormal; guard counts.
Reports, v5 vs v5.1: **A2** h_v5, h_v5.1, h_exp in d bins [0, 0.05], [0.45, 0.55], [0.95, 1]: (a) RV body (w >= 0.9, UVC z 0.4-0.6, >= 5 mm from Dirichlet sets); infundibulum (b) septal 9.6-15.1 mm and (c) free wall 14.2-16.6 mm below the PV plane; (d) 2-4 mm below it; w at every RVOT site. **A7** fibre angle across the septal interface, epicardial junctions and R_new border. **A9** in Step 6.
**STOP 4a** (time: Laplace solves and gates, measure per heart).

### 4.3 Graph solver fix (F01)
First: rerun a copy of the F01 script (paths only changed) on the v5 solver; reproduce 0.564/0.489/0.485 and 0.50/0.365/0.35. Build the 2-ring stencil for one heart in row blocks (subset first): report edges per node, build time, peak RSS, E2 pairs rejected, single-beat time. Confirm openCARP ffce195's eikonal takes separate fibre/sheet/normal speeds.
- S1. Remove the single k (v5_grid.py 62-66, 119-138; 14_purkinje.py 542-544); use a 2-ring tissue stencil and per-heart factors f_f, f_s, f_n on tissue edges only.
- S2. E1 = unique sorted tet-edge pairs. E2 = pairs (i, j), i ≠ j, with (A@A)_ij > 0 and A_ij = 0 (boolean sparsity patterns, no numeric subtraction: graph distance exactly 2), kept only if |x_i − x_j| <= 3.5 mm (twice the 1.75 mm max edge) and the midpoint lies in a myocardial tet (test at least when i, j and a middle node k are all surface nodes). Tissue graph = E1 ∪ E2.
- S3. t_ij = sqrt(dᵀ M̄ d), d = x_j − x_i, M = Σ_a (f_a·v_a)⁻² a aᵀ over fibre, sheet, normal of the v5.1 fibre file; nodal M = volume-weighted mean of element M; M̄ = mean of nodal M at i, j and, for E2, the middle node k (A_ik = A_kj = 1) giving the smallest t_ij.
- S5. Fit per heart with the F01 script copy (site list and paths only changed) on tissue-only point-stimulus beats at its LV free-wall mid-wall sites: f = 1, then f_a ← f_a·target_a/measured_a until all three are within ±0.5 %. Save f with speeds, stencil version and fibre sha256 in a versioned JSON; the solver stops if it is missing or a hash differs. Cache key = every input of the cached object (fibre hash, speeds, f, stencil version; if network/junction edges are cached, also network hash, class and fascicle speeds, v_edge, junction delays).
- **Acceptance A** (after S5; each heart's speeds and f): slab 36 × 36 × 20 mm of unstructured tets with the hearts' edge lengths (mean about 1.05, max 1.75 mm): jittered-grid points via scipy.spatial.Delaunay or an installed tool (name it; none usable: ask). Uniform fibres: principal speeds within ±1.5 %; ray speeds |x|/t in 15° bins per principal plane within ±3 % of the exact |x|/T, T = sqrt(xᵀ diag(v⁻²) x). Fibres rotating +60° to −60° across a 10 mm wall, endocardial face fired: transmural arrival within ±2 % of z/v_n.
- **Acceptance B**, held-out regions (septum, RV free wall, septal and free-wall RVOT, apex): each direction within ±3 % in every heart.
- **Acceptance C**, openCARP eikonal (dream.solve = 0, FIM; v5.1 speeds without factors; same fibre file and single-node stimulus; no network; cap 20 min per site) at 12 sites per heart (LV free wall 10 % and 90 %, 2 septum, RV free wall 10 % and 90 %, septal and free-wall RVOT, 2 cusps, 2 summit): no −1 in act (raise dream.fim.max_iter); per site median |Δt| <= 1 ms, p95 |Δt| <= 2 % of total activation, total activation within ±2 %. Report the openCARP fields' F01 speeds beside the graph's.
- S11. If B or C fails, add no region-specific factors; report. S12. Network coupling unchanged (one Dijkstra pass). S13 (report): refit at v5 speeds and rerun the F01 copy.
- Time: v3 openCARP took 43-85 s per site: 36 runs ≈ 26-51 min, up to 12 h if all hit the cap; needs OK. Grid about 5× v5 per beat (inference; one-heart timing supersedes). **STOP 4b.**

### 4.4 Conduction system: bundles (E), then distal Purkinje (B)
- E1. Disable the per-heart Durrer-offset calibration (14_purkinje.py 331-346); grep 14_purkinje.py, v5_grid.py and callers to show no speed is set from a timing target or per heart.
- E2. One class per edge. HIS: root to the LB/RB split. RB: split along the RB main stem to the moderator-band insertion. LB_TRUNK: split along the LB to the last node shared by >= 2 fascicle-end paths (all shared division edges). FASCICLE: edges on exactly one fascicle-end path, division node to Durrer end node. DISTAL: all else (RB side branches, beyond the moderator band).
- E3. HIS, RB, LB_TRUNK 1.5 m/s (Kupersmith 1973: mean 1.5, range 1.3-1.7; section 8); FASCICLE `{{FASCICLE_SPEED}}`; DISTAL = v_edge (P5). Same constants in all hearts.
- E4. Resample each non-distal segment polyline at 0.5 mm; at each point take the arc length s whose chord is 10 mm; R10 = median(s/10 mm); R10 <= 1.10: nominal speed, else nominal × R10, flagged. Segments under 10 mm: arc/chord.
- E5-E7. Junction delays unchanged, 4 ms antegrade, 2 ms retrograde (14_purkinje.py 34-35, 561). 6G8DD8S5 cut unchanged (cut-edge diff vs v5 empty). No scaling by sex, heart or HF; no tissue factor on network edges.
- E8 guard: every edge speed = class value (× R10 if flagged) within 1e-9, else abort; rerun after P5 sets v_edge and after any network edit (Table B: final run, all five classes). Write `params_network_<heart>_v51.json`: per segment class, edges, arc and chord (mm), R10, speed, transit (ms); root position (proximal His near the central fibrous body, or distal).
- F19: count exact duplicate node pairs apart from shared division edges; show removing duplicates changes no Dijkstra time while removing shared edges does (e.g. 6G septal 18.9 → 19.8 ms). Keep duplicates in the v5.1 network (no decision covers removing them); de-duplicate only inside P6. If removing them changes a time, stop and report.
- E9 (timestamped before any beat, once `{{FASCICLE_SPEED}}` is recorded): analytic His → each fascicle end and moderator band; predicted Durrer areas within 5 ms of the earliest, and spread; His → first muscle (earliest arrival + 4 ms); also at 1.27 and 1.8 m/s for HIS/RB/LB_TRUNK as a range (analytic only).
- P2. Distal roots: every node where a distal edge leaves a bundle or fascicle node (fascicle termini, RB end, budding points); not the His.
- P3. Distal-only run: distal edges at v0 = 2.0 m/s, roots fired at t = 0, no bundles, delays or tissue; multi-source Dijkstra (scipy, `min_only=True`, `return_predecessors=True`) gives t_j and serving root r(j).
- P4-P5. D_j = |x_j − x_r(j)|, A_j = D_j/t_j over junctions with D_j >= 10 mm, LV and RV pooled; v_edge = v0 × 2.0 / median(A_j), rounded to 0.01 m/s, on every distal edge of that heart. Expected near 3.6-3.9 m/s. Never reuse 1.79/1.94/1.80.
- P6 gate: path lengths on the de-duplicated distal graph give the same v_edge within 1 %. P7 gate: rerun at v_edge; median A_j = 2.00 ± 0.02 m/s per heart; report IQR, LV-only, RV-only, all-junction median, mean, ratio of sums. If v_edge > 4.0 m/s (Camps 2024 upper bound), report; do not cap. P8 (report): LV septal junction pairs 15-25 mm apart in one subtree, median D/|Δt|.
- Recompute v_edge after any network edit; it and the network hash go in the manifest; the solver stops on mismatch. Time: minutes. **STOP 4c.**

### 4.5 Lead fields and source term (F11-F13)
First: report how 15_conductor.py 95-130 tags blood and why only 70/56/70 %; print current σi/σe triplets; confirm ECG weights use σi and follow the fibre file.
- C1-C2. Fibre σi 0.174, σe 0.625 S/m (Clerc 1976, derived). Cross-fibre direction d: σi,d = 0.174·(v_d/0.60)², σe,d = 0.625·(v_d/0.60)² (equal anisotropy), from target speeds, never by rescaling cb values.
- C3 (check values, S/m; code uses C2 at full precision, never these): σi/σe sheet 0.0626/0.2250, normal 0.1114/0.4000 (Y5HYEDL4); sheet 0.0327/0.1174, normal 0.0546/0.1960 (HF).
- C5. One tensor set, oriented by the v5.1 fibre file, in the lead-field solve (myocardium σi+σe, blood 0.7, torso 0.2) and the ECG source term (σi); assert on the computed values σm,d/σm,fibre = (v_d/0.60)² to 1e-6, σm = σiσe/(σi+σe).
- C6 gate: watertight LV and RV cavity surfaces (endocardium plus flat caps on the four valve rings; each edge in 2 triangles, consistently oriented) enclose within ±1 % of LV 172.0/157.8/172.8 mL and RV 197.9/107.2/122.5 mL.
- C7. Tag as blood every non-myocardial torso element with centroid inside a cavity surface (winding number > 0.5, or majority of 3 ray-parity tests), testing only elements in each cavity's bounding box, in chunks. Fallback if C8 fails or cavity elements are coarser than about 2 mm: meshtool remesh with cavity surfaces as internal boundaries, only with Alex's OK and an estimate.
- C8 gate per ventricle: blood within ±2 % of cavity volume; 0.2 S/m elements inside < 1 % of it; no blood outside; >= 95 % of endocardial faces border blood; blood stops at the valve planes.
- C9. Lead fields one heart at a time as in 1.1; v5 took 7.5-10 min per heart: ask before each heart. Gate: ECG weights match openCARP within 0.0002 mV on one beat per heart (time it from its 13 Oct log; ask if over 10 min). Then run the 36 openCARP and matching graph tissue-only maps of 4.3 through the v5.1 lead fields and AP template; report ECG measures side by side (not gated: on 14 Oct tiny lead-field changes moved IDT and RS by up to 95 and 61 ms).
- Decision 8, cost only (no run): time, memory, disk for one more lead-field build of one heart with the sensitivity set (cross-fibre σe 0.236, σi solved so σm scales with v²: control sheet σi 0.0618, normal 0.1381; HF 0.0287, 0.0521 S/m). **STOP 4d.**

### 4.6 His beats
Run the three v5.1 His beats; report beside the PRED/E9 lines, changing nothing: His to first muscle and to detected QRS onset vs HV (proximal root: Serban 2025 HVprox 51 ± 10 ms, Kupersmith proximal H-Q 35-54 ms; distal root: HVdis 46 ± 10 ms, dH-Q 18-35 ms); Durrer (a) areas within 5 ms and spread, (b) at 30 and 37.5 ms, (c), first RV endocardium after LV onset (Durrer 5-10, report only), latest activation. Durrer (a) is now an uncalibrated test (location caveat: fascicle ends still sit on Durrer's areas). C10 (report): His-beat R/S in V1-V6, Sokolow-Lyon, frontal QRS magnitude and axis. **STOP 4e** with Table B so far; wait.

### 4.7 Tag
After Alex's go: commit (staged by name), tag `v5.1`, add all v5.1 data hashes to `manifests/v51_data_sha256.tsv`, push (no force); short LABNOTES entry; post one line.

---

## Step 5. Decision F: AHA-segment labels and placement rule

**Goal.** Study-heart sites placed by AHA segment; pilot hearts labelled read-only beside the old labels; the Bazan 2007 fail stays on record.
1. Per heart, find the anterior and inferior RV insertion points at basal, mid and apical levels; assign AHA segments (Cerqueira) anchored at them, with a copy of the 14 Oct audit's AHA script (name it).
2. Read-only (no site moves, no beats): `analysis/v51_2026-10-15/05_aha_labels/pilot_site_labels.csv`: heart, site, old name, old Bazan region, AHA segment, body-defined Bazan region (superior/inferior, basal/apical from body axes), tissue label. Flag 6G8DD8S5 rv_free_wall_q75_z0.25 and 7D98EVAR rv_free_wall_q25_z0.25 (LV-tagged muscle). Old labels stay of record for 13 Oct.
3. Study-heart placement function: sites at AHA segment centres at the pilot depth levels, named by segment, Bazan regions from body axes; geometry-only dry run on the pilot hearts beside old positions. Segments and sites per segment: a proposal for Alex, fixed before any study heart runs.
4. Reading of F (inference; confirm at STOP 5): Step 6 scores Bazan 2007 with the old labels (comparable with 13 Oct) and prints the AHA/body-label version beside it with its position count (not evaluable below 20 pooled positions; 14 Oct body regions: 4/14 vs 1/14).

**Acceptance.** Every pilot LV site gets exactly one AHA segment; sites.json and old labels unchanged (diff empty). **Time.** Minutes. **STOP 5.**

---

## Step 6. Pilot grids on v5.1 and Aim 1 rescore

**Goal.** v5.1 beats at the same 144 sites per heart (432 network beats), 144 no-network control-heart beats and 3 His beats, scored with 0.4.0 at `{{Q_WINDOW_MS}}`; every gate rescored as a dated correction.
1. Same sites.json, families and pairs as 13 Oct; v5.1 solver, network, fibres, lead fields (the no-network arm too; on 13 Oct it used v3's). Save activation maps and per-site ECGs in `runs/v51_2026-10-15/06_pilot_rerun/` (disk check first: one map × 579). Pick the process count from the measured RSS of one v5.1 beat process (v5: 2 processes, 816 MB in total); state it with the time estimate.
2. Score with the section 2 convention under 0.4.0; true mode beside; q gates also under each named sensitivity (Step 2).
3. Fill Table A. A verdict that differs from 13 Oct is a dated correction ("v5.1 rebuild, decisions A-H, 15 Oct 2026"); one that differs between primary and any sensitivity is flagged convention-dependent.
4. Reports, never used to retune: A9: Doste's 10-ms isochrone length/width ratio and area on the RV endocardium around the earliest RV endocardial node (RVOT septal and free-wall sites, tissue-only and with network; long axis along the septal projection of the RVOT axis) vs Doste 1.86 ± 0.22 and clinical 1.9 ± 1.2 (Acosta 2015), expected lower (inference); HF hearts need a few extra tissue-only RVOT beats. Taggart-style speeds on tissue-only beats (copy of the 14 Oct script). 6G8DD8S5 His beat on Strauss and AHA LBBB items. His QRS vs cohort male controls 90.3 ± 8 ms, Mason 2007 69-109, Rijnbeek 2014 men 20-29 y 80-126 ms. Relative QRS 2,000-resample bootstrap CI (seed 0) over the 10 pairs, beside Bazan's (basal inferior about 1.01-1.14, apical superior 1.08-1.24). Berruezo with its caveat (baseline QRS 194 ± 19 ms; no stimulus latency in the model).

**Acceptance.** His beats equal 4.6; no unactivated nodes in any beat; every unscorable value listed. **Outputs.** `analysis/v51_2026-10-15/06_pilot_rerun/` (CSV/MD, array sha256).
**Time.** About 1.5 h for 576 beats (inference: v5's 19 min × about 5; use the measured one-heart timing): needs OK. Time scoring on 10 beats first. **STOP 6.**

---

## Step 7. LABNOTES deviation entry and final report

**LABNOTES** (append, dated): "v5.1 (15 Oct 2026; Alex's decisions A-H of 05:18-05:19 UTC and 4-9 of 05:23 UTC)"; the three fork values and the CSE choice with source and time; each change with value, source, reason, gate results (speeds, solver, v_edge, bundle classes, fascicles `{{FASCICLE_SPEED}}`, Doste fibres `{{DOSTE_SCOPE}}` with β = 0 and no Eq. 5 blend, tensors, blood fill, 0.4.0 with N = `{{Q_WINDOW_MS}}` and CSE recognition primary); unchanged: 1.5 mm stimulus, 4/2 ms delays, 6G cut, z 0.9 cap, Tomek template (140 ms, no T wave), F19 duplicate edges; Step 3 reported only; "13 Oct verdicts stay on record; v5.1 rescore is a dated correction"; from section 8 only the bullets for Alex's chosen values.

**Report** `analysis/v51_2026-10-15/07_report/REPORT.md`, also posted in the thread, tables in full: 1 Summary (5 lines); 2 Fork values, source, time; 3 Steps, commits, tags; 4-6 Tables B, A, C; 7 Step 2 and 3 findings; 8 Deviations and inferences; 9 Files and hashes; 10 Still open (monodomain check not run: not evaluable; study-heart placement awaiting Alex; Proposal Model-tab entry, done in the cloud later).

**Table A: Aim 1 gates (fixed layout).** Prefilled from the 13 Oct record and 14 Oct rescore; check each value against the PC files, report mismatches. Where a gate script's threshold differs from this table, the 13 Oct script governs; report it.

| # | Gate (hearts) | Rule | 13 Oct v5 (true mode, 0.3.0) | 14 Oct v5 (surface ECG, 0.3.0) | v5, 0.4.0 | v5.1 primary | v5.1 verdict | Changed? | Convention-dependent? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Absolute paced QRS, summit + cusp (control) | median 132-193 ms | 159.0 PASS | 137.0 PASS | | | | | 14 Oct: yes | |
| 2a | Relative QRS Y5HYEDL4 | 1.0785-1.1587 (mean QRS 90/10 %, 10 LV free-wall pairs) | 1.0712 FAIL | 1.0586 FAIL (CI 1.000-1.124) | | | | | | Bazan CIs |
| 2b | Relative QRS 6G8DD8S5 | same | 1.1371 PASS | 1.1840 FAIL (CI 1.167-1.199) | | | | | 14 Oct: yes | |
| 2c | Relative QRS 7D98EVAR | same | 1.0930 PASS | 1.1147 PASS (CI 1.062-1.160) | | | | | | |
| 3 | Daniels order (control) | summit 90, vein 90 and aortic sinus > RVOT > LV endo 10 (values in this order) | .542, .458, .587, .679, .348 FAIL | .621, .497, .616, .689, .360 FAIL | | | | | | |
| 4 | Bazan 2006 RV (all) | median pair % in −1.9 to +6.6 and below the heart's LV | 4.2/8.0, 4.1/14.7, 4.0/10.3 PASS | 3.9/6.1, 3.5/18.7, 4.3/12.9 PASS | | | | | | Step 3 arm S |
| 5 | Bazan 2007 region Q (pooled) | 90-10 % Q-rate difference inside Bazan's regional CI; >= 20 positions | basal superior q in I 4/21 vs 3/21 FAIL | 4/21 vs 3/21 FAIL | | | | | | AHA labels; sensitivities |
| 6 | Berruezo (6G8DD8S5) | QRS/PdW/IDT/RS direction and size (RS 20-52 %) | 14.7/60.6/31.6/7.6 % FAIL | 18.7/60.6/31.6/7.6 % FAIL | | | | | | LBBB items |
| 7 | Durrer (control, His beat) | T 62-100 ms; (a) >= 2 of Durrer's three areas activated within the first 5 ms of LV endocardial activation (approved 12 Oct; spread reported); (b) >= 90 % LV endo outside posterobasal by 37.5 ms; (c) RV epi breakthrough 20-31 ms; (d) reported; (e) His QRS 63-88 ms | T 100.8; (a) 0/2.7/5.0 (calibrated); (b) 66.8 % at 37.5 ms (48.7 % at 30 ms); (c) 15.1; (e) 94 FAIL | (e) 94.5 FAIL | | | | | | (a) now uncalibrated; 14 Oct audit (b): 67.0 % / 48.5-48.8 % |
| 8 | No-network control | summit + cusp median > 193 ms, wider in every family | 240.0 PASS | 220.25 PASS (7/7) | | | | | | |
| 9 | Monodomain agreement | locked: 27 sites, 5 ms, >= 90 % of 108 pairs | not evaluable | not evaluable | not run | not run | not evaluable | | | bias-band fallback |
| | Tally | | 3 / 5 / 1 | 3 / 5 / 1 | | | | | | |

**Table B: verification gates** (gate | criterion | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR | PASS/FAIL): Step 1 guards; Step 2 regression; Doste A1, A3, A4, A5, A8; solver A, B, C (sites passing of 12); E6; E8; F19; P6; P7; C5; C6; C8; C9.

**Table C: predictions vs results** (quantity | heart | PRED / E9 | v5 | v5.1 | comparator): the 4.6 quantities, His-beat QRS, v_edge, A9 ratio, Taggart along/across.

**Time.** Writing only, no runs. **Final STOP**: post the report and wait.

---

## 8. What is inference
- q window: N = `{{Q_WINDOW_MS}}` is inferred (no standard or VT-criteria paper gives a maximum initial isoelectric length). If 40 ms: Vereckei's "initial 40 ms" (a VT-vs-SVT definition); inside epicardial initial slow phases of 33-56 ms; over 6 × the 6.5 ms CSE onset tolerance. If 20 ms: closer to Vallès/Piers's "short isoelectric segment"; about 3 × that tolerance; may miss slow initial q's in HF hearts.
- CSE recognition (primary, Alex's choice): 20 µV and 6 ms are CSE's wave-recognition limits for measurement programs (Kligfield 2007), applied here to each lead's first deflection; the 5 × baseline SD floor and the "reach ±wave_mv before turning back" step are this study's.
- Bundles: no human speed for the LB trunk or the RB beyond ~11 mm (extrapolated from 1.5 m/s). If `{{FASCICLE_SPEED}}` = 2.0: one pair of spikes in one heart (Durrer 1970). If 1.5: fascicles take the His/bundle value, no fascicle-level source. His root position unknown; PRED-1 to PRED-4.
- Doste: linear-in-w angles, d = 1 − Φ_D, apex rule, zero-flux rings, sign calibration, 0.5° and 1 %/2 mm limits, β and blend omitted; the `RVOT_FREE_WALL_ONLY` border.
- Also: solver tolerances (±3 %, 1 ms, 2 %), 5× cost, openCARP finishing at outflow sites; equal anisotropy; blood ending at the valve planes; the 10 mm minimum D_j (3.6-3.9 m/s edges have no human source); the Step 3 design and Step 5 reading of F.
  
