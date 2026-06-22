#!/usr/bin/env python3
"""Targeted fix for specific remaining patterns."""
import sys

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Manual mapping of known corruption patterns
# These were identified from reading the corrupted file
REPLACEMENTS = {}

# Build a dict of all unique corrupted sequences and their fixes
# by scanning through the file looking for fixable sequences
i = 0
while i < len(content):
    ch = content[i]
    cp = ord(ch)
    
    if cp > 127 and cp not in (0x200B,):  # skip zero-width spaces
        for length in range(2, 10):
            if i + length > len(content):
                break
            candidate = content[i:i+length]
            try:
                raw = candidate.encode("cp1252")
                fixed = raw.decode("utf-8")
                if fixed != candidate and len(fixed) < len(candidate):
                    # Validate: fixed should not contain C0/C1 control chars
                    bad = False
                    for fc in fixed:
                        fcp = ord(fc)
                        if fcp < 0x20 and fcp not in (0x0A, 0x0D, 0x09):
                            bad = True
                            break
                        if 0x7F <= fcp <= 0x9F:
                            bad = True
                            break
                    if not bad:
                        REPLACEMENTS[candidate] = fixed
            except:
                pass
    i += 1

print(f"Found {len(REPLACEMENTS)} unique fixable sequences")

# Apply replacements (longest first to avoid partial matches)
fixes = 0
for old, new in sorted(REPLACEMENTS.items(), key=lambda x: -len(x[0])):
    if old in content:
        count = content.count(old)
        content = content.replace(old, new)
        fixes += count
        print(f"  {repr(old)} -> {new} ({count}x)")

print(f"Applied {fixes} total replacements")

if fixes > 0:
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("File written successfully")
else:
    print("Checking for remnants...")
    # Check if there are actually any corrupt sequences left
    for idx, ch in enumerate(content):
        if 0x80 <= ord(ch) <= 0x9F:
            start = max(0, idx-8)
            end = min(len(content), idx+8)
            ctx = content[start:end]
            print(f"  pos {idx}: U+{ord(ch):04X} in: {repr(ctx)}")
            break
    # Also check for ð patterns
    for idx, ch in enumerate(content):
        if ord(ch) == 0xF0:
            ctx = content[idx:idx+10]
            print(f"  pos {idx}: F0 in: {repr(ctx)}")
            break
    for idx, ch in enumerate(content):
        if ord(ch) == 0xE2:
            ctx = content[idx:idx+10]
            # Only show if followed by non-ASCII
            if idx+1 < len(content) and ord(content[idx+1]) > 127:
                print(f"  pos {idx}: E2 in: {repr(ctx)}")
                break
