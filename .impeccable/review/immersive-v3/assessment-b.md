# Assessment B — detector and browser evidence

Method: isolated Assessment B sub-agent `/root/v3_evidence_critique`; Assessment A output was not read. This document supplies mechanical evidence for parent synthesis, not a replacement design direction or an independent aesthetic score.

- Target: `F:/pnpline-landing/output/landing-immersive-v2/index.html`
- Live page: `http://127.0.0.1:7320/`
- Date: 2026-10-31 local task date
- Scope: hero, services, quote and separate privacy access path. This is the three-section design preview, not the full V4 site or a production enquiry system.
- Writes: this report and `assessment-b-detector.json` only. No UI/source/design-document modifications.

## Deterministic scan

Executed exactly once from `F:/pnpline-landing`:

```text
C:/Users/KIM TAEHYUNG/.agents/skills/impeccable/scripts/impeccable.cmd detect --json F:/pnpline-landing/output/landing-immersive-v2/index.html
```

The detector returned exit code **2**, meaning findings. The complete, unmodified stdout JSON is saved in `assessment-b-detector.json`. It is an array of **10 findings**, all category `quality`: **5 warning + 5 advisory**, **4 rule names**, **1 reported file**. Every finding reports `line: 0`, so these are not precise source-line locations.

| Rule | Count | Severity | Reported file/location |
| --- | ---: | --- | --- |
| `low-contrast` | 2 | warning | target `index.html`, line 0; identical `#f3f7f8` on `#c4c4c4`, 1.6:1 |
| `cramped-padding` | 2 | warning | target `index.html`, line 0; `.hero-pin` top, `.quote` left/right |
| `design-system-font` | 1 | warning | target `index.html`, line 0; skip-link font reported as malformed `sans sc\",sans-serif` |
| `design-system-color` | 5 | advisory | target `index.html`, line 0; values enumerated below |

Color advisories: `rgb(206,215,217)` details border, `rgb(73,84,90)` inactive service-tab text, `rgb(8,119,153)` service CTA text, `rgb(93,109,116)` volume hint, and `rgb(89,107,114)` submit helper. These literals exist in the CSS and are not all declared as primitive colors in current `DESIGN.md` frontmatter. They are documentation/token-coverage advisories, not evidence that these five text/border uses are illegible or visually inconsistent. No unsolicited document repair was performed.

### Adjudication and false positives

1. **`design-system-font`: confirmed false positive.** Current `DESIGN.md` declares `'Noto Sans SC', sans-serif` in display, headline, title, body, compact body, label and action. CSS line 11 uses that same family; live computed styles resolve `"Noto Sans SC", sans-serif` and `document.fonts.status` is `loaded`. The detector's truncated family string is not the actual font-family.
2. **`.hero-pin` cramped top padding: false positive for the tested layout.** It is the full-bleed media wrapper, not a text box that needs inset. Live `.hero-panel` is x=32, width=556 with padding `30px 32px 28px`; text is inside that panel. Source: `style.css:55`, `style.css:60`.
3. **`.quote` cramped left/right padding: false positive for the tested layout.** Outer section has vertical padding and an inner `.wrap`. At 1280×720, `.quote-layout` starts x=56.323 and ends x=1213.677 within a 1270px content width; `.quote-form` has 34px internal padding. The screenshot visibly has inset text and fields. Mobile CSS also declares separate intro/form inset, but mobile was not rendered in this B run. Source: `.wrap`, `style.css:104`, `style.css:109`, mobile `style.css:211–215`.
4. **Two `low-contrast` entries: not reproduced on the tested desktop; do not report as confirmed desktop contrast failures.** The stated pair is the mobile hero text color and the media wrapper fallback background. Live desktop body copy is `#424b50` over a 95%-opaque white panel, not `#f3f7f8` over gray. Mobile CSS adds a dark pseudo-element scrim over the video (`style.css:178–181`). The detector pair ignores that composited layer. This is a likely incomplete-background/static-cascade finding; mobile pixel contrast across video frames remains unverified and must not be declared a universal false positive or a mobile pass.

## Browser method and coverage

Fresh B-only IAB tab, never an existing/user/A tab. Initial `chrome` creation failed with `Browser is not available: chrome`; inventory then showed IAB, which was used successfully. No existing tab was repurposed. The B tab was closed after the checks. Browser remained hidden; no `[Human]` overlay tab was created.

The **unchanged current viewport was 1280×720 CSS px, DPR 1.5**. Scrollbar consumed 10px, leaving `document.documentElement.clientWidth=1270`. Screenshot and DOM inspection covered initial hero, a scrubbed hero frame, service heading/warehouse, service tabs, quote/default form, invalid-email state, and separate privacy page. Screenshots were visually inspected through the native tool; no screenshot file was written because B's output ownership was limited to the two report files.

Read-only DOM/computed-style inspection and ordinary UI interaction were used. `evaluate` did not set globals, mutate the document, inject scripts, or dispatch synthetic application events. Overlay injection is **unavailable**: this browser documents `playwright.evaluate` as read-only. Consequently the detector visualization live-server, mutation preflight, script injection, `[Human]` labeling, and overlay console collection were skipped. No alternate live-server was started. The fallback is the successful CLI JSON plus native screenshots, DOM geometry, actual interaction states, and source inspection.

### Hero behavior: observed live

| Observation | Result |
| --- | --- |
| Video source | `/assets/hero-scrub.mp4` |
| Metadata | duration **33s**, readyState **4**, `autoplay=false`, `controls=false`, body `media-ready` |
| Initial | scrollY=0, currentTime=0, paused=true |
| Forward scroll | scrollY=720, currentTime=13.749583, paused=true |
| No further scroll, separate subsequent read | scrollY=720, currentTime remained 13.749583, paused=true |
| Reverse scroll | scrollY=360, currentTime=6.874791, paused=true |

At this viewport, `.journey` is 2448px (340svh) and the sticky pin is 720px, leaving a 1728px scrub interval. The observed times agree with the source mapping `progress × (duration − 0.001)`. Forward seeking, holding position between observations, and reverse seeking were observed. This was not a frame-by-frame accuracy/performance benchmark or a long-duration soak test. Source confirms video remains paused and seeks via scroll/rAF/seeked (`script.js:19–59`).

### Structure, navigation and overflow: observed live

- `main > section` contains exactly `journey`, `services`, `quote`. Document language is `zh-CN`. Chinese headings, body and six form labels were present; no exhaustive byte comparison against original V4 manuscript was performed.
- Initial document width is 1270px, equal to clientWidth; element geometry scan found no element beyond the viewport by >1px. Service and quote states also returned no horizontal overflow. This is a current-viewport result, not a mobile or 200% zoom pass.
- Clicking the service nav set URL `#services`, scrollY=2448 and `document.activeElement.id=services`. Service heading top=112px, below the fixed header bottom=76px.
- Quote nav set `#quote`, focused `quote`, and showed the six-field form. The quote container top was approximately 0 and its content started about 96px below, so the fixed header did not cover the section title in this tested state.
- Headings exposed h1 → h2 → h3 hierarchy. Meaningful illustrative-image alt text, decorative SVG `aria-hidden`, skip link, section labels and explicit form labels are in source/AX. A real screen reader was not run.

### Service exploration: observed live

- Clicking FBA detail expanded it while the initial dropshipping detail remained open. AX reported the native expanded state. Independent native disclosures work.
- Clicking the IOR tab selected it and exposed `panel-import` while freight became hidden.
- Pressing ArrowRight on the IOR tab selected/focused inventory. Observed inventory `aria-selected=true`, `tabIndex=0`; other tabs `false`, `-1`; only `panel-inventory.hidden=false`.
- Current tablist `aria-orientation=horizontal`. Source supplies vertical orientation ≤680px and Home/End/arrow handling; those other keys and mobile orientation were not exercised in this run.
- Keyboard-focused inventory tab showed a visible outline in the screenshot. Computed outline was `rgb(0,125,168) solid 2.66667px` at the browser's raster scale; CSS declares 3px with 5px offset.

### Quote behavior: observed live and source-limited conclusions

- Exactly **six non-consent fields**: product, shipping, volume, destination, IOR, email. Every control has a visible associated label. All six measured 52px high. A separately labelled consent checkbox and two privacy links are present.
- Source/DOM show form `method=dialog`, `novalidate=true`, no action attribute, and submit handler `preventDefault()`. No fetch/XHR/backend call is in the inspected script.
- Empty submit with unchecked consent stayed on `#quote` and displayed **“设计预览：信息未发送。”**. Status has `role=status` and `aria-live=polite`. This supports the intended non-transmitting preview contract. No network interception was available/used, so this is source plus observed UI evidence, not a network-capture certification.
- Entering synthetic `invalid` into email and submitting exposed “请填写有效的联系邮箱。”, set `aria-invalid=true`, and moved focus to email. Screenshot showed error text and focus ring.
- Replacing it with synthetic `qa@example.test` cleared the error immediately and set `aria-invalid=false` without another submission.
- No field or consent is `required`; blank email is intentionally accepted by this preview. Mandatory production validation, consent enforcement and successful backend receipt are outside this review's current contract and must not be called regressions or completed features.
- Warn/error console collection at the end of the main-page interaction returned **[]**. This is only the tool-captured console for that tab, not proof of complete absence of browser/network failures.

### Separate privacy path: observed live

Clicking the form's “《隐私政策》” link navigated to `/privacy/`, title `PNPLINE · 隐私政策`, with an h1 and explicit design-preview text stating it is not the formal privacy policy. Its quote link returned to `/#quote`, where six fields remained present and the viewport remained 1280×720. No formal policy completeness or legal adequacy judgment is made.

## Contrast evidence and one additional concrete issue

Ratios below were computed from inspected CSS/live color values using sRGB relative luminance. They are source-color calculations, not pixel sampling or a full accessibility audit.

| Pair | Ratio |
| --- | ---: |
| Hero body `#424b50` on worst-case `#f2f2f2` (95% white panel over black) | 7.969:1 |
| Button text `#092f3b` on `#00abe1` | 5.341:1 |
| Muted body `#586166` on white | 6.332:1 |
| Volume hint `#5d6d74` on white | 5.378:1 |
| Consent `#4c5a60` on white | 7.146:1 |
| Submit helper `#596b72` on white | 5.569:1 |
| Placeholder `#68777d` on white | 4.642:1 |
| Error text `#ad3429` on white | 6.364:1 |
| Focus `#007da8` on white | 4.668:1 |
| Default input/select boundary `#aebbc0` on white | **1.968:1** |
| Hover boundary `#6c858f` on white | 3.897:1 |

**[P2] Default form-control boundaries are low contrast.** The inputs/selects and form share a white background, so the default 1px `#aebbc0` boundary provides the primary visible field perimeter, at only 1.968:1 against white. Live computed style matched this value, and the quote screenshot shows the faint borders. Hover and focus are stronger but do not help a user locate an unfocused field. A small correction can retain the existing visual direction and bring the default identifying border to at least 3:1 against white. This is source + rendered-state evidence; it was not emitted by the detector. Affects `style.css` input/select border rule (around line 113) and `field-line` in the documented palette. Suggested follow-up: `$impeccable audit` or focused polish. No P0/P1 is established by these B checks.

The 12px hint/consent/helper text is a factual sizing observation, not a contrast failure in these measured pairs. No claim is made about every text/background combination, inactive/selected controls, mobile video pixels, focus occlusion across all scroll positions, or complete WCAG conformance.

## Source-only fallback and untested conditions

- Reduced motion: source listens to `prefers-reduced-motion` and toggles `is-reduced`; CSS removes transitions/animations, hides video, changes journey height to auto and removes sticky. Current live body was not reduced. Actual OS preference change or emulated reduced-motion run was not performed; the exposed browser API did not offer media emulation and no OS setting was changed.
- Media failure: source error handler pauses video, sets `media-failed`, and CSS leaves poster/copy/actions while removing long scroll/sticky. No forced network/media failure was injected; read-only evaluate cannot safely perform that mutation, and no routing/failure-interception API was documented.
- Responsive: no viewport override was applied because another agent also uses the browser and B was expressly restricted to the current viewport. Mobile rules were read only. Mobile contrast/overflow, small-height behavior and 200% zoom require separate validation.
- Original video sequence fidelity: live duration/seek behavior confirmed, but B did not decode/hash-compare the derived video against the source edit. Current Chinese copy presence confirmed, not full manuscript equivalence.
- No real screen-reader session, touch-device session, automated performance trace, network capture, or all-keyboard full-form traversal was conducted.

## Run accounting for parent synthesis

| Item | Status |
| --- | --- |
| Target | Exact supplied source path used |
| Slug/persistence/trend | Parent orchestration responsibility; not rerun by B |
| Ignore file | `.impeccable/critique/ignore.md` absent when checked |
| Independence | A output not read; no findings sent early to parent/A |
| CLI | One real run, exit 2, complete JSON, counts/rules/file locations above |
| Browser inspection | Completed on own IAB tab at unchanged 1280×720 |
| Browser visibility | Hidden; visual inspection used native returned screenshots |
| Overlay injection | Unavailable, read-only evaluate; no overlay claimed |
| Overlay console findings | Not applicable; no injected detector |
| App console | Captured warn/error list empty at checked point |
| Live-server cleanup | No B server started; existing 7320 server left running |
| Temporary tab cleanup | B-created tab explicitly closed |
| Temporary files | None created beyond the two assigned deliverables |
| UI changes | None |

Questions skipped: Assessment B supplies evidence only; targeted critique questions belong to the parent's combined report.
