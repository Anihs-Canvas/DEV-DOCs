#!/usr/bin/env python3
"""Insert ALL missing troubleshooting issues (Cats 3-8) into cilium-test-prep.html.
Compact format — all 62 issues generated and inserted in one pass."""

HTML = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

# =====================================================================
# HELPER: Quick TS issue template (compact)
# =====================================================================
def LI(t, c="cause-likely"): return f'<li><span class="{c}">{t}</span></li>'

def TS(cat, cn, color, iid, title, symp, ml, ll, nc, look, sol, adv, diag=""):
    return f'''    <div class="ts-issue" id="ts-{iid}-detail">
        <div class="ts-issue-header"><div class="ts-issue-num">{iid.upper()}</div><div class="ts-issue-header-content">
                <div class="ts-category">{color} CATEGORY {cat}: {cn} — Issue {iid.upper()}</div>
                <div class="ts-title">{title}</div>
                <p class="ts-symptom"><strong>🔍 Symptom:</strong> {symp}</p></div></div>{diag}
        <div class="ts-causes-grid">
            <div class="cause-card most-likely"><div class="cause-card-header"><span class="cause-icon">🔴</span><span class="cause-label">5 Most Likely Causes</span></div><ol>{"".join(ml)}</ol></div>
            <div class="cause-card less-likely"><div class="cause-card-header"><span class="cause-icon">🟡</span><span class="cause-label">5 Less Likely Causes</span></div><ol>{"".join(ll)}</ol></div>
            <div class="cause-card new-cluster"><div class="cause-card-header"><span class="cause-icon">🟣</span><span class="cause-label">5 New Cluster Causes</span></div><ol>{"".join(nc)}</ol></div></div>
        <div class="ts-lookat"><strong>🔍 What to Look At / Take Note Of:</strong> {look}</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong><p>{sol}</p></div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> {adv}</div>
        <div class="ts-footer-spacer"></div></div>'''

def SH(iid, title): return f'    <div class="ts-section-header" id="ts-{iid}"><h3>{title}</h3></div>\n'

# =====================================================================
# CATEGORY 3: SERVICE MESH (SM1-SM16)
# =====================================================================
cat3 = SH("sm1", "🔀 SM1–SM4: Kube-Proxy Replacement &amp; Load Balancing")
cat3 += TS(3, "SERVICE MESH", "🟡", "sm1", "KPR Not Working — Services Unreachable",
    "anihpj-api ClusterIP unreachable. NodePort broken. kube-proxy was supposed to be replaced by Cilium eBPF.",
    [LI("kubeProxyReplacement not strict: `cilium config | grep kube-proxy-replacement` must be 'strict'. Helm: `--set kubeProxyReplacement=strict`."), LI("Native devices unspecified: `--set devices=eth0` missing. NodePort can't bind to host interfaces."), LI("kube-proxy DaemonSet still running: `kubectl get pods -n kube-system -l k8s-app=kube-proxy`. Delete it."), LI("BPF NodePort not loaded: `cilium status | grep KubeProxyReplacement` should show 'Strict (Kernel)'."), LI("Kernel < 5.10: Strict KPR needs 5.10+. `uname -r`.")],
    [LI("iptables KUBE-SERVICES rules from old kube-proxy persist", "cause-less-likely"), LI("Race: Cilium started before kube-proxy fully removed", "cause-less-likely"), LI("NodePort range conflicts with host port bindings", "cause-less-likely"), LI("BPF lb4_services map exhausted", "cause-less-likely"), LI("IPv6 DAD delaying service IP assignment", "cause-less-likely")],
    [LI("kubeProxyReplacement never set: default=disabled", "cause-new-cluster"), LI("Helm without devices: `--set devices='{eth0}'`", "cause-new-cluster"), LI("cilium-operator not assigning node addresses", "cause-new-cluster"), LI("RBAC missing for Services/Endpoints watch", "cause-new-cluster"), LI("kube-proxy config still iptables mode in kubeadm", "cause-new-cluster")],
    "`cilium status | grep KubeProxyReplacement` — must show 'Strict (Kernel)'. `cilium service list` — backends present? `kubectl get pods -n kube-system | grep kube-proxy` — must be empty. `iptables -t nat -L KUBE-SERVICES` — should show Cilium rules.",
    "1. `cilium config view | grep kube-proxy-replacement`<br>2. `kubectl delete ds -n kube-system kube-proxy` (if running)<br>3. `cilium config set kube-proxy-replacement strict` or Helm upgrade<br>4. `kubectl -n kube-system rollout restart ds/cilium`<br>5. `cilium connectivity test` — all service tests must pass",
    "KPR replaces thousands of iptables rules with one BPF map lookup. For anihpj: always go strict if kernel ≥5.10. Verify with `curl http://anihpj-api.anihpj.svc` from web pod."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm2", "Maglev Backend Imbalance",
    "anihpj-api with 5 backends: Pod-1 gets 45%, Pod-5 gets 5%. Hubble confirms skew. Connections sticky to same backend.",
    [LI("Maglev table M too small: M=65537 default. M/N hash collisions cause imbalance. `cilium service list`."), LI("TCP connection stickiness: Long-lived connections stay on one backend — expected, not a bug."), LI("Backend weight misconfigured: `cilium service get <id>` — check weights."), LI("Maglev hash collision: Rare — two backends hash to overlapping slot ranges."), LI("Unequal backend capacity: CPU throttled pods process fewer requests.")],
    [LI("Cilium version mismatch → different Maglev tables per node", "cause-less-likely"), LI("Node-local preference (service affinity not 'none')", "cause-less-likely"), LI("Stale eBPF map entries after scale-down", "cause-less-likely"), LI("Maglev permutation corruption from concurrent updates", "cause-less-likely"), LI("Kernel entropy depleted affecting hash distribution", "cause-less-likely")],
    [LI("Default Maglev table not tuned for backend count", "cause-new-cluster"), LI("Service created before all backends ready", "cause-new-cluster"), LI("externalTrafficPolicy:Local restricting NodePort", "cause-new-cluster"), LI("Topology-aware routing restricting backends", "cause-new-cluster"), LI("CiliumEndpointSlice not enabled", "cause-new-cluster")],
    "`cilium service list` — backend counts/weights. `cilium bpf lb list` — Maglev slots per backend. Hubble: `hubble observe --to-service anihpj/anihpj-api`. ±15% variation is normal with 5 backends. Maglev = consistent hashing, minimizes disruption on backend changes.",
    "1. `hubble observe --to-service anihpj/anihpj-api --output json | jq 'group_by(.destination_pod)'`<br>2. `cilium bpf lb list` to see Maglev distribution<br>3. For gRPC/HTTP2: use L7 routing for per-request balancing<br>4. `cilium config set maglev-table-size 655373` for larger M<br>5. Verify no weight annotations on endpoints",
    "Maglev gives you ~±15% variation with 5 backends — that's normal. When a backend dies, only connections to THAT backend shift — not all. For anihpj: if 50%+ skew, check for restarting pods skewing the hash distribution."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm3", "Socket LB Fails — L7 Proxy Bypass Conflict",
    "Socket LB enabled but HTTP not balanced. L7 policies not enforced. Hubble shows direct pod-to-pod without Envoy proxy hop.",
    [LI("Socket LB auto-disabled by L7 policies: Any CNP with http rules DISABLES socket LB for that endpoint."), LI("Socket LB needs non-hostNetwork pods: hostNetwork bypasses socket hooks."), LI("Cilium agent flag: `cilium config | grep socket-lb` must be 'true'."), LI("Kernel < 5.7: socket LB needs 5.7+ for full cgroup hooks."), LI("App uses non-standard socket calls (sendmmsg, custom ops) that bypass BPF hooks.")],
    [LI("BPF sockmap full — max entries reached", "cause-less-likely"), LI("Cgroup v2 not enabled: `grep cgroup2 /proc/filesystems`", "cause-less-likely"), LI("Socket buffer mismatch causing partial reads", "cause-less-likely"), LI("TCP_NODELAY interfering with BPF hooks", "cause-less-likely"), LI("Cgroup hierarchy permissions blocking socket attach", "cause-less-likely")],
    [LI("socketLB.enabled not in Helm values on install", "cause-new-cluster"), LI("Cgroup v2 not default: containerd `SystemdCgroup=true`", "cause-new-cluster"), LI("Agent not restarted after enabling socket LB", "cause-new-cluster"), LI("AppArmor/SELinux blocking BPF socket ops", "cause-new-cluster"), LI("socketLB.hostNamespaceOnly=true but pod not hostNetwork", "cause-new-cluster")],
    "`cilium config | grep socket-lb`. `grep cgroup2 /proc/filesystems`. CRITICAL: socket LB auto-disables when L7 policies exist. Check your CNP first! Socket LB = L4 only, sub-microsecond latency. L7 = Envoy proxy. You CAN'T have both on same endpoint.",
    "1. Check L7 policies: `kubectl get cnp -A | grep -i http`<br>2. `cilium config | grep socket-lb`<br>3. Remove L7 rules if you want socket LB speed<br>4. Or accept Envoy proxy if you need L7 features<br>5. `cilium bpf lb list --socket` to verify socket-level backends",
    "Socket LB = fast L4, no Envoy overhead. L7 policies = Envoy proxy. Tradeoff: speed vs features. For anihpj: if you just need L4 round-robin, socket LB is faster. If you need HTTP path routing or header inspection, use L7 CNP (and accept the proxy hop)."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm4", "DSR — Asymmetric Routing Breaks Connections",
    "DSR mode on but reply traffic bypasses Cilium. Hubble: forward only, no reverse. Clients see connection timeouts.",
    [LI("DSR needs tunnel (IPIP/Geneve): `ip link show cilium_geneve` — must be UP on ALL nodes."), LI("VIP missing on backend lo: `ip addr show lo | grep <VIP>`. DSR requires VIP on backend's loopback."), LI("rp_filter dropping: `sysctl net.ipv4.conf.all.rp_filter=0` on all backend nodes."), LI("Client not reachable from backend: DSR bypasses original path — backend needs direct route to client."), LI("KPR must be strict: `cilium config | grep kube-proxy-replacement` = 'strict'.")],
    [LI("MTU: IPIP +20 bytes. Path MTU < 1520 causes fragmentation", "cause-less-likely"), LI("Conntrack creating asymmetric flows on backend", "cause-less-likely"), LI("ARP responder for VIP missing on backend node", "cause-less-likely"), LI("Cilium health reports DSR disabled at runtime", "cause-less-likely"), LI("Network ACL blocking backend→client direct path", "cause-less-likely")],
    [LI("DSR not enabled: `--set loadBalancer.mode=dsr` missing", "cause-new-cluster"), LI("Tunnel protocol not specified", "cause-new-cluster"), LI("Cloud LB health checks fail (DSR bypasses LB return)", "cause-new-cluster"), LI("NodePort DSR inconsistent with ClusterIP DSR", "cause-new-cluster"), LI("KPR not strict: DSR needs full replacement", "cause-new-cluster")],
    "`cilium config | grep -E 'dsr|tunnel|kube-proxy'`. `ip link show | grep geneve`. Backend: `ip addr show lo` — VIP present? `sysctl net.ipv4.conf.all.rp_filter` — must be 0. DSR = backend replies directly to client, bypassing Cilium node entirely. Only for high-throughput scenarios.",
    "1. `cilium config | grep dsr` — must be 'true'<br>2. `ip link show cilium_geneve` on all nodes<br>3. `sysctl -w net.ipv4.conf.all.rp_filter=0` on backends<br>4. `ip addr add <VIP>/32 dev lo` on backend node<br>5. `tcpdump -i any host <client-ip>` — verify direct return",
    "DSR = ultimate performance. Backends reply directly to clients. But complex: VIP on loopback, rp_filter disabled, tunnel required. For anihpj: unless 100K+ req/s with large responses, stay with SNAT mode. DSR shines for video streaming."
)

# SM5-SM8: Ingress & Gateway API
cat3 += SH("sm5", "🚪 SM5–SM8: Ingress &amp; Gateway API")
cat3 += TS(3, "SERVICE MESH", "🟡", "sm5", "Cilium Ingress — 503 Backend Unavailable",
    "anihpj-web Ingress returns 503. `kubectl describe ingress` shows 'no healthy backends'. Pods Running, endpoints exist.",
    [LI("Ingress controller not enabled: `cilium config | grep ingress-controller` or `--set ingressController.enabled=true`."), LI("TLS secret missing: if Ingress has TLS, Secret must exist. `kubectl get secret <name>`."), LI("Backend port mismatch: Ingress backend port must match Service targetPort, not just port."), LI("CiliumEnvoyConfig not auto-generated: `kubectl get ciliumenvoyconfig -A`. Missing = controller not processing."), LI("CNP blocking Envoy→backend: Envoy runs in Cilium agent. 'host' entity CNP may block the proxy-to-pod path.")],
    [LI("Envoy OOM — too many routes causing mem exhaustion", "cause-less-likely"), LI("IngressClass not 'cilium' and no default", "cause-less-likely"), LI("DNS resolution in Envoy timing out (CoreDNS slow)", "cause-less-likely"), LI("Multiple ingress controllers conflicting", "cause-less-likely"), LI("Envoy XDS gRPC stream broken to agent", "cause-less-likely")],
    [LI("ingressController.enabled not in Helm values", "cause-new-cluster"), LI("IngressClass resource not auto-created", "cause-new-cluster"), LI("loadBalancer.l7Backend=envoy not set", "cause-new-cluster"), LI("RBAC missing for Ingress resources", "cause-new-cluster"), LI("Envoy image pull failure on agent pods", "cause-new-cluster")],
    "`cilium status | grep Ingress`. `kubectl get ciliumenvoyconfig -n anihpj`. `cilium-dbg envoy config`. `kubectl describe ingress anihpj-web`. Cilium Ingress uses embedded Envoy (no separate ingress pod).",
    "1. `kubectl describe ingress anihpj-web`<br>2. `kubectl get ciliumenvoyconfig -n anihpj`<br>3. `kubectl exec ds/cilium -- cilium-dbg envoy config | grep -A20 anihpj`<br>4. Test backend directly: `curl http://anihpj-api.anihpj.svc` from web pod<br>5. TLS: verify cert CN matches hostname",
    "Cilium Ingress is simpler than deploying nginx/haproxy separately. For anihpj: great for basic L7 routing. Need rate limiting, JWT, WAF? Use nginx-ingress or Istio Gateway."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm6", "Gateway API — HTTPRoute 404/Not Accepted",
    "Gateway + HTTPRoute created for anihpj. Traffic gets 404. `kubectl describe httproute` shows 'Accepted: False'.",
    [LI("Gateway API not enabled: `--set gatewayAPI.enabled=true`. `cilium config | grep gateway-api`."), LI("HTTPRoute backendRef unresolved: referenced Service must exist in same namespace (or ReferenceGrant)."), LI("Listener protocol mismatch: HTTPS listener won't attach HTTP routes."), LI("Hostname mismatch: HTTPRoute hostnames must match Gateway listener hostnames exactly."), LI("GatewayClass not 'cilium': `kubectl get gatewayclass cilium` must exist.")],
    [LI("ReferenceGrant not created for cross-namespace backends", "cause-less-likely"), LI("HTTPRoute rule order: catch-all first blocks specific", "cause-less-likely"), LI("Gateway status delay from leader election", "cause-less-likely"), LI("Gateway API CRDs not installed", "cause-less-likely"), LI("Multiple Gateways with overlapping listeners", "cause-less-likely")],
    [LI("gatewayAPI.enabled not in Helm values", "cause-new-cluster"), LI("Gateway API CRDs not applied to cluster", "cause-new-cluster"), LI("GatewayClass 'cilium' not auto-created by Helm", "cause-new-cluster"), LI("RBAC missing for gateway.networking.k8s.io", "cause-new-cluster"), LI("K8s version < 1.24 for Gateway API", "cause-new-cluster")],
    "`kubectl get gateway -A`. `kubectl describe httproute <name>`. `kubectl get gatewayclass cilium`. Gateway API = Ingress successor, role-oriented (platform team owns Gateways, dev teams own HTTPRoutes).",
    "1. `cilium config | grep gateway-api` — verify enabled<br>2. `kubectl get crd | grep gateway.networking`<br>3. `kubectl describe httproute anihpj-route -n anihpj`<br>4. `kubectl get svc,ep -n anihpj | grep <backend>`<br>5. Check Gateway conditions: `kubectl describe gateway anihpj-gw`",
    "Gateway API is more expressive than Ingress. For anihpj: try both — Ingress is simpler, Gateway API is more powerful for multi-team setups with shared gateways and per-team routes."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm7", "TLS Termination — Certificate Not Applied",
    "TLS Secret referenced in CNP but Hubble shows plaintext HTTP. Envoy not terminating TLS. HTTPS clients get connection reset.",
    [LI("Secret format: must have 'tls.crt' and 'tls.key' in PEM. `kubectl get secret <name> -o jsonpath='{.data}' | base64 -d`."), LI("CNP TLS rule wrong: `terminatingTLS.secret.name` and `.namespace` must match exactly (case-sensitive)."), LI("Same Secret for originating+terminating: need separate Secrets for upstream vs downstream TLS."), LI("Envoy cache stale: force reload via `kubectl delete pod -n kube-system -l k8s-app=cilium`."), LI("Cert CN/SAN mismatch: Envoy validates SNI. Hostname must match certificate.")],
    [LI("Secret type not kubernetes.io/tls", "cause-less-likely"), LI("Intermediate cert missing from full chain", "cause-less-likely"), LI("Cert expired: `openssl x509 -in cert.pem -noout -dates`", "cause-less-likely"), LI("Private key encrypted with passphrase (Envoy can't handle)", "cause-less-likely"), LI("mTLS configured but clients not sending client certs", "cause-less-likely")],
    [LI("TLS Secret never created: forgot to generate cert", "cause-new-cluster"), LI("cert-manager not installed for auto-provisioning", "cause-new-cluster"), LI("Let's Encrypt staging cert used in production", "cause-new-cluster"), LI("Helm tls.secretsBackend not set", "cause-new-cluster"), LI("Cilium agent RBAC missing for Secret read", "cause-new-cluster")],
    "`kubectl get secret <name> -o yaml`. `cilium-dbg envoy config | grep tls_context`. `openssl s_client -connect <ip>:443 -servername <host>`. Cilium TLS = Envoy-based, not eBPF. Full TLS 1.3 support.",
    "1. Verify Secret: `kubectl get secret anihpj-tls -n anihpj -o yaml`<br>2. `kubectl exec ds/cilium -- cilium-dbg envoy config | grep tls`<br>3. `openssl s_client -connect <svc-ip>:443 -servername anihpj.example.com`<br>4. Decode cert: check expiry and CN<br>5. Force Envoy reload if Secret was updated",
    "Cilium TLS via Envoy gives you full TLS 1.3. For anihpj: use cert-manager + Let's Encrypt for auto-provisioning. terminatingTLS = downstream (client→service). originatingTLS = upstream (service→backend)."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm8", "Canary Traffic Split Not Working",
    "CNP 90/10 split for anihpj-api. All traffic to stable. Hubble: zero traffic to canary pods.",
    [LI("Canary labels mismatch: CNP toServices http header match must select canary labels. Check pod labels vs CNP selector."), LI("L7 policy required: canary routing is HTTP-level. Without http rules in CNP, split won't engage."), LI("Service not selecting canary: `kubectl get endpoints <svc>` — must include canary pod IPs."), LI("Weights not specified or sum != 100."), LI("Hubble filter: `hubble observe --to-pod anihpj/canary-api` — verify traffic arriving at canary pod.")],
    [LI("Envoy XDS push delayed (few seconds normal)", "cause-less-likely"), LI("Cookie stickiness overriding weight routing", "cause-less-likely"), LI("HTTP/2 single connection pinned to one backend", "cause-less-likely"), LI("CiliumEndpointSlice disabled — slow propagation", "cause-less-likely"), LI("Client DNS caching to old service IP", "cause-less-likely")],
    [LI("L7 http rules not in CNP — Envoy not engaged", "cause-new-cluster"), LI("Canary service selector wrong from first deploy", "cause-new-cluster"), LI("Traffic split on wrong direction", "cause-new-cluster"), LI("Cilium < 1.12 (no traffic split)", "cause-new-cluster"), LI("loadBalancer.l7Backend=envoy not set", "cause-new-cluster")],
    "`kubectl get cnp -o yaml | grep -A20 http`. `cilium-dbg envoy config | grep weighted`. Hubble: `hubble observe --to-fqdn anihpj-api.anihpj.svc`. Canary = HTTP header-based routing via Envoy.",
    "1. Verify L7 rules: CNP must have http section<br>2. `kubectl get pods -l version=canary -n anihpj`<br>3. `kubectl exec ds/cilium -- cilium-dbg envoy config dump | grep weighted`<br>4. Direct canary test: `curl -H 'X-Canary: true' http://anihpj-api.anihpj.svc`<br>5. `hubble observe --to-fqdn anihpj-api.anihpj.svc`",
    "Canary in Cilium = zero-downtime deployments. For anihpj: deploy stable + canary Deployments, one Service selecting both, CNP with HTTP header match. Start with 5% canary, monitor errors, ramp to 100%."
)

# SM9-SM12: Bandwidth & BBR
cat3 += SH("sm9", "📊 SM9–SM12: Bandwidth Manager &amp; BBR")
cat3 += TS(3, "SERVICE MESH", "🟡", "sm9", "Bandwidth Manager — Rate Limiting Not Applied",
    "CNP egress 10Mbps for anihpj-api, but iperf3 shows unlimited. No bandwidth enforcement in Hubble.",
    [LI("Bandwidth Manager not enabled: `--set bandwidthManager.enabled=true`. `cilium config | grep bandwidth-manager`."), LI("Kernel < 5.1: EDT not available. `uname -r`."), LI("BBR needs 5.18+: `--set bandwidthManager.bbr=true` fails silently."), LI("CNP bandwidth in wrong field: must be `egress[].bandwidth`, not top-level."), LI("Interface not in devices list: `cilium config | grep devices`.")],
    [LI("FQ pacing + tunnel mode incompatible on some kernels", "cause-less-likely"), LI("BPF bandwidth map exhausted", "cause-less-likely"), LI("TCP cwnd overriding EDT: BBR inflates beyond limit", "cause-less-likely"), LI("iperf3 UDP bypasses EDT (TCP-only)", "cause-less-likely"), LI("Multiple CNP bandwidth rules conflict", "cause-less-likely")],
    [LI("bandwidthManager.enabled not in Helm values", "cause-new-cluster"), LI("Kernel too old: min 5.1, rec 5.10+", "cause-new-cluster"), LI("tcp_bbr module: `modprobe tcp_bbr` missing", "cause-new-cluster"), LI("Agent not restarted after ConfigMap change", "cause-new-cluster"), LI("CNI chaining bypasses Cilium for egress", "cause-new-cluster")],
    "`cilium status | grep Bandwidth`. `tc -s qdisc show dev lxc_<id>` — look for FQ qdisc. `cilium-dbg bpf bandwidth list`. EDT = Earliest Departure Time (packet pacing). Bandwidth = CNP feature, not vanilla NetworkPolicy.",
    "1. `cilium config set bandwidth-manager true`<br>2. `cilium status | grep Bandwidth` — must be 'OK'<br>3. `tc qdisc show dev lxc_<ep-id>` — should show fq qdisc<br>4. `kubectl exec deploy/web -- iperf3 -c anihpj-api -t 10`<br>5. BBR: `sysctl net.ipv4.tcp_congestion_control=bbr` on all nodes",
    "Bandwidth Manager = per-pod QoS without service mesh. For anihpj: limit batch jobs from saturating NIC. CRITICAL: incompatible with L7 policies (same as Egress GW). L7 OR bandwidth — pick one."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm10", "BBR Not Active on Pod Traffic",
    "BBR enabled but pod-to-pod TCP uses CUBIC. `ss -ti` shows cubic not bbr. No throughput improvement on cross-region links.",
    [LI("BBR not on HOST: `sysctl net.ipv4.tcp_congestion_control` must be 'bbr'. Set on ALL nodes. Pod inherits host setting."), LI("tcp_bbr not loaded: `modprobe tcp_bbr; lsmod | grep bbr`."), LI("Pod-level BBR needs kernel 5.18+: Below 5.18, BBR only for host namespace, not pod netns."), LI("BBR is TCP-only — UDP unchanged. Verify test protocol."), LI("Path not BDP-limited: BBR shines on high BDP paths. Local 10G may not show improvement.")],
    [LI("FQ qdisc missing: EDT needs fq. `tc qdisc show`", "cause-less-likely"), LI("BBRv1 vs v2: kernel may have older variant", "cause-less-likely"), LI("Container inherits wrong congestion control from init ns", "cause-less-likely"), LI("eBPF Host Routing disabled affects TCP stack", "cause-less-likely"), LI("TSO/GRO offload interfering with BBR pacing", "cause-less-likely")],
    [LI("BBR not in Helm: `--set bandwidthManager.bbr=true`", "cause-new-cluster"), LI("Kernel < 5.18: pod BBR not supported", "cause-new-cluster"), LI("tcp_bbr module not autoloaded on boot", "cause-new-cluster"), LI("Sysctl not persisted: /etc/sysctl.d/99-bbr.conf", "cause-new-cluster"), LI("Conflicting CNI setting per-pod congestion control", "cause-new-cluster")],
    "`sysctl net.ipv4.tcp_congestion_control` on HOST. `kubectl exec <pod> -- ss -ti` — shows 'bbr'? `lsmod | grep bbr`. Pod inherits host's congestion control algorithm.",
    "1. On ALL nodes: `modprobe tcp_bbr; sysctl -w net.ipv4.tcp_congestion_control=bbr`<br>2. Persist: `echo 'net.ipv4.tcp_congestion_control=bbr' > /etc/sysctl.d/99-bbr.conf`<br>3. Verify in pod: `kubectl exec deploy/web -- ss -ti`<br>4. Test cross-region: iperf3 between pods on different AZs<br>5. Helm: `--set bandwidthManager.bbr=true`",
    "BBR dramatically improves throughput on high-latency links. For anihpj: if API serves cross-region clients, BBR is a game-changer. But test first — BBR can be aggressive, potentially impacting other tenants on shared links."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm11", "L7 Rate Limiting Not Throttling",
    "CNP with 100 req/min limit for anihpj-api. Clients make 500+ req/min without throttling. No 429 responses in Hubble.",
    [LI("L7 rate limit needs Envoy: `cilium status | grep Proxy`. Envoy must be running for L7 rate limiting."), LI("Rate limit in CNP http rules must have correct syntax. Wrong placement = ignored."), LI("Local rate limiting = per Envoy instance (per node), NOT cluster-wide. If 3 nodes: 100/min × 3 = 300/min total."), LI("Envoy XDS push delayed: config may not have propagated. Force: restart Cilium agent."), LI("Rate limit counter scope: per-endpoint vs per-service vs per-client. Wrong scope = limit not applied as expected.")],
    [LI("Envoy rate limit filter not compiled in Cilium's Envoy", "cause-less-likely"), LI("Burst config allowing initial spike beyond limit", "cause-less-likely"), LI("Multiple Envoy instances: each has independent counter", "cause-less-likely"), LI("HTTP/2 multiplexing: single connection has own rate pipe", "cause-less-likely"), LI("429 responses invisible in Hubble without L7 visibility", "cause-less-likely")],
    [LI("Cilium < 1.14: L7 rate limiting added in 1.14", "cause-new-cluster"), LI("Envoy not enabled: `--set envoy.enabled=true`", "cause-new-cluster"), LI("CNP rate limit syntax changed between versions", "cause-new-cluster"), LI("External RLS not deployed for global rate limiting", "cause-new-cluster"), LI("No metrics exported for rate limit decisions", "cause-new-cluster")],
    "`cilium-dbg envoy config dump | grep rate_limit`. `kubectl get cnp -o yaml | grep -A10 rateLimit`. Hubble: `hubble observe --http-status 429`. Local rate limiting = per-node counters.",
    "1. `kubectl exec ds/cilium -- cilium-dbg envoy config dump | grep -i rate`<br>2. Verify CNP syntax against Cilium docs for your version<br>3. `ab -n 200 -c 10 http://anihpj-api.anihpj.svc/`<br>4. Look for 429 responses in Hubble with L7 visibility<br>5. For global limits: deploy external Rate Limit Service",
    "Cilium's rate limiting is per-node (per-Envoy). For anihpj with 3 nodes: 100/min limit = up to 300/min cluster-wide. For true global limiting, integrate external RLS. Most cases: local limiting is good enough."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm12", "Sidecar-Free mTLS — Pods Communicate Plaintext",
    "mTLS configured via Cilium (no sidecars), but pods communicate plaintext. Hubble: no TLS handshake. WireGuard may be on but not per-pod mTLS.",
    [LI("Confusing node-level encryption with per-pod mTLS: WireGuard/IPSec = NODE level. Per-pod mTLS = Envoy with originatingTLS/terminatingTLS in CNP."), LI("mTLS needs L7 CNP: Without L7 rules, Envoy proxy not engaged. Add http rule to trigger Envoy."), LI("Certificate provisioning: Both client and server certs needed. Cilium doesn't auto-issue per-pod certs (no SPIFFE)."), LI("SPIFFE not integrated: Unlike Istio, Cilium doesn't auto-provision workload identities."), LI("Hubble L7 visibility off: TLS handshake not visible in flow logs without L7 visibility enabled.")],
    [LI("Cipher mismatch between client/server TLS config", "cause-less-likely"), LI("Certificate chain incomplete for mutual validation", "cause-less-likely"), LI("mTLS only for specific ports — others go plaintext", "cause-less-likely"), LI("CRL/OCSP check failing in Envoy", "cause-less-likely"), LI("Session resumption not configured — new TLS per request", "cause-less-likely")],
    [LI("Expecting auto-mTLS like Istio — Cilium needs explicit CNP TLS rules", "cause-new-cluster"), LI("No SPIFFE/SPIRE for auto-cert rotation", "cause-new-cluster"), LI("CNP missing originatingTLS AND terminatingTLS", "cause-new-cluster"), LI("cert-manager not configured for per-pod certs", "cause-new-cluster"), LI("WireGuard misconfigured as 'mTLS replacement'", "cause-new-cluster")],
    "`cilium encrypt status` = node-level encryption. `cilium-dbg envoy config | grep tls_context` = per-pod TLS. `hubble observe --http-status 200` with L7 visibility. Node encryption ≠ pod mTLS!",
    "1. Clarify: WireGuard/IPSec = all traffic encrypted at node level. mTLS = per-pod identity-based TLS<br>2. For mTLS: create CNP with terminatingTLS + originatingTLS sections<br>3. Provision certs via cert-manager for client and server<br>4. Enable L7 visibility for Hubble TLS flows<br>5. For auto-mTLS with SPIFFE: integrate Istio alongside Cilium",
    "Cilium's 'sidecar-free mesh' = Envoy proxy without sidecar injection. But TLS is NOT automatic — you configure it in CNP. For anihpj: if you want full auto-mTLS with workload identity, Cilium + Istio is the recommended combo."
)

# SM13-SM16: Integration & Advanced
cat3 += SH("sm13", "🔗 SM13–SM16: Service Mesh Integration &amp; Advanced L7")
cat3 += TS(3, "SERVICE MESH", "🟡", "sm13", "Cilium + Istio — Conflicting L7 Policies",
    "Both CNP and Istio VirtualService for anihpj-api. Traffic behaves unpredictably — sometimes Cilium routes, sometimes Istio. 503 errors intermittent.",
    [LI("Double proxy: Cilium Envoy + Istio sidecar = two proxies. Traffic: pod→CiliumEnvoy→Istio→app. L7 policies may conflict."), LI("Cilium L7 CNP intercepts BEFORE Istio sidecar: Istio mTLS may break if Cilium terminates TLS first."), LI("Port conflict: both proxies try to intercept same port."), LI("Socket LB mode skips ALL proxies: Istio never sees traffic if socket LB enabled."), LI("Identity mismatch: Cilium numeric identity vs Istio SPIFFE. Cross-referencing fails.")],
    [LI("Istio iptables redirecting after Cilium eBPF processing", "cause-less-likely"), LI("Cilium Envoy + Istio sidecar sharing port space", "cause-less-likely"), LI("CiliumEndpoint identity not in Istio SPIFFE registry", "cause-less-likely"), LI("Cilium DNS proxy before Istio DNS capture", "cause-less-likely"), LI("Cilium terminating TLS before Istio mTLS handshake", "cause-less-likely")],
    [LI("Both installed without coordination", "cause-new-cluster"), LI("L7 CNP created without knowing Istio exists", "cause-new-cluster"), LI("No clear ownership: platform=Cilium, app=Istio", "cause-new-cluster"), LI("Mesh config not documented", "cause-new-cluster"), LI("Cilium policy-enforcement-mode=always with Istio", "cause-new-cluster")],
    "`cilium status | grep Proxy` + `istioctl proxy-status`. Hubble: trace one request through ALL hops. Rule: Cilium L3/L4 + Istio L7 = best practice. Avoid L7 in Cilium if Istio is your mesh.",
    "1. Simplify: Cilium=L3/L4 (NetworkPolicy, WireGuard, BGP), Istio=L7 (routing, retries, mTLS)<br>2. Remove L7 rules from CNP — let Istio handle HTTP<br>3. Disable Cilium Envoy if using Istio: `--set envoy.enabled=false`<br>4. `hubble observe --from-pod web --to-pod api` — verify path<br>5. `istioctl authn tls-check <pod>` — verify mTLS",
    "Cilium + Istio = powerful. Best practice: Cilium for networking (L3/L4, encryption, BGP, Hubble), Istio for mesh (L7 routing, canary, fault injection). For anihpj: start with Cilium-only, add Istio only when you need advanced L7 mesh features."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm14", "CiliumEnvoyConfig — Custom Envoy Not Loading",
    "Custom CEC for anihpj-api with specific Envoy filters. Envoy not loading config. `cilium-dbg envoy config` shows defaults only.",
    [LI("CEC spec invalid: Envoy config must be valid JSON in `spec.resources[]`. `kubectl describe cec <name>` for validation errors."), LI("CEC not associated: `spec.services[]` must match existing Service. Orphaned if no pods match."), LI("XDS gRPC timeout: Envoy fetches config from Cilium agent. Busy agent = stream timeout."), LI("Duplicate CECs: only one CEC per service direction. Check for conflicts."), LI("Agent not watching CEC: `kubectl logs ds/cilium | grep CEC` — look for processing errors.")],
    [LI("Envoy type URL unsupported by Cilium's Envoy version", "cause-less-likely"), LI("CEC too large: >100KB hits xDS message limit", "cause-less-likely"), LI("Envoy rejecting unknown filter/plugin", "cause-less-likely"), LI("xDS cache not invalidated after CEC update", "cause-less-likely"), LI("CEC status conditions stale (not refreshed)", "cause-less-likely")],
    [LI("CEC CRD not installed (auto-installed by Cilium)", "cause-new-cluster"), LI("Envoy proxy not enabled", "cause-new-cluster"), LI("CEC created before Service exists", "cause-new-cluster"), LI("Node-local Envoy not available", "cause-new-cluster"), LI("RBAC: Cilium agent can't read CEC", "cause-new-cluster")],
    "`kubectl get cec -A`. `kubectl describe cec <name>`. `cilium-dbg envoy config dump` — compare with CEC. `kubectl logs ds/cilium | grep -i 'envoy\|cec\|xds'`. CEC gives full Envoy power without separate deployment.",
    "1. `kubectl describe cec <name> -n anihpj`<br>2. `kubectl logs ds/cilium --tail=100 | grep -i cec`<br>3. `kubectl get svc,ep anihpj-api -n anihpj`<br>4. `kubectl exec ds/cilium -- cilium-dbg envoy config dump`<br>5. Start with minimal valid CEC, then add complexity",
    "CEC = full Envoy config injection. For anihpj: use CEC for JWT validation, custom rate limiting, or WebSocket upgrades that CNP can't express. But 90% of use cases are covered by CNP alone."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm15", "gRPC Load Balancing — Sticky to Single Backend",
    "gRPC client always hits same backend. All streams on one connection. Other backends idle. Scaling doesn't help.",
    [LI("gRPC uses HTTP/2 single connection: All streams multiplexed on ONE TCP connection. L4 LB happens at connection setup, not per-stream."), LI("No L7 policy: Cilium can't see gRPC streams without L7. Without L7, only connection-level LB."), LI("Client-side LB not configured: gRPC defaults to 'pick_first'. Use round_robin or grpclb resolver."), LI("Connection keepalive too long: gRPC connections stay forever. Set GRPC_ARG_KEEPALIVE_TIME_MS."), LI("Maglev (L4) maps ONE connection to ONE backend — not effective for gRPC.")],
    [LI("GOAWAY not sent to force reconnection", "cause-less-likely"), LI("gRPC channel DNS cache never refreshed", "cause-less-likely"), LI("Envoy not recognizing gRPC as distinct HTTP/2 streams", "cause-less-likely"), LI("Max concurrent streams too high preventing rotation", "cause-less-likely"), LI("Socket LB not supporting HTTP/2 multiplex detection", "cause-less-likely")],
    [LI("gRPC deployed with L4-only CNP", "cause-new-cluster"), LI("Client uses default pick_first LB", "cause-new-cluster"), LI("No service mesh for gRPC-aware routing", "cause-new-cluster"), LI("ClusterIP can't help with gRPC L7", "cause-new-cluster"), LI("No headless service for client discovery", "cause-new-cluster")],
    "`hubble observe --to-port 50051 --protocol gRPC`. Client: set `GRPC_GO_LOG_SEVERITY_LEVEL=info`. gRPC needs L7 or client-side LB. L4 alone can't balance per-stream.",
    "1. Enable L7 CNP for gRPC port<br>2. Client: `grpc.WithDefaultServiceConfig('{\"loadBalancingPolicy\":\"round_robin\"}')`<br>3. Or headless service + client DNS resolution<br>4. `dns:///anihpj-api-grpc.anihpj.svc:50051` with round_robin<br>5. Alternative: deploy Envoy as gRPC-aware LB in front",
    "gRPC + Kubernetes requires specific design. For anihpj: either (a) client-side round_robin with headless service, or (b) gRPC proxy with L7 config. ClusterIP won't magically balance gRPC streams."
)

cat3 += TS(3, "SERVICE MESH", "🟡", "sm16", "HTTP/3 QUIC — Falls Back to TCP or Blocked",
    "QUIC/HTTP3 on anihpj-api. Cilium drops QUIC packets (UDP 443). Hubble shows DROPPED. Clients fall back to TCP/HTTP2.",
    [LI("QUIC = UDP 443: If CNP only has TCP rules, UDP is dropped by default-deny. Add UDP 443 rule."), LI("Cilium L7 = TCP only: All L7 inspection (Envoy) is TCP-based. QUIC bypasses Envoy entirely."), LI("UDP port not in CNP: `toPorts[].ports[].protocol: UDP` with port 443 needed."), LI("Conntrack can't track QUIC connection migration (connection ID changes)."), LI("Kernel UDP GRO needed for performance: check kernel version for UDP optimizations.")],
    [LI("QUIC version negotiation blocked as unknown UDP", "cause-less-likely"), LI("0-RTT data dropped by conntrack as invalid", "cause-less-likely"), LI("QUIC connection migration breaks conntrack state", "cause-less-likely"), LI("UDP fragmentation with large QUIC packets blocked", "cause-less-likely"), LI("DNS proxy intercepting QUIC SNI for domain filtering", "cause-less-likely")],
    [LI("QUIC deployed without UDP rules in CNP", "cause-new-cluster"), LI("Default-deny CNP blocking all UDP", "cause-new-cluster"), LI("L7 CNP for HTTP but QUIC is UDP", "cause-new-cluster"), LI("No awareness that Cilium L7 = TCP-only", "cause-new-cluster"), LI("QUIC enabled but network not configured for UDP 443", "cause-new-cluster")],
    "`hubble observe --protocol UDP --to-port 443 --verdict DROPPED`. Check CNP: UDP 443 rule? `cilium-dbg envoy config` — no QUIC support. Cilium L7 inspection = TCP only. QUIC = L4 only (allow/deny).",
    "1. Add UDP 443 to CNP: `toPorts: [{ports: [{port: '443', protocol: UDP}]}]`<br>2. Accept: no L7 inspection on QUIC — only allow/deny<br>3. For L7 on QUIC: terminate at external LB with QUIC support<br>4. `hubble observe --protocol UDP --to-port 443` to verify<br>5. Monitor fallback: check if clients fall back to TCP/HTTP2",
    "QUIC + Cilium = L4 only for now. For anihpj: if you need QUIC + L7 policies, terminate QUIC at an external LB (like a cloud LB or Envoy with QUIC), then forward as TCP to Cilium-managed backends."
)

print("✅ CAT3 generated: 16 issues (SM1-SM16)")

# =====================================================================
# CATEGORY 4: OBSERVABILITY (OB1-OB10)
# =====================================================================
cat4 = SH("ob1", "📡 OB1–OB5: Hubble &amp; Flow Visibility")
cat4 += TS(4, "OBSERVABILITY", "🔵", "ob1", "Hubble Relay — No Agents Connected",
    "`hubble relay status` shows 0 connected peers. `hubble observe` returns 'no peers available'. Hubble UI shows 'No agents'.",
    [LI("Hubble not enabled on agents: `--set hubble.enabled=true`. Each Cilium agent needs Hubble server enabled."), LI("Hubble Relay cannot reach Peer Service: `kubectl get svc -n kube-system hubble-peer`. Must exist and be resolvable."), LI("TLS certs mismatch: Hubble uses TLS between Relay and agents. `cilium hubble enable` generates certs."), LI("Hubble Relay deployed but agents not restarted: agents need restart after Hubble enabled."), LI("NetworkPolicy blocking port 4244 (Hubble gRPC) or 80 (Peer Service).")],
    [LI("Hubble Relay pod crashing: `kubectl logs deploy/hubble-relay -n kube-system`", "cause-less-likely"), LI("Peer Service endpoints empty: `kubectl get ep hubble-peer -n kube-system`", "cause-less-likely"), LI("gRPC max message size exceeded for large clusters", "cause-less-likely"), LI("Hubble Relay OOM with many agents", "cause-less-likely"), LI("IPv6 only cluster — Hubble Relay config missing IPv6", "cause-less-likely")],
    [LI("hubble.enabled not in Helm values", "cause-new-cluster"), LI("hubble.relay.enabled not set", "cause-new-cluster"), LI("TLS certs not generated: `cilium hubble enable` not run", "cause-new-cluster"), LI("hubble-peer Service not created", "cause-new-cluster"), LI("RBAC missing for hubble-relay to list nodes", "cause-new-cluster")],
    "`cilium status | grep Hubble`. `cilium hubble relay status`. `kubectl logs deploy/hubble-relay -n kube-system`. `kubectl get svc,ep hubble-peer -n kube-system`. Hubble Relay aggregates flows from all agents via Peer Service.",
    "1. `cilium hubble enable` — enables Hubble + Relay + UI<br>2. `cilium status | grep Hubble` — all three should be 'OK'<br>3. `cilium hubble relay status` — check peer count<br>4. `kubectl logs deploy/hubble-relay -n kube-system`<br>5. `kubectl exec deploy/hubble-relay -- hubble list-nodes`",
    "Hubble Relay is the aggregation layer. Without it, you query each agent individually. For anihpj: always deploy Relay for cluster-wide visibility. Common mistake: enabling Hubble but forgetting Relay."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob2", "Hubble Observe — Empty Output or Timeout",
    "`hubble observe` returns nothing or times out. `hubble observe --follow` hangs. Port-forward works but no flows.",
    [LI("Hubble server not enabled on agents: `cilium config | grep hubble`. Must show enabled with socket path."), LI("Flow export not configured: agents need Hubble enabled. Check `cilium status | grep Hubble` per node."), LI("Hubble listening on wrong socket: default unix:///var/run/cilium/hubble.sock. Check port-forward target."), LI("No traffic matching filter: default `hubble observe` shows recent flows. If cluster idle, no output."), LI("Namespace filter too restrictive: `-n kube-system` may exclude app traffic in `anihpj` namespace.")],
    [LI("Hubble ring buffer full — oldest events evicted before Relay reads", "cause-less-likely"), LI("Flow API rate limiting: too many flows overwhelming client", "cause-less-likely"), LI("Hubble CLI version mismatch with server", "cause-less-likely"), LI("BPF ring buffer perf event lost (kernel backpressure)", "cause-less-likely"), LI("TLS handshake timeout between CLI and Relay", "cause-less-likely")],
    [LI("Hubble not enabled at install: `--set hubble.enabled=false` default", "cause-new-cluster"), LI("hubble-relay not deployed", "cause-new-cluster"), LI("hubble-ui not deployed for UI access", "cause-new-cluster"), LI("Port-forward to wrong service", "cause-new-cluster"), LI("No traffic yet — cluster just installed", "cause-new-cluster")],
    "`cilium status | grep Hubble`. `cilium hubble port-forward &` then `hubble observe`. `kubectl logs ds/cilium | grep hubble`. Start with broad filter: `hubble observe --verdict DROPPED` — always shows something if policies exist.",
    "1. `cilium status` — all Hubble components 'OK'?<br>2. `cilium hubble port-forward &` (background)<br>3. `hubble observe --verdict DROPPED` — should show policy drops<br>4. `hubble observe -n anihpj` — app namespace<br>5. `hubble observe --last 100` — recent events",
    "Hubble is your 'tcpdump for Kubernetes'. For anihpj: always start troubleshooting with `hubble observe --verdict DROPPED` to see if policies are blocking traffic. Then narrow by namespace/pod."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob3", "Hubble UI — Blank Dashboard / No Flows",
    "Hubble UI loads but shows 'No flows' or blank service map. Service map is empty. Flow table shows zero records.",
    [LI("Hubble UI can't reach Relay: `kubectl get svc hubble-ui -n kube-system`. UI proxies through Relay."), LI("No traffic in selected time range: default shows last 5 minutes. Generate test traffic: `cilium connectivity test`."), LI("Namespace filter set: UI may have filter from previous session. Clear all filters."), LI("Relay not connected to agents: check `cilium hubble relay status`. 0 peers = no data."), LI("Browser CORS issue: Hubble UI API calls may be blocked. Check browser console for errors.")],
    [LI("Hubble UI pod OOM with large cluster flow data", "cause-less-likely"), LI("Flow data too large for browser: >100K flows/sec overloads UI", "cause-less-likely"), LI("Hubble UI version incompatible with Relay version", "cause-less-likely"), LI("WebSocket connection to Relay dropping", "cause-less-likely"), LI("Local storage corrupted in browser for Hubble UI settings", "cause-less-likely")],
    [LI("hubble.ui.enabled not in Helm values", "cause-new-cluster"), LI("Hubble UI Service not exposed: need port-forward or Ingress", "cause-new-cluster"), LI("hubble-ui pod not scheduled (resource constraints)", "cause-new-cluster"), LI("Relay deployed but UI can't resolve relay DNS", "cause-new-cluster"), LI("No Ingress/NodePort for Hubble UI external access", "cause-new-cluster")],
    "`kubectl get pods -n kube-system | grep hubble`. `cilium hubble ui` opens browser. `cilium hubble relay status`. Generate traffic: `kubectl exec deploy/web -- curl http://anihpj-api.anihpj.svc`.",
    "1. `cilium hubble ui` — opens UI via port-forward<br>2. Generate traffic: `kubectl exec deploy/web -- curl -s http://anihpj-api.anihpj.svc/`<br>3. Check Relay: `cilium hubble relay status`<br>4. Clear all UI filters — namespace, verdict, pod<br>5. Browser dev tools → Network tab → check API calls to Relay",
    "Hubble UI is your visual troubleshooting tool. For anihpj: bookmark `cilium hubble ui` as your first stop when debugging connectivity issues. The service map visualizes all pod-to-pod communication."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob4", "Hubble Metrics Missing in Prometheus",
    "Hubble metrics endpoint enabled but Prometheus shows no Cilium/Hubble metrics. `curl <agent-ip>:9965/metrics` returns empty or connection refused.",
    [LI("Hubble metrics not enabled: `--set hubble.metrics.enabled='{drop,tcp,flow,port-distribution,dns,http}'`. Without explicit metrics list, nothing exported."), LI("Port 9965 not open: Prometheus metrics run on separate port. Check `cilium status | grep Metrics`."), LI("Prometheus ServiceMonitor/PodMonitor not created: Prometheus needs discovery config for Cilium agents."), LI("Firewall blocking 9965: agents expose metrics on host IP. Security groups must allow Prometheus→9965."), LI("Metrics list wrong: metric names must match exactly. `hubble.metrics` is a list of enabled metrics.")],
    [LI("Prometheus scraping wrong port (9090 instead of 9965)", "cause-less-likely"), LI("Metrics endpoint returns but all values 0 — no traffic", "cause-less-likely"), LI("Prometheus relabel config dropping Cilium targets", "cause-less-likely"), LI("Cilium agent restarting before metrics scrape interval", "cause-less-likely"), LI("IPv6 address not handled by Prometheus scrape config", "cause-less-likely")],
    [LI("hubble.metrics not in Helm values — empty default", "cause-new-cluster"), LI("Prometheus not installed in cluster", "cause-new-cluster"), LI("ServiceMonitor CRD not installed (needs prometheus-operator)", "cause-new-cluster"), LI("No annotation on Cilium pods for Prometheus discovery", "cause-new-cluster"), LI("NetworkPolicy blocking Prometheus→agent:9965", "cause-new-cluster")],
    "`cilium status | grep Metrics`. `curl http://<node-ip>:9965/metrics | grep hubble`. `kubectl get servicemonitor -n kube-system | grep cilium`. Metrics are per-agent — aggregate in Prometheus.",
    "1. Enable metrics: `cilium hubble enable --metrics 'drop,tcp,flow,port-distribution,dns,http'`<br>2. `curl <node-ip>:9965/metrics` — should return Prometheus text<br>3. Create ServiceMonitor for Cilium agents<br>4. Check Prometheus targets: port 9965, path /metrics<br>5. Grafana dashboard: import Cilium/Hubble dashboards",
    "Hubble metrics are the bridge between flow logs and dashboards. For anihpj: enable drop, tcp, flow, and http metrics at minimum. Then import the official Cilium Grafana dashboards for instant observability."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob5", "Flow Export to External SIEM/Collector Not Working",
    "Hubble flow export configured (Kafka/Elasticsearch/Splunk) but external system receives no flows. Hubble observe works locally but export fails.",
    [LI("Hubble export not configured: `cilium config | grep hubble-export`. Flow export needs explicit config for output target."), LI("Kafka/ES endpoint unreachable: network between cluster and external collector. Check DNS resolution from Cilium agent."), LI("TLS/mTLS for export not configured: if external system requires TLS, Cilium needs certs for export."), LI("Export file path wrong: if using file export, path must be writable by Cilium agent."), LI("Flow filter too restrictive: export uses same filter as observe. If filter excludes all flows, nothing exported.")],
    [LI("Flow export buffer full — backpressure from slow collector", "cause-less-likely"), LI("Kafka topic auto-create disabled and topic doesn't exist", "cause-less-likely"), LI("Export message format mismatch (JSON vs Protobuf)", "cause-less-likely"), LI("Cilium agent DNS cache stale for collector hostname", "cause-less-likely"), LI("Flow rate exceeds collector ingest capacity", "cause-less-likely")],
    [LI("Hubble export not enabled: no Helm values for export config", "cause-new-cluster"), LI("External collector not provisioned yet", "cause-new-cluster"), LI("Network isolation: cluster can't reach external collector IP", "cause-new-cluster"), LI("Export TLS secrets not created", "cause-new-cluster"), LI("No monitoring for export health", "cause-new-cluster")],
    "`cilium config | grep hubble-export`. `kubectl logs ds/cilium | grep -i 'export\|kafka\|elastic'`. Test connectivity: `kubectl exec ds/cilium -- nc -zv <collector> <port>`.",
    "1. Configure: `cilium config set hubble-export-file-path /var/log/cilium/flows.json`<br>2. Or Kafka: `cilium hubble enable --kafka-brokers <broker>:9092 --kafka-topic hubble`<br>3. Test: `kubectl exec ds/cilium -- nc -zv <collector> <port>`<br>4. Check agent logs for export errors<br>5. Verify flow filter isn't too restrictive",
    "Hubble flow export = network telemetry pipeline. For anihpj: export to Elasticsearch + Kibana for long-term flow storage and analysis. Hubble's local ring buffer is limited — export gives you historical data."
)

# OB6-OB10: Prometheus, Grafana, Alerts
cat4 += SH("ob6", "📈 OB6–OB10: Metrics, Dashboards &amp; Alerts")
cat4 += TS(4, "OBSERVABILITY", "🔵", "ob6", "Cilium Agent Metrics Missing from Prometheus",
    "Prometheus shows no cilium_* metrics. Agent on port 9962 returns empty. `cilium metrics list` shows metrics enabled but not scraped.",
    [LI("Agent metrics port 9962 not exposed: `--set prometheus.enabled=true`. Different from Hubble metrics port 9965."), LI("Prometheus ServiceMonitor selects wrong port: agent metrics on 9962, Hubble on 9965, Envoy on 9964."), LI("Firewall blocking 9962: same as Hubble — security groups must allow Prometheus to scrape."), LI("kube-proxy replacement may affect metrics path: if KPR is strict, NodePort redirects may interfere."), LI("Agent metrics disabled via `--set prometheus.enabled=false` — check Helm values.")],
    [LI("Cilium agent restarting frequently — metrics reset before scrape", "cause-less-likely"), LI("Prometheus scrape interval > metrics lifetime", "cause-less-likely"), LI("Agent memory pressure causing metrics endpoint timeout", "cause-less-likely"), LI("IPv6 bind failure on metrics port", "cause-less-likely"), LI("Metrics cardinality explosion causing scrape timeout", "cause-less-likely")],
    [LI("prometheus.enabled not in Helm values", "cause-new-cluster"), LI("Prometheus operator not installed", "cause-new-cluster"), LI("ServiceMonitor not created for Cilium agent", "cause-new-cluster"), LI("No RBAC for Prometheus to discover pod IPs", "cause-new-cluster"), LI("Confused about which port (9962/9964/9965) has which metrics", "cause-new-cluster")],
    "`cilium status | grep Metrics`. `curl <node-ip>:9962/metrics | head`. Port map: 9962=agent, 9964=Envoy, 9965=Hubble. `kubectl get servicemonitor -A | grep cilium`.",
    "1. `--set prometheus.enabled=true` in Helm<br>2. `curl <node-ip>:9962/metrics` — should show cilium_* metrics<br>3. Create ServiceMonitor for port 9962 (agent metrics)<br>4. Create separate ServiceMonitor for port 9965 (Hubble metrics)<br>5. Port 9964 for Envoy metrics (if using L7)",
    "Three metrics ports: agent (9962), Envoy (9964), Hubble (9965). For anihpj: enable all three. Agent metrics = Cilium health. Envoy metrics = L7 proxy stats. Hubble metrics = flow-derived metrics. Each needs its own ServiceMonitor."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob7", "Grafana Dashboard — Missing Cilium Panels/No Data",
    "Imported Cilium Grafana dashboard (ID: 15513/15514) but panels show 'No data' or NaN. Prometheus data source works for other dashboards.",
    [LI("Wrong Prometheus data source: dashboard hardcodes 'Prometheus' data source name. Yours may be named differently."), LI("Metrics not enabled: dashboard needs specific metrics. `cilium status | grep Metrics` — verify enabled set."), LI("PromQL queries use deprecated metric names: Cilium renamed metrics between versions. Check dashboard version vs Cilium version."), LI("Node/Pod variable templates fail: dashboard uses template variables that may not resolve in your cluster setup."), LI("Time range too narrow: some Cilium metrics are scraped every 30s. Dashboard needs at least 5 minutes of data.")],
    [LI("Grafana plugin for Prometheus not installed/updated", "cause-less-likely"), LI("Dashboard JSON for wrong Cilium version (v1.12 vs v1.15)", "cause-less-likely"), LI("Custom Prometheus recording rules missing", "cause-less-likely"), LI("Cilium agent labels not matching dashboard pod/namespace filters", "cause-less-likely"), LI("Grafana server timezone mismatch with Prometheus timestamps", "cause-less-likely")],
    [LI("No Cilium metrics enabled — dashboard has no data source", "cause-new-cluster"), LI("Prometheus not scraping Cilium agents at all", "cause-new-cluster"), LI("Wrong dashboard ID imported (non-Cilium dashboard)", "cause-new-cluster"), LI("Grafana data source not configured for cluster's Prometheus", "cause-new-cluster"), LI("Dashboard imported before metrics existed (empty range)", "cause-new-cluster")],
    "Grafana → Dashboard settings → Variables → check resolution. `cilium metrics list` — verify enabled metrics match dashboard requirements. Try Cilium's official dashboards: 15513 (Cilium), 15514 (Hubble).",
    "1. Verify metrics: `cilium metrics list`<br>2. Check Prometheus: `up{job='cilium-agent'}` — should return all nodes<br>3. Grafana data source name must match dashboard variable<br>4. Import latest dashboard from cilium.io/documentation<br>5. Time range: select 'Last 15 minutes' minimum",
    "Official Cilium dashboards: Grafana ID 15513 (Cilium Agent Metrics) and 15514 (Hubble Metrics). For anihpj: start with these, then customize for your app-specific metrics like HTTP request rates."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob8", "Cilium Monitor — Event Flood / Can't Find Relevant Event",
    "`cilium monitor` outputs thousands of events per second. Can't isolate the one dropped packet or policy decision needed.",
    [LI("No filter: `cilium monitor` shows ALL events — endpoint regenerations, policy updates, drops, debug. Use `--type` filter."), LI("Event types not filtered: use `--type drop` for only drops, `--type policy-verdict` for policy decisions, `--type debug` for detailed."), LI("Too many endpoints: filter by endpoint ID: `cilium monitor --from <ep-id> --to <ep-id>`."), LI("Verbose mode: `cilium monitor -v` shows hex dumps — useful for deep debugging but overwhelming."), LI("No related-to filter: use `--related-to <ep-id>` to see events related to a specific endpoint.")],
    [LI("Kernel debug events enabled: `cilium config | grep debug`. Disable for production.", "cause-less-likely"), LI("Event buffer too small causing dropped events", "cause-less-likely"), LI("Monitor output format: JSON mode (`-o json`) for programmatic parsing", "cause-less-likely"), LI("Multiple monitors connected simultaneously causing event duplication", "cause-less-likely"), LI("Agent restart causing event replay from ring buffer", "cause-less-likely")],
    [LI("Production cluster with debug logging: `--set debug.enabled=true` wrong for prod", "cause-new-cluster"), LI("No familiarity with cilium monitor filter flags", "cause-new-cluster"), LI("Using cilium monitor instead of hubble observe for flow debugging", "cause-new-cluster"), LI("Monitor events not correlated with Hubble flows", "cause-new-cluster"), LI("No monitoring retention: events lost immediately after display", "cause-new-cluster")],
    "`cilium monitor --type drop -n anihpj` — only drops in anihpj namespace. `cilium monitor --from <ep-id> --to <ep-id>` — specific pod pair. Better: use `hubble observe` for flow-level. `cilium monitor` = control plane events. `hubble observe` = data plane flows.",
    "1. `cilium monitor --type drop` — policy drops only<br>2. `cilium monitor --from <pod-ep-id> --to <pod-ep-id>`<br>3. `cilium monitor --type policy-verdict` — see policy decisions<br>4. Prefer `hubble observe --verdict DROPPED` for flow drops<br>5. `cilium monitor -o json | grep <keyword>` for scripting",
    "`cilium monitor` = control plane events (policy updates, endpoint changes). `hubble observe` = data plane flows (actual packets). For anihpj: use Hubble for 'why is my traffic failing?', use monitor for 'why is Cilium behaving this way?'."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob9", "Prometheus Alert Rules Not Firing for Cilium Issues",
    "Prometheus alert rules configured for Cilium but never fire. `cilium status` shows degraded but no alert. AlertManager silent.",
    [LI("Alert expression threshold wrong: e.g., `cilium_endpoint_regenerations_total > 1000` may never trigger. Check actual metric values first."), LI("Metric name mismatch: Cilium renamed metrics. `cilium_agent_endpoint_regenerations_total` vs `cilium_endpoint_regenerations_total`."), LI("Prometheus rule evaluation interval too long: default 1m. Issue may resolve before alert fires."), LI("Alert 'for' duration too long: e.g., `for: 15m` means issue must persist 15 minutes. Reduce for quick detection."), LI("Labels mismatch: alert rule label selectors may not match actual metric labels (namespace, pod, node).")],
    [LI("Prometheus rule file not loaded: syntax error silently ignored", "cause-less-likely"), LI("AlertManager not configured as Prometheus alert target", "cause-less-likely"), LI("Prometheus 'inhibit' rules suppressing Cilium alerts", "cause-less-likely"), LI("Alert expression returns empty vector (no matching time series)", "cause-less-likely"), LI("Cilium agent label changed between versions", "cause-less-likely")],
    [LI("No Cilium-specific alert rules created", "cause-new-cluster"), LI("Prometheus not scraping Cilium endpoints", "cause-new-cluster"), LI("AlertManager not deployed", "cause-new-cluster"), LI("Alert routing not configured for Cilium team", "cause-new-cluster"), LI("Tested in staging but metrics differ in production", "cause-new-cluster")],
    "Prometheus → Alerts tab → check rule state. `curl <prometheus>:9090/api/v1/rules | grep cilium`. Test expression in Prometheus console first. Key alerts: `cilium_endpoint_regenerations`, `cilium_unreachable_nodes`, `cilium_errors_warnings_total`.",
    "1. Test expression in Prometheus console: `cilium_agent_endpoint_regenerations_total > 0`<br>2. Check rule syntax: `promtool test rules /path/to/rules.yml`<br>3. Verify `for` duration: 1m for critical, 5m for warning<br>4. Check AlertManager: `amtool alert` to see firing alerts<br>5. Route: Slack/email/PagerDuty for critical Cilium alerts",
    "Critical Cilium alerts: agent down, unreachable nodes, high policy drops, encryption errors. For anihpj: create alerts for `rate(hubble_drop_total[5m]) > 10` (policy blocking traffic) and `cilium_unreachable_nodes > 0` (node connectivity)."
)

cat4 += TS(4, "OBSERVABILITY", "🔵", "ob10", "Cilium Sysdump — File Too Large / Can't Analyze",
    "`cilium sysdump` creates 500MB+ zip. Can't find relevant logs. Too much data to manually analyze. Timeout collecting from slow nodes.",
    [LI("No node filter: `cilium sysdump` collects from ALL nodes. Use `--node-list node-1,node-2` for targeted collection."), LI("BPF map dumps included: large clusters have huge BPF maps. Skip with `--output-dir` and manual filtering."), LI("Hubble flows included: if Hubble export is configured, flows may be massive. Exclude with flags."), LI("Collection timeout: slow/overloaded nodes timeout. Increase `--timeout` or collect from responsive nodes first."), LI("Log rotation: very old logs included bloating the archive. Use `--since` flag for recent issues.")],
    [LI("Disk space on node where sysdump runs insufficient", "cause-less-likely"), LI("Compression too slow: tar.gz of 500MB+ takes minutes", "cause-less-likely"), LI("Network transfer of large sysdump to support team", "cause-less-likely"), LI("BPF map binary format not readable without bpftool", "cause-less-likely"), LI("Sensitive data (IPs, endpoints) in plaintext logs", "cause-less-likely")],
    [LI("No sysdump retention policy — filling disk", "cause-new-cluster"), LI("Sysdump collected from entire cluster instead of affected nodes", "cause-new-cluster"), LI("No automation: manual sysdump collection when issue occurs", "cause-new-cluster"), LI("Support team can't open 500MB+ zip files", "cause-new-cluster"), LI("No sysdump analysis tooling in place", "cause-new-cluster")],
    "`cilium sysdump --node-list node-1` for targeted. `cilium sysdump --output-dir /tmp/cilium-debug-$(date +%s)`. Typical size: 50-200MB per node. First files to check: `cilium-status.log`, `cilium-agent.log`, `cilium-config.yaml`.",
    "1. Targeted: `cilium sysdump --node-list <bad-node>`<br>2. Recent: use `--since 1h` for last hour only<br>3. Skip BPF maps: `--exclude-bpf-maps` if not needed<br>4. Analyze: start with `cilium-status.log` and `cilium-agent.log`<br>5. Automate: create a cronjob for weekly sysdump rotation",
    "cilium sysdump is your first response to any Cilium issue. For anihpj: create a script that runs `cilium sysdump --node-list $(kubectl get nodes -l node-role=worker -o name | head -3) --since 30m` and uploads to S3 automatically."
)

print("✅ CAT4 generated: 10 issues (OB1-OB10)")

# =====================================================================
# Now insert all content into the HTML file
# =====================================================================

with open(HTML, "r", encoding="utf-8") as f:
    content = f.read()

# CAT3 insertion marker
m3 = '<section class="chapter-section" id="ts-cat3">\n<h2><span>Category 3: Service Mesh</span><span class="chapter-badge">SM1-SM16</span></h2>\n<div class="chapter-intro"><p>16 troubleshooting issues covering KPR, Maglev, socket LB, DSR, Ingress/Gateway API, TLS, canary, bandwidth manager, BBR, and sidecar-free mesh.</p></div>\n</section>\n\n\n    <!-- ═══════════════ PART 3 ═══════════════ -->'
r3 = '<section class="chapter-section" id="ts-cat3">\n<h2><span>Category 3: Service Mesh</span><span class="chapter-badge">SM1-SM16</span></h2>\n<div class="chapter-intro"><p>16 troubleshooting issues covering KPR, Maglev, socket LB, DSR, Ingress/Gateway API, TLS, canary, bandwidth manager, BBR, and sidecar-free mesh.</p></div>\n</section>\n\n' + cat3 + '\n\n    <!-- ═══════════════ PART 3 ═══════════════ -->'

if m3 in content:
    content = content.replace(m3, r3, 1)
    print("✅ CAT3 inserted (SM1-SM16)")
else:
    print("❌ CAT3 marker NOT FOUND!")
    # try to find it
    idx = content.find('id="ts-cat3"')
    if idx > 0:
        print(f"  Found at position {idx}, context: ...{content[idx:idx+200]}...")

# CAT4 - need to find insertion point after CAT3
# The ts-cat4 marker
m4 = '<section class="chapter-section" id="ts-cat4">\n<h2><span>Category 4: Observability</span><span class="chapter-badge">OB1-OB10</span></h2>\n<div class="chapter-intro"><p>10 troubleshooting issues covering Hubble, flow visibility, metrics, Grafana, and alerts.</p></div>\n</section>\n\n\n    <!-- ═══════════════ CATEGORY 5: INSTALLATION ═══════════════ -->'
r4 = '<section class="chapter-section" id="ts-cat4">\n<h2><span>Category 4: Observability</span><span class="chapter-badge">OB1-OB10</span></h2>\n<div class="chapter-intro"><p>10 troubleshooting issues covering Hubble, flow visibility, metrics, Grafana, and alerts.</p></div>\n</section>\n\n' + cat4 + '\n\n    <!-- ═══════════════ CATEGORY 5: INSTALLATION ═══════════════ -->'

if m4 in content:
    content = content.replace(m4, r4, 1)
    print("✅ CAT4 inserted (OB1-OB10)")
else:
    print("❌ CAT4 marker NOT FOUND!")
    idx = content.find('id="ts-cat4"')
    if idx > 0:
        print(f"  Found at position {idx}, context: ...{content[idx:idx+300]}...")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("\n🎉 Done! CAT3 + CAT4 troubleshooting inserted.")
