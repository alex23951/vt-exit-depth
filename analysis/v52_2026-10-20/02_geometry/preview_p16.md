# P16: read-only preview for D36 (d), report 1 of 2

PC, 1-2 Nov 2026, from commit c0ced35 (the P16 scripts and outputs are committed with this report). Request:
notes/A/2026-10-22-v52-lock/d36/p16-request-2026-10-26.md (13,640 B, sha256 4bf5e513...66f2). Read only under D36's
hold: no beat, no activation, lead-field or ECG solve, no mesh built, nothing written into the manifest, and no v5.2
activation, ECG or lead-field value read. Every item is per heart in the order Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR. Nothing
is chosen. Figures marked "estimate" are estimates; the rest are counted or read from logged runs.

Scripts and outputs (analysis/v52_2026-10-20/02_geometry/): preview_p16_sites.py -> preview_p16_sites_<H>.json (items
(1)(a), (2)(a)-(b), (2)(d), (3)(a), (5), (6), (8), with every site's labels and counts); preview_p16_clearance.py ->
preview_p16_clearance_<H>.json ((1)(c)); preview_p16_torso.py -> preview_p16_torso.json ((4)(a)).

**Not in this report (report 2, once built under the hold):** (2)(c) the ladder as built; the ladder's and (h2)'s rows of
(5)(b)-(c); (10) A11's slab refit and acceptance A. None of these has been built yet.

## (1) Report 8

**(a) Its site.** v5.1 has 10 LV free-wall sites at 50 % depth in each heart (ids, phi, z, achieved depth and every
stored label are in preview_p16_sites_<H>.json, key 1a). Per heart, by id (phi deg, z, achieved depth; bazan_region;
AHA number from v5.1's label file):

- Y5HYEDL4: phi60_z0.25 (57.3, 0.250, 0.478; lv_apical_superior; 13), phi120_z0.25 (120.4, 0.252, 0.432;
  lv_apical_superior; 16), phi180_z0.25 (-171.6, 0.254, 0.504; lv_apical_inferior; 15), phi-120_z0.25 (-115.5, 0.242,
  0.457; lv_apical_inferior; 14), phi120_z0.5 (120.0, 0.497, 0.473; lv_apical_superior; 12), **phi180_z0.5** (-171.1,
  0.502, 0.477; lv_apical_inferior; 10), phi-150_z0.5 (-138.7, 0.501, 0.461; lv_basal_inferior; 9), phi120_z0.75 (120.9,
  0.748, 0.496; lv_basal_superior; 6), phi180_z0.75 (-175.6, 0.756, 0.472; lv_basal_superior; 4), phi-150_z0.75 (-139.6,
  0.758, 0.513; lv_basal_inferior; 4).
- 6G8DD8S5: phi60_z0.25 (52.2, 0.249, 0.487; lv_apical_superior; 14), phi120_z0.25 (121.2, 0.254, 0.562;
  lv_apical_superior; 16), phi180_z0.25 (-174.8, 0.251, 0.495; lv_apical_inferior; 15), phi-120_z0.25 (-111.5, 0.254,
  0.526; lv_apical_inferior; 15), phi120_z0.5 (119.1, 0.502, 0.498; lv_apical_superior; 12), **phi180_z0.5** (-175.6,
  0.502, 0.468; lv_basal_inferior; 11), phi-120_z0.5 (-112.7, 0.500, 0.509; lv_basal_inferior; 9), phi120_z0.75 (117.8,
  0.750, 0.491; lv_basal_superior; 6), phi180_z0.75 (-176.2, 0.748, 0.489; lv_basal_superior; 5), phi-120_z0.75 (-113.7,
  0.766, 0.522; lv_basal_inferior; 9).
- 7D98EVAR: phi60_z0.25 (54.5, 0.255, 0.498; lv_apical_superior; 13), phi120_z0.25 (116.3, 0.248, 0.537;
  lv_apical_superior; 16), phi180_z0.25 (-175.0, 0.251, 0.494; lv_apical_inferior; 15), phi-120_z0.25 (-115.6, 0.251,
  0.488; lv_apical_inferior; 15), phi120_z0.5 (119.5, 0.500, 0.532; lv_apical_superior; 12), **phi180_z0.5** (-175.0,
  0.498, 0.476; lv_basal_superior; 11), phi-135_z0.5 (-127.5, 0.502, 0.475; lv_basal_inferior; 10), phi120_z0.75 (119.2,
  0.742, 0.512; lv_basal_superior; 1), phi180_z0.75 (-175.6, 0.741, 0.497; lv_basal_inferior; 5), phi-135_z0.75 (-123.2,
  0.760, 0.527; lv_basal_inferior; 3).
- Gate-5 pool: none of the 30. The pool is each position's 90 % and 10 % sites (11.3 item 3; gate5count52.json).
- Gate 9: lv_free_wall_phi180_z0.5_d50 in each heart (bold above) is a gate-9 site (and one of (h1)'s 8 in the control
  heart, item (8)).
- Template site: lv_free_wall_original_d0 (nodes 313318 / 19052 / 277582) is not among them; it is not a v5.1 paced site
  and is at 0 % depth.
- C68: LABNOTES logs no C68 run or site. C68's note (26 Oct 11:40 UTC) never reached the PC (old thread could not resume;
  the relay of 1 Nov did not repeat it), so no site "C68 timed" is logged here.

**(b) Electrodes (A34's bank).** Not coded. No function in the repository displaces an electrode, takes a direction or
distance, recomputes V3, or caps a displacement. What exists:
- 08_torso.py (v5.1) places each of T13's 10 electrodes (RA, LA, LL, V1-V6, RL; data/torso/torsoModels/T_13_electrodes.csv)
  at the nearest node of the torso-skin mesh (snap 1.8-5.1 mm in Y5HYEDL4's v5.1 mesh).
- pose52.py's forward_check() measures the T13 electrodes against Kligfield's landmark rules, report only ("the primary
  electrodes are not moved").
- So none of 9.4's moves (16 / 32 mm, superior / inferior, 40 mm heavy build, Doste's 20 mm draws) and no cap against
  report 8's 0-32 mm factor (i) range exists in code. What it would take: a placement function (electrode, direction,
  distance -> a point on the skin) and V3's midpoint rule written to 9.4, plus A34's open values (Doste's
  configurations, LL / RL positions; P15). Not written; nothing chosen.

**(c) Torsos and clearance.** See the table at the end of this item (filled from preview_p16_clearance_<H>.json).
- Meshes now: none of T_24, T_20, T_17, T_01 exists as a volume mesh. The repository holds each of the 25 KIT shapes as
  a coarse skin surface (T_<nn>_torso_coarse_surface.vtk, about 3,000 nodes / 6,000 triangles) and an electrode file.
  The only heart-torso volume meshes are v5.1's three T13 meshes (v5.1 pose; data/biv/<H>/torso/full_nofast_blood_v51).
- Placement as coded: no code places a heart in T_24, T_20, T_17 or T_01. The only placement code is pose52.py (T13):
  identity rotation, translation t' so the LA+RA surface centroid lands where v5.1's rigid atrial fit put it; no
  registration or scaling. P16's numbers below use R-M8's reading (each heart keeps its CT-pose coordinates, x + t', in
  the shared frame; not moved).
- Node sets (as 9.1 and pose52.py): (a) the v5.2 simulation mesh (ventricles and sleeves, biv52), (b) every node of the
  cohort mesh (atria, valves, vessel stubs and the closed cavity surfaces that bound the blood). Boundary nodes of both,
  signed distance to the skin (negative = outside, by winding number).
- A33's 12 fixed poses: -10 / +10 deg about each torso axis and -10 / +10 mm along each, about the ventricular centroid
  (mean of the biv52 node coordinates at the CT pose; no other pivot is coded, item (d)).
- Combined pose: worst clearance anywhere in +-10 deg / +-10 mm on all six axes (rotations applied as Rz Ry Rx about the
  same pivot, then the translation): a 3^3 x 3^3 grid (-10, 0, +10 on each axis) on the candidate nodes (convex-hull
  vertices plus the 3,000 boundary nodes nearest the skin), then bounded L-BFGS-B from the three worst grid poses, and
  the result re-checked on every boundary node. A local search: it may miss a worse pose (estimate of its reach only).

Signed clearance in mm (negative = outside the skin). CT pose: smallest over the v5.2 simulation mesh / over the cohort
mesh, and boundary nodes outside the skin. A33's 12 fixed poses: smallest of the 12, and every pose under 9.1's 5 mm by
name. Combined: worst within +-10 deg / +-10 mm on all axes (local search; where a fixed pose is worse, that value is
given, marked *). T_13 (A33's own torso) is added for reference.

| Heart, shape | CT pose (sim / cohort; outside) | Fixed poses: smallest; under 5 mm | Combined worst |
|---|---|---|---|
| Y5HYEDL4 T_24 | -2.17 / -2.17; 798 outside | -11.06; 11 of 12 (all but +10 mm y) | -11.06* (search -7.18) |
| Y5HYEDL4 T_20 | 17.07 / 17.07 | 9.64; none | -3.87 |
| Y5HYEDL4 T_17 | 1.35 / 1.35 | -8.33; 11 of 12 (all but +10 mm y) | -9.80 |
| Y5HYEDL4 T_01 | 45.69 / 45.69 | 36.10; none | 27.82 |
| Y5HYEDL4 T_13 | 29.19 / 29.19 | 19.39; none | 10.21 |
| 6G8DD8S5 T_24 | 12.13 / 9.31 | 1.26; -10 mm y 1.26, +10 deg y 3.78, +10 deg z 1.62, +10 mm z 3.44 | -2.70 |
| 6G8DD8S5 T_20 | 23.50 / 21.05 | 13.61; none | -1.28 |
| 6G8DD8S5 T_17 | 21.69 / 20.51 | 10.90; none | -0.68 |
| 6G8DD8S5 T_01 | 59.25 / 55.84 | 46.34; none | 28.51 |
| 6G8DD8S5 T_13 | 40.64 / 36.57 | 27.67; none | 8.70 |
| 7D98EVAR T_24 | 12.74 / 12.74 | 4.70; -10 mm y 4.70 | -1.23 |
| 7D98EVAR T_20 | 23.87 / 23.87 | 16.32; none | 0.71 |
| 7D98EVAR T_17 | 18.44 / 18.44 | 8.51; none | -0.69 |
| 7D98EVAR T_01 | 55.72 / 55.72 | 46.06; none | 35.51 |
| 7D98EVAR T_13 | 39.20 / 39.20 | 29.83; none | 18.07 |

- P15 l.434-435 confirmed: Y5HYEDL4 fails at the CT pose in T_24 (798 boundary nodes outside the skin, worst 2.17 mm out)
  and in T_17 (1.35 mm); every other pair clears 9.31-55.84 mm (cohort nodes; 6G8DD8S5 T_24 the closest, T_01 the
  farthest).
- Under 9.1's 5 mm at A33's fixed poses: Y5HYEDL4 in T_24 and T_17 (11 of 12 poses each); 6G8DD8S5 in T_24 (4 poses);
  7D98EVAR in T_24 (1 pose, -10 mm y, 4.70 mm). None in T_20, T_01 or T_13.
- Combined poses within the box reach the skin or beyond in T_24, T_20 and T_17 in all three hearts (7D98EVAR T_20
  0.71 mm); T_01 and T_13 stay above 5 mm (worst 8.70 mm, 6G8DD8S5 in T_13). The combined values come from a local
  search and may understate the worst case; poses are in the JSON.
- Pivot (ventricular centroid, torso mm): 44.75, -69.28, -28.92 / 69.74, -43.38, -15.20 / 60.12, -52.62, -16.31. Run time
  66 / 41 / 41 min (one process).

**(d) Pose (A33's code).** Not coded. No code rotates or translates the heart about any axis or pivot. pose52.py applies
the CT pose only (identity rotation; translation in mm; torso frame +x left, -y anterior, +z superior). No pose within
+-10 deg / +-10 mm can be applied by existing code, the fixed set included.

**(e) Helix.** fibres52.py run(), the frame() step (LV side; D19b frame, D20a/D20b blend):
alpha = (1 - b)(66 - 107 w) + b (+90 (1 - w)), with w the LV transmural coordinate (0 endo, 1 epi) and b the outflow blend
clamp((z - 0.80) / 0.20, 0, 1)(1 - w_LV); f = cos(alpha) c + sin(alpha) l. So +66 deg at the endocardium and -41 deg at
the epicardium on the LV side, 90 (1 - w) inside the outflow blend. The RV keeps v5.1's rows (Doste) bit-identical, and
the pulmonary sleeves are circumferential. The two ends are constants in the code (66, 107), not inputs: setting either
end per sample would need a code change (and the RV ends are v5.1's stored rows). One fibre build: 1.0 min (Y5HYEDL4)
and 1.7 min (6G8DD8S5 and 7D98EVAR together), 21 Oct (LABNOTES).

**(f) Speeds and conductivities (logged runs only).**
- R4.1 slab refit with acceptance A (step 3, 21 Oct, one process, both speed sets): 89 s on the 2-ring stencil; 101.5 s
  with the 3-ring stencil added. Peak memory was not logged. A11's: report 2.
- In-heart graph build (step 3, 21 Oct): 4.4 min for the three hearts together, peak 3.2 GB (Y5HYEDL4 2-ring;
  6G8DD8S5 and 7D98EVAR 3-ring). P15's probes: coupled-matrix build 3.5 / 10.7 / 11.7 s; set-up plus one assembly
  1.19 / 2.71 / 2.36 GB.
- A new speed set adds no graph build on the same stencil: graph52.py caches the topology and edge q, and applies speeds
  and factors at load ("never cached"). It adds its slab refit (about 1.5-2 min, as step 3's) and, if a heart passes on
  a stencil it does not already have (for example Y5HYEDL4 on 3-ring), that stencil's topology build (part of the
  4.4 min above; estimate 1-2 min per heart). The per-beat matrix assembly is unchanged.
- Atrial-wall conductivity (R3.3): not coded. v5.1's lead-field build (conductor51.py leadfield()) has three regions:
  heart (ventricles, tag 1, anisotropic sigma from the speeds), torso 0.2 S/m and blood 0.7 S/m; v5.1's torso mesh has no
  atrial wall. v5.2's step-5 code (heart-torso mesh with atria, R3.3) is not written, so neither a fixed number nor a
  rule from the sigma it is given is coded.

**(g) Costs (logged runs, then arithmetic).**
- One graph-engine activation solve: no v5.2 solve has run. Logged v5.1: about 2 s graph in a 4.6 s network beat
  (1.35 GB). With v5.2's per-beat matrix assembly (3.5 / 10.7 / 11.7 s, P15 probe): about 5.5 / 13 / 14 s (estimate).
- One heart-torso mesh build: 26 min (9 Oct re-pose pipeline, LABNOTES; P15). Disk about 1.1 GB per mesh (v5.1's
  .elem 436 MB, .lon 579 MB, .pts about 60 MB; Y5HYEDL4).
- One lead-field set (v5.1, 18 Oct; leadfield51_<H>.json): 3 openCARP runs of 3 leads, 2 MPI processes, light AMG
  options, watchdog 900 MB: 8.1 / 6.3 / 6.7 min; peak system memory 6.45 / 5.83 / 5.88 GB; disk 47 / 47 / 42 MB.
- Forming one beat's ECG from a set: about 3.3 s at v5.1's window (decision 8's 579 ECGs); about 9-12 s at v5.2's
  window (P15, estimate); one pseudo-Vm projected onto 56 sets took 4.6 s (P15).
- 1,024 activations per heart: 1.6 / 3.7 / 4.0 h single process (estimate); maps about 1.4 GB per heart (P15's
  38 GB per 27,000 beats).
- 1,792 lead-field sets per heart: 242 / 188 / 200 h at 2 processes, run alone (10 / 7.8 / 8.3 days; 26 days for the
  three); disk 84 / 84 / 75 GB. Held at the primary's sigma and fibres, 1,024 per heart: 138 / 108 / 114 h; 48 / 48 /
  43 GB. Single-process timing (section 13's rule) is unmeasured (P15 l.507).
- 512 heart-torso meshes per heart: 222 h per heart (9.2 days; 28 days for three); disk about 0.56 TB per heart if kept
  (estimate).
- ECGs: 1,792 per heart at 9-12 s: 4.5-6 h per heart (estimate; less with a shared pseudo-Vm).

**(h) Localisation.** None. No code holds a library of site ECGs with a metric that returns a site or a distance.
"Pace-map convention" in v5.1's scoring code (report_040.py, rescore040_51.py, tableA51.py, ecg_side.py) is an onset
convention (stimulus onset, clean ECG) for the depth criteria, not localisation.

## (2) Report 7

**(a) Site sets (per heart).** v5.1 paced 144 / 144 / 144; report 7's displaced points 288 / 288 / 288 (144
transmural, 144 tangential); gate-5 fill 66 / 66 / 60; cusp-crescent 4 / 4 / 4; summit-reanchored 8 / 8 / 8;
supravalvar 3 / 3 / 3; D25 focus 1 / 1 / 1; ladder not built. Report 26's grid points: not placed; they come from the
D25 focus beat, which the hold keeps waiting (at most 18 per heart); left out of (b).
- Snapped node coordinates: no set stores coordinates; every entry stores its node index on biv52 (coordinates from
  biv52.pts).
- Nominal step: the displaced points store the rule (4 mm, D33, in the step-2 report) and the achieved move
  (moved_mm), not a per-point nominal step.
- APD w: only the transmural displaced points store one (the parent site's, site_w_apd); no other set stores it (the
  node values are in data/biv/<H>/v52/apd52.npz).
- Depth: v5.1 sites (target and achieved), gate-5 fill and summit-reanchored (target); displaced points through their
  parent (the transmural ones also store site and node d_s); cusp, supravalvar and focus store none.
- Region labels: v5.1 sites (bazan_region, bazan_region_v1, region_study); gate-5 fill (region_filled, region_of_site,
  aha_segment); focus (AHA_segment); the others none.

**(b) Pair counts (3D distance between site nodes; bins 0-2 / 2-4 / 4-6 / 6-10 / 10-20 / 20-40 mm).**
- (i) Among the 144: Y5HYEDL4 71 / 77 / 43 / 67 / 246 / 1,833; 6G8DD8S5 63 / 71 / 48 / 76 / 381 / 2,176; 7D98EVAR 62 /
  83 / 58 / 51 / 327 / 2,180. Nearest neighbour among the 144 (median, smallest): 1.79, 0.84 / 1.89, 0.71 / 1.81, 0.79 mm
  (the depth neighbours on one line).
- (ii) Each v5.1 site with its own displaced points (288 pairs): 2 / 152 / 134 / 0 / 0 / 0; 3 / 152 / 133 / 0 / 0 / 0;
  1 / 165 / 122 / 0 / 0 / 0. The ladder's pairs: report 2.
- (iii) All built sets together (514 / 514 / 508 points): 371 / 669 / 1,137 / 970 / 3,655 / 22,528; 341 / 669 / 1,075 /
  936 / 4,674 / 26,426; 374 / 726 / 1,119 / 909 / 4,067 / 25,054.

**(c) The ladder as built.** Report 2.

**(d) Regions.** Each v5.1 site's labels, by id, are in preview_p16_sites_<H>.json (key 2d_labels_by_site): family,
name, bazan_region, bazan_region_v1, region_study, AHA segment and number (v5.1's pilot_site_labels.csv), gate-5 region
(11.3 map, pool sites only; "no region" otherwise) and the 8.1 RVOT label (P14, RVOT sites only).
- Label values that state one of the six regions outright, matched by the words they contain (rvot, lvot, cusp, summit,
  free wall, septum / septal): family 6 values (rvot, aortic_cusp, lv_summit, lv_free_wall, rv_free_wall, lv_septum),
  name 31, bazan_region and bazan_region_v1 1 each (rvot), region_study 3, AHA segment 3 (septal, anteroseptal,
  inferoseptal), 8.1 label 1 ("septal component"); gate-5 region none.
- Sites per region: RVOT 8 / 8 / 8; LVOT 0 / 0 / 0 (no label names it); cusps 8 / 8 / 8; summit 8 / 8 / 8; free walls
  80 / 80 / 80; septum 53 / 55 / 55.
- More than one region: 21 / 23 / 19 sites, in four combinations: RVOT + septum (rvot_septal, and 8.1 "septal
  component"), RVOT + free walls + septum (rvot_free_wall sites that 8.1 labels "septal component"), cusps + septum
  (aortic cusp sites whose AHA segment is septal), free walls + septum (free-wall sites whose name or AHA segment says
  septal, e.g. "apical anteroseptal lv free wall").
- None: 12 / 12 / 8 sites, all lv_vein_course (Y5HYEDL4 and 6G8DD8S5: basal_ring_anterolateral, basal_ring_lateral,
  proximal_aiv; 7D98EVAR: the first two). Ids in the JSON.

**(e) Cycle length and single beats.**
- Each report-7 beat is set up as one paced beat from one stimulus, with no train: heart52.py (the v5.2 graph-engine
  driver) has no cycle length or pacing train. Beats are computed noiseless; v5.1's noise (10 uV) was added only in its
  rescoring code, not in a beat.
- Templates: R1.2's templates come from single-cell runs at CL 1000 ms to steady state (cell52.py, BCL = 1000;
  l.2850). The splice-template and ECG code of the v5.2 graph engine are not written yet (heart52.py computes
  activation only), so "uses CL 1000 templates" holds by the lock's text, not yet by code.
- (h1)'s monodomain beats: v5.2's step-10 code is not written. Step 10's settings (l.1981-1986) give ToR-ORd with the R1.3
  blend, R1.4 and R1.5, and name no starting cell state or pacing cycle length. v5.1's mono51.py started each beat from
  openCARP's built-in Tomek initial values (no state file, no pre-pacing), with one stimulus.
- No v5.2 code paces a train at CL 600; CL 600 appears only as the RE+ subset, deferred with step 11.

## (3) Report 26

**(a) D25's set-up.** Focus node 106732 / 251656 / 181680 (step-2e manifest, intramural52_focus): confirmed. D25's grid
code is not written (no grid, geodesic-spacing, low-gradient or drop function in the repository), and no grid node or
breakthrough site is placed (the manifest holds none; its D25 entry reads "placed from the focus beat").

**(b) Yokokawa's form.** None. The repository has no Pearson-CC-plus-RMS score on averaged leads, no window, alignment
or filter chain for it, and no "fewer than 10 of 12 leads" rule. The only correlations in code are per-lead checks of
one ECG method against another (13_fast_ecg.py, v5_adopted.py).

## (4) Report 22

**(a) The torso mesh as used now.** Only v5.1's heart-torso meshes exist (v5.2's step 5 is not built):
full_nofast_blood_v51, 1,983,222 / 1,640,909 / 1,709,957 nodes and 12,528,941 / 10,333,536 / 10,791,117 elements.
Built by 08_torso.py with meshtool: T13's coarse skin resampled to an 8 mm average edge (`resample surfmesh
-avrg=8000`), `generate mesh` with the ventricular boundary kept as a hole (`-holes=0,1 -prsv_bdry=1 -mode=1`), merged
with the heart; blood retagged 101 by conductor51.py. Edge lengths (per-element mean edge, mm; p5 / p50 / p95):

| Heart | Torso + blood, all | Near the heart (< 5 mm) | Far (> 20 mm) | Heart | Within 10 mm of an electrode (median, by electrode) |
|---|---|---|---|---|---|
| Y5HYEDL4 | 0.77 / 0.94 / 6.79 | 0.76 / 0.91 / 1.31 | 1.03 / 5.56 / 8.66 | 0.97 / 1.05 / 1.14 | 6.7-9.2 |
| 6G8DD8S5 | 0.78 / 0.96 / 7.31 | 0.77 / 0.92 / 1.33 | 0.99 / 6.08 / 8.76 | 0.97 / 1.05 / 1.13 | 7.0-9.1 |
| 7D98EVAR | 0.78 / 0.97 / 7.13 | 0.77 / 0.92 / 1.30 | 0.93 / 5.55 / 8.60 | 0.97 / 1.05 / 1.14 | 6.7-8.8 |

Most torso elements sit near the heart, so the overall median is about 1 mm; away from the heart it is about 5.6-6.1 mm,
and at the electrodes 6.7-9.2 mm (per electrode in preview_p16_torso.json).

No torso refinement for report 22 exists in the repository or LABNOTES (v5.1's included).

**(b) A refined torso, without building one (all estimates).** Torso nodes are about 1.6 / 1.3 / 1.3 M of the totals
above (heart about 0.38 M).
- (i) Typical torso edge halved throughout the torso: about 8x the torso elements, about 13 / 11 / 11 M nodes.
  meshtool: `meshtool resample mesh -msh=<mesh> -tags=100,101 -uniform=1 -outmsh=<out>` (one uniform split of the torso
  and blood elements; whether it keeps the heart interface conforming is unchecked), or regenerate with the skin at
  4 mm. Build about 3 h; disk about 8 GB; one lead-field set about 40-55 min and about 40-50 GB at 2 processes (scaled
  by nodes from 6.3-8.2 min at 5.8-6.5 GB): does not fit the PC's 7.9 GB.
- (ii) The near-heart edge (about 1 mm) carried out to the skin: a near-uniform 1 mm mesh of the 34.6 L torso, about
  290 M elements and 50 M nodes. meshtool: regenerate with the skin resampled to 1 mm (`resample surfmesh -avrg=1000`,
  then `generate mesh`), or `resample mesh -tags=100,101 -max=<near-heart edge>`. Build many hours to days, memory far
  beyond the PC; one lead-field set about 3-4 h and about 150-200 GB: does not fit the PC.
- Neither is chosen.

**(c) A34's bank as coded.** Not coded (item (1)(b)): no configuration exists in code, so none moves the whole
precordial set 2 cm vertically. As written (9.4), the bank's vertical moves are V1 and V2 only.

## (5) The three no-beat outputs

**(a)** lv_endo and rv_endo carry triangles (lv_endo.surf / rv_endo.surf), so an activated area can be summed from
triangle areas or per-node areas (a third of the adjacent triangles): lv_endo 45,467 / 41,355 / 43,982 triangles
(15,330 / 13,899 / 14,910 mm2), rv_endo 55,852 / 37,641 / 41,641 (18,893 / 12,679 / 14,103 mm2). No node is on both.
The septum lies on both surfaces: its LV face on lv_endo and its RV face on rv_endo (the lv_septum sites lie a median
5.3 / 5.6 / 5.9 mm from lv_endo and 2.5 / 2.7 / 2.7 mm from rv_endo).

**(b) Stimulated node sets holding at least one lv_endo or rv_endo node** (8.7 sets rebuilt exactly as sites52.py;
every count matches the manifest). Format: with either (with lv_endo / with rv_endo), of n.

| Set, depth label | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| v5.1 paced, 10 % (n 36) | 35 (24 / 11) | 32 (21 / 11) | 34 (23 / 11) |
| v5.1 paced, 50 % | 1 (1 / 0) | 1 (0 / 1) | 1 (0 / 1) |
| v5.1 paced, 75 % | 2 (1 / 1) | 2 (0 / 2) | 4 (0 / 4) |
| v5.1 paced, 90 % | 9 (1 / 8) | 9 (1 / 8) | 8 (1 / 7) |
| displaced transmural, parent 10 % (n 36) | 0 | 0 | 0 |
| displaced transmural, parent 50 % | 23 (13 / 10) | 17 (8 / 9) | 21 (10 / 11) |
| displaced transmural, parent 75 % | 14 (3 / 11) | 11 (1 / 10) | 15 (4 / 11) |
| displaced transmural, parent 90 % | 11 (2 / 9) | 10 (0 / 10) | 11 (2 / 9) |
| displaced tangential, parent 10 % (n 36) | 33 (22 / 11) | 27 (17 / 10) | 30 (20 / 10) |
| displaced tangential, parent 50 % | 1 (1 / 0) | 1 (0 / 1) | 2 (0 / 2) |
| displaced tangential, parent 75 % | 2 (1 / 1) | 4 (0 / 4) | 3 (0 / 3) |
| displaced tangential, parent 90 % | 9 (1 / 8) | 9 (1 / 8) | 8 (1 / 7) |
| gate-5 fill, 10 % (n 33 / 33 / 30) | 31 (31 / 0) | 17 (17 / 0) | 25 (25 / 0) |
| gate-5 fill, 90 % | 0 | 0 | 0 |
| cusp-crescent (n 4) | 0 | 1 (0 / 1) | 0 |
| summit-reanchored 10 / 50 / 75 / 90 % (n 2 each) | 1 / 0 / 0 / 0 | 2 / 1 / 0 / 0 | 2 / 0 / 0 / 0 |
| supravalvar (n 3) | 0 | 0 | 0 |
| D25 focus (n 1) | 0 | 0 | 0 |

The ladder's points and (h2)'s 2.5 mm sets: report 2.

**(c) PMJ coupling nodes.** Yes: network_v52.npz gives each network node its muscle node ('nodes') and lists the
junctions ('pmj'), so each PMJ couples at one node, nodes[pmj] (heart52.py moves RV junctions on the infundibulum cut to
the cut copies). PMJs 3,605 / 3,014 / 3,251; distinct coupling nodes 3,585 / 3,011 / 3,243 (RV junctions on copies 0 /
7 / 0). Stimulated sets holding a coupling node: v5.1 sites 15 / 13 / 12 (all at 10 % in Y5HYEDL4; 6G8DD8S5 12 at 10 %
and 1 at 90 %; 7D98EVAR 8 / 1 / 1 / 2 at 10 / 50 / 75 / 90 %); report 7's displaced points 33 / 32 / 31 (transmural 23 /
20 / 19, tangential 10 / 12 / 12). Per depth in the JSON. The ladder's points: report 2.

## (6) The bias-run sites

- The 9 gate-9 sites per heart: lv_free_wall_original_d0 (template; not a v5.1 site, so it carries no stored label),
  lv_free_wall_phi180_z0.5_d50 / _d90, lv_septum_phi0_z0.5_d10 / _d50 / _d90, rv_free_wall_q50_z0.5_d10 / _d50 / _d90.
- Uncovered regions of each heart's v5.1 grid, by scheme (count of v5.1 sites in the region; the 8 labelled gate-9 sites
  only):
  - Family (also v5.1's bias-run plan, below): aortic_cusp 8, lv_summit 8, lv_vein_course 12, rvot 8, in all three.
  - Six regions of (2)(d): RVOT 8, cusps 8, summit 8, in all three (LVOT has no site under any label).
  - region_study: Y5HYEDL4 aortic_cusp 8, lv_apical_superior 16, lv_basal_inferior 12, lv_basal_superior 16, lv_summit
    8, lv_vein_course 12, rv_apical_superior 4, rv_basal_inferior 12, rv_basal_superior 4, rvot 8; 6G8DD8S5
    aortic_cusp 8, lv_apical_inferior 12, lv_apical_superior 20, lv_summit 8, lv_vein_course 12, rv_apical_superior 4,
    rv_basal_inferior 12, rv_basal_superior 8, rvot 8; 7D98EVAR aortic_cusp 8, lv_apical_inferior 12,
    lv_apical_superior 16, lv_basal_inferior 20, lv_summit 8, lv_vein_course 12, rv_apical_inferior 12,
    rv_basal_superior 8, rvot 8.
  - bazan_region, bazan_region_v1, AHA segment, gate-5 region, 8.1 label and name: in the JSON (key 6_uncovered).
- Bias-run list and seed in the repository: yes. analysis/v51_2026-10-15/08_monodomain/bias_sites51.json, commit
  6cdbabc (19 Oct 2026, "seed-0 draw of one site per region per heart"); rule "numpy default_rng(0); hearts in HEARTS
  order; families in BIAS_FAMILIES + COVERED order; one id from the sorted candidates"; regions = site families. Drawn
  ("new", the 4 families with no gate-9 site; 12 beats): Y5HYEDL4 rvot_septal_z_d75, aortic_cusp_rcc_z_d50,
  lv_summit_superior_z_d10, lv_vein_course_basal_ring_anterolateral_z_d90; 6G8DD8S5 rvot_free_wall_z_d10,
  aortic_cusp_lcc_z_d50, lv_summit_superior_z_d75, lv_vein_course_basal_ring_lateral_z_d90; 7D98EVAR rvot_septal_z_d90,
  aortic_cusp_rcc_z_d50, lv_summit_superior_z_d50, lv_vein_course_basal_ring_lateral_z_d75. Also drawn ("covered", one
  gate-9 site per covered family): lv_free_wall_original_d0 / phi180_z0.5_d90 / phi180_z0.5_d50, lv_septum_phi0_z0.5
  d10 / d50 / d90, rv_free_wall_q50_z0.5 d10 / d50 / d10.
- Candidates: every v5.1 site in an uncovered region is a v5.1 paced site whose graph beat is in the ledger (E holds all
  144 per heart); the ids per region and scheme are in the JSON (key 6_uncovered_candidates).
- The site C68 timed: not logged in LABNOTES (item (1)(a)).

## (7) Electrode potentials

The lead-field sets as built give lead combinations only: v5.1's sets (conductor51.py, 15_conductor.py) solve the
lead fields of I, II, III and V1-V6 (V leads against Wilson's terminal) in three openCARP runs of three leads, and derive
aVR, aVL and aVF; the stored weights (ecgW_*.npz) are 12 x nodes. No electrode's potential against a fixed reference is
stored. Step 5's v5.2 code is not written. What per-electrode potentials would take (estimate): one lead field per
electrode against one fixed reference (8 or 9 for RA, LA, LL, V1-V6, plus one per moved A34 electrode), which at three
per run is three runs per set, as now (about 6.3-8.2 min and 5.8-6.5 GB per set at 2 processes, disk about 45 MB), with
the 12 leads formed by subtraction; it needs a custom lead definition in place of carputils' 12-lead setup (not written).

## (8) (h1)'s sites

Confirmed in Y5HYEDL4 (all present in data/biv/Y5HYEDL4/sites.json): lv_free_wall_phi180_z0.5_d50,
lv_free_wall_phi180_z0.5_d90, lv_septum_phi0_z0.5_d10, lv_septum_phi0_z0.5_d50, lv_septum_phi0_z0.5_d90,
rv_free_wall_q50_z0.5_d10, rv_free_wall_q50_z0.5_d50, rv_free_wall_q50_z0.5_d90. The ninth gate-9 site,
lv_free_wall_original_d0, is the template site, not a ledger site.

## (9) The breath-hold phase (C67 (9))

The cohort data as the repository holds them give no breath-hold or respiratory phase for any of the three hearts.
Logged in LABNOTES at PC clock 22:36 on 1 Nov 2026 (21:36 UTC), with what was checked (the case archives hold meshes and
the cohort's simulation files, no imaging metadata; dataset_info.csv's columns are Case, Status, Sex, Translation_case;
the cohort paper is not held, so its methods text was not read).

## (10) A11 and the ladder

A11's slab refit and acceptance A: not yet run (report 2). Arithmetic for 3,456 more A11 activation re-solves and ECGs
on A11's own 3 lead-field sets (estimate, from (1)(g)): 1,152 per heart x (activation about 5.5 / 13 / 14 s + ECG
9-12 s) = about 4.6-5.6 / 7.0-8.0 / 7.4-8.3 h single process, about 19-22 h in all; no new lead field.
