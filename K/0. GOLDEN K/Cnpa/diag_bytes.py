#!/usr/bin/env python3
"""Diagnose remaining corruption patterns."""
FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "rb") as f:
    data = f.read()

# Find the character offset 250641 in byte terms
char_count = 0
byte_pos = 0
target_char = 250641
while byte_pos < len(data) and char_count < target_char:
    b = data[byte_pos]
    if b < 0x80:
        byte_pos += 1
    elif b < 0xE0:
        byte_pos += 2
    elif b < 0xF0:
        byte_pos += 3
    else:
        byte_pos += 4
    char_count += 1

print(f"Character {char_count} starts at byte position {byte_pos}")
print(f"Bytes: {' '.join(f'{b:02X}' for b in data[byte_pos:byte_pos+16])}")

# Search for C3 B0 C5 B8 pattern (corrupted ðŸ)
pattern = b'\xC3\xB0\xC5\xB8'
count = data.count(pattern)
print(f"\nOccurrences of C3 B0 C5 B8 (corrupted ðŸ): {count}")

# Find all positions
pos = 0
found = []
while True:
    pos = data.find(pattern, pos)
    if pos == -1:
        break
    found.append(pos)
    pos += 1

if found:
    print(f"At byte positions: {found[:10]}")
    for p in found[:5]:
        chunk = data[p:p+12]
        print(f"  byte {p}: {' '.join(f'{b:02X}' for b in chunk)}")
        print(f"  as utf8: {chunk.decode('utf-8', errors='replace')}")

# Also check for the â• pattern
pattern2 = b'\xC3\xA2\xE2\x80\xA2\xC2\x90'
count2 = data.count(pattern2)
print(f"\nOccurrences of C3 A2 E2 80 A2 C2 90 (â•): {count2}")

# Just C2 90
count3 = data.count(b'\xC2\x90')
print(f"Occurrences of C2 90 (U+0090 control char): {count3}")
count4 = data.count(b'\xC2\x8D')
print(f"Occurrences of C2 8D (U+008D control char): {count4}")
count5 = data.count(b'\xC2\x9D')
print(f"Occurrences of C2 9D (U+009D control char): {count5}")
count6 = data.count(b'\xC2\x8F')
print(f"Occurrences of C2 8F (U+008F control char): {count6}")
