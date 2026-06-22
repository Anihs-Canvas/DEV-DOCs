#!/usr/bin/env python3
"""Fix remaining corrupted emoji - corrected byte patterns."""
FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "rb") as f:
    data = f.read()

fixes = 0

# Pattern A: C3 B0 C5 B8 E2 80 9D C2 8D -> F0 9F 94 8D (🔍)
# This is ðŸ" where " is U+201D (right smart quote)
old = b'\xC3\xB0\xC5\xB8\xE2\x80\x9D\xC2\x8D'
new = b'\xF0\x9F\x94\x8D'
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f"Fixed {count}x: corrupted 🔍")

# Pattern B: C3 B0 C5 B8 E2 80 9C C2 90 -> F0 9F 93 90 (📐)
old = b'\xC3\xB0\xC5\xB8\xE2\x80\x9C\xC2\x90'
new = b'\xF0\x9F\x93\x90'
count = data.count(old)
if count:
    data = data.replace(old, new)
    fixes += count
    print(f"Fixed {count}x: corrupted 📐")

# Pattern C: Find standalone C2 90 that are remnants of â• corruption
# The original was: E2 95 90 (═). The corrupted form was C3 A2 E2 80 A2 C2 90.
# But the C3 A2 E2 80 A2 part might have been fixed already, leaving just C2 90.
# These standalone C2 90 bytes need to be converted back.
# But we need context - let's check what's around these bytes.

# Let's look for the actual â• pattern with different byte encoding
# The display showed 'â•' - let me check the exact bytes of this text
# If it's C3 A2 E2 80 A2 C2 90, replace with E2 95 90
old_box = b'\xC3\xA2\xE2\x80\xA2\xC2\x90'
new_box = b'\xE2\x95\x90'  # ═
count_box = data.count(old_box)
print(f"Found {count_box}x â• pattern (C3 A2 E2 80 A2 C2 90)")
if count_box:
    data = data.replace(old_box, new_box)
    fixes += count_box
    print(f"Fixed {count_box}x: â• -> ═")

# Also check alternative encoding: C3 A2 C2 95 C2 90
old_box2 = b'\xC3\xA2\xC2\x95\xC2\x90'
count_box2 = data.count(old_box2)
print(f"Found {count_box2}x â• pattern (C3 A2 C2 95 C2 90)")
if count_box2:
    data = data.replace(old_box2, new_box)
    fixes += count_box2
    print(f"Fixed {count_box2}x: â•-> ═")

# Check at position where U+0090 appears (around line 84271 in chars)
# Find the context of standalone C2 90 bytes
print(f"\nStandalone U+0090 (C2 90) count: {data.count(b'\\xC2\\x90')}")
print(f"Standalone U+008D (C2 8D) count: {data.count(b'\\xC2\\x8D')}")
print(f"Standalone U+008F (C2 8F) count: {data.count(b'\\xC2\\x8F')}")
print(f"Standalone U+009D (C2 9D) count: {data.count(b'\\xC2\\x9D')}")

# Show context of first few C2 90 occurrences
pos = 0
for i in range(5):
    pos = data.find(b'\xC2\x90', pos)
    if pos == -1:
        break
    ctx = data[max(0,pos-10):pos+10]
    print(f"  C2 90 at byte {pos}: ...{' '.join(f'{b:02X}' for b in ctx)}...")
    pos += 1

print(f"\nTotal fixes applied: {fixes}")

if fixes > 0:
    with open(FILE, "wb") as f:
        f.write(data)
    print("File written successfully")
