#!/usr/bin/env python3
"""Extract patterns from CKAD.html for comparison"""
import re

html = open("CKAD.html", "r", encoding="utf-8").read()

# Find Q&A pattern
q_idx = html.find('class="question"')
if q_idx > 0:
    chunk = html[q_idx:q_idx+2500]
    print("=== QUESTION/ANSWER PATTERN ===")
    print(chunk[:2000])
else:
    # Try finding exam questions
    q_idx = html.find("Practice Questions")
    if q_idx > 0:
        chunk = html[q_idx:q_idx+2000]
        print("=== PRACTICE QUESTIONS SECTION ===")
        print(chunk[:1500])

# Find info-box usage
print("\n\n=== INFO-BOX USAGE ===")
for m in re.finditer(r'<div class="info-box[^"]*">(.+?)</div>', html, re.DOTALL):
    print(m.group(1).strip()[:400])
    print("---")
    break

# Find split-panel usage
print("\n\n=== SPLIT-PANEL USAGE ===")
for m in re.finditer(r'<div class="split-panel[^"]*">(.+?)</div>\s*</div>', html, re.DOTALL):
    print(m.group(0).strip()[:500])
    print("---")
    break

# Check how pre tags are used for code
print("\n\n=== PRE TAG USAGE (first 3) ===")
count = 0
for m in re.finditer(r'<pre[^>]*>(.{50,200}?)</pre>', html, re.DOTALL):
    if count < 2:
        print(m.group(0)[:300])
        print("---")
    count += 1

