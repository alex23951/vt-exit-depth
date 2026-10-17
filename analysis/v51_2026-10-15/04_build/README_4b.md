# Step 4.3 (graph solver fix, F01): stopped at the factor fit (S5) and acceptance A

PC clock 2026-10-17 03:44-04:03 CEST (UTC 01:44-02:03). Alex "Go for 4.3 up to the openCARP runs" (01:39:48 UTC).
No beat with the network has been run; no openCARP reference run.

## Done

- F01 script copy (f01_copy_v5.py; only the output path changed; original sha256 in f01_copy_v5.orig_sha256) rerun on
  the v5 solver: output identical to analysis/audit_2026-10-13/a03_speeds_activation.json. Realised speeds:
  0.564 / 0.489 / 0.485 m/s (control), 0.501 / 0.364 / 0.350 and 0.503 / 0.366 / 0.351 (HF).
- openCARP v20 (ffce195) eikonal: separate `gregion[].dream.vel_l` (fibre), `vel_t` (transverse) and `vel_n` (normal),
  checked with +Help.
- S1-S3 solver, graph51.py (stencil v51-2ring-1):
  - E1 tet edges plus E2 graph-distance-2 pairs. The 3.5 mm limit never binds (two edges ≤ 1.75 mm).
  - Surface-surface E2 pairs are kept only if their midpoint lies in a tet.
  - Nodal volume-weighted metric; E2 time = minimum over the middle nodes.
  - Speeds and factors applied at load; caches keyed by mesh, stencil and fibre sha256.

| | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR |
|---|---|---|---|
| E1 / E2 edges | 2.42 M / 8.43 M | 2.46 M / 8.76 M | 2.18 M / 7.64 M |
| edges per node | 57.8 | 59.7 | 58.2 |
| surface pairs tested / rejected (midpoint outside) | 669 k / 322 k | 553 k / 260 k | 578 k / 278 k |
| interior validation (midpoints found inside) | 99.975 % | 99.995 % | 99.990 % |
| build time, peak RSS | 95 s, 1.9 GB | 121 s, 2.0 GB | 96 s, 1.8 GB |
| one tissue-only beat | 0.7 s | 0.7 s | 0.3 s |

The subset run came first: 10 % of rows, 13 s, 0.6 GB.

## S5 factor fit (as specified: F01 measure, LV free wall 50 % sites, single-node stimulus, tissue only)

- **Y5HYEDL4 converged** in 4 iterations: factors 1.101 / 0.946 / 1.031. Measured 0.5988 / 0.3607 / 0.4799 m/s (targets 0.60 / 0.36 / 0.48).
- **6G8DD8S5 did not converge** in 10 iterations. The fibre ratio stalled at 0.97-0.975 while f_fibre rose to 1.54 and f_sheet fell to 0.78.
- **7D98EVAR diverged** after iteration 4. The fibre ratio peaked at 0.954, then fell to 0.879; f_fibre reached 1.95.
- These factors are not adopted: saved as solver51_fit_attempt1_factors.json, and params/v51_graph_factors.json does not
  exist, so the solver stops.

## Acceptance A (synthetic slab 36 × 36 × 20 mm, jittered grid Delaunay, edges mean 1.03 / max 1.75 mm, 44,376 nodes, 278,666 tets; solver51_slab.json)

Principal speed ratios (graph / target, fibre / sheet / normal):

| Speeds | Factors 1 (stencil alone) | Fitted factors |
|---|---|---|
| control | 0.967 / 0.993 / 0.971 (rays worst 4.2 %) | 1.057 / 0.941 / 1.001 (rays 6.0 %) |
| HF, 6G8DD8S5 factors | 0.940 / 0.995 / 0.983 (rays 6.9 %) | 1.302 / 0.780 / 0.968 (rays 21.9 %) |
| HF, 7D98EVAR factors | same as above | 1.456 / 0.638 / 0.967 (rays 36.0 %) |

The gate is ±1.5 % for principal speeds and ±3 % for rays, so A fails in every heart, with or without the fit. With the
fit the HF hearts are much worse. Rotating fibres, transmural arrival at 10 mm: 0.992 (control, factors 1) and 0.963
(control, fitted), against a ±2 % gate.

## Why: the F01 measure is biased on graph fields at high anisotropy (measure_bias_check.py / .json)

The same a03 local-CV measure, on the slab with uniform fibres:

| Speeds | Exact analytic front | Graph field, factors 1 | Graph's true principal speed |
|---|---|---|---|
| control (0.60 / 0.36 / 0.48) | 0.596 / 0.369 / 0.482 | 0.563 / 0.365 / 0.466 | 0.580 / 0.358 / 0.466 |
| HF (0.60 / 0.26 / 0.336) | 0.573 / 0.267 / 0.341 | **0.307** (40 elements) / 0.265 / 0.330 | 0.564 / 0.259 / 0.330 |

At 2.3 : 1 anisotropy the graph front is faceted. Few elements have a gradient within 18° of the fibre axis, and those
read about half the true fibre speed. The fit corrects the measure, not the solver. At v5's anisotropy (≤ 1.7 : 1) the
measure is close on exact fronts and biased by about 3 % on graph fields.

So the F01 numbers for v5 itself stay usable as reported, but the measure cannot fit v5.1's heart-failure speeds.

Not run because of this: acceptance B (held-out regions; it uses the same measure), S13 (refit at v5 speeds), and
acceptance C (openCARP; needs Alex's OK anyway).
