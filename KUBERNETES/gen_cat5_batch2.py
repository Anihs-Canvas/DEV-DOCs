#!/usr/bin/env python3
"""Generate Category 5: Installation & Configuration — Batch 2: S68-S70"""
import re

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_short, verify_detail, tenet_steps, tenet_text, before_outputs, after_outputs):
    ei_html = ''.join(f'<div class="lookat-item"><span class="li-check {"pass" if t=="pass" else "fail"}">{"✓" if t=="pass" else "✗"}</span><span>{txt}</span></div>\n' for t,txt in error_items)
    di_html = ''.join(f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n' for num,label,cmd,ftype,ftext in debug_items)
    tf_html = '\n'.join(f'<div class="tenet-step"><div class="step-num">{chr(0x2460+i)}</div><div class="step-label">{lbl}</div></div>' for i,lbl in enumerate(tenet_steps))
    bo_html = '\n'.join(before_outputs)
    ao_html = '\n'.join(after_outputs)

    return f'''    <!-- ═══════════════ S{n}: {title} ═══════════════ -->
    <div class="scenario-block" id="sc-s{n}">
        <div class="sc-header">
            <div class="sc-badge">S{n}</div>
            <div class="sc-header-content">
                <div class="sc-num">🧪 SCENARIO S{n} — Category 5: Installation &amp; Configuration</div>
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
                    {ei_html}
                </div>
            </div>
            <div class="sc-step debug-find">
                <div class="sc-step-num">🔍</div>
                <div class="sc-step-content">
                    <h4>🔍 Debug — Find the Root Cause</h4>
                    {di_html}
                </div>
            </div>
            <div class="sc-step">
                <div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div>
                <div class="sc-step-content">
                    <h4 style="color: #3fb950;">🔧 Fix — {fix_desc}</h4>
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-lang">BASH — apply the fix</span>
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
                <div class="tenet-flow">{tf_html}</div>
                <p><strong>Tenet:</strong> {tenet_text}</p>
                <h5>📟 Command Outputs — Error State (BEFORE fix)</h5>
                {bo_html}
                <h5>📟 Command Outputs — AFTER Fix</h5>
                {ao_html}
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

# ======================== S68 ========================
s68 = sc(68,
    "Fix CNI Chaining — Cilium + AWS VPC CNI for anihpj",
    "On EKS, you install Cilium alongside AWS VPC CNI for <strong>CNI chaining</strong> (AWS VPC CNI does IPAM, Cilium does policy). But <strong>anihpj pods lose network connectivity</strong> after Cilium installation. Some pods get IPs from AWS VPC CNI, others from Cilium — causing a split-brain IPAM scenario.",
    r"""<span class="token comment"># EKS cluster with AWS VPC CNI running</span>
kubectl get pods -n kube-system -l k8s-app=aws-node
<span class="token comment"># aws-node-xxxxx   1/1     Running</span>

<span class="token comment"># Install Cilium for CNI chaining</span>
helm install cilium cilium/cilium -n kube-system \
  --set cni.chainingMode=aws-cni \
  --set cni.exclusive=false

<span class="token comment"># ❌ BUG: anihpj pods get split between CNIs</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=3
kubectl get pods -n anihpj -o wide
<span class="token comment"># web-xxx   1/1   Running   192.168.1.5   ← VPC CNI IP (OK)
# web-yyy   1/1   Running   10.0.0.23     ← Cilium IP (WRONG!)
# web-zzz   0/1   Pending   &lt;none&gt;         ← No IP assigned</span>""",
    [
        ("pass", "<strong>1.</strong> AWS VPC CNI running: <code>kubectl get pods -n kube-system -l k8s-app=aws-node</code> → Running ✅"),
        ("pass", "<strong>2.</strong> Cilium installed: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → Running ✅"),
        ("fail", "<strong>3.</strong> Pods get different IP ranges: <code>kubectl get pods -n anihpj -o wide</code> → <strong>mixed 192.168.x (VPC) and 10.0.x (Cilium) IPs!</strong> ❌"),
        ("fail", "<strong>4.</strong> Some pods Pending: <code>kubectl get pods -n anihpj</code> → <strong>Status: Pending — kubelet can't decide which CNI to use</strong> ❌"),
        ("fail", "<strong>5.</strong> Cross-pod connectivity broken: Pods with VPC CNI IPs cannot reach pods with Cilium IPs ❌"),
    ],
    [
        (1, "Check which CNI configs exist on the node:", "ls /etc/cni/net.d/ on a worker node", "discovery", "Both 10-aws.conflist AND 05-cilium.conflist exist — kubelet picks the lowest numbered config, but both compete for IP allocation"),
        (2, "Verify Cilium chaining mode:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -A3 cni", "discovery", "cni.chainingMode is set but cni.customConf might not be true — Cilium overwrites the AWS CNI config instead of chaining after it"),
        (3, "Check AWS VPC CNI ENI limits:", "kubectl logs -n kube-system ds/aws-node | grep ENI", "discovery", "AWS VPC CNI may be exhausted on ENI IPs — some pods get Cilium IPs because AWS CNI can't assign more"),
        (4, "Check Cilium IPAM mode:", "kubectl get cm -n kube-system cilium-config -o yaml | grep ipam", "discovery", "ipam.mode=cluster-pool is active — Cilium is independently allocating IPs from its own pool rather than deferring to AWS CNI"),
        (5, "Root cause identified:", "Improper CNI chaining config causes dual IPAM allocation", "root-cause", "CNI chaining requires: 1) cni.chainingMode must match the primary CNI (aws-cni), 2) cni.customConf=true so Cilium doesn't overwrite the primary CNI config, 3) ipam.mode must be set to 'eni' or 'cluster-pool' depending on who owns IPAM, and 4) the primary CNI's config must list Cilium as the chained plugin, not the other way around"),
    ],
    r"""<span class="token comment"># Fix: Proper CNI chaining — Cilium sits AFTER AWS VPC CNI</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --reuse-values \
  --set cni.chainingMode=aws-cni \
  --set cni.customConf=true \
  --set cni.configMap=cni-configuration \
  --set ipam.mode=eni \
  --set eni.enabled=true \
  --set egressMasqueradeInterfaces=eth0

<span class="token comment"># Restart Cilium agents</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system

<span class="token comment"># Delete and recreate anihpj pods to get proper IPs</span>
kubectl delete pods -n anihpj --all
kubectl wait --for=condition=ready pod -n anihpj --all --timeout=120s""",
    "CNI Chaining Working Correctly",
    "Cilium and AWS VPC CNI Properly Chained",
    'CNI chaining is properly configured. AWS VPC CNI handles <strong>IPAM via ENI</strong> — all anihpj pods receive VPC-routable IPs (192.168.x). Cilium sits on top for <strong>policy enforcement, observability, and eBPF-based routing</strong>. All pods are Running with consistent VPC IPs. Cross-pod connectivity and Hubble flows work correctly.',
    ["Dual CNI configs compete for IP allocation", "Pods get mixed IPs from both CNIs", "Check cni.chainingMode and ipam.mode", "Set cni.customConf=true, ipam.mode=eni", "Restart agents → all pods get VPC IPs"],
    "CNI chaining means Cilium delegates IPAM to the primary CNI (AWS VPC CNI or Azure CNI) while handling policy and observability. The critical settings are: <code>cni.chainingMode</code> (identifies the primary CNI), <code>cni.customConf=true</code> (don't overwrite primary CNI config), and <code>ipam.mode</code> (must match the primary CNI's IPAM — 'eni' for AWS, 'cluster-pool' only if Cilium owns IPAM). Without these aligned, both CNIs compete for IP allocation causing split-brain.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    IP            NODE\nweb-xxx    1/1     Running   192.168.1.5   node-1\nweb-yyy    1/1     Running   10.0.0.23     node-2    ← Mix of VPC IP and Cilium cluster-pool IP!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj web-xxx -- ping 10.0.0.23\n<span class="output">PING 10.0.0.23: 56 data bytes\n(no response)    ← Cross-CNI connectivity broken!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    IP            NODE\nweb-xxx    1/1     Running   192.168.1.5   node-1\nweb-yyy    1/1     Running   192.168.2.8   node-2\nweb-zzz    1/1     Running   192.168.3.11  node-1    ← All VPC IPs! ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj web-xxx -- wget -qO- http://192.168.2.8\n<span class="output">&lt;html&gt;...nginx...&lt;/html&gt;    ✅ Cross-pod connectivity restored!</span></div>',
    ]
)

# ======================== S69 ========================
s69 = sc(69,
    "Debug Cilium Connectivity Test Failures in New Cluster",
    "You run <code>cilium connectivity test</code> after a fresh Cilium install, but <strong>multiple test scenarios fail</strong>. The test reports FAIL for pod-to-pod, pod-to-service, and pod-to-world tests. Your job: diagnose why the connectivity test fails and fix the underlying issues.",
    r"""<span class="token comment"># Fresh Cilium install completed</span>
cilium status --wait

<span class="token comment"># ❌ BUG: Connectivity test fails</span>
cilium connectivity test
<span class="token comment"># [=] Test [pod-to-pod] .............................................. ❌
# [=] Test [pod-to-service] ......................................... ❌
# [=] Test [pod-to-world] ........................................... ❌
# [!] 3 of 8 tests failed</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium status OK: <code>cilium status</code> → all components healthy ✅"),
        ("pass", "<strong>2.</strong> Nodes ready: <code>kubectl get nodes</code> → All Ready ✅"),
        ("fail", "<strong>3.</strong> Connectivity test fails: <code>cilium connectivity test</code> → <strong>pod-to-pod, pod-to-service, pod-to-world FAIL</strong> ❌"),
        ("fail", "<strong>4.</strong> Test pods stuck: <code>kubectl get pods -n cilium-test</code> → <strong>some pods Pending/CrashLoopBackOff</strong> ❌"),
        ("fail", "<strong>5.</strong> Hubble shows DROPPED: <code>hubble observe --verdict DROPPED</code> → <strong>policy denied or no route to host</strong> ❌"),
    ],
    [
        (1, "Check connectivity test namespace:", "kubectl get pods -n cilium-test", "discovery", "Some test pods in Pending/CrashLoopBackOff — indicates CNI or resource issues, not policy"),
        (2, "Check if DNS is working for test pods:", "kubectl exec -n cilium-test <pod> -- nslookup kubernetes.default", "discovery", "DNS resolution fails — CoreDNS pods may not be reachable from the test namespace"),
        (3, "Verify pod-to-pod across nodes:", "kubectl exec -n cilium-test <pod-node1> -- ping <pod-node2-ip>", "discovery", "Ping fails across nodes — VXLAN tunnel, routing, or firewall blocking cross-node pod traffic"),
        (4, "Check kube-proxy or KPR status:", "cilium config | grep kubeProxyReplacement", "discovery", "KPR is disabled but kube-proxy not running — Services have no backend routing"),
        (5, "Root cause identified:", "Multiple possible causes based on cluster setup", "root-cause", "Connectivity test failures are rarely a single issue. Common root causes: 1) MTU mismatch (VXLAN/Geneve overhead), 2) kube-proxy not running alongside KPR=disabled, 3) NetworkPolicy denying test traffic, 4) DNS blocked by policy, or 5) firewall rules between nodes blocking VXLAN port 8472/UDP"),
    ],
    r"""<span class="token comment"># Fix 1: Check MTU and adjust for tunnel overhead</span>
MTU=$(ip link show eth0 | grep -oP 'mtu \K[0-9]+')
cilium config set mtu $((MTU - 50))  <span class="token comment"># 50 bytes for VXLAN overhead</span>

<span class="token comment"># Fix 2: Ensure kube-proxy is running if KPR is disabled</span>
kubectl get pods -n kube-system -l k8s-app=kube-proxy
<span class="token comment"># If not running and KPR disabled → install kube-proxy</span>

<span class="token comment"># Fix 3: Check for default-deny NetworkPolicies blocking test namespace</span>
kubectl get netpol -A
<span class="token comment"># If a deny-all exists, create an allow rule for cilium-test</span>

<span class="token comment"># Fix 4: Check firewall between nodes</span>
<span class="token comment"># Ensure VXLAN port 8472/UDP is open between all nodes</span>
<span class="token comment"># iptables -I INPUT -p udp --dport 8472 -j ACCEPT</span>

<span class="token comment"># Fix 5: Re-run connectivity test</span>
cilium connectivity test""",
    "Connectivity Test Passes",
    "All Connectivity Tests Passing",
    'All 8 connectivity test scenarios pass: pod-to-pod (intra-node), pod-to-pod (inter-node), pod-to-service, pod-to-world, pod-to-host, DNS, client-egress, and network-perf. <code>cilium connectivity test</code> reports <strong>8/8 PASS</strong>. Hubble shows FORWARDED flows between all test pods.',
    ["cilium connectivity test → FAIL", "Check test pods → some Pending/CrashLoop", "Debug specific failures: MTU, DNS, kube-proxy, firewall", "Apply targeted fixes for each failure", "Re-run → 8/8 PASS"],
    "The Cilium connectivity test is the single most important diagnostic. It tests the full networking stack: pod-to-pod, Services, DNS, egress, and performance. When it fails, break it down: <strong>if pod-to-pod fails → routing/tunnel issue</strong>; <strong>if pod-to-service fails → kube-proxy/KPR issue</strong>; <strong>if DNS fails → CoreDNS reachability</strong>; <strong>if pod-to-world fails → masquerading/egress</strong>. Fix one layer at a time.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium connectivity test\n<span class="output">[=] Test [pod-to-pod] .................................... ❌ FAIL\n[=] Test [pod-to-service] ................................ ❌ FAIL\n[=] Test [pod-to-world] .................................. ❌ FAIL\n[!] 3 of 8 tests failed — check cilium-test namespace for details</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl describe pod -n cilium-test <failing-pod> | tail -5\n<span class="output">Events:\n  Type     Reason     Message\n  Warning  Failed     Failed to create pod sandbox: network plugin cni failed to set up pod network: MTU too large</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium connectivity test\n<span class="output">[=] Test [pod-to-pod] .................................... ✅ PASS\n[=] Test [pod-to-service] ................................ ✅ PASS\n[=] Test [pod-to-world] .................................. ✅ PASS\n[=] Test [dns] ........................................... ✅ PASS\n[=] Test [client-egress] ................................. ✅ PASS\n[=] Test [pod-to-host] ................................... ✅ PASS\n[=] Test [host-to-pod] ................................... ✅ PASS\n[=] Test [network-perf] .................................. ✅ PASS\n[✓] All 8 tests passed! 🎉</span></div>',
    ]
)

# ======================== S70 ========================
s70 = sc(70,
    "Upgrade Cilium from v1.15 to v1.16 with anihpj Running",
    "You need to upgrade Cilium from v1.15 to v1.16 on a production cluster running anihpj. After the Helm upgrade, <strong>Cilium agents fail to start with new errors</strong> and anihpj experiences downtime. Your job: perform a safe rolling upgrade preserving anihpj connectivity.",
    r"""<span class="token comment"># Current: Cilium v1.15 running, anihpj deployed</span>
cilium version
<span class="token comment"># cilium-cli: v0.16, cilium image: quay.io/cilium/cilium:v1.15.0</span>

kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=3
kubectl expose deployment web -n anihpj --port=80

<span class="token comment"># ❌ BUG: Direct Helm upgrade breaks agents</span>
helm upgrade cilium cilium/cilium -n kube-system --version 1.16.0
<span class="token comment"># Agents enter CrashLoopBackOff — anihpj loses connectivity!</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium v1.15 running: <code>cilium version</code> → v1.15.0 ✅"),
        ("pass", "<strong>2.</strong> anihpj deployed and serving: <code>kubectl get pods -n anihpj</code> → 3/3 Running ✅"),
        ("fail", "<strong>3.</strong> Helm upgrade to v1.16: <code>helm upgrade cilium cilium/cilium --version 1.16.0</code> → <strong>agents CrashLoopBackOff!</strong> ❌"),
        ("fail", "<strong>4.</strong> Agent logs show CRD schema mismatch: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>\"Field 'xyz' not recognized in CRD v2alpha1\"</strong> ❌"),
        ("fail", "<strong>5.</strong> anihpj pods lose connectivity during agent restart: <strong>rolling restart doesn't preserve connections if not drained first</strong> ❌"),
    ],
    [
        (1, "Check Cilium upgrade guide for v1.16:", "cilium upgrade --help | grep -A5 1.16", "discovery", "Cilium v1.16 requires CRD migration and deprecated field removal — direct Helm upgrade skips CRD updates"),
        (2, "Check current CRD versions:", "kubectl get crd | grep cilium | awk '{print $1, $3}'", "discovery", "CRDs are at v2alpha1 but v1.16 introduces v2 — the new agents can't reconcile old CRD schema"),
        (3, "Review Helm diff before upgrade:", "helm diff upgrade cilium cilium/cilium -n kube-system --version 1.16.0", "discovery", "Multiple deprecated values flagged: 'enable-endpoint-routes' removed, 'tunnel' changed, 'identityAllocationMode' renamed"),
        (4, "Check if pre-upgrade steps are needed:", "kubectl get cm -n kube-system cilium-pre-flight -o yaml 2>/dev/null", "discovery", "No pre-flight check run — Cilium v1.16 requires pre-flight validation to detect incompatible configs before upgrade"),
        (5, "Root cause identified:", "Direct Helm upgrade skips CRD migration and config validation", "root-cause", "Major Cilium version upgrades (v1.15→v1.16) require: 1) CRD upgrade BEFORE agent upgrade, 2) Removal of deprecated Helm values, 3) Pre-flight validation, and 4) Per-node draining to preserve workload connectivity during agent restart. Skipping any step causes agent crashes and downtime"),
    ],
    r"""<span class="token comment"># Fix: Safe upgrade with pre-flight and per-node draining</span>
<span class="token comment"># Step 1: Upgrade CRDs first</span>
kubectl apply -f https://raw.githubusercontent.com/cilium/cilium/v1.16.0/install/kubernetes/cilium/crds/crd-clustermesh.yaml
kubectl apply -f https://raw.githubusercontent.com/cilium/cilium/v1.16.0/install/kubernetes/cilium/crds/all-crds.yaml

<span class="token comment"># Step 2: Run pre-flight check</span>
cilium preflight --version 1.16.0

<span class="token comment"># Step 3: Helm upgrade with updated values</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --version 1.16.0 \
  --set upgradeCompatibility=1.15 \
  --set routingMode=native \
  --set ipam.mode=cluster-pool

<span class="token comment"># Step 4: Drain nodes one at a time for zero-downtime</span>
for node in $(kubectl get nodes -o name); do
  kubectl cordon $node
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data
  sleep 30  <span class="token comment"># Wait for Cilium agent to restart on node</span>
  kubectl uncordon $node
done

<span class="token comment"># Step 5: Verify</span>
cilium version
cilium status""",
    "Cilium v1.16 Running",
    "anihpj Running on Cilium v1.16 with Zero Downtime",
    'Cilium is upgraded to v1.16.0. All agents are healthy. <code>cilium version</code> confirms v1.16. anihpj pods maintained connectivity throughout the upgrade thanks to <strong>per-node draining</strong>. <code>kubectl get pods -n anihpj</code> shows all 3 pods Running with the same IPs. Hubble shows continued FORWARDED flows.',
    ["cilium version → v1.15", "Helm upgrade → CrashLoopBackOff", "CRD schema mismatch + deprecated values", "CRD upgrade → pre-flight → Helm with updated values", "Per-node drain → v1.16 running → zero downtime"],
    "Never upgrade Cilium across minor versions without: 1) <strong>Upgrading CRDs first</strong> (major versions often add/change CRD fields), 2) <strong>Running pre-flight</strong> (validates config compatibility), 3) <strong>Removing deprecated Helm values</strong> (check release notes), and 4) <strong>Per-node draining</strong> (cordon→drain→restart agent→uncordon). This preserves workload connectivity throughout the upgrade.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> helm upgrade cilium cilium/cilium -n kube-system --version 1.16.0\n<span class="output">Release "cilium" has been upgraded. Happy Helming!\n(but agents enter CrashLoop...)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i "crd\\\\|schema\\\\|field"\n<span class="output">level=fatal msg="Failed to register CRD" error="field \'endpointRoutes\' not found in v2.CiliumEndpoint"\nlevel=fatal msg="CRD schema validation failed" subsys=k8s    ← CRD mismatch!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj\n<span class="output">NAME       READY   STATUS    RESTARTS   AGE\nweb-xxx    0/1     Error     0          30s    ← Downtime!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium version\n<span class="output">cilium-cli: v0.16\ncilium image (running): quay.io/cilium/cilium:v1.16.0    ✅ Upgraded!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    IP            NODE\nweb-xxx    1/1     Running   192.168.1.5   node-1\nweb-yyy    1/1     Running   192.168.2.8   node-2\nweb-zzz    1/1     Running   192.168.3.11  node-3    ✅ All running!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK     v1.16.0\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       All 3 nodes healthy ✅</span></div>',
    ]
)

# ====== Assemble ======
all_scenarios = s68 + '\n\n' + s69 + '\n\n' + s70

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 2 (S68-S70) inserted!")
else:
    print("ERROR: appendices marker not found!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File size: {len(html.encode('utf-8'))} bytes")
