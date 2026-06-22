#!/usr/bin/env python3
"""Final comprehensive fix for ALL remaining corrupted emoji/character patterns."""
FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "rb") as f:
    data = f.read()

fixes = 0

# Map of corrupted byte sequences -> correct byte sequences
# Each corruption: original UTF-8 byte partially misinterpreted as cp1252 chars

REPLACEMENTS = [
    # âŒ -> ❌  (C3 A2 C2 9D C5 92 -> E2 9D 8C)
    (b'\xC3\xA2\xC2\x9D\xC5\x92', b'\xE2\x9D\x8C'),
    
    # â±ï¸ -> ⏱️  (corrupted variation selector)
    (b'\xC3\xA2\xC2\x8F\xC2\xB1\xC3\xAF\xC2\xB8\xC2\x8F', b'\xE2\x8F\xB1\xEF\xB8\x8F'),
    
    # ⚠ï¸ -> ⚠️  (E2 9A A0 preserved, C3 AF C2 B8 C2 8F -> EF B8 8F)
    (b'\xE2\x9A\xA0\xC3\xAF\xC2\xB8\xC2\x8F', b'\xE2\x9A\xA0\xEF\xB8\x8F'),
    
    # 🛡ï¸ -> 🛡️  (F0 9F 9B A1 preserved, C3 AF C2 B8 C2 8F -> EF B8 8F)
    (b'\xF0\x9F\x9B\xA1\xC3\xAF\xC2\xB8\xC2\x8F', b'\xF0\x9F\x9B\xA1\xEF\xB8\x8F'),
    
    # ☸ï¸ -> ☸️  (E2 98 B8 preserved, C3 AF C2 B8 C2 8F -> EF B8 8F)
    (b'\xE2\x98\xB8\xC3\xAF\xC2\xB8\xC2\x8F', b'\xE2\x98\xB8\xEF\xB8\x8F'),
    
    # ✈ï¸ -> ✈️  (E2 9C 88 preserved, C3 AF C2 B8 C2 8F -> EF B8 8F)
    (b'\xE2\x9C\x88\xC3\xAF\xC2\xB8\xC2\x8F', b'\xE2\x9C\x88\xEF\xB8\x8F'),
    
    # â” -> └ (box-drawing) C3 A2 C2 94 C2 90 -> E2 94 90
    (b'\xC3\xA2\xC2\x94\xC2\x90', b'\xE2\x94\x90'),
]

for old, new in REPLACEMENTS:
    count = data.count(old)
    if count:
        data = data.replace(old, new)
        fixes += count
        print(f"Fixed {count:3d}x: {old.hex(' ')} -> {new.hex(' ')}")

print(f"\nTotal fixes: {fixes}")

if fixes > 0:
    with open(FILE, "wb") as f:
        f.write(data)
    print("File written successfully")

# Final verification
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

bad = 0
for ch in content:
    if 0x80 <= ord(ch) <= 0x9F:
        bad += 1
print(f"\nRemaining U+0080-U+009F control chars: {bad}")
