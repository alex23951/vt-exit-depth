# Aim 1 verdict follow-up, model v5 (13 Oct 2026; existing v5 beats, true onset)

## 1 Relative QRS, LV free wall 90 % vs 10 % at matched positions (pass 206/191 = 1.0785 to 219/189 = 1.1587)

| heart | pairs | median QRS 90 / 10 % (ms) | ratio of medians | median of per-pair ratios | pass (ratio of medians / per-pair) |
|---|---|---|---|---|---|
| Y5HYEDL4 | 10 | 166.0 / 151.5 | 1.0957 | 1.0796 | True / True |
| 6G8DD8S5 | 10 | 167.5 / 145.0 | 1.1552 | 1.1472 | True / True |
| 7D98EVAR | 10 | 169.5 / 151.5 | 1.1188 | 1.1028 | True / True |

The "medians 1.096" of the v5 gate table is the ratio of median QRSs (median over the 10 positions at 90 % divided by the median at 10 %), the 12 Oct statistic.

## 2 Durrer on the v5 His beat (times after the first LV endocardial activation)

### Y5HYEDL4
- (a) first 5 ms of LV endocardial activation (131 nodes):
  - high anterior paraseptal (phi +60, z 0.80): earliest activation within 10 mm at 0.0 ms -> inside the first 5 ms; 104 of the first-5-ms nodes within 15 mm
  - central left septum (phi 0, z 0.50): earliest activation within 10 mm at 2.7 ms -> inside the first 5 ms; 26 of the first-5-ms nodes within 15 mm
  - posterior paraseptal at 1/3 apex-base (phi -60, z 0.33): earliest activation within 10 mm at 5.0 ms -> inside the first 5 ms; 1 of the first-5-ms nodes within 15 mm
- (b) LV endocardium outside the posterobasal region (UVC z >= 2/3, phi -150..-30 deg) active by 37.5 ms: 66.8 % (by 30 ms 48.7 %)
- (c) first RV epicardial breakthrough at 15.1 ms, UVC z 0.38, phi -0 deg (lateral RV free wall, mid level), 3.9 mm from the moderator-band insertion: consistent with the area pretrabecularis (anterior RV free wall at the moderator-band insertion) if that proxy is accepted; the mesh has no trabecular labels, so this is a geometric proxy
- (d) last 5 % of the volume (from 71.4 ms): pulmonary conus (<= 20 mm from the pulmonary rim) 36.6 %, RV A-V sulcus (<= 10 mm from the tricuspid rim) 36.0 %, other (anterior / septal base) 20.4 %, LV posterolateral base 6.5 %, RV posterobasal 0.5 %. Durrer's late areas: posterobasal LV, pulmonary conus, RV posterobasal / A-V sulcus.

### 7D98EVAR
- (a) first 5 ms of LV endocardial activation (105 nodes):
  - high anterior paraseptal (phi +60, z 0.80): earliest activation within 10 mm at 0.0 ms -> inside the first 5 ms; 84 of the first-5-ms nodes within 15 mm
  - central left septum (phi 0, z 0.50): earliest activation within 10 mm at 2.5 ms -> inside the first 5 ms; 21 of the first-5-ms nodes within 15 mm
  - posterior paraseptal at 1/3 apex-base (phi -60, z 0.33): earliest activation within 10 mm at 5.4 ms -> outside the first 5 ms; 4 of the first-5-ms nodes within 15 mm
- (b) LV endocardium outside the posterobasal region (UVC z >= 2/3, phi -150..-30 deg) active by 37.5 ms: 61.0 % (by 30 ms 44.4 %)
- (c) first RV epicardial breakthrough at 16.4 ms, UVC z 0.24, phi 10 deg (lateral RV free wall, mid level), 11.2 mm from the moderator-band insertion: consistent with the area pretrabecularis (anterior RV free wall at the moderator-band insertion) if that proxy is accepted; the mesh has no trabecular labels, so this is a geometric proxy
- (d) last 5 % of the volume (from 72.0 ms): pulmonary conus (<= 20 mm from the pulmonary rim) 27.2 %, other (anterior / septal base) 27.0 %, LV posterolateral base 25.8 %, RV A-V sulcus (<= 10 mm from the tricuspid rim) 20.0 %. Durrer's late areas: posterobasal LV, pulmonary conus, RV posterobasal / A-V sulcus.

## 3 Bazan 2007 per region, pooled over the three hearts (LV free wall, vein-course and summit positions; true onset)

Bazan 2007 (abstract): epi vs endo q in I basal superior 90 vs 16 %, apical superior 88 vs 26 %; Q in II/III/aVF basal inferior 81 vs 37 %, apical inferior 92 vs 33 %; basal superior: absence of inferior Q identifies epicardium (P .002, no % given). Gate: per-region 95 % CI, >= 20 pooled positions.

| region / feature | threshold | positions | 90 % | 10 % | difference (95 % CI), pp | Bazan difference, pp | verdict |
|---|---|---|---|---|---|---|---|
| basal superior: q in I | 0.05 mV | 21 | 4/21 (19 %) | 3/21 (14 %) | +5 (-19 to +28) | +74 | fail (Bazan outside CI) |
| basal superior: q in I | 0.10 mV | 21 | 3/21 (14 %) | 0/21 (0 %) | +14 (-4 to +35) | +74 | fail (Bazan outside CI) |
| basal superior: no Q in II/III/aVF | 0.05 mV | 21 | 12/21 (57 %) | 6/21 (29 %) | +29 (-1 to +52) | n/a | direction as Bazan (more at epi); no Bazan % to compare |
| basal superior: no Q in II/III/aVF | 0.10 mV | 21 | 13/21 (62 %) | 6/21 (29 %) | +33 (+3 to +56) | n/a | direction as Bazan (more at epi); no Bazan % to compare |
| apical superior: q in I | 0.05 mV | 9 | 4/9 (44 %) | 2/9 (22 %) | +22 (-19 to +55) | +62 | not evaluable (< 20 positions) |
| apical superior: q in I | 0.10 mV | 9 | 2/9 (22 %) | 1/9 (11 %) | +11 (-25 to +45) | +62 | not evaluable (< 20 positions) |
| basal inferior: Q in II/III/aVF | 0.05 mV | 8 | 8/8 (100 %) | 0/8 (0 %) | +100 (+54 to +100) | +44 | not evaluable (< 20 positions) |
| basal inferior: Q in II/III/aVF | 0.10 mV | 8 | 5/8 (62 %) | 0/8 (0 %) | +62 (+17 to +86) | +44 | not evaluable (< 20 positions) |
| apical inferior: Q in II/III/aVF | 0.05 mV | 7 | 6/7 (86 %) | 0/7 (0 %) | +86 (+34 to +97) | +59 | not evaluable (< 20 positions) |
| apical inferior: Q in II/III/aVF | 0.10 mV | 7 | 6/7 (86 %) | 0/7 (0 %) | +86 (+34 to +97) | +59 | not evaluable (< 20 positions) |

0.10 mV = package q present and q depth >= 0.10 mV (saved amplitudes; no ECGs were saved for the v5 grid, so no full rescoring).

## 4 Berruezo direction, 6G8DD8S5 LV free wall, median paired difference 90 - 10 % (ms, true onset)

- QRS: +22.0 ms (positive in 10 / 10 pairs, zero 0)
- pseudo-delta: +25.0 ms (positive in 9 / 10 pairs, zero 0)
- IDT: +17.0 ms (positive in 6 / 10 pairs, zero 0)
- shortest RS: +6.0 ms (positive in 5 / 10 pairs, zero 0)

## 5 Relative QRS as the ratio of group mean QRS (Alex "Means", 19:23 UTC 13 Oct; pass 1.0785-1.1587), LV free wall 90 % / 10 % at matched positions

| heart | set | pairs | mean QRS 90 % (ms) | mean QRS 10 % (ms) | ratio of means | pass |
|---|---|---|---|---|---|---|
| Y5HYEDL4 | v3 | 10 | 169.9 | 159.3 | 1.0665 | FAIL |
| Y5HYEDL4 | v5 | 10 | 165.4 | 154.4 | 1.0712 | FAIL |
| 6G8DD8S5 | v3 | 10 | 147.8 | 134.8 | 1.0964 | pass |
| 6G8DD8S5 | v5 | 10 | 163.4 | 143.7 | 1.1371 | pass |
| 7D98EVAR | v3 | 10 | 156.1 | 145.3 | 1.0743 | FAIL |
| 7D98EVAR | v5 | 10 | 166.9 | 152.7 | 1.0930 | pass |

Verdict on v5 with the ratio of means: control heart FAIL (below 1.0785); 6G8DD8S5 and 7D98EVAR pass.

