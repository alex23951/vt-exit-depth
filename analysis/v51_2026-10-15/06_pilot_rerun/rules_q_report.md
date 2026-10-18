# Step 2.5: ecg_depth_criteria 0.3.0 vs 0.4.0 on the saved v5 beats (read-only)

Input runs/v51_2026-10-15/06_pilot_rerun/rules/per_measurement.csv (sha256 bd58cb980db5f27e...). Rules: 030; primary (N 40 ms + CSE); sensitivities N20, window_only, no_window, wave010.

## Gate 5: Bazan 2007 region Q (13 Oct rule: pooled positions, 90 % vs 10 %, Newcombe 95 % CI vs Bazan difference)

| condition | rule | basal superior q in I | basal superior no inferior Q | apical superior q in I | basal inferior Q | apical inferior Q |
|---|---|---|---|---|---|---|
| true mode (13 Oct) | 030 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | primary | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | N20 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | window_only | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | no_window | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| true mode (13 Oct) | wave010 | 3/21 vs 2/21, +5 (-17 to +26): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 2/9 vs 0/9, +22 (-12 to +55): not evaluable (< 20 positions) | 5/8 vs 0/8, +62 (+17 to +86): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | 030 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | primary | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | N20 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | window_only | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | no_window | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 11/21 vs 6/21, +24 (-6 to +48): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | wave010 | 3/21 vs 2/21, +5 (-17 to +26): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 2/9 vs 0/9, +22 (-12 to +55): not evaluable (< 20 positions) | 5/8 vs 0/8, +62 (+17 to +86): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | 030 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 10/21 vs 6/21, +19 (-10 to +44): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | primary | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 17/21 vs 6/21, +52 (+22 to +71): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |

## Changed q / initial-r calls, 0.3.0 -> 0.4.0 primary (clean ECG; per site and mode; details in q_changes.csv)

- true / q_lead_I: 62 (62 lost, 0 new)
- true / inferior_q_all: 45 (45 lost, 0 new)
- true / inferior_q_any: 64 (64 lost, 0 new)
- true / inferior_r_any: 55 (55 lost, 0 new)
- true / q_V1: 33 (33 lost, 0 new)
- true / q_V2: 27 (27 lost, 0 new)
- true / qs_V2: 2 (2 lost, 0 new)
- stim / q_lead_I: 62 (62 lost, 0 new)
- stim / inferior_q_all: 45 (45 lost, 0 new)
- stim / inferior_q_any: 64 (64 lost, 0 new)
- stim / inferior_r_any: 55 (55 lost, 0 new)
- stim / q_V1: 33 (33 lost, 0 new)
- stim / q_V2: 27 (27 lost, 0 new)
- stim / qs_V2: 2 (2 lost, 0 new)
- detected / q_lead_I: 62 (62 lost, 0 new)
- detected / inferior_q_all: 45 (45 lost, 0 new)
- detected / inferior_q_any: 64 (64 lost, 0 new)
- detected / inferior_r_any: 55 (55 lost, 0 new)
- detected / q_V1: 33 (33 lost, 0 new)
- detected / q_V2: 27 (27 lost, 0 new)
- detected / qs_V2: 2 (2 lost, 0 new)

Causes (lead level; window = first 0.05 mV wave after 40 ms; recognition = CSE step):

- 747 x window: first 0.05 mV wave (s) starts N ms after the visible onset (> 40)
- 405 x recognition: an earlier + deflection (>= threshold for >= N ms, from N ms) comes first
- 222 x recognition: an earlier - deflection (>= threshold for >= N ms, from N ms) comes first
- 6 x recognition: the first deflection turns back before reaching 0.05 mV

## Summit / cusp sites with a changed Q ratio aVL/aVR, R/S V1 or Santangeli no-q-V1

- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 4.730071090951421 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 3.983482967272881 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 4.7401762644397 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 3.452202247857816 -> 0.0
- true | Y5HYEDL4 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.13045343861682498 -> inf
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.6490554777325384 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | rs_ratio_v1: 0.0 -> nan
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 0.6836229085623575 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | rs_ratio_v1: 0.0 -> nan
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.6697826732319525 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | rs_ratio_v1: 0.0 -> nan
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 0.719314946669622 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | rs_ratio_v1: 0.0 -> nan
- true | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | santangeli2015_no_q_v1: False -> True
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 3.0297777352274173 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 2.991378069734684 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 2.9398821793962866 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 2.8929913522943407 -> 0.0
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 2.854034650553405 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 2.7449955476552064 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 2.7226767452974556 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 4.069410669094593 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 3.8435733429561205 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 3.7831722170761175 -> inf
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- true | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08573503844992736 -> 1.5190478084895866
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
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 4.730071090951421 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 3.983482967272881 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 4.7401762644397 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 3.452202247857816 -> 0.0
- stim | Y5HYEDL4 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.13045343861682498 -> inf
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.6490554777325384 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | rs_ratio_v1: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 0.6836229085623575 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | rs_ratio_v1: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.6697826732319525 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | rs_ratio_v1: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 0.719314946669622 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | rs_ratio_v1: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | santangeli2015_no_q_v1: False -> True
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 3.0297777352274173 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 2.991378069734684 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 2.9398821793962866 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 2.8929913522943407 -> 0.0
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 2.854034650553405 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 2.7449955476552064 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 2.7226767452974556 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 4.069410669094593 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 3.8435733429561205 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 3.7831722170761175 -> inf
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08573503844992736 -> 1.5190478084895866
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
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 4.730071090951421 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 3.983482967272881 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 4.7401762644397 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 3.452202247857816 -> 0.0
- detected | Y5HYEDL4 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.13045343861682498 -> inf
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: 0.6490554777325384 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | rs_ratio_v1: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d10 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: 0.6836229085623575 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | rs_ratio_v1: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d50 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: 0.6697826732319525 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | rs_ratio_v1: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d75 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: 0.719314946669622 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | rs_ratio_v1: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | aortic_cusp_rcc_z_d90 | santangeli2015_no_q_v1: False -> True
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 3.0297777352274173 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 2.991378069734684 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 2.9398821793962866 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 2.8929913522943407 -> 0.0
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d50 | q_ratio_avl_avr: 2.854034650553405 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d75 | q_ratio_avl_avr: 2.7449955476552064 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_superior_z_d90 | q_ratio_avl_avr: 2.7226767452974556 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 4.069410669094593 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 3.8435733429561205 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 3.7831722170761175 -> inf
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.08573503844992736 -> 1.5190478084895866
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
| true | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| true | window_only | 132 | 101 | 83 | 164 | 104 | 93 | 49 | 30 | 66 | 79 | 92 | 114 |
| true | N20 | 255 | 263 | 195 | 308 | 207 | 240 | 177 | 134 | 225 | 233 | 240 | 253 |
| true | primary | 123 | 115 | 118 | 151 | 110 | 121 | 78 | 68 | 103 | 117 | 108 | 129 |
| stim | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stim | window_only | 132 | 101 | 83 | 164 | 104 | 93 | 49 | 30 | 66 | 79 | 92 | 114 |
| stim | N20 | 255 | 263 | 195 | 308 | 207 | 240 | 177 | 134 | 225 | 233 | 240 | 253 |
| stim | primary | 123 | 115 | 118 | 151 | 110 | 121 | 78 | 68 | 103 | 117 | 108 | 129 |
| detected | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| detected | window_only | 132 | 101 | 83 | 164 | 104 | 93 | 49 | 30 | 66 | 79 | 92 | 114 |
| detected | N20 | 255 | 263 | 195 | 308 | 207 | 240 | 177 | 134 | 225 | 233 | 240 | 253 |
| detected | primary | 123 | 115 | 118 | 151 | 110 | 121 | 78 | 68 | 103 | 117 | 108 | 129 |

## initial_start_ms and visible onset - stimulus: see gates_040.json (per heart and region / family and depth)

