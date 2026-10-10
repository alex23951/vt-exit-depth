# Purkinje network as the conduction model: setup on all three hearts (9 Oct 2026)

The study now uses the His-Purkinje network **v3** (the job-8 network) instead of the frozen fast endocardial layer,
on all three pilot hearts. Jobs 9 (6G8DD8S5) and 10 (7D98EVAR) are ready; Alex starts them with
`bash jobs/start_seq.sh 9 10` (~7 h on the PC). Details: LABNOTES.md, 9 Oct entries.

## Decisions (Alex, 9 Oct, project thread)
| Time (UTC) | Decision |
|---|---|
| 15:39 | "network": the network replaces the frozen fast layer (dated deviation in LABNOTES and the Model parameters tab) |
| 15:47 | LBBB-like heart 6G8DD8S5: proximal left-bundle cut, LV fascicles and Purkinje intact (Upadhyay 2019, doi 10.1161/CIRCULATIONAHA.118.038648) |
| 16:15 | "yes" to calibrating the distal network to Durrer's timing (v4), then, after the paced-QRS check below: |
| 16:38 | "v3": grids use the network as built for job 8; the normal-beat axis is a reported limitation; exploring a model that gets both right is future work |

## Why v3 and not v4 (control heart Y5HYEDL4)
| | v3 (2.0 m/s distal, up to 90 % apex-to-base) | v4 (distal calibrated to Durrer, to the base) |
|---|---|---|
| His-driven frontal axis | -92 deg | -27 deg |
| LV endocardium activated by 30 ms (Durrer: nearly all) | 48 % | 95 % |
| Latest activation after LV onset (Durrer 62-80 ms) | 104 ms | 72 ms |
| Summit + cusp paced QRS, median (normal-heart ectopy 147-175 ms) | 162 ms | 92 ms |

The superior axis of v3 is present in all three hearts (-92, -83, LBBB heart -55 deg). Torso placement is normal
(LV long axis +51 deg). Most of the superior pull comes from the base and outflow, activated last.

## Setup done today (PC)
- No-layer lead fields and ECG weights for 7D98EVAR and 6G8DD8S5; graph scale k 1.0682 / 1.0658 (control 1.0685).
- Networks v3: 5,294 / 5,120 nodes, 3,241 / 3,192 junctions; the control heart's rebuild is identical to job 8's.
- His-driven checks: 7D98EVAR axis -83 deg; 6G8DD8S5 (LBBB cut) RV first, LV 19 ms later, span 125 ms, axis -55 deg.
- Smoke test, LV free wall 10 % -> 90 % depth, true-onset QRS: 7D98EVAR 158 -> 171 ms, 6G8DD8S5 150 -> 170 ms
  (control heart 166 -> 181 ms); pseudo-delta 49 -> 62 / 41 -> 68 ms; IDT 77 -> 89 / 68 -> 88 ms.
