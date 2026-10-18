# 27-site monodomain check on the frozen v5.1 model: plan and time estimate (nothing run yet)

Written PC clock 2026-10-18 22:55 CEST. Alex, 20:45:11 UTC: "Yes to all", which includes planning the check. It runs on the
frozen model before the OSF registration (Alex, 17 Oct 2026).

## Locked rule

From the Research Proposal, Analysis plan, locked by Alex on 15 Oct 2026.
- **Sites:** 27, nine per heart.
- **Measures:** pseudo-delta, IDT, shortest RS, and time to the largest precordial deflection.
- **Pass:** at least 90 % of the 108 site-measure pairs within 5 ms of the eikonal value (Berruezo's reading threshold),
  i.e. at least 98 pairs. The maximum difference is reported.
- **Not gated:** last activation, reported only (it was used to calibrate the eikonal).
- **Network:** network beats replay the eikonal junction timings as stimuli. This one-way coupling was accepted on 12 Oct
  2026, so the test checks the tissue solution and the forward ECG, not the network.
- **If it fails:** no rerun of the Aim 2 grid in monodomain. A subsample, one site per region per heart, gives each onset
  measure's eikonal-minus-monodomain bias, and onset results are reported with that bias band.

## Sites (as batch_2026-10-03 agreement_sites())

Per heart:
1. The original LV mid-endocardial site of the template beat. Node 313318 / 19052 / 277582.
2. LV free wall phi180 z0.5 at 50 and 90 %.
3. Septum phi0 z0.5 at 10, 50 and 90 %.
4. RV free wall q50 z0.5 at 10, 50 and 90 %.

## Two beats per site

- **"Eikonal":** the v5.1 graph beat (heart51: nodal 2-ring solver, v5.1 network, pseudo-Vm template). These already exist
  in runs/.../06_pilot_rerun/maps; the 3 original sites take one graph beat each.
- **Monodomain:**
  - Tomek, dt 10 us, LAT -10 mV, Vm every 1 ms, v5.1 fibres, heart mesh;
  - stimulus 400 uA/cm3 x 1 ms on the nodes within 1.5 mm of the site;
  - junction stimuli at the graph beat's network exit times (+4 ms), each widened to 1.0 mm as on 12 Oct;
  - tend = the graph beat's total activation + 30 ms.
- **ECG:** both through the same v5.1 lead fields (sigma_i weights).
- **Scoring:** ecg_depth_criteria 0.4.0, pace-map convention (stimulus onset, clean ECG), true mode beside.

## Needed first

The v5.1 speeds changed (sheet 0.36, HF 0.26 / 0.336 m/s), so the monodomain conductivities must be re-tuned. 07_patch_tune
did this on 3 Oct, on each heart's LV free-wall patch: fibre 0.60, sheet 0.36 (HF 0.26), normal 0.48 (HF 0.336) m/s, within
3 %. Without this the two models would differ by design, not by method.

Risk: a cross-fibre speed of 0.26 m/s on the ~1 mm heart mesh may be hard to reach or may block in monodomain. The
calibration shows this before any beat.

## Time and resources

| Part | PC time | Notes |
|---|---|---|
| Conductivity calibration, 3 hearts | about 1 h | 3 Oct took about 40 min for all three |
| 10 ms timing test | about 5 min | measures s per simulated ms with the v5.1 settings |
| 27 monodomain beats | about 21-27 h | 4,780 simulated ms in all; 16-20 s per simulated ms (12 Oct, same mesh); about 45-60 min per beat |
| Analysis | minutes | |

- **Memory:** about 4.8 GB for openCARP. Beats run one at a time with 4 processes, under the memory guard (stop if less
  than 900 MB is free).
- **The PC:** it must stay on and should not run anything heavy meanwhile.
- **Suggested schedule:** one heart per night, about 7-9 h each, three nights in all. Each night's runs are resumable.

## Decision for Alex

Go for the calibration and the timing test now (about 1 h)? Then I report the measured speed, and the first heart runs
overnight on your OK.
