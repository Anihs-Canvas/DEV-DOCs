# Fix double-encoded UTF-8 in networking.html
# Approach: Read as bytes, find double-encoded patterns, replace with correct UTF-8

$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"

# Read raw bytes
$bytes = [System.IO.File]::ReadAllBytes($f)
$origLen = $bytes.Length
Write-Output "Original size: $origLen bytes ($([math]::Round($origLen/1KB,1)) KB)"

# Build hex string from bytes for searching
$hex = -join ($bytes | ForEach-Object { $_.ToString('X2') })
Write-Output "Converted to hex string: $($hex.Length) chars"

# Define replacements: [doubleEncodedHex] -> [correctHex]
# Pattern: original UTF-8 bytes -> interpreted as Latin-1 chars -> re-encoded as UTF-8
$replacements = @()

# F0 9F 8E AF -> C3 B0 C5 B8 C5 BD C2 AF  (target/dart emoji)
$replacements += @{ Old = 'C3B0C5B8C5BDC2AF'; New = 'F09F8EAF' }

# F0 9F 93 8B -> C3 B0 C5 B8 E2 80 9C C2 8B  (clipboard)
$replacements += @{ Old = 'C3B0C5B8E2809CC28B'; New = 'F09F938B' }

# F0 9F 94 A7 -> C3 B0 C5 B8 E2 80 9C C2 A7  (wrench)
$replacements += @{ Old = 'C3B0C5B8E2809CC2A7'; New = 'F09F94A7' }

# F0 9F 92 A1 -> C3 B0 C5 B8 E2 80 99 C2 A1  (lightbulb)
$replacements += @{ Old = 'C3B0C5B8E28099C2A1'; New = 'F09F92A1' }

# F0 9F 94 A5 -> C3 B0 C5 B8 E2 80 9C C2 A5  (fire)
$replacements += @{ Old = 'C3B0C5B8E2809CC2A5'; New = 'F09F94A5' }

# F0 9F 94 B1 -> C3 B0 C5 B8 E2 80 9C C2 B1  (trident)
$replacements += @{ Old = 'C3B0C5B8E2809CC2B1'; New = 'F09F94B1' }

# E2 9A A0 EF B8 8F -> C3 A2 C5 A1 C2 A0 C3 AF C2 B8 C2 8F  (warning + VS16)
$replacements += @{ Old = 'C3A2C5A1C2A0C3AFC2B8C28F'; New = 'E29AA0EFB88F' }

# E2 9A A0 (warning without VS16)
$replacements += @{ Old = 'C3A2C5A1C2A0'; New = 'E29AA0' }

# EF B8 8F -> C3 AF C2 B8 C2 8F  (VS16 variation selector)
$replacements += @{ Old = 'C3AFC2B8C28F'; New = 'EFB88F' }

# E2 80 94 -> C3 A2 E2 82 AC  (em dash)
$replacements += @{ Old = 'C3A2E282AC'; New = 'E28094' }

# E2 86 92 -> C3 A2 E2 80 A0  (right arrow)
$replacements += @{ Old = 'C3A2E280A0'; New = 'E28692' }

# E2 86 92 variant (different double-encoding)
$replacements += @{ Old = 'C3A2E28099'; New = 'E28099' }

# F0 9F 98 B0 ->  (anxious face)
$replacements += @{ Old = 'C3B0C5B8CB9CC2B0'; New = 'F09F98B0' }

# F0 9F 8E 89 ->  (party popper)
$replacements += @{ Old = 'C3B0C5B8C5BDC289'; New = 'F09F8E89' }

# F0 9F 93 A6 ->  (package)
$replacements += @{ Old = 'C3B0C5B8E2809CC2A6'; New = 'F09F93A6' }

# F0 9F 93 A1 ->  (satellite)
$replacements += @{ Old = 'C3B0C5B8E2809CC2A1'; New = 'F09F93A1' }

$totalReplaced = 0
foreach ($r in $replacements) {
    $before = $hex.Length
    $hex = $hex.Replace($r.Old, $r.New)
    $after = $hex.Length
    $count = ($before - $after) / ($r.Old.Length - $r.New.Length)
    if ($count -gt 0) {
        Write-Output "  Fixed $count instances of $($r.Old.Substring(0, [Math]::Min(8,$r.Old.Length)))..."
        $totalReplaced += $count
    }
}

Write-Output "Total replacements: $totalReplaced"

if ($totalReplaced -gt 0) {
    # Convert hex back to bytes
    $newBytes = New-Object byte[] ($hex.Length / 2)
    for ($i = 0; $i -lt $hex.Length; $i += 2) {
        $newBytes[$i/2] = [Convert]::ToByte($hex.Substring($i, 2), 16)
    }
    
    # Write back with UTF-8 BOM
    $utf8Bom = [System.Text.UTF8Encoding]::new($true)
    $text = [System.Text.Encoding]::UTF8.GetString($newBytes)
    [System.IO.File]::WriteAllText($f, $text, $utf8Bom)
    
    $finalLen = (Get-Item $f).Length
    Write-Output "Done: $origLen -> $finalLen bytes ($([math]::Round($finalLen/1KB,1)) KB)"
} else {
    Write-Output "No replacements needed - file may already be correct"
}
