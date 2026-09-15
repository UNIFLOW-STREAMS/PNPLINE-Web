# Cinematic miniature finish

Shared finish for basic and high-angle desktop/mobile journey scenes, static keyframes and journey thumbnails. Intro artwork and its review keyframes are excluded.

- Linear-light exposure: 0.8, approximately −0.32 EV before the vignette.
- AgX contrast and gamut transform blended at 24% with the already display-referred source; saturation 96%. This is an SDR grade, not recovered HDR data.
- Visible navy-black vignette: corner opacity 76%, central subject left open.
- Screen-space tilt-shift DOF: 1.6–3.2 CSS px at top/bottom, clear central 30–74% band. The source images have no depth map; this does not claim physically based depth reconstruction.
- Fine monochrome grain: 13% soft-light, stepped movement only during playback, frozen while paused or with reduced motion.

The AgX matrices and polynomial curve follow the [Three.js AgX implementation](https://github.com/mrdoob/three.js/blob/dev/src/renderers/shaders/ShaderChunk/tonemapping_pars_fragment.glsl.js), itself based on Filament / Blender. The native SVG filter uses linear RGB, a sampled log/sigmoid transfer, outset, gamma and gamut conversion. Fallback grading is CSS brightness/saturation.

The image filter affects only artwork; captions and controls remain above the optics layers. Effects are turned off throughout the intro phase, including the underlying first journey image. Original image files are never rewritten.

Third-party reference: Three.js, MIT License, Copyright © 2010–2026 three.js authors. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
