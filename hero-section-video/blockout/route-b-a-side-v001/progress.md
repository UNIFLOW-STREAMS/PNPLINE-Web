# Plan: inputs/task-spec.md

T1 started: source frozen; hash differs from delivery record. Inspect before changing.
Ruling: use separate immutable-input artifact directory per supplied workflow, preserving existing checkout and GUI; no branch switch or automatic commit. Path isolation, not a Git worktree.
Preflight: T1 baseline feeds T2 route and T3 regional transfer; T4 metrics must use same source and frame range; T5 evidence tied to final hash.

T1 complete: frozen current disk source hash 79990474…; original integration 8/8; object/action signatures equal the v032 integration baseline. Recorded delivery hash differs, not treated as proof of changed geometry. Existing GUI was not saved or closed.
T1 evidence: actual departure f146, landing f510; actual visible bow +ship X, A lies on negative original CN X. No constraints/drivers found. Recorded video inspected at 10s; its time was not mapped to timeline frames.
T2 complete: A-side route test RED on baseline -> GREEN on B. Broad seaward turn then spherical voyage, original timing retained. B v001 camera join failed (4.315m / 8.375deg step); blending to evaluated moving arrival states produced v002 GREEN. Superseded v001 retained as failed evidence.
T3 complete: fixed US rigid transfer with explicit regional root list; shared ship/cargo/camera separately baked. Local normalized US root samples at all integer frames and quarter-frame joins pass; protected child action signatures and all mesh geometry preserved.
Scope approval: user explicitly approved a separate city-rotation alternative, including port/S1 connection review. It does not authorize adopting or replacing the master.
City alternative: CN_FRAME rotated 180deg about original CN origin; existing ship voyage/cargo/US retained; crane shifted 2m in new layout Y and retargeted. v001 rotated S1 close camera; ray tests did NOT fail (files named *red were exploratory, not RED evidence). A separate original-S1-camera preservation test did fail on v001; v002 preserves f0..72 and passes. Camera changes f73..339.
T4 quantitative findings: city rotation reduces transition camera rotation 226.6 -> 63.6deg; B -> 92.5deg. B relative camera azimuth travel and ship turn speed worsen. Both candidates retain hull/shore or hull/US overlap; no acceptance claimed.
Ruling: finish these as explicitly unadopted failed/conditional proposals instead of changing protected coast geometry or the US internal layout — task explicitly allows a negative recommendation; cost if wrong is another iteration before a usable master.
T4 video: current and B all 577 integer frames f96..672 completed at 12fps. City v002 full f0..672 render underway; discarded partial city-v001 sequence retained and excluded from comparison.
T5 underway: fresh process reopen, exact-source reproduction to review/reproduced-b.blend and review/reproduced-city.blend; structural/evaluated comparisons and representative re-render underway.

T4 complete: all three f96..672 12fps videos decoded successfully; CUA browser playback reached end, rate 1 and no media errors. Additional city S1 f0..156 video included. Quantitative and static visual evidence supports conditional city-rotation preference, not complete AC acceptance.
T5 complete: separate reproduction for both candidates objects/actions/mesh geometry exact, all-frame major-object evaluation error 0; 8/8 representative render pixel comparisons exact. Source disk hash unchanged. Tracked working-tree changes none; only this new task folder untracked. No commit/push/master replacement.
Final: read-only independent review by route_proposal_final_review returned Critical 0 / Important 0 / Minor 2. No second review requested.
Final: minor (deferred): NPZ region samples lack embedded candidate hash; current run traced by fresh process and matching metrics/render hash, future automation should enforce the binding.
Final: minor (deferred): protected object Action/slot assignment is not independently compared; Action datablock signatures are compared. Report wording narrowed to actual verification scope.
Final UI: old master Blender window has unsaved indicator; left untouched. Separate candidate-city-rotation-v002 Blender window verified. Comparison tab http://127.0.0.1:18776/review.html marked deliverable.
