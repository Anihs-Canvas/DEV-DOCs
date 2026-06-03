#!/usr/bin/env python3
"""Fix Cat4+Cat5 (S55-S74) error-spot indentation to match S1 reference"""
import re

with open('cilium-test-prep.html', 'rb') as f:
    c = f.read()

fix_headers = {
    65: "reinstall Cilium with EKS-specific values",
    66: "use CNI chaining or recreate cluster with network-plugin=none",
    67: "perform per-node drain migration with preserve-existing-ips",
    68: "configure proper CNI chaining with cni.customConf=true",
    69: "check MTU, DNS, kube-proxy, and firewall per-layer",
    70: "upgrade CRDs first, run pre-flight, drain nodes individually",
    71: "upgrade CRDs manually and rotate TLS certificates",
    72: "create Kubernetes TLS secret and reference certs in Helm values",
    73: "restart Cilium agents to force full CES reconciliation",
    74: "disable BBR and use EDT fallback matching kernel capabilities",
}

for n in range(55, 75):
    bs = c.find(f'id="sc-s{n}"'.encode())
    if bs < 0: continue
    bs = max(0, bs - 30)
    
    be = c.find(f'id="sc-s{n+1}"'.encode()) if n < 75 else -1
    if be < 0:
        be = c.find(b'id="appendices"', bs + 100)
    if be < 0: continue
    
    chunk = c[bs:be]
    
    # Fix error-spot AND debug-find: ensure all lookat-item divs have 20-space indent
    # Both sections share the same pattern: </div>\r\n<div class="lookat-item">
    # We need: </div>\r\n                    <div class="lookat-item">
    
    # Simple global replace within the chunk for both \r\n and \n variants
    chunk = chunk.replace(
        b'</div>\r\n<div class="lookat-item">',
        b'</div>\r\n                    <div class="lookat-item">'
    )
    chunk = chunk.replace(
        b'</div>\n<div class="lookat-item">',
        b'</div>\n                    <div class="lookat-item">'
    )
    
    # Fix generic code header in fix step
    if n in fix_headers:
        old = b'<span class="code-lang">BASH - apply the fix</span>'
        new = f'<span class="code-lang">BASH - {fix_headers[n]}</span>'.encode()
        # Only replace the one in the fix step (after the gradient)
        grad = chunk.find(b'linear-gradient(135deg, #d2991d, #3fb950)')
        if grad > 0:
            before = chunk[:grad]
            after = chunk[grad:]
            after = after.replace(old, new, 1)
            chunk = before + after
    
    c = c[:bs] + chunk + c[be:]
    print(f'S{n}: FIXED')

with open('cilium-test-prep.html', 'wb') as f:
    f.write(c)
print(f'\nDone! {len(c)} bytes')
