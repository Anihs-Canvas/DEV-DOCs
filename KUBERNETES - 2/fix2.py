import re
with open('lfcs.html', 'r', encoding='utf-8') as f:
    content = f.read()

all_q = content.count('exam-question-item')
all_ex = content.count('eq-explanation')
with_details = 0
without_details = 0
no_expl_no_details = 0

pattern = re.compile(r'<div class=.exam-question-item.>(.*?)</div>\s*(?=<div class=.exam-question-item.>|<div class=.visual-summary.>|</div>\s*</div>|<!--)', re.DOTALL)
blocks = pattern.findall(content)
for i, b in enumerate(blocks):
    has_d = '<details>' in b
    has_e = 'eq-explanation' in b
    if has_d:
        with_details += 1
    else:
        without_details += 1
        if not has_e:
            no_expl_no_details += 1
            qm = re.search(r'<div class=.eq-question.>(.*?)</div>', b, re.DOTALL)
            preview = qm.group(1)[:80] if qm else '???'
            print(f'NEEDS FIX: has_details=NO  has_expl=NO  preview={preview}')

print(f'Total: {all_q}  Explanations: {all_ex}  Blocks found: {len(blocks)}')
print(f'With details: {with_details}  Without details: {without_details}')
print(f'Missing both details+expl: {no_expl_no_details}')
