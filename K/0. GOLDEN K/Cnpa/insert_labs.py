#!/usr/bin/env python3
"""Insert Chapter lab sections into cnpa_main.html."""
import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Insertion points: right before the next chapter's <div id="chX"> marker
# Labs 1-4 are ready. Insert each before the next chapter.
insertions = [
    ("lab_ch1.html", r'<div id="ch2">'),
    ("lab_ch2.html", r'<div id="ch3">'),
    ("lab_ch3.html", r'<div id="ch4">'),
    ("lab_ch4.html", r'<div id="ch5">'),
]

for lab_file, anchor in insertions:
    lab_path = rf"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\{lab_file}"
    with open(lab_path, "r", encoding="utf-8") as f:
        lab_html = f.read()
    
    # Find anchor
    idx = content.find(anchor)
    if idx == -1:
        print(f"ERROR: Anchor '{anchor}' not found!")
        continue
    
    # Insert lab before the anchor, with proper spacing
    insertion = f"\n\n        {lab_html}\n\n        "
    content = content[:idx] + insertion + content[idx:]
    
    # Verify the anchor moved correctly
    ch_num = re.search(r'ch(\d+)', lab_file).group(1)
    new_idx = content.find(anchor)
    print(f"Inserted Ch{ch_num} lab at position {idx} → new anchor at {new_idx}")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nDone! File size: {len(content):,} chars")
