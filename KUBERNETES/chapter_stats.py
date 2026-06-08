import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

print("=== Current Chapter Sizes ===\n")
for ch in range(1, 21):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 20 else 'id="appendix-a"'
    ch_start = html.find(cid)
    ch_end = html.find(ncid, ch_start+1) if ch_start >= 0 else -1
    if ch_start >= 0 and ch_end > 0:
        chapter = html[ch_start:ch_end]
        lines = chapter.count('\n')
        # Count sections
        sections = len(re.findall(r'class="(?:section-block|chapter-intro|learning-objectives|visual-summary|key-takeaways|diagram-container|terminal-block|split-panel|compare-table|card-grid|process-steps|summary-hero|ckad-gotcha|ckad-exam-tip|cka-chapter-relevance|code-block-wrapper|stat-bar-group|ba-comparison|cka-exam-questions|ckad-practice-drill)"', chapter))
        qas = len(re.findall(r'class="exam-question-item"', chapter))
        drills = len(re.findall(r'class="ckad-practice-drill"', chapter))
        print("Ch{:2d}: {:4d} lines, {:2d} sections, {:2d} Q&As, {:1d} drills".format(ch, lines, sections, qas, drills))

# Also check appendices
for app in ['a','b','c','d','e','f']:
    aid = 'id="appendix-{}"'.format(app)
    naid = 'id="appendix-{}"'.format(chr(ord(app)+1)) if app < 'f' else 'id="footer"'
    if naid == 'id="footer"' or html.find(naid) < 0:
        # find next appendix or end
        nexts = [html.find('id="appendix-{}"'.format(chr(ord(app)+1)))]
        nexts = [x for x in nexts if x > 0]
        naid_pos = min(nexts) if nexts else len(html)
    else:
        naid_pos = html.find(naid)
    
    app_start = html.find(aid)
    app_end = naid_pos if isinstance(naid_pos, int) else html.find(naid)
    if app_start >= 0 and app_end > app_start:
        alines = html[app_start:app_end].count('\n')
        print("App{}: {:4d} lines".format(app.upper(), alines))

print("\nTotal file: {} lines".format(html.count('\n')))
