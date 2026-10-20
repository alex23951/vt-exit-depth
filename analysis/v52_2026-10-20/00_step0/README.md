# v5.2 step 0: read-only checks and reports 34 and 35

PC clock 2026-10-20, 18:32-19:08 CEST. LOCK.md (re-issued 20 Oct 2026 13:51 UTC; 439,872 bytes; sha256
49601f59a485f760f09c0479f5dffbde3643ba16b0be62a6f0bef1b83d2cf310), section 15.2 step 0. Nothing was simulated, no beat was
run, no gate value was looked at and no model file was changed. Step 1 has not started.

## 1. What needs Alex before step 1

Two of the lock's step-0 rules send this report to Alex before step 1.

1. **The sheet's anterior and posterior outflows have nowhere to attach inside the envelope** (report 34 item 13; 7.1, D4).
   The lock attaches them to the two v5.1 fascicle endpoints, but those endpoints are Durrer's anterior and posterior
   paraseptal points, far from the 33 mm sheet:
   - posterior endpoint (z 0.33): 57.8 / 48.4 / 48.2 mm down the His line, that is 15-25 mm beyond the sheet's 33 mm
     end, in all three hearts;
   - anterior endpoint (z 0.80): 18.4 mm anterior of the His line in Y5HYEDL4 (limit 16.1 mm at its level, 2.2 mm
     outside) and 22.0 mm in 7D98EVAR (limit 15.2 mm, 6.8 mm outside); inside in 6G8DD8S5 (15.8 against 17.8 mm).
   - The envelope itself stays on the left septal surface in all three hearts (0 nodes off it).
   - Rule: stop and put the attachment to Alex before step 1; the envelope is not widened.
2. **v5.1's left-bundle trunk and fascicle nodes carried no junctions** (report 34 item 8; D1). In v5.1 every junction
   sits on a distal-network node; the LB_TRUNK and FASCICLE paths were insulated (0 junctions on their 125 / 82 / 105
   nodes; 18 / 8 / 13 distal-network junctions share a mesh node with them where the distal trees branch off). So the
   07:30 rule (junctions on every sheet node beyond 10 mm) would have added upper-septal junctions relative to v5.1, and
   D1 partly restores v5.1. The network part of D1 is not empty: 255 / 239 / 220 v5.1 LV junctions sit above the D1 line
   (AHA 2, 3, 8, 9), so D1 removes those.

All checksums match, so the third step-0 stop (a different file set) does not apply.

## 2. Found now that will stop a later step (reported early)

- **Aortic angular frame, step 2c (8.5 item 6).** The aortic-ring point nearest the pulmonary valve lies 42 / 63 / 61 deg
  from the ring point nearest the mitral valve (the other sense: 318 / 297 / 299 deg). The lock accepts 90-150 deg (Toh's
  120.4 deg) and says stop if both senses fail, without picking the closer one. Both fail in all three hearts, with both
  readings of "nearest the pulmonary valve" (nearest disc node; nearest the disc centre).
- **The crescents and sleeves would add little or no muscle.** The mesh's valves are solid discs about 6 mm thick, and
  ventricular muscle already wraps them: LV muscle reaches 1.1-5.5 mm above the aortic valve mid-plane all round the
  root (sinus medians 2.7-4.5 mm), and RV muscle 1.7-8.0 mm above the pulmonary mid-plane (medians 3.9-6.9 mm; the ring's
  lowest points are 2.3-3.7 mm below the plane). With max(existing, lune), the 2.4 mm RCC axial cap and the sleeve rule
  max(existing, 4.0 mm), existing muscle already exceeds the RCC cap at every angle of the RCC lune in all three hearts,
  and stands at least 4.2 mm above each pulmonary sinus's ring low point at every angle, so on this reading neither the
  RCC crescent nor the sleeves add muscle; the LCC lune (2.9 mm) could add a little where the existing LCC muscle is
  lower (down to 1.1 mm in 7D98EVAR). If the reference were the disc's arterial face instead of its mid-plane (about
  3 mm higher), more would be added; the lock does not say which face the "valve-plane ring" is. Precondition 35 (h) passes: the
  tag-1/tag-5 boundary is 2.0-5.6 mm above the valve plane at all six positions in every heart.
- **The infundibulum cut height (D6, step 2b).** The mesh's posterior RVOT wall, from the superior tricuspid annulus to
  the pulmonary ring, is 13.6 / 10.2 / 13.7 mm long against Jakiel's 26.9 +- 6.5 mm. The 12.7 mm split therefore falls at
  93 % of the span in Y5HYEDL4 and 7D98EVAR and beyond the ring in 6G8DD8S5, so almost no free-standing infundibulum
  is split on the posterior wall. The infundibulum touches the aortic root over 829 / 733 / 880 mm2, up to 18-22 mm above
  the ring at the right sinus (de Kerchove: 2.4 mm).
- **The right bundle already crosses a moderator band in v5.1 (D2, step 2g).** The lock treats v5.1's right bundle as
  septal-only (7.2: "the septal-only course ... becomes arm A20"). In v5.1 it runs down the RV septum to z 0.35 and then
  crosses the cavity as one straight 1.5 m/s edge (14.7 / 18.2 / 10.1 mm, class RB) to the anterior RV free wall, where
  the RV distal network starts; the band edge carries no junction. The mesh also has no papillary muscle and no
  "anterior RV free wall" label, so assumption 47's end node needs a label definition (my candidate, below, is a
  construction).
- **D1 leaves most of the sheet junction-free.** The D1 line (one third of the septal crest-to-apex length) crosses the
  His line 28.7 / 29.2 / 25.4 mm below the His exit, so junctions are allowed on only 21 % / 6 % / 22 % of the sheet's
  area (the part below the line and beyond 10 mm).
- **A37's "first four" KIT torsos.** In the record's own archive order they are T_13, T_24, T_20, T_17, and T_13 is the
  primary torso itself. The IDs are written into LABNOTES as the lock asks; whether T_13 counts needs a word before step 8a.
- **Arms not run (not a stop).** A35 (lungs, KCL_torso1): checks (i)-(iii) pass, (iv) fails: the mesh ends at z -306 mm,
  above the iliac crest, so the LL electrode cannot be placed by the Kligfield rule, and the skeleton is one tag and one
  connected piece, so the clavicles cannot be told apart. A36 (Moss torso): Torso.vtu has no skeletal muscle at all
  (Material 8 is listed in material.tab but no cell carries it), and its 24.95 M cells need about 12-13 GB.

## 3. Step-0 acceptance

| Check | Result |
|---|---|
| Report exists; v5.1 tag matches | v5.1 = d1ff89b, ancestor of HEAD 189c822; since the tag only LABNOTES.md (appended) and heart51.py (no-network mode added at step 6, ad121dd) changed |
| v5.1 data files | 70 of 70 unchanged (size, mtime to 1 us, sha256), manifests/v51_data_sha256.tsv |
| v5 files | unchanged: yes (3,484 files, sha256, check_v5_files.py --full) |
| 17.3 checksums | all match: md5 of the 3 zips; md5 of dataset_info.csv (no copy was stored on the PC; downloaded now from record 19351401); CRC32 of the 6 named files per heart (zip directory and extracted file) and of Y5HYEDL4's 3 binaries |
| Report 34 complete (item 3b after step 2g) | yes, 3 hearts |
| Report 35 complete | yes, 3 hearts; (b) and (c) measure built lunes, so they follow step 2c |
| Step-0 stops | two triggered (section 1); none for the septal boundaries, the mitral annulus or 35 (h) |

## 4. The other step-0 items

| Item | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| Template run (fix 1) | runs/2026-10-02_biv_fullqrs; site node 313318 (z 0.50, phi -179), monodomain Tomek, cell type ENDO (default, no flag) | runs/2026-10-03_6G8DD8S5_fullqrs; node 19052 (z 0.50, phi 180), ENDO | runs/2026-10-03_7D98EVAR_fullqrs; node 277582 (z 0.50, phi -180), ENDO |
| Template node and window | LAT 60.0 ms; -60 to +80 ms | same | same |
| Atrial-fit pose applied in v5.1 | yes (max node error 7e-6 mm) | yes | yes |
| Rotation, axis | 13.45 deg about (-0.22, -0.79, 0.57) | 19.87 deg about (0.46, 0.19, -0.87) | 18.65 deg about (0.75, 0.57, -0.34) |
| Translation (mm); pivot | (-9.8, -122.0, -82.0); R about the mesh origin, then t | (-49.6, -73.2, -59.7) | (-50.6, -77.3, -63.0) |
| Stimulated nodes per site (1.5 mm ball) | 7-24, median 17 | 12-23, median 17 | 8-22, median 17 |

- **openCARP Tomek cell types**: ENDO (default), EPI, MCELL (Tomek.model, flag; openCARP build ffce195).
- **Transmural coordinate of the v5.1 fibres**: LV side phi_epi_fix (Laplace, LV + RV endocardium 0 to epicardium and
  aortic-root interface 1), septal blend by d = phi_rv / (phi_lv + phi_rv); RV side (d > 0.5) Doste's d = 1 - Phi_D.
- **v5.1 atrial and vessel-wall conductivity**: 0.2 S/m. The v5.1 heart-torso mesh holds only ventricles (tag 1), cavity
  blood (101, 0.7 S/m) and one torso conductor (100, 0.2 S/m); atria, their blood and the great vessels are torso.
- **Stimulus**: radius 1.5 mm confirmed (heart51.py:31, BALL_UM = 1500.0, strict "<"); no tissue or connectivity clause.
- **dream.solve**: offered: 0 eikonal, 1 RE+ (diffusion), 2 RE- (default), 3 DREAM. openCARP +Help lists no Purkinje
  coupling option (that is T0's question; recorded here only).
- **Cavity capping (R3.1)**: possible in all three hearts. The LA and RA cavity surfaces are already closed (every edge
  in two faces), with one ostium loop per vein (5 on the LA, SVC and IVC on the RA; Y5HYEDL4's RIPV and IVC loops have a
  pinch point that a cap has to split). The aortic root and pulmonary artery lumens open only at their cut ends and
  close there with a cap: voxel fills (0.75 mm) stay bounded: LA 55.7 / 115.0 / 57.6 mL (dataset 65.5 / 149.4 / 66.4),
  RA 83.6 / 84.4 / 67.0 mL (91.2 / 104.7 / 73.1), aortic root 13.9 / 27.2 / 17.3 mL, pulmonary artery 3.8 / 11.0 / 4.7 mL;
  the LV / RV controls give 162 / 185, 149 / 100 and 163 / 114 mL against v5.1's C6 172 / 198, 158 / 107 and 173 / 122 mL
  (the voxel method reads about 6 % low).
- **Supraventricular crest**: none in the meshes (no tag; the RV wall along the shortest tricuspid-to-pulmonary path is
  5.5-7.0 / 4.2-4.8 / 5.1-6.2 mm thick against Jakiel's crest 12.3 and 9.2 mm).
- **Papillary muscles, trabeculae**: none (no tag; the LV endocardium has genus 0 in all hearts, so nothing bridges the
  cavity).
- **KIT torsos for A37** (data/torso/torsoModels.zip = record 20086105's file, md5 528b7c89...): archive order T_13, T_24,
  T_20, T_17, T_01, T_05, T_09, ... (25 shapes plus a mean torso).
- **KCL host for A35**: Zenodo record 7253863 (DOI 10.5281/zenodo.7253863, Qian and Bishop, CC BY 4.0, 26 Oct 2022);
  KCL_torso1.zip, file id d4471b7d-4471-47c8-a34f-5d2064be89f5, 167,823,369 B, md5 23082fcd5649f39671e3d831121948cb (the
  download matches); 1,689,018 nodes, 9,686,213 elements; host lung value 0.0714 S/m recorded, not used.
- **Moss host for A36**: Zenodo record 8285403 (EUPL-1.2), Torso.vtu file id d776d4da-75d0-4d46-b790-904d8c959197, 4,252,911
  points, 24,954,345 cells; read by HTTP range requests only (header and the 133 MB Material array).

## 5. Report 34: conduction geometry (geometry only, before any beat)

Definitions are mine and are written at the top of step0_report34.py: surface distances by Dijkstra on the 2-ring surface
graph (the edge-only value beside it over-estimates); left septal surface = LV endocardial nodes in AHA 2, 3, 8, 9 and 14
(v5.1's insertion-point rule); septal crest = the top edge of that surface where it meets the valve rims; His line = the
surface shortest path from the v5.1 His node to the LV endocardial apex; sheet coordinates s (along the line) and a
(surface distance from it, + anterior by the AHA angle). UVC phi is not used for "anterior" or "midway" because it is
distorted on the septum (audit F02: the inferior septal boundary reads phi -115 to -153 deg).

| Item | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| 1. Fascicle endpoints = the code's Durrer points | yes: anterior z 0.80 phi 60 (AHA 2), septal 0.50 / 0 (9), posterior 0.33 / -59 (14) | yes: AHA 8, 9, 14 | yes: AHA 2, 9, 14 |
| 2. UVC z of the mitral, aortic, tricuspid and pulmonary rims and the septal crest | 1.000 for all (z = 1 on the base set by construction) | same | same |
| 2. Axial fraction f (apex 0, mitral-ring centroid 1): mitral / aortic / crest / His | 1.00 / 1.00 / 0.96 / 0.86 | 1.00 / 0.91 / 0.90 / 0.85 | 1.00 / 0.97 / 0.94 / 0.87 |
| 2. Moderator-band septal insertion (v5.1 rbb_low) z | 0.351 | 0.349 | 0.353 |
| 2, 10. Septal crest-to-apex length (edge-only) | 100.2 mm (104.3) | 77.2 (80.4) | 86.9 (90.3) |
| 3. His exit z, phi, AHA; distance to crest | 0.919, 43 deg, AHA 3; 6.6 mm | 0.918, -3 deg, AHA 3; 2.0 mm | 0.917, 43 deg, AHA 3; 6.1 mm |
| 3. z at 10 mm / 33 mm down the His line | 0.830 / 0.575 | 0.844 / 0.514 | 0.817 / 0.531 |
| 3. Septal-outflow node (nearest LV distal node to the mid-septal point at 16.5 mm) | 229026 (2.3 mm away) | 981 (0.9) | 39804 (0.8) |
| 4. LV / RV junctions; per cm2 | 2,221 / 1,444; 14.5 / 7.6 | 1,983 / 1,209; 14.3 / 9.6 | 2,004 / 1,237; 13.4 / 8.8 |
| 4. LV septal junctions, upper / middle / lower third | 255 / 333 / 94 | 239 / 311 / 119 | 220 / 262 / 91 |
| 4. Above the D1 line, by AHA segment | 255 (2: 107, 3: 76, 8: 59, 9: 13) | 239 (2: 32, 3: 78, 8: 57, 9: 72) | 220 (2: 47, 3: 93, 8: 60, 9: 20) |
| 4. Cross-checks: septal junctions with UVC z >= 0.67; junctions in AHA 2-3 | 217; 183 | 256; 110 | 218; 140 |
| 5. Papillary muscles or trabeculae | none | none | none |
| 6, 12. v5.1 moderator band | straight edge 14.7 mm, z 0.351 -> 0.361 | 18.2 mm | 10.1 mm |
| 12. Candidate end node (assumption 47, my construction) and chain length | 369808, 12.0 mm | 37002, 16.0 mm | 26551, 9.0 mm |
| 12. Insertion level on the RV septum (crest 0 -> apex 1) | 0.82, lower third | 0.63, middle third | 0.82, lower third |
| 7. The z 0.90 network cap below the mitral annulus | 10.1 mm axial (9.5 along the endocardium) | 8.9 (4.8) | 9.3 (7.7) |
| 8. Junctions on v5.1 LB_TRUNK / FASCICLE nodes | 0 | 0 | 0 |
| 10. D1 line: distance from the crest; its UVC z | 33.4 mm; 0.63 (0.59-0.69) | 25.7 mm; 0.67 (0.57-0.87) | 29.0 mm; 0.64 (0.59-0.73) |
| 10. Share of the above-D1 septum with z >= 0.67 / in AHA 2-3 | 0.90 / 0.78 | 0.94 / 0.64 | 0.93 / 0.74 |
| 11. Upadhyay line, 12 points at 2 mm | s 0-22 mm, z 0.92 -> 0.70, all on the left septum | report34_6G8DD8S5.json | report34_7D98EVAR.json |
| 13. Anterior endpoint (s, a) against the 17.8 / 4.8 mm envelope | 10.9, +18.4 mm: outside by 2.2 | 23.6, +15.8: inside | 10.0, +22.0: outside by 6.8 |
| 13. Posterior endpoint s | 57.8 mm: beyond the 33 mm end | 48.4: beyond | 48.2: beyond |
| 13. Anterior minus posterior a; surface distance between them | 24.4; 52.6 mm | 21.9; 34.3 | 22.0; 43.4 |
| 13. Envelope nodes off the left septal surface (adopted; centred) | 0; 0 | 0; 0 | 0; 0 |
| 13. Sheet area where D1 allows junctions | 132 of 628 mm2 (21 %) | 35 of 603 (6 %) | 128 of 579 (22 %) |
| 14. Septal boundary at z 0.33, 0.50 (AHA angle, UVC phi) | anterior 65 / 78 deg (phi 51 / 68); inferior -59 / -65 deg (phi -144 / -153) | anterior 66 / 67 (phi 65 / 70); inferior -66 / -66 (phi -124 / -128) | anterior 57 / 62 (phi 58 / 68); inferior -55 / -62 (phi -116 / -129) |
| 14. Posterior paraseptal centre (z = z_MA / 3) | node 32305, z 0.342, AHA 15, 10.2 mm from the boundary | 165870, 0.328, AHA 15 | 5925, 0.340, AHA 10 |
| 14. Central centre (z 0.50, equidistant from both boundaries) | 63071, z 0.499, AHA 9 (27.6 mm from each) | 30396, 0.492, AHA 9 | 250241, 0.501, AHA 9 |
| 14. Anterior paraseptal centre (10 mm below the mitral annulus) | 53314, z 0.898, AHA 1, 9.4 mm below, 10.3 mm from the boundary | 54805, 0.882, AHA 1 | 10692, 0.890, AHA 1 |
| 9. Code Durrer points to the new centres (surface mm): anterior, septal, posterior | 34.8, 7.1, 23.0 | 31.7, 7.1, 25.0 | 34.5, 0.0, 24.6 |

## 6. Report 35: outflow geometry (at step 0; again after steps 2b-2d)

Definitions are written at the top of step0_report35.py (valve plane = mid-plane of the valve disc; ring = the disc's
contact with the wall; Toh's theta frame; de Kerchove's six positions at the derived angles N/L 0, LCS 60.2, L/R 120.4,
RCS 180.7, R/N 241.0, NCS 300.5 deg).

| Item | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| Valve-disc thickness, aortic / pulmonary | 6.3 / 6.2 mm | 5.7 / 5.8 | 6.2 / 6.2 |
| (a, h) tag-1/tag-5 boundary above the valve plane, luminal-epicardial, over the six positions | 2.7-5.6 mm | 2.6-5.0 | 2.0-5.4 |
| (h) any position below the plane | no | no | no |
| Existing LV muscle above the aortic plane, sinus medians L / R / N (range) | 3.4 / 4.4 / 4.5 (2.6-5.3) | 2.7 / 3.4 / 4.0 (2.2-5.1) | 3.3 / 4.0 / 4.4 (1.1-5.5) |
| Existing RV muscle above the pulmonary plane, posterior / +120 / -120 (range); ring low point | 6.9 / 5.4 / 6.2 (4.2-8.0); -2.3 to -3.5 | 5.2 / 5.1 / 4.9 (2.0-6.0); -2.8 to -3.7 | 3.9 / 5.4 / 4.6 (1.7-6.7); -2.5 to -3.2 |
| (d) aortic wall 20 mm above the valve (Hasdemir 1.6); pulmonary | 3.3 mm (2.4-5.9); the artery ends at 16 mm | 3.2 (2.4-4.5); 5.4 (2.9-13.8) | 3.4 (2.8-5.1); ends at 18.9 mm |
| (e) RV contact on the root at L/R; at the RCS (de Kerchove 4.6; 2.4 mm) | none; up to 18.5 mm above the ring | none; 20.5 | none; 22.1 |
| (f) posterior RVOT span (Jakiel 26.9 +- 6.5) | 13.6 mm (12.8 on the second reading) | 10.2 | 13.7 (13.1) |
| (f) candidates from 0 %: 37.3 % / 12.7 mm / 15.3 mm below the ring | 5.1 / 12.7 / -1.7 mm | 3.8 / 12.7 (beyond the ring) / -5.1 | 5.1 / 12.7 / -1.6 |
| Contact areas: infundibulum on the aortic root (tag 2-5); tag 1-2 above the 12.7 mm height | 829; 97 mm2 | 733; 68 | 880; 123 |
| (g) supraventricular crest | none (5.5-7.0 mm wall) | none (4.2-4.8) | none (5.1-6.2) |
| Angular frame check, 90-150 deg | fail (42 / 318) | fail (63 / 297) | fail (61 / 299) |

The third reading of "the tricuspid-annulus level" (the TV-ring centroid) puts the 0 % point off the posterior wall and
gives spans of 101-122 mm, so it is not usable; it is kept in the JSON for the record.

## 7. Files

- step0_base.py -> base.json (git, manifests, checksums, template, Tomek, fibres, wall conductivity, stimulus, dream, pose, KIT IDs)
- step0_report34.py -> report34_<H>.json; step0_report35.py -> report35_<H>.json; step0_cavities.py -> cavities.json;
  step0_hosts.py -> hosts.json
- runs/v52_2026-10-20/00_step0/: dataset_info.csv (downloaded), hosts/ (KCL_torso1.zip and its extract, the Moss header
  and Material array, the Zenodo record JSONs, the KCL info PDF)
