import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\helm_cli.html', encoding='utf-8').read()
nav = html[html.find('<nav'):html.find('</nav>')]
links = re.findall(r'href="#([^"]+)"', nav)
print(f"Sidebar links: {len(links)}")
for l in links:
    print(f"  #{l}")
# Count sub-toc blocks
print(f"\nsub-toc blocks: {nav.count('class=\"sub-toc\"')}")
print(f"section-toggle: {nav.count('section-toggle')}")
