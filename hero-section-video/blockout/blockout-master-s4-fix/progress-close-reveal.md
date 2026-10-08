# S4 f502 foreground-scale correction — 2026-10-07

FINAL STATUS: T1–T5 complete. Corrected master saved/opened; 41 tests passed; independent review accepted with no findings; 17 reopened RGB pairs and source replay1393 states exact; all1421 package hashes verified. No commit/push/deployment. The final hash inventory is refreshed again after this ledger edit.

Plan: original S4 T1–T5, reopened after user rejected f502 as excessively distant.
Target: master-s4-fix.blend. Current backup: inputs/before-close-reveal.blend.
Baseline SHA256: 85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de.

Previous AC-2/overall visual acceptance is withdrawn. The 24%-width gate failed to detect an undersized subject. The user screenshot is f502, consistent with the saved camera. Latest user save has no camera, target, lens, non-camera evaluated/static/material/event differences from the prior delivered state at 1393 frames.

Pre-flight: new local camera patch consumes the latest saved file and must preserve the existing f522+ camera, S5 join, entry roll, and every non-camera state. New visual-scale tests supplement, never replace, all previous preservation/visibility tests.

Ruling: Keep work and evidence in the user-designated version folder without a new worktree, commit, or cleanup — the explicit file workflow and retained review evidence take precedence over generic skill wrappers — the cost is manual version tracking.

T1: backup and full-state capture complete; excessive f499 retreat (18,-38,28) plus 32mm confirmed. Disposable trials do not save scene changes.
T2: foreground framing trial4-b chosen: f499 camera (0,-30,14), target (6,6,2), 35mm. The previous pose was (18,-38,28), target (12,12,2), 32mm. The ship remains a foreground subject, with the quay/road/destination behind it. This still was connected back to the original f522 pose before validation.
T3: test_close_reveal.py RED: f494 ship width 29.80% <42%. First candidate passed size but failed f509 left margin (1.284% <1.5%). Root cause: inland target tangent overshoot on approach. Setting its reveal x-tangent to zero passes 4/4 without changing gates. Camera/target/lens only f458..521. Master saved via hash-guarded source; visible Blender process 69520 opened at f502.
T4: 41/41 freshly passed on saved master: 24 original, 9 S4, 4 close-reveal, 2 surface metric, 2 quaternion metric. Quarter-frame f452..684 (929 samples): OBB hits0, max1.1995m/frame, max3.1533deg/frame. Full 12fps videos rendered/encoded. Chrome no-seek 1x playback completed, before193/after193/connection253 decoded with zero display drops. Actual sample sheet and f502/board/approach comparisons inspected. Ship remains the foreground subject through the reveal; dock preparation approaches continuously without returning to the distant map view.
T5: reopen17 RGB exact, source replay1393 full states/metadata exact, both input hashes intact. Current master SHA256 2ba73fc3baca6b3617ac534349d0d794c2dc744b48e50ccc66b685f07572e2ff. First full-suite invocation supplied a duplicated output prefix to test_close_reveal and failed before its tests; preserved test-invocation-error.log, corrected the invocation, all tests passed. Fresh gpt-6-astra/high read-only final review accepts the correction, Critical0/Important0/Minor0. No second review or fix pass required. Final report/hash packaging complete; all1421 inventory entries checked and current master hash matches reopening evidence.

Final: Ruling: Exact ship proportions, scenery detail and rendering-style equivalence remain outside the camera-only correction — the user receives the corrected foreground scale with existing assets and the broadside/partial-warehouse difference disclosed — cost if wrong: remaining board likeness may need a separately authorized asset change.
Final: Ruling: Keep f522 onward unchanged and do not reapprove its artistic direction as part of this local correction — preservation was verified and the reported defect concerns early S4 distance — cost if wrong: existing later crane sweeps or framing preferences may need a separate revision.
Final: Ruling: Retain finite quarter-frame OBB and visibility evidence without claiming continuous mathematical proof — this supports the bounded approach check honestly — cost if wrong: a thin contact between samples could remain undetected.
Final: Ruling: Accept the independent review's rendered/playback samples and runtime records without claiming a second perceptual real-time viewing — no new defect appeared and completed1x playback plus sampled frames support this handoff — cost if wrong: subtle pacing preferences may require user playback judgment.
Final: Ruling: Leave unrelated changes, historical candidates, deployment and detailed asset improvements outside this correction — the requested master and evidence are delivered without unrelated edits — cost if wrong: older artifacts or unrelated defects remain the user's separate work.

Deferred minors: none.
