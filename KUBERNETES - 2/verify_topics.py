import re
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()
for ch in [1,6,15,27,40,45]:
    m = re.search(rf'<h4>Chapter {ch} .*? LFCS Practice Questions</h4>(.*?)(?:<h4>Chapter|$)', c, re.DOTALL)
    if m:
        topics = re.findall(r'eq-explanation.*?<p><strong>(.*?)</strong>', m.group(1), re.DOTALL)
        if topics: print(f'Ch {ch:2d}: {topics[0][:60]}')
print(f'File: {len(c)//1024} KB | Qs: {c.count("exam-question-item")} | Generic: {c.count("Understanding this concept is critical")}')
print(f'ch1: {"id=\"ch1\"" in c} | ch45: {"id=\"ch45\"" in c}')
