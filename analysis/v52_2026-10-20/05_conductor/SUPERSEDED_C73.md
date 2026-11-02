# Superseded by C73 (lock thread, 2 Nov 2026)

These reports were built on conductor52.py's great-vessel lumen rules 1 and 2 (861a760), which cap the aortic and
pulmonary blood inside the stub, not on the stub's own cut-end rim as R3.1 reads under C73. They are kept as they are
and are used for no v5.2 result. The C73 rebuild writes the same reports with a `_c73` suffix.

| File | What it is |
|---|---|
| conductor52_Y5HYEDL4.json | control heart's step-5 build (rule 1 caps) |
| conductor52_6G8DD8S5.json | 6G8DD8S5's step-5 build (rule 2 caps) |
| leadfield52_Y5HYEDL4.json, leadfield52_Y5HYEDL4_jacobi.json, leadfield52_Y5HYEDL4_jacobi_tol1e-10.json | control heart's lead-field runs on that mesh |
| weights52_Y5HYEDL4.json | its C9 and sigma_i weights (data/biv/Y5HYEDL4/v52/ecgW_v52.npz) |
| clearance_d40_Y5HYEDL4.json, clearance_d40_6G8DD8S5.json | D40 (1) 12 mm checks read from those meshes (heart nodes unchanged by C73) |
| lumens52_Y5HYEDL4.json, lumens52_6G8DD8S5.json, lumens52_7D98EVAR.json | read-only checks of rules 1 and 2 |
| c69_recount_Y5HYEDL4.json | C69 recount on the rule-1 mesh |
| vessel_ends_answer_2026-11-02.md | the PC's read-only answer on rules 1 and 2 (still a correct description of them) |

Run folders labelled the same way (SUPERSEDED_C73.txt): data/biv/Y5HYEDL4/v52/torso52/, data/biv/6G8DD8S5/v52/torso52/,
runs/v52_2026-10-20/05_conductor/Y5HYEDL4/leadfield52*/, runs/v52_2026-10-20/05_conductor/6G8DD8S5/leadfield52_jacobi/.
