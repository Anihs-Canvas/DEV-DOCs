import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

fixes = 0

# Process chapters 20 down to 2
for ch in range(20, 1, -1):
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos < 0:
        continue
    
    div_start = html.rfind('<div', 0, pos)
    if div_start < 0:
        continue
    
    between = html[div_start:pos]
    
    if '<!-- Practice & Lab Sections -->' not in between:
        continue
    
    # Extract Q&A content from broken tag
    prac_pos = html.find('<!-- Practice & Lab Sections -->', div_start)
    end_div = html.rfind('</div>', 0, pos)
    
    qa_content = html[prac_pos:end_div].strip()
    
    # Remove Q&A from broken tag + fix the tag
    html = html[:prac_pos] + html[pos:]
    fixes += 1
    
    # Find previous chapter's end to insert Q&A there
    prev_cid = 'id="ch{}"'.format(ch-1)
    prev_pos = html.find(prev_cid)
    if prev_pos < 0:
        continue
    
    next_cid = 'id="ch{}"'.format(ch)
    next_pos = html.find(next_cid)
    if next_pos < 0:
        next_pos = html.find('id="appendix-a"')
    
    if next_pos > prev_pos:
        # Find the <div that starts the next chapter
        next_div = html.rfind('<div', prev_pos, next_pos)
        if next_div > prev_pos:
            # Find the last </div> before next_div
            last_close = html.rfind('</div>', prev_pos, next_div)
            if last_close > prev_pos:
                html = html[:last_close] + '\n                ' + qa_content + '\n            ' + html[last_close:]
                print("Ch{}: Fixed + moved Q&A to Ch{}".format(ch, ch-1))
            else:
                print("Ch{}: Fixed but no insertion point".format(ch))

print("\nFixed {} chapter divs".format(fixes))

# Verify
all_ok = True
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos < 0:
        print("Ch{}: NOT FOUND".format(ch))
        all_ok = False
        continue
    div_start = html.rfind('<div', 0, pos)
    between = html[div_start:pos]
    if '<!-- Practice & Lab Sections -->' in between:
        print("Ch{}: Still broken".format(ch))
        all_ok = False

# Section ordering
print("\n--- Section Ordering ---")
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 20 else 'id="appendix-a"'
    ch_start = html.find(cid)
    ch_end = html.find(ncid, ch_start+1) if ch_start >= 0 else -1
    if ch_start >= 0 and ch_end > 0:
        chapter = html[ch_start:ch_end]
        markers = ['class="cka-exam-questions"', 'class="ckad-practice-drill"',
                   'class="chapter-intro"', 'class="learning-objectives"', 
                   'class="section-block"', 'class="visual-summary"',
                   'class="key-takeaways"', 'class="diagram-container"',
                   'class="terminal-block"', 'class="split-panel"',
                   'class="compare-table"', 'class="summary-hero"',
                   'class="ckad-gotcha"', 'class="ckad-exam-tip"',
                   'class="code-block-wrapper"', 'class="stat-bar-group"']
        positions = [(chapter.find(m), m) for m in markers if chapter.find(m) >= 0]
        positions.sort()
        if positions:
            last = positions[-1][1].replace('class="','').replace('"','')
            ok = last in ('cka-exam-questions', 'ckad-practice-drill')
            if not ok:
                print("Ch{:2d} ✗ Last: {}".format(ch, last))
                all_ok = False

if all_ok:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nAll checks passed! Saved. Lines: {}".format(html.count('\n')))
