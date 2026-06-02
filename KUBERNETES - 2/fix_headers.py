import re

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix all broken sc-header structures.
# Broken: <div class="sc-badge">XX</div>\n\n        </div>\n    \n            <div class="sc-header-content">
# Fixed:  <div class="sc-badge">XX</div>\n            <div class="sc-header-content">

pattern = re.compile(
    r'(<div class="sc-badge">S\d+</div>)\s*\n\s*</div>\s*\n\s*(<div class="sc-header-content">)'
)
count = len(pattern.findall(c))
c = pattern.sub(r'\1\n            \2', c)

# Also fix the diagram-container that may have been duplicated
# Check for consecutive diagram-containers
dc = c.count('diagram-container')
print(f'diagram-container count: {dc}')

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Fixed {count} broken sc-header structures. Size: {sz} KB')

# Verify by reading S1
idx = c.find('<div class="scenario-block" id="s1">')
chunk = c[idx:idx+800]
if 'sc-badge">S1</div>\n            <div class="sc-header-content">' in chunk:
    print('S1 structure: GOOD')
else:
    print('S1 structure: NEEDS CHECK')
    # Print the relevant section
    hdr = chunk[:400]
    for i, line in enumerate(hdr.split('\n')):
        print(f'  {i}: {line}')
