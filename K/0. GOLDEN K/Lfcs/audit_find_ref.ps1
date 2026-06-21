$file = "c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Lfcs\linux_cli.html"
$c = [System.IO.File]::ReadAllText($file)
$articles = [regex]::Split($c, '(?=<article\b)')

Write-Output "============================================="
Write-Output "  FIND-REFERENCE STRUCTURAL AUDIT"
Write-Output "============================================="
Write-Output "Total articles: $($articles.Count)"
Write-Output ""

# Reference pattern from find:
# 1. h3
# 2. api-meta (badges+tags)
# 3. api-subtitle
# 4. api-description
# 5. syntax-header -> Syntax
# 6. Parameters table
# 7. Return Value table
# 8. 📁 Context (carol commands)
# 9. 📁 Context (Daily Workflow)
# 10. Examples

$issues = @{
    MissingH3 = @()
    MissingMeta = @()
    MissingSubtitle = @()
    MissingDesc = @()
    MissingSyntax = @()
    MissingParams = @()
    MissingRV = @()
    MissingContext = @()
    MissingExamples = @()
    WrongOrder = @()
    ThinSyntax = @()
    NoCommonPatterns = @()
}

foreach ($a in $articles) {
    if ($a -notmatch '<h3>') { continue }
    $id = ''
    if ($a -match 'id="([^"]+)"') { $id = $Matches[1] }
    
    # Check each element
    if ($a -notmatch '<h3>[^<]+</h3>') { $issues.MissingH3 += $id }
    if ($a -notmatch 'api-meta') { $issues.MissingMeta += $id }
    if ($a -notmatch 'api-subtitle') { $issues.MissingSubtitle += $id }
    if ($a -notmatch 'api-description') { $issues.MissingDesc += $id }
    if ($a -notmatch 'syntax-header') { $issues.MissingSyntax += $id }
    if ($a -notmatch '<h4>Parameters</h4>') { $issues.MissingParams += $id }
    if ($a -notmatch '<h4>Return Value</h4>') { $issues.MissingRV += $id }
    
    # Context check
    if ($a -notmatch '📁 Context') { $issues.MissingContext += $id }
    
    # Examples check
    if ($a -notmatch '<h4>Examples</h4>') { $issues.MissingExamples += $id }
    
    # Syntax depth check
    if ($a -match 'syntax-header.*?<pre><code[^>]*>(.*?)</code></pre>') {
        $code = $Matches[1]
        $lines = ($code -split '\r?\n' | Where-Object { $_.Trim() -ne '' }).Count
        if ($lines -le 4) { $issues.ThinSyntax += $id }
        if ($code -notmatch 'Common patterns' -and $code -notmatch '# Common:') {
            if ($lines -gt 4) { $issues.NoCommonPatterns += $id }
        }
    }
    
    # Order check: find heading positions
    $ordered = $true
    $lastPos = -1
    $orderLabels = @('syntax-header', '<h4>Parameters</h4>', '<h4>Return Value</h4>', '<h4>📁 Context', '<h4>Examples</h4>')
    foreach ($label in $orderLabels) {
        $pos = $a.IndexOf($label)
        if ($pos -ge 0 -and $pos -lt $lastPos) { $ordered = $false; break }
        if ($pos -ge 0) { $lastPos = $pos }
    }
    if (-not $ordered) { $issues.WrongOrder += $id }
}

# Report
Write-Output "--- Missing Elements ---"
foreach ($key in $issues.Keys | Sort-Object) {
    $count = $issues[$key].Count
    if ($count -eq 0) { continue }
    $label = $key -replace 'Missing', 'Missing '
    Write-Output "${label}: ${count}"
    if ($count -le 20) {
        $issues[$key] | ForEach-Object { Write-Output "  $_" }
    } else {
        $issues[$key] | Select-Object -First 10 | ForEach-Object { Write-Output "  $_" }
        Write-Output "  ... and $($count - 10) more"
    }
}

Write-Output "`n--- Order Issues ---"
Write-Output "Wrong element order: $($issues.WrongOrder.Count)"
if ($issues.WrongOrder.Count -le 30) {
    $issues.WrongOrder | ForEach-Object { Write-Output "  $_" }
}

Write-Output "`n--- Syntax Depth ---"
Write-Output "Thin syntax (<=4 lines): $($issues.ThinSyntax.Count)"
Write-Output "No Common patterns (but >4 lines): $($issues.NoCommonPatterns.Count)"

Write-Output "`n============================================="
Write-Output "  AUDIT COMPLETE"
Write-Output "============================================="