with open('k8s-cluster-structure.txt', 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.count('\n')
print(f'Total lines: {lines}')

# Count parts
for kw in ['PART 0:', 'PART 1:', 'PART 2:', 'PART 3:', 'PART 4:', 'PART 5:', 'PART 6:', 'PART 7:', 'PART 8:', 'PART 9:']:
    count = c.count(kw)
    if count > 0:
        print(f'  {kw} found')

# Key terms
for term in ['kubeadm', 'cp-01', 'cp-02', 'cp-03', 'wk-01', 'wk-02', 'wk-03', 'wk-04', 'wk-05', 'fe-01', 'fe-02', 'etcd', 'containerd', 'kubelet', 'Calico', 'iptables', 'kubeadm init', 'kubeadm join', 'static Pod', 'Raft']:
    print(f'  "{term}": {c.count(term)}')
