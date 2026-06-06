"""Build Part 3 content — Node Runtime Deep Dive"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 3: NODE RUNTIME DEEP DIVE -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-3">
        <h2>🔍 <span class="section-num">Part 3</span> — Inside a Single Node: Runtime Deep Dive</h2>
        <div class="section-intro">
            <p>This section zooms into <strong>what actually runs on a node</strong> — the processes, the configurations, and the inner workings of kubelet, containerd, and the CNI plugin chain. Understanding the runtime is the difference between guessing and knowing when something goes wrong.</p>
            <p>We'll focus on <strong>wk-04</strong> (a standard worker node) for the process tree and configurations, then show what's different on a control plane node. Every process, every config line, and every architectural decision is explained.</p>
        </div>

        <!-- 3.1 WORKER NODE PROCESS TREE -->
        <h3 id="part-3-1">3.1 Worker Node Process Tree & Runtime State</h3>
        <div class="api-block">
            <p style="margin-bottom:12px;"><strong>wk-04</strong> (10.0.4.24) — Worker, 2 vCPU, 8 GB RAM, Ubuntu 24.04, containerd v1.7, Calico v3.28, kubelet/kube-proxy v1.31.0. Currently running <strong>~20 Pods</strong> with <strong>~30 containers</strong>.</p>

            <h4>Systemd Services — What Starts at Boot</h4>
            <table>
                <tr><th style="width:200px;">Service</th><th style="width:120px;">State</th><th>ExecStart</th></tr>
                <tr><td><code class="inline">kubelet.service</code></td><td><span class="badge b-cp">enabled, running</span></td><td><code class="inline">/usr/bin/kubelet --config=/var/lib/kubelet/config.yaml --container-runtime-endpoint=unix:///run/containerd/containerd.sock --kubeconfig=/etc/kubernetes/kubelet.conf</code></td></tr>
                <tr><td><code class="inline">containerd.service</code></td><td><span class="badge b-cp">enabled, running</span></td><td><code class="inline">/usr/bin/containerd</code></td></tr>
                <tr><td><code class="inline">sshd.service</code></td><td><span class="badge b-cp">enabled, running</span></td><td>OpenSSH daemon — remote access</td></tr>
                <tr><td><code class="inline">cron.service</code></td><td><span class="badge b-cp">enabled, running</span></td><td>Scheduled task runner</td></tr>
                <tr><td><code class="inline">systemd-journald</code></td><td><span class="badge b-cp">static, running</span></td><td>Centralized logging daemon</td></tr>
            </table>

            <div class="info">
                <strong>💡 Where is kube-proxy?</strong> Notice <code class="inline">kube-proxy</code> is NOT listed as a systemd service. It runs as a <strong>DaemonSet Pod</strong> in the <code class="inline">kube-system</code> namespace — managed by kubelet, not systemd. Same for Calico (<code class="inline">calico-node</code> DaemonSet). This is a key architectural pattern: systemd manages the node-level infrastructure (kubelet, containerd), and kubelet manages Kubernetes components (kube-proxy, CNI, DNS).
            </div>

            <h4 style="margin-top:24px;">Process Tree — Every Process on wk-04</h4>
            <div class="diagram-box">
                <div class="diagram-title">🖥 Process Tree (ps auxf) — wk-04</div>
                <div class="ascii-block">systemd (1)                                        # PID 1 — the init system
├─ containerd (890)                                # Container runtime daemon
│   ├─ containerd-shim-runc-v2 (23451)            # ─┐
│   │   └─ /pause (23452)                         #  │ Pod sandbox: kube-proxy-wk04
│   │                                              #  │ (pause container — holds
│   │                                              #  │ the network namespace)
│   ├─ containerd-shim-runc-v2 (23453)            #  │
│   │   └─ /usr/local/bin/kube-proxy (23454)      # ─┘ kube-proxy process
│   ├─ containerd-shim-runc-v2 (23500)            # ─┐
│   │   └─ /pause (23501)                         #  │ Pod sandbox: calico-node-xxxxx
│   ├─ containerd-shim-runc-v2 (23502)            #  │
│   │   └─ calico-felix (23503)                   #  │ Calico policy agent
│   ├─ containerd-shim-runc-v2 (23504)            #  │
│   │   └─ calico-bird (23505)                    # ─┘ BGP daemon
│   ├─ containerd-shim-runc-v2 (24000)            # ─┐
│   │   └─ /pause (24001)                         #  │ Pod: webapp-7d8f9c6b5-xk2lm
│   ├─ containerd-shim-runc-v2 (24002)            #  │
│   │   └─ /opt/anihpj/bin/webapp (24003)         # ─┘ anihpj webapp
│   └─ containerd-shim-runc-v2 (24100)            # ... more Pods/containers
│       └─ /pause (24101)                         # Pod sandbox
├─ kubelet (1234)                                  # Node agent
│   └─ (talks to API server — syncs Pod specs, reports node status)
├─ sshd (500)
└─ cron (600)</div>
            </div>

            <div class="highlight-box">
                <strong>🧠 The Pause Container — The Invisible Backbone:</strong> Every Pod has a <strong>pause container</strong> that does absolutely nothing except hold the Pod's <strong>network namespace</strong> open. All other containers in the Pod join the pause container's namespaces (network, IPC). This is why containers in the same Pod share <code class="inline">localhost</code> — they're in the same network namespace, owned by the pause container. If the pause container dies, the Pod's IP is released and all containers lose network connectivity. The pause container image is tiny (~300KB) and literally just calls <code class="inline">pause()</code> in an infinite loop.
            </div>

            <h4 style="margin-top:24px;">Kubelet Configuration — Fully Annotated</h4>
            <p style="color:var(--text-secondary);font-size:13px;">This is the resolved kubelet configuration at <code class="inline">/var/lib/kubelet/config.yaml</code>, generated by kubeadm from the <code class="inline">KubeletConfiguration</code> in kubeadm-config.yaml:</p>
            <pre><code class="language-yaml">apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
address: 0.0.0.0
port: 10250                                     # Kubelet API port (logs, exec, metrics)
readOnlyPort: 0                                 # Disabled for security
staticPodPath: /etc/kubernetes/manifests/       # Only used on CP nodes
clusterDNS:
  - 10.96.0.10                                  # CoreDNS ClusterIP
clusterDomain: cluster.local
containerRuntimeEndpoint: unix:///run/containerd/containerd.sock
maxPods: 110                                    # Default Pod limit per node
podCIDR: 10.244.4.0/26                          # This node's Pod CIDR (64 IPs)
cgroupDriver: systemd                           # MUST match containerd
failSwapOn: true                                # K8s requires swap OFF
serializeImagePulls: false                      # Pull images in parallel
registryPullQPS: 5                              # Rate limit image pulls
registryBurst: 10
eventRecordQPS: 50
eventBurst: 100
kubeAPIQPS: 50                                  # Rate limit API server calls
kubeAPIBurst: 100
# ══ Eviction Thresholds (when kubelet evicts Pods under pressure) ══
evictionHard:
  memory.available: "100Mi"                     # Evict if < 100MB free RAM
  nodefs.available: "10%"                       # Evict if < 10% disk
  imagefs.available: "15%"                      # Evict if < 15% image disk
  nodefs.inodesFree: "5%"                       # Evict if < 5% inodes
evictionSoft:
  memory.available: "200Mi"                     # Soft eviction at 200MB
evictionSoftGracePeriod: "2m"                   # Wait 2 mins before hard eviction
# ══ Resource Reservation (not available to Pods) ══
systemReserved:                                  # For OS daemons
  cpu: "500m"
  memory: "1Gi"
kubeReserved:                                    # For kubelet itself
  cpu: "250m"
  memory: "512Mi"
# ══ Authentication ══
authentication:
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt    # Verify client certs with this CA
  anonymous:
    enabled: false                               # No anonymous access
  webhook:
    enabled: true                                # Delegate auth to API server
# ══ Authorization ══
authorization:
  mode: Webhook                                  # Ask API server: "Is this allowed?"</code></pre>

            <h4 style="margin-top:24px;">Containerd Configuration</h4>
            <p style="color:var(--text-secondary);font-size:13px;">The container runtime config at <code class="inline">/etc/containerd/config.toml</code>. The critical setting is <code class="inline">SystemdCgroup = true</code> — without this, kubeadm refuses to proceed:</p>
            <pre><code class="language-toml">version = 2
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.9"    # The pause container image
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "runc"
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
      runtime_type = "io.containerd.runc.v2"
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
        SystemdCgroup = true                      # ★ MUST be true for kubeadm
  [plugins."io.containerd.grpc.v1.cri".registry]
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
        endpoint = ["https://mirror.gcr.io", "https://registry-1.docker.io"]</code></pre>

            <h4 style="margin-top:24px;">CNI Configuration — Calico</h4>
            <p style="color:var(--text-secondary);font-size:13px;">The CNI plugin chain at <code class="inline">/etc/cni/net.d/10-calico.conflist</code> — executed in order for every Pod created on this node:</p>
            <pre><code class="language-json">{
  "name": "k8s-pod-network",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "calico",                          # Step 1: IP allocation, veth, routes, BGP
      "ipam": { "type": "calico-ipam" },
      "policy": { "type": "k8s" }
    },
    { "type": "portmap",                         # Step 2: hostPort → podIP DNAT
      "snat": true,
      "capabilities": {"portMappings": true} },
    { "type": "bandwidth",                       # Step 3: Pod bandwidth limits (tc)
      "capabilities": {"bandwidth": true} }
  ]
}</code></pre>
        </div>

        <!-- 3.2 CP NODE DIFFERENCES -->
        <h3 id="part-3-2">3.2 Control Plane Node — What's Different</h3>
        <div class="api-block">
            <p style="margin-bottom:14px;">A control plane node like <strong>cp-01</strong> (10.0.0.10) has EVERYTHING a worker has, PLUS four static Pods that form the control plane. These Pods are defined in <code class="inline">/etc/kubernetes/manifests/</code> and run with <code class="inline">hostNetwork: true</code> — they use the node's network directly, not the Pod network.</p>

            <table>
                <tr><th style="width:60px;">#</th><th>Static Pod</th><th>Key Ports</th><th>What It Does</th></tr>
                <tr><td>1</td><td><strong>etcd</strong></td><td>:2379 (client), :2380 (peer)</td><td>Distributed key-value store. Stores ALL cluster state. Uses Raft consensus — needs 2/3 members for quorum.</td></tr>
                <tr><td>2</td><td><strong>kube-apiserver</strong></td><td>:6443 (HTTPS)</td><td>REST API frontend. Validates and processes all requests. The ONLY component that talks to etcd. Authenticates via certs/tokens; authorizes via RBAC.</td></tr>
                <tr><td>3</td><td><strong>kube-controller-manager</strong></td><td>:10257 (healthz)</td><td>Runs ALL control loops: node controller (health monitoring), replication controller (Pod counts), endpoints controller (Service endpoints), ServiceAccount controller.</td></tr>
                <tr><td>4</td><td><strong>kube-scheduler</strong></td><td>:10259 (healthz)</td><td>Watches for unassigned Pods. Selects optimal node based on resource requests, affinity/anti-affinity, taints/tolerations. Binds Pod to node via API server.</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 Static Pods vs Regular Pods — The Critical Difference:</strong> Static Pods are managed by <strong>kubelet directly</strong>, not by the API server. kubelet watches <code class="inline">/etc/kubernetes/manifests/</code> and guarantees these Pods are ALWAYS running. If you delete them via <code class="inline">kubectl delete pod</code>, kubelet immediately recreates them. To stop a static Pod, you must MOVE the manifest file out of the directory (<code class="inline">mv etcd.yaml /tmp/</code>). This is why the control plane survives API server restarts — the API server is itself a static Pod, managed by kubelet, which doesn't need the API server to function.
            </div>

            <h4>Complete etcd Static Pod Manifest (Annotated)</h4>
            <pre><code class="language-yaml">apiVersion: v1
kind: Pod
metadata:
  name: etcd
  namespace: kube-system
  labels:
    component: etcd
    tier: control-plane
spec:
  hostNetwork: true                              # Uses host's network directly
  priorityClassName: system-node-critical        # Highest priority — never evicted
  containers:
  - name: etcd
    image: registry.k8s.io/etcd:3.5.15-0
    command:
    - etcd
    - --advertise-client-urls=https://10.0.0.10:2379
    - --cert-file=/etc/kubernetes/pki/etcd/server.crt
    - --key-file=/etc/kubernetes/pki/etcd/server.key
    - --client-cert-auth=true
    - --data-dir=/var/lib/etcd
    - --initial-advertise-peer-urls=https://10.0.0.10:2380
    - --initial-cluster=cp-01=https://10.0.0.10:2380,cp-02=https://10.0.0.11:2380,cp-03=https://10.0.0.12:2380
    - --initial-cluster-state=existing           # "new" on first init
    - --listen-client-urls=https://127.0.0.1:2379,https://10.0.0.10:2379
    - --name=cp-01
    - --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
    - --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
    - --peer-client-cert-auth=true
    - --snapshot-count=10000                     # Snapshot every 10K writes
    - --quota-backend-bytes=8589934592          # 8GB max DB size
    livenessProbe:
      httpGet:
        path: /health
        port: 2381
      initialDelaySeconds: 10
      periodSeconds: 10
    volumeMounts:
    - name: etcd-data
      mountPath: /var/lib/etcd                   # Host path — persists across restarts
    - name: etcd-certs
      mountPath: /etc/kubernetes/pki/etcd
  volumes:
  - name: etcd-data
    hostPath:
      path: /var/lib/etcd
      type: DirectoryOrCreate
  - name: etcd-certs
    hostPath:
      path: /etc/kubernetes/pki/etcd
      type: DirectoryOrCreate</code></pre>

            <div class="warning">
                <strong>⚠️ Static Pod Priority:</strong> Both etcd and the API server use <code class="inline">priorityClassName: system-node-critical</code>. This is the HIGHEST priority class — the kubelet will <strong>never evict these Pods</strong>, even under extreme memory pressure. Eviction would kill the control plane, which would kill the cluster. If you see these Pods being evicted, your node is in serious trouble.
            </div>
        </div>

        <!-- 3.3 POD LIFECYCLE STATE MACHINE -->
        <h3 id="part-3-3">3.3 Pod Lifecycle — State Machine Diagram</h3>
        <div class="api-block">
            <p>Every Pod goes through this exact lifecycle. Understanding each state helps you diagnose why a Pod is stuck:</p>
            <div class="diagram-box">
                <div class="diagram-title">🔄 Pod Lifecycle State Machine</div>
                <div class="ascii-block">                    ┌─────────┐
                    │ Pending │  ← Pod accepted by API server, NOT yet running
                    └────┬────┘      Reason: Image not pulled, PVC not bound,
                         │           node taint not tolerated, resource quota
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Container│  │ PodSched-│  │   PVC    │
    │ Creating │  │  uled    │  │ Binding  │
    │ (image   │  │ (node    │  │(waiting  │
    │  pull)   │  │ assigned)│  │ for PV)  │
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
                       ▼
                 ┌─────────┐
                 │ Running │  ← All containers started, liveness probe passing
                 └────┬────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │Succeeded │ │  Failed  │ │  Crash-  │
    │(exit 0)  │ │(exit !=0)│ │ LoopBack │
    │Job done  │ │Fatal err │ │   Off    │
    └──────────┘ └──────────┘ └────┬─────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │  Evicted │  ← Node under pressure (disk/memory)
                            │ Terminat-│      Kubelet evicted the Pod
                            │   ing    │
                            └──────────┘</div>
            </div>

            <h4>Pod Conditions — What kubectl describe Shows</h4>
            <table>
                <tr><th style="width:180px;">Condition</th><th>What It Means</th><th>Troubleshooting When False</th></tr>
                <tr><td><code class="inline">PodScheduled</code></td><td>Pod has been assigned to a node</td><td>No nodes with capacity? Taints not tolerated? NodeSelector doesn't match?</td></tr>
                <tr><td><code class="inline">Initialized</code></td><td>All init containers completed successfully</td><td>Check init container logs: <code class="inline">kubectl logs &lt;pod&gt; -c &lt;init-container&gt;</code></td></tr>
                <tr><td><code class="inline">ContainersReady</code></td><td>All containers passed readiness probes</td><td>Readiness probe failing? Wrong port? App still starting up?</td></tr>
                <tr><td><code class="inline">Ready</code></td><td>Pod can receive traffic (added to Service endpoints)</td><td>Check all of the above. Readiness gates not passing?</td></tr>
                <tr><td><code class="inline">DisruptionTarget</code></td><td>Pod is being evicted (preemption or PDB)</td><td>Node under pressure? Higher priority Pod preempting? PDB violation?</td></tr>
            </table>
        </div>

        <!-- 3.4 CONTAINER RUNTIME ARCHITECTURE -->
        <h3 id="part-3-4">3.4 Container Runtime Architecture — How Containerd Runs a Pod</h3>
        <div class="api-block">
            <div class="diagram-box">
                <div class="diagram-title">🐳 Containerd Runtime Stack — From Kubelet to Container</div>
                <div class="ascii-block">┌─────────────────────────────────────────────────────────────────────────┐
│                     CONTAINERD RUNTIME STACK                             │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                     KUBELET (node agent)                     │      │
│   │  "Create Pod webapp with containers [webapp, sidecar]"       │      │
│   └──────────────────────────┬───────────────────────────────────┘      │
│                              │                                          │
│                              │ CRI gRPC (Container Runtime Interface)   │
│                              ▼                                          │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                   CONTAINERD (daemon)                        │      │
│   │  ┌──────────────────────────────────────────────────────┐   │      │
│   │  │              CRI Plugin (grpc.v1.cri)                 │   │      │
│   │  │  - Manages PodSandboxes (pause containers)            │   │      │
│   │  │  - Manages Containers (create/start/stop/remove)      │   │      │
│   │  │  - Manages Images (pull/list/remove)                  │   │      │
│   │  └──────────────────────┬───────────────────────────────┘   │      │
│   │                         │                                    │      │
│   │                         ▼                                    │      │
│   │  ┌──────────────────────────────────────────────────────┐   │      │
│   │  │            containerd-shim-runc-v2                    │   │      │
│   │  │  (one shim process per Pod — survives daemon restart) │   │      │
│   │  │                                                      │   │      │
│   │  │  Pod "webapp-7d8f":                                  │   │      │
│   │  │  ┌────────────────┐  ┌────────────────┐              │   │      │
│   │  │  │ Pause Container│  │ webapp :8080   │              │   │      │
│   │  │  │ (PID namespace │  │ (joins pause's │              │   │      │
│   │  │  │  owner)        │  │  namespaces)   │              │   │      │
│   │  │  │ PID: 24001     │  │ PID: 24003     │              │   │      │
│   │  │  └────────────────┘  └────────────────┘              │   │      │
│   │  └──────────────────────────────────────────────────────┘   │      │
│   │                                                              │      │
│   │  ┌──────────────────────┐  ┌────────────────────────────┐   │      │
│   │  │ Snapshotter          │  │ Content Store              │   │      │
│   │  │ (overlayfs layers)   │  │ (image blobs by sha256)    │   │      │
│   │  │ /var/lib/containerd/ │  │ /var/lib/containerd/       │   │      │
│   │  │ io.containerd.       │  │ io.containerd.content.     │   │      │
│   │  │ snapshotter.v1.      │  │ v1.content/                │   │      │
│   │  │ overlayfs/           │  │                            │   │      │
│   │  └──────────────────────┘  └────────────────────────────┘   │      │
│   └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
│   Key: If you restart containerd, shim processes keep running.          │
│        Containers stay alive. Only NEW container operations pause.      │
└─────────────────────────────────────────────────────────────────────────┘</div>
            </div>

            <table>
                <tr><th style="width:180px;">Component</th><th>Role</th><th>Survives containerd Restart?</th></tr>
                <tr><td><strong>containerd (daemon)</strong></td><td>gRPC server. Receives CRI requests from kubelet. Manages images, snapshots, and shim processes.</td><td>No — this IS the daemon being restarted</td></tr>
                <tr><td><strong>containerd-shim-runc-v2</strong></td><td>Per-Pod process. Manages the Pod's containers. Decouples container lifecycle from the daemon.</td><td><strong>YES</strong> — this is the key design feature. Containers keep running.</td></tr>
                <tr><td><strong>runc</strong></td><td>OCI runtime. Actually creates the container using Linux namespaces and cgroups. One-shot binary.</td><td>N/A — invoked per operation, not a daemon</td></tr>
                <tr><td><strong>Snapshotter (overlayfs)</strong></td><td>Manages container filesystem layers. Creates writable snapshots from read-only image layers.</td><td>No — but snapshots persist on disk</td></tr>
                <tr><td><strong>Content Store</strong></td><td>Stores container image blobs, content-addressed by SHA256 digest.</td><td>No — but blobs persist on disk at /var/lib/containerd/</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 Why the shim matters:</strong> The containerd-shim is the secret sauce that allows you to restart containerd without killing all containers. The shim process sits between the daemon and the container. When the daemon restarts, it reconnects to existing shims. This is critical for Kubernetes node upgrades — you can restart containerd (for a version update or config change) and running Pods keep running uninterrupted.
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-3">
        <h2>🔍 <span class="section-num">Part 3</span> — Inside a Single Node: Runtime Deep Dive</h2>
        <div class="section-intro"><p>Process trees, kubelet/containerd configs, Pod lifecycle state machine, and container runtime architecture — what actually runs on a node.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 3: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, Code blocks: {content.count("language-")}, ASCII: {content.count("ascii-block")}')
