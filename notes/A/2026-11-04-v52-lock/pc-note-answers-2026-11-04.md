# Alex's answers to D49 and D50 (4 Nov 2026), for the PC thread "Speed up RE+ beats and fit foot current"

From the lock thread, about 11:52 UTC, via the coordinator. Follows pc-note-2026-11-04.md (sha256 cf6e22b2...1247) and answers the PC's reply logged at 12:46 PC (commit 8e31a4e).

## D49, adopted 11:47:40 UTC: "Whole channel"
"ICaL" in D44 (d2) is ToR-ORd's whole L-type channel: the factor on PCa, so ICaL, ICaNa and ICaK (and their phosphorylated parts) are 0 at the flagged nodes. model_fexc_O2_ftz stands as built and checked. **The HF hearts' 36 ionic beats are released from this hold** (their other conditions are logged, as your report says).

## D50, adopted 11:47:56 UTC: "Cap at 1000 with a check"
- dream.fim.max_iter = 1000 for every RE+ beat that starts from now on (the control heart's 9 included, since their chunk has not started), and for the flat block's rerun.
- When a beat's t = 0 solve ends at the cap with a non-empty active list (eik_stats.dat), rerun that solve alone, with the same inputs and the same thread count, at max_iter 1001, 1002 and 1003. If no node's activation time differs from the beat's own by more than 0.01 ms (one dt), the beat stands; report its list size at exit and the largest difference, as counts. Otherwise it is a numerical failure under D42 (1): no new beat in that lane, raw file kept, reported before the next chunk.
- Keep logging each RE+ beat's t = 0 iteration count and list size at exit (summary.json, LABNOTES).
- D44 (b), report only: rerun the control sheet axis at max_iter 1000 with the same check, and report its row (CV from Vm, Vm act - eikonal min / median / max, upstroke) with the list size at exit and the largest difference.

## Your 12:46 reply
Logged in C75: the factor's reach in the generated source; the HF sheet run's 8 negative nodes, away from the stimulus (report only); -output_level 2 (an output change, vm.igb byte-identical); check 6's class split (every flagged node a stimulus or junction-exit node). Check 6 stays as it is: report the counts by class, nothing removed, the beat kept.

## Hold on reading
It ends when you log D49's and D50's answers (D42: all later cards answered, relayed and logged; the fit, margins and D44 (d)'s checks are logged). Rule 0.3 binds from the first opened result. The record republish with D49, D50 and C75 follows; its hash comes next.
