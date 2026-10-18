# Step 4.4: v5.1 conduction system (decisions E and B), STOP 4c

PC clock 2026-10-18 15:01-15:08 CEST (UTC 13:01-13:08). Script: network51.py (`HEART=<H> python -B ... build`).
Reports: network51_<H>.json. Parameters: params/params_network_<H>_v51.json. Networks: data/biv/<H>/purkinje_v51/.
E9: predictions_E9.md, written before any v5.1 beat.

## What changed

The network topology stays exactly v5's network v3: the same nodes, edges and junctions, the junction delays of 4 / 2 ms,
and 6G8DD8S5's left-bundle cut. Only the speeds change:

| Class | Edges (Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR) | v5 speed (m/s) | v5.1 speed (m/s) |
|---|---|---|---|
| HIS | 0 / 0 / 0 (root = LB/RB split) | - | 1.5 |
| RB (His to moderator-band insertion) | 67 / 54 / 59 | 3.36 / 2.72 / 2.91, tuned to Durrer | 1.5 |
| LB_TRUNK | 17 / 27 / 13 | 2.0 | 1.5 |
| FASCICLE (to Durrer's three sites) | 109 / 75 / 91 | 2.0-3.16 / 1.75-2.37 / 2.0-2.91, tuned | 2.0 |
| DISTAL (rest) | 9471 / 7655 / 7936 | 2.0 per edge (tuned paths beyond the sites) | 3.00 / 2.88 / 2.84 |

- **E1:** no v5.1 code imports or calls the v5 Durrer-offset calibration (sims/biv_model/14_purkinje.py 331-346). The
  only speed sources are CLASS_SPEED, R10 and P5 in network51.py. The 14_purkinje.py lines remain for v5 only.
- **E4 R10 (none above 1.10, so no speed is scaled):**
  - Y5HYEDL4: RB 1.047, LB 1.044, fascicles 1.068 / 1.036 / 1.042.
  - 6G8DD8S5: 1.049, 1.051, 1.036 / 1.047 / 1.038.
  - 7D98EVAR: 1.042, 1.053, 1.067 / 1.058 / 1.037.
- **Durrer sites** (the first distal root on each division): at UVC (z, phi) of about (0.80, 60), (0.50, 0) and
  (0.33, -59) in every heart. These are the waypoints of the v5 build.
- **Distal roots (P2):** the 3 Durrer sites, the RB low point (where the RB apical branch leaves) and the moderator-band
  insertion. 5 per heart.

## Gates

| Gate | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| E6 cut unchanged (diff vs v5) | n/a | empty: PASS | n/a |
| E8 every edge = class value | PASS | PASS | PASS |
| P5 v_edge (m/s) | 3.00 | 2.88 | 2.84 |
| P6 de-duplicated v_edge within 1 % | 3.0038 vs 3.0038: PASS | 2.8753 vs 2.8753: PASS | 2.8447 vs 2.8447: PASS |
| P7 median A_j = 2.00 +- 0.02 | 1.9975: PASS | 2.0032: PASS | 1.9967: PASS |
| F19 de-duplication changes no v5.1 time | 0.0 ms: PASS | 0.0 ms: PASS | 0.0 ms: PASS |

- **P5 expectation:** the brief expected 3.6-3.9 m/s (inference). The measured path ratio is lower: 1.50 / 1.44 / 1.42 at
  2.0 m/s per edge, against 1.79 / 1.94 / 1.80 quoted for v5, which was measured differently. No v_edge is above 4.0 m/s.
- **P7 details:**
  - IQR 1.70-2.27 m/s in Y5HYEDL4.
  - LV-only and RV-only medians: 1.996 and 2.009 (Y5HYEDL4).
  - Ratio of sums: 1.92 / 1.99 / 1.92.
  - Junctions used: 3499 / 2981 / 3053, of 3665 / 3192 / 3241; none unreached.
- **P8 (report):** LV septal junction pairs 15-25 mm apart in one subtree, median D / |dt|: 3.32 / 2.57 / 3.89 m/s.
- **F19 (report):**
  - Exact duplicate pairs: 2803 / 2227 / 2307.
  - v5 shared division edges with different speeds: 2 / 6 / 0.
  - Each division on its own copies only: 6G8DD8S5 septal site 18.94 -> 19.79 ms, which reproduces the audit's
    18.9 -> 19.8 ms. Y5HYEDL4 septal: 18.29 -> 18.45 ms.
  - In v5.1 all copies of a pair share one speed.

## E9 (analytic, before any beat; details in predictions_E9.md)

| | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| His to Durrer sites (ms) | 17.9 / 23.2 / 30.4 | not reached (LB cut) | 16.8 / 20.7 / 28.1 |
| Durrer spread; sites within 5 ms | 12.6 ms; 1 of 3 | n/a | 11.2 ms; 2 of 3 |
| His to first muscle (ms) | 21.9 (20.6-23.2) | 40.8 (35.3-46.7), RV | 20.8 (19.5-22.3) |

Ranges in brackets are HIS / RB / LB_TRUNK at 1.8-1.27 m/s. Durrer (a) is predicted to fail in the control heart.
