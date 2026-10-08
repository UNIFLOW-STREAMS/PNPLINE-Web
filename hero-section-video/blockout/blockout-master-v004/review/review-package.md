# Final fresh review package: S2 v004 provisional alternatives

Plan/spec: ../inputs/task-spec.md (original repository plan/pnpline-s2-camera-revision-codex-v0.1.md).
Ledger: ../progress.md (all Ruling lines).
Report: ../report-s2-camera.md.
Baseline commit: main@6079b392d7de54509ed50454ddd2745273cc0078. No commits requested; changes are local, version-isolated, per user instruction.

Review current version directory F:/pnpline-landing/hero-section-video/blockout/blockout-master-v004. Main implementation scripts/revise_s2.py. Tests scripts/test_s2.py, test_scene.py, test_s1_camera.py. Evidence generation scripts/scene_evidence.py, validate_motion.py, propose_join.py. View K1-K5-comparison.png, camera-path-top.png, candidate/f0216.png, play-candidate-4.png.

Two deliverables, intentionally distinct:
- master-v004.blend: limited boundary-preserving camera changes f98..214, improved K2/K3, K5 deliberately unmet because B23 is fixed.
- s2-target-candidate-v004.blend: S2 proposal f98..216; large K5 but known f217 discontinuity (19.729m). User approval requested for f216..251 camera/target joining; NOT integrated. This known discontinuity and AC-2/6 pending are not concealed and must not be graded as an unexpected implementation bug. Assess clarity and safety of deliverable labelling and completeness of disclosure.

Fresh validation:
- baseline original v003 32/32 passes, SHA preserved.
- limited scene24 +S1 4 +S2 4 applicable passes; 2 candidate-only K5 tests marked inapplicable, unmet criterion remains explicit in report.
- candidate S2 6/6; global scene 23/24 fails precisely f217. Logs/suite-candidate.log records it.
- all1393 noncamera evaluated states and static signatures match; camera outside declared range exactly matches, lens and clips unchanged.
- 0.25f S2 point+0.12m OBB collisions zero. Not exact swept mesh.
- all4 generated videos actually played at1x, end reached, dropped0. Supplied recording dropped3; still extraction supplements it.
- fresh-process reopen f96/148/216 RGB matches for both outputs, review/reopen-check.json.

Focus: preservation test validity (including animation and material state), end/boundary honesty, source/output version consistency, unsupported visual claims or acceptance shortcuts, robust scripts, and whether proposed approval scope is adequately concrete. Do not judge proxy model mismatch as silently fixed. Do not modify any files or .blend. Do not implement the pending S3 join. Return Critical/Important/Minor findings with precise file/lines, strengths, overall provisional readiness, and Declined to judge list. One final review only; parent will perform a single RED/GREEN fix pass for real important findings.
