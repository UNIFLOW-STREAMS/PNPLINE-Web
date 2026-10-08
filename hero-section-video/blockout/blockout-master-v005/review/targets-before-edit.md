# S3 targets fixed before production modification

Boards use varied scene ratios; compare their inner scene without notes, never stretch the 16:9 renders. Approximate hand-read board ship widths: K1 .65; K2 .30; K3 .32; K4 .52; K5 .85; K6 .75. Proxy hull/bridge proportions and R140 are fixed, so these are compositional references, not claimed exact matches.

First lens-preserving feasibility: local (-25,-27,35), target (0,0,5) gives a readable rearquarter ship and a visible spherical cap. Curvature is weaker than the illustrated dome, and the proxy's tall box stacks increase deck dominance. Do not call the result identical to the boards.

Frozen mechanical targets: f278..338 (5 seconds boundary-to-boundary), ship projected width .26..38, all bounds inset >=.04, distance max/min <=1.02, world camera translation >40m; sphere silhouette peak y .65..95 and rise >=.11 between center and x=.05/.95. Sphere diagnostic is not a substitute for visual coastline/ship-visibility review. Projected bounds include occluded geometry and are never claimed as visible pixel area.

Destination: f366..390 (2 seconds), rear X<-8; ship width .32..55 and recognizable crane/quay plus bow/water in the actual images, not just a projected port box. Recover ship width >.50 by f398, before side passage at f422; f398..450 width max/min <1.5. Same Y<-9 throughout; frontquarter X>12, width>.48 at f450. K6 framing remains constrained by preserved B34.

Preserve f0..217 and f455..1392 camera/target/lens exactly, including endpoint adjacent differences; preserve all noncamera states, object count, geometry, animation, guides, materials, markers, FPS, camera sensor/shift/clip/lens. Existing 24 master behavior checks retain their thresholds. Stronger-than-possible storyboard curvature and larger-than-B34 K6 remain disclosed constraints, not silently relaxed numeric goals.

Transient probe issue: Blender render reevaluated animated camera keys, restoring baseline poses. Cleared camera animation only in the disposable no-save feasibility process; reran the probes and visually confirmed distinct outputs. Final production uses keyed evaluated poses.
