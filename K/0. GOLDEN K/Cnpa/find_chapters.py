#!/usr/bin/env python3
import re
FILE = r"c:\Users\owner\Desktop\DEV-DOCs\K\0. GOLDEN K\Cnpa\cnpa_main.html"
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Find all chapter start markers
for m in re.finditer(r'id="ch(\d+)"', content):
    ch_num = int(m.group(1))
    pos = m.start()
    ctx = content[pos:pos+200].replace('\n', ' ').replace('  ', ' ')
    print(f"ch{ch_num} at char {pos}: {ctx[:130]}...")

print()
# Find chapter end positions
for m in re.finditer(r'id="ch(\d+)"', content):
    ch_num = int(m.group(1))
    pos = m.start()
    
    # Find next chapter
    next_match = re.search(rf'id="ch{ch_num+1}"', content[pos+1:])
    if next_match:
        next_pos = pos + 1 + next_match.start()
    elif ch_num < 26:
        # Find next part marker
        pm = re.search(r'PART \d+:', content[pos+1:pos+50000])
        if pm:
            next_pos = pos + 1 + pm.start()
        else:
            next_pos = len(content)
    else:
        next_pos = len(content)
    
    chunk = content[pos:next_pos]
    last = chunk[-300:].replace('\n', ' ').replace('  ', ' ')
    print(f"Ch{ch_num} ends ~char {next_pos}. Last 200: ...{last[-200:]}")
