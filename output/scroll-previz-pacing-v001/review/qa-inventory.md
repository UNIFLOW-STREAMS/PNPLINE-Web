# QA inventory

- Positive C1 scroll mapping: dense numerical sampling, inverse roundtrip, exact endpoints, nonzero boundary derivative.
- Mode switch (paced/linear): same visible frame at toggle, different scroll positions; both reach first/last frame.
- Native wheel: slow progression, fast flick, reverse, sudden stop; record frame error and settling latency using rVFC.
- All scene boundaries and slow-zone edges/centres: seek to relevant scroll positions, settle, capture observations.
- Poster/loading/error: visible before first decoded frame; missing media retains readable static content and all scenes.
- Debug toggle: hidden/default, visible metrics, can hide; all seven scene buttons navigate correctly.
- Resize: same frame after desktop width change; coarse-pointer height-only change preserves scroll range; rotation recomputes layout.
- Reload: restores progress/mode; first frame paints at restored time.
- Reduced motion: no video download or scrubbing, static posters and normal content.
- Desktop/mobile layout: no horizontal overflow, film uses contain, no invented portrait source.
- Recording/screenshots: actual scroll run in Chromium, desktop and emulated mobile. Physical iOS and Safari are not claimed.
- Server Range: 206 with correct Content-Range; Blob URL reports seekable duration >0.
- Source preservation: source SHA checked before and after rendering; source file never saved by render script.

Off-path scenarios: reload midway through media loading, rapid reversal while decoder seeking, missing media, reduced-motion toggle at runtime.
