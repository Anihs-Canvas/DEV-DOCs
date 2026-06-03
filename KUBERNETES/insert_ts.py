#!/usr/bin/env python3
"""Insert all missing troubleshooting issues (Cats 3-8) into cilium-test-prep.html"""

HTML_PATH = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\cilium-test-prep.html"

# =============================================================================
# Helper to generate a TS issue
# =============================================================================
def ts_issue(cat_num, cat_name, cat_color, issue_id, issue_label, title, symptom, 
             diagram, most_likely, less_likely, new_cluster, lookat, solution, advice):
    return f'''    <div class="ts-issue" id="ts-{issue_id}-detail">
        <div class="ts-issue-header">
            <div class="ts-issue-num">{issue_label}</div>
            <div class="ts-issue-header-content">
                <div class="ts-category">{cat_color} CATEGORY {cat_num}: {cat_name} — Issue {issue_label}</div>
                <div class="ts-title">{title}</div>
                <p class="ts-symptom"><strong>🔍 Symptom:</strong> {symptom}</p>
            </div>
        </div>
        {diagram}
        <div class="ts-causes-grid">
            <div class="cause-card most-likely">
                <div class="cause-card-header">
                    <span class="cause-icon">🔴</span>
                    <span class="cause-label">5 Most Likely Causes</span>
                </div>
                <ol>
{most_likely}
        </ol>
            </div>
            <div class="cause-card less-likely">
                <div class="cause-card-header">
                    <span class="cause-icon">🟡</span>
                    <span class="cause-label">5 Less Likely Causes</span>
                </div>
                <ol>
{less_likely}
        </ol>
            </div>
            <div class="cause-card new-cluster">
                <div class="cause-card-header">
                    <span class="cause-icon">🟣</span>
                    <span class="cause-label">5 New Cluster Causes</span>
                </div>
                <ol>
{new_cluster}
        </ol>
            </div>
        </div>
        
        <div class="ts-lookat"><strong>🔍 What to Look At / Take Note Of:</strong> {lookat}</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong>
            {solution}
        </div>
        <div class="ts-advice"><strong>💡 Personal Advice:</strong> {advice}
    </div>
        <div class="ts-footer-spacer"></div>
    </div>'''

def li(text, cls="cause-likely"):
    return f'            <li><span class="{cls}">{text}</span></li>'

# =============================================================================
# CATEGORY 3: SERVICE MESH (SM1-SM16, 16 issues)
# =============================================================================
CAT3 = """
    <!-- ═══ SM1-SM4: Kube-Proxy Replacement ═══ -->
    <div class="ts-section-header" id="ts-sm1">
        <h3>🔀 SM1 &mdash; SM4: Kube-Proxy Replacement Issues</h3>
    </div>
""" + ts_issue(3, "SERVICE MESH", "🟡", "sm1", "SM1",
    "kube-proxy Replacement Not Working — Services Unreachable",
    "anihpj-api ClusterIP (10.96.100.50) is unreachable from pods. kube-proxy was supposed to be replaced by Cilium eBPF, but service traffic times out. NodePort also broken.",
    "",
    "\n".join([
        li("kubeProxyReplacement not set to strict: Check `cilium config | grep kube-proxy-replacement`. Must be 'strict' for full replacement. If 'partial', only ClusterIP works."),
        li("Native devices not specified: Cilium needs to know which interfaces handle NodePort. `--set devices=eth0` or check `cilium config | grep devices`."),
        li("kube-proxy still running: `kubectl get pods -n kube-system -l k8s-app=kube-proxy`. If kube-proxy DaemonSet still exists, it conflicts. Delete it."),
        li("BPF NodePort not loaded: Check `cilium status | grep KubeProxyReplacement`. Should show 'Strict' with BPF NodePort. If not, daemon may have fallen back."),
        li("Kernel version < 5.10: Strict mode needs kernel 5.10+. Check `uname -r`. Below 5.10, NodePort via BPF is unreliable."),
    ]),
    "\n".join([
        li("iptables rules from previous kube-proxy still present: `iptables -t nat -L KUBE-SERVICES`", "cause-less-likely"),
        li("Cilium agent started before kube-proxy was fully removed causing race condition", "cause-less-likely"),
        li("NodePort range conflict with host port bindings", "cause-less-likely"),
        li("BPF map cilium_lb4_services exhausted (max service entries reached)", "cause-less-likely"),
        li("IPv6 DAD (Duplicate Address Detection) delaying service IP assignment", "cause-less-likely"),
    ]),
    "\n".join([
        li("kubeProxyReplacement never set: Default is 'disabled'. Set via Helm: `--set kubeProxyReplacement=strict`", "cause-new-cluster"),
        li("Helm install without devices: `--set devices='{eth0,eth1}'` missing — NodePort can't bind", "cause-new-cluster"),
        li("cilium-operator not assigning node addresses for NodePort", "cause-new-cluster"),
        li("RBAC missing for Cilium to watch Services/Endpoints", "cause-new-cluster"),
        li("kube-proxy mode still iptables in kubeadm config. Check `kubectl get cm kube-proxy -n kube-system`", "cause-new-cluster"),
    ]),
    "<code>cilium status | grep KubeProxyReplacement</code> — must say 'Strict (Kernel)'. <code>cilium service list</code> shows if services have backends. <code>kubectl get pods -n kube-system | grep kube-proxy</code> — should be empty. Note: if KPR falls back to partial, services still work but NodePort may not.",
    """<p>1. <code>cilium config view | grep kube-proxy-replacement</code> — verify it's 'strict'<br>
2. <code>kubectl delete ds -n kube-system kube-proxy</code> — remove kube-proxy if running<br>
3. <code>cilium config set kube-proxy-replacement strict</code> or Helm upgrade with flag<br>
4. Restart Cilium agents: <code>kubectl -n kube-system rollout restart ds/cilium</code><br>
5. Verify: <code>cilium connectivity test</code> — all service tests should pass</p>""",
    "KPR is the single most impactful Cilium feature — it replaces thousands of iptables rules with one BPF map lookup. Always go strict if your kernel supports it (5.10+). For anihpj: test with `curl http://anihpj-api.anihpj.svc` from the web pod to verify KPR is serving ClusterIP traffic."
) + "\n" + ts_issue(3, "SERVICE MESH", "🟡", "sm2", "SM2",
    "Maglev Backend Imbalance — Service Load Not Evenly Distributed",
    "anihpj-api service with 5 backend pods shows uneven traffic distribution. Pod-1 gets 45% of requests, Pod-5 gets 5%. Hubble flow logs confirm imbalance. Connection tracking shows sticky sessions.",
    "",
    "\n".join([
        li("Maglev table size (M) too small relative to backend count: Default M=65537. If M/N causes hash collisions, some backends get more slots. Check with `cilium service list`."),
        li("Connection tracking (conntrack) keeping sessions pinned: Long-lived connections stick to same backend. Not a bug — TCP session affinity. Check `cilium bpf ct list global`."),
        li("Backend weight misconfiguration: If service backends have different weights, imbalance is expected. Check `cilium service get <svc-id>`."),
        li("Maglev hash seed collision: Rare but possible — two backends hash to overlapping slot ranges. Only fixable by changing table size."),
        li("Unequal backend capacity: Some pods may be slower (CPU throttling), causing natural imbalance. Check pod resource usage."),
    ]),
    "\n".join([
        li("Cilium agent version mismatch causing different Maglev tables per node", "cause-less-likely"),
        li("Node-local backends preferred over remote (service affinity not set to 'none')", "cause-less-likely"),
        li("eBPF map pre-allocation causing stale backend entries after scale-down", "cause-less-likely"),
        li("Maglev permutation array corruption from concurrent map updates", "cause-less-likely"),
        li("Kernel entropy source depleted affecting Maglev hash distribution", "cause-less-likely"),
    ]),
    "\n".join([
        li("Default Maglev table size not tuned: M=65537 is fine for most. For 100+ backends, consider larger M via `cilium config set maglev-table-size 655373`", "cause-new-cluster"),
        li("Service created before all backends ready: Initial Maglev table computed with fewer backends", "cause-new-cluster"),
        li("externalTrafficPolicy: Local causing only local backends to receive NodePort traffic", "cause-new-cluster"),
        li("Topology-aware routing (service.kubernetes.io/topology-mode) restricting backend selection", "cause-new-cluster"),
        li("CiliumEndpointSlice not enabled causing slow backend updates", "cause-new-cluster"),
    ]),
    "<code>cilium service list</code> — shows backend count and weights. <code>cilium bpf lb list</code> — shows Maglev table slots per backend. Hubble: `hubble observe --to-service anihpj/anihpj-api` — count per backend. Note: Maglev is consistent hashing — it MINIMIZES disruption, not guarantees perfect balance.",
    """<p>1. Check actual distribution: <code>hubble observe --to-service anihpj/anihpj-api --output json | jq 'group_by(.destination_pod) | map({pod: .[0].destination_pod, count: length})'</code><br>
2. If imbalance >20%: <code>cilium bpf lb list</code> — verify Maglev table distribution<br>
3. For connection-heavy workloads: this is normal TCP behavior. Use HTTP/2 multiplexing or gRPC for better distribution<br>
4. Tune Maglev table: <code>cilium config set maglev-table-size 655373</code> (larger M = better distribution)<br>
5. Verify backend weights not set via <code>kubectl get endpoints anihpj-api -o yaml</code></p>""",
    "Perfect load balancing is an ideal, not reality. Maglev gives you consistent hashing — when a backend goes down, only connections to THAT backend are redistributed. This is far better than random which reshuffles everything. For anihpj: 5 backends with Maglev will show ±15% variation normally. If you see 50%+ skew, check if one pod is restarting frequently."
) + "\n" + ts_issue(3, "SERVICE MESH", "🟡", "sm3", "SM3",
    "Socket-Level Load Balancing Failing — L7 Proxy Bypass Issues",
    "Cilium socket LB is enabled but HTTP requests to anihpj-api are not being load balanced correctly. Connections go directly to same backend. L7 policies not enforced on socket-LB traffic.",
    "",
    "\n".join([
        li("Socket LB enabled but not compatible with L7 policies: Socket LB bypasses Envoy proxy. Any L7 policy automatically DISABLES socket LB for that endpoint. Check CNP for L7 rules."),
        li("Socket LB requires hostNetwork pods or specific cgroup configuration: Check if pod is in hostNetwork — socket LB only works for pods in their own netns."),
        li("Cilium agent socket-LB-enable flag not set: Check `cilium config | grep socket-lb`. Must be true."),
        li("Kernel < 5.7: Socket LB requires kernel 5.7+ for full cgroup hooks. Older kernels may not support all features."),
        li("Application using non-standard socket calls: Socket LB hooks connect()/sendmsg(). If app uses sendmmsg() or custom socket ops, it may bypass."),
    ]),
    "\n".join([
        li("BPF sockmap full — max entries reached for socket redirection", "cause-less-likely"),
        li("Cgroup v2 not enabled: `cat /proc/filesystems | grep cgroup2` — must be present", "cause-less-likely"),
        li("Socket buffer size mismatch between sender and receiver causing partial reads", "cause-less-likely"),
        li("TCP_NODELAY or TCP_QUICKACK socket options interfering with BPF hooks", "cause-less-likely"),
        li("Namespace-aware socket hook not attaching due to cgroup hierarchy permissions", "cause-less-likely"),
    ]),
    "\n".join([
        li("Socket LB not enabled at install: `--set socketLB.enabled=true` missing from Helm values", "cause-new-cluster"),
        li("Cgroup v2 not the default cgroup manager. Check containerd config: `SystemdCgroup = true`", "cause-new-cluster"),
        li("Cilium agent not restarted after enabling socket LB: ConfigMap changes need agent restart", "cause-new-cluster"),
        li("AppArmor/SELinux blocking BPF socket operations", "cause-new-cluster"),
        li("socketLB.hostNamespaceOnly=true set but pod not in host namespace", "cause-new-cluster"),
    ]),
    "<code>cilium config | grep socket-lb</code> — must be true. <code>cat /proc/filesystems | grep cgroup2</code> — must show cgroup2. Note: Socket LB is AUTO-DISABLED when L7 policies apply to the endpoint. Check your CNP before debugging socket LB.",
    """<p>1. Check if L7 policies exist: <code>kubectl get cnp -A | grep -i http</code><br>
2. Verify socket LB enabled: <code>cilium config | grep socket-lb</code><br>
3. Remove any L7 rules if you want socket LB (socket LB = L4 only by design)<br>
4. For anihpj with HTTP: if you need L7 policies (HTTP method filtering), you CANNOT use socket LB<br>
5. Monitor: <code>cilium bpf lb list --socket</code> shows socket-level backends</p>""",
    "Socket LB is fast (sub-microsecond) but limited to L4. For anihpj: if you're just doing round-robin to API backends with no L7 inspection, enable socket LB. If you need HTTP path-based routing or header inspection, use Envoy proxy via CiliumNetworkPolicy L7 rules — socket LB will auto-disable. You can't have both."
) + "\n" + ts_issue(3, "SERVICE MESH", "🟡", "sm4", "SM4",
    "DSR (Direct Server Return) Not Working — Asymmetric Routing",
    "DSR mode is configured but reply traffic from anihpj-api backends bypasses Cilium. Hubble shows forward traffic but no reverse traffic. Clients see connection timeouts for established connections.",
    "",
    "\n".join([
        li("DSR needs specific tunnel configuration: Cilium IPIP or Geneve DSR tunnel must be enabled. Check `cilium config | grep dsr`. DSR mode requires tunnel not disabled."),
        li("Backend node missing IPIP/Geneve DSR tunnel interface: `ip link show cilium_ipip` or `ip link show cilium_geneve`. Must be UP on ALL nodes."),
        li("Backend server responds directly to client without encapsulating: DSR requires the service VIP to be configured on the backend's loopback. If missing, reply goes with pod IP, not VIP."),
        li("Reverse path filter (rp_filter) dropping DSR replies: The reply comes from VIP but kernel sees it as spoofed. Set `net.ipv4.conf.all.rp_filter=0` on backends."),
        li("Client IP not reachable from backend network: DSR bypasses the original path — backend must have direct route to client."),
    ]),
    "\n".join([
        li("MTU issue: IPIP adds 20 bytes. If path MTU < 1500+20, packets get fragmented and dropped", "cause-less-likely"),
        li("Conntrack on backend node creating asymmetric flow entries", "cause-less-likely"),
        li("ARP responder for VIP not running on backend — DSR needs VIP to answer ARP", "cause-less-likely"),
        li("Cilium health endpoint reporting DSR mode disabled at runtime", "cause-less-likely"),
        li("Network ACL between client subnet and backend node blocking direct traffic", "cause-less-likely"),
    ]),
    "\n".join([
        li("DSR not enabled at install: `--set loadBalancer.mode=dsr` missing from Helm values", "cause-new-cluster"),
        li("Tunnel protocol not specified: DSR needs `--set tunnelProtocol=geneve` or ipip explicitly", "cause-new-cluster"),
        li("Cloud load balancer health checks failing because DSR bypasses LB return path", "cause-new-cluster"),
        li("NodePort DSR not enabled alongside ClusterIP DSR: inconsistent config", "cause-new-cluster"),
        li("kubeProxyReplacement not strict — DSR needs full KPR replacement", "cause-new-cluster"),
    ]),
    "<code>cilium config | grep -E 'dsr|tunnel|kube-proxy'</code>. <code>ip link show | grep -E 'ipip|geneve'</code>. Backend nodes: <code>ip addr show lo</code> — VIP should appear. <code>sysctl net.ipv4.conf.all.rp_filter</code> — must be 0. Note: DSR is advanced — only use if you have high-throughput services needing direct return.",
    """<p>1. Verify DSR enabled: <code>cilium config | grep dsr</code> — should show 'true'<br>
2. Check tunnel: <code>ip link show cilium_geneve</code> on all nodes<br>
3. Set rp_filter on backends: <code>sysctl -w net.ipv4.conf.all.rp_filter=0</code><br>
4. Verify VIP on backend loopback: <code>ip addr show lo | grep <VIP></code><br>
5. Test: <code>tcpdump -i any host <client-ip></code> on backend — verify direct return path</p>""",
    "DSR is the ultimate performance mode — backends reply directly to clients, bypassing the Cilium node entirely. But it's operationally complex. For anihpj: unless you're serving 100K+ req/s with large responses, stay with standard SNAT mode. DSR's main use case is video streaming or large file downloads where the return path bandwidth matters."
)

# =============================================================================
# CAT3 SM5-SM8: Ingress & Gateway API
# =============================================================================
CAT3 += """
    <!-- ═══ SM5-SM8: Ingress & Gateway API ═══ -->
    <div class="ts-section-header" id="ts-sm5">
        <h3>🚪 SM5 &mdash; SM8: Ingress &amp; Gateway API Issues</h3>
    </div>
""" + ts_issue(3, "SERVICE MESH", "🟡", "sm5", "SM5",
    "Cilium Ingress Controller — 503 Backend Unavailable",
    "anihpj-web Ingress is created but returns HTTP 503. `kubectl describe ingress` shows 'no healthy backends'. Pods are Running and ready. Service endpoints exist.",
    "",
    "\n".join([
        li("Ingress controller not enabled: `cilium config | grep ingress-controller` must be true. Or Helm: `--set ingressController.enabled=true`. Without it, Ingress resources are ignored."),
        li("TLS secret missing or misconfigured: If Ingress has TLS section, the referenced Secret must exist in same namespace. Check `kubectl get secret <tls-name>`."),
        li("Backend service port mismatch: Ingress backend.service.port must match the Service's targetPort (not just port). Check `kubectl get svc anihpj-web -o yaml`."),
        li("CiliumEnvoyConfig not auto-generated: Cilium creates a CEC from Ingress. Check `kubectl get ciliumenvoyconfig -A`. If missing, controller not processing the Ingress."),
        li("NetworkPolicy blocking Envoy-to-backend traffic: Envoy proxy runs as part of Cilium agent. If a CNP blocks traffic from 'host' or 'remote-node', it may block the proxy."),
    ]),
    "\n".join([
        li("Envoy proxy OOM — too many routes causing memory exhaustion", "cause-less-likely"),
        li("IngressClass not set to 'cilium': `kubectl get ingressclass` — must have cilium as default or Ingress must reference it", "cause-less-likely"),
        li("DNS resolution failure in Envoy: Envoy resolves backend via DNS. If CoreDNS is slow, Envoy times out", "cause-less-likely"),
        li("Multiple Ingress controllers installed (nginx + cilium) — conflicts for same Ingress", "cause-less-likely"),
        li("Envoy XDS config not pushed from Cilium agent (gRPC stream broken)", "cause-less-likely"),
    ]),
    "\n".join([
        li("ingressController.enabled not set in Helm values on fresh install", "cause-new-cluster"),
        li("IngressClass resource not created: Cilium CLI auto-creates but Helm may not", "cause-new-cluster"),
        li("loadBalancer.l7Backend=envoy not set (needed for Ingress)", "cause-new-cluster"),
        li("Cilium agent ServiceAccount missing RBAC for Ingress resources", "cause-new-cluster"),
        li("Envoy image not pulled: Check `kubectl describe pod -n kube-system -l k8s-app=cilium` for image pull errors", "cause-new-cluster"),
    ]),
    "<code>cilium status | grep Ingress</code> — shows if controller is running. <code>kubectl get ciliumenvoyconfig -A</code> — auto-generated from Ingress. <code>kubectl describe ingress <name></code> — shows backend health. Note: Cilium Ingress uses Envoy embedded in agent — no separate ingress pod.",
    """<p>1. Check Ingress status: <code>kubectl describe ingress anihpj-web</code><br>
2. Verify CEC exists: <code>kubectl get ciliumenvoyconfig -n anihpj</code><br>
3. Check Envoy config: <code>kubectl exec -n kube-system ds/cilium -- cilium-dbg envoy config</code><br>
4. Test backend directly: <code>kubectl exec deploy/web -- curl http://anihpj-api.anihpj.svc</code><br>
5. If TLS issue: verify cert is valid and matches hostname</p>""",
    "Cilium Ingress is simpler than deploying a separate ingress controller, but it's less feature-rich than dedicated solutions. For anihpj: if you need rate limiting, JWT auth, or WAF, use nginx-ingress or Istio. Cilium Ingress is great for simple L7 routing to services within the cluster."
) + "\n" + ts_issue(3, "SERVICE MESH", "🟡", "sm6", "SM6",
    "Gateway API — HTTPRoute Not Applying (404/No Routes)",
    "Gateway and HTTPRoute resources created for anihpj, but traffic gets 404 or defaults. `kubectl describe httproute` shows 'Accepted: False' or 'ResolvedRefs: False'. Gateway appears healthy.",
    "",
    "\n".join([
        li("Gateway API not enabled: `--set gatewayAPI.enabled=true` required. Check `cilium config | grep gateway-api`. Without it, Gateway resources are not processed."),
        li("HTTPRoute backendRef not resolving: The referenced Service must exist in the same namespace (or ReferenceGrant for cross-namespace). Check `kubectl get svc <backend-name>`."),
        li("Gateway listener protocol mismatch: If Gateway listener is HTTPS but HTTPRoute is HTTP, the route won't attach. Check listener protocol in Gateway spec."),
        li("Hostname mismatch: HTTPRoute hostnames must match Gateway listener hostnames. Wildcard rules: `*.example.com` matches `foo.example.com` but not `example.com`."),
        li("Gateway Class not 'cilium': The Gateway must reference gatewayClassName: cilium. Check `kubectl get gatewayclass cilium`."),
    ]),
    "\n".join([
        li("ReferenceGrant not created for cross-namespace backend references", "cause-less-likely"),
        li("HTTPRoute rule order: rules are evaluated top-to-bottom. A catch-all rule first blocks specific rules", "cause-less-likely"),
        li("Gateway status not updated due to controller leader election delay", "cause-less-likely"),
        li("CRDs for Gateway API v1 not installed: `kubectl get crd | grep gateway.networking.k8s.io`", "cause-less-likely"),
        li("Multiple Gateways with overlapping listeners — port conflict", "cause-less-likely"),
    ]),
    "\n".join([
        li("gatewayAPI.enabled not set during Helm install", "cause-new-cluster"),
        li("Gateway API CRDs not installed: `kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/...`", "cause-new-cluster"),
        li("GatewayClass 'cilium' not created: Helm chart should auto-create", "cause-new-cluster"),
        li("Cilium agent RBAC missing for gateway.networking.k8s.io resources", "cause-new-cluster"),
        li("Kubernetes version < 1.24: Gateway API needs recent K8s", "cause-new-cluster"),
    ]),
    "<code>kubectl get gateway -A</code> — check status. <code>kubectl describe httproute <name> -n <ns></code> — see condition messages. <code>kubectl get gatewayclass cilium</code> — must exist. Note: Gateway API is the future — more expressive than Ingress but more complex.",
    """<p>1. Verify Gateway API enabled: <code>cilium config | grep gateway-api</code><br>
2. Check CRDs: <code>kubectl get crd | grep gateway.networking</code><br>
3. Debug HTTPRoute: <code>kubectl describe httproute <name> -n anihpj</code><br>
4. Check Gateway status: <code>kubectl describe gateway <name></code><br>
5. Verify backend: <code>kubectl get svc,ep -n anihpj | grep <service></code></p>""",
    "Gateway API replaces the aging Ingress API with a role-oriented model. For anihpj: if you're exploring Cilium, try both Ingress and Gateway API — the concepts translate. Gateway API is better for multi-team clusters where platform team manages Gateways and dev teams manage HTTPRoutes."
)

# =============================================================================
# Continue with SM7-SM16, CAT4, CAT5, CAT6, CAT7, CAT8
# This script is very long — let me continue generating
# =============================================================================

# SM7-SM8
CAT3 += ts_issue(3, "SERVICE MESH", "🟡", "sm7", "SM7",
    "TLS Termination in Cilium — Certificate Not Applied",
    "TLS Secret created and referenced in CiliumNetworkPolicy, but Hubble shows plaintext HTTP (not TLS). Envoy not terminating TLS. Clients connecting over HTTP see connection reset.",
    "",
    "\n".join([
        li("Secret format wrong: Cilium expects 'tls.crt' and 'tls.key' keys in the Secret. PEM format required. Check `kubectl get secret <name> -o jsonpath='{.data}' | base64 -d`."),
        li("CNP TLS rule not referencing correct Secret: `terminatingTLS.secret.name` and `terminatingTLS.secret.namespace` must match exactly. Case-sensitive."),
        li("Same secret referenced as both originatingTLS and terminatingTLS: Cilium needs separate Secrets for upstream vs downstream TLS."),
        li("Envoy not reloading after Secret update: TLS Secrets have a cache TTL. Force reload: `kubectl delete pod -n kube-system -l k8s-app=cilium` on relevant nodes."),
        li("Cert CN/SAN doesn't match the hostname used by clients: Envoy validates SNI against cert. Mismatch = TLS handshake failure."),
    ]),
    "\n".join([
        li("Secret type not 'kubernetes.io/tls': Cilium auto-detects but may fail for opaque Secrets", "cause-less-likely"),
        li("Intermediate cert missing from tls.crt — full chain not provided (root CA not needed)", "cause-less-likely"),
        li("Cert expired: `openssl x509 -in cert.pem -noout -dates`. Cilium/Envoy doesn't auto-check expiry in logs", "cause-less-likely"),
        li("Private key encrypted with passphrase — Envoy doesn't support encrypted keys at rest", "cause-less-likely"),
        li("Mutual TLS (mTLS) configured but clients not sending client certificates", "cause-less-likely"),
    ]),
    "\n".join([
        li("TLS Secret not created: Step skipped during deployment. Generate with cert-manager or manually", "cause-new-cluster"),
        li("cert-manager not installed: If using cert-manager annotations, the operator must be running", "cause-new-cluster"),
        li("Let's Encrypt staging cert used in production — not trusted by clients", "cause-new-cluster"),
        li("Helm `tls.secretsBackend=k8s` not set (default is k8s — fine for most)", "cause-new-cluster"),
        li("Cilium agent doesn't have RBAC to read Secrets in the namespace", "cause-new-cluster"),
    ]),
    "<code>kubectl get secret <tls-name> -o yaml</code> — verify keys exist. <code>cilium-dbg envoy config</code> — check if TLS context loaded. <code>openssl s_client -connect <pod-ip>:443</code> — test TLS. Note: Cilium TLS is implemented via Envoy, not in eBPF directly.",
    """<p>1. Verify Secret: <code>kubectl get secret anihpj-tls -n anihpj -o yaml</code><br>
2. Check Envoy TLS config: <code>kubectl exec ds/cilium -- cilium-dbg envoy config | grep tls</code><br>
3. Test TLS: <code>openssl s_client -connect <service-ip>:443 -servername anihpj.example.com</code><br>
4. Check cert validity: <code>kubectl get secret anihpj-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout</code><br>
5. Force reload if Secret was updated: restart Cilium agent</p>""",
    "TLS in Cilium is Envoy-based, not eBPF. This means you get full TLS 1.3 with cipher negotiation. For anihpj: use cert-manager to auto-provision Let's Encrypt certs, then reference the Secret in your CNP. Remember: terminatingTLS = downstream (clients → service), originatingTLS = upstream (service → backend)."
) + "\n" + ts_issue(3, "SERVICE MESH", "🟡", "sm8", "SM8",
    "Canary Deployments — Traffic Split Not Working",
    "CiliumNetworkPolicy with traffic split (canary) configured for anihpj-api: 90% to stable, 10% to canary. But all traffic still goes to stable. Hubble shows no traffic to canary pods.",
    "",
    "\n".join([
        li("Canary backend labels don't match: CNP toServices[].toPorts[].rules.http[].header matches must select the canary backend. Check pod labels vs CNP selector."),
        li("Traffic split needs L7 policy: Canary routing works at HTTP level. If CNP only has L3/L4 rules, traffic splitting won't engage. Must have http rules section."),
        li("Canary service not annotated properly: Both stable and canary services need correct labels. CNP uses serviceName in toServices."),
        li("Weight not specified or sum != 100: Traffic split weights must be explicitly set. Missing weight defaults may cause all traffic to one backend."),
        li("Hubble filtering: Check `hubble observe --to-ns anihpj --http-status 200` — verify canary pod IPs appear. May need port filter."),
    ]),
    "\n".join([
        li("Envoy config not updated: XDS push from Cilium agent to Envoy may be delayed (few seconds normal)", "cause-less-likely"),
        li("Cookie stickiness overriding weight-based routing: If session affinity enabled, users stick to same backend", "cause-less-likely"),
        li("HTTP/2 multiplexing: Single connection reuses same backend — canary traffic appears stuck", "cause-less-likely"),
        li("CiliumEndpointSlice not enabled: Slow endpoint propagation delays canary backend addition", "cause-less-likely"),
        li("DNS caching on client side pointing to old service IP", "cause-less-likely"),
    ]),
    "\n".join([
        li("HTTP L7 policy not writable — Cilium L7 policies need Envoy. Check if envoy config loaded", "cause-new-cluster"),
        li("Canary service selector not correct in first deployment", "cause-new-cluster"),
        li("Traffic split configured in wrong direction (egress vs ingress)", "cause-new-cluster"),
        li("Cilium version doesn't support traffic splitting (needs 1.12+)", "cause-new-cluster"),
        li("Missing --set loadBalancer.l7Backend=envoy during install", "cause-new-cluster"),
    ]),
    "<code>kubectl get cnp -o yaml | grep -A20 http</code> — verify L7 section. <code>cilium-dbg envoy config | grep -A10 weighted</code> — check Envoy route weights. Hubble: `hubble observe --to-pod anihpj/canary-api` — filter to canary pod only. Note: Traffic split is HTTP-only (no TCP/UDP splitting).",
    """<p>1. Verify L7 rules exist in CNP: must have http section with headers/path rules<br>
2. Check canary labels: <code>kubectl get pods -l version=canary -n anihpj</code><br>
3. Validate Envoy config: <code>kubectl exec ds/cilium -- cilium-dbg envoy config dump</code><br>
4. Test canary directly: <code>curl -H 'X-Canary: true' http://anihpj-api.anihpj.svc</code><br>
5. Monitor: <code>hubble observe --to-fqdn anihpj-api.anihpj.svc -n anihpj</code></p>""",
    "Canary in Cilium is L7 HTTP-based. For anihpj: set up two deployments (anihpj-api-stable, anihpj-api-canary) with different labels, one service selecting both, and a CNP with HTTP header matching for canary routing. This is how you do zero-downtime deployments with traffic splitting."
)

# Now SM9-SM12: Bandwidth Manager & BBR
CAT3 += """
    <!-- ═══ SM9-SM12: Bandwidth Manager & BBR ═══ -->
    <div class="ts-section-header" id="ts-sm9">
        <h3>📊 SM9 &mdash; SM12: Bandwidth Manager &amp; BBR</h3>
    </div>
""" + ts_issue(3, "SERVICE MESH", "🟡", "sm9", "SM9",
    "Bandwidth Manager — Rate Limiting Not Applied",
    "CiliumNetworkPolicy sets egress bandwidth: 10Mbps for anihpj-api pods, but `iperf3` tests show unlimited throughput. Hubble shows no bandwidth enforcement. Pods transfer at full line rate.",
    "",
    "\n".join([
        li("Bandwidth Manager not enabled at install: `--set bandwidthManager.enabled=true` required. Check `cilium config | grep bandwidth-manager`. If false, bandwidth annotations/policies ignored."),
        li("Kernel < 5.1: Bandwidth Manager needs EDT (Earliest Departure Time) in kernel. Check `uname -r`. Below 5.1, EDT not available."),
        li("BBR enabled but kernel < 5.18: `--set bandwidthManager.bbr=true` needs kernel 5.18+ for pod-level BBR. Without it, FQ works but BBR doesn't."),
        li("CNP bandwidth field in wrong section: Bandwidth goes under `egress[]` with `bandwidth: \"10Mbps\"` — not as a separate field."),
        li("Interface not in devices list: Bandwidth Manager attaches to specified devices. Check `cilium config | grep devices`. If pod's host veth isn't on a managed device, no enforcement."),
    ]),
    "\n".join([
        li("FQ (Fair Queue) pacing not compatible with tunnel mode for some kernel versions", "cause-less-likely"),
        li("BPF map cilium_bandwidth_map full — per-endpoint limit reached", "cause-less-likely"),
        li("TCP congestion window overriding EDT pacing: BBR may inflate cwnd beyond rate limit", "cause-less-likely"),
        li("iperf3 using UDP bypasses EDT (EDT works on TCP — UDP needs different mechanism)", "cause-less-likely"),
        li("Multiple CNP bandwidth rules conflicting for same endpoint", "cause-less-likely"),
    ]),
    "\n".join([
        li("bandwidthManager.enabled not in Helm values on fresh install", "cause-new-cluster"),
        li("Kernel too old for EDT: minimum 5.1, recommend 5.10+", "cause-new-cluster"),
        li("BBR module not loaded: `modprobe tcp_bbr` and `sysctl net.ipv4.tcp_congestion_control=bbr`", "cause-new-cluster"),
        li("Cilium agent not restarted after enabling bandwidth manager via ConfigMap", "cause-new-cluster"),
        li("Kubernetes networking model conflicts: some CNI chaining modes don't pass through Cilium for egress", "cause-new-cluster"),
    ]),
    "<code>cilium status | grep Bandwidth</code> — shows if manager is active. <code>tc -s qdisc show dev lxc_&lt;id&gt;</code> — look for FQ qdisc. <code>cilium-dbg bpf bandwidth list</code> — shows per-endpoint rate limits. Note: Bandwidth is a CiliumNetworkPolicy feature, not NetworkPolicy.",
    """<p>1. Enable bandwidth manager: <code>cilium config set bandwidth-manager true</code> or Helm upgrade<br>
2. Verify: <code>cilium status | grep Bandwidth</code> — should say 'OK'<br>
3. Check EDT qdisc: <code>tc qdisc show dev lxc_&lt;endpoint-id&gt;</code> — should show fq<br>
4. Test: <code>kubectl exec deploy/web -- iperf3 -c anihpj-api -t 10</code> — measure actual throughput<br>
5. For BBR: <code>sysctl net.ipv4.tcp_congestion_control=bbr</code> on ALL nodes</p>""",
    "Bandwidth Manager is underrated — it gives you per-pod QoS without a service mesh. For anihpj: limit batch job egress so they don't saturate the NIC. But remember: it's incompatible with L7 policies (same as Egress Gateway). If you need L7, bandwidth enforcement won't work."
)

print("CAT3 SM1-SM9 generated...")

# Write the full script will be very long. Let me save in parts.
# For now let me just generate and insert CAT3 first.

with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Find ts-cat3 section and insert content after it
marker = '<section class="chapter-section" id="ts-cat3">\n<h2><span>Category 3: Service Mesh</span><span class="chapter-badge">SM1-SM16</span></h2>\n<div class="chapter-intro"><p>16 troubleshooting issues covering KPR, Maglev, socket LB, DSR, Ingress/Gateway API, TLS, canary, bandwidth manager, BBR, and sidecar-free mesh.</p></div>\n</section>'

# For now just verify the marker exists
if marker in content:
    print("✅ ts-cat3 marker found — ready for CAT3 insertion")
else:
    print("❌ ts-cat3 marker not found!")
