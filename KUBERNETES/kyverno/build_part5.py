"""Build Part 5 — Network Flow"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 5: NETWORK FLOW -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-5">
        <h2>🌐 <span class="section-num">Part 5</span> — Network Flow: How a Request Reaches a Pod</h2>
        <div class="section-intro">
            <p>Kubernetes networking has a reputation for being complex — but when broken down step by step, it's actually a series of simple transformations. This section traces a request from an external user's browser all the way to a Pod container, explaining every hop, every IP translation, and every iptables rule along the way.</p>
            <p>We cover the <strong>three distinct networks</strong> that coexist in every cluster: the <strong>Node Network</strong> (physical IPs), the <strong>Pod Network</strong> (10.244.0.0/16, real routable IPs), and the <strong>Service Network</strong> (10.96.0.0/12, virtual — exists only as iptables rules).</p>
        </div>

        <!-- 5.1 EXTERNAL REQUEST FLOW -->
        <h3 id="part-5-1">5.1 External Request Flow — User → Pod</h3>
        <div class="api-block">
            <p>Trace a request from <code class="inline">https://anihpj.io/api/jobs</code> through every hop to the webapp container:</p>
            <div class="diagram-box">
                <div class="diagram-title">🌐 Complete Request Flow — Browser to Container</div>
                <div class="ascii-block">User Browser: https://anihpj.io/api/jobs
    │
    ▼
[DNS Resolution: anihpj.io → 203.0.113.10 (Cloud LB public IP)]
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLOUD LOAD BALANCER (HAProxy / AWS NLB / Azure LB)            │
│  Public IP: 203.0.113.10 → Backend: fe-01:443, fe-02:443       │
│  Health check: GET /healthz on each frontend every 5s           │
└────────────┬────────────────────────────┬───────────────────────┘
             │                            │
    ┌────────▼────────┐          ┌────────▼────────┐
    │  fe-01:443      │          │  fe-02:443      │
    │  NGINX INGRESS  │          │  NGINX INGRESS  │
    │  TLS termination│          │  TLS termination│
    └────────┬────────┘          └────────┬────────┘
             │                            │
             │  Nginx routes by Host + path:
             │  anihpj.io/api/* → Service webapp-svc:8080
             │
             ▼
    ┌────────────────────────────────────────────────────────────┐
    │  KUBE-PROXY iptables (on whichever node receives packet)   │
    │  Chain KUBE-SVC-XXXX (webapp-svc:8080):                   │
    │    → 33.3% KUBE-SEP-wk03 (DNAT to 10.244.3.45:8080)       │
    │    → 50.0% KUBE-SEP-wk04 (DNAT to 10.244.4.72:8080)      │
    │    → 100%  KUBE-SEP-wk05 (DNAT to 10.244.5.18:8080)      │
    └──────────────────────┬─────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ wk-03 Pod    │ │ wk-04 Pod    │ │ wk-05 Pod    │
    │ 10.244.3.45  │ │ 10.244.4.72  │ │ 10.244.5.18  │
    │ webapp :8080 │ │ webapp :8080 │ │ webapp :8080 │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
               ┌────────────────────────┐
               │  POSTGRESQL DATABASE   │
               │  10.0.6.10:5432       │
               │  (external to K8s)    │
               └────────────────────────┘</div>
            </div>
            <table style="margin-top:14px;">
                <tr><th style="width:60px;">Hop</th><th>Component</th><th>What Happens</th><th>IP Translation</th></tr>
                <tr><td>1</td><td>DNS</td><td>anihpj.io resolves to cloud LB public IP</td><td>—</td></tr>
                <tr><td>2</td><td>Cloud LB</td><td>Terminates TCP, forwards to fe-01 or fe-02 on port 443</td><td>203.0.113.10 → 10.0.5.10:443</td></tr>
                <tr><td>3</td><td>Nginx (fe-01)</td><td>TLS termination, routes by Host header to Service ClusterIP</td><td>TLS decrypt, forward to 10.96.50.100:8080</td></tr>
                <tr><td>4</td><td>kube-proxy</td><td>iptables DNAT: ClusterIP → random Pod IP</td><td>10.96.50.100:8080 → 10.244.4.72:8080</td></tr>
                <tr><td>5</td><td>Calico/CNI</td><td>Routes Pod IP across the cluster network to the correct node</td><td>Packet forwarded to wk-04</td></tr>
                <tr><td>6</td><td>Containerd</td><td>Delivers packet to the webapp container's network namespace</td><td>—</td></tr>
            </table>
        </div>

        <!-- 5.2 POD-TO-POD SAME NODE -->
        <h3 id="part-5-2">5.2 Pod-to-Pod — Same Node</h3>
        <div class="api-block">
            <p>When two Pods on <strong>the same node</strong> communicate, the traffic never leaves the node. Calico routes it directly between veth pairs:</p>
            <div class="diagram-box">
                <div class="diagram-title">🏠 Same-Node Pod Communication (wk-04)</div>
                <div class="ascii-block">  Pod A (10.244.4.72)                          Pod B (10.244.4.73)
  ┌─────────────────────┐                    ┌─────────────────────┐
  │ webapp container    │                    │ worker container    │
  │ eth0: 10.244.4.72   │                    │ eth0: 10.244.4.73   │
  └──────────┬──────────┘                    └──────────┬──────────┘
             │ veth                                    │ veth
             ▼                                         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │              HOST NETWORK NAMESPACE (wk-04)                  │
  │                                                              │
  │  caliXXXX (host-side veth for Pod A)                         │
  │  caliYYYY (host-side veth for Pod B)                         │
  │                                                              │
  │  Calico route table on wk-04:                                │
  │    10.244.4.72 dev caliXXXX scope link                       │
  │    10.244.4.73 dev caliYYYY scope link                       │
  │                                                              │
  │  Calico iptables rules:                                      │
  │    FORWARD chain → cali-FORWARD → apply NetworkPolicy        │
  └──────────────────────────────────────────────────────────────┘

  No overlay. No tunnel. Pure Linux routing. ~0.05ms latency.</div>
            </div>
            <div class="info">
                <strong>⚡ Why Calico is fast:</strong> Calico programs routes directly into the Linux kernel's routing table using <code class="inline">ip route</code>. There's no overlay network (VXLAN, IP-in-IP) unless your network requires it. Same-node Pod-to-Pod traffic has latency in the <strong>microsecond</strong> range because it's just a kernel routing decision between two veth interfaces. No packets leave the node.
            </div>
        </div>

        <!-- 5.3 POD-TO-POD CROSS-NODE -->
        <h3 id="part-5-3">5.3 Pod-to-Pod — Cross-Node (BGP Routing)</h3>
        <div class="api-block">
            <p>When Pods on <strong>different nodes</strong> communicate, Calico uses BGP to tell every node how to reach every Pod:</p>
            <div class="diagram-box">
                <div class="diagram-title">🌍 Cross-Node Pod Communication (wk-04 → wk-03)</div>
                <div class="ascii-block">  Pod A (wk-04, 10.244.4.72) → Pod B (wk-03, 10.244.3.45)

  Step 1: Pod A sends packet to 10.244.3.45
  Step 2: Pod A's veth → wk-04 root network namespace
  Step 3: Calico route on wk-04:
           10.244.3.0/26 via 10.0.4.23 dev eth0
           → "wk-03's Pod CIDR is reachable via wk-03's node IP"
           (This route was learned via BGP from wk-03's Calico)
  Step 4: Packet goes out eth0 on wk-04 → physical network
  Step 5: Switch/router delivers to 10.0.4.23 (wk-03)
  Step 6: Calico route on wk-03:
           10.244.3.45 dev cali9876543210 scope link
           → "This specific Pod IP is on this veth"
  Step 7: Packet arrives at Pod B's veth → Pod B receives it

  ┌─────────────┐     BGP Route      ┌─────────────┐
  │    wk-04    │◄──────────────────►│    wk-03    │
  │ Bird (BGP)  │  "I have routes    │ Bird (BGP)  │
  │             │   for 10.244.4.0   │             │
  │             │   /26 via 10.0.    │             │
  │             │   4.24"            │             │
  └─────────────┘                    └─────────────┘

  Optional: IP-in-IP or VXLAN encapsulation for networks without BGP support.
  Adds ~20 bytes overhead per packet, ~0.1ms extra latency.</div>
            </div>
            <div class="highlight-box">
                <strong>🧠 BGP — Why Calico uses a routing protocol:</strong> In a traditional datacenter, routers use BGP to exchange routes. Calico runs a lightweight BGP daemon (called <strong>bird</strong>) on every node to advertise "I can reach Pod IPs X, Y, Z at this node's IP." This means every node knows exactly how to reach every Pod — no central controller, no overlay network, just pure IP routing. If your physical network already runs BGP (e.g., with ToR switches), Calico can peer with your routers for seamless Pod-to-external routing.
            </div>
        </div>

        <!-- 5.4 SERVICE TO POD (iptables DNAT) -->
        <h3 id="part-5-4">5.4 Service to Pod — iptables DNAT Deep Dive</h3>
        <div class="api-block">
            <p>This is the magic of Kubernetes Services. A <strong>ClusterIP is not a real IP</strong> — it's a virtual address that exists only as iptables rules. Here's exactly what happens:</p>

            <p style="margin-bottom:10px;"><strong>Service:</strong> <code class="inline">webapp-svc</code> — ClusterIP <code class="inline">10.96.50.100:8080</code></p>
            <p style="margin-bottom:10px;"><strong>Endpoints:</strong> <code class="inline">10.244.3.45:8080</code> (wk-03), <code class="inline">10.244.4.72:8080</code> (wk-04), <code class="inline">10.244.5.18:8080</code> (wk-05)</p>

            <h4>Step-by-Step iptables Processing</h4>
            <table>
                <tr><th style="width:80px;">Step</th><th>Chain</th><th>What Happens</th></tr>
                <tr><td>1</td><td><code class="inline">PREROUTING</code></td><td>Packet with dst=10.96.50.100:8080 enters netfilter</td></tr>
                <tr><td>2</td><td><code class="inline">KUBE-SERVICES</code></td><td>Matches dst=10.96.50.100, dport=8080 → JUMP to KUBE-SVC-WXYZ</td></tr>
                <tr><td>3</td><td><code class="inline">KUBE-SVC-WXYZ</code></td><td>Random selection: Rule 1 (33.3% → wk-03), Rule 2 (50% → wk-04), Rule 3 (100% → wk-05)</td></tr>
                <tr><td>4</td><td><code class="inline">KUBE-SEP-XXXX</code></td><td>DNAT: rewrites destination to the selected Pod IP:Port</td></tr>
                <tr><td>5</td><td>(routing)</td><td>Kernel routes the rewritten packet to the Pod's node</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 The Probability Math:</strong> iptables rules are evaluated sequentially. With 3 endpoints: <strong>Rule 1</strong> matches with probability 0.333 (1/3 of traffic goes to wk-03). <strong>Rule 2</strong> has probability 0.500, but only 66.7% of traffic reaches it — so 0.500 × 66.7% = 33.3% goes to wk-04. <strong>Rule 3</strong> catches the remaining 33.3% for wk-05. The result: statistically even distribution. The cost: every packet evaluates O(n) rules where n = number of endpoints.
            </div>

            <div class="warning">
                <strong>⚠️ iptables Scalability Limit:</strong> Each Service with 3 endpoints creates ~12 iptables rules. A cluster with 5,000 Services × 5 endpoints each = <strong>hundreds of thousands</strong> of iptables rules. iptables evaluates rules sequentially (O(n)), so adding a new Service gets slower as the rule count grows. This is why <strong>IPVS mode</strong> exists — it uses a hash table (O(1)) instead of sequential rules. For the anihpj cluster (well under 1,000 Services), iptables mode is perfectly fine.
            </div>
        </div>

        <!-- 5.5 KUBE-PROXY IPTABLES CHAIN -->
        <h3 id="part-5-5">5.5 kube-proxy iptables Chain — Visual Walkthrough</h3>
        <div class="api-block">
            <p>The full netfilter hook pipeline that a packet traverses when destined for a ClusterIP:</p>
            <div class="diagram-box">
                <div class="diagram-title">🔗 Netfilter Hooks — Full iptables Pipeline</div>
                <div class="ascii-block">┌─────────────────────────────────────────────────────────────────────┐
│                         NETFILTER HOOKS                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ PREROUTING (raw) — connection tracking                       │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ PREROUTING (nat) — DNAT happens here                         │   │
│  │   ├── KUBE-SERVICES → KUBE-SVC-WXYZ → KUBE-SEP-XXXX          │   │
│  │   │   Rule 1: 33.3% → DNAT to 10.244.3.45:8080               │   │
│  │   │   Rule 2: 50.0% → DNAT to 10.244.4.72:8080               │   │
│  │   │   Rule 3: 100%  → DNAT to 10.244.5.18:8080              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ FORWARD — between interfaces                                 │   │
│  │   ├── cali-FORWARD: Calico NetworkPolicy enforcement          │   │
│  │   └── KUBE-FORWARD: ACCEPT if conntrack state valid           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ POSTROUTING (nat) — SNAT/MASQUERADE for external traffic     │   │
│  │   └── KUBE-POSTROUTING: SNAT to node IP if leaving cluster   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘</div>
            </div>
            <div class="info">
                <strong>💡 IPVS Mode Alternative:</strong> If you switch kube-proxy to <code class="inline">mode: "ipvs"</code> in the kubeadm config, the iptables rules are replaced with a kernel-level IP Virtual Server. IPVS uses a hash table for Service lookup (O(1) vs O(n)) and supports multiple scheduling algorithms (round-robin, least-connection, source-hash). For clusters with thousands of Services, IPVS is the preferred mode.
            </div>
        </div>

        <!-- 5.6 CNI PLUGIN CHAIN -->
        <h3 id="part-5-6">5.6 CNI Plugin Execution Chain — When a Pod is Created</h3>
        <div class="api-block">
            <p>When kubelet asks containerd to create a Pod, the CNI plugin chain executes in order — Calico → Portmap → Bandwidth:</p>
            <div class="diagram-box">
                <div class="diagram-title">🔌 CNI Plugin Chain — Pod webapp-7d8f on wk-04</div>
                <div class="ascii-block">  kubelet: "Create Pod webapp-7d8f on wk-04"
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  CONTAINERD (CRI Runtime)                                       │
  │  1. Pull image: registry.anihpj.io/webapp:v1.2.3                │
  │  2. Create PodSandbox (pause container)                         │
  │  3. Call CNI: "I need network for Pod webapp-7d8f"              │
  └────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  CNI PLUGIN CHAIN (executed in order from .conflist)            │
  │                                                                 │
  │  STEP 1: CALICO — Allocate IP 10.244.4.72, create veth pair,   │
  │           add routes, program NetworkPolicy iptables, advertise │
  │           /32 via BGP                                           │
  │                         │                                       │
  │  STEP 2: PORTMAP — If hostPort is defined, add DNAT rule       │
  │           (hostPort → podIP); otherwise no-op                   │
  │                         │                                       │
  │  STEP 3: BANDWIDTH — If Pod has bandwidth annotations, create  │
  │           tc qdisc on veth; otherwise no-op                     │
  │                                                                 │
  │  Result: Pod IP = 10.244.4.72, reachable cluster-wide          │
  └─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  kubelet receives Pod IP → updates Pod.status.podIP             │
  │  Pod is now reachable at 10.244.4.72 from any node in cluster   │
  └─────────────────────────────────────────────────────────────────┘</div>
            </div>
            <table>
                <tr><th style="width:100px;">Plugin</th><th>Order</th><th>What It Does</th><th>When It's Used</th></tr>
                <tr><td><strong>calico</strong></td><td>1st</td><td>Allocates Pod IP from node's /26 CIDR, creates veth pair, programs routes, enforces NetworkPolicy via iptables, advertises /32 via BGP</td><td>Every Pod creation — always active</td></tr>
                <tr><td><strong>portmap</strong></td><td>2nd</td><td>Creates iptables DNAT rule mapping hostPort to Pod IP if the Pod spec includes <code class="inline">hostPort</code></td><td>Only when Pod uses hostPort (rare in production)</td></tr>
                <tr><td><strong>bandwidth</strong></td><td>3rd</td><td>Creates Linux tc (traffic control) qdisc on the Pod's veth to enforce ingress/egress bandwidth limits from Pod annotations</td><td>Only when Pod has bandwidth annotations set</td></tr>
            </table>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-5">
        <h2>🌐 <span class="section-num">Part 5</span> — Network Flow: How a Request Reaches a Pod</h2>
        <div class="section-intro"><p>End-to-end: external request → LB → Nginx → kube-proxy iptables → Pod. Includes Pod routing, Service DNAT, and CNI plugin chains.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 5: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, ASCII: {content.count("ascii-block")}, Diagrams: {content.count("diagram-box")}')
