# Independent review (candidate before final fix pass)

Reviewer: one fresh-context gpt-6-astra agent, high reasoning; read-only. Required by executing-plans skill. No shared-scene editing or second reviewer.

Verdict before corrections: rework required. The then-green 12 tests and 0 camera OBB hits did not establish acceptance.

| Finding | Impact | Final correction / regression |
|---|---|---|
| Outbound cart travels beyond x68 floor, floating and intersecting loader | P1, AC-8 | Cart stops x66; loader has a supported bridge; clearance test |
| Last box moves without support and overlaps preloaded box | P1, AC-8 | Arm/carry-support proxies, empty rear slot, floor contact test |
| Primary van hits destination building at f1373 onward | P1, AC-9 | Move building outside route; test complete body envelope against destinations |
| Picking product floats outside rack | P2, AC-8 | Supported bin shelf and legs; contact test |
| Crane cable tops connect to empty space | P2, AC-6 | Moving cross-member trolleys; cable attachment test |
| Secondary van yaws independently of diagonal merge | P2, AC-9 | Curved merge, tangent-derived yaw, matching road; heading test |
| Manifest says fixed 40mm although lens reaches 32mm | Reporting | Record actual 32–40mm range and interval |

All six scene findings reproduced before corrections: logs/review-findings-red.log (18 tests, six failures). Final pass and whole suite are recorded in logs/validation-final.log.

Declined-to-judge list and executor rulings:
- Full temporal readability / AC-4/5: reviewer saw selected stills while video was rendering. Ruling: parent performs actual browser playback and visual sample inspection; no reviewer playback claim. Cost if insufficient: acceptance must remain on hold.
- AC-10 hashes/reopen/report: still being produced. Ruling: parent must complete them before final judgment. Cost if omitted: irreproducible handoff.
- Final modeling, hands/mechanisms, operational safety, mobile/web composition, storyboard matching: expressly outside scope or unverified. Ruling: preserve these deferrals; supporting contact proxies are still required. Cost: cannot advance to final production without later verification.
- Keel metric sentinel: already acknowledged by parent. Ruling: replace sentinel with actual evaluated minimum/maximum; no acceptance from a placeholder.

No deferred minor code findings were reported. The author found two further dock contact issues during correction: folded doors overlap side panels and rear chassis penetrates dock wall. Both reproduced in logs/dock-clearances-red.log, then corrected geometrically.
