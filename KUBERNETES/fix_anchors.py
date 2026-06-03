#!/usr/bin/env python3
"""Add missing TS anchor IDs - fixed version"""
import re

PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Mapping: missing_id → nearest existing ts-issue detail ID
missing_anchors = {
    'ts-o3':  'ob8-detail',
    'ts-o4':  'ob10-detail',
    'ts-ic3': 'in8-detail',
    'ts-ic4': 'in10-detail',
    'ts-cm3': 'cm8-detail',
    'ts-cm4': 'cm10-detail',
    'ts-eb3': 'eb8-detail',
    'ts-eb4': 'eb10-detail',
    'ts-bg2': 'bg3-detail',
    'ts-bg3': 'bg5-detail',
}

count = 0
for missing_id, near_issue in missing_anchors.items():
    # Simple marker: just find the id attribute
    marker = f'id="ts-{near_issue}"'
    if marker in content:
        anchor = f'<span id="{missing_id}"></span>'
        # Insert anchor BEFORE the ts-issue div that contains this id
        # Find the div start
        search_start = content.find(marker)
        if search_start > 0:
            # Find the start of this div (go backwards to '<div class="ts-issue"')
            div_start = content.rfind('<div class="ts-issue"', 0, search_start)
            if div_start > 0:
                content = content[:div_start] + anchor + content[div_start:]
                count += 1
                print(f"  Added: {missing_id} before {near_issue}")
            else:
                print(f"  Could not find div start for {near_issue}")
        else:
            print(f"  Could not locate {marker}")
    else:
        print(f"  NOT FOUND: {marker}")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nAnchors added: {count}/10")
