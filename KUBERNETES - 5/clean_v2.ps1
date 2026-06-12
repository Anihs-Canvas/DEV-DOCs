$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$origKB = [math]::Round($html.Length/1KB,0)
Write-Output "Size: $origKB KB"

# Find ALL <pre> blocks
$pat = '<pre><code>[^<]*</code></pre>'
$all = [regex]::Matches($html, $pat, [System.Text.RegularExpressions.RegexOptions]::Singleline)
Write-Output "Total <pre> blocks in file: $($all.Count)"

# Classify each block
$toRemove = @()
$kept = 0
$removedWord = 0
$removedTag = 0
$removedNested = 0

for ($i = 0; $i -lt $all.Count; $i++) {
    $m = $all[$i]
    $pos = $m.Index
    $len = $m.Length
    
    $before = if ($pos -gt 0) { $html[$pos - 1] } else { " " }
    $after = if ($pos + $len -lt $html.Length) { $html[$pos + $len] } else { " " }
    
    $remove = $false
    
    # Rule 1: Splits a word (letter both sides)
    if ($before -match '[a-zA-Z]' -and $after -match '[a-zA-Z]') {
        $remove = $true
        $removedWord++
    }
    
    # Rule 2: Inside a tag attribute (before is > or " and after is " or letter)
    if ($before -match '[>"]' -and $after -match '[a-zA-Z"]') {
        $remove = $true
        $removedTag++
    }
    
    # Rule 3: Nested inside another <pre> (check if we're inside an unclosed <pre>)
    $context = $html.Substring([Math]::Max(0, $pos - 500), [Math]::Min(500, $pos))
    $opens = ([regex]::Matches($context, '<pre>')).Count
    $closes = ([regex]::Matches($context, '</pre>')).Count
    if ($opens -gt $closes) {
        $remove = $true
        $removedNested++
    }
    
    if ($remove) {
        $toRemove += @{ Pos = $pos; Len = $len }
    } else {
        $kept++
    }
}

Write-Output "Keeping: $kept | Removing word-splits: $removedWord | tag-splits: $removedTag | nested: $removedNested"
Write-Output "Total to remove: $($toRemove.Count)"

# Deduplicate by position
$seen = @{}
$unique = @()
foreach ($r in ($toRemove | Sort-Object -Property Pos -Descending)) {
    if (-not $seen.ContainsKey("$($r.Pos)")) {
        $seen["$($r.Pos)"] = $true
        $unique += $r
    }
}

Write-Output "Unique removals: $($unique.Count)"

# Apply removals
$cnt = 0
foreach ($r in $unique) {
    $html = $html.Substring(0, $r.Pos) + $html.Substring($r.Pos + $r.Len)
    $cnt++
}

Write-Output "Removed: $cnt"
Write-Output "Writing..."

[System.IO.File]::WriteAllText($f, $html, [System.Text.UTF8Encoding]::new($true))
$newKB = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Output "Done: $origKB -> $newKB KB"

# Quick verify
$h2 = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)
$remaining = ([regex]::Matches($h2, '[a-z]<pre><code>[^<]*</code></pre>[a-z]')).Count
Write-Output "Remaining word-splits: $remaining"
