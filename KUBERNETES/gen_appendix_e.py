"""Generate Appendix E: 15 Decision Tree Flowcharts for cilium-test-prep.html"""

HTML_FILE = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html'

# ── 15 Decision Trees ──
# Each: (dt_id, title, category, est_time, tree_ascii)
trees = []

# DT-1: Pod Cannot Reach Another Pod
trees.append(("dt1", "DT-1: Pod Cannot Reach Another Pod", "Architecture", "5-15 min", r"""
    START: Pod A cannot reach Pod B
    │
    ├─ Q1: Can Pod A reach ANY pod (including itself)?
    │   ├─ YES → Issue specific to Pod B or path between them
    │   │   ├─ Q2: Are Pod A and Pod B on the SAME node?
    │   │   │   ├─ YES → Check: cilium endpoint list (both present?)
    │   │   │   │   ├─ Both present → hubble observe --from-pod A --to-pod B
    │   │   │   │   │   ├─ DROPPED → Network Policy blocking → Review CNPs
    │   │   │   │   │   └─ No flows → Identity issue → Check CEP identity
    │   │   │   │   └─ B missing → kubectl describe cep -n NS B → Fix CEP
    │   │   │   └─ NO (different nodes) → Check: ip link show cilium_vxlan
    │   │   │       ├─ DOWN → Tunnel broken → Check node firewall, restart agent
    │   │   │       └─ UP → Check: ip route | grep &lt;pod-B-CIDR&gt;
    │   │   │           ├─ Route missing → Add route or check BGP config
    │   │   │           └─ Route exists → MTU issue → ping -M do -s 1400 B_IP
    │   │   └─ (DNS/Services → go to DT-2)
    │   └─ NO → Pod A has no network at all
    │       ├─ Check: kubectl describe pod A | grep -A5 Conditions
    │       │   ├─ CNI error → Check /etc/cni/net.d/ on node
    │       │   └─ PodRunning → Check: cilium endpoint list | grep A
    │       │       └─ Missing → Agent issue → kubectl logs ds/cilium on node
    │       └─ FIX: Restart Cilium agent on pod's node if endpoint missing
"""))

# DT-2: Service DNS Not Resolving
trees.append(("dt2", "DT-2: Service DNS Not Resolving", "Architecture", "5-10 min", r"""
    START: Service hostname (e.g., anihpj-api) won't resolve
    │
    ├─ Q1: Can you resolve external domains (google.com)?
    │   ├─ YES → CoreDNS is working, issue is specific to cluster domain
    │   │   ├─ Q2: Can you resolve the FQDN? (service.namespace.svc.cluster.local)
    │   │   │   ├─ YES → Short-name issue → Check pod's dnsPolicy &amp; ndots config
    │   │   │   └─ NO → Service or namespace may not exist
    │   │   │       ├─ kubectl get svc -n NAMESPACE | grep SERVICE
    │   │   │       │   ├─ Exists → Check CoreDNS configmap for stubDomain override
    │   │   │       │   └─ Missing → Service not deployed → kubectl apply service.yaml
    │   │   │       └─ FIX: Ensure service exists and namespace is correct
    │   └─ NO → CoreDNS is down or unreachable
    │       ├─ kubectl get pods -n kube-system | grep coredns
    │       │   ├─ Not running → Check CoreDNS deployment, node resources
    │       │   └─ Running → Check: hubble observe --to-port 53 --verdict DROPPED
    │       │       ├─ DROPPED → NetworkPolicy blocking DNS (UDP 53) → Fix CNP/Cilium DNS policy
    │       │       └─ No flows → Check kube-dns service ClusterIP reachable
    │       └─ FIX: Restart CoreDNS pods, allow UDP 53 in CNP
"""))

# DT-3: Network Policy Blocking Legitimate Traffic
trees.append(("dt3", "DT-3: Network Policy Blocking Legitimate Traffic", "Network Policy", "5-15 min", r"""
    START: Expected traffic is being blocked (pods can't communicate)
    │
    ├─ Q1: Is ANY traffic getting through between these pods?
    │   ├─ YES (some works, some doesn't) → Likely L7 policy rule mismatch
    │   │   ├─ Run: cilium policy trace --src-pod NS/A --dst-pod NS/B --dport PORT
    │   │   │   ├─ Result: ALLOW → Policy is correct; check application-level issue
    │   │   │   └─ Result: DENY (rule: XXX) → Specific rule is blocking
    │   │   │       ├─ L3/L4 denied → Check port/protocol in policy spec
    │   │   │       └─ L7 denied → Check HTTP method, path, or header mismatch
    │   │   └─ FIX: Update CNP to add missing rule or correct fromEndpoints selector
    │   └─ NO (all blocked) → Likely missing policy OR default-deny catching all
    │       ├─ Run: hubble observe --from-pod NS/A --to-pod NS/B
    │       │   ├─ VERDICT: DROPPED (Policy denied) → Policy explicitly blocking
    │       │   │   └─ Run: cilium policy get | grep -A20 "fromEndpoints"
    │       │   │       └─ FIX: Add ingress rule allowing source pod labels
    │       │   └─ VERDICT: DROPPED (Identity mismatch) → Identity out of sync
    │       │       └─ FIX: kubectl delete cep -n NS BAD-POD (force recreate CEP)
    │       └─ Run: cilium endpoint list → check if both endpoints have identities
"""))

# DT-4: Hubble Shows No Flows
trees.append(("dt4", "DT-4: Hubble Shows No Flows", "Network Observability", "5-10 min", r"""
    START: hubble observe returns no output or empty results
    │
    ├─ Q1: Is Hubble enabled and running?
    │   ├─ NO → cilium hubble enable → cilium status | grep Hubble
    │   │   └─ If still not working → Check Helm values: hubble.enabled=true
    │   └─ YES → Check connectivity and filtering
    │       ├─ Q2: Are you using Hubble Relay or direct node access?
    │       │   ├─ Relay → hubble status (check relay connection)
    │       │   │   ├─ Connected → Filters may be too restrictive
    │       │   │   │   └─ Try: hubble observe --since 1h (wider time window)
    │       │   │   └─ Disconnected → Check: kubectl logs -n kube-system deploy/hubble-relay
    │       │   └─ Direct → cilium hubble port-forward &amp; (local port-forward)
    │       ├─ Q3: Do you have filters that exclude everything?
    │       │   ├─ Check: hubble observe -n NAMESPACE (without --verdict filter)
    │       │   ├─ If flows appear → Your original filter was too strict
    │       │   └─ If still empty → Check if any pods exist in namespace
    │       └─ FIX: Remove restrictive filters; use --since for time range
"""))

# DT-5: Cilium Agent Not Starting
trees.append(("dt5", "DT-5: Cilium Agent Not Starting", "Architecture", "5-20 min", r"""
    START: Cilium agent pod in CrashLoopBackOff or stuck in Init
    │
    ├─ Q1: Check agent pod logs: kubectl logs -n kube-system ds/cilium
    │   ├─ "BPF filesystem not mounted" → bpffs missing
    │   │   └─ FIX: mount -t bpf bpffs /sys/fs/bpf; systemctl enable bpf-mount
    │   ├─ "Kernel version too old" → Kernel &lt; 5.10
    │   │   └─ FIX: Upgrade kernel to 5.10+ (required for Cilium eBPF features)
    │   ├─ "Unable to connect to kube-apiserver" → API server unreachable
    │   │   ├─ Check: kubectl get nodes (if this works, API is up)
    │   │   │   └─ Check agent's kubeconfig and network path to API server
    │   │   └─ FIX: Verify kubeconfig mount, check NetworkPolicy allows API access
    │   ├─ "CRD schema not found" → CRDs not installed
    │   │   └─ FIX: kubectl apply -f cilium-crds.yaml OR reinstall Cilium
    │   ├─ "IPAM allocation failed" → No available pod CIDRs
    │   │   └─ FIX: Check cilium config | grep cluster-pool; expand CIDR if needed
    │   └─ "Failed to create CNI config" → /etc/cni/net.d/ conflict
    │       └─ FIX: Remove old CNI configs (Calico/Flannel), reinstall Cilium
"""))

# DT-6: KPR Services Not Working
trees.append(("dt6", "DT-6: KPR Services Not Working", "Service Mesh", "5-15 min", r"""
    START: Service (ClusterIP/NodePort) not routing traffic in KPR mode
    │
    ├─ Q1: Is kube-proxy replacement actually enabled?
    │   ├─ NO → cilium config set kube-proxy-replacement strict
    │   │   └─ OR Helm: --set kubeProxyReplacement=true
    │   └─ YES → Check: cilium status | grep "KubeProxyReplacement"
    │       ├─ Q2: Does the service appear in BPF lb maps?
    │       │   ├─ cilium service list | grep SERVICE-NAME
    │       │   │   ├─ Not listed → Service not synced to Cilium
    │       │   │   │   └─ FIX: Check service selector matches running pods
    │       │   │   └─ Listed → Check: cilium bpf lb list | grep SERVICE-IP
    │       │   │       ├─ Backends empty → No healthy endpoints
    │       │   │       │   └─ FIX: kubectl get ep SERVICE; ensure pods are Ready
    │       │   │       └─ Backends present → Check NAT/CT: cilium bpf ct list
    │       │   └─ FIX: Restart Cilium agent on affected node if BPF maps stale
    │       └─ Q3: Is NodePort accessible? Check: curl NODE_IP:NODEPORT
    │           ├─ Timeout → Check node firewall allows NodePort range (30000-32767)
    │           └─ Connection refused → Check externalTrafficPolicy setting
"""))

# DT-7: Cluster Mesh Not Connecting
trees.append(("dt7", "DT-7: Cluster Mesh Not Connecting", "Cluster Mesh", "10-20 min", r"""
    START: Cluster Mesh enabled but clusters can't see each other
    │
    ├─ Q1: Are cluster IDs unique? (each cluster needs unique cluster.id AND cluster.name)
    │   ├─ NO → FIX: cilium config set cluster-id UNIQUE_ID (1-255) + cluster-name UNIQUE
    │   └─ YES → Check connectivity
    │       ├─ Q2: Is etcd accessible between clusters?
    │       │   ├─ Check: kubectl -n kube-system exec ds/cilium -- cilium clustermesh status
    │       │   │   ├─ "not connected" → TLS or network issue
    │       │   │   │   ├─ Check: etcd certs match between clusters
    │       │   │   │   └─ FIX: Regenerate certs with cilium clustermesh connect
    │       │   │   └─ "connected" but no services → Sync delay or config issue
    │       │   │       └─ Check: service has annotation io.cilium/global-service=true
    │       │   └─ FIX: Ensure etcd endpoint is reachable (port 2379 open between clusters)
    │       ├─ Q3: Do both clusters share the same CA?
    │       │   ├─ NO → FIX: Re-run cilium clustermesh connect with proper --context
    │       │   └─ YES → Check: cilium clustermesh status --context CLUSTER1 (and CLUSTER2)
    │       └─ FIX: cilium clustermesh disconnect; then reconnect with correct settings
"""))

# DT-8: eBPF Program Load Fails
trees.append(("dt8", "DT-8: eBPF Program Load Fails", "eBPF", "5-15 min", r"""
    START: Cilium agent reports "failed to load eBPF program" or verifier error
    │
    ├─ Q1: What does the error say?
    │   ├─ "BPF verifier rejected" → Kernel too old or missing features
    │   │   ├─ Check: uname -r (needs 5.10+)
    │   │   │   ├─ &lt; 5.10 → FIX: Upgrade kernel (required by Cilium)
    │   │   │   └─ >= 5.10 → Check: grep CONFIG_BPF /boot/config-$(uname -r)
    │   │   │       └─ Missing CONFIG_BPF_JIT or CONFIG_BPF_SYSCALL → Recompile kernel
    │   │   └─ FIX: Enable CONFIG_BPF, CONFIG_BPF_SYSCALL, CONFIG_BPF_JIT in kernel
    │   ├─ "Map creation failed (max entries)" → BPF map limit hit
    │   │   └─ FIX: Increase vm.max_map_count: sysctl -w vm.max_map_count=262144
    │   ├─ "Program too large" → eBPF complexity exceeds kernel limit
    │   │   └─ FIX: Upgrade kernel (5.15+ supports larger programs) OR reduce policy complexity
    │   ├─ "Failed to pin map" → bpffs not mounted or permissions issue
    │   │   └─ FIX: mount | grep bpf; mount -t bpf bpffs /sys/fs/bpf if missing
    │   └─ "CO-RE relocation failed" → Custom kernel without BTF
    │       └─ FIX: Enable CONFIG_DEBUG_INFO_BTF in kernel, recompile
"""))

# DT-9: BGP Peering Down
trees.append(("dt9", "DT-9: BGP Peering Down", "BGP & External Networking", "5-15 min", r"""
    START: BGP session not reaching Established state
    │
    ├─ Q1: Check BGP session state: cilium bgp peers
    │   ├─ State: "Connect" or "Active" → TCP not connecting to peer
    │   │   ├─ Q2: Can the node reach the BGP peer IP?
    │   │   │   ├─ NO → Network/firewall blocking TCP 179 (BGP)
    │   │   │   │   └─ FIX: Allow TCP 179 from Cilium nodes to BGP peer
    │   │   │   └─ YES → Check BGP peer is listening on TCP 179
    │   │   │       └─ FIX: Start BGP daemon on peer (FRR/GoBGP) on port 179
    │   │   └─ FIX: Verify CiliumBGPPeeringPolicy CRD peerAddress is correct
    │   ├─ State: "OpenSent" → ASN mismatch
    │   │   └─ FIX: Verify local ASN in CiliumBGPPeeringPolicy matches peer expectation
    │   ├─ State: "Established" but no routes → Route advertisement issue
    │   │   └─ Check: cilium bgp routes available ipv4 unicast
    │   │       └─ Empty → FIX: Ensure LB IPAM or CiliumLoadBalancerIPPool has addresses
    │   └─ State: "Idle" → Configuration error
    │       └─ FIX: kubectl describe ciliumbgppeeringpolicy; check for validation errors
"""))

# DT-10: Cilium Installation Fails
trees.append(("dt10", "DT-10: Cilium Installation Fails", "Installation &amp; Config", "10-20 min", r"""
    START: cilium install or helm install fails
    │
    ├─ Q1: What stage does it fail?
    │   ├─ "Preflight checks failed" → System requirements not met
    │   │   ├─ Check kernel: uname -r (needs >= 5.10)
    │   │   ├─ Check kubelet: kubectl version (needs >= 1.20)
    │   │   ├─ Check CNI conflict: ls /etc/cni/net.d/ (must be empty or Cilium only)
    │   │   └─ FIX: Upgrade kernel/kubelet; remove old CNI configs; retry
    │   ├─ "Helm install timeout" → Images not pulling or agent not becoming ready
    │   │   ├─ Check: kubectl get pods -n kube-system -l k8s-app=cilium
    │   │   │   ├─ ImagePullBackOff → Registry access issue
    │   │   │   │   └─ FIX: Check image pull secrets; verify quay.io accessible
    │   │   │   └─ CrashLoopBackOff → Agent failing (see DT-5)
    │   │   └─ FIX: Use --version to pin known-stable release
    │   ├─ "CRD conflict" → Previous Cilium installation left CRDs
    │   │   └─ FIX: kubectl delete crd ciliumnetworkpolicies.cilium.io etc. then retry
    │   └─ "API server unavailable" → kubeconfig issue
    │       └─ FIX: kubectl cluster-info; verify context is correct
"""))

# DT-11: L7 Policy Not Enforcing
trees.append(("dt11", "DT-11: L7 Policy Not Enforcing", "Network Policy", "5-15 min", r"""
    START: L7 HTTP/DNS policy rules are not blocking/allowing as expected
    │
    ├─ Q1: Is the policy actually loaded?
    │   ├─ Check: cilium policy get | grep POLICY-NAME
    │   │   ├─ Not listed → Policy not applied
    │   │   │   └─ FIX: kubectl apply -f cnp-l7.yaml; check: kubectl get cnp
    │   │   └─ Listed → Policy loaded in Cilium
    │       ├─ Q2: Do you see "Proxy redirect" in endpoint status?
    │       │   ├─ Check: cilium endpoint get ENDPOINT_ID | grep proxy
    │       │   │   ├─ No proxy → L7 enforcement requires Envoy proxy redirection
    │       │   │   │   └─ FIX: Ensure Cilium is installed with --set envoy.enabled=true
    │       │   │   └─ Proxy present → Check policy trace with --http-method and --http-path
    │       │   └─ Run: cilium policy trace --src-pod NS/A --dst-pod NS/B --dport 80 \\
    │       │            --http-method GET --http-path /api/test
    │       │       ├─ Result: ALLOW (no L7 check) → Policy rules field may be wrong
    │       │       │   └─ FIX: Verify CNP has rules.http section, not just toPorts
    │       │       └─ Result: DENY → Policy is correct; check actual HTTP request matches
    │       └─ FIX: Add rules: - http: - method: GET; path: /api/.* for L7 enforcement
"""))

# DT-12: Hubble UI Not Loading
trees.append(("dt12", "DT-12: Hubble UI Not Loading", "Network Observability", "3-8 min", r"""
    START: Hubble UI shows blank page or connection refused on port 12000
    │
    ├─ Q1: How are you accessing Hubble UI?
    │   ├─ Port-forward: cilium hubble port-forward &amp;
    │   │   ├─ Does the port-forward command succeed?
    │   │   │   ├─ NO → Hubble not deployed → cilium hubble enable --ui
    │   │   │   └─ YES → Open browser: http://localhost:12000
    │   │   │       ├─ Blank page → Check browser console for errors
    │   │   │       │   └─ FIX: Clear cache; try http://localhost:12000/?namespace=default
    │   │   │       └─ Shows UI but no data → Hubble Relay may be down
    │   │   └─ FIX: restart port-forward; ensure port 12000 not in use
    │   ├─ NodePort/LB: Check service: kubectl get svc -n kube-system hubble-ui
    │   │   ├─ Exists → Check service type and external IP
    │   │   │   └─ Pending LB IP → FIX: Use NodePort and access via node IP:nodePort
    │   │   └─ Missing → FIX: helm upgrade cilium --set hubble.ui.enabled=true
    │   └─ FIX: Verify hubble-ui pod is Running: kubectl get pods -n kube-system -l k8s-app=hubble-ui
"""))

# DT-13: WireGuard Encryption Not Working
trees.append(("dt13", "DT-13: WireGuard Encryption Not Working", "Architecture", "5-15 min", r"""
    START: Traffic not encrypted despite enabling WireGuard
    │
    ├─ Q1: Is encryption actually enabled?
    │   ├─ Check: cilium encrypt status
    │   │   ├─ "Encryption: Disabled" → Not enabled
    │   │   │   └─ FIX: cilium config set encryption-enabled true && \
    │   │   │        cilium config set encryption-type wireguard
    │   │   └─ "Encryption: Wireguard" but no peers → Key distribution issue
    │   │       └─ FIX: Restart Cilium agents (rolling restart via kubectl rollout)
    │   └─ YES → Check WireGuard interfaces on each node
    │       ├─ ip link show cilium_wg0 (should show WireGuard interface)
    │       │   ├─ Missing → Kernel doesn't support WireGuard
    │       │   │   └─ FIX: Install wireguard-tools; modprobe wireguard
    │       │   └─ Present but no handshake → wg show cilium_wg0
    │       │       ├─ "latest handshake: 0 seconds ago" → Working!
    │       │       └─ No handshake → Check: hubble observe --verdict DROPPED \\
    │       │           (look for "StaleIPSec" or encryption-related drops)
    │       └─ FIX: Verify UDP port for WireGuard (default dynamic) not firewalled
"""))

# DT-14: Bandwidth Manager Not Limiting
trees.append(("dt14", "DT-14: Bandwidth Manager Not Limiting", "Service Mesh", "5-10 min", r"""
    START: Pod egress traffic not being rate-limited despite bandwidth annotation
    │
    ├─ Q1: Is Bandwidth Manager enabled?
    │   ├─ Check: cilium config | grep enable-bandwidth-manager
    │   │   ├─ false → Not enabled
    │   │   │   └─ FIX: cilium config set enable-bandwidth-manager true
    │   │   │        (requires BPF Host Routing + kernel 5.1+)
    │   │   └─ true → Check kernel supports FQ (Fair Queue) qdisc
    │   │       └─ FIX: Kernel must have CONFIG_NET_SCH_FQ enabled
    │   └─ YES → Check pod annotation
    │       ├─ kubectl get pod POD -o yaml | grep egress-bandwidth
    │       │   ├─ Not set → Annotation missing
    │       │   │   └─ FIX: kubectl annotate pod POD kubernetes.io/egress-bandwidth=50M
    │       │   └─ Set → Check if BPF program is attached
    │       │       └─ bpftool prog list | grep bandwidth → should show EDT/rate-limit
    │       └─ Q2: Is BPF Host Routing enabled? (requirement for Bandwidth Manager)
    │           ├─ NO → FIX: cilium config set bpf-host-routing true (kernel 5.10+)
    │           └─ YES → Verify: tc qdisc show dev eth0 (should show fq qdisc)
"""))

# DT-15: High Latency Between Pods
trees.append(("dt15", "DT-15: High Latency Between Pods", "Architecture", "5-15 min", r"""
    START: Pod-to-pod latency is unexpectedly high (&gt;10ms for same-node, &gt;50ms cross-node)
    │
    ├─ Q1: Is the latency same-node or cross-node?
    │   ├─ Same-node high → BPF datapath or eBPF overhead issue
    │   │   ├─ Check: cilium endpoint list | grep ENDPOINT (ready state?)
    │   │   │   ├─ "regenerating" → Endpoint being rebuilt → Wait for ready
    │   │   │   └─ "ready" → Check: cilium bpf ct list ENDPOINT_ID
    │   │   │       └─ Large conntrack table → bpftool map dump (check size)
    │   │   ├─ Check: top/htop on node → CPU contention on Cilium agent?
    │   │   │   └─ FIX: Reduce policy complexity; increase agent CPU limit
    │   │   └─ FIX: Verify no L7 proxy in path unnecessarily (adds latency)
    │   └─ Cross-node high → Network or tunnel overhead
    │       ├─ Q2: What's the tunnel type?
    │       │   ├─ VXLAN → 50 bytes overhead, MTU may cause fragmentation
    │       │   │   └─ FIX: Set MTU to 1400 (cilium config set mtu 1400)
    │       │   ├─ Geneve → Similar to VXLAN, check MTU
    │       │   └─ Native Routing → Check: traceroute POD_B_IP
    │       │       └─ Extra hops → Suboptimal routing → Check BGP or node routes
    │       ├─ Q3: Is encryption (WireGuard/IPSec) enabled?
    │       │   └─ YES → Encryption adds ~5-10% overhead (expected)
    │       └─ FIX: Native routing + BGP eliminates tunnel overhead entirely
"""))

# ── Generate HTML ──
lines = []
lines.append('')
lines.append('    <!-- ═══════════════ APPENDIX E: 15 DECISION TREE FLOWCHARTS ═══════════════ -->')
lines.append('    <section class="chapter-section" id="apx-e">')
lines.append('        <h2><span>🌳 Appendix E: Decision Tree Flowcharts</span><span class="chapter-badge">15 Printable Diagrams</span></h2>')
lines.append('')
lines.append('        <div class="aq-info">')
lines.append('            <p>These <strong>15 decision tree flowcharts</strong> cover the most common Cilium troubleshooting scenarios across all 8 exam domains. Each tree starts with a symptom, branches through <strong>YES/NO diagnostic decisions</strong>, provides specific commands at each branch, and ends with a <strong>terminal leaf: root cause + fix</strong>. Print these for your wall — they\'re designed to train your diagnostic intuition for the CCA exam.</p>')
lines.append('            <p><strong>How to read:</strong> Follow the branches top-to-bottom. Each <strong>Q</strong> is a yes/no question. Each leaf (end of branch) shows a <strong>FIX</strong> — the resolution. Commands shown are the exact diagnostic tools you\'d run at that decision point.</p>')
lines.append('        </div>')
lines.append('')

# Summary grid
lines.append('        <h3>📊 Decision Tree Index</h3>')
lines.append('        <div class="cmd-table-wrap">')
lines.append('        <table class="cmd-table">')
lines.append('            <tr><th>ID</th><th>Title</th><th>Domain</th><th>Est. Time</th><th>Levels</th></tr>')
for dt_id, title, cat, time, tree in trees:
    depth = tree.count('├─') + tree.count('└─')
    lines.append(f'            <tr><td class="cmd-num">{dt_id.upper()}</td><td class="cmd-syn"><code>{title}</code></td><td class="cmd-purpose">{cat}</td><td class="cmd-num">{time}</td><td class="cmd-num">{depth}</td></tr>')
lines.append('        </table>')
lines.append('        </div>')
lines.append('')

# Individual trees
for dt_id, title, cat, time, tree in trees:
    lines.append(f'        <h3>🌳 {title}</h3>')
    lines.append(f'        <p><strong>Category:</strong> {cat} | <strong>Est. Resolution Time:</strong> {time}</p>')
    lines.append('        <div class="decision-tree">')
    # Clean up tree - strip leading newlines and common indentation
    clean = tree.strip('\n')
    lines.append(f'<pre>{clean}')
    lines.append('</pre>')
    lines.append('        </div>')
    lines.append('')

# Tips
lines.append('        <div class="aq-tips">')
lines.append('            <h4>💡 How to Use Decision Trees in the Exam</h4>')
lines.append('            <ul>')
lines.append('                <li><strong>Start at the top:</strong> Every tree begins with a clear symptom. Match your exam scenario to the closest tree title.</li>')
lines.append('                <li><strong>Follow YES/NO branches:</strong> Run the diagnostic command shown at each branch. The result determines which path to follow next.</li>')
lines.append('                <li><strong>Commands are part of the answer:</strong> In CCA exam troubleshooting tasks, showing you know WHICH command to run is as important as the fix itself.</li>')
lines.append('                <li><strong>Terminal leaves are your solution:</strong> Each end point includes both the root cause AND the fix command — these are directly applicable to exam answers.</li>')
lines.append('                <li><strong>Time estimates:</strong> Use these to manage your exam pacing. If you\'ve spent more than the estimate on one issue, move on and return later.</li>')
lines.append('                <li><strong>Print and practice:</strong> These 15 trees cover ~80% of real-world Cilium issues. Practice navigating them mentally before exam day.</li>')
lines.append('            </ul>')
lines.append('        </div>')
lines.append('')
lines.append('    </section>')

appendix_e_html = '\n'.join(lines)

# ── Insert into file ──
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

marker = '\n\n    <!-- ═══════════════ FOOTER ═══════════════ -->'
if marker in content:
    new_content = content.replace(marker, appendix_e_html + marker, 1)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'✅ Appendix E inserted! File: {len(new_content):,} bytes')
    print(f'   Decision Trees: {len(trees)} across all 8 domains')
else:
    print('❌ Could not find FOOTER marker!')
