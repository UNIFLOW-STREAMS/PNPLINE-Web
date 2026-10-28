# SDD ledger — plan: F:/pnpline-landing/hero-section-video/blockout/plan/pnpline-stage3-s5-storyboard-sync-codex-handoff-v01.md

User explicitly selected s5-integration-v001 for this storyboard task on 2026-10-09 (client date; exact approval time unavailable). This replaces the full-layout master as the source of this task only. No instruction to delete or replace the separately integrated full master.

Ruling: Reuse validated raw renders and the minimal style sample from s5-sync-v001 because the current selected source is byte-identical (8c76f0e1…). Preserve original render records; freshly reopen the source and compare evaluated cameras/states before reuse. Cost if wrong: stale artwork; mitigated by input/dependency/output hashes and fresh scene-state comparison.

Ruling: Work in a new s5-sync-v002 output directory in the user-designated checkout, with the source and earlier outputs read-only. Existing plan permits this when no .blend changes require worktree isolation. No commit, branch mutation or cleanup. Cost if wrong: outputs share the working tree; isolated directory and input hashes prevent overwrite.

Pre-flight: T0 source/state/validation -> T1 candidate package and style sample -> frame/style choice gate -> T2 six line-art panels -> T4 final provenance -> T5 user final confirmation. Prior approval selected the layout proposal, not these six frames or this style. Latest source selection is recorded and will not be asked again.

T0: source hash matches previous raw source. Existing provenance/role rejection tests freshly pass 12/12. Fresh scene-state and existing behavior regression in progress.
T1: preserve roles 01/02/04/05; verify corrected 03 f732 and 03A f766 from actual state. f810 remains a stopped diagnostic.
Model/reasoning runtime configuration: unconfirmed. Final reviewer may use explicit gpt-6-astra/high per skill.

T0 complete: fresh actual source reopen/state equality and all34 regression tests pass. T1 selected by actual user reply: “6개 프레임과 선화 방향 채택”. Raw 325-frame preview played to27.083333s at1x with no media error. New expression lineage tests8 failures RED (valid case passes), implementation GREEN pending.

T2/T4 technical complete: six selected frames freshly rendered as Freestyle in separate Blender process; full source unchanged. Expression lineage8 RED failures ->9/9 GREEN. All6 raw/line-art comparisons visually inspected, all6 same camera projections and all6 expression-to-panel regions verified. Playback27.083333s at1x complete. Final user approval remains separate. Freestyle duplicate-visible-edge warnings auto-corrected by renderer; inspected output retained. Final read-only review next.

Final review: fresh gpt-6-astra/high reviewer found no Critical/Important current-output issue. Independently rechecked all current provenance hashes and validation logic read-only.
Final: minor (deferred): verify_final.py can strengthen future-run completeness by invoking validate_selection and all dependency checks already independently verified for this bundle.
Final: minor (deferred): package_final.py repeat execution duplicates HTML comparison links; current page is unaffected.
Final: Ruling: Final artistic judgment remains the user's T5 decision — technical tests cannot grant it — cost if wrong: final adoption remains pending.
Final: Ruling: Do not infer hidden door visibility from the S5-04 still; rely on actual neighbor motion and existing door tests for state — user selected this frame and camera remains unchanged — cost if wrong: still-only door readability remains limited.
Final: Ruling: No new precise physics claim — the plan calls for existing regression reproduction with an unmodified master — cost if wrong: behavior beyond those tested conditions remains unverified.
Final: Ruling: full-layout-master suitability is outside this task — user explicitly selected s5-integration-v001 — cost if wrong: these boards will not match the separately integrated layout master.
T4 technical synchronization passed. T5 exact final package awaiting actual user approval; do not overwrite approved panel files.

User steering: “지금 프리뷰 렌더링을 보면 너무 느리다.” Clarification answer: “프리뷰 재생만 빠르게”. Added full-frame 2x file and page speed controls; original master/timing/selected frames preserved.

Root cause investigation: user-visible master path was saved later, hash changed from8c76f0e1 tocc2dec40; saved frame907→521. Full f624–948,304-object world matrices, all camera matrices/lens and meshes equal. Updated final manifest to reference frozen exact render source and current equivalent save; original rendered record remains immutable. 2x browser playback ended13.541667s in13.616s, no media error.
