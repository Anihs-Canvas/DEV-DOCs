import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<div class="exam-question-item">.*?</details>'
blocks = [(content[:m.start()].count('\n')+1, m.group()) for m in re.finditer(pattern, content, re.DOTALL)]

count = 0
for ln, block in blocks:
    if '<pre>' not in block and '<div class="eq-explanation">' in block:
        qm = re.search(r'<span class="eq-number">([^<]+)</span>', block)
        qm2 = re.search(r'<div class="eq-question">(.+?)</div>', block)
        q = qm.group(1) if qm else '?'
        question = qm2.group(1)[:100] if qm2 else '?'
        print(f'L{ln}: Q{q}: {question}')
        count += 1

print(f'\nTotal: {count} Q&As with explanation divs but no YAML')
