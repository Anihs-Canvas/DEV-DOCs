$file = 'Backstage.html'
$content = Get-Content $file -Raw -Encoding UTF8

# Map of answer-ending text -> explanation text for chapters 21-27
# We'll use regex replacement to add explanations after each answer
$replacements = @{}

# Ch 21 Q2-Q10
$replacements['Q2.*?Answer</div><p>It shows ArgoCD application sync status.*?entity YAML\.</p></div></details></div>'] = '...{add explanation for ArgoCD plugin}'

# Instead, let's count missing per chapter by analyzing the content
$lines = $content -split "`n"
$currentChapter = ""
$chapterMissing = @{}
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'Chapter (\d+).*CBA Practice Questions') {
        $currentChapter = $matches[1]
        $chapterMissing[$currentChapter] = 0
    }
    if ($currentChapter -and $lines[$i] -match '<div class="eq-answer">') {
        # Check if next lines have eq-explanation before next question or end
        $hasExp = $false
        for ($j = $i; $j -lt [Math]::Min($i+5, $lines.Count); $j++) {
            if ($lines[$j] -match 'eq-explanation') {
                $hasExp = $true
                break
            }
            if ($lines[$j] -match 'exam-question-item.*eq-number' -and $j -gt $i) {
                break
            }
            if ($lines[$j] -match 'cba-speed-tip|visual-summary|</div>\s*</div>\s*$') {
                break
            }
        }
        if (-not $hasExp) {
            $chapterMissing[$currentChapter]++
        }
    }
}

Write-Host "Missing explanations per chapter:"
$total = 0
foreach ($ch in $chapterMissing.Keys | Sort-Object { [int]$_ }) {
    $m = $chapterMissing[$ch]
    $total += $m
    Write-Host "  Ch $ch : $m missing"
}
Write-Host "Total: $total"
