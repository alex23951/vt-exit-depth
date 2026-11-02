# PC answer: the great-vessel lumen rules (lock thread's question of 2 Nov 2026, read-only)

Question note: notes/A/2026-11-02-v52-lock/pc-question-vessel-ends-2026-11-02.md (2,821 B, sha256 816603eb...7977b, checked).
Written 2 Nov 2026 about 08:20 UTC while the HF chain runs. No beat, ECG or lead-field value exists or was read for this.

## 1. The two rules
- Code: analysis/v52_2026-10-20/05_conductor/conductor52.py at commit 861a760, lumen_faces() l.303-357 (called by
  build() at l.517); comps_space() l.273-300.
- Rule 1 (l.332-346; first written for Y5HYEDL4's build at PC 02:44, committed in aad216d, build() then l.405-427 at
  3a1c71f): the cut end's direction n_cut = mean normal of the wall faces in the top 20 % of the wall's height above the
  disc that face along the vessel (refined 3 times to faces within 25 deg); a plane normal to n_cut placed `back` mm
  (1.0, 1.5, ... 5.0) before the lowest end-facing face; luminal set = edge-connected component of the valve-side faces
  holding the disc face nearest the axis. 861a760 adds one condition to both rules: the set must hold under 20 % of the
  outer boundary and no tag beyond those of the disc-level set plus the wall tags.
- Rule 2 (l.347-357): only where rule 1 finds no sealed set. The highest plane normal to the valve axis, in 0.5 mm
  steps from 1 mm above the disc's upper face, whose valve-side set (pinch edges paired by the empty wedge each face
  bounds) is sealed.
- Used: rule 1 for Y5HYEDL4 aorta and PA and 7D98EVAR aorta; rule 2 for 6G8DD8S5 aorta and PA and 7D98EVAR PA.

## 2. Where rule 1 failed
No R3.2 check was reached: for every back from 1 to 5 mm the valve-side set reached the exterior (>= 20 % of the
outer boundary), so no closed surface could be capped. 6G8DD8S5 aorta (tag 5): n_cut 42.5 deg off the valve axis, end
faces spread 27.8 mm (the ascending aorta curves; the "top 20 %" faces include its outer curvature). 6G8DD8S5 PA
(tag 6): 15.2 deg, spread 7.3 mm. 7D98EVAR PA (tag 6): 32.9 deg, spread 4.3 mm; traced face by face, the luminal
surface runs over the wall's free edge about 6 mm above the disc's mid-plane at one azimuth (the cut end is very
oblique), then down the outer wall to the aorta and the LV epicardium.

## 3. Where the caps lie (neither rule puts the cap on the rim)
- Rule 1 caps lie inside the stub: 1.0 / 2.0 / 1.5 mm (Y5HYEDL4 aorta / PA, 7D98EVAR aorta) before the lowest
  end-facing face; with the end faces spread 1.98 / 4.26 / 8.96 mm along n_cut, the cap is 1.0-3.0 / 2.0-6.3 /
  1.5-10.5 mm from those faces (a proxy for the rim). The lumen volume between cap and rim was not computed.
- Rule 2 caps lie at most 0.5 mm below the lowest point where the lumen opens; elsewhere the wall rises beyond the
  cap by up to 6.7 / 11.5 / 14.5 mm (6G8DD8S5 aorta, cap 35.0 mm above the disc's mid-plane / 6G8DD8S5 PA, 9.6 mm /
  7D98EVAR PA, 4.5 mm). Lumen left out above the cap plane, upper bound (convex hull of the wall beyond the plane minus
  the wall's volume there): 5.0 / 6.6 / 5.1 mL. For 6G8DD8S5's curved aorta any part of the stub that descends again
  below the plane beyond the arch is also left out and is not in that bound.
- Neither rule touches another cap: the valve discs stay the floor of each lumen, the four chambers (valve and vein
  rings) are separate closed components, and sleeve elements are heart tissue, which C7 never turns to blood.

## 4. Blood and R3.2 per heart and vessel (rule 1 gave no closed surface where it failed)
| Heart, vessel | Rule | Blood elements | Blood / enclosed mL | Closed (pinch edges) | +-2 % | Outside (torso in / blood out, mL sampled) | >= 95 % |
|---|---|---|---|---|---|---|---|
| Y5HYEDL4 aorta | 1 | 211,391 | 13.287 / 13.287 | yes (2) | 1.000 | 0.040 / 0.044 | 100 % |
| Y5HYEDL4 PA | 1 | 53,526 | 3.254 / 3.253 | yes (2) | 1.0002 | 0.027 / 0.026 | 100 % |
| 6G8DD8S5 aorta | 2 | 390,761 | 25.254 / 25.254 | yes (1) | 1.000 | 0.068 / 0.069 | 99.98 % |
| 6G8DD8S5 PA | 2 | 101,327 | 6.326 / 6.328 | yes (0) | 0.9997 | 0.061 / 0.056 | 100 % |
| 7D98EVAR aorta / PA | 1 / 2 | its build starts about 09:15 UTC | | | | | |

7D98EVAR's luminal faces from the read-only check: aorta 7,734 (rule 1, 1.5 mm back), PA 2,170 (rule 2). Its R3.2
numbers come with the step-5 report.

## 5. The control heart
Rule 2 is not used in Y5HYEDL4: rule 1 seals both vessels and the 861a760 code reproduces the logged sets (7,645 faces
at 1.0 mm; 3,892 at 2.0 mm; same code path, same inputs). The mesh the lead fields were solved on was not rebuilt
(heart_torso52.elem sha256 6fa3ac7cdb816a8e...), and params/v52_conductivities.json is unchanged (sha256
0675d97846491bc4..., last changed in aad216d). A rebuild to compare blood element ids one by one was not run (about
5 min and 4 GB; it can run after the chain if wanted).

## 6. Confirmation
Rule 2 and the added sealing condition were set from the geometry and the face-connectivity and R3.2 checks only, at
PC 08:4x-09:09 on 2 Nov, before any v5.2 beat or ECG exists. No lead-field value was read.
