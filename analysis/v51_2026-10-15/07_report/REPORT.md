# Model v5.1: final report (v5.1 brief Step 7)

Written PC clock 2026-10-18 22:42 CEST. Brief: analysis/v51_2026-10-15/BRIEF_v51.md (Alex's decisions A-H of 15 Oct 2026 05:18-05:19 UTC and
4-9 of 05:23 UTC). Built on the PC 16-18 Oct 2026. Tag `v5.1` (commit d1ff89b). The model is frozen from here (Alex, 17 Oct
2026 07:58 / 08:18 UTC): later realism issues become sensitivity analyses, not model changes.

## 1. Summary

1. v5.1 makes the audit's corrections with values from human data, with no tuning to any Aim 1 check:
   - cross-fibre speed 0.36 m/s (HF 0.26), on Doste RV fibres;
   - a 2-ring graph solver;
   - bundle speeds at human values (1.5 / 2.0 m/s) instead of Durrer-tuned ones, and a straight-line distal Purkinje speed;
   - conductivities from the speeds, full blood fill and a sigma_i ECG source;
   - ecg_depth_criteria 0.4.0.
2. Every build gate passes except two:
   - the solver's agreement with openCARP (acceptance C), kept with its error reported, as Alex decided;
   - A4, which fails by construction of Doste's rule, also Alex's decision.
3. Aim 1 rescore: 2 of 9 gates pass, 6 fail and 1 is not evaluable (13 Oct v5: 3 / 5 / 1).
   - The only gate-level change: the absolute summit + cusp QRS falls from PASS to FAIL (119.5 ms vs 132-193). This is
     convention-dependent: true activation is 145 ms.
   - Within gate 2, the control heart now passes and 6G8DD8S5 overshoots.
4. The normal (His) beat is now closer to human data: QRS 76 ms (v5 94), RV breakthrough 27.5 ms after LV onset. Durrer's
   early LV areas are 9 ms apart and activation ends at 113 ms, so Durrer still fails.
5. Still open: the 27-site monodomain check (gate 9), to run on the frozen model before the OSF registration; the study-heart
   placement rule (Alex); the GitHub push (Alex's sign-in).

## 2. Fork values (recorded before first use, LABNOTES 16 Oct 23:06 PC time)

| Placeholder | Value | Source |
|---|---|---|
| Q_WINDOW_MS | 40 ms | Alex: "40 ms" on "Set the q-wave initial window for the rescore and Aim 2?", 15 Oct 2026 08:30:47 UTC |
| FASCICLE_SPEED | 2.0 m/s | Alex: "2.0 m/s" on "Set the left fascicle speed in the v5.1 conduction system?", 08:31:01 UTC |
| DOSTE_SCOPE | WHOLE_RV | Alex: "Whole RV" on "Apply Doste's RV fibre rule to the whole RV or only the RVOT free wall?", 08:31:14 UTC |
| Primary q rule | CSE recognition | Alex: "Make primary", 08:31:22 UTC; kept as written after STOP 2 ("Keep the CSE rule as written", 16 Oct 21:36:04 UTC) |

Decisions taken during the build:
- STOP 4a (17 Oct 01:39:48 UTC):
  - RV region = the RV side of the septal split (d > 0.5);
  - A4 recorded as failing by construction;
  - corner-sharing elements count as connected.
- STOP 4b, first round (17 Oct 04:06:56 UTC): graph factors calibrated on a synthetic slab (option 1).
- 17 Oct 07:58 UTC, "Adopt all":
  - test element-wise tensors first;
  - if acceptance C still fails, keep the graph and report its error;
  - freeze after v5.1;
  - run the monodomain check before the OSF registration.
- 18 Oct 12:59:10 UTC: "Nodal is good. Drop any caps or limits."
- 13:22:54 UTC: "Intracellular" (ECG source).
- 14:12:20 UTC, "All recommended":
  - C6 pinch edges count as passing;
  - stop the frozen openCARP run;
  - go for the lead fields.

## 3. Steps, commits, tags

| Step | What | Commits |
|---|---|---|
| 0 | Orientation (read only), STOP 0 | (README only) |
| 1 | Decision G: v5 committed, manifest, tag v5, guards, push | ad63ed7, b3bce5c, 8c484cf, 76f02ec, fdc840c, a30f97a |
| 2 | Decision H: ecg_depth_criteria 0.4.0, read-only v5 rescore | 766b647 (tag ecg_depth_criteria-0.4.0), 71b4a29 |
| 3 | Decision D: stimulus / retrograde check (reported only) | 6d898eb |
| 4.0-4.1 | Predictions (before any beat), speeds file | 966ee76 |
| 4.2 | Doste RV fibres (STOP 4a) | a4910a0, 6fd9667 |
| 4.3 | Graph solver, slab factors, acceptance A / C, S13, element-wise test (STOP 4b) | f0d5f03, 5fdfca8, 8185ca1, 12383a3, 55a8d66, ad0ae83 |
| 4.4 | Conduction system, E9 (STOP 4c) | 6705ba9 |
| 4.5 | Conductor and lead fields (STOP 4d) | 973a06d, 5f9c725 |
| 4.6 | v5.1 solver and His beats (STOP 4e) | c4fe22d, 5ffa017 |
| 4.7 | Tag v5.1, data hashes | d1ff89b (tag v5.1) |
| 5 | AHA labels and placement dry run (STOP 5) | 5f6cc00 |
| 6 | Pilot grids on v5.1, Aim 1 rescore (STOP 6) | ad121dd |
| 7 | This report, LABNOTES entry | (this commit) |

Tags: v5 (b3bce5c), ecg_depth_criteria-0.4.0 (766b647), v5.1 (d1ff89b). The remote has master up to 55a8d66. Every later
commit and the v5.1 tag wait for Alex's GitHub sign-in on the PC (the credential cache was lost on a WSL restart).

## 4. Table B: verification gates

| Gate | Criterion | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR | Result |
|---|---|---|---|---|---|
| Step 1 guards | guard tests; beats equal before / after | 7 / 7; bit-identical | bit-identical | bit-identical | PASS |
| Step 2 regression | 0.4.0 with window / recognition off = 0.3.0 | 579 beats bit-identical | | | PASS |
| A1 | Doste angles within 0.5 deg | max 0.0005 deg | idem | idem | PASS |
| A3 | RV epicardial / mid-wall helix sign | pass | pass | pass | PASS |
| A4 | endocardial fibre along l within 0.5 deg | up to 2.2 deg | idem | idem | FAIL by construction (Alex) |
| A5 | nodes outside R_new unchanged | 0 | 0 | 0 | PASS |
| A8 | one component; orthonormal | corner-sharing counted (Alex) | idem | idem | PASS |
| Solver A | slab: principal +-1.5 %, rays +-3 %, rotating wall +-2 % | 0.9992-0.9998; 1.34 %; 0.982 | HF: 0.9988-1.0011; 1.83 %; 0.989 | as 6G8DD8S5 | PASS |
| Solver B | held-out regions +-3 % | judged by C (the F01 measure is biased at HF anisotropy) | | | see C |
| Solver C | vs openCARP: median abs(dt) <= 1 ms, p95 <= 2 %, total +-2 % | 4 / 12 | 0 / 12 | 0 / 10 (2 non-converged) | FAIL: graph kept, error reported (Alex) |
| E6 | 6G8DD8S5 cut unchanged | n/a | diff empty | n/a | PASS |
| E8 | edge speed = class value | pass | pass | pass | PASS |
| F19 | de-duplication changes no v5.1 time | 0.0 ms | 0.0 ms | 0.0 ms | PASS |
| P6 | de-duplicated v_edge within 1 % | 3.0038 = 3.0038 | 2.8753 = 2.8753 | 2.8447 = 2.8447 | PASS |
| P7 | median straight-line speed 2.00 +- 0.02 m/s | 1.9975 | 2.0032 | 1.9967 | PASS |
| C5 | sigma_m ratio = (v_d / 0.60)^2 | pass | pass | pass | PASS |
| C6 | cavity surfaces: volume +-1 %, closed, oriented | 172.03 / 197.90 mL | 157.76 / 107.20 mL (15 pinch edges, counted, Alex) | 172.79 / 122.48 mL (11 pinch edges, idem) | PASS |
| C8 | blood fill +-2 %; torso inside < 1 %; endocardium >= 95 % | 1.000; 0.06-0.09 %; 100 % | 1.000; 0.07-0.13 %; 100 % | 1.000; 0.05-0.11 %; 100 % | PASS |
| C9 | ECG weights vs openCARP <= 0.0002 mV | 4.9e-7 | 5.1e-7 | 3.7e-7 | PASS |
| Step 6 | no unactivated node; His beats = Step 4.6 | pass | pass | pass | PASS |

Acceptance C, measured error of the adopted (nodal) graph against openCARP (tissue only, single-node stimulus):
- Y5HYEDL4: median abs(dt) 0.69-1.48 ms per site, totals within 1 %.
- 6G8DD8S5: 1.07-5.73 ms, totals -1.8 to +2.7 %.
- 7D98EVAR: 1.21-6.48 ms, totals -0.5 to +3.0 %. Worst at the aortic cusps.
- The same maps through the v5.1 lead fields (C9 report): median abs(graph - openCARP) QRS 0.5-2.5 ms, IDT 1-6 ms, MDI
  0.01-0.02. Pseudo-delta and shortest RS jumped 20-50 ms at a few sites (threshold measures).
- q in I differs at 1 of 34 sites.

## 5. Table A: Aim 1 gates

| # | Gate | 13 Oct v5 (true, 0.3.0) | 14 Oct v5 (surface ECG, 0.3.0) | v5, 0.4.0 | v5.1 primary | v5.1 verdict | Changed? | Convention-dependent? | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Absolute paced QRS, summit + cusp (control) | 159.0 PASS | 137.0 PASS | 137.0 PASS (inputs unchanged) | 119.5 | FAIL | dated correction (v5.1 rebuild, decisions A-H, 15 Oct 2026) | yes | true mode 145.0; summit / cusp 108.0 / 127.25 |
| 2a | Relative QRS Y5HYEDL4 | 1.0712 FAIL | 1.0586 FAIL (CI 1.000-1.124) | as 14 Oct | 1.0980 (CI 1.051-1.141) | PASS | dated correction (v5.1 rebuild, decisions A-H, 15 Oct 2026) | yes | true mode 1.0774 |
| 2b | Relative QRS 6G8DD8S5 | 1.1371 PASS | 1.1840 FAIL (CI 1.167-1.199) | as 14 Oct | 1.2170 (CI 1.190-1.239) | FAIL | dated correction (v5.1 rebuild, decisions A-H, 15 Oct 2026) | no | true mode 1.1646 |
| 2c | Relative QRS 7D98EVAR | 1.0930 PASS | 1.1147 PASS (CI 1.062-1.160) | as 14 Oct | 1.1427 (CI 1.101-1.180) | PASS | no | no | true mode 1.1016 |
| 3 | Daniels order (control) | .542, .458, .587, .679, .348 FAIL | .621, .497, .616, .689, .360 FAIL | as 14 Oct | 0.605, 0.450, 0.694, 0.637, 0.362 | FAIL | no | no | true mode 0.514, 0.415, 0.610, 0.579, 0.262 |
| 4 | Bazan 2006 RV (all) | 4.2/8.0, 4.1/14.7, 4.0/10.3 PASS | 3.9/6.1, 3.5/18.7, 4.3/12.9 PASS | as 14 Oct | 4.4 / 9.2, 3.9 / 22.6, 4.6 / 16.7 | PASS | no | no | true mode 3.6 / 7.7, 3.9 / 17.9, 5.4 / 10.6 |
| 5 | Bazan 2007 region Q (pooled) | 4/21 vs 3/21 FAIL | 4/21 vs 3/21 FAIL | FAIL (primary and every sensitivity) | 5/21 vs 3/21, diff 9.5 pp (CI -14.7 to 32.8) vs Bazan +74 | FAIL | no | no | 14 of 14 rule x convention combinations FAIL (primary, N20, window only, no window, wave 0.10 mV and 0.3.0; true mode, 14 Oct pace-map convention, 10 uV noise); AHA / body labels, basal superior: 7/17 vs 1/17 (not evaluable, < 20 positions) |
| 6 | Berruezo (6G8DD8S5) | 14.7/60.6/31.6/7.6 % FAIL | 18.7/60.6/31.6/7.6 % FAIL | as 14 Oct | 22.6/107.0/51.4/14.2 % | FAIL | no | no | true mode {'QRS': 17.9, 'PdW': 107.0, 'IDT': 51.4, 'RS': 14.2}; caveat: Berruezo's baseline QRS 194 +- 19 ms; no stimulus latency in the model |
| 7 | Durrer (control, His beat) | T 100.8; (a) 0/2.7/5.0 (calibrated); (b) 66.8 %; (c) 15.1; (e) 94 FAIL | (e) 94.5 FAIL | as 14 Oct | T 113.3; (a) 0.0/5.5/8.7 (1 of 3 within 5 ms, uncalibrated); (b) 85.2 % at 37.5 ms (63.4 % at 30); (c) 27.5; (d) last 5 % in Durrer areas 78.7 %; (e) 76.0 | FAIL | no | no | parts: T 62-100 FAIL, (a) >= 2 within 5 ms FAIL, (b) >= 90 % by 37.5 ms FAIL, (c) 20-31 ms PASS, (e) 63-88 ms PASS; His beat equal to Step 4.6: True |
| 8 | No-network control | 240.0 PASS | 220.25 PASS (7/7) | as 14 Oct | 230.75 (7/7 wider) | PASS | no | no | true mode 250.50 |
| 9 | Monodomain agreement | not evaluable | not evaluable | not run | not run | not evaluable | no | no | locked: 27 sites, 5 ms, >= 90 % of 108 pairs; runs on the frozen model before the OSF registration (Alex, 17 Oct) |
| | Tally (pass / fail / not evaluable; gate 2 counted once, failing if any heart fails) | 3 / 5 / 1 | 3 / 5 / 1 | 3 / 5 / 1 | | 2 / 6 / 1 | | | |

- **Changed vs 13 Oct:** gate 1 (PASS -> FAIL) and, within gate 2, 2a (FAIL -> PASS) and 2b (PASS -> FAIL).
- **Convention-dependent:** gates 1 and 2a. True mode reverses both.
- **Gate 5:** fails under all 14 rule x convention combinations.
- **Table B vs Table A:** none of the build gates was tuned to an Aim 1 result.

## 6. Table C: predictions vs results

| Quantity | Heart | PRED (4.0) / E9 (4.4) | v5 | v5.1 | Comparator |
|---|---|---|---|---|---|
| His -> first muscle (ms) | Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR | PRED-1 23-25 / 40-50 / 22-24; E9 21.9 / 40.8 / 20.8 | 19.9 / 26.4 / 18.8 | 21.9 / 40.8 / 20.8 | human HV 35-55; distal root dH-Q 18-35, HVdis 46 +- 10 |
| His -> detected QRS onset (ms) | idem | - | - | 23 / 42 / 22 | dH-Q 18-35 |
| Durrer (a) spread (ms); areas within 5 ms | idem | PRED-2: spread > 5 likely, < 2 areas possible; E9 12.6 / n/a / 11.2 | 5.0 / 22.4 / 5.4 (calibrated) | 8.7 (1 of 3) / 19.7 (1) / 6.3 (2) | >= 2 areas within 5 ms |
| RV epicardial breakthrough after LV onset (ms) | idem | PRED-3: about 30-36 | 15.1 / -12.4 / 16.4 | 27.5 / -11.5 / 30.5 | 20-31 |
| First RV endocardium after LV onset (ms) | idem | PRED-3: 20-26 | 6.6 / -24.2 / 8.2 | 19.3 / -23.4 / 21.3 | Durrer 5-10 (report) |
| LV endocardium outside posterobasal by 37.5 ms | idem | PRED-4: direction unpredictable | 66.8 / 40.6 / 61.0 % | 85.2 / 57.4 / 77.4 % | >= 90 % |
| Total His-beat activation (ms) | idem | - | 100.8 / 142.0 / 100.2 | 113.3 / 126.9 / 110.2 | Durrer 62-100 |
| His-beat QRS (ms) | idem | PRED-4: widen somewhat | 94 / 141 / 86 (13 Oct, detected) | 76 / 123 / 72 (spontaneous primary) | Durrer (e) 63-88; cohort male 90.3 +- 8; Mason 69-109; Rijnbeek men 20-29 y 80-126 |
| v_edge, distal Purkinje (m/s per edge) | idem | brief 3.6-3.9 (inference) | 2.0 (straight-line 1.0-1.1) | 3.00 / 2.88 / 2.84 (straight-line 2.00) | Camps 2024: <= 4.0 |
| A9 RV 10-ms isochrone length / width (RVOT sites, median) | idem | expected lower than Doste (inference) | not computed | 1.10 / 0.97 / 1.23 | Doste 1.86 +- 0.22; Acosta 2015 1.9 +- 1.2 |
| Taggart epicardial speeds, control tissue only, along / across (m/s) | Y5HYEDL4 | - | 0.612 / 0.636 | 0.61 / 0.65 | Taggart about 0.65 along; 0.576 across (14 Oct reading) |

Reading (inference, not verified):
- The His-to-first-muscle predictions were 1-2 ms high in the narrow-QRS hearts, and right for 6G8DD8S5.
- Durrer (a) failed in the control heart, as PRED-2 / E9 allowed.
- The RV breakthrough moved into Durrer's window, as PRED-3 expected.
- PRED-4 expected the His QRS to widen; it narrowed (94 -> 76 ms).
- v_edge came out about 20 % below the brief's guess.

## 7. Step 2 and Step 3 findings (on v5, reported)

**Step 2 (decision H, ecg_depth_criteria 0.4.0):**
- Tests 76 / 76.
- With the window and recognition off, 0.4.0 equals 0.3.0 bit for bit on all 579 v5 beats. At 20 / 40 ms only the q
  outputs differ.
- 0.3.0 -> 0.4.0 only removed q / initial-r calls, never added one. Changes: q in I at 73 site-modes, inferior r at 87.
  Causes: the window (1,125 lead-level changes) and recognition (552).
- Gate 5 failed under 0.3.0, 0.4.0 and every sensitivity, in true mode and the 14 Oct convention.
- At 20 uV noise, CSE recognition cuts false q in an isoelectric lead from 42 % to 2 %. It raises false q before a
  0.10 mV initial r from 2.25 % to 14.25 %. At 10 uV every rate is <= 0.25 %. Alex kept the rule.
- NaN handling: 6G8DD8S5's LV-septum IDT median is now 47.0 ms (3 unscorable). No gate used those tables.

**Step 3 (decision D, reported only):**
- Arm S, single-node stimulus:
  - Bazan 2006 RV median pair % 3.6 / 3.4 / 4.6 (true), still passing.
  - RV 90-10 differences grow 0-4 ms.
  - Y5HYEDL4 cusp MDI 0.587 -> 0.596 (true) and 0.616 -> 0.697 (14 Oct convention).
  - Daniels still fails.
- Arm R, retrograde 4 ms:
  - relative QRS 1.0653 / 1.1355 / 1.0866 (true) and 1.0536 / 1.1794 / 1.1094 (14 Oct); verdicts as v5;
  - MDI AUC falls 0.03-0.07;
  - first network activation at 10 % sites +2 ms.
- v5.1 keeps the 1.5 mm ball and the 2 ms retrograde delay.

## 8. Deviations and inferences

**Dated deviations (LABNOTES):**
- Decision A speeds.
- Doste RV fibres:
  - beta = 0 and no Eq. 5 blend;
  - a neighbour guard where grad Phi_D is parallel to l (75 / 74 / 98 elements);
  - RV region = the split side d > 0.5.
- Graph factors calibrated on a synthetic slab (option 1), not the brief's S5 heart fit: the F01 measure is biased at HF
  anisotropy.
- Element-wise metric tested (deviation entry written before results) and not adopted.
- Acceptance C failing, graph kept (Alex).
- openCARP caps:
  - the 20-min cap (17 Oct);
  - then no cap (Alex, 18 Oct);
  - two 7D98EVAR sites non-converged (no progress past t = 0; a rerun with max_iter 2147483647 was stopped by hand after
    64 min).
- Conduction-system classes and speeds; v_edge.
- Conductor: speeds -> conductivities, closed-surface blood tagging, sigma_i ECG source (Alex). The C9 check was run with
  sigma_m.
- ecg_depth_criteria 0.4.0 (decision H).

**Implementation fixes in my own code (no model effect):**
- slab extents;
- path speeds rounded in summary.json;
- E4 chord interpolation;
- the valve-plane report sign;
- the C9 frame alignment;
- the network_first_ms field in Step 3.

**Inferences (brief section 8, chosen values):**
- N = 40 ms is inferred: Vereckei's "initial 40 ms"; inside epicardial initial slow phases of 33-56 ms; > 6 x the 6.5 ms
  CSE onset tolerance.
- CSE recognition: 20 uV / 6 ms are CSE program limits (Kligfield 2007). The 5 x SD floor and the "reach +-wave_mv" step are
  this study's.
- Fascicles at 2.0 m/s rest on one pair of spikes in one heart (Durrer 1970). There is no human speed for the LB trunk or the
  RB beyond ~11 mm (1.5 m/s extrapolated). The His root position is unknown; ours is the LB/RB split.
- Doste: linear-in-w angles, d = 1 - Phi_D, apex rule, zero-flux rings, sign calibration, 0.5 deg and 1 % / 2 mm limits,
  beta and blend omitted.
- Also inferred:
  - solver tolerances (+-3 %, 1 ms, 2 %);
  - equal anisotropy;
  - blood ending at the valve rings;
  - the 10 mm minimum D_j;
  - the Step 3 design;
  - the Step 5 reading of decision F:
    - level thirds;
    - apex cap below f 0.08;
    - AV-ring sites take the last valid frame;
    - body basal / apical at f 0.5.
- Operational rules of the Step 6 reports (A9, LBBB items) are mine (reports51.py docstring).
- Step 6 run: Alex's "yes" (19:30:43 UTC) arrived before the 30-min estimate was posted. I took it as the OK and said so in
  the thread.

## 9. Files and hashes

**Brief and notes:**
- analysis/v51_2026-10-15/BRIEF_v51.md.
- LABNOTES.md (entries 16-18 Oct).
- README per step: 00_orientation, 01_backup, 02_measure_040, 03_stimulus_check, 04_build/README_4a ... 4g,
  05_aha_labels, 06_pilot_rerun.

**Code (v5.1):**
- 04_build: graph51.py, solver51.py, acceptance_c.py, network51.py, conductor51.py, heart51.py, ecg_side.py.
- 05_aha_labels: aha51.py.
- 06_pilot_rerun: grid51.py, rescore51.py, gates51.py, rescore040_51.py, report040_51.py, taggart51.py, reports51.py,
  tableA51.py.

**Parameters:**
- params/v51_speeds.json, v51_graph_factors.json (adopted, nodal), v51_graph_factors_element.json (tested, not adopted).
- params/params_network_<H>_v51.json, v51_conductivities.json.

**Manifests:**
- manifests/v5_data_sha256.tsv: 3,484 files, sha256 342388ba...09e0f6.
- manifests/v51_data_sha256.tsv: 70 entries, sha256 cb866bb0...c7c35.
  - fibres_v51, purkinje_v51 networks, torso full_nofast_blood_v51 .elem / .lon, lead fields, ecgW_v51.npz, graph caches,
    package modules.

**Step 6 arrays:**
- runs/v51_2026-10-15/06_pilot_rerun/maps: 1,174 arrays, 838 MB.
- per-file sha256 in maps_sha256.tsv (sha256 a0b89c61...b9b1).
- rescore/per_site.csv sha256 a49182ad...bb8b (2.3 MB, not committed; Alex to decide).
- rules/per_measurement.csv sha256 bd58cb98...c838.

**Check:** v5 files unchanged (full sha256 of all 3,484 manifest files at this final STOP; see LABNOTES).

## 10. Still open

- **Monodomain agreement (gate 9):** not run, not evaluable. Locked design: 27 sites, 5 ms, >= 90 % of 108 pairs, bias-band
  fallback. It runs on the frozen v5.1 before the OSF registration (Alex, 17 Oct); needs its own time estimate.
- **Study-heart placement (Step 5):** awaiting Alex.
  - Segments and sites per segment: the proposal is 17 segments x 4 depths.
  - Apex-cap rule: anchor to the endocardial apex, needed for 6G8DD8S5-like thick apices.
- **Open item from Alex (18 Oct 12:27 UTC):** the surface QRS end misses late basal activation. It bears directly on gates 1
  and 2 (true vs surface conventions). To check the detector against true activation and hand reading; then Alex chooses a
  dated measurement change or a sensitivity analysis.
- **Decision 8:** the conductivity sensitivity build costs 6-8 min, about 6.5 GB peak and about 50 MB per heart. Not run.
- **GitHub push:** Alex runs `git push -u origin master` and `git push origin v5.1` on the PC.
- **Proposal Model-tab entry:** done in the cloud later.
