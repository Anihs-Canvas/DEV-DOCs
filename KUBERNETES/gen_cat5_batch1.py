#!/usr/bin/env python3
"""Generate Category 5: Installation & Configuration — Batch 1: S65-S67 (redesigned format)"""

with open('cilium-test-prep.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

def sc(n, title, desc, deploy_code, error_items, debug_items, fix_code, fix_desc, verify_short, verify_detail, tenet_steps, tenet_text, before_outputs, after_outputs):
    """Generate a scenario block matching S1 reference exactly (redesigned format)"""
    ei_html = ''.join(
        f'<div class="lookat-item"><span class="li-check {"pass" if t == "pass" else "fail"}">{"✓" if t == "pass" else "✗"}</span><span>{txt}</span></div>\n'
        for t, txt in error_items
    )
    di_html = ''.join(
        f'<div class="lookat-item"><span class="li-num">{num}</span><span><strong>{label} </strong><code>{cmd}</code><br><span class="li-finding {ftype}">→ {ftext}</span></span></div>\n'
        for num, label, cmd, ftype, ftext in debug_items
    )
    tf_html = '\n'.join(
        f'<div class="tenet-step"><div class="step-num">{chr(0x2460 + i)}</div><div class="step-label">{label}</div></div>'
        for i, label in enumerate(tenet_steps)
    )
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
                <div class="tenet-flow">
                    {tf_html}
                </div>
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

# ======================== S65 ========================
s65 = sc(65,
    "Install Cilium from Scratch on EKS with anihpj Deployment",
    "You are setting up a new EKS cluster for anihpj. Cilium installation via Helm <strong>fails with node initialization errors</strong>. Pods stay in Pending state and Cilium agents crash. Your job: install Cilium correctly on EKS, accounting for AWS-specific networking requirements.",
    r"""<span class="token comment"># ❌ BUG: Default Helm install fails on EKS</span>
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium \
  --namespace kube-system

<span class="token comment"># Check Cilium status — agents not ready</span>
kubectl get pods -n kube-system -l k8s-app=cilium
<span class="token comment"># NAME           READY   STATUS             RESTARTS
# cilium-xxxxx   0/1     CrashLoopBackOff   5</span>

<span class="token comment"># Deploy anihpj — pods stuck Pending</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl get pods -n anihpj
<span class="token comment"># NAME       READY   STATUS    RESTARTS
# web-xxx    0/1     Pending   0      ← Stuck!</span>""",
    [
        ("pass", "<strong>1.</strong> EKS cluster running: <code>kubectl get nodes</code> → 2+ nodes Ready ✅"),
        ("pass", "<strong>2.</strong> Helm installed: <code>helm version</code> → v3.x ✅"),
        ("fail", "<strong>3.</strong> Cilium pods crash: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → <strong>CrashLoopBackOff</strong> ❌"),
        ("fail", "<strong>4.</strong> anihpj pods Pending: <code>kubectl get pods -n anihpj</code> → <strong>Status: Pending — no CNI</strong> ❌"),
        ("fail", "<strong>5.</strong> Cilium agent logs: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>\"Unable to set up ENI mode — AWS API access denied\"</strong> ❌"),
    ],
    [
        (1, "Check Cilium agent logs for EKS errors:", "kubectl logs -n kube-system ds/cilium | grep -i error", "discovery", "Failed to initialize ENI datapath — Cilium defaults to ENI mode on EKS but the node's IAM role lacks EC2:DescribeNetworkInterfaces permission"),
        (2, "Verify AWS VPC CNI is installed (EKS default):", "kubectl get pods -n kube-system -l k8s-app=aws-node", "discovery", "AWS VPC CNI (aws-node) is running — Cilium must either replace it or chain with it"),
        (3, "Check IAM permissions for worker node role:", "aws iam list-attached-role-policies --role-name <node-role>", "discovery", "Node role missing AmazonEKS_CNI_Policy — required for ENI/IPAM mode, OR the role exists but lacks EC2:AssignPrivateIpAddresses"),
        (4, "Check Cilium ConfigMap for ENI settings:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -i eni", "discovery", "eni: \"true\" is set — but EKS with managed node groups requires proper IAM and security group setup"),
        (5, "Root cause identified:", "Default Helm install uses ENI IPAM mode on EKS without required IAM permissions", "root-cause", "Cilium auto-detects EKS and enables ENI (Elastic Network Interface) IPAM mode. This requires: 1) IAM role with EC2 permissions on worker nodes, 2) AWS VPC CNI removal or chaining config, and 3) subnet tags for auto-discovery. Missing any of these causes agent crash"),
    ],
    r"""<span class="token comment"># Fix 1: Reinstall Cilium with EKS-specific values</span>
helm uninstall cilium -n kube-system
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set ipam.mode=cluster-pool \
  --set ipam.operator.clusterPoolIPv4PodCIDRList="10.0.0.0/16" \
  --set routingMode=native \
  --set enable-endpoint-routes=true \
  --set kubeProxyReplacement=disabled \
  --set nodeinit.enabled=true \
  --set nodeinit.reconfigureKubelet=true

<span class="token comment"># Fix 2: Wait for Cilium to be ready</span>
cilium status --wait
kubectl wait --for=condition=ready pod -n kube-system -l k8s-app=cilium --timeout=300s

<span class="token comment"># Fix 3: Verify anihpj pods get IPs</span>
kubectl get pods -n anihpj -o wide""",
    "Cilium Installed on EKS",
    "Cilium Installed on EKS with anihpj Running",
    'Cilium is installed with <code>ipam.mode=cluster-pool</code> (not ENI mode) and <code>routingMode=native</code> for direct VPC routing. The <code>nodeinit</code> component configures kubelet to use Cilium. All Cilium agents are healthy. anihpj pods transition from <strong>Pending to Running</strong> with IPs from the cluster-pool CIDR. <code>hubble observe -n anihpj</code> shows FORWARDED flows between web and api pods.',
    ["Helm install cilium → agents CrashLoop", "Logs show ENI/AWS API access denied", "Check IAM role → missing EC2 permissions", "Switch ipam.mode to cluster-pool", "Reinstall → agents healthy → anihpj pods Running"],
    "On EKS, Cilium auto-detects the platform and defaults to <strong>ENI IPAM mode</strong> (<code>ipam.mode=eni</code>). This requires proper IAM roles, security groups, and subnet tags. For simpler setups, use <code>ipam.mode=cluster-pool</code> with <code>routingMode=native</code>. The <code>nodeinit</code> component is essential — it reconfigures kubelet's CNI config to point to Cilium. Without it, kubelet cannot assign pod IPs.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n kube-system -l k8s-app=cilium\n<span class="output">NAME           READY   STATUS             RESTARTS   AGE\ncilium-abcde   0/1     CrashLoopBackOff   6          5m\ncilium-fghij   0/1     CrashLoopBackOff   6          5m    ← Agents crashing!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | tail -5\n<span class="output">level=fatal msg="Unable to set up ENI datapath" error="AccessDenied: User arn:aws:sts::123:assumed-role/node-role/i-xxx is not authorized to perform ec2:DescribeNetworkInterfaces"\nlevel=fatal msg="Failed to initialize IPAM" subsys=ipam    ← IAM permission missing!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj\n<span class="output">NAME       READY   STATUS    RESTARTS   AGE\nweb-xxx    0/1     Pending   0          3m    ← No CNI, no IP assigned</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       All 2 nodes healthy ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    RESTARTS   AGE   IP\nweb-xxx    1/1     Running   0          30s   10.0.1.10    ← IP assigned! ✅\nweb-yyy    1/1     Running   0          30s   10.0.2.11</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> hubble observe -n anihpj\n<span class="output">TIMESTAMP          SOURCE             DESTINATION        VERDICT\n12:05:01.123        anihpj/web-xxx     anihpj/web-yyy     FORWARDED    ✅ anihpj live!</span></div>',
    ]
)

# ======================== S66 ========================
s66 = sc(66,
    "Debug Cilium Install Failing on AKS Due to Network Plugin Conflict",
    "You try to install Cilium on an existing AKS cluster, but <strong>Cilium agents fail to start</strong>. The Azure CNI is already running and there's a <strong>network plugin conflict</strong>. Your job: resolve the CNI conflict and install Cilium correctly on AKS.",
    r"""<span class="token comment"># ❌ BUG: Installing Cilium on AKS with Azure CNI still active</span>
helm install cilium cilium/cilium \
  --namespace kube-system

<span class="token comment"># Agents crash — network plugin conflict</span>
kubectl get pods -n kube-system -l k8s-app=cilium
<span class="token comment"># NAME           READY   STATUS             RESTARTS
# cilium-xxxxx   0/1     CrashLoopBackOff   3</span>

<span class="token comment"># Azure CNI still running</span>
kubectl get pods -n kube-system -l k8s-app=azure-cni
<span class="token comment"># NAME              READY   STATUS    RESTARTS
# azure-cni-xxxxx   1/1     Running   0</span>""",
    [
        ("pass", "<strong>1.</strong> AKS cluster running: <code>kubectl get nodes</code> → 2+ nodes Ready ✅"),
        ("pass", "<strong>2.</strong> Helm v3 available: <code>helm version</code> → OK ✅"),
        ("fail", "<strong>3.</strong> Cilium agents CrashLoop: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → <strong>CrashLoopBackOff</strong> ❌"),
        ("fail", "<strong>4.</strong> Azure CNI still active: <code>kubectl get pods -n kube-system -l k8s-app=azure-cni</code> → <strong>Running alongside Cilium</strong> ❌"),
        ("fail", "<strong>5.</strong> Cilium logs: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>\"Cannot start: another CNI plugin detected on node\"</strong> ❌"),
    ],
    [
        (1, "Check for Azure CNI DaemonSet:", "kubectl get ds -n kube-system azure-cni", "discovery", "Azure CNI DaemonSet is running — AKS clusters use Azure CNI by default for pod networking"),
        (2, "Check CNI config directory:", "kubectl exec -n kube-system ds/cilium -- ls /etc/cni/net.d/", "discovery", "/etc/cni/net.d/ contains 10-azure.conflist — Azure CNI config takes precedence over Cilium's 05-cilium.conflist"),
        (3, "Verify AKS network plugin mode:", "az aks show -g <rg> -n <cluster> --query networkProfile.networkPlugin", "discovery", "networkPlugin: azure — AKS was created with Azure CNI, not 'none' or 'cilium'"),
        (4, "Check if CNI chaining is possible:", "kubectl get cm -n kube-system cilium-config -o yaml | grep -i chain", "discovery", "CNI chaining not configured — Cilium needs to either replace Azure CNI or be configured to chain with it"),
        (5, "Root cause identified:", "Two CNI plugins (Azure CNI + Cilium) cannot both manage pod networking on the same node", "root-cause", "Only one CNI plugin can manage pod IP allocation at a time. AKS deploys Azure CNI by default. Cilium detects the existing CNI config and refuses to overwrite it. Solution: either use CNI chaining (Cilium + Azure CNI for IPAM) or recreate the AKS cluster with networkPlugin=none and let Cilium handle everything."),
    ],
    r"""<span class="token comment"># Fix 1: For new AKS clusters — create with 'none' CNI</span>
az aks create \
  --resource-group anihpj-rg \
  --name anihpj-aks \
  --network-plugin none \
  --node-count 3

<span class="token comment"># Fix 2: For existing cluster — use CNI chaining</span>
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set cni.chainingMode=generic-veth \
  --set cni.customConf=true \
  --set ipam.mode=cluster-pool \
  --set ipam.operator.clusterPoolIPv4PodCIDRList="10.0.0.0/16"

<span class="token comment"># Fix 3: Wait for Cilium and verify</span>
cilium status --wait
kubectl get pods -n kube-system -l k8s-app=cilium""",
    "Cilium Installed on AKS",
    "Cilium Running on AKS with CNI Chaining",
    'Cilium is installed with <code>cni.chainingMode=generic-veth</code>, allowing it to coexist with Azure CNI for IPAM while handling policy enforcement and observability. Or, the cluster was recreated with <code>--network-plugin none</code> and Cilium fully manages networking. All Cilium agents are healthy and <code>cilium status</code> shows all components OK.',
    ["helm install cilium → CrashLoopBackOff", "Azure CNI DaemonSet still running", "CNI config conflict in /etc/cni/net.d/", "Use CNI chaining or recreate with network-plugin=none", "Cilium agents healthy → anihpj deploys"],
    "AKS has two paths for Cilium: <strong>CNI chaining</strong> (Cilium sits on top of Azure CNI for policy/observability, Azure CNI handles IPAM) or <strong>BYOCNI</strong> (Bring Your Own CNI — create cluster with <code>--network-plugin none</code>). CNI chaining is simpler for existing clusters but limits some Cilium features (no KPR, no native routing). BYOCNI gives full Cilium capabilities but requires cluster recreation.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n kube-system -l k8s-app=cilium\n<span class="output">NAME           READY   STATUS             RESTARTS   AGE\ncilium-abcde   0/1     CrashLoopBackOff   5          3m    ← CNI conflict!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get ds -n kube-system azure-cni\n<span class="output">NAME         DESIRED   CURRENT   READY   UP-TO-DATE\nazure-cni    2         2         2       2    ← Still running!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i cni\n<span class="output">level=fatal msg="Cannot start: another CNI plugin detected" existing-plugin=azure subsys=cni</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       CNI Chaining:   generic-veth    ✅ AKS compatible!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n kube-system -l k8s-app=cilium\n<span class="output">NAME           READY   STATUS    RESTARTS   AGE\ncilium-abcde   1/1     Running   0          2m    ✅ Healthy!</span></div>',
    ]
)

# ======================== S67 ========================
s67 = sc(67,
    "Migrate from Calico to Cilium with Zero Downtime for anihpj",
    "Your anihpj production cluster runs Calico as the CNI, but you need to <strong>migrate to Cilium without downtime</strong>. Simply deleting Calico and installing Cilium causes all pods to lose networking. Your job: perform a zero-downtime CNI migration from Calico to Cilium while anihpj stays online.",
    r"""<span class="token comment"># Current state: Calico is the CNI</span>
kubectl get pods -n kube-system -l k8s-app=calico-node
<span class="token comment"># NAME                READY   STATUS    RESTARTS
# calico-node-xxxxx   1/1     Running   0</span>

<span class="token comment"># anihpj is running on Calico</span>
kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment web -n anihpj --port=80

<span class="token comment"># ❌ BUG: Naive migration = downtime</span>
kubectl delete -f calico.yaml  <span class="token comment"># Removes Calico — all pods lose networking!</span>
helm install cilium cilium/cilium -n kube-system
<span class="token comment"># Pods are broken during the gap between Calico removal and Cilium readiness</span>""",
    [
        ("pass", "<strong>1.</strong> Calico running: <code>kubectl get pods -n kube-system -l k8s-app=calico-node</code> → All Running ✅"),
        ("pass", "<strong>2.</strong> anihpj deployed on Calico: <code>kubectl get pods -n anihpj -o wide</code> → Running with Calico IPs ✅"),
        ("fail", "<strong>3.</strong> Delete Calico directly: <code>kubectl delete -f calico.yaml</code> → <strong>All pods lose IP connectivity immediately!</strong> ❌"),
        ("fail", "<strong>4.</strong> New pods fail: After Calico removal, <strong>no CNI available — kubelet cannot assign pod IPs</strong> ❌"),
        ("fail", "<strong>5.</strong> Existing pods lose networking: <strong>Calico's routes and iptables rules are removed, disrupting existing connections</strong> ❌"),
    ],
    [
        (1, "Understand the migration gap:", "Between Calico removal and Cilium readiness, there is NO CNI — kubelet cannot create new pods and existing pods lose routes", "discovery", "A naive delete-then-install creates a networking outage window — must use Cilium's migration mode"),
        (2, "Check Cilium migration tools:", "cilium upgrade --from-calico --help", "discovery", "Cilium CLI has built-in Calico migration support that imports Calico's IP pools and handles the transition safely"),
        (3, "Verify Calico IP pool configuration:", "kubectl get ippools.crd.projectcalico.org -o yaml", "discovery", "Calico IP pool CIDR must match Cilium's cluster-pool-ipv4-cidr to preserve existing pod IPs"),
        (4, "Check node taint during migration:", "kubectl describe nodes | grep -A5 Taints", "discovery", "Nodes should be cordoned one at a time during migration to drain Calico pods and let Cilium take over gracefully"),
        (5, "Root cause identified:", "Direct Calico deletion creates a CNI vacuum before Cilium is ready", "root-cause", "CNI migration requires a per-node rollout: cordon node → drain pods → switch CNI config → install Cilium → uncordon. Cilium's cilium-cli automates this with preserve-existing-ips and per-node draining to achieve zero downtime"),
    ],
    r"""<span class="token comment"># Fix: Zero-downtime migration using Cilium CLI</span>
<span class="token comment"># Step 1: Deploy Cilium alongside Calico (dual-CNI mode)</span>
cilium install \
  --set ipam.mode=cluster-pool \
  --set ipam.operator.clusterPoolIPv4PodCIDRList="<same-as-calico-cidr>" \
  --set migrate.calico.enabled=true

<span class="token comment"># Step 2: Cordon and drain each node individually</span>
for node in $(kubectl get nodes -o name); do
  kubectl cordon $node
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data --force
  <span class="token comment"># CNI switch happens during drain — Cilium takes over</span>
  kubectl uncordon $node
  sleep 30
done

<span class="token comment"># Step 3: Once all nodes migrated, remove Calico</span>
kubectl delete -f calico.yaml

<span class="token comment"># Step 4: Verify anihpj never went down</span>
kubectl get pods -n anihpj -o wide""",
    "Zero-Downtime Migration Complete",
    "anihpj Running on Cilium with Zero Downtime",
    'The migration is complete. All anihpj pods retained their IPs throughout the migration. <code>kubectl get pods -n anihpj</code> shows pods Running with the same IPs they had under Calico. <code>cilium status</code> shows all agents healthy. <strong>Zero request failures</strong> during the migration — the per-node cordon-drain-uncordon strategy prevented any outage window.',
    ["Calico is current CNI — anihpj running", "Delete Calico → all pods lose networking", "Cilium migration mode preserves existing IPs", "Per-node cordon→drain→switch→uncordon", "All nodes on Cilium → Calico removed → zero downtime"],
    "The key to zero-downtime CNI migration is <strong>per-node draining</strong>. You never delete Calico from all nodes at once. Instead: cordon one node, drain its pods (they reschedule on other Calico-managed nodes), switch that node's CNI to Cilium, uncordon. Repeat for each node. Cilium's <code>migrate.calico.enabled</code> flag ensures it configures the same pod CIDR so IPs don't change. Only after ALL nodes are on Cilium do you delete Calico.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n kube-system -l k8s-app=calico-node\n<span class="output">NAME                READY   STATUS    RESTARTS   AGE\ncalico-node-abcde   1/1     Running   0          30d    ← Current CNI</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    IP           NODE\nweb-xxx    1/1     Running   192.168.1.5  node-1\nweb-yyy    1/1     Running   192.168.2.8  node-2    ← Calico assigned IPs</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME       READY   STATUS    IP           NODE\nweb-xxx    1/1     Running   192.168.1.5  node-1\nweb-yyy    1/1     Running   192.168.2.8  node-2    ← Same IPs after migration! ✅</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n kube-system -l k8s-app=cilium\n<span class="output">NAME           READY   STATUS    RESTARTS   AGE\ncilium-abcde   1/1     Running   0          5m    ✅ Cilium now the CNI</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium status\n<span class="output">    /¯¯\\\n /¯¯\\__/¯¯\\    Cilium:         OK\n \\__/¯¯\\__/    Operator:       OK\n /¯¯\\__/¯¯\\    Hubble:         OK\n \\__/¯¯\\__/    ClusterMesh:    disabled\n    \\__/       All 2 nodes healthy — Calico migrated! ✅</span></div>',
    ]
)

# ====== Assemble and insert ======
all_scenarios = s65 + '\n\n' + s66 + '\n\n' + s67

insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 1 (S65-S67) inserted!")
else:
    print("ERROR: appendices marker not found!")
    exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)

print(f"File size: {len(html.encode('utf-8'))} bytes")
