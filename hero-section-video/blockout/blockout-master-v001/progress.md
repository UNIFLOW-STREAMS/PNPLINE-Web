# SDD ledger — plan: F:/pnpline-landing/hero-section-video/blockout/plan/master-codex-instructions.md

7구간 연출안 검증용 / 기존 #61 승인안 대체 아님.

## M0
- N0~N7 Notion full bodies fetched and read. All eight returned isError=false; no truncation or unknown block flags returned. Native page verification is unverified.
- Asset inventory v0.1 read. Existing storyboard PNGs S1~S5 discovered, but version and selected status are absent. Text-based candidate / board comparison not performed.
- Baseline: main@8e3d5700b671a2b0e0b6af0daa42bf3644ba8c43. Existing untracked hero-section-video/ must be preserved. No applicable nonempty AGENTS.md found (global file empty).
- Blender 5.1.0 (adfe2921d5f3) executable exists. ffmpeg 7.1 exists. No project-wide automated test command found.
- Default command and Node runtimes failed before process start: sandbox setup refresh errors. Read-only escalated commands work; use approved local execution without changing global settings.
- Git ownership warning resolved per command with -c safe.directory=F:/pnpline-landing; no global Git setting changed.
- Ruling: use a new dedicated local output directory in the requested checkout; retain main and HEAD, without commits, branch switching or worktree creation. The supplied brief explicitly requires preserving the selected checkout and local deliverables. Cost if wrong: artifacts require manual Git inclusion later.
- Ruling: adapt skill ledger/task helpers to this M0–M4 artifact plan, which lacks Task N/Expected/commit blocks; retain logs and ledger because there will be no commits. Cost if wrong: skill Bash automation is not the record; evidence must remain in this folder.
- Ruling: inspect provided PNG existence only until version/selection metadata is supplied; text is the binding composition input. Cost if wrong: visual board matching remains unverified.

## Pre-flight interfaces
| Producer → consumer | Contract |
|---|---|
| M0 → M1 | Eight complete sources; asset IDs; working save/render runtime |
| M1 → M2 | Fixed world; entire camera; same ship/container/vehicle |
| M2 → M3 | Curvature/contact; dock axes; articulation/doors; collision margins |
| M3 → M4 | One evaluated timeline; export evidence from reopened blend |

M1–M4 pending. Do not claim acceptance before fresh checks and playback review.

## M0 complete / M1–M2 evidence
- `smoke.py`: Blender 5.1 saved/reopened-compatible smoke.blend and rendered PNG; viewed actual cube image. ffmpeg available.
- Eight scene contract tests written first; factory-default scene failed all eight as expected (`logs/tests-red.log`). No implementation existed then.
- First whole-world candidate: 294 editable objects, 1392 frames, one camera. All source JSON snapshots persisted.
- Reopen without factory settings loaded installed third-party addons and emitted background GPU registration errors. Cause: user startup addons. Subsequent commands use `--factory-startup` before the explicit blend; no user preferences were modified.
- Quaternion rotation metric initially reported a 358.85-degree turn because q and -q are equivalent; corrected metric to the shortest physical rotation (2 acos(abs(dot))). This was a measurement defect, not an animation fix or relaxed tolerance.
- Regression RED: road was a 2.5-unit cylindrical bevel that buried tires, rear door faced away from camera at f900, ship position jumped 6.09 units at f217 due to overlapping departure formulas. Fixed the underlying road geometry, camera position, and single ship interpolation path. 11/11 tests then passed (`tests-02.log`).
- Ruling: radius 180 → 140 test units, S3 camera offset increased to reveal a visibly round limb while keeping the rigid ship readable. Exact sphere keel checks remain unchanged. Cost if wrong: terrace proportions may need another layout trial; no operational scale implied.
- M2 visual inspection showed S4 destination and final S7 vehicles cropped. Added final-vehicle projection regression; it failed with primary normalized x=1.21. Expanded the S4 and S7 camera arcs without moving terrain or vehicles.
- Detail animation remains explicitly deferred by timeline markers. New inbound cargo stays separate from rack and outbound cargo.

## Current stage
M3 candidate generated; M4 all-frame collision/state extraction, continuous playback, final review and reproducibility pending.

## M3 and final correction pass
- One fresh-context gpt-6-astra/high reviewer inspected the whole candidate under executing-plans. Its findings and declined-to-judge list are in `review/independent-review.md`. No second reviewer or shared scene writer was used.
- Final: fixed outbound cart floor loss and loader overlap — `test_outbound_cart_stays_on_warehouse_floor` RED→GREEN.
- Final: fixed unsupported last box and occupied cargo slot — `test_last_load_has_support_and_clear_cargo_slot` RED→GREEN.
- Final: fixed van/building collision — `test_delivery_vehicle_envelopes_clear_destination_buildings` RED→GREEN.
- Final: fixed unsupported picking product — `test_picking_bin_product_has_support` RED→GREEN.
- Final: fixed crane cable tops without trolley support — `test_crane_cables_have_overhead_trolley_support` RED→GREEN.
- Final: fixed secondary van yaw/merge mismatch — `test_secondary_heading_matches_merge_motion` RED→GREEN. Six failures reproduced together in `logs/review-findings-red.log`; corrected suite 18/18.
- Manifest lens range corrected to evaluated 32–40 mm. It was a reporting error, not a fixed-40-mm scene.
- Folded doors/side panel penetration and rear chassis/dock overlap reproduced in `logs/dock-clearances-red.log`; corrected geometry, suite 20/20.
- Actual 1x browser playback completed 116 seconds, 1392 decoded frames, 0 dropped. Visual sample inspection found two additional issues: auxiliary catches primary and overlaps, and container roof crops during unloading. Both reproduced in `logs/playback-findings-red.log`; fixed delay 1231→1261, transfer camera positions; suite 22/22.
- Final brief comparison found reverse distance 17.4 test units too long for “short reverse.” `test_dock_reverse_is_short_after_doors_open` failed first (`logs/short-reverse-red.log`). Arc-length sampled half ellipse (radii 6/10) now aligns at x29.2; 5.2-unit reverse reaches x34.4. Warehouse/port positions unchanged. Added raised-floor envelope regression. Whole suite 24/24.
- A combined still-render/animation command initially retained the last still filepath. Stopped only that owned background renderer, removed only matching erroneous generated PNGs from this output directory, and separated render processes. Final complete frame sequence replaced the earlier sequence.

## Final rulings on review exclusions and workflow
- Final: Ruling: full temporal readability was outside the reviewer's selected-still review — executor performs actual 1x browser playback and visual sample inspection; no reviewer playback claim. Cost if insufficient: acceptance remains on hold.
- Final: Ruling: hashes/reopen/report were still being produced at review time — executor completes these before final judgment. Cost if omitted: handoff is not reproducible.
- Final: Ruling: final modeling, precise hands/mechanisms, operational safety, mobile/web layout and storyboard matching — preserve explicit scope exclusions/unverified status; visible support proxies are still required and now present. Cost: final production requires those later checks.
- Final: Ruling: keel summary sentinel was not valid evidence — replace it with measured minimum/maximum from all evaluated frames. Cost if incorrect: curved-water contact judgment must be repeated.
- Final: Ruling: finishing-a-development-branch is applied as keep-as-is under the supplied local-only handoff boundary — no merge/push/PR menu, no commits, no ledger/output cleanup. Cost: user must separately request repository integration.
- No deferred minor findings. Trial value changes, including 140 radius, 32–40 mm lens, 5.2 reverse and 60-frame outbound departure interval, are recorded in manifest/report; none are operating specifications.

## M4 verification record
- Fresh Blender reopen ran 24/24 tests and full evaluated state export: `logs/reopen-final.log`. All 1392 frames: no camera OBB hits and no fixed-environment/ship-side errors. 100 fixed environment objects, 304 scene objects.
- Fresh reopen independently rendered f900. Pixel and boundary-data comparison, latest actual video playback, input preservation, hashes and visual review are recorded in final report and `review/*-check.json`.
- Authoritative artifact is the saved scene generated by `scripts/build_master.py`; metadata enriched by `scripts/finalize_handoff.py`. No GUI edits saved. Existing input files and tracked repository files remain preserved.
- M4 complete within spatial blockout scope: latest actual playback ended at 116s, 1392 decoded frames, 1 browser display frame dropped, 0 errors; all six playback sheets inspected. Final S5 top-view review framing expanded to include the complete approach/turn. Reopened f900 is pixel-identical and independently re-extracted boundary JSON has identical SHA-256. Input hashes unchanged, tracked diff empty; final tests 24/24. AC-1–10 pass at the explicitly documented sampling level; detailed production remains excluded.
