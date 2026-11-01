# Independent final candidate review — US arrival rework v008

Spec/plan: `../objective.md` (read in full). Ledger/rulings: `../decision-log.md`. Report is still provisional pending this review. Reproduction commands: `../REPRODUCE.md`.

Review the entire task, not merely the current tracked diff. Original repository base b40b41df97a878d62238518fc36bb73603ead7e2; user independently committed a work-in-progress snapshot as deacdefb. Current tracked and untracked files under `us-arrival-rework-v001` form the candidate. Do not amend or undo that user commit.

Candidate: `../candidate-arrival-v008.blend`, SHA256 4f0501406fb2172d18ab39a8849bb5ce2bfccd101737d35ed742d27a7e08827c. Immutable input `../inputs/current-v004.blend`, f74c7284ccda0498a1ad0b4eb60421758a6ecdca13cc75fe037bb51957054c42. User's reported earlier v004 retained as `../inputs/verified-v004.blend`. Source D was not overwritten; its live file later changed externally (eec2697b05bad025c7604ddb84aa9c5eb9a87199c45eb548657c0cf8de6d246c), so do not confuse the live D file with the frozen comparison input.

Core implementation: build_arrival.py, design_details.py, scene-config.json. Camera permission is explicit for f300–528; no renewed camera approval is needed. All other protected original geometry/animation and camera outside this interval must be preserved. Own UC city geometry may move and be refined. Functional P02 may change only material slots, not geometry or work points.

Inspect actual images: evidence-v008/f0440.png, f0455.png, f0471.png, arrival-v008/f0450.png and f0648.png, material-v008/f0450.png, inputs/usa-miniature.png. Diagnostic overview is supplementary and partly crops letters; do not use it to pass the actual arrival composition. Videos: ../preview/baseline-v004.mp4 and ../preview/candidate-v008.mp4, same 433 integer frames f288–720, 12fps, 640×360. Browser playback at 1× reached both ends (36.083 seconds); screenshots inspected at f288, f485, f689, plus seeked hero comparison. These are sampled observations, not a claim of a human viewing every instant. UI preview ../review-v008.html is available at local port 18784.

Fresh technical evidence: v008-evidence-summary.json binds exact hashes; preservation 1,561 samples zero errors, collision 1,513 samples zero surface intersections/near-camera hits; continuous surface co-visibility f440–471, 2.667 seconds. Six arrival/support/motion/civic tests and three verifier mutation tests pass. Existing inherited 24-test suite reproduces the same P01 cable support failure in both baseline and candidate (not skipped). Independent rebuild matches 1,505 owned/crane/camera entries plus protected signatures; f450 RGB pixels exactly match.

Review focus:
- Is this actually a low stern-follow shot and readable continuous arrival, not a side orbit or overhead workaround?
- Does the static arc, ten stars, enlarged statue, building variety/density, civic dome, bridge and blue/white functional crane satisfy the visual spec in actual camera images?
- Could allowed-camera exceptions hide protected motion edits? Examine verifier and real mutation tests, not just green labels.
- Are camera joins and local-water roll justified, with exterior baseline behavior kept separate from changed behavior?
- Does collision coverage miss a material route obstruction, floating city support, or severe occlusion visible in later shots?
- Are reproduction, source guards and evidence hashes coherent? Are claims overstated or missing important evidence?

Read-only: do not edit files, index, HEAD, branches, Blender input/candidate or UI; do not spawn subagents. Return specific Critical / Important / Minor findings, requirements verdict, and a list of any behaviors you declined to judge with reasons. Acknowledge limitations honestly; the author will make one fix pass after this review.
