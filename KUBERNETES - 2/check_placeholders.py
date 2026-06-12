c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()
print('Placeholders remaining:', c.count('Content will be added in the next phase'))
for sec in ['master-summary','exam-strategy','new-topics-2026','port-analogy','exam-quick-ref','last-minute-review']:
    idx=c.find('id="'+sec+'"')
    if idx>0:
        snippet=c[idx:idx+250]
        has_ph='Content will be added' in snippet
        print(f'{sec}: {"PLACEHOLDER" if has_ph else "CONTENT"}')
    else:
        print(f'{sec}: MISSING')
