import re
c = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()

expected = {
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

issues = []
ok = 0
for ch in range(1, 46):
    m = re.search(rf'<h4>Chapter {ch} .*? LFCS Practice Questions</h4>(.*?)(?:<h4>Chapter|$)', c, re.DOTALL)
    if not m:
        issues.append(f'Ch {ch:2d}: MISSING practice question header')
        continue
    
    block = m.group(1)
    q_count = block.count('exam-question-item')
    exp_count = block.count('eq-explanation')
    generic = block.count('Understanding this concept is critical')
    
    if q_count == 0:
        issues.append(f'Ch {ch:2d}: NO questions found')
        continue
    
    topics = re.findall(r'eq-explanation.*?<p><strong>(.*?)</strong>', block, re.DOTALL)
    exp_topic = expected.get(ch, '')
    
    wrong_topics = []
    for t in topics:
        t_short = t[:len(exp_topic)]
        if not t.startswith(exp_topic):
            wrong_topics.append(t[:40])
    
    if wrong_topics:
        # Show unique wrong topics
        unique_wrong = list(set(wrong_topics))
        issues.append(f'Ch {ch:2d}: {len(wrong_topics)}/{len(topics)} WRONG topic | expected "{exp_topic}" | got {unique_wrong[:3]}')
    elif generic > 0:
        issues.append(f'Ch {ch:2d}: {generic} GENERIC explanations remaining')
    else:
        ok += 1

print(f'✅ {ok}/45 chapters OK')
print(f'⚠️ {len(issues)} issues:')
for i in issues:
    print(f'  {i}')
print(f'\nTotal questions: {c.count("exam-question-item")}')
print(f'Generic remaining: {c.count("Understanding this concept is critical")}')
