# P15: step-8a beat lists for the 37 arm entries other than A41 (read-only preview)

For the lock thread, from the PC (v5.2 build). No beat ran. Nothing was built or saved for any arm, and nothing went
into the manifest. LOCK.md e8ed1c6 (sha256 08ea65d3...). Records: relock4-build-answers 60f01c99..., relock5-papers
0621a03f.... Hearts are always given in the order Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR.

How this was made:
- Five readers drafted the entries from section 13 and the text each row points to.
- A consistency critic checked them.
- Five independent refuters and a cost estimator then checked every count, quote and cited line against LOCK.md, the
  record and the data files. They recounted the site lists from data/biv/<H>/sites.json, sites52.json and
  gate5fill52.json.
- Every count below survived both checks. Where a check changed a reading, the entry says so.
- The probes were read-only: they loaded graph caches and assembled one matrix, ran no Dijkstra and no beat, and wrote
  nothing into the repo outside this file and its counts JSON.

## 0. Conventions used in every entry

- **Two shared lists.**
  - **E** is every 11.2a ledger beat outside gate 9: 689 / 533 / 527 = 1,749. It is the v5.1 paced 144, His 1,
    cusp_crescent 4, summit_reanchored 8, supravalvar 3, gate-5 fill 66 / 66 / 60, displaced 288 and intramural (at
    most) 19 per heart, plus the control heart's 156 no-network beats (v5.1 144 + no-network-new 12).
  - **N** is the network-carrying part of E, which is A41's list (D34): 533 / 533 / 527 = 1,593.
  - In the HF hearts E and N are the same list.
- **Gate 9 is out of every list.** The 31 gate-9 report beats (sinus-mono 1 / 1 / 1, lbbb-mono 0 / 1 / 0, CL 600
  9 / 9 / 9) are excluded by l.2576-2577 ("Arms ... are not run inside gate 9").
  - The graph-engine beats at the 8 gate-9 sites that are v5.1 paced sites stay in the lists, as in A41's.
  - The gate-9 template site lv_free_wall_original_d0 (nodes 313318 / 19052 / 277582) is not a ledger site, so it has
    no graph-engine beat.
- **Which beats each kind of arm takes.**
  - An arm that changes the muscle, the stimulus, the cell or the forward model also changes the no-network beats. It
    takes **E** (or E cut to its hearts).
  - An arm that changes only the conduction system takes **N**: the no-network beats carry no network and stay the
    primary's, as D34 read for A41.
  - No list is cut by which gate a beat feeds, except where the Scope cell itself names a gate (A15, A28).
- **Site nodes.**
  - Every arm uses the primary's site nodes. Report 26's grids are as placed from the primary's focus beat (D25), and
    report 7's displaced nodes are D33's.
  - Report 7's tangential nodes keep the step taken along the **primary's** fibre, including under A14, A15 and A16,
    which change the fibre. This is a reading; the deviation should state it.
  - A27 keeps the site nodes as ball centres. A32, A33 and A37 move the same mesh nodes rigidly with the heart. A28's
    own crescent sites equal the primary's by construction (see A28).
- **Engine.**
  - All step-8a counts are graph-engine beats.
  - "ECG only" arms re-use the primary's activation and pseudo-Vm and change only the ECG.
  - The RE+ re-run after T4 is a later step, but its list should be fixed in the same deviation (section 4).
- **Lead fields.**
  - The lock's list is A8-A16, A31-A37 and A40 (l.2522). Step 8a (l.2882-2884) restates the rule by its clause alone:
    "any arm that changes sigma, fibres or pose recomputes lead fields".
  - Under R2.2 a speed change is a sigma change; that is why A11-A13 are on the list.
  - **A24, A25 and A30a change sigma but are not on the list.** I propose recomputing them, per the clause: A24 1,
    A25 1, A30a 3. A28 is moot (0, see A28).
  - Total: 188 solves (60 / 65 / 63), against 183 under the list alone.
- **Gate-5 and gate-6 values of every arm** are written to the sealed file beside the primary's until T4 is recorded.
  The lock seals only the primary's (15.1), but opening an arm's gate-5 or gate-6 values first would preview the sealed
  primary. This is a proposed reading.
- **"Not run".** A failed acceptance or reachability check means stop and report (15.1). Then, with Alex's word, the
  arm or heart is recorded "not run" (step 8a). No heart is ever moved, and no value is changed to make a check pass.

## 1. The 37 entries

Format: **Scope** (quoted from section 13) / **Beats** (rows, sites, count per heart) / **Engine and lead fields** /
**Choices** (my pick, why, and the alternative with its count). "Decided" marks a point the draft treated as open
that the lock or record already fixes.

### Repolarisation (A1-A7): ECG only, primary activation, primary lead fields (0 solves)

The arms change only the template after +80 ms (R1.2) or, for A7, the APD map. Decided: reuse lead fields
(l.2522-2524); each beat's own R1.6 window (latest activation + APD90, + 50 ms); the "mean held" build (R1.4,
assumption 29), and for A6 R1.5's form with 29 in place of 7.

**Applies to all of A1-A7.**
- **Choice: arm T-wave ranges and R1.8.** R1.8 requires an RE+ redo if a T-derived quantity becomes "a gate, a report
  metric or a claim". Section 13 reports arms "as ranges beside the primary". My pick: read those ranges as display,
  not as a report metric. The other reading (they count under R1.8) would need an RE+ redo of every A1-A7 beat, at
  ionic settings the lock does not give.
- **Choice: QRS check.** The QRS measures are recomputed only to check "no gate" (the +80-100 ms cross-fade can touch
  a long QRS). A change above 1 ms is reported; nothing is re-scored.

**A1**, S1: 111 ms.
- Scope: "ECG, ledger beats".
- Beats: E in the control heart, 689 / 0 / 0.
- Choice: control heart only. Change-log row 2 makes A1-A3 alternatives to the control 28 ms, and A1's HF side
  already exists as A6 (111 x 29/111 = 29 ms). The alternative, all three hearts, would add 1,060 beats. Once the
  hearts are set, "ledger beats" decides the list.

**A2**, S1a: 0 ms.
- Scope: "ECG".
- Beats: E in the control heart, 689 / 0 / 0.
- Choice: control heart only, as A1 (a real choice; R1.5's derivation would give 0 ms in HF, and there is no HF arm).
  The alternative, all three hearts, would add 1,060 beats.
- Decided: "no gradient" flattens APD only; R1.3's shape blend stays (R1.4, change-log row 41).

**A3**, S1b: 21 ms, epicardium longer.
- Scope: "ECG".
- Beats: E in the control heart, 689 / 0 / 0.
- Choice: control heart only. R1.5 states its derivation for the primary, not for the arms; for A3 it would give
  -5.5 ms in HF. The alternative, all three hearts, would add 1,060 beats.

**A4**, S1c: apex 29 ms longer.
- Scope: "ECG".
- Beats: E, 689 / 533 / 527.
- Choice: all three hearts. The flat apex-base profile has no HF value or HF arm of its own. The alternative,
  control only, gives 689 / 0 / 0.
- Choice: the profile is linear in D19a's converged UVC z, base held at the primary, +29 ms at the apex. This is a
  model assumption.
- Choice: 29 ms as written in every heart, not scaled by 1.110.

**A5**, S1c': base 25 ms longer, as a graded IKs increase.
- Scope: "ECG".
- Beats: E, 689 / 533 / 527.
- Decided: the mechanism is a graded IKs increase (R1.4 l.204-206), not a time-stretch.
- Feasibility: step 4's IKs x1.35 moved ENDO APD90 by only -0.85 ms (271.72 to 270.87). Removing IKs moved APD90 by
  +2.5 ms (ENDO) and +2.9 ms (EPI) (D28). A bench IKs ladder (single cells, about 30 s per steady state; no beat) runs
  first. If 25 ms cannot be reached without afterdepolarisations, stop and report. No time-stretch is substituted (15.1).
- Choice: the APD change is linear in UVC z, 0 at the base and -25 ms at the apex.

**A6**, HF transmural difference 29 ms.
- Scope: "ECG, HF hearts".
- Beats: E in the HF hearts, 0 / 533 / 527.
- Decided: both HF hearts (R1.5 heading). Target 1.110 x mean + 14.5 - 29 w.

**A7**, activation-APD coupling, slope -0.71.
- Scope: "the LV-endocardial basal paced beats, one per heart".
- Beats: 1 / 1 / 1, ECG only. The APD map is rebuilt per beat from that beat's own activation.
- Choice: which site. **I pick lv_free_wall_phi120_z0.75_d10** ("basal anterolateral", nodes 218558 / 87003 / 287357,
  depth achieved 0.079 / 0.115 / 0.096).
  - Why: it has the same site id and the same Bazan region (lv_basal_superior) in all three hearts.
  - The draft's phi180 site (189232 / 290079 / 117301) also has the same id everywhere, but in 7D98EVAR it lies in
    lv_basal_inferior.
  - Septal sites are out: D19b's w runs 0 to 0.5 to 0 across the septum, so "transmurally" would be two-sided.
  - Neither site is at z 0.5, so neither is in gate 9.
  - Whether either matches Srinivasan's LV-endocardial pacing position was not checked.
- Choice: the coupling term. dAPD = -0.71 x (AT - AT at the node's own endocardial reference) is added on top of the
  primary map. The row rules out the global form.
  - Stated consequence: R1.4's 28 ms already comes from Srinivasan's paced ARI differences, so adding on top double
    counts. The control LV-endo-paced beat would reach about 43 ms, against Srinivasan's 25 ms.
  - Alternative: the coupling replaces the paced beat's transmural gradient.
- Choice: one slope, -0.71. The +-0.4 is an SE label, not levels. Running +-1 SE would give 9 beats.

### Conductivity (A8-A10): ECG only, primary activation, new lead fields

**A8**, S2: Clerc's full set.
- Scope: "ECG, ledger beats".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Decided:
  - The no-network beats are in: R2.4 says "every beat in the ledger".
  - The source term is Clerc's sigma_i (R2.4 with R2.3). A40's fix-2 source is A40's own stated exception.
- Reading for the deviation: R2.4's "every beat in the ledger" against section 14's gate-9 exclusion. Gate 9 is
  excluded here.
- **Choice: atrial walls (R3.3; C66 tags 3, 4, 26), one rule for A8, A9 and A11-A14.**
  - My pick: re-derive the walls from R3.3's rule ("at the ventricular cross-fibre bulk"; its numbers are marked
    derived). That gives A8 0.2553; A9 0.1398 (-44 % control, -42 % HF); A11 0.2489 / 0.2425; A12 0.2468 / 0.2416;
    A13 (HF) 0.2478 S/m.
  - Alternative: hold the primary's 0.248 / 0.242.

**A9**, S3: Roberts and Scher.
- Scope: "ECG only".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Decided:
  - The values are used directly (R2.5: "no volume-fraction scaling").
  - S3 is never varied inside the engine test (11.4).
- Walls: by A8's rule. "A9" in reports 24, 5.4, 11.5 and 14.3 is v5.1's isochrone-ratio report, not this arm.
- Choice: the list is E, as for A8 (it shares A8's comparison in 11.3 item 6). The cell names no beats.

**A10**, S4: blood 0.63 and 0.89 S/m.
- Scope: "ECG only".
- Beats: E per level, 1,378 / 1,066 / 1,054.
- Lead fields: 6.
- Decided:
  - Two levels (R3.4, D7); 0.435 and 1.0 S/m are not run.
  - The level applies to all blood (R3.1 gives one blood value).

### Speeds and fibres (A11-A16): activation re-solved, new lead fields

Graph factors for a new speed set: a slab refit and acceptance A (R4.1) run before any arm beat. This is numerics,
not a heart beat.

**Choice for A11-A14: the stencil.** I start each heart on its primary stencil (2-ring control, 3-ring HF). R4.2
literally says to try the 2-ring first and fall back to the 3-ring, so this departs from it and needs Alex's word.
- The literal order may switch an HF heart's stencil inside the arm.
- Acceptance A passes or fails per speed set and stencil, so both HF hearts pass or fail together.
- If both stencils fail, stop and report; the heart or arm is "not run" with Alex's word.

**A11**, Caldwell speeds.
- Scope: "activation and ECG".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3, with sigma_i under R2.2: control cross 0.01292, transmural 0.02744; HF 0.00654 / 0.01236 S/m.
- Decided: control 0.80 / 0.24 / 0.34, HF 0.80 / 0.173 / 0.235 m/s (the cell); network speeds unchanged (R4.5).
- Choice: the list is E, because the tissue change also moves the no-network beats.

**A12**, Glukhov CL-1000 pair, 0.92 / 0.22.
- Scope: "activation and ECG".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Decided:
  - Transmural speed unchanged.
  - R2.2 read literally (ii): fibre sigma_i stays 0.174; cross becomes 0.01076 (control) and 0.00557 (HF) S/m.
    Reading (i), the ratio to 0.92, would be a deviation.
- Choice: HF speeds 0.92 / 0.16 / 0.336, derived as A11's HF values are (x 16/22). No lock text gives A12's HF values.
  The alternative, 0.92 / 0.22 in every heart, mixes in A13.
- Risk: the HF fibre-to-cross ratio 5.75 is the highest any arm needs. The 2-ring already failed at 4.79, and the
  3-ring is untested above it. This is the likeliest stop-and-report in the block.

**A13**, no HF conduction remodelling.
- Scope: "HF hearts".
- Beats: E in the HF hearts, 0 / 533 / 527.
- Lead fields: 2.
- Choice: control speeds 0.80 / 0.23 / 0.48, which removes both of the primary's HF factors. Restoring the transmural
  speed rests on the arm's title; Anderson measured no transmural speed.
- Choice: keep the HF 3-ring and refit at control speeds. The literal R4.2 would use the 2-ring, which passes at these
  speeds. Needs Alex's word.
- Unchanged: 6G's LBBB cut and the HF cell settings. The wall follows A8's rule (0.2478).

**A14**, Lombaert transverse angle 7 / 9 / 34 deg.
- Scope: "activation and ECG".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3, after the refit.
- **Blocked.** No lock or record text gives the mapping of 7 / 9 / 34 deg (transmural levels, regions, or per heart),
  its sign, its rotation axis, the region it applies to, or the refit procedure to Taggart's 12.6 ms. These are one
  question for Alex, with Lombaert 2012's page. Nothing is chosen here.
- The beat list does not depend on the answer, so E can be fixed now.

**A15**, v5.1 fibres.
- Scope: "gate 5 only".
- Beats: L_g5, 100 / 100 / 94 = 294.
  - v5.1 lv_free_wall d10 + d90: 20 per heart.
  - lv_vein_course d10 + d90: 6.
  - summit_reanchored superior and inferior_lateral d10 / d90: 4.
  - Gate-5 fill: 66 / 66 / 60.
  - v5.1 lv_summit d10 + d90, which D23 scores beside: 4.
  - 6G8DD8S5's 10 gate-6 pairs lie inside L_g5.
- Lead fields: 3.
- Decided, largely: the v5.1 stored rows (data/biv/<H>/fibres_v51/bivF_v51.lon; R5.4 "keeps the v5.1 fibres"). The
  primary's rows go on the 0 / 1,004 / 732 sleeve elements, which v5.1 lacks.
- Choice: (b), 294, which reproduces every gate-5 line the primary prints. The verdict pool alone, (a), is
  96 / 96 / 90. A41's list would add 433 per heart that nothing reads.

**A16**, LVOT fibres circumferential.
- Scope: "activation and ECG".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Decided: D20a (same b, alpha_OT = 0 at every depth).
- Choice: the list is E. The fibre change moves the no-network beats too, and D20b found 33 gate-1/3/5/8 stimulus
  nodes per heart with b > 0.

### Conduction system (A17-A22, A19b, A39): activation re-solved, primary lead fields (0 solves)

All of these take **N**, 533 / 533 / 527 = 1,593, at the primary's site nodes. Only the network changes, so the
no-network beats stay the primary's.

**A17 and A18**, LB sheet origin width 1 mm and 14 mm.
- Scope: "activation and ECG" (both).
- Decided:
  - Only the origin width changes (7.1).
  - 6G8DD8S5's cut is 7.8's "edge or edges" from the His to the arm's own origin nodes, with 7.8's acceptance checked
    on the arm's sheet.
  - Reachability is checked before the cut.
- **Choice: is "not run" per heart or for the whole arm?** The lock says "the arm" everywhere (7.1 l.739-741, 7.2,
  assumption 58, l.2471, step 8a). D34's adopted A41 row says "in that heart ... as A17, A18 and A20 are". My pick:
  per heart. A failing heart drops its 533 / 533 / 527; the other hearts run. The deviation must settle the conflict.

**A19**, LV free-wall junctions only from 50-67 % of base-to-apex.
- Scope: "activation and ECG".
- Choice: one level at 50 %. In 13 of 13 hearts Massing's posterior fibres reached the wall only after half to
  two-thirds of the way (p.620), so 50 % is the level the posterior finding supports in every heart. The anterior
  fibres reached the basal third in 2 of 13, which the arm already overrides by extrapolating. Two levels (50 and
  67 %) would give 3,186.
- Choice: UVC z on the converged fields; LV free wall = AHA 1, 4-7, 10-13 and 15-17; PMJs are removed, nodes and
  edges kept.

**A19b**, no LV junctions in AHA 4 and 5.
- Scope: "activation and ECG".
- Decided by 7.7: junctions only; A19's rule is not applied.

**A20**, the RB on the septum only.
- Scope: "activation and ECG".
- Decided: D16 and assumption 58, built against the primary RV network (not A41's).
- Choice: per-heart "not run", as A17.
- 6G8DD8S5 runs: the left cut does not touch the RB, which is its His beat's only antegrade route.

**A21 and A22**, PMJ antegrade 7 ms and retrograde 4 ms.
- Scope: "activation and ECG" (both).
- Decided by 7.3: every PMJ (3,605 / 3,014 / 3,251; LV, RV and sheet) carries the one value; each arm replaces only
  its own direction.
- A22 keeps the His beats. In 6G8DD8S5 the LV network can be entered only retrogradely (7.8), so A22 acts on the His
  beat's LV entry junctions.

**A39**, the 07:30 sheet coupling with v5.1's upper-septal coverage.
- Scope: "activation and ECG".
- All three hearts, 6G8DD8S5's cut sheet included. Report 29 reads the His beats of all three.

### 6G arms (A23-A25): activation re-solved in 6G8DD8S5 only, on N's 6G column (533)

**A23**, LBBB without retrograde entry.
- Scope: "6G".
- Beats: 0 / 533 / 0.
- Lead fields: 0.
- Choice: every LV junction loses its retrograde direction (distal_lv 1,744 + sheet 61 = 1,805). Stated consequence:
  with the 7.8 cut, the LV network is silent in every 6G beat, so report 19 is empty under A23.

**A24**, 6G LV tissue slowed to 0.3 m/s (labelled tuning).
- Scope: "6G".
- Beats: 0 / 533 / 0.
- Lead fields: 1 (proposed; see section 0).
- Choice: the region is the LV side of the model's LV/RV split as built (C2 with D31's moved elements). The
  alternative is the tag groups LV_GROUP [1, 25, 29]; they differ by D31's moved elements.
- Choice: 0.3 m/s as a ceiling on fibre (0.80 -> 0.3) and transmural (0.336 -> 0.3), with cross-fibre 0.167 kept, so
  that no axis speeds up. To be confirmed against Gillette's text, which was not read.
- Decided by R2.2: fibre sigma_i stays 0.174. Only LV transmural sigma_i changes, 0.02673 -> 0.02083 S/m (bulk -2.2 %).
- **Choice for Alex: graph factors.** The refit at A24's speeds gives the LV different factors from the RV, and R4.2
  says "no region factors". I read that as barring factors fitted per region to pass acceptance, not factors tied to
  a speed set. Needs Alex's word.

**A25**, slower transseptal conduction in LBBB with HF.
- Scope: "6G".
- Choice: one level, 0.13 m/s.
  - The arm names "LBBB with HF", and 6G8DD8S5 is an HF heart. 0.30 is Strik's acute-LBBB group without HF, only
    10.7 % below 6G's 0.336.
  - The lock does not settle the level count. The cell's "X and Y" form matches A10 and A27, so two levels
    (0.30 and 0.13) is the alternative: 1,066 beats and 2 solves.
- Beats: 0 / 533 / 0.
- Lead fields: 1 (proposed).
- Choice: replace the transmural speed of septal elements only. Septum = elements nearer both the LV and the RV
  endocardium than the epicardium (both halves). Written into the manifest before any beat.
- Graph factors: as A24.

### Focus and outflow (A26-A28, A30a)

**A26**, depth-dependent latency, 17 + 17w ms.
- Scope: "all paced beats".
- Beats: E minus the His beats, 688 / 532 / 526 = 1,746, no-network beats included.
- Engine: an exact time shift. ECG_arm(t) = ECG_primary(t - L), padded with the rest value, with the window lengthened
  by L. No activation or Vm is recomputed. Lead fields: 0.
- Decided: w = D19b's w_APD at the site node (R1.3 is the lock's only w; D19b). Fibre w would put about 34 ms on
  every RV-side site.
- Note: the Moves cell names gates 1, 2, 4 and 6. A detected-onset reading would add gate 5 and spare gates 1, 3 and 8.
  The cell stays the stated prediction.

**A27**, finite focal source, 5 and 10 mm.
- Scope: "cusp, summit and coronary-vein sites".
- Beats per radius: 136 / 96 / 96; both radii 272 / 192 / 192 = 656.
  - Sites: cusp_crescent 4 + v5.1 aortic_cusp 8 (cusp); summit_reanchored 8 + v5.1 lv_summit 8 (summit);
    lv_vein_course 12 (vein, all depths).
  - Plus their displaced copies (56).
  - Plus, in the control heart, the 40 no-network beats at those sites.
- Lead fields: 0.
- Decided: 8.7's clipping (same connected excitable set inside the ball, no crossing of the cut or the fibrous layer;
  the ball is never grown to compensate).
- Choice: include the displaced copies and the no-network beats, because the stimulus changes for them too. The
  literal minimum is 40 / 40 / 40 per radius.
- Choice: all vein-course depths. The 90 % sites only would remove 36 / 27 / 27 per radius.
- Choice: no supravalvar sites (pulmonary).

**A28**, Gami's smaller aortic crescents.
- Scope: "the gate-1 and gate-3 beats of the ledger".
- Beats: 60 / 0 / 0. Decided: gates 1 and 3 are control-heart gates.
  - Gate 1: crescent 4 + re-anchored summit 8, plus the v5.1 cusp 8 and summit 8 scored beside.
  - Gate 3 adds vein 90 % 3, RVOT 8, LV endo 10 % 18 and the supravalvar 3.
  - The verdict-setting sets alone come to 41.
- Finding: A28 re-tags 0 elements in every heart by construction.
  - Its lunes lie pointwise inside the primary's, under the same 2.4 mm cap, and the primary re-tagged none.
  - Even without the cap, no 5-deg bin reaches Gami's lune; the closest is 7D98EVAR's RCC at 0.19 mm.
- So 0 new beats and 0 solves: build A28, confirm the tag, fibre and site hashes equal the primary's, and report the
  60 as the primary's ("identical by construction"). If any hash differs, the 60 beats run with 1 control solve.

**A30a**, trim all mesh muscle above 4.0 mm over the cusp nadir.
- Scope: "RVOT and supravalvar beats".
- Beats: 35 / 27 / 27 = 89.
  - rvot 8 + supravalvar 3 + rvot displaced 16 per heart.
  - Plus the control heart's 8 no-network rvot beats.
- Lead fields: 3 (proposed).
- Trim size: RV muscle (tags 2, 28) above +4.0 mm is 4,477 / 1,295 / 1,279 elements, 484 / 134 / 136 mm3
  (0.21 / 0.06 / 0.06 %).
- Choice: re-tag the trimmed elements to pulmonary wall (0.2 S/m; non-excitable) and keep the primary's fields on the
  rest. That changes sigma, hence 3 solves. The alternative, trimming excitability only, keeps their conductivity and
  needs 0 solves.
- Every supravalvar node (1.7-3.2 mm above the mid-plane) survives, and no RV PMJ is trimmed.
- The intramural set is out: its focus is 12.8-16.9 mm below the mid-plane.
- Limitation stated: the His and other beats whose late activation reaches the trimmed conus are not in scope.

### Forward model (A31-A34, A37, A40): ECG only, primary activation, new lead fields

**A31**, epicardial fat 0.0377 S/m.
- Scope: "ECG only".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Decided: one Abbara column per heart by donor age. 17.3 gives 25 / 64 / 65, so all three take the <= 65 column.
- Choice: the central value only, with the bounds recorded. The lock does not say whether the bounds run; three
  levels would be 9 solves and 5,247 ECGs.
- **Blocker before any A31 beat:** the <= 65 column's thicknesses and the RVOT and summit valve-plane fat values
  (Jakiel 2025, Kuniewicz 2023) are in neither the lock nor the repo. They must be read from the papers and recorded by
  dated note with Alex's word. If a source gives no value, stop and report.

**A32**, the heart pose not chosen.
- Scope: "ECG only".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3, plus 3 heart-torso meshes at the v5.1 pose, with tensors rotated with the heart.
- Decided: 9.1's acceptance runs at the v5.1 pose (9.2). Simulation-mesh clearance is 30.8 / 34.2 / 42.1 mm; the full
  cohort mesh is still to be checked. A failure means stop and report; the heart is never moved.

**A33**, respiration.
- Scope: "ECG only".
- Beats: E x 20 runs, 13,780 / 10,660 / 10,540 = 34,980.
- Lead fields: 60, plus 60 meshes.
- Decided: the McLeish runs are in addition to the 12 fixed runs. 9.4 (ii) ties the 12 to the +-10 deg / +-10 mm set,
  and "both signs are run" rules out 4 McLeish runs.
- Choice: 8 McLeish runs (2 modes x half-vector either way x both overall rotation signs). The alternative is 12,
  with tidal's two rotation signs flipped independently: 72 solves.
- Choice: rotations about axes parallel to T13's, through the ventricular centroid. The worst node moves 16.7 / 18.0 /
  17.0 mm, against primary clearances of at least 29.2 / 36.6 / 39.2 mm.

**A34**, electrode misplacement bank.
- Scope: "ECG only".
- Beats: E x 25 configurations, 17,225 / 13,325 / 13,175 = 43,725.
- Lead fields: 75 as listed.
  - Only the moved electrodes' jobs are needed. 15_conductor.py splits I-III / V1-V3 / V4-V6, so this is about 45
    full-solve equivalents.
- Decided: the 25 configurations (Wenger V1+V2 5, V4-V6 3, Anter +-1 ICS 2, limb 2, Doste 13); V4-V6 move together;
  the Anter pair is V1 and V2, with V3 recomputed; the best-scoring choice is among Doste's 13 and is report-only.
- **Open, before any beat:** the contents of Doste's 13 configurations, and the LL and RL positions under "all four"
  (T13 has no legs). Both set values, so they need a dated deviation.
- Report: the displacement actually achieved after snapping to the skin, per configuration (snap error up to about
  5 mm).

**A37**, KIT torso shapes T_24, T_20, T_17, T_01.
- Scope: "ECG only".
- Beats: E per heart-shape pair, 1,378 / 2,132 / 2,108 = 5,618 (10 pairs).
- Lead fields: 10, plus 10 meshes.
- Choice: keep each heart's CT-pose coordinates (the shapes share T13's frame; centroids within about 6 mm), with
  9.1's acceptance, and use each shape's own electrode file snapped to its skin.
- **Finding:** Y5HYEDL4 fails in T_24 (nodes outside the skin) and T_17 (1.4 mm clearance).
  - Every other pair passes, at 9.3-55.8 mm.
  - Re-placing by the electrode map would rescue only T_24 (5.1 mm).
  - So stop and report; with Alex's word those 2 pairs are "not run".
  - If all 12 pairs ran: 6,996 ECGs and 12 solves.

**A40**, Hooks bulk set.
- Scope: "ECG only".
- Beats: E, 689 / 533 / 527.
- Lead fields: 3.
- Values: sigma_b 0.70 fibre / 0.35 transmural / 0.16 cross-fibre. Implied sigma_e (fibre / cross / transmural):
  control 0.526 / 0.148 / 0.288, HF 0.526 / 0.154 / 0.323 S/m. Asserted positive at build, else stop and report.

### Where one list serves several entries

- **E** (1,749) serves A4, A5, A8, A9, A10 (each level), A11, A12, A14, A16, A31, A32, A33 (each run), A34 (each
  configuration), A37 (each pair) and A40. Its control part (689) serves A1-A3; its HF part (533 / 527) serves A6
  and A13.
- **N** (1,593) serves A17, A18, A19, A19b, A20, A21, A22 and A39, as it serves A41. Its 6G column (533) serves
  A23-A25.
- **Own lists:** A7 (3), A15 (294), A26 (1,746 = E minus His), A27 (656), A28 (60), A30a (89).

## 2. Totals beside the ledger's 1,780

| | Y5HYEDL4 | 6G8DD8S5 | 7D98EVAR | All |
|---|---|---|---|---|
| Primary ledger (11.2a) | 699 | 544 | 537 | 1,780 |
| Arm activation re-solves (graph engine), 37 entries | 7,427 | 8,847 | 7,164 | 23,438 |
| plus A41 (D34, two levels) | 1,066 | 1,066 | 1,054 | 3,186 |
| Arm ECG-only recomputes (primary activation) | 40,652 | 31,448 | 31,094 | 103,194 |
| A26 time-shifted ECGs | 688 | 532 | 526 | 1,746 |
| A28 (reported identical, not re-run) | 60 | 0 | 0 | 60 |
| **All arm beat-ECGs, 37 entries** | **48,827** | **40,827** | **38,784** | **128,438** |
| Lead-field solves | 60 | 65 | 63 | 188 |

- Of the 128,438, the forward-model and conductivity arms re-use one primary pseudo-Vm per beat projected onto many
  lead-field sets: 96,566 ECGs (A8, A9, A10, A31, A32, A33, A34, A37, A40).
- A33 and A34 alone are 78,705.
- Under the draft's alternatives the totals move as follows:
  - A25 two levels: +533 beats, +1 solve.
  - A1-A3 in all three hearts: +3,180.
  - A19 two levels: +1,593.
  - A31 three levels: +3,498 ECGs, +6 solves.
  - A33 twelve McLeish runs: +6,996 ECGs, +12 solves.
  - A34 changed-electrode jobs only: about -30 solve-equivalents.
  - Reuse instead of recompute for A24, A25 and A30a: -5 solves.

## 3. Expected step-8a run time and peak memory

All figures come from measured v5.1 runs (LABNOTES) scaled to v5.2, plus read-only probes run today. No v5.2 beat or
lead field has run, so the first beat (the D25 focus beat) and step 5's first lead field will replace these estimates.

**Graph beats** (26,624 with A41).
- Measured: v5.1's network beat took 4.6 s in one process (about 2 s graph, 2.6-3 s ECG), at 1.35 GB peak.
- v5.2's R1.6 window (-100 ms to latest activation + APD90 + 50 ms) is about 556-665 samples against v5.1's mean of
  194, so the ECG costs about 3.3x as much.
- The 3-ring graphs have 2.5-2.9x the edges. heart52 currently rebuilds the coupled matrix on every beat, which takes
  3.5 / 10.7 / 11.7 s.
- Estimate per beat: about 11.5 s (Y5HYEDL4) and about 15 s (HF) with v5.1's plain template. R1.2's splice template is
  not written yet; a naive version costs up to 4x the ECG.
- Wall time: about 57-78 h at the plain template; about 200 h with a naive splice. This assumes the control heart at
  4 processes and the HF hearts at 2 (memory below).

**ECG-only recomputes.**
- Measured: about 3.3 s per ECG at v5.1's window (decision 8's 579 ECGs), so about 9-12 s at v5.2's window.
- Sharing one pseudo-Vm per beat across all lead-field sets (projecting 56 sets took about 4.6 s) brings the 96,566
  forward-model ECGs to about 7 h CPU, instead of about 270 h done one by one.
- A1-A7 need their own Vm: about 18 h CPU at the plain template.
- Together about 10 h wall at 4 light processes (about 38 h with a naive splice).

**Lead fields.**
- Measured v5.1: 6.3-8.2 min per set at 5.8-6.5 GB of 7.9 GB, with 2 MPI processes.
- 188 sets come to about 19-26 h. They must run alone: nothing else fits beside them.
- Single-process solves (the section 13 rule) are untimed and may be slower.
- Full-torso lead-field runs still wait on Alex's yes (asked after the 10 Oct out-of-memory crash; step 5 needs it
  first for the primary).

**Remeshing** for A32, A33 and A37: 73 heart-torso meshes.
- Measured: 9 Oct's re-pose pipeline took 26 min, and "remesh ~26 min each" for other shapes. The draft's "4 min" was
  a pre-run guess.
- Estimate: about 7-32 h. Each mesh is about 2 GB, so about 150 GB on disk if all are kept (900 GB free; deleting
  them needs Alex).

**Total step 8a: about 95-150 h of continuous PC time (4-6 days), and up to about 300 h (12 days)** with a naive splice
ECG, slow meshing and 8-minute solves.
- Today's PC measured about 1.7x slower than the 19 Oct runs. If that persists: about 6.5-10 days, up to about
  20 days.
- Three engineering levers change no value and cut most of this: build the 3-ring matrix once per process instead of
  once per beat; share the pseudo-Vm across lead-field sets; treat A26 as an exact shift.

**Peak memory.**
- About 6.2-7.0 GB of WSL's 7.9 GB during lead-field solves, which run alone.
- Graph beats:
  - The control heart's 2-ring beat measured 1.19 GB, inside 15.1's 1.35 GB.
  - **The HF 3-ring beat measured 2.71 GB (6G8DD8S5) and 2.36 GB (7D98EVAR) at set-up plus one matrix assembly, about
    twice 15.1's per-process figure.**
  - Two HF processes take about 5.1-5.4 GB, which equals 15.1's 4 x 1.35 GB total; three do not fit.
  - This also applies to the primary's step-8 HF beats, not only to the arms. Reading for Alex: 15.1's budget is the
    5.4 GB total, so HF beats run at 2 processes.
- Disk: about 38 GB of activation maps for about 27,000 beats.

## 4. The RE+ re-run after T4 (not step 8a, but its list should be fixed now)

- **Where the lock places it.** 15.1 says that after T4 "the section 12 reports and the arms are re-run on the chosen
  engine where the engine matters, with both engines' values printed". No numbered step in 15.2 runs it. The deviation
  should place it after T4 and before step 12.
- **Why fix it now.** Choosing its arms, beats or window after T4 would come after step 8a's graph-engine arm results.
- **What "where the engine matters" covers.** T4 decides gates 5 and 6 only (15.3), so I read it as each arm's gate-5
  and gate-6 values. Those come from L_g5 (100 / 100 / 94), and gate 6's 20 beats in 6G lie inside it.
  - The ECG-only arms project the RE+ primary's L_g5 Vm and need no new RE+ beat.
  - A26 is a shift.
  - A1-A7 are out: no gate, and RE+ ionic settings for them are not given.
- **The fork: which activation arms re-run on RE+.**
  - Reading A: every activation arm on its L_g5 part. About 4,500 RE+ beats, about 5,090 with A41.
  - Reading B: only arms whose cells name gate 5 or 6 (A11-A15, A19b, A24, A25, A39). About 1,020 beats.
  - My pick on principle is A, because B picks arms by the gates they move.
- **Cost, stated for the record.** T4(iii) says PC time is not a constraint (Alex, 19 Oct 18:37), so this is not a stop.
  RE+ is untimed (T0b times it).
  - The lock's own 15.3 estimate is 16-20 s per simulated ms. Measured RE- was 17 s/ms and monodomain 14 s/ms.
  - v5.2's window is about 460-480 ms, so about 2-3 h per beat.
  - Reading B would take about 77-165 days of PC time; reading A about 0.9-1.7 years.
  - **T4(iii) itself requires every ledger beat to complete on RE+.** For v5.2's 1,780 beats that is about 150-220 days
    at 2-3 h per beat. 15.3's "weeks to about 2 months for the ledger" matches RE-'s 40 min per beat on 3 Oct (window
    not recorded), not its own "up to about 3 h" (inference).
  - A QRS-only window would roughly halve these figures.
  - This is a finding for the engine test, not a P15 choice. 15.3 already says "Aim 2 would need the bigger computer";
    on these figures the engine test may too.

## 5. What the deviation needs Alex's word on (picks in brackets)

1. The two shared lists and the per-arm assignment in section 1 (E for muscle, cell and forward arms; N for network
   arms; the own lists).
2. A1-A3 heart scope (control only); A4/A5 (all three hearts).
3. The arm T-wave ranges against R1.8 (display, not a report metric).
4. A7's site (phi120) and its coupling term (added on top, with the double count stated).
5. The atrial walls under the sigma and speed arms (re-derive by R3.3's rule).
6. The A11-A13 stencils (each heart's primary stencil, not R4.2's 2-ring-first); the A24/A25 region factors (reading as
   stated); A12's HF speeds (0.92 / 0.16 / 0.336).
7. A14's mapping, sign, axis, region and refit, with Lombaert's page. A14 cannot be built until this is answered.
8. A15 (294); A19's level (50 %); A17 / A18 / A20 "not run" per heart.
9. A24's region and axes; A25's level count (one level, 0.13).
10. A27's list (with displaced copies and no-network beats; all vein depths).
11. A30a's trim (re-tag to wall).
12. Lead fields for A24, A25 and A30a (recompute, 5 solves).
13. A31's bounds (central only) and its missing source values; A33's McLeish count (8) and pivot; A34's Doste set and
    LL/RL positions; A37's two failing Y5HYEDL4 pairs.
14. Sealing every arm's gate-5/6 values until T4.
15. The RE+ re-run's place, list and reading (A), with the cost finding above.
16. The memory reading: HF 3-ring beats at about 2.4-2.7 GB per process, 2 processes.
