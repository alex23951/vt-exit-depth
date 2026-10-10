# Fast layer vs Purkinje network vs no fast conduction: control heart, 144 sites (9 Oct 2026)

One heart (Y5HYEDL4), pure eikonal beats, ecg_depth_criteria 0.3.0. Descriptive only. Medians at true onset
(stimulus to last activation) unless marked; detected onset gives the same picture (tables.txt).

## Short answer

1. **The Purkinje network gives realistic paced QRS widths.** At the LV summit and aortic cusps the median QRS is
   162.5 ms with the network, compared with 123 ms with the fast layer and 250 ms with no fast conduction.
   Normal-heart idiopathic VAs measure 147-175 ms. The network is the only arm that passes the decision-7 range
   (132-193 ms). Other regions: LV free wall 165 ms, septum 143 ms, RV free wall 151 ms, RVOT 146.5 ms, vein course
   174.5 ms.
2. **The depth signal survives with the network, a little weaker.** At the same LV free-wall spot, 10 % -> 90 %:

   | | Fast layer | Network | No layer |
   |---|---|---|---|
   | QRS change | +13.5 ms (+10.3 %) | +10.5 ms (+7.9 %) | +4.5 ms (+2.4 %) |
   | AUC shortest RS | 0.94 | 0.95 | 0.69 |
   | AUC MDI | 0.96 | 0.83 | 0.54 |
   | AUC pseudo-delta | 0.84 | 0.80 | 0.49 |
   | AUC IDT | 0.79 | 0.76 | 0.62 |

   Over all sites with a depth truth (cusps excluded), the AUCs for 90 % vs 10 % sites are 0.65-0.72 with the
   network and 0.59-0.79 with the layer.
3. **The published cut-offs behave differently with the network.** Pseudo-delta is longer everywhere, so >= 34 ms
   calls 24 of 34 endocardial sites epicardial (31 of 34 at 90 %). Shortest RS >= 121 ms almost never fires (0 at
   10 %, 1 at 90 %). IDT >= 85 ms goes from 8 to 15 of 34. MDI >= 0.55 goes from 2 to 6.
4. **Daniels's MDI order still fails, in all three arms.** With the network: RVOT 0.64 > cusp 0.57 > vein course
   0.46 > summit 0.41 = LV endocardium 0.41 (Daniels: LV epicardial perivascular 0.61 > aortic sinus 0.46 >
   RVOT 0.40 > LV endocardium 0.34). The outflow MDI excess is present with any conduction model. That points to
   geometry or lead placement, which fits the 5 Oct desk check and the open frontal-axis item.

## Caveats

- One heart. The network is a rule-based model (sources in sims/biv_model/14_purkinje.py). Two of its values
  are assumptions: the bundle speeds (2.0-3.4 m/s), calibrated to Durrer's activation timing, and the 2 ms
  muscle -> Purkinje delay.
- The His-driven normal beat has a QRS of 98 ms and starts at Durrer's sites, but its frontal axis is about -92
  deg. An idealised beat with the whole inner wall activated at once gives the same superior axis, so the cause is
  the heart or torso model, not the network. This is an open item.
- 11 of 144 network beats use the combined-graph activation, because openCARP's solver did not finish for them.
  The graph matched openCARP to a median 0.24 ms on the other sites.
