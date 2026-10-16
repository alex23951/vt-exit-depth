# Step 2: decision H, ecg_depth_criteria 0.4.0 and the read-only rescore of v5

PC clock 2026-10-16 23:06-23:30 CEST (UTC 21:06-21:30). Read-only on every v5 file: no beat was recomputed; the 14 Oct
saved maps / ECGs were reused (analysis/audit_addendum_2026-10-14/maps).

## 2.1-2.2 Package 0.4.0 (tag `ecg_depth_criteria-0.4.0`, commit 766b647)

- `fiducials.Settings`: `q_window_ms = 40.0` (Q_WINDOW_MS, Alex 15 Oct 08:30:47 UTC), `q_anchor = "visible"`, `recog_mv = 0.02`
  (CSE recognition primary, Alex "Make primary" 15 Oct 08:31:22 UTC), `recog_ms = 6.0`; validated in `__post_init__`.
  New helpers `first_deflection()` and `follow()`.
- `measure_beat`: the rule of the brief (section "Primary rule"). Window only when `recog_mv=None`; 0.3.0 when both are None.
  q / initial r flags, `qs_V2` and the Q amplitudes read the new polarity; new outputs `q_anchor_ms`, `initial_start_ms`,
  `initial_sign`. README: new q rows and "Changes in 0.4.0".
- Tests (pytest 9.1.1): 76 / 76 pass (63 of 0.3.0, of which `test_version` now expects 0.4.0, + 13 in tests/test_q_window.py:
  validation, (a)-(i)). Test (g) reruns every 0.3.0 test with the window off (`tests/conftest.py`, EDC_LEGACY_Q=1): 63 / 63.
  The 0.3.0 copy's own 63 tests also pass (first run on the PC). Per-module sha256: manifests/v51_data_sha256.tsv.
- Test (h) (seed 21): in the package's default detected mode 0.3.0 does **not** call a q (first wave positive), unlike the
  cloud's assumption. With the project's true-onset convention (onset o, baseline 40 ms ending 5 ms before it) 0.3.0 and
  window only call the noise spike a q, and the CSE rule does not. The test checks both modes; (i) holds as well (0 / 400).

## 2.3 Regression (regression_report.md, regression.json): PASS

All 579 saved v5 beats, 7,527 measurements per rule. With the window and recognition off, 0.4.0 is bit-identical to the
0.3.0 copy in every output. At 20 / 40 ms, with and without recognition, only the q outputs and the criteria reading them differ.

## 2.5 Rescore (rescore_040.py -> runs/.../per_measurement.csv, sha256 b56f5891...a356, 22,002 rows; report_040.py)

**Gate 5, Bazan 2007 region Q (13 Oct rule, `followup.py`):** basal superior q in I, 21 pooled positions:
- 0.3.0, true mode: 4/21 vs 3/21, +5 pp (−19 to +28). Bazan +74: FAIL. This reproduces the 13 Oct value.
- 0.4.0 primary: identical, FAIL, in true mode, under the 14 Oct pace-map convention, and with 10 µV noise (5/21 vs 3/21).
- Every named sensitivity (N 20, window only, no window, wave_mv 0.10): FAIL.
- The verdict is unchanged by decision H and is not convention-dependent.

Descriptive rows:
- Basal superior, no inferior Q: +29 pp (−1 to +52) under 0.3.0, +57 pp (+28 to +75) under 0.4.0 primary. The direction matches Bazan; there is no Bazan % to compare.
- The other three regions have 7-9 positions: not evaluable.

**Other Aim 1 gates:** their inputs are bit-identical (2.3), so their 14 Oct values stand under 0.4.0 (checked against
analysis/audit_addendum_2026-10-14/rescore/gates.txt).

**Changed calls 0.3.0 → 0.4.0 (clean ECG; the same counts in true, stimulus and detected mode):**

| Call | Changed | Direction |
|---|---|---|
| q in lead I | 73 | all lost |
| inferior q all | 37 | all lost |
| inferior q any | 64 | all lost |
| inferior initial r | 87 | all lost |
| q V1 | 32 | all lost |
| q V2 | 35 | all lost |
| QS V2 | 7 | all lost |

No new q appeared anywhere. Lead-level causes (q_changes.csv; the window is checked first):
- 1,125: the first 0.05 mV wave starts more than 40 ms after the visible onset
- 546: an earlier deflection of the opposite sign (315 +, 231 −) is recognised first
- 6: the recognised deflection turns back before reaching 0.05 mV

**Polarity 0 (neither):** under 0.4.0 primary, 90-215 of 579 beats per lead; lead I 174. Window only: 54-282. N 20: 155-364.
0.3.0: 0, except 3 in aVR.

**initial_start_ms** (primary, stimulus mode, ms after the visible onset; gates_040.json):
- LV regions, lead I: median 9.5-19.5 ms.
- RV and RVOT: 17.5-38.5 ms.
- A start over 40 ms is uncommon. Most counts are 0-4 sites per region; the largest is 4 of 8 in the 6G8DD8S5 RV basal superior region.

**Visible onset − stimulus** (per site in per_site.csv):
- 2-4 ms at 10 %, 75 % and 90 % depth.
- 5-14 ms (range 3-18) at 50 % depth: mid-wall exits start silently on the surface ECG.
- His beats 21-28 ms.

**Summit / cusp:**
- The aVL/aVR Q ratio changes at 96 of 192 site-modes. Many go 0/0 (missing) because the aVR or aVL Q falls outside the window or isn't recognised.
- As a result, Yamada aVL/aVR > 1.1 and Jauregui < 1.45 change at 81, and Santangeli 2-of-3 at 57.
- R/S V1 and Santangeli's "no q in V1" don't change.

**Noise table (noise_table.csv; synthetic lead I, 400 draws, detected mode):**

| Beat | Noise | 0.3.0 | Window only 40 | CSE primary 40 |
|---|---|---|---|---|
| Isoelectric lead: false q / false initial r | 10 µV | 0 % / 0 % | 0 % / 0 % | 0 % / 0 % |
| same | 20 µV | 42.0 % / 41.0 % | 18.3 % / 19.0 % | 2.0 % / 1.5 % |
| 0.10 mV initial r: false q | 10 µV | 0 % | 0 % | 0.25 % |
| same | 20 µV | 2.25 % | 2.25 % | **14.25 %** |

At 20 µV the noise floor (5 × SD) lifts the recognition threshold to the 0.05 mV cap. The 0.10 mV × 10 ms initial r then
stays above it for under 6 ms in some draws, so it isn't recognised, and the following S counts as the first deflection,
which is read as a q. This is the rule exactly as written in the brief (the first excursion of at least 6 ms decides). It is
reported, not changed: decision for Alex (see STOP 2).

**NaN handling (nanstats.py, test_nanstats.py 5/5):**
- Copies three_hearts_v5_nanfix.py and network_three_hearts_nanfix.py (diffs beside them; originals' sha256 in the headers).
- Medians drop NaN only (±inf kept). Unpaired AUCs use scored cross pairs only. Paired statistics drop the whole pair. Rates print "k / n scored (m unscorable)".
- 6G8DD8S5 LV-septum IDT median: was "nan", now 47.0 ms (true onset) / 43.0 ms (detected), each "(3 unscorable)".
- 6G8DD8S5 IDT AUC 90 vs 10 %, true onset: 0.53 → 0.57 (2 unscorable). The F17 loss bias is removed.
- Consoles: *_console.txt.
- Unscorable beats (onset not before offset): 0 of 22,002 measurements; none left out.
- Missing values carry their reason (`reason` column: Q ratio 0/0, no wave in V1).
- n_scored by heart × family × depth: n_scored_by_depth.csv.

**Scripts with private q logic** (Step 6 calls the package only):
- analysis/rvot_tests_2026-10-12/q_lead_I.py (first 0.05 mV wave in 40 ms after the stimulus)
- analysis/aim1_gates_2026-10-12/aim1_gates.py (`first_wave_sign`, 0.05 / 0.10 mV)
- analysis/free_checks_2026-10-13/free_checks.py (`q_call`, the 13 Oct Bazan q sweep)
- analysis/audit_addendum_2026-10-14/part3/p3.py: derives q in I / aVL / V5 / V6 from the package's `initial_polarity` (package-based)

## Files

regression.py / .json / _report.md, rescore_040.py / .json, report_040.py, q_report.md, q_changes.csv, per_site.csv
(true and stimulus mode, 0.3.0 and primary), gates_040.json, noise_rates.py, noise_table.csv, n_scored_by_depth.csv,
nanstats.py, test_nanstats.py, three_hearts_v5_nanfix.py (+ .diff, _console.txt, three_hearts_v5/), network_three_hearts_nanfix.py
(+ .diff, _console.txt, network_three_hearts_2026-10-10/). Full rescore table: runs/v51_2026-10-15/02_measure_040/per_measurement.csv
(10.3 MB, git-ignored). 0.3.0 copy: runs/v51_2026-10-15/pkg_030.
