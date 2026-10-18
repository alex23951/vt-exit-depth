# Step 4.5: lead fields and ECG source term (C1-C9, decision 8 cost), STOP 4d

PC clock 2026-10-18 15:20-16:41 CEST. Scripts: conductor51.py (tensors, blood, lon, leadfield, weights) and ecg_side.py.
The read-only checks and C1-C8 are in README_4e_first_checks.md.

Alex's answers:
- "Intracellular", 13:22:54 UTC: the ECG source uses sigma_i.
- "All recommended", 14:12:20 UTC:
  - the C6 pinch edges count as passing;
  - the frozen openCARP rerun is stopped;
  - go for the control heart's lead fields.
- "Both", 14:25:32 UTC: go for the two HF hearts' lead fields.

## Gates (Table B rows)

| Gate | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| C5 sigma_m ratio | PASS | PASS | PASS |
| C6 cavity surfaces (volume, closure, orientation) | PASS | PASS (RV: 15 pinch edges, counted as passing by Alex) | PASS (RV: 11 pinch edges, idem) |
| C8 blood fill | PASS (100 %) | PASS (100 %) | PASS (100 %) |
| C9 weights vs openCARP (<= 0.0002 mV), sigma_m | 4.9e-7 mV PASS | 5.1e-7 mV PASS | 3.7e-7 mV PASS |

Lead-field builds (2 processes, light AMG options, watchdog at 900 MB):

| | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| Time | 489 s | 377 s | 404 s |
| Peak memory used (of 7.9 GB) | 6.45 GB | 5.82 GB | 5.88 GB |

- v5.1 weights: data/biv/<H>/ecgW_v51.npz, written with sigma_i.
- Every weight is 1.2784 x its sigma_m value (= 0.799 / 0.625).

## C9 report (not gated)

The acceptance C activation maps were run through the v5.1 lead fields: openCARP vs the adopted nodal graph solver, tissue
only. Scoring used ecg_depth_criteria 0.4.0 in the pace-map convention. Values are |graph - openCARP|, median / max over
sites.

| | Y5HYEDL4 (12) | 6G8DD8S5 (12) | 7D98EVAR (10) |
|---|---|---|---|
| QRS (ms) | 0.5 / 8 | 1.5 / 7 | 2.5 / 7 |
| pseudo-delta (ms) | 2 / 40 | 1.5 / 9 | 2.5 / 26 |
| IDT V2 (ms) | 1 / 1 | 3 / 10 | 6 / 10 |
| shortest RS (ms) | 2 / 32 | 2 / 19 | 2.5 / 52 |
| MDI | 0.010 / 0.096 | 0.011 / 0.057 | 0.021 / 0.061 |
| q in I calls that differ | 0 | 0 | 1 |

- **Typical sites:** the graph's timing error (1-6 ms) moves QRS, IDT and MDI only a little.
- **Threshold measures:** at a few sites pseudo-delta and shortest RS jump by 20-50 ms. These are threshold-based measures,
  and a small timing change can switch which deflection crosses the threshold, as seen on 14 Oct.
- **Full tables:** ecg_side_<H>.csv.

## Decision 8, cost only (no run)

One more lead-field build per heart with the sensitivity conductivities is the same openCARP job:
- about 6-8 min per heart;
- peak memory 5.8-6.5 GB of 7.9 GB with 2 processes, so it must run alone with the watchdog;
- about 50 MB of disk per heart;
- 20 s for the weights.

Rescoring beats with the new weights is extra.

v5 files unchanged: yes.
