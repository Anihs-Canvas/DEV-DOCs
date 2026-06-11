#!/usr/bin/env python3
"""Add ASCII skeletal diagrams to practice question explanations."""
import re, random

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

count_before = content.count('eq-explanation')
added = 0

def get_diagram(question_text, answer_text):
    """Return an appropriate ASCII diagram based on question content."""
    q = question_text.lower()
    a = answer_text.lower()
    
    # Permission/ACL diagrams
    if any(w in q for w in ['permission', 'chmod', 'chown', 'rwx', 'octal', 'umask']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">🔐 Permission Model</div><pre>
  OWNER   GROUP   OTHER
  r w x   r - x   r - -
  │ │ │   │ │ │   │ │ │
  4 2 1   4 0 1   4 0 0  = 754
  └─┬─┘   └─┬─┘   └─┬─┘
    7       5       4
  Read = 4  |  Write = 2  |  Execute = 1</pre></div>"""
    
    # Filesystem/directory diagrams
    if any(w in q for w in ['directory', 'mkdir', 'filesystem', 'fhs', '/etc', '/var', '/opt']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">📁 Linux Directory Structure</div><pre>
  /                    ← Root
  ├── /bin             ← Essential binaries (ls, cp, mv)
  ├── /etc             ← Config files (nginx, ssh, systemd)
  │   ├── /etc/nginx/
  │   └── /etc/ssh/
  ├── /var             ← Variable data (logs, databases)
  │   └── /var/log/
  ├── /opt             ← Optional / third-party software
  │   └── /opt/anihpj/ ← Your Django app!
  ├── /home            ← User home directories
  ├── /tmp             ← Temporary files (cleared on boot)
  └── /proc, /sys, /dev ← Virtual filesystems (kernel info)</pre></div>"""
    
    # Pipeline / data flow diagrams
    if any(w in q for w in ['pipe', 'pipeline', 'grep', 'awk', 'sed', 'sort', 'uniq', 'stdout', 'stdin']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">🔗 Pipeline Data Flow</div><pre>
  ┌─────────┐    stdout    ┌─────────┐    stdout    ┌─────────┐
  │  cmd1   │─────────────▶│  cmd2   │─────────────▶│  cmd3   │
  │ (write) │   pipe (|)   │(filter) │   pipe (|)   │ (final) │
  └─────────┘              └─────────┘              └─────────┘
       │                        │                        │
       ▼                        ▼                        ▼
  Produces raw           Transforms/             Outputs final
  data stream            filters data             result

  KEY: All commands run CONCURRENTLY — no temp files needed!
  Data flows through 64KB kernel buffers (very efficient).</pre></div>"""
    
    # Process / signal diagrams
    if any(w in q for w in ['process', 'signal', 'kill', 'pid', 'background', 'foreground', 'nice']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">⚙️ Process States & Signals</div><pre>
  ┌──────────┐  SIGTERM(15)  ┌──────────┐
  │ RUNNING  │──────────────▶│ STOPPING │──▶ EXIT(0)
  │ (active) │               │(cleanup) │
  └──────────┘               └──────────┘
       │                          ▲
       │ SIGKILL(9)               │ SIGHUP(1)
       ▼                          │
  ┌──────────┐                    │
  │  KILLED  │  Ctrl+Z ┌──────────┴──┐  fg ┌──────────┐
  │ (force)  │────────▶│  STOPPED    │────▶│ RUNNING  │
  └──────────┘         │ (paused)    │     │ (resume) │
                       └─────────────┘     └──────────┘
  Nice values: -20 (highest priority) to 19 (lowest)</pre></div>"""
    
    # Network / firewall diagrams
    if any(w in q for w in ['firewall', 'network', 'ufw', 'iptables', 'port', 'ip addr', 'routing']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">🌐 Network Packet Flow</div><pre>
  INTERNET ──▶ [UFW/iptables] ──▶ [Routing] ──▶ [Application]
                  │                                    │
                  ├── ALLOW: 80/tcp (HTTP)            ▼
                  ├── ALLOW: 443/tcp (HTTPS)    ┌──────────┐
                  ├── ALLOW: 22/tcp (SSH)       │  Nginx   │
                  └── DENY:  everything else    │  :80:443 │
                                                └────┬─────┘
                                                     │ proxy_pass
                                                     ▼
                                                ┌──────────┐
                                                │ Gunicorn │
                                                │ :8000    │
                                                └──────────┘</pre></div>"""
    
    # Storage / LVM diagrams
    if any(w in q for w in ['lvm', 'partition', 'mount', 'fstab', 'mkfs', 'disk', 'storage']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">💿 LVM Architecture</div><pre>
  ┌─────────────────────────────────────────────┐
  │  LOGICAL VOLUMES (what you actually use)     │
  │  lv_root (50GB)  lv_home (100GB)  lv_data   │
  └──────────────────┬──────────────────────────┘
                     │ lvcreate / lvextend
  ┌──────────────────┴──────────────────────────┐
  │  VOLUME GROUP (pool of storage)              │
  │  vg_system = /dev/sda1 + /dev/sdb1          │
  └──────────────────┬──────────────────────────┘
                     │ vgcreate / vgextend
  ┌──────────────────┴──────────────────────────┐
  │  PHYSICAL VOLUMES (actual disks/partitions)  │
  │  /dev/sda1 (100GB SSD)  /dev/sdb1 (200GB)   │
  └─────────────────────────────────────────────┘</pre></div>"""
    
    # systemd / service diagrams
    if any(w in q for w in ['systemd', 'service', 'unit', 'systemctl', 'daemon']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">⚡ systemd Unit Lifecycle</div><pre>
  ┌────────────┐    systemctl start    ┌────────────┐
  │  INACTIVE  │──────────────────────▶│  ACTIVE    │
  │  (dead)    │                      │ (running)  │
  └────────────┘                      └─────┬──────┘
       ▲                                    │
       │ systemctl stop                     │ systemctl reload
       │                                    ▼
       │                            ┌──────────────┐
       │                            │   RELOADING  │
       │                            │ (config only)│
       │                            └──────────────┘
  ┌────┴───────┐
  │  ENABLED   │ ← systemctl enable (survives reboot)
  │ (boot:yes) │ ← systemctl disable (doesn't start on boot)
  └────────────┘</pre></div>"""
    
    # User/Group diagrams
    if any(w in q for w in ['user', 'group', 'uid', 'gid', '/etc/passwd', '/etc/shadow']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">👤 User & Group Model</div><pre>
  ┌─────────────────────────────────────────────┐
  │  /etc/passwd (user database)                 │
  │  alice:x:1001:1001:Alice:/home/alice:/bin/bash│
  │  │      │    │    │     │         │          │
  │  name   pw   UID  GID   comment   home    shell
  └─────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────┐
  │  /etc/shadow (passwords)                     │
  │  alice:$6$salt$hash:19500:0:99999:7:::     │
  │  │      │            │     │  │     │        │
  │  name   hash     last_chg min max  warn     │
  └─────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────┐
  │  /etc/group (group database)                 │
  │  anihpj-devs:x:2001:alice,bob,carol        │
  │  │           │  │    └─ members ─┘          │
  │  name        pw  GID                        │
  └─────────────────────────────────────────────┘</pre></div>"""
    
    # Git workflow diagrams
    if any(w in q for w in ['git', 'commit', 'branch', 'clone', 'push', 'pull']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">📝 Git Workflow</div><pre>
  ┌─────────┐   git clone    ┌─────────┐
  │ Remote  │───────────────▶│  Local  │
  │ (GitHub)│               │  Repo   │
  └────┬────┘               └────┬────┘
       │ git push                │
       │◀────────────────────────┘
       │                    ┌────┴────┐
       │ git pull           │ Staging │ ← git add
       │◀───────────────────│  Area   │
                            └────┬────┘
                                 │ git commit -m "msg"
                                 ▼
                            ┌─────────┐
                            │  Local  │
                            │ Commits │
                            └─────────┘
  Workflow: edit → add → commit → push
  Undo: git checkout -- file (revert uncommitted changes)</pre></div>"""
    
    # Container / VM diagrams
    if any(w in q for w in ['container', 'docker', 'podman', 'vm', 'kvm', 'libvirt', 'virt']):
        return """<div class="diagram-container" style="margin:12px 0;padding:12px 16px;font-size:0.78em;"><div class="diagram-title">📦 Container vs VM</div><pre>
  VIRTUAL MACHINE              CONTAINER
  ┌──────────────┐            ┌──────────────┐
  │   App Code   │            │   App Code   │
  ├──────────────┤            ├──────────────┤
  │ Dependencies │            │ Dependencies │
  ├──────────────┤            ├──────────────┤
  │  Guest OS    │            │  Runtime     │
  ├──────────────┤            ├──────────────┤
  │ Hypervisor   │            │  Host OS     │
  ├──────────────┤            ├──────────────┤
  │  Hardware    │            │  Hardware    │
  └──────────────┘            └──────────────┘
  GBs | Minutes to boot      MBs | Milliseconds
  Full OS isolation          Process isolation</pre></div>"""
    
    return None  # No diagram needed

# Process all explanation blocks and add diagrams
def process_explanation(match):
    global added
    full = match.group(0)
    
    # Skip if already has a diagram
    if 'diagram-container' in full:
        return full
    
    # Extract question text (we need to look before this match)
    # The explanation is inside a details block; find the question from the surrounding exam-question-item
    # This is complex with regex, so we'll use the answer text instead
    
    # Get the answer text from the same details block
    answer_match = re.search(r'<div class="eq-answer">(.*?)</div>', full, re.DOTALL)
    question_match = re.search(r'<div class="eq-question">(.*?)</div>', full, re.DOTALL)
    
    if not answer_match:
        return full
    
    question = question_match.group(1) if question_match else ""
    answer = answer_match.group(1)
    
    diagram = get_diagram(question, answer)
    if not diagram:
        return full
    
    # Add diagram before the closing </div> of the explanation
    # Find the closing </div> of the explanation
    expl_end = full.rfind('</div>')
    if expl_end > 0:
        new_full = full[:expl_end] + '\n            ' + diagram + '\n        ' + full[expl_end:]
        added += 1
        return new_full
    
    return full

# Find all eq-explanation blocks and add diagrams
pattern = re.compile(r'<div class="eq-explanation">.*?</div>\s*(?=\s*</details>|\s*</div>\s*</div>)', re.DOTALL)
content = pattern.sub(process_explanation, content)

count_after = content.count('diagram-container')
print(f"Diagrams before: {count_before}")
print(f"Diagrams added to explanations: {added}")
print(f"Total diagrams now: {count_after}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
