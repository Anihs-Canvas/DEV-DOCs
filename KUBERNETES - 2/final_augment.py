#!/usr/bin/env python3
"""Final augmentation of the 4 pre-Chapter-1 sections with extra visual polish and depth."""

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ============================================================
# AUGMENT 1: Master Summary — Add Study Time Pie + LFCS vs Other Certs table
# ============================================================
augment1 = r'''
        <!-- STUDY TIME ALLOCATION -->
        <div class="diagram-container" style="margin:24px 0;"><div class="diagram-title">⏱️ Recommended Study Time Allocation — 66 Hours Total</div>
<pre>
  ████████████████████  Part 1: Fundamentals      6h  (9%)   ██
  ████████████████████████  Part 2: Essential Cmds   7h  (11%)  ███
  ████████████████████  Part 3: Scripting          6h  (9%)   ██
  ██████████  Part 4: Users              4h  (6%)   █
  ██████████████  Part 5: Processes         5h  (8%)   ██
  ████████████████████  Part 6: Networking        6h  (9%)   ██
  ██████████████  Part 7: Storage            5h  (8%)   ██
  ████████████████████  Part 8: Services          6h  (9%)   ██
  ██████████████  Part 9: Security           5h  (8%)   ██
  ██████████████  Part 10: Monitoring        5h  (8%)   ██
  ██████████  Part 11: Production        4h  (6%)   █
  ████████████████████  Part 12: 2026 Topics      7h  (11%)  ███

  TOTAL: ~66 hours across 45 chapters. Study 2 hours/day = 33 days.
  Add 2 weeks for review + Killer.sh = 8-week plan (Appendix F).</pre></div>

        <!-- LFCS vs OTHER CERTS -->
        <div class="info-box note" style="margin:24px 0;">
            <h5>🔬 LFCS vs Other Linux Certifications — Why LFCS?</h5>
            <table class="compare-table" style="margin-top:12px;"><thead><tr><th>Feature</th><th>LFCS (Linux Foundation)</th><th>RHCSA (Red Hat)</th><th>LPIC-1 (LPI)</th><th>CompTIA Linux+</th></tr></thead><tbody>
                <tr><td><strong>Vendor Lock-in</strong></td><td class="winner">❌ Distribution-neutral</td><td>⚠️ RHEL-only</td><td class="winner">❌ Distribution-neutral</td><td class="winner">❌ Distribution-neutral</td></tr>
                <tr><td><strong>Format</strong></td><td class="winner">Performance-based (hands-on)</td><td class="winner">Performance-based (hands-on)</td><td>Multiple choice</td><td>Multiple choice + PBQ</td></tr>
                <tr><td><strong>Duration</strong></td><td>2 hours</td><td>2.5 hours</td><td>90 min per exam (2 exams)</td><td>90 min</td></tr>
                <tr><td><strong>Cost</strong></td><td>$445 (incl. retake)</td><td>$400-$500</td><td>$200 per exam ($400 total)</td><td>$358</td></tr>
                <tr><td><strong>Validity</strong></td><td>2 years</td><td>3 years</td><td>5 years</td><td>Lifetime (CE since 2019)</td></tr>
                <tr><td><strong>2026 Topics</strong></td><td class="winner">✅ Podman, libvirt, bridges, autofs, Git, ACLs/LDAP</td><td>✅ Podman, Stratis, VDO</td><td>❌ Older curriculum</td><td>❌ Older curriculum</td></tr>
                <tr><td><strong>Best For</strong></td><td class="winner">Cloud/DevOps/SRE roles (vendor-neutral foundation)</td><td>Red Hat shops (government, enterprise RHEL)</td><td>Traditional IT (multiple choice = easier for some)</td><td>Entry-level/DOD 8570 compliance</td></tr>
                <tr><td><strong>Anihpj Relevance</strong></td><td class="winner">Full deployment on Ubuntu AND Rocky</td><td>Only RHEL/CentOS/Rocky</td><td>Theory-focused, less hands-on</td><td>Entry-level, less depth</td></tr>
            </tbody></table>
        </div>'''

ms_closing = '        <div class="info-box tip" style="margin:20px 0;">\n            <h5>💡 How to Implement This Learning System</h5>'
if ms_closing in content and 'Study Time Allocation' not in content:
    content = content.replace(ms_closing, augment1 + '\n' + ms_closing)
    changes += 1
    print("  ✅ Augmented Master Summary: Study time chart + LFCS vs certs comparison")

# ============================================================
# AUGMENT 2: Exam Strategy — Add Rescue Commands card + What NOT to Study
# ============================================================
augment2 = r'''
        <!-- RESCUE COMMANDS -->
        <div class="section-block" id="exam-rescue-cmds">
            <h3>🆘 Emergency Rescue Commands — When Something Breaks</h3>
            <div class="diagram-container"><div class="diagram-title">Quick Reference — Commands That Save You on Exam Day</div>
<pre>
  SITUATION                          | RESCUE COMMAND
  ───────────────────────────────────┼──────────────────────────────────────
  Can't find a file                  | find / -name filename 2>/dev/null
  Forgot exact command name          | apropos keyword  OR  man -k keyword
  Forgot command syntax              | command --help  OR  man command
  Service won't start                | journalctl -xeu service-name
  fstab typo broke boot              | Boot recovery → mount -o remount,rw /
  Wrong runlevel/target              | systemctl isolate multi-user.target
  Process stuck / frozen             | kill -9 PID  (LAST RESORT)
  Disk full emergency                | du -sh /* | sort -h  (find culprit)
  Forgot which config file to edit   | dpkg -L package | grep etc  (Debian)
                                     | rpm -qc package  (RHEL)
  Network down, can't ping           | ip link set eth0 up; dhclient eth0
  DNS not resolving                  | echo "8.8.8.8" > /etc/resolv.conf
  User can't log in                  | faillock --user username --reset
  Password forgotten (as root)       | passwd username
  SELinux blocking everything        | getenforce → setenforce 0 (diagnose)
                                     | ausearch -m avc -ts recent
  GRUB won't boot                    | grub-install /dev/sda; update-grub</pre></div>
        </div>

        <!-- WHAT NOT TO STUDY -->
        <div class="info-box danger" style="margin:20px 0;">
            <h5>🚫 What NOT to Study for LFCS — Don't Waste Your Time</h5>
            <p style="color:#c9d1d9;line-height:1.8;">The LFCS exam has a specific scope. Here's what is <strong>NOT tested</strong> — save your study time for what matters:</p>
            <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; margin-top:12px;">
                <div class="info-card" style="border-left:3px solid #ef4444;"><h5>❌ NOT Tested</h5><p>• Kernel compilation<br>• X11/Wayland/GUI config<br>• SQL queries or DB design<br>• Python/Django/Node.js coding<br>• CI/CD pipeline setup (Jenkins, GitHub Actions)<br>• Cloud-specific tools (awscli, gcloud)</p></div>
                <div class="info-card" style="border-left:3px solid #ef4444;"><h5>❌ NOT Tested</h5><p>• Kubernetes (separate CKA/CKAD certs)<br>• Ansible/Chef/Puppet config management<br>• Advanced networking (BGP, OSPF, MPLS)<br>• Hardware-specific tools (dmidecode, lshw details)<br>• Performance benchmarking (fio deep-dive)<br>• LDAP server setup (only client config)</p></div>
                <div class="info-card" style="border-left:3px solid #22c55e;"><h5>✅ DO Study Instead</h5><p>• systemd unit files & targets<br>• User/group management + sudo<br>• LVM (pvcreate→vgcreate→lvcreate→resize2fs)<br>• fstab (6 fields, mount -a test)<br>• netplan/nmcli (persistent config)<br>• systemctl, journalctl, cron</p></div>
                <div class="info-card" style="border-left:3px solid #22c55e;"><h5>✅ DO Study Instead</h5><p>• iptables/nftables/ufw/firewalld<br>• SSH key auth + sshd_config hardening<br>• Nginx reverse proxy config<br>• setfacl/getfacl (ACLs)<br>• sysctl -w vs /etc/sysctl.d/<br>• useradd, usermod, passwd, chage</p></div>
            </div>
        </div>'''

es_before_checklist = '        <div class="info-box tip" style="margin:20px 0;">\n            <h5>✅ Exam Day Checklist</h5>'
if es_before_checklist in content and 'Emergency Rescue Commands' not in content:
    content = content.replace(es_before_checklist, augment2 + '\n' + es_before_checklist)
    changes += 1
    print("  ✅ Augmented Exam Strategy: Rescue commands + What NOT to study")

# ============================================================
# AUGMENT 3: New 2026 Topics — Add Skill Progression Timeline
# ============================================================
augment3 = r'''
        <!-- SKILL PROGRESSION TIMELINE -->
        <div class="diagram-container" style="margin:24px 0;"><div class="diagram-title">📈 Skill Progression — From LFCS Fundamentals to 2026 Modern Topics</div>
<pre>
  LEVEL 1: FOUNDATION (Ch 1-11)          LEVEL 3: MODERN (Ch 39-45)
  ┌─────────────────────────┐            ┌─────────────────────────────┐
  │ • Terminal & FHS         │            │ • libvirt VMs (Ch 39)       │
  │ • Permissions (chmod)    │───────────▶│ • Podman containers (Ch 40) │
  │ • grep/sed/awk           │   Basic    │ • Bridges/bonding (Ch 41)   │
  │ • Bash scripting         │   Linux    │ • autofs (Ch 42)            │
  │ • Package management     │   Admin    │ • Storage perf (Ch 43)      │
  └─────────────────────────┘            │ • Git operations (Ch 44)     │
           │                              │ • ACLs + LDAP (Ch 45)       │
           │  LEVEL 2: CORE (Ch 12-38)    └─────────────────────────────┘
           └──────────────▶ ┌─────────────────────────────┐
                            │ • Users/Groups (Ch 12-14)   │
                            │ • systemd + cron (Ch 15-17) │
                            │ • Networking (Ch 18-21)     │
                            │ • Storage + LVM (Ch 22-25)  │
                            │ • SSH/Nginx/PostgreSQL      │
                            │   (Ch 26-30)                │
                            │ • SELinux/Security (31-33)  │
                            │ • Monitoring/Tuning (34-36) │
                            │ • Production Deploy (37-38) │
                            └─────────────────────────────┘
  
  THE PATTERN: Each 2026 topic builds on core skills:
  Containers ← Processes + Networking + Storage
  Bridges ← Network config + IP routing
  autofs ← NFS + fstab + systemd
  Git ← File ops + Permissions + SSH keys
  ACLs ← chmod + chown + groups
  LDAP ← User management + PAM + SSSD</pre></div>

        <!-- INTEGRATED EXAMPLE -->
        <div class="info-box note" style="margin:20px 0;">
            <h5>🔬 Integrated 2026 Scenario — How These Topics Combine on the Exam</h5>
            <p style="color:#c9d1d9;line-height:1.8;"><strong>Real LFCS task (simulated):</strong> "Create a KVM virtual machine named <code>anihpj-worker</code> with 2GB RAM and 20GB disk. Configure a network bridge so the VM is on the same subnet as the host. Inside the VM, deploy the anihpj application as a Podman container. Ensure the container starts automatically at boot. Create an ACL on <code>/var/www/anihpj/media/</code> giving the container's user read-write access."</p>
            <p style="color:#a1a1aa;font-size:0.9em;margin-top:8px;"><strong>This ONE task tests:</strong> Ch 39 (libvirt) + Ch 41 (bridge) + Ch 40 (Podman) + Ch 16 (systemd auto-start) + Ch 45 (ACLs) + Ch 4 (permissions). <strong>Welcome to the 2026 LFCS exam.</strong></p>
        </div>'''

nt_before_tip = '        <div class="info-box tip" style="margin:20px 0;">\n            <h5>💡 How These Topics Are Tested</h5>'
if nt_before_tip in content and 'Skill Progression Timeline' not in content:
    content = content.replace(nt_before_tip, augment3 + '\n' + nt_before_tip)
    changes += 1
    print("  ✅ Augmented New 2026 Topics: Skill progression + integrated scenario")

# ============================================================
# AUGMENT 4: Port Analogy — Add Dockerfile + K8s manifest inline
# ============================================================
augment4 = r'''
        <!-- REAL DOCKERFILE -->
        <div class="diagram-container" style="margin:24px 0;"><div class="diagram-title">📦 Anihpj Dockerfile — The Blueprint Behind the Analogy</div>
        <div class="split-panel">
            <div class="split-side split-good"><h5>✅ Dockerfile for anihpj/jobpost</h5><pre><code># --- anihpj/Dockerfile ---
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    DJANGO_SETTINGS_MODULE=anihpj.settings.prod

# Create app user (not root!)
RUN groupadd -r anihpj && \\
    useradd -r -g anihpj -d /app anihpj

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER anihpj

# Expose port and run Gunicorn
EXPOSE 8000
CMD ["gunicorn", "anihpj.wsgi:application", \\
     "--bind", "0.0.0.0:8000", \\
     "--workers", "3"]</code></pre></div>
            <div class="split-side split-good"><h5>✅ Kubernetes Deployment (YAML)</h5><pre><code># --- k8s/anihpj-deployment.yaml ---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anihpj
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anihpj
  template:
    metadata:
      labels:
        app: anihpj
    spec:
      containers:
      - name: anihpj
        image: registry.anihpj.com/anihpj:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: anihpj-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: anihpj-svc
spec:
  selector:
    app: anihpj
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP</code></pre></div>
        </div></div>

        <!-- QUICK MEMORY HOOKS -->
        <div class="info-box tip" style="margin:24px 0;">
            <h5>🧠 Quick Memory Hooks — Never Forget These Analogies</h5>
            <div class="card-grid" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-top:12px;">
                <div class="info-card"><div class="card-icon-lg">📋</div><h5>etcd</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Harbor Logbook</strong><br>Records every ship, dock, container. Single source of truth. If the logbook burns, the port forgets everything.</p></div>
                <div class="info-card"><div class="card-icon-lg">🏢</div><h5>API Server</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Front Desk</strong><br>Everyone talks to the front desk. Nobody talks directly to dock workers. Single entry point.</p></div>
                <div class="info-card"><div class="card-icon-lg">🏗️</div><h5>Scheduler</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Dock Master</strong><br>"Ship #42, go to Dock B. Dock B has space and the right cranes." Assigns work to nodes.</p></div>
                <div class="info-card"><div class="card-icon-lg">🏭</div><h5>kubelet</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Dock Worker</strong><br>Actually loads/unloads containers. Reports: "Dock B is full!" or "Container unloaded successfully."</p></div>
                <div class="info-card"><div class="card-icon-lg">🚢</div><h5>Pod</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Container Ship</strong><br>Carries 1+ containers that share the journey. Smallest unit K8s manages. Ships come and go.</p></div>
                <div class="info-card"><div class="card-icon-lg">🏗️</div><h5>kube-proxy</h5><p style="font-size:13px;color:#a1a1aa;">The <strong>Crane Operator</strong><br>Moves containers between ships and docks. Knows exactly where each container needs to go.</p></div>
            </div>
        </div>'''

pa_before_closing = '        <div class="info-box note" style="margin:20px 0;">\n            <h5>🧠 Why This Analogy Works</h5>'
if pa_before_closing in content and 'Anihpj Dockerfile' not in content:
    content = content.replace(pa_before_closing, augment4 + '\n' + pa_before_closing)
    changes += 1
    print("  ✅ Augmented Port Analogy: Dockerfile + K8s YAML + Memory hooks")

# ============================================================
# WRITE OUTPUT
# ============================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 Total augmentations: {changes}")
print("Done!")
