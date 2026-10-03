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

### 2026-10-02 pilot draw from the Solis-Lemus 2026 cohort (no simulation)
- Date/time: 2026-10-02 17:50
- Git commit: a27f3a9 (uncommitted changes: this entry, sims/cohort/draw_pilot.py)
- Alex chose "Pilot hearts" on the download card (relayed via the project thread).
- Source: Zenodo concept DOI 10.5281/zenodo.17048090, version 10.5281/zenodo.19351401 (2026-03-31), CC-BY 4.0. Groups from the record's dataset_info.csv (26 control, 12 HF wide QRS, 12 HF narrow QRS).
- Method: `python sims/cohort/draw_pilot.py`. IDs sorted within each group; one heart drawn per group in the order control, HF wide QRS, HF narrow QRS with numpy.random.default_rng(20261002).
- Drawn: Y5HYEDL4 (control, M, paper case MC5, 0.36 GB zip, md5 a7e648775f75badcbfddb73df3e1d720); 6G8DD8S5 (HF wide QRS, F, FHF8, 0.38 GB, md5 8e8122eb09e0b1b0a65d13303159576b); 7D98EVAR (HF narrow QRS, F, FHF6, 0.33 GB, md5 48b4cc87b766d3fe6a70e481deb22f8a). Total 1.07 GB zipped.
- These three hearts are the PILOT only; they are excluded from the study draw and from confirmatory analyses.
- Download: NOT done. This session's permission check blocked the download; Alex needs to allow it or run it. md5 check therefore still pending (values above are from the Zenodo record).
- Note: dataset_info.csv's Translation_case column repeats FC5 (98EK6960 and FC5) and FC7 (D16RF7C3 and FC7). Possible duplicate hearts or labelling quirk; to check before the study draw.
- Update 2026-10-02 18:30: Alex downloaded the three heart zips (the extra torso "files-archive" link returned HTTP 400). md5 of all three matches the Zenodo record (Y5HYEDL4 a7e64877..., 6G8DD8S5 8e8122eb..., 7D98EVAR 48b4cc87...). Unzipped to data/cohort/<ID>/<ID>/ (0.69-0.81 GB each). data/ added to .gitignore. Torso set: torsoModels.zip (Zenodo 10.5281/zenodo.20086105, CC-BY 4.0), the 1.9 MB copy I fetched at 17:46 for inspection, md5 528b7c89d1a8ab86168a9d59a87a4ed1 matches the record; unzipped to data/torso/torsoModels/.
- Pilot heart Y5HYEDL4 (inspection only): simulation mesh myocardium_AV_FEC_BB_lvrv (.pts/.elem/.lon text + binary), 521,183 nodes, 2,638,070 linear tets, coordinates in um. Edge length mean 1.05 mm (5th-95th pct 0.83-1.31 mm), i.e. ~1 mm, not the 0.5 mm in the paper. Fibre file: 6 columns = fibre + sheet, unit and orthogonal. 29 element tags (tags_lvrv.json): LV 1, RV 2, LA 3, RA 4, Ao 5, PArt 6, valve planes MV 7, TV 8, AV 9, PV 10, vein/appendage caps 11-17, rings 18-24, FEC_LV 25, BB 26, AV_plane 27, FEC_RV 28, FEC_SV 29. Bounding box 0-129 x 0-116 x 0-132 mm (translated so the box starts at the origin). Base-to-apex direction (+0.26, -0.76, -0.60): apex to +x, -y, -z, consistent with CT patient axes in LPS (x to patient left, y to posterior, z to superior) with the origin shifted; the record says nothing about the frame.
- Torso T13 (mean shape per record): T_13_torso_coarse_surface.vtk (VTK polydata, outer skin only, 2,987 points / 5,970 triangles, mm) + T_13_electrodes.csv (x,y,z in mm; rows RA, LA, LL, V1-V6, RL). Electrode positions imply LPS axes too (+x patient left, -y anterior, +z superior). The zip also has meantorso_* files (4,355 points; electrodes differ from T13 by up to 11.6 mm), unexplained in the record; following the record, T13 is used.

### 2026-10-02_biv_timing: 2 ms timing test of the pilot ventricular model (Y5HYEDL4)
- Date/time: 2026-10-02 22:05
- Git commit: a27f3a9 (uncommitted changes: sims/biv_model/, sims/cohort/, .gitignore, LABNOTES.md)
- Status: running
- Purpose: measure runtime per simulated ms before the full check run (step 6).
- Command: `python sims/biv_model/06_check_run.py --tend 2 --np 6 --ID 2026-10-02_biv_timing`
- Model: monodomain, Tomek, frozen 1 mm parameters (see PARAMETERS FROZEN), dt 10 us
- Geometry: data/biv/Y5HYEDL4/bivF (375,190 nodes, 1,939,909 tets, ~1.05 mm edges), fibres from step 4, fast layer (tag 2) from step 5
- Exit site: LV endocardium, free wall, mid-level (z ~ 0.5); depth 0 (endo)
- Output folder: runs/2026-10-02_biv_timing
- Status update 2026-10-02 22:10: ok. 2 ms simulated in 42 s wall time (6 cores, including ~15 s setup), i.e. ~13 s per simulated ms. Stimulus (400 uA/cm3, 19 nodes within 1.5 mm of an LV free-wall mid-level endocardial node, z 0.50, phi -179 deg) captured: 140 nodes active by 2 ms. No errors. A full activation (100-160 ms) would take ~25-35 min, so the step-6 check run waits for Alex's OK (CLAUDE.md: ask before runs > 10 min).

#### Note 2026-10-02: first ventricular model from pilot heart Y5HYEDL4 (steps 1-5, no simulation)
- Scripts: sims/biv_model/01_extract.py ... 05_fastlayer.py (+ common.py); outputs in data/biv/Y5HYEDL4/ (git-ignored); summaries summary_01..05.json.
- Tools present: meshtool, openCARP, igbextract, numpy, scipy, pandas. Missing: gmsh, TetGen, meshio, pyvista, vtk (not needed so far; torso volume meshing later may need gmsh/TetGen or meshtool's own "generate mesh").
- Step 1, ventricles (meshtool extract mesh, tags 1, 2, 25, 28, 29; outflow-tract muscle kept up to the valve planes): 375,190 nodes, 1,939,909 tets, one connected piece. Boundary faces classified by the neighbouring four-chamber element: LV endo 45,467 faces, RV endo 55,852, epi 92,365, MV rim 1,563, TV rim 1,720, AV rim 1,382, PV rim 1,132, AV-plane interface 5,609, aortic wall 2,787, pulmonary wall 1,630, RA 13. 29,744 epicardial faces were missing from the authors' epicardium_for_sim.surf (all on the epicardial side, none touching endocardium) and were added to epi. Four-chamber mesh kept unchanged for placement.
- Step 2, Laplace solves (openCARP experiment 2, unit isotropic conductivity): zeta, basal, ot, w, phi_epi, phi_lv, phi_rv, v; ~15 s each. Apex = all nodes within 5 mm of the LV epicardial apex point (369 nodes): a single-node apex gave a degenerate field (~1 everywhere; first attempt, re-solved). w has 0.01 % of nodes slightly outside 0-1 (clipped).
- Step 3, coordinates (Bayer 2018 UVC idea; outflow tracts handled by putting all four valve rims and the aortic/pulmonary interfaces in the base boundary, as in Doste 2019): z apex-to-base (Laplace, remapped monotonically to follow distance along the LV long axis: r = 0.989 vs 0.940 raw; raw field kept as z_laplace); rho transmural (0 endo, 1 epi; exactly 0/1 on the surfaces); sep (septal depth, LV endo 0 -> RV endo 1); v (LV 0 / RV 1; matches RV-only tags 99.95 %, puts 84 % of cohort-"LV" nodes on the LV side because the cohort LV label includes the whole septum); phi rotational (0 = septum direction, +90 deg anterior). Apex to MV/TV-rim centroid 100.8 mm.
- Step 4, fibres: Bayer 2012 LDRB (with bislerp), frozen angles +60 -> -60, sheet angle 0 = sheets parallel to wall; Doste 2019 OT rule: longitudinal direction blended by w between apex->MV/TV and apex->AV/PV gradients; OT angles endo 90 deg, epi 0 deg, sheet 0. Sheet-normal within 0.7 deg (median) of transmural. Difference from the cohort's own fibres: median 9.5 deg overall (8.8 deg ventricle body, 27.1 deg in outflow tracts w < 0.5; 83 % of elements within 20 deg).
- Step 5, fast layer: every element touching LV/RV endocardium with element z in 10-90 %: 222,581 elements (11.5 %), mean thickness 0.89 mm. Overlap with the cohort's own fast-layer tags (25, 28, 29): Jaccard 0.81; 96 % of the cohort layer is inside ours; the cohort layer spans z 0.15-0.82 (5th-95th pct).
- Step 7 (no download): the torso record's LATs.zip holds ~130 atrial models (LAE###.vtk, g###.vtk, ~30-50 MB each), one per atrial shape, each paired with all 25 torsos in the results; whether they sit in torso coordinates is not stated and can't be confirmed without opening one file.
- Note 2026-10-02 22:20 (coordinator relay): the 5 mm apex patch and the distance-scaled apex-to-base coordinate are accepted and kept. The 25-35 min full check run is skipped; a 36 ms run replaces it.

### 2026-10-02_biv_check36: 36 ms check run of the pilot ventricular model (Y5HYEDL4)
- Date/time: 2026-10-02 22:21
- Git commit: a27f3a9 (uncommitted changes: sims/biv_model/, sims/cohort/, .gitignore, LABNOTES.md)
- Status: running
- Purpose: measure the fast layer's speed along the LV endocardium (target 2.0 m/s) and the LV free-wall endo -> epi time near the pacing site.
- Command: `cd sims/biv_model && python 06_check_run.py --tend 36 --np 6 --ID 2026-10-02_biv_check36`
- Model / geometry / exit site / stimulus: as 2026-10-02_biv_timing (LV free-wall endocardium, mid-level, z 0.50; depth 0 = endo)
- Measurement: speed = slope of geodesic distance along the LV endocardium vs LAT, fast-layer nodes 10-40 mm from the site (2.5 mm bins, medians); transmural = epi LAT minus nearest LV-endo LAT, LV free wall, z 0.3-0.7, endo point within 20 mm of the site
- Output folder: runs/2026-10-02_biv_check36

#### Note 2026-10-02 22:15: atrial file for torso placement (Alex said yes to one 35 MB file)
- Fetched LATs/g001.vtk only (36.7 MB, zip CRC verified) from Zenodo 10.5281/zenodo.20086105 LATs.zip via range requests -> data/torso/atria/g001.vtk. VTK unstructured grid (ASCII), 75,231 nodes, 358,520 elements, mm, ~90 fine regional tags (Nagel SSM), fibres, LATs.
- The atria sit inside the T13 torso: 300/300 sampled atrial points inside the torso surface; atrial centroid (8.6, -30.1, 8.0) mm; same LPS-type axes as the torso and the cohort heart (LA to patient left and posterior of RA in both).
- Rigid fit (ICP, 90 % trimmed) of the pilot heart's own LA + RA (cohort tags 3, 4) onto g001: rotation 13.4 deg, translation (-9.8, -122.0, -82.0) mm applied to heart coordinates in mm; residual our->theirs median 2.4 mm (90th pct 5.5 mm), theirs->ours median 3.5 mm (90th 11.4 mm). Transform saved: data/torso/atria/Y5HYEDL4_to_g001_rigid.txt. So placing the heart by matching its atria to these SSM atria is feasible. Caveat (not checked): that each atrial model uses the same placement for all 25 torsos.
- Status update 2026-10-02 22:32 (2026-10-02_biv_check36): ok, no errors (petsc_err_log empty). Wall time 622 s (10.4 min, 6 cores), slightly over the 10-min guide. 44 % of nodes active by 36 ms; first epicardial breakthrough 18.2 ms.
  - Fast-layer speed along the LV endocardium: 4.0 m/s measured (1,614 nodes, 10-40 mm from the site) vs 2.0 m/s target from the 1 mm wedge calibration. NOT retuned. Possible causes, unverified: (1) the wedge calibration used a one-element-thick quasi-2D slab with a structured mesh, which may not transfer to this unstructured 3D mesh; (2) here the layer is every element touching the endocardium, a different cross-section from the wedge's box-tagged row; (3) the edge-path (Dijkstra) distance overestimates true surface distance by a few %, which only explains a small part.
  - LV free-wall endo -> epi time (z 0.3-0.7, within 20 mm of the site, 491 pairs): median 16.8 ms (p10-p90 16.0-17.7) over a median 11.0 mm wall = ~0.65 m/s effective, vs 12.6 ms over 6 mm (0.48 m/s) in the wedge. Not a like-for-like comparison: here activation enters the wall along a fast endocardium, so the wavefront is not planar.
  - Next step suggested: calibrate the fast layer (and check transmural speed) on this 3D mesh itself, e.g. a patch of the pilot heart, instead of the quasi-2D wedge. Needs Alex's decision.

### 2026-10-02_patch_*: implement the frozen measured targets on the heart mesh (LV free-wall patch of Y5HYEDL4)
- Date/time: 2026-10-02 22:45
- Git commit: a27f3a9 (uncommitted changes: sims/biv_model/, sims/cohort/, .gitignore, LABNOTES.md)
- Status: running
- Step A finding (setup check, heart run 2026-10-02_biv_check36 vs wedge run 2026-10-02_fastcal_1000um_S400_v2.0_it2): conductivities, isotropy, region mapping, dt, mass lumping, threshold and stimulus strength identical; only the parabolic PETSc option file differs (carputils ilu_cg vs openCARP default). The 4.0 m/s was a MEASUREMENT error: distance was taken along LV-endocardial surface edges, which on this rough CT endocardium is 2.1x the straight-line distance. With straight-line distance (as in the wedge), the same run gives 1.90 m/s (5-25 mm), 1.91 (5-20), 1.89 (10-25). Layer construction: fast elements touch the endocardium by 1 node (68k), 2 nodes (74k) or 3 nodes (81k); fast-layer nodes reach at most 1.6 mm deep (median 0, p90 1.07 mm), so the layer is ~one element thick but ragged.
- Purpose: tune the fast-layer conductivity on the heart mesh to a measured 2.0 m/s (and 1.5 / 3.0 range ends), then check the outer-6 mm transit (target 12.6 ms) with whole-endocardium activation.
- Command: `cd sims/biv_model && python 07_patch_tune.py --fast-scan 0.7,1.0,1.4 --fit` then confirmation / transit runs (see updates)
- Model: monodomain, Tomek, dt 10 us, frozen 1 mm myocardial conductivities, stimulus 400 uA/cm3 x 1 ms
- Geometry: LV free-wall patch of data/biv/Y5HYEDL4/bivF (v = 0, |phi| >= 120 deg, z 0.25-0.75, full thickness), same fibres and fast layer
- Output folders: runs/2026-10-02_patch_*; all results in data/biv/Y5HYEDL4/patch_runs.json
- Status update 2026-10-02 23:05: ok (11 patch runs, 43-90 s each, no errors; patch 68,121 nodes, 357,047 tets, 31,013 fast). Results in data/biv/Y5HYEDL4/patch_runs.json.
  - Fast layer, measured speed vs gi (ge = 3.592 gi): 2.3103 -> 1.29 m/s; 4.6205 (frozen 1 mm value) -> 1.89; 9.2410 -> 2.73. Fit speed = 0.826 gi^0.538. Confirmed: gi 3.0283 -> 1.50 m/s; 5.1670 -> 2.01; 10.9717 -> 2.97.
  - Outer-6 mm transit (whole patch endocardium, fast layer 5.1670): sheet-normal gi 0.3843 (frozen 1 mm value) -> 10.82 ms (14 % fast); 0.30 -> 12.54; 0.24 -> 14.22. Fit transit = 6.22 gn^-0.580. Confirmed: gn 0.2962 (ge 1.0642) -> 12.64 ms.

### 2026-10-02_biv_check30_tuned: 30 ms whole-heart confirmation with the heart-mesh conductivities
- Date/time: 2026-10-02 23:07
- Git commit: a27f3a9 (uncommitted changes)
- Status: running
- Command: `cd sims/biv_model && python 06_check_run.py --tend 30 --np 6 --ID 2026-10-02_biv_check30_tuned --g-fast 5.1670 18.5601 --g-n 0.2962 1.0642`
- Everything else as 2026-10-02_biv_check36 (same site, stimulus, mesh); speed now measured with straight-line distance, 5-25 mm
- Output folder: runs/2026-10-02_biv_check30_tuned
- Status update 2026-10-02 23:25 (2026-10-02_biv_check30_tuned): ok, 555 s wall, no errors (first background launch at 23:07 failed to start: wrong working folder, nothing ran). Fast-layer speed along the LV endocardium (straight-line, 5-25 mm): 2.04 m/s (target 2.0). LV free-wall endo -> epi near the site: median 19.8 ms (p10-p90 18.9-20.8) over 11.0 mm. First epicardial breakthrough 21.1 ms. 31 % of nodes active by 30 ms.

#### Note 2026-10-02 23:25: frozen measured targets implemented on the heart mesh (not new targets)
- The frozen targets are unchanged: fast layer measured 2.0 m/s (range 1.5 / 3.0), sheet-normal giving 12.6 ms over the outer 6 mm (Taggart 2000); fibre 0.6 and sheet 0.4 m/s settings unchanged.
- The 1 mm conductivities calibrated in the quasi-2D wedge do not reproduce those targets on the cohort heart mesh (Y5HYEDL4, ~1.05 mm unstructured tets): fast layer 1.89-1.90 m/s, outer-6 mm transit 10.8 ms.
- Heart-mesh implementation (gi / ge, S/m), from the LV free-wall patch, confirmed on the whole heart for 2.0 m/s:
  | | wedge 1 mm (frozen entry) | heart mesh |
  |---|---|---|
  | fast layer 2.0 m/s (baseline) | 4.6205 / 16.5972 | 5.1670 / 18.5601 |
  | fast layer 1.5 m/s | 2.8314 / 10.1705 | 3.0283 / 10.8778 |
  | fast layer 3.0 m/s | 9.1370 / 32.8204 | 10.9717 / 39.4111 |
  | sheet-normal (12.6 ms outer 6 mm) | 0.3843 / 1.3805 | 0.2962 / 1.0642 |
  | fibre 0.6, sheet 0.4 | unchanged | unchanged |
- Speed measured with straight-line distance; surface-edge paths on this CT endocardium are ~2x longer and gave a spurious 4.0 m/s in 2026-10-02_biv_check36.
- Open question for Alex: whether each cohort heart needs its own patch calibration (likely, if element size varies), or one set per resolution.

### 2026-10-02_lf_T13_Y5HYEDL4: heart in torso T13, torso mesh and lead fields (12-lead)
- Date/time: 2026-10-02 23:45
- Git commit: a27f3a9 (uncommitted changes)
- Status: running (lead fields)
- Placement: ventricles (bivF) moved by the rigid atrial fit (rotation 13.4 deg, translation (-9.8, -122.0, -82.0) mm), i.e. matched to ONE SSM atrial geometry (g001). Heart bbox in torso frame (-16.0, -111.3, -67.0) to (105.6, -4.5, 54.2) mm.
- Torso mesh (sims/biv_model/08_torso.py mesh, 2 min 50 s): T13 skin resampled to ~8 mm edges, ventricular boundary kept exactly as an inner hole, meshtool generate mesh (mode 1, sizing from surface edges), merged with the ventricles. Result 1,983,222 nodes, 12,528,941 tets: heart 1,939,909 (tags 1, 2), torso 10,589,032 (tag 100); torso volume 34.6 L; torso edge length p5/p50/p95 0.72 / 1.03 / 6.91 mm (fine near the heart, so the mesh is large). Problems fixed: 19 tiny tag-0 elements (< 0.3 mm3) in a crevice of the heart surface removed; meshtool merge dropped the sheet directions, so full.lon was rebuilt with the heart's fibre + sheet vectors (heart elements first, same order, checked).
- Torso conductor: uniform 0.2 S/m (blood, lungs, cavities all 0.2; simplification for now). Heart: heart-mesh conductivities (fast 5.1670 / 18.5601, sheet-normal 0.2962 / 1.0642, fibre and sheet as frozen 1 mm).
- Electrodes: nearest skin node to each T13 electrode; snap distance RA 3.8, LA 3.4, LL 1.8, V1 4.2, V2 3.5, V3 5.1, V4 1.6, V5 4.3, V6 3.1, RL 2.1 mm.
- Command: `cd sims/biv_model && python 08_torso.py leadfield` (carputils leadfield_setup 12-lead, experiment 4 with Vm from 2026-10-02_biv_check30_tuned, 4 processes)
- Output folder: runs/2026-10-02_lf_T13_Y5HYEDL4
- Status update 2026-10-02 23:55 (2026-10-02_lf_T13_Y5HYEDL4): ok, 423 s wall (4 processes), no errors, fit in memory (7.7 GB machine). 12 lead fields written (runs/2026-10-02_lf_T13_Y5HYEDL4/POSTPROC_DIR/LF_*.igb, 375,190 values each = heart nodes, reusable via --lf_dir for every exit site on this heart/torso). Test ECG from the 30 ms check-run Vm (5 ms frames only, first 30 ms of the QRS): plumbing check only, not interpretable. Values at 5-25 ms: lead I small negative (to -0.11 mV), II/III/aVF positive (to +0.40-0.45 mV), V5-V6 positive; all leads change sharply in the 30 ms frame (after epicardial breakthrough at 21 ms), which needs finer ECG sampling (1 ms) and a full-QRS run to judge.
- Next: full-length run (whole QRS, ECG at 1 ms) for one site, after Alex OKs the runtime (~13 s per simulated ms -> ~25-35 min).

### 2026-10-02_biv_fullqrs: full-QRS run of the pilot heart with 12-lead ECG (Alex said yes to the ~30 min run)
- Date/time: 2026-10-03 00:05
- Git commit: a27f3a9 (uncommitted changes)
- Status: running
- Purpose: first full paced beat and 12-lead ECG from the heart-in-torso model; check that an LV free-wall endocardial paced beat looks plausible.
- Commands (one chained background job):
  `python sims/biv_model/06_check_run.py --tend 140 --spacedt 1 --np 6 --ID 2026-10-02_biv_fullqrs --g-fast 5.1670 18.5601 --g-n 0.2962 1.0642`
  `python sims/biv_model/08_torso.py leadfield --vm runs/2026-10-02_biv_fullqrs/vm.igb --lf-dir runs/2026-10-02_lf_T13_Y5HYEDL4/POSTPROC_DIR --run-id 2026-10-02_biv_fullqrs_ecg --ecg-dt 1 --tend 140`
  `python sims/biv_model/09_plot_ecg.py runs/2026-10-02_biv_fullqrs_ecg/POSTPROC_DIR runs/2026-10-02_biv_fullqrs_ecg/ecg12.png`
- Model: monodomain, Tomek, dt 10 us; heart-mesh conductivities (calibration.json); Vm saved every 1 ms
- Exit site: LV free-wall endocardium, mid-level (z 0.50); depth 0 (endo)
- Lead fields: reused from 2026-10-02_lf_T13_Y5HYEDL4 (T13 torso, uniform 0.2 S/m)
- QRS rule (provisional): sum of |ECG| over 12 leads; onset/offset = first/last time above 2 % of its maximum
- Output folders: runs/2026-10-02_biv_fullqrs, runs/2026-10-02_biv_fullqrs_ecg
- Status update 2026-10-03 00:50 (2026-10-02_biv_fullqrs + _ecg): ok, no errors. Simulation 2,400 s wall (140 ms, 6 cores); ECG projection with reused lead fields 59 s. All nodes activated; total activation 118.6 ms after the stimulus; fast layer 2.04 m/s; first epicardial breakthrough 21.1 ms.
  - 12-lead plot: runs/2026-10-02_biv_fullqrs_ecg/ecg12.png (+ ecg12.json).
  - Morphology (from the plot): small, slow initial deflection for the first ~20 ms (until epicardial breakthrough), then the main QRS. Lead I biphasic, small r then S (net slightly negative, +0.53 / -0.61 mV); aVL positive (1.1 mV); II, III, aVF predominantly negative (to -1.8 mV, superior axis); aVR positive; V1 dominant R (+2.3 mV, small S); V2 R > S; V3 RS (transition); V4-V6 predominantly negative (to -2.1 to -2.3 mV, small initial r). Consistent with an LV free-wall origin (RBBB-like V1, negative lateral precordials, lead I not positive); the superior axis suggests the site sits on the inferolateral side, to be checked against its position in the torso.
  - QRS duration: the provisional ECG rule (2 % of the 12-lead summed |ECG|) gave 133 ms (onset 7, offset 140 = end of run) because the signal settles to a small non-zero plateau-phase level (~0.1 mV) instead of zero after ~115 ms. By eye the QRS ends at ~115-120 ms, i.e. ~110 ms from onset, consistent with total activation 118.6 ms. The QRS-end rule needs revising (e.g. relative to the post-QRS level or a slope criterion) before criteria are measured; Alex to decide the rule.
- Note 2026-10-03 00:55 (site position, 2026-10-02_biv_fullqrs): in torso coordinates the pacing site (node 313318) is at (62.2, -48.1, -44.1) mm, 23 mm inferior and 9 mm posterior to the LV cavity centroid. In the plane across the LV long axis it points mostly inferior (-0.87) and posterior (+0.45). So "LV free wall opposite the septum" (phi ~180 deg) lands on the INFERO-POSTERIOR LV wall in this heart, which explains the superior axis. Site labels must come from torso/anatomical directions, not from the UVC angle alone.

#### Note 2026-10-03 01:10: criteria measured on 2026-10-02_biv_fullqrs with ecg_depth_criteria v0.1.0 (no simulation)
- Package: Alex's ecg_depth_criteria.zip (placed in the project root) unpacked to code/ecg_depth_criteria/, used via PYTHONPATH (no install). Tests not run: pytest is not installed.
- Script: sims/biv_model/10_measure_ecg.py (20 ms flat 0 mV prepended because the simulated ECG starts at the stimulus; times below are ms after the stimulus). Region not given: the site (mid-level inferoposterior LV) fits none of the package's basal/apical regions. Output: runs/2026-10-02_biv_fullqrs_ecg/criteria.json.
- Detected mode: onset 29 ms, offset 103 (precordial) / 104 ms (any lead), QRS 74 ms. Pseudo-delta 3 ms (V3), IDT V2 15 ms, shortest RS 22 ms (V4), MDI 0.20 (V6) both definitions; q in I no; inferior q in all three leads; RBBB-like, superior axis. All interval criteria "not epi"; Vallès 4-step: not epi (step 1, inferior q); Piers Q-INF (superior-axis rule): epi (true).
- True mode (onset = stimulus 0 ms, offset = last activation 118.6 ms): QRS 119 ms. Pseudo-delta 32 ms, IDT V2 44 ms, shortest RS 42 ms (V6), MDI 0.40 (V6); q in lead I yes; inferior leads start positive; q in V2. Interval criteria all "not epi"; Vallès q in lead I: epi; no inferior q: epi; Vallès 4-step: EPI at step 4 (q in lead I); Piers Q-INF: not epi.
- Observations: the detector puts the onset at 29 ms, after the ~20-30 ms slow, low-amplitude start that comes from endocardial spread before epicardial breakthrough (21 ms), so every detected interval shrinks by ~29 ms and the morphology calls flip (the initial small deflections are what the true-mode q/r calls see). For this ENDOCARDIAL site, true mode gives a false "epicardial" call from the Vallès 4-step (q in lead I) and from Piers Q-INF in detected mode. The detected-vs-true gap is the measurement-error component the plan wants quantified.

#### Correction 2026-10-03: detected-mode criteria for 2026-10-02_biv_fullqrs (bug in my measuring script, not in the package)
- Cause: without a stimulus time, ecg_depth_criteria takes the first 40 ms of the signal as baseline (Settings.baseline_ms). 10_measure_ecg.py prepended only 20 ms of flat signal, so the "baseline" included the first 20 ms of the slow QRS start (up to 0.48 mV combined); the detector then treated everything below that as noise and put the onset at 29 ms. The 01:10 note's detected-mode values are wrong.
- Fix: 60 ms flat pad, passed explicitly as baseline_window_ms (0-59 ms) in both modes.
- Corrected detected mode: onset 2 ms, offset 103 (precordial) / 104 ms (any lead), QRS 101 ms; pseudo-delta 30 ms, IDT V2 42 ms, shortest RS 40 ms, MDI 0.40 (Vallès) / 0.39 (Daniels); q in lead I yes; inferior leads start positive. Re-run true mode (same baseline window): QRS 119 ms; pseudo-delta 32, IDT 44, shortest RS 42 ms, MDI 0.35; q in lead I yes; inferior start positive.
- Calls now agree in both modes: all interval criteria not epi; Piers Q-INF not epi; Vallès q in lead I EPI; Vallès no inferior q EPI; Vallès 4-step EPI (step 4). The remaining detected-vs-true difference is the offset (103 vs 119 ms), which changes MDI (0.40 vs 0.35).
- Interpretation: the Vallès false-epicardial call is real model output, not measurement. The beat starts with a small q in lead I (to -0.11 mV over the first ~20 ms) while activation spreads along the fast endocardial layer before epicardial breakthrough at 21 ms. Vallès 2010 derived the q-in-lead-I step from basal-superior and lateral LV pace maps in NICM; this site is mid-level infero-posterior, outside that territory. Whether criteria are scored only inside their derivation regions is a pre-registration decision for Alex.

### 2026-10-03_<HEART>_*: full pipeline on the other two pilot hearts (Alex: "go with the 3 hearts")
- Date/time: 2026-10-03 00:15
- Git commit: f9d274e (uncommitted changes: per-heart edits to 06/08, new 08a_atrial_fit.py and run_heart.sh, 10_measure_ecg.py fix, LABNOTES.md)
- Status: running (6G8DD8S5 first, then 7D98EVAR)
- Purpose: same model, calibration, torso placement, lead fields, full paced beat and ECG scoring as Y5HYEDL4, for 6G8DD8S5 (HF wide QRS) and 7D98EVAR (HF narrow QRS).
- Command: `bash sims/biv_model/run_heart.sh <HEART> 2026-10-03` (steps 01-05, 07 --auto, 08a atrial fit, 08 place / mesh / electrodes, 06 full QRS 140 ms with Vm every 1 ms, 08 lead fields + ECG, 09 plot, 10 criteria); step logs in runs/2026-10-03_<HEART>_pipeline/
- Model: as Y5HYEDL4 (monodomain, Tomek, dt 10 us, frozen measured targets implemented per heart by 07 --auto, i.e. per-heart conductivities in data/biv/<HEART>/calibration.json)
- Exit site: same rule as Y5HYEDL4 (LV endocardium, z ~ 0.5, phi ~ 180 deg from the septum); depth 0 (endo). Anatomical position to be read from torso coordinates.
- Torso: T13, uniform 0.2 S/m; placement by each heart's own atria matched to g001
- Expected wall time ~75-90 min per heart
- Status update 2026-10-03 03:05, 6G8DD8S5: steps 01-09 ok (00:11-01:23, 72 min); step 10 failed on a line-order bug I had just introduced into 10_measure_ecg.py (baseline-window edit); fixed and re-scored at 02:58. A usage limit paused me between ~01:25 and 02:50; the simulations themselves were not affected. 7D98EVAR started 02:58.
  - Model: 375,672 nodes, 1,997,928 tets; apex to valve centroid 89.0 mm; fibres vs cohort median 10.9 deg (body 10.3, OT 21.1); fast layer 0.90 mm thick, overlap with cohort layer 0.76.
  - Calibration (07 --auto): fast gi 5.286 for 2.0 m/s (measured 1.50 / 2.01 / 2.97 m/s for the three targets), sheet-normal gi 0.2938 -> 12.66 ms; within 3 %.
  - Placement: atrial fit rotation 19.9 deg, residual median 2.7 mm (p90 6.6); torso mesh 1,640,909 nodes, 10,333,536 tets, no tag-0 elements; torso edge p50 1.05 mm.
  - Full beat (same site rule): total activation 103.8 ms; fast layer 2.08 m/s; LV free-wall endo -> epi 21.7 ms; first breakthrough 23.2 ms. 12-lead: runs/2026-10-03_6G8DD8S5_ecg/ecg12.png.
  - Criteria (baseline window 40 ms ending 5 ms before onset): detected onset 2 ms, offset 91/92 ms, QRS 89 ms, PdW 23, IDT 49, SRS 44 ms, MDI 0.46; no q in I; inferior start positive; RBBB-like, superior axis. Epi calls: Vallès MDI >= 0.45 (detected only; true-mode MDI 0.41) and Vallès no-inferior-q. Vallès 4-step not epi (reaches step 4, no q in I). True mode: QRS 104 ms, PdW 25, IDT 51, SRS 46, MDI 0.41.
- Re-scoring 2026-10-03 03:00: all beats now scored with the plan's baseline window (40 ms ending 5 ms before the true onset, inside the 60 ms flat pad). Y5HYEDL4 values unchanged from the 2026-10-03 correction.

#### Note 2026-10-03 03:10: site grid script and eikonal check (nothing run)
- sims/biv_model/11_site_grid.py written, not run (Alex approves the grid batch separately): LV 3 levels (z 0.25/0.50/0.75) x 6 rotational positions (phi 0, +-60, +-120, 180; septal vs free wall decided per point), RV free wall 3 x 3, RVOT 2, LV summit 2, aortic-cusp region 2 (LV muscle at the annulus under RCC / LCC), each at 10/50/90 % wall depth = 99 sites per heart, 297 for the pilot. Names from torso-frame directions (AHA-style sector); Bazan region per site (mid level flagged as basal/apical boundary).
- Eikonal: openCARP v20 here has the DREAM module (-dream.solve 0 eikonal, 1 RE+, 2 RE-, 3 DREAM), so eikonal activation is available; not yet timed.
- Status update 2026-10-03 04:00, 7D98EVAR: all steps ok (02:58-03:58). Model 337,505 nodes, 1,755,714 tets; apex to valve centroid 92.8 mm; fibres vs cohort median 10.6 deg (body 9.9, OT 24.7); fast layer 0.90 mm, overlap 0.80. Calibration: fast gi 5.299 for 2.0 m/s (measured 1.51 / 2.01 / 2.97), sheet-normal gi 0.2987 -> 12.64 ms; within 3 %. Atrial fit rotation 18.6 deg, residual median 2.2 mm (p90 6.1). Torso mesh 1,709,957 nodes, 10,791,117 tets, no tag-0 elements. Full beat: total activation 110.3 ms; fast layer 2.08 m/s; LV free-wall endo -> epi 21.9 ms; breakthrough 23.2 ms. ECG: runs/2026-10-03_7D98EVAR_ecg/ecg12.png. Criteria detected: onset 2, offset 83/85 ms, QRS 81 ms, PdW 26, IDT 42, SRS 39, MDI 0.48; no q in I; RBBB-like, superior axis; epi calls Vallès MDI >= 0.45 and no-inferior-q (4-step not epi). True mode: QRS 110 ms, PdW 28, IDT 44, SRS 41, MDI 0.37; epi call no-inferior-q only.
- Pilot summary (3 hearts, same endocardial LV site rule, all depth 0): no interval criterion (Berruezo PdW/IDT/SRS, Daniels MDI) called epi in any heart or mode. Calls that did: Vallès q-in-I and 4-step in Y5HYEDL4 (both modes); Vallès MDI >= 0.45 in 6G8DD8S5 and 7D98EVAR in detected mode only (true-mode MDI 0.41 / 0.37), driven by the early detected offset (detected QRS 81-101 ms vs true 104-119 ms); Vallès no-inferior-q in all three (superior-axis beats, criterion meant for inferior-axis VT).

### 2026-10-03_eik_timing_Y5HYEDL4 / 2026-10-03_reminus_timing_Y5HYEDL4: eikonal and RE- timing tests (one site)
- Date/time: 2026-10-03 04:15
- Git commit: f9d274e (uncommitted changes)
- Status: running
- Purpose: per-site wall time for pure eikonal (+ pseudo-Vm + lead-field ECG) and RE-, to estimate the grid.
- Command: `cd sims/biv_model && python 12_eikonal.py --mode eik --ID 2026-10-03_eik_timing_Y5HYEDL4 --tend 140` and `--mode re- --tend 20` (RE- extrapolated from 20 ms to stay under 10 min)
- Model: eikonal speeds = effective frozen targets (fibre 0.6, sheet 0.4, sheet-normal 0.48, fast layer 2.0 m/s); RE- with Tomek and the heart's calibrated conductivities; same site as 2026-10-02_biv_fullqrs (node 313318, LV endo, depth 0)
- Output folders: runs/2026-10-03_eik_timing_Y5HYEDL4, runs/2026-10-03_reminus_timing_Y5HYEDL4
- Status update 2026-10-03 05:05 (eikonal / RE- timing):
  - runs/2026-10-03_eik_timing_Y5HYEDL4: FAILED / INVALID, kept. First attempt used an electrics physics region (ran the ionic model, ~17 s per ms, stopped at the 10-min limit); second attempt aborted (DREAM/eikonal physics do not support MPI); third ran but with speeds in the wrong unit (openCARP dream.vel_* is mm/s; I gave 0.6 instead of 600), so its activation times are 1000x too long.
  - runs/2026-10-03_eik2_timing_Y5HYEDL4 (+ _ecg): ok. Pure eikonal, Eikonal physics region, 1 process with 6 OpenMP threads, speeds 600/400/480/2000 mm/s: 84 s wall; all nodes activated; total activation 129.1 ms (monodomain 118.6 ms); activation times correlate r = 0.999 with the monodomain map of the same site. Pseudo-Vm from a template AP (monodomain Vm at the node whose LAT is ~60 ms, shifted to each node's activation time): 3 s. Lead-field ECG projection (openCARP experiment 4, saved lead fields): 59 s. The pseudo-Vm file must reuse openCARP's own IGB header (my hand-written headers gave rejected or garbage reads; two failed projections). ECG vs monodomain, same site: per-lead correlation 0.95-0.99, peak amplitude ratio 0.93-1.08. About 2.5 min per site.
  - runs/2026-10-03_reminus_timing_Y5HYEDL4: ok. RE- (dream.solve 2, Tomek), 20 ms in 364 s, ~17 s per simulated ms, i.e. ~40 min per 140 ms beat: no faster than monodomain here.

#### Note 2026-10-03 05:10: LBBB-like variant for 6G8DD8S5 (frozen definition "LV activated without left-sided fast-layer entry")
- Cohort tag 29 (FEC_SV) lines the RV side of the septum in 6G8DD8S5 (100 % of its elements touch the RV endocardium, 0 % the LV); the left septal surface is in tag 25 (FEC_LV).
- sims/biv_model/05b_lbbb_variant.py: every fast-layer element touching the LV endocardium (incl. left septum; 106,921 elements, 28 of them also touching the RV endocardium) gets myocardial conductivities (tag 1); the RV-side layer stays fast (88,812 elements). Mesh: data/biv/6G8DD8S5/bivF_lbbb. Y5HYEDL4 and 7D98EVAR keep the normal layer.
- The 2026-10-03 6G8DD8S5 full beat (2026-10-03_6G8DD8S5_fullqrs) used the NORMAL fast layer; it is not rerun. Lead fields for the variant should be recomputed (heart conductivities change; ~6 min) before its grid runs.

#### Note 2026-10-03 05:40: eikonal vs monodomain check on Y5HYEDL4 (site node 313318)
- Eikonal speeds confirmed in parameters.par: 600 / 400 / 480 / 2000 mm/s = fibre 0.6, sheet 0.4, sheet-normal 0.48 (effective, not the 0.45 tuneCV setting), fast layer 2.0 m/s.
- Where the +10 ms last activation comes from: eikonal minus monodomain LAT is small in the fast-layer region (median +0.7 ms for z 0.1-0.9; fast-layer speed 1.95 vs 2.04 m/s; first breakthrough 20.6 vs 21.1 ms) and grows in the basal 10 % without a fast layer (median +2.7 ms; last activation 129.1 vs 118.6 ms, same RV basal node). Patch test (runs/2026-10-03_patch_myospeed_*): mid-wall stimulus, fast layer neutralised, nodes 3-10 mm away: eikonal LAT = 1.087 x monodomain LAT, i.e. monodomain myocardial conduction is ~9 % faster than 0.6 / 0.4 / 0.48 on this mesh. Cause: the monodomain fibre and sheet conductivities are the wedge (1 mm) values and were never re-checked on the heart mesh (only the fast layer and sheet-normal were). Not an eikonal setting. Not fixed: needs a decision (re-calibrate fibre and sheet on the patch to measured 0.6 / 0.4, as was done for the other two).
- ECG scoring, eikonal vs monodomain, same site (ecg_depth_criteria, plan baseline window): detected mode: onset 2 vs 2 ms, pseudo-delta 30 vs 30, IDT 45 vs 42, shortest RS 42 vs 40, MDI 0.38 vs 0.40, QRS 110 vs 101 ms. True mode: pseudo-delta 32 vs 32, IDT 47 vs 44, shortest RS 44 vs 42, MDI 0.34 vs 0.35, QRS 129 vs 119 ms. Onset intervals within the +-5 ms tolerance (max 3 ms); QRS duration differs by 9-10 ms; all criterion calls identical.

### 2026-10-03_<HEART>_patch_myo_*: fibre / sheet conductivities to measured 0.6 / 0.4 m/s on each heart's patch (Alex chose "Run it all", 08:58 UTC)
- Date/time: 2026-10-03 11:10
- Git commit: f9d274e (uncommitted changes)
- Status: running
- Method (07_patch_tune.py --myo): mid-wall stimulus at the LV free-wall patch centre, fast layer neutralised (given the sheet conductivity isotropically); speed along the local fibre and the local sheet axis (within 20 deg) at the same depth, 3-10 mm away; scan of fibre and sheet gi x 0.7 / 0.85 / 1.0, power fit, confirmation run; then re-check sheet-normal transit (12.6 ms) and fast-layer speed (2.0 m/s) with the new values, one correction each if more than 3 % off. Old values kept in calibration.json 'history'.
- Command: `cd sims/biv_model && HEART=<H> RUN_PREFIX=2026-10-03_<H>_patch python 07_patch_tune.py --myo` for Y5HYEDL4, 6G8DD8S5, 7D98EVAR

#### Note 2026-10-03 11:40: site grid finalised before the batch (selection only, no simulation)
- 11_site_grid.py run for all three hearts: 99 sites each (LV septum 24, LV free wall 30, RV free wall 27, RVOT 6, LV summit 6, aortic-cusp region 6). Fixes after the first test: septal only within +-60 deg of the septal centre (the nearer-RV-than-epi test alone mislabelled some +-120 deg positions); each site records its actual depth; depth_miss flag when more than 0.1 from the target (Y5HYEDL4 3, 6G8DD8S5 2, 7D98EVAR 2: septal RVOT at 50 % has no epicardium; annulus RCC sites at 10 %). Bazan regions assigned per site.

### batch_2026-10-03: eikonal grid, monodomain agreement check, no-fast-layer control (Alex: "Run it all", then "go")
- Date/time: launched after the fibre/sheet calibration (see 2026-10-03_<HEART>_patch_myo_*)
- Git commit: f9d274e (uncommitted changes: sims/biv_model/ 05b, 07 --myo, 08 variants, 11, 12, batch driver; LABNOTES.md)
- Driver: `setsid nohup python sims/biv_model/batch_2026-10-03.py` (detached, resumable; pause by creating runs/batch_2026-10-03/PAUSE). Progress: runs/batch_2026-10-03/{driver.log, progress.jsonl, status.json}. Run folders: runs/2026-10-03b_*.
- Stages: S0 site grids / mesh variants; S1 lead fields with the re-calibrated conductivities (normal x3, LBBB-like 6G8DD8S5, no-fast-layer x3); S2 eikonal grid 297 sites (6G8DD8S5 on the LBBB-like mesh); S3 monodomain agreement 27 sites (per heart: original LV mid-endocardial site + LV free wall phi 180 z 0.5 at 50/90 %, septum phi 0 z 0.5 and RV free wall q50 z 0.5 at 10/50/90 %) plus eikonal for each original site; S4 no-fast-layer eikonal 297 sites.
- Model: eikonal = pure eikonal (effective 0.6 / 0.4 / 0.48 / 2.0 m/s), pseudo-Vm from each heart's own monodomain template AP; monodomain = Tomek, dt 10 us, heart-mesh calibrated conductivities (calibration.json), tend 160 ms (220 ms LBBB-like). Torso T13, uniform 0.2 S/m. Scoring: ecg_depth_criteria v0.1.0, both onset modes, site's Bazan region.
- Large Vm files deleted after each ECG (activation times kept), to protect disk space on C:.
- Status update 2026-10-03 11:50 (fibre / sheet calibration): ok. First --myo pass (joint scan) left fibre at 0.56-0.59 and sheet at 0.42-0.43 m/s (a first background launch at 11:10 failed to start: wrong working folder); one separate correction step (07 --myo-refine) brought all three within 3 %. Final heart-mesh conductivities (gi / ge, S/m) and measured values:
  | heart | fibre (0.6 m/s) | sheet (0.4 m/s) | sheet-normal (12.6 ms) | fast layer (2.0 m/s) |
  |---|---|---|---|---|
  | Y5HYEDL4 | 0.7105 / 2.5522 (0.598) | 0.2415 / 0.8675 (0.409) | 0.2962 / 1.0642 (12.49 ms) | 5.1670 / 18.5601 (2.009) |
  | 6G8DD8S5 | 0.6724 / 2.4154 (0.592) | 0.2789 / 1.0016 (0.408) | 0.2938 / 1.0555 (12.51 ms) | 5.2862 / 18.9883 (2.024) |
  | 7D98EVAR | 0.7300 / 2.6224 (0.596) | 0.2577 / 0.9255 (0.407) | 0.2987 / 1.0732 (12.41 ms) | 5.2989 / 19.0340 (2.016) |
  Wedge values were fibre 0.5606 / 2.0138, sheet 0.3368 / 1.2096: on the heart mesh the fibre conducted too slowly (0.55 m/s) and the sheet too fast (0.45 m/s) with them. Speeds are point-stimulus speeds 3-10 mm from the site (wavefront curvature included), the regime that matters for exit sites and for eikonal agreement. The full beats run on 2-3 Oct used the wedge fibre/sheet values.
- Fast ECG (13_fast_ecg.py): validated against openCARP lead-field ECGs on Y5HYEDL4: harmonic-mean conductivity, factor -1; max error 0.0002 mV (monodomain beat, peak 2.47 mV) and 0.000006 mV (eikonal beat).
- Batch change 2026-10-03 11:44 (Alex can give the PC only ~2 h): driver relaunched with BATCH_STAGES=S0,S1,S2 and no new site after 11:25 UTC; 3 eikonal sites at a time (2 threads each, ~1.6 GB peak per run); S3 (27-site monodomain check) and S4 (no-fast-layer control) deferred to the new PC (same driver, resume logic kept). A first launch at 11:43 failed before starting (log folder missing).
- Status update 2026-10-03 13:27 (batch_2026-10-03): stopped at the deadline as planned (driver state "paused" 11:26 UTC; no openCARP / Python processes of ours left). 115 items ok, 0 failed: S0 LBBB-like mesh variant (6G8DD8S5); S1 lead fields + ECG weights (Y5HYEDL4 normal, 6G8DD8S5 LBBB-like, 7D98EVAR normal; 4.6-6.5 min each); S2 eikonal grid: Y5HYEDL4 99/99 sites, 6G8DD8S5 9/99 (LV septum phi 0 at the three levels; LBBB-like beats take longer), 7D98EVAR 0/99. Eikonal sites ran 3 at a time, ~107-133 s each (~40 s per site overall).
  - NOT done (deferred to the new PC, same driver; finished items are skipped on relaunch): S2 for 90 6G8DD8S5 and 99 7D98EVAR sites; S3 27-site monodomain check (+ 3 eikonal original sites); S4 no-fast-layer control (297 sites; its lead fields and weights also still to build). Relaunch: `BATCH_STAGES=S0,S1,S2,S3,S4 setsid nohup python sims/biv_model/batch_2026-10-03.py`.
  - Results: analysis/pilot_grid_sites.csv (one row per finished site), analysis/pilot_grid_calls_by_depth.csv (script analysis/pilot_grid_summary.py).
  - Y5HYEDL4 (normal conduction, 33 sites per depth), share called epicardial, detected / true onset mode: depth 10 %: PdW>=34 8/33 / 8/33, IDT>=85 2/32 / 9/33, SRS>=121 0 / 0, Daniels MDI>=0.55 3 / 0, Vallès MDI>=0.45 11 / 7, q in I 14 / 14, Vallès 4-step 14 / 13. Depth 50 %: PdW 6 / 10, IDT 7/28 / 14/33, SRS 0 / 0, Daniels 2 / 1, Vallès MDI 9 / 6, q in I 7 / 7, 4-step 9 / 7. Depth 90 %: PdW 12 / 14, IDT 6/26 / 17/33, SRS 0 / 0, Daniels 6 / 2, Vallès MDI 24 / 14, q in I 11 / 11, 4-step 14 / 13. Medians (true mode) 10 -> 50 -> 90 %: PdW 26 -> 26 -> 27 ms, IDT 49 -> 64 -> 97 ms, shortest RS 44 -> 52 -> 60 ms, MDI 0.37 -> 0.39 -> 0.44, QRS 118 -> 120 -> 122 ms. Detected onset median 2 ms (max 9). IDT in V2 is often unmeasurable in detected mode (no R in V2 at 1-7 of 33 sites).
  - 6G8DD8S5 LBBB-like (9 septal sites): QRS 169-190 ms; no interval criterion epi except IDT in true mode (IDT 178-187 ms: the largest R in V2 comes very late in these wide beats; detected-mode IDT 19-30 ms) - to check before interpreting.
