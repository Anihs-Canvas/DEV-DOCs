import re
from collections import defaultdict, OrderedDict

FILE_PATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

total_lines = len(lines)
print(f"Total lines: {total_lines}")

# ── Step 1: Find all chapter markers with line numbers ──
chapter_markers = []  # (line_number, chapter_id, chapter_title)

for i, line in enumerate(lines):
    m = re.search(r'id="(ch\d+|master-summary|exam-readiness|exam-strategy)" class="chapter-section"', line)
    if m:
        ch_id = m.group(1)
        # Look ahead up to 3 lines for the h2 title
        title = ch_id
        for offset in range(0, 4):
            if i + offset < len(lines):
                h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', lines[i + offset])
                if h2_match:
                    title = re.sub(r'<[^>]+>', '', h2_match.group(1)).strip()
                    break
        chapter_markers.append((i + 1, ch_id, title))

print(f"\nFound {len(chapter_markers)} chapter markers:")
for ln, cid, ctitle in chapter_markers:
    print(f"  Line {ln}: {cid} — {ctitle}")

# ── Step 2: Find all exam-question-item blocks using regex on full content ──
# We'll find blocks from <div class="exam-question-item"> to </details></div>
# But we need line numbers, so we'll use a line-by-line approach with proper state tracking

questions = []  # list of dicts

i = 0
while i < total_lines:
    line = lines[i]
    if 'class="exam-question-item"' not in line:
        i += 1
        continue

    start_line = i + 1  # 1-indexed

    # Extract Q number
    q_match = re.search(r'eq-number">(Q\d+)', line)
    q_num = q_match.group(1) if q_match else '?'

    # Extract question text - try eq-question class first, then plain <p>
    q_text_match = re.search(r'eq-question">(.*?)</p>', line)
    if not q_text_match:
        q_text_match = re.search(r'<p>(.*?)</p>', line)
    q_text = q_text_match.group(1) if q_text_match else '?'
    q_text = re.sub(r'<[^>]+>', '', q_text).strip()

    # Determine which chapter
    ch_id, ch_title = ('Unknown', 'Unknown')
    for ln, cid, ctitle in chapter_markers:
        if ln <= start_line:
            ch_id, ch_title = cid, ctitle
        else:
            break

    # Now collect the full block - find </details></div>
    block_text = line
    end_line = start_line
    has_answer = False
    has_explanation = False

    if '</details></div>' in line:
        # Single-line question
        end_line = start_line
    else:
        # Multi-line question - scan forward
        j = i + 1
        while j < total_lines:
            block_text += '\n' + lines[j]
            if '</details></div>' in lines[j]:
                end_line = j + 1
                break
            j += 1
        if end_line == start_line:
            end_line = j + 1  # safety

    has_answer = 'class="eq-answer"' in block_text
    has_explanation = 'class="eq-explanation"' in block_text

    # Extract answer text
    answer_text = ''
    ans_match = re.search(r'class="eq-answer"[^>]*>(.*?)(?=</div>\s*(?:<div class="eq-explanation"|</details>))', block_text, re.DOTALL)
    if ans_match:
        ans_raw = ans_match.group(1)
        # Remove the label div
        ans_raw = re.sub(r'<div class="eq-answer-label">.*?</div>', '', ans_raw, flags=re.DOTALL)
        answer_text = re.sub(r'<[^>]+>', ' ', ans_raw).strip()
        answer_text = re.sub(r'\s+', ' ', answer_text)

    if not has_explanation:
        questions.append({
            'chapter_id': ch_id,
            'chapter_title': ch_title,
            'q_num': q_num,
            'q_text': q_text,
            'answer': answer_text,
            'start_line': start_line,
            'end_line': end_line,
            'has_answer': has_answer,
            'has_explanation': has_explanation
        })

    if end_line > start_line:
        i = end_line  # 1-indexed to 0-indexed
    else:
        i += 1

# ── Step 3: Group by chapter ──
grouped = defaultdict(list)
for q in questions:
    key = (q['chapter_id'], q['chapter_title'])
    grouped[key].append(q)

# Sort chapters by their marker order
ch_order = {cid: idx for idx, (ln, cid, ctitle) in enumerate(chapter_markers)}
grouped_sorted = sorted(grouped.items(), key=lambda x: ch_order.get(x[0][0], 999))

print(f"\n\nTOTAL MISSING EXPLANATIONS: {len(questions)}")
print()

for (ch_id, ch_title), items in grouped_sorted:
    print(f"{'=' * 80}")
    print(f"CHAPTER: {ch_id} — {ch_title}")
    print(f"Missing explanations: {len(items)}")
    print(f"{'=' * 80}")
    for item in items:
        print(f"\n  Q#: {item['q_num']} (Lines {item['start_line']}-{item['end_line']})")
        print(f"  Question: {item['q_text'][:250]}")
        if item['answer']:
            print(f"  Answer:   {item['answer'][:350]}")
        else:
            print(f"  Answer:   [EMPTY OR NOT FOUND]")

# Flat summary
print(f"\n\n{'=' * 80}")
print(f"FLAT SUMMARY — All {len(questions)} missing explanations")
print(f"{'=' * 80}")
for idx, item in enumerate(questions):
    print(f"{idx+1:3d}. [{item['chapter_id']}] {item['q_num']:4s} (L{item['start_line']:5d}): {item['q_text'][:130]}")
