param([switch]$Execute)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path -LiteralPath 'F:/pnpline-landing/hero-section-video').Path.TrimEnd('\')
$reportRoot=$PSScriptRoot
$dependencies=Get-Content -LiteralPath (Join-Path $reportRoot 'preserved-dependencies.json') -Raw | ConvertFrom-Json
$keep=[System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$sourceAssets=[System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach($d in $dependencies){
    [void]$keep.Add([IO.Path]::GetFullPath($d.file))
    foreach($im in $d.images){[void]$sourceAssets.Add([IO.Path]::GetFullPath($im.path))}
    if($d.libraries.Count -gt 0){throw 'Linked libraries require dependency handling first.'}
    if((Get-FileHash -LiteralPath $d.file -Algorithm SHA256).Hash -ne $d.sha256){throw "Preserved file changed: $($d.file)"}
}
if($keep.Count -ne 4){throw 'Expected exactly four preserved files'}
function Assert-ScopedFile([string]$path){
    $full=[IO.Path]::GetFullPath($path)
    if(!$full.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Out of scope: $full"}
    if($keep.Contains($full) -or $sourceAssets.Contains($full)){throw "Protected path: $full"}
    $item=Get-Item -LiteralPath $full -Force
    if($item.PSIsContainer){throw "File expected: $full"}
    $cursor=$item
    while($cursor -and $cursor.FullName -ne $taskRoot){
        if($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse point: $($cursor.FullName)"}
        $cursor=if($cursor.PSIsContainer){$cursor.Parent}else{$cursor.Directory}
    }
    return $item
}
$planPath=Join-Path $reportRoot 'deletion-manifest.json'
if(!$Execute){
    $delete=[Collections.Generic.List[object]]::new()
    $preservedImages=[Collections.Generic.List[object]]::new()
    $files=Get-ChildItem -LiteralPath $taskRoot -File -Recurse -Force
    foreach($f in $files){
        $relative=$f.FullName.Substring($taskRoot.Length+1).Replace('\','/')
        $reason=$null
        if($f.Name -match '\.blend\d*$'){
            if(!$keep.Contains($f.FullName)){$reason=if($f.Extension -eq '.blend'){'obsolete_blend'}else{'blend_autobackup'}}
        }elseif($f.Extension -match '^\.(png|jpg|jpeg|exr|tif|tiff|webp)$'){
            $protect=$null
            if($sourceAssets.Contains($f.FullName)){$protect='source_texture'}
            elseif($relative -match '^(lookdev/test-(003|004|007|010)[^/]*/|final/hero-section-B-test-004[^/]*/|renders/test-004-toon/|final/hero-section-final/)'){$protect='preserved_version_render'}
            elseif($relative -match '(^|/)(assets|resources|textures|fonts|references|reference|inputs|boards|site-stage|node_modules|public|source)(/|$)'){$protect='source_or_web_asset'}
            elseif($relative -match '^lookdev/ink-(and-yard-revision|width-70)/' -and $f.Name -match '004'){$protect='preserved_004_render'}
            elseif($relative -match '^(concept-design|styleframe|prompts)/'){$protect='design_source'}
            elseif($relative -match '^storyboard/' -and $relative -notmatch '/(raw[^/]*|review|layout-proposal[^/]*)(/|$)'){$protect='storyboard_source'}
            if($protect){$preservedImages.Add([pscustomobject]@{path=$f.FullName;reason=$protect;bytes=$f.Length})}
            elseif($relative -match '^(blockout|lookdev|final|renders)/' -or ($relative -match '^storyboard/' -and $relative -match '/(raw[^/]*|review|layout-proposal[^/]*)(/|$)')){$reason='obsolete_render_or_review_frame'}
            else{$preservedImages.Add([pscustomobject]@{path=$f.FullName;reason='unclassified_keep';bytes=$f.Length})}
        }
        if($reason){$delete.Add([pscustomobject]@{path=$f.FullName;relative=$relative;reason=$reason;bytes=$f.Length;modifiedUtc=$f.LastWriteTimeUtc.ToString('o')})}
    }
    $delete | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $planPath -Encoding utf8
    $preservedImages | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reportRoot 'preserved-images.json') -Encoding utf8
    $summary=[pscustomobject]@{deleteCount=$delete.Count;deleteGiB=[math]::Round(($delete|Measure-Object bytes -Sum).Sum/1GB,2);byReason=@($delete|Group-Object reason|ForEach-Object{[pscustomobject]@{reason=$_.Name;count=$_.Count;GiB=[math]::Round(($_.Group|Measure-Object bytes -Sum).Sum/1GB,2)}});preservedImages=$preservedImages.Count;preservedBlends=@($keep)}
    $summary|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $reportRoot 'plan-summary.json') -Encoding utf8
    $summary|ConvertTo-Json -Depth 5
    exit
}
$plan=@(Get-Content -LiteralPath $planPath -Raw|ConvertFrom-Json)
# Validate every exact file and every ancestor before deleting any file.
foreach($entry in $plan){
    $item=Assert-ScopedFile $entry.path
    if($item.Length -ne $entry.bytes -or $item.LastWriteTimeUtc.Ticks -ne ([datetime]$entry.modifiedUtc).ToUniversalTime().Ticks){throw "File changed after planning: $($entry.path)"}
}
$deleted=0;$freed=[long]0
foreach($entry in $plan){
    Remove-Item -LiteralPath $entry.path -Force -ErrorAction Stop
    $deleted++;$freed+=$entry.bytes
    if($deleted % 5000 -eq 0){Write-Output "Deleted $deleted / $($plan.Count) files"}
}
$remaining=@(Get-ChildItem -LiteralPath $taskRoot -File -Recurse -Force|Where-Object{$_.Name -match '\.blend\d*$'})
if($remaining.Count -ne 4 -or @($remaining|Where-Object{!$keep.Contains($_.FullName)}).Count -gt 0){throw 'Unexpected Blender files remain'}
foreach($d in $dependencies){if((Get-FileHash -LiteralPath $d.file -Algorithm SHA256).Hash -ne $d.sha256){throw 'Preserved hash mismatch'}}
$result=[pscustomobject]@{deletedFiles=$deleted;freedBytes=$freed;freedGiB=[math]::Round($freed/1GB,2);remainingBlends=@($remaining.FullName);allFourPreservedHashesMatch=$true}
$result|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $reportRoot 'result.json') -Encoding utf8
$result|ConvertTo-Json -Depth 4
