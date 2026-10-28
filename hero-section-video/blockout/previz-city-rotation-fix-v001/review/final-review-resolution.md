# Final review and resolution

Fresh-context read-only reviewer: city_rotation_contact_final_review.

Blocking finding: the extended jib stays crossed the trolley wheels at f0–106. Existing stay/body overlap was also still present. The external collision gate grouped the moving crane as one assembly and missed these internal contacts.

Resolution: stay anchors moved to ±1.35m across the boom, end cross-members extended to meet them. Carriage wheel outer halfwidth is0.86m. Added a separate jib-versus-carriage/head/hoist test.

- RED: `master-previz-city-rotation-fix-v001-internal.json`,6 bad pairs, process exit1.
- GREEN: `master-previz-city-rotation-fix-v002-internal.json`,625 quarter-frame samples,0 unexpected pairs, process exit0.
- Final shore/cab, dense external crane, protected trajectory, coast/camera gates rerun against v002. `verification-summary.json` binds every report to the delivered file hash.
- The final render is from v002, not the rejected intermediate file.225 source samples, f0–672 step3, before/after videos56.083 seconds.

Other reviewer observations: no visible-mesh modifiers in this scene; raw vertex BVHs cover the actual meshes. Shore and departing-ship separation look correct in the reviewed frames. Protected animation and timing checks pass.

Scope limitation remains explicit: the inherited S4–S7 warehouse contact models are preserved, not certified free from every legacy interference by this city-rotation correction.
