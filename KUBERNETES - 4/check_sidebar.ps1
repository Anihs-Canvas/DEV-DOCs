$c = Get-Content "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html" -Raw

# Find sidebar - look for different possible sidebar containers
Write-Output "=== SEARCHING FOR SIDEBAR ==="
$patterns = @(
    '(?s)<nav[^>]*>(.*?)</nav>',
    '(?s)<div[^>]*sidebar[^>]*>(.*?)</div>',
    '(?s)<aside[^>]*>(.*?)</aside>',
    '(?s)<ul[^>]*sidebar[^>]*>(.*?)</ul>'
)

$sidebarContent = ""
foreach ($pat in $patterns) {
    $matches = [regex]::Matches($c, $pat, 'IgnoreCase')
    Write-Output "Pattern: $($pat.Substring(0, [Math]::Min(50, $pat.Length)))... => $($matches.Count) matches"
    if ($matches.Count -gt 0 -and $sidebarContent -eq "") {
        $sidebarContent = $matches[0].Groups[1].Value
        Write-Output "Sidebar length: $($sidebarContent.Length) chars"
    }
}

if ($sidebarContent -eq "") {
    # Look for any element with class containing "sidebar" or "nav"
    $anySidebar = [regex]::Match($c, '(?s)<(\w+)[^>]*class="[^"]*sidebar[^"]*"[^>]*>(.{200,500})')
    if ($anySidebar.Success) {
        Write-Output "Found sidebar-like element:"
        Write-Output $anySidebar.Value.Substring(0, [Math]::Min(500, $anySidebar.Value.Length))
    } else {
        Write-Output "NO SIDEBAR FOUND - checking for any navigation structure"
        # Look for table of contents or navigation
        $toc = [regex]::Match($c, '(?s)(?:table.of.contents|toc|chapter.nav|chapter.list).{0,200}', 'IgnoreCase')
        if ($toc.Success) { Write-Output $toc.Value }
    }
}

# Extract sidebar hrefs and check against all ids
Write-Output "`n=== EXTRACTING SIDEBAR HREFS ==="
if ($sidebarContent.Length -gt 0) {
    $sidebarHrefs = [regex]::Matches($sidebarContent, 'href="#([^"]+)"')
    Write-Output "Sidebar hrefs found: $($sidebarHrefs.Count)"
    
    # Collect all ids
    $allIds = @{}
    $idMatches = [regex]::Matches($c, 'id="([^"]+)"')
    foreach ($m in $idMatches) { $allIds[$m.Groups[1].Value] = $true }
    
    $broken = @()
    foreach ($m in $sidebarHrefs) {
        $href = $m.Groups[1].Value
        if (-not $allIds.ContainsKey($href)) {
            $broken += $href
        }
    }
    
    if ($broken.Count -eq 0) {
        Write-Output "All sidebar links VALID!"
    } else {
        Write-Output "BROKEN SIDEBAR LINKS:"
        foreach ($b in $broken) { Write-Output "  #$b" }
    }
} else {
    # Fallback: find all href=# links that look like chapter/section anchors and check them
    Write-Output "No sidebar found - checking ALL href=#ch and href=#s links"
    $allHrefs = [regex]::Matches($c, 'href="#(ch\d+[a-c]?|s\d+-\w+)"')
    $allIds = @{}
    $idMatches = [regex]::Matches($c, 'id="([^"]+)"')
    foreach ($m in $idMatches) { $allIds[$m.Groups[1].Value] = $true }
    
    $broken = @{}
    foreach ($m in $allHrefs) {
        $href = $m.Groups[1].Value
        if (-not $allIds.ContainsKey($href) -and -not $broken.ContainsKey($href)) {
            $broken[$href] = $true
        }
    }
    
    if ($broken.Count -eq 0) {
        Write-Output "All chapter/section links VALID!"
    } else {
        Write-Output "BROKEN chapter/section links:"
        foreach ($b in ($broken.Keys | Sort-Object)) { Write-Output "  #$b" }
    }
}

# Also: show where the broken s31-4, s31-5, s36-x, s5-2x, s7-6x links are referenced
Write-Output "`n=== CONTEXT FOR PREVIOUSLY FOUND BROKEN LINKS ==="
$brokenIds = @("s31-4","s31-5","s36-1","s36-10","s36-2","s36-3","s36-4","s36-5","s36-6","s36-7","s36-8","s36-9","s5-2a","s5-2b","s5-2c","s7-6a","s7-6b","s7-6c")
foreach ($bid in $brokenIds) {
    $escaped = [regex]::Escape($bid)
    $refs = [regex]::Matches($c, "href=""#$escaped""[^>]*>(.{0,80})</a>")
    if ($refs.Count -gt 0) {
        foreach ($r in $refs) {
            $txt = $r.Groups[1].Value -replace '<[^>]+>', '' -replace '\s+', ' '
            Write-Output "  #$bid linked from: $txt"
        }
    }
}