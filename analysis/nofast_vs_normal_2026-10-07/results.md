# No-fast-layer control (job 1), control heart Y5HYEDL4, 7 Oct 2026

One heart, pure eikonal beats, so everything here is descriptive. "Normal" is the frozen model, with a 2.0 m/s
fast endocardial layer. "No fast layer" gives those same elements ordinary myocardial speeds and conductivities.
Both grids were scored with ecg_depth_criteria 0.3.0. Values are medians at true onset (stimulus to last
activation) unless marked. Detected onset gives the same picture (tables below).

## Short answer

1. **The fast layer is what makes the model's QRS narrow, but taking it out overshoots.** Without the layer, the
   QRS roughly doubles at every site, to about 250 ms (true onset) or 220-250 ms (detected). With the layer it is
   111-131 ms. Normal-heart idiopathic VAs measure 147-175 ms (Yamada 2010 and 2016, Santangeli 2015), and Bazan
   2007's mostly cardiomyopathy patients measure 191-213 ms. Real conduction lies somewhere between the two models.
2. **The depth signal comes from the layer.** Without it, an endocardial and an epicardial exit at the same LV
   free-wall spot look almost the same:

   | LV free wall, 10 % -> 90 % at the same spot | With layer | Without layer |
   |---|---|---|
   | QRS change | +13.5 ms (10/10 up), +10.3 % | +4.5 ms (6/10 up), +2.4 % |
   | AUC, MDI | 0.96 | 0.54 |
   | AUC, shortest RS | 0.94 | 0.69 |
   | AUC, pseudo-delta | 0.84 | 0.49 |
   | AUC, IDT | 0.79 | 0.62 |

   The relative QRS rule (epicardial 8-16 % longer, Bazan 2007 Table 2) passes with the layer and fails without it.
3. **The high outflow MDI is not caused by the layer.** Without the layer, the RVOT MDI rises (0.52 -> 0.61), the
   cusp MDI stays at 0.55 and the LV endocardium rises (0.36 -> 0.44). The summit at 90 % is 0.44, and the new
   Daniels vein-course sites are 0.34. So Daniels's order still fails, and now more clearly. The aim 1 gaps note
   (4 Oct) set a rule in advance: if outflow MDI stays above 0.50 without the layer, the cause is geometry or lead
   placement. That rule now applies. It fits the 5 Oct desk check, which found the axis was off at the left cusp,
   the summit and the free-wall RVOT.
4. **Without the layer, the interval criteria call nearly everything epicardial.** For example, shortest RS
   >= 121 ms fires at 21 of 29 endocardial (10 %) sites, against 0 of 29 with the layer. Every beat is slow, so
   every interval is long.

## What this means (inference, not tested)

The model's depth signal depends on how an endocardial exit reaches fast conduction. A continuous sheet gives every
endocardial exit immediate access. That is probably too efficient: the QRS is narrow, and the depth signal may be
too strong. No fast conduction at all gives no access: the QRS is far too wide and there is no depth signal. A
branched Purkinje network that joins the muscle at discrete points (your point of 5 Oct) is the physiological
middle. It could change both the QRS width and the size of the depth signal. That makes the network question
central to the study rather than a side issue. On 5 Oct you chose "After the test" for that decision, and the test
is now done.

## Tables

Paired sites: the same site id and node in both grids (94: the 93 unchanged v3 sites and one new site). The new
summit, vein-course and 75 % sites have no normal-layer run yet. Job 2 adds them.

True onset, medians, with layer -> without layer:

| Group | n | QRS ms | Pseudo-delta ms | IDT V2 ms | Shortest RS ms | MDI (Daniels) |
|---|---|---|---|---|---|---|
| LV free wall | 30 | 130.5 -> 254.5 | 33.5 -> 48.5 | 49.5 -> 108.5 | 56.5 -> 139 | 0.37 -> 0.43 |
| LV septum | 24 | 111 -> 210 | 28.5 -> 45 | 100 -> 205 | 49 -> 126 | 0.41 -> 0.45 |
| RV free wall | 27 | 121 -> 257 | 14 -> 14 | 23 -> 241 | 49 -> 176 | 0.39 -> 0.44 |
| RVOT | 6 | 112.5 -> 234.5 | 46.5 -> 88 | 41 -> 73 | 69 -> 143.5 | 0.52 -> 0.61 |
| Aortic cusp | 6 | 131 -> 233.5 | 68 -> 85.5 | 55 -> 128.5 | 77 -> 186.5 | 0.55 -> 0.55 |

Detected onset, same pairs: QRS LV free wall 111.5 -> 243, septum 96.5 -> 199.5, RV 103 -> 250, RVOT 101 -> 229.5,
cusp 108 -> 221.5 ms. MDI LV free wall 0.40 -> 0.43, septum 0.43 -> 0.45, RV 0.44 -> 0.43, RVOT 0.54 -> 0.61,
cusp 0.63 -> 0.55.

Daniels order, precordial MDI (Daniels 2006: LV epicardial 0.61 > ASOV 0.46 > RVOT 0.40 > LV endocardial 0.34):

| | Summit 90 % | Vein course 90 % | Cusp | RVOT | LV endo 10 % |
|---|---|---|---|---|---|
| With layer, true | job 2 | job 2 | 0.55 | 0.52 | 0.36 |
| Without layer, true | 0.44 | 0.34 | 0.55 | 0.61 | 0.44 |
| Without layer, detected | 0.45 | 0.35 | 0.55 | 0.61 | 0.44 |

Epicardial calls at true / detected onset, paired sites with a depth truth (cusps excluded), with -> without layer:

| Depth | n | PdW >= 34 | IDT >= 85 | SRS >= 121 | MDI >= 0.55 |
|---|---|---|---|---|---|
| 10 % | 29 | 6/6 -> 19/17 | 2/1 -> 19/16 | 0/0 -> 21/18 | 0/0 -> 6/6 |
| 50 % | 30 | 8/3 -> 19/18 | 9/2 -> 23/15 | 0/0 -> 23/19 | 0/0 -> 5/5 |
| 90 % | 29 | 11/8 -> 18/18 | 12/6 -> 24/19 | 0/0 -> 23/23 | 0/5 -> 5/5 |

Absolute QRS, decision 7 (median at the LV summit and aortic-cusp sites must lie within 132-193 ms): with the
layer, true 131 ms (n 6, the cusps only until job 2 runs the new summit sites), which narrowly fails. Without the
layer, true 250 ms (n 16), which fails.

Total activation: median 122 ms with the layer, 248 ms without (range 200-288).

## Run and files

- Job 1: `bash jobs/start.sh 1`, started by Alex at 19:42 and finished at 20:59 (PC time, UTC+2). 144/144 sites,
  0 failed. The smoke-test site ran at 19:33. Median 94 s per site, 3 at a time. The 2.5-3 h estimate was too
  high; the whole job took 77 min.
- Grids: analysis/grids_2026-10-07/nofast_Y5HYEDL4.csv and new_Y5HYEDL4.csv. Pairs: analysis/nofast_vs_normal_2026-10-07/pairs.csv.
  Script: analysis/nofast_vs_normal_2026_10_07.py.
- Caveats: one heart; eikonal with a pseudo-Vm template action potential taken from the normal-layer monodomain
  beat; torso T13 with uniform 0.2 S/m. Lead fields for the no-layer variant were computed fresh with its own
  conductivities.
