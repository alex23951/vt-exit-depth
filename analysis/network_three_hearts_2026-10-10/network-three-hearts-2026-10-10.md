# Purkinje network on all three pilot hearts: paced QRS, depth signal and published cut-offs (10 Oct 2026)

Network v3, 144 v5 sites per heart (jobs 8-10), ECG with the realistic "cb" volume conductor (heart at Clerc scale +
cavity blood), ecg_depth_criteria 0.3.0. Y5HYEDL4 = control, 6G8DD8S5 = HF wide QRS (proximal left-bundle cut),
7D98EVAR = HF narrow QRS. Pilot hearts: descriptive only. Medians at true onset (stimulus to last activation) unless
marked; detected onset gives the same picture (tables.txt). Script: analysis/network_three_hearts_2026_10_10.py.

## Short answer

1. **Paced QRS width is realistic in the control heart and narrower in the two failure hearts.** LV summit + aortic
   cusp median: 162.5 ms (control), 134 ms (LBBB heart), 144 ms (narrow-QRS HF heart). All three lie in the
   decision-7 range (132-193 ms), but only the control heart is in the normal-heart idiopathic range (147-175 ms).
   The model gives every heart the same tissue speeds, so the HF hearts differ only in geometry, network and (6G8DD8S5)
   the bundle cut (inference: no HF remodelling is modelled).
2. **Deeper exits widen the QRS by about the published amount.** Same LV free-wall spot, 10 % -> 90 % depth:
   +10.5 / +16 / +11.5 ms (+7.9 / +12.1 / +8.2 %), against Bazan 2007's 8-16 % epi-over-endo range.
3. **Pseudo-delta and MDI still track depth; IDT and shortest RS mostly don't.**

   | AUC, 90 % vs 10 % depth | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
   |---|---|---|---|
   | LV free wall, pseudo-delta | 0.76 | 0.94 | 0.75 |
   | LV free wall, MDI | 0.88 | 0.80 | 0.84 |
   | LV free wall, IDT V2 | 0.44 | 0.57 | 0.34 |
   | LV free wall, shortest RS | 0.49 | 0.68 | 0.50 |
   | All depth-truth sites, best criterion | pseudo-delta 0.65, MDI 0.68 | pseudo-delta 0.75 | pseudo-delta 0.70 |

4. **The published cut-offs misclassify in opposite directions** (34 depth-truth sites per depth per heart):

   | Epicardial calls at 10 % / 90 % depth | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
   |---|---|---|---|
   | Pseudo-delta >= 34 ms | 24 / 27 | 26 / 28 | 23 / 29 |
   | IDT >= 85 ms | 4 / 5 | 1 / 5 | 1 / 1 |
   | Shortest RS >= 121 ms | 1 / 2 | 0 / 0 | 0 / 0 |
   | MDI >= 0.55 | 3 / 6 | 8 / 11 | 7 / 9 |
   | q in lead I | 18 / 15 | 16 / 9 | 17 / 16 |

   Pseudo-delta >= 34 ms calls about 70 % of endocardial exits epicardial; IDT and RS cut-offs almost never fire, even
   at 90 % depth; q in lead I does not change with depth.
5. **Daniels's MDI order still fails in all three hearts.** RVOT has the highest MDI (0.67 / 0.59 / 0.69), then the
   cusps; LV endocardium is lowest (0.34 / 0.41 / 0.39), as Daniels found.

## Caveats

- Three pilot hearts, one network rule, one torso. The cb conductor changed IDT and shortest RS by 5-20 ms and removed
  most of their depth signal compared with the old lead fields (analysis/axis_2026-10-10/compare_cb.md), so the
  conductor is a material sensitivity.
- Combined-graph activation (openCARP did not finish in 6 min) at 11 / 0 / 8 sites.
- The normal-beat axis is now normal in the intact hearts (+64 / +63 deg) and left in the LBBB heart (-42 deg).
