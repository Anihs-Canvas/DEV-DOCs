import re

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all diagram-container divs (the full block)
diag_start_str = '<div class="diagram-container">\n            <div class="diagram-title">🏗️ Part 3 Labs'

# Find first occurrence
first = c.find(diag_start_str)
if first == -1:
    print('ERROR: diagram not found')
else:
    # Find the end of this diagram block
    end_marker = '</pre>\n        </div>'
    first_end = c.find(end_marker, first)
    first_end = c.find('</div>', first_end + len(end_marker)) + 6
    
    first_diagram = c[first:first_end]
    
    # Now find and remove ALL diagram-container blocks
    diag_pattern = re.compile(
        r'\n\s*<div class="diagram-container">.*?</div>\s*\n\s*</div>\s*',
        re.DOTALL
    )
    
    # Remove all diagram blocks first
    c = diag_pattern.sub('\n', c)
    
    # Now find where to insert the single diagram - before the first scenario-block
    s1_marker = '<div class="scenario-block" id="s1">'
    s1_pos = c.find(s1_marker)
    if s1_pos == -1:
        print('ERROR: S1 not found')
    else:
        c = c[:s1_pos] + '\n        ' + first_diagram + '\n    \n    ' + c[s1_pos:]
        print('Re-inserted single diagram before S1')

# Add diagram-container CSS if missing
diag_css = '''
        /* ═══════════════ DIAGRAM STYLES ═══════════════ */
        .diagram-container { background: var(--gradient-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 20px 24px; margin: 20px 0 24px 0; overflow-x: auto; box-shadow: var(--shadow); }
        .diagram-container .diagram-title { font-size: 16px; font-weight: 700; color: var(--accent-purple); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
        .diagram-container pre { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace; font-size: 12px; line-height: 1.4; color: var(--accent); white-space: pre; background: transparent !important; padding: 0 !important; border: none !important; margin: 0; }
'''

# Check if diagram CSS already exists
if '.diagram-container {' not in c:
    # Insert after scenario CSS block
    css_marker = '.copy-btn.copied { border-color: var(--accent-green); color: var(--accent-green); background: rgba(63,185,80,0.1); }'
    css_pos = c.find(css_marker)
    if css_pos != -1:
        css_pos += len(css_marker)
        c = c[:css_pos] + diag_css + c[css_pos:]
        print('Added diagram CSS')

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

import os
sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)

# Count remaining diagram-containers in HTML (not CSS)
html_diags = len(re.findall(r'(?<!\.)diagram-container', c))
print(f'Size: {sz} KB | HTML diagram-containers: {html_diags} | </main>: {c.count("</main>")}')
print(f'sc-step: {c.count("sc-step")} | scenario-block: {c.count("scenario-block")}')
