# VT exit depth — in silico ECG criteria study

## What this project is

An in silico study asking: **how well do published surface-ECG criteria separate
endocardial, intramural and epicardial VT exit sites?** We pace or initiate
activation at controlled transmural depths in a ventricular model, compute 12-lead
ECGs with the lead-field method, and measure each criterion automatically.

Criteria under study (thresholds are the published "epicardial" cut-offs; they are
hypotheses to test, not ground truth):

| Criterion | Definition (measured from QRS onset) | Epicardial if | Source |
|---|---|---|---|
| Pseudo-delta wave | QRS onset → earliest fast deflection in any precordial lead | ≥ 34 ms | Berruezo 2004 |
| Intrinsicoid deflection time (IDT) | QRS onset → peak of R in V2 | ≥ 85 ms | Berruezo 2004 |
| Shortest RS | QRS onset → nadir of first S, shortest across precordial leads | ≥ 121 ms | Berruezo 2004 |
| Maximum deflection index (MDI) | (QRS onset → earliest max deflection in precordial leads) ÷ QRS duration | ≥ 0.55 | Daniels 2006 |
| q wave in lead I | Initial negative deflection in lead I | present | Vallès 2010 (basal/apical superior LV) |

Exit depth categories: **endocardial**, **intramural**, **epicardial**. Define depth
with a continuous transmural coordinate (0 = endo, 1 = epi, e.g. from a Laplace solve;
see example `02_EP_tissue/13_laplace`) and record the numeric value for every run,
not just the category.

## The user

The user is an EP fellow, not a programmer. They know the clinical side well (ECG
criteria, VT mapping, anatomy) but not Python, Linux or numerical methods.

- Explain every step in plain language **before** doing it: what it does, why, and
  roughly how long it will take. Skip programming jargon, or explain it in one clause
  when you have to use it.
- Use clinical analogies where they help (e.g. lead field ≈ "how much each bit of
  myocardium 'counts' toward a given lead").
- After a run, summarise the result in clinical terms first (what the ECG looks like,
  what the criteria say), then technical details.
- Ask before long runs (> ~10 min), before deleting anything, and before changing
  model assumptions (conduction velocities, anisotropy, fibre rules, geometry).
- Don't silently "fix" a scientific choice. If an assumption looks questionable, say
  so and let the user decide.

## Lab notebook: LABNOTES.md (mandatory)

**Every simulation run gets an entry in `LABNOTES.md`**, including failed, aborted and
test runs. Write the entry as soon as the run starts (status "running"), then update
it when the run finishes. Use the template at the top of LABNOTES.md. Each entry
records:

- Run ID (matches the output folder name), date/time, git commit (`git rev-parse --short HEAD`, note "uncommitted changes" if `git status` isn't clean)
- Purpose in one plain-language sentence
- Exact command line
- Model: eikonal / reaction-eikonal (RE+ or RE−) / other; ionic model
- Geometry/mesh, resolution, exit location and transmural depth (numeric + category)
- Conduction velocities (longitudinal/transverse), fibre setup, lead-field source (computed fresh or reused from which run)
- Output folder, wall-clock runtime, outcome (ok / failed + error message)
- Criteria values if computed, plus observations and next steps

Never delete or rewrite old entries; add corrections as new dated notes.
Never paste the output of `openCARP -buildinfo` wholesale: its "GIT repo" line
contains an access token. Record only the tag and hash.

## Environment

Before running **anything** Python or openCARP related, in the same shell command:

```bash
source ~/venv_carputils/bin/activate
export PATH=/usr/local/lib/opencarp/lib/petsc/bin:$PATH   # makes mpiexec available
```

(Each Bash call starts a fresh shell, so prefix these to every command that needs
them.)

- **openCARP** v20 at `/usr/local/bin/openCARP` (buildinfo hash `ffce195`). Other tools (`igbextract`, meshtool) are in `/usr/local/bin`.
- **carputils** in `~/venv_carputils` (Python 3.14). Settings: `~/.config/carputils/settings.yaml` (flavor petsc, platform desktop).
- **MPI**: `mpiexec` is bundled with openCARP's PETSc in `/usr/local/lib/opencarp/lib/petsc/bin` and isn't on the default PATH. Without the export above, `--np N` runs will fail.
- **CPUs**: 8 cores. Use `--np 4` to `--np 6` for tissue runs so the machine stays usable.
- **Meshalyzer**: `meshalyzer <mesh_basename> <data.igb or .dat>`. It's a GUI (WSLg). Claude can't see it, so give the user the exact command to run and describe what they should look for.
- `MESH_DIR` in settings.yaml points to `/usr/local/meshes`, which doesn't exist. Keep meshes inside this repo under `meshes/`.
- This is WSL2: never run `find /` or other whole-disk searches (they crawl the Windows drives and hang).

## Reference examples (~/opencarp-examples/examples)

Copy and adapt these; don't edit them in place.

- `03_Eikonal/01_Eikonal`: pure eikonal (`-dream.solve 0`). Gives activation times only, no transmembrane voltage (Vm).
- `03_Eikonal/02_Reaction_eikonal`: reaction-eikonal (`-dream.solve 1` = RE+ with diffusion current, `2` = RE−). Gives Vm, which the ECG needs. CVs are set with `-gregion[i].dream.vel_l / vel_t`.
- `02_EP_tissue/09_leadfield`: lead-field ECG (`--post_processing_opts 64`, `--lf_config 12`, `--ecg_timedt`). Writes `LF_*.igb` (sensitivity maps) and `ECG_*.dat`. Supports reusing lead fields (`--lf_dir`) and reusing Vm (`--lf_vmfile`).
- `02_EP_tissue/13_laplace`: Laplace solves, useful for the transmural coordinate.
- `02_EP_tissue/24_electrode_definition`, `04_tagging`: defining stimulus sites and regions.

Run an example to see its options: `python run.py --help`.

## Key methodological points

- **Pure eikonal can't give an ECG by itself.** It only gives activation times. Use
  reaction-eikonal for Vm, or explicitly build a pseudo-Vm from activation times plus a
  template action potential. State which one each run used.
- **Reuse lead fields.** They depend only on geometry, conductivities and electrode
  positions, not on the exit site. Compute them once per geometry, then reuse them via
  `--lf_dir` for every exit site. Recompute if the torso, conductivities or electrodes change.
- **QRS onset** drives every interval criterion. Measure it with one fixed,
  documented rule applied to all runs (e.g. first time the global ECG signal crosses a
  threshold). Also record the true earliest activation time from the simulation;
  comparing the two is itself informative.
- **Fibres and transmural anisotropy** strongly affect endo-versus-epi differences.
  Keep fibre rules fixed across the exit-depth comparison and log them.
- Keep the mesh, CVs, ionic model and electrode set identical across exit sites, so the
  only thing that changes is the exit location/depth.
- Check resolution sensitivity on at least one exit site before the full sweep
  (see `02_EP_tissue/03G_study_resolution`).

## Project layout (create as needed)

```
meshes/        geometry and fibre files
leadfields/    precomputed LF_*.igb per geometry (reused across runs)
sims/          scripts that set up and run simulations (carputils run.py style)
runs/          simulation outputs, one folder per run ID (not committed: large)
analysis/      ECG criteria measurement scripts and results tables (CSV)
figures/
LABNOTES.md    run log (see above)
```

Commit scripts, analysis code, results tables and LABNOTES.md. Don't commit `runs/`
or large `.igb` files; add them to `.gitignore`.
