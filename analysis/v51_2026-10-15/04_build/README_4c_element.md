# Step 4.3, continued 18 Oct 2026: element-wise speed tensors, and the unrun 7D98EVAR openCARP sites (STOP 4b again)

PC clock 2026-10-18 14:20-14:45 CEST (UTC 12:20-12:45). Alex 18 Oct 12:03:13 UTC "go" on the coordinator's post, carrying
Alex's decisions of 17 Oct 07:58 UTC ("Adopt all"): test element-wise tensors first (slab recalibration, acceptance A,
comparison with the saved openCARP fields; no new openCARP runs for that); run the 10 unrun 7D98EVAR sites under the
20-minute cap guard; retry the hung site once with a raised dream.fim.max_iter. If acceptance C still fails: keep the
graph solver, report its measured error, and let the 27-site monodomain check judge accuracy.

## Element-wise metric (graph51.METRIC_ELEMENT = 'element-1'; LABNOTES deviation entry written before any result)

- Each element keeps its own speed tensor; no nodal averaging.
- Tet edge (E1): the minimum over the tets sharing the edge of sqrt(d^T M_e d).
- 2-ring pair (E2): the sum over the segment's three thirds of the travel time in the tet holding each third's centre.
- Stencil, speeds and the single Dijkstra pass are unchanged. Edge data are cached as runs/v51_2026-10-15/cache51/qe_<H>_*.npz
  (145-187 s and 2.1-2.3 GB per heart; 0.06-0.07 % of the E2 sample points lay in no tet, so the nearest tet was used).

## Slab recalibration and acceptance A: PASS

The factors equal the nodal slab factors to 1e-8, as expected with uniform fibres
(params/v51_graph_factors_element.json, solver51_slab_calibration_element.json).
- Control: principal 0.9992 / 0.9997 / 0.9998, worst ray bin 1.34 %, rotating wall 0.982-0.983.
- HF: 1.0011 / 0.9988 / 1.0006, rays 1.83 %, rotating wall 0.988-0.989.

## Acceptance C: FAILS with both metrics

| Heart | Sites passing, nodal (17 Oct factors) | Sites passing, element-wise |
|---|---|---|
| Y5HYEDL4 | 4 / 12 | 0 / 12 |
| 6G8DD8S5 | 0 / 12 | 0 / 12 |
| 7D98EVAR | 0 / 3 | 0 / 3 |

- **Element-wise speeds:** the local speeds now match openCARP. Control fibre speed is 0.583-0.586 vs 0.584-0.586 m/s, with
  sheet and normal speeds within about 1 %. In the HF hearts the fibre speed is 0.559-0.566 vs 0.575-0.579 m/s (nodal:
  0.516-0.556).
- **Element-wise arrival times:** arrival is systematically early. The graph minus openCARP is -2.5 to -3.3 ms in the control
  heart (totals 2-2.4 % short) and -4.8 to -6.2 ms in the HF hearts (totals 3-5 % short).
- **Nodal arrival times:** the nodal metric scatters around zero in the control heart (-1.0 to +1.0 ms; totals within 1 %).
  In the HF hearts it ranges from -1.9 to +6.6 ms, worst at the outflow and cusp sites.
- **Reading (inference, not verified):** taking the fastest tet on every edge lets graph paths gain a little on each step
  where the fibres rotate. Nodal averaging loses on each step instead. openCARP lies between the two.
- Nothing was fitted to openCARP, and no region-specific factors were added.

Per site (nodal values for Y5HYEDL4 and 6G8DD8S5 from the 17 Oct acceptance_c.json; the rest computed 18 Oct):

| Heart | Site | median \|dt\| ms nodal / element | p95 % of total nodal / element | total ratio nodal / element | mean dt graph - openCARP ms nodal / element | fibre speed openCARP / nodal / element m/s |
|---|---|---|---|---|---|---|
| Y5HYEDL4 | lv_free_wall_phi180_z0.5_d10 | 1.28 / 2.90 | 0.93 / 2.00 | 0.9987 / 0.9810 | -0.97 / -2.89 | 0.585 / 0.575 / 0.584 |
| Y5HYEDL4 | lv_free_wall_phi180_z0.5_d90 | 1.15 / 3.11 | 0.97 / 2.03 | 0.9984 / 0.9791 | -0.97 / -3.11 | 0.585 / 0.577 / 0.585 |
| Y5HYEDL4 | lv_septum_phi0_z0.5_d50 | 1.18 / 2.74 | 1.30 / 2.27 | 1.0036 / 0.9792 | -0.27 / -2.76 | 0.585 / 0.569 / 0.584 |
| Y5HYEDL4 | lv_septum_phi0_z0.25_d50 | 1.19 / 2.45 | 2.12 / 2.18 | 0.9942 / 0.9766 | +0.46 / -2.50 | 0.585 / 0.569 / 0.583 |
| Y5HYEDL4 | rv_free_wall_q50_z0.5_d10 | 0.69 / 3.32 | 1.03 / 2.02 | 1.0031 / 0.9783 | +0.41 / -3.24 | 0.585 / 0.565 / 0.583 |
| Y5HYEDL4 | rv_free_wall_q50_z0.5_d90 | 0.70 / 3.48 | 0.90 / 2.02 | 1.0039 / 0.9780 | +0.19 / -3.31 | 0.585 / 0.567 / 0.583 |
| Y5HYEDL4 | rvot_septal_z_d50 | 0.90 / 3.16 | 1.48 / 2.33 | 1.0019 / 0.9838 | +0.25 / -3.11 | 0.586 / 0.569 / 0.585 |
| Y5HYEDL4 | rvot_free_wall_z_d50 | 0.75 / 3.09 | 0.88 / 2.22 | 1.0001 / 0.9790 | +0.19 / -3.14 | 0.585 / 0.572 / 0.586 |
| Y5HYEDL4 | aortic_cusp_rcc_z_d50 | 1.23 / 2.85 | 2.24 / 2.34 | 1.0051 / 0.9851 | +0.95 / -2.93 | 0.584 / 0.566 / 0.584 |
| Y5HYEDL4 | aortic_cusp_lcc_z_d50 | 1.43 / 2.70 | 1.49 / 1.96 | 1.0099 / 0.9839 | +0.64 / -2.87 | 0.586 / 0.573 / 0.585 |
| Y5HYEDL4 | lv_summit_superior_z_d50 | 1.48 / 3.11 | 1.19 / 2.16 | 0.9964 / 0.9759 | -0.73 / -3.19 | 0.586 / 0.571 / 0.583 |
| Y5HYEDL4 | lv_summit_inferior_lateral_z_d50 | 1.44 / 3.15 | 1.15 / 2.03 | 0.9971 / 0.9756 | -0.72 / -3.20 | 0.586 / 0.574 / 0.584 |
| 6G8DD8S5 | lv_free_wall_phi180_z0.5_d10 | 2.28 / 5.19 | 1.87 / 3.43 | 1.0175 / 0.9606 | -1.70 / -5.41 | 0.576 / 0.549 / 0.559 |
| 6G8DD8S5 | lv_free_wall_phi180_z0.5_d90 | 2.19 / 5.63 | 1.76 / 3.52 | 1.0127 / 0.9642 | -1.89 / -5.82 | 0.577 / 0.556 / 0.565 |
| 6G8DD8S5 | lv_septum_phi0_z0.5_d50 | 1.52 / 5.47 | 2.30 / 3.90 | 0.9937 / 0.9601 | +0.07 / -5.41 | 0.575 / 0.525 / 0.561 |
| 6G8DD8S5 | lv_septum_phi0_z0.25_d50 | 2.18 / 4.93 | 2.36 / 3.83 | 1.0092 / 0.9641 | +0.35 / -4.93 | 0.579 / 0.532 / 0.563 |
| 6G8DD8S5 | rv_free_wall_q50_z0.5_d10 | 1.53 / 6.10 | 1.76 / 3.60 | 1.0023 / 0.9607 | +1.67 / -6.08 | 0.579 / 0.528 / 0.566 |
| 6G8DD8S5 | rv_free_wall_q50_z0.5_d90 | 1.43 / 6.40 | 1.52 / 3.53 | 1.0015 / 0.9612 | +0.78 / -6.23 | 0.579 / 0.529 / 0.566 |
| 6G8DD8S5 | rvot_septal_z_d50 | 3.53 / 5.17 | 5.10 / 3.68 | 1.0131 / 0.9652 | +4.37 / -5.08 | 0.578 / 0.519 / 0.562 |
| 6G8DD8S5 | rvot_free_wall_z_d50 | 1.07 / 5.48 | 1.77 / 3.55 | 0.9953 / 0.9615 | +0.67 / -5.49 | 0.577 / 0.529 / 0.562 |
| 6G8DD8S5 | aortic_cusp_rcc_z_d50 | 5.73 / 5.17 | 7.20 / 3.55 | 1.0269 / 0.9659 | +6.57 / -5.28 | 0.578 / 0.516 / 0.559 |
| 6G8DD8S5 | aortic_cusp_lcc_z_d50 | 2.88 / 4.85 | 5.36 / 3.69 | 0.9962 / 0.9700 | +3.62 / -4.97 | 0.576 / 0.525 / 0.560 |
| 6G8DD8S5 | lv_summit_superior_z_d50 | 1.83 / 5.26 | 3.44 / 4.17 | 0.9825 / 0.9636 | +0.45 / -5.25 | 0.577 / 0.527 / 0.559 |
| 6G8DD8S5 | lv_summit_inferior_lateral_z_d50 | 2.27 / 5.86 | 3.91 / 4.14 | 1.0107 / 0.9580 | +0.21 / -5.83 | 0.577 / 0.538 / 0.561 |
| 7D98EVAR | lv_free_wall_phi180_z0.5_d10 | 2.06 / 5.67 | 1.74 / 3.70 | 1.0125 / 0.9677 | -1.29 / -5.80 | 0.576 / 0.545 / 0.560 |
| 7D98EVAR | lv_free_wall_phi180_z0.5_d90 | hit the 20-minute cap | | | | |
| 7D98EVAR | lv_septum_phi0_z0.5_d50 | 1.80 / 5.17 | 3.55 / 4.29 | 1.0185 / 0.9531 | +1.88 / -5.35 | 0.576 / 0.524 / 0.563 |
| 7D98EVAR | lv_septum_phi0_z0.25_d50 | 2.59 / 4.66 | 3.19 / 3.78 | 1.0150 / 0.9574 | +2.17 / -4.78 | 0.577 / 0.528 / 0.563 |
| 7D98EVAR | rv_free_wall_q50_z0.5_d10 | hit the 20-minute cap | | | | |
| 7D98EVAR | rv_free_wall_q50_z0.5_d90 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rvot_septal_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | rvot_free_wall_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | aortic_cusp_rcc_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | aortic_cusp_lcc_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | lv_summit_superior_z_d50 | not run (batch stopped earlier) | | | | |
| 7D98EVAR | lv_summit_inferior_lateral_z_d50 | not run (batch stopped earlier) | | | | |

Files: acceptance_c_element_2026-10-18_Y5HYEDL4_6G8DD8S5.json, acceptance_c_element_2026-10-18_7D98EVAR.json,
acceptance_c_nodal_2026-10-18_7D98EVAR.json (the 17 Oct acceptance_c.json is unchanged).

## 7D98EVAR openCARP runs: STOPPED at the 20-minute cap again

- lv_septum_phi0_z0.5_d50: 64.6 s. lv_septum_phi0_z0.25_d50: 69.0 s. Neither had unactivated nodes.
- rv_free_wall_q50_z0.5_d10 hit the 20-minute cap with the same signature as lv_free_wall_phi180_z0.5_d90 on 17 Oct:
  - one core busy;
  - no progress past t = 0;
  - empty act.igb and eik_stats.dat.

  A finished run converges in about 106 FIM iterations (57 s). The same site ran normally in the other two hearts.
- The batch stopped, as instructed. The retry of lv_free_wall_phi180_z0.5_d90 was not run, because the script refuses
  retries after a new cap. 7 sites remain unrun.
- dream.fim.max_iter was already 1e9 in every run (openCARP's default is 50). A "raised" value can only go to 2147483647,
  the largest the int parameter takes, so a retry mainly tests whether the hang repeats.

Status: runs/v51_2026-10-15/04_build/7D98EVAR/acceptance_c/status.json; log batch_2026-10-18.log there.

## Decisions for Alex

1. **Graph solver metric.** Both metrics fail C, so per Alex's 17 Oct rule the graph solver stays and its error is reported.
   Which metric goes forward?
   - The nodal metric, as briefed: arrival times are closer to openCARP.
   - The element-wise metric: local speeds are closer, but arrivals are 2-6 % early.
2. **The remaining 7D98EVAR openCARP sites.** Options:
   - Run the remaining 7 with a shorter per-run limit.
   - Stop here, with 3 of 12 compared in 7D98EVAR.
   - Keep the 20-minute cap and the retry.

v5 files unchanged: yes (check_v5_files.py: 3,484 manifest files, size and mtime; no tracked change in the protected folders).
