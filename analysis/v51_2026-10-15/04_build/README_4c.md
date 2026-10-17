# Step 4.3: acceptance C (openCARP eikonal reference) and S13, stopped at a 20-minute cap

PC clock 2026-10-17 08:23-09:17 CEST (UTC 06:23-07:17). Alex (06:20:06 UTC): "Go for acceptance C and S13. Stop and tell me
if any openCARP run hits the 20-minute cap."

## Setup

- openCARP v20 (ffce195), pure eikonal: -dream.solve 0, FIM, tol 0.001, max_iter 1e9, 6 OpenMP threads.
- v5.1 speeds without graph factors; v5.1 fibres; mesh bivF (same tets as biv.elem).
- Single-node stimulus, tissue only.
- Graph: graph51 with the slab-calibrated factors.
- Script: acceptance_c.py. Results: acceptance_c.json.

Gates per site: median |dt| ≤ 1 ms; p95 |dt| ≤ 2 % of total activation; total within ±2 %; no −1.

## Outcome

- Y5HYEDL4: 12 / 12 runs (64-184 s each).
- 6G8DD8S5: 12 / 12 runs (70-98 s each).
- 7D98EVAR: lv_free_wall_phi180_z0.5_d10 ran (73 s). lv_free_wall_phi180_z0.5_d90 **hit the 20-minute cap**: openCARP
  never left t = 0 (empty act.igb, empty eik_stats.dat; ~1 core busy). This is the FIM non-convergence already seen on
  8 Oct, not a slow run. The batch stopped as instructed; the remaining 10 7D98EVAR sites were not run.
- No −1 (unactivated) node in any finished run.

Sites passing: Y5HYEDL4 4 / 12, 6G8DD8S5 0 / 12, 7D98EVAR 0 / 1 compared.

| Heart | Site | median \|dt\| ms | p95 % of total | total graph / openCARP | mean dt graph − openCARP ms | F01 fibre speed openCARP / graph m/s | Result |
|---|---|---|---|---|---|---|---|
| Y5HYEDL4 | lv_free_wall_phi180_z0.5_d10 | 1.28 | 0.93 | 0.9987 | -0.97 | 0.585 / 0.575 | FAIL |
| Y5HYEDL4 | lv_free_wall_phi180_z0.5_d90 | 1.15 | 0.97 | 0.9984 | -0.97 | 0.585 / 0.577 | FAIL |
| Y5HYEDL4 | lv_septum_phi0_z0.5_d50 | 1.18 | 1.30 | 1.0036 | -0.27 | 0.585 / 0.569 | FAIL |
| Y5HYEDL4 | lv_septum_phi0_z0.25_d50 | 1.19 | 2.12 | 0.9942 | +0.46 | 0.585 / 0.569 | FAIL |
| Y5HYEDL4 | rv_free_wall_q50_z0.5_d10 | 0.69 | 1.03 | 1.0031 | +0.41 | 0.585 / 0.565 | PASS |
| Y5HYEDL4 | rv_free_wall_q50_z0.5_d90 | 0.70 | 0.90 | 1.0039 | +0.19 | 0.585 / 0.567 | PASS |
| Y5HYEDL4 | rvot_septal_z_d50 | 0.90 | 1.48 | 1.0019 | +0.25 | 0.586 / 0.569 | PASS |
| Y5HYEDL4 | rvot_free_wall_z_d50 | 0.75 | 0.88 | 1.0001 | +0.19 | 0.585 / 0.572 | PASS |
| Y5HYEDL4 | aortic_cusp_rcc_z_d50 | 1.23 | 2.24 | 1.0051 | +0.95 | 0.584 / 0.566 | FAIL |
| Y5HYEDL4 | aortic_cusp_lcc_z_d50 | 1.43 | 1.49 | 1.0099 | +0.64 | 0.586 / 0.573 | FAIL |
| Y5HYEDL4 | lv_summit_superior_z_d50 | 1.48 | 1.19 | 0.9964 | -0.73 | 0.586 / 0.571 | FAIL |
| Y5HYEDL4 | lv_summit_inferior_lateral_z_d50 | 1.44 | 1.15 | 0.9971 | -0.72 | 0.586 / 0.574 | FAIL |
| 6G8DD8S5 | lv_free_wall_phi180_z0.5_d10 | 2.28 | 1.87 | 1.0175 | -1.70 | 0.576 / 0.549 | FAIL |
| 6G8DD8S5 | lv_free_wall_phi180_z0.5_d90 | 2.19 | 1.76 | 1.0127 | -1.89 | 0.577 / 0.556 | FAIL |
| 6G8DD8S5 | lv_septum_phi0_z0.5_d50 | 1.52 | 2.30 | 0.9937 | +0.07 | 0.575 / 0.525 | FAIL |
| 6G8DD8S5 | lv_septum_phi0_z0.25_d50 | 2.18 | 2.36 | 1.0092 | +0.35 | 0.579 / 0.532 | FAIL |
| 6G8DD8S5 | rv_free_wall_q50_z0.5_d10 | 1.53 | 1.76 | 1.0023 | +1.67 | 0.579 / 0.528 | FAIL |
| 6G8DD8S5 | rv_free_wall_q50_z0.5_d90 | 1.43 | 1.52 | 1.0015 | +0.78 | 0.579 / 0.529 | FAIL |
| 6G8DD8S5 | rvot_septal_z_d50 | 3.53 | 5.10 | 1.0131 | +4.37 | 0.578 / 0.519 | FAIL |
| 6G8DD8S5 | rvot_free_wall_z_d50 | 1.07 | 1.77 | 0.9953 | +0.67 | 0.577 / 0.529 | FAIL |
| 6G8DD8S5 | aortic_cusp_rcc_z_d50 | 5.73 | 7.20 | 1.0269 | +6.57 | 0.578 / 0.516 | FAIL |
| 6G8DD8S5 | aortic_cusp_lcc_z_d50 | 2.88 | 5.36 | 0.9962 | +3.62 | 0.576 / 0.525 | FAIL |
| 6G8DD8S5 | lv_summit_superior_z_d50 | 1.83 | 3.44 | 0.9825 | +0.45 | 0.577 / 0.527 | FAIL |
| 6G8DD8S5 | lv_summit_inferior_lateral_z_d50 | 2.27 | 3.91 | 1.0107 | +0.21 | 0.577 / 0.538 | FAIL |
| 7D98EVAR | lv_free_wall_phi180_z0.5_d10 | 2.06 | 1.74 | 1.0125 | -1.29 | 0.576 / 0.545 | FAIL |
| 7D98EVAR | lv_free_wall_phi180_z0.5_d90 | hit the 20-minute cap | | | | |
| 7D98EVAR | lv_septum_phi0_z0.5_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | lv_septum_phi0_z0.25_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rv_free_wall_q50_z0.5_d10 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rv_free_wall_q50_z0.5_d90 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rvot_septal_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rvot_free_wall_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | aortic_cusp_rcc_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | aortic_cusp_lcc_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | lv_summit_superior_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | lv_summit_inferior_lateral_z_d50 | not run (batch stopped earlier) | | | | |

## Reading

**Control heart:** close but strict. Totals agree within 1 %. The mean signed difference is −0.97 to +0.95 ms on totals
of 210-280 ms, and the median |dt| is 0.69-1.48 ms. 8 sites miss the 1 ms median gate by up to 0.5 ms, and 2 also miss
the 2 % p95 gate (2.12 %, 2.24 %).

**Heart-failure heart 6G8DD8S5:** fails everywhere. Median |dt| is 1.1-2.3 ms at most sites and 2.9-5.7 ms at the
outflow and cusp sites (RCC: p95 7.2 %, total +2.7 %).

**Likely cause** (inference, not verified):
- The F01 measure reads openCARP's own field at about 0.577 m/s along the fibre at every site, but the graph's at
  0.52-0.56. In the real heart the graph conducts more slowly along the fibre than openCARP.
- On the uniform-fibre slab they agreed, so the gap comes from rotating, curved fibres. The brief's nodal metric
  averaging (S3) mixes fibre and cross-fibre directions where fibres rotate, and the HF anisotropy (2.3 : 1) amplifies it.
- Per brief S11, no region-specific factors were added. Nothing was retuned.

## S13 (report only)

Slab factors at the v5 speeds, with the v5.1 stencil and the v5 fibres, measured as the audit's F01 (a03) at
lv_free_wall_phi180_z0.5_d50:
- Control: 0.588 / 0.484 / 0.491 m/s (v5 solver 0.564 / 0.489 / 0.485; targets 0.60 / 0.48 / 0.48).
- HF: 0.569 / 0.360 / 0.349 and 0.568 / 0.363 / 0.352 (v5 0.50 / 0.36 / 0.35; targets 0.60 / 0.3504 / 0.336).

Results in solver51_s13.json.

## Open (decisions for Alex)

1. The hung 7D98EVAR run, and whether to run the 10 remaining 7D98EVAR sites. Options: rerun with another FIM
   tolerance or thread count, a different cap, or leave them.
2. What to do about acceptance C failing. The brief's named fallbacks are a 3-ring stencil and openCARP for tissue-only
   fields. Two other routes: element-wise rather than nodal-averaged metric (a change to the S3 rule), or fitting the
   factors to openCARP fields. Nothing has been changed.
