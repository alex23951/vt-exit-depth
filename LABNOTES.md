# Lab notes: VT exit depth study

Every simulation run is logged here, including failed and test runs. Newest entries
go at the bottom. Never delete or rewrite old entries; add dated corrections instead.

## Entry template

```
### <run ID>: <one-line purpose>
- Date/time:
- Git commit:
- Status: running / ok / failed / aborted
- Command:
- Model: eikonal | reaction-eikonal RE+ | RE− ; ionic model:
- Geometry / resolution:
- Exit site: location; transmural depth = <0–1> (<endo|intramural|epi>)
- CV (long/trans), fibres:
- Lead fields: computed fresh | reused from <run ID>
- Output folder:
- Runtime:
- Criteria: pseudo-delta= ms, IDT(V2)= ms, shortest RS= ms, MDI= , q in I= 
- Observations / next steps:
```

---

## Log

### 2026-09-27_ext_endo: wedge, endocardial stimulation, extracellular electrograms
- Date/time: 2026-09-27 21:22
- Git commit: none (repository has no commits yet)
- Status: ok
- Command: `cd runs && python ../sims/07_extracellular/run.py --tm-stim-location endo --np 4 --ID 2026-09-27_ext_endo`
- Model: monodomain (full reaction-diffusion, not eikonal); ionic model tenTusscherPanfilov with ENDO/MCELL/EPI cell types by layer (from example 02_EP_tissue/07_extracellular, unmodified)
- Geometry / resolution: 0.25 x 50 x 10 mm wedge (one element thick, quasi-2D), 250 um, no bath
- Exit site: endocardial surface, mid apex-to-base; transmural depth = 0 (endo)
- CV (long/trans), fibres: isotropic conductivities (g_i 0.174, g_e 0.625 S/m) so fibre rotation (+60/-60) has no effect
- Lead fields: n/a; extracellular potentials by phie recovery at 7 points on the transmural centreline (unbounded-medium assumption)
- Output folder: runs/2026-09-27_ext_endo
- Runtime: 7.0 s (4 cores)
- Status update: ok. First activation z=+5 mm (endo) as intended; total activation 51.5 ms. No errors (petsc_err_log empty). Console log: runs/2026-09-27_ext_endo.log
- Criteria: n/a (not a 12-lead ECG)
- Observations / next steps: Steepest local downstroke: endo surface 0.8 ms, mid-wall 10.1 ms, epi surface 19.5 ms (transmural conduction ~0.5 m/s). Far-field onset immediate after stimulus; endo-side fluid goes negative (wave moving away, -42 uV at 5 ms, 5 mm out), epi-side positive (+8 uV). Figure: figures/2026-09-27_ext_endo_vs_epi.png (+ .csv). Compare with 2026-09-27_ext_epi.

### 2026-09-27_ext_epi: wedge, epicardial stimulation, extracellular electrograms
- Date/time: 2026-09-27 21:22
- Git commit: none (repository has no commits yet)
- Status: ok
- Command: `cd runs && python ../sims/07_extracellular/run.py --tm-stim-location epi --np 4 --ID 2026-09-27_ext_epi`
- Model: monodomain (full reaction-diffusion, not eikonal); ionic model tenTusscherPanfilov with ENDO/MCELL/EPI cell types by layer (from example 02_EP_tissue/07_extracellular, unmodified)
- Geometry / resolution: 0.25 x 50 x 10 mm wedge (one element thick, quasi-2D), 250 um, no bath
- Exit site: epicardial surface, mid apex-to-base; transmural depth = 1 (epi)
- CV (long/trans), fibres: isotropic conductivities (g_i 0.174, g_e 0.625 S/m) so fibre rotation (+60/-60) has no effect
- Lead fields: n/a; extracellular potentials by phie recovery at 7 points on the transmural centreline (unbounded-medium assumption)
- Output folder: runs/2026-09-27_ext_epi
- Runtime: 7.5 s (4 cores)
- Status update: ok. First activation z=-5 mm (epi) as intended; total activation 51.5 ms. No errors. Console log: runs/2026-09-27_ext_epi.log
- Criteria: n/a (not a 12-lead ECG)
- Observations / next steps: Exact mirror image of 2026-09-27_ext_endo: epi surface 0.8 ms, mid-wall 10.1 ms, endo surface 19.5 ms; far-field onset timing identical, only polarity flips. Expected, because this wedge has uniform isotropic conduction and no fast endocardial (Purkinje) layer, so nothing slows the epicardial onset. To test pseudo-delta-type criteria the model needs fast endocardial conduction and/or anisotropy. Note: the example's compute_tmECG() labels point 0 as endo and point 2 as epi; the coordinates (ecg.pts) show the reverse. Not used here.

#### Note 2026-09-27 (applies to 2026-09-27_ext_endo and _ext_epi)
- Meshalyzer showed a blank window under WSL, and headless PNG export (-P) rendered pure black even with the preset background, so the GL rendering path looks broken here (unresolved). Made face-on activation and Vm snapshot maps in Python instead: figures/2026-09-27_ext_wedge_maps.png (script analysis/plot_wedge_maps.py). They confirm activation starts on the intended surface and spreads as a semicircle, crossing the wall in about 19 ms.

### 2026-10-02_tuneCV_tomek_500um: convert target CVs to conductivities (Tomek, 0.5 mm)
- Date/time: 2026-10-02 17:10
- Git commit: none (repository has no commits yet)
- Status: ok
- Command: `cd runs/2026-10-02_tuneCV_tomek_500um && tuneCV --model Tomek --resolution 500 --velocity <v> --converge true --np 1 --ID tune_v<v>` for v = 0.6 (fibre), 0.4 (sheet), and sheet-normal candidates 0.15–0.55 m/s
- Model: monodomain 1D strand (tuneCV), ionic model Tomek (ToR-ORd), default parameters
- Geometry / resolution: 1 cm cable, 500 um, dt 10 us
- Exit site: n/a (calibration)
- CV (long/trans), fibres: n/a
- Lead fields: n/a
- Output folder: runs/2026-10-02_tuneCV_tomek_500um
- Runtime: ~4 s per CV (10 CVs)
- Criteria: n/a
- Observations / next steps: tuneCV --converge (1% tolerance, bidomain-equivalent harmonic mean, beqm=1). Tuned (gi, ge) S/m [last measured strand CV]: 0.15 -> 0.0541, 0.1943 [0.159]; 0.20 -> 0.0833, 0.2993 [0.191]; 0.25 -> 0.1038, 0.3727 [0.260]; 0.30 -> 0.1379, 0.4954 [0.291]; 0.35 -> 0.1673, 0.6009 [0.342]; 0.40 -> 0.1995, 0.7166 [0.390]; 0.45 -> 0.2312, 0.8306 [0.444]; 0.50 -> 0.2668, 0.9584 [0.492]; 0.55 -> 0.3039, 1.0915 [0.540]; 0.60 -> 0.3376, 1.2126 [0.604]. tuneCV overwrites tune.json each call, so the per-CV values were copied from each tune_v<v>.out into tune_v<v>.json in the same folder (these are what the wedge script reads). Low CVs converge less tightly at 0.5 mm (0.15 and 0.20 within ~5%); the wedge measures transit directly, so this does not affect the calibration result. No Tomek prepacing (tuneCV default initial state).

### 2026-10-02_cvcal_vn0.2: first test of the transmural calibration wedge (baseline sheet-normal 0.2 m/s)
- Date/time: 2026-10-02 17:20
- Git commit: none (repository has no commits yet)
- Status: ok (first attempt crashed after the simulation finished, in my result-reading code; fixed and rerun with the same ID)
- Command: `cd runs && python ../sims/cv_calibration/run.py --tune-f T/tune_v0.6/tune.json --tune-s T/tune_v0.4/tune.json --tune-n T/tune_v0.2/tune.json --np 4 --ID 2026-10-02_cvcal_vn0.2` (T = 2026-10-02_tuneCV_tomek_500um; see note on json paths in the results entry)
- Model: monodomain reaction-diffusion; ionic model Tomek (ToR-ORd), default parameters, single cell type, no prepacing
- Geometry / resolution: 2 x 2 x 10 mm block (10 mm wall), 500 um tets, dt 10 us
- Exit site: whole endocardial surface stimulated at once (normal endo-first activation); depth 0 (endo)
- CV (fibre/sheet/sheet-normal): 0.6 / 0.4 / 0.2 m/s via tuneCV; fibres Bayer 2012 rule (fibre +60 -> -60, sheet -65 -> +25, endo -> epi)
- Lead fields: n/a
- Output folder: runs/2026-10-02_cvcal_vn0.2
- Runtime: 5 s (4 cores)
- Criteria: n/a
- Observations / next steps: Transit 7 -> 1 mm below epi = 15.17 ms (target 12.6). Total activation 30.3 ms. Local transmural speed rises from ~0.19 m/s near the endocardium to ~0.42 m/s near the epicardium: with this fibre rule the outer wall conducts transmurally mostly along the SHEET axis (see summary note below). No PETSc errors.

### 2026-10-02_cvcal_vn{0.15,0.25,0.3,0.35,0.4,0.45,0.5,0.55}: sheet-normal CV sweep (8 runs, one folder each)
- Date/time: 2026-10-02 17:30
- Git commit: none (repository has no commits yet)
- Status: ok (all 8)
- Command: as 2026-10-02_cvcal_vn0.2 with `--tune-n T/tune_v<vn>.json --ID 2026-10-02_cvcal_vn<vn>`, `--overwrite-behaviour overwrite`
- Model / geometry / resolution / exit site / fibres: identical to 2026-10-02_cvcal_vn0.2; only the sheet-normal CV changes
- Output folders: runs/2026-10-02_cvcal_vn<vn>
- Runtime: 2-7 s each
- Observations / next steps: Transit 7 -> 1 mm below epi (ms), by sheet-normal CV: 0.15 -> 15.48; 0.20 -> 15.17; 0.25 -> 14.98; 0.30 -> 14.65; 0.35 -> 14.35; 0.40 -> 14.11; 0.45 -> 13.95; 0.50 -> 13.81; 0.55 -> 13.69. Total activation 33.1 -> 21.9 ms. 12.6 ms is NOT reached anywhere in the allowed 0.15-0.55 range: the sheet-normal CV only moves the outer-wall transit by 1.8 ms across the whole range. No PETSc errors.

### 2026-10-02_cvcal_swap_vn{0.4,0.45,0.5,0.55}: DIAGNOSTIC only, sheet angles shifted +90 deg (4 runs)
- Date/time: 2026-10-02 17:35
- Git commit: none (repository has no commits yet)
- Status: ok (all 4)
- Purpose: test what sheet-normal CV would give 12.6 ms if the sheet-normal axis (not the sheet axis) carried transmural conduction. Not a proposed model change.
- Command: as the sweep plus `--sheet 25 115 --ID 2026-10-02_cvcal_swap_vn<vn>`
- Everything else identical to 2026-10-02_cvcal_vn0.2
- Output folders: runs/2026-10-02_cvcal_swap_vn<vn>
- Observations: Runtime 2-4 s each. Transit (ms): 0.40 -> 14.11 (same as the unswapped run, as it must be when sheet = sheet-normal CV, a useful sanity check); 0.45 -> 12.77; 0.50 -> 11.65; 0.55 -> 10.75. Linear interpolation gives 12.6 ms at sheet-normal ~0.46 m/s. Diagnostic only; the swapped angles are NOT adopted.

#### Note 2026-10-02: model-parameter checks for freezing (summary, NOT frozen; for Alex to review)
- **openCARP version**: v20 install, `openCARP -buildinfo` reports GIT tag `latest`, hash `ffce195` (ffce19513ca9). carputils in ~/venv_carputils.
- **Tomek (ToR-ORd)**: present. `bench --list-imps` lists `Tomek` (use `-imp_region[i].im Tomek`) and also `Tomek20Land17_DynSarc` (coupled mechanics, not needed). No tenTusscherPanfilov fallback required.
- **Which axis carries transmural conduction** (checked by building a mesh with the planned angles and reading the fibre/sheet vectors in the .lon file): in openCARP's mesher (and in the Bayer 2012 convention) a sheet angle of 0 means the sheet axis points straight across the wall. With sheet -65 deg (endo) -> +25 deg (epi), transmural conduction runs mainly along the sheet-NORMAL axis in the inner ~3 mm of the 10 mm wall and mainly along the SHEET axis beyond that. In the 1-7 mm-below-epi band the sheet axis stays within ~25-40 deg of the transmural direction (from the mesher vectors), so the sheet CV (0.4) dominates there. Fibres always lie in the wall plane, so the fibre CV does not affect transmural transit.
- **Calibration result (Taggart 2000 target, 12.6 ms over 1-7 mm below epi, whole endocardium activated)**: with fibre 0.6 / sheet 0.4 m/s fixed and the planned angles, no sheet-normal CV in 0.15-0.55 m/s reaches 12.6 ms (range 15.5 ms at 0.15 to 13.7 ms at 0.55; baseline 0.2 gives 15.2 ms). If the roles were swapped so the sheet-normal axis carried transmural conduction (diagnostic only), 12.6 ms needs a sheet-normal CV of ~0.46 m/s, which matches Durrer 1970's 0.46 m/s upper cross-check.
- **Decision needed (Alex)**: (a) treat the "transmural = sheet-normal" assumption as a convention mismatch and shift the sheet angles so the sheet-normal axis is transmural, then use ~0.46 m/s; or (b) keep the angles and calibrate the SHEET CV instead (changes the fixed 0.4); or (c) keep everything and accept ~13.7-15 ms transit. No value was frozen.
- **Resolution / numerics**: 0.5 mm tetrahedra (finer end of the planned 0.5-1 mm), dt 10 us, monodomain, Tomek default (endo) cell type, no prepacing, 10 mm wall, 2 x 2 mm block. Not yet repeated at 1 mm.
- **Orientation caveat for the old example wedge (sims/07_extracellular)**: the mesher applies the "endo" angles at z min, but that script tags/stimulates z max as endo. Harmless there (isotropic), but any future script must put the endocardium at z min. sims/cv_calibration/run.py does.
- **No ECG-criteria paper values were used** (Berruezo 2004 etc. held out).
- Commands: see the 2026-10-02_tuneCV_tomek_500um, _cvcal_vn*, _cvcal_swap_vn* entries above. New script: sims/cv_calibration/run.py.

### 2026-10-02_tuneCV_tomek_1000um: CV -> conductivity at 1 mm (PROVISIONAL option (a) work)
- Date/time: 2026-10-02 17:50
- Git commit: none (repository has no commits yet)
- Status: ok
- Command: `cd runs/2026-10-02_tuneCV_tomek_1000um && tuneCV --model Tomek --resolution 1000 --velocity <v> --converge true --np 1 --ID tune_v<v>` for v = 0.6, 0.4, 0.4-0.55
- Model: monodomain 1D strand, Tomek default parameters; 1 cm cable, 1000 um, dt 10 us
- Output folder: runs/2026-10-02_tuneCV_tomek_1000um
- Runtime: ~5-10 s per CV
- Observations / next steps: Tuned (gi, ge) S/m [last measured strand CV]: 0.40 -> 0.3368, 1.2096 [0.410]; 0.42 -> 0.3569, 1.2820 [0.429]; 0.44 -> 0.3773, 1.3553 [0.449]; 0.46 -> 0.3980, 1.4296 [0.469]; 0.48 -> 0.4190, 1.5049 [0.488]; 0.50 -> 0.4402, 1.5811 [0.508]; 0.55 -> 0.5065, 1.8192 [0.540]; 0.60 -> 0.5606, 2.0138 [0.591]. Converges less tightly at 1 mm (~1.5-2.5% off, 13-14 iterations). Conductivities are ~1.6x the 0.5 mm values for the same CV (coarse mesh slows conduction), so values are resolution-specific. Also tuned at 0.5 mm (added to 2026-10-02_tuneCV_tomek_500um): 0.42 -> 0.2064, 0.7415; 0.44 -> 0.2243, 0.8056; 0.46 -> 0.2382, 0.8557; 0.48 -> 0.2524, 0.9067.

### 2026-10-02_cvcalA_{500,1000}um_vn<vn>: PROVISIONAL option (a), sheets parallel to the wall (pending Alex's choice of a/b/c)
- Date/time: 2026-10-02 17:58
- Git commit: none (repository has no commits yet)
- Status: ok (17 runs incl. 3 confirmation runs at interpolated conductivities: _vninterp at both resolutions and 500um _vn0.45)
- Purpose: under option (a) (sheet angle 90 deg at every depth, so the sheet-normal axis points straight across the wall), find the sheet-normal CV giving 12.6 ms over 1-7 mm below epi, at 0.5 and 1 mm; also record full-wall (endo -> epi surface) crossing time to compare with Durrer's 0.46 m/s. Requested by the coordinator as provisional work; earlier runs unchanged.
- Command: `cd runs && python ../sims/cv_calibration/run.py --sheet 90 90 --resolution <500|1000> --tune-f T/tune_v0.6.json --tune-s T/tune_v0.4.json --tune-n T/tune_v<vn>.json --np 4 --ID 2026-10-02_cvcalA_<res>um_vn<vn> --overwrite-behaviour overwrite` (T = tuneCV folder for that resolution); vn in 0.40-0.55
- Model: monodomain, Tomek default (endo) cell, no prepacing, dt 10 us
- Geometry: 2 x 2 x 10 mm block; fibres +60 -> -60 (unchanged), sheet 90 -> 90; fibre 0.6, sheet 0.4 m/s
- Exit site: whole endocardial surface (depth 0)
- Output folders: runs/2026-10-02_cvcalA_*
- Runtime: 2-8 s each
- Observations: Outer-6 mm transit / full-wall (endo->epi surface) time, ms, by tuneCV sheet-normal CV:
  - 0.5 mm: 0.40 -> 14.11/22.90; 0.42 -> 13.75/22.31; 0.44 -> 12.91/20.94; 0.46 -> 12.34/20.02; 0.48 -> 11.83/19.18; 0.50 -> 11.37/18.42; 0.55 -> 10.37/16.79
  - 1 mm: 0.40 -> 14.19/22.56; 0.42 -> 13.46/21.40; 0.44 -> 12.80/20.36; 0.46 -> 12.21/19.41; 0.48 -> 11.67/18.56; 0.50 -> 11.18/17.78; 0.55 -> 9.93/15.79
  - Confirmation: 0.5 mm, gi 0.2319 / ge 0.8329 S/m (tuneCV CV ~0.45) -> 12.59 ms outer 6 mm, 20.43 ms full wall; tune_v0.45 (gi 0.2312 / ge 0.8306) -> 12.62 / 20.47 ms. 1 mm, gi 0.3843 / ge 1.3805 (tuneCV CV ~0.45) -> 12.59 / 20.03 ms. No PETSc errors.
  - The tuneCV (1D cable) label is ~0.45 m/s at both resolutions, but the effective speed in the wedge is faster: 6 mm / 12.6 ms = 0.48 m/s in the outer wall, 10 mm / 20.0-20.4 ms = 0.49-0.50 m/s across the full wall. That is slightly ABOVE Durrer's 0.46 m/s upper cross-check (by ~6-8%). Likely contributors: the endo stimulus pad and the sealed epicardial boundary, which speeds conduction near the edge. For Alex to judge.

#### Note 2026-10-02: Alex chose option (a), "Rotate sheets" (decision card, relayed via the project thread)
- Sheets are parallel to the wall at every depth (mesher sheet angle 90 deg endo and epi), so the sheet-normal axis runs straight across the wall; fibre angles unchanged (+60 -> -60); fibre 0.6, sheet 0.4 m/s.
- Calibrated sheet-normal: tuneCV CV 0.45 m/s. Conductivities (gi / ge, S/m): 0.5 mm -> 0.2312 / 0.8306 (tune_v0.45); 1 mm -> 0.3843 / 1.3805 (interpolated). Gives 12.6 ms over 1-7 mm below epi; full-wall crossing 20.0-20.5 ms (effective 0.49-0.50 m/s vs Durrer 0.46). Not frozen; Alex freezes the table.

### 2026-10-02_wedgeA_{endoall,endopoint,endoall_nolayer}: anisotropic wedge + fast endocardial layer, activation check (3 runs)
- Date/time: 2026-10-02 18:15
- Git commit: none (repository has no commits yet)
- Status: running
- Purpose: add the three-speed anisotropy (option a) and the fast endocardial layer to the wedge and check endocardium-first activation still runs; the no-layer run is a reference.
- Command: `cd runs && python ../sims/wedge_aniso/run.py --tune-f T/tune_v0.6.json --tune-s T/tune_v0.4.json --tune-n T/tune_v0.45.json --tune-fast T/tune_v2.0.json --stim <endo-all|endo-point> --np 4 --ID 2026-10-02_wedgeA_<...>` (T = runs/2026-10-02_tuneCV_tomek_500um; no-layer run omits --tune-fast)
- Model: monodomain reaction-diffusion; Tomek default (endo) cell type everywhere, no prepacing; dt 10 us
- Geometry / resolution: 0.5 x 50 x 10 mm wedge (one element thick, apex y=-25, base y=+25, endo z=-5), 500 um tets
- Exit site: endo-all = whole endocardial surface (depth 0); endo-point = 1 x 1 x 0.5 mm endocardial pad at mid apex-to-base (depth 0)
- CV (fibre/sheet/sheet-normal): 0.6 / 0.4 / 0.45 (tuneCV) m/s; fibres +60 -> -60, sheet 90 -> 90 (sheets parallel to wall). Fast layer: isotropic 2.0 m/s (gi 2.3865, ge 8.5724), 0.8 mm, 10-90 % apex-to-base
- Lead fields: n/a
- Output folders: runs/2026-10-02_wedgeA_*
- Runtime:
- Observations:
- Status update 2026-10-02 18:20: runs finished without solver errors, but the stimulus is inadequate with the fast layer. endoall_nolayer is fine: all nodes active by 21.3 ms, outer-6 mm transit 12.62 ms (matches calibration), epi uniform 21.2 ms. endoall (with layer): the stimulus captured only outside the layer (apex/base endo 0.75 ms); endo inside the layer did not activate until ~17 ms (mid), total 34.4 ms. endopoint (pad inside the layer): no capture at all. Interpretation: the high-conductivity layer (gi 2.39 S/m) is a large current sink, so 100 uA/cm3 for 1 ms applied to the surface nodes is below threshold there. Realised layer thickness 0.83 mm (mesher tags whole elements). Next: stimulus strength test (technical setting, not a model assumption).

### 2026-10-02_wedgeA_stimtest_*: stimulus capture test in the fast layer (technical)
- Date/time: 2026-10-02 18:22
- Git commit: none (repository has no commits yet)
- Status: running
- Purpose: find the stimulus (strength, pad depth) that captures inside the fast layer. Setup otherwise identical to 2026-10-02_wedgeA_endopoint.
- Command: as 2026-10-02_wedgeA_endopoint plus `--stim-strength <S> --stim-depth <D> --duration 50 --ID 2026-10-02_wedgeA_stimtest_S<S>_D<D>`
- Output folders: runs/2026-10-02_wedgeA_stimtest_*
- Observations:
- Status update 2026-10-02 18:26: ok (5 runs, ~13 s each, no PETSc errors). Mid-endo LAT / last endo / total activation (ms): S200 D0 -> 0.55 / 22.2 / 34.0; S400 D0 -> 0.26 / 21.8 / 33.6; S800 D0 -> 0.13 / 21.5 / 33.4; S100 D1.0 -> 0.85 / 22.4 / 34.2; S200 D1.0 -> 0.45 / 22.0 / 33.8. Capture threshold in the layer lies between 100 and 200 uA/cm3 (surface pad). Chosen for the wedge runs: 200 uA/cm3, surface pad (same pad geometry as calibration). Stimulus strength changes LATs by < 1 ms.

### 2026-10-02_wedgeA_S200_{endoall,endopoint,endoall_nolayer}: repeat of the 3 activation-check runs with 200 uA/cm3 stimulus
- Date/time: 2026-10-02 18:27
- Git commit: none (repository has no commits yet)
- Status: running
- Command: as 2026-10-02_wedgeA_* plus `--stim-strength 200 --ID 2026-10-02_wedgeA_S200_<...>`
- Everything else identical to 2026-10-02_wedgeA_* (80 ms simulated)
- Output folders: runs/2026-10-02_wedgeA_S200_*
- Observations:
- Status update 2026-10-02 18:32: ok (3 runs, 14-17 s each, no PETSc errors, every node activated).
  - endoall (layer, 200 uA/cm3): endo activated 0.4-0.9 ms everywhere; epi breakthrough 19.5 ms over the layer region (first at y = -10.5 mm), 20.5 ms at apex/base strips without layer; total activation 20.6 ms. Outer-6 mm transit 12.62 ms mid-wedge, 12.54 ms apex/base: calibration preserved.
  - endoall_nolayer: total 20.7 ms, epi uniform 20.6 ms, outer-6 mm transit 12.62 ms.
  - endopoint (layer, mid apex-to-base pad): endo LAT along the layer 0.55 (y=0), 3.54 (5 mm), 6.74 (10 mm), 9.94 (15 mm), 12.88 (20 mm = layer edge); then slows to myocardial speed in the layer-free apical/basal 10 % (17.9 ms at 22.5 mm, 21.7 ms at 24.5 mm). Epi breakthrough 19.9 ms directly over the pacing site; total 34.0 ms. Outer-6 mm transit 13.0 ms mid, 9.5 ms near apex/base (oblique wavefronts there).
  - FLAG: effective speed along the fast layer is ~1.56 m/s (5 -> 15 mm), not the 2.0 m/s set by tuneCV. A thin (0.83 mm) fast layer bonded to slow myocardium loses current into it (electrotonic load), and at 0.5 mm the layer is only ~2 elements thick. Reaching an effective 2.0 m/s would need the layer conductivity tuned in the wedge rather than in a free 1D cable. That is a model-assumption choice for Alex; not changed.

#### Note 2026-10-02 18:40: sheet-normal setting (coordinator relay of the recommended choice)
- Keep the tuneCV setting 0.45 m/s for the sheet-normal axis. Effective speed in the wedge: 12.6 ms over the outer 6 mm = 0.48 m/s (full wall 20.0-20.4 ms = 0.49-0.50 m/s). Record the effective value for the eikonal runs, which take effective speeds.

### 2026-10-02_fastcal_{500,1000}um_v{2.0,1.5,3.0}_it<k>: fast-layer conductivity tuned INSIDE the wedge (PENDING Alex's choice on the fast-layer card)
- Date/time: 2026-10-02 18:40
- Git commit: none (repository has no commits yet)
- Status: ok (final values below). Aborted/failed iterations: 1000um_v2.0 at 200 uA/cm3 (no capture, it0 and crash at it1); 1000um_S400_v3.0 it1 (no capture at gi 10.3); 1000um_S800_v2.0 (stimulus test, 1 iteration). The first 500um_v2.0 attempt crashed after it1 while saving results (numpy bool in json); fixed and rerun.
- Purpose: find the layer conductivity for which the MEASURED speed along the endocardium is 2.0 m/s (and range ends 1.5 and 3.0 m/s), at 0.5 and 1 mm. Earlier 2.0 m/s tuneCV setting (gi 2.3865 / ge 8.5724) kept; revert to it if Alex picks "Keep setting".
- Command: `cd runs && python ../sims/wedge_aniso/tune_fast_layer.py --target <v> --resolution <500|1000> --tune-f T/tune_v0.6.json --tune-s T/tune_v0.4.json --tune-n <T/tune_v0.45.json at 500 | T/tune_interp.json at 1000> --start <json> --prefix 2026-10-02_fastcal_<res>um_v<v>`; each iteration runs sims/wedge_aniso/run.py with `--stim endo-point --stim-strength 200 --duration 25`
- Measurement: endo-point stimulus at y = 0; speed = 10 mm / (LAT at y = 15 mm minus LAT at y = 5 mm) on the endocardial surface (both inside the layer); gi and ge scaled together, g <- g (target/measured)^2, tolerance 1 %
- Model / geometry: as 2026-10-02_wedgeA_S200_endopoint (Tomek, monodomain, dt 10 us, 0.6 / 0.4 / 0.45 m/s, sheets parallel to wall, layer 0.8 mm, 10-90 % apex-to-base); at 1 mm the wedge is 1 mm thick and uses the 1 mm myocardial conductivities
- Output folders: runs/2026-10-02_fastcal_*  (+ <prefix>_result.json, <prefix>_it<k>_g.json)
- Runtime: 3-6 s per wedge run, 2-4 iterations per target
- Observations: in-wedge tuned fast-layer conductivities (gi / ge, S/m) -> measured speed:
  - 0.5 mm (stimulus 200 uA/cm3; layer 0.83 mm as meshed): 1.5 m/s -> 2.2107 / 7.9409 (1.501); 2.0 m/s -> 3.9154 / 14.0641 (2.018); 3.0 m/s -> 8.4071 / 30.1987 (2.998)
  - 1 mm (stimulus 400 uA/cm3, 800 for 3.0; layer 1.0 mm as meshed): 1.5 m/s -> 2.8314 / 10.1705 (1.493); 2.0 m/s -> 4.6205 / 16.5972 (2.012); 3.0 m/s -> 9.1370 / 32.8204 (2.978)
  - For comparison, the free-cable tuneCV value for 2.0 m/s (gi 2.3865) measures 1.56 m/s in the wedge at 0.5 mm. In-wedge 2.0 m/s needs ~1.6x that conductivity (0.5 mm).
  - Stimulus strength shifts LATs but not the measured speed (1 mm, 2.0 target: 400 vs 800 uA/cm3 -> 2.403 vs 2.402 m/s). Capture threshold rises with layer conductivity and coarser mesh.
  - FLAG: at 1 mm the mesher can only make a 1-element (1.0 mm) layer, not 0.8 mm, so 1 mm and 0.5 mm values are for slightly different layers.
  - Speed measured 5 -> 15 mm from the pacing site, i.e. well clear of the stimulus and of the layer edges (+-20 mm).

#### Note 2026-10-02 18:55: Alex chose "Measured 2.0" for the fast layer (fast-layer card, relayed via the project thread)
- The in-wedge re-tune (2026-10-02_fastcal_*) is Alex's choice, no longer pending. The free-cable tuneCV 2.0 setting (gi 2.3865 / ge 8.5724, measures 1.56 m/s) is superseded.
- Baseline fast layer = measured 2.0 m/s along the endocardium; range ends 1.5 and 3.0 m/s measured. Conductivities (gi / ge, S/m):
  - 0.5 mm: baseline 2.0 -> 3.9154 / 14.0641 (runs/2026-10-02_fastcal_500um_v2.0_result.json); 1.5 -> 2.2107 / 7.9409; 3.0 -> 8.4071 / 30.1987
  - 1 mm: baseline 2.0 -> 4.6205 / 16.5972 (runs/2026-10-02_fastcal_1000um_S400_v2.0_result.json); 1.5 -> 2.8314 / 10.1705; 3.0 -> 9.1370 / 32.8204 (runs/2026-10-02_fastcal_1000um_S800_v3.0_result.json)
- Stimulus needed for capture in the layer: 200 uA/cm3 at 0.5 mm; 400 at 1 mm (800 for the 3.0 m/s layer).
- Parameter table: ready for Alex to freeze; NOT frozen.

## 2026-10-02 17:37 (UTC 15:36): PARAMETERS FROZEN (Alex said "freeze" in the project thread)
Baseline model parameters for the VT exit-depth study. Change only with a new dated entry.
- Software: openCARP v20 install, buildinfo GIT tag `latest`, hash `ffce195`; carputils in ~/venv_carputils.
- Ionic model: `Tomek` (ToR-ORd), default parameters (endocardial cell type), no prepacing so far.
- Source model: monodomain, bidomain-equivalent harmonic-mean conductivities (tuneCV beqm=1, beta 0.14 cm^-1 tuneCV default); dt 10 us; LAT threshold -10 mV.
- Fibre rule: fibre +60 deg (endo) -> -60 deg (epi); sheets parallel to the wall (mesher sheet angle 90 deg throughout), so the sheet-normal axis is transmural (Alex's option (a)). In mesher blocks the endocardium is z min.
- Conduction velocities (tuneCV setting; effective in brackets):
  - fibre 0.6 m/s
  - sheet 0.4 m/s
  - sheet-normal 0.45 m/s [effective 0.48 m/s: 12.6 ms over 1-7 mm below epi, Taggart 2000; full wall 20.0-20.4 ms = 0.49-0.50 m/s; Durrer 0.46 cross-check]
  - fast endocardial layer: measured 2.0 m/s along the endocardium (in-wedge tuned, Alex's "Measured 2.0"); range ends 1.5 and 3.0 m/s measured; isotropic; 0.8 mm thick (0.83 mm as meshed at 0.5 mm, 1.0 mm at 1 mm); covers 10-90 % of apex-to-base, none in the apical and basal 10 %
- Conductivities, gi / ge (S/m):
  | | 0.5 mm | 1 mm |
  |---|---|---|
  | fibre 0.6 | 0.3376 / 1.2126 | 0.5606 / 2.0138 |
  | sheet 0.4 | 0.1995 / 0.7166 | 0.3368 / 1.2096 |
  | sheet-normal 0.45 | 0.2312 / 0.8306 | 0.3843 / 1.3805 |
  | fast layer 2.0 (baseline) | 3.9154 / 14.0641 | 4.6205 / 16.5972 |
  | fast layer 1.5 (range end) | 2.2107 / 7.9409 | 2.8314 / 10.1705 |
  | fast layer 3.0 (range end) | 8.4071 / 30.1987 | 9.1370 / 32.8204 |
  Sources: runs/2026-10-02_tuneCV_tomek_{500,1000}um/tune_v*.json (1 mm sheet-normal: tune_interp.json), runs/2026-10-02_fastcal_*_result.json.
- Stimulus (technical, not a model parameter): 200 uA/cm3 x 1 ms at 0.5 mm; 400 at 1 mm (800 for the 3.0 m/s layer).
- Held out (not used for any parameter): Berruezo 2004 and all other ECG-criteria papers.
- Known caveats carried forward: 1 mm and 0.5 mm fast layers differ in thickness; 1 mm tuneCV converged to ~1.5-2.5 %; calibration done in a 10 mm wall wedge, not yet in the biventricular mesh.
