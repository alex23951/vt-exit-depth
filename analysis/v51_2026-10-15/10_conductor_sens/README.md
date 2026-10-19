# Decision 8 conductivity sensitivity on v5.1 (19 Oct 2026)

Alex, 19 Oct 2026 17:58:45 UTC: "2" (run the decision 8 check). Sensitivity only: nothing adopted, v5.1 unchanged.

**Set** (`sigma_sens.json`): fibre sigma_i / sigma_e 0.174 / 0.625 S/m as v5.1; in both cross-fibre directions
sigma_e = 0.236 S/m, with sigma_i solved so sigma_m keeps the v5.1 speed ratios. Control heart: sheet 0.0618 / 0.236,
normal 0.1381 / 0.236 (v5.1 0.0626 / 0.225, 0.1114 / 0.400). HF hearts: sheet 0.0287 / 0.236, normal 0.0521 / 0.236
(v5.1 0.0327 / 0.1174, 0.0546 / 0.196). Blood 0.7, torso 0.2 S/m. The activation maps are unchanged; only the lead fields
and ECG weights change.

**Pipeline**:
- `sens51.py`: lead fields as conductor51.py, then the C9 check, which passes (4.8-5.0e-7 mV).
- `sens_ecg51.py`: the 579 Step 6 pilot-beat ECGs with the new weights. With the v5.1 weights, the same code reproduces
  the stored His ECGs within 1.7e-7 mV.
- The Step 6 scoring scripts, copied with path changes only (`copies.diff`, 10 lines), giving `tableA51.md`.

The weights change by 59-62 % (relative L2, per lead) in the control heart and by 15-17 % in the HF hearts.

## Result

**Table A: no verdict changes.** Tally 2 pass / 6 fail / 1 not evaluable, the same as v5.1 (gate 9 here is the Step 6
placeholder; the monodomain check itself failed on 19 Oct). The primary values move a little:

| Gate | v5.1 | Sensitivity |
|---|---|---|
| 1 | 119.5 ms | 119.5 ms |
| 2a / 2b / 2c | 1.0980 / 1.2170 / 1.1427 | 1.0980 / 1.2175 / 1.1453 |
| 3 | 0.605, 0.450, 0.694, 0.637, 0.362 | 0.614, 0.465, 0.696, 0.645, 0.345 |
| 4 | 4.4 / 9.2, 3.9 / 22.6, 4.6 / 16.7 | 3.6 / 9.7, 3.9 / 22.5, 4.6 / 16.5 |
| 5 | 5 / 21 vs 3 / 21 | 6 / 21 vs 3 / 21 |
| 6 | 22.6 / 107.0 / 51.4 / 14.2 % | 22.5 / 110.1 / 50.7 / 14.2 % |
| 7 (e) | 76.0 | 76.5 |
| 8 | 230.75 | 231.25 |

**Per beat** (432 paced network beats, stimulus onset, clean ECG; sensitivity minus v5.1):

| Measure | Median change | Within 5 ms (MDI: 0.05) | Largest change |
|---|---|---|---|
| QRS duration | 0 ms | 98 % | 21 ms |
| Pseudo-delta | 0 ms | 98 % | 19 ms |
| IDT (V2) | 0 ms | 95 % | 114 ms |
| Shortest RS | 0 ms | 91 % | 68 ms |
| MDI | 0.000 | 93 % | 0.24 |
| q in lead I | | 20 of 432 calls change (4.6 %) | |

**Depth effect** (LV free wall, 90 % minus 10 % depth, median of the 10 pairs per heart; v5.1 vs sensitivity):

| Measure | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| Pseudo-delta (ms) | 15.0 vs 15.0 | 27.0 vs 27.5 | 19.5 vs 20.0 |
| MDI | 0.098 vs 0.101 | 0.129 vs 0.125 | 0.096 vs 0.095 |
| QRS (ms) | 10.5 vs 11.0 | 24.5 vs 24.5 | 17.0 vs 18.5 |
| IDT (ms) | -12.5 vs -46.5 | 23.5 vs 23.5 | 15.0 vs 14.5 |
| Shortest RS (ms) | -1.0 vs -8.5 | 8.5 vs 8.5 | -5.5 vs -5.5 |

**Reading:**
- Measured: pseudo-delta, MDI and QRS duration, and their depth effects, barely move. IDT and shortest RS mostly don't
  move either, but a few beats jump by 40-114 ms, and in the control heart the IDT depth effect changes from -12.5 to
  -46.5 ms. The q call in lead I changes in 1 beat in 22.
- Inferred: the jumps are which-peak-is-picked swaps, as in the monodomain check and the 10 Oct conductor note. So IDT,
  shortest RS and the q call in lead I are sensitive to the heart's conductivities; pseudo-delta and MDI are not.

Files: `tableA51.md`/`.json`, `rescore/per_site.csv` (2.3 MB, not committed), `ecg_sens51.json`,
`leadfield_sens_<H>.json`, `weights_sens_<H>.json`. Runs: runs/v51_2026-10-15/10_conductor_sens/.
