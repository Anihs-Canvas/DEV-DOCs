import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all exam-question-item blocks
pattern = r'<div class="exam-question-item">.*?</details>'
blocks = [(m.start(), m.group()) for m in re.finditer(pattern, content, re.DOTALL)]

without_pre = []
for pos, block in blocks:
    if '<pre>' not in block:
        # Find line number
        line_num = content[:pos].count('\n') + 1
        # Extract Q number
        q_match = re.search(r'<span class="eq-number">([^<]+)</span>', block)
        q_num = q_match.group(1) if q_match else "?"
        # Check if has explanation div
        has_expl = '<div class="eq-explanation">' in block
        without_pre.append((line_num, q_num, has_expl))

print(f"Total without <pre>: {len(without_pre)}")
print(f"With explanation div: {sum(1 for _,_,e in without_pre if e)}")
print(f"Without explanation div: {sum(1 for _,_,e in without_pre if not e)}")
print()
# Group by line ranges (rough chapters)
for ln, qn, ex in without_pre:
    ch = "?"
    if ln < 2930: ch = "Ch1"
    elif ln < 3870: ch = "Ch2"
    elif ln < 4544: ch = "Ch3"
    elif ln < 5247: ch = "Ch4"
    elif ln < 5788: ch = "Ch5"
    elif ln < 6459: ch = "Ch6"
    elif ln < 6890: ch = "Ch7"
    elif ln < 7550: ch = "Ch8-9"
    elif ln < 8500: ch = "Ch10-12"
    elif ln < 9250: ch = "Ch13-14"
    elif ln < 10100: ch = "Ch15-16"
    elif ln < 10600: ch = "Ch17a"
    elif ln < 12500: ch = "Ch17b-20"
    elif ln < 13800: ch = "Ch21+App"
    else: ch = "App F"
    print(f"  L{ln}: {ch} Q{qn}  {'[has expl]' if ex else '[no expl]'}")
