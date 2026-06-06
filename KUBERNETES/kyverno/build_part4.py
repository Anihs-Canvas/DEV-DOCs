"""Build Part 4 — Directory Quick Reference"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 4: DIRECTORY QUICK REFERENCE -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-4">
        <h2>📋 <span class="section-num">Part 4</span> — Key Directory Quick Reference</h2>
        <div class="section-intro">
            <p>This is the <strong>fast lookup table</strong> for every critical file and directory on a Kubernetes node. When you're troubleshooting and need to know "where is the kubelet config?" or "where are container logs stored?", start here. Grouped by functional area for quick scanning.</p>
            <p>Directories marked with <span style="color:#f85149;">★★★</span> are <strong>critical</strong> — the cluster stops functioning if they're missing. Directories marked with <span style="color:#d29922;">★★</span> are important — degraded but not fatal.</p>
        </div>

        <!-- 4.0 FULL REFERENCE TABLE -->
        <h3 id="part-4">4.0 Complete Directory Reference — Every Path Explained</h3>
        <div class="api-block">

            <!-- GROUP: Static Pods & Manifests -->
            <h4 style="margin-top:0;">📦 Static Pod Manifests (Control Plane Only)</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/manifests/</code></td><td><span style="color:#f85149;">★★★</span></td><td>Static Pod manifest directory — kubelet watches this and guarantees these Pods are always running</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">.../etcd.yaml</code></td><td><span style="color:#f85149;">★★★</span></td><td>etcd static Pod definition — the cluster database</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">.../kube-apiserver.yaml</code></td><td><span style="color:#f85149;">★★★</span></td><td>API server static Pod — the front door to the cluster</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">.../kube-controller-manager.yaml</code></td><td><span style="color:#f85149;">★★★</span></td><td>Controller manager static Pod — all control loops</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">.../kube-scheduler.yaml</code></td><td><span style="color:#f85149;">★★★</span></td><td>Scheduler static Pod — Pod placement decisions</td><td><span class="badge b-cp">CP Only</span></td></tr>
            </table>

            <!-- GROUP: Certificates & PKI -->
            <h4 style="margin-top:20px;">🔐 Certificates & PKI</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/ca.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>Cluster CA certificate — signs ALL cluster certificates</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/ca.key</code></td><td><span style="color:#f85149;">★★★</span></td><td>Cluster CA private key — PROTECT THIS FILE!</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/apiserver.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>API server serving certificate (includes certSANs)</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/apiserver-kubelet-client.crt</code></td><td><span style="color:#d29922;">★★</span></td><td>Client cert for API server to authenticate to kubelet</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/apiserver-etcd-client.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>Client cert for API server to authenticate to etcd</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/etcd/ca.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>etcd CA — separate trust domain from cluster CA</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/etcd/server.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>etcd server certificate — etcd serves TLS with this</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/etcd/peer.crt</code></td><td><span style="color:#f85149;">★★★</span></td><td>etcd peer certificate — member-to-member Raft communication</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/sa.pub</code> + <code class="inline">sa.key</code></td><td><span style="color:#d29922;">★★</span></td><td>ServiceAccount key pair — signs and verifies SA tokens</td><td><span class="badge b-cp">CP Only</span></td></tr>
            </table>

            <!-- GROUP: Kubeconfigs -->
            <h4 style="margin-top:20px;">📝 Kubeconfig Files</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/admin.conf</code></td><td><span style="color:#f85149;">★★★</span></td><td>Admin kubeconfig — cluster-admin access (what kubectl uses)</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/kubelet.conf</code></td><td><span style="color:#f85149;">★★★</span></td><td>Kubelet kubeconfig — kubelet authenticates to API server</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/controller-manager.conf</code></td><td><span style="color:#f85149;">★★★</span></td><td>Controller manager kubeconfig</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/scheduler.conf</code></td><td><span style="color:#f85149;">★★★</span></td><td>Scheduler kubeconfig</td><td><span class="badge b-cp">CP Only</span></td></tr>
            </table>

            <!-- GROUP: Systemd & Runtime -->
            <h4 style="margin-top:20px;">⚙ Systemd & Runtime Config</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/etc/systemd/system/kubelet.service</code></td><td><span style="color:#f85149;">★★★</span></td><td>Kubelet systemd unit — starts the node agent at boot</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/etc/systemd/system/kubelet.service.d/10-kubeadm.conf</code></td><td><span style="color:#d29922;">★★</span></td><td>kubeadm kubelet drop-in — overrides default kubelet flags</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/etc/systemd/system/containerd.service</code></td><td><span style="color:#f85149;">★★★</span></td><td>Containerd systemd unit — starts the container runtime</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/etc/containerd/config.toml</code></td><td><span style="color:#f85149;">★★★</span></td><td>Containerd configuration — MUST have SystemdCgroup=true</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/etc/cni/net.d/10-calico.conflist</code></td><td><span style="color:#d29922;">★★</span></td><td>Calico CNI configuration — network plugin chain</td><td><span class="badge b-wk">All K8s</span></td></tr>
            </table>

            <!-- GROUP: Runtime Data -->
            <h4 style="margin-top:20px;">💾 Runtime Data Directories</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/var/lib/kubelet/config.yaml</code></td><td><span style="color:#f85149;">★★★</span></td><td>Kubelet resolved configuration — the active kubelet config</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/lib/kubelet/pki/kubelet-server-current.pem</code></td><td><span style="color:#d29922;">★★</span></td><td>Kubelet serving cert — auto-rotated by kubelet</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/lib/kubelet/plugins/</code></td><td><span style="color:var(--text-muted);">★</span></td><td>CSI & device plugin registration sockets</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/lib/etcd/member/snap/db</code></td><td><span style="color:#f85149;">★★★</span></td><td><strong>THE etcd database file</strong> — ALL cluster state lives here</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/var/lib/etcd/member/wal/</code></td><td><span style="color:#f85149;">★★★</span></td><td>etcd Write-Ahead Logs — Raft durability guarantee</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/var/lib/kube-proxy/config.conf</code></td><td><span style="color:#d29922;">★★</span></td><td>kube-proxy configuration (iptables/ipvs mode, CIDR)</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/lib/containerd/</code></td><td><span style="color:#d29922;">★★</span></td><td>Container images, snapshots, shim state — runtime data</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/lib/calico/</code></td><td><span style="color:var(--text-muted);">★</span></td><td>Calico node data (nodename, Felix iptables state)</td><td><span class="badge b-wk">All K8s</span></td></tr>
            </table>

            <!-- GROUP: Logs -->
            <h4 style="margin-top:20px;">📜 Logs</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/var/log/pods/</code></td><td><span style="color:#d29922;">★★</span></td><td>Pod logs (per-namespace, symlinked from /var/log/containers)</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/log/containers/</code></td><td><span style="color:#d29922;">★★</span></td><td>Container logs (CRI format — what kubectl logs reads)</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/var/log/kubernetes/audit/</code></td><td><span style="color:var(--text-muted);">★</span></td><td>API audit logs — records every API request</td><td><span class="badge b-cp">CP Only</span></td></tr>
            </table>

            <!-- GROUP: Sockets & Runtime -->
            <h4 style="margin-top:20px;">🔌 Runtime Sockets</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/run/containerd.sock</code></td><td><span style="color:#f85149;">★★★</span></td><td>Containerd gRPC socket — kubelet talks to CRI through this</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/run/kubelet/kubelet.sock</code></td><td><span style="color:#d29922;">★★</span></td><td>Kubelet API socket — local diagnostics endpoint</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/opt/cni/bin/</code></td><td><span style="color:#d29922;">★★</span></td><td>CNI plugin binaries (calico, portmap, bandwidth, etc.)</td><td><span class="badge b-wk">All K8s</span></td></tr>
                <tr><td><code class="inline">/proc/sys/net/ipv4/ip_forward</code></td><td><span style="color:#f85149;">★★★</span></td><td><strong>MUST be 1</strong> — enables Pod-to-Pod networking</td><td><span class="badge b-wk">All K8s</span></td></tr>
            </table>

            <!-- GROUP: Other Configs -->
            <h4 style="margin-top:20px;">📋 Other Configuration Files</h4>
            <table>
                <tr><th style="width:280px;">Path</th><th>Criticality</th><th>Purpose</th><th>Node Type</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/audit-policy.yaml</code></td><td><span style="color:var(--text-muted);">★</span></td><td>API audit policy — defines what gets logged and at what level</td><td><span class="badge b-cp">CP Only</span></td></tr>
                <tr><td><code class="inline">/etc/kubernetes/encryption-config.yaml</code></td><td><span style="color:#d29922;">★★</span></td><td>Secret encryption at rest config — protects Secrets in etcd</td><td><span class="badge b-cp">CP Only</span></td></tr>
            </table>

            <div class="highlight-box" style="margin-top:20px;">
                <strong>🧠 How to use this reference:</strong> When <code class="inline">kubectl logs</code> returns empty, check <code class="inline">/var/log/pods/</code> and <code class="inline">/var/log/containers/</code>. When kubelet won't start, check <code class="inline">/var/lib/kubelet/config.yaml</code> and <code class="inline">/etc/kubernetes/kubelet.conf</code>. When the cluster has amnesia, check <code class="inline">/var/lib/etcd/member/snap/db</code>. When Pod networking is broken, check <code class="inline">/proc/sys/net/ipv4/ip_forward</code> is 1. This reference answers the question <strong>"where do I look?"</strong> for every common failure mode.
            </div>
        </div>

        <!-- 4.1 FILESYSTEM HEAT MAP -->
        <h3 id="part-4-1">4.1 Filesystem Heat Map — What Lives Where by Node Type</h3>
        <div class="api-block">
            <p style="margin-bottom:14px;color:var(--text-secondary);">Not every directory exists on every node type. This heat map shows which directories are present, important, or critical for each node role:</p>

            <div class="diagram-box">
                <div class="diagram-title">🔥 Filesystem Heat Map — CP vs Worker vs Frontend</div>
                <div class="ascii-block">┌──────────────────────────────┬───────────┬───────────┬───────────┐
│         DIRECTORY            │ CONTROL   │  WORKER   │ FRONTEND  │
│                              │  PLANE    │   NODE    │   NODE    │
├──────────────────────────────┼───────────┼───────────┼───────────┤
│ /etc/kubernetes/manifests/   │    ⭐⭐⭐   │     -     │     -     │
│ /etc/kubernetes/pki/         │    ⭐⭐⭐   │    ⭐     │    ⭐     │
│ /etc/kubernetes/pki/etcd/    │    ⭐⭐⭐   │     -     │     -     │
│ /etc/kubernetes/admin.conf   │    ⭐⭐⭐   │     -     │     -     │
│ /etc/kubernetes/kubelet.conf │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /etc/systemd/system/kubelet* │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /etc/containerd/config.toml  │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /etc/cni/net.d/              │    ⭐⭐    │    ⭐⭐    │     -     │
│ /var/lib/etcd/member/        │    ⭐⭐⭐   │     -     │     -     │
│ /var/lib/kubelet/            │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /var/lib/containerd/         │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /var/lib/kube-proxy/         │    ⭐     │    ⭐⭐    │     -     │
│ /var/log/pods/               │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /var/log/containers/         │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /opt/cni/bin/                │    ⭐⭐    │    ⭐⭐    │     -     │
│ /etc/nginx/                  │     -     │     -     │    ⭐⭐⭐   │
│ /run/containerd.sock         │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /run/kubelet/                │    ⭐⭐    │    ⭐⭐    │     -     │
└──────────────────────────────┴───────────┴───────────┴───────────┘</div>
            </div>

            <table style="margin-top:16px;">
                <tr><th style="width:80px;">Rating</th><th>Meaning</th><th>Example</th></tr>
                <tr><td><span style="color:#f85149;">⭐⭐⭐</span></td><td><strong>Critical</strong> — node fails its role without this</td><td><code class="inline">/var/lib/etcd/member/</code> — without etcd data, the cluster has no state</td></tr>
                <tr><td><span style="color:#d29922;">⭐⭐</span></td><td><strong>Important</strong> — degraded if missing, but node may still partially function</td><td><code class="inline">/var/log/pods/</code> — without logs, debugging is impossible but Pods still run</td></tr>
                <tr><td><span style="color:var(--text-muted);">★</span></td><td><strong>Present</strong> — helpful for specific functionality, not essential</td><td><code class="inline">/var/lib/kube-proxy/</code> — kube-proxy can operate from its ConfigMap</td></tr>
                <tr><td style="color:var(--text-muted);">—</td><td><strong>Not present</strong> — this directory does not exist on this node type</td><td>Worker nodes have no <code class="inline">/etc/kubernetes/manifests/</code></td></tr>
            </table>

            <div class="info" style="margin-top:16px;">
                <strong>💡 Key Insight from the Heat Map:</strong> The frontend node (Nginx) column is almost entirely empty — that's because <strong>frontend nodes are NOT part of the Kubernetes cluster</strong>. They run standalone Nginx with no container runtime, no kubelet, no CNI. The CP column is dense because control plane nodes run everything. The worker column has the most <span style="color:#f85149;">⭐⭐⭐</span> entries because workers are where your applications actually run.
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-4">
        <h2>📋 <span class="section-num">Part 4</span> — Key Directory Quick Reference</h2>
        <div class="section-intro"><p>Quick lookup table + filesystem heat map showing what lives where on each node type.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 4: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, ASCII: {content.count("ascii-block")}')
