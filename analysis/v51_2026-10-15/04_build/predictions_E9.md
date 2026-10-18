# v5.1 analytic predictions E9 (brief Step 4.4), written before any v5.1 beat

Written: PC clock 2026-10-18 15:07 CEST (UTC 13:07), from analysis/v51_2026-10-15/04_build/network51_<H>.json. No v5.1 beat (His or paced) has
been computed. Network-only shortest paths from the His (the v5.1 network: HIS / RB / LB_TRUNK 1.5 m/s, fascicles 2.0 m/s,
distal v_edge per heart, R10 never above 1.10 so no speed was scaled); first muscle = earliest junction + 4 ms. In brackets:
HIS / RB / LB_TRUNK at 1.8 and 1.27 m/s (analytic range only). Never tuned to. Supersedes PRED-1 to PRED-4 where they overlap.

| Heart | His -> Durrer site, anterior / septal / posterior (ms) | Durrer spread (ms); sites within 5 ms of the earliest | His -> moderator-band end (ms) | His -> first muscle (ms), side | v_edge (m/s) |
|---|---|---|---|---|---|
| Y5HYEDL4 | 17.9 (16.6-19.2) / 23.2 (21.7-24.7) / 30.4 (29.0-32.0) | 12.6 (12.4-12.8); 1 of 3 | 52.6 (43.8-62.1) | 21.9 (20.6-23.2), LV | 3.00 |
| 6G8DD8S5 | not reached through the network (left bundle cut) | n/a | 45.0 (37.5-53.1) | 40.8 (35.3-46.7), RV | 2.88 |
| 7D98EVAR | 16.8 (15.5-18.3) / 20.7 (19.4-22.2) / 28.1 (26.7-29.5) | 11.2 (11.2-11.2); 2 of 3 | 43.3 (36.1-51.1) | 20.8 (19.5-22.3), LV | 2.84 |

Against the 4.0 predictions (inference):
- PRED-1 His -> first muscle 23-25 / 40-50 / 22-24 ms: E9 gives 21.9 / 40.8 / 20.8 ms, about 1-2 ms shorter in the
  two narrow-QRS hearts.
- PRED-2 Durrer (a): E9 predicts a spread above 5 ms in both hearts with an intact left bundle. Fewer than 2 of
  Durrer's 3 areas fall within 5 ms in Y5HYEDL4 (1 of 3), so the control heart is predicted to fail (a).
- Root position: the network's root is at the LB/RB split, a distal His. So 4.6 compares His -> QRS onset with the
  distal-root ranges: HVdis 46 +- 10 ms and dH-Q 18-35 ms.
