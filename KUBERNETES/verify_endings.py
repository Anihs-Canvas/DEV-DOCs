import re

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# For each chapter, find the last 3 significant sections before chapter close
for ch in range(1, 22):
    cid = 'id="ch{}"'.format(ch)
    if ch < 20:
        ncid = 'id="ch{}"'.format(ch+1)
    elif ch == 20:
        ncid = 'id="ch21"'
    else:
        ncid = 'id="appendix-a"'
    
    ch_start = html.find(cid)
    if ch_start < 0:
        continue
    
    ch_end = html.find(ncid, ch_start + 1)
    if ch_end < 0:
        continue
    
    chapter = html[ch_start:ch_end]
    
    # Find all section markers
    section_markers = [
        'class="chapter-intro"', 'class="learning-objectives"', 'class="section-block"',
        'class="visual-summary"', 'class="key-takeaways"', 'class="diagram-container"',
        'class="terminal-block"', 'class="split-panel"', 'class="compare-table"',
        'class="card-grid"', 'class="process-steps"', 'class="summary-hero"',
        'class="ckad-gotcha"', 'class="ckad-exam-tip"', 'class="cka-chapter-relevance"',
        'class="code-block-wrapper"', 'class="stat-bar-group"', 'class="ba-comparison"',
        'class="cka-exam-questions"', 'class="ckad-practice-drill"'
    ]
    
    positions = []
    for marker in section_markers:
        pos = chapter.find(marker)
        if pos >= 0:
            positions.append((pos, marker))
    
    positions.sort()
    
    # Show last 3 sections
    last_3 = positions[-3:] if len(positions) >= 3 else positions
    labels = [p[1].replace('class="','').replace('"','') for p in last_3]
    is_ok = 'cka-exam-questions' in labels[-1] or 'ckad-practice-drill' in labels[-1]
    status = '✓' if is_ok else '✗ LAST IS ' + labels[-1]
    print("Ch{:2d} {} | Last 3: {}".format(ch, status, ' → '.join(labels[-3:])))
