"""Build Part 6 — etcd: The Brain of the Cluster"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 6: ETCD -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-6">
        <h2>🧠 <span class="section-num">Part 6</span> — etcd: The Brain of the Cluster</h2>
        <div class="section-intro">
            <p>etcd is the <strong>single source of truth</strong> for the entire Kubernetes cluster. Every object you create — Pods, Services, Deployments, Secrets, Nodes — is stored as a key-value pair in etcd. If etcd goes down, the cluster has amnesia. If etcd is lost, the cluster is lost. Understanding etcd isn't optional — it's <strong>the most critical skill</strong> for any Kubernetes administrator.</p>
            <p>This deep dive covers everything: Raft consensus internals, the complete data model, how the API server interacts with etcd, MVCC time-travel, performance requirements, backup/restore procedures, TLS security, etcdctl commands, and real disaster scenarios.</p>
        </div>

        <!-- 6.1 WHAT IS ETCD -->
        <h3 id="part-6-1">6.1 What is etcd?</h3>
        <div class="api-block">
            <p>etcd is a <strong>distributed, reliable key-value store</strong> written in Go. It is the persistence layer for Kubernetes — every cluster object lives in etcd and nowhere else.</p>

            <div class="highlight-box">
                <strong>🧠 Why etcd matters:</strong> Without etcd:
                <ul style="margin-top:6px;">
                    <li><code class="inline">kubectl get pods</code> → returns <strong>nothing</strong></li>
                    <li>New Pods → <strong>can't be scheduled</strong> (scheduler reads from etcd via API server)</li>
                    <li>Nodes → <strong>disappear</strong> (kubelet heartbeats are stored in etcd)</li>
                    <li>Everything → <strong>the cluster has amnesia</strong></li>
                </ul>
            </div>

            <table>
                <tr><th style="width:180px;">Property</th><th>Value</th></tr>
                <tr><td>Language</td><td>Go</td></tr>
                <tr><td>Consensus Algorithm</td><td>Raft (leader + followers)</td></tr>
                <tr><td>API</td><td>gRPC-based (etcd v3 API)</td></tr>
                <tr><td>Data Format</td><td>Protobuf-encoded blobs</td></tr>
                <tr><td>Concurrency Model</td><td>Multi-Version Concurrency Control (MVCC) — every write creates a new revision</td></tr>
                <tr><td>Minimum Production Nodes</td><td><strong>3</strong> (survives 1 node failure)</td></tr>
                <tr><td>Quorum Formula</td><td>(N/2) + 1 → 3-node cluster: quorum = 2, can lose 1</td></tr>
                <tr><td>Data Directory</td><td><code class="inline">/var/lib/etcd</code></td></tr>
                <tr><td>Client Port</td><td><code class="inline">:2379</code> (API server connects here)</td></tr>
                <tr><td>Peer Port</td><td><code class="inline">:2380</code> (etcd-to-etcd communication)</td></tr>
            </table>
        </div>

        <!-- 6.2 RAFT CONSENSUS -->
        <h3 id="part-6-2">6.2 Raft Consensus — How 3 Nodes Agree on State</h3>
        <div class="api-block">
            <p>Raft is the consensus algorithm that keeps all etcd nodes in sync. There is exactly <strong>one Leader</strong> and <strong>two (or more) Followers</strong>. All writes go through the Leader, which replicates them to the Followers.</p>

            <div class="diagram-box">
                <div class="diagram-title">🏛️ Raft Cluster Topology — Leader + Followers</div>
                <div class="ascii-block">                         ┌──────────────┐
                         │   LEADER     │  ← All writes go through the Leader
                         │  (cp-01)     │
                         └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ FOLLOWER │ │ FOLLOWER │ │ FOLLOWER │
              │ (cp-02)  │ │ (cp-03)  │ │ (cp-04)  │
              └──────────┘ └──────────┘ └──────────┘</div>
            </div>

            <h4>Write Flow — What Happens When You Run <code class="inline">kubectl create deployment</code></h4>
            <table>
                <tr><th style="width:40px;">Step</th><th>Component</th><th>Action</th></tr>
                <tr><td>1</td><td>API server</td><td>Receives the create request, validates it, encodes as protobuf</td></tr>
                <tr><td>2</td><td>API server → etcd Leader</td><td>Sends <code class="inline">Put</code> request to the etcd Leader (cp-01)</td></tr>
                <tr><td>3</td><td>etcd Leader (cp-01)</td><td>Appends the entry to its <strong>WAL</strong> (Write-Ahead Log) — this is an fsync'd write to disk</td></tr>
                <tr><td>4</td><td>etcd Leader → Followers</td><td>Sends <code class="inline">AppendEntries</code> RPC to ALL Followers (cp-02, cp-03)</td></tr>
                <tr><td>5</td><td>Followers (cp-02, cp-03)</td><td>Write to their WAL and send <strong>ACK</strong> back to Leader</td></tr>
                <tr><td>6</td><td>etcd Leader</td><td>Once <strong>quorum</strong> (2 out of 3 nodes) ACKs → entry is <strong>COMMITTED</strong></td></tr>
                <tr><td>7</td><td>etcd Leader</td><td>Applies the entry to its state machine (the in-memory B-tree key-value store)</td></tr>
                <tr><td>8</td><td>etcd Leader → API server</td><td>Responds with the new revision number</td></tr>
                <tr><td>9</td><td>API server → kubectl</td><td>Returns <code class="inline">201 Created</code></td></tr>
            </table>

            <h4>Leader Election — What Happens When the Leader Dies</h4>
            <div class="highlight-box">
                <strong>🔁 Election Process:</strong>
                <ul style="margin-top:6px;">
                    <li>If the Leader dies (or fails to send heartbeats within ~100ms), Followers detect a timeout and <strong>start an election</strong></li>
                    <li>Each Follower increments its <strong>term</strong> and votes for ONE candidate (itself or another Follower)</li>
                    <li>A candidate needs <strong>majority</strong> (2 out of 3 votes) to become the new Leader</li>
                    <li><strong>Election timeout:</strong> ~150-300ms — <em>randomized per node</em> to prevent split votes (every node waits a different random duration before starting its election)</li>
                    <li><strong>During election:</strong> NO writes are accepted. Reads still work if quorum exists</li>
                    <li>Once a Leader is elected, it starts sending AppendEntries (heartbeats) and normal operation resumes</li>
                </ul>
            </div>

            <div class="warning">
                <strong>⚠️ The Split-Vote Problem:</strong> In a 3-node cluster, if two Followers start elections at exactly the same time, each votes for itself — neither gets a majority (each has 1 of 3 votes). The election fails, both wait for another random timeout, and try again. This is why the election timeout is <strong>randomized</strong>: it makes simultaneous elections statistically unlikely.
            </div>
        </div>

        <!-- 6.3 ETCD DATA MODEL -->
        <h3 id="part-6-3">6.3 etcd Data Model — How Kubernetes Objects Are Stored</h3>
        <div class="api-block">
            <p>Everything Kubernetes knows is stored under <code class="inline">/registry/</code> as protobuf-encoded bytes. Here's the complete directory tree of the anihpj cluster:</p>

            <div class="diagram-box">
                <div class="diagram-title">📁 /registry/ — The Complete Kubernetes Data Store</div>
                <div class="ascii-block">/registry/
│
├── 📁 namespaces/                         # Namespace definitions
│   ├── 📄 default                         # → k8s.io.api.core.v1.Namespace (protobuf)
│   ├── 📄 kube-system
│   └── 📄 anihpj-prod
│
├── 📁 pods/                               # EVERY Pod in the cluster
│   ├── 📁 default/
│   │   ├── 📄 webapp-7d8f9c6b5-xk2lm     # → k8s.io.api.core.v1.Pod
│   │   │                                  #   Contains: spec (containers, volumes),
│   │   │                                  #            status (phase, hostIP, podIP,
│   │   │                                  #            conditions, containerStatuses)
│   │   └── 📄 nginx-6d4b75cb6d-8j9xz
│   ├── 📁 kube-system/
│   │   ├── 📄 coredns-6d4b75cb6d-8j9xz
│   │   ├── 📄 kube-proxy-wk04
│   │   └── 📄 calico-node-xxxxx
│   └── 📁 anihpj-prod/
│       └── 📄 worker-7b8c9d-xk2lm
│
├── 📁 services/                           # Services & Endpoints
│   ├── 📁 endpoints/
│   │   └── 📁 default/
│   │       └── 📄 webapp-svc             # → Endpoints: {subsets: [{addresses: [
│   │                                      #     {ip: "10.244.3.45"}, {ip: "10.244.4.72"}
│   │                                      #   ], ports: [{port: 8080}]}]}
│   └── 📁 endpointslices/                # Newer, more scalable (max 100 eps/slice)
│       └── 📁 default/
│           └── 📄 webapp-svc-abcde
│
├── 📁 deployments/                        # Deployments
│   └── 📁 default/
│       └── 📄 webapp                     # → replicas, selector, template, strategy
│
├── 📁 replicasets/                        # ReplicaSets (owned by Deployments)
│   └── 📁 default/
│       └── 📄 webapp-7d8f9c6b5           # → OwnerReference → Deployment "webapp"
│
├── 📁 configmaps/                         # ConfigMaps (plain key-value)
│   └── 📁 default/
│       └── 📄 webapp-config              # → data: { DATABASE_URL: "...", DEBUG: "false" }
│
├── 📁 secrets/                            # Secrets (base64-encoded, encrypt at rest recommended)
│   └── 📁 default/
│       └── 📄 db-credentials             # → data: { username: "YWRtaW4=", password: "..." }
│
├── 📁 serviceaccounts/                    # ServiceAccounts
│   └── 📁 default/
│       └── 📄 default                    # → secrets, automountServiceAccountToken
│
├── 📁 nodes/                              # Node objects (registered by kubelet)
│   ├── 📄 cp-01, cp-02, cp-03
│   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05
│   └── 📄 fe-01, fe-02                   # → status.conditions, status.capacity,
│                                          #   status.addresses, spec.taints,
│                                          #   status.nodeInfo (kubeletVersion, osImage,
│                                          #   containerRuntimeVersion, kernelVersion)
│
├── 📁 leases/                             # Leader election & heartbeats
│   ├── 📁 kube-node-lease/               # Node heartbeats (lighter than Node updates)
│   │   ├── 📄 wk-01, wk-02, wk-03, wk-04, wk-05
│   │   └── 📄 cp-01, cp-02, cp-03       # → holderIdentity, renewTime (renewed every 10s)
│   ├── 📁 kube-system/                   # Controller leader elections
│   │   ├── 📄 kube-controller-manager
│   │   └── 📄 kube-scheduler
│   └── 📁 calico-system/
│       └── 📄 calico-typha
│
├── 📁 events/                             # Kubernetes Events (retained ~1 hour)
│   └── 📁 default/
│       ├── 📄 webapp-7d8f.123abc         # → "Pulled image nginx:1.25"
│       └── 📄 webapp-7d8f.123def         # → "Started container nginx"
│
├── 📁 crd/                                # Custom Resource Definitions
│   └── 📁 apiextensions.k8s.io/
│       └── 📁 customresourcedefinitions/
│           ├── 📄 virtualservices.networking.istio.io
│           └── 📄 bgpconfigurations.crd.projectcalico.org
│
├── 📁 persistentvolumes/ & persistentvolumeclaims/
├── 📁 clusterroles/ & clusterrolebindings/
├── 📁 roles/ & rolebindings/
├── 📁 controllerrevisions/
├── 📁 daemonsets/ & statefulsets/ & jobs/ & cronjobs/
├── 📁 ingress/ & networkpolicies/
├── 📁 resourcequotas/ & limitranges/
├── 📁 poddisruptionbudgets/ & priorityclasses/
├── 📁 storageclasses/
└── 📁 mutatingwebhookconfigurations/ & validatingwebhookconfigurations/</div>
            </div>

            <div class="info">
                <strong>💡 Key Insight:</strong> The entire cluster state is just a <strong>key-value tree</strong>. The key is the object path (e.g., <code class="inline">/registry/pods/default/webapp-7d8f9c6b5-xk2lm</code>) and the value is the protobuf-serialized object. etcd doesn't understand Kubernetes objects — it just stores bytes. The API server is the only component that knows how to decode/encode Kubernetes objects.
            </div>
        </div>

        <!-- 6.4 API SERVER INTERACTION -->
        <h3 id="part-6-4">6.4 How the API Server Interacts with etcd</h3>
        <div class="api-block">
            <p>The API server is the <strong>ONLY</strong> component that talks directly to etcd. No other component — kubelet, scheduler, controller-manager, kubectl — ever touches etcd directly. They all go through the API server.</p>

            <table>
                <tr><th style="width:100px;">Operation</th><th style="width:150px;">API Server → etcd</th><th>What Happens</th></tr>
                <tr>
                    <td><strong>LIST</strong></td>
                    <td><code class="inline">Range</code> (prefix scan)</td>
                    <td><code class="inline">kubectl get pods</code> → API server sends a Range request on <code class="inline">/registry/pods/default/</code> (prefix). etcd returns all matching keys sorted by key. The API server decodes each protobuf value and returns JSON.</td>
                </tr>
                <tr>
                    <td><strong>GET</strong></td>
                    <td><code class="inline">Range</code> (single key)</td>
                    <td><code class="inline">kubectl get pod webapp-xxx</code> → Range on the exact key. Returns one key-value pair.</td>
                </tr>
                <tr>
                    <td><strong>WATCH</strong></td>
                    <td><code class="inline">Watch</code> (stream)</td>
                    <td><code class="inline">kubectl get pods -w</code> opens a long-lived gRPC stream. etcd pushes every create/update/delete event in <strong>real time</strong>. This is how controllers (scheduler, deployment controller, kube-proxy) know about changes <strong>instantly</strong> — they all watch the API server, which watches etcd.</td>
                </tr>
                <tr>
                    <td><strong>CREATE</strong></td>
                    <td><code class="inline">Put</code></td>
                    <td>API server validates → admits (webhooks) → encodes as protobuf → <code class="inline">Put</code> to etcd. etcd Leader appends to WAL, replicates to Followers, commits. Returns the new <strong>revision number</strong>.</td>
                </tr>
                <tr>
                    <td><strong>UPDATE</strong></td>
                    <td><code class="inline">Put</code> (same key, new value)</td>
                    <td>Uses <strong>optimistic concurrency</strong> via <code class="inline">resourceVersion</code>. If another client modified the object first → <code class="inline">409 Conflict</code>. The client must re-read and retry. This prevents lost updates without locking.</td>
                </tr>
                <tr>
                    <td><strong>DELETE</strong></td>
                    <td><code class="inline">Delete</code></td>
                    <td>Soft-deletes with a <strong>tombstone</strong> marker. The data isn't physically removed until <strong>compaction</strong> runs later. This allows watches to see the deletion event.</td>
                </tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 Optimistic Concurrency Explained:</strong> Every object in Kubernetes has a <code class="inline">metadata.resourceVersion</code> field. When you update an object, you must send the resourceVersion you read. If etcd's current resourceVersion doesn't match (someone else updated it), the update is rejected with 409 Conflict. This is the same idea as "compare-and-swap" — no locks, no deadlocks, just "try again if someone beat you to it."
            </div>
        </div>

        <!-- 6.5 MVCC & REVISIONS -->
        <h3 id="part-6-5">6.5 etcd MVCC & Revisions — Time Travel in the Database</h3>
        <div class="api-block">
            <p>etcd uses <strong>Multi-Version Concurrency Control (MVCC)</strong>. Every write creates a NEW revision — old values are <strong>preserved</strong> until compaction removes them. This means you can read the state of any key at any historical revision.</p>

            <h4>Timeline of a Pod's Life in etcd Revisions</h4>
            <div class="diagram-box">
                <div class="diagram-title">⏱️ Revision Timeline — /registry/pods/default/webapp-xxx</div>
                <div class="ascii-block">  Revision 100,000: Created          (phase: Pending)
  Revision 100,050: ContainerCreating (image pulled, volumes mounted)
  Revision 100,100: Running          (container started, IP assigned)
  Revision 100,500: Running          (status heartbeat updated)
  Revision 105,000: Running          (another heartbeat update)
  Revision 110,000: Terminating      (deletionTimestamp set, grace period starts)
  Revision 110,001: Deleted          (tombstone marker — removed after compaction)</div>
            </div>

            <table>
                <tr><th style="width:200px;">MVCC Feature</th><th>Why It Matters for Kubernetes</th></tr>
                <tr><td><strong>Historical reads</strong><br><code class="inline">etcdctl get /key --rev=100000</code></td><td>You can read the Pod spec as it was at any past revision. Useful for auditing and debugging "what changed and when."</td></tr>
                <tr><td><strong>Watches from revision</strong><br><code class="inline">etcdctl watch /key --rev=100000</code></td><td>Watches can start from ANY revision, not just "now." If a controller restarts, it can replay events from its last known revision — no events are lost.</td></tr>
                <tr><td><strong>Optimistic concurrency</strong><br><code class="inline">resourceVersion</code></td><td>"Only update if current revision == 110,000." Prevents lost updates when multiple clients modify the same object.</td></tr>
            </table>

            <div class="warning">
                <strong>⚠️ Compaction — The Silent Killer:</strong> Old revisions accumulate and consume disk space. Without compaction, etcd eventually <strong>runs out of disk and dies</strong>. Kubernetes defaults: compact every 5 minutes, keep the last 5 minutes of history. If you need longer history for auditing, increase <code class="inline">--auto-compaction-retention</code> and monitor disk usage. <strong>DO NOT disable compaction.</strong>
            </div>

            <div class="info">
                <strong>💡 Compaction Command:</strong> <code class="inline">etcdctl compaction 110000 --physical</code> removes all revisions older than 110,000 and defragments the database file. The <code class="inline">--physical</code> flag actually shrinks the file on disk (without it, space is just marked as reusable).
            </div>
        </div>

        <!-- 6.6 CLUSTER TOPOLOGY -->
        <h3 id="part-6-6">6.6 etcd Cluster Topology — anihpj's 3-Node Setup</h3>
        <div class="api-block">
            <p>anihpj runs a 3-node etcd cluster <strong>co-located with the control plane</strong> — each CP node runs etcd as a static Pod managed by kubelet:</p>

            <table>
                <tr><th>Node</th><th>IP</th><th>Role</th><th>Peer Port</th><th>Client Port</th></tr>
                <tr><td><strong>cp-01</strong></td><td>10.0.0.10</td><td>Leader</td><td>:2380</td><td>:2379</td></tr>
                <tr><td><strong>cp-02</strong></td><td>10.0.0.11</td><td>Follower</td><td>:2380</td><td>:2379</td></tr>
                <tr><td><strong>cp-03</strong></td><td>10.0.0.12</td><td>Follower</td><td>:2380</td><td>:2379</td></tr>
            </table>

            <h4>Static Pod Manifest — <code class="inline">/etc/kubernetes/manifests/etcd.yaml</code></h4>
            <div class="diagram-box">
                <div class="diagram-title">📄 etcd Static Pod Manifest (on cp-01)</div>
                <pre><code class="language-yaml">apiVersion: v1
kind: Pod
metadata:
  name: etcd
  namespace: kube-system
spec:
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
    - --initial-cluster-state=existing
    - --listen-client-urls=https://127.0.0.1:2379,https://10.0.0.10:2379
    - --listen-peer-urls=https://10.0.0.10:2380
    - --name=cp-01
    - --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
    - --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
    - --peer-client-cert-auth=true
    - --snapshot-count=10000
    - --quota-backend-bytes=8589934592      # 8GB limit
    - --auto-compaction-retention=1         # Compact every 1 hour
    volumeMounts:
    - mountPath: /var/lib/etcd
      name: etcd-data
    - mountPath: /etc/kubernetes/pki/etcd
      name: etcd-certs</code></pre>
            </div>

            <h4>Key Flags Explained</h4>
            <table>
                <tr><th style="width:250px;">Flag</th><th>Purpose</th></tr>
                <tr><td><code class="inline">--initial-cluster</code></td><td>The complete list of ALL etcd members. Must be identical on every node for the cluster to form.</td></tr>
                <tr><td><code class="inline">--initial-cluster-state</code></td><td><code class="inline">"new"</code> for first bootstrap (kubeadm init), <code class="inline">"existing"</code> for joining members (kubeadm join).</td></tr>
                <tr><td><code class="inline">--advertise-client-urls</code></td><td>Where the API server connects (<code class="inline">:2379</code>). Must match what's in the API server's <code class="inline">--etcd-servers</code> flag.</td></tr>
                <tr><td><code class="inline">--listen-peer-urls</code></td><td>Where other etcd members connect (<code class="inline">:2380</code>) for Raft consensus traffic.</td></tr>
                <tr><td><code class="inline">--snapshot-count</code></td><td>Take an automatic snapshot every 10,000 writes. These are critical for recovery.</td></tr>
                <tr><td><code class="inline">--quota-backend-bytes</code></td><td>Maximum database size — <strong>8GB</strong>. etcd raises a NOSPACE alarm at ~7.2GB (90%). ALL writes fail if this is hit.</td></tr>
                <tr><td><code class="inline">--auto-compaction-retention</code></td><td>Compact revisions older than 1 hour. Prevents the database from growing unboundedly.</td></tr>
            </table>
        </div>

        <!-- 6.7 PERFORMANCE -->
        <h3 id="part-6-7">6.7 etcd Performance Requirements</h3>
        <div class="api-block">
            <p>etcd is <strong>extremely sensitive to disk I/O</strong>. Every write calls <code class="inline">fsync()</code> to guarantee data is on physical disk — slow disk = slow cluster.</p>

            <table>
                <tr><th style="width:150px;">Metric</th><th>Requirement</th><th>Why</th></tr>
                <tr><td><strong>Disk type</strong></td><td><span class="badge badge-err">SSD/NVMe REQUIRED</span></td><td>Every etcd write calls fsync() to guarantee data is on physical disk. Spinning disks have 5-10ms fsync latency → etcd becomes unusable.</td></tr>
                <tr><td><strong>Disk latency</strong></td><td>&lt; 10ms p99</td><td>Raft consensus waits for fsync on the Leader AND Followers. If fsync takes more than ~100ms, heartbeats are missed and elections trigger.</td></tr>
                <tr><td><strong>Disk IOPS</strong></td><td>500+ sequential write</td><td>The WAL is append-only (sequential), but snapshots are bulk writes. Both matter.</td></tr>
                <tr><td><strong>Network latency</strong></td><td>&lt; 5ms between members</td><td>Raft heartbeats every 100ms. If latency exceeds this, elections fire. Run CP nodes in the same availability zone.</td></tr>
                <tr><td><strong>Memory</strong></td><td>4-8GB recommended</td><td>etcd caches the entire keyspace in memory (B-tree). More objects = more memory.</td></tr>
                <tr><td><strong>CPU</strong></td><td>2-4 cores</td><td>gRPC processing, protobuf serialization/deserialization, Raft consensus logic.</td></tr>
                <tr><td><strong>Database size</strong></td><td>&lt; 8GB (default)</td><td>Larger = slower snapshot & restore. If your cluster has > 8GB of objects, you need to adjust <code class="inline">--quota-backend-bytes</code>.</td></tr>
            </table>

            <div class="warning">
                <strong>⚠️ The fsync Problem:</strong> If you use network-attached storage (NFS, EBS without Provisioned IOPS, Azure Standard SSD), expect <strong>terrible</strong> performance. The fsync call must flush to physical media — NFS and low-IOPS cloud volumes can take 50-200ms per fsync. This causes frequent leader elections and makes the cluster unstable.
            </div>

            <table>
                <tr><th>Cloud Provider</th><th>Recommended Disk</th><th>Minimum IOPS</th></tr>
                <tr><td>AWS</td><td>EBS gp3 or io2</td><td>3,000 IOPS (gp3) / Provisioned (io2)</td></tr>
                <tr><td>Azure</td><td>Premium SSD or Ultra Disk</td><td>1,200 IOPS (P15)</td></tr>
                <tr><td>GCP</td><td>SSD Persistent Disk</td><td>3,000 IOPS</td></tr>
            </table>
        </div>

        <!-- 6.8 OPERATIONS -->
        <h3 id="part-6-8">6.8 etcd Operations — Backup, Restore, Defrag, Snapshot</h3>
        <div class="api-block">
            <h4>📸 Snapshot (Backup) — THE Most Important etcd Operation</h4>
            <div class="diagram-box">
                <div class="diagram-title">💾 Taking an etcd Snapshot</div>
                <pre><code class="language-bash"># Save a snapshot of the entire keyspace:
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify the snapshot is valid:
etcdctl snapshot status /backup/etcd-snapshot-20260606.db --write-out=table
# +----------+----------+------------+------------+
# |   HASH   | REVISION | TOTAL KEYS | TOTAL SIZE |
# +----------+----------+------------+------------+
# | a1b2c3d4 |   523456 |      1,250 |      256MB |
# +----------+----------+------------+------------+</code></pre>
            </div>

            <table>
                <tr><th style="width:160px;">Backup Schedule</th><th>Details</th></tr>
                <tr><td>Every 6 hours</td><td>Snapshot saved locally on cp-01 at <code class="inline">/backup/</code></td></tr>
                <tr><td>Every 24 hours</td><td>Snapshot uploaded to S3: <code class="inline">s3://anihpj-backups/etcd/</code></td></tr>
                <tr><td>Retention</td><td>30 daily snapshots + 4 weekly snapshots (rotating)</td></tr>
            </table>

            <h4>🔄 Restore — Disaster Recovery Procedure</h4>
            <div class="warning">
                <strong>⚠️ WARNING: This is a DESTRUCTIVE operation.</strong> Only do it when etcd is truly corrupted, lost, or you're rebuilding from backup. All etcd data will be replaced with the snapshot contents.
            </div>

            <div class="diagram-box">
                <div class="diagram-title">🩺 Full Restore Procedure (10 Steps)</div>
                <pre><code class="language-bash"># 1. Stop the API server FIRST (prevent writes during restore):
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/

# 2. On ALL CP nodes, stop etcd:
mv /etc/kubernetes/manifests/etcd.yaml /tmp/

# 3. On the restore node (cp-01), clean old data:
rm -rf /var/lib/etcd
mkdir -p /var/lib/etcd

# 4. Restore the snapshot into a new data directory:
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot-20260606.db \
  --name=cp-01 \
  --initial-cluster=cp-01=https://10.0.0.10:2380,cp-02=https://10.0.0.11:2380,cp-03=https://10.0.0.12:2380 \
  --initial-advertise-peer-urls=https://10.0.0.10:2380 \
  --data-dir=/var/lib/etcd

# 5. On OTHER CP nodes (cp-02, cp-03), CLEAN their data:
rm -rf /var/lib/etcd

# 6. Start etcd on cp-01 first (bootstrap member):
mv /tmp/etcd.yaml /etc/kubernetes/manifests/etcd.yaml

# 7. Once cp-01 is running, start etcd on cp-02 and cp-03:
mv /tmp/etcd.yaml /etc/kubernetes/manifests/etcd.yaml
# They join cp-01's cluster and sync automatically

# 8. Verify cluster health:
etcdctl endpoint health --cluster

# 9. Start the API server:
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# 10. Verify the cluster works:
kubectl get nodes
kubectl get pods -A</code></pre>
            </div>

            <h4>🗜️ Defrag — Reclaim Fragmented Disk Space</h4>
            <div class="info">
                <strong>💡 When to defrag:</strong> etcd stores data in 4KB pages. Over time, deletes leave gaps (fragmentation). The database file size grows even if the actual data size hasn't. If <code class="inline">DB SIZE</code> in <code class="inline">etcdctl endpoint status</code> is near the 8GB quota but actual keyspace is small, you need defrag.
            </div>

            <div class="diagram-box">
                <div class="diagram-title">🗜️ Defrag Procedure</div>
                <pre><code class="language-bash"># Check fragmentation:
etcdctl endpoint status --write-out=table
# Look at DB SIZE — near 8GB = defrag needed

# Defrag ONE NODE AT A TIME (to avoid quorum loss):
etcdctl defrag --endpoints=https://10.0.0.11:2379

# CAUTION: Defrag LOCKS the database on that node for 30s-5min
# depending on database size. Do it during maintenance windows.
# Never defrag more than one node simultaneously.</code></pre>
            </div>
        </div>

        <!-- 6.9 SECURITY -->
        <h3 id="part-6-9">6.9 etcd Security — TLS, Certificates & Encryption</h3>
        <div class="api-block">
            <p>All etcd communication in production <strong>must be TLS-encrypted</strong>. Kubernetes uses mutual TLS (mTLS) — both client and server authenticate with certificates.</p>

            <table>
                <tr><th style="width:250px;">Certificate</th><th>Purpose</th></tr>
                <tr><td><code class="inline">etcd/server.crt</code></td><td>etcd server identity — the API server verifies this when connecting to etcd</td></tr>
                <tr><td><code class="inline">etcd/server.key</code></td><td>Private key for the server certificate</td></tr>
                <tr><td><code class="inline">etcd/peer.crt</code></td><td>etcd-to-etcd communication between cluster members (Raft consensus traffic)</td></tr>
                <tr><td><code class="inline">etcd/peer.key</code></td><td>Private key for the peer certificate</td></tr>
                <tr><td><code class="inline">etcd/ca.crt</code></td><td>Certificate Authority that signed ALL etcd certificates</td></tr>
                <tr><td><code class="inline">etcd/healthcheck-client.crt</code></td><td>Client cert for kubelet's etcd health checks</td></tr>
                <tr><td><code class="inline">apiserver-etcd-client.crt</code></td><td>API server's client certificate — etcd verifies this on every connection. Only the API server should have this.</td></tr>
            </table>

            <h4>API Server etcd Connection Flags</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔐 API Server → etcd mTLS Configuration</div>
                <pre><code class="language-bash">--etcd-servers=https://10.0.0.10:2379,https://10.0.0.11:2379,https://10.0.0.12:2379
--etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
--etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
--etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key</code></pre>
            </div>

            <div class="warning">
                <strong>⚠️ Encryption at Rest:</strong> On disk, etcd data is stored as plain protobuf in <code class="inline">/var/lib/etcd/member/snap/db</code>. Anyone with root access to a CP node can read <strong>ALL cluster data including Secrets</strong> (they're base64-encoded, not encrypted — base64 is encoding, not encryption). You must enable <strong>EncryptionConfiguration</strong> to protect Secrets at rest.
            </div>

            <h4>EncryptionConfiguration — Protect Secrets at Rest</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔒 EncryptionConfiguration for Secrets</div>
                <pre><code class="language-yaml">apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: &lt;base64-encoded-32-byte-key&gt;
    - identity: {}    # Fallback for reading old plain-text Secrets</code></pre>
            </div>
            <p>Apply to API server with: <code class="inline">--encryption-provider-config=/etc/kubernetes/encryption-config.yaml</code></p>
        </div>

        <!-- 6.10 TROUBLESHOOTING -->
        <h3 id="part-6-10">6.10 Common etcd Issues & Troubleshooting</h3>
        <div class="api-block">
            <table>
                <tr><th style="width:180px;">Issue</th><th>Symptoms</th><th>Fix</th></tr>
                <tr>
                    <td><strong>Database Space Exceeded</strong><br><code class="inline">etcdserver: mvcc: database space exceeded</code></td>
                    <td>ALL writes fail. Cluster goes <strong>READ-ONLY</strong>. <code class="inline">kubectl apply</code> hangs or errors.</td>
                    <td>1. <code class="inline">etcdctl defrag</code> (reclaims fragmented space)<br>2. <code class="inline">etcdctl compaction</code> (removes old revisions)<br>3. Increase <code class="inline">--quota-backend-bytes</code> and restart etcd</td>
                </tr>
                <tr>
                    <td><strong>Slow fsync</strong><br><code class="inline">etcdserver: request timed out</code></td>
                    <td>fsync taking >1 second. Leader steps down. Frequent elections. Cluster unstable.</td>
                    <td>Move etcd data directory to faster storage (SSD/NVMe). Test with: <code class="inline">fio --name=fsync --rw=write --bs=4k --fsync=1 --size=1M</code></td>
                </tr>
                <tr>
                    <td><strong>Frequent Leader Elections</strong><br><code class="inline">etcdserver: leader changed</code></td>
                    <td>Brief write unavailability (~1-3s) during each election. Log shows repeated leader changes.</td>
                    <td>Check network latency between CP nodes (<code class="inline">etcdctl endpoint health --cluster</code>). Must be &lt; 5ms. Check for CPU starvation or disk I/O contention.</td>
                </tr>
                <tr>
                    <td><strong>Lost Quorum</strong><br>(2 out of 3 nodes down)</td>
                    <td>Cluster completely <strong>READ-ONLY</strong>. No writes possible. Existing Pods keep running but no new Pods can be created.</td>
                    <td><strong>DISASTER SCENARIO.</strong> Restore from snapshot on the surviving node (see 6.8 Restore procedure).</td>
                </tr>
                <tr>
                    <td><strong>Corrupted WAL</strong></td>
                    <td>etcd won't start. Log shows <code class="inline">wal: corrupted</code>. Usually caused by unclean shutdown or disk corruption.</td>
                    <td>Remove corrupted WAL files (<code class="inline">rm /var/lib/etcd/member/wal/*.wal</code>) and restore from snapshot: <code class="inline">etcdctl snapshot restore ...</code></td>
                </tr>
            </table>
        </div>

        <!-- 6.11 ETCDCTL REFERENCE -->
        <h3 id="part-6-11">6.11 etcdctl Command Reference</h3>
        <div class="api-block">
            <p>Set up the environment (or pass flags to each command):</p>
            <div class="diagram-box">
                <div class="diagram-title">⚙️ etcdctl Environment Setup</div>
                <pre><code class="language-bash">export ETCDCTL_API=3
export ETCDCTL_ENDPOINTS=https://127.0.0.1:2379
export ETCDCTL_CACERT=/etc/kubernetes/pki/etcd/ca.crt
export ETCDCTL_CERT=/etc/kubernetes/pki/etcd/server.crt
export ETCDCTL_KEY=/etc/kubernetes/pki/etcd/server.key</code></pre>
            </div>

            <table>
                <tr><th style="width:280px;">Command</th><th>Purpose</th></tr>
                <tr><td colspan="2"><strong>🩺 Health & Status</strong></td></tr>
                <tr><td><code class="inline">etcdctl endpoint health</code></td><td>Is the local member healthy?</td></tr>
                <tr><td><code class="inline">etcdctl endpoint health --cluster</code></td><td>Check ALL members' health</td></tr>
                <tr><td><code class="inline">etcdctl endpoint status --write-out=table</code></td><td>DB size, leader, raft index, revision per member</td></tr>
                <tr><td><code class="inline">etcdctl member list --write-out=table</code></td><td>All members with peer URLs</td></tr>
                <tr><td colspan="2"><strong>📖 Read / ✏️ Write</strong></td></tr>
                <tr><td><code class="inline">etcdctl put /test/key "hello world"</code></td><td>Write a key-value pair</td></tr>
                <tr><td><code class="inline">etcdctl get /test/key</code></td><td>Read a key (with metadata)</td></tr>
                <tr><td><code class="inline">etcdctl get /test/key --print-value-only</code></td><td>Read just the value, no metadata</td></tr>
                <tr><td><code class="inline">etcdctl get /registry/pods --prefix --keys-only</code></td><td>List ALL Pods in the cluster</td></tr>
                <tr><td><code class="inline">etcdctl get /registry/ --prefix --keys-only | wc -l</code></td><td>Count ALL Kubernetes objects</td></tr>
                <tr><td colspan="2"><strong>👁️ Watch</strong></td></tr>
                <tr><td><code class="inline">etcdctl watch /registry/pods --prefix</code></td><td>Stream all Pod changes in real time</td></tr>
                <tr><td colspan="2"><strong>🔧 Maintenance</strong></td></tr>
                <tr><td><code class="inline">etcdctl snapshot save /backup/snapshot.db</code></td><td>Save a full snapshot</td></tr>
                <tr><td><code class="inline">etcdctl snapshot status /backup/snapshot.db --write-out=table</code></td><td>Verify snapshot integrity</td></tr>
                <tr><td><code class="inline">etcdctl snapshot restore /backup/snapshot.db --data-dir=/var/lib/etcd-new</code></td><td>Restore a snapshot into a new data directory</td></tr>
                <tr><td><code class="inline">etcdctl defrag --endpoints=https://10.0.0.10:2379</code></td><td>Defragment (reclaim disk space)</td></tr>
                <tr><td><code class="inline">etcdctl compaction 523456 --physical</code></td><td>Compact old revisions + physically shrink file</td></tr>
                <tr><td><code class="inline">etcdctl alarm list</code></td><td>Check for alarms (NOSPACE, etc.)</td></tr>
                <tr><td><code class="inline">etcdctl alarm disarm</code></td><td>Clear alarms after fixing the issue</td></tr>
            </table>
        </div>

        <!-- 6.12 COMPONENT INTERACTION MAP -->
        <h3 id="part-6-12">6.12 How Each Kubernetes Component Uses etcd</h3>
        <div class="api-block">
            <table>
                <tr><th style="width:180px;">Component</th><th>Direct etcd Access?</th><th>How It Uses etcd</th></tr>
                <tr><td><strong>kube-apiserver</strong></td><td>✅ YES — the ONLY direct client</td><td>Reads and writes ALL objects. Maintains an in-memory <strong>watch cache</strong> to reduce etcd load — instead of querying etcd for every LIST, it serves from its cache.</td></tr>
                <tr><td><strong>kubelet</strong></td><td>❌ No</td><td>Reports node/Pod status via API server. Node heartbeats → API server → PUT <code class="inline">/registry/leases/kube-node-lease/...</code></td></tr>
                <tr><td><strong>kube-scheduler</strong></td><td>❌ No</td><td>Watches API server for unassigned Pods. API server WATCHes etcd → pushes events to scheduler via watch stream.</td></tr>
                <tr><td><strong>kube-controller-mgr</strong></td><td>❌ No</td><td>Watches API server for changes. E.g., Deployment controller: "I see desired=5, current=3 → create 2 more Pods via API server." All changes go through API server.</td></tr>
                <tr><td><strong>kube-proxy</strong></td><td>❌ No</td><td>Watches API server for Service/Endpoint changes. Programs local iptables/IPVS rules on each node.</td></tr>
                <tr><td><strong>kubectl</strong></td><td>❌ No</td><td>All commands go through API server. Never talks to etcd directly.</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 The Architecture Principle:</strong> etcd is the API server's database. <strong>Everything goes through the API server.</strong> This is why the API server is the most critical component — if it's down, the cluster still runs (existing Pods, kube-proxy rules, DNS) but you can't make any changes. The API server is the gatekeeper: it validates, authenticates, authorizes, admits (webhooks), and transforms objects before they reach etcd.
            </div>
        </div>

        <!-- 6.13 DISASTER SCENARIOS -->
        <h3 id="part-6-13">6.13 etcd Disaster Scenarios — What Happens When Things Go Wrong</h3>
        <div class="api-block">
            <table>
                <tr><th style="width:200px;">Scenario</th><th>Impact</th><th>Recovery</th></tr>
                <tr>
                    <td><strong>Scenario A:<br>1 etcd node fails</strong><br>(cp-03 down)</td>
                    <td>✅ Cluster still has <strong>quorum (2/3)</strong>. Writes continue. Reads continue. All operations normal. No user impact.</td>
                    <td>Replace the failed node within hours. No data loss. No downtime.</td>
                </tr>
                <tr>
                    <td><strong>Scenario B:<br>2 etcd nodes fail</strong><br>(cp-02 AND cp-03 down)</td>
                    <td>🔴 <strong>QUORUM LOST</strong> — cluster is READ-ONLY.<br>• <code class="inline">kubectl apply</code> → hangs or errors<br>• New Pods → can't be created<br>• Existing Pods → <strong>KEEP RUNNING</strong><br>• kube-proxy → keeps working (iptables rules are local)<br>• DNS → keeps working (CoreDNS pods keep running)<br>• But: <strong>no changes</strong> possible</td>
                    <td>Restore from snapshot on the surviving node (see 6.8). <strong>Do NOT try to restart the failed nodes</strong> — they may have divergent state.</td>
                </tr>
                <tr>
                    <td><strong>Scenario C:<br>All 3 etcd nodes fail</strong></td>
                    <td>🔴🔴 <strong>Complete cluster state loss.</strong><br>• All running Pods KEEP RUNNING (they don't know etcd is down)<br>• BUT: once Pods crash, they <strong>can't be recreated</strong><br>• You have <strong>hours</strong> (not minutes) to recover</td>
                    <td>Restore from the <strong>most recent backup snapshot</strong>. You lose any state created after the snapshot. This is why regular backups are non-negotiable.</td>
                </tr>
            </table>

            <div class="highlight-box">
                <strong>🥇 Golden Rule of etcd:</strong> The more backups you have, the better you sleep. Test your restore procedure <strong>monthly</strong>. A backup you haven't tested is not a backup — it's a hope. And hope is not a disaster recovery strategy.
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-6">
        <h2>🧠 <span class="section-num">Part 6</span> — etcd: The Brain of the Cluster</h2>
        <div class="section-intro"><p>Raft consensus, data model, MVCC, performance, backup/restore, security, troubleshooting, and disaster recovery scenarios.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 6: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, ASCII: {content.count("ascii-block")}, Diagrams: {content.count("diagram-box")}')
print(f'Code blocks: {content.count("<pre><code")}, Highlights: {content.count("highlight-box")}, Warnings: {content.count("warning")}, Infos: {content.count("class=\"info\"")}')
