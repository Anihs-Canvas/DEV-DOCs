import re

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\systemd_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the systemctl section boundaries
start_marker = '        <section class="section" id="systemctl-section">'
end_marker = '        <section class="section" id="systemctl-advanced">'

start_idx = c.find(start_marker)
end_idx = c.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('ERROR: could not find section boundaries')
    exit(1)

# Extract parts
before = c[:start_idx]
after = c[end_idx:]

content = '''        <section class="section" id="systemctl-section">
            <h2>⚙ systemctl — Service Management</h2>
            <div class="section-intro">
                <p><code class="inline">systemctl</code> is the central management tool for controlling the systemd system and service manager. On Kubernetes nodes, it manages <strong>kubelet</strong> (the node agent), <strong>containerd</strong> (container runtime), and control plane components such as <strong>kube-apiserver</strong>, <strong>etcd</strong>, <strong>kube-scheduler</strong>, <strong>kube-controller-manager</strong>, and <strong>kube-proxy</strong>.</p>
            </div>
            <!-- ==================== systemctl overview ==================== -->
            <article class="api-block" id="systemctl-overview">
                <h3>systemctl — The Systemd Service Manager</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">CORE</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">Kubernetes Node Services</span>
                </div>
                <p class="api-subtitle">The central management tool for controlling the systemd system and service manager on every Kubernetes node</p>
                <div class="api-description">
                    <p><code class="inline">systemctl</code> is the primary command for interacting with systemd. On Kubernetes nodes, systemd controls the critical services that make the cluster work: <strong>kubelet</strong> registers the node with the API server, <strong>containerd</strong> runs your Pods, and on control plane nodes <strong>kube-apiserver</strong>, <strong>etcd</strong>, <strong>kube-scheduler</strong>, and <strong>kube-controller-manager</strong> orchestrate the cluster.</p>
                    <p>For the <strong>anihpj</strong> platform, each cluster runs 3 control plane nodes and 5 worker nodes. Every node has <code class="inline">kubelet</code> and <code class="inline">containerd</code> managed by systemd. Control plane nodes additionally run the API server, etcd, scheduler, and controller manager as systemd services.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl [OPTIONS...] COMMAND [UNIT...]

# Core commands on a Kubernetes node:
systemctl start kubelet             # Start the K8s node agent
systemctl stop kubelet              # Stop the node agent (node becomes NotReady)
systemctl restart kubelet           # Restart after config change
systemctl status kubelet            # Check node agent health
systemctl status containerd         # Check container runtime
systemctl enable kubelet            # Auto-start node agent at boot
systemctl disable kubelet           # Disable auto-start (drain first!)
systemctl list-units 'kube*'        # List all K8s-related services</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Command</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>start UNIT</code></td><td>Start (activate) one or more units</td></tr>
                        <tr><td><code>stop UNIT</code></td><td>Stop (deactivate) one or more units</td></tr>
                        <tr><td><code>restart UNIT</code></td><td>Stop then start one or more units</td></tr>
                        <tr><td><code>reload UNIT</code></td><td>Reload configuration (no restart)</td></tr>
                        <tr><td><code>status UNIT</code></td><td>Show runtime status and recent logs</td></tr>
                        <tr><td><code>enable/disable UNIT</code></td><td>Enable/disable auto-start at boot</td></tr>
                        <tr><td><code>list-units</code></td><td>List loaded units with state</td></tr>
                        <tr><td><code>daemon-reload</code></td><td>Reload systemd configuration</td></tr>
                    </tbody>
                </table>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — command executed</td></tr><tr><td><code>1</code></td><td>Error — unit not found, permission denied, or operation failed</td></tr></tbody>
                </table>

                <h4>📄 Context — Kubernetes Node Services:</h4>
                <pre><code class="language-bash"># Every Kubernetes node runs these systemd services:
# /etc/systemd/system/kubelet.service       — K8s node agent (registers with API server)
# /etc/systemd/system/containerd.service    — Container runtime (runs your Pods)
# /etc/systemd/system/kube-proxy.service    — Network proxy & load balancer
#
# Control plane nodes additionally run:
# /etc/systemd/system/kube-apiserver.service       — Front-end to the control plane
# /etc/systemd/system/kube-scheduler.service       — Pod scheduler
# /etc/systemd/system/kube-controller-manager.service — Controller loops
# /etc/systemd/system/etcd.service                 — Cluster state database</code></pre>

                <div class="example">
                    <h5>Example 1: Check Kubelet Status</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/systemd/system/kubelet.service — K8s node agent
# The kubelet registers this node with the API server and runs Pods
# Carol checks kubelet health on worker node wk-03 before a maintenance window</code></pre>
                    <p><strong>Scenario:</strong> Carol verifies kubelet is healthy on worker node wk-03 before cordoning it for maintenance.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● kubelet.service — kubelet: The Kubernetes Node Agent
     Loaded: loaded (/etc/systemd/system/kubelet.service; enabled)
     Active: active (running) since Fri 2026-06-06 08:00:00 UTC; 2h ago
   Main PID: 1234 (kubelet)
      Tasks: 12 (limit: 4915)
     Memory: 128.5M
        CPU: 15.345s
     CGroup: /system.slice/kubelet.service
             └─1234 /usr/bin/kubelet --config=/var/lib/kubelet/config.yaml</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet is active (running) — the node will appear as "Ready" in <code>kubectl get nodes</code>. Memory at 128MB is normal. If kubelet stops, the node becomes NotReady and Pods stop being scheduled. Carol can proceed with the maintenance window.</p>
                </div>

                <div class="example">
                    <h5>Example 2: List All Kubernetes Services on a Node</h5>
                    <p><strong>Scenario:</strong> Alice audits all K8s-related services running on a control plane node cp-01.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --type=service 'kube*' 'etcd*' 'container*' --state=running</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                         LOAD   ACTIVE SUB     DESCRIPTION
containerd.service           loaded active running containerd container runtime
etcd.service                 loaded active running etcd — key-value store for K8s
kube-apiserver.service       loaded active running Kubernetes API Server
kube-controller-manager.service loaded active running Kubernetes Controller Manager
kube-proxy.service           loaded active running Kubernetes Network Proxy
kube-scheduler.service       loaded active running Kubernetes Scheduler
kubelet.service              loaded active running kubelet: Kubernetes Node Agent</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Seven K8s services running — this is a healthy control plane node. All critical components are up. <code>kube-apiserver</code> is the front door to the cluster. <code>etcd</code> stores all cluster state. This is the standard health check on any control plane node.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Enable Kubelet to Auto-Start After Reboot</h5>
                    <p><strong>Scenario:</strong> Carol ensures kubelet automatically starts whenever a worker node reboots (critical for node recovery).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable kubelet && systemctl is-enabled kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Created symlink /etc/systemd/system/multi-user.target.wants/kubelet.service → /etc/systemd/system/kubelet.service.
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> A symlink was created — kubelet will auto-start when the node boots and reaches multi-user.target. Without this, an unexpected reboot would leave the node NotReady until someone manually starts kubelet. All Kubernetes nodes MUST have kubelet and containerd enabled.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Check For Failed K8s Services After Kernel Update</h5>
                    <p><strong>Scenario:</strong> Alice checks for failed K8s services on all control plane nodes after a kernel update and reboot.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units 'kube*' 'etcd*' 'container*' --state=failed</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                         LOAD   ACTIVE SUB    DESCRIPTION
kube-scheduler.service       loaded failed failed Kubernetes Scheduler</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The scheduler failed on this control plane node — possibly a stale config reference after the kernel update. Alice runs <code>systemctl status kube-scheduler</code> to see the logs. Failed control plane services are critical — they must be fixed immediately or the cluster loses scheduling capability.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Restart Cycle — Stop containerd & kubelet for Config Update</h5>
                    <p><strong>Scenario:</strong> Dave updates the containerd configuration to change the container runtime endpoint, then restarts both containerd and kubelet.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop kubelet && systemctl stop containerd && echo "Both stopped" && sleep 3 && systemctl start containerd && systemctl start kubelet && systemctl is-active kubelet containerd</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Both stopped
active
active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet stopped first (node becomes NotReady), then containerd. After 3 seconds, containerd starts first, then kubelet. Both are active. During this window, Pods on this node were unreachable. In production, you drain the node first with <code>kubectl drain wk-03 --ignore-daemonsets</code> before stopping kubelet.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> <code>systemctl status kubelet</code> is always the first command on any node showing NotReady. The kubelet and containerd MUST be enabled on every node. Before stopping kubelet on a worker node, ALWAYS drain it: <code>kubectl drain &lt;node&gt; --ignore-daemonsets --delete-emptydir-data</code>. Control plane services (apiserver, etcd, scheduler, controller-manager) should NEVER all be down simultaneously.
                </div>
            </article>

            <!-- ==================== systemctl start ==================== -->
            <article class="api-block" id="systemctl-start">
                <h3>systemctl start</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">START</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                    <span class="tag">containerd</span>
                </div>
                <p class="api-subtitle">Start (activate) one or more systemd units — bring Kubernetes node services online</p>
                <div class="api-description">
                    <p><code class="inline">systemctl start</code> brings a unit into the active state. On Kubernetes nodes, this is used to start <strong>kubelet</strong> (the node agent), <strong>containerd</strong> (the container runtime), and control plane components. If already active, it's a no-op. The <code>.service</code> suffix is assumed if omitted.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl start UNIT...
systemctl start kubelet
systemctl start kubelet.service containerd.service</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Argument</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>UNIT...</code></td><td>One or more units to start</td></tr></tbody>
                </table>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — unit started</td></tr><tr><td><code>1</code></td><td>Error — unit not found or failed to start</td></tr></tbody>
                </table>

                <h4>📄 Context — Starting K8s Node Services:</h4>
                <pre><code class="language-bash"># After a node reboot, kubelet must be running for the node to be Ready:
# systemctl start kubelet
# systemctl start containerd
#
# Kubelet definition in /etc/systemd/system/kubelet.service:
# ExecStart=/usr/bin/kubelet \\
#   --config=/var/lib/kubelet/config.yaml \\
#   --container-runtime-endpoint=unix:///run/containerd/containerd.sock</code></pre>

                <div class="example">
                    <h5>Example 1: Start Kubelet on a Worker Node</h5>
                    <p><strong>Scenario:</strong> Carol starts kubelet on worker node wk-04 after replacing the node's certificate.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start kubelet && systemctl is-active kubelet && kubectl get node wk-04</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active
NAME    STATUS   ROLES    AGE   VERSION
wk-04   Ready    worker   180d  v1.31.0</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet started, registered with the API server, and the node is now "Ready". Within seconds, the scheduler will start placing pending Pods on wk-04. <code>is-active</code> confirms systemd sees it running; <code>kubectl get node</code> confirms the cluster sees the node as healthy.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Start containerd Then kubelet (Dependency Order)</h5>
                    <p><strong>Scenario:</strong> Dave starts the container runtime and node agent in the correct dependency order after a node reboot.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start containerd && systemctl is-active containerd --quiet && echo "containerd ready" && systemctl start kubelet && systemctl start kube-proxy</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">containerd ready</div>
                    <p class="output-note"><strong>📝 What happened:</strong> containerd starts first (kubelet depends on it for running Pods), then kubelet, then kube-proxy. The order matters: container runtime → node agent → networking. systemd handles this automatically if <code>After=</code> and <code>Requires=</code> are set in the unit files.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Start Kubelet and Control Plane Components</h5>
                    <p><strong>Scenario:</strong> Alice starts all services on a rebuilt control plane node cp-03.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start etcd kube-apiserver kube-controller-manager kube-scheduler kubelet && kubectl get cs</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Warning: v1 ComponentStatus is deprecated
NAME                 STATUS    MESSAGE   ERROR
controller-manager   Healthy   ok
scheduler            Healthy   ok
etcd-0               Healthy   ok</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All control plane components started. <code>kubectl get cs</code> (componentstatus) confirms etcd, controller-manager, and scheduler are Healthy. The control plane is now operational. Start etcd first — the API server stores all state there.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Start with Timeout Check</h5>
                    <p><strong>Scenario:</strong> Carol starts kubelet and wants confirmation it registered with the API server within 30 seconds.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start kubelet && for i in $(seq 1 30); do kubectl get node wk-04 --no-headers 2>/dev/null | grep -q Ready && echo "Node Ready after ${i}s" && break || sleep 1; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Node Ready after 8s</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet started locally in ~1s, but took 8s to register with the API server and report Ready. This loop is useful in automation scripts — it waits for the actual cluster-level health check, not just the process status.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Start etcd Backup Timer</h5>
                    <p><strong>Scenario:</strong> Dave activates the etcd snapshot timer on cp-01 after deploying the timer unit.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start etcd-backup.timer && systemctl list-timers etcd-backup.timer</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">NEXT                        LEFT       LAST PASSED  UNIT
Fri 2026-06-07 02:00:00 UTC  17h left   n/a  n/a     etcd-backup.timer</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The etcd backup timer is active — first snapshot at 2 AM. etcd backups are critical for disaster recovery. The timer triggers <code>etcd-backup.service</code> which runs <code>etcdctl snapshot save</code> and uploads to S3.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> Always start <code>containerd</code> before <code>kubelet</code> — kubelet needs the container runtime socket. On control plane nodes, start order: <code>etcd → kube-apiserver → kube-controller-manager → kube-scheduler → kubelet → kube-proxy</code>. Use <code>kubectl get node</code> (not just <code>systemctl is-active</code>) to confirm the cluster sees the node as Ready.
                </div>
            </article>

            <!-- ==================== systemctl stop ==================== -->
            <article class="api-block" id="systemctl-stop">
                <h3>systemctl stop</h3>
                <div class="api-meta">
                    <span class="method-badge method-delete">STOP</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                </div>
                <p class="api-subtitle">Stop (deactivate) one or more units — drain node first before stopping kubelet</p>
                <div class="api-description">
                    <p><code class="inline">systemctl stop</code> deactivates a running unit. On Kubernetes nodes, stopping <code>kubelet</code> makes the node NotReady — Pods stop being managed. ALWAYS drain a worker node (<code>kubectl drain</code>) before stopping kubelet. Systemd sends SIGTERM, then SIGKILL after <code>TimeoutStopSec</code>.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl stop UNIT...
systemctl stop kubelet
systemctl stop containerd kubelet</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — unit stopped</td></tr><tr><td><code>1</code></td><td>Error — unit not found or already inactive</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Proper Drain & Stop Kubelet for Maintenance</h5>
                    <p><strong>Scenario:</strong> Carol drains worker node wk-04 before stopping kubelet for a kernel upgrade.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">kubectl drain wk-04 --ignore-daemonsets --delete-emptydir-data && systemctl stop kubelet && systemctl is-active kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">node/wk-04 cordoned
node/wk-04 drained
inactive</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Pods were gracefully evicted and rescheduled elsewhere. Kubelet stopped cleanly. The node shows <code>SchedulingDisabled</code> in <code>kubectl get nodes</code>. This is the ONLY safe way to stop kubelet in production — drain first, then stop.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Stop Containerd to Replace Runtime Config</h5>
                    <p><strong>Scenario:</strong> Dave stops containerd to change its configuration (sandbox image, registry mirrors).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop containerd && echo "containerd stopped" && nano /etc/containerd/config.toml && systemctl start containerd && systemctl is-active containerd</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">containerd stopped
active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> containerd stopped, config updated, restarted. During the stop, kubelet can't start/stop Pods (it will retry). Existing containers keep running because containerd uses a daemonless shim model — stopping the daemon only prevents new container operations.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Stop with Timeout (Force Kill Fallback)</h5>
                    <p><strong>Scenario:</strong> Alice stops kubelet but it's hanging (stuck on a Pod teardown). She implements a timeout with force-kill.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop kubelet && echo "Kubelet stopped" || (echo "Timeout — forcing..."; systemctl kill -s KILL kubelet)</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Kubelet stopped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet stopped gracefully within the 90s default timeout. If it exceeded <code>TimeoutStopSec</code>, the <code>||</code> branch would forcefully kill it. Force-killing kubelet leaves Pods orphaned (they keep running but aren't managed).</p>
                </div>

                <div class="example">
                    <h5>Example 4: Stop Before Editing Kubelet Config</h5>
                    <p><strong>Scenario:</strong> Carol stops kubelet, edits the kubelet config (adds node labels), then restarts.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">kubectl drain wk-04 --ignore-daemonsets && systemctl stop kubelet && echo 'nodeLabels: {env: prod}' >> /var/lib/kubelet/config.yaml && systemctl daemon-reload && systemctl start kubelet && kubectl uncordon wk-04</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">node/wk-04 drained
node/wk-04 uncordoned</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Full maintenance workflow: drain → stop kubelet → edit config → daemon-reload → start → uncordon. After uncordon, the scheduler places Pods back on wk-04. The updated config is now active.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Conditional Stop (Only if Running)</h5>
                    <p><strong>Scenario:</strong> Dave's automation script stops kubelet only if it's currently active.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-active --quiet kubelet && systemctl stop kubelet && echo "Kubelet was running — stopped" || echo "Kubelet was already stopped"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Kubelet was running — stopped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>is-active --quiet</code> returns exit 0 if active. The <code>&&</code> runs stop only if active. This prevents errors in scripts where kubelet may already be down. Use this pattern in idempotent automation.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> NEVER stop kubelet on a worker node without draining first: <code>kubectl drain &lt;node&gt; --ignore-daemonsets --delete-emptydir-data</code>. Stopping kubelet without draining causes Pods to become unmanaged and the API server marks them as Unknown after the node's lease expires (default 40s). Stop containerd only after kubelet to prevent race conditions.
                </div>
            </article>

            <!-- ==================== systemctl restart ==================== -->
            <article class="api-block" id="systemctl-restart">
                <h3>systemctl restart</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">RESTART</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                </div>
                <p class="api-subtitle">Stop and then start one or more units — apply config changes with minimal downtime</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl restart UNIT...
systemctl restart kubelet
systemctl restart containerd kubelet</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — unit restarted</td></tr><tr><td><code>1</code></td><td>Error — unit not found or start failed</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Restart Kubelet After Config Change</h5>
                    <p><strong>Scenario:</strong> Carol restarts kubelet after updating its config to add a new eviction threshold.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /var/lib/kubelet/config.yaml && systemctl daemon-reload && systemctl restart kubelet && kubectl get node wk-04 --no-headers | awk '{print $2}'</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Ready</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet restarted with the new eviction threshold. The node briefly went NotReady (5-10s) then returned to Ready. During restart, existing Pods keep running (kubelet restarts quickly). New Pod scheduling pauses briefly. Always <code>daemon-reload</code> before restarting after config changes.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Restart Containerd Then Kubelet (Runtime Update)</h5>
                    <p><strong>Scenario:</strong> Dave restarts containerd first then kubelet after upgrading the container runtime.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl restart containerd && sleep 3 && systemctl restart kubelet && echo "Runtime updated — node recovering"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Runtime updated — node recovering</div>
                    <p class="output-note"><strong>📝 What happened:</strong> containerd restarted first (3s wait for it to stabilize), then kubelet. The correct order: runtime first, node agent second. During this ~8s window, Pods on the node still run (containerd shim processes survive the daemon restart). Kubelet reconnects to containerd on restart.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Conditional Restart (only if running)</h5>
                    <p><strong>Scenario:</strong> Alice restarts kubelet only if it's currently active — avoids starting if it was deliberately stopped.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-active --quiet kubelet && systemctl restart kubelet || echo "Kubelet not running — inspect before starting"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Kubelet not running — inspect before starting</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet wasn't running (possibly drained intentionally), so restart was skipped. This prevents accidentally re-joining a node to the cluster that was intentionally taken offline. Use <code>try-restart</code> for this natively.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Restart with Pre-Flight Config Validation</h5>
                    <p><strong>Scenario:</strong> Dave validates kubelet config before restarting to prevent a broken config.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">kubelet --config=/var/lib/kubelet/config.yaml --dry-run 2>&1 | grep -q "error" && echo "Config has errors — NOT restarting" || (systemctl daemon-reload && systemctl restart kubelet && echo "Config valid — restarted")</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Config valid — restarted</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>kubelet --dry-run</code> validated the config. No errors found, so daemon-reload + restart proceeded. This is critical in production — a broken kubelet config causes the node to go NotReady and stay there. Always validate before restarting.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Restart etcd for Certificate Rotation</h5>
                    <p><strong>Scenario:</strong> Carol restarts etcd on cp-01 after rotating its serving certificate.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">cp /etc/kubernetes/pki/etcd/server-new.crt /etc/kubernetes/pki/etcd/server.crt && systemctl restart etcd && etcdctl endpoint health --endpoints=https://127.0.0.1:2379</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">https://127.0.0.1:2379 is healthy: successfully committed proposal: took 8.2ms</div>
                    <p class="output-note"><strong>📝 What happened:</strong> New certificate deployed, etcd restarted, endpoint health confirmed. etcd is the most critical component — it stores ALL cluster state. Always verify etcd health after a restart with <code>etcdctl endpoint health</code>. On a 3-node etcd cluster, restart one at a time.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> Always validate configs before restarting production services. Restart control plane components one at a time in multi-node clusters. After restarting kubelet, verify with <code>kubectl get node</code> (not just <code>systemctl is-active</code>). For etcd, verify quorum health with <code>etcdctl endpoint health</code>.
                </div>
            </article>

            <!-- ==================== systemctl reload ==================== -->
            <article class="api-block" id="systemctl-reload">
                <h3>systemctl reload</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">RELOAD</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                </div>
                <p class="api-subtitle">Reload configuration without restarting — for services that support hot-reload</p>
                <div class="api-description">
                    <p><code class="inline">systemctl reload</code> asks a service to reload its configuration without a full restart. The service must define <code>ExecReload=</code> in its unit file. Not all Kubernetes services support reload — kubelet, containerd, and etcd typically require a full restart for config changes.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl reload UNIT...
systemctl reload kube-proxy           # If ExecReload= is configured
systemctl reload kubelet              # Not supported by default — use restart</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — config reloaded</td></tr><tr><td><code>1</code></td><td>Error — service doesn't support reload or reload command failed</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Reload kube-proxy Config (Zero Downtime)</h5>
                    <p><strong>Scenario:</strong> Carol updates kube-proxy's iptables mode and reloads without disrupting traffic.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /var/lib/kube-proxy/config.conf && systemctl reload kube-proxy && echo "kube-proxy reloaded — iptables rules updated"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">kube-proxy reloaded — iptables rules updated</div>
                    <p class="output-note"><strong>📝 What happened:</strong> kube-proxy re-read its config and updated iptables rules without dropping existing connections. Reload is much faster than restart — and doesn't disrupt active connections to ClusterIP services.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Reload Not Supported — Fallback to Restart</h5>
                    <p><strong>Scenario:</strong> Alice tries reloading kubelet (which doesn't support it) and learns the fallback.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload kubelet 2>&1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Job type reload is not applicable for unit kubelet.service.
# Use 'systemctl restart kubelet' instead</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet has no <code>ExecReload=</code> directive — reload is not supported. Most Kubernetes components (kubelet, containerd, etcd, apiserver) require restart for config changes. Only a few (like kube-proxy with custom unit files) support reload.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Reload vs Restart Timing Comparison</h5>
                    <p><strong>Scenario:</strong> Carol compares reload vs restart timing on kube-proxy to understand the difference.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "=== RELOAD ===" && time systemctl reload kube-proxy && echo "=== RESTART ===" && time systemctl restart kube-proxy</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">=== RELOAD ===
real    0m0.038s
=== RESTART ===
real    0m0.612s</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Reload: 38ms. Restart: 612ms (16× slower). For kube-proxy (which handles all Service traffic), reload is preferred — no disruption to iptables/IPVS rules. Restart causes a brief window where new connections to Services may fail.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Verify PID Stability After Reload</h5>
                    <p><strong>Scenario:</strong> Dave confirms reload didn't restart the process by checking PID stability.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">BEFORE=$(systemctl show kube-proxy -p MainPID) && systemctl reload kube-proxy && AFTER=$(systemctl show kube-proxy -p MainPID) && echo "$BEFORE → $AFTER (same PID = reload confirmed)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">MainPID=1234 → MainPID=1234 (same PID = reload confirmed)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Same PID before and after — confirming it was a reload, not a restart. Reload preserves process state, connections, and caches. Restart creates a new PID. Use this check in validation scripts to ensure zero-downtime deployments.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Batch Reload on Control Plane</h5>
                    <p><strong>Scenario:</strong> Alice reloads all control plane services that support it after rotating certificates.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">for svc in kube-proxy; do systemctl reload $svc && echo "$svc reloaded OK"; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">kube-proxy reloaded OK</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Only kube-proxy supports reload among K8s services. Other components (kubelet, containerd, etcd, apiserver, controller-manager, scheduler) need restart for certificate changes — plan for brief downtime when rotating certs.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> Most K8s components do NOT support <code>reload</code>. Use <code>restart</code> instead. kube-proxy is the notable exception if <code>ExecReload=</code> is configured. For production cert rotation, restart one control plane component at a time. Verify with <code>kubectl get cs</code> (componentstatus) after each restart.
                </div>
            </article>

            <!-- ==================== systemctl reload-or-restart ==================== -->
            <article class="api-block" id="systemctl-reload-or-restart">
                <h3>systemctl reload-or-restart</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">SMART</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Reload if supported, otherwise restart — safest config-apply for any service</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl reload-or-restart UNIT...
systemctl reload-or-restart kubelet
systemctl reload-or-restart kube-proxy containerd kubelet</code></pre>

                <div class="example">
                    <h5>Example 1: Smart Reload/Restart for kube-proxy</h5>
                    <p><strong>Scenario:</strong> Carol uses reload-or-restart in automation — it reloads if supported, restarts if not.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload-or-restart kube-proxy && echo "Config applied to kube-proxy"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Config applied to kube-proxy</div>
                    <p class="output-note"><strong>📝 What happened:</strong> kube-proxy supports reload, so it reloaded (zero downtime). If it didn't support reload, it would have restarted. This is the safest generic command for scripts that don't know which services support reload.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Apply Config Across All K8s Services</h5>
                    <p><strong>Scenario:</strong> Dave's node bootstrap script applies config changes to all K8s services without knowing their reload capabilities.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">for svc in kubelet containerd kube-proxy; do echo "Applying $svc..."; systemctl reload-or-restart $svc; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Applying kubelet... (restarted — no reload support)
Applying containerd... (restarted — no reload support)
Applying kube-proxy... (reloaded)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> kubelet and containerd restarted (no reload support). kube-proxy reloaded (zero downtime). The script handles both cases without if/else logic. This is the recommended pattern for generic node configuration scripts.</p>
                </div>
            </article>

            <!-- ==================== systemctl status ==================== -->
            <article class="api-block" id="systemctl-status">
                <h3>systemctl status</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">INSPECT</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                    <span class="tag">containerd</span>
                </div>
                <p class="api-subtitle">Show runtime status — THE first command when a node shows NotReady</p>
                <div class="api-description">
                    <p><code class="inline">systemctl status</code> displays everything about a unit: loaded/enabled state, active state, PID, memory, CPU, start time, and the last 10 journal log lines. When a Kubernetes node reports <code>NotReady</code>, this is the FIRST command to run on that node.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl status UNIT...
systemctl status kubelet
systemctl status kubelet containerd   # Check both critical services</code></pre>

                <div class="example">
                    <h5>Example 1: Full Status of Healthy Kubelet</h5>
                    <p><strong>Scenario:</strong> Carol checks kubelet status on wk-04 after noticing the node is Slow to report metrics.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● kubelet.service — kubelet: The Kubernetes Node Agent
     Loaded: loaded (/etc/systemd/system/kubelet.service; enabled)
     Active: active (running) since Fri 2026-06-06 08:00:00 UTC
   Main PID: 1234 (kubelet)
      Tasks: 12 (limit: 4915)
     Memory: 128.5M
        CPU: 45.345s
     CGroup: /system.slice/kubelet.service</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet is active (running) and enabled at boot. 128MB memory usage is normal for a node running ~20 Pods. The dot (●) is green for active — if it were red, the node would be NotReady. Always check kubelet status first when troubleshooting node issues.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Status of Failed Kubelet (Node Unhealthy)</h5>
                    <p><strong>Scenario:</strong> Alice investigates why node wk-05 is NotReady — kubelet has failed.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● kubelet.service — kubelet: The Kubernetes Node Agent
     Loaded: loaded (/etc/systemd/system/kubelet.service; enabled)
     Active: failed (Result: exit-code) since Fri 2026-06-06 08:15:00 UTC
    Process: 5678 ExecStart=/usr/bin/kubelet --config=/var/lib/kubelet/config.yaml (code=exited, status=1/FAILURE)
   Main PID: 5678 (code=exited, status=1/FAILURE)

Jun 06 08:15:00 wk-05 kubelet[5678]: E0606 08:15:00.123456 kubelet.go:2467] "Failed to register node" err="node wk-05 already exists"
Jun 06 08:15:00 wk-05 kubelet[5678]: F0606 08:15:00.234567 kubelet.go:1370] failed to start ContainerManager: invalid kernel flag "cgroup.memory=nokmem"</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet failed — the last 10 journal lines show the root cause: invalid kernel flag <code>cgroup.memory=nokmem</code>. This is a common issue after kernel updates. Status output gives the error AND the logs in one view — no need to run journalctl separately for initial diagnosis.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Check All Critical Services on Control Plane</h5>
                    <p><strong>Scenario:</strong> Dave checks the health of all control plane services on cp-01.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status kube-apiserver etcd kube-scheduler kube-controller-manager kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● kube-apiserver.service — active (running)
● etcd.service — active (running)
● kube-scheduler.service — active (running)
● kube-controller-manager.service — active (running)
● kubelet.service — active (running)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All five control plane services are active. This is the standard daily health check on every control plane node. Any failed service (red dot) would indicate a degraded control plane that needs immediate attention.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Status of containerd with Recent Pod Events</h5>
                    <p><strong>Scenario:</strong> Alice checks containerd status to see if there are any recent container errors.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status containerd</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● containerd.service — containerd container runtime
     Active: active (running) since Fri 2026-06-06 07:55:00 UTC
   Main PID: 890 (containerd)
     Memory: 512.3M
        CPU: 1h 23min 45.123s

Jun 06 08:14:00 wk-04 containerd[890]: time="2026-06-06T08:14:00Z" level=warning msg="failed to delete container" error="container still has running tasks"
Jun 06 08:14:05 wk-04 containerd[890]: time="2026-06-06T08:14:05Z" level=info msg="Container deleted successfully" id=abc123</div>
                    <p class="output-note"><strong>📝 What happened:</strong> containerd is running with 512MB memory (normal for a busy node). Recent logs show a container deletion that briefly failed (running tasks) but succeeded 5s later. This is typical when kubelet tries to delete a container that's still shutting down.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Status with Custom Property Extraction</h5>
                    <p><strong>Scenario:</strong> Carol extracts specific properties from kubelet status for a monitoring script.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl show kubelet -p ActiveState -p SubState -p MemoryCurrent -p MainPID -p ExecMainStartTimestamp</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">ActiveState=active
SubState=running
MemoryCurrent=134742016
MainPID=1234
ExecMainStartTimestamp=Fri 2026-06-06 08:00:00 UTC</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Machine-readable property extraction — ideal for monitoring scripts and Prometheus exporters. <code>systemctl show</code> returns 200+ properties; use <code>-p</code> to extract specific ones. <code>MemoryCurrent</code> is in bytes (134MB). Use this for automated health checks.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> <code>systemctl status kubelet</code> is THE first command when a node shows NotReady. The last 10 journal lines usually reveal the root cause immediately. For monitoring scripts, use <code>systemctl show &lt;UNIT&gt; -p ActiveState</code> for machine-readable output. Control plane health: check etcd first — if etcd is down, nothing else matters.
                </div>
            </article>

            <!-- systemctl enable/disable -->
            <article class="api-block" id="systemctl-enable">
                <h3>systemctl enable / disable</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">BOOT</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">kubelet</span>
                    <span class="tag">containerd</span>
                </div>
                <p class="api-subtitle">Enable K8s services to auto-start at boot — critical for node recovery after reboots</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl enable UNIT...
systemctl disable UNIT...
systemctl enable --now UNIT...     # Enable AND start immediately
systemctl disable --now UNIT...    # Disable AND stop immediately

# Critical on every Kubernetes node:
systemctl enable kubelet containerd
systemctl enable --now kube-proxy</code></pre>

                <div class="example">
                    <h5>Example 1: Enable Kubelet to Survive Node Reboots</h5>
                    <p><strong>Scenario:</strong> Carol ensures kubelet auto-starts whenever a worker node reboots unexpectedly.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable kubelet && systemctl is-enabled kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Created symlink /etc/systemd/system/multi-user.target.wants/kubelet.service → /etc/systemd/system/kubelet.service.
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Symlink created — when the node boots and reaches multi-user.target, kubelet will auto-start. Without this, an unexpected reboot leaves the node NotReady until manual intervention. ALL Kubernetes nodes MUST have kubelet and containerd enabled.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Enable and Start Containerd + Kubelet in One Go</h5>
                    <p><strong>Scenario:</strong> Dave bootstraps a new worker node — enabling and starting both services atomically.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable --now containerd && systemctl enable --now kubelet && kubectl get node $(hostname) --no-headers</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">wk-06   Ready   worker   30s   v1.31.0</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>--now</code> combines enable + start into one operation. Both services are running AND configured for auto-start. Within 30 seconds, the node appears in <code>kubectl get nodes</code> as Ready. This is the standard node bootstrap pattern.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Enable All Control Plane Services</h5>
                    <p><strong>Scenario:</strong> Alice enables all services on a newly built control plane node.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">for svc in etcd kube-apiserver kube-controller-manager kube-scheduler kubelet kube-proxy; do systemctl enable $svc && echo "$svc: enabled"; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">etcd: enabled
kube-apiserver: enabled
kube-controller-manager: enabled
kube-scheduler: enabled
kubelet: enabled
kube-proxy: enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All six control plane services enabled — the node will fully recover after any reboot. The order in the loop doesn't matter for enabling (it creates symlinks). At boot, systemd respects <code>After=</code> and <code>Requires=</code> directives for ordering.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Disable Kubelet Before Draining & Decommissioning</h5>
                    <p><strong>Scenario:</strong> Carol disables kubelet on a node being decommissioned from the cluster.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">kubectl drain wk-07 --ignore-daemonsets --delete-emptydir-data && systemctl stop kubelet && systemctl disable kubelet && echo "wk-07 decommissioned — will not rejoin at reboot"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">node/wk-07 drained
Removed /etc/systemd/system/multi-user.target.wants/kubelet.service.
wk-07 decommissioned — will not rejoin at reboot</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Full decommission: drain → stop → disable. The symlink is removed — if the node reboots, kubelet won't start and won't rejoin the cluster. This is the proper way to remove a node permanently.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Verify All Critical Services Are Enabled</h5>
                    <p><strong>Scenario:</strong> Dave audits a node to ensure kubelet and containerd are enabled (survive reboots).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-enabled kubelet containerd kube-proxy 2>&1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">enabled
enabled
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All three services are enabled — the node will auto-recover from reboots. If any showed "disabled" or "static", the node would not fully recover. This check should be part of every node bootstrap script and regular audit.</p>
                </div>

                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> Every K8s node MUST have <code>kubelet</code> and <code>containerd</code> enabled. Without this, a reboot takes the node offline until manual intervention. Use <code>enable --now</code> for node bootstrap — one command instead of two. After disabling kubelet, also disable kube-proxy and containerd to fully clean up.
                </div>
            </article>

            <!-- systemctl list-units -->
            <article class="api-block" id="systemctl-list">
                <h3>systemctl list-units</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">AUDIT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">List loaded units with state — see all K8s services on a node at a glance</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl list-units [PATTERN...]
systemctl list-units --type=service --state=running 'kube*' 'containerd*' 'etcd*'
systemctl list-units --all
systemctl list-units 'kube*'          # Pattern match</code></pre>

                <div class="example">
                    <h5>Example 1: Show Only Running K8s Services</h5>
                    <p><strong>Scenario:</strong> Alice wants to see exactly which Kubernetes services are running on a control plane node.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --type=service --state=running 'kube*' 'etcd*' 'containerd*'</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                         LOAD   ACTIVE SUB     DESCRIPTION
containerd.service           loaded active running containerd container runtime
etcd.service                 loaded active running etcd
kube-apiserver.service       loaded active running Kubernetes API Server
kube-controller-manager.service loaded active running Kubernetes Controller Manager
kube-proxy.service           loaded active running Kubernetes Network Proxy
kube-scheduler.service       loaded active running Kubernetes Scheduler
kubelet.service              loaded active running kubelet: Kubernetes Node Agent</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Seven K8s services running — this is a healthy control plane. Filtering by patterns and state=running gives a clean view. On a worker node, you'd only see containerd, kube-proxy, kubelet (3 services).</p>
                </div>

                <div class="example">
                    <h5>Example 2: Find Failed K8s Services After Update</h5>
                    <p><strong>Scenario:</strong> Dave checks for failed services across the entire system after a cluster upgrade.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --state=failed</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">0 loaded units listed.</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Zero failed units — the upgrade was clean. Any failed K8s service (especially kubelet, containerd, or etcd) needs immediate investigation. This is the first post-upgrade check on every node.</p>
                </div>

                <div class="example">
                    <h5>Example 3: List All Services with Pattern Match</h5>
                    <p><strong>Scenario:</strong> Carol lists all units matching 'kube' to see what's loaded.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units 'kube*'</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                         LOAD   ACTIVE SUB     DESCRIPTION
kube-apiserver.service       loaded active running Kubernetes API Server
kube-controller-manager.service loaded active running Kubernetes Controller Manager
kube-proxy.service           loaded active running Kubernetes Network Proxy
kube-scheduler.service       loaded active running Kubernetes Scheduler
kubelet.service              loaded active running kubelet: Kubernetes Node Agent</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Five kube* services. Pattern matching is a quick way to see all related services. Note that etcd and containerd don't match 'kube*' — use multiple patterns for a complete picture: <code>'kube*' 'etcd*' 'container*'</code>.</p>
                </div>
            </article>

            <!-- systemctl daemon-reload -->
            <article class="api-block" id="systemctl-daemon-reload">
                <h3>systemctl daemon-reload</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">REFRESH</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Reload systemd configuration — required after ANY unit file change on a K8s node</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl daemon-reload

# Typical workflow on a K8s node:
cp kubelet.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now kubelet</code></pre>

                <div class="example">
                    <h5>Example 1: Deploy New Kubelet Unit File</h5>
                    <p><strong>Scenario:</strong> Carol deploys a customized kubelet unit file with resource limits and security hardening.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">cp kubelet-custom.service /etc/systemd/system/kubelet.service && systemctl daemon-reload && systemctl enable kubelet && systemctl restart kubelet && echo "Kubelet unit deployed"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Kubelet unit deployed</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Copy unit file → daemon-reload (makes systemd aware) → enable → restart (applies changes). Skipping daemon-reload is the #1 cause of "unit file not found" errors after deploying new unit files.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Modify Memory Limit and Reload</h5>
                    <p><strong>Scenario:</strong> Alice increases kubelet's memory limit from 1G to 2G via a drop-in override.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">mkdir -p /etc/systemd/system/kubelet.service.d && echo -e "[Service]\\nMemoryMax=2G" > /etc/systemd/system/kubelet.service.d/override.conf && systemctl daemon-reload && systemctl restart kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">(no output = success)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Drop-in override created, daemon-reload picks it up, restart applies the new limit. Without daemon-reload, systemd would use the old (cached) unit definition. Drop-in overrides are preferred over editing the original unit file — they survive package updates.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Remove a Service Properly</h5>
                    <p><strong>Scenario:</strong> Dave removes an old custom controller that ran as a systemd service on the control plane.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop old-controller && systemctl disable old-controller && rm /etc/systemd/system/old-controller.service && systemctl daemon-reload && echo "Old controller removed"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Old controller removed</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Full removal: stop → disable → delete file → daemon-reload. If you skip daemon-reload after deleting, systemd still remembers the unit (from its cache) and shows confusing "not-found" errors.</p>
                </div>
            </article>

            <!-- systemctl show/cat/edit -->
            <article class="api-block" id="systemctl-show">
                <h3>systemctl show / cat / edit</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">INSPECT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Inspect and modify unit configuration — view kubelet/containerd properties</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl show UNIT              # All properties (200+ key=value pairs)
systemctl show UNIT -p ExecStart  # Specific property
systemctl cat UNIT                # Show unit file + all drop-in overrides
systemctl edit UNIT               # Create/edit drop-in override (uses $EDITOR)</code></pre>

                <div class="example">
                    <h5>Example 1: Show Kubelet's ExecStart Command</h5>
                    <p><strong>Scenario:</strong> Carol checks exactly what command and flags are used to start kubelet.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl show kubelet -p ExecStart</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">ExecStart={ path=/usr/bin/kubelet ; argv[]=/usr/bin/kubelet --config=/var/lib/kubelet/config.yaml --container-runtime-endpoint=unix:///run/containerd/containerd.sock --kubeconfig=/etc/kubernetes/kubelet.conf ; ignore_errors=no ... }</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The exact path, config file, container runtime endpoint, and kubeconfig are displayed. <code>-p</code> extracts one property. Use this to verify which config file kubelet is using — a common issue when multiple configs exist.</p>
                </div>

                <div class="example">
                    <h5>Example 2: View Kubelet Unit File and Drop-in Overrides</h5>
                    <p><strong>Scenario:</strong> Dave checks if any drop-in overrides are applied to kubelet on a problematic node.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl cat kubelet</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"># /etc/systemd/system/kubelet.service
[Unit]
Description=kubelet: The Kubernetes Node Agent
After=containerd.service
Requires=containerd.service
[Service]
ExecStart=/usr/bin/kubelet --config=/var/lib/kubelet/config.yaml
Restart=on-failure
RestartSec=5

# /etc/systemd/system/kubelet.service.d/override.conf
[Service]
MemoryMax=2G
CPUQuota=200%
LimitNOFILE=65536</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Base unit + drop-in override shown together. The override adds resource limits without modifying the original file. <code>After=containerd.service</code> ensures containerd starts first. <code>RestartSec=5</code> waits 5s before restarting on failure.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Show All Properties for Monitoring</h5>
                    <p><strong>Scenario:</strong> Alice extracts resource usage properties from containerd for a monitoring dashboard.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl show containerd -p MemoryCurrent -p CPUUsageNSec -p TasksCurrent -p NRestarts -p ActiveState</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">MemoryCurrent=536870912
CPUUsageNSec=45123000000000
TasksCurrent=45
NRestarts=0
ActiveState=active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> 512MB memory, ~45s CPU time, 45 tasks, 0 restarts, active. <code>systemctl show</code> is preferred over parsing <code>status</code> output for automation — it's machine-readable. <code>NRestarts=0</code> means containerd has never crashed on this node (good sign).</p>
                </div>
            </article>

            <!-- systemctl mask/unmask -->
            <article class="api-block" id="systemctl-mask">
                <h3>systemctl mask / unmask</h3>
                <div class="api-meta">
                    <span class="method-badge method-delete">BLOCK</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Prevent a unit from being started (even manually) — stronger than disable</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl mask UNIT       # Symlink to /dev/null — prevents ANY start
systemctl unmask UNIT      # Remove the mask</code></pre>

                <div class="example">
                    <h5>Example 1: Mask Docker When Using Containerd</h5>
                    <p><strong>Scenario:</strong> Carol masks docker.service because the cluster uses containerd as the container runtime.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl mask docker.service && systemctl mask docker.socket && systemctl start docker.service 2>&1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Failed to start docker.service: Unit docker.service is masked.</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Docker is completely blocked — even manual start is blocked. The unit file is symlinked to <code>/dev/null</code>. On Kubernetes 1.24+, dockershim is removed — mask docker to prevent conflicts with containerd and ensure no one accidentally starts it.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Mask Unused Network Managers on K8s Nodes</h5>
                    <p><strong>Scenario:</strong> Dave masks NetworkManager on a K8s node that uses systemd-networkd, preventing it from interfering with CNI.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl mask NetworkManager && systemctl stop NetworkManager 2>/dev/null; echo "NetworkManager masked — CNI will manage networking"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">NetworkManager masked — CNI will manage networking</div>
                    <p class="output-note"><strong>📝 What happened:</strong> NetworkManager masked — even if someone tries to start it, it's blocked. This prevents NetworkManager from modifying iptables rules that conflict with Calico/Cilium/Flannel CNI plugins. Common practice on production K8s nodes.</p>
                </div>
            </article>

            <!-- systemctl kill -->
            <article class="api-block" id="systemctl-kill">
                <h3>systemctl kill</h3>
                <div class="api-meta">
                    <span class="method-badge method-delete">SIGNAL</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Send a signal to one or more processes of a unit — for stuck kubelet/containerd</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl kill UNIT...
systemctl kill -s HUP kubelet          # Reload signal (if supported)
systemctl kill -s TERM containerd      # Graceful termination
systemctl kill -s KILL kubelet         # Force kill (last resort for stuck kubelet)</code></pre>

                <div class="example">
                    <h5>Example 1: Force Kill Stuck Kubelet</h5>
                    <p><strong>Scenario:</strong> Carol force-kills a kubelet that is hanging on shutdown (not responding to SIGTERM).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop kubelet & STOP_PID=$!; sleep 90 && kill -0 $STOP_PID 2>/dev/null && systemctl kill -s KILL kubelet && echo "Kubelet force-killed after 90s timeout" || wait $STOP_PID</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Kubelet force-killed after 90s timeout</div>
                    <p class="output-note"><strong>📝 What happened:</strong> After 90s, kubelet hadn't stopped (the <code>systemctl stop</code> was still running), so SIGKILL was sent. This is a last resort — force-killing kubelet leaves Pods orphaned and the node in an inconsistent state. Always try graceful stop first.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Send SIGUSR1 to Kubelet for Debug Log Dump</h5>
                    <p><strong>Scenario:</strong> Dave sends SIGUSR1 to kubelet to trigger a goroutine dump for debugging.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl kill -s USR1 kubelet && journalctl -u kubelet --since "1 min ago" | grep "goroutine" -A 5</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">goroutine 1 [running]:
goroutine 17 [syscall, 10 minutes]:
goroutine 23 [select, 2 minutes]:
goroutine 45 [IO wait, 30 seconds]:</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kubelet dumped all goroutine traces to the journal. SIGUSR1 is the signal kubelet listens to for debug dumps. This is useful when kubelet is responsive but behaving strangely — the goroutine dump shows what every goroutine is doing.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Common K8s Kill Signals Reference</h5>
                    <p><strong>Scenario:</strong> Alice learns the common signals used with Kubernetes services.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "Common K8s signals:
SIGHUP (1)  — Reload config (kube-proxy only)
SIGTERM (15) — Graceful stop (default for systemctl stop)
SIGKILL (9)  — Force kill (last resort)
SIGUSR1 (10) — Debug dump (kubelet, containerd)
SIGUSR2 (12) — Custom (varies by service)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Common K8s signals:
SIGHUP (1)  — Reload config (kube-proxy only)
SIGTERM (15) — Graceful stop (default for systemctl stop)
SIGKILL (9)  — Force kill (last resort)
SIGUSR1 (10) — Debug dump (kubelet, containerd)
SIGUSR2 (12) — Custom (varies by service)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Signal reference — most K8s components use standard signal conventions. <code>systemctl stop</code> sends SIGTERM first; if the process doesn't exit within <code>TimeoutStopSec</code>, systemd sends SIGKILL. Use <code>systemctl kill -s</code> to send any signal.</p>
                </div>
            </article>
        </section>'''

# Build final document
result = before + content + after

print(f'Articles: {result.count("<article class=")}/{result.count("</article>")}')
print(f'Examples: {result.count("class=\"example\"")}')
print(f'Total Lines: {len(result.split(chr(10)))}')

# Verify no nginx/nginx/webapp/webapp references remain in systemctl section
section_start = result.find('<section class="section" id="systemctl-section">')
section_end = result.find('<section class="section" id="systemctl-advanced">')
section_content = result[section_start:section_end]

old_refs = ['nginx.service', 'webapp.service', 'worker.service', 'Gunicorn', 'Celery', 'celery', 
            'reverse proxy', 'Nginx Proxy', 'load balancer', 'apache2', 'webapp']

for ref in old_refs:
    count = section_content.count(ref)
    if count > 0:
        print(f'WARNING: {ref} still appears {count} times')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(result)

print('Done — systemctl section rewritten with Kubernetes services')
