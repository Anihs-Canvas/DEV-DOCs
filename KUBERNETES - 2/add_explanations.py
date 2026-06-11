#!/usr/bin/env python3
"""Add explanations to LFCS practice questions that lack them."""
import re, sys

filepath = r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find questions without explanations
# Look for: </div></details></div> (end of answer without explanation before it)
# The pattern: an exam-question-item that has an answer but no explanation

# Simpler approach: find all </pre> or </p> just before </div></details></div>
# that are inside exam-question-item but NOT preceded by eq-explanation

def add_explanation(match):
    full_match = match.group(0)
    # Extract question text and answer
    q_match = re.search(r'<div class="eq-question">(.*?)</div>', full_match, re.DOTALL)
    a_match = re.search(r'<div class="eq-answer">(.*?)</div>', full_match, re.DOTALL)
    
    if not q_match or not a_match:
        return full_match
    
    question = q_match.group(1).strip()
    answer = a_match.group(1).strip()
    
    # Skip if already has explanation
    if 'eq-explanation' in full_match:
        return full_match
    
    # Generate a brief explanation based on the answer content
    # Extract key command from answer
    cmd_match = re.search(r'<code>(.*?)</code>', answer)
    if cmd_match:
        cmd = cmd_match.group(1)
        cmd_words = cmd.split()
        if cmd_words:
            main_cmd = cmd_words[0].strip()
            # Generate context-aware explanation
            if 'useradd' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>useradd</code> creates a new user account. Key flags: <code>-m</code> creates the home directory, <code>-s</code> sets the login shell, <code>-u</code> specifies UID, <code>-G</code> adds supplementary groups. Always verify with <code>id username</code> afterwards.</p>'
            elif 'usermod' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>usermod</code> modifies an existing user. The critical flag is <code>-aG</code> (append to group) — using <code>-G</code> alone REMOVES the user from all other groups. Always use <code>-aG</code> together.</p>'
            elif 'groupadd' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>groupadd</code> creates a new group. Use <code>-g</code> to specify the GID. Groups are defined in <code>/etc/group</code>. Verify with <code>getent group groupname</code>.</p>'
            elif 'chmod' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>chmod</code> changes file permissions. Octals: 4=read, 2=write, 1=execute. Common: 755 (rwxr-xr-x) for dirs, 644 (rw-r--r--) for files, 600 (rw-------) for secrets. Use <code>chmod -R</code> for recursive.</p>'
            elif 'chown' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>chown</code> changes file ownership. Format: <code>user:group</code>. Use <code>-R</code> for recursive. Only root can change ownership. Verify with <code>ls -l file</code>.</p>'
            elif 'passwd' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>passwd</code> manages passwords. Without arguments, changes your own password. With a username, changes that user\'s password (requires root). <code>-l</code> locks, <code>-u</code> unlocks, <code>-e</code> expires (forces change on next login).</p>'
            elif 'chage' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>chage</code> manages password aging. <code>-M</code> sets maximum days, <code>-W</code> sets warning days, <code>-I</code> sets inactive days before lock. Use <code>chage -l username</code> to view current policy.</p>'
            elif 'sudo' in cmd or 'visudo' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>visudo</code> safely edits <code>/etc/sudoers</code> with syntax validation. Format: <code>USER HOST=(RUNAS) TAGS: COMMAND</code>. Use <code>NOPASSWD:</code> for passwordless sudo. Always use <code>visudo -c</code> to check syntax.</p>'
            elif 'setfacl' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>setfacl</code> manages Access Control Lists. <code>-m</code> modifies, <code>-x</code> removes, <code>-b</code> removes all. Format: <code>u:user:perms</code> or <code>g:group:perms</code>. Files with ACLs show <code>+</code> in <code>ls -l</code> output.</p>'
            elif 'find' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>find</code> searches for files. <code>-name</code> matches by name, <code>-type f/d</code> filters by type, <code>-mtime -N</code> finds files modified within N days. <code>-exec</code> runs a command on each match. Always quote wildcards to prevent shell expansion.</p>'
            elif 'grep' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>grep</code> searches text using patterns. <code>-r</code> searches recursively, <code>-i</code> ignores case, <code>-n</code> shows line numbers, <code>-v</code> inverts match. Combine: <code>grep -rin "error" /var/log/</code> is the sysadmin\'s best friend.</p>'
            elif 'sed' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>sed</code> is a stream editor. <code>-i</code> edits files in-place. <code>s/old/new/g</code> substitutes all occurrences. Without <code>-i</code>, output goes to stdout (dry-run safe). Always backup before using <code>-i</code>.</p>'
            elif 'awk' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>awk</code> processes text by columns. <code>$1</code> is the first field, <code>$NF</code> is the last. <code>-F</code> sets the field separator. Perfect for parsing structured output like logs and config files.</p>'
            elif 'tar' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>tar</code> archives files. <code>-c</code> creates, <code>-x</code> extracts, <code>-z</code> uses gzip, <code>-j</code> uses bzip2, <code>-f</code> specifies filename. <code>-v</code> shows progress. Remember: <code>tar -czf</code> (create) and <code>tar -xzf</code> (extract).</p>'
            elif 'rsync' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>rsync</code> efficiently syncs files using delta transfer (only changed parts are sent). <code>-a</code> archives (preserves everything), <code>-v</code> verbose, <code>-z</code> compresses. Trailing <code>/</code> matters: <code>src/</code> copies contents, <code>src</code> copies the directory.</p>'
            elif 'systemctl' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>systemctl</code> manages systemd services. <code>start</code>/<code>stop</code> controls current state. <code>enable</code>/<code>disable</code> controls boot behavior. <code>--now</code> combines start+enable in one command. Always run <code>systemctl daemon-reload</code> after editing unit files.</p>'
            elif 'journalctl' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>journalctl</code> queries the systemd journal. <code>-u</code> filters by unit, <code>-n N</code> shows last N lines, <code>-f</code> follows (like tail -f), <code>--since "10 min ago"</code> filters by time. Logs are binary and indexed — much faster than grep on text files.</p>'
            elif 'ps' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>ps</code> shows running processes. <code>aux</code> shows all users\' processes in BSD format. <code>-ef</code> shows full listing in standard format. Pipe through <code>grep</code> to find specific processes. <code>ps --forest</code> shows parent-child relationships.</p>'
            elif 'kill' in cmd or 'pkill' in cmd or 'renice' in cmd or 'nice' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Process signals: <code>SIGTERM</code> (15, graceful) is the default. <code>SIGKILL</code> (9) forces termination. <code>SIGHUP</code> (1) reloads config. <code>pkill -f pattern</code> matches by command name. <code>nice</code> sets priority (-20 highest, 19 lowest).</p>'
            elif 'ip ' in cmd or 'ss ' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>ip</code> replaces ifconfig/route/arp. <code>ip addr</code> shows IPs, <code>ip route</code> shows routing, <code>ip link</code> shows interfaces. <code>ss</code> replaces netstat — <code>ss -tlnp</code> shows listening TCP ports with process names.</p>'
            elif 'ufw' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>ufw</code> (Uncomplicated FireWall) is Ubuntu\'s firewall frontend. Rules are persistent across reboots. <code>ufw enable</code> activates, <code>ufw status numbered</code> shows rules. Default: deny incoming, allow outgoing.</p>'
            elif 'netplan' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Netplan is Ubuntu\'s network configuration system. Config files are YAML in <code>/etc/netplan/</code>. <code>netplan apply</code> applies changes immediately. Always validate YAML syntax — a single indentation error breaks networking.</p>'
            elif 'mount' in cmd or 'fstab' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>mount</code> attaches a filesystem to the directory tree. <code>/etc/fstab</code> defines persistent mounts. Format: device, mountpoint, type, options, dump, pass. Always run <code>mount -a</code> after editing fstab to verify syntax before rebooting.</p>'
            elif 'mkfs' in cmd or 'fdisk' in cmd or 'lsblk' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Disk management: <code>lsblk</code> lists block devices. <code>fdisk -l</code> shows partitions. <code>mkfs.ext4 /dev/sdb1</code> creates a filesystem. Always double-check the device name — writing to the wrong disk destroys data.</p>'
            elif 'lvm' in cmd or 'lvcreate' in cmd or 'lvextend' in cmd or 'pvcreate' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> LVM provides flexible disk management. Three layers: PV (physical volume) → VG (volume group) → LV (logical volume). <code>lvextend -L +SIZE /dev/vg/lv && resize2fs /dev/vg/lv</code> extends both the LV and filesystem online.</p>'
            elif 'df' in cmd or 'du' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> <code>df -hT</code> shows filesystem disk usage with type. <code>du -sh /dir/*</code> shows directory sizes sorted. <code>df -i</code> shows inode usage — running out of inodes prevents new files even with free space.</p>'
            elif 'ping' in cmd or 'dig' in cmd or 'curl' in cmd or 'nc' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Network diagnostics: <code>ping -c 4 host</code> tests connectivity. <code>dig domain ANY +short</code> queries DNS. <code>curl -I URL</code> checks HTTP headers. <code>nc -zv host port</code> tests if a TCP port is open.</p>'
            elif 'git' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Git workflow: <code>clone</code> downloads, <code>add</code> stages changes, <code>commit</code> saves a snapshot, <code>push</code> uploads to remote. <code>git log --oneline</code> shows history. <code>git checkout -- file</code> reverts uncommitted changes.</p>'
            elif 'podman' in cmd or 'docker' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Container commands: <code>pull</code> downloads images, <code>run -d --name X -p H:C image</code> starts a container, <code>ps</code> lists running containers, <code>stop/rm</code> stops and removes. Podman is daemonless and rootless — more secure than Docker.</p>'
            elif 'virsh' in cmd or 'virt-install' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> libvirt commands: <code>virsh list --all</code> shows all VMs. <code>virsh start/shutdown/destroy</code> controls VM state. <code>virt-install</code> creates VMs from CLI. VMs are defined as XML files in <code>/etc/libvirt/qemu/</code>.</p>'
            elif 'cron' in cmd or 'crontab' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Cron runs scheduled tasks. Format: minute hour day-of-month month day-of-week command. <code>/etc/cron.d/</code> is preferred for system jobs (includes username field). Use <code>@daily</code>, <code>@hourly</code>, <code>@reboot</code> shortcuts.</p>'
            elif 'ssh' in cmd or 'sshd' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> SSH configuration: Edit <code>/etc/ssh/sshd_config</code> for server settings. ALWAYS run <code>sshd -t</code> to test syntax before reloading. <code>systemctl reload sshd</code> applies changes without dropping connections.</p>'
            elif 'nginx' in cmd:
                expl = f'<p><strong>💡 Explanation:</strong> Nginx is a high-performance web server and reverse proxy. Config files in <code>/etc/nginx/sites-available/</code>, enabled via symlink to <code>sites-enabled/</code>. Always run <code>nginx -t</code> to test config before reloading.</p>'
            else:
                expl = f'<p><strong>💡 Explanation:</strong> This command performs a key Linux administration task. Practice it repeatedly until you can type it from memory — the LFCS exam has limited time and no autocomplete. Verify your work after every task.</p>'
        else:
            expl = '<p><strong>💡 Explanation:</strong> This is an essential concept for LFCS. Understanding the theory behind this task is as important as executing it correctly. Review the relevant chapter section if this was unclear.</p>'
    else:
        expl = '<p><strong>💡 Explanation:</strong> Understanding this concept is critical for the LFCS exam. Practice the associated commands until they become muscle memory. Review the chapter content if you struggled with this question.</p>'
    
    # Insert explanation before the closing </div> of the answer
    expl_block = f'\n                    <div class="eq-explanation">\n                        <div class="eq-exp-label">📖 Explanation</div>\n                        {expl}\n                    </div>\n                '
    
    # Insert before </details>
    new_text = full_match.replace('</details>', expl_block + '</details>', 1)
    return new_text

# Find all exam-question-item blocks
pattern = r'<div class="exam-question-item">.*?</details>\s*</div>'
result = re.sub(pattern, add_explanation, content, flags=re.DOTALL)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(result)

# Count results
old_count = len(re.findall(r'eq-explanation', content))
new_count = len(re.findall(r'eq-explanation', result))
print(f"Explanations before: {old_count}")
print(f"Explanations after: {new_count}")
print(f"Added: {new_count - old_count} explanations")
