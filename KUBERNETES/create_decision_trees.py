#!/usr/bin/env python3
"""Create and insert all 15 decision trees + ts-dt section header"""

PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

dt_header = '''
    <!-- ═══════════════ DECISION TREES ═══════════════ -->
    <div class="ts-section-header" id="ts-dt">
        <h3>🌲 Decision Trees — Rapid Troubleshooting Checklists</h3>
    </div>
'''

def make_dt(num, title, intro, steps):
    """Generate a decision tree block. steps is list of (question, yes_goto, no_goto) tuples."""
    rows = ""
    for i, (q, yes, no) in enumerate(steps):
        rows += f"""                <tr>{"style=\"background:#1c2128;\"" if i % 2 == 0 else ""}>
                    <td style="padding:8px 12px;border:1px solid #30363d;font-weight:600;">{i+1}</td>
                    <td style="padding:8px 12px;border:1px solid #30363d;">{q}</td>
                    <td style="padding:8px 12px;border:1px solid #30363d;color:#3fb950;">✅ {yes}</td>
                    <td style="padding:8px 12px;border:1px solid #30363d;color:#f85149;">❌ {no}</td>
                </tr>
"""
    return f'''    <div class="ts-issue" id="dt{num}">
        <div class="ts-issue-header">
            <div class="ts-issue-num">DT{num}</div>
            <div class="ts-issue-header-content">
                <div class="ts-category">🌲 DECISION TREE — DT{num}</div>
                <div class="ts-title">{title}</div>
                <p class="ts-symptom"><strong>📋 Quick Decision Flow:</strong> {intro}</p>
            </div>
        </div>
        <table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;">
            <tr style="background:#0d1117;">
                <th style="padding:8px 12px;border:1px solid #30363d;text-align:left;width:40px;">#</th>
                <th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">🔍 Check This</th>
                <th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">If YES →</th>
                <th style="padding:8px 12px;border:1px solid #30363d;text-align:left;">If NO →</th>
            </tr>
{rows}        </table>
        <div class="ts-footer-spacer"></div>
    </div>
'''

# =====================================================================
# Generate all 15 decision trees
# =====================================================================
trees = ""

trees += make_dt(1, "Pod Cannot Reach Another Pod",
    "Start here for ANY pod-to-pod connectivity issue on Cilium.",
    [
        ("Run: <code>cilium status</code> — all components OK?", "Go to step 2", "Fix agent/operator first"),
        ("Are both pods on the SAME node? (<code>kubectl get pod -o wide</code>)", "Go to step 3 (same-node)", "Go to step 4 (cross-node)"),
        ("<code>cilium endpoint list</code> — both endpoints 'ready'?", "Check CNP/L7 policy", "Restart Cilium agent on node"),
        ("<code>cilium bpf tunnel list</code> — tunnel to remote node exists?", "Go to step 5", "Check VXLAN/Geneve/encapsulation"),
        ("<code>hubble observe --from-pod a --to-pod b --verdict DROPPED</code> — drops?", "Policy issue → check CNP", "Check MTU/conntrack/identity"),
    ])

trees += make_dt(2, "Service ClusterIP Unreachable",
    "Troubleshoot when a pod cannot reach a Kubernetes Service via its ClusterIP.",
    [
        ("<code>cilium service list | grep &lt;svc-ip&gt;</code> — service exists with backends?", "Go to step 2", "KPR not working / service not synced"),
        ("Backend count &gt; 0? (<code>cilium service get &lt;id&gt;</code>)", "Go to step 3", "Check endpoints: <code>kubectl get ep</code>"),
        ("<code>kubectl get ep &lt;svc&gt;</code> — ready endpoints match pods?", "Go to step 4", "Service selector doesn't match pods"),
        ("<code>hubble observe --to-service &lt;ns&gt;/&lt;name&gt;</code> — traffic forwarded?", "Service is working!", "Go to step 5"),
        ("<code>cilium bpf lb list</code> — Maglev table has backend slots?", "Check CNP blocking service traffic", "Restart Cilium agent / check KPR mode"),
    ])

trees += make_dt(3, "NetworkPolicy Blocking Traffic",
    "Debug traffic being dropped by CiliumNetworkPolicy or Kubernetes NetworkPolicy.",
    [
        ("<code>hubble observe --verdict DROPPED -n &lt;ns&gt;</code> — drops exist?", "Go to step 2", "Policy is NOT the issue — check connectivity"),
        ("<code>cilium policy get -n &lt;ns&gt;</code> — policies present?", "Go to step 3", "Check default-deny / entity rules"),
        ("Drop reason in Hubble: 'Policy denied' or 'Auth required'?", "Policy rule matched → go to step 4", "Check if it's an identity/resolve issue"),
        ("<code>kubectl describe cnp &lt;name&gt; -n &lt;ns&gt;</code> — rule selects correct pods?", "Go to step 5", "Fix pod selector in CNP"),
        ("Rule has correct port/protocol + L7 rules (if HTTP)?", "Policy is correct — check entity/endpoint identity", "Fix CNP port/protocol or add L7 allow rule"),
    ])

trees += make_dt(4, "Hubble Shows No Flows",
    "Troubleshoot when Hubble observe returns empty or Hubble UI shows blank.",
    [
        ("<code>cilium status | grep Hubble</code> — all components 'OK'?", "Go to step 2", "Enable Hubble: <code>cilium hubble enable</code>"),
        ("<code>cilium hubble relay status</code> — peers &gt; 0?", "Go to step 3", "Check hubble-peer Service / agent Hubble enabled"),
        ("Generate test traffic: <code>cilium connectivity test</code> — flows visible?", "Go to step 4", "Cluster idle — no traffic to observe"),
        ("<code>hubble observe --last 100</code> — recent flows appear?", "Go to step 5", "Check time range / ring buffer"),
        ("<code>hubble observe --verdict DROPPED</code> — policy drops visible?", "Hubble working! Narrow filter by namespace/pod", "Check if Hubble metrics/export enabled"),
    ])

trees += make_dt(5, "Cilium Agent CrashLoopBackOff",
    "Agent pods fail to start or repeatedly crash after deployment or upgrade.",
    [
        ("<code>kubectl logs ds/cilium -n kube-system --tail=50</code> — error message?", "Go to step 2 based on error", "Check <code>kubectl describe pod</code> for events"),
        ("BPF/kernel error? (<code>uname -r</code> ≥ 5.10?)", "Kernel too old → upgrade to 5.10+", "Go to step 3"),
        ("CNI conflist conflict? (<code>ls /etc/cni/net.d/</code> — multiple files?)", "Remove old CNI config, keep only Cilium", "Go to step 4"),
        ("kube-proxy still running? (<code>kubectl get ds -n kube-system</code>)", "Delete kube-proxy DaemonSet", "Go to step 5"),
        ("<code>mount | grep bpf</code> — bpffs mounted?", "Check kernel config for CONFIG_BPF=y", "Mount: <code>mount -t bpf bpffs /sys/fs/bpf</code>"),
    ])

trees += make_dt(6, "Cluster Mesh Not Connecting",
    "Two clusters won't form a mesh — cross-cluster communication fails.",
    [
        ("<code>cilium clustermesh status</code> — shows 'connected'?", "Mesh is working! Check cross-cluster policy", "Go to step 2"),
        ("etcd reachable? (<code>nc -zv &lt;etcd-ip&gt; 2379</code> from Cilium node)", "Go to step 3", "Fix network/firewall to etcd"),
        ("Cluster IDs unique? (<code>cilium config | grep cluster-id</code> on both)", "Go to step 4", "Set unique cluster.id (1, 2, 3...)"),
        ("Pod CIDRs non-overlapping? (<code>cilium config | grep cluster-pool</code>)", "Go to step 5", "Re-IP one cluster — CIDRs MUST be unique"),
        ("TLS certs valid? (<code>cilium clustermesh status</code> shows TLS errors?)", "Check node-to-node IP reachability between clusters", "Regenerate certs: <code>cilium clustermesh disable; enable</code>"),
    ])

trees += make_dt(7, "BGP Peering Down",
    "BGP session won't establish between Cilium node and external router.",
    [
        ("<code>cilium-dbg bgp peers</code> — session state 'Established'?", "BGP is up! Check route advertisement", "Go to step 2"),
        ("Peer IP reachable? (<code>ping &lt;peer-ip&gt;</code> from Cilium node)", "Go to step 3", "Fix L3 connectivity / routing to peer"),
        ("TCP 179 open? (<code>nc -zv &lt;peer-ip&gt; 179</code>)", "Go to step 4", "Open firewall for TCP 179 (BGP port)"),
        ("<code>kubectl get ciliumbgppeeringpolicy</code> — policy exists?", "Go to step 5", "Create CiliumBGPPeeringPolicy CRD"),
        ("nodeSelector matches at least one node? (<code>kubectl get nodes -l &lt;sel&gt;</code>)", "Check ASN values match peer config on both sides", "Fix nodeSelector or label node"),
    ])

trees += make_dt(8, "Encryption Not Working (WireGuard/IPSec)",
    "Traffic between nodes is not encrypted despite encryption being enabled.",
    [
        ("<code>cilium encrypt status</code> — shows 'OK' / keys present?", "Go to step 2", "Enable: <code>cilium encrypt enable</code>"),
        ("All nodes show 'OK'? (<code>cilium encrypt status</code> on each node)", "Go to step 3", "Check agent logs on failing nodes"),
        ("Type correct? WireGuard needs kernel 5.6+. IPSec needs no special kernel.", "Go to step 4", "Switch encryption type or upgrade kernel"),
        ("<code>hubble observe --verdict FORWARDED</code> — traffic flowing encrypted?", "Encryption working!", "Go to step 5"),
        ("<code>kubectl logs ds/cilium | grep -i 'wireguard|ipsec|encrypt'</code> — errors?", "Check WireGuard port 51871/UDP open between nodes", "Check if encryption key rotation is in progress"),
    ])

trees += make_dt(9, "Bandwidth Manager Not Limiting",
    "CNP bandwidth rules not enforced — pods exceed configured rate limits.",
    [
        ("<code>cilium status | grep Bandwidth</code> — 'OK'?", "Go to step 2", "Enable: <code>--set bandwidthManager.enabled=true</code>"),
        ("<code>tc qdisc show dev lxc_&lt;id&gt;</code> — shows 'fq' qdisc?", "Go to step 3", "EDT/FQ not attached — kernel may be too old"),
        ("Kernel ≥ 5.1? (<code>uname -r</code>)", "Go to step 4", "Upgrade kernel to ≥ 5.1 for EDT support"),
        ("CNP bandwidth field in correct location? (<code>egress[].bandwidth</code>)", "Go to step 5", "Move bandwidth to correct CNP field"),
        ("Are there L7 policies on same endpoint?", "Incompatible! L7 → bandwidth disabled. Choose one.", "Test with <code>iperf3</code> between pods — measure actual rate"),
    ])

trees += make_dt(10, "DNS Resolution Failing for Pods",
    "Pods cannot resolve internal or external DNS names via CoreDNS.",
    [
        ("<code>kubectl exec &lt;pod&gt; -- nslookup kubernetes.default</code> — resolves?", "DNS is working — check specific domain", "Go to step 2"),
        ("<code>kubectl get pods -n kube-system -l k8s-app=kube-dns</code> — CoreDNS running?", "Go to step 3", "CoreDNS is down — fix CoreDNS first"),
        ("<code>hubble observe --to-port 53 --verdict DROPPED</code> — DNS drops?", "CNP blocking DNS! Add UDP 53 rule.", "Go to step 4"),
        ("Cilium DNS proxy enabled? (<code>cilium config | grep dns-proxy</code>)", "Go to step 5", "Check iptables DNS redirect rules"),
        ("<code>cilium endpoint list</code> — endpoint has DNS proxy enabled?", "Check CoreDNS service ClusterIP reachable from pod", "Restart Cilium agent or disable DNS proxy"),
    ])

trees += make_dt(11, "L7 Policy Not Enforcing (HTTP/gRPC)",
    "CiliumNetworkPolicy with L7 HTTP rules doesn't block/allow as expected.",
    [
        ("<code>cilium status | grep Proxy</code> — Envoy proxy 'OK'?", "Go to step 2", "Enable Envoy: L7 needs proxy running"),
        ("CNP has <code>toPorts[].rules.http</code> section?", "Go to step 3", "Add L7 HTTP rules — L3/L4 rules don't trigger Envoy"),
        ("<code>hubble observe --http-status &lt;code&gt;</code> — L7 flows visible?", "Go to step 4", "Enable Hubble L7 visibility / check TLS"),
        ("<code>cilium-dbg envoy config dump | grep &lt;domain&gt;</code> — config loaded?", "Go to step 5", "CNP syntax error — check with <code>kubectl describe cnp</code>"),
        ("HTTP method/path matches request? (GET vs POST, /api vs /health)", "L7 policy working! Check header values if using headerMatches", "Fix CNP HTTP rule to match actual request pattern"),
    ])

trees += make_dt(12, "Egress Gateway Not Working",
    "Pod egress traffic not exiting through designated gateway node with fixed IP.",
    [
        ("<code>cilium status | grep Egress</code> — Egress Gateway enabled?", "Go to step 2", "Enable: <code>--set egressGateway.enabled=true</code>"),
        ("<code>kubectl get cegp -A</code> — policy exists?", "Go to step 3", "Create CiliumEgressGatewayPolicy CRD"),
        ("Gateway node labeled? (<code>kubectl get nodes -l cilium.io/egress-gateway=true</code>)", "Go to step 4", "Label gateway node(s)"),
        ("CES (CiliumEndpointSlice) disabled? (Egress GW incompatible with CES)", "Go to step 5", "Disable CES: <code>--set endpointSlice.enabled=false</code>"),
        ("Destination CIDR matches pod's egress target?", "Check <code>cilium-dbg bpf egress list</code> for entries", "Fix policy destination CIDRs to match actual targets"),
    ])

trees += make_dt(13, "NodePort Service Not Accessible Externally",
    "External clients cannot reach a NodePort service on any cluster node.",
    [
        ("<code>cilium status | grep KubeProxyReplacement</code> — 'Strict'?", "Go to step 2", "KPR must be 'strict' for NodePort via eBPF"),
        ("<code>curl http://&lt;node-ip&gt;:&lt;nodeport&gt;</code> from same node — works?", "Go to step 3", "Check NodePort BPF program / devices config"),
        ("From different node: <code>curl http://&lt;other-node&gt;:&lt;nodeport&gt;</code> — works?", "Go to step 4", "Firewall/security group blocking NodePort range (30000-32767)"),
        ("<code>cilium service list | grep &lt;nodeport&gt;</code> — service listed?", "Go to step 5", "Service not recognized — check KPR configuration"),
        ("<code>hubble observe --to-port &lt;nodeport&gt;</code> — traffic arriving?", "Check externalTrafficPolicy (Local vs Cluster) + backend health", "Check external firewall / cloud LB health checks"),
    ])

trees += make_dt(14, "Cilium Upgrade Fails or Causes Outage",
    "After upgrading Cilium, agents crash, connectivity breaks, or features stop working.",
    [
        ("Read UPGRADE NOTES for target version? (<a href='https://docs.cilium.io'>docs.cilium.io</a>)", "Go to step 2", "STOP! Read upgrade notes — BREAKING CHANGES section"),
        ("Applied new CRDs BEFORE Helm upgrade? (<code>kubectl apply -f crds.yaml</code>)", "Go to step 3", "Apply new CRD schemas first, then upgrade Helm"),
        ("<code>cilium status</code> — all agents 'OK' after upgrade?", "Go to step 4", "Check agent logs for version mismatch / BPF errors"),
        ("<code>cilium connectivity test</code> — all tests pass?", "Upgrade successful! 🎉", "Go to step 5"),
        ("Specific test failures? (L7 tests = Envoy, encryption = WireGuard, etc.)", "Restart pods to reload eBPF programs with new agent version", "Run <code>cilium sysdump</code> and check for partial upgrade state"),
    ])

trees += make_dt(15, "Performance Degradation (High Latency / Low Throughput)",
    "Pod-to-pod latency increased or throughput decreased after Cilium deployment.",
    [
        ("<code>cilium status</code> — all components healthy?", "Go to step 2", "Fix unhealthy components first"),
        ("Same-node or cross-node traffic slow? (test both with <code>ping</code>)", "Go to step 3 (same-node)", "Go to step 4 (cross-node)"),
        ("eBPF Host Routing enabled? (<code>cilium config | grep host-routing</code>)", "Host routing bypasses iptables → lower latency", "Check iptables rule count: <code>iptables -t nat -L | wc -l</code>"),
        ("Tunnel mode? (<code>cilium config | grep tunnel</code>)", "Tunnel adds ~50 bytes overhead. Try native routing.", "Go to step 5"),
        ("MTU issues? (<code>ping -M do -s 1472 &lt;remote-pod&gt;</code> — fragments?)", "Check bandwidth manager / BBR / conntrack table size", "Reduce MTU: <code>cilium config set mtu 1400</code>"),
    ])

# =====================================================================
# Insert into file before Appendix E
# =====================================================================

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Find Appendix E and insert before it
marker = '<section class="chapter-section" id="apx-e">'
if marker in content:
    # Find the ts-dt section header that should precede the trees
    # Actually, insert the whole block before Appendix E
    full_block = dt_header + "\n" + trees + "\n\n    "
    content = content.replace(marker, full_block + marker.lstrip(), 1)
    print("✅ 15 decision trees + ts-dt inserted before Appendix E")
else:
    print("❌ Appendix E marker not found!")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 Batch 3 complete!")
