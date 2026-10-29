# PNPLINE warehouse replacement

Spec: the user's 2026-10-30 warehouse request and the three copied reference images in inputs/.

Use the completed arrival-v010 scene. Replace the existing US warehouse proxy with the reference's navy industrial cutaway shell, readable authentic PNPLINE branding, dense multi-tier racks, a continuous conveyor, packing stations and functional end loading bays. Replace green accents with logo cyan and gray. Adapt stored and moving cargo, equipment, workers and truck interfaces to this layout; trucks must not intersect the building.

Keep original inputs, previous task files and unrelated user changes. No commit, push, upload or master promotion. Preserve the city/arrival shot, ship/ocean/China/cranes, scene duration and markers. Warehouse-zone layout and its existing operations are authorized to change by this new request. Keep logistics event timing where possible.

1. Survey actual scene, parent spaces, existing transfer times, truck swept envelopes and branding colors. Freeze input and record scope.
2. Write failing scene tests for functional shell/brand, cargo support, conveyors and truck clearance. Build shell around surveyed envelope; preserve entry and exit openings.
3. Reposition rack/cargo and animate warehouse transfers on physical surfaces; preserve continuous custody of cargo. Add conveyor flow and detailed handling, with no teleport between stages.
4. Verify all-frame truck/building and equipment clearance, cargo support/continuity, narrow allowed changes against frozen input, and existing regressions. Reopen and independently reproduce.
5. Render actual-camera and design views and 12fps warehouse sequence. Inspect imagery and playback. One fresh read-only final review under executing-plans, then one Important fix pass if needed.
6. Deliver versioned .blend, scripts/config, before-after stills/video, report and file inventory.

Review focus: gaps between collision samples; open truck doors and articulated trailer envelopes; cargo support during handoff; visual reference fidelity including header/logo/conveyor/rack density; new roof/wall occlusion of existing camera; preservation outside authorized warehouse scope.

Interfaces: shell openings consume truck survey; conveyors and cargo share independently verified top heights; animation maps must match rack slots and loading bridge endpoints; verification consumes evaluated scene rather than builder labels alone. Visual review remains required in addition to tests.
