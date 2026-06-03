import re
c=open('cilium-test-prep.html','rb').read()
for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be].decode('utf-8',errors='replace')
    bad=[]
    for req in ['scenario-block','sc-header','sc-badge','error-spot','debug-find','li-check pass','li-check fail','li-num','li-finding discovery','li-finding root-cause','sc-resolution','sc-answer-toggle','tenet-flow','BEFORE fix','AFTER Fix','cmd-output']:
        if req not in chunk: bad.append(req)
    print(f'S{n}: {"CLEAN" if not bad else "MISSING: "+",".join(bad)}')
blocks=re.findall(rb'id="sc-s(\d+)"',c)
nums=sorted(int(b) for b in blocks)
print(f'\nTotal: {len(nums)} (S{nums[0]}-S{nums[-1]})')
print(f'Cat1:{sum(1 for x in nums if 1<=x<=20)} Cat2:{sum(1 for x in nums if 21<=x<=38)} Cat3:{sum(1 for x in nums if 39<=x<=54)} Cat4:{sum(1 for x in nums if 55<=x<=64)} Cat5:{sum(1 for x in nums if 65<=x<=74)} Cat6:{sum(1 for x in nums if 75<=x<=84)} Cat7:{sum(1 for x in nums if 85<=x<=94)}')
