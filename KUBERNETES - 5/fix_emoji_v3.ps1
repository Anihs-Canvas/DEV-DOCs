$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$bytes = [System.IO.File]::ReadAllBytes($f)
$origLen = $bytes.Length
Write-Output "Original: $origLen bytes"

$hex = -join ($bytes | ForEach { $_.ToString('X2') })
$fixed = 0

# Windows-1252 double-encoding patterns -> correct UTF-8
$map = @(
    # 4-byte emojis (F0 9F xx yy)
    @{O='C3B0C5B8E2809CE280B9'; N='F09F938B'},  # clipboard
    @{O='C3B0C5B8E2809CE280A6'; N='F09F94A7'},  # wrench
    @{O='C3B0C5B8E28099E280A1'; N='F09F92A1'},  # lightbulb
    @{O='C3B0C5B8E2809CE280A0'; N='F09F94A5'},  # fire
    @{O='C3B0C5B8E2809CE280B0'; N='F09F94B1'},  # trident
    @{O='C3B0C5B8CB9CE280B0'; N='F09F98B0'},    # anxious face
    @{O='C3B0C5B8E2809CE280A1'; N='F09F93A6'},  # package
    @{O='C3B0C5B8E2809CE280A0'; N='F09F93A1'},  # satellite  
    @{O='C3B0C5B8C5BDE280B0'; N='F09F8E89'},    # party popper
    # 3-byte symbols
    @{O='C3A2C593C285'; N='E29C85'},  # checkmark
    @{O='C3A2C593C28C'; N='E29D8C'}   # cross
)

foreach ($r in $map) {
    $before = $hex.Length
    $hex = $hex.Replace($r.O, $r.N)
    $diff = ($before - $hex.Length)
    if ($diff -gt 0) {
        $cnt = $diff / ($r.O.Length - $r.N.Length)
        Write-Output "  Fixed $cnt : $($r.O.Substring(0,8))..."
        $fixed += $cnt
    }
}

if ($fixed -gt 0) {
    $newBytes = [byte[]]::new($hex.Length / 2)
    for ($i = 0; $i -lt $hex.Length; $i += 2) {
        $newBytes[$i/2] = [Convert]::ToByte($hex.Substring($i, 2), 16)
    }
    $text = [System.Text.Encoding]::UTF8.GetString($newBytes)
    [System.IO.File]::WriteAllText($f, $text, [System.Text.UTF8Encoding]::new($true))
    $newLen = (Get-Item $f).Length
    Write-Output "Done: $origLen -> $newLen bytes"
    Write-Output "Total fixes: $fixed"
} else {
    Write-Output "No changes needed"
}
