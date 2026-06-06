"""Final comprehensive audit of k8s-cluster-structure.html"""
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html', 'r', encoding='utf-8') as f:
    h = f.read()

print("=" * 60)
print("FINAL DOCUMENT AUDIT")
print("=" * 60)

# Overall stats
print(f'\nTotal lines: {h.count(chr(10)):,}')
print(f'Total chars: {len(h):,}')

# Count all parts
parts = re.findall(r'<section class="section" id="part-(\d+)">', h)
print(f'\nParts present: {sorted(set(parts), key=int)} ({len(set(parts))} sections)')

# Count major elements
print(f'\n--- Element Counts ---')
print(f'Tables:          {h.count("<table>")}')
print(f'Code blocks:     {h.count("<pre><code")}')
print(f'ASCII blocks:    {h.count("ascii-block")}')
print(f'Diagram boxes:   {h.count("diagram-box")}')
print(f'Highlight boxes: {h.count("highlight-box")}')
print(f'Warning boxes:   {h.count("warning")}')
print(f'Info boxes:      {h.count("class=\"info\"")}')
print(f'API blocks:      {h.count("api-block")}')

# Check for unescaped << in code blocks
blocks = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', h, re.DOTALL)
print(f'\n--- Code Block Audit ---')
print(f'Total code blocks: {len(blocks)}')
issues = 0
for i, b in enumerate(blocks):
    if '<<' in b and '&lt;&lt;' not in b:
        # Double check - count actual << vs &lt;&lt;
        lt_count = b.count('&lt;&lt;')
        raw_count = b.count('<<')
        if raw_count > lt_count:
            print(f'  ISSUE: Block {i} has {raw_count - lt_count} unescaped <<')
            issues += 1
if issues == 0:
    print('All << patterns properly escaped in code blocks')

# Tag balance check
print(f'\n--- Tag Balance ---')
divs_open = len(re.findall(r'<div[ >]', h))
divs_close = len(re.findall(r'</div>', h))
print(f'<div>:  {divs_open} open, {divs_close} close {"✅" if divs_open == divs_close else "❌ MISMATCH"}')

sections_open = len(re.findall(r'<section[ >]', h))
sections_close = len(re.findall(r'</section>', h))
print(f'<section>: {sections_open} open, {sections_close} close {"✅" if sections_open == sections_close else "❌ MISMATCH"}')

pre_open = len(re.findall(r'<pre[ >]', h))
pre_close = len(re.findall(r'</pre>', h))
print(f'<pre>:  {pre_open} open, {pre_close} close {"✅" if pre_open == pre_close else "❌ MISMATCH"}')

table_open = len(re.findall(r'<table[ >]', h))
table_close = len(re.findall(r'</table>', h))
print(f'<table>: {table_open} open, {table_close} close {"✅" if table_open == table_close else "❌ MISMATCH"}')

# Cross-reference links
xrefs = re.findall(r'href="#part-', h)
print(f'\nCross-reference links: {len(xrefs)}')

# Check for any raw & that aren't entity starts
raw_amps = re.findall(r'&(?!(?:lt|gt|amp|quot|apos|#\d+|#x[0-9a-fA-F]+);)', h)
if raw_amps:
    print(f'\nWARNING: {len(raw_amps)} potentially unescaped & characters')
else:
    print('\nNo unescaped & characters found')

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
