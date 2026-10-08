# SDD ledger — plan: F:/pnpline-landing/hero-section-video/blockout/plan/pnpline-s2-camera-revision-codex-v0.1.md

## Status
User approved the proposed B23/S3 change ("승인한다"). Approved camera integration is complete and verified; known proxy/board shape differences remain documented.
Required recording was subsequently supplied at C:/Users/KIM TAEHYUNG/Documents/Bandicam/bandicam 2026-10-07 01-22-53-539.mp4 and copied to inputs/recording.mp4.
User confirmed output directory `blockout-master-v004` after being asked whether to base it on saved v003.
`master-v004.blend` now contains the close S2 candidate plus approved S3 join through f251, original camera from f252. Previous limited revision is preserved as limited-v004.blend and previous unjoined candidate remains historical.

## Baseline
- Branch main; HEAD 6079b392d7de54509ed50454ddd2745273cc0078.
- Saved v003 SHA256 ae1a8ea2dfbf8127b27ecd9ad999589575e87aac9eb578c970fd812e7063964e.
- Original GUI Blender PID 57744; title master-v003, no unsaved asterisk observed.
- Saved scene PNPLINE_MASTER_v003; 304 objects; CAM_MASTER; no camera constraints or parent.
- Timeline 0–1392, 12 fps; S2/B12 96, S3/B23 216; lens 40mm.
- Camera ship-local f96 (4.5,-9.8,6.5), f160 (-5,-25,17), f216 (-17,-26,19).
- Five boards reviewed at hero-section-video/storyboard/section-02/s2-01.png through s2-05.png.

## Pre-flight interfaces
- T1 baseline transforms/source provenance feed T2 boundaries and T3 preservation tests: use saved v003 snapshot, not the original v001 generator.
- T2 endpoint feasibility feeds T3 path: boundary/S1/S3 modifications require separate approval per spec section 6.
- T3 output feeds T4/T5: same source, scene hash and render conditions required.

## Rulings
- Ruling: Keep work in the exact version folder requested by the user; do not switch branches, create commits or run the scene-resetting generator — explicit output location and spec preservation/no-commit requirements control — cost if wrong: local output needs relocation.
- Ruling: Store the durable ledger and local validation artifacts in this v004 directory instead of commit-oriented skill helper outputs — user requires all v004 files here and no commits — cost if wrong: manual bookkeeping must be kept current.

## Outstanding input
Initial missing recording was resolved by the user's attachment. B23/S3 f216–251 change was subsequently approved explicitly. No input or approval remains pending for this camera integration.

## Fresh baseline evidence
- Created an exact immutable source copy at inputs/base-v003.blend and initial master-v004.blend; both match the recorded saved v003 SHA256.
- Opened visible Blender PID 61304 on initial master-v004.blend at frame 96. Original v003 GUI remains open.
- Existing v003 behavioral suites test_scene, test_s1_camera, test_framing: 32 tests passed, zero failures/errors, run on the preserved snapshot. Evidence: logs/baseline-tests.log and baseline-tests.json. No old logs were overwritten.
- These are baseline results only; no S2 improvement, recording correspondence, or final acceptance claim is made.

## Execution
- Task 1: complete for saved baseline reproduction. Recording checked at normal speed; start/end geometry visually corresponds to CAM_MASTER but exact recording time-to-frame alignment remains unproven and is not used. Existing 32/32 tests pass.
- Task 2: complete for feasibility investigation. Observations at 96/124/148/180/216. Fixed B23 cannot yield close K5. Separate candidate plus limited alternative produced. Low bridge/short hull/background differences explicitly reported.
- Task 3: complete within authorized ranges. s2-red.log contains three intended failures (K2 crop, K3 height, K5 size); subsequent implementation passed. Stern-crop RED was reproduced then fixed by lowering/shifting target; candidate tests 6/6. Limited changes 98–214; candidate 98–216 only.
- Task 4: complete for current alternatives. Before/limited/candidate S2 121 frames; limited connection 157 frames, all 960x540 at 12fps, actual 1x playback completed with zero generated-video dropped frames. Input recording playback dropped 3 frames; extracted stills supplement review.
- Task 5: complete for provisional comparison delivery, not integrated acceptance. Reopened both .blend files in fresh processes and f96/148/216 RGB matched. Baseline original hash unchanged. Fresh final review completed by gpt-6-astra/high; no Critical/Important issues for provisional approval delivery.
- Ruling: Keep B23 exact in the integrated limited version and put changed B23 only in a labelled S2 candidate — spec section 6 requires approval before changing S3 — cost if wrong: the limited version deliberately fails the desired close K5 composition.
- Ruling: Replace v003's old 'all camera frames >=96 unchanged' revision test with full-timeline preservation outside the newly authorized S2 range — old test conflicts with this explicit camera-change request — cost if wrong: range mistakes must be caught by the new exact all-frame preservation check.
- Ruling: Retain the original CAMERA_PATH object and identify it as obsolete in metadata/report; provide a separate path diagram — preserve all noncamera data and avoid treating a guide as scene geometry — cost if wrong: enabling old overlays can show an outdated guide.
- Limited suite: 24/24 original scene +4/4 S1 +4/4 applicable S2, two candidate-only K5 checks explicitly not applicable; K5 is reported unmet, not accepted through skipped checks.
- Candidate: 6/6 S2 probes; original full-scene suite 23/24 with known test_full_timeline_camera_continuity failure at f217 (19.7293m), reported in logs/suite-candidate.log. This is the reason it remains a proposal.
- Quarter-frame motion: limited max step .483035m/f, max angle 1.25614deg/f; candidate .336570m/f and 1.59048deg/f. OBB collisions zero for both over tested S2; noncamera 1393 frames exact.
- S3 joining feasibility (not applied): endpoint search 218..300, earliest passing this Hermite family's numerical limits f250; recommended f252 with last changed f251. Requires subframe/collision/render validation after approval.
- Tooling finding: system Python lacks numpy/cv2; no install. Comparison helper changed to PIL/standard-library maths. Initial helper failure logs are not scene failures.

## Final independent review rulings
Reviewer independently reopened all three scenes and recomputed every stored frame/static/material state in memory; exact matches. No Critical/Important fix pass required.
- Final: minor (deferred): Candidate saved file does not enable 96–216 preview range. Current GUI enables it through open_review.py; direct future reopening requires manual S2-only playback. Kept deferred per execution skill.
- Final: Ruling: B23/S3 approval and implementation remain pending — explicit user brief section 6 controls — cost if wrong: full integration cannot be accepted yet.
- Final: Ruling: Candidate f217 jump remains an expressly unjoined proposal, not an integrated result — both README and report disclose 19.729m jump — cost if wrong: full-timeline playback of candidate will visibly jump.
- Final: Ruling: Limited K5 remains unmet — exact B23 preservation prevents close ending — cost if wrong: treating limited output as complete would lose the intended ending.
- Final: Ruling: Bridge/hull/port/branding/artwork changes remain outside camera scope — source geometry preserved — cost if wrong: storyboard visual resemblance remains partial.
- Final: Ruling: Other seven-section direction and retiming remain unchanged — preserves user-authored master — cost if wrong: new S2 cannot be optimized by borrowing time elsewhere.
- Final: Ruling: Recording-time/frame equivalence remains unproven — correspondence is visual only — cost if wrong: exact recorded moment cannot be cited as a Blender frame.
- Final: Ruling: Collision and visibility claims stay limited to quarter-frame point-plus-margin OBBs and inspected frames — no exact swept mesh proof — cost if wrong: unsampled/occluded details can remain.
- Final: Ruling: S3 join is only a feasibility result within one Hermite family — actual render, collision and subframe checks wait for authorization — cost if wrong: approved range may need additional iteration.
- Final: Ruling: Numerical framing is supporting evidence only — AC-2 remains partial from visual review — cost if wrong: thresholds alone can miss an aesthetic failure.
- Final: Ruling: Parent normal-speed playback evidence and inspected samples support motion review; independent reviewer did not replay — disclose the review limit — cost if wrong: independent aesthetic motion judgment is absent.
- Final: Ruling: Saved user-edited v003 snapshot is the reproduction source, not the old reset generator — preserves edits — cost if wrong: complete procedural regeneration from v001 is not available.
- Final: Ruling: Parent validates final manifest and oblique plot — produced after review freeze and hashes checked locally — cost if wrong: those artifacts lack independent review.
- Final: Ruling: No production deployment, publishing, commit or PR readiness claim — not requested or performed — cost if wrong: local review package remains unshipped.

## Approved integration continuation
- User approval: "승인한다", following concrete request for B23 f216 and S3 camera/target f217–251, exact baseline restored at f252. Earlier approval-pending statements above are historical and superseded.
- Preserved prior master a394c90d... as limited-v004.blend before replacement. Original base v003 SHA unchanged.
- New regression for exact accepted S2 and join acceleration, plus extended subframe continuity to254: candidate failed 2 tests (join-red.log), then integrated passed all7 S2 tests. Original scene24 and S1 4 also passed:35/35, no skips.
- Changed range98–251; exact approved candidate matrices98–216; camera/target0–97 and252–1392 exact baseline; noncamera1393frames exact; lens/clip/timing/markers unchanged.
- Quarter-frame collision/motion extended95–254: OBB hits0, max step1.608779m/f, max angle1.590481deg/f. Position/target join acceleration under.15m/f². limits unchanged.
- Generated integrated frames84–276 and clips: S2 121frames, connection193frames, 960x540/12fps. Actual1x playback completed, decoded121/193, dropped0/0.
- Fresh-process reopen RGB equal at96/148/216/217/234/251/252. Final master SHA256 0ab8f7a273bc7cc24a0d7ea6de3fdf7965780191625395df5ac7297035adbbca.
- Task3/4/5 completed for approved integration. Prior independent review covered pre-approval alternatives; no second review was dispatched. New approved implementation verified through new RED→GREEN+35-test suite, collision, playback, and reopen checks.
- Ruling: Apply the approved36-frame world-space joining family and preserve f252 onward exactly — matches reviewed user-approved range — cost if wrong: other S3 direction changes would require a new request.
- Ruling: Finish as local files in the user-designated folder with durable ledger; no merge/push/menu or ledger deletion — explicit instruction says no commits and keep v004 files here — cost if wrong: user must handle later Git integration and the audit is file-based.
- Prior deferred Minor remains on the historical candidate only; final integrated master stores preview84–276 as part of its approved-join review UI.
