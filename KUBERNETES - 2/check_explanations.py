import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all exam-question-item blocks
pattern = r'<div class="exam-question-item">.*?</details>\s*</div>'
blocks = re.findall(pattern, content, re.DOTALL)

missing = 0
has_exp = 0
missing_info = []

for block in blocks:
    if 'eq-explanation' in block:
        has_exp += 1
    else:
        missing += 1
        q_match = re.search(r'eq-number">(Q\d+)', block)
        q_num = q_match.group(1) if q_match else '?'
        q_text_match = re.search(r'eq-question">(.*?)</p>', block)
        q_text = q_text_match.group(1)[:100] if q_text_match else '?'
        missing_info.append((q_num, q_text[:80]))

print(f'With explanation: {has_exp}')
print(f'Missing: {missing}')
print()
for q_num, q_text in missing_info:
    print(f'{q_num}: {q_text}...')
