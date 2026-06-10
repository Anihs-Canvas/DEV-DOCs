import re
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html','r',encoding='utf-8').read()

# Check exam-question-item blocks specifically
items = re.findall(r'<div class="exam-question-item">.*?</details>', c, re.DOTALL)
total = len(items)
enriched = sum(1 for i in items if '<pre>' in i or '<table' in i or 'diagram-container' in i or 'code-block-wrapper' in i)
print(f'Exam Q&A blocks: {total}')
print(f'Enriched (with visuals): {enriched} ({enriched/total*100:.0f}%)')
print(f'Still text-only: {total - enriched}')

# Show topics of remaining unenriched
print('\n--- Remaining text-only topics ---')
for i, item in enumerate(items):
    if not ('<pre>' in item or '<table' in item or 'diagram-container' in item or 'code-block-wrapper' in item):
        qm = re.search(r'class="eq-question">(.*?)</div>', item)
        if qm:
            print(f'  {i+1}: {qm.group(1)[:120]}')

print(f'\n</main> tags: {c.count("</main>")}')
print(f'Section tags: open={c.count("<section")} close={c.count("</section")}')
