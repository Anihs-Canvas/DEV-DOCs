#!/usr/bin/env python3
"""Deep audit of explanation quality gaps."""
import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Count explanations with diagrams
diagrams_in_exp = len(re.findall(r'eq-explanation.*?diagram-container', c, re.DOTALL))
print(f'Explanations with diagrams: {diagrams_in_exp}')

# Explanation lengths
exp_texts = re.findall(r'eq-exp-label.*?Explanation</div>\s*<p>(.*?)</p>', c, re.DOTALL)
lengths = [len(t) for t in exp_texts]
print(f'Total explanations: {len(exp_texts)}')
print(f'Min/Max explanation length: {min(lengths)}/{max(lengths)} chars')
print(f'Avg explanation length: {sum(lengths)//len(lengths)} chars')

# Count short explanations (<200 chars = likely thin)
short = [l for l in lengths if l < 200]
print(f'Short explanations (<200 chars): {len(short)}')

# Check chapter detection accuracy
print('\n--- Chapter Detection Audit ---')
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

mismatches = 0
for ch in range(1, 46):
    pattern = f'Chapter {ch} — LFCS Practice Questions</h4>'
    pos = c.find(pattern)
    if pos == -1: continue
    next_ch = c.find('Chapter ', pos + len(pattern))
    block = c[pos:next_ch] if next_ch > 0 else c[pos:]
    
    # Get ALL explanation topics in this chapter
    topics = re.findall(r'eq-explanation.*?<p><strong>(.*?)</strong>', block, re.DOTALL)
    if not topics:
        print(f'Ch {ch:2d}: NO explanations found!')
        continue
    
    expected = chapter_topics.get(ch, '')
    wrong = [t[:40] for t in topics if not t.startswith(expected)]
    if wrong:
        mismatches += len(wrong)
        print(f'Ch {ch:2d}: ❌ {len(wrong)}/{len(topics)} wrong | expected "{expected}" | got "{wrong[0][:50]}..."')

print(f'\nTotal chapter-topic mismatches: {mismatches}')

# Count diagram containers overall
print(f'\nTotal diagrams: {c.count("diagram-container")}')
print(f'Total exam questions: {c.count("exam-question-item")}')
print(f'File size: {len(c)//1024} KB')
