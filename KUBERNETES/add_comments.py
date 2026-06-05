#!/usr/bin/env python
"""Add remaining step comments"""
import os, re
os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')

with open('cka_test_prep.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Add STEP 5: Verify and CLEANUP comments for S2-S10
for s in range(2, 11):
    sid = f'sc-s{s}'
    
    # Find the scenario start
    idx = h.find(f'id="{sid}"')
    if idx == -1:
        continue
    
    # Find STEP 5: Verify - first answer step after this scenario
    pattern_v = r'(            <div class="sc-step">\n                <div class="sc-step-num answer">\xe2\x9c\x93</div>)'
    for m in re.finditer(pattern_v, h):
        if m.start() > idx:
            before = h[max(0, m.start()-200):m.start()]
            if 'STEP 5' not in before and 'STEP' not in before[-50:]:
                h = h[:m.start()] + '            <!-- STEP 5: Verify -->\n' + h[m.start():]
            break
    
    # Find CLEANUP comment
    pattern_c = r'(            <div class="sc-step">\n                <div class="sc-step-num" style="background:linear-gradient\(135deg,#6e7681,#8b949e\);">\xf0\x9f\xa7\xb9</div>)'
    for m in re.finditer(pattern_c, h):
        if m.start() > idx:
            before = h[max(0, m.start()-200):m.start()]
            if 'CLEANUP' not in before:
                h = h[:m.start()] + '            <!-- CLEANUP -->\n' + h[m.start():]
            break

with open('cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(h)

print('Step comments added.')
