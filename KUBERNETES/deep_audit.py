import re
c=open('cilium-test-prep.html','rb').read()

# Get S1 and S85 chunks
s1s=c.find(b'id="sc-s1"')-30
s2s=c.find(b'id="sc-s2"')
s85s=c.find(b'id="sc-s85"')-30
s86s=c.find(b'id="sc-s86"')
s1=c[s1s:s2s].decode('utf-8',errors='replace')
s85=c[s85s:s86s].decode('utf-8',errors='replace')

print("=== S1 vs S85 DEEP COMPARISON ===")
print()

# Compare div structure count
s1_divs=len(re.findall(r'<div\b', s1))
s85_divs=len(re.findall(r'<div\b', s85))
print(f"Div count: S1={s1_divs}, S85={s85_divs}")

# Check element order and count
checks = {
    'scenario-block': (s1.count('scenario-block'), s85.count('scenario-block')),
    'sc-header': (s1.count('sc-header'), s85.count('sc-header')),
    'sc-step': (s1.count('sc-step'), s85.count('sc-step')),
    'lookat-item': (s1.count('lookat-item'), s85.count('lookat-item')),
    'li-check pass': (s1.count('li-check pass'), s85.count('li-check pass')),
    'li-check fail': (s1.count('li-check fail'), s85.count('li-check fail')),
    'li-num': (s1.count('li-num'), s85.count('li-num')),
    'li-finding discovery': (s1.count('li-finding discovery'), s85.count('li-finding discovery')),
    'li-finding root-cause': (s1.count('li-finding root-cause'), s85.count('li-finding root-cause')),
    'tenet-step': (s1.count('tenet-step'), s85.count('tenet-step')),
    'cmd-output': (s1.count('cmd-output'), s85.count('cmd-output')),
    'copy-btn': (s1.count('copy-btn'), s85.count('copy-btn')),
    'sc-answer-toggle': (s1.count('sc-answer-toggle'), s85.count('sc-answer-toggle')),
}

for name, (s1c, s85c) in checks.items():
    flag = '✅' if s1c == s85c else f'⚠️ S1={s1c}/S85={s85c}'
    print(f"  {name:30s}: {flag}")

# Check indentation in error-spot
def count_indent(chunk, section):
    es=chunk.find('error-spot')
    df=chunk.find('debug-find', es)
    es_s=chunk[es:df]
    total=es_s.count('<div class="lookat-item">')
    proper=es_s.count('\n                    <div class="lookat-item">')
    return total, proper

s1_t, s1_p = count_indent(s1, 'error-spot')
s85_t, s85_p = count_indent(s85, 'error-spot')
print(f"\n  error-spot indent: S1={s1_p}/{s1_t-1}, S85={s85_p}/{s85_t-1}")

# Check verify h4 length
vh1=re.search(r'<h4>✅ Verify — .+?</h4>', s1)
vh85=re.search(r'<h4>✅ Verify — .+?</h4>', s85)
if vh1 and vh85:
    print(f"  Verify h4: S1={len(vh1.group())}c, S85={len(vh85.group())}c")

# Check code headers
ch1=re.findall(r'<span class="code-lang">(.+?)</span>', s1)
ch85=re.findall(r'<span class="code-lang">(.+?)</span>', s85)
print(f"\n  Code headers S1: {ch1[:3]}")
print(f"  Code headers S85: {ch85[:3]}")

# Check ALL Cat7 scenarios for indentation
print("\n=== INDENTATION AUDIT (S85-S94) ===")
for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    
    # Error-spot indentation
    es=chunk.find(b'error-spot')
    df=chunk.find(b'debug-find', es)
    es_bytes=chunk[es:df]
    es_total=es_bytes.count(b'<div class=\"lookat-item\">')
    es_proper=es_bytes.count(b'\n                    <div class=\"lookat-item\">')
    
    # Debug-find indentation
    df_end=chunk.find(b'</div>\n', df+100)
    df_bytes=chunk[df:df+4000]
    df_total=df_bytes.count(b'<div class=\"lookat-item\">')
    df_proper=df_bytes.count(b'\n                    <div class=\"lookat-item\">')
    
    # Check code headers
    ch=re.findall(rb'<span class="code-lang">(.+?)</span>', chunk)
    fix_header=ch[1].decode('utf-8',errors='replace') if len(ch)>1 else 'MISSING'
    
    es_ok=es_proper>=es_total-1
    df_ok=df_proper>=df_total-1
    hdr_ok='BASH - apply the fix' not in fix_header
    
    flags=[]
    if not es_ok: flags.append(f'es-indent:{es_proper}/{es_total-1}')
    if not df_ok: flags.append(f'df-indent:{df_proper}/{df_total-1}')
    if not hdr_ok: flags.append('generic fix header')
    
    print(f'S{n}: {"CLEAN" if not flags else "; ".join(flags)}')
