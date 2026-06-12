#!/usr/bin/env python3
"""Smart syntax highlighting: code gets language classes, diagrams don't."""
import re

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Loaded: {len(content):,} chars")

def classify_block(code_text):
    """Determine if text is code or diagram, and what language."""
    text = code_text.strip()
    first_line = text.split('\n')[0].strip() if text else ''
    first_100 = text[:200].lower()
    
    # DIAGRAM DETECTORS — these should NOT get syntax highlighting
    # Box-drawing characters
    if any(c in text[:100] for c in '╔╗╚╝║═╠╣╦╩╬┌┐└┘├┤┬┴┼│─'):
        return 'diagram'
    # Tree structures with ├── └──
    if '├──' in text[:200] or '└──' in text[:200] or '│  ' in text[:100]:
        return 'diagram'
    # Arrow/flow diagrams
    if '──▶' in text[:200] or '──►' in text[:200] or '────▶' in text[:200]:
        return 'diagram'
    # Step/roadmap with STEP X:
    if re.match(r'^\s*STEP\s+\d', first_line):
        return 'diagram'
    # Process flow with → arrows
    if ' → ' in first_line and len(first_line) < 30:
        return 'diagram'
    # Title-heavy diagrams (single-line headers followed by boxes)
    if first_line.startswith('╔') and '╗' in first_line:
        return 'diagram'
    # Study time charts (bar charts)
    if first_line.startswith('█') or '████' in text[:200]:
        return 'diagram'
    # Timeline structures
    if 'LEVEL 1:' in text[:200] or 'LEVEL 2:' in text[:200]:
        return 'diagram'
    # ASCII art separators
    if first_line.startswith('===') or first_line.startswith('---') and len(first_line) > 20:
        return 'diagram'
    
    # CODE DETECTORS
    # YAML
    if ('apiversion:' in first_100 or 'apiVersion:' in first_100 or 
        'kind:' in first_100 or 'metadata:' in first_100 or
        'spec:' in first_100 and 'containers:' in first_200):
        return 'yaml'
    
    # Python
    if ('#!/usr/bin/env python' in first_100 or '#!/usr/bin/python' in first_100 or
        'import os' in first_100 or 'from django' in first_100 or
        'def ' in first_100 and 'return' in text[:500] or
        'class ' in first_100 and 'self' in text[:300]):
        return 'python'
    
    # SQL
    if re.match(r'^\s*(SELECT|CREATE\s+TABLE|INSERT\s+INTO|ALTER\s+TABLE|GRANT|DROP|UPDATE)\b', first_line, re.IGNORECASE):
        return 'sql'
    if 'postgresql' in first_100 and ('#' in first_100 or '--' in first_100):
        return 'sql'
    
    # nginx config
    if re.match(r'^\s*(server\s*\{|location\s+/|upstream\s+\w|proxy_pass|listen\s+\d)', first_line):
        return 'nginx'
    if ('server {' in text[:200] and 'listen' in text[:300] and 'location' in text[:500]):
        return 'nginx'
    
    # JSON
    if first_line.startswith('{') or first_line.startswith('['):
        if '"' in first_line or ':' in text[:100]:
            return 'json'
    
    # Dockerfile
    if re.match(r'^\s*FROM\s+\w+', first_line, re.IGNORECASE):
        if 'RUN ' in text[:500] or 'COPY ' in text[:500] or 'CMD ' in text[:500]:
            return 'docker'
    
    # INI/config
    if re.match(r'^\s*\[.*\]\s*$', first_line):
        if '=' in text[:200]:
            return 'ini'
    
    # Diff
    if first_line.startswith('--- ') or first_line.startswith('+++ ') or first_line.startswith('@@'):
        return 'diff'
    
    # Shell/bash (actual commands — look for $ or # prompts, or common bash patterns)
    if re.match(r'^\s*[$#]\s', first_line):
        return 'bash'
    if re.match(r'^\s*(apt|dnf|yum|systemctl|grep|sed|awk|find|tar|gzip|ssh|scp|git|docker|podman|kubectl|chmod|chown|useradd|usermod|passwd|mount|umount|iptables|ufw|firewall|ps|kill|top|htop|free|df|du|ls|cd|cp|mv|rm|mkdir|touch|cat|echo|export|source|curl|wget|python|pip|npm|node|make|gcc)\b', first_line):
        return 'bash'
    if re.match(r'^\s*(for|while|if|case|function|alias)\b', first_line):
        return 'bash'
    if 'sudo ' in first_line[:50] or '#!/bin/bash' in first_100 or '#!/bin/sh' in first_100:
        return 'bash'
    # Comment lines that look like command documentation
    if first_line.startswith('# ') and any(cmd in first_100 for cmd in ['command', 'example', 'syntax', 'usage']):
        return 'bash'
    
    # Default — if it has typical code patterns, assume bash
    if any(c in text[:100] for c in ['{', '}', ';', '&&', '||', '|', '>>', '<<']):
        return 'bash'
    if '#' in text[:200] and '\n' in text[:200]:
        return 'bash'
    
    # If nothing matches, it's a diagram
    return 'diagram'

# Process all <pre> blocks
count_fixed = 0
count_diagram = 0
count_code = 0

# Find <pre> blocks that already have a language- class and fix misclassified ones
pre_pattern = re.compile(r'<pre[^>]*>(.*?)</pre>', re.DOTALL)
code_pattern = re.compile(r'<code[^>]*>(.*?)</code>', re.DOTALL)

def process_pre_block(m):
    global count_fixed, count_diagram, count_code
    full = m.group(0)
    inner = m.group(1)
    
    # Extract code content (may be in <code> or direct)
    code_m = code_pattern.search(full)
    actual_code = code_m.group(1) if code_m else inner
    
    classification = classify_block(actual_code)
    
    if classification == 'diagram':
        count_diagram += 1
        # Remove any existing language class, add diagram-ascii
        result = re.sub(r'class="[^"]*language-\w+[^"]*"', '', full)
        if 'class="diagram-ascii"' not in result:
            result = result.replace('<pre', '<pre class="diagram-ascii"', 1)
        elif 'class=' not in result[:50]:
            result = result.replace('<pre', '<pre class="diagram-ascii"', 1)
        return result
    else:
        count_code += 1
        lang = classification
        # Add language class to <code> tag or <pre> tag
        if '<code' in full:
            if 'class="language-' in full:
                # Already has a class, replace if wrong
                old_lang = re.search(r'class="language-(\w+)"', full)
                if old_lang and old_lang.group(1) != lang:
                    result = full.replace(f'language-{old_lang.group(1)}', f'language-{lang}')
                    count_fixed += 1
                    return result
            elif 'class=' not in full[:100]:
                result = full.replace('<code', f'<code class="language-{lang}"', 1)
                count_fixed += 1
                return result
        else:
            if 'class="language-' in full:
                old_lang = re.search(r'class="language-(\w+)"', full)
                if old_lang and old_lang.group(1) != lang:
                    result = full.replace(f'language-{old_lang.group(1)}', f'language-{lang}')
                    count_fixed += 1
                    return result
            elif 'class=' not in full[:50]:
                result = full.replace('<pre', f'<pre class="language-{lang}"', 1)
                count_fixed += 1
                return result
    
    return full

content = pre_pattern.sub(process_pre_block, content)

print(f"Diagrams tagged: {count_diagram}")
print(f"Code blocks classified: {count_code}")
print(f"Language fixes applied: {count_fixed}")

# Verify
diagram_count = content.count('diagram-ascii')
bash_count = len(re.findall(r'language-bash', content))
python_count = len(re.findall(r'language-python', content))
yaml_count = len(re.findall(r'language-yaml', content))
sql_count = len(re.findall(r'language-sql', content))
nginx_count = len(re.findall(r'language-nginx', content))
docker_count = len(re.findall(r'language-docker', content))
json_count = len(re.findall(r'language-json', content))
ini_count = len(re.findall(r'language-ini', content))

print(f"\n📊 Language distribution:")
print(f"  diagram-ascii: {diagram_count}")
print(f"  bash:    {bash_count}")
print(f"  python:  {python_count}")
print(f"  yaml:    {yaml_count}")
print(f"  sql:     {sql_count}")
print(f"  nginx:   {nginx_count}")
print(f"  docker:  {docker_count}")
print(f"  json:    {json_count}")
print(f"  ini:     {ini_count}")

# Check key anchors
for aid in ['ch1', 'ch45', 'master-summary']:
    if f'id="{aid}"' not in content:
        print(f"⚠️ MISSING: {aid}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("\nDone!")
