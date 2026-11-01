# China container port — continued 2026-10-31

Source: `inputs/base.blend`, SHA256 `e29fe506211d1b7f647f3eee01e066e49319aaae29dffebc6e4ed82aca371af3`. This is the saved China scene from the interrupted session, with the raised working crane and its original 12fps, f0–1392 timeline. Other US-city/33-second branches are separate files and are not overwritten.

Scope: build the front container terminal from the supplied Shanghai concept, move the existing working crane and berth, preserve container lowering, and leave camera animation unchanged. New camera direction and final voyage planning belong to the next task.

Layout: quay x[-28,30], y[-15,1.7], deck z1.25 in SF_CN_LAYOUT coordinates. Four rows contain 127 individually modeled cyan, blue and ivory containers, stacked 1–3 high. Three cranes comprise two static companions and the original animated rig. Apron roads, rails, bollards, fenders, service sheds, lighting and terminal vehicles fill the intervening space. The existing crane, ship, container and payload receive a shared placement displacement (14,-13.5,0). Four crane feet remain on the deck.

Preservation: original actions are not rewritten. Added placement parents hold the working berth through f252 and smoothly reconnect to the source by f360. Original camera matrices/lens remain exact across all 1393 frames; original downstream logistics transforms remain exact from f360. The provisional connection is not a final route design.

Corrections from the interrupted candidate: move five old bollards out of container bodies; move remaining apron rocks to landscaping; deepen quay foundation to z-7; add corrugated container roofs; locally refine the original connected ocean surface so the relocated loading berth supports the hull. Far ocean/US geometry and materials remain unchanged.

Acceptance evidence: review/verification.json, connections.json, master-cn-port-layout-v001-lift.json, master-cn-port-layout-v001-internal.json, and static-audit.json must all identify the current saved master hash. Still images and motion-review metadata must identify the same hash. Review cameras are temporary and never saved into the master.
