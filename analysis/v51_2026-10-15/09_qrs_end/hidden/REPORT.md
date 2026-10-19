# Hidden late-QRS check (19 Oct 2026, read-only)

Why does the last part of activation leave so little on the v5.1 model ECG? Control heart Y5HYEDL4, v5.1 network beats.
Target: the 16 LV summit and aortic-cusp beats behind gate 1. Contrast: the 10 LV free-wall 10 % / 90 % pairs (20 beats).
No simulation was run, no v5.1 file changed, nothing tuned. Script: `analysis/v51_2026-10-15/09_qrs_end/hidden51.py`.
Per-beat values: `hidden51.csv` (one row per beat; per-lead columns for all 12 leads).

Definitions (my reading of the brief, stated where it forks):
- Surface QRS end = the Step 6 0.4.0 offset in any lead under gate 1's primary convention (detected onset, 10 uV noise,
  median of 10 seeds), for target and contrast alike. The clean offsets differ by at most 1 ms.
- True end = the latest node activation. Hidden window = surface end to true end.
- Hidden tissue = myocardium activated at or after the surface end (nodal volumes from the mesh; all ventricular tags).
- ECG contributions use the Step 6 lead fields and template, with Vm taken relative to rest. Peaks are the change from
  the surface end, inside the hidden window. "Early tissue" = everything activated before the surface end.
- Spatial velocity = the 0.4.0 offset velocity (6 ms smoothing, leads I, II, V1-V6). Threshold = 10 % of the full ECG's
  peak, as the rule uses on a clean ECG.

## Table 1. Target vs contrast (median [range])

| Measure | Target (summit + cusp, n = 16) | Contrast (LV free wall, n = 20) |
|---|---|---|
| Surface QRS, any lead (ms) | 120 [102-130] | 97 [80-124] |
| Surface end (ms from stimulus) | 122 [109-134] | 100 [83-128] |
| True activation end (ms) | 145 [132-155] | 142 [131-169] |
| Hidden window (ms) | 24 [13-26] | 43 [30-49] |
| Hidden tissue (mL) | 4.6 [1.2-5.9] | 12.2 [7.5-16.0] |
| Hidden tissue (% of 233.6 mL myocardium) | 2.0 [0.5-2.5] | 5.2 [3.2-6.8] |
| Hidden tissue in the LV (%) | 0 [0-0] | 5 [0-18] |
| Hidden tissue endo / mid / epi third (%) | 24 / 30 / 46 | 26 / 30 / 44 |
| Hidden tissue's largest lead contribution (mV) | 0.23 [0.05-0.32] | 0.39 [0.26-0.62] |
| Full beat's largest QRS deflection (mV) | 2.75 [2.56-3.33] | 2.35 [1.82-3.07] |
| Hidden contribution / largest QRS deflection | 0.09 [0.01-0.12] | 0.16 [0.09-0.31] |
| Cancellation (plain sum / sum of absolute AHA-region parts, median lead) | 1.00 [0.28-1.00] | 0.93 [0.87-1.00] |
| Early tissue's signal in the window, largest lead (mV) | 0.08 [0.06-0.09] | 0.11 [0.07-0.17] |
| Hidden tissue's peak spatial velocity / threshold | 0.55 [0.16-0.79] | 0.68 [0.45-1.45] |
| Early tissue's peak spatial velocity in the window / threshold | 0.72 [0.58-1.01] | 0.85 [0.73-1.07] |
| Full ECG's peak spatial velocity in the window / threshold | 1.03 [0.87-1.14] | 1.05 [0.83-1.63] |
| Full ECG's spatial velocity at the true end / threshold | 0.22 [0.04-0.46] | 0.10 [0.05-0.29] |

Target, per lead (median mV, hidden contribution vs QRS deflection): largest in V2 (0.23 vs 2.52) and V3 (0.21 vs 2.23);
smallest in III (0.05 vs 2.19) and aVF (0.06 vs 2.05).

## Table 2. Where the hidden tissue is (target beats)

Regions are LV AHA segments by the adopted placement frame; RV nodes are labelled RV basal / mid / apical by the same
level thirds; depth third from the UVC transmural coordinate (0 endocardium, 1 epicardium).

| Beat | Hidden mL | In LV % | Endo / mid / epi % | Main regions (% of hidden volume) |
|---|---|---|---|---|
| aortic_cusp_lcc_z_d10 | 4.10 | 0 | 24 / 32 / 45 | RV basal 77; RV apical 17; RV mid 7 |
| aortic_cusp_lcc_z_d50 | 4.28 | 0 | 24 / 31 / 45 | RV basal 76; RV apical 17; RV mid 7 |
| aortic_cusp_lcc_z_d75 | 3.99 | 0 | 24 / 32 / 45 | RV basal 76; RV apical 17; RV mid 7 |
| aortic_cusp_lcc_z_d90 | 4.24 | 0 | 23 / 31 / 45 | RV basal 75; RV apical 18; RV mid 8 |
| aortic_cusp_rcc_z_d10 | 1.45 | 0 | 17 / 26 / 57 | RV apical 51; RV basal 47; RV mid 2 |
| aortic_cusp_rcc_z_d50 | 1.53 | 0 | 17 / 26 / 56 | RV apical 57; RV basal 42; RV mid 1 |
| aortic_cusp_rcc_z_d75 | 1.17 | 0 | 17 / 26 / 57 | RV apical 52; RV basal 47; RV mid 1 |
| aortic_cusp_rcc_z_d90 | 1.53 | 0 | 18 / 26 / 56 | RV apical 58; RV basal 40; RV mid 1 |
| lv_summit_inferior_lateral_z_d10 | 4.84 | 0 | 23 / 30 / 48 | RV basal 97; RV apical 2; RV mid 1 |
| lv_summit_inferior_lateral_z_d50 | 5.10 | 0 | 23 / 30 / 47 | RV basal 96; RV apical 3; RV mid 1 |
| lv_summit_inferior_lateral_z_d75 | 5.18 | 0 | 24 / 30 / 46 | RV basal 94; RV apical 4; RV mid 1 |
| lv_summit_inferior_lateral_z_d90 | 4.99 | 0 | 24 / 30 / 45 | RV basal 93; RV apical 5; RV mid 2 |
| lv_summit_superior_z_d10 | 5.61 | 0 | 24 / 30 / 46 | RV basal 93; RV apical 6; RV mid 2 |
| lv_summit_superior_z_d50 | 5.87 | 0 | 25 / 30 / 45 | RV basal 82; RV apical 13; RV mid 5 |
| lv_summit_superior_z_d75 | 4.88 | 0 | 25 / 30 / 45 | RV basal 81; RV apical 13; RV mid 8 |
| lv_summit_superior_z_d90 | 4.94 | 0 | 25 / 30 / 45 | RV basal 79; RV apical 13; RV mid 8 |

Activation of the hidden tissue (5 ms histogram, per beat in `hidden51.csv`): 74-100 % of it falls in the first three
5 ms bins after the surface end, and the last bin holds at most 0.11 mL.

## Repolarisation overlap

The model's ECG has no repolarisation. Its template (Tomek pseudo-Vm from the openCARP template run) covers -60 to +80 ms
around each node's activation: upstroke, then a plateau dome rising to about 21 mV at 20-30 ms and falling to 13.9 mV at
80 ms, held after that. So there is no phase-1 notch, no phase 3 and no T wave. The dome of early tissue does add signal
inside the hidden window: 0.08 mV [0.06-0.09] in the target beats, with a spatial velocity at 0.72 times the threshold. That
is about a third of the hidden tissue's own amplitude, and of similar slope.

## What makes the hidden tissue quiet

- Measured: it is small. The last 24 ms of the target beats activate 4.6 mL, 2 % of the ventricles, and all of it is in the
  RV, mostly the basal RV (the RV apex too for the RCC beats). Its largest lead contribution is 0.23 mV, 9 % of the largest
  QRS deflection, and its spatial velocity peaks at about half the rule's threshold. On its own, the 10 % rule cannot see it.
- Measured: cancellation is not the reason for the LCC and summit beats (plain sum equals the sum of absolute regional
  parts). It is a reason for the RCC beats, where the hidden tissue is split between the RV apex and base and the parts
  cancel to about a third.
- Measured: the full ECG's spatial velocity in the window only touches the threshold (peak 1.03 times) and is at 0.22
  times it by the true end. The rule's ending reflects a slow, low tail, not a sharp cut.
- Measured: this is not special to summit and cusp beats. The LV free-wall contrast beats hide more: 43 ms and 12 mL,
  again almost all RV.
- Inferred: the quiet tail is the late, slowly spreading activation of the thin basal RV, which adds little new wavefront
  per millisecond. The early tissue's plateau dome adds a signal of similar slope, which blurs the tail further. Whether
  real hearts show this tail more clearly (a thicker or larger late region, faster late conduction, or the T wave's onset)
  cannot be told from this check.
