"""Fix Cat7 code headers using correct em dash character"""
c=open('cilium-test-prep.html','rb').read()

# Em dash in UTF-8
EM = b'\xe2\x80\x94'

fh={
    85:f'BASH {EM.decode()} inspect BPF programs with sudo bpftool',
    86:f'BASH {EM.decode()} upgrade kernel to 5.10+ for verifier support',
    87:f'BASH {EM.decode()} use cilium-dbg to decode policy map entries',
    88:f'BASH {EM.decode()} increase BPF map sizes via ConfigMap',
    89:f'BASH {EM.decode()} clear stale TC qdisc and restart endpoint',
    90:f'BASH {EM.decode()} upgrade kernel to enable bpf_redirect_neigh',
    91:f'BASH {EM.decode()} enable BTF or use pre-compiled BPF templates',
    92:f'BASH {EM.decode()} regenerate BTF or disable CO-RE',
    93:f'BASH {EM.decode()} mount bpffs and create systemd unit',
    94:f'BASH {EM.decode()} disable per-packet events and optimize maps',
}

old = b'<span class="code-lang">BASH ' + EM + b' apply the fix</span>'

for n in range(85,95):
    bs=c.find(f'id="sc-s{n}"'.encode())-30
    be=c.find(f'id="sc-s{n+1}"'.encode()) if n<95 else c.find(b'id="appendices"',bs+100)
    if be<0: be=c.find(b'id="appendices"',bs+100)
    chunk=c[bs:be]
    
    new_hdr = f'<span class="code-lang">{fh[n]}</span>'.encode()
    if old in chunk:
        chunk=chunk.replace(old, new_hdr, 1)
        c=c[:bs]+chunk+c[be:]
        print(f'S{n}: HEADER FIXED')
    else:
        print(f'S{n}: pattern not found')

open('cilium-test-prep.html','wb').write(c)
print(f'\nDone! {len(c):,} bytes')
