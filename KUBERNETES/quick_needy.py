import re
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8') as f:
    c = f.read()
pat = r'<div class="exam-question-item">.*?</details>'
blocks = [(c[:m.start()].count('\n')+1, m.group()) for m in re.finditer(pat, c, re.DOTALL)]
for ln,b in blocks:
    if '<pre>' not in b and '<div class="eq-explanation">' in b:
        qm = re.search(r'<span class="eq-number">([^<]+)</span>',b)
        qm2 = re.search(r'<div class="eq-question">(.+?)</div>',b)
        q = qm.group(1) if qm else '?'
        t = qm2.group(1)[:80] if qm2 else '?'
        print(f'{ln}:{q}:{t}')
