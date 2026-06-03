#!/usr/bin/env python3
"""Analyze MCQ section boundaries for missing subsection IDs"""
import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find positions of all cat section headers and the Q ranges within them
missing_ids = ['cat3-4','cat4-3','cat5-1','cat6-1','cat6-2','cat6-3','cat7-1','cat7-2','cat7-3','cat8-1','cat8-2']

# For each cat section, find what Q numbers it contains
for cat_num in [3,4,5,6,7,8]:
    # Find the cat section start
    cat_marker = f'id="cat{cat_num}"'
    cat_pos = content.find(cat_marker)
    if cat_pos < 0:
        print(f"Cat{cat_num}: NOT FOUND")
        continue
    
    # Find the next cat section to bound the range
    next_cat_marker = f'id="cat{cat_num+1}"'
    next_cat_pos = content.find(next_cat_marker)
    if next_cat_pos < 0:
        # Find PART 2 or next major section
        next_cat_pos = len(content)
    
    section = content[cat_pos:next_cat_pos]
    
    # Find all Q numbers in this section
    qs = re.findall(r'id="q(\d+)"', section)
    q_nums = sorted(int(q) for q in qs)
    
    if q_nums:
        print(f"Cat{cat_num}: Q{q_nums[0]}-Q{q_nums[-1]} ({len(q_nums)} questions)")
    
    # Find existing subsection IDs
    subs = re.findall(rf'id="(cat{cat_num}-\d+)"', section)
    print(f"  Existing subsections: {subs}")
    
    # Find what's missing for this cat
    needed = [s for s in missing_ids if s.startswith(f'cat{cat_num}-')]
    print(f"  Missing: {needed}")
    
    # For each missing sub, find a good insertion point
    for mid in needed:
        sub_num = int(mid.split('-')[1])
        # Show context around the expected Q range
        # Roughly: subs divide the Q range evenly
        n_questions = len(q_nums)
        if n_questions > 0:
            per_sub = n_questions // 4 if cat_num <= 4 else n_questions // 3 if cat_num <= 7 else n_questions // 2
            start_q = q_nums[0] + (sub_num - 1) * per_sub
            end_q = min(start_q + per_sub, q_nums[-1])
            print(f"  → {mid} should cover approx Q{start_q}-Q{end_q}")
            
            # Find the actual MCQ block for start_q
            q_marker = f'id="q{start_q}"'
            q_pos = section.find(q_marker)
            if q_pos > 0:
                # Show a snippet of what's just before this Q
                snippet_start = max(0, q_pos - 200)
                snippet = section[snippet_start:q_pos]
                # Show last 100 chars
                print(f"  → Context before Q{start_q}: ...{snippet[-100:]}")
    print()
