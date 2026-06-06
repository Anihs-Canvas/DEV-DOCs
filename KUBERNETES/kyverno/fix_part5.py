"""Update Part 5 — fix gaps and enrich content"""

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# FIX 1: 5.1 ASCII diagram — add SSL certs, iptables command, second route
# ============================================================
old_51_ascii = '''                <div class="ascii-block">User Browser: https://anihpj.io/api/jobs
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
               └────────────────────────┘</div>'''

new_51_ascii = '''                <div class="ascii-block">User Browser: https://anihpj.io/api/jobs
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
    │  SSL cert:      │          │  SSL cert:      │
    │  anihpj.io.crt  │          │  anihpj.io.crt  │
    └────────┬────────┘          └────────┬────────┘
             │                            │
             │  Nginx routes by Host header + path:
             │  anihpj.io/api/* → Service webapp-svc:8080
             │  anihpj.io/*     → Service webapp-svc:8080
             │
             ▼
    ┌────────────────────────────────────────────────────────────┐
    │  KUBE-PROXY (iptables/IPVS rules on whichever node        │
    │  the packet lands on)                                     │
    │                                                           │
    │  iptables -t nat -L KUBE-SERVICES:                        │
    │  Chain KUBE-SVC-XXXX (webapp-svc:8080):                   │
    │    ── probability 0.333 → KUBE-SEP-wk03 (10.244.3.45)     │
    │    ── probability 0.500 → KUBE-SEP-wk04 (10.244.4.72)    │
    │    ── probability 1.000 → KUBE-SEP-wk05 (10.244.5.18)    │
    │  (Random load balancing — iptables statistics module)     │
    └──────────────────────┬─────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ wk-03        │ │ wk-04        │ │ wk-05        │
    │ Pod IP:      │ │ Pod IP:      │ │ Pod IP:      │
    │ 10.244.3.45  │ │ 10.244.4.72  │ │ 10.244.5.18  │
    │              │ │              │ │              │
    │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
    │ │ webapp   │ │ │ │ webapp   │ │ │ │ webapp   │ │
    │ │ container│ │ │ │ container│ │ │ │ container│ │
    │ │ :8080    │ │ │ │ :8080    │ │ │ │ :8080    │ │
    │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
    └──────────────┘ └──────────────┘ └──────────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  POSTGRESQL DATABASE   │
              │  10.0.6.10:5432       │
              │  (external to K8s)    │
              └────────────────────────┘</div>'''

html = html.replace(old_51_ascii, new_51_ascii)
print("FIX 1: 5.1 ASCII diagram enriched with SSL certs, iptables command, second route, container boxes")

# ============================================================
# FIX 2: Add probability bullet points + scalability numbers to 5.5
# ============================================================
old_55_end = '''│  └── KUBE-POSTROUTING: SNAT to node IP if leaving cluster   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘</div>
            </div>
            <div class="info">
                <strong>💡 IPVS Mode Alternative:</strong>'''

new_55_end = '''│  └── KUBE-POSTROUTING: SNAT to node IP if leaving cluster   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘</div>
            </div>

            <div class="highlight-box">
                <strong>🧠 Why Probability Mode? The Math Behind iptables Load Balancing:</strong> iptables rules are evaluated sequentially — there is no hash table or round-robin counter. To achieve statistically even distribution across 3 endpoints, kube-proxy writes rules with carefully calculated probabilities:
                <ul style="margin-top:8px;">
                    <li><strong>Endpoint 1 (wk-03):</strong> probability 0.33333333 — 1/3 of traffic matches and gets DNAT'd to <code class="inline">10.244.3.45:8080</code></li>
                    <li><strong>Endpoint 2 (wk-04):</strong> probability 0.50000000 — of the remaining 66.7%, half (33.3%) goes to <code class="inline">10.244.4.72:8080</code></li>
                    <li><strong>Endpoint 3 (wk-05):</strong> probability 1.00000000 — all remaining traffic (33.3%) goes to <code class="inline">10.244.5.18:8080</code></li>
                </ul>
                This gives statistically even load distribution <strong>without needing a separate load balancer process</strong>. The trade-off: every packet evaluates O(n) iptables rules where n = number of endpoints.
            </div>

            <div class="warning">
                <strong>⚠️ iptables Scalability Ceiling:</strong> For 100 Services with 5 endpoints each: <strong>~6,000 iptables rules</strong>. For 5,000 Services: <strong>hundreds of thousands</strong> of rules. iptables evaluates rules sequentially (O(n)), so adding a new Service gets progressively slower. This is why iptables mode doesn't scale past <strong>~5,000 Services</strong> — IPVS mode uses a kernel hash table instead, which is O(1) vs O(n). For the anihpj cluster (well under 1,000 Services), iptables mode is perfectly fine.
            </div>

            <div class="info">
                <strong>💡 IPVS Mode Alternative:</strong>'''

html = html.replace(old_55_end, new_55_end)
print("FIX 2: 5.5 enriched with probability bullet points, scalability numbers, IPVS comparison")

# ============================================================
# FIX 3: Add "12 rules per Service" note + post-diagram context to 5.4
# ============================================================
old_54_end = '''            <div class="warning">
                <strong>⚠️ iptables Scalability Limit:</strong> Each Service with 3 endpoints creates ~12 iptables rules. A cluster with 5,000 Services × 5 endpoints each = <strong>hundreds of thousands</strong> of iptables rules. iptables evaluates rules sequentially (O(n)), so adding a new Service gets slower as the rule count grows. This is why <strong>IPVS mode</strong> exists — it uses a hash table (O(1)) instead of sequential rules. For the anihpj cluster (well under 1,000 Services), iptables mode is perfectly fine.
            </div>
        </div>'''

new_54_end = '''            <div class="info">
                <strong>📊 iptables Rule Count Per Service:</strong> For this one Service with 3 endpoints, kube-proxy creates approximately <strong>12 iptables rules</strong>: 1 rule in KUBE-SERVICES (the match), 3 probability rules in KUBE-SVC-WXYZ (the selection), 3 DNAT rules in KUBE-SEP chains (the rewrite), plus connection tracking and forwarding rules. Multiply by the number of Services in your cluster — this is why iptables rule count grows linearly with Service count.
            </div>

            <div class="warning">
                <strong>⚠️ iptables Scalability Limit:</strong> Each Service with 3 endpoints creates ~12 iptables rules. A cluster with <strong>100 Services × 5 endpoints = ~6,000 rules</strong>. At <strong>5,000 Services</strong>, you have hundreds of thousands of rules. iptables evaluates rules sequentially (O(n)), so packet processing time grows with every new Service. This is why <strong>IPVS mode</strong> exists — it uses a kernel hash table (O(1)) instead of sequential rules, and supports multiple scheduling algorithms (round-robin, least-connection, source-hash, destination-hash). For the anihpj cluster (well under 1,000 Services), iptables mode is perfectly fine.
            </div>
        </div>'''

html = html.replace(old_54_end, new_54_end)
print("FIX 3: 5.4 enriched with rule count info box + exact scalability numbers")

# ============================================================
# FIX 4: Add more thorough explanation to 5.2 (6-step enumeration)
# ============================================================
old_52_end = '''            <div class="info">
                <strong>⚡ Why Calico is fast:</strong> Calico programs routes directly into the Linux kernel's routing table using <code class="inline">ip route</code>. There's no overlay network (VXLAN, IP-in-IP) unless your network requires it. Same-node Pod-to-Pod traffic has latency in the <strong>microsecond</strong> range because it's just a kernel routing decision between two veth interfaces. No packets leave the node.
            </div>
        </div>'''

new_52_end = '''            <div class="highlight-box">
                <strong>🔍 Step-by-Step — What Actually Happens at the Kernel Level:</strong>
                <ol style="margin-top:8px;">
                    <li><strong>Pod A</strong> (10.244.4.72) sends a TCP SYN packet to 10.244.4.73:8080</li>
                    <li>The packet exits Pod A's network namespace through its <strong>veth</strong> (virtual ethernet) interface and enters the <strong>node's root network namespace</strong></li>
                    <li>The Linux kernel looks up <code class="inline">10.244.4.73</code> in the routing table — Calico has programmed: <code class="inline">10.244.4.73 dev cali1234567890 scope link</code> → "Send directly to Pod B's veth"</li>
                    <li>The packet passes through Calico's <strong>iptables FORWARD chain</strong> (<code class="inline">cali-FORWARD</code>) where NetworkPolicy rules are enforced — if a NetworkPolicy denies this traffic, the packet is dropped here</li>
                    <li>The packet crosses into <strong>Pod B's network namespace</strong> through its veth interface</li>
                    <li>Pod B's Linux kernel delivers the packet to the <strong>container process</strong> listening on :8080</li>
                </ol>
                Total latency: <strong>~0.05 milliseconds</strong>. No overlay encapsulation. No tunnel. No packets leaving the node.
            </div>

            <div class="info">
                <strong>⚡ Why Calico is fast:</strong> Calico programs routes directly into the Linux kernel's routing table using <code class="inline">ip route</code>. There's no overlay network (VXLAN, IP-in-IP) unless your network requires it. Same-node Pod-to-Pod traffic has latency in the <strong>microsecond</strong> range because it's just a kernel routing decision between two veth interfaces. No packets leave the node.
            </div>
        </div>'''

html = html.replace(old_52_end, new_52_end)
print("FIX 4: 5.2 enriched with 6-step kernel-level walkthrough")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nFinal: {html.count(chr(10))} lines')
