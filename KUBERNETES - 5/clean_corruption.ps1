$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$origKB = [math]::Round($html.Length/1KB,0)
Write-Output "Size: $origKB KB"
Write-Output "Scanning for corruption..."

$removed = 0

# Pattern 1: <pre> blocks that split words (letter on both sides)
$pat = '(?<=[a-zA-Z])<pre><code>[^<]*</code></pre>(?=[a-zA-Z])'
$m1 = [regex]::Matches($html, $pat)
Write-Output "Word-splitting <pre> blocks: $($m1.Count)"

# Process in reverse order
$allRemovals = @()
foreach ($m in $m1) {
    $allRemovals += @{ Pos = $m.Index; Len = $m.Length }
}

# Pattern 2: <pre> blocks injected into tag attributes
$pat2 = '<pre><code>[^<]*</code></pre>'
$m2 = [regex]::Matches($html, $pat2, [System.Text.RegularExpressions.RegexOptions]::Singleline)
foreach ($m in $m2) {
    $pos = $m.Index
    # Check if inside a tag (find last < before this position, and next > after)
    $lastTag = $html.LastIndexOf('<', $pos)
    $nextClose = $html.IndexOf('>', $pos)
    if ($lastTag -gt 0 -and $nextClose -gt $pos) {
        $tagContent = $html.Substring($lastTag, $nextClose - $lastTag + 1)
        if ($tagContent -match '^<(div|span|p|h\d)\s' -and $tagContent -notmatch '</') {
            $allRemovals += @{ Pos = $pos; Len = $m.Length }
        }
    }
}

Write-Output "Total blocks to remove: $($allRemovals.Count)"

# Deduplicate by position (keep only one per position) and sort reverse
$seen = @{}
$unique = @()
foreach ($r in ($allRemovals | Sort-Object -Property Pos -Descending)) {
    $key = "$($r.Pos)"
    if (-not $seen.ContainsKey($key)) {
        $seen[$key] = $true
        $unique += $r
    }
}
$cnt = 0
foreach ($r in $unique) {
    $html = $html.Substring(0, $r.Pos) + $html.Substring($r.Pos + $r.Len)
    $cnt++
}

Write-Output "Removed: $cnt blocks"
Write-Output "Writing..."

[System.IO.File]::WriteAllText($f, $html, [System.Text.UTF8Encoding]::new($true))
$newKB = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Output "Done. $origKB KB -> $newKB KB"
