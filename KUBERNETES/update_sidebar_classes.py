"""Add category color classes to sidebar chapter links and numbers."""

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Add cat-N class to chapter numbers: <span class="chapter-number">N</span>
#    → <span class="chapter-number cat-N">N</span>
for n in range(1, 9):
    old = f'<span class="chapter-number">{n}</span>'
    new = f'<span class="chapter-number cat-{n}">{n}</span>'
    content = content.replace(old, new)

# 2. Add cat-N class to chapter links in Part 1: href="#catN"
for n in range(1, 9):
    old = f'<a href="#cat{n}" class="chapter-link">'
    new = f'<a href="#cat{n}" class="chapter-link cat-{n}">'
    content = content.replace(old, new)

# 3. Add cat-N class to chapter links in Part 2: href="#ts-catN"
for n in range(1, 9):
    old = f'<a href="#ts-cat{n}" class="chapter-link">'
    new = f'<a href="#ts-cat{n}" class="chapter-link cat-{n}">'
    content = content.replace(old, new)

# 4. Add cat-N class to chapter links in Part 3: href="#sc-catN"
for n in range(1, 9):
    old = f'<a href="#sc-cat{n}" class="chapter-link">'
    new = f'<a href="#sc-cat{n}" class="chapter-link cat-{n}">'
    content = content.replace(old, new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# Count changes
import subprocess
# Quick sanity checks
checks = [
    '<span class="chapter-number cat-1">',
    '<a href="#cat1" class="chapter-link cat-1">',
    '<a href="#ts-cat3" class="chapter-link cat-3">',
    '<a href="#sc-cat8" class="chapter-link cat-8">',
]
for c in checks:
    count = content.count(c)
    print(f'  {c[:60]}... → {count} occurrences')

print(f'\n✅ Sidebar category classes applied!')
print(f'   File: {len(content):,} bytes')
