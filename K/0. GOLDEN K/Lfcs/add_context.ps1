$c = [System.IO.File]::ReadAllText("linux_cli.html")
$fixed = 0

# Add Context to compact sections before Examples
$addContext = @{
    'vgremove-cmd' = "<h4>📁 Context: anihpj/jobpost — Remove Volume Group</h4><pre><code class=`"language-bash`">carol@prod-api-01:~$ sudo vgremove old_vg`r`n  Volume group `"old_vg`" successfully removed</code></pre>"
    'pvremove-cmd' = "<h4>📁 Context: anihpj/jobpost — Remove Physical Volume</h4><pre><code class=`"language-bash`">carol@prod-api-01:~$ sudo pvremove /dev/sdc1`r`n  Labels on physical volume `"/dev/sdc1`" successfully wiped</code></pre>"
    'atq-cmd' = "<h4>📁 Context: anihpj/jobpost — List Pending Jobs</h4><pre><code class=`"language-bash`">carol@prod-api-01:~$ atq`r`n5`tThu Jun  5 02:00:00 2026 a carol</code></pre>"
    'atrm-cmd' = "<h4>📁 Context: anihpj/jobpost — Remove Scheduled Job</h4><pre><code class=`"language-bash`">carol@prod-api-01:~$ atq && atrm 5 && atq</code></pre>"
}

foreach ($id in $addContext.Keys) {
    $pattern = "(?s)id=`"${id}`".*?<h4>Examples</h4>"
    if ($c -match $pattern) {
        $pos = $c.IndexOf($Matches[0]) + $Matches[0].Length
        $c = $c.Insert($pos - '<h4>Examples</h4>'.Length, $addContext[$id] + "`r`n                ")
        $fixed++
        Write-Output "Added Context: ${id}"
    } else {
        Write-Output "NOT FOUND: ${id}"
    }
}

[System.IO.File]::WriteAllText("linux_cli.html", $c)
Write-Output "Fixed: ${fixed}"
