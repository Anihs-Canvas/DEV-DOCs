#!/usr/bin/env python3
"""Convert decision tree tables to card-based flow design (v2 - per-ID approach)"""
import re

PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

count = 0
for dt_num in range(1, 16):
    dt_id = f'id="dt{dt_num}"'
    dt_start = content.find(dt_id)
    if dt_start < 0:
        print(f"  DT{dt_num}: NOT FOUND")
        continue
    
    # Find the start of this ts-issue div
    div_start = content.rfind('<div class="ts-issue"', 0, dt_start)
    if div_start < 0:
        print(f"  DT{dt_num}: div start not found")
        continue
    
    # Find the table start and end within this div
    table_start = content.find('<table', div_start)
    table_end = content.find('</table>', table_start)
    if table_start < 0 or table_end < 0:
        print(f"  DT{dt_num}: no table found")
        continue
    
    table_html = content[table_start:table_end + 8]
    
    # Parse rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    data_rows = [r for r in rows if '<th' not in r]
    
    if not data_rows:
        print(f"  DT{dt_num}: no data rows")
        continue
    
    # Build card-based HTML
    cards = '<div class="dt-container">\n'
    for row_html in data_rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(cells) < 4:
            continue
        
        step_num = cells[0].strip()
        check = cells[1].strip()
        yes = cells[2].strip()
        no = cells[3].strip()
        
        cards += f'''            <div class="dt-step">
                <div class="dt-step-num">{step_num}</div>
                <div class="dt-step-body">
                    <div class="dt-check">{check}</div>
                    <div class="dt-branches">
                        <div class="dt-yes"><span class="dt-icon">✅</span> <span>{yes}</span></div>
                        <div class="dt-no"><span class="dt-icon">❌</span> <span>{no}</span></div>
                    </div>
                </div>
            </div>
'''
    cards += '        </div>'
    
    # Replace the table with cards
    content = content[:table_start] + cards + content[table_end + 8:]
    count += 1
    print(f"  DT{dt_num}: ✅ converted ({len(data_rows)} steps)")

# Add tree title icon to each dt
# Find ts-issue headers in decision trees and add the tree-icon
for dt_num in range(1, 16):
    pass  # Tree icons are already in the ts-category label

print(f"\n✅ Converted {count}/15 decision trees to card flow design")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 Done!")
