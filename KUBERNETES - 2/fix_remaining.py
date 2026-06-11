import re

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "r", encoding="utf-8") as f:
    content = f.read()

# Strategy: find every </details> that comes after an exam-question-item but is NOT preceded by eq-explanation
# Use a simpler approach: find all </details> and check backwards

count_before = content.count("eq-explanation")

# Find all positions of '</details>'
positions = [m.end() for m in re.finditer(r'</details>', content)]
fixed = 0

for pos in positions:
    # Look back 3000 chars to find the start of this question
    lookback = content[max(0, pos-3000):pos]
    # Check if this </details> is preceded by exam-question-item
    if 'exam-question-item' not in lookback[-300:]:
        continue
    # Check if explanation already exists
    if 'eq-explanation' in lookback[-600:]:
        continue
    
    # This question needs an explanation
    # Extract question text from lookback
    qmatch = re.search(r'<div class="eq-question">(.*?)</div>', lookback, re.DOTALL)
    if qmatch:
        question = qmatch.group(1).strip()
        # Generate explanation
        if 'mkdir' in question.lower() or 'directory' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> <code>mkdir -p</code> creates parent directories as needed. Always verify with <code>ls -ld /path</code> after creating directories. For the LFCS exam, remember to set both the directory structure AND correct permissions.</p></div>'
        elif 'user' in question.lower() or 'group' in question.lower() or 'permission' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> User/group management is a fundamental LFCS skill. Remember: <code>useradd -m</code> for home dir, <code>usermod -aG</code> to append groups, <code>chmod</code> for permissions, <code>chown</code> for ownership. Always verify with <code>id username</code> or <code>ls -l file</code>.</p></div>'
        elif 'find' in question.lower() or 'grep' in question.lower() or 'search' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> Search and filter commands are essential for LFCS. <code>find</code> locates files by name/type/time and can execute actions with <code>-exec</code>. <code>grep -rin</code> searches recursively with case-insensitive matching and line numbers. Master these for log analysis and system troubleshooting.</p></div>'
        elif 'disk' in question.lower() or 'storage' in question.lower() or 'mount' in question.lower() or 'fstab' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> Storage management is tested on LFCS. Remember: <code>lsblk</code> to see devices, <code>mkfs.ext4</code> to format, <code>mount</code> to attach, <code>/etc/fstab</code> for persistence. ALWAYS test with <code>mount -a</code> after editing fstab — a typo makes the system unbootable.</p></div>'
        elif 'network' in question.lower() or 'ip ' in question.lower() or 'firewall' in question.lower() or 'ufw' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> Networking is 25% of the LFCS exam. Know: <code>ip addr/route/link</code> for configuration, <code>ss -tlnp</code> for port checking, <code>ufw</code> for Ubuntu firewalls, <code>firewall-cmd</code> for Rocky/RHEL. Persistence requires editing netplan or NetworkManager configs.</p></div>'
        elif 'systemd' in question.lower() or 'service' in question.lower() or 'systemctl' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> systemd service management is critical. <code>systemctl start/stop</code> for immediate control, <code>enable/disable</code> for boot behavior. ALWAYS run <code>systemctl daemon-reload</code> after creating or modifying unit files. Verify with <code>systemctl status service</code>.</p></div>'
        elif 'ssh' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> SSH configuration: edit <code>/etc/ssh/sshd_config</code>, then ALWAYS run <code>sshd -t</code> to test syntax before applying. <code>systemctl reload sshd</code> applies changes without dropping existing connections. Key security: disable root login, disable password auth, use key-based auth only.</p></div>'
        elif 'cron' in question.lower() or 'schedule' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> Cron format: minute hour day-of-month month day-of-week command. Use <code>/etc/cron.d/</code> for system jobs (includes username field). Shortcuts: @daily, @hourly, @weekly, @monthly, @reboot. Verify with <code>crontab -l</code> or check <code>/var/log/syslog</code> for cron execution.</p></div>'
        elif 'git' in question.lower():
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> Git workflow: <code>clone</code> to download, <code>add</code> to stage, <code>commit</code> to save, <code>push</code> to upload. <code>git log --oneline</code> shows history. <code>git checkout -- file</code> reverts uncommitted changes. Always verify with <code>git status</code> before and after operations.</p></div>'
        else:
            expl = '<div class="eq-explanation"><div class="eq-exp-label">📖 Explanation</div><p><strong>💡 Explanation:</strong> This is a key LFCS concept. Practice this task repeatedly until you can execute it from memory within 2-3 minutes. The exam tests both correctness and speed — you should be able to complete most tasks without consulting documentation.</p></div>'
        
        # Insert before </details>
        insertion_point = pos - 11  # Position just before '</details>'
        content = content[:insertion_point] + '\n                    ' + expl + '\n                ' + content[insertion_point:]
        fixed += 1

count_after = content.count("eq-explanation")
print(f"Explanations before: {count_before}")
print(f"Explanations after: {count_after}")
print(f"Fixed: {fixed}")

with open(r"c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html", "w", encoding="utf-8") as f:
    f.write(content)
