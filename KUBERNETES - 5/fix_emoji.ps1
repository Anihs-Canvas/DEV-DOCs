$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$bytes = [System.IO.File]::ReadAllBytes($f)
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$origKB = [math]::Round($bytes.Length/1KB,0)
Write-Output "Original: $origKB KB"

# Build fix table: garbled sequence (as literal string) -> correct emoji
$fixes = @{}

# F0 9F 8E AF = U+1F3AF (target/dart) -> appears as "ðŸŽ¯"
$fixes['ðŸŽ¯'] = [char]0xD83C.ToString() + [char]0xDFAF.ToString()
# F0 9F 93 8B = U+1F4CB (clipboard) -> "ðŸ"‹" 
$fixes['ðŸ"‹'] = [char]0xD83D.ToString() + [char]0xDCCB.ToString()
# F0 9F 94 A7 = U+1F527 (wrench) -> "ðŸ"§"
$fixes['ðŸ"§'] = [char]0xD83D.ToString() + [char]0xDD27.ToString()
# E2 9A A0 EF B8 8F = U+26A0 + VS16 (warning) -> "âš ï¸"
$fixes['âš ï¸'] = [char]0x26A0.ToString() + [char]0xFE0F.ToString()
$fixes['âš ï¸'] = [char]0x26A0.ToString() + [char]0xFE0F.ToString()
# E2 80 94 = U+2014 (em dash)
$fixes['â€"'] = [char]0x2014.ToString()
$fixes['â€˜'] = [char]0x2014.ToString()
# E2 86 92 = U+2192 (right arrow)
$fixes['â†\''] = [char]0x2192.ToString()
$fixes['â†’'] = [char]0x2192.ToString()
# F0 9F 92 A1 = U+1F4A1 (lightbulb)
$fixes['ðŸ'¡'] = [char]0xD83D.ToString() + [char]0xDCA1.ToString()
# F0 9F 94 B1 = U+1F531 (trident)
$fixes['ðŸ"±'] = [char]0xD83D.ToString() + [char]0xDD31.ToString()
$fixes['ðŸ'±'] = [char]0xD83D.ToString() + [char]0xDD31.ToString()
# E2 9C 85 = U+2705 (checkmark)
$fixes['âœ…'] = [char]0x2705.ToString()
# E2 9D 8C = U+274C (cross mark)
$fixes['âœŒ'] = [char]0x274C.ToString()
# F0 9F 94 A5 = U+1F525 (fire)
$fixes['ðŸ"¥'] = [char]0xD83D.ToString() + [char]0xDD25.ToString()
# F0 9F 98 B0 = U+1F630 (anxious face)
$fixes['ðŸ˜°'] = [char]0xD83D.ToString() + [char]0xDE30.ToString()
# F0 9F 8E 89 = U+1F389 (party popper)
$fixes['ðŸŽ‰'] = [char]0xD83C.ToString() + [char]0xDF89.ToString()
# F0 9F 93 A6 = U+1F4E6 (package)
$fixes['ðŸ"¦'] = [char]0xD83D.ToString() + [char]0xDCE6.ToString()
# F0 9F 93 A1 = U+1F4E1 (satellite antenna)
$fixes['ðŸ"¡'] = [char]0xD83D.ToString() + [char]0xDCE1.ToString()
# F0 9F 8F 97 = U+1F3D7 (building construction) 
$fixes['ðŸ\x8f—'] = [char]0xD83C.ToString() + [char]0xDFD7.ToString()
# F0 9F 9F B0 = U+1F7F0
$fixes['ðŸŸ°'] = [char]0xD83D.ToString() + [char]0xDFF0.ToString()
# F0 9F 93 8A = U+1F4CA (chart)
$fixes['ðŸ"Š'] = [char]0xD83D.ToString() + [char]0xDCCA.ToString()

$count = 0
foreach ($bad in $fixes.Keys) {
    if ($text.Contains($bad)) {
        $text = $text.Replace($bad, $fixes[$bad])
        $count++
        Write-Output "  Fixed: $bad"
    }
}

Write-Output "Fixed $count character sequences"
[System.IO.File]::WriteAllText($f, $text, [System.Text.UTF8Encoding]::new($true))
$newKB = [math]::Round((Get-Item $f).Length/1KB,0)
Write-Output "Done: $origKB -> $newKB KB"
