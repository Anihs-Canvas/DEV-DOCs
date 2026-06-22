#!/usr/bin/env python3
"""More aggressive emoji fixer - handles all cp1252 double-encoded sequences."""
import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

fixes = 0

def try_fix_sequence(text):
    """Try to reverse cp1252→UTF-8 double encoding. Returns (fixed, True) or (original, False)."""
    try:
        raw = text.encode("cp1252")
        fixed = raw.decode("utf-8")
        if fixed == text:
            return text, False
        # Must be shorter (emoji = fewer chars than corrupted form)
        if len(fixed) >= len(text):
            return text, False
        # Sanity: no null bytes, no C0/C1 control chars (except \n\r\t)
        for ch in fixed:
            cp = ord(ch)
            if cp < 0x20 and cp not in (0x0A, 0x0D, 0x09):
                return text, False
            if 0x7F <= cp <= 0x9F:
                return text, False
        return fixed, True
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text, False

# Build list of all distinct corrupted sequences to fix
# Find all runs of non-ASCII chars that could be cp1252-re-encoded emoji
results = []
i = 0
while i < len(content):
    ch = content[i]
    cp = ord(ch)
    
    if cp > 127:
        # Try sequences of length 2-8 starting here
        best_fix = None
        best_len = 0
        for length in range(2, 9):
            if i + length > len(content):
                break
            candidate = content[i:i+length]
            fixed, ok = try_fix_sequence(candidate)
            if ok:
                best_fix = fixed
                best_len = length
        
        if best_fix is not None:
            results.append(best_fix)
            fixes += 1
            i += best_len
            continue
    
    results.append(ch)
    i += 1

if fixes > 0:
    fixed_content = "".join(results)
    # Verify it's valid HTML
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    print(f"Fixed {fixes} more corrupted sequences")
else:
    print("No additional fixes found")

# Report total fixes
print("Done - check cnpa_main.html")
