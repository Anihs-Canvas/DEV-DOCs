import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all exam-question-item blocks
blocks = re.findall(r'<div class="exam-question-item">.*?</details>', content, re.DOTALL)

total = len(blocks)
with_pre = 0
without_pre = 0

for b in blocks:
    # Check if the eq-explanation section has a <pre> block
    expl_start = b.find('<div class="eq-explanation">')
    if expl_start != -1:
        # Find the end of this explanation (next eq-explanation or /details)
        rest = b[expl_start:]
        next_expl = rest.find('<div class="eq-explanation">', 30)  # skip the first one
        end_details = rest.find('</details>')
        if next_expl != -1 and next_expl < end_details:
            expl_content = rest[:next_expl]
        else:
            expl_content = rest[:end_details] if end_details != -1 else rest
        
        if '<pre>' in expl_content:
            with_pre += 1
        else:
            without_pre += 1
    else:
        without_pre += 1

print(f'Total Q&A blocks: {total}')
print(f'With YAML/pre: {with_pre}')
print(f'Without YAML/pre: {without_pre}')
