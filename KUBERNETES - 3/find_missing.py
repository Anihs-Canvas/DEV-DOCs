import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 3\Backstage.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all exam questions without explanations
# Pattern: answer ending </div></details></div> NOT followed by eq-explanation
# but followed by next question or end of section

# We'll find each exam block and process questions
exam_blocks = list(re.finditer(r'<div class="cba-exam-questions"><h4>📝 Chapter (\d+).*?</h4>(.*?)</div>\s*(?:<div class="cba-speed-tip">|<div class="visual-summary">)', content, re.DOTALL))

print(f"Found {len(exam_blocks)} exam blocks")

changes = []

for match in exam_blocks:
    ch_num = match.group(1)
    block = match.group(2)
    
    # Find individual questions
    questions = list(re.finditer(r'(<div class="exam-question-item">.*?</details></div>)', block, re.DOTALL))
    
    missing = 0
    for q in questions:
        q_html = q.group(1)
        has_exp = 'eq-explanation' in q_html
        if not has_exp:
            missing += 1
    
    if missing > 0:
        print(f"  Ch {ch_num}: {missing}/{len(questions)} missing explanations")

print(f"\nTotal changes to process: checking for patterns...")

# For each missing explanation, we need to insert after </div> before </details>
# Let's find all missing and show the question text
total_missing = 0
for match in exam_blocks:
    ch_num = match.group(1)
    block = match.group(2)
    questions = list(re.finditer(r'(<div class="exam-question-item">.*?</details></div>)', block, re.DOTALL))
    for q in questions:
        q_html = q.group(1)
        if 'eq-explanation' not in q_html:
            total_missing += 1
            # Extract question text
            qtext_match = re.search(r'<div class="eq-question">(.*?)</div>', q_html)
            qtext = qtext_match.group(1) if qtext_match else "UNKNOWN"
            print(f"  Ch{ch_num}: {qtext[:80]}...")

print(f"\nTotal missing: {total_missing}")
