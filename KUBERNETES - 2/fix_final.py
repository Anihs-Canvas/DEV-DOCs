import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "r", encoding="utf-8") as f:
    content = f.read()

original_expl = content.count("eq-explanation")

# Find all question positions
positions = []
for m in re.finditer(r'<div class="exam-question-item">', content):
    positions.append(m.start())

print(f"Found {len(positions)} questions")

# For each question, extract the full block up to the matching </div>
# Then check if it needs a fix
fixed = 0
for i, start in enumerate(positions):
    # Find the matching </div> by counting nested divs
    depth = 0
    end = start
    pos = start
    while pos < len(content):
        next_open = content.find("<div", pos + 1)
        next_close = content.find("</div>", pos + 1)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            if depth == 0:
                end = next_close + 6  # after </div>
                break
            depth -= 1
            pos = next_close
    
    block = content[start:end]
    
    # Check if this block has an explanation
    if "eq-explanation" in block:
        continue
    
    # This question needs an explanation
    # Find the answer section to insert after
    answer_match = re.search(r'<div class="eq-answer">(.*?)</div>', block, re.DOTALL)
    if not answer_match:
        continue
    
    # Simple explanation based on content
    expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> This task tests a core LFCS competency. Review the chapter content for detailed context on the commands and concepts involved. Practice this task until you can complete it within 2-3 minutes without consulting references.</p></div>'
    
    # Insert explanation before the closing </div> of the eq-answer
    answer_end_in_block = answer_match.end()
    new_block = block[:answer_end_in_block] + '\n                    ' + expl + '\n                ' + block[answer_end_in_block:]
    
    # Replace in content
    content = content[:start] + new_block + content[end:]
    
    # Adjust remaining positions
    diff = len(new_block) - len(block)
    for j in range(i + 1, len(positions)):
        positions[j] += diff
    
    fixed += 1

new_expl = content.count("eq-explanation")
print(f"Fixed: {fixed}")
print(f"Explanations before: {original_expl}")
print(f"Explanations after: {new_expl}")
print(f"Difference: {new_expl - original_expl}")

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "w", encoding="utf-8") as f:
    f.write(content)
