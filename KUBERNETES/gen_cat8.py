#!/usr/bin/env python3
"""Generate Category 8: BGP & External Networking — All 6 scenarios (S95-S100)"""
with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

EM = '\u2014'  # em dash

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_short, verify_detail, tenet_steps, tenet_text, before_outputs, after_outputs):
    ei = ''.join(f'<div class="lookat-item"><span class="li-check {"pass" if t=="pass" else "fail"}">{"✓" if t=="pass" else "✗"}</span><span>{txt}</span></div>\n' for t,txt in error_items)
    di = ''.join(f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n' for num,label,cmd,ftype,ftext in debug_items)
    tf = ''.join(f'<div class="tenet-step"><div class="step-num">{chr(0x2460+i)}</div><div class="step-label">{lbl}</div></div>\n' for i,lbl in enumerate(tenet_steps))
    bo = '\n'.join(before_outputs)
    ao = '\n'.join(after_outputs)
    return f'''    <!-- ═══════════════ S{n}: {title} ═══════════════ -->
    <div class="scenario-block" id="sc-s{n}">
        <div class="sc-header"><div class="sc-badge">S{n}</div><div class="sc-header-content"><div class="sc-num">🧪 SCENARIO S{n} — Category 8: BGP &amp; External Networking</div><h4>{title}</h4><div class="sc-desc"><strong>The Problem:</strong> {desc}</div></div></div>
        <div class="sc-body">
            <div class="sc-step"><div class="sc-step-num deploy">1</div><div class="sc-step-content"><h4 class="deploy">📋 Deploy the YAML (contains the bug)</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-code')">📋 Copy</button></div><pre><code id="sc-s{n}-code" class="language-bash">{deploy_code}</code></pre></div></div></div>
            <div class="sc-step error-spot"><div class="sc-step-num">⚠</div><div class="sc-step-content"><h4>⚠️ Observe the Error — Spot What's Broken</h4>{ei}</div></div>
            <div class="sc-step debug-find"><div class="sc-step-num">🔍</div><div class="sc-step-content"><h4>🔍 Debug — Find the Root Cause</h4>{di}</div></div>
            <div class="sc-step"><div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div><div class="sc-step-content"><h4 style="color: #3fb950;">🔧 Fix {EM} {fix_desc}</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH {EM} {fix_desc.lower()[:60]}</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-fix')">📋 Copy</button></div><pre><code id="sc-s{n}-fix" class="language-bash">{fix_code}</code></pre></div></div></div>
            <div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution"><h4>✅ Verify {EM} {verify_short}</h4><p>{verify_detail}</p></div></div></div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{n}')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa{n}"><h5>🧠 Diagnostic Tenet (Thought Process)</h5><div class="tenet-flow">{tf}</div><p><strong>Tenet:</strong> {tenet_text}</p><h5>📟 Command Outputs — Error State (BEFORE fix)</h5>{bo}<h5>📟 Command Outputs — AFTER Fix</h5>{ao}</div>
            <div class="sc-step"><div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div><div class="sc-step-content"><h4 style="color: #8b949e;">🧹 Cleanup — Delete All Resources</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH — copy &amp; paste to clean up</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-cleanup')">📋 Copy</button></div><pre><code id="sc-s{n}-cleanup" class="language-bash"><span class="token comment"># Delete the namespace</span>
kubectl delete namespace anihpj
<span class="token comment"># Verify cleanup</span>
kubectl get all -n anihpj</code></pre></div></div></div>
        </div>
    </div>
'''

# ======================== S95 ========================
s95 = sc(95,
    "Configure BGP Peering for anihpj LoadBalancer on Bare Metal",
    'You have a bare metal Kubernetes cluster and need to expose anihpj via BGP. Cilium BGP is configured but <strong>peering sessions never establish</strong>. anihpj LoadBalancer services get external IPs but they are <strong>unreachable from outside</strong>. Your job: configure BGP peering correctly and make anihpj accessible via BGP-advertised IPs.',
    r"""<span class="token comment"># Deploy anihpj LoadBalancer service</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer

<span class="token comment"># Configure Cilium BGP — ❌ BUG: BGP session never established</span>
cat > bgp-config.yaml << 'EOF'
apiVersion: "cilium.io/v2alpha1"
kind: CiliumBGPPeeringPolicy
metadata:
  name: anihpj-bgp
spec:
  virtualRouters:
  - localASN: 65001
    exportPodCIDR: true
    neighbors:
    - peerAddress: "10.0.0.1/32"
      peerASN: 65000
EOF
kubectl apply -f bgp-config.yaml

<span class="token comment"># Check BGP peers — ❌ No session</span>
cilium-dbg bgp peers
<span class="token comment"># (empty output — no peers)</span>""",
    [
        ("pass", '<strong>1.</strong> BGP policy applied: <code>kubectl get ciliumbgppeeringpolicy</code> → anihpj-bgp exists ✅'),
        ("pass", '<strong>2.</strong> LoadBalancer service created: <code>kubectl get svc -n anihpj</code> → web LoadBalancer with external IP ✅'),
        ("fail", '<strong>3.</strong> BGP peers empty: <code>cilium-dbg bgp peers</code> → <strong>no peers listed — session not established!</strong> ❌'),
        ("fail", '<strong>4.</strong> External IP unreachable: <code>curl http://<LB-IP></code> from outside → <strong>connection timeout</strong> ❌'),
        ("fail", '<strong>5.</strong> Check node BGP speaker: <code>kubectl logs -n kube-system ds/cilium | grep -i bgp</code> → <strong>"BGP speaker not started: no matching nodes"</strong> ❌'),
    ],
    [
        (1, "Check if BGP Control Plane is enabled:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -i bgp", "discovery", "enable-bgp-control-plane: false — BGP speaker is NOT enabled in Cilium ConfigMap; the CRD exists but the control plane never starts"),
        (2, "Check nodeSelector for BGP:", "kubectl get ciliumbgppeeringpolicy anihpj-bgp -o yaml | grep -A5 nodeSelector", "discovery", "nodeSelector is missing — BGP speaker needs to know which nodes to run on; without it, no nodes are selected"),
        (3, "Check BGP port accessibility:", "kubectl exec -n kube-system ds/cilium -- netstat -tlnp | grep 179", "discovery", "TCP port 179 (BGP) not listening — the BGP speaker process never started because enable-bgp-control-plane is false"),
        (4, "Check if IP pool is configured for LB:", "kubectl get ciliumloadbalancerippool -o yaml", "discovery", "No CiliumLoadBalancerIPPool — BGP can advertise routes but there's no IP pool to allocate from; LB services get ClusterIP but no routable external IP"),
        (5, "Root cause identified:", "BGP Control Plane not enabled and no IP pool configured", "root-cause", "Cilium BGP requires: 1) enable-bgp-control-plane=true in ConfigMap, 2) CiliumBGPPeeringPolicy with correct ASN and peer, 3) CiliumLoadBalancerIPPool defining which IPs to allocate, and 4) nodeSelector (or all nodes). Missing any of these = no BGP peering and unreachable LB services"),
    ],
    r"""<span class="token comment"># Fix 1: Enable BGP Control Plane</span>
kubectl patch configmap -n kube-system cilium-config --type merge -p '{"data":{"enable-bgp-control-plane":"true"}}'

<span class="token comment"># Fix 2: Create LB IP Pool for anihpj</span>
cat > lb-ip-pool.yaml << 'EOF'
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: anihpj-pool
spec:
  blocks:
  - cidr: "192.168.100.0/24"
EOF
kubectl apply -f lb-ip-pool.yaml

<span class="token comment"># Fix 3: Update BGP policy with nodeSelector</span>
kubectl patch ciliumbgppeeringpolicy anihpj-bgp --type merge -p '{"spec":{"nodeSelector":{"matchLabels":{"kubernetes.io/os":"linux"}}}}'

<span class="token comment"># Fix 4: Restart Cilium agents</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system --timeout=300s""",
    "BGP Peering Established",
    "BGP Session Active and anihpj Reachable via Advertised IP",
    'After enabling BGP Control Plane and creating the IP pool, <code>cilium-dbg bgp peers</code> shows an <strong>ESTABLISHED</strong> BGP session with the upstream router (ASN 65000). The anihpj LoadBalancer service gets an external IP from the 192.168.100.0/24 pool. External clients can <code>curl http://192.168.100.x</code> and reach anihpj.',
    ["BGP policy created → no peers", "enable-bgp-control-plane: false", "No LB IP pool → no external IP", "Enable BGP + create IP pool", "Peering established → anihpj reachable"],
    "Cilium BGP on bare metal requires four components: <strong>1) BGP Control Plane enabled</strong> (runs a GoBGP speaker per node), <strong>2) CiliumBGPPeeringPolicy</strong> (defines ASN, peers, nodeSelector), <strong>3) CiliumLoadBalancerIPPool</strong> (defines IP ranges for LB services), and <strong>4) LB IPAM enabled</strong> (auto-allocates from pool). The BGP speaker advertises the LB IP via BGP to upstream routers. Without all four, BGP sessions never form.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bgp peers\n<span class="output">(empty — no BGP peers)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cm -n kube-system cilium-config -o yaml | grep bgp\n<span class="output">enable-bgp-control-plane: "false"    ← Not enabled!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web\n<span class="output">NAME   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)\nweb    LoadBalancer   10.96.100.50   <pending>     80/TCP    ← No external IP!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bgp peers\n<span class="output">PEER         ASN     STATE         UPTIME\n10.0.0.1     65000   ESTABLISHED   2m    ✅ BGP session up!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web\n<span class="output">NAME   TYPE           CLUSTER-IP     EXTERNAL-IP        PORT(S)\nweb    LoadBalancer   10.96.100.50   192.168.100.5      80/TCP    ✅ External IP allocated!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://192.168.100.5\n<span class="output">&lt;html&gt;...nginx welcome...&lt;/html&gt;    ✅ anihpj reachable via BGP!</span></div>',
    ]
)

# ======================== S96 ========================
s96 = sc(96,
    "Debug BGP Session Stuck in Connect/Active State",
    'BGP is configured but the session is <strong>stuck in Connect or Active state</strong>, never reaching Established. anihpj LoadBalancer IPs are allocated but <strong>not advertised</strong> because BGP is not up. Your job: debug why the BGP session won\'t establish and fix it.',
    r"""<span class="token comment"># BGP configured but stuck</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer

<span class="token comment"># ❌ BUG: BGP session stuck in Connect/Active</span>
cilium-dbg bgp peers
<span class="token comment"># PEER         ASN     STATE     UPTIME
# 10.0.0.1     65000   Connect   0s</span>

<span class="token comment"># Check for 30 seconds — still Connect</span>
sleep 30
cilium-dbg bgp peers
<span class="token comment"># PEER         ASN     STATE     UPTIME
# 10.0.0.1     65000   Active    0s    ← Oscillating, never Established!</span>""",
    [
        ("pass", '<strong>1.</strong> BGP configured: <code>kubectl get ciliumbgppeeringpolicy</code> → exists ✅'),
        ("pass", '<strong>2.</strong> BGP speaker running: <code>kubectl logs -n kube-system ds/cilium | grep "BGP"</code> → speaker started ✅'),
        ("fail", '<strong>3.</strong> Session stuck in Connect/Active: <code>cilium-dbg bgp peers</code> → <strong>Connect→Active→Connect oscillation</strong> ❌'),
        ("fail", '<strong>4.</strong> LB IP allocated but not advertised: <code>kubectl get svc -n anihpj</code> → <strong>external IP exists but unreachable</strong> ❌'),
        ("fail", '<strong>5.</strong> Check BGP connectivity: <code>telnet 10.0.0.1 179</code> from node → <strong>connection refused — TCP/179 blocked!</strong> ❌'),
    ],
    [
        (1, "Check BGP session state details:", "cilium-dbg bgp peers", "discovery", "State oscillates between Connect and Active — Connect means TCP SYN sent but no reply; Active means retrying. This indicates a network/firewall issue between the node and the BGP peer"),
        (2, "Check if BGP port 179 is open on peer:", "nc -zv 10.0.0.1 179", "discovery", "Connection refused — the upstream router (10.0.0.1) is not listening on TCP/179, or a firewall between the node and router is blocking the port"),
        (3, "Check node firewall rules:", "sudo iptables -L INPUT -n | grep 179", "discovery", "DROP rule for tcp dpt:179 — the node's own iptables is blocking incoming BGP connections from the peer"),
        (4, "Check if peer expects a specific source IP:", 'kubectl logs -n kube-system ds/cilium | grep -i "bgp.*connect\|bgp.*reject"', "discovery", "Peer rejected connection from <node-ip> — the upstream router expects BGP connections from a specific IP that doesn't match the node's IP"),
        (5, "Root cause identified:", "TCP/179 blocked by firewall or mismatched peer expectations", "root-cause", "BGP uses TCP port 179. A Connect→Active oscillation means: 1) firewall/iptables blocking TCP/179 (either on the node or between node and peer), 2) the peer router expects a specific source IP (multihop), or 3) the peer's BGP ASN is wrong. In Connect state, the local speaker sent TCP SYN; in Active, it's waiting for the peer to initiate"),
    ],
    r"""<span class="token comment"># Fix 1: Allow BGP port 179 on the node</span>
sudo iptables -I INPUT -p tcp --dport 179 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4

<span class="token comment"># Fix 2: If multihop BGP required (peer not directly connected)</span>
kubectl patch ciliumbgppeeringpolicy anihpj-bgp --type merge -p '{"spec":{"virtualRouters":[{"localASN":65001,"neighbors":[{"peerAddress":"10.0.0.1/32","peerASN":65000,"ebgpMultihop":5}]}]}}'

<span class="token comment"># Fix 3: Set specific source address for BGP</span>
kubectl patch ciliumbgppeeringpolicy anihpj-bgp --type merge -p '{"spec":{"virtualRouters":[{"localASN":65001,"exportPodCIDR":true,"neighbors":[{"peerAddress":"10.0.0.1/32","peerASN":65000,"sourceAddress":"192.168.1.10"}]}]}}'

<span class="token comment"># Fix 4: Verify session establishes</span>
cilium-dbg bgp peers --watch""",
    "BGP Session Established",
    "BGP Session Transitioned from Connect to Established",
    'After opening TCP/179 and configuring multihop, the BGP session transitions from <strong>Connect→Active→OpenSent→OpenConfirm→Established</strong>. <code>cilium-dbg bgp peers</code> shows ESTABLISHED with uptime. The anihpj LB IP is advertised via BGP and reachable from external networks.',
    ["BGP stuck Connect/Active → never Established", "TCP/179 blocked by iptables", "Peer expects specific source IP", "Open port 179 + configure multihop", "Session Established → LB IP advertised"],
    "BGP state machine: <strong>Idle→Connect→Active→OpenSent→OpenConfirm→Established</strong>. Stuck in Connect means TCP SYN sent but no SYN-ACK (firewall or peer down). Stuck in Active means the speaker is waiting for the peer to connect (asymmetric firewall, wrong peer IP, or the peer is also stuck Active). Always check <code>iptables -L INPUT | grep 179</code> on the node and verify the peer router's BGP configuration matches ASN and expected source IP.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bgp peers\n<span class="output">PEER         ASN     STATE     UPTIME\n10.0.0.1     65000   Connect   0s    ← TCP SYN sent, no reply</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> sudo iptables -L INPUT -n | grep 179\n<span class="output">DROP   tcp  --  0.0.0.0/0  0.0.0.0/0  tcp dpt:179    ← Blocked!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bgp peers\n<span class="output">PEER         ASN     STATE         UPTIME\n10.0.0.1     65000   ESTABLISHED   5m    ✅ BGP up!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bgp routes advertised 10.0.0.1\n<span class="output">PREFIX            NEXT-HOP       COMMUNITY\n192.168.100.5/32  192.168.1.10   —    ✅ anihpj LB IP advertised!</span></div>',
    ]
)

# ======================== S97 ========================
s97 = sc(97,
    "Fix LB IPAM Not Assigning IP to anihpj LoadBalancer Service",
    'Cilium BGP is working but <strong>anihpj LoadBalancer services get no external IP</strong>. The service stays in <code>&lt;pending&gt;</code> state forever. Your job: fix LB IPAM so anihpj services get external IPs from the configured pool.',
    r"""<span class="token comment"># BGP working, but LB services stuck Pending</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer

<span class="token comment"># ❌ BUG: External IP stuck Pending</span>
kubectl get svc -n anihpj web
<span class="token comment"># NAME   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)
# web    LoadBalancer   10.96.100.50   <pending>     80/TCP    ← Never assigned!</span>

kubectl describe svc -n anihpj web | tail -5
<span class="token comment"># Events:
#   Type     Reason     Message
#   Warning  AllocationFailed  No IP pool available for service</span>""",
    [
        ("pass", '<strong>1.</strong> BGP configured and working: <code>cilium-dbg bgp peers</code> → ESTABLISHED ✅'),
        ("pass", '<strong>2.</strong> LB service created: <code>kubectl get svc -n anihpj</code> → LoadBalancer type ✅'),
        ("fail", '<strong>3.</strong> External IP stuck: <code>kubectl get svc -n anihpj web</code> → <strong>EXTERNAL-IP: &lt;pending&gt;</strong> ❌'),
        ("fail", '<strong>4.</strong> Service events: <code>kubectl describe svc -n anihpj web</code> → <strong>"No IP pool available"</strong> ❌'),
        ("fail", '<strong>5.</strong> Check IP pool: <code>kubectl get ciliumloadbalancerippool</code> → <strong>No resources found — pool not created!</strong> ❌'),
    ],
    [
        (1, "Check if LB IPAM is enabled:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -i lb", "discovery", "enable-lb-ipam: false — the LB IPAM controller is NOT enabled; it's separate from BGP and must be explicitly turned on"),
        (2, "Check CiliumLoadBalancerIPPool:", "kubectl get ciliumloadbalancerippool -A", "discovery", "No resources found — LB IPAM needs at least one CiliumLoadBalancerIPPool CRD defining available IP ranges"),
        (3, "Check if pool selector matches service:", "kubectl get svc -n anihpj web -o yaml | grep -A5 annotations", "discovery", "No lbipam.cilium.io/ips annotation — the service must either match a pool's serviceSelector or have an explicit IP annotation"),
        (4, "Check if CIDR overlaps with node network:", "kubectl get nodes -o wide", "discovery", "Node CIDR 192.168.100.0/24 overlaps with intended LB pool — Cilium LB IPAM refuses to allocate IPs that conflict with node CIDRs"),
        (5, "Root cause identified:", "LB IPAM not enabled and no IP pool defined", "root-cause", "Cilium LB IPAM is a separate controller from BGP. It requires: 1) enable-lb-ipam=true in ConfigMap, 2) at least one CiliumLoadBalancerIPPool CRD with a non-overlapping CIDR, and 3) the service must match the pool's serviceSelector (or use lbipam.cilium.io/ips annotation). Without LB IPAM, BGP advertises nothing because there are no IPs to advertise"),
    ],
    r"""<span class="token comment"># Fix 1: Enable LB IPAM in Cilium ConfigMap</span>
kubectl patch configmap -n kube-system cilium-config --type merge -p '{"data":{"enable-lb-ipam":"true"}}'

<span class="token comment"># Fix 2: Create an IP pool with a non-overlapping CIDR</span>
cat > lb-pool.yaml << 'EOF'
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: anihpj-lb-pool
spec:
  blocks:
  - cidr: "10.100.0.0/24"
  serviceSelector:
    matchLabels:
      app: anihpj
EOF
kubectl apply -f lb-pool.yaml

<span class="token comment"># Fix 3: Label the service to match the pool selector</span>
kubectl label svc -n anihpj web app=anihpj

<span class="token comment"># Fix 4: Restart Cilium operator and agents</span>
kubectl rollout restart deploy/cilium-operator -n kube-system
kubectl rollout restart ds/cilium -n kube-system
kubectl wait --for=condition=ready pod -n kube-system -l k8s-app=cilium --timeout=120s""",
    "LB IP Allocated",
    "anihpj LoadBalancer Gets External IP from Pool",
    'After enabling LB IPAM and creating the pool, the anihpj service transitions from <code>&lt;pending&gt;</code> to an IP from the 10.100.0.0/24 pool within seconds. <code>kubectl get svc -n anihpj web</code> shows <strong>EXTERNAL-IP: 10.100.0.5</strong>. The BGP speaker advertises this IP. External clients can reach anihpj.',
    ["LB service external IP stuck <pending>", "No CiliumLoadBalancerIPPool exists", "enable-lb-ipam: false in ConfigMap", "Enable LB IPAM + create pool", "IP allocated → BGP advertises → anihpj reachable"],
    "LB IPAM is the allocator — BGP is the announcer. They work together: <strong>LB IPAM</strong> watches LoadBalancer services and allocates IPs from CiliumLoadBalancerIPPool CRDs. <strong>BGP Control Plane</strong> watches allocated IPs and advertises them to peers. Without LB IPAM, BGP has nothing to advertise. Pools can use <code>serviceSelector</code> to allocate only to matching services (multi-tenant), or omit the selector for catch-all allocation.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web\n<span class="output">NAME   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)\nweb    LoadBalancer   10.96.100.50   &lt;pending&gt;     80/TCP    ← Stuck!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ciliumloadbalancerippool\n<span class="output">No resources found    ← No IP pool to allocate from!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web\n<span class="output">NAME   TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)\nweb    LoadBalancer   10.96.100.50   10.100.0.5     80/TCP    ✅ IP allocated!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ciliumloadbalancerippool anihpj-lb-pool -o yaml | grep -A5 status\n<span class="output">status:\n  conditions:\n  - status: "True"\n    type: Ready\n  used:\n    - 10.100.0.5    ✅ IP tracked in pool status!</span></div>',
    ]
)

# ======================== S98 ========================
s98 = sc(98,
    "Enable L2 Announcements for anihpj in Office Network (No BGP)",
    'Your office network has no BGP routers, so you need <strong>L2 Announcements (ARP/NDP)</strong> instead. Cilium L2 announcements are configured but <strong>anihpj LoadBalancer IPs are not responding to ARP</strong>. Your job: configure L2 announcements for anihpj without BGP.',
    r"""<span class="token comment"># No BGP — using L2 announcements instead</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer

<span class="token comment"># ❌ BUG: L2 announcements not working</span>
arp -a | grep 10.100.0.5
<span class="token comment"># (empty — no ARP entry for the LB IP)</span>

<span class="token comment"># Check L2 announcement policy</span>
kubectl get ciliuml2announcementpolicy
<span class="token comment"># No resources found</span>""",
    [
        ("pass", '<strong>1.</strong> LB service with external IP: <code>kubectl get svc -n anihpj</code> → External IP assigned ✅'),
        ("pass", '<strong>2.</strong> Nodes in same L2 domain: <code>kubectl get nodes -o wide</code> → all on same subnet ✅'),
        ("fail", '<strong>3.</strong> ARP not responding: <code>arping -I eth0 10.100.0.5</code> → <strong>no ARP reply — IP not present on L2!</strong> ❌'),
        ("fail", '<strong>4.</strong> No L2 announcement policy: <code>kubectl get ciliuml2announcementpolicy</code> → <strong>No resources found</strong> ❌'),
        ("fail", '<strong>5.</strong> External clients cannot reach: <code>curl http://10.100.0.5</code> → <strong>No route to host</strong> ❌'),
    ],
    [
        (1, "Check if L2 announcements are enabled:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -i l2", "discovery", "enable-l2-announcements: false — L2 announcements are a separate feature from BGP and must be explicitly enabled"),
        (2, "Check CiliumL2AnnouncementPolicy:", "kubectl get ciliuml2announcementpolicy -A", "discovery", "No resources found — an L2 announcement policy CRD is required to specify which IPs to answer ARP for and which interfaces to announce on"),
        (3, "Check node interface for ARP responder:", "ip addr show eth0 | grep -A1 10.100", "discovery", "The LB IP 10.100.0.5 is NOT present as a secondary IP on eth0 — Cilium uses an ARP responder (not IP assignment) to answer ARP requests; the responder needs the policy to know which IPs to respond for"),
        (4, "Check if the LB IP is in the same subnet:", "ip route | grep 10.100", "discovery", "No route for 10.100.0.0/24 — L2 announcements only work if the LB IP is in a subnet reachable from the node's L2 domain"),
        (5, "Root cause identified:", "L2 announcements not enabled and no announcement policy defined", "root-cause", "L2 announcements require: 1) enable-l2-announcements=true in ConfigMap, 2) CiliumL2AnnouncementPolicy CRD specifying interfaces, nodeSelector, and serviceSelector, and 3) a leader election lease (one node per LB IP answers ARP). Without the policy, the ARP responder doesn't know which IPs to answer for or which interfaces to use"),
    ],
    r"""<span class="token comment"># Fix 1: Enable L2 announcements</span>
kubectl patch configmap -n kube-system cilium-config --type merge -p '{"data":{"enable-l2-announcements":"true"}}'

<span class="token comment"># Fix 2: Create L2 announcement policy</span>
cat > l2-policy.yaml << 'EOF'
apiVersion: "cilium.io/v2alpha1"
kind: CiliumL2AnnouncementPolicy
metadata:
  name: anihpj-l2
spec:
  nodeSelector:
    matchLabels:
      kubernetes.io/os: linux
  interfaces:
  - eth0
  serviceSelector:
    matchLabels:
      app: anihpj
  loadBalancerIPs: true
EOF
kubectl apply -f l2-policy.yaml

<span class="token comment"># Fix 3: Label the service</span>
kubectl label svc -n anihpj web app=anihpj

<span class="token comment"># Fix 4: Restart Cilium agents</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system --timeout=120s""",
    "L2 Announcements Working",
    "anihpj LB IP Responds to ARP via L2 Announcements",
    'After enabling L2 announcements and creating the policy, <code>arping -I eth0 10.100.0.5</code> receives ARP replies from the leader node\'s MAC address. <code>curl http://10.100.0.5</code> from any machine in the same L2 domain reaches anihpj. The L2 leader election lease confirms which node is the active ARP responder.',
    ["arping → no ARP reply", "No L2 announcement policy", "enable-l2-announcements: false", "Enable + create policy + label service", "ARP replies received → anihpj reachable"],
    "L2 announcements are BGP-free LoadBalancer IP advertisement for flat networks (office LAN, home lab, single subnet). Cilium uses an <strong>ARP/NDP responder</strong> on one leader node (elected via Kubernetes Lease) to answer ARP requests for the LB IP. Key difference from BGP: L2 only works within the same broadcast domain; BGP works across routed networks. Use L2 for simple setups, BGP for multi-subnet/data center deployments.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> arping -c 3 -I eth0 10.100.0.5\n<span class="output">ARPING 10.100.0.5 from 192.168.1.10 eth0\n(no reply — timeout)    ← No ARP responder!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ciliuml2announcementpolicy\n<span class="output">No resources found    ← No policy created!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> arping -c 3 -I eth0 10.100.0.5\n<span class="output">ARPING 10.100.0.5 from 192.168.1.10 eth0\nUnicast reply from 10.100.0.5 [aa:bb:cc:dd:ee:ff] 0.5ms    ✅ ARP replies!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://10.100.0.5\n<span class="output">&lt;html&gt;...nginx...&lt;/html&gt;    ✅ anihpj reachable via L2!</span></div>',
    ]
)

# ======================== S99 ========================
s99 = sc(99,
    "Debug L2 Announcement Lease Not Being Acquired by Leader",
    'L2 announcements are enabled and the policy exists, but <strong>no node acquires the leader lease</strong> for the anihpj LB IP. ARP requests go unanswered because no node is responding. Your job: debug why the lease is not acquired.',
    r"""<span class="token comment"># L2 policy exists but no leader</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer
kubectl label svc -n anihpj web app=anihpj

<span class="token comment"># ❌ BUG: No leader lease acquired</span>
kubectl get leases -n kube-system | grep cilium-l2
<span class="token comment"># (empty — no L2 lease exists)</span>

arping -c 3 -I eth0 10.100.0.5
<span class="token comment"># (no reply — no leader responding to ARP)</span>""",
    [
        ("pass", '<strong>1.</strong> L2 policy applied: <code>kubectl get ciliuml2announcementpolicy</code> → exists ✅'),
        ("pass", '<strong>2.</strong> L2 announcements enabled: <code>cilium config | grep l2</code> → enabled ✅'),
        ("fail", '<strong>3.</strong> No leader lease: <code>kubectl get leases -n kube-system | grep cilium-l2</code> → <strong>no lease — no node is the ARP responder!</strong> ❌'),
        ("fail", '<strong>4.</strong> ARP unanswered: <code>arping 10.100.0.5</code> → <strong>timeout — no node responding</strong> ❌'),
        ("fail", '<strong>5.</strong> Cilium agent logs: <code>kubectl logs -n kube-system ds/cilium | grep -i "l2\|lease\|leader"</code> → <strong>"L2 announcement lease creation failed: RBAC denied"</strong> ❌'),
    ],
    [
        (1, "Check Cilium agent RBAC for leases:", 'kubectl auth can-i create leases -n kube-system --as=system:serviceaccount:kube-system:cilium', "discovery", "No — Cilium agent ServiceAccount lacks RBAC permissions to create/update Leases; leader election requires Lease coordination.k8s.io/v1 create and update permissions"),
        (2, "Check if nodeSelector matches any nodes:", "kubectl get nodes -l kubernetes.io/os=linux", "discovery", "All nodes have kubernetes.io/os=linux — nodeSelector matches; the issue is not node filtering"),
        (3, "Check if interfaces exist on nodes:", 'kubectl debug node/<node> -it --image=busybox -- ip link show eth0', "discovery", "Interface eth0 exists on all nodes — interface filtering is not the issue"),
        (4, "Check Cilium agent logs for lease errors:", 'kubectl logs -n kube-system ds/cilium | grep -i "lease\|l2\|leader\|rbac\|forbidden"', "discovery", "Failed to create lease: leases.coordination.k8s.io is forbidden — the Cilium agent RBAC (ClusterRole cilium) does not include leases in coordination.k8s.io resources"),
        (5, "Root cause identified:", "Cilium agent lacks RBAC permissions for Lease creation", "root-cause", "L2 leader election uses Kubernetes Lease objects (coordination.k8s.io/v1). The Cilium agent ServiceAccount must have create, get, update on leases in kube-system. If Cilium was installed without L2 announcements initially, the RBAC ClusterRole doesn't include lease permissions. Requires updating the ClusterRole or reinstalling Cilium with L2 support"),
    ],
    r"""<span class="token comment"># Fix 1: Patch Cilium ClusterRole to allow lease management</span>
kubectl patch clusterrole cilium --type json -p '[{"op":"add","path":"/rules/-","value":{"apiGroups":["coordination.k8s.io"],"resources":["leases"],"verbs":["create","get","update","list","watch","delete"]}}]'

<span class="token comment"># Fix 2: Or reinstalling Cilium with L2 enabled (preferred)</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set l2announcements.enabled=true

<span class="token comment"># Fix 3: Restart Cilium agents to pick up new RBAC</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system --timeout=120s

<span class="token comment"># Fix 4: Verify lease is acquired</span>
kubectl get leases -n kube-system | grep cilium-l2""",
    "Leader Lease Acquired",
    "L2 Leader Elected and ARP Responder Active",
    'After granting lease RBAC, <code>kubectl get leases -n kube-system | grep cilium-l2</code> shows an active lease with a holder. <code>arping 10.100.0.5</code> now receives ARP replies from the leader node. The L2 announcement system is fully operational with leader election.',
    ["No leader lease → no ARP responder", "Agent logs: RBAC denied for leases", "Cilium ClusterRole missing lease permissions", "Patch RBAC + restart agents", "Lease acquired → ARP replies → anihpj reachable"],
    "Kubernetes Leases (coordination.k8s.io/v1) are the backbone of Cilium's L2 leader election. Each LB IP gets a lease. The node that holds the lease is the active ARP/NDP responder. If the leader node fails, another node acquires the lease within ~15 seconds (lease duration). Always verify RBAC: <code>kubectl auth can-i create leases --as=system:serviceaccount:kube-system:cilium</code>. This is the #1 cause of L2 announcement failures.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get leases -n kube-system | grep cilium-l2\n<span class="output">(empty — no L2 leader leases exist)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i "lease\|rbac"\n<span class="output">level=error msg="Failed to create L2 announcement lease" error="leases.coordination.k8s.io is forbidden" subsys=l2-announcer    ← RBAC denied!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get leases -n kube-system | grep cilium-l2\n<span class="output">cilium-l2-announce-anihpj-web-lb-ip   cilium-xxxxx   30s    ✅ Leader elected!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> arping -c 1 -I eth0 10.100.0.5\n<span class="output">Unicast reply from 10.100.0.5 [aa:bb:cc:dd:ee:ff] 0.3ms    ✅ ARP responder active!</span></div>',
    ]
)

# ======================== S100 ========================
s100 = sc(100,
    "Fix ARP Requests for anihpj VIP Receiving No Response",
    'L2 announcements are configured and the lease is acquired, but <strong>ARP requests for the anihpj VIP still receive no response</strong>. Other L2 announcements work fine — only the anihpj VIP is unreachable. Your job: find why this specific VIP has no ARP responder.',
    r"""<span class="token comment"># L2 working for other services, but not anihpj</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80 --type=LoadBalancer

<span class="token comment"># ❌ BUG: ARP for anihpj VIP gets no response</span>
arping -c 3 -I eth0 10.100.0.5
<span class="token comment"># (no reply — but other LB IPs work!)</span>

<span class="token comment"># Check if service matches L2 policy selector</span>
kubectl get svc -n anihpj web -o yaml | grep -A5 labels
<span class="token comment"># app: web    ← Does NOT match the L2 policy serviceSelector!</span>""",
    [
        ("pass", '<strong>1.</strong> L2 announcements enabled: <code>cilium config | grep l2</code> → true ✅'),
        ("pass", '<strong>2.</strong> Leader lease acquired: <code>kubectl get leases -n kube-system | grep cilium-l2</code> → exists ✅'),
        ("fail", '<strong>3.</strong> ARP no reply for anihpj: <code>arping 10.100.0.5</code> → <strong>timeout — only this VIP!</strong> ❌'),
        ("fail", '<strong>4.</strong> Service labels mismatch: <code>kubectl get svc -n anihpj web --show-labels</code> → <strong>app=web, not app=anihpj</strong> ❌'),
        ("fail", '<strong>5.</strong> L2 policy has restrictive serviceSelector: <code>kubectl get ciliuml2announcementpolicy -o yaml</code> → <strong>serviceSelector: app=anihpj — service has app=web!</strong> ❌'),
    ],
    [
        (1, "Check L2 policy serviceSelector:", "kubectl get ciliuml2announcementpolicy anihpj-l2 -o yaml | grep -A3 serviceSelector", "discovery", "serviceSelector: {app: anihpj} — the policy only responds for services with label app=anihpj, but the web service has app=web"),
        (2, "Check service labels:", "kubectl get svc -n anihpj web --show-labels", "discovery", "app=web — created by kubectl expose which inherits the deployment labels; the deployment was created without custom labels"),
        (3, "Check if any service matches the selector:", "kubectl get svc -A -l app=anihpj", "discovery", "No resources found — no service has the app=anihpj label; the policy selects zero services"),
        (4, "Check Cilium agent logs for service matching:", 'kubectl logs -n kube-system ds/cilium | grep "l2.*service\|announce.*ip"', "discovery", "No L2 announcement logs for 10.100.0.5 — the Cilium agent doesn't see any service matching the policy selector, so it doesn't create an ARP responder for this IP"),
        (5, "Root cause identified:", "L2 policy serviceSelector doesn't match the service labels", "root-cause", "L2 announcement policies use serviceSelector to determine which LoadBalancer IPs to answer ARP for. If the selector doesn't match the service labels, the ARP responder is never created for that IP. This is a label mismatch — fix the service label or update the policy selector"),
    ],
    r"""<span class="token comment"># Fix 1: Label the service to match L2 policy selector</span>
kubectl label svc -n anihpj web app=anihpj --overwrite

<span class="token comment"># Fix 2: Or update L2 policy to match existing labels</span>
kubectl patch ciliuml2announcementpolicy anihpj-l2 --type merge -p '{"spec":{"serviceSelector":{"matchLabels":{"app":"web"}}}}'

<span class="token comment"># Fix 3: Or remove serviceSelector for catch-all (all LB services)</span>
kubectl patch ciliuml2announcementpolicy anihpj-l2 --type json -p '[{"op":"remove","path":"/spec/serviceSelector"}]'

<span class="token comment"># Fix 4: Verify ARP works immediately</span>
arping -c 3 -I eth0 10.100.0.5""",
    "ARP Responds to VIP",
    "anihpj VIP Responds to ARP Requests",
    'After labeling the service with <code>app=anihpj</code>, the L2 policy matches it. The leader node immediately creates an ARP responder for 10.100.0.5. <code>arping 10.100.0.5</code> receives replies within milliseconds. External clients in the same L2 domain reach anihpj.',
    ["ARP no reply for specific VIP", "Service labels don't match L2 policy", "serviceSelector: app=anihpj ≠ app=web", "Label service to match → ARP works", "All VIPs now responding to ARP"],
    "L2 announcement policy serviceSelector is a <strong>label-based filter</strong> — only LoadBalancer services matching the selector get L2 announcement. This is by design for multi-tenant environments where different services need different announcement policies. Use <code>kubectl get svc -l &lt;selector&gt;</code> to verify which services match. For simplicity in single-tenant setups, omit serviceSelector entirely to announce all LB IPs.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> arping -c 3 -I eth0 10.100.0.5\n<span class="output">ARPING 10.100.0.5 from 192.168.1.10 eth0\n(no reply — timeout)    ← Only this VIP fails!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web --show-labels\n<span class="output">NAME   TYPE           CLUSTER-IP     EXTERNAL-IP    LABELS\nweb    LoadBalancer   10.96.100.50   10.100.0.5     app=web    ← Wrong label!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ciliuml2announcementpolicy anihpj-l2 -o yaml | grep -A2 serviceSelector\n<span class="output">  serviceSelector:\n    matchLabels:\n      app: anihpj    ← Policy wants app=anihpj, service has app=web!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> arping -c 3 -I eth0 10.100.0.5\n<span class="output">ARPING 10.100.0.5 from 192.168.1.10 eth0\nUnicast reply from 10.100.0.5 [aa:bb:cc:dd:ee:ff] 0.4ms\nUnicast reply from 10.100.0.5 [aa:bb:cc:dd:ee:ff] 0.3ms    ✅ ARP working!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> curl -s http://10.100.0.5\n<span class="output">&lt;html&gt;...nginx welcome...&lt;/html&gt;    ✅ anihpj reachable! 🎉</span></div>',
    ]
)

# ====== Insert all 6 ======
all_scenarios = s95 + '\n\n' + s96 + '\n\n' + s97 + '\n\n' + s98 + '\n\n' + s99 + '\n\n' + s100

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ All 6 Cat8 scenarios (S95-S100) inserted!")
else:
    print("ERROR"); exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File: {len(html.encode('utf-8')):,} bytes")
