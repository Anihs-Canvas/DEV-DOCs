#!/usr/bin/env python3
"""Find exact insertion points for each chapter in cnpa_main.html."""
import re

FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Find all chapter divs
chapters = []
for m in re.finditer(r'<div id="ch(\d+)">', content):
    chapters.append((int(m.group(1)), m.start()))

# Sort by position
chapters.sort(key=lambda x: x[1])

for i, (ch_num, pos) in enumerate(chapters):
    # Find the end of this chapter - either next chapter or end of file
    if i + 1 < len(chapters):
        next_pos = chapters[i + 1][1]
    else:
        next_pos = len(content)
    
    chunk = content[pos:next_pos]
    
    # Find the LAST occurrence of a significant closing tag before next chapter
    # Look for patterns like: </div>\n\n<div id="ch or </div>\n\n        <div id="ch
    # The insertion point should be right before the opening of the next chapter
    
    # Find the anchor - look backwards from next_pos to find the gap between chapters
    # Usually it's: </div>\n        </div>\n<div id="chN+1">
    
    # Search for the pattern right before next_pos
    gap_start = max(0, next_pos - 500)
    gap = content[gap_start:next_pos]
    
    # Find the last occurrence of something like </div> or </section> before ch marker
    last_div = gap.rfind('</div>')
    last_close = gap.rfind('</div>\n')
    
    # Print some context
    ctx = gap[-200:].replace('\n', '\\n')
    print(f"Ch{ch_num} (pos {pos}) -> Ch{chapters[i+1][0] if i+1 < len(chapters) else 'END'} (pos {next_pos})")
    print(f"  Last 200 chars of gap: ...{ctx[-150:]}")
    print()
