"""Fix unescaped <<EOF in Part 8 code blocks breaking HTML parser"""

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# Find Part 8 section boundaries
start = html.find('<section class="section" id="part-8">')
end = html.find('<section class="section" id="part-9">')
part8 = html[start:end]

count = part8.count('<<EOF')
print(f'Found {count} unescaped <<EOF in Part 8')

# Replace <<EOF with &lt;&lt;EOF inside Part 8 only
part8_fixed = part8.replace('<<EOF', '&lt;&lt;EOF')
html = html[:start] + part8_fixed + html[end:]

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open(fp, 'r', encoding='utf-8') as f:
    html2 = f.read()
remaining = html2[start:html2.find('<section class="section" id="part-9">')].count('<<EOF')
print(f'After fix: {remaining} remaining in Part 8')
print(f'Total lines: {html2.count(chr(10))}')
