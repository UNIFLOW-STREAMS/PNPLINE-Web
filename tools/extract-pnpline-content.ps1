param(
    [string]$OutputRoot = (Join-Path (Get-Location).Path 'docs\source-content')
)

$ErrorActionPreference = 'Stop'

$Routes = @(
    '/',
    '/3PL.html',
    '/about.html',
    '/air.html',
    '/amazon.html',
    '/b2c-express.html',
    '/blog.html',
    '/customs-fda.html',
    '/customs-fta.html',
    '/customs-ior.html',
    '/customs-tariff.html',
    '/customs.html',
    '/d2c.html',
    '/ocean.html',
    '/privacy.html',
    '/quote.html',
    '/retail.html',
    '/returns-recovery.html',
    '/shopify.html',
    '/support.html',
    '/system-air.html',
    '/system-ocean.html',
    '/system-wms.html',
    '/system.html',
    '/tiktok.html',
    '/transport.html'
)

function Get-AttributeValue {
    param(
        [string]$Tag,
        [string]$Name
    )

    $pattern = '(?is)\b' + [regex]::Escape($Name) + '\s*=\s*(?:"(?<value>[^"]*)"|''(?<value>[^'']*)''|(?<value>[^\s>]+))'
    $match = [regex]::Match($Tag, $pattern)
    if ($match.Success) {
        return [System.Net.WebUtility]::HtmlDecode($match.Groups['value'].Value).Trim()
    }

    return ''
}

function ConvertTo-PlainText {
    param([string]$Html)

    if ([string]::IsNullOrWhiteSpace($Html)) {
        return ''
    }

    $text = $Html
    $text = [regex]::Replace($text, '(?is)<(script|style|noscript|template|svg)\b[^>]*>.*?</\1\s*>', '')
    $text = [regex]::Replace($text, '(?is)<br\s*/?>', "`n")
    $text = [regex]::Replace($text, '(?is)</?(p|div|section|article|header|footer|h[1-6]|li|tr|td|th|blockquote|details|summary|button|label|option)\b[^>]*>', "`n")
    $text = [regex]::Replace($text, '(?is)<[^>]+>', '')
    $text = [System.Net.WebUtility]::HtmlDecode($text)
    $text = $text -replace "`r", ''
    $lines = $text -split "`n" | ForEach-Object { $_ -replace '\s+', ' ' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    return ($lines -join "`n")
}

function Get-TagMatches {
    param(
        [string]$Html,
        [string]$TagName
    )

    return [regex]::Matches($Html, '(?is)<' + $TagName + '\b(?<attributes>[^>]*)>(?<content>.*?)</' + $TagName + '\s*>')
}

function Get-MetaContent {
    param(
        [string]$Html,
        [string]$Name
    )

    foreach ($tag in [regex]::Matches($Html, '(?is)<meta\b[^>]*>')) {
        $key = Get-AttributeValue -Tag $tag.Value -Name 'name'
        if (-not $key) {
            $key = Get-AttributeValue -Tag $tag.Value -Name 'property'
        }

        if ($key -ieq $Name) {
            return Get-AttributeValue -Tag $tag.Value -Name 'content'
        }
    }

    return ''
}

function Add-MarkdownList {
    param(
        [System.Text.StringBuilder]$Builder,
        [string[]]$Items,
        [string]$EmptyMessage = '없음'
    )

    if (-not $Items -or $Items.Count -eq 0) {
        [void]$Builder.AppendLine("- $EmptyMessage")
        return
    }

    foreach ($item in $Items) {
        [void]$Builder.AppendLine("- $item")
    }
}

function Format-MultilineBlock {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return '_없음_'
    }

    return $Text
}

New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$PagesRoot = Join-Path $OutputRoot 'pages'
New-Item -ItemType Directory -Path $PagesRoot -Force | Out-Null

$index = [System.Text.StringBuilder]::new()
[void]$index.AppendLine('# PNPLINE 한국어 사이트 원문 콘텐츠 추출본')
[void]$index.AppendLine()
[void]$index.AppendLine(("추출일: {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')))
[void]$index.AppendLine()
[void]$index.AppendLine('이 디렉터리에는 `https://www.pnpline.co.kr/`의 공개 HTML 페이지에서 추출한 원문이 들어 있습니다. 번역 원본으로 사용할 때에는 날짜, 운임, 리드타임, 규제 및 플랫폼 정책 문구를 별도로 최신 검수해야 합니다.')
[void]$index.AppendLine()
[void]$index.AppendLine('| 경로 | 원문 제목 | 추출 파일 |')
[void]$index.AppendLine('| --- | --- | --- |')

foreach ($Route in $Routes) {
    $url = if ($Route -eq '/') { 'https://www.pnpline.co.kr/' } else { 'https://www.pnpline.co.kr' + $Route }
    Write-Host "Extracting $url"
    $client = [System.Net.WebClient]::new()
    $client.Headers.Add('User-Agent', 'Mozilla/5.0 (compatible; PNPLINE-content-inventory/1.0)')
    try {
        $html = [System.Text.Encoding]::UTF8.GetString($client.DownloadData($url))
    } finally {
        $client.Dispose()
    }

    $titleMatch = [regex]::Match($html, '(?is)<title\b[^>]*>(?<content>.*?)</title\s*>')
    $title = ConvertTo-PlainText $titleMatch.Groups['content'].Value
    $description = Get-MetaContent -Html $html -Name 'description'
    $ogTitle = Get-MetaContent -Html $html -Name 'og:title'
    $ogDescription = Get-MetaContent -Html $html -Name 'og:description'
    $canonicalMatch = [regex]::Match($html, '(?is)<link\b(?=[^>]*\brel\s*=\s*(?:"canonical"|''canonical''|canonical))[^>]*>')
    $canonical = if ($canonicalMatch.Success) { Get-AttributeValue -Tag $canonicalMatch.Value -Name 'href' } else { '' }

    $h1 = @()
    foreach ($match in Get-TagMatches -Html $html -TagName 'h1') {
        $value = ConvertTo-PlainText $match.Groups['content'].Value
        if ($value) { $h1 += $value }
    }

    $sections = @()
    $sectionMatches = Get-TagMatches -Html $html -TagName 'section'
    foreach ($match in $sectionMatches) {
        $sectionText = ConvertTo-PlainText $match.Groups['content'].Value
        if (-not $sectionText) { continue }

        $headingMatch = [regex]::Match($match.Groups['content'].Value, '(?is)<h[1-3]\b[^>]*>(?<content>.*?)</h[1-3]\s*>')
        $heading = ConvertTo-PlainText $headingMatch.Groups['content'].Value
        $sectionId = Get-AttributeValue -Tag $match.Value.Substring(0, $match.Value.IndexOf('>') + 1) -Name 'id'
        $sectionClass = Get-AttributeValue -Tag $match.Value.Substring(0, $match.Value.IndexOf('>') + 1) -Name 'class'
        $sections += [pscustomobject]@{
            Heading = $heading
            Id = $sectionId
            Class = $sectionClass
            Text = $sectionText
        }
    }

    $faq = @()
    foreach ($match in Get-TagMatches -Html $html -TagName 'details') {
        $questionMatch = [regex]::Match($match.Groups['content'].Value, '(?is)<summary\b[^>]*>(?<content>.*?)</summary\s*>')
        $question = ConvertTo-PlainText $questionMatch.Groups['content'].Value
        $answerHtml = [regex]::Replace($match.Groups['content'].Value, '(?is)<summary\b[^>]*>.*?</summary\s*>', '')
        $answer = ConvertTo-PlainText $answerHtml
        if ($question -or $answer) {
            $faq += [pscustomobject]@{ Question = $question; Answer = $answer }
        }
    }

    if ($faq.Count -eq 0) {
        foreach ($article in Get-TagMatches -Html $html -TagName 'article') {
            $openingTag = $article.Value.Substring(0, $article.Value.IndexOf('>') + 1)
            $className = Get-AttributeValue -Tag $openingTag -Name 'class'
            if ($className -notmatch '(^|\s)faq-item(\s|$)') { continue }

            $question = ''
            $answer = ''
            foreach ($button in Get-TagMatches -Html $article.Groups['content'].Value -TagName 'button') {
                $buttonTag = $button.Value.Substring(0, $button.Value.IndexOf('>') + 1)
                if ((Get-AttributeValue -Tag $buttonTag -Name 'class') -match '(^|\s)faq-q(\s|$)') {
                    $question = ConvertTo-PlainText $button.Groups['content'].Value
                    break
                }
            }
            foreach ($div in Get-TagMatches -Html $article.Groups['content'].Value -TagName 'div') {
                $divTag = $div.Value.Substring(0, $div.Value.IndexOf('>') + 1)
                if ((Get-AttributeValue -Tag $divTag -Name 'class') -match '(^|\s)faq-a(\s|$)') {
                    $answer = ConvertTo-PlainText $div.Groups['content'].Value
                    break
                }
            }
            if ($question -or $answer) {
                $faq += [pscustomobject]@{ Question = $question; Answer = $answer }
            }
        }
    }

    if ($faq.Count -eq 0) {
        foreach ($script in [regex]::Matches($html, '(?is)<script\b[^>]*>(?<content>.*?)</script\s*>')) {
            if ($script.Groups['content'].Value -notmatch '(?s)"@type"\s*:\s*"FAQPage"') { continue }
            try {
                $json = $script.Groups['content'].Value.Trim() | ConvertFrom-Json
            } catch {
                continue
            }

            foreach ($item in @($json.mainEntity)) {
                $question = [string]$item.name
                $answer = [string]$item.acceptedAnswer.text
                if ($question -or $answer) {
                    $faq += [pscustomobject]@{ Question = $question; Answer = $answer }
                }
            }
        }
    }

    if ($Route -eq '/support.html' -and $faq.Count -eq 0) {
        $faqClient = [System.Net.WebClient]::new()
        $faqClient.Headers.Add('User-Agent', 'Mozilla/5.0 (compatible; PNPLINE-content-inventory/1.0)')
        try {
            $faqData = [System.Text.Encoding]::UTF8.GetString($faqClient.DownloadData('https://www.pnpline.co.kr/assets/faq-data.js'))
        } finally {
            $faqClient.Dispose()
        }

        foreach ($categoryMatch in [regex]::Matches($faqData, '(?is)id:\s*"(?<id>[^"]+)",\s*label:\s*"(?<label>[^"]+)",\s*items:\s*\[(?<items>.*?)\]\s*\}')) {
            $category = $categoryMatch.Groups['label'].Value
            foreach ($itemMatch in [regex]::Matches($categoryMatch.Groups['items'].Value, '(?is)q:\s*"(?<question>(?:\\.|[^"])*)",\s*a:\s*`(?<answer>.*?)`\s*\}')) {
                $question = [regex]::Unescape($itemMatch.Groups['question'].Value)
                $answer = ConvertTo-PlainText $itemMatch.Groups['answer'].Value
                if ($question -or $answer) {
                    $faq += [pscustomobject]@{ Category = $category; Question = $question; Answer = $answer }
                }
            }
        }
    }

    if ($faq.Count -eq 0) {
        foreach ($match in $sectionMatches) {
            $tag = $match.Value.Substring(0, $match.Value.IndexOf('>') + 1)
            $identifier = (Get-AttributeValue -Tag $tag -Name 'id') + ' ' + (Get-AttributeValue -Tag $tag -Name 'class')
            if ($identifier -match '(?i)faq|accordion') {
                $faqText = ConvertTo-PlainText $match.Groups['content'].Value
                if ($faqText) { $faq += [pscustomobject]@{ Question = ''; Answer = $faqText } }
            }
        }
    }

    $mainMatch = [regex]::Match($html, '(?is)<main\b[^>]*>(?<content>.*?)</main\s*>')
    $mainHtml = if ($mainMatch.Success) { $mainMatch.Groups['content'].Value } else { $html }
    $ctas = @()
    foreach ($match in Get-TagMatches -Html $mainHtml -TagName 'a') {
        $copy = ConvertTo-PlainText $match.Groups['content'].Value
        $openingTag = $match.Value.Substring(0, $match.Value.IndexOf('>') + 1)
        $href = Get-AttributeValue -Tag $openingTag -Name 'href'
        if ($copy -match '견적|상담|문의|시작|신청|무료|알아보기|연락|바로') {
            $ctas += [pscustomobject]@{ Copy = $copy; Target = $href }
        }
    }
    foreach ($match in Get-TagMatches -Html $mainHtml -TagName 'button') {
        $copy = ConvertTo-PlainText $match.Groups['content'].Value
        if ($copy -match '견적|상담|문의|시작|신청|무료|알아보기|연락|바로') {
            $ctas += [pscustomobject]@{ Copy = $copy; Target = 'button' }
        }
    }

    $images = @()
    foreach ($match in [regex]::Matches($html, '(?is)<img\b[^>]*>')) {
        $alt = Get-AttributeValue -Tag $match.Value -Name 'alt'
        $src = Get-AttributeValue -Tag $match.Value -Name 'src'
        if ($alt -or $src) {
            $images += [pscustomobject]@{ Alt = $alt; Source = $src }
        }
    }

    $forms = @()
    foreach ($match in Get-TagMatches -Html $html -TagName 'form') {
        $formHtml = $match.Groups['content'].Value
        $formFields = @()
        foreach ($fieldMatch in [regex]::Matches($formHtml, '(?is)<(?:input|textarea|select)\b[^>]*>')) {
            $tag = $fieldMatch.Value
            $type = Get-AttributeValue -Tag $tag -Name 'type'
            if ($type -in @('hidden', 'submit', 'button')) { continue }
            $name = Get-AttributeValue -Tag $tag -Name 'name'
            $placeholder = Get-AttributeValue -Tag $tag -Name 'placeholder'
            $label = Get-AttributeValue -Tag $tag -Name 'aria-label'
            $formFields += ("{0} | name: {1} | placeholder: {2} | label: {3}" -f $type, $name, $placeholder, $label)
        }
        foreach ($labelMatch in Get-TagMatches -Html $formHtml -TagName 'label') {
            $value = ConvertTo-PlainText $labelMatch.Groups['content'].Value
            if ($value) { $formFields += "label: $value" }
        }
        foreach ($buttonMatch in Get-TagMatches -Html $formHtml -TagName 'button') {
            $value = ConvertTo-PlainText $buttonMatch.Groups['content'].Value
            if ($value) { $formFields += "button: $value" }
        }
        $formText = ConvertTo-PlainText $formHtml
        $forms += [pscustomobject]@{
            Action = Get-AttributeValue -Tag $match.Value.Substring(0, $match.Value.IndexOf('>') + 1) -Name 'action'
            Method = Get-AttributeValue -Tag $match.Value.Substring(0, $match.Value.IndexOf('>') + 1) -Name 'method'
            Fields = $formFields
            Copy = $formText
        }
    }

    if ($forms.Count -eq 0) {
        $looseFields = @()
        foreach ($fieldMatch in [regex]::Matches($html, '(?is)<(?:input|textarea|select)\b[^>]*>')) {
            $tag = $fieldMatch.Value
            $type = Get-AttributeValue -Tag $tag -Name 'type'
            if ($type -in @('hidden', 'submit', 'button')) { continue }
            $name = Get-AttributeValue -Tag $tag -Name 'name'
            $placeholder = Get-AttributeValue -Tag $tag -Name 'placeholder'
            $ariaLabel = Get-AttributeValue -Tag $tag -Name 'aria-label'
            $looseFields += ("{0} | name: {1} | placeholder: {2} | aria-label: {3}" -f $type, $name, $placeholder, $ariaLabel)
        }

        if ($looseFields.Count -gt 0) {
            $labels = @()
            foreach ($labelMatch in Get-TagMatches -Html $html -TagName 'label') {
                $value = ConvertTo-PlainText $labelMatch.Groups['content'].Value
                if ($value) { $labels += "label: $value" }
            }
            $sourceSection = $sections | Where-Object { $_.Text -match '회사명|전화번호|이메일' } | Select-Object -Last 1
            $forms += [pscustomobject]@{
                Action = '표준 <form> 태그 없음: 스크립트 기반 제출'
                Method = '감지되지 않음'
                Fields = @($labels + $looseFields)
                Copy = if ($sourceSection) { $sourceSection.Text } else { '' }
            }
        }
    }

    $footerMatch = [regex]::Match($html, '(?is)<footer\b[^>]*>(?<content>.*?)</footer\s*>')
    $footerText = ConvertTo-PlainText $footerMatch.Groups['content'].Value
    $footerLinks = @()
    if ($footerMatch.Success) {
        foreach ($match in Get-TagMatches -Html $footerMatch.Groups['content'].Value -TagName 'a') {
            $copy = ConvertTo-PlainText $match.Groups['content'].Value
            $openingTag = $match.Value.Substring(0, $match.Value.IndexOf('>') + 1)
            $href = Get-AttributeValue -Tag $openingTag -Name 'href'
            if ($copy) { $footerLinks += "$copy -> $href" }
        }
    }

    $cookieText = ''
    $cookieMatch = [regex]::Match($html, '(?is)<(?:div|section)\b[^>]*(?:class|id)\s*=\s*(?:"[^"]*(?:cookie|consent)[^"]*"|''[^'']*(?:cookie|consent)[^'']*'')[^>]*>(?<content>.*?)</(?:div|section)\s*>')
    if ($cookieMatch.Success) {
        $cookieText = ConvertTo-PlainText $cookieMatch.Groups['content'].Value
    }

    $slug = if ($Route -eq '/') { 'home' } else { [System.IO.Path]::GetFileNameWithoutExtension($Route.TrimStart('/')) }
    $fileName = "$slug.md"
    $safeTitle = $title -replace '\|', '\|'
    $page = [System.Text.StringBuilder]::new()
    [void]$page.AppendLine("# $Route 원문 콘텐츠")
    [void]$page.AppendLine()
    [void]$page.AppendLine("- 원문 URL: $url")
    [void]$page.AppendLine(("- 추출 시각: {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')))
    [void]$page.AppendLine()
    [void]$page.AppendLine('## 제목 및 메타 정보')
    [void]$page.AppendLine()
    [void]$page.AppendLine("- 문서 제목: $title")
    [void]$page.AppendLine("- 메타 설명: $description")
    [void]$page.AppendLine("- Open Graph 제목: $ogTitle")
    [void]$page.AppendLine("- Open Graph 설명: $ogDescription")
    [void]$page.AppendLine("- Canonical URL: $canonical")
    [void]$page.AppendLine()
    [void]$page.AppendLine('## H1')
    [void]$page.AppendLine()
    Add-MarkdownList -Builder $page -Items $h1
    [void]$page.AppendLine()
    [void]$page.AppendLine('## 섹션 카피')
    [void]$page.AppendLine()
    if ($sections.Count -eq 0) {
        [void]$page.AppendLine('_`section` 요소를 찾지 못했습니다. 본문 텍스트는 수동 확인이 필요합니다._')
    } else {
        $sectionNumber = 0
        foreach ($section in $sections) {
            $sectionNumber++
            $sectionName = if ($section.Heading) { $section.Heading } elseif ($section.Id) { "#$($section.Id)" } elseif ($section.Class) { ".$($section.Class)" } else { "섹션 $sectionNumber" }
            [void]$page.AppendLine("### $sectionNumber. $sectionName")
            [void]$page.AppendLine()
            [void]$page.AppendLine((Format-MultilineBlock $section.Text))
            [void]$page.AppendLine()
        }
    }
    [void]$page.AppendLine('## FAQ 및 아코디언')
    [void]$page.AppendLine()
    if ($faq.Count -eq 0) {
        [void]$page.AppendLine('- FAQ 또는 아코디언 요소를 찾지 못했습니다.')
    } else {
        foreach ($item in $faq) {
            if ($item.Question) {
                $faqHeading = if ($item.Category) { "[$($item.Category)] $($item.Question)" } else { $item.Question }
                [void]$page.AppendLine("### $faqHeading")
                [void]$page.AppendLine()
            }
            [void]$page.AppendLine((Format-MultilineBlock $item.Answer))
            [void]$page.AppendLine()
        }
    }
    [void]$page.AppendLine('## CTA')
    [void]$page.AppendLine()
    if ($ctas.Count -eq 0) {
        [void]$page.AppendLine('- CTA 후보를 찾지 못했습니다.')
    } else {
        foreach ($cta in $ctas) {
            [void]$page.AppendLine("- $($cta.Copy) -> $($cta.Target)")
        }
    }
    [void]$page.AppendLine()
    [void]$page.AppendLine('## 이미지 대체 텍스트')
    [void]$page.AppendLine()
    if ($images.Count -eq 0) {
        [void]$page.AppendLine('- 이미지 요소를 찾지 못했습니다.')
    } else {
        foreach ($image in $images) {
            [void]$page.AppendLine("- alt: $($image.Alt) | src: $($image.Source)")
        }
    }
    [void]$page.AppendLine()
    [void]$page.AppendLine('## 폼 문구')
    [void]$page.AppendLine()
    if ($forms.Count -eq 0) {
        [void]$page.AppendLine('- 폼 요소를 찾지 못했습니다.')
    } else {
        $formNumber = 0
        foreach ($form in $forms) {
            $formNumber++
            [void]$page.AppendLine("### 폼 $formNumber")
            [void]$page.AppendLine()
            [void]$page.AppendLine("- action: $($form.Action)")
            [void]$page.AppendLine("- method: $($form.Method)")
            [void]$page.AppendLine('- 필드 및 버튼:')
            Add-MarkdownList -Builder $page -Items $form.Fields
            [void]$page.AppendLine()
            [void]$page.AppendLine('원문 문구:')
            [void]$page.AppendLine()
            [void]$page.AppendLine((Format-MultilineBlock $form.Copy))
            [void]$page.AppendLine()
        }
    }
    [void]$page.AppendLine('## 푸터')
    [void]$page.AppendLine()
    [void]$page.AppendLine((Format-MultilineBlock $footerText))
    [void]$page.AppendLine()
    [void]$page.AppendLine('푸터 링크:')
    Add-MarkdownList -Builder $page -Items $footerLinks
    [void]$page.AppendLine()
    [void]$page.AppendLine('## 쿠키 안내')
    [void]$page.AppendLine()
    [void]$page.AppendLine((Format-MultilineBlock $cookieText))

    $pagePath = Join-Path $PagesRoot $fileName
    [System.IO.File]::WriteAllText($pagePath, $page.ToString(), [System.Text.UTF8Encoding]::new($false))
    [void]$index.AppendLine(("| `{0}` | {1} | [pages/{2}](pages/{2}) |" -f $Route, $safeTitle, $fileName))
}

[System.IO.File]::WriteAllText((Join-Path $OutputRoot 'README.md'), $index.ToString(), [System.Text.UTF8Encoding]::new($false))
