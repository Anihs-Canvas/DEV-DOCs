c=open('cilium-test-prep.html','rb').read()
s=c.find(b'id="sc-s85"')
e=c.find(b'id="sc-s86"')
chunk=c[s:e]

# Find code headers
import re
headers=re.findall(rb'<span class="code-lang">(.+?)</span>', chunk)
for i,h in enumerate(headers):
    print(f'Header {i}: {h}')

# Find gradient position
grad=chunk.find(b'linear-gradient(135deg, #d2991d, #3fb950)')
print(f'\nGradient at byte: {grad}')

# Find 'apply the fix' positions
for m in re.finditer(rb'apply the fix', chunk):
    ctx=chunk[max(0,m.start()-30):m.end()+5]
    print(f'\n"apply the fix" at {m.start()}: ...{ctx}...')
