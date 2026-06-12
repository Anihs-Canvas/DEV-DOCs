# Remove orphaned explanations that sit BETWEEN question divs or BEFORE first question
$filePath = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\aws_devops.html"
$h = Get-Content $filePath -Raw

Write-Host "=== CLEANING ORPHANED EXPLANATIONS ==="

# Pattern 1: Orphans between questions  
# </div></details></div> + <div class="eq-explanation">...</div> + <div class="exam-question-item">
$pattern1 = '(?s)</div></details></div>\s*<div class="eq-explanation"><div class="eq-exp-label">📖 EXPLANATION</div><p>This concept is tested on .+?</p></div>\s*(?=<div class="exam-question-item">)'
$before1 = ([regex]::Matches($h, $pattern1)).Count
$h = [regex]::Replace($h, $pattern1, '</div></details></div>', 'Singleline')
$after1 = ([regex]::Matches($h, $pattern1)).Count
Write-Host "Removed $($before1 - $after1) between-question orphans"

# Pattern 2: Orphans at start of question section (before first question)
# <h4>...Questions</h4> + explanation(s) + <div class="exam-question-item">
$pattern2 = '(?s)(<h4>📝 Chapter .+?Questions</h4>)\s*(<div class="eq-explanation"><div class="eq-exp-label">📖 EXPLANATION</div><p>This concept is tested on .+?</p></div>\s*)+(?=<div class="exam-question-item">)'
$before2 = ([regex]::Matches($h, $pattern2)).Count
$h = [regex]::Replace($h, $pattern2, '$1', 'Singleline')
$after2 = ([regex]::Matches($h, $pattern2)).Count
Write-Host "Removed $($before2 - $after2) start-of-section orphans"

# Pattern 3: Orphans before drill section
# </div></details></div> + explanation(s) + <div class="cka-practice-drill">
$pattern3 = '(?s)</div></details></div>\s*<div class="eq-explanation"><div class="eq-exp-label">📖 EXPLANATION</div><p>This concept is tested on .+?</p></div>\s*(?=<div class="cka-practice-drill">)'
$before3 = ([regex]::Matches($h, $pattern3)).Count
$h = [regex]::Replace($h, $pattern3, '</div></details></div>', 'Singleline')
$after3 = ([regex]::Matches($h, $pattern3)).Count
Write-Host "Removed $($before3 - $after3) before-drill orphans"

Set-Content $filePath -Value $h -NoNewline

# Verify
$h2 = Get-Content $filePath -Raw
$s = ([regex]::Matches($h2, '<section')).Count - ([regex]::Matches($h2, '</section>')).Count
$d = ([regex]::Matches($h2, '<details[ >]')).Count - ([regex]::Matches($h2, '</details>')).Count
$a = ([regex]::Matches($h2, 'eq-answer"')).Count
$e = ([regex]::Matches($h2, 'eq-explanation"')).Count
Write-Host ""
Write-Host "POST-CLEAN: section=$s details=$d answers=$a explanations=$e gap=$($a-$e)"
