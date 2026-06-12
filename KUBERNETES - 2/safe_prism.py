#!/usr/bin/env python3
"""SAFE Prism.js fix — no risky string slicing."""
import os

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Starting: {len(content)//1024:,} KB")

# Fix 1: Direct CSS load (not preload)
old_preload = '<link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">'
if old_preload in content:
    content = content.replace(old_preload, '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css">')
    print("✅ Fixed Prism CSS: preload → direct link")

# Remove noscript fallback
noscript = '<noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css"></noscript>'
if noscript in content:
    content = content.replace(noscript, '')
    print("✅ Removed noscript fallback")

# Fix 2: Replace EXISTING Prism script section exactly
# Find the block from "<!-- Prism.js" to the next "<!--" comment
prism_comment = '    <!-- Prism.js for syntax highlighting -->'
if prism_comment in content:
    idx = content.find(prism_comment)
    # Find the next comment or script boundary after the Prism scripts
    next_section = content.find('    <!-- Reading Progress Bar -->', idx)
    if next_section < 0:
        next_section = content.find('    <div id="readingProgress"', idx)
    if next_section < 0:
        # Fallback: find the closing script tag after prism
        end_search = content.find('prism-docker.min.js"></script>', idx)
        if end_search > 0:
            next_section = end_search + len('prism-docker.min.js"></script>') + 1
    
    if next_section > idx:
        new_scripts = '''    <!-- Prism.js for syntax highlighting -->
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-sql.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-nginx.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-docker.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-ini.min.js"></script>
    <script>Prism.highlightAll();</script>

'''
        content = content[:idx] + new_scripts + content[next_section:]
        print("✅ Prism.js updated: 8 languages + highlightAll()")
    else:
        print("⚠️ Could not find Prism section end — skipping")
else:
    print("⚠️ Prism comment not found")

# Fix 3: Add Prism CSS overrides (only if not present)
if 'Prism.js syntax highlighting' not in content:
    prism_css = '''
        /* Prism.js syntax highlighting */
        pre[class*="language-"] code[class*="language-"],
        pre code[class*="language-"] { color: inherit !important; background: transparent !important; }
        pre.diagram-ascii, pre.diagram-ascii code { color: #c9d1d9 !important; }
        .token.comment,.token.prolog,.token.doctype,.token.cdata { color: #8b949e; }
        .token.punctuation { color: #c9d1d9; }
        .token.property,.token.tag,.token.boolean,.token.number,.token.constant,.token.symbol,.token.deleted { color: #79c0ff; }
        .token.selector,.token.attr-name,.token.string,.token.char,.token.builtin,.token.inserted { color: #a5d6ff; }
        .token.operator,.token.entity,.token.url { color: #d2a8ff; }
        .token.atrule,.token.attr-value,.token.keyword { color: #ff7b72; }
        .token.function,.token.class-name { color: #d2a8ff; }
        .token.regex,.token.important,.token.variable { color: #ffa657; }
'''
    style_end = content.find('    </style>')
    if style_end > 0:
        content = content[:style_end] + prism_css + '\n    </style>'
        print("✅ Added Prism CSS token overrides")

# Fix 4: Add language-bash to bare <pre><code> blocks (only if they lack any class)
count = content.count('<pre><code>')
if count > 0:
    content = content.replace('<pre><code>', '<pre><code class="language-bash">')
    print(f"✅ Added language-bash to {count} bare <pre><code> blocks")

# Fix 5: Tag diagram blocks (safe — only matches specific patterns)
import re
tagged = 0
def tag_diagram(m):
    global tagged
    tagged += 1
    return '<pre class="diagram-ascii">'
content = re.sub(r'<pre>\s*(?=[╔╗╚╝║═╠╣╦╩╬])', tag_diagram, content)
print(f"✅ Tagged {tagged} diagram blocks")

# Verify
sz = os.path.getsize(filepath) if False else 0  # will get after write
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
sz = os.path.getsize(filepath)

# Integrity check
anchors = ['ch1', 'ch45', 'master-summary', 'exam-strategy', 'port-analogy', 'new-topics-2026']
missing = [a for a in anchors if f'id="{a}"' not in content]
if missing:
    print(f"\n⚠️ MISSING: {missing}")
else:
    print(f"\n✅ All {len(anchors)} key anchors intact")

questions = content.count('exam-question-item')
print(f"📊 Questions: {questions} | Diagrams: {content.count('diagram-container')} | Size: {sz//1024:,} KB")
print("Done!")
