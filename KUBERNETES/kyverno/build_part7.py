"""Build Part 7 — kubeadm Day 2 Operations"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 7: KUBEADM DAY 2 OPS -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-7">
        <h2>🔄 <span class="section-num">Part 7</span> — kubeadm Day 2 Operations</h2>
        <div class="section-intro">
            <p>Installing Kubernetes is Day 1. <strong>Keeping it running, upgraded, and healthy</strong> is Day 2 — and that's where the real work happens. This section covers every operational task you'll encounter as a cluster administrator: version upgrades across all 10 nodes, replacing failed nodes, rotating certificates before they expire, troubleshooting the most common failures, and following decision trees when things go wrong.</p>
            <p>Every command shown is a <strong>copy-paste ready shell snippet</strong> tested on the anihpj cluster (Ubuntu 24.04, Kubernetes v1.31.x).</p>
        </div>

        <!-- 7.1 UPGRADING -->
        <h3 id="part-7-1">7.1 Upgrading the Cluster with kubeadm</h3>
        <div class="api-block">
            <p>kubeadm supports upgrading <strong>one minor version at a time</strong> (e.g., 1.31 → 1.32). You <strong>cannot skip</strong> minor versions — 1.30 → 1.32 is NOT supported. Each upgrade follows a strict sequence: <strong>Control Plane first, Workers second, one node at a time.</strong></p>

            <div class="warning">
                <strong>⚠️ Pre-Upgrade Checklist:</strong>
                <ul style="margin-top:6px;">
                    <li>✅ <strong>Backup etcd</strong> — snapshot before touching anything (see Part 6.8)</li>
                    <li>✅ <strong>Read the release notes</strong> — check for breaking changes and deprecated API removals</li>
                    <li>✅ <strong>Verify CNI compatibility</strong> — is Calico v3.28 compatible with the new k8s version?</li>
                    <li>✅ <strong>Check the upgrade plan</strong> — <code class="inline">kubeadm upgrade plan</code> tells you exactly what will change</li>
                    <li>✅ <strong>Schedule a maintenance window</strong> — API server may be briefly unavailable during CP upgrades</li>
                </ul>
            </div>

            <h4>Step 1: Upgrade kubeadm on the FIRST Control Plane Node (cp-01)</h4>
            <div class="diagram-box">
                <div class="diagram-title">📦 Step 1 — Upgrade kubeadm binary</div>
                <pre><code class="language-bash"># On cp-01 ONLY:
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm</code></pre>
            </div>

            <h4>Step 2: Verify the Upgrade Plan</h4>
            <div class="diagram-box">
                <div class="diagram-title">📋 Step 2 — Check what kubeadm will upgrade</div>
                <pre><code class="language-bash">kubeadm upgrade plan
# Output shows:
#   - Current version: v1.31.0
#   - Available upgrades: v1.31.4 (stable), v1.32.0 (stable)
#   - Components that CAN be upgraded: kube-apiserver, kube-controller-manager,
#       kube-scheduler, kube-proxy, CoreDNS, etcd
#   - Components that MUST be upgraded manually: kubelet (you do this next)</code></pre>
            </div>

            <h4>Step 3: Apply the Upgrade (on cp-01)</h4>
            <div class="diagram-box">
                <div class="diagram-title">🚀 Step 3 — kubeadm upgrade apply</div>
                <pre><code class="language-bash">kubeadm upgrade apply v1.31.4
# This performs:
#   1. Renews certificates if they're close to expiry
#   2. Upgrades static Pod manifests (etcd, apiserver, scheduler, controller-manager)
#   3. Upgrades kubelet configuration on this node
#   4. Updates kubeadm-config and kubelet-config ConfigMaps in the cluster
#   5. Upgrades CoreDNS and kube-proxy addons
#   6. Does NOT upgrade kubelet itself — you do that in Step 4</code></pre>
            </div>

            <div class="info">
                <strong>💡 What "upgrade apply" actually does:</strong> kubeadm reads the current cluster configuration from the <code class="inline">kubeadm-config</code> ConfigMap, compares it with the new version's defaults, and generates updated static Pod manifests in <code class="inline">/etc/kubernetes/manifests/</code>. The kubelet detects the changed manifests and restarts the containers with the new images. The API server is briefly unavailable during this restart (typically 5-30 seconds).
            </div>

            <h4>Step 4: Upgrade kubelet and kubectl on cp-01</h4>
            <div class="diagram-box">
                <div class="diagram-title">📦 Step 4 — Upgrade kubelet + kubectl</div>
                <pre><code class="language-bash">apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.31.4-* kubectl=1.31.4-*
apt-mark hold kubelet kubectl
systemctl daemon-reload
systemctl restart kubelet</code></pre>
            </div>

            <h4>Step 5: Upgrade OTHER Control Plane Nodes (cp-02, cp-03)</h4>
            <div class="diagram-box">
                <div class="diagram-title">📦 Step 5 — Other CP nodes (NON-disruptive)</div>
                <pre><code class="language-bash"># On EACH remaining CP node (cp-02, cp-03):
apt-mark unhold kubeadm
apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm

# kubeadm upgrade node — NOT "upgrade apply"!
# "upgrade node" only upgrades static Pods on THIS node
kubeadm upgrade node

# Then upgrade kubelet+kubectl and restart kubelet:
apt-mark unhold kubelet kubectl
apt-get install -y kubelet=1.31.4-* kubectl=1.31.4-*
apt-mark hold kubelet kubectl
systemctl daemon-reload
systemctl restart kubelet</code></pre>
            </div>

            <h4>Step 6: Upgrade Worker Nodes (wk-01 through wk-05)</h4>
            <p>Workers must be upgraded <strong>one at a time</strong>. For each worker, you <strong>drain</strong> the node first (evict all Pods), upgrade it, then <strong>uncordon</strong> it (allow Pods back):</p>

            <h4>Option A: Manual — One Node at a Time (Safest)</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔄 Option A — Manual Worker Upgrade (wk-01 example)</div>
                <pre><code class="language-bash"># Step A1: Drain the worker (Pods are rescheduled to other workers):
kubectl drain wk-01 --ignore-daemonsets --delete-emptydir-data

# Step A2: SSH to wk-01 and upgrade:
ssh wk-01
apt-mark unhold kubeadm
apt-get install -y kubeadm=1.31.4-*
apt-mark hold kubeadm
kubeadm upgrade node
apt-get install -y kubelet=1.31.4-* kubectl=1.31.4-*
systemctl daemon-reload
systemctl restart kubelet
exit

# Step A3: Uncordon the node (Pods can now be scheduled here again):
kubectl uncordon wk-01

# Step A4: Wait for node to be Ready before proceeding to wk-02:
kubectl wait --for=condition=Ready node/wk-01 --timeout=120s</code></pre>
            </div>

            <h4>Option B: Shell Script — Bulk Upgrade (Faster)</h4>
            <div class="diagram-box">
                <div class="diagram-title">⚡ Option B — Bulk Worker Upgrade Loop</div>
                <pre><code class="language-bash">for node in wk-{01..05}; do
  echo "=== Upgrading $node ==="
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data --timeout=5m
  ssh $node "apt-get update && apt-get install -y kubeadm=1.31.4-* && \
             kubeadm upgrade node && \
             apt-get install -y kubelet=1.31.4-* && \
             systemctl restart kubelet"
  kubectl uncordon $node
  kubectl wait --for=condition=Ready node/$node --timeout=120s
  echo "=== $node complete ==="
done</code></pre>
            </div>

            <div class="highlight-box">
                <strong>🧠 Why "drain before upgrade" matters:</strong> <code class="inline">kubectl drain</code> gracefully evicts all Pods from the node. This ensures zero-downtime for your applications — the Deployment controller sees the evicted Pods and creates replacements on healthy nodes. The <code class="inline">--ignore-daemonsets</code> flag skips DaemonSet Pods (like Calico and kube-proxy) because they can't be evicted — they run on every node by design. <code class="inline">--delete-emptydir-data</code> allows eviction of Pods using emptyDir volumes (the data is lost, which is expected for ephemeral storage).
            </div>
        </div>

        <!-- 7.2 ADDING A NEW NODE -->
        <h3 id="part-7-2">7.2 Adding a New Node to the Cluster</h3>
        <div class="api-block">
            <p>Nodes fail. Hardware dies. Adding a replacement node is a routine operation:</p>

            <div class="info">
                <strong>Scenario:</strong> Worker <code class="inline">wk-04</code> (IP 10.0.4.24) suffered a disk failure and was replaced with a new VM at <code class="inline">10.0.4.30</code>. We need to join the new VM to the cluster.
            </div>

            <table>
                <tr><th style="width:40px;">Step</th><th style="width:120px;">Where</th><th>Command</th><th>What It Does</th></tr>
                <tr>
                    <td>1</td><td>cp-01</td>
                    <td><code class="inline">kubectl delete node wk-04</code></td>
                    <td>Removes the old node from the API server. This cleans up the Node object, associated leases, and tells the scheduler the node is gone.</td>
                </tr>
                <tr>
                    <td>2</td><td>wk-04-new</td>
                    <td><em>(Same prerequisites as initial setup)</em></td>
                    <td>Install containerd, kubeadm, kubelet, kubectl, kernel modules, sysctls — identical to the initial bootstrap (see Part 8).</td>
                </tr>
                <tr>
                    <td>3</td><td>cp-01</td>
                    <td><code class="inline">kubeadm token create --print-join-command</code></td>
                    <td>Generates a new bootstrap token and prints the full <code class="inline">kubeadm join</code> command. Tokens expire after 24 hours by default (<code class="inline">--ttl</code> flag controls this).</td>
                </tr>
                <tr>
                    <td>4</td><td>wk-04-new</td>
                    <td><code class="inline">kubeadm join 10.0.0.100:6443 --token &lt;token&gt; --discovery-token-ca-cert-hash sha256:&lt;hash&gt;</code></td>
                    <td>Joins the new node to the cluster. The kubelet on the new node connects to the API server, registers itself, and starts receiving Pod assignments.</td>
                </tr>
                <tr>
                    <td>5</td><td>cp-01</td>
                    <td><code class="inline">kubectl get nodes</code></td>
                    <td>Verify: <code class="inline">wk-04-new   Ready   worker   30s   v1.31.0</code></td>
                </tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 How bootstrap tokens work:</strong> A bootstrap token is a temporary secret (<code class="inline">bootstrap-token-&lt;id&gt;</code>) stored in the <code class="inline">kube-system</code> namespace. The joining node presents this token to the API server. The API server validates it and returns the cluster CA certificate and a kubelet certificate signed by the cluster CA. After joining, the node uses its own signed certificate — the bootstrap token is no longer needed.
            </div>
        </div>

        <!-- 7.3 RENEWING CERTIFICATES -->
        <h3 id="part-7-3">7.3 Renewing Certificates</h3>
        <div class="api-block">
            <p>Kubernetes certificates have <strong>expiry dates</strong>. Leaf certificates (apiserver, etcd, kubelet) expire after <strong>1 year</strong>. If they expire, components <strong>stop working</strong>. Certificate renewal is a critical recurring task.</p>

            <h4>Check Certificate Expiry</h4>
            <div class="diagram-box">
                <div class="diagram-title">📅 Check All Certificate Expiry Dates</div>
                <pre><code class="language-bash">kubeadm certs check-expiration
[check-expiration] Reading configuration from the cluster...
CERTIFICATE                                  EXPIRES                  RESIDUAL TIME
/etc/kubernetes/pki/apiserver.crt            Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/apiserver-kubelet-client.crt Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/front-proxy-client.crt   Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/server.crt          Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/peer.crt            Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/etcd/healthcheck-client.crt Jan 01 2027 08:00 UTC   208d
/etc/kubernetes/pki/apiserver-etcd-client.crt  Jan 01 2027 08:00 UTC   208d
CERTIFICATE AUTHORITY          EXPIRES                  RESIDUAL TIME
/etc/kubernetes/pki/ca.crt                   Jun 01 2036 08:00 UTC   9y
/etc/kubernetes/pki/front-proxy-ca.crt       Jun 01 2036 08:00 UTC   9y
/etc/kubernetes/pki/etcd/ca.crt              Jun 01 2036 08:00 UTC   9y</code></pre>
            </div>

            <table>
                <tr><th style="width:200px;">Certificate Type</th><th>Validity</th><th>Consequence of Expiry</th></tr>
                <tr><td><strong>Leaf certs</strong> (apiserver, etcd, kubelet client)</td><td>1 year</td><td>Component stops accepting connections. API server becomes unreachable. etcd cluster may lose quorum.</td></tr>
                <tr><td><strong>CA certs</strong> (ca.crt, front-proxy-ca.crt, etcd/ca.crt)</td><td>10 years</td><td>ENTIRE cluster must be rebuilt. All certificates are signed by these CAs — if they expire, nothing trusts anything anymore.</td></tr>
            </table>

            <h4>Renew Certificates</h4>
            <div class="diagram-box">
                <div class="diagram-title">🔄 Renew All or Specific Certificates</div>
                <pre><code class="language-bash"># Renew ALL certificates:
kubeadm certs renew all

# Or renew specific certs:
kubeadm certs renew apiserver
kubeadm certs renew apiserver-etcd-client
kubeadm certs renew etcd-server
kubeadm certs renew admin.conf        # Renew the admin kubeconfig cert</code></pre>
            </div>

            <h4>Restart Components After Renewal (on EVERY CP Node)</h4>
            <p>After renewing certificates, the affected components must be restarted to load the new certs:</p>

            <table>
                <tr><th style="width:100px;">Method</th><th>Command</th><th>Impact</th></tr>
                <tr><td><strong>Option 1:</strong> Move manifest</td><td><code class="inline">mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/</code></td><td>Restarts only the API server static Pod. Minimal disruption (~5-30 seconds).</td></tr>
                <tr><td><strong>Option 2:</strong> crictl stop</td><td><code class="inline">crictl ps | grep kube-apiserver</code> then <code class="inline">crictl stop &lt;container-id&gt;</code></td><td>Same as Option 1 — kubelet detects the stopped container and recreates it.</td></tr>
                <tr><td><strong>Option 3:</strong> Restart kubelet</td><td><code class="inline">systemctl restart kubelet</code></td><td>Restarts ALL static Pods on this node. More disruptive — all control plane components restart.</td></tr>
            </table>

            <div class="diagram-box">
                <div class="diagram-title">🔍 Verify the New Certificate</div>
                <pre><code class="language-bash"># Check the new certificate's validity dates:
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates
# notBefore=Jun  6 08:00:00 2026 GMT
# notAfter=Jun  6 08:00:00 2027 GMT</code></pre>
            </div>

            <div class="warning">
                <strong>⚠️ Certificate Expiry is a Cluster-Killer:</strong> Set a <strong>calendar reminder 30 days before expiry</strong>. If leaf certs expire, the affected component stops working. If the CA expires, the <strong>entire cluster needs to be rebuilt from scratch</strong> — there is no recovery from an expired CA. The CA certs last 10 years, but don't rely on memory.
            </div>
        </div>

        <!-- 7.4 TROUBLESHOOTING -->
        <h3 id="part-7-4">7.4 Troubleshooting kubeadm Clusters</h3>
        <div class="api-block">
            <p>The most common kubeadm errors and exactly how to fix them:</p>

            <table>
                <tr><th style="width:200px;">Error</th><th>Cause & Symptoms</th><th>Fix</th></tr>
                <tr>
                    <td><strong>kubeadm init hangs</strong><br><code class="inline">[wait-control-plane] waiting for the API server...</code></td>
                    <td>API server static Pod isn't starting. Kubelet can't reach the API server.</td>
                    <td><code class="inline">journalctl -u kubelet -f</code> (on cp-01)<br><code class="inline">crictl ps -a | grep kube-apiserver</code><br><code class="inline">crictl logs &lt;apiserver-container-id&gt;</code><br>Common causes: wrong advertise address, port 6443 already in use, etcd not starting, certificate issue.</td>
                </tr>
                <tr>
                    <td><strong>kubeadm join hangs</strong><br><code class="inline">[preflight] Waiting for the control plane...</code></td>
                    <td>Can't reach the API server from the joining node.</td>
                    <td><code class="inline">curl -k https://10.0.0.100:6443/healthz</code> (from the joining node)<br>Is the load balancer forwarding to the right CP nodes?<br>Is the bootstrap token still valid? (<code class="inline">kubeadm token list</code>)<br>Firewall rules: port 6443 must be open between workers and CP.</td>
                </tr>
                <tr>
                    <td><strong>Node shows NotReady after join</strong></td>
                    <td>No CNI plugin installed, OR kubelet can't talk to the container runtime.</td>
                    <td><code class="inline">kubectl describe node wk-04 | grep -A5 Conditions</code><br><code class="inline">journalctl -u kubelet -n 50</code><br><code class="inline">systemctl status containerd</code><br>Is <code class="inline">/run/containerd/containerd.sock</code> present?</td>
                </tr>
                <tr>
                    <td><strong>ip_forward error</strong><br><code class="inline">[ERROR FileContent--proc-sys-net-ipv4-ip_forward]</code></td>
                    <td>Kernel IP forwarding is not enabled.</td>
                    <td><code class="inline">echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.d/99-kubernetes.conf && sysctl --system</code></td>
                </tr>
                <tr>
                    <td><strong>Swap error</strong><br><code class="inline">[ERROR Swap]: running with swap on is not supported</code></td>
                    <td>Swap is enabled. Kubernetes requires swap OFF for predictable memory management and QoS guarantees.</td>
                    <td><code class="inline">swapoff -a && sed -i '/swap/d' /etc/fstab</code></td>
                </tr>
                <tr>
                    <td><strong>Container runtime error</strong><br><code class="inline">container runtime is not running</code></td>
                    <td>containerd is down or the CRI socket doesn't exist.</td>
                    <td><code class="inline">systemctl start containerd && systemctl enable containerd</code><br>Check: <code class="inline">ls -la /run/containerd/containerd.sock</code></td>
                </tr>
                <tr>
                    <td><strong>Kubelet health check failed</strong><br><code class="inline">The HTTP call equal to 'curl -sSL http://localhost:10248/healthz' failed</code></td>
                    <td>Kubelet health check on port 10248 failed.</td>
                    <td><code class="inline">systemctl status kubelet</code><br><code class="inline">journalctl -u kubelet -n 100</code><br>Is the kubeconfig correct? Does the API server respond?</td>
                </tr>
            </table>
        </div>

        <!-- 7.5 UPGRADE TIMELINE -->
        <h3 id="part-7-5">7.5 Upgrade Timeline — Full Sequence Visualized</h3>
        <div class="api-block">
            <p>The complete upgrade sequence from v1.31.0 → v1.32.0 across all 10 nodes:</p>
            <div class="diagram-box">
                <div class="diagram-title">📊 Cluster Upgrade Sequence — v1.31.0 → v1.32.0</div>
                <div class="ascii-block">  ┌──────────────────────────────────────────────────────────────────────┐
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
  └──────────────────────────────────────────────────────────────────────┘</div>
            </div>

            <table>
                <tr><th style="width:100px;">Phase</th><th>Nodes</th><th>Duration</th><th>Downtime</th></tr>
                <tr><td>Primary CP</td><td>cp-01</td><td>5-10 min</td><td>API server brief unavailability (~5-30s)</td></tr>
                <tr><td>Other CPs</td><td>cp-02, cp-03</td><td>3-5 min each</td><td>None (other CPs serve API requests)</td></tr>
                <tr><td>Workers</td><td>wk-01..05</td><td>5-10 min each</td><td>None (Pods rescheduled to other workers)</td></tr>
                <tr><td><strong>Total</strong></td><td><strong>10 nodes</strong></td><td><strong>~45-90 min</strong></td><td><strong>~5-30 seconds</strong></td></tr>
            </table>
        </div>

        <!-- 7.6 CERTIFICATE LIFECYCLE -->
        <h3 id="part-7-6">7.6 Certificate Renewal Lifecycle</h3>
        <div class="api-block">
            <p>Understanding certificate lifetimes is critical for preventing cluster outages:</p>
            <div class="diagram-box">
                <div class="diagram-title">📜 Certificate Lifecycle Management</div>
                <div class="ascii-block">  ┌──────────────────────────────────────────────────────────────────┐
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
  │  Restart: mv manifests to /tmp/ and back                         │
  │                                                                  │
  │  ⚠  If leaf certs expire → component stops accepting connections │
  │  ⚠  If CA expires → ENTIRE CLUSTER needs to be rebuilt           │
  │  ⚠  Set calendar reminder 30 days before expiry!                │
  └──────────────────────────────────────────────────────────────────┘</div>
            </div>

            <div class="highlight-box">
                <strong>🧠 Why CAs last 10 years but leaf certs only 1 year:</strong> The CA is the root of trust — if it changes, every certificate must be reissued and every component must be reconfigured to trust the new CA (essentially rebuilding the cluster). Leaf certs are disposable — they can be reissued and components restarted with no architectural changes. The 1-year rotation limits the window of compromise if a private key is leaked.
            </div>
        </div>

        <!-- 7.7 TROUBLESHOOTING DECISION TREE -->
        <h3 id="part-7-7">7.7 Troubleshooting Decision Tree — "My Pod Is Stuck"</h3>
        <div class="api-block">
            <p>When a Pod isn't working, follow this decision tree to isolate the problem:</p>
            <div class="diagram-box">
                <div class="diagram-title">🔍 Pod Troubleshooting Decision Tree</div>
                <div class="ascii-block">  ┌──────────────────────────────────────────────────────────────────┐
  │           "MY POD IS STUCK — WHAT DO I CHECK FIRST?"             │
  │                                                                  │
  │  ┌──────────────────┐                                           │
  │  │ kubectl describe │                                           │
  │  │ pod &lt;name&gt;       │                                           │
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
  │  │for   │  │for   │  │&lt;pod&gt;  │  │                  │            │
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
  └──────────────────────────────────────────────────────────────────┘</div>
            </div>

            <h4>How to Use This Decision Tree</h4>
            <table>
                <tr><th style="width:100px;">Status</th><th>First Command</th><th>Most Common Fix</th></tr>
                <tr><td><strong>Pending</strong></td><td><code class="inline">kubectl describe pod &lt;name&gt; | grep -A10 Events</code></td><td>Look for "0/X nodes are available" — check node capacity, taints, tolerations, node selectors, and affinity rules.</td></tr>
                <tr><td><strong>ContainerCreating</strong></td><td><code class="inline">kubectl describe pod &lt;name&gt; | grep -A5 Events</code></td><td>Look for "Failed to pull image" — check image name, registry auth (imagePullSecrets), or network connectivity to the registry.</td></tr>
                <tr><td><strong>CrashLoopBackOff</strong></td><td><code class="inline">kubectl logs &lt;pod&gt; --previous</code></td><td>The <code class="inline">--previous</code> flag shows logs from the crashed container. Check for application errors, missing config, OOMKilled, or wrong command/args.</td></tr>
                <tr><td><strong>Running but not Ready</strong></td><td><code class="inline">kubectl describe pod &lt;name&gt; | grep -A10 Conditions</code></td><td>Check the Readiness probe — is the probe path correct? Is the port right? Is <code class="inline">initialDelaySeconds</code> long enough for the app to start?</td></tr>
            </table>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-7">
        <h2>🔄 <span class="section-num">Part 7</span> — kubeadm Day 2 Operations</h2>
        <div class="section-intro"><p>Upgrading the cluster, adding new nodes, renewing certificates, troubleshooting common issues, and maintenance timelines.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Total: {html.count(chr(10))} lines, Part 7: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, ASCII: {content.count("ascii-block")}, Diagrams: {content.count("diagram-box")}')
print(f'Code blocks: {content.count("<pre><code")}, Highlights: {content.count("highlight-box")}, Warnings: {content.count("warning")}, Infos: {content.count("class=\"info\"")}')
