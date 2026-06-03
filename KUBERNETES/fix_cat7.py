"""Fix Cat7 indentation and code headers"""
c=open('cilium-test-prep.html','rb').read()

fh={
    85:'inspect BPF programs with sudo bpftool',
    86:'upgrade kernel to 5.10+ for verifier support',
    87:'use cilium-dbg to decode policy map entries',
    88:'increase BPF map sizes via ConfigMap',
    89:'clear stale TC qdisc and restart endpoint',
    90:'upgrade kernel to enable bpf_redirect_neigh',
    91:'enable BTF or use pre-compiled BPF templates',
    92:'regenerate BTF or disable CO-RE',
    93:'mount bpffs and create systemd unit',
    94:'disable per-packet events and optimize maps',
}

for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    
    # Fix indentation
    chunk=chunk.replace(b'</div>\r\n<div class="lookat-item">',b'</div>\r\n                    <div class="lookat-item">')
    chunk=chunk.replace(b'</div>\n<div class="lookat-item">',b'</div>\n                    <div class="lookat-item">')
    
    # Fix code header
    grad=chunk.find(b'linear-gradient(135deg, #d2991d, #3fb950)')
    if grad>0:
        old=b'<span class="code-lang">BASH - apply the fix</span>'
        new=f'<span class="code-lang">BASH - {fh[n]}</span>'.encode()
        before=chunk[:grad]
        after=chunk[grad:]
        after=after.replace(old, new, 1)
        chunk=before+after
    
    c=c[:bs]+chunk+c[be:]
    print(f'S{n}: FIXED')

open('cilium-test-prep.html','wb').write(c)
print(f'\nDone! {len(c):,} bytes')
