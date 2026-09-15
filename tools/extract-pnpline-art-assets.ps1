[CmdletBinding()]
param(
    [uri]$BaseUrl = 'https://www.pnpline.com/',
    [string]$OutputRoot = (Join-Path (Get-Location).Path 'output\source-assets\pnpline.com'),
    [ValidateRange(0, 60000)][int]$ThrottleMilliseconds = 150,
    [ValidateRange(0, 100000)][int]$PageLimit = 0,
    [ValidateRange(0, 10000)][int]$WpMediaPageLimit = 0,
    [ValidateRange(1, 20)][int]$CssImportDepth = 3,
    [ValidateRange(1, 10000)][int]$MaxStylesheets = 500,
    [ValidateRange(1, 100000)][int]$MaxAssets = 2500,
    [ValidateRange(1, 2147483647)][long]$MaxFileBytes = 536870912,
    [ValidateRange(5, 300)][int]$RequestTimeoutSeconds = 30,
    [ValidateRange(5, 300)][int]$AssetRequestTimeoutSeconds = 20,
    [switch]$DownloadVariants,
    [switch]$Refresh
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 3.0

$script:StartedAt = [DateTimeOffset]::UtcNow
$script:UserAgent = 'Mozilla/5.0 (compatible; PNPLINE-public-art-inventory/1.0; +https://www.pnpline.com/)'
$script:BaseUri = [uri]$BaseUrl
$script:BaseHost = $script:BaseUri.DnsSafeHost.ToLowerInvariant()
$script:OutputRootFull = [System.IO.Path]::GetFullPath($OutputRoot)
$script:Errors = [System.Collections.Generic.List[object]]::new()
$script:Skipped = [System.Collections.Generic.List[object]]::new()
$script:SkipKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$script:CandidateGroups = [ordered]@{}
$script:InlineAssets = [ordered]@{}
$script:PageRecords = [System.Collections.Generic.List[object]]::new()
$script:FontIcons = [System.Collections.Generic.List[object]]::new()
$script:FontIconKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$script:RemoteMedia = [System.Collections.Generic.List[object]]::new()
$script:RemoteMediaKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$script:RequestCount = 0
$script:DiscoveredReferenceCount = 0
$script:DeduplicatedCount = 0
$script:Robots = [ordered]@{
    url = ([uri]::new($script:BaseUri, '/robots.txt')).AbsoluteUri
    status = 'not-checked'; httpStatus = $null; rules = @(); sitemaps = @(); error = $null
}
$script:Sitemap = [ordered]@{
    status = 'not-checked'; attempted = @(); used = @(); pageCount = 0; fallbackCrawl = $false
}
$script:WpRest = [ordered]@{
    url = ([uri]::new($script:BaseUri, '/wp-json/wp/v2/media')).AbsoluteUri
    status = 'not-checked'; pagesRead = 0; mediaItems = 0; error = $null
}

$handler = [System.Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $true
$handler.MaxAutomaticRedirections = 10
$handler.AutomaticDecompression = [System.Net.DecompressionMethods]::GZip -bor [System.Net.DecompressionMethods]::Deflate
$script:HttpClient = [System.Net.Http.HttpClient]::new($handler)
$script:HttpClient.Timeout = [TimeSpan]::FromSeconds($RequestTimeoutSeconds)
$script:HttpClient.DefaultRequestHeaders.UserAgent.ParseAdd($script:UserAgent)
$script:HttpClient.DefaultRequestHeaders.Accept.ParseAdd('*/*')

function Add-RunError {
    param([string]$Phase, [string]$Url, [Nullable[int]]$HttpStatus, [string]$Message)
    $script:Errors.Add([pscustomobject][ordered]@{
        phase = $Phase; url = $Url; httpStatus = $HttpStatus; error = $Message
        timestamp = [DateTimeOffset]::UtcNow.ToString('o')
    })
}

function Add-SkippedItem {
    param([string]$Url, [string]$Reason, [string]$Context, [string]$Referrer = '')
    $key = "$Reason|$Context|$Url|$Referrer"
    if ($script:SkipKeys.Add($key)) {
        $script:Skipped.Add([pscustomobject][ordered]@{
            url = $Url; reason = $Reason; context = $Context; referrer = $Referrer
        })
    }
}

function Get-StringSha256 {
    param([string]$Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally { $sha.Dispose() }
}

function Wait-RequestThrottle {
    if ($ThrottleMilliseconds -gt 0 -and $script:RequestCount -gt 0) { Start-Sleep -Milliseconds $ThrottleMilliseconds }
    $script:RequestCount++
}

function Invoke-TextRequest {
    param([uri]$Uri, [string]$Phase, [switch]$QuietFailure)
    $attempt = 0
    while ($attempt -lt 3) {
        $attempt++
        $response = $null
        try {
            Wait-RequestThrottle
            $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Get, $Uri)
            $response = $script:HttpClient.SendAsync($request, [System.Net.Http.HttpCompletionOption]::ResponseContentRead).GetAwaiter().GetResult()
            $status = [int]$response.StatusCode
            if ($status -eq 429 -and $attempt -lt 3) {
                $response.Dispose()
                Start-Sleep -Seconds ([Math]::Pow(2, $attempt))
                continue
            }
            $content = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            $headers = [ordered]@{}
            foreach ($header in $response.Headers) { $headers[$header.Key] = @($header.Value) -join ', ' }
            foreach ($header in $response.Content.Headers) { $headers[$header.Key] = @($header.Value) -join ', ' }
            return [pscustomobject]@{
                success = $response.IsSuccessStatusCode; status = $status
                finalUrl = $response.RequestMessage.RequestUri.AbsoluteUri
                contentType = if ($response.Content.Headers.ContentType) { $response.Content.Headers.ContentType.MediaType } else { '' }
                content = $content; headers = $headers; error = $null
            }
        } catch {
            if (-not $QuietFailure) { Add-RunError -Phase $Phase -Url $Uri.AbsoluteUri -HttpStatus $null -Message $_.Exception.Message }
            return [pscustomobject]@{
                success = $false; status = $null; finalUrl = $Uri.AbsoluteUri; contentType = ''
                content = ''; headers = @{}; error = $_.Exception.Message
            }
        } finally { if ($response) { $response.Dispose() } }
    }
}

function Resolve-ResourceUrl {
    param([string]$Value, [uri]$ContextUri)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    $decoded = [System.Net.WebUtility]::HtmlDecode($Value.Trim().Trim('"', "'"))
    if ($decoded -match '^(?i)(data|blob|javascript|mailto|tel):' -or $decoded.StartsWith('#')) { return $null }
    try {
        $resolved = [uri]::new($ContextUri, $decoded)
        if ($resolved.Scheme -notin @('http', 'https')) { return $null }
        $builder = [System.UriBuilder]::new($resolved)
        $builder.Fragment = ''
        return $builder.Uri
    } catch { return $null }
}

function ConvertTo-CanonicalPageUrl {
    param([uri]$Uri)
    $builder = [System.UriBuilder]::new($Uri)
    $builder.Fragment = ''
    if ($builder.Query) {
        $kept = [System.Collections.Generic.List[string]]::new()
        foreach ($part in $builder.Query.TrimStart('?').Split('&', [System.StringSplitOptions]::RemoveEmptyEntries)) {
            $name = [System.Uri]::UnescapeDataString(($part.Split('=', 2))[0])
            if ($name -notmatch '^(?i)(utm_.+|gclid|fbclid|mc_cid|mc_eid|_ga)$') { $kept.Add($part) }
        }
        $builder.Query = $kept -join '&'
    }
    return $builder.Uri.AbsoluteUri
}

function Test-SameSitePage {
    param([uri]$Uri)
    if ($Uri.DnsSafeHost -ine $script:BaseHost) { return $false }
    if ($Uri.AbsolutePath -match '(?i)^/(wp-admin|wp-login|wp-json|xmlrpc\.php|search|feed)(/|$)' -or
        $Uri.AbsolutePath -match '(?i)/(cart|checkout|my-account|customer-portal)(/|$)' -or
        $Uri.AbsolutePath -match '(?i)\.(?:jpe?g|png|webp|avif|gif|svg|ico|css|js|pdf|zip|mp4|webm|m4v)(?:$|/)') { return $false }
    if ($Uri.Query -match '(?i)(^|[?&])s=') { return $false }
    return $true
}

function Get-AttributeMap {
    param([string]$Tag)
    $map = [ordered]@{}
    $pattern = '(?is)(?<name>[a-z_:][a-z0-9_:.-]*)\s*=\s*(?:"(?<value>[^"]*)"|''(?<value>[^'']*)''|(?<value>[^\s>]+))'
    foreach ($match in [regex]::Matches($Tag, $pattern)) {
        $map[$match.Groups['name'].Value.ToLowerInvariant()] = [System.Net.WebUtility]::HtmlDecode($match.Groups['value'].Value)
    }
    return $map
}

function Get-SrcsetUrls {
    param([string]$Srcset)
    $values = [System.Collections.Generic.List[string]]::new()
    foreach ($item in $Srcset.Split(',')) {
        $candidate = ($item.Trim() -split '\s+')[0]
        if ($candidate) { $values.Add($candidate) }
    }
    return $values
}

function Get-OriginalCandidateUrl {
    param([uri]$ObservedUri)
    $uri = $ObservedUri
    $resourceHost = $uri.DnsSafeHost.ToLowerInvariant()
    if ($resourceHost -match '^i[0-9]+\.wp\.com$' -and $uri.AbsolutePath -match '^/www\.pnpline\.com(?<path>/.*)$') {
        $uri = [uri]("{0}://{1}{2}" -f $script:BaseUri.Scheme, $script:BaseUri.Authority, $Matches['path'])
    }
    $builder = [System.UriBuilder]::new($uri)
    if ($builder.Query) {
        $kept = [System.Collections.Generic.List[string]]::new()
        foreach ($part in $builder.Query.TrimStart('?').Split('&', [System.StringSplitOptions]::RemoveEmptyEntries)) {
            $name = [System.Uri]::UnescapeDataString(($part.Split('=', 2))[0])
            if ($name -notmatch '^(?i)(resize|fit|crop|w|h|width|height|quality|q|zoom|ssl)$') { $kept.Add($part) }
        }
        $builder.Query = $kept -join '&'
    }
    $builder.Path = [regex]::Replace($builder.Path, '-\d{2,5}x\d{2,5}(?=\.(?:jpe?g|png|webp|avif|gif)$)', '', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    return $builder.Uri.AbsoluteUri
}

function Test-UnsupportedResource {
    param([uri]$Uri)
    $resourceHost = $Uri.DnsSafeHost.ToLowerInvariant()
    if ($resourceHost -match '(?i)(google-analytics|googletagmanager|doubleclick|facebook\.com|connect\.facebook|hotjar|clarity\.ms)') { return 'tracking-resource' }
    if ($resourceHost -match '(?i)(youtube\.com|youtu\.be|vimeo\.com|player\.vimeo\.com)') { return 'third-party-streaming' }
    if ($Uri.AbsolutePath -match '(?i)\.(?:woff2?|ttf|otf|eot)(?:$|/)') { return 'font-file' }
    if ($Uri.AbsolutePath -match '(?i)\.(?:js|mjs|css|html?|php|pdf|docx?|xlsx?|pptx?|zip|rar|7z)(?:$|/)') { return 'unsupported-file-type' }
    if ($Uri.DnsSafeHost -in @('forwarding.pnpline.com', 'b2b.pnpline.com')) { return 'excluded-service-host' }
    return ''
}

function Add-AssetReference {
    param([string]$ObservedUrl, [uri]$ContextUri, [string]$PageUrl, [string]$Method, [string]$Alt = '')
    $resolved = Resolve-ResourceUrl -Value $ObservedUrl -ContextUri $ContextUri
    if (-not $resolved) {
        if ($ObservedUrl -and $ObservedUrl -notmatch '^(?i)(data|blob):') { Add-SkippedItem -Url $ObservedUrl -Reason 'invalid-or-non-http-url' -Context $Method -Referrer $PageUrl }
        return
    }
    $unsupported = Test-UnsupportedResource -Uri $resolved
    if ($unsupported) { Add-SkippedItem -Url $resolved.AbsoluteUri -Reason $unsupported -Context $Method -Referrer $PageUrl; return }
    $familyKey = Get-OriginalCandidateUrl -ObservedUri $resolved
    if (-not $script:CandidateGroups.Contains($familyKey)) {
        if ($script:CandidateGroups.Count -ge $MaxAssets) { Add-SkippedItem -Url $resolved.AbsoluteUri -Reason 'max-assets-limit' -Context $Method -Referrer $PageUrl; return }
        $script:CandidateGroups[$familyKey] = [pscustomobject]@{
            key = $familyKey; canonicalUrl = $familyKey
            refs = [System.Collections.Generic.List[object]]::new()
            variants = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        }
    }
    $group = $script:CandidateGroups[$familyKey]
    [void]$group.variants.Add($resolved.AbsoluteUri)
    $refKey = "$($resolved.AbsoluteUri)|$PageUrl|$Method|$Alt"
    if (-not @($group.refs | Where-Object { $_.key -eq $refKey }).Count) {
        $group.refs.Add([pscustomobject]@{ key = $refKey; observedUrl = $resolved.AbsoluteUri; pageUrl = $PageUrl; method = $Method; alt = $Alt })
        $script:DiscoveredReferenceCount++
    }
}

function Add-RemoteMediaReference {
    param([string]$Url, [string]$PageUrl, [string]$Method)
    $key = "$Url|$PageUrl|$Method"
    if ($script:RemoteMediaKeys.Add($key)) {
        $script:RemoteMedia.Add([pscustomobject][ordered]@{ url = $Url; pageUrl = $PageUrl; method = $Method; downloadStatus = 'reference-only' })
        Add-SkippedItem -Url $Url -Reason 'third-party-streaming-reference-only' -Context $Method -Referrer $PageUrl
    }
}

function Add-InlineSvg {
    param([string]$Svg, [string]$PageUrl, [int]$Index)
    $trimmed = $Svg.Trim()
    if (-not $trimmed) { return }
    $hash = Get-StringSha256 -Value $trimmed
    if (-not $script:InlineAssets.Contains($hash)) {
        $script:InlineAssets[$hash] = [pscustomobject]@{
            hash = $hash; content = $trimmed
            pages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
            observed = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        }
    }
    [void]$script:InlineAssets[$hash].pages.Add($PageUrl)
    [void]$script:InlineAssets[$hash].observed.Add("$PageUrl#inline-svg-$Index")
    $script:DiscoveredReferenceCount++
}

function Read-RobotsPolicy {
    $robotsUri = [uri]$script:Robots.url
    $result = Invoke-TextRequest -Uri $robotsUri -Phase 'robots' -QuietFailure
    $script:Robots.httpStatus = $result.status
    if (-not $result.success) {
        $script:Robots.status = 'unavailable'
        $script:Robots.error = if ($result.error) { $result.error } else { "HTTP $($result.status)" }
        Add-RunError -Phase 'robots' -Url $robotsUri.AbsoluteUri -HttpStatus $result.status -Message $script:Robots.error
        return
    }
    $script:Robots.status = 'read'
    $activeForWildcard = $false
    $rules = [System.Collections.Generic.List[object]]::new()
    $sitemaps = [System.Collections.Generic.List[string]]::new()
    foreach ($rawLine in ($result.content -split "`n")) {
        $line = ($rawLine -replace '#.*$', '').Trim()
        if (-not $line -or $line -notmatch '^(?<name>[^:]+):\s*(?<value>.*)$') { continue }
        $name = $Matches['name'].Trim().ToLowerInvariant()
        $value = $Matches['value'].Trim()
        if ($name -eq 'user-agent') { $activeForWildcard = ($value -eq '*'); continue }
        if ($name -eq 'sitemap' -and $value) { $sitemaps.Add($value); continue }
        if ($activeForWildcard -and $name -in @('allow', 'disallow') -and $value) {
            $rules.Add([pscustomobject]@{ directive = $name; path = $value })
        }
    }
    $script:Robots.rules = @($rules)
    $script:Robots.sitemaps = @($sitemaps)
}

function Test-RobotsAllowed {
    param([uri]$Uri)
    if ($script:Robots.status -ne 'read' -or $Uri.DnsSafeHost -ine $script:BaseHost) { return $true }
    $target = $Uri.PathAndQuery
    $winner = $null
    foreach ($rule in $script:Robots.rules) {
        if ($target.StartsWith($rule.path, [System.StringComparison]::OrdinalIgnoreCase)) {
            if (-not $winner -or $rule.path.Length -gt $winner.path.Length -or
                ($rule.path.Length -eq $winner.path.Length -and $rule.directive -eq 'allow')) { $winner = $rule }
        }
    }
    return (-not $winner -or $winner.directive -eq 'allow')
}

function Discover-SitemapPages {
    $candidateUrls = [System.Collections.Generic.List[string]]::new()
    foreach ($url in $script:Robots.sitemaps) { if (-not $candidateUrls.Contains($url)) { $candidateUrls.Add($url) } }
    foreach ($path in @('/wp-sitemap.xml', '/sitemap_index.xml', '/sitemap.xml')) {
        $url = ([uri]::new($script:BaseUri, $path)).AbsoluteUri
        if (-not $candidateUrls.Contains($url)) { $candidateUrls.Add($url) }
    }
    $pending = [System.Collections.Generic.Queue[string]]::new()
    foreach ($url in $candidateUrls) { $pending.Enqueue($url) }
    $visited = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $pages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    while ($pending.Count -gt 0 -and $visited.Count -lt 100) {
        $url = $pending.Dequeue()
        if (-not $visited.Add($url)) { continue }
        $script:Sitemap.attempted += $url
        $uri = Resolve-ResourceUrl -Value $url -ContextUri $script:BaseUri
        if (-not $uri) { continue }
        $result = Invoke-TextRequest -Uri $uri -Phase 'sitemap' -QuietFailure
        if (-not $result.success -or $result.content -notmatch '<(?:sitemapindex|urlset)(?:\s|>)') { continue }
        $script:Sitemap.used += $result.finalUrl
        try { [xml]$xml = $result.content } catch {
            Add-RunError -Phase 'sitemap-parse' -Url $result.finalUrl -HttpStatus $result.status -Message $_.Exception.Message
            continue
        }
        if ($xml.DocumentElement.LocalName -eq 'sitemapindex') {
            foreach ($node in $xml.SelectNodes('//*[local-name()="sitemap"]/*[local-name()="loc"]')) {
                if ($node.InnerText.Trim()) { $pending.Enqueue($node.InnerText.Trim()) }
            }
        } elseif ($xml.DocumentElement.LocalName -eq 'urlset') {
            foreach ($node in $xml.SelectNodes('//*[local-name()="url"]/*[local-name()="loc"]')) {
                $pageUri = Resolve-ResourceUrl -Value $node.InnerText.Trim() -ContextUri $script:BaseUri
                if ($pageUri -and (Test-SameSitePage -Uri $pageUri) -and (Test-RobotsAllowed -Uri $pageUri)) {
                    [void]$pages.Add((ConvertTo-CanonicalPageUrl -Uri $pageUri))
                }
            }
        }
    }
    $script:Sitemap.status = if ($pages.Count -gt 0) { 'used' } else { 'unavailable-or-empty' }
    $script:Sitemap.pageCount = $pages.Count
    return @($pages)
}

function Register-FontIcons {
    param([string]$Html, [string]$PageUrl, [string[]]$Stylesheets)
    foreach ($tag in [regex]::Matches($Html, '(?is)<[a-z][^>]*\bclass\s*=\s*(?:"[^"]*"|''[^'']*'')[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tag.Value
        if (-not $attrs.Contains('class')) { continue }
        $classes = @($attrs['class'] -split '\s+' | Where-Object { $_ -match '^(?i)(fa[srbld]?|fa|eicon|icon)-[a-z0-9_-]+$' })
        foreach ($iconClass in $classes) {
            $element = ([regex]::Match($tag.Value, '^<\s*(?<name>[a-z0-9:-]+)', 'IgnoreCase')).Groups['name'].Value
            $key = "$PageUrl|$element|$iconClass"
            if ($script:FontIconKeys.Add($key)) {
                $script:FontIcons.Add([pscustomobject][ordered]@{
                    pageUrl = $PageUrl; element = $element; elementClass = $attrs['class']
                    iconClass = $iconClass; stylesheetUrls = @($Stylesheets)
                })
            }
        }
    }
}

function Register-CssUrls {
    param([string]$Css, [uri]$CssUri, [string[]]$PageUrls, [hashtable]$CssContexts, [int]$Depth)
    foreach ($import in [regex]::Matches($Css, '(?is)@import\s+(?:url\(\s*)?["'']?(?<url>[^\s"'')]+)')) {
        $importUri = Resolve-ResourceUrl -Value $import.Groups['url'].Value -ContextUri $CssUri
        if (-not $importUri) { continue }
        if ($Depth -ge $CssImportDepth) {
            Add-SkippedItem -Url $importUri.AbsoluteUri -Reason 'css-import-depth-limit' -Context 'css-import' -Referrer $CssUri.AbsoluteUri
            continue
        }
        if (-not $CssContexts.ContainsKey($importUri.AbsoluteUri)) {
            $CssContexts[$importUri.AbsoluteUri] = [pscustomobject]@{
                pages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
                depth = $Depth + 1
            }
        }
        foreach ($page in $PageUrls) { [void]$CssContexts[$importUri.AbsoluteUri].pages.Add($page) }
    }
    foreach ($match in [regex]::Matches($Css, '(?is)url\(\s*(?:"(?<url>[^"]+)"|''(?<url>[^'']+)''|(?<url>[^)]+))\s*\)')) {
        foreach ($page in $PageUrls) {
            Add-AssetReference -ObservedUrl $match.Groups['url'].Value.Trim() -ContextUri $CssUri -PageUrl $page -Method 'css-url'
        }
    }
}

function Process-HtmlAssets {
    param([string]$Html, [uri]$PageUri, [string]$PageUrl, [hashtable]$CssContexts)
    $pageStylesheets = [System.Collections.Generic.List[string]]::new()
    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<link\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $rel = if ($attrs.Contains('rel')) { $attrs['rel'].ToLowerInvariant() } else { '' }
        $href = if ($attrs.Contains('href')) { $attrs['href'] } else { '' }
        if (-not $href) { continue }
        if ($rel -match '(^|\s)stylesheet(\s|$)') {
            $cssUri = Resolve-ResourceUrl -Value $href -ContextUri $PageUri
            if ($cssUri) {
                $pageStylesheets.Add($cssUri.AbsoluteUri)
                if (-not $CssContexts.ContainsKey($cssUri.AbsoluteUri)) {
                    $CssContexts[$cssUri.AbsoluteUri] = [pscustomobject]@{
                        pages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase); depth = 0
                    }
                }
                [void]$CssContexts[$cssUri.AbsoluteUri].pages.Add($PageUrl)
            }
        }
        if ($rel -match '(?i)(^|\s)(icon|shortcut|apple-touch-icon|mask-icon|image_src)(\s|$)') {
            $method = if ($rel -match 'mask-icon') { 'mask-icon' } elseif ($rel -match 'image_src') { 'image-src-link' } else { 'link-icon' }
            Add-AssetReference -ObservedUrl $href -ContextUri $PageUri -PageUrl $PageUrl -Method $method
        }
    }

    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<img\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $alt = if ($attrs.Contains('alt')) { $attrs['alt'] } else { '' }
        foreach ($name in @('src', 'data-src', 'data-lazy-src', 'data-original', 'data-image', 'data-url')) {
            if ($attrs.Contains($name)) { Add-AssetReference -ObservedUrl $attrs[$name] -ContextUri $PageUri -PageUrl $PageUrl -Method "img-$name" -Alt $alt }
        }
        foreach ($name in @('srcset', 'data-srcset', 'data-lazy-srcset')) {
            if ($attrs.Contains($name)) {
                foreach ($url in Get-SrcsetUrls -Srcset $attrs[$name]) { Add-AssetReference -ObservedUrl $url -ContextUri $PageUri -PageUrl $PageUrl -Method $name -Alt $alt }
            }
        }
        foreach ($name in $attrs.Keys) {
            if ($name -like 'data-*' -and $name -match '(?i)(src|image|original|lazy)' -and
                $name -notin @('data-src', 'data-lazy-src', 'data-original', 'data-image', 'data-srcset', 'data-lazy-srcset') -and
                $attrs[$name] -match '(?i)(https?:|/|\.(?:jpe?g|png|webp|avif|gif|svg|ico))') {
                if ($name -match 'srcset') {
                    foreach ($url in Get-SrcsetUrls -Srcset $attrs[$name]) { Add-AssetReference -ObservedUrl $url -ContextUri $PageUri -PageUrl $PageUrl -Method "img-$name" -Alt $alt }
                } else { Add-AssetReference -ObservedUrl $attrs[$name] -ContextUri $PageUri -PageUrl $PageUrl -Method "img-$name" -Alt $alt }
            }
        }
    }

    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<source\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $isVideo = $attrs.Contains('type') -and $attrs['type'] -match '^video/'
        if ($attrs.Contains('src')) { Add-AssetReference -ObservedUrl $attrs['src'] -ContextUri $PageUri -PageUrl $PageUrl -Method $(if ($isVideo) { 'video-source' } else { 'picture-source' }) }
        if ($attrs.Contains('srcset')) { foreach ($url in Get-SrcsetUrls -Srcset $attrs['srcset']) { Add-AssetReference -ObservedUrl $url -ContextUri $PageUri -PageUrl $PageUrl -Method 'srcset' } }
    }
    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<video\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        if ($attrs.Contains('src')) { Add-AssetReference -ObservedUrl $attrs['src'] -ContextUri $PageUri -PageUrl $PageUrl -Method 'video' }
        if ($attrs.Contains('poster')) { Add-AssetReference -ObservedUrl $attrs['poster'] -ContextUri $PageUri -PageUrl $PageUrl -Method 'poster' }
    }
    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<(?:object|embed)\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $value = if ($attrs.Contains('data')) { $attrs['data'] } elseif ($attrs.Contains('src')) { $attrs['src'] } else { '' }
        $mime = if ($attrs.Contains('type')) { $attrs['type'] } else { '' }
        if ($value -and ($mime -match '^(?i)(image|video)/' -or $value -match '(?i)\.(?:jpe?g|png|webp|avif|gif|svg|ico|mp4|webm|m4v)(?:[?#]|$)')) {
            Add-AssetReference -ObservedUrl $value -ContextUri $PageUri -PageUrl $PageUrl -Method 'object-embed'
        }
    }

    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<meta\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $name = if ($attrs.Contains('property')) { $attrs['property'] } elseif ($attrs.Contains('name')) { $attrs['name'] } else { '' }
        if ($name -match '^(?i)(og:image(?::(?:url|secure_url))?|twitter:image(?::src)?)$' -and $attrs.Contains('content')) {
            Add-AssetReference -ObservedUrl $attrs['content'] -ContextUri $PageUri -PageUrl $PageUrl -Method 'og-image'
        }
    }
    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<(?:use|image)\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        $href = if ($attrs.Contains('href')) { $attrs['href'] } elseif ($attrs.Contains('xlink:href')) { $attrs['xlink:href'] } else { '' }
        if ($href -and -not $href.StartsWith('#')) { Add-AssetReference -ObservedUrl $href.Split('#')[0] -ContextUri $PageUri -PageUrl $PageUrl -Method 'svg-external' }
    }
    $svgIndex = 0
    foreach ($svgMatch in [regex]::Matches($Html, '(?is)<svg\b[^>]*>.*?</svg\s*>')) { $svgIndex++; Add-InlineSvg -Svg $svgMatch.Value -PageUrl $PageUrl -Index $svgIndex }
    foreach ($styleMatch in [regex]::Matches($Html, '(?is)<style\b[^>]*>(?<css>.*?)</style\s*>')) {
        Register-CssUrls -Css $styleMatch.Groups['css'].Value -CssUri $PageUri -PageUrls @($PageUrl) -CssContexts $CssContexts -Depth 0
    }
    foreach ($tagMatch in [regex]::Matches($Html, '(?is)<[a-z][^>]*\bstyle\s*=\s*(?:"[^"]*"|''[^'']*'')[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $tagMatch.Value
        if ($attrs.Contains('style')) { Register-CssUrls -Css $attrs['style'] -CssUri $PageUri -PageUrls @($PageUrl) -CssContexts $CssContexts -Depth 0 }
    }
    foreach ($iframeMatch in [regex]::Matches($Html, '(?is)<iframe\b[^>]*>')) {
        $attrs = Get-AttributeMap -Tag $iframeMatch.Value
        if ($attrs.Contains('src')) {
            $remoteUri = Resolve-ResourceUrl -Value $attrs['src'] -ContextUri $PageUri
            if ($remoteUri -and $remoteUri.DnsSafeHost -match '(?i)(youtube\.com|youtu\.be|vimeo\.com|player\.vimeo\.com)') {
                Add-RemoteMediaReference -Url $remoteUri.AbsoluteUri -PageUrl $PageUrl -Method 'iframe'
            }
        }
    }
    Register-FontIcons -Html $Html -PageUrl $PageUrl -Stylesheets @($pageStylesheets)
}

function Register-WpMedia {
    $pageNumber = 1
    $maxPages = if ($WpMediaPageLimit -gt 0) { $WpMediaPageLimit } elseif ($PageLimit -gt 0) { 1 } else { [int]::MaxValue }
    while ($pageNumber -le $maxPages) {
        $fields = 'id,source_url,mime_type,media_details,alt_text,link'
        $uri = [uri]::new($script:BaseUri, "/wp-json/wp/v2/media?per_page=100&page=$pageNumber&_fields=$fields")
        $result = Invoke-TextRequest -Uri $uri -Phase 'wp-rest' -QuietFailure
        if (-not $result.success) {
            if ($pageNumber -eq 1) {
                $script:WpRest.status = 'unavailable'
                $script:WpRest.error = if ($result.error) { $result.error } else { "HTTP $($result.status)" }
                Add-RunError -Phase 'wp-rest' -Url $uri.AbsoluteUri -HttpStatus $result.status -Message $script:WpRest.error
            }
            break
        }
        try { $items = @($result.content | ConvertFrom-Json) } catch {
            $script:WpRest.status = 'parse-error'; $script:WpRest.error = $_.Exception.Message
            Add-RunError -Phase 'wp-rest-parse' -Url $uri.AbsoluteUri -HttpStatus $result.status -Message $_.Exception.Message
            break
        }
        $script:WpRest.status = 'read'; $script:WpRest.pagesRead++; $script:WpRest.mediaItems += $items.Count
        foreach ($item in $items) {
            $pageRef = if ($item.link) { [string]$item.link } else { $script:BaseUri.AbsoluteUri }
            $alt = [string]$item.alt_text
            if ($item.source_url) { Add-AssetReference -ObservedUrl ([string]$item.source_url) -ContextUri $script:BaseUri -PageUrl $pageRef -Method 'wp-media' -Alt $alt }
            $sizesProperty = if ($item.media_details) { $item.media_details.PSObject.Properties['sizes'] } else { $null }
            if ($sizesProperty -and $sizesProperty.Value) {
                foreach ($property in $sizesProperty.Value.PSObject.Properties) {
                    $sourceProperty = $property.Value.PSObject.Properties['source_url']
                    if ($sourceProperty -and $sourceProperty.Value) {
                        Add-AssetReference -ObservedUrl ([string]$sourceProperty.Value) -ContextUri $script:BaseUri -PageUrl $pageRef -Method 'wp-media-variant' -Alt $alt
                    }
                }
            }
        }
        $totalPages = 0
        if ($result.headers.Contains('X-WP-TotalPages')) { [void][int]::TryParse([string]$result.headers['X-WP-TotalPages'], [ref]$totalPages) }
        if ($items.Count -eq 0 -or ($totalPages -gt 0 -and $pageNumber -ge $totalPages)) { break }
        if ($script:CandidateGroups.Count -ge $MaxAssets) {
            Add-SkippedItem -Url $uri.AbsoluteUri -Reason 'wp-media-stopped-at-max-assets' -Context 'wp-rest'
            break
        }
        $pageNumber++
    }
}

function Get-ExtensionFromMime {
    param([string]$Mime, [string]$Url)
    $cleanMime = ($Mime -split ';')[0].Trim().ToLowerInvariant()
    $map = @{
        'image/jpeg' = 'jpg'; 'image/png' = 'png'; 'image/webp' = 'webp'; 'image/avif' = 'avif'
        'image/gif' = 'gif'; 'image/svg+xml' = 'svg'; 'image/x-icon' = 'ico'; 'image/vnd.microsoft.icon' = 'ico'
        'video/mp4' = 'mp4'; 'video/webm' = 'webm'; 'video/x-m4v' = 'm4v'; 'video/quicktime' = 'mov'
    }
    if ($map.ContainsKey($cleanMime)) { return $map[$cleanMime] }
    try {
        $extension = [System.IO.Path]::GetExtension(([uri]$Url).AbsolutePath).TrimStart('.').ToLowerInvariant()
        if ($extension -eq 'jpeg') { return 'jpg' }
        if ($extension -in @('jpg', 'png', 'webp', 'avif', 'gif', 'svg', 'ico', 'mp4', 'webm', 'm4v', 'mov')) { return $extension }
    } catch {}
    return ''
}

function Get-AssetType {
    param([string]$Mime, [string]$Extension, [string[]]$Methods)
    if ($Mime -match '^video/' -or $Extension -in @('mp4', 'webm', 'm4v', 'mov')) { return 'video' }
    if ($Extension -in @('svg', 'ico') -or @($Methods | Where-Object { $_ -match '(icon|svg|mask)' }).Count -gt 0) { return 'icon' }
    return 'image'
}

function Test-AllowedDownloadedType {
    param([string]$Mime, [string]$Extension)
    if ($Mime -match '^(?i)text/html|application/xhtml|text/css|application/javascript|text/javascript|application/pdf') { return $false }
    return ($Mime -match '^(?i)(image|video)/' -and $Extension) -or
        ($Extension -in @('jpg', 'png', 'webp', 'avif', 'gif', 'svg', 'ico', 'mp4', 'webm', 'm4v', 'mov'))
}

function Invoke-AssetDownload {
    param([string[]]$CandidateUrls, [string]$TempPath)
    $lastFailure = $null
    foreach ($candidateUrl in $CandidateUrls) {
        $attempt = 0
        while ($attempt -lt 3) {
            $attempt++
            $response = $null
            $cancellation = [System.Threading.CancellationTokenSource]::new([TimeSpan]::FromSeconds($AssetRequestTimeoutSeconds))
            try {
                Wait-RequestThrottle
                $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Get, [uri]$candidateUrl)
                $response = $script:HttpClient.SendAsync($request, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead, $cancellation.Token).GetAwaiter().GetResult()
                $status = [int]$response.StatusCode
                if ($status -eq 429 -and $attempt -lt 3) {
                    $response.Dispose(); Start-Sleep -Seconds ([Math]::Pow(2, $attempt)); continue
                }
                if (-not $response.IsSuccessStatusCode) {
                    $lastFailure = [pscustomobject]@{ url = $candidateUrl; status = $status; message = "HTTP $status" }; break
                }
                $length = $response.Content.Headers.ContentLength
                if ($length -and $length -gt $MaxFileBytes) {
                    $lastFailure = [pscustomobject]@{ url = $candidateUrl; status = $status; message = "Content-Length $length exceeds MaxFileBytes $MaxFileBytes" }; break
                }
                $mime = if ($response.Content.Headers.ContentType) { $response.Content.Headers.ContentType.MediaType } else { '' }
                $extension = Get-ExtensionFromMime -Mime $mime -Url $response.RequestMessage.RequestUri.AbsoluteUri
                if (-not (Test-AllowedDownloadedType -Mime $mime -Extension $extension)) {
                    $lastFailure = [pscustomobject]@{ url = $candidateUrl; status = $status; message = "Unsupported response type '$mime'" }; break
                }
                $inputStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
                $outputStream = [System.IO.File]::Open($TempPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
                try {
                    [void]$inputStream.CopyToAsync($outputStream, $cancellation.Token).GetAwaiter().GetResult()
                } finally {
                    $outputStream.Dispose()
                    $inputStream.Dispose()
                }
                $fileInfo = [System.IO.FileInfo]::new($TempPath)
                if ($fileInfo.Length -gt $MaxFileBytes) {
                    Remove-Item -LiteralPath $TempPath -Force
                    $lastFailure = [pscustomobject]@{ url = $candidateUrl; status = $status; message = "Downloaded size $($fileInfo.Length) exceeds MaxFileBytes $MaxFileBytes" }; break
                }
                return [pscustomobject]@{
                    success = $true; observedAttemptUrl = $candidateUrl
                    finalUrl = $response.RequestMessage.RequestUri.AbsoluteUri; status = $status
                    mime = $mime; extension = $extension; byteSize = $fileInfo.Length; error = $null
                }
            } catch {
                $lastFailure = [pscustomobject]@{ url = $candidateUrl; status = $null; message = $_.Exception.Message }
                break
            } finally {
                if ($response) { $response.Dispose() }
                $cancellation.Dispose()
            }
        }
    }
    return [pscustomobject]@{
        success = $false; observedAttemptUrl = if ($lastFailure) { $lastFailure.url } else { '' }; finalUrl = ''
        status = if ($lastFailure) { $lastFailure.status } else { $null }; mime = ''; extension = ''; byteSize = 0
        error = if ($lastFailure) { $lastFailure.message } else { 'No candidate URL was available.' }
    }
}

function Merge-UniqueStrings {
    param([object[]]$Collections)
    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($collection in $Collections) {
        foreach ($value in @($collection)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$value)) { [void]$set.Add([string]$value) }
        }
    }
    return @($set | Sort-Object)
}

function Write-JsonFile {
    param([string]$Path, [object]$Value)
    $json = $Value | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Get-RelativeManifestPath {
    param([string]$FullPath)
    return [System.IO.Path]::GetRelativePath($script:OutputRootFull, $FullPath).Replace('\', '/')
}

try {
    $directories = @(
        $script:OutputRootFull,
        (Join-Path $script:OutputRootFull 'assets\images'),
        (Join-Path $script:OutputRootFull 'assets\videos'),
        (Join-Path $script:OutputRootFull 'assets\icons'),
        (Join-Path $script:OutputRootFull 'assets\inline-svg'),
        (Join-Path $script:OutputRootFull '.partial')
    )
    foreach ($directory in $directories) { [System.IO.Directory]::CreateDirectory($directory) | Out-Null }

    Write-Host "Reading robots policy: $($script:Robots.url)"
    Read-RobotsPolicy
    Write-Host 'Discovering public pages from sitemaps'
    $discoveredPages = @(Discover-SitemapPages)
    $useFallback = ($discoveredPages.Count -lt 2)
    $script:Sitemap.fallbackCrawl = $useFallback
    $pageQueue = [System.Collections.Generic.Queue[string]]::new()
    $basePageUrl = ConvertTo-CanonicalPageUrl -Uri $script:BaseUri
    $pageQueue.Enqueue($basePageUrl)
    foreach ($page in ($discoveredPages | Sort-Object)) {
        if ($page -ne $basePageUrl) { $pageQueue.Enqueue($page) }
    }
    $visitedPages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $cssContexts = @{}

    while ($pageQueue.Count -gt 0 -and ($PageLimit -eq 0 -or $script:PageRecords.Count -lt $PageLimit)) {
        $requestedUrl = $pageQueue.Dequeue()
        if (-not $visitedPages.Add($requestedUrl)) { continue }
        $pageUri = [uri]$requestedUrl
        if (-not (Test-RobotsAllowed -Uri $pageUri)) {
            Add-SkippedItem -Url $requestedUrl -Reason 'robots-disallow' -Context 'page-crawl'; continue
        }
        Write-Host "Crawling page $($script:PageRecords.Count + 1): $requestedUrl"
        $result = Invoke-TextRequest -Uri $pageUri -Phase 'page'
        $crawlTimestamp = [DateTimeOffset]::UtcNow.ToString('o')
        $canonical = $requestedUrl
        if ($result.success -and $result.contentType -match '^(?i)text/html|application/xhtml') {
            foreach ($linkMatch in [regex]::Matches($result.content, '(?is)<link\b[^>]*>')) {
                $attrs = Get-AttributeMap -Tag $linkMatch.Value
                if ($attrs.Contains('rel') -and $attrs['rel'] -match '(?i)(^|\s)canonical(\s|$)' -and $attrs.Contains('href')) {
                    $canonicalUri = Resolve-ResourceUrl -Value $attrs['href'] -ContextUri ([uri]$result.finalUrl)
                    if ($canonicalUri) { $canonical = ConvertTo-CanonicalPageUrl -Uri $canonicalUri }
                    break
                }
            }
            Process-HtmlAssets -Html $result.content -PageUri ([uri]$result.finalUrl) -PageUrl $canonical -CssContexts $cssContexts
            if ($useFallback) {
                foreach ($anchorMatch in [regex]::Matches($result.content, '(?is)<a\b[^>]*>')) {
                    $attrs = Get-AttributeMap -Tag $anchorMatch.Value
                    if (-not $attrs.Contains('href')) { continue }
                    $linked = Resolve-ResourceUrl -Value $attrs['href'] -ContextUri ([uri]$result.finalUrl)
                    if ($linked -and (Test-SameSitePage -Uri $linked) -and (Test-RobotsAllowed -Uri $linked)) {
                        $linkedUrl = ConvertTo-CanonicalPageUrl -Uri $linked
                        if (-not $visitedPages.Contains($linkedUrl)) { $pageQueue.Enqueue($linkedUrl) }
                    }
                }
            }
        } elseif ($result.success) {
            Add-RunError -Phase 'page-content-type' -Url $requestedUrl -HttpStatus $result.status -Message "Expected HTML but received '$($result.contentType)'."
        }
        $script:PageRecords.Add([pscustomobject][ordered]@{
            url = $requestedUrl; canonicalUrl = $canonical
            crawlStatus = if ($result.success -and $result.contentType -match '^(?i)text/html|application/xhtml') { 'success' } else { 'failed' }
            httpStatus = $result.status; finalUrl = $result.finalUrl; assetIds = @(); crawlTimestamp = $crawlTimestamp
        })
    }

    Write-Host "Processing $($cssContexts.Count) discovered stylesheets"
    $processedCss = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    while ($true) {
        $nextCss = @($cssContexts.Keys | Where-Object { -not $processedCss.Contains($_) } | Select-Object -First 1)
        if ($nextCss.Count -eq 0) { break }
        if ($processedCss.Count -ge $MaxStylesheets) {
            Add-SkippedItem -Url '' -Reason 'max-stylesheets-limit' -Context 'stylesheet'
            break
        }
        $cssUrl = [string]$nextCss[0]
        [void]$processedCss.Add($cssUrl)
        $context = $cssContexts[$cssUrl]
        $result = Invoke-TextRequest -Uri ([uri]$cssUrl) -Phase 'css' -QuietFailure
        if (-not $result.success) {
            $message = if ($result.error) { $result.error } else { "HTTP $($result.status)" }
            Add-RunError -Phase 'css' -Url $cssUrl -HttpStatus $result.status -Message $message
            continue
        }
        if ($result.contentType -and $result.contentType -notmatch '(?i)(text/css|text/plain|application/octet-stream)') {
            Add-SkippedItem -Url $cssUrl -Reason 'unexpected-css-content-type' -Context 'stylesheet'; continue
        }
        Register-CssUrls -Css $result.content -CssUri ([uri]$result.finalUrl) -PageUrls @($context.pages) -CssContexts $cssContexts -Depth $context.depth
    }

    Write-Host 'Enumerating public WordPress media metadata'
    Register-WpMedia

    $assetsByHash = [ordered]@{}
    $failedAssets = [System.Collections.Generic.List[object]]::new()
    $partialRoot = Join-Path $script:OutputRootFull '.partial'
    $assetFamilyIndex = 0
    foreach ($group in $script:CandidateGroups.Values) {
        $assetFamilyIndex++
        if ($assetFamilyIndex -eq 1 -or $assetFamilyIndex % 25 -eq 0 -or $assetFamilyIndex -eq $script:CandidateGroups.Count) {
            Write-Host "Downloading asset family $assetFamilyIndex/$($script:CandidateGroups.Count)"
        }
        $observedUrls = @($group.variants | Sort-Object)
        $jobs = [System.Collections.Generic.List[object]]::new()
        $primaryCandidates = [System.Collections.Generic.List[string]]::new()
        $primaryCandidates.Add($group.canonicalUrl)
        $fallbackUrl = @($observedUrls | Where-Object { $_ -ne $group.canonicalUrl } | Select-Object -First 1)
        if ($fallbackUrl.Count -gt 0) { $primaryCandidates.Add([string]$fallbackUrl[0]) }
        $jobs.Add([pscustomobject]@{ isVariant = $false; labelUrl = $group.canonicalUrl; candidates = @($primaryCandidates) })
        if ($DownloadVariants) {
            foreach ($url in $observedUrls) {
                if ($url -ne $group.canonicalUrl) { $jobs.Add([pscustomobject]@{ isVariant = $true; labelUrl = $url; candidates = @($url) }) }
            }
        }

        foreach ($job in $jobs) {
            $tempPath = Join-Path $partialRoot (([guid]::NewGuid().ToString('N')) + '.part')
            $download = Invoke-AssetDownload -CandidateUrls $job.candidates -TempPath $tempPath
            $refs = if ($job.isVariant) { @($group.refs | Where-Object { $_.observedUrl -eq $job.labelUrl }) } else { @($group.refs) }
            if (-not $download.success) {
                if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
                $failedAssets.Add([pscustomobject][ordered]@{
                    id = 'asset-url-' + (Get-StringSha256 -Value $job.labelUrl).Substring(0, 16)
                    assetType = 'unknown'; localPath = $null; sha256 = $null; byteSize = 0
                    detectedMime = $null; extension = $null
                    observedSourceUrls = @($refs.observedUrl | Sort-Object -Unique)
                    canonicalOriginalSourceUrl = $group.canonicalUrl; downloadUrl = $download.observedAttemptUrl
                    aliasDownloadUrls = @(); sourcePages = @($refs.pageUrl | Sort-Object -Unique)
                    discoveryMethods = @($refs.method | Sort-Object -Unique)
                    altTexts = @($refs.alt | Where-Object { $_ } | Sort-Object -Unique); variants = $observedUrls
                    httpStatus = $download.status; downloadTimestamp = [DateTimeOffset]::UtcNow.ToString('o')
                    downloadStatus = 'failed'; errorSummary = $download.error
                    rightsStatus = 'unverified'; approvalStatus = 'unreviewed'
                    variantOf = if ($job.isVariant) { $group.canonicalUrl } else { $null }
                })
                Add-RunError -Phase 'asset-download' -Url $job.labelUrl -HttpStatus $download.status -Message $download.error
                continue
            }

            $hash = (Get-FileHash -LiteralPath $tempPath -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($assetsByHash.Contains($hash)) {
                $existing = $assetsByHash[$hash]
                $existing.observedSourceUrls = Merge-UniqueStrings -Collections @($existing.observedSourceUrls, $refs.observedUrl)
                $existing.sourcePages = Merge-UniqueStrings -Collections @($existing.sourcePages, $refs.pageUrl)
                $existing.discoveryMethods = Merge-UniqueStrings -Collections @($existing.discoveryMethods, $refs.method)
                $existing.altTexts = Merge-UniqueStrings -Collections @($existing.altTexts, @($refs.alt | Where-Object { $_ }))
                $existing.variants = Merge-UniqueStrings -Collections @($existing.variants, $observedUrls)
                $existing.aliasDownloadUrls = Merge-UniqueStrings -Collections @($existing.aliasDownloadUrls, @($download.finalUrl))
                Remove-Item -LiteralPath $tempPath -Force
                $script:DeduplicatedCount++
                continue
            }

            $methods = @($refs.method | Sort-Object -Unique)
            $assetType = Get-AssetType -Mime $download.mime -Extension $download.extension -Methods $methods
            $bucket = if ($assetType -eq 'video') { 'videos' } elseif ($assetType -eq 'icon') { 'icons' } else { 'images' }
            $targetPath = Join-Path $script:OutputRootFull ("assets\$bucket\$hash.$($download.extension)")
            if (Test-Path -LiteralPath $targetPath) {
                $existingHash = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($existingHash -eq $hash -and -not $Refresh) { Remove-Item -LiteralPath $tempPath -Force }
                else { Move-Item -LiteralPath $tempPath -Destination $targetPath -Force }
            } else { Move-Item -LiteralPath $tempPath -Destination $targetPath }
            $assetsByHash[$hash] = [pscustomobject][ordered]@{
                id = 'asset-' + $hash.Substring(0, 16); assetType = $assetType
                localPath = Get-RelativeManifestPath -FullPath $targetPath; sha256 = $hash; byteSize = $download.byteSize
                detectedMime = $download.mime; extension = $download.extension
                observedSourceUrls = @($refs.observedUrl | Sort-Object -Unique)
                canonicalOriginalSourceUrl = $group.canonicalUrl; downloadUrl = $download.finalUrl
                aliasDownloadUrls = @($download.finalUrl); sourcePages = @($refs.pageUrl | Sort-Object -Unique)
                discoveryMethods = $methods; altTexts = @($refs.alt | Where-Object { $_ } | Sort-Object -Unique)
                variants = $observedUrls; httpStatus = $download.status
                downloadTimestamp = [DateTimeOffset]::UtcNow.ToString('o')
                downloadStatus = if ($Refresh) { 'refreshed' } else { 'success' }
                errorSummary = $null; rightsStatus = 'unverified'; approvalStatus = 'unreviewed'
                variantOf = if ($job.isVariant) { $group.canonicalUrl } else { $null }
            }
        }
    }

    foreach ($inline in $script:InlineAssets.Values) {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($inline.content)
        $hash = $inline.hash
        if ($assetsByHash.Contains($hash)) {
            $existing = $assetsByHash[$hash]
            $existing.sourcePages = Merge-UniqueStrings -Collections @($existing.sourcePages, @($inline.pages))
            $existing.observedSourceUrls = Merge-UniqueStrings -Collections @($existing.observedSourceUrls, @($inline.observed))
            $existing.discoveryMethods = Merge-UniqueStrings -Collections @($existing.discoveryMethods, @('inline-svg'))
            $script:DeduplicatedCount++
            continue
        }
        $targetPath = Join-Path $script:OutputRootFull "assets\inline-svg\$hash.svg"
        if (-not (Test-Path -LiteralPath $targetPath) -or $Refresh) { [System.IO.File]::WriteAllBytes($targetPath, $bytes) }
        $assetsByHash[$hash] = [pscustomobject][ordered]@{
            id = 'asset-' + $hash.Substring(0, 16); assetType = 'inline-svg'
            localPath = Get-RelativeManifestPath -FullPath $targetPath; sha256 = $hash; byteSize = $bytes.Length
            detectedMime = 'image/svg+xml'; extension = 'svg'
            observedSourceUrls = @($inline.observed | Sort-Object); canonicalOriginalSourceUrl = $null
            downloadUrl = $null; aliasDownloadUrls = @(); sourcePages = @($inline.pages | Sort-Object)
            discoveryMethods = @('inline-svg'); altTexts = @(); variants = @(); httpStatus = $null
            downloadTimestamp = [DateTimeOffset]::UtcNow.ToString('o'); downloadStatus = 'extracted'
            errorSummary = $null; rightsStatus = 'unverified'; approvalStatus = 'unreviewed'; variantOf = $null
        }
    }

    $allAssets = @($assetsByHash.Values) + @($failedAssets)
    foreach ($page in $script:PageRecords) {
        $page.assetIds = @($allAssets | Where-Object {
            $_.sourcePages -contains $page.canonicalUrl -or $_.sourcePages -contains $page.url
        } | ForEach-Object { $_.id } | Sort-Object -Unique)
    }

    $finishedAt = [DateTimeOffset]::UtcNow
    $successfulAssets = @($assetsByHash.Values)
    [long]$totalDownloadedBytes = 0
    foreach ($asset in $successfulAssets) { $totalDownloadedBytes += [long]$asset.byteSize }
    $summary = [ordered]@{
        crawledPages = $script:PageRecords.Count
        discoveredAssetReferences = $script:DiscoveredReferenceCount
        uniqueAssets = $successfulAssets.Count
        uniqueImages = @($successfulAssets | Where-Object { $_.assetType -eq 'image' }).Count
        uniqueVideos = @($successfulAssets | Where-Object { $_.assetType -eq 'video' }).Count
        uniqueIconsAndSvg = @($successfulAssets | Where-Object { $_.assetType -in @('icon', 'inline-svg') }).Count
        downloadedAssets = @($successfulAssets | Where-Object { $_.downloadStatus -in @('success', 'refreshed') }).Count
        extractedInlineSvg = @($successfulAssets | Where-Object { $_.downloadStatus -eq 'extracted' }).Count
        deduplicatedAssets = $script:DeduplicatedCount
        skipped = $script:Skipped.Count
        failedAssets = $failedAssets.Count
        errors = $script:Errors.Count
        totalDownloadedBytes = $totalDownloadedBytes
        requestCount = $script:RequestCount
        outputPath = $script:OutputRootFull
    }
    $manifest = [ordered]@{
        schemaVersion = 1; baseUrl = $script:BaseUri.AbsoluteUri; generatedAt = $finishedAt.ToString('o')
        rightsStatusDefault = 'unverified'; approvalStatusDefault = 'unreviewed'
        options = [ordered]@{
            throttleMilliseconds = $ThrottleMilliseconds; pageLimit = $PageLimit; wpMediaPageLimit = $WpMediaPageLimit
            cssImportDepth = $CssImportDepth; maxStylesheets = $MaxStylesheets
            maxAssets = $MaxAssets; maxFileBytes = $MaxFileBytes
            requestTimeoutSeconds = $RequestTimeoutSeconds
            assetRequestTimeoutSeconds = $AssetRequestTimeoutSeconds
            downloadVariants = [bool]$DownloadVariants; refresh = [bool]$Refresh
        }
        discovery = [ordered]@{ robots = $script:Robots; sitemap = $script:Sitemap; wpRest = $script:WpRest }
        summary = $summary; assets = $allAssets
    }
    $pagesOutput = [ordered]@{
        baseUrl = $script:BaseUri.AbsoluteUri; generatedAt = $finishedAt.ToString('o')
        pages = @($script:PageRecords); fontIcons = @($script:FontIcons); remoteMediaReferences = @($script:RemoteMedia)
    }
    Write-JsonFile -Path (Join-Path $script:OutputRootFull 'asset-manifest.json') -Value $manifest
    Write-JsonFile -Path (Join-Path $script:OutputRootFull 'pages.json') -Value $pagesOutput
    Write-JsonFile -Path (Join-Path $script:OutputRootFull 'skipped.json') -Value @($script:Skipped)
    Write-JsonFile -Path (Join-Path $script:OutputRootFull 'errors.json') -Value @($script:Errors)

    $readme = @"
# PNPLINE public art source inventory

Generated: $($finishedAt.ToString('o'))

This directory is produced by ``tools/extract-pnpline-art-assets.ps1``. It contains public visual resources observed on ``$($script:BaseUri.AbsoluteUri)`` and provenance metadata. Collection does **not** establish publication rights or approval for use on another site. Every asset defaults to ``rightsStatus: unverified`` and ``approvalStatus: unreviewed``.

## Run summary

- Crawled pages: $($summary.crawledPages)
- Discovered asset references: $($summary.discoveredAssetReferences)
- Unique assets: $($summary.uniqueAssets)
- Images: $($summary.uniqueImages)
- Videos: $($summary.uniqueVideos)
- Icons and SVG: $($summary.uniqueIconsAndSvg)
- Downloaded assets: $($summary.downloadedAssets)
- SHA-256 deduplications: $($summary.deduplicatedAssets)
- Skipped references: $($summary.skipped)
- Failed assets: $($summary.failedAssets)
- Recorded errors: $($summary.errors)
- Total bytes: $($summary.totalDownloadedBytes)

## Files

- ``asset-manifest.json``: unique assets, hashes, sources, discovery context, variants, and review status.
- ``pages.json``: crawled pages, per-page asset IDs, font-icon metadata, and remote streaming references.
- ``skipped.json``: unsupported, excluded, or policy-limited references.
- ``errors.json``: request, parsing, and per-asset failures.
- ``assets/``: downloaded binaries and extracted inline SVG files.

Re-run without ``-Refresh`` to preserve an existing content-addressed file when its SHA-256 matches. Use ``-Refresh`` to replace the file after downloading the current response. Use ``-DownloadVariants`` only when WordPress/CDN derivatives are also required.
"@
    [System.IO.File]::WriteAllText((Join-Path $script:OutputRootFull 'README.md'), $readme, [System.Text.UTF8Encoding]::new($false))

    Write-Host ''
    Write-Host 'PNPLINE art inventory complete'
    foreach ($property in $summary.GetEnumerator()) { Write-Host ("  {0}: {1}" -f $property.Key, $property.Value) }
} finally {
    if ($script:HttpClient) { $script:HttpClient.Dispose() }
    if ($handler) { $handler.Dispose() }
}
