#!/usr/bin/env python3
"""Fix TS section header ID mismatches:
1. Update sidebar hrefs for IDs that have matching content (6 changes)
2. Add hidden anchor spans for IDs missing from content (8 additions)
"""
import re

PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# =============================================================================
# Part 1: Update sidebar hrefs (6 changes)
# Map: old sidebar ID → actual content ID
# =============================================================================
sidebar_fixes = {
    'ts-sm2': 'ts-sm5',
    'ts-sm3': 'ts-sm9',
    'ts-sm4': 'ts-sm13',
    'ts-o1':  'ts-ob1',
    'ts-o2':  'ts-ob6',
    'ts-ic1': 'ts-in1',
    'ts-ic2': 'ts-in6',
    'ts-cm2': 'ts-cm6',
    'ts-eb2': 'ts-eb6',
}

count_sidebar = 0
for old_id, new_id in sidebar_fixes.items():
    # Only update in sidebar (href="#old_id")
    old_href = f'href="#{old_id}"'
    new_href = f'href="#{new_id}"'
    if old_href in content:
        content = content.replace(old_href, new_href)
        count_sidebar += 1
        print(f"  Updated sidebar: {old_href} → {new_href}")
    else:
        print(f"  NOT FOUND in sidebar: {old_href}")

print(f"Sidebar updates: {count_sidebar}")

# =============================================================================
# Part 2: Add hidden anchor spans for IDs missing from content (8 additions)
# These go near the appropriate TS issues
# =============================================================================
# Mapping: missing_id → find this existing ts-issue ID and insert before it
missing_anchors = {
    # Cat4 (OB1-OB10): ts-o3 near OB8, ts-o4 near OB10
    'ts-o3':  'ts-ob8-detail',
    'ts-o4':  'ts-ob10-detail',
    # Cat5 (IN1-IN10): ts-ic3 near IN8, ts-ic4 near IN10
    'ts-ic3': 'ts-in8-detail',
    'ts-ic4': 'ts-in10-detail',
    # Cat6 (CM1-CM10): ts-cm3 near CM8, ts-cm4 near CM10
    'ts-cm3': 'ts-cm8-detail',
    'ts-cm4': 'ts-cm10-detail',
    # Cat7 (EB1-EB10): ts-eb3 near EB8, ts-eb4 near EB10
    'ts-eb3': 'ts-eb8-detail',
    'ts-eb4': 'ts-eb10-detail',
    # Cat8 (BG1-BG6): ts-bg2 near BG3, ts-bg3 near BG5
    'ts-bg2': 'ts-bg3-detail',
    'ts-bg3': 'ts-bg5-detail',
}

count_anchors = 0
for missing_id, near_issue in missing_anchors.items():
    marker = f'id="ts-{near_issue}"'
    if marker in content:
        anchor_html = f'<span id="{missing_id}"></span>\n    <div class="ts-issue" id="ts-{near_issue}"'
        old_html = f'<div class="ts-issue" id="ts-{near_issue}"'
        # Only replace first occurrence
        content = content.replace(old_html, anchor_html, 1)
        count_anchors += 1
        print(f"  Added anchor: {missing_id} before {near_issue}")
    else:
        print(f"  NOT FOUND: marker for {near_issue}")

print(f"Anchors added: {count_anchors}")

# Also need to handle ts-o3, ts-o4, ts-ic3, ts-ic4 — these are sidebar IDs that need
# section-header style divs? No, the sidebar just needs the href to work.
# The hidden spans are sufficient.

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nDone! {count_sidebar} sidebar updates + {count_anchors} anchors added.")
