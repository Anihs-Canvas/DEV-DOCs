import re
fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.split('\n')
issues = []

# 1. Malformed context blocks: <h4> opened but closed with </strong></p></h4>
malformed = re.findall(r'<h4>[📁📄][^<]*:</strong></p>', c)
if malformed:
    issues.append(f"⚠ {len(malformed)} malformed context blocks (mixed h4/strong/p tags)")

# 2. Self-closing tags that shouldn't be
# Check for patterns like <h4 ...></h4> with extra closing
for i, line in enumerate(lines, 1):
    # Find h4 that ends with </strong></p></h4> - malformed
    if '</strong></p></h4>' in line and '<h4>' in line:
        issues.append(f"  Line {i}: malformed h4: {line.strip()[:120]}")

# 3. Check sidebar anchors vs content IDs
sidebar_section = c.find('<nav')
sidebar_end = c.find('</nav>', sidebar_section)
sidebar = c[sidebar_section:sidebar_end]
sidebar_hrefs = re.findall(r'href="#([^"]+)"', sidebar)

content_ids = set()
for m in re.finditer(r'id="([^"]+)"', c):
    # Only count IDs in articles/sections, not in sidebar
    pos = m.start()
    if c.rfind('<nav', 0, pos) < c.rfind('</nav>', 0, pos):
        content_ids.add(m.group(1))

# Also collect IDs from sections
for m in re.finditer(r'id="(section-\d+)"', c):
    content_ids.add(m.group(1))

broken_anchors = [h for h in sidebar_hrefs if h not in content_ids]
if broken_anchors:
    issues.append(f"⚠ {len(broken_anchors)} broken sidebar anchors (no matching content ID)")
    for a in broken_anchors[:10]:
        issues.append(f"  → #{a}")

# 4. Check for duplicate IDs
all_ids = re.findall(r'id="([^"]+)"', c)
dup_ids = {i for i in all_ids if all_ids.count(i) > 1}
if dup_ids:
    issues.append(f"⚠ {len(dup_ids)} duplicate IDs: {', '.join(sorted(dup_ids)[:10])}")

# 5. Check HTML tag balance (key tags)
for tag in ['div', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'ul', 'li', 'strong', 'em', 'span', 'p']:
    opens = len(re.findall(f'<{tag}[ >]', c))
    closes = len(re.findall(f'</{tag}>', c))
    diff = opens - closes
    if diff != 0:
        issues.append(f"⚠ Tag imbalance: <{tag}> ({opens} open, {closes} close, diff={diff:+d})")

# 6. Check for orphaned </section> or </article>
extra_close = []
for tag in ['section', 'article', 'div']:
    # Count approximate nesting
    pass

# 7. Summary
arts = c.split('<article')
total = len(arts) - 1

# Count total Return Value matches in file
rv_count = c.count('<h4>Return Value</h4>')

print("=" * 60)
print("  🔍  FINAL REVISION SCAN — linux_cli.html")
print("=" * 60)
print(f"  Total lines:     {len(lines)}")
print(f"  Articles:        {total}")
print(f"  Sections:        {c.count('<section')}/{c.count('</section>')}")
print(f"  Article tags:    {c.count('<article')}/{c.count('</article>')}")
print(f"  Sidebar links:   {len(sidebar_hrefs)}")
print(f"  Content IDs:     {len(content_ids)}")
print(f"  Return Values:   {rv_count}")
print()

if issues:
    print(f"  🚨 {len(issues)} ISSUES FOUND:")
    for issue in issues:
        print(f"    {issue}")
else:
    print("  ✅ No structural issues found!")

# 8. Check for articles that might have the old broken context format
broken_ctx = []
for chunk in arts[1:]:
    end = chunk.find('</article>')
    if end == -1: continue
    b = chunk[:end]
    id_m = re.search(r'id="([^"]+)"', b)
    aid = id_m.group(1) if id_m else '?'
    # Check for broken h4 context: opens with <h4> but has </strong></p> inside
    if re.search(r'<h4>[📁📄][^<]*:</strong></p>', b):
        broken_ctx.append(aid)

if broken_ctx:
    print(f"\n  🚨 {len(broken_ctx)} malformed context blocks (mixed h4/strong/p):")
    for a in broken_ctx[:20]:
        print(f"    → {a}")
