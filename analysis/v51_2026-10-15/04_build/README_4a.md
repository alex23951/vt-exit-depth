# Step 4.0-4.2 (up to STOP 4a): predictions, speeds, Doste RV fibres (candidate)

PC clock 2026-10-17 00:03-00:27 CEST (UTC 2026-10-16 22:03-22:27). Alex "Go for Step 4 up to STOP 4a" (22:00:06 UTC).
DOSTE_SCOPE = WHOLE_RV (Alex 15 Oct 08:31:14 UTC). No v5.1 beat has been run.

- 4.0 predictions.md (PRED-1 to PRED-4), committed and pushed at 00:03 (966ee76) before anything else of v5.1.
- 4.1 params/v51_speeds.json: 0.60 / 0.36 / 0.48 m/s (Y5HYEDL4), 0.60 / 0.26 / 0.336 (6G8DD8S5, 7D98EVAR).
- 4.2 doste_rv.py (stages laplace, fibres); results doste_<H>.json; candidate fibre files
  runs/v51_2026-10-15/04_build/<H>/bivF_v51_candidate.lon (not adopted; no beat uses them).

## How the brief's rule maps onto the v5 data

Fibres are per element, as in v5 (one .lon row per element):
- Nodal Laplace fields from openCARP experiment 2, unit isotropic conductivity, as 02_laplace.py (4 processes).
- Element value = mean of its nodes. Gradient = the element's P1 gradient (fibres_fix.elem_grad).
- The brief's "nodes" are these elements.

**R_field:** elements on the RV side of v5's septal split, d = phi_rv / (phi_lv + phi_rv) > 0.5. This is the array
`d` in fibres_fix.py main(); its sha256 is in doste_<H>.json. There is no discrete RV label in the fibre code.

| Heart | R_field elements | Of which LV-tagged (RV half of the septum) | Mesh RV tag 2 (alternative) | Tag 2 outside R_field |
|---|---|---|---|---|
| Y5HYEDL4 | 787,003 (94 mL) | 178,679 | 506,625 (61 mL) | 403 |
| 6G8DD8S5 | 526,146 | 147,078 | 312,487 | 430 |
| 7D98EVAR | 579,450 | 121,917 | 382,325 | 579 |

R_field also holds the RV fast-endocardial-layer tags (28, 29). With tag 2 instead, the RV half of the septum and those
layers would keep their v5 fibres.

**Fields:**
- Φ_D = −2 u_lv + u_rv, from two unit problems. The outer surface is epi + aortic-root interface minus endocardial
  nodes (the 13 Oct phi_epi_fix set). LV and RV endocardia do not overlap (0 nodes).
- Ψ_TV, Ψ_PV and w on the R_field submesh. Rings: tv_rim / pv_rim nodes in R_field. TV 1060 / 846 / 887 of
  1087 / 876 / 908 (the rest lie on the LV side of the split); PV all.
- 02_laplace.py's TV / PV sets: tv_rim, pv_rim (confirmed).
- v5's LV outflow treatment is unchanged: it lies outside R_new (A5).

**Apex set A:** 18 / 23 / 27 RV endocardial nodes, UVC z 0.18 / 0.19 / 0.20. Distance to the LV apex 26.2 / 24.4 /
28.9 mm; to the TV-ring centroid 79.4 / 69.7 / 71.9 mm.

**Maximum-principle overshoot** (audit F15, where Dirichlet sets touch): u_lv / u_rv outside 0-1 at 1 / 1 (Y5HYEDL4),
29 / 33 (6G8DD8S5) and 3 / 1 (7D98EVAR) nodes. Φ_D is outside −2..1 at 0 / 36 / 4 nodes; d is clipped there, as the
brief says.

**Guard counts** (Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR):
- w clipped: 0 / 0 / 0
- |g| < 1 % of its median, so l is taken from neighbours: 108 / 85 / 92
- |∇Φ_D| < 1 % of its median: 1723 / 247 / 410. These are mostly the flat Φ_D ≈ 0 pulmonary-artery stump above the
  valve plane. In Y5HYEDL4, 395 of them had no passing neighbour within 2 mm and took the nearest passing element.
- Added guard (not in the brief): ∇Φ_D (nearly) parallel to l, so the transmural direction is undefined: 75 / 74 / 98
  elements took the neighbour mean, as for small gradients. Without it, one row had a zero sheet vector and A1 failed
  at a handful of elements.

## Gates

| Gate | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR | Verdict |
|---|---|---|---|---|
| A1 helix vs rule, max \|Δh\| / max out-of-plane (from the written file) | 0.0005° / 0.0005° | 0.0005° / 0.0005° | 0.0005° / 0.0005° | PASS |
| A3 sign: RV epi h < 0 near the anterior / inferior junctions (median) | −19.0° / −21.7° (all < 0) | −18.9° / −20.4° | −19.5° / −21.5° | |
| A3 adjacent LV epicardium in its own frame (median) | −36.3° / −50.2° | −31.1° / −48.0° | −33.1° / −49.0° | |
| A3 RV-body mid-wall h > 0 (median) | +33.4° (all > 0) | +33.0° | +33.3° | PASS ×3 |
| A4 d ≤ 0.02: acos(\|f·l\|) ≤ 0.5° | 200 elements, max 2.20°, 87 over 0.5° | 129, max 2.16°, 1 over | 138, max 2.19°, 18 over | FAIL ×3 (by construction, see below) |
| A5 elements outside R_new unchanged | 0 of 1,152,906 changed | 0 of 1,471,782 | 0 of 1,176,264 | PASS |
| A8 orthonormal (max \|norm − 1\|, \|f·s\|) | 8.5e-6, 1.5e-5 | 8.4e-6, 1.5e-5 | 8.3e-6, 1.4e-5 | PASS |
| A8 one connected component | face-sharing 2 (a 3-element island, tag 28); node-sharing 1 | face 4 (6 elements in 3 islands, tag 1); node 1 | 1 / 1 | FAIL ×2 under face-sharing, PASS under node-sharing |

**A4 conflicts with the rule.** h = 90 (1 − d) − 25 w d gives 90° − h = d (90 + 25 w): up to 2.3° at d = 0.02. The
0.5° limit therefore holds only for d ≤ 0.0043-0.0056. A1 shows the rule is followed exactly (0.0005°), so the elements
over 0.5° are the rule itself, not an error. Not changed (brief 1.3).

**A8 islands.** They are R_field elements (d > 0.5) that touch the rest only at an edge or corner. The Laplace solve
connects them through those shared nodes, so their fields are valid.

## Reports

**A2** (median helix angles in the v5.1 frame; v5 / v5.1 / expected; w; Y5HYEDL4 shown, all hearts in doste_<H>.json):

| Region | d 0-0.05 (endo) | d 0.45-0.55 (mid) | d 0.95-1 (epi) | w |
|---|---|---|---|---|
| (a) RV body free wall (w ≥ 0.9; 1,131 elements) | +54.7 / +85.2 / +85.2 | +26.3 / +33.6 / +33.6 | −59.6 / −18.3 / −18.3 | 0.90 |
| (b) septal infundibulum, 9.6-15.1 mm below the PV plane | +70.7 / +85.3 / +85.3 | +56.5 / +39.4 / +39.4 | −4.2 / −10.7 / −10.7 | 0.41-0.45 |
| (c) free-wall infundibulum, 14.2-16.6 mm below | −81.9 / +85.5 / +85.5 | +72.0 / +42.3 / +42.3 | +0.7 / −3.9 / −3.9 | 0.22-0.27 |
| (d) septal, 2-4 mm below | −28.5 (n 7) / −90 / −90 | +63.9 / +43.9 / +43.9 | +3.5 / −2.0 / −2.0 | 0.01-0.10 |
| (d) free wall, 2-4 mm below | −87.1 / +85.6 / +85.5 | +68.6 / +44.1 / +44.1 | +6.3 / +1.4 / +1.4 | 0.05-0.07 |

Notes on A2:
- The endocardial bin includes d up to 0.05, so v5.1 reads +85°, not +90°. Angles are folded to −90..+90, so −90 ≡ +90.
- The brief expected v5 at about +64-66 / −42 to −46° in the RV body. Measured in this frame: +54.7 / −59.6.
- The brief expected v5 at about 81 / −16° at the RVOT free wall. Measured: |−81.9| (= 98°, 8° past longitudinal) / +0.7.
- (a) is empty in the heart-failure hearts: mid-RV free-wall w is 0.78 / 0.84 (median), 0.84 in the control heart, and w ≥ 0.9 in ≤ 1 %.

w at the RVOT sites: septal 0.35-0.37 / 0.51-0.54 / 0.31-0.34; free wall 0.21-0.22 / 0.22-0.23 / 0.24-0.25.

**A7** (angle between the fibres of face-sharing neighbours; median, p95; v5 → v5.1):

| Where | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| R_new border (the septal interface) | 9.7° → 25.8° (p95 63.8 → 75.9) | 12.8° → 30.9° | 12.4° → 28.9° |
| R_new border within 10 mm of the epicardial junctions | 10.3° → 40.4° | 9.0° → 45.2° | 11.1° → 44.1° |
| inside R_new (reference) | 3.5° → 5.4° (p95 18.6 → 13.4) | 3.7° → 5.5° | 3.7° → 5.5° |

The jump at the border is expected: there is no Eq. 5 septal blend (brief step 9). Inside the RV the new field is
smoother than v5 at the 95th percentile.

**Run times:** Laplace 143 / 93 / 80 s; fibres 88 / 58 / 54 s (peak memory 0.56 GB and 2.0 GB). Data
runs/v51_2026-10-15/04_build/ (593 MB).

**Bugs found and fixed in my own code before these results** (none in v5):
- A5 compared identical vectors through arccos (2e-6° noise); it now compares the values.
- A7 compared whole 6-number rows instead of fibre vectors.
- The degenerate-frame guard above.
