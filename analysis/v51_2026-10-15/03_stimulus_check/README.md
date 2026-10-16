# Step 3: decision D, stimulus-size and retrograde-delay check on v5 (reported only)

PC clock 2026-10-16 23:37-23:51 CEST (UTC 21:37-21:51). Alex "Go for Step 3" (16 Oct 21:36:04 UTC). Nothing here is used to
retune: v5.1 keeps the 1.5 mm ball and the 2 ms retrograde delay. No verdict changes.

## Design (beat list posted at STOP 2, run as posted)

**Solver:** the guarded v5 copy, Heart('E'), junction antegrade delay 4 ms, v5 ECG weights. stim_check.py `solve_ext()`
is `Heart.solve()` with two switches that default to v5:
- `stim`: `'ball'` (v5) or `'node'` (the site node only)
- `d_ret`: 2 ms (v5) or 4 ms

**Cache:** the graph cache (tissue graph only) is not affected by either switch, so it is reused unchanged.

**Beats (125 in all):**
- Arm S, single-node stimulus: RV free wall 9 positions × 10 / 90 % × 3 hearts (54), plus Y5HYEDL4 aortic cusps at all depths (8)
- Arm R, retrograde 4 ms: LV free wall 10 positions × 10 / 90 % × 3 hearts (60)
- Reproduction: the v5 defaults at rv_free_wall_q25_z0.25_d10 in each heart (3)

**Run:** 411 s (Y5HYEDL4) in parallel with 342 + 283 s (6G8DD8S5, 7D98EVAR). Peak RSS 0.70 GB per process.
Unactivated nodes: 0.

## Acceptance

| Check | Result |
|---|---|
| v5 defaults reproduce the saved 14 Oct beat (activation map and ECG), 3 hearts | PASS (bit-identical) |
| `solve_ext()` with defaults equals `Heart.solve()` | PASS |
| Every Arm R beat (all have a retrograde network entry) differs from its v5 beat | PASS, 60 / 60 (max change 4.0 ms median, 6.0 ms max) |
| Arm S beats differ from v5 | 62 / 62 |
| 0.3.0 and 0.4.0 give identical values for these measures | yes |

A bug in my script, fixed: the run's `beats.json` field `network_first_ms` included the solver's source node, so it read
−1e-6 ms. The beats themselves are unaffected. The score stage now takes the first network activation as the earliest
junction muscle time + the retrograde delay. A fresh `verify` solve in each heart confirmed this equals the network
minimum (9 / 9 beats, and those beats equal the saved maps; runs/.../verify_<H>.json).

## Results (Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR; report.json, beats.csv)

**Arm S, single-node stimulus:**
- Bazan 2006 RV median per-pair QRS % (90 vs 10):
  - true mode: v5 4.2 / 4.1 / 4.0 → Arm S 3.6 / 3.4 / 4.6 (LV 8.0 / 14.7 / 10.3)
  - 14 Oct convention: 3.9 / 3.5 / 4.3 → 4.1 / 3.4 / 4.6 (LV 6.1 / 18.7 / 12.9)
  - The gate still PASSES in every heart and convention.
- RV 90-10 median paired differences, true mode, v5 → Arm S:
  - QRS +6 / +7 / +6 → +6 / +6 / +7 ms
  - pseudo-delta +6 / +9 / +6 → +7 / +9 / +7
  - MDI +0.013 / +0.018 / +0.016 → +0.018 / +0.021 / +0.018
  - IDT +6 / +7 / +8 → +7 / +8 / +10
  - shortest RS +4 / +4 / +9 → +6 / +8 / +10 ms
  - Depth separation in the RV grows slightly with a point stimulus; the 14 Oct convention is similar.
- Y5HYEDL4 cusps, v5 → Arm S:
  - true QRS 157.5 → 160.0 ms; true MDI 0.587 → 0.596
  - 14 Oct convention (detected, 10 µV): QRS 137.2 → 137.8 ms, MDI 0.616 → 0.697
  - Daniels order with the Arm S cusp median: still FAIL in both conventions. The cusp now exceeds the RVOT (0.697 vs 0.689) in the 14 Oct convention, but the summit 90 % (0.621) and vein 90 % (0.497) stay below it.

**Arm R, retrograde 4 ms** (LV free wall 90 / 10 %, ratio of mean QRS, v5 → Arm R):
- true mode 1.0712 / 1.1371 / 1.0930 → 1.0653 / 1.1355 / 1.0866 (FAIL / PASS / PASS unchanged)
- 14 Oct convention 1.0586 / 1.1840 / 1.1147 → 1.0536 / 1.1794 / 1.1094 (FAIL / FAIL / PASS unchanged)

Up-counts and AUCs, true mode, v5 → Arm R:
- pseudo-delta 10/10, 9/10, 10/10 and AUC 0.78 / 0.90 / 0.89: unchanged
- MDI AUC 0.87 / 0.87 / 0.94 → 0.80 / 0.82 / 0.91 (6G8DD8S5 up 10 → 9 / 10)
- IDT AUC 0.47 / 0.55 / 0.51 → 0.44 / 0.55 / 0.54
- RS AUC 0.40 / 0.59 / 0.45 → 0.40 / 0.67 / 0.53

First network activation at the 10 % sites (median, range): 2.6 (2.0-9.0) / 4.2 (2.0-10.2) / 5.6 (2.0-14.7) ms → +2 ms in
every site under Arm R. An endocardial exit captures the network within a few ms either way (audit F04).

The bootstrap CIs of the v5 ratios differ from the 14 Oct ones in the third decimal (e.g. Y5HYEDL4 1.003-1.125 vs
1.000-1.124). The method and seed are the same; only the order of the 10 pairs differs.

## Files

stim_check.py (stages run / verify / score), beats.csv (per beat: both arms and their v5 beats, true and 14 Oct
conventions, both packages), report.json, report.md. Maps and ECGs: runs/v51_2026-10-15/03_stimulus_check/<arm>/<H>/ (176 MB).
