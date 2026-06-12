#!/usr/bin/env python3
"""Re-generate ALL practice question explanations with maximum variation."""
import re, random

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

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

exam_tips = [
    '<strong>LFCS Exam Tip:</strong> Always verify your work immediately. Run a confirmation command after completing the task — catching your own mistakes before submission is the difference between passing and failing.',
    '<strong>LFCS Exam Tip:</strong> If the task mentions "persistently" or "across reboots," you MUST edit a configuration file in <code>/etc/</code>. Runtime-only changes will earn zero points for those tasks.',
    '<strong>LFCS Exam Tip:</strong> Practice this command until it becomes automatic. On the timed exam (2 hours, ~24 tasks), you cannot afford to look up basic syntax — every second counts.',
    '<strong>LFCS Exam Tip:</strong> Man pages are available during the exam (<code>man command</code>). Use them if you forget a flag, but knowing common options by heart will save you 2-3 minutes per task.',
    '<strong>LFCS Exam Tip:</strong> Read every exam task TWICE before touching the keyboard. Missing a single detail like "UID 1500" or "GID 2000" means zero points — even if your commands are otherwise perfect.',
    '<strong>LFCS Exam Tip:</strong> When troubleshooting, change ONE thing at a time and test. Making multiple simultaneous changes makes it impossible to know which change solved the problem.',
    '<strong>LFCS Exam Tip:</strong> The LFCS is performance-based — no multiple choice. If you can perform this task on your lab VM within 5 minutes, you can perform it on the real exam.',
    '<strong>LFCS Exam Tip:</strong> Reboot your exam VM at least once before submitting (last 5 minutes). This catches non-persistent configs, broken fstab entries, and services that weren\'t enabled.',
]

# Match each exam-question-item block
q_pattern = re.compile(
    r'(<div class="exam-question-item">.*?)'
    r'(<div class="eq-exp-label">.*?Explanation</div>\s*<p>)(.*?)(</p>)',
    re.DOTALL
)

random.seed(42)
replacements = 0

for qm in q_pattern.finditer(content):
    full_match = qm.group(0)
    prefix = qm.group(1)   # everything before explanation
    exp_open = qm.group(2) # <div class="eq-exp-label">...<p>
    old_exp_body = qm.group(3)  # current explanation text
    exp_close = qm.group(4) # </p>
    
    # Determine chapter number — find the NEAREST preceding chapter header
    pos = qm.start()
    all_ch = list(re.finditer(r'Chapter (\d+) — LFCS Practice Questions</h4>', content[:pos]))
    if not all_ch:
        continue
    ch_num = int(all_ch[-1].group(1))  # Take the LAST (nearest) match
    topic = chapter_topics.get(ch_num, "Linux")
    
    # Extract question text
    q_text_match = re.search(r'<div class="eq-question">(.*?)</div>', prefix, re.DOTALL)
    q_text = q_text_match.group(1) if q_text_match else "this task"
    q_text = re.sub(r'<[^>]+>', ' ', q_text).strip()
    
    # Extract answer
    ans_match = re.search(r'<div class="eq-answer">(.*?)</div>', prefix, re.DOTALL)
    ans_text = ans_match.group(1) if ans_match else ""
    ans_text = re.sub(r'<[^>]+>', '', ans_text).strip()
    
    # Extract question number
    q_num_match = re.search(r'<div class="eq-number">(Q\d+)</div>', prefix)
    q_num = q_num_match.group(1) if q_num_match else ""
    
    # Extract key command from answer
    ans_lines = [l.strip() for l in ans_text.split('\n') if l.strip() and not l.strip().startswith('#')]
    first_cmd = ans_lines[0] if ans_lines else ""
    cmd_word = first_cmd.split()[0] if first_cmd else ""
    
    # Build varied explanation
    parts = []
    
    # Part 1: Chapter-specific opening (with slight variation per question)
    openings = {
        1: [f'<strong>{topic}:</strong> This question tests the foundations of Linux — the kernel, GNU tools, and the "everything is a file" philosophy. Understanding these core concepts helps you troubleshoot effectively on the exam.',
            f'<strong>{topic}:</strong> Linux\'s history and architecture are not just trivia — they explain WHY the system behaves as it does. This question tests that foundational understanding every sysadmin needs.',
            f'<strong>{topic}:</strong> Before diving into commands, knowing what Linux IS matters. This question reinforces the kernel-userspace split and why distributions differ despite sharing the same kernel.'],
        2: [f'<strong>{topic}:</strong> The terminal is where real Linux work happens. This question tests your ability to navigate, find help, and control your shell environment — skills used in every single exam task.',
            f'<strong>{topic}:</strong> Shell mastery separates beginners from professionals. This question covers PATH resolution, builtins vs external commands, and shell configuration that affects everything you do.',
            f'<strong>{topic}:</strong> Understanding how the shell finds and executes commands is fundamental. This question tests the PATH mechanism, shell variables, and command discovery that powers every terminal interaction.'],
        3: [f'<strong>{topic}:</strong> The Linux filesystem is a single tree rooted at <code>/</code>. This question tests your knowledge of the FHS — knowing where configs, logs, binaries, and data live helps you find problems fast.',
            f'<strong>{topic}:</strong> Every file on Linux has a prescribed location per the Filesystem Hierarchy Standard. This question tests your mental map of the directory tree — essential for navigating unfamiliar systems.',
            f'<strong>{topic}:</strong> Unlike Windows drive letters, Linux mounts everything into one tree. This question reinforces where critical system files live and why the FHS matters for system administration.'],
        4: [f'<strong>{topic}:</strong> The rwx permission model (owner-group-other) is Linux\'s first security layer. This question tests your ability to read, set, and troubleshoot permissions — a daily sysadmin task.',
            f'<strong>{topic}:</strong> File permissions control every access on a Linux system. This question tests the 9 permission bits, special bits (setuid/setgid/sticky), and how to apply them correctly in production.',
            f'<strong>{topic}:</strong> "Permission denied" is the most common error you\'ll encounter. This question builds the skills to diagnose and fix permission issues — from basic rwx to umask and special bits.'],
        5: [f'<strong>{topic}:</strong> Creating, copying, moving, and inspecting files are the most fundamental Linux operations. This question tests inode behavior, hard vs symbolic links, and redirection — core skills for every task.',
            f'<strong>{topic}:</strong> Understanding how <code>cp</code> differs from <code>mv</code> at the inode level matters for performance and data safety. This question tests file operations that every sysadmin performs daily.',
            f'<strong>{topic}:</strong> File operations are the building blocks of everything else. This question covers the commands you\'ll use hundreds of times — knowing their flags and edge cases prevents costly mistakes.'],
    }
    
    # Generic openings for chapters without custom ones
    gen_openings = [
        f'<strong>{topic}:</strong> This question tests a key concept from this chapter that appears frequently on the LFCS exam. Mastering this will help you complete related tasks quickly and accurately under time pressure.',
        f'<strong>{topic}:</strong> This is a core skill tested on the LFCS. Understanding not just the command but WHY it works this way helps you adapt when exam tasks combine multiple concepts.',
        f'<strong>{topic}:</strong> The LFCS exam emphasizes practical, hands-on skills — exactly what this question tests. Practice this until you can complete it without consulting documentation.',
    ]
    
    if ch_num in openings:
        idx = hash(q_text) % len(openings[ch_num])
        parts.append(openings[ch_num][idx])
    else:
        idx = hash(q_text) % len(gen_openings)
        parts.append(gen_openings[idx])
    
    # Part 2: Command-specific insight (if we can identify the command)
    cmd_insights = {
        'grep': '<code>grep</code> uses efficient pattern matching that scales to gigabyte-sized files. The <code>-r</code> flag searches recursively, <code>-i</code> ignores case, and <code>-v</code> inverts the match.',
        'sed': '<code>sed</code> processes text as a stream — one line at a time, never loading the full file into RAM. <code>-i</code> edits in-place (always test without <code>-i</code> first).',
        'awk': '<code>awk</code> is a full programming language optimized for columnar data. <code>-F:</code> sets the delimiter; numbers like <code>$1, $2</code> reference fields by position.',
        'find': '<code>find</code> searches the actual filesystem in real time. Use <code>2>/dev/null</code> to suppress "Permission denied" noise. Combine with <code>-exec</code> to act on results.',
        'systemctl': '<code>systemctl</code> talks to systemd via D-Bus. <code>start</code> runs now; <code>enable</code> makes it survive reboot — you need BOTH for persistent services.',
        'journalctl': '<code>journalctl</code> queries systemd\'s indexed binary journal. <code>-u</code> filters by unit; <code>-xe</code> shows recent entries with explanations; <code>--since</code> filters by time.',
        'mount': 'Always validate fstab changes with <code>mount -a</code> BEFORE rebooting. A typo drops you into emergency mode, costing precious exam time to recover.',
        'iptables': 'Firewall rules process top-to-bottom — first match wins. Rules evaporate on reboot unless saved with <code>iptables-save</code> or <code>netfilter-persistent</code>.',
        'ufw': '<code>ufw</code> is a friendly frontend for iptables. Rules are persistent by default. <code>ufw status verbose</code> shows all active rules with their numbers.',
        'ssh': 'SSH encrypts everything between client and server. Private keys MUST be 0600 — wrong permissions cause SSH to silently refuse the key.',
        'crontab': 'Cron jobs run with a minimal environment (no .bashrc, stripped PATH). Always use absolute paths or set PATH explicitly at the top of the crontab.',
        'git': '<code>git</code> tracks content changes, not just filenames. <code>git log</code> shows history; <code>git diff</code> shows unstaged changes; <code>git status</code> shows current state.',
        'podman': 'Podman is daemonless and supports rootless containers — no background process, no root requirements. CLI is Docker-compatible: same commands, better security.',
        'virsh': '<code>virsh</code> communicates with libvirtd, not directly with QEMU/KVM. VMs defined but not running show as "shut off" in <code>virsh list --all</code>.',
        'chmod': 'Permissions use octal (4=read, 2=write, 1=execute). Common patterns: 755 for directories/scripts, 644 for configs, 600 for SSH keys.',
        'useradd': '<code>-m</code> creates the home directory with /etc/skel contents. <code>-s</code> sets the shell. Without <code>-m</code>, the user has no home — many services fail silently.',
        'usermod': '<code>usermod -aG</code> APPENDS groups — the <code>-a</code> flag is CRITICAL. Without it, all other supplementary groups are removed, potentially locking the user out.',
    }
    
    for key, insight in cmd_insights.items():
        if cmd_word == key or (cmd_word and first_cmd.startswith(key + ' ')):
            parts.append(insight)
            break
    
    # Part 3: Random exam tip
    tip_idx = hash(q_text + str(ch_num) + q_num) % len(exam_tips)
    parts.append(exam_tips[tip_idx])
    
    new_body = ' '.join(parts)
    new_block = prefix + exp_open + new_body + exp_close
    
    if full_match in content:
        content = content.replace(full_match, new_block, 1)
        replacements += 1

print(f"Re-generated {replacements} explanations with varied content")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")
