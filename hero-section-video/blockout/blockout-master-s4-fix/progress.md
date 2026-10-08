# SDD ledger — plan: ../plan/pnpline-s4-camera-revision-handoff-v0.1/pnpline-s4-camera-revision-codex-v0.1.md

FOLLOW-UP: The user rejected f502 as excessively distant. The prior visual acceptance below is historical and superseded by progress-close-reveal.md and the regenerated report-s4-camera.md. Latest correction is camera/target/lens f458..521 atop the user's latest saved input, with f522+ unchanged.

FINAL STATUS: T1–T5 complete; independent review's one Important issue fixed by RED→GREEN; full suite37/37passed. User designated master-s4-fix.blend and its version folder. Original preserved as inputs/base-s4.blend. Main HEAD 6079b392d7de54509ed50454ddd2745273cc0078; existing unrelated changes in v001/v003/v004/v005 and plan folders remain untouched. No repo AGENTS found. No Blender GUI initially running this task. Historical steps below are retained in chronological order; final checksum is in the last entry.

Pre-flight: T1 actual B34/B45, current event states and S2/S3 preservation feed T2. T2 must test ship+road+warehouse, preparation and K5 departure direction before routing; fixed B45 may conflict with K5, in which case do not force a last-frame restoration or edit S5 without approval. T3 requires behavioral RED before production patch; T4/T5 must use the final version and fresh previews.

Ruling: Work in the exact user-designated folder/current branch with preserved baseline and retained local evidence, no commits/cleanup — user's specified source and no-commit/preservation requirements override skill worktree/commit/cleanup defaults — cost if wrong: Git integration and evidence cleanup remain manual.

Hypothesis to investigate: the current wide reveal plus lens widening loses the ship, then a landward camera aimed seaward crosses foreground crane columns and loses road/warehouse direction. Determine this from actual camera output, not recording timing.

T1 evidence: baseline SHA256 63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976; 14/14 input hashes verified; 24/24 legacy tests passed freshly; user confirms 19-35-47 recording is same camera state and slider scrubbing. Baseline actual fps12, B34=456/B45=648; noncamera 302 objects preserved. Current S2/S3 matches previously delivered evaluation through f456 exactly. Blender GUI opened for review.

T2: rendered position/look candidates at 40mm before testing 32–38mm. Weighted surface rays supplement renders, not visual acceptance. North-facing final camera cannot show warehouse behind it but may keep exit road and ship; original B45 shows no exit road and a foreground leg overlaps the cab. Target-only S4 and fixed-B45 limited candidates will be separate; no S5 edit before approval.

T3 RED: scripts/test_s4.py against preserved baseline: 3 pass, 5 fail (whole-ship framing, K3 preparation, K4 vehicle cropping, contact visibility, K5 exit context). Failures are behavioral assertions, not loading/syntax errors; logs/s4-red.log. Auxiliary criteria frozen before production: K2 ship >=24% width and 1% margin, destination visible overlap >=18%; cargo/vehicle full bounds during transfer, critical cab/cargo <=15% weighted crane occlusion; actual image/playback still required. Cargo weighted visibility includes internal faces and is only a conservative sample measure.

Ruling: Use task-specific progress.md and scripts/logs as the T1–T5 ledger rather than skill shell task-start/task-done wrappers — supplied Blender brief has no wrapper-format Interfaces/Expected blocks and Windows uses PowerShell; commands and observed outcomes remain explicit — cost if wrong: no automatic wrapper completion tracking.

T3 candidate GREEN: target S4 camera tests 8/8; exact evaluated noncamera and outside-S4 states retained. Internal cargo walls were incorrectly counted as external occluders; independent panel-assembly regression failed first, corrected grouped surface-ray semantics passed 2/2. Re-ran original with corrected metric: still 5/8 fail. No acceptance thresholds changed. Angle validator raw quaternion difference mistook q/-q as a 360-degree change; independent regression RED records this representation bug before shortest-orientation fix.

T4 candidates: rendered before/target/limited f456–648 at 960x540 12fps, each 193 frames. Installed Chrome no-seek 1x playback completed all three with 0 dropped frames. Goal candidate quarter-frame OBB hits=0; actual shortest max rotation ~5.53 deg/frame, max translation 1.593m/frame. f532–648 cargo/tractor/trailer crops=0; f631–648 cab weighted crane occlusion=0, cargo <=3.28%. Candidate target f648→649 still discontinuous by design because S5 is unapproved; existing scene tests were run to expose that failure, not suppressed.

Approval requested: S5 f649–671 camera/aim/lens join, return exactly at f672, no object/event changes. Concrete candidate-target.blend, candidate-limited.blend, before/target/limited videos, b45-proposal.png and report-s4-camera.md supplied. Visible candidate-target Blender window PID18040 alongside original master PID81876. Until reply, no S5 keys or designated master overwrite.

User APPROVED: “승인: S5 초반 접합까지 수정”. Stored scope in review/approval-s5-join.json. Integrated Hermite offset only f649–671, returning to unchanged original keys at672. Existing scene continuity RED at f649 (15.727m jump) → 24/24 GREEN after join; S4 8/8 GREEN with user-approved exact outside range. Quaternion metric regression 2/2 GREEN. Master now saved with external-change hash guard; backup retained. Original/candidate GUI windows were clean and closed gracefully; final master reopened visibly in PID67276.

T4 final: all1393 state diff changes camera/target only458–671 (214 frames), lens213 frames in that range, noncamera0; outside approved scope exactly preserved. Quarter-frame checks452–684: OBB hits0, maxtranslation1.593m/frame, maxshortestrotation5.531deg/frame. Contact f631–648 cabin crane occlusion0; cargo<=3.28%. Permitted transient sweeps remain: cargo f579–582 and598–606 (max38.4%), cab f612–625 (max40.2%); renders f602/f618 confirm load/receiving bed remain readable, no total disappearance. Contact and separation occur after these sweeps. After f672 the original S5 includes a passing crane pole over the moving cargo; unchanged by approved scope.

T1–T5 implemented and verified, pending final independent review. Final tests:24+8+2+2=36pass. Fresh reopened master9representative renders RGBexact, replay of final source from baselineall1393evaluationstatesexact, baselinehashpreserved. Final before/after/connection normal12fps decode193/193/253frames, zero dropped. Final masterSHA256 d7eebdfe99fa8e37c630e47344b3ab36fd63126ad412f6d18c3ebd78d7ea87e0. Report/board comparisons/path/occlusion views generated from final data. No remaining approval pending.

Final independent review: gpt-6-astra/high, fresh context, read-only. Critical0, Important1 (entry roll), Minor0. Reviewer independently checked images, state/replay equality, file hash, and11 MP4 decoded samples. Accepted remaining K2–K5/framing/scope evidence. Full review recorded in review/final-review.md.

Final: fixed abrupt S4 entry roll — test_entry_has_no_single_frame_roll_spike RED at4.838deg/frame-to-frame angular-speed change → inherited6.015deg roll and derivative released smoothly f457–480 → GREEN; whole suite37/37 (24+9+2+2). f457→458 now~0.79deg rather than5.53, whole sampled interval max2.944deg/frame. Refreshed master, final renders/videos, validation and reopen/source evidence; no second reviewer per skill's one-fix-pass rule.

Final: Ruling: Do not evaluate or recreate storyboard vessel proportions, port details, signs, or full warehouse interiors — camera-only scope and fixed geometry explicitly exclude them — cost if wrong: visual likeness to the storyboard remains limited by existing proxies.

Final: Ruling: Preserve original S5 framing fromf672 and unrelated S1–S3/S6–S7 artistic choices — only equality/regression belongs to this revision and approval explicitly ends at671 — cost if wrong: existing artistic issues outside this range remain.

Final: Ruling: Retain historical target-only and fixed-boundary candidates with explicit non-final labels — required to show approval alternatives, while README identifies the final master/video — cost if wrong: a reader may open a historical candidate instead of the final file.

Final: Ruling: Accept finite quarter-frame point+0.12m OBB evidence without claiming mathematical continuous collision freedom — actual path checks and rendered views meet the stated verification method, not a continuous geometry proof — cost if wrong: an unsampled thin contact could be missed.

Final: Ruling: Treat independent still/decoded-sample review and recorded1x playback as technical evidence, not an independent uninterrupted aesthetic viewing — reviewer disclosed this limit; motion data and actual sequence samples support technical acceptance — cost if wrong: subjective pacing or cinematic preference may still require the user's visual judgment.

Final: minor (deferred): none.

Post-fix T5 complete:13 newly reopened RGBstills identical (including457/458/459/470), source replay all1393states exact, baseline preserved. Final masterSHA256 08bb7e28e96148a48274b685d7fd1dabe675fe9aeb0047f2d374aba735a7fb52. Final1xafter/connection decode193/253with0displaydrops; before193with1displaydrop during this rerun, ffprobe confirms193fileframes intact. Final master visibly open in PID65460. All required ACs technically met; finite collision/aesthetic limits disclosed. Keeping main and all task evidence in place per user spec; no merge/push/commit or cleanup requested.
