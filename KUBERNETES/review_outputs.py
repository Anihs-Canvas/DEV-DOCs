import re, os
os.chdir(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES')
with open('cka_test_prep.html','r',encoding='utf-8') as f: h=f.read()
for s in range(1,11):
    said=f'sc-sa{s}'
    pat=rf'<div class="sc-answer" id="{said}">(.*?)</div>\s*\n\s*<div class="sc-step">'
    m=re.search(pat,h,re.DOTALL)
    if not m:
        pat=rf'<div class="sc-answer" id="{said}">(.*?)</div>\s*\n\s*<!-- STEP'
        m=re.search(pat,h,re.DOTALL)
    if not m: print(f'S{s}: NOT FOUND'); continue
    content=m.group(1)
    blocks=re.findall(r'<div class="cmd-output">(.*?)</div>',content,re.DOTALL)
    print(f'S{s}: {len(blocks)} blocks')
    for i,b in enumerate(blocks):
        pm=re.search(r'<span class="prompt">.*?</span>\s*(.*?)(?:<span class="output">|$)',b,re.DOTALL)
        om=re.search(r'<span class="output">(.*?)</span>',b,re.DOTALL)
        cmd=pm.group(1).strip()[:90] if pm else '???'
        out=om.group(1).strip()[:180].replace('\n','|') if om else 'NO OUTPUT'
        flag=''
        if '...' in out and 'pg_commit' not in out and 'total' not in out: flag+=' [ELLIPSIS]'
        if not om: flag+=' [NO_OUT]'
        print(f'  [{i+1}] {cmd[:80]}')
        print(f'       {out[:160]}{flag}')
    print()
