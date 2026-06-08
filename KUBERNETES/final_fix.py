filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Simple fix: find every "id=\"chN\">" that is NOT preceded by "<div" 
# and insert "<div " before it

# Pattern: whitespace + </div> + newline + whitespace + id="chN"> + newline + whitespace + <div class="chapter-intro">
# We want: whitespace + </div> + newline + whitespace + <div id="chN"> + newline + whitespace + <div class="chapter-intro">

fixes = 0
for ch in range(20, 1, -1):  # Reverse order
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos < 0:
        continue
    
    # Check if already has <div before it
    pre = html[max(0,pos-20):pos]
    if '<div' in pre:
        continue
    
    # Find the newline before id=
    nl_before = html.rfind('\n', 0, pos)
    if nl_before < 0:
        continue
    
    # Insert <div before the id= on the same indentation
    indent = html[nl_before+1:pos]  # whitespace before id=
    # Replace the whitespace+id= with whitespace+<div id=
    old_str = html[nl_before+1:pos+len(cid)+1]  # indent + id="chN">
    new_str = indent + '<div ' + cid + '>'
    
    html = html[:nl_before+1] + new_str + html[pos+len(cid)+1:]
    fixes += 1

print("Fixed {} orphaned id= tags".format(fixes))

# Verify
all_ok = True
for ch in range(1, 21):
    pat = r'<div\s+id="ch{}"'.format(ch)
    if not re.search(pat, html):
        print("Ch{}: STILL BROKEN".format(ch))
        all_ok = False

if all_ok:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nAll 20 chapters have well-formed <div id=\"chN\"> tags!")
    print("Lines: {}".format(html.count('\n')))
    
    # Final section ordering check
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
