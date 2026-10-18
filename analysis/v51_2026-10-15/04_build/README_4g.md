# Step 4.6: the three v5.1 His beats, and Table B so far (STOP 4e)

PC clock 2026-10-18 16:50-17:00 CEST. Alex 14:45:56 UTC: "Yes".
- **Solver:** heart51.py (Heart51), built from the adopted nodal graph tissue solver, the v5.1 network and the v5.1 sigma_i
  ECG weights.
- **Coupling check:** fed v5's tissue graph and network, heart51's coupling reproduces the v5 solver bit for bit (His beat
  and one paced site: 0.0 ms).
- **Outputs:** his51_<H>.json; arrays in runs/v51_2026-10-15/04_build/<H>/his51/.
- **Scoring:** values here are clean-ECG reports. Step 6 scores the Aim 1 gates with the full convention (noise etc.).

## His beats (reported, nothing changed)

| | Y5HYEDL4 (control) | 6G8DD8S5 (LBBB-like) | 7D98EVAR | Comparator |
|---|---|---|---|---|
| His -> first muscle (ms) | 21.9 | 40.8 | 20.8 | E9 21.9 / 40.8 / 20.8; PRED-1 23-25 / 40-50 / 22-24 |
| His -> detected QRS onset (ms) | 23 | 42 | 22 | distal root: dH-Q 18-35, HVdis 46 +- 10 |
| Total activation T (ms) | 113.3 | 126.9 | 110.2 | Durrer 62-100 (control gate) |
| (a) onsets ant / sep / post after LV onset (ms) | 0 / 5.5 / 8.7 | 19.7 / 9.3 / 0 | 0 / 3.9 / 6.3 | >= 2 areas within 5 ms |
| (a) areas within 5 ms; spread | 1; 8.7 ms | 1; 19.7 ms | 2; 6.3 ms | PRED-2: spread > 5 ms |
| (b) LV endo outside posterobasal, by 30 / 37.5 ms | 63.4 / 85.2 % | 38.2 / 57.4 % | 55.3 / 77.4 % | >= 90 % by 37.5 ms |
| (c) RV epi breakthrough after LV onset (ms) | 27.5 | -11.5 (RV first) | 30.5 | 20-31 |
| First RV endocardium after LV onset (ms) | 19.3 | -23.4 | 21.3 | Durrer 5-10 (report) |
| (e) His QRS, clean, detected (ms) | 75 | 123 | 72 | 63-88 (control gate) |
| Frontal axis, net / area (deg) | +79 / +115 | -16 / -11 | +81 / +88 | |
| R/S V1, V6 | 1.01, 1.69 | 0.37, 20.2 | 1.18, 1.91 | |
| Sokolow-Lyon (mV) | 4.02 | 3.30 | 3.09 | |
| Frontal net magnitude (mV) | 0.57 | 0.97 | 1.21 | |

Against v5 (control, 13 Oct, true mode):
- T: 100.8 -> 113.3 ms.
- (a): 0 / 2.7 / 5.0 -> 0 / 5.5 / 8.7 ms. The v5 values were calibrated to Durrer; the v5.1 ones are not.
- (b): 66.8 -> 85.2 % at 37.5 ms.
- (c): 15.1 -> 27.5 ms.
- (e): 94 -> 75 ms.

Reading (inference, not verified):
- The control His beat is now narrower, with an RV breakthrough inside Durrer's window. The early LV areas are spread out,
  and activation finishes later than Durrer's 100 ms.
- Sokolow-Lyon and R/S in V1 are high for a normal heart. Part of this is the 1.28x sigma_i source (Alex's choice); the
  rest is torso and lead placement. Voltages are reported only.
- PRED-4 expected the His-beat QRS to widen somewhat. It narrowed instead (94 -> 75 ms).

## Table B: verification gates so far

| Gate | Criterion | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR | Result |
|---|---|---|---|---|---|
| Step 1 guards | guard tests; beats equal before / after | 7 / 7 tests; bit-identical | bit-identical | bit-identical | PASS |
| Step 2 regression | 0.4.0 with window / recognition off = 0.3.0 | 579 beats bit-identical (all hearts) | | | PASS |
| A1 Doste angles | abs(dh) and tilt <= 0.5 deg | max 0.0005 deg | idem | idem | PASS |
| A3 RV epi / mid-wall sign | as Doste | PASS | PASS | PASS | PASS |
| A4 endocardial fibre along l | <= 0.5 deg at d <= 0.02 | up to 2.2 deg | idem | idem | FAIL by construction (Alex) |
| A5 nodes outside R_new unchanged | 0 changed | 0 | 0 | 0 | PASS |
| A8 connectivity, orthonormal | one component | PASS (corner-sharing counted, Alex) | idem | idem | PASS |
| Solver A (slab) | principal +-1.5 %, rays +-3 %, transmural +-2 % | PASS | PASS (HF factors) | PASS (HF factors) | PASS |
| Solver B (held-out regions) | +-3 % | judged by C at the held-out sites (measure biased) | | | see C |
| Solver C (vs openCARP) | median abs(dt) <= 1 ms, p95 <= 2 %, total +-2 % | 4 / 12 | 0 / 12 | 0 / 10 (2 non-converged) | FAIL: graph kept, error reported (Alex) |
| E6 6G cut unchanged | diff vs v5 empty | n/a | empty | n/a | PASS |
| E8 class speeds | every edge = class value | PASS | PASS | PASS | PASS |
| F19 duplicates | de-duplication changes no v5.1 time | 0.0 ms | 0.0 ms | 0.0 ms | PASS |
| P6 de-duplicated v_edge | within 1 % | 3.0038 = 3.0038 | 2.8753 = 2.8753 | 2.8447 = 2.8447 | PASS |
| P7 straight-line speed | median A_j 2.00 +- 0.02 | 1.9975 | 2.0032 | 1.9967 | PASS |
| C5 sigma_m ratio | (v_d / 0.60)^2 to 1e-6 | PASS | PASS | PASS | PASS |
| C6 cavity surfaces | volume +-1 %, closed, oriented | PASS | PASS (pinch edges counted, Alex) | PASS (idem) | PASS |
| C8 blood fill | +-2 %, < 1 %, >= 95 % | PASS | PASS | PASS | PASS |
| C9 weights vs openCARP | <= 0.0002 mV | 4.9e-7 | 5.1e-7 | 3.7e-7 | PASS |

Next, after Alex's go (brief 4.7):
- commit, tag v5.1 and add all v5.1 data hashes to the manifest;
- push, which needs Alex to sign in to GitHub on the PC;
- a short LABNOTES entry.

Then Step 5 (AHA labels, read only), then Step 6 (pilot grids and the Aim 1 rescore; about 1.5 h of PC time, needs an OK).
