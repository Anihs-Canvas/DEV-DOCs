#!/usr/bin/env python3
"""Generate and insert ALL missing troubleshooting issues (Cats 3-8) in one pass."""

HTML_PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

def li(t, cls="cause-likely"):
    return f'            <li><span class="{cls}">{t}</span></li>'

def ts(cat, cat_name, color, iid, label, title, symptom, most, less, new, look, sol, adv, diag=""):
    return f'''    <div class="ts-issue" id="ts-{iid}-detail">
        <div class="ts-issue-header">
            <div class="ts-issue-num">{label}</div>
            <div class="ts-issue-header-content">
                <div class="ts-category">{color} CATEGORY {cat}: {cat_name} — Issue {label}</div>
                <div class="ts-title">{title}</div>
                <p class="ts-symptom"><strong>🔍 Symptom:</strong> {symptom}</p>
            </div>
        </div>
        {diag}
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>{"".join(most)}</ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>{"".join(less)}</ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>{"".join(new)}</ol></div>
        </div>
        <div class="ts-lookat"><strong>🔍 What to Look At / Take Note Of:</strong> {look}</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>{sol}</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> {adv}</div>
        <div class="ts-footer-spacer"></div>
    </div>'''

def section_header(iid, title):
    return f'    <div class="ts-section-header" id="ts-{iid}"><h3>{title}</h3></div>'

# =====================================================================
# BUILD ALL CONTENT
# =====================================================================
parts = []

# ---------- CAT 3: SERVICE MESH (SM1-SM16) ----------
parts.append(section_header("sm1", "🔀 SM1–SM4: Kube-Proxy Replacement & Load Balancing"))
parts.append(ts(3, "SERVICE MESH", "🟡", "sm1", "SM1",
    "Kube-Proxy Replacement Not Working — Services Unreachable",
    "anihpj-api ClusterIP unreachable from pods. kube-proxy was supposed to be replaced by Cilium eBPF. NodePort also broken.",
    [li("kubeProxyReplacement not set to strict: Check `cilium config | grep kube-proxy-replacement`. Must be 'strict'."),
     li("Native devices not specified: `--set devices=eth0`. Check `cilium config | grep devices`."),
     li("kube-proxy still running: `kubectl get pods -n kube-system -l k8s-app=kube-proxy`. If DaemonSet exists, delete it."),
     li("BPF NodePort not loaded: Check `cilium status | grep KubeProxyReplacement`. Should show 'Strict'."),
     li("Kernel < 5.10: Strict mode needs kernel 5.10+. Check `uname -r`.")],
    [li("iptables rules from old kube-proxy still present: `iptables -t nat -L KUBE-SERVICES`", "cause-less-likely"),
     li("Race condition: Cilium agent started before kube-proxy fully removed", "cause-less-likely"),
     li("NodePort range conflict with host port bindings", "cause-less-likely"),
     li("BPF map cilium_lb4_services exhausted (max service entries)", "cause-less-likely"),
     li("IPv6 DAD delaying service IP assignment", "cause-less-likely")],
    [li("kubeProxyReplacement never set: Default 'disabled'. Helm: `--set kubeProxyReplacement=strict`", "cause-new-cluster"),
     li("Helm install without devices: `--set devices='{eth0}'` missing", "cause-new-cluster"),
     li("cilium-operator not assigning node addresses for NodePort", "cause-new-cluster"),
     li("RBAC missing for Cilium to watch Services/Endpoints", "cause-new-cluster"),
     li("kube-proxy mode still iptables in kubeadm config", "cause-new-cluster")],
    "<code>cilium status | grep KubeProxyReplacement</code> — must say 'Strict (Kernel)'. <code>cilium service list</code> shows backend counts. <code>kubectl get pods -n kube-system | grep kube-proxy</code> — should be empty.",
    "1. <code>cilium config view | grep kube-proxy-replacement</code><br>2. <code>kubectl delete ds -n kube-system kube-proxy</code><br>3. <code>cilium config set kube-proxy-replacement strict</code><br>4. Restart: <code>kubectl -n kube-system rollout restart ds/cilium</code><br>5. Verify: <code>cilium connectivity test</code>",
    "KPR is Cilium's killer feature — replaces thousands of iptables rules with one BPF map lookup. For anihpj: always go strict if kernel ≥5.10. Test with `curl http://anihpj-api.anihpj.svc` from web pod."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm2", "SM2",
    "Maglev Backend Imbalance — Uneven Service Load Distribution",
    "anihpj-api with 5 backends: Pod-1 gets 45%, Pod-5 gets 5%. Hubble confirms imbalance. Connection tracking shows sticky sessions.",
    [li("Maglev table size (M) too small: M=65537 default. If M/N causes hash collisions. Check `cilium service list`."),
     li("Connection tracking pinning: Long-lived TCP connections stick to same backend. Expected behavior."),
     li("Backend weight misconfiguration: Check `cilium service get <svc-id>` for unequal weights."),
     li("Maglev hash seed collision: Rare — two backends hash to overlapping ranges."),
     li("Unequal backend capacity: CPU throttled pods process fewer requests — natural skew.")],
    [li("Cilium version mismatch causing different Maglev tables per node", "cause-less-likely"),
     li("Node-local backends preferred (service affinity not 'none')", "cause-less-likely"),
     li("eBPF map stale entries after backend scale-down", "cause-less-likely"),
     li("Maglev permutation corruption from concurrent updates", "cause-less-likely"),
     li("Kernel entropy depleted affecting hash distribution", "cause-less-likely")],
    [li("Default Maglev table not tuned: M=65537 fine for most", "cause-new-cluster"),
     li("Service created before all backends ready", "cause-new-cluster"),
     li("externalTrafficPolicy:Local restricting NodePort traffic", "cause-new-cluster"),
     li("Topology-aware routing restricting backend selection", "cause-new-cluster"),
     li("CiliumEndpointSlice not enabled — slow backend updates", "cause-new-cluster")],
    "<code>cilium service list</code> — backend counts/weights. <code>cilium bpf lb list</code> — Maglev slots per backend. Hubble: `hubble observe --to-service anihpj/anihpj-api`. Note: Maglev is consistent hashing — minimizes disruption, not guarantees perfect balance.",
    "1. Check distribution: <code>hubble observe --to-service anihpj/anihpj-api --output json | jq 'group_by(.destination_pod)'</code><br>2. If >20% skew: <code>cilium bpf lb list</code><br>3. For connection-heavy apps: normal TCP behavior. Use gRPC streaming for better distribution<br>4. Tune: <code>cilium config set maglev-table-size 655373</code><br>5. Verify no weight annotations on endpoints",
    "±15% variation with 5 backends is normal for Maglev. If 50%+ skew, check for restarting pods. Maglev's strength: when a backend dies, only connections to THAT backend shift — not all connections."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm3", "SM3",
    "Socket-Level Load Balancing Fails — L7 Proxy Bypass Conflict",
    "Socket LB enabled but HTTP requests not balanced. L7 policies not enforced. Hubble shows direct pod-to-pod without proxy hop.",
    [li("Socket LB incompatible with L7 policies: Any L7 rule AUTO-DISABLES socket LB for that endpoint. Check CNP for http rules."),
     li("Socket LB requires non-hostNetwork pods: Host network pods use host stack, bypass socket hooks."),
     li("Cilium agent socket-lb-enable flag not set: `cilium config | grep socket-lb` must be 'true'."),
     li("Kernel < 5.7: Socket LB needs 5.7+ for full cgroup hooks."),
     li("App using non-standard socket calls: sendmmsg() or custom ops may bypass BPF hooks.")],
    [li("BPF sockmap full — max entries reached", "cause-less-likely"),
     li("Cgroup v2 not enabled: `cat /proc/filesystems | grep cgroup2`", "cause-less-likely"),
     li("Socket buffer size mismatch causing partial reads", "cause-less-likely"),
     li("TCP_NODELAY/TCP_QUICKACK interfering with BPF hooks", "cause-less-likely"),
     li("Cgroup hierarchy permissions blocking socket hooks", "cause-less-likely")],
    [li("Socket LB not enabled at install: `--set socketLB.enabled=true` missing", "cause-new-cluster"),
     li("Cgroup v2 not default: containerd config `SystemdCgroup = true` missing", "cause-new-cluster"),
     li("Agent not restarted after enabling socket LB", "cause-new-cluster"),
     li("AppArmor/SELinux blocking BPF socket operations", "cause-new-cluster"),
     li("socketLB.hostNamespaceOnly=true set but pod not hostNetwork", "cause-new-cluster")],
    "<code>cilium config | grep socket-lb</code> — must be true. <code>cat /proc/filesystems | grep cgroup2</code>. Note: Socket LB AUTO-DISABLES when L7 policies apply. Check CNP before debugging socket LB.",
    "1. Check L7 policies: <code>kubectl get cnp -A | grep -i http</code><br>2. Verify: <code>cilium config | grep socket-lb</code><br>3. Remove L7 rules for pure L4 load balancing<br>4. For L7 needs: accept that socket LB won't work — use Envoy<br>5. Monitor: <code>cilium bpf lb list --socket</code>",
    "Socket LB = sub-microsecond L4, no Envoy. L7 policies = Envoy proxy hop. You CAN'T have both — it's an architectural tradeoff. For anihpj: if you just need round-robin to API backends, socket LB is faster. If you need HTTP path routing, stick with L7 CNP."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm4", "SM4",
    "DSR (Direct Server Return) — Asymmetric Routing Breaks Connections",
    "DSR mode configured but reply traffic bypasses Cilium. Hubble shows forward only, no reverse. Clients see connection timeouts.",
    [li("DSR needs IPIP/Geneve tunnel: `ip link show cilium_geneve` must be UP on ALL nodes."),
     li("VIP not on backend loopback: DSR requires service VIP on `lo` interface of backend pod's node. If missing, reply goes with pod IP."),
     li("rp_filter dropping replies: Kernel sees spoofed source (VIP). `sysctl net.ipv4.conf.all.rp_filter=0`."),
     li("Client not reachable from backend: DSR bypasses original path — backend needs direct route to client."),
     li("DSR requires strict KPR: `cilium config | grep kube-proxy-replacement` must be 'strict'.")],
    [li("MTU: IPIP adds 20 bytes. Path MTU < 1520 causes fragmentation", "cause-less-likely"),
     li("Conntrack on backend creating asymmetric flow entries", "cause-less-likely"),
     li("ARP responder for VIP not running on backend node", "cause-less-likely"),
     li("Cilium health endpoint reporting DSR disabled at runtime", "cause-less-likely"),
     li("Network ACL blocking direct backend-to-client traffic", "cause-less-likely")],
    [li("DSR not enabled at install: `--set loadBalancer.mode=dsr` missing", "cause-new-cluster"),
     li("Tunnel protocol not specified: DSR needs Geneve or IPIP explicitly", "cause-new-cluster"),
     li("Cloud LB health checks fail — DSR bypasses LB return path", "cause-new-cluster"),
     li("NodePort DSR not enabled alongside ClusterIP DSR", "cause-new-cluster"),
     li("KPR not strict — DSR requires full kube-proxy replacement", "cause-new-cluster")],
    "<code>cilium config | grep -E 'dsr|tunnel|kube-proxy'</code>. <code>ip link show | grep geneve</code>. Backend: <code>ip addr show lo</code> — VIP present. <code>sysctl net.ipv4.conf.all.rp_filter</code> — must be 0.",
    "1. Verify: <code>cilium config | grep dsr</code><br>2. Check tunnel: <code>ip link show cilium_geneve</code><br>3. rp_filter: <code>sysctl -w net.ipv4.conf.all.rp_filter=0</code><br>4. VIP on lo: <code>ip addr add <VIP>/32 dev lo</code><br>5. Test: <code>tcpdump -i any host <client-ip></code> on backend",
    "DSR = ultimate performance (backends reply directly to clients). But operationally complex. For anihpj: unless serving 100K+ req/s with large responses, stick with SNAT mode. DSR shines for video streaming where return bandwidth matters."
))

# SM5-SM8: Ingress & Gateway API
parts.append(section_header("sm5", "🚪 SM5–SM8: Ingress & Gateway API"))
parts.append(ts(3, "SERVICE MESH", "🟡", "sm5", "SM5",
    "Cilium Ingress Controller — 503 Backend Unavailable",
    "anihpj-web Ingress returns HTTP 503. `kubectl describe ingress` shows 'no healthy backends'. Pods Running, endpoints exist.",
    [li("Ingress controller not enabled: `cilium config | grep ingress-controller` must be true. Helm: `--set ingressController.enabled=true`."),
     li("TLS secret missing: If Ingress has TLS, referenced Secret must exist. Check `kubectl get secret <name>`."),
     li("Backend port mismatch: Ingress backend.service.port must match Service targetPort."),
     li("CiliumEnvoyConfig not generated: `kubectl get ciliumenvoyconfig -A`. Missing = controller not processing."),
     li("NetworkPolicy blocking Envoy→backend: Envoy runs in Cilium agent. CNP from 'host' entity may block.")],
    [li("Envoy OOM — too many routes", "cause-less-likely"),
     li("IngressClass not set to 'cilium'", "cause-less-likely"),
     li("DNS resolution failure in Envoy: CoreDNS slow", "cause-less-likely"),
     li("Multiple Ingress controllers conflicting", "cause-less-likely"),
     li("Envoy XDS stream broken (gRPC)", "cause-less-likely")],
    [li("ingressController.enabled not in Helm values", "cause-new-cluster"),
     li("IngressClass resource not auto-created", "cause-new-cluster"),
     li("loadBalancer.l7Backend=envoy not set", "cause-new-cluster"),
     li("RBAC missing for Ingress resources", "cause-new-cluster"),
     li("Envoy image pull failure on agent pods", "cause-new-cluster")],
    "<code>cilium status | grep Ingress</code>. <code>kubectl get ciliumenvoyconfig -A</code>. <code>kubectl describe ingress <name></code>. Note: Cilium Ingress uses embedded Envoy — no separate pod.",
    "1. Check Ingress: <code>kubectl describe ingress anihpj-web</code><br>2. Verify CEC: <code>kubectl get ciliumenvoyconfig -n anihpj</code><br>3. Envoy config: <code>kubectl exec ds/cilium -- cilium-dbg envoy config</code><br>4. Test backend: <code>curl http://anihpj-api.anihpj.svc</code> from web pod<br>5. TLS: verify cert matches hostname",
    "Cilium Ingress is simple but less feature-rich than dedicated controllers. For anihpj: great for basic L7 routing. If you need rate limiting, JWT auth, or WAF — use nginx-ingress or Istio Gateway."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm6", "SM6",
    "Gateway API — HTTPRoute Not Applying (404/No Routes)",
    "Gateway + HTTPRoute created for anihpj, but traffic gets 404. `kubectl describe httproute` shows 'Accepted: False' or 'ResolvedRefs: False'.",
    [li("Gateway API not enabled: `--set gatewayAPI.enabled=true`. Check `cilium config | grep gateway-api`."),
     li("HTTPRoute backendRef unresolved: Service must exist in same namespace (or ReferenceGrant for cross-ns)."),
     li("Gateway listener protocol mismatch: HTTPS listener won't attach HTTP routes."),
     li("Hostname mismatch: HTTPRoute hostnames must match Gateway listener hostnames."),
     li("Gateway Class not 'cilium': `kubectl get gatewayclass cilium` must exist.")],
    [li("ReferenceGrant not created for cross-namespace backends", "cause-less-likely"),
     li("HTTPRoute rule order: catch-all first blocks specific rules", "cause-less-likely"),
     li("Gateway status delay due to controller leader election", "cause-less-likely"),
     li("Gateway API CRDs not installed", "cause-less-likely"),
     li("Multiple Gateways with overlapping listeners", "cause-less-likely")],
    [li("gatewayAPI.enabled not set in Helm install", "cause-new-cluster"),
     li("Gateway API CRDs not installed: apply from upstream release", "cause-new-cluster"),
     li("GatewayClass 'cilium' not auto-created", "cause-new-cluster"),
     li("RBAC missing for gateway.networking.k8s.io", "cause-new-cluster"),
     li("Kubernetes version < 1.24", "cause-new-cluster")],
    "<code>kubectl get gateway -A</code>. <code>kubectl describe httproute <name></code>. <code>kubectl get gatewayclass cilium</code>. Gateway API = future of K8s ingress.",
    "1. Verify enabled: <code>cilium config | grep gateway-api</code><br>2. Check CRDs: <code>kubectl get crd | grep gateway.networking</code><br>3. Debug: <code>kubectl describe httproute anihpj-route -n anihpj</code><br>4. Verify backend: <code>kubectl get svc,ep -n anihpj</code><br>5. Check Gateway status conditions",
    "Gateway API is the Ingress successor — role-oriented (platform team owns Gateways, dev teams own HTTPRoutes). More expressive than Ingress. For anihpj: try Gateway API for multi-team setups."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm7", "SM7",
    "TLS Termination — Certificate Not Applied by Envoy",
    "TLS Secret created and referenced in CNP, but Hubble shows plaintext HTTP. Envoy not terminating TLS. Clients get connection reset on HTTPS.",
    [li("Secret format wrong: Must have 'tls.crt' and 'tls.key' keys in PEM. Check `kubectl get secret <name> -o jsonpath='{.data}'`."),
     li("CNP TLS rule wrong reference: `terminatingTLS.secret.name` and `.namespace` must match exactly (case-sensitive)."),
     li("Secret reused for both originating and terminating TLS: Need separate Secrets for upstream vs downstream."),
     li("Envoy cache not reloaded: Force via `kubectl delete pod -n kube-system -l k8s-app=cilium`."),
     li("Cert CN/SAN mismatch: Envoy validates SNI. If hostname doesn't match cert, TLS handshake fails.")],
    [li("Secret type not 'kubernetes.io/tls' — opaque secrets may fail detection", "cause-less-likely"),
     li("Intermediate cert missing from chain", "cause-less-likely"),
     li("Cert expired: `openssl x509 -in cert.pem -noout -dates`", "cause-less-likely"),
     li("Private key encrypted with passphrase — Envoy doesn't support", "cause-less-likely"),
     li("mTLS configured but clients not sending client certs", "cause-less-likely")],
    [li("TLS Secret never created — generate with cert-manager", "cause-new-cluster"),
     li("cert-manager not installed for auto-provisioning", "cause-new-cluster"),
     li("Let's Encrypt staging cert in production", "cause-new-cluster"),
     li("Helm `tls.secretsBackend=k8s` not set", "cause-new-cluster"),
     li("Cilium agent missing RBAC for Secret read", "cause-new-cluster")],
    "<code>kubectl get secret <tls-name> -o yaml</code>. <code>cilium-dbg envoy config | grep tls</code>. <code>openssl s_client -connect <ip>:443 -servername <host></code>. Note: Cilium TLS = Envoy-based, not eBPF.",
    "1. Verify Secret: <code>kubectl get secret anihpj-tls -n anihpj -o yaml</code><br>2. Envoy config: <code>kubectl exec ds/cilium -- cilium-dbg envoy config | grep tls</code><br>3. Test: <code>openssl s_client -connect <svc-ip>:443 -servername anihpj.example.com</code><br>4. Cert validity: decode base64 and check dates<br>5. Force reload if Secret updated",
    "TLS in Cilium is Envoy-based, getting full TLS 1.3. For anihpj: use cert-manager with Let's Encrypt, reference the auto-created Secret in CNP. terminatingTLS = downstream, originatingTLS = upstream."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm8", "SM8",
    "Canary Deployments — Traffic Split Not Working",
    "CNP with 90/10 traffic split for anihpj-api. All traffic still goes to stable. Hubble shows zero traffic to canary pods.",
    [li("Canary labels don't match: CNP toServices http header match must select canary labels. Check pod labels."),
     li("L7 policy required: Canary routing is HTTP-level. Without http rules in CNP, split won't engage."),
     li("Service selector not matching canary pods: Verify `kubectl get endpoints <svc>` includes canary pod IPs."),
     li("Weight sum not 100%: Both weights must be explicitly specified."),
     li("Hubble filter: Check `hubble observe --to-ns anihpj --http-status 200` for canary pod IPs.")],
    [li("Envoy XDS push delay: config propagation takes a few seconds", "cause-less-likely"),
     li("Cookie stickiness overriding weight routing", "cause-less-likely"),
     li("HTTP/2 multiplexing: single connection pinned to one backend", "cause-less-likely"),
     li("CiliumEndpointSlice disabled — slow backend propagation", "cause-less-likely"),
     li("Client-side DNS caching to old service IP", "cause-less-likely")],
    [li("HTTP L7 policy not configured — Envoy not engaged", "cause-new-cluster"),
     li("Canary service selector incorrect in initial deploy", "cause-new-cluster"),
     li("Traffic split configured on wrong direction (egress vs ingress)", "cause-new-cluster"),
     li("Cilium version < 1.12 (no traffic split support)", "cause-new-cluster"),
     li("loadBalancer.l7Backend=envoy not set", "cause-new-cluster")],
    "<code>kubectl get cnp -o yaml | grep -A20 http</code>. <code>cilium-dbg envoy config | grep weighted</code>. Hubble: filter to canary pod. Note: Traffic split is HTTP-only.",
    "1. Verify L7 rules: must have http section in CNP<br>2. Check canary labels: <code>kubectl get pods -l version=canary -n anihpj</code><br>3. Envoy: <code>kubectl exec ds/cilium -- cilium-dbg envoy config dump</code><br>4. Test: <code>curl -H 'X-Canary: true' http://anihpj-api.anihpj.svc</code><br>5. Monitor: <code>hubble observe --to-fqdn anihpj-api.anihpj.svc</code>",
    "Canary in Cilium = HTTP header-based routing via Envoy. For anihpj: deploy stable + canary Deployments, one Service selecting both, CNP with HTTP header match for canary. Zero-downtime deployments achieved."
))

# SM9-SM12: Bandwidth & BBR
parts.append(section_header("sm9", "📊 SM9–SM12: Bandwidth Manager & BBR"))
parts.append(ts(3, "SERVICE MESH", "🟡", "sm9", "SM9",
    "Bandwidth Manager — Rate Limiting Not Applied",
    "CNP sets egress 10Mbps for anihpj-api, but iperf3 shows unlimited throughput. No bandwidth enforcement visible in Hubble.",
    [li("Bandwidth Manager not enabled: `--set bandwidthManager.enabled=true`. Check `cilium config | grep bandwidth-manager`."),
     li("Kernel < 5.1: EDT (Earliest Departure Time) not available. `uname -r` must be ≥5.1."),
     li("BBR needs kernel ≥5.18: `--set bandwidthManager.bbr=true` fails silently below 5.18."),
     li("CNP bandwidth in wrong field: Must be under `egress[].bandwidth` — not top-level."),
     li("Interface not managed: Bandwidth attaches to devices list. Check `cilium config | grep devices`.")],
    [li("FQ pacing incompatible with tunnel mode on some kernels", "cause-less-likely"),
     li("BPF bandwidth map full — per-endpoint limit", "cause-less-likely"),
     li("TCP cwnd overriding EDT: BBR inflates beyond rate", "cause-less-likely"),
     li("iperf3 UDP bypasses EDT (TCP-only enforcement)", "cause-less-likely"),
     li("Multiple CNP bandwidth rules conflicting", "cause-less-likely")],
    [li("bandwidthManager.enabled not in Helm values", "cause-new-cluster"),
     li("Kernel too old: minimum 5.1, recommend 5.10+", "cause-new-cluster"),
     li("BBR module: `modprobe tcp_bbr; sysctl net.ipv4.tcp_congestion_control=bbr`", "cause-new-cluster"),
     li("Agent not restarted after ConfigMap change", "cause-new-cluster"),
     li("CNI chaining bypasses Cilium for egress", "cause-new-cluster")],
    "<code>cilium status | grep Bandwidth</code>. <code>tc -s qdisc show dev lxc_&lt;id&gt;</code> — look for FQ. <code>cilium-dbg bpf bandwidth list</code>. Note: Bandwidth = CNP feature, not vanilla NetworkPolicy.",
    "1. Enable: <code>cilium config set bandwidth-manager true</code><br>2. Verify: <code>cilium status | grep Bandwidth</code><br>3. EDT qdisc: <code>tc qdisc show dev lxc_&lt;id&gt;</code> — should show fq<br>4. Test: <code>kubectl exec deploy/web -- iperf3 -c anihpj-api -t 10</code><br>5. BBR: <code>sysctl net.ipv4.tcp_congestion_control=bbr</code> on all nodes",
    "Bandwidth Manager gives per-pod QoS without service mesh. For anihpj: limit batch jobs so they don't saturate NIC. Caveat: incompatible with L7 policies (same as Egress Gateway). L7 OR bandwidth — pick one."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm10", "SM10",
    "BBR Congestion Control — Not Active on Pod Traffic",
    "BBR enabled via Helm but pod-to-pod TCP still using CUBIC. `ss -ti` shows cubic not bbr. Throughput not improved for high-BDP paths.",
    [li("BBR not loaded on HOST: `sysctl net.ipv4.tcp_congestion_control` — must show 'bbr'. Set on ALL nodes."),
     li("kernel module missing: `modprobe tcp_bbr`. Check `lsmod | grep bbr`."),
     li("BBR for pods needs kernel 5.18+: Below 5.18, BBR only works on host namespace traffic, not pod traffic."),
     li("BBR only affects TCP — UDP unchanged. Verify test uses TCP."),
     li("Network path not BDP-limited: BBR shines with high bandwidth-delay product. On local 10G, CUBIC may be similar.")],
    [li("FQ qdisc missing: EDT needs fq qdisc. `tc qdisc show` on veth", "cause-less-likely"),
     li("BBR v1 vs v2: Kernel may have BBRv1 (less aggressive). Check kernel docs.", "cause-less-likely"),
     li("Container inherits wrong congestion control from init namespace", "cause-less-likely"),
     li("EBPF Host Routing disabled: affects TCP stack interaction", "cause-less-likely"),
     li("TSO/GRO offload interfering with BBR pacing", "cause-less-likely")],
    [li("BBR not enabled in Helm: `--set bandwidthManager.bbr=true` missing", "cause-new-cluster"),
     li("Kernel < 5.18: BBR for pods not supported", "cause-new-cluster"),
     li("tcp_bbr module not loaded on node startup", "cause-new-cluster"),
     li("Sysctl not persisted: /etc/sysctl.d/99-bbr.conf missing", "cause-new-cluster"),
     li("Conflicting CNI setting TCP congestion control per-pod", "cause-new-cluster")],
    "<code>sysctl net.ipv4.tcp_congestion_control</code> on HOST. <code>kubectl exec <pod> -- ss -ti</code> inside pod — check 'bbr'. <code>lsmod | grep bbr</code>. Note: pod inherits host's congestion control.",
    "1. Enable BBR on ALL nodes: <code>modprobe tcp_bbr; sysctl -w net.ipv4.tcp_congestion_control=bbr</code><br>2. Persist: <code>echo 'net.ipv4.tcp_congestion_control=bbr' > /etc/sysctl.d/99-bbr.conf</code><br>3. Verify in pod: <code>kubectl exec deploy/web -- ss -ti</code><br>4. Test: iperf3 between cross-region pods<br>5. Helm: <code>--set bandwidthManager.bbr=true</code>",
    "BBR dramatically improves throughput on high-latency links (cross-region, internet). For anihpj: if API serves clients across regions, enable BBR. But test first — BBR can be more aggressive, potentially impacting other tenants on shared links."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm11", "SM11",
    "L7 Rate Limiting — Requests Not Throttled",
    "CNP with L7 rate limit (100 req/min) for anihpj-api, but clients make 500+ req/min without throttling. Envoy config shows no rate limit filter.",
    [li("L7 rate limiting needs Envoy: Verify `cilium status | grep Proxy`. Envoy must be running for L7 features."),
     li("Rate limit in CNP must be under http rules: `toPorts[].rules.http[].headerMatches` with rate limit. Wrong placement = ignored."),
     li("Rate limit type: Cilium supports local rate limiting (per Envoy instance). Global rate limiting needs external RLS service."),
     li("Envoy config not updated: XDS push from Cilium agent to Envoy may be delayed. Force: restart Cilium agent."),
     li("Rate limit counter scoped incorrectly: Per-endpoint vs per-service. Check if counter applies to right scope.")],
    [li("Envoy rate limit filter not compiled in Cilium's Envoy build", "cause-less-likely"),
     li("Rate limit burst configuration allowing initial spike", "cause-less-likely"),
     li("Multiple Envoy instances: each has independent counter (not global)", "cause-less-likely"),
     li("HTTP/2 multiplexing: single connection may have independent rate pipe", "cause-less-likely"),
     li("Rate limit response code (429) not visible in Hubble without L7 visibility", "cause-less-likely")],
    [li("Cilium version < 1.14: L7 rate limiting added in 1.14", "cause-new-cluster"),
     li("Envoy not enabled in Helm: `--set envoy.enabled=true`", "cause-new-cluster"),
     li("CNP syntax for rate limit changed between Cilium versions", "cause-new-cluster"),
     li("Global rate limit service (RLS) not deployed for distributed limiting", "cause-new-cluster"),
     li("Monitoring: no metrics for rate limit decisions", "cause-new-cluster")],
    "<code>cilium-dbg envoy config dump | grep rate_limit</code>. <code>kubectl get cnp -o yaml | grep -A10 rateLimit</code>. Hubble: `hubble observe --http-status 429`. Note: Local rate limiting is per Envoy (per node), not cluster-wide.",
    "1. Check Envoy config: <code>kubectl exec ds/cilium -- cilium-dbg envoy config dump | grep -i rate</code><br>2. Verify CNP syntax against Cilium docs for your version<br>3. Test: <code>ab -n 200 -c 10 http://anihpj-api.anihpj.svc/</code><br>4. Look for 429 responses in Hubble<br>5. For global limits: deploy external Rate Limit Service (RLS)",
    "Cilium's local rate limiting is per-Envoy-instance (per-node). For anihpj with 3 nodes: 100 req/min limit = 300 req/min total cluster-wide. For true global limiting, integrate an external RLS. Most use cases: local limiting is sufficient."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm12", "SM12",
    "Sidecar-Free Mesh — Pod-to-Pod mTLS Without Sidecar",
    "Mutual TLS configured via Cilium (no sidecar), but pods communicate over plaintext. Hubble shows no TLS handshake. WireGuard/IPSec may be working but not per-pod mTLS.",
    [li("Cilium transparent encryption is NODE-level (WireGuard/IPSec), not per-pod mTLS. Pod-to-pod mTLS requires Envoy proxy with originatingTLS in CNP."),
     li("mTLS needs L7 CNP: Without L7 rules, Envoy not engaged. Add http rule to trigger Envoy for mTLS."),
     li("Certificate provisioning: Both originatingTLS and terminatingTLS secrets needed — one for client cert, one for server cert."),
     li("SPIFFE not integrated: Cilium doesn't auto-issue per-pod certs. Cert-manager or manual provisioning needed."),
     li("Hubble TLS visibility: Without L7 visibility enabled, TLS handshake not visible in flow logs.")],
    [li("Envoy TLS context configured but cipher mismatch between client/server", "cause-less-likely"),
     li("Certificate chain incomplete for mutual validation", "cause-less-likely"),
     li("mTLS only for specific ports — non-matching traffic goes plaintext", "cause-less-likely"),
     li("CRL/OCSP check failing in Envoy", "cause-less-likely"),
     li("Session resumption tickets not configured — new TLS per request", "cause-less-likely")],
    [li("Confusing WireGuard encryption with per-pod mTLS — they're different", "cause-new-cluster"),
     li("No SPIFFE/SPIRE integration for auto-cert rotation", "cause-new-cluster"),
     li("CNP missing both originatingTLS AND terminatingTLS sections", "cause-new-cluster"),
     li("cert-manager not configured for per-pod certificates", "cause-new-cluster"),
     li("Expecting automatic mTLS like Istio — Cilium requires explicit CNP TLS rules", "cause-new-cluster")],
    "<code>cilium encrypt status</code> — shows node-level encryption. For pod-level TLS: <code>cilium-dbg envoy config | grep tls_context</code>. Hubble: enable L7 visibility. Note: Cilium sidecar-free mesh = you manage certs, Cilium enforces in Envoy.",
    "1. Understand: Cilium transparent encryption (WireGuard/IPSec) ≠ per-pod mTLS<br>2. For mTLS: create CNP with both terminatingTLS and originatingTLS<br>3. Provision certs via cert-manager for both client and server<br>4. Enable L7 visibility: <code>hubble observe --http-status 200</code> for TLS flows<br>5. Monitor: <code>cilium-dbg envoy config dump | grep tls</code>",
    "Cilium's 'sidecar-free mesh' means you get Envoy proxy functionality WITHOUT sidecar injection. But you still need to configure TLS explicitly in CNP — it's not automatic like Istio. For anihpj: if you need full auto-mTLS with SPIFFE, Istio + Cilium is a powerful combo."
))

# SM13-SM16: Sidecar-Free Mesh Deep Dive & Service Mesh Integration
parts.append(section_header("sm13", "🔗 SM13–SM16: Service Mesh Integration & Advanced L7"))
parts.append(ts(3, "SERVICE MESH", "🟡", "sm13", "SM13",
    "Cilium + Istio Integration — Conflicting L7 Policies",
    "Both CiliumNetworkPolicy and Istio DestinationRule/VirtualService configured for anihpj-api. Traffic behaves unexpectedly — sometimes routed by Istio, sometimes by Cilium. 503 errors intermittent.",
    [li("Double proxy hop: Cilium Envoy + Istio sidecar = two proxies. Traffic goes: pod→Cilium Envoy→Istio sidecar→app. L7 policies may conflict."),
     li("Cilium L7 policy bypasses Istio: If CNP has L7 http rules, Cilium Envoy intercepts BEFORE Istio sidecar. Istio mTLS may break."),
     li("Port conflict: Both Cilium and Istio may try to intercept same port. Check which proxy gets the traffic first."),
     li("Cilium in socket-LB mode skips all proxies — Istio sidecar never sees traffic."),
     li("Identity mismatch: Cilium uses numeric identity, Istio uses SPIFFE. Cross-referencing fails.")],
    [li("Istio's iptables rules redirecting traffic after Cilium eBPF processed it", "cause-less-likely"),
     li("Cilium Envoy and Istio sidecar sharing same port namespace", "cause-less-likely"),
     li("CiliumEndpoint identity not propagated to Istio's SPIFFE", "cause-less-likely"),
     li("DNS resolution: Cilium DNS proxy intercepting before Istio's DNS capture", "cause-less-likely"),
     li("Certificate chain: Cilium terminating TLS before Istio's mTLS", "cause-less-likely")],
    [li("Both Cilium and Istio installed without coordination: default configs conflict", "cause-new-cluster"),
     li("Cilium L7 CNP created without knowing Istio is deployed", "cause-new-cluster"),
     li("Mesh configuration not documented in deployment runbook", "cause-new-cluster"),
     li("No clear ownership: platform team manages Cilium, app team manages Istio", "cause-new-cluster"),
     li("cilium config set policy-enforcement-mode=always with Istio", "cause-new-cluster")],
    "<code>cilium status | grep Proxy</code> + <code>istioctl proxy-status</code>. Hubble: trace one request through all hops. <code>kubectl exec <pod> -c istio-proxy -- pilot-agent request GET /config_dump</code>. Rule: Cilium L3/L4 + Istio L7 = best combo.",
    "1. Simplify: Use Cilium for L3/L4 (NetworkPolicy, encryption), Istio for L7 (routing, retries, mTLS)<br>2. Remove L7 rules from CNP — let Istio handle HTTP routing<br>3. Disable Cilium Envoy if using Istio: `--set envoy.enabled=false`<br>4. Verify traffic path: `hubble observe --from-pod web --to-pod api`<br>5. Test: `istioctl authn tls-check <pod-name>` for mTLS verification",
    "Cilium + Istio = powerful but tricky. Best practice: Cilium handles networking (L3/L4, WireGuard, BGP, observability), Istio handles service mesh (L7 routing, mTLS, canary, fault injection). Avoid L7 in Cilium if Istio is your mesh. For anihpj: start with Cilium-only, add Istio only when you need mesh features."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm14", "SM14",
    "CiliumEnvoyConfig (CEC) — Custom Envoy Configuration Not Loading",
    "Custom CiliumEnvoyConfig resource created for anihpj-api with specific Envoy filters, but Envoy not loading the config. `cilium-dbg envoy config` shows default config only.",
    [li("CEC spec format invalid: Envoy config must be valid JSON in `spec.resources[]`. Check `kubectl describe cec <name>` for validation errors."),
     li("CEC not associated with correct endpoint: `spec.services[].namespace/name` must match an existing Service. If service selector doesn't match any pod, CEC is orphaned."),
     li("CEC gRPC timeout: Envoy fetches config via xDS from Cilium agent. If agent is busy, xDS stream may timeout."),
     li("Multiple CECs conflict: Only one CEC per service direction. Check for duplicate CECs targeting the same service."),
     li("Cilium agent not watching CEC CRD: Check agent logs for CEC processing errors: `kubectl logs ds/cilium | grep CEC`.")],
    [li("Envoy config type URL not supported by Cilium's Envoy version", "cause-less-likely"),
     li("CEC too large: Envoy config > 100KB may hit xDS message size limit", "cause-less-likely"),
     li("Envoy rejecting config due to unknown filter/plugin", "cause-less-likely"),
     li("Cilium agent xDS cache not invalidated after CEC update", "cause-less-likely"),
     li("CEC status conditions not updated (stale status)", "cause-less-likely")],
    [li("CEC CRD schema not installed with Cilium: should auto-install", "cause-new-cluster"),
     li("CEC feature not enabled: needs Envoy proxy enabled", "cause-new-cluster"),
     li("CEC created before Service exists: retroactive association may not happen", "cause-new-cluster"),
     li("Node-local Envoy not available: agent uses per-node Envoy", "cause-new-cluster"),
     li("RBAC: Cilium agent can't read CEC resources", "cause-new-cluster")],
    "<code>kubectl get cec -A</code>. <code>kubectl describe cec <name></code>. <code>cilium-dbg envoy config dump</code> — compare with CEC content. <code>kubectl logs ds/cilium | grep -i 'envoy\|cec\|xds'</code>.",
    "1. Validate CEC: <code>kubectl describe cec <name> -n anihpj</code><br>2. Check Cilium agent logs: <code>kubectl logs ds/cilium --tail=100 | grep -i cec</code><br>3. Verify service: <code>kubectl get svc,ep anihpj-api -n anihpj</code><br>4. Check Envoy: <code>kubectl exec ds/cilium -- cilium-dbg envoy config dump</code><br>5. Simplify: start with minimal valid CEC, then add complexity",
    "CEC gives you full Envoy power without running a separate Envoy deployment. For anihpj: use CEC for advanced scenarios like JWT validation, custom rate limiting, or WebSocket upgrades that CNP can't express. But start with CNP — it covers 90% of use cases."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm15", "SM15",
    "gRPC Load Balancing — Sticky to Single Backend",
    "gRPC client connecting to anihpj-api-grpc service always hits same backend. All gRPC streams go to one pod. Other backends idle. Scaling doesn't distribute load.",
    [li("gRPC uses HTTP/2 single connection: All streams multiplexed on ONE TCP connection. L4 load balancing happens at connection setup, not per-stream."),
     li("No L7 policy for gRPC: Cilium needs L7 rules to see gRPC streams. Without L7, only connection-level LB."),
     li("Client-side load balancing not configured: gRPC clients should use round_robin or grpclb resolver. Default is 'pick first'."),
     li("Connection keepalive too long: gRPC connections stay open indefinitely. Set `GRPC_ARG_KEEPALIVE_TIME_MS` for rotation."),
     li("Maglev (L4) not effective for gRPC: Consistent hashing maps ONE connection to ONE backend. Same hash = same backend always.")],
    [li("HTTP/2 GOAWAY not sent by server to force reconnection", "cause-less-likely"),
     li("gRPC channel not refreshing DNS resolution (cached forever)", "cause-less-likely"),
     li("Envoy not recognizing gRPC traffic as HTTP/2 distinct streams", "cause-less-likely"),
     li("Max concurrent streams setting too high on server preventing rotation", "cause-less-likely"),
     li("Cilium socket LB not supporting HTTP/2 multiplex detection", "cause-less-likely")],
    [li("gRPC service deployed without L7 policy — only L4 (connection-level) balancing", "cause-new-cluster"),
     li("Client using default gRPC load balancing (pick-first) instead of round_robin", "cause-new-cluster"),
     li("No service mesh for gRPC-aware routing", "cause-new-cluster"),
     li("Kubernetes Service type ClusterIP doesn't help with gRPC L7", "cause-new-cluster"),
     li("No headless service for client-side discovery", "cause-new-cluster")],
    "<code>hubble observe --to-port 50051 --protocol gRPC</code> — check per-stream distribution. Client: <code>GRPC_GO_LOG_SEVERITY_LEVEL=info</code>. gRPC needs L7 or client-side LB — L4 alone can't do it.",
    "1. Enable L7 policy for gRPC port in CNP<br>2. Configure client: use `grpc.WithDefaultServiceConfig('{\"loadBalancingPolicy\":\"round_robin\"}')`<br>3. Or: use headless service + client-side DNS resolution<br>4. Consider: `dns:///anihpj-api-grpc.anihpj.svc:50051` with round_robin<br>5. Alternative: deploy Envoy proxy as gRPC-aware LB in front",
    "gRPC + Kubernetes + Cilium requires specific design. For anihpj: if using gRPC, either (a) client-side round_robin with headless service, or (b) deploy a gRPC proxy like Envoy with proper L7 config. Don't expect ClusterIP to magically balance gRPC — it can't see inside HTTP/2."
))

parts.append(ts(3, "SERVICE MESH", "🟡", "sm16", "SM16",
    "HTTP/3 QUIC — Not Supported or Falling Back to TCP",
    "QUIC/HTTP3 enabled on anihpj-api, but Cilium policy enforcement breaks QUIC. Clients fall back to TCP. QUIC packets appear as DROPPED in Hubble.",
    [li("QUIC uses UDP 443: Cilium L7 policies work on TCP. If your CNP only has TCP rules, UDP/QUIC is not inspected — may be dropped by default-deny."),
     li("Cilium L7 proxy (Envoy) doesn't support QUIC: All L7 inspection is TCP-based. QUIC bypasses Envoy entirely."),
     li("UDP port not allowed in CNP: Add `toPorts[].ports[].protocol: UDP` with port 443 to allow QUIC through."),
     li("Connection tracking for QUIC: Cilium's conntrack may not track QUIC connection migration. Connection ID changes break state."),
     li("Kernel UDP GRO/GSR: QUIC performance limited without kernel support. Check kernel version for UDP optimizations.")],
    [li("QUIC version negotiation blocked by Cilium as unknown UDP", "cause-less-likely"),
     li("0-RTT data dropped by conntrack as invalid state", "cause-less-likely"),
     li("QUIC connection migration (IP change) breaks conntrack", "cause-less-likely"),
     li("UDP fragmentation with QUIC large packets blocked", "cause-less-likely"),
     li("Cilium DNS proxy intercepting QUIC SNI for domain filtering", "cause-less-likely")],
    [li("QUIC deployed without UDP rules in CNP", "cause-new-cluster"),
     li("Default-deny CiliumNetworkPolicy blocking all UDP", "cause-new-cluster"),
     li("L7 CNP created for HTTP but QUIC is UDP-based", "cause-new-cluster"),
     li("No awareness that Cilium L7 = TCP-only", "cause-new-cluster"),
     li("QUIC enabled on app but network not configured for UDP 443", "cause-new-cluster")],
    "<code>hubble observe --protocol UDP --to-port 443 --verdict DROPPED</code>. Check CNP: any UDP 443 rule? Note: Cilium L7 (HTTP rules, TLS termination) is TCP-only. QUIC/UDP = L4 only in Cilium.",
    "1. Add UDP 443 rule in CNP: `toPorts: [{ports: [{port: '443', protocol: UDP}]}]`<br>2. Accept: L7 inspection won't work on QUIC — only L4 allow/deny<br>3. For L7 on QUIC: terminate QUIC at a dedicated LB (Envoy with QUIC support)<br>4. Test: `hubble observe --protocol UDP --to-port 443`<br>5. Monitor fallback: check if clients fall back to TCP (HTTP/2)",
    "QUIC + Cilium = L4 only for now. Cilium's Envoy may support QUIC inspection in future, but today you get basic UDP allow/deny. For anihpj: if you need QUIC + L7 policies, terminate QUIC at an external LB, then forward as TCP to Cilium-managed backend."
))

# =============================================================================
# Write a test marker to verify the script structure
# =============================================================================
print("Generated CAT3: SM1-SM16")
print("Total parts:", len(parts))
print("First part preview:", parts[0][:100])
print("...")
print("Last part preview:", parts[-1][:100])
