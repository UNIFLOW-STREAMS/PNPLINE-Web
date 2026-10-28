# Independent engineering review — motion-polish A/B

Reviewed 2026-10-09. Scope: the isolated `previz-motion-polish-v001` output, specification `inputs/handoff.md`, and the user's additional approval for S5 road/contact corrections. The reviewer made no implementation edits. This document is the reviewer's only authored output file.

**Core engineering and saved stills verdict: acceptable. No unresolved blocking implementation finding in the reviewed versions.** Final delivery acceptance still requires the primary agent's completed matching A/B media package and full 1× playback evidence. User A/B rhythm selection and public Scroll World approval remain separate.

## Exact version scope

| Asset | SHA-256 |
|---|---|
| Immutable `inputs/source.blend` | `8cf66b7713b85fbe175229ab87456d40b420b866d222b28d8a712d60e4511412` |
| Final candidate A | `c7ff4e0938804a7f5d5979a62423ac9eab666b6e9c6076934f9bf076398eb1b2` |
| Final candidate B | `34ea2951504696fe087f76ba67d06be2e15ae1d83e91c6c46070ee51ebd8aa63` |

A is 1,393 displayed frames / 24 fps = 58.0416667 seconds. B is 1,306 displayed frames / 24 fps = 54.4166667 seconds. No extra playback multiplier is intended. First-to-last frame time and total video exposure duration are correctly distinguished in the maps.

## Review and independently executed checks

- Read `motion.py`, `build_candidates.py`, `contact_repair.py`, `validate_candidates.py`, the test suite, render/media/map scripts, and source regression adapter. The shared monotone map preserves actor synchronization. The wheel correction transforms US-space vertical displacement through the full parent basis, preserving horizontal route and rotation within explicit tolerances.
- Independently ran `python -B scripts/test_motion.py`: 9/9 tests passed. Inspected retained red evidence: 8 of 9 initial tests failed, and the original camera-stop check failed. Reviewed the later road-overlap red assertion and green bounds result. Earlier failed contact/driver experiments were not treated as final evidence.
- Opened both final `.blend` files in a new `C:/Program Files/Blender Foundation/Blender 5.1/blender.exe --background --factory-startup --python-expr ...` process; no file saving occurred in the probes. Runtime reported Blender 5.1.0, build `adfe2921d5f3`.
- Independently checked all eight wheels' saved location X/Y/Z correction times in source interval 648–900. All three axes have identical time arrays for every wheel. A has 35,566 correction keys per axis; B has 34,290. Maximum interval is exactly 0.0078125 output frame (1/128). Dense keys survive save/reopen.
- Independently measured ground clearance under **every transformed tyre mesh vertex**, using visible support surfaces only: `US_QUAY`, `US_LAND_TERRACE`, `E09_MANEUVER_YARD`, `MP_CONTINUOUS_ROAD`. At each vertex, a US-vertical downward ray starts 5 m above the vertex and is limited to 20 m; the highest visible hit is used. Minimum signed vertex clearance per wheel is the support gap; its negative is penetration.
- Contact probe used 4,053 distinct source times per candidate: source 648–900 inclusive at 1/16-frame steps; original failures 700.5450141107419, 704.0991761629364, 707.2786643890552, 709.48074155479, 737.0149324809711; and output offsets −0.01, −0.005, 0, +0.005, +0.01 around mapped source 700.625, 707.1875, 766.4375, inverted through each candidate's map.
- Independently confirmed the added road has US-space minimum X = 17 and maximum Y = 26; it no longer overlays the coplanar quay/yard tops.
- Inspected matching final stills at A source 700.545 and 776.5, and B source 776.5. The previously introduced quay/yard stripe artifacts are absent. Compared the yard case to the unchanged source still.
- Verified actual SHA-256 values, not just manifest text: each final blend matches its build, validation, time-map, stills, and master-regression records. Build script, timing script, contact script, configuration, validation script, and still-render script hashes match their corresponding manifests. All 23 still-image hashes per candidate match disk files. Immutable input hash remains the value above.

| Independent contact result | A | B |
|---|---:|---:|
| Maximum observed penetration | 0.144303 mm | 0.121474 mm |
| Maximum observed support gap | 0.017762 mm | 0.017762 mm |
| Contact acceptance tolerance | 2 mm | 2 mm |

The independent A maximum occurs at source 707.1926718201842 (`A03_TRAILER_WHEEL_0.250.85`); B at 707.1951049955762 (`A03_TRAILER_WHEEL_0.25-0.85`). These extra near-edge probes explain why the maximum is larger than the main validator's 0.023782 mm figure. Both are below the unchanged 2 mm actual tyre-contact criterion.

## Corroborating saved validation

Read final `validation-A.json` and `validation-B.json`: both `pass_all: true`, empty errors, and the exact final hashes above. A covers 11,190 source-matched samples; B covers 11,103. Six storyboard camera/actor matrix and lens deltas are reported as zero; the approved wheel vertical repair is checked separately. Wheel horizontal drift is at most 0.037257 mm, hitch error 0.440197 mm, container-support translation error 0.583662 mm, and door/body penetration zero in the reported sampling domain.

The original 24 master regression tests passed for each final candidate. Reviewed `run_source_regression.py`: it maps source frame requests into output time, forwards camera projection to the actual Blender scene, and leaves the original assertions unchanged. The earlier adapter exception is retained as diagnostic evidence. These master-suite runs were performed by the primary agent; the reviewer verified the records, final blend hashes, and adapter implementation.

Camera patch endpoint checks were expanded beyond the six scene joins. An independent earlier probe of unchanged camera animation at all patch starts, nodes, and ends found no major endpoint jump (maximum measured positional velocity delta about 0.02588 m/frame over ±0.125 output frame). The final saved validator additionally checks integer-frame rotation jumps and scene/patch translation continuity. Rotation/lens rate rows are diagnostic measurements; they are not a mathematical proof of continuous differentiability.

## Findings resolved during review

1. **Tyre penetration hidden by the center-ray test.** A previously saved candidate penetrated a road/yard transition by 16.23 mm at source 776.5 even though the center-based measure could appear acceptable. Repair and validation now use actual lower tyre vertices against visible support, retain the historical center-ray metric for diagnosis, and preserve the 2 mm physical-contact tolerance.
2. **Discontinuous transition geometry and lost dense keys.** Sparse road-ring heights created a roughly 6.5 mm quay step. `FCurve.update()` also silently discarded close keys: a controlled in-memory Blender test reduced 20 keys at 1/128-frame spacing to 10. Exact ramp-break clipping and preserving already sorted distinct LINEAR keys resolved both mechanisms. The final saved-file density/contact checks above confirm the fix.
3. **Visible coplanar overlap.** The first numerically passing road overlay produced pronounced new stripe artifacts over the quay and yard. Clipping the added road to the connecting region X ≥ 17, Y ≤ 26 resolved the overlap. Final stills confirm that the introduced stripes are gone.
4. **Evidence coverage.** The build manifest now includes `contact_repair.py`; saved validation checks common XYZ key arrays and road bounds; camera patch endpoints are included; failed attempts remain identifiable.

## Limits and remaining delivery gate

This review establishes the engineering result for the hashes above and the stated sampled domains. It does not prove collision-free motion at every real-valued time or certify final character/detail animation; original deferred blockout details remain deferred. Direct tyre sampling tests mesh vertices, not an analytic swept-volume solution.

At the time this document was written, the primary agent was completing final MP4 rendering/encoding and would perform full 1× playback. The reviewer has inspected the provenance/encoding code, but has **not** claimed to watch either complete final MP4. The delivery report must verify matching final render/media hashes, complete frame counts and decode results, and actual playback evidence before declaring the whole handoff complete. A/B rhythm remains the user's choice.

## Final delivery follow-up — AC10 consistency passed

This follow-up supersedes the pending media/playback delivery gate above. The final media and playback records are now available. **Final engineering-candidate verdict: 속도·이징 검증 후보 수용 가능 / 사용자 리듬 선택 대기.** No blocking inconsistency was found in the final delivery evidence.

The reviewer independently executed a read-only Python hash/manifest audit after reading the final `report.md`, `README.md`, and `review/visual-review.json`:

- All 76 files listed by `hashes.json` matched their actual on-disk SHA-256 before this follow-up was appended. The primary agent must refresh that manifest after this document changes.
- All 1,393 A frame PNG hashes and all 1,306 B frame PNG hashes match their final render records; frame lists cover exactly 0–1392 and 0–1305 without omissions or duplicates.
- Final render records have `status: complete`; their blend, current render script, configuration, and validation-record hashes match disk. Media records link to those exact render-record hashes.
- Final blend identities agree across render, media, validation, full time map, S5 storyboard map, scroll map, and visual-playback record. They remain the same reviewed A/B hashes listed at the beginning of this document.
- Actual MP4 hashes agree with both media and visual-playback records. A is 1,393 frames at 24 fps / 58.041667 seconds; B is 1,306 frames at 24 fps / 54.416667 seconds. Stored FFprobe reports confirm 960×540, H.264, 24/1 fps and the full decoded frame counts; both packaging records report full decode PASS.
- The primary agent's browser observation record reports playback rate 1, an unbroken played range from zero to the complete duration, `ended: true`, and `error: null` for both exact final videos. The record explicitly limits its visual claim to representative live screenshots and actual rendered stills. This reviewer audited that evidence and its hashes; the reviewer did not personally watch both complete videos.
- The original external source `.blend` and the isolated input copy independently hash to the same unchanged `8cf66b77…` identity. The final report distinguishes main-validator and independent edge-probe contact maxima and retains the blockout/finite-sampling limitations.

| Final media | SHA-256 |
|---|---|
| `preview/candidate-A.mp4` | `5d5ce6d96e51e384c17c515082fe17db0c1c47eb768fbe4425be9cd8f064e4d1` |
| `preview/candidate-B.mp4` | `4b027da7a35f7389ddfdd274f91fa3f6dd1a14d64d277346d1e666ed0625e4c6` |

No contact tests were unnecessarily repeated in this follow-up: the implementation and reviewed Blender files are unchanged. User rhythm selection and final public scroll-experience approval remain outside this engineering acceptance.
