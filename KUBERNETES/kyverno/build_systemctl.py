fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\systemd_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

content = '''            <!-- ==================== systemctl overview ==================== -->
            <article class="api-block" id="systemctl-overview">
                <h3>systemctl — The Systemd Service Manager</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">CORE</span>
                    <span class="tag">systemctl</span>
                    <span class="tag">Service Management</span>
                </div>
                <p class="api-subtitle">The central management tool for controlling the systemd system and service manager</p>
                <div class="api-description">
                    <p><code class="inline">systemctl</code> is the primary command for interacting with systemd. It controls services, checks status, manages boot-time behavior, inspects the system state, and handles power management. Every Linux administrator uses it daily.</p>
                    <p>For the <strong>anihpj</strong> infrastructure, <code class="inline">systemctl</code> manages Nginx (reverse proxy), the web application service, background workers, and periodic backup/cleanup timers. These services run both on bare-metal VMs and inside Kubernetes nodes.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl [OPTIONS...] COMMAND [UNIT...]

# Core commands:
systemctl start nginx              # Start a service
systemctl stop nginx               # Stop a service
systemctl restart nginx            # Restart a service
systemctl reload nginx             # Reload config (no downtime)
systemctl status nginx             # Check runtime status
systemctl enable nginx             # Auto-start at boot
systemctl disable nginx            # Disable auto-start
systemctl list-units --type=service  # List all services</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Flag</th><th>Description</th></tr></thead>
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

                <h4>📄 Context — Daily System Administration:</h4>
                <pre><code class="language-bash"># The anihpj infrastructure runs these services:
# /etc/systemd/system/nginx.service       — Reverse proxy (port 80/443)
# /etc/systemd/system/webapp.service       — Main application
# /etc/systemd/system/worker.service       — Background job processor
# /etc/systemd/system/backup.timer         — Daily database backup</code></pre>

                <div class="example">
                    <h5>Example 1: Check Service Status</h5>
                    <p><strong>📁 Context:</strong></p>
                    <pre><code class="language-bash"># /etc/systemd/system/nginx.service — the anihpj reverse proxy
# Carol checks if Nginx is running before a deployment</code></pre>
                    <p><strong>Scenario:</strong> Carol verifies Nginx is running on prod-web-01 before deploying a new app version.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.service — Nginx Reverse Proxy for anihpj
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled)
     Active: active (running) since Fri 2026-06-06 08:00:00 UTC; 2h ago
   Main PID: 1234 (nginx)
      Tasks: 5 (limit: 4915)
     Memory: 45.2M
        CPU: 2.345s
     CGroup: /system.slice/nginx.service
             ├─1234 nginx: master process
             ├─1235 nginx: worker process</div>
                    <p class="output-note"><strong>📝 What happened:</strong> STATUS=active (running), PID=1234, running for 2 hours. The service is "enabled" (auto-starts at boot). Memory usage is 45MB — normal for a proxy. Carol proceeds with deployment because Nginx is healthy.</p>
                </div>

                <div class="example">
                    <h5>Example 2: List All Running Services</h5>
                    <p><strong>Scenario:</strong> Alice audits all active services on the production server.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --type=service --state=running</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                 LOAD   ACTIVE SUB     DESCRIPTION
nginx.service        loaded active running Nginx Reverse Proxy for anihpj
webapp.service       loaded active running anihpj Web Application
worker.service       loaded active running anihpj Background Worker
sshd.service         loaded active running OpenSSH Daemon
cron.service         loaded active running Regular background program processing</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Five services are running: Nginx, webapp, worker, SSH, and cron. Alice can see SUB state — all are "running" (not "exited" or "dead"). This is the morning health check for every production server.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Enable a Service to Auto-Start at Boot</h5>
                    <p><strong>Scenario:</strong> Carol ensures Nginx starts automatically whenever the server reboots.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable nginx && systemctl is-enabled nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /etc/systemd/system/nginx.service.
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> A symlink was created in <code>multi-user.target.wants/</code> — this is how systemd implements "enable". When the server boots and reaches multi-user.target, it will start Nginx automatically. <code>is-enabled</code> confirms the state.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Check Failed Services</h5>
                    <p><strong>Scenario:</strong> Alice checks for any failed services after a kernel update reboot.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --state=failed</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT                 LOAD   ACTIVE SUB    DESCRIPTION
worker.service       loaded failed failed anihpj Background Worker</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The worker service failed after reboot — possibly a dependency issue (database not ready yet). Alice investigates the logs. Failed services are the first thing to check after any system change. Zero failed services = healthy system.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Stop and Start a Service (Restart Cycle)</h5>
                    <p><strong>Scenario:</strong> Dave stops Nginx to apply configuration changes, then starts it back.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop nginx && echo "Nginx stopped" && sleep 2 && systemctl start nginx && systemctl is-active nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Nginx stopped
active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx was stopped (connections dropped briefly), then restarted 2 seconds later. <code>is-active</code> confirms it's running again. For zero-downtime, use <code>systemctl reload</code> instead. Stop+start is for major configuration changes that can't be hot-reloaded.</p>
                </div>

                <div class="success">
                    <strong>💡 Systemd Pro Tip:</strong> <code>systemctl status</code> is always the first command — it shows everything you need in one output: state, PID, memory, recent logs. Use <code>list-units --state=failed</code> to find problems fast. <code>enable</code> creates symlinks in <code>multi-user.target.wants/</code>. <code>daemon-reload</code> after ANY unit file change.
                </div>
            </article>

            <!-- ==================== systemctl start ==================== -->
            <article class="api-block" id="systemctl-start">
                <h3>systemctl start</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">START</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Start (activate) one or more systemd units — bring services online</p>
                <div class="api-description">
                    <p><code class="inline">systemctl start</code> brings a unit into the active state. If already active, it's a no-op. Units can be services (.service), sockets (.socket), timers (.timer), or targets (.target). The <code>.service</code> suffix is assumed if omitted.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl start UNIT...
systemctl start nginx
systemctl start nginx.service webapp.service worker.service</code></pre>

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

                <h4>📄 Context — Starting Services:</h4>
                <pre><code class="language-bash"># After deploying new configuration, Carol restarts the webapp:
# systemctl start webapp
# The service definition in /etc/systemd/system/webapp.service:
# ExecStart=/opt/anihpj/bin/webapp --config /etc/anihpj/config.yaml</code></pre>

                <div class="example">
                    <h5>Example 1: Start a Single Service</h5>
                    <p><strong>Scenario:</strong> Carol starts Nginx after a configuration update.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start nginx && systemctl is-active nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx started. <code>is-active</code> returns "active" — the service is running. If the service was already running, <code>start</code> does nothing (idempotent).</p>
                </div>

                <div class="example">
                    <h5>Example 2: Start Multiple Services at Once</h5>
                    <p><strong>Scenario:</strong> Dave starts the entire web stack after server maintenance.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start nginx webapp worker</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">(no output = success)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Three services started simultaneously. systemd handles parallel startup with dependency ordering. No output means all three started without errors.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Start a Socket-Activated Service</h5>
                    <p><strong>Scenario:</strong> Alice starts a socket-activated service manually to warm it up before traffic arrives.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start nginx.socket && systemctl status nginx.socket</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.socket — Nginx Proxy Socket
     Active: active (listening) since Fri 2026-06-06 08:00:00 UTC
     Listen: [::]:80 (Stream), [::]:443 (Stream)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The socket is listening on ports 80 and 443. When a connection arrives, Nginx will be auto-started via socket activation. This saves resources — Nginx only runs when traffic exists.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Start with Timeout Handling</h5>
                    <p><strong>Scenario:</strong> Carol starts a service and wants to verify it's actually running within 10 seconds.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start webapp && for i in $(seq 1 10); do systemctl is-active webapp --quiet && echo "Started after ${i}s" && break || sleep 1; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Started after 3s</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The webapp started after 3 seconds. The loop checks every second and reports the exact startup time. If the service never becomes active within 10 seconds, the loop exits silently — useful for scripts that need startup confirmation.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Start a Timer</h5>
                    <p><strong>Scenario:</strong> Dave activates the database backup timer after setting it up.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl start backup.timer && systemctl list-timers backup.timer</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">NEXT                        LEFT       LAST PASSED  UNIT
Fri 2026-06-07 02:00:00 UTC  17h left   n/a  n/a     backup.timer</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The backup timer is active — next run in 17 hours at 2 AM. Timers need to be started like any other unit. The timer will trigger <code>backup.service</code> at the scheduled time.</p>
                </div>

                <div class="success">
                    <strong>💡 Systemd Pro Tip:</strong> <code>systemctl start</code> is idempotent — safe to run on already-running units. Combine with <code>is-active</code> for verification. Start multiple units simultaneously for efficiency. For socket-activated services, start the <code>.socket</code> unit first.
                </div>
            </article>

            <!-- ==================== systemctl stop ==================== -->
            <article class="api-block" id="systemctl-stop">
                <h3>systemctl stop</h3>
                <div class="api-meta">
                    <span class="method-badge method-delete">STOP</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Stop (deactivate) one or more units — gracefully shut down services</p>
                <div class="api-description">
                    <p><code class="inline">systemctl stop</code> deactivates a running unit. It sends the configured kill signal (SIGTERM by default, configurable via <code>KillSignal=</code> in the unit file). If the service doesn't exit within <code>TimeoutStopSec=</code>, systemd sends SIGKILL.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl stop UNIT...
systemctl stop nginx
systemctl stop webapp worker</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — unit stopped</td></tr><tr><td><code>1</code></td><td>Error — unit not found or already inactive</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Stop a Service for Maintenance</h5>
                    <p><strong>Scenario:</strong> Carol stops Nginx before replacing the binary.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop nginx && systemctl is-active nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">inactive</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx stopped — connections dropped. <code>is-active</code> returns "inactive". For zero-downtime, use <code>reload</code> or graceful restart instead of stop.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Stop All Non-Essential Services</h5>
                    <p><strong>Scenario:</strong> Dave stops webapp and worker before a database migration.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop webapp worker && echo "App stack stopped, ready for migration"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">App stack stopped, ready for migration</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Both services stopped. Nginx is still running (returning 502 to clients). This is the standard pre-migration pattern: stop app, migrate DB, start app.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Stop with Timeout Handling</h5>
                    <p><strong>Scenario:</strong> Alice stops a worker that may take time to finish current jobs.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop worker && echo "Stopped" || (echo "Stop timed out — forcing..."; systemctl kill -s KILL worker)</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Stopped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Worker stopped gracefully within the timeout. If it had exceeded <code>TimeoutStopSec</code> (default 90s), the <code>||</code> branch would force-kill it. Always try graceful stop first.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Stop Before Uninstalling a Service</h5>
                    <p><strong>Scenario:</strong> Carol stops and disables an old service before removing its unit file.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl stop old-service && systemctl disable old-service && rm /etc/systemd/system/old-service.service && systemctl daemon-reload</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Removed /etc/systemd/system/multi-user.target.wants/old-service.service</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Proper uninstall sequence: stop → disable → remove file → daemon-reload. Skipping daemon-reload would leave systemd unaware that the unit was deleted.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Conditional Stop (Only if Running)</h5>
                    <p><strong>Scenario:</strong> Dave's script stops a service only if it's currently active.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-active --quiet nginx && systemctl stop nginx && echo "Nginx was running — stopped" || echo "Nginx was already stopped"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Nginx was running — stopped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>is-active --quiet</code> returns exit code 0 if active, non-zero if not. The <code>&&</code> runs stop only if active. This prevents unnecessary stop attempts in scripts.</p>
                </div>

                <div class="success">
                    <strong>💡 Systemd Pro Tip:</strong> Stop sends SIGTERM first, then SIGKILL after <code>TimeoutStopSec</code>. Use <code>is-active --quiet</code> for conditional stops. Always <code>daemon-reload</code> after removing unit files. Stop accepts multiple units for bulk operations.
                </div>
            </article>

            <!-- ==================== systemctl restart ==================== -->
            <article class="api-block" id="systemctl-restart">
                <h3>systemctl restart</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">RESTART</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Stop and then start one or more units — apply changes with minimal downtime</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl restart UNIT...
systemctl restart nginx
systemctl restart webapp worker</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — unit restarted</td></tr><tr><td><code>1</code></td><td>Error — unit not found or start failed</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Restart After Config Change</h5>
                    <p><strong>Scenario:</strong> Carol restarts Nginx after updating its configuration file.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /etc/nginx/nginx.conf && systemctl restart nginx && systemctl is-active nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx restarted with new config. Connections were briefly dropped. For zero-downtime config changes, use <code>systemctl reload nginx</code> instead — Nginx supports graceful reload.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Restart Multiple Services in Sequence</h5>
                    <p><strong>Scenario:</strong> Dave restarts the entire stack after updating shared libraries.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl restart worker && systemctl restart webapp && systemctl restart nginx && echo "Stack restarted"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Stack restarted</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Sequential restart: worker first, then webapp, then Nginx. Each waits for the previous to finish. This avoids downtime from simultaneous restarts. The order matters — restart the least critical first.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Conditional Restart</h5>
                    <p><strong>Scenario:</strong> Alice restarts a service only if it's currently running.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl is-active --quiet nginx && systemctl restart nginx || echo "Nginx not running — use start instead"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Nginx not running — use start instead</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx wasn't running, so restart wasn't attempted. Use <code>try-restart</code> for this pattern natively: it only restarts if already active.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Restart with Pre-Flight Check</h5>
                    <p><strong>Scenario:</strong> Dave validates the new config before committing to a restart.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nginx -t && echo "Config OK" && systemctl restart nginx || (echo "Config error — NOT restarting" && exit 1)</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">nginx: configuration file /etc/nginx/nginx.conf test is successful
Config OK</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>nginx -t</code> validated the config before restart. If the test fails, the restart is skipped — preventing a broken config from being applied. Always validate before restarting in production.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Restart a Timer After Config Change</h5>
                    <p><strong>Scenario:</strong> Carol changes a timer's schedule and restarts it to apply.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /etc/systemd/system/backup.timer && systemctl daemon-reload && systemctl restart backup.timer && systemctl list-timers backup.timer</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">NEXT                        LEFT    PASSED  UNIT
Fri 2026-06-06 22:00:00 UTC  3h left 2h ago  backup.timer</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Timer schedule updated — next run at 10 PM instead of 2 AM. After editing timer files, always <code>daemon-reload</code> then <code>restart</code> the timer. The timer's previous trigger time still shows in the PASSED column.</p>
                </div>

                <div class="success">
                    <strong>💡 Systemd Pro Tip:</strong> Use <code>restart</code> for full stop+start. Use <code>reload</code> for zero-downtime config changes. Use <code>try-restart</code> to only restart if already running. Always validate configs before production restarts. Restart timers after editing to apply new schedules.
                </div>
            </article>

            <!-- ==================== systemctl reload ==================== -->
            <article class="api-block" id="systemctl-reload">
                <h3>systemctl reload</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">RELOAD</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Reload configuration without restarting — zero-downtime config changes</p>
                <div class="api-description">
                    <p><code class="inline">systemctl reload</code> asks the service to reload its configuration without a full restart. The service must define <code>ExecReload=</code> in its unit file. For Nginx, this sends a HUP signal — workers reload config and gracefully drain old connections.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl reload UNIT...
systemctl reload nginx          # Graceful config reload
systemctl reload nginx webapp   # Multiple units</code></pre>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody><tr><td><code>0</code></td><td>Success — config reloaded</td></tr><tr><td><code>1</code></td><td>Error — service doesn't support reload or reload command failed</td></tr></tbody>
                </table>

                <div class="example">
                    <h5>Example 1: Reload Nginx Config (Zero Downtime)</h5>
                    <p><strong>Scenario:</strong> Carol adds a new server block to Nginx without dropping connections.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">nano /etc/nginx/sites-enabled/webapp.conf && nginx -t && systemctl reload nginx && echo "Reloaded — no connections dropped"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">nginx: configuration file test is successful
Reloaded — no connections dropped</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx reloaded the new config. Existing connections continue on old workers; new connections use the new config. Active connections: 0 dropped. This is the standard production config deployment pattern.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Reload a Service Without Restart Capability</h5>
                    <p><strong>Scenario:</strong> Alice tries reloading a service that doesn't support it.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload worker 2>&1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Job type reload is not applicable for unit worker.service.
# Use 'systemctl restart worker' instead</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The worker service has no <code>ExecReload=</code> directive — reload is not supported. Alice uses <code>restart</code> instead. Not all services support hot-reload; it must be configured in the unit file.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Batch Reload Multiple Services</h5>
                    <p><strong>Scenario:</strong> Dave reloads all services that support it after updating shared certificates.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload nginx && systemctl reload webapp && echo "All services reloaded"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">All services reloaded</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Both Nginx and webapp reloaded their configs. Certificates updated without any restarts or dropped connections. Always prefer reload over restart when changing configs.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Reload vs Restart Comparison</h5>
                    <p><strong>Scenario:</strong> Carol demonstrates the difference to a junior admin.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "=== RELOAD ===" && time systemctl reload nginx && echo "=== RESTART ===" && time systemctl restart nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">=== RELOAD ===
real    0m0.045s
=== RESTART ===
real    0m0.834s</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Reload: 45ms. Restart: 834ms (18× slower). Reload is faster because it doesn't tear down and recreate the process — it just re-reads config. For high-traffic services, reload prevents thundering-herd reconnection storms.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Verify Reload Was Successful</h5>
                    <p><strong>Scenario:</strong> Dave verifies the new config is actually being used after reload.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload nginx && sleep 1 && systemctl status nginx | grep "Main PID" && curl -sI https://webapp.io | head -1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Main PID: 1234 (nginx)
HTTP/2 200</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The PID stayed the same (1234) — proving it was a reload, not a restart. The curl confirms the site is responding with HTTP 200. PID stability after reload is the key indicator: same PID = no restart occurred.</p>
                </div>

                <div class="success">
                    <strong>💡 Systemd Pro Tip:</strong> <code>reload</code> is the preferred way to apply config changes — zero downtime, faster, and no PID change. Only works if <code>ExecReload=</code> is configured. For services without reload support, use <code>restart</code>. Always validate config before reloading.
                </div>
            </article>

            <!-- ==================== systemctl reload-or-restart ==================== -->
            <article class="api-block" id="systemctl-reload-or-restart">
                <h3>systemctl reload-or-restart</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">SMART</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Reload if supported, otherwise restart — the safest config-apply command</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl reload-or-restart UNIT...
systemctl reload-or-restart nginx</code></pre>

                <div class="example">
                    <h5>Example 1: Smart Reload for Any Service</h5>
                    <p><strong>Scenario:</strong> Carol uses reload-or-restart in a script that works with any service.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl reload-or-restart webapp && echo "Config applied (reload or restart)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Config applied (reload or restart)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> If webapp supports reload, it reloaded. If not, it restarted. The script doesn't need to know which services support reload — reload-or-restart handles both cases. This is the safest generic command for config changes.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Apply Config Across Multiple Unknown Services</h5>
                    <p><strong>Scenario:</strong> Dave's deployment script applies config changes to all services without knowing their capabilities.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">for svc in nginx webapp worker; do echo "Applying $svc..."; systemctl reload-or-restart $svc; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Applying nginx... (reloaded)
Applying webapp... (reloaded)
Applying worker... (restarted — no reload support)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Nginx and webapp reloaded (zero downtime). Worker restarted (no reload support). The script handles both cases without if/else logic. This is the recommended pattern for generic deployment scripts.</p>
                </div>
            </article>

            <!-- ==================== systemctl status ==================== -->
            <article class="api-block" id="systemctl-status">
                <h3>systemctl status</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">INSPECT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Show runtime status — the primary diagnostic command for any service</p>
                <div class="api-description">
                    <p><code class="inline">systemctl status</code> displays everything about a unit: loaded/enabled state, active state, PID, memory, CPU, start time, and the last 10 journal log lines. It's always the first command to run when troubleshooting.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl status UNIT...
systemctl status nginx
systemctl status nginx webapp   # Multiple units</code></pre>

                <div class="example">
                    <h5>Example 1: Full Status of Running Service</h5>
                    <p><strong>Scenario:</strong> Carol checks Nginx status after a deployment.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.service — Nginx Reverse Proxy
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled)
     Active: active (running) since Fri 2026-06-06 08:00:00 UTC
   Main PID: 1234 (nginx)
      Tasks: 5 (limit: 4915)
     Memory: 45.2M
        CPU: 2.345s
     CGroup: /system.slice/nginx.service</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Active=running, enabled at boot, 45MB memory. The "enabled" means it auto-starts. The dot (●) is green for active, white for inactive, red for failed — color-coded at a glance.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Status of Failed Service with Logs</h5>
                    <p><strong>Scenario:</strong> Alice investigates why the worker service failed.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status worker</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● worker.service — Background Worker
     Loaded: loaded (/etc/systemd/system/worker.service; enabled)
     Active: failed (Result: exit-code) since Fri 2026-06-06 08:05:00 UTC
    Process: 5678 ExecStart=/opt/anihpj/bin/worker (code=exited, status=1/FAILURE)
   Main PID: 5678 (code=exited, status=1/FAILURE)

Jun 06 08:05:00 prod-worker-01 worker[5678]: ERROR: Cannot connect to database at 10.0.1.50:5432
Jun 06 08:05:00 prod-worker-01 worker[5678]: FATAL: Database connection refused</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Worker failed with exit code 1. The last 10 journal lines show the root cause: database connection refused at 10.0.1.50:5432. Status output gives you the error AND the logs in one view — no need to run journalctl separately for initial diagnosis.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Check Status Across Multiple Services</h5>
                    <p><strong>Scenario:</strong> Dave checks the entire stack status in one command.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl status nginx webapp worker</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">● nginx.service — Nginx Reverse Proxy — active (running)
● webapp.service — Web Application — active (running)
● worker.service — Background Worker — active (running)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All three services are active and running. Status accepts multiple units — great for quick stack health checks. Any failed service would show a red dot instead of green.</p>
                </div>
            </article>

            <!-- systemctl enable/disable -->
            <article class="api-block" id="systemctl-enable">
                <h3>systemctl enable / disable</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">BOOT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Enable services to auto-start at boot, or disable automatic startup</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl enable UNIT...
systemctl disable UNIT...
systemctl enable --now UNIT...    # Enable AND start immediately
systemctl disable --now UNIT...   # Disable AND stop immediately</code></pre>

                <div class="example">
                    <h5>Example 1: Enable Nginx to Survive Reboots</h5>
                    <p><strong>Scenario:</strong> Carol ensures Nginx auto-starts after server reboot.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable nginx && systemctl is-enabled nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /etc/systemd/system/nginx.service.
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Symlink created in <code>multi-user.target.wants/</code>. When the system reaches multi-user.target during boot, systemd starts all services linked here. This is how "enable" works internally — it's just a symlink.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Enable and Start in One Command</h5>
                    <p><strong>Scenario:</strong> Dave deploys a new service and wants it running immediately AND at boot.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl enable --now webapp && systemctl is-active webapp && systemctl is-enabled webapp</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active
enabled</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>--now</code> combines enable + start into one atomic operation. The service is running AND configured for auto-start. Without <code>--now</code>, you'd need two separate commands.</p>
                </div>
            </article>

            <!-- systemctl list-units -->
            <article class="api-block" id="systemctl-list">
                <h3>systemctl list-units</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">AUDIT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">List loaded units with state — see everything systemd is tracking</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl list-units [PATTERN...]
systemctl list-units --type=service --state=running
systemctl list-units --all             # Include inactive
systemctl list-units 'nginx*'          # Pattern match</code></pre>

                <div class="example">
                    <h5>Example 1: Show Only Running Services</h5>
                    <p><strong>Scenario:</strong> Alice checks what's actually running right now.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --type=service --state=running</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">UNIT           LOAD   ACTIVE SUB     DESCRIPTION
nginx.service  loaded active running Nginx Reverse Proxy
webapp.service loaded active running Web Application
worker.service loaded active running Background Worker</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Three services running. Filtering by type=service and state=running gives a clean view. Without filters, you'd see devices, mounts, sockets, timers, etc. — hundreds of units.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Find Failed Units</h5>
                    <p><strong>Scenario:</strong> Dave checks for any failed units after a system update.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl list-units --state=failed</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">0 loaded units listed.</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Zero failed units — system is healthy. This is the first post-update check. Any failed unit would show here with its description and failure reason.</p>
                </div>
            </article>

            <!-- systemctl daemon-reload -->
            <article class="api-block" id="systemctl-daemon-reload">
                <h3>systemctl daemon-reload</h3>
                <div class="api-meta">
                    <span class="method-badge method-post">REFRESH</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Reload systemd configuration — required after any unit file change</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl daemon-reload</code></pre>

                <div class="example">
                    <h5>Example 1: Standard Unit File Workflow</h5>
                    <p><strong>Scenario:</strong> Carol deploys a new service unit file.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">cp webapp.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now webapp && echo "Service deployed"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Service deployed</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Copy file → daemon-reload → enable → start. Skipping daemon-reload is the #1 cause of "unit file not found" errors. systemd doesn't watch the filesystem — it must be explicitly told to reload.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Modify and Reload</h5>
                    <p><strong>Scenario:</strong> Alice edits an existing unit file and applies changes.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">sed -i 's/MemoryMax=1G/MemoryMax=2G/' /etc/systemd/system/webapp.service && systemctl daemon-reload && systemctl restart webapp</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">(no output = success)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Memory limit increased from 1G to 2G. daemon-reload makes systemd aware of the change, then restart applies it. Without daemon-reload, systemd would still use the old (cached) unit definition.</p>
                </div>
            </article>

            <!-- systemctl show/cat/edit -->
            <article class="api-block" id="systemctl-show">
                <h3>systemctl show / cat / edit</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">INSPECT</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Inspect and modify unit configuration</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl show UNIT              # All properties (key=value)
systemctl show UNIT -p ExecStart  # Specific property
systemctl cat UNIT                # Show unit file + drop-in overrides
systemctl edit UNIT               # Create/edit drop-in override</code></pre>

                <div class="example">
                    <h5>Example 1: Inspect a Single Property</h5>
                    <p><strong>Scenario:</strong> Carol checks the exact command used to start Nginx.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl show nginx -p ExecStart</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">ExecStart={ path=/usr/sbin/nginx ; argv[]=/usr/sbin/nginx -c /etc/nginx/nginx.conf ; ignore_errors=no ... }</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The exact path and arguments for Nginx startup. <code>-p</code> extracts one property from the hundreds that <code>show</code> returns. Use <code>systemctl show nginx</code> (no -p) to see all 200+ properties.</p>
                </div>

                <div class="example">
                    <h5>Example 2: View Unit File and Overrides</h5>
                    <p><strong>Scenario:</strong> Dave checks if a service has any drop-in overrides applied.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl cat nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"># /etc/systemd/system/nginx.service
[Unit]
Description=Nginx Reverse Proxy
After=network.target
[Service]
ExecStart=/usr/sbin/nginx
Restart=on-failure

# /etc/systemd/system/nginx.service.d/override.conf
[Service]
MemoryMax=512M
LimitNOFILE=65536</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The base unit file AND the override are shown together. The override increases MemoryMax and file descriptors without modifying the original unit file. Drop-in overrides in <code>UNIT.service.d/</code> take priority over the base unit.</p>
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
                    <h5>Example 1: Mask a Conflicting Service</h5>
                    <p><strong>Scenario:</strong> Carol prevents Apache from starting because Nginx handles port 80.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl mask apache2 && systemctl start apache2 2>&1</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Failed to start apache2.service: Unit apache2.service is masked.</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Apache is masked — even manual start is blocked. The unit file is symlinked to <code>/dev/null</code>. This is stronger than <code>disable</code> (which only prevents auto-start). Use mask for services that must NEVER run.</p>
                </div>
            </article>

            <!-- systemctl kill -->
            <article class="api-block" id="systemctl-kill">
                <h3>systemctl kill</h3>
                <div class="api-meta">
                    <span class="method-badge method-delete">SIGNAL</span>
                    <span class="tag">systemctl</span>
                </div>
                <p class="api-subtitle">Send a signal to one or more processes of a unit</p>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">systemctl kill UNIT...
systemctl kill -s HUP nginx         # Reload signal
systemctl kill -s TERM worker       # Graceful termination
systemctl kill -s KILL worker       # Force kill (last resort)</code></pre>

                <div class="example">
                    <h5>Example 1: Send HUP for Graceful Reload</h5>
                    <p><strong>Scenario:</strong> Carol sends a HUP signal to Nginx for gracefulel reload (same as <code>systemctl reload nginx</code>).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">systemctl kill -s HUP nginx && systemctl is-active nginx</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">active</div>
                    <p class="output-note"><strong>📝 What happened:</strong> HUP signal caused Nginx to reload config — same effect as <code>systemctl reload</code>. The process stays running with the same PID. Common signals: HUP (1), TERM (15), KILL (9), USR1 (10), USR2 (12).</p>
                </div>
            </article>'''

old = '''        <section class="section" id="systemctl-section">
            <h2>⚙ systemctl — Service Management</h2>
            <div class="section-intro">
                <p><code class="inline">systemctl</code> is the central management tool for controlling the systemd system and service manager. The anihpj team uses it to manage Gunicorn, Celery workers, Nginx, and periodic backup timers.</p>
            </div>
        </section>'''

new = f'''        <section class="section" id="systemctl-section">
            <h2>⚙ systemctl — Service Management</h2>
            <div class="section-intro">
                <p><code class="inline">systemctl</code> is the central management tool for controlling the systemd system and service manager. The anihpj team uses it to manage Nginx (reverse proxy), the webapp service, background workers, and periodic backup timers across production and staging servers.</p>
            </div>
{content}
        </section>'''

c = c.replace(old, new)
print(f'Articles: {c.count("<article class=")}/{c.count("</article>")}')
print(f'Examples: {c.count("class=\"example\"")}')
print(f'Lines: {len(c.split(chr(10)))}')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
