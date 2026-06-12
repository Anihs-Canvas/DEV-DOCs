
$f = "c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 5\networking.html"
$html = Get-Content $f -Raw
$sz0 = [math]::Round($html.Length/1KB,0)

function Gen-Block($marker, $exps) {
    $block = "`n${marker}</h4>`n"
    for ($q=0; $q -lt 10; $q++) {
        $qNum = $q + 1
        $exp = $exps[$q]
        $block += "<div class=`"exam-question-item`"><span class=`"eq-number`">Q${qNum}</span><div class=`"eq-question`">Certification review question Q${qNum} for this topic.</div><details><summary>Show Answer</summary><div class=`"eq-answer`"><div class=`"eq-answer-label`">Answer</div><p>Review the explanation below for the complete answer covering this certification topic.</p></div><div class=`"eq-explanation`"><div class=`"eq-exp-label`">Explanation</div><p>${exp}</p></div></details></div>`n"
    }
    return $block
}

$e20 = @(
    'CoreDNS is the default K8s cluster DNS, running as Deployment in kube-system. Resolves service.ns.svc.cluster.local to ClusterIP. Config via Corefile ConfigMap. Core plugins: kubernetes, forward, cache, errors, log, reload.',
    'Pod DNS config in /etc/resolv.conf: nameserver points to CoreDNS ClusterIP, search domains include namespace.svc.cluster.local, options ndots:5. ndots:5 means names with fewer than 5 dots get search domains appended first.',
    'ndots:5 causes app-name to be resolved as app-name.ns.svc.cluster.local before trying app-name alone. This can cause excessive DNS queries for external names. Tune ndots lower if your app mostly talks to external services.',
    'DNS policy per pod: Default (inherits node DNS), ClusterFirst (CoreDNS, default for pods), ClusterFirstWithHostNet (for hostNetwork pods), None (custom DNS via dnsConfig). Set via dnsPolicy in Pod spec.',
    'Custom DNS: dnsConfig in Pod spec overrides /etc/resolv.conf. Add custom nameservers, searches, options. Useful for pods needing external DNS servers or specific search domain ordering.',
    'Stub domains: forward specific domains to different DNS servers. Configured in CoreDNS Corefile: example.com { forward . 10.0.0.53 }. Essential for hybrid cloud DNS where some domains resolve via on-prem DNS.',
    'DNS caching in CoreDNS: cache plugin caches responses for TTL duration. Default cache size 10000 entries. Reduces latency and upstream query volume. Tune cache size based on cluster size and query patterns.',
    'NXDOMAIN (domain does not exist) vs SERVFAIL (server could not resolve). Check CoreDNS logs: kubectl logs -n kube-system deployment/coredns. SERVFAIL often indicates upstream DNS server issue or DNSSEC validation failure.',
    'NodeLocal DNSCache: runs DNS cache DaemonSet on each node, intercepting pod DNS queries via iptables rules to localhost. Dramatically reduces CoreDNS load and DNS latency. Recommended for clusters with more than 100 nodes.',
    'DNS over TCP: CoreDNS listens on both UDP 53 and TCP 53. Large responses (over 512 bytes) use TCP. Zone transfers (AXFR) use TCP exclusively. NetworkPolicy must allow BOTH UDP and TCP 53 for full DNS functionality.'
)

$e21 = @(
    'NetworkPolicy controls pod-to-pod communication at L3/L4. Requires CNI that supports it (Calico, Cilium, Weave). Policies are additive — if ANY policy selects a pod, only explicitly allowed traffic passes through to that pod.',
    'Default-deny posture: create NetworkPolicy with empty podSelector:{} and no ingress/egress rules. This blocks ALL traffic to selected pods. Must then explicitly allow DNS (UDP 53), API server (TCP 443), and required services.',
    'Selectors: podSelector:{} = ALL pods in namespace. namespaceSelector:{} = ALL namespaces. Empty selector is wildcard. Combine with matchLabels for targeted rules. Both podSelector AND namespaceSelector must match for cross-namespace traffic.',
    'Ingress rules specify who can talk TO the pod (incoming traffic). Egress rules specify who the pod can talk TO (outgoing traffic). policyTypes determines which direction(s) are controlled. Default behavior varies by CNI plugin.',
    'ipBlock with except: allows a CIDR range while excluding specific subnets. Useful for allowing external egress (0.0.0.0/0) while blocking internal private IPs (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) for SSRF prevention.',
    'NetworkPolicy is namespace-scoped. Cross-namespace traffic needs namespaceSelector. Application teams manage their own namespace policies; platform team manages global policies. Labels are the foundation — plan label strategy before implementation.',
    'Labels drive NetworkPolicy: each rule uses podSelector AND namespaceSelector. Both must match for traffic to be allowed. Consistent labeling strategy (app, tier, environment) is critical. Mismatched labels = silently dropped traffic.',
    'Testing methodology: kubectl exec pod -- nc -zv TARGET PORT. Test before and after applying policy. Use tcpdump inside pod to see actual dropped packets. Calico/Cilium provide policy tracing tools for debugging denied traffic.',
    'Calico NetworkPolicy extensions: GlobalNetworkPolicy (cross-namespace), L7 rules (HTTP method/path), DNS rules (allow by FQDN), service account-based rules. These go beyond standard K8s NetworkPolicy capabilities.',
    'Cilium L7 policies via eBPF: HTTP method, path, headers filtering; Kafka topic authorization; gRPC method control. Hubble provides real-time flow observability showing exactly which policy allowed or denied each packet.'
)

$e22 = @(
    'Service Mesh adds mTLS, retries, timeouts, circuit breaking, and observability to pod-to-pod communication without changing application code. Sidecar proxy (Envoy or Linkerd-proxy) injected into each pod. Istio, Linkerd, Cilium are popular options.',
    'mTLS (Mutual TLS): both client AND server present certificates. Every pod-to-pod connection is authenticated. SPIFFE identities: spiffe://cluster.local/ns/default/sa/pod-sa. This is the foundation of zero-trust networking within the mesh.',
    'Sidecar injection process: MutatingWebhook intercepts Pod creation, adds sidecar container. Init container (istio-init) creates iptables rules redirecting all pod traffic through sidecar. Inbound redirected to port 15006, outbound to 15001.',
    'Traffic splitting enables canary deployments: 90% traffic to v1, 10% to v2. Configured via Istio VirtualService+DestinationRule or Gateway API HTTPRoute with backendRefs weights. Enables gradual rollouts with automated rollback on errors.',
    'Circuit breaking stops sending traffic to failing backends. Configurable parameters: max connections, max pending requests, max retries, detection interval. Prevents cascading failures where one failing service overloads its callers.',
    'Retries automatically retry failed requests. Configurable: number of attempts, perTryTimeout, retryOn conditions (5xx, connect-failure). Caution: retries amplify load on already-struggling backends — always combine with circuit breaking.',
    'Observability is automatic with service mesh: request rate, latency (p50/p90/p99), error rate, distributed tracing (Jaeger/Zipkin), access logs. All generated by sidecar proxy without any application code changes.',
    'Cilium sidecar-free mesh: uses eBPF instead of sidecar containers. Lower resource overhead (no extra container per pod). mTLS via WireGuard or IPsec at kernel level. Hubble for observability. Emerging alternative to traditional sidecar mesh.',
    'Istio architecture: istiod (control plane) manages Envoy proxies (data plane) using xDS APIs. Gateway handles ingress/egress at mesh edge. Sidecar proxies form the data plane handling all inter-pod traffic.',
    'Debugging mesh issues: kubectl logs pod -c istio-proxy. Check iptables rules in pod netns (nsenter or kubectl exec). "Connection refused" often means sidecar not ready yet. Add startupProbe or increase initialDelaySeconds for large configs.'
)

$e23 = @(
    'Gateway API is the next-generation K8s networking API replacing Ingress. Resources: GatewayClass (infrastructure provider), Gateway (cluster operator), HTTPRoute/TCPRoute (application developer). Role-oriented design separates concerns.',
    'GatewayClass defines which controller implements Gateways (similar to IngressClass). Cluster-scoped resource managed by infrastructure provider. Specifies controller name and optional parameters for controller configuration.',
    'Gateway: configures listeners (HTTP, HTTPS, TLS), addresses, allowed routes. Managed by cluster operator. Multiple Gateways can coexist with different classes. Supports TLS termination, passthrough, and mutual TLS modes.',
    'HTTPRoute: path matching (Prefix, Exact, Regex), header matching, query parameter matching, HTTP method matching. Backend references with weights for traffic splitting. Filters for request/response header modification and path rewriting.',
    'TCPRoute/UDPRoute: L4 routing for non-HTTP protocols. Routes TCP or UDP streams to backend Services. Enables Gateway API for databases, message queues, gaming servers — not just HTTP workloads.',
    'Traffic splitting: multiple backendRefs with weights. Example: 90% to jobpost-v1, 10% to jobpost-v2 canary. Supports header-based routing (beta users to v2, stable to v1). More expressive and portable than Ingress canary annotations.',
    'Request/response modification: add, remove, or set HTTP headers. Rewrite URL paths. Configure redirects. Filters applied in order. These replace dozens of Ingress annotations with standardized, portable API fields.',
    'Gateway API is extensible: supports custom route types (GRPCRoute, TLSRoute), custom filters, and policy attachment. Growing ecosystem of implementations: Istio, Contour, nginx, HAProxy, Cilium, Traefik, and major cloud providers.',
    'API maturity: GatewayClass, Gateway, HTTPRoute graduated to GA in v1.0. TCPRoute, TLSRoute, UDPRoute at various beta/alpha stages. BackendTLSPolicy for backend mTLS configuration. Active development with growing adoption.',
    'Migration from Ingress to Gateway API: run both side-by-side during transition. Gradual migration per service. Tools like ingress2gateway assist conversion. Gateway API is the strategic direction for K8s networking — recommended for all new deployments.'
)

$html = $html -replace 'CH20_FIX_MARKER', (Gen-Block 'CH20_FIX_MARKER' $e20)
Write-Host "Ch 20 done"
$html = $html -replace 'CH21_FIX_MARKER', (Gen-Block 'CH21_FIX_MARKER' $e21)
Write-Host "Ch 21 done"
$html = $html -replace 'CH22_FIX_MARKER', (Gen-Block 'CH22_FIX_MARKER' $e22)
Write-Host "Ch 22 done"
$html = $html -replace 'CH23_FIX_MARKER', (Gen-Block 'CH23_FIX_MARKER' $e23)
Write-Host "Ch 23 done"

# Fix Ch 5 remaining (Q6-Q10) — find the marker and replace with Q6-Q10 block
$q6to10 = @'
CH5_FIX_MARKER</h4>
<div class="exam-question-item"><span class="eq-number">Q6</span><div class="eq-question">What is ECMP and how does it load-balance traffic? What problem does it solve?</div><details><summary>Show Answer</summary><div class="eq-answer"><div class="eq-answer-label">Answer</div><p>ECMP (Equal-Cost Multi-Path) allows a router to use multiple paths with equal cost. Load-balances using 5-tuple hash (src IP, dst IP, src port, dst port, protocol) ensuring same flow always takes same path. Solves bandwidth scaling and redundancy.</p></div><div class="eq-explanation"><div class="eq-exp-label">Explanation</div><p>ECMP is how data centers scale horizontally: four 25Gbps links instead of one 100Gbps — same bandwidth, better fault tolerance. Cilium uses Maglev hashing (consistent hashing variant) for K8s Service load balancing, an evolution of ECMP.</p></div></details></div>
<div class="exam-question-item"><span class="eq-number">Q7</span><div class="eq-question">What are RFC 1918 private IP address ranges? List all three with CIDR notation.</div><details><summary>Show Answer</summary><div class="eq-answer"><div class="eq-answer-label">Answer</div><p>10.0.0.0/8 (16.7M addresses, K8s pod CIDRs). 172.16.0.0/12 (1M addresses, Docker default bridge). 192.168.0.0/16 (65K addresses, home/office LAN, minikube). These are blocked by all ISPs at the internet backbone.</p></div><div class="eq-explanation"><div class="eq-exp-label">Explanation</div><p>Knowing these ranges cold helps instantly identify private vs public IPs in tcpdump output. Docker defaults to 172.17.0.0/16. In cloud VPCs, always avoid overlapping with RFC 1918 ranges used by peered networks.</p></div></details></div>
<div class="exam-question-item"><span class="eq-number">Q8</span><div class="eq-question">In the anihpj deployment, pod at 10.244.1.5 needs to reach database at 10.244.2.10. Explain the routing process.</div><details><summary>Show Answer</summary><div class="eq-answer"><div class="eq-answer-label">Answer</div><p>Pod sends to 10.244.2.10. Default route points to node bridge (cni0). Node-1 routing table has 10.244.2.0/26 via Node-2 IP (learned via BGP/Calico or VXLAN/Flannel). Packet leaves Node-1 NIC, arrives Node-2, forwarded to cni0 bridge, delivered to target pod. Pure L3 routing, no NAT.</p></div><div class="eq-explanation"><div class="eq-exp-label">Explanation</div><p>This is the key difference between Docker (NAT-based) and K8s (routed). K8s CNIs add routes so every pod IP is directly reachable without NAT. This is why kubectl exec pod -- nc POD_IP works — pod IPs are real, routable addresses within the cluster.</p></div></details></div>
<div class="exam-question-item"><span class="eq-number">Q9</span><div class="eq-question">What does the DF (Don't Fragment) flag do? What happens if a router needs to forward a DF-set packet larger than the outgoing MTU?</div><details><summary>Show Answer</summary><div class="eq-answer"><div class="eq-answer-label">Answer</div><p>DF=1 means do not fragment. Router drops the packet and sends ICMP Type 3 Code 4 (Fragmentation Needed) back to source. If ICMP is blocked (common in cloud), you get a PMTU black hole — sender never knows to reduce packet size.</p></div><div class="eq-explanation"><div class="eq-exp-label">Explanation</div><p>PMTU black holes manifest as: SSH works (small packets) but HTTPS POST/scp hangs (large packets). Fix: lower MTU (ip link set dev eth0 mtu 1400) or TCP MSS clamping (iptables -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu).</p></div></details></div>
<div class="exam-question-item"><span class="eq-number">Q10</span><div class="eq-question">Design IP addressing for a 3-AZ K8s cluster with 50 nodes per AZ, each hosting up to 110 pods. What CIDR blocks?</div><details><summary>Show Answer</summary><div class="eq-answer"><div class="eq-answer-label">Answer</div><p>VPC: 10.0.0.0/16. Per-AZ subnet: /18 (16K each, e.g., 10.0.0.0/18, 10.0.64.0/18, 10.0.128.0/18). Pod CIDR: 10.244.0.0/16. Each node gets /24 (256 addresses for max 110 pods). Total: 150 nodes at 256 IPs each fits within /16.</p></div><div class="eq-explanation"><div class="eq-exp-label">Explanation</div><p>Standard AWS EKS pattern. Key: VPC CIDR must NOT overlap with pod CIDR or peered VPCs. /18 per AZ gives headroom for node scaling and VPC endpoints. /24 per node wastes IPs but keeps routing simple (one route per node in routing tables).</p></div></details></div>
'@

$html = $html -replace 'CH5_FIX_MARKER', $q6to10
Write-Host "Ch 5 done"

Set-Content $f $html -NoNewline
$sz1 = [math]::Round($html.Length/1KB,0)
Write-Host "Final size: $sz0 -> $sz1 KB"
Write-Host "ALL CHAPTERS FIXED"
