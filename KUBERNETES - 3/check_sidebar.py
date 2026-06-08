import re

with open('Terraform_pro.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

with open('Terraform_pro.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all section headers in .txt (e.g., "    14.1  Public Registry...")
txt_sections = re.findall(r' {4}(\d+\.\d+[a-z]?)\s+(.*)', txt)

# Group by chapter
from collections import defaultdict
chapters = defaultdict(list)
for num, title in txt_sections:
    ch = num.split('.')[0]
    chapters[ch].append((num, title.strip()))

# Find which chapters have sub-toc in sidebar
sidebar = html[html.find('<!-- SIDEBAR -->'):html.find('</nav>')]
sidebar_subs = set(re.findall(r'id="sub-ch(\d+)"', sidebar))

print("Chapters with sub-sections in .txt:")
for ch in sorted(chapters.keys(), key=int):
    has_toggle = ch in sidebar_subs
    status = "✅" if has_toggle else "❌ MISSING"
    print(f"  Ch {ch}: {len(chapters[ch])} sections {status}")
    if not has_toggle:
        for num, title in chapters[ch]:
            print(f"    - {num} {title}")
