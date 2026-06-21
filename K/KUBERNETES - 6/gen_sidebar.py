import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 6\cks.txt', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Parse chapters
chapters = []
current_chapter = None
for line in lines:
    ch_match = re.match(r'^Chapter (\d+):\s*(.+)', line)
    if ch_match:
        if current_chapter:
            chapters.append(current_chapter)
        current_chapter = {'num': ch_match.group(1), 'title': ch_match.group(2).strip(), 'sections': []}
        continue
    sec_match = re.match(r'^\s+(\d+\.\d+)\s+(.+)', line)
    if sec_match and current_chapter:
        current_chapter['sections'].append({'num': sec_match.group(1), 'title': sec_match.group(2).strip()})
if current_chapter:
    chapters.append(current_chapter)

# Parse appendices
appendices = []
current_app = None
for line in lines:
    app_match = re.match(r'^Appendix ([A-G]):\s*(.+)', line)
    if app_match:
        if current_app:
            appendices.append(current_app)
        current_app = {'letter': app_match.group(1), 'title': app_match.group(2).strip(), 'sections': []}
        continue
    sec_match = re.match(r'^\s+([A-G]\.\d+)\s+(.+)', line)
    if sec_match and current_app:
        current_app['sections'].append({'num': sec_match.group(1), 'title': sec_match.group(2).strip()})
if current_app:
    appendices.append(current_app)

# Filter chapters
for ch in chapters:
    ch['sections'] = [s for s in ch['sections'] if s['num'].startswith(ch['num'] + '.')]
chapters = [ch for ch in chapters if ch['num'] != '7']

# Manual Chapter 7
ch7 = {'num': '7', 'title': 'Ingress Security with TLS', 'sections': [
    {'num': '7.1', 'title': 'TLS Certificates in Kubernetes'},
    {'num': '7.2', 'title': 'cert-manager - Automated Certificate Management'},
    {'num': '7.3', 'title': 'Enforcing HTTPS - Redirecting HTTP to HTTPS'},
]}
for i, ch in enumerate(chapters):
    if ch['num'] == '6':
        chapters.insert(i + 1, ch7)
        break

# Part mapping
parts = {
    '1': ('Part 1: Foundation', 'BEGINNER', 'beginner'),
    '2': ('Part 1: Foundation', 'BEGINNER', 'beginner'),
    '3': ('Part 1: Foundation', 'BEGINNER', 'beginner'),
    '4': ('Part 2: Cluster Setup', 'CKS 15%', 'beginner'),
    '5': ('Part 2: Cluster Setup', 'CKS 15%', 'beginner'),
    '6': ('Part 2: Cluster Setup', 'CKS 15%', 'beginner'),
    '7': ('Part 2: Cluster Setup', 'CKS 15%', 'beginner'),
    '8': ('Part 3: Cluster Hardening', 'CKS 15%', 'intermediate'),
    '9': ('Part 3: Cluster Hardening', 'CKS 15%', 'intermediate'),
    '10': ('Part 3: Cluster Hardening', 'CKS 15%', 'intermediate'),
    '11': ('Part 3: Cluster Hardening', 'CKS 15%', 'intermediate'),
    '12': ('Part 3: Cluster Hardening', 'CKS 15%', 'intermediate'),
    '13': ('Part 4: System Hardening', 'CKS 10%', 'intermediate'),
    '14': ('Part 4: System Hardening', 'CKS 10%', 'intermediate'),
    '15': ('Part 4: System Hardening', 'CKS 10%', 'intermediate'),
    '16': ('Part 4: System Hardening', 'CKS 10%', 'intermediate'),
    '17': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '18': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '19': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '20': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '21': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '22': ('Part 5: Microservice Vulnerabilities', 'CKS 20%', 'intermediate'),
    '23': ('Part 6: Supply Chain Security', 'CKS 20%', 'advanced'),
    '24': ('Part 6: Supply Chain Security', 'CKS 20%', 'advanced'),
    '25': ('Part 6: Supply Chain Security', 'CKS 20%', 'advanced'),
    '26': ('Part 6: Supply Chain Security', 'CKS 20%', 'advanced'),
    '27': ('Part 6: Supply Chain Security', 'CKS 20%', 'advanced'),
    '28': ('Part 7: Monitoring and Runtime Security', 'CKS 20%', 'advanced'),
    '29': ('Part 7: Monitoring and Runtime Security', 'CKS 20%', 'advanced'),
    '30': ('Part 7: Monitoring and Runtime Security', 'CKS 20%', 'advanced'),
    '31': ('Part 7: Monitoring and Runtime Security', 'CKS 20%', 'advanced'),
    '32': ('Part 7: Monitoring and Runtime Security', 'CKS 20%', 'advanced'),
    '33': ('Part 8: Hands-On - Securing anihpj', 'PROJECT', 'advanced'),
    '34': ('Part 8: Hands-On - Securing anihpj', 'PROJECT', 'advanced'),
    '35': ('Part 8: Hands-On - Securing anihpj', 'PROJECT', 'advanced'),
    '36': ('Part 9: CKS Exam Preparation', 'EXAM', 'advanced'),
    '37': ('Part 9: CKS Exam Preparation', 'EXAM', 'advanced'),
    '38': ('Part 9: CKS Exam Preparation', 'EXAM', 'advanced'),
}

level_emoji = {'beginner': '🟢 ', 'intermediate': '🟡 ', 'advanced': '🔴 '}

html = []
last_part = None

# Generate chapter sidebar
for ch in chapters:
    part_info = parts.get(ch['num'], ('', '', ''))
    part_name = part_info[0]
    
    if part_name != last_part:
        if last_part is not None:
            html.append('                </ul>')
            html.append('            </li>')
            html.append('')
        badge_class = part_info[2]
        badge_text = part_info[1]
        emoji = level_emoji.get(badge_class, '')
        html.append(f'            <!-- {emoji}{part_name} -->')
        html.append('            <li>')
        html.append(f'                <div class="part-header" onclick="togglePart(this)">')
        html.append(f'                    <div class="part-title"><span>{emoji}{part_name}</span><span class="part-badge {badge_class}">{badge_text}</span></div>')
        html.append('                </div>')
        html.append('                <ul class="chapter-list">')
        last_part = part_name
    
    if ch['sections']:
        html.append('                    <li class="chapter-item">')
        html.append('                        <div class="chapter-row">')
        html.append(f'                            <a href="#ch{ch["num"]}" class="chapter-link"><span class="chapter-number">Ch {ch["num"]}</span>{ch["title"]}</a>')
        html.append(f'                            <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>')
        html.append('                        </div>')
        html.append('                        <ul class="sub-toc">')
        for sec in ch['sections']:
            parts_num = sec['num'].split('.')
            sec_id = f's{parts_num[0]}-{parts_num[1]}'
            html.append(f'                            <li><a href="#{sec_id}">{sec["num"]} {sec["title"]}</a></li>')
        html.append('                        </ul>')
        html.append('                    </li>')
    else:
        html.append(f'                    <li class="chapter-item"><a href="#ch{ch["num"]}" class="chapter-link"><span class="chapter-number">Ch {ch["num"]}</span>{ch["title"]}</a></li>')

if last_part is not None:
    html.append('                </ul>')
    html.append('            </li>')

# Generate appendices sidebar
html.append('')
html.append('            <!-- Appendices -->')
html.append('            <li>')
html.append('                <div class="part-header" onclick="togglePart(this)">')
html.append('                    <div class="part-title"><span>📚 Appendices</span><span class="part-badge">REFERENCE</span></div>')
html.append('                </div>')
html.append('                <ul class="chapter-list">')

for app in appendices:
    letter_lower = app['letter'].lower()
    if app['sections']:
        html.append('                    <li class="chapter-item">')
        html.append('                        <div class="chapter-row">')
        html.append(f'                            <a href="#appendix-{letter_lower}" class="chapter-link"><span class="chapter-number">{app["letter"]}</span>{app["title"]}</a>')
        html.append(f'                            <button class="section-toggle-btn" onclick="toggleSections(this)">▶</button>')
        html.append('                        </div>')
        html.append('                        <ul class="sub-toc">')
        for sec in app['sections']:
            parts_num = sec['num'].split('.')
            sec_id = f's{letter_lower}-{parts_num[1]}'
            html.append(f'                            <li><a href="#{sec_id}">{sec["num"]} {sec["title"]}</a></li>')
        html.append('                        </ul>')
        html.append('                    </li>')
    else:
        html.append(f'                    <li class="chapter-item"><a href="#appendix-{letter_lower}" class="chapter-link"><span class="chapter-number">{app["letter"]}</span>{app["title"]}</a></li>')

html.append('                </ul>')
html.append('            </li>')

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 6\cks_sidebar_full.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))

total_secs = sum(len(c['sections']) for c in chapters)
app_secs = sum(len(a['sections']) for a in appendices)
print(f"Chapters: {len(chapters)} with {total_secs} sections")
print(f"Appendices: {len(appendices)} with {app_secs} sections")
for app in appendices:
    print(f"  Appendix {app['letter']}: {len(app['sections'])} sub-sections - {app['title'][:50]}")