#!/usr/bin/env python3
"""Fix remaining corrupted emoji via direct byte-level repair."""
import sys

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

# Read as raw bytes
with open(FILE, "rb") as f:
    data = f.read()

fixes = 0

# Pattern 1: C3 B0 C5 B8 22 C2 8D -> F0 9F 94 8D (🔍)
# "ðŸ"" (corrupted) -> 🔍
old = b'\xC3\xB0\xC5\xB8\x22\xC2\x8D'
new = b'\xF0\x9F\x94\x8D'  # 🔍
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: ðŸ"\\x8d -> 🔍')

# Pattern 2: C3 B0 C5 B8 22 C2 90 -> F0 9F 93 90 (📐)
old = b'\xC3\xB0\xC5\xB8\x22\xC2\x90'
new = b'\xF0\x9F\x93\x90'  # 📐
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: ðŸ"\\x90 -> 📐')

# Pattern 3: C3 B0 C5 B8 C2 8F E2 80 94 C3 AF C2 B8 C2 8F -> 🏗️
# ðŸ\x8f—ï¸\x8f -> 🏗️ (U+1F3D7 + U+FE0F)
old = b'\xC3\xB0\xC5\xB8\xC2\x8F\xE2\x80\x94\xC3\xAF\xC2\xB8\xC2\x8F'
new = b'\xF0\x9F\x8F\x97\xEF\xB8\x8F'  # 🏗️
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: corrupted 🏗️')

# Pattern 4: C3 B0 C5 B8 C2 8F E2 80 A0 -> 🏆
# ðŸ\x8f† -> 🏆 (U+1F3C6)
# Wait, let me check: the corruption is 'ðŸ\x8f†' = C3 B0 C5 B8 C2 8F E2 80 A0
# That should be F0 9F 8F 86 (🏆)
old = b'\xC3\xB0\xC5\xB8\xC2\x8F\xE2\x80\xA0'
new = b'\xF0\x9F\x8F\x86'  # 🏆
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: corrupted 🏆')

# Pattern 5: â (smart quote corruption) -> "
# C3 A2 E2 82 AC E2 80 9C -> E2 80 9C (") but wait, this might be wrong
# Let me check what 'â' actually is...
# Actually this is C3 A2 C2 80 C2 9C which is the corrupted "
# But we don't have this pattern anymore, let me skip for now

# Pattern 6: 'â€”' (C3 A2 E2 82 AC E2 80 9D) -> '—' (E2 80 94) em dash
# â€" -> — (em dash)
old = b'\xC3\xA2\xE2\x82\xAC\xE2\x80\x94'
new = b'\xE2\x80\x94'  # — (em dash)
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â€" -> —')

# Pattern 7: 'â€œ' (C3 A2 E2 82 AC E2 80 9C) -> '"' (E2 80 9C) left smart quote
old = b'\xC3\xA2\xE2\x82\xAC\xE2\x80\x9C'
new = b'\xE2\x80\x9C'  # " (left double quote)
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â€œ -> "')

# Pattern 8: 'â€' (C3 A2 E2 82 AC E2 80 9D) -> '"' (E2 80 9D) right smart quote  
old = b'\xC3\xA2\xE2\x82\xAC\xC2\x9D'  # Wait, this might be different
# Let me check: â€ is C3 A2 E2 82 AC. Then  is C2 9D.
# So â€ = C3 A2 E2 82 AC C2 9D -> E2 80 9D (right double quote)
old = b'\xC3\xA2\xE2\x82\xAC\xC2\x9D'
new = b'\xE2\x80\x9D'  # " (right double quote)
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â€\\x9d -> "')

# Pattern 9: 'â€¢' -> '•' (bullet, E2 80 A2)
old = b'\xC3\xA2\xE2\x82\xAC\xC2\xA2'
new = b'\xE2\x80\xA2'  # • (bullet)
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â€¢ -> •')

# Pattern 10: 'â€¦' -> '…' (ellipsis, E2 80 A6)
old = b'\xC3\xA2\xE2\x82\xAC\xC2\xA6'
new = b'\xE2\x80\xA6'  # … (ellipsis)
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â€¦ -> …')

# Pattern 11: â• -> ═ (box drawing double horizontal)
# C3 A2 E2 80 A2 C2 90 -> E2 95 90
old = b'\xC3\xA2\xE2\x80\xA2\xC2\x90'
new = b'\xE2\x95\x90'  # ═
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f'Fixed {count}x: â•\x90 -> ═')

print(f'Total fixes: {fixes}')

if fixes > 0:
    with open(FILE, "wb") as f:
        f.write(data)
    print("File written successfully")
