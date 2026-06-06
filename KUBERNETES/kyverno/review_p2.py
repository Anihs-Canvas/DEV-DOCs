"""Cross-check Part 2 txt vs HTML"""
html = open('k8s-cluster-structure.html', 'r', encoding='utf-8').read()
txt = open('k8s-cluster-structure.txt', 'r', encoding='utf-8').read()

# Extract Part 2 from both
txt_p2 = txt.split('PART 2:')[1].split('PART 3:')[0] if 'PART 3:' in txt.split('PART 2:')[1] else txt.split('PART 2:')[1]
html_p2 = html.split('id="part-2"')[1].split('id="part-3"')[0]

# Key directories from txt that MUST be in HTML
key_dirs = [
    '/etc/kubernetes/manifests/',
    '/etc/kubernetes/pki/',
    '/etc/kubernetes/pki/etcd/',
    '/etc/systemd/system/kubelet.service.d/',
    '/etc/containerd/config.toml',
    '/etc/cni/net.d/',
    '/var/lib/kubelet/config.yaml',
    '/var/lib/etcd/member/',
    '/var/lib/etcd/member/snap/db',
    '/var/lib/etcd/member/wal/',
    '/var/lib/kube-proxy/',
    '/var/lib/containerd/',
    '/var/log/pods/',
    '/var/log/containers/',
    '/var/log/kubernetes/audit/',
    '/run/containerd.sock',
    '/run/kubelet/',
    '/opt/cni/bin/',
    '/opt/anihpj/',
    'kubeadm-flags.env',
    'kubelet-server-current.pem',
    'kube-api-access-xxxxx',
    'admin.conf',
    'kubelet.conf',
    'controller-manager.conf',
    'scheduler.conf',
    'audit-policy.yaml',
    'encryption-config.yaml',
    'kubeadm-config.yaml',
    '10-kubeadm.conf',
    '10-calico.conflist',
    'calico',
    'calico-ipam',
    'bandwidth',
    'portmap',
    'loopback',
    'host-local',
    'containerd-stress.sock',
    'ca.crt',
    'ca.key',
    'apiserver.crt',
    'sa.pub',
    'sa.key',
    'front-proxy-ca.crt',
    'healthcheck-client.crt',
    'apiserver-etcd-client.crt',
    'peer.crt',
    'server.crt',
]

print('=== Part 2 TXT → HTML Cross-Check ===')
missing = []
for d in key_dirs:
    if d in html_p2:
        print(f'  ✓ {d}')
    else:
        print(f'  ✗ MISSING: {d}')
        missing.append(d)

print(f'\nTotal: {len(key_dirs) - len(missing)}/{len(key_dirs)} present, {len(missing)} missing')

# Check structural elements
print(f'\n=== HTML Rich Content ===')
print(f'  Tables: {html_p2.count("<table>")}')
print(f'  ASCII blocks: {html_p2.count("ascii-block")}')
print(f'  Info boxes: {html_p2.count("class=\"info\"")}')
print(f'  Highlight boxes: {html_p2.count("highlight-box")}')
print(f'  Diagram boxes: {html_p2.count("diagram-box")}')
print(f'  Sub-section anchors: part-2-1={("part-2-1" in html_p2)}, part-2-2={("part-2-2" in html_p2)}')
