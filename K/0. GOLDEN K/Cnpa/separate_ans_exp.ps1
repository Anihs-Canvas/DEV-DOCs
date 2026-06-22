
$file = 'c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html'
$txt = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# Simple: Replace Explanation label to be preceded by Answer label
$old1 = '<p class="eq-exp-label">Explanation</p>'
$new1 = '<p class="ans-section-label">Answer</p><p class="eq-exp-label">Explanation</p>'
$txt = $txt.Replace($old1, $new1)
$count1 = ([regex]::Matches($txt, '<p class="ans-section-label">')).Count
Write-Host "Answer labels added: $count1"

[System.IO.File]::WriteAllText($file, $txt, (New-Object System.Text.UTF8Encoding $true))
