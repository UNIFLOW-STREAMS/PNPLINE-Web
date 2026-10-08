# Fresh-context final review package

Read-only review, no file/index/HEAD edits, no further subagents. Task is camera-only S3 revision in the user's exact v005 file. Base and HEAD both 6079b392d7de54509ed50454ddd2745273cc0078; user forbids commits. All task changes are in this untracked v005 folder; use baseline blend/hash and state diffs rather than empty commit diff.

Spec: ../pnpline-s3-camera-revision-handoff-v0.1/pnpline-s3-camera-revision-codex-v0.1.md
Plan/ledger: ../progress.md, especially Ruling lines.
Implementation: ../scripts/revise_s3.py, test_s3.py, test_scene.py version expectation, scene_evidence.py, s3_metrics.py, validate_s3.py, visibility_s3.py, reopen_check.py.
Baseline: ../inputs/base-v005.blend hash de03eca6e92f7c03ab967a44ed434531e5506536669a8383d69ac1bbf056ad0d.
Result: ../master-v005.blend hash fbd23c09009f925e7d1d082b7a08ded1b302a9fa0915304acb2cbb78f39b09ea.
Read ../report-s3-camera.md for proposed AC judgments and limitations. Final independent review is pending; assess readiness for local user handoff, not merge or production.

Evidence: ../camera-before-after.json, baseline-full.json, states-after.json, reopen-check.json, playback-check.json, visibility.json, targets-before-edit.md, K1-K6-comparison.png, destination-sequence.png, overtake-sequence.png, camera-path.png. Use view_image to visually inspect actual final frames/boards, not just numeric proxies. Preview mp4s and playback screenshot samples are available. Tests: red four behavior failures, green S3 7/7 + existing master 24/24. Reopen 7 RGB outputs equal; source replay all states exact. Quarter samples 1041, no OBB hits. User confirmed current v005 camera is the recording source but manually scrubbed timeline at uneven speed.

Deliberately check: K2/K3 curved world versus merely bending horizon; readable rear/side/deck versus projected bounds; actual 5-second moving tracking interval; destination readability before overtake and crane clipping; same sea-side path; K6 and boundary joins; unsafe overclaim of preservation/replay/visibility/continuous collision; source-preview version consistency; original source or GUI overwrite risks. Do not demand geometry forbidden by the spec, but flag whether claimed AC success is overstated. Required output: strengths, Critical/Important/Minor issues with concrete evidence/file line, Declined to judge list with reasons, readiness verdict. One review only.
