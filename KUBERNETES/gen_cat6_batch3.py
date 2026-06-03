#!/usr/bin/env python3
"""Category 6: Cluster Mesh — Batch 3: S81-S84 (Egress Gateway)"""

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_short, verify_detail, tenet_steps, tenet_text, before_outputs, after_outputs):
    ei = ''.join(f'<div class="lookat-item"><span class="li-check {"pass" if t=="pass" else "fail"}">{"✓" if t=="pass" else "✗"}</span><span>{txt}</span></div>\n' for t,txt in error_items)
    di = ''.join(f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n' for num,label,cmd,ftype,ftext in debug_items)
    tf = ''.join(f'<div class="tenet-step"><div class="step-num">{chr(0x2460+i)}</div><div class="step-label">{lbl}</div></div>\n' for i,lbl in enumerate(tenet_steps))
    bo = '\n'.join(before_outputs)
    ao = '\n'.join(after_outputs)

    return f'''    <!-- ═══════════════ S{n}: {title} ═══════════════ -->
    <div class="scenario-block" id="sc-s{n}">
        <div class="sc-header">
            <div class="sc-badge">S{n}</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{n} — Category 6: Cluster Mesh</div>
                <h4>{title}</h4>
                <div class="sc-desc"><strong>The Problem:</strong> {desc}</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML (contains the bug)</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-code')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-code" class="language-bash">{deploy_code}</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step error-spot">
                <div class="sc-step-num">⚠</div>
                <div class="sc-step-content">
                    <h4>⚠️ Observe the Error — Spot What's Broken</h4>
                    {ei}
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    {di}
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — {fix_desc}</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — {fix_desc.lower()}</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-fix')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-fix" class="language-bash">{fix_code}</code></pre>
                    </div>
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num answer">✓</div>
                <div class="sc-step-content">
                    <div class="sc-resolution">
                        <h4>✅ Verify — {verify_short}</h4>
                        <p>{verify_detail}</p>
                    </div>
                </div>
            </div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{n}')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa{n}">
                <h5>🧠 Diagnostic Tenet (Thought Process)</h5>
                <div class="tenet-flow">{tf}</div>
                <p><strong>Tenet:</strong> {tenet_text}</p>
                <h5>📟 Command Outputs — Error State (BEFORE fix)</h5>
                {bo}
                <h5>📟 Command Outputs — AFTER Fix</h5>
                {ao}
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div>
                <div class="sc-step-content">
                    <h4 style="color: #8b949e;">🧹 Cleanup — Delete All Resources</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — copy &amp; paste to clean up</span>
                            <button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-cleanup')">📋 Copy</button>
                        </div>
                        <pre><code id="sc-s{n}-cleanup" class="language-bash"><span class="token comment"># Delete the namespace — cascades everything inside</span>
kubectl delete namespace anihpj

<span class="token comment"># Verify cleanup</span>
kubectl get all -n anihpj</code></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

# S81
s81 = sc(81,
    "Debug Egress Gateway Not Routing anihpj Outbound Traffic",
    "You configure Egress Gateway to route anihpj outbound traffic through a specific node, but <strong>traffic exits from random nodes</strong> instead of the gateway node. External services see varying source IPs. Your job: fix the Egress Gateway to enforce consistent source IP masquerading.",
    r"""<span class="token comment"># Enable Egress Gateway on Cilium</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set egressGateway.enabled=true

<span class="token comment"># Configure Egress NAT policy for anihpj</span>
cat > egress-policy.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumEgressGatewayPolicy
metadata:
  name: anihpj-egress
spec:
  selectors:
  - podSelector:
      matchLabels:
        app: anihpj
  destinationCIDRs:
  - "0.0.0.0/0"
  egressGateway:
    nodeSelector:
      matchLabels:
        egress-gateway: "true"
    egressIP: 203.0.113.10
EOF
kubectl apply -f egress-policy.yaml

<span class="token comment"># Label gateway node</span>
kubectl label node worker-1 egress-gateway=true

<span class="token comment"># Deploy anihpj</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj --replicas=2

<span class="token comment"># ❌ BUG: Traffic exits from random nodes</span>
kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me
<span class="token comment"># Returns node-2 IP (not gateway node-1 IP)!</span>""",
    [
        ("pass", "<strong>1.</strong> Egress Gateway enabled: <code>cilium config | grep egress-gateway</code> → enabled ✅"),
        ("pass", "<strong>2.</strong> Gateway node labeled: <code>kubectl get nodes -l egress-gateway=true</code> → worker-1 ✅"),
        ("fail", "<strong>3.</strong> Traffic exits wrong node: <code>curl ifconfig.me</code> → <strong>returns random node IP, not gateway egressIP</strong> ❌"),
        ("fail", "<strong>4.</strong> Source IP not masqueraded: <strong>egressIP 203.0.113.10 not used — pod's original IP visible</strong> ❌"),
        ("fail", "<strong>5.</strong> Gateway policy not enforcing: <code>cilium egress-gateway status</code> → <strong>0 active policies, 0 matched endpoints</strong> ❌"),
    ],
    [
        (1, "Check Egress Gateway policy status:", "kubectl get cegp -A", "discovery", "Policy exists but CiliumEgressGatewayPolicy status shows '0 matched' — the podSelector may not match any pods"),
        (2, "Verify pod labels match the policy selector:", "kubectl get pods -n anihpj --show-labels", "discovery", "Pods have app=anihpj — but the policy uses matchLabels: {app: anihpj} which should match; check if the policy is in the correct namespace"),
        (3, "Check if the policy is namespace-scoped:", "kubectl get cegp anihpj-egress -o yaml | grep -E 'namespace|podSelector'", "discovery", "CiliumEgressGatewayPolicy is cluster-scoped (not namespaced) — but podSelector needs namespaceSelector to target specific namespaces or use matchExpressions"),
        (4, "Verify gateway node has the egress IP configured:", "kubectl get node worker-1 -o yaml | grep egress-gateway", "discovery", "Node has label but egressIP 203.0.113.10 may not be assigned to the node's network interface — the IP must exist on the gateway node"),
        (5, "Root cause identified:", "Egress Gateway policy missing namespace selector; gateway IP not on node interface", "root-cause", "Egress Gateway requires: 1) Policy must specify BOTH podSelector AND namespaceSelector (or empty namespaceSelector {} for all namespaces), 2) The egressIP must be assigned to the gateway node's network interface (secondary IP or loopback alias), and 3) The gateway node must have IP forwarding enabled for the egress IP to be used as source"),
    ],
    r"""<span class="token comment"># Fix 1: Add namespace selector to the policy</span>
kubectl patch cegp anihpj-egress --type=merge -p '{"spec":{"selectors":[{"namespaceSelector":{"matchLabels":{"kubernetes.io/metadata.name":"anihpj"}},"podSelector":{"matchLabels":{"app":"anihpj"}}}]}}'

<span class="token comment"># Fix 2: Add the egress IP to the gateway node</span>
kubectl exec -n kube-system ds/cilium -- ip addr add 203.0.113.10/32 dev eth0

<span class="token comment"># Fix 3: Enable IP forwarding on gateway node</span>
kubectl exec -n kube-system ds/cilium -- sysctl -w net.ipv4.ip_forward=1

<span class="token comment"># Fix 4: Verify policy activates</span>
cilium egress-gateway status""",
    "Egress Gateway Enforcing",
    "Traffic Exits via Gateway Node with Correct IP",
    'All anihpj outbound traffic now exits through <strong>worker-1</strong> with source IP <strong>203.0.113.10</strong>. <code>cilium egress-gateway status</code> shows active policy with matched endpoints. <code>curl ifconfig.me</code> from any anihpj pod returns the consistent egress IP.',
    ["Egress policy created → traffic exits random nodes", "Check policy → 0 matched endpoints", "Missing namespaceSelector in policy", "Add namespaceSelector + configure egressIP on node", "All traffic exits via gateway with consistent IP"],
    "CiliumEgressGatewayPolicy needs both <strong>podSelector AND namespaceSelector</strong> (even if namespaceSelector is empty {} for all namespaces). Without namespaceSelector, the policy doesn't match any pods. The egressIP must be configured on the gateway node's interface — Cilium doesn't auto-assign it. IP forwarding must be enabled on the gateway node for NAT to work correctly.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me\n<span class="output">198.51.100.45    ← Random node IP, not gateway egressIP!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium egress-gateway status\n<span class="output">Egress Gateway: enabled\n  Active Policies: 0    ← Policy not matching any pods!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me\n<span class="output">203.0.113.10    ✅ Consistent egress IP via gateway!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium egress-gateway status\n<span class="output">Egress Gateway: enabled\n  Active Policies: 1 (anihpj-egress: 2 endpoints matched)    ✅</span></div>',
    ]
)

# S82
s82 = sc(82,
    "Fix Egress Gateway Source IP Not Being Masqueraded",
    "Egress Gateway routes traffic through the gateway node, but the <strong>source IP is the pod IP, not the egress IP</strong>. External services reject traffic from private pod IPs. Your job: fix source IP masquerading so outbound traffic uses the gateway's egress IP.",
    r"""<span class="token comment"># Egress Gateway policy created, traffic flows through gateway node</span>
<span class="token comment"># but source IP is still the pod IP</span>

kubectl exec -n anihpj deploy/web -- curl -s http://httpbin.org/ip
<span class="token comment"># {"origin": "10.0.1.15"}    ← Pod IP, not egress IP! External services reject private IPs</span>

<span class="token comment"># Check if masquerading is working</span>
kubectl logs -n kube-system ds/cilium | grep -i masquerade
<span class="token comment"># "Egress Gateway masquerading: disabled"</span>""",
    [
        ("pass", "<strong>1.</strong> Egress Gateway policy active: <code>cilium egress-gateway status</code> → policy matched ✅"),
        ("pass", "<strong>2.</strong> Traffic routed via gateway: <strong>packets exit through gateway node</strong> ✅"),
        ("fail", "<strong>3.</strong> Source IP not masqueraded: <code>curl httpbin.org/ip</code> → <strong>returns pod IP (10.0.x), not egress IP</strong> ❌"),
        ("fail", "<strong>4.</strong> External services reject traffic: <strong>private pod IPs (10.0.x) dropped by external firewalls</strong> ❌"),
        ("fail", "<strong>5.</strong> Masquerade not enabled: <code>cilium config | grep masquerade</code> → <strong>enable-ip-masq-agent: false</strong> ❌"),
    ],
    [
        (1, "Check masquerading configuration:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -A3 masquerade", "discovery", "enable-ip-masq-agent: \"false\" — IP masquerading is disabled; the egress gateway routes traffic but does not NAT the source IP"),
        (2, "Verify egress masquerade interface:", "kubectl get cm -n kube-system cilium-config -o yaml | grep egress-masquerade", "discovery", "egress-masquerade-interfaces not set — Cilium doesn't know which interface to use for source NAT on the gateway node"),
        (3, "Check if the gateway node can SNAT correctly:", "kubectl exec -n kube-system ds/cilium -- iptables -t nat -L POSTROUTING | grep MASQUERADE", "discovery", "No MASQUERADE rule for egress traffic — Cilium relies on BPF-based masquerading, not iptables; BPF masquerading must be explicitly enabled"),
        (4, "Verify BPF masquerade is enabled:", "cilium config | grep bpf-masquerade", "discovery", "bpf-masquerade: false — BPF-based masquerading is the most efficient; without it, fallback to iptables may not be configured"),
        (5, "Root cause identified:", "IP masquerading is disabled — traffic is routed but source IP is not rewritten", "root-cause", "Egress Gateway routing and SNAT are separate features. The gateway policy routes traffic through a specific node, but without masquerading enabled, the source IP remains the pod IP. Enable BPF masquerade and specify the egress interface to rewrite source IP to the gateway node's egress IP"),
    ],
    r"""<span class="token comment"># Fix 1: Enable BPF masquerading</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set bpf.masquerade=true \
  --set egressMasqueradeInterfaces=eth0

<span class="token comment"># Fix 2: Configure IP masquerade agent for egress</span>
kubectl patch cm -n kube-system cilium-config \
  --patch '{"data":{"enable-ip-masq-agent":"true"}}'

<span class="token comment"># Fix 3: Restart Cilium agents to pick up masquerade config</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system

<span class="token comment"># Fix 4: Verify source IP is now masqueraded</span>
kubectl exec -n anihpj deploy/web -- curl -s http://httpbin.org/ip""",
    "Source IP Masqueraded",
    "Outbound Traffic Uses Gateway Egress IP",
    'All anihpj outbound traffic now exits with source IP <strong>203.0.113.10</strong> (the egress IP). <code>curl httpbin.org/ip</code> returns the egress IP, not the pod IP. BPF masquerading is active on the <code>eth0</code> interface. External services accept traffic from the routable egress IP.',
    ["Traffic routed via gateway but source IP unchanged", "enable-ip-masq-agent: false", "BPF masquerade not enabled", "Enable BPF masquerade + set egress interface", "Source IP rewritten to egress IP"],
    "Egress Gateway <strong>routing</strong> (which node) and <strong>SNAT</strong> (source IP rewrite) are separate. The policy controls routing; masquerading controls IP rewriting. Enable <code>bpf.masquerade=true</code> for efficient BPF-based SNAT. Set <code>egressMasqueradeInterfaces</code> to the interface that has the egress IP. Without masquerading, the pod's private IP (10.0.x) leaks to external networks and gets dropped.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s http://httpbin.org/ip\n<span class="output">{"origin": "10.0.1.15"}    ← Pod private IP — external services reject this!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium config | grep -E "masquerade|egress"\n<span class="output">enable-ip-masq-agent             false\nbpf-masquerade                   false    ← Both disabled!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s http://httpbin.org/ip\n<span class="output">{"origin": "203.0.113.10"}    ✅ Egress IP — external services accept!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium config | grep -E "masquerade|egress"\n<span class="output">enable-ip-masq-agent             true\nbpf-masquerade                   true\nenable-bpf-masquerade            true    ✅ Masquerading active!</span></div>',
    ]
)

# S83
s83 = sc(83,
    "Configure Egress NAT Policy for anihpj to Use Specific IP",
    "You need different anihpj components to use <strong>different egress IPs</strong>. The web tier should use one public IP, the api tier another. But the current Egress Gateway policy applies the same IP to all pods. Your job: create per-tier egress NAT policies with specific source IPs.",
    r"""<span class="token comment"># Current: Single egress policy for all anihpj pods</span>
cat > single-egress.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumEgressGatewayPolicy
metadata:
  name: anihpj-egress
spec:
  selectors:
  - namespaceSelector: {}
    podSelector:
      matchLabels: {app: anihpj}
  destinationCIDRs: ["0.0.0.0/0"]
  egressGateway:
    nodeSelector: {egress-gateway: "true"}
    egressIP: 203.0.113.10
EOF

<span class="token comment"># ❌ BUG: All pods share the same egress IP — can't differentiate by tier</span>
kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me
<span class="token comment"># 203.0.113.10</span>
kubectl exec -n anihpj deploy/api -- curl -s ifconfig.me
<span class="token comment"># 203.0.113.10    ← Same IP! Need different IPs per tier</span>""",
    [
        ("pass", "<strong>1.</strong> Egress Gateway enabled and working: <code>cilium egress-gateway status</code> → active policies ✅"),
        ("pass", "<strong>2.</strong> Traffic masqueraded correctly: <code>curl ifconfig.me</code> → returns egress IP ✅"),
        ("fail", "<strong>3.</strong> All pods share same IP: <code>curl ifconfig.me</code> from web and api → <strong>both return 203.0.113.10</strong> ❌"),
        ("fail", "<strong>4.</strong> Cannot differentiate traffic by source: <strong>external API rate limiting treats all anihpj pods as one client</strong> ❌"),
        ("fail", "<strong>5.</strong> Single policy for all pods: <strong>no per-tier egress NAT — web and api need separate egress IPs</strong> ❌"),
    ],
    [
        (1, "Check if multiple policies can coexist:", "kubectl get cegp -A", "discovery", "Currently one policy — Cilium supports multiple CiliumEgressGatewayPolicy resources; each can target different podSelectors with different egress IPs"),
        (2, "Create per-tier policies with different selectors:", "For web tier: podSelector: {tier: web}; For api tier: podSelector: {tier: api}", "discovery", "Each policy needs a unique name and different podSelector to target specific tiers"),
        (3, "Verify the gateway node has multiple egress IPs:", "ip addr show eth0 | grep inet", "discovery", "Only 203.0.113.10 configured — need to add 203.0.113.11 for the second tier's egress IP"),
        (4, "Check if policies overlap correctly:", "CiliumEgressGatewayPolicy with overlapping podSelectors uses first-match semantics; more specific selectors should be listed first", "discovery", "Policy order matters — if a catch-all policy matches first, more specific policies are ignored; create tier-specific policies with higher priority"),
        (5, "Root cause identified:", "Single catch-all policy — need multiple policies with per-tier selectors and egress IPs", "root-cause", "Cilium supports multiple Egress Gateway policies with different selectors. Create separate policies for web and api tiers with their own podSelectors, egressIPs, and (optionally) different gateway nodes. Add the additional egress IPs to the gateway node's interface"),
    ],
    r"""<span class="token comment"># Fix 1: Add second egress IP to gateway node</span>
kubectl exec -n kube-system ds/cilium -- ip addr add 203.0.113.11/32 dev eth0

<span class="token comment"># Fix 2: Create per-tier egress policies</span>
cat > web-egress.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumEgressGatewayPolicy
metadata:
  name: anihpj-web-egress
spec:
  selectors:
  - namespaceSelector: {}
    podSelector:
      matchLabels: {app: anihpj, tier: web}
  destinationCIDRs: ["0.0.0.0/0"]
  egressGateway:
    nodeSelector: {egress-gateway: "true"}
    egressIP: 203.0.113.10
EOF

cat > api-egress.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumEgressGatewayPolicy
metadata:
  name: anihpj-api-egress
spec:
  selectors:
  - namespaceSelector: {}
    podSelector:
      matchLabels: {app: anihpj, tier: api}
  destinationCIDRs: ["0.0.0.0/0"]
  egressGateway:
    nodeSelector: {egress-gateway: "true"}
    egressIP: 203.0.113.11
EOF

kubectl delete cegp anihpj-egress
kubectl apply -f web-egress.yaml -f api-egress.yaml""",
    "Per-Tier Egress IPs",
    "Web and API Use Different Egress IPs",
    'Web pods now exit with <strong>203.0.113.10</strong>. API pods exit with <strong>203.0.113.11</strong>. <code>cilium egress-gateway status</code> shows 2 active policies with separate endpoint matches. External services can differentiate traffic and apply per-tier rate limiting.',
    ["Single egress policy → all pods same IP", "Need per-tier egress IPs for web and api", "Multiple CEGPs supported with different selectors", "Add second egress IP + create per-tier policies", "Web→203.0.113.10, API→203.0.113.11"],
    "Create separate <strong>CiliumEgressGatewayPolicy</strong> resources for different workload tiers. Each policy specifies its own podSelector (using more specific labels like tier=web vs tier=api) and egressIP. The gateway node must have all egress IPs configured on its interface. Delete any catch-all policy that would match all pods before the tier-specific policies.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me\n<span class="output">203.0.113.10</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/api -- curl -s ifconfig.me\n<span class="output">203.0.113.10    ← Same IP as web — can\'t differentiate!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/web -- curl -s ifconfig.me\n<span class="output">203.0.113.10    ✅ Web tier egress IP</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj deploy/api -- curl -s ifconfig.me\n<span class="output">203.0.113.11    ✅ API tier egress IP — different!</span></div>',
    ]
)

# S84
s84 = sc(84,
    "Debug Cluster Mesh Performance Degradation Under Load",
    "Under high traffic load, <strong>cross-cluster latency spikes and connections drop</strong>. Cluster Mesh performance degrades significantly when anihpj scales to 50+ pods. Your job: diagnose the performance bottleneck and optimize Cluster Mesh for production load.",
    r"""<span class="token comment"># Cluster Mesh working but performance degrades under load</span>
cilium clustermesh status
<span class="token comment"># Both clusters: OK</span>

<span class="token comment"># Scale anihpj to 50 pods</span>
kubectl scale deployment web -n anihpj --replicas=50

<span class="token comment"># ❌ BUG: Cross-cluster latency spikes, connections drop</span>
kubectl exec -n anihpj deploy/web -- curl -s -o /dev/null -w '%{time_total}\n' \
  http://api-service.anihpj.svc.global
<span class="token comment"># 2.5s, 5.1s, timeout — latency spikes under load!</span>""",
    [
        ("pass", "<strong>1.</strong> Cluster Mesh connected: <code>cilium clustermesh status</code> → OK ✅"),
        ("pass", "<strong>2.</strong> Cross-cluster services resolve: <code>nslookup api-service.anihpj.svc.global</code> → resolves ✅"),
        ("fail", "<strong>3.</strong> Latency spikes under load: <code>curl -w '%{time_total}'</code> → <strong>2-5 seconds, intermittent timeouts</strong> ❌"),
        ("fail", "<strong>4.</strong> Connections dropped: <strong>TCP connections to remote cluster services fail under high concurrency</strong> ❌"),
        ("fail", "<strong>5.</strong> Cilium agent CPU spikes: <code>kubectl top pods -n kube-system -l k8s-app=cilium</code> → <strong>CPU 80%+ on agents handling cross-cluster traffic</strong> ❌"),
    ],
    [
        (1, "Check tunnel MTU for cross-cluster traffic:", "kubectl exec -n kube-system ds/cilium -- ip link show cilium_vxlan | grep mtu", "discovery", "MTU 1450 — VXLAN tunnel adds 50 bytes overhead; with cross-cluster WAN links (typically 1500 MTU), fragmentation causes latency spikes"),
        (2, "Check Hubble flow rate under load:", "hubble observe --cluster anihpj-eu --output json | jq -r '.flow.traffic_direction' | sort | uniq -c", "discovery", "High drop rate during load — the tunnel bandwidth between clusters may be saturated or the etcd sync is falling behind"),
        (3, "Verify etcd sync performance:", "etcdctl endpoint status --write-out=table", "discovery", "etcd db size growing rapidly — large number of identities and endpoints being synced; etcd compaction may be needed"),
        (4, "Check CiliumEndpointSlice count:", "kubectl get ces -A --no-headers | wc -l", "discovery", "100+ CES objects — with 50 pods per cluster, CES reduces API load but etcd sync still carries full endpoint state across clusters"),
        (5, "Root cause identified:", "Tunnel MTU mismatch, etcd sync overhead, and missing performance tuning", "root-cause", "Cross-cluster performance degrades due to: 1) MTU mismatch causing packet fragmentation on WAN links, 2) etcd sync overhead proportional to endpoint count — each new pod triggers identity and endpoint sync across the mesh, 3) No connection-level load balancing — all cross-cluster traffic may funnel through a single tunnel endpoint, and 4) Missing affinity configuration causing unnecessary cross-cluster hops"),
    ],
    r"""<span class="token comment"># Fix 1: Adjust MTU for cross-cluster WAN links</span>
cilium config set mtu 1400  <span class="token comment"># Account for VXLAN + WAN overhead</span>
cilium config set tunnel-port 8472

<span class="token comment"># Fix 2: Reduce etcd sync overhead with fewer, larger sync intervals</span>
cilium config set clustermesh-sync-interval 60s

<span class="token comment"># Fix 3: Enable service affinity to prefer local backends</span>
kubectl annotate svc -n anihpj api-service \
  io.cilium/service-affinity=local --overwrite

<span class="token comment"># Fix 4: Verify performance improvement</span>
for i in $(seq 10); do
  kubectl exec -n anihpj deploy/web -- curl -s -o /dev/null -w '%{time_total}\n' \
    http://api-service.anihpj.svc.global
done""",
    "Performance Optimized",
    "Cross-Cluster Latency Under 50ms",
    'Cross-cluster latency is <strong>under 50ms</strong> even with 50+ pods. MTU adjusted for WAN overhead eliminates fragmentation. Service affinity prefers <strong>local backends</strong> reducing cross-cluster hops. etcd sync interval increased to reduce control plane load. Hubble shows consistent FORWARDED flows with normal latency.',
    ["50 pods → latency spikes 2-5s", "Check MTU → 1450 causes fragmentation on WAN", "etcd sync overhead per endpoint", "Reduce MTU → enable affinity → increase sync interval", "Latency <50ms under load"],
    "Cluster Mesh performance tuning is critical at scale. Key optimizations: 1) <strong>MTU adjustment</strong> — VXLAN + WAN = 100 bytes overhead; set MTU to 1400 or lower, 2) <strong>Service affinity</strong> — prefer local backends to avoid cross-cluster hops when possible, 3) <strong>etcd sync interval</strong> — increase from default to reduce control plane overhead at scale, and 4) <strong>Monitor etcd DB size</strong> — compact regularly to prevent performance degradation.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> for i in $(seq 5); do kubectl exec -n anihpj deploy/web -- curl -s -o /dev/null -w "%{time_total}\n" http://api-service.anihpj.svc.global; done\n<span class="output">2.451\n5.103\n1.892\ntimeout\n3.214    ← 2-5s latency + timeout under load!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- ip link show cilium_vxlan | grep mtu\n<span class="output">vxlan id 2 local 10.0.1.1 dev eth0 srcport 0 0 dstport 8472 mtu 1450    ← Too high for WAN!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> for i in $(seq 5); do kubectl exec -n anihpj deploy/web -- curl -s -o /dev/null -w "%{time_total}\n" http://api-service.anihpj.svc.global; done\n<span class="output">0.032\n0.028\n0.045\n0.031\n0.029    ✅ All under 50ms!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj api-service -o yaml | grep service-affinity\n<span class="output">io.cilium/service-affinity: local    ✅ Local backends preferred!</span></div>',
    ]
)

# ====== Assemble ======
all_scenarios = s81 + '\n\n' + s82 + '\n\n' + s83 + '\n\n' + s84

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 3 (S81-S84) inserted!")
else:
    print("ERROR!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File size: {len(html.encode('utf-8'))} bytes")
