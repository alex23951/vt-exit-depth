# Step 2.5: ecg_depth_criteria 0.3.0 vs 0.4.0 on the saved v5 beats (read-only)

Input runs/v51_2026-10-15/10_conductor_sens/rules/per_measurement.csv (sha256 4a025825c524c960...). Rules: 030; primary (N 40 ms + CSE); sensitivities N20, window_only, no_window, wave010.

## Gate 5: Bazan 2007 region Q (13 Oct rule: pooled positions, 90 % vs 10 %, Newcombe 95 % CI vs Bazan difference)

| condition | rule | basal superior q in I | basal superior no inferior Q | apical superior q in I | basal inferior Q | apical inferior Q |
|---|---|---|---|---|---|---|
| true mode (13 Oct) | 030 | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | primary | 6/21 vs 3/21, +14 (-11 to +38): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | N20 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | window_only | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | no_window | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | wave010 | 4/21 vs 2/21, +10 (-13 to +32): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 3/9 vs 0/9, +33 (-3 to +65): not evaluable (< 20 positions) | 7/8 vs 0/8, +88 (+40 to +98): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | 030 | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | primary | 6/21 vs 3/21, +14 (-11 to +38): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | N20 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | window_only | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | no_window | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | wave010 | 4/21 vs 2/21, +10 (-13 to +32): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 3/9 vs 0/9, +33 (-3 to +65): not evaluable (< 20 positions) | 7/8 vs 0/8, +88 (+40 to +98): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | 030 | 7/21 vs 3/21, +19 (-7 to +42): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | primary | 6/21 vs 3/21, +14 (-11 to +38): FAIL (Bazan outside CI) | 16/21 vs 6/21, +48 (+17 to +67): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |

## Changed q / initial-r calls, 0.3.0 -> 0.4.0 primary (clean ECG; per site and mode; details in q_changes.csv)

- true / q_lead_I: 49 (49 lost, 0 new)
- true / inferior_q_all: 38 (38 lost, 0 new)
- true / inferior_q_any: 46 (46 lost, 0 new)
- true / inferior_r_any: 57 (57 lost, 0 new)
- true / q_V1: 34 (34 lost, 0 new)
- true / q_V2: 38 (38 lost, 0 new)
- true / qs_V2: 7 (7 lost, 0 new)
- stim / q_lead_I: 49 (49 lost, 0 new)
- stim / inferior_q_all: 38 (38 lost, 0 new)
- stim / inferior_q_any: 46 (46 lost, 0 new)
- stim / inferior_r_any: 57 (57 lost, 0 new)
- stim / q_V1: 34 (34 lost, 0 new)
- stim / q_V2: 38 (38 lost, 0 new)
- stim / qs_V2: 7 (7 lost, 0 new)
- detected / q_lead_I: 49 (49 lost, 0 new)
- detected / inferior_q_all: 38 (38 lost, 0 new)
- detected / inferior_q_any: 46 (46 lost, 0 new)
- detected / inferior_r_any: 57 (57 lost, 0 new)
- detected / q_V1: 34 (34 lost, 0 new)
- detected / q_V2: 38 (38 lost, 0 new)
- detected / qs_V2: 7 (7 lost, 0 new)

Causes (lead level; window = first 0.05 mV wave after 40 ms; recognition = CSE step):

- 633 x window: first 0.05 mV wave (s) starts N ms after the visible onset (> 40)
- 396 x recognition: an earlier + deflection (>= threshold for >= N ms, from N ms) comes first
- 189 x recognition: an earlier - deflection (>= threshold for >= N ms, from N ms) comes first

## Summit / cusp sites with a changed Q ratio aVL/aVR, R/S V1 or Santangeli no-q-V1

- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 7.067777727390593 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 6.001931460813442 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 7.143352927230327 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 5.1348421917450455 -> 0.0
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.09624660906799624 -> inf
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.9572471889433322 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 1.0068106326971484 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.9927696019623088 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 1.068450582754399 -> 0.0
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 3.4706842033987093 -> nan
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 3.291335149037932 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 3.299659742797325 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- true | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08456006320279434 -> inf
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 7.067777727390593 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 6.001931460813442 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 7.143352927230327 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 5.1348421917450455 -> 0.0
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.09624660906799624 -> inf
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.9572471889433322 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 1.0068106326971484 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.9927696019623088 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 1.068450582754399 -> 0.0
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 3.4706842033987093 -> nan
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 3.291335149037932 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 3.299659742797325 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08456006320279434 -> inf
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 7.067777727390593 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 6.001931460813442 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 7.143352927230327 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 5.1348421917450455 -> 0.0
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.09624660906799624 -> inf
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.9572471889433322 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 1.0068106326971484 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.9927696019623088 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 1.068450582754399 -> 0.0
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 3.4706842033987093 -> nan
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 3.291335149037932 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 3.299659742797325 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08456006320279434 -> inf
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan

## Leads with polarity 0 (neither), clean ECG, 579 beats per cell

| mode / rule | I | II | III | aVR | aVL | aVF | V1 | V2 | V3 | V4 | V5 | V6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | 030 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| true | window_only | 113 | 100 | 75 | 147 | 97 | 83 | 40 | 26 | 67 | 72 | 82 | 101 |
| true | N20 | 233 | 253 | 182 | 289 | 205 | 231 | 162 | 123 | 226 | 225 | 235 | 239 |
| true | primary | 111 | 105 | 106 | 136 | 110 | 113 | 81 | 73 | 99 | 102 | 98 | 108 |
| stim | 030 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stim | window_only | 113 | 100 | 75 | 147 | 97 | 83 | 40 | 26 | 67 | 72 | 82 | 101 |
| stim | N20 | 233 | 253 | 182 | 289 | 205 | 231 | 162 | 123 | 226 | 225 | 235 | 239 |
| stim | primary | 111 | 105 | 106 | 136 | 110 | 113 | 81 | 73 | 99 | 102 | 98 | 108 |
| detected | 030 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| detected | window_only | 113 | 100 | 75 | 147 | 97 | 83 | 40 | 26 | 67 | 72 | 82 | 101 |
| detected | N20 | 233 | 253 | 182 | 289 | 205 | 231 | 162 | 123 | 226 | 225 | 235 | 239 |
| detected | primary | 111 | 105 | 106 | 136 | 110 | 113 | 81 | 73 | 99 | 102 | 98 | 108 |

## initial_start_ms and visible onset - stimulus: see gates_040.json (per heart and region / family and depth)

