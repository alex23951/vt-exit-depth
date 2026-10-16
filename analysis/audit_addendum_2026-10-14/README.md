# Audit addendum, 14 Oct 2026 (read-only; PC)

The specification was fixed by the cloud audit session before any result existed. Alex's decisions: "Rescore" and "Measure first" (14 Oct, 06:57-06:58 UTC), and "ok go" for regenerating the maps (17:32 UTC).

Nothing outside this folder was changed: no model file, result, LABNOTES, CLAUDE.md or git.

One rule slip: I ran `rm -rf` on two `__pycache__` folders that my own syntax check had just created inside this folder. That breaks the "no rm -rf" rule. Nothing else was deleted.

## What had to be regenerated (Alex's OK, 17:32 UTC)

- The 13 Oct v5 grid ran in memory. Its per-site activation maps and ECGs were never saved; only the His beats' were.
- `regen.py` recomputed them with the identical code path (v5_grid.Heart('E', h), junction delay 4.0 ms, saved v5 ECG weights ecgW_v5_<h>.npz). No lead field was rebuilt.
  - Output: `maps/<h>/` with 145 beats per heart, and `maps/Y5HYEDL4_nonet/` with 144 no-network beats.
  - 816 MB in total; 19 min of PC time with 2 processes.
- **A1 reproduction check passed: the regenerated beats are bit-exact** (`rescore/a1_repro.json`).
  - Every network beat matches the 13 Oct CSV: max |Δ| 0.0 for QRS, MDI, pseudo-delta, IDT and RS; total activation within 6e-14 ms; 0 q-flag mismatches.
  - The His beats equal the saved his_T / his_ecg exactly.
  - All 49 gate values match, with the same verdicts.
  - No-network beats: activation is identical (Δ ≤ 6e-14 ms), so the no-network gate (activation-based) reproduces at 240.0 ms.
  - Their ECG-derived values differ, because the 13 Oct no-network grid (arm E) used the v3 cb weights and the regeneration uses the v5 weights. Pseudo-delta differs by up to 45 ms, IDT up to 95 ms, RS up to 61 ms, MDI up to 0.17, and there is one q flip. So in slow no-network beats, IDT and RS react strongly to tiny lead-field changes.

## A. Rescore of the QRS-based Aim 1 gates

**Setup.** ecg_depth_criteria 0.3.0 with default Settings (PC copy; per-file sha256 in ../audit_2026-10-13/report.md A2). Package commit: code/ is tracked in git at 47808c6. The v5 model is uncommitted and nothing is pushed (no git remote).

**Noise.** The project's only noise code is analysis/noise_onset_2026-10-12/noise_onset.py. Its settings were kept, except as listed:

| Item | Setting |
|---|---|
| Noise | white Gaussian per independent lead (I, II, V1-V6); III, aVR, aVL and aVF derived |
| Filter | 2nd-order zero-phase Butterworth (sosfiltfilt); 1000 ms flat pads |
| Plan rule (as the spec says) | band 0.05-100 Hz, notch off |
| Effective noise after filtering | 10 µV in → about 5.1 µV RMS out; 20 µV with 0.5-150 Hz plus notch → about 9.9 µV out |
| Baseline wander | **not modelled** (the code has none) |
| Seeds | 0-9, the same at every site and in every heart; site value = median over the 10 |
| Sites the package could not score | 0 |

**Output.** Per-site file: `rescore/per_site.csv` (13,347 rows). Gate table: `rescore/gates.json` and `rescore/gates.txt`.

### Gate table

The primary value decides the verdict. "13 Oct" is the 13 Oct verdict as reported, which equals true mode except for Durrer (e) (13 Oct: detected clean, precordial offset).

| Gate | Primary value → verdict | A3 values | 13 Oct / true mode | Changed? | Convention-dependent? |
|---|---|---|---|---|---|
| Relative QRS Y5HYEDL4, ratio of means (1.0785-1.1587) | stim onset, clean, any-lead QRS: **1.0586 FAIL** (bootstrap CI 1.000-1.124) | stim + 10 µV 1.0722; precordial offset 1.0567 | 1.0712 FAIL | no | no |
| Relative QRS 6G8DD8S5 | **1.1840 FAIL (above the range)** (CI 1.167-1.199) | 1.1828; 1.1888 | 1.1371 PASS | **yes: PASS → FAIL** | **yes** (true mode passes) |
| Relative QRS 7D98EVAR | **1.1147 PASS** (CI 1.062-1.160) | 1.1179; 1.1275 | 1.0930 PASS | no | no |
| Bazan 2006, RV / LV median pair % | Y5 3.9 / 6.1; 6G 3.5 / 18.7; 7D 4.3 / 12.9: **PASS all** | 10 µV: 3.5/7.0, 3.5/18.3, 4.1/13.0; precordial: 3.9/6.7, 3.5/19.4, 4.3/14.6 | 4.2/8.0, 4.1/14.7, 4.0/10.3 PASS | no | no |
| Berruezo 6G8DD8S5 QRS / PdW / IDT / RS % | 18.7 / 60.6 / 31.6 / 7.6: **FAIL** (RS < 20) | 10 µV: 18.3 / 65.7 / 31.9 / −6.6; precordial: 19.4 / 60.6 / 31.6 / 7.6 | 14.7 / 60.6 / 31.6 / 7.6 FAIL | no | no |
| Bazan 2007 basal superior q in I, pooled 90 vs 10 | 4/21 vs 3/21; Bazan's 90/16 outside the CI: **FAIL** | 10 µV 5/21 vs 3/21; precordial 4/21 vs 3/21 | 4/21 vs 3/21 FAIL | no | no |
| Bazan 2007 other regions (n < 20, not evaluable) | apical superior 4/9 vs 2/9; basal inferior 8/8 vs 0/8; apical inferior 6/7 vs 0/7 | similar | same | no | no |
| Absolute QRS, summit + cusp, control (132-193) | detected, 10 µV: **137.0 PASS** (summit 129.25, cusp 137.25) | clean 138.0; 20 µV 134.0; 20 µV 0.5-150 + notch **128.75 FAIL**; stim → ECG offset 141.5 | 159.0 PASS | no | **yes** (legacy filter fails) |
| Daniels order, control: summit90 / vein90 / cusp / RVOT / LVendo10 | 0.621 / 0.497 / 0.616 / 0.689 / 0.360: **FAIL** | clean 0.625/0.503/0.621/0.699/0.362; 20 µV 0.616/0.492/0.592/0.667/0.342; legacy 0.610/0.486/0.586/0.663/0.358; stim 0.633/0.512/0.630/0.708/0.380 | 0.542/0.458/0.587/0.679/0.348 FAIL | no | no |
| No-network control: summit + cusp > 193 and wider in every family | 220.25; wider in 7/7: **PASS** | 224.5 / 211.25 / 205.75 / 228.5, all PASS | 240.0 PASS | no | no |
| Durrer (e) His QRS, control (63-88) | **94.5 FAIL** | clean 94.0; 20 µV 94.5; legacy 92.5; stim (His) → offset 116.0 | 94 FAIL (detected clean); true from His 121 | no | no |

**Dated correction to record** (Alex, 14 Oct 2026, 06:57 UTC, measurement mismatch): **6G8DD8S5 relative QRS, PASS → FAIL.**
- Primary value 1.1840: the ratio is now above the upper bound 1.1587.
- 13 Oct value: 1.1371 (true mode).
- The verdict depends on the convention.

### Per-family medians behind the no-network gate (primary)

Medians in ms, [no network, network]:

| Family | No network | Network |
|---|---|---|
| LV free wall | 224.5 | 138.75 |
| LV septum | 193.25 | 120.75 |
| RV free wall | 246.25 | 139.25 |
| RVOT | 215.75 | 133.5 |
| Aortic cusp | 212.0 | 137.25 |
| LV summit | 239.25 | 129.25 |
| LV vein course | 237.5 | 141.25 |

## B. Taggart-style apparent conduction speed (`taggart/`)

**Grid.**
- Centre: LV free-wall epicardium at UVC z 0.51 / 0.51 / 0.52, at the middle of the free-wall arc between the RV insertion lines (−172° / −175° / −176° from the septal direction).
- Long axis: the local v5 epicardial fibre.
- Electrodes snapped to nodes within ≤ 0.8 mm (`electrodes.csv`).

**Candidates.** All RV free-wall and RVOT v5 beats (44 per heart).

**Chosen beats and speeds** (m/s; primary = fit 1/gx or 1/gy; "2-pt" = two-point estimate):

| Heart, grid | Run | Beat | Angle to axis | Accepted (≤ 20°) | Primary | 1/\|g\| | 2-pt | Fit RMS |
|---|---|---|---|---|---|---|---|---|
| Y5HYEDL4 primary, network | longitudinal | rv_free_wall_q25_z0.5_d50 | 14.2° | yes | **1.509** | 1.463 | 1.599 | 0.92 ms |
| Y5HYEDL4 primary, network | transverse | rv_free_wall_q75_z0.5_d50 | 1.9° | yes | **2.270** | 2.269 | 2.317 | 1.01 ms |
| Y5HYEDL4 basal 1 cm, network | long / trans | q25_z0.5_d75 / q75_z0.5_d10 | 36.5° / 30.4° | no / no | 2.261 / 2.172 | | | |
| Y5HYEDL4 apical 1 cm, network | long / trans | q25_z0.5_d75 / q50_z0.75_d90 | 28.6° / 8.0° | no / yes | 2.127 / 1.987 | | | |
| Y5HYEDL4 primary, **no network** | longitudinal | rv_free_wall_q25_z0.25_d50 | 0.2° | yes | **0.612** | 0.612 | 0.611 | 0.17 ms |
| Y5HYEDL4 primary, **no network** | transverse | rv_free_wall_q75_z0.5_d75 | 8.8° | yes | **0.636** | 0.629 | 0.652 | 0.16 ms |
| Y5HYEDL4 basal 1 cm, no network | long / trans | q25_z0.25_d90 / q75_z0.5_d90 | 3.4° / 8.1° | yes / yes | 0.567 / 0.633 | | | |
| Y5HYEDL4 apical 1 cm, no network | long / trans | q25_z0.25_d75 / q75_z0.25_d50 | 0.8° / 8.6° | yes / yes | 0.594 / 0.675 | | | |
| 6G8DD8S5 primary (HF; input cross-fibre 0.35) | long / trans | q25_z0.25_d10 / rvot_septal_d90 | 6.5° / 39.7° | yes / no | 0.787 / 1.194 | | | 1.3 / 0.7 ms |
| 7D98EVAR primary (HF) | long / trans | q25_z0.75_d75 / q75_z0.75_d10 | 2.2° / 8.4° | yes / yes | 6.483 / 1.256 | | | 0.6 / 1.1 ms |

Basal and apical HF grids are in speeds.json: apparent speeds 1.5-4.7 m/s, fit RMS up to 2.5 ms.

**Reading, applied exactly as fixed in the spec** (control heart):
- **Primary (network beats):** longitudinal 1.51 m/s, outside 0.52-0.78. Transverse 2.27 m/s, above 0.576, so by the fixed reading the 0.48 setting "likely double-counts" (implied intrinsic transverse 0.48 × 0.48 / 2.27 = 0.10 m/s).
- **Caveat** (observation, not a change of setting): with the network, the epicardium under the grid is reached by breakthrough from the LV Purkinje network, not by a wave travelling across the epicardium.
  - The 8 times fit a plane less well: RMS ~1 ms, against 0.16-0.2 ms without the network.
  - Apparent speeds range from 0.8 to 6.5 m/s across hearts and grid positions.
  - So the network-beat value does not measure tissue conduction.
- **Tissue only (no-network control, sensitivity):**
  - Longitudinal 0.612 m/s (basal 0.567, apical 0.594): consistent with Taggart's ~0.65.
  - Transverse 0.636 m/s (basal 0.633, apical 0.675): above 0.576, so by the fixed reading the 0.48 setting likely double-counts. Implied intrinsic transverse = 0.48 × 0.48 / 0.636 = **0.36 m/s**.
  - In the solver itself, the realised in-wall transverse speed is 0.489 and the fibre speed 0.564 (audit F01), so the epicardial apparent-to-intrinsic transverse ratio is about 1.30.
- **HF hearts** (input cross-fibre 0.35 m/s): reported only, no no-network beats. 6G8DD8S5's transverse run has no accepted beat (best 39.7°).
- Any model change that follows (for example an anisotropy arm) is Alex's decision.

## 3. Other read-only checks (`part3/part3.json`)

### 3.1 Daniels MDI AUC

The plan's exact definition is not on the PC, so the variants are written out. AUC (number of positives, number of negatives); true / detected onset.

| Variant | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| A: positives summit 90 + vein 90; negatives cusp + RVOT + LV endo 10 | 0.553 / 0.541 (5, 34) | 0.600 / 0.612 | 0.418 / 0.406 |
| B: cusps out | 0.600 / 0.608 (5, 26) | 0.692 / 0.700 | 0.515 / 0.492 |
| C: negatives RVOT 10 % only | 0.0 / 0.0 (5, 2) | 0.5 | 0.0 |
| D: negatives LV endo 10 only | 0.867 / 0.878 (5, 18) | 0.811 / 0.778 | 0.744 / 0.711 |
| E: cusps as positives | 0.683 / 0.680 (13, 26) | 0.774 / 0.781 | 0.589 / 0.565 |
| Out of domain: 90 vs 10, LV free wall + septum + RV free wall | 0.716 / 0.723 (27, 27) | 0.728 / 0.676 | 0.724 / 0.711 |

Summit-site distances from the left-sinus point: superior 12.8-14.0 / 15.6-20.2 / 11.7-13.2 mm; inferior-lateral 18.4-18.9 / 21.2-22.8 / 16.8-17.7 mm.

### 3.2 His-beat 12-leads

- **Exports:** `part3/his_ecg_<H>.csv` (1 ms, t = 0 at the His) and 72 outflow-site traces in `part3/outflow_traces/`.
- **Control and 7D98EVAR:**

| Item | Y5HYEDL4 | 7D98EVAR |
|---|---|---|
| Detected QRS | 94 ms | 86/87 ms |
| Axis net / area | 64° / −17° | 67° / 64° |
| Septal q in I, aVL, V5, V6 | present (normal) | present |
| V1 R / S | 0.77 / 0.51 mV, so R > S | 1.05 / 0.89 mV, R > S |
| Transition | already at V1 (abnormal for a normal beat) | already at V1 |
| R peak time V5 / V6 | 41 / 43 ms | 47 / 51 ms |
| Peak-to-peak limb / precordial | 0.66 / 2.92 mV | 0.93 / 2.81 mV |

- **6G8DD8S5:** QRS 141 ms; axis −36° / −29°; no q in I, V5, V6; R peak time V5 / V6 71 / 73 ms; transition at V5; V1 rS (0.15 / 1.10 mV); V2 R/S 0.25 (0.43 / 1.70 mV).
  - **AHA/ACCF/HRS 2009 LBBB: all assessable items met.** ST-T cannot be assessed: the template has no repolarisation.
  - **Strauss 2011 (women):** QRS ≥ 130 met; QS/rS in V1-V2 met in V1, borderline in V2 (r = 25 % of S); notching or slurring flagged in 6 leads by my heuristic detector. That detector also flags slurs in the control beat, so treat it as unreliable.

### 3.3 Durrer time zero (solver clock, His = 0 ms)

| Event | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| First muscle | 19.9 | 26.4 | 18.8 |
| First LV endocardium | 19.9 | 50.5 | 18.8 |
| First RV endocardium | 26.5 | 26.4 | 27.0 |
| RV epicardial breakthrough | 35.0 | 38.1 | 35.2 |
| Latest activation | 120.8 | 168.4 | 119.0 |

- The bundle calibration fits only two things:
  - The LV Durrer sites at 0 / +2.5 / +5 ms after the first site.
  - The RV moderator-band end at +7.5 ms after the first LV site.
- The absolute His → first LV site time is the shortest path at 2.0 m/s: 15.9 / 17.3 / 14.8 ms in the network, plus 4 ms exit delay.
- There is no target for latest activation, RV breakthrough or QRS.

### 3.4 Network

- **Distal speed** is 2.0 m/s per edge (1 mm segments along the grown tree), not a straight line.
- **Path tortuosity** (path length / straight line):

| | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| His → junction, median (p10-p90) | 2.22 (1.34-3.92) | 3.15 | 2.05 |
| Root → junction | 1.79 (1.18-2.38) | 1.94 | 1.80 |
| Effective straight-line distal speed | 1.12 m/s | 1.03 m/s | 1.11 m/s |

- **Junctions:** depth 0 mm; all on the endocardial surface.
- **Bundles:** lengths and speeds are in ../audit_2026-10-13/report.md B5. The full parameter list with sources is in part3.json "3.4_parameters_14_purkinje".
- **Share of RVOT-beat muscle reached through the network:** proxy only. For the septal RVOT 10 % beats, 81 / 90 / 79 % of nodes activate more than 1 ms earlier than in the myocardium-only beat (audit a03b).

### 3.5 RVOT beats (v5, ms from the stimulus)

| Measure | Septal RVOT | Free-wall RVOT |
|---|---|---|
| Rapid onset (end of pseudo-delta) | 88-90 / 78-79 / 85-86 | 46-53 / 41-60 / 55-61 |
| Largest deflection | 90-92 / 92-93 / 100-101 | 102-109 / 75-80 / 108 |
| QRS end (last activation) | 148-150 / 139-140 / 145-147 | 137-142 / 168-170 / 155-157 |
| Detected onset (clean ECG) | 3-14 ms after the stimulus | same |
| Height below the PV plane, mm | 9.6-10.9 / 13.2-15.1 / 9.6-10.6 | 15.2-15.8 / 16.3-16.6 / 14.2-15.2 |

- **Septal RVOT 10 %:** first His at 62.5 / 99.8 / 62.8 ms; first network entry at 40.6 / 17.3 / 44.8 ms.
- **Path to the LV:** runs through muscle continuous with the LV in all three hearts, with no cavity or aortic-root gap (rvot_anatomy 12 Oct).

### 3.6 Conductivities and graph vs openCARP

- Conductivities, per heart and direction: ../audit_2026-10-13/a08_ecg_conductivity.txt.
- Blood: tag 101 at 0.7 S/m, covering 70 / 56 / 70 % of the cavities.
- Graph vs openCARP on v5 sites: there are no openCARP v5 runs. On v3 sites the total times agree, but local speed differs by direction (audit F01).

### 3.7 Commit

The v5 model has no commit and nothing has been pushed (no git remote). The last commit is 47808c6 (10 Oct).
