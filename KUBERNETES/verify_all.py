filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# Check all chapter div tags are well-formed
import re

# Find all chapter opening patterns
# Good: <div id="chN">
# Bad:  <div \n...stuff...\nid="chN">  or  <div \n...stuff...\n</div>\nid="chN">

issues = []
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos < 0:
        issues.append("Ch{}: id='ch{}' NOT FOUND".format(ch, ch))
        continue
    
    # Check what's between the nearest <div before this id and the id
    div_start = html.rfind('<div', 0, pos)
    between = html[div_start:pos+len(cid)]
    
    # A well-formed tag should have <div...id="chN"> with no content between <div and id=
    # Check if there's > between <div and id=
    gt_pos = between.find('>')
    if gt_pos >= 0 and between.find('id="ch') > gt_pos:
        issues.append("Ch{}: '>' found BEFORE id= in opening tag".format(ch))
    
    # Check for <!-- or other content between <div and id=
    if '<!--' in between[:between.find('id="ch')]:
        issues.append("Ch{}: Comment found between <div and id=".format(ch))

# Also check for orphaned id= that aren't inside <div ... >
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    pos = html.find(cid)
    if pos > 0:
        # Check preceding context
        pre = html[max(0,pos-30):pos]
        if not pre.strip().endswith('<div'):
            if '<div' not in pre:
                issues.append("Ch{}: id= not preceded by <div".format(ch))

if issues:
    for i in issues:
        print(i)
    print("\n{} issues found".format(len(issues)))
else:
    print("All 20 chapter div tags are well-formed!")

# Also check Q&A position in each chapter
print("\n--- Section Ordering Check ---")
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 20 else 'id="appendix-a"'
    
    ch_start = html.find(cid)
    ch_end = html.find(ncid, ch_start + 1) if ch_start >= 0 else -1
    
    if ch_start >= 0 and ch_end > 0:
        chapter = html[ch_start:ch_end]
        markers = [
            'class="chapter-intro"', 'class="learning-objectives"', 'class="section-block"',
            'class="visual-summary"', 'class="key-takeaways"', 'class="diagram-container"',
            'class="terminal-block"', 'class="split-panel"', 'class="compare-table"',
            'class="card-grid"', 'class="process-steps"', 'class="summary-hero"',
            'class="ckad-gotcha"', 'class="ckad-exam-tip"', 'class="cka-chapter-relevance"',
            'class="code-block-wrapper"', 'class="stat-bar-group"', 'class="ba-comparison"',
            'class="cka-exam-questions"', 'class="ckad-practice-drill"'
        ]
        positions = [(chapter.find(m), m) for m in markers if chapter.find(m) >= 0]
        positions.sort()
        if positions:
            last = positions[-1][1].replace('class="','').replace('"','')
            is_ok = last in ('cka-exam-questions', 'ckad-practice-drill')
            if not is_ok:
                print("Ch{:2d} ✗ Last: {}".format(ch, last))
