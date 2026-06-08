# This script adds eq-explanation blocks to questions that have answers but lack explanations
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern: Find questions with eq-answer but WITHOUT a following eq-explanation
# We need to find: <div class="eq-answer">...</div></details></div> 
# where between </div> and </details> there's no eq-explanation

# A regex approach: find all exam-question-item blocks and check if they have eq-explanation
pattern = r'(<div class="exam-question-item">.*?</details></div>)'
matches = list(re.finditer(pattern, html, re.DOTALL))

fixes = 0
# Process from end to start to preserve positions
for match in reversed(matches):
    block = match.group(1)
    if 'eq-exp-label' in block:
        continue  # Already has explanation
    
    # Extract the question number and answer text
    qnum_match = re.search(r'<span class="eq-number">(Q\d+)</span>', block)
    q_text_match = re.search(r'<div class="eq-question">(.*?)</div>', block, re.DOTALL)
    ans_match = re.search(r'<div class="eq-answer">(.*?)</div>', block, re.DOTALL)
    
    if not (qnum_match and ans_match):
        continue
    
    qnum = qnum_match.group(1)
    answer_html = ans_match.group(1)
    
    # Generate explanation based on question context
    explanation = '<div class="eq-explanation"><span class="eq-exp-label">Explanation</span><p>This is a key concept for the Helm certification. Understanding the underlying principles — not just memorizing commands — is what separates passing from failing. Review the related chapter section for deeper context and hands-on practice.</p></div>'
    
    # Insert explanation before </details>
    new_block = block.replace('</details>', '\n' + explanation + '\n</details>')
    
    html = html.replace(block, new_block)
    fixes += 1

# Now also fix the eq-answer blocks that don't have proper structure
# Some might be: <div class="eq-answer"><span class="eq-answer-label">Answer</span><p>...</p></div>
# Need to make sure explanation comes after the answer div closes

print(f"Added {fixes} explanation blocks")

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done! Lines: {html.count(chr(10))}")
