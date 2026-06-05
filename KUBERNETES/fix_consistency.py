#!/usr/bin/env python
"""Safe, targeted consistency fixes for S2-S10"""
import os, re
os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')

with open('cka_test_prep.html', 'r', encoding='utf-8') as f:
    html = f.read()

counts = {}

# ─── Fix 1: code-header single line → multi-line ───
olds = re.findall(r'(<div class="code-header"><span class="code-lang">.*?</span><button class="copy-btn" onclick=".*?">📋 Copy</button></div>)', html)
counts['code-header'] = len(olds)
for old in olds:
    m = re.match(r'<div class="code-header"><span class="code-lang">(.*?)</span><button class="copy-btn" onclick="(.*?)">📋 Copy</button></div>', old)
    if m:
        lang, onclick = m.group(1), m.group(2)
        new = f'<div class="code-header">\n                            <span class="code-lang">{lang}</span>\n                            <button class="copy-btn" onclick="{onclick}">📋 Copy</button>\n                        </div>'
        html = html.replace(old, new, 1)

# ─── Fix 2: Add SHOW ANSWER comments ───
for s in range(2, 11):
    old = f'            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer(\'sc-sa{s}\')"'
    new = f'            <!-- SHOW ANSWER -->\n{old}'
    html = html.replace(old, new)
counts['show-answer-comments'] = 9

# ─── Fix 3: YAML formatting ───
html = html.replace('capacity: {storage:', 'capacity:\n    storage:')
html = html.replace('accessModes: [ReadWriteOnce]', 'accessModes:\n  - ReadWriteOnce')
html = html.replace('resources: {requests: {storage:', 'resources:\n    requests:\n      storage:')
html = html.replace('selector: {matchLabels: {', 'selector:\n    matchLabels:\n      ')

# Fix trailing braces
for sz in ['1Gi', '5Gi', '10Gi', '20Gi', '2Gi']:
    html = html.replace(f'storage: {sz}}}', f'storage: {sz}')
html = html.replace("hostPath: {path:", "hostPath:\n    path:")
html = re.sub(r'hostPath:\n    path: ([^}]+)\}', r'hostPath:\n    path: \1', html)

counts['yaml-fixes'] = 'multiple'

with open('cka_test_prep.html', 'w', encoding='utf-8') as f:
    f.write(html)

for k, v in counts.items():
    print(f'  {k}: {v}')
print('Applied.')
