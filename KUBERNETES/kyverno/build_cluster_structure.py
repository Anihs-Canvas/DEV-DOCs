#!/usr/bin/env python3
"""Build the fully expanded k8s-cluster-structure.txt with kubeadm demonstrations."""

content = r'''# ============================================================================
# ANIHPJ KUBERNETES CLUSTER STRUCTURE — COMPLETE REFERENCE
# Cluster: anihpj-prod | Tool: kubeadm v1.31.0
# Topology: 3 Control Plane + 5 Worker + 2 Frontend Nodes
# CNI: Calico v3.28 | Runtime: containerd v1.7 | OS: Ubuntu 24.04 LTS
# ============================================================================

# ============================================================================
# PART 0: CLUSTER INVENTORY — ALL NODES AT A GLANCE
# ============================================================================

┌──────────────────────────────────────────────────────────────────────────────┐
│                         ANIHPJ CLUSTER TOPOLOGY                               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                    CONTROL PLANE (3 nodes)                          │    │
│   │  ┌──────────┐     ┌──────────┐     ┌──────────┐                    │    │
│   │  │  cp-01   │◄───►│  cp-02   │◄───►│  cp-03   │   etcd Raft       │    │
│   │  │10.0.0.10 │     │10.0.0.11 │     │10.0.0.12 │   + API server     │    │
│   │  │ Leader   │     │ Follower │     │ Follower │   + scheduler      │    │
│   │  └────┬─────┘     └────┬─────┘     └────┬─────┘   + ctrl-mgr       │    │
│   │       │                │                │                           │    │
│   └───────┼────────────────┼────────────────┼───────────────────────────┘    │
│           │                │                │                                  │
│   ┌───────┼────────────────┼────────────────┼───────────────────────────┐    │
│   │       │          WORKER NODES (5 nodes) │                            │    │
│   │  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌──────────┐ ┌──────────┐  │    │
│   │  │  wk-01   │ │  wk-02   │ │  wk-03   │ │  wk-04   │ │  wk-05   │  │    │
│   │  │10.0.4.21 │ │10.0.4.22 │ │10.0.4.23 │ │10.0.4.24 │ │10.0.4.25 │  │    │
│   │  │ 4 CPU    │ │ 4 CPU    │ │ 8 CPU    │ │ 8 CPU    │ │ 4 CPU    │  │    │
│   │  │ 16GB RAM │ │ 16GB RAM │ │ 32GB RAM │ │ 32GB RAM │ │ 16GB RAM │  │    │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                    FRONTEND NODES (2 nodes)                         │    │
│   │  ┌──────────┐     ┌──────────┐                                      │    │
│   │  │  fe-01   │     │  fe-02   │    Nginx Ingress + TLS termination   │    │
│   │  │10.0.5.10 │     │10.0.5.11 │                                      │    │
│   │  └──────────┘     └──────────┘                                      │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   Cluster CIDR:      10.244.0.0/16    (Calico default)                       │
│   Service CIDR:      10.96.0.0/12     (ClusterIP range)                      │
│   DNS Service IP:    10.96.0.10       (CoreDNS)                              │
│   API Server VIP:    10.0.0.100:6443  (HAProxy load-balanced)                │
│   Pod CIDR per node: /26              (64 Pod IPs per worker node)           │
└──────────────────────────────────────────────────────────────────────────────┘


# ============================================================================
# PART 1: KUBEADM DEEP DIVE — HOW THE CLUSTER IS BUILT
# ============================================================================

# ──────────────────────────────────────────────────────────────────────────
# 1.1 WHAT IS KUBEADM?
# ──────────────────────────────────────────────────────────────────────────

kubeadm is the official Kubernetes tool for bootstrapping production-ready
clusters. It does NOT provision infrastructure (no VMs, no networking) —
it ONLY sets up Kubernetes components on existing Linux machines.

What kubeadm DOES:
  ✅ Generates ALL certificates (CA, apiserver, etcd, front-proxy, SA)
  ✅ Writes static Pod manifests for control plane components
  ✅ Starts etcd cluster (3 nodes via static Pods)
  ✅ Starts kube-apiserver, kube-scheduler, kube-controller-manager
  ✅ Generates kubeconfig files for all components
  ✅ Uploads cluster config to a ConfigMap (kubeadm-config) for future upgrades
  ✅ Bootstraps kubelet on every node
  ✅ Manages the bootstrap token flow for joining new nodes

What kubeadm does NOT do:
  ❌ Does NOT install kubelet, kubeadm, or kubectl (you install those via apt/yum)
  ❌ Does NOT install a container runtime (containerd/CRI-O — you set that up)
  ❌ Does NOT install a CNI plugin (Calico/Flannel/Cilium — you apply that after)
  ❌ Does NOT provision VMs or networking between nodes
  ❌ Does NOT configure load balancers for the API server

kubeadm workflow for anihpj:

  Phase 1: PRE-FLIGHT (on ALL 10 nodes)
    ├── Install containerd + runc
    ├── Install kubeadm, kubelet, kubectl (v1.31.0-*)
    ├── Configure kernel modules (overlay, br_netfilter)
    ├── Set sysctls (net.bridge.bridge-nf-call-iptables=1, net.ipv4.ip_forward=1)
    ├── Disable swap (swapoff -a, comment out in /etc/fstab)
    └── Configure containerd (SystemdCgroup=true, sandbox_image)

  Phase 2: INIT (on cp-01 only)
    ├── kubeadm init --config=kubeadm-config.yaml --upload-certs
    ├── Generates all certs in /etc/kubernetes/pki/
    ├── Starts etcd (single node on cp-01 initially)
    ├── Starts kube-apiserver, kube-scheduler, kube-controller-manager
    ├── Writes admin.conf to /etc/kubernetes/admin.conf
    └── Prints bootstrap token for joining other nodes

  Phase 3: JOIN CONTROL PLANE (on cp-02, cp-03)
    ├── kubeadm join 10.0.0.100:6443 --token <token> \
    │     --discovery-token-ca-cert-hash sha256:<hash> \
    │     --control-plane --certificate-key <cert-key>
    ├── etcd members join the Raft cluster automatically
    ├── API server, scheduler, controller-manager start as static Pods
    └── Now we have 3-node HA control plane

  Phase 4: JOIN WORKERS (on wk-01 through wk-05)
    ├── kubeadm join 10.0.0.100:6443 --token <token> \
    │     --discovery-token-ca-cert-hash sha256:<hash>
    ├── kubelet registers with API server
    └── Node appears as "Ready" after CNI is installed

  Phase 5: INSTALL CNI (from cp-01, after all nodes joined)
    ├── kubectl apply -f calico.yaml
    ├── Calico DaemonSet starts on every node
    ├── Nodes transition from "NotReady" to "Ready"
    └── CoreDNS pods start (were Pending, now have a network)

  Phase 6: DEPLOY APPLICATIONS
    └── kubectl apply -f anihpj-webapp.yaml, etc.


# ──────────────────────────────────────────────────────────────────────────
# 1.2 KUBEADM CONFIGURATION FILE (kubeadm-config.yaml)
# ──────────────────────────────────────────────────────────────────────────

This is the single file that defines the ENTIRE cluster. It lives on cp-01
and is uploaded to the cluster as a ConfigMap after init.

# File: ~/kubeadm-config.yaml (on cp-01 before init)
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "10.0.0.10"     # cp-01's IP
  bindPort: 6443
nodeRegistration:
  name: cp-01
  criSocket: unix:///run/containerd/containerd.sock
  kubeletExtraArgs:
  - name: cgroup-driver
    value: systemd
---
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
kubernetesVersion: v1.31.0
controlPlaneEndpoint: "10.0.0.100:6443"    # HAProxy VIP — ALL nodes connect here
imageRepository: registry.k8s.io

# ── Networking ──
networking:
  serviceSubnet: "10.96.0.0/12"
  podSubnet: "10.244.0.0/16"               # Must match Calico's default
  dnsDomain: "cluster.local"

# ── API Server ──
apiServer:
  extraArgs:
  - name: audit-log-path
    value: "/var/log/kubernetes/audit/audit.log"
  - name: audit-policy-file
    value: "/etc/kubernetes/audit-policy.yaml"
  - name: audit-log-maxage
    value: "30"
  - name: audit-log-maxbackup
    value: "10"
  - name: audit-log-maxsize
    value: "100"
  - name: enable-admission-plugins
    value: "NodeRestriction,PodSecurity"
  - name: encryption-provider-config
    value: "/etc/kubernetes/encryption-config.yaml"
  - name: service-account-issuer
    value: "https://kubernetes.default.svc.cluster.local"
  - name: service-account-key-file
    value: "/etc/kubernetes/pki/sa.pub"
  - name: service-account-signing-key-file
    value: "/etc/kubernetes/pki/sa.key"
  certSANs:
  - "10.0.0.100"            # HAProxy VIP
  - "anihpj-k8s-api.io"     # Public DNS name
  - "127.0.0.1"
  - "localhost"

# ── Controller Manager ──
controllerManager:
  extraArgs:
  - name: bind-address
    value: "0.0.0.0"
  - name: cluster-signing-cert-file
    value: "/etc/kubernetes/pki/ca.crt"
  - name: cluster-signing-key-file
    value: "/etc/kubernetes/pki/ca.key"

# ── Scheduler ──
scheduler:
  extraArgs:
  - name: bind-address
    value: "0.0.0.0"

# ── etcd ──
etcd:
  local:
    dataDir: "/var/lib/etcd"
    extraArgs:
      quota-backend-bytes: "8589934592"    # 8GB
      auto-compaction-retention: "1"        # 1 hour
      snapshot-count: "10000"
    serverCertSANs:
    - "cp-01"
    - "10.0.0.10"
    peerCertSANs:
    - "cp-01"
    - "10.0.0.10"
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
maxPods: 110
failSwapOn: true
clusterDNS:
- "10.96.0.10"
clusterDomain: "cluster.local"
containerRuntimeEndpoint: "unix:///run/containerd/containerd.sock"
evictionHard:
  memory.available: "100Mi"
  nodefs.available: "10%"
  imagefs.available: "15%"
systemReserved:
  cpu: "500m"
  memory: "1Gi"
kubeReserved:
  cpu: "250m"
  memory: "512Mi"
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "iptables"                   # Can be "ipvs" for better performance
clusterCIDR: "10.244.0.0/16"


# ──────────────────────────────────────────────────────────────────────────
# 1.3 KUBEADM PHASES — WHAT HAPPENS STEP BY STEP
# ──────────────────────────────────────────────────────────────────────────

kubeadm init runs through these phases in order. You can run them individually
with `kubeadm init phase <phase-name>` for troubleshooting:

  PHASE                         │ WHAT IT DOES
  ──────────────────────────────┼─────────────────────────────────────────────
  preflight                     │ Check: root, kernel, cgroups, container runtime,
                                │ ports not in use, kubelet version, swap disabled
  certs/ca                      │ Generate self-signed CA cert+key (10yr validity)
  certs/apiserver               │ Generate apiserver cert (signed by CA)
  certs/apiserver-kubelet-client│ Generate cert for apiserver→kubelet auth
  certs/front-proxy-ca          │ Generate front-proxy CA (for aggregation layer)
  certs/front-proxy-client      │ Generate front-proxy client cert
  certs/etcd-ca                 │ Generate etcd CA
  certs/etcd-server             │ Generate etcd server cert
  certs/etcd-peer               │ Generate etcd peer cert (member-to-member)
  certs/etcd-healthcheck-client │ Generate cert for kubelet→etcd health checks
  certs/apiserver-etcd-client   │ Generate cert for apiserver→etcd
  certs/sa                      │ Generate ServiceAccount key pair
  kubeconfig/admin              │ Generate admin.conf (cluster-admin access)
  kubeconfig/kubelet            │ Generate kubelet.conf bootstrap kubeconfig
  kubeconfig/controller-manager │ Generate controller-manager.conf
  kubeconfig/scheduler          │ Generate scheduler.conf
  control-plane/apiserver       │ Write /etc/kubernetes/manifests/kube-apiserver.yaml
  control-plane/controller-manager│ Write kube-controller-manager.yaml
  control-plane/scheduler       │ Write kube-scheduler.yaml
  etcd/local                    │ Write etcd.yaml + create /var/lib/etcd data dir
  upload-config/kubeadm         │ Upload ClusterConfiguration to kube-system/kubeadm-config
  upload-config/kubelet         │ Upload KubeletConfiguration to kube-system/kubelet-config
  upload-certs                  │ Upload certs as Secret (for other CP nodes to download)
  mark-control-plane            │ Label + taint cp-01 as control-plane
  bootstrap-token               │ Create bootstrap token + Secret for node join
  kubelet-finalize              │ Update kubelet.conf with final cert
  addon/kube-proxy              │ Create kube-proxy DaemonSet
  addon/coredns                 │ Create CoreDNS Deployment (Pending until CNI)

You can view the phases without executing:
  kubeadm init --dry-run --config=kubeadm-config.yaml
  # Prints exactly what it WOULD do without doing it.

Or run a specific phase:
  kubeadm init phase certs apiserver --config=kubeadm-config.yaml
  # Generate ONLY the API server certificate.


# ──────────────────────────────────────────────────────────────────────────
# 1.4 KUBEADM CERTIFICATE MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────

kubeadm generates ALL certificates automatically. Here's the complete PKI:

  Certificate                    │ Path                                      │ Purpose
  ───────────────────────────────┼───────────────────────────────────────────┼──────────────────────
  CA certificate                 │ /etc/kubernetes/pki/ca.crt                │ Signs ALL cluster certs
  CA private key                 │ /etc/kubernetes/pki/ca.key                │ PROTECT THIS — the root of trust
  API server cert                │ /etc/kubernetes/pki/apiserver.crt         │ Serves HTTPS on :6443
  API server key                 │ /etc/kubernetes/pki/apiserver.key         │
  API server→kubelet client cert │ /etc/kubernetes/pki/apiserver-kubelet-client.crt │ API server auth to kubelet
  Front proxy CA                 │ /etc/kubernetes/pki/front-proxy-ca.crt    │ For API aggregation
  Front proxy client cert        │ /etc/kubernetes/pki/front-proxy-client.crt│
  etcd CA                        │ /etc/kubernetes/pki/etcd/ca.crt           │ Signs all etcd certs
  etcd server cert               │ /etc/kubernetes/pki/etcd/server.crt       │ etcd serving TLS
  etcd peer cert                 │ /etc/kubernetes/pki/etcd/peer.crt         │ etcd-to-etcd TLS
  etcd healthcheck client        │ /etc/kubernetes/pki/etcd/healthcheck-client.crt │ kubelet→etcd probe
  API server→etcd client         │ /etc/kubernetes/pki/apiserver-etcd-client.crt │ API server→etcd auth
  ServiceAccount key pair        │ /etc/kubernetes/pki/sa.pub + sa.key       │ Signs ServiceAccount tokens

Certificate renewal:
  kubeadm certs check-expiration          # Show ALL cert expiry dates
  kubeadm certs renew all                 # Renew ALL certificates
  kubeadm certs renew apiserver           # Renew just the API server cert

After renewal, you MUST restart the component using the cert:
  mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
  mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
  # (Moving it out and back forces kubelet to restart the static Pod)

Certificate rotation for joining CP nodes:
  # When adding a third CP node months later, the cert key is needed.
  # Create a new cert key from the existing cluster:
  kubeadm init phase upload-certs --upload-certs
  # Prints: [upload-certs] Using certificate key: a1b2c3d4e5f6...


# ──────────────────────────────────────────────────────────────────────────
# 1.5 KUBEADM JOIN — HOW NODES ENTER THE CLUSTER
# ──────────────────────────────────────────────────────────────────────────

JOIN AS WORKER NODE (wk-01 through wk-05):

  # On cp-01, get the join command:
  kubeadm token create --print-join-command
  # Output:
  kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
      --discovery-token-ca-cert-hash sha256:1234567890abcdef...

  # On each worker node, paste the command:
  kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
      --discovery-token-ca-cert-hash sha256:1234567890abcdef...

What happens during worker join:
  1. kubeadm checks pre-flight (container runtime, swap, etc.)
  2. Pulls required images (kube-proxy, pause)
  3. Discovers the API server using the bootstrap token
  4. Gets a kubelet client certificate (signed by the cluster CA)
  5. Writes /etc/kubernetes/kubelet.conf
  6. Writes /var/lib/kubelet/config.yaml
  7. Writes /etc/kubernetes/pki/ca.crt
  8. Starts kubelet (via systemd)
  9. kubelet registers the node with the API server
  10. Node appears in `kubectl get nodes` (as NotReady until CNI)

JOIN AS CONTROL PLANE NODE (cp-02, cp-03):

  # First, upload certificates from cp-01 (creates an encryption key):
  kubeadm init phase upload-certs --upload-certs
  # Prints: [upload-certs] Using certificate key: a1b2c3d4...

  # Then on cp-02:
  kubeadm join 10.0.0.100:6443 --token abc123.0123456789abcdef \
      --discovery-token-ca-cert-hash sha256:... \
      --control-plane --certificate-key a1b2c3d4...

What happens during control plane join:
  1. Everything from worker join (steps 1-10)
  2. Downloads certificates from the kubeadm-certs Secret (encrypted with cert key)
  3. Writes static Pod manifests (etcd, apiserver, scheduler, controller-manager)
  4. kubelet detects new manifests → starts etcd and other CP components
  5. etcd joins the existing Raft cluster
  6. New API server, scheduler, controller-manager instances join the HA setup

Bootstrap token details:
  Token format: <6 chars>.<16 chars> (e.g., abc123.0123456789abcdef)
  Token TTL: 24 hours (configurable via --ttl)
  List tokens: kubeadm token list
  Delete tokens: kubeadm token delete <token-id>
  CA cert hash: sha256 of the CA certificate — prevents MITM during join


# ============================================================================
# PART 2: CLUSTER-LEVEL DIRECTORY TREE (FULL EXPANSION)
# ============================================================================

# This is the complete filesystem layout for EVERY node type in the cluster.
# Created by kubeadm, with additions for anihpj applications.

# ──────────────────────────────────────────────────────────────────────────
# 2.1 CONTROL PLANE NODE (cp-01) — COMPLETE FILESYSTEM
# ──────────────────────────────────────────────────────────────────────────

cp-01 (10.0.0.10) — CONTROL PLANE — COMPLETE TREE:

/
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
│   │   │   ├── 📄 ca.key                       #   ★ Cluster CA key — THE MOST CRITICAL FILE
│   │   │   ├── 📄 apiserver.crt                #   API server serving cert (SANs included)
│   │   │   ├── 📄 apiserver.key                #   API server private key
│   │   │   ├── 📄 apiserver-kubelet-client.crt #   API server → kubelet client cert
│   │   │   ├── 📄 apiserver-kubelet-client.key #
│   │   │   ├── 📄 apiserver-etcd-client.crt    #   API server → etcd client cert
│   │   │   ├── 📄 apiserver-etcd-client.key    #
│   │   │   ├── 📄 front-proxy-ca.crt           #   Front-proxy CA (aggregation layer)
│   │   │   ├── 📄 front-proxy-ca.key           #
│   │   │   ├── 📄 front-proxy-client.crt       #   Front-proxy client cert
│   │   │   ├── 📄 front-proxy-client.key       #
│   │   │   ├── 📄 sa.pub                       #   ServiceAccount public key
│   │   │   ├── 📄 sa.key                       #   ServiceAccount private key
│   │   │   ├── 📁 etcd/                        #   etcd-specific PKI
│   │   │   │   ├── 📄 ca.crt                   #     etcd CA
│   │   │   │   ├── 📄 ca.key                   #     etcd CA key
│   │   │   │   ├── 📄 server.crt               #     etcd server cert
│   │   │   │   ├── 📄 server.key               #
│   │   │   │   ├── 📄 peer.crt                 #     etcd peer cert (member-to-member)
│   │   │   │   ├── 📄 peer.key                 #
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
        └── 📄 config                           # → symlink to /etc/kubernetes/admin.conf


# ──────────────────────────────────────────────────────────────────────────
# 2.2 WORKER NODE (wk-04) — COMPLETE FILESYSTEM
# ──────────────────────────────────────────────────────────────────────────

wk-04 (10.0.4.24) — WORKER — COMPLETE TREE:

/
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
    └── 📄 ip_forward = 1


# ============================================================================
# PART 3: INSIDE A SINGLE NODE — RUNTIME DEEP DIVE
# ============================================================================

# ──────────────────────────────────────────────────────────────────────────
# 3.1 WORKER NODE (wk-04) — PROCESS TREE & RUNTIME STATE
# ──────────────────────────────────────────────────────────────────────────

[WORKER NODE: wk-04]
IP: 10.0.4.24 | Role: worker | CPUs: 8 | RAM: 32GB
OS: Ubuntu 24.04 LTS | Kernel: 6.8.0-31-generic
Container Runtime: containerd v1.7.20
CNI: Calico v3.28.1 | Kubelet: v1.31.0 | kube-proxy: v1.31.0 (iptables mode)
Pods running: 34 | Containers running: 47

## SYSTEMD SERVICES (managed by systemd, started at boot):
kubelet.service          → enabled, active (running)
                           ExecStart=/usr/bin/kubelet --config=/var/lib/kubelet/config.yaml
                           --container-runtime-endpoint=unix:///run/containerd/containerd.sock
                           --kubeconfig=/etc/kubernetes/kubelet.conf
containerd.service       → enabled, active (running)
                           ExecStart=/usr/bin/containerd
sshd.service             → enabled, active (running)
cron.service             → enabled, active (running)
systemd-journald.service → static, active (running)

NOTE: kube-proxy does NOT run as a systemd service. It runs as a DaemonSet Pod
      in kube-system namespace. Calico (felix + bird) runs as DaemonSet Pods too.

## PROCESS TREE (ps auxf —h on wk-04):
systemd (1)                                        # PID 1 — the init system
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
└─ cron (600)

Key insight: Every Pod has a "pause" container that holds the network namespace.
All other containers in the Pod join that namespace. The pause container never
does anything — it just exists so the Pod's IP and network stay alive.

## KUBELET CONFIGURATION (/var/lib/kubelet/config.yaml):
# Generated by kubeadm, customized via KubeletConfiguration in kubeadm-config.yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
address: 0.0.0.0
port: 10250                                     # Kubelet API port
readOnlyPort: 0                                 # Disabled (security)
staticPodPath: /etc/kubernetes/manifests/       # Only used on CP nodes
clusterDNS:
  - 10.96.0.10                                  # CoreDNS ClusterIP
clusterDomain: cluster.local
containerRuntimeEndpoint: unix:///run/containerd/containerd.sock
maxPods: 110                                    # Default: 110 Pods per node
podCIDR: 10.244.4.0/26                          # This node's Pod CIDR (64 IPs)
cgroupDriver: systemd
failSwapOn: true
serializeImagePulls: false                      # Pull images in parallel
registryPullQPS: 5                              # Rate limit image pulls
registryBurst: 10
eventRecordQPS: 50
eventBurst: 100
kubeAPIQPS: 50
kubeAPIBurst: 100
# Eviction thresholds (when to evict Pods under pressure):
evictionHard:
  memory.available: "100Mi"                     # Evict if < 100MB free RAM
  nodefs.available: "10%"                       # Evict if < 10% disk
  imagefs.available: "15%"                      # Evict if < 15% image disk
  nodefs.inodesFree: "5%"                       # Evict if < 5% inodes
evictionSoft:
  memory.available: "200Mi"                     # Soft eviction at 200MB
evictionSoftGracePeriod: "2m"                   # Wait 2 mins before hard eviction
# System reserved (for OS daemons — not available to Pods):
systemReserved:
  cpu: "500m"
  memory: "1Gi"
kubeReserved:
  cpu: "250m"
  memory: "512Mi"
# Authentication:
authentication:
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt    # Verify client certs with this CA
  anonymous:
    enabled: false                               # No anonymous access
  webhook:
    enabled: true                                # Use API server for auth
# Authorization:
authorization:
  mode: Webhook                                  # Ask API server: "Is this request allowed?"

## CONTAINERD CONFIGURATION (/etc/containerd/config.toml):
# kubeadm requires SystemdCgroup=true for cgroup v2 compatibility
version = 2
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.9"    # The "pause" container image
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "runc"
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
      runtime_type = "io.containerd.runc.v2"
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
        SystemdCgroup = true                      # ★ MUST be true for kubeadm
  [plugins."io.containerd.grpc.v1.cri".registry]
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
        endpoint = ["https://mirror.gcr.io", "https://registry-1.docker.io"]

## CNI CONFIGURATION (/etc/cni/net.d/10-calico.conflist):
{
  "name": "k8s-pod-network",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "calico",
      "log_level": "info",
      "datastore_type": "kubernetes",
      "nodename": "wk-04",
      "mtu": 1440,
      "ipam": { "type": "calico-ipam" },
      "policy": { "type": "k8s" }
    },
    { "type": "portmap", "snat": true, "capabilities": {"portMappings": true} },
    { "type": "bandwidth", "capabilities": {"bandwidth": true} }
  ]
}
# The CNI plugin chain executes in order:
# 1. calico: Assigns IP, creates veth pair, sets up routes/firewall rules
# 2. portmap: Maps hostPort to container port (if hostPort is defined)
# 3. bandwidth: Enforces Pod bandwidth limits (if annotations are set)


# ──────────────────────────────────────────────────────────────────────────
# 3.2 CONTROL PLANE NODE (cp-01) — WHAT'S DIFFERENT
# ──────────────────────────────────────────────────────────────────────────

[CONTROL PLANE NODE: cp-01]
IP: 10.0.0.10 | Role: control-plane | CPUs: 4 | RAM: 16GB
ALL of the worker node contents PLUS:

## STATIC POD MANIFESTS (/etc/kubernetes/manifests/):
# kubelet watches this directory. Each .yaml file becomes a Pod that kubelet
# guarantees is ALWAYS running. If a static Pod crashes, kubelet restarts it.
# These are NOT managed by the API server — they're managed by kubelet directly.

### 1. etcd.yaml — Static Pod manifest
apiVersion: v1
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
    - --initial-cluster-state=existing           # "new" on first init, "existing" on join
    - --listen-client-urls=https://127.0.0.1:2379,https://10.0.0.10:2379
    - --listen-metrics-urls=http://127.0.0.1:2381
    - --listen-peer-urls=https://10.0.0.10:2380
    - --name=cp-01
    - --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
    - --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
    - --peer-client-cert-auth=true
    - --snapshot-count=10000
    - --quota-backend-bytes=8589934592          # 8GB limit
    - --auto-compaction-retention=1
    livenessProbe:                               # Kubelet checks this every 10s
      httpGet:
        path: /health
        port: 2381
      initialDelaySeconds: 10
      periodSeconds: 10
    volumeMounts:
    - name: etcd-data
      mountPath: /var/lib/etcd
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
      type: DirectoryOrCreate

### 2. kube-apiserver.yaml — Static Pod manifest
# The most important component. If this is down on ALL nodes, the cluster
# is unreachable (but existing workloads keep running).
apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
  namespace: kube-system
  labels:
    component: kube-apiserver
    tier: control-plane
spec:
  hostNetwork: true
  priorityClassName: system-node-critical
  containers:
  - name: kube-apiserver
    image: registry.k8s.io/kube-apiserver:v1.31.0
    command:
    - kube-apiserver
    - --advertise-address=10.0.0.10
    - --allow-privileged=true
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
    - --authorization-mode=Node,RBAC
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --enable-admission-plugins=NodeRestriction,PodSecurity
    - --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
    - --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key
    - --etcd-servers=https://10.0.0.10:2379,https://10.0.0.11:2379,https://10.0.0.12:2379
    - --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt
    - --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key
    - --kubelet-preferred-address-types=InternalIP,Hostname
    - --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt
    - --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key
    - --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt
    - --secure-port=6443
    - --service-account-issuer=https://kubernetes.default.svc.cluster.local
    - --service-account-key-file=/etc/kubernetes/pki/sa.pub
    - --service-account-signing-key-file=/etc/kubernetes/pki/sa.key
    - --service-cluster-ip-range=10.96.0.0/12
    - --tls-cert-file=/etc/kubernetes/pki/apiserver.crt
    - --tls-private-key-file=/etc/kubernetes/pki/apiserver.key
    livenessProbe:
      httpGet:
        path: /livez
        port: 6443
        scheme: HTTPS
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /readyz
        port: 6443
        scheme: HTTPS
      initialDelaySeconds: 5
      periodSeconds: 5

### 3. kube-controller-manager.yaml — Static Pod manifest
apiVersion: v1
kind: Pod
metadata:
  name: kube-controller-manager
  namespace: kube-system
  labels:
    component: kube-controller-manager
    tier: control-plane
spec:
  hostNetwork: true
  priorityClassName: system-node-critical
  containers:
  - name: kube-controller-manager
    image: registry.k8s.io/kube-controller-manager:v1.31.0
    command:
    - kube-controller-manager
    - --bind-address=0.0.0.0
    - --cluster-cidr=10.244.0.0/16
    - --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt
    - --cluster-signing-key-file=/etc/kubernetes/pki/ca.key
    - --controllers=*,bootstrapsigner,tokencleaner     # ALL controllers
    - --kubeconfig=/etc/kubernetes/controller-manager.conf
    - --leader-elect=true                               # Only 1 active at a time
    - --node-cidr-mask-size=26                          # /26 per node = 64 Pod IPs
    - --use-service-account-credentials=true
    livenessProbe:
      httpGet:
        path: /healthz
        port: 10257
      initialDelaySeconds: 10
      periodSeconds: 10

### 4. kube-scheduler.yaml — Static Pod manifest
apiVersion: v1
kind: Pod
metadata:
  name: kube-scheduler
  namespace: kube-system
  labels:
    component: kube-scheduler
    tier: control-plane
spec:
  hostNetwork: true
  priorityClassName: system-node-critical
  containers:
  - name: kube-scheduler
    image: registry.k8s.io/kube-scheduler:v1.31.0
    command:
    - kube-scheduler
    - --bind-address=0.0.0.0
    - --kubeconfig=/etc/kubernetes/scheduler.conf
    - --leader-elect=true
    livenessProbe:
      httpGet:
        path: /healthz
        port: 10259
      initialDelaySeconds: 10
      periodSeconds: 10


# ============================================================================
# PART 4: KEY DIRECTORY QUICK REFERENCE (EXPANDED)
# ============================================================================

Directory / File                                  │ Purpose
──────────────────────────────────────────────────┼────────────────────────────────────────
/etc/kubernetes/manifests/                        │ ★ Static Pod manifests — kubelet watches this
/etc/kubernetes/manifests/etcd.yaml               │ etcd static Pod (CP only)
/etc/kubernetes/manifests/kube-apiserver.yaml     │ API server static Pod (CP only)
/etc/kubernetes/manifests/kube-controller-manager.yaml │ Controller manager static Pod (CP only)
/etc/kubernetes/manifests/kube-scheduler.yaml     │ Scheduler static Pod (CP only)
/etc/kubernetes/pki/ca.crt                        │ ★ Cluster CA certificate
/etc/kubernetes/pki/ca.key                        │ ★ Cluster CA private key — PROTECT THIS
/etc/kubernetes/pki/apiserver.crt                 │ API server serving certificate
/etc/kubernetes/pki/apiserver.key                 │ API server private key
/etc/kubernetes/pki/apiserver-kubelet-client.crt  │ API server → kubelet client cert
/etc/kubernetes/pki/apiserver-etcd-client.crt     │ API server → etcd client cert
/etc/kubernetes/pki/etcd/ca.crt                   │ etcd CA certificate
/etc/kubernetes/pki/etcd/server.crt               │ etcd server certificate
/etc/kubernetes/pki/etcd/peer.crt                 │ etcd peer certificate
/etc/kubernetes/pki/sa.pub + sa.key               │ ServiceAccount key pair
/etc/kubernetes/admin.conf                        │ ★ Admin kubeconfig (cluster-admin)
/etc/kubernetes/kubelet.conf                      │ Kubelet kubeconfig
/etc/kubernetes/controller-manager.conf           │ Controller manager kubeconfig
/etc/kubernetes/scheduler.conf                    │ Scheduler kubeconfig
/etc/kubernetes/audit-policy.yaml                 │ API audit policy
/etc/kubernetes/encryption-config.yaml            │ Secret encryption at rest config
/etc/systemd/system/kubelet.service               │ Kubelet systemd unit
/etc/systemd/system/kubelet.service.d/10-kubeadm.conf │ kubeadm kubelet drop-in
/etc/systemd/system/containerd.service            │ Containerd systemd unit
/etc/containerd/config.toml                       │ Containerd configuration
/etc/cni/net.d/10-calico.conflist                 │ Calico CNI configuration
/var/lib/kubelet/config.yaml                      │ ★ Kubelet resolved configuration
/var/lib/kubelet/pki/kubelet-server-current.pem   │ Kubelet's serving cert (auto-rotated)
/var/lib/kubelet/plugins/                         │ CSI device plugin sockets
/var/lib/etcd/member/snap/db                      │ ★★ etcd database file (the cluster state!)
/var/lib/etcd/member/wal/                         │ etcd Write-Ahead Logs
/var/lib/kube-proxy/config.conf                   │ kube-proxy configuration
/var/lib/containerd/                              │ Container images, snapshots, runtime state
/var/lib/calico/                                  │ Calico node data
/var/log/pods/                                    │ Pod logs (symlinked)
/var/log/containers/                              │ Container logs (CRI format)
/var/log/kubernetes/audit/                        │ API audit logs
/run/containerd.sock                              │ ★ Containerd gRPC API socket
/run/kubelet/kubelet.sock                         │ Kubelet API socket
/opt/cni/bin/                                     │ CNI plugin binaries
/proc/sys/net/ipv4/ip_forward                     │ MUST be 1

# ============================================================================
# PART 5: NETWORK FLOW — HOW A REQUEST REACHES A POD (EXPANDED)
# ============================================================================

# ──────────────────────────────────────────────────────────────────────────
# 5.1 EXTERNAL REQUEST FLOW (USER → POD)
# ──────────────────────────────────────────────────────────────────────────

User Browser: https://anihpj.io/api/jobs
    │
    ▼
[DNS Resolution: anihpj.io → 203.0.113.10 (Cloud LB public IP)]
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLOUD LOAD BALANCER (HAProxy / AWS NLB / Azure LB)            │
│  Public IP: 203.0.113.10 → Backend: fe-01:443, fe-02:443       │
│  Health check: GET /healthz on each frontend every 5s           │
└────────────┬────────────────────────────┬───────────────────────┘
             │                            │
    ┌────────▼────────┐          ┌────────▼────────┐
    │  fe-01:443      │          │  fe-02:443      │
    │  NGINX INGRESS  │          │  NGINX INGRESS  │
    │  TLS termination│          │  TLS termination│
    │  SSL cert:      │          │  SSL cert:      │
    │  anihpj.io.crt  │          │  anihpj.io.crt  │
    └────────┬────────┘          └────────┬────────┘
             │                            │
             │  Nginx routes by Host header + path:
             │  anihpj.io/api/* → Service webapp-svc:8080
             │  anihpj.io/*     → Service webapp-svc:8080
             │
             ▼
    ┌────────────────────────────────────────────────────────────┐
    │  KUBE-PROXY (iptables/IPVS rules on whichever node        │
    │  the packet lands on)                                     │
    │                                                           │
    │  iptables -t nat -L KUBE-SERVICES:                        │
    │  Chain KUBE-SVC-XXXX (webapp-svc:8080):                   │
    │    ── probability 0.333 → KUBE-SEP-wk03 (10.244.3.45)     │
    │    ── probability 0.500 → KUBE-SEP-wk04 (10.244.4.72)    │
    │    ── probability 1.000 → KUBE-SEP-wk05 (10.244.5.18)    │
    │  (Random load balancing — iptables statistics module)     │
    └──────────────────────┬─────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ wk-03        │ │ wk-04        │ │ wk-05        │
    │ Pod IP:      │ │ Pod IP:      │ │ Pod IP:      │
    │ 10.244.3.45  │ │ 10.244.4.72  │ │ 10.244.5.18  │
    │              │ │              │ │              │
    │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
    │ │ webapp   │ │ │ │ webapp   │ │ │ │ webapp   │ │
    │ │ container│ │ │ │ container│ │ │ │ container│ │
    │ │ :8080    │ │ │ │ :8080    │ │ │ │ :8080    │ │
    │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
    └──────────────┘ └──────────────┘ └──────────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  POSTGRESQL DATABASE   │
              │  10.0.6.10:5432       │
              │  (external to K8s)    │
              └────────────────────────┘


# ──────────────────────────────────────────────────────────────────────────
# 5.2 POD-TO-POD COMMUNICATION (SAME NODE)
# ──────────────────────────────────────────────────────────────────────────

Pod A (10.244.4.72) → Pod B (10.244.4.73) on SAME node (wk-04):

1. Pod A sends packet to 10.244.4.73
2. Pod A's veth (virtual ethernet) → node's root network namespace
3. Calico route table on wk-04:
   10.244.4.73 dev cali1234567890 scope link
   → "Send directly to the veth of Pod B"
4. Packet goes through Calico's iptables rules (for NetworkPolicy enforcement)
5. Arrives at Pod B's veth → Pod B's network namespace
6. Pod B's container receives the packet

No overlay, no tunnel — Calico uses pure IP routing (BGP). This is why Calico
is so fast: it programs the Linux kernel's routing table directly.


# ──────────────────────────────────────────────────────────────────────────
# 5.3 POD-TO-POD COMMUNICATION (CROSS-NODE)
# ──────────────────────────────────────────────────────────────────────────

Pod A (wk-04, 10.244.4.72) → Pod B (wk-03, 10.244.3.45):

1. Pod A sends packet to 10.244.3.45
2. Pod A's veth → wk-04 root namespace
3. Calico route on wk-04:
   10.244.3.0/26 via 10.0.4.23 dev eth0
   → "wk-03's Pod CIDR is reachable via wk-03's node IP"
   This route was learned via BGP from Calico on wk-03
4. Packet goes out eth0 on wk-04 → physical network
5. Switch/router delivers to 10.0.4.23 (wk-03)
6. Calico route on wk-03:
   10.244.3.45 dev cali9876543210 scope link
   → "This specific Pod IP is on this veth"
7. Arrives at Pod B's veth → Pod B receives the packet

Optional: If you enable IP-in-IP or VXLAN in Calico (for networks that
don't support BGP), the packet is encapsulated at step 4 and decapsulated
at step 6. This adds ~20 bytes overhead but works on any network.


# ──────────────────────────────────────────────────────────────────────────
# 5.4 SERVICE TO POD (ClusterIP) — iptables DEEP DIVE
# ──────────────────────────────────────────────────────────────────────────

Service: webapp-svc (ClusterIP: 10.96.50.100, Port: 8080)
Endpoints: 10.244.3.45:8080, 10.244.4.72:8080, 10.244.5.18:8080

When any Pod sends a packet to 10.96.50.100:8080, iptables does this:

1. PREROUTING chain: packet enters netfilter
2. KUBE-SERVICES chain: matches 10.96.50.100:8080
   → jumps to KUBE-SVC-XXXX (the Service's chain)
3. KUBE-SVC-XXXX chain:
   # Probability-based random selection (3 endpoints = 33.3% each)
   [1st rule]  probability 0.33333333 → jump KUBE-SEP-wk03  (DNAT to 10.244.3.45:8080)
   [2nd rule]  probability 0.50000000 → jump KUBE-SEP-wk04  (DNAT to 10.244.4.72:8080)
   [3rd rule]  probability 1.00000000 → jump KUBE-SEP-wk05  (DNAT to 10.244.5.18:8080)
4. KUBE-SEP-XXXX chain: DNAT to the selected Pod IP:Port
5. Packet is now addressed to the Pod IP → follows Pod-to-Pod routing

Total iptables rules for this ONE Service: ~12 rules
For 100 Services with 5 endpoints each: ~6000 rules
This is why iptables mode doesn't scale past ~5000 Services — IPVS mode
uses a hash table instead, which is O(1) vs O(n).


# ============================================================================
# PART 6: ETCD — THE BRAIN OF THE CLUSTER (KEPT FROM PREVIOUS VERSION)
# ============================================================================

# [Part 6 content preserved from previous expansion — see full file for
#  6.1-6.13 covering: What is etcd, Raft consensus, Data model, API server
#  interaction, MVCC, Topology, Performance, Operations, Security,
#  Troubleshooting, etcdctl reference, Component map, Disaster scenarios]
#
# NOTE: Part 6 is the same extensive 13-section deep dive from the previous
#       expansion. It covers etcd exhaustively.

'''

# ── Now add the preserved Part 6 content ──
# Read the existing Part 6 from the current file
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.txt', 'r', encoding='utf-8') as f:
    old = f.read()

# Extract Part 6 (from "PART 6:" to end of file)
part6_start = old.find('# PART 6: ETCD')
if part6_start > 0:
    part6 = old[part6_start:]
    content += '\n' + part6

# Also add new parts 7+ after Part 6
content += r'''

# ============================================================================
# PART 7: KUBEADM DAY 2 OPERATIONS
# ============================================================================

# ──────────────────────────────────────────────────────────────────────────
# 7.1 UPGRADING THE CLUSTER WITH KUBEADM
# ──────────────────────────────────────────────────────────────────────────

kubeadm supports upgrading one minor version at a time (e.g., 1.30 → 1.31).
You CANNOT skip minor versions (1.29 → 1.31 is NOT supported).

UPGRADE PROCESS (1.31.0 → 1.31.4, then 1.31.4 → 1.32.0):

## Step 1: Upgrade kubeadm on the FIRST control plane node (cp-01):
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm

## Step 2: Verify the upgrade plan:
kubeadm upgrade plan
# Output shows:
#   - Current version: v1.31.0
#   - Available upgrades: v1.31.4 (stable), v1.32.0 (stable)
#   - Components that CAN be upgraded
#   - Components that MUST be upgraded manually

## Step 3: Apply the upgrade (on cp-01):
kubeadm upgrade apply v1.31.4
# This:
#   1. Renews certificates if needed
#   2. Upgrades the static Pod manifests (etcd, apiserver, scheduler, ctrl-mgr)
#   3. Upgrades kubelet configuration
#   4. Updates kubeadm-config and kubelet-config ConfigMaps
#   5. Upgrades CoreDNS and kube-proxy addons
#   6. Does NOT upgrade kubelet itself (you do that next)

## Step 4: Upgrade kubelet and kubectl on cp-01:
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.31.4-* kubectl=1.31.4-*
apt-mark hold kubelet kubectl
systemctl daemon-reload
systemctl restart kubelet

## Step 5: Upgrade OTHER control plane nodes (cp-02, cp-03):
# On each CP node:
apt-mark unhold kubeadm
apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm
kubeadm upgrade node          # Upgrades static Pod manifests on THIS node
# Then upgrade kubelet+kubectl and restart kubelet (same as Step 4)

## Step 6: Upgrade WORKER nodes (wk-01 through wk-05):
# Option A: One at a time (safe):
kubectl drain wk-01 --ignore-daemonsets --delete-emptydir-data
# SSH to wk-01:
apt-mark unhold kubeadm
apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm
kubeadm upgrade node
apt-get install -y kubelet=1.31.4-* kubectl=1.31.4-*
systemctl daemon-reload
systemctl restart kubelet
# Back on cp-01:
kubectl uncordon wk-01
# Wait for node to be Ready, then proceed to wk-02

# Option B: Ansible/shell script for bulk:
for node in wk-{01..05}; do
  echo "Upgrading $node..."
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data --timeout=5m
  ssh $node "apt-get update && apt-get install -y kubeadm=1.31.4-* && kubeadm upgrade node && apt-get install -y kubelet=1.31.4-* && systemctl restart kubelet"
  kubectl uncordon $node
  kubectl wait --for=condition=Ready node/$node --timeout=120s
done


# ──────────────────────────────────────────────────────────────────────────
# 7.2 ADDING A NEW NODE TO THE CLUSTER
# ──────────────────────────────────────────────────────────────────────────

Scenario: wk-04 failed and was replaced with a new VM (wk-04-new, 10.0.4.30).

## Step 1: Remove the old node from the cluster:
kubectl delete node wk-04          # Remove from API server

## Step 2: On the new VM, install prerequisites:
# (Same as initial setup: containerd, kubeadm, kubelet, kubectl, kernel modules, sysctls)

## Step 3: Generate a new bootstrap token (on cp-01):
kubeadm token create --print-join-command
# Output: kubeadm join 10.0.0.100:6443 --token newtoken.abcdefghijk --discovery-token-ca-cert-hash sha256:...

## Step 4: Join the cluster (on wk-04-new):
kubeadm join 10.0.0.100:6443 --token newtoken.abcdefghijk --discovery-token-ca-cert-hash sha256:...

## Step 5: Verify:
kubectl get nodes
# wk-04-new   Ready   worker   30s   v1.31.0


# ──────────────────────────────────────────────────────────────────────────
# 7.3 RENEWING CERTIFICATES
# ──────────────────────────────────────────────────────────────────────────

# Check all certificate expiry dates:
kubeadm certs check-expiration
[check-expiration] Reading configuration from the cluster...
CERTIFICATE                     EXPIRES                  RESIDUAL TIME
/etc/kubernetes/pki/apiserver.crt             Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/apiserver-kubelet-client.crt  Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/front-proxy-client.crt    Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/server.crt           Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/peer.crt             Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/healthcheck-client.crt  Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/apiserver-etcd-client.crt   Jan 01 2027 08:00 UTC   208d
CERTIFICATE AUTHORITY           EXPIRES                  RESIDUAL TIME
/etc/kubernetes/pki/ca.crt                    Jun 01 2036 08:00 UTC   9y
/etc/kubernetes/pki/front-proxy-ca.crt        Jun 01 2036 08:00 UTC   9y
/etc/kubernetes/pki/etcd/ca.crt               Jun 01 2036 08:00 UTC   9y

# Renew ALL certificates:
kubeadm certs renew all

# Or renew specific certs:
kubeadm certs renew apiserver
kubeadm certs renew apiserver-etcd-client
kubeadm certs renew etcd-server

# After renewal, restart the affected components (on EVERY CP node):
# Option 1: Move static Pod manifest (kubelet restarts it)
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sleep 5
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Option 2: Use crictl to stop the container (kubelet restarts it)
crictl ps | grep kube-apiserver
crictl stop <container-id>

# Option 3: Restart kubelet (restarts ALL static Pods — more disruptive)
systemctl restart kubelet

# Verify the component is using the new cert:
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates


# ──────────────────────────────────────────────────────────────────────────
# 7.4 TROUBLESHOOTING KUBEADM CLUSTERS
# ──────────────────────────────────────────────────────────────────────────

PROBLEM 1: "kubeadm init hangs at [wait-control-plane]"
  Cause: API server static Pod isn't starting. Kubelet can't reach the API server.
  Check: journalctl -u kubelet -f (on cp-01)
         crictl ps -a | grep kube-apiserver (check if container is starting)
         crictl logs <apiserver-container-id>
  Common: Wrong advertise address, port conflict (6443 already in use),
         etcd not starting, certificate issue.

PROBLEM 2: "kubeadm join hangs at [preflight]"
  Cause: Can't reach the API server at the join address.
  Check: curl -k https://10.0.0.100:6443/healthz (from the joining node)
         Is the load balancer forwarding to the right CP nodes?
         Is the bootstrap token still valid? (kubeadm token list)
         Firewall rules: port 6443 must be open between workers and CP.

PROBLEM 3: "Node shows NotReady after join"
  Cause: No CNI plugin installed, OR kubelet can't talk to the container runtime.
  Check: kubectl describe node wk-04 | grep -A5 Conditions
         journalctl -u kubelet -n 50
         systemctl status containerd
         Is /run/containerd/containerd.sock present?

PROBLEM 4: "[ERROR FileContent--proc-sys-net-ipv4-ip_forward]: /proc/sys/net/ipv4/ip_forward contents are not set to 1"
  Fix: echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.d/99-kubernetes.conf && sysctl --system

PROBLEM 5: "[ERROR Swap]: running with swap on is not supported"
  Fix: swapoff -a && sed -i '/swap/d' /etc/fstab
  (Kubernetes requires swap to be OFF for predictable memory management)

PROBLEM 6: "container runtime is not running: validate service connection"
  Cause: containerd is down or socket doesn't exist.
  Fix: systemctl start containerd && systemctl enable containerd
       Check: ls -la /run/containerd/containerd.sock

PROBLEM 7: "The HTTP call equal to 'curl -sSL http://localhost:10248/healthz' failed"
  Cause: Kubelet health check on port 10248 failed.
  Check: systemctl status kubelet
         journalctl -u kubelet -n 100
         Is the kubeconfig correct? Does the API server respond?


# ============================================================================
# PART 8: COMPLETE CLUSTER BOOTSTRAP — COPY-PASTE WALKTHROUGH
# ============================================================================

# ──────────────────────────────────────────────────────────────────────────
# 8.1 PRE-REQUISITES (ALL 10 NODES: cp-01..03, wk-01..05, fe-01..02)
# ──────────────────────────────────────────────────────────────────────────

#!/bin/bash
# Run as root on EVERY node before kubeadm init/join

# ── System configuration ──
cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
modprobe overlay
modprobe br_netfilter

cat <<EOF | tee /etc/sysctl.d/99-kubernetes.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sysctl --system

swapoff -a
sed -i '/swap/d' /etc/fstab

# ── Install containerd ──
apt-get update && apt-get install -y containerd
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd

# ── Install kubeadm, kubelet, kubectl ──
apt-get update && apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list
apt-get update && apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl
systemctl enable kubelet


# ──────────────────────────────────────────────────────────────────────────
# 8.2 INITIALIZE THE CLUSTER (cp-01 ONLY)
# ──────────────────────────────────────────────────────────────────────────

# Create kubeadm config (on cp-01):
cat <<EOF > ~/kubeadm-config.yaml
# [Full config from Section 1.2 above]
EOF

# Initialize:
kubeadm init --config=~/kubeadm-config.yaml --upload-certs

# Save output! It contains:
# - The join command for worker nodes
# - The join command for control plane nodes
# - The certificate key (needed for other CP nodes)

# Set up kubectl:
mkdir -p $HOME/.kube
cp /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# Verify:
kubectl get nodes
# cp-01   NotReady   control-plane   30s   v1.31.0


# ──────────────────────────────────────────────────────────────────────────
# 8.3 JOIN OTHER CONTROL PLANE NODES (cp-02, cp-03)
# ──────────────────────────────────────────────────────────────────────────

# On cp-02 and cp-03 (using the cert-key from init):
kubeadm join 10.0.0.100:6443 \
  --token abc123.0123456789abcdef \
  --discovery-token-ca-cert-hash sha256:... \
  --control-plane \
  --certificate-key a1b2c3d4e5f6...


# ──────────────────────────────────────────────────────────────────────────
# 8.4 JOIN WORKER NODES (wk-01 through wk-05)
# ──────────────────────────────────────────────────────────────────────────

# On each worker node:
kubeadm join 10.0.0.100:6443 \
  --token abc123.0123456789abcdef \
  --discovery-token-ca-cert-hash sha256:...


# ──────────────────────────────────────────────────────────────────────────
# 8.5 INSTALL CNI (CALICO)
# ──────────────────────────────────────────────────────────────────────────

# On cp-01 (or any node with kubectl):
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/calico.yaml

# Wait for all nodes to become Ready:
kubectl get nodes -w
# All nodes should transition from NotReady → Ready

# Verify CoreDNS is running:
kubectl get pods -n kube-system | grep coredns
# coredns-6d4b75cb6d-8j9xz   1/1   Running   0   2m
# coredns-6d4b75cb6d-9k0yz   1/1   Running   0   2m


# ──────────────────────────────────────────────────────────────────────────
# 8.6 DEPLOY ANIHPJ APPLICATIONS
# ──────────────────────────────────────────────────────────────────────────

# Create namespace:
kubectl create namespace anihpj-prod

# Deploy webapp:
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  namespace: anihpj-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: registry.anihpj.io/webapp:v1.2.3
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

# Expose as a Service:
kubectl expose deployment webapp -n anihpj-prod \
  --port=8080 --target-port=8080 --name=webapp-svc

# Create Ingress:
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp-ingress
  namespace: anihpj-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - anihpj.io
    secretName: anihpj-tls
  rules:
  - host: anihpj.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp-svc
            port:
              number: 8080
EOF

# Verify:
kubectl get all -n anihpj-prod
curl -k https://anihpj.io/api/jobs


# ============================================================================
# PART 9: DAY 2 MAINTENANCE CHEAT SHEET
# ============================================================================

# ── Cluster Health ──
kubectl get nodes -o wide                          # All nodes status
kubectl get pods -A --field-selector=status.phase!=Running  # Non-running Pods
kubectl get cs                                     # Component status (deprecated but useful)
kubectl cluster-info dump                          # Full cluster diagnostics

# ── etcd Operations ──
kubectl -n kube-system exec -it etcd-cp-01 -- etcdctl endpoint health --cluster
kubectl -n kube-system exec -it etcd-cp-01 -- etcdctl endpoint status --write-out=table
# Full etcdctl reference: See Part 6.11

# ── Certificate Management ──
kubeadm certs check-expiration                     # When do certs expire?
kubeadm certs renew all                            # Renew everything
# Then restart static Pods (see Part 7.3)

# ── Node Maintenance ──
kubectl drain wk-04 --ignore-daemonsets --delete-emptydir-data  # Evacuate Pods
kubectl cordon wk-04                                # Mark unschedulable
kubectl uncordon wk-04                              # Mark schedulable again

# ── Upgrade ──
kubeadm upgrade plan                                # What versions are available?
kubeadm upgrade apply v1.32.0                       # Upgrade CP (on first CP node)
kubeadm upgrade node                                # Upgrade this node
# Full upgrade process: See Part 7.1

# ── Diagnostics ──
journalctl -u kubelet -n 100 --no-pager            # Kubelet logs
journalctl -u containerd -n 100 --no-pager         # Container runtime logs
crictl ps -a                                        # List ALL containers
crictl logs <container-id>                          # Container logs
kubectl describe node wk-04 | grep -A10 Conditions # Node conditions
kubectl get events -A --sort-by='.lastTimestamp'    # Recent cluster events

# ── Bootstrap Token Management ──
kubeadm token list                                  # Active tokens
kubeadm token create --print-join-command           # New token + join command
kubeadm token delete <token-id>                     # Revoke a token

# ── Reset (DESTROY the node's K8s state) ──
kubeadm reset -f                                    # Wipes /etc/kubernetes/, stops kubelet
rm -rf /etc/cni/net.d /var/lib/kubelet /var/lib/etcd
iptables -F && iptables -t nat -F && iptables -t mangle -F
ip link delete cni0 2>/dev/null
ip link delete flannel.1 2>/dev/null
systemctl restart containerd
# Now the node is clean and can be re-joined
'''

# ── Read existing Part 6 and append ──
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.txt', 'r', encoding='utf-8') as f:
    old = f.read()
part6_start = old.find('# PART 6: ETCD')
if part6_start > 0:
    content += '\n\n' + old[part6_start:]

print(f'Total lines: {len(content.splitlines())}')
with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print('File written successfully.')
