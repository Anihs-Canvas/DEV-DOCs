#!/usr/bin/env python3
"""Fill all 4 placeholder sections before Chapter 1 with rich, illustrated content."""

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ============================================================
# SECTION 1: Master Summary & Roadmap
# ============================================================
master_summary = r'''
    <div class="chapter-section" id="master-summary">
        <h2><span class="chapter-badge">📋</span> Master Summary & Roadmap — Your Complete LFCS Learning Journey</h2>

        <div class="intro-callout" style="margin:24px 0;">
            <p>This document is a <strong>complete learning system</strong> — not just a reference. It covers <strong>45 chapters</strong> across 12 Parts, <strong>10 Appendices</strong>, <strong>550+ practice questions</strong>, and everything mapped to the official <strong>5 LFCS exam domains</strong>. By the end, you'll have deployed a real Django production application (<strong>anihpj/jobpost</strong>) on a Linux server from scratch — the exact skills tested on the exam. Below is your bird's-eye view of the entire journey and how to implement every piece.</p>
        </div>

        <!-- DOMAIN WEIGHT CARDS -->
        <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin:24px 0;">
            <div class="info-card" style="border-left:4px solid #22c55e;">
                <div class="card-icon-lg">⚙️</div>
                <h5>Operations Deployment</h5>
                <p style="font-size:2em;font-weight:700;color:#22c55e;">25%</p>
                <p style="font-size:12px;color:#a1a1aa;">Kernel, processes, cron, packages, recovery, VMs, containers, SELinux</p>
            </div>
            <div class="info-card" style="border-left:4px solid #326ce5;">
                <div class="card-icon-lg">🌐</div>
                <h5>Networking</h5>
                <p style="font-size:2em;font-weight:700;color:#60a5fa;">25%</p>
                <p style="font-size:12px;color:#a1a1aa;">IPv4/IPv6, DNS, SSH, firewall, routing, bridges, load balancers</p>
            </div>
            <div class="info-card" style="border-left:4px solid #eab308;">
                <div class="card-icon-lg">💿</div>
                <h5>Storage</h5>
                <p style="font-size:2em;font-weight:700;color:#eab308;">20%</p>
                <p style="font-size:12px;color:#a1a1aa;">LVM, filesystems, NFS, swap, autofs, storage performance</p>
            </div>
            <div class="info-card" style="border-left:4px solid #8b5cf6;">
                <div class="card-icon-lg">⌨️</div>
                <h5>Essential Commands</h5>
                <p style="font-size:2em;font-weight:700;color:#8b5cf6;">20%</p>
                <p style="font-size:12px;color:#a1a1aa;">Git, systemd, monitoring, tuning, SSL, troubleshooting</p>
            </div>
            <div class="info-card" style="border-left:4px solid #ef4444;">
                <div class="card-icon-lg">👥</div>
                <h5>Users & Groups</h5>
                <p style="font-size:2em;font-weight:700;color:#ef4444;">10%</p>
                <p style="font-size:12px;color:#a1a1aa;">Accounts, profiles, limits, ACLs, LDAP</p>
            </div>
        </div>

        <!-- BIG PICTURE DIAGRAM -->
        <div class="diagram-container"><div class="diagram-title">🏗️ The Complete LFCS Architecture — How Everything Connects</div>
<pre>
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ANIHPJ/JOBPOST — FULL STACK                          ║
║                     A Real Django App on Real Linux                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🌐 USER'S BROWSER ──HTTPS──▶ INTERNET ──▶ YOUR LINUX SERVER                ║
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │                         LINUX SERVER                                  │   ║
║  │                                                                       │   ║
║  │  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────────┐   │   ║
║  │  │ UFW     │───▶│ Nginx    │───▶│ Gunicorn │───▶│ PostgreSQL     │   │   ║
║  │  │ :443    │    │ Reverse  │    │ :8000    │    │ :5432          │   │   ║
║  │  │ Filter  │    │ Proxy+LB │    │ Django   │    │ Database       │   │   ║
║  │  └─────────┘    └──────────┘    └──────────┘    └────────────────┘   │   ║
║  │       │              │               │                  │            │   ║
║  │       ▼              ▼               ▼                  ▼            │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐    │   ║
║  │  │                    FILESYSTEM LAYER                          │    │   ║
║  │  │  /var/www/anihpj/    /var/lib/postgresql/    /var/log/       │    │   ║
║  │  │  (LVM Logical Volume on XFS filesystem)                      │    │   ║
║  │  └──────────────────────────────────────────────────────────────┘    │   ║
║  │       │                                                              │   ║
║  │       ▼                                                              │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐    │   ║
║  │  │   SECURITY LAYER: SELinux/AppArmor + ACLs + File Permissions │    │   ║
║  │  │   MONITORING: htop, iostat, journalctl, /proc, /sys          │    │   ║
║  │  │   AUTOMATION: systemd units, cron jobs, bash scripts         │    │   ║
║  │  └──────────────────────────────────────────────────────────────┘    │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝</pre></div>

        <!-- IMPLEMENTATION ROADMAP -->
        <div class="diagram-container"><div class="diagram-title">🗺️ Implementation Roadmap — From Zero to Production</div>
<pre>
  STEP 1: Bare Metal/VPS           STEP 4: Deploy App Code
  ├─ Install Ubuntu/Rocky          ├─ git clone anihpj
  ├─ Partition with LVM            ├─ python venv + deps
  ├─ Format with XFS               ├─ ./manage.py migrate
  └─ Mount + fstab                 └─ collectstatic

  STEP 2: Secure the Server        STEP 5: Wire It Together
  ├─ Create anihpj user (no sudo)  ├─ systemd unit for Gunicorn
  ├─ SSH key-only, no root login   ├─ Nginx reverse proxy config
  ├─ UFW: allow 22,80,443 only     ├─ PostgreSQL auth (pg_hba.conf)
  └─ fail2ban for SSH              └─ SSL via Let's Encrypt

  STEP 3: Install Services         STEP 6: Go Live
  ├─ PostgreSQL 16                 ├─ systemctl start everything
  ├─ Nginx (reverse proxy)         ├─ curl -I https://anihpj.com
  ├─ Gunicorn (WSGI server)        ├─ Monitor: htop, journalctl -f
  └─ Certbot (SSL)                 └─ Backup: pg_dump + tar cron job</pre></div>

        <!-- 12-PART JOURNEY CARDS -->
        <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; margin:24px 0;">
            <div class="info-card"><div class="card-icon-lg">🐧</div><h5>Part 1: Fundamentals (Ch 1-4)</h5><p>Linux history, terminal mastery, FHS, permissions. <strong>~6 hours.</strong> Foundation for everything.</p></div>
            <div class="info-card"><div class="card-icon-lg">⌨️</div><h5>Part 2: Essential Cmds (Ch 5-8)</h5><p>File ops, grep/sed/awk, tar/gzip, apt/dnf. <strong>~7 hours.</strong> Your daily toolkit.</p></div>
            <div class="info-card"><div class="card-icon-lg">📜</div><h5>Part 3: Scripting (Ch 9-11)</h5><p>Advanced regex, bash scripts, anihpj automation. <strong>~6 hours.</strong> Automate everything.</p></div>
            <div class="info-card"><div class="card-icon-lg">👥</div><h5>Part 4: Users (Ch 12-14)</h5><p>useradd, groups, sudo, PAM, password aging. <strong>~4 hours.</strong> Who can do what.</p></div>
            <div class="info-card"><div class="card-icon-lg">⚙️</div><h5>Part 5: Processes (Ch 15-17)</h5><p>ps/top/kill, systemd, journalctl. <strong>~5 hours.</strong> Keep services running.</p></div>
            <div class="info-card"><div class="card-icon-lg">🌐</div><h5>Part 6: Networking (Ch 18-21)</h5><p>TCP/IP, netplan/nmcli, DNS, firewalls. <strong>~6 hours.</strong> Connect everything.</p></div>
            <div class="info-card"><div class="card-icon-lg">💿</div><h5>Part 7: Storage (Ch 22-25)</h5><p>Partitions, ext4/xfs, LVM, NFS, swap. <strong>~5 hours.</strong> Where data lives.</p></div>
            <div class="info-card"><div class="card-icon-lg">🔧</div><h5>Part 8: Services (Ch 26-30)</h5><p>SSH, Nginx, PostgreSQL, anihpj stack. <strong>~6 hours.</strong> Production services.</p></div>
            <div class="info-card"><div class="card-icon-lg">🛡️</div><h5>Part 9: Security (Ch 31-33)</h5><p>SELinux, auditd, fail2ban, OpenSSL. <strong>~5 hours.</strong> Defense in depth.</p></div>
            <div class="info-card"><div class="card-icon-lg">📊</div><h5>Part 10: Monitoring (Ch 34-36)</h5><p>htop/iostat, sysctl tuning, troubleshooting. <strong>~5 hours.</strong> See inside the system.</p></div>
            <div class="info-card"><div class="card-icon-lg">🚀</div><h5>Part 11: Production (Ch 37-38)</h5><p>Cron, systemd timers, full deployment. <strong>~4 hours.</strong> Automate recurring work.</p></div>
            <div class="info-card"><div class="card-icon-lg">🆕</div><h5>Part 12: 2026 Topics (Ch 39-45)</h5><p>libvirt, Podman, bridges, autofs, Git, ACLs/LDAP. <strong>~7 hours.</strong> Latest exam domains.</p></div>
        </div>

        <!-- HOW TO IMPLEMENT -->
        <div class="info-box tip" style="margin:20px 0;">
            <h5>💡 How to Implement This Learning System</h5>
            <p><strong>1. Set up your lab FIRST (Chapter 1, Section 1.8):</strong> VirtualBox/VMware + Ubuntu Server 24.04 VM. Don't skip this — every command is meant to be typed.</p>
            <p><strong>2. Go chapter by chapter in order:</strong> Each chapter builds on the previous. Do NOT skip Parts 1-3 — they're the foundation 80% of exam tasks depend on.</p>
            <p><strong>3. Do ALL practice questions:</strong> 518 questions with full explanations and diagrams. After each chapter, do its 10 questions. Track your score.</p>
            <p><strong>4. Build anihpj alongside:</strong> Chapters 26-30 walk you through deploying a real Django app. By Chapter 38, you'll have a full production server.</p>
            <p><strong>5. Use the appendices as quick reference:</strong> Appendix A (commands), D (config files), F (8-week plan), J (50 extra questions).</p>
            <p><strong>6. Take the Killer.sh simulator:</strong> Attempt #1 at week 4 (diagnostic), Attempt #2 at week 7 (readiness check). The simulator is included with your exam registration.</p>
            <p><strong>7. Review weak areas:</strong> If you score below 7/10 on any chapter's questions, re-read that chapter and re-do the questions after a week.</p>
        </div>
    </div>'''

old_master_summary = '''    <!-- Master Summary & Roadmap -->
    <div class="chapter-section" id="master-summary">
        <h2><span class="chapter-badge">📋</span> Master Summary & Roadmap</h2>
        <div class="content-placeholder">
            <div class="placeholder-icon">🗺️</div>
            <p>Content will be added in the next phase. This section will include: Evolution of Linux, LFCS Exam Domains & Weights (all 5 domains), LFCS vs RHCSA vs LPIC-1 comparison, Complete Topic Checklist, Official Domain Coverage Map, Linux Architecture at a Glance, Linux-Docker-K8s Technology Stack, The Shipping Port Analogy, Full anihpj Request Flow, anihpj Hands-On Project Showcase, Your LFCS Learning Journey (11 Parts), 8-Week Study Plan, and Implementation Guide.</p>
        </div>
    </div>'''

if old_master_summary in content:
    content = content.replace(old_master_summary, master_summary)
    changes += 1
    print("  ✅ Replaced Master Summary placeholder with full content")

# ============================================================
# SECTION 2: LFCS Exam Strategy
# ============================================================
exam_strategy = r'''
    <div class="chapter-section" id="exam-strategy">
        <h2><span class="chapter-badge">🎯</span> LFCS Exam Strategy — How to Execute Perfectly on Exam Day</h2>

        <div class="intro-callout" style="margin:24px 0;">
            <p>The LFCS exam is <strong>performance-based</strong> — you perform real tasks in a live Linux terminal. There are <strong>NO multiple-choice questions</strong>. You either make the system do what the task asks, or you don't get points. <strong>~24 tasks in 2 hours</strong> means ~5 minutes per task. Strategy isn't optional — it's the difference between passing at 66% and failing at 64%.</p>
        </div>

        <!-- FIRST 5 MINUTES -->
        <div class="section-block" id="exam-first-five">
            <h3>⏱️ First 5 Minutes — Your Setup Ritual (CRITICAL)</h3>
            <div class="split-panel">
                <div class="split-side split-good"><h5>✅ DO THIS FIRST — Every Time</h5><pre><code># 1. Set hostname immediately (many tasks need it)
hostnamectl set-hostname anihpj-server

# 2. Verify network connectivity
ping -c 2 8.8.8.8
ip addr show

# 3. Check what OS you''re on
cat /etc/os-release
# Ubuntu? Use apt. Rocky? Use dnf.

# 4. Set your editor (tasks may open vim/nano)
export EDITOR=vim
# OR: export EDITOR=nano

# 5. Create a notes file to track what you''ve done
echo "LFCS Exam Notes — $(date)" > ~/exam-notes.txt
# Log every task number and what you did</code></pre></div>
                <div class="split-side split-bad"><h5>❌ DON''T DO THIS</h5><pre><code># ❌ DON''T skip hostname — many tasks reference it
# ❌ DON''T assume distro — check /etc/os-release
# ❌ DON''T start tasks without setting editor
# ❌ DON''T rely on memory — use the notes file
# ❌ DON''T spend 20 min on a single task
#    Flag it and come back!</code></pre></div>
            </div>
        </div>

        <!-- TIME MANAGEMENT -->
        <div class="section-block" id="exam-time-mgmt">
            <h3>⏰ Time Management — The 3-Pass Strategy</h3>
            <table class="compare-table"><thead><tr><th>Pass</th><th>Time</th><th>What You Do</th><th>Goal</th></tr></thead><tbody>
                <tr><td><strong>Pass 1</strong></td><td>First 10 min</td><td>READ all tasks. Mark difficulty: 🟢 Easy / 🟡 Medium / 🔴 Hard</td><td>Know the battlefield before you fight</td></tr>
                <tr><td><strong>Pass 2</strong></td><td>Next 80 min</td><td>Solve ALL 🟢 tasks first (quick wins), then 🟡, then 🔴. Skip if stuck >5 min.</td><td>Maximize points on what you KNOW</td></tr>
                <tr><td><strong>Pass 3</strong></td><td>Last 30 min</td><td>Return to skipped tasks. Verify ALL completed tasks. Reboot once to test persistence.</td><td>Catch mistakes, get partial credit</td></tr>
            </tbody></table>
        </div>

        <!-- DOMAIN STRATEGIES -->
        <div class="section-block" id="exam-domain-strategies">
            <h3>📋 Domain-by-Domain Strategy</h3>
            <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px;">
                <div class="info-card"><h5>⚙️ Operations (25%)</h5><p><strong>Focus:</strong> systemctl, sysctl -w vs /etc/sysctl.conf, cron syntax, apt/dnf. <strong>Trick:</strong> "persistent" = MUST write to config file. <strong>Verify:</strong> systemctl status, sysctl -p, crontab -l.</p></div>
                <div class="info-card"><h5>🌐 Networking (25%)</h5><p><strong>Focus:</strong> netplan/nmcli, hostnamectl, ufw/firewalld, sshd_config. <strong>Trick:</strong> ALWAYS reload after config change: netplan apply, firewall-cmd --reload. <strong>Verify:</strong> ip addr, ping, ss -tln.</p></div>
                <div class="info-card"><h5>💿 Storage (20%)</h5><p><strong>Focus:</strong> fdisk/gdisk, mkfs, mount, /etc/fstab, lvm (pvcreate→vgcreate→lvcreate). <strong>Trick:</strong> Always test fstab with mount -a BEFORE rebooting. <strong>Verify:</strong> df -h, lsblk, mount | grep.</p></div>
                <div class="info-card"><h5>⌨️ Essential (20%)</h5><p><strong>Focus:</strong> grep/sed/awk, git clone/commit/push, systemd units, journalctl, openssl. <strong>Trick:</strong> man pages are available — use them! <strong>Verify:</strong> grep pattern file, git log, systemctl status.</p></div>
                <div class="info-card"><h5>👥 Users (10%)</h5><p><strong>Focus:</strong> useradd -m -u -G, groupadd, chmod/chown, setfacl. <strong>Trick:</strong> -a in usermod -aG is critical. <strong>Verify:</strong> id username, getent passwd, getfacl.</p></div>
            </div>
        </div>

        <!-- TOP MISTAKES -->
        <div class="info-box danger" style="margin:20px 0;">
            <h5>⚠️ Top 10 Mistakes That Cost Points on the LFCS Exam</h5>
            <ol style="color:#c9d1d9;line-height:2;">
                <li><strong>Not making changes persistent:</strong> If the task says "persistently" or "across reboots," you MUST edit config files (fstab, sysctl.conf, netplan). Runtime commands alone earn 0 points.</li>
                <li><strong>Not verifying your work:</strong> After every task, verify: id user, df -h, systemctl status, ss -tln, mount. A typo in fstab that breaks boot = points lost on ALL storage tasks.</li>
                <li><strong>Using the wrong distro commands:</strong> Check /etc/os-release first. apt on Rocky won't work, dnf on Ubuntu won't work.</li>
                <li><strong>Forgetting to reload:</strong> After editing: netplan (netplan apply), firewalld (firewall-cmd --reload), systemd (systemctl daemon-reload), sshd (systemctl reload sshd).</li>
                <li><strong>Wrong file permissions:</strong> SSH keys MUST be 600 (private) and 644 (public). Wrong perms = SSH refuses to use them.</li>
                <li><strong>Not enabling services:</strong> systemctl enable is separate from systemctl start. Service won't survive reboot without enable.</li>
                <li><strong>fstab syntax errors:</strong> Wrong UUID, missing dump/pass fields, wrong filesystem type. ALWAYS test with mount -a before leaving the task.</li>
                <li><strong>iptables/nftables rules not saved:</strong> iptables rules are lost on reboot unless you save them. Use iptables-save or nft list ruleset > /etc/nftables.conf.</li>
                <li><strong>Ignoring SELinux/AppArmor:</strong> If a service can't access a file despite correct permissions, check: getenforce, aa-status. The exam may have SELinux enforcing.</li>
                <li><strong>Panic-rebooting:</strong> Only reboot at the END (Pass 3) to test persistence. A mid-exam reboot wastes time and you may lose unsaved work.</li>
            </ol>
        </div>

        <!-- EXAM DAY CHECKLIST -->
        <div class="info-box tip" style="margin:20px 0;">
            <h5>✅ Exam Day Checklist</h5>
            <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px;">
                <div class="info-card"><h5>🔧 Before Exam</h5><p>☐ Test webcam & microphone<br>☐ Chrome/Chromium installed<br>☐ Government ID ready<br>☐ Quiet, private room<br>☐ No screens/phones visible<br>☐ Restroom break taken<br>☐ Water bottle (clear)</p></div>
                <div class="info-card"><h5>💻 During Exam</h5><p>☐ First 5 min setup ritual<br>☐ Read all tasks first (Pass 1)<br>☐ Solve easy tasks first (Pass 2)<br>☐ Verify EVERY task<br>☐ Use man pages freely<br>☐ Flag hard tasks, return later</p></div>
                <div class="info-card"><h5>🔄 Before Submit</h5><p>☐ Reboot ONCE (test persistence)<br>☐ Check all services started<br>☐ Verify fstab, netplan survived<br>☐ Review notes file<br>☐ Check for any "TODO" markers<br>☐ Submit with 2 min remaining</p></div>
            </div>
        </div>
    </div>'''

old_exam_strategy = '''    <!-- Exam Strategy -->
    <div class="chapter-section" id="exam-strategy">
        <h2><span class="chapter-badge">🎯</span> LFCS Exam Strategy</h2>
        <div class="content-placeholder">
            <div class="placeholder-icon">🎯</div>
            <p>Content will be added in the next phase. Includes: First 5 Minutes Setup Ritual, Terminal Shortcuts & Aliases, Documentation Bookmarks (man pages), Time Management Strategy, Domain-by-Domain Strategy, Top 10 Mistakes That Cost Points, and Exam Day Checklist.</p>
        </div>
    </div>'''

if old_exam_strategy in content:
    content = content.replace(old_exam_strategy, exam_strategy)
    changes += 1
    print("  ✅ Replaced Exam Strategy placeholder with full content")

# ============================================================
# SECTION 3: New 2026 Topics
# ============================================================
new_topics = r'''
    <div class="chapter-section" id="new-topics-2026">
        <h2><span class="chapter-badge">🆕</span> New 2026 Official Exam Topics — What Changed & How to Prepare</h2>

        <div class="intro-callout" style="margin:24px 0;">
            <p>In 2026, the Linux Foundation updated the LFCS exam domains to include <strong>7 new topic areas</strong> reflecting the modern sysadmin's reality: virtualization, containers, advanced networking, automated storage, performance analysis, version control, and enterprise identity management. These topics appear primarily in <strong>Part 12 (Chapters 39-45)</strong> but concepts are woven throughout the entire document.</p>
        </div>

        <div class="diagram-container"><div class="diagram-title">🆕 7 New LFCS 2026 Topics — Overview Map</div>
<pre>
  ┌─────────────────────────────────────────────────────────────────┐
  │                   NEW 2026 LFCS EXAM TOPICS                     │
  │                                                                  │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
  │  │  libvirt/KVM │  │   Podman     │  │  Bridges, Bonding,   │  │
  │  │  Virtual     │  │  Containers  │  │  Static Routes       │  │
  │  │  Machines    │  │  (daemonless)│  │  (Advanced Network)  │  │
  │  │  Chapter 39  │  │  Chapter 40  │  │  Chapter 41          │  │
  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
  │         │                 │                      │              │
  │         ▼                 ▼                      ▼              │
  │  ┌──────────────────────────────────────────────────────────┐   │
  │  │         Operations Deployment Domain (25%)                │   │
  │  └──────────────────────────────────────────────────────────┘   │
  │                                                                  │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
  │  │   autofs     │  │   Storage    │  │   Git Operations     │  │
  │  │  Automounters│  │   Perf Mon   │  │   for SysAdmins      │  │
  │  │  Chapter 42  │  │  Chapter 43  │  │   Chapter 44         │  │
  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
  │         │                 │                      │              │
  │         ▼                 ▼                      ▼              │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
  │  │  Storage     │  │  Storage     │  │  Essential Commands  │  │
  │  │  Domain      │  │  Domain      │  │  Domain              │  │
  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │
  │                                                                  │
  │  ┌──────────────────────────────────────────────────────────┐   │
  │  │        ACLs Deep-Dive + LDAP Integration                 │   │
  │  │        Chapter 45 — Users & Groups Domain (10%)          │   │
  │  └──────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────┘</pre></div>

        <table class="compare-table"><thead><tr><th>#</th><th>New Topic</th><th>Chapter</th><th>Why It Was Added</th><th>Key Commands to Know</th></tr></thead><tbody>
            <tr><td>1</td><td><strong>Virtual Machines (libvirt/KVM)</strong></td><td>Ch 39</td><td>Linux IS the hypervisor. Every cloud runs on KVM.</td><td><code>virsh list, virt-install, virsh start/stop/destroy, virsh snapshot-create</code></td></tr>
            <tr><td>2</td><td><strong>Container Engines (Podman)</strong></td><td>Ch 40</td><td>Containers are the new unit of deployment. Podman is daemonless (safer than Docker).</td><td><code>podman run, podman build, podman ps, podman stop/rm, podman logs</code></td></tr>
            <tr><td>3</td><td><strong>Bridges, Bonding, Static Routes</strong></td><td>Ch 41</td><td>VMs need bridges. High-availability needs bonding. Complex networks need static routes.</td><td><code>ip link add br0 type bridge, ip link add bond0 type bond, ip route add</code></td></tr>
            <tr><td>4</td><td><strong>Filesystem Automounters (autofs)</strong></td><td>Ch 42</td><td>NFS home dirs shouldn't be mounted 24/7. autofs mounts on demand.</td><td><code>automount, auto.master, auto.home, systemctl restart autofs</code></td></tr>
            <tr><td>5</td><td><strong>Storage Performance Monitoring</strong></td><td>Ch 43</td><td>Disk I/O is the #1 bottleneck for databases. You need to quantify it.</td><td><code>iostat -x 1, iotop, sar -d, fio --name=test</code></td></tr>
            <tr><td>6</td><td><strong>Git Operations for SysAdmins</strong></td><td>Ch 44</td><td>Infrastructure-as-code. /etc in git. Deploy via git pull.</td><td><code>git clone, git add, git commit, git push, git log, git branch</code></td></tr>
            <tr><td>7</td><td><strong>ACLs + LDAP Integration</strong></td><td>Ch 45</td><td>Fine-grained permissions beyond rwx. Enterprise user management via LDAP.</td><td><code>setfacl -m u:alice:rw file, getfacl, sssd, authselect</code></td></tr>
        </tbody></table>

        <div class="info-box tip" style="margin:20px 0;">
            <h5>💡 How These Topics Are Tested</h5>
            <p>The LFCS exam doesn't test these as separate "new topic" sections — they're integrated into existing tasks. For example: a storage task might require LVM <em>and</em> ask you to monitor its performance (Ch 43). A networking task might involve creating a bridge (Ch 41) for a VM (Ch 39). A user task might require ACLs (Ch 45) instead of standard permissions. <strong>The key insight:</strong> these new topics are skills layered ON TOP of the fundamentals in Chapters 1-38. Master the fundamentals first, then layer in these modern tools.</p>
        </div>
    </div>'''

old_new_topics = '''    <!-- New 2026 Topics Overview -->
    <div class="chapter-section" id="new-topics-2026">
        <h2><span class="chapter-badge">🆕</span> New 2026 Official Exam Topics</h2>
        <div class="content-placeholder">
            <div class="placeholder-icon">🆕</div>
            <p>Content will be added in the next phase. Covers all 7 new topics: Virtual Machines (libvirt), Container Engines (Podman/Docker), Advanced Networking (Bridges, Bonding, Static Routes), Filesystem Automounters (autofs), Storage Performance Monitoring, Git Operations for SysAdmins, and ACLs & LDAP Integration.</p>
        </div>
    </div>'''

if old_new_topics in content:
    content = content.replace(old_new_topics, new_topics)
    changes += 1
    print("  ✅ Replaced New 2026 Topics placeholder with full content")

# ============================================================
# SECTION 4: Shipping Port Analogy
# ============================================================
port_analogy = r'''
    <div class="chapter-section" id="port-analogy">
        <h2><span class="chapter-badge">🚢</span> Linux-Docker-Kubernetes: The Shipping Port Analogy</h2>

        <div class="intro-callout" style="margin:24px 0;">
            <p>If you've seen diagrams with ships, containers, cranes, and harbor masters — this is the analogy that makes the entire Linux→Docker→Kubernetes stack <strong>intuitive</strong>. Once you understand this mental model, every Kubernetes concept clicks into place. The <strong>anihpj/jobpost</strong> app is our cargo — let's follow it from development to production.</p>
        </div>

        <!-- THE BIG ANALOGY -->
        <div class="diagram-container"><div class="diagram-title">🚢 The Complete Shipping Port Analogy — Linux → Docker → Kubernetes</div>
<pre>
╔══════════════════════════════════════════════════════════════════════════════╗
║                    THE SHIPPING PORT — FULL ANALOGY                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🏗️ LINUX = THE PORT INFRASTRUCTURE                                        ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │  The physical land, roads, electricity, water, security fences.     │     ║
║  │  Without the port, nothing operates. Linux is the foundation that   │     ║
║  │  Docker and Kubernetes run ON TOP OF.                               │     ║
║  │                                                                      │     ║
║  │  Linux provides: CPU (cargo processing), RAM (staging area),        │     ║
║  │  Disk (warehouses), Network (roads in/out), Security (firewall).    │     ║
║  │                                                                      │     ║
║  │  Anihpj equivalent: Ubuntu Server 24.04, ext4 filesystem, UFW.      │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                    │                                         ║
║                                    ▼                                         ║
║  📦 DOCKER = STANDARDIZED SHIPPING CONTAINERS                               ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │  Before containers: every ship carried different-sized crates,      │     ║
║  │  barrels, and pallets. Loading/unloading was chaos.                  │     ║
║  │                                                                      │     ║
║  │  After standard containers: ONE standard size. Any ship, any crane,  │     ║
║  │  any truck, any port can handle them. Predictable, stackable, safe.  │     ║
║  │                                                                      │     ║
║  │  Docker container = standard shipping container for software.        │     ║
║  │  Inside: anihpj code + Python + Django + all dependencies.          │     ║
║  │  Runs identically on your laptop, a VM, or a K8s cluster.           │     ║
║  │                                                                      │     ║
║  │  Dockerfile = blueprint for building the container.                  │     ║
║  │  Image = the container ready to ship (stored in a registry).         │     ║
║  │  Container = a running instance of the image (on a ship).            │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                    │                                         ║
║                                    ▼                                         ║
║  ☸️ KUBERNETES = THE HARBOR MASTER (Control Plane)                         ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │  A busy port has hundreds of ships arriving/departing. You need:    │     ║
║  │                                                                      │     ║
║  │  📋 HARBOR LOGBOOK (etcd)                                           │     ║
║  │     Records EVERYTHING: which ship is at which dock, which          │     ║
║  │     containers are on which ship, schedules, manifests.              │     ║
║  │     → etcd: distributed key-value store. The single source of truth. │     ║
║  │                                                                      │     ║
║  │  🏢 FRONT DESK (API Server / kube-apiserver)                        │     ║
║  │     All communication goes through the front desk. Ship captains,    │     ║
║  │     dock workers, crane operators — everyone talks to the front      │     ║
║  │     desk, never directly to each other.                              │     ║
║  │     → kube-apiserver: The single entry point for all K8s operations. │     ║
║  │                                                                      │     ║
║  │  🏗️ DOCK MASTER (Scheduler / kube-scheduler)                        │     ║
║  │     A new ship arrives. Which dock has space? Which dock has the     │     ║
║  │     right cranes? The dock master assigns ships to docks.            │     ║
║  │     → kube-scheduler: Assigns Pods to Nodes based on resources.      │     ║
║  │                                                                      │     ║
║  │  🏭 DOCK WORKERS (kubelet on each Node)                              │     ║
║  │     Each dock has workers who load/unload containers, maintain       │     ║
║  │     equipment, and report status to the front desk.                  │     ║
║  │     → kubelet: The agent running on every Node. Starts/stops Pods.   │     ║
║  │                                                                      │     ║
║  │  🚢 CONTAINER SHIP (Pod)                                             │     ║
║  │     A ship carries multiple containers that share the journey.       │     ║
║  │     → Pod: Smallest deployable unit. Contains 1+ containers          │     ║
║  │       sharing network namespace and storage volumes.                 │     ║
║  │                                                                      │     ║
║  │  🏗️ CRANE (kube-proxy)                                              │     ║
║  │     Cranes move containers between ships and docks. They know where  │     ║
║  │     each container needs to go.                                      │     ║
║  │     → kube-proxy: Network rules that route traffic to Pods.          │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝</pre></div>

        <!-- ANIHPJ JOURNEY -->
        <div class="diagram-container"><div class="diagram-title">📦 The Anihpj/JobPost Container Journey — End to End</div>
<pre>
  DEVELOPMENT (Your Laptop)              PRODUCTION (K8s Cluster)
  ┌────────────────────────┐            ┌─────────────────────────────┐
  │  1. Write code          │            │  7. K8s schedules the Pod    │
  │  anihpj/jobpost/models  │            │  Scheduler: "Node 3 has      │
  │                         │            │  2GB RAM free → place there"  │
  │  2. Create Dockerfile   │            │                              │
  │  FROM python:3.12       │            │  8. kubelet pulls image      │
  │  COPY . /app            │            │  kubelet on Node 3:          │
  │  RUN pip install -r     │            │  "podman pull anihpj:latest" │
  │      requirements.txt   │            │                              │
  │                         │            │  9. Container starts         │
  │  3. Build image         │            │  Django runs, connects to    │
  │  docker build -t        │            │  PostgreSQL Service          │
  │      anihpj:latest .    │            │                              │
  │                         │            │  10. Service exposes app     │
  │  4. Test locally        │            │  anihpj-svc (ClusterIP)      │
  │  docker run -p 8000:8000│            │  → Nginx Ingress → Internet  │
  │      anihpj:latest      │            │                              │
  │                         │            │  11. User visits             │
  │  5. Push to registry    │            │  https://anihpj.com          │
  │  docker push registry.  │──────────▶│  → Ingress → Service → Pod   │
  │      anihpj.com/anihpj  │            │  → Django → PostgreSQL       │
  │                         │            │  → HTML Response → User!     │
  │  6. Apply K8s manifests │            │                              │
  │  kubectl apply -f       │            │  12. Scaling (if traffic ↑)  │
  │      deployment.yaml    │            │  kubectl scale deploy/anihpj │
  │                         │            │      --replicas=5            │
  └────────────────────────┘            └─────────────────────────────┘</pre></div>

        <!-- KEY TERMS TABLE -->
        <table class="compare-table"><thead><tr><th>Shipping Concept</th><th>Docker/K8s Concept</th><th>What It Does</th><th>Anihpj Example</th></tr></thead><tbody>
            <tr><td>🏗️ Port Land + Utilities</td><td><strong>Linux OS</strong></td><td>Provides CPU, RAM, disk, network</td><td>Ubuntu Server 24.04 on a VPS</td></tr>
            <tr><td>📦 Standard Container</td><td><strong>Docker Image</strong></td><td>Packaged app with all dependencies</td><td>anihpj:latest image (Python + Django + code)</td></tr>
            <tr><td>📋 Container Manifest</td><td><strong>Dockerfile</strong></td><td>Blueprint for building the image</td><td>FROM python:3.12, COPY, RUN, CMD</td></tr>
            <tr><td>🏪 Container Yard</td><td><strong>Container Registry</strong></td><td>Stores and distributes images</td><td>Docker Hub, GHCR, AWS ECR</td></tr>
            <tr><td>🚢 Ship at Sea</td><td><strong>Pod</strong></td><td>Running instance with 1+ containers</td><td>anihpj Pod (Django + sidecar)</td></tr>
            <tr><td>🏗️ Dock (Berth)</td><td><strong>Node (Worker)</strong></td><td>Physical/virtual machine running Pods</td><td>3 worker nodes in the K8s cluster</td></tr>
            <tr><td>🏢 Harbor Master Office</td><td><strong>Control Plane</strong></td><td>Manages the entire cluster</td><td>API server, scheduler, etcd</td></tr>
            <tr><td>📋 Harbor Logbook</td><td><strong>etcd</strong></td><td>Single source of truth (all cluster state)</td><td>Stores: which Pods exist, on which Nodes</td></tr>
            <tr><td>🏢 Front Desk</td><td><strong>API Server</strong></td><td>All requests go through here</td><td>kubectl → API Server → etcd/Scheduler</td></tr>
            <tr><td>🏗️ Dock Master</td><td><strong>Scheduler</strong></td><td>Assigns ships (Pods) to docks (Nodes)</td><td>"Place anihpj Pod on Node with 2GB free RAM"</td></tr>
            <tr><td>🏭 Dock Worker</td><td><strong>kubelet</strong></td><td>Starts/stops containers, reports health</td><td>Runs on every Node, reports to API Server</td></tr>
            <tr><td>🏗️ Crane</td><td><strong>kube-proxy</strong></td><td>Routes network traffic to correct Pod</td><td>iptables rules: Service IP → Pod IP</td></tr>
            <tr><td>📻 Radio Channel</td><td><strong>Service</strong></td><td>Stable endpoint to reach Pods (they come and go)</td><td>anihpj-svc (ClusterIP 10.96.0.10:8000)</td></tr>
            <tr><td>🚪 Port Gate</td><td><strong>Ingress</strong></td><td>Entry point for external traffic</td><td>Nginx Ingress → anihpj.com → Service → Pod</td></tr>
        </tbody></table>

        <div class="info-box note" style="margin:20px 0;">
            <h5>🧠 Why This Analogy Works</h5>
            <p>Before standardized containers (1950s), shipping was chaos — every item was different sizes, loading took days, theft was rampant. Standard containers revolutionized global trade: any ship, any crane, any port. <strong>Docker did the same for software:</strong> before Docker, deploying to production meant "it works on my machine" nightmares. With Docker, the exact same container runs on your laptop, a VM, or a 1000-node K8s cluster. <strong>Kubernetes</strong> adds the harbor master layer — when you have hundreds of containers, you need automation to schedule them, heal them, scale them, and route traffic. The port runs 24/7 without human intervention — that's the promise of K8s.</p>
        </div>
    </div>'''

# Find the port-analogy placeholder by its closing </div> sequence and the unique text
old_port_start = '    <!-- Shipping Port Analogy -->\n    <div class="chapter-section" id="port-analogy">'
old_port_end = 'With detailed breakdowns of etcd (Harbor Logbook), API Server (Front Desk), Scheduler (Dock Master), kubelet (Dock Worker), Pod (Container Ship), and the full anihpj request journey end-to-end.</p>\n        </div>\n    </div>'

if old_port_start in content and old_port_end in content:
    # Find the full block
    start_idx = content.index(old_port_start)
    end_idx = content.index(old_port_end) + len(old_port_end)
    content = content[:start_idx] + port_analogy + content[end_idx:]
    changes += 1
    print("  ✅ Replaced Shipping Port Analogy placeholder with full content")

# ============================================================
# WRITE OUTPUT
# ============================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 Total changes: {changes}")
print("Done!")
