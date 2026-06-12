#!/usr/bin/env python3
"""Add more content from official LFCS documentation domains.

Additions:
1. s23-6: Virtual Filesystems (/proc & /sys) deep-dive — "Manage and configure the virtual file system"
2. s19-5: IPv6 Configuration with netplan & nmcli — "Configure IPv4 and IPv6 networking"
3. Expand exam logistics section with official Killer.sh simulator, validity, digital badge details
"""

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ============================================================
# ADDITION 1: s23-6 Virtual Filesystems (/proc & /sys)
# ============================================================
vfs_section = '''
        <div class="section-block" id="s23-6"><h3>23.6 Virtual Filesystems — /proc & /sys Deep-Dive 🎯</h3>
            <div class="info-box note"><h5>🧠 Why Virtual Filesystems Matter for LFCS</h5><p>The official LFCS domain explicitly tests "<strong>Manage and configure the virtual file system</strong>." This means <code>/proc</code> and <code>/sys</code> — pseudo-filesystems that don't store data on disk but instead expose kernel data structures as files. <strong>/proc</strong> exposes process and kernel information. <strong>/sys</strong> exposes device and driver information. Together they let you read and sometimes WRITE kernel settings — no special tools needed, just <code>cat</code> and <code>echo</code>. Understanding these virtual filesystems is what separates script-kiddies from real sysadmins: when <code>top</code> or <code>lsblk</code> isn't available, you can still get everything you need from <code>/proc</code> and <code>/sys</code>.</p></div>

            <div class="diagram-container"><div class="diagram-title">/proc vs /sys — Two Virtual Filesystems, Two Purposes</div>
<pre>
  ╔══════════════════════════════════════════════════════════════════╗
  ║                         /proc (procfs)                          ║
  ║  PURPOSE: Process and kernel runtime information                ║
  ║  MOUNTED: proc on /proc type proc (rw,nosuid,nodev,noexec)     ║
  ║  KEY DIRS: /proc/PID/ — per-process info                       ║
  ║            /proc/sys/ — kernel parameters (sysctl interface)    ║
  ║            /proc/cpuinfo, /proc/meminfo, /proc/mounts           ║
  ║  CAN WRITE? YES — /proc/sys/ entries are writable (tunables)   ║
  ╚══════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════╗
  ║                         /sys (sysfs)                            ║
  ║  PURPOSE: Device, driver, and kernel subsystem information      ║
  ║  MOUNTED: sysfs on /sys type sysfs (rw,nosuid,nodev,noexec)    ║
  ║  KEY DIRS: /sys/class/ — devices grouped by type               ║
  ║            /sys/block/ — block devices (disks)                  ║
  ║            /sys/devices/ — physical device tree                 ║
  ║            /sys/kernel/ — kernel tuning (newer than /proc/sys)  ║
  ║  CAN WRITE? YES — device power states, driver parameters       ║
  ╚══════════════════════════════════════════════════════════════════╝</pre></div>

            <table class="compare-table"><thead><tr><th>Virtual File</th><th>What It Shows</th><th>Practical Use</th><th>Anihpj Example</th></tr></thead><tbody>
                <tr><td><code>/proc/cpuinfo</code></td><td>CPU model, cores, flags, MHz</td><td>Verify hardware before installing</td><td><code>grep -c processor /proc/cpuinfo</code> → number of CPU cores</td></tr>
                <tr><td><code>/proc/meminfo</code></td><td>Total RAM, free, buffers, swap</td><td>Memory sizing for DB, web server</td><td><code>grep MemTotal /proc/meminfo</code> → plan PostgreSQL shared_buffers</td></tr>
                <tr><td><code>/proc/mounts</code></td><td>All currently mounted filesystems</td><td>Check if mount succeeded</td><td><code>grep /var/www /proc/mounts</code> → verify anihpj data mount</td></tr>
                <tr><td><code>/proc/partitions</code></td><td>All block devices with major/minor</td><td>See what disks kernel detects</td><td>Check if new disk is visible before partitioning</td></tr>
                <tr><td><code>/proc/filesystems</code></td><td>Filesystems the kernel supports</td><td>See if xfs/btrfs is compiled in</td><td>Verify kernel supports your chosen FS</td></tr>
                <tr><td><code>/proc/sys/vm/swappiness</code></td><td>Swap tendency (0-100)</td><td>Read/Write kernel tunable</td><td><code>echo 10 > /proc/sys/vm/swappiness</code> — tune for DB server</td></tr>
                <tr><td><code>/proc/sys/net/ipv4/ip_forward</code></td><td>IP forwarding (0=off, 1=on)</td><td>Enable routing/NAT</td><td>Enable for container networking</td></tr>
                <tr><td><code>/sys/class/net/eth0/speed</code></td><td>Link speed (1000=1Gbps)</td><td>Verify NIC speed negotiated</td><td>Check if server is on 1Gbps or 100Mbps</td></tr>
                <tr><td><code>/sys/block/sda/queue/scheduler</code></td><td>I/O scheduler (mq-deadline, none)</td><td>Tune for SSD vs HDD</td><td><code>echo none > /sys/block/sda/queue/scheduler</code> for NVMe SSD</td></tr>
                <tr><td><code>/sys/block/sda/size</code></td><td>Disk size in 512-byte sectors</td><td>Verify disk size detected</td><td>Multiply by 512 to get bytes</td></tr>
            </tbody></table>

            <div class="split-panel">
                <div class="split-side split-good"><h5>✅ /proc — Process Internals Exposed</h5><pre><code># Every PID has a directory in /proc:
ls /proc/$$/    # $$ = current shell's PID

# Key per-process files:
/proc/PID/cmdline    # Exact command that started it
/proc/PID/environ    # Environment variables (null-separated)
/proc/PID/cwd        # Symlink to current working dir
/proc/PID/fd/        # All open file descriptors
/proc/PID/maps        # Memory map (loaded libraries)
/proc/PID/limits      # Resource limits (ulimit values)
/proc/PID/status      # Human-readable process state

# Find what file a process has open:
ls -la /proc/$(pgrep nginx | head -1)/fd/
# 0 -> /dev/null, 3 -> /var/log/nginx/access.log

# Recover a deleted but still-open file:
cp /proc/PID/fd/3 /tmp/recovered.log</code></pre></div>
                <div class="split-side split-good"><h5>✅ /sys — Devices & Drivers Exposed</h5><pre><code># Network interface info:
cat /sys/class/net/eth0/address    # MAC address
cat /sys/class/net/eth0/mtu        # MTU size
cat /sys/class/net/eth0/operstate  # up or down

# Disk/block device info:
ls /sys/block/                     # All block devices
cat /sys/block/sda/removable       # 0=fixed, 1=removable
cat /sys/block/sda/queue/rotational  # 0=SSD, 1=HDD

# Power management:
cat /sys/power/state               # Supported sleep states

# Kernel parameters (sysctl alternative):
cat /proc/sys/net/ipv4/ip_forward
# Writing to /proc/sys is equivalent to sysctl -w:
echo 1 > /proc/sys/net/ipv4/ip_forward
# Same as: sysctl -w net.ipv4.ip_forward=1</code></pre></div>
            </div>

            <div class="info-box tip"><h5>💡 The LFCS Virtual FS Trick — When Tools Fail, Go to /proc</h5><p>On the LFCS exam, you might find yourself in a minimal recovery environment where <code>top</code>, <code>free</code>, <code>lscpu</code> aren't available. Everything you need is in <code>/proc</code>: <code>cat /proc/cpuinfo</code> (CPU), <code>cat /proc/meminfo</code> (RAM), <code>cat /proc/partitions</code> (disks), <code>cat /proc/mounts</code> (what's mounted). This knowledge can save you when standard tools are missing. <strong>Exam scenario:</strong> You boot into emergency mode and need to fix <code>/etc/fstab</code>. <code>mount</code> doesn't work? <code>cat /proc/mounts</code> shows what's actually mounted. <code>lsblk</code> missing? <code>cat /proc/partitions</code> shows all disks.</p></div>

            <div class="info-box danger"><h5>⚠️ Writing to /proc and /sys — Immediate, But NOT Persistent</h5><p>Changes made by writing to <code>/proc/sys/</code> or <code>/sys/</code> take effect IMMEDIATELY but are lost on reboot. <strong>For persistence:</strong> <code>/proc/sys/</code> values → add to <code>/etc/sysctl.conf</code> or <code>/etc/sysctl.d/*.conf</code>. <code>/sys/</code> values → add to <code>/etc/rc.local</code>, a systemd service, or udev rules. <strong>LFCS exam tip:</strong> If the task says "set kernel parameter X" without mentioning persistence, <code>sysctl -w</code> or <code>echo > /proc/sys/</code> is fine. If it says "persistently" or "permanent," you MUST add it to <code>/etc/sysctl.conf</code> or <code>/etc/sysctl.d/</code>.</p></div>
        </div>'''

# Insert s23-6 before Ch23 visual summary or before exam questions
ch23_vs_marker = '        <div class="visual-summary"><h4>📊 Chapter 23 Visual Summary</h4><div class="vs-grid">\n'
if ch23_vs_marker in content and 'id="s23-6"' not in content:
    content = content.replace(ch23_vs_marker, vfs_section + '\n' + ch23_vs_marker)
    changes += 1
    print("  ✅ Added s23-6: Virtual Filesystems (/proc & /sys) to Chapter 23")

# Add sidebar entry for s23-6
s23_sidebar_marker = '                            <li><a href="#s23-5">23.5 Checking & Repairing Filesystems</a></li>\n'
s23_sidebar_new = '                            <li><a href="#s23-5">23.5 Checking & Repairing</a></li>\n                            <li><a href="#s23-6">23.6 /proc & /sys Virtual FS</a></li>\n'
if s23_sidebar_marker in content and s23_sidebar_new not in content:
    content = content.replace(s23_sidebar_marker, s23_sidebar_new)
    changes += 1
    print("  ✅ Added s23-6 sidebar entry")

# ============================================================
# ADDITION 2: s19-5 IPv6 Configuration with netplan & nmcli
# ============================================================
ipv6_section = '''
        <div class="section-block" id="s19-5"><h3>19.5 IPv6 Configuration — netplan & nmcli 🎯</h3>
            <div class="info-box note"><h5>🧠 Why IPv6 Configuration Matters for LFCS</h5><p>The official LFCS domain requires you to "<strong>Configure IPv4 and IPv6 networking and hostname resolution</strong>." While IPv4 is familiar, IPv6 is increasingly tested. You need to know how to configure IPv6 addresses via <strong>netplan</strong> (Ubuntu) and <strong>nmcli</strong> (Rocky/RHEL), understand IPv6 address types (global unicast, link-local, unique local), and verify connectivity. For <strong>anihpj</strong>, dual-stack (IPv4 + IPv6) ensures the site is accessible from IPv6-only networks — increasingly common with mobile carriers and ISPs in Asia.</p></div>

            <div class="diagram-container"><div class="diagram-title">IPv6 Address Types — Quick Reference</div>
<pre>
  TYPE              PREFIX        EXAMPLE                        SCOPE
  ───────────────── ────────────  ─────────────────────────────  ────────────
  Global Unicast    2000::/3      2001:db8:1234:5678::1          Internet-routable
  Unique Local      fc00::/7      fd12:3456:789a::1              Private (like 10.0.0.0/8)
  Link-Local        fe80::/10     fe80::a00:27ff:fe4e:66a1       Single link only
  Loopback          ::1/128       ::1                            Local host only
  Multicast         ff00::/8      ff02::1                        All nodes on link</pre></div>

            <div class="split-panel">
                <div class="split-side split-good"><h5>✅ Netplan — IPv6 on Ubuntu (anihpj server)</h5><pre><code># /etc/netplan/01-netcfg.yaml — Dual-stack (IPv4 + IPv6)
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      # IPv4 (static)
      addresses:
        - 192.168.1.100/24
      # IPv6 (static global unicast)
      addresses:
        - 2001:db8:1234:5678::100/64
      routes:
        - to: default
          via: 192.168.1.1
        - to: default
          via: 2001:db8:1234:5678::1
      nameservers:
        addresses:
          - 8.8.8.8
          - 2001:4860:4860::8888   # Google DNS IPv6

# OR: IPv6 via SLAAC (auto-config):
    eth0:
      dhcp4: yes
      accept-ra: yes   # Accept Router Advertisements
      # IPv6 auto-configured from router

# Apply: sudo netplan apply
# Verify: ip -6 addr show eth0</code></pre></div>
                <div class="split-side split-good"><h5>✅ nmcli — IPv6 on Rocky/RHEL</h5><pre><code># Show current IPv6 config:
nmcli connection show eth0

# Add static IPv6 address:
nmcli connection modify eth0 \\
  ipv6.addresses "2001:db8:1234:5678::100/64"
nmcli connection modify eth0 \\
  ipv6.gateway "2001:db8:1234:5678::1"
nmcli connection modify eth0 \\
  ipv6.dns "2001:4860:4860::8888"
nmcli connection modify eth0 \\
  ipv6.method manual

# Enable SLAAC (auto-config):
nmcli connection modify eth0 \\
  ipv6.method auto

# Apply and verify:
nmcli connection down eth0 && \\
nmcli connection up eth0
ip -6 addr show eth0
ping6 2001:4860:4860::8888</code></pre></div>
            </div>

            <table class="compare-table"><thead><tr><th>Command</th><th>What It Shows/Does</th><th>IPv4 Equivalent</th></tr></thead><tbody>
                <tr><td><code>ip -6 addr show</code></td><td>Show IPv6 addresses</td><td><code>ip addr show</code></td></tr>
                <tr><td><code>ip -6 route show</code></td><td>Show IPv6 routing table</td><td><code>ip route show</code></td></tr>
                <tr><td><code>ping6 google.com</code></td><td>Ping via IPv6</td><td><code>ping google.com</code></td></tr>
                <tr><td><code>ss -6 -tln</code></td><td>Show IPv6 listening TCP ports</td><td><code>ss -4 -tln</code></td></tr>
                <tr><td><code>tracepath6 google.com</code></td><td>Trace IPv6 route</td><td><code>tracepath google.com</code></td></tr>
                <tr><td><code>curl -6 https://anihpj.com</code></td><td>Force IPv6 connection</td><td><code>curl -4 https://anihpj.com</code></td></tr>
                <tr><td><code>nft add rule inet filter input ip6 saddr ...</code></td><td>Firewall rule for IPv6</td><td><code>nft ... ip saddr ...</code></td></tr>
                <tr><td><code>dig AAAA anihpj.com</code></td><td>Query IPv6 DNS record</td><td><code>dig A anihpj.com</code></td></tr>
            </tbody></table>

            <div class="info-box tip"><h5>💡 IPv6 on the LFCS Exam — What You Must Know</h5><p>(1) <strong>Address format:</strong> 8 groups of 4 hex digits, shorthand with <code>::</code> (once only). (2) <strong>Link-local:</strong> Every interface auto-configures <code>fe80::/10</code> — used for neighbor discovery (like ARP in IPv4). (3) <strong>Loopback</strong> is <code>::1</code> (not 127.0.0.1). (4) <strong>Listening services:</strong> <code>ss -6 -tln</code> shows what's listening on IPv6. Nginx needs <code>listen [::]:443 ssl</code> to accept IPv6. (5) <strong>Firewall:</strong> IPv6 has its own rules — if you block IPv4 but leave IPv6 open, you're exposed. Always configure both. (6) <strong>Disabling IPv6:</strong> <code>sysctl -w net.ipv6.conf.all.disable_ipv6=1</code> (temporary) or add to <code>/etc/sysctl.conf</code> (persistent). <strong>For anihpj:</strong> If your hosting provider doesn't support IPv6, disable it to avoid timeout issues when applications try IPv6 first.</p></div>
        </div>'''

# Insert s19-5 before Ch19 visual summary
ch19_vs_marker = '        <div class="visual-summary"><h4>📊 Chapter 19 Visual Summary</h4><div class="vs-grid">\n'
if ch19_vs_marker in content and 'id="s19-5"' not in content:
    content = content.replace(ch19_vs_marker, ipv6_section + '\n' + ch19_vs_marker)
    changes += 1
    print("  ✅ Added s19-5: IPv6 Configuration to Chapter 19")

# Add sidebar entry for s19-5
s19_sidebar_marker = '                            <li><a href="#s19-4">19.4 Network Troubleshooting</a></li>\n'
s19_sidebar_new = '                            <li><a href="#s19-4">19.4 Network Troubleshooting</a></li>\n                            <li><a href="#s19-5">19.5 IPv6 Configuration</a></li>\n'
if s19_sidebar_marker in content and s19_sidebar_new not in content:
    content = content.replace(s19_sidebar_marker, s19_sidebar_new)
    changes += 1
    print("  ✅ Added s19-5 sidebar entry")

# ============================================================
# ADDITION 3: Expand Exam Logistics with Official Details
# ============================================================
exam_logistics_new = '''
        <div class="section-block" id="exam-logistics-official"><h3>📋 Official LFCS Exam Logistics — What the Linux Foundation Provides</h3>
            <div class="info-box note"><h5>🧠 Know Your Exam Package</h5><p>When you register for the LFCS exam ($445 USD or bundled options), here's exactly what you get — straight from the official Linux Foundation certification page. Understanding these details helps you plan your study timeline and make the most of your investment.</p></div>

            <table class="compare-table"><thead><tr><th>Item</th><th>Details</th><th>Why It Matters</th></tr></thead><tbody>
                <tr><td><strong>⏰ Exam Eligibility</strong></td><td>12 months from purchase to schedule AND take the exam</td><td>You have a full year. Don't rush — but don't wait until month 11 either.</td></tr>
                <tr><td><strong>🔄 Retake Policy</strong></td><td>1 free retake included with registration</td><td>If you fail the first attempt, you get a second chance at no extra cost. This removes the pressure — you can take the exam when you're "mostly ready" and still have a safety net.</td></tr>
                <tr><td><strong>📅 Certification Validity</strong></td><td>2 years from passing date</td><td>After 2 years, you must recertify. Plan your career path accordingly — LFCS → CKA → CKS is a natural progression within 2-year windows.</td></tr>
                <tr><td><strong>🏆 Digital Badge</strong></td><td>PDF certificate + digital badge (Credly)</td><td>Share on LinkedIn, add to email signature. The digital badge is verifiable — employers can click to confirm your certification is real.</td></tr>
                <tr><td><strong>🖥️ Exam Simulator</strong></td><td>Killer.sh — 2 simulation attempts, 36 hours of access each</td><td><strong>THIS IS THE MOST VALUABLE PART.</strong> The simulator is the EXACT exam environment. 20-25 practice questions that test the same domains. Use attempt #1 at week 4 (diagnostic), attempt #2 at week 7 (final preparation). The simulator grades your answers so you know your weak spots.</td></tr>
                <tr><td><strong>📝 Exam Format</strong></td><td>Performance-based, hands-on CLI tasks (NO multiple choice)</td><td>You perform real tasks in a live Linux terminal. No guessing — you either make the system do what the task asks or you don't get points.</td></tr>
                <tr><td><strong>💻 Exam Environment</strong></td><td>Distribution-independent — you choose Ubuntu or Rocky/Alma</td><td>Use the distro you practiced on. All essential tools are pre-installed. The exam tests concepts, not distro-specific trivia.</td></tr>
                <tr><td><strong>📋 Tasks</strong></td><td>~24 performance-based tasks in 2 hours</td><td>That's ~5 minutes per task. Some tasks take 1 minute, others 10. Flag difficult tasks and return to them later — partial credit may not apply, so prioritize tasks you can complete fully.</td></tr>
            </tbody></table>

            <div class="diagram-container"><div class="diagram-title">Your 12-Month LFCS Timeline — Strategic Planning</div>
<pre>
  MONTH 1-2:   Foundation (Ch 1-11)
  MONTH 3:     Users/Groups + Permissions (Ch 12-14)
  MONTH 4:     Processes + systemd + Logging (Ch 15-17)
  MONTH 5:     Networking (Ch 18-21) → KILLER.SH ATTEMPT #1
  MONTH 6:     Storage (Ch 22-25)
  MONTH 7:     Services (Ch 26-30) + Security (Ch 31-33)
  MONTH 8:     Monitoring/Tuning/Troubleshooting (Ch 34-38)
               → KILLER.SH ATTEMPT #2
  MONTH 9:     Modern Topics (Ch 39-45)
  MONTH 10-12: Review + Schedule Exam (buffer zone)

  COST BREAKDOWN:
  $445 — Exam only
  $625 — Exam + THRIVE-ONE (all e-learning courses)
  $645 — Exam + LFS207 course (Linux System Admin Essentials)</pre></div>

            <div class="info-box tip"><h5>💡 Killer.sh Simulator Strategy — Maximize Your 2 Attempts</h5><p><strong>Attempt #1 (Week 4-5 of study):</strong> Take it EARLY as a diagnostic. Don't worry about your score — use it to see exactly what the exam environment looks like, how tasks are structured, and where your weak spots are. You get 36 hours of access — spread the 20-25 questions across 2-3 sessions. <strong>Between attempts:</strong> Study the areas where you scored lowest. The simulator shows you the expected solution after grading — STUDY THESE SOLUTIONS. They show exactly what the graders look for. <strong>Attempt #2 (Week 7-8):</strong> Take it 2-3 weeks before your real exam. Simulate real conditions: no phone, no distractions, 2-hour timer. Your score should be significantly higher. If it's not, reschedule your exam — you're not ready. <strong>Note:</strong> The simulator has the SAME 20-25 questions every time — unlike the real exam which draws from a larger pool. The simulator teaches you the FORMAT and EXPECTATIONS, not the actual exam content.</p></div>

            <div class="info-box danger"><h5>⚠️ Common Exam Registration Mistakes</h5><p>(1) <strong>Waiting until month 12:</strong> Schedule at least 3-4 weeks before your eligibility expires — all slots might be booked. (2) <strong>Not checking system requirements:</strong> The online proctored exam requires: Chrome/Chromium browser, webcam, microphone, quiet room with no one else present. Test your setup 1 week before. (3) <strong>Forgetting ID:</strong> You need government-issued photo ID that matches your registration name EXACTLY. (4) <strong>Booked wrong distro:</strong> The exam is now distribution-independent (you choose in the environment), but verify this when scheduling. (5) <strong>Not reading the Candidate Handbook:</strong> Available at docs.linuxfoundation.org — covers ALL policies on rescheduling, cancellations, accommodations, and technical requirements. Read it before exam day.</p></div>
        </div>'''

# Insert after the existing exam strategy section, before the TOC section
exam_strategy_marker = '    <!-- ==================== LFCS EXAM QUICK REFERENCE ==================== -->\n'
if exam_strategy_marker in content and 'id="exam-logistics-official"' not in content:
    content = content.replace(exam_strategy_marker, exam_logistics_new + '\n' + exam_strategy_marker)
    changes += 1
    print("  ✅ Added Official Exam Logistics section before Exam Quick Reference")

# ============================================================
# WRITE OUTPUT
# ============================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 Total changes made: {changes}")
print("Done!")
