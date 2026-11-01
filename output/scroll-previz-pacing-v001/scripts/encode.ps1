$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Push-Location $taskRoot
try {
  $renderLog = Get-Content -Raw -LiteralPath 'review/final-render.log'
  if ($renderLog -notmatch 'SOURCE_UNMODIFIED') { throw 'Render not complete; refusing to encode stale or incomplete frames.' }
  foreach ($frame in 0..989) { if (-not (Test-Path -LiteralPath ('frames/f{0:d4}.png' -f $frame))) { throw "Missing frame $frame" } }
  & ffmpeg -y -v warning -framerate 30 -start_number 0 -i 'frames/f%04d.png' -frames:v 990 -an -c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p -g 60 -keyint_min 60 -sc_threshold 0 -movflags +faststart 'assets/previz-source.mp4'
  if ($LASTEXITCODE -ne 0) { throw 'Source encode failed' }
  & ffmpeg -y -v warning -framerate 30 -start_number 0 -i 'frames/f%04d.png' -frames:v 990 -an -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -g 8 -keyint_min 8 -sc_threshold 0 -movflags +faststart 'assets/previz-scrub.mp4'
  if ($LASTEXITCODE -ne 0) { throw 'Scrub encode failed' }
  $posterFrames = @(0,110,240,390,570,740,920)
  for ($i=0;$i -lt $posterFrames.Count;$i++) {
    & ffmpeg -y -v error -i ('frames/f{0:d4}.png' -f $posterFrames[$i]) -frames:v 1 -q:v 2 ('assets/s{0}.jpg' -f ($i+1))
  }
  Copy-Item -LiteralPath 'assets/s1.jpg' -Destination 'assets/poster.jpg' -Force
  & python 'scripts/media_manifest.py'
  if ($LASTEXITCODE -ne 0) { throw 'Media manifest failed' }
} finally { Pop-Location }
