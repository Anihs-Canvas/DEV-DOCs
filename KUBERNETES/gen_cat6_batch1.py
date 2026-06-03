#!/usr/bin/env python3
"""Category 6: Cluster Mesh — Batch 1: S75-S77"""

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

# ======================== S75 ========================
s75 = sc(75,
    "Set Up Cluster Mesh Between anihpj-us and anihpj-eu",
    "You need to connect two anihpj clusters (us-east and eu-west) via Cilium Cluster Mesh. After running <code>cilium clustermesh connect</code>, the <strong>clusters fail to establish a connection</strong>. Hubble shows no cross-cluster flows. Your job: set up Cluster Mesh correctly and verify cross-cluster service discovery.",
    r"""<span class="token comment"># Cluster 1: anihpj-us (context: us-east)</span>
kubectl config use-context us-east
cilium install --cluster-name anihpj-us --cluster-id 1

<span class="token comment"># Cluster 2: anihpj-eu (context: eu-west)</span>
kubectl config use-context eu-west
cilium install --cluster-name anihpj-eu --cluster-id 2

<span class="token comment"># Deploy anihpj in both clusters</span>
for ctx in us-east eu-west; do
  kubectl config use-context $ctx
  kubectl create namespace anihpj
  kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
  kubectl expose deployment web -n anihpj --port=80 --name=web-service
done

<span class="token comment"># ❌ BUG: Cluster Mesh connection fails</span>
cilium clustermesh connect --context us-east --destination-context eu-west
<span class="token comment"># Error: Unable to establish connection — TLS handshake failed</span>""",
    [
        ("pass", "<strong>1.</strong> Both clusters running Cilium: <code>cilium status</code> → OK on both clusters ✅"),
        ("pass", "<strong>2.</strong> Unique cluster names/IDs: <code>cilium config | grep cluster</code> → cluster-id=1 (us), cluster-id=2 (eu) ✅"),
        ("fail", "<strong>3.</strong> Cluster Mesh connect fails: <code>cilium clustermesh connect</code> → <strong>TLS handshake failed — connection refused</strong> ❌"),
        ("fail", "<strong>4.</strong> Cross-cluster pod ping: <code>kubectl exec -n anihpj web-us-xxx -- ping web-eu-service.anihpj.svc</code> → <strong>unknown host</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble shows no cross-cluster flows: <code>hubble observe --cluster anihpj-eu</code> → <strong>no flows from remote cluster</strong> ❌"),
    ],
    [
        (1, "Check Cluster Mesh status:", "cilium clustermesh status --context us-east", "discovery", "Cluster Mesh: disconnected — clusters cannot see each other; the clustermesh-apiserver service may not be accessible between clusters"),
        (2, "Verify clustermesh-apiserver is running:", "kubectl get svc -n kube-system clustermesh-apiserver", "discovery", "Service exists as ClusterIP only — remote clusters cannot reach it; needs to be exposed via LoadBalancer or NodePort for cross-cluster access"),
        (3, "Check TLS certificates for cross-cluster auth:", "kubectl get secret -n kube-system cilium-ca -o yaml | grep -c cert", "discovery", "Each cluster has its own CA — but the clusters don't trust each other's CA certificates; mutual TLS requires shared CA or cross-signed certificates"),
        (4, "Verify network connectivity between clusters:", "kubectl exec -n kube-system ds/cilium -- curl -k https://<remote-cluster-ip>:2379/version", "discovery", "Connection timeout — firewall or network policy is blocking inter-cluster traffic on the etcd port (2379)"),
        (5, "Root cause identified:", "Cluster Mesh requires exposed apiserver, shared CA trust, and open network paths between clusters", "root-cause", "Three requirements for Cluster Mesh: 1) clustermesh-apiserver must be accessible from the remote cluster (LoadBalancer/NodePort, not just ClusterIP), 2) Both clusters must share the same CA certificate for mutual TLS authentication, and 3) Network connectivity must exist between cluster nodes (firewall rules allowing ports 2379 and 4240)"),
    ],
    r"""<span class="token comment"># Fix 1: Export CA from us-east and import into eu-west</span>
kubectl config use-context us-east
kubectl get secret -n kube-system cilium-ca -o yaml > us-ca.yaml
<span class="token comment"># Edit: change namespace to kube-system, rename to cilium-ca</span>
kubectl config use-context eu-west
kubectl apply -f us-ca.yaml

<span class="token comment"># Fix 2: Expose clustermesh-apiserver via LoadBalancer</span>
kubectl patch svc -n kube-system clustermesh-apiserver \
  -p '{"spec":{"type":"LoadBalancer"}}'
<span class="token comment"># Do this on BOTH clusters</span>

<span class="token comment"># Fix 3: Connect Cluster Mesh with shared CA</span>
cilium clustermesh connect \
  --context us-east \
  --destination-context eu-west

<span class="token comment"># Fix 4: Verify connection</span>
cilium clustermesh status --context us-east""",
    "Cross-Cluster Service Discovery",
    "Cluster Mesh Connected Between anihpj-us and anihpj-eu",
    'Cluster Mesh is established. <code>cilium clustermesh status</code> shows <strong>connected</strong> with both clusters listed. <code>kubectl exec -n anihpj web-us-xxx -- curl web-service.anihpj.svc</code> resolves to the global service across both clusters. Hubble shows cross-cluster flows with remote cluster labels. anihpj services are discoverable from either cluster.',
    ["cilium clustermesh connect → TLS handshake failed", "clustermesh-apiserver is ClusterIP only", "Different CAs per cluster → no mutual TLS trust", "Share CA → expose LoadBalancer → connect", "Cross-cluster service resolution works"],
    "Cluster Mesh requires three prerequisites: 1) <strong>Shared CA certificate</strong> — both clusters must trust the same CA for mutual TLS between clustermesh-apiservers, 2) <strong>Exposed apiserver</strong> — clustermesh-apiserver must be reachable from the remote cluster (LoadBalancer, NodePort, or routable IP), and 3) <strong>Network path</strong> — firewalls must allow etcd (2379) and health-check (4240) ports between clusters. Without any one of these, the mesh cannot form.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium clustermesh connect --context us-east --destination-context eu-west\n<span class="output">Error: Unable to establish connection to remote cluster\n  rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing: dial tcp 10.0.1.50:2379: connect: connection refused"\n[!] Cluster Mesh connection FAILED</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n kube-system clustermesh-apiserver\n<span class="output">NAME                     TYPE        CLUSTER-IP     PORT(S)    AGE\nclustermesh-apiserver    ClusterIP   10.96.50.100   2379/TCP   1h    ← Not externally accessible!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium clustermesh status --context us-east\n<span class="output">Cluster Mesh: connected\n  anihpj-us (cluster-id: 1): OK\n  anihpj-eu (cluster-id: 2): OK    ✅ Both clusters connected!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj web-us-xxx -- curl -s web-service.anihpj.svc.global\n<span class="output">&lt;html&gt;...nginx...&lt;/html&gt;    ✅ Cross-cluster service reachable!</span></div>',
    ]
)

# ======================== S76 ========================
s76 = sc(76,
    "Debug Cluster Mesh Not Connecting — TLS Certificate Mismatch",
    "You established Cluster Mesh but <strong>periodically the connection drops</strong>. Cilium agents log TLS errors. The mesh works initially but breaks after certificate rotation. Your job: diagnose the TLS certificate mismatch and fix the Cluster Mesh authentication.",
    r"""<span class="token comment"># Cluster Mesh was working, now disconnected</span>
cilium clustermesh status --context us-east
<span class="token comment"># anihpj-us: OK, anihpj-eu: TLS_ERROR</span>

<span class="token comment"># Deploy anihpj for testing</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2

<span class="token comment"># ❌ BUG: Cross-cluster connections failing with TLS errors</span>
kubectl logs -n kube-system ds/cilium | grep -i tls
<span class="token comment"># "x509: certificate has expired or is not yet valid"</span>""",
    [
        ("pass", "<strong>1.</strong> Both clusters have Cilium running: <code>cilium status</code> → OK ✅"),
        ("pass", "<strong>2.</strong> Cluster Mesh was previously working: <code>cilium clustermesh status</code> → previously connected ✅"),
        ("fail", "<strong>3.</strong> Mesh now shows TLS error: <code>cilium clustermesh status</code> → <strong>anihpj-eu: TLS_ERROR — certificate validation failed</strong> ❌"),
        ("fail", "<strong>4.</strong> Agent logs show expiry: <code>kubectl logs -n kube-system ds/cilium | grep x509</code> → <strong>certificate has expired</strong> ❌"),
        ("fail", "<strong>5.</strong> Cross-cluster services unreachable: <code>kubectl exec -n anihpj web-us-xxx -- curl web-service.anihpj.svc.global</code> → <strong>connection refused</strong> ❌"),
    ],
    [
        (1, "Check Cilium CA certificate expiry:", "kubectl get secret -n kube-system cilium-ca -o jsonpath='{.data.ca\\.crt}' | base64 -d | openssl x509 -noout -dates", "discovery", "CA certificate expired 2 days ago — Cilium's internal CA has a default 1-year validity; after expiry, all TLS connections between clusters fail"),
        (2, "Check clustermesh-apiserver certificate:", "kubectl get secret -n kube-system clustermesh-apiserver-server-cert -o jsonpath='{.data.tls\\.crt}' | base64 -d | openssl x509 -noout -dates", "discovery", "Server certificate also expired — tied to the same CA; cert-manager or manual rotation is needed"),
        (3, "Verify both clusters use the same CA:", "diff <(kubectl get secret -n kube-system cilium-ca -o jsonpath='{.data.ca\\.crt}' --context us-east) <(kubectl get secret -n kube-system cilium-ca -o jsonpath='{.data.ca\\.crt}' --context eu-west)", "discovery", "CA certificates differ — one cluster rotated its CA but the other still has the old CA; the clusters no longer trust each other"),
        (4, "Check if cert-manager is managing Cilium certs:", "kubectl get certificate -n kube-system | grep cilium", "discovery", "No Certificate resources — Cilium's built-in CA auto-generates certs but does NOT auto-renew them; manual rotation or cert-manager integration is required for production"),
        (5, "Root cause identified:", "Cilium internal CA certificates expire after 1 year with no auto-renewal", "root-cause", "Cilium generates a self-signed CA during installation. All Cluster Mesh TLS certs (clustermesh-apiserver, remote, admin) are signed by this CA with a 1-year validity. When the CA or any certificate expires, all cross-cluster TLS connections fail. Production clusters need either cert-manager integration or manual certificate rotation before expiry"),
    ],
    r"""<span class="token comment"># Fix 1: Rotate CA on both clusters with matching cert</span>
<span class="token comment"># Generate new CA (do once, share between clusters)</span>
openssl req -new -x509 -days 3650 -nodes \
  -out ca.crt -keyout ca.key \
  -subj "/CN=cilium-ca"

<span class="token comment"># Update CA secret on BOTH clusters</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx delete secret -n kube-system cilium-ca
  kubectl --context $ctx create secret generic cilium-ca \
    -n kube-system --from-file=ca.crt --from-file=ca.key
done

<span class="token comment"># Fix 2: Restart Cilium components to pick up new CA</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx rollout restart ds/cilium -n kube-system
  kubectl --context $ctx rollout restart deploy/clustermesh-apiserver -n kube-system
done

<span class="token comment"># Fix 3: Re-establish Cluster Mesh</span>
cilium clustermesh connect --context us-east --destination-context eu-west""",
    "Cluster Mesh Reconnected",
    "TLS Certificates Rotated and Mesh Restored",
    'Both clusters now trust the renewed CA certificate (valid for 10 years). <code>cilium clustermesh status</code> shows both clusters <strong>connected with OK status</strong>. Cross-cluster service resolution works. Agent logs show successful TLS handshakes. The shared CA ensures both clusters trust each other for mutual TLS.',
    ["Mesh was working → now TLS_ERROR", "Check CA cert → expired 2 days ago", "Cilium CA has 1-year validity, no auto-renew", "Generate new shared CA → update both clusters", "Restart agents → Mesh reconnects"],
    "Cilium's internal CA auto-generates during install but <strong>never auto-renews</strong>. The CA and all derived certificates (clustermesh-apiserver, remote, admin) share a 1-year lifespan. For production: either integrate <strong>cert-manager</strong> to auto-renew, or set up monitoring to alert 30 days before expiry. When rotating, always share the SAME CA between both clusters — different CAs break mutual TLS trust.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium clustermesh status --context us-east\n<span class="output">Cluster Mesh: connected (1/2)\n  anihpj-us (cluster-id: 1): OK\n  anihpj-eu (cluster-id: 2): TLS_ERROR — x509: certificate has expired    ❌</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get secret -n kube-system cilium-ca -o jsonpath="{.data.ca\\.crt}" | base64 -d | openssl x509 -noout -dates\n<span class="output">notBefore=Jun  3 2025 12:00:00 GMT\nnotAfter=Jun  3 2026 12:00:00 GMT    ← Expired 2 days ago!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get secret -n kube-system cilium-ca -o jsonpath="{.data.ca\\.crt}" | base64 -d | openssl x509 -noout -dates\n<span class="output">notBefore=Jun  3 2026 12:00:00 GMT\nnotAfter=Jun  3 2036 12:00:00 GMT    ✅ 10-year validity!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium clustermesh status --context us-east\n<span class="output">Cluster Mesh: connected (2/2)\n  anihpj-us (cluster-id: 1): OK\n  anihpj-eu (cluster-id: 2): OK    ✅ TLS restored!</span></div>',
    ]
)

# ======================== S77 ========================
s77 = sc(77,
    "Fix Global Service Not Resolving Across Clusters",
    "Cluster Mesh is connected, but <strong>anihpj services are not discoverable across clusters</strong>. <code>web-service.anihpj.svc.global</code> returns NXDOMAIN. Pods in us-east cannot reach services in eu-west. Your job: enable global service discovery and fix cross-cluster DNS resolution.",
    r"""<span class="token comment"># Cluster Mesh connected, but global services failing</span>
cilium clustermesh status --context us-east
<span class="token comment"># Both clusters: OK</span>

<span class="token comment"># Deploy anihpj in both clusters</span>
kubectl --context us-east create namespace anihpj
kubectl --context us-east create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl --context us-east expose deployment web -n anihpj --port=80 --name=web-service

kubectl --context eu-west create namespace anihpj
kubectl --context eu-west create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl --context eu-west expose deployment web -n anihpj --port=80 --name=web-service

<span class="token comment"># ❌ BUG: Global service not resolving</span>
kubectl --context us-east exec -n anihpj web-xxx -- nslookup web-service.anihpj.svc.global
<span class="token comment"># server can't find web-service.anihpj.svc.global: NXDOMAIN</span>""",
    [
        ("pass", "<strong>1.</strong> Cluster Mesh connected: <code>cilium clustermesh status</code> → both clusters OK ✅"),
        ("pass", "<strong>2.</strong> Local services resolve: <code>nslookup web-service.anihpj.svc.cluster.local</code> → resolves locally ✅"),
        ("fail", "<strong>3.</strong> Global service NXDOMAIN: <code>nslookup web-service.anihpj.svc.global</code> → <strong>NXDOMAIN — no global record</strong> ❌"),
        ("fail", "<strong>4.</strong> Cross-cluster curl fails: <code>curl web-service.anihpj.svc.global</code> → <strong>Could not resolve host</strong> ❌"),
        ("fail", "<strong>5.</strong> No global services listed: <code>cilium service list | grep global</code> → <strong>empty</strong> ❌"),
    ],
    [
        (1, "Check if the service is annotated as global:", "kubectl get svc -n anihpj web-service -o yaml | grep -i global", "discovery", "No global annotation — services are local by default; must add io.cilium/global-service: \"true\" annotation to expose across clusters"),
        (2, "Verify service is annotated on BOTH clusters:", "for ctx in us-east eu-west; do kubectl --context $ctx get svc -n anihpj web-service -o yaml | grep io.cilium/global-service; done", "discovery", "Neither cluster has the annotation — both need io.cilium/global-service: \"true\" for cross-cluster discovery"),
        (3, "Check Cilium global service list:", "cilium service list | grep -A5 global", "discovery", "No global services registered — the annotation triggers Cilium to register the service in the global service registry shared via Cluster Mesh"),
        (4, "Verify shared service identity across clusters:", "kubectl --context us-east get cep -n anihpj -o yaml | grep -A3 identity && kubectl --context eu-west get cep -n anihpj -o yaml | grep -A3 identity", "discovery", "Pods in different clusters have different identity IDs — global services use identity-based backend selection; identities must be consistent"),
        (5, "Root cause identified:", "Services are not annotated as global — Cluster Mesh does not auto-export services", "root-cause", "Cluster Mesh connects clusters but does NOT automatically make services global. Each Service must be explicitly annotated with io.cilium/global-service: \"true\" on ALL clusters that should share it. Without this annotation, services remain local to their cluster and .svc.global DNS resolution fails with NXDOMAIN"),
    ],
    r"""<span class="token comment"># Fix 1: Annotate services as global on BOTH clusters</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx annotate svc -n anihpj web-service \
    io.cilium/global-service=true \
    io.cilium/shared-service=true --overwrite
done

<span class="token comment"># Fix 2: Verify global service appears</span>
sleep 10  <span class="token comment"># Wait for Cluster Mesh to sync</span>
cilium service list | grep global

<span class="token comment"># Fix 3: Test cross-cluster resolution</span>
kubectl --context us-east exec -n anihpj deploy/web -- nslookup web-service.anihpj.svc.global

<span class="token comment"># Fix 4: Test cross-cluster connectivity</span>
kubectl --context us-east exec -n anihpj deploy/web -- curl -s http://web-service.anihpj.svc.global""",
    "Global Service Resolution",
    "Cross-Cluster Service Discovery Working",
    '<code>web-service.anihpj.svc.global</code> resolves to backend pods in <strong>both clusters</strong>. <code>cilium service list</code> shows the service as GLOBAL with backends from us-east AND eu-west. Requests are load-balanced across all backend pods regardless of which cluster they reside in.',
    ["Cluster Mesh connected but .svc.global NXDOMAIN", "Check annotation → no io.cilium/global-service", "Services are local by default", "Annotate both clusters → service registered as global", ".svc.global resolves → cross-cluster LB works"],
    "Cluster Mesh provides the infrastructure for cross-cluster connectivity, but <strong>global services are opt-in</strong>. Each Service needs <code>io.cilium/global-service: \"true\"</code> annotation on ALL participating clusters. Use <code>io.cilium/shared-service: \"true\"</code> for services that exist in multiple clusters (shared identity). DNS resolution via <code>.svc.global</code> suffix is handled by Cilium's internal DNS proxy, not CoreDNS.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context us-east exec -n anihpj deploy/web -- nslookup web-service.anihpj.svc.global\n<span class="output">Server:    10.96.0.10\nAddress:   10.96.0.10#53\n** server can\'t find web-service.anihpj.svc.global: NXDOMAIN    ← Not resolving!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get svc -n anihpj web-service -o yaml | grep -E "annotations|global"\n<span class="output">  annotations:\n    kubectl.kubernetes.io/last-applied-configuration: ...\n(no io.cilium/global-service annotation)    ← Missing!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context us-east exec -n anihpj deploy/web -- nslookup web-service.anihpj.svc.global\n<span class="output">Name:   web-service.anihpj.svc.global\nAddress: 10.0.1.10\nAddress: 10.0.1.11\nAddress: 10.1.2.10\nAddress: 10.1.2.11    ✅ Backends from BOTH clusters!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium service list | grep web-service\n<span class="output">GLOBAL   anihpj/web-service    ClusterIP 10.96.50.200   4 backends (us-east:2, eu-west:2)    ✅</span></div>',
    ]
)

# ====== Assemble ======
all_scenarios = s75 + '\n\n' + s76 + '\n\n' + s77

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 1 (S75-S77) inserted!")
else:
    print("ERROR: appendices marker not found!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File size: {len(html.encode('utf-8'))} bytes")
