# -*- coding: utf-8 -*-
import re, os

with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

# STEP 1: Inject 15 Decision Trees before PART 3
with open('tmp_decision_trees.html', 'r', encoding='utf-8') as f:
    trees = f.read()

part3_marker = '    <!-- \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n         PART 3: SCENARIOS \u2014 CONTENT GOES HERE'
c = c.replace(part3_marker, trees + '\n' + part3_marker)

# STEP 2: Add "What to Look At" to each ts-issue
lookat_data = {}

lookat_data['ts-a1-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> <code>cilium endpoint list</code> output -- state must be "ready". Check <code>ip link show lxc_*</code> for veth pairs. <code>cilium-dbg bpf policy get &lt;id&gt;</code> shows if BPF programs are attached. Note: same-node failures are the rarest Cilium issue -- usually a recent CNI change.'

lookat_data['ts-a2-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> <code>ip link show cilium_vxlan</code> -- interface MUST be UP. Cloud security groups MUST allow UDP 8472 (VXLAN) or 6081 (Geneve) between ALL worker nodes. MTU: if using VXLAN, packets > 1450 bytes get fragmented. <code>cilium-health status</code> is the fastest cross-node check.'

lookat_data['ts-a3-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> <code>cilium-dbg bpf ct list global | wc -l</code> -- conntrack > 100k on a node is a red flag. Default GC interval is 5 min (too slow for high-churn). <code>cilium-dbg monitor --type drop</code> shows retransmissions. Envoy proxy at :9090/metrics for L7 latency.'

lookat_data['ts-a4-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> CiliumNetworkPolicy + Kubernetes NetworkPolicy use UNION semantics -- a KNP ALLOW + CNP DENY = ALLOW. <code>cilium policy trace</code> ALWAYS shows the truth. Namespace labels are NOT set by default. Check BOTH namespaces for default-deny policies.'

lookat_data['ts-a5-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> WireGuard uses UDP port 51871 by default. Kernel module <code>wireguard</code> must be loaded on ALL nodes. MTU for VXLAN+WireGuard: 1400 (1500 - 50 VXLAN - 60 WG). <code>cilium-dbg encrypt status</code> shows per-node key state. One-way encryption = missing key on one side.'

lookat_data['ts-a6-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> <code>kubectl get endpoints</code> is the single most important command -- empty endpoints = selector mismatch. Service selector matches pod LABELS (from template), NOT deployment name. BPF service map: <code>cilium-dbg service list</code>. KPR mode matters: Partial may use iptables.'

lookat_data['ts-a7-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> DNS is ALWAYS UDP port 53 first, TCP/53 only for large responses. Default-deny policy MUST include DNS allow rule FIRST. Pod /etc/resolv.conf should point to <code>10.96.0.10</code> (CoreDNS ClusterIP). Cross-namespace resolution REQUIRES FQDN.'

lookat_data['ts-a8-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> KPR MUST be "Strict" for full NodePort (not "Partial"). <code>externalTrafficPolicy: Local</code> drops traffic if receiving node has NO local backend. Cloud NLB health checks: use TCP on NodePort. NodePort range: 30000-32767 only.'

lookat_data['ts-a9-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Health endpoint is a CANARY -- if unhealthy, cross-node pod traffic is also broken. <code>cilium-health status</code> runs ICMP pings between all nodes. Health IP CIDR must NOT overlap with pod CIDR. ICMP must be allowed between worker nodes.'

lookat_data['ts-a10-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Cilium agent does NOT hot-reload ConfigMap -- restart REQUIRED. Helm values override ConfigMap on every upgrade. ConfigMap keys use kebab-case: <code>enable-hubble</code> NOT <code>enableHubble</code>. Agent CLI args take PRECEDENCE over ConfigMap.'

lookat_data['ts-a11-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Cilium Operator is a SINGLE POINT OF FAILURE for identity allocation. Always run 2+ replicas. <code>cilium identity list | wc -l</code> -- max 65535 identities. CRDs must exist: <code>kubectl get crd | grep cilium</code>. RBAC: agent needs create/update on CiliumIdentity.'

lookat_data['ts-a12-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Identity is derived from pod LABELS at creation time -- labels changed later do NOT update identity. Pods with identical security-relevant labels SHARE an identity. Reserved identities 1-255 are special (1=world, 2=cluster). Add <code>component: api</code> label.'

lookat_data['ts-a13-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Default identity GC interval: 15 minutes. If pods have 15min+ idle periods, their identity may be GC\'d. Operator heartbeat tracks identity usage -- network blips cause missed heartbeats. NEVER manually delete CiliumIdentity CRDs while pods are running.'

lookat_data['ts-a14-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> No CEP = CNI plugin was never called. Check init container logs for CNI conflist copy errors. <code>/etc/cni/net.d/05-cilium.conflist</code> must exist. Agent needs RBAC to create CiliumEndpoint in ALL namespaces. CNI ADD timeout is 30s.'

lookat_data['ts-a15-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> CES (CiliumEndpointSlice) batches CRD writes -- without it, every endpoint is a separate kube-apiserver call. Default: 100 endpoints per slice. CES requires Kubernetes 1.21+. If apiserver is slow, CES sync degrades.'

lookat_data['ts-a16-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> ALWAYS check <code>kubectl logs --previous</code> first -- crash reason in last 20 lines. Kernel 5.10+ REQUIRED. <code>bpftool prog list</code> shows leftover BPF programs. <code>mount | grep bpf</code> -- bpffs must be mounted at /sys/fs/bpf. iptables leftovers are #1 crash cause.'

lookat_data['ts-a17-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> OOMKilled = exit code 137. Conntrack table is the #1 memory consumer. Default 512Mi limit is too low for production with Hubble. Each BPF conntrack entry ~200 bytes in kernel + mirror. Connection-per-request apps explode conntrack.'

lookat_data['ts-a18-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Cilium agent needs EXTENSIVE RBAC -- ClusterRole covers 20+ API groups. Agent uses hostNetwork: true -- check NODE-level connectivity. Private EKS/GKE API endpoints need worker node subnet access. SA token must be mounted at /var/run/secrets.'

lookat_data['ts-a19-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Endpoint restore after agent restart: normal to take 2-3 min for 100+ pods. Stuck restore = state inconsistency between CRD and BPF maps. <code>ip link show | grep lxc</code> -- orphaned veth pairs. First pod on new node takes 30-60s.'

lookat_data['ts-a20-detail'] = '<strong>🔍 What to Look At / Take Note Of:</strong> Default cluster-pool: /24 per node = 256 IPs. Sidecar containers consume IPs too. Stale CEP CRDs hold IPs after pod deletion. AWS ENI mode: limited by ENI attachments per instance. Azure: limited by NIC IPs per VM. <code>cilium status | grep IPAM</code> shows % used.'

# Insert .ts-lookat blocks
for issue_id, lookat_text in lookat_data.items():
    issue_start = c.find('id="' + issue_id + '"')
    if issue_start < 0:
        print('WARNING: ' + issue_id + ' not found!')
        continue
    sol_pos = c.find('<div class="ts-solution">', issue_start)
    if sol_pos < 0:
        print('WARNING: ts-solution not found in ' + issue_id + '!')
        continue
    lookat_block = '\n        <div class="ts-lookat">' + lookat_text + '</div>\n        '
    c = c[:sol_pos] + lookat_block + c[sol_pos:]

# STEP 3: Add CSS for .ts-lookat
old_adv_end = '.ts-advice { font-size: 15px; color: var(--text-secondary); line-height: 1.7; font-style: italic; }'
new_lookat_css = '''.ts-lookat { margin: 12px 24px 0 24px; padding: 14px 18px; background: linear-gradient(135deg, rgba(210,153,29,0.05) 0%, rgba(210,153,29,0.01) 100%); border: 1px solid rgba(210,153,29,0.2); border-radius: 10px; font-size: 14px; color: var(--text-secondary); line-height: 1.7; position: relative; }
        .ts-lookat strong { color: var(--accent-orange); font-size: 14px; }
        .ts-advice { font-size: 15px; color: var(--text-secondary); line-height: 1.7; font-style: italic; }'''
c = c.replace(old_adv_end, new_lookat_css)

# STEP 4: Enhance decision-tree CSS
c = c.replace(
    '.decision-tree { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-bottom: 16px; overflow-x: auto; }',
    '.decision-tree { background: linear-gradient(145deg, #1a1f2b 0%, #161b22 100%); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px; margin-bottom: 20px; overflow-x: auto; box-shadow: var(--shadow); transition: var(--transition); position: relative; }\n        .decision-tree:hover { border-color: rgba(88,166,255,0.3); box-shadow: var(--shadow-glow); }\n        .decision-tree pre { font-family: \'JetBrains Mono\', \'Fira Code\', \'Consolas\', monospace; font-size: 12px; line-height: 1.35; color: var(--text); }'
)
c = c.replace(
    '.decision-tree h4 { color: var(--accent); margin-bottom: 12px; }',
    '.decision-tree h4 { color: var(--accent); margin-bottom: 14px; font-size: 16px; display: flex; align-items: center; gap: 6px; }'
)

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print('Done. Size: ' + str(sz) + ' KB')
print('</main>: ' + str(c.count('</main>')))
print('decision-tree: ' + str(c.count('decision-tree')))
print('ts-lookat: ' + str(c.count('ts-lookat')))

os.remove('tmp_decision_trees.html')
