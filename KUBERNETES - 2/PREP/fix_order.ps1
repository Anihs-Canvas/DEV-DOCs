$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\PREP\argocd_test_Prep.html"
$c = [System.IO.File]::ReadAllText($f)

$m1s = '<!-- ═══════════════ 3.4 Advanced Canary Strategies ═══════════════ -->'
$m1e = '    <!-- ═══════════════ CATEGORY 4: ARGO EVENTS ═══════════════ -->'
$m2s = '<!-- ═══════════════ 4.3 Advanced Event Patterns ═══════════════ -->'
$m2e = '    <!-- ═══════════════ 1.6 Advanced Workflow Patterns ══════════'
$mIns = '    <!-- ═══════════════════════════════════════════ -->'

$p1s = $c.IndexOf($m1s)
$p1e = $c.IndexOf($m1e)
$p2s = $c.IndexOf($m2s)
$p2e = $c.IndexOf($m2e)
$pIns = $c.IndexOf($mIns)

"Positions: $p1s $p1e $p2s $p2e $pIns"

$block1 = $c.Substring($p1s, $p1e - $p1s)
$block2 = $c.Substring($p2s, $p2e - $p2s)

$new = $c.Substring(0, $p1s) + $c.Substring($p1e, $p2s - $p1e) + $c.Substring($p2e, $pIns - $p2e) + $block1 + $block2 + $c.Substring($pIns)

"Old: $($c.Length) New: $($new.Length)"

[System.IO.File]::WriteAllText($f, $new)
"Written."
