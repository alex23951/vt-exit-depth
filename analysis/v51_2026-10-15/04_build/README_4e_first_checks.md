# Step 4.5 "First" checks (read only), 18 Oct 2026 15:20 CEST

Alex, 18 Oct 2026 13:10:35 UTC: "yes" (go for Step 4.5's read-only checks). Nothing was run or changed.

## 1. How 15_conductor.py tags blood, and why only 70 / 56 / 70 % of the cavity volume

Code: sims/biv_model/15_conductor.py blood(), lines 95-130.
- The heart is laid on 1 mm voxels. "Wall" voxels are those holding heart nodes or element centroids, closed by one
  voxel.
- A "cavity" voxel is a non-wall voxel with wall on both sides along all three axes, and inside the convex hull of the
  LV and RV endocardial nodes.
- A torso element becomes blood (tag 101, 0.7 S/m) if its centroid falls in a cavity voxel.

Blood actually tagged:

| Heart | Blood (mL) | Brief's cavity volume LV + RV (mL) | Fill |
|---|---|---|---|
| Y5HYEDL4 | 258.5 (LV 127.5, RV 131.0) | 172.0 + 197.9 | 70 % |
| 6G8DD8S5 | 148.5 | 157.8 + 107.2 | 56 % |
| 7D98EVAR | 208.0 | 172.8 + 122.5 | 70 % |

Why the fill is incomplete (from the code; the share of each cause is not measured):
- Near the valve openings there is no wall above, so the six-direction test fails and that blood stays torso, by design
  ("conservative at the valve openings").
- The one-voxel closing adds about 1 mm of "wall" along the endocardium, which excludes the blood next to it.
- Trabecular recesses and spaces outside the convex hull of the endocardial nodes are left out.
- The 1 mm voxel discretisation adds error.
- Inference: the dilated, rounder 6G8DD8S5 cavities lose more volume near the openings.

Brief C6-C8 replaces this with watertight cavity surfaces and a winding-number test.

## 2. Current (v5, "cb") conductivities, S/m

These are each heart's calibration.json values divided by s, so that the fibre values equal Clerc 1976.

| Heart (s) | fibre sigma_i / sigma_e | sheet | sheet-normal |
|---|---|---|---|
| Y5HYEDL4 (4.084) | 0.174 / 0.625 | 0.0592 / 0.2124 | 0.0725 / 0.2606 |
| 6G8DD8S5 (3.865) | 0.174 / 0.625 | 0.0722 / 0.2592 | 0.0760 / 0.2731 |
| 7D98EVAR (4.196) | 0.174 / 0.625 | 0.0614 / 0.2206 | 0.0712 / 0.2558 |

- Blood is 0.7 S/m and torso 0.2 S/m.
- v5.1 (C2) will instead use sigma_d = 0.174 (v_d / 0.60)^2 for sigma_i and 0.625 (v_d / 0.60)^2 for sigma_e.
  - Y5HYEDL4: sheet 0.0626 / 0.2250, normal 0.1114 / 0.4000.
  - HF hearts: sheet 0.0327 / 0.1174, normal 0.0546 / 0.1960.

## 3. ECG source term

- The v5 weights (13_fast_ecg.py weights, called with sigma 'm' and c = -1 by v5_adopted.py weights()) use the combined
  sigma_m = sigma_i sigma_e / (sigma_i + sigma_e) in the source stiffness matrix. They do not use sigma_i, as brief C5
  requires.
- The weights follow the fibre file. The stiffness reads the mesh's .lon, which for v5 is the fibres_E link. The torso
  .lon of the v5 lead fields was rebuilt from the same fibres (v5_adopted.py 63-86).
- Validation (13_fast_ecg.py docstring, 3 Oct 2026): sigma_m with c = -1 reproduces openCARP's own lead-field ECG to
  0.0002 mV on a monodomain beat and 0.000006 mV on an eikonal beat. So openCARP's monodomain mode (-bidomain 0) builds
  its ECG source from the monodomain conductivity, although its manual (4.2.6, eqs 34-36) writes sigma_i.
- **Consequence:**
  - With equal anisotropy (v5.1 C2), sigma_m / sigma_i = 0.625 / 0.799 = 0.782 in every direction. Switching to sigma_i
    scales every lead by 1.28, with timing and shape unchanged.
  - Measures that use thresholds would move: the 0.05 mV wave threshold, the 20 uV CSE limit, the 10 uV noise, Q
    amplitudes and Sokolow-Lyon.
  - With sigma_i, the brief's C9 check ("weights match openCARP within 0.0002 mV") cannot pass as written. It can be
    run with sigma_m to prove the code, then switched.

# Step 4.5 C1-C8, 18 Oct 2026 15:26-15:44 CEST (conductor51.py; no openCARP run)

ECG source: sigma_i (Alex, 13:22:54 UTC, "Intracellular").

| Check | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| C3 check values (4 decimals) | PASS | PASS | PASS |
| C5 sigma_m ratio = (v_d / 0.60)^2 to 1e-6 | PASS | PASS | PASS |
| C6 LV volume (mL) vs audit | 172.03 vs 172.0 | 157.76 vs 157.8 | 172.79 vs 172.8 |
| C6 RV volume (mL) vs audit | 197.90 vs 197.9 | 107.20 vs 107.2 | 122.48 vs 122.5 |
| C6 every edge in 2 triangles | PASS | LV PASS, RV 15 pinch edges (4 triangles) | LV PASS, RV 11 pinch edges |
| C6 orientation consistent | PASS | PASS | PASS |
| C8 blood / cavity volume (+-2 %) | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 |
| C8 torso volume inside (< 1 %) | 0.06 / 0.09 % | 0.07 / 0.13 % | 0.05 / 0.11 % |
| C8 endocardial faces bordering blood (>= 95 %) | 100 / 99.99 % | 100 / 100 % | 100 / 100 % |
| C8 blood beyond the valve rings | none (closed caps) | none | none |

Notes:
- **C6 volumes:** the closed surfaces reproduce the audit's volumes to within 0.03 %.
- **Pinch edges:** at a pinch edge, two triangles run in each direction. The surface is closed and consistently oriented,
  so the inside test is unaffected. As written, C6 still fails for the two HF RVs; Alex to decide.
- **Blood fill:** now 100 % of every cavity, up from v5's 70 / 56 / 70 %.
- **Valve rings:** the rings are saddle-shaped (rms 0.4-2.1 mm from a plane). So up to ~1.3 mL of blood lies more than
  0.5 mm beyond a best-fit ring plane, but never beyond the ring caps.
- **Mesh size:** median element edge in the blood is 0.92 mm, so no remesh is needed.

Files:
- data/biv/<H>/torso/full_nofast_blood_v51.elem / .lon / .pts.
- params/v51_conductivities.json.
- conductor51_<H>.json.
