#!/usr/bin/env python3
"""Add syntax highlighting language classes to ALL code blocks in lfcs.html."""
import re

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File loaded: {len(content):,} chars")

# First, let's count the current state
total_pre = content.count('<pre>') + content.count('<pre ')
total_pre_code = content.count('<pre><code>') + content.count('<pre><code ')
total_with_lang = len(re.findall(r'<pre[^>]*language-', content))

print(f"Total <pre> blocks: ~{total_pre}")
print(f"<pre><code> blocks: {total_pre_code}")
print(f"Already have language class: {total_with_lang}")

# Strategy: Add language-bash to all <pre><code> blocks that don't already have a language class
# Add Prism.js plugins for better highlighting

# 1. Add additional Prism.js language components before </body>
prism_langs = '''
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-nginx.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-sql.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-ini.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-diff.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1/plugins/line-numbers/prism-line-numbers.min.js"></script>
    <script>Prism.highlightAll();</script>'''

# Insert before closing body tag
if 'prism-sql.min.js' not in content:
    content = content.replace('</body>', prism_langs + '\n</body>')
    print("✅ Added Prism.js language components (json, nginx, sql, ini, diff) + highlightAll()")

# 2. Add class="language-bash" to bare <pre><code> blocks (most common case)
# Match <pre><code> without any class
count_fixed = 0

# Pattern: <pre><code> that doesn't already have a language class
# We need to handle: <pre><code>, <pre><code >, <pre><code style="...">
pattern = re.compile(r'(<pre><code)([^>]*>)((?:(?!</pre>).)*?</code></pre>)', re.DOTALL)

def replace_code_block(match):
    global count_fixed
    pre_code = match.group(1)
    attrs = match.group(2)
    body = match.group(3)
    
    # Skip if already has language class
    if 'language-' in match.group(0)[:200] or 'language-' in attrs:
        return match.group(0)
    
    # Determine language from content
    body_text = body.lower()
    first_lines = body[:300].lower()
    
    # YAML detection
    if ('apiversion:' in first_lines or 'kind:' in first_lines or 
        'metadata:' in first_lines or 'apiVersion:' in first_lines[:200] or
        ('---' in first_lines[:10] and ':' in first_lines)):
        lang = 'yaml'
    # Python detection
    elif ('import ' in first_lines or 'def ' in first_lines or 'class ' in first_lines or
          '#!/usr/bin/env python' in first_lines or 'print(' in first_lines[:100] or
          'from ' in first_lines[:50] and 'import ' in first_lines):
        lang = 'python'
    # SQL detection
    elif ('select ' in first_lines or 'create table' in first_lines or 
          'insert into' in first_lines or 'alter table' in first_lines or
          'grant ' in first_lines[:50] or 'postgresql' in first_lines):
        lang = 'sql'
    # nginx config detection
    elif ('server {' in first_lines or 'location /' in first_lines or 
          'upstream ' in first_lines or 'proxy_pass' in first_lines or
          'listen ' in first_lines[:50] and ('80' in first_lines or '443' in first_lines)):
        lang = 'nginx'
    # JSON detection
    elif (first_lines.strip().startswith('{') or first_lines.strip().startswith('[')):
        lang = 'json'
    # Dockerfile detection
    elif ('from ' in first_lines[:10] and ('ubuntu' in first_lines or 'python' in first_lines or 
                                           'nginx' in first_lines or 'alpine' in first_lines)):
        lang = 'docker'
    # INI/config detection
    elif (first_lines.strip().startswith('[') and ']' in first_lines[:20]):
        lang = 'ini'
    # Diff detection
    elif (first_lines.strip().startswith('---') or first_lines.strip().startswith('+++') or
          first_lines.strip().startswith('@@')):
        lang = 'diff'
    # Default to bash for shell commands
    else:
        lang = 'bash'
    
    count_fixed += 1
    return f'<pre><code class="language-{lang}"{attrs}{body}'

content = pattern.sub(replace_code_block, content)
print(f"✅ Added language classes to {count_fixed} <pre><code> blocks")

# 3. Also handle <pre> blocks that wrap code without <code> tag
# These are ASCII diagrams — add a special class
pre_no_code = re.compile(r'(<pre)([^>]*>)((?:(?!</pre>).)*?</pre>)', re.DOTALL)
count_pre_fixed = 0

def replace_pre_block(match):
    global count_pre_fixed
    tag = match.group(1)
    attrs = match.group(2)
    body = match.group(3)
    
    # Skip if has code tag or language class
    if '<code' in match.group(0)[:100] or 'language-' in attrs:
        return match.group(0)
    
    # Add class for diagram containers (no coloring needed, just consistent styling)
    count_pre_fixed += 1
    return f'<pre class="diagram-ascii"{attrs}{body}'

content = pre_no_code.sub(replace_pre_block, content)
print(f"✅ Tagged {count_pre_fixed} bare <pre> blocks as diagram-ascii")

# 4. Verify
remaining = len(re.findall(r'<pre><code>', content))
print(f"\n📊 Remaining bare <pre><code> (no class): {remaining}")

# Write output
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Syntax highlighting added to all code blocks.")
