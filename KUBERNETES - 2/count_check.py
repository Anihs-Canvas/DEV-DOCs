import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Count total exam-question-item
all_q = re.findall(r'class="exam-question-item"', c)
print(f'Total exam-question-item divs: {len(all_q)}')

# Count using regex blocks
all_blocks = re.findall(r'<div class="exam-question-item">.*?</details>\s*</div>', c, re.DOTALL)
no_exp = [b for b in all_blocks if 'eq-explanation' not in b]
has_exp = [b for b in all_blocks if 'eq-explanation' in b]
print(f'Total blocks (regex): {len(all_blocks)}')
print(f'Blocks with explanation: {len(has_exp)}')
print(f'Blocks without explanation: {len(no_exp)}')

# Check for blocks without eq-answer
no_answer = [b for b in all_blocks if 'eq-answer' not in b]
print(f'Blocks without eq-answer: {len(no_answer)}')

# Check for blocks that have BOTH eq-answer and eq-explanation
both = [b for b in all_blocks if 'eq-answer' in b and 'eq-explanation' in b]
print(f'Blocks with both: {len(both)}')

# Check edge cases
only_answer = [b for b in all_blocks if 'eq-answer' in b and 'eq-explanation' not in b]
print(f'Blocks with answer only (no explanation): {len(only_answer)}')

# Check special patterns
only_exp = [b for b in all_blocks if 'eq-explanation' in b and 'eq-answer' not in b]
print(f'Blocks with explanation only (no answer): {len(only_exp)}')
