# PC addendum 3 (27-site test), from the lock thread, 3 Nov 2026 (sent to the coordinator at about 15:05 UTC)

Please relay this to the PC as written.

0. The record is republished: notes/A/2026-10-19-v52-lock/relock4-build-answers-2026-10-20.md, 636,336 B, sha256 1ff9895e70f7ad6b5b36becb71cbd050647d6cf2b7da6f44dba29550840dff84 (the 13:36 text, 606,149 B, aa07e338..., is kept as relock4-build-answers-2026-10-20-1336.md). It holds D42-D46 adopted and D47 and D48 proposed. In addendum 2, "the record governs over all three" means this revision, not the 13:36 text the 13:39 note cites; where the 13:36 text differs from the addenda (the hold on reading, the ECG of D42's graph beats, D45's Gaussian fit), it governs nothing.

1. Corrections to addendum 2, item 1 (the foot-current fit):
   - (i) tau_F: form dVm/dt by central differences of the sampled Vm. The line through the origin (dVm/dt against Vm - V_rest) is the record's reading of Neic's Appendix A (the foot's offset taken at rest, from its eq. 40-44); Fig. 10's caption gives only the slope. Beside it, as a check that changes nothing, also log the slope and Vm-axis intercept of the least-squares line with a free intercept over the same window.
   - Last bullet, replaced: enter nothing until D48's answer is relayed. If it is "Fit the time constant only", enter tau_F from (i) with A_F 0.91 mV. If it is "Fit both", send the lock thread (iii) and (iv) and enter nothing, and start no RE+ heart beat, until Alex's answer on the onset is relayed. Either way the values are entered per imp_region, fixed before the first of the 27 RE+ beats and never changed after; D44 (b)'s flat-block run uses them and is report only.

2. Correction to addendum 2, item 4 (HF RE+ flagged sleeve nodes):
   - While the hold on reading lasts, the check prints counts only, after each HF RE+ beat: the flagged nodes; how many were driven again; and whether any flagged node's Vm exceeded the largest Vm of that beat's excitable nodes (the stop). Their largest Vm and eikonal times are reported beside T2 only after the hold ends. Add these counts to the per-chunk counts.
   - "Driven again" is counted in the run, at every solver step: a node counts when, within TA + 5 ms, openCARP applies the foot to it (Idiff non-zero) at a step after one at which it withheld it because Vm was at or above V_th. openCARP tests Vm < V_th on the Vm after each step's ionic update and adds the foot in that same step, before the diffusion solve, and it writes Vm and Idiff only every 1 ms here, so neither the dip nor the kick need show in the output. If the build cannot keep the count, say so and report it as not measured, never as 0.
   - If the stop fires: no new beat in that lane, raw file kept, reported as a count before the next chunk.

Nothing else changes. D47 and D48 are still with Alex; I'll relay his answers.
