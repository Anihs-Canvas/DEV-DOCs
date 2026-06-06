"""Build Part 9 — Day 2 Maintenance Cheat Sheet"""

content = r'''    <!-- ══════════════════════════════════════════════════════ -->
    <!-- PART 9: MAINTENANCE CHEAT SHEET -->
    <!-- ══════════════════════════════════════════════════════ -->
    <section class="section" id="part-9">
        <h2>⚡ <span class="section-num">Part 9</span> — Day 2 Maintenance Cheat Sheet</h2>
        <div class="section-intro">
            <p>This is your <strong>quick-reference card</strong> for daily cluster operations. Every command you need — cluster health checks, etcd operations, certificate management, node maintenance, upgrades, diagnostics, token management, and full cluster reset — is here in one place. Each section links back to the detailed deep-dive in earlier parts.</p>
            <p><strong>Print this section.</strong> Keep it handy. When something breaks at 2 AM, you don't want to search through documentation — you want the command <em>right now</em>.</p>
        </div>

        <!-- 9.1 CLUSTER HEALTH -->
        <h3 id="part-9-1">9.1 Cluster Health — Is Everything Running?</h3>
        <div class="api-block">
            <p>The first commands you run when checking cluster health. Start here every time:</p>
            <table>
                <tr><th style="width:280px;">Command</th><th>What It Shows</th><th>When to Use</th></tr>
                <tr><td><code class="inline">kubectl get nodes -o wide</code></td><td>All nodes with status, roles, version, internal IP, OS, kernel. The <code class="inline">-o wide</code> flag adds IP and OS columns.</td><td>First check every time. Any node showing <code class="inline">NotReady</code> needs investigation.</td></tr>
                <tr><td><code class="inline">kubectl get pods -A --field-selector=status.phase!=Running</code></td><td>All non-Running Pods across ALL namespaces. Filters out healthy Pods so you see only problems.</td><td>When something seems wrong. A Pod stuck in Pending/CrashLoopBackOff will show here.</td></tr>
                <tr><td><code class="inline">kubectl get cs</code></td><td>Component status — scheduler and controller-manager health. (Deprecated in newer versions but still useful on v1.31).</td><td>If the API server works but scheduling or replication isn't happening.</td></tr>
                <tr><td><code class="inline">kubectl cluster-info dump</code></td><td>Complete cluster diagnostics dump — API server endpoints, health checks, component versions, all Pods/Services/Deployments.</td><td>Full health audit. Pipe to a file for analysis: <code class="inline">kubectl cluster-info dump > cluster-dump-$(date +%Y%m%d).log</code></td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 Quick Health Check Routine:</strong>
                <ol style="margin-top:6px;">
                    <li><code class="inline">kubectl get nodes</code> — all Ready?</li>
                    <li><code class="inline">kubectl get pods -A | grep -v Running | grep -v Completed</code> — any stuck Pods?</li>
                    <li><code class="inline">kubectl top nodes</code> — any node at >80% CPU/memory? (requires metrics-server)</li>
                    <li><code class="inline">kubectl get events -A --sort-by='.lastTimestamp' | tail -20</code> — recent warnings?</li>
                </ol>
            </div>
        </div>

        <!-- 9.2 ETCD OPERATIONS -->
        <h3 id="part-9-2">9.2 etcd Operations — Database Health & Status</h3>
        <div class="api-block">
            <p>Quick etcd health checks via kubectl exec (runs etcdctl inside the etcd container). For the full etcd reference, see <a href="#part-6">Part 6</a>:</p>
            <table>
                <tr><th style="width:340px;">Command</th><th>What It Shows</th></tr>
                <tr><td><code class="inline">kubectl -n kube-system exec -it etcd-cp-01 -- etcdctl endpoint health --cluster</code></td><td>Health of ALL etcd members. Each member reports <code class="inline">is healthy</code> or errors. If any member is unhealthy, investigate immediately.</td></tr>
                <tr><td><code class="inline">kubectl -n kube-system exec -it etcd-cp-01 -- etcdctl endpoint status --write-out=table</code></td><td>Per-member status: DB size, leader ID, raft index, raft term, revision. Watch the DB SIZE column — if near 8GB, you need defrag.</td></tr>
            </table>

            <div class="warning">
                <strong>⚠️ etcd health = cluster health:</strong> If <code class="inline">endpoint health</code> shows any unhealthy member, check immediately. A single unhealthy etcd member can be tolerated, but if a second goes down, the cluster becomes read-only. See <a href="#part-6-10">Part 6.10</a> for troubleshooting and <a href="#part-6-13">Part 6.13</a> for disaster scenarios.
            </div>
        </div>

        <!-- 9.3 CERTIFICATE MANAGEMENT -->
        <h3 id="part-9-3">9.3 Certificate Management — Don't Let Them Expire</h3>
        <div class="api-block">
            <p>Certificate expiry is a <strong>silent cluster killer</strong>. Check expiry dates regularly. Full cert management in <a href="#part-7-3">Part 7.3</a>:</p>
            <table>
                <tr><th style="width:250px;">Command</th><th>What It Does</th></tr>
                <tr><td><code class="inline">kubeadm certs check-expiration</code></td><td>Shows ALL certificate expiry dates. Leaf certs expire in 1 year. CA certs expire in 10 years. Set a calendar reminder for 30 days before leaf cert expiry.</td></tr>
                <tr><td><code class="inline">kubeadm certs renew all</code></td><td>Renews ALL expiring certificates. Run this ON cp-01, then restart static Pods on all CP nodes (see Part 7.3 for the restart procedure).</td></tr>
            </table>

            <div class="highlight-box">
                <strong>🧠 Certificate Health Check Routine (Monthly):</strong>
                <ol style="margin-top:6px;">
                    <li><code class="inline">kubeadm certs check-expiration</code> — any certs within 30 days of expiry?</li>
                    <li>If yes: <code class="inline">kubeadm certs renew all</code></li>
                    <li>Restart static Pods on ALL CP nodes (see Part 7.3)</li>
                    <li>Verify: <code class="inline">openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates</code></li>
                </ol>
            </div>
        </div>

        <!-- 9.4 NODE MAINTENANCE -->
        <h3 id="part-9-4">9.4 Node Maintenance — Drain, Cordon, Uncordon</h3>
        <div class="api-block">
            <p>The three essential node lifecycle commands. Full node management in <a href="#part-7-2">Part 7.2</a>:</p>
            <table>
                <tr><th style="width:300px;">Command</th><th>What It Does</th><th>When to Use</th></tr>
                <tr><td><code class="inline">kubectl drain wk-04 --ignore-daemonsets --delete-emptydir-data</code></td><td>Evacuates ALL Pods from the node. DaemonSet Pods are skipped (<code class="inline">--ignore-daemonsets</code>). Pods using emptyDir volumes are evicted even though data is lost (<code class="inline">--delete-emptydir-data</code>). The node is marked as SchedulingDisabled.</td><td>Before maintenance, upgrades, or decommissioning. Always drain before touching a worker node.</td></tr>
                <tr><td><code class="inline">kubectl cordon wk-04</code></td><td>Marks the node as <strong>unschedulable</strong>. Existing Pods stay, but no NEW Pods are scheduled here. Less disruptive than drain.</td><td>When you suspect a node is unstable but don't want to evict all Pods yet. Also used to reserve a node for debugging.</td></tr>
                <tr><td><code class="inline">kubectl uncordon wk-04</code></td><td>Removes the unschedulable taint. The node is available for scheduling again. Pods don't automatically move back — only new Pods can be placed here.</td><td>After maintenance or upgrade is complete. Follow with <code class="inline">kubectl wait --for=condition=Ready node/wk-04</code>.</td></tr>
            </table>

            <div class="diagram-box">
                <div class="diagram-title">🔄 Node Lifecycle State Machine</div>
                <div class="ascii-block">                    kubectl drain
  [Schedulable] ──────────────────► [SchedulingDisabled + Pods Evicted]
       ▲                                      │
       │ kubectl uncordon                     │ Maintenance / Upgrade
       │                                      ▼
       └──────────────────────────── [SchedulingDisabled + Pods Evicted]
                                               │
                                               │ kubectl uncordon
                                               ▼
                                      [Schedulable — Ready for Pods]</div>
            </div>
        </div>

        <!-- 9.5 CLUSTER UPGRADE -->
        <h3 id="part-9-5">9.5 Cluster Upgrade — Quick Commands</h3>
        <div class="api-block">
            <p>The essential upgrade commands. Full upgrade process with all 6 steps in <a href="#part-7-1">Part 7.1</a>:</p>
            <table>
                <tr><th style="width:240px;">Command</th><th>What It Does</th><th>Run On</th></tr>
                <tr><td><code class="inline">kubeadm upgrade plan</code></td><td>Shows available versions and what components will be upgraded. Always run this FIRST to verify the upgrade path.</td><td>cp-01</td></tr>
                <tr><td><code class="inline">kubeadm upgrade apply v1.32.0</code></td><td>Upgrades the control plane: static Pods (etcd, apiserver, scheduler, controller-manager), kubeadm-config, kubelet-config, CoreDNS, kube-proxy. Does NOT upgrade kubelet.</td><td>cp-01 only</td></tr>
                <tr><td><code class="inline">kubeadm upgrade node</code></td><td>Upgrades static Pods on THIS node only. Use on remaining CP nodes and all worker nodes (after draining).</td><td>cp-02, cp-03, wk-01..05</td></tr>
            </table>

            <div class="warning">
                <strong>⚠️ NEVER skip minor versions.</strong> Kubernetes supports upgrading one minor version at a time (1.31 → 1.32). Skipping versions (1.30 → 1.32) is <strong>NOT supported</strong> and will corrupt the cluster. Always backup etcd before starting any upgrade.
            </div>
        </div>

        <!-- 9.6 DIAGNOSTICS -->
        <h3 id="part-9-6">9.6 Diagnostics & Debugging — When Things Go Wrong</h3>
        <div class="api-block">
            <p>The most-used diagnostic commands. For the full troubleshooting decision tree, see <a href="#part-7-7">Part 7.7</a>:</p>
            <table>
                <tr><th style="width:280px;">Command</th><th>What It Shows</th><th>When to Use</th></tr>
                <tr><td><code class="inline">journalctl -u kubelet -n 100 --no-pager</code></td><td>Last 100 lines of kubelet logs. Shows Pod creation errors, image pull failures, CNI errors, disk pressure, and memory pressure events.</td><td>When a node shows NotReady, or Pods on a specific node are failing. The kubelet log is the single most useful diagnostic source.</td></tr>
                <tr><td><code class="inline">journalctl -u containerd -n 100 --no-pager</code></td><td>Last 100 lines of container runtime logs. Shows image pull progress, container start/stop events, and runtime errors.</td><td>When containers fail to start (<code class="inline">ContainerCreating</code> stuck, <code class="inline">CreateContainerError</code>).</td></tr>
                <tr><td><code class="inline">crictl ps -a</code></td><td>ALL containers on this node (running + stopped). Shows container IDs, images, state, and creation time. Uses the CRI API directly — works even if kubelet is down.</td><td>When kubectl is unavailable or you need to see containers that kubelet doesn't show. Essential for node-level debugging.</td></tr>
                <tr><td><code class="inline">crictl logs &lt;container-id&gt;</code></td><td>Container stdout/stderr logs via the CRI API. Same content as <code class="inline">kubectl logs</code> but works without the API server.</td><td>When the API server is down but containers are still running. Or when kubectl logs times out.</td></tr>
                <tr><td><code class="inline">kubectl describe node wk-04 | grep -A10 Conditions</code></td><td>Node conditions: Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable. Each condition shows status (True/False/Unknown), reason, and last transition time.</td><td>When a node shows NotReady. The Conditions section tells you WHY — is it memory pressure? Disk full? Network plugin missing?</td></tr>
                <tr><td><code class="inline">kubectl get events -A --sort-by='.lastTimestamp'</code></td><td>All cluster events sorted by time (newest first). Shows scheduling decisions, image pulls, volume mounts, probe failures, and errors.</td><td>When you don't know what's wrong and need a broad view. Events are retained for ~1 hour — check quickly after a failure.</td></tr>
            </table>
        </div>

        <!-- 9.7 BOOTSTRAP TOKEN MANAGEMENT -->
        <h3 id="part-9-7">9.7 Bootstrap Token Management</h3>
        <div class="api-block">
            <p>Manage the tokens used to join new nodes. Tokens expire after 24 hours by default. Full token details in <a href="#part-1-5">Part 1.5</a>:</p>
            <table>
                <tr><th style="width:250px;">Command</th><th>What It Does</th></tr>
                <tr><td><code class="inline">kubeadm token list</code></td><td>Shows all active bootstrap tokens with their TTL, expiration, and associated groups. Tokens that have expired still show in the list but can't be used.</td></tr>
                <tr><td><code class="inline">kubeadm token create --print-join-command</code></td><td>Creates a NEW bootstrap token and prints the complete <code class="inline">kubeadm join</code> command. Copy-paste this directly onto the new node. Add <code class="inline">--ttl 0</code> for a non-expiring token (use with caution).</td></tr>
                <tr><td><code class="inline">kubeadm token delete &lt;token-id&gt;</code></td><td>Revokes a token. The token ID is the first part of the token string (before the dot). Use this to clean up old tokens or revoke a compromised token.</td></tr>
            </table>

            <div class="info">
                <strong>💡 Pro Tip:</strong> Store the join command from <code class="inline">kubeadm token create --print-join-command</code> in your password manager or secure documentation. You'll need it when adding replacement nodes or recovering from a hardware failure. Don't rely on finding the original init output months later.
            </div>
        </div>

        <!-- 9.8 CLUSTER RESET -->
        <h3 id="part-9-8">9.8 Cluster Reset — DESTROY and Start Over</h3>
        <div class="api-block">
            <div class="warning">
                <strong>🔴 DANGER: This DESTROYS all Kubernetes state on the node.</strong> This is irreversible — all Pods, configurations, and certificates on this node will be deleted. Only use this when decommissioning a node or rebuilding a broken cluster. For the full reset/rejoin procedure, see <a href="#part-7-2">Part 7.2</a>.
            </div>

            <table>
                <tr><th style="width:250px;">Command</th><th>What It Destroys</th></tr>
                <tr><td><code class="inline">kubeadm reset -f</code></td><td>Stops the kubelet. Deletes <code class="inline">/etc/kubernetes/</code> (all manifests, certs, kubeconfigs). Removes the node from the cluster if the API server is reachable. The <code class="inline">-f</code> flag skips confirmation prompts.</td></tr>
                <tr><td><code class="inline">rm -rf /etc/cni/net.d /var/lib/kubelet /var/lib/etcd</code></td><td>Removes CNI configuration (Calico IPAM state), kubelet state (Pod data, volumes, secrets), and etcd data (the entire database — ONLY run this on CP nodes you're resetting).</td></tr>
                <tr><td><code class="inline">iptables -F && iptables -t nat -F && iptables -t mangle -F</code></td><td>Flushes ALL iptables rules in all tables. Removes kube-proxy's iptables rules and any leftover Calico/CNI rules. The node's networking returns to pre-Kubernetes state.</td></tr>
                <tr><td><em>IP link cleanup</em></td><td><code class="inline">ip link delete cni0 2>/dev/null; ip link delete flannel.1 2>/dev/null</code> — removes CNI bridge interfaces. The <code class="inline">2>/dev/null</code> suppresses errors if the interfaces don't exist (if using a different CNI).</td></tr>
                <tr><td><code class="inline">systemctl restart containerd</code></td><td>Restarts the container runtime to clean up any lingering container state. After this, the node is completely clean and ready to re-join the cluster with <code class="inline">kubeadm join</code>.</td></tr>
            </table>

            <div class="diagram-box">
                <div class="diagram-title">🔄 Complete Node Reset Procedure (Copy-Paste)</div>
                <pre><code class="language-bash"># === DESTROY KUBERNETES ON THIS NODE ===
# WARNING: This is IRREVERSIBLE

kubeadm reset -f
rm -rf /etc/cni/net.d /var/lib/kubelet /var/lib/etcd
iptables -F && iptables -t nat -F && iptables -t mangle -F
ip link delete cni0 2>/dev/null
ip link delete flannel.1 2>/dev/null
systemctl restart containerd

# Now the node is clean.
# To re-join as a worker: kubeadm join 10.0.0.100:6443 --token &lt;token&gt; --discovery-token-ca-cert-hash sha256:&lt;hash&gt;
# To re-join as a CP:     Add --control-plane --certificate-key &lt;key&gt;
# To re-init as cp-01:    kubeadm init --config=kubeadm-config.yaml --upload-certs</code></pre>
            </div>
        </div>
    </section>'''

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\k8s-cluster-structure.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <section class="section" id="part-9">
        <h2>⚡ <span class="section-num">Part 9</span> — Day 2 Maintenance Cheat Sheet</h2>
        <div class="section-intro"><p>Quick reference: cluster health, etcd operations, certificate management, node maintenance, diagnostics, and cluster reset.</p></div>
    </section>'''

html = html.replace(old, content)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)

# Check for unescaped << in code blocks
part9_start = html.find('<section class="section" id="part-9">')
part9_end = html.find('</main>')
part9 = html[part9_start:part9_end]
heredoc_count = part9.count('<<')
escaped_count = part9.count('&lt;&lt;')
print(f'Total: {html.count(chr(10))} lines, Part 9: {content.count(chr(10))} lines')
print(f'Tables: {content.count("<table>")}, Code blocks: {content.count("<pre><code")}, ASCII: {content.count("ascii-block")}')
print(f'Highlights: {content.count("highlight-box")}, Warnings: {content.count("warning")}, Infos: {content.count("class=\"info\"")}')
if heredoc_count > 0 and heredoc_count != escaped_count:
    print(f'WARNING: {heredoc_count} << found vs {escaped_count} escaped!')
else:
    print(f'<< check: {heredoc_count} total, all properly escaped')
