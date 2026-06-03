#!/usr/bin/env python3
"""Generate Category 7: eBPF — Batch 2: S88-S90"""
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
        <div class="sc-header"><div class="sc-badge">S{n}</div><div class="sc-header-content"><div class="sc-num">🧪 SCENARIO S{n} — Category 7: eBPF</div><h4>{title}</h4><div class="sc-desc"><strong>The Problem:</strong> {desc}</div></div></div>
        <div class="sc-body">
            <div class="sc-step"><div class="sc-step-num deploy">1</div><div class="sc-step-content"><h4 class="deploy">📋 Deploy the YAML (contains the bug)</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-code')">📋 Copy</button></div><pre><code id="sc-s{n}-code" class="language-bash">{deploy_code}</code></pre></div></div></div>
            <div class="sc-step error-spot"><div class="sc-step-num">⚠</div><div class="sc-step-content"><h4>⚠️ Observe the Error — Spot What's Broken</h4>{ei}</div></div>
            <div class="sc-step debug-find"><div class="sc-step-num">🔍</div><div class="sc-step-content"><h4>🔍 Debug — Find the Root Cause</h4>{di}</div></div>
            <div class="sc-step"><div class="sc-step-num" style="background: linear-gradient(135deg, #d2991d, #3fb950);">🔧</div><div class="sc-step-content"><h4 style="color: #3fb950;">🔧 Fix — {fix_desc}</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH — apply the fix</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-fix')">📋 Copy</button></div><pre><code id="sc-s{n}-fix" class="language-bash">{fix_code}</code></pre></div></div></div>
            <div class="sc-step"><div class="sc-step-num answer">✓</div><div class="sc-step-content"><div class="sc-resolution"><h4>✅ Verify — {verify_short}</h4><p>{verify_detail}</p></div></div></div>
            <button class="sc-answer-toggle" onclick="toggleScenarioAnswer('sc-sa{n}')">🔍 Show Full Answer &amp; Expected Outputs</button>
            <div class="sc-answer" id="sc-sa{n}"><h5>🧠 Diagnostic Tenet (Thought Process)</h5><div class="tenet-flow">{tf}</div><p><strong>Tenet:</strong> {tenet_text}</p><h5>📟 Command Outputs — Error State (BEFORE fix)</h5>{bo}<h5>📟 Command Outputs — AFTER Fix</h5>{ao}</div>
            <div class="sc-step"><div class="sc-step-num" style="background: linear-gradient(135deg, #6e7681, #8b949e);">🧹</div><div class="sc-step-content"><h4 style="color: #8b949e;">🧹 Cleanup — Delete All Resources</h4><div class="code-block"><div class="code-header"><span class="code-lang">BASH — copy &amp; paste to clean up</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-cleanup')">📋 Copy</button></div><pre><code id="sc-s{n}-cleanup" class="language-bash"><span class="token comment"># Delete the namespace</span>
kubectl delete namespace anihpj
<span class="token comment"># Verify cleanup</span>
kubectl get all -n anihpj</code></pre></div></div></div>
        </div>
    </div>
'''

# ======================== S88 ========================
s88 = sc(88,
    "Fix eBPF Map Full Error — Max Entries Reached for anihpj",
    "Cilium agent logs show <strong>BPF map full errors</strong> and new anihpj pods cannot get network connectivity. The conntrack or policy map has reached its maximum entry limit. Your job: identify which map is full, increase its max entries, and restore anihpj connectivity.",
    r"""<span class="token comment"># Deploy many anihpj pods to fill BPF maps</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
for i in $(seq 1 100); do
  kubectl create deployment anihpj-web-$i -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
done

<span class="token comment"># ❌ BUG: New pods stuck Pending or have no network</span>
kubectl get pods -n anihpj | grep -c Running
<span class="token comment"># Only 75 Running — 25 stuck Pending or without IP</span>

kubectl logs -n kube-system ds/cilium | grep -i "map full"
<span class="token comment"># "Cannot insert entry into BPF map: map is full (max_entries reached)"</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → Running ✅"),
        ("pass", "<strong>2.</strong> 75 anihpj pods Running: <code>kubectl get pods -n anihpj | grep Running | wc -l</code> → 75 ✅"),
        ("fail", "<strong>3.</strong> 25 pods stuck: <code>kubectl get pods -n anihpj | grep -v Running</code> → <strong>Pending/CrashLoopBackOff</strong> ❌"),
        ("fail", '<strong>4.</strong> Agent logs show map full: <code>kubectl logs -n kube-system ds/cilium | grep "map full"</code> → <strong>"Cannot insert entry: map is full"</strong> ❌'),
        ("fail", '<strong>5.</strong> Check map sizes: <code>bpftool map list -j | jq \'.[] | {name, max_entries}\'</code> → <strong>conntrack map at 512K entries — full!</strong> ❌'),
    ],
    [
        (1, "Check which BPF map is full:", "kubectl logs -n kube-system ds/cilium | grep -B2 'map is full'", "discovery", "cilium_ct4_global (conntrack table) at 512K/512K entries — the default conntrack map size is insufficient for 100+ pods with active connections"),
        (2, "Check Cilium ConfigMap for map sizes:", 'kubectl get cm -n kube-system cilium-config -o yaml | grep -i \'map\\|bpf\'', "discovery", "bpf-ct-global-any-max and bpf-policy-map-max not explicitly set — using defaults (512K conntrack, 16K policy)"),
        (3, "Count current conntrack entries:", "cilium-dbg bpf ct list global | wc -l", "discovery", "512000 entries — the conntrack table is at absolute maximum; new connections cannot be tracked, so they are dropped or pods cannot get IPs"),
        (4, "Check if GC is running:", 'kubectl logs -n kube-system ds/cilium | grep -i \'garbage\\|gc\\|ct cleanup\'', "discovery", "Conntrack GC is running but the churn rate from 100 pods exceeds GC cleanup rate — entries are created faster than they are cleaned"),
        (5, "Root cause identified:", "Default BPF map sizes are too small for large-scale deployments", "root-cause", "Cilium's default BPF map sizes (512K for conntrack, 16K for policy, 64K for NAT) are sized for typical workloads. At 100+ pods with active connections, the conntrack table fills up. When a BPF map is full, Cilium cannot insert new entries — new connections fail and new pods cannot register endpoints. The fix is to increase map sizes via ConfigMap or Helm values"),
    ],
    r"""<span class="token comment"># Fix 1: Increase conntrack map size (and other maps)</span>
kubectl patch configmap -n kube-system cilium-config --type merge -p '{"data":{"bpf-ct-global-any-max":"1048576","bpf-ct-global-tcp-max":"524288","bpf-policy-map-max":"65536","bpf-nat-global-max":"524288"}}'

<span class="token comment"># Fix 2: Restart Cilium agents to recreate maps with new sizes</span>
kubectl rollout restart ds/cilium -n kube-system
kubectl rollout status ds/cilium -n kube-system --timeout=300s

<span class="token comment"># Fix 3: Verify new map sizes</span>
kubectl exec -n kube-system ds/cilium -- bpftool map list | grep -E "ct|policy|nat"

<span class="token comment"># Fix 4: If using Helm, set values permanently</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set bpf.ctGlobalAnyMax=1048576 \
  --set bpf.policyMapMax=65536""",
    "BPF Maps Resized",
    "BPF Maps Have Sufficient Capacity for 100+ Pods",
    'After increasing BPF map sizes via ConfigMap and restarting agents, the conntrack map has 1M entries (was 512K), policy map has 64K entries (was 16K). All 100 anihpj pods are Running with IPs. Agent logs show no more "map is full" errors. <code>bpftool map list</code> confirms the new max_entries values.',
    ["100 pods → 25 stuck without network", "Agent logs: map is full", "Conntrack at 512K/512K → full", "Increase bpf-ct-global-any-max to 1M", "Restart agents → all 100 pods Running"],
    "BPF maps are pre-allocated at agent startup. Key maps and recommended sizes for large clusters: <strong>Conntrack (ct)</strong> = number of active connections, <strong>Policy</strong> = number of policy rules × endpoints, <strong>NAT</strong> = number of NAT entries for services. Rule of thumb: conntrack = 10K × number of pods, policy = 1K × endpoints. All map sizes are configured via <code>bpf-*-max</code> Helm values or ConfigMap entries. Maps cannot be resized without agent restart.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep "map is full"\n<span class="output">level=error msg="Cannot insert entry into BPF map: map is full" map-name=cilium_ct4_global max_entries=524288 current=524288 subsys=ct\nlevel=error msg="Failed to create CT entry for new flow"</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj --no-headers | grep -v Running | wc -l\n<span class="output">25    ← 25 pods stuck due to full BPF maps</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n kube-system ds/cilium -- bpftool map list | grep ct\n<span class="output">123: lru_hash  name cilium_ct4_global  flags 0x0  key 20B  value 64B  max_entries 1048576  memlock 134217728B    ✅ 1M entries!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj --no-headers | grep Running | wc -l\n<span class="output">100    ✅ All pods Running!</span></div>',
    ]
)

# ======================== S89 ========================
s89 = sc(89,
    "Debug eBPF Program Not Attaching to anihpj veth Interface",
    "After creating a new anihpj pod, its veth interface has <strong>no Cilium eBPF programs attached</strong> at the TC hook. Traffic to/from this pod bypasses all Cilium policy enforcement. Your job: find why the program didn't attach and fix the attachment.",
    r"""<span class="token comment"># Deploy anihpj — one pod has no eBPF programs</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=3
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=1

<span class="token comment"># ❌ BUG: Check veth interfaces for eBPF programs</span>
POD_IP=$(kubectl get pod -n anihpj api-xxx -o jsonpath='{.status.podIP}')
VETH=$(ip link | grep -B1 "$POD_IP" | head -1 | awk -F': ' '{print $2}' | cut -d@ -f1)
tc filter show dev $VETH ingress
<span class="token comment"># (empty — no TC filter/program on ingress!)</span>

<span class="token comment"># Meanwhile, other pods have programs</span>
POD_IP2=$(kubectl get pod -n anihpj web-yyy -o jsonpath='{.status.podIP}')
VETH2=$(ip link | grep -B1 "$POD_IP2" | head -1 | awk -F': ' '{print $2}' | cut -d@ -f1)
tc filter show dev $VETH2 ingress
<span class="token comment"># filter protocol all pref 1 bpf chain 0 handle 0x1 cil_from_container    ← Attached!</span>""",
    [
        ("pass", "<strong>1.</strong> Pod Running with IP: <code>kubectl get pod -n anihpj api-xxx -o wide</code> → IP assigned ✅"),
        ("pass", "<strong>2.</strong> CiliumEndpoint exists: <code>kubectl get cep -n anihpj api-xxx</code> → ready ✅"),
        ("fail", "<strong>3.</strong> No TC programs on veth: <code>tc filter show dev vethXXXXX ingress</code> → <strong>empty — no Cilium program!</strong> ❌"),
        ("fail", "<strong>4.</strong> Policy not enforced: <code>hubble observe --from-pod api-xxx</code> → <strong>all traffic FORWARDED even when CNP should DENY</strong> ❌"),
        ("fail", '<strong>5.</strong> Cilium agent logs: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>"Failed to attach BPF program to vethXXXXX: device or resource busy"</strong> ❌'),
    ],
    [
        (1, "Check agent logs for attachment errors:", 'kubectl logs -n kube-system ds/cilium | grep -i "attach\|veth\|tc"', "discovery", "Failed to attach BPF program: device or resource busy — another program or qdisc is already attached to the veth's TC hook"),
        (2, "Check existing TC qdisc on veth:", "tc qdisc show dev vethXXXXX", "discovery", "qdisc clsact already exists but has another filter at the same priority — a leftover filter from a previous pod is blocking Cilium's attachment"),
        (3, "Check if endpoint regeneration failed:", "kubectl get cep -n anihpj api-xxx -o yaml | grep -A5 'status:'", "discovery", "Status shows 'regenerating' or 'waiting-for-identity' — endpoint regeneration is stuck, BPF programs haven't been loaded for this endpoint"),
        (4, "Check if veth is in the correct namespace:", "ip netns identify $(pgrep -f 'api-xxx')", "discovery", "Pod's network namespace is correct, but the veth's host-side interface has a stale TC configuration from a previous pod that used the same veth name (recycled)"),
        (5, "Root cause identified:", "Stale TC filter or qdisc blocking Cilium's BPF attachment", "root-cause", "TC (Traffic Control) hooks on veth interfaces are exclusive — if another program/qdisc is already attached at the same priority, Cilium cannot attach its BPF programs. This happens when: 1) a previous pod's veth was not properly cleaned up, 2) another CNI plugin left TC filters, or 3) endpoint regeneration fails and leaves partial state"),
    ],
    r"""<span class="token comment"># Fix 1: Delete the broken endpoint to force recreation</span>
kubectl delete cep -n anihpj api-xxx
kubectl delete pod -n anihpj api-xxx

<span class="token comment"># Fix 2: If veth still stuck, manually clear TC on the host interface</span>
<span class="token comment"># (run on the node hosting the pod)</span>
VETH=$(ip link | grep "<pod-ip>" -B1 | head -1 | awk -F': ' '{print $2}' | cut -d@ -f1)
sudo tc qdisc del dev $VETH clsact 2>/dev/null
sudo tc qdisc add dev $VETH clsact

<span class="token comment"># Fix 3: Restart Cilium agent to re-attach all programs</span>
kubectl delete pod -n kube-system -l k8s-app=cilium --field-selector spec.nodeName=<node-name>

<span class="token comment"># Fix 4: Verify attachment</span>
tc filter show dev $VETH ingress""",
    "eBPF Programs Attached",
    "Cilium BPF Programs Attached to veth Interface",
    'After clearing stale TC filters and restarting the pod, Cilium successfully attaches <code>cil_from_container</code> (ingress) and <code>cil_to_container</code> (egress) BPF programs to the pod\'s veth interface. <code>tc filter show dev vethXXXXX ingress</code> shows the bpf filter. <code>hubble observe</code> now correctly shows DROPPED verdicts for denied traffic.',
    ["veth has no eBPF programs → no policy", "TC filter show → empty", "Agent logs: attach failed, device busy", "Clear stale TC qdisc → restart pod", "BPF programs attached → policy enforced"],
    "Cilium attaches BPF programs to pod veth interfaces using the TC (Traffic Control) subsystem. The attachment uses a <code>clsact</code> qdisc with two hooks: <strong>ingress</strong> (for cil_from_container) and <strong>egress</strong> (for cil_to_container). If any other qdisc or filter occupies these hooks, attachment fails silently or with 'device busy'. Always check <code>tc qdisc show</code> and <code>tc filter show</code> on the veth when debugging attachment issues.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> tc filter show dev veth12345 ingress\n<span class="output">(empty — no filters/programs attached)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -A2 "Failed to attach"\n<span class="output">level=error msg="Failed to attach BPF program to veth12345" error="device or resource busy" subsys=datapath-loader\nlevel=error msg="Endpoint regeneration failed for endpoint 1234"</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> tc filter show dev veth12345 ingress\n<span class="output">filter protocol all pref 1 bpf chain 0\nfilter protocol all pref 1 bpf chain 0 handle 0x1 cil_from_container direct-action not_in_hw id 89 tag 6deef7357e7b4530    ✅ Attached!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> tc filter show dev veth12345 egress\n<span class="output">filter protocol all pref 1 bpf chain 0 handle 0x1 cil_to_container direct-action not_in_hw id 92 tag abc123def456    ✅ Both hooks have BPF programs!</span></div>',
    ]
)

# ======================== S90 ========================
s90 = sc(90,
    "Verify eBPF Host Routing Is Active for anihpj Traffic",
    "You enabled BPF Host Routing for better performance, but <strong>anihpj inter-node traffic still goes through the legacy routing stack</strong> (iptables/netfilter). Your job: verify that eBPF Host Routing is actually active and anihpj traffic bypasses iptables.",
    r"""<span class="token comment"># Enable BPF Host Routing</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set bpf.hostRouting.enabled=true \
  --set routingMode=native

<span class="token comment"># Deploy anihpj across nodes</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># ❌ BUG: Traffic still going through iptables</span>
iptables -t filter -L FORWARD -v | grep anihpj
<span class="token comment"># Shows iptables rules matching anihpj traffic — should be NONE with BPF Host Routing!</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium with BPF Host Routing configured: <code>cilium config | grep host-routing</code> → enabled ✅"),
        ("pass", "<strong>2.</strong> anihpj pods Running on multiple nodes: <code>kubectl get pods -n anihpj -o wide</code> → spread across nodes ✅"),
        ("fail", "<strong>3.</strong> iptables still has FORWARD rules: <code>iptables -t filter -L FORWARD -v | grep anihpj</code> → <strong>packets still hitting iptables!</strong> ❌"),
        ("fail", "<strong>4.</strong> Check BPF Host Routing BPF programs: <code>bpftool prog list | grep host</code> → <strong>no cil_to_host or cil_from_host programs</strong> ❌"),
        ("fail", "<strong>5.</strong> Kernel requirements not met: <code>uname -r</code> → <strong>5.4 — BPF Host Routing requires kernel 5.10+</strong> ❌"),
    ],
    [
        (1, "Check if BPF Host Routing is actually loaded:", "bpftool prog list | grep -E 'to-host|from-host'", "discovery", "No host routing BPF programs loaded — the feature requires kernel 5.10+ with specific BPF capabilities that the current kernel lacks"),
        (2, "Check kernel version:", "uname -r", "discovery", "5.4.0 — BPF Host Routing requires kernel 5.10+ for the necessary BPF helpers and map types"),
        (3, "Check Cilium agent logs for host routing:", "kubectl logs -n kube-system ds/cilium | grep -i 'host.routing\|hostrouting'", "discovery", "BPF Host Routing disabled: kernel version 5.4 does not support required BPF features — Cilium silently falls back to legacy iptables routing"),
        (4, "Verify the fallback routing mode:", "cilium config | grep -i routing", "discovery", "routing-mode: native is set but the actual data path uses iptables fallback — the kernel cannot support the bpf_redirect_neigh helper needed for BPF host routing"),
        (5, "Root cause identified:", "Kernel 5.4 lacks BPF helpers required for host routing", "root-cause", "BPF Host Routing uses the bpf_redirect_neigh() and bpf_redirect_peer() BPF helpers to bypass the host networking stack. These helpers were added in kernel 5.10. On older kernels, Cilium silently falls back to legacy routing through iptables/netfilter — the Helm value is accepted but the feature doesn't activate"),
    ],
    r"""<span class="token comment"># Fix 1: Upgrade kernel to 5.10+</span>
sudo apt-get update && sudo apt-get install -y linux-generic-hwe-22.04
sudo reboot

<span class="token comment"># Fix 2: After reboot, verify kernel and restart Cilium</span>
uname -r  <span class="token comment"># Should show 5.15+</span>
kubectl delete pod -n kube-system -l k8s-app=cilium

<span class="token comment"># Fix 3: Verify BPF Host Routing is active</span>
bpftool prog list | grep -E 'to-host|from-host'
cilium config | grep host-routing

<span class="token comment"># Fix 4: Confirm iptables bypass</span>
iptables -t filter -L FORWARD -v -w | grep -c anihpj
<span class="token comment"># Should be 0 — all routing done in BPF</span>""",
    "BPF Host Routing Active",
    "anihpj Traffic Bypasses iptables via BPF Host Routing",
    'After upgrading to kernel 5.15, BPF Host Routing is active. <code>bpftool prog list</code> shows <code>cil_to_host</code> and <code>cil_from_host</code> programs. <code>iptables -L FORWARD</code> shows zero anihpj-related rules — all inter-node anihpj traffic is routed directly via BPF, bypassing iptables/netfilter entirely.',
    ["BPF Host Routing enabled in Helm", "iptables still has FORWARD rules", "bpftool: no host routing programs loaded", "Kernel 5.4 lacks bpf_redirect_neigh", "Upgrade kernel → host routing programs loaded"],
    "BPF Host Routing is one of Cilium's most impactful performance features. It uses <code>bpf_redirect_neigh()</code> to forward packets directly from the source pod's veth to the destination pod's veth, bypassing the entire host networking stack (iptables, netfilter, routing table). This reduces latency by ~30% and increases throughput. It requires <strong>kernel 5.10+</strong> and is verified by the absence of Cilium iptables rules in the FORWARD chain.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> bpftool prog list | grep -E "to-host|from-host"\n<span class="output">(empty — no host routing BPF programs)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> iptables -t filter -L FORWARD -v | grep -c cilium\n<span class="output">12    ← Cilium iptables rules still active!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i "host.routing"\n<span class="output">level=info msg="BPF Host Routing disabled" reason="Kernel 5.4 does not support required BPF features" subsys=datapath    ← Silent fallback!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> bpftool prog list | grep -E "to-host|from-host"\n<span class="output">101: sched_cls  name cil_to_host   tag xyz789\n102: sched_cls  name cil_from_host  tag abc456    ✅ Host routing programs loaded!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> iptables -t filter -L FORWARD -v | grep -c cilium\n<span class="output">0    ✅ Zero Cilium iptables rules — all BPF!</span></div>',
    ]
)

# ====== Insert ======
all_scenarios = s88 + '\n\n' + s89 + '\n\n' + s90
insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 2 (S88-S90) inserted!")
else:
    print("ERROR"); exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File: {len(html.encode('utf-8')):,} bytes")
