# Read-only final review: S4 f502 foreground-scale correction

User request: The revised S4 camera pulls much farther away than storyboard S4-01..05; screenshot is f502. We must correct the excessive distant shot, not merely explain the board caption. This is a continuation of the authorized S4 camera task. User explicitly approved S5 f649..671 previously; this follow-up preserves f522+ exactly.

Authority: ../../../../plan/pnpline-s4-camera-revision-handoff-v0.1/pnpline-s4-camera-revision-codex-v0.1.md (use absolute path from dispatch). Current ledger: ../../progress-close-reveal.md. Follow its single Ruling line. Previous S4 completion was visually rejected and must not be treated as evidence for this revision.

Review range is an uncommitted artifact delta, not Git commits. Current repository HEAD remains 6079b392d7de54509ed50454ddd2745273cc0078. Do not review unrelated repository changes or alter Git state. Before: inputs/before-close-reveal.blend SHA85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de. After master SHA2ba73fc3baca6b3617ac534349d0d794c2dc744b48e50ccc66b685f07572e2ff.

Implemented: new scripts/revise_close_reveal.py changes only f458..521 camera/target/lens, preserving latest saved input and prior entry-roll release. f499 (18,-38,28), target(12,12,2),32mm becomes (0,-30,14),target(6,6,2),35mm in US frame. It joins existing camera and velocity at f522. No geometry/material/event changes.

Review focus (check deliberately):
- Does actual f502 and the reveal sequence visibly keep the ship foreground, versus only passing loose bounding-box tests? Inspect supplied boards, f502-before-after.png, approach-sequence.png, real-time-playback-samples.png, review/K1-K5-comparison.png; inspect individual full-resolution frames if needed.
- Does reducing distance create crop, subject loss, crane occlusion, sudden roll/heading, or a large reverse reframe before docking? Fixed proxy shape and layout are constraints, not excuses for an avoidable distant camera.
- Check exact preservation f0..457 and f522..1392 including the approved S5 join, all object states/events. Source hash guard must preserve latest user save.
- Check stale report/source instructions and whether claimed evidence corresponds to current master. Historical inputs/candidates explicitly retained. Main report has a pending-review note until this review is integrated.
- Treat finite numerical collision/occlusion checks and runtime playback honestly; neither proves pixel visibility or artistic equivalence by itself.

New tests scripts/test_close_reveal.py: RED f494 width29.8%<42; first candidate had crop-margin failure f509; target tangent fixed, GREEN4/4. All previous tests retained and freshly passed (24+9+4+2+2=41). Logs review/close-reveal/final-test_*.log. Validation-final.json: 929 quarter frames, OBB0, speed1.1995/angle3.1533; states-final.json plus before-states.json/correction-diff.json. Reopen-check.json:17 RGB identical; source replay1393 state/metadata exact; all four video formats verified. Playback-check.json:before193/after193/connection253 decoded,1x,no seeking,zero display drops. Report and README regenerated.

No new modifications or tests needed unless a credible gap is found; if running anything, remain read-only and do not invoke scripts that save or overwrite evidence. Use returned assessment rather than writing a report. Never dispatch subagents. Return strengths, Critical/Important/Minor findings with specific references, every behavior declined to judge with reason, and acceptance of THIS follow-up. Do not request commits/merge/deploy.
