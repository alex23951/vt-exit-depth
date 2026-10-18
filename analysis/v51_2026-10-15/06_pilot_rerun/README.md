# Step 6: pilot grids on v5.1 and the Aim 1 rescore (STOP 6)

PC clock 2026-10-18 21:30-22:40 CEST. Alex: "go" 19:29:08 UTC (timing run) and "yes" 19:30:43 UTC. The "yes" arrived
before my 30-min estimate was posted; I took it as the OK and said so in the thread.

## Beats

- 579 v5.1 beats, as on 13 Oct:
  - 3 His beats;
  - 432 paced sites (144 per heart, same sites.json, families and pairs);
  - 144 no-network beats of the control heart.
- Model: v5.1 (tag v5.1) through heart51.Heart51.
- Arrays: runs/v51_2026-10-15/06_pilot_rerun/maps/ (816 MB). grid51.py, 4 processes, 15-22 min, peak RSS <= 1.35 GB per
  process.
- No unactivated node in any beat. The His beats equal the Step 4.6 beats bit for bit.

## Scoring

- **Package:** ecg_depth_criteria 0.4.0 primary (q window 40 ms, CSE recognition).
- **Convention:** section 2 of the brief, with true mode beside.
- **Scripts:** copies of the 14 Oct rescore.py / gates_rescore.py and of 02_measure_040 rescore_040.py / report_040.py,
  paths only. Originals' sha256 are in copied_originals.sha256 and the diffs in copies.diff.
- **Unscorable values:** 0 (13,347 rows in rescore/per_site.csv). So n_scored = n_total in every heart x family x depth.

## Table A (Aim 1 gates)

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

Reading:
- **Tally:** v5.1 passes 2 of 9 gates, fails 6, and 1 is not evaluable. v5 on 13 Oct was 3 / 5 / 1.
- **Gate 1, absolute paced QRS (summit + cusp): PASS -> FAIL.** The v5.1 surface QRS is 119.5 ms against 132-193 ms. True
  activation (145 ms) would pass. This is convention-dependent, and linked to the open item on the surface QRS end
  missing late basal activation (LABNOTES 18 Oct 14:30).
- **Gate 2 (relative QRS), still FAIL overall:**
  - Y5HYEDL4 now passes: 1.098 (v5 1.0586). This is convention-dependent: true mode gives 1.0774, just below 1.0785.
  - 6G8DD8S5 fails high: 1.217, against 1.0785-1.1587.
  - 7D98EVAR passes: 1.143.
- **Gate 7, Durrer, still FAIL:**
  - (c) RV breakthrough 27.5 ms and (e) His QRS 76 ms now pass.
  - T (113.3 ms), (a) and (b) fail.
- **Gates 3, 5 and 6:** fail as before.
- **Gates 4 and 8:** pass as before.

## Step 6 reports (never used to retune; reports51.json, taggart/speeds.json)

- **A9, Doste's 10-ms isochrone on the RV endocardium (RVOT sites):** median length / width ratio 1.10 (Y5HYEDL4, range
  0.94-1.45), 0.97 (6G8DD8S5, 0.70-1.59) and 1.23 (7D98EVAR, 1.01-1.82).
  - Comparators: Doste 1.86 +- 0.22; clinical 1.9 +- 1.2 (Acosta 2015).
  - Lower, as expected (inference).
  - Network and tissue-only beats are identical here: the network is not reached within 10 ms of RV endocardial onset.
  - Median isochrone area: 155 / 112 / 122 mm2.
- **Taggart-style epicardial speeds (8 electrodes on the LV free wall, copy of the 14 Oct script with v5.1 maps and fibres):**
  - Control tissue-only: longitudinal 0.61 m/s, transverse 0.65 m/s (apparent, epicardial).
  - With the network, the paced wavefront is not a plane wave over the grid: see taggart/speeds.json.
- **6G8DD8S5 His beat against the LBBB criteria** (operational rules in reports51.py; slurring not scored):
  - QRS 123 ms.
  - V2 rS but V1 not QS / rS (R 0.64, S 1.72 mV).
  - Notching in all 6 leads.
  - No q in I, V5, V6.
  - R-peak time in V5 / V6: 64 / 67 ms.
  - Meets the AHA/ACCF/HRS 2009 items (QRS >= 120, no q in I / V5 / V6, R-peak time > 60 ms, notched R). Fails Strauss
    2011: QRS under 130 / 140 ms, and V1 not QS / rS.
- **His-beat QRS (spontaneous convention):** 76 / 123 / 72 ms.
  - The control's 76 ms is inside Mason 2007 (69-109 ms).
  - It is below the cohort's male controls (90.3 +- 8 ms) and below Rijnbeek 2014 men 20-29 y (80-126 ms).
- **Relative QRS bootstrap CIs (2,000 resamples, seed 0):** 1.051-1.141 / 1.190-1.239 / 1.101-1.180.
  - Bazan's CIs: basal inferior about 1.01-1.14, apical superior 1.08-1.24.
- **Berruezo (6G8DD8S5):** QRS / pseudo-delta / IDT / RS +22.6 / +107.0 / +51.4 / +14.2 %. RS is below the 20-52 % band.
  - Caveat: Berruezo's patients had a baseline QRS of 194 +- 19 ms, and the model has no stimulus latency.

## Files

- **Scripts:** grid51.py, rescore51.py, gates51.py, rescore040_51.py, report040_51.py, taggart51.py, reports51.py,
  tableA51.py.
- **Results:**
  - rescore/ (per_site.csv, gates.json);
  - rules_per_site.csv, rules_gates.json, rules_q_changes.csv, rules_q_report.md;
  - taggart/;
  - reports51.json, tableA51.json, tableA51.md.
- **Arrays and logs (runs/, git-ignored):** maps, rules/per_measurement.csv, the extra HF tissue-only RVOT beats in
  maps/<H>_nonet_rvot/, logs.

Large outputs (not committed; sha256):
- a49182ada5c73669ab389c20201db4bb18a5ffc99987b5f5c3a7cfec99f2bb8b  analysis/v51_2026-10-15/06_pilot_rerun/rescore/per_site.csv
- bd58cb980db5f27ee94885b173e8c5cfcca0960158022eacac706ca1c6fcc838  runs/v51_2026-10-15/06_pilot_rerun/rules/per_measurement.csv
- maps: 1174 arrays, 838M; per-file sha256 in runs/v51_2026-10-15/06_pilot_rerun/maps_sha256.tsv
- maps_sha256.tsv: a0b89c6184d6213a49cc414db2ac432868d46aac09b482e7aea6aca3132ab9b1  runs/v51_2026-10-15/06_pilot_rerun/maps_sha256.tsv
