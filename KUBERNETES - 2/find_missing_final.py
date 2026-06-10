import re
from collections import defaultdict

FILE_PATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\finOps_ai.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# ── Find all chapter markers ──
chapter_markers = []  # (line_number, chapter_id, chapter_title)
for i, line in enumerate(lines):
    m = re.search(r'id="(ch\d+|master-summary|exam-readiness|exam-strategy|appendix-i)" class="chapter-section"', line)
    if m:
        ch_id = m.group(1)
        title = ch_id
        for offset in range(0, 5):
            if i + offset < len(lines):
                h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', lines[i + offset])
                if h2_match:
                    title = re.sub(r'<[^>]+>', '', h2_match.group(1)).strip()
                    break
        chapter_markers.append((i + 1, ch_id, title))

# ── Find all exam question blocks using regex ──
block_pattern = r'<div class="exam-question-item">(.*?)</details>\s*</div>'
all_blocks = list(re.finditer(block_pattern, content, re.DOTALL))

# ── For each block without explanation, extract info ──
missing = []

for block_match in all_blocks:
    block = block_match.group(0)
    start_pos = block_match.start()
    # Calculate line number
    start_line = content[:start_pos].count('\n') + 1

    if 'eq-explanation' in block:
        continue  # Has explanation, skip

    # Determine chapter
    ch_id, ch_title = ('Unknown', 'Unknown')
    for ln, cid, ctitle in chapter_markers:
        if ln <= start_line:
            ch_id, ch_title = cid, ctitle
        else:
            break

    # Extract Q number
    q_match = re.search(r'eq-number">(Q\d+)', block)
    q_num = q_match.group(1) if q_match else '?'

    # Extract question text
    q_text_match = re.search(r'eq-question">(.*?)</p>', block)
    if not q_text_match:
        q_text_match = re.search(r'<p>(.*?)</p>', block)
    q_text = q_text_match.group(1) if q_text_match else '?'
    q_text = re.sub(r'<[^>]+>', '', q_text).strip()

    # Extract answer text
    ans_match = re.search(r'class="eq-answer"[^>]*>(.*?)(?=</div>\s*(?:</details>))', block, re.DOTALL)
    answer_text = ''
    if ans_match:
        ans_raw = ans_match.group(1)
        ans_raw = re.sub(r'<div class="eq-answer-label">.*?</div>', '', ans_raw, flags=re.DOTALL)
        answer_text = re.sub(r'<[^>]+>', ' ', ans_raw).strip()
        answer_text = re.sub(r'\s+', ' ', answer_text)

    # Calculate end line
    end_pos = block_match.end()
    end_line = content[:end_pos].count('\n') + 1

    missing.append({
        'chapter_id': ch_id,
        'chapter_title': ch_title,
        'q_num': q_num,
        'q_text': q_text,
        'answer': answer_text,
        'start_line': start_line,
        'end_line': end_line,
    })

# ── Group by chapter ──
grouped = defaultdict(list)
for q in missing:
    key = (q['chapter_id'], q['chapter_title'])
    grouped[key].append(q)

ch_order = {cid: idx for idx, (ln, cid, ctitle) in enumerate(chapter_markers)}
grouped_sorted = sorted(grouped.items(), key=lambda x: ch_order.get(x[0][0], 999))

print(f"TOTAL MISSING EXPLANATIONS: {len(missing)}")
print()

for (ch_id, ch_title), items in grouped_sorted:
    print(f"{'=' * 80}")
    print(f"CHAPTER: {ch_id} — {ch_title}")
    print(f"Missing explanations: {len(items)}")
    print(f"{'=' * 80}")
    for item in items:
        print(f"\n  Q#: {item['q_num']} (Lines {item['start_line']}-{item['end_line']})")
        print(f"  Question: {item['q_text'][:300]}")
        if item['answer']:
            print(f"  Answer:   {item['answer'][:400]}")
        else:
            print(f"  Answer:   [EMPTY]")

# Flat summary
print(f"\n\n{'=' * 80}")
print(f"FLAT SUMMARY — All {len(missing)} missing explanations")
print(f"{'=' * 80}")
for idx, item in enumerate(missing):
    print(f"{idx+1:3d}. [{item['chapter_id']:12s}] {item['q_num']:4s} (L{item['start_line']:5d}): {item['q_text'][:130]}")
