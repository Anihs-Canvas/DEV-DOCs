import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
changes = 0

def find_closing_div(html_slice, start_pos):
    """Find matching </div> for a <div> at start_pos"""
    depth = 0
    i = start_pos
    while i < len(html_slice):
        next_open = html_slice.find('<div', i)
        next_close = html_slice.find('</div>', i)
        if next_close < 0:
            return -1
        if next_open >= 0 and next_open < next_close:
            depth += 1
            i = next_open + 4
        else:
            if depth == 0:
                return next_close + len('</div>')
            depth -= 1
            i = next_close + len('</div>')
    return -1

for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 20 else 'id="appendix-a"'
    
    ch_start = html.find(cid)
    if ch_start < 0:
        continue
    
    div_start = html.rfind('<div', 0, ch_start)
    if div_start < 0:
        continue
    
    ch_end = html.find(ncid, ch_start + 1)
    if ch_end < 0:
        continue
    
    chapter_html = html[div_start:ch_end]
    
    qa_match = re.search(r'<div class="cka-exam-questions">', chapter_html)
    drill_match = re.search(r'<div class="ckad-practice-drill"', chapter_html)
    
    if not qa_match and not drill_match:
        continue
    
    blocks_to_move = []
    
    if qa_match:
        qa_start = div_start + qa_match.start()
        qa_rel_end = find_closing_div(chapter_html, qa_match.end())
        if qa_rel_end > 0:
            qa_end = div_start + qa_rel_end
            after_qa = html[qa_end:ch_end].strip()
            if after_qa:
                # Include preceding comment
                qa_start_adj = html.rfind('<!--', max(0, qa_start-200), qa_start)
                if qa_start_adj > 0 and 'Practice' in html[qa_start_adj:qa_start]:
                    qa_text = html[qa_start_adj:qa_end]
                    qa_start = qa_start_adj
                else:
                    qa_text = html[qa_start:qa_end]
                blocks_to_move.append((qa_start, qa_end, qa_text, 'Q&A'))
    
    if drill_match:
        drill_start = div_start + drill_match.start()
        drill_rel_end = find_closing_div(chapter_html, drill_match.end())
        if drill_rel_end > 0:
            drill_end = div_start + drill_rel_end
            after_drill = html[drill_end:ch_end].strip()
            if after_drill:
                already_in_qa = any(b[0] <= drill_start < b[1] for b in blocks_to_move)
                if not already_in_qa:
                    drill_text = html[drill_start:drill_end]
                    blocks_to_move.append((drill_start, drill_end, drill_text, 'Drill'))
    
    if blocks_to_move:
        blocks_to_move.sort(key=lambda x: x[0], reverse=True)
        
        all_text = ''
        for _, _, text, _ in reversed(blocks_to_move):
            all_text = text + '\n' + all_text
        
        for (pos, end, _, _) in blocks_to_move:
            html = html[:pos] + html[end:]
            ch_end -= (end - pos)
        
        html = html[:ch_end] + '\n                <!-- Practice & Lab Sections -->\n' + all_text.strip() + '\n' + html[ch_end:]
        changes += 1
        print("Ch{}: Moved {} block(s) to end".format(ch, len(blocks_to_move)))

print("\nChapters fixed: {}".format(changes))
if changes > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("File updated. Lines: {}".format(html.count('\n')))
