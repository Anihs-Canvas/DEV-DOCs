with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix ALL Step 2 headers not wrapped in sc-step divs
# Pattern: \n        <h4>🔍 Step 2: Debug & Troubleshoot</h4>
# But only when NOT preceded by sc-step-content>
import re

# Find all Step 2 headers
pattern = r'\n        <h4>🔍 Step 2: Debug & Troubleshoot</h4>'
matches = list(re.finditer(pattern, c))
print(f'Found {len(matches)} Step 2 headers')

# For each match, check if it's already inside sc-step-content
fixed = 0
for m in reversed(matches):  # Reverse to not mess up offsets
    pos = m.start()
    # Look back 200 chars to see if we're inside sc-step-content
    before = c[max(0, pos-200):pos]
    if 'sc-step-content">' in before.split('\n')[-5:]:  # Check recent context
        continue  # Already wrapped
    
    # This one needs wrapping. Replace:
    # \n        <h4>🔍 Step 2: Debug & Troubleshoot</h4>\n        <div class="ts-lookat">
    old = '\n        <h4>🔍 Step 2: Debug & Troubleshoot</h4>\n        <div class="ts-lookat">'
    new = '\n        <div class="sc-step">\n            <div class="sc-step-num debug">2</div>\n            <div class="sc-step-content">\n                <h4 class="debug">🔍 Debug & Troubleshoot</h4>\n                <div class="ts-lookat"><p style="margin-top:0">'
    
    # Check if old pattern matches at this position
    if c[pos:pos+len(old)] == old:
        c = c[:pos] + new + c[pos+len(old):]
        fixed += 1

print(f'Fixed {fixed} Step 2 headers')

# Also fix the closing of those fixed sections:
# After ts-lookat content ends with </div>, we need to close sc-step-content and sc-step
# Pattern: </p></div>\n            </div>\n        </div>
# (This is the end of ts-lookat, close of old sc-step-content, close of old sc-step)
# Then the resolution sc-step follows.
# Actually this should already be OK because the fix_sc_structure.py already added those closings.

# Fix S1 specifically - its Step 2 is at line 5335
# Let me check the exact context around it
idx_s1_s2 = c.find('id="s1"')
if idx_s1_s2 != -1:
    s1_chunk = c[idx_s1_s2:idx_s1_s2+3000]
    s2_h4 = s1_chunk.find('<h4>🔍 Step 2: Debug & Troubleshoot</h4>')
    if s2_h4 != -1:
        print(f'S1 Step 2 found at offset {s2_h4} within S1 block')
        # Show context
        ctx = s1_chunk[s2_h4-50:s2_h4+50]
        print(f'Context: ...{ctx}...')

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
print(f'Size: {round(os.path.getsize("cilium-test-prep.html")/1024,1)} KB')
