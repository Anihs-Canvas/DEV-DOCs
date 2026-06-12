import re
c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()

# Find all exam-question-item blocks that DON'T have an eq-explanation
blocks = re.findall(r'<div class="exam-question-item">(.*?)</details>', c, re.DOTALL)
missing = []
for i, b in enumerate(blocks):
    if 'eq-explanation' not in b:
        # Find which chapter this is in
        pos = c.find(b)
        ch_match = re.search(r'<h4>Chapter (\d+) .*? LFCS Practice Questions</h4>', c[:pos])
        ch = ch_match.group(1) if ch_match else '?'
        # Get question text
        q = re.search(r'<div class="eq-question">(.*?)</div>', b, re.DOTALL)
        q_text = q.group(1)[:80] if q else '?'
        missing.append((ch, q_text))

print(f'Questions without explanations: {len(missing)}')
for ch, q in missing:
    print(f'  Ch {ch}: {q}...')
