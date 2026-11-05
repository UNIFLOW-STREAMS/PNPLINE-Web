# Hero Section B — Cycles GPU web publication

Adopted source: `F:/pnpline-landing/hero-section-video/hero-section-B.blend`.
Source SHA-256: `65299a8273754bade3a47cc7dbf4f21e92a8e28ac4d6b0e48747a6e5556c55bb`.
The source is read-only throughout this delivery. Camera, DOF, lighting, background gradient,
geometry and source animation remain intact: CAM_MASTER, frames 0–989, 30 fps, 33 seconds.
The approved seven-section / 13-viewport scroll mapping runs in the website only.

## Deliverables and status

`audit/progress.json` is the pipeline status. `ready_for_browser_review` means encoding,
media checks, application to both apps and their production builds passed; browser QA is
recorded separately. Do not infer completion from an early benchmark or a partial frame folder.

- `hero-section-B-web.blend`: render-configured copy, source animation unchanged.
- `frames/f0000.png` … `f0989.png`: native 1920×1080 16-bit RGB PNG sequence.
- `assets/hero-b-v002-1080p.mp4`: desktop H.264, YUV420p, 30 fps, GOP 8, no B frames.
- `assets/hero-b-v002-720p.mp4`: compact-device H.264, 1280×720, GOP 4.
- `assets/hero-b-v002-poster.webp` / `hero-b-v002-final.webp`: matching actual endpoint frames.
- `assets/hero-b-v002-manifest.json`: hashes, sizes, encodes, measured render time and VMAF.
- `review/{ocean,us-port,warehouse}-30fps.mp4`: continuous two-second review extracts.
- `site-backup/{en,zh}/`: pre-application source backup; old media files are retained.

## Rendering

Blender 5.1, Cycles, RTX 4070 OptiX GPU, CPU device disabled. 96 maximum samples,
adaptive threshold 0.018, minimum 16, OpenImageDenoise with albedo and normal guides.
Stable seed 29, animated seed disabled. AgX / Medium High Contrast / exposure +0.3
are retained from B. The production PNG sequence remains 16-bit; web conversion uses
error-diffusion dithering, BT.709 matrix/range tags and fast-start MP4.

Initial 1080p benchmark: f132 25.50 s, f260 11.64 s, f780 28.11 s. Sequential frames
benefit from persistent data. Final measured timing is the sum of `review/frame-times.jsonl`;
GPU memory readings in `review/gpu-memory.csv` are total board usage, including other apps.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' `
  -b 'F:/pnpline-landing/hero-section-video/hero-section-B.blend' -t 12 `
  --python 'F:/pnpline-landing/hero-section-video/final/hero-section-b-web-v002/scripts/render.py' `
  -- --mode production --samples 96
python 'F:/pnpline-landing/hero-section-video/final/hero-section-b-web-v002/scripts/encode.py'
python 'F:/pnpline-landing/hero-section-video/final/hero-section-b-web-v002/scripts/sites.py' --apply
```

The render script resumes an existing frame sequence. Use a new output version to change
sampling or render settings, rather than mixing new settings into this sequence.

## Web implementation

English app: `C:/Users/KIM TAEHYUNG/.codex/visualizations/2026/11/01/01a19616-7090-7b72-86b1-f85ae4da029a/pnpline-web`.
Chinese app: `F:/pnpline-landing/output/pnpline-web-zh`.
Local URLs: http://127.0.0.1:3091/ and http://127.0.0.1:3092/.

Both use identical assets and numerical pacing, with localized seven-stage labels.
The existing reveal curtain is retained. Paused seeks are coalesced to the newest target;
muted inline priming is used on first interaction. Posters remain available before decode
and when reduced motion, Save-Data or a media error disables the film. Portrait keeps the
whole landscape composition with a blurred ambient extension; it is not a newly composed
portrait film. Stable viewport sizing avoids scroll-distance changes caused by phone toolbars.

Encoding budgets: desktop ≤32 MiB, compact ≤12 MiB, decoded VMAF mean ≥95 against
the same-size uncompressed source after identical color conversion. Both files must decode
to exactly 990 frames / 33 seconds, with no audio, fast-start metadata and bounded keyframe gaps.
Versioned file names receive immutable cache headers. Byte-range responses are checked on
the actual running servers during final browser QA.

For hosting, deploy each existing Next.js app with its `public/assets/video/hero-b-v002-*`
files together. Run `npm run build` and `npm start` from the respective app directory.
No production-domain deployment is implied by local application or a successful build.
