$c = Get-Content "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html" -Raw

# Extract chapter headings near id="chNN"
Write-Output "=== CHAPTER HEADINGS (from body) ==="
$chHeadingMatches = [regex]::Matches($c, 'id="(ch\d+[a-c]?)"[^>]*>(?:.*?\n)?.*?<(?:h[1-4])\s*[^>]*>(.*?)</(?:h[1-4])>')
$shown = 0
$titles = @{}
foreach ($m in $chHeadingMatches) {
    $chId = $m.Groups[1].Value
    $title = $m.Groups[2].Value -replace '<[^>]+>', '' -replace '\s+', ' ' -replace '^\d+\.?\s*', ''
    $titles[$chId] = $title.Trim()
    Write-Output "$chId : $($title.Trim())"
    $shown++
}

Write-Output "`nCount: $shown"

# Also try to find via sidebar links
Write-Output "`n=== SIDEBAR LINKS ==="
$sidebarLinks = [regex]::Matches($c, 'href="#(ch\d+[a-c]?)"[^>]*?>([^<]+)')
$shown = 0
foreach ($m in $sidebarLinks) {
    $chId = $m.Groups[1].Value
    $title = $m.Groups[2].Value.Trim()
    if (-not $titles.ContainsKey($chId) -or $titles[$chId] -eq "") {
        $titles[$chId] = $title
    }
    Write-Output "$chId : $title"
    $shown++
}

Write-Output "`nCount: $shown"
Write-Output "`n=== MERGED TITLES ==="
foreach ($k in ($titles.Keys | Sort-Object { ($k -replace '[^0-9]','0').PadLeft(10,'0') })) {
    Write-Output "$k : $($titles[$k])"
}