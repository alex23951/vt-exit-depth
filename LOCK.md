# Model v5.2: fixes, values, arms, gate rules and predictions

**LOCKED (20 Oct 2026 07:30 UTC); RE-ISSUED (20 Oct 2026 13:51 UTC) with the deviations of section 19 (D1-D10 and G, 20 Oct 2026); RE-ISSUED AGAIN (20 Oct 2026 19:28 UTC) after step 0, with the deviations D11-D17 of 19.15 (20 Oct 2026).** At the 07:30 lock every card was answered: list "Adopt all" (20 Oct 05:15:17 UTC), cusp muscle "Both" (05:18:46; called **the cusp-muscle card** below), heart pose "CT pose" (05:19:07; **the pose card**), retrograde junction delay "2 ms (v5.1)" (07:22:39), gate 5 "Matched bands" (07:23:01). After the lock, and before any v5.2 beat, three more cards were put to Alex and answered: **post-lock card 1**, the upper third of the left septum: "Junction-free", 20 Oct 2026 11:22:09 UTC; **post-lock card 2**, changes 2-10 of the post-lock review: "Adopt all", 20 Oct 2026 11:23:21 UTC; **post-lock card 3**, the calibration-check rule: "Targeted", 20 Oct 2026 11:23:49 UTC. Four parts of the deviations were not shown on post-lock card 2 and carry their own **follow-up answers**: the D4 placement of the sheet envelope about the His line ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC), D5 (a) the crescent reference ring and max rule ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC), D5 (c) the cusp-site depth ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC) and D9b, arm A36 ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC). The text is drafted on the recommended option of each post-lock card ("Junction-free", "Adopt all", "Targeted") and on "adopt" for each follow-up item; where an answer differs, the "If declined" text of that deviation in section 19 is applied before the commit (0.2). **After step 0**, which the PC ran read-only on the 13:51 file (report README-20261020T170855-4447.md, 20 Oct 2026 17:08 UTC), Alex chose "Lock thread" in the PC thread ("lock", 20 Oct 2026 17:11:07 UTC), and five **step-0 cards** were answered: **step-0 card 1**, the sheet's outflows: "Keep tails", 20 Oct 2026 17:32:26 UTC; **step-0 card 2**, the valve-plane ring: "Mid-plane", 20 Oct 2026 17:33:39 UTC; **step-0 card 3**, the infundibulum cut: "Scale to span", 20 Oct 2026 17:32:47 UTC; **step-0 card 4**, D1 after the step-0 counts: "Keep", 20 Oct 2026 17:33:10 UTC; **step-0 card 5**, the aortic frame, the right bundle and the torso list: "Adopt all", 20 Oct 2026 17:36:27 UTC. Each answer took the option 19.15 is drafted on, and each is applied as one or more of deviations D11-D17 (19.15). From here no value, arm, gate rule or prediction changes without Alex's word and a dated deviation entry, and none after a v5.2 result is seen.

Lock time: **20 Oct 2026 07:30 UTC**. Re-issue time: **20 Oct 2026 13:51 UTC** (re-issue, 20 Oct 2026). Second re-issue time: **20 Oct 2026 19:28 UTC** (re-issue after step 0; deviations D11-D17, 20 Oct 2026). The PC commits **this file, as re-issued again**, unchanged as its step 1 and records its sha256 in LABNOTES and PROGRESS.md before any beat. The 07:30 file (kept in the cloud as LOCK-2026-10-20-0730.md) and the 13:51 file (kept in the cloud as LOCK-2026-10-20-1351.md) are superseded and are not committed as the v5.2 lock. Step 0 is not repeated on this file: it ran on the 13:51 file, and its outputs stand (0.2, 15.2). Step 1 refuses the file while any placeholder (a card or follow-up answer, or a re-issue time) remains: stop and report (0.2).

## 0. Decision log, status and the change rule

### 0.1 Decision log

| When (UTC) | Who | What |
|---|---|---|
| 18 Oct 2026 20:43 | Alex | **v5.1 frozen** (MEMORY.md); the 12-beat bias run on v5.1 not run (skip logged 19 Oct) |
| 18 Oct, chat | Alex | ECG source term sigma_i; monodomain re-tuned on a **flat block with straight fibres**; "Drop any caps or limits" |
| 19 Oct 08:45 | PC | C1 won the QRS-end calibration against 40 real PVCs |
| 19 Oct 16:23 | Alex | Hidden late QRS: the surface C1 value decides, the true end is reported beside it, **gate 1 stays failed** |
| 19 Oct 17:42 | PC | **v5.1 monodomain check FAILED**: 72 of 108 pairs within 5 ms against at least 98 needed, maximum 38 ms (so v5.1 is 2 pass / 7 fail) |
| 19 Oct 17:58:45 | Alex | Decision-8 run on v5.1 (Clerc conductivities), reported 18:59 |
| 19 Oct 18:04-18:05, project chat | Alex | **"Build v5.2"**; "I want to build the best most accurate realistic model before registering" |
| 19 Oct 18:27:09, card | Alex | "Fixes 1 to 5" (the gate rules themselves were approved 12 Oct 18:27:09) |
| 19 Oct 18:37, chat | Alex | "dont worry about pc costs i got time" (PC time is not a constraint) |
| 19 Oct 18:42, chat | Alex | Deep literature dive asked for: RVOT and LVOT anatomy, a realistic Purkinje network, any other change |
| 19 Oct 18:44:03, card | Alex | Engine: "Test first" |
| 19 Oct 21:26-21:29 | Alex | 49 of 52 papers uploaded |
| 20 Oct 05:15:17, card "Adopt the v5.2 list as updated by your papers?" | Alex | **"Adopt all"** (option A) |
| 20 Oct 05:18:46, card "Build the aortic and pulmonary cusp muscle once the papers arrive?" | Alex | **"Both"** (option A): section 8 as written |
| 20 Oct 05:18:51, withdrawn 19 Oct card "Adopt the full v5.2 list on the doc's new tab?" | Alex | "Adopt all" (same answer as 05:15:17) |
| 20 Oct 05:19:07, card "Place each heart in the torso by its own CT orientation?" | Alex | **"CT pose"** (option A): section 9 as written; the atrial fit runs as arm A32 |
| 20 Oct, review | Cloud | Two points put to Alex before the lock time: retrograde junction delay (7.3) and gate 5 comparator (11, row 5) |
| 20 Oct 07:22:39, card "Return the backward junction delay to v5.1's sourced 2 ms?" | Alex | **"2 ms (v5.1)"** (option A): retrograde PMJ delay 2 ms primary, 4 ms arm A22 (dated deviation from the 05:15:17 list) |
| 20 Oct 07:23:01, card "Score gate 5 against Bazan's matched Table 3 bands, as approved 12 Oct?" | Alex | **"Matched bands"** (option A): gate 5 scored on Bazan 2007 Table 3 matched bands, unmatched +74 beside |
| 20 Oct 07:30 | Cloud | **Lock time written** |
| 20 Oct 07:44-07:45 | Alex | Five papers uploaded: de Kerchove 2015, Hasdemir 2007, Schwan and Kay 1956, Kaufman and Johnston 1943, and a second copy of the Campos 2026 main article (re-download; the supplement is read from notes/A/2026-10-19-v52-lit/oa/) |
| 20 Oct 08:28:47, chat | Alex | "I uploaded some more articles / should the purkinje stay a sheet and not a network? / also wha about the not adopted still open suggestsions" |
| 20 Oct, after 08:28:47 | Cloud | Post-lock re-review in three domains (conduction system; outflow anatomy; conductivities, torso and gate rules) of every not-adopted row and open item of section 17, each proposal checked by an independent verifier whose verdicts and corrections override the reviewer (notes/A/2026-10-19-v52-lock/notadopted-review-2026-10-20.json); the summary put to Alex as the doc tab "After the lock" |
| 20 Oct, cards | Cloud | Three cards put to Alex: post-lock card 1 "Junction-free" upper third of the left septum (recommended); post-lock card 2 "Adopt all" for changes 2-10 (recommended); post-lock card 3 "Targeted" calibration-check rule (recommended) |
| 20 Oct 10:33-11:05 | Cloud | **Massing 1976 fan digitisation for D4**, before any beat (method written 10:33 UTC; deviations 1-5 logged 10:41-10:55 before any width was computed; deviation 6, descriptive outputs, 11:05 after the results): full width **22.6 mm** (IQR 20.4-29.9; human ex vivo, n = 7; Figs 8A-11A, pp.614-616); outputs in the shared project folder at notes/A/2026-10-19-v52-lock/massing/ (METHOD.md, results.json, per_case.csv, profiles.csv, summary.json, split.json, code/ and overlays/; the 600 dpi page renders are not kept, being reproducible from METHOD.md) (7.1) |
| 20 Oct, at the time recorded in the answer | Alex | Post-lock card 1: "Junction-free", 20 Oct 2026 11:22:09 UTC: deviation D1 (section 19) |
| 20 Oct, at the time recorded in the answer | Alex | Post-lock card 2: "Adopt all", 20 Oct 2026 11:23:21 UTC: deviations D2-D10 (section 19) |
| 20 Oct, at the time recorded in the answer | Alex | Post-lock card 3: "Targeted", 20 Oct 2026 11:23:49 UTC: deviation G, the calibration-check rule of 11.5 (section 19); under it the 07:30 labels on fix 4 (gates 1 and 7), fix 5's LV helix (gate 5), the sleeve existing-muscle rule (gate 3) and the left-bundle sheet (gate 3, the 07:30 section 11 gate-3 cell) are withdrawn (19.11) |
| 20 Oct, at the time recorded in each answer | Alex | Follow-up items not shown on post-lock card 2: D4 placement "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; D5 (a) "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; D5 (c) "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; D9b, arm A36 "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC (section 19) |
| 20 Oct 2026 13:51 UTC | Cloud | **Re-issued** with section 19; nothing had run on the PC. Assumption 9 (LB sheet anterior-posterior envelope) replaced by a measured, derived value of 22.6 mm (human ex vivo, n = 7; Massing 1976 Figs 8A-11A, pp.614-616): Alex, "Adopt all", 20 Oct 2026 11:23:21 UTC (change 4); its anterior share 0.79 (17.8 / 4.8 mm; a post-hoc output), "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC. Made before any v5.2 beat |
| 20 Oct 2026 17:08 (PC clock 18:32-19:08 CEST) | PC | **Step 0 run on the 13:51 file**, read-only (report README-20261020T170855-4447.md): nothing simulated, no gate value looked at, no model file changed; all checksums matched; reports 34 and 35 complete. Two step-0 rules sent the report to Alex before step 1 (report 34 item 13, the outflow attachments; items 4 and 8, the D1 counts), and five findings bearing on later steps were reported early (the aortic angular frame, the valve discs, the cut on a short posterior RVOT, v5.1's moderator band, A37's list); A35 and A36 failed their feasibility checks (19.15) |
| 20 Oct 2026 17:11:07, PC thread | Alex | **"lock"**, choosing the option "Lock thread": the lock's thread drafts dated fixes for all five issues, then the PC commits LOCK.md and continues |
| 20 Oct, about 17:29-17:35 | Cloud | Five step-0 cards put to Alex (card 1 about 17:29 UTC, card 5 about 17:35 UTC), each with a recommended option. The first version of step-0 card 2 (the valve-plane ring) was **withdrawn unanswered** because its second option's consequence was wrong, and was re-posted about 17:31 UTC |
| 20 Oct 2026 17:32:26, step-0 card 1 "Keep the v5.1 fascicles beyond the sheet's edge, so the sheet still feeds their old endpoints?" | Alex | **"Keep tails"** (recommended): deviation D11 (19.15.1) |
| 20 Oct 2026 17:32:47, step-0 card 3 "Scale the infundibulum cut to each mesh's shorter outflow tract?" | Alex | **"Scale to span"** (recommended): deviation D14 (19.15.4) |
| 20 Oct 2026 17:33:10, step-0 card 4 "Keep the upper left septum junction-free now that the PC has counted v5.1's junctions?" | Alex | **"Keep"** (recommended): deviation D12 (19.15.2), D1 unchanged |
| 20 Oct 2026 17:33:39, step-0 card 2 (re-posted) "Measure the aortic crescents and pulmonary sleeves from the valve disc's mid-plane?" | Alex | **"Mid-plane"** (recommended): deviation D13 (19.15.3) |
| 20 Oct 2026 17:34:23 (relayed) | PC | **Follow-up geometry**, read-only (analysis/v52_2026-10-20/00_step0/followup.json, script step0_followup.py, local commit a2e25a1, not pushed): report 34 item 15 and report 35 (i); no beat, no model file changed, LOCK.md not committed |
| 20 Oct 2026 17:36:27, step-0 card 5 "Adopt the three corrections from the PC's geometry checks: aortic frame, right bundle, torso list?" | Alex | **"Adopt all"** (recommended): deviations D15, D16 and D17 (19.15.5-19.15.7) |
| 20 Oct 2026 19:28 UTC | Cloud | **Re-issued again** with 19.15 (deviations D11-D17); nothing had been simulated on the PC; step 0 is not repeated, and its outputs and the follow-up geometry stand (0.2). Made before any v5.2 beat |

Nothing in this file was chosen to pass an Aim 1 check. Where a change was prompted by a check's failure, is aimed at
that check's mechanism, or was accepted by Alex on a card as making that check a calibration check (post-lock card 1:
gate 1 for D1), the check is labelled a calibration check in section 11 and in every v5.2 report (the Targeted rule of
11.5; deviation G, 20 Oct 2026). Where a change is tuning-shaped (it
leans a failing gate toward passing), that is said where the change is written.

### 0.2 Status of the cards and the two review points

- The cusp-muscle card answered "Both" (20 Oct 05:18:46 UTC): aortic crescents and pulmonary sleeves are built as
  section 8 says. The swap-in blocks of section 8.9 are not used and stay only as a record.
- The pose card answered "CT pose" (20 Oct 05:19:07 UTC): each heart keeps its CT orientation and is only translated (section
  9.1). The swap-in rule of section 9.2 is not used; the atrial fit runs as arm A32.
- The two review points are answered: retrograde junction delay 2 ms (v5.1), 07:22:39 UTC (section 7.3); gate 5
  scored on the matched Table 3 bands, 07:23:01 UTC (section 11, row 5).
- The lock time is written (header). Step 0 ran on the 13:51 file and is not repeated (below; 15.2 step 0); on this
  file the build continues at step 1 when Alex has the PC on, with his OK for runs over 10 minutes (15.1). The 07:30
  text, "The build may start at step 0 when Alex has the PC on ...", is superseded.
- When the second re-issue time is written, this file (as re-issued again) is committed and its hash recorded in
  PROGRESS.md and LABNOTES before any beat (step 1); neither the 07:30 nor the 13:51 file is committed as the v5.2
  lock.
- **Re-issued (20 Oct 2026 13:51 UTC; re-issue, 20 Oct 2026).** After the 07:30 lock and before any beat, Alex's 08:28:47
  questions led to a verified re-review, three post-lock cards and four follow-up items (0.1). The answers are applied
  as deviations D1-D10 and G, each written out in section 19 and tagged where it lands. At 13:51 the PC was to commit
  the re-issued file at step 1 in place of the 07:30 file; that is superseded by the second re-issue (next bullet).
  Step 1's acceptance refuses a file that still holds an unfilled placeholder (a card or follow-up answer, or the
  re-issue time): stop and report. The Massing measurement of 7.1 is done and written in (20 Oct 2026, 10:33-11:05
  UTC).
- **Re-issued again after step 0 (20 Oct 2026 19:28 UTC; deviations D11-D17, 20 Oct 2026).** The PC ran step 0 on the 13:51
  file (report README-20261020T170855-4447.md, 20 Oct 2026 17:08 UTC). **Step 0 is not repeated on this file**: its
  outputs stand (the 17:08 report, reports 34 and 35, the checksums, which all matched, and the A35 and A36 feasibility
  results, both failed, 9.4), and so does the follow-up geometry measured read-only afterwards (report 34 item 15 and
  report 35 (i); relayed 20 Oct 2026 17:34 UTC; followup.json, local commit a2e25a1). Its two step-0 stops are
  answered: the outflow attachments (report 34 item 13) by D11, and the D1 counts (items 4 and 8) by D12; the later
  findings it reported (two of which would have stopped a step) are answered by D13-D17. Alex chose "Lock thread"
  ("lock", 20 Oct 2026 17:11:07 UTC) and answered the five step-0 cards (0.1); each deviation is written out in 19.15
  and tagged where it lands. The PC commits **this file**, unchanged, at step 1; the 13:51 file
  (LOCK-2026-10-20-1351.md) is superseded, as the 07:30 file (LOCK-2026-10-20-0730.md) already is, and neither is
  committed. Step 1 still refuses a file that holds an unfilled placeholder: stop and report.
- **If an answer differs from the option the text is drafted on.** Section 19 is written for post-lock card 1 =
  "Junction-free", post-lock card 2 = "Adopt all" (changes 2-10), post-lock card 3 = "Targeted", and "adopt" for each
  follow-up item. If any answer differs, or adopts only part of post-lock card 2, the "If declined" text of each
  affected deviation (19.1-19.11) is applied to every section it names (that text is the 07:30 text unless the "If
  declined" line says otherwise, as for the D4 placement, whose envelope is then centred on the v5.1 footprint and the
  build continues), before the re-issue time is written. Step 1 refuses a file whose 0.1 answers do not match the
  options its text is drafted on, unless the "If declined" text of section 19 has been applied: stop and report.
  The same holds for 19.15: D11-D17 are drafted on the recommended option of each step-0 card ("Keep tails",
  "Mid-plane", "Scale to span", "Keep", "Adopt all"), each has its own "If declined" line, and every answer took the
  drafted option (0.1), so no "If declined" text of 19.15 is applied.

### 0.3 Change rule

- Any change to a value in this file needs Alex's word and a dated deviation entry (LABNOTES on the PC, PROGRESS.md in
  the cloud).
- No value here may be changed, and no structure resized, after a v5.2 result is seen. The crescent thickness
  (section 8.5), the sleeve geometry (section 8.6) and the stimulus clipping rule (section 8.7) are singled out: they sit
  on failing gates 1 and 3 and are fixed in writing now.
- Arms are reported as ranges beside the primary. Verdicts come from the primary only. No arm is promoted after its
  result is seen. An arm marked "prompted by a fail" would make that gate a calibration check if it were ever promoted.
- Reports never change a model value or a locked verdict.
- Every number below carries its source, species and n. Values I derived are marked "derived" with the arithmetic shown.
  Values with no source are marked "model assumption" and collected in section 16.

## 1. Unchanged from v5.1

- Conduction system speeds:
  - HIS / RB / LB trunk 1.5 m/s; fascicles 2.0 m/s;
  - distal Purkinje at a straight-line 2.0 m/s (v_edge per heart as in v5.1).
- The v5.1 Purkinje graph network itself (nodes, edges, classes HIS / RB / LB_TRUNK / FASCICLE / DISTAL, per-heart
  v_edge) is the starting point. Section 7 states exactly what the left-bundle sheet adds to it and what it leaves alone;
  the right bundle, its moderator-band edge included, is v5.1's, unchanged (deviation D16, 20 Oct 2026; 7.2).
- The 6G8DD8S5 LBBB cut (section 7.8 states how it is applied to the sheet).
- Stimulus: the **1.5 mm radius** ball (3 mm across), as v5.1's code implements it (v51-pc-run memory, 16 Oct: "Stimulus:
  radius 1.5 mm (3 mm ball)"; the 15 Oct brief had left "radius or diameter?" open and the PC answered it). The clipping
  rule of section 8.7 applies at every site, and is a no-op wherever nothing changed, so v5.1 sites stay bit-identical.
- RV fibres: Doste 2019 on the whole RV (RV side of the septal split, d > 0.5), bit-identical to v5.1.
- Meshes; the T13 torso; torso 0.2 S/m; no lungs.
- LV and RV cavity blood (v5.1 surfaces, 0.7 S/m). ECG source term sigma_i (Alex, 18 Oct).
- Measurement: ecg_depth_criteria 0.4.0 with the 10 % QRS-end rule (C1, which won the 19 Oct calibration).
- The **v5.1 core of 579 beats** (sites.json, families, pairs) and their composition: 3 His beats, 432 paced sites
  (144 per heart), 144 no-network beats of the control heart. v5.2 **adds** beats at the new sites and for the new
  reports; every added beat is counted in the site-and-beat ledger of section 11.2a, which is what step 7's acceptance
  is checked against. No v5.1 beat is dropped.
- The Table A gate rules (section 11, restated verbatim there) and the monodomain rule: 27 sites, 4 measures, 5 ms, at
  least 98 of 108 pairs, with the bias-band fallback. ("At least 90 % of 108" and "at least 98 of 108" are the same
  rule: 0.90 x 108 = 97.2, and an integer count of at least 97.2 is at least 98.)

## 2. Fix 1: repolarisation in the ECG template

v5.1 has one Tomek tissue template per heart from the openCARP template run. It covers -60 to +80 ms around activation,
then holds at 13.9 mV, so there is no repolarisation and no T wave.

### 2.1 Rules

- **R1.1 Cell model.** The same openCARP Tomek model (ToR-ORd, Tomek 2019, human ventricular myocyte) the monodomain runs
  use. Single-cell (bench) runs of the endocardial and the epicardial cell type at CL 1000 ms, paced until APD90 changes
  by less than 0.5 ms over the last 10 beats. Record each type's APD90 and its last beat at 1 ms.
  - **Run the cell model to get these two numbers.** Tomek 2019 prints no APD90 for the three cell types (checked by
    full-text search), so the baseline cannot be quoted. A reader's measurement off Appendix 1-figure 9 gives about
    290 ms (endo) and 258 ms (epi), a difference of about 32 ms with about +-5 ms on the difference; that figure reading
    is a sanity check only and is never used as a value.
  - If the installed model has no epicardial cell type, stop and report.
- **R1.2 Shape.** Every node keeps the v5.1 tissue template up to +80 ms after its own activation. From +80 ms it follows
  the single-cell trace of its blend (R1.3), aligned at the upstroke. The two are joined by a linear cross-fade over
  **+80 to +100 ms**, with **voltage continuity enforced**: the cell trace is offset by a constant so that its value at
  +80 ms equals the template's held 13.9 mV, and the offset is recorded per blend weight. Without that offset the splice
  puts a step of order 10 mV into every node's trace 80-100 ms after its own activation.
  - **Why this matters for the QRS, against the 19 Oct draft's claim that the window "is built exactly as in v5.1".** It
    is not, for any beat whose activation lasts longer than 80 ms. In a paced beat the nodes activated in the first
    40-65 ms pass +80 to +100 ms while the QRS is still being written, so a discontinuous splice adds a trailing
    transmural source during the late QRS. Order of magnitude (inference): about 10 mV against a 120 mV upstroke is
    about 8 % of the QRS dipole, and the C1 rule ends the QRS at 10 % of peak spatial velocity, with the hidden tail
    already at 0.55 of that threshold (qrs-end memory). So an uncorrected splice could lengthen the surface QRS and
    help failing gate 1 as a template artefact.
  - **Step-4 template-only check (pre-registered).** Recompute the gate-1 and gate-3 beats with **v5.1 activation** and
    the v5.2 template, and report the change in QRS end, QRS duration and MDI caused by the template alone. Any change
    above 1 ms is reported beside gate 1 and gate 3 as a template effect, not a model effect.
  - The splice window (+80 to +100 ms), the continuity offset and the post-+80 ms time-stretch are model assumptions
    (section 16).
- **R1.3 Transmural blend, continuous in w.** w = 0 at the endocardium and 1 at the epicardium, the coordinate v5.1's
  fibre rule uses (the septum as in v5.1).
  - The action-potential shape at depth w is a linear blend, weight w, of the epicardial trace and the endocardial trace.
  - **There is no cell-type step at w = 0.5.** A step puts a source sheet through every wall, and no human data show one
    (Opthof 2017, 3 intact human hearts; Glukhov 2010 found mid-wall islands in 3 of 5 hearts, not a layer boundary).
    **Glukhov interprets those islands as M-cells** ("evidence of the isolated islands of delayed repolarization
    (M-cells) in three out of five non-failing human hearts"), so Glukhov 2010 is a **conflicting** source here, not a
    supporting one: the model does not adopt that interpretation, on Opthof 2017 and Boukens 2017.
  - No mid-wall (M) cell type. Source: Opthof 2017 p.268, "In none of the hearts there is early epicardial repolarization
    or late midmural repolarization" (3 intact human hearts); Boukens 2017 (intact dog hearts, no M cells optically or
    electrically, mid-myocardial APD between endo and epi even at CL 4000 ms). Drouin 1995 did find M cells in human LV
    slices (APD90 439 +- 22 ms at CL 1000, 1 to 4-5 mm from the epicardium, about 30 % of the mass); that is the
    dissection-sensitive preparation Boukens's cut-surface argument predicts, and it is reported as the conflicting
    source, not used.
- **R1.4 APD map, non-failing heart (Y5HYEDL4).**
  - **One mechanism, stated once (the 19 Oct draft gave two).** The trace *shape* at depth w is the linear blend of
    R1.3. The trace *duration* is set by a linear time-stretch after +80 ms to hit a target map that is linear in w and
    **holds the mean fixed**:
    APD90_target(w) = mean(APD90_endo, APD90_epi) + 14 - 28 w ms, so endocardium +14 ms and epicardium -14 ms about the
    measured mean, a difference of 28 ms. For the HF hearts (R1.5):
    APD90_target(w) = 1.110 x mean(APD90_endo, APD90_epi) + 3.5 - 7 w ms.
  - Holding the mean (rather than the endocardial or the epicardial value) is a model assumption, stated so that the
    absolute APD map and the base for the HF x 1.110 are both unambiguous.
  - **Target transmural difference 28 ms, endocardium longer.** Source: Srinivasan 2016, 10 normal human hearts in vivo,
    CL 600, transmural ARI/APD difference 30 ms during RV-apex pacing and 25 ms during LV-endocardial pacing; 28 ms is
    the mean of the two (derived: (30 + 25) / 2 = 27.5, written as 28 ms to the paper's own precision).
  - **28 ms is the TARGET difference, not a gradient added on top of the blend.** The blend of R1.3 already carries
    ToR-ORd's own endo-epi gradient. After R1.1 measures that gradient, the time-stretch of the rule above brings the
    model's endo-epi APD90 difference to 28 ms. If ToR-ORd's own difference is about 32 ms, the implied scale is about
    0.88 (derived). The scale and the per-w stretch factors are recorded in the manifest.
  - **Apex to base: flat, primary.** Opthof 2017 found gradients along every axis and differing between the three hearts,
    so leaving an apicobasal gradient out is a choice between conflicting sources, not an absence of data.
  - Arms: apex 29 ms longer (A4, Srinivasan 2016, the only significant intact human value) and base 25 ms longer (A5,
    Tomek 2019 Appendix 1-15.1.5 p.39, implemented as a graded IKs increase from base to apex, as in ToR-ORd's own
    whole-heart ECG). The two sources disagree on the sign.
- **R1.5 HF hearts (6G8DD8S5, 7D98EVAR).**
  - Mean APD90 x **1.110** over the whole wall, and a transmural difference of **7 ms** (endocardium longer).
  - Source: Glukhov 2010 (Circ Res 106:981), human LV wedges, 5 failing and 5 non-failing, CL 2000 ms, APD80 by layer:
    non-failing subepi / mid / subendo 383 / 455 / 494 ms; failing 477 / 495 / 506 ms.
  - Derived: mean non-failing (383 + 455 + 494) / 3 = 444.0 ms; mean failing (477 + 495 + 506) / 3 = 492.7 ms; ratio
    1.1096, written 1.110. Transmural non-failing 494 - 383 = 111 ms; failing 506 - 477 = 29 ms.
  - Derived default: the intact control value scaled by the wedge ratio, 28 x 29 / 111 = 7.3 ms, written **7 ms**. This is
    a derived value, labelled as such: no paper measures HF transmural repolarisation in an intact human heart.
  - Arm A6: HF transmural 29 ms (Glukhov's own wedge difference).
  - **Why the three per-layer factors of the 19 Oct draft are gone.** Multiplying Glukhov's layer ratios onto a ToR-ORd
    baseline reverses the HF transmural gradient: the epicardium repolarises last unless the baseline gap exceeds
    48.5 ms. Glukhov's own failing wedges keep the epicardium 29 ms shorter.
  - Applying wedge ratios measured at CL 2000 at CL 1000 is an inference.
- **R1.6 ECG window.** From -100 ms to the latest (activation + APD90) of the beat, plus 50 ms.
- **R1.7 Not modelled.** Electrotonic smoothing of repolarisation; activation-APD coupling; restitution. So
  repolarisation = activation + APD exactly and the T wave is approximate.
  - **The T wave is shown, never gated.**
  - The QT and ARI-dispersion predictions of the 19 Oct draft are dropped (section 14).
  - **H5 is not tested by fix 1.** Each modelled beat starts from rest, so no T wave precedes it, and the PVC's own
    conduction at a short coupling interval (restitution) is still missing.
- **R1.8 Standing rule, RE+.** If any T-derived quantity is ever promoted to a gate, a report metric or a claim, that run
  is redone with reaction-eikonal with diffusion (openCARP dream.solve = 1), not with shifted templates.
  - Source: Nagel 2023 (atrial, so it transfers by mechanism and not by magnitude): a template-shifted eikonal gave
    **APD90 absolute error 25.1 +- 20.7 ms** and repolarisation-segment ECG correlation 0.6233, against **RE+ APD90
    error 1.13 +- 1.69 ms** (Fig. 4, p.517) and correlation 0.9953 (Table I, p.517), with an inverted repolarisation
    polarity in aVL. The 1.37 +- 1.16 ms figure the 19 Oct draft quoted here is Nagel's RE+ **activation-time** (LAT)
    difference (text p.516), which is the number used in 11.4, not an APD90 error.

### 2.2 Fix-1 numbers in one place

| Quantity | Primary | Source | Species, n |
|---|---|---|---|
| Cell model | ToR-ORd, endo and epi types, CL 1000 ms | Tomek 2019 | human model |
| Baseline endo-epi APD90 | measured by R1.1 (figure reading about 32 ms, sanity only) | Tomek 2019 Appendix 1-figure 9 | human model |
| Transmural APD90 difference, control | 28 ms, endo longer (blend target, mean held) | Srinivasan 2016 (30 and 25 ms, mean +- SE) | human in vivo, n = 10 |
| Transmural shape | continuous blend, linear in w | Opthof 2017; Glukhov 2010 | human, n = 3 and 10 |
| Apex-base | flat | Opthof 2017 | human, n = 3 |
| HF mean APD90 | x 1.110 (derived) | Glukhov 2010 | human wedges, 5 HF / 5 NF |
| HF transmural difference | 7 ms (derived, 28 x 29 / 111) | Glukhov 2010 plus Srinivasan 2016 | as above |
| Arms | 0 ms; 21 ms epi longer; 111 ms wedge; apex +29; base +25; HF 29 ms; coupling slope -0.71 +- 0.4 (SE), LV-endocardial paced beats only | A1-A7, section 13 | |

## 3. Fix 2: measured extracellular conductivities

This is decision 8's rule (v5.1 brief 4.5) with the v5.2 speeds.

- **R2.1 sigma_e.** Fibre 0.625 S/m, cross-fibre 0.236 S/m, transmural 0.236 S/m.
  - Source: Clerc 1976, via the standard set sigma_i 0.174 / 0.0193 and sigma_e 0.625 / 0.236 S/m.
  - Provenance, recorded: **calf ventricular trabeculae, in vitro, 25 C.**
  - Taking the extracellular space as transversely isotropic (transmural = cross-fibre) is an inference: Clerc measured
    two directions.
- **R2.2 sigma_i.** Fibre 0.174 S/m (Clerc). Cross-fibre and transmural are solved so that
  sigma_m,d = sigma_m,f x (v_d / 0.80)^2, where sigma_m = sigma_i sigma_e / (sigma_i + sigma_e) and
  sigma_m,f = 0.13611 S/m. The code solves R2.2 at full precision; the table below is a check only.

| Heart | Direction | Speed (m/s) | sigma_i (S/m) | sigma_e (S/m) |
|---|---|---|---|---|
| all | fibre | 0.80 | 0.174 | 0.625 |
| Y5HYEDL4 | cross-fibre | 0.23 | 0.01181 | 0.236 |
| Y5HYEDL4 | transmural | 0.48 | 0.06184 | 0.236 |
| 6G8DD8S5, 7D98EVAR | cross-fibre | 0.167 | 0.00608 | 0.236 |
| 6G8DD8S5, 7D98EVAR | transmural | 0.336 | 0.02673 | 0.236 |

- **R2.3 Lead fields.** Myocardium sigma_i + sigma_e; blood 0.7 S/m; torso 0.2 S/m; source term sigma_i. The C9 weight
  check runs against openCARP with sigma_m, as in v5.1, then switches to sigma_i. Assert
  sigma_m,d / sigma_m,f = (v_d / 0.80)^2 to 1e-6.
- **R2.4 Arm S2 (A8), ECG only.** Lead fields with Clerc's full set (sigma_i 0.174 / 0.0193 / 0.0193, sigma_e
  0.625 / 0.236 / 0.236 S/m) in every heart, every beat in the ledger (11.2a), reported beside the primary.
- **R2.5 Arm S3 (A9), ECG only.** The in situ set of Roberts and Scher 1982 (dog, in vivo in situ, open chest, n = 6,
  temperature not reported, action-potential amplitude A = 100 mV assumed, transmural = cross by the paper's own
  axial-symmetry assumption). The paper's means are rho_il 291, rho_it 1677, rho_ol 852, rho_ot 1247 ohm-cm, with SDs of
  13-27 %. Derived conductivities (sigma = 100 / rho ohm-cm): sigma_i 0.344 / 0.0596 S/m, sigma_e 0.117 / 0.0802 S/m.
  Used as tissue-level conductivities with no volume-fraction scaling (Roberts 1979 Appendix A).
  - S3 stays an **arm**, not the primary. Under the project's own evidence rule (prefer in vivo, intact heart) the in
    situ set outranks Clerc for the lead fields, and a reader recommended promoting it. It is not promoted, because
    Alex's 19 Oct 18:27 pick named decision 8's Clerc-based rule and because the primary must be fixed before any beat.
    This is recorded in section 17 as a reader proposal not adopted, so that promoting it later would be a visible,
    dated deviation.
- **R2.6 Bulk conductivity report (never a gate).** Report each set's sigma_i + sigma_e per direction against the in situ
  gross tissue values 0.40-0.50 S/m along fibres and 0.14-0.18 S/m across: Rush 1963 0.40 / 0.18; Roberts 1979
  0.50 / 0.16; Roberts and Scher 1982 0.47 / 0.14 (all dog, in situ). Derived for S3: 0.344 + 0.117 = 0.461 S/m along,
  0.0596 + 0.0802 = 0.140 S/m across, which reproduces that paper's own measured gross values of 0.469 and 0.142 S/m.
  - **Added comparator (report only; 20 Oct 2026, after the post-lock review).** Hooks 2007, pig in vivo, 6 hearts,
    61 sites, p.e108: 0.70 S/m along fibres, 0.35 S/m in the lamina plane across the fibres, 0.16 S/m normal to the
    laminae. Mapping the lamina-plane value onto this model's transmural direction and the lamina-normal value onto its
    in-wall cross-fibre direction is an inference from LeGrice 1995 (dog, 4 hearts, p.H571: cleavage planes run
    radially), and a coarse one, because Hooks's own laminae were not uniformly radial (p.e107). Two of the three dog
    in situ values come from one lab (Roberts 1979; Roberts and Scher 1982), and Rush 1963 is cited, not read.
- **R2.7 Hooks caution.** Hooks 2007's 4:2:1 is a **bulk** (monodomain, intra- plus extracellular) conductivity ratio,
  gf 0.70 / gl 0.35 / gn 0.16 S/m (pig in vivo, 6 hearts, 61 sites). It is never used as a speed ratio and never as an
  extracellular ratio: sqrt(4:2:1) = 2 : 1.41 : 1, while the same group measured a velocity ratio of 4 : 1.8 : 1. Since
  fix 2 solves sigma_i from speeds, importing 4:2:1 anywhere as a speed ratio would silently change the anisotropy.
  **This caution does not apply to a lead-field-only use (deviation D8, 20 Oct 2026):** arm A40 puts Hooks's bulk
  values into the lead field only, with the fix-2 sigma_i as the source term (R2.3: the lead field takes
  sigma_i + sigma_e, the source sigma_i), so nothing reaches the speeds or the propagation.
- **Consequence (derived arithmetic).** With Anderson's speed ratio, R2.2 gives an intracellular fibre-to-cross ratio of
  14.7 in the control heart and 28.6 in the HF hearts. That is above the published sets: 5.7 in MedalCare-XL and about 9
  in Clerc. Stated as a limitation, not corrected.
  - **Added (correction, 20 Oct 2026).** The primary's cross-fibre wavefront fraction sigma_i / (sigma_i + sigma_e) is
    0.048 in the control heart and 0.025 in the HF hearts (derived: 0.01181 / 0.2478 and 0.00608 / 0.2421), far below
    the dog in situ values. The gap comes mainly from fix 4's human speed anisotropy under the R2.2 rule, not from
    Clerc's provenance. Derived: R2.2 run on Roberts and Scher's own set (sigma_i 0.344 and sigma_e 0.117 S/m along
    fibres, sigma_e 0.0802 S/m across) at the control speed ratio (0.23 / 0.80)^2 gives sigma_i 0.0079 S/m across and a
    cross-fibre fraction of only 0.090, that is 10.8 mV at a 120 mV upstroke.
- **Decision 8's run on v5.1** is reported as a v5.1 sensitivity and does not change this fix (PC, 19 Oct 18:59 UTC,
  /mnt/project-files/README-20261019T185935-93bb.md):
  - no Table A verdict changed (gate 5 went 5/21 to 6/21);
  - pseudo-delta, MDI and QRS duration and their 90 % minus 10 % depth effects barely moved: 93-98 % of the 432 paced
    beats stayed within 5 ms (MDI within 0.05);
  - IDT, shortest RS and the lead I q call are fragile: a few beats jump 40-114 ms when a different peak is picked, the
    q call flips in 20 of 432 beats, and the control heart's IDT depth effect goes from -12.5 to -46.5 ms.
  - So the v5.2 predictions for IDT, shortest RS and q waves carry this fragility, and fix 2 plus fix 4 (cross-fibre
    sigma_i 0.0626 to 0.0118) is a larger change than decision 8's.

## 4. Fix 3: blood in the atria and great vessels, and the wall values

- **R3.1 Blood 0.7 S/m**, as in the ventricles.
  - Sources: Geddes and Sadler 1973, human blood at 37 C, Maxwell-Fricke
    rho = 58.0 (1 + 0.75 H / 100) / (1 - H / 100) ohm-cm, which gives 0.71 S/m at Hct 45 % (derived from the formula);
    Geddes and Baker 1967, human at 37 C, Hct 40 %, 148-176 ohm-cm = 0.57-0.68 S/m. Keller 2010, Potse 2018 and
    MedalCare-XL all model blood as its own conductor. Blood is resistive below several hundred kHz (Hoetink 2004), so
    the 1-25 kHz data hold for the ECG band.
  - It fills every non-myocardial torso element inside closed cavity surfaces of the LA (tag 3), RA (4), aortic root (5)
    and pulmonary artery (6).
  - The surfaces are the cohort's endocardial or luminal surfaces, capped at: the valve rings (7-10); the vein rings
    (11-24); the mesh's cut ends of the two great vessels; **and, where pulmonary sleeves are built, at the sleeve's
    inner (luminal) face**, so sleeve muscle is never flooded.
- **R3.2 Gates, as C6-C8.** Each surface closed and consistently oriented (pinch edges counted, as Alex allowed); blood
  within +- 2 % of the enclosed volume; no blood outside; at least 95 % of the luminal faces border blood; report each
  volume.
- **R3.3 Wall values, set now (not after a run).**
  - Atrial muscle: isotropic at the ventricular cross-fibre bulk, **0.248 S/m in the control heart and 0.242 S/m in the
    HF hearts** (derived: sigma_i + sigma_e cross-fibre, 0.01181 + 0.236 = 0.2478 and 0.00608 + 0.236 = 0.2421). Model
    assumption: no atrial measurement is used, and the atria are not excitable in this model.
  - Aortic and pulmonary artery walls: **0.2 S/m** (the torso value). Model assumption, inside Keller 2010's range for
    vessel wall and connective tissue. The nearest measurement read (relabel, 20 Oct 2026): Schwan and Kay 1956 p.666,
    pieces of vein, pulmonary artery and bronchus 250-700 ohm cm, that is 0.14-0.40 S/m (derived, sigma = 100 / rho);
    species, n and frequency are not stated for these pieces, and the aorta was not measured. The walls sit between the summit source and the new blood columns, so the value
    matters and is fixed here.
  - The pulmonary sleeve's overlying fibrous layer (0.32-0.47 mm, Lis 2021) is non-excitable and takes 0.2 S/m.
  - Step 0 of the build order reports what v5.1 used, so the change is visible.
- **R3.4 Arm S4 (A10), ECG only. Levels 0.63 and 0.89 S/m (deviation D7, 20 Oct 2026).** Human blood at Hct 50 % and
  35 % from the Geddes and Sadler 1973 human formula (Table I p.337: rho = 58.0 (1 + 0.75 H / 100) / (1 - H / 100)
  ohm-cm; human blood in vitro, 37 C, 25 kHz). Derived: H = 50 gives rho = 58.0 x 1.375 / 0.50 = 159.5 ohm-cm and
  sigma = 100 / 159.5 = 0.627 S/m; H = 35 gives rho = 58.0 x 1.2625 / 0.65 = 112.65 ohm-cm and sigma = 0.888 S/m.
  - The 07:30 levels are kept as **labelled literature extremes and are not run**: **0.435 S/m** = 230 ohm-cm, Kaufman
    and Johnston 1943 Table IV p.49, defibrinated dog blood in vitro, about half cells by volume (p.50), 2 observations,
    1 kHz, prebiologic calibration; equal to human Hct about 63 % by the same formula (derived: 230 (1 - H / 100) =
    58.0 (1 + 0.75 H / 100) gives H = 172 / 2.735 = 62.9 %). **1.0 S/m**, Schwan and Kay 1956 pp.664 and 669, a stated
    round figure ("about 100 ohm cm") citing Schwan 1941 (not read); equal to human Hct about 29 % stationary (derived:
    H = 42 / 1.435 = 29.3 %).
  - Not tuning: A10 is ECG-only and decides no verdict.
- **R3.5 Blood anisotropy and haematocrit, stated with numbers instead of as a bare limitation.** Along steady laminar
  flow, conductivity rises 25-30 % above randomly oriented blood (human blood in vitro at 37 C; about 19 % at Hct 36 %
  and about 25 % at Hct 48 %), of which 4-9 % is red-cell deformation alone; the in vivo pulsatile change is probably
  smaller (Hoetink 2004 pp.1257, 1260). Haematocrit at 37 C gives 0.89 / 0.80 / 0.71 / 0.63 S/m at Hct 35 / 40 / 45 /
  50 % (Geddes and Sadler 1973 formula). No separate flow-orientation arm is run. **With 0.89 S/m as A10's top level
  (deviation D7, 20 Oct 2026), full flow alignment is covered only at Hct of about 45 % and above** (derived:
  0.71 x 1.25-1.30 = 0.89-0.92 S/m); Hoetink 2004 pp.1257 and 1260 say the in vivo pulsatile effect is probably smaller
  than the steady-flow one. That is stated on the arm's label.
- **R3.6 Report.** The summit and cusp ECG amplitude change from fix 3 alone, per heart.
- **R3.7 Limitations kept.** Blood beyond the cut vessel ends; the lungs; the atria as passive conductors.

## 5. Fix 4: human in-plane speeds (reopens decision A)

| Heart | Fibre (m/s) | Cross-fibre, in-plane (m/s) | Transmural (m/s) | Fibre : cross |
|---|---|---|---|---|
| Y5HYEDL4 (v5.1) | 0.60 | 0.36 | 0.48 | 1.67 |
| **Y5HYEDL4 (v5.2)** | **0.80** | **0.23** | **0.48** | **3.48** |
| 6G8DD8S5, 7D98EVAR (v5.1) | 0.60 | 0.26 | 0.336 | 2.31 |
| **6G8DD8S5, 7D98EVAR (v5.2)** | **0.80** | **0.167** | **0.336** | **4.79** |

### 5.1 Sources

- **Anderson 1993** (J Clin Invest 92:122, doi 10.1172/JCI116540). Living human hearts at surgery, 8 x 8 epicardial
  array at 2 mm. The control group was 14 patients operated to interrupt an accessory atrioventricular connection (WPW
  surgery), 8 male and 6 female, mean age 28 +- 10 y, **range 18-45**. The velocities used here, **longitudinal
  0.80 +- 0.08 and transverse 0.23 +- 0.03 m/s** (ratio 3.5 +- 0.6), are from the **12 of those 14 controls (86 %) that
  showed uniform anisotropic propagation**; the other two had moderately disturbed activation and are excluded by the
  paper. Mildly affected IDC hearts (group I, n = 7) did not differ (0.84 +- 0.09 / 0.23 +- 0.05). Recorded: the pacing
  was at CL 400 on one anterior LV patch.
- **Glukhov 2012** (project PDF), human LV wedges, CL 1000 ms: non-failing 0.92 +- 0.04 / 0.22 +- 0.02 m/s; HF transverse
  0.16 +- 0.02 m/s with anisotropy 5.8, so longitudinal is about unchanged. The HF cross-fibre factor is 16 / 22, so
  0.23 x 16 / 22 = 0.167 m/s (derived). HF fibre stays 0.80 m/s. Recorded: the HF factor rests on 2 against 3 hearts with
  no statistics (Glukhov 2012 Online Table IV).
- **Transmural 0.48 m/s**: Taggart 2000, plunge needles, 51 cm/s in controls. **It is labelled an apparent
  wall-crossing speed, not a sheet-normal speed**, and it reverses the 4:2:1 order MedalCare-XL and Neic 2017 use.
  Human wall crossing agrees: Taggart 0.51 and Betensky about 0.43 m/s.
- **HF transmural 0.336 m/s** (x 0.70): Glukhov 2012, subepicardial 28 vs 40 cm/s.
- **Three speeds, not two.** Caldwell 2009 p.438: a transversely isotropic (two-speed) experiment-specific model of the
  same pig hearts "failed to reproduce even the qualitative features of experimental data obtained under exactly
  comparable conditions".
- **Outflow tracts take the same speeds as the rest of the ventricle.** Boukens 2013 (mouse, ex vivo, n = 3-9): adult
  RVOT transversal conduction velocity about 0.37-0.48 m/s against RV free wall about 0.45-0.465 m/s, no significant
  difference, despite markedly lower Gja1 and Scn5a; slowing appears only with ajmaline or a Brugada sodium-channel
  mutation. Caveats recorded: mouse, ex vivo, transversal only (longitudinal was unmeasurable in the adult RVOT, so this
  paper cannot constrain outflow anisotropy at all), and the fetal RVOT genuinely is slow. Applying LV speeds to the
  outflow tracts goes in Limitations.

### 5.2 Why decision A's 0.36 m/s is replaced

- 0.36 came from Taggart's epicardial array values, which are "effective" speeds of a wave arriving from a remote RV
  pacing site over 1.5 cm: longitudinal about 0.65, transverse 0.48 m/s in controls.
- In this model that measure does not respond to the cross-fibre input: v5 at 0.48 gave 0.636 m/s across, and v5.1 at
  0.36 gave 0.65 m/s.
- Anderson and Glukhov measured near the pacing site, where the model's apparent speed equals its input: v5.1 gave
  0.59 / 0.37 m/s 3-10 mm from a mid-wall site for inputs of 0.60 / 0.36.
- So using these values as the tensor speeds matches the human measure at its own scale. This is an inference.

### 5.3 How the speeds reach each engine

- **R4.1 Graph eikonal factors.** Refit on the synthetic slab (v5.1 option 1). Acceptance A with v5.1's tolerances:
  principal +- 1.5 %, rays +- 3 %, rotating wall +- 2 %. The rotating wall uses the v5.2 LV profile (+66 to -41 deg).
- **R4.2 Fallback.** If acceptance A fails with the 2-ring stencil, use the 3-ring stencil (graph distance <= 3, edge
  <= 5.25 mm, same rules as S2) and retest. If that fails too, stop and report. No region factors, no tuning.
- **R4.3 Acceptance C** (openCARP eikonal at the v5.1 sites, including the two 7D98EVAR sites that did not converge):
  report only, no time cap.
- **R4.4 Monodomain, tuned as Alex decided on 18 Oct: on a flat block with straight fibres.** Re-tune the
  conductivities on a **flat block with straight fibres** (Alex, 18 Oct; MEMORY.md), at the hearts' element size and
  again at **each mesh of the gate-9 ladder** (11.4 item 1), holding the sigma_i / sigma_e ratio fixed from fix 2's
  Clerc sigma_e, until the measured plane-wave CV equals the v5.2 speeds within 3 % on all three axes
  (0.80 / 0.23 / 0.48 control; 0.80 / 0.167 / 0.336 HF). openCARP **tuneCV (Costa 2013) on 10 cm strands may be used
  only to generate the starting values** for that flat-block tuning; it is not the tuning method, and the 19 Oct draft's
  wording that replaced the flat block with tuneCV is withdrawn. Publish the tuned sigma and the achieved CV at every
  element size. If 0.167 m/s cannot be reached, or conduction blocks, stop and report.
  - **Which sigma goes where (stated, because the draft said "one and the same conductivity set").** Propagation in each
    engine uses that engine's **tuned** sigma at its own element size. The **lead fields and the monodomain ECG source
    term use the fix-2 sigma_i / sigma_e of R2.1-R2.3, unchanged**, so the forward problem is identical across engines
    and only the propagation solution differs. This is the only legitimate reading of "all engines use one conductivity
    set", and it is what gate 9 needs to compare like with like.
  - **Engine amendment 3, restored (adopted list row for the engine test).** At 1 mm, measure the monodomain's
    **achieved speed per axis inside each heart** (not only in the block or strand), and report the **signed bias** per
    axis. If the in-heart cross-fibre speed is more than 10 % slow, the signed bias is reported and the comparison is
    treated as a calibration, not as engine disagreement. Pre-registered as a report; it never changes the gate-9 rule.
  - Why tune at all: an untuned 1 mm monodomain does not implement the fix-4 speeds, so gate 9 would measure
    discretisation error rather than engine disagreement (Niederer 2011 p.4346; Nagel 2023 does the same tuning in the
    same code family).
- **R4.5 Network edge speeds stay bit-identical to v5.1**; the straight-line apparent speed of the network is reported.

### 5.4 Fix-4 reports

- Emergent 6 mm transmural transit, against Taggart's 12.6 ms.
- Far-field transverse speed, against 48 cm/s.
- Near-site apparent speeds 2-7 mm from an LV free-wall epicardial site.
- The A9 RV isochrone ratio (section 12), paired with fix 5 as well as fix 4.
- The achieved plane-wave CV of every engine on every axis at every element size, control and HF.

## 6. Fix 5: human LV helix (Lombaert 2012) and the outflow blend

- **R5.1 LV body** (LV side of the septal split, d <= 0.5): helix angle alpha(w) = 66 - 107 w degrees, linear in
  transmural depth w (0 endocardium, 1 epicardium).
  - The fibre is the local circumferential direction of v5.1's frame, rotated by alpha(w) about the transmural axis.
  - There is no bislerp between endocardial and epicardial frames, which removes the blend's mid-wall offset (about
    +30 deg in v5.1, audit TA-3).
  - Transverse angle 0, as in v5.1. Same sign convention as v5.1's +60 deg endocardium.
  - Source: Lombaert 2012 (IEEE TMI 31:1436), 10 human ex vivo DT-MRI hearts: -41 +- 26 deg at the epicardium to
    +66 +- 15 deg at the endocardium, with "a linear dependence between the helix angle and the transmural location".
    Greenbaum 1981 histology agrees on a near-circumferential mid-wall.
  - One profile for every heart. Lombaert's apex differs but gives no numbers, so the apex is a limitation.
- **R5.2 Outflow blend.** In the LVOT, the summit region and the subvalvar region, the helix profile blends to the
  outflow angles **0 deg epicardial and 90 deg endocardial at the aortic valve**.
  - Source: **Doste et al. 2019, Int J Numer Method Biomed Eng 35:e3185, section 2.3.1 / Eq. 3, pp.5-6** (the OT-RBM
    paper, **in the project file set**): "Outflow tracts (based on Sanchez-Quintana): alpha epi (w = 0) = 0 deg
    (circumferential); alpha endo (w = 0) = 90 deg (longitudinal)". Re-cited: the Europace 2020 paper names the method
    but states no angles. The paper states explicitly that its alpha **is not equivalent to the histological helix
    angle**; it is a rule-based outflow angle.
  - The blend runs over the band between the LV body and the valve plane, **linear in the normalised long-axis
    coordinate z over the fixed interval z = 0.80 (LV-body boundary) to z = 1.00 (valve plane)**, where z is the same
    long-axis coordinate v5.1's frame uses, normalised apex 0 to valve plane 1. Fixed here as a model assumption (Doste
    states the end angles, not the band), and recorded in the manifest; it is no longer "the model's own choice" made at
    build time.
  - Crescent muscle (section 8.5) takes this same blend.
  - Arm A16: LVOT fibres circumferential through the whole wall (Acosta 2015 histology describes both the
    subendocardial and the subepicardial LVOT fibres as circumferential or spiral).
- **R5.3 Gates.**
  - LV free-wall angles at w = 0.1 / 0.5 / 0.9 equal 55.3 / 12.5 / -30.3 deg within 0.5 deg;
  - RV-region fibres bit-identical to v5.1;
  - frames orthonormal;
  - one connected fibre field (v5.1 A8 rule).
- **R5.4 Reports.** Signed angle per region against the cohort's own fibre field (the one check that would catch a helix
  sign error); the helix angle at every gate-5 stimulus node. Arm A15 keeps the v5.1 fibres for gate 5 only.
- **R5.5 Recorded.** If the OT fibre field is taken from the Doste OT-RBM, it was exercised in Doste 2020 with only two
  velocities (0.68 along, 0.26 transverse) and no sheet-normal speed, so the OT geometry has never been run with a
  distinct transmural speed in its source publication.

## 7. Conduction system

### 7.1 Left bundle as a septal sheet (primary, new in v5.2)

The left bundle is built as **one interconnected subendocardial sheet** on the left septal surface, not as two or three
separable fascicles.

| Quantity | Value | Source | Species, n |
|---|---|---|---|
| Origin width | 6 mm | Massing 1976 Table 1, median (my recompute: median 6.0, mean 6.66 +- 4.21, IQR 3.5-9.5, range 0.5-14.0 mm; the paper's own text gives "less than 1 mm to 14 mm") | human ex vivo, **n = 27 non-neonatal hearts (ages from 9 y; Table 1 excludes only the 5 neonates, and cases 5 and 9 are aged 9 and 15)** |
| Independent origin width | 6-10 mm, ribbon-like, subendocardial | Demoulin 1972 p.808 | human ex vivo, n = 20 control hearts |
| Widening | reaches maximal width over the first 10-15 mm | Elizari 2017 p.5 | human ex vivo, 60 human of 206 hearts |
| Undivided run | at least the first 10 mm | Massing 1976 p.612, 11 of 13 hearts (some 20 mm or more) | human ex vivo |
| Length base to apex | 33 mm (range 24-41) | Massing 1976 p.614, stated average | human ex vivo, n = 10 |
| Thickness | one element (4-25 cell layers proximally, 1-10 in the fibre groups, so of order 0.06-0.6 mm) | Massing 1976 pp.613-614 | human ex vivo |
| Topology | a sheet, not a cable; three preferential outflows (anterior, septal, posterior); no separable fascicles | Massing 1976 **p.618** (0 of 13 hearts, and 0 of Tawara's 2, bifascicular without major interconnections); Demoulin 1972 p.809 (peripheral anastomoses in 20 of 20); Stephenson 2017 (broad sheet draped over the left basal septum) | human ex vivo; Stephenson n = 1 whole heart, micro-CT 73 um |
| Anterior-posterior envelope, maximum full drawn width (**deviation D4, 20 Oct 2026**) | **22.6 mm** (IQR 20.4-29.9, range 17.3-31.9). Widest at a median 25.7 mm from the origin (0.89 of the drawn length, IQR 0.77-0.92). The measured width profile is reported, not applied (assumption 10 kept) | Massing 1976 Figs 8A, 8B, 9A, 9B, 10A, 10B and 11A (pp.614-616). Measured on 20 Oct 2026 on each panel's own in-frame photographed ruler or drawn scale bar (drawn bars: cases 1, 3 and 6), by the method of notes/A/2026-10-19-v52-lock/massing/METHOD.md (written 10:33 UTC, before any width was measured; its logged deviations are listed below; overlays in notes/A/2026-10-19-v52-lock/massing/overlays/). **Derived**: per-heart maxima 17.3 (case 7), 20.2 (case 4), 20.7 (case 6), 22.6 (case 5), 28.4 (case 3), 31.4 (case 1) and 31.9 (case 2) mm; median = the 4th of 7 = 22.6 mm; quartiles 20.15 + 0.5 x (20.69 - 20.15) = 20.4 and 28.35 + 0.5 x (31.38 - 28.35) = 29.9 mm. A lower bound toward the specimen margins and the distal fan | human ex vivo, **n = 7** of the 10 non-neonatal hearts (cases 1-7, ages 9-83 y). Cases 8-10 (Figs 12A, 12B, 11B) are excluded by the pre-set rule: the drawn ink cannot be separated from the black photographic background. Fig 13 is neonatal and excluded by design |

- **Geometry rule.** The sheet starts at the His exit on the left septal crest, is 6 mm wide at its origin, widens
  linearly to its full width over the first 12.5 mm (the midpoint of Elizari's 10-15 mm; model assumption), carries no
  internal conduction boundary for the first 10 mm, and extends 33 mm along the base-to-apex direction of the left septal
  surface. **Its anterior-posterior envelope is 22.6 mm at its widest** (derived, from Massing's drawings; table above;
  deviation D4, 20 Oct 2026; post-lock card 2, change 4, "Adopt all", 20 Oct 2026 11:23:21 UTC). This replaces model assumption 9 (the 07:30 rule:
  the v5.1 network's LV septal node footprint). The full width is reached by the linear widening of assumption 10
  (kept as locked) at 12.5 mm and held to the sheet end; the measured profile is reported beside the value (below) and
  is not applied. Massing's text publishes no fan width, so the width was measured from his drawings. The value is the
  pre-specified primary quantity of notes/A/2026-10-19-v52-lock/massing/METHOD.md (the median of the per-heart maxima), was used whatever it turned
  out to be, and was not chosen with reference to any gate; its effect on gates 2, 6 and 7 is unknown in direction, so
  it is not tuning-shaped.
- **Placement about the His line (derived; a post-hoc output, METHOD.md deviation 6 (d); follow-up item,
  "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC).** At the widest level the drawn envelope lies mostly anterior to the origin: a median 0.79 of it
  (IQR 0.69-0.82; 6 of 7 hearts above two-thirds, case 3 the exception at 0.42). The sheet is therefore laid out
  **17.8 mm anterior and 4.8 mm posterior** of the base-to-apex line through the His exit (derived: 0.788 x 22.6 = 17.8;
  22.6 - 17.8 = 4.8), with the same split at every level while the sheet widens (assumption 9, restated). The share
  depends on defining the origin as the mean position of the first 1 mm of ink, and it was computed after the widths
  were seen, so it is labelled post-hoc; it was not shown on post-lock card 2. **If it is declined, the envelope is
  centred on the v5.1 LV septal node footprint** (the 07:30 placement basis of assumption 9) **with the measured
  22.6 mm width**: at each level it is laid 11.3 mm anterior and 11.3 mm posterior (derived: 22.6 / 2) of the
  footprint's anterior-posterior midpoint on the left septal surface (reported at step 0, report 34 item 13), with the
  same split while the sheet widens, and the build continues. **The midpoint at each level (model rule, assumption 9;
  fixed before any beat):** report 34 item 13 gives it at 2.5 mm steps along the sheet's base-to-apex direction from
  the His exit and at the sheet's 33 mm end; between two of those levels it is interpolated linearly, and it is never
  extrapolated. If item 13 can give no midpoint at one of those levels (no footprint node there), no midpoint is
  guessed: under a declined placement the build stops after step 0 and the placement goes to Alex before step 1; under
  the adopted placement this is reported only. The step-0 fascicle-endpoint check (report 34 item 13)
  still runs, against that envelope, with its stop rule unchanged (fallback fixed before any beat; deviation D4,
  20 Oct 2026).
- **Step-0 check of the outflow attachments (report 34 item 13).** Before any beat, the anterior-posterior distance
  between the v5.1 anterior and posterior fascicle endpoints, measured on the left septal surface at their level, is
  reported against the 22.6 mm envelope, with each endpoint's position against the 17.8 / 4.8 mm split and against the
  centred 11.3 / 11.3 mm envelope that applies if the placement is declined (above). If either
  endpoint lies outside the envelope that applies under the placement answer (outside either envelope while that
  answer is still open at step 0), or the envelope runs off a heart's left septal surface, the build stops after
  step 0 and the attachment is put to Alex before step 1. **The envelope is not widened to reach an endpoint.**
  **Run at step 0 on the 13:51 file (deviation D11, 20 Oct 2026).** The posterior endpoint lies outside the envelope in
  all three hearts, 57.8 / 48.4 / 48.2 mm down the His line, 15-25 mm beyond the 33 mm sheet end; the anterior endpoint
  lies 2.2 mm (Y5HYEDL4) and 6.8 mm (7D98EVAR) beyond the envelope's anterior edge at its level, and inside it in
  6G8DD8S5; the envelope stays on the left septal surface (0 nodes off it) (report 34 item 13). The build stopped after
  step 0 and the attachment went to Alex, who chose "Keep tails" (step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC): the outflows are
  fixed by D11 (the three outflows, below). The envelope was not widened.
- **Massing digitisation, as run (deviation D4, 20 Oct 2026).**
  - **Method.** notes/A/2026-10-19-v52-lock/massing/METHOD.md, written 20 Oct 2026 10:33 UTC, before any width was measured. Six deviations are
    logged there with their UTC times. Deviations 1-5 (10:41-10:55 UTC), all made before any width, length or profile
    was computed, changed the segmentation (Gaussian descreening and hysteresis from a per-panel core threshold) after
    case 2's raw mask and then all ten masks had been seen, set the crops, added case 4's thin posterior strand as drawn
    ink, and recorded the three exclusions under the 10:33 rule. The per-panel threshold constants (+5 grey levels, a
    10 px disk) were chosen after seeing which fixed thresholds worked for cases 2, 3 and 5, a stated limitation.
    Deviation 6 (11:05 UTC) added descriptive outputs after the results were seen: the specimen-edge judgement, the
    edge-free subset, the width/length ratio, the anterior/posterior split and the 12.5 mm fraction. None of them
    replaces the pre-specified primary median, and none sets a model value except the placement, which is a follow-up
    item (above).
  - **Cases.** All ten adult panels in Figs 8-12 (Fig 8 = cases 1 and 2; Fig 9 = 3 and 4; Fig 10 = 5 and 6; Fig 11 =
    7 and 10; Fig 12 = 8 and 9) were examined. Cases 8, 9 and 10 are excluded (ink not separable from the background),
    so the primary is n = 7, cases 1-7 (Figs 8A-11A); a ten-case summary on hand-traced outlines is a sensitivity only.
    Fig 13 shows the neonatal cases 11-13 and is not used.
  - **Calibration.** Each panel on its own in-frame scale: photographed rulers in Figs 8B, 9B, 10A, 11A, 11B, 12A and
    12B, drawn scale bars in 8A, 9A and 10B (cases 1, 3 and 6, +-4-6 % from tick-width ambiguity).
  - **Measurement.** The full anterior-posterior width of the drawn left bundle (the envelope across fibre groups and
    the gaps between them) at every pixel row, sampled every 2.5 mm from the origin and at each tenth of the drawn
    length; the per-heart maximum is the primary quantity, summarised as the median and IQR across cases. Each case's
    drawn length is reported against Table 1 p.610 (cases 1-10: 32, 33, 33, 45, 26, 24, 32, 41, 27, 35 mm).
  - **Exclusion rule (fixed before measuring).** A case is excluded if its panel has no in-frame ruler or scale bar, if
    its graduations or end ticks cannot be located, or if its ink cannot be separated from the photographic background.
    Excluded cases are listed with the reason.
  - **Where it was done, and where it is kept.** In the cloud, before any beat. The outputs are kept in the shared
    project folder at notes/A/2026-10-19-v52-lock/massing/: METHOD.md, results.json, per_case.csv, profiles.csv,
    summary.json, split.json, the code (code/) and the overlays (overlays/). The 600 dpi page renders are not kept;
    they are reproducible from METHOD.md.
- **Reported beside the value (no value changes; not arms unless Alex adds them).**
  - Sensitivities on the same drawings by the same method: without the length-flagged case 4 (drawn 24.4 mm against
    Table 1's 45 mm): 25.5 mm (IQR 21.2-30.6, n = 6); cases whose fan reaches no specimen or photograph edge (cases 4
    and 6 are lower bounds): 28.4 mm (IQR 22.6-31.4, n = 5); principal ink axis instead of the panel vertical: 22.3 mm;
    scale set so that each drawn length equals Table 1: 24.3 mm (IQR 19.0-28.6); width over drawn length 0.77 (IQR
    0.74-0.84), i.e. 25.5 mm on the 33 mm sheet (derived: 0.774 x 33); segmentation thresholds move the median by -1.9
    to +0.5 mm; the three excluded hearts, inside hand-traced outlines: 38.5 mm (case 8, a lower bound), 19.5 or
    14.6 mm (case 9) and 20.3 mm (case 10), giving a ten-heart median of 21.7 mm.
  - At the widest level the drawn ink covers a median 57 % of the envelope (range 30-97 %); the rest is gaps between
    fibre groups, which the sheet's no-boundary topology spans.
  - **The measured profile (reported, not applied).** Median full drawn width (mm, IQR) by fraction of each heart's
    drawn length, n = 7: 0.0: 1.5 (1.3-2.9); 0.1: 6.0 (4.0-9.2); 0.2: 9.4 (7.5-13.4); 0.3: 12.4 (9.8-16.2); 0.4: 16.1
    (13.0-18.6); 0.5: 18.3 (15.7-22.4); 0.6: 20.6 (17.4-26.0); 0.7: 21.7 (16.9-28.2); 0.8: 22.5 (18.4-27.7); 0.9:
    20.1 (17.1-20.4); 1.0: 0.8 (the last strand tip only). The width at 12.5 mm is a median 0.64 of each heart's
    maximum (IQR 0.56-0.71), and the envelope keeps widening to 0.75-0.92 of the length. The drawings therefore do not
    show full width by 12.5 mm: the envelope of the divided fibre groups is not the compact ribbon Elizari measured, and
    assumption 10 is not supported by them. Replacing the widening rule with the measured profile would replace
    assumption 10; that needs Alex's own word and is not part of D4.
  - **Limits.** The drawings are reconstructions from sections 100-300 um apart (p.610), with gaps under 100 um not
    drawn and boundary cells sometimes "difficult to determine" (p.614). Each width is a projected chord on a
    photograph whose ruler need not lie in the septal plane. The drawn lengths ran a median 1.11 times Table 1 (IQR
    1.04-1.15). The exclusions (among them the widest drawn fan, case 8) and two lower-bound cases (4 and 6) bias the
    value low, so 22.6 mm is probably conservative, and n = 7 is small. The specimens exclude the paraseptal free walls
    (p.620) and the anterior papillary muscle (p.610), so no width says where the bundle ends anteriorly or
    posteriorly.
- **Built on the v5.1 network (amended by deviations D11 and D16, 20 Oct 2026).** The sheet replaces the v5.1
  LB_TRUNK and FASCICLE nodes and edges **only inside its envelope** (D11; step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC). Beyond the
  envelope each v5.1 fascicle path (anterior, septal and posterior) is kept exactly as v5.1 built it, with the distal
  trees it feeds, and joins the sheet through its own v5.1 edge across the envelope's edge (assumption 56; the three
  outflows, below). The v5.1 LV distal network, its nodes, its edges and its per-heart v_edge are kept unchanged,
  except that its junctions above the D1 line on the left septal surface are removed (deviation D1, 20 Oct 2026;
  below), and every v5.1 DISTAL edge that joined an LB_TRUNK or FASCICLE node inside the envelope joins the sheet node
  at the same mesh node instead, or the nearest sheet node if none shares it (assumption 56). The 13:51 text said "the
  sheet connects to them where the v5.1 fascicle endpoints were" (superseded by D11). The RV network is v5.1's,
  unchanged, its moderator-band edge included (deviation D16, 20 Oct 2026; 7.2); the 13:51 text added "the
  moderator-band chain of 7.2 (deviation D2, 20 Oct 2026), which joins the nearest v5.1 RV distal-network node", which
  is not built. The sheet's edge speed is the v5.1 LB trunk speed, 1.5 m/s, for the first 10 mm, and the fascicle
  speed, 2.0 m/s, beyond it.
- **No conduction-blocking boundary** is inserted between anterior and posterior territories.
- **Discretisation, fixed now (model assumption).** The sheet is a triangulated strip on the left septal endocardial
  surface with node spacing **1.0 mm** (the mesh's own mean edge), edges along the triangulation, and speeds as above.
  Because a graph on a triangulated surface over-estimates distance, the **metrication error is measured and reported**:
  the graph distance between the sheet's origin and its distal corner against the surface geodesic distance, per heart,
  with the edge speeds left unchanged whatever it shows (correcting it would be tuning a failing gate's input).
- **How the sheet couples to muscle (deviation D1, 20 Oct 2026; post-lock card 1, "Junction-free", 20 Oct 2026 11:22:09 UTC).** **No PMJ on any sheet node above
  the D1 line on the left septal surface, and a PMJ at every sheet node below it**, each with the antegrade and
  retrograde delays of 7.3. The sheet's first 10 mm (the undivided run, Massing p.612) stays junction-free in every
  heart, wherever the line falls. Written before any beat and never changed afterwards.
  - **The D1 line, defined once (assumption 46).** One third of the septal crest-to-apex length, measured along the left
    septal surface from the crest. AHA segments 2 and 3 and UVC z >= 0.67 are reported beside it as cross-checks only and
    are never used to place it: Durrer's thirds are septal thirds, and UVC z = 1 may sit at the valve plane or at the
    MV+TV centre rather than at the crest (report 34 item 10). The paraseptal free wall (AHA 1, the area of Durrer's
    anterior early site) is not part of the mask.
  - **The same line on the v5.1 LV distal network.** No PMJ on v5.1 LV distal-network nodes above the line on the left
    septal surface. Step 0 counts the LV septal junctions above the line per heart and per AHA segment (report 34 item 4);
    if the count is near zero, the network part changes nothing, and that is recorded. Step 0 also reports whether v5.1's
    LB_TRUNK and FASCICLE nodes carried PMJs (item 8): if they did not, the 07:30 rule had added upper-septal junctions
    relative to v5.1, and D1 partly restores v5.1. Post-lock card 1 was answered without items 4 and 8, which the
    re-review asked for before the choice; if item 8 shows that v5.1's LB_TRUNK and FASCICLE nodes carried no PMJs, or
    item 4 shows no LV septal junction above the D1 line in a heart, the step-0 report goes to Alex before step 1
    (15.2 step 0).
  - **Run at step 0, and D1 kept (deviation D12, 20 Oct 2026; step-0 card 4, "Keep", 20 Oct 2026 17:33:10 UTC).** Item 8:
    v5.1's LB_TRUNK and FASCICLE nodes carried no PMJ (0 on 125 / 82 / 105 nodes; 18 / 8 / 13 distal-network junctions
    share a mesh node with one of them), so for the sheet D1 partly restores v5.1. Item 4: the network part is not a
    no-op: 255 / 239 / 220 v5.1 LV junctions lie above the D1 line on the left septal surface (AHA 2, 3, 8 and 9) and are
    removed. The line lies 33.4 / 25.7 / 29.0 mm from the septal crest and crosses the His line 28.7 / 29.2 / 25.4 mm
    below the His exit, so junctions are allowed on 132 of 628, 35 of 603 and 128 of 579 mm2 of the sheet (21 / 6 /
    22 %), its lowest band (report 34 items 4, 8, 10 and 13). The step-0 report went to Alex before step 1, as this rule
    requires, and **D1 stands as written** (19.15.2).
  - **Evidence (human function first; dog anatomy beside).** Durrer 1970 p.899 (abstract), p.901 and p.906 (Results):
    "Septal activation started in the middle third ... somewhat anteriorly", then proceeded in an apical-basal
    direction; the three early areas rest on "the data obtained from four hearts" (p.901). Cassidy 1984 p.39 (human in vivo, n = 15): "The inferior border of the
    middle septum was the earliest area"; the group-mean map of Fig 5 (p.41, a reading of the figure) shows mid-septal
    breakthrough at 11 ms against 27-37 ms toward the basal septum. Upadhyay 2019 pp.6-8 and 12 (human in vivo, a
    catheter on the proximal septum in a basal-to-apical orientation): delta LV time -37 ms (IQR -50 to -27) in controls
    and -37 ms (-46 to -18) with intact Purkinje activation, against +45 ms (30-60) in complete block; the V shape is part
    of Upadhyay's definition of intact Purkinje activation (p.7), so only delta LV time is a measurement, and the
    patients were referred for devices or VT ablation, not healthy people. Myerburg 1972 (dog): p.227, "never identified
    conducting tissue in the subendocardium of the upper half of the septum which was activated immediately before the
    muscle"; p.237, the upper LV system is "functionally isolated"; pp.231 and 239-240 (islands of early activation on
    the high paraseptal free wall; Fig 12 legend p.233). Elizari 2017 p.7: septal fibres
    cover the inferior third; p.9, Fig 12 legend (Spach, 2-day human infant): the upper third of the left septal surface
    "devoid of conduction fibers". Modelling practice points the same way: Camps 2024 rule 2 (p.4) feeds the LV septal
    root nodes from the apical (ab < 0.4) part of the bundle.
  - **Counter-evidence, stated.** Massing 1976 p.614 and the Fig 17 legend (the distal left bundle with "no underlying
    collagen to isolate" it) are real anatomical grounds for coupling. Anatomy does not settle it; the human functional
    series above do.
  - **Tuning-shaped toward gate 1, and why it is adopted anyway (a departure from precedent).** D1 leans failing gate 1
    toward passing, so by 0.1 it is tuning-shaped, and that is said here. It is not tuning in origin: the trigger is the
    07:30 rule itself (assumption 30,
    added by the B1 build fix of the 20 Oct review, not chosen by Alex), an unsourced assumption that makes the upper
    left septum early, against Durrer, Cassidy and Upadhyay. **This departs from the A19 precedent** ("it moves failing
    gate 1 toward passing, so it stays an arm", also used to reject the 5 ms delay). The reason: A19 extrapolated one
    finding to the whole free wall, and the 5 ms delay set an unsourced value against a sourced default, while this
    region was observed directly in three independent human functional series, and the alternative is itself an
    unsourced assumption, so no neutral choice exists.
  - **Declared gate effect.** D1 moves failing gate 1 toward passing, of unknown size (the 9 Oct v3/v4 contrast, paced
    QRS 162 against 92 ms, shows that basal coverage is a strong gate-1 lever, though v4 also changed speeds), and
    post-lock card 1 stated that this makes gate 1 a calibration check for D1, so **gate 1 is a calibration check for
    D1** (11.5, clause (iii)); it moves failing gate 7(b) away from passing. Calibration checks for D1 (11.5): gate 1;
    and, inherited from the sheet because D1 sets where the sheet couples to muscle, gates 2, 5, 6 and 7 (the sheet's
    parts: (a), (b), (T) and the RV items). Not gates 3 and 8: they score no depth contrast, and D1 reaches them only by
    retrograde entry or through gate 8's network arm (its narrower gate-8 margin is movement), which is involvement,
    not aim; not 7(e), which is not one of the sheet's parts (deviation G, 20 Oct 2026). Report 29 is the direct human
    observable.
  - **Arm A39** keeps the 07:30 rule (no PMJ over the first 10 mm, one at every sheet node beyond it) together with the
    current v5.1 LV distal coverage of the upper septum (to z 0.9), so one arm holds the "early upper septum"
    hypothesis and the primary holds the "isolated upper septum" one.
- **The three outflows, fixed now (rewritten by deviation D11, 20 Oct 2026; step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC).**
  v5.1 has **three** LV fascicles, anterior, septal and posterior, each ending at one of the code's Durrer points
  (anterior z 0.80, septal z 0.50 in AHA 9, posterior z 0.33; report 34 item 1). Inside the envelope the sheet replaces
  them. **Beyond the envelope, each v5.1 fascicle path, from the point where it first leaves the envelope to its
  endpoint, is kept exactly as v5.1 built it**: its nodes, edges, v5.1 edge classes and speeds, and no PMJ, and the distal
  trees it feeds, apart from D1's junction mask, which applies to the distal network as before. Each kept path joins the
  sheet through its own v5.1 edge across the envelope's edge, from its exit node (its first node outside, report 34
  item 15) to the sheet node at the mesh node of its last node inside (the nearest sheet node if none shares it), with
  that edge's v5.1 class and speed (assumption 56); those joins, with the distal edges re-joined inside the envelope,
  carry the sheet's anterior, septal and posterior outflows toward the code's Durrer points (report 34 item 9:
  31.7-34.8 mm from D3's anterior paraseptal centre, 23.0-25.0 mm from its posterior paraseptal centre and 0-7.1 mm
  from its central centre). An endpoint inside the envelope (6G8DD8S5's anterior) is replaced by the sheet, and the
  distal trees it fed re-join the sheet (assumption 56). The **septal** outflow also attaches, as adopted, to the v5.1
  LV distal node **nearest the mid-septal point at 50 % of the sheet's base-to-apex extent**, which is where Massing's
  septal fibre groups run (p.620) and where Durrer's second early LV area sits (assumption 31, kept). The join is one
  edge from the sheet node nearest the mid-septal point (on the His line at 50 % of the sheet's 33 mm base-to-apex
  extent, 16.5 mm, derived: 0.5 x 33) to that distal node (at step 0, report 34 item 3: nodes 229026 / 981 / 39804, 2.3
  / 0.9 / 0.8 mm from the point), at 2.0 m/s, the sheet's speed beyond its first 10 mm (the fascicle speed); the edge
  carries no PMJ of its own, and each end node's PMJ follows D1 (deviation D11, 20 Oct 2026; assumption 31). The
  envelope is not widened, and no v5.1 node outside it is moved or reclassified. Source: Massing 1976 p.614 (human ex
  vivo, n = 10 non-neonatal hearts: the left bundle can be traced for 24-41 mm, after which the septum is "relatively
  diffusely covered by Purkinje fibers") and p.618 (0 of 13 hearts, nor Tawara's 2, bifascicular without major
  interconnections; the three outflows are this lock's reading, with p.620 and Demoulin 1972 p.807); Demoulin 1972
  pp.808-809 (human ex vivo, 20 control hearts: peripheral anastomoses in all 20); Durrer 1970 pp.899 and 901 (human;
  the early areas from 4 hearts). The sheet is Massing's; beyond it, the conduction toward the code's Durrer points
  stays the route v5.1 already built (19.15.1). Gate effect and calibration (D11): "?" on gates 1, 2, 3, 5, 6, 7 and 9
  and "0" on gates 4 and 8 (section 14); the sheet's labels, gates 2, 5, 6 and 7 ((a), (T), (b) and the RV items), not
  gates 1, 3, 8 or 9 (11.5, 14).
  - **Measured before D11 was written in (report 34 item 15; read-only, relayed 20 Oct 2026 17:34 UTC).** Each path
    first leaves the envelope: anterior at s 7.5 mm, a +15.9 mm in Y5HYEDL4 (2.6 mm kept beyond), never in 6G8DD8S5
    (endpoint inside), at s 10.0, a +15.2 mm in 7D98EVAR (7.1 mm beyond); septal past the sheet end at
    s 34.7 / 33.9 / 33.5 mm (6.0 / 0.8 / 1.4 mm beyond); posterior at s 32.8 / 32.1 / 33.5 mm (24.7 / 14.7 / 16.0 mm
    beyond); none re-enters. 40 / 18 / 30 tail nodes are kept and 0 / 2 / 0 distal edges re-joined; DISTAL edges meet
    trunk or fascicle nodes only at the three fascicle endpoints; 0 / 0 / 0 LV distal nodes are unreachable from the
    His.
  - **Acceptance at step 2g (D11).** Every v5.1 LV distal-network node is reachable from the His through the sheet, as in
    v5.1 (6G8DD8S5 checked before its cut; after the cut, 7.8 applies); the kept fascicle paths are identical to v5.1's
    from the exit node to the endpoint, with each join edge as assumption 56 states; per heart, the exit node, the kept
    length and the join edge (its two nodes, class and length) of each fascicle path and the number of distal edges
    re-joined to the sheet are reported (report 34 item 15). If any LV distal node is unreachable, stop and report; no
    edge is added to reach it.
  - **Superseded by D11 (the 13:51 text, kept as history).** "Anterior and posterior attach to the two v5.1 fascicle
    endpoints (anterior to the v5.1 anterior endpoint, posterior to the v5.1 posterior endpoint, each identified by its
    own v5.1 class label). The septal outflow has no v5.1 counterpart; it attaches to the v5.1 LV distal node nearest
    the mid-septal point at 50 % of the sheet's base-to-apex extent ... Recorded as a model assumption; no source gives
    a septal endpoint position." Step 0 found the posterior endpoint outside the envelope in all three hearts and the
    anterior one in two, and v5.1 does have a septal fascicle, ending at z 0.50 (19.15.1).
- **Arms.** A17 origin width 1 mm (the right-sided His phenotype: 5 of 32 hearts, 15.6 %, the stem at most 1.5 mm in
  cross-section, widening abruptly on reaching the left septum; Massing 1976 pp.611-612). A18 origin width 14 mm
  (Massing's observed maximum). In A17 and A18 the D11 rule is applied to that arm's own envelope (its origin width,
  widening by assumption 10 to 22.6 mm at 12.5 mm, with the same 17.8 / 4.8 split, 0.79 / 0.21 of the width at every
  level, assumption 9): each v5.1 fascicle path is kept from its first node outside that envelope, with the join edge
  and the distal-edge joins of assumption 56; the exit nodes, kept lengths and re-joined distal edges are reported with
  the arm; if any v5.1 LV distal-network node is then unreachable from the His, the arm is recorded "not run" with the
  reason and no edge is added (deviation D11, 20 Oct 2026; 15.2 step 8a).
- **Consequence for the gates.** This change sets the LV septal subendocardial conduction system. It is aimed at
  earliest LV endocardial activation in the His-driven beat, which gate 7 measures ((a), (T) and (b), and the RV items,
  which are timed after LV onset), and at the subendocardial conduction that a 10 % LV stimulus engages, which is what
  the 90 %/10 % depth contrast of gates 2, 5 and 6 measures. So **gates 2, 5, 6 and 7 are calibration checks** for it
  (11.5, limb (ii), with its depth-contrast reading). **Gates 1, 3 and 8 are not**: they score no depth contrast; every
  paced beat enters the sheet retrogradely, and gate 8's network arm contains it, but for these gates that is
  involvement in the activation, not aim; the sheet is aimed neither at the paced summit and cusp QRS, the Daniels
  order or the network-against-no-network comparison nor at their definitions or sites (section 11, 11.5; deviation G,
  20 Oct 2026). The 07:30 section 11 gate-3 cell named the sheet; that label is withdrawn under post-lock card 3 for
  this reason (19.11).
  Gate 9 is not either: both engines replay the same network's junction times (one-way, 11.4 item 5), so gate 9
  compares the engines on the same activation and scores no fit of the sheet to data. The change is driven by four
  independent human sources, not by the gates.
- Reported beside it: in 5 of 13 hearts the left-bundle distribution was a close anatomical fit to Durrer's three sites
  of earliest LV endocardial activation (Massing 1976 p.620); 15 of 60 human hearts had no identifiable compact ribbon at
  all, the fibres fanning straight out of the branching His bundle (Elizari 2017 p.5); 2 of 60 had an intramural left
  bundle re-emerging about 15 mm below the top of the septum (Elizari 2017 p.6).

### 7.2 Right bundle

- On the septum, as v5.1: the RB runs under 1 mm wide, 0.5-1 mm below the right septal endocardium, and **unbranched
  throughout the IV septum in all 32 hearts** (Massing 1976 p.615: "In all 32 hearts the RBB remained a narrow (less
  than one millimeter in size), unbranched ... structure throughout the IV septum"); the 07:30 text's "29 of 32" refers
  to its course near the endocardium, not to branching (correction, 20 Oct 2026). It then becomes the distal network.
- Its course is predictable and its origin invariant, unlike the left bundle (Elizari 2017 p.6).
- **Primary: v5.1's right bundle, unchanged, its moderator-band edge included (deviation D16, 20 Oct 2026;
  step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC).** v5.1's RB runs down the RV septum to the moderator band's septal
  insertion (z 0.351 / 0.349 / 0.353) and then crosses the cavity as one straight edge of class RB at 1.5 m/s, with no
  PMJ, to the anterior RV free wall, where the v5.1 RV distal network starts: 14.7 / 18.2 / 10.1 mm, against Lee and
  Hur's mean 13.6 mm (report 34 items 6 and 12). Its septal insertion lies at 0.82 / 0.63 / 0.82 of the RV septum from
  crest to apex (lower, middle and lower third; Lee and Hur: middle of the septum in 25 of 36). D2's anatomy (the RB
  along the moderator band to the anterior RV free wall, no PMJ on its free-running part) is therefore what v5.1
  already has, and **no chain is built**: the choice on post-lock card 2, change 2, stands in substance. The mesh
  carries no papillary muscle and no anterior RV free-wall label (report 34 item 5), so assumption 47's end node could
  only have been a construction: assumption 47 is withdrawn, and assumption 54's 37.8 mm is reported against v5.1's
  band (all three within it) rather than used as a stop. Sources as for D2 (Stephenson 2017 p.4; Lee and Hur 2019;
  Massing 1976 p.615; below). Not tuning: a correction of a premise, and nothing is built.
  - **Arm A20 (redefined by D16).** The RB on the septum only, the counterfactual the 13:51 text meant: v5.1's band edge
    is removed and the RB ends at the band's septal insertion, which joins the nearest v5.1 RV distal-network node with
    a PMJ (7.3 delays; assumption 58); if any RV distal node is then unreachable from the His, A20 is recorded "not
    run" with the reason, and no edge is added (13).
  - **Gate effect and calibration (D16).** None against v5.1, since nothing changes, so the right bundle makes no gate a
    calibration check (as the retrograde 2 ms row of 11.5). D2's 13:51 signs (7(c) earlier and possibly below 20 ms,
    RV onset earlier, gate 1 "0 or -", gate 8 "0 or +") and its gate-7 label ((c) and the RV items) are withdrawn,
    because nothing they named is built (11.5, 14).
- **Superseded by D16: D2 as written at 13:51 (kept as history; not built).** The 13:51 primary read "Primary: the RB
  continues along the moderator band (deviation D2, 20 Oct 2026; post-lock card 2, change 2, "Adopt all", 20 Oct 2026
  11:23:21 UTC). The septal-only course of the 07:30 lock becomes arm A20 (swapped)." Step 0 showed that v5.1's RB is
  not septal-only (19.15.6). Of the items below, the build rule and the plausibility stop are not live rules, the
  sources stand for D16, the gate effect and calibration are replaced by D16's (above), and the Camps quotation stands.
  - **Build rule (13:51; superseded by D16, not built).** A Purkinje chain at 1 mm node spacing and 1.5 m/s (the v5.1 RB speed), with **no PMJ on
    its free-running segment**, from the v5.1 RB end (the moderator band's septal insertion) to **one anterior RV
    free-wall endocardial node** fixed by rule: the anterior papillary-muscle base if the mesh carries one; otherwise the
    nearest node carrying the anterior RV free-wall label within z +- 0.05 of the insertion (assumption 47; the
    anterior constraint stops the nearest free-wall node at the same z from being an inferior one). The end node joins
    the nearest v5.1 RV distal-network node and carries a PMJ with the delays of 7.3. A graph network can carry a
    cavity-crossing edge, so the chain is buildable. The chain length is reported per heart against Lee and Hur's
    mean 13.6 mm (by type 18.9, 15.0 and 12.7 mm) (report 34 items 6 and 12). The source's type means do not reproduce
    its overall mean: weighted by n they give about 14.9 mm (derived: (7 x 18.9 + 15 x 15.0 + 14 x 12.7) / 36 = 14.86),
    and type 3's two subtypes give 13.2 mm, not 12.7 (derived: (11 x 14.4 + 3 x 9.0) / 14 = 13.24); recorded, not
    corrected. The insertion's level on the septum is reported against Lee and Hur's origins (middle of the septum 25
    of 36, upper third 13.9 %, lower third 11.1 %, top fifth 5.6 %) (report 34 item 12).
  - **Plausibility stop (13:51, assumption 54; under D16 a report only: v5.1's band, 14.7 / 18.2 / 10.1 mm, lies within
    it in all three hearts).** If a heart's chain is longer than **37.8 mm** (twice the longest
    type mean, 18.9 mm; derived: 2 x 18.9), the build stops at step 2g and reports before any beat; no node is moved to
    fit. The insertion level is reported, not a stop: Lee and Hur's origins range from the supraventricular crest to the
    apex, and 11 of 36 lie outside the middle of the septum.
  - **Sources.** Stephenson 2017 p.4 (human, whole-heart micro-CT, n = 1): the RB "descended the septum running on the
    superficial and deep surfaces of a major free-running trabeculation". Lee and Hur 2019 (Anat Cell Biol 52:38-42;
    38 formalin-fixed human hearts, donors 38-90 y; full text read as Europe PMC XML, which prints no page numbers):
    moderator band in 36 of 38 hearts, mean length 13.6 mm and thickness 4.6 mm, originating most often from the middle
    of the septum (25 of 36, 69.4 %). Massing p.615 supports it only implicitly ("We did not follow it into the
    moderator band"). Not support for a mid-septal crossing, and not cited as such: Myerburg 1972 Fig 1 legend (dog: the
    RB runs down the septum to the base of the anterior papillary muscle, and only then becomes a free-running false
    tendon) and De Almeida 2020 (human, n = 3, abstract only: conducting cells from the anterior papillary-muscle base to
    the supraventricular crest and subpulmonary infundibulum).
  - **Why it is not tuning.** The case rests on anatomy. The v5.1 RV onset mismatch (first RV endocardium 19.3 ms after
    LV onset in the control heart, REPORT.md Table C, against Durrer's 5-10 ms) is **not** a reason for the change, since
    choosing a structure to fix a reported mismatch would be comparator-driven; an earlier RV onset is recorded only as a
    likely consequence. No failing gate is predictably helped.
  - **Gate effect and calibration (13:51; withdrawn by D16, above).** Gate 7(c), which passes now (27.5 ms in 20-31 ms), could fall below 20 ms; RV onset
    (report 14) moves earlier; gate 3's RVOT value and gate 4 move either way. Calibration check for D2 (11.5): **gate 7
    ((c) and the RV items)**, because D2 is aimed at the RV activation sequence they measure, with report 14 beside it.
    **Not gate 4:** Bazan 2006 scores the RV depth effect, the 90 % against 10 % paced QRS difference at RV sites, so
    under the depth-contrast reading of 11.5 a change aimed at the RV subendocardial conduction that a 10 % RV stimulus
    engages would be aimed at it. D2 is not such a change: it is a free-running bundle with no PMJ on its free-running
    segment, aimed at the RB's course in the His-driven beat, and it leaves the RV subendocardial network, its junctions
    and its coupling as in v5.1 apart from the one PMJ at its end node; nor is it aimed at transmural RV conduction or at
    the sites or the definition gate 4 is scored on.
    **Not gate 3:** the Daniels order is scored on paced summit, vein, aortic-sinus,
    RVOT and LV endocardial sites, and D2 touches neither those sites, their anatomy nor the MDI rule. **Not gates 1 and
    8**, as for the sheet. D2 reaches gates 1, 3, 4 and 8 only through the network that paced beats enter retrogradely,
    which is involvement, not aim (deviation G, 20 Oct 2026).
  - **Camps 2024, quoted exactly (correction, 20 Oct 2026).** Their Discussion says the endocardial-surface approach
    "limited the ability to represent the moderator bands and false tendons not bound to the endocardial surfaces" and
    "can be easily extended to incorporate these new structures (Barber et al., 2021)". The 07:30 text's "cannot
    represent free tendons at all" overstated it.

### 7.3 Purkinje-to-muscle junction delays

- **Antegrade 4 ms (primary).** Source: Myerburg 1972 p.241, canine ex vivo isolated endocardial preparation: intervals
  between terminal Purkinje fibres and ventricular muscle "not exceeding 4 msec and quite frequently less than 2 msec"
  **at sites of impulse egress**. Every modelled PMJ is by construction an egress site, which is why the egress-site
  value and not the whole-preparation value is used. No human PMJ delay exists in any paper read; the value is canine.
- **5 ms is rejected.** It is not a measurement of an egress site, and it would help failing gate 1, so adopting it would
  be indistinguishable from tuning. Recorded explicitly.
- **Arm A21: 7 ms antegrade**, Wiedmann 1996's measured canine control mean (in vitro superfused LV papillary muscle;
  all dispersions below are **mean +- SE**, as Wiedmann's Table 1 and Table 3 legends state;
  groups 6.5 +- 0.7, n = 10; 8.6 +- 0.9, n = 6; 6.9 +- 0.53, n = 8; 6.7 +- 0.90, n = 5; my pool of all 29 control values
  across Tables 1 and 3: mean 7.06, median 6.8, SD 2.07, range 4.1-11.3 ms). Reported against Camps 2024's calibration
  target of a 3-25 ms antegrade delay, noting that Camps attributes that range to Wiedmann while Wiedmann's own text
  quotes the literature as 5-25 ms.
- **Retrograde 2 ms (primary; v5.1's value, bit-identical).** Alex, 20 Oct 07:22:39 UTC, card "Return the backward
  junction delay to v5.1's sourced 2 ms?": "2 ms (v5.1)". This reverses the 4 ms of the 05:15:17 UTC list and is logged
  as a dated deviation (PROGRESS.md, LABNOTES).
  - **Source.** Vergara 2016 p.223: "an orthodromic delay do of about 5-15 ms and an antidromic delay da of about
    2-3 ms" (citing Palamara et al.), and their model uses do = 5.0 and da = 2.0 ms. This is a cited modelling range, not
    a human measurement; no human PMJ delay in either direction exists in any paper read. The literature puts the
    antidromic delay **below** the orthodromic one, consistent with the higher muscle-to-Purkinje safety factor.
    Wiedmann 1996 and Myerburg 1972 do not cover this direction.
  - **Why the 4 ms was reversed.** It was proposed on 19 Oct on the premise that "the 2 ms has no source", which is
    false (above). It also has a gate effect: under the retrograde rule below every paced (non-His) beat starts in muscle
    and enters the network retrogradely (in v3 a paced LV free-wall site reached its first junction at 0.6-3 ms), so an
    extra 2 ms would delay network engagement in all 432 paced beats, lengthen paced QRS and move failing gate 1 toward
    passing, and move MDI through network timing (project J1 test: junction delays moved cusp MDI 0.579 to 0.478 and
    summit+cusp QRS 161.5 to 165 ms).
  - **Gate effect of the primary:** none against v5.1 (the value is unchanged), so this delay makes no gate a
    calibration check.
  - **Arm A22: 4 ms, "equal to antegrade, helps gate 1"** (no source for the retrograde direction).
- **Retrograde rule, documented (a priori).** A graph eikonal solver cannot discover which junctions conduct backwards,
  so the rule is fixed here: every PMJ is bidirectional; a junction conducts retrogradely when its muscle node activates
  before its Purkinje node by more than the retrograde delay; the Purkinje node then takes (muscle time + 2 ms, the retrograde delay) if that
  is earlier than its own antegrade arrival. The solution is taken as the earliest time at every node, computed by one
  shortest-path pass over the combined graph, so no junction is labelled by hand and no two-front problem is solved.
  The number of retrogradely entered junctions is reported per beat.
- Spread recorded, not modelled: within one canine papillary muscle the junction delay ran from 2 ms at the base to 17 ms
  at the apical site with the electrodes within 0.5 mm (Myerburg 1972 Fig 9 legend), and upper papillary preparations
  gave delays over 50 ms and up to 150 ms with the mechanism unresolved (p.230). No junction-density or
  junction-delay gradient is built: there are no human counts or positions, and the 1 mm meshes cannot carry them
  (limitation, with a 10 ms bound stated on gate 1).

### 7.4 Purkinje speeds, kept and reported

- His / RB / LB trunk 1.5 m/s; fascicles and distal network 2.0 m/s (v5.1 values, unchanged).
- Reported, not changed: Camps 2024 p.4 treats 2.0-4.0 m/s as the human Purkinje bounds, so the trunk value sits below
  their lower bound, while the distal network's per-edge speeds, 3.00 / 2.88 / 2.84 m/s per heart (v5.1 REPORT.md
  Table C, set so that the straight-line speed is 2.00 m/s), sit inside their 2.0-4.0 m/s path speeds (correction,
  20 Oct 2026: the 07:30 text said "exactly on it"); Wiedmann 1996 Table 2 measured 1.5 +- 0.08 m/s (n = 12) in a
  canine papillary-muscle subendocardial Purkinje layer, which supports 1.5 m/s for a layer but not for a bundle trunk.
  Lowering the trunk speed would lengthen QRS and move failing gate 1 toward passing, so no change is made; on gate 7 (T)
  and (b), which are timed from LV onset, it is near-neutral to away, not toward passing (correction, 20 Oct 2026).

### 7.5 No Purkinje network in the outflow tracts (kept, now sourced)

Elizari 2017 p.9 (Fig 13 legend), Indian-ink injection in a **sheep** heart: while the inflow tract of the left ventricle
is plentiful of Purkinje fibres, the outflow tract is totally deprived of them, and the same holds for the right outflow
tract. Species labelled. Stephenson's human micro-CT neither contradicts nor confirms it, because its Purkinje networks
are explicitly incomplete. Noted: an outflow tract without Purkinje is part of why gate 1's paced QRS is narrow, and this
source predates and is independent of that gate.

### 7.6 Intramural Purkinje: not modelled

Primary: subendocardial Purkinje only. No intramural geometry arm is opened, because building one would mean inventing
connectivity.
- Report the unresolved human-on-human conflict: Hillestad 2025 (MYL4 immunofluorescence, n = 3 human donors for the
  quantification, the authors' own stated limitation) finds over 60 % of myocardial Purkinje content intramural (derived
  from its segment figures: 4.5 % at 100-199 um plus 59.3 % beyond 199 um = 63.8 %, or 76.6 % counting everything below
  the subendocardial layer), with regional shares LV free wall 47.1 %, septum 36 %, RV free wall 13.4 %, papillary
  muscles 3.5 %; Stephenson 2017 p.8 (intact-heart iodine micro-CT at 73 um isotropic, n = 1) found no evidence of
  intramural Purkinje fibres.
- State the likely reconciliation (73 um voxels cannot resolve single transmurally intercalated cells) and that
  Hillestad's depth bins put 59.3 % of the content in a single ">199 um" bin spanning 0.2 mm to the epicardium, with no
  connectivity, paths, junction density or velocity reported.
- Note for the two HF hearts: MYL4 reactivation is reported in certain congenital and hypertrophic cardiomyopathies, so
  the marker's specificity in disease is not guaranteed (Hillestad 2025 p.1732).

### 7.7 Junction coverage (arm only)

Arm A19: LV free-wall junctions only from 50-67 % of the base-to-apex length. Source: Massing 1976 p.620, in all 13
hearts the **posterior** fibres reached the posterior LV wall only after running half to two thirds of the way from base
to apex, and no heart had posterior fibres distributed to the basal third; **anterior** fibres reached the basal third in
only 2 of 13 (with 3 more at the basal-middle junction), which is on **pp.612-613**, not p.620 (p.620 reports a different
count, "in five of our 13 ... one or more anterior LBB subdivisions ... toward the basal third", for subdivisions rather
than distribution). **Labelled: the arm extrapolates a posterior-fibre finding to the whole LV free wall**, which
Massing does not do. Spach's iodine-stained 2-day infant heart (via Elizari 2017 Fig 12 legend) had no conduction fibres over the upper
third of the left septal surface.
**It stays an arm and is not promoted.** The evidence is narrower than the 07:30 text said ("the evidence is strong"):
Massing's anatomical studies "do not include the anterior and posterior paraseptal free walls" (p.620), and the free
walls were removed from every specimen (p.610), so the arm is the extrapolation labelled above. Delaying basal LV
activation lengthens QRS and moves failing gate 1 toward passing, so adopting it in the same lock as that gate would be
indistinguishable from tuning; it moves failing gate 7 (T) and (b) **away** from passing, not toward (correction,
20 Oct 2026). This is recorded as the reason.

**Sub-variant A19b (deviation D10, 20 Oct 2026; post-lock card 2, change 10, "Adopt all", 20 Oct 2026 11:23:21 UTC).** A19b is **the primary with no
LV distal-network junctions in AHA segments 4 and 5** (the basal inferior and basal inferolateral free wall); A19's
50-67 % rule is not applied. Functional support (human): Durrer 1970 p.906 (the front is "nearly
completely closed ... after 30 msec, except at the posterobasal area", which is reached last) and Cassidy 1984
pp.39-40 (the base of the inferior posterior wall "consistently the last area"). The evidence for **zero** junctions
there is weak: Massing p.620 did not study the free walls and p.610 removed them; Cassidy p.40 offers "Purkinje fibers
are less dense at the base" only as one possible explanation; Camps 2024 pp.2-3 makes the base sparse, not
junction-free; Sebastian 2013's basal sparsity comes from hard-coded rules. **Labelled tuning-shaped toward gate 1:**
superior paced sites end in the inferobasal LV, so A19b likely lengthens summit and cusp paced QRS (toward failing
gate 1 passing) and moves 7(T) away. Never promoted.

### 7.8 Heart 6G8DD8S5: the LBBB cut

- **Primary, with the removed set named exactly (the 19 Oct wording "the sheet and its connections proximal to the same
  cut level" was ambiguous, because the sheet starts at the His exit, so "proximal" could mean none of it or all of it).**
  The cut removes **only the edge or edges that connect the His node to the sheet's origin node**, at the same level as
  v5.1's cut (just below the His). **The whole sheet, all its nodes, all its internal edges and all its PMJs are kept**,
  and so are the v5.1 LV distal network and the v5.1 fascicle paths kept beyond the envelope (deviation D11,
  20 Oct 2026). This is the reading that reproduces v5.1's cut, which is complete left
  intra-Hisian block with the LV tree intact for backward entry (scorecard: 0 of 2,965 LV Purkinje nodes reachable from
  the His, tree intact).
- **Acceptance, checked and recorded per heart:** 0 LV Purkinje or sheet nodes reachable from the His node by any
  antegrade path; the sheet still one connected component; the removed edge list written into LABNOTES.
- The 6G cut is a change in its own right. Because the sheet now carries the retrograde surface that the LV wavefront
  enters, the cut gets its own prediction row, **G2 "?" and G6 "?"** (section 14). It is named in the gate-2 and
  gate-6 calibration entries (11.5, limb (ii)) for a different reason: it defines the conduction state of the LBBB-like
  heart (complete left intra-Hisian block with the sheet kept), the substrate in which gate 6 is scored and 6G's gate-2
  pairs are paced. The retrograde surface is the reason for the prediction row, not for the label (deviation G,
  20 Oct 2026).
- Retrograde entry into the LV network stays primary, with direct human support: in complete conduction block the distal
  Purkinje is not silent but late, with latent Purkinje potentials activated after local ventricular septal activation
  (Upadhyay 2019 p.15), and in one patient converting between conducted and blocked beats the same potentials move from
  presystolic to post-ventricular.
- Arms: A23 no retrograde entry (Upadhyay 2019); A24 tissue slowed to 0.3 m/s in the blocked ventricle, labelled tuning
  (Gillette 2022); A25 slower transseptal conduction in LBBB with HF (Strik 2013, dog: transseptal crossing 44 +- 16 ms
  in acute LBBB and 67 +- 9 ms in LBBB with HF during LV septal pacing, against about 30 ms transmural LV free-wall
  conduction; with the paper's M-mode septal thicknesses of 1.31 +- 0.09 and 0.86 +- 0.12 cm that is an apparent
  septum-crossing speed of about 0.30 and 0.13 m/s, derived, assuming path length equals wall thickness). All three stay
  arms; A25 would move gates 2 and 6, and cannot move gate 7, which is scored on the control heart only (correction,
  20 Oct 2026: the 07:30 text said gates 2 and 7).
- Recorded in the model description: which of Upadhyay's two complete-block levels the cut represents (left intra-hisian,
  72 % of complete block and 45.8 % of all surface-LBBB patients, derived; or left-bundle level, 28 % and 18.1 %).
- Recorded: a graph eikonal model with fixed anisotropy cannot produce a rate- and site-dependent functional line of
  block, so it will reproduce Derval's homogeneous centrifugal picture by construction and gets no credit for matching
  it, while Auricchio 2004 saw a U-shaped wavefront with a functional line of block in 23 of 24 patients.

## 8. Outflow-tract anatomy

The cusp-muscle card was answered "Both" (20 Oct 05:18:46 UTC), so **both structures are built**. The outflow tracts are the model's largest realism gap: the
CT meshes fuse the free-standing infundibulum to the aortic root, the summit sites sit on a guessed anchor, and the cusps
have almost no muscle. Both new structures are the tissue the comparator studies actually ablate, so pace-mapping cusp
and RVOT sites without them means stimulating tissue that is not there. The decision is anatomy-driven; it is likely to
move failing gates 1 and 3. Both structures are new muscle at the outflow sites, so gates 1, 3 and 8 are calibration
checks for the crescents and gate 3 for the sleeves, by what the structures are aimed at and not by the expected
movement (11.5; deviation G, 20 Oct 2026), and **neither structure may be resized after a result is seen**.

### 8.1 RVOT labels (report only)

Label each RVOT site as septal component or free-standing infundibulum by the rule of 8.2 (deviation D14, 20 Oct 2026,
which supersedes D6): the septal component is the part of the posterior wall up to **47.2 % of the mesh's own
posterior span above the 0 % landmark** (derived: 12.7 / 26.9 = 0.472, the ratio of Jakiel 2025's mean septal
component maximum height, 12.7 +- 4.8 mm, to his mean posterior RVOT wall, 26.9 +- 6.5 mm, Table 1, 220 human hearts;
assumption 57). D6's rule (the 13:51 text: the part of the posterior wall up to 12.7 mm above the 0 % landmark,
superseded) and the 07:30 label rule, the lowest 37.3 % of the posterior wall, are reported beside it. Map the model sites onto Zheng's RVOT labels so the Zheng comparison is
like-for-like. Report only; it changes no value.

### 8.2 The infundibulum cut

- Where the mesh fuses the free-standing infundibulum to the aortic root or to the LV, split the shared nodes and cut the
  graph edges across the interface (an insulating plane). **The septal component stays fused.**
- **Where the cut plane is, in mesh landmarks (deviation D6, 20 Oct 2026; post-lock card 2, change 6, "Adopt all", 20 Oct 2026 11:23:21 UTC).** The interface is the
  **tag-1 (LV) to tag-2 (RV) element interface** above the septal component. The two landmarks of the **posterior RVOT
  wall** on the mesh are fixed here: **0 % = the lowest point of the pulmonary-valve-plane ring's posterior aspect
  (on the mesh, the pulmonary mid-plane ring, deviation D13, 20 Oct 2026) projected onto the RVOT wall at the
  tricuspid-annulus level** (the inferior end of the posterior wall), **relabelled as the mesh proxy for Jakiel's RVOT
  base** (the horizontal plane through the lowest point of the supraventricular crest, which runs along the superior
  tricuspid annulus); and **100 % = the pulmonary valve plane ring itself** (the superior end; on the mesh, the
  pulmonary **mid-plane ring**, deviation D13, 20 Oct 2026), measured along the surface in the long-axis
  direction. **The septal component's upper limit is 47.2 % of the mesh's own posterior span above the 0 % landmark
  (deviation D14, 20 Oct 2026; step-0 card 3, "Scale to span", 20 Oct 2026 17:32:47 UTC; assumption 57)** (derived:
  12.7 / 26.9 = 0.472, the ratio of Jakiel 2025's mean septal component maximum height, from the RVOT base to the
  subpulmonary infundibulum boundary, 12.7 +- 4.8 mm, to his mean posterior RVOT wall, 26.9 +- 6.5 mm, Table 1, 220
  human hearts, measured along the middle of the wall): **6.4 / 4.8 / 6.5 mm** at the step-0 spans of 13.6 / 10.2
  / 13.7 mm (derived: 0.472 x 13.6, 0.472 x 10.2 and 0.472 x 13.7, to 0.1 mm; the step-0 spans run to the PC's
  "pulmonary ring", its level within the disc's wall contact not stated), recomputed from the span measured at step 2b
  on the first reading of report 35 (f) (as defined there). Below that height the tag-1/tag-2 interface stays fused;
  above it, it is split. **Superseded by D14 (D6's 13:51 rule, kept as history and reported beside at step 2b):** "The
  septal component's upper limit is 12.7 mm above the 0 % landmark (Jakiel 2025 Table 1: septal component maximum
  height, from the RVOT base to the subpulmonary infundibulum boundary, 12.7 +- 4.8 mm, 220 human hearts, measured
  along the middle of the wall)."
  - **Why a proportion of the mesh span (deviation D14).** The step-0 posterior RVOT wall is 13.6 / 10.2 / 13.7 mm
    (second reading 12.8 / - / 13.1 mm) against Jakiel's 26.9 +- 6.5 mm (Table 1, 220 human hearts), 2.0-2.6 SD short in
    all three hearts (derived: (13.6 - 26.9) / 6.5 = -2.05; (10.2 - 26.9) / 6.5 = -2.57; (13.7 - 26.9) / 6.5 = -2.03;
    report 35 (f)). D6's 12.7 mm would fall at 93 % of the span in Y5HYEDL4 and 7D98EVAR and beyond the ring in
    6G8DD8S5, so the free-standing infundibulum would be split from the LV over only 0.9 / 0 / 1.0 mm of the posterior
    wall (derived: 13.6 - 12.7; none; 13.7 - 12.7), against Jakiel's posterior infundibulum height of 15.3 mm (Table 1).
    D6's reason (below) treats the mesh span as an anatomical span; three meshes 2.0-2.6 SD short, the control heart
    included, point to how the mesh's outflow landmarks were built (6 mm valve discs, report 35; the pipeline's valve
    cuts) rather than to three anatomically short outflow tracts (inference). The proportion maps Jakiel's mean anatomy
    onto each mesh's own landmarks, as the model places its other sites in normalised coordinates (UVC). It is chosen
    from the span, before any beat, not from contact area or gates.
  - **Why 12.7 mm and not the 07:30 rule's 37.3 % (D6's 13:51 reasoning; superseded by D14, kept as history).**
    Jakiel's Methods never define the 37.3 % share (it appears only in
    the abstract and the Results text), and the paper's own heights do not reproduce it (derived: 12.7 / 26.9 = 47 % from
    the maximum heights; about 43 % from mid-wall heights). The septal height is nearly independent of the posterior
    RVOT height (Table 2: r = 0.199), while the posterior infundibulum tracks it (r = 0.745), so a fixed height from the
    base leaves the heart-to-heart variation in the free-standing part, as the data do. **15.3 mm measured down from the
    ring** (the posterior infundibulum height) **is not used**: it would push that variation into the fused septal part,
    against Table 2. Derived: on a 26.9 mm posterior wall 37.3 % is 10.0 mm, 2.7 mm below the 12.7 mm rule; at an
    illustrative 24-27 mm span the 12.7 mm rule sits about 2.6-3.7 mm above the 37.3 % rule (derived:
    12.7 - 0.373 x 24 = 3.75; 12.7 - 0.373 x 27 = 2.63), and over Jakiel's mean +- SD posterior span (20.4-33.4 mm;
    derived: 26.9 +- 6.5 mm, Table 1, 220 human hearts) 0.2-5.1 mm above it (derived: 12.7 - 0.373 x 33.4 = 0.24;
    12.7 - 0.373 x 20.4 = 5.09). **The 24-27 mm span is a post-lock review estimate, not a mesh measurement and not a
    Jakiel value**: the outflow verifier wrote "at a 24-27 mm span the rules differ by 1-3 mm" without a derivation
    (notadopted-review-2026-10-20.json, infundibulum-cut item). Its ends lie near the reviewer's derived 24.4 mm, the
    span at which the 37.3 % rule and the 15.3 mm-below-the-ring rule agree (derived: 15.3 / (1 - 0.373) = 24.4), and
    Jakiel's mean posterior RVOT wall, 26.9 mm (Table 1, 220 human hearts); that reading is an inference. Each mesh's own
    posterior span, and so the actual gap between the two rules on it, comes from the step-2b report (report 35 (f)).
    Chosen by source, not by contact area or gates.
  - **Reported at step 2b (report 35 (f)):** the D14 boundary (47.2 % of the span) and, beside it, the three candidate
    boundaries (37.3 % of the span; D6's 12.7 mm above the 0 % landmark; 15.3 mm below the ring), each with the
    tag-1/tag-2 area above it (reported, not used; deviation D14), and the mesh's posterior span against Jakiel's
    26.9 +- 6.5 mm.
  - **Fixation note.** Jakiel's hearts were fixed in formalin for about 2 months, which shrinks absolute millimetres, by
    about one element at most (inference). Not corrected.
- **Per engine, because an insulating crack means different things in different solvers (fixed now):**
  - graph eikonal: every edge crossing the plane is removed, **at every stencil radius** (2-ring and the 3-ring fallback
    of R4.2, edges up to 5.25 mm), so no edge jumps the crack;
  - monodomain and RE+: the nodes are **duplicated** (split) across the plane, so no current crosses;
  - **lead fields and the ECG forward problem: the conductor stays continuous.** A split node set in a volume conductor
    would put an insulating crack into the torso solution, which is not what the anatomy says: the two walls are
    apposed, not separated. The forward mesh therefore keeps its original connectivity with myocardial conductivity on
    both sides.
- The PC reports the contact area before cutting, **and again after steps 2c and 2d**, because the RCC sinus wall is
  contiguous with the posterior RVOT infundibulum in 603 of 603 hearts (Gami 2011), so new crescent muscle can re-bridge
  the cut. The acceptance "no node and no graph edge crosses the plane" is re-checked at the end of step 2, not only at
  2b.
- **Connectivity acceptance.** After the cut and after the new muscle, every excitable component must be reachable from
  at least one stimulus site or network node, and the component list is recorded. This is what stops step 7's "no
  unactivated node" check from failing silently.
- Sources: Gami 2011 (J Interv Card Electrophysiol 30:5-15) pp.9-10, the right coronary cusp wall of the aorta was
  immediately subjacent and contiguous with the
  posterior wall of the RVOT infundibulum in 603 of 603 autopsy hearts (100 %); Acosta 2015, no epicardial connections
  were found between RVOT and LVOT, the only continuity being subendocardial across the infundibular septum. So the two
  must be geometrically adjacent and electrically separate.
- Companion fact recorded for fix 3: the posterior aortic wall at the non-coronary cusp was contiguous with the
  interatrial septum in 603 of 603, which is the anatomical basis for the atrial muscle and atrial blood assignment near
  that sinus.
- This was found while auditing the Daniels fail, so **gate 3 is a calibration check for the cut** (11.5).
  Unconditionally: the label does not depend on whether the gate moves or passes, because a label decided after the
  result is seen is not a pre-registration. The 19 Oct "if it moves" and the adopted list's "if it passes" are both
  withdrawn.
- **Stop rule.** If the contact area is zero, or the interface cannot be identified on a heart, stop and report before
  any further geometry step; do not guess a plane.

### 8.3 LV summit re-anchor (Kuniewicz 2023)

- **What changes against v5.1 is only how the anchor point is found.** v5.1 already used Kuniewicz's 9.6 mm and 18.9 mm,
  but from a guessed "left sinus" point (the most left-posterior annulus point; pilot-grid-v4 note). The meshes carry no
  coronary arteries, no ostia and no cardiac veins (virtual-cohort tag list), so every step below is a construction on
  the mesh, labelled as such.
- **Placement algorithm, fixed now.**
  1. **LCA ostium**: on the aortic root shell at Toh's angular frame, as D15 builds it on the mesh (8.5 item 6;
     deviation D15, 20 Oct 2026), **theta = 56.2 deg** (Toh 2020 Fig. 3) and
     **14.8 mm above the virtual basal ring plane** (Toh 2020 Table 1, LCA ostium height 14.8 +- 2.4 mm), measured
     along the root's central axis (the aortic disc's normal). On the mesh the virtual basal ring plane is the aortic
     disc's mid-plane: the plane in which D15 builds Toh's frame and which holds the aortic mid-plane ring of 8.5 item
     5, as 8.5 item 2b reads de Kerchove's basal ring (deviation D15, 20 Oct 2026).
  2. **Artery direction**: from the ostium, the LCA runs in the plane tangent to the root shell, in the direction of the
     **left atrioventricular groove** on the mesh (the tag-1 to tag-3 boundary line, which is the groove the LCx
     follows). The bifurcation is placed at **9.59 mm from the ostium along the mesh surface** (Kuniewicz 2023 Table 1,
     LCA ostium to bifurcation 9.59 +- 4.14 mm). **Surface (geodesic) distance, not straight line** (recorded choice:
     Kuniewicz measured along the vessel, which lies on the surface).
  3. **Summit apex** = that bifurcation point.
  4. **Septal margin** = the line from the apex running toward the anterior interventricular groove (the tag-1/tag-2
     boundary on the anterior surface) of length **18.92 mm** (Kuniewicz Table 1, "LAD bifurcation - SP", the distance
     from the bifurcation along the LAD to the first dominant septal perforator). This is the **septal margin of the
     triangle, not its base** (correcting the 19 Oct draft): Kuniewicz publishes **no base length**.
  5. **Base** = the arc on the epicardial surface connecting the septal-perforator end point to the left AV groove
     (Lin 2016 Fig. 1: the base is "an arc connecting the first septal perforator branch (SP) of the LAD with the LCx"),
     closing the triangle. The apex angle is reported against Kuniewicz's 85.46 +- 15.94 deg.
  6. **Superior / inferior split**: by the great-cardiac-vein line, taken as the **bisector of the apex angle** running
     to the base (Lin: the summit is "bisected by the great cardiac vein"), with the vein arc length reported against
     v5.1's 14.0 mm.
  7. **Sites**: as v5.1, **2 summit sites per heart in each of the superior and inferior parts (4 in all), at the same
     depths v5.1 used**, so only the positions change and the family structure does not.
- **Check, reported:** the distance each re-anchored site moved from its v5.1 position, per heart, and the site-to-tip
  distances of 8.4.
- The v5.1 summit sites are scored beside the re-anchored ones (section 11, gate 1).
- Lin 2016's own definition is recorded: the summit is the triangular epicardial LVOT region whose tip is the
  bifurcation between the left anterior descending and the circumflex arteries, with its base on the arc between the
  first septal perforator and the circumflex, bisected by the great cardiac vein.

### 8.4 Geometry checks on the meshes (Lin 2016, report only)

- Straight-line distance from each simulated site to the summit tip (LAD/LCx bifurcation) against the group means
  11.89 mm (aortic sinus of Valsalva), 16.49 mm (subvalvar), 22.86 mm (GCV/AIV) and 31.10 mm (epicardium needing
  pericardial access), and against the 18.9 mm threshold (sensitivity 96.8 %, specificity 97.1 %); the comparator
  correlation between distance and the aVL/aVR Q ratio is r = 0.863, n = 66.
- Local wall thickness, measured perpendicular in diastole as Lin did, against 7.84 +- 0.84 mm (cusp and subvalvar) and
  11.03 +- 1.35 mm (GCV/AIV and epicardial), and against the 9.1 mm threshold (Lin 2016 accepted manuscript p.13, PDF
  p.14, where the cut-off has sensitivity 87.1 % and specificity 97.1 %; page added, 20 Oct 2026).
- The 9.1 mm **summit wall guard is dropped** (section 17): it is a clinical route predictor that would reclassify
  exactly the failing sites.

### 8.5 Aortic crescents (Toh 2020)

**Angular frame.** theta in the virtual-basal-ring plane about the root's central axis, theta = 0 at the bisector of the
interleaflet triangle between the non- and left coronary sinuses, increasing left to right to non. On the mesh the
frame is built as item 6 says (deviation D15, 20 Oct 2026).

| Landmark | theta (deg) |
|---|---|
| Left fibrous trigone | 52.4 +- 12.6 |
| LCA ostium (**Fig. 3 only**) | 56.2 +- 10.0 |
| LCC crescent anterior margin | 106.6 +- 8.0 |
| Centre of the L-R interleaflet triangle | 120.4 +- 5.2 |
| RCC crescent left margin | 135.5 +- 8.7 |
| RCA ostium (**Fig. 3 only**) | 205.3 +- 8.7 |
| RCC crescent right margin | 206.0 +- 13.1 |
| Centre of the R-N interleaflet triangle | 241.0 +- 6.0 |
| Right fibrous trigone | 305.0 +- 13.7 |

Source: Toh 2020 (Semin Thorac Cardiovasc Surg 32:230), 84 living human hearts, CT. The two ostium angles are **cited to
Toh 2020 Fig. 3**, where they appear; they are in neither the text nor the tables. Arithmetic checks reproduce:
106.6 - 52.4 = 54.2 deg (LCC extent); 206.0 - 135.5 = 70.5 deg (RCC extent); (206.0 - 52.4) / 360 = 42.7 % (muscular
share).

**Build rule.**
1. Muscle at basal-ring level occupies theta 52.4 to 206.0 deg continuously, 42.7 +- 4.3 % of the ring. The remaining
   57.3 % is fibrous on the root shell: membranous septum, right fibrous trigone, aortic-to-mitral continuity, left
   fibrous trigone. **No crescent under the non-coronary sinus.**
2. Two crescents, as lunes with h = 0 at every margin (the margins are where the anatomic ventriculo-arterial junction
   crosses the semilunar hingeline):
   - LCC lune over theta 52.4 to 106.6 deg (54.2 +- 13.0 deg), peak **2.9 +- 0.8 mm** (range 1.5-6.7);
   - h = 0 over 106.6 to 135.5 deg (the L-R interleaflet triangle carries no crescent, though it is muscular at ring
     level);
   - RCC lune over theta 135.5 to 206.0 deg (70.4 +- 13.5 deg), peak **6.4 +- 1.2 mm** (range 4.1-8.8).
2b. **RCC axial cap (deviation D5 (b), 20 Oct 2026; post-lock card 2, change 5, "Adopt all", 20 Oct 2026 11:23:21 UTC).** The RCC lune is built under two constraints at
   once: its reach along the root wall is at most h(theta) of item 2, **and** its axial height above the aortic
   valve-plane ring (the mid-plane ring of item 5; deviation D13, 20 Oct 2026) is at most
   **H(theta) = 2.4 sin(pi (theta - 135.5) / 70.5) mm** over theta 135.5-206.0 deg (the
   half-sine shape is assumption 48). Source of the 2.4 mm: de Kerchove 2015 Table 1 p.4 (pages of the uploaded 2014
   online proof, pp.1-9, used throughout this file, not journal pages; human, 58 fresh unfixed
   tricuspid aortic roots, 41 homograft and 17 cadaver): the external ventriculo-arterial junction lies 2.4 +- 1.5 mm
   (range -1 to +7) above the basal ring at mid-RCS. De Kerchove p.7 ties that height to right-ventricular and septal
   muscle adherent to the sinus base, so it is the external limit of all heart structures there and bounds the crescent
   height from above; it is not a direct crescent height. Gami 2011's 2.8 +- 1.2 mm (pp.6-8: the extent above the nadir,
   in the 55 % of hearts with an RCC extension; straight-line or along-wall not stated) is recorded and is carried by
   arm A28. **The value is fixed now, before step 2c, by source, and not chosen by its effect.** Where the cap binds on a
   near-vertical wall, the primary RCC crescent becomes nearly A28's 2.8 mm one. **No LCC cap**: the LCC lune's axial
   rise is reported against Gami's 1.5 +- 0.5 mm (report 35 (b)). Khelil 2015 (abstract only; its +- 0.4 with n = 20 is
   probably an SE) is not counted as a source. Under the precondition of item 9 the cap can only shrink the crescent,
   which moves gate 1 away from passing; gates 1, 3 and 8 are calibration checks for it (11.5).
3. **What the mm are: an inference, labelled.** Toh's own wording is "**maximal width**" (Methods p.232, Tables
   pp.235-236), and the paper never defines it further. This lock reads it as the **maximal distal extent** of the
   crescent inside the sinus wall, from the leaflet hinge to the distal limit of ventricular myocardium, on multiplanar
   reconstruction planes orthogonal to the virtual basal ring, rotated to the maximum. **That reading is a sound
   inference, not a stated definition, and is labelled so wherever the values are used.** It is not a circumferential
   width (those are the degrees) and not a thickness. **Used as a geodesic distance up the root wall from the hinge, not
   as a height above the basal plane.** No axial-component factor is used anywhere: the 19 Oct draft's "the purely axial
   rise is only about 45-50 % of the quoted value" is **deleted**, because that 0.45-0.50 figure was rated overstated
   and was never to be carried. **de Kerchove 2015, now read, cannot confirm the definition (correction, 20 Oct 2026).**
   Its 6.2 +- 1.2 mm (range 4-9) is a straight line from the inner basal ring to the outer ventriculo-arterial junction,
   at mid-RCS only (Methods p.2); it measures no LCC crescent. Toh p.236 cites de Kerchove's cadaver-subgroup LCS wall
   thickness (2.8 +- 0.8 mm, n = 17) as an LCC crescent width, so the "2.8 / 6.2 mm" concordance was not independent.
   Toh's own words for what was measured are "radial and circumferential extent" (Fig 8 legend p.238; p.240), so Toh's
   mm and de Kerchove's 6.2 mm are mostly radial (inference): with de Kerchove's means the horizontal component at
   mid-RCS is about sqrt(6.2^2 - 2.4^2) = 5.7 mm (derived). That is why item 2b caps the axial height.
4. **Shape between the margins (model assumption, fixed now).** A half-sine lune,
   h(theta) = h_max sin(pi (theta - theta_0) / (theta_1 - theta_0)), peaked at the angular midpoint of each lune. Toh
   gives neither the shape nor where the maximum sits.
5. **Reference line (model assumption; amended by deviation D5 (a), 20 Oct 2026, and defined on the mesh by deviation
   D13, 20 Oct 2026).** s is measured along the root wall
   from the **aortic valve-plane ring**, which stands in for the leaflet hingeline, since the meshes have no leaflets.
   **On the mesh it is the mid-plane ring** (D13; step-0 card 2, "Mid-plane", 20 Oct 2026 17:33:39 UTC; assumption 55): the closed curve
   where the aortic valve disc's mid-plane meets the luminal wall. The mesh valves are solid discs (aortic 6.3 / 5.7 /
   6.2 mm thick; report 35), the meshes carry no leaflets, hinge lines or nadirs, and the disc's mid-plane is the
   valve plane of the PC's report 35 (taken as the construction's own: inference, no pipeline source), so it is the
   reading that adds no offset of its own; which face an anatomical hingeline would sit on cannot be read from the
   mesh. Report 35 (a) and (h) give each disc's thickness, its two faces and the existing muscle above each face, per
   position. The 07:30 reference (the mesh's LV-myocardium-to-aortic-wall boundary) is withdrawn, so the lune and the
   existing mesh muscle are measured from one line (item 9, with its precondition and stop rule). Follow-up item,
   "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC (not shown on post-lock card 2). **If D5 (a) is
   declined:** the 07:30 text applies: s is measured from the mesh's LV-myocardium-to-aortic-wall boundary (assumption
   13 as locked).
6. **Angle frame on the mesh (model assumption 14; rewritten by deviation D15, 20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC).**
   theta = 0 is the direction of **the mitral-disc centroid**, projected onto the aortic disc's mid-plane about the
   root's central axis (the aortic disc's normal through the aortic ring's centroid). The direction of increasing theta
   is the sense in which **the pulmonary-disc centroid**, projected the same way, lies **90-150 deg** from theta = 0
   (Toh's L-R interleaflet triangle lies at 120.4 +- 5.2 deg; that it faces the pulmonary valve is this lock's check
   rule, kept from 13:51, not a statement of Toh's). Toh 2020 (84 living human hearts, CT) puts the left and right
   fibrous trigones at 52.4 and 305.0 deg, so the aorto-mitral continuity between them is centred at -1.3 deg (derived:
   (52.4 + 305.0 + 360) / 2 - 360), within this frame's resolution, and no offset is applied. The continuity is where
   the anterior mitral leaflet hangs from the aortic root, so its centre faces the mitral orifice, and the projected
   direction of the mitral-disc centroid is the mesh's reading of it (model assumption); centroid directions are used
   for both valves, so the two ends of the check are read the same way. The frame serves every use of Toh's theta: the
   lunes and the hard gate of this section, the cusp sites of item 11b, the RCC cap of item 2b, de Kerchove's six
   positions in report 35, and the LCA ostium of the summit re-anchor (8.3 step 1), its angle and the plane and axis
   its 14.8 mm height is measured from (the aortic disc's mid-plane and its normal). The LCA ostium angle is reported
   against 56.2 +- 10.0 deg as a second check, and the 13:51 nearest-point readings are reported beside the frame
   (report 35 (i)). **Stop rule (unchanged):** if neither sense puts the pulmonary-disc centroid in 90-150 deg, stop
   and report; do not pick the closer of the two. **Measured before D15 was written in (report 35 (i), read-only):**
   126.9 / 126.4 / 128.1 deg (derived from the PC's angles: 59.1 - 292.2 + 360; 72.0 - 305.6 + 360; 67.1
   - 299.0 + 360), inside 90-150 deg in all three hearts, so the frame check passes and step 2c can run. Reported
   beside it, not used: the centre of the arc where RV muscle (tag 2) touches the aortic root (tag 5) 0-6 mm above the
   mid-plane lies at 183.9 / 186.7 / 190.4 deg in this frame, at the right coronary sinus (de Kerchove's RCS, placed at
   180.7 deg in Toh's frame as in the PC's report 35; derived: (120.4 + 241.0) / 2, midway between Toh's L-R and R-N
   interleaflet triangles; de Kerchove gives positions, not angles), where Gami 2011 pp.9-10 found the RCC sinus wall
   contiguous with the posterior RVOT infundibulum in 603 of 603 human autopsy hearts. **Superseded by D15 (the 13:51
   rule, kept as history):** "theta = 0 is placed at the aortic-ring point nearest the mitral ring (the aorto-mitral
   continuity lies in the non-left region). The direction of increasing theta is checked by requiring the L-R
   interleaflet triangle landmark to face the pulmonary valve, accepted when the measured angle from theta = 0 to the
   ring point nearest the pulmonary valve lies in 90-150 deg against Toh's 120.4 deg." At step 0 it failed in every
   heart (42.3 / 62.9 / 60.9 deg; the other sense 317.7 / 297.1 / 299.1 deg), because the aortic and mitral discs never
   touch on these meshes (closest ring-to-ring distance 8.84 / 7.66 / 7.91 mm), so the nearest point is not a point of
   continuity (19.15.5).
7. **Thickness (model assumption, fixed now, unsourced).** Toh reports no crescent thickness anywhere (verified by
   full-text search). The crescent inherits the parent mesh's local LVOT wall thickness at the hinge and tapers linearly
   to 1.0 mm at the distal margin. **It is never resized after a run.** Note (report only, 20 Oct 2026): the tag-5 wall
   is a 2 mm distance-map shell (Solis-Lemus, section 3.2.1), so where the rule asks for more the achieved thickness is
   about 2 mm; the LCC achieved thickness is reported against de Kerchove's LCS root-base wall thickness,
   3.0 +- 1.0 mm (Table 1 p.4), report only (report 35 (c)).
8. **Tissue identity and physics.** The LCC lune is LV free wall; the RCC lune is ventricular septum. Both are LV
   myocardium, electrically continuous with the LVOT wall, and take the fix-5 LVOT fibre blend (**R5.2**) and the LV
   speeds of fix 4, not an RV rule.
8b. **The mesh operation, fixed now (the crescents are outside the v5.1 simulation mesh).** The simulation mesh is tags
   1, 2, 25, 28, 29; the aortic root is tag 5 and the pulmonary artery tag 6, so new outflow muscle can only come from
   **re-tagging existing tag-5 wall elements into tag 1**, within the lune h(theta) measured from the reference line of
   item 5. Nothing is extruded and no new elements are generated, so the geometry stays the published mesh's. Rules:
   - where the tag-5 wall is **thinner** than item 7's thickness rule asks for, the whole wall thickness is re-tagged
     and the achieved thickness is reported (the mesh, not the rule, sets it there);
   - where it is **thicker**, only the elements within the required thickness from the luminal face are re-tagged;
   - the re-tagged elements are added to the LV/RV simulation mesh, and the **UVC and transmural w are re-solved on the
     merged mesh** (the same Laplace solves v5.1 used) so that R1.3's blend and R5.1-R5.2's fibre rule are defined on
     the new muscle; this re-solve runs inside step 2c, before fibres are written, and step 2a's fibre assignment is
     repeated on the merged mesh;
   - every re-tagged element is listed in the manifest, per heart, with its volume.
9. **Hard gate.** No muscle bridge across the aorto-mitral continuity or under the non-coronary sinus. The build fails
   if any is created. **Pre-existing mesh muscle above the aortic valve plane** (the disc's mid-plane, deviation D13),
   if step 0 finds any (for example under
   the non-coronary sinus), is **left exactly as v5.1 had it and reported per heart**; none is trimmed. **Inside the two
   lunes the total crescent muscle is max(existing, lune), both measured from the aortic valve-plane ring** (the
   mid-plane ring of item 5; deviation D13, 20 Oct 2026): the same
   rule as the pulmonary side (8.6), now stated without ambiguity (deviation D5 (a), 20 Oct 2026, a follow-up item,
   "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; the 07:30 text said both "no crescent is added there" and "the same rule as the pulmonary side").
   Outside the lunes nothing is added.
   **Precondition and stop rule:** step 0 reports, per heart, the height of the tag-1/tag-5 boundary relative to the
   valve plane (report 35 (h)); if the boundary lies below the plane, moving the reference line (item 5) could add muscle
   instead of only bounding it, so **stop and report before step 2c**. **At step 0 it passed, from the mid-plane ring
   (deviation D13, 20 Oct 2026):** report 35 (h) puts the tag-1/tag-5 boundary 2.0-5.6 mm above the mid-plane at all six
   positions in every heart, and LV muscle stands 1.1-5.5 mm above it all round the root, so the result does not depend
   on the angular frame (D15; inference). Measured from the disc's arterial face, about 3 mm higher, the boundary would
   lie below it at some positions in every heart (19.15.3). Recorded beside the hard gate: muscle beyond the
   junction at the non-coronary sinus is a rare variant (Hasdemir 2007 p.536, non-coronary 4 of 95 hearts, derived;
   Gami 2011 NCC 0.66 %). **If D5 (a) is declined:** the 07:30 text of this item applies ("no crescent is added there,
   and none is trimmed. The same rule as the pulmonary side (8.6)"), its two readings are put to Alex before step 2c,
   and the precondition above does not apply.
10. **Ceiling check.** The shell muscle stays far below the ostia (LCA 14.8 +- 2.4 mm, RCA 17.7 +- 3.2 mm above the basal
    plane, on the mesh the aortic disc's mid-plane, as 8.3 step 1), so there is no conflict.
11. **Resolution flag, reported.** On a 1 mm mesh the LCC crescent of 2.9 mm is about 3 elements and the 1.5 mm
    per-patient floor is at the mesh limit; the RCC crescent of 6.4 mm is about 6 elements. **Nothing here is resized to
    move a gate**, at any resolution.
11b. **Cusp sites in the crescents, fixed now (this is the gate-1 primary cusp set).** Per heart, **4 cusp sites**: two
    in the LCC lune and two in the RCC lune, at **theta = the lune's angular midpoint** (theta in the frame of item 6,
    deviation D15) and at **theta = midpoint +- a
    quarter of the lune's angular extent** as follows - LCC at 79.5 deg and 93.1 deg; RCC at 170.8 deg and 188.4 deg
    (derived from the margins of item 2). Each site sits at **50 % of the built extent** at that theta along the
    reference line (the mid-plane ring of item 5, deviation D13; half-way up the crescent as built, after the item 2b
    cap and the item 9 max rule; this amends the
    07:30 "50 % of the local h(theta)" and assumption 35: deviation D5 (c), 20 Oct 2026, a follow-up item,
    "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC, not shown on post-lock card 2) and at **mid-thickness** of the re-tagged muscle (where the crescent adds no muscle at that height, which D13 makes
    likely in places, mid-thickness of the existing muscle there, the built extent then being the existing muscle;
    clarified with deviation D13, 20 Oct 2026, no value changes). **If D5 (c) is
    declined:** each site sits at 50 % of the local h(theta), as at 07:30 (assumption 35 as locked); a site that then
    falls outside the built muscle is handled by the capture criterion of 8.7 (recorded, counted and excluded, never
    moved). Depths are therefore fixed by geometry,
    not chosen per heart. The v5.1 valve-plane cusp sites are kept and scored beside them (11.2).
12. **Arm.** A28 Gami's smaller crescents (RCC 55 % of hearts, 2.8 +- 1.2 mm, maximum 8 mm; LCC 24 %, 1.5 +- 0.5 mm,
    maximum 2 mm; NCC 0.66 %, 1.3 +- 0.5 mm; intercuspal 49 %, 2.2 +- 1.1 mm; 603 formalin-fixed autopsy hearts,
    Gami 2011), **a second, smaller measurement of the same structure** (correction, 20 Oct 2026: the 07:30 text called
    it "the lower bound"). Gami measured the "extent ... from the inferior-most point of the line of attachment ... to
    the maximum height of sleeve extension" (p.6; straight-line or along-wall is not stated) and found an RCC extension
    in only 55 % of hearts, against 84 of 84 in Toh; the gap is probably partly measurement direction and partly
    detection or definition (inference). It disagrees with Toh by more than a factor of two for the RCC. Against the D5
    primary, A28's RCC (2.8 mm) moves gate 1 either way per heart, depending on how far the cap binds, and its LCC
    (1.5 against 2.9 mm) moves gate 1 away from passing.
    - The per-heart rotation correction read off Toh Fig 6 (rotation defined in Methods p.233; root rotation
      4.3 +- 14.0 deg, range -47.8 to 27.0, in the Table on p.236; clockwise rotation decreases the LCC extent,
      R2 = 0.3899, and increases the RCC extent, R2 = 0.2752, both P < 0.001, printed on Fig 6 p.237 and in the abstract
      p.230; the regressions relate rotation to the angular extents in degrees, not to the mm widths; pages added,
      20 Oct 2026) is **not an arm in v5.2**: it is not on the adopted list, and Toh prints no regression coefficients, so
      it cannot be built. It is recorded as a reader proposal in 17.1 (former A29).
13. Recorded: Toh's abstract prints the LCC extent as 54.2 +- 12.0 deg where the Results and Fig 8 print
    54.2 +- 13.0 deg. **13.0 is used.**

### 8.6 Pulmonary sleeves (Lis 2021)

Source: Lis 2021 (J Cardiovasc Electrophysiol 32:2269), 65 human hearts, ex vivo histology.

| Quantity | Value | Note |
|---|---|---|
| Shape | a **complete cylindrical sleeve** over the whole circumference, continuous with the infundibular myocardium below, wide base and narrow apex | Lis p.2273 (citing Stamm 1998); not three crescents |
| Height above the cusp-insertion nadir, along the sinus midline | left anterior 4.12 +- 1.76 [0.99-9.05], right anterior 3.69 +- 1.47 [0.83-8.59], posterior 4.28 +- 1.73 [1.12-8.96] mm; p = .137 | **built as 4.0 mm uniformly** (derived mean of the three; no significant difference between sinuses) |
| Thickness at 25 / 50 / 75 % of sleeve length | 2.0 / 1.7 / 1.0 mm (per sinus 1.89 / 1.94 / 2.08, 1.72 / 1.60 / 1.68, 0.89 / 0.96 / 1.04 mm; levels differ at p < .001, sinuses do not) | piecewise linear between the three levels, full infundibular thickness at 0 %, **1.0 mm held from 75 % to the end** (model assumption) |
| Overlying fibrous layer | 0.32-0.47 mm on the arterial (luminal) aspect, always thinner than the muscle | **0.40 mm taken as the single value** (midpoint, fixed now, no longer a range). On a 1.05 mm mean-edge mesh it cannot be its own element layer, so it is **not meshed as geometry**: it is a **conductivity-and-excitability tag on the luminal element face of the sleeve** - non-excitable, 0.2 S/m in the lead-field mesh (section 4). Blood is capped at that **fibrous layer's luminal face**, which is the correct side (the layer lies between blood and muscle) |
| Prevalence | left anterior 86.2 %, right anterior 89.2 %, posterior 90.7 % (p = .699); all three in 69.2 % of hearts | **all three built, the modal heart** |
| Supporting dimensions | sinus wall height 4.96-5.39 mm; cusp length **13.5-13.8 mm** (right anterior 13.8 +- 2.4, left anterior 13.7 +- 2.6, posterior 13.5 +- 2.4; differences not significant) | |

- **The nadir and the reference on the mesh (deviation D13, 20 Oct 2026; step-0 card 2, "Mid-plane", 20 Oct 2026 17:33:39 UTC;
  assumption 55).** The meshes carry no leaflets, hinge lines or nadirs, and the pulmonary valve is a solid disc
  6.2 / 5.8 / 6.2 mm thick (report 35). Each sinus's **cusp-insertion nadir is the mid-plane ring's point at that
  sinus's centre** (the sinus centres placed by assumption 18), and the sleeve's height, its 25 / 50 / 75 % thickness
  levels, the max(existing, 4.0 mm) rule and the supravalvar sites are measured from the **mid-plane ring**, the closed
  curve where the pulmonary disc's mid-plane meets the luminal wall. At step 0 (13:51 file) the PC read the nadir at the
  ring's lowest point, 2.3-3.7 mm below the mid-plane; that reading is superseded. RV muscle already stands 1.7-8.0 mm
  above the mid-plane (medians 3.9-6.9 mm), so the sleeves add muscle only where it stands less than 4.0 mm (6G8DD8S5
  from 2.0 mm and 7D98EVAR from 1.7 mm; none in Y5HYEDL4, whose minimum is 4.2 mm); nothing is trimmed (19.15.3).
- **Placement on the mesh (model assumption, fixed now).** The posterior sinus is centred at the pulmonary ring point
  nearest the aortic root (on the mid-plane ring, deviation D13); the other two sinuses at +- 120 deg from it.
- **The mesh operation, fixed now.** As on the aortic side (8.5 item 8b): the sleeve is made by **re-tagging existing
  tag-6 (pulmonary artery) wall elements into tag 2**, within 4.0 mm above the pulmonary mid-plane ring all round the
  circumference (the ring that carries the three cusp-insertion nadirs, deviation D13, 20 Oct 2026), never by extruding
  new elements; where the tag-6 wall is thinner than the thickness profile asks for, the whole wall is re-tagged and
  the achieved profile is reported; the **UVC and w are re-solved on the merged mesh** in step 2d and the fibre rule is
  re-applied. Because the mean edge is 1.05 mm, the **acceptance tolerance on the thickness profile is one element
  (+- 1.05 mm), not 0.1 mm** - a 0.1 mm tolerance cannot be met or even measured on this mesh, and the 19 Oct draft's
  0.1 mm acceptance is withdrawn.
- **Heart scope.** All three hearts, with their own mesh walls; the sourced dimensions are the same for all three (Lis
  reports no group split).
- **Speeds in sleeve muscle.** The same fix-4 RV speeds as the rest of the RV, with the circumferential fibre rule
  below. No slower outflow value is used (section 5.1: the only data are mouse and show no difference, and slowing the
  outflow is the most tempting tuning knob for gate 3).
- **Fibres.** Circumferential throughout the sleeve (Doste 2019 outflow epicardial angle 0 deg; Ho 2006 describes the
  arterial sleeves' myocardium as circumferentially arranged).
- **Supravalvar sites.** One per sinus, **three per heart (nine in all)**, at 50 % of the sleeve length and
  mid-thickness.
- **The "circumference share" is wrong and is dropped.** Lis's 26.7-31.9 % is a percentage of sinus height covered by
  the extension, and its denominator is not the paper's own 4.96-5.39 mm sinus wall height: the reported percentages
  reproduce extension height divided by **cusp length** for two of the three sinuses (derived: 3.69 / 13.8 = 26.7 %
  against the reported 26.7 %; 4.28 / 13.5 = 31.7 % against 31.9 %; but 4.12 / 13.7 = 30.1 % against the reported
  28.9 % for the left anterior sinus, which does not reproduce). The 5 mm denominator would give 74-83 %. The sleeve is
  never built as 0.27 x 5 mm.
- **Existing mesh muscle above the pulmonary valve plane: neither extended nor trimmed, and the built height is capped
  at the sourced 4.0 mm (rule fixed now).** Step 0 reports, per heart, how much muscle the mesh already carries above
  the valve plane (the disc's mid-plane, deviation D13). Then:
  - the sleeve is built so that the **total** muscle height above the cusp-insertion nadir is
    **max(existing, 4.0 mm)** - that is, muscle is added only where the mesh has less than the sourced 4.0 mm, and
    **nothing is added anywhere else**;
  - **nothing is trimmed**: pre-existing mesh muscle (up to the 8.8-9.05 mm seen in these series) is v5.1 geometry and
    stays bit-identical, because trimming a published mesh is unsourced mesh surgery on a failing gate;
  - the achieved height per sinus per heart is reported against 4.0 mm, so any heart-specific excess is visible.
  Neither of the two options a reviewer offered is taken: "keep the mesh muscle and add nothing" would drop an adopted
  structure, and "trim everything above 4.0 mm" is mesh surgery. **Arm A30a** (new, replacing the withdrawn island arm's
  slot): trim all mesh muscle above 4.0 mm above the nadir, **marked "moves gate 3"**.
- **Default stops at the fibro-arterial transition zone.** Sleeves extending beyond it were present in at least one sinus
  in 33.8 % of hearts (posterior 21.5 %, each anterior 7.7 %, p = .021) and exceeded 10 % of sleeve length in only 13.8 %
  of hearts. The beyond-the-zone variant is **not** run as an arm (section 17).
- The muscular-island perturbation (horizontally oriented muscular islands separated by adipose tissue, seen in at least
  one sinus in 33.8 % of hearts) is **not an arm in v5.2**: it is not on the adopted list and the perturbation itself
  cannot be specified from the sources read (17.1, reworded 20 Oct 2026). Recorded as a reader proposal in 17.1 (former
  A30).
- **Shrinkage caveat, recorded.** These are formalin-fixed, dehydrated, paraffin-embedded specimens, so the heights and
  thicknesses are plausibly underestimates in vivo.
- **Prevalence, written with Hasdemir 2007 in hand (correction, 20 Oct 2026; the PDF arrived at 07:44, after the
  lock).** Hasdemir 2007 p.534 (95 consecutive human autopsy hearts): **22 % is the per-heart figure for muscle beyond
  the junction in either artery (21 of 95)**; pulmonary artery 16 of 95 (17 %), aorta 7 of 95 (7 %). Gami 2011 reports
  his own 57 % (aorta) and 74 % (pulmonary), and Lis frames the gap as 100 % against 17 %. Hasdemir's method (p.535):
  one longitudinal strip about 10 mm wide per cusp, from 20 mm below the ventriculo-arterial junction to 20 mm above the
  sinotubular junction; his ventriculo-arterial junction is where the ventricular myocardium within the sinus ends, and
  his "subtle ridge at the level of the top of the three commissures" is the sinotubular junction. The 07:30 text,
  following Gami's description, called that ridge the junction and the sampling "random biopsies"; both are withdrawn.
  The difference is definitional, not a conflict: Gami and Lis count muscle above the lowest point of cusp attachment,
  Hasdemir only muscle beyond the end of the sinus myocardium. The cusp-insertion line lies about 4 mm below the
  ventriculo-arterial junction (Lis 2021 p.2273, citing Gami 2011, where the figure was not found); Hasdemir gives no
  nadir-to-junction distance. **The build uses the cusp-nadir reference**, the landmark the heights are tied to and the
  one visible on intracardiac echo; on the mesh the nadir is the mid-plane ring's point at each sinus centre
  (deviation D13, 20 Oct 2026). Also from Hasdemir p.536: pulmonary extensions 3.25 +- 1.3 mm long and
  0.83 +- 0.71 mm thick, and the arterial walls 2 cm above the junction 1.6 +- 0.4 mm (aorta) and 1.01 +- 0.4 mm
  (pulmonary artery), compared in report 35 (d).

### 8.7 The stimulus in thin muscle (clipping rule, fixed before gates 1 and 3 are re-run)

- **The ball is 1.5 mm in radius** (3 mm across), as v5.1's code implements it (section 1). The 19 Oct draft used
  "diameter" here and "radius" in 17.1; radius is correct.
- **The stimulated set, defined exactly.** The stimulated nodes are the nodes within 1.5 mm of the site node that (a)
  are excitable myocardium, and (b) lie in the **same connected excitable component as the site node, reached without
  crossing the infundibulum cut plane (8.2), the non-excitable fibrous layer (8.6) or any non-myocardial tag**. The ball
  is never grown to compensate. Condition (b) is what the rule is really for: without it, a ball at an RCC crescent site
  could stimulate RVOT muscle across the cut, because the RCC sinus wall is contiguous with the posterior RVOT
  infundibulum in 603 of 603 hearts (Gami 2011), and that co-capture would defeat the cut on both gate 1 and gate 3.
- **Scope: every site.** Wherever nothing changed, the rule selects exactly the v5.1 node set, so the v5.1 sites stay
  bit-identical; the 19 Oct draft's "outflow sites only" is withdrawn as a scope statement.
- **Capture criterion, fixed now.** A site is a valid stimulus site only if **at least 4 nodes** (about 4 mm3 at the
  mesh's 1.05 mm spacing, that is roughly one element's worth of tissue in every direction) satisfy (a) and (b). A site
  that does not is **recorded, counted and excluded from its family**, with its family's n reported as reduced. **It is
  never moved**, never grown and never re-placed, because moving a site after seeing that it failed would be choosing
  sites by their result.
- **What clipping does in each engine, stated so the prediction is honest.** The simulation mesh contains myocardium
  only, so clause (a) removes nothing in the graph eikonal: the eikonal effect of clipping proper is **0**. Clause (b),
  the connectivity restriction, does bite at RCC and supravalvar sites next to the cut, and it can only **reduce** the
  seed set, which **delays** activation and **lengthens** paced QRS. The 19 Oct draft's "a slightly earlier and smaller
  start ... shortens paced QRS" is backwards and is withdrawn: fewer seed nodes cannot advance activation.
- The **fraction of the ball landing in muscle is reported at every site**, outflow sites in particular.
- Why the rule is needed: the sleeve apex is 0.89-1.04 mm thick and the LCC crescent floor is 1.5 mm, both at or below
  the ball's 3 mm extent, so without a rule the stimulus geometry and not the anatomy would set the result.
- Clinical context reported beside gates 1 and 3: **Yamada 2010 (J Cardiovasc Electrophysiol 21:170)** could not capture
  LV myocardium within the left coronary cusp in 13 of 29 cases (45 %) even at 20 mA and 2.0 ms, and in 2 of 9
  epicardial cases; Yokokawa 2016 reports cusp capture thresholds of about 17-19 mA at 2 ms. **This is clinical context
  only**: in a model there is no stimulus current, so non-capture here can only come from the capture criterion above,
  and the model is not expected to reproduce the clinical 45 %.
- The finite-source arm (A27, 5 and 10 mm) covers the clinical reality that cusp and coronary-vein pacing at 12-19 mA
  captures tissue remote from the electrode. It stays an arm and is not promoted to primary (section 17).

### 8.8 Site placement checks (Acosta 2015, Yamada 2010)

- Pulmonary valve to left coronary cusp 5 +- 3 mm (range 1-8); PV to right coronary cusp 11 +- 5 mm.
- Every RVOT origin within the first 10 mm below the PV; earliest-activation-site-to-PV distance 4.2 +- 5.5 mm.
- LVOT origins project to a septal-RVOT breakout 9.2 +- 7 mm below the PV (range -3 to 22).
- Subendocardial outflow-to-outflow connections a median 7 mm (5-11) below the PV at the LCC against 12 mm (9-15) at the
  RCC.
- LCC to GCV/AIV 14.3 +- 3.5 mm (**Yamada 2010, J Cardiovasc Electrophysiol 21:170**) as the cusp-to-summit spacing
  check.
- Paired sites at two apicobasal levels, at the valve and about 1 cm below, following Doste.
- Closest outflow myocardium to the left main is the posterior RVOT infundibulum, not the LVOT: nearest pulmonary sleeve
  4.8 +- 1.7 mm against nearest aortic sleeve 16.3 +- 3.3 mm (Gami 2011, p = 0.0005).

### 8.9 Swap-in rules had the cusp-muscle card been answered differently (record only; it was answered "Both", 05:18:46)

Each option below is a **complete block**: finalising the lock is a single line, "use block X", and the block lists every
section, row, arm, assumption, prediction, site set and build step it replaces. **Under every option the infundibulum
cut (8.2), the summit re-anchor (8.3), the clipping rule (8.7) and fixes 1-5 are built**, so **gates 1 and 3 stay
calibration checks under every option** (gate 1 for fix 1, fix 5's outflow blend, the cut, the re-anchor and the clipping rule; gate 3 for fix 5's outflow blend, the cut, the re-anchor and the clipping rule; gate 8, by the site test of 11.5, for the same changes except fix 1; fix 4's 07:30 gate-1 label is withdrawn under post-lock card 3, deviation G, 20 Oct 2026; the per-change lists of 11.5 govern for whatever each block builds). The 19 Oct claims that gate 1 or gate 3 would
"stay a plain failing gate" are wrong and are withdrawn, as is "no other value in this file changes".

**Block A: "Build both" (the option chosen on the cusp-muscle card, 05:18:46).** As written throughout.

**Block B: "Aortic crescents only".**
- Build 8.5; **drop 8.6 entirely** (no sleeve, no supravalvar sites).
- R3.1: blood capped at the **pulmonary valve ring**, not at a sleeve face. R3.3: the sleeve fibrous-layer row falls
  away. Assumptions 16-19 are deleted; assumption 15 stays.
- Site and beat ledger (11.2a): the **9 supravalvar beats are removed** (3 per heart) and the ledger total drops by 9;
  the cusp-crescent sites of 8.5 item 11b stay.
- Gate 3's site families (11.2b): **no supravalvar sites join the RVOT family**; the RVOT family is v5.1's.
- Section 14: delete the "Pulmonary sleeves" row; the "Aortic crescents" row stays. 14.3's muscle-fraction row keeps
  only the crescent half. **Gate 3 remains a calibration check** for the cut, the re-anchor, the clipping rule, fix 5's outflow
  blend **and now also the crescents** (the aortic-sinus value is one of the five in the Daniels order; 11.5 governs).
- Arms: A30a falls away. Step 2d is deleted; steps 2c, 2e stay. Report 28 keeps only the crescent flags.
- **Stated limitation to be written in the paper:** "The pulmonary sleeves, present in 86-91 % of human hearts over the
  whole circumference to a mean 3.7-4.3 mm above the cusp nadir (Lis 2021, 65 hearts), are not represented; RVOT
  supravalvar origins therefore cannot be paced in this model, and RVOT-site results carry that limitation."
- **The option not chosen runs as an arm**, symmetrically with the pose card: the sleeves run as **arm A38** (ECG and
  activation, RVOT and supravalvar beats), reported beside the primary.

**Block C: "Neither".**
- Drop 8.5 and 8.6. Keep 8.1-8.4, 8.7, 8.8.
- **Gate-1 and gate-3 cusp sites revert to the v5.1 valve-plane muscle sites** (the precedent is recorded: Doste 2022
  places cusp-region sites in valve-plane muscle, as v5.1 does). 11.2's primary cusp set becomes the v5.1 set, and
  11.2's "new crescent cusp sites" clause falls away; the summit sites are still the re-anchored ones.
- R3.1 and R3.3 as in block B. Assumptions 12-19 are deleted.
- Ledger: the 12 crescent cusp beats (4 per heart) and the 9 supravalvar beats are removed.
- Section 14: delete the "Aortic crescents" and "Pulmonary sleeves" rows; 14.3's muscle-fraction row is deleted.
- Arms: A28 and A30a fall away. Steps 2c and 2d are deleted. Report 28 is deleted.
- Gates 1 and 3 **stay calibration checks** for the cut, the re-anchor, the clipping rule and fix 5's outflow blend,
  and gate 1 also for fix 1 (fix 4's 07:30 label is withdrawn under post-lock card 3; deviation G, 20 Oct 2026; 11.5
  governs).
- **The option not chosen runs as an arm**: crescents and sleeves together as **arm A38**, reported beside the primary.

## 9. Heart pose in the torso, and the torso arms

### 9.1 Pose (the pose card, answered "CT pose", 20 Oct 05:19:07 UTC)

- **Primary: each heart's own CT orientation, translated into place only, with no rotation.** The heart keeps the
  orientation its own CT gives it; only the translation that puts it in the T13 torso is applied.
- **The translation rule, fixed now (the draft's "translated into place only" did not say how).** v5.1's pose is a rigid
  ICP fit of the atria onto the SSM shape g001, x' = R x + t. Dropping R while keeping t would move the heart by
  (R - I) c, which depends on the pivot: for the 13.4 deg heart |(R - I) c| = 2 sin(theta/2) |c| = 0.233 x 70-110 mm,
  that is 16-26 mm, enough to change every amplitude criterion (Bradley 2000: about 8 % relative RMS per 10 mm). So the
  rule is: **translate each heart with rotation fixed at the identity so that the LA+RA surface centroid lands exactly
  where the v5.1 ICP fit put it**, t' = R c + t - c, with c the LA+RA centroid in mesh coordinates. The resulting 4x4
  transform is recorded per heart in the manifest.
- **Acceptance (step 2f).** No myocardial, blood or sleeve node outside the T13 skin, with a stated minimum clearance of
  **5 mm** from the skin; every electrode-to-nearest-myocardium distance reported per heart. If the acceptance fails,
  stop and report; do not rotate the heart to make it fit.
- **Orientation report, never used to choose the pose.** The heart's long-axis and short-axis orientation in torso
  coordinates is reported per heart, and against the v5.1 pose. It is a report: it plays no part in choosing or
  adjusting the pose, in either direction.
- The v5.1 atrial-fit rotation is dropped from the primary. For the record, the fitted rotations were 13.4 deg
  (Y5HYEDL4), 19.9 deg (6G8DD8S5) and 18.6 deg (7D98EVAR); the "13 degrees" in the card text is the control heart's
  value only, not a cohort value. **Step 0 first confirms that v5.1 really applied that rotation and records its axis
  and pivot**, since the swap-in depends on it.
- **CT-phase caveat, recorded.** The cohort CTs are not ECG-gated to a specific cardiac phase, so the pose and the wall
  thicknesses belong to an unknown phase, while the CMR norms of section 12 are end-diastolic.

### 9.2 Swap-in rule had the pose card been answered "the v5.1 atrial fit" (record only)

**Use v5.1's own tagged 4x4 transform per heart, bit-identical** (rotation and translation together, as the v5.1
manifest records them) - not "the rotation with the same translation", which would produce a third pose that is neither
v5.1's nor the CT pose. Then:
- run the **CT pose as arm A32** instead (it is an arm either way);
- **swap the prediction rows**: the section 14 "CT pose" row becomes "Atrial fit", and its 14.1 mechanism row changes
  from "rotates the heart by 13-20 deg against v5.1" to "**keeps v5.1's pose, so the pose contributes 0 against v5.1**,
  and the CT pose becomes the arm"; the 14.1 and 14.2 entries that lean on a pose change are set to "0" accordingly;
- the acceptance and orientation report of 9.1 still run, on the v5.1 pose.

### 9.3 Torso, primary

T13 (the KIT mean torso: shape T_13, which the record's description names the mean of its 25 shapes, 9.4), homogeneous
at 0.2 S/m, no lungs. Recorded: comparison models use 0.22 S/m (Bradley 2000
cavity, 455 ohm-cm) and 0.239 S/m (Klepfer 1997, a mean of tissue values and not a measurement), and Keller 2010's trunk
range is 0.216-0.241 S/m. A torso-conductivity arm at 0.22 or 0.25 S/m is **not** run (section 17).

### 9.4 Torso and forward-model arms (A31-A37; values here, scope in section 13)

- **Lungs (A35): a feasibility-gated, ECG-only arm in a host human torso that has lungs (deviation D9a, 20 Oct 2026;
  post-lock card 2, change 9, "Adopt all", 20 Oct 2026 11:23:21 UTC).** Values: central **0.078 S/m** (Geddes and Baker 1967, dog in vivo average, 1275 ohm-cm), bounds
  0.0389 (Gabriel 1996 Part III, excised animal) and 0.134 S/m (Kaufman and Johnston 1943 Table IV p.49: dog lung at
  the end of normal inspiration, 4 animals, 744 ohm-cm (postbiologic calibration, 7 observations; the prebiologic
  value is 766 ohm-cm, 9 observations, 0.131 S/m); relabel, 20 Oct 2026). All labelled non-human: no human
  low-frequency lung value exists in these papers. Support for the centre: Schwan and Kay 1956 p.668 (dog lung in situ,
  7 dogs in the series, 1 kHz) measured about 1000 ohm cm, 0.100 S/m. p.669: the 1 kHz figures are "uniformly lower by
  about 20 per cent" than the resistance at heart frequencies, so about 0.080 S/m in the ECG band (derived:
  1000 / 0.8 = 1250 ohm cm; 100 / 1250 = 0.080); pp.668-669: resistance rises by about 5 % from 1 kHz to 100 c/s and by
  about 20 % to 10 c/s (derived: 100 / 1050 = 0.095 and 100 / 1200 = 0.083 S/m), so 0.080-0.095 S/m in the ECG band
  (corrected 20 Oct 2026: the earlier 100 / 1200 applied the p.669 20 % in the wrong direction). Values taken at 1 kHz
  are biased high in conductivity by about that margin. The host's own lung value, 0.0714 S/m, is unsourced; it is
  recorded and not used. Lungs stay an arm, not the primary, because they come from another person.
  - **Host, fixed now.** KCL_torso1 of the KCL whole-torso models (Zenodo record 7253863, Qian and Bishop, CC BY 4.0,
    published 26 Oct 2022; the record describes torso models of five healthy patients, with hearts and ICD lead and
    can). Its record and file IDs are written into LABNOTES at step 0.
  - **Placement, fixed now.** The host's heart, blood pools, valves and ICD lead and can tags are removed. Each pilot
    heart is placed by its UVC long and short axes onto the removed host heart's long and short axes, as Campos 2026
    registers a heart in an existing torso ("aligned via the heart's short and long-axes defined via UVCs", supplement
    p.7). After placement the heart is never moved, scaled or rotated (assumption 52).
  - **Overlap and clearance, fixed now (assumption 52).** Host lung elements that overlap the pilot heart, or lie within
    2 mm of its epicardium, are re-tagged to background; the lung volume removed is reported per heart.
  - **Remeshing.** meshtool only (fTetWild is not installed on the PC, 11.4 item 1). If meshtool cannot produce the
    merged mesh, the arm is **not run**, and that is recorded.
  - **Tissues.** Every non-lung host tissue (skin, bone, liver and the rest) is homogenised to the 0.2 S/m background,
    identically in both legs, so the arm isolates the lungs.
  - **Electrodes.** The KCL record lists no ECG electrode positions, so they are placed by the Kligfield landmark rules
    of the forward check below.
  - **Report.** Lungs on minus lungs off, both in the host torso (the arm's effect); host lungs-off against T13 (the host
    effect); and a memory estimate under the 15.1 rule before any solve.
  - **Step-0 read-only check, fixed now.** (i) The KCL_torso1 files open with meshtool or the Python standard library on
    the PC (meshio and pyvista are not installed); (ii) their element and node counts, and a memory estimate, fit the
    15.1 single-process rule within WSL's 7.7 GB; (iii) the host heart's long and short axes can be computed by the same
    UVC Laplace solves v5.1 used, and if they cannot, A35 is not run; (iv) the electrode landmarks of the forward check
    below (sternum, intercostal spaces, clavicles, costal margin, iliac crest) can be identified in the host's tags. Any
    failure: A35 is recorded as not run, with the reason.
  - **Run at step 0 on the 13:51 file (no deviation; the rule above).** Checks (i)-(iii) passed; check (iv) failed:
    KCL_torso1 ends at z -306 mm, above the iliac crest, so the LL electrode cannot be placed by the Kligfield rule, and
    the skeleton is one tag in one connected piece, so the clavicles cannot be told apart. **A35 is recorded as not
    run**, with this reason (19.15.8).
  - **Caveat.** The heart-lung relationship is still across two people, and the dilated HF hearts may not fit the host's
    cavity; the rules above are fixed so that neither is solved by moving the heart.
- **Epicardial fat (A31):** 0.0377 S/m with bounds 0.0122-0.0667 S/m (Keller 2010 Table I). The upper bound, 0.0667 S/m
  = 1500 ohm cm, equals the lowest of Schwan and Kay 1956's 8 fat measurements (p.668, dog in situ, 1 kHz; their
  average about 3000 ohm cm = 0.033 S/m, derived; relabel, 20 Oct 2026). Relabelled non-human:
  0.0377 is a Gabriel Part III parametric fit; it agrees with the dog in vivo average 0.035 S/m and with Rush 1963 and
  Bradley at 0.040 S/m, and Gabriel Part II's adipose curve of about 0.013-0.02 S/m in the ECG band supports the lower
  bound.
  - Thickness map from Abbara 2006 Table 1, by region, in mm at base / mid / apex level: anterior interventricular
    groove 11.2 / 8.6 / 7.3 then 7.7 at the apex; posterior (inferior) interventricular groove 9.2 / 6.5 / 6.1; LV
    anterolateral 1.0 / 1.5 / 1.7; LV inferolateral 1.3 / 2.2 / 3.5; RV diaphragmatic 1.4 / 0.2 / 1.0; acute margin
    9.2 / 7.3 / 7.8; RV anterior free wall inferior 6.8 / 4.0 / 4.7 and superior 6.5 / 3.2 / 3.1; RV superior
    para-septal 5.6 / 2.7 / 4.0; LV apex 2.8; RV apex 4.8; left AV groove 12.7; right AV groove 14.8; overall mean
    5.3 +- 1.6 mm.
  - The short-axis "superior interventricular groove" and the four-chamber "anterior interventricular groove" are **one**
    groove at different levels, not two regions. Groove values are maxima and are tapered to the neighbouring wall value
    across the groove width (inference).
  - **The +22 % age scale is replaced by Abbara's own age <= 65 and age > 65 columns**, because the stated percentages do
    not reproduce from the table means and the age effect is site-specific. Above Abbara's basal plane (RVOT, summit)
    Abbara has no level, so the **blend is stated here instead of "pre-stated" later**: fat thickness above the basal
    plane is **linear in the long-axis coordinate from Abbara's basal value at the basal plane to the RVOT- or
    summit-specific value at the valve plane** (Jakiel 2025 for the RVOT, Kuniewicz 2023 for the summit), evaluated per
    region, with no extrapolation above the valve plane. Fixed now; recorded as a model assumption.
- **Electrode misplacement bank (A34).** Wenger 1996's measured directions, not pure vertical shifts: V1 and V2 moved
  together along the upper-outer diagonal (V1 superior-rightward, V2 superior-leftward, the quadrant bisector at 45 deg
  as an inference) at 16 and 32 mm, which are Wenger's two radii (27 % and 64 % of electrodes fall within them; mean
  radial error V1 33, V2 31 mm), plus 16 and 32 mm pure superior and 16 mm inferior; V4, V5 and V6 along the
  inferior-leftward diagonal at 16 and 32 mm (mean radial error V4 25, V5 27, V6 31 mm), with a heavy-build variant at
  40 mm for V5 and V6. **V3 is never shifted on its own: it is recomputed as the midpoint of the displaced V2 and V4**,
  per the AHA definition, because Wenger shows no dominant V3 direction. An Anter-equivalent pair at +- 1 intercostal
  space uses T13's own V2-to-V4 vertical offset as the pitch (inference: T13 has no ribs). Limb arms are run separately,
  arms-only (Anter's design, LL fixed) and all four (Arya's design), with the configurations labelled: arm-torso junction
  = Anter's shoulder, current T13 = Anter's torso = Arya's modified = Kligfield's Mason-Likar. V1-V6 are recomputed with
  the moved Wilson terminal and the precordial change is reported. Doste's protocol is the coarse level of the same arm:
  13 precordial configurations, each electrode displaced within 2 cm, best-scoring configuration per site.
- **Respiration and orientation (A33).** Respiration as McLeish 2002's **coupled** one-mode poses, not independent axes:
  tidal end-inspiration = primary + 8.3 mm inferior, 1.5 mm anterior, 0.4 mm rightward, with rotations 2.7 deg about the
  anteroposterior axis and -1.4 deg about the right-left axis; deep breath = + 16.4 mm inferior, 7.1 mm anterior, 3.8 mm
  rightward, 3.8 deg about the anteroposterior axis. If the respiratory phase of the primary pose is unknown, apply half
  of each vector either way (inference). Rotation signs are undefined in McLeish, so both signs are run. The +- 10 deg
  and +- 1 cm spread is kept but **relabelled inter-subject orientation and placement uncertainty, not respiration**
  (McLeish's largest respiratory rotation is 8.0 deg with means of 0.5-3.8 deg; his largest right-left translation is
  6.1 mm). Effect sizes recorded: geometry alone gave RV 0.40 of a total 0.52 in 25 healthy humans, about 59 % of the
  variance (Hoekema 2001); +- 20 mm or +- 15 deg changes the pattern about as much as a homogeneous torso, and 10 mm
  gives about 8 % relative RMS (Bradley 2000). These spreads are reported beside the primary and are never used to
  re-score a gate after the fact.
- **Four KIT torso shapes (A37)** (Bender 2026) are run as listed, with no new values set here. **Skeletal muscle with
  subcutaneous fat (A36)** (Keller 2010; Klepfer 1997) follows the feasibility rule at the end of this section
  (deviation D9b, 20 Oct 2026; follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC).
- **Forward check before the bank runs (report only).** Every T13 electrode against Kligfield's landmarks: V1 and V2
  parasternal and level with each other; V4 one intercostal space below V2; V3 at the midpoint; V5 and V6 on V4's
  horizontal plane; RA and LA infraclavicular medial to the deltoid insertion (Mason-Likar); LL midway between the costal
  margin and the iliac crest. These are the bank's reference positions. The primary is not moved.
- **Two bookkeeping rules for the bank, fixed now.** (i) **A34's "best-scoring configuration per site"** (Doste's coarse
  level) is scored by the 12-lead Doste rho of section 10 against the primary configuration's ECG, and it is
  **report-only: the best-scoring configuration never feeds a gate verdict or a report comparator.** (ii) **A33's
  +- 10 deg and +- 1 cm spread** is run as a fixed deterministic set, not a random sample: **rotations of -10 and +10 deg
  about each of the three torso axes (6 runs) and translations of -10 and +10 mm along each axis (6 runs), 12 runs per
  heart**, each reported separately.
- **A37's four torso shapes, named deterministically (amended by deviation D17, 20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC):**
  the **first four shapes in the Zenodo record's own file ordering** of the 25 KIT shapes (Bender 2026) **other than the
  primary T_13: T_24, T_20, T_17 and T_01**. At step 0 the PC read the archive order (record 20086105, torsoModels.zip,
  md5 528b7c89...): T_13, T_24, T_20, T_17, T_01, T_05, T_09, ... (25 shapes, of which the record's description names T_13 the mean shape, plus a separate meantorso file that
  is not used), and wrote the IDs into LABNOTES before any beat; that entry is superseded by D17, and the PC enters
  A37's four IDs, T_24, T_20, T_17 and T_01, in LABNOTES at step 1. The 13:51 rule, the first four in that order, would have made T_13, the primary torso
  (9.3), one of A37's shapes (superseded; assumption 45).
- **A36 (skeletal muscle with subcutaneous fat) and A35 (lungs) need geometry T13 does not contain** (T13 is a skin
  surface only: no lungs, blood, bone or heart). At 07:30 no source geometry was named, and both were not run.
  **Deviation D9 (20 Oct 2026)** names a host torso for each and makes each **feasibility-gated**, in two parts:
  **D9a**, A35 (post-lock card 2, change 9, "Adopt all", 20 Oct 2026 11:23:21 UTC), and **D9b**, A36, which was not shown on post-lock card 2
  (follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC):
  - A35 (D9a) runs in the KCL host as written above if its step-0 checks pass;
  - A36 (D9b) stays **not run** unless a read-only step-0 check on the Moss/Wuelfers/Seemann torso (Zenodo record 8285403,
    EUPL-1.2; Torso.vtu 2,363,848,659 B; material tags Muscles_Skeleton 8, Fatty_Tissue 2, Lung 17, Blood 9; one male
    torso, source and n not stated) shows: (i) that the PC can read the VTU (meshio and pyvista are not installed, and
    meshtool's VTU input is unverified); (ii) the element count and a memory estimate that fit the 15.1 single-process
    rule within WSL's 7.7 GB; (iii) whether a skeletal-muscle fibre field exists, and if none, the fibres follow Klepfer
    1997's circumferential rule (Fig 4 p.709; assumption 53).
  - **Run at step 0 on the 13:51 file (no deviation; the rule above).** Torso.vtu carries no skeletal muscle (Material 8
    is listed in material.tab, but no cell carries it), and its 24.95 M cells need about 12-13 GB against WSL's 7.7 GB.
    **A36 is recorded as not run**, with this reason (19.15.8); its two levels below are not used.
  - A36's values if it runs: **two labelled levels, with no primary between them.** (a) The adopted 19 Oct value,
    skeletal muscle 0.202 S/m isotropic (Gabriel 10 Hz via Keller 2010), with an anisotropic variant at ratio 7 (Keller
    2010 p.1569, literature range 2.04-15.3; Klepfer 1997 p.709: 7:1 "the value cited in most literature"). (b) Burger's
    human 0.417 / 0.148 S/m (ratio 2.8; 37 C, 100-1000 c/s, 4 electrodes; n and preparation not given; via Geddes and
    Baker 1967 Table 4 p.285; the primary paper not read). Keller attributes other numbers to Burger (2.04 and 0.213),
    which conflicts with the Geddes reading; recorded. Fat as A31. Which level to prefer is settled only after Burger
    and van Dongen 1961 is read (17.2).
  - **If D9b is declined:** A36 is not run, as at 07:30; the Moss/Wuelfers/Seemann check and assumption 53 move to 17.3
    as an open item.
  - Recorded as an option for Alex, **not adopted**: one host torso for both A35 and A36, so that only one registration
    and one host effect enter.
  - Whatever is not run is recorded with its reason, and its absence stays a stated limitation of the forward model.

## 10. Measurement chain

- **Package** ecg_depth_criteria **0.4.0**, primary, with the q window at 40 ms and CSE recognition.
- **QRS end: the C1 10 % rule**, which won the 19 Oct calibration against 40 real PVCs (19 Oct 08:45 UTC). Recorded
  limitation: the surface QRS end can miss late basal activation, which is why gate 1's surface value (119.5 ms) and its
  true-mode value (145.0 ms) differ so much (REPORT-20261019T161216-f04d.md). Alex decided on 19 Oct 16:23 UTC that the
  **surface C1 value decides**, with the true end reported beside it, and that gate 1 stays failed.
  - **Standing rule, added here so the rule cannot become a post-hoc lever.** The C1 rule is re-checked on the filtered,
    noisy model chain in the plan rewrite (17.3). **No change to the QRS-end rule made after any v5.2 result has been
    seen may alter a v5.2 Aim 1 verdict.** Any such change applies **forward only**, needs Alex's word and a dated
    deviation, and is reported beside the locked v5.2 value, never in place of it.
- **The primary measurement chain per gate is the 14 Oct convention (locked 14 Oct 2026, before results), restated here
  in full.** The Kligfield constraints below govern the **comparator-chain report column**, not the primary value.

| Gate (and the quantity it scores) | Onset reference | Noise and seeds | Band and notch | Rate | The value that decides |
|---|---|---|---|---|---|
| 1, absolute paced QRS at summit + cusp | **detected onset**, baseline window 40 ms ending 5 ms before the true onset | 10 uV white noise per lead, seeds 0-9, **site value = median of 10** | 0.05-100 Hz, **notch off** | 1 kHz | surface C1 QRS duration (`qrs_duration_any_lead_ms`); true mode beside |
| 2, relative QRS (epi/endo) | **stimulus-referenced**, clean ECG, default baseline 40 ms before the stimulus | none (clean) | unfiltered | 1 kHz | mean QRS ratio over the 10 LV free-wall pairs |
| 3, Daniels MDI order | **detected onset**, as gate 1 | 10 uV, seeds 0-9, median of 10 | 0.05-100 Hz, notch off | 1 kHz | `mdi_daniels` per family |
| 4, Bazan 2006 RV | stimulus-referenced, clean | none | unfiltered | 1 kHz | median per-pair 90/10 % difference |
| 5, Bazan 2007 region q | stimulus-referenced, clean | none | unfiltered | 1 kHz | q call at 0.05 mV with CSE recognition, 40 ms window |
| 6, Berruezo (6G) | stimulus-referenced, clean | none | unfiltered | 1 kHz | median over pairs of (90 % - 10 %)/10 % |
| 7 (e), His-beat QRS | **detected onset**, as gate 1 | 10 uV, seeds 0-9, median of 10 | 0.05-100 Hz, notch off | 1 kHz | QRS duration |
| 7 (T), (a), (b), (c), (d) | activation times, not ECG | not applicable | not applicable | not applicable | activation-based values |
| 8, no-network control | **detected onset**, as gate 1 | 10 uV, seeds 0-9, median of 10 | 0.05-100 Hz, notch off | 1 kHz | median QRS, and per-family comparison |
| 9, monodomain agreement | as each measure's own gate above, identically in both engines | none (clean) | unfiltered | 1 kHz | pairs within 5 ms |

- **Reading of that table.** The clean, stimulus-referenced value decides gates 2, 4, 5 and 6; the noisy detected-onset
  median of 10 decides gates 1, 3, 7(e) and 8. Nothing here is new: it is the 14 Oct convention, copied so that no
  noise level, band or clean-versus-filtered choice is open after the run. The 19 Oct draft's general constraints
  ("low-pass at least 150 Hz, never 40 Hz", "every criterion reported both clean and chain-filtered") are **not**
  primary and did not match this convention; they now describe the report column only. Gate 1's 119.5 ms was measured
  under the 0.05-100 Hz convention, so raising its low-pass would change a failing gate's value; it is not raised.
- **Comparator-chain report column, one chain per gate** (adopted row 37; Kligfield 2007, AHA). Every gate value above
  is **also** reported through its own comparator's chain, side by side with the primary, and **the comparator-chain
  value never decides a verdict**:
  - at least 500 samples/s, preferably the comparator's own front-end rate;
  - high-pass 0.05 Hz, or at most 0.67 Hz and only with a zero-phase (forward-backward) linear filter, designed so the
    combined two-pass response meets the stated cut-off (inference: Kligfield gives no dB definition); never a causal
    0.5 Hz monitor filter;
  - low-pass at least 150 Hz, never 40 Hz;
  - a notch only where the comparator used one, and only on noise-added signals;
  - global QRS onset and offset from time-coherent multi-lead data;
  - each gate's comparator chain, named: gate 2, 4, 5 and 7 **Bazan/Durrer-era 0.05-100 Hz**; gate 6 **Berruezo
    0.05-100 Hz**; gate 1 and 3 **the spontaneous-comparator chain they already use**; report 9 **Gerstenfeld
    0.05-100 Hz with a 60 Hz notch at 1 kHz**; report 7 **Campos 20 Hz low-pass**; the MedalCare chain (0.5-150 Hz
    third-order Butterworth at 500 Hz) only where a MedalCare-derived number is quoted.
  - Every criterion is reported **both clean and comparator-chain-filtered**, with the primary marked per the table
    above.
  - Direction recorded for gate 5: a 100 Hz low-pass smooths small q waves, which moves the model away from Bazan's
    90 %, not toward a pass. (Gate 5's **primary** is the clean pace-map ECG, so this is a reported sensitivity.)
- **Hidden q waves (report only).** List the model's lead I q waves below the CSE recognition floor (under 20 uV or under
  6 ms) per gate-5 beat. The q rule itself is not changed: Bazan's own definition governs, and changing it after gate 5
  failed would be tuning.
- **Similarity metrics, reported side by side with their equations.**
  - **Gerstenfeld 2003 pooled 12-lead normalised MAD, with Gerstenfeld's own denominator** (Eq. 1 p.2047, Eq. 3
    p.2048):
    MAD = 100 x [ sum over 12 leads sum over t | (X_t - Xbar_l) - (Y_t - Ybar_l) | ]
    / [ sum over 12 leads sum over t ( | X_t - Xbar_l | + | Y_t - Ybar_l | ) ],
    with X the model and Y the reference, the **mean removed per lead** (Xbar_l, Ybar_l), and **numerator and
    denominator each pooled over the 12 leads**. Gerstenfeld's text defines it as dividing "the absolute value of the
    difference between the two waveforms by the absolute value of the sum of the area under the curve of the two
    waveforms", and calls it the **normalized** MAD: that denominator *is* the normalisation.
    - **Correction recorded.** The 19 Oct draft divided by sum | V_ref(t) | alone. For two waveforms of similar
      amplitude that denominator is about half of Gerstenfeld's, so the draft's MAD would come out about twice as
      large, and every comparison against Gerstenfeld's 12 % cut-off, the 9.5 +- 2.8 % successful-site value and the
      4.7 +- 1.7 % beat-to-beat floor would have been invalid.
    - Settings, as Gerstenfeld specifies them: a sliding alignment that minimises the 12-lead MAD; a window loosely
      bracketing the complex rather than QRS onset to offset; 1 kHz; 0.05-100 Hz with a 60 Hz notch; pacing at twice
      diastolic threshold, 2 ms pulse width; **cycle length = the tachycardia cycle length, or 400 ms when only
      isolated premature ventricular complexes were identified** (p.2047). The flat "CL 400 ms" of the 19 Oct draft
      overgeneralised it.
  - Doste 12-lead rho: per-lead Pearson r averaged through the Fisher Z transform,
    z_l = atanh(r_l), rho = tanh( (1/12) sum over l z_l ).
  - Yokokawa uses a third form (Pearson CC plus RMS on averaged leads), so a CC quoted against Yokokawa's 0.86 cut-off is
    not the same quantity as one quoted against Doste's ratios. Never quote one model number against all comparators.
  - **Floor:** Gerstenfeld's beat-to-beat MAD 4.7 +- 1.7 % and correlation 99.5 +- 0.5 %. A noiseless model reaching
    below 4.7 % is evidence of missing variability, not of a better match.
- **Pace-map acquisition settings, copied so the Campos comparison is like-for-like:** CL 600 ms, 20 Hz low-pass on the
  simulated ECGs, mean-QRS templates, the ground-truth site modelled as a 2.5 mm-radius hemisphere. The two Campos
  metrics, the model's window and the filter design are fixed in report 32 (assumptions 50 and 51; added 20 Oct 2026).

## 11. The nine Aim 1 gates, with their v5.2 amendments

Gate rules are those Alex approved on **12 Oct 2026 ("Gate all", 17:48 UTC, with the written rules approved 18:27:09
UTC)**, as amended by the later decisions that are part of the locked rules: **13 Oct 19:23 UTC** (relative QRS scored as
the ratio of group means), the **14 Oct measurement convention** (section 10), **15 Oct decisions 9 and H** (monodomain
gate locked with its bias-band fallback; Durrer (a) uncalibrated after the bundle speeds were replaced), and **19 Oct
16:23 UTC** (surface C1 decides gate 1, true end beside, gate 1 stays failed). **No gate definition and no tolerance is
changed in v5.2.** Each rule below is copied from the v5.1 brief's Table A and the 12 Oct rules draft, **with its
statistic, pair count and convention**, because an incompletely restated rule is a rule that can be reinterpreted after
the result. The amendments add pre-registered detail, comparators reported beside a gate, or calibration-check labels.

| # | Gate (rule as locked, verbatim statistic) | Hearts | v5.1 | v5.1 verdict | v5.2 amendments | Calibration check in v5.2? |
|---|---|---|---|---|---|---|
| 1 | **Absolute paced QRS**: the control heart's **median** QRS duration over the summit plus cusp sites inside **132-193 ms** (147-175 ms +- 10 %; the 10 % is unsourced and was Alex's choice, 4 Oct). Measured with the spontaneous-comparator chain (section 10): detected onset, 0.05-100 Hz, 10 uV, seeds 0-9, median of 10, `qrs_duration_any_lead_ms`. **The surface C1 value decides; the true-mode value is reported beside it** (Alex, 19 Oct 16:23 UTC) | control | 119.5 ms (true mode 145.0; summit 108.0, cusp 127.25) | FAIL | Comparator provenance recorded in 11.1 (it is a **spontaneous** band; procedure fixed, every branch leaves the band and the verdict unchanged). Site set redefined: the crescent cusp sites (8.5 item 11b) and the re-anchored summit sites (8.3) are primary, with the v5.1 sites scored beside them (11.2). Stimulus clipping, capture criterion and muscle fraction reported per site (8.7) | **Yes**, for fix 1 (the hidden-late-QRS finding prompted it), the crescents, the infundibulum cut, the summit re-anchor, the clipping rule and the site-set redefinition; and (deviation G, 20 Oct 2026) for D1 (post-lock card 1 stated that D1 makes gate 1 a calibration check; tuning-shaped toward gate 1), D5 and D6, and for fix 5's outflow blend (new fibre angles at the gate-1 summit and cusp sites); and (deviations D13-D15, 20 Oct 2026) for D13 (the mid-plane ring, as the crescents), D14 (the cut at 47.2 % of the mesh span, as the cut; D6's label passes to it, D6 being superseded) and D15 (the aortic frame, which places the crescents, the cusp sites and, through the LCA ostium, the summit sites). **Withdrawn under post-lock card 3** (deviation G, "Targeted", 20 Oct 2026 11:23:49 UTC): fix 4's 07:30 label (a speeds change, exempt by name). **Not** a check for the left-bundle sheet, D2, D4 or D11 (D2 carries no label at all under deviation D16): gate 1 scores no depth contrast, and paced beats enter them retrogradely, which is involvement, not aim (11.5) |
| 2 | **Relative QRS (epi/endo)** inside **1.0785-1.1587** (Bazan 2007 Table 2 regional range), as the **ratio of group means of QRS duration over the 10 LV free-wall 90 %/10 % pairs** (Alex, 13 Oct 19:23 UTC: ratio of means, not of medians - in v5 the control heart passed on medians, 1.0957, and failed on means, 1.0712). Clean stimulus-referenced ECG | all three | 1.0980 (CI 1.051-1.141); 1.2170 (1.190-1.239); 1.1427 (1.101-1.180) | PASS / FAIL / PASS | Rule unchanged. Reported beside it: the 6G Strauss scoring by donor sex (female, so the threshold is 130 ms), and the transseptal comparison of report 13 | **Yes**, for the left-bundle septal sheet and for the 6G cut applied to it; and (deviation G, 20 Oct 2026) for D1 and D4, and (deviation D11, 20 Oct 2026) for D11, which inherit the sheet's label. The sheet, D1, D4 and D11 are aimed at the LV subendocardial conduction that a 10 % stimulus engages, which is what the 90 %/10 % contrast measures; the 6G cut defines the LBBB-like substrate in which 6G's pairs are paced (11.5) |
| 3 | **Daniels MDI order (control)**, verbatim: **summit 90 %, vein (GCV/AIV) 90 % and aortic sinus each > RVOT > LV endo 10 %** ("summit 90, vein 90 and aortic sinus > RVOT > LV endo 10 (values in this order)", v5.1 brief Table A; PROGRESS decision log 12 Oct). `mdi_daniels`, spontaneous-comparator chain | control | **in the locked order: summit 0.605, vein 0.450, aortic sinus 0.694, RVOT 0.637, LV endo 0.362** | FAIL (**the binding failures are summit 0.605 < RVOT 0.637 and vein 0.450 < RVOT 0.637**) | **Not demoted, and not restated loosely.** The 19 Oct draft's "RVOT must sit between the septal value 0.362 and the cusp and summit values" **dropped the vein criterion, which is the one that fails**, and relabelled LV endo 10 % as "septal"; both are withdrawn and the locked wording is restored. Site families for v5.2 fixed in 11.2b. The four published MDI series are reported beside it, and Yamada 2010 (J Cardiovasc Electrophysiol 21:170) that MDI is unreliable at the cusps (MDI > 0.555 in **7 (27 %)** of 29 LCC cases, <= 0.55 in 3 of 9 epicardial cases; > 0.55 gives 67 % sensitivity and 46 % positive predictive accuracy there) is reported, not acted on | **Yes**, for the infundibulum cut, the pulmonary sleeves, the crescents, the summit re-anchor, the clipping rule, the gate-1 and gate-3 site-set redefinitions and the gate-3 site-set change; and (deviation G, 20 Oct 2026) for D5 and D6 (D6's label passing to D14, which supersedes it), and for fix 5's outflow blend; and (deviations D13-D15, 20 Oct 2026) for D13 (as the crescents and the sleeves), D14 (as the cut) and D15 (the aortic frame). **Withdrawn under post-lock card 3** (deviation G, "Targeted", 20 Oct 2026 11:23:49 UTC): the sleeve existing-muscle rule's 07:30 label (neither limb applies, 11.5), and the sheet's 07:30 label in this cell (the 07:30 11.5 and section 14 did not give it; 19.11). **Not** a check for the sheet, D1, D2, D4, D11 or D16: gate 3 scores no depth contrast, and none is aimed at the MDI order, its definition or its sites; paced beats enter them retrogradely, which is involvement, not aim (11.5) |
| 4 | **Bazan 2006 RV equivalence**: the **median per-pair** 90 % vs 10 % relative QRS difference inside **-1.9 to +6.6 %**, and smaller than the same heart's LV. Clean stimulus-referenced ECG | all three | +4.4 / +3.9 / +4.6 % (LV 9.2 / 22.6 / 16.7 %) | PASS | Rule unchanged. RV wall thickness reported as a cohort construction constant, not a measurement (report 11) | **No** (deviation G, 20 Oct 2026). Under deviation D16 (20 Oct 2026) the primary right bundle is v5.1's, unchanged, its moderator-band edge included, so it is not a change and D2 builds nothing; the 13:51 reasoning follows as history: D2, the moderator-band course, changes RV activation but is not aimed at what gate 4 measures, the RV depth effect: it is a free-running bundle that leaves the RV subendocardial network a 10 % RV stimulus engages as in v5.1, apart from the one PMJ at its end node; nor is it aimed at gate 4's sites or definition (11.5). Fix 2, fix 3 and the pose are exempt whole-model changes (11.5), although a lead-field-only change (decision 8) moved the control value from 4.4 to 3.6 %, so they are **not** "0" on this gate (section 14) |
| 5 | **Bazan 2007 region q waves**: per region, the **90 % minus 10 % difference in q-wave rate over pooled matched positions**, inside **that region's 95 % CI from Bazan 2007 Table 3 (matched pairs)**, with **five sub-checks** and **at least 20 pooled positions per region or the region is not evaluable** (12 Oct rules draft, rule 6, approved 18:27 UTC; v5.1 brief Table A ">= 20 positions"). Bands, verbatim: **basal superior q in I +67.2 (53.8-80.7); apical superior q in I +62.5 (43.4-81.6); basal inferior inferior-lead Q +25.7 (3.7-47.7); apical inferior inferior-lead Q +55.6 (30.7-80.4); basal superior inferior-lead Q reversed -15.5 (-24.8 to -6.2)**. **q = first wave at or above 0.05 mV** with the package's CSE recognition (0.02 mV for 6 ms) and the 40 ms window. **Not evaluable blocks a pass and is never reported as an improvement on a FAIL** (principle 3) | all three | basal superior q in I 5/21 vs 3/21, +9.5 points (CI -14.7 to +32.8); AHA-label variant 7/17 vs 1/17 not evaluable (< 20 positions) | FAIL | **The pass band is now numeric and complete** (the five sub-checks above; the 19 Oct draft gave no CI for the comparator it named). **Comparator settled by Alex, 20 Oct 07:23:01 UTC ("Matched bands")**: the gate is scored on Bazan 2007 Table 3 matched bands as in the 12 Oct approved rule (the v5.1 Table A cell had used the unmatched +74 points, 90 % of 162 against 13/82). The unmatched comparison is reported beside it with its own CI (**+73.7 points, Wald 64.4-82.9; Newcombe 62.7-81.1**). The model fails both on v5.1. Site map, region boundaries, eligibility and pairing pre-registered in 11.3 | **Yes**, for the left-bundle sheet, the Cassidy site map, the 18 +- 5 mm pair geometry and the summit re-anchor (summit and vein sites dominate the basal superior pool: 15 of 21 in v3); and (deviation G, 20 Oct 2026) for the T4 engine choice (11.5 already listed it), D1 and D4 (the sheet, D1 and D4 are aimed at the LV subendocardial conduction that a 10 % stimulus engages, the source of the depth contrast gate 5 scores; 11.5); and (deviations D11 and D15, 20 Oct 2026) for D11, which inherits the sheet's label, and for D15, which places the summit sites through the LCA ostium, as the summit re-anchor. **Withdrawn under post-lock card 3** (deviation G, "Targeted", 20 Oct 2026 11:23:49 UTC): fix 5's 07:30 label (neither limb applies: the LV helix is a whole-model fibre field from human data, not prompted by a fail, and arm A15, which keeps the v5.1 fibres for gate 5 only, reports the gate beside the primary and does not aim the helix at it) |
| 6 | **Berruezo 2004 in the LBBB-like heart**: direction positive for QRS, pseudo-delta, IDT and shortest RS, and size inside QRS -1 to +25 %, IDT 12-86 %, shortest RS 20-52 %, as the **median over pairs of (90 % - 10 %)/10 %** (12 Oct rules draft, rule 7). Clean stimulus-referenced ECG | 6G8DD8S5 | +22.6 / +107.0 / +51.4 / +14.2 % | FAIL (RS below the band) | Rule unchanged. Latency and transseptal reports beside it; the substrate difference stated in Limitations (Berruezo's patients: QRS 194 +- 19 ms, LVEF 24 +- 7 %, wall 10.4 +- 1.5 mm, intervals including stimulus latency) | **Yes**, for the left-bundle sheet and the 6G cut applied to it; and (deviation G, 20 Oct 2026) for the T4 engine choice (11.5 already listed it) and for D1 and D4, and (deviation D11, 20 Oct 2026) for D11, which inherit the sheet's label (the depth contrast, as for gate 2; 11.5) |
| 7 | **Durrer 1970 normal activation, His-driven beat**: (T) total LV activation 62-100 ms; **(a) at least 2 of Durrer's three early areas activated within the first 5 ms of LV endocardial activation** (approved 12 Oct, spread reported); (b) at least 90 % of LV endocardium outside the posterobasal region by 37.5 ms; (c) first RV epicardial breakthrough 20-31 ms; **(d) reported, not gated**; (e) His-beat QRS 63-88 ms (spontaneous-comparator chain) | control | T 113.3; (a) 0 / 5.5 / 8.7 ms, 1 of 3 within 5 ms (**uncalibrated in v5.1**); (b) 85.2 % at 37.5 ms (63.4 % at 30); (c) 27.5; (d) 78.7 %; (e) 76.0 | FAIL ((T), (a), (b) fail; (c), (e) pass; (d) not gated) | Rule unchanged, and **(d) is marked reported, not gated** (the 19 Oct draft listed it as if gated). **The three (a) areas are defined in model coordinates, with the patch centres corrected by deviation D3 (20 Oct 2026; post-lock card 2, change 3, "Adopt all", 20 Oct 2026 11:23:21 UTC)**: Durrer's three areas (Durrer 1970 pp.899, 901 and 906; from 4 hearts, p.901) are 10 mm-radius patches on the LV endocardial surface, written into the manifest before any beat: **posterior paraseptal** (the inferior free wall next to the septum) centred at **one third of the distance from apex to base** (Durrer: "posterior paraseptal about one third of the distance from apex to base"), measured against the mitral-annulus level the PC reports (about z 0.33; report 34 item 2); **central** at **0.50 on the mid left septum**; **anterior paraseptal** (the anterior free wall next to the septum, "just below the attachment of the mitral valve, extending at least 2 cm toward the apex") centred **10 mm below the mitral annulus** (assumption 40). **Circumferential placement, fixed now (assumption 40):** each paraseptal centre lies on the free-wall side of the AHA septal-to-free-wall boundary at its level, one patch radius (10 mm, geodesic on the LV endocardium) from that boundary; the central centre lies at the phi midway between the anterior and posterior septal boundaries at z = 0.50; the anterior centre's 10 mm is a geodesic along the endocardium from the annulus toward the apex. The boundaries' phi and each centre's (z, phi) are reported at step 0 (report 34 item 14); if a boundary or the annulus cannot be identified in a heart, the build stops and reports, and no centre is placed by eye. No patch is centred on the code's Durrer points (14_purkinje.py:92-95): the sheet reaches the v5.1 fascicle endpoints, which sit on those points, along the v5.1 fascicle paths kept beyond its envelope (deviation D11, 20 Oct 2026; the 13:51 text said its outflows attach at the endpoints), and that would make (a) circular (deep audit F06); each code point's distance to its patch is reported (report 34 item 9). v5.1's (a) is scored at both the old code points and the new patches. This restores the 12 Oct approved text ("posterior paraseptal at one third apex-base"); the 07:30 centres (0.70 for both paraseptal areas, labelled "anterior-septal" and "posterior-septal") were a transcription slip, corrected before any beat, and the labels now read paraseptal free wall. **(a) is a calibration check because the left-bundle sheet now sets the early LV pattern** - *not* because the fascicle speeds were set to it: v5.1 replaced the Durrer-tuned bundle speeds with human speeds (decision E) and Table A already marks (a) uncalibrated. RV onset and breakthrough reported as a pair with RV volume, and crista and conus timing added (report 14) | **Yes**: (a) always, for the sheet; (T), (b) and the RV items for the sheet (the RV items are timed after LV onset, which the sheet sets: REPORT.md Table C reports RV epicardial breakthrough and first RV endocardium after LV onset; 11.5); and (deviation G, 20 Oct 2026) the sheet's parts ((a), (T), (b) and the RV items) for D1 and for D4, and (a) for D3 (D2's 13:51 label on (c) and the RV items is withdrawn, below); and (deviation D11, 20 Oct 2026) the sheet's parts for D11. **Withdrawn by deviation D16** (20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC): D2's label on (c) and the RV items, because D2 builds nothing (v5.1 already has the moderator band, 7.2), and the primary right bundle, v5.1's unchanged, is not a change. **Withdrawn under post-lock card 3** (deviation G, "Targeted", 20 Oct 2026 11:23:49 UTC): fix 4's 07:30 label on (T), (b) and the RV items (a speeds change, exempt by name) |
| 8 | **No-conduction-system control**: the control heart's paced summit plus cusp **median** QRS above **193 ms** and wider than the network arm **in every site family**. Spontaneous-comparator chain | control | 230.75 ms, 7/7 families wider | PASS | Rule unchanged. **Matching no-network beats are added at the new gate-1 sites** (ledger, 11.2a), so "every site family" still means every family that exists in v5.2 | **Yes** (deviation G, 20 Oct 2026), by the site test of 11.5: gate 8 is scored on the same summit and cusp sites as gate 1, so it is a check for every change labelled for gate 1 under (ii) by those sites: the gate-1 site-set redefinitions, the crescents, the summit re-anchor, the infundibulum cut, the clipping rule, fix 5's outflow blend, D5 and D6 (D6's label passing to D14), and (deviations D13-D15, 20 Oct 2026) D13, D14 and D15. **Not** for fix 1 (gate 1 by (i) only), and not for the left-bundle sheet, D1, D2, D4, D11 or D16: gate 8 scores no depth contrast, they sit in the network arm gate 8 compares against, which is involvement, not aim, and its absolute criterion is scored on the no-network beats, which contain none of them; D1's gate-1 label is by (iii) only (11.5) |
| 9 | **Monodomain agreement**: at 27 sites (9 per heart), for pseudo-delta, IDT, shortest RS and time to the largest precordial deflection, **at least 98 of the 108 site-measure pairs within 5 ms** (= at least 90 % of 108), maximum reported; **bias-band fallback if it fails** (decision 9, 15 Oct) | all three | **72 of 108 within 5 ms, maximum 38 ms, misses mostly peak-picking swaps** (PC run 19 Oct 17:42 UTC, on the v5.1 flat-block-tuned monodomain 0.599 / 0.360 / 0.480 m/s; MEMORY.md and README-20261019T185935-93bb.md) | **FAIL** | **Gate definition and tolerance unchanged.** Six pre-registered additions: 11.4. The additions were adopted **after** this fail was seen, which is exactly why gate 9 is a calibration check | **Yes**, pre-registered |

**Tally on v5.1: 2 pass, 7 fail** (gate 2 counted once, failing if any heart fails). The "2 pass, 6 fail, 1 not
evaluable" of the 19 Oct draft came from the 18 Oct Table A, which predates the 19 Oct 17:42 UTC monodomain run; the run
makes gate 9 a scored FAIL and the tally 2 / 7, which is also what MEMORY.md and the 19 Oct draft's own prediction table
say.

### 11.1 Gate 1: comparator provenance, recorded now (and the pre-registered if/then for every case)

**The trace is done, in the cloud, before this lock closes - not on the PC.** The PC session cannot see
/mnt/project-files or the cloud Analysis plan (alex-opencarp-setup memory), so a PC step-0 trace could not have answered
it. The answer is in the cloud files:

- The 132-193 ms band is **147-175 ms +- 10 %** (notes/P/2026-10-04-open-decisions.md item 7), and the 147-175 ms
  anchors are the 4 Oct normal-heart series, **every one of them a spontaneous arrhythmia QRS**:
  **Santangeli 2015 147 and 149 ms**, **Yamada 2016 169 / 174 / 168 ms**, **Yamada 2010 (LV summit) 175 ms
  (CI 166-184)** (notes/A/2026-10-04-aim1-gaps.md lines 89-99, "Normal-heart anchors ... spontaneous idiopathic VAs").
  The 19 Oct draft cited Yamada 2007 Table 1's 140-196 ms and Yamada 2010's LCC / AMC / epicardial widths instead;
  those are not the series the band was built from, and that citation is corrected here.
- So the gate compares the model's **paced** QRS against a **spontaneous** QRS band. The 14 Oct convention already
  classes gate 1 as a spontaneous comparator, which is consistent.

**What follows, pre-registered for every case (the band and the verdict are the same in all of them):**
1. **Band spontaneous (the recorded case).** The gate is **relabelled** as comparing a paced model QRS against a
   spontaneous-QRS range. **The band stays 132-193 ms**, the surface C1 measure still decides, and the paced comparator
   is reported beside it: Bazan 2007 Table 2, LV endocardial 191 +- 41 ms and epicardial 213 +- 45 ms (by region,
   endocardial 175-197 and epicardial 192-222 ms).
2. **Band paced-derived.** Nothing changes.
3. **Mixed or untraceable.** Nothing changes: the band stays, the gate is labelled a spontaneous comparator, and the
   paced comparator is reported beside it. (This third branch exists so that no case is decided after results.)
4. **The relabel does not make gate 1 inapplicable**, and it is not a loosening: the band, the measure and the verdict
   are identical in every branch.
5. **Dropped claim.** The 19 Oct draft said the correction "can only make the gate stricter: a paced comparator sits
   above the current band". That does not hold: Bazan's paced widths come from a diseased, partly drug-treated
   population that the 4 Oct analysis rejected as unfit for a normal heart, and pace-mapping at the origin is meant to
   reproduce the spontaneous QRS. The honest statement, which replaces it: **no normal-heart paced comparator exists;
   Bazan's paced widths are a diseased-population figure and are reported only.**

### 11.2 Gate 1: the site set

- Primary: the **cusp sites placed in the new crescent muscle** (8.5 item 11b, 4 per heart) and the **summit sites on
  the re-anchored Kuniewicz construction** (8.3, 4 per heart).
- Scored beside, in the same report: the v5.1 summit and cusp sites, unchanged.
- This is a **pre-registered site redefinition**, written before any beat, and it is **an amendment Alex adopted** in the
  outflow and summit rows of the 20 Oct list ("Summit sites ... Placement, fixed before any beat"), not a new gate
  change. It is the reason gate 1 is a calibration check for the crescents and the re-anchor.
- **Capture:** a site that fails the capture criterion of 8.7 is dropped and counted, never moved.

### 11.2a Site-and-beat ledger (fixed now; step 7's acceptance is checked against this, not against v5.1's count)

| Set | Sites per heart | Hearts | Beats | Depths | Family label | Feeds |
|---|---|---|---|---|---|---|
| v5.1 paced sites | 144 | 3 | **432** | as v5.1 | as v5.1 | gates 1-6, reports |
| v5.1 His beats | - | 3 | **3** | - | His | gate 7, reports 1, 13, 19-21, 29 and 31 |
| v5.1 no-network beats | 144 | control | **144** | as v5.1 | no-network | gate 8 |
| Crescent cusp sites (8.5 item 11b) | 4 | 3 | **12** | 50 % of the built extent, after the 8.5 item 2b cap and the item 9 max rule (8.5 item 11b, assumption 35; deviation D5 (c), a follow-up item), mid-thickness; 50 % of h(theta) if D5 (c) is declined; theta in the D15 frame and s from the D13 mid-plane ring (deviations D13, D15) | cusp-crescent | gate 1 primary, gate 3 aortic-sinus family |
| Re-anchored summit sites (8.3) | 4 | 3 | **12** | as v5.1 summit | summit-reanchored | gate 1 primary, gate 3 summit family, gate 5 pool |
| Supravalvar sleeve sites (8.6) | 3 | 3 | **9** | 50 % of sleeve length from the D13 mid-plane ring, mid-thickness | supravalvar | gate 3 **report-only** family (11.2b), report 28 |
| No-network beats at the new gate-1 sites | 8 | control | **8** | as above | no-network-new | gate 8 ("every site family") |
| Gate-5 added free-wall positions, if a region is under 20 (11.3) | up to 4 | 3 | up to **12** | 10 % and 90 % transmural | gate5-fill | gate 5 only |
| Displaced-site test (report 7) | 2 displacements x 144 | 3 | **864** | +4 mm transmural, +4 mm tangential | displaced | report 7 only, never a gate |
| Intramural-origin test (report 26) | 1 focus + a 9-point endocardial pace-map grid on each surface | 3 | **57** | mid-wall septum; endocardial grids | intramural | report 26 only |
| Gate-9 sinus beats | - | 3 | **3** | - | sinus-mono | gate 9 **report-only** (11.4 item 5), outside the 108 pairs |
| Gate-9 LBBB beat | - | 6G | **1** | - | lbbb-mono | as above |
| CL 600 train subset (15.3, only if RE+ is chosen) | 9 (the gate-9 sites) | 3 | **27** | as gate 9 | cl600 | H5 report only |
| **Total under the cusp-muscle card's "Both" (05:18:46)** | | | **1 584** (1 557 before the RE+-only CL 600 subset) | | | |

- Every count above is per this table; **no beat is added at build time**. Blocks B and C of 8.9 (the cusp-muscle
  card's other options, not chosen) would drop the rows they delete; they are a record only.
- **Tangential direction rule for the displaced set (report 7), fixed now:** "transmural" is along the local w gradient;
  "tangential" is along the **local fibre direction**, and the 4 mm step is taken in the +fibre sense. Both are recorded
  per site.
- **The Sobol design (report 8)** needs its own beats; it is specified there, and it runs after scoring, as a report.

### 11.2b Gate 3: the site families in v5.2 (fixed now, before any beat)

The Daniels order is scored over five families. Their v5.2 membership, with the calibration consequence stated:

| Family in the locked order | v5.2 primary membership | Beside it |
|---|---|---|
| summit 90 % | the **re-anchored** summit sites, 90 % depth | the v5.1 summit sites |
| vein (GCV/AIV) 90 % | **the v5.1 vein-course sites, unchanged** - they do **not** move with the summit re-anchor, because the meshes carry no veins and the re-anchor gives no vein geometry | - |
| aortic sinus | the **crescent** cusp sites (8.5 item 11b) | the v5.1 valve-plane cusp sites |
| RVOT | **the v5.1 RVOT sites only.** The new **supravalvar sleeve sites do not join the RVOT family**: adding sites to a failing gate's family would redefine the gate's measure, and the adopted amendments cover gate 5 and gate 9 only. The supravalvar sites are reported as their own family beside the gate | the supravalvar family, reported |
| LV endo 10 % | the v5.1 LV endocardial sites, unchanged (this is **LV endo 10 %**, not "the septal value") | - |

- The crescent and re-anchor substitutions are **site redefinitions of a failing gate**; both are adopted changes
  (crescents: the cusp-muscle card, 05:18:46; summit: the adopted summit rows), and both make gate 3 a calibration check (11.5), with the v5.1
  sets scored beside so the redefinition's effect is visible.
- **Consequence for the sleeve prediction.** Because the sleeves are not in the RVOT family, the sleeves cannot move the
  gate-3 verdict directly; their row in section 14 is corrected accordingly.

### 11.3 Gate 5: site map, eligibility, pairing and pass bands (pre-registered)

1. **Region map**, from **Bazan 2007 p.1404** onto Cassidy 1984's site numbering: basal superior = sites 10 and 12;
   apical superior = 9 and 11; basal inferior = 6 and 8; apical inferior = 5 and 7; apex = site 1. Cassidy's septal
   sites 2, 3 and 4 fall outside Bazan's scheme, so **no model septal site may be assigned to a Bazan region**.
2. **Cassidy's sites in model coordinates (fixed now; each site stands for a 5-10 cm2 patch, not a point).** Using the
   AHA 17-segment labels the model already carries, plus the UVC apicobasal coordinate z (0 apex, 1 base):
   - **superior** = AHA **anterior + anterolateral** segments; **inferior** = AHA **inferior + inferolateral**
     segments; **septal** segments are excluded entirely (item 1); **apex** = AHA 17;
   - **basal** = the AHA basal third **plus the upper half of the mid third** (z >= 0.55); **apical** = the rest
     (z < 0.55);
   - so: basal superior = anterior/anterolateral with z >= 0.55; apical superior = anterior/anterolateral with
     z < 0.55; basal inferior = inferior/inferolateral with z >= 0.55; apical inferior = inferior/inferolateral with
     z < 0.55; apex = AHA 17. Written into the manifest before any beat.
3. **Eligibility, fixed now.** Eligible: **LV free-wall, vein-course and summit** positions (as in v5.1's pool).
   Excluded: cusp, supravalvar, RVOT and septal positions. This keeps v5.1's pool definition, so the gate's population
   is not changed by the new outflow sites. Recorded: in v3, **15 of 21 basal superior positions were summit, AIV or
   GCV-ring sites** (free wall alone gave 6), so this pool is dominated by summit and vein sites, which is why the
   summit re-anchor makes gate 5 a calibration check (11.5).
4. **At least 20 pooled positions per region, or the region is not evaluable; not evaluable blocks a pass and is never
   reported as an improvement on a FAIL.** **Step 2e counts the positions per region before any beat.** If a gated
   region comes out under 20, the shortfall is made up with **pre-registered added LV free-wall 90 %/10 % position
   pairs on the existing site grid, taken in ascending site-id order within that region** (about 4 per heart, the 12 Oct
   estimate), entered in the ledger as "gate5-fill". The gate therefore cannot become "not evaluable" through the new
   site sets, and nothing is added after a count is seen.
5. **Pairing, deterministic (fixed now).** For each 90 % position, the paired 10 % position is the one **in the same
   region whose distance from it is nearest 18 mm, inside 13-23 mm, and at most 25 mm**, taken greedily in ascending
   site-id order with each position used once. This implements the adopted amendment (**Cassidy site map plus
   18 +- 5 mm matched pairs**) deterministically.
   - **Provenance corrected.** 18 +- 5 mm is the **mean separation Bazan achieved**, not his selection rule: his rule
     was "the anatomically closest opposite endocardial PM site ... within 25 mm from each other", with the mean
     distance 18 +- 5 mm (p.1404; Table 3 gives 18 +- 5 / 18 +- 6 by region, apex 19 +- 6).
   - **Bazan's literal rule is reported beside**, as a second pairing: nearest opposite-surface position within 25 mm.
     It is not the primary, because on a 1 mm model grid "nearest" collapses to v5.1's transmurally opposite 3 mm pairs,
     which would silently undo the pair geometry Alex adopted.
   - **The achieved mean separation is reported against Bazan's 18 +- 5 mm**, per region.
   - v5.1's 3 mm transmural pairing is also reported, so all three pairings are visible; **the verdict comes from the
     adopted 18 +- 5 mm pairing**.
6. **q threshold.** Primary **0.05 mV** with the package's CSE recognition (0.02 mV for 6 ms) and the 40 ms window, on
   the clean stimulus-referenced ECG (section 10). Reported beside: 0.02 and 0.10 mV, S2 and S3 conductivity arms,
   unfiltered and the 0.05-100 Hz comparator chain, and every pair's call.
7. **Fragility band reported beside the score**: under decision 8 the 0.05 mV sign test flipped in 20 of 432 beats.
### 11.4 Gate 9: the six pre-registered additions

1. **Mesh ladder 1.0 / 0.5 / 0.2 mm, as a locally refined region, and 0.1 mm at one site in one heart.** A whole-heart
   0.2 mm mesh is not runnable on this PC and is not attempted: WSL sees 7.7 GB of RAM and 8 cores, the hearts are
   375k nodes / 1.94 M elements at a 1.05 mm mean edge, and (1.05 / 0.2)^3 = 145x gives about 54 M nodes, whose ToR-ORd
   state alone is of order 17 GB; at 16-20 s per simulated ms at 1 mm, 145x nodes with a roughly 5x smaller dt is weeks
   per beat. So the ladder is **local**, and fixed here:
   - **Refined region: a sphere of radius 20 mm around the site**, with a 10 mm graded transition shell out to 30 mm,
     the rest of the heart left at 1 mm;
   - **tool: meshtool** (the only mesher on the PC; gmsh, TetGen, meshio and pyvista are not installed), with the
     command and its arguments recorded in LABNOTES;
   - **fields on the refined mesh**: fibres, UVCs and w **interpolated from the 1 mm mesh by nearest-element
     barycentric interpolation**, junction exit times **replayed from the graph solution at the nearest 1 mm node**
     (one-way, as item 5), and **lead fields taken from the 1 mm mesh** (the forward problem is not refined, so the
     comparison isolates propagation);
   - **sites: 3 per heart, chosen by fixed seed** from the 9 gate-9 sites (seed 20261020, recorded before the run), and
     the **0.1 mm run at one site in the control heart only** (the adopted row says "0.1 mm at one site"). The 19 Oct
     "if affordable" is dropped: PC time is not a constraint (Alex, 19 Oct 18:37), memory is, so the rule is a memory
     rule, not an affordability one;
   - **memory stop rule**: estimate nodes x states x 8 bytes before each run; if the single-process estimate exceeds
     **6 GB**, reduce the refined radius in 5 mm steps and record the change; if 10 mm still exceeds it, stop and
     report.
   - Reported as a **convergence curve of last-activation time per site**, not as pass or fail. The 0.5 mm point is an
     intermediate mesh, not a refinement. Source: Niederer 2011 p.4346, at element sizes of 0.5 mm and above the error
     is approximately 180-230 % and results are "extremely difficult to interpret as either solutions to the governing
     equations or physiologically meaningful results".
2. **Flat-block tuning at every element size** (R4.4), with the tuned sigma and achieved CV published at each, plus the
   in-heart achieved speeds and signed bias of engine amendment 3.
3. **The Niederer 2011 N-version benchmark, once**: 3 x 7 x 20 mm slab, fibres along the 20 mm axis, a 1.5 mm corner
   cube **stimulated for 2 ms at 50 000 uA/cm^3 (= 50 mA/cm^3 = 50 uA/mm^3)** (Niederer 2011 Table 3, p.4339; the
   19 Oct draft wrote 50 000 mA/cm^3, a factor of 1000 too large, from a lost micro sign in the text layer - the same
   extraction renders the capacitance as "mF mm-2" where the paper means uF), the ten Tusscher and Panfilov epicardial
   model with the paper's Table 2 initial state, beta 140 mm^-1, Cm 0.01 uF/mm^2, sigma_i 0.17 / 0.019 and sigma_e
   0.62 / 0.24 S/m, at 0.1 mm and 0.005 ms. Accept if the last activation lands inside the published across-code range
   37.8-48.7 ms, and report where it sits relative to the 42.5-43 ms gold standard. This separates "our solver is
   correct" from "our engines disagree".
   - **Stop rule:** if the last activation falls outside 37.8-48.7 ms, **stop and report before any gate-9 beat**. The
     gate rule itself does not change; the benchmark failure is reported beside gate 9 as a solver-validity limitation,
     and whether to proceed, re-configure or re-tune is Alex's call, recorded with its reason before the gate-9 values
     are produced.
4. **HF hearts reported apart**, with the pooled count kept as the gate. Stated: the 1 mm comparator is not expected to
   resolve HF cross-fibre propagation, since 0.167 m/s sits close to the **0.15 m/s** Nagel 2023 (p.520) calls too slow
   to capture on a 523 um mesh, and this comparator is about twice as coarse.
5. **Sinus beats, and an LBBB beat for 6G: report-only, outside the 108 pairs.** Under the approved comparator design
   (12 Oct rules draft, rule 8) and T2c, **every engine replays the graph network's junction times as stimuli (one-way
   coupling)**, so network timing is identical in both engines by construction and these beats **cannot** test the
   network divergence Vergara describes - that needs bidirectional coupling. The 19 Oct wording "added so the network
   is exercised" is therefore withdrawn, and so is the clause that allowed the monodomain leg to carry a 1D network,
   which would have changed the locked gate-9 comparator. What these 4 beats do test is **tissue spread and the forward
   ECG under a network-driven activation pattern**, which the 27 focal sites do not cover. They are reported as such,
   they are **not** part of the 108 pairs, and they cannot change the gate-9 verdict.
   - Recorded beside them, as the reason a bidirectional test would matter: Vergara 2016 found eikonal and monodomain
     agreeing in muscle (66 against 72 ms, about 9 %) but diverging nearly twofold in the network (16 against 31 ms),
     from a bifurcation pull-and-push effect a prescribed-velocity eikonal cannot reproduce. A bidirectionally coupled
     comparator is not part of gate 9; it runs as report 33, outside gate 9, only if the T0 check finds a released
     bidirectional coupling (15.3; 17.1).
   - Misses are counted separately at sites whose early activation is junction-driven.
6. **One extra reported quantity**: for each engine, the change in total ventricular activation time caused by adding
   network detail, beside the per-site differences. Camps 2024 found 8.3 % (7 ms, 84 to 77 ms), 3.5 times their own 2 ms
   per-site threshold, from electrotonic coupling alone, which a per-site 5 ms tolerance cannot see.

**The v5.2 monodomain's cell and heterogeneity settings, stated so gate 9 compares like with like** (the gate compares
engines, so both legs must carry the same physiology): the monodomain uses **ToR-ORd with the R1.3 transmural blend
realised as a per-node interpolation between the endocardial and epicardial parameter sets in w**, the R1.4 APD target
map (28 ms, mean held) and the R1.5 HF settings (mean x 1.110, 7 ms), with **no mid-wall cell type**; the ECG is
computed from the same lead fields as the graph leg, on the fix-2 sigma_i. Propagation uses each engine's flat-block
tuned sigma at its own element size (R4.4).

**The bias-band fallback, scoped.** If gate 9 fails, the subsample bias-band fallback (decision 9, 15 Oct) produces a
**bias band for Aim 2 onset intervals**: the 12-beat bias run moves Aim 2's onset intervals to monodomain runs. It
**never changes the gate-9 verdict**, and it is not a second pass at the gate.

Recorded beside the gate so it is never loosened to make it pass: Nagel 2023 found eikonal-against-bidomain mean
absolute activation differences of 1.43 +- 1.17 ms and RE+ 1.37 +- 1.16 ms on a properly tuned 523 um mesh, both well
inside 5 ms, while Vergara 2016 found a 6 ms gap at the last-activated point even with matched velocities. So 5 ms tests
the tail, not the mean. The comparator is fixed first (tuning, mesh ladder), the location of the failures in the
activation sequence is reported, and only then may the tolerance be discussed - and only forward, never for a v5.2
verdict. Arm S3 is never varied inside the engine test.

### 11.5 Calibration-check register

**One register, keyed by change: the Targeted rule (deviation G, 20 Oct 2026; post-lock card 3, "Targeted", 20 Oct 2026 11:23:49 UTC).** A gate is a
calibration check for a change if **(i)** the change was prompted by that gate's failure, or by an audit of that
failure; or **(ii)** the change is aimed at that gate's mechanism: the physiological process the gate measures, the
definition of what it scores (its measurement rule or comparator), or the sites it is scored on. A change that only
alters the value of the scored quantity, as every whole-model change does, is not thereby aimed at it, and neither is a
change that is only part of the activation every paced beat passes through (retrograde entry into the sheet or the
network, or the network arm that gate 8 compares against), which would be the withdrawn "moved" trigger under another
name, except at the depth-contrast gates (below); or **(iii)** a label Alex accepted on a card:
post-lock card 1 stated that D1 makes gate 1 a calibration check, so
it is one. **Whole-model changes adopted on general evidence** (conductivities, blood, speeds, pose) **are exempt** for
the gates they move only incidentally, and each exemption is written with its reason below. The card names
conductivities, blood, speeds and pose, and only those are exempt; fix 5's LV helix is not exempted by name and
carries no label because neither limb applies to it (its row), while its regional outflow blend is aimed at gates 1,
3 and 8. **Four 07:30 labels are withdrawn under card 3**
("Gates stay independent tests unless a change was aimed at them"; 19.11): fix 4 on gates 1 and 7, fix 5's LV helix on
gate 5, the sleeve existing-muscle rule on gate 3 (the 07:30 section 14 column), and the left-bundle sheet on gate 3
(the 07:30 section 11 gate-3 cell; the 07:30 11.5 and section 14 gave the sheet gates 2, 5, 6 and 7 only, so the 07:30
file disagreed with itself there, and the re-issue resolves it by the rule); each row below gives the reason. The label is
fixed here, before any beat, from why a change was made and what it is aimed at, **never from what it does to a gate**:
the 07:30 trigger "or if that gate's own measure is moved by the change", which contradicted "does not depend on whether
the gate moves or passes", is withdrawn, and every "if it moves" and "if it passes" stays withdrawn. A gate that is a
calibration check for a change cannot count as validation of that change. This table and the section 14 calibration
column say the same thing.

**Depth-contrast reading (a reading of card 3's "aimed at its mechanism", fixed before any beat; deviation G, 20 Oct
2026).** Gates 2, 4, 5 and 6 each score a 90 %/10 % depth contrast between paired paced sites. That contrast exists
because a stimulus near the endocardium engages the subendocardial conduction system early, while one near the
epicardium reaches it only after crossing the wall (the transmural crossing of 14.2; it is the contrast Hyde 2015,
canine data with a model scaled to human, needed a fast endocardial layer to reproduce; 19.0). For these four gates that
engagement is the process measured, so a change aimed at the subendocardial conduction system on the paced side (its
extent, its junctions or where it couples to muscle) is aimed at the gate: the sheet, D1, D4 and D11 (deviation D11,
20 Oct 2026) on the LV side (gates 2, 5 and 6). Gates 1, 3 and 8 score no depth contrast, and for them retrograde entry into the sheet or the network stays
involvement, not aim.

**Gate 8 and the gate-1 sites (the site test; deviation G, 20 Oct 2026).** Gate 8 is scored on the same summit and
cusp sites as gate 1 (its no-network beats match the gate-1 sites, 11.2a). So a change labelled for gate 1 under (ii)
because it changes the tissue, fibres, anatomy or stimulus at those sites, or which of them count, is labelled for
gate 8 too, for gate 8's absolute criterion (median above 193 ms) as for its comparison. A gate-1 label under (i) or
(iii) alone (fix 1; D1) does not carry over.

| Change | Gates it is a calibration check for | Why |
|---|---|---|
| Fix 1, repolarisation template | **1** | (i): the hidden-late-QRS finding prompted fix 1; the splice sits inside the late QRS (R1.2) |
| Fix 2, conductivities | **none (exempt)** | Whole-model forward change adopted on general evidence (Alex's 19 Oct 18:27 pick of decision 8's Clerc-based rule); not prompted by a fail and not aimed at any gate. It moves gates 1, 3-6 and 9 only incidentally, through lead-field weighting and peak picking ("?" in section 14) |
| Fix 3, blood and walls | **none (exempt)** | Whole-model forward change: blood columns and wall values from human data; same reason as fix 2 |
| Fix 4, human in-plane speeds | **none (exempt)** | A speeds change, which post-lock card 3 exempts by name: a whole-model change on human speeds (Anderson 1993, 12 human controls; Glukhov 2012, human LV wedges; section 5.1), not prompted by a fail and not aimed at any gate, which it moves only incidentally (section 14). **The 07:30 labels on gate 1 (this register) and gate 7 ((T), (b) and the RV items; section 11, gate 7 row) are withdrawn under card 3** (deviation G, 20 Oct 2026; Alex, "Targeted", 20 Oct 2026 11:23:49 UTC). Reports A9 and Taggart are fix 4's own checks and carry no verdict |
| Fix 5, LV helix and outflow blend | **1, 3, 8 for the outflow blend; none for the LV helix** | The outflow blend (R5.2) is (ii): it sets new fibre angles in the LVOT, the summit region and the crescent muscle, at the gate-1 and gate-3 summit and cusp sites, as for the crescents, and so at gate 8's sites (the site test above) (deviation G, 20 Oct 2026). The LV helix (R5.1) is a whole-model fibre field from human data (Lombaert 2012, 10 human ex vivo DT-MRI hearts); neither limb applies: it was not prompted by a fail and is not aimed at any gate, which it moves only incidentally (card 3 exempts conductivities, blood, speeds and pose by name, not fibres, so the helix rests on the two limbs alone). **Its 07:30 gate-5 label is withdrawn under card 3** (deviation G, 20 Oct 2026; Alex, "Targeted", 20 Oct 2026 11:23:49 UTC): it rested on arm A15 keeping the v5.1 fibres for gate 5 only, and an arm that reports one gate under the old fibres does not aim the helix at that gate |
| Left-bundle septal sheet | **2, 5, 6, 7** | (ii): the sheet is the LV septal subendocardial conduction system (its extent, junctions and coupling to muscle). Gate 7: it is aimed at earliest LV endocardial activation in the His-driven beat, which (a), (T) and (b) measure and which is the time zero of the RV items (they are timed after LV onset: REPORT.md Table C reports RV epicardial breakthrough and first RV endocardium after LV onset); 7(a) is a check for the sheet, not for the replaced fascicle tuning. Gates 2, 5 and 6: it is aimed at the subendocardial conduction that a 10 % LV stimulus engages, which is what their 90 %/10 % depth contrast measures (the depth-contrast reading above). Not gates 1, 3 and 8: they score no depth contrast; every paced beat enters the sheet retrogradely, and gate 8's network arm contains it, but for these gates that is involvement, not aim; the sheet is aimed neither at the paced summit and cusp QRS, the Daniels order or the network-against-no-network comparison nor at their definitions or sites, and gate 8's absolute criterion is scored on no-network beats, which do not contain it (deviation G, 20 Oct 2026). **The 07:30 gate-3 label is withdrawn under card 3** (deviation G, 20 Oct 2026; Alex, "Targeted", 20 Oct 2026 11:23:49 UTC) for that reason; the 07:30 file carried it in its section 11 gate-3 cell but not in its 11.5 or its section 14 column. Not gate 9: both engines replay the same network's junction times (one-way, 11.4 item 5), so gate 9 compares the engines on the same activation and scores no fit of the sheet to data |
| 6G cut applied to the sheet | **2, 6** | (ii): it defines the conduction state of the LBBB-like heart (complete left intra-Hisian block with the sheet kept, 7.8), the substrate gate 6 is scored in and in which 6G's gate-2 pairs are paced |
| Retrograde PMJ delay 2 ms (v5.1, unchanged; Alex 20 Oct 07:22:39 UTC) | **none** | Unchanged from v5.1, so it is not a change; arm A22 (4 ms) would move gates 1 and 3 (7.3) |
| Infundibulum cut | **1, 3, 8** | (i) for gate 3: found while auditing the Daniels fail. (ii) for gates 1 and 3: anatomy at the sites they are scored on: it separates the RVOT (gate 3's RVOT family) from the aortic root, whose RCC sinus wall, where the RCC cusp sites of gate 1 and of gate 3's aortic-sinus family sit, is contiguous with the posterior RVOT infundibulum (Gami 2011 pp.9-10, 603 of 603 human autopsy hearts; 8.7). Gate 8 by the site test above: the RCC cusp sites are in its summit-plus-cusp population |
| Aortic crescents | **1, 3, 8** | (ii): new muscle at the gate-1 and gate-3 cusp sites (the aortic-sinus value is one of the five in the Daniels order). Gate 8 by the site test above: the cusp sites are in the summit-plus-cusp population of gate 8's beats |
| Pulmonary sleeves | **3** | (ii): new supravalvar muscle continuous with the infundibular myocardium below (Lis 2021 p.2273, citing Stamm 1998; 8.6), that is, anatomy of the RVOT outflow muscle in which gate 3's RVOT family is scored, as the infundibulum cut is anatomy at that family. The supravalvar sites themselves are a reported family, not in the RVOT family (11.2b), so the sleeves cannot move the verdict through added sites; the label (the 07:30 one) is kept on that anatomical reason, conservatively (deviation G, 20 Oct 2026) |
| Sleeve existing-muscle rule | **none** | Neither limb applies. Not (i): it came from review finding R12 (review log), which asked for one rule fixed in advance for mesh muscle above the pulmonary valve plane so that no unsourced extent sat on a failing gate; it was not prompted by the Daniels fail or an audit of it. Not (ii): the muscle it adds is the sleeve itself, which keeps its own gate-3 label (row above); beyond that the rule only leaves v5.1 mesh muscle bit-identical, so it changes no site, definition or process gate 3 scores (0 on every gate by construction, section 14). **The 07:30 gate-3 label (section 14 column) is withdrawn under card 3** (deviation G, 20 Oct 2026; Alex, "Targeted", 20 Oct 2026 11:23:49 UTC). Arm A30a (trimming) stays marked "moves gate 3" |
| Summit re-anchor | **1, 3, 5, 8** | (ii): it moves the summit sites, which are in the gate-1 set, the Daniels order (summit 90 %), the gate-5 basal superior pool (15 of 21 in v3) and gate 8's population |
| Stimulus clipping and capture rule | **1, 3, 8** | (ii): it defines which nodes a gate-1 or gate-3 site stimulates and which sites count (the capture criterion, 8.7), so it is aimed at the sites those gates are scored on; it was fixed before either gate is re-run. Gate 8 by the site test above: the stimulated set and the capture criterion apply in the no-network beats as in the network beats (a site that fails capture is excluded from its family, 8.7, whichever arm the beat is in), so the rule defines which of gate 8's sites count, for its absolute criterion as for its comparison |
| Gate-1 and gate-3 site-set redefinitions | **1, 3, 8** | (ii): pre-registered in 11.2 and 11.2b; gate 8 inherits the gate-1 site set through its matching no-network beats (11.2a) |
| Gate-3 site-set change (crescent cusps into the aortic-sinus family) | **3** | (ii): the family gate 3 scores |
| Gate-5 Cassidy map, eligibility and 18 +- 5 mm pairing | **5** | (ii): the pool and the pairing are redefined (11.3) |
| Gate-9 mesh ladder, flat-block tuning, Niederer benchmark, HF split, sinus and LBBB beats | **9** | (i): adopted after the 19 Oct 72/108 fail was seen |
| T4 engine choice (gates 5 and 6 only) | **5, 6** | (ii): those two gates are scored on the engine T4 picks (15.3). Not gate 9: gate 9's comparator is unaffected by T4 (15.3) |
| A9 RV isochrone ratio and the Taggart-style speeds (reports, not gates) | **none** | Fix 4; reports, so no verdict is involved |
| Measurement chain (14 Oct convention kept) | **none** | Unchanged as primary (section 10); the comparator chains are a report column |
| CT pose (the pose card of 05:19:07) | **none (exempt)** | Whole-model forward change chosen on anatomical grounds; it moves gates 1-7 and 9 only incidentally ("?" in section 14) |
| **D1**, upper third of the left septum junction-free | **1; 2, 5, 6, 7 ((a), (b), (T), RV items)** | Gate 1 by (iii): post-lock card 1 stated that D1 "also moves failing gate 1 toward passing, so gate 1 would be labelled a calibration check for it", and Alex chose that option ("Junction-free", 20 Oct 2026 11:22:09 UTC); D1 is tuning-shaped toward gate 1 (7.1). Gates 2, 5, 6 and 7 by (ii), inherited from the sheet: D1 sets where the sheet couples to muscle (its junctions), so it is aimed at the same LV septal subendocardial conduction system (gates 2, 5 and 6 by the depth-contrast reading; for gate 7, the sheet's parts (a), (b), (T) and the RV items). Not gates 3 and 8: they score no depth contrast, and D1 reaches them only by retrograde entry or through gate 8's network arm (its narrower gate-8 margin is movement), which is involvement, not aim. Not 7(e): it is not one of the sheet's parts |
| **D2**, right bundle along the moderator band | **none (withdrawn by deviation D16, 20 Oct 2026)** | D16: v5.1's right bundle already runs along the moderator band to the anterior RV free wall as one straight 1.5 m/s edge with no PMJ (report 34 items 6 and 12), so D2 builds nothing, and its 13:51 label, gate 7 ((c) and the RV items), is withdrawn because nothing it named is built (Alex, step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC). The 13:51 reasoning, kept as history: 7 ((c) and the RV items) by (ii): aimed at the RV activation sequence (the RB's course to the anterior RV free wall, 7.2), which 7(c) and the RV items measure; report 14 beside it. Not gate 4: gate 4 is a depth-contrast gate (Bazan 2006, the 90 % against 10 % paced QRS difference at RV sites), but D2 is a free-running bundle, with no PMJ on its free-running segment, that leaves the RV subendocardial network a 10 % RV stimulus engages as in v5.1 apart from the one PMJ at its end node, so it is not aimed at the contrast (the depth-contrast reading above), nor at transmural RV conduction or gate 4's sites or definition. Not gate 3: D2 touches neither the Daniels families' sites, their anatomy nor the MDI rule. Not gates 1 and 8, as for the sheet. D2 reaches gates 1, 3, 4 and 8 only through the network that paced beats enter retrogradely, which is involvement, not aim (deviation G, 20 Oct 2026) |
| **D3**, gate 7(a) patch centres | **7** | (ii): it redefines the (a) site population |
| **D4**, sheet envelope from the Massing digitisation | **2, 5, 6, 7** | (ii), inherited from the sheet: it sets the sheet's extent, so it is aimed at the same LV septal subendocardial conduction system (gates 2, 5 and 6 by the depth-contrast reading, gate 7 as for the sheet); the sheet's labels (gate 7: (a), (T), (b) and the RV items). Not gates 1, 3, 8 or 9, as for the sheet; not gate 1 by (iii) either, since post-lock card 1 named D1 only |
| **D5**, RCC cap, reference ring and built-extent cusp sites | **1, 3, 8** | (ii): it changes the cusp muscle and moves the cusp sites of gates 1, 3 and 8. Part (b) is on post-lock card 2; parts (a) and (c) are follow-up items (19.5); the labels stand for whichever parts are built |
| **D6**, infundibulum cut height (**superseded by D14, 20 Oct 2026**; reported beside at step 2b, not built) | **none of its own: its labels, 1, 3 and 8, are D14's** | As the cut, at 13:51. D14 replaces D6's 12.7 mm with 47.2 % of the mesh's posterior span, so the cut D6 defined is not built; the labels stay with the cut (D14 row) |
| **D7-D10**, arms A10, A40, A35 and A36, A19b | **none** | Arms decide no verdict and are never promoted after their results are seen; A19b is labelled tuning-shaped toward gate 1 (13) |
| **D11**, the sheet's outflows beyond its envelope: the v5.1 fascicle paths kept beyond it, distal edges re-joined (19.15.1) | **2, 5, 6, 7 ((a), (T), (b), RV items)** | (ii), as D4, inherited from the sheet: D11 sets where the sheet joins the LV network, so it is aimed at the same LV septal subendocardial conduction system (gates 2, 5 and 6 by the depth-contrast reading; gate 7, the sheet's parts). Not gates 1, 3, 8 or 9, as for the sheet |
| **D12**, D1 kept after the step-0 counts (19.15.2) | **D1's, unchanged: 1; 2, 5, 6, 7 ((a), (b), (T), RV items)** | Nothing changes: D1 stands as written (7.1), and the D1 row above governs |
| **D13**, the valve-plane ring on the mesh's valve discs: the mid-plane ring (19.15.3) | **1, 3, 8 (as the crescents); 3 (as the sleeves)** | (ii): it sets the outflow muscle at the crescent and sleeve sites and where the cusp and supravalvar sites sit, as the crescents (gates 1, 3 and 8, gate 8 by the site test) and the sleeves (gate 3) |
| **D14**, the infundibulum cut at 47.2 % of the mesh's posterior span; it supersedes D6 (19.15.4) | **1, 3, 8** | As the cut (and as D6, whose labels it carries) |
| **D15**, the aortic angular frame on the mesh (19.15.5) | **1, 3, 5, 8** | (ii): it places the crescents and the cusp sites of gates 1, 3 and 8 and, through the LCA ostium (8.3 step 1), the summit sites of gates 1, 3, 5 and 8, as the crescents and the summit re-anchor. The frame check is a geometric acceptance, not a gate |
| **D16**, the moderator band is already in v5.1: the primary right bundle is v5.1's, unchanged (19.15.6) | **none** | v5.1's right bundle is not a change (as the retrograde 2 ms row above); D2's gate-7 label is withdrawn (D2 row). Arm A20, the RB on the septum only, decides no verdict |
| **D17**, A37's four torso shapes (19.15.7) | **none** | An arm; arms decide no verdict |
## 12. Reports (none changes a model value or a locked verdict)

**Scope note, added 20 Oct.** Reports 1-16, 22-24, 27 and 28 come from the adopted list. **Reports 17-21, 25 and 26 go
beyond it**: they were written while reading the papers and are kept as **report-only additions**, which the change rule
(0.3) allows because a report cannot change a model value or a verdict. They are labelled here so that nothing in this
file looks adopted that was not. Report 26 needs its own beats, which are in the ledger (11.2a). No report is a gate, a
comparator for a gate, or a tie-breaker. **Reports 29-35 were added at the re-issue** (20 Oct 2026, after the post-lock
review; post-lock card 2, "Adopt all", 20 Oct 2026 11:23:21 UTC), report-only on the same terms; reports 34 and 35 run at step 0, on geometry only,
before any beat, so that the rules of D1-D6 are placed blind (report 34 item 3b follows step 2g, when the sheet exists).
Step 0 ran on the 13:51 file (report README-20261020T170855-4447.md, 20 Oct 2026 17:08 UTC). Report 34 item 15 and
report 35 (i) were added by deviations D11 and D15 and measured read-only by the PC afterwards (relayed 20 Oct 2026
17:34 UTC; followup.json, local commit a2e25a1), so that D11 and D15 were placed blind; report 35 (a), (f) and (h) are
amended by D13 and D14, and (a) and (h) also by D15, whose frame places their six positions (20 Oct 2026).

1. **Retrograde His (S-H) and HV.** Targets: HV 30-55 ms; V-H exceeds H-V by 25-65 ms; His seen retrogradely in 5 of 25
   (Akhtar 1975).
2. **Capture latency at each site.** RV endocardium 17 +- 8 ms, LV via the vein 34 +- 17 ms (Herweg 2010). Recorded
   here (correction, 20 Oct 2026; the 07:30 text called Macchi's value a 2-3 mm latency radius and the source of the
   ball): **Macchi 2004 (rat, 8 senescent hearts in situ; detailed maps from one heart): excitation latency of about
   2-3 ms paced and about 2 ms spontaneous, read from the map timings of Figs 2-3; no latency distance is stated. The
   1.5 mm radius is v5.1's code (PC run note, 16 Oct); Macchi is at most consistent with it in order of magnitude**
   (17.1). It is not run as a second latency arm. Primary
   latency comparator for outflow sites is **Yamada 2007's stimulus-to-QRS interval**: RVOT 0 ms in every case, aortic
   sinus cusp 36 +- 8 ms with a per-case range of 25-50 ms and never 0. Scored on landing the cusp sites inside 25-50 ms
   and the RVOT sites at 0, not on a single mean. Stated: the cusp stimulus-to-QRS interval is not electrode latency;
   Yamada attributes it to conduction from the cusp origin to a breakout, so in the model it must emerge from cusp
   geometry and connectivity. If it has to be imposed, that is a finding about the mesh, not a calibration.
3. **Daniels's mechanism**: earliest epicardium before QRS onset, -41 +- 7 ms against -15 +- 11 ms endocardial
   (Daniels 2006), with the four published MDI series beside gate 3.
4. **Gate 5 beside its score**: Bazan's matched pairs (his achieved separation 18 +- 5 mm; his selection rule was the
   anatomically closest opposite endocardial site within 25 mm, p.1404), q in lead I 50/58 against 11/58 (+67.2 points,
   CI 53.8-80.7); the **unmatched** comparison with its CI (145/162 against 13/82, +73.7 points, Wald 64.4-82.9); the
   model's achieved pair separation against 18 +- 5 mm; q thresholds 0.02, 0.05 and 0.10 mV; primary, S2 and S3;
   unfiltered and 0.05-100 Hz; every pair's call; the q waves below the CSE recognition floor.
5. **Stimulus to first endocardium at septal sites**: 25.7 +- 8.8 ms in controls (Betensky 2013), about 45 ms in
   Berruezo's patients.
6. **Gate 6 against Berruezo's LBBB patients**: paced QRS 241 +- 39 ms endocardial, 266 +- 25 ms epicardial
   (+12 +- 13 %).
7. **Depth signal against pace-map resolution, with a Sobol share for depth.** Two separate lines, because they are
   different papers measuring different quantities: Campos 2026, clinical pace-map resolution 4.02 +- 2.81 mm at
   correlation above 0.99 (the resolution curve comes from 5 patients with structural heart disease, 1 ICM, 3 NICM and
   1 mixed; supplement p.2), in-silico localisation 8.2 mm [IQR 6.9-12.0] on 107 of 162 points in 16 of 17 cases after
   excluding points with maxCC below 0.85 (the abstract's "270 clinical pace-mapping locations" is the pre-exclusion
   count: main e2305, 270 points, 162 after signal-quality exclusion; noted 20 Oct 2026) (11.0 mm [7.9-14.2] on all 162 points; model-versus-clinical maxCC 0.90
   [0.88-0.92]; main e2307 and supplement p.8 Table S2; n added 20 Oct 2026), target area 35.9 mm2 (IQR 6.5-161.0) at
   the 99 % isoline and
   453.3 mm2 (201.9-1109.5) at 95 %; Campos 2025 (Heart Rhythm 22:1790-1799, "(c) 2024" in the PDF, which prints no
   online date, doi
   10.1016/j.hrthm.2024.12.036; cited as 2025 in Campos 2026; citation corrected 20 Oct 2026; human, pacing sites LV
   endocardial n = 5, LV epicardial n = 1, septal n = 3, RV apical n = 15), abstract p.1790: in-silico localisation
   accuracy for LV pacing 9.5 mm from body-surface potentials and 12.2 mm from ECGs against 30.8 mm for ECG imaging;
   for RV apical pacing 26.1 mm from body-surface potentials, 30.9 mm from ECGs and 29.1 mm from ECG imaging. Reproduce
   Campos's Figure 4 in
   silico: mean 12-lead QRS correlation between every pair of simulated sites in a neighbourhood, plotted as mean 3D
   separation against correlation threshold at 0.90 / 0.92 / 0.94 / 0.96 / 0.98 / 0.99, overlaid on the digitised
   comparator curve (about 7.1 / 5.8 / 5.4 / 4.6 / 4.1 / 4.02 mm; the 4.02 +- 2.81 mm at 0.99 is exact from the text).
   **The test that answers the project's question**: displace each site 4 mm transmurally (along the local w gradient)
   and 4 mm tangentially (**along the local fibre direction, in the +fibre sense**, 11.2a) and compare the correlation
   drop; the depth signal exists only if the transmural drop exceeds the tangential one at the same displacement. The
   864 displaced beats are in the ledger. Context: Bogun 2008's 180 mm2 and 7.6 mm radius at r >= 0.94; Kadish 1991's 5 mm; and depth gave
   no significant ECG change in Gillette 2025's model.
8. **Sobol sensitivity analysis: design fixed now, run as a report after scoring.**
   - **Factors (6), with ranges:** (i) electrode displacement radius 0-32 mm (the A34 bank); (ii) torso shape, the four
     A37 shapes as a discrete factor; (iii) heart pose, +- 10 deg and +- 10 mm (A33); (iv) helix profile, endocardial
     +56 to +76 deg with epicardial -31 to -51 deg (Lombaert +- 1 SD); (v) cross-fibre speed 0.18-0.28 m/s control and
     0.13-0.21 m/s HF; (vi) transmural speed 0.40-0.56 m/s control and 0.28-0.39 m/s HF.
   - **Sampling and estimator:** Saltelli's extension of the Sobol sequence, **N = 128** base samples, so
     N x (2k + 2) = 1 792 evaluations per heart; first-order and total-effect indices by the Jansen estimator with
     bootstrap 95 % intervals (200 resamples).
   - **Beat budget:** one paced beat per sample at one site per heart (the LV free-wall 50 % site), 1 792 beats per
     heart. It sits outside the 11.2a ledger because it is a report, it runs **after** step 8, and if it is not run that
     is recorded; nothing in this lock depends on it.
   - **Pre-registered expectation** (Campos 2026's measured ordering): electrode and torso specification first (8.2 to
     12.5 mm for standard electrodes on the correct torso, to 57.3 mm for a generic torso), conduction personalisation
     after it (to 9.4 mm, not significant). Written down first because it is counter-intuitive and directly adverse to
     a study run in a mean torso.
   - **Scar is dropped from the pre-registered ordering**: Campos ranks it second (to 10.6 mm overall, 18.9 mm in
     ischaemic cardiomyopathy), but **the pilot hearts have no scar** (17.3), so in v5.2 it is marked untestable rather
     than pre-registered as a factor.
9. **Exit against origin**: Gerstenfeld's mean absolute difference 9.5 +- 2.8 % at successful sites with the full
   specification of section 10; good pace maps 7.3 mm from the origin (Bogun 2008). Displacement leg from Yamada: when
   the best pace map is at a breakout rather than the origin, the two are 11.9 +- 3.0 mm apart in cusp cases (4 of 15,
   27 %), 16.4 +- 8.0 and 18.9 +- 1.8 mm in the other groups, and in 3 of 9 summit cases (33 %) the excellent pace map
   is at the transmurally opposite endocardial site.
10. **Each comparator's signal chain**, with Zheng 2020's own recorded noise, scored beside the unfiltered ECG.
11. **Wall thickness, perpendicular, per AHA segment.** Primary comparator **Kawel-Boehm 2020 Table 26** (short axis, 16
    AHA segments, sex-specific, pooled bSSFP at 1.5 T); Table 27 (long axis) only as a sensitivity, since long-axis
    values are significantly greater at base and mid. Convention printed on every row: compact myocardium only,
    end-diastole, papillary muscles and trabeculations excluded, lower and upper limits = mean +- 2 SD, not percentiles.
    **The RV leg is dropped**: the review contains no RV wall-thickness norm, and in this cohort the RV wall is assigned
    by distance maps at a user-specified constant, so it is a construction parameter and is reported as one (3.5 mm).
    Phase caveat printed beside every verdict (section 9.1).
12. **The cohort's own benchmark activation**, pinned to the six-way group each heart belongs to, naming the source file
    (**dataset_info.csv, Zenodo record 19351401** - the version record the stored file came from, dated 31 Mar 2026,
    which is the current version of concept DOI 10.5281/zenodo.17048090; the 17 supplementary files hold no per-case
    metadata):
    - 6G8DD8S5, group HF-W_F (female, 64, HF with wide QRS, n = 6): TAT_LV 186.73 +- 10.91, TAT_RV 192.89 +- 13.47,
      TAT_V 197.02 +- 9.66 ms; Vol_LV 193.11 +- 46.89, Vol_RV 136.24 +- 20.41 mL; age 59.17 +- 6.94 y.
    - 7D98EVAR, group HF-N_F (n = 6): 185.32 +- 11.18, 194.64 +- 16.39, 201.81 +- 10.29 ms; 172.96 +- 74.09,
      137.24 +- 40.86 mL.
    - Y5HYEDL4, group C_M (n = 13): 197.03 +- 10.55, 200.59 +- 16.63, 206.93 +- 13.41 ms; 179.63 +- 36.31,
      188.65 +- 25.74 mL.
    - Group wall volumes: female HF 297.3 +- 50.0, male control 319.0 +- 43.7 cm3.
    - Context: the cohort's own ANOVA shows sex explains more of the simulated activation time than heart failure does
      (eta squared 0.27-0.35 against 0.00-0.18; TAT_LV condition p = 0.499), so sex-matching comes first.
    - The cohort's own benchmark settings: 1 m/s, 40 % cross-fibre, from the sinus node; activation-to-QRS correlation
      r = 0.649 in controls and none in HF (Solis-Lemus 2026).
13. **LBBB septal crossing in heart 6G, split by definition** (the four sources measure four different quantities up to
    30 ms apart, and the model's value is 23.4 ms):
    - **Primary comparator**: QRS onset to earliest LV endocardial activation, Derval 2017 eLVAT 38 +- 15 ms (LBBB,
      n = 11, contact mapping). The model's 23.4 ms is that quantity.
    - Beside it: Auricchio 2004 time to LV breakthrough, bimodal (under 20 ms in 9, over 40 ms in 15 of 24);
      Vassallo 1984 RV apex to earliest LV 33 +- 17 ms; Upadhyay 2019 RV-at-His to the latest LV septal electrogram
      51 +- 15 ms in complete block against 4 +- 15 ms with intact Purkinje activation; Strik 2013 (dog) LV septal pacing
      to earliest RV septal 44 +- 16 ms and 67 +- 9 ms.
    - **Verdict printed**: 23.4 ms is about 1 SD below Derval's LBBB mean (derived: (23.4 - 38) / 15 = -0.97 SD), sits
      inside Auricchio's nearly empty 20-40 ms gap between the two human modes, and is below the over-40 ms Upadhyay
      reports in every complete-block patient. A finding about v5.2, not a reason to change a speed.
    - Also reported: Auricchio saw a line of block in 23 of 24 and Derval in none, so the model gets no credit for
      matching Derval (section 7.8).
14. **RV onset and breakthrough as a pair, with RV volume, and crista and conus timing** (Durrer 1970): a pure RV timing
    shift cannot pass both RV sub-checks.
15. **Initial phase, inside the engine test**: wavefront shape at 2, 5 and 10 ms, with the initial-slope comparison.
    **The Prisco 2024 main article is in the project** (prisco-et-al-2024-rate-of-change-of-initial-intrinsicoid-
    deflection-..., JACC CEP 2024;10:1150-1160), so its values are restored here, as the adopted list says
    ("Confirmed from the main article"):
    - **all 12 leads, first 30 ms: epicardial 4.6 +- 2.2 against endocardial 9.9 +- 4.8 mV/s, P = 0.0299**; average
      slope 6.3 +- 3.1 against 11.4 +- 3.7 mV/s, P = 0.0353 (**journal p.1153**, not p.1154 as the notes say);
    - limb leads, initial: 3.2 +- 1.7 against 8.4 +- 5.4 mV/s, P = 0.0246; **precordial, initial: 6.2 +- 3.2 against
      11.3 +- 7.8 mV/s, P = 0.3996, not significant** (**Table 2, p.1156**);
    - n = **26** patients with VT in nonischaemic cardiomyopathy (8 epicardial, 18 endocardial); Table 3 cut-offs 4.5
      and 6.0 mV/s.
    - Kept beside them, the supplement's bootstrap AUC table: epicardial-VT prediction, initial against average slope,
      all leads 0.88 [0.72, 0.99] against 0.86 [0.63, 1.0]; limb 0.89 [0.74, 1.0] against 0.87 [0.64, 1.0]; precordial
      0.72 [0.50, 0.91] against 0.78 [0.52, 1.0]. The initial-over-average advantage is stated as marginal (0.01-0.02
      AUC with heavily overlapping intervals), and **no claim is made that the precordial initial slope discriminates
      depth**, since both its AUC interval and its P value include chance.
16. **Intramural Purkinje, the human conflict** (section 7.6).
17. **Network against the Camps 2024 comparator**: Purkinje velocity against their 2.0-4.0 m/s human bounds; the model's
    effective PMJ spacing against Garcia-Bustos 0.33-0.55 PMJ per mm2 (pig) and Camps's 0.5 cm dense and 1 cm sparse
    candidate spacing; the 4 ms antegrade delay against the 3-25 ms target with its resistor implementation
    (R_PMJ = 500 kOhm, N_PMJ = 60); root-node-equivalent density against their 2.5 cm RV and 1.5 cm LV sampling.
18. **How much of a gate failure can be blamed on the network** (bounding statement, Camps 2024): across 4 controls and
    2 hypertrophic patients, differences between Purkinje configurations were under 0.05 in correlation in most cases;
    root nodes alone against a minimal network gave correlation 0.99 and a 1 ms QRS-duration difference; 8 stimulation
    points against 1266 gave 0.95. This bounds how much of gates 5 and 6 can legitimately be attributed to network
    detail rather than to repolarisation, conductivity or geometry.
19. **Retrograde LV Purkinje timing (6G only)**: the fraction of LV Purkinje nodes activating after the local myocardium
    at their insertion, and the mean delay. Human target: in complete block the Purkinje potentials follow local
    ventricular activation at every recorded left-septal site (Upadhyay 2019), and no Purkinje potential precedes the LV
    breakthrough in any LBBB patient (Derval 2017, 0 of 11, against 17 of 18 in narrow QRS and 23 of 23 in non-specific
    conduction delay).
20. **Delta LV time and septal QLV for 6G** (Upadhyay 2019): latest minus earliest LV septal electrogram peak along a
    base-to-apex line, target +45 ms (IQR 30-60) for complete block against -37 ms (IQR -50 to -27) in controls and
    -37 ms (IQR -46 to -18) with intact Purkinje activation (Upadhyay 2019 p.12; corrected 20 Oct 2026), with the
    **sign** reported; septal QLV as a percentage of QRS, 67 +- 9 % against
    44 +- 11 %.
21. **LV endocardial breakthrough count, site and total activation for 6G**: count 1 +- 0 in LBBB (Derval, single in 11
    of 11; Auricchio 22 of 24 single septal; Vassallo 12 of 18 single septal); site mid-septal 73 % and apical-septal
    27 % (Derval), apical 14 / basal 4 / middle 4 of 22 (Auricchio), mid-third 9 and apical-third 3 of 12 (Vassallo);
    LV total endocardial activation 117 +- 28 ms (Derval), 91 +- 36 ms = 52 +- 16 % of QRS (Vassallo), 94-107 ms
    (Auricchio); latest site basal lateral in 11 of 11 (Derval), inferobasal or lateral in 12 of 18 (Vassallo).
22. **Forward-model check**: lead I R and aVR S against Arya; exact electrode positions; one torso refinement. Never
    used to scale signals. With the electrode-bank human reference per heart: V1 and V2 R change per intercostal space
    against about 0.1 mV per interspace; outflow-site V1 and V2 R/S ratios at +- 1 space against Anter's pooled RVOT
    0.17 going to 0.11 and 0.46 and LVOT 0.32 going to 0.05 and 1.1; lead I R change torso against shoulder
    (-0.20 mV, Anter) and torso against distal limb (-0.087 mV, Arya); aVR S +0.155 mV (Arya); the transition-zone shift
    at 2 cm vertical (75 % of patients, Herman via Wenger).
23. **Lin 2016 aVL/aVR Q-ratio ordering** (report, not a gate). Scored on **strict monotonic ordering** of the four
    simulated group means (aortic sinus of Valsalva < subvalvar < GCV/AIV < epicardial) plus only the two outer bands
    (sinus mean <= 1.415, epicardial mean > 1.740), with every simulated value inside Lin's observed range
    0.373-3.000. The two middle bands are treated as non-discriminating, because Lin's Figure 2 shows the subvalvar
    group (about 1.40-1.78) and the GCV/AIV group (about 1.46-1.80) overlapping across both middle boundaries. Group
    means for reference: 1.06 +- 0.26 (n = 20), 1.47 +- 0.89 (n = 15), 1.61 +- 0.08 (n = 16), 2.10 +- 0.35 (n = 15),
    P < 0.001. **Table 2's SDs are not used as tolerances** (the subvalvar SD of 0.89 contradicts the figure). The model
    publishes its own definition of the ratio, since Lin never defines it: the absolute Q amplitude in aVL divided by the
    absolute Q amplitude in aVR, from the isoelectric baseline to the Q nadir, averaged over three beats as Lin did.
    Lin gives no filter settings (only a BARD system displayed at 100 and 200 mm/s), so this report carries no
    comparator-specific filter: it is run unfiltered, said to be unfiltered, and its sensitivity to a plausible
    0.05-150 Hz band is reported with the forward-model arms. The ratio-against-distance correlation is reported against
    r = 0.863, not gated. **Second comparator for the identical quantity**: Yamada 2010 (J Cardiovasc Electrophysiol
    21:170), aorto-mitral continuity
    0.9 +- 0.4 < LCC 1.2 +- 0.3 < epicardial (GCV/AIV) 1.6 +- 0.8, with > 1.4 as the published epicardial threshold;
    the ordering is scored under both limb-electrode placements.
24. **A9, the 10-ms isochrone ratio. Clinical comparator: Acosta 2015 directly. In-silico comparator: Doste 2019
    Table 2 (p.10)**, which is where the old "Doste 1.86" benchmark came from and which **does** compute the ratio
    (OT-RBM: RVOT 1.86 +- 0.22, LVOT-RCC 1.02 +- 0.2, LVOT-LCC 0.74 +- 0.25; ST-RBM RVOT 0.57 +- 0.16, in 9 patients,
    with their clinical values beside). It is **Doste 2020**, not Doste 2019, that cites Acosta once in its introduction
    and never computes the ratio; the 19 Oct re-attribution rested on that confusion and is corrected here. Clinical:
    RVOT site of origin 1.97 +- 1.2 (n = 14) against LVOT 0.79 +- 0.49
    (n = 23), P = .001, cut-off 0.8 or less rules out an RVOT origin with 68 % sensitivity in the text and 77 % in
    Table 2, 100 % specificity in both. **The text-against-table discrepancy is flagged, not averaged**, and the SD is
    printed as 0.49 as in the table (0.4 elsewhere). Second leg, since Acosta's own algorithm needs both: the 10-ms
    isochronal **area**, LVOT 3.8 +- 2.4 against RVOT 1.1 +- 0.7 cm2, cut-off 2.3 cm2 or more (82.6 % sensitivity, 92 %
    specificity). Measurement constraints copied: the septal RVOT endocardial map only, not the whole chamber and not the
    epicardium, during the PVC, from a contact map with a 6 mm fill threshold and a 3.5 mm tip, with "longitudinal"
    meaning parallel to the RVOT long axis; computed on a comparably sampled septal-RVOT endocardial patch, not on the
    full-resolution mesh. Stated: this is primarily a test of the RVOT **fibre** field, since Acosta's histology
    attributes the long thin RVOT isochrone to longitudinally disposed subendocardial fibres and the round LVOT pattern
    to circumferential or spiral LVOT fibres. **But the RV fibre field is bit-identical to v5.1 in v5.2 (R5.3), so this
    septal-RVOT report cannot test fix 5**: it is paired with **fix 4** (and with fix 2 for the ECG leg). Fix 5 shows in
    the **LVOT** leg of the same measure, which is reported separately. The 19 Oct pairing with fix 5 is corrected.
    v5.1 values for reference: 1.10 / 0.97 / 1.23, areas 155 / 112 / 122 mm2.
25. **Opthof 2017 transmural repolarisation profile** (report, not a gate): the model's LV transmural repolarisation-time
    and activation-recovery-interval profiles against the three intact human hearts, whose transmural gradients were
    about +7 ms (heart 1, not significant), +47 ms (heart 2, p < 0.005) and -17 ms (heart 3, not significant); heart 1
    LV ARI endocardium about 275 against epicardium about 254 ms; mean ARI 252 ms (range 200-298) at CL 700; whole-heart
    activation-to-recovery slope positive (0.19 / 1.15 / 0.15) but epicardium-only slope negative
    (-1.53 / -1.92 / -0.14). Noted: Opthof's recovery time corresponds to APD80, not APD90.
26. **Intramural-origin test** (Yokokawa 2016's definition, so the model can be scored on it): place a focus mid-wall in
    the septum and check that neither endocardial surface yields a matching pace map (fewer than 10 of 12 leads), that
    the two surfaces' earliest activation times fall within 8 ms of each other, and that the single-site correlation at
    the earliest breakthrough falls at or below 0.86. Clinical reference: at the true intramural origin the activation
    was 34 +- 10 ms pre-QRS against 25 +- 7 ms at the nearest endocardial breakthrough (n = 7, P = .022), pace-map score
    10.5 +- 0.4 against 5.0 +- 3.2 of 12, correlation 0.95 +- 0.02 against 0.82 +- 0.1. Derived context: the 9 ms
    origin-to-breakout offset corresponds to about 4.3 mm at the model's 0.48 m/s transmural speed.
27. **Bulk conductivity report** (R2.6) and **the summit and cusp amplitude change from fix 3 alone** (R3.6).
28. **Muscle fraction of the stimulus ball at every site** (8.7), with the crescent and sleeve resolution flags.
29. **Left-septal activation sequence against Upadhyay 2019** (added 20 Oct 2026, report only). A line from the sheet
    origin (the model's left-bundle potential site) along the left septal surface toward the apex, with 12 sample
    points at 2 mm spacing (assumption 49: Upadhyay's catheter is a duodecapolar 2-2-2 mm one, p.6, but its length is not
    stated in the text read). Output per His beat: delta LV time, whose **magnitude** is the latest minus the earliest
    myocardial (ventricular) local activation time at the 12 points, not sheet or Purkinje node times (Upadhyay p.8:
    the "absolute difference" between the earliest and latest ventricular electrogram peaks), given the **sign** of
    t(apical-most point) - t(basal-most point), so that **negative = apical-first** (the sign rule is an inference from
    Upadhyay's reported negative values in distal-to-proximal patterns, stated as such); and a flag for whether the
    sequence is monotonic distal-to-proximal. Comparators (Upadhyay 2019
    p.12, human in vivo): the control and 7D His beats against controls -37 ms (IQR -50 to -27) and intact Purkinje
    activation -37 ms (-46 to -18); 6G (left intra-Hisian cut) against complete block +45 ms (30-60), "early basal or
    mid, rather than apical". Caveats: the V shape is part of Upadhyay's definition of intact Purkinje activation (p.7),
    so only delta LV time is a measurement; the patients were referred for devices or VT ablation, not healthy people.
    (Report 20 corrected 20 Oct 2026.) It is the most direct human observable for D1 against arm A39. Never a gate.
30. **Wavefront voltage per direction** (added 20 Oct 2026, report only, beside R2.6). sigma_i / (sigma_i + sigma_e) per
    direction and per conductivity set, multiplied by the upstroke amplitude of the R1.2 tissue template that drives the
    QRS source (about 120 mV, measured from the template), not by an R1.1 cell-bench value. Fractions (derived from
    R2.1-R2.5): primary 0.218 along, 0.048 / 0.025 across (control / HF), 0.208 / 0.102 transmural; A8 (Clerc) 0.218
    along, 0.076 across; S3 (Roberts and Scher) 0.746 along, 0.426 across. Comparators, labelled as what they are:
    Roberts 1979 p.704, measured epicardial wavefront voltage defined as the maximum difference over 2 ms, which Roberts
    calls method-dependent (Fig 4B): 46 +- 18 mV along and 22 +- 11 mV across, 9 dogs in situ; Roberts and Scher 1982
    p.348: 74 +- 7 / 43 +- 6 mV, a regression output at an assumed A = 100 mV from which S3 itself was derived, so S3
    matches it by construction and it is **not an independent check of S3**; Clerc via Roberts 1979 p.707: 20 / 7 mV,
    calculated at 100 mV. Changes no value.
31. **Sinus-beat QRS voltage against Rijnbeek 2014** (added 20 Oct 2026, report only; control heart only, the donor
    being male, 25 y). Sokolow-Lyon and Cornell voltages of the control heart's His-driven beat (graph engine, with the
    gate-9 monodomain sinus beat beside it) against Rijnbeek 2014 Table 3 (PDF p.4; 13,354 individuals aged 16-90 from
    four Dutch population studies), male 20-29: Sokolow-Lyon 2.68 mV median (98th percentile 4.28); Cornell 1.21 mV
    (2.78). Table 3 gives medians and 98th percentiles only, so the report can show the model's distance from the median
    and flag a too-large amplitude but **cannot flag a too-small one**, which is the direction that matters for the
    absolute 0.05 mV q call; the 2nd-percentile and per-lead limits are in the supplement, which is not in the project
    (17.2). Report 22 already compares lead I R and aVR S with Arya 2011 (human OT-VT, n = 20). Never used to scale
    signals.
32. **Campos 2026 pace-map scoring with both of its metrics** (added 20 Oct 2026, report only). (a) The Figure-4
    resolution metric: the mean of the 12 per-lead correlation coefficients over 150 ms of data from 10 ms after the
    window start (supplement p.2). (b) The InSPM metric: per-lead Pearson r on signals trimmed from onset to the QRS
    peak and aligned on the pacing stimulus, the 12 values sorted and the top 10 averaged (supplement p.5). **The
    model's window** for (a): 150 ms from 10 ms after the stimulus (assumption 50; the model has no Carto
    window-of-interest). **The filter**, applied identically to both beats of every comparison: a zero-phase
    (forward-backward) Butterworth low-pass, 2nd order per pass, designed so that the combined two-pass response is
    -3 dB at 20 Hz (assumption 51; Campos states only "a low-pass filter at 20Hz", supplement p.5). Each correlation is
    quoted only against the comparator whose metric it uses (section 10), and thresholds do not transfer between
    model-model and model-clinical comparisons.
33. **Bidirectionally coupled Purkinje network in a monodomain run** (added 20 Oct 2026, report only, outside gate 9).
    Run only if a read-only T0 check (15.3) finds a released, documented bidirectional Purkinje-myocardium coupling in
    the installed openCARP; the openCARP Q&A (q2a/1112) recorded a Purkinje system only as a work-in-progress branch as
    of Dec 2024. If none exists, the absence is recorded as a limitation and **no coupling is built**: a home-made
    1D-in-3D coupling would need junction parameters (junction resistance, junction node count) with no human source,
    fitted to reproduce the delays of 7.3, which is calibration and would have to be labelled so. The report changes
    neither gate 9 (whose comparator stays the approved one-way junction replay) nor 7.1, and it tests engine timing in
    the network, not whether a sheet or a network is anatomically right (Vergara 2016: eikonal 66 against monodomain
    72 ms in muscle, from the pull-and-push effect).
34. **Step-0 conduction geometry** (added 20 Oct 2026, report only; geometry, before any beat). Per heart:
    1. UVC (z, phi) and AHA segment of the v5.1 fascicle endpoints and of the code's three Durrer points
       (14_purkinje.py:92-95);
    2. the z of the mitral annulus, the aortic valve, the septal crest and the moderator-band septal insertion, and the
       septal crest-to-apex length in mm;
    3. the z of the His exit (the sheet origin), of the planned 10 mm line and 33 mm sheet end, and of the
       septal-outflow node; 3b, the sheet nodes per septal third, above and below the D1 line, is completed after step 2g,
       when the sheet exists;
    4. LV distal-network junctions per AHA segment and per septal third, those above the D1 line counted per heart and
       per AHA segment, and the LV and RV junction densities per cm2;
    5. whether the mesh carries papillary muscles or trabeculae;
    6. the distance from the moderator-band insertion to the anterior RV free wall;
    7. the 0.9 network cap in mm below the mitral annulus;
    8. whether v5.1's LB_TRUNK and FASCICLE nodes carried PMJs;
    9. the code's Durrer points and their distances to the corrected gate-7(a) patch centres;
    10. the definition of UVC z = 1 (valve plane, septal crest or MV+TV centre) and the septal crest-to-apex geodesic
        length, so that the D1 line can be placed;
    11. the Upadhyay sampling line and its 12 points (report 29);
    12. the length of v5.1's moderator-band edge against Lee and Hur's mean 13.6 mm and against assumption 54's 37.8 mm
        (report only, deviation D16, 20 Oct 2026; 14.7 / 18.2 / 10.1 mm at step 0); the candidate moderator-band end
        node (withdrawn assumption 47; **report only** under D16: the PC's step-0 construction, nodes 369808 / 37002 /
        26551, chains 12.0 / 16.0 / 9.0 mm) and its distance from the insertion; and the insertion's
        level on the septum (top fifth, upper, middle or lower third) against Lee and Hur's origins (7.2; 0.82 / 0.63 /
        0.82, lower, middle and lower third, at step 0);
    13. the anterior-posterior distance between the v5.1 anterior and posterior fascicle endpoints on the left septal
        surface at their level, and each endpoint's position against the 17.8 / 4.8 mm envelope of 7.1 (inside or
        outside, and by how far) and against the centred 11.3 / 11.3 mm envelope that applies if the placement is
        declined (7.1); the v5.1 LV septal node footprint width, and its anterior-posterior midpoint (the centre used if
        the placement is declined, interpolated linearly between these levels, 7.1), at 2.5 mm steps along the sheet's
        base-to-apex direction from the His exit and at the sheet's 33 mm end; and the septal surface's
        anterior-posterior extent at the envelope's widest level. If either endpoint lies outside the envelope that
        applies under the placement answer (either envelope while that answer is open), or the envelope runs off the
        septal surface, the build stops after step 0 and the attachment goes to Alex; the envelope is not widened; if no
        footprint midpoint can be given at one of these levels, a declined placement also stops the build after step 0
        (7.1). **Answered (deviation D11, 20 Oct 2026):** at step 0 on the 13:51 file the posterior endpoint lay outside
        the envelope in all three hearts and the anterior one in two (7.1), the build stopped after step 0, and Alex
        fixed the attachment on step-0 card 1 ("Keep tails", 20 Oct 2026 17:32:26 UTC); the envelope was not widened;
    14. the phi of the anterior and posterior septal-to-free-wall boundaries at z = 0.33, at z = 0.50 and 10 mm below the
        mitral annulus, and each gate-7(a) patch centre in (z, phi) (section 11, gate 7; assumption 40). If a boundary or
        the annulus cannot be identified, stop and report; no centre is placed by eye;
    15. (added by deviation D11, 20 Oct 2026; measured read-only by the PC after step 0, relayed 20 Oct 2026 17:34 UTC,
        analysis/v52_2026-10-20/00_step0/followup.json, script step0_followup.py, local commit a2e25a1) **the D11
        topology**: for each v5.1 fascicle path (anterior, septal and posterior; His to endpoint along the LB_TRUNK and
        FASCICLE edges), the node where it first leaves the envelope (its s, a and mesh node), the kept tail's length and
        node count beyond it, and whether the endpoint lies inside the envelope; where the v5.1 DISTAL edges meet
        LB_TRUNK or FASCICLE nodes, and how many are re-joined to the sheet; whether the v5.1 LV network stays connected
        with the trunk and fascicles removed; and whether every v5.1 LV distal-network node is reachable from the His
        through the sheet. Measured: anterior exit at s 7.5 mm, a +15.9 mm (mesh node 53851; limit 12.6 mm there) in
        Y5HYEDL4, 2.6 mm beyond; none in 6G8DD8S5 (endpoint inside, s 23.6, a +15.8 mm); at s 10.0, a +15.2 mm (node
        23592) in 7D98EVAR, 7.1 mm beyond. Septal past the sheet end at s 34.7 / 33.9 / 33.5 mm (nodes 70951 / 44159 /
        219778), 6.0 / 0.8 / 1.4 mm beyond, the endpoint outside in all three (s 39.3 / 33.9 / 35.3 mm). Posterior at
        s 32.8 / 32.1 / 33.5 mm (nodes 34895 / 56691 / 9848), 24.7 / 14.7 / 16.0 mm beyond; none re-enters. DISTAL edges
        meet trunk or fascicle nodes only at the three fascicle endpoints (0 / 1 / 0 of them inside the envelope); with
        the trunk and fascicles removed the LV network is one connected component (3,758 / 3,183 / 3,180 nodes);
        40 / 18 / 30 tail nodes kept, 0 / 2 / 0 distal edges re-joined, 0 / 0 / 0 LV distal nodes unreachable.
        Re-checked on the built network at step 2g (the D11 acceptance, 7.1; 15.2).
    No beat is run and no result is seen; these place the D1, D3, D4 and D11 geometry blind (D2's item 12 is report only
    under deviation D16).
35. **Step-0 outflow geometry** (added 20 Oct 2026, report only; at step 0, and again after steps 2b-2d, before any
    beat). Per heart:
    - (a) the height of the tag-1/tag-5 boundary, luminal and epicardial, above the aortic basal ring (on the mesh the
      aortic mid-plane ring, deviation D13, 20 Oct 2026) at de Kerchove's six positions (in the D15 frame, deviation
      D15), with the aortic disc's thickness, its two faces and the existing muscle above each face per position (D13),
      against his external junction heights (Table 1 p.4; 58 human roots): NCS -0.1, N/L +0.3,
      LCS +0.5, L/R +4.6, RCS +2.4, R/N +2.5 mm;
    - (b) the axial rise and the radial reach of each built lune (the LCC rise against Gami's 1.5 +- 0.5 mm);
    - (c) the LCC achieved thickness against de Kerchove's LCS root-base wall thickness, 3.0 +- 1.0 mm;
    - (d) the mesh aortic and pulmonary wall thickness 2 cm above the valves against Hasdemir's 1.6 +- 0.4 and
      1.01 +- 0.4 mm (p.536), labelled **a comparison of construction constants**, as report 11 does: the aorta and the
      pulmonary artery are 2 mm and the RV 3.5 mm distance-map shells (Solis-Lemus section 3.2.1), so the mesh
      pulmonary wall is known in advance to be about twice Hasdemir's, which does not stop the sleeve's 2.0 / 1.7 mm
      levels being re-tagged;
    - (e) the height of RV-infundibulum contact on the aortic root at the L/R commissure and the RCS against de Kerchove's
      +4.6 and +2.4 mm;
    - (f) the D14 boundary, 47.2 % of the span above the 0 % landmark (deviation D14, 20 Oct 2026; the primary, computed
      from the first reading of the span: the PC's first reading of the tricuspid-annulus level in step0_report35.py,
      the one that gave 13.6 / 10.2 / 13.7 mm at step 0; the second gave 12.8 / - / 13.1 mm, and the third, the TV-ring
      centroid, gave 101-122 mm and is not usable), and the three candidate infundibulum-cut boundaries beside it (37.3
      % of the span; D6's 12.7 mm above the 0 % landmark; 15.3 mm below the ring), each with the tag-1/tag-2 area above
      it (reported, not used), and the mesh's posterior span against Jakiel's 26.9 +- 6.5 mm, with the 100 % landmark
      the pulmonary mid-plane ring (D13); at step 0, to the PC's "pulmonary ring" (level not stated), 13.6 / 10.2
      / 13.7 mm (second reading 12.8 / - / 13.1 mm);
    - (g) the wall thickness along the supraventricular crest's course, if the mesh carries one, against Jakiel's
      12.26 mm at its origin (12.3 +- 2.9 in Table 1) and 9.2 +- 1.9 mm at its termination;
    - (h) the height of the tag-1/tag-5 boundary relative to the aortic valve plane (the disc's mid-plane ring,
      deviation D13, 20 Oct 2026) at the same six positions, with the disc's thickness, its two faces and the existing
      muscle above each face per position (D13): the precondition of 8.5 item 9 (D5). At step 0, 2.0-5.6 mm above the
      mid-plane at all six positions in every heart: passed (8.5 item 9);
    - (i) (added by deviation D15, 20 Oct 2026; measured read-only by the PC after step 0, relayed 20 Oct 2026 17:34 UTC,
      followup.json, local commit a2e25a1) **the D15 frame landmarks**: the directions of the mitral-disc and
      pulmonary-disc centroids, projected onto the aortic disc's mid-plane about the root axis (the aortic disc's
      normal), and the angle from the first to the second in the sense that puts it in 90-150 deg (the frame check of
      8.5 item 6); the 13:51 nearest-point readings beside them (the aortic-ring point nearest the mitral ring, the
      closest ring-to-ring distance and the spread of the ring points within one mean edge of it, and the ring point
      nearest the pulmonary valve, in both senses); and the arcs where RV muscle (tag 2) touches the aortic root (tag 5)
      0-3 mm and 0-6 mm above the aortic mid-plane, with their centres in the D15 frame. Measured: mitral-to-pulmonary
      centroid angle 126.9 / 126.4 / 128.1 deg; the aortic and mitral discs never touch (closest ring-to-ring 8.84 /
      7.66 / 7.91 mm; the ring points within 1.05 mm of that minimum spread over 19 / 132 / 137 deg); the 13:51 check
      42.3 / 62.9 / 60.9 deg (317.7 / 297.1 / 299.1 deg in the other sense); RV-root contact 0-6 mm centred at 183.9 /
      186.7 / 190.4 deg, and 0-3 mm 4 / 8 / 0 nodes, centred at 167.7 / 219.0 deg / none (derived in 19.15.5).
    Reports change no value or verdict (0.3).

## 13. Sensitivity arms

All arms are fixed now, with their values and their scopes, and are reported as ranges beside the primary. Verdicts come
from the primary only. No arm is promoted after its result is seen.

**Count, corrected.** The adopted list's arm table has 24 rows, and its own "what your papers changed" rows split 11 of
them by axis, definition or source (0 / 21 ms, apex, base, HF 29, LVOT circumferential, 1 and 14 mm sheet, 7 ms, 2 ms,
junction coverage, septal slowing, Gami), which gives **35 adopted arms**. The 19 Oct draft listed 37, and the two
extras (a per-heart crescent rotation correction from Toh Fig 6, and a pulmonary-sleeve island perturbation) were
**reader proposals that Alex did not adopt**; they are moved to 17.1, their slots A29 and A30 are left vacant rather
than renumbered so that every cross-reference in this file stays valid, and **A30a** (trim mesh muscle above the sourced
4.0 mm sleeve) takes the place the sleeve-geometry arm needs. **A38** would exist only under blocks B and C of 8.9 (the
cusp-muscle card's other options, not chosen), as the option not chosen. At 07:30 this paragraph ended "so v5.2 runs **35 arms**: A1-A28, A30a, A31-A37", but that list
holds **36** numbered arms (28 + 1 + 7); the stated count was wrong (correction, 20 Oct 2026). The two figures do not
conflict: the 35 adopted arms are A1-A28 and A31-A37, and the 36th, **A30a**, is not one of them; it was added in this
lock from review finding R12 (8.6; review log). **After the re-issue
(deviations D1, D8 and D10, 20 Oct 2026; post-lock card 1, "Junction-free", 20 Oct 2026 11:22:09 UTC; post-lock card 2, "Adopt all", 20 Oct 2026 11:23:21 UTC)** v5.2 has **38
numbered arms**, A1-A28, A30a, A31-A37, A39 and A40, plus the sub-variant **A19b**, that is **39 arm entries** (some
entries contain several levels or runs, e.g. A10's two levels, A27's two radii, A33's 12-run set and A36's two levels;
see each row). A35 (D9a) and A36 (D9b, a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; not run if declined) are feasibility-gated
(9.4) and are recorded as not run if their step-0 checks fail. **At step 0 (13:51 file) both failed** (A35: check (iv), the host ends above the iliac crest and its skeleton is one tag; A36: Torso.vtu carries no skeletal muscle and needs about 12-13 GB; 9.4, 19.15.8; no deviation), **so at most 37 of the 39 arm entries are run** (A17, A18 and A20 are also recorded as not run if their reachability checks fail, 7.1, 7.2). A38 stays reserved for blocks B and C of 8.9, so the new arms take the next free numbers, A39 and A40. A20 and A10 keep their numbers with new content
(A20 swapped by D2 and redefined by D16, 20 Oct 2026, as the RB on the septum only with v5.1's band edge removed; A10's levels set by D7).

**The "prompted by a fail?" column of the 19 Oct draft mixed three different questions and is split in two:**
"prompted by a fail" is about provenance (did a failing gate cause this arm to exist?), and "moves which gates, which
way" is about effect, stated **relative to the v5.2 primary**, not relative to v5.1 or to another arm.

| # | Group | Arm | Scope | Source | Prompted by a fail? | Moves which gates, which way (against the primary) |
|---|---|---|---|---|---|---|
| A1 | Repolarisation | S1: wedge transmural APD gradient 111 ms (upper bound) | ECG, ledger beats | Glukhov 2010, human NF wedges | No | T wave only; no gate |
| A2 | Repolarisation | S1a: no transmural APD gradient, 0 ms | ECG | Boukens 2017 (intact dog, 5 +- 16 ms). ("Srinivasan 2019, about 5 ms" is **not read / unverified**: no such paper is in the file set, inputs.md or the paper reads, so it is not cited as a source) | No | T wave only; no gate |
| A3 | Repolarisation | S1b: 21 ms with the epicardium longer | ECG | Drouin 1995 (human slices, EPI 351 +- 14 against ENDO 330 +- 16 at CL 1000) | No | T-wave polarity only |
| A4 | Repolarisation | S1c: apex 29 ms longer | ECG | Srinivasan 2016 (mean +- SE) | No | T wave only |
| A5 | Repolarisation | S1c': base 25 ms longer, as a graded IKs increase | ECG | Tomek 2019 Appendix 1-15.1.5 p.39 | No | T wave only |
| A6 | Repolarisation | HF transmural difference 29 ms instead of 7 ms | ECG, HF hearts | Glukhov 2010 | No | T wave only |
| A7 | Repolarisation | Activation-APD coupling, slope **-0.71 +- 0.4 (mean +- SE)**, applied **transmurally and only to beats paced from the LV endocardium** | the LV-endocardial basal paced beats, one per heart | Srinivasan 2016 Table 1 (LV-endo base pacing, transmural). **Restricted here**: the slope is site-dependent (RV-endo pacing -1.36 +- 1.9, LV-epi pacing +0.63 +- 0.3) and **global coupling was not negative** (-0.03, 0.14, 0.4), so applying -0.71 to His beats or to arbitrary paced beats is not supported. The 19 Oct scope ("His beats and one paced beat per heart") is withdrawn | No | T wave only |
| A8 | Conductivity | S2: Clerc's full set | ECG, ledger beats | Clerc 1976 | No | q calls and amplitudes: gates 5 and 6 either way |
| A9 | Conductivity | S3: the Roberts and Scher in situ set | ECG only | Roberts and Scher 1982 (dog in situ, n = 6) | No | gates 2, 4, 5, 6 either way (amplitude and peak picking) |
| A10 | Conductivity | S4: blood **0.63 and 0.89 S/m** (human Hct 50 and 35 %; **deviation D7, 20 Oct 2026**); 0.435 and 1.0 S/m kept as labelled literature extremes, not run (R3.4) | ECG only | Geddes and Sadler 1973 Table I p.337 (human formula, in vitro, 37 C, 25 kHz); the extremes: Kaufman and Johnston 1943 Table IV p.49 (dog), Schwan and Kay 1956 pp.664, 669 | No | amplitudes; gate 5 either way |
| A11 | Speeds | Transmural 0.34 and in-plane cross-fibre 0.24 m/s (HF **0.235** and **0.173**, derived from the unrounded re-projection 0.336 / 0.238) | activation and ECG | Caldwell 2009 (pig in vivo), axes re-projected onto the wall and scaled to fibre 0.80 m/s | No: Caldwell is a different measurement, not a response to a fail | **Against the primary 0.48 m/s it is slower**: 6 mm transmural crossing goes from 12.5 to 17.6 ms (derived), which **lengthens paced QRS (toward gate 1 passing)**, widens depth effects (toward gate 6 passing), pushes 6G's gate-2 ratio further out and risks gate 4. The 19 Oct entry ("No: it raises the arm, away from helping gate 1") compared it with the old 0.24 arm and is withdrawn |
| A12 | Speeds | CL-1000 pair 0.92 / 0.22 m/s | activation and ECG | Glukhov 2012 | No | QRS durations; gates 1, 2, 6 either way |
| A13 | Speeds | No HF conduction remodelling | HF hearts | Anderson 1993 IDC group I | No | gates 2 and 6 rest on it, both directions |
| A14 | Fibres | Lombaert transverse angle 7 / 9 / 34 deg, with the transmural speed refitted to Taggart's 12.6 ms | activation and ECG | Lombaert 2012 | No; the refit is a declared calibration | gates 4 and 6 either way |
| A15 | Fibres | v5.1 fibres | gate 5 only | v5.1 | No | gate 5 either way; it reports gate 5 under the v5.1 fibres. At 07:30 it made gate 5 fix 5's calibration check; that label is withdrawn under post-lock card 3, since neither limb applies to the LV helix: it was not prompted by a fail, and this arm reports gate 5 under the v5.1 fibres without aiming the helix at it (11.5; deviation G, 20 Oct 2026) |
| A16 | Fibres | LVOT fibres circumferential through the whole wall | activation and ECG | Acosta 2015 histology | No | gates 1 and 3 either way; the A9 LVOT report leg |
| A17 | Conduction system | LB sheet origin width 1 mm (right-sided His phenotype, 5 of 32 hearts); D11 applied to the arm's own envelope, with assumption 56's joins; exit nodes, kept lengths and re-joined distal edges reported; "not run" with the reason if any LV distal node is unreachable (7.1; deviation D11, 20 Oct 2026) | activation and ECG | Massing 1976 | No | Durrer (a), (b) either way |
| A18 | Conduction system | LB sheet origin width 14 mm; D11 applied to the arm's own envelope, with assumption 56's joins; exit nodes, kept lengths and re-joined distal edges reported; "not run" with the reason if any LV distal node is unreachable (7.1; deviation D11, 20 Oct 2026) | activation and ECG | Massing 1976 | No | Durrer (a), (b) either way |
| A19 | Conduction system | LV free-wall junctions only from 50-67 % of base-to-apex (**extrapolating Massing's posterior-fibre finding to the whole free wall**) | activation and ECG | Massing 1976 p.620 (posterior fibres, 13 of 13); pp.612-613 (anterior, 2 of 13) | **Yes** | It would lengthen QRS, **toward** gate 1 passing, which is why it stays an arm; it moves gate 7 (T) and (b) **away** from passing (correction, 20 Oct 2026: the 07:30 text said toward gates 1 and 7) |
| A19b | Conduction system | The primary with no LV distal-network junctions in AHA segments 4 and 5, the basal inferior and inferolateral free wall; A19's 50-67 % rule is not applied (a sub-variant of A19; **deviation D10, 20 Oct 2026**) | activation and ECG | Durrer 1970 p.906 and Cassidy 1984 pp.39-40 (human function: posterobasal LV last); the zero-junction evidence is weak (7.7) | No (sourced to Durrer and Cassidy), but tuning-shaped toward failing gate 1; 0.3 applies if it were ever promoted | **Labelled tuning-shaped toward gate 1**: it likely lengthens summit and cusp paced QRS, toward gate 1 passing, and moves 7(T) away. Never promoted |
| A20 | Conduction system | **Redefined (deviation D16, 20 Oct 2026):** the RB on the septum only: v5.1's moderator-band edge is removed and the RB ends at the band's septal insertion, which joins the nearest v5.1 RV distal-network node with a PMJ (7.3 delays; assumption 58); if any RV distal node is then unreachable from the His, A20 is recorded "not run" with the reason, and no edge is added (7.2). At 13:51: "Swapped (deviation D2, 20 Oct 2026): the RB on the septum only, the 07:30 primary; the moderator-band course is now primary (7.2)", which read v5.1 as septal-only (superseded) | activation and ECG | Massing 1976 p.615; v5.1 | No | Against the corrected primary (v5.1's RB, its band edge included; D16): RV onset later, 7(c) later (toward or past 31 ms), gate 3's RVOT value and gate 4 either way, gate 1 "0 or +", gate 8 "0 or -". The 13:51 cell, "Against the D2 primary: RV onset later and 7(c) back toward v5.1's 27.5 ms", is superseded |
| A21 | Conduction system | PMJ antegrade delay 7 ms (Wiedmann's canine control pool, **mean +- SE** in his tables) | activation and ECG | Wiedmann 1996 (pooled 7.06 ms) | **Yes** | Lengthens QRS, **toward** gate 1 passing; near-neutral to away on gate 7 (T) and (b), which are timed from LV onset (correction, 20 Oct 2026) |
| A22 | Conduction system | PMJ retrograde delay 4 ms, equal to antegrade ("helps gate 1"; no source for this direction) | activation and ECG | none (model assumption) | No | Against the 2 ms primary it **lengthens** paced QRS by about 1-3 ms, that is **toward** gate 1 passing, and moves MDI (gate 3) either way |
| A23 | Conduction system | 6G: LBBB without retrograde entry into the LV network | 6G | Upadhyay 2019 | No | 6G His QRS and gate 2, either way |
| A24 | Conduction system | 6G: tissue slowed to 0.3 m/s in the blocked ventricle, **labelled tuning** | 6G | Gillette 2022 | **Yes, and it is tuning**: it was proposed to move 6G's QRS | Widens 6G QRS, **toward** gate 2 and gate 6 passing; it is reported only, and never promoted |
| A25 | Conduction system | Slower transseptal conduction in LBBB with HF (apparent 0.30 and 0.13 m/s, derived) | 6G | Strik 2013 (dog) | No | gates 2 and 6 in 6G, **toward** passing, so it stays an arm; it cannot move gate 7, which is scored on the control heart (correction, 20 Oct 2026) |
| A26 | Focus | Depth-dependent latency, 17 + 17w ms (not a measured depth effect) | all paced beats | Herweg 2010 | No | gates 1, 2, 6 **and gate 4**: adding latency broke Bazan 2006 on 13 Oct (RV +13.0 / 12.3 / 14.3 %), so it moves gate 4 away from passing |
| A27 | Focus | Finite focal source, **5 and 10 mm radius** | cusp, summit and coronary-vein sites | Xie 2010 (rabbit, in silico); Yokokawa 2016 capture currents | No | gates 1 and 3 either way; it would change the stimulus on two failing gates, so it is not promoted |
| A28 | Outflow | Gami's smaller aortic crescents (RCC 2.8, LCC 1.5 mm) | the gate-1 and gate-3 beats of the ledger | Gami 2011 (603 autopsy hearts) | No: it is a second, smaller measurement of the same structure | Against the D5 primary (deviation D5, 20 Oct 2026): the RCC (2.8 mm) moves gate 1 either way per heart, depending on how far the 2.4 mm axial cap binds; the LCC (1.5 against 2.9 mm) shortens the cusp exit path, **away** from gate 1 passing; it is never selected on its gate effect |
| A29 | *(vacant)* | Withdrawn to 17.1: per-heart crescent rotation correction (not adopted; Toh prints no regression coefficients) | - | - | - | - |
| A30 | *(vacant)* | Withdrawn to 17.1: pulmonary-sleeve island perturbation (not adopted; the perturbation cannot be specified from the sources read) | - | - | - | - |
| A30a | Outflow | Trim all mesh muscle above 4.0 mm over the cusp nadir (the alternative sleeve rule, 8.6) | RVOT and supravalvar beats | Lis 2021 | No | **Marked "moves gate 3"**: less RVOT muscle, direction reported, never promoted |
| A31 | Forward model | Epicardial fat, one compartment, 0.0377 S/m (0.0122-0.0667), with the Abbara map, its age columns and the long-axis blend above the basal plane | ECG only | Abbara 2006; Keller 2010; Jakiel 2025; Kuniewicz 2023 | No | amplitudes; gates 5 and 6 either way |
| A32 | Forward model | The heart pose not chosen on the pose card (05:19:07) | ECG only | v5.1 atrial fit; CT | No | amplitude criteria (gate 5), and gates 2, 4, 7(e) weakly |
| A33 | Forward model | Respiration as McLeish coupled poses, plus the fixed +- 10 deg / +- 10 mm set (12 runs per heart, 9.4) | ECG only | McLeish 2002; Kayyali 2025; Hoekema 2001; Bradley 2000 | No | amplitudes; reported as a band, never used to re-score |
| A34 | Forward model | Electrode misplacement bank (Wenger directions, V3 recomputed, limb variants, Doste's 13 configurations; **best-scoring selection is report-only**) | ECG only | Wenger 1996; Anter 2012; Arya 2011; Kligfield 2007; Doste 2020 | No | gates 5 and 6 either way; no verdict |
| A35 | Forward model | Lungs, 0.078 S/m (0.0389-0.134), in the KCL host torso, lungs on against lungs off in the same host (**deviation D9a, 20 Oct 2026**) | ECG only, **feasibility-gated** (9.4): not run if the step-0 checks or meshtool fail. **Not run**: check (iv) failed at step 0 (9.4, 19.15.8) | Geddes and Baker 1967; Gabriel 1996 III; Kaufman and Johnston 1943 Table IV p.49; Schwan and Kay 1956 pp.668-669 (support); host: Zenodo 7253863 | No | amplitudes; gates 5 and 6 either way; no verdict |
| A36 | Forward model | Skeletal muscle at two labelled levels with no primary between them, (a) 0.202 S/m isotropic with a ratio-7 anisotropic variant and (b) Burger's human 0.417 / 0.148 S/m, with subcutaneous fat as A31, in the Moss/Wuelfers/Seemann torso (**deviation D9b, 20 Oct 2026; a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC**) | **not run** unless the read-only step-0 feasibility check passes (9.4), and not run if D9b is declined. **Not run**: at step 0 Torso.vtu carried no skeletal muscle and needed about 12-13 GB (9.4, 19.15.8) | Keller 2010 p.1569; Klepfer 1997 p.709; Geddes and Baker 1967 Table 4 p.285 (Burger, as cited there; the primary paper not read); host: Zenodo 8285403 | No | amplitudes either way; no verdict |
| A37 | Forward model | Four KIT torso shapes: **T_24, T_20, T_17 and T_01**, the first four in the record's own ordering other than the primary T_13 (**deviation D17, 20 Oct 2026**; the 13:51 text said "the first four in the record's own ordering", which begins with T_13; IDs recorded in step 0) | ECG only | Bender 2026 | No | amplitudes; gates 5 and 6 either way |
| A39 | Conduction system | The 07:30 sheet coupling (no PMJ over the first 10 mm, one at every sheet node beyond it) together with the v5.1 LV distal coverage of the upper left septum (to z 0.9): the "early upper septum" hypothesis (**deviation D1, 20 Oct 2026**) | activation and ECG | Assumption 30 of the 07:30 lock; the v5.1 network | No: it is the rule D1 replaced | Against the D1 primary: shorter summit and cusp paced QRS, **away** from gate 1 passing; 7(b) toward passing; gate 8's margin wider; report 29's sign either way |
| A40 | Conductivity | S5: Hooks bulk set in the lead field only, sigma_b 0.70 fibre / 0.35 transmural / 0.16 cross-fibre S/m, source term the fix-2 sigma_i (**deviation D8, 20 Oct 2026**). Implied sigma_e = sigma_b - sigma_i, derived (fibre / cross / transmural): control 0.526 / 0.148 / 0.288 S/m, HF 0.526 / 0.154 / 0.323 S/m, all positive, **asserted positive at build** | ECG only | Hooks 2007 p.e108 (pig in vivo, 6 hearts, 61 sites); axis mapping inferred from LeGrice 1995 (dog, 4 hearts, p.H571), coarse because Hooks's laminae were not uniformly radial (p.e107) | No | q calls and amplitudes: gates 2, 4, 5 and 6 either way; no verdict |

- **Arms and the forward problem.** Any arm that changes sigma, the fibre field or the pose **recomputes the lead fields**
  for every heart it touches (A8-A16, A31-A37 and A40); arms that change only timing or cell behaviour reuse the primary lead
  fields. Lead-field solves take 6-8 minutes per heart and have run WSL out of memory before, so they run **one heart
  and one arm at a time, single process**, with the memory rule of 15.1, and the count is in the arms build step
  (15.2 step 8a).

## 14. Predictions, written before any v5.2 beat and never used to change a value

Signs are for the gate's own measure: **+** moves it toward passing, **-** away from passing, **0** no change expected
(under about 1 ms or under 1 % of the index), **?** no lean. Every entry is an inference. The table is per change, so the
combined row is the only one that predicts a verdict.

**Two corrections of method against the 19 Oct draft.** (i) A "0" is a claim, not a default: where the project's own data
show that a change of this kind moved a measure, the entry is "?" or signed, not "0". In particular a **lead-field-only**
change (decision 8) moved gate 4's control value from 4.4 to 3.6 % (18 % of the band's index) and made a few beats jump
40-114 ms in IDT through **which-peak-is-picked swaps**, which are also what most of the gate-9 misses were; so fix 2,
fix 3, the pose and the measurement chain are not "0" on gates 4 and 9. (ii) Every change in this lock now has a row,
including the T4 engine choice, the gate-5 map and pairing, the 6G cut on the sheet, the sleeve existing-muscle rule and
the gate-3 site-set change.

| Change | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | Calibration check |
|---|---|---|---|---|---|---|---|---|---|---|
| Fix 1, repolarisation (spliced template) | ? | ? | ? | 0 | 0 | ? | 0 | 0 | ? | G1 |
| Fix 2, conductivities | ? | 0 | ? | ? | ? | ? | 0 | 0 | ? | none (exempt whole-model change, 11.5; deviation G) |
| Fix 3, blood and walls | ? | 0 | ? | ? | ? | ? | 0 | 0 | ? | none (exempt whole-model change, 11.5; deviation G) |
| Fix 4, speeds | ? | - | ? | 0 | **-** | **?** | **?** | ? | ? | none (exempt whole-model change, 11.5; the 07:30 G1 and G7 labels withdrawn, deviation G); A9 and Taggart reports |
| Fix 5, LV helix and outflow blend | ? | ? | ? | 0 | ? | ? | ? | 0 | 0 | G1, G3, G8 for the outflow blend (deviation G); none for the LV helix (neither limb applies, 11.5; the 07:30 G5 label withdrawn, deviation G) |
| LB septal sheet | ? | ? | ? | 0 | ? | ? | ? | 0 | ? | G2, G5, G6, G7 (the 07:30 section 11 G3 label withdrawn, deviation G) |
| 6G cut applied to the sheet (**new row**) | 0 | ? | 0 | 0 | 0 | ? | 0 | 0 | 0 | G2, G6 |
| PMJ retrograde 2 ms (v5.1, unchanged) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none (unchanged from v5.1) |
| Infundibulum cut | ? | 0 | **?** | 0 | 0 | 0 | 0 | 0 | 0 | G1, G3, G8 (deviation G) |
| Aortic crescents | **?** | 0 | ? | 0 | ? | 0 | 0 | 0 | 0 | G1, G3, G8 (deviation G) |
| Pulmonary sleeves | 0 | 0 | **0 on the verdict** (the supravalvar sites are a reported family, 11.2b), ? on the reported RVOT family | 0 | 0 | 0 | 0 | 0 | 0 | G3 |
| Sleeve existing-muscle rule (**new row**) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none (neither limb applies, 11.5; the 07:30 G3 label withdrawn, deviation G) |
| Summit re-anchor and new gate-1 site set | ? | 0 | ? | 0 | **?** | 0 | 0 | 0 | 0 | G1, G3, G5, G8 (deviation G) |
| Gate-3 site-set change (crescent cusps into the aortic-sinus family) (**new row**) | 0 | 0 | ? | 0 | 0 | 0 | 0 | 0 | 0 | G3 |
| Gate-5 Cassidy map, eligibility and 18 +- 5 mm pairing (**new row**) | 0 | 0 | 0 | 0 | **?** (wider pairs sample more transmural difference, but the pool is unchanged in kind) | 0 | 0 | 0 | 0 | G5 |
| Stimulus clipping and capture rule | **0 in the eikonal; + where the connectivity clause bites (RCC, supravalvar)** | 0 | ? | 0 | 0 | 0 | 0 | 0 | ? (monodomain only) | G1, G3, G8 (deviation G) |
| Measurement chain (14 Oct convention kept; comparator chains reported) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none (unchanged) |
| CT pose | ? | **?** | ? | **?** | ? | ? | **?** | 0 | **?** | none (exempt whole-model change, 11.5; deviation G) |
| Gate-9 mesh ladder, flat-block tuning, Niederer benchmark | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | ? | G9 |
| T4 engine choice (**new row**; gates 5 and 6 only, 15.3) | 0 | 0 | 0 | 0 | ? | ? | 0 | 0 | ? | G5, G6 |
| **D1**, upper third of the left septum junction-free (**deviation D1, 20 Oct 2026**) | **+** | ? | ? | 0 | ? | ? | **-** ((b) away; (T) 0 to -; (e) slightly longer; (a) ?) | **-** (the margin shrinks) | ? | G1 (post-lock card 1; tuning-shaped toward gate 1), G2, G5, G6, G7 ((a), (b), (T), RV items); kept unchanged after the step-0 counts (deviation D12, 20 Oct 2026) |
| **D2**, right bundle along the moderator band (**deviation D2**), **superseded in substance by D16 (20 Oct 2026)**: v5.1 already has the band, so the primary right bundle is v5.1's, unchanged, and nothing is built (the 13:51 signs, kept as history: G1 0 or -, G3 ?, G4 ?, G7 - ((c) earlier, could fall below 20 ms), G8 0 or +; the rest 0) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none: v5.1's right bundle is not a change (D16); D2's 13:51 G7 ((c) and the RV items) label withdrawn |
| **D3**, gate 7(a) patch centres (**deviation D3**) | 0 | 0 | 0 | 0 | 0 | 0 | ? ((a) only) | 0 | 0 | G7 |
| **D4**, sheet envelope from the Massing digitisation (**deviation D4**) | ? | ? | ? | 0 | ? | ? | ? | 0 | ? | the sheet's: G2, G5, G6, G7 |
| **D5**, RCC axial cap, valve-plane reference ring, cusp sites at half the built extent (**deviation D5**) | - or 0 | 0 | ? | 0 | 0 | 0 | 0 | ? | 0 | G1, G3, G8 |
| **D6**, infundibulum cut at 12.7 mm above the 0 % landmark (**deviation D6**), **superseded by D14 (20 Oct 2026)**: reported beside at step 2b, not built; the signs are the 13:51 ones, kept as history | ? | 0 | ? | 0 | 0 | 0 | 0 | 0 | 0 | none of its own: G1, G3, G8 are D14's (11.5) |
| **D11**, the sheet's outflows beyond its envelope: v5.1 fascicle paths kept, distal edges re-joined (**deviation D11, 20 Oct 2026**; the 13:51 attachment could not be built, so the signs are against the alternative, "Nearest node", in D4's pattern) | ? | ? | ? | 0 | ? | ? | ? | 0 | ? | the sheet's: G2, G5, G6, G7 ((a), (T), (b), RV items) |
| **D13**, the valve-plane ring on the mesh's valve discs: the mid-plane ring (**deviation D13**; against the arterial-face reading) | 0 or - | 0 | ? | 0 | 0 | 0 | 0 | ? | 0 | G1, G3, G8 (as the crescents); G3 (as the sleeves) |
| **D14**, infundibulum cut at 47.2 % of the mesh's posterior span (**deviation D14**; against D6) | ? | 0 | ? | 0 | 0 | 0 | 0 | ? | 0 | G1, G3, G8 (as the cut) |
| **D15**, the aortic angular frame on the mesh (**deviation D15**; the 13:51 frame could not be built) | ? | 0 | ? | 0 | ? | 0 | 0 | ? | 0 | G1, G3, G5, G8 |

**Arm predictions added at the re-issue** (deviations D1, D2, D5, D7-D10, 20 Oct 2026; A20's row restated against the corrected primary by deviation D16, 20 Oct 2026), against the re-issued primary and
written before any beat. Arms decide no verdict; the signs say which way each arm would move a gate's measure. Arms are
not run inside gate 9, so its column is 0.

| Arm | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| A39, the 07:30 sheet coupling with upper-septal coverage | - | ? | ? | 0 | ? | ? | + ((b); (T) 0 to +) | + | 0 | The reverse of D1 |
| A20, septal-only RB (redefined by D16: v5.1's band edge removed) | 0 or + | 0 | ? | ? | 0 | 0 | - ((c) later, toward or past 31 ms; RV onset later) | 0 or - | 0 | Against the corrected primary, v5.1's RB with its band (D16). The 13:51 row, "+ ((c) back toward 27.5 ms)" as the reverse of D2, is superseded |
| A19b, no LV junctions in AHA 4 and 5 | + | ? | ? | 0 | ? | ? | - ((T)) | - | 0 | Tuning-shaped toward gate 1; never promoted |
| A40, Hooks bulk set in the lead field | ? | ? | ? | ? | ? | ? | 0, (e) ? | ? | 0 | ECG only: amplitudes and peak picking |
| A10, blood 0.63 and 0.89 S/m | ? | ? | ? | ? | ? | ? | 0, (e) ? | ? | 0 | ECG only |
| A35, lungs in the KCL host | ? | ? | ? | ? | ? | ? | 0, (e) ? | ? | 0 | ECG only; only if feasible |
| A28, Gami crescents (against the D5 primary) | - (LCC); ? (RCC) | 0 | ? | 0 | 0 | 0 | 0 | ? | 0 | The RCC sign depends on how far the cap binds per heart |

**A35, A36 and A37 after step 0 (20 Oct 2026).** A35 and A36 failed their step-0 feasibility checks and are not run
(9.4; 19.15.8), so the A35 row above cannot be tested. D17 changes which four KIT shapes A37 runs (T_24, T_20, T_17
and T_01) and no prediction: A37 stays "amplitudes; gates 5 and 6 either way" (13); calibration none (11.5).

### 14.1 Mechanism and magnitude for each change

| Change | Mechanism | Expected magnitude |
|---|---|---|
| Fix 1 | The T wave appears. The window to +80 ms is as in v5.1, **but the splice at +80 to +100 ms falls inside the late QRS of any beat whose activation lasts longer than 80 ms**, so with the continuity offset of R1.2 the QRS measures move only through the cross-fade, and without it they would move through a trailing transmural source | QRS-based measures under 5 ms **if** the continuity offset holds; the step-4 template-only check measures it directly |
| Fix 2 | The cross-fibre intracellular source falls from 0.0626 to 0.0118 S/m, so the lead-field weighting of cross-fibre current changes; activation is untouched (eikonal speeds come from fix 4) | Larger than decision 8's change, which left every verdict unchanged but moved gate 4's control value 4.4 to 3.6 %, moved IDT by up to 114 ms in a few beats and flipped the q call in 20 of 432 |
| Fix 3 | New blood columns in the atria and great vessels sit between the summit and cusp sources and the electrodes | Summit and cusp amplitudes; direction unknown, reported per heart; peak-picking swaps possible, as in decision 8 |
| Fix 4 | Anisotropy rises from 1.67 to 3.48 (HF 2.31 to 4.79): faster along fibres, slower across them. **Transmural speed is unchanged** (0.48 control, 0.336 HF), so the epicardial-to-endocardial crossing time is unchanged; what changes is in-plane spread, which lengthens the endocardial baseline that gate 6's RS ratio divides by | A9 ratio rises; near-site apparent speeds 0.80 / 0.23 m/s within 10 %; paced QRS moves either way by 5-20 ms. **Gate 6: the v5 evidence points the other way** - slowing HF tissue cut 6G's RS from 17.6 % to 7.6 % in the v5 arm-B test, so "+" is withdrawn and the entry is "?" with that magnitude on record. **Gate 7: also "?"** - from v5 to v5.1 (fibre +6 %, cross-fibre -25 %) both the no-network QRS (220.25 to 230.75 ms) and Durrer T (100.8 to 113.3 ms) got **longer**, that is away from passing. **Gate 5: "-"**, since the dive's own check found the initial dipole becoming less epicardium-to-endocardium |
| Fix 5 | The mid-wall offset of about +30 deg disappears, and the LVOT and summit get outflow angles | Local wavefront direction changes most at mid-wall and in the LVOT; the A9 LVOT leg depends on this |
| LB septal sheet | Earliest LV endocardial activation becomes a broad basal septal sheet with PMJs beyond its first 10 mm, instead of v5.1's trunk and three fascicles inside its envelope, whose paths beyond it are kept (deviation D11, 20 Oct 2026; the 13:51 text said "instead of two fascicle endpoints") (the 07:30 rule; under D1 the upper third of the left septum is junction-free, see the D1 row) | Durrer (a) and (b) move most; the 6G ratio moves through how much LV network survives the cut; **gate 6 is "?" not "0"**, because the surviving retrograde surface changes 6G's endocardial baseline |
| 6G cut applied to the sheet | Only the His-to-sheet edges are cut, so the whole sheet stays available for retrograde entry (7.8). That is more retrograde surface than v5.1's trunk and three fascicles, which carried no PMJ (report 34 item 8; deviations D11 and D12, 20 Oct 2026; the 13:51 text said "v5.1's two fascicle endpoints") | 6G QRS and the gate-2 ratio either way, by a few ms |
| PMJ retrograde 2 ms (v5.1, unchanged) | Every paced beat starts in muscle and enters the network retrogradely (7.3); the delay is v5.1's, so nothing changes against v5.1 | None against v5.1. Arm A22 (4 ms) would lengthen paced QRS by about 1-3 ms, toward gate 1 passing, and move MDI (gate 3) |
| Infundibulum cut | Lengthens the RVOT-to-LV path, which the mesh fusion had shortened. **But the direction on the Daniels index is not what the 19 Oct draft assumed**: MDI = t_peak / QRS, and in the project's J3b test delaying LV access **raised** RVOT MDI from 0.667 to 0.782 (peak +30 ms, QRS +14 ms). A short path would also have lowered the RVOT MDI, not raised it, so it cannot be the source of the excess | RVOT paced QRS longer by about 5-15 ms; gate 3 "?" with the J3b magnitude on record, and gate 1 "?" rather than "+" |
| Aortic crescents | Cusp stimuli now capture real muscle above the hinge, so the exit path to the LV body is longer. **But gate 1 is scored from detected onset**, and conduction inside a 2.9-6.4 mm crescent is near-silent on the surface: clinically it shows up as a stimulus-to-QRS interval (Yamada: cusp 36 +- 8 ms, report 2), which is exactly the part the detected-onset measure does not see | Cusp paced QRS longer in true mode; on the surface measure the gain may be small or zero, so G1 is "?" not "+". The LCC crescent is only about 3 elements at 1 mm, so the effect is bounded by the mesh |
| Pulmonary sleeves | Supravalvar stimuli now capture real muscle, with a 1 mm apex. They are **not** in gate 3's RVOT family (11.2b), so they cannot move the verdict; the reported supravalvar family does move | Supravalvar MDI and pseudo-delta are new quantities; the gate-3 RVOT value is unchanged by this |
| Sleeve existing-muscle rule | Built height = max(existing, 4.0 mm) over the nadir, nothing trimmed, so v5.1 geometry is preserved wherever it already exceeded the sourced height | 0 against v5.1 by construction; the per-heart achieved heights are reported, and A30a gives the trimmed alternative |
| Summit re-anchor | Sites move to the constructed Kuniewicz anchor, so the summit values are measured somewhere else; summit and vein sites also dominate the gate-5 basal superior pool (15 of 21 in v3), so gate 5's pool content moves with them | Site-to-summit-tip distance changes by millimetres (reported per site); QRS by a few ms; gate 5 "?" |
| Gate-3 site-set change | The aortic-sinus family is measured in crescent muscle instead of valve-plane muscle | The aortic-sinus MDI moves; the v5.1 family is scored beside it, so the size of the redefinition is visible |
| Gate-5 map and pairing | Wider (18 mm) pairs sample more of the transmural difference than v5.1's 3 mm pairs, on an unchanged eligible pool | q-rate difference either way; the achieved separations are reported against 18 +- 5 mm |
| Stimulus clipping | The simulation mesh is myocardium only, so clipping to muscle removes nothing in the graph eikonal; the **connectivity** clause removes seed nodes at RCC and supravalvar sites next to the cut, and fewer seed nodes can only **delay** activation | 0 in the eikonal for the clipping proper; a few ms longer where connectivity bites; monodomain "?" |
| Measurement chain | The 14 Oct convention is kept unchanged as primary, so nothing moves; the comparator chains are reported beside | 0 by construction. (A low-pass at a comparator's own band would smooth small q waves and move onset detection, which is why it is a report and not the primary) |
| CT pose | Rotates the heart relative to the electrodes by 13-20 deg against v5.1, at an unchanged centroid position | Amplitude criteria (q waves, R/S ratios) most affected; **and, through peak picking, timing measures too**: decision 8 showed a forward-model change moving gate 4 by 0.8 points and IDT by up to 114 ms in a few beats |
| Mesh ladder and flat-block tuning | The comparator finally implements the fix-4 speeds, so part of the v5.1 disagreement (72/108) should vanish | Unknown; the HF cross-fibre leg may still not resolve at 1 mm (0.167 m/s against Nagel's 0.15 m/s limit on a 523 um mesh) |
| T4 engine choice | Gates 5 and 6 are scored on the engine T4 picks; RE+ carries diffusion, so it has a diffusive QRS onset that the graph eikonal lacks | Gate 5's q calls are the most likely to move, since they are decided in the first 30 ms |
| D1, upper third junction-free (deviation D1, 20 Oct 2026) | The His beat reaches muscle first below the D1 line, so the septum activates from the middle third toward the base, and the upper septum later through muscle; paced beats lose quick retrograde entry into the upper septum | Summit and cusp paced QRS longer, size unknown (the 9 Oct v3/v4 contrast, 162 against 92 ms, shows how strong basal coverage can be, though v4 also changed speeds); 7(b) lower; (e) slightly longer; report 29 negative (apical-first) in the control and 7D His beats. Counted at step 0 (deviation D12, 20 Oct 2026): 255 / 239 / 220 network junctions removed, and junctions allowed on 21 / 6 / 22 % of the sheet |
| D2, moderator band (deviation D2), **superseded in substance by D16 (20 Oct 2026)** | The 13:51 text: a 1.5 m/s chain carries the RB across to the anterior RV free wall, adding a path that can only advance RV activation. Withdrawn: v5.1 already carries the RB across the band as one 1.5 m/s edge with no PMJ (14.7 / 18.2 / 10.1 mm), so nothing is built | None against v5.1 (D16). The 13:51 magnitudes, kept as history: RV onset earlier (report 14); 7(c) may fall below 20 ms; RV paced QRS shorter or unchanged |
| D3, gate 7(a) patches (deviation D3) | The three (a) areas move to Durrer's positions; no model value changes | The (a) times change with the patch positions; v5.1 scored at both patch sets shows the size of the redefinition |
| D4, sheet envelope (deviation D4) | The sheet's envelope is the Massing width, 22.6 mm at its widest, laid 17.8 mm anterior and 4.8 mm posterior of the His line (the placement a follow-up item), instead of the v5.1 footprint; the widening rule (assumption 10) is unchanged | Either way, by how far the measured envelope differs from the v5.1 footprint (report 34 item 13) |
| D5, RCC cap, reference ring, cusp sites (deviation D5) | The RCC lune is capped at 2.4 mm of axial height; the lune and the existing muscle are measured from the valve-plane ring; the cusp sites sit at half the built extent | Less RCC muscle where the cap binds, so the RCC exit path shortens: gate 1 "-" or "0"; MDI (gate 3) and gate 8's cusp family either way |
| D6, cut height (deviation D6), **superseded by D14 (20 Oct 2026)**; the 13:51 entry, kept as history | The fused septal component ends 12.7 mm above the base instead of at 37.3 % of the span: about 2.6-3.7 mm higher at an illustrative 24-27 mm span (a post-lock review estimate, not a mesh measurement; 8.2) (derived: 12.7 - 0.373 x 24 = 3.75; 12.7 - 0.373 x 27 = 2.63), and 0.2-5.1 mm higher over Jakiel's mean +- SD span of 20.4-33.4 mm (derived: 26.9 +- 6.5 mm, Table 1, 220 human hearts); each mesh's span comes from the step-2b report (report 35 (f)) | Small: RVOT paced QRS and gate 3 either way, by a few ms at most |
| D11, the sheet's outflows (deviation D11, 20 Oct 2026) | The sheet replaces v5.1's trunk and fascicles only inside its envelope; beyond it the v5.1 fascicle paths (40 / 18 / 30 nodes) carry its activation to the code's Durrer points as in v5.1, and the distal trees fed inside the envelope (0 / 2 / 0 edges) re-join the sheet | Against "Nearest node": the Durrer points are reached along v5.1's fascicle paths rather than through the distal network; gates 1, 2, 3, 5, 6, 7 and 9 "?" and gates 4 and 8 "0" (section 14), size unknown |
| D13, the mid-plane ring (deviation D13, 20 Oct 2026) | The crescents and sleeves are measured from each disc's mid-plane, where at step 0, in the 13:51 frame, existing muscle exceeded the RCC cap at every RCC angle (in the D15 frame certain only in Y5HYEDL4, minimum 2.6 mm; read at step 2c) and the sleeve's 4.0 mm over most of the ring | Little new muscle: some LCC lune muscle (existing LCC muscle down to 1.1 mm in 7D98EVAR in the 13:51 frame; in the D15 frame read at step 2c) and sleeve muscle in 6G8DD8S5 and 7D98EVAR (from 2.0 and 1.7 mm), none in Y5HYEDL4's sleeves. Against the arterial face, cusp and supravalvar sites about 3 mm lower; gate 1 "0 or -" |
| D14, the cut at 47.2 % of the span (deviation D14, 20 Oct 2026) | The fused septal component ends 6.4 / 4.8 / 6.5 mm above the 0 % landmark instead of D6's 12.7 mm, so about half of each mesh's posterior RVOT wall is split from the LV instead of 0.9 / 0 / 1.0 mm | RVOT paced QRS longer by a few ms; gate 3 "?" (the J3b test: delaying LV access raised the RVOT MDI; infundibulum cut row), gates 1 and 8 "?" |
| D15, the aortic frame (deviation D15, 20 Oct 2026) | Toh's theta is read from the mitral-disc centroid, with the pulmonary-disc centroid at 126.4-128.1 deg, so the crescents, the cusp sites and the LCA ostium sit at Toh's angles in a frame whose 0-6 mm RV-root contact arc is centred at 183.9-190.4 deg, near the RCS, where Gami found the RCC sinus wall contiguous with the infundibulum (19.15.5) | Gates 1, 3, 5 and 8 "?"; no change can be stated against the 13:51 frame, which could not be built |
| D16, the right bundle is v5.1's (deviation D16, 20 Oct 2026) | Nothing is built: v5.1's right bundle, its moderator-band edge included, is the primary | 0 against v5.1; arm A20 removes the band edge (13) |

### 14.2 Gate-by-gate predictions

| Gate | v5.1 | v5.2 prediction | Why |
|---|---|---|---|
| 1, summit and cusp paced QRS (132-193 ms) | 119.5 FAIL (true 145.0) | **Likely still FAIL, but less certain than at 07:30** (deviation D1, 20 Oct 2026). Longer than v5.1 but short of 132 ms more often than not | The crescents and the cut lengthen the true exit path, but the surface C1 measure misses late basal activation and much of the crescent conduction is pre-QRS latency. A paced comparator does not close the gap either (11.1). D1 leans toward a pass of unknown size (the 9 Oct v3/v4 contrast, 162 against 92 ms paced QRS, shows that basal coverage is a strong lever, though v4 also changed speeds), but the delay D1 adds falls in late basal activation, the part the surface measure already misses (v5.1: 119.5 ms on the surface against 145.0 ms true mode), which is why a fail stays more likely than not (inference); D5's cap leans away, and so does D13's mid-plane ring against the arterial-face reading (section 14; D2's lean is withdrawn: the right bundle is v5.1's, deviation D16, 20 Oct 2026), and D14 and D15 have no lean. A pass would be a calibration result, since gate 1 is a calibration check for D1 |
| 2, relative QRS (1.0785-1.1587) | 1.098 PASS / 1.217 FAIL / 1.143 PASS | **Uncertain; 6G more likely to stay FAIL** | If paced QRS shortens, the unchanged transmural crossing weighs more and the ratio rises; the sheet and the 6G cut change how much LV network survives |
| 3, Daniels order | FAIL (summit and vein both below RVOT) | **Uncertain.** The RVOT index may fall or rise | The cut removes a short RVOT-to-LV path, but the project's J3b test says delaying LV access **raises** RVOT MDI; the summit re-anchor and the crescents move two of the other four values. The cut was found while auditing the fail (limb (i)), and the re-anchor and the crescents change gate 3's sites (limb (ii)), so a pass is a calibration result, not validation (11.5). D5 (cap, reference ring and cusp sites), D13 (the mid-plane ring), D14 (the cut at 47.2 % of the mesh span, which supersedes D6's 12.7 mm) and D15 (the aortic frame) each move it too, and all are calibration checks for it (11.5). D2's RVOT effect is withdrawn: the right bundle is v5.1's (deviation D16, 20 Oct 2026; the 13:51 text: "D2 (the RVOT value) ... while D2 is not aimed at it and gate 3 stays an independent test of D2") |
| 4, Bazan 2006 RV | PASS | **Likely still PASS, but not "unchanged"** | Thin RV wall, transmural speed unchanged; however a lead-field-only change moved the control value 4.4 to 3.6 %, so fix 2, fix 3 and the pose can move it inside the band; the right bundle is v5.1's, unchanged (deviation D16, 20 Oct 2026), so D2's RV change is withdrawn (the 13:51 text: "D2 (the moderator-band RB, 7.2) changes RV activation but is not aimed at the RV depth effect gate 4 scores, so gate 4 stays an independent test of D2"); arm A20 moves it either way (13) |
| 5, Bazan 2007 q in lead I | 5/21 against 3/21 FAIL | **Likely still FAIL** | Fix 2 cuts the cross-fibre source, fix 4 makes the initial dipole less epicardium-to-endocardium, and the graph engine has no diffusive start. The re-anchor and the pairing redefine the pool and the pairs, and the sheet (with D1, D4 and D11) is aimed at the LV subendocardial conduction that a 10 % stimulus engages, the source of the depth contrast gate 5 measures, and D15 places the summit sites through the LCA ostium, so gate 5 is a calibration check for them (11.5) |
| 6, Berruezo shortest RS (20-52 %) | +14.2 % FAIL | **Uncertain; direction not predicted** | The 19 Oct reasoning ("HF cross-fibre speed falls, which widens the epicardial-endocardial difference") is wrong: the epi-endo difference is set by transmural crossing, which is unchanged at 0.336 m/s, and slower in-plane spread lengthens the endocardial baseline. The project's v5 arm-B test cut 6G's RS from 17.6 % to 7.6 % when HF tissue was slowed |
| 7, Durrer | FAIL | **Likely still FAIL overall** | See the parts below |
| 7 (T), 62-100 ms | 113.3 | **Uncertain; could go either way, likely still above 100 ms** | Faster spread along fibres against slower cross-fibre spread; from v5 to v5.1 the same kind of change **lengthened** T from 100.8 to 113.3 ms. D1 adds 0 to a little, away from passing (deviation D1) |
| 7 (a), early LV areas | 0 / 5.5 / 8.7 ms, 1 of 3 within 5 ms | Moves for the first time; 2 of 3 uncertain | The sheet replaces v5.1's trunk and three fascicles inside its envelope with a broad basal septal source and PMJs below the D1 line, and the fascicle paths beyond it are kept (deviation D11, 20 Oct 2026; the 13:51 text said "two fascicle endpoints"). A calibration check for the sheet either way. The patches move to Durrer's positions (D3), and D1 leaves the upper third of the septum junction-free, so whether the central and anterior paraseptal areas are early depends on where the first junctions sit (deviations D1, D3; direction not predicted) |
| 7 (b), LV endocardium by 37.5 ms | 85.2 % | **Uncertain against v5.1; less likely to pass than predicted at 07:30** (deviation D1) | Faster myocardial spread between junctions, and a broader early source; but under D1 the upper third of the septum is reached through muscle, which moves (b) away |
| 7 (c), RV breakthrough 20-31 ms | 27.5 PASS | **Likely still PASS** (deviation D16, 20 Oct 2026; the 13:51 prediction under D2, "Earlier; may fall below 20 ms", is withdrawn) | RV transmural speed unchanged, and the right bundle is v5.1's, its moderator band included, so no RV path is added; the RV items are timed after LV onset, which the sheet sets, so (c) can still move either way (inference). The 13:51 reason ("the moderator-band chain adds a fast path to the anterior RV free wall") is withdrawn |
| 7 (e), His QRS 63-88 ms | 76.0 PASS | Same or slightly longer; likely PASS (deviations D1, D16) | D1 delays the upper septum; the right bundle is v5.1's (D16; the 13:51 text: "D2 advances the RV") |
| 8, no-network control | PASS (7/7 wider) | **Likely PASS, with a smaller margin** (deviation D1) | Now including the new gate-1 site families (ledger); D1 lengthens the network arm's paced QRS, which narrows the gap to the no-network beats |
| 9, monodomain (at least 98 of 108) | **72 of 108, maximum 38 ms, FAIL** (19 Oct 17:42 UTC) | **Likely still FAIL, with fewer misses than 72/108** | Flat-block tuning at each mesh removes the discretisation part of the disagreement, but most misses were peak-picking swaps on the ECG side, and HF cross-fibre propagation at 0.167 m/s may not resolve at 1 mm |
| **Combined** | **2 pass, 7 fail** | **Likely 2 or 3 of 9 pass (gates 4 and 8, plus gate 3 either way); 3 or 4 if D1 carries gate 1 over 132 ms. Gate 6 uncertain; gate 2 more likely to fail, through 6G** (deviations D1-D6 and D11-D16, 20 Oct 2026) | D2's risk to 7(c) is withdrawn (D16; the 13:51 text: "D2 can take 7(c) out of its band"), and gate 7 is already predicted to fail; D5, D13, D14 (which supersedes D6) and D15 move gates 1 and 3 by little |
| Gates expected to stay failed | | **5, 7 and 9; 2 in 6G; and gate 1 more likely than not** (deviation D1) | No change was prompted by the gate-5 fail (the sheet, D1, D4, D11, the re-anchor and D15 are aimed at its mechanism, so a pass would be a calibration result); gate 1's gap is 12.5 ms at best on the surface measure, and D1 is the one change that could close it (gate 1 is a calibration check for D1 by post-lock card 1, so a pass would be a calibration result); gate 7's (T) is 13 ms over; gate 9's comparator is only partly repaired |

### 14.3 Reports and T-wave or QRS quantities with a prediction

| Quantity | v5.1 | v5.2 prediction | Why |
|---|---|---|---|
| A9 RV isochrone length / width (Acosta 1.97 +- 1.2) | 1.10 / 0.97 / 1.23 | Rises in all three hearts; size uncertain | Anisotropy 1.67 to 3.48 (HF 2.31 to 4.79), plus the outflow fibre blend |
| A9 isochrone area (Acosta RVOT 1.1 +- 0.7 cm2) | 155 / 112 / 122 mm2 | Falls | A narrower, longer isochrone covers less area |
| Taggart-style control tissue-only speeds (along / across) | 0.61 / 0.65 m/s | Along rises toward 0.75-0.80; **across stays near 0.65, and tracks the fibre input rather than the cross-fibre input** | The far-field across measure did not respond to the cross-fibre input before (v5 0.48 in gave 0.636 across; v5.1 0.36 in gave 0.65), so predicting "near 0.6" from the cross-fibre change would be reading it the wrong way |
| Near-site apparent speeds, 2-7 mm from an LV free-wall epicardial site | 0.59 / 0.37 (3-10 mm, mid-wall site) | 0.80 / 0.23 within 10 % | Apparent speed matched the input in v5.1 |
| Emergent 6 mm transmural transit (Taggart 12.6 ms) | not reported | 12-13 ms | 6 mm at 0.48 m/s is 12.5 ms (derived) |
| His to first muscle | 21.9 / 40.8 / 20.8 ms | Changes in the LV for the first time, later under D1 (the first LV junctions sit below the D1 line); RV unchanged (deviation D16, 20 Oct 2026: the right bundle is v5.1's; the 13:51 text said "unchanged or earlier (D2)") | The sheet moves the first LV junction (deviations D1 and D11, 20 Oct 2026); D2 builds nothing (D16; the 13:51 text: "the moderator-band chain adds an RV path") |
| 6G His QRS (Strauss, female donor, 130 ms) | 123 ms | Uncertain; wider more likely, and still short of Derval's 165 +- 18 ms | HF cross-fibre slower; the sheet changes the surviving network |
| Transseptal time (Derval 38 +- 15 ms) | 23.4 ms | Longer; still about 1 SD below | Slower HF cross-fibre speed |
| Control His-beat T wave (new) | none | Upright in I, II and V4-V6, **on a margin of about 7 ms** | The endocardial APD is 28 ms longer and the wall-crossing time is 9.9 mm / 0.48 m/s = 20.6 ms, so the epicardium repolarises first by only about 7 ms (derived). A small change in either number flips the polarity, which is why the T wave is shown and never gated |
| HF His-beat T wave (new) | none | **Discordant** (inverted where the QRS is upright), with a longer QT than the control | Under R1.7 (repolarisation = activation + APD exactly) the 7 ms HF transmural APD gap is **smaller than the endo-to-epi activation delay**: 12.3 mm / 0.336 m/s = 36.6 ms in 6G and 10.6 / 0.336 = 31.5 ms in 7D (wall thicknesses from the 12 Oct scorecard), so the epicardium repolarises 24-30 ms **after** the endocardium. Discordance is also typical of LBBB. The 19 Oct "upright" prediction is withdrawn |
| Muscle fraction of the stimulus ball at cusp and supravalvar sites (new) | not applicable | Below 1 at most outflow sites; **a few sites may fail the 4-node capture criterion, and those are counted, not moved** | The sleeve apex is 0.9-1.0 mm and the LCC crescent floor 1.5 mm against a 1.5 mm-radius ball. The clinical 45 % LCC non-capture (Yamada, 13 of 29) is context, not a target: a model has no stimulus current, so the only non-capture here comes from the capture criterion of 8.7 |
| Lin aVL/aVR ordering (report) | not reported | Ordering more likely to hold than the outer bands | The ordering is a geometric effect; the absolute ratio depends on limb placement, which moves it by about 1.3 times (inference) |
| Bulk conductivity (report) | not reported | Along fibres the primary (0.799 S/m) is above the dog in situ 0.40-0.50 and 14 % above Hooks's pig in vivo 0.70. Across (0.248 / 0.242) it is above both the dog 0.14-0.18 and Hooks's 0.16 (51-55 % above). Transmurally (0.298 / 0.263) it is below Hooks's 0.35 (15-25 % below) | Derived from R2.1 and R2.2: 0.174 + 0.625; 0.01181 + 0.236 and 0.00608 + 0.236; 0.06184 + 0.236 and 0.02673 + 0.236. Two of the three dog values come from one lab (Roberts 1979; Roberts and Scher 1982). The 07:30 wording gave only the along and across directions (correction, 20 Oct 2026) |
| Left-septal delta LV time (report 29, new) | not reported | Control and 7D His beats: negative (apical-first), size against -37 ms unknown; 6G: sign uncertain, against Upadhyay's +45 ms in complete block | Under D1 the first septal junctions sit below the upper third, so the line from the sheet origin activates distal-first (deviation D1). In 6G the LV septum is entered transseptally from the RV; v5.1 caps the RV septal junctions at 0.35 of apex-to-base (14 Oct lit-purkinje notes), which leans the entry low and the sign negative, against Upadhyay's basal-or-mid early site (inference) |
| **Dropped from the 19 Oct draft** | | QT and ARI coefficient-of-variation predictions are not made | Template T waves without diffusion miss the T wave in this model class (Nagel 2023; Pezzuto 2017; Neic 2017), so a QT prediction would not be testable on the primary engine |

## 15. Build order for the PC, from the v5.1 tag to the v5.2 tag

### 15.1 Standing rules

- Any run over 10 minutes needs Alex's OK, with an estimate first.
- **No rm -rf.** Where files must go, give Alex the command and let him run it.
- One report when a step is done or blocked. Stop only where a decision may be needed.
- **No step looks at a gate value, and no step is repeated after seeing one.** Acceptance in every step below is a
  geometry, numerics or bookkeeping criterion.
- **Where gates are scored, stated exactly (the 19 Oct claim "gate scoring happens once, in step 8" was not true, since
  gate 9 is scored at step 10 and the engine test follows):**
  - **step 8**: gates 1, 2, 3, 4, 7, 8 on the **graph engine**. These verdicts are **final**; RE+ values are reported
    beside them if RE+ is run.
  - **step 8, held**: gates 5 and 6 are computed at step 8 but **written to a sealed file and not opened** until T4 is
    recorded, because Alex adopted "gates 5 and 6 are scored on whichever engine T4 picks". Their verdicts are published
    once, from the T4 engine.
  - **step 10**: gate 9.
  - **after T4**: gates 5 and 6 published; the section 12 reports and the arms are re-run on the chosen engine where
    the engine matters, with both engines' values printed.
  - **No other gate moves engine without Alex's word and a dated deviation entered before Table A is computed on the
    other engine.**
- Memory: the v5.1 grid ran 4 processes at a peak of 1.35 GB each. Keep that budget; if a step runs out of memory,
  reduce the process count first, then the chunk size, and report the change. Never silently drop beats.
- Every step writes its inputs, its outputs and its acceptance result into LABNOTES with a timestamp.
- **Every acceptance check in 15.2 has a stop rule**: unless a fallback is named in the step, a failed check means
  **stop and report**, with no substitution and no retry on changed settings.

### 15.2 The steps

**Step 0. Read only.** Inputs: the v5.1 tag. Outputs: a report saying the v5.1 tag and files are unchanged, plus the
template run's site and cell type; the openCARP Tomek cell types available; the transmural coordinate v5.1's fibres use;
the atrial and vessel wall conductivity in v5.1; whether the cohort surfaces can be capped as R3.1 says; the mesh contact
area where the free-standing infundibulum fuses to the aortic root or LV, per heart; whether the meshes already carry a
supraventricular crest; **how much muscle already exists above the pulmonary and above the aortic valve planes, per
heart and per sinus** (this feeds the 8.6 cap rule and the 8.5 item 9 report); **whether v5.1 applied the atrial-fit
rotation, with its axis, angle and pivot, and the v5.1 4x4 pose matrix per heart** (this feeds 9.1 and the pose-card
swap-in); **the v5.1 stimulus implementation, confirming radius 1.5 mm**; whether openCARP offers dream.solve; and the
four KIT torso shape IDs for A37. **Added by the re-issue (20 Oct 2026):** report 34, the step-0 conduction geometry
that places the D1 line, the D2 end node (report only under deviation D16), the D3 patch centres (item 14) and the D4 envelope (item 13) blind
(deviations D1-D4, 20 Oct 2026);
report 35, the step-0 outflow geometry, including item (h), the precondition of 8.5 item 9, and item (f), the three cut
candidates (deviations D5 and D6, 20 Oct 2026); the dataset checksums of 17.3 (the md5 of each heart's zip and of
dataset_info.csv, the CRC32 of each heart's mesh files) checked against the values recorded there; the KCL host's record
and file IDs, and the read-only A35 and A36 feasibility checks of 9.4 (deviations D9a and D9b, 20 Oct 2026).
Acceptance: the report exists and the tag matches; **reports 34 (item 3b excepted, which follows step 2g) and 35 are
complete for every heart; every checksum matches 17.3, or
stop and report** (the file set would differ from the one this lock was written against); **if report 35 (h) puts the
tag-1/tag-5 boundary below the aortic valve plane in any heart, stop and report before step 2c** (8.5 item 9; deviation
D5 (a), 20 Oct 2026); **if report 34 item 13 puts a v5.1 fascicle endpoint outside the 22.6 mm envelope (the placement that
applies under the follow-up answer, or either placement while that answer is open), or the envelope off the left septal
surface, in any heart, or, under a declined placement, gives no footprint midpoint at one of its levels, stop and put
the attachment to Alex before step 1** (7.1; deviation D4);
**if item 14 cannot identify a septal boundary or the mitral annulus in a heart, stop and report** (section 11,
gate 7; deviation D3); **if item 8 shows that v5.1's LB_TRUNK and FASCICLE nodes carried no PMJs, or item 4 shows no LV
septal junction above the D1 line in a heart, the step-0 report goes to Alex before step 1** (7.1; deviation D1). A failed A35 or A36 feasibility check is not a stop: the arm is recorded as not run, with the reason.
Stop only if something blocks.
**Run on the 13:51 file; not repeated (deviations D11-D17, 20 Oct 2026).** The PC ran step 0 read-only on the 13:51
file (report README-20261020T170855-4447.md, 20 Oct 2026 17:08 UTC; PC clock 18:32-19:08 CEST): nothing was simulated,
no gate value was looked at and no model file was changed; the v5.1 tag and files matched; every checksum of 17.3
matched; reports 34 and 35 were complete for every heart; 35 (h) passed, and item 14 identified every septal boundary
and the mitral annulus in all three hearts, so neither the 35 (h) stop nor the item-14 stop fired. Two step-0 stops
fired and went to Alex before step 1: the outflow attachments (report 34 item 13), answered by D11, and the D1 counts
(items 4 and 8), answered by D12. A35 and A36 failed their feasibility checks and are recorded as not run (9.4). The
follow-up geometry (report 34 item 15 and report 35 (i)) was measured read-only afterwards (relayed 20 Oct 2026 17:34
UTC; followup.json, local commit a2e25a1). **Step 0 is not repeated on this file**: its outputs and the follow-up
geometry stand, and the build continues at step 1.
- **The gate-1 provenance trace is not a PC task** and is not listed here: that session cannot see /mnt/project-files or
  the cloud notes. It is done in the cloud and recorded in 11.1, and the gate-9 v5.1 status is likewise settled in
  section 11 (FAIL, 72/108) rather than "resolved against Table A" on the PC.

**Step 1. Commit this file.** Inputs: this lock **as re-issued again** (20 Oct 2026 19:28 UTC; deviations D11-D17,
20 Oct 2026; it supersedes the 13:51 re-issue), **finalised after every card, the three post-lock cards, the four
follow-up items and the five step-0 cards included, is answered** (0.1,
0.2), with the Massing values written into 7.1 (deviation D4, 20 Oct 2026; measured 20 Oct 10:33-11:05 UTC). Outputs: section 14
committed verbatim, timestamped, before any v5.2 beat, together with the pre-registered items of 11.1, 11.2, 11.2a,
11.2b, 11.3, 11.4 and report 8, **section 19**, and the file's hash; A37's four torso IDs (T_24, T_20, T_17 and
T_01) entered in LABNOTES in place of the step-0 entry (deviation D17, 9.4). Acceptance: the commit hash is in LABNOTES **and in
PROGRESS.md**; **the committed file holds no unfilled placeholder (a card or follow-up answer, or a re-issue time); if
one remains, stop and report; and each 0.1 answer matches the option its text is drafted on, or the "If declined" text
of section 19 has been applied; if not, stop and report** (0.2).

**Step 2. Geometry.** Inputs: the v5.1 meshes. Outputs, in this order:
- 2a Fix 5 fibres: the LV helix of R5.1 and the outflow blend of R5.2. Acceptance: R5.3, all four checks. (**Re-run
  after 2c and 2d on the merged mesh**, since those add muscle that needs fibres and w.)
- 2b The infundibulum cut (8.2). Acceptance: the two sides share no node and no graph edge crosses the plane at any
  stencil radius; the septal component is still fused; element count and contact area reported; the per-engine treatment
  of 8.2 applied; **the connectivity acceptance of 8.2**. Stop rule as in 8.2. **The split height is the D14 rule of 8.2
  (deviation D14, 20 Oct 2026; it supersedes D6)**: fused below 47.2 % of the mesh's posterior span above the 0 %
  landmark, split above it, the span taken from the first reading of report 35 (f) (as defined there) at this step and
  the 100 % landmark the pulmonary mid-plane ring (deviation D13); the two landmark positions and the span are written
  into LABNOTES, and the D14 boundary, the three candidate boundaries beside it (37.3 %; D6's 12.7 mm above the 0 %
  landmark; 15.3 mm below the ring) with the tag-1/tag-2 area above each, and the posterior span (report 35 (f)) are
  reported before the split is applied. (The 13:51 text: "The split height is the D6 rule of 8.2: fused below 12.7 mm
  above the 0 % landmark, split above it"; superseded.)
- 2c The aortic crescents (8.5; the cusp-muscle card answered "Both"). Acceptance: the hard gate of 8.5 item 9; the angular frame of item 6 as D15 builds
  it (theta = 0 at the mitral-disc centroid's direction, the pulmonary-disc centroid 90-150 deg from it; deviation D15,
  20 Oct 2026; 126.9 / 126.4 / 128.1 deg at step 0, report 35 (i)), its check and stop rule; the re-tagged element list and volumes of item 8b; UVC and w re-solved; the reported element
  counts across each lune; **the 2b cut re-checked**; **the D5 rules applied (deviation D5, 20 Oct 2026)**: the RCC
  axial cap of 8.5 item 2b (H(theta), at most 2.4 mm above the aortic valve-plane ring, the mid-plane ring of deviation
  D13) and the max(existing, lune) rule
  of item 9, both measured from the ring (item 5), parts (a) and (c) as their follow-up answers fix them (if D5 (a) is
  declined, the 07:30 reference line and item 9 text apply, and item 9's two readings go to Alex before 2c); report 35 (b), the axial rise and radial reach of each lune, and
  35 (c), the LCC thickness against 3.0 +- 1.0 mm, written. **Stop rule:** if the item 9 precondition (report 35 (h))
  failed in any heart, step 2c is not started there; stop and report. Nothing is trimmed or moved to make it pass. At
  step 0 it passed in every heart, measured from the mid-plane ring (8.5 item 9; deviation D13).
- 2d The pulmonary sleeves (8.6; the cusp-muscle card answered "Both"). Acceptance: a closed ring; the thickness profile within **one
  element (1.05 mm)** of the 2.0 / 1.7 / 1.0 mm rule at 25 / 50 / 75 %; the built height = max(existing, 4.0 mm) rule
  applied and the achieved heights reported, all measured from the pulmonary mid-plane ring, each sinus's nadir the
  ring's point at the sinus centre (deviation D13, 20 Oct 2026); the fibrous layer tagged non-excitable on the luminal face; blood capped
  at that face; UVC and w re-solved; report 35 re-run, as its header says, after 2b-2d and before any beat: (a) and (h)
  at de Kerchove's six positions and (e) at the L/R commissure and the RCS, all in the D15 frame, with each disc's thickness and two faces and, per position,
  the muscle above each face on the v5.1 mesh (the existing muscle) and on the built mesh (deviations D13 and D15,
  20 Oct 2026); report only, no value or verdict changes (0.3).
- 2e Site sets **against the ledger of 11.2a**: the re-anchored summit sites (the LCA ostium at Toh's theta in the D15
  frame and 14.8 mm above its plane, the aortic disc's mid-plane, 8.3), the cusp sites in crescent muscle (theta in the
  D15 frame and s from the D13 mid-plane ring, deviations D13 and D15; at 50 % of the built extent, after the 8.5 item
  2b cap and the item 9 max rule: 8.5 item 11b; deviation D5 (c), 20 Oct 2026; at 50 % of h(theta) if D5 (c) is
  declined), the three gate-7 (a) patches at the D3 centres written into the manifest at the (z, phi) of report 34 item
  14 (section 11, row 7; deviation D3, 20 Oct 2026; if a boundary or the annulus cannot be identified, stop and report;
  no centre is placed by eye), the three supravalvar sleeve sites per heart (50 % of the sleeve length from the D13
  mid-plane ring), the v5.1 sites kept beside, the no-network sites at the new gate-1 sites, the displaced-site set and
  the intramural-origin set. Acceptance: the placement checks of 8.8 reported; every site inside myocardium or recorded
  as clipped; the capture criterion of 8.7 evaluated and failures counted (never moved); muscle fraction reported per
  site; **the gate-5 position count per region (11.3 item 4), with the fill rule applied if any gated region is under
  20**.
- 2f Heart pose (section 9) and the T13 electrode report (9.4). Acceptance: the 4x4 pose matrix recorded per heart; the
  skin-clearance acceptance of 9.1 (5 mm) met, or stop and report; the electrode-to-myocardium distances and the
  orientation report written.
- 2g **Conduction system (section 7, new in this build order).** Inputs: the v5.1 network and the left septal surface.
  Outputs: the left-bundle sheet built as 7.1 says (6 mm origin, widening to full width by 12.5 mm, 33 mm long, 1 mm
  node spacing, trunk speed for the first 10 mm then fascicle speed), **inside the anterior-posterior envelope of 7.1
  (deviation D4, 20 Oct 2026): 22.6 mm, laid 17.8 mm anterior and 4.8 mm posterior of the His line (if the placement
  is declined, 11.3 mm either side of the v5.1 footprint's anterior-posterior midpoint, 7.1), reached at 12.5 mm
  by the widening of assumption 10 and held to the sheet end**; its PMJ rule applied
  **as D1 fixes it (deviation D1, 20 Oct 2026): the D1 line placed by assumption 46 from report 34 item 10; no PMJ on a
  sheet node above the line and one at every sheet node below it; none in the first 10 mm wherever the line falls; and
  no PMJ on v5.1 LV distal-network nodes above the line on the left septal surface**; the three outflows attached as
  7.1 fixes them under **deviation D11 (20 Oct 2026): the v5.1 LB_TRUNK and FASCICLE nodes and edges replaced only inside
  the envelope; each v5.1 fascicle path beyond it kept exactly as v5.1 built it and joined to the sheet through its own
  v5.1 edge from its exit node (its first node outside, report 34 item 15) to the sheet node at the mesh node of its
  last node inside, or the nearest sheet node, with that edge's v5.1 class and speed; every v5.1 DISTAL edge that
  joined a trunk or fascicle node inside the envelope re-joined to the sheet node at the same mesh node, or the nearest
  sheet node (assumption 56); the septal outflow at assumption 31's node (one 2.0 m/s edge from the sheet node nearest
  the mid-septal point, 7.1)**; **the right bundle v5.1's, unchanged, its moderator-band edge included, and no chain
  built (deviation D16, 20 Oct 2026)**; the 13:51 text built "the moderator-band chain ... as 7.2 fixes it (deviation
  D2, 20 Oct 2026): 1 mm nodes at 1.5 m/s, no PMJ on the free-running segment, from the v5.1 RB end to the end node of
  assumption 47, which joins the nearest v5.1 RV distal-network node and carries a PMJ" (superseded by D16); the
  retrograde rule of 7.3 implemented; the 6G cut applied as 7.8 defines it. Acceptance: origin width 6 mm within one
  element; length 33 mm within one element; **the built full width within one element of 22.6 mm from 12.5 mm to the
  sheet end, with its anterior and posterior extents within one element of 17.8 and 4.8 mm (of 11.3 and 11.3 mm about
  the footprint midpoint if the placement is declined)**; one connected sheet; the edge classes and speeds as
  written; **no PMJ inside the first 10 mm; no PMJ on any sheet or LV distal-network node above the D1 line and one at
  every sheet node below it, with the removed junctions counted per heart and per AHA segment (report 34 item 4)**;
  report 34 item 3b (the sheet nodes per septal third, above and below the D1 line) completed; **the D11 acceptance:
  every v5.1 LV distal-network node reachable from the His through the sheet, as in v5.1 (6G8DD8S5 checked before its
  cut; after the cut, 7.8 applies); the kept fascicle paths identical to v5.1's from the exit node to the endpoint,
  with each join edge as assumption 56 states; per heart the exit node, kept length and join edge (its two nodes, class
  and length) of each fascicle path and the number of distal edges re-joined reported (report 34 item 15)**; **v5.1's
  right bundle bit-identical, its band edge's length reported against Lee and Hur's 13.6 mm and assumption 54's 37.8 mm
  (report only, deviation D16; report 34 items 6 and 12)**; the 13:51 acceptance ("the moderator-band chain connected
  from the RB end to its end node, with no PMJ before the end node, its length reported against Lee and Hur's 13.6 mm
  and no longer than 37.8 mm") is superseded by D16; the metrication error reported; for 6G, 0 sheet or LV Purkinje
  nodes reachable antegradely from the His, the sheet still connected, and the removed edge list recorded. **Stop rules
  (deviations D1, D4, D11 and D16, 20 Oct 2026):** if the D1 line cannot be placed on a heart (no septal crest or
  crest-to-apex length identifiable, report 34 item 10); if any v5.1 LV distal-network node is unreachable from the His
  through the sheet (D11; no edge is added to reach it); or if the envelope cannot be laid on a heart's left septal
  surface, or a v5.1 fascicle endpoint lies outside it without Alex's word on the attachment (report 34 item 13; given
  at step 0 as D11, step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC): stop and report. The 13:51 stops on
  assumption 47 ("if no node satisfies assumption 47 ...") and on a chain longer than 37.8 mm (assumption 54) are
  withdrawn with the chain (deviation D16). A declined D4 placement (17.8 / 4.8 mm) is not a stop: the envelope is
  centred on the v5.1 footprint's anterior-posterior midpoint with the 22.6 mm width (7.1; the midpoint interpolated
  between report 34 item 13's levels, a level without one having already stopped the build at step 0) and the build
  continues. No line, attachment or width is guessed, and nothing falls back to a 07:30 or 13:51 rule without Alex's
  word.

**Step 3. Fix 4 speeds into the engines.** Inputs: params/v52_speeds.json. Outputs: the slab refit and acceptance A
(R4.1), with the R4.2 fallback if needed; then acceptance C as a report (R4.3), with Alex's OK for the time.
Acceptance: A's tolerances, or a reported stop.

**Step 4. Fix 1 cell runs.** Inputs: the openCARP Tomek model. Outputs: the endocardial and epicardial single-cell runs
at **CL 1000 ms** to steady state, both APD90 values, the two last beats at 1 ms, the per-w time-stretch factors and the
**splice continuity offsets** of R1.2, the HF factors, **and the RE+ ionic scalings of 15.3 (the IKs scaling that
reaches mean APD90 x 1.110 and a 7 ms transmural difference)**. Acceptance: the steady-state criterion of R1.1 met; the
blended field's endo-epi APD90 difference equals 28 ms within 0.5 ms in the control heart and 7 ms within 0.5 ms in the
HF hearts; no cell-type step anywhere in w; the template-only check of R1.2 run and reported.

**Step 5. Fixes 2 and 3.** Inputs: the cavity surfaces, R2.1-R2.2, R3.1-R3.3. Outputs: cavity surfaces and their gates
(R3.2); the conductivities, checked against the table in section 3; lead fields one heart at a time (about 6-8 min each),
then C9. Acceptance: R3.2's five checks; the R2.3 assertion to 1e-6; C9 as in v5.1.

**Step 6. Monodomain calibration.** Inputs: the v5.2 speeds and the fix-2 sigma_e. Outputs: **flat-block tuning with
straight fibres** (R4.4) at the hearts' element size and at 1.0, 0.5 and 0.2 mm, with the tuned sigma and achieved CV
published at each, the in-heart achieved speeds and signed bias (amendment 3); the one-off **Niederer N-version slab run
at 2 ms and 50 000 uA/cm^3** (11.4 item 3). Acceptance: achieved CV within 3 % of each target, or a reported stop if
0.167 m/s cannot be reached; the slab's last activation inside 37.8-48.7 ms, **or stop and report** (11.4 item 3).

**Step 7. Beats.** Inputs: everything above. Outputs: the three His beats first, then **every beat in the ledger of
11.2a** (Alex's OK with an estimate, since the ECG window is longer than v5.1's and the ledger is larger than 579).
Acceptance: no unactivated node in any beat; **the beat count and families equal to the ledger** (not "identical to
v5.1's", which the new sites contradict); the His beats reproducible twice; the v5.1 beats bit-identical where nothing
that affects them changed.

**Step 8. Scoring.** Outputs: Table A with v5 / v5.1 / v5.2 columns **for gates 1, 2, 3, 4, 7, 8**; **gates 5 and 6
computed and sealed** per 15.1; Table C; the section 12 reports beside the section 14 predictions; the LBBB items for
6G8DD8S5. Acceptance: every scored gate has a verdict or "not evaluable"; every calibration check of 11.5 is labelled as
such in the output; no gate definition differs from section 11.

**Step 8a. Arms.** Outputs: **the 38 numbered arms of section 13 plus the sub-variant A19b, 39 arm entries**
(the 07:30 text said 35 arms, a miscount of its own 36-arm list, corrected 20 Oct 2026; deviations D1, D8 and D10 add
A39, A40 and A19b, 20 Oct 2026), **A35 and A36 only if their step-0 feasibility checks passed** (9.4; deviations D9a and
D9b, 20 Oct 2026; A36 only if D9b is adopted); **at step 0 both failed, so both are recorded as not run and step 8a
runs at most 37 of the 39 arm entries** (9.4, 19.15.8; A17, A18 and A20 are also recorded as not run if their reachability checks fail, 7.1, 7.2); **A37 on T_24, T_20, T_17 and T_01** (deviation D17, 20 Oct 2026); in
their stated scopes, with the lead-field rule of section 13
(any arm that changes sigma, fibres or pose recomputes lead fields, one heart and one arm at a time, single process),
the per-arm beat scope as the table states it, and a running memory log. Acceptance: every arm either has results or is
recorded as "not run", with the reason; no arm value differs from section 13.

**Step 9. Tag v5.2** after Alex's go: manifest, LABNOTES entry, dated deviations for fixes 1-5 and for every change in
sections 7 to 10, **and deviations D1-D10 and G of section 19 (20 Oct 2026), each with Alex's card or follow-up answer, and D11-D17 of
19.15 (20 Oct 2026), each with its step-0 card answer**.

**Step 10. The monodomain gate.** Outputs: 27 beats offline, one heart per night, started by Alex with run_offline.sh,
plus the local mesh ladder, and the sinus and 6G LBBB beats of 11.4 as **report-only** runs outside the 108 pairs; the
score; and, if it fails, the 12-beat bias run offline (about 8-9 h) for the Aim 2 bias band only. Acceptance: the gate
rule of section 11 unchanged.

**Step 11. The engine test** (locked below).

**Step 12. Final report** in the v5.1 format, with gates 5 and 6 published from the T4 engine.

### 15.3 The engine test (Alex chose "Test first", 19 Oct 18:44:03 UTC), with its eight amendments

- **T0. Read only.** Say which reaction-eikonal variant the installed openCARP offers. **RE+ with diffusion
  (dream.solve = 1) is the variant tested; the version without diffusion is only a named fallback.** Say whether it can
  take the v5.2 speeds, fibres and cell settings, and seed the graph network's junction exit times as the monodomain runs
  replay them. If it cannot, stop and report. **Also read only (report 33, added 20 Oct 2026):** say whether the
  installed openCARP has a released, documented bidirectional Purkinje-myocardium coupling. If it has none, the absence
  is recorded as a limitation and no coupling is built; that finding is not a stop.
- **T0b. Time one beat first** against Neic 2017 (1,582 s on 24 cores). A gap of about 20 times points to configuration,
  not to the method; if it appears, **stop and report** before T1, and record the configuration checked.
- **T1.** It runs after the v5.2 tag, beside step 10's monodomain beats, at the same 27 sites with the same lead fields
  and the same conductivity set, over the R1.6 window. **RE+ ionic settings for T1, fixed now:** ToR-ORd with the
  transmural blend realised as a per-node interpolation between the endocardial and epicardial parameter sets in w (as
  the monodomain, 11.4), the R1.4 APD target map, and the HF factors reached by **scaling IKs conductance** - the named
  repolarising current - to hit mean APD90 x 1.110 and a 7 ms transmural difference, with the scalings computed in
  step 4 before any RE+ beat.
- **T2. Report for each engine** (graph eikonal, RE+) against monodomain by the locked gate-9 rule (4 measures, 5 ms,
  108 pairs): pairs within 5 ms; the maximum difference; the misses by measure; **and** the achieved plane-wave CV per
  axis per element size, the in-heart achieved speeds and signed bias (amendment 3), the per-pair differences against
  activation time and against distance from the stimulus, the full spread of differences, the change in total activation
  time from adding network detail, and the time per beat, per simulated ms and projected for the ledger. Beside it: the
  published whole-heart engine agreement, 75 % of activations within 7.5 % (Neic 2017).
- **T2b. Mesh.** Re-run the 3 ladder sites per heart (11.4 item 1, local refinement, chosen by the recorded seed).
  Without it an engine difference cannot be told from a mesh difference.
- **T2c. Scope.** The test checks tissue and ECG only: every engine replays the graph network's junction times (one-way
  coupling, as approved). Count the misses at sites whose early activation is junction-driven. The sinus and LBBB beats
  are reported here too, as tissue-and-ECG reports outside the 108 pairs (11.4 item 5).
- **T3. Held-out check, with its threshold set now.** The 12 bias-run sites (fixed seed, one per uncovered region per
  heart) are run in monodomain and in **both** candidate engines, giving **48 held-out site-measure pairs** (12 sites x
  4 measures). The held-out criterion is **at least 90 % of the 48 pairs within 5 ms**, the same tolerance as the gate.
- **T4. The engine rule, mechanical and binding.** **RE+ becomes the engine for gates 5 and 6 if and only if**: (i) it
  agrees with monodomain in **at least 10 more of the 108 pairs** than the graph engine does, **and** (ii) it meets the
  T3 held-out criterion (at least 90 % of 48 pairs within 5 ms) while the graph engine does not, or meets it by a wider
  margin, **and** (iii) **it can run**, defined as: T0 passes, T0b shows no unexplained 20x gap, and every beat of the
  ledger completes **without numerical failure** (no divergence, no non-convergence, no NaN) - **not** a time limit,
  since PC time is not a constraint (Alex, 19 Oct 18:37). Otherwise the graph engine stands.
  - **Alex still signs off**, but the rule is written before the test, with its margin and its threshold. If he departs
    from it, that is recorded as a dated deviation **with its reason, before the sealed gate-5 and gate-6 values are
    opened**.
  - **Gates 5 and 6 are the only gates this decides** (the adopted list: "Gates 5 and 6 are scored on whichever engine
    T4 picks"). The gate-1, 2, 3, 4, 7, 8 verdicts of step 8 stand on the graph engine whatever T4 says, and gate 9's
    comparator is unaffected. This is the whole repair of the 19 Oct draft's post-hoc lever: previously the Aim 1
    verdict came "from the engine Alex picks at T4", after every graph-engine verdict had been seen.
  - Section 14 carries a prediction row for this choice.
- If RE+ is chosen for gates 5 and 6: those two gates are computed on it and published; Table A's other rows keep the
  graph engine with RE+ printed beside; the section 12 reports and the arms are printed for both engines where the
  engine matters; its diffusion uses the fix-2 conductivities; fix 1's cell-type and APD rules (R1.3-R1.5) become ionic
  settings as T1 states; fix 1's template rules (R1.2, R1.6, R1.7) fall away for that leg.
- **The CL 600 subset, fixed now:** the **9 gate-9 sites per heart (27 beats)**, each after a **10-beat train at
  CL 600 ms**, the only way to test H5 and coupling-interval effects (Goyal 1996, still to be read). Report only, and in
  the ledger.
- Initial-phase measures (report 15) are added to the engine test.
- Cost estimate for RE+, inference: RE- took about 40 min a beat on 3 Oct (the simulated window is not recorded in the
  cloud notes); monodomain runs 16-20 s per simulated ms; a beat long enough for a T wave (about 600 ms) could take up to
  about 3 h, so weeks to about 2 months for the ledger. Aim 2 would need the bigger computer.

## 16. Model assumptions (no source; every one fixed before any beat)

| # | Assumption | Where | Why it is an assumption |
|---|---|---|---|
| 1 | Extracellular space transversely isotropic (transmural = cross-fibre) | R2.1 | Clerc measured two directions |
| 2 | Atrial muscle isotropic at 0.248 / 0.242 S/m | R3.3 | Derived from the ventricular cross-fibre bulk; no atrial measurement used |
| 3 | Aortic and pulmonary wall 0.2 S/m | R3.3 | Inside Keller's range; no direct measurement. The nearest measurement read, Schwan and Kay 1956 p.666 (pieces of vein, pulmonary artery and bronchus, 0.14-0.40 S/m derived; species, n and frequency not stated; the aorta not measured), brackets it (relabel, 20 Oct 2026) |
| 4 | The atria and great-vessel walls are passive conductors | section 4 | No atrial excitation in this model |
| 5 | 0.48 m/s used as a tensor transmural speed, labelled an apparent wall-crossing speed | section 5 | Taggart's plunge-needle value is not a sheet-normal measurement |
| 6 | Human in-plane speeds used as tensor speeds | section 5.2 | They were measured near a pacing site, where the model's apparent speed equals its input |
| 7 | One Lombaert helix profile for every heart and every region of the LV body, apex included | R5.1 | Lombaert's apex differs but prints no numbers |
| 8 | The LVOT blend band's extent | R5.2 | Doste states the end angles, not the band |
| 9 | **Rewritten (deviation D4, 20 Oct 2026; post-lock card 2, change 4, "Adopt all", 20 Oct 2026 11:23:21 UTC).** At 07:30 the LB sheet's anterior-posterior envelope was taken from the v5.1 LV septal node footprint. Now: the LB sheet envelope laid on the mesh: the drawings' horizontal (anterior-posterior) direction is taken as the mesh's anterior-posterior direction on the left septal surface, perpendicular to the base-to-apex direction; the drawn widths (projected chords) are laid out as surface distances; and the 17.8 / 4.8 mm split about the His line is kept at every level while the sheet widens. The width (22.6 mm, n = 7) and the anterior share (0.79) themselves are derived (7.1); the share is a post-hoc output, used under the follow-up answer "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; if that answer declines it, the envelope is centred on the v5.1 footprint's anterior-posterior midpoint at each level, 11.3 mm either side (derived: 22.6 / 2), with the measured 22.6 mm width, and the build continues (7.1); the midpoint is read at report 34 item 13's 2.5 mm steps and the sheet end and interpolated linearly between them, never extrapolated, and a level with no footprint midpoint stops the build after step 0 (7.1). If D4 is declined, the 07:30 footprint applies | 7.1 | Massing's photographs carry no depth and no surface coordinates |
| 10 | LB sheet widening complete at 12.5 mm (kept as locked) | 7.1 | Midpoint of Elizari's 10-15 mm. Massing's drawings do not support it (the width at 12.5 mm is a median 0.64 of each heart's maximum, IQR 0.56-0.71, and the widest level is at 0.89 of the length; human ex vivo, n = 7; 7.1); reported, not changed: replacing it needs Alex's own word |
| 11 | Retrograde PMJ rule as written (bidirectional junctions, earliest-time solution) | 7.3 | An eikonal solver cannot discover it |
| 12 | Crescent shape a half-sine lune peaked at the angular midpoint | 8.5 item 4 | Toh gives neither shape nor peak position |
| 13 | Crescent reference line = **the aortic valve-plane ring**, standing in for the leaflet hingeline (deviation D5 (a), 20 Oct 2026, a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; the 07:30 line, the mesh LV-myocardium to aortic-wall boundary, is withdrawn, and applies again if D5 (a) is declined); on the mesh, the **mid-plane ring** of the aortic valve disc (deviation D13, 20 Oct 2026; assumption 55) | 8.5 item 5 | The meshes have no leaflets |
| 14 | **Rewritten (deviation D15, 20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC).** Crescent angular frame: theta = 0 at the direction of the mitral-disc centroid, projected onto the aortic disc's mid-plane about the root's central axis (the aortic disc's normal through the aortic ring's centroid); theta increasing in the sense that puts the pulmonary-disc centroid, projected the same way, 90-150 deg from theta = 0; no offset for Toh's -1.3 deg continuity centre. It serves every use of Toh's theta (8.5, 8.3 step 1, report 35). Its plane, the aortic disc's mid-plane, is also the virtual-basal-ring plane from which the LCA ostium height of 8.3 step 1 is measured, along the root's central axis. The 13:51 anchor, "the ring point nearest the mitral ring", is withdrawn: the aortic and mitral discs never touch on these meshes (7.66-8.84 mm apart; report 35 (i)), and its check failed in every heart | 8.5 item 6; 8.3 step 1 | Toh's zero is an interleaflet-triangle bisector, which the mesh does not carry; that the continuity's centre faces the mitral-disc centroid is the mesh's reading of Toh's anatomy |
| 15 | **Crescent thickness: local LVOT wall thickness at the hinge, tapering linearly to 1.0 mm** | 8.5 item 7 | Toh reports no thickness anywhere. Never resized after a run |
| 16 | Sleeve height 4.0 mm uniform over the three sinuses | 8.6 | Derived mean; Lis found no significant difference |
| 17 | Sleeve thickness held at 1.0 mm from 75 % of its length to the end | 8.6 | Lis measures three levels only |
| 18 | Sleeve sinus placement anchored at the ring point nearest the aortic root, others at +- 120 deg; the ring is the pulmonary mid-plane ring, and each sinus's cusp-insertion nadir is that ring's point at the sinus centre (deviation D13, 20 Oct 2026; assumption 55) | 8.6 | The meshes carry no sinus labels, leaflets or nadirs |
| 19 | Supravalvar site at 50 % of sleeve length, mid-thickness | 8.6 | A choice of where to pace in a 4 mm sleeve |
| 20 | Groove fat values tapered to the neighbouring wall value | 9.4 | Abbara's groove values are maxima |
| 21 | 45 deg quadrant bisector for the V1 and V2 displacement direction; T13 intercostal pitch from its own V2-to-V4 offset; half-vectors if the primary respiratory phase is unknown | 9.4 | Wenger gives quadrants, not angles; T13 has no ribs; McLeish's phase is not matched to the CTs |
| 22 | Two-pass filter designed so the combined response meets the stated cut-off | section 10 | Kligfield gives no dB definition |
| 23 | The 10 % of the 132-193 ms band | section 11 | Unsourced; Alex chose it on 4 Oct |
| 24 | HF transmural APD difference 7 ms (derived by applying a wedge ratio to an intact value) | R1.5 | No intact human HF measurement exists |
| 25 | Glukhov's CL 2000 ratios applied at CL 1000 | R1.5 | An inference across rates |
| 26 | Sheet edge speeds taken from v5.1's trunk and fascicle values | 7.1 | No human bundle-sheet velocity exists |
| 27 | **Withdrawn (Alex, 20 Oct 07:22:39 UTC).** The retrograde delay is v5.1's 2 ms, sourced to Vergara 2016; 4 ms equal to antegrade is arm A22 only | 7.3 | - |
| 28 | Splice window +80 to +100 ms, with a constant continuity offset and a post-+80 ms time-stretch | R1.2 | The template and the cell trace are two different sources joined inside the beat |
| 29 | APD90 target map holds the **mean** of the two cell types fixed | R1.4 | Any of mean, endo or epi could be held; the choice sets the absolute map |
| 30 | **Replaced (deviation D1, 20 Oct 2026; post-lock card 1, "Junction-free", 20 Oct 2026 11:22:09 UTC).** The 07:30 LB sheet PMJ rule (none in the first 10 mm, one at every node beyond it) is now arm A39's; the primary is D1's mask, placed by assumption 46 | 7.1 | Massing gives distributions, not junction densities; the 07:30 rule was added by a build fix of the review, not chosen by Alex |
| 31 | The septal outflow of the sheet attaches at 50 % of its base-to-apex extent (kept as adopted under deviation D11, 20 Oct 2026; v5.1's septal fascicle, which the 13:51 text missed, ends at z 0.50, and its path beyond the envelope is kept as well, assumption 56); the join is one edge at the sheet's 2.0 m/s from the sheet node nearest the mid-septal point, on the His line at 16.5 mm (7.1; deviation D11, 20 Oct 2026) | 7.1 | No source gives a septal endpoint position |
| 32 | The infundibulum-cut landmarks on the mesh (deviation D6, 20 Oct 2026): 0 % = the lowest point of the pulmonary-valve-plane ring's posterior aspect (on the mesh, the pulmonary mid-plane ring, deviation D13, 20 Oct 2026) projected onto the RVOT wall at the tricuspid-annulus level, the mesh proxy for Jakiel's RVOT base; 100 % = the pulmonary valve plane ring, on the mesh the pulmonary mid-plane ring (deviation D13, 20 Oct 2026) | 8.2 | Jakiel measures from anatomical landmarks the mesh does not carry. The split height is now 47.2 % of the mesh's posterior span above the 0 % landmark (deviation D14, 20 Oct 2026; Jakiel's ratio of means, assumption 57); D6's 12.7 mm above the 0 % landmark, which is his (Table 1), is reported beside it (superseded); the landmarks are not his |
| 33 | Lead fields keep a continuous conductor across the cut | 8.2 | The two walls are apposed, not separated; an insulating crack in the volume conductor is not the anatomy |
| 34 | Summit construction: ostium at Toh's theta and height, artery along the AV-groove direction, surface distances | 8.3 | The meshes carry no coronary arteries or veins |
| 35 | Cusp-site positions in the crescents (lune midpoint and quarter points, **50 % of the built extent** after the item 2b cap and the item 9 max rule, mid-thickness; deviation D5 (c), 20 Oct 2026, a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; the 07:30 text said 50 % of h, which applies again if D5 (c) is declined) | 8.5 item 11b | A choice of where to pace inside a 3-6 mm crescent |
| 36 | Fibrous layer represented as a 0.40 mm conductivity-and-excitability tag, not as geometry | 8.6 | It is below the mesh's resolution |
| 37 | Sleeve height capped at max(existing, 4.0 mm); nothing trimmed | 8.6 | Neither extending nor trimming is sourced; this rule adds only what Lis measures |
| 38 | Stimulus capture criterion: at least 4 stimulated nodes | 8.7 | No source defines capture in a model with no stimulus current |
| 39 | CT-pose translation defined by the LA+RA centroid landing where the v5.1 ICP fit put it | 9.1 | "Translated into place" needs a named point |
| 40 | Durrer's three early LV areas as 10 mm-radius patches on the LV endocardial surface, centred (deviation D3, 20 Oct 2026) posterior paraseptal at one third of the distance from apex to base, central at 0.50 on the mid left septum, and anterior paraseptal 10 mm below the mitral annulus (a geodesic along the endocardium); each paraseptal centre on the free-wall side of the AHA septal-to-free-wall boundary at its level, one patch radius (10 mm, geodesic) from it, and the central centre at the phi midway between the anterior and posterior septal boundaries (report 34 item 14) | section 11 gate 7 | Durrer describes areas on a drawing, not in model coordinates; the 10 mm radius, the 10 mm offsets and the circumferential rule are not his |
| 41 | Cassidy-to-AHA/UVC region map, and the basal/apical split at z = 0.55 | 11.3 | Cassidy's numbered sites are drawn on a schematic, not in UVC |
| 42 | Gate-5 pairing: nearest 18 mm inside 13-23 mm, greedy in site-id order | 11.3 | It implements the adopted 18 +- 5 mm geometry deterministically |
| 43 | Mesh-ladder refinement radius 20 mm with a 10 mm transition, fields interpolated, lead fields unrefined | 11.4 | A whole-heart fine mesh is not runnable; the local region is a choice |
| 44 | RE+ HF factors reached by scaling IKs | 15.3 | ToR-ORd offers several candidates; one had to be named before any beat |
| 45 | A33's fixed +- 10 deg / +- 10 mm set and A37's four shapes by record order, **the first four other than the primary T_13: T_24, T_20, T_17 and T_01** (amended by deviation D17, 20 Oct 2026; the 13:51 rule, the first four, began with T_13) | 9.4 | Deterministic stand-ins for an unspecified sampling |
| 46 | The D1 line: one third of the septal crest-to-apex length, measured along the left septal surface from the crest; AHA segments 2-3 and UVC z >= 0.67 reported beside it only (deviation D1, 20 Oct 2026) | 7.1 | Durrer, Cassidy and Upadhyay describe the upper septum in thirds or regions, not as a line in model coordinates |
| 47 | **Withdrawn (deviation D16, 20 Oct 2026).** v5.1 already has the moderator band, so no chain and no end node are built; the PC's step-0 construction is reported only (report 34 item 12). The 13:51 text, kept as history: Moderator-band end node: the anterior papillary-muscle base if the mesh carries one, otherwise the nearest node carrying the anterior RV free-wall label within z +- 0.05 of the septal insertion (deviation D2, 20 Oct 2026) | 7.2 | Lee and Hur give the band's length and septal origin, not a free-wall insertion point on a mesh |
| 48 | RCC axial cap profile H(theta) = 2.4 sin(pi (theta - 135.5) / 70.5) mm, a half-sine over the RCC lune (deviation D5 (b), 20 Oct 2026) | 8.5 item 2b | De Kerchove gives the junction height at mid-RCS (2.4 mm), not its profile across the sinus |
| 49 | Report-29 sampling line: 12 points at 2 mm spacing from the sheet origin toward the apex | report 29 | Upadhyay's catheter is a duodecapolar 2-2-2 mm one (p.6), but its length on the septum is not stated in the text read |
| 50 | Report-32 model window for the Figure-4 metric: 150 ms from 10 ms after the stimulus | report 32 | The model has no Carto window-of-interest |
| 51 | Report-32 filter: zero-phase Butterworth low-pass, 2nd order per pass, combined two-pass response -3 dB at 20 Hz | report 32 | Campos states only "a low-pass filter at 20Hz" (supplement p.5) |
| 52 | A35 host placement: the pilot heart's UVC long and short axes onto the removed host heart's, never moved, scaled or rotated afterwards; host lung overlapping the heart or within 2 mm of its epicardium re-tagged to background; every non-lung host tissue at 0.2 S/m (deviation D9a, 20 Oct 2026) | 9.4 | The heart and the lungs come from different people; the axis registration follows Campos 2026, while the 2 mm clearance and the homogenisation are choices |
| 53 | A36 skeletal-muscle fibres, if the host torso carries none: circumferential, by Klepfer 1997's rule (Fig 4 p.709) (deviation D9b, 20 Oct 2026, a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; moves to 17.3 if D9b is declined) | 9.4 | A modelling convention from another torso model, not a measurement in this host |
| 54 | **Report only (deviation D16, 20 Oct 2026).** The 37.8 mm limit is reported against v5.1's band (14.7 / 18.2 / 10.1 mm, all within it) and is not used as a stop. The 13:51 text, kept as history: Moderator-band plausibility stop: a chain longer than 37.8 mm (twice Lee and Hur's longest type mean, 18.9 mm) stops the build at step 2g, and no node is moved to fit (deviation D2, 20 Oct 2026) | 7.2, 15.2 step 2g | The factor of two is a choice; Lee and Hur give type means only, with no range, SD or upper limit for the length |
| 55 | The valve-plane ring on the mesh's valve discs is the **mid-plane ring**, the closed curve where the disc's mid-plane meets the luminal wall, on both valves: the aortic valve-plane ring of 8.5 (items 2b, 5, 9 and 11b) and of report 35 (a), (b) and (h); the pulmonary cusp-insertion nadir of 8.6 (the ring's point at each sinus centre), the sleeve's height, thickness levels and supravalvar sites; and the 0 % and 100 % landmarks of the cut (8.2, assumption 32) (deviation D13, 20 Oct 2026; step-0 card 2, "Mid-plane", 20 Oct 2026 17:33:39 UTC) | 8.2, 8.5, 8.6 | The mesh valves are solid discs 5.7-6.3 mm thick with no leaflets, hinge lines or nadirs; the mid-plane is the valve plane of the PC's report 35 (taken as the construction's own: inference), and which face an anatomical hingeline would sit on cannot be read from the mesh |
| 56 | The sheet's joins to the v5.1 LV network: each v5.1 fascicle path kept beyond the envelope starts at its exit node, the path's first node outside the envelope (report 34 item 15), and is joined to the sheet by its own v5.1 edge from its last node inside the envelope to that exit node, kept with that edge's v5.1 class and speed and with no PMJ added; the edge's inside end is moved to the sheet node at the same mesh node as that last inside node, or to the nearest sheet node if none shares it, and its length is then the distance between its two end nodes; every v5.1 DISTAL edge that joined an LB_TRUNK or FASCICLE node inside the envelope re-joins the sheet node at the same mesh node, or the nearest sheet node if none shares it (deviation D11, 20 Oct 2026; step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC) | 7.1 | Massing describes interconnected fibre groups fanning out over the left septal surface (pp.609, 614 and 618), not where its fibres join a distal network on a mesh |
| 57 | Jakiel's ratio of means, 12.7 / 26.9 = 0.472 (derived; Table 1, 220 human hearts), mapped onto each mesh's own posterior RVOT span as the septal component's upper limit (deviation D14, 20 Oct 2026; step-0 card 3, "Scale to span", 20 Oct 2026 17:32:47 UTC) | 8.1, 8.2 | Jakiel gives the two heights, not their ratio within a heart; using the ratio of means on meshes 2.0-2.6 SD short treats the mesh's landmarks, not its millimetres, as anatomical |
| 58 | Arm A20's septal-only right bundle (deviation D16, 20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC): v5.1's moderator-band edge is removed; the RB ends at the band's septal insertion, which joins the v5.1 RV distal-network node nearest it by surface (geodesic) distance on the RV endocardium, so that the join does not cross the cavity, by one edge of class RB at 1.5 m/s (the v5.1 RB speed), and the insertion node carries a PMJ with the delays of 7.3; if any RV distal node is then unreachable from the His, A20 is recorded "not run" with the reason, and no edge is added | 7.2, 13 | No source gives where a septal-only right bundle joins the distal network on a mesh |

## 17. Not adopted, and what is still open

### 17.1 No new model changes beyond those above

Everything Alex adopted on 20 Oct is in this file. **No model change is in the primary that was not on the adopted
list**, and the two arms that had crept past it (the Toh Fig 6 rotation correction and the sleeve islands, the 19 Oct
draft's A29 and A30) are moved into the table below. **Reports 17-21, 25 and 26 are report-only additions beyond the
adopted list** and are labelled as such in section 12; they change no value and no verdict, which is why they are not
model changes. Reader proposals that would have changed the model, and that are not adopted, are listed here so that
adopting any of them later would be a visible, dated deviation.

| Proposal | Why not adopted | Kept as |
|---|---|---|
| S3 (Roberts and Scher in situ set) as the primary conductivity set | The evidence rule favours it, but Alex's 18:27 pick named decision 8's Clerc-based rule, and the primary must be fixed before any beat | Arm A9, with the reasoning recorded in R2.5 |
| The right bundle along the moderator band as primary | **Adopted (deviation D2, 20 Oct 2026; post-lock card 2, change 2, "Adopt all", 20 Oct 2026 11:23:21 UTC).** The case rests on anatomy (Stephenson 2017 p.4, n = 1; Lee and Hur 2019, 36 of 38 hearts; Massing 1976 p.615, implicitly), not on the v5.1 RV-onset mismatch. The 07:30 reason overstated Camps 2024, whose Discussion says the endocardial-surface approach "limited the ability to represent the moderator bands and false tendons not bound to the endocardial surfaces" and "can be easily extended to incorporate these new structures"; a graph network can carry a cavity-crossing edge | Primary (7.2); the 07:30 septal-only course is now arm A20. **Dated note (deviation D16, 20 Oct 2026):** v5.1 already carries the RB along the moderator band, so the primary is v5.1's RB, unchanged, and nothing is built; the 13:51 reading of v5.1 as septal-only was wrong, and A20 is now the RB on the septum only with v5.1's band edge removed |
| A finite focal source as primary at cusp and vein sites | It would change the stimulus on the two failing gates it touches | Arm A27 |
| A 2-3 ms Macchi excitation-latency arm beside Herweg's | Two arms standing for one quantity (A26, Herweg 2010, already covers latency). **Corrected (20 Oct 2026):** Macchi 2004 (rat, 8 senescent hearts in situ; detailed maps from one heart) gives an excitation latency of about 2-3 ms paced and about 2 ms spontaneous, read from the map timings of Figs 2-3; no latency distance is stated. The 1.5 mm radius is v5.1's code (PC run note, 16 Oct); Macchi is at most consistent with it in order of magnitude. The 07:30 text called Macchi's value the source of the 1.5 mm ball radius, which was wrong | Recorded in report 2; dropped again on re-check (20 Oct 2026) |
| **Per-heart crescent rotation correction from Toh Fig 6** (the 19 Oct A29) | Not on the adopted list, and unbuildable as described: Toh prints the R2 values (0.3899 LCC, 0.2752 RCC; Fig 6 p.237 and the abstract p.230) but no regression coefficients. The rotation is defined in Methods p.233 against the right fibrous trigone and the L-R interleaflet triangle, which the meshes do not carry; its range is in the Table on p.236; and the Fig 6 regressions relate rotation to the angular extents in degrees, not to the mm widths (page corrections, 20 Oct 2026) | Withdrawn; slot A29 left vacant; dropped again on re-check (20 Oct 2026) |
| **Pulmonary-sleeve muscular islands as an anisotropy perturbation** (the 19 Oct A30) | Not on the adopted list, and the perturbation cannot be specified (reworded, 20 Oct 2026): neither Lis 2021 (islands, p.2272) nor Hasdemir 2007 (discontinuous extensions, p.535; 10 of 26, p.536) gives an island size or spacing, and 0.05-2.1 mm is Hasdemir's thickness of the pulmonary extensions beyond the junction (p.536), not an island size. The sleeve is about 1 mm thick at its apex on a 1.05 mm mesh, so islands near the transition zone would be sub-element, and the supravalvar sites are a report-only family (11.2b), so no verdict could move. Lis's island counts (p.2272) and beyond-zone counts (p.2271) share their numbers, so the mis-assignment of Discrepancies item 9 is real | Withdrawn; slot A30 left vacant; dropped again on re-check (20 Oct 2026) |
| Retrograde PMJ delay 4 ms (equal to antegrade) as the primary | Reversed by Alex, 20 Oct 07:22:39 UTC: 2 ms (v5.1) is primary, sourced to Vergara 2016 p.223 | Arm A22 |
| **Bidirectionally coupled network in the monodomain leg of gate 9** | It would change the locked gate-9 comparator, which is one-way junction replay by the approved rule | Not in gate 9; run as report 33, outside gate 9, only if the T0 check finds a released coupling (15.3); the reason a bidirectional test would matter is recorded in 11.4 item 5 |
| **Trimming mesh muscle above the sourced sleeve height in the primary** | Unsourced mesh surgery on a published mesh, on a failing gate | Arm A30a |
| **Moving gates other than 5 and 6 onto the T4 engine** | Alex adopted the T4 engine for gates 5 and 6 only; moving more gates after their verdicts were seen would be a post-hoc lever | Needs Alex's word and a dated deviation (15.1, 15.3) |
| S1d, ToR-ORd's published three-layer configuration (endo 45 %, mid 25 %, epi 30 % with its transmural current scalings) | It reintroduces the mid-wall layer that R1.3 removes on human evidence | Not run |
| S5, the Hooks orthotropic bulk set | **Adopted as an ECG-only arm (deviation D8, 20 Oct 2026; post-lock card 2, change 8, "Adopt all", 20 Oct 2026 11:23:21 UTC).** R2.7's reason (the bulk ratio cannot be mapped onto this model's speed-solved conductivities) applies to the tissue and source model; it does not apply to a lead-field-only use with the fix-2 sigma_i as the source term | Arm A40 (Hooks 2007 p.e108, pig in vivo; lead field only) |
| Cassidy 1984 as a second gate-7 comparator | A second comparator the model may meet or miss differently would have to be a calibration check, and gate 7 already has three | Reported in the Durrer context only |
| Vassallo's LBBB-specific RV endocardial targets as gate-7 comparators | Same reason | Report 21 context |
| A diffuse-LBBB arm and an intact-Purkinje-activation arm for 6G | The 36 % intact-Purkinje phenotype is a different patient group, not an uncertainty in this heart's cut | Reported in 7.8 |
| A His-course variant arm with Massing's prevalences | The His course changes nothing the model measures, since the His is one node | Reported in 7.1 |
| The sleeve-beyond-the-transition-zone arm | 13.8 % of hearts exceed 10 % of sleeve length; it would extend RVOT muscle on a failing gate | Not run; the maxima are recorded |
| A flat-topped crescent lune as an arm | The shape is already a declared assumption; a second shape on an unsourced thickness adds no information | Not run |
| Supraventricular crest and septoparietal band | Lengths are measured but width and course are not | Step 0 reports whether the meshes already have a crest |
| Liu's asymmetric sleeve (longest on the septal side, 5.6 against 1.7 mm) | Lis found no significant difference between sinuses in 65 hearts | Not built |
| Slower outflow-tract conduction | The only data are mouse and show RVOT speed equal to the RV free wall at baseline; it is the most tempting tuning knob for gate 3 | Limitation (section 5.1) |
| A torso-conductivity arm at 0.22 or 0.25 S/m | T13's 0.2 S/m is the project standard and the comparison values are not measurements of this torso | Recorded in 9.3 |
| Burger's human skeletal-muscle anisotropy values | **Re-checked (deviation D9b, 20 Oct 2026; a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC):** not made A36's primary level. If A36 runs, Burger's 0.417 / 0.148 S/m (human, ratio 2.8; 37 C, 100-1000 c/s, 4 electrodes; n and preparation not given; via Geddes and Baker 1967 Table 4 p.285; the primary paper not read) is one of two labelled levels with no primary between them; which to prefer is settled only after Burger and van Dongen 1961 is read (17.2) | A36, if D9b is adopted and its check passes: (a) 0.202 S/m isotropic with its ratio-7 variant and (b) Burger's pair, both labelled (9.4) |
| Demoting gate 3 | Demoting a failing gate is what the rules forbid, even though the evidence that MDI misleads at the cusps is real | Report under gate 3 |
| A 5 ms antegrade junction delay | Not a measurement of an egress site, and it would help failing gate 1 | Rejected (7.3) |
| Purkinje in the outflow tracts | **Reworded (20 Oct 2026):** the 07:30 "no human evidence" was wrong. De Almeida 2020 (human, n = 3, abstract only) found specialised conducting cardiomyocytes from the base of the anterior papillary muscle to the supraventricular crest and subpulmonary infundibulum; there are no LVOT data. Durrer's late conus (60-70 ms) is still compatible with the current rule, so the rule stays (7.5) | Timing report; De Almeida's full text wanted (17.2) |
| Intramural Purkinje | Human evidence conflicts and the geometry would be invented | Limitation; report 16 |
| Junction density gradient, false tendons, trabeculae | No human counts or positions; the only regional junction-density count found is in pig (Garcia-Bustos 2017, abstract only; 17.2). **Reworded (20 Oct 2026):** a graph network can carry a cavity-crossing edge whatever the mesh resolution, so what is missing is a human source and per-heart position data, not mesh capacity; whether the meshes carry papillary muscles or trabeculae is reported at step 0 (report 34 item 5) | Limitation, with a 10 ms bound on gate 1 |
| Extra late-activating RVOT muscle | Mesh surgery on a published mesh | On hold until the Daniels mechanism report |
| A 36 ms cusp exit delay | It is a pacing stimulus-to-QRS interval, not a focus exit delay | Dropped |
| A 9.1 mm summit wall guard | A clinical route predictor that would reclassify exactly the failing sites: Lin 2016 p.13 (accepted manuscript, PDF p.14; page corrected, 20 Oct 2026) gives the >9.1 mm cut-off (sensitivity 87.1 %, specificity 97.1 %) for ablation at the vein or epicardium against the cusp or subvalvar area, in the same 66-patient sample | Dropped again on re-check (20 Oct 2026); the 8.4 wall-thickness report kept |
| Doste angles across the whole RV | Its two clinical benchmarks disagree, and on v5 evidence it moves gate 3 the wrong way | Wording corrected only |
| GPU monodomain | A second solver to validate, for a comparator and not the primary | In reserve |

### 17.2 Papers still wanted (none blocks the lock)

**Read since the 07:30 lock (20 Oct 2026)**, so rows 1, 2, 4, 9 and 10 of the 07:30 table are closed:

- de Kerchove 2015, J Thorac Cardiovasc Surg 149:425 (10.1016/j.jtcvs.2014.09.042), uploaded 07:44-07:45 as the 2014
  online proof, whose pages 1-9 are the ones cited in this file (not the journal's pages): the junction
  heights and root-base wall thickness used by D5 (8.5 item 2b) and report 35; it cannot confirm what Toh's mm measure
  (8.5 item 3).
- Hasdemir 2007, Pacing Clin Electrophysiol 30:534 (10.1111/j.1540-8159.2007.00704.x), uploaded 07:44-07:45: the
  prevalence conflict is written up with its numbers (8.6; Discrepancies item 11).
- Campos 2026, Supplementary Material (10.1016/j.hrthm.2026.05.023), read from notes/A/2026-10-19-v52-lit/oa/: the
  metrics and window of report 32 and the registration method of A35 (9.4).
- Schwan and Kay 1956, Circ Res 4:664 (10.1161/01.RES.4.6.664), uploaded 07:44-07:45: it gives the 1.0 S/m only as a
  stated round figure (pp.664, 669) and is the primary source of Keller's fat upper bound (p.668) (R3.4, A10, 9.4).
- Kaufman and Johnston 1943, Am Heart J 26:42 (10.1016/s0002-8703(43)90050-x), uploaded 07:44-07:45: dog; the source of
  Keller's blood lower bound 0.435 S/m and lung upper bound 0.134 S/m (Table IV p.49) (R3.4, A10, A35).

**Still wanted (20 Oct 2026):**

| # | Paper | DOI | What it decides |
|---|---|---|---|
| 1 | Spach 1963, Circulation 28:333 | 10.1161/01.cir.28.3.333 | Primary source for the upper third of the left septum devoid of conduction fibres (seen only via Elizari 2017 Fig 12; D1) |
| 2 | Garcia-Bustos 2017, J Anat 230:664 | 10.1111/joa.12594 | The only regional junction-density count found (pig) |
| 3 | Kupersmith 1973, Circulation 47:776 | 10.1161/01.cir.47.4.776 | Human bundle-branch speed, to check the 1.5 m/s trunk (7.4) |
| 4 | De Almeida 2020, Heart Rhythm | 10.1016/j.hrthm.2019.07.033 | Conducting cells in the human infundibulum (read as abstract only; 7.5) |
| 5 | Barber 2021, IEEE Trans Med Imaging | 10.1109/tmi.2021.3073499 | How others built a cavity-crossing right bundle (D2; v5.1 already has one, deviation D16, so it bears on A20 and the record only) |
| 6 | Khelil 2015, Ann Thorac Surg 99:1220 | 10.1016/j.athoracsur.2014.12.034 | A possible third source for the RCC junction height (D5). Abstract only, n = 20, and its +- 0.4 is probably an SE, so it is **not counted as evidence** until the full text is read |
| 7 | Merrick 2000, Ann Thorac Surg 69:556 | 10.1016/s0003-4975(99)01300-4 | Infundibulum lengths around the aortic root (8.2) |
| 8 | Burger and van Dongen 1961, Phys Med Biol 5:431 | 10.1088/0031-9155/5/4/304 | Human skeletal-muscle conductivity, before any Burger value enters A36 (D9) |
| 9 | Rush 1963, Circ Res 12:40 | 10.1161/01.res.12.1.40 | Low-frequency tissue resistivities (R2.6 cites its heart bulk values) |
| 10 | Steendijk 1993, IEEE Trans Biomed Eng 40:1138 | 10.1109/10.245632 | In vivo anisotropic myocardial resistivity by four electrodes |
| 11 | Rijnbeek 2014 supplement, J Electrocardiol 47:914 | 10.1016/j.jelectrocard.2014.07.022 | Lower limits of normal QRS voltage, per lead (report 31) |
| 12 | Gabriel 1996 part III, Phys Med Biol 41:2271 | 10.1088/0031-9155/41/11/003 | The fits behind the 10 Hz torso values (still wanted from 07:30) |
| 13 | Goyal 1996, Circulation 94:2843 | 10.1161/01.cir.94.11.2843 | The coupling-interval effect on paced QRS, for the CL 600 subset (still wanted from 07:30) |
| 14 | Nagel 2023, supplement only | 10.1109/TBME.2022.3196144 | Whether 0.167 m/s resolves on a 1 mm mesh (still wanted from 07:30) |
| 15 | Mori 2023, Card Electrophysiol Clin 15:1 | 10.1016/j.ccep.2022.04.003 | Summit anatomy review (still wanted from 07:30) |
| 16 | Li 2026, Ann Anat 265:152804 | 10.1016/j.aanat.2026.152804 | Summit anatomy (still wanted from 07:30) |

```csv
doi
10.1161/01.cir.28.3.333
10.1111/joa.12594
10.1161/01.cir.47.4.776
10.1016/j.hrthm.2019.07.033
10.1109/tmi.2021.3073499
10.1016/j.athoracsur.2014.12.034
10.1016/s0003-4975(99)01300-4
10.1088/0031-9155/5/4/304
10.1161/01.res.12.1.40
10.1109/10.245632
10.1016/j.jelectrocard.2014.07.022
10.1088/0031-9155/41/11/003
10.1161/01.cir.94.11.2843
10.1109/TBME.2022.3196144
10.1016/j.ccep.2022.04.003
10.1016/j.aanat.2026.152804
```

### 17.3 Open items that are not papers

- **Massing's fan digitisation. Done 20 Oct 2026, 10:33-11:05 UTC; closed** (deviation D4; post-lock card 2, change 4,
  "Adopt all", 20 Oct 2026 11:23:21 UTC; 7.1; notes/A/2026-10-19-v52-lock/massing/METHOD.md, with deviations 1-5 logged with their times before any width was computed and
  deviation 6, descriptive outputs, after). All ten adult panels carry a scale: photographed rulers in Figs 8B, 9B, 10A,
  11A, 11B, 12A and 12B, and drawn bars in 8A, 9A and 10B. Seven were measurable: **22.6 mm** (IQR 20.4-29.9; human ex
  vivo, n = 7), a lower bound toward the specimen margins and the distal fan; assumption 10 is kept and the measured
  profile is reported, not applied. The 07:30 note's "Figures 11-13" should read Figs 8-12 (Fig 13 is neonatal). Its
  by-eye 25-32 mm for case 8 is superseded: inside a hand-traced outline case 8 measures 38.5 mm, a lower bound, but it
  is excluded from the value by the pre-set rule. Its 41 mm check (case 8's drawn bundle against its tabulated 41 mm)
  holds for that heart only: across the seven measured hearts the drawn lengths ran a median 1.11 times Table 1 (IQR
  1.04-1.15).
- **Dataset version check: closed in the cloud (20 Oct 2026).** Concept DOI 10.5281/zenodo.17048090 has exactly two
  versions, 17048091 ("1.0.0", 3 Sep 2025) and 19351401 (31 Mar 2026, current), each with 51 files. They differ in one
  file only (OHV835G6.zip in the first, 98G5I5CE.zip in the second); the three pilot zips and dataset_info.csv have the
  same size and md5 in both, so the pilot meshes are the same whichever version was downloaded on 2 Oct. The pilot rows
  of the csv match report 12 (Y5HYEDL4 control, male, 25; 6G8DD8S5 HF, female, 64; 7D98EVAR HF, female, 65). The donor
  sex stays load-bearing for the cohort benchmark subgroup, and not for the Strauss verdict (123 ms fails both the 130
  and the 140 ms thresholds). **The PC verifies its stored copies at step 0** against:
  - md5: Y5HYEDL4.zip a7e648775f75badcbfddb73df3e1d720; 6G8DD8S5.zip 8e8122eb09e0b1b0a65d13303159576b; 7D98EVAR.zip
    48b4cc87b766d3fe6a70e481deb22f8a; dataset_info.csv 5b5a670d36373535f0013b3b94d2d33e;
  - CRC32 from the zip central directories, if only extracted files are kept (myocardium_AV_FEC_BB_lvrv pts, elem and
    lon; fascicles_lv.vtx; fascicles_rv.vtx; tags_lvrv.json): Y5HYEDL4 a15d542b, fd5ee8b4, 46ebe383, c531067a,
    eaa854b6, 6e271ea0; 6G8DD8S5 3fe32117, 6a0d49b6, b069be97, d8391977, ac8d314d, 49119edb; 7D98EVAR 98f27b73,
    939eef82, 197c680e, 1753e290, 5ddd73c5, 49119edb; and, for Y5HYEDL4's binary files if kept, .belem f6e99f45,
    .bpts ee9fd3f7, .blon 37a73ce5. The Y5HYEDL4 values were re-read independently by the verifier.
- **For the plan rewrite, after v5.2 is final** (not model questions): whether a scar-VT arm stays in Paper 1, given that
  the pilot hearts have no scar while gates 5 and 6 come from scarred or LBBB patients; multiple comparisons, since there
  are 14 q-rule variants, 9 gates, 1 584 beats in the ledger and **39 arm entries** (38 numbered arms plus A19b, some
  entries with several levels or runs; the 07:30 text said 35 arms, corrected 20 Oct 2026; at most 37 of them run, since A35
  and A36 failed their step-0 feasibility checks, 9.4, and A17, A18 and A20 are also recorded as not run if their reachability checks fail, 7.1, 7.2); and re-checking the 10 % QRS-end rule on the filtered,
  noisy model chain - **which, as section 10 now states, can never alter a v5.2 verdict: any change applies forward
  only, with Alex's word and a dated deviation.**
  - **The registration statement is drafted now, before any v5.2 result (20 Oct 2026)**, as text for Alex to approve:
    the primary analysis is the 9 gate verdicts on the v5.2 primary under the locked rules; the arms, the q-rule
    variants and the comparator chains are robustness, reported as ranges; no gate is re-scored on an arm; the arm
    count is the one above.
  - **The QRS-end re-check, fixed now (20 Oct 2026):** the script is prepared now and run only after Alex has read the
    40 model beats. Every candidate rule is scored first on the chain that decides gates 1, 3, 7(e) and 8 (section 10:
    detected onset, 10 uV white noise, seeds 0-9, 0.05-100 Hz, notch off, 1 kHz, median of 10), then on the Kligfield
    comparator chain as a secondary report, with each reader end against the true activation end, as PREREG lines
    60-62 already pre-register. Forward only.
- **Still to do in the cloud once v5.2 is built**: the Proposal's Model tab v5.2 deviation entry, and the Analysis plan
  Decisions line saying the v5.1 freeze was lifted for v5.2.

## 18. Change log against the 19 October draft

| # | Change | Where |
|---|---|---|
| 1 | HF repolarisation: the three per-layer factors replaced by mean x 1.110 and a 7 ms transmural difference (29 ms as an arm) | R1.5 |
| 2 | Control transmural APD difference set to 28 ms from intact human hearts, with the wedge 111 ms demoted to an arm and 0 ms and 21 ms added as named arms | R1.4, A1-A3 |
| 3 | The endocardial and epicardial AP shapes blended continuously in w; no cell-type step at w = 0.5 | R1.3 |
| 4 | 28 ms restated as the blend's target difference, reached by running the cell model at CL 1000 | R1.1, R1.4 |
| 5 | Apex-base arms added (apex +29, base +25 ms), and the Opthof citation reworded | R1.4 |
| 6 | QT and ARI-dispersion predictions dropped; H5 stated as not tested; the RE+ standing rule added | R1.7, R1.8, 14.3 |
| 7 | Clerc provenance recorded (calf, in vitro, 25 C); arm S3 added with its own provenance; the bulk-conductivity report added; the Hooks 4:2:1 caution added | R2.1, R2.5-R2.7 |
| 8 | Wall values set now: atrial 0.248 / 0.242 S/m, aortic and pulmonary 0.2 S/m; blood capped at the sleeve's inner face; arm S4 added with labels; blood anisotropy and haematocrit written with numbers | R3.3-R3.5 |
| 9 | 0.48 m/s relabelled an apparent wall-crossing speed; the Caldwell arm corrected to 0.34 transmural and 0.24 cross-fibre; Anderson's and Glukhov's provenance recorded; outflow speeds sourced to Boukens 2013 | section 5 |
| 10 | Monodomain comparator must be tuneCV-tuned at every element size, with published sigma and achieved CV | R4.4 |
| 11 | LVOT, summit and subvalvar fibres blended to Doste's outflow angles, re-cited to Doste 2019; a circumferential-LVOT arm added; the signed per-region comparison added | R5.2, R5.4, A16 |
| 12 | **Left bundle as a septal sheet becomes primary**, with a central geometry from four human sources, and 1 and 14 mm as arms; gates 2, 5 and 7 become calibration checks | 7.1 |
| 13 | Junction delay: 4 ms antegrade kept and sourced at egress sites, 5 ms rejected, 7 ms added as an arm; **retrograde kept at v5.1's 2 ms** (Alex, 20 Oct 07:22:39 UTC), now sourced to Vergara 2016 (antidromic 2-3 ms), with the mechanism corrected; 4 ms equal to antegrade is arm A22 | 7.3 |
| 14 | Intramural Purkinje kept out, with the human conflict as a report | 7.6 |
| 15 | No outflow network, now sourced to Elizari 2017 with its species | 7.5 |
| 16 | Three outflow changes added: the Jakiel labels, the infundibulum cut and the Kuniewicz summit re-anchor | 8.1-8.3 |
| 17 | Aortic crescents written as a full build rule, with the angular frame, the lune shape, the thickness assumption and the hard gate | 8.5 |
| 18 | Pulmonary sleeves written as a complete ring with Lis's thickness profile; the "circumference share" dropped; the Hasdemir conflict restated without the 22 % figure | 8.6 |
| 19 | The stimulus clipping rule and the muscle-fraction report added | 8.7 |
| 20 | Heart pose moved to each heart's own CT orientation, with the atrial fit as the arm and the CT-phase caveat recorded | section 9 |
| 21 | Measurement chain: Kligfield filters locked per gate, the MedalCare chain folded in, the q-recognition-floor report added, the two similarity metrics written with their equations and the 4.7 % floor | section 10 |
| 22 | Gate 1 comparator provenance procedure with its if/then, and the new site set | 11.1, 11.2 |
| 23 | Gate 5 site map and 18 +- 5 mm pair geometry pre-registered; the locked unmatched comparator kept, with the matched figures beside it | 11.3 |
| 24 | Gate 9: mesh ladder, tuneCV, the Niederer benchmark, HF reported apart, sinus and LBBB beats, the network-detail activation-time report; the gate itself untouched | 11.4 |
| 25 | Gate 3 not demoted; Durrer (a) added to the calibration checks | section 11 |
| 26 | Reports grown to 28 items, with the corrections to the Lin, Acosta, Campos, Kawel-Boehm, cohort-benchmark, transseptal and Prisco lines | section 12 |
| 27 | Arms grown from 24 to **35 adopted arms** (the 19 Oct draft said 37; the two extras were not adopted and are now in 17.1), each with its scope | section 13 |
| 28 | Predictions rewritten as a signed per-change-per-gate table with mechanisms and magnitudes | section 14 |
| 29 | Build order rewritten with inputs, outputs and acceptance per step, and a rule that no step looks at a gate | section 15 |
| 30 | Engine test amended in eight places; RE+ named as the variant tested; the Aim 1 verdict comes from the engine chosen at T4 | 15.3 |
| 31 | Assumptions collected in one table | section 16 |
| 32 | Not-adopted list extended with every reader proposal that would have changed the model | 17.1 |

**Changes made on 20 Oct 2026, after the three reviews of the 19 Oct-20 Oct draft** (every one of them is logged
finding by finding in "Review log (20 Oct 2026)" at the end of this file):

| # | Change | Where |
|---|---|---|
| 33 | Gerstenfeld's MAD denominator corrected to his own (both mean-removed waveforms, pooled over 12 leads); his pacing CL stated as "tachycardia CL, or 400 ms for PVC-only cases" | section 10 |
| 34 | Niederer's stimulus corrected to 50 000 uA/cm^3 (a factor of 1000), with a stop rule if the slab lands outside 37.8-48.7 ms | 11.4 item 3, step 6 |
| 35 | **Gate 9 scored as FAIL on v5.1 (72 of 108, max 38 ms, 19 Oct 17:42 UTC) and the v5.1 tally corrected to 2 pass / 7 fail** | section 11, 14.2, discrepancy 2 |
| 36 | **Gate 3's locked wording restored verbatim** (summit 90, vein 90 and aortic sinus each > RVOT > LV endo 10), the five v5.1 values labelled, and the v5.2 site families fixed in 11.2b | section 11, 11.2b |
| 37 | **Gate 5 written in full**: five matched Table 3 sub-checks with their CIs, the 20-position rule, the Cassidy-to-UVC map, eligibility, a deterministic 18 mm pairing, the 0.05 mV primary q rule, and the matched-versus-unmatched comparator conflict put to Alex | 11.3, section 11 |
| 38 | **Per-gate measurement chain table**, with the 14 Oct convention as primary and the Kligfield chains as a report column; the QRS-end rule made forward-only | section 10 |
| 39 | **Site-and-beat ledger** (1 584 beats), with step 7's acceptance changed from "identical to v5.1" to "equal to the ledger"; gate-8 beats added at the new gate-1 sites | 11.2a, step 7 |
| 40 | **The engine choice fixed before the test**: gates 1-4, 7, 8 final on the graph engine at step 8; gates 5 and 6 sealed until T4; T4 made mechanical with a held-out threshold (90 % of 48 pairs) and "can run" defined; an engine prediction row added | 15.1, 15.3, section 14 |
| 41 | Fix 1's splice given voltage continuity, a step-4 template-only check and a corrected prediction; one APD-map mechanism instead of two | R1.2, R1.4, section 14 |
| 42 | Predictions corrected where they contradicted project data (fix 4 on gates 5, 6, 7; the cut and the crescents on gates 1 and 3; the retrograde delay; clipping; "0" entries on gates 4 and 9) and rows added for every change | section 14 |
| 43 | **Calibration register rebuilt, keyed by change, with unconditional triggers**; "if it moves" and "if it passes" removed | 11.5, 8.2 |
| 44 | Build step **2g (conduction system)** and step **8a (arms)** added; stop rules added to every acceptance check; the cut re-checked after the new muscle | 15.2, 8.2 |
| 45 | Mesh ladder made a local refinement with a tool, an interpolation rule, a seed and a memory stop rule; "if affordable" dropped | 11.4 item 1 |
| 46 | Gate-9 sinus and LBBB beats made report-only outside the 108 pairs; the 1D-network clause dropped; the monodomain's ionic settings stated; the bias-band fallback scoped to Aim 2 | 11.4 |
| 47 | Monodomain tuning restored to Alex's flat block with straight fibres (tuneCV only for starting values), with engine amendment 3 and the sigma-to-engine rule | R4.4 |
| 48 | Crescent and sleeve builds made implementable (re-tagging tag 5 / tag 6, UVC re-solve, resolution-consistent tolerances, fibrous layer as a tag, cusp-site positions, sleeve height cap and arm A30a) | 8.5, 8.6 |
| 49 | Summit re-anchor given a placement algorithm from the LCA ostium, with the Kuniewicz 18.92 mm relabelled the septal margin | 8.3 |
| 50 | Clipping rule given a radius, a connected-component definition, a capture criterion and a corrected prediction | 8.7 |
| 51 | Cusp-muscle-card and pose-card swap-ins rewritten as complete blocks, each with the option not chosen running as an arm | 8.9, 9.2 |
| 52 | CT pose given a translation rule, a skin-clearance acceptance and an orientation report that never chooses the pose | 9.1 |
| 53 | Gate-1 provenance resolved in the cloud (spontaneous band), with the correct sources and a third branch; "can only make the gate stricter" dropped | 11.1 |
| 54 | Arms: A29 and A30 withdrawn to 17.1, the count corrected to 35, the effect column split from the provenance column, A7 restricted to LV-endocardial paced beats, A11's direction corrected, A26 given gate 4, A2's unverifiable source flagged, A21's and A7's dispersions labelled SE, A34 and A33 made deterministic, A35 and A36 marked not run | section 13, 9.4 |
| 55 | Source citations corrected: Prisco's values restored from the main article (p.1153 and Table 2 p.1156), Doste 2019 cited and dropped from the papers-wanted list, Doste 2019 Table 2 added as the A9 in-silico comparator, Bazan's population and p.1404, Anderson's 12 of 14, Massing's p.618 and pp.612-613 and n = 27 non-neonatal, Gami 2011, Lis's 13.5-13.8 mm, Zenodo record 19351401, Toh Fig. 3, Yamada 2010 JCE 21:170 with "7 (27 %)", Nagel's 0.15 m/s and RE+ APD90 1.13 +- 1.69 ms, Glukhov's M-cell interpretation, A11's unrounded 0.235 / 0.173 | sections 2-13 |
| 56 | HF His-beat T wave predicted **discordant**, with the control's upright T stated as a 7 ms margin | 14.3 |
| 57 | Sobol design specified (factors, ranges, N, estimator, beat budget) and scar dropped as untestable in v5.2 | report 8 |
| 58 | 0.2 corrected: only step 0 may run before the cards are answered | 0.2, step 1 |
| 59 | Assumptions 27-45 added for every value this review fixed | section 16 |

**Changes after the 07:30 lock (the re-issue, 20 Oct 2026).** Rows 60-79 record the deviations, reports and corrections
of section 19. All were written after the 07:30 lock and before any v5.2 beat; nothing had run on the PC.

| # | Change | Where |
|---|---|---|
| 60 | D1: no PMJ above the D1 line on the left septal surface, on the sheet and on the v5.1 LV distal network; the first 10 mm junction-free in every heart; the 07:30 rule becomes arm A39 | 7.1, 13, 14, 15.2 steps 0 and 2g, 16 (30, 46), report 34 |
| 61 | D2: the right bundle along the moderator band as primary; the septal-only course becomes A20 (superseded in substance by D16, row 85: v5.1 already has the band, and nothing is built) | 7.2, 13, 14, 15.2 step 2g, 16 (47), 17.1, report 34 |
| 62 | D3: gate 7(a) patch centres corrected to Durrer's positions; no patch on the code's Durrer points | section 11 row 7, 15.2 step 2e, 16 (40), report 34 |
| 63 | D4: the sheet's anterior-posterior envelope from the Massing digitisation, 22.6 mm (human ex vivo, n = 7; method written before measuring, its deviations logged); assumption 10 kept and the profile reported, not applied; the placement 17.8 / 4.8 mm about the His line a follow-up item; the step-0 endpoint check (report 34 item 13) | 0.1, 7.1, 14.1, 15.2 steps 0, 1 and 2g, 16 (9, 10), 17.3, report 34 |
| 64 | D5: crescents: (b) the RCC axial cap 2.4 mm (post-lock card 2); (a) max(existing, lune) from the aortic valve-plane ring, with precondition and stop rule, and (c) cusp sites at 50 % of the built extent, both follow-up items with the 07:30 text as their if-declined swap-in; A28's effect restated | 8.5 items 2b, 5, 7, 9, 11b, 12; 11.2a; 11.5; 13; 14; 15.2 steps 0, 2c, 2e; 16 (13, 35, 48); report 35 |
| 65 | D6: the infundibulum cut fused up to 12.7 mm above the 0 % landmark, the landmark relabelled, three boundaries reported (the 12.7 mm height superseded by D14, row 83; the landmarks kept) | 8.1, 8.2, 15.2 step 2b, 16 (32), report 35 |
| 66 | D7: A10 blood levels 0.63 and 0.89 S/m; 0.435 and 1.0 S/m kept as labelled extremes, not run; R3.5's alignment sentence rewritten | R3.4, R3.5, 13 |
| 67 | D8: the Hooks bulk set as ECG-only lead-field arm A40, implied sigma_e asserted positive; R2.7's caution reworded | R2.7, 13, 14, 17.1 |
| 68 | D9a: A35 in the KCL host torso, feasibility-gated, with its step-0 check (post-lock card 2). D9b: A36's read-only feasibility check on the Moss/Wuelfers/Seemann torso and its two labelled levels, the adopted 0.202 S/m and Burger's 0.417 / 0.148 S/m (a follow-up item; not run if declined) | 9.4, 13, 15.2 steps 0 and 8a, 16 (52, 53), 17.1, 17.2 |
| 69 | D10: sub-variant A19b, no LV junctions in AHA 4 and 5, labelled tuning-shaped toward gate 1 | 7.7, 13, 14 |
| 70 | G: the Targeted calibration-check rule; 11.5 and the section 11 and 14 calibration columns re-derived | 0.1, 7.1, 11, 11.5, 14 |
| 71 | Reports 29-35 added, report only | 12, 14.3, 15.2 step 0, 15.3 T0 |
| 72 | Arm count corrected: the 07:30 text said 35 but listed 36; now 38 numbered arms plus A19b, 39 arm entries | 13, 15.2 step 8a, 17.3 |
| 73 | Wording, page and provenance corrections (19.13) | R2.6, R2.7, R3.3, R3.4, 7.2, 7.4, 7.7, 7.8, 8.4, 8.5, 8.6, 9.4, reports 2 and 7, 13, 14.3, 17.1, Discrepancies 7, 11, 17, review log B27 |
| 74 | 17.1 rows re-checked and reworded; 17.2 rewritten (five papers read, sixteen wanted); 17.3 Massing and dataset items closed, the registration and QRS-end items fixed | 17 |
| 75 | Assumptions 3, 9, 13, 30, 32, 35 and 40 rewritten; 10 kept with a note; 46-54 added | 16 |
| 76 | Step 0 extended (reports 34 and 35, the checksums, the KCL IDs, the A35 and A36 checks); step 1 commits the re-issued file and refuses an unfilled placeholder; step 9 enters section 19; T0 checks for a released bidirectional coupling | 15.2, 15.3 |
| 77 | Header, 0.1 and 0.2: the 08:28:47 question, the re-review, the three cards and the re-issue recorded | header, 0.1, 0.2 |
| 78 | Finalisation of the re-issue (20 Oct 2026): the Massing value written into 7.1, 16 and 17.3; the post-lock cards named apart from the cusp-muscle and pose cards; four follow-up items with their if-declined text; the 11.5 (ii) wording; D2 and fix 5's outflow blend labelled; report 34 items 3b, 13 and 14; the moderator-band stop (assumption 54); arithmetic and page corrections (19.13) | throughout; 19 |
| 79 | Labels kept to post-lock card 3's wording (20 Oct 2026): clause (iii) is only the label card 1 stated (gate 1 for D1); four 07:30 labels withdrawn: fix 4 (gates 1 and 7), fix 5's LV helix (gate 5; neither limb applies), the sleeve existing-muscle rule (gate 3) and the sheet (gate 3, from the 07:30 section 11 cell); no label given where it would rest only on retrograde entry or on gate 8's network arm (the sheet on 1, 8; D1 on 3, 8; D2 on 1, 3, 4, 8; D4 on 1, 3, 8), with the depth-contrast reading of 11.5 for gates 2, 4, 5 and 6 (the sheet, D1 and D4 keep 2, 5 and 6; D2 not on 4); gate 8 given by one site test to every change labelled for gate 1 under (ii) by its sites (the outflow blend, the cut, the stimulus rule and D6 added); the sheet's gate-7 RV items given their reason (timed after LV onset) and inherited by D1 and D4, D1's 7(e) not being a sheet part; the sleeves' gate-3 reason written. If the D4 placement is declined, the 22.6 mm envelope is centred on the v5.1 footprint (the midpoint interpolated between report 34 item 13's levels; a level without one stops the build after step 0) and the build continues; the step-0 endpoint stop is tested against the envelope that applies, or both while the answer is open. The Massing outputs located in the shared folder; the D6 24-27 mm span labelled a review estimate | header, 0.1, 0.2, 7.1, 7.2, 7.8, 8, 8.2, 8.9, 11, 11.5, 13, 14, 14.2, 15.2 steps 0 and 2g, 16 (9), 17.3, report 34, 19, review log R10 |

**Changes after step 0 (the second re-issue, 20 Oct 2026).** Rows 80-88 record deviations D11-D17 of 19.15 and the
step-0 records. All were written after the PC's read-only step 0 on the 13:51 file and before any v5.2 beat; nothing
had been simulated on the PC.

| # | Change | Where |
|---|---|---|
| 80 | D11: the sheet replaces the v5.1 trunk and fascicles only inside its envelope; each v5.1 fascicle path beyond it kept and joined to the sheet through its own crossing edge (assumption 56), also in A17 and A18 on their own envelopes; distal edges inside it re-joined; the reachability acceptance at step 2g; v5.1's septal fascicle recognised | 1, 7.1, 7.8, 11, 11.5, 13, 14, 14.1, 14.2, 14.3, 15.2 step 2g, 16 (31, 56), 19.0, 19.4, report 34 items 13 and 15 |
| 81 | D12: D1 kept after the step-0 counts | 7.1, 11.5, 14, 14.1, 19.1 |
| 82 | D13: the valve-plane ring on the mesh's valve discs is the mid-plane ring, on both valves; the pulmonary nadir is its point at each sinus centre; the cut's 0 % and 100 % landmarks read on it; disc thickness and faces reported | 8.2, 8.5 items 2b, 5, 9 and 11b, 8.6, 11, 11.2a, 11.5, 14, 14.1, 14.2, 15.2 steps 2b-2e, 16 (13, 18, 32, 55), report 35 (a), (f) and (h), 19.5 |
| 83 | D14: the infundibulum cut at 47.2 % of the mesh's posterior span, superseding D6's 12.7 mm, which is reported beside | 8.1, 8.2, 11, 11.5, 14, 14.1, 14.2, 15.2 step 2b, 16 (32, 57), report 35 (f), 19.6, review log B17 |
| 84 | D15: the aortic angular frame from the mitral-disc and pulmonary-disc centroids; the stop rule unchanged; 126.9 / 126.4 / 128.1 deg measured | 8.3, 8.5 items 6 and 10, 11, 11.2a, 11.5, 14, 14.1, 14.2, 15.2 steps 2c and 2e, 16 (14), report 35 (i), 19.5 |
| 85 | D16: the primary right bundle is v5.1's, unchanged, its moderator-band edge included; D2's chain, assumption 47 and the 37.8 mm stop withdrawn (assumption 54 report only); D2's gate-7 label withdrawn; A20 redefined | 1, 7.1, 7.2, 11, 11.5, 13, 14, 14.1, 14.2, 14.3, 15.2 step 2g, 16 (47, 54, 58), 17.1, 17.2, report 34 item 12, 19.2, 19.11 |
| 86 | D17: A37's four shapes are T_24, T_20, T_17 and T_01, the first four other than the primary T_13 | 9.4, 13, 14, 15.2 step 8a, 16 (45) |
| 87 | Recorded at step 0, no deviation: A35 and A36 not run (feasibility); step 8a runs at most 37 of the 39 arm entries (A17, A18 and A20 also need their reachability checks) | 7.1, 7.2, 9.4, 13, 14, 15.2 step 8a, 17.3 |
| 88 | Header, 0.1 and 0.2: step 0, Alex's "lock", the five step-0 cards, the withdrawn first valve-ring card, the follow-up geometry and the second re-issue recorded; step 0 not repeated; step 1 commits this file | header, 0.1, 0.2, 12, 15.2 steps 0, 1 and 9, 19, 19.12, 19.13, 19.15, Resolutions |

## 19. Deviations after the 07:30 lock (20 Oct 2026)

At 08:28:47 UTC, after the 07:30 lock and before anything had run on the PC, Alex wrote: "I uploaded some more articles
/ should the purkinje stay a sheet and not a network? / also wha about the not adopted still open suggestsions". The
answer was a re-review, in three domains (conduction system; outflow anatomy; conductivities, torso and gate rules), of
every not-adopted row and open item of section 17 and of the five uploads (0.1). Every proposal was checked by an
independent verifier who opened the sources; **the verifier's final recommendation and its listed errors override the
reviewer, and nothing the verifier refuted is applied** (notes/A/2026-10-19-v52-lock/notadopted-review-2026-10-20.json).
The result went to Alex as three post-lock cards: post-lock card 1 (D1), post-lock card 2 (D2-D10, "Adopt all" for
changes 2-10) and post-lock card 3 (G). Four parts were not shown on post-lock card 2 and are follow-up items with their
own answers: the D4 placement ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC), D5 (a) ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC), D5 (c) ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC) and D9b, arm
A36 ("Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC). In this section "card 1-3" means the post-lock cards; the 05:18:46 and 05:19:07 cards are called
the cusp-muscle card and the pose card, and they are what "card 2" and "card 3" mean in the Discrepancies and Review log
sections below. Each change is a dated deviation under 0.3, written before any v5.2 beat and tagged "(deviation Dn,
20 Oct 2026)" where it lands; the tag gives the date it was written, and each deviation takes the date and time of
Alex's answer recorded in 0.1. Each deviation ends with an "If declined" line: the text that applies if Alex's answer
differs from the option this file is drafted on (0.2). From here, 17.1's "adopted list" means the 05:15:17 list together
with these answers. **19.15 adds deviations D11-D17**, written after the PC's step 0 on the 13:51 file and before any
v5.2 beat, on Alex's "lock" in the PC thread (20 Oct 2026 17:11:07 UTC) and the five step-0 cards; they bear on D1,
D2, D4, D5 and D6 where the dated notes below say so, and each takes the date and time of Alex's answer, recorded in
0.1.

### 19.0 Should the Purkinje stay a sheet and not a network? (Alex, 08:28:47 UTC; no change)

**Keep the hybrid as built.** Only the proximal left bundle is a sheet (7.1), and it replaces the v5.1 LB_TRUNK and
FASCICLE representation (inside its envelope only, the v5.1 fascicle paths beyond it kept: deviation D11, 20 Oct 2026);
the v5.1 LV distal network and the RV network are kept. So v5.2 is already a sheet feeding a
network, and no value changes for this question.

- **Human anatomy supports exactly this split.** Massing 1976 p.614 (human ex vivo): the left bundle can be traced for
  24-41 mm, then the septum is "relatively diffusely covered by Purkinje fibers", with a "ragged termination".
  Demoulin 1972 pp.808-809 (human ex vivo, 20 control hearts): a 6-10 mm ribbon fanning into 2-3 radiations, with
  peripheral anastomoses in all 20. Elizari 2017 p.6: a "complex subendocardial network" with false tendons.
  Stephenson 2017 p.4 (human micro-CT, n = 1): a sheet, then three fascicles, then a Purkinje network with free-running
  elements.
- **A whole-system sheet or fast layer is not adopted.** Its speed and extent would have to be fitted to a comparator
  (MedalCare-XL's layer is "Durrer-based", 2.0 m/s over 10-90 %), which is tuning, and it would reverse Alex's 9 Oct
  choices (15:39 "network"; 16:38 "v3").
- **Reasons corrected by the verifier.** Camps 2024 is **not** a network-only precedent: its eikonal inference puts
  root nodes on a fast isotropic endocardial layer (pp.2-3), and its monodomain adds a 0.4 mm fast endocardial layer to
  the network. A whole-LV layer is not ruled out by the endocardial-versus-epicardial contrast that gates 2, 5 and 6
  measure: Hyde 2015 (canine data, model scaled to human) needed a fast endocardial layer to reproduce it. Camps's PCC
  0.99 compares root nodes with the minimal network; adding branches and PMJs to the minimal network reduced the time
  to activate the ventricles by 8.3 % (7 ms, 84 to 77 ms) and gave "a significant shortening of the QRS duration",
  while the QRS correlation stayed at PCC 0.97 (Camps 2024 p.11; corrected 20 Oct 2026: the 7 ms is the time to
  activate the ventricles, not the QRS duration), so network detail does move QRS duration. Durrer's early-area finding
  rests on 4 hearts (p.901). The valid grounds for keeping
  the network are anatomy and the absence of a fitted parameter.
- **What the question did change:** how the sheet couples to muscle in the upper septum (D1) and its envelope (D4).

### 19.1 D1: the upper third of the left septum junction-free (post-lock card 1)

- **What changes.** No PMJ on any sheet node above the D1 line on the left septal surface, and a PMJ at every sheet node
  below it; the sheet's first 10 mm stays junction-free in every heart; the same line removes the v5.1 LV distal-network
  junctions above it on the left septal surface; the paraseptal free wall (AHA 1) is untouched. The line is one third
  of the septal crest-to-apex length, measured along the septum from the crest (assumption 46); AHA 2-3 and UVC
  z >= 0.67 are cross-checks only. The 07:30 rule (assumption 30, added by the review's B1 build fix, not chosen by
  Alex) and the v5.1 upper-septal coverage (to z 0.9) become arm A39. Where: 7.1, 13, 14, 15.2 steps 0 and 2g, 16,
  report 34.
- **Source.** Human function first: Durrer 1970 pp.899, 901 and 906 (human; the early areas from 4 hearts, p.901): septal
  activation starts in the middle third, somewhat anteriorly, and proceeds apical-basal. Cassidy 1984 p.39 (human in
  vivo, n = 15): the inferior border of the middle septum is earliest; Fig 5 p.41 group means, 11 ms mid-septal against
  27-37 ms toward the base (a reading of the figure). Upadhyay 2019 p.12 (human in vivo; 16 controls and 26 patients
  with intact Purkinje activation): delta LV time -37 ms, apical-first. Dog anatomy beside: Myerburg 1972 pp.227, 237.
  Elizari 2017 p.7 and p.9 Fig 12 legend (Spach, one 2-day human infant). Counter-evidence: Massing 1976 p.614 and the
  Fig 17 legend.
- **Tuning-shaped toward gate 1 (declared); not tuning in origin.** The trigger is the 07:30 rule itself, an unsourced assumption that makes the
  upper septum early against three human functional series. But D1 **moves failing gate 1 toward passing**, of unknown
  size, which departs from the A19 precedent; the reason for the departure is written in 7.1 (A19 extrapolated one
  finding, while this region was observed directly in three human series and the alternative is itself unsourced, so
  no neutral choice exists). A gate-1 pass would be a calibration result.
- **Gate effect (section 14).** Gate 1 toward passing; 7(b) away; 7(T) 0 to away; 7(e) slightly longer; gate 8's margin
  narrower; report 29 expected negative (apical-first) in the control and 7D His beats.
- **Calibration label (11.5).** Gate 1 by clause (iii) (post-lock card 1 stated it); gates 2, 5, 6 and 7 ((a), (b),
  (T) and the RV items), inherited from the sheet. Not gates 3 and 8, nor 7(e), which is not one of the sheet's parts
  (deviation G, 20 Oct 2026).
- **Order of the step-0 checks (dated note, 20 Oct 2026).** The re-review asked for report 34 items 4 (the LV septal
  junctions above the line) and 8 (whether v5.1's LB_TRUNK and FASCICLE nodes carried PMJs) before Alex decided; post-lock
  card 1 was answered without them, and they run at step 0. If item 8 shows that v5.1's trunk and fascicle nodes carried
  no PMJs (so D1 partly restores v5.1), or item 4 shows no junction above the line in a heart (so the network part of D1
  is a no-op there), the step-0 report goes to Alex before step 1 (15.2 step 0).
- **Alex's word.** Post-lock card 1, "Junction-free", 20 Oct 2026 11:22:09 UTC.
- **If declined.** The 07:30 rule stays primary: no PMJ in the sheet's first 10 mm and one at every sheet node beyond it
  (assumption 30 as locked), with the v5.1 LV distal coverage of the upper septum (to z 0.9); assumption 46 is unused,
  arm A39 is not run, gate 1 is not a calibration check for D1, and report 29 is kept as a report against the 07:30 rule.
- **Dated note (deviation D12, 20 Oct 2026).** The step-0 checks ran on the 13:51 file: item 8 showed that v5.1's
  LB_TRUNK and FASCICLE nodes carried no PMJ, so the report went to Alex before step 1; item 4 found 255 / 239 / 220 v5.1
  LV junctions above the line. Alex kept D1 (step-0 card 4, "Keep", 20 Oct 2026 17:33:10 UTC; 19.15.2).

### 19.2 D2: the right bundle along the moderator band (post-lock card 2, change 2)

- **What changes.** The primary RB continues from the v5.1 RB end (the moderator band's septal insertion) as a chain of
  1 mm nodes at 1.5 m/s with no PMJ on its free-running segment, to one anterior RV free-wall endocardial node fixed by
  rule (assumption 47), which joins the nearest v5.1 RV distal-network node with a PMJ. The 07:30 septal-only course
  becomes arm A20. A chain longer than 37.8 mm stops the build (assumption 54). This partly reverses the 05:15:17 list,
  which kept the moderator band as an arm, hence Alex's card.
  Where: 7.2, 13, 14, 15.2 step 2g, 16, 17.1, report 34 items 6 and 12.
- **Source.** Stephenson 2017 p.4 (human whole-heart micro-CT, n = 1): the RB "descended the septum running on the
  superficial and deep surfaces of a major free-running trabeculation". Lee and Hur 2019 (38 formalin-fixed human
  hearts; Europe PMC full text, no page numbers): moderator band in 36 of 38, mean length 13.6 mm, mid-septal origin in
  25 of 36; its type means do not reproduce the overall mean (n-weighted about 14.9 mm; type 3's subtypes 13.2 mm;
  recorded, not corrected). Massing 1976 p.615 (32 human hearts): implicit only.
- **Not tuning.** The case rests on anatomy. The v5.1 RV-onset mismatch (19.3 ms after LV onset against Durrer's
  5-10 ms) is **not** a reason, since choosing a structure to fix a reported mismatch would be comparator-driven; no
  failing gate is predictably helped.
- **Gate effect.** 7(c), which passes now (27.5 ms in 20-31 ms), could fall below 20 ms; RV onset earlier (report 14);
  gate 3's RVOT value and gate 4 either way; gate 1 unchanged or away.
- **Calibration label.** Gate 7 ((c) and the RV items), with report 14 beside it: D2 is aimed at the RV activation
  sequence. Not gates 1, 3, 4 or 8, which it reaches only through the network that paced beats enter retrogradely;
  gate 4 is a depth-contrast gate, but D2 leaves the RV subendocardial network a 10 % RV stimulus engages as in v5.1,
  apart from its one end-node PMJ (7.2, 11.5; deviation G).
- **Alex's word.** Post-lock card 2, change 2, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** The septal-only course of the 07:30 lock stays primary and arm A20 is the moderator band, as at
  07:30; assumptions 47 and 54 are unused.
- **Dated note: superseded in substance by D16 (20 Oct 2026; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC).** Step 0
  showed that v5.1's right bundle already crosses the cavity along the moderator band as one straight 1.5 m/s edge with
  no PMJ, 14.7 / 18.2 / 10.1 mm, to the anterior RV free wall (report 34 items 6 and 12), so the premise above (v5.1
  septal-only) was wrong. The primary right bundle is v5.1's, unchanged; no chain is built; assumption 47 is withdrawn
  and assumption 54 is report only; D2's gate-7 label is withdrawn; A20 is redefined as the RB on the septum only, with
  v5.1's band edge removed (19.15.6). The choice on post-lock card 2, change 2, stands in substance.

### 19.3 D3: the gate-7(a) patch centres (post-lock card 2, change 3)

- **What changes.** Posterior paraseptal (the inferior free wall next to the septum) centred at one third of the distance
  from apex to base, about z 0.33 against the mitral-annulus level the PC reports; central at 0.50 on the mid left
  septum; anterior paraseptal centred 10 mm below the mitral annulus (assumption 40, rewritten). Each centre's
  circumferential position is fixed by the rule of section 11 row 7 (one patch radius onto the free wall from the AHA
  septal boundary; the central centre midway between the septal boundaries), from report 34 item 14, with a stop if a
  boundary or the annulus cannot be identified. No patch is centred on
  the code's Durrer points (14_purkinje.py:92-95), whose distances to the patches are reported (report 34 item 9), and
  v5.1's (a) is scored at both sets. The 07:30 centres (0.70 for both paraseptal areas) were a transcription slip
  against the 12 Oct approved text. Where: section 11 row 7, 15.2 step 2e, 16, report 34.
- **Source.** Durrer 1970 pp.899, 901 and 906 (human; 4 hearts for the early areas, p.901): "posterior paraseptal about one third of
  the distance from apex to base"; the anterior paraseptal area "just below the attachment of the mitral valve,
  extending at least 2 cm toward the apex".
- **Not tuning.** It restores the approved definition, removes a circularity (the sheet's outflows attach at the code
  points, deep audit F06), changes no model value and is fixed before any beat.
- **Gate effect.** 7(a) only; direction not predicted.
- **Calibration label.** Gate 7 ((a)).
- **Alex's word.** Post-lock card 2, change 3, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** The 07:30 centres apply: (apicobasal 0.70, circumferential anterior-septal), (0.70, posterior-septal)
  and (0.50, mid-septal), with assumption 40 as locked and report 34 item 14 unused.

### 19.4 D4: the sheet envelope from the Massing digitisation (post-lock card 2, change 4; the placement a follow-up item)

- **What changes.** The sheet's anterior-posterior envelope is **22.6 mm at its widest** (derived; IQR 20.4-29.9,
  range 17.3-31.9), measured in the cloud before any beat from Massing's drawings by the method of
  notes/A/2026-10-19-v52-lock/massing/METHOD.md (7.1). It replaces assumption 9 (the v5.1 LV septal node footprint). Assumption 10 (full width by 12.5 mm) is kept;
  the measured profile is reported beside the value and is not applied. The envelope is laid 17.8 mm anterior and
  4.8 mm posterior of the His line (derived from the post-hoc anterior share 0.79; a follow-up item). Step 0 checks the
  v5.1 fascicle endpoints against the envelope (report 34 item 13) and stops if either lies outside it. Where: 0.1,
  7.1, 14.1, 15.2 steps 0, 1 and 2g, 16 (9, 10), 17.3, report 34.
- **Source.** Massing 1976 Figs 8A, 8B, 9A, 9B, 10A, 10B and 11A, pp.614-616, with Table 1 p.610 (human ex vivo, n = 7
  of the 10 non-neonatal hearts, cases 1-7, aged 9-83 y; cases 8-10 excluded because their ink cannot be separated from
  the background; Fig 13 neonatal, not used). A lower bound toward the specimen margins and the distal fan (pp.610, 614,
  620), probably conservative, because the exclusions and two lower-bound cases bias it low.
- **Not tuning.** The method was written at 10:33 UTC before any width was measured, and its primary quantity (the
  median of the per-heart maxima) was pre-specified and used whatever it turned out to be; no gate was involved. The
  logged deviations are listed in 7.1: deviations 1-5 (segmentation, crops, case 4's strand, the exclusions) came before
  any width was computed, though after the masks were seen, and the threshold constants were chosen after seeing cases
  2, 3 and 5 (a stated limitation); deviation 6 added descriptive outputs after the results were seen (the placement
  split, the width/length ratio, the edge-free subset and the 12.5 mm fraction), which set no value except the
  placement, put to Alex separately.
- **Gate effect.** Either way, by how far the measured envelope differs from the v5.1 footprint (report 34 item 13).
- **Calibration label.** The sheet's: gates 2, 5, 6 and 7 (gate 7: (a), (T), (b) and the RV items; 11.5; not gates 1, 3
  and 8, deviation G).
- **Alex's word.** The width: post-lock card 2, change 4, "Adopt all", 20 Oct 2026 11:23:21 UTC. The placement (17.8 / 4.8 mm about the His line):
  follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC.
- **If declined.** If change 4 is declined, the 07:30 envelope applies (the v5.1 network's LV septal node footprint,
  assumption 9 as locked) and report 34 item 13 reports the footprint only. If only the placement is declined, the
  envelope is centred on the v5.1 LV septal node footprint (the 07:30 placement basis of assumption 9) with the measured
  22.6 mm width: 11.3 mm either side of the footprint's anterior-posterior midpoint at each level (derived: 22.6 / 2;
  the midpoint interpolated linearly between report 34 item 13's levels, and a level without one a stop after step 0;
  7.1), and the build continues; the step-0 fascicle-endpoint check (report 34 item 13) still runs against that
  envelope, with its stop rule unchanged.
- **Dated note: the attachment answered by D11 (20 Oct 2026; step-0 card 1, "Keep tails", 20 Oct 2026 17:32:26 UTC).** At step 0 the
  posterior endpoint lay outside the envelope in all three hearts and the anterior one in two, and the envelope stayed
  on the left septal surface; the build stopped and the attachment went to Alex. Under D11 the sheet replaces the v5.1
  trunk and fascicles only inside its envelope, and each v5.1 fascicle path beyond it is kept and joins the sheet
  through its own crossing edge (assumption 56; 19.15.1). The envelope was not widened.

### 19.5 D5: the aortic crescents, in three parts ((b) on post-lock card 2, change 5; (a) and (c) follow-up items)

- **What changes.** (a) Inside the two lunes, total crescent muscle = max(existing, lune), both measured from the aortic
  valve-plane ring, which becomes the reference line (assumption 13 rewritten); precondition: step 0 reports the
  tag-1/tag-5 boundary height relative to the valve plane (report 35 (h)), and if it lies below the plane the build
  stops before step 2c. (b) An RCC axial cap, H(theta) = 2.4 sin(pi (theta - 135.5) / 70.5) mm (the half-sine is
  assumption 48); no LCC cap. (c) The cusp sites at 50 % of the built extent (assumption 35 rewritten). Where: 8.5 items
  2b, 5, 7, 9, 11b and 12; 13 (A28); 14; 15.2 steps 0, 2c and 2e; 16; report 35.
- **Source.** De Kerchove 2015 Table 1 p.4 (human, 58 fresh unfixed tricuspid roots, 41 homograft and 17 cadaver): the
  external ventriculo-arterial junction 2.4 +- 1.5 mm above the basal ring at mid-RCS; p.7 ties that height to adherent
  right-ventricular and septal muscle, so it bounds the crescent from above and is not a direct crescent height. Gami
  2011 pp.6-8 (603 formalin-fixed autopsy hearts): 2.8 +- 1.2 mm in the 55 % with an RCC extension, carried by A28. (a)
  is the pulmonary-side rule of 8.6, max(existing, 4.0 mm).
- **Not tuning.** (a) removes an internal contradiction (the 07:30 item 9 said both "no crescent is added there" and
  "the same rule as the pulmonary side"). The cap is fixed before step 2c, by source and not by effect; under the
  precondition it can only shrink the crescent, which moves failing gate 1 **away** from passing.
- **Gate effect.** Gate 1 away or unchanged; gate 3 and gate 8's cusp family either way.
- **Calibration label.** Gates 1, 3 and 8.
- **Alex's word.** (b): post-lock card 2, change 5, "Adopt all", 20 Oct 2026 11:23:21 UTC. (a) and (c) were not shown on post-lock card 2 (its
  change 5 read "Right-coronary crescent capped at 2.4 mm height"), and the outflow verifier asked for three separate
  decisions: (a) follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC; (c) follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC.
- **If declined.** (a): the 07:30 reference line (the mesh LV-myocardium to aortic-wall boundary; assumption 13 as
  locked) and the 07:30 item 9 text apply, item 9's two readings go to Alex before step 2c, and the report 35 (h)
  precondition does not apply. (b): no RCC cap; assumption 48 is unused. (c): the cusp sites sit at 50 % of the local
  h(theta) (assumption 35 as locked), as in the 11.2a ledger's if-declined entry.
- **Dated note (deviations D13 and D15, 20 Oct 2026).** The "aortic valve-plane ring" of (a) and (b) is, on the mesh,
  the **mid-plane ring** of the aortic valve disc (D13; step-0 card 2, "Mid-plane", 20 Oct 2026 17:33:39 UTC; assumption 55); at step 0
  report 35 (h) put the boundary 2.0-5.6 mm above it at all six positions in every heart, so the precondition passed.
  Toh's theta, on which the lunes, the cap and the cusp sites sit, is read in the frame of D15 (the mitral-disc and
  pulmonary-disc centroids; step-0 card 5, "Adopt all", 20 Oct 2026 17:36:27 UTC; assumption 14 rewritten) (19.15.3, 19.15.5).

### 19.6 D6: the infundibulum cut height (post-lock card 2, change 6)

- **What changes.** The fused septal component of the infundibulum ends 12.7 mm above the 0 % landmark, which is
  relabelled as the mesh proxy for Jakiel's RVOT base, instead of at 37.3 % of the posterior span; the same rule sets
  the 8.1 labels; the three candidate boundaries and the posterior span are reported (report 35 (f)); 15.3 mm measured
  down from the ring is not used. Where: 8.1, 8.2, 15.2 step 2b, 16, report 35.
- **Source.** Jakiel 2025 Table 1 (220 human hearts): septal component maximum height 12.7 +- 4.8 mm, posterior RVOT
  wall 26.9 +- 6.5 mm; Table 2: the septal height is nearly independent of the posterior RVOT height (r = 0.199), the
  posterior infundibulum tracks it (r = 0.745).
- **Not tuning.** Jakiel's Methods never define the 37.3 % share and his heights do not reproduce it (derived: 47 % from
  the maximum heights, about 43 % from mid-wall heights); chosen by source, not by contact area or gates.
- **Gate effect.** Small: the boundary sits about 2.6-3.7 mm higher at an illustrative 24-27 mm span (a post-lock
  review estimate stated without a derivation, not a mesh measurement and not a Jakiel value; 8.2) (derived:
  12.7 - 0.373 x 24 = 3.75; 12.7 - 0.373 x 27 = 2.63), 0.2-5.1 mm over Jakiel's mean +- SD span of 20.4-33.4 mm
  (derived: 26.9 +- 6.5 mm, Table 1, 220 human hearts); each mesh's own span comes from the step-2b report (report 35
  (f)). RVOT paced QRS and gate 3 either way, by a few ms at most.
- **Calibration label.** Gates 1, 3 and 8, as the cut (gate 8 by the site test of 11.5; deviation G).
- **Alex's word.** Post-lock card 2, change 6, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** The 07:30 rule applies: the septal component is the lowest 37.3 % of the posterior RVOT wall, for the
  cut and the 8.1 labels; the three candidate boundaries are still reported (report 35 (f)).
- **Dated note: superseded by D14 (20 Oct 2026; step-0 card 3, "Scale to span", 20 Oct 2026 17:32:47 UTC).** The mesh's posterior RVOT
  wall is 13.6 / 10.2 / 13.7 mm, 2.0-2.6 SD short of Jakiel's 26.9 mm, so the 12.7 mm split would leave almost no
  free-standing infundibulum (0.9 / 0 / 1.0 mm of the posterior wall). The septal component's upper limit is now 47.2 %
  of the mesh's own posterior span above the 0 % landmark (19.15.4; assumption 57), and the 12.7 mm height above is
  reported beside it at step 2b (report 35 (f)).

### 19.7 D7: the A10 blood levels (post-lock card 2, change 7)

- **What changes.** A10 runs blood at 0.63 and 0.89 S/m (human Hct 50 and 35 %); the 07:30 levels, 0.435 and 1.0 S/m,
  are kept as labelled literature extremes and not run; R3.5's flow-alignment sentence is rewritten (with 0.89 S/m as
  the top level, full alignment is covered only at Hct of about 45 % and above; derived 0.71 x 1.25-1.30 =
  0.89-0.92 S/m). Where: R3.4, R3.5, 13.
- **Source.** Geddes and Sadler 1973 Table I p.337 (human blood in vitro, 37 C, 25 kHz), derived 0.627 and 0.888 S/m.
  The extremes: Kaufman and Johnston 1943 Table IV p.49 (dog, defibrinated, 2 observations, 1 kHz; about Hct 63 % by the
  same formula, derived); Schwan and Kay 1956 pp.664 and 669 (a stated round figure citing Schwan 1941, not read; about
  Hct 29 %, derived). Hoetink 2004 pp.1257, 1260 for flow alignment.
- **Not tuning.** An ECG-only arm that decides no verdict; human values replace a dog value and a round figure.
- **Gate effect.** Amplitudes; gate 5 either way; no verdict.
- **Calibration label.** None (an arm).
- **Alex's word.** Post-lock card 2, change 7, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** A10 runs the 07:30 levels, 0.435 and 1.0 S/m, with their relabels (R3.4), and R3.5's sentence stays
  as at 07:30.

### 19.8 D8: the Hooks bulk set as lead-field arm A40 (post-lock card 2, change 8)

- **What changes.** New ECG-only arm A40: sigma_b 0.70 fibre / 0.35 transmural / 0.16 cross-fibre S/m in the lead field
  only, with the fix-2 sigma_i as the source term; implied sigma_e (derived, sigma_b - sigma_i, fibre / cross /
  transmural) control 0.526 / 0.148 / 0.288 S/m and HF 0.526 / 0.154 / 0.323 S/m, asserted positive at build; lead
  fields recomputed. R2.7's caution is reworded: it does not apply to a lead-field-only use. Numbered A40 rather than
  the verifier's "arm 36", because A36 is taken and A38 is reserved (8.9). Where: R2.7, 13, 14, 17.1.
- **Source.** Hooks 2007 p.e108 (pig in vivo, 6 hearts, 61 sites); the axis mapping is an inference from LeGrice 1995
  (dog, 4 hearts, p.H571), coarse because Hooks's laminae were not uniformly radial (p.e107).
- **Not tuning.** An arm, no verdict; the only in vivo orthotropic bulk set read; non-human and labelled.
- **Gate effect.** q calls and amplitudes: gates 2, 4, 5 and 6 either way; no verdict.
- **Calibration label.** None (an arm).
- **Alex's word.** Post-lock card 2, change 8, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** No arm A40; R2.7's caution stays as at 07:30, and S5 stays a not-adopted row of 17.1.

### 19.9 D9: lungs, skeletal muscle and fat in host torsos (D9a on post-lock card 2, change 9; D9b a follow-up item)

- **What changes.** **D9a:** A35 (lungs) becomes a feasibility-gated, ECG-only arm in the KCL host torso (KCL_torso1,
  Zenodo record 7253863), lungs on against lungs off in the same host, with its placement, overlap, remeshing, tissue and
  electrode rules fixed now (assumption 52) and a read-only step-0 check (9.4). **D9b:** A36 (skeletal muscle and
  subcutaneous fat) stays not run unless a read-only step-0 check on the Moss/Wuelfers/Seemann torso (Zenodo record
  8285403) passes; its fibres follow assumption 53 if the host has none; if it runs, its muscle values are two labelled
  levels with no primary between them, (a) the adopted 0.202 S/m isotropic with a ratio-7 variant and (b) Burger's human
  0.417 / 0.148 S/m, and fat as A31; which level to prefer is settled only after Burger and van Dongen 1961 is read. One host torso for both arms is
  recorded as an option and not adopted. Where: 9.4, 13, 15.2 steps 0 and 8a, 16, 17.1, 17.2.
- **Source.** Lungs: 0.078 S/m, Geddes and Baker 1967 (dog in vivo average), bounds 0.0389 S/m (Gabriel 1996 Part III,
  excised animal) and 0.134 S/m (Kaufman and Johnston 1943 Table IV p.49, dog, 4 animals, postbiologic calibration,
  7 observations; prebiologic 0.131 S/m, 9 observations); support from Schwan and Kay 1956 pp.668-669 (dog lung in situ,
  7 dogs, 1 kHz; about 0.080-0.095 S/m in the ECG band, derived). Registration by UVC axes as in Campos 2026 (supplement p.7).
  Muscle: Keller 2010 p.1569; Klepfer 1997 p.709 (ratio 7:1); Burger via Geddes and Baker 1967 Table 4 p.285 (human;
  n not given; the primary paper not read). No human low-frequency lung value exists in these papers.
- **Not tuning.** Arms, no verdict; every rule is fixed before any beat, so neither the two-person mismatch nor the fit
  of the dilated HF hearts is solved by moving the heart.
- **Gate effect.** Amplitudes; gates 5 and 6 either way; no verdict.
- **Calibration label.** None (arms).
- **Alex's word.** D9a: post-lock card 2, change 9, "Adopt all", 20 Oct 2026 11:23:21 UTC. D9b was not shown on post-lock card 2 (its change 9 named
  only the lungs arm A35 in the KCL torso), so it is a follow-up item, "Adopt all" on the follow-up card, 20 Oct 2026 13:27:28 UTC.
- **If declined.** D9a: A35 is not run in v5.2, as at 07:30, and assumption 52 is unused. D9b: A36 is not run, as at
  07:30; the Moss/Wuelfers/Seemann check, its two levels and assumption 53 move to 17.3 as an open item.

### 19.10 D10: sub-variant A19b (post-lock card 2, change 10)

- **What changes.** The primary with no LV distal-network junctions in AHA segments 4 and 5 (the basal inferior and
  basal inferolateral free wall), with A19's 50-67 % rule not applied; a sub-variant of A19, folded into A19 rather than added as a new numbered arm, given the multiplicity concern of
  17.3. Where: 7.7, 13, 14.
- **Source.** Durrer 1970 p.906 (human: the posterobasal area is reached last); Cassidy 1984 pp.39-40 (human in vivo,
  n = 15: the base of the inferior posterior wall "consistently the last area"). The evidence for **zero** junctions
  there is weak (Massing pp.610 and 620; Cassidy p.40; Camps 2024 pp.2-3; Sebastian 2013).
- **Tuning-shaped, said plainly.** Superior paced sites end in the inferobasal LV, so A19b likely lengthens summit and
  cusp paced QRS, toward failing gate 1 passing. It is an arm only and is never promoted.
- **Gate effect.** Gate 1 toward passing; 7(T) away; gate 8's margin narrower (section 14).
- **Calibration label.** None while it stays an arm; if it were ever promoted, gate 1 would be a calibration check for
  it (0.3).
- **Alex's word.** Post-lock card 2, change 10, "Adopt all", 20 Oct 2026 11:23:21 UTC.
- **If declined.** No A19b; A19 stays as at 07:30.

### 19.11 G: the Targeted calibration-check rule (post-lock card 3)

- **What changes.** One register keyed by change (11.5). A gate is a calibration check for a change if (i) the change
  was prompted by that gate's failure or an audit of it, (ii) it is aimed at that gate's mechanism (the process the
  gate measures, the definition of what it scores, or the sites it is scored on; a change that only alters the value of
  the scored quantity, or that is only part of the activation every paced beat passes through, is not thereby aimed
  at it, except at the depth-contrast gates 2, 4, 5 and 6, below), or (iii) it is a label Alex accepted on a card:
  post-lock card 1 stated that D1 makes gate 1 a calibration check, so it is one.
  Whole-model changes adopted on general evidence (conductivities, blood, speeds, pose) are exempt
  for gates they move only incidentally, each exemption written with its reason. The 07:30 trigger "or if that gate's
  own measure is moved by the change" is withdrawn, which removes its contradiction with "does not depend on whether
  the gate moves or passes". Every row is re-derived: gate 8 goes, by one site test, to every change labelled for gate 1
  under (ii) by the summit and cusp sites both gates are scored on (the crescents, the summit re-anchor, the site-set
  redefinitions, the infundibulum cut and D6, the stimulus rule, fix 5's outflow blend and D5); fix 5's outflow blend
  carries gates 1, 3 and 8 (new fibre angles at their summit and cusp sites); rows for D1-D10 are added, with D1 and D4
  inheriting the sheet's gates 2, 5, 6 and 7 ((a), (T), (b) and the RV items), D1 carrying gate 1 under (iii), and D2
  carrying gate 7 ((c) and the RV items). Where: 0.1, 7.1, 7.2, 7.8, 8, 8.9, section 11 (calibration column), 11.5, 13
  (A15), 14, 14.2, 19.1, 19.2, 19.4, 19.6.
- **The cards' words.** Post-lock card 3, as shown: question "Count a gate as a calibration check only for changes
  aimed at it?"; context "Targeted: a gate is a calibration check for a change prompted by its failure or aimed at its
  mechanism, and whole-model changes (conductivities, blood, speeds, pose) are exempt with the reason written."; the
  chosen option's consequence "Gates stay independent tests unless a change was aimed at them; the register is
  rewritten to match." Clause (iii) adds only what a card stated: post-lock card 1 said that D1 "also moves failing
  gate 1 toward passing, so gate 1 would be labelled a calibration check for it" ("Junction-free", 20 Oct 2026 11:22:09 UTC).
- **07:30 labels withdrawn under card 3 (dated deviation, 20 Oct 2026; Alex, post-lock card 3, "Targeted", 20 Oct 2026 11:23:49 UTC).** Neither
  limb applies to any of them, each reason written in 11.5:
  - fix 4 on gate 1 (the 07:30 register) and on gate 7 ((T), (b) and the RV items; the 07:30 section 11 row): a speeds
    change, which the card exempts by name;
  - fix 5's LV helix on gate 5: a whole-model fibre field from human data (Lombaert 2012, 10 human ex vivo DT-MRI
    hearts); arm A15, which keeps the v5.1 fibres for gate 5 only, reports the gate beside the primary and does not
    aim the helix at it. Fix 5's outflow blend keeps gates 1 and 3, and gate 8 by the site test, under (ii);
  - the sleeve existing-muscle rule on gate 3 (the 07:30 section 14 column): not (i), since it came from review
    finding R12 (review log), which asked for one rule fixed in advance for mesh muscle above the pulmonary valve plane,
    and was not prompted by the Daniels fail or an audit of it; not (ii), since the muscle it adds is the sleeve itself, which keeps its own gate-3
    label, and beyond that it only leaves v5.1 mesh muscle bit-identical (0 on every gate by construction, section 14);
  - the left-bundle sheet on gate 3 (the 07:30 section 11 gate-3 cell; the 07:30 11.5 and section 14 column gave the
    sheet gates 2, 5, 6 and 7 only, so the 07:30 file disagreed with itself, and this resolves it by the rule): not (i),
    since the sheet was not prompted by the Daniels fail; not (ii), since gate 3 scores the Daniels order, not a depth
    contrast, the sheet touches none of its sites, their anatomy or the MDI rule, and paced beats reach the sheet only
    by retrograde entry, which for this gate is involvement, not aim.
- **Labels not given, because they rest on involvement, not aim.** "Every paced beat enters the sheet (or the network)
  retrogradely" and "it is part of the network arm gate 8 compares against" describe activation every paced beat passes
  through, which is the withdrawn "moved" trigger under another name. So no label is given for the sheet on gates 1
  and 8 (its 07:30 gate-3 label is withdrawn, above); for D2 on gates 1, 3, 4 and 8; for D1 on gates 3 and 8; or for
  D4 on gates 1, 3 and 8. D1 has no 7(e) label because (e) is not one of the sheet's gate-7 parts. For D2 the
  two near cases are written out (7.2, 11.5): gate 4 scores the RV depth effect and gate 3 the Daniels order at its
  outflow, vein and LV sites, and D2, aimed at the RB's course in the His-driven beat, is aimed at neither. Changes of
  anatomy or scoring at a gate's own sites keep their labels (the crescents, the summit re-anchor, the infundibulum cut,
  the stimulus rule, the site sets, D5 and D6).
- **The depth-contrast reading (dated, 20 Oct 2026; 11.5).** Gates 2, 4, 5 and 6 score a 90 %/10 % depth contrast,
  which exists because a 10 % stimulus engages the subendocardial conduction system early, while a 90 % stimulus
  reaches it only after crossing the wall (19.0: Hyde 2015 needed a fast endocardial layer to reproduce it). For these
  gates that engagement is the process measured, so the sheet, D1 and D4, which set the LV septal subendocardial
  system's extent, junctions and coupling, keep gates 2, 5 and 6 under (ii), and D2, a free-running bundle that leaves
  the RV subendocardial network as in v5.1 apart from its end-node PMJ, is not aimed at gate 4. Gates 1, 3 and 8 score
  no depth contrast, so retrograde entry stays involvement for them. The sheet's gate-7 RV items rest on time zero:
  they are timed after LV onset (REPORT.md Table C), which the sheet sets, and D1 and D4 inherit the same parts.
- **Source.** The conductivity-domain verifier's two wordings, with the consequence of the broad one shown (the CT pose
  would make almost every gate a calibration check, passing gate 4 included); the conduction-domain verifier asked for
  gates 1 and 3 on the sheet row, and the outflow-domain verifier for gate 8 on the cusp sites, both under the 07:30
  trigger: the cusp-site label stands under (ii), because it changes gate 8's sites, and the sheet's gates 1 and 3 do
  not.
- **Not tuning.** A labelling rule; it changes no value, is fixed before any beat, and takes labels from why a change was
  made and what it is aimed at, never from what it does to a gate.
- **Gate effect.** None on any value; it fixes which verdicts cannot count as validation.
- **Calibration label.** Not applicable.
- **Alex's word.** Post-lock card 3, "Targeted", 20 Oct 2026 11:23:49 UTC.
- **If declined** (the "Any moved" option). The 07:30 register applies, with its trigger "or if that gate's own measure
  is moved by the change"; the calibration labels of section 11, 11.5 and section 14 are re-derived from the section 14
  sign table (every "?" or signed entry becomes a label, passing gate 4 under fix 2, fix 3 and the pose included) before
  the re-issue time is written.
- **Dated note (deviations D11 and D13-D16, 20 Oct 2026).** D2's gate-7 label described above is withdrawn by D16 (D2
  builds nothing; 11.5), D6's labels pass to D14, which supersedes it, and the step-0 deviations are labelled by the
  same rule: D11 the sheet's (2, 5, 6, 7), D13 the crescents' and sleeves' (1, 3, 8), D14 the cut's (1, 3, 8), D15 1, 3,
  5 and 8, D12 D1's unchanged, D16 and D17 none (11.5; 19.15).

### 19.12 Reports added (report only; none changes a value or a verdict)

- **29** Left-septal activation sequence against Upadhyay 2019 (D1's direct human observable; assumption 49).
- **30** Wavefront voltage per direction, beside R2.6.
- **31** Sinus-beat QRS voltage against Rijnbeek 2014 (control heart only).
- **32** Campos 2026 pace-map scoring with both of its metrics (assumptions 50 and 51).
- **33** A bidirectionally coupled Purkinje network in a monodomain run, only if a released coupling exists (15.3 T0);
  outside gate 9.
- **34** Step-0 conduction geometry (places D1, D2, D3 and D4 blind; items 13 and 14 added at the finalisation, item 3b
  completed after step 2g).
- **35** Step-0 outflow geometry, including D5's precondition (h) and D6's candidates (f).
- **Added after step 0 (deviations D11, D13-D16, 20 Oct 2026):** report 34 item 15, the D11 topology (exit nodes, kept
  tail lengths and nodes, re-joined distal edges, reachability), measured read-only in the PC's follow-up; item 12's
  candidate end node is report only (D16); item 13's stop is answered (D11). Report 35 (i), the D15 frame landmarks,
  measured in the same follow-up; (a) and (h) give each disc's thickness and faces per position (D13); (f) adds the
  D14 boundary, 47.2 % of the span (D14).

### 19.13 Corrections (wording, pages and provenance; no value changes)

Applied in this re-issued file as dated corrections (20 Oct 2026), not in the 07:30 file, which is superseded and not
committed (0.2). Where the outflow-domain verifier asked for "a separate dated erratum", this section and the in-text
tags serve as that erratum.

- 0.1: two actor labels normalised to "Cloud".
- R2.6 and 14.3: Hooks 2007 added as a comparator (report), and the bulk comparison stated in all three directions.
- R2.7: the primary's cross-fibre wavefront fraction (0.048 control, 0.025 HF) is far below the dog in situ values,
  mainly because of fix 4's speed anisotropy under R2.2, not Clerc's provenance (derived 0.090 with Roberts and Scher's
  own sigma_e).
- R3.3, R3.4 and 9.4: the wall, blood, fat and lung citations relabelled to what Schwan and Kay 1956 (pp.664, 666, 668,
  669) and Kaufman and Johnston 1943 (Table IV p.49) measured.
- 7.2: the RB is unbranched throughout the septum in all 32 hearts (Massing p.615); Camps 2024 quoted exactly.
- 7.4: the distal per-edge speeds 3.00 / 2.88 / 2.84 m/s (straight-line 2.00) lie inside Camps's 2.0-4.0 m/s; a slower
  trunk moves gate 1 toward passing and is near-neutral to away on 7(T) and (b).
- 7.7, 7.8 and 13: A19 moves 7(T) and (b) away, and its evidence is narrower (Massing pp.610, 620); A21 is near-neutral
  to away on gate 7; A25 acts on gates 2 and 6 in 6G and cannot move gate 7, which is scored on the control heart.
- 8.4 and 17.1: Lin 2016's thickness values and the 9.1 mm cut-off are on p.13 (PDF p.14).
- 8.5: de Kerchove's 6.2 mm is a diagonal at mid-RCS and Toh p.236 cites his LCS wall thickness as the LCC width (item
  3); A28 is a second, smaller measurement, not "the lower bound" (item 12); Toh's rotation pages (p.233, p.236, p.237,
  p.230).
- 8.6: the Hasdemir prevalence written up with numbers (22 % = 21 of 95 hearts; pulmonary 16 of 95, aorta 7 of 95) and
  his strip method; no conflict once the landmark is named.
- Report 2, 17.1 and review log B27: Macchi 2004 is not the source of the 1.5 mm radius.
- Report 7: the Campos 2026 n's added, and the Campos 2025 citation corrected (Heart Rhythm 22:1790-1799).
- Report 20: the controls' IQR corrected to -50 to -27 ms (the intact-Purkinje IQR is -46 to -18 ms; Upadhyay 2019
  p.12); report 29 points to it.
- 13, 15.2 step 8a and 17.3: the arm count.
- 17.1: outflow Purkinje (De Almeida 2020), junction density, sleeve islands, the Toh rotation and the guard reworded.
- 17.3: Massing's adult cases are in Figs 8-12; the digitisation and the dataset check are closed.
- Discrepancies items 7, 11 and 17 carry dated notes.
- **Finalisation of the re-issue (20 Oct 2026), each checked against the source:**
  - Durrer 1970: the 4-heart basis and the anterior paraseptal description are on p.901, now cited with pp.899 and 906
    (7.1, section 11 row 7, 19.0, 19.1, 19.3).
  - Myerburg 1972: the islands of early activation are on pp.231 and 239-240, with the Fig 12 legend on p.233, not
    pp.238-239 (7.1).
  - Camps 2024 p.11: the 7 ms (84 to 77 ms, 8.3 %) is the time to activate the ventricles; the QRS shortening is stated
    only as "a significant shortening of the QRS duration", with PCC 0.97 (19.0).
  - Campos 2025: the PDF prints "(c) 2024" and no online date (report 7). Campos 2026: the abstract's 270 locations are
    the pre-exclusion count (report 7).
  - Kaufman and Johnston 1943 Table IV p.49: the lung's 744 ohm-cm is the postbiologic value from 7 observations; the
    prebiologic value is 766 ohm-cm from 9 (9.4, 19.9).
  - Schwan and Kay 1956 pp.668-669: the ECG-band lung value is 0.080-0.095 S/m; the earlier 0.083 S/m (100 / 1200)
    applied the p.669 20 % in the wrong direction (9.4).
  - de Kerchove 2015: the cited pages are those of the uploaded 2014 online proof (pp.1-9), not journal pages (8.5 item
    2b, 17.2).
  - Lee and Hur 2019: the type means do not reproduce the overall 13.6 mm (n-weighted about 14.9 mm; type 3's subtypes
    13.2 mm); recorded, not corrected (7.2, 19.2).
  - D6 arithmetic: at a 24-27 mm span the 12.7 mm rule sits 2.6-3.7 mm above the 37.3 % rule, not 1-3 mm (8.2, 14.1,
    19.6). The 24-27 mm span itself is labelled as what it is (20 Oct 2026): a post-lock review estimate, stated by the
    outflow verifier without a derivation, not a mesh measurement and not a Jakiel value; each mesh's span comes from
    the step-2b report (report 35 (f)).
  - The sleeve islands' "never specified" reworded to "cannot be specified from the sources read" (8.6, 13).
  - The R3.3 wall and A31 fat relabels to Schwan and Kay 1956 pp.666 and 668 came from a reviewer suggestion the verifier
    did not check; the values were checked against the PDF in the cloud on 20 Oct 2026.
  - The summary put to Alex (the doc tab "After the lock") listed page fixes for Toh, Kuniewicz and de Kerchove; the
    post-lock review contains no Kuniewicz page fix, and none is made (20 Oct 2026). Alex is told when the answers are
    filled in.
- **Second re-issue (20 Oct 2026), each checked against the PC's step-0 report or its follow-up geometry:**
  - 7.1, 11 (row 7), 14.1 and 14.2: v5.1 has three LV fascicles, anterior, septal (ending at z 0.50) and posterior; the
    13:51 text's "the septal outflow has no v5.1 counterpart" and "two fascicle endpoints" are corrected (D11).
  - 7.2, 13, 14 and 17.1: v5.1's right bundle is not septal-only; it already crosses the moderator band (D16).
  - 9.4 and 16 (45): "the first four" KIT shapes include the primary T_13 (D17).
  - 9.4 and 19.15.7: the PC's "25 shapes plus a mean torso" is read with the record's description ("25 torso models,
    T13 is the mean shape", Zenodo 20086105): T_13 is one of the 25 shapes and is the mean shape used since 2 Oct 2026
    (9.3); the archive's extra meantorso file is a separate file and is not used.

### 19.14 Considered in the re-review and not applied

- **S3 as the primary conductivity set:** refuted by the verifier; S3 stays arm A9.
- **Dropped again on re-check:** the Macchi latency arm, the Toh Fig 6 rotation, the sleeve islands, a flat-topped
  crescent lune (assumption 12 stays declared), a 36 ms cusp exit delay, and a 9.1 mm summit wall guard.
- **Not proposed:** the sleeve beyond the transition zone (it could now be specified from Lis and Hasdemir, but would add
  an arm on a report-only family).
- **Not used:** the 15.3 mm cut rule measured down from the ring (D6); an LCC axial cap (D5); one host torso for both A35
  and A36 (D9, recorded as an option).
- **Reviewer wording suggestions the verifier did not check, not applied** (wording only; none is needed for the
  re-issue): the crest row's reason and the Doste row's contradiction with section 1 (17.1); A27's source cell (Xie
  2010); the septal-outflow attachment check (its planned z is already reported, report 34 item 3); the Clerc
  temperature label and the 1 kHz labels other than the lungs' (9.4); the KCL 0.24725 S/m as a 9.3 comparison value; the trabecular blood-and-muscle limitation of
  the forward model.
- **Refuted by the verifier, not applied:** the "15/cm2, junctions about 0.9 mm apart" figure (15/cm2 gives about
  2.6 mm spacing; the 14 Oct notes give 10.7-12.0 per cm2).
- **Not applied from the finalisation checks:** a stop rule on a moderator-band insertion outside the middle third of the
  septum, because Lee and Hur's origins range from the supraventricular crest to the apex, with 11 of 36 outside the
  middle; the level is reported instead (report 34 item 12).

### 19.15 Deviations after step 0 (D11-D17, 20 Oct 2026)

At step 0 the PC ran the read-only checks of 15.2 on the 13:51 file (PC report README-20261020T170855-4447.md, written
20 Oct 2026 17:08 UTC; PC clock 18:32-19:08 CEST): nothing was simulated, no gate value was looked at and no model file
was changed. All checksums matched. Two step-0 rules sent the report to Alex before step 1: the outflow attachments of
7.1 (report 34 item 13) and the D1 counts (items 4 and 8). Five further findings bore on later steps (PC report section
2). Two would have stopped them: the aortic angular frame (8.5 item 6, step 2c) and the moderator band that v5.1
already has, whose assumption-47 end node the mesh's labels cannot give (7.2, step 2g). Three needed a definition or
Alex's word: the valve discs on which the crescent and sleeve heights are measured (8.5, 8.6), the infundibulum cut on
a short posterior RVOT (8.2, step 2b; it would have built, splitting almost nothing, 19.15.4), and A37's list, which
begins with the primary torso (before step 8a). Alex chose "Lock thread" in the PC thread ("lock", 20 Oct 2026 17:11:07
UTC): the lock's thread drafts dated fixes and the PC continues from the re-issued file. Each fix below is sourced or
declared as a model assumption, written before any v5.2 beat and chosen without reference to any gate; its gate effect
and its calibration label follow 11.5. The follow-up geometry the fixes needed (report 34 item 15 and report 35 (i))
was measured read-only by the PC on 20 Oct 2026 and relayed at 17:34:23 UTC (PC: followup.json, step0_followup.py, local commit
a2e25a1), before the fixes were written into this file. Each deviation takes the date and time of Alex's answer,
recorded in 0.1.

#### 19.15.1 D11: the sheet's outflows beyond its envelope

- **Finding (report 34 items 1 and 13).** The 13:51 text attached the sheet's anterior and posterior outflows to the
  two v5.1 fascicle endpoints, but the posterior one lies outside the 22.6 mm envelope in all three hearts and the
  anterior one in two: the posterior endpoint 57.8 / 48.4 / 48.2 mm
  down the His line, 15-25 mm beyond the 33 mm sheet end, in all three hearts; the anterior endpoint 2.2 mm
  (Y5HYEDL4) and 6.8 mm (7D98EVAR) beyond the envelope's anterior edge at its level, and inside it in 6G8DD8S5. The
  envelope itself stays on the left septal surface (0 nodes off it). v5.1 also has a **septal** fascicle, ending at the
  code's central Durrer point (z 0.50, AHA 9), which the 13:51 text said did not exist ("the septal outflow has no v5.1
  counterpart"; corrected here). The follow-up geometry (report 34 item 15) gives where each path, His to endpoint along
  the LB_TRUNK and FASCICLE edges, first leaves the envelope: anterior at s 7.5 mm, a +15.9 mm (limit 12.6 mm there) in
  Y5HYEDL4 with 2.6 mm beyond, never in 6G8DD8S5 (endpoint inside), at s 10.0, a +15.2 mm in 7D98EVAR with 7.1 mm
  beyond; septal past the sheet end at s 34.7 / 33.9 / 33.5 mm, 6.0 / 0.8 / 1.4 mm beyond (endpoint outside in all
  three, at s 39.3 / 33.9 / 35.3 mm); posterior at s 32.8 / 32.1 / 33.5 mm, 24.7 / 14.7 / 16.0 mm beyond; none re-enters.
  DISTAL edges meet LB_TRUNK or FASCICLE nodes only at the three fascicle endpoints (0 / 1 / 0 of them inside the
  envelope), and with the trunk and fascicles removed the v5.1 LV network is one connected component in every heart
  (3,758 / 3,183 / 3,180 nodes).
- **What changes.** The sheet replaces the v5.1 LB_TRUNK and FASCICLE nodes and edges **only inside its envelope**.
  Beyond the envelope, each v5.1 fascicle path (anterior, septal and posterior), from the point where it first leaves
  the envelope to its endpoint, is **kept exactly as v5.1 built it**: its nodes, edges, v5.1 edge classes and speeds,
  and no PMJ, and the distal trees it feeds, apart from D1's junction mask, which applies to the distal network as before. It
  joins the sheet through its own v5.1 edge from its exit node (its first node outside the envelope, report 34 item 15)
  to the sheet node at the mesh node of its last node inside, or the nearest sheet node if none shares it, with that
  edge's v5.1 class and speed (assumption 56). Every v5.1 DISTAL edge that joined an
  LB_TRUNK or FASCICLE node inside the envelope is joined instead to the sheet node at the same mesh node (the nearest
  sheet node if none shares it), so every v5.1 distal tree keeps its root. The septal outflow of 7.1 (assumption 31:
  the v5.1 LV distal node nearest the mid-septal point at 50 % of the sheet's extent) is kept as adopted. The envelope
  is not widened, and no v5.1 node outside it is moved or reclassified.
- **Source.** Massing 1976 p.614 (human ex vivo, n = 10 non-neonatal hearts): the left bundle can be traced for 24-41
  mm, after which the septum is "relatively diffusely covered by Purkinje fibers"; p.618: in none of 13 hearts, nor
  Tawara's 2, did the left bundle separate into only two major divisions with no major interconnections; p.620: in five
  of their cases its distribution was a close anatomical fit with Durrer's three early LV areas. The three outflows
  (anterior, septal and posterior) are this lock's reading of that anatomy (7.1, topology row), with Demoulin 1972
  p.807 (human ex vivo, 20 control hearts: three main, widely interconnected peripheral networks, anterior,
  centroseptal and posterior). Demoulin 1972 pp.808-809 (human ex vivo, 20 control hearts): a 6-10 mm ribbon fanning
  into 2-3 radiations, with peripheral anastomoses in all 20 (19.0). Durrer 1970 pp.899 and 901 (human; the early areas
  from 4 hearts): three early LV endocardial areas. The sheet is Massing's; beyond it, the conduction toward the code's
  Durrer points stays the route v5.1 already built.
- **Not tuning.** It keeps v5.1's fascicle paths beyond the sheet (their nodes, edges, class and speed) and the distal
  trees they feed, so D11 itself changes nothing beyond the envelope. The only change there is D1's junction mask,
  which removes the v5.1 LV junctions above the D1 line on the left septal surface beyond the envelope as well
  (deviation D1; kept on step-0 card 4, "Keep", 20 Oct 2026 17:33:10 UTC). Step-0 card 1's consequence ("Conduction
  beyond the sheet stays exactly as in v5.1") holds for the paths, edges, classes and speeds, not for those junctions.
  It was chosen from step-0 geometry, before any beat and with no gate value seen.
- **Gate effect.** The 13:51 attachment could not be built, so no change against it can be stated. Against the
  alternative ("Nearest node"), the code's Durrer points are still reached along v5.1's fascicle paths rather than
  through the distal network; direction not predicted ("?") on gates 1, 2, 3, 5, 6, 7 and 9, as for the sheet and D4,
  and gates 4 and 8 "0" (section 14).
- **Calibration label.** The sheet's: gates 2, 5, 6 and 7 ((a), (T), (b) and the RV items), since D11 sets where the
  sheet joins the LV network (11.5, limb (ii), as D4). Not gates 1, 3, 8 or 9, as for the sheet.
- **Acceptance at step 2g.** Every v5.1 LV distal-network node is reachable from the His through the sheet, as in v5.1
  (6G8DD8S5 checked before its cut; after the cut, 7.8 applies); the kept fascicle paths are identical to v5.1's from
  the exit node to the endpoint, with each join edge as assumption 56 states; per heart, the exit node, the kept length
  and the join edge (its two nodes, class and length) of each fascicle path and the number of distal edges re-joined to
  the sheet are reported (report 34 item 15). If any LV distal node is unreachable, stop and report; no edge is added
  to reach it. Measured read-only before this was written in: 0 / 0 / 0 LV distal nodes unreachable, 40 / 18 / 30 tail
  nodes kept, 0 / 2 / 0 distal edges re-joined (report 34 item 15).
- **Alex's word.** step-0 card 1 (the sheet's outflows), "Keep tails", 20 Oct 2026 17:32:26 UTC.
- **If declined ("Nearest node").** Each outflow whose v5.1 endpoint lies outside the envelope attaches to the v5.1 LV
  distal node nearest that endpoint inside the envelope, and the v5.1 fascicle paths beyond the envelope are removed;
  an endpoint inside the envelope is attached as it stands. The same reachability acceptance applies at step 2g, with
  the same stop.

#### 19.15.2 D12: D1 kept after the step-0 counts

- **Finding (report 34 items 4, 8, 10 and 13).** v5.1's LB_TRUNK and FASCICLE nodes carried no PMJ (0 on 125 / 82 /
  105 nodes; 18 / 8 / 13 distal-network junctions share a mesh node with one of them), so for the
  sheet D1 partly restores v5.1. On the network D1 is not a no-op: 255 / 239 / 220 v5.1 LV junctions lie above the D1
  line on the left septal surface (AHA 2, 3, 8 and 9) and are removed. The line lies 33.4 / 25.7 / 29.0 mm from the
  septal crest and crosses the His line 28.7 / 29.2 / 25.4 mm below the His exit, so junctions are allowed on 132 of
  628, 35 of 603 and 128 of 579 mm2 of the sheet (21 / 6 / 22 %), its lowest band.
- **What changes.** Nothing: D1 stands as written (7.1, 19.1). The step-0 report went to Alex before step 1, as 15.2
  step 0 requires.
- **Gate effect and tuning.** D1's, unchanged (19.1; section 14): D1 leans failing gate 1 toward passing and is
  tuning-shaped, as declared in 7.1 and 19.1. The step-0 counts give the size of the junction change (255 / 239 / 220
  v5.1 LV junctions removed; junctions on 21 / 6 / 22 % of the sheet's area), not its effect on any gate; D1 was kept
  before any beat, with no gate value seen.
- **Calibration label.** Unchanged (D1's, 11.5).
- **Alex's word.** step-0 card 4 (D1 after the step-0 counts), "Keep", 20 Oct 2026 17:33:10 UTC.
- **If declined ("07:30 rule").** D1's "If declined" text (19.1) is applied to every section it names.

#### 19.15.3 D13: the valve-plane ring on the mesh's valve discs

- **Finding (report 35).** The mesh valves are solid discs 5.7-6.3 mm thick (aortic 6.3 / 5.7 / 6.2 mm, pulmonary
  6.2 / 5.8 / 6.2 mm), and ventricular muscle already wraps their rims: LV muscle reaches 1.1-5.5 mm above the aortic
  disc's mid-plane all round the root (sinus medians L / R / N, read in the 13:51 frame, 3.4 / 4.4 / 4.5, 2.7 / 3.4
  / 4.0 and 3.3 / 4.0 / 4.4 mm), and RV muscle 1.7-8.0 mm above the pulmonary mid-plane (medians 3.9-6.9 mm). The 13:51
  text measured the crescents from "the aortic valve-plane ring" and the sleeves from "the cusp-insertion nadir"
  without saying which part of a 6 mm disc either is; the PC read the aortic ring at the mid-plane and the pulmonary
  nadir at the ring's lowest point, 2.3-3.7 mm below the mid-plane.
- **What changes (assumption 55).** On both valves the reference is the **mid-plane ring**: the closed curve where the
  valve disc's mid-plane meets the luminal wall. On the aortic side it is "the aortic valve-plane ring" of 8.5 (items
  2b, 5, 9 and 11b; assumption 13) and of report 35 (a), (b) and (h). On the pulmonary side, each sinus's
  "cusp-insertion nadir" (8.6) is the mid-plane ring's point at that sinus's centre (placed by assumption 18), and the
  sleeve's height, its 25 / 50 / 75 % thickness levels, the max(existing, 4.0 mm) rule and the supravalvar sites are
  measured from the mid-plane ring. The infundibulum cut's 100 % landmark (8.2, assumption 32) is the same pulmonary
  mid-plane ring, and its 0 % landmark is read from that ring's lowest posterior point. Each disc's thickness, its two
  faces and the existing muscle above each face are reported (report 35 (a) and (h), per position).
- **Why.** The meshes carry no leaflets, hinge lines or nadirs (virtual-cohort tag list); each disc is the pipeline's
  valve region, and its mid-plane is the valve plane of the PC's report 35 (taken as the construction's own: inference,
  no pipeline source), so it is the reading that adds no offset of its own; which face an anatomical hingeline would
  sit on cannot be read from the mesh (model assumption). Of the two readings put to Alex on step-0 card 2, it is also
  the one under which the precondition of 8.5 item 9 (a build check, not a gate), adopted at 13:27:28 UTC, holds:
  report 35 (h) puts the tag-1/tag-5 boundary 2.0-5.6 mm above the mid-plane at all six positions in every heart, but
  below the arterial face (about 3 mm above the mid-plane; half of each disc's thickness) at some positions in every
  heart, where a lune measured from that face would add muscle instead of only bounding it.
- **What it builds.** At step 0, with the sinuses read in the 13:51 nearest-point frame, existing muscle exceeded the
  RCC axial cap (2.4 mm) at every angle of the RCC lune, and the LCC lune could add muscle only where the existing LCC
  muscle was lower (down to 1.1 mm in 7D98EVAR). D15 moves theta = 0 to the mitral-centroid direction, 67.8 / 54.4
  / 61.0 deg from the 13:51 zero (report 35 (i)), and the sense the step-0 sinus medians were read in is not stated, so
  only the all-round ranges carry over to the adopted frame: LV muscle 2.6-5.3 / 2.2-5.1 / 1.1-5.5 mm above the
  mid-plane. In Y5HYEDL4 every value exceeds the 2.4 mm cap, so its RCC crescent adds nothing in any frame; where the
  crescents add muscle in 6G8DD8S5 and 7D98EVAR is read at step 2c (report 35 (b)). Existing RV muscle exceeds the
  sleeve's 4.0 mm over most of the pulmonary ring, whose sinuses are placed by assumption 18 and not by the aortic
  frame, so the sleeves add little: sleeve muscle where the RV muscle stands less than 4.0 mm above the mid-plane
  (6G8DD8S5 from 2.0 mm and 7D98EVAR from 1.7 mm; none in Y5HYEDL4, whose minimum is 4.2 mm). Nothing is trimmed (8.5
  item 9; 8.6), and whether the cusp sites at 50 % of the built extent (D5 (c)) fall in muscle the mesh already carries is read
  at step 2c (report 35 (b)); in 7D98EVAR existing LV muscle stands as low as 1.1 mm somewhere around the root, under
  half the LCC crescent's 2.9 mm (8.5 item 11), so an LCC site there may fall in muscle the crescent build adds
  (step-0 card 2's consequence, "the cusp and sleeve sites sit in muscle the mesh already has", is qualified here,
  20 Oct 2026).
  Step 2c runs: precondition 35 (h) passes.
- **Not tuning.** A definition the adopted structures need in order to be built, fixed from geometry before any beat;
  it changes no sourced dimension.
- **Gate effect.** Against the arterial-face reading, less new outflow muscle and cusp and supravalvar sites about 3 mm
  lower: gate 1 "0 or -", gates 3 and 8 "?".
- **Calibration label.** As the crescents (gates 1, 3 and 8) and the sleeves (gate 3), since it sets the outflow
  muscle at their sites (11.5).
- **Alex's word.** step-0 card 2 (the valve-plane ring), "Mid-plane", 20 Oct 2026 17:33:39 UTC.
- **If declined ("Arterial face").** The reference on both valves is the arterial-face ring, the closed curve where the
  disc's arterial face meets the luminal wall, and every measurement above is made from it; the precondition of 8.5
  item 9 is re-measured from that face, and since the tag-1/tag-5 boundary lies below it at some positions, the build
  stops before step 2c and the crescent rule goes to Alex.

#### 19.15.4 D14: the infundibulum cut scaled to the mesh's posterior RVOT span

- **Finding (report 35 (f)).** The mesh's posterior RVOT wall, from the superior tricuspid annulus to the pulmonary
  ring (the disc's wall contact; the level within it is not stated), is 13.6 / 10.2 / 13.7 mm (second reading 12.8
  / - / 13.1 mm) against Jakiel's 26.9 +- 6.5 mm (Table 1, 220 human hearts), 2.0-2.6 SD short in all three hearts
  (derived: (13.6 - 26.9) / 6.5 = -2.05; (10.2 - 26.9) / 6.5 = -2.57; (13.7 - 26.9) / 6.5 = -2.03). D6's 12.7 mm split
  falls at 93 % of the span in Y5HYEDL4 and 7D98EVAR and beyond the ring in 6G8DD8S5, so the free-standing infundibulum
  would be split from the LV over 0.9 / 0 / 1.0 mm of the posterior wall (derived: 13.6 - 12.7; none; 13.7 - 12.7),
  against Jakiel's posterior infundibulum height of 15.3 mm.
- **What changes.** The septal component's upper limit on the posterior RVOT wall is **47.2 % of the mesh's own
  posterior span above the 0 % landmark** (derived: 12.7 / 26.9 = 0.472, the ratio of Jakiel's mean septal-component
  maximum height to his mean posterior RVOT wall, Table 1): 6.4 / 4.8 / 6.5 mm at the step-0 spans (derived:
  0.472 x 13.6 = 6.42; 0.472 x 10.2 = 4.81; 0.472 x 13.7 = 6.47; the step-0 spans run to the PC's "pulmonary ring",
  the disc's wall contact, at a level within it that the report does not state, so these heights are provisional),
  recomputed from the span measured at step 2b on the first reading of report 35 (f) (as defined there), with the 0 %
  and 100 % landmarks of 8.2 (the 100 % landmark is the pulmonary mid-plane ring, D13, and the 0 % landmark is read
  from it). Below it the tag-1/tag-2 interface stays fused; above it, it is split. The same rule sets the
  8.1 labels. D6's 12.7 mm, the 07:30 37.3 % and the 15.3 mm-below-the-ring rule are reported beside it at step 2b
  (report 35 (f)), with the tag-1/tag-2 area above each, which is reported and not used.
- **Why a proportion here, against D6's reason.** D6 chose a fixed height because Jakiel's septal height is nearly
  independent of the posterior RVOT height (Table 2: r = 0.199) while the posterior infundibulum tracks it (r = 0.745).
  That reasoning treats the mesh span as an anatomical span. All three meshes are 2.0-2.6 SD short, the control heart
  included, which points to how the mesh's outflow landmarks were built (6 mm valve discs, report 35; the pipeline's
  valve cuts) rather than to three anatomically short outflow tracts (inference). A fixed 12.7 mm would then leave
  almost no free-standing infundibulum, against Jakiel's posterior infundibulum height of 15.3 mm (Table 1). The
  proportion maps Jakiel's mean anatomy onto each mesh's own landmarks, as the model places its other sites in
  normalised coordinates (UVC). It is chosen from the span, not from contact area or gates.
- **Not tuning.** Fixed from geometry before any beat; no gate value was seen.
- **Gate effect.** More of the posterior RVOT is split from the LV than under D6: RVOT paced QRS longer by a few ms;
  gate 3 "?" (the J3b test: delaying LV access raised the RVOT MDI, 14.1), gates 1 and 8 "?".
- **Calibration label.** As the cut: gates 1, 3 and 8 (11.5).
- **Alex's word.** step-0 card 3 (the infundibulum cut), "Scale to span", 20 Oct 2026 17:32:47 UTC.
- **If declined ("Keep 12.7 mm").** D6 applies as written (19.6): fused below 12.7 mm above the 0 % landmark, for the
  cut and the 8.1 labels; in 6G8DD8S5 the posterior wall then stays fused over its whole span, which is reported, not
  a stop.

#### 19.15.5 D15: the aortic angular frame on the mesh

- **Finding (report 35, angular frame check; report 35 (i)).** 8.5 item 6 anchored theta = 0 at the aortic-ring point
  nearest the mitral ring and accepted the direction of increasing theta if the ring point nearest the pulmonary valve
  lay 90-150 deg from it (Toh's 120.4 deg). It lay 42.3 / 62.9 / 60.9 deg away for the ring point nearest the
  pulmonary-valve disc (the other sense 317.7 / 297.1 / 299.1 deg; report 35 (i)), and the PC's second reading (nearest
  the disc centre) failed as well (PC report section 2), so step 2c would stop. The follow-up geometry shows why: the
  aortic and mitral discs never touch on these meshes (closest ring-to-ring distance 8.84 / 7.66 / 7.91 mm; no
  aortic-ring node within 1.05 mm of the mitral ring), so "the point nearest the mitral ring" is not a point of
  continuity, and the ring points within one mean edge of that minimum spread over 19 / 132 / 137 deg.
- **What changes (assumption 14 rewritten).** theta = 0 is the direction of **the mitral-disc centroid**, projected
  onto the aortic disc's mid-plane about the root's central axis (the aortic disc's normal through the aortic ring's
  centroid). The direction of increasing theta is the sense in which **the pulmonary-disc centroid**, projected the same
  way, lies 90-150 deg from theta = 0 (Toh's L-R interleaflet triangle lies at 120.4 +- 5.2 deg; that it faces the
  pulmonary valve is this lock's check rule, kept from 13:51, not a statement of Toh's). The stop rule of 8.5 item 6 is
  unchanged: if neither sense puts it in 90-150 deg, stop and report, and do not pick the closer. The frame serves
  every use of Toh's theta: the lunes and the hard gate of 8.5, the cusp sites of 8.5 item 11b, the RCC cap of item 2b,
  de Kerchove's six positions in report 35, and the LCA ostium of the summit re-anchor (8.3 step 1), its angle and the
  plane and axis its 14.8 mm height is measured from (the aortic disc's mid-plane and its normal). The 13:51
  nearest-point readings are reported beside it.
- **Measured before it was written in (report 35 (i), read-only).** The pulmonary-centroid direction lies 126.9 / 126.4
  / 128.1 deg from the mitral-centroid direction (derived from the PC's angles: 59.1 - 292.2 + 360; 72.0 - 305.6 + 360;
  67.1 - 299.0 + 360), inside 90-150 deg in all three hearts, so the frame check passes and step 2c can run. Reported
  beside it, not used: the centre of the arc where RV muscle (tag 2) touches the aortic root (tag 5) 0-6 mm above the
  mid-plane lies at 183.9 / 186.7 / 190.4 deg in this frame (derived: 116.1 - 292.2 + 360; 132.3 - 305.6 + 360;
  129.4 - 299.0 + 360), at the right coronary sinus (de Kerchove's RCS, placed at 180.7 deg in Toh's frame as in the
  PC's report 35; derived: (120.4 + 241.0) / 2, midway between Toh's L-R and R-N interleaflet triangles; de Kerchove
  gives positions, not angles), where Gami 2011 pp.9-10 found the RCC sinus wall contiguous with the posterior RVOT
  infundibulum in 603 of 603 human autopsy hearts; within 0-3 mm the contact is 4 / 8 / 0 nodes, centred at 167.7
  / 219.0 deg / none (derived: 99.9 - 292.2 + 360; 164.6 - 305.6 + 360).
- **Source and why.** Toh 2020 (84 living human hearts, CT): theta = 0 at the bisector of the non-left interleaflet
  triangle; the left and right fibrous trigones at 52.4 and 305.0 deg, so the aorto-mitral continuity between them is
  centred at -1.3 deg (derived: (52.4 + 305.0 + 360) / 2 - 360), within this frame's resolution, so no offset is
  applied; the L-R interleaflet triangle at 120.4 deg. The continuity is where the anterior mitral leaflet hangs from
  the aortic root, so its centre faces the mitral orifice, and the projected direction of the mitral-disc centroid is
  the mesh's reading of it (model assumption, assumption 14); centroid directions are used for both valves, so the two
  ends of the check are read the same way.
- **Not tuning.** A construction rule for a frame the meshes do not carry, fixed from geometry before any beat; the
  frame check is a geometric acceptance, not a gate, and no gate value was seen. The rule follows from why the
  nearest-point reading fails (the discs do not touch); it was not chosen among candidates for passing.
- **Gate effect.** The 13:51 frame could not be built, so none can be stated against it; the crescents, the cusp sites
  and the summit sites now sit at Toh's angles in a frame whose pulmonary-disc centroid lies 126.4-128.1 deg from
  theta = 0 (Toh's L-R triangle 120.4 +- 5.2 deg) and whose 0-6 mm RV-root contact arc, 161-189 deg wide (derived:
  331.0 - 156.9 = 174.1; 308.4 - 147.0 = 161.4; 324.8 - 136.3 = 188.5), is centred at 183.9-190.4 deg, near the RCS,
  where Gami found the RCC sinus wall contiguous with the infundibulum: gates 1, 3, 5 and 8 "?".
- **Calibration label.** Gates 1, 3, 5 and 8 (11.5, limb (ii)): it places the crescents and cusp sites of gates 1, 3
  and 8 and, through the LCA ostium, the summit sites of gates 1, 3, 5 and 8, as the crescents and the summit re-anchor.
- **Alex's word.** step-0 card 5 (the aortic frame, the right bundle and the torso list), "Adopt all", 20 Oct 2026 17:36:27 UTC.
- **If declined.** The 13:51 rule applies (theta = 0 at the aortic-ring point nearest the mitral ring), its check fails
  in every heart, and the build stops before step 2c for Alex's word, as 8.5 item 6 says.

#### 19.15.6 D16: the moderator band is already in v5.1

- **Finding (report 34 items 5, 6 and 12).** v5.1's right bundle runs down the RV septum to the moderator band's
  septal insertion (z 0.351 / 0.349 / 0.353) and then crosses the cavity as one straight edge of class RB at 1.5 m/s,
  with no PMJ, to the anterior RV free wall, where the v5.1 RV distal network starts: 14.7 / 18.2 / 10.1 mm, against
  Lee and Hur's 13.6 mm and all within assumption 54's 37.8 mm. Its septal insertion lies at 0.82 / 0.63 / 0.82 of the
  RV septum from crest to apex (lower, middle and lower third; Lee and Hur: middle of the septum in 25 of 36). The 13:51
  text read v5.1 as septal-only (7.2: "the septal-only course of the 07:30 lock becomes arm A20"), so D2's chain would
  duplicate a band v5.1 already has. The mesh carries no papillary muscle and no anterior RV free-wall label, so
  assumption 47's end node could only be a construction.
- **What changes.** The primary right bundle is **v5.1's, unchanged** (identical, its moderator-band edge included);
  no new chain is built. Assumption 47 is withdrawn, and assumption 54's 37.8 mm limit is reported against v5.1's band
  (all three within it) rather than used as a stop. D2's anatomy (the RB along the moderator band to the anterior RV
  free wall, no PMJ on its free-running part) is what v5.1 already has, so the choice on post-lock card 2, change 2,
  stands in substance. **Arm A20** becomes the counterfactual the 13:51 text meant, the RB on the septum only: v5.1's
  band edge is removed and the RB ends at the band's septal insertion, which joins the nearest v5.1 RV distal-network
  node with a PMJ (7.3 delays; assumption 58); if any RV distal node is then unreachable from the His, A20 is recorded
  "not run" with the reason, and no edge is added.
- **Source.** As D2: Stephenson 2017 p.4; Lee and Hur 2019; Massing 1976 p.615 (7.2).
- **Not tuning.** A correction of a premise; nothing is built.
- **Gate effect.** None against v5.1, since nothing changes: D2's signs (7(c) earlier and possibly below 20 ms, RV
  onset earlier, gate 1 "0 or -", gate 8 "0 or +") are withdrawn. A20 against the corrected primary: RV onset later,
  7(c) later (toward or past 31 ms), gate 3's RVOT value and gate 4 either way, gate 1 "0 or +", gate 8 "0 or -".
- **Calibration label.** None: v5.1's right bundle is not a change (as the retrograde 2 ms row of 11.5). D2's gate-7
  label ((c) and the RV items) is withdrawn because nothing it named is built.
- **Alex's word.** step-0 card 5 (the aortic frame, the right bundle and the torso list), "Adopt all", 20 Oct 2026 17:36:27 UTC.
- **If declined.** D2 is built as written at 13:51, replacing v5.1's band edge: the 1 mm chain at 1.5 m/s with no PMJ
  on its free-running segment runs from the band's septal insertion to the PC's step-0 construction of assumption 47
  (report 34 item 12: nodes 369808 / 37002 / 26551, chains 12.0 / 16.0 / 9.0 mm), whose label rule is written into
  LABNOTES before step 2g; A20 as above.

#### 19.15.7 D17: A37's four torso shapes

- **Finding (step 0).** In the archive's own order the KIT shapes are T_13, T_24, T_20, T_17, T_01, T_05, T_09, ...
  (25 shapes, of which the record's description names T_13 the mean shape, plus a separate meantorso file that is not
  used; record 20086105, torsoModels.zip, md5 528b7c89...), and T_13 is the primary torso
  (9.3), so "the first four" would make one of A37's shapes the primary itself.
- **What changes.** A37's four shapes are the first four in that order **other than the primary T_13: T_24, T_20,
  T_17 and T_01**. Assumption 45 amended.
- **Source.** Bender 2026 (Zenodo 20086105). **Not tuning.** Bookkeeping, before any beat. **Gate effect.** As A37.
  **Calibration label.** None (an arm).
- **Alex's word.** step-0 card 5 (the aortic frame, the right bundle and the torso list), "Adopt all", 20 Oct 2026 17:36:27 UTC.
- **If declined.** The first four as listed (T_13, T_24, T_20, T_17), with T_13 reported as a reproduction of the
  primary.

#### 19.15.8 Recorded at step 0, no deviation

- **A35 not run** (9.4; deviation D9a). Checks (i)-(iii) passed; check (iv) failed: KCL_torso1 ends at z -306 mm,
  above the iliac crest, so the LL electrode cannot be placed by the Kligfield rule, and the skeleton is one tag in one
  connected piece, so the clavicles cannot be told apart. The arm is recorded as not run, with this reason.
- **A36 not run** (9.4; deviation D9b). Torso.vtu carries no skeletal muscle (Material 8 is listed in material.tab, but
  no cell carries it), and its 24.95 M cells need about 12-13 GB against WSL's 7.7 GB. Recorded as not run.
- Step 8a therefore runs at most 37 of the 39 arm entries (A17, A18 and A20 are also recorded as not run if their reachability checks fail, 7.1, 7.2); the absence of lungs and skeletal muscle stays a stated limitation of
  the forward model (9.4).
- Also recorded, no change: the meshes carry no supraventricular crest, papillary muscles or trabeculae (report 34
  item 5, report 35 (g)); the cavity caps of R3.1 are possible in all three hearts; the v5.1 stimulus radius is 1.5 mm.

## Discrepancies found while writing

Each of these is a conflict between files, or between a file and a primary source. Where the adopted list and a source
disagreed, I followed the source and flagged it here.

1. **Gate 5's comparator (open; needs Alex's word).** The **approved gate rule** of 12 Oct (notes/A/2026-10-12-aim1-gate-
   rules-draft.md, approved 18:27 UTC) gives Bazan Table 3's **matched** figures as the bands - basal superior q in
   lead I +67.2 points, CI 53.8-80.7, from 50/58 against 11/58 - and the 12 Oct scorecard scored the model against
   53.8-80.7. The **v5.1 Table A cell and MEMORY** instead name the **unmatched** +74 points (90 % against 16 %) as the
   locked comparator. The files conflict, and the project rule is that the files win, so I have drafted the **approved
   rule text** as primary (five matched sub-checks with their CIs, 11.3) and report the unmatched comparison with its
   own CI beside it (+73.7 points, Wald 64.4-82.9, my arithmetic). Nothing is loosened either way: v5.1 fails both. The
   adopted 18 +- 5 mm pair geometry also fits only the matched comparator. **Alex's word settles which is the gate.**
2. **Gate 9's v5.1 status (resolved).** Table A of 18 Oct 20:38 UTC records gate 9 as "not run", but the check **was**
   run on v5.1 the next day and **failed: 72 of 108 pairs within 5 ms, maximum 38 ms, 19 Oct 17:42 UTC** (MEMORY.md;
   README-20261019T185935-93bb.md, "the monodomain check itself failed on 19 Oct"; the 19 Oct draft's own prediction
   table, "72 FAIL"). Table A simply predates the run. So gate 9 is a **scored FAIL** on v5.1 and the tally is
   **2 pass / 7 fail**, which is also what the brief and MEMORY say. The 19 Oct draft's "not evaluable" and its
   attribution of 72/108 to "the earlier engine comparison" are withdrawn, and no step-0 reconciliation is needed.
3. **Gate 9's threshold wording (not a discrepancy).** "At least 90 % of the 108 site-measure pairs" and "at least 98 of
   108" are the **same rule**: 0.90 x 108 = 97.2, and an integer count of at least 97.2 is at least 98. Neither reading
   is stricter, and the claim that one was is withdrawn.
4. **The "13 degree" rotation.** Card 3's alternative is described as "the v5.1 atrial fit (13 degrees)". The audit
   records three different fitted rotations: 13.4 deg for Y5HYEDL4, 19.9 deg for 6G8DD8S5 and 18.6 deg for 7D98EVAR. The
   swap-in rule uses the per-heart values (9.2).
5. **The HF repolarisation arithmetic.** 28 x 1.110 = 31.1 ms, so a 29 ms HF transmural difference would imply the
   transmural gradient scales by 1.036 and not by 1.110. The adopted list carried both numbers. I resolved it by making
   the derived 7 ms (28 x 29 / 111) the default, which states explicitly that HF flattens the transmural difference
   relative to the mean APD, and by keeping 29 ms as arm A6. No paper measures this in an intact human heart.
6. **Toh's LCC angular SD.** The abstract prints 54.2 +- 12.0 deg where the Results and Figure 8 print 54.2 +- 13.0 deg.
   I used 13.0 (8.5 item 13).
7. **Toh against Gami for the same structure.** Toh (living CT, n = 84) gives RCC 6.4 +- 1.2 mm and LCC
   2.9 +- 0.8 mm; Gami (formalin-fixed autopsy, n = 603) gives 2.8 +- 1.2 mm in 55 % of hearts and 1.5 +- 0.5 mm in
   24 %. They differ by more than a factor of two for the RCC. I kept Toh as primary (living heart, defined plane,
   rotated to the maximum) and made Gami arm A28, which is the lower bound. Both agree on the ordering RCC >> LCC >> NCC.
   **Note (20 Oct 2026):** "the lower bound" is withdrawn: A28 is a second, smaller measurement of the same structure
   (8.5 item 12). Under deviation D5 the primary RCC crescent is capped at 2.4 mm of axial height (8.5 item 2b), so
   where the cap binds it comes close to A28's 2.8 mm one.
8. **Lis's "percentage of sinus height covered".** The reported 26.7-31.9 % do not reproduce against the paper's own
   4.96-5.39 mm sinus wall height (which would give 74-83 %); they reproduce against **cusp length, 13.5-13.8 mm**, for
   **two of the three sinuses** (right anterior 3.69 / 13.8 = 26.7 % against 26.7 %; posterior 4.28 / 13.5 = 31.7 %
   against 31.9 %; but left anterior 4.12 / 13.7 = 30.1 % against the printed 28.9 %). I dropped the ratio from the
   build and used the mm heights directly (8.6).
9. **Lis's two findings with the same counts.** "Sleeves beyond the fibro-arterial transition zone" (posterior 14 of 65)
   and muscular "islands" (right anterior 14 of 65) are reported with the same three counts and the same p = .021 in two
   paragraphs, so one is probably mis-assigned. Neither is built: the beyond-the-zone variant is not run, and the island
   perturbation is not an adopted arm (17.1), so nothing in the lock depends on which sinus leads.
10. **Gami's internal conflicts.** Gami's text and tables disagree twice (none against 2 hearts with all three aortic
    cusps involved; a 19 mm against a 12 mm upper range for pulmonary intercuspal extension). Neither affects a build
    rule, and neither is quoted without this caveat.
11. **The "22 %" Hasdemir figure.** Nothing in the file set supports it. The sources in hand give 7 % (aorta) and 17 %
    (pulmonary) for Hasdemir against Gami's 57 % and 74 % and Lis's 100 %, and the conflict is definitional (8.6).
    **Closed (20 Oct 2026):** this was true when written; Hasdemir 2007 arrived at 07:44-07:45. The 22 % is his
    per-heart figure for either artery, 21 of 95 hearts (pulmonary 16 of 95, aorta 7 of 95); the conflict stays
    definitional and is written up with its numbers in 8.6.
12. **Acosta's cut-off sensitivity.** 68 % in the Results text against 77 % in Table 2 for the same cut-off, with 100 %
    specificity in both; and the LVOT SD is 0.49 in the table and 0.4 elsewhere. Flagged, not averaged (report 24).
13. **The A9 benchmark's attribution.** It is **Doste 2020** that cites Acosta once in its introduction and never
    computes the ratio; **Doste 2019 Table 2 (p.10) does compute it** (OT-RBM RVOT 1.86 +- 0.22), and that is where the
    old "Doste 1.86" benchmark came from. So the clinical comparator is Acosta 2015 and the in-silico comparator is
    Doste 2019, reported side by side (report 24). The blanket re-attribution in the 19 Oct draft is corrected.
14. **Lin's Table 2 SDs against Figure 2.** The subvalvar SD of 0.89 is irreconcilable with a figure in which the whole
    subvalvar group lies between about 1.40 and 1.78, and Lin never defines the aVL/aVR ratio nor states any filter. The
    report therefore scores ordering plus the two outer bands, publishes the model's own definition, and uses no SD as a
    tolerance (report 23).
15. **Prisco's initial-slope values (resolved).** The **main article is in the project**
    (prisco-et-al-2024-rate-of-change-of-initial-intrinsicoid-deflection-..., JACC CEP 2024;10:1150-1160), and it
    states the values: all 12 leads, first 30 ms, **epicardial 4.6 +- 2.2 against endocardial 9.9 +- 4.8 mV/s,
    P = 0.0299**, with the average slopes 6.3 +- 3.1 against 11.4 +- 3.7, n = 26 NICM VT. They are on **journal p.1153
    (text) and p.1156 (Table 2)**, not p.1154 as the project notes say. Report 15 now carries them with the supplement's
    AUC table beside, and the 19 Oct claim that the article "is not here" is withdrawn.
16. **The 1.5 mm stimulus against the new anatomy.** The sleeve apex (0.89-1.04 mm) and the LCC crescent floor (1.5 mm)
    are at or below the ball's 3 mm extent, so a rule was needed before gates 1 and 3 could be read at all (8.7). The
    ball is a **radius** of 1.5 mm, as the PC's own run note records; the 15 Oct brief had left radius-or-diameter open
    and the 19 Oct draft used both readings in different places.
17. **Purkinje trunk speed against its own comparator.** v5.2 keeps 1.5 m/s for His, RB and the LB trunk, which sits
    below Camps 2024's stated human lower bound of 2.0 m/s, while the distal 2.0 m/s sits exactly on it. Lowering the
    trunk speed would help failing gates 1 and 7, so nothing is changed and the mismatch is reported (7.4).
    **Corrected (20 Oct 2026):** the distal network's per-edge speeds are 3.00 / 2.88 / 2.84 m/s (straight-line 2.00),
    inside Camps's 2.0-4.0 m/s rather than on its lower bound; a slower trunk would move failing gate 1 toward passing
    and is near-neutral to away on gate 7 (T) and (b), which are timed from LV onset (7.4).
18. **The intracellular anisotropy that fix 2 implies.** 14.7 in the control heart and 28.6 in the HF hearts, against
    5.7 in MedalCare-XL and about 9 in Clerc. This follows from solving sigma_i from human speeds and is stated as a
    limitation, not corrected (section 3).
19. **The primary conductivity set against the project's own evidence rule.** The rule prefers in vivo intact-heart
    measurements, which would make the in situ set primary over Clerc's in vitro calf trabeculae. The pick stands as
    Alex made it, and the tension is recorded in R2.5 and 17.1 rather than resolved silently.
20. **Gate 1's comparator kind (resolved).** Every QRS duration behind the 147-175 ms band is a **spontaneous**
    arrhythmia QRS (Santangeli 2015 147 / 149; Yamada 2016 169 / 174 / 168; Yamada 2010 summit 175 ms), and the model
    value is a paced QRS. The band stays as locked and the verdict is unchanged in every branch (11.1). The 19 Oct claim
    that the correction "can only make the gate stricter" is dropped: Bazan's paced widths come from a diseased,
    partly drug-treated population, and pace-mapping at the origin is meant to reproduce the spontaneous QRS, so no
    normal-heart paced comparator exists.
21. **Massing's own table against its stated range.** The left bundle length is given as 24-41 mm with an average of
    33 mm, but case 4 is tabulated at 45 mm. I used 33 mm with the 24-41 mm range, and recorded that the range appears to
    describe the confidently delineable extent (7.1).
22. **Hillestad against Stephenson on intramural Purkinje**, two human studies in direct conflict, reconcilable only by
    voxel size. Reported, not resolved; nothing is built (7.6).
23. **Auricchio against Derval on the LBBB line of block.** 23 of 24 against 0 of 11. The model cannot produce a
    functional line of block, so it gets no credit for matching Derval (7.8).
24. **Boukens 2013's n.** The legend says 3 and the panel is annotated 9, and every conduction velocity in it is read off
    a bar graph. The outflow-speed decision cites it with those caveats and quotes no number as exact (5.1).
25. **Blood at 0.7 S/m against its own human formula.** The Maxwell-Fricke formula gives 0.71 S/m at Hct 45 %, so 0.7 is
    a rounding of a human value, and the 10 Hz "0.7" in the Keller table is a Gabriel Part III parametric fit rather than
    a measurement. Both provenances are recorded (R3.1, 9.4).

26. **Vergara against the adopted retrograde delay.** The 20 Oct list adopted a 4 ms retrograde PMJ delay on the stated
    ground that "the 2 ms has no source", but Vergara 2016 p.223 gives an antidromic delay of about 2-3 ms against an
    orthodromic 5-15 ms, and its own model uses 2.0 ms. I kept the adopted value, corrected the premise and the
    mechanism, labelled gates 1 and 3 calibration checks for it, and wrote a one-line swap-in back to 2 ms for Alex
    (7.3).
27. **Massing's two anterior-fibre counts.** pp.612-613 report anterior fibres reaching the basal third in 2 of 13
    hearts (3 more at the basal-middle junction); p.620 reports "in five of our 13" for anterior **subdivisions**
    directed at the basal third. They are different quantities, and the lock now cites each at its own page (7.1, 7.7).
28. **The Prisco page.** Both the adopted row and .notes/inputs.md put the initial-slope values on p.1154. They are on
    p.1153 (text) and p.1156 (Table 2). The lock cites the pages that hold them (report 15).
29. **Toh's own wording.** Toh defines only a "maximal width"; the distal-extent reading the build needs is an
    inference, and it is labelled as one wherever the millimetres are used (8.5 item 3).

## Review log (20 Oct 2026)

Three reviewers (sources, rules, build) checked the 19-20 Oct draft and raised **85 findings**. I verified each one
against the evidence it cites - opening the PDFs and the project files, and redoing the arithmetic - and then applied it
or rejected it. **84 applied, 1 rejected.** Nothing here was resolved by loosening a gate, by demoting one, or by
choosing a value because of its effect on a gate; where a finding's own fix would have done that, the review entry says
so. Two things are held open for Alex because a standing rule reserves them to him, and both are drafted on the
recommended option with a one-line swap-in: the **retrograde PMJ delay** (7.3) and the **gate-5 comparator** (11.3,
discrepancy 1). The two open cards (2 and 3) are unchanged and are drafted on their recommended options.

| # | Lens | Severity | Subject | Verdict | Verification and what changed |
|---|---|---|---|---|---|
| **S1** | sources | blocker | Gerstenfeld MAD denominator | **Applied** | Verified in the PDF: Eq. 1 p.2047 divides by the sum of the two mean-removed absolute values and Eq. 3 p.2048 pools numerator and denominator over 12 leads, called the normalized MAD. Section 10 now carries that equation, with the error and its factor-of-two effect recorded. |
| **S2** | sources | blocker | Niederer stimulus units | **Applied** | Verified on the rendered Table 3 page (p.4339): 2 ms at 50 000 uA cm-3, with the same lost micro sign in the capacitance. 11.4 item 3 and step 6 now read 50 000 uA/cm^3 (= 50 mA/cm^3), plus a stop rule outside 37.8-48.7 ms. |
| **S3** | sources | blocker | Gate 9 v5.1 = FAIL, tally 2/7 | **Applied** | Verified in MEMORY.md (72/108, max 38 ms, 19 Oct 17:42 UTC) and README-20261019T185935-93bb.md; the 18 Oct Table A predates the run. Section 11, 14.2 and discrepancy 2 rewritten. |
| **S4** | sources | major | Prisco values restored | **Applied** | Verified in the main article, which is in the project: p.1153 text gives 4.6 +- 2.2 against 9.9 +- 4.8 mV/s (P = 0.0299) and 6.3 +- 3.1 against 11.4 +- 3.7 (P = 0.0353); Table 2 is on p.1156 (limb P = 0.0246, precordial P = 0.3996); n = 26. Report 15 restored, 17.2 row and discrepancy 15 rewritten. Page corrected to p.1153 / p.1156, not p.1154. |
| **S5** | sources | major | Doste 2019 is in the project | **Applied** | Verified: doste2019.pdf section 2.3.1 / Eq. 3, pp.5-6 states alpha epi 0 deg and alpha endo 90 deg, and that alpha is not the histological helix angle. 17.2 row 12 and its DOI removed; R5.2 cites it. |
| **S6** | sources | major | A9 in-silico comparator | **Applied** | Verified Doste 2019 Table 2 p.10 (OT-RBM RVOT 1.86 +- 0.22, LVOT-RCC 1.02 +- 0.2, LVOT-LCC 0.74 +- 0.25; ST-RBM 0.57 +- 0.16). Report 24 now carries Acosta as the clinical and Doste 2019 as the in-silico comparator; discrepancy 13 corrected to name Doste 2020. |
| **S7** | sources | major | Gate-5 pair selection rule | **Rejected in its core request, applied in part** | The provenance is right and is now stated (Bazan 2007 p.1404: closest opposite endocardial site within 25 mm, mean separation 18 +- 5 mm; Table 3 18 +- 5 / 18 +- 6, apex 19 +- 6), and the achieved separation is reported against 18 +- 5 mm with Bazan's literal rule as a second pairing. But I did not make 'closest within 25 mm' the model's pairing rule: Alex adopted the 18 +- 5 mm matched-pair geometry on 20 Oct, and on a 1 mm mesh 'closest opposite' collapses to v5.1's 3 mm transmural pairs, which would silently undo the adopted amendment. |
| **S8** | sources | major | Bazan's population | **Applied** | Verified Bazan 2007 Table 1: nonischaemic DCM in 9 (one with CAD and no MI), CAD without MI 1, RV cardiomyopathy 1, no structural disease 4, none with prior MI. 11.1 now says 'mostly nonischaemic dilated cardiomyopathy, 4 without structural heart disease, none with prior MI'. |
| **S9** | sources | major | Toh crescent dimension | **Applied** | Verified Toh's own word is 'maximal width' (Methods p.232, tables pp.235-236). 8.5 item 3 now labels the distal-extent reading an inference, and the 0.45-0.50 axial factor is deleted from the build. |
| **S10** | sources | major | RE+ APD90 error | **Applied** | Verified on the rendered Fig. 4 / Table I page (p.517): RE+ APD90 1.13 +- 1.69 ms, eikonal 25.1 +- 20.72 ms, correlation 0.9953; 1.37 +- 1.16 ms is the LAT difference (text p.516). R1.8 corrected, 11.4 keeps the LAT figures. |
| **S11** | sources | major | A7 Srinivasan slope scope | **Applied** | Verified Table 1: transmural slope -0.71 +- 0.4 under LV-endo base pacing only, RV-endo -1.36 +- 1.9, LV-epi +0.63 +- 0.3, global -0.03 / 0.14 / 0.4. A7 restricted to LV-endocardial paced beats, dispersion labelled SE, and the global non-result stated. |
| **S12** | sources | major | Kuniewicz 18.92 mm | **Applied** | Verified Kuniewicz Table 1 (LAD bifurcation to first dominant septal perforator 18.92 +- 5.19 mm; ostium to bifurcation 9.59 +- 4.14; apex angle 85.46 +- 15.94) and Lin's Fig. 1 base definition. 8.3 now calls 18.9 mm the septal margin and builds the base as Lin's SP-to-LCx arc, noting that Kuniewicz gives no base length. |
| **S13** | sources | minor | Decision-log dates | **Applied** | Verified against MEMORY.md and PROGRESS.md: v5.1 frozen 18 Oct 20:43 UTC; Build v5.2 19 Oct 18:04-18:05 UTC; 'dont worry about pc costs' 19 Oct 18:37 UTC. 0.1 corrected and the missing 19 Oct rows added. |
| **S14** | sources | minor | Massing citations | **Applied** | Verified: the no-separable-fascicles statement is under the p.618 header; the 2-of-13 anterior count is on pp.612-613 while p.620 gives 'five of our 13' for subdivisions; Table 1 excludes only the 5 neonates, so cases aged 9 and 15 are included. 7.1, 7.7 and A19 corrected, with A19 labelled an extrapolation of a posterior-fibre finding. |
| **S15** | sources | minor | Bazan page for the site map | **Applied** | Verified the mapping paragraph sits above the 1405 page header, so it is p.1404. 11.3 item 1 cites p.1404. |
| **S16** | sources | minor | Anderson n | **Applied** | Verified: 14 WPW-surgery controls, 8 male and 6 female, 28 +- 10 y (range 18-45); the 0.80 +- 0.08 / 0.23 +- 0.03 m/s values come from the 12 of 14 (86 %) with uniform anisotropic propagation. 5.1 rewritten. |
| **S17** | sources | minor | SE labels | **Applied** | Verified the Wiedmann Table 1 and Table 3 legends and Srinivasan Table 1 give mean +- SE (consistent with the draft's own pooled SD of 2.07: 0.7 x sqrt(10) = 2.2). A21, A7, 2.2 and the fix-1 table now label these +- SE. |
| **S18** | sources | minor | Gami year | **Applied** | Verified the masthead on every page: J Interv Card Electrophysiol (2011) 30:5-15. Cited as Gami 2011 throughout (8.2, 8.6, 8.7, 8.8, A28). |
| **S19** | sources | minor | Lis cusp length | **Applied** | Verified p.2272: 13.8 +- 2.4 / 13.7 +- 2.6 / 13.5 +- 2.4 mm, differences not significant, so the range is 13.5-13.8 mm. Discrepancy 8 rewritten, and I redid the ratios: it reproduces for the right anterior and posterior sinuses but not the left anterior (30.1 % computed against 28.9 % printed). |
| **S20** | sources | minor | Zenodo version record | **Applied** | Verified against the adopted list row 34 and .notes/inputs.md: the stored dataset_info.csv is record 19351401 (31 Mar 2026), the current version of concept DOI 10.5281/zenodo.17048090. Report 12 and 17.3 corrected. |
| **S21** | sources | minor | A2 'Srinivasan 2019' | **Applied** | Verified absent: only Srinivasan 2016 (PMC5142177) is in the file set, inputs.md or the paper reads. A2 now marks it 'not read / unverified' and keeps Boukens 2017 as the source. |
| **S22** | sources | minor | Glukhov M-cells | **Applied** | Verified the quote in the fetched full text ('isolated islands of delayed repolarization (M-cells) in three out of five non-failing human hearts'). R1.3 now names Glukhov a conflicting source and says the model does not adopt that interpretation. |
| **S23** | sources | minor | A11 rounding | **Applied** | Redid the arithmetic: 0.2812 and 0.1995 x 1.194 = 0.3357 and 0.2382; x 0.70 = 0.235 and x 16/22 = 0.173. A11 now carries 0.235 / 0.173 from the unrounded re-projection. |
| **S24** | sources | minor | Toh ostium angles | **Applied** | Verified on the rendered Fig. 3 page: the 56.2 +- 10.0 and 205.3 +- 8.7 deg values appear only in the figure. 8.5 cites Toh 2020 Fig. 3 for both. |
| **S25** | sources | minor | Yamada 2010 ambiguity | **Applied** | Verified the numbers are from J Cardiovasc Electrophysiol 21:170-176 (LCC n = 29, 'MDI of >0.555 was observed in 7 (27%)'), and that a separate Yamada 2010 Circ AE summit paper is in the project. Every use now names the journal, and the gate-3 row quotes '7 (27 %)' as printed. |
| **S26** | sources | minor | Nagel coarse-mesh speed | **Applied** | Verified p.520: 0.15 m/s on a 523 um mesh. 11.4 item 4 now says 0.167 m/s against Nagel's 0.15 m/s. |
| **S27** | sources | minor | Gerstenfeld pacing CL | **Applied** | Verified p.2047: pacing at the tachycardia cycle length, and at 400 ms only when just isolated PVCs were present. Section 10 states it that way. |
| **R1** | rules | blocker | Engine chosen after seeing the gates | **Applied** | The draft did let the verdict engine be picked after every graph-engine verdict had been seen. Fixed as the finding recommends and as the adopted list limits it: gates 1-4, 7, 8 are final on the graph engine at step 8; gates 5 and 6 are computed at step 8 but sealed until T4; T4 is mechanical (10-pair margin, held-out 90 % of 48 pairs, 'can run' = completes without numerical failure); an engine prediction row is added; moving any other gate needs Alex's word and a dated deviation. |
| **R2** | rules | blocker | Retrograde PMJ 4 ms | **Applied (Option B, with the Option A swap-in written and put to Alex)** | Verified Vergara 2016 p.223 (orthodromic 5-15 ms, antidromic 2-3 ms; their model uses 5.0 / 2.0), so 'the 2 ms has no source' was false, and verified the mechanism: under 7.3's own rule every paced beat enters the network retrogradely. 7.3 rewritten with the correct premise and mechanism; gates 1 and 3 made calibration checks; the prediction row set to G1 '+' with G2/G3/G5/G6 '?'; assumption 27 added. I did not switch the primary to 2 ms: Alex adopted 4 ms on 20 Oct and reversing it needs his word, so the one-line swap-in is written and recommended instead. |
| **R3** | rules | blocker | Gate 3 loosened | **Applied** | Verified the locked wording in the v5.1 brief Table A line 252 and the PROGRESS decision log, and verified the value order from v5's labelled .542/.458/.587/.679/.348: the v5.1 values are summit 0.605, vein 0.450, aortic sinus 0.694, RVOT 0.637, LV endo 0.362, so the vein criterion is one of the two that fail. The locked wording is restored verbatim with labels, and 11.2b fixes the v5.2 site families. |
| **R4** | rules | blocker | Gate 5 has no pass band | **Applied** | Verified the approved rule's five sub-checks and CIs, the >= 20-position rule, the 0.05 mV q definition and the 15-of-21 summit/vein dominance. 11.3 now gives the bands, the Cassidy-to-UVC map, eligibility, the deterministic pairing, the fill rule and the q threshold, and the matched-versus-unmatched comparator conflict is flagged for Alex (both fail on v5.1, so nothing is loosened by flagging it). |
| **R5** | rules | blocker | Which chain decides which gate | **Applied** | Verified the 14 Oct convention in the v5.1 brief lines 55-58 and the conflict with the draft's generic constraints. Section 10 now has a per-gate table with the 14 Oct convention as primary and the Kligfield chains as a report column, so no band, noise level or clean-versus-filtered choice is open after the run. |
| **R6** | rules | blocker | New primary site sets unspecified | **Applied** | Added 8.5 item 11b (cusp-site positions), 8.3's placement algorithm, 11.2b (gate-3 families), 11.2a (the ledger, including gate-8 beats at the new sites), the capture rule in 8.7, and step 2e's acceptance. Step 7's acceptance now reads 'equal to the ledger'. |
| **R7** | rules | major | Fix-1 splice can lengthen the QRS | **Applied** | The mechanism checks out: nodes activated in the first 40-65 ms of a paced beat pass +80-100 ms inside the QRS, and the hidden tail already sits at 0.55 of the C1 threshold. R1.2 now enforces voltage continuity at the splice, adds a step-4 template-only check on the gate-1 and gate-3 beats, and the fix-1 prediction row is '?' on G1, G2, G3, G6 and G9. |
| **R8** | rules | major | Gate 9 misreported (duplicate of S3) | **Applied** | Same evidence, same fix; 11.4 and 11.5 now say the additions were adopted after the fail was seen. |
| **R9** | rules | major | Card-2 swap-in drops labels | **Applied** | 8.9 rewritten as three complete blocks; gates 1 and 3 stay calibration checks under every option; every dependent section, arm, assumption, prediction, site set and build step is listed per block; and the option not chosen runs as an arm (A38), symmetrically with card 3. |
| **R10** | rules | major | Calibration register incomplete and conditional | **Applied** | 11.5 rebuilt as one register keyed by change, with unconditional triggers; 8.2's 'if it moves' and the adopted list's 'if it passes' are withdrawn; gate 1, 3 and 5 rows now name every change that prompted or moves them. **[Superseded in part by deviation G, 20 Oct 2026:** the "moves" trigger is withdrawn; labels follow the Targeted rule; see 11.5 and 19.11.] |
| **R11** | rules | major | Clipping rule inconsistent | **Applied** | Radius stated as 1.5 mm (confirmed from the PC's own run note), the stimulated set defined as the connected excitable component without crossing the cut or the fibrous layer, a 4-node capture criterion fixed, and the prediction corrected: 0 for the muscle-clipping clause in the eikonal, '+' where the connectivity clause bites, '?' in the monodomain. The draft's 'slightly earlier and smaller start' is withdrawn as backwards. |
| **R12** | rules | major | Mesh muscle above the pulmonary valve plane | **Applied, with a third rule rather than either of the two offered** | The concern is right: 'kept up to the 8.8-9.05 mm maxima' was an unsourced, heart-specific extent on a failing gate. 8.6 now caps the built height at max(existing, 4.0 mm), trims nothing, and reports the achieved heights, with trimming as arm A30a marked 'moves gate 3'; the aortic side gets the same rule in 8.5 item 9, and step 0 reports the pre-existing extent. I took neither of the finding's two options because one would drop an adopted structure and the other is unsourced mesh surgery. |
| **R13** | rules | major | 6G cut on the sheet ambiguous | **Applied** | Verified the v5.1 cut is complete left intra-Hisian block with the tree intact (0 of 2,965 LV Purkinje nodes reachable). 7.8 now removes only the His-to-sheet edges and keeps the whole sheet, with an acceptance check, and a 6G-cut prediction row (G2, G6 '?') is added. |
| **R14** | rules | major | Fix-4 predictions | **Applied** | Verified that HF transmural speed is unchanged at 0.336 m/s, that the v5 arm-B test cut 6G's RS from 17.6 % to 7.6 % when HF tissue was slowed, and that v5 to v5.1 lengthened both the no-network QRS (220.25 to 230.75 ms) and Durrer T (100.8 to 113.3 ms). G6 and G7 set to '?' with those magnitudes, G5 to '-', and the far-field 'across' row corrected to follow the fibre input. |
| **R15** | rules | major | Outflow predictions lean the wrong way | **Applied** | Verified the J3b result (delaying LV access raised RVOT MDI 0.667 to 0.782) and that gate 1 is scored from detected onset while cusp conduction appears as stimulus-to-QRS latency (Yamada 36 +- 8 ms). The cut's G3 and G1, the crescents' G1, and the sheet's and retrograde delay's G3 are now '?', and 14.2's 'the one real chance of a third' is rewritten. |
| **R16** | rules | major | Missing rows and contradicted zeros | **Applied, with one cell resolved differently** | Verified decision 8 moved gate 4's control value 4.4 to 3.6 % and caused 40-114 ms peak-picking swaps, and that the gate-9 misses were mostly such swaps. Rows added for the T4 engine, the gate-5 map and pairing, the 6G cut, the sleeve rule and the gate-3 site set; fix 2, fix 3 and the pose are no longer '0' on gates 4 and 9. The one divergence: the measurement-chain row stays 0 on gate 9, because under R5 the chain is kept unchanged rather than altered, so it contributes no change. |
| **R17** | rules | major | Gate-1 provenance sources and claim | **Applied** | Verified the 4 Oct anchors (Santangeli 2015 147 / 149; Yamada 2016 169 / 174 / 168; Yamada 2010 summit 175, CI 166-184) and that the band is 147-175 +- 10 %. 11.1 now records the provenance as spontaneous, cites those series instead of Yamada 2007, adds a mixed-or-untraceable branch, and drops 'can only make the gate stricter'. |
| **R18** | rules | major | QRS-end rule as a post-hoc lever | **Applied** | Section 10 now states that no post-result change to the QRS-end rule may alter a v5.2 verdict: forward only, with Alex's word and a dated deviation, reported beside the locked value. 17.3 points at it. |
| **R19** | rules | major | Gate-9 additions against the approved design | **Applied** | Verified approved rule 8 (one-way junction replay) and T2c. The sinus and LBBB beats are now report-only and outside the 108 pairs, the 1D-network clause is dropped, the monodomain's ionic settings are stated, the bias-band fallback is scoped to Aim 2 onset intervals, and R4.4 says propagation uses each engine's tuned sigma while lead fields and the ECG source use the fix-2 sigma_i. |
| **R20** | rules | major | Gate rules restated incompletely | **Applied** | Verified every statistic in the v5.1 brief Table A and the rules draft (gate 2 ratio of means over 10 pairs, 13 Oct; gate 6 median over pairs; gate 7 (d) reported; gate 4 median per pair; approval at 18:27). The section 11 table now copies each rule with its statistic, the gate-1 row says the surface C1 value decides, Durrer (d) is marked not gated, the (a) areas are defined in model coordinates, and the header lists every approval time. |
| **R21** | rules | major | CT pose not executable | **Applied** | 9.1 now gives the translation rule (rotation at identity, LA+RA centroid landing where the v5.1 ICP fit put it, t' = Rc + t - c), a 5 mm skin-clearance acceptance, and an orientation report that never chooses the pose; 9.2 uses v5.1's tagged 4x4 bit-identically and swaps the prediction rows. |
| **R22** | rules | minor | Arms column mixes three questions | **Applied** | Column split into provenance and effect. A11 corrected (against the 0.48 m/s primary it lengthens 6 mm crossing 12.5 to 17.6 ms, which helps gate 1 and gate 6), A26 given gate 4 (latency broke Bazan 2006 on 13 Oct), A28's 'Yes' corrected to 'No', and A24 labelled tuning in both columns. |
| **R23** | rules | minor | Arms not fully fixed | **Applied** | A31's blend stated (linear to the valve plane), A33 made a fixed 12-run set, A34's best-scoring selection made report-only, A37's four shapes named by record order, A27 stated as a radius, the RE+ current named (IKs), and the CL 600 subset fixed at the 9 gate-9 sites after a 10-beat train. A29 and A30 are withdrawn to 17.1, and A35 and A36 are marked 'not run in v5.2' for want of geometry. **[Superseded in part by deviation D9, 20 Oct 2026:** A35 (D9a) and A36 (D9b, a follow-up item) are feasibility-gated in host torsos; see 19.9.] |
| **R24** | rules | minor | HF T-wave polarity | **Applied** | Redid the arithmetic with the scorecard's wall thicknesses: 12.3 / 0.336 = 36.6 ms and 10.6 / 0.336 = 31.5 ms, both far above the 7 ms HF APD gap, so the HF T wave is discordant; the control's 9.9 / 0.48 = 20.6 ms against 28 ms leaves only a 7 ms margin. 14.3 rewritten. |
| **R25** | rules | minor | Reason for gate 7 (a) being a calibration check | **Applied** | Verified v5.1 Table A marks (a) uncalibrated after decision E replaced the Durrer-tuned bundle speeds. The label stays, with the left-bundle sheet given as the reason. |
| **R26** | rules | minor | Steps before the cards are answered | **Applied** | 0.2 and step 1 corrected: only step 0 may run before the answers, because step 1 commits card-dependent predictions and 2c-2f depend on the cards; the finalised file's hash goes into PROGRESS.md before any beat. |
| **B1** | build | blocker | No build step for the septal sheet | **Applied** | Step 2g added, with the sheet's discretisation and metrication check, an explicit PMJ rule (none in the first 10 mm, one per node beyond it), the three outflows' attachment points, the retrograde rule and the 6G cut, plus acceptance checks on width, length, connectivity and the removed edge list. |
| **B2** | build | blocker | New sites but only 579 beats | **Applied** | Ledger added (11.2a) with counts, depths, families and what each set feeds, including no-network beats at the new gate-1 sites, the displaced-site and intramural sets, the gate-9 report beats and the CL 600 subset; step 7's acceptance now checks against the ledger, and steps 8a and 10 carry the extra runs. |
| **B3** | build | blocker | Card-2 swap-in not a one-line edit | **Applied** | Same fix as R9: three complete blocks, one register keyed by change, and every card-dependent row listed. |
| **B4** | build | major | Steps 1-2 depend on the cards | **Applied** | Verified the adopted list's 'no PC brief goes out until all three are answered'. Only step 0 may run first; predictions are committed after both answers. |
| **B5** | build | major | v5.1 gate-9 status and tally (duplicate of S3) | **Applied** | Same fix; the step-0 'resolve against Table A' item is dropped because section 11 settles it. |
| **B6** | build | major | Adopted Prisco row altered (duplicate of S4) | **Applied** | Report 15 rewritten from the main article, 17.2 rows 11 and 12 and the cnm DOI removed, discrepancy 15 rewritten. One correction to the finding: the values are on p.1153 and p.1156, not the p.1154 that the notes and the adopted row give. |
| **B7** | build | major | One chain per gate never assigned (duplicate of R5) | **Applied** | Per-gate table added, 14 Oct convention kept primary, Kligfield chains in a separate report column. |
| **B8** | build | major | MAD equation (duplicate of S1) | **Applied** | Same fix. |
| **B9** | build | major | Gate 3 restated incompletely (duplicate of R3) | **Applied** | Same fix, plus 11.2b for the site families and the sleeve consequence in section 14. |
| **B10** | build | major | Cassidy map not executable | **Applied** | 11.3 items 2-4 add the Cassidy-to-AHA/UVC map with the basal/apical split at z = 0.55, all five regions, the 20-position rule, the per-region count in step 2e and a pre-registered deterministic fill rule so the gate cannot become 'not evaluable' through the new site sets. |
| **B11** | build | major | Mesh ladder cannot run | **Applied** | Verified the memory numbers (WSL 7.7 GB, 375k nodes, 1.05 mm edge, meshtool only) and redid the estimate. 11.4 item 1 is now a local refinement (20 mm sphere, 10 mm transition, meshtool, interpolated fields, lead fields unrefined), 3 seeded sites per heart, 0.1 mm at one site in the control heart, a 6 GB memory stop rule, and 'if affordable' dropped. |
| **B12** | build | major | Niederer units and no fallback (duplicate of S2) | **Applied** | Units fixed and a stop-and-report rule added. One nuance: the gate rule itself does not change, so the benchmark failure is reported beside gate 9 and the next step is Alex's, recorded before the gate-9 values exist. |
| **B13** | build | major | Scoring happens more than once | **Applied via option (a)** | 15.1 now names every scoring point (step 8, sealed 5 and 6, step 10, after T4) and makes the T4 rule binding and mechanical. I did not take option (b), withholding step-8 Table A from Alex: he owns the project and the brief requires reporting, so the control belongs in the pre-registered rule, not in hiding results from him. |
| **B14** | build | major | RE+ ionic settings missing | **Applied** | T1 now names IKs as the scaled repolarising current, states the ionic transmural rule as a per-node interpolation of the endocardial and epicardial parameter sets in w to the R1.4 target map, and step 4 computes the scalings before any RE+ beat. |
| **B15** | build | major | Pose transform (duplicate of R21) | **Applied** | Same fix, with the centroid rule, the 4x4 record, the skin-clearance acceptance and the bit-identical atrial-fit swap-in. |
| **B16** | build | major | Crescent and sleeve builds not implementable | **Applied** | 8.5 item 8b and 8.6 now state the mesh operation (re-tag tag-5 / tag-6 elements, never extrude), what happens where the wall is thinner than the rule, the UVC and w re-solve with fibres re-applied in 2c/2d, the fibrous layer as a 0.40 mm conductivity-and-excitability tag on the luminal face with blood capped there, the heart scope, the sleeve speeds, and a one-element thickness tolerance instead of 0.1 mm. |
| **B17** | build | major | Infundibulum cut under-specified and out of order | **Applied** | 8.2 now fixes the 0 % and 100 % landmarks of Jakiel's posterior wall on the mesh, states the cut as the tag-1/tag-2 interface above 37.3 %, specifies the treatment per engine (split nodes, edges removed at every stencil radius, continuous lead-field conductor), re-checks the cut after 2c and 2d, and adds a connectivity acceptance plus a stop rule. **[Superseded in part by deviation D6, 20 Oct 2026:** the cut now sits 12.7 mm above the 0 % landmark, not at 37.3 % of the span; see 19.6. **D6 is itself superseded by deviation D14, 20 Oct 2026:** the cut sits at 47.2 % of the mesh's posterior span above the 0 % landmark; see 19.15.4.] |
| **B18** | build | major | Summit re-anchor cannot be built (overlaps S12) | **Applied** | 8.3 now carries the full placement algorithm from Toh's LCA ostium (theta 56.2 deg, 14.8 mm) along the AV-groove direction, with surface distances, the Lin base arc, the GCV bisector, the site count and depths, and a report of how far each site moved from v5.1. |
| **B19** | build | major | Provenance assigned to the PC | **Applied** | Verified that the PC session cannot see /mnt/project-files. The trace is done here and recorded in 11.1 with the correct sources and a third branch; step 0 no longer carries it. |
| **B20** | build | major | Monodomain tuning replaced Alex's decision | **Applied** | R4.4 restored to the flat block with straight fibres at every mesh (tuneCV only for starting values), with engine amendment 3 (in-heart achieved speeds at 1 mm, signed bias, 10 % threshold) and an explicit statement that lead fields and the ECG source use the fix-2 sigma_i. |
| **B21** | build | major | Values left to build time | **Applied** | Each one is now a number or a deterministic rule: the LVOT blend band (z 0.80-1.00), the fibrous layer 0.40 mm, the ladder's refined region, the CL 600 subset (9 sites, 10-beat train), A27 as a radius, A33's 12-run set, A37's four shapes by record order, and report 7's tangential direction (along the fibre). |
| **B22** | build | major | No build step for the arms | **Applied** | Step 8a added, with the lead-field recomputation rule, single-process memory handling and per-arm beat scope. A35 and A36 are marked not run in v5.2, because T13 has no lung or muscle geometry and the adopted list names no source mesh. **[Superseded in part by deviation D9, 20 Oct 2026:** A35 (D9a) and A36 (D9b, a follow-up item) are feasibility-gated in host torsos; see 19.9.] |
| **B23** | build | minor | Arms and reports beyond the adopted list | **Applied, except one clause** | A29 and A30 withdrawn to 17.1 with their slots left vacant, the count corrected to 35 adopted arms with the splits enumerated, and reports 17-21, 25 and 26 labelled report-only additions with report 26's beats in the ledger. The clause I did not apply: these reports do not 'need Alex's word', because no standing rule requires it for a report that changes no value and no verdict (0.3), and treating reports as model changes would blur exactly the line the rule draws. |
| **B24** | build | minor | Decision log (duplicate of S13) | **Applied** | Dates corrected and the missing 19 Oct decisions added with their UTC times. |
| **B25** | build | minor | Discrepancy 3 is not real | **Applied** | Redid the arithmetic: 0.90 x 108 = 97.2, so an integer count of at least 97.2 is at least 98 and the two wordings are identical. Discrepancy 3 restated as equivalent and the 'stricter reading' claim withdrawn. |
| **B26** | build | minor | Zenodo record and the direction of the check (overlaps S20) | **Applied** | Report 12 cites record 19351401, and 17.3's check now asks whether that record matches the version the pilot meshes were downloaded from on 2 Oct 2026. |
| **B27** | build | minor | Cross-references | **Applied** | 'Section 6.2' corrected to R5.2; the gate-2 transseptal reference now points at report 13; Macchi moved into report 2 as the source of the 1.5 mm radius; and report 24's fix-5 pairing dropped, since R5.3 keeps the RV fibres bit-identical, with the LVOT leg named as where fix 5 shows. **Correction (20 Oct 2026):** Macchi is not the source of the 1.5 mm radius, which is v5.1's code (PC run note, 16 Oct); Macchi 2004 (rat) gives an excitation latency of about 2-3 ms paced, read from map timings, and no distance (report 2, 17.1). |
| **B28** | build | minor | Ball radius and clipping scope (overlaps R11) | **Applied** | Radius 1.5 mm stated in section 1, 8.7 and 17.1; the stimulated set defined by connectivity; the scope stated as all sites, with v5.1 sites bit-identical where nothing changed. |
| **B29** | build | minor | Checks without stop rules | **Applied** | Stop rules added for the contact area, the angular-frame check, the Niederer slab and the connectivity acceptance, and 15.1 now makes 'stop and report' the default for any acceptance check without a named fallback. |
| **B30** | build | minor | Two mechanisms for the 28 ms target | **Applied** | R1.4 now gives one rule: shape from the blend, duration from a time-stretch to APD90_target(w) = mean + 14 - 28w, with the HF form 1.110 x mean + 3.5 - 7w, and the choice to hold the mean recorded as an assumption. |
| **B31** | build | minor | Sinus beats contradict T2c (overlaps R19) | **Applied** | 11.4 item 5 and T2c now agree: one-way junction replay, the sinus and LBBB beats report-only outside the 108 pairs, and a bidirectionally coupled leg listed in 17.1 as not adopted. |
| **B32** | build | minor | Sobol has no design | **Applied** | Report 8 now specifies six factors with ranges, Saltelli sampling at N = 128, the Jansen estimator with bootstrap intervals, the beat budget and when it runs, and scar is dropped as untestable in v5.2. |

**The one rejection, in full.** *S7 (sources, major): "Pre-register the rule as 'anatomically closest opposite-surface
site within 25 mm (Bazan 2007 p.1404)' and report the achieved mean separation against Bazan's 18 +- 5 mm."* The
finding's factual half is right and is applied: 18 +- 5 mm is the separation Bazan achieved, not his selection rule, and
11.3 item 5 now says so, reports the model's achieved separation against it, and reports Bazan's literal rule as a
second pairing. The core request is rejected, because **Alex adopted "the Cassidy site map plus 18 +- 5 mm matched
pairs" on 20 Oct**, and on a 1 mm mesh "the anatomically closest opposite-surface site" is the transmurally opposite
node about 3 mm away - that is v5.1's pairing. Making Bazan's clinical rule the model's rule would therefore silently
undo the amendment Alex adopted, under the appearance of following the source more closely.

**Partial divergences, recorded so they are not mistaken for silent edits.**
- **R2**: applied as its Option B (keep the adopted 4 ms, correct the premise and the mechanism, label gates 1 and 3
  calibration checks, predict G1 "+"), not as Option A, which would have reversed a value Alex adopted. The Option A
  swap-in is written in 7.3 and recommended.
- **R12**: neither of the two offered rules is taken; 8.6 caps the built sleeve at max(existing, 4.0 mm), trims nothing
  and puts trimming in arm A30a, because trimming is unsourced mesh surgery and "add nothing" would drop an adopted
  structure.
- **R16**: applied except the gate-9 cell for the measurement chain, which stays 0 because the chain is kept unchanged
  (R5) rather than altered.
- **B13**: applied as option (a), a binding pre-registered T4 rule, not as option (b), withholding step-8 results from
  Alex.
- **B23**: applied except the clause that reports 17-21, 25 and 26 need Alex's word; a report changes no value and no
  verdict (0.3), and no standing rule reserves reports to him. They are labelled report-only additions beyond the
  adopted list.
- **B6**: applied with a correction to the finding itself - the Prisco values are on journal p.1153 (text) and p.1156
  (Table 2), not the p.1154 that both the adopted row and .notes/inputs.md give.

**What still needs Alex's word** (only items a standing rule reserves to him; the two open cards are already known):
1. **Retrograde PMJ delay.** He adopted 4 ms on 20 Oct on the stated premise that "the 2 ms has no source". That premise
   is false: Vergara 2016 p.223 gives an antidromic delay of 2-3 ms and an orthodromic delay of 5-15 ms. 4 ms also
   lengthens paced QRS in all 432 paced beats, which moves failing gate 1 toward passing. The lock keeps 4 ms (changing
   an adopted value needs his word), labels gates 1 and 3 calibration checks for it, and holds a one-line swap-in back
   to 2 ms, which is what I recommend.
2. **Gate 5's comparator.** The approved 12 Oct rule text and the 12 Oct scorecard use Bazan's **matched** Table 3 CIs;
   the v5.1 Table A cell and MEMORY call the **unmatched** +74 points the locked comparator. The files conflict, the
   gate is a locked rule, and only he can settle it. Drafted on the approved rule text, with the unmatched comparison
   and its CI reported beside; the model fails both on v5.1, so the choice loosens nothing either way.
3. **The engine for gates other than 5 and 6.** Alex adopted the T4 engine for gates 5 and 6. If the intention was that
   RE+ could carry the whole Aim 1 verdict, that is a change to how every gate is scored and it needs his word and a
   dated deviation **before** Table A is computed on the other engine (15.1, 15.3). As locked, gates 1-4, 7 and 8 are
   final on the graph engine.


## Resolutions after the review (20 Oct 2026)

1. Retrograde PMJ delay: Alex chose "2 ms (v5.1)" at 07:22:39 UTC. Applied in 7.3, 11 (rows 1 and 3), 11.5, 13 (A22),
   14, 16 (item 27), 17 and 18. Dated deviation from the 05:15:17 UTC list.
2. Gate 5 comparator: Alex chose "Matched bands" at 07:23:01 UTC. Section 11 row 5 and 11.3 as written; unmatched
   reported beside.
3. Engine scope: unchanged from the adopted list. T4 decides gates 5 and 6 only; gates 1-4, 7 and 8 are final on the
   graph engine (15.3). Any wider use of the T4 engine needs Alex's word and a dated deviation before Table A is
   computed on it.
4. Lock time written: 20 Oct 2026 07:30 UTC.
5. Re-issue (20 Oct 2026 13:51 UTC): the post-lock review (notes/A/2026-10-19-v52-lock/notadopted-review-2026-10-20.json) led
   to deviations D1-D10 and G, recorded in section 19 and in section 18 rows 60-79, on post-lock cards 1-3 and the four
   follow-up items (0.1).
6. Second re-issue (20 Oct 2026 19:28 UTC): the PC's read-only step 0 on the 13:51 file (README-20261020T170855-4447.md) and
   its follow-up geometry led to deviations D11-D17, recorded in 19.15 and in section 18 rows 80-88, on Alex's "lock"
   (20 Oct 2026 17:11:07 UTC) and the five step-0 cards (0.1). Step 0 is not repeated.
