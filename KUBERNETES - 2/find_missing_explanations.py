import re
from collections import defaultdict

# Read the file
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Track chapters: {line_number: (id, title)}
chapters = {}
chapter_starts = []
special_starts = []

for i, line in enumerate(lines):
    # Chapter sections
    m = re.search(r'id="(ch\d+)" class="chapter-section"', line)
    if m:
        chapter_starts.append((i + 1, m.group(1)))
    # Also track special sections
    m2 = re.search(r'id="(master-summary|exam-readiness|exam-strategy)" class="chapter-section"', line)
    if m2:
        special_starts.append((i + 1, m2.group(1)))

# Find chapter titles (h2 that follows the chapter div)
for line_no, ch_id in chapter_starts:
    title = ch_id
    for j in range(line_no, min(line_no + 5, len(lines))):
        m = re.search(r'<h2[^>]*>(.*?)</h2>', lines[j - 1])
        if m:
            title = m.group(1).strip()
            title = re.sub(r'<[^>]+>', '', title).strip()
            break
    chapters[line_no] = (ch_id, title)

for line_no, sec_id in special_starts:
    title = sec_id
    for j in range(line_no, min(line_no + 5, len(lines))):
        m = re.search(r'<h2[^>]*>(.*?)</h2>', lines[j - 1])
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            break
    chapters[line_no] = (sec_id, title)

# Sort chapter starts
sorted_chapters = sorted(chapters.keys())
print(f"Found {len(chapters)} chapter/section markers:")
for ch_start in sorted_chapters:
    print(f"  Line {ch_start}: {chapters[ch_start]}")

# Now scan for exam questions
missing_explanations = []
questions_with_exp = 0

i = 0
while i < len(lines):
    line = lines[i]
    if 'class="exam-question-item"' in line:
        question_start = i + 1  # 1-indexed line number

        # Determine which chapter this belongs to
        current_chapter = ('Unknown', 'Unknown')
        for ch_start in sorted_chapters:
            if ch_start <= question_start:
                current_chapter = chapters[ch_start]
            else:
                break

        # Extract Q number
        q_match = re.search(r'eq-number">(Q\d+)', line)
        q_num = q_match.group(1) if q_match else '?'

        # Extract question text
        q_text_match = re.search(r'eq-question">(.*?)</p>', line)
        q_text = q_text_match.group(1) if q_text_match else '?'

        # Now find the entire block
        has_answer = False
        has_explanation = False
        answer_parts = []
        end_line = question_start

        j = i + 1
        in_answer = False

        while j < len(lines):
            current_line = lines[j]
            if 'class="eq-answer"' in current_line:
                has_answer = True
                in_answer = True
            if 'class="eq-explanation"' in current_line:
                has_explanation = True
                in_answer = False
            if in_answer:
                # Extract answer text from <p> tags, skip label
                p_matches = re.findall(r'<p[^>]*>(.*?)</p>', current_line)
                for pm in p_matches:
                    if 'eq-answer-label' not in pm and 'ANSWER' not in pm:
                        text = re.sub(r'<[^>]+>', '', pm).strip()
                        if text:
                            answer_parts.append(text)
                # Also check for pre blocks in answer
                pre_match = re.search(r'<pre[^>]*>(.*?)</pre>', current_line, re.DOTALL)
                if pre_match:
                    text = re.sub(r'<[^>]+>', '', pre_match.group(1)).strip()
                    if text:
                        answer_parts.append(text)
            if '</details>' in current_line:
                end_line = j + 1
                break
            j += 1

        answer_text = ' '.join(answer_parts)

        if has_answer and not has_explanation:
            missing_explanations.append({
                'chapter_id': current_chapter[0],
                'chapter_title': current_chapter[1],
                'q_num': q_num,
                'q_text': q_text[:300],
                'answer': answer_text[:300],
                'start_line': question_start,
                'end_line': end_line
            })
        elif has_answer and has_explanation:
            questions_with_exp += 1

        i = j
    else:
        i += 1

# Group by chapter
grouped = defaultdict(list)
for item in missing_explanations:
    grouped[(item['chapter_id'], item['chapter_title'])].append(item)

print(f"\nTotal questions with explanations: {questions_with_exp}")
print(f"Total missing explanations: {len(missing_explanations)}")
print()

# Print grouped by chapter
for ch_key in sorted(grouped.keys(), key=lambda x: next((k for k in chapters.values() if k[0] == x[0]), (999, ''))[0]):
    ch_id, ch_title = ch_key
    items = grouped[ch_key]
    print(f"\n{'=' * 80}")
    print(f"CHAPTER: {ch_id} — {ch_title}")
    print(f"Missing explanations: {len(items)}")
    print(f"{'=' * 80}")
    for item in items:
        print(f"\n  Q#: {item['q_num']} (Lines {item['start_line']}-{item['end_line']})")
        print(f"  Question: {item['q_text'][:200]}")
        if item['answer']:
            print(f"  Answer: {item['answer'][:250]}")
        else:
            print(f"  Answer: [NO ANSWER TEXT EXTRACTED]")

# Also print a flat summary
print(f"\n\n{'=' * 80}")
print("FLAT SUMMARY — All {0} missing explanations".format(len(missing_explanations)))
print(f"{'=' * 80}")
for i, item in enumerate(missing_explanations):
    print(f"{i+1}. [{item['chapter_id']}] {item['q_num']} (Line {item['start_line']}): {item['q_text'][:120]}")
