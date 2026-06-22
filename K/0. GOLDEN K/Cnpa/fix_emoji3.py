#!/usr/bin/env python3
"""Test and fix specific corruption patterns."""
import sys

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Test specific patterns found in file
# These are the raw byte patterns we need to check

# Pattern 1: Find all instances of corrupted emoji that contain U+0080-U+009F chars
fixes = 0
i = 0
result = []
while i < len(content):
    ch = content[i]
    cp = ord(ch)
    
    if cp > 127:
        # Try longer sequences more aggressively
        best_fix = None
        best_len = 0
        for length in range(2, 10):
            if i + length > len(content):
                break
            candidate = content[i:i+length]
            try:
                raw = candidate.encode("cp1252")
                fixed = raw.decode("utf-8")
                if fixed != candidate and len(fixed) < len(candidate):
                    # Validate
                    ok = True
                    for fc in fixed:
                        fcp = ord(fc)
                        if fcp < 0x20 and fcp not in (0x0A, 0x0D, 0x09):
                            ok = False
                            break
                    if ok:
                        best_fix = fixed
                        best_len = length
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        
        if best_fix is not None:
            result.append(best_fix)
            fixes += 1
            i += best_len
            continue
    
    result.append(ch)
    i += 1

print(f"Fixed {fixes} sequences")
if fixes > 0:
    fixed_content = "".join(result)
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    print("File written")
else:
    # Let's debug what specific patterns exist
    # Search for characters in U+0080-U+009F range
    bad_spots = []
    for idx, ch in enumerate(content):
        if 0x80 <= ord(ch) <= 0x9F:
            start = max(0, idx-5)
            end = min(len(content), idx+5)
            ctx = content[start:end].replace('\n','↵')
            bad_spots.append(f"  pos {idx}: U+{ord(ch):04X} near: {repr(ctx)}")
    
    if bad_spots:
        print(f"Found {len(bad_spots)} instances of 0x80-0x9F chars:")
        for s in bad_spots[:30]:
            print(s)
    else:
        # Check for ð and â patterns
        for idx, ch in enumerate(content):
            if ord(ch) in (0xF0, 0xE2):
                start = max(0, idx)
                end = min(len(content), idx+20)
                ctx = content[start:end].replace('\n','↵')
                print(f"  pos {idx}: U+{ord(ch):04X} -> {repr(ctx)}")
                if idx > 100:
                    break
