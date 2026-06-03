import re
c=open('cilium-test-prep.html','rb').read()

print("=== CODE HEADER CHECK (S85-S94) ===")
for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    ch=re.findall(rb'<span class="code-lang">(.+?)</span>', chunk)
    fix_hdr=ch[1].decode('utf-8',errors='replace') if len(ch)>1 else 'MISSING'
    is_ok='apply the fix' not in fix_hdr
    print(f"S{n}: {'OK' if is_ok else 'FIX'} {fix_hdr[:80]}")

# Also final quick indent check
print("\n=== INDENT CHECK (S85-S94) ===")
for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    es=chunk.find(b'error-spot'); df=chunk.find(b'debug-find',es)
    es_bytes=chunk[es:df]; t=es_bytes.count(b'<div class=\"lookat-item\">'); p=es_bytes.count(b'\n                    <div class=\"lookat-item\">')
    print(f"S{n}: es={p}/{t-1} {'OK' if p>=t-1 else 'FIX'}")
