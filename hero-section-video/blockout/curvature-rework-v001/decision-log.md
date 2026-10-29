# SDD ledger — plan: hero-section-video/blockout/curvature-rework-v001/plan.md

Input warehouse-v008 SHA256 98b171ca73e85b535ce6a9c7953eb0b686143715878919ba40ff5d7524f5bccd. Current branch main; no workspace separation.

Task 1 complete: Earth center (0,0,0), radius140; US_FRAME is a tangent basis at a point on that sphere. Existing US land has flat z0.68 top with a deep skirt, and extra -40 foundations. Static architectural detail is often baked into mesh coordinates with shared city parents, so changing only parent tilt would not give per-building normals.

Ruling: scope is the pictured US district, including its warehouse and delivery roads — user points to that plate — China and the working harbor/voyage stay unchanged; if broader global conversion was intended, that would require a separate regional pass.

Ruling: buildings remain rigid assemblies, with short radial-bottom/tangent-top foundations; the warehouse is one tangent work floor at its footprint normal — keeps architectural shapes and existing handling contacts — its large interior floor is locally flat, while the underlying landscape is spherical.

Ruling: preserve the working crane/ship interface on its existing port tangent plane and grade the approach road into the curved landscape — maintains the proven crane/ship transfer — this localized engineered quay is a deliberate exception to the spherical landscape, not a city-wide plane.

Pre-flight: terrain consumes exact radius; grouped buildings must include facade/roof parts; roads and moving frames share spatial mapping; carrier/trailer/tractor share a frame to keep the hitch closed; all warehouse elements share one transform; camera adjustment begins only in the US reveal.

Task 2: v001 terrain passes; front building normal failed at 0.264 degrees because lowest ornaments shifted its anchor. v002 anchors main building body footprint instead. Warehouse apron widened to full yard and closed maneuver mesh receives radial support. Logistics test fixture corrected: rays must use road-only BVH and actual wheel vertices (rotating bounding boxes and self hits were invalid).

Task 2 complete: spherical terrain and building normals pass. Task 3: v002 showed 186 wheel support misses; baseline had 28 road-edge misses. v003 fits a rigid frame to all tire contacts and adds 0.8-unit shoulders / 3.2-unit terminal extensions; curvature 2/2, logistics 2/2, warehouse 11/11 pass. Existing actions and rigid geometry retained. Camera parent uses exact identity before frame381 to avoid floating-point drift in protected shots. Task 4: final-v003 renders running.

Final review: fresh gpt-6-astra read-only reviewer found one Important double transform in remaining cargo, one concealed Minor port foundation inverted section. Cargo regression test failed on v003 with5.95684-unit relative transform error; v004 excludes all carrier-owned descendants from warehouse membership. One fix pass in progress. Final: minor (deferred): hidden port foundation top/bottom inversion below existing quay; does not show in inspected renders. Final: Ruling: existing underwater island/bridge/hill portions remain submerged support geometry; fabrication-solid cleanup is outside this visual model change. Final: Ruling: final preview is Workbench6fps at original timing, production shading/settings and24fps source timeline remain; a final production render is not being claimed.

Task3 complete: full16/16 green onv004 including carrier-owned cargo regression. Final: fixed double transformation of remaining container cargo — test_remaining_cartons_stay_in_their_source_container_slots RED(v003)→GREEN(v004), full suite16/16. v004 clearance3126samples /0hits; preservation7425protected objects /2483rigid meshes /all9869source object actions unchanged. Task4 stills complete; updated6fps preview rendering. Task5 independent rebuild complete, final comparison running.

Task4 complete: refreshed11stills and254preview frames generated fromv004. Task5 complete: all16tests passed, clearance3126samples zero intersections; independent full10087object reproduction identical. Final read-only reviewImportant resolved inone RED→GREEN fix pass; one concealedMinor deferred. Same workspace/main retained; no commit or push. Task6 packaging and browser playback verification in progress.

Task6 complete: review.html finalv004 links verified, comparison view selector/slider operate, MP4 plays42.333seconds withreadyState4/errornull inin-app browser. Final tab7 kept asdeliverable; local127.0.0.1:18786server session54033 retained. delivery-manifest.json binds candidate/tests/audits/video/scripts. No branch/workspace separation and no commit/push.
