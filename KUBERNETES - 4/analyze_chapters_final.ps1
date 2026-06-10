$html = Get-Content "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html" -Raw
$lines = $html -split '\r?\n'

# Find ALL lines matching "CHAPTER N:" pattern
$allChapterLines = @{}
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s+CHAPTER (\d+[A-Za-z]*):') {
        $ch = $matches[1]
        if (-not $allChapterLines.ContainsKey($ch)) {
            $allChapterLines[$ch] = $i + 1  # 1-based, first occurrence
        }
    }
}

# Define chapter boundaries
$targetChapters = [ordered]@{}
$chapterNums = @(2..31) + @('28B','28C')

foreach ($ch in $chapterNums) {
    $key = "$ch"
    if ($allChapterLines.ContainsKey($key)) {
        $targetChapters[$key] = $allChapterLines[$key]
    }
}

# Also add Ch32 to cap Ch31
$ch32Line = $allChapterLines['32']

Write-Output "Chapter boundaries:"
foreach ($ch in $targetChapters.Keys) {
    Write-Output "  Ch$ch : line $($targetChapters[$ch])"
}
Write-Output "  Ch32 cap : line $ch32Line"

# Process chapters
$results = @()
$chKeys = @($targetChapters.Keys)

for ($idx = 0; $idx -lt $chKeys.Count; $idx++) {
    $ch = $chKeys[$idx]
    $startLine = $targetChapters[$ch]
    
    if ($ch -eq '31') {
        $endLine = $ch32Line - 1
    } elseif ($idx + 1 -lt $chKeys.Count) {
        $endLine = $targetChapters[$chKeys[$idx + 1]] - 1
    } else {
        $endLine = $lines.Count
    }
    
    $s = $startLine - 1
    $e = $endLine - 1
    if ($e -lt $s) { $e = $s }
    
    $segmentLines = $lines[$s..$e]
    $segment = $segmentLines -join "`n"
    $lineCount = $segmentLines.Count
    
    $sectionBlocks = ([regex]::Matches($segment, 'class="section-block"')).Count
    $diagramContainers = ([regex]::Matches($segment, 'class="diagram-container"')).Count
    $compareTables = ([regex]::Matches($segment, 'class="compare-table"')).Count
    $infoCards = ([regex]::Matches($segment, 'class="info-card"')).Count
    $practiceQuestions = ([regex]::Matches($segment, 'class="exam-question-item"')).Count
    $keyTakeaways = ([regex]::Matches($segment, 'class="key-takeaway"')).Count
    $codeBlocks = ([regex]::Matches($segment, 'class="code-block"')).Count
    $allTables = ([regex]::Matches($segment, '<table')).Count
    $infoBoxes = ([regex]::Matches($segment, 'class="info-box"')).Count
    $examSpeedTips = ([regex]::Matches($segment, 'class="exam-speed-tip"')).Count
    $cardGrids = ([regex]::Matches($segment, 'class="card-grid"')).Count
    
    $results += [PSCustomObject]@{
        Chapter = "Ch$ch"
        Lines = $lineCount
        SectionBlocks = $sectionBlocks
        DiagramContainers = $diagramContainers
        CompareTables = $compareTables
        InfoCards = $infoCards
        InfoBoxes = $infoBoxes
        PracticeQuestions = $practiceQuestions
        ExamSpeedTips = $examSpeedTips
        KeyTakeaways = $keyTakeaways
        CodeBlocks = $codeBlocks
        AllTables = $allTables
        CardGrids = $cardGrids
    }
}

Write-Output ""
Write-Output "=== RANKED FROM THINNEST TO RICHEST ==="
$ranked = $results | Sort-Object Lines
$rank = 1
$ranked | ForEach-Object {
    if ($_.Lines -lt 120) { $tier = "[VERY THIN]" }
    elseif ($_.Lines -lt 180) { $tier = "[THIN]" }
    elseif ($_.Lines -lt 250) { $tier = "[MODERATE]" }
    elseif ($_.Lines -lt 400) { $tier = "[SOLID]" }
    else { $tier = "[RICH]" }
    
    Write-Output ("{0,2}. {1,-6} {2,4}L | sec:{3,2} diag:{4,2} cmpTbl:{5,2} infoCard:{6,2} infoBox:{7,2} examQ:{8,2} speedTip:{9,2} {10}" -f 
        $rank++, $_.Chapter, $_.Lines, $_.SectionBlocks, $_.DiagramContainers, 
        $_.CompareTables, $_.InfoCards, $_.InfoBoxes, $_.PracticeQuestions, $_.ExamSpeedTips, $tier)
}

Write-Output ""
Write-Output "=== TIER SUMMARY ==="
$veryThin = $ranked | Where-Object Lines -lt 120
$thin = $ranked | Where-Object { $_.Lines -ge 120 -and $_.Lines -lt 180 }
$moderate = $ranked | Where-Object { $_.Lines -ge 180 -and $_.Lines -lt 250 }
$solid = $ranked | Where-Object { $_.Lines -ge 250 -and $_.Lines -lt 400 }
$rich = $ranked | Where-Object { $_.Lines -ge 400 }

Write-Output "VERY THIN  (<120 lines): $(($veryThin | ForEach-Object { "$($_.Chapter)($($_.Lines)L)" }) -join ', ')"
Write-Output "THIN       (120-179): $(($thin | ForEach-Object { "$($_.Chapter)($($_.Lines)L)" }) -join ', ')"
Write-Output "MODERATE   (180-249): $(($moderate | ForEach-Object { "$($_.Chapter)($($_.Lines)L)" }) -join ', ')"
Write-Output "SOLID      (250-399): $(($solid | ForEach-Object { "$($_.Chapter)($($_.Lines)L)" }) -join ', ')"
Write-Output "RICH       (400+):   $(($rich | ForEach-Object { "$($_.Chapter)($($_.Lines)L)" }) -join ', ')"

Write-Output ""
Write-Output "=== CONTENT GAPS ==="
Write-Output "No diagrams: $(($ranked | Where-Object DiagramContainers -eq 0 | ForEach-Object { $_.Chapter }) -join ', ')"
Write-Output "No info-cards: $(($ranked | Where-Object InfoCards -eq 0 | ForEach-Object { $_.Chapter }) -join ', ')"
Write-Output "No compare-tables: $(($ranked | Where-Object CompareTables -eq 0 | ForEach-Object { $_.Chapter }) -join ', ')"
Write-Output "No info-boxes: $(($ranked | Where-Object InfoBoxes -eq 0 | ForEach-Object { $_.Chapter }) -join ', ')"
Write-Output "No exam-speed-tips: $(($ranked | Where-Object ExamSpeedTips -eq 0 | ForEach-Object { $_.Chapter }) -join ', ')"

Write-Output ""
Write-Output "=== OVERALL ==="
Write-Output "Total chapters: $($results.Count)"
Write-Output "Total lines: $(($results | Measure-Object Lines -Sum).Sum)"
Write-Output "Avg lines/chapter: $([math]::Round(($results | Measure-Object Lines -Average).Average, 1))"
Write-Output "Median lines: $(($ranked[ [math]::Floor($ranked.Count/2) ]).Lines)"
