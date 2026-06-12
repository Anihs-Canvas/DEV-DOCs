$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
Write-Host "Reading file..."
$html = Get-Content $f -Raw
Write-Host "File size: $([math]::Round($html.Length/1KB,0)) KB"

# Helper: replace chapter practice block with one that has explanations
function Replace-ChapterBlock($html, $chNum, $newBlockContent) {
    $marker = "CH${chNum}_FIX_MARKER"
    Write-Host "Processing Chapter $chNum..."
    $result = $html -replace $marker, $newBlockContent
    if ($result -eq $html) {
        Write-Host "  WARNING: Marker not found, trying direct replacement..."
        $heading = "Chapter $chNum"
        $pos = $html.IndexOf($heading)
        if ($pos -ge 0) {
            $endPos = $html.IndexOf('</section>', $pos + 1000)
            if ($endPos -lt 0) { $endPos = $pos + 50000 }
            # Find the practice questions block
            $pqStart = $html.IndexOf('net-exam-questions', $pos)
            $pqEnd = $html.IndexOf('</div>', $html.IndexOf('</div>', $pqStart + 5000) + 100)
            if ($pqStart -ge 0) {
                $before = $html.Substring(0, $pqStart)
                $after = $html.Substring($pqStart + 100)
                $result = $before + $newBlockContent + $after
                Write-Host "  Direct replacement done"
            }
        }
    }
    return $result
}

# Place markers first, then replace
Write-Host "Placing markers..."
$chapters = @(7, 8, 9, 10, 18, 19, 20, 21, 22, 23)
foreach ($ch in $chapters) {
    $heading = "Chapter $ch — Networking Practice Questions"
    $marker = "CH${ch}_FIX_MARKER"
    $html = $html -replace $heading, $marker
    Write-Host "  Ch $ch marked"
}
Set-Content $f $html -NoNewline
Write-Host "Markers placed. Proceeding to replace..."
