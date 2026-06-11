#!/usr/bin/env python3
"""Add ASCII skeletal diagrams to practice question explanations."""
import re

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

added = 0

def get_diagram(question_text):
    """Return an appropriate ASCII diagram based on question content."""
    q = question_text.lower()
    
    if any(w in q for w in ['permission', 'chmod', 'chown', 'rwx', 'octal', 'umask']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔐 Linux Permissions</div><pre>
  OWNER   GROUP   OTHER
  r w x   r - x   r - -
  4 2 1   4 0 1   4 0 0  = 754
  Read=4 | Write=2 | Execute=1</pre></div>"""
    
    if any(w in q for w in ['directory', 'mkdir', 'fhs', 'filesystem']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📁 FHS Structure</div><pre>
  /            Root
  ├── /bin     Binaries
  ├── /etc     Configs
  ├── /var     Logs/Data
  ├── /opt     3rd-party (anihpj!)
  └── /home    Users</pre></div>"""
    
    if any(w in q for w in ['pipe', 'pipeline', 'grep', 'awk', 'sed', 'sort', 'uniq']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔗 Pipeline</div><pre>
  cmd1 | cmd2 | cmd3 → all run concurrently
  Data flows through 64KB kernel buffers</pre></div>"""
    
    if any(w in q for w in ['process', 'signal', 'kill', 'pid', 'background', 'foreground', 'nice']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">⚙️ Signals</div><pre>
  SIGTERM(15)=graceful | SIGKILL(9)=force
  SIGSTOP(19)=pause | SIGCONT(18)=resume
  Ctrl+Z=SIGTSTP | Ctrl+C=SIGINT</pre></div>"""
    
    if any(w in q for w in ['firewall', 'ufw', 'iptables', 'port', 'routing']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🌐 Firewall</div><pre>
  INTERNET → [UFW] → [APP]
  Default: deny incoming, allow outgoing
  ufw allow 80/tcp; ufw enable</pre></div>"""
    
    if any(w in q for w in ['lvm', 'partition', 'mount', 'fstab', 'mkfs', 'disk', 'storage']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">💿 LVM Layers</div><pre>
  LV (logical volume) → VG (volume group) → PV (physical volume)
  lvcreate → vgcreate → pvcreate</pre></div>"""
    
    if any(w in q for w in ['systemd', 'service', 'unit', 'systemctl']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">⚡ systemd</div><pre>
  start/stop=now | enable/disable=boot
  daemon-reload (after editing units!)
  systemctl status → check state</pre></div>"""
    
    if any(w in q for w in ['user', 'group', 'uid', 'gid', 'passwd', 'shadow']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">👤 User Model</div><pre>
  /etc/passwd: name:x:UID:GID:comment:home:shell
  /etc/shadow: name:hash:last:min:max:warn:inactive
  /etc/group:  name:x:GID:members</pre></div>"""
    
    if any(w in q for w in ['git', 'commit', 'branch', 'clone', 'push', 'pull']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📝 Git Flow</div><pre>
  edit → git add → git commit → git push
  git clone URL → git pull (update)</pre></div>"""
    
    if any(w in q for w in ['container', 'docker', 'podman', 'vm', 'kvm', 'libvirt']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📦 Container vs VM</div><pre>
  VM: App→OS→Hypervisor→Hardware (GBs)
  Container: App→Runtime→OS→Hardware (MBs)</pre></div>"""
    
    if any(w in q for w in ['ssh', 'sshd', 'key']):
        return """<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔑 SSH Auth</div><pre>
  Client → ssh user@host → Server
  ssh-keygen → ssh-copy-id → key-based login
  sshd -t (test config) → systemctl reload sshd</pre></div>"""
    
    return None

# Process each exam-question-item by finding its explanation and adding diagram
# Strategy: find </div> before </details> and insert diagram before it
# More precisely: find the eq-explanation's closing </div> and insert before it

def process_match(match):
    global added
    block = match.group(0)
    
    # Skip if already has diagram
    if 'diagram-container' in block:
        return block
    
    # Get question text
    qm = re.search(r'<div class="eq-question">(.*?)</div>', block, re.DOTALL)
    if not qm:
        return block
    
    question = qm.group(1)
    diagram = get_diagram(question)
    if not diagram:
        return block
    
    # Find the explanation's closing </div> (the one right before </details> or the next </div>)
    # The explanation block is: <div class="eq-explanation"> ... </div>
    # We need to find the matching closing </div>
    
    # Find position of eq-explanation start
    expl_start = block.find('<div class="eq-explanation">')
    if expl_start == -1:
        return block
    
    # Find the matching </div> by counting nested divs
    depth = 0
    pos = expl_start
    while pos < len(block):
        next_open = block.find('<div', pos + 1)
        next_close = block.find('</div>', pos + 1)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            if depth == 0:
                expl_end = next_close  # Position of </div> that closes eq-explanation
                break
            depth -= 1
            pos = next_close
    else:
        return block  # couldn't find matching close
    
    # Insert diagram before the closing </div> of the explanation
    new_block = block[:expl_end] + '\n            ' + diagram + '\n        ' + block[expl_end:]
    added += 1
    return new_block

# Find all exam question blocks
pattern = re.compile(r'<div class="exam-question-item">.*?</details>', re.DOTALL)
content = pattern.sub(process_match, content)

print(f"Diagrams added to explanations: {added}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

diagrams_total = content.count('diagram-container')
print(f"Total diagrams now: {diagrams_total}")
