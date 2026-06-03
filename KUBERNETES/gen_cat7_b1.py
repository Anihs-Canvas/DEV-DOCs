#!/usr/bin/env python3
"""Generate Category 7: eBPF — Batch 1: S85-S87"""
import re

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
                <div class="sc-num">🧪 SCENARIO S{n} — Category 7: eBPF</div>
                <h4>{title}</h4>
                <div class="sc-desc"><strong>The Problem:</strong> {desc}</div>
            </div>
        </div>
        <div class="sc-body">
            <div class="sc-step">
                <div class="sc-step-num deploy">1</div>
                <div class="sc-step-content">
                    <h4 class="deploy">📋 Deploy the YAML (contains the bug)</h4>
                    <div class="code-block"><div class="code-header"><span class="code-lang">BASH — copy &amp; paste into Ubuntu terminal</span><button class="copy-btn" onclick="copyToClipboard(this, 'sc-s{n}-code')">📋 Copy</button></div><pre><code id="sc-s{n}-code" class="language-bash">{deploy_code}</code></pre></div>
                </div>
            </div>
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

# ======================== S85 ========================
s85 = sc(85,
    "Inspect Cilium eBPF Programs Loaded on anihpj Node with bpftool",
    "You need to inspect the eBPF programs Cilium loaded on a node running anihpj pods, but <strong>bpftool commands return empty output</strong>. Your job: use bpftool correctly to list, dump, and analyze Cilium's eBPF programs and maps on the node.",
    r"""<span class="token comment"># Deploy anihpj on a Cilium node</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># ❌ BUG: bpftool shows nothing</span>
kubectl exec -n kube-system ds/cilium -- bpftool prog list
<span class="token comment"># (empty output — no programs listed)</span>

<span class="token comment"># Try on the node directly</span>
bpftool prog list
<span class="token comment"># (empty — bpftool needs root or CAP_BPF)</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → Running ✅"),
        ("pass", "<strong>2.</strong> anihpj pods deployed: <code>kubectl get pods -n anihpj</code> → Running ✅"),
        ("fail", "<strong>3.</strong> bpftool inside agent: <code>kubectl exec -n kube-system ds/cilium -- bpftool prog list</code> → <strong>empty — no Cilium programs listed!</strong> ❌"),
        ("fail", '<strong>4.</strong> bpftool on node: <code>bpftool prog list</code> → <strong>empty or "Operation not permitted"</strong> ❌'),
        ("fail", "<strong>5.</strong> Cannot see any BPF maps either: <code>bpftool map list</code> → <strong>no BPF maps visible</strong> ❌"),
    ],
    [
        (1, "Check if bpftool is installed on the node:", "which bpftool || apt list --installed | grep bpftool", "discovery", "bpftool not installed — it's a separate package (linux-tools-common) that must be installed explicitly"),
        (2, "Check if running with sufficient privileges:", "sudo bpftool prog list | head -5", "discovery", "With sudo, programs appear — bpftool requires CAP_BPF, CAP_SYS_ADMIN, or root to inspect kernel eBPF objects"),
        (3, "Use bpftool with proper mount namespace:", "nsenter -t $(pgrep cilium-agent) -m bpftool prog list", "discovery", "Cilium programs live in the agent's mount namespace — accessing from host namespace requires nsenter to the agent's PID"),
        (4, "List Cilium-specific programs by tag prefix:", "bpftool prog list | grep -E 'cilium|from-container|to-container|from-overlay|to-host'", "discovery", "Cilium programs are tagged with names like 'cil_from_container', 'cil_to_container', 'cil_to_overlay' — filtering reveals them"),
        (5, "Root cause identified:", "bpftool requires root/CAP_BPF and correct mount namespace", "root-cause", "eBPF programs are kernel objects protected by Linux capabilities. bpftool must run as root (or with CAP_BPF+CAP_SYS_ADMIN) to enumerate programs. On the node, use sudo. Inside Cilium agent pod, the container has these capabilities. For node-level inspection, use nsenter to the Cilium agent's PID mount namespace since eBPF filesystem (bpffs) is mounted per-namespace"),
    ],
    r"""<span class="token comment"># Fix 1: Install bpftool on the node</span>
sudo apt-get update && sudo apt-get install -y linux-tools-common linux-tools-$(uname -r)

<span class="token comment"># Fix 2: Run bpftool with sudo to list all eBPF programs</span>
sudo bpftool prog list

<span class="token comment"># Fix 3: Filter Cilium programs only</span>
sudo bpftool prog list | grep -E 'cil|from-container|to-container'

<span class="token comment"># Fix 4: Inside Cilium agent pod (already has caps)</span>
kubectl exec -n kube-system ds/cilium -- bpftool prog list

<span class="token comment"># Fix 5: From host, enter agent's namespace</span>
CILIUM_PID=$(pgrep -f cilium-agent | head -1)
sudo nsenter -t $CILIUM_PID -m bpftool prog list""",
    "bpftool Lists Cilium eBPF Programs",
    "Cilium eBPF Programs Visible with bpftool",
    'Running <code>sudo bpftool prog list</code> on the node shows all eBPF programs, including Cilium\'s datapath programs tagged with names like <code>cil_from_container</code>, <code>cil_to_container</code>, and <code>cil_to_overlay</code>. Each program shows its BPF type (sched_cls, xdp, cgroup_skb), ID, and tag hash. The anihpj pod\'s veth interface has Cilium programs attached at the TC hook.',
    ["bpftool prog list → empty", "Check: bpftool not installed", "Check: needs sudo/CAP_BPF", "Check: wrong mount namespace", "Install bpftool → sudo → nsenter → programs visible"],
    "eBPF programs are kernel objects — they are NOT visible to unprivileged users. Always use <code>sudo bpftool</code> on the host or run inside the Cilium agent pod. Cilium programs use TC (sched_cls) hooks on veth interfaces and XDP hooks on physical interfaces. Key program names: <code>cil_from_container</code> (ingress from pod), <code>cil_to_container</code> (egress to pod), <code>cil_to_overlay</code> (VXLAN/Geneve encapsulation), <code>cil_from_network</code> (from physical network).",
    [
        '<div class="cmd-output"><span class="prompt">$</span> bpftool prog list\n<span class="output">(empty — no output)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> which bpftool\n<span class="output">bpftool not found    ← Not installed!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> sudo bpftool prog list | head -10\n<span class="output">89: sched_cls  name cil_from_container  tag 6deef7357e7b4530\n        loaded_at 2025-12-16T12:00:00  uid 0\n        xlated 240B  jited 152B  memlock 4096B\n92: sched_cls  name cil_to_container   tag abc123def456\n        loaded_at 2025-12-16T12:00:00  uid 0\n        xlated 312B  jited 198B  memlock 4096B    ✅ Cilium programs visible!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> sudo bpftool prog list | grep -c cil\n<span class="output">8    ← 8 Cilium eBPF programs loaded on this node</span></div>',
    ]
)

# ======================== S86 ========================
s86 = sc(86,
    "Debug eBPF Verifier Rejecting Cilium Program on Old Kernel",
    "After upgrading Cilium on a node with kernel 5.4, <strong>the eBPF verifier rejects Cilium's programs</strong>. The Cilium agent logs show verifier errors and anihpj pods on that node lose connectivity. Your job: diagnose why the verifier rejects programs and fix the issue.",
    r"""<span class="token comment"># Node with kernel 5.4 — Cilium agent fails after upgrade</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=1

<span class="token comment"># ❌ BUG: Cilium agent logs show verifier rejection</span>
kubectl logs -n kube-system ds/cilium | grep -i verifier
<span class="token comment"># "BPF program rejected by verifier: back-edge from insn 142 to 47"
# "load program: invalid argument (possible verifier complexity issue on older kernels)"</span>

kubectl get pods -n anihpj
<span class="token comment"># web-xxx   0/1   Pending   ← No CNI for this pod!</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium agent started: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → Init:Error/Running ✅"),
        ("pass", "<strong>2.</strong> Other nodes fine: other nodes with kernel 5.10+ run Cilium OK ✅"),
        ("fail", '<strong>3.</strong> Agent logs show verifier errors: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>"BPF program rejected by verifier"</strong> ❌'),
        ("fail", "<strong>4.</strong> anihpj pods Pending on this node: <code>kubectl get pods -n anihpj -o wide</code> → <strong>Pods scheduled to bad node are stuck Pending</strong> ❌"),
        ("fail", "<strong>5.</strong> Check kernel version: <code>uname -r</code> → <strong>5.4.0 — too old for new Cilium eBPF features</strong> ❌"),
    ],
    [
        (1, "Check kernel version:", "uname -r", "discovery", "5.4.0-110-generic — Cilium v1.16 requires kernel 5.10+ for full feature set; the verifier in 5.4 has complexity limits that reject newer Cilium programs"),
        (2, "Check verifier error details:", "kubectl logs -n kube-system ds/cilium | grep -A3 'verifier'", "discovery", "back-edge from insn 142 to 47 — the program has a bounded loop, but kernel 5.4 verifier rejects ALL loops (loop support added in 5.3, improved in 5.8+)"),
        (3, "Check verifier log for complexity:", "kubectl logs -n kube-system ds/cilium | grep 'processed.*insn'", "discovery", "processed 1000000 insns (limit 1000000) — the verifier hit its complexity limit; Cilium's newer programs are larger and exceed the 5.4 verifier's state pruning limits"),
        (4, "Check if CO-RE is available:", "ls /sys/kernel/btf/vmlinux 2>/dev/null", "discovery", "BTF not available — without BTF, Cilium falls back to non-CO-RE mode which generates more complex BPF programs that the old verifier rejects"),
        (5, "Root cause identified:", "Kernel 5.4 verifier has lower complexity limits and stricter loop handling", "root-cause", "eBPF verifier limits increased significantly across kernel versions: 5.4 allows 1M processed instructions, 5.10 allows 1M with better state pruning, 5.15+ allows 1M+ with bounded loops. Cilium v1.16 programs are optimized for kernels 5.10+ and may exceed 5.4 verifier limits. Without BTF for CO-RE, the fallback programs are even more complex"),
    ],
    r"""<span class="token comment"># Fix 1: Upgrade kernel to 5.10+ (recommended for Cilium v1.16+)</span>
sudo apt-get update
sudo apt-get install -y linux-generic-hwe-22.04
sudo reboot

<span class="token comment"># Fix 2: If kernel upgrade not possible, downgrade Cilium</span>
helm upgrade cilium cilium/cilium -n kube-system \
  --version 1.15.0 \
  --reuse-values

<span class="token comment"># Fix 3: Cordon old-kernel node so anihpj pods don't schedule there</span>
kubectl cordon <old-kernel-node>
kubectl drain <old-kernel-node> --ignore-daemonsets --delete-emptydir-data

<span class="token comment"># Fix 4: Verify verifier limits after kernel upgrade</span>
cat /proc/sys/kernel/unprivileged_bpf_disabled
sysctl net.core.bpf_jit_enable=1  <span class="token comment"># Ensure JIT is enabled</span>""",
    "Verifier Accepts Cilium Programs",
    "eBPF Verifier Passes on Upgraded Kernel",
    'After upgrading to kernel 5.10+, the eBPF verifier accepts Cilium\'s programs. Agent logs show <code>BPF program loaded successfully</code> instead of verifier errors. anihpj pods on the node transition from <strong>Pending to Running</strong>. <code>bpftool prog list | grep cil</code> shows all Cilium programs loaded on the node.',
    ["Agent logs → verifier rejection", "Kernel 5.4 → verifier complexity limit hit", "No BTF → non-CO-RE programs too complex", "Upgrade kernel to 5.10+ → restart Cilium", "Verifier passes → anihpj pods Running"],
    "The eBPF verifier is a kernel component that validates BPF programs before loading. Each kernel version has different verifier capabilities. Key milestones: <strong>5.3:</strong> bounded loops, <strong>5.8:</strong> improved state pruning, <strong>5.10:</strong> 1M insn limit with BTF/CO-RE, <strong>5.15:</strong> significantly higher limits. Cilium targets 5.10+ for full functionality. The <code>cilium kernel-check</code> command validates each node against feature requirements.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -i verifier\n<span class="output">level=fatal msg="BPF program rejected by verifier" error="back-edge from insn 142 to 47" subsys=datapath-loader\nlevel=fatal msg="load program: invalid argument" error="verifier complexity limit reached"</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> uname -r\n<span class="output">5.4.0-110-generic    ← Too old for Cilium v1.16 programs</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> ls /sys/kernel/btf/vmlinux\n<span class="output">ls: cannot access \'/sys/kernel/btf/vmlinux\': No such file or directory    ← No BTF!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> uname -r\n<span class="output">5.15.0-91-generic    ✅ Kernel upgraded!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep "loaded"\n<span class="output">level=info msg="BPF program loaded successfully" program=cil_from_container\nlevel=info msg="BPF program loaded successfully" program=cil_to_container    ✅ Verifier passed!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> sudo bpftool prog list | grep cil | wc -l\n<span class="output">8    ✅ All 8 Cilium programs loaded</span></div>',
    ]
)

# ======================== S87 ========================
s87 = sc(87,
    "Dump and Analyze BPF Policy Maps for anihpj Endpoints",
    "You need to inspect Cilium's BPF policy maps to understand why anihpj traffic is being dropped, but <strong>you cannot find or dump the policy maps</strong>. Your job: locate Cilium's pinned BPF maps, dump policy entries, and correlate them with anihpj endpoint identities.",
    r"""<span class="token comment"># Deploy anihpj with a CNP that drops api→db</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true

cat > cnp-restrict.yaml << 'EOF'
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: restrict-db
  namespace: anihpj
spec:
  endpointSelector:
    matchLabels: {app: anihpj, tier: db}
  ingress:
  - fromEndpoints:
    - matchLabels: {app: anihpj, tier: web}
    toPorts:
    - ports: [{port: "5432"}]
EOF
kubectl apply -f cnp-restrict.yaml

kubectl create deployment web -n anihpj --image=nginx:alpine -l app=anihpj,tier=web
kubectl create deployment api -n anihpj --image=nginx:alpine -l app=anihpj,tier=api
kubectl create deployment db -n anihpj --image=nginx:alpine -l app=anihpj,tier=db
kubectl expose deployment db -n anihpj --port=5432

<span class="token comment"># ❌ BUG: Cannot find policy maps</span>
sudo bpftool map list | grep -i policy
<span class="token comment"># (empty — need to know map names/paths)</span>""",
    [
        ("pass", "<strong>1.</strong> CNP applied: <code>kubectl get cnp -n anihpj restrict-db</code> → exists ✅"),
        ("pass", "<strong>2.</strong> Traffic being dropped: <code>hubble observe --verdict DROPPED</code> → api→db:5432 DROPPED ✅"),
        ("fail", "<strong>3.</strong> Cannot find policy maps: <code>sudo bpftool map list | grep -i pol</code> → <strong>too many maps, need Cilium-specific paths</strong> ❌"),
        ("fail", "<strong>4.</strong> Generic bpftool map dump: <code>bpftool map dump id <id></code> → <strong>shows raw hex — unreadable without understanding Cilium's map structure</strong> ❌"),
        ("fail", "<strong>5.</strong> No correlation to identity: <strong>map entries are opaque (identity IDs, not labels) — need Cilium CLI to decode</strong> ❌"),
    ],
    [
        (1, "Locate Cilium's BPF map pins:", "ls /sys/fs/bpf/tc/globals/ | grep cilium", "discovery", "Cilium pins its BPF maps under /sys/fs/bpf/tc/globals/ — policy maps are named cilium_policy_XXXXX where XXXXX is the endpoint ID"),
        (2, "Find an anihpj endpoint ID:", "kubectl get cep -n anihpj -o json | jq '.items[0].status.id'", "discovery", "Endpoint ID 1234 — Cilium creates per-endpoint policy maps pinned with this ID"),
        (3, "Dump a specific policy map:", "sudo bpftool map dump pinned /sys/fs/bpf/tc/globals/cilium_policy_01234", "discovery", "Map entries show identity keys and policy action values (1=allow, 0=deny) — this is the ingress policy for endpoint 1234"),
        (4, "Use cilium-dbg to decode map entries:", "cilium-dbg bpf policy get 1234", "discovery", "cilium-dbg translates map entries into human-readable format: shows which identities are allowed/denied for the endpoint"),
        (5, "Root cause identified:", "BPF policy maps are pinned per-endpoint and require Cilium CLI for decoding", "root-cause", "Cilium's BPF policy maps use numeric identity IDs as keys and policy decision IDs as values. Raw bpftool dump shows hex — you need cilium-dbg or cilium endpoint list to correlate endpoint IDs with pods and cilium-dbg bpf policy get <epID> to decode the actual allow/deny rules per identity"),
    ],
    r"""<span class="token comment"># Fix 1: List Cilium endpoints and their IDs</span>
kubectl get cep -n anihpj -o custom-columns=NAME:.metadata.name,ID:.status.id,IDENTITY:.status.identity.id,IP:.status.networking.addressing[0].ipv4

<span class="token comment"># Fix 2: Use cilium-dbg to inspect policy for an endpoint</span>
cilium-dbg bpf policy get <endpoint-id>

<span class="token comment"># Fix 3: Dump the raw BPF policy map</span>
sudo bpftool map dump pinned /sys/fs/bpf/tc/globals/cilium_policy_0<endpoint-id>

<span class="token comment"># Fix 4: Correlate identity IDs with labels</span>
cilium-dbg identity list | grep -E "anihpj|reserved"

<span class="token comment"># Fix 5: Check which identities can reach an endpoint</span>
cilium-dbg bpf policy get <endpoint-id> --all""",
    "Policy Maps Dumped and Analyzed",
    "BPF Policy Maps Correlated with anihpj Endpoints",
    'Using <code>cilium-dbg bpf policy get &lt;endpoint-id&gt;</code>, the BPF policy map for the db endpoint shows <strong>identity 128 (web)</strong> is ALLOWED on port 5432 and <strong>identity 256 (api)</strong> is DENIED — matching the CNP. Raw <code>bpftool map dump</code> confirms the same entries in hex format. The policy is correctly enforced at the eBPF level.',
    ["bpftool map list → too many maps", "Find Cilium's pinned maps under /sys/fs/bpf", "Get endpoint IDs from CEP CRD", "cilium-dbg bpf policy get <epID> → decoded", "Policy map confirms CNP: web ALLOW, api DENY"],
    "Cilium pins BPF maps at <code>/sys/fs/bpf/tc/globals/</code> (for endpoint-specific maps) and <code>/sys/fs/bpf/cilium/</code> (for global maps). Key maps: <strong>cilium_policy_XXXXX</strong> (per-endpoint policy), <strong>cilium_ct4_global</strong> (conntrack), <strong>cilium_lb4_services</strong> (service load balancing), <strong>cilium_ipcache</strong> (identity↔IP mapping). Always prefer <code>cilium-dbg bpf</code> over raw bpftool — it decodes Cilium's data structures.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> sudo bpftool map list | wc -l\n<span class="output">47    ← 47 BPF maps on the node — need to filter!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> ls /sys/fs/bpf/tc/globals/ | grep cilium_policy\n<span class="output">cilium_policy_01234\ncilium_policy_01235\ncilium_policy_01236    ← Per-endpoint policy maps</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium-dbg bpf policy get 1234\n<span class="output">DIRECTION   IDENTITY   PORT/PROTO   ACTION\nIngress     128 (web)  5432/TCP     ALLOW\nIngress     256 (api)  5432/TCP     DENY      ← CNP enforced!\nIngress     0 (world)  ANY           DENY\nEgress      0 (world)  ANY           ALLOW    ✅ Policy matches CNP!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> sudo bpftool map dump pinned /sys/fs/bpf/tc/globals/cilium_policy_01234 | head -3\n<span class="output">key: 80 00 00 00  value: 01 00 00 00    ← Identity 128 = ALLOW(1)\nkey: 00 01 00 00  value: 00 00 00 00    ← Identity 256 = DENY(0)    ✅ Raw hex matches decoded output!</span></div>',
    ]
)

# ====== Insert ======
all_scenarios = s85 + '\n\n' + s86 + '\n\n' + s87
insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 1 (S85-S87) inserted!")
else:
    print("ERROR: appendices marker not found!"); exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File: {len(html.encode('utf-8')):,} bytes")
