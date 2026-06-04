#!/usr/bin/env python3
"""Build System Information section for linux_cli.html"""

filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find insertion point: right before </main> after process-management
# The pattern: process-management's </section> followed by </main>
marker = '        </section>\n    </main>'
pos = content.find(marker)
if pos == -1:
    print("ERROR: marker not found")
    exit(1)

# Build section - does NOT include </main> at end
section = r'''
        <!-- ═══════════════════════════════════════════════════════ -->
        <!-- SYSTEM INFORMATION -->
        <!-- ═══════════════════════════════════════════════════════ -->
        <section class="section" id="system-information">
            <h2>🖥️ System Information</h2>
            <div class="section-intro">
                <p>Commands for inspecting system state: OS version, uptime, memory, disk space, hardware info, kernel modules, and system messages. Essential for troubleshooting, capacity planning, and verifying the <strong>anihpj/jobpost</strong> production environment across all 11 servers.</p>
            </div>

            <!-- ==================== uname ==================== -->
            <article class="api-block" id="uname">
                <h3>uname</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">SYSTEM</span>
                    <span class="tag">System Information</span>
                    <span class="tag">Core</span>
                    <span class="tag">LFCS Domain 4</span>
                </div>
                <p class="api-subtitle">Print system information — kernel, hostname, architecture, and OS</p>
                <div class="api-description">
                    <p><code class="inline">uname</code> displays key system identifiers: kernel name, hostname, kernel release, kernel version, machine hardware name, and operating system. It is the first command to run on an unfamiliar server to understand the environment.</p>
                    <p>For the <strong>anihpj/jobpost</strong> project, <code class="inline">uname</code> is essential for:</p>
                    <ul>
                        <li>Verifying kernel version compatibility before installing Kubernetes components</li>
                        <li>Confirming architecture (x86_64 vs ARM) before pulling Docker images</li>
                        <li>Auditing all 11 servers for consistent kernel versions</li>
                        <li>Documenting the OS baseline in deployment runbooks</li>
                        <li>Troubleshooting kernel-module-dependent features like Cilium eBPF</li>
                    </ul>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">uname [OPTIONS]

# Common patterns:
uname                   # Kernel name (Linux)
uname -a                # All system information
uname -r                # Kernel release
uname -m                # Machine hardware name (x86_64, aarch64)
uname -o                # Operating system</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Flag</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>-a, --all</code></td><td>Print all info: kernel-name nodename kernel-release kernel-version machine processor hardware-platform OS</td></tr>
                        <tr><td><code>-s, --kernel-name</code></td><td>Print kernel name (default: Linux)</td></tr>
                        <tr><td><code>-n, --nodename</code></td><td>Print network node hostname</td></tr>
                        <tr><td><code>-r, --kernel-release</code></td><td>Print kernel release (e.g., 5.15.0-91-generic)</td></tr>
                        <tr><td><code>-v, --kernel-version</code></td><td>Print kernel version (build date string)</td></tr>
                        <tr><td><code>-m, --machine</code></td><td>Print machine hardware name (e.g., x86_64, aarch64)</td></tr>
                        <tr><td><code>-p, --processor</code></td><td>Print processor type or "unknown"</td></tr>
                        <tr><td><code>-i, --hardware-platform</code></td><td>Print hardware platform or "unknown"</td></tr>
                        <tr><td><code>-o, --operating-system</code></td><td>Print operating system (e.g., GNU/Linux)</td></tr>
                    </tbody>
                </table>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>0</code></td><td>Success — system information printed</td></tr>
                        <tr><td><code>1</code></td><td>Error — invalid option</td></tr>
                    </tbody>
                </table>

                <h4>📁 Context: anihpj/jobpost — Server Baseline Audit</h4>
                <div class="info"><strong>Daily Workflow:</strong> Carol runs <code>uname -a</code> on every server to verify consistent kernel versions across the anihpj fleet before deploying kernel-dependent features like Cilium eBPF.</div>

                <pre><code class="language-bash"># Carol audits all 11 servers for kernel consistency:
carol@prod-web-01:~$ uname -a
Linux prod-web-01 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux

carol@prod-api-01:~$ uname -a
Linux prod-api-01 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux</code></pre>

                <pre><code class="language-yaml"># Kernel audit script for Cilium compatibility:
# Cilium requires kernel >= 4.9.17 for basic eBPF, >= 5.10 for full features
# Script: /lpj/scripts/kernel-audit.sh
#   for host in $(cat /lpj/scripts/hosts.txt); do
#     ssh "$host" "echo \$(hostname): \$(uname -r)"
#   done

# Expected output (all 11 servers):
#   prod-web-01: 5.15.0-91-generic  ✅
#   prod-web-02: 5.15.0-91-generic  ✅
#   prod-api-01: 5.15.0-91-generic  ✅</code></pre>

                <h4>Examples</h4>

                <div class="example">
                    <h5>Example 1: Full System Overview</h5>
                    <p><strong>Scenario:</strong> Carol logs into a new staging server and needs a complete picture of the system.</p>
                    <p><strong>📄 Context — Server Onboarding Checklist:</strong></p>
                    <pre><code class="language-yaml"># New server spin-up checklist for anihpj:
# 1. Kernel version → uname -r (must be >= 5.4 for Cilium eBPF)
# 2. Architecture → uname -m (must be x86_64 for our Docker images)
# 3. OS type → uname -o (must be GNU/Linux)
# 4. Hostname → uname -n (should match DNS A record)
# 5. All-in-one → uname -a (paste into onboarding doc)</code></pre>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uname -a</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Linux staging-01 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux</div>
                    <p class="output-note"><strong>📝 What happened:</strong> All key identifiers in one line: OS=Linux, host=staging-01, kernel=5.15.0-91-generic, arch=x86_64. This kernel is fully compatible with Cilium eBPF and all anihpj Docker images. Server is ready for deployment.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Check Kernel Version for Cilium</h5>
                    <p><strong>Scenario:</strong> Alice needs to verify the kernel version before installing a Cilium network policy that requires eBPF features from kernel 5.10+.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uname -r</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">5.15.0-91-generic</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Kernel 5.15.0 is well above the 5.10 minimum for advanced Cilium features. The <code>-generic</code> suffix means it's the standard Ubuntu kernel. No custom kernel build needed — proceed with Cilium network policy deployment.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Verify Architecture for Docker Images</h5>
                    <p><strong>Scenario:</strong> Bob needs to confirm the server is x86_64 before pulling the anihpj Docker image (built for amd64).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "Arch: $(uname -m), OS: $(uname -o)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Arch: x86_64, OS: GNU/Linux</div>
                    <p class="output-note"><strong>📝 What happened:</strong> x86_64 (also called amd64) is the standard 64-bit Intel/AMD architecture. The anihpj Docker images are built for this architecture. If this returned <code>aarch64</code>, we would need ARM-compatible images. The one-liner pattern is great for scripts.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Script-Friendly Kernel + Arch</h5>
                    <p><strong>Scenario:</strong> Carol's deployment script needs to conditionally pull the correct Docker image based on architecture.</p>
                    <p><strong>📄 Context — Multi-Arch Deployment:</strong></p>
                    <pre><code class="language-yaml"># Deployment script: /lpj/scripts/deploy.sh
# Determines which Docker image tag to pull based on architecture:
#   ARCH=$(uname -m)
#   if [ "$ARCH" = "x86_64" ]; then TAG="amd64"
#   elif [ "$ARCH" = "aarch64" ]; then TAG="arm64"
#   else echo "Unsupported architecture: $ARCH"; exit 1; fi
#   docker pull registry.anihpj.internal/jobpost:${TAG}-latest</code></pre>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uname -m</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">x86_64</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The script detects x86_64 and pulls the <code>amd64-latest</code> tag. This pattern makes deployment scripts portable across architectures. The same script works on both Intel servers and ARM-based Raspberry Pi clusters.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Comprehensive One-Liner for Incident Reports</h5>
                    <p><strong>Scenario:</strong> Dave documents the server environment for a post-incident report that requires full system context.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">echo "$(uname -s) $(uname -r) ($(uname -m)) — $(uname -o), host: $(uname -n)"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">Linux 5.15.0-91-generic (x86_64) — GNU/Linux, host: prod-db-01</div>
                    <p class="output-note"><strong>📝 What happened:</strong> A comprehensive one-liner combining five uname flags. This is the standard format for incident reports, runbooks, and system documentation. Copy-paste this into any post-mortem to establish the environment baseline.</p>
                </div>

                <div class="success">
                    <strong>💡 LFCS Exam Tip:</strong> <code>uname -a</code> is a must-know. <code>uname -r</code> for kernel version is the most-used flag. <code>uname -m</code> tells architecture (x86_64 vs aarch64). <code>uname -n</code> is equivalent to <code>hostname</code>. Know the output order of <code>-a</code>: kernel-name nodename kernel-release kernel-version machine processor hardware-platform OS.
                </div>
            </article>

            <!-- ==================== hostname ==================== -->
            <article class="api-block" id="hostname">
                <h3>hostname / hostnamectl</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">IDENTITY</span>
                    <span class="tag">System Information</span>
                    <span class="tag">Core</span>
                    <span class="tag">LFCS Domain 4</span>
                </div>
                <p class="api-subtitle">Show or set the system hostname — identify which server you are on</p>
                <div class="api-description">
                    <p><code class="inline">hostname</code> displays or temporarily sets the system hostname. <code class="inline">hostnamectl</code> (systemd) provides a richer interface for viewing and persistently changing the hostname. In a multi-server anihpj environment with 11 servers, checking the hostname is a critical safety habit before running destructive commands.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">hostname [OPTIONS]
hostnamectl [COMMAND]

# Common patterns:
hostname                        # Show hostname
hostname -f                     # Show FQDN (fully qualified domain name)
hostname -I                     # Show all IP addresses
hostnamectl set-hostname NAME   # Permanently change hostname (systemd)</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Flag</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>-a, --alias</code></td><td>Alias name (if set)</td></tr>
                        <tr><td><code>-d, --domain</code></td><td>DNS domain name</td></tr>
                        <tr><td><code>-f, --fqdn, --long</code></td><td>Fully qualified domain name (FQDN)</td></tr>
                        <tr><td><code>-i, --ip-address</code></td><td>IP address(es) of the host</td></tr>
                        <tr><td><code>-I, --all-ip-addresses</code></td><td>All network addresses (excluding loopback)</td></tr>
                        <tr><td><code>-s, --short</code></td><td>Short hostname (before first dot)</td></tr>
                    </tbody>
                </table>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>0</code></td><td>Success — hostname displayed or set</td></tr>
                        <tr><td><code>1</code></td><td>Error — permission denied or invalid hostname</td></tr>
                    </tbody>
                </table>

                <h4>📁 Context: anihpj/jobpost — Multi-Server Identification</h4>
                <pre><code class="language-bash"># Carol manages 11 servers — checking hostname avoids costly mistakes:
carol@prod-web-01:~$ hostname
prod-web-01

carol@prod-api-01:~$ hostname -f
prod-api-01.anihpj.internal

# anihpj hostname convention: {env}-{role}-{number}.anihpj.internal
#   prod-web-01 = Production, Web server, Instance 1
#   staging-01  = Staging environment, General purpose
#   ci-runner-01 = CI/CD pipeline runner</code></pre>

                <h4>Examples</h4>

                <div class="example">
                    <h5>Example 1: Quick Server Identification</h5>
                    <p><strong>Scenario:</strong> Carol has 3 SSH sessions open and needs to confirm which server each terminal is on before running a restart.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hostname</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">prod-api-01</div>
                    <p class="output-note"><strong>📝 What happened:</strong> This is prod-api-01 — the API server. Carol was about to run <code>systemctl restart gunicorn</code>, which is correct. If it had returned <code>prod-db-01</code>, that command would have been a catastrophic mistake. Always check hostname before destructive commands.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Get Full Domain Name for SSL</h5>
                    <p><strong>Scenario:</strong> Alice needs the FQDN for an SSL certificate CSR (Certificate Signing Request).</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hostname -f</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">prod-web-01.anihpj.internal</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The FQDN includes the domain (<code>.anihpj.internal</code>). This is the exact value needed in SSL certificate CSRs and DNS A records. The <code>.internal</code> TLD is standard for private/internal domains that should not resolve on the public internet.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Get All IP Addresses for Firewall Rules</h5>
                    <p><strong>Scenario:</strong> Carol needs every IP bound to this server for a firewall whitelist update.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hostname -I</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">10.0.1.50 172.17.0.1 192.168.1.100</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Three IPs: primary interface (10.0.1.50), Docker bridge (172.17.0.1), and secondary NIC (192.168.1.100). Loopback (127.0.0.1) is excluded. Use <code>-I</code> (capital i) for all IPs; <code>-i</code> (lowercase) shows only one. Feed directly into firewall rules.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Verify DNS Domain Configuration</h5>
                    <p><strong>Scenario:</strong> Dave needs to verify the DNS domain is correctly set after a network reconfiguration.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hostname -d && echo "DNS domain is configured" || echo "No DNS domain set!"</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">anihpj.internal
DNS domain is configured</div>
                    <p class="output-note"><strong>📝 What happened:</strong> The DNS domain <code>anihpj.internal</code> is correctly set. If this returned empty, DNS resolution for short hostnames would fail. After network changes, always verify the domain is populated — an empty domain is a common post-migration issue.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Rich System Identity with hostnamectl</h5>
                    <p><strong>Scenario:</strong> Carol uses systemd's hostnamectl to see comprehensive system identity for a runbook.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">hostnamectl status</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">   Static hostname: prod-web-01
         Icon name: computer-vm
           Chassis: vm
        Machine ID: a1b2c3d4e5f6...
           Boot ID: f6e5d4c3b2a1...
    Virtualization: kvm
  Operating System: Ubuntu 22.04.3 LTS
            Kernel: Linux 5.15.0-91-generic
      Architecture: x86-64
   Hardware Vendor: QEMU
    Hardware Model: Standard PC (i440FX + PIIX, 1996)</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>hostnamectl</code> shows far more than <code>hostname</code>: OS version, kernel, architecture, virtualization type (KVM), chassis (VM), and hardware model. One command replaces <code>hostname</code> + <code>uname</code> + <code>lsb_release</code> combined. The modern systemd way.</p>
                </div>

                <div class="success">
                    <strong>💡 LFCS Exam Tip:</strong> <code>hostname</code> shows/changes hostname temporarily (lost on reboot). <code>hostnamectl set-hostname</code> changes it permanently (writes <code>/etc/hostname</code>). <code>hostname -f</code> for FQDN. <code>hostname -I</code> (capital i) prints all IPs — useful in scripts. Know <code>hostnamectl</code> for systemd-based systems.
                </div>
            </article>

            <!-- ==================== uptime ==================== -->
            <article class="api-block" id="uptime">
                <h3>uptime</h3>
                <div class="api-meta">
                    <span class="method-badge method-get">STATUS</span>
                    <span class="tag">System Information</span>
                    <span class="tag">LFCS Domain 4</span>
                </div>
                <p class="api-subtitle">Show how long the system has been running — plus load average and user count</p>
                <div class="api-description">
                    <p><code class="inline">uptime</code> displays the current time, how long the system has been up, how many users are logged in, and the load average for the past 1, 5, and 15 minutes. It is the quickest health check — if uptime is low, something recently rebooted; if load is high, something is overloaded.</p>
                </div>

                <h4 class="syntax-header">Syntax</h4>
                <pre><code class="language-bash">uptime [OPTIONS]

# Common patterns:
uptime              # Standard output
uptime -p           # Pretty format (human-readable uptime)
uptime -s           # Since when the system has been up</code></pre>

                <h4>Parameters</h4>
                <table class="param-table">
                    <thead><tr><th>Flag</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>-p, --pretty</code></td><td>Show uptime in pretty format: "up 2 weeks, 3 days, 5 hours"</td></tr>
                        <tr><td><code>-s, --since</code></td><td>Show system up since: "2024-06-01 08:00:00"</td></tr>
                        <tr><td><code>-h, --help</code></td><td>Display help and exit</td></tr>
                    </tbody>
                </table>

                <h4>Return Value</h4>
                <table class="param-table">
                    <thead><tr><th>Exit Code</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>0</code></td><td>Success — uptime displayed</td></tr>
                        <tr><td><code>1</code></td><td>Error — cannot read /proc/uptime</td></tr>
                    </tbody>
                </table>

                <h4>📁 Context: anihpj/jobpost — Uptime Monitoring Across Servers</h4>
                <pre><code class="language-bash"># Carol checks uptime on all production servers after a datacenter event:
carol@prod-web-01:~$ uptime
 14:30:01 up 45 days,  3:22,  2 users,  load average: 0.15, 0.10, 0.08

carol@prod-db-01:~$ uptime
 14:30:05 up 3 min,  1 user,  load average: 0.85, 0.45, 0.20
# ⚠️ prod-db-01 rebooted 3 minutes ago — investigate immediately!</code></pre>

                <h4>Examples</h4>

                <div class="example">
                    <h5>Example 1: Standard Uptime Health Check</h5>
                    <p><strong>Scenario:</strong> Carol's first command after SSH-ing into any server — verifies nothing rebooted unexpectedly overnight.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uptime</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"> 14:30:01 up 45 days, 3:22, 2 users, load average: 0.15, 0.10, 0.08</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Server has been up 45 days — no unexpected reboots. Only 2 users logged in (normal for production). Load averages: 0.15 (1min), 0.10 (5min), 0.08 (15min) — all well below 1.0, indicating the 4-core server is mostly idle. A perfectly healthy production server.</p>
                </div>

                <div class="example">
                    <h5>Example 2: Interpret High Load Average</h5>
                    <p><strong>Scenario:</strong> Alice checks the API server during a traffic spike and sees elevated load numbers.</p>
                    <p><strong>📄 Context — Load Average Interpretation:</strong></p>
                    <pre><code class="language-yaml"># Load average rules of thumb:
#   Load < CPU cores = normal (no queuing)
#   Load = CPU cores = fully utilized (optimal)
#   Load > CPU cores = queue forming (processes waiting)
#   Load > 2× CPU cores = significant overload
#
# This server has 4 CPU cores.
# Expected baseline for prod-api-01: 0.5-1.5 (moderate traffic)</code></pre>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uptime</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output"> 14:35:00 up 45 days, 3:27, 4 users, load average: 5.20, 3.80, 2.10</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Load 5.20 on a 4-core server = processes are queuing. The rising trend (5.20 > 3.80 > 2.10) shows the spike is recent. 4 users suggests multiple team members are investigating. Alice should run <code>top</code> next to identify the CPU-hungry process.</p>
                </div>

                <div class="example">
                    <h5>Example 3: Pretty Uptime for SLA Reports</h5>
                    <p><strong>Scenario:</strong> Dave needs human-readable uptime for the monthly SLA report to stakeholders.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uptime -p</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">up 6 weeks, 3 days, 5 hours, 22 minutes</div>
                    <p class="output-note"><strong>📝 What happened:</strong> <code>-p</code> formats uptime as plain English — perfect for reports, dashboards, and emails to non-technical stakeholders. 6 weeks uptime means approximately 99.95% availability for this server this quarter.</p>
                </div>

                <div class="example">
                    <h5>Example 4: Check Exact Boot Time</h5>
                    <p><strong>Scenario:</strong> Carol suspects an unauthorized reboot during the weekend. She checks when the server last booted.</p>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">uptime -s</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">2024-04-20 08:15:00</div>
                    <p class="output-note"><strong>📝 What happened:</strong> Boot time is April 20 at 08:15 — exactly during the scheduled kernel update maintenance window. No unauthorized reboots. Cross-reference with <code>last reboot</code> to see the full reboot history and confirm this was the only one.</p>
                </div>

                <div class="example">
                    <h5>Example 5: Script Server Reboot Detection Across Fleet</h5>
                    <p><strong>Scenario:</strong> Carol's monitoring script checks uptime on all 11 servers to detect any that recently rebooted (uptime < 24 hours triggers an alert).</p>
                    <p><strong>📄 Context — Uptime Monitoring Script:</strong></p>
                    <pre><code class="language-yaml"># Script: /lpj/scripts/uptime-check.sh
# Runs every hour via cron. Alerts if any server has < 24h uptime.
#   for host in $(cat /lpj/scripts/hosts.txt); do
#     up=$(ssh "$host" "uptime -p")
#     if echo "$up" | grep -qE "minute|hour" && ! echo "$up" | grep -q "day"; then
#       echo "ALERT: $host recently rebooted: $up"
#     fi
#   done</code></pre>
                    <p><strong>Command:</strong></p>
                    <pre><code class="language-bash">for host in prod-web-01 prod-api-01 prod-db-01; do echo -n "$host: "; ssh $host "uptime -p"; done</code></pre>
                    <p><strong>Output:</strong></p>
                    <div class="example-output">prod-web-01: up 45 days, 3 hours, 30 minutes
prod-api-01: up 45 days, 3 hours, 28 minutes
prod-db-01: up 3 minutes</div>
                    <p class="output-note"><strong>📝 What happened:</strong> prod-web-01 and prod-api-01 show 45 days — normal. prod-db-01 shows only 3 minutes — it just rebooted! This triggers an immediate alert: check why the database restarted, verify replication is catching up, ensure no data corruption occurred.</p>
                </div>

                <div class="success">
                    <strong>💡 LFCS Exam Tip:</strong> Load average < CPU cores = normal; Load > CPU cores = overload. Three numbers: 1-min, 5-min, 15-min. Rising 1-min with low 15-min = recent spike. All three high = sustained overload. <code>uptime -s</code> shows boot time; <code>uptime -p</code> for reports. <code>/proc/loadavg</code> contains the raw load data.
                </div>
            </article>

        </section>

    </main>'''

# Insert: replace the marker with our section (which includes its own </section> and </main>)
new_content = content[:pos] + section

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ System Information section added with 3 articles: uname, hostname, uptime")
print(f"   Each article has 5 examples, Return Value table, Context block, 📝 prefix, and LFCS tip")
