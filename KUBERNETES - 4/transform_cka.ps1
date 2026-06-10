# Transform CKA test prep HTML to new stacked design pattern
# Usage: pwsh -File transform_cka.ps1
# Always creates a backup first

$file = ".\cka_test_prep.html"
$backup = ".\cka_test_prep.backup.html"

Write-Host "=== CKA Transform Script ===" -ForegroundColor Cyan

# Backup
Copy-Item $file $backup -Force
Write-Host "Backup: $backup" -ForegroundColor Green

$html = Get-Content $file -Raw
$changed = 0

# ============================================================
# TRANSFORM 1: ts-lookat blocks
# Old: <div class="ts-lookat"><strong>🔍...</strong> <code>X</code> — text <code>Y</code> — text</div>
# New: stacked items with code/span
# ============================================================

$lookatRegex = [regex]::new(
    '<div class="ts-lookat"><strong>🔍 What to Look At:</strong>\s*(.*?)</div>',
    [System.Text.RegularExpressions.RegexOptions]::Singleline
)

$lookatEval = {
    param($m)
    $inner = $m.Groups[1].Value
    $items = @()
    # Match <code>...</code> — text patterns
    $subRegex = [regex]::new('<code>(.*?)</code>\s*[—–-]\s*(.*?)(?=<code>|$)', 'Singleline')
    foreach ($match in $subRegex.Matches($inner)) {
        $cmd = $match.Groups[1].Value
        $desc = $match.Groups[2].Value.Trim()
        $items += "`n                <div class=`"ts-lookat-item`">`n                    <code>$cmd</code>`n                    <span>$desc</span>`n                </div>"
    }
    
    if ($items.Count -gt 0) {
        return "        <div class=`"ts-lookat`">`n            <strong>🔍 What to Look At:</strong>`n            <div class=`"ts-lookat-list`">" + ($items -join '') + "`n            </div>`n        </div>"
    }
    # Fallback: just wrap content
    $clean = $inner.Trim()
    return "        <div class=`"ts-lookat`">`n            <strong>🔍 What to Look At:</strong>`n            <span>$clean</span>`n        </div>"
}

$html = $lookatRegex.Replace($html, $lookatEval)
$newCount = ([regex]::Matches($html, 'ts-lookat-item')).Count
Write-Host "ts-lookat items created: $newCount" -ForegroundColor Yellow

# ============================================================
# TRANSFORM 2: ts-solution blocks
# Old: <div class="ts-solution"><strong>🔧...</strong><p>1. ...<br>2. ...</p></div>
# New: stacked solution-item cards
# ============================================================

$solnRegex = [regex]::new(
    '<div class="ts-solution"><strong>🔧 How to Solve:</strong>\s*<p>(.*?)</p>\s*</div>',
    [System.Text.RegularExpressions.RegexOptions]::Singleline
)

$solnEval = {
    param($m)
    $inner = $m.Groups[1].Value
    # Split by <br> and numbered steps
    $steps = $inner -split '\s*<br>\s*(?=\d+\.\s*)'
    $items = @()
    foreach ($step in $steps) {
        $step = $step.Trim() -replace '^\d+\.\s*', ''
        if ($step.Length -gt 5) {
            # Try to extract heading (text before first <code>)
            if ($step -match '^(.*?)<code>(.*?)</code>\s*[—–-]?\s*(.*)$') {
                $head = $matches[1].Trim()
                $cmd = $matches[2]
                $desc = $matches[3].Trim()
                $items += "`n                <div class=`"ts-solution-item`">`n                    <strong>$head</strong>`n                    <code>$cmd</code>`n                    <span>$desc</span>`n                </div>"
            } elseif ($step -match '^([^<]+)\s*[—–-]\s*(.*)$') {
                $head = $matches[1].Trim()
                $desc = $matches[2].Trim()
                $items += "`n                <div class=`"ts-solution-item`">`n                    <strong>$head</strong>`n                    <span>$desc</span>`n                </div>"
            } else {
                $items += "`n                <div class=`"ts-solution-item`">`n                    <span>$step</span>`n                </div>"
            }
        }
    }
    if ($items.Count -gt 0) {
        return "        <div class=`"ts-solution`">`n            <strong>🔧 How to Solve:</strong>`n            <div class=`"ts-solution-list`">" + ($items -join '') + "`n            </div>`n        </div>"
    }
    # Fallback
    return "        <div class=`"ts-solution`">`n            <strong>🔧 How to Solve:</strong>`n            <span>$inner</span>`n        </div>"
}

$html = $solnRegex.Replace($html, $solnEval)
$newCount = ([regex]::Matches($html, 'ts-solution-item')).Count
Write-Host "ts-solution items created: $newCount" -ForegroundColor Yellow

# ============================================================
# TRANSFORM 3: ts-advice blocks
# Old: <div class="ts-advice"><strong>💡...</strong> paragraph</div>
# New: single stacked advice-item
# ============================================================

$advRegex = [regex]::new(
    '<div class="ts-advice"><strong>💡 Personal Advice:</strong>\s*(.*?)</div>',
    [System.Text.RegularExpressions.RegexOptions]::Singleline
)

$advEval = {
    param($m)
    $inner = $m.Groups[1].Value.Trim()
    return "        <div class=`"ts-advice`">`n            <strong>💡 Personal Advice:</strong>`n            <div class=`"ts-advice-list`">`n                <div class=`"ts-advice-item`">`n                    <span>$inner</span>`n                </div>`n            </div>`n        </div>"
}

$html = $advRegex.Replace($html, $advEval)
$newCount = ([regex]::Matches($html, 'ts-advice-item')).Count
Write-Host "ts-advice items created: $newCount" -ForegroundColor Yellow

# Save
Set-Content $file -Value $html -NoNewline
Write-Host "Saved: $file" -ForegroundColor Green

# Verify
$final = Get-Content $file -Raw
$so = ([regex]::Matches($final, '<section\b')).Count
$sc = ([regex]::Matches($final, '</section>')).Count
Write-Host "Sections: $so/$sc = $(if($so -eq $sc){'BALANCED'}else{'MISMATCH'})" -ForegroundColor $(if($so -eq $sc){'Green'}else{'Red'})
