with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8') as f: html=f.read()
issues=[]
for ch in range(1,21):
    cid=f'ch{ch}'
    ncid=f'ch{ch+1}' if ch<20 else 'appendix-a'
    cnt=html.count(f'id="{cid}"')
    if cnt!=1: issues.append(f'Ch{ch}: found {cnt} instances')
    idx=html.find(f'id="{cid}"')
    nidx=html.find(f'id="{ncid}"',idx+1) if idx>=0 else -1
    if idx>=0 and nidx>0:
        sec=html[idx:nidx]
        do=sec.count('<div')
        dc=sec.count('</div>')
        if do!=dc: issues.append(f'Ch{ch}: divs +{do}/-{dc} = {do-dc}')
if issues:
    for i in issues: print(i)
else:
    print('All chapters structurally sound')
print(f'File: {html.count(chr(10))} lines')
