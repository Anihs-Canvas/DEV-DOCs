#!/usr/bin/env python3
"""Chapter-first approach: find each chapter block, then process questions within it."""
import re, random

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

random.seed(42)

chapter_topics = {
    1:"Linux Fundamentals",2:"Terminal & Shell",3:"Filesystem Hierarchy",
    4:"Linux Permissions",5:"File Operations",6:"Text Processing",
    7:"Archives & Compression",8:"Package Management",9:"Advanced Regex",
    10:"Bash Scripting",11:"Advanced Scripting",12:"User Management",
    13:"Group Management",14:"PAM & Passwords",15:"Process Management",
    16:"systemd & Boot",17:"Log Management",18:"Networking Basics",
    19:"Network Config",20:"DNS & Hostnames",21:"Firewall Security",
    22:"Disks & Partitions",23:"Filesystems",24:"LVM Storage",
    25:"Swap & NFS",26:"SSH Remote Access",27:"Nginx & Apache",
    28:"PostgreSQL",29:"Time & Email",30:"Production Stack",
    31:"SELinux & AppArmor",32:"System Hardening",33:"Encryption & Certs",
    34:"System Monitoring",35:"Performance Tuning",36:"Troubleshooting",
    37:"Cron & Scheduling",38:"Full Deployment",39:"libvirt & KVM",
    40:"Podman Containers",41:"Bridges & Bonding",42:"autofs Automounters",
    43:"Storage Performance",44:"Git Operations",45:"ACLs & LDAP",
}

# Same command insights, diagrams, tips, and openings as before
# Inlining the key functions to avoid import issues

def get_command_insight(cmd_word, answer_text, question_text):
    a_lower = answer_text.lower()
    insights = {
        'grep': '<code>grep</code> uses the Boyer-Moore and Aho-Corasick algorithms internally — it\'s not doing naive string search. <code>-r</code> enables recursive directory traversal. <code>-i</code> performs case-insensitive matching. <code>-c</code> counts matches instead of showing them. <code>-v</code> inverts the match — show lines that DON\'T contain the pattern. Combined with <code>-n</code> (line numbers) and <code>-l</code> (filenames only), grep becomes a precision search tool that scales to gigabyte-sized log files.',
        'sed': '<code>sed</code> (Stream EDitor) processes text as a stream — read line, apply script, print result, repeat. It NEVER loads the full file into RAM, making it safe for files of any size. <code>-i</code> edits files in-place (always test WITHOUT <code>-i</code> first). <code>s/old/new/g</code> performs substitution; the <code>g</code> flag replaces ALL occurrences on each line. Address ranges let you apply edits to specific line ranges.',
        'awk': '<code>awk</code> is a full programming language designed for columnar text. It auto-splits lines into fields (<code>$1, $2, $3...</code>) based on <code>-F:</code> (delimiter). <code>$NF</code> = last field, <code>NF</code> = field count, <code>NR</code> = line number. The pipeline <code>awk | sort | uniq -c | sort -rn | head</code> is the single most useful data analysis pattern in Linux administration.',
        'find': '<code>find</code> recursively walks the directory tree, testing each file against your criteria. It searches the actual filesystem in real-time — always current but slower than <code>locate</code>. Key tests: <code>-name</code> (pattern), <code>-type f/d</code>, <code>-size +100M</code>, <code>-mtime -7</code>, <code>-perm 644</code>. Use <code>2>/dev/null</code> to suppress "Permission denied" noise when searching system-wide.',
        'systemctl': '<code>systemctl</code> is your interface to systemd (PID 1). <code>start</code> activates now; <code>enable</code> creates symlinks for auto-start at boot — you need BOTH. <code>status</code> shows loaded state, active state, PID, and recent logs. Always run <code>systemctl daemon-reload</code> after editing unit files before restarting services.',
        'journalctl': '<code>journalctl</code> queries systemd\'s indexed binary journal. <code>-u nginx</code> filters by unit; <code>--since "10 min ago"</code> sets time range; <code>-f</code> tails like <code>tail -f</code>; <code>-p err</code> shows only errors. The journal is stored in <code>/var/log/journal/</code> and configured via <code>/etc/systemd/journald.conf</code>.',
        'iptables': '<code>iptables</code> rules are organized into tables (filter, nat) and chains (INPUT, OUTPUT, FORWARD). Rules process top-to-bottom — first match wins. <code>-A</code> appends, <code>-I</code> inserts, <code>-D</code> deletes. <code>-j DROP</code> silently discards; <code>-j REJECT</code> sends ICMP response. Rules are VOLATILE — lost on reboot unless saved with <code>iptables-save > /etc/iptables/rules.v4</code>.',
        'ufw': '<code>ufw</code> (Uncomplicated Firewall) is Ubuntu\'s user-friendly netfilter frontend. Rules persist in <code>/etc/ufw/</code>. <code>ufw status verbose</code> shows numbered rules. Default policy (<code>ufw default deny incoming</code>) sets the baseline; individual rules carve out exceptions. <code>ufw enable</code> activates at boot via systemd.',
        'ssh': '<code>ssh</code> creates an encrypted tunnel using public-key cryptography. The server authenticates FIRST (host key), then the client (password or key). Private keys MUST be mode 0600 — wrong permissions cause SSH to silently refuse. <code>ssh -v</code> enables verbose debugging. <code>~/.ssh/config</code> defines per-host aliases and options.',
        'mount': '<code>mount</code> attaches a filesystem to the directory tree. ALWAYS test fstab changes with <code>mount -a</code> before rebooting — a typo drops you into emergency mode. <code>mount -o remount,rw /</code> remounts root as read-write in recovery. Use <code>findmnt</code> for a tree view of all mounts.',
        'crontab': '<code>crontab -e</code> edits the user\'s cron table. Five time fields: minute(0-59) hour(0-23) day(1-31) month(1-12) dow(0-7). <code>*/5 * * * *</code> = every 5 minutes. Cron runs with a MINIMAL environment — no .bashrc, stripped PATH. Always use absolute paths or set PATH at the top of the crontab.',
        'git': '<code>git</code> is a distributed version control system. <code>git clone</code> downloads a full repo. The staging area (<code>git add</code>) lets you craft exactly what goes into each commit. <code>git log --oneline</code> shows compact history; <code>git diff</code> shows unstaged changes. For sysadmins, tracking <code>/etc</code> in Git provides an audit trail and instant rollback capability.',
        'podman': '<code>podman</code> is Red Hat\'s daemonless container engine — no background process, rootless by default, CLI-compatible with Docker. <code>podman run -d --name web -p 8080:80 nginx</code> starts a detached container. <code>podman generate systemd</code> creates systemd unit files for auto-starting containers at boot.',
        'virsh': '<code>virsh</code> is the CLI for libvirt — the standard Linux virtualization API. <code>virsh list --all</code> shows all VMs including shut-off ones. XML definitions in <code>/etc/libvirt/qemu/</code> are the source of truth. <code>virsh edit vm-name</code> safely edits domain XML.',
        'chmod': '<code>chmod</code> changes file mode bits. Octal: 4=read, 2=write, 1=execute. 755 (rwxr-xr-x) for dirs/scripts, 644 (rw-r--r--) for configs, 600 (rw-------) for SSH keys. Special bits: setuid(4---) runs as file owner, setgid(2---) inherits group, sticky(1---) on /tmp prevents deletion by non-owners.',
        'useradd': '<code>useradd</code> creates a new user. <code>-m</code> creates home AND copies <code>/etc/skel/</code>. <code>-u UID</code> sets specific UID (required if the exam task specifies one). <code>-s /bin/bash</code> sets shell. Without <code>-m</code>, the user has no home directory — many services fail silently.',
        'usermod': '<code>usermod -aG</code> APPENDS supplementary groups. The <code>-a</code> flag is CRITICAL — without it, the user is REMOVED from all groups not listed. This is one of the most dangerous mistakes: <code>usermod -G docker alice</code> removes Alice from sudo, ssh, and every other group. Always verify with <code>groups alice</code>.',
        'tar': '<code>tar</code> bundles files into one archive, preserving permissions, ownership, and directory structure. <code>-c</code>=create, <code>-x</code>=extract, <code>-t</code>=list, <code>-v</code>=verbose, <code>-f</code>=file. Compression: <code>-z</code>(gzip), <code>-j</code>(bzip2), <code>-J</code>(xz). Always list contents before extracting: <code>tar -tzf archive.tar.gz</code>.',
        'apt': '<code>apt</code> is Debian/Ubuntu\'s package manager. <code>apt update</code> refreshes the package index; <code>apt upgrade</code> installs updates; <code>apt install pkg</code> installs with dependency resolution. <code>apt-cache search keyword</code> searches available packages. Repos: <code>/etc/apt/sources.list</code> and <code>/etc/apt/sources.list.d/</code>.',
        'dnf': '<code>dnf</code> (Dandified YUM) is RHEL/Rocky\'s package manager. <code>dnf install pkg</code> installs; <code>dnf provides */command</code> finds which package owns a file — invaluable on the exam. Repos live in <code>/etc/yum.repos.d/</code>. <code>dnf update</code> updates all packages.',
        'ps': '<code>ps aux</code> shows ALL processes: %CPU, %MEM, VSZ, RSS, STAT, START, TIME, COMMAND. STAT column: R=running, S=sleeping, D=uninterruptible I/O, Z=zombie, T=stopped. <code>ps aux --sort=-%mem</code> sorts by memory usage — find the hogs instantly.',
        'kill': '<code>kill</code> sends signals to processes. SIGTERM(15)="please stop gracefully" (process can catch and clean up). SIGKILL(9)="die now" (kernel terminates without warning — LAST RESORT). Try SIGTERM→SIGINT(2)→SIGKILL. SIGHUP(1) traditionally means "hangup" but many daemons reload config on SIGHUP.',
    }
    for key, insight in insights.items():
        if cmd_word == key or (cmd_word and key in a_lower.split('\n')[0]):
            return insight
    # Pipeline insight
    if '|' in answer_text:
        return 'This pipeline demonstrates the Unix philosophy: small, focused tools connected by pipes to solve complex problems. All commands run CONCURRENTLY — data streams through 64KB kernel buffers without being fully loaded into RAM. Each command does one thing well: <code>awk</code> extracts fields, <code>sort</code> orders, <code>uniq</code> deduplicates, <code>head</code> limits output.'
    if '>' in answer_text:
        return 'Redirection operators control I/O flow. <code>></code> OVERWRITES (destroys old content); <code>>></code> APPENDS (safe for logs). <code>2>&1</code> merges stderr into stdout. ORDER MATTERS: <code>cmd > file 2>&1</code> works correctly; <code>cmd 2>&1 > file</code> does NOT — stderr goes to the ORIGINAL stdout before redirection takes effect.'
    if 'ip ' in a_lower:
        return 'The <code>ip</code> command from iproute2 replaces deprecated <code>ifconfig</code>, <code>route</code>, and <code>arp</code>. <code>ip addr show</code> displays IP addresses; <code>ip link set eth0 up</code> controls interface state; <code>ip route show</code> shows routing. Changes are immediate but NOT persistent — lost on reboot unless configured in netplan or NetworkManager.'
    if 'openssl' in a_lower or 'ssl' in a_lower:
        return 'TLS certificates use X.509 format with a chain of trust: Root CA → Intermediate CA → Server Certificate. <code>openssl s_client -connect host:443</code> shows the full chain. <code>openssl x509 -in cert.pem -text -noout</code> displays certificate fields. Let\'s Encrypt (<code>certbot</code>) provides free 90-day DV certificates.'
    return f'This command is essential for the {chapter_topics.get(0, "Linux")} domain. Understanding its flags, typical use cases, and common pitfalls is critical — the LFCS exam tests practical application under time pressure. Practice variations of this command until the syntax becomes muscle memory.'

def get_skeletal_diagram(cmd_word, answer_text, question_text):
    a_lower = answer_text.lower()
    diagrams = {
        'grep': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔍 grep Pattern Matching</div><pre>  File → Read line → Match pattern? → YES → Print\n                              → NO  → Skip\n  grep "ERROR" *.log | -r=recursive -i=ignore_case -v=invert -c=count</pre></div>',
        'sed': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">✏️ sed Stream Model</div><pre>  Input → Apply script → Print → Next line\n  sed \'s/old/new/g\' | -i=in-place | /pat/d=delete | 10,20p=print range</pre></div>',
        'awk': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📊 awk Fields</div><pre>  Line:"root:x:0:0:root:/root:/bin/bash"\n  $1=root $3=0 $NF=/bin/bash NF=7 NR=line#\n  -F: = delimiter | awk \'{print $1,$3}\' = extract columns</pre></div>',
        'find': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔎 find Traversal</div><pre>  find /start -name "*.log" -mtime -7 -size +10M\n  └─ For each file: name match? time match? size match?\n     └─ ALL pass → print path OR exec command</pre></div>',
        'systemctl': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">⚙️ systemd Lifecycle</div><pre>  Unit → daemon-reload → start → Running\n  enable → Auto-start at boot\n  status → Loaded:Active PID: | disable → No auto-start</pre></div>',
        'journalctl': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📋 journalctl Query</div><pre>  Binary Journal → Indexed DB → Query\n  journalctl -u nginx --since "1h ago" -p err\n  Filter: unit=nginx time>1h priority<=err</pre></div>',
        'iptables': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🛡️ Netfilter Flow</div><pre>  Packet → PREROUTING → [route] → INPUT → Process\n                   ↓\n               FORWARD → POSTROUTING → Out\n  Chains: INPUT OUTPUT FORWARD | -j ACCEPT/DROP/REJECT</pre></div>',
        'ufw': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔥 UFW Hierarchy</div><pre>  default deny incoming ← BASELINE\n  allow 22/tcp          ← SSH exception\n  allow 80,443/tcp      ← HTTP/HTTPS exception\n  First match wins — order matters</pre></div>',
        'ssh': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔐 SSH Sequence</div><pre>  Client→TCP:22→Server host key→Verify→DH key exchange\n  → Encrypted tunnel → Auth (key/password) → Shell\n  ~/.ssh/config: per-host aliases, keys, options</pre></div>',
        'mount': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">💾 Mount Tree</div><pre>  / (root) ← Always first\n  ├── /boot (kernel)\n  ├── /home (user data)\n  └── /var/www/anihpj (LVM LV)\n  df -h | mount -a | findmnt (tree view)</pre></div>',
        'crontab': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">⏰ Cron Fields</div><pre>  * * * * * cmd\n  │ │ │ │ └─ DOW(0-7)\n  │ │ │ └─── Month(1-12)\n  │ │ └───── Day(1-31)\n  │ └─────── Hour(0-23)\n  └───────── Min(0-59)\n  */5 * * * * = every 5min | 0 2 * * 0 = Sun 2AM</pre></div>',
        'git': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🌿 Git Flow</div><pre>  Working Dir → add → Staging → commit → Local → push → Remote\n  git status | git diff | git log --oneline | git pull</pre></div>',
        'podman': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📦 Container Cycle</div><pre>  pull → run → Running → stop → Stopped → rm → Gone\n  ps (list) | logs (output) | exec -it bash (enter)\n  generate systemd → auto-start at boot</pre></div>',
        'virsh': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🖥️ VM Lifecycle</div><pre>  XML Def → define → Shut Off → start → Running\n  shutdown ← Running | destroy (force off)\n  virsh list --all | dominfo | domifaddr</pre></div>',
        'chmod': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔐 Permission Bits</div><pre>  rwx rwx rwx = owner group others\n  421 421 421   read=4 write=2 execute=1\n  755=rwxr-xr-x  644=rw-r--r--  600=rw-------\n  setuid=4--- setgid=2--- sticky=1---</pre></div>',
        'useradd': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">👤 User Creation</div><pre>  useradd -m -u 1500 -s /bin/bash -G dev alice\n  → /etc/passwd entry (UID 1500)\n  → /etc/shadow entry (locked)\n  → /home/alice/ (/etc/skel/ copied)\n  Verify: id alice | getent passwd alice</pre></div>',
        'tar': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📦 tar Workflow</div><pre>  CREATE: tar -czf backup.tar.gz /source\n  -c=create -z=gzip -f=file\n  EXTRACT: tar -xzf backup.tar.gz -C /dest\n  LIST: tar -tzf backup.tar.gz (safe preview)</pre></div>',
        'apt': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📦 APT Flow</div><pre>  sources.list → apt update → Index\n  → search → show → install\n  upgrade (all) | autoremove (clean orphans)\n  dpkg -l | grep pkg (check if installed)</pre></div>',
        'dnf': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📦 DNF Flow</div><pre>  *.repo → check-update → install pkg\n  provides */cmd (find package owner)\n  remove | autoremove | rpm -qa | grep pkg</pre></div>',
        'ps': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📊 Process States</div><pre>  R=Running S=Sleeping D=I/O Wait Z=Zombie T=Stopped\n  ps aux --sort=-%mem | ps -ef | pstree -p</pre></div>',
        'kill': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">⚡ Signal Order</div><pre>  SIGTERM(15) → "Please stop" (graceful)\n  SIGINT(2)   → Ctrl+C (interrupt)\n  SIGKILL(9)  → Kernel kills (no cleanup)\n  SIGHUP(1)   → Reload config (many daemons)</pre></div>',
        'lvm': '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">💿 LVM Layers</div><pre>  PVs→VG(pool)→LVs→mkfs→mount\n  /dev/sdb┐         lv_uploads(50G)\n  /dev/sdc┤→vg_data→lv_db(100G)\n  /dev/sdd┘         lv_logs(20G)\n  pvcreate→vgcreate→lvcreate→mkfs→mount</pre></div>',
    }
    for key, d in diagrams.items():
        if cmd_word == key or (cmd_word and key in a_lower.split('\n')[0]):
            return d
    if '|' in answer_text:
        return '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">🔗 Pipeline Flow</div><pre>  cmd1 | cmd2 | cmd3 → All run CONCURRENTLY\n  stdout→64KB buffer→stdin | Data streams, never fully loaded</pre></div>'
    if '>' in answer_text:
        return '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📤 I/O Redirection</div><pre>  stdin(0)→CMD→stdout(1)→file(>)\n               stderr(2)→file(2>)\n  > =overwrite  >> =append  2>&1 =merge</pre></div>'
    return '<div class="diagram-container" style="margin:10px 0;padding:10px 14px;"><div class="diagram-title">📊 Concept Map</div><pre>  Command → Syscall → Kernel → Hardware\n  man command → see all flags and examples</pre></div>'

def get_chapter_opening(ch_num, question_hash):
    openings = {
        1: ['<strong>Linux Fundamentals:</strong> Linux\'s kernel-userspace architecture is the foundation. The kernel manages hardware; GNU tools provide the userland. "Everything is a file" means devices, processes, and kernel params appear as files — enabling the Unix pipe model.',
            '<strong>Linux Fundamentals:</strong> Born in 1991 when Linus combined his kernel with GNU tools. Now powers 96% of servers. Understanding kernel space vs user space explains why distributions differ despite sharing the same kernel.',
            '<strong>Linux Fundamentals:</strong> The kernel schedules CPU, allocates memory, manages devices. The shell and utilities run in user space. This separation is why a crashing application can\'t take down the entire system — the kernel isolates processes.'],
        2: ['<strong>Terminal & Shell:</strong> The shell interprets commands, expands wildcards, resolves PATH, and manages I/O. When you type <code>ls</code>, bash forks a child, calls <code>execve()</code> to run <code>/usr/bin/ls</code>, and waits. Builtins like <code>cd</code> must run in the shell process itself.',
            '<strong>Terminal & Shell:</strong> Environment variables (with <code>export</code>) are inherited by child processes; shell variables are not. <code>PATH</code> determines command lookup order. Understanding this is essential for debugging "command not found" and "works in terminal but not in script."',
            '<strong>Terminal & Shell:</strong> Tab completion, history (<code>Ctrl+R</code>), and shortcuts (<code>Ctrl+A/E</code> for line start/end) make you faster. The shell is your primary interface — invest time mastering it. Every second saved navigating adds up over 24 exam tasks.'],
        3: ['<strong>Filesystem Hierarchy:</strong> Linux uses a single inverted tree rooted at <code>/</code>. Everything mounts into this tree — hard drives, USB sticks, network shares. The FHS defines where files belong: configs in <code>/etc</code>, logs in <code>/var/log</code>, binaries in <code>/usr/bin</code>.',
            '<strong>Filesystem Hierarchy:</strong> Every file has an inode storing permissions, ownership, timestamps, and block pointers. The filename lives in the directory entry, not the inode. This is why <code>mv</code> within a filesystem is instant (only directory entries change) while <code>cp</code> creates a new inode and copies data.',
            '<strong>Filesystem Hierarchy:</strong> <code>/proc</code> and <code>/sys</code> are virtual filesystems — they don\'t store data on disk but expose kernel data structures as files. <code>cat /proc/cpuinfo</code> reads CPU info; <code>echo 1 > /proc/sys/net/ipv4/ip_forward</code> enables routing. No special tools needed.'],
        4: ['<strong>Linux Permissions:</strong> The rwx model controls access through 9 bits: owner(3) + group(3) + others(3). Directories need execute(+x) to be traversed. Special bits: setuid (run as owner), setgid (inherit group), sticky (/tmp — only owner can delete).',
            '<strong>Linux Permissions:</strong> Octal: 4=read, 2=write, 1=execute. 755 (rwxr-xr-x) for dirs/scripts. 644 (rw-r--r--) for files. 600 (rw-------) for SSH keys. Permissions are the FIRST thing to check when something fails with "Permission denied."',
            '<strong>Linux Permissions:</strong> <code>umask</code> subtracts from default permissions at file creation. Default umask 022 means new files get 644 (666-022) and dirs get 755 (777-022). The sticky bit on <code>/tmp</code> (mode 1777) prevents users from deleting each other\'s files.'],
        5: ['<strong>File Operations:</strong> <code>mv</code> within a filesystem only updates directory entries — instant, no data copy. <code>cp</code> creates a new inode and copies data blocks. Hard links share the SAME inode; symlinks have their own inode storing a path. Understanding inode behavior prevents data loss and performance surprises.',
            '<strong>File Operations:</strong> <code>cp -a</code> preserves ALL attributes. <code>rm -rf</code> is the most dangerous command — silently deletes everything. Always verify your path. <code>touch</code> updates timestamps or creates empty files. <code>mkdir -p</code> creates parent directories as needed.',
            '<strong>File Operations:</strong> <code>ls -la</code> shows all files including hidden (dotfiles). The link count after permissions tells you how many hard links point to this inode. <code>stat filename</code> shows every filesystem-level detail: inode number, blocks, access/modify/change times.'],
    }
    if ch_num in openings:
        idx = question_hash % len(openings[ch_num])
        return openings[ch_num][idx]
    topic = chapter_topics.get(ch_num, "Linux")
    generic = [
        f'<strong>{topic}:</strong> This chapter covers skills that appear frequently on the LFCS exam. The command shown is one you must execute from memory — the exam tests practical application, not theory. Understanding the flags, use cases, and pitfalls ensures you can complete related tasks quickly under time pressure.',
        f'<strong>{topic}:</strong> Mastering this means understanding not just syntax but the underlying mechanism. When you know WHY a command behaves as it does, you can adapt when the exam presents a variation you haven\'t seen before — which it will.',
        f'<strong>{topic}:</strong> The LFCS emphasizes real-world sysadmin tasks. This question tests exactly the kind of scenario you\'d encounter managing a production server — the anihpj deployment you\'ve been building throughout this guide.',
    ]
    return generic[question_hash % 3]

exam_tips = [
    '<strong>LFCS Exam Tip:</strong> Always verify your work immediately after completing a task. Run a confirmation command — catching your own mistakes before submission is the difference between passing and failing.',
    '<strong>LFCS Exam Tip:</strong> If the task says "persistently" or "across reboots," you MUST write to a configuration file in <code>/etc/</code>. Runtime-only changes will earn ZERO points for that requirement.',
    '<strong>LFCS Exam Tip:</strong> Practice this until it becomes automatic. On the timed exam (2 hours, ~24 tasks, ~5 min/task), you cannot afford to look up basic syntax — every second counts.',
    '<strong>LFCS Exam Tip:</strong> Man pages are available during the exam. Use <code>man command</code> if you forget a flag, but knowing common options by heart saves 2-3 minutes per task.',
    '<strong>LFCS Exam Tip:</strong> Read every exam task TWICE before typing. Missing a detail like "UID 1500" or "make persistent" means zero points — even if your commands are otherwise perfect.',
    '<strong>LFCS Exam Tip:</strong> When troubleshooting, change ONE thing at a time and test. Multiple simultaneous changes make it impossible to know which change solved the problem.',
    '<strong>LFCS Exam Tip:</strong> The LFCS is 100% performance-based — no multiple choice. If you can perform this task in your lab VM within 5 minutes, you can perform it on the real exam.',
    '<strong>LFCS Exam Tip:</strong> Reboot your exam VM ONCE before submitting (last 5 minutes). This catches non-persistent configs, broken fstab entries, and services that weren\'t enabled.',
    '<strong>LFCS Exam Tip:</strong> Use the exam\'s built-in man pages. <code>man systemd.unit</code>, <code>man fstab</code>, <code>man crontab</code> — these are your safety net if you blank on exact syntax.',
    '<strong>LFCS Exam Tip:</strong> The sidebar has a built-in text editor. If you struggle with vim, use <code>nano</code> — the exam doesn\'t care which editor you use, only that the config file is correct.',
    '<strong>LFCS Exam Tip:</strong> Partial credit may not apply — tasks are typically all-or-nothing. If a task has 3 requirements and you miss 1, you might get 0 points. Complete EVERY part of EVERY task.',
    '<strong>LFCS Exam Tip:</strong> Check <code>/etc/os-release</code> FIRST. Using <code>apt</code> on Rocky or <code>dnf</code> on Ubuntu wastes time and produces errors. Know which distro you\'re on before touching the keyboard.',
]

# Find ALL chapter practice question headers with their positions
ch_headers = list(re.finditer(r'<h4>Chapter (\d+) — LFCS Practice Questions</h4>', content))
print(f"Found {len(ch_headers)} chapter question headers")

replacements = 0
all_replacements = []  # Collect (old, new) pairs

for i, ch_match in enumerate(ch_headers):
    ch_num = int(ch_match.group(1))
    ch_start = ch_match.end()  # Right after the </h4>
    
    # Find where this chapter's block ends (next chapter-intro or EOF)
    next_intro = re.search(r'<div class="chapter-intro">', content[ch_start:])
    if next_intro:
        ch_end = ch_start + next_intro.start()
    else:
        ch_end = len(content)
    
    ch_block = content[ch_start:ch_end]
    
    # Find ALL exam-question-item blocks within this chapter's block
    q_pattern = re.compile(
        r'(<div class="exam-question-item">.*?)'
        r'(<div class="eq-exp-label">.*?Explanation</div>\s*<p>)(.*?)(</p>)',
        re.DOTALL
    )
    
    for qm in q_pattern.finditer(ch_block):
        full_match = qm.group(0)
        prefix = qm.group(1)
        exp_open = qm.group(2)
        exp_close = qm.group(4)
        
        # Extract question text
        q_text_match = re.search(r'<div class="eq-question">(.*?)</div>', prefix, re.DOTALL)
        q_text = q_text_match.group(1) if q_text_match else ""
        q_text_clean = re.sub(r'<[^>]+>', ' ', q_text).strip()
        
        # Extract answer
        ans_match = re.search(r'<div class="eq-answer">(.*?)</div>', prefix, re.DOTALL)
        ans_text = ans_match.group(1) if ans_match else ""
        ans_text_clean = re.sub(r'<[^>]+>', '', ans_text).strip()
        
        # Question number
        q_num_match = re.search(r'<div class="eq-number">(Q\d+)</div>', prefix)
        q_num = q_num_match.group(1) if q_num_match else ""
        
        # Key command
        ans_lines = [l.strip() for l in ans_text_clean.split('\n') if l.strip() and not l.strip().startswith('#')]
        first_cmd = ans_lines[0] if ans_lines else ""
        cmd_word = first_cmd.split()[0] if first_cmd else ""
        
        # Hash for variety
        q_hash = abs(hash(q_text_clean + str(ch_num) + q_num)) % 1000
        
        # Build explanation
        parts = []
        parts.append(get_chapter_opening(ch_num, q_hash))
        parts.append(get_command_insight(cmd_word, ans_text_clean, q_text_clean))
        tip_idx = (q_hash * 7 + ch_num) % len(exam_tips)
        parts.append(exam_tips[tip_idx])
        
        new_body = ' '.join(parts)
        diagram = get_skeletal_diagram(cmd_word, ans_text_clean, q_text_clean)
        
        # Build the new block
        old_full = prefix + exp_open + qm.group(3) + exp_close
        new_full = prefix + exp_open + new_body + exp_close + '\n' + diagram + '\n'
        
        # Collect replacement
        if old_full in content:
            all_replacements.append((old_full, new_full))
            replacements += 1

# Apply all replacements at once (process in reverse to preserve positions)
all_replacements.sort(key=lambda x: len(x[0]), reverse=True)  # Longest first to avoid substring conflicts
for old, new in all_replacements:
    content = content.replace(old, new, 1)

print(f"Enhanced {replacements} explanations")
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")
