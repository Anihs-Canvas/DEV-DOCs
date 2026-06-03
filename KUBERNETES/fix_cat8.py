"""Fix indentation for Cat8 (S95-S100) + apply indent + verify"""
import re
c=open('cilium-test-prep.html','rb').read()

# Fix indentation
for n in range(95,101):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<101 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    chunk=chunk.replace(b'</div>\r\n<div class="lookat-item">',b'</div>\r\n                    <div class="lookat-item">')
    chunk=chunk.replace(b'</div>\n<div class="lookat-item">',b'</div>\n                    <div class="lookat-item">')
    c=c[:bs]+chunk+c[be:]

# Audit Cat8
print("=== CAT8 AUDIT (S95-S100) ===")
for n in range(95,101):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<101 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    
    # Structure check
    s=chunk.decode('utf-8',errors='replace')
    bad=[]
    for req in ['scenario-block','sc-header','sc-badge','error-spot','debug-find','li-check pass','li-check fail','li-num','li-finding discovery','li-finding root-cause','sc-resolution','sc-answer-toggle','tenet-flow','BEFORE fix','AFTER Fix','cmd-output']:
        if req not in s: bad.append(req)
    
    # Indent check
    es=chunk.find(b'error-spot'); df=chunk.find(b'debug-find',es)
    es_bytes=chunk[es:df]; t=es_bytes.count(b'<div class=\"lookat-item\">'); p=es_bytes.count(b'\n                    <div class=\"lookat-item\">')
    if p<t-1: bad.append(f'es-indent:{p}/{t-1}')
    
    # Code header check
    ch=re.findall(rb'<span class="code-lang">(.+?)</span>', chunk)
    if len(ch)>1:
        hdr=ch[1].decode('utf-8',errors='replace')
        if 'apply the fix' in hdr: bad.append('generic fix header')
    
    print(f"S{n}: {'CLEAN' if not bad else '; '.join(bad)}")

# Count
blocks=re.findall(rb'id="sc-s(\d+)"',c)
nums=sorted(int(b) for b in blocks)
print(f'\nTotal: {len(nums)} (S{nums[0]}-S{nums[-1]})')
missing=[x for x in range(1,101) if x not in nums]
print(f'Missing: {missing if missing else "NONE"}')

open('cilium-test-prep.html','wb').write(c)
print(f'File: {len(c):,} bytes')
