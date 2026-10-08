# Final read-only review package

Task root: F:/pnpline-landing/hero-section-video/blockout/blockout-master-s4-fix
Spec: ../plan/pnpline-s4-camera-revision-handoff-v0.1/pnpline-s4-camera-revision-codex-v0.1.md
Plan T1–T5 is in that spec. Progress and all Ruling lines: ../progress.md.
Base and current HEAD: 6079b392d7de54509ed50454ddd2745273cc0078. User forbids commit/push/PR; review working files, not an empty Git commit diff. This version directory was initially only the saved master; all new scripts/evidence here belong to S4. Do not inspect or change unrelated user changes.

Final artifact: ../master-s4-fix.blend; SHA256 d7eebdfe99fa8e37c630e47344b3ab36fd63126ad412f6d18c3ebd78d7ea87e0.
Baseline: ../inputs/base-s4.blend; SHA256 63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976.
User explicitly approved S5 f649–671 camera/target/lens join, exact original return at672; approval-s5-join.json records reply. No S3 change. No asset/event/geometry/timing changes. Final GUI opened for user.

Implemented: local S4 position/aim/lens Hermite camera, reveal f499, prepare f522, lift f532–555, transfer/lower, seat632 and separate637+, final context at648; join to existing S5 within approved interval. S4-only target and fixed-boundary alternatives are retained and clearly labeled as NOT final. Final previews s4-after.mp4 and s3-tail_s4_s5-head.mp4 are from the saved final master.

Review production code: ../scripts/revise_s4.py; validators test_s4.py, s4_metrics.py, camera_math.py, validate_s4.py, reopen_check.py, scene_evidence.py. Existing test_scene.py was copied unchanged from current v005 (24 tests). Test_surface_metrics.py/test_camera_math.py capture measurement defects with RED→GREEN.

Evidence: ../report-s4-camera.md, ../camera-before-after.json, states-final.json/baseline-full.json, reopen-check.json, playback-check.json, ../logs/final-scene-tests.log (24), final-s4-tests.log (8), surface-green.log (2), angle-green.log (2). Baseline corrected RED is s4-red-corrected-metric.log (5 failures); pre-approval join RED is join-red.log (camera f649 jump). Final all36 pass, quarterframe OBB hits0, outside scope/noncamera exact, fresh reopen9 RGBidentical, source replay1393stateexact. Videos 12fps,193/193/253 frames and no dropped frames.

Please inspect actual images, not just numeric boxes: K1-K5-comparison.png, occlusion-review.png, camera-path.png, ../preview final videos via available means, selected final-continuity stills as needed. Original references are in spec folder references/. Known intermediate sweeps (allowed short sweeps under spec): cargo f579–582 and598–606 max38.4% weighted rays, cab f612–625 max40.2%; cargo+receiving bed still readable. At critical lift532 and seat/separate631–648 cab pole0, cargo<=3.28%. Original S5 later than672 has its own pole crossing; preserved by explicit approval limit.

Review focus: actual K2 ship/road/warehouse relationship despite cropped far-right warehouse; continuous K2→K3 and receive-bed tracking; critical contact/spreader gap/cab visibility rather than bounding-box tautology; approved boundary scope and actual exact672 return; quaternion sign interpolation; saved file/source/preview freshness and honest limitations. Identify Critical/Important/Minor by user impact. Do not confuse candidate-target unjoined f649 with final master. Read-only: do not write files, run mutating tests, alter Git or dispatch other agents. Return findings to parent and list every behavior declined to judge with reasons. One review only.
