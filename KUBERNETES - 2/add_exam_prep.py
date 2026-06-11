#!/usr/bin/env python3
"""Add LFCS exam preparation enrichments to each chapter."""
import re

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Chapter-specific enrichment data
# Format: chapter_num -> (quick_commands, exam_focus, common_mistake)
enrichments = {
    1: ("uname -r, uname -a, lsmod, modprobe, cat /proc/cpuinfo",
        "LFCS tests your understanding of the Linux ecosystem: know the difference between kernel and distribution, understand FHS, and be able to identify your distro and kernel version.",
        "Confusing the Linux kernel with a distribution. The kernel is just the core; the distro adds GNU tools, package manager, and desktop."),
    2: ("ls, cd, pwd, mkdir, cp, mv, rm, find, locate, which",
        "File navigation is tested in EVERY task. You must navigate quickly between directories and find files efficiently. Time spent searching = points lost.",
        "Using rm without -i or double-checking pwd. Always verify your location before destructive commands."),
    3: ("cat, less, head, tail, grep, sed, awk, cut, sort, uniq, wc, diff",
        "Text processing is the backbone of Linux administration. LFCS may ask you to parse logs, extract fields, or transform config files. Master grep+awk+sed.",
        "Forgetting -r with grep for recursive search. Not using -i for case-insensitive matching when it would save time."),
    4: ("tar -czf, tar -xzf, gzip, bzip2, apt install, apt update, apt search, dpkg -l, yum install, dnf install",
        "Package management differs between Ubuntu (apt/dpkg) and Rocky (dnf/rpm). LFCS tests BOTH — know which distro you're on and use the right tool.",
        "Using apt on Rocky or dnf on Ubuntu. Also: forgetting apt update before apt install on a fresh system."),
    5: ("bash, sh, source, ., export, env, alias, unalias, history, !!, echo $PATH",
        "Shell mastery is fundamental. LFCS expects you to customize your environment, set variables, create aliases, and use command history efficiently.",
        "Using sh instead of bash for scripting (no arrays, no [[]]). Forgetting to export variables that child processes need."),
    6: ("cat > file, echo >> file, tee, stdin/stdout/stderr, 2>&1, >/dev/null, <<EOF, pipe |",
        "Redirection and pipes are tested implicitly in every task. You must understand stdout vs stderr and how to combine or suppress output.",
        "Using > when you mean >> (overwrites instead of appends). Not redirecting stderr (2>&1) when troubleshooting."),
    7: ("vim, nano, :wq, :q!, /search, dd, yy, p, u, Ctrl+R, :%s/old/new/g",
        "You WILL need to edit config files in the exam. Know basic vi/vim: save, quit, search, delete lines. Nano is also available if you prefer it.",
        "Getting stuck in vim and wasting time. Practice :wq, :q!, and i/Esc until they're automatic."),
    8: ("tar -czf, gzip -k, bzip2 -k, xz, zip, unzip, rsync -avz, dd if=/dev/zero of=file bs=1M count=100",
        "Archiving is essential for backups and file transfers. Know the tar flags: c=create, x=extract, z=gzip, j=bzip2, f=file.",
        "Forgetting the -f flag with tar. Extracting archives without checking contents first (tar -tzf to list)."),
    9: ("#!/bin/bash, $var, ${var}, $1-$9, $#, $@, $?, $(command), if/elif/else, for/while",
        "Shell scripting is tested directly — you may need to write a script from scratch. Focus on: variables, conditionals, loops, and error handling.",
        "Forgetting #!/bin/bash shebang. Using [ ] instead of [[ ]] (breaks on empty vars). Not quoting variables."),
    10: ("for f in *; do ... done, while read line, case $var in, select, until, break, continue",
        "Loops automate repetitive tasks. LFCS may ask you to process multiple files, iterate over users, or create batch operations.",
        "Using for f in $(ls) instead of for f in * (breaks on filenames with spaces). Infinite loops from forgetting increment."),
    11: ("f(){...}, return, local var, trap cleanup EXIT, set -euo pipefail, $RANDOM, mktemp",
        "Functions organize code into reusable blocks. Trap handles cleanup. set -euo pipefail is the gold standard for robust scripts.",
        "Not using local for function variables (pollutes global scope). Forgetting to make scripts executable with chmod +x."),
    12: ("useradd -m -s /bin/bash -u UID -G groups user, usermod -aG group user, userdel -r user, passwd, chage",
        "User management is directly tested. Know: useradd (create), usermod (modify), userdel (delete). The -m flag creates home dir — ALWAYS use it.",
        "Using usermod -G instead of -aG (removes from all other groups!). Forgetting -m with useradd."),
    13: ("groupadd -g GID name, groupmod, groupdel, usermod -aG group user, gpasswd, newgrp, /etc/group",
        "Group management controls access. LFCS tests creating groups, adding users, and understanding primary vs supplementary groups.",
        "Confusing primary group (in /etc/passwd) with supplementary groups (in /etc/group). Not using -a with usermod -G."),
    14: ("chage -l user, chage -M 90 -W 7 user, passwd -l/-u user, ulimit -n/-u, /etc/security/limits.conf, pam_tally2",
        "Password policies and resource limits protect systems. LFCS tests chage for aging, ulimit for limits, and basic PAM concepts.",
        "Setting password policies but not verifying with chage -l. Forgetting that ulimit changes only affect the current shell."),
    15: ("ps aux, ps -ef, top, htop, kill -l, kill -9 PID, pkill -f pattern, pgrep, pidof, /proc/PID/",
        "Process management is tested in every exam scenario. Know how to find, monitor, and terminate processes. pkill is safer than kill -9.",
        "Using kill -9 as first resort instead of kill -15 (SIGTERM allows cleanup). Killing the wrong process due to similar names."),
    16: ("systemctl start/stop/restart/status/enable/disable/is-active/is-enabled, systemctl daemon-reload, systemctl list-units",
        "systemd is the init system on ALL modern Linux distros. Every LFCS task involving services uses systemctl. Know start/stop/enable/disable cold.",
        "Forgetting systemctl daemon-reload after creating/modifying unit files. Using start without enable (doesn't survive reboot)."),
    17: ("journalctl -u unit -n 50 -f --since '1 hour ago', /var/log/syslog, /var/log/messages, logger, logrotate, /etc/logrotate.d/",
        "Logging is essential for troubleshooting. LFCS tests journalctl for systemd services and traditional log files for older services.",
        "Not knowing how to filter journalctl by time or unit. Forgetting that rsyslog handles traditional logs while journald handles systemd services."),
    18: ("ip addr, ip link, ip route, ss -tlnp, ping -c 4, traceroute, mtr, /etc/hosts, /etc/resolv.conf, /etc/nsswitch.conf",
        "Networking is 25% of the exam. Master ip (replaces ifconfig), ss (replaces netstat), and understand DNS resolution order.",
        "Using deprecated commands (ifconfig, netstat, route) instead of modern ip/ss. Not knowing /etc/nsswitch.conf controls resolution order."),
    19: ("netplan (Ubuntu): /etc/netplan/*.yaml, netplan apply. nmcli/nmtui (Rocky): nmcli con show, nmcli con mod, nmcli con up",
        "LFCS tests TWO network configuration systems. Ubuntu uses netplan (YAML), Rocky uses NetworkManager (nmcli). Know both!",
        "Editing netplan YAML with wrong indentation. Forgetting netplan apply after changes. Using wrong tool for the distro."),
    20: ("dig domain ANY +short, host domain, nslookup domain, /etc/hosts, /etc/resolv.conf, systemd-resolve --status, resolvectl",
        "DNS troubleshooting is critical. Know dig for detailed queries and how /etc/hosts overrides DNS. systemd-resolved is the modern resolver.",
        "Editing /etc/resolv.conf directly (gets overwritten by NetworkManager/systemd-resolved). Not knowing nsswitch.conf order."),
    21: ("ufw enable/disable/status/allow/deny (Ubuntu). firewall-cmd --add-port/--add-service --permanent, firewall-cmd --reload (Rocky)",
        "Firewall configuration is tested on BOTH distros. Ubuntu=UFW (simple), Rocky=firewalld (zones). Know which to use and make rules persistent.",
        "Using iptables directly (rules don't survive reboot unless saved). Forgetting --permanent with firewall-cmd."),
    22: ("lsblk, fdisk -l, gdisk -l, parted -l, mkfs.ext4, mkfs.xfs, blkid, partprobe, wipefs",
        "Disk partitioning is fundamental. LFCS tests creating partitions, formatting them, and understanding GPT vs MBR. Know fdisk (MBR) and gdisk (GPT).",
        "Writing to the wrong disk (/dev/sda instead of /dev/sdb). Forgetting to run partprobe after partition changes."),
    23: ("mount /dev/sdX /mnt, umount /mnt, mount -a, /etc/fstab format, df -hT, du -sh, fsck, tune2fs, xfs_repair",
        "Filesystem management is directly tested. Know fstab format (6 fields), mount options (defaults, noatime, _netdev), and how to check/repair filesystems.",
        "Editing fstab without testing with mount -a (unbootable system if there's a typo). Forgetting the dump and pass fields in fstab."),
    24: ("pvcreate, vgcreate, lvcreate -L SIZE -n name vg, lvextend -L +SIZE /dev/vg/lv, resize2fs, xfs_growfs, pvs, vgs, lvs",
        "LVM provides flexible storage. LFCS tests creating PVs, VGs, and LVs, then extending them online. Master the PV→VG→LV hierarchy.",
        "Extending LV but forgetting to resize the filesystem (resize2fs for ext4, xfs_growfs for XFS). Running out of space in VG."),
    25: ("swapon, swapoff, mkswap, /etc/fstab swap entry, NFS mount, mount -t nfs server:/path /mnt, showmount -e server, exportfs",
        "Swap and NFS are tested. Know how to create/activate swap and configure NFS mounts. autofs (Ch42) automates NFS mounting.",
        "Forgetting _netdev option for NFS in fstab (mount fails at boot if network isn't ready). Not setting proper NFS export permissions."),
    26: ("ssh-keygen -t ed25519, ssh-copy-id user@host, ssh user@host, /etc/ssh/sshd_config, sshd -t, systemctl reload sshd",
        "SSH is the primary remote administration tool. LFCS tests key generation, key-based auth setup, and server hardening. ALWAYS test config with sshd -t.",
        "Locking yourself out by misconfiguring SSH. Always keep a second terminal open when editing sshd_config."),
    27: ("apt install nginx, /etc/nginx/sites-available/, ln -s to sites-enabled/, nginx -t, systemctl reload nginx",
        "Nginx is a high-performance web server. LFCS tests virtual host configuration, reverse proxy setup, and static file serving.",
        "Forgetting to symlink from sites-available to sites-enabled. Not testing config with nginx -t before reloading."),
    28: ("apt install postgresql, sudo -u postgres psql, CREATE DATABASE, CREATE USER, GRANT, pg_hba.conf, pg_dump, pg_restore",
        "PostgreSQL is the database for anihpj. LFCS tests basic setup, user/database creation, and backup/restore operations.",
        "Forgetting to configure pg_hba.conf for network access. Using trust authentication in production (no password required!)."),
    29: ("timedatectl set-timezone, chronyc sources, ntpq -p, /etc/chrony.conf, date, hwclock, postfix, mailq, mail",
        "Time sync and email are basic services. Know NTP/Chrony for time and basic Postfix configuration for system emails.",
        "Timezone set incorrectly causing log timestamps to be wrong. NTP not running causing clock drift."),
    30: ("systemctl enable --now anihpj gunicorn celery nginx postgresql, ufw allow 8000/tcp, certbot, logrotate, rsync",
        "The full anihpj production stack combines SSH, Nginx, PostgreSQL, Gunicorn, and Celery. LFCS tests your ability to integrate multiple services.",
        "Services not enabled (survive reboot). Firewall blocking application ports. SSL certificate expiration not monitored."),
}

# Build a generic enrichment for chapters without specific data
def get_generic(ch_num):
    return (
        "Review the chapter's command table and practice all listed commands.",
        f"Chapter {ch_num} covers essential LFCS topics. Focus on the hands-on exercises and practice questions at the end of the chapter.",
        "Skipping the practice questions. Hands-on experience is the only way to pass the LFCS exam."
    )

# Process each chapter
added = 0
for ch_num in range(1, 46):
    cmds, focus, mistake = enrichments.get(ch_num, get_generic(ch_num))
    
    enrichment_html = f'''
        <div class="lfcs-exam-tip" style="margin:16px 0;">
            <h5>🎯 LFCS Exam Preparation — Chapter {ch_num} Quick Reference</h5>
            <p><strong>⌨️ Key Commands:</strong> <code>{cmds}</code></p>
            <p><strong>📋 Exam Focus:</strong> {focus}</p>
            <p><strong>⚠️ Common Mistake:</strong> {mistake}</p>
        </div>'''
    
    # Find the chapter's learning-objectives end and insert after it
    # Pattern: after </div> of learning-objectives, before the first <div class="section-block"
    chapter_pattern = re.compile(
        rf'(<div id="ch{ch_num}">.*?<div class="learning-objectives">.*?</div>)',
        re.DOTALL
    )
    
    match = chapter_pattern.search(content)
    if not match:
        print(f"  Ch{ch_num}: learning-objectives not found, skipping")
        continue
    
    # Check if enrichment already exists
    if 'LFCS Exam Preparation' in match.group(0):
        continue
    
    # Insert enrichment after learning-objectives
    old_block = match.group(1)
    new_block = old_block + '\n' + enrichment_html
    content = content.replace(old_block, new_block, 1)
    added += 1

print(f"Added exam prep enrichments to {added}/45 chapters")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"File updated successfully")
