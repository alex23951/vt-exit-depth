# P16: read-only preview for D36 (d), report 2 of 2

PC, 2 Nov 2026, from commit b25a154 (set-up built under D36's hold; this report and its LABNOTES lines are committed
next). Request: notes/A/2026-10-22-v52-lock/d36/p16-request-2026-10-26.md (13,640 B, sha256 4bf5e513...66f2). Report 1:
preview_p16.md (commit 058fc65). This report gives the items report 1 left for after the set-up: (2)(a)-(b) with the
ladder, (2)(c), the ladder's and (h2)'s rows of (5)(b)-(c), and (10). Every item is per heart in the order Y5HYEDL4 /
6G8DD8S5 / 7D98EVAR. Nothing is chosen. No beat, no activation, lead-field or ECG solve has run.

Built since report 1 (LABNOTES 2026-11-02_v52_02_ladder and 2026-11-02_v52_03_A11slab):
- **D36 (g), the ladder:** ladder52.py placed 1,152 / 1,152 / 1,152 points and wrote them into the step-2 manifests
  (data/biv/<H>/v52/sites52.json, family "ladder", with capture rows) in 4.4 min, one process. The manifests as
  sites52.py wrote them are kept as sites52_pre_ladder.json, and every run of ladder52.py starts from them.
- **D36 (h2), 2.5 mm sets:** 576 sets in the control heart (manifest key "stim25_sets", node lists in biv52cut ids).
- **A11's slab refit and acceptance A** (a11slab52.py): passes on each heart's primary stencil; params/v52_graph_factors_A11.json.
- **Not built yet: step 5's heart-torso meshes and any lead field.** After Alex asked on 2 Nov (01:12 UTC) for a
  realistic heart position, the lock thread found the primary's CT pose in T13 inside the normal adult range (29.2 /
  36.6 / 39.2 mm under the skin) and released step 5 for the primary only (relayed 01:22 UTC); it is the next build.
  No arm-pose mesh (A32, A33, A37) or report-8 mesh is built until the pose deviation is answered.

Outputs (analysis/v52_2026-10-20/): 02_geometry/ladder52_<H>.json (every number below for (2) and (5), with per-step,
per-parent-depth and per-parent-family tables and the per-site direction checks); 03_speeds/a11slab52.json ((10)).

## (2) Report 7

**(a) Site sets.** The ladder: 1,152 / 1,152 / 1,152 points (144 sites x 8 steps). Each ladder entry stores its node
on biv52 and that node's coordinates (xyz_mm), the unsnapped point (unsnapped_xyz_mm), the step name and nominal length
(nominal_mm), the unit direction, the achieved 3D distance from its site (moved_mm) and the snap distance, APD w at the
site and at the node and their difference, the parent's id, family and depth target, and whether the unsnapped point
lay inside the myocardium; its capture row stores the stimulated node count, validity, muscle fraction, and its
lv_endo, rv_endo and PMJ contacts. A ladder point carries no region label of its own: its parent's labels apply by
parent id. The other sets are as report 1 gives them. Report 26's grid points are still not placed (the D25 focus beat
is held).

**(b) Pair counts with the ladder** (3D distance between snapped nodes; bins 0-2 / 2-4 / 4-6 / 6-10 / 10-20 / 20-40 mm).
- (i) Among the 144: unchanged from report 1.
- (ii) Each v5.1 site with its own displaced and ladder points (1,440 pairs per heart): 221 / 442 / 348 / 311 / 118 / 0;
  255 / 405 / 350 / 311 / 119 / 0; 231 / 441 / 345 / 295 / 128 / 0. (The 10-20 mm pairs are the 10 mm steps, achieved
  up to 12.3 mm.)
- (iii) All built sets together (1,666 / 1,666 / 1,660 points): 2,056 / 6,211 / 9,016 / 16,806 / 39,836 / 232,902;
  1,970 / 5,942 / 8,722 / 16,942 / 54,925 / 282,219; 2,081 / 6,464 / 9,192 / 16,660 / 50,381 / 273,654.

**(c) The ladder as built.** None of the 3,456 points fails 8.7's capture (at least 4 stimulated nodes), so none is
excluded: at most 1,152 / 1,152 / 1,152 ladder beats. Directions as coded (model details mine where D36 is silent):
taken at the site node from the element whose centroid is nearest the node, as sites52.py's displaced set; +f
agrees with report 7's held fibre directions and the D33 direction with report 7's transmural directions within
0.0005 deg; |f . s| <= 1e-5.

Achieved 3D distance from the site, mm: median (smallest-largest).

| Step | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| fibre 2 mm | 2.02 (0.68-2.85) | 1.97 (0.80-2.49) | 1.96 (1.30-2.54) |
| fibre 6 mm | 5.95 (3.90-7.11) | 5.96 (3.45-6.51) | 6.00 (3.22-6.58) |
| fibre 10 mm | 9.96 (8.29-11.76) | 9.90 (5.96-12.34) | 9.96 (5.28-10.81) |
| cross-fibre 2 mm | 2.01 (0.73-2.58) | 1.92 (1.24-2.46) | 2.00 (1.55-2.61) |
| cross-fibre 4 mm | 3.99 (1.50-4.56) | 4.01 (1.77-4.52) | 4.00 (2.94-4.50) |
| cross-fibre 6 mm | 6.04 (0.88-6.59) | 6.04 (2.90-6.50) | 5.96 (3.76-6.56) |
| cross-fibre 10 mm | 9.92 (7.41-11.14) | 9.90 (4.43-10.48) | 9.96 (4.92-10.56) |
| transmural 2 mm | 1.98 (1.28-2.77) | 1.94 (1.07-2.91) | 1.98 (1.37-2.79) |

Change in APD w (node minus site): median, the change of largest size, median of the absolute change; then the count
whose unsnapped point left the myocardium (of 144).

| Step | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| fibre 2 mm | +0.000, +0.45, 0.010; 28 | +0.000, -0.15, 0.010; 26 | +0.000, +0.45, 0.013; 27 |
| fibre 6 mm | +0.007, +0.61, 0.027; 38 | +0.011, -1.00, 0.041; 28 | +0.018, +0.67, 0.039; 33 |
| fibre 10 mm | +0.079, +0.95, 0.127; 49 | +0.049, -1.00, 0.101; 50 | +0.077, +1.00, 0.133; 47 |
| cross-fibre 2 mm | +0.000, +0.62, 0.013; 26 | +0.000, +0.19, 0.010; 22 | +0.000, +0.58, 0.015; 23 |
| cross-fibre 4 mm | +0.000, +0.86, 0.017; 25 | +0.000, +0.41, 0.018; 25 | +0.000, +1.00, 0.022; 27 |
| cross-fibre 6 mm | +0.004, +1.00, 0.038; 28 | +0.004, +0.63, 0.044; 29 | +0.016, +1.00, 0.049; 31 |
| cross-fibre 10 mm | +0.061, +1.00, 0.091; 52 | +0.044, +1.00, 0.111; 46 | +0.069, +1.00, 0.123; 52 |
| transmural 2 mm | -0.140, +0.76, 0.257; 3 | -0.118, +1.00, 0.217; 6 | -0.139, +1.00, 0.263; 5 |

Read with the tables: a point whose unsnapped position left the wall is snapped to the nearest unused node, which can
lie close to its site (Y5HYEDL4 cross-fibre 6 mm at 0.88 mm) or across a thin wall (an APD w change of 1.0), so the
nominal step and the achieved distance can differ widely at single points; the per-point values are in the manifest.
Muscle fraction of the 1.5 mm ball (median, 10th centile, smallest): 0.907, 0.491, 0.113 / 0.961, 0.494, 0.073 / 0.907,
0.490, 0.123.

**Step 2e's 8.8 placement checks, the ones that apply to steps from a site.** RVOT parents (64 points per heart):
36 / 58 / 36 lie more than 10 mm below the pulmonary valve (range 1.35-16.67 / 6.18-17.55 / 0.48-17.03 mm; none above
it), as do 7 / 8 / 8 of the 8 parent v5.1 RVOT sites themselves (9.95-15.59 / 13.43-16.53 / 10.14-15.71 mm, step 2e's
report). Aortic-cusp parents, distance to the PV rim (min, median, max): LCC 7.75, 13.05, 19.30 / 8.08, 18.94, 23.18 /
8.66, 16.99, 22.27 mm; RCC 21.08, 28.61, 30.52 / 24.29, 29.53, 32.96 / 23.78, 30.12, 32.85 mm (8.8: PV-LCC 5 +- 3,
PV-RCC 11 +- 5; the parents' own distances are step 2e's). 8.8's other checks place site families, not steps, and do
not apply.

**Four findings for the lock thread (nothing changed; each point stays as built):**
1. **Undefined transmural direction at one site.** In Y5HYEDL4, aortic_cusp_rcc_z_d90 has APD w = 1.0 on every element
   around its node, so APD w's gradient is zero and D33's direction does not exist. Report 7's own transmural point,
   built 22 Oct, already carries direction (0, 0, 0) and lies 1.07 mm from the site (the nearest unused node); the
   ladder's 2 mm transmural point does the same (1.29 mm). Both capture. Every other site has a non-zero gradient
   (smallest 0.013 per mm, 6G8DD8S5 lv_septum_phi0_z0.25_d50). Question: how should D33's step be defined where APD
   w's gradient is zero (for example: excluded as "direction undefined", or the fibre frame's transmural n = f x s)?
2. **Cross-fibre is not always in-wall by APD w.** The stored s is in-wall by construction relative to the fibres' own
   w (D19b's t_out), but at aortic-cusp sites APD w's gradient points elsewhere: |s . unit grad APD w| is above 0.3 at
   3 / 5 / 5 of the 8 cusp sites (0.48-0.94 / 0.33-0.95 / 0.31-0.99) and at two 6G8DD8S5 LV sites (0.43, 0.44); the
   median over all 144 sites is 0.015 / 0.015 / 0.015, and the RV rows reach at most 0.09 / 0.26 / 0.16. At those sites
   the +s steps move partly across the wall as APD w measures it.
3. **Points in the other ventricle's tissue.** 18 / 45 / 65 ladder points snap to a node that touches no element of
   their parent's ventricle: by parent, aortic cusp 12 / 11 / 12, RV free wall 5 / 30 / 31, LV septum 1 / 1 / 21, LV
   free wall 0 / 3 / 1. The RV free-wall ones mostly stay inside the wall (unsnapped point in the myocardium at 5 / 27 /
   27 of 5 / 30 / 31), so the wall itself crosses the LV-RV tag boundary there, as do 14 of 7D98EVAR's 21 septal ones;
   the cusp ones mostly left the wall (11 / 8 / 7 of 12 / 11 / 12; e.g. Y5HYEDL4 aortic_cusp_rcc_z_d10 +s 2-6 mm, in RV
   muscle). 8.7's capture is run against the parent family, as D36 says, so an LV-family point that lands in RV muscle
   stimulates RV muscle.
4. **RVOT depth below the valve:** see the 8.8 lines above; most RVOT-parent points sit over 10 mm below the PV
   because their parent sites already do.

## (5) The three no-beat outputs: the ladder's and (h2)'s rows

**(b) Stimulated sets holding at least one lv_endo or rv_endo node.** Ladder (1.5 mm sets), by parent depth 10 / 50 /
75 / 90 % (n 36 each), then the number of sets holding a PMJ coupling node, all depths ((c)):

| Step | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| fibre 2 mm | 35 / 1 / 4 / 9; PMJ 11 | 30 / 2 / 2 / 9; PMJ 11 | 31 / 2 / 3 / 8; PMJ 13 |
| fibre 6 mm | 31 / 1 / 1 / 9; PMJ 10 | 22 / 1 / 6 / 11; PMJ 4 | 26 / 1 / 4 / 8; PMJ 11 |
| fibre 10 mm | 17 / 2 / 9 / 10; PMJ 4 | 17 / 4 / 9 / 12; PMJ 12 | 11 / 2 / 8 / 10; PMJ 3 |
| cross-fibre 2 mm | 35 / 2 / 2 / 8; PMJ 15 | 30 / 2 / 2 / 9; PMJ 12 | 32 / 2 / 5 / 8; PMJ 16 |
| cross-fibre 4 mm | 31 / 2 / 5 / 7; PMJ 10 | 29 / 1 / 3 / 9; PMJ 11 | 28 / 1 / 5 / 8; PMJ 10 |
| cross-fibre 6 mm | 24 / 1 / 3 / 9; PMJ 12 | 20 / 1 / 6 / 9; PMJ 10 | 22 / 1 / 5 / 9; PMJ 7 |
| cross-fibre 10 mm | 12 / 1 / 10 / 10; PMJ 7 | 8 / 2 / 7 / 11; PMJ 7 | 10 / 3 / 7 / 7; PMJ 4 |
| transmural 2 mm | 1 / 10 / 7 / 3; PMJ 9 | 0 / 8 / 4 / 1; PMJ 3 | 0 / 10 / 7 / 2; PMJ 7 |

The lv_endo / rv_endo split of every cell is in ladder52_<H>.json (key 5b_5c). (h2)'s 2.5 mm sets, control heart, by
site depth (n 36 each), with either surface (lv_endo / rv_endo):

| Set (control heart, 2.5 mm) | 10 % | 50 % | 75 % | 90 % | PMJ (all depths) |
|---|---|---|---|---|---|
| base | 35 (24 / 11) | 11 (3 / 8) | 9 (1 / 8) | 9 (1 / 8) | 25 |
| transmural 4 mm (report 7) | 2 (0 / 2) | 28 (17 / 11) | 18 (7 / 11) | 14 (3 / 11) | 39 |
| fibre 4 mm (report 7) | 35 (24 / 11) | 8 (3 / 5) | 9 (1 / 8) | 9 (1 / 8) | 20 |
| cross-fibre 4 mm (ladder) | 35 (24 / 11) | 8 (3 / 5) | 11 (2 / 9) | 9 (0 / 9) | 23 |

Against the 1.5 mm base sets (report 1: 35 / 1 / 2 / 9 with either surface, 15 with a PMJ node), the 2.5 mm ball
reaches an endocardium from 11 rather than 1 of the 36 mid-wall (50 %) sites and holds a PMJ coupling node at 25 sites
rather than 15.

**(h2)'s sets as built.** 576 of 576 built and valid (no cross-fibre 4 mm point was excluded at 1.5 mm, so none drops
out); stimulated nodes median 80 (range 29-100) against 17 at 1.5 mm (median ratio 4.51; the volume ratio is 4.63);
every 2.5 mm set contains its point's 1.5 mm set, and none is smaller than the plain 2.5 mm ball (no cut or fibrous
layer clips it). Muscle fraction of the 2.5 mm ball: median 0.762, 10th centile 0.491, smallest 0.188. So at most 576
stim25 beats. heart52.py fixes the ball at 1.5 mm; the stim25 beats will need the stored node lists (or a radius
option) when beats are allowed.

**(c) PMJ coupling nodes in the ladder's sets:** 78 / 70 / 71 of 1,152 sets hold one (per step above).

## (10) A11 and the ladder

**A11's slab refit and acceptance A** (C67 (5); stencil by R-L9; LABNOTES 2026-11-02_v52_03_A11slab; 90.5 s in all,
peak memory 1.6 GB, one process). Speeds control 0.80 / 0.24 / 0.34, HF 0.80 / 0.173 / 0.235 m/s. Each heart passed on
its primary's stencil, so no other stencil was tried:
- Y5HYEDL4, 2-ring: factors 1.1624 / 1.0027 / 1.0121 (fibre / sheet / normal; primary 1.1247 / 1.0019 / 1.0265);
  PASS: principal 1.0019 / 0.9986 / 1.0000 (limit +-1.5 %), rays worst 2.03 % (3 %), rotating wall 0.9933-0.9945
  (+-2 %); 34.6 s.
- 6G8DD8S5 and 7D98EVAR (one HF speed set), 3-ring: factors 1.1821 / 1.0012 / 1.0041 (primary 1.1158 / 1.0008 /
  1.0092); PASS: principal 1.0107 / 0.9997 / 1.0005, rays worst 2.69 %, rotating wall 0.9972-0.9978; 55.9 s. The fibre
  principal and the rays pass with less margin than the primary's (1.0022, 1.44 %).
- No fail on either stencil, so no stop.

**Arithmetic for 3,456 more A11 activation re-solves and ECGs on A11's own 3 lead-field sets** (estimate, from report
1's (1)(g); A11 keeps the primary's stencils, so the per-beat activation cost is the primary's): 1,152 per heart x
(activation about 5.5 / 13 / 14 s + ECG 9-12 s) = about 4.6-5.6 / 7.0-8.0 / 7.4-8.3 h single process, about 19-22 h
in all; no new lead field (A11's 3 sets are needed for its E beats either way). None of this runs while the hold
stands, and the ladder joins A11's list only if (d)'s follow-up deviation adds it (R-T1).
