import re
c=open('cilium-test-prep.html','rb').read()
for n in range(85,88):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<88 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be].decode('utf-8',errors='replace')
    bad=[]
    for req in ['scenario-block','sc-header','sc-badge','error-spot','debug-find','li-check pass','li-check fail','li-num','li-finding discovery','li-finding root-cause','sc-resolution','sc-answer-toggle','tenet-flow','BEFORE fix','AFTER Fix','cmd-output']:
        if req not in chunk: bad.append(req)
    print(f'S{n}: {"CLEAN" if not bad else "MISSING: "+",".join(bad)}')
blocks=re.findall(rb'id="sc-s(\d+)"',c)
print(f'Total: {len(blocks)}')
