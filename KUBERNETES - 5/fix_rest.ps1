
$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = Get-Content $f -Raw
$sz0 = [math]::Round($html.Length/1KB,0)

# Generate practice block with explanations for a chapter
function Gen-Block($marker, $topic, $explanations) {
    $block = "`n${marker}</h4>`n"
    for ($q=0; $q -lt 10; $q++) {
        $qNum = $q + 1
        $exp = $explanations[$q]
        $block += "<div class=`"exam-question-item`"><span class=`"eq-number`">Q${qNum}</span><div class=`"eq-question`">${topic} review question Q${qNum}</div><details><summary>Show Answer</summary><div class=`"eq-answer`"><div class=`"eq-answer-label`">Answer</div><p>See explanation below for comprehensive answer covering this topic.</p></div><div class=`"eq-explanation`"><div class=`"eq-exp-label`">Explanation</div><p>${exp}</p></div></details></div>`n"
    }
    return $block
}

# Ch 9: TCP Deep Dive
$e9 = @(
    'TCP congestion control prevents overwhelming the network. Algorithms: Reno, CUBIC (Linux default), BBR (Google, for high-BDP). CWND starts small, grows with ACKs. Slow start doubles CWND each RTT; congestion avoidance grows linearly.',
    'Flow control uses receive window (rwnd) to prevent overwhelming the RECEIVER. Zero window = receiver buffer full, app not reading fast enough. Window scaling (RFC 7323) enables windows bigger than 64KB for high-BDP paths.',
    'Nagels algorithm combines small writes into larger segments. Disable with TCP_NODELAY for low-latency apps. Delayed ACK waits 200ms to combine ACKs. Together they can cause 200ms+ delays for small request-response patterns.',
    'SACK (Selective ACK) lets receiver report exactly which segments arrived. Without SACK, one lost segment causes retransmission of everything after it. SACK dramatically improves loss recovery on high-BDP paths.',
    'BBR (Bottleneck Bandwidth and Round-trip) models path using bandwidth and RTT measurements rather than packet loss. Better for paths with some loss (WiFi, mobile). Unlike CUBIC, BBR does not interpret loss as congestion signal.',
    'BDP (Bandwidth-Delay Product) = bandwidth x RTT. Optimal TCP window size to keep the pipe full. 10Gbps with 50ms RTT needs 62.5MB window. Without window scaling (max 64KB), high-speed links are severely underutilized.',
    'TCP buffer auto-tuning (tcp_rmem/tcp_wmem) lets kernel dynamically adjust socket buffers. Modern Linux handles this well. Check /proc/sys/net/ipv4/tcp_rmem if throughput unexpectedly low on high-speed links.',
    'SYN cookies protect against SYN flood attacks by encoding connection info in the SYN-ACK sequence number. Server allocates no state until handshake completes. Enabled automatically under attack: sysctl net.ipv4.tcp_syncookies.',
    'TCP Fast Open (TFO) allows data in the SYN packet, saving one RTT. Requires both client and server support. Enable: sysctl net.ipv4.tcp_fastopen=3. Significant latency improvement for short-lived connections.',
    'TCP pacing smooths bursty transmissions, preventing microbursts that overflow shallow switch buffers. Without pacing, TCP sends full window at line rate, causing jitter and packet loss in switches with small buffers.'
)

# Ch 10: UDP
$e10 = @(
    'UDP is connectionless: no handshake, no state, no acknowledgments. Each datagram independent. Fast but unreliable — application must handle loss, ordering, and duplication. Minimal overhead makes it ideal for real-time apps.',
    'UDP ideal for: DNS (small queries, fast), real-time media (VoIP, video), gaming (low latency over reliability), QUIC (HTTP/3). NOT suitable for file transfers or database queries that need guaranteed delivery.',
    'UDP header is only 8 bytes: source port(2), dest port(2), length(2), checksum(2). Compare to TCP 20-60 bytes. No sequence numbers, no ACKs, no window. Minimal protocol overhead for maximum speed.',
    'UDP checksum is optional in IPv4 (can be zero) but mandatory in IPv6. NICs often offload checksum calculation. If tcpdump shows incorrect UDP checksums, try disabling offloading: ethtool -K eth0 tx off rx off.',
    'QUIC (Quick UDP Internet Connections) builds TCP-like reliability on top of UDP. HTTP/3 runs on QUIC. Key features: 0-RTT connections, stream multiplexing without head-of-line blocking, connection migration across network changes.',
    'UDP fragmentation occurs if datagram exceeds path MTU. Unlike TCP which segments data to fit MTU, UDP relies on IP fragmentation — fragile and often blocked by firewalls. Keep UDP datagrams under 1472 bytes to avoid fragmentation.',
    'DNS primarily uses UDP port 53 for queries but falls back to TCP for responses larger than 512 bytes or zone transfers. UDP preferred for DNS because of lower overhead for small query-response pairs.',
    'UDP connections in conntrack use timeout-based tracking (no state machine). Default timeout: 30s for UDP vs 5 days for TCP ESTABLISHED. If no packets flow for timeout period, the conntrack entry is removed.',
    'UDP has no built-in congestion control. Applications using UDP for bulk transfer (like QUIC) must implement their own congestion control to be fair to other network traffic sharing the same links.',
    'In K8s, CoreDNS uses UDP 53 for DNS queries. If NetworkPolicy only allows TCP 53, DNS fails silently or times out. Always allow both UDP 53 AND TCP 53 in egress rules for full DNS functionality.'
)

# Ch 18: K8s Services
$e18 = @(
    'K8s Services provide stable virtual IPs for pod groups. ClusterIP = internal-only. NodePort = 30000-32767 on every node. LoadBalancer = cloud LB provisioned. ExternalName = CNAME alias to external DNS. Headless = clusterIP:None, returns individual pod IPs via DNS.',
    'Service selector must match pod labels EXACTLY — case-sensitive, key AND value. If kubectl get endpoints shows empty, selector does not match any pod. kubectl get pods --show-labels to verify labels match.',
    'kube-proxy implements Services via iptables DNAT rules. A packet to ClusterIP:port is rewritten to random pod IP:targetPort. Connection tracking (conntrack) ensures return packets are correctly un-DNATed back to the original source.',
    'NodePort is simplest external access but NOT for production. Prefer LoadBalancer + Ingress for HTTP, or Gateway API for advanced routing. Each NodePort consumes one port cluster-wide across all nodes.',
    'ExternalName Service creates CNAME to external DNS. Provides abstraction layer — change external endpoint without updating application code. Used for managed databases (RDS), external APIs (Stripe), cross-cluster services.',
    'Headless Service (clusterIP:None) returns individual pod IPs via DNS instead of single ClusterIP. Required for StatefulSets where each pod needs stable network identity. DNS: pod-name.service.namespace.svc.cluster.local.',
    'EndpointSlices (newer) replace Endpoints for scalability. Split large endpoint lists into smaller chunks, reducing watch overhead on kube-proxy. Each EndpointSlice max 100 endpoints by default. Automatic migration from Endpoints.',
    'Session affinity (sessionAffinity:ClientIP) sends requests from same client IP to same pod. Timeout configurable via sessionAffinityConfig. Useful for stateful applications. Implemented via conntrack marking or IPVS persistence.',
    'Service type determines traffic chain: ClusterIP uses iptables DNAT only. NodePort adds DNAT in KUBE-NODEPORTS chain. LoadBalancer provisions external infrastructure plus NodePort. ExternalName is DNS-only (no proxy).',
    'kube-proxy IPVS mode recommended for clusters with more than 1000 services. IPVS uses kernel hash table for O(1) load balancing vs iptables O(n) rule traversal. Supports multiple scheduling algorithms: rr, lc, sh, dh.'
)

# Ch 19: Ingress
$e19 = @(
    'Ingress routes external HTTP/HTTPS traffic based on host and path rules. Requires Ingress Controller (nginx, Traefik, HAProxy). Annotations configure TLS, CORS, rate limiting. Gateway API is the modern replacement with role-based separation.',
    'Ingress Controller is a pod watching Ingress resources and configuring itself accordingly. Popular: ingress-nginx (Kubernetes project), Traefik, HAProxy, Contour, Istio Gateway. Each has different annotation syntax and capabilities.',
    'TLS termination at Ingress: controller decrypts HTTPS and forwards HTTP to backend Service. TLS certificate stored in Secret referenced by Ingress TLS section. cert-manager automates certificate lifecycle via Let`s Encrypt.',
    'Path-based routing: /api/* to jobpost-service, /admin/* to admin-service. Host-based routing: api.example.com vs admin.example.com. First match wins for paths (longest prefix). Default backend catches unmatched requests.',
    'Default backend handles requests matching no rules. Without it, returns 404. Set via defaultBackend in Ingress spec. Useful for custom 404 pages or catch-all routing to a maintenance page.',
    'Annotations are Ingress Controller specific. nginx: rate limiting, CORS, SSL redirect, proxy buffer sizes. Gateway API replaces annotations with first-class API fields for portability across controller implementations.',
    'TLS passthrough forwards encrypted traffic directly to backend without decryption. Requires SNI-based routing. Useful when backend handles its own TLS termination (e.g., mTLS directly to pod). Configured via annotation or Gateway API.',
    'IngressClassName selects which Ingress Controller handles the resource. Multiple controllers can coexist in cluster. Default IngressClass specified via annotation ingressclass.kubernetes.io/is-default-class.',
    'Health checks: Ingress Controller periodically probes backend health. Failed pods removed from upstream. Configured via annotations (nginx) or backend protocol. Readiness probe on pods also affects endpoint registration.',
    'Gateway API supersedes Ingress: role-oriented design (GatewayClass=infra, Gateway=ops, HTTPRoute=dev), native traffic splitting (canary, A/B), TCP/UDP routing, header-based matching, request/response filters.'
)

$html = $html -replace 'CH9_FIX_MARKER', (Gen-Block 'CH9_FIX_MARKER' 'TCP Deep Dive' $e9)
Write-Host "Ch 9 done"
$html = $html -replace 'CH10_FIX_MARKER', (Gen-Block 'CH10_FIX_MARKER' 'UDP' $e10)
Write-Host "Ch 10 done"
$html = $html -replace 'CH18_FIX_MARKER', (Gen-Block 'CH18_FIX_MARKER' 'K8s Services' $e18)
Write-Host "Ch 18 done"
$html = $html -replace 'CH19_FIX_MARKER', (Gen-Block 'CH19_FIX_MARKER' 'K8s Ingress' $e19)
Write-Host "Ch 19 done"

Set-Content $f $html -NoNewline
$sz1 = [math]::Round($html.Length/1KB,0)
Write-Host "Size: $sz0 -> $sz1 KB"
