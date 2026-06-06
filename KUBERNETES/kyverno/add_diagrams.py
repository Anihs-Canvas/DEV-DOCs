"""Add illustrative diagrams throughout k8s-cluster-structure.txt"""
import re

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.txt'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Each entry: (unique_marker_string, new_insertion_text, insert_position)
# Position: 'before' or 'after' the marker
injections = []

# ══════════════════════════════════════════════════════════════════════════
# PART 0: NODE SPECS TABLE + CLUSTER CAPACITY CARD (after topology diagram)
# ══════════════════════════════════════════════════════════════════════════
inj1 = {
    'marker': 'Pod CIDR per node: /26              (64 Pod IPs per worker node)',
    'after': '''└──────────────────────────────────────────────────────────────────────────────┘


# ──────────────────────────────────────────────────────────────────────────
# 0.1 NODE SPECIFICATIONS — HARDWARE & SOFTWARE INVENTORY
# ──────────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              NODE INVENTORY & SPECIFICATIONS                                              │
├──────────┬──────────────┬──────────┬──────────┬────────────┬──────────────────┬──────────────────────────────────────────┤
│   NODE   │      IP      │   ROLE   │  CPUs    │    RAM     │       DISK       │              SOFTWARE                    │
├──────────┼──────────────┼──────────┼──────────┼────────────┼──────────────────┼──────────────────────────────────────────┤
│  cp-01   │  10.0.0.10   │  CP (L)  │  4 vCPU  │   16 GB    │  100 GB SSD      │  Ubuntu 24.04, kubeadm v1.31,            │
│          │              │          │          │            │                  │  containerd v1.7, kubelet v1.31,         │
│          │              │          │          │            │                  │  etcd v3.5, Calico v3.28                 │
├──────────┼──────────────┼──────────┼──────────┼────────────┼──────────────────┼──────────────────────────────────────────┤
│  cp-02   │  10.0.0.11   │  CP (F)  │  4 vCPU  │   16 GB    │  100 GB SSD      │  Ubuntu 24.04, kubeadm v1.31,            │
│          │              │          │          │            │                  │  containerd v1.7, kubelet v1.31,         │
│          │              │          │          │            │                  │  etcd v3.5, Calico v3.28                 │
├──────────┼──────────────┼──────────┼──────────┼────────────┼──────────────────┼──────────────────────────────────────────┤
│  cp-03   │  10.0.0.12   │  CP (F)  │  4 vCPU  │   16 GB    │  100 GB SSD      │  Ubuntu 24.04, kubeadm v1.31,            │
│          │              │          │          │            │                  │  containerd v1.7, kubelet v1.31,         │
│          │              │          │          │            │                  │  etcd v3.5, Calico v3.28                 │
├──────────┼──────────────┼──────────┼──────────┼────────────┼──────────────────┼──────────────────────────────────────────┤
│  wk-01   │  10.0.4.21   │  worker  │  4 vCPU  │   16 GB    │  200 GB SSD      │  Ubuntu 24.04, kubeadm v1.31,            │
│  wk-02   │  10.0.4.22   │  worker  │  4 vCPU  │   16 GB    │  200 GB SSD      │  containerd v1.7, kubelet v1.31,         │
│  wk-03   │  10.0.4.23   │  worker  │  8 vCPU  │   32 GB    │  500 GB SSD      │  kube-proxy v1.31, Calico v3.28          │
│  wk-04   │  10.0.4.24   │  worker  │  8 vCPU  │   32 GB    │  500 GB SSD      │  (wk-03/wk-04 are high-capacity          │
│  wk-05   │  10.0.4.25   │  worker  │  4 vCPU  │   16 GB    │  200 GB SSD      │   nodes for database workloads)          │
├──────────┼──────────────┼──────────┼──────────┼────────────┼──────────────────┼──────────────────────────────────────────┤
│  fe-01   │  10.0.5.10   │ frontend │  2 vCPU  │    8 GB    │   80 GB SSD      │  Ubuntu 24.04, nginx v1.27,              │
│  fe-02   │  10.0.5.11   │ frontend │  2 vCPU  │    8 GB    │   80 GB SSD      │  certbot (LetsEncrypt)                   │
└──────────┴──────────────┴──────────┴──────────┴────────────┴──────────────────┴──────────────────────────────────────────┘

       CP = Control Plane    L = etcd Leader    F = etcd Follower


# ──────────────────────────────────────────────────────────────────────────
# 0.2 CLUSTER CAPACITY — RESOURCE BUDGET
# ──────────────────────────────────────────────────────────────────────────

┌──────────────────────────────────────────────────────────────────┐
│                    CLUSTER CAPACITY OVERVIEW                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   TOTAL vCPUs:     54 cores  (3×4 CP + 5 worker + 2×2 FE)      │
│   TOTAL RAM:       212 GB   (3×16 CP + workers + 2×8 FE)       │
│   TOTAL DISK:      2.3 TB   (3×100 CP + workers + 2×80 FE)     │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              RESOURCE ALLOCATION BREAKDOWN               │    │
│   │                                                         │    │
│   │  System Reserved (kubelet systemReserved + kubeReserved):│    │
│   │    Per node: 750m CPU + 1.5 GB RAM                       │    │
│   │    Cluster-wide: 7.5 CPU + 15 GB RAM                     │    │
│   │                                                         │    │
│   │  Available for Pods (after system overhead):              │    │
│   │    Control plane: ~3.25 CPU + ~14.5 GB RAM per node      │    │
│   │    Workers (wk-01/02/05): ~3.25 CPU + ~14.5 GB RAM       │    │
│   │    Workers (wk-03/04): ~7.25 CPU + ~30.5 GB RAM          │    │
│   │                                                         │    │
│   │  Max Pods (110 per node × 10 nodes):  1,100 Pods         │    │
│   │  Pod IPs (/26 per worker × 5):         320 Pod IPs       │    │
│   │  Service ClusterIPs (/12):        1,048,576 addresses    │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘''',
}
injections.append(inj1)

# ══════════════════════════════════════════════════════════════════════════
# PART 1.1: KUBEADM WORKFLOW TIMELINE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════
inj2 = {
    'marker': 'Phase 6: DEPLOY APPLICATIONS\n    └── kubectl apply -f anihpj-webapp.yaml, etc.',
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 1.1a KUBEADM BOOTSTRAP TIMELINE — VISUAL OVERVIEW
# ──────────────────────────────────────────────────────────────────────────

Time ─────────────────────────────────────────────────────────────────────►
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
│  │ contain│      │ certs  │    │ certs  │    │  with  │     │ Calico │   │
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
│  └─────────────────────────────────────────────────────────────────────┘  │''',
}
injections.append(inj2)

# ══════════════════════════════════════════════════════════════════════════
# PART 1.3: KUBEADM PHASES DEPENDENCY TREE
# ══════════════════════════════════════════════════════════════════════════
inj3 = {
    'marker': 'kubeadm init phase certs apiserver --config=kubeadm-config.yaml\n  # Generate ONLY the API server certificate.',
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 1.3a PHASE DEPENDENCY TREE — WHAT DEPENDS ON WHAT
# ──────────────────────────────────────────────────────────────────────────

                          ┌─────────────┐
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
                  └─────────────────┘

Order matters! If a parent phase fails, all children are skipped.''',
}
injections.append(inj3)

# ══════════════════════════════════════════════════════════════════════════
# PART 1.4: CERTIFICATE TRUST CHAIN DIAGRAM
# ══════════════════════════════════════════════════════════════════════════
inj4 = {
    'marker': 'kubeadm init phase upload-certs --upload-certs\n  # Prints: [upload-certs] Using certificate key: a1b2c3d4e5f6...',
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 1.4a CERTIFICATE TRUST CHAIN — WHO SIGNS WHAT
# ──────────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────────┐
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
│   │    /etc/kubernetes/pki/          │                                  │
│   │    front-proxy-ca.crt            │                                  │
│   └────────────┬─────────────────────┘                                  │
│                │ SIGNS                                                   │
│                ▼                                                        │
│        ┌──────────────┐                                                 │
│        │ front-proxy  │                                                 │
│        │ -client.crt  │                                                 │
│        └──────────────┘                                                 │
│                                                                         │
│   ┌──────────────────────────────────┐                                  │
│   │    ETCD CA                       │  ← Separate CA for etcd         │
│   │    /etc/kubernetes/pki/etcd/     │     (best practice)             │
│   │    ca.crt                        │                                  │
│   └────────────┬─────────────────────┘                                  │
│                │ SIGNS                                                   │
│     ┌──────────┼──────────────┬───────────────┐                         │
│     ▼          ▼              ▼               ▼                         │
│ ┌───────┐ ┌────────┐ ┌──────────────┐ ┌──────────────┐                 │
│ │ etcd  │ │ etcd   │ │ healthcheck  │ │ apiserver-   │                 │
│ │ server│ │ peer   │ │ -client.crt  │ │ etcd-client  │                 │
│ │ .crt  │ │ .crt   │ │              │ │ .crt         │                 │
│ └───────┘ └────────┘ └──────────────┘ └──────────────┘                 │
│                                                                         │
│  Key Insight: etcd has its OWN CA, separate from the cluster CA.        │
│  This means etcd trust is isolated — compromising the cluster CA        │
│  does NOT give access to etcd directly.                                 │
└─────────────────────────────────────────────────────────────────────────┘''',
}
injections.append(inj4)

# ══════════════════════════════════════════════════════════════════════════
# PART 1.5: JOIN SEQUENCE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════
inj5 = {
    'marker': 'CA cert hash: sha256 of the CA certificate — prevents MITM during join',
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 1.5a JOIN SEQUENCE — WORKER NODE
# ──────────────────────────────────────────────────────────────────────────

  New Node (wk-04)                    API Server (10.0.0.100:6443)         cp-01 (kubelet)
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

  Total time: ~30-60 seconds per worker node (after the join command)


# ──────────────────────────────────────────────────────────────────────────
# 1.5b JOIN SEQUENCE — CONTROL PLANE NODE (ADDITIONAL STEPS)
# ──────────────────────────────────────────────────────────────────────────

  New CP (cp-02)                     API Server                    cp-01 (etcd Leader)
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

  Total time: ~60-90 seconds per CP join (most time spent syncing etcd data)''',
}
injections.append(inj5)

# ══════════════════════════════════════════════════════════════════════════
# PART 3: POD LIFECYCLE STATE MACHINE (after the static pod manifests)
# ══════════════════════════════════════════════════════════════════════════
inj6 = {
    'marker': '# ============================================================================\n# PART 4: KEY DIRECTORY QUICK REFERENCE (EXPANDED)',
    'before': '''# ──────────────────────────────────────────────────────────────────────────
# 3.3 POD LIFECYCLE — STATE MACHINE DIAGRAM
# ──────────────────────────────────────────────────────────────────────────

Every Pod goes through this exact lifecycle. Understanding it is critical
for debugging why a Pod is stuck:

                    ┌─────────┐
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
    │(exit 0)  │ │(exit ≠0) │ │ LoopBack │
    │Job done  │ │Fatal err │ │  Off     │
    └──────────┘ └──────────┘ └────┬─────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │  Evicted │  ← Node under pressure (disk/memory)
                            │ Terminat-│      Kubelet evicted the Pod
                            │   ing    │
                            └──────────┘

Pod Conditions (kubectl describe pod):
  PodScheduled   → True if assigned to a node
  Initialized    → True if init containers completed
  ContainersReady→ True if all containers passed readiness probes
  Ready          → True if Pod can receive traffic (added to Service endpoints)
  DisruptionTarget→ True if Pod is being evicted (preemption/PDB)


# ──────────────────────────────────────────────────────────────────────────
# 3.4 CONTAINER RUNTIME ARCHITECTURE — HOW CONTAINERD RUNS A POD
# ──────────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────────┐
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
└─────────────────────────────────────────────────────────────────────────┘


''',
}
injections.append(inj6)

# ══════════════════════════════════════════════════════════════════════════
# PART 4: ADD FILESYSTEM VISUAL MAP
# ══════════════════════════════════════════════════════════════════════════
inj7 = {
    'marker': '/opt/anihpj/                       │ Application binaries & data',
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 4.1 FILESYSTEM HEAT MAP — WHAT LIVES WHERE (BY NODE TYPE)
# ──────────────────────────────────────────────────────────────────────────

┌──────────────────────────────┬───────────┬───────────┬───────────┐
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
│ /opt/anihpj/                 │     -     │    ⭐     │     -     │
│ /etc/nginx/                  │     -     │     -     │    ⭐⭐⭐   │
│ /run/containerd.sock         │    ⭐⭐    │    ⭐⭐⭐   │     -     │
│ /run/kubelet/                │    ⭐⭐    │    ⭐⭐    │     -     │
└──────────────────────────────┴───────────┴───────────┴───────────┘

  ⭐⭐⭐ = Critical — node fails without this
  ⭐⭐  = Important — degraded if missing
  ⭐   = Present — helpful but not essential
  -    = Not present on this node type''',
}
injections.append(inj7)

# ══════════════════════════════════════════════════════════════════════════
# PART 5: ADD KUBE-PROXY IPTABLES RULE CHAIN VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════
inj8 = {
    'marker': "Total iptables rules for this ONE Service: ~12 rules",
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 5.5 KUBE-PROXY IPTABLES RULE CHAIN — VISUAL WALKTHROUGH
# ──────────────────────────────────────────────────────────────────────────

Packet arrives on wk-04 destined for ClusterIP 10.96.50.100:8080:

  ┌─────────────────────────────────────────────────────────────────────┐
  │                         NETFILTER HOOKS                             │
  │                                                                     │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │ PREROUTING (raw)                                             │   │
  │  │   │ No rule matches → continue                               │   │
  │  └──────────────────────────┬───────────────────────────────────┘   │
  │                             ▼                                       │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │ PREROUTING (nat)                                             │   │
  │  │   ├── KUBE-SERVICES chain                                    │   │
  │  │   │   ┌─────────────────────────────────────────────────┐    │   │
  │  │   │   │ Match: dst=10.96.50.100, dport=8080             │    │   │
  │  │   │   │ Action: JUMP → KUBE-SVC-WXYZ (Service's chain)  │    │   │
  │  │   │   └─────────────────────┬───────────────────────────┘    │   │
  │  │   │                         ▼                                │   │
  │  │   │   ┌─────────────────────────────────────────────────┐    │   │
  │  │   │   │ KUBE-SVC-WXYZ (Service webapp-svc)              │    │   │
  │  │   │   │                                                 │    │   │
  │  │   │   │  ┌──────────────────────────────────────────┐   │    │   │
  │  │   │   │  │ Rule 1: random 33.3% → KUBE-SEP-AAAA     │   │    │   │
  │  │   │   │  │   DNAT → 10.244.3.45:8080 (wk-03)        │   │    │   │
  │  │   │   │  ├──────────────────────────────────────────┤   │    │   │
  │  │   │   │  │ Rule 2: random 50.0% → KUBE-SEP-BBBB     │   │    │   │
  │  │   │   │  │   DNAT → 10.244.4.72:8080 (wk-04)        │   │    │   │
  │  │   │   │  ├──────────────────────────────────────────┤   │    │   │
  │  │   │   │  │ Rule 3: always match → KUBE-SEP-CCCC     │   │    │   │
  │  │   │   │  │   DNAT → 10.244.5.18:8080 (wk-05)        │   │    │   │
  │  │   │   │  └──────────────────────────────────────────┘   │    │   │
  │  │   │   └─────────────────────────────────────────────────┘    │   │
  │  │   └── (other KUBE-* chains...)                               │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                                                     │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │ POSTROUTING (nat) — MASQUERADE if leaving the node           │   │
  │  │   ├── KUBE-POSTROUTING: SNAT to node IP if needed            │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                                                     │
  │  ┌──────────────────────────────────────────────────────────────┐   │
  │  │ FORWARD — KUBE-FORWARD: ACCEPT if conntrack state is valid   │   │
  │  │   (Allows Pod-to-Pod traffic through the node's bridge)       │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────┘

  Why probability mode? iptables rules are evaluated sequentially. With 3
  endpoints, the probabilities ensure equal distribution:
    - Endpoint 1: 1/3 = 33.3% (hits if random < 0.333)
    - Endpoint 2: 1/2 of remaining 66.7% = 33.3% (hits if random < 0.500)
    - Endpoint 3: 100% of remaining 33.3% = 33.3% (always matches)

  This gives statistically even load distribution without needing a
  separate load balancer process. The cost: O(n) rule evaluation.''',
}
injections.append(inj8)

# ══════════════════════════════════════════════════════════════════════════
# PART 5b: ADD CNI PLUGIN CHAIN VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════
inj9 = {
    'marker': "# The CNI plugin chain executes in order:",
    'after': '''


# ──────────────────────────────────────────────────────────────────────────
# 5.6 CNI PLUGIN EXECUTION CHAIN — WHAT HAPPENS WHEN A POD IS CREATED
# ──────────────────────────────────────────────────────────────────────────

  kubelet: "Create Pod webapp-7d8f on wk-04"
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  CONTAINERD (CRI Runtime)                                       │
  │  1. Pull image: registry.anihpj.io/webapp:v1.2.3                │
  │  2. Create PodSandbox (pause container)                         │
  │  3. Call CNI: "I need network for Pod webapp-7d8f"              │
  └────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  CNI PLUGIN CHAIN (executed in order from .conflist)            │
  │                                                                 │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ STEP 1: CALICO PLUGIN                                   │    │
  │  │  - Allocate IP from node's PodCIDR (10.244.4.72)        │    │
  │  │  - Create veth pair (host side: caliXXXX, pod side: eth0)│   │
  │  │  - Assign IP to pod-side veth                            │    │
  │  │  - Add route: 10.244.4.72 dev caliXXXX                   │    │
  │  │  - Program iptables for NetworkPolicy (if any)           │    │
  │  │  - Advertise /32 route via BGP to other nodes            │    │
  │  │  Result: { "ip4": { "ip": "10.244.4.72/32" } }          │    │
  │  └──────────────────────┬──────────────────────────────────┘    │
  │                         │                                       │
  │                         ▼                                       │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ STEP 2: PORTMAP PLUGIN                                  │    │
  │  │  - Check if Pod spec has hostPort defined                │    │
  │  │  - If yes: add iptables DNAT rule (hostPort → podIP)    │    │
  │  │  - If no: pass through (no-op)                          │    │
  │  └──────────────────────┬──────────────────────────────────┘    │
  │                         │                                       │
  │                         ▼                                       │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ STEP 3: BANDWIDTH PLUGIN                                │    │
  │  │  - Check Pod annotations for bandwidth limits            │    │
  │  │  - kubernetes.io/ingress-bandwidth: "10Mbps"             │    │
  │  │  - kubernetes.io/egress-bandwidth: "5Mbps"               │    │
  │  │  - If set: create tc (traffic control) qdisc on veth     │    │
  │  │  - If not set: pass through (no-op)                     │    │
  │  └─────────────────────────────────────────────────────────┘    │
  │                                                                 │
  │  Result returned to containerd: Pod IP = 10.244.4.72            │
  └─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  kubelet receives Pod IP → updates Pod status                   │
  │  Pod is now reachable at 10.244.4.72 from any node in cluster   │
  └─────────────────────────────────────────────────────────────────┘''',
}
injections.append(inj9)

# ══════════════════════════════════════════════════════════════════════════
# PART 7: ADD UPGRADE TIMELINE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════
inj10 = {
    'marker': '# ============================================================================\n# PART 8: COMPLETE CLUSTER BOOTSTRAP',
    'before': '''# ──────────────────────────────────────────────────────────────────────────
# 7.5 UPGRADE TIMELINE — 1.31.0 → 1.32.0 STEP BY STEP
# ──────────────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────────────────┐
  │                    CLUSTER UPGRADE SEQUENCE                           │
  │                    v1.31.0 → v1.32.0                                 │
  │                                                                      │
  │  STEP 1: cp-01 (PRIMARY CONTROL PLANE)                               │
  │  ┌──────────────────────────────────────────────────────────────┐    │
  │  │ 1a. apt upgrade kubeadm                                       │    │
  │  │ 1b. kubeadm upgrade plan                                      │    │
  │  │ 1c. kubeadm upgrade apply v1.32.0                             │    │
  │  │     → Upgrades static Pods (etcd, apiserver, scheduler, CM)   │    │
  │  │     → Updates kubeadm-config & kubelet-config ConfigMaps      │    │
  │  │     → Upgrades CoreDNS & kube-proxy                           │    │
  │  │ 1d. apt upgrade kubelet kubectl                               │    │
  │  │ 1e. systemctl restart kubelet                                 │    │
  │  └──────────────────────────────────────────────────────────────┘    │
  │  Duration: ~5-10 min (API server briefly unavailable on cp-01)       │
  │                                                                      │
  │  STEP 2: cp-02, cp-03 (OTHER CONTROL PLANE NODES)                    │
  │  ┌──────────────────────────────────────────────────────────────┐    │
  │  │ 2a. apt upgrade kubeadm                                       │    │
  │  │ 2b. kubeadm upgrade node                                      │    │
  │  │     → Upgrades static Pods on THIS node only                  │    │
  │  │ 2c. apt upgrade kubelet kubectl                               │    │
  │  │ 2d. systemctl restart kubelet                                 │    │
  │  └──────────────────────────────────────────────────────────────┘    │
  │  Duration: ~3-5 min each (do one at a time)                          │
  │                                                                      │
  │  STEP 3: wk-01 through wk-05 (WORKERS — ONE AT A TIME)               │
  │  ┌──────────────────────────────────────────────────────────────┐    │
  │  │ 3a. kubectl drain wk-01 --ignore-daemonsets                   │    │
  │  │ 3b. apt upgrade kubeadm                                       │    │
  │  │ 3c. kubeadm upgrade node                                      │    │
  │  │ 3d. apt upgrade kubelet kubectl                               │    │
  │  │ 3e. systemctl restart kubelet                                 │    │
  │  │ 3f. kubectl uncordon wk-01                                    │    │
  │  │ 3g. kubectl wait --for=condition=Ready node/wk-01 --timeout=2m│    │
  │  └──────────────────────────────────────────────────────────────┘    │
  │  Duration: ~5-10 min per worker (depends on Pod rescheduling time)   │
  │                                                                      │
  │  ┌──────────────────────────────────────────────────────────────┐    │
  │  │  ⚠  NEVER upgrade more than one node at a time               │    │
  │  │  ⚠  NEVER skip minor versions (1.30→1.32 NOT supported)     │    │
  │  │  ⚠  ALWAYS drain workers before upgrading                    │    │
  │  │  ⚠  ALWAYS backup etcd before starting the upgrade           │    │
  │  └──────────────────────────────────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────────────┘


# ──────────────────────────────────────────────────────────────────────────
# 7.6 CERTIFICATE RENEWAL LIFECYCLE
# ──────────────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────────────┐
  │                CERTIFICATE LIFECYCLE MANAGEMENT                   │
  │                                                                  │
  │  CA Certificates (10 year validity):                             │
  │  ┌──────────────────────────────────────────────────────┐        │
  │  │ ca.crt ────────────────────────────────────► 2036    │        │
  │  │ front-proxy-ca.crt ────────────────────────► 2036    │        │
  │  │ etcd/ca.crt ───────────────────────────────► 2036    │        │
  │  └──────────────────────────────────────────────────────┘        │
  │                                                                  │
  │  Leaf Certificates (1 year validity — renewed annually):         │
  │  ┌──────────────────────────────────────────────────────┐        │
  │  │ apiserver.crt ─────────────► 2027 ──► RENEW ──► 2028│        │
  │  │ apiserver-kubelet-client ──► 2027 ──► RENEW ──► 2028│        │
  │  │ etcd/server.crt ───────────► 2027 ──► RENEW ──► 2028│        │
  │  │ etcd/peer.crt ─────────────► 2027 ──► RENEW ──► 2028│        │
  │  │ apiserver-etcd-client ─────► 2027 ──► RENEW ──► 2028│        │
  │  └──────────────────────────────────────────────────────┘        │
  │                                                                  │
  │  Check:  kubeadm certs check-expiration                          │
  │  Renew:  kubeadm certs renew all                                 │
  │  Restart: mv /etc/kubernetes/manifests/*.yaml /tmp/ && mv back   │
  │                                                                  │
  │  ⚠  If leaf certs expire → component stops accepting connections │
  │  ⚠  If CA expires → ENTIRE CLUSTER needs to be rebuilt           │
  │  ⚠  Set calendar reminder 30 days before expiry!                │
  └──────────────────────────────────────────────────────────────────┘


# ──────────────────────────────────────────────────────────────────────────
# 7.7 TROUBLESHOOTING DECISION TREE
# ──────────────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────────────┐
  │           "MY POD IS STUCK — WHAT DO I CHECK FIRST?"             │
  │                                                                  │
  │  ┌──────────────────┐                                           │
  │  │ kubectl describe │                                           │
  │  │ pod <name>       │                                           │
  │  └────────┬─────────┘                                           │
  │           │                                                      │
  │           ▼                                                      │
  │  ┌────────────────────────────────────────────┐                  │
  │  │ What does "Status" say?                    │                  │
  │  └──┬──────────┬──────────┬──────────┬───────┘                  │
  │     │          │          │          │                          │
  │     ▼          ▼          ▼          ▼                          │
  │  Pending    Container  CrashLoop  Running                       │
  │             Creating   BackOff    but not                       │
  │                                  Ready                          │
  │     │          │          │          │                          │
  │     ▼          ▼          ▼          ▼                          │
  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────────────┐            │
  │  │ Check│  │ Check│  │kubectl│  │kubectl describe  │            │
  │  │Events│  │Events│  │ logs  │  │pod → Conditions  │            │
  │  │for   │  │for   │  │<pod>  │  │                  │            │
  │  │sched-│  │image │  │--prev │  │Readiness probe   │            │
  │  │uling │  │pull  │  │ious   │  │failing?          │            │
  │  │issues│  │errors│  │       │  │Wrong port/path?  │            │
  │  └──┬───┘  └──┬───┘  └──┬───┘  └────────┬─────────┘            │
  │     │         │         │               │                       │
  │     ▼         ▼         ▼               ▼                       │
  │  No nodes  ImagePull  App bug         Fix probe                  │
  │  with cap- BackOff or or OOMKilled   config or                   │
  │  acity?    wrong tag?                increase                    │
  │  Taints?   Registry                 initialDelay                │
  │  Affinity? auth issue?                                          │
  └──────────────────────────────────────────────────────────────────┘


''',
}
injections.append(inj10)

# ══════════════════════════════════════════════════════════════════════════
# Execute all injections
# ══════════════════════════════════════════════════════════════════════════

for i, inj in enumerate(injections):
    marker = inj['marker']
    if 'after' in inj:
        text = inj['after']
        pos = 'after'
    else:
        text = inj['before']
        pos = 'before'

    if marker not in c:
        print(f'Injection {i+1} FAILED: marker not found')
        print(f'  First 100 chars: {marker[:100]}')
        continue

    if pos == 'after':
        c = c.replace(marker, marker + text, 1)
    else:
        c = c.replace(marker, text + marker, 1)

    print(f'Injection {i+1}: OK ({pos} marker)')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

print(f'\nTotal lines: {len(c.splitlines())}')
print('All diagrams injected successfully.')
