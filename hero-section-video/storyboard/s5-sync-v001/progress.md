# SDD ledger — plan: F:/pnpline-landing/hero-section-video/blockout/plan/pnpline-stage3-s5-storyboard-sync-codex-handoff-v01.md

Stage ③, source HEAD b56acf916901ce24be69686ef349ed61b437d608. Implementation inline; no master writes. Model/reasoning runtime selection not exposed reliably, reported unconfirmed.

Pre-flight: T0 source identity -> T1 render record -> T2 selected frame/style -> T3-T5 final manifest and approval. Current source hash differs from Stage2 report; investigate before adopting. Old Stage2 packaging has hardcoded wrong role labels and no render-time provenance; do not reuse.

Ruling: Work in a new dedicated storyboard/s5-sync-v001 directory within the user-designated checkout; keep the ledger here — the handoff only needs a worktree if isolation requires it, and source files are read-only — cost if wrong: output is not separated by Git branch, mitigated by scoped files and recorded dirty state.

T0 in progress: capture exact current input, compare committed master, fresh regression logs.
T1 pending: real-state probe, tested provenance pipeline, raw frames/contact sheet and continuous preview.
T1 user gate pending: baseline adoption, frame choice, style direction. Prior hinge/door/bridge approvals remain accepted.
T2 pending user selection: six line-art panels, source structure comparison.
T3 pending: limited master repair only if real defect confirmed and authorized.
T4 pending: final synchronization validation and fresh read-only review.
T5 pending: final user approval. Never infer from technical tests.

T0 technical complete: current8c76f0e1 vs committedcf4d9f15, 5,569 all-object/camera samples and mesh/hierarchy hashes equal. Saved frame720 vs907. Existing34 tests passed in new logs, originals not overwritten.
T1 structural candidates created: 672/720/732/766/842/900, 325 fresh raw PNGs, 27.083333s preview, six unmodified image-region panels, one Freestyle sample. Provenance/error rejection tests11 RED then12/12 GREEN, actual f810 rejected as turning, artifact checks pass. New Notion fetch equals stored snapshot.
User steering: “S4-05와 지금 제안한 S5-01이 일치하지 않는데 괜찮아?” Confirmed old board spatial left/right mismatch already at f648. Added explicit three-way comparison. Initial bundle-adoption question held; new baseline-direction question pending. Do not infer adoption or change protected frames. No full line-art production while this gate is unresolved.

User chose “기존 S4-05 콘티를 기준으로 연결 구도 재검토”. This resolves reference choice only, not master revision approval. Camera-only static trials and f552–840 diagnostic comparison completed. No tested camera-only result satisfies reference composition; do not call a technical continuity pass a storyboard match. Separate Stage2 layout/route proposal scope documented in review/s4-s5-recheck/recheck.md. Source SHA unchanged.

User explicitly approved separate layout/route proposal. Implemented bounded f552–948 proposal; original master read-only. Final adoption and upstream/downstream integration remain separate.

User explicitly approved separate layout/route proposal. Implemented bounded f552–948 proposal; original master read-only. Final adoption and upstream/downstream integration remain separate.

User explicitly approved separate layout/route proposal. Implemented bounded f552–948 proposal; original master read-only. Final adoption and upstream/downstream integration remain separate.

User explicitly approved separate layout/route proposal. Implemented bounded f552–948 proposal; original master read-only. Final adoption and upstream/downstream integration remain separate.

Layout proposal submitted: c9efed5cabde76926b340732191ef8470986a5b36b2095f1a416f2064a2c4296. Original unchanged. f552–948,397 frames/12fps; source and saved proposal provenance verified. Acceptance14/14, collision1,650,704pairs0errors; integrity pass; browser real-time playback ended at33.083333s. Fresh reviewer gpt-6-astra/high: no Critical/Important.
Final: minor (deferred): f692–700 crane leg briefly occludes the moving vehicle; disclosed for user artistic review.

Full-master integration authorized by user: “전체 마스터에 통합해라.” Completed at blockout/full-layout-master-v001/master-full-layout-v001.blend, SHA 194f9d5885efab2826fae8ba80c72313b08ffe9525a3f2d3d4edd78e3aeb0544. f0–1392/12fps. Full7, regression23, wheel5, layout14 checks pass; handoff and dock SAT pass in documented intervals; opening and adopted local composition preservation pass. Original unchanged. Fresh read-only final reviewer: no Critical/Important. Six line-art panels and style selection remain separate from this master integration.
