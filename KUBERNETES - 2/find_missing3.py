import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find all lines with exam-question-item
question_lines = []
for i, line in enumerate(lines):
    if 'class="exam-question-item"' in line:
        question_lines.append(i)

print(f"Lines with exam-question-item: {len(question_lines)}")

# For each question, check if eq-explanation appears before the next question or details end
missing = []
for idx, qline in enumerate(question_lines):
    # Determine end: next question line or 50 lines ahead (whichever is first)
    end = question_lines[idx + 1] if idx + 1 < len(question_lines) else qline + 80
    end = min(end, qline + 80)
    
    # Check for eq-explanation in this range
    has_expl = any('eq-explanation' in lines[j] for j in range(qline, end + 1))
    if not has_expl:
        # Extract question number
        for j in range(qline, min(qline + 5, len(lines))):
            match = re.search(r'<div class="eq-number">(Q\d+)</div>', lines[j])
            if match:
                qnum = match.group(1)
                # Get question preview
                preview = ""
                for k in range(j, min(j + 3, len(lines))):
                    qmatch = re.search(r'<div class="eq-question">(.*?)</div>', lines[k])
                    if qmatch:
                        preview = qmatch.group(1)[:80]
                        break
                missing.append(f"Line {qline+1}: {qnum} - {preview}")
                break

print(f"Missing explanations: {len(missing)}")
for m in missing[:20]:
    print(f"  {m}")
