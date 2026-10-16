# Deep audit, PC half (13-14 Oct 2026)

Read-only audit of the pipeline code, the saved results and the meshes on the PC. Nothing in the model, the results,
LABNOTES, CLAUDE.md or git was changed. Everything new is in this folder: audit scripts `a01`-`a11` with their JSON/CSV
outputs, `findings.csv` (32 findings) and this report.

**Subagents:** I started three independent second-read subagents on 13 Oct.
- The Purkinje/solver reviewer finished, and its findings are merged below (marked "subagent").
- The ECG-chain and geometry reviewers stopped early on a usage limit. I did those parts myself.

## Summary in plain language

**Did the results hold up?**
- Every Aim 1 gate value reported on 13 Oct reproduces exactly from the saved per-site files with my own code (section B9).
- 63 of 67 numbers I spot-checked across 18 analysis folders match their own data files. Of the 4 that don't, one is a rounding difference; the other three are old 4 Oct fast-layer numbers computed in the cloud (section E).
- I found no fabricated or unsupported numbers.

**The meshes are sound.**
- No inverted or broken elements.
- My cavity volumes agree with the cohort authors' own volumes to within 1-2 %.

**What is wrong or questionable.**
1. **F01 (speed).** The v5 model runs on a fast shortcut solver (the "graph"). Measured the way you would on a map, it conducts too slowly along fibres:
   - Control heart: 0.56 instead of 0.60 m/s.
   - The two heart-failure hearts: 0.50 instead of 0.60 m/s. Only their cross-fibre speed was meant to be slowed.
   - The earlier v3 grids were mostly openCARP's own solver, which gives 0.59 m/s. So part of the v3 → v5 changes (for example the HF His-beat QRS rising to 142 ms) is a solver effect, not the intended physiology.
2. **F02 (labels).** The rotational coordinate used to place and name LV sites is distorted. Its centre line runs close to the septum, so the septum takes up about 210° of the 360°.
   - Sites called "lateral" are really inferolateral or inferior.
   - Sites called "inferolateral" are inferior.
   - 4-5 positions per heart labelled "superior" for the Bazan 2007 regions are actually in the lower half of the heart.
   - Same-spot depth comparisons are unaffected. Region-based results (Bazan 2007 Q waves) and site names are.
3. **F03-F06 (how depth is modelled and judged).**
   - Each pacing site switches on everything within 1.5 mm, which blurs depth in the 4-5 mm RV wall.
   - Every one of the ~3,500 Purkinje junctions can be entered from the muscle in 2 ms (an unsourced value).
   - The bundle speeds are tuned, but the docstring calls them "sourced 2.0 m/s".
   - The Durrer "first 5 ms" check passes by construction, so it isn't evidence.
4. **F07.** The "Doste 2019 outflow fibres" change fixed the septal RVOT only. RVOT free-wall fibres are unchanged and not Doste-like.
5. **F08.** Nothing since 10 Oct is committed and there is no git remote, so the adopted v5 model has no commit and nothing has ever been pushed.
6. **F09.** The package's "q in lead I" counts any first negative wave, even one starting 40-60 ms in, as a q.
7. **F10.** Two gate rules changed after results were seen: the Durrer window (62-80 → 62-100 ms) and the relative-QRS statistic (medians → means). Both are documented.

**Decisions for you:** F01-F04, F06-F11, F14 and F25 (see findings.csv, column `needs_alex_decision`).

---

## A. Inventory and provenance

### A1. Scripts → outputs → numbers now in use (model v5, 13 Oct)

| Stage | Script (mtime) | Output in use (mtime) | Committed? |
|---|---|---|---|
| Mesh cut | sims/biv_model/01_extract.py (2 Oct) | data/biv/<H>/biv.*, surfaces/ (2-3 Oct) | yes (47808c6) |
| Laplace | 02_laplace.py (2 Oct) | data/biv/<H>/laplace/ (2-3 Oct) | yes |
| UVC | 03_uvc.py (7 Oct 19:25, phi sign fix) | uvc/*.dat (7 Oct 19:26) | yes |
| Frozen fibres | 04_fibres.py (2 Oct) | bivF.lon (2-3 Oct) | yes |
| v5 fibres | analysis/fibre_fix_2026-10-13/{laplace_fix,fibres_fix}.py (13 Oct 02:16) via v5_grid.py fibres | analysis/v5_grid_2026-10-13/fibres_E/<H>/bivF.lon (13 Oct 18:53-18:56) | **no** |
| Site grid | 11_site_grid.py (7 Oct 19:22) | data/biv/<H>/sites.json (7 Oct 19:23-19:28) | yes |
| Network | 14_purkinje.py (10 Oct 12:07; last change = comment only, per LABNOTES) | purkinje/network.npz, summary.json (9 Oct 18:39), graph_scale.json (8-9 Oct) | yes |
| Torso placement | 08a_atrial_fit.py, 08_torso.py | data/torso/atria/<H>_to_g001_rigid.txt; torso/ | yes |
| cb conductor | 15_conductor.py (10 Oct 11:18) | used by v5_adopted leadfield() | yes |
| v5 lead fields + weights | analysis/v5_adopted_2026-10-13/v5_adopted.py (13 Oct 20:16) | runs/2026-10-13_LF_<H>_v5, ecgW_v5_<H>.npz (20:26-20:44) | **no** |
| v5 grid | v5_adopted.py grid → v5_grid.py Heart (18:52) | purk_<H>_v5.csv (20:58-21:07), grid/<H>/his_*.npy | **no** |
| v5 gates | v5_adopted.py gates; followup.py (21:12) | gates_v3_v5.txt (21:07), gates_followup.md (21:23) | **no** |
| Three-heart table | three_hearts_v5.py (20:17) | three_hearts/results.md (21:08) | **no** |
| Scoring | code/ecg_depth_criteria 0.3.0 (4 Oct) | all criteria | yes (tracked in git) |

- Every output is newer than the script that produced it, except the network files. 14_purkinje.py (10 Oct 12:07) is newer than network.npz (9 Oct 18:39).
  - LABNOTES (l.865) says the 10 Oct change was the `--weights` comment only.
  - I cannot diff the 9 Oct version because no commit exists between them.
- Git:
  - Last commit 47808c6 (10 Oct 12:20). No commit since.
  - `git remote -v` is empty, so nothing has ever been pushed (F08).
  - Uncommitted: LABNOTES.md (modified) and 13 untracked analysis folders from 12-13 Oct, including all v5 code. The repo-root zip and chain2.log are also untracked.
  - The scoring package in `code/` is tracked and committed.
  - `data/` and `runs/` are git-ignored by design (meshes, networks, sites.json and lead fields are not versioned).

### A2. Scoring package on the PC vs the cloud's 0.3.0

- The repo-root `ecg_depth_criteria.zip` (sha256 `f84c3886f6a844a8a153b2b8f369044a6aad74940526c14da039f24807d57492`) is **version 0.1.0**. Its source is identical to code/ecg_depth_criteria_0.1.0 (F31).
- There is no 0.3.0 zip on the PC, so I cannot compare against the cloud zip hash (244879223a…).
- The PC's 0.3.0 copy is `code/ecg_depth_criteria/` (`__version__ = "0.3.0"`). Per-file sha256:

```
ed55943a6beca3ce9634aa38fdc5fd3102d3af33d7a1bb4e553b82061021d053  ecg_depth_criteria/__init__.py
7f68169e25c711af7cb977932d6bce5a1835651ebc70b2d4dbf317811ad86764  ecg_depth_criteria/__main__.py
2b5318351346dbea98054e52d53cd63134d3da51c0a5d8844619addbda0ffb13  ecg_depth_criteria/criteria.py
71ba77507e2cf5466108f8f049191ba3c6af393a70f360734a3d279570c4df14  ecg_depth_criteria/fiducials.py
1a71b3c4c2c87ca6adbc3c0d4b02b8bb41010e885ff6846de462a01f592e1117  ecg_depth_criteria/leads.py
a228be4ec9657c5b4af52428218e55e88404bf03311a5715e1f87650b4bebf2c  ecg_depth_criteria/measure.py
f1774157217f3c6fda487a284bf63a793df01a9873c70cbf319433aaa7915c99  pyproject.toml
0ee10dc2fd28583b16e23e355bcad5d362a62c3a66b6b9c2033b492dfbf8fbb0  README.md
f86edc5da90a07b50d3af624930188f50898fb70d06801150a259b983c5a9887  tests/synthetic.py
831caf18e88acaa914d6791f65571e845cd29fb937468ba4e6ef5ec66352d117  tests/test_criteria.py
d9edf9f69ebe207201c5324fc5b66eb61989d5a8f92c7b5cf63233cc58869fc9  tests/test_measure.py
78678eb7435ff6c567df56a332dfc937ab0ef231e792ebd5388f430a512a1780  tests/test_summit_prisco.py
```

## B. Code audit, stage by stage

Classification: bug / undocumented assumption / tuned value presented as sourced / fine.

### B1. Mesh cut and units

- **Tags** (common.py:16-18): 1 LV, 2 RV, 25 FEC_LV, 28 FEC_RV, 29 FEC_SV. Myocardial volumes by tag are in section C. **Fine.**
- **Units:** µm → mm conversions are correct in every file I opened (01-15, v5_grid, v5_adopted). Speeds are in mm/ms, the openCARP velocity in µm/ms (600 = 0.6 m/s). **Fine.**
- **Re-added epicardial faces** (01_extract.py:137-140): free faces outside the authors' three surfaces are counted as epicardium. That covers 29,744 / 73,810 / 485 faces. In 6G8DD8S5 the authors' epicardium has only 11,717 faces, so 92 % of its epicardium comes from this rule. I checked: no epicardial face has all three nodes on an endocardial surface (0 / 0 / 0). **Fine** (undocumented for 6G8DD8S5).
- **Mesh quality** (a01): one connected component per heart; 0 inverted and 0 degenerate tets; edge length 0.33-1.75 mm (median 1.04); smallest element 0.010 mm³. **Fine.**
- **Laplace fields** (02_laplace.py:38-47): there are maximum-principle overshoots at 30-52 nodes per heart, all at z 0.89-1.0, where conflicting Dirichlet sets meet (F15, minor).

### B2. UVCs (03_uvc.py)

- **z** (174-191): monotone remap of the zeta Laplace field to axial distance. Correlation with axial distance 0.989 / 0.962 / 0.981. Outflow tracts reach z = 1 at their valves by design. **Fine.**
- **phi** (198-211): measured around the line apex → centroid of MV + TV rim nodes. phi 0 points to the RV endocardial centroid, and +90° is chosen so the aortic annulus has positive phi. **Bug in effect (F02, major):**
  - The axis passes close to the septum, so phi is strongly non-uniform.
  - Body check (a05), with sector centroids in the torso frame:
    - phi +90 is left and superior (anterolateral).
    - phi 180 is posterior-inferior (inferolateral or inferior; cos to body-superior -0.75 to -1.00).
    - phi -90 is inferoseptal.
  - So "+90 = anterior" is approximately true (anterolateral). But AHA-style positions using the RV insertion points (a05_site_labels_<H>.csv) show the phi-based names are rotated by roughly one segment on the free wall.
- **rho** = phi_epi (193): it is near 0 everywhere in the septum, so 11_site_grid.py uses `sep` there. **Fine.**
- **v** (196): LV/RV Laplace field thresholded at 0.5, which splits the septum in half (F26, minor).

### B3. Fibres

- **Rule** (04_fibres.py): Bayer 2012 LDRB with fibre = cos α·e0 + sin α·e1, e0 = e1 × e2 (e1 apex→base, e2 outward).
  - So +60° at the endocardium is a right-handed helix and −60° at the epicardium is left-handed, which is correct.
  - The mesh is not mirrored: the rigid placement has det R = +1 (08a_atrial_fit.py:50-53), and the LV long axis points left, anterior and inferior in the CT frame. **Fine.**
- **Sheets:** sheet normal = transmural (median deviation 0.7-0.9°, summary_04). Option (a) is as documented. **Fine.**
- **Unit length and orthogonality** (a03): |f| and |s| = 1 ± 1e-5 and |f·s| < 2e-5 in all six files (v3, v5). **Fine.**
- **Transmural profile** (04_fibres.py:135-141): Bayer's published double interpolation gives a non-linear profile (F27, minor).
- **Sampled angles** (a07): five elements per region and depth band, helix angle in a geometric frame (transmural = grad phi_epi; longitudinal = LV axis, or the PV/AV axis in the outflow tracts; + = right-handed). This frame is not the rule's own frame, so expect ±10-20° offsets (the rule-frame check is in analysis/free_checks_2026-10-13/fibres_frame/).

  v5 values, endo / mid / epi (degrees):

| Region | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| LV free wall mid | 67-70 / 44-52 / −35..−36 | 72-74 / 40-45 / −33..−35 | 73-75 / 44-53 / −32..−33 |
| Septum mid (LV side → RV side) | 43-46 / −10..−17 / −51..−54 | 46-49 / −13..−21 / −57..−62 | 49-52 / −8..−20 / −56..−59 |
| RV free wall mid | 85-89 / 62-67 / −23..−26 | 36-37 / 16-19 / −70..−72 | 51-55 / 31-39 / −51..−56 |
| RVOT septal | 59-67 / scattered / scattered | 47-74 / scattered / scattered | 60-76 / −8..21 / −27..48 |
| RVOT free wall (vs PV axis; ±90 = along the axis) | −74 / ±88-90 / 33-36 | −71..−72 / ±86-89 / 38-40 | −70..−72 / ±87-90 / 38-41 |
| LVOT / summit | 77-81 / −27..3 / −55..−81 | 67-82 / 5-23 / −32..−62 | 50-71 / −5..20 / −41..−57 |

- **Against Doste 2019:**
  - Septal RVOT endocardium moved from 41-53° (v3, Y5HYEDL4) to 59-67° (v5): closer to longitudinal, but not 90.
  - RVOT free wall endocardium is about 16-20° off the outflow axis; its epicardium is 33-41° off circumferential.
  - The free wall is identical in v3 and v5, so the v5 fix did not touch it (F07, major: the claim is broader than the implementation).

### B4. Conduction actually used in v5 (code path read end to end, then measured)

- **Speeds:** v5_adopted.py:123-127 builds `VG.Heart('E', h)`. v5_grid.py:62-66 sets 0.60/0.48/0.48, and in 6G8DD8S5 and 7D98EVAR 0.60/0.3504/0.336.
  - Fibres: fibres_E. Junction delays: 4/2 ms.
  - The network is not slowed in the HF hearts.
  - Graph-only: no openCARP activation in v5.
  - Cache files are newer than the fibre files, and the subagent rebuilt 6G8DD8S5's cache from scratch (relative difference 6e-8). **Fine** as implemented.
- **Realised speeds** (a03): local CV = 1/|∇T|, sorted by propagation direction (within 18° of an axis), myocardium only.

| Field | fibre | sheet (cross, in wall) | normal (transmural) |
|---|---|---|---|
| openCARP eikonal, v3 speeds (3 hearts, 3 sites each) | 0.585-0.587 | 0.406-0.416 | 0.476-0.480 |
| Graph / k, v3 speeds, same sites | 0.546-0.555 | 0.417-0.426 | 0.471-0.484 |
| **Graph / k, v5 control** (target 0.60/0.48/0.48) | **0.564** | 0.489 | 0.485 |
| **Graph / k, v5 HF** (target 0.60/0.350/0.336) | **0.501-0.503** | 0.364-0.366 | 0.350-0.351 |

- Graph and openCARP total times agree (median ratio 0.997-1.008, median |Δ| 0.6-1.0 ms), but the agreement hides a direction-dependent error.
- One k, fitted on v3 speeds, cannot correct it, and the error grows as the cross-fibre speed drops (**F01, major**).
- The claimed effective transmural speed of ~0.48 m/s is met in the control heart (0.485).

### B5. Purkinje network (14_purkinje.py; subagent second read agrees)

- **His:** z 0.919 / 0.918 / 0.917, phi 43.2 / −3.0 / 42.6°.
  - Chosen as the nearest LV septal node to the "RCC" annulus point, which is the most anterior-rightward annulus node (lines 269-273).
  - Distance from His to that RCC point: 18.1 / 10.6 / 15.7 mm.
  - His → RV penetration: 6.5 / 0.9 / 3.8 mm.
  - Undocumented heuristic (subagent F4).
- **Lengths (mm):**
  - LBB 11.5 / 13.5 / 12.1.
  - Divisions to Durrer's sites: anterior 20.4 / 21.1 / 17.5; septal 30.5 / 22.8 / 25.3; posterior 48.1 / 36.8 / 39.9.
  - RBB 64.1 / 49.2 / 54.8.
  - Moderator band 14.7 / 18.2 / 10.1, a single straight edge at z 0.35 (unsourced level).
- **Junctions:** all on the endocardial surface, none inside the wall (checked).
  - Density per cm² of endocardium (a10), Y5HYEDL4 (other hearts similar):
    - LV septal: apical 17.5, mid 15.7, basal 14.5.
    - LV free wall: apical 17.7, mid 15.1, basal 18.9.
    - RV septal: apical 16.9, mid 1.0, basal 0.
    - RV free wall: apical 14.8, mid 10.9, basal 14.1.
  - z > 0.9: 0 everywhere, LV and RV (outflow tracts bare).
  - Totals 3,665 / 3,192 / 3,241. The cap at 0.9 and "no RV septum above 0.35" are verified.
- **Speeds:** distal 2.0 m/s per edge (graph path along endocardial surface nodes, so tortuous). Proximal speeds are tuned to Durrer offsets (F05).
- **Delays:** 4 ms antegrade, 2 ms retrograde (unsourced) (F04).
- **Loops:** reconnections LV 553/466/468 and RV 353/266/300, so the network is not a tree. That is fine for shortest-path solving.
- **LBBB cut (6G8DD8S5):** genuinely disconnects the LV network from the His (0 of 1,983 LV junctions reachable; subagent).
- **Sources in docstrings, for the cloud to verify:**
  - Elizari 2017 (LBB origin); Durrer 1970 (three sites, 30 ms, 62-80 ms latest, RV +5-10 ms).
  - Sahli Costabal 2016 (tree parameters, coverage 11 ± 3 mm); Bayer 2025 (reconnections, 15 junctions/cm², no junctions on the upper RV septum: not in the abstract).
  - Berg 2023 (2 m/s, 3-5 ms delay); Choi 2023 (rabbit 3.4 ± 0.8 / 7.8 ± 2.4 ms).
  - Upadhyay 2019 (proximal LBB block 64 %).
  - Taggart 2000, Glukhov 2012, Joyner 1985, Doste 2019 (cited without DOI in v5 code).
- **Tuned / assumed values:** His window; LBB drop 0.10; moderator-band and RV-septum levels 0.35; cap 0.90; fascicle waypoints; Durrer offsets 0/2.5/5 and RV +7.5 ms; retrograde 2 ms; k; stimulus 1.5 mm; tree seed and parameters.

### B6. Activation solver

- **v5:** 100 % combined-graph, with no fallback needed. Directed Dijkstra; myocardial edge time = √((d·f/vf)² + (d·s/vs)² + (d·n/vn)²) / k; muscle→junction +2 ms, junction→muscle +4 ms.
- My independent re-implementation (a03) reproduces every checked v5 total activation to 0.1 ms.
- No unactivated nodes in any v5 beat.
- **v3:** openCARP eikonal with a 6-minute timeout and graph fallback: 11 / 0 / 8 grid sites fell back (Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR); 38 network beats in all (subagent).
- **Stimulus:** all nodes within 1.5 mm at t = 0 (F03).
- **Time:** continuous activation times; ECG sampled at 1 ms.

### B7. ECG

- **Lead fields** (15_conductor.py):
  - Heart g = calibration.json / s, with s = g_e,fibre / 0.625 = 4.084 / 3.865 / 4.196.
  - Cross-fibre g_i is 3-4 × Clerc (F12).
  - Blood 0.7 S/m in tag 101, which covers only 56-70 % of the cavity volume (F13).
  - Torso 0.2 S/m (the gbath test of 10 Oct confirms g_i/g_e are used). No lungs.
  - aVR/aVL/aVF are derived from I and II with the correct formulas (220).
- **Electrodes:** nearest torso-skin node, 0.5-0.7 mm snap for V1/V2.
- **Source term** (13_fast_ecg.py:235-237): monodomain-equivalent σ, with c = −1 validated against openCARP to 0.0002 mV. Sheet conductivity is inconsistent with the v5 speeds (F11).
- **Template:** one Tomek beat per heart (F16).
- **Sampling and padding:** 1 ms sampling; 60 ms flat pad at v[0] before scoring; no filtering in the main scoring.
- **Saved ECGs:** |I + III − II| and |aVR + aVL + aVF| ≤ 9e-6 mV in 63 cb folders checked (file rounding), and ≤ 1.5e-7 mV in the v5 His ECGs. **Fine.**
- **True onset:** onset = stimulus and offset = last activation (10_measure_ecg.py:76), so the true QRS equals total activation.

### B8. Site grid (11_site_grid.py)

- **Depth achieved vs target** (a06), worst |Δ| per family:
  - LV free wall 0.068 / 0.062 / 0.052; septum ≤ 0.068; summit ≤ 0.055; vein course ≤ 0.076.
  - RV free wall 0.125 / 0.10 / 0.116, with 16-20 of 36 sites off by more than 0.05.
  - RVOT ≤ 0.166.
  - Aortic cusps up to 0.37 / 0.46 / 0.10, because their walls are 1.0-2.2 mm in Y5HYEDL4 (F28).
  - No depth-order violations except one per heart at the cusps or RVOT.
- **Wall thickness at sites** (site-grid line method), min / median / max mm:
  - LV free wall: 8.4 / 9.9 / 11.8 (Y5); 10.2 / 12.3 / 15.8 (6G); 8.2 / 10.6 / 12.6 (7D).
  - RV free wall: median 4.8 in all three.
  - RVOT 2.8-5.4; summit 9.4-10.0 / 14.0 / 7.4-8.4; vein course 6.0-13.2.
- **Wrong chamber:** 6G8DD8S5 rv_free_wall_q75_z0.25 and 7D98EVAR rv_free_wall_q25_z0.25 sit in LV-tagged muscle (F14). Excluding them leaves Bazan 2006 unchanged.
- **Placement rules:**
  - RVOT: w < 0.3, 8-15 mm from the PV rim; septal = nearest the aortic interface, free wall = farthest.
  - Cusps: most anterior-rightward / most leftward-posterior annulus node with v = 0.
  - Summit: point A = LCC proxy; B = 9.6 mm (Kuniewicz); sector 18.9 mm; GCV arc 14.0 mm. The arc shape and B's direction are assumptions.
  - Vein proxies: groove = LV epicardium within 2 mm of RV epicardium; GCV 4-6 mm below the AV-groove edge; vein-adjacent ≤ 5 mm (assumption).
- **Names and regions** come from the distorted phi (F02).

### B9. Gate scoring: re-implemented independently (a02_gates.py)

| Gate (v5, true onset unless noted) | Reported 13 Oct | My value | Verdict |
|---|---|---|---|
| Daniels order, control: RVOT / cusp / summit 90 / vein 90 / LV endo 10 | 0.679 / 0.587 / 0.542 / 0.458 / 0.348, fail | 0.679 / 0.587 / 0.542 / 0.458 / 0.348, fail (n 8/8/2/3/18) | reproduced |
| Same, detected (clean) / det20 | fail | 0.699/0.621/0.625/0.503/0.362; 0.667/0.588/0.609/0.482/0.368, fail | reproduced |
| Summit + cusp QRS, control | 159.0 ms | 159.0 (n 16) | reproduced |
| Relative QRS, ratio of means, LV free wall 90/10 (10 pairs) | 1.071 / 1.137 / 1.093 | 1.0712 / 1.1371 / 1.0930 (means 165.4/154.4, 163.4/143.7, 166.9/152.7) | reproduced |
| Berruezo 6G8DD8S5 QRS / PdW / IDT / RS % | 14.7 / 60.6 / 31.6 / 7.6, fail on RS | same | reproduced |
| Durrer: latest after LV onset; LV endo outside posterobasal by 30 ms; RV epi breakthrough; His detected QRS | 100.8; ~48 %; 15.1; 94 ms | 100.8; 48.5 % (nodes) / 48.8 % (area); 15.1; 94 | reproduced |
| 6G8DD8S5 His QRS (activation span) | 142.0 | 142.0 | reproduced |
| Bazan 2006 RV vs LV, median pair % | RV 4.2/4.1/4.0 vs LV 8.0/14.7/10.3, pass | same, pass | reproduced |
| Bazan 2007 basal superior q in I, pooled 90 vs 10 | +5 pp (−19 to +28), fail | 4/21 vs 3/21 (+4.8 pp), fail | reproduced; with body regions 4/14 vs 1/14 (F02) |
| No-network control (E fibres) | pass | summit + cusp 240.0 ms; wider in all 7 families; pass | reproduced |
| Normal-beat axes, net / area | 64/−17, −36/−29, 67/64 | 64/−17, −36/−29, 67/64 | reproduced |
| Depth AUC, LV free wall 90 vs 10: PdW / MDI / IDT / RS | 0.78-0.90 / 0.87-0.94 / 0.47-0.55 / 0.40-0.59 | 0.78/0.90/0.885; 0.87/0.87/0.94; 0.465/0.545/0.51; 0.40/0.59/0.445 | reproduced |

- **How the AUCs are computed:** unpaired Mann-Whitney over the 10 LV free-wall positions per depth per heart, true onset, "higher = more epicardial" for every measure.
- They are not paired, although the positions are matched. Paired up-counts: PdW 10/9/10, MDI 9/10/10, IDT 6/6/7, RS 5/5/4 of 10.
- With n = 10 vs 10 the 95 % CI of an AUC is roughly ±0.2.
- The plan's definition is not on the PC; the cloud should check it.

## C. Anatomy of the three hearts (numbers only)

- **Cohort metadata** on the PC (sims/cohort/draw_pilot.py):
  - Y5HYEDL4: control, male, paper label MC5.
  - 6G8DD8S5: HF with wide QRS, female, FHF8.
  - 7D98EVAR: HF with narrow QRS, female, FHF6.
  - Age, height, weight, BSA, LVEF, QRS and CT phase are **not on the PC** (F25). The authors' own simulated activation spans (electrophisiology/Y.txt) and mechanics volumes are present.
- **Method:** cavities closed at the valve openings; wall thickness by nearest surface; AHA segments anchored at the RV insertion points (a11).
- **Torso frame:** +x left, −y anterior, +z superior.

| Measure | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| LV cavity volume, mL (authors' mechanics t0) | 172.0 (170.2) | 157.8 (156.6) | 172.8 (170.6) |
| RV cavity volume, mL (authors) | 197.9 (195.7) | 107.2 (107.3) | 122.5 (121.4) |
| LV myocardium mL / mass g (×1.05; tags 1 + 25 + 29) | 164.6 / 172.8 | 199.3 / 209.3 | 160.0 / 168.0 |
| RV myocardium mL / mass g (tags 2 + 28) | 69.0 / 72.5 | 42.4 / 44.5 | 51.8 / 54.4 |
| Septum basal / mid, mm (AHA anteroseptal, inferoseptal) | 9.6, 9.1 / 8.1, 8.2 | 11.7, 8.8 / 7.8, 8.9 | 8.1, 8.4 / 7.1, 7.1 |
| LV anterior base / mid / apex, mm | 8.7 / 8.3 / 8.6 | 10.7 / 8.6 / 9.6 | 8.4 / 7.6 / 8.3 |
| LV lateral base / mid (anterolateral, inferolateral) / apex | 8.7, 9.9 / 7.9, 9.7 / 8.0 | 15.5, 13.2 / 13.0, 12.0 / 8.8 | 10.3, 10.4 / 8.6, 10.1 / 7.6 |
| LV inferior base / mid / apex | 10.2 / 10.6 / 8.2 | 13.2 / 11.3 / 8.9 | 10.9 / 12.0 / 7.6 |
| LV apex cap (< 8 % of long axis) | 4.5 | n/a | n/a |
| RV free wall mid / base | 4.0 / 4.2 | 4.2 / 4.2 | 4.2 / 4.3 |
| RVOT septal / free wall (5-15 mm below PV) | 4.2 / 4.4 | 5.0 / 4.2 | 3.9 / 4.6 |
| LV long axis: endo apex → MV plane / epi apex → MV centre, mm | 97.9 / 105.0 | 75.3 / 93.9 | 83.0 / 93.4 |
| LV short-axis equivalent diameter 15 / 25 / 35 mm below MV | 57.3 / 58.1 / 56.4 | 56.6 / 58.4 / 59.8 | 58.8 / 59.3 / 58.7 |
| Annulus mean diameter, mm: aortic / pulmonary / mitral / tricuspid | 24.2 / 30.4 / 39.4 / 48.2 | 25.0 / 33.4 / 39.2 / 41.0 | 21.6 / 26.5 / 32.1 / 40.2 |
| RVOT equivalent diameter 10 mm below PV | 36.4 | 38.3 | 32.4 |
| Infundibulum proxy: min TV-rim → PV-rim, mm | 24.3 | 19.4 | 24.2 |
| Aorto-mitral min rim distance, mm | 8.8 | 7.7 | 7.9 |
| PV above AV (torso z) / anterior / left, mm | 26.5 / 16.9 / 4.4 | 22.1 / 28.4 / 4.6 | 18.6 / 22.3 / 9.5 |
| Angle between AV and PV plane normals / LVOT-RVOT axis angle | 61.5° / 21.8° | 63.2° / 36.4° | 65.3° / 27.0° |
| Muscle beyond PV plane: max height mm / mL (> 1 mm) | 8.8 / 1.73 | 9.2 / 2.08 | 7.3 / 1.34 |
| Muscle beyond AV plane within annulus radius + 10 mm: max mm / mL | 39.8 / 5.28 (mostly RV infundibulum) | 32.3 / 3.51 | 32.4 / 3.97 |
| Cusp sites (d50) vs AV plane: RCC / LCC, mm (+ = aortic side); wall | +4.7 / −3.1; 2.2 / 1.0 | +3.5 / −2.7; 1.6 / 3.6 | +2.8 / −2.9; 4.0 / 4.6 |
| Summit sites (d50) below AV plane: superior / inferior-lateral; wall | −7.1 / −14.0; 10.0 / 9.4 | −6.5 / −13.0; 14.0 | −4.9 / −10.0; 8.4 / 7.4 |
| LV long axis in torso: frontal angle / anterior tilt / from sagittal | 46.6° / 47.5° / 27.7° | 42.9° / 53.9° / 25.6° | 54.8° / 37.8° / 27.1° |
| Epicardium → skin (min) / most anterior epicardium → skin | 30.8 / 32.0 | 34.2 / 37.9 | 42.1 / 43.9 |
| RVOT d50 septal / free wall: height vs V1, mm; to skin, mm | +19.2 / +30.5; 66.6 / 46.5 | −7.9 / +8.5; 75.3 / 41.6 | +3.5 / +3.2; 73.0 / 57.1 |
| Rigid placement: rotation from the CT frame / det R | 13.4° / 1 | 19.9° / 1 | 18.6° / 1 |

- **T13 at the V1/V2 level** (z = 5 mm): chest width 343.7 mm, depth 258.0 mm. V4 is 76.4 mm below V2. V1 x = −14.5, V2 x = +40.6 vs shoulder midline +6.4 mm.
- **Summit stand-in** (summary_11.json): bifurcation proxy B 9.6 mm from the left-sinus proxy A; sector radius 18.9 mm; GCV arc 14.0 mm. Site distances to B and A, and sector areas, are in a04_anatomy.json under summit_v5_summary_11.
- **Daniels vein-course sites** (proximal AIV, basal ring anterolateral, basal ring lateral): wall 7.4 / 11.2 / 7.4 mm (medians). Distances are in summary_11.json vein_course_sites.

## D. Activation sanity (v5 beats)

| His-driven beat | Y5HYEDL4 | 6G8DD8S5 (LBBB cut) | 7D98EVAR |
|---|---|---|---|
| His → first myocardium | 19.9 ms | 26.4 (RV first) | 18.8 |
| First LV endocardium (UVC z, phi) | z 0.80, phi 60 (high anterior paraseptal, by construction) | z 0.25, phi −53, at 50.5 ms | z 0.80, phi 60 |
| Onset at Durrer's three areas after LV onset | 0.0 / 2.7 / 5.0 | 22.4 / 10.7 / 0.0 | 0.0 / 2.5 / 5.4 |
| First RV endocardium | 26.5 ms (z 0.27, phi −6) | 26.4 | 27.0 |
| RV epicardial breakthrough after LV onset | 15.1 ms (z 0.38, phi 0) | −12.4 (RV before LV) | 16.4 (free wall > 5 mm from LV: 19.2) |
| LV endocardium (outside posterobasal) by 30 / 37.5 ms | 48.8 / 67.0 % | 26.8 / 40.5 % | 44.5 / 61.0 % |
| Latest node; latest 5 % | RV z 1.0, phi 41 (conus); 85 % RV, median z 0.98 | LV z 0.77, phi 138 (lateral); 0 % RV | RV z 0.99, phi 50; 52 % RV |
| Total activation span / detected QRS | 100.8 / 94 ms | 142.0 / 141 | 100.2 / 86 |
| Axis net / area | 64° / −17° | −36° / −29° | 67° / 64° |

Paced beats (graph v5, my solver; times from the stimulus):

| Beat | First network entry | First junction exit | His (retrograde) | Total | Latest region |
|---|---|---|---|---|---|
| Y5HYEDL4 RVOT septal 10 % | 40.6 (22.5 mm to nearest junction) | 48.3 | 62.5 | 147.8 | RV base, z 1.0, phi −73 |
| Y5HYEDL4 LV free wall phi180 z0.5 10 % | 3.2 | 10.6 | 46.3 | 161.0 | RV base / outflow |
| Y5HYEDL4 summit superior 90 % | 21.0 | 29.0 | 55.3 | 157.2 | RV base, phi −40 |
| 6G8DD8S5 RVOT septal 10 % | 17.3 | 23.4 | 99.8 | 140.0 | LV lateral mid (phi 155) |
| 6G8DD8S5 LV free wall 10 % | 2.0 | 9.2 | 87.4 | 158.4 | RV base |
| 6G8DD8S5 summit superior 90 % | 32.6 | 40.8 | 100.3 | 142.6 | RV base / LV inferior |
| 7D98EVAR RVOT septal 10 % | 44.8 | 52.0 | 62.8 | 147.4 | RV / LV inferior base |
| 7D98EVAR LV free wall 10 % | 14.7 (6.6 mm gap to network) | 21.3 | 58.4 | 168.7 | RV base |
| 7D98EVAR summit superior 90 % | 23.2 | 32.1 | 49.9 | 152.4 | RV base |

- The network shortens total activation by 66-112 ms compared with myocardium alone.
- 79-95 % of nodes activate earlier with the network than without it.

## E. Results integrity, 3-13 Oct

67 numbers checked across 18 folders (a09_integrity.csv).

**Matched (63):**
- network_three_hearts and grids_2026-10-07: 9 checks, including AUCs.
- three_arms: 2. nofast_vs_normal: 3. rvot_diag: 5. aim1_gates: 6. rvot_tests: 6. noise_onset: 2. junction_tests: 4.
- rvot_anatomy: 2. monodomain_check: 1 (8 values). free_checks: 2. fibre_fix: 1. daniels_onset: 2.
- v5_grid: 11. v5_adopted: 4 (plus all of B9). idt_v2: 1.
- pilot v4 median changes (true onset): 1.

**Not matched (4):**
- No-layer PdW AUC: 0.495 rounds to 0.49 or 0.50 (rounding only).
- Three 4 Oct pilot-grid AUC sets computed in the cloud (F30).

**LABNOTES numbers with no file behind them:** these come from scratch scripts that were not kept or were lost at the 10 Oct WSL restart, as LABNOTES itself states.
- The 9 Oct axis investigation (axis.py, axis2.py, axis3.py) and the v3/v4 axis variants.
- The 9 Oct 21:55 retrograde-delay and junction-fraction exploration (explore.py, mix.py).
- The 9 Oct v4 paced-beat widths.
- The 9 Oct 23:22 source-vs-torso decomposition (axis_src.py, geom.py), except the ventricular myocardial volumes, which I reproduced (164.6 / 69.0, 199.3 / 42.4, 160.0 / 51.8 mL).
- Later desk checks reproduced the key ones: Durrer 48 % / 104 ms in aim1_gates, and the axes in axis_2026-10-10.
