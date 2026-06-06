import re
c = open('systemd_cli.html', 'r', encoding='utf-8').read()
sec = c.split('id="systemctl-section"')[1].split('id="systemctl-advanced"')[0]
ng = sec.count('nginx')
kb = sec.count('kubelet')
ex = sec.count('class="example"')
ar = sec.count('<article class=')
print(f'nginx: {ng}, kubelet: {kb}, examples: {ex}, articles: {ar}')
for t in re.findall(r'<h5>(Example \d+.*?)</h5>', sec):
    print(f'  {t}')
