$file = "c:\Users\owner\Desktop\DEV-DOCs\TERRAFORM 2\terraform_1.html"

# Step 1: Extract ALL sidebar href="#..." targets
Write-Host "=== EXTRACTING SIDEBAR ANCHORS ===" -ForegroundColor Cyan
$sidebarHrefs = @{}
$sidebarLines = Select-String -Path $file -Pattern 'href="#([^"]+)"' -AllMatches
foreach ($match in $sidebarLines) {
    # Only sidebar lines (before main content, roughly < line 13000)
    if ($match.LineNumber -lt 13000) {
        foreach ($m in $match.Matches) {
            $target = $m.Groups[1].Value
            if (-not $sidebarHrefs.ContainsKey($target)) {
                $sidebarHrefs[$target] = $match.LineNumber
            }
        }
    }
}
Write-Host "Total sidebar targets: $($sidebarHrefs.Count)"

# Step 2: Extract ALL id="..." in content
Write-Host "`n=== EXTRACTING CONTENT IDS ===" -ForegroundColor Cyan
$contentIds = @{}
$contentLines = Select-String -Path $file -Pattern 'id="([^"]+)"' -AllMatches
foreach ($match in $contentLines) {
    foreach ($m in $match.Matches) {
        $id = $m.Groups[1].Value
        if (-not $contentIds.ContainsKey($id)) {
            $contentIds[$id] = $match.LineNumber
        }
    }
}
Write-Host "Total content IDs: $($contentIds.Count)"

# Step 3: Find MISSING anchors (in sidebar but not in content)
Write-Host "`n=== MISSING ANCHORS (sidebar target has no matching content ID) ===" -ForegroundColor Red
$missing = @()
foreach ($href in ($sidebarHrefs.Keys | Sort-Object)) {
    if (-not $contentIds.ContainsKey($href)) {
        $missing += $href
        Write-Host "  MISSING: $href (sidebar line $($sidebarHrefs[$href]))" -ForegroundColor Yellow
    }
}
Write-Host "`nTotal MISSING: $($missing.Count)" -ForegroundColor $(if ($missing.Count -eq 0) { "Green" } else { "Red" })

# Step 4: Summary per chapter
Write-Host "`n=== PER-CHAPTER SUMMARY ===" -ForegroundColor Cyan
$chapters = $sidebarHrefs.Keys | Where-Object { $_ -match '^chapter-(\d+)$' } | Sort-Object { [int]($_ -replace 'chapter-','') }
foreach ($ch in $chapters) {
    $num = $ch -replace 'chapter-',''
    $chTargets = $sidebarHrefs.Keys | Where-Object { $_ -eq "chapter-$num" -or $_ -match "^section-$num-" -or $_ -match "^$num-\d" }
    $chMissing = $chTargets | Where-Object { -not $contentIds.ContainsKey($_) }
    $status = if ($chMissing.Count -eq 0) { "[OK]" } else { "[FAIL]" }
    $color = if ($chMissing.Count -eq 0) { "Green" } else { "Red" }
    Write-Host ("  Ch {0,2}: {1,3} targets, {2,3} missing {3}" -f $num, $chTargets.Count, $chMissing.Count, $status) -ForegroundColor $color
    if ($chMissing.Count -gt 0) {
        foreach ($m in $chMissing) { Write-Host "         -> $m" -ForegroundColor Yellow }
    }
}

# Appendices
$appendices = $sidebarHrefs.Keys | Where-Object { $_ -match '^appendix-' } | Sort-Object
$appGroups = @{}
foreach ($a in $appendices) {
    $letter = ($a -replace 'appendix-','')[0]
    if (-not $appGroups.ContainsKey($letter)) { $appGroups[$letter] = @() }
    $appGroups[$letter] += $a
}
foreach ($letter in ($appGroups.Keys | Sort-Object)) {
    $appMissing = $appGroups[$letter] | Where-Object { -not $contentIds.ContainsKey($_) }
    $status = if ($appMissing.Count -eq 0) { "[OK]" } else { "[FAIL]" }
    $color = if ($appMissing.Count -eq 0) { "Green" } else { "Red" }
    Write-Host ("  App {0}: {1,3} targets, {2,3} missing {3}" -f $letter.ToString().ToUpper(), $appGroups[$letter].Count, $appMissing.Count, $status) -ForegroundColor $color
    if ($appMissing.Count -gt 0) {
        foreach ($m in $appMissing) { Write-Host "         -> $m" -ForegroundColor Yellow }
    }
}

Write-Host "`n=== AUDIT COMPLETE ===" -ForegroundColor Cyan
