"""Build Part 2 content — Directory Tree"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 2: DIRECTORY TREE -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-2">
        <h2>📁 <span class="section-num">Part 2</span> — Cluster-Level Directory Tree</h2>
        <div class="section-intro">
            <p>Every file and directory on a Kubernetes node exists for a reason. This section maps out the <strong>complete filesystem</strong> for both control plane and worker nodes — what each directory contains, which component created it, and what happens if it's missing. Understanding the filesystem is essential for troubleshooting: when kubelet won't start, the first thing you check is whether <code class="inline">/etc/kubernetes/kubelet.conf</code> exists.</p>
            <p>All directories under <code class="inline">/etc/kubernetes/</code> are created by <strong>kubeadm</strong>. Most directories under <code class="inline">/var/lib/</code> are created at runtime by kubelet and containerd. Files under <code class="inline">/run/</code> are tmpfs (in-memory) and disappear on reboot.</p>
        </div>

        <!-- 2.1 CP NODE FILESYSTEM -->
        <h3 id="part-2-1">2.1 Control Plane Node — Complete Filesystem</h3>
        <div class="api-block">
            <p style="margin-bottom:12px;color:var(--text-secondary);">A control plane node like <strong>cp-01</strong> has the most complex filesystem — it hosts etcd data, all certificates, static Pod manifests, and kubeconfigs for every control plane component. Here's every directory, organized by functional area:</p>

            <!-- KEY DIRECTORIES OVERVIEW TABLE -->
            <h4>Key Directory Groups on a CP Node</h4>
            <table>
                <tr><th style="width:240px;">Directory</th><th>Purpose</th><th>Created By</th><th>If Missing...</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/manifests/</code></td><td>Static Pod manifests — kubelet watches this</td><td>kubeadm init/join</td><td>Control plane stops. etcd, apiserver, scheduler, controller-manager disappear.</td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/</code></td><td>All TLS certificates and private keys</td><td>kubeadm init certs phase</td><td>No TLS communication possible. API server won't start.</td></tr>
                <tr><td><code class="inline">/etc/kubernetes/*.conf</code></td><td>Kubeconfig files for each component</td><td>kubeadm init kubeconfig phase</td><td>Components can't authenticate to API server.</td></tr>
                <tr><td><code class="inline">/etc/systemd/system/kubelet.service.d/</code></td><td>Kubelet systemd drop-in overrides</td><td>kubeadm init/join</td><td>Kubelet starts with wrong flags — node may not register.</td></tr>
                <tr><td><code class="inline">/var/lib/kubelet/</code></td><td>Kubelet working directory & config</td><td>Kubelet at runtime</td><td>Kubelet loses Pod state. Node must re-register.</td></tr>
                <tr><td><code class="inline">/var/lib/etcd/member/</code></td><td><strong>★ etcd database</strong> — the cluster state</td><td>etcd at runtime</td><td><strong>CLUSTER AMNESIA.</strong> All objects forgotten. Restore from backup.</td></tr>
                <tr><td><code class="inline">/var/log/pods/</code> &amp; <code class="inline">/var/log/containers/</code></td><td>Pod and container logs (symlinked)</td><td>Kubelet/CRI</td><td><code class="inline">kubectl logs</code> returns empty. Debugging becomes hard.</td></tr>
                <tr><td><code class="inline">/run/containerd.sock</code></td><td>Containerd gRPC API socket</td><td>Containerd at startup</td><td>Kubelet can't create/start containers. Node shows NotReady.</td></tr>
            </table>

            <!-- FULL FILESYSTEM TREE -->
            <h4 style="margin-top:24px;">Complete Directory Tree — cp-01 (10.0.0.10)</h4>
            <div class="diagram-box">
                <div class="diagram-title">📁 CP Node Filesystem — Every File and Directory</div>
                <div class="ascii-block">/
├── 📁 etc/
│   ├── 📁 kubernetes/                          # ← kubeadm's domain
│   │   │
│   │   ├── 📁 manifests/                       # Static Pod manifests (WATCHED BY KUBELET)
│   │   │   ├── 📄 etcd.yaml                    #   etcd static Pod
│   │   │   ├── 📄 kube-apiserver.yaml          #   API server static Pod
│   │   │   ├── 📄 kube-controller-manager.yaml #   Controller manager static Pod
│   │   │   └── 📄 kube-scheduler.yaml          #   Scheduler static Pod
│   │   │   # NOTE: kubelet watches this directory. Any .yaml file added/removed
│   │   │   #       causes kubelet to create/delete the Pod. A temporary move
│   │   │   #       (mv manifest.yaml /tmp/) is how you stop a static Pod.
│   │   │
│   │   ├── 📁 pki/                             # Certificates & Keys (kubeadm-generated)
│   │   │   ├── 📄 ca.crt                       #   ★ Cluster CA cert — signs everything
│   │   │   ├── 📄 ca.key                       #   ★ Cluster CA key — PROTECT THIS
│   │   │   ├── 📄 apiserver.crt                #   API server serving cert (SANs included)
│   │   │   ├── 📄 apiserver.key                #   API server private key
│   │   │   ├── 📄 apiserver-kubelet-client.crt #   API server → kubelet client cert
│   │   │   ├── 📄 apiserver-kubelet-client.key
│   │   │   ├── 📄 apiserver-etcd-client.crt    #   API server → etcd client cert
│   │   │   ├── 📄 apiserver-etcd-client.key
│   │   │   ├── 📄 front-proxy-ca.crt           #   Front-proxy CA (aggregation layer)
│   │   │   ├── 📄 front-proxy-ca.key
│   │   │   ├── 📄 front-proxy-client.crt       #   Front-proxy client cert
│   │   │   ├── 📄 front-proxy-client.key
│   │   │   ├── 📄 sa.pub                       #   ServiceAccount public key
│   │   │   ├── 📄 sa.key                       #   ServiceAccount private key
│   │   │   ├── 📁 etcd/                        #   etcd-specific PKI (separate CA)
│   │   │   │   ├── 📄 ca.crt                   #     etcd CA
│   │   │   │   ├── 📄 ca.key                   #     etcd CA key
│   │   │   │   ├── 📄 server.crt               #     etcd server cert
│   │   │   │   ├── 📄 server.key
│   │   │   │   ├── 📄 peer.crt                 #     etcd peer cert (member-to-member)
│   │   │   │   ├── 📄 peer.key
│   │   │   │   └── 📄 healthcheck-client.crt   #     Kubelet→etcd health probe cert
│   │   │   └── 📁 temp/                        #   Temporary certs during rotation
│   │   │
│   │   ├── 📄 admin.conf                       # kubeconfig for cluster-admin (root)
│   │   ├── 📄 kubelet.conf                     # kubeconfig for kubelet → API server
│   │   ├── 📄 controller-manager.conf          # kubeconfig for controller-manager
│   │   ├── 📄 scheduler.conf                   # kubeconfig for scheduler
│   │   ├── 📄 audit-policy.yaml                # API audit policy
│   │   ├── 📄 encryption-config.yaml           # Secret encryption at rest config
│   │   └── 📄 kubeadm-config.yaml              # (saved copy of the init config)
│   │
│   ├── 📁 systemd/system/                      # systemd unit files
│   │   ├── 📄 kubelet.service                  # Kubelet systemd service
│   │   ├── 📁 kubelet.service.d/
│   │   │   └── 📄 10-kubeadm.conf              # kubeadm's kubelet drop-in override
│   │   ├── 📄 containerd.service               # Container runtime service
│   │   └── 📄 kube-proxy.service               # (not on CP — kube-proxy is a DaemonSet Pod)
│   │
│   ├── 📁 containerd/
│   │   └── 📄 config.toml                      # Containerd configuration
│   │
│   ├── 📁 cni/net.d/
│   │   └── 📄 10-calico.conflist               # Calico CNI configuration
│   │
│   └── 📁 hosts                                # /etc/hosts (node IPs for name resolution)
│
├── 📁 var/
│   ├── 📁 lib/
│   │   ├── 📁 kubelet/
│   │   │   ├── 📄 config.yaml                  # Kubelet resolved configuration
│   │   │   ├── 📁 plugins/                     # CSI & device plugin registrations
│   │   │   ├── 📁 plugins_registry/            # Plugin socket files
│   │   │   ├── 📁 pod-resources/               # PodResources API socket
│   │   │   ├── 📁 pki/                         # Kubelet's own certs (auto-rotated)
│   │   │   │   └── 📄 kubelet-server-current.pem
│   │   │   └── 📁 volumes/                     # Volume data for Pods on this node
│   │   │       └── 📁 kubernetes.io~projected/ # Projected ServiceAccount tokens
│   │   │           └── 📁 kube-api-access-xxxxx/
│   │   │               ├── 📄 ca.crt
│   │   │               ├── 📄 namespace
│   │   │               └── 📄 token            # Mounted into Pods at /var/run/secrets/...
│   │   │
│   │   ├── 📁 etcd/                            # ★ etcd DATA DIRECTORY (critical)
│   │   │   └── 📁 member/
│   │   │       ├── 📁 snap/
│   │   │       │   └── 📄 db                   # The actual keyspace (can be >1GB)
│   │   │       └── 📁 wal/
│   │   │           ├── 📄 0000000000000001-0000000000000001.wal
│   │   │           └── 📄 0.tmp                # Temporary WAL file
│   │   │
│   │   └── 📁 calico/
│   │       ├── 📄 nodename                     # "cp-01"
│   │       └── 📁 felix/                       # Calico Felix (policy agent) state
│   │
│   └── 📁 log/
│       ├── 📁 pods/                            # Pod logs (per-namespace)
│       │   └── 📁 kube-system_etcd-cp-01/
│       │       └── 📄 etcd.log
│       ├── 📁 containers/                      # Container logs (CRI format)
│       └── 📁 kubernetes/audit/                # API audit logs
│           └── 📄 audit-2026-06-06T08-00-00.log
│
├── 📁 opt/
│   ├── 📁 cni/bin/                             # CNI plugin binaries
│   │   ├── 📄 calico
│   │   ├── 📄 calico-ipam
│   │   ├── 📄 bandwidth
│   │   ├── 📄 portmap
│   │   ├── 📄 loopback
│   │   └── 📄 host-local
│   │
│   └── 📁 anihpj/                              # anihpj project files
│       ├── 📁 bin/
│       │   ├── 📄 webapp
│       │   └── 📄 worker
│       └── 📁 config/
│           ├── 📄 webapp.yaml
│           └── 📄 worker.yaml
│
├── 📁 run/                                     # Runtime files (tmpfs — gone after reboot)
│   ├── 📄 containerd.sock                      # Containerd gRPC socket
│   ├── 📄 containerd-stress.sock
│   └── 📁 kubelet/
│       └── 📄 kubelet.sock                     # Kubelet API socket
│
├── 📁 proc/sys/net/ipv4/
│   └── 📄 ip_forward = 1                       # MUST be 1 for Pod networking
│
└── 📁 root/
    ├── 📄 kubeadm-config.yaml                  # Saved copy of init config
    └── 📁 .kube/
        └── 📄 config                           # → symlink to /etc/kubernetes/admin.conf</div>
            </div>

            <!-- CRITICAL FILES EXPLAINED -->
            <h4 style="margin-top:24px;">Critical Files — What Each One Does</h4>
            <table>
                <tr><th style="width:250px;">File</th><th>What It Is</th><th>Who Reads It</th></tr>
                <tr><td><code class="inline">/etc/kubernetes/manifests/*.yaml</code></td><td>Static Pod definitions — kubelet guarantees these Pods are always running</td><td>Kubelet (watches directory via inotify)</td></tr>
                <tr><td><code class="inline">/etc/kubernetes/admin.conf</code></td><td>Cluster-admin kubeconfig — full root access to the cluster</td><td>kubectl (symlinked from ~/.kube/config)</td></tr>
                <tr><td><code class="inline">/etc/kubernetes/kubelet.conf</code></td><td>Kubeconfig for kubelet to authenticate to the API server</td><td>Kubelet</td></tr>
                <tr><td><code class="inline">/etc/kubernetes/pki/ca.crt</code></td><td>Cluster CA certificate — the root of all trust</td><td>Every component that verifies TLS certificates</td></tr>
                <tr><td><code class="inline">/etc/systemd/system/kubelet.service.d/10-kubeadm.conf</code></td><td>Kubelet flags set by kubeadm (overrides the default unit)</td><td>Systemd (when starting kubelet)</td></tr>
                <tr><td><code class="inline">/var/lib/kubelet/config.yaml</code></td><td>Kubelet's resolved configuration (merged from kubeadm config)</td><td>Kubelet (on startup)</td></tr>
                <tr><td><code class="inline">/var/lib/etcd/member/snap/db</code></td><td><strong>★ The actual etcd database file</strong> — contains all cluster state</td><td>etcd (continuously reads/writes)</td></tr>
                <tr><td><code class="inline">/run/containerd.sock</code></td><td>Containerd gRPC socket — kubelet talks to CRI through this</td><td>Kubelet (CRI client), crictl</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 The "mv trick" for static Pods:</strong> To stop a static Pod (like the API server), move its manifest out of <code class="inline">/etc/kubernetes/manifests/</code>: <code class="inline">mv kube-apiserver.yaml /tmp/</code>. Kubelet detects the removal and deletes the Pod. To restart it, move it back: <code class="inline">mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/</code>. Kubelet detects the new file and creates the Pod. This is how you restart control plane components without <code class="inline">kubectl</code> — essential when the API server itself is the component you're restarting.
            </div>
        </div>

        <!-- 2.2 WORKER NODE FILESYSTEM -->
        <h3 id="part-2-2">2.2 Worker Node — Complete Filesystem</h3>
        <div class="api-block">
            <p style="margin-bottom:12px;color:var(--text-secondary);">A worker node like <strong>wk-04</strong> is much simpler than a control plane node. It has no static Pod manifests (except on CP nodes), no etcd data, and far fewer certificates. The kubelet, containerd, and kube-proxy are the only Kubernetes components running.</p>

            <div class="diagram-box">
                <div class="diagram-title">📁 Worker Node Filesystem — wk-04 (10.0.4.24)</div>
                <div class="ascii-block">/
├── 📁 etc/
│   ├── 📁 kubernetes/                          # Much simpler than CP
│   │   ├── 📁 pki/
│   │   │   └── 📄 ca.crt                       # Cluster CA (copy — used to verify apiserver)
│   │   ├── 📄 kubelet.conf                     # kubeconfig for kubelet → API server
│   │   └── 📄 kubeadm-flags.env                # Flags set by kubeadm join
│   │
│   ├── 📁 systemd/system/
│   │   ├── 📄 kubelet.service
│   │   ├── 📁 kubelet.service.d/
│   │   │   └── 📄 10-kubeadm.conf
│   │   ├── 📄 containerd.service
│   │   └── 📄 kube-proxy.service               # (rare — usually runs as DaemonSet Pod)
│   │
│   ├── 📁 containerd/
│   │   └── 📄 config.toml
│   │
│   └── 📁 cni/net.d/
│       └── 📄 10-calico.conflist
│
├── 📁 var/
│   ├── 📁 lib/
│   │   ├── 📁 kubelet/
│   │   │   ├── 📄 config.yaml
│   │   │   ├── 📁 plugins/
│   │   │   ├── 📁 plugins_registry/
│   │   │   ├── 📁 pod-resources/
│   │   │   ├── 📁 pki/
│   │   │   │   └── 📄 kubelet-server-current.pem  # Kubelet's serving cert (rotated)
│   │   │   └── 📁 volumes/
│   │   │
│   │   ├── 📁 kube-proxy/
│   │   │   └── 📄 config.conf                  # kube-proxy configuration
│   │   │
│   │   └── 📁 containerd/                      # Container images, snapshots, shims
│   │
│   └── 📁 log/
│       ├── 📁 pods/                            # Per-Pod log files
│       └── 📁 containers/                      # Per-container CRI logs
│
├── 📁 opt/cni/bin/                             # CNI plugins
├── 📁 run/
│   ├── 📄 containerd.sock
│   └── 📁 kubelet/
│       └── 📄 kubelet.sock
│
└── 📁 proc/sys/net/ipv4/
    └── 📄 ip_forward = 1</div>
            </div>

            <h4 style="margin-top:24px;">CP vs Worker — What's Different?</h4>
            <table>
                <tr><th style="width:250px;">What</th><th style="width:150px;">CP Node</th><th style="width:150px;">Worker Node</th><th>Why</th></tr>
                <tr><td><strong>Static Pod Manifests</strong></td><td>✅ 4 files</td><td>❌ None</td><td>Only CP nodes run etcd, apiserver, scheduler, ctrl-mgr as static Pods</td></tr>
                <tr><td><strong>etcd Data</strong></td><td>✅ /var/lib/etcd/</td><td>❌ None</td><td>etcd only runs on CP nodes</td></tr>
                <tr><td><strong>PKI Directory</strong></td><td>✅ 20+ files</td><td>✅ 1 file (ca.crt)</td><td>Workers only need the CA to verify the API server's certificate</td></tr>
                <tr><td><strong>Kubeconfigs</strong></td><td>✅ 5 files</td><td>✅ 1 file (kubelet.conf)</td><td>CP nodes need kubeconfigs for scheduler, ctrl-mgr, admin. Workers only need kubelet.</td></tr>
                <tr><td><strong>kubeadm-flags.env</strong></td><td>❌ None</td><td>✅ Present</td><td>Only created by <code class="inline">kubeadm join</code> (workers join; CP nodes init or join with --control-plane)</td></tr>
                <tr><td><strong>Audit Logs</strong></td><td>✅ /var/log/kubernetes/audit/</td><td>❌ None</td><td>Only the API server generates audit logs</td></tr>
                <tr><td><strong>Container Images</strong></td><td>System images only</td><td>Application images</td><td>Workers pull and store app images; CP nodes mostly run system containers</td></tr>
            </table>

            <div class="info">
                <strong>💡 Why is the worker filesystem so much simpler?</strong> This is by design. Kubernetes follows the principle of <strong>least privilege at the filesystem level</strong>. Worker nodes don't need certificates beyond the CA — they don't serve TLS, they only verify the API server. They don't need kubeconfigs beyond the kubelet's — kube-proxy runs as a Pod and gets its config from a ConfigMap, not from a file on disk. The simpler the filesystem, the smaller the attack surface and the fewer things that can go wrong.
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-2">
        <h2>📁 <span class="section-num">Part 2</span> — Cluster-Level Directory Tree</h2>
        <div class="section-intro"><p>Complete filesystem layout for control plane and worker nodes — every file and directory created by kubeadm, with additions for anihpj applications.</p></div>
    </section>'''

html = html.replace(old, content)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Total lines: {html.count(chr(10))}')
print(f'Part 2 content: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}')
print(f'ASCII blocks: {content.count("ascii-block")}')
print('Done.')
