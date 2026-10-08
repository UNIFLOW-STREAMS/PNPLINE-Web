# SDD ledger — plan: F:/pnpline-landing/hero-section-video/blockout/plan/pnpline-stage2-s5-integration-codex-handoff-v01.md

User confirmed current DA742469… base as selected stage1 result for integration on2026-10-08.
HEAD main@af33d386b82f3620a02d6e7c4ce102e7a50fe0df. Initial status: only untracked handoff markdown. No applicable AGENTS.md found.
Base: s4-s5-boundary-v001/master-s4-s5-boundary-v001.blend SHA256 da742469879948266a948b8534c44ed3ae3e3d85e281c521342c34f2c3470c6d.
Donor candidate: s5-dock-test-v001/master-with-s5-test-v001.blend SHA256 5b2565b642c7f646d8e08386ddcd6c4039df6755eb7bcc90dadf0e81d8115b16. Compare actual action to saved a9c280… blend1 before selecting donor version.

Ruling: Isolate outputs in the expressly proposed new s5-integration-v001 folder of the user-designated checkout, without a worktree/branch change — the handoff says worktrees only when necessary and needs local-only .blend inputs — cost if wrong: untracked outputs require manual management.
Ruling: Use this folder/progress.md as the plan ledger and retain it with reproduction evidence; omit commit-based skill wrappers and branch finishing — the handoff prohibits commits, pushes and PRs — cost if wrong: history lives in artifact evidence rather than Git commits.

Preflight T0→T1: live file hashes differ from past reports, user confirmed current base. Donor semantic difference under inspection.
Preflight T1→T2: base world/quaternion vs donor local/Euler; evaluated state conversion required; f720 base has nonzero speed vs donor648 standstill.
Preflight T2→T3: terminal dock position may match but camera and proxy geometry differ; door/bridge collision and timing gates need measured evidence.
Preflight T3→T4/T5: single-camera master and all rendered candidates must be generated from identical saved-file hash.

T0 in progress. T1–T5 pending. Source files must remain read-only. No geometry/retiming scope approval inferred.
T0 complete: selected base existing 24 master + 5 strict wheel tests pass. Current donor and recorded blend1 have identical actions, geometry and evaluated sample states; only saved non-evaluated observation camera location differs. Select current 5b2565... donor.
User approved exactly two hinge local X translations -1.60 to -1.65, globally in integration copy; leaf dimensions, wheels, bridge remain base geometry. Before door overlap0.04m; in-memory hinge-only proposal sampled overlap0.
T1 contract: F_lock720, F_rejoin948. Preserve original12fps, aligned810, doors811–842, reverse849–890, inbound900, end1392. No time shift.
Ruling: Reparameterize donor spatial path from the already moving base f720 instead of replaying donor stationary f648 — preserves protected road travel and original S6 timing — cost if wrong: compressed approach may require retiming approval after motion review.
Ruling: Recalculate rolling phase and local Z after f720 and retain the resulting parked phase during S6/S7 — rolling distance changes with selected route; resetting phase would visibly snap wheels — cost if wrong: parked wheel orientation differs from prior master, although body/cargo/choreography remain identical.
Model: current session exact model ID/reasoning setting is not exposed to available tools; no model switch claimed. Tool catalog offers gpt-6-astra/high for the one final fresh review.
T1 RED: saved base tests reproduced15.13deg heading mismatch and0.040m closed-door penetration. Central donor ellipse test already passed (the old route used same ellipse), so endpoint/ellipse identity alone is not acceptance.
T2 initial integration fixes doors and tangent; all24 master +5 wheel tests passed. Tiny0.0001m braking displacements made 1/8f heading differences float32-noisy; use1f geometric chord, sampled1/4f, same2deg threshold. It passes0.327deg while original15deg failure remains meaningful.
User approved additional minimal dock repair: bridge width1.48→1.34, centerZ1.82→1.88; both door leaves lower edge raised0.07m, upper edge unchanged (height1.43, center+.035). Readonly proposal zero forbidden door/bridge/chassis overlaps; originals preserved.
T2 second RED: collision scan identified door/warehouse floor0.05m and bridge/body0.05m; motion audit identified entry turn8.15deg/f and numeric stop steering180deg. Reduce entry acceleration slightly while preserving initial speed and events; derive rolling/steering in double-precision local trajectory to avoid float32 world cancellation.
Task T1: complete. Evaluated donor logic/world conversion max1.92e-5; source-map and monotone time-map generated. New5 tests observed RED then GREEN.
Task T2: complete. Selected spatial path with corrected hitch tangent and payload. 24 master +5 wheel +5 integration tests pass on final cf4d9f...; wheel support max0.000100315m at original strict sampling. Full SAT1,650,704 pairs pass; max forbidden7.63e-6m; bridge-floor designated overlap0.07999m.
Task T3: complete. Camera bounds f720–899 and pallet point/ray visibility912–948 pass; lens monotone29→40; no cuts. Original camera position/rotation/lens and evaluation preserved from948. Endpoint evaluated orientation blend preserves inherited angular motion.
Task T4: complete. Reopen regression34/34, all304 world matrices/lens across5569 quarter-frame samples match independent recreation; original protection max0. Source base603523.../donor5b256... hashes unchanged since captured inputs. GUI final file opened separately PID55712. Browser real1x playbackapproximately27.1s for27.083s videos, both ended/errornull; FFmpeg decode0.
Task T5: complete. Six actual same-version frames672/720/766/810/842/900, manifest; before/after boundary stills719/720/721/947/948/949; diagnostic path and contact closeups. User final storyboard choice not performed.
Final review pending: exactly one fresh-context gpt-6-astra/high review of folder and handoff; no implementer agents used.
Final review complete: gpt-6-astra/high fresh read-only review, no Critical/Important. Independently checked protected raw keys/handles/interpolation and artifact/source hashes. No further reviewer dispatched.
Final: minor (deferred): Pin sibling kinematics.py/config.json hashes for future regeneration; current equivalence/reproduction passes.
Final: minor (deferred): Add render-time provenance records and enforce them in packaging; current outputs have consistent hashes/logs/timestamps and viewed imagery.
Final: Ruling: Leave artistic pacing/composition and final storyboard choice for user continuous review — handoff defines provisional integration only — cost if wrong: further camera/shot revision may be requested.
Final: Ruling: Do not claim real vehicle/facility safety or repair the disclosed6cm original floor difference — blockout and approved minimal geometry scope — cost if wrong: detailed modeling may need a later dock interface revision.
Final: Ruling: Accept documented sampled collision/visibility evidence without claiming continuous-time/full-frustum proof — evidence matches declared sampling and strict original contact tolerances — cost if wrong: unsampled narrow interference may remain.
Final: Ruling: Preserve S6/S7 choreography and timings instead of judging a new production treatment — explicitly excluded from scope — cost if wrong: inherited choreography issues need separate work.
Final: Ruling: Use author's actual browser1x playback and decoder evidence with reviewer's representative-frame inspection — reviewer did not independently replay full videos — cost if wrong: less independent visual-motion coverage than a second playback.
Final: Ruling: Do not commit/merge/push — expressly prohibited — cost if wrong: delivery remains local and uncommitted.
Final: accepted technical candidate; pending user continuous-preview preference review. Deliver exact report verdict after final artifact check.
T0 hash reconciliation: current base and initial copied working file are603523d6... (saved18:31); approved DA742469... survives in base.blend1. Readonly surveys show identical keys, shapes, hierarchy, markers and all evaluated samples; only unevaluated current-frame properties differ. Use user-approved current saved state603523d6..., and verify this actual hash thereafter. Earlier ledger hash was stale.
