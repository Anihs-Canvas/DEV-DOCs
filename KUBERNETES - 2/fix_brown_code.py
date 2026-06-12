#!/usr/bin/env python3
"""Fix syntax highlighting: remove inline colors that override Prism.js"""
import re

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Loaded: {len(content):,} chars")

# Count pre blocks with inline color styles
inline_color_pre = len(re.findall(r'<pre[^>]*style="[^"]*color:', content))
print(f"<pre> with inline color: {inline_color_pre}")

# Strategy 1: Remove "color:#XXXXXX;" from <pre> style attributes
# This lets Prism CSS take over
def strip_inline_color(match):
    full = match.group(0)
    # Remove color: #XXXXXX; from style attr
    cleaned = re.sub(r'color:\s*#[0-9a-fA-F]{3,6};?\s*', '', full)
    # Also remove color: name;
    cleaned = re.sub(r'color:\s*[a-z]+;?\s*', '', cleaned)
    # Clean up empty style attributes
    cleaned = re.sub(r'style="\s*"', '', cleaned)
    cleaned = re.sub(r'style=""', '', cleaned)
    return cleaned

# Apply to all <pre> tags
count_fixed = 0
pre_pattern = re.compile(r'<pre\b[^>]*>')
def fix_pre_tag(m):
    global count_fixed
    tag = m.group(0)
    if 'color:' in tag and 'style=' in tag:
        count_fixed += 1
        return strip_inline_color(m)
    return tag

content = pre_pattern.sub(fix_pre_tag, content)
print(f"Stripped inline colors from {count_fixed} <pre> tags")

# Also fix <code> tags with inline color
code_pattern = re.compile(r'<code\b[^>]*>')
code_fixed = 0
def fix_code_tag(m):
    global code_fixed
    tag = m.group(0)
    if 'color:' in tag and 'style=' in tag:
        code_fixed += 1
        return strip_inline_color(m)
    return tag

content = code_pattern.sub(fix_code_tag, content)
print(f"Stripped inline colors from {code_fixed} <code> tags")

# Add CSS to ensure Prism styling takes priority
prism_css_fix = '''
        /* Ensure Prism.js syntax highlighting displays correctly */
        pre[class*="language-"] code[class*="language-"],
        pre code[class*="language-"] {
            color: inherit !important;
            background: transparent !important;
        }
        pre.diagram-ascii,
        pre.diagram-ascii code {
            color: #c9d1d9 !important;
            background: transparent !important;
        }
        /* Prism token overrides for dark theme */
        .token.comment,
        .token.prolog,
        .token.doctype,
        .token.cdata { color: #8b949e; }
        .token.punctuation { color: #c9d1d9; }
        .token.property,
        .token.tag,
        .token.boolean,
        .token.number,
        .token.constant,
        .token.symbol,
        .token.deleted { color: #79c0ff; }
        .token.selector,
        .token.attr-name,
        .token.string,
        .token.char,
        .token.builtin,
        .token.inserted { color: #a5d6ff; }
        .token.operator,
        .token.entity,
        .token.url { color: #d2a8ff; }
        .token.atrule,
        .token.attr-value,
        .token.keyword { color: #ff7b72; }
        .token.function,
        .token.class-name { color: #d2a8ff; }
        .token.regex,
        .token.important,
        .token.variable { color: #ffa657; }
'''

# Insert before closing </style> — find the end of the main style block
style_end = content.find('    </style>')
if style_end > 0 and 'Prism.js syntax highlighting displays correctly' not in content:
    content = content[:style_end] + prism_css_fix + '\n    </style>'
    print("✅ Added Prism CSS override rules")

# Verify Prism scripts are present
if 'Prism.highlightAll()' not in content:
    print("⚠️ WARNING: Prism.highlightAll() still missing!")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone!")
