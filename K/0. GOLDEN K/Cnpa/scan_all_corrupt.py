#!/usr/bin/env python3
"""Comprehensive scan and fix of all remaining corruption patterns."""
import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Find all patterns containing control chars and their context
# Group similar patterns to identify corruption types
patterns = {}

i = 0
while i < len(content):
    cp = ord(content[i])
    if 0x80 <= cp <= 0x9F:
        # Extract a window around this char
        start = max(0, i - 3)
        end = min(len(content), i + 6)
        seq = content[start:end]
        # Find just the corrupted run
        run_start = i
        while run_start > 0 and ord(content[run_start-1]) > 127:
            run_start -= 1
        run_end = i + 1
        while run_end < len(content) and ord(content[run_end]) > 127:
            run_end += 1
        corrupt_run = content[run_start:run_end]
        
        if corrupt_run not in patterns:
            patterns[corrupt_run] = {"count": 0, "contexts": []}
        patterns[corrupt_run]["count"] += 1
        if len(patterns[corrupt_run]["contexts"]) < 3:
            patterns[corrupt_run]["contexts"].append(seq)
        
        i = run_end  # skip past the run
    else:
        i += 1

print(f"Found {len(patterns)} unique corruption patterns:\n")
for seq, info in sorted(patterns.items(), key=lambda x: -x[1]["count"]):
    try:
        raw = seq.encode("cp1252")
        fixed = raw.decode("utf-8", errors="replace")
    except:
        fixed = "<encoding error>"
    print(f"  Count: {info['count']:4d} | {repr(seq)[:60]} -> {repr(fixed)[:40]}")
    for ctx in info["contexts"][:2]:
        print(f"           ctx: {repr(ctx)[:100]}")
    print()
