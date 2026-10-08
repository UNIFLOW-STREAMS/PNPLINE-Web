# Fresh independent review and executor disposition

Reviewer: gpt-6-astra / high, fresh context, read-only, no subagents.
Reviewed master SHA: d7eebdfe99fa8e37c630e47344b3ab36fd63126ad412f6d18c3ebd78d7ea87e0.
Pre-fix verdict: With fixes. Critical: none. Important: one. Minor: none.

## Important: S4 entry roll

revise_s4.py immediately used US_FRAME up on the first edited frame f458. Physical rotation was0.936deg (456→457),5.532deg (457→458),0.693deg (458→459), with only0.783deg viewing-direction change in the large step. Actual f457/f458 images showed the sudden horizon roll. Quaternion hemisphere normalization was correct but did not resolve this physical roll change. Reviewer requested preserving inherited roll and smoothly releasing it inside S4, with angular-speed-change regression and refreshed deliverables.

Executor agrees this is Important under AC-7. The single RED→GREEN fix pass is complete. No re-review was dispatched.

New test `test_entry_has_no_single_frame_roll_spike` failed first at4.838deg angular-speed change, then passed after inheriting entry roll+velocity and releasing it overf457–480. Final suite37/37passed (24legacy+9S4+2surface+2quaternion). f457→458 now~0.79deg; whole quarter-sampled range maximum2.944deg/frame. Final camera/target changes remainf458–671 with exact original672+, noncamera unchanged.

Final master SHA: 08bb7e28e96148a48274b685d7fd1dabe675fe9aeb0047f2d374aba735a7fb52. Refreshed final renders/videos and source replay;13 fresh reopened RGBrenders identical and all1393 replay states exact. Final after/connection1x playback decoded193/253frames with0displaydrops. Before decoded193with1displaydrop in this rerun; ffprobe file frames intact. The pre-fix review conclusion is not represented as a second review of the fixed file; covering tests and refreshed evidence close the Important issue.

Executor final disposition: technical acceptance; Critical0, unresolved Important0, deferred Minor0.

## Other findings

Actual K2/K3 views, cargo/receive-bed tracking, critical seat/separation, K5 ship/exit direction, permitted transient crane sweeps, approved scope, exact672 return and state equality were accepted. Reviewer independently compared static/noncamera/outside-scope and replay JSON, final hash, and11 video samples decoded in memory against final PNGs (RGB MAE1.2–1.8/255, normal encoding loss). Recorded tests36passed and reopened9RGB identical before this fix.

## Declined to judge

1. Storyboard-level vessel proportions, detailed port assets, signs and warehouse completeness: outside camera-only blockout scope.
2. Original S5 framing after672 and unrelated S1–S3/S6–S7 artistic quality: only preservation/regression equality assessed.
3. Historical unjoined and limited candidates as final deliverables: labeled alternatives, not final master.
4. Mathematical continuous collision freedom: finite quarter-frame OBB evidence cannot establish it.
5. Full real-time aesthetic playback: reviewer inspected sequences, numeric continuity, decoded samples and playback logs, not an uninterrupted real-time presentation.

Executor dispositions and costs are recorded as Final: Ruling lines in progress.md and carried to the final user handoff.
