$file = 'Backstage.html'
$content = Get-Content $file -Raw -Encoding UTF8

$answers = [regex]::Matches($content, '<div class="eq-answer">')
$withExp = [regex]::Matches($content, '<div class="eq-answer">.*?</div><div class="eq-explanation">')

Write-Host "Total answers found: $($answers.Count)"
Write-Host "Answers with explanations: $($withExp.Count)"
Write-Host "Answers MISSING explanations: $($answers.Count - $withExp.Count)"

# Find which chapters have missing explanations
$chapters = [regex]::Matches($content, 'Chapter (\d+).*?CBA Practice Questions')
$lines = @()
foreach ($ch in $chapters) {
    $num = $ch.Groups[1].Value
    $lines += "Ch $num"
}
Write-Host "Chapters found: $($lines -join ', ')"
