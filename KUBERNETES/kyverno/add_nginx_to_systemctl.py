import re

fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\systemd_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

replacements = []

# ── 1. Update section-intro to mention nginx ──
r1 = {
    'old': '''    <p><code class="inline">systemctl</code> is the central management tool for controlling the systemd system and service manager. On Kubernetes nodes, it manages <strong>kubelet</strong> (the node agent), <strong>containerd</strong> (container runtime), and control plane components such as <strong>kube-apiserver</strong>, <strong>etcd</strong>, <strong>kube-scheduler</strong>, <strong>kube-controller-manager</strong>, and <strong>kube-proxy</strong>.</p>''',
    'new': '''    <p><code class="inline">systemctl</code> is the central management tool for controlling the systemd system and service manager. On Kubernetes nodes, it manages <strong>kubelet</strong> (the node agent), <strong>containerd</strong> (container runtime), and control plane components. On frontend nodes, it manages <strong>nginx</strong> (Ingress/reverse proxy) — and on every Linux server, it manages <strong>sshd</strong>, <strong>cron</strong>, and countless other daily services.</p>'''
}
replacements.append(r1)

# ── 2. Update overview description to mention nginx ──
r2 = {
    'old': '''                    <p>For the <strong>anihpj</strong> platform, each cluster runs 3 control plane nodes and 5 worker nodes. Every node has <code class="inline">kubelet</code> and <code class="inline">containerd</code> managed by systemd. Control plane nodes additionally run the API server, etcd, scheduler, and controller manager as systemd services.</p>''',
    'new': '''                    <p>For the <strong>anihpj</strong> platform, each cluster runs 3 control plane nodes, 5 worker nodes, and 2 frontend nodes. Every node has <code class="inline">kubelet</code> and <code class="inline">containerd</code> managed by systemd. Frontend nodes run <code class="inline">nginx</code> as the Ingress/reverse proxy. Control plane nodes additionally run the API server, etcd, scheduler, and controller manager.</p>'''
}
replacements.append(r2)

# ── 3. Update overview Syntax to include nginx ──
r3 = {
    'old': '''systemctl list-units 'kube*'        # List all K8s-related services</code></pre>''',
    'new': '''systemctl list-units 'kube*'        # List all K8s-related services

# Classic everyday usage:
systemctl start nginx              # Start Nginx web server
systemctl reload nginx             # Reload Nginx config (zero downtime)
systemctl status sshd              # Check SSH daemon status
systemctl enable cron              # Ensure cron starts at boot</code></pre>'''
}
replacements.append(r3)

# ── 4. Update context block to include nginx ──
r4 = {
    'old': '''<pre><code class="language-bash"># Every Kubernetes node runs these systemd services:
# /etc/systemd/system/kubelet.service       — K8s node agent (registers with API server)
# /etc/systemd/system/containerd.service    — Container runtime (runs your Pods)
# /etc/systemd/system/kube-proxy.service    — Network proxy & load balancer
#
# Control plane nodes additionally run:
# /etc/systemd/system/kube-apiserver.service       — Front-end to the control plane
# /etc/systemd/system/kube-scheduler.service       — Pod scheduler
# /etc/systemd/system/kube-controller-manager.service — Controller loops
# /etc/systemd/system/etcd.service                 — Cluster state database</code></pre>''',
    'new': '''<pre><code class="language-bash"># Every Kubernetes node runs these systemd services:
# /etc/systemd/system/kubelet.service       — K8s node agent (registers with API server)
# /etc/systemd/system/containerd.service    — Container runtime (runs your Pods)
# /etc/systemd/system/kube-proxy.service    — Network proxy & load balancer
#
# Control plane nodes additionally run:
# /etc/systemd/system/kube-apiserver.service       — Front-end to the control plane
# /etc/systemd/system/kube-scheduler.service       — Pod scheduler
# /etc/systemd/system/kube-controller-manager.service — Controller loops
# /etc/systemd/system/etcd.service                 — Cluster state database
#
# Frontend / general-purpose nodes:
# /etc/systemd/system/nginx.service         — Reverse proxy / Ingress controller
# /etc/systemd/system/sshd.service          — SSH daemon (remote access)</code></pre>'''
}
replacements.append(r4)

# ── 5. Add nginx example 2 to overview list-units (make it more relatable) ──
r5 = {
    'old': '''                <div class="example">
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
                </div>''',
    'new': '''                <div class="example">
                    <h5>Example 2: List All Kubernetes Services on a Control Plane Node</h5>
                    <p><strong>Scenario:</strong> Alice audits all K8s-related services running on control plane node cp-01.</p>
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
                    <h5>Example 2b: Check Nginx Status (Relatable Daily Use)</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/systemd/system/nginx.service — the anihpj Ingress/reverse proxy
# Runs on frontend nodes fe-01 and fe-02, handling all external traffic</code></pre>
                    <p><strong>Scenario:</strong> Carol checks if Nginx is running on frontend node fe-01 before deploying a configuration update.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.service — Nginx Ingress Proxy for anihpj
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled)
     Active: active (running) since Fri 2026-06-06 08:00:00 UTC; 4h ago
   Main PID: 890 (nginx)
      Tasks: 5 (limit: 4915)
     Memory: 45.2M
        CPU: 12.345s
     CGroup: /system.slice/nginx.service
             ├─890 nginx: master process
             ├─891 nginx: worker process
             └─892 nginx: worker process</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx is active (running), enabled at boot, 45MB memory — normal for a reverse proxy. Two worker processes handling connections. Carol can proceed with the config update; she'll use <code>systemctl reload nginx</code> for zero-downtime deployment.</p>
                </div>'''
}
replacements.append(r5)

# ── 6. systemctl start — add nginx example ──
r6 = {
    'old': '''                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> Always start <code>containerd</code> before <code>kubelet</code> — kubelet needs the container runtime socket. On control plane nodes, start order: <code>etcd → kube-apiserver → kube-controller-manager → kube-scheduler → kubelet → kube-proxy</code>. Use <code>kubectl get node</code> (not just <code>systemctl is-active</code>) to confirm the cluster sees the node as Ready.
                </div>''',
    'new': '''                <div class="success">
                    <strong>💡 Pro Tip:</strong> Always start <code>containerd</code> before <code>kubelet</code> — kubelet needs the container runtime socket. On control plane nodes, start order: <code>etcd → kube-apiserver → kube-controller-manager → kube-scheduler → kubelet → kube-proxy</code>. For nginx, <code>systemctl start nginx</code> is idempotent — safe to run even if already running. Use <code>kubectl get node</code> (not just <code>systemctl is-active</code>) to confirm the cluster sees the node as Ready.
                </div>'''
}
replacements.append(r6)

# ── 7. Add nginx start example before the start section's Pro Tip ──
r7 = {
    'old': '''                <div class="example">
                    <h5>Example 5: Start etcd Backup Timer</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Start Nginx (Generic Web Server)</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/systemd/system/nginx.service — standard Nginx unit
# ExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf
# Carol deploys Nginx on fe-02 after initial setup</code></pre>
                    <p><strong>Scenario:</strong> Carol starts Nginx on frontend node fe-02 after a fresh install and configuration.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start nginx && systemctl is-active nginx && curl -sI http://localhost | head -1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active
HTTP/1.1 200 OK</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx started, confirmed active by systemd AND responding with HTTP 200. Two-level verification: systemd process check + application-level health check. This is the standard pattern — don't just trust <code>is-active</code>, also check the application responds correctly.</p>
                </div>

                <div class="example">
                    <h5>Example 6: Start etcd Backup Timer</h5>'''
}
replacements.append(r7)

# ── 8. systemctl stop — add nginx example ──
r8 = {
    'old': '''                <div class="success">
                    <strong>💡 Kubernetes Pro Tip:</strong> NEVER stop kubelet on a worker node without draining first: <code>kubectl drain &lt;node&gt; --ignore-daemonsets --delete-emptydir-data</code>. Stopping kubelet without draining causes Pods to become unmanaged and the API server marks them as Unknown after the node's lease expires (default 40s). Stop containerd only after kubelet to prevent race conditions.
                </div>''',
    'new': '''                <div class="success">
                    <strong>💡 Pro Tip:</strong> NEVER stop kubelet on a worker node without draining first: <code>kubectl drain &lt;node&gt; --ignore-daemonsets --delete-emptydir-data</code>. For nginx, stopping drops all active connections — use <code>reload</code> instead for config changes. Stop sends SIGTERM first, then SIGKILL after <code>TimeoutStopSec</code>. Always prefer <code>reload</code> over <code>stop+start</code> for zero-downtime.
                </div>'''
}
replacements.append(r8)

# ── 9. Add nginx stop example before stop section's Example 3 ──
r9 = {
    'old': '''                <div class="example">
                    <h5>Example 3: Stop with Timeout (Force Kill Fallback)</h5>
                    <p><strong>Scenario:</strong> Alice stops kubelet but it's hanging (stuck on a Pod teardown). She implements a timeout with force-kill.</p>''',
    'new': '''                <div class="example">
                    <h5>Example 3: Stop Nginx Before Binary Upgrade</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># Nginx binary upgrade from v1.26 to v1.27 on fe-01
# Carol stops Nginx, upgrades the binary, then restarts</code></pre>
                    <p><strong>Scenario:</strong> Carol stops Nginx on fe-01 before upgrading the Nginx binary package.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-active --quiet nginx && systemctl stop nginx && echo "Nginx stopped — ready for upgrade" || echo "Nginx already stopped"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Nginx stopped — ready for upgrade</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx was running, so it was stopped. During this window, traffic to fe-01 will be routed to fe-02 by the load balancer. After the binary upgrade, Carol will <code>systemctl start nginx</code> and traffic resumes. This pattern applies to ANY service, not just K8s — nginx, postgresql, redis, etc.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Stop with Timeout (Force Kill Fallback)</h5>
                    <p><strong>Scenario:</strong> Alice stops kubelet but it's hanging (stuck on a Pod teardown). She implements a timeout with force-kill.</p>'''
}
replacements.append(r9)

# ── 10. Renumber stop examples 3→4, 4→5, 5→6 ──
r10 = {
    'old': '''                <div class="example">
                    <h5>Example 3: Stop with Timeout (Force Kill Fallback)</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 4: Stop with Timeout (Force Kill Fallback)</h5>'''
}
replacements.append(r10)

r10b = {
    'old': '''                <div class="example">
                    <h5>Example 4: Stop Before Editing Kubelet Config</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Stop Before Editing Kubelet Config</h5>'''
}
replacements.append(r10b)

r10c = {
    'old': '''                <div class="example">
                    <h5>Example 5: Conditional Stop (Only if Running)</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 6: Conditional Stop (Only if Running)</h5>'''
}
replacements.append(r10c)

# ── 11. systemctl restart — add nginx example ──
r11 = {
    'old': '''                <div class="example">
                    <h5>Example 1: Restart Kubelet After Config Change</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 1: Restart Nginx After Config Change</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/nginx/sites-enabled/anihpj.conf — the anihpj site config
# Dave adds a new location block for /api/v2 endpoint</code></pre>
                    <p><strong>Scenario:</strong> Dave updates Nginx config and restarts to apply the change (connections will drop briefly).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nginx -t && systemctl restart nginx && systemctl is-active nginx && curl -sI https://anihpj.io/api/v2 | head -1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">nginx: configuration file /etc/nginx/nginx.conf test is successful
active
HTTP/2 200</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Config validated, Nginx restarted, confirmed active, new /api/v2 endpoint responds 200. Connections dropped for ~500ms during restart. For zero-downtime, use <code>systemctl reload nginx</code> instead — nginx supports graceful reload. Use restart only for major changes that can't be hot-reloaded.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Restart Kubelet After Config Change</h5>'''
}
replacements.append(r11)

# ── 12. Renumber restart examples ──
r12 = {
    'old': '''                <div class="example">
                    <h5>Example 2: Restart Containerd Then Kubelet (Runtime Update)</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 3: Restart Containerd Then Kubelet (Runtime Update)</h5>'''
}
replacements.append(r12)

r12b = {
    'old': '''                <div class="example">
                    <h5>Example 3: Conditional Restart (only if running)</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 4: Conditional Restart (only if running)</h5>'''
}
replacements.append(r12b)

r12c = {
    'old': '''                <div class="example">
                    <h5>Example 4: Restart with Pre-Flight Config Validation</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Restart with Pre-Flight Config Validation</h5>'''
}
replacements.append(r12c)

r12d = {
    'old': '''                <div class="example">
                    <h5>Example 5: Restart etcd for Certificate Rotation</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 6: Restart etcd for Certificate Rotation</h5>'''
}
replacements.append(r12d)

# ── 13. systemctl reload — make nginx the first example (it's the classic reload use case) ──
r13 = {
    'old': '''                <div class="example">
                    <h5>Example 1: Reload kube-proxy Config (Zero Downtime)</h5>
                    <p><strong>Scenario:</strong> Carol updates kube-proxy's iptables mode and reloads without disrupting traffic.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /var/lib/kube-proxy/config.conf && systemctl reload kube-proxy && echo "kube-proxy reloaded — iptables rules updated"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">kube-proxy reloaded — iptables rules updated</div>
                    <p class="output-note"><strong>📝 What happened:</strong> kube-proxy re-read its config and updated iptables rules without dropping existing connections. Reload is much faster than restart — and doesn't disrupt active connections to ClusterIP services.</p>
                </div>''',
    'new': '''                <div class="example">
                    <h5>Example 1: Reload Nginx Config (Classic Zero-Downtime)</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/nginx/conf.d/anihpj.conf — the anihpj site configuration
# Carol adds a new upstream server block for load balancing</code></pre>
                    <p><strong>Scenario:</strong> Carol adds a new upstream backend to Nginx and reloads without dropping a single connection.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "server 10.0.1.25:8080;" >> /etc/nginx/conf.d/upstream.conf && nginx -t && systemctl reload nginx && echo "Reloaded — 0 connections dropped"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">nginx: configuration file test is successful
Reloaded — 0 connections dropped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx re-read the config — existing connections continue on old workers; new connections use the updated config with the new upstream. Nginx is the gold standard for graceful reload — this is the #1 reason admins love nginx. PID stays the same, all connections preserved.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Reload kube-proxy Config (Zero Downtime)</h5>
                    <p><strong>Scenario:</strong> Carol updates kube-proxy's iptables mode and reloads without disrupting traffic.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /var/lib/kube-proxy/config.conf && systemctl reload kube-proxy && echo "kube-proxy reloaded — iptables rules updated"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">kube-proxy reloaded — iptables rules updated</div>
                    <p class="output-note"><strong>📝 What happened:</strong> kube-proxy re-read its config and updated iptables rules without dropping existing connections. Reload is much faster than restart — and doesn't disrupt active connections to ClusterIP services.</p>
                </div>'''
}
replacements.append(r13)

# ── 14. Renumber reload examples ──
r14 = {
    'old': '''                <div class="example">
                    <h5>Example 2: Reload Not Supported — Fallback to Restart</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 3: Reload Not Supported — Fallback to Restart</h5>'''
}
replacements.append(r14)

r14b = {
    'old': '''                <div class="example">
                    <h5>Example 3: Reload vs Restart Timing Comparison</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 4: Reload vs Restart Timing Comparison</h5>'''
}
replacements.append(r14b)

r14c = {
    'old': '''                <div class="example">
                    <h5>Example 4: Verify PID Stability After Reload</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Verify PID Stability After Reload</h5>'''
}
replacements.append(r14c)

r14d = {
    'old': '''                <div class="example">
                    <h5>Example 5: Batch Reload on Control Plane</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 6: Batch Reload on Control Plane</h5>'''
}
replacements.append(r14d)

# ── 15. Update reload Pro Tip ──
r15 = {
    'old': '''                    <strong>💡 Kubernetes Pro Tip:</strong> Most K8s components do NOT support <code>reload</code>. Use <code>restart</code> instead. kube-proxy is the notable exception if <code>ExecReload=</code> is configured. For production cert rotation, restart one control plane component at a time. Verify with <code>kubectl get cs</code> (componentstatus) after each restart.
                </div>''',
    'new': '''                    <strong>💡 Pro Tip:</strong> <code>reload</code> is the preferred way to apply config changes — zero downtime, faster, and no PID change. Nginx is the gold standard for reload: <code>nginx -t && systemctl reload nginx</code>. Most K8s components do NOT support reload — use <code>restart</code> instead. kube-proxy is the K8s exception. For production cert rotation, restart one component at a time.
                </div>'''
}
replacements.append(r15)

# ── 16. Add nginx example to status article ──
r16 = {
    'old': '''                <div class="example">
                    <h5>Example 1: Full Status of Healthy Kubelet</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 1: Status of Nginx (Relatable Daily Use)</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/systemd/system/nginx.service — anihpj Ingress proxy on fe-01
# Carol checks Nginx health during a traffic spike investigation</code></pre>
                    <p><strong>Scenario:</strong> Carol checks Nginx status on fe-01 during a traffic spike — is it overloaded?</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.service — Nginx Ingress Proxy for anihpj
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled)
     Active: active (running) since Fri 2026-06-06 06:00:00 UTC; 6h ago
   Main PID: 890 (nginx)
      Tasks: 9 (limit: 4915)
     Memory: 187.3M
        CPU: 2h 15min 34.123s
     CGroup: /system.slice/nginx.service
             ├─890 nginx: master process
             ├─891 nginx: worker process
             ├─892 nginx: worker process
             ├─893 nginx: worker process
             └─894 nginx: worker process</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx is active, 187MB memory (normal under load), 4 worker processes. Tasks: 9 (includes cache manager/loader). CPU time: 2h15min over 6h runtime = ~37% average CPU utilization — healthy. The green dot (●) means everything is fine. Carol can rule out Nginx as the bottleneck.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Full Status of Healthy Kubelet</h5>'''
}
replacements.append(r16)

# ── 17. Renumber status examples ──
r17 = {
    'old': '''                <div class="example">
                    <h5>Example 2: Status of Failed Kubelet (Node Unhealthy)</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 3: Status of Failed Kubelet (Node Unhealthy)</h5>'''
}
replacements.append(r17)

r17b = {
    'old': '''                <div class="example">
                    <h5>Example 3: Check All Critical Services on Control Plane</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 4: Check All Critical Services on Control Plane</h5>'''
}
replacements.append(r17b)

r17c = {
    'old': '''                <div class="example">
                    <h5>Example 4: Status of containerd with Recent Pod Events</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Status of containerd with Recent Pod Events</h5>'''
}
replacements.append(r17c)

r17d = {
    'old': '''                <div class="example">
                    <h5>Example 5: Status with Custom Property Extraction</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 6: Status with Custom Property Extraction</h5>'''
}
replacements.append(r17d)

# ── 18. Add nginx example to enable article ──
r18 = {
    'old': '''                <div class="example">
                    <h5>Example 1: Enable Kubelet to Survive Node Reboots</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 1: Enable Nginx to Auto-Start at Boot</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># Everyone's favorite — ensure Nginx survives server reboots
# Carol enables Nginx on the new frontend node fe-02</code></pre>
                    <p><strong>Scenario:</strong> Carol ensures Nginx starts automatically whenever fe-02 reboots.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable nginx && systemctl is-enabled nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /etc/systemd/system/nginx.service.
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Symlink created — when the server boots and reaches multi-user.target, Nginx auto-starts. This is the same mechanism for ALL services: kubelet, nginx, sshd — <code>enable</code> creates a symlink in <code>multi-user.target.wants/</code>. Without this, a reboot means manual intervention.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Enable Kubelet to Survive Node Reboots</h5>'''
}
replacements.append(r18)

# ── 19. Renumber enable examples ──
r19 = {
    'old': '''                <div class="example">
                    <h5>Example 2: Enable and Start Containerd + Kubelet in One Go</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 3: Enable and Start Containerd + Kubelet in One Go</h5>'''
}
replacements.append(r19)

r19b = {
    'old': '''                <div class="example">
                    <h5>Example 3: Enable All Control Plane Services</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 4: Enable All Control Plane Services</h5>'''
}
replacements.append(r19b)

r19c = {
    'old': '''                <div class="example">
                    <h5>Example 4: Disable Kubelet Before Draining & Decommissioning</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 5: Disable Kubelet Before Draining & Decommissioning</h5>'''
}
replacements.append(r19c)

r19d = {
    'old': '''                <div class="example">
                    <h5>Example 5: Verify All Critical Services Are Enabled</h5>''',
    'new': '''                <div class="example">
                    <h5>Example 6: Verify All Critical Services Are Enabled</h5>'''
}
replacements.append(r19d)

# ── 20. Update enable Pro Tip ──
r20 = {
    'old': '''                    <strong>💡 Kubernetes Pro Tip:</strong> Every K8s node MUST have <code>kubelet</code> and <code>containerd</code> enabled. Without this, a reboot takes the node offline until manual intervention. Use <code>enable --now</code> for node bootstrap — one command instead of two. After disabling kubelet, also disable kube-proxy and containerd to fully clean up.
                </div>''',
    'new': '''                    <strong>💡 Pro Tip:</strong> Every K8s node MUST have <code>kubelet</code> and <code>containerd</code> enabled. Every server running nginx MUST have <code>nginx</code> enabled. This is Server Administration 101 — if it's not enabled, it won't survive a reboot. Use <code>enable --now</code> to enable AND start in one command. Run <code>systemctl is-enabled &lt;service&gt;</code> to verify before reboots.
                </div>'''
}
replacements.append(r20)

# ── 21. Add nginx to systemctl kill examples ──
r21 = {
    'old': '''systemctl kill -s KILL kubelet         # Force kill (last resort for stuck kubelet)</code></pre>''',
    'new': '''systemctl kill -s KILL kubelet         # Force kill (last resort for stuck kubelet)

# Generic examples:
systemctl kill -s HUP nginx          # Graceful reload (nginx classic)
systemctl kill -s TERM nginx         # Graceful stop</code></pre>'''
}
replacements.append(r21)

# ── 22. Add nginx kill example ──
r22 = {
    'old': '''                <div class="example">
                    <h5>Example 3: Common K8s Kill Signals Reference</h5>
                    <p><strong>Scenario:</strong> Alice learns the common signals used with Kubernetes services.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "Common K8s signals:''',
    'new': '''                <div class="example">
                    <h5>Example 3: Send HUP to Nginx (Classic Graceful Reload via Signal)</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># Classic Linux pattern: sending SIGHUP to nginx master process
# This is what `systemctl reload nginx` does internally — sends HUP</code></pre>
                    <p><strong>Scenario:</strong> Carol sends a HUP signal to Nginx (same effect as <code>systemctl reload nginx</code>).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl kill -s HUP nginx && systemctl show nginx -p MainPID && curl -sI http://localhost | head -1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">MainPID=890
HTTP/1.1 200 OK</div>
                    <p class="output-note"><strong>📝 What happened:</strong> HUP signal caused Nginx to reload config — PID stayed the same (890). Nginx responds 200. This is the classic Linux pattern: HUP = reload config without restart. Every Unix admin knows this. Same pattern works for nginx, apache, and many other daemons.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Common Signals Reference (K8s & Nginx)</h5>
                    <p><strong>Scenario:</strong> Alice learns the common signals across both K8s services and generic Linux daemons.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "Common signals for systemctl kill:'''
}
replacements.append(r22)

# ── 23. Update kill signal reference content ──
r23 = {
    'old': '''SIGHUP (1)  — Reload config (kube-proxy only)
SIGTERM (15) — Graceful stop (default for systemctl stop)
SIGKILL (9)  — Force kill (last resort)
SIGUSR1 (10) — Debug dump (kubelet, containerd)
SIGUSR2 (12) — Custom (varies by service)"</code></pre>
                    <p class="output-note"><strong>📝 What happened:</strong> Signal reference — most K8s components use standard signal conventions. <code>systemctl stop</code> sends SIGTERM first; if the process doesn't exit within <code>TimeoutStopSec</code>, systemd sends SIGKILL. Use <code>systemctl kill -s</code> to send any signal.</p>
                </div>''',
    'new': '''SIGHUP (1)  — Reload config (nginx, kube-proxy)
SIGTERM (15) — Graceful stop (default — all services)
SIGKILL (9)  — Force kill (last resort)
SIGUSR1 (10) — Debug dump (kubelet, containerd, nginx log reopen)
SIGUSR2 (12) — Graceful shutdown (nginx workers)"</code></pre>
                    <p class="output-note"><strong>📝 What happened:</strong> Signal reference covering both K8s and generic Linux daemons. <code>systemctl stop</code> sends SIGTERM first; if the process doesn't exit within <code>TimeoutStopSec</code>, systemd sends SIGKILL. Nginx uses USR2 for graceful upgrade (start new master, let old workers drain). Use <code>systemctl kill -s</code> to send any signal.</p>
                </div>'''
}
replacements.append(r23)

# ── 24. Update systemctl overview Pro Tip ──
r24 = {
    'old': '''                    <strong>💡 Kubernetes Pro Tip:</strong> <code>systemctl status kubelet</code> is always the first command on any node showing NotReady. The kubelet and containerd MUST be enabled on every node. Before stopping kubelet on a worker node, ALWAYS drain it: <code>kubectl drain &lt;node&gt; --ignore-daemonsets --delete-emptydir-data</code>. Control plane services (apiserver, etcd, scheduler, controller-manager) should NEVER all be down simultaneously.
                </div>''',
    'new': '''                    <strong>💡 Pro Tip:</strong> <code>systemctl status</code> is always the first diagnostic command — whether it's kubelet on a K8s node or nginx on a web server. The kubelet and containerd MUST be enabled on every K8s node. Before stopping kubelet, drain the node. For nginx config changes, prefer <code>reload</code> over <code>restart</code> for zero downtime. Control plane services should NEVER all be down simultaneously.
                </div>'''
}
replacements.append(r24)

# ── Execute all replacements ──
for i, r in enumerate(replacements):
    old = r['old']
    new = r['new']
    if old not in c:
        print(f'REPLACEMENT {i+1} FAILED: old string not found')
        # Show first 120 chars of old for debugging
        print(f'  Old starts with: {old[:120]}...')
    else:
        c = c.replace(old, new, 1)
        print(f'Replacement {i+1}: OK')

# Verify
print(f'\nArticles: {c.count("<article class=")}/{c.count("</article>")}')
print(f'Examples: {c.count("class=\"example\"")}')
print(f'Lines: {len(c.split(chr(10)))}')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

print('Done — nginx examples blended into systemctl section')
