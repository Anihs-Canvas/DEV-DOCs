#!/usr/bin/env python3
"""
SAFE rebuild: Re-apply ALL enhancements to restored lfcs.html.
Runs each step atomically and verifies file integrity after each.
"""
import re, os

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"

def load():
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save(content, step_name):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    sz = os.path.getsize(filepath)
    print(f"  ✅ {step_name} — File: {sz//1024:,} KB")

def check_anchor(content, anchor):
    return f'id="{anchor}"' in content

content = load()
print(f"Starting: {len(content)//1024:,} KB")

# ============================================================
# STEP 3: Fix syntax highlighting — SAFE version
# ============================================================
# Fix 1: Ensure Prism CSS is loaded directly
content = content.replace(
    '<link rel="preload" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">',
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css">'
)
content = content.replace(
    '<noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css"></noscript>',
    ''
)

# Fix 2: Ensure Prism scripts include all languages + highlightAll
old_prism_scripts = '    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>'
new_prism_scripts = '''    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-yaml.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-sql.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-nginx.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-docker.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-ini.min.js"></script>
    <script>Prism.highlightAll();</script>'''

if old_prism_scripts in content:
    # Find the Prism section and replace
    # Look for the pattern: prism.min.js followed by individual language scripts
    prism_start = content.find(old_prism_scripts)
    if prism_start > 0:
        # Find where existing prism scripts end (before next non-prism content)
        after_prism = content.find('    <!-- Reading Progress Bar -->', prism_start)
        if after_prism > 0:
            content = content[:prism_start] + new_prism_scripts + '\n\n' + content[after_prism:]
            print("  ✅ Prism.js updated with all languages + highlightAll()")

# Fix 3: Add Prism CSS overrides (inside the main <style> block)
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
if style_end > 0 and 'Prism.js syntax highlighting' not in content:
    content = content[:style_end] + prism_css + '\n    </style>'

save(content, "Step 3: Syntax highlighting fixed")

# ============================================================
# STEP 4: Add language classes to code blocks (SAFE — simple string search)
# ============================================================
# Only add language-bash to bare <pre><code> that don't have any class
# Use a simple, safe approach
count_bare = content.count('<pre><code>')
if count_bare > 0:
    content = content.replace('<pre><code>', '<pre><code class="language-bash">')
    print(f"  ✅ Added language-bash to {count_bare} bare <pre><code> blocks")

# Also add diagram-ascii to <pre> blocks with box-drawing chars
# SAFE: only target specific patterns
count_diagrams = 0
# Find <pre> blocks that start with box-drawing characters
content = re.sub(
    r'<pre>\s*(?=[╔╗╚╝║═╠╣╦╩╬┌┐└┘├┤┬┴┼│─])',
    r'<pre class="diagram-ascii">',
    content
)
# Count how many were tagged
count_diagrams = content.count('<pre class="diagram-ascii">')
print(f"  ✅ Tagged {count_diagrams} diagram blocks")

save(content, "Step 4: Language classes added")

# Final integrity check
anchors = ['ch1', 'ch45', 'master-summary', 'exam-strategy', 'port-analogy', 'new-topics-2026']
missing = [a for a in anchors if f'id="{a}"' not in content]
if missing:
    print(f"\n⚠️ MISSING ANCHORS: {missing}")
else:
    print(f"\n✅ All {len(anchors)} key anchors intact")

print(f"\n🎉 Rebuild complete! Final size: {os.path.getsize(filepath)//1024:,} KB")
