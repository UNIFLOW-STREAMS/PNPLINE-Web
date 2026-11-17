$ErrorActionPreference = 'Stop'
$job = $PSScriptRoot
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$source = 'F:/pnpline-landing/hero-section-video/hero-section-B-test-007-cream-aqua.blend'
$partial = Join-Path $job 'hero-test-007-cream-aqua-1080p.partial.mp4'
$final = Join-Path $job 'hero-test-007-cream-aqua-1080p.mp4'
function Set-Phase($phase, $detail) {
    @{phase=$phase; detail=$detail; updated=(Get-Date).ToString('o'); total_frames=990; output=$final; supervisor_pid=$PID} |
        ConvertTo-Json | Set-Content -LiteralPath "$job/status.json" -Encoding UTF8
}
try {

    Set-Phase 'rendering' 'Blender EEVEE, 1920x1080, 30 fps, frames 0-989'
    $argsRender = '-b --factory-startup --disable-autoexec "{0}" -o "{1}/frames/f####" -F PNG -x 1 -a' -f $source, $job
    $render = Start-Process -FilePath $blender -ArgumentList $argsRender -WorkingDirectory $job -WindowStyle Hidden -RedirectStandardOutput "$job/render.log" -RedirectStandardError "$job/render-errors.log" -PassThru -Wait
    if ($render.ExitCode -ne 0) { throw "Blender exited with code $($render.ExitCode). See render.log and render-errors.log." }
    for ($i = 0; $i -lt 990; $i++) {
        $frame = Get-Item -LiteralPath (Join-Path $job ('frames/f{0:D4}.png' -f $i))
        if ($frame.Length -lt 8) { throw "Empty or incomplete frame: $($frame.Name)" }
    }
    Set-Phase 'encoding' 'Encoding 990 frames into web-ready H.264 MP4'
    $binaryDir = 'C:/tmp/pnpline-render-ffmpeg/imageio_ffmpeg/binaries'
    $ffmpeg = (Get-ChildItem -LiteralPath $binaryDir -Filter '*.exe' -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
    if (!$ffmpeg) {
        $env:TEMP = 'C:\tmp'
        $env:TMP = 'C:\tmp'
        & 'C:/ProgramData/miniconda3/python.exe' -m pip install --no-cache-dir --disable-pip-version-check --no-deps --retries 5 --timeout 90 --target C:/tmp/pnpline-render-ffmpeg imageio-ffmpeg
        if ($LASTEXITCODE -ne 0) { throw 'FFmpeg setup failed. Rendered frames are available.' }
        $ffmpeg = (Get-ChildItem -LiteralPath $binaryDir -Filter '*.exe' | Select-Object -First 1).FullName
    }
    $argsEncode = '-hide_banner -nostdin -n -framerate 30 -start_number 0 -i "{0}/frames/f%04d.png" -frames:v 990 -vf "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1" -c:v libx264 -preset slow -crf 22 -profile:v high -level:v 4.1 -g 8 -keyint_min 8 -sc_threshold 0 -bf 0 -x264-params "open-gop=0" -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 -an -movflags +faststart "{1}"' -f $job, $partial
    $encoder = Start-Process -FilePath $ffmpeg -ArgumentList $argsEncode -WorkingDirectory $job -WindowStyle Hidden -RedirectStandardOutput "$job/encode-output.log" -RedirectStandardError "$job/encode.log" -PassThru -Wait
    if ($encoder.ExitCode -ne 0) { throw "FFmpeg exited with code $($encoder.ExitCode). See encode.log." }
    Move-Item -LiteralPath $partial -Destination $final
    Set-Phase 'complete' '1920x1080 H.264 MP4, 30 fps, 33 seconds'
} catch {
    Set-Phase 'failed' $_.Exception.Message
    throw
}

