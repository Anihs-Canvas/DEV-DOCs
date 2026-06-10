$ErrorActionPreference = "Stop"
$filePath = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html"
$c = Get-Content $filePath -Raw
$lines = $c -split "`n"
$totalLines = $lines.Count
Write-Output "=== FILE LOADED: $($c.Length) chars, $totalLines lines ==="

# =============================================
# PART 1: Extract chapter titles from sidebar
# =============================================
$sidebarPattern = '(?s)<nav class="sidebar-nav">(.*?)</nav>'
$sidebarMatch = [regex]::Match($c, $sidebarPattern)
$sidebar = if ($sidebarMatch.Success) { $sidebarMatch.Groups[1].Value } else { "" }

$chapterLinks = [regex]::Matches($sidebar, '<a\s+href="#(ch\d+[a-c]?)"[^>]*?>(.*?)</a>')
$chapterTitles = @{}
foreach ($link in $chapterLinks) {
    $id = $link.Groups[1].Value
    $title = $link.Groups[2].Value -replace '<[^>]+>', '' -replace '\s+', ' ' -replace '^\d+\.?\s*', ''
    $chapterTitles[$id] = $title.Trim()
}

Write-Output "`n=== CHAPTER TITLES ==="
foreach ($k in ($chapterTitles.Keys | Sort-Object { [int]($k -replace '[^0-9]','') -replace '^0','0' })) {
    Write-Output "$k : $($chapterTitles[$k])"
}

# =============================================
# PART 2: Find chapter boundaries by id="chNN" in body
# =============================================
$chapterBoundaries = [regex]::Matches($c, 'id="(ch\d+[a-c]?)"[^>]*>')
$chStarts = @{}
$chIds = @()
foreach ($m in $chapterBoundaries) {
    $chId = $m.Groups[1].Value
    $pos = $m.Index
    $chStarts[$chId] = $pos
    $chIds += $chId
}

# Find which line each chapter starts at
$chLineNums = @{}
$runningPos = 0
for ($i = 0; $i -lt $totalLines; $i++) {
    $runningPos += $lines[$i].Length + 1
    foreach ($chId in $chIds) {
        if ($runningPos -ge $chStarts[$chId] -and -not $chLineNums.ContainsKey($chId)) {
            $chLineNums[$chId] = $i + 1
        }
    }
}

# Compute chapter line ranges
$chRanges = @{}
$sortedIds = $chIds | ForEach-Object { $_ }  # keep original order
for ($i = 0; $i -lt $sortedIds.Count; $i++) {
    $chId = $sortedIds[$i]
    $startLine = $chLineNums[$chId]
    if ($i + 1 -lt $sortedIds.Count) {
        $nextId = $sortedIds[$i + 1]
        $endLine = $chLineNums[$nextId] - 1
    } else {
        $endLine = $totalLines
    }
    $chRanges[$chId] = @{ Start = $startLine; End = $endLine }
}

# =============================================
# PART 3: Analyze each chapter
# =============================================
$results = @()
foreach ($chId in $sortedIds) {
    $range = $chRanges[$chId]
    $startIdx = $range.Start - 1
    $endIdx = $range.End - 1
    if ($endIdx -ge $totalLines) { $endIdx = $totalLines - 1 }
    if ($endIdx -lt $startIdx) { $endIdx = $startIdx }
    
    $segLines = $lines[$startIdx..$endIdx]
    $segment = $segLines -join "`n"
    $lineCount = $segLines.Count
    
    $sectionBlocks = ([regex]::Matches($segment, 'class="section-block"')).Count
    $diagramContainers = ([regex]::Matches($segment, 'class="diagram-container"')).Count
    $compareTables = ([regex]::Matches($segment, 'class="compare-table"')).Count
    $infoCards = ([regex]::Matches($segment, 'class="info-card"')).Count
    $practiceQuestions = ([regex]::Matches($segment, 'class="exam-question-item"')).Count
    $keyTakeaways = ([regex]::Matches($segment, 'class="key-takeaway"')).Count
    $codeBlocks = ([regex]::Matches($segment, 'class="code-block"')).Count
    $tables = ([regex]::Matches($segment, '<table')).Count
    
    $title = if ($chapterTitles.ContainsKey($chId)) { $chapterTitles[$chId] } else { "???" }
    
    $results += [PSCustomObject]@{
        Chapter = $chId
        Title = $title
        Lines = $lineCount
        SectionBlocks = $sectionBlocks
        DiagramContainers = $diagramContainers
        CompareTables = $compareTables
        InfoCards = $infoCards
        PracticeQuestions = $practiceQuestions
        KeyTakeaways = $keyTakeaways
        CodeBlocks = $codeBlocks
        AllTables = $tables
    }
}

# =============================================
# PART 3 OUTPUT: Thin Chapters (diagrams < 2)
# =============================================
Write-Output "`n========================================"
Write-Output "THIN CHAPTERS (LESS THAN 2 DIAGRAMS)"
Write-Output "========================================"
$thinChapters = $results | Where-Object { $_.DiagramContainers -lt 2 } | Sort-Object Lines
$thinChapters | Format-Table Chapter, Title, Lines, SectionBlocks, DiagramContainers, InfoCards -AutoSize

# =============================================
# PART 4: Broken anchor links
# =============================================
Write-Output "`n========================================"
Write-Output "BROKEN INTERNAL ANCHOR LINKS"
Write-Output "========================================"

# Collect all id="..." targets in the body
$allIds = [regex]::Matches($c, 'id="([^"]+)"')
$idSet = @{}
foreach ($m in $allIds) {
    $idVal = $m.Groups[1].Value
    $idSet[$idVal] = $true
}

# Collect all href="#..." links in the sidebar
$sidebarHrefs = [regex]::Matches($sidebar, 'href="#([^"]+)"')
$brokenLinks = @()
$seenBroken = @{}
foreach ($m in $sidebarHrefs) {
    $href = $m.Groups[1].Value
    if (-not $idSet.ContainsKey($href) -and -not $seenBroken.ContainsKey($href)) {
        $seenBroken[$href] = $true
        # Find context
        $ctxStart = [Math]::Max(0, $m.Index - 50)
        $ctxLen = [Math]::Min(200, $sidebar.Length - $ctxStart)
        $ctx = $sidebar.Substring($ctxStart, $ctxLen) -replace '\s+', ' '
        $brokenLinks += [PSCustomObject]@{ Href = $href; Context = $ctx }
    }
}

if ($brokenLinks.Count -eq 0) {
    Write-Output "No broken anchor links found in sidebar!"
} else {
    $brokenLinks | Format-Table Href, Context -AutoSize -Wrap
}

# Also check ALL href="#..." in entire document
Write-Output "`n--- All href=# links in document (not just sidebar) ---"
$allHrefs = [regex]::Matches($c, 'href="#([^"]+)"')
$allBroken = @{}
foreach ($m in $allHrefs) {
    $href = $m.Groups[1].Value
    if (-not $idSet.ContainsKey($href) -and -not $allBroken.ContainsKey($href)) {
        $allBroken[$href] = $true
    }
}
if ($allBroken.Count -eq 0) {
    Write-Output "No broken href=# links anywhere in document!"
} else {
    Write-Output "Broken href=# links found:"
    foreach ($k in ($allBroken.Keys | Sort-Object)) {
        Write-Output "  #$k"
    }
}

# =============================================
# PART 5: Red Hat AI Topics coverage
# =============================================
Write-Output "`n========================================"
Write-Output "RED HAT AI TOPICS COVERAGE"
Write-Output "========================================"

$topics = @(
    "AutoML", "AutoRAG", "Distributed Inference", "llm-d", "KServe RawDeployment",
    "CodeFlare", "Kueue", "RAY", "vLLM", "TGI", "Embeddings", "Vector Store",
    "OpenTelemetry", "Distributed Workloads", "Node Feature Discovery",
    "Cluster Logging Operator", "LokiStack"
)

foreach ($topic in $topics) {
    # Case-insensitive search
    $count = ([regex]::Matches($c, [regex]::Escape($topic), 'IgnoreCase')).Count
    if ($count -eq 0) {
        Write-Output "MISSING: $topic (0 mentions)"
    } elseif ($count -le 3) {
        Write-Output "THIN:    $topic ($count mentions)"
    } else {
        Write-Output "OK:      $topic ($count mentions)"
    }
}

# Additional: find sections near these topics
Write-Output "`n=== TOPIC SECTION CONTEXT ==="
foreach ($topic in $topics) {
    $escTopic = [regex]::Escape($topic)
    $matches = [regex]::Matches($c, "(.{0,100}$escTopic.{0,100})", 'IgnoreCase')
    if ($matches.Count -gt 0) {
        Write-Output "`n--- $topic ($($matches.Count) matches) ---"
        $shown = 0
        foreach ($mm in $matches) {
            if ($shown -ge 3) { Write-Output "  ... ($($matches.Count - 3) more)"; break }
            $ctx = $mm.Value -replace '\s+', ' ' -replace '<[^>]+>', ' '
            Write-Output "  $ctx"
            $shown++
        }
    }
}

Write-Output "`n=== SCAN COMPLETE ==="
