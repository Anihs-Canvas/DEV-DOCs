#!/usr/bin/env python3
"""Category 6: Cluster Mesh — Batch 2: S78-S80"""

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

# S78
s78 = sc(78,
    "Debug Cross-Cluster Pod-to-Pod Connectivity Failure",
    "Cluster Mesh is connected, but <strong>pods in us-east cannot ping pods in eu-west directly</strong>. Global services work, but direct pod-to-pod IP communication across clusters fails. Your job: debug why cross-cluster pod IP routing is broken.",
    r"""<span class="token comment"># Cluster Mesh connected, global services work</span>
cilium clustermesh status
<span class="token comment"># Both clusters: OK</span>

<span class="token comment"># Deploy pods in both clusters</span>
kubectl --context us-east create namespace anihpj
kubectl --context us-east run debug-us -n anihpj --image=nginx:alpine
kubectl --context eu-west create namespace anihpj
kubectl --context eu-west run debug-eu -n anihpj --image=nginx:alpine

<span class="token comment"># Get pod IPs</span>
US_IP=$(kubectl --context us-east get pod debug-us -n anihpj -o jsonpath='{.status.podIP}')
EU_IP=$(kubectl --context eu-west get pod debug-eu -n anihpj -o jsonpath='{.status.podIP}')

<span class="token comment"># ❌ BUG: Direct pod-to-pod across clusters fails</span>
kubectl --context us-east exec -n anihpj debug-us -- ping -c3 $EU_IP
<span class="token comment"># 100% packet loss — no route to host</span>""",
    [
        ("pass", "<strong>1.</strong> Cluster Mesh connected: <code>cilium clustermesh status</code> → both OK ✅"),
        ("pass", "<strong>2.</strong> Local pod-to-pod works: <code>ping <local-pod-IP></code> → success within same cluster ✅"),
        ("fail", "<strong>3.</strong> Cross-cluster pod ping fails: <code>ping <remote-pod-IP></code> → <strong>100% packet loss, no route to host</strong> ❌"),
        ("fail", "<strong>4.</strong> No cross-cluster routes: <code>ip route | grep <remote-pod-CIDR></code> → <strong>no route to remote pod CIDR</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble shows DROPPED: <code>hubble observe --from-pod anihpj/debug-us --to-ip $EU_IP</code> → <strong>DROPPED — no tunnel to remote cluster</strong> ❌"),
    ],
    [
        (1, "Check if tunnel is established between clusters:", "kubectl exec -n kube-system ds/cilium -- cilium bpf tunnel list | grep <remote-cluster>", "discovery", "No tunnel entries for remote cluster — Cilium uses VXLAN or Geneve tunnels between clusters; if the tunnel mesh is not established, pod IPs are not routable"),
        (2, "Verify pod CIDR routing between clusters:", "ip route show | grep <remote-pod-cidr>", "discovery", "No route to remote pod CIDR — Cilium should install routes to remote cluster pod CIDRs via the tunnel interface"),
        (3, "Check CiliumNode resources for remote cluster:", "kubectl get ciliumnode -l io.cilium/cluster=<remote-cluster>", "discovery", "No CiliumNode resources from remote cluster — Cluster Mesh syncs CiliumNode CRDs between clusters; if they're missing, the local cluster doesn't know about remote node IPs and pod CIDRs"),
        (4, "Verify etcd or CRD sync is working:", "etcdctl get --prefix cilium/state/nodes/v2/", "discovery", "Remote cluster node entries not synced — the Cluster Mesh etcd sync may be incomplete or failing due to network issues"),
        (5, "Root cause identified:", "Cross-cluster pod IP routing requires tunnel mesh and route propagation via Cluster Mesh etcd", "root-cause", "Direct pod-to-pod communication across clusters requires: 1) Tunnel mesh between all nodes in both clusters (VXLAN/Geneve), 2) Route propagation via shared etcd (each cluster publishes its pod CIDRs), and 3) No firewall blocking the tunnel port (8472/UDP for VXLAN) between cluster nodes. If any of these is missing, cross-cluster pod IPs are unreachable"),
    ],
    r"""<span class="token comment"># Fix 1: Verify and fix tunnel mesh configuration</span>
cilium config set tunnel=vxlan
cilium config set tunnel-port=8472

<span class="token comment"># Fix 2: Ensure firewall allows VXLAN between clusters</span>
<span class="token comment"># AWS: Update security groups to allow UDP 8472 between cluster nodes</span>
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx --protocol udp --port 8472 \
  --source-group sg-yyy

<span class="token comment"># Fix 3: Force Cluster Mesh re-sync</span>
kubectl --context us-east delete pod -n kube-system -l k8s-app=cilium
kubectl --context eu-west delete pod -n kube-system -l k8s-app=cilium
<span class="token comment"># Wait for agents to restart and re-establish tunnels</span>

<span class="token comment"># Fix 4: Verify routes appear</span>
kubectl exec -n kube-system ds/cilium -- ip route | grep <remote-cidr>""",
    "Cross-Cluster Pod Connectivity",
    "Direct Pod-to-Pod Routing Across Clusters",
    'Pods in us-east can now <strong>ping pods in eu-west by IP</strong>. <code>ip route</code> shows routes to remote cluster pod CIDRs via the Cilium tunnel interface. <code>cilium bpf tunnel list</code> shows tunnel endpoints for all remote cluster nodes. Hubble shows FORWARDED flows for cross-cluster pod-to-pod traffic.',
    ["Direct pod IP ping across clusters fails", "Check routes → no route to remote CIDR", "Tunnel mesh not established between clusters", "Open firewall UDP 8472 + restart agents", "Routes appear → cross-cluster ping works"],
    "Cross-cluster pod-to-pod routing relies on <strong>tunnel mesh</strong> between ALL nodes across clusters. Cilium uses the same VXLAN/Geneve tunnel it uses within a cluster, extended across Cluster Mesh. The tunnel port (8472/UDP) must be open between all nodes in both clusters. Routes to remote pod CIDRs are propagated via the Cluster Mesh etcd and installed by each Cilium agent. Without route propagation, even if tunnels exist, traffic won't be forwarded.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context us-east exec -n anihpj debug-us -- ping -c3 10.1.2.10\n<span class="output">PING 10.1.2.10 (10.1.2.10) 56(84) bytes of data.\n--- 10.1.2.10 ping statistics ---\n3 packets transmitted, 0 received, 100% packet loss    ← No route!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- ip route | grep 10.1\n<span class="output">(empty — no routes to remote cluster pod CIDR)    ← Routes missing!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context us-east exec -n anihpj debug-us -- ping -c3 10.1.2.10\n<span class="output">PING 10.1.2.10 (10.1.2.10) 56(84) bytes of data.\n64 bytes from 10.1.2.10: icmp_seq=1 ttl=63 time=2.5 ms\n64 bytes from 10.1.2.10: icmp_seq=2 ttl=63 time=2.3 ms    ✅ Cross-cluster!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- ip route | grep 10.1\n<span class="output">10.1.0.0/16 via 10.0.1.1 dev cilium_vxlan    ✅ Route to remote CIDR!</span></div>',
    ]
)

# S79
s79 = sc(79,
    "Configure Network Policy for Cross-Cluster anihpj Traffic",
    "You need to restrict cross-cluster traffic — anihpj-us pods should only access anihpj-eu API, not the database. But <strong>CiliumNetworkPolicy doesn't apply across clusters</strong>. Your job: create cross-cluster network policies for anihpj traffic.",
    r"""<span class="token comment"># Cluster Mesh connected, anihpj global services work</span>
<span class="token comment"># Deploy anihpj in both clusters</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx create namespace anihpj
  kubectl --context $ctx create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
  kubectl --context $ctx create deployment db -n anihpj --image=postgres:15 -l app=anihpj,tier=db
  kubectl --context $ctx expose deployment api -n anihpj --port=80 --name=api-service
  kubectl --context $ctx annotate svc -n anihpj api-service io.cilium/global-service=true --overwrite
done

<span class="token comment"># ❌ BUG: CNP applied to us-east doesn't restrict eu-west traffic</span>
kubectl --context us-east apply -f - << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: restrict-db
  namespace: anihpj
spec:
  endpointSelector:
    matchLabels: {tier: db}
  ingress:
  - fromEndpoints:
    - matchLabels: {tier: api}
EOF
<span class="token comment"># Policy only applies to local cluster — eu-west pods can still access us-east db!</span>""",
    [
        ("pass", "<strong>1.</strong> Cluster Mesh connected: <code>cilium clustermesh status</code> → OK ✅"),
        ("pass", "<strong>2.</strong> CNP applied locally: <code>kubectl get cnp -n anihpj restrict-db</code> → deployed ✅"),
        ("fail", "<strong>3.</strong> Verify policy blocks local: <strong>local non-api pod blocked from db ✅</strong> — but <strong>remote cluster non-api pod reaches db!</strong> ❌"),
        ("fail", "<strong>4.</strong> Check remote pod access: <code>kubectl --context eu-west exec deploy/web -- curl db-service.anihpj.svc.global:5432</code> → <strong>CONNECTED — policy not enforced across clusters!</strong> ❌"),
        ("fail", "<strong>5.</strong> Policy only in local cluster: <code>cilium policy get</code> → <strong>restrict-db applies locally but not to remote cluster traffic</strong> ❌"),
    ],
    [
        (1, "Check if CCNP (cluster-wide) was used instead of CNP:", "kubectl get ccnp restrict-db", "discovery", "No CCNP exists — CNP is namespace-scoped and local to one cluster; cross-cluster policies require CCNP (CiliumClusterwideNetworkPolicy) which applies across all clusters in the mesh"),
        (2, "Verify the CNP is only in one cluster:", "for ctx in us-east eu-west; do kubectl --context $ctx get cnp -n anihpj restrict-db 2>/dev/null; done", "discovery", "CNP exists only in us-east — policies are NOT automatically synced across Cluster Mesh; each cluster manages its own policies"),
        (3, "Check if identity-based policy works across clusters:", "cilium identity list | grep anihpj", "discovery", "Identities are local per cluster — us-east identity 128 for 'tier=db' is different from eu-west identity 256 for 'tier=db'. Cross-cluster identity mapping is needed"),
        (4, "Create CCNP for cross-cluster enforcement:", "kubectl apply -f ccnp-cross-cluster.yaml", "discovery", "CCNP with cluster scope applies to all clusters — but it must be created on EACH cluster where enforcement is desired, or the policy must use global identity references"),
        (5, "Root cause identified:", "CNP is namespace and cluster scoped — cross-cluster policy requires CCNP on all clusters", "root-cause", "CiliumNetworkPolicy (CNP) is namespaced and applies only to the local cluster. For cross-cluster policy enforcement, you need: 1) CiliumClusterwideNetworkPolicy (CCNP) on all clusters, 2) Consistent labels across clusters (same labels = same identity via Cluster Mesh), and 3) The policy must reference identities, not endpoints, for cross-cluster matching"),
    ],
    r"""<span class="token comment"># Fix: Create CCNP on BOTH clusters for cross-cluster enforcement</span>
cat > ccnp-cross-cluster.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: restrict-db-cross-cluster
spec:
  endpointSelector:
    matchLabels:
      app: anihpj
      tier: db
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: anihpj
        tier: api
    - matchLabels:
        app: anihpj
        tier: web
EOF

for ctx in us-east eu-west; do
  kubectl --context $ctx apply -f ccnp-cross-cluster.yaml
done

<span class="token comment"># Verify policy is clusterwide</span>
kubectl --context us-east get ccnp restrict-db-cross-cluster
kubectl --context eu-west get ccnp restrict-db-cross-cluster""",
    "Cross-Cluster Policy Enforcement",
    "Network Policy Enforced Across Both Clusters",
    'CCNP <code>restrict-db-cross-cluster</code> is applied on both clusters. Remote eu-west pods can no longer bypass the policy — only pods with <code>tier=api</code> or <code>tier=web</code> labels can reach the db service across clusters. Hubble shows <strong>DROPPED</strong> verdicts for unauthorized cross-cluster db access.',
    ["CNP applied locally → blocks local only", "Remote pods bypass local CNP → no enforcement", "Check CCNP → not deployed, CNP is cluster-scoped", "Create CCNP on both clusters → cross-cluster enforcement", "Remote unauthorized traffic now DROPPED"],
    "Network policies are <strong>not synced across Cluster Mesh</strong>. Each cluster enforces its own policies independently. For cross-cluster enforcement, apply policies on ALL clusters where traffic originates or terminates. Use <strong>CiliumClusterwideNetworkPolicy (CCNP)</strong> for consistent cluster-wide rules. CCNP applies to all namespaces and, when deployed on all clusters, provides consistent cross-cluster policy enforcement.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context eu-west exec deploy/web -- curl -s db-service.anihpj.svc.global:5432\n<span class="output">Connected to PostgreSQL 15.0    ← Remote pod reaches db — policy bypassed!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context eu-west get cnp -n anihpj restrict-db\n<span class="output">Error from server (NotFound): ciliumnetworkpolicies.cilium.io "restrict-db" not found    ← Only on us-east!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context eu-west exec deploy/web -- curl -s --connect-timeout 3 db-service.anihpj.svc.global:5432\n<span class="output">curl: (28) Connection timed out after 3001 ms    ← DROPPED by CCNP! ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe --verdict DROPPED --to-port 5432\n<span class="output">TIMESTAMP          SOURCE                    DESTINATION               VERDICT\n12:05:01            anihpj/web-eu-xxx:45678   anihpj/db-us-yyy:5432     DROPPED    ✅ Cross-cluster policy enforced!</span></div>',
    ]
)

# S80
s80 = sc(80,
    "Fix Cluster Mesh Identity Conflict Between Clusters",
    "After connecting clusters, you notice <strong>identity conflicts</strong> — pods with the same labels in different clusters receive different numeric identities. Hubble shows incorrect policy verdicts. Your job: fix the identity allocation to ensure consistent identities across clusters.",
    r"""<span class="token comment"># Cluster Mesh connected but identity conflicts exist</span>
cilium clustermesh status
<span class="token comment"># Both clusters: OK</span>

<span class="token comment"># Deploy same app in both clusters</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx create namespace anihpj
  kubectl --context $ctx create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
done

<span class="token comment"># ❌ BUG: Same labels → different numeric identities across clusters</span>
kubectl --context us-east exec -n kube-system ds/cilium -- cilium identity list | grep anihpj
<span class="token comment"># 128    app=anihpj,tier=web    (us-east)</span>
kubectl --context eu-west exec -n kube-system ds/cilium -- cilium identity list | grep anihpj
<span class="token comment"># 256    app=anihpj,tier=web    (eu-west)    ← Different identity!</span>""",
    [
        ("pass", "<strong>1.</strong> Cluster Mesh connected: <code>cilium clustermesh status</code> → OK ✅"),
        ("pass", "<strong>2.</strong> Same labels in both clusters: <code>kubectl get pods -n anihpj --show-labels</code> → app=anihpj,tier=web ✅"),
        ("fail", "<strong>3.</strong> Different numeric identities: <code>cilium identity list | grep anihpj</code> → <strong>us-east: 128, eu-west: 256 — mismatch!</strong> ❌"),
        ("fail", "<strong>4.</strong> Cross-cluster policy inconsistent: <strong>policy allowing identity 128 on us-east doesn't match identity 256 on eu-west</strong> ❌"),
        ("fail", "<strong>5.</strong> Identity-based policy broken: <strong>policies referencing pod labels resolve to different numeric IDs per cluster</strong> ❌"),
    ],
    [
        (1, "Check identity allocation mode:", "kubectl get cm -n kube-system cilium-config -o yaml | grep identity-allocation-mode", "discovery", "identity-allocation-mode: crd — each cluster independently allocates numeric identities from its own pool; no coordination across clusters"),
        (2, "Verify Cluster Mesh identity sync:", "kubectl exec -n kube-system ds/cilium -- cilium bpf identity list | grep <remote-cluster>", "discovery", "Remote cluster identities are prefixed differently — Cluster Mesh does not unify local identity pools by default"),
        (3, "Check if cluster-pool identity mode would help:", "cilium config | grep cluster-pool", "discovery", "identity-allocation-mode could be set to 'kvstore' with shared etcd to coordinate identity allocation globally, but this requires external etcd setup"),
        (4, "Compare identity labels vs numeric IDs:", "kubectl get ciliumidentity -A | grep anihpj", "discovery", "Each cluster has its own CiliumIdentity CRDs with different numeric IDs — the identity-to-label mapping is local; Cluster Mesh propagates identities but doesn't unify them"),
        (5, "Root cause identified:", "CRD-based identity allocation assigns numeric IDs independently per cluster", "root-cause", "When identity-allocation-mode=crd, each Cilium agent independently allocates a numeric identity for a label set. Since clusters don't coordinate identity allocation, the same labels get different numbers. For unified identities, either: 1) Use kvstore mode with shared etcd (global identity pool), or 2) Reference policies by labels (not numeric IDs), which Cilium resolves locally per cluster"),
    ],
    r"""<span class="token comment"># Fix 1: Use label-based policies instead of identity-based</span>
<span class="token comment"># Policies already use matchLabels — Cilium resolves per-cluster</span>
<span class="token comment"># The numeric identity difference is cosmetic for label-based policies</span>

<span class="token comment"># Fix 2 (for production): Switch to kvstore identity mode</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set identityAllocationMode=kvstore \
  --set etcd.enabled=true \
  --set etcd.endpoints[0]=https://shared-etcd.internal:2379

<span class="token comment"># Fix 3: Verify consistent identities after switch</span>
for ctx in us-east eu-west; do
  kubectl --context $ctx exec -n kube-system ds/cilium -- cilium identity list | grep anihpj
done

<span class="token comment"># Important: label-based policies work fine even with different numeric IDs</span>
<span class="token comment"># The numeric ID difference is only a problem for policies using toCIDRSet or identity-based rules</span>""",
    "Policies Work Across Clusters",
    "Label-Based Policies Enforced Consistently",
    'Label-based CiliumNetworkPolicies work correctly across clusters despite different numeric identities. Cilium resolves <code>matchLabels</code> to the appropriate local numeric identity in each cluster. Cross-cluster traffic is correctly allowed/denied based on labels. For production, <code>identityAllocationMode=kvstore</code> with shared etcd ensures globally consistent numeric identities.',
    ["Same labels → different numeric IDs per cluster", "identity-allocation-mode: crd → local pools", "Label-based policies still work (resolve locally)", "For unified IDs → switch to kvstore mode", "Policies enforce correctly despite numeric differences"],
    "Numeric identity differences across clusters are <strong>expected with CRD mode</strong> and generally don't break policies. Cilium resolves <code>matchLabels</code> to the local numeric identity in each cluster. Policies using labels work correctly. Only policies that reference numeric identities directly (rare) would be affected. For globally consistent numeric IDs, use <code>identityAllocationMode=kvstore</code> with a shared etcd cluster — this coordinates identity allocation across the mesh.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- cilium identity list | grep "tier=web"\n<span class="output">128    k8s:app=anihpj k8s:tier=web k8s:io.kubernetes.pod.namespace=anihpj    ← us-east: 128</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl --context eu-west exec -n kube-system ds/cilium -- cilium identity list | grep "tier=web"\n<span class="output">256    k8s:app=anihpj k8s:tier=web k8s:io.kubernetes.pod.namespace=anihpj    ← eu-west: 256 — DIFFERENT!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get cm -n kube-system cilium-config -o yaml | grep identity-allocation-mode\n<span class="output">identity-allocation-mode: crd    ← Local allocation per cluster (labels still work)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> <span class="token comment"># Label-based CNP resolves correctly per cluster — no changes needed</span>\nkubectl exec -n kube-system ds/cilium -- cilium policy get | grep anihpj\n<span class="output">POLICY    LABELS                          ENFORCEMENT\nrestrict-db  app=anihpj,tier=db           ingress    ✅ Enforced per cluster!</span></div>',
    ]
)

# ====== Assemble ======
all_scenarios = s78 + '\n\n' + s79 + '\n\n' + s80

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 2 (S78-S80) inserted!")
else:
    print("ERROR!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File size: {len(html.encode('utf-8'))} bytes")
