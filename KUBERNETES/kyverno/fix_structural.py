import re
fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = 0

# FIX 1: Malformed context blocks
# Pattern: <h4>📄 Context — TEXT:</strong></p><pre><code class="language-yaml">
# Fix: <h4>📄 Context — TEXT:</h4>\n                <pre><code class="language-yaml">
# And closing: </code></pre></h4> → </code></pre>

old_open_pattern = r'<h4>(📄 Context — [^:]+):</strong></p><pre><code class="language-yaml">'
def fix_open(m):
    global fixes
    fixes += 1
    return f'<h4>{m.group(1)}:</h4>\n                <pre><code class="language-yaml">'

c, n1 = re.subn(old_open_pattern, fix_open, c)

# Fix closing: </code></pre></h4> → </code></pre>
# But only for context blocks. The safest approach: fix all </code></pre></h4> that follow
# a 📄 Context pattern. Actually, let me just find and fix the specific broken ones.
# Pattern: </code></pre></h4>\n<h4>Examples</h4> → </code></pre>\n\n<h4>Examples</h4>

old_close = r'</code></pre></h4>\n<h4>Examples</h4>'
new_close = r'</code></pre>\n\n<h4>Examples</h4>'
c, n2 = re.subn(old_close, new_close, c)
fixes += n2

print(f"Fixed {n1} context block openings + {n2} context block closings")

# FIX 2: Find and report duplicate IDs
all_ids = re.findall(r'id="([^"]+)"', c)
dup_ids = {i for i in all_ids if all_ids.count(i) > 1}
print(f"\nDuplicate IDs: {sorted(dup_ids)}")

# Find positions of each duplicate
for did in sorted(dup_ids):
    positions = [m.start() for m in re.finditer(f'id="{did}"', c)]
    for i, pos in enumerate(positions):
        line_num = c[:pos].count('\n') + 1
        # Get context around the id
        ctx_start = max(0, pos - 50)
        ctx_end = min(len(c), pos + 100)
        snippet = c[ctx_start:ctx_end].replace('\n', '\\n')
        print(f"  {did} occurrence {i+1}: line {line_num} — ...{snippet[:120]}...")

# FIX 3: Tag balance check after fixes
for tag in ['strong', 'p']:
    opens = len(re.findall(f'<{tag}[ >]', c))
    closes = len(re.findall(f'</{tag}>', c))
    print(f"\n<{tag}>: {opens} open, {closes} close, diff={opens - closes:+d}")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print(f"\nTags: {c.count('<article')}/{c.count('</article>')}, {c.count('<section')}/{c.count('</section>')}")
print(f"Lines: {len(c.split(chr(10)))}")
