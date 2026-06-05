$f = "KCSA.html"
$c = Get-Content $f -Raw

# Search for "nothing allowed" case-insensitive
$pattern = [regex]::new("nothing allowed", [Text.RegularExpressions.RegexOptions]::IgnoreCase)
$m = $pattern.Match($c)
if ($m.Success) {
    $idx = $m.Index
    Write-Host "Found at position $idx"
    Write-Host "Context: " + $c.Substring([Math]::Max(0,$idx-20), [Math]::Min(100, $c.Length-$idx+20))
} else {
    Write-Host "NOT FOUND - searching for Q2 text"
    # Try finding "Empty podSelector"
    $idx = $c.IndexOf("Empty podSelector")
    if ($idx -ge 0) {
        Write-Host "Found Q2 at $idx"
        Write-Host "Context: " + $c.Substring([Math]::Max(0,$idx-50), [Math]::Min(300, $c.Length-$idx+50))
    }
}