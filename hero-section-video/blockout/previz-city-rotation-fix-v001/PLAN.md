# City rotation collision correction

User request: fix all collisions/interference in the adopted city-rotation option.
Baseline: inputs/base.blend, SHA256 ce36841b9e3418efe1611fdbd9645b6ed9d332ff5db4278974024274d9d6cebb.

1. Reproduce ship/coast, cargo/landscape, crane/portal, US arrival contacts.
2. Preserve the adopted city orientation and its internal layout. Separate the city from the voyage corridor; reconnect the crane to the unchanged load position and release time.
3. Retract/park the crane clear of the departing ship; remove US underwater terrain intrusion.
4. Check every frame of changed motion, dense samples near clashes, actor-to-environment and actor-to-actor crossings; verify protected source trajectories and timeline.
5. Render before/after and a continuous preview, independent final review, promote a new master and open it visibly.

## Progress / rulings

- Baseline contact regression RED: 251 obstruction pairs. Coarse full-timeline environment scan: 725 raw crossing pairs, many are normal floor/rail/landing contacts.
- Trial v001 rejected: moving CN_FRAME also moved the legacy CN_QUAY into the ship. Ruling: move SF_CN_LAYOUT only, retaining the adopted orientation and the legacy quay position.
- Trial v002: shore/cab regression GREEN; separate actor scan found the extended jib striking the departing bridge mast at f220–223. Reject and park the jib shore-parallel, trolley retracted, empty spreader raised.
- Ruling: exact seated cargo/deck surfaces, engaged twistlocks and slew-bearing contacts are intentional. Do not remove these to make a raw triangle count zero.
- Ruling: source S4–S7 warehouse mechanisms and their pre-existing contacts are outside the city-rotation change. Keep their transforms and geometry identical and disclose unchanged baseline contacts in the audit. This correction must not introduce new interference there.
- Original source and prior masters are preserved. Trial files are not adopted. No git commit/push is requested; all new artifacts stay in this dedicated version folder.
- Final review found stay-to-trolley wheel intersections inside the single crane group. Internal regression RED confirmed 6 stay/body/wheel pairs through f116. Moved stay anchors outboard (halfwidth1.35m) and widened the end cross-members to support them. GREEN: 625 quarter-frame samples, no internal jib/trolley/head/hoist crossings. Final delivery advances to master-previz-city-rotation-fix-v002.blend; provisional v001 is rejected.
- Re-seated the translated coast toe on the curved ocean: original translated toe gap reached1.205m; all512 toe points now6cm submerged, XY contours and upper rim exact. No collision geometry is hidden.
- Complete: final v002 hash37fa14b4e0123cb94da18de2338af1a1bccbf69341cc96b64949719e6045ec7e; all five hash-bound verification gates pass,225 final render samples packaged, latest-previz registry updated, final Blender file and localhost18777 comparison page opened. Original files preserved; no commit/push.
