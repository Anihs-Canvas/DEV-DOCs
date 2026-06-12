import re
c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()
m=re.search(r'<h4>Chapter 6 .*? LFCS Practice Questions</h4>(.*?)<h4>Chapter 7', c, re.DOTALL)
block=m.group(1)
exps=re.findall(r'<div class="eq-explanation">\s*<div class="eq-exp-label">.*?</div>\s*<p>(.*?)</p>', block, re.DOTALL)
for i,e in enumerate(exps[:5]):
    print(f'--- Q{i+1} ---')
    print(e[:250])
    print()
