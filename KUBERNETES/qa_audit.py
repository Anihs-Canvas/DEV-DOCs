import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html', 'r', encoding='utf-8').read()

# Count Q&As per chapter
for ch in range(1, 22):
    cid = 'id="ch{}"'.format(ch)
    ncid = 'id="ch{}"'.format(ch+1) if ch < 21 else ('id="ch22"' if ch == 21 else 'id="appendix-a"')
    ch_start = html.find(cid)
    if ch_start < 0:
        continue
    # Find next id
    if ch == 21:
        npos = html.find('id="appendix-a"', ch_start+1)
    else:
        npos = html.find(ncid, ch_start+1)
    if npos < 0:
        continue
    chapter = html[ch_start:npos]
    qas = len(re.findall(r'class="exam-question-item"', chapter))
    generic = chapter.count('This is a key Helm certification concept')
    real_exps = len(re.findall(r'class="eq-explanation">.*?<span class="eq-exp-label">Explanation</span>\s*<p>(?!This is a key Helm)', chapter, re.DOTALL))
    if qas > 0:
        print("Ch{:2d}: {:2d} Q&As, {:2d} generic expl, {:2d} real expl".format(ch, qas, generic, real_exps))

# Total
total_qas = len(re.findall(r'class="exam-question-item"', html))
total_generic = html.count('This is a key Helm certification concept')
print("\nTotal Q&As: {}, Generic boilerplates: {}".format(total_qas, total_generic))
