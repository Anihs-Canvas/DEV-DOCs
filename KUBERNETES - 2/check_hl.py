#!/usr/bin/env python3
"""Quick check of syntax highlighting state"""
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html', 'r', encoding='utf-8') as f:
    c = f.read()

blocks = re.findall(r'<pre[^>]*><code[^>]*>.*?</code></pre>', c, re.DOTALL)
print(f'Total <pre><code> blocks: {len(blocks)}')

with_lang = 0
without_lang = 0
for b in blocks[:10]:
    code_tag = re.search(r'<code([^>]*)>', b)
    cls = code_tag.group(1) if code_tag else ''
    has_lang = 'language-' in cls
    if has_lang:
        with_lang += 1
        lang = re.search(r'language-(\w+)', cls).group(1)
        preview = b[80:150].replace('\n',' ').strip()[:60]
        print(f'  [{lang:8s}] {preview}...')
    else:
        without_lang += 1
        preview = b[50:120].replace('\n',' ').strip()[:60]
        print(f'  [NO LANG ] {preview}...')

# Count all
all_blocks = re.findall(r'<pre[^>]*>', c)
all_with_lang = len([b for b in all_blocks if 'language-' in b])
print(f'\nTotal <pre> blocks: {len(all_blocks)}')
print(f'With language class: {all_with_lang}')
print(f'Without language: {len(all_blocks) - all_with_lang}')

# Check Prism scripts
scripts = re.findall(r'prism[a-z0-9.-]*\.min\.js', c)
print(f'\nPrism.js scripts: {len(scripts)}')
for s in scripts:
    print(f'  {s}')
