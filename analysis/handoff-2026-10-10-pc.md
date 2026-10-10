---
saved-at: 2026-10-10T10:13:57Z
saved-at-sha: afbbb7f
saved-at-branch: master
saved-from-cwd: /home/alex/vt-exit-depth
---

- Pick up: nothing running or queued. Network v3 grids done on all three hearts (jobs 8-10, 432 sites) and rescored with the cb conductor (10 Oct, other thread); three-heart analysis done: analysis/network_three_hearts_2026-10-10/results.md (also in the project files). Wait for Alex's next decision.
- Read first: LABNOTES.md entries of 9-10 Oct (network deviation, v4 rejected, LBBB cut, cb conductor deviation, jobs 9-10, three-heart note); memories conduction-model-network-v3, lead-field-conductor-cb, pc-memory-leadfield-oom.
- Use the *_cb CSVs / *_ecg_cb folders for network-arm results; new network beats need 15_conductor.py rescore.
- Open for Alex: HF hearts' paced summit/cusp QRS narrower than control (134 / 144 vs 162.5 ms; same tissue speeds, no HF remodelling); Daniels MDI order fails in all hearts (RVOT highest); IDT and shortest RS lose depth signal with cb; pseudo-delta >= 34 ms fires at ~70 % of endocardial sites; by-eye IDT check (analysis/idt_v2_2026-10-07/) still pending; data/biv/Y5HYEDL4/torso_rot-20_INCOMPLETE (2.1 GB) awaits OK to delete.
- Constraints: runs > 10 min need Alex's OK; full-torso lead fields only alone with the light AMG options + watchdog; network beats at most 2 at a time; never pkill -f with a pattern matching your own command; commit or push only when asked (nothing committed since afbbb7f); keep Claude usage minimal.
