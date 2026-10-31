$ErrorActionPreference = 'Stop'
$lookdevRoot = $PSScriptRoot
$blenderExecutable = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $blenderExecutable --background --factory-startup "$lookdevRoot/pnpline-hero-material-v001.blend" -t 6 --python-exit-code 1 --python "$lookdevRoot/scripts/render.py" -- --frames '0:990' --width 1920 --samples 128 --depth 16 --label production --device OPTIX
if ($LASTEXITCODE -ne 0) { throw 'Blender production render failed. See console output.' }
& ffmpeg -hide_banner -y -framerate 30 -start_number 0 -i "$lookdevRoot/review/production/f%04d.png" -frames:v 990 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart -an "$lookdevRoot/pnpline-hero-1080p.mp4"
if ($LASTEXITCODE -ne 0) { throw 'Video encoding failed.' }
