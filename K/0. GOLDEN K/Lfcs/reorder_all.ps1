$file = "c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Lfcs\linux_cli.html"
$c = [System.IO.File]::ReadAllText($file)
$articles = [regex]::Split($c, '(?=<article\b)')
$fixed = 0

for ($i = 0; $i -lt $articles.Count; $i++) {
    $a = $articles[$i]
    
    # Check if this article has syntax, params, RV, and examples
    if ($a -notmatch 'syntax-header') { continue }
    
    # Find positions of key elements
    $syntaxIdx = $a.IndexOf('syntax-header')
    $paramsIdx = $a.IndexOf('<h4>Parameters</h4>')
    $rvIdx = $a.IndexOf('<h4>Return Value</h4>')
    # Find first Context heading
    $ctxMatch = [regex]::Match($a, '<h4>📁 Context[^<]*</h4>')
    $ctxIdx = if ($ctxMatch.Success) { $ctxMatch.Index } else { -1 }
    $exIdx = $a.IndexOf('<h4>Examples</h4>')
    
    # Check if order is wrong
    $positions = @(
        @{Name='Syntax'; Idx=$syntaxIdx},
        @{Name='Params'; Idx=$paramsIdx},
        @{Name='RV'; Idx=$rvIdx},
        @{Name='Context'; Idx=$ctxIdx},
        @{Name='Examples'; Idx=$exIdx}
    ) | Where-Object { $_.Idx -ge 0 }
    
    $inOrder = $true
    for ($j = 1; $j -lt $positions.Count; $j++) {
        if ($positions[$j].Idx -lt $positions[$j-1].Idx) { $inOrder = $false; break }
    }
    if ($inOrder) { continue }
    
    # Extract blocks and rearrange
    # Find blocks by matching from <h4> to next <h4> or </article>
    $blocks = @()
    $h4s = [regex]::Matches($a, '<h4[^>]*>[^<]*</h4>')
    for ($j = 0; $j -lt $h4s.Count; $j++) {
        $start = $h4s[$j].Index
        $end = if ($j + 1 -lt $h4s.Count) { $h4s[$j+1].Index } else { $a.IndexOf('</article>', $start) }
        if ($end -lt 0) { $end = $a.Length }
        $label = $h4s[$j].Value
        $blocks += @{Label=$label; Start=$start; End=$end; Content=$a.Substring($start, $end - $start)}
    }
    
    # Content before first h4
    $preContent = ''
    if ($h4s.Count -gt 0) {
        $preContent = $a.Substring(0, $h4s[0].Index)
    }
    
    # Desired order: Syntax -> Params -> RV -> Context -> Examples -> (other)
    $orderedBlocks = @()
    $used = @{}
    
    foreach ($target in @('Syntax', 'Parameters</h4>', 'Return Value</h4>', '📁 Context', 'Examples</h4>')) {
        foreach ($b in $blocks) {
            if ($used.ContainsKey($b.Start)) { continue }
            if ($b.Label -match $target) {
                $orderedBlocks += $b
                $used[$b.Start] = $true
                break
            }
        }
    }
    # Add remaining blocks
    foreach ($b in $blocks) {
        if (-not $used.ContainsKey($b.Start)) {
            $orderedBlocks += $b
        }
    }
    
    # Rebuild article
    $result = $preContent
    foreach ($b in $orderedBlocks) {
        $result += $b.Content
    }
    # Add closing </article> if not included
    if ($result -notmatch '</article>\s*$') {
        $result += "`r`n            </article>"
        # Clean up multiple </article> tags
        $result = $result -replace '(?s)</article>\s*</article>', '</article>'
    }
    
    $articles[$i] = $result
    $fixed++
    if ($a -match 'id="([^"]+)"') { Write-Output "Reordered: $($Matches[1])" }
}

$c = $articles -join ''
[System.IO.File]::WriteAllText($file, $c)
Write-Output "Total reordered: ${fixed}"