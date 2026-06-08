import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern: <div \n<spaces><!-- Practice & Lab Sections -->\n...any content...\n<spaces></div>\nid="chN">
# We need to match across the broken tag and fix it

pattern = re.compile(
    r'(<div )\n( +)<!-- Practice & Lab Sections -->\n'
    r'(.*?)'  # Q&A content (non-greedy)
    r'\n\2</div>\n'
    r'(id="ch\d+">)',
    re.DOTALL
)

matches = list(pattern.finditer(html))
print("Found {} broken chapter divs".format(len(matches)))

# Process in reverse to preserve positions
for m in reversed(matches):
    # Full broken tag
    broken = m.group(0)
    # Proper tag
    fixed = '<div ' + m.group(4)  # <div id="chN">
    
    html = html[:m.start()] + fixed + html[m.end():]

print("Fixed {} tags".format(len(matches)))

# Verify
issues = 0
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos < 0:
        print("Ch{}: NOT FOUND".format(ch))
        issues += 1
        continue
    # Check well-formed: <div...id="chN"> should have no > before id=
    div_start = html.rfind('<div', max(0, pos-200), pos)
    if div_start < 0:
        print("Ch{}: No <div before id=".format(ch))
        issues += 1
        continue
    between = html[div_start:pos]
    gt = between.find('>')
    if gt >= 0 and between.find('id="ch') > gt:
        print("Ch{}: > before id=".format(ch))
        issues += 1

if issues == 0:
    print("All chapter divs well-formed!")
    
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
                    issues += 1

if issues == 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nAll checks passed! Saved. Lines: {}".format(html.count('\n')))
else:
    print("\n{} issues remaining".format(issues))
