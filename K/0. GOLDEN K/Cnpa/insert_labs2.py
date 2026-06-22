#!/usr/bin/env python3
"""Insert Chapter 5-8 lab sections into cnpa_main.html."""
import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

insertions = [
    ("lab_ch5.html", r'<div id="ch6">'),
    ("lab_ch6.html", r'<div id="ch7">'),
    ("lab_ch7.html", r'<div id="ch8">'),
    ("lab_ch8.html", r'<div id="ch9">'),
]

for lab_file, anchor in insertions:
    lab_path = rf"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\{lab_file}"
    with open(lab_path, "r", encoding="utf-8") as f:
        lab_html = f.read()
    
    idx = content.find(anchor)
    if idx == -1:
        print(f"ERROR: Anchor '{anchor}' not found!")
        continue
    
    insertion = f"\n\n        {lab_html}\n\n        "
    content = content[:idx] + insertion + content[idx:]
    
    ch_num = re.search(r'ch(\d+)', lab_file).group(1)
    print(f"Inserted Ch{ch_num} lab at position {idx}")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Done! File size: {len(content):,} chars")
