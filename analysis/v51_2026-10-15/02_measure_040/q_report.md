# Step 2.5: ecg_depth_criteria 0.3.0 vs 0.4.0 on the saved v5 beats (read-only)

Input runs/v51_2026-10-15/02_measure_040/per_measurement.csv (sha256 b56f5891cd92bf7f...). Rules: 030; primary (N 40 ms + CSE); sensitivities N20, window_only, no_window, wave010.

## Gate 5: Bazan 2007 region Q (13 Oct rule: pooled positions, 90 % vs 10 %, Newcombe 95 % CI vs Bazan difference)

| condition | rule | basal superior q in I | basal superior no inferior Q | apical superior q in I | basal inferior Q | apical inferior Q |
|---|---|---|---|---|---|---|
| true mode (13 Oct) | 030 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 12/21 vs 6/21, +29 (-1 to +52): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 2/9, +22 (-19 to +55): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| true mode (13 Oct) | primary | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| true mode (13 Oct) | N20 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| true mode (13 Oct) | window_only | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 14/21 vs 6/21, +38 (+8 to +60): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| true mode (13 Oct) | no_window | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 12/21 vs 6/21, +29 (-1 to +52): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 2/9, +22 (-19 to +55): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| true mode (13 Oct) | wave010 | 3/21 vs 0/21, +14 (-4 to +35): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 2/9 vs 0/9, +22 (-12 to +55): not evaluable (< 20 positions) | 5/8 vs 0/8, +62 (+17 to +86): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | 030 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 12/21 vs 6/21, +29 (-1 to +52): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 2/9, +22 (-19 to +55): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | primary | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | N20 | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | window_only | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 14/21 vs 6/21, +38 (+8 to +60): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 1/9, +33 (-8 to +64): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | no_window | 4/21 vs 3/21, +5 (-19 to +28): FAIL (Bazan outside CI) | 12/21 vs 6/21, +29 (-1 to +52): direction as Bazan (more at epi); no Bazan % to compare | 4/9 vs 2/9, +22 (-19 to +55): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| 14 Oct pace-map convention (stimulus onset, clean) | wave010 | 3/21 vs 0/21, +14 (-4 to +35): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 2/9 vs 0/9, +22 (-12 to +55): not evaluable (< 20 positions) | 5/8 vs 0/8, +62 (+17 to +86): not evaluable (< 20 positions) | 6/7 vs 0/7, +86 (+34 to +97): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | 030 | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 12/21 vs 6/21, +29 (-1 to +52): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 2/9, +33 (-10 to +63): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |
| stimulus onset, 10 uV noise (majority of 10 seeds) | primary | 5/21 vs 3/21, +10 (-15 to +33): FAIL (Bazan outside CI) | 18/21 vs 6/21, +57 (+28 to +75): direction as Bazan (more at epi); no Bazan % to compare | 5/9 vs 1/9, +44 (+1 to +72): not evaluable (< 20 positions) | 8/8 vs 0/8, +100 (+54 to +100): not evaluable (< 20 positions) | 7/7 vs 0/7, +100 (+50 to +100): not evaluable (< 20 positions) |

## Changed q / initial-r calls, 0.3.0 -> 0.4.0 primary (clean ECG; per site and mode; details in q_changes.csv)

- true / q_lead_I: 73 (73 lost, 0 new)
- true / inferior_q_all: 37 (37 lost, 0 new)
- true / inferior_q_any: 64 (64 lost, 0 new)
- true / inferior_r_any: 87 (87 lost, 0 new)
- true / q_V1: 32 (32 lost, 0 new)
- true / q_V2: 35 (35 lost, 0 new)
- true / qs_V2: 7 (7 lost, 0 new)
- stim / q_lead_I: 73 (73 lost, 0 new)
- stim / inferior_q_all: 37 (37 lost, 0 new)
- stim / inferior_q_any: 64 (64 lost, 0 new)
- stim / inferior_r_any: 87 (87 lost, 0 new)
- stim / q_V1: 32 (32 lost, 0 new)
- stim / q_V2: 35 (35 lost, 0 new)
- stim / qs_V2: 7 (7 lost, 0 new)
- detected / q_lead_I: 73 (73 lost, 0 new)
- detected / inferior_q_all: 37 (37 lost, 0 new)
- detected / inferior_q_any: 64 (64 lost, 0 new)
- detected / inferior_r_any: 87 (87 lost, 0 new)
- detected / q_V1: 32 (32 lost, 0 new)
- detected / q_V2: 35 (35 lost, 0 new)
- detected / qs_V2: 7 (7 lost, 0 new)

Causes (lead level; window = first 0.05 mV wave after 40 ms; recognition = CSE step):

- 1125 x window: first 0.05 mV wave (s) starts N ms after the visible onset (> 40)
- 315 x recognition: an earlier + deflection (>= threshold for >= N ms, from N ms) comes first
- 231 x recognition: an earlier - deflection (>= threshold for >= N ms, from N ms) comes first
- 6 x recognition: the first deflection turns back before reaching 0.05 mV

## Summit / cusp sites with a changed Q ratio aVL/aVR, R/S V1 or Santangeli no-q-V1

- true | Y5HYEDL4 | net | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.11980883456119612 -> inf
- true | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.1573892066153769 -> inf
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 1.682724227563142 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 1.7248800777289102 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 1.6311363479921313 -> 0.0
- true | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 1.6922096286368227 -> 0.0
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 2.5343316224379144 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 2.4178395347448562 -> inf
- true | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 2.4320625466148305 -> inf
- true | 6G8DD8S5 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 5.787594671590025 -> 0.0
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 5.9764916274448705 -> 0.0
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.5348102645622288 -> 0.0
- true | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.5416911632099317 -> 0.0
- true | 6G8DD8S5 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- true | 7D98EVAR | net | lv_summit_superior_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_superior_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- true | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.11980883456119612 -> inf
- stim | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.1573892066153769 -> inf
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 1.682724227563142 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 1.7248800777289102 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 1.6311363479921313 -> 0.0
- stim | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 1.6922096286368227 -> 0.0
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 2.5343316224379144 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 2.4178395347448562 -> inf
- stim | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 2.4320625466148305 -> inf
- stim | 6G8DD8S5 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 5.787594671590025 -> 0.0
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 5.9764916274448705 -> 0.0
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.5348102645622288 -> 0.0
- stim | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.5416911632099317 -> 0.0
- stim | 6G8DD8S5 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- stim | 7D98EVAR | net | lv_summit_superior_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_superior_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- stim | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_superior_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 0.11980883456119612 -> inf
- detected | Y5HYEDL4 | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.1573892066153769 -> inf
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 1.682724227563142 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 1.7248800777289102 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 1.6311363479921313 -> 0.0
- detected | Y5HYEDL4 | nonet | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 1.6922096286368227 -> 0.0
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d10 | q_ratio_avl_avr: 0.0 -> nan
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 2.5343316224379144 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d75 | q_ratio_avl_avr: 2.4178395347448562 -> inf
- detected | Y5HYEDL4 | nonet | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 2.4320625466148305 -> inf
- detected | 6G8DD8S5 | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d10 | q_ratio_avl_avr: 5.787594671590025 -> 0.0
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d50 | q_ratio_avl_avr: 5.9764916274448705 -> 0.0
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d75 | q_ratio_avl_avr: 0.5348102645622288 -> 0.0
- detected | 6G8DD8S5 | net | aortic_cusp_lcc_z_d90 | q_ratio_avl_avr: 0.5416911632099317 -> 0.0
- detected | 6G8DD8S5 | net | lv_summit_superior_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 6G8DD8S5 | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d10 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d50 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d75 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | aortic_cusp_rcc_z_d90 | q_ratio_avl_avr: inf -> nan
- detected | 7D98EVAR | net | lv_summit_superior_z_d75 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_superior_z_d90 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_inferior_lateral_z_d50 | q_ratio_avl_avr: 0.0 -> nan
- detected | 7D98EVAR | net | lv_summit_inferior_lateral_z_d90 | q_ratio_avl_avr: 0.0 -> nan

## Leads with polarity 0 (neither), clean ECG, 579 beats per cell

| mode / rule | I | II | III | aVR | aVL | aVF | V1 | V2 | V3 | V4 | V5 | V6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| true | window_only | 198 | 148 | 112 | 282 | 152 | 137 | 110 | 54 | 71 | 127 | 139 | 171 |
| true | N20 | 317 | 286 | 228 | 364 | 267 | 269 | 229 | 155 | 213 | 258 | 268 | 290 |
| true | primary | 174 | 147 | 119 | 215 | 150 | 144 | 95 | 90 | 100 | 124 | 118 | 148 |
| stim | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stim | window_only | 198 | 148 | 112 | 282 | 152 | 137 | 110 | 54 | 71 | 127 | 139 | 171 |
| stim | N20 | 317 | 286 | 228 | 364 | 267 | 269 | 229 | 155 | 213 | 258 | 268 | 290 |
| stim | primary | 174 | 147 | 119 | 215 | 150 | 144 | 95 | 90 | 100 | 124 | 118 | 148 |
| detected | 030 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| detected | window_only | 198 | 148 | 112 | 282 | 152 | 137 | 110 | 54 | 71 | 127 | 139 | 171 |
| detected | N20 | 317 | 286 | 228 | 364 | 267 | 269 | 229 | 155 | 213 | 258 | 268 | 290 |
| detected | primary | 174 | 147 | 119 | 215 | 150 | 144 | 95 | 90 | 100 | 124 | 118 | 148 |

## initial_start_ms and visible onset - stimulus: see gates_040.json (per heart and region / family and depth)

