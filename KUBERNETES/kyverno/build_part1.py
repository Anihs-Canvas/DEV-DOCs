"""Build Part 1: kubeadm Deep Dive content for k8s-cluster-structure.html"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 1: KUBEADM DEEP DIVE -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-1">
        <h2>🔧 <span class="section-num">Part 1</span> — kubeadm Deep Dive: How the Cluster Is Built</h2>
        <div class="section-intro">
            <p><strong>kubeadm</strong> is the official CNCF tool for bootstrapping production-ready Kubernetes clusters. It doesn't provision VMs or install an OS — it takes existing Linux machines and transforms them into a fully operational Kubernetes cluster. This section covers every phase, every certificate, every bootstrap token, and every join sequence in detail.</p>
            <p>For the <strong>anihpj-prod</strong> cluster, kubeadm v1.31.0 was used to bootstrap 3 control plane nodes and 5 worker nodes across the <code class="inline">10.0.0.0/24</code> and <code class="inline">10.0.4.0/24</code> networks. All nodes connect through an HAProxy load balancer at <code class="inline">10.0.0.100:6443</code>.</p>
        </div>

        <!-- 1.1 WHAT IS KUBEADM? -->
        <h3 id="part-1-1">1.1 What is kubeadm?</h3>
        <div class="api-block">
            <p><code class="inline">kubeadm</code> is a CLI tool that follows the principle of <strong>"do one thing well"</strong>: it bootstraps Kubernetes clusters. It does NOT manage infrastructure — you bring the Linux machines; kubeadm installs Kubernetes on them.</p>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0;">
                <div class="success">
                    <strong>✅ What kubeadm DOES</strong>
                    <ul style="margin:6px 0 0 16px;font-size:12px;">
                        <li>Generates ALL certificates (CA, apiserver, etcd, front-proxy, ServiceAccount)</li>
                        <li>Writes static Pod manifests for control plane components</li>
                        <li>Bootstraps a 3-node etcd cluster via static Pods</li>
                        <li>Starts kube-apiserver, kube-scheduler, kube-controller-manager</li>
                        <li>Generates kubeconfig files for all components</li>
                        <li>Uploads cluster config to a ConfigMap for future upgrades</li>
                        <li>Manages the bootstrap token flow for joining new nodes</li>
                        <li>Phases can be run individually for fine-grained control</li>
                    </ul>
                </div>
                <div class="error">
                    <strong>❌ What kubeadm does NOT do</strong>
                    <ul style="margin:6px 0 0 16px;font-size:12px;">
                        <li>Does NOT install kubelet, kubeadm, or kubectl (you do that via apt/yum)</li>
                        <li>Does NOT install a container runtime (containerd/CRI-O — you set that up)</li>
                        <li>Does NOT install a CNI plugin (Calico/Flannel/Cilium — applied after init)</li>
                        <li>Does NOT provision VMs or networking between nodes</li>
                        <li>Does NOT configure external load balancers for the API server</li>
                        <li>Does NOT manage certificates after initial generation (you renew them)</li>
                    </ul>
                </div>
            </div>

            <div class="highlight-box">
                <strong>🧠 Mental Model:</strong> Think of kubeadm as the <strong>"cluster assembler"</strong>. You bring the parts (Linux machines with a container runtime installed), and kubeadm assembles them into a working Kubernetes cluster. It's like IKEA for Kubernetes — kubeadm provides the instructions and the fittings, but you need to bring the furniture (the nodes).
            </div>

            <h4>kubeadm Workflow for anihpj (6 Phases)</h4>
            <div class="flow-steps">
                <div class="flow-step"><div class="step-num">Phase 1</div><div class="step-label">⚙ Pre-flight<br>All 10 nodes</div></div>
                <div class="flow-step"><div class="step-num">Phase 2</div><div class="step-label">🚀 Init<br>cp-01 only</div></div>
                <div class="flow-step"><div class="step-num">Phase 3</div><div class="step-label">🔗 Join CP<br>cp-02, cp-03</div></div>
                <div class="flow-step"><div class="step-num">Phase 4</div><div class="step-label">🔗 Join Workers<br>wk-01..05</div></div>
                <div class="flow-step"><div class="step-num">Phase 5</div><div class="step-label">🌐 Install CNI<br>Calico</div></div>
                <div class="flow-step"><div class="step-num">Phase 6</div><div class="step-label">📦 Deploy Apps<br>anihpj webapp</div></div>
            </div>

            <table style="margin-top:16px;">
                <tr><th style="width:100px;">Phase</th><th>Location</th><th>Key Actions</th></tr>
                <tr><td><strong>1. Pre-flight</strong></td><td>ALL 10 nodes</td><td>Install containerd, kubeadm, kubelet, kubectl. Configure kernel modules (overlay, br_netfilter). Set sysctls. Disable swap. Configure containerd with SystemdCgroup=true.</td></tr>
                <tr><td><strong>2. Init</strong></td><td>cp-01 only</td><td>Run <code class="inline">kubeadm init --config=kubeadm-config.yaml --upload-certs</code>. Generates all certs, starts etcd (single node), starts apiserver/scheduler/controller-manager as static Pods. Prints bootstrap token.</td></tr>
                <tr><td><strong>3. Join CP</strong></td><td>cp-02, cp-03</td><td>Run <code class="inline">kubeadm join --control-plane --certificate-key &lt;key&gt;</code>. Downloads certs from kubeadm-certs Secret. etcd joins Raft cluster. Static Pods start.</td></tr>
                <tr><td><strong>4. Join Workers</strong></td><td>wk-01..05</td><td>Run <code class="inline">kubeadm join --token &lt;token&gt;</code>. Kubelet registers with API server. Nodes appear as NotReady (no CNI yet).</td></tr>
                <tr><td><strong>5. Install CNI</strong></td><td>cp-01 (kubectl)</td><td><code class="inline">kubectl apply -f calico.yaml</code>. Calico DaemonSet starts on every node. Nodes transition NotReady → Ready. CoreDNS Pods start.</td></tr>
                <tr><td><strong>6. Deploy Apps</strong></td><td>cp-01 (kubectl)</td><td><code class="inline">kubectl apply -f anihpj-webapp.yaml</code>. Application Pods are scheduled and start running.</td></tr>
            </table>
        </div>

        <!-- 1.1a BOOTSTRAP TIMELINE -->
        <h3 id="part-1-1a">1.1a Bootstrap Timeline — Visual Overview</h3>
        <div class="api-block">
            <p style="margin-bottom:14px;color:var(--text-secondary);">Total time to bootstrap a 10-node anihpj cluster: <strong>~45 minutes</strong> from bare metal to running applications.</p>
            <div class="diagram-box">
                <div class="diagram-title">⏱ Bootstrap Timeline — 6 Phases, ~45 Minutes</div>
                <div class="ascii-block">Time ─────────────────────────────────────────────────────────────────────►
│                                                                           │
│  PHASE 1          PHASE 2       PHASE 3       PHASE 4        PHASE 5
│  PRE-FLIGHT       INIT          JOIN CP       JOIN WORKERS   CNI + APPS
│  (ALL nodes)      (cp-01)       (cp-02,03)    (wk-01..05)    (cp-01)
│                                                                           │
│  ┌────────┐      ┌────────┐    ┌────────┐    ┌────────┐     ┌────────┐   │
│  │ 10 min │ ───► │  5 min │───►│ 3 min  │───►│ 15 min │────►│ 5 min  │   │
│  │        │      │        │    │  each  │    │  total │     │        │   │
│  └────────┘      └────────┘    └────────┘    └────────┘     └────────┘   │
│      │               │              │              │              │       │
│      ▼               ▼              ▼              ▼              ▼       │
│  ┌────────┐      ┌────────┐    ┌────────┐    ┌────────┐     ┌────────┐   │
│  │Install │      │Generate│    │Download│    │Register│     │ Apply  │   │
│  │contain │      │ certs  │    │ certs  │    │  with  │     │ Calico │   │
│  │  erd   │      │ Start  │    │ Start  │    │  API   │     │  YAML  │   │
│  │Install │      │ static │    │ static │    │ server │     │ Pods   │   │
│  │kubeadm │      │ Pods   │    │ Pods   │    │ Start  │     │ get IPs│   │
│  │Config  │      │ Create │    │ Join   │    │  kube- │     │ CoreDNS│   │
│  │kernel  │      │bootstrap│   │  etcd  │    │  proxy │     │ starts │   │
│  │Disable │      │ token  │    │ Raft   │    │        │     │ Node→  │   │
│  │ swap   │      │        │    │        │    │        │     │ Ready  │   │
│  └────────┘      └────────┘    └────────┘    └────────┘     └────────┘   │
│                                                                           │
│  TOTAL TIME: ~45 minutes (for 10-node cluster)                            │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  NODE STATE TRANSITIONS DURING BOOTSTRAP:                           │  │
│  │                                                                     │  │
│  │  cp-01: [bare] → [init] → [etcd leader] → [Ready]                  │  │
│  │  cp-02: [bare] → [join CP] → [etcd follower] → [Ready]             │  │
│  │  cp-03: [bare] → [join CP] → [etcd follower] → [Ready]             │  │
│  │  wk-XX: [bare] → [join] → [NotReady] → [CNI installed] → [Ready]   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │</div>
            </div>
            <div class="info">
                <strong>💡 Why does worker join take the longest?</strong> worker join itself is fast (~30s per node), but you need to do it 5 times sequentially (or in parallel if you're confident). The real time sink is pulling container images on each worker — kube-proxy, pause, and Calico images total ~200MB. On a slow network, image pulls dominate the timeline. Pre-pulling images with <code class="inline">kubeadm config images pull</code> on each node BEFORE init cuts Phase 4 to ~2 minutes.
            </div>
        </div>

        <!-- 1.2 KUBEADM CONFIGURATION FILE -->
        <h3 id="part-1-2">1.2 The kubeadm Configuration File</h3>
        <div class="api-block">
            <p>This single YAML file — <code class="inline">~/kubeadm-config.yaml</code> on cp-01 — defines the <strong>entire cluster</strong>. After <code class="inline">kubeadm init</code>, it's uploaded to the cluster as a ConfigMap (<code class="inline">kube-system/kubeadm-config</code>) so future upgrades know exactly how the cluster was built.</p>
            <p>It has <strong>four YAML documents</strong> separated by <code class="inline">---</code>, each configuring a different part of the system:</p>

            <table>
                <tr><th style="width:200px;">Document</th><th>Kind</th><th>What It Configures</th></tr>
                <tr><td>Document 1</td><td><code class="inline">InitConfiguration</code></td><td>Node-specific: advertise address, node name, CRI socket, kubelet flags</td></tr>
                <tr><td>Document 2</td><td><code class="inline">ClusterConfiguration</code></td><td>Cluster-wide: K8s version, networking CIDRs, API server flags, etcd config, cert SANs</td></tr>
                <tr><td>Document 3</td><td><code class="inline">KubeletConfiguration</code></td><td>Kubelet behavior: cgroup driver, max pods, eviction thresholds, system reserved</td></tr>
                <tr><td>Document 4</td><td><code class="inline">KubeProxyConfiguration</code></td><td>kube-proxy mode (iptables/ipvs) and cluster CIDR</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🔑 Why is this file so important?</strong> It's the <strong>single source of truth</strong> for your cluster. If you lose this file and need to rebuild a control plane node from scratch, you'd have to reverse-engineer the configuration from running Pods. Always keep a copy in git! The anihpj team stores <code class="inline">kubeadm-config.yaml</code> in the infrastructure repo alongside the Terraform/Ansible code.
            </div>

            <h4>Full kubeadm-config.yaml (annotated)</h4>
            <pre><code class="language-yaml"># Document 1: Node-specific settings
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "10.0.0.10"     # cp-01's IP — other nodes discover the API server here
  bindPort: 6443                     # Standard HTTPS port for the API server
nodeRegistration:
  name: cp-01                        # This node's hostname
  criSocket: unix:///run/containerd/containerd.sock  # Path to container runtime socket
  kubeletExtraArgs:
  - name: cgroup-driver
    value: systemd                   # MUST match containerd's cgroup driver
---
# Document 2: Cluster-wide settings
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
kubernetesVersion: v1.31.0          # Exact version — kubeadm enforces this
controlPlaneEndpoint: "10.0.0.100:6443"  # HAProxy VIP — ALL nodes connect here, never to individual CP IPs
imageRepository: registry.k8s.io    # Official registry (use mirror for air-gapped)

# ── Networking — CRITICAL: Must match CNI plugin expectations ──
networking:
  serviceSubnet: "10.96.0.0/12"     # ClusterIP range — virtual, never assigned to interfaces
  podSubnet: "10.244.0.0/16"        # Pod IP range — must match Calico's default
  dnsDomain: "cluster.local"        # Internal DNS domain — Pods resolve as svc.cluster.local

# ── API Server — the front door to the cluster ──
apiServer:
  extraArgs:
  - name: audit-log-path             # Where API audit logs are written
    value: "/var/log/kubernetes/audit/audit.log"
  - name: enable-admission-plugins   # Security: restrict node actions, enforce Pod Security Standards
    value: "NodeRestriction,PodSecurity"
  - name: encryption-provider-config # Encrypt Secrets at rest in etcd
    value: "/etc/kubernetes/encryption-config.yaml"
  - name: service-account-issuer     # ServiceAccount token issuer URL
    value: "https://kubernetes.default.svc.cluster.local"
  certSANs:                          # Extra names in the API server's TLS certificate
  - "10.0.0.100"                     # HAProxy VIP — kubectl connects here
  - "anihpj-k8s-api.io"             # Public DNS name
  - "127.0.0.1"                      # Localhost for health checks
  - "localhost"

# ── Controller Manager ──
controllerManager:
  extraArgs:
  - name: cluster-signing-cert-file  # Used to sign kubelet client certs
    value: "/etc/kubernetes/pki/ca.crt"
  - name: cluster-signing-key-file
    value: "/etc/kubernetes/pki/ca.key"

# ── etcd — the cluster database ──
etcd:
  local:
    dataDir: "/var/lib/etcd"
    extraArgs:
      quota-backend-bytes: "8589934592"   # 8GB max database size
      auto-compaction-retention: "1"      # Compact revisions older than 1 hour
      snapshot-count: "10000"             # Trigger snapshot every 10K writes
---
# Document 3: Kubelet configuration
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd               # Must match containerd
maxPods: 110                        # Default Pod limit per node
failSwapOn: true                    # K8s requires swap OFF
clusterDNS:
- "10.96.0.10"                      # CoreDNS ClusterIP
clusterDomain: "cluster.local"
containerRuntimeEndpoint: "unix:///run/containerd/containerd.sock"
evictionHard:                        # When to evict Pods under pressure
  memory.available: "100Mi"         # Evict if less than 100MB free RAM
  nodefs.available: "10%"           # Evict if less than 10% disk
  imagefs.available: "15%"          # Evict if less than 15% image disk
systemReserved:                      # CPU/RAM set aside for OS daemons
  cpu: "500m"
  memory: "1Gi"
kubeReserved:                        # CPU/RAM set aside for kubelet itself
  cpu: "250m"
  memory: "512Mi"
---
# Document 4: kube-proxy configuration
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "iptables"                     # Can be "ipvs" for better performance at scale
clusterCIDR: "10.244.0.0/16"</code></pre>
        </div>

        <!-- 1.3 KUBEADM PHASES -->
        <h3 id="part-1-3">1.3 kubeadm Phases — What Happens Step by Step</h3>
        <div class="api-block">
            <p><code class="inline">kubeadm init</code> runs through <strong>27 phases</strong> in a specific order. Each phase can be run individually for troubleshooting — if one phase fails, you can fix the issue and re-run just that phase without starting over.</p>
            <div class="info">
                <strong>💡 Pro Tip:</strong> Use <code class="inline">kubeadm init --dry-run --config=kubeadm-config.yaml</code> to see exactly what kubeadm WOULD do, without making any changes. To run a single phase: <code class="inline">kubeadm init phase certs apiserver --config=kubeadm-config.yaml</code>.
            </div>
            <table>
                <tr><th style="width:200px;">Phase</th><th>Category</th><th>What It Does</th></tr>
                <tr><td><code class="inline">preflight</code></td><td>Validation</td><td>Checks root access, kernel cgroups v2, container runtime socket, port availability (6443, 10250, 10259, 10257, 2379, 2380), kubelet version, swap disabled, /proc/sys/net settings</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">certs/ca</code></td><td>Certificate</td><td>Generates self-signed Cluster CA certificate + key (10-year validity)</td></tr>
                <tr><td><code class="inline">certs/apiserver</code></td><td>Certificate</td><td>Generates API server cert (signed by CA) — includes certSANs</td></tr>
                <tr><td><code class="inline">certs/apiserver-kubelet-client</code></td><td>Certificate</td><td>Client cert for API server to authenticate to kubelet</td></tr>
                <tr><td><code class="inline">certs/front-proxy-ca</code></td><td>Certificate</td><td>Generates front-proxy CA (for API aggregation layer)</td></tr>
                <tr><td><code class="inline">certs/front-proxy-client</code></td><td>Certificate</td><td>Front-proxy client cert for aggregating other API servers</td></tr>
                <tr><td><code class="inline">certs/etcd-ca</code></td><td>Certificate</td><td>Generates separate etcd CA (isolated trust from cluster CA)</td></tr>
                <tr><td><code class="inline">certs/etcd-server</code></td><td>Certificate</td><td>etcd server cert — used by etcd for client TLS</td></tr>
                <tr><td><code class="inline">certs/etcd-peer</code></td><td>Certificate</td><td>etcd peer cert — used for etcd-to-etcd member communication</td></tr>
                <tr><td><code class="inline">certs/etcd-healthcheck-client</code></td><td>Certificate</td><td>Client cert for kubelet to health-check etcd</td></tr>
                <tr><td><code class="inline">certs/apiserver-etcd-client</code></td><td>Certificate</td><td>Client cert for API server to authenticate to etcd</td></tr>
                <tr><td><code class="inline">certs/sa</code></td><td>Certificate</td><td>Generates ServiceAccount public/private key pair — used to sign and verify SA tokens</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">kubeconfig/admin</code></td><td>Kubeconfig</td><td>Generates admin.conf (cluster-admin access — what kubectl uses)</td></tr>
                <tr><td><code class="inline">kubeconfig/kubelet</code></td><td>Kubeconfig</td><td>Generates bootstrap kubeconfig for kubelet</td></tr>
                <tr><td><code class="inline">kubeconfig/controller-manager</code></td><td>Kubeconfig</td><td>Generates kubeconfig for controller-manager</td></tr>
                <tr><td><code class="inline">kubeconfig/scheduler</code></td><td>Kubeconfig</td><td>Generates kubeconfig for scheduler</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">control-plane/apiserver</code></td><td>Manifest</td><td>Writes /etc/kubernetes/manifests/kube-apiserver.yaml (static Pod)</td></tr>
                <tr><td><code class="inline">control-plane/controller-manager</code></td><td>Manifest</td><td>Writes kube-controller-manager.yaml (static Pod)</td></tr>
                <tr><td><code class="inline">control-plane/scheduler</code></td><td>Manifest</td><td>Writes kube-scheduler.yaml (static Pod)</td></tr>
                <tr><td><code class="inline">etcd/local</code></td><td>Manifest</td><td>Writes etcd.yaml + creates /var/lib/etcd data directory</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">upload-config/kubeadm</code></td><td>Upload</td><td>Uploads ClusterConfiguration to ConfigMap kube-system/kubeadm-config</td></tr>
                <tr><td><code class="inline">upload-config/kubelet</code></td><td>Upload</td><td>Uploads KubeletConfiguration to ConfigMap kube-system/kubelet-config</td></tr>
                <tr><td><code class="inline">upload-certs</code></td><td>Upload</td><td>Uploads certificates as an encrypted Secret (for other CP nodes to download)</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">mark-control-plane</code></td><td>Label</td><td>Adds label node-role.kubernetes.io/control-plane and taint to cp-01</td></tr>
                <tr><td><code class="inline">bootstrap-token</code></td><td>Token</td><td>Creates bootstrap token + Secret for other nodes to join</td></tr>
                <tr><td><code class="inline">kubelet-finalize</code></td><td>Finalize</td><td>Updates kubelet.conf with final certificate after API server is running</td></tr>
                <tr style="border-top:1px solid var(--border-color);"><td><code class="inline">addon/kube-proxy</code></td><td>Addon</td><td>Creates kube-proxy DaemonSet (runs on every node)</td></tr>
                <tr><td><code class="inline">addon/coredns</code></td><td>Addon</td><td>Creates CoreDNS Deployment (Pods stay Pending until CNI is installed)</td></tr>
            </table>
        </div>

        <!-- 1.3a PHASE DEPENDENCY TREE -->
        <h3 id="part-1-3a">1.3a Phase Dependency Tree</h3>
        <div class="api-block">
            <p>Phases depend on each other. If a parent phase fails, all children are skipped. Understanding these dependencies helps you troubleshoot init failures:</p>
            <div class="diagram-box">
                <div class="diagram-title">🌳 kubeadm Phase Dependency Tree</div>
                <div class="ascii-block">                          ┌─────────────┐
                          │  preflight  │  ← Must pass or init aborts
                          └──────┬──────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │ certs/ca │      │kubeconfig│      │  etcd    │
        │ (gen CA) │      │  /admin  │      │ /local   │
        └────┬─────┘      └────┬─────┘      └────┬─────┘
             │                 │                  │
    ┌────────┼────────┐        │         ┌────────┼────────┐
    │        │        │        │         │        │        │
    ▼        ▼        ▼        ▼         ▼        ▼        ▼
┌──────┐┌──────┐┌──────┐┌──────────┐┌──────┐┌──────┐┌──────┐
│certs ││certs ││certs ││kubeconfig││certs ││certs ││certs │
│/api- ││/api- ││/etcd ││/kubelet  ││/etcd ││/etcd ││/api- │
│server││server││ -ca  ││/ctrl-mgr ││server││peer  ││server│
│      ││-kube-││      ││/scheduler││      ││      ││-etcd │
│      ││let   ││      ││          ││      ││      ││client│
└──┬───┘└──┬───┘└──┬───┘└────┬─────┘└──┬───┘└──┬───┘└──┬───┘
   │       │       │         │         │       │       │
   └───────┼───────┼─────────┼─────────┼───────┼───────┘
           │       │         │         │       │
           ▼       ▼         ▼         ▼       ▼
    ┌──────────────────────────────────────────────┐
    │         control-plane/  (Static Pods)        │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
    │  │apiserver │ │ctrl-mgr  │ │scheduler │     │
    │  │  .yaml   │ │  .yaml   │ │  .yaml   │     │
    │  └──────────┘ └──────────┘ └──────────┘     │
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ mark-control-   │
                  │ plane + taint   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ bootstrap-token │
                  │ (join command)  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ addon/kube-proxy│
                  │ addon/coredns   │
                  └─────────────────┘</div>
            </div>
            <div class="warning">
                <strong>⚠️ Common failure point:</strong> The <code class="inline">preflight</code> phase is the most common failure. If swap is enabled, kubeadm refuses to proceed. If port 6443 is already in use, init fails with a clear error. If the container runtime socket doesn't exist, kubeadm can't proceed. <strong>Read the preflight errors carefully</strong> — they're explicit about what's wrong.
            </div>
        </div>

        <!-- 1.4 CERTIFICATE MANAGEMENT -->
        <h3 id="part-1-4">1.4 Certificate Management</h3>
        <div class="api-block">
            <p>kubeadm generates <strong>all certificates automatically</strong> during <code class="inline">kubeadm init</code>. You don't need to create any manually — but you DO need to know when they expire and how to renew them.</p>

            <table>
                <tr><th style="width:220px;">Certificate</th><th style="width:260px;">File Path</th><th>Purpose</th></tr>
                <tr><td><strong>★ Cluster CA</strong></td><td><code class="inline">/etc/kubernetes/pki/ca.crt</code></td><td>Root of trust — signs ALL cluster certificates. 10-year validity.</td></tr>
                <tr><td><strong>★ CA Private Key</strong></td><td><code class="inline">/etc/kubernetes/pki/ca.key</code></td><td><span style="color:var(--error);">PROTECT THIS FILE!</span> Anyone with this key can issue valid cluster certificates.</td></tr>
                <tr><td>API Server Cert</td><td><code class="inline">/etc/kubernetes/pki/apiserver.crt</code></td><td>Serves HTTPS on port 6443. Includes certSANs from the kubeadm config.</td></tr>
                <tr><td>API Server → Kubelet</td><td><code class="inline">/etc/kubernetes/pki/apiserver-kubelet-client.crt</code></td><td>API server authenticates to kubelet using this cert (for logs, exec, port-forward).</td></tr>
                <tr><td>Front-Proxy CA</td><td><code class="inline">/etc/kubernetes/pki/front-proxy-ca.crt</code></td><td>CA for the API aggregation layer (metrics-server, custom apiservices).</td></tr>
                <tr><td>etcd CA</td><td><code class="inline">/etc/kubernetes/pki/etcd/ca.crt</code></td><td>Separate CA for etcd — isolates etcd trust from the cluster PKI.</td></tr>
                <tr><td>etcd Server</td><td><code class="inline">/etc/kubernetes/pki/etcd/server.crt</code></td><td>etcd serving TLS certificate — API server verifies this.</td></tr>
                <tr><td>etcd Peer</td><td><code class="inline">/etc/kubernetes/pki/etcd/peer.crt</code></td><td>etcd member-to-member communication (Raft messages, data sync).</td></tr>
                <tr><td>API Server → etcd</td><td><code class="inline">/etc/kubernetes/pki/apiserver-etcd-client.crt</code></td><td>API server authenticates to etcd. Only the API server should have this.</td></tr>
                <tr><td>ServiceAccount Key Pair</td><td><code class="inline">/etc/kubernetes/pki/sa.pub</code> + <code class="inline">sa.key</code></td><td>Used to sign and verify ServiceAccount tokens. Pods mount these tokens at <code>/var/run/secrets/kubernetes.io/serviceaccount/token</code>.</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🔑 Why does etcd have its own CA?</strong> It's a security best practice called <strong>"defense in depth"</strong>. If the cluster CA is compromised, the attacker can impersonate any Kubernetes component — but they still can't talk to etcd directly because etcd uses a separate CA. The only component with an etcd client cert is the API server. This is why the API server is the <strong>only</strong> component that talks to etcd.
            </div>

            <h4>Certificate Renewal Commands</h4>
            <pre><code class="language-bash"># Check ALL certificate expiry dates (run this monthly!)
kubeadm certs check-expiration

# Renew ALL certificates
kubeadm certs renew all

# Renew specific certificates
kubeadm certs renew apiserver
kubeadm certs renew apiserver-etcd-client
kubeadm certs renew etcd-server
kubeadm certs renew etcd-peer

# After renewal, RESTART the affected component:
# Option 1: Move static Pod manifest (kubelet restarts it automatically)
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sleep 3
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Option 2: Restart kubelet (restarts ALL static Pods — more disruptive)
systemctl restart kubelet

# Verify the new cert is in use:
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates</code></pre>

            <div class="warning">
                <strong>⚠️ Certificate Expiry = Cluster Failure:</strong> If the API server certificate expires, <code class="inline">kubectl</code> stops working and no component can communicate. The kubelet's serving cert auto-rotates, but the static Pod certs (apiserver, etcd) do NOT auto-rotate. Set a calendar reminder 30 days before expiry. CA certificates have 10-year validity — if the CA expires, you need to rebuild the cluster.
            </div>
        </div>

        <!-- 1.4a CERTIFICATE TRUST CHAIN -->
        <h3 id="part-1-4a">1.4a Certificate Trust Chain — Who Signs What</h3>
        <div class="api-block">
            <div class="diagram-box">
                <div class="diagram-title">🔐 Kubernetes PKI Trust Chain</div>
                <div class="ascii-block">┌─────────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES PKI TRUST CHAIN                           │
│                                                                         │
│   ┌──────────────────────────────────┐                                  │
│   │     CLUSTER ROOT CA (ca.crt)     │  ← Self-signed, 10yr validity   │
│   │     /etc/kubernetes/pki/ca.crt   │     The ROOT OF ALL TRUST       │
│   │     /etc/kubernetes/pki/ca.key   │     ★ PROTECT THIS FILE ★       │
│   └────────────┬─────────────────────┘                                  │
│                │ SIGNS                                                   │
│     ┌──────────┼──────────┬──────────────┬───────────────┐              │
│     │          │          │              │               │              │
│     ▼          ▼          ▼              ▼               ▼              │
│ ┌───────┐ ┌───────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐        │
│ │ apis- │ │ apis- │ │kubelet   │ │ controller│ │  scheduler   │        │
│ │ erver │ │ erver │ │.conf     │ │ -manager  │ │  .conf       │        │
│ │ .crt  │ │-kube- │ │(client   │ │ .conf     │ │  (client     │        │
│ │       │ │ let   │ │ cert for │ │ (client   │ │   cert for   │        │
│ │ :6443 │ │client │ │ kubelet) │ │ cert)     │ │  scheduler)  │        │
│ └───────┘ └───────┘ └──────────┘ └───────────┘ └──────────────┘        │
│                                                                         │
│   ┌──────────────────────────────────┐                                  │
│   │    FRONT-PROXY CA                │  ← For API aggregation layer    │
│   └────────────┬─────────────────────┘                                  │
│                │ SIGNS  ┌──────────────┐                                │
│                └───────►│ front-proxy  │                                │
│                         │ -client.crt  │                                │
│                         └──────────────┘                                │
│                                                                         │
│   ┌──────────────────────────────────┐                                  │
│   │    ETCD CA (separate!)           │  ← Isolated trust for etcd      │
│   └────────────┬─────────────────────┘                                  │
│                │ SIGNS                                                   │
│     ┌──────────┼──────────┬───────────────┐                             │
│     ▼          ▼          ▼               ▼                             │
│ ┌───────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐                     │
│ │ etcd  │ │ etcd   │ │healthchk │ │ apiserver-   │                     │
│ │ server│ │ peer   │ │-client   │ │ etcd-client  │                     │
│ └───────┘ └────────┘ └──────────┘ └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘</div>
            </div>
            <div class="info">
                <strong>💡 Three CAs, Three Trust Domains:</strong> Kubernetes uses three separate Certificate Authorities: <strong>(1) Cluster CA</strong> — signs API server, kubelet, scheduler, controller-manager certs. <strong>(2) Front-Proxy CA</strong> — signs certs for the API aggregation layer (extending the API with custom resources). <strong>(3) etcd CA</strong> — isolated from the other two; only etcd and the API server have certs from this CA. This compartmentalization means a compromise in one domain doesn't automatically spread to others.
            </div>
        </div>

        <!-- 1.5 KUBEADM JOIN -->
        <h3 id="part-1-5">1.5 kubeadm Join — How Nodes Enter the Cluster</h3>
        <div class="api-block">
            <p>After <code class="inline">kubeadm init</code> on cp-01, every other node joins the cluster using a <strong>bootstrap token</strong> — a time-limited secret that proves "I'm allowed to join this cluster."</p>

            <h4>Worker Node Join</h4>
            <pre><code class="language-bash"># On cp-01, generate the join command:
kubeadm token create --print-join-command
# Output:
kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
    --discovery-token-ca-cert-hash sha256:a1b2c3d4e5f6...

# On each worker node (wk-01 through wk-05), paste the command:
kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
    --discovery-token-ca-cert-hash sha256:a1b2c3d4e5f6...</code></pre>

            <h4>Control Plane Node Join</h4>
            <pre><code class="language-bash"># First, upload certificates from cp-01 (generates an encryption key):
kubeadm init phase upload-certs --upload-certs
# Output: [upload-certs] Using certificate key: a1b2c3d4e5f6...

# On cp-02 (and cp-03), join as control plane:
kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
    --discovery-token-ca-cert-hash sha256:... \
    --control-plane --certificate-key a1b2c3d4e5f6...</code></pre>

            <h4>Bootstrap Token Details</h4>
            <table>
                <tr><th style="width:180px;">Property</th><th>Value</th></tr>
                <tr><td>Format</td><td><code class="inline">&lt;6 chars&gt;.&lt;16 chars&gt;</code> (e.g., <code class="inline">abc123.0123456789abcdef</code>)</td></tr>
                <tr><td>Default TTL</td><td>24 hours (configurable with <code class="inline">--ttl</code>)</td></tr>
                <tr><td>List Tokens</td><td><code class="inline">kubeadm token list</code></td></tr>
                <tr><td>Delete Token</td><td><code class="inline">kubeadm token delete &lt;token-id&gt;</code></td></tr>
                <tr><td>CA Cert Hash</td><td>SHA256 fingerprint of the CA certificate — prevents man-in-the-middle attacks during join</td></tr>
                <tr><td>Where Stored</td><td>As a Secret in <code class="inline">kube-system</code> namespace</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🔑 What is the CA cert hash for?</strong> When a new node joins, it connects to the API server over TLS. Without the CA cert hash, the node can't verify it's talking to the REAL API server and not an imposter. The hash is printed during <code class="inline">kubeadm init</code> — it's the SHA256 fingerprint of <code class="inline">/etc/kubernetes/pki/ca.crt</code>. This prevents man-in-the-middle attacks during the join process. Always verify the hash before pasting a join command from an untrusted source.
            </div>
        </div>

        <!-- 1.5a JOIN SEQUENCE (WORKER) -->
        <h3 id="part-1-5a">1.5a Join Sequence — Worker Node (Step by Step)</h3>
        <div class="api-block">
            <div class="diagram-box">
                <div class="diagram-title">🔗 Worker Node Join Sequence</div>
                <div class="ascii-block">  New Node (wk-04)                    API Server (10.0.0.100:6443)         cp-01 (kubelet)
  ─────────────                       ────────────────────────────         ──────────────
       │                                        │                               │
       │  1. kubeadm join --token xyz          │                               │
       │──────────────────────────────────────►│                               │
       │                                        │                               │
       │  2. "Here's my bootstrap token"        │                               │
       │                                        │                               │
       │  3. Token valid? Yes!                  │                               │
       │◄──────────────────────────────────────│                               │
       │     Here's a client certificate        │                               │
       │     (signed by cluster CA)             │                               │
       │                                        │                               │
       │  4. kubeadm writes:                    │                               │
       │     /etc/kubernetes/kubelet.conf       │                               │
       │     /var/lib/kubelet/config.yaml       │                               │
       │     /etc/kubernetes/pki/ca.crt         │                               │
       │                                        │                               │
       │  5. systemctl start kubelet            │                               │
       │──────────────────────────────────────────────────────────────────────►│
       │                                        │                               │
       │  6. kubelet: "Register node wk-04"     │                               │
       │──────────────────────────────────────►│                               │
       │                                        │                               │
       │  7. Node wk-04 created in etcd         │                               │
       │◄──────────────────────────────────────│                               │
       │                                        │                               │
       │  8. kubelet starts reporting status    │                               │
       │     (Node shows as NotReady — no CNI)  │                               │
       │                                        │                               │
       │  9. Admin applies Calico YAML          │                               │
       │     Calico DaemonSet Pod starts        │                               │
       │     CNI assigns PodCIDR: 10.244.4.0/26 │                               │
       │                                        │                               │
       │ 10. Node transitions to Ready!         │                               │
       │──────────────────────────────────────►│                               │
       │                                        │                               │

  Total time: ~30-60 seconds per worker node (after the join command)</div>
            </div>
            <table>
                <tr><th>Step</th><th>What Happens</th><th>Key File Written</th></tr>
                <tr><td>1-3</td><td>kubeadm authenticates to the API server using the bootstrap token</td><td>—</td></tr>
                <tr><td>4</td><td>kubeadm writes kubeconfig, kubelet config, and the cluster CA certificate</td><td><code class="inline">kubelet.conf</code>, <code class="inline">config.yaml</code>, <code class="inline">ca.crt</code></td></tr>
                <tr><td>5-6</td><td>kubelet starts via systemd, connects to API server, registers the Node object</td><td>—</td></tr>
                <tr><td>7</td><td>Node object is persisted to etcd via the API server</td><td>(etcd key: <code class="inline">/registry/nodes/wk-04</code>)</td></tr>
                <tr><td>8</td><td>Node shows NotReady — kubelet is running but there's no Pod network (CNI not installed)</td><td>—</td></tr>
                <tr><td>9</td><td>Calico DaemonSet Pod starts on wk-04, assigns PodCIDR, creates veth pairs and routes</td><td><code class="inline">/etc/cni/net.d/10-calico.conflist</code></td></tr>
                <tr><td>10</td><td>Node condition "Ready" flips to True. Scheduler can now place Pods on this node.</td><td>—</td></tr>
            </table>
        </div>

        <!-- 1.5b JOIN SEQUENCE (CP) -->
        <h3 id="part-1-5b">1.5b Join Sequence — Control Plane Node (Additional Steps)</h3>
        <div class="api-block">
            <div class="diagram-box">
                <div class="diagram-title">🔗 Control Plane Node Join Sequence (Extra Steps)</div>
                <div class="ascii-block">  New CP (cp-02)                     API Server                    cp-01 (etcd Leader)
  ─────────────                      ──────────                    ──────────────────
       │                                  │                               │
       │  1-9. Same as worker join        │                               │
       │      (steps above)               │                               │
       │                                  │                               │
       │  10. kubeadm downloads certs     │                               │
       │      from kubeadm-certs Secret   │                               │
       │◄─────────────────────────────────│                               │
       │                                  │                               │
       │  11. Decrypts certs with         │                               │
       │      --certificate-key           │                               │
       │                                  │                               │
       │  12. Writes static Pod manifests:│                               │
       │      /etc/kubernetes/manifests/  │                               │
       │      ├── etcd.yaml               │                               │
       │      ├── kube-apiserver.yaml     │                               │
       │      ├── kube-scheduler.yaml     │                               │
       │      └── kube-controller-manager.yaml                           │
       │                                  │                               │
       │  13. kubelet detects new         │                               │
       │      manifests → starts etcd     │                               │
       │──────────────────────────────────────────────────────────────────►│
       │                                  │                               │
       │  14. "I'm cp-02, joining Raft"   │                               │
       │──────────────────────────────────────────────────────────────────►│
       │                                  │                               │
       │  15. "Welcome, cp-02!            │                               │
       │       Syncing data..."           │                               │
       │◄─────────────────────────────────────────────────────────────────│
       │                                  │                               │
       │  16. etcd data synced.           │                               │
       │      Now a full Raft member.     │                               │
       │      API server + scheduler +    │                               │
       │      controller-manager start.   │                               │
       │                                  │                               │

  Total time: ~60-90 seconds per CP join (most time spent syncing etcd data)</div>
            </div>
            <div class="info">
                <strong>💡 Why does CP join take longer?</strong> The extra time is for <strong>etcd data synchronization</strong>. When cp-02 joins, its etcd instance is empty — it needs to sync ALL existing data from the etcd leader (cp-01). For the anihpj cluster with ~1,250 keys, this takes ~15-30 seconds. For larger clusters with 100K+ keys, syncing can take several minutes. During the sync, cp-02's etcd is not yet a voting member of the Raft cluster.
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# Find and replace the Part 1 placeholder
old = '''    <section class="section" id="part-1">
        <h2>🔧 <span class="section-num">Part 1</span> — kubeadm Deep Dive: How the Cluster Is Built</h2>
        <div class="section-intro"><p>kubeadm generates certificates, writes static Pod manifests, starts etcd and control plane components, and manages the join process. Covers every phase, certificate, and join sequence.</p></div>
    </section>'''

html = html.replace(old, content)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Lines: {html.count(chr(10))}')
print(f'Part 1 content: {content.count(chr(10))} lines')
print(f'Code blocks: {content.count("language-")}')
print(f'Tables: {content.count("<table>")}')
print(f'Diagrams: {content.count("diagram-box")} + {content.count("ascii-block")}')
print(f'Info boxes: {content.count("class=\"info\"")}')
print(f'Highlight boxes: {content.count("highlight-box")}')
print('Done.')
