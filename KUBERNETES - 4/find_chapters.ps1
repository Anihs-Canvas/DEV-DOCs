$c = Get-Content "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 4\OpenShift_pro.html" -Raw

foreach ($id in @("ch1","ch2","ch3","ch4","ch5","ch32","ch33","ch34","ch35","ch36","ch37","ch38","ch39")) {
    $pattern = 'id="' + $id + '"[^>]*>(.{0,250}?)</(?:h[1-4]|section|div)>'
    $m = [regex]::Match($c, $pattern)
    if ($m.Success) {
        $txt = $m.Groups[1].Value -replace '<[^>]+>', '' -replace '\s+', ' '
        Write-Output "$id : $txt"
    } else {
        $pattern2 = 'id="' + $id + '"'
        $m2 = [regex]::Match($c, $pattern2)
        if ($m2.Success) {
            $pos = $m2.Index
            $ctx = $c.Substring($pos, [Math]::Min(250, $c.Length - $pos)) -replace '<[^>]+>', '' -replace '\s+', ' '
            Write-Output "$id (broad): $ctx"
        } else {
            Write-Output "$id : NOT FOUND"
        }
    }
}