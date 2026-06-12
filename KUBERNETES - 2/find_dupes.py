#!/usr/bin/env python3
"""Find duplicate explanations - FIXED."""
import re
from collections import Counter

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<div class="eq-exp-label">.*?Explanation</div>\s*<p>(.*?)</p>'
explanations = re.findall(pattern, content, re.DOTALL)
print(f'Total explanations found: {len(explanations)}')

cleaned = [e.strip() for e in explanations]
counts = Counter(cleaned)
dupes = {k: v for k, v in counts.items() if v > 1}
print(f'Duplicate explanation groups: {len(dupes)}')
print(f'Total duplicate instances: {sum(v for v in dupes.values())}')

if dupes:
    print('\n--- THE DUPLICATE TEXT ---')
    for text, count in sorted(dupes.items(), key=lambda x: -x[1])[:5]:
        print(f'\n[{count}x occurrences]:')
        print(text[:300])
        print('...')
else:
    print('No duplicates!')

unique = [k for k, v in counts.items() if v == 1]
print(f'\nUnique explanations: {len(unique)}')
