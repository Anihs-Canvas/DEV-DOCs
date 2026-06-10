$c = Get-Content "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html" -Raw
$lines = $c -split "`n"
$totalLines = $lines.Count

# Find line positions of all chapter id="chNN"
$chPositions = @{}
$chMatches = [regex]::Matches($c, 'id="(ch\d+[a-c]?)"')
foreach ($m in $chMatches) {
    $chId = $m.Groups[1].Value
    $chPositions[$chId] = $m.Index
}

# Convert positions to line numbers
$chLineNums = @{}
$runningPos = 0
for ($i = 0; $i -lt $totalLines; $i++) {
    $runningPos += $lines[$i].Length + 1
    foreach ($chId in $chPositions.Keys) {
        if ($runningPos -ge $chPositions[$chId] -and -not $chLineNums.ContainsKey($chId)) {
            $chLineNums[$chId] = $i + 1
        }
    }
}

# Sort by position in document
$sortedIds = $chPositions.Keys | Sort-Object { $chPositions[$_] }

# Compute ranges
$chRanges = @{}
for ($i = 0; $i -lt $sortedIds.Count; $i++) {
    $chId = $sortedIds[$i]
    $startLine = $chLineNums[$chId]
    if ($i + 1 -lt $sortedIds.Count) {
        $endLine = $chLineNums[$sortedIds[$i + 1]] - 1
    } else {
        $endLine = $totalLines
    }
    $chRanges[$chId] = @{ Start = $startLine; End = $endLine }
}

# Analyze ALL chapters, show only those missing from first scan or with <2 diagrams
Write-Output "=== ALL CHAPTERS (showing thin ones) ==="
Write-Output ("{0,-7} {1,-60} {2,>6} {3,>8} {4,>8} {5,>8}" -f "Ch", "Title", "Lines", "Sections", "Diagrams", "Cards")
Write-Output ("{0,-7} {1,-60} {2,>6} {3,>8} {4,>8} {5,>8}" -f "--", "-----", "-----", "--------", "--------", "-----")

# Extract titles
$titles = @{
    "ch1" = "Ch1: What is OpenShift?"
    "ch2" = "Ch2: Containers, Docker & Podman"
    "ch3" = "Ch3: OpenShift CLI (oc)"
    "ch4" = "Ch4: OpenShift Web Console"
    "ch5" = "Ch5: Installing OpenShift"
    "ch6" = "Ch6: Authentication & User Management"
    "ch7" = "Ch7: Networking - Routes, Services & Ingress"
    "ch8" = "Ch8: Storage for AI Workloads"
    "ch9" = "Ch9: Deploying Applications on OpenShift"
    "ch10" = "Ch10: Build Strategies & Image Management"
    "ch11" = "Ch11: Operators - Heart of OpenShift"
    "ch12" = "Ch12: Templates & Helm"
    "ch13" = "Ch13: Data Science Projects"
    "ch14" = "Ch14: Jupyter Notebooks on OpenShift"
    "ch15" = "Ch15: Data Science Pipelines"
    "ch16" = "Ch16: Feature Engineering & Data Prep"
    "ch17" = "Ch17: ML Model Development"
    "ch18" = "Ch18: Model Registry"
    "ch19" = "Ch19: Training Pipelines"
    "ch20" = "Ch20: GPU-Accelerated Training"
    "ch21" = "Ch21: Introduction to Model Serving"
    "ch22" = "Ch22: Single-Model Serving - KServe"
    "ch23" = "Ch23: Multi-Model Serving - ModelMesh"
    "ch24" = "Ch24: Advanced Inference Patterns"
    "ch25" = "Ch25: GPU Architecture for AI"
    "ch26" = "Ch26: NVIDIA GPU Operator"
    "ch27" = "Ch27: Hardware Sizing & Capacity Planning"
    "ch28" = "Ch28: Specialized AI Hardware"
    "ch28b" = "Ch28B: Advanced NVIDIA Infrastructure"
    "ch28c" = "Ch28C: NVIDIA Infrastructure Mastery"
    "ch29" = "Ch29: Monitoring AI Workloads"
    "ch30" = "Ch30: Troubleshooting AI Workloads"
    "ch31" = "Ch31: Day 2 Operations"
    "ch32" = "Ch32: Performance Tuning for AI"
    "ch33" = "Ch33: EX267 Exam Deep Dive"
    "ch34" = "Ch34: Practice Questions (90+)"
    "ch35" = "Ch35: Hands-On Labs (12 Labs)"
    "ch36" = "Ch36: Quick Reference Cards"
    "ch37" = "Ch37: Production AI Architecture"
    "ch38" = "Ch38: anihpj - Complete Production Deployment"
    "ch39" = "Ch39: AI Platform Engineering (SRE)"
}

$thinList = @()
$allList = @()

foreach ($chId in $sortedIds) {
    $range = $chRanges[$chId]
    $startIdx = $range.Start - 1
    $endIdx = $range.End - 1
    if ($endIdx -ge $totalLines) { $endIdx = $totalLines - 1 }
    if ($endIdx -lt $startIdx) { $endIdx = $startIdx }
    
    $segLines = $lines[$startIdx..$endIdx]
    $segment = $segLines -join "`n"
    $lineCount = $segLines.Count
    
    $sections = ([regex]::Matches($segment, 'class="section-block"')).Count
    $diagrams = ([regex]::Matches($segment, 'class="diagram-container"')).Count
    $cards = ([regex]::Matches($segment, 'class="info-card"')).Count
    
    $title = if ($titles.ContainsKey($chId)) { $titles[$chId] } else { $chId }
    
    $obj = [PSCustomObject]@{ Ch=$chId; Title=$title; Lines=$lineCount; Sections=$sections; Diagrams=$diagrams; Cards=$cards }
    $allList += $obj
    
    if ($diagrams -lt 2) {
        $thinList += $obj
        $flag = if ($diagrams -eq 0) { "*** ZERO" } else { "" }
        Write-Output ("{0,-7} {1,-60} {2,>6} {3,>8} {4,>8} {5,>8} {6}" -f $chId, $title, $lineCount, $sections, $diagrams, $cards, $flag)
    }
}

Write-Output "`n=== SUMMARY ==="
Write-Output "Total chapters: $($allList.Count)"
Write-Output "Thin chapters (<2 diagrams): $($thinList.Count)"
Write-Output "Chapters with 0 diagrams: $(($thinList | Where-Object { $_.Diagrams -eq 0 }).Count)"
Write-Output "Chapters with 1 diagram: $(($thinList | Where-Object { $_.Diagrams -eq 1 }).Count)"

# Show chapters with 0 diagrams
Write-Output "`n=== CHAPTERS WITH ZERO DIAGRAMS ==="
$thinList | Where-Object { $_.Diagrams -eq 0 } | Format-Table Ch, Title, Lines, Sections, Cards -AutoSize

# Show all chapters sorted by lines
Write-Output "`n=== ALL CHAPTERS BY SIZE (thinness) ==="
$allList | Sort-Object Lines | Format-Table Ch, Title, Lines, Sections, Diagrams, Cards -AutoSize
