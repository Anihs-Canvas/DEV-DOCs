# -*- coding: utf-8 -*-
import os

# All Category 2 issues as flat list of dicts
cat2 = []

def add_issue(pid, pid_detail, title, cat, symptom, ml, ll, nc, sol, adv, la):
    cat2.append({
        'pid': pid, 'pid_detail': pid_detail, 'title': title, 'cat': cat,
        'symptom': symptom, 'ml': ml, 'll': ll, 'nc': nc, 'sol': sol, 'adv': adv, 'la': la
    })

# P1-P5: CNP Not Enforcing
add_issue("P1","ts-p1-detail","CiliumNetworkPolicy Not Applied to Pods","🛡️ CATEGORY 2: NETWORK POLICY — Issue P1","You create a CiliumNetworkPolicy but traffic still flows as if the policy doesn't exist. <code>cilium policy get</code> shows the policy but endpoints aren't enforcing it.",
    [("endpointSelector mismatch:","Policy selects pods by labels. Run <code>kubectl get pods -l &lt;selector&gt;</code>. If no pods match, policy does nothing."),
     ("Policy in wrong namespace:","CNP is namespaced. A CNP in 'default' does NOT affect pods in 'anihpj'. Verify with <code>kubectl get cnp -n anihpj</code>."),
     ("Policy status not enforced:","Check <code>cilium-dbg bpf policy get &lt;id&gt;</code>. If 'Disabled', agent hasn't processed it. Restart agent."),
     ("CiliumClusterwideNetworkPolicy needed:","For cluster-wide rules or host-level rules, use CCNP not CNP."),
     ("CRD schema validation failed:","Check <code>kubectl describe cnp &lt;name&gt;</code> for events. Use <code>cilium policy validate file.yaml</code>.")],
    ["Policy version conflict (two policies with same name in different API versions)","CiliumEndpoint CRD not updated with new policy revision","Agent watch on CNP CRD broken — missed create event","Policy with empty ingress AND egress (implicit deny but no explicit allow)","Kubernetes NetworkPolicy with same selector overriding Cilium behavior"],
    [("CNP CRD not installed:","Check <code>kubectl get crd ciliumnetworkpolicies.cilium.io</code>. If missing, Cilium wasn't installed correctly."),
     ("No default-deny:","New cluster has no policies — all traffic allowed. Apply default-deny first."),
     ("Agent not watching namespace:","Check <code>cilium config | grep policy</code>. Must be 'default' or 'always'."),
     ("Wrong API version:","CNP v1 vs v2 have different schemas. Check Cilium version compatibility."),
     ("Helm disables policy:","Check <code>cilium config | grep enable-policy</code>. Must be 'default' or 'always'.")],
    "1. <code>cilium policy get</code> — verify policy enforced<br>2. <code>kubectl get pods -l &lt;selector&gt; -A</code> — verify selector matches<br>3. <code>cilium-dbg bpf policy get &lt;id&gt;</code> — check BPF policy map<br>4. <code>hubble observe --verdict DROPPED</code> — verify drops<br>5. If not in BPF: restart agent pod on affected node",
    "<strong>💡 Personal Advice:</strong> The #1 reason CNPs 'don't work' is selector mismatch. Run <code>kubectl get pods -l</code> with the exact selector BEFORE applying. For anihpj: add <code>policy-group: api</code> label to pods for trivial selectors.",
    "<strong>🔍 What to Look At:</strong> <code>cilium policy get</code> shows Enabled vs Disabled. <code>kubectl describe cnp</code> has Status field. Selector matching 0 pods = silently inactive.")

add_issue("P2","ts-p2-detail","CNP Blocks Traffic But Should Allow","🛡️ CATEGORY 2: NETWORK POLICY — Issue P2","CNP applied but legitimate anihpj-web→anihpj-api traffic blocked. Hubble shows DROPPED. Policy has allow rule but it's not matching.",
    [("Rule ordering:","Rules evaluated top-to-bottom. Deny before allow = blocked. Check YAML order."),
     ("fromEndpoints label mismatch:","Source pod labels changed. Verify labels on both source and destination."),
     ("namespaceSelector missing:","fromEndpoints without namespaceSelector only matches SAME namespace. Add <code>namespaceSelector: {}</code> for all."),
     ("Protocol/port mismatch:","Rule says port 8080 but app listens on 8443. Check <code>kubectl get svc --show-labels</code>."),
     ("Policy union confusion:","Cilium uses UNION for CNP+KNP. KNP allow + CNP deny = ALLOW (union wins).")],
    ["L7 rule redirecting to proxy but proxy not running","toFQDNs with DNS not resolved (fails first, works later)","fromCIDR but pod IP not in that CIDR","CCNP and CNP conflicting on same endpoint","Policy applied to wrong direction (ingress on source instead of dest)"],
    [("No allow rules:","New cluster all-allowed. First CNP with ANY deny blocks everything. Create allows first."),
     ("Default-deny before allows:","Apply allow rules FIRST, then default-deny. Order matters."),
     ("Labels not standardized:","Pods need consistent labels (app=anihpj, component=api)."),
     ("Wrong namespace in trace:","<code>cilium policy trace</code> needs correct source/dest namespaces."),
     ("Cluster Mesh policies:","If Cluster Mesh active, imported policies from other clusters apply.")],
    "1. <code>cilium policy trace --src-k8s-pod ns:src --dst-k8s-pod ns:dst --dport X</code><br>2. Review YAML rule order<br>3. <code>hubble observe --verdict DROPPED --from-pod ns/src</code><br>4. Verify labels: <code>kubectl get pods --show-labels</code><br>5. Test with audit mode first",
    "<strong>💡 Personal Advice:</strong> Use <code>cilium policy trace</code> BEFORE deploying — it shows exact matching rule. For anihpj: keep a debug namespace with no policies for connectivity testing.",
    "<strong>🔍 What to Look At:</strong> Trace shows FINAL verdict + matching rule. Union: KNP+CNP = ALLOW if either allows. namespaceSelector REQUIRED for cross-ns. Rule order matters in CNP.")

add_issue("P3","ts-p3-detail","Default-Deny Blocks All Traffic Including DNS","🛡️ CATEGORY 2: NETWORK POLICY — Issue P3","Default-deny CNP applied. All pods lose connectivity — even DNS stops. Nothing can reach anything.",
    [("DNS rule missing:","Default-deny blocks EVERYTHING including DNS (UDP 53). FIRST egress rule MUST allow DNS to kube-dns."),
     ("No allow rules at all:","Policy with empty ingress:[] means deny all. Need explicit allows."),
     ("Health probes blocked:","Kubelet liveness/readiness probes blocked. Add <code>toEntities: [host]</code>."),
     ("kube-apiserver blocked:","Pods need kube-apiserver access. Add <code>toEntities: [kube-apiserver]</code>."),
     ("CoreDNS cross-namespace:","CoreDNS in kube-system. CNP in anihpj must have egress to kube-system labels.")],
    ["CNP with no egress blocks outbound but ingress from others still reaches","Agent health endpoint blocked causing unhealthy agent","Prometheus scraping blocked","Sidecar mesh communication blocked on different ports","CNI meta-plugin communication blocked"],
    [("No baseline:","Start permissive, lock down gradually. Don't default-deny on day 0."),
     ("No DNS template:","Always deploy standard 'allow-dns' CNP before restrictive policies."),
     ("Missing fromEntities: [cluster]:","Allow all cluster-internal traffic as baseline."),
     ("CCNP too broad:","CCNP default-deny affects ALL namespaces. Use namespaced CNP."),
     ("No audit testing:","Apply with <code>policyAudit: true</code> first to see what would break.")],
    "1. Add DNS allow FIRST: egress to kube-dns UDP 53<br>2. Add cluster: <code>fromEntities: [cluster]</code> for ingress<br>3. Add egress: <code>toEntities: [cluster]</code> for outbound<br>4. Add kube-apiserver: <code>toEntities: [kube-apiserver]</code><br>5. <code>cilium policy trace</code> before applying",
    "<strong>💡 Personal Advice:</strong> The DNS lesson is painful. Default-deny = everything blocked, including DNS. For anihpj: create dns-allow.yaml and ALWAYS deploy it before any restrictive CNP.",
    "<strong>🔍 What to Look At:</strong> Hubble shows DNS drops as UDP/53 to 10.96.0.10. Trace with --dport 53 shows DENIED. Always include DNS allow as rule #1 in any restrictive policy.")

add_issue("P4","ts-p4-detail","L3/L4 Works But L7 Rules Ignored","🛡️ CATEGORY 2: NETWORK POLICY — Issue P4","CNP with L3/L4 and L7 rules. Port blocking works but HTTP method/path filtering ignored — all methods pass through.",
    [("L7 proxy not enabled:","L7 requires Envoy. Check <code>cilium status | grep Proxy</code>. Enable with <code>--set proxy.enabled=true</code>."),
     ("L7 rule syntax error:","Rules under <code>toPorts: [{ports: [...], rules: {http: [...]}}]</code>. Wrong nesting silently fails."),
     ("Proxy redirection not active:","<code>cilium-dbg bpf proxy list</code> empty. Restart agent after enabling proxy."),
     ("Port mismatch L3 vs L7:","L7 rules only apply to port they're nested under. Check correct port."),
     ("HTTP/2 or gRPC traffic:","L7 HTTP rules only inspect HTTP/1.1. HTTP/2/gRPC need dedicated rules.")],
    ["Envoy proxy crash or resource exhaustion","Too many L7 policies causing proxy config timeout","TLS traffic — L7 inspection needs TLS termination","Kafka L7 needs specific Kafka proxy config","Proxy listener port conflict with service port"],
    [("Proxy not in default install:","Add <code>--set proxy.enabled=true</code> on fresh install."),
     ("Envoy image unavailable:","Check <code>kubectl get pods -n kube-system -l app=envoy</code>."),
     ("Kernel too old for socket redirect:","L7 proxy needs kernel 5.7+ for optimal redirect."),
     ("Mixed L3/L7 syntax:","New users confuse CNP and CCNP L7 formats. Check examples."),
     ("No test traffic:","L7 activates only when traffic hits the protected port. Generate traffic.")],
    "1. <code>cilium status | grep Proxy</code><br>2. <code>cilium-dbg bpf proxy list</code><br>3. <code>hubble observe --protocol HTTP</code><br>4. Check CNP YAML nesting<br>5. Test: <code>curl -X GET svc/api</code> vs <code>curl -X POST</code>",
    "<strong>💡 Personal Advice:</strong> L7 adds ~1-2ms latency per request through Envoy. Don't use L7 when L3/L4 suffices. For anihpj: L3/L4 for service-to-service, L7 only for method/path control like blocking POST /admin.",
    "<strong>🔍 What to Look At:</strong> Proxy must be 'Running'. Hubble shows HTTP details only through proxy. gRPC needs separate rules. L7 rules nested under correct toPorts entry.")

add_issue("P5","ts-p5-detail","NetworkPolicy Rules Work Intermittently","🛡️ CATEGORY 2: NETWORK POLICY — Issue P5","CNP sometimes blocks, sometimes allows. Same curl works 3/5 times. Hubble shows mixed FORWARDED/DROPPED.",
    [("toFQDNs DNS TTL:","FQDN resolves to IP. When TTL expires, new IP may differ. Old IP still allowed until re-resolution."),
     ("Policy order race:","Multiple policies competing. BPF map evaluation order determines behavior."),
     ("Pod restart identity change:","New identity on restart. Policy may block until new identity syncs."),
     ("CES identity sync lag:","CiliumEndpointSlice batch delay. Stale identities cause intermittent blocks."),
     ("DNS cache inconsistency:","Between re-resolution cycles, cached IPs differ from actual. First=allowed, second=blocked.")],
    ["BPF conntrack timeout between requests causing re-evaluation","LB sending to different backends with different identities","Hubble sampling making it appear intermittent","fromCIDR with changing pod IPs (CIDR static, IPs change)","NodeLocal DNSCache bypassing Cilium DNS proxy"],
    [("toFQDNs not resolved:","First connections to FQDN may fail until DNS resolved. Retry."),
     ("Agent version mismatch:","Different agent versions causing policy sync issues."),
     ("Incomplete rollout:","Not all agents received updated policy. <code>cilium policy wait &lt;rev&gt;</code>."),
     ("EndpointSlice not updated:","Service endpoints changed but not propagated."),
     ("Multiple CNPs same selector:","Overlapping rules cause evaluation ordering issues.")],
    "1. <code>hubble observe --verdict DROPPED -o json</code> — patterns<br>2. <code>cilium policy trace</code> multiple times<br>3. <code>cilium-dbg bpf policy get &lt;id&gt;</code> — revision check<br>4. toFQDNs: <code>cilium-dbg fqdn cache list</code><br>5. <code>kubectl get cep -A | grep &lt;pod&gt;</code>",
    "<strong>💡 Personal Advice:</strong> Intermittent = DNS (toFQDNs) or identity sync lag. For anihpj: avoid toFQDNs for internal services — use ClusterIP or CIDRGroup instead.",
    "<strong>🔍 What to Look At:</strong> Run trace multiple times. Same result = stable. Different = race. DNS cache: cilium-dbg fqdn cache list. Identity: check after pod restart.")

# P6-P10: L7 Policy Issues
add_issue("P6","ts-p6-detail","HTTP L7 Rule Not Matching Specific Path","📋 CATEGORY 2: NETWORK POLICY — Issue P6","HTTP L7 rule with path '/api/.*' matching all paths including /admin. Regex not working as expected.",
    [("RE2 regex, not PCRE:","Cilium uses RE2. No backreferences, no lookaheads. /api/.* matches /api AND /api/admin. Use <code>/api/[^/]+$</code> for exact."),
     ("Missing anchors:","Without ^ and $, pattern matches anywhere. Use <code>^/api$</code> for exact match."),
     ("Headers ANDed:","Multiple header conditions are ANDed. Both must match."),
     ("Method without path:","method: GET without path matches ALL GET requests. Add path restriction."),
     ("Wrong toPorts entry:","Each toPorts with L7 creates separate proxy listener. Rules in one don't apply to another.")],
    ["HTTP/2 not inspected (binary to HTTP parser)","Encoded URLs (%2F) not matching regex","Query params in path (strip ? and after)","Case sensitivity in header values","Request body exceeding proxy buffer"],
    [("RE2 unfamiliar:","Practice RE2. No negative lookaheads. Use [^/]+ instead."),
     ("Testing without anchors:","Always test regex with ^...$ anchors."),
     ("HTTP/2 lowercases headers:","Use lowercase in policy rules for HTTP/2."),
     ("Multiple L7 policies merged:","All L7 rules for a port merge. Check for conflicts."),
     ("No Hubble verification:","Use <code>hubble observe --http-path /test</code> to verify.")],
    "1. Test regex externally: <code>echo '/api/users' | grep -E '^/api/[^/]+$'</code><br>2. <code>hubble observe --protocol HTTP --http-path /api</code><br>3. Check merged: <code>cilium-dbg bpf policy get &lt;id&gt;</code><br>4. Start simple: method-only, then add path<br>5. <code>cilium policy trace</code> with simulated request",
    "<strong>💡 Personal Advice:</strong> Path regex is #1 L7 headache. Test externally first. For anihpj: use TWO rules — allow GET /api/.*, deny POST /admin/.*. Deny-allow ordering critical.",
    "<strong>🔍 What to Look At:</strong> RE2 ≠ PCRE. No lookaheads. Hubble shows ACTUAL matched path. Headers must match EXACTLY. Test regex with ^...$ anchors.")

add_issue("P7","ts-p7-detail","DNS Policy Not Resolving Specific Domains","📋 CATEGORY 2: NETWORK POLICY — Issue P7","toFQDNs policy allows api.github.com but DNS fails. Hubble shows DNS queries dropped or NXDOMAIN.",
    [("matchName vs matchPattern:","<code>matchName: 'api.github.com'</code> = EXACT. <code>matchPattern: '*.github.com'</code> = wildcard. Wrong type silently fails."),
     ("DNS proxy not intercepting:","Check <code>cilium status | grep DNS</code>. DNS proxy must be enabled."),
     ("CoreDNS bypassed:","NodeLocal DNSCache or custom resolv.conf bypasses Cilium DNS proxy."),
     ("TCP/53 blocked:","Large DNS responses use TCP/53. Allow both UDP and TCP/53."),
     ("toFQDNs under wrong section:","toFQDNs is egress only. Putting under ingress silently fails.")],
    ["DNS cache TTL expired and re-resolution blocked","CNAME chain too long (each hop needs policy match)","DNS IP change but old IP cached","L7 DNS conflicting with L3 DNS (L3 allows all, L7 restricts)","DNS proxy rate limiting"],
    [("DNS proxy not enabled:","toFQDNs requires DNS proxy. <code>--set dnsProxy.enabled=true</code>."),
     ("No CoreDNS allow:","Pod needs egress to CoreDNS UDP/TCP 53 even with toFQDNs."),
     ("matchPattern wrong:","Pattern is glob: *.example.com (not regex). Only * supported."),
     ("FQDN in wrong namespace:","Cross-namespace toFQDNs needs CCNP."),
     ("DNS timeout before proxy ready:","First lookup may timeout. Retry.")],
    "1. <code>hubble observe --protocol DNS --from-pod ns/pod</code><br>2. <code>cilium-dbg fqdn cache list</code><br>3. <code>kubectl exec pod -- nslookup api.github.com</code><br>4. Verify matchPattern uses * wildcard<br>5. <code>cilium status | grep DNS</code>",
    "<strong>💡 Personal Advice:</strong> toFQDNs is powerful but tricky. DNS proxy MUST intercept. For critical APIs, use CiliumCIDRGroup instead — more reliable than DNS-dependent policies.",
    "<strong>🔍 What to Look At:</strong> matchName = exact. matchPattern = glob (*.example.com). DNS proxy must be OK. Hubble shows DNS QTypes. DNS cache shows resolved IPs.")

add_issue("P8","ts-p8-detail","Kafka L7 Policy Not Filtering Messages","📋 CATEGORY 2: NETWORK POLICY — Issue P8","CNP with Kafka L7 rules (topic filtering) applied but all messages pass regardless of topic.",
    [("Kafka proxy not configured:","Kafka L7 needs dedicated proxy. Enable: <code>--set kafka.enabled=true</code>."),
     ("Topic name case-sensitive:","'Orders' ≠ 'orders'. Verify exact Kafka topic name."),
     ("API version mismatch:","Cilium Kafka inspection works with API versions 0-2. Newer may not parse."),
     ("Non-standard port:","Kafka default 9092. If using different port, add explicit port in rules."),
     ("SASL/SSL encrypted:","Proxy must terminate TLS to inspect. Configure TLS certs in Cilium.")],
    ["Message batching causing incomplete data to proxy","Multiple brokers — proxy only intercepts targeted broker","ZooKeeper separate from Kafka (not inspected)","Client library version incompatible with proxy","Proxy buffer overflow on large messages"],
    [("Kafka not default:","Install with <code>--set kafka.enabled=true</code>."),
     ("Proxy pod not running:","Check <code>kubectl get pods -n kube-system | grep kafka</code>."),
     ("CNP syntax:","<code>rules: {kafka: [{role: 'consume', topic: 'orders'}]}</code>. Role: consume/produce."),
     ("No real traffic:","Kafka proxy activates on Kafka protocol. Generate real traffic."),
     ("No Kafka in test env:","Set up test Kafka pod if needed.")],
    "1. <code>kubectl logs -n kube-system -l app=cilium-envoy | grep kafka</code><br>2. <code>hubble observe --protocol KAFKA</code><br>3. Verify topic: <code>kubectl exec kafka-pod -- kafka-topics --list</code><br>4. <code>cilium-dbg bpf proxy list | grep kafka</code><br>5. Test with kafka-console-producer/consumer",
    "<strong>💡 Personal Advice:</strong> Kafka L7 is niche. For CCA: know it exists with topic/role filtering. For anihpj: unless jobpost uses Kafka, stick with HTTP L7.",
    "<strong>🔍 What to Look At:</strong> Kafka proxy separately enabled. Topic case-sensitive exact match. Role: consume/produce. Hubble shows Kafka protocol. SASL/SSL needs TLS termination.")

add_issue("P9","ts-p9-detail","gRPC L7 Policy Not Working","📋 CATEGORY 2: NETWORK POLICY — Issue P9","CNP with gRPC L7 rules applied but all gRPC methods pass through unfiltered.",
    [("gRPC under http section:","gRPC rules must use <code>rules: {grpc: [...]}</code>, NOT <code>rules: {http: [...]}</code>."),
     ("Method path format:","gRPC method is <code>/package.Service/Method</code>. Must match exactly."),
     ("HTTP/2 required:","gRPC uses HTTP/2. Proxy must support HTTP/2."),
     ("TLS termination needed:","Encrypted gRPC needs TLS termination at proxy to inspect."),
     ("Streaming not supported:","Some gRPC streaming types may not be supported. Check Cilium version.")],
    ["Proto file unavailable for method parsing","gRPC-web different protocol (needs separate handling)","Reflection calls blocked (different methods)","LB stripping HTTP/2 headers","gRPC deadline exceeded before policy evaluation"],
    [("gRPC support version:","gRPC L7 added in Cilium 1.12+. Check <code>cilium version</code>."),
     ("HTTP/2 proxy:","gRPC uses same Envoy but needs HTTP/2 support."),
     ("Method discovery:","<code>grpcurl svc:50051 list</code> to see actual methods."),
     ("Service connection:","gRPC client must connect through service, not pod IP."),
     ("mTLS disabling inspection:","mTLS requires both client and server certs at proxy.")],
    "1. <code>grpcurl svc:50051 describe</code><br>2. <code>hubble observe --protocol gRPC</code><br>3. CNP: use <code>grpc:</code> key, not <code>http:</code><br>4. Enable HTTP/2 in proxy<br>5. Test without TLS first",
    "<strong>💡 Personal Advice:</strong> gRPC L7 is more niche than Kafka. For CCA: know grpc vs http syntax. For anihpj: use L3/L4 based on service accounts — simpler.",
    "<strong>🔍 What to Look At:</strong> grpc key (not http). Method: /Package.Service/Method. HTTP/2 required. Hubble shows gRPC protocol. TLS termination needed.")

add_issue("P10","ts-p10-detail","L7 Policy Performance Degradation","📋 CATEGORY 2: NETWORK POLICY — Issue P10","After L7 policies enabled, request latency +10-20ms. Pod CPU higher. Some requests timeout under load.",
    [("Envoy resource limits:","Too many L7 listeners consume CPU/memory. <code>kubectl top pods -n kube-system | grep envoy</code>."),
     ("Connection pool exhaustion:","Envoy pools to backends. Full pool = queuing. Increase pool size."),
     ("Too many L7 rules:","100+ rules = significant regex overhead. Consolidate."),
     ("TLS termination CPU:","Crypto per connection adds 1-5ms."),
     ("Proxy buffer too small:","Large headers/bodies overflow buffer. Increase proxy buffer.")],
    ["BPF redirect to proxy adds ~0.5ms","Hubble export competing for CPU","BPF policy check before redirect adds latency","Multiple proxies (ingress + sidecar) doubling","Proxy health check failures causing resets"],
    [("Start L3/L4 only:","New cluster — use L3/L4 until L7 needed. Each L7 rule adds latency."),
     ("Proxy resources low:","Default 128Mi/0.1 CPU may be too low. Increase: <code>--set proxy.resources.limits.cpu=1</code>."),
     ("Specific vs broad regex:","<code>/api/v1/users</code> faster than <code>/api/.*</code>."),
     ("Disable Hubble if unused:","Hubble capture adds overhead."),
     ("Proxy metrics:","Enable: <code>--set proxy.prometheus.enabled=true</code>.")],
    "1. <code>kubectl top pods -n kube-system -l app=envoy</code><br>2. <code>cilium status | grep Proxy</code><br>3. Reduce rules: consolidate regex<br>4. Increase proxy resources<br>5. Consider Ingress/Gateway API instead of per-pod proxy",
    "<strong>💡 Personal Advice:</strong> L7 proxy latency is the price of deep inspection. For anihpj: keep L7 rules minimal. 10ms may be acceptable for security but not real-time. Measure BEFORE and AFTER.",
    "<strong>🔍 What to Look At:</strong> Envoy CPU/memory. Listener count: <code>cilium-dbg bpf proxy list | wc -l</code>. Hubble latency shows proxy hop. Consolidate patterns.")

# P11-P13: Audit Mode
add_issue("P11","ts-p11-detail","Policy Audit Mode Shows No Logs","🔊 CATEGORY 2: NETWORK POLICY — Issue P11","CNP with policyAudit:true but Hubble shows no DROPPED flows. Audit mode seems not working.",
    [("Hubble filtering hides drops:","Use <code>hubble observe --verdict DROPPED</code> with NO other filters."),
     ("Policy not denying:","If policy would allow anyway, nothing to audit. Audit only logs WOULD-BE denies."),
     ("Hubble relay down:","<code>cilium status | grep Relay</code>. Relay must be connected."),
     ("Audit on wrong policy:","<code>policyAudit: true</code> must be on the specific policy, not a different one."),
     ("Event buffer full:","High traffic fills buffer. Increase <code>hubble-event-queue-size</code>.")],
    ["Audit only works with CNP, not Kubernetes NetworkPolicy","Hubble TLS expired preventing connection","Multiple Hubble instances (UI ≠ CLI)","Events to different peer","Kernel dropping BPF events under load"],
    [("Hubble not enabled:","Audit requires Hubble. <code>cilium config | grep enable-hubble</code> = true."),
     ("Syntax:","<code>policyAudit: true</code> at top level of CNP spec, not under rules."),
     ("No denies on new cluster:","If nothing denies, audit shows nothing. Create test deny."),
     ("Hubble observe flags:","Default shows FORWARDED only. Add <code>--verdict DROPPED</code>."),
     ("Relay not deployed:","<code>cilium hubble enable --relay</code>.")],
    "1. <code>hubble observe --verdict DROPPED -n anihpj</code><br>2. <code>kubectl get cnp -o yaml | grep policyAudit</code><br>3. Test: apply CNP denying port 9999<br>4. <code>curl svc:9999</code> — should appear DROPPED<br>5. <code>cilium status | grep Hubble</code>",
    "<strong>💡 Personal Advice:</strong> Audit mode is your safety net. Deploy in audit 24-48h before enforcing. For anihpj: audit lets you see what WOULD break without actually breaking production.",
    "<strong>🔍 What to Look At:</strong> Hubble shows 'DROPPED (Audit)' vs 'DROPPED (Policy)'. Use <code>-o json</code> for reason. Audit only logs DENIED flows, not ALLOWED.")

add_issue("P12","ts-p12-detail","Switching Audit to Enforce Breaks Traffic","🔊 CATEGORY 2: NETWORK POLICY — Issue P12","Policy in audit for days showing no drops. Switched to enforce — immediately broke production. False confidence from audit.",
    [("Audit only shows THAT policy:","Multiple policies. Audit on one doesn't show what OTHER policies deny. Union matters."),
     ("Hubble filters hid drops:","Your observe command may have filtered out some drops. Use unfiltered."),
     ("Race on switch:","Removing audit + reapply = brief gap where old policy removed, new not active."),
     ("DNS behavior differs:","Audit allows DNS so FQDNs resolve. Enforce blocks DNS so FQDNs can't resolve."),
     ("Policy edited between:","Different revision between audit and enforce. Rules changed.")],
    ["Sidecar/init container traffic not in Hubble (short-lived)","Health probes blocked but missed in audit window","Metrics scraping blocked (periodic, may miss)","CRD lag: some nodes still running old policy","Hubble sampling hiding some flows"],
    [("No test traffic:","New cluster with no traffic — audit shows nothing. Generate test traffic."),
     ("Audit too short:","24-48h minimum. Some traffic is daily/weekly (cronjobs, batches)."),
     ("Only checking ingress:","Policy has both directions. Audit applies to both."),
     ("UI vs CLI:","UI has time limits. CLI with <code>--since 72h</code> captures more."),
     ("Multiple ns not checked:","Policy in ns-A may audit fine, but ns-B policy also affects.")],
    "1. Before switch: <code>hubble observe --verdict DROPPED --since 72h</code> NO filters<br>2. <code>kubectl get cnp,ccnp -A</code> — ALL policies<br>3. Switch one at a time, wait 30min<br>4. Have rollback ready<br>5. Monitor: <code>watch hubble observe --verdict DROPPED</code>",
    "<strong>💡 Personal Advice:</strong> Audit is probability, not guarantee. Longer audit = more confidence but never 100%. For anihpj: switch during maintenance window with rollback plan.",
    "<strong>🔍 What to Look At:</strong> Unfiltered Hubble: NO flags on observe. Check ALL policies (cnp+ccnp). DNS behavior differs audit vs enforce. Switch one policy at a time.")

add_issue("P13","ts-p13-detail","Audit Mode Performance Impact","🔊 CATEGORY 2: NETWORK POLICY — Issue P13","Audit mode on many policies causes agent CPU spike and Hubble flow loss. 'event queue full, dropping events' in logs.",
    [("Event generation rate:","Every WOULD-BE denied packet = Hubble event. High traffic = millions/sec. Overwhelms buffer."),
     ("Buffer too small:","Default 4095 events. Under audit with high traffic, fills in ms. Increase to 65535."),
     ("Multiple audit policies:","5 policies = 5x events. Audit one at a time."),
     ("Relay bottleneck:","Relay aggregates from all agents. Undersized relay = backpressure."),
     ("perf ring buffer overflow:","Kernel-side BPF events overflow before reaching agent.")],
    ["TLS encryption overhead on event transmission","Agent Go GC from event allocation","Disk I/O for Hubble Timescape","Network bandwidth agent→relay","Prometheus cardinality from per-flow metrics"],
    [("Audit on default-deny:","NEVER audit default-deny on busy cluster — generates events for ALL traffic."),
     ("No rate limiting:","Hubble doesn't rate-limit. Traffic spike = event storm."),
     ("All policies in audit:","Audit one policy at a time, not all."),
     ("Relay not scaled:","Single relay for large cluster. Increase replicas/resources."),
     ("No retention:","Events accumulate. Set up consumer or Timescape.")],
    "1. Limit scope: audit specific ports/protocols<br>2. Increase buffer: <code>hubble-event-queue-size: 65535</code><br>3. Scale relay: more replicas/resources<br>4. <code>cilium-dbg bpf events list | wc -l</code><br>5. Flow sampling: capture 1/N flows",
    "<strong>💡 Personal Advice:</strong> Audit is for VALIDATION, not constant monitoring. Turn on, observe 24-48h, enforce. For anihpj: audit during low traffic with specific scope.",
    "<strong>🔍 What to Look At:</strong> Event queue depth. Agent CPU during audit. Audit scope: specific pods/ports. Relay CPU/memory. Sampling for high-traffic envs.")

# P14-P16: Host Firewall
add_issue("P14","ts-p14-detail","Host Firewall CCNP Blocks SSH to Nodes","🔥 CATEGORY 2: NETWORK POLICY — Issue P14","CCNP for host firewall applied. SSH to worker nodes blocked. Administrators locked out.",
    [("nodeSelector matches all:","<code>nodeSelector: {}</code> = ALL nodes. Use specific labels."),
     ("No SSH allow:","Must include: <code>fromEntities: [world] toPorts: [{ports: [{port: '22'}]}]</code>."),
     ("fromEntities not set:","Host uses fromEntities (world, cluster, host, remote-node, kube-apiserver)."),
     ("Control-plane affected:","CCNP on master nodes blocks kube-apiserver. Exclude control-plane."),
     ("Kubelet port 10250 blocked:","Kube-apiserver needs kubelet access. Blocking breaks node management.")],
    ["Node IP change causing CCNP to match different nodes","Cilium health ICMP blocked","CNI agent communication blocked","NodePort traffic blocked","Cloud metadata (169.254.169.254) blocked"],
    [("hostFirewall not enabled:","CCNP nodeSelector needs <code>hostFirewall.enabled=true</code> in Helm."),
     ("CCNP syntax:","nodeSelector not endpointSelector. fromEntities not fromEndpoints."),
     ("No baseline allows:","Start with SSH, kubelet, Cilium allows before denies."),
     ("Testing from wrong source:","Test from world (external), not cluster (internal). Different entities."),
     ("Node labels missing:","<code>kubectl label node worker-1 host-firewall=enabled</code>.")],
    "1. <code>kubectl get ccnp -o yaml</code> — verify nodeSelector<br>2. <code>cilium-dbg bpf policy get --host</code><br>3. Add SSH: fromEntities world port 22<br>4. Add kubelet: port 10250 from kube-apiserver<br>5. <code>hubble observe --from-entity world --to-port 22 --verdict DROPPED</code>",
    "<strong>💡 Personal Advice:</strong> Host firewall is powerful but dangerous. One wrong CCNP = lockout from ALL nodes. Test on single non-critical node first. For anihpj: skip host firewall unless you truly need host-level protection.",
    "<strong>🔍 What to Look At:</strong> nodeSelector (not endpointSelector). fromEntities: world, cluster, host, remote-node, kube-apiserver, ingress. SSH=22, kubelet=10250.")

add_issue("P15","ts-p15-detail","Host Firewall Not Enforcing on Specific Nodes","🔥 CATEGORY 2: NETWORK POLICY — Issue P15","CCNP with nodeSelector applied but only enforces on some nodes. Others matching same selector show no rules.",
    [("Labels missing on nodes:","<code>kubectl get nodes --show-labels</code>. Must match EXACTLY."),
     ("Agent version mismatch:","Host firewall needs Cilium 1.12+. Older agents ignore CCNP."),
     ("hostFirewall not enabled:","Must be enabled cluster-wide AND node has labels. Check ConfigMap."),
     ("CCNP not synced:","<code>cilium policy wait &lt;rev&gt;</code>. Some agents lag."),
     ("matchExpressions:","Complex selectors may not evaluate correctly. Use simple matchLabels.")],
    ["Agent restart cleared in-memory policy","CRD watch broken for specific agent","Node renamed — selector misses it","Tainted nodes (doesn't affect CCNP but may affect agent)","Custom agent config overriding host firewall"],
    [("Not in initial install:","Check <code>helm get values cilium | grep hostFirewall</code>."),
     ("Labels AFTER CCNP:","Add labels before CCNP. If CCNP first, selects nothing."),
     ("CCNP in namespace:","CCNP is cluster-scoped. Don't use -n flag."),
     ("Testing wrong node:","SSH to specific node: <code>cilium-dbg bpf policy get --host</code>."),
     ("Masters excluded:","Some setups skip Cilium on masters. Check agent presence.")],
    "1. <code>kubectl get nodes --show-labels | grep &lt;label&gt;</code><br>2. Per-node: <code>cilium-dbg bpf policy get --host</code><br>3. <code>kubectl describe ccnp &lt;name&gt;</code><br>4. Check agent versions per node<br>5. Restart agent on non-enforcing nodes",
    "<strong>💡 Personal Advice:</strong> Label issues = #1 host firewall inconsistency. For anihpj: use single label <code>cilium-host-fw=true</code> on ALL workers for simple nodeSelector.",
    "<strong>🔍 What to Look At:</strong> EXACT label match per node. Per-node BPF check. Agent >= v1.12. CCNP cluster-scoped. hostFirewall.enabled=true in ConfigMap.")

add_issue("P16","ts-p16-detail","Host Firewall Blocks Inter-Node Cilium Communication","🔥 CATEGORY 2: NETWORK POLICY — Issue P16","After host firewall CCNP, Cilium agents can't communicate. Health status fails. Cross-node broken.",
    [("Tunnel port blocked:","UDP 8472 (VXLAN) or 6081 (Geneve) must be open between ALL nodes."),
     ("ICMP blocked:","Health checks use ICMP. Must allow from remote-node entity."),
     ("WireGuard port blocked:","UDP 51871 for encryption. Open between all nodes."),
     ("Hubble peer blocked:","Port 4244 for Hubble relay. Blocking breaks flow aggregation."),
     ("etcd blocked:","TCP 2379 to external etcd if used.")],
    ["NodePort inter-node forwarding blocked","Agent API port 9090 blocked","SNAT/masquerade traffic blocked","DNS for node hostnames blocked","ClusterIP traffic blocked at host level"],
    [("No remote-node rules:","Must include <code>fromEntities: [remote-node]</code> for ingress."),
     ("Default-deny host:","Empty ingress/egress = block ALL inter-node. Create allows first."),
     ("Tunnel protocol:","Check <code>cilium config | grep tunnel</code>. VXLAN=8472, Geneve=6081."),
     ("ALL node pairs:","Allow traffic between EVERY pair of nodes."),
     ("Health CIDR:","Health endpoints use separate CIDR. Add fromCIDR for health-ipv4-cidr.")],
    "1. <code>cilium-health status</code><br>2. <code>hubble observe --from-entity remote-node --verdict DROPPED</code><br>3. Add: fromEntities [remote-node, cluster, health]<br>4. Add tunnel port: UDP 8472/6081<br>5. Add ICMP and WireGuard ports",
    "<strong>💡 Personal Advice:</strong> Inter-node rules are most error-prone. Miss one port = broken cluster. For anihpj: create baseline CCNP allowing ALL inter-node Cilium traffic first, then add restrictions.",
    "<strong>🔍 What to Look At:</strong> Must allow: UDP 8472/6081, UDP 51871, TCP 4244, ICMP. fromEntities [remote-node] essential. Check cilium-health after every CCNP change.")

# P17-P18: CIDRGroup
add_issue("P17","ts-p17-detail","CiliumCIDRGroup Not Resolving to IPs","🌐 CATEGORY 2: NETWORK POLICY — Issue P17","CIDRGroup created with external CIDRs but policies referencing it don't work. Trace shows CIDRGroup as empty.",
    [("Invalid CIDR format:","Must be valid: <code>10.0.0.0/8</code>. Check <code>kubectl describe cidrgroup</code>."),
     ("Wrong reference field:","Use <code>fromCIDRSet: [{cidrGroup: 'name'}]</code>, NOT <code>fromCIDR: [{cidrGroup: 'name'}]</code>."),
     ("Namespace mismatch:","CIDRGroup namespaced. CNP in 'anihpj' can only reference CIDRGroups in 'anihpj'."),
     ("CRD missing:","Check <code>kubectl get crd ciliumcidrgroups.cilium.io</code>."),
     ("Agent watch broken:","Agent not picking up CIDRGroup changes. Restart agent.")],
    ["Empty CIDR list (created but no IPs)","DNS-based group not resolving","Name changed between CRD and policy reference","Multiple policies referencing same group slowing updates","IPv6 CIDRs in IPv4-only cluster"],
    [("CIDRGroup vs fromCIDR:","fromCIDR for inline CIDRs. CIDRGroup for named, reusable sets."),
     ("Namespacing:","Must be same namespace as referencing CNP, or use CCNP."),
     ("Empty group:","Create CIDRGroup with actual CIDRs before referencing."),
     ("CRD install:","Should be installed with Cilium. Check if missing."),
     ("DNS-based groups:","FQDNs resolve to CIDRs. DNS must be resolvable from cluster.")],
    "1. <code>kubectl get cidrgroup &lt;name&gt; -o yaml</code><br>2. <code>kubectl get cnp &lt;name&gt; -o yaml | grep cidrGroup</code><br>3. <code>cilium policy trace</code><br>4. Verify same namespace<br>5. Delete and recreate CIDRGroup to force refresh",
    "<strong>💡 Personal Advice:</strong> CIDRGroup is underused. Define IPs once, reference everywhere. For anihpj: create CIDRGroups for office VPN, AWS VPC, and external API IPs.",
    "<strong>🔍 What to Look At:</strong> Valid CIDR format. fromCIDRSet with cidrGroup key. Same namespace. CRD must exist. DNS-based groups resolve asynchronously.")

add_issue("P18","ts-p18-detail","CIDRGroup DNS Resolution Delayed","🌐 CATEGORY 2: NETWORK POLICY — Issue P18","CIDRGroup with FQDN entries takes minutes to resolve. During delay, policy blocks legitimate traffic.",
    [("DNS TTL too long:","CIDRGroup respects DNS TTL. TTL 3600s = 1hr cache. IP changes during TTL = blocked."),
     ("DNS rate limiting:","Multiple CIDRGroups resolving simultaneously may hit limits."),
     ("CoreDNS unreachable from agent:","Agent uses host network for DNS. Host DNS misconfig = resolution fails."),
     ("FQDN format wrong:","Use plain domain: <code>dns: api.example.com</code>. No protocol, path, port."),
     ("Cache not refreshed:","FQDN changes not picked up until agent restart or cache expiry.")],
    ["Negative DNS caching (NXDOMAIN cached)","IPv6 responses when IPv4-only","DNS-over-TLS/HTTPS not supported by agent resolver","Split-horizon DNS (different inside vs outside)","Stale FQDN entry causing repeated resolution failures"],
    [("CoreDNS required:","Agent uses cluster DNS. Ensure CoreDNS running on all nodes."),
     ("FQDN format:","Plain domain only: <code>dns: github.com</code>. No https://, no path."),
     ("Initial delay:","First resolution 5-30s. Subsequent use cache. Plan for delay."),
     ("Test from node:","<code>nslookup api.github.com</code> from worker node first."),
     ("Mixed static+DNS:","Static resolve instantly. DNS async. Policy partially active during resolution.")],
    "1. <code>kubectl describe cidrgroup &lt;name&gt;</code> — check status<br>2. <code>nslookup &lt;fqdn&gt;</code> from worker node<br>3. Check agent logs for cidrgroup<br>4. Use short TTL DNS provider (60s)<br>5. Use static CIDRs for critical services",
    "<strong>💡 Personal Advice:</strong> DNS-based CIDRGroup is convenient but unreliable for critical paths. For anihpj: static CIDRs for RDS/S3 IP ranges, DNS-based only for non-critical APIs.",
    "<strong>🔍 What to Look At:</strong> Plain FQDN only. DNS TTL = cache duration. Agent logs show resolution errors. Status shows resolved IPs. Static CIDRs resolve instantly.")

# Generate HTML
section_headers = {
    "ts-p1": "📦 P1 — P5: CNP Not Enforcing",
    "ts-p2": "📋 P6 — P10: L7 Policy Issues",
    "ts-p3": "🔊 P11 — P13: Policy Audit Mode",
    "ts-p4": "🔥 P14 — P16: Host Firewall Problems",
    "ts-p5": "🌐 P17 — P18: CiliumCIDRGroup Issues",
}

# Group issues by section
sections = {
    "ts-p1": ["P1","P2","P3","P4","P5"],
    "ts-p2": ["P6","P7","P8","P9","P10"],
    "ts-p3": ["P11","P12","P13"],
    "ts-p4": ["P14","P15","P16"],
    "ts-p5": ["P17","P18"],
}

html = ''
for sec_id, sec_pids in sections.items():
    html += f'''    <div class="ts-section-header" id="{sec_id}">
        <h3>{section_headers[sec_id]}</h3>
    </div>
'''
    for pid in sec_pids:
        issue = next(i for i in cat2 if i['pid'] == pid)
        html += f'''    <div class="ts-issue" id="{issue['pid_detail']}">
        <div class="ts-issue-header">
            <div class="ts-issue-num">{issue['pid']}</div>
            <div class="ts-issue-header-content">
                <div class="ts-category">{issue['cat']}</div>
                <div class="ts-title">{issue['title']}</div>
                <p class="ts-symptom"><strong>🔍 Symptom:</strong> {issue['symptom']}</p>
            </div>
        </div>
        <div class="ts-causes-grid">
            <div class="cause-card most-likely">
                <div class="cause-card-header">
                    <span class="cause-icon">🔴</span>
                    <span class="cause-label">5 Most Likely Causes</span>
                </div>
                <ol>
'''
        for label, desc in issue['ml']:
            html += f'            <li><span class="cause-likely">{label}</span> {desc}</li>\n'
        html += '''                </ol>
            </div>
            <div class="cause-card less-likely">
                <div class="cause-card-header">
                    <span class="cause-icon">🟡</span>
                    <span class="cause-label">5 Less Likely Causes</span>
                </div>
                <ol>
'''
        for item_text in issue['ll']:
            html += f'            <li><span class="cause-less-likely">{item_text}</span></li>\n'
        html += '''                </ol>
            </div>
            <div class="cause-card new-cluster">
                <div class="cause-card-header">
                    <span class="cause-icon">🟣</span>
                    <span class="cause-label">5 New Cluster Causes</span>
                </div>
                <ol>
'''
        for label, desc in issue['nc']:
            html += f'            <li><span class="cause-new-cluster">{label}</span> {desc}</li>\n'
        html += f'''                </ol>
            </div>
        </div>
        <div class="ts-lookat">{issue['la']}</div>
        <div class="ts-solution"><strong>🔧 How to Solve:</strong>
            <p>{issue['sol']}</p>
        </div>
        <div class="ts-advice">{issue['adv']}</div>
        <div class="ts-footer-spacer"></div>
    </div>
'''

# Inject into main file
with open('cilium-test-prep.html', 'r', encoding='utf-8') as f:
    c = f.read()

anchor = 'id="decision-trees"'
idx = c.find(anchor)
section_start = c.rfind('<!--', 0, idx)  # comment before decision-trees section

cat2_header = '''
    <!-- ═══════════════════════════════════════════════════════════
         CATEGORY 2: NETWORK POLICY (18 Issues: P1-P18)
         ═══════════════════════════════════════════════════════════ -->

    <section class="chapter-section" id="ts-cat2">
        <h2><span>🛡️ Category 2: Network Policy</span><span class="chapter-badge">P1-P18</span></h2>
        <div class="chapter-intro">
            <p>18 troubleshooting issues covering CiliumNetworkPolicy enforcement, L7 HTTP/DNS/Kafka/gRPC rules, policy audit mode, host firewall CCNP, and CiliumCIDRGroup management.</p>
        </div>
    </section>

'''

c = c[:section_start] + cat2_header + html + '\n' + c[section_start:]

with open('cilium-test-prep.html', 'w', encoding='utf-8') as f:
    f.write(c)

sz = round(os.path.getsize('cilium-test-prep.html') / 1024, 1)
print(f'Done Category 2. Size: {sz} KB')
print(f'</main>: {c.count("</main>")}')
print(f'ts-issue-header (total pairs): {c.count("ts-issue-header")}')
print(f'Cat 2 issues: {len(cat2)}')
