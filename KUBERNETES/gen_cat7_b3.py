#!/usr/bin/env python3
"""Generate Category 7: eBPF — Batch 3: S91-S94"""
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

# ======================== S91 ========================
s91 = sc(91,
    "Trace eBPF Lifecycle — From Cilium Agent to Kernel Attachment",
    "You need to understand how Cilium loads an eBPF program end-to-end, but the <strong>loading process fails silently</strong> for a new anihpj pod. Your job: trace the full eBPF lifecycle from Cilium agent code to kernel BPF attachment and find where it breaks.",
    r"""<span class="token comment"># Deploy anihpj — observe BPF loading</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=1

<span class="token comment"># ❌ BUG: BPF program not loaded for new pod</span>
cilium endpoint list
<span class="token comment"># Shows endpoint 1234 but with warnings</span>

bpftool prog list | grep 1234
<span class="token comment"># (no programs associated with this endpoint)</span>

kubectl exec -n anihpj web-xxx -- wget -qO- http://1.1.1.1 2>&1
<span class="token comment"># wget: bad address — no network</span>""",
    [
        ("pass", "<strong>1.</strong> Endpoint created: <code>cilium endpoint list</code> → endpoint 1234 exists ✅"),
        ("pass", "<strong>2.</strong> Pod Running: <code>kubectl get pod -n anihpj web-xxx</code> → Running ✅"),
        ("fail", "<strong>3.</strong> No BPF programs for endpoint: <code>bpftool prog list | grep -i 1234</code> → <strong>no programs!</strong> ❌"),
        ("fail", "<strong>4.</strong> Pod has no connectivity: <code>kubectl exec web-xxx -- ping 1.1.1.1</code> → <strong>network unreachable</strong> ❌"),
        ("fail", '<strong>5.</strong> Agent logs: <code>kubectl logs -n kube-system ds/cilium | grep "endpoint 1234"</code> → <strong>"BPF compilation failed: missing BTF info for kernel"</strong> ❌'),
    ],
    [
        (1, "Check endpoint state:", "cilium endpoint list | grep 1234", "discovery", "Endpoint state: waiting-for-regeneration — the agent created the endpoint object but BPF program compilation/loading hasn't started"),
        (2, "Check agent logs for BPF compilation:", 'kubectl logs -n kube-system ds/cilium | grep "endpoint 1234"', "discovery", "BPF compilation failed: missing BTF info — the kernel doesn't have BTF enabled, and Cilium is trying to use CO-RE which requires BTF"),
        (3, "Check BTF availability:", "ls /sys/kernel/btf/vmlinux", "discovery", "BTF file missing — kernel was compiled without CONFIG_DEBUG_INFO_BTF=y; Cilium cannot compile CO-RE BPF programs without BTF type information"),
        (4, "Check if Cilium falls back to non-CO-RE:", 'kubectl logs -n kube-system ds/cilium | grep -i "co-re\|fallback\|precompile"', "discovery", "CO-RE compilation failed, but no fallback BPF template available — the Cilium image was built for CO-RE only and doesn't include pre-compiled non-CO-RE programs"),
        (5, "Root cause identified:", "Missing BTF prevents CO-RE BPF compilation and no fallback templates exist", "root-cause", "The eBPF lifecycle is: Agent receives endpoint event → generates BPF C code → compiles with clang/LLVM using CO-RE (if BTF available) → loads into kernel via bpf() syscall → verifier checks → JIT compiles → attaches to TC hook. If BTF is missing AND no pre-compiled fallback templates exist, compilation fails at step 2 and the endpoint never gets BPF programs"),
    ],
    r"""<span class="token comment"># Fix 1: Enable BTF on the kernel (requires kernel rebuild or upgrade)</span>
<span class="token comment"># Check if BTF can be enabled without rebuild:</span>
sudo apt-get install linux-headers-$(uname -r) linux-tools-$(uname -r)

<span class="token comment"># Fix 2: Use Cilium with pre-compiled non-CO-RE templates</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set bpf.precompile=enabled \
  --set enable-btf=false

<span class="token comment"># Fix 3: If kernel upgrade needed</span>
sudo apt-get install -y linux-generic-hwe-22.04
sudo reboot

<span class="token comment"># Fix 4: After enabling BTF, verify</span>
ls /sys/kernel/btf/vmlinux
kubectl delete pod -n anihpj web-xxx  <span class="token comment"># Force endpoint recreation</span>""",
    "BPF Lifecycle Complete",
    "eBPF Program Compiled and Attached for Endpoint 1234",
    'After enabling BTF or providing pre-compiled templates, the BPF lifecycle completes: <code>cil_from_container</code> and <code>cil_to_container</code> programs are compiled, loaded, verified, JIT-compiled, and attached to the pod\'s veth. <code>bpftool prog list</code> shows the programs. The pod has full network connectivity.',
    ["Endpoint created but no BPF programs", "Agent logs: BPF compilation failed", "Missing BTF → CO-RE can't compile", "Enable BTF or use pre-compiled templates", "BPF programs loaded → pod has network"],
    "The eBPF lifecycle in Cilium follows: 1) <strong>Agent detects endpoint</strong> → 2) <strong>Generates BPF C source</strong> from templates → 3) <strong>clang compiles</strong> using BTF for CO-RE → 4) <strong>bpf() syscall</strong> loads program → 5) <strong>Verifier</strong> checks safety → 6) <strong>JIT</strong> compiles to native code → 7) <strong>TC hook attachment</strong>. Break at any step and the endpoint has no networking. The most common failure is step 3: missing BTF on custom/old kernels.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> cilium endpoint list | grep 1234\n<span class="output">1234  Disabled  Disabled  0  10.0.1.50  waiting-for-regeneration    ← Stuck!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> ls /sys/kernel/btf/vmlinux\n<span class="output">ls: cannot access \'/sys/kernel/btf/vmlinux\': No such file or directory    ← No BTF!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> ls -la /sys/kernel/btf/vmlinux\n<span class="output">-r--r--r-- 1 root root 4567890 Dec 16 12:00 /sys/kernel/btf/vmlinux    ✅ BTF available!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> cilium endpoint list | grep 1234\n<span class="output">1234  Enabled  Enabled  128  10.0.1.50  ready    ✅ BPF programs loaded!</span></div>',
    ]
)

# ======================== S92 ========================
s92 = sc(92,
    "Debug CO-RE Failure on Custom Kernel for anihpj Node",
    "A node running a custom-compiled kernel (5.15-custom) has <strong>Cilium CO-RE compilation failures</strong>. anihpj pods on this node have no network. Other nodes with the same kernel version but from a standard distribution work fine. Your job: debug why CO-RE fails on the custom kernel.",
    r"""<span class="token comment"># Node with custom kernel 5.15-custom — Cilium fails</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true

<span class="token comment"># Deploy pod on problematic node</span>
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=1
kubectl get pods -n anihpj -o wide
<span class="token comment"># web-xxx   0/1   Pending    ← Stuck on custom-kernel node</span>

kubectl logs -n kube-system ds/cilium | grep -i "co-re\|btf\|compile"
<span class="token comment"># "CO-RE compilation failed: BTF type mismatch — struct sk_buff has unexpected field layout"</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium agent running: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → Running ✅"),
        ("pass", "<strong>2.</strong> BTF file exists: <code>ls /sys/kernel/btf/vmlinux</code> → file present ✅"),
        ("fail", '<strong>3.</strong> CO-RE compilation fails: <code>kubectl logs -n kube-system ds/cilium | grep "CO-RE"</code> → <strong>"BTF type mismatch"</strong> ❌'),
        ("fail", "<strong>4.</strong> anihpj pods Pending: <code>kubectl get pods -n anihpj</code> → <strong>Pending on custom-kernel node</strong> ❌"),
        ("fail", "<strong>5.</strong> Other nodes work: Standard kernel 5.15.0-91 nodes run Cilium fine — <strong>only the custom kernel fails</strong> ❌"),
    ],
    [
        (1, "Compare kernel config with standard:", "diff <(cat /boot/config-5.15-custom) <(cat /boot/config-5.15.0-91-generic) | grep -i bpf", "discovery", "CONFIG_DEBUG_INFO_BTF=y is set but CONFIG_DEBUG_INFO_BTF_MODULES=n on custom kernel — module BTF is missing, which Cilium needs for kernel module types"),
        (2, "Check BTF type integrity:", "bpftool btf dump file /sys/kernel/btf/vmlinux format raw | grep sk_buff | head -5", "discovery", "BTF dump shows sk_buff has different field offsets than expected — the custom kernel has backported patches that changed struct layouts without updating BTF"),
        (3, "Check if kernel headers match:", "ls /usr/src/linux-headers-5.15-custom", "discovery", "Kernel headers are from a different build than the running kernel — BTF was generated from a different source tree than the running kernel, causing struct layout mismatches"),
        (4, "Check Cilium CO-RE relocation errors:", 'kubectl logs -n kube-system ds/cilium | grep -A5 "CO-RE relocation"', "discovery", "Relocation #47 for sk_buff->len failed: offset 112 in BTF vs offset 108 in kernel — the custom kernel has a patched sk_buff that Cilium's CO-RE cannot reconcile"),
        (5, "Root cause identified:", "Custom kernel has BTF that doesn't match actual kernel struct layouts", "root-cause", "CO-RE (Compile Once, Run Everywhere) relies on BTF to describe kernel data structures accurately. When a custom kernel changes struct layouts (via patches) without regenerating BTF, CO-RE relocations fail because the BTF says a field is at offset X but the actual kernel has it at offset Y. This is common with vendor kernels, backported patches, and custom builds"),
    ],
    r"""<span class="token comment"># Fix 1: Regenerate BTF for the running kernel</span>
sudo pahole -J /sys/kernel/btf/vmlinux
<span class="token comment"># Or rebuild kernel with: make LLVM=1 (includes BTF generation)</span>

<span class="token comment"># Fix 2: Disable CO-RE and use pre-compiled BPF templates</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set bpf.compileOnce=false \
  --set enable-btf=false

<span class="token comment"># Fix 3: Cordon the node until BTF is fixed</span>
kubectl cordon <custom-kernel-node>
kubectl drain <custom-kernel-node> --ignore-daemonsets --delete-emptydir-data

<span class="token comment"># Fix 4: Verify BTF integrity after fix</span>
bpftool btf dump file /sys/kernel/btf/vmlinux | grep -A10 sk_buff | head -15""",
    "CO-RE Compilation Works",
    "Cilium CO-RE Compiles Successfully on Custom Kernel",
    'After regenerating BTF or switching to pre-compiled templates, Cilium compiles BPF programs without CO-RE relocation errors. Agent logs show <code>BPF program compiled and loaded successfully</code>. anihpj pods on the custom-kernel node are Running with full network connectivity.',
    ["Custom kernel → CO-RE type mismatch", "BTF present but struct layouts differ", "Kernel headers from different build", "Regenerate BTF or disable CO-RE", "BPF compiles → anihpj pods Running"],
    "CO-RE is powerful but fragile: it trusts BTF to accurately describe the running kernel. When BTF is stale (from a different build) or incomplete (missing module BTF), CO-RE relocations fail with cryptic type mismatch errors. Always regenerate BTF (<code>pahole -J</code>) after kernel rebuilds. For production, prefer <strong>distribution kernels</strong> where BTF is guaranteed to match, or use <strong>pre-compiled BPF templates</strong> as a CO-RE fallback.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep -A2 "CO-RE"\n<span class="output">level=fatal msg="CO-RE compilation failed" error="BTF type mismatch: struct sk_buff field \'len\' at offset 112, expected 108"\nlevel=fatal msg="BPF program compilation failed" subsys=datapath-loader    ← Relocation error!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> diff <(uname -r) <(ls /usr/src/linux-headers-* | cut -d- -f3-)\n<span class="output">5.15-custom vs 5.15.0-91-generic    ← Headers don\'t match running kernel!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | grep "compiled"\n<span class="output">level=info msg="BPF program compiled and loaded successfully" program=cil_from_container subsys=datapath-loader    ✅ CO-RE working!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj -o wide\n<span class="output">NAME      READY   STATUS    IP          NODE\nweb-xxx   1/1     Running   10.0.1.50   custom-kernel-node    ✅ Running on custom kernel!</span></div>',
    ]
)

# ======================== S93 ========================
s93 = sc(93,
    "Fix BPF Filesystem (bpffs) Not Mounted on anihpj Node",
    "After a node reboot, <strong>Cilium agent fails to start</strong> because the BPF filesystem (bpffs) is not mounted. All anihpj pods on this node are stuck Pending. Your job: mount bpffs and restore Cilium functionality.",
    r"""<span class="token comment"># Node rebooted — Cilium agent CrashLoopBackOff</span>
kubectl get pods -n kube-system -l k8s-app=cilium -o wide
<span class="token comment"># cilium-xxxxx   0/1   CrashLoopBackOff   10   <node-name></span>

kubectl create namespace anihpj
kubectl create deployment web -n anihpj --image=nginx:alpine
<span class="token comment"># web-xxx   0/1   Pending   ← No CNI!</span>

kubectl logs -n kube-system ds/cilium | tail -3
<span class="token comment"># "Failed to mount BPF filesystem: no such device"</span>""",
    [
        ("pass", "<strong>1.</strong> Cilium agent pod exists: <code>kubectl get pods -n kube-system -l k8s-app=cilium</code> → present ✅"),
        ("pass", "<strong>2.</strong> Node is Ready: <code>kubectl get nodes</code> → Ready ✅"),
        ("fail", "<strong>3.</strong> Agent CrashLoop: <code>kubectl get pods -n kube-system</code> → <strong>cilium-xxx CrashLoopBackOff</strong> ❌"),
        ("fail", '<strong>4.</strong> Agent logs: <code>kubectl logs -n kube-system ds/cilium</code> → <strong>"Failed to mount BPF filesystem"</strong> ❌'),
        ("fail", "<strong>5.</strong> Check bpffs: <code>mount | grep bpf</code> → <strong>(empty — bpffs not mounted!)</strong> ❌"),
    ],
    [
        (1, "Check if bpffs is mounted:", "mount | grep bpf", "discovery", "No bpffs mount — the BPF filesystem is not mounted after reboot; Cilium needs it to pin BPF maps and programs"),
        (2, "Check if bpffs support exists in kernel:", "grep bpf /proc/filesystems", "discovery", "nodev bpf — the kernel supports bpffs but it's not mounted; likely a systemd mount unit issue after reboot"),
        (3, "Check Cilium's bpffs mount path:", "ls -la /sys/fs/bpf/", "discovery", "/sys/fs/bpf exists but is empty — the directory exists but bpffs is not mounted on it; Cilium expects bpffs at /sys/fs/bpf"),
        (4, "Check systemd mount unit for bpffs:", "systemctl status sys-fs-bpf.mount", "discovery", "sys-fs-bpf.mount is inactive/failed — the systemd mount unit that mounts bpffs at boot failed or was never created"),
        (5, "Root cause identified:", "bpffs not mounted after node reboot — missing systemd mount unit", "root-cause", "bpffs (BPF filesystem) must be mounted at /sys/fs/bpf for Cilium to pin BPF maps and programs. Most distributions auto-mount it, but custom images or nodes where systemd mount units were removed will not mount bpffs after reboot. Without it, Cilium cannot persist BPF objects and the agent crashes"),
    ],
    r"""<span class="token comment"># Fix 1: Manually mount bpffs</span>
sudo mount -t bpf bpf /sys/fs/bpf
sudo mount -t bpf bpf /sys/fs/bpf -o rw,nosuid,nodev,noexec,relatime,mode=700

<span class="token comment"># Fix 2: Create systemd mount unit for persistence</span>
cat << 'EOF' | sudo tee /etc/systemd/system/sys-fs-bpf.mount
[Unit]
Description=BPF Filesystem
DefaultDependencies=no
Before=local-fs.target
ConditionPathIsMountPoint=/sys/fs/bpf

[Mount]
What=bpf
Where=/sys/fs/bpf
Type=bpf
Options=rw,nosuid,nodev,noexec,relatime,mode=700

[Install]
WantedBy=local-fs.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable sys-fs-bpf.mount
sudo systemctl start sys-fs-bpf.mount

<span class="token comment"># Fix 3: Restart Cilium agent</span>
kubectl delete pod -n kube-system -l k8s-app=cilium""",
    "bpffs Mounted",
    "Cilium Agent Running with bpffs Mounted",
    'After mounting bpffs and creating the systemd unit, <code>mount | grep bpf</code> shows bpffs at /sys/fs/bpf. Cilium agent starts successfully. <code>ls /sys/fs/bpf/tc/globals/</code> shows pinned BPF maps. anihpj pods transition from Pending to Running. The mount persists across reboots via the systemd unit.',
    ["Agent CrashLoop → bpffs not mounted", "mount | grep bpf → empty", "sys-fs-bpf.mount inactive", "Manually mount bpffs", "Create systemd unit → persistent → agent starts"],
    "bpffs is essential for Cilium — it's where BPF maps and programs are pinned for persistence across agent restarts. The path <code>/sys/fs/bpf/tc/globals/</code> contains per-endpoint policy maps, conntrack tables, and other BPF objects. Without bpffs, Cilium cannot create or access these objects. Always verify bpffs is mounted in node provisioning scripts and ensure the systemd mount unit is enabled.",
    [
        '<div class="cmd-output"><span class="prompt">$</span> mount | grep bpf\n<span class="output">(empty — no bpffs mount)</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl logs -n kube-system ds/cilium | tail -2\n<span class="output">level=fatal msg="Failed to mount BPF filesystem" error="no such device" subsys=bpf\nlevel=fatal msg="Agent initialization failed"</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> mount | grep bpf\n<span class="output">bpf on /sys/fs/bpf type bpf (rw,nosuid,nodev,noexec,relatime,mode=700)    ✅ bpffs mounted!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> kubectl get pods -n anihpj\n<span class="output">NAME      READY   STATUS    RESTARTS   AGE\nweb-xxx   1/1     Running   0          30s    ✅ Pod Running!</span></div>',
    ]
)

# ======================== S94 ========================
s94 = sc(94,
    "Analyze eBPF Overhead Impact on anihpj Throughput",
    "You notice <strong>increased latency and reduced throughput</strong> for anihpj after enabling additional Cilium features. Your job: measure the eBPF overhead per packet, identify which BPF programs add the most latency, and optimize the datapath.",
    r"""<span class="token comment"># Deploy anihpj with monitoring</span>
kubectl create namespace anihpj
kubectl label namespace anihpj io.cilium/network-policy=true
kubectl create deployment web -n anihpj --image=nginx:alpine --replicas=2
kubectl create deployment api -n anihpj --image=nginx:alpine --replicas=2
kubectl expose deployment api -n anihpj --port=80

<span class="token comment"># ❌ BUG: Throughput degradation detected</span>
kubectl exec -n anihpj web-xxx -- ab -n 10000 -c 10 http://api/
<span class="token comment"># Requests per second: 8500 (Expected: 12000+)</span>

<span class="token comment"># Check BPF program run time</span>
bpftool prog show
<span class="token comment"># Shows run_time_ns but needs root</span>""",
    [
        ("pass", "<strong>1.</strong> anihpj pods Running: <code>kubectl get pods -n anihpj</code> → All Running ✅"),
        ("pass", "<strong>2.</strong> Traffic flowing: <code>hubble observe -n anihpj</code> → FORWARDED flows ✅"),
        ("fail", "<strong>3.</strong> Throughput below baseline: <code>ab -n 10000 http://api/</code> → <strong>8500 req/s (expected 12000+)</strong> ❌"),
        ("fail", "<strong>4.</strong> BPF program run time: <code>bpftool prog show --json | jq '.[] | {name, run_time_ns}'</code> → <strong>cil_from_container: 450ns avg — too high!</strong> ❌"),
        ("fail", '<strong>5.</strong> Too many BPF programs: <code>bpftool prog list | grep cil | wc -l</code> → <strong>12 programs per pod — each adds overhead</strong> ❌'),
    ],
    [
        (1, "Measure per-program runtime:", 'bpftool prog show --json | jq \'.[] | select(.name | startswith("cil")) | {name, run_time_ns, run_cnt}\'', "discovery", "cil_from_container runs 450ns avg over 5M runs — the policy lookup in the BPF map is the bottleneck; the policy map has grown large with many identities"),
        (2, "Check policy map size and lookup time:", "cilium-dbg bpf policy get <epID> | wc -l", "discovery", "Policy map has 1500 entries — each packet must do a hash lookup across 1500 entries; larger maps = slower lookups"),
        (3, "Check if observability adds overhead:", 'bpftool prog show --json | jq \'.[] | select(.name | contains("event")) | {name, run_time_ns}\'', "discovery", "cil_perf_event_output runs 120ns avg — Hubble's per-packet event generation adds 120ns to every packet's data path"),
        (4, "Check total BPF instruction count per packet:", "bpftool prog show id 89 --pretty | grep -E 'xlated|jited'", "discovery", "cil_from_container: 480 xlated instructions, 312 jited — the program has grown to 480 BPF instructions; each instruction adds ~1-2ns of overhead"),
        (5, "Root cause identified:", "Multiple BPF features compound per-packet overhead", "root-cause", "Each Cilium BPF feature adds instructions to the data path: policy enforcement (~200 insns), conntrack (~100 insns), NAT (~50 insns), bandwidth manager (~30 insns), L7 proxy redirection (~40 insns), per-packet Hubble events (~60 insns). With all features enabled, each packet traverses 480+ BPF instructions, each adding ~1-2ns. At 12000 req/s with multiple features, this compounds to ~30% throughput reduction"),
    ],
    r"""<span class="token comment"># Fix 1: Disable per-packet Hubble events (keep flow-level observability)</span>
helm upgrade cilium cilium/cilium -n kube-system --reuse-values \
  --set hubble.eventBufferCapacity=0 \
  --set monitor-aggregation=medium

<span class="token comment"># Fix 2: Optimize policy maps by consolidating identities</span>
<span class="token comment"># Use label-based policies instead of identity-based to reduce map entries</span>

<span class="token comment"># Fix 3: Disable unused features per namespace</span>
<span class="token comment"># If L7 policies are not needed, disable Envoy proxy redirection</span>
kubectl annotate ns anihpj io.cilium.no-l7-proxy=true --overwrite

<span class="token comment"># Fix 4: Re-measure throughput</span>
kubectl exec -n anihpj web-xxx -- ab -n 10000 -c 10 http://api/

<span class="token comment"># Fix 5: Profile specific BPF programs</span>
bpftool prog show id 89 --json | jq '{name, run_time_ns, run_cnt, instructions: .xlated}'""",
    "eBPF Overhead Optimized",
    "anihpj Throughput Restored to Baseline",
    'After disabling per-packet Hubble events and optimizing policy maps, throughput returns to 12000+ req/s. <code>bpftool prog show</code> shows <code>cil_from_container</code> runtime reduced from 450ns to 280ns. BPF instruction count dropped from 480 to 350. The overhead is now within acceptable bounds for the enabled feature set.',
    ["Throughput: 8500 req/s → below baseline", "BPF program runtime: 450ns → too high", "12 programs × 480 insns = per-packet tax", "Disable per-packet events, optimize maps", "Throughput restored to 12000 req/s"],
    "eBPF overhead is real but well-understood. Each BPF instruction costs ~1-2ns on modern CPUs. A typical Cilium data path has 300-500 instructions per packet. At line rate, this translates to: <strong>500 insns × 1.5ns × 1M pps = 0.75ms of CPU per second</strong> — negligible at moderate loads. But with Hubble per-packet events, L7 proxy, and large policy maps, this can double. Key optimization: use <strong>monitor-aggregation=medium</strong> (aggregates Hubble events) and <strong>label-based policies</strong> (fewer identity entries in BPF maps).",
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj web-xxx -- ab -n 10000 -c 10 http://api/ 2>&1 | grep "Requests per second"\n<span class="output">Requests per second:    8534.21 [#/sec] (mean)    ← Degraded!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> bpftool prog show id 89 --json | jq \'.run_time_ns / .run_cnt\'\n<span class="output">452.3    ← 450ns avg per packet — too high!</span></div>',
    ],
    [
        '<div class="cmd-output"><span class="prompt">$</span> kubectl exec -n anihpj web-xxx -- ab -n 10000 -c 10 http://api/ 2>&1 | grep "Requests per second"\n<span class="output">Requests per second:    12156.78 [#/sec] (mean)    ✅ Baseline restored!</span></div>',
        '<div class="cmd-output"><span class="prompt">$</span> bpftool prog show id 89 --json | jq \'.run_time_ns / .run_cnt\'\n<span class="output">281.5    ✅ 280ns avg — 38% faster after optimization!</span></div>',
    ]
)

# ====== Insert ======
all_scenarios = s91 + '\n\n' + s92 + '\n\n' + s93 + '\n\n' + s94
insert_marker = '\n\n    <section class="chapter-section" id="appendices">'
if insert_marker in html:
    html = html.replace(insert_marker, '\n\n' + all_scenarios + insert_marker)
    print("✅ Batch 3 (S91-S94) inserted!")
else:
    print("ERROR"); exit(1)

with open('cilium-test-prep.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print(f"File: {len(html.encode('utf-8')):,} bytes")
