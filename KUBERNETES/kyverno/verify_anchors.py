import re
fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

nav_start = c.find('<nav class="toc-sidebar"')
nav_end = c.find('</nav>', nav_start)
sidebar = c[nav_start:nav_end]
sidebar_hrefs = re.findall(r'href="#([^"]+)"', sidebar)

main_start = c.find('<main')
main_end = c.find('</main>', main_start)
main_content = c[main_start:main_end]
article_ids = set(re.findall(r'id="([^"]+)"', main_content))

broken = []
for href in sidebar_hrefs:
    if href not in article_ids:
        broken.append(href)

if broken:
    print(f'BROKEN ANCHORS ({len(broken)}):')
    for b in broken:
        print(f'   #{b}')
else:
    print(f'All {len(sidebar_hrefs)} sidebar anchors valid')

open_articles = len(re.findall(r'<article\b', c))
close_articles = len(re.findall(r'</article>', c))
open_divs = len(re.findall(r'<div\b', c))
close_divs = len(re.findall(r'</div>', c))
open_sections = len(re.findall(r'<section\b', c))
close_sections = len(re.findall(r'</section>', c))

print(f'<article>: {open_articles} open, {close_articles} close {"OK" if open_articles==close_articles else "MISMATCH"}')
print(f'<div>: {open_divs} open, {close_divs} close {"OK" if open_divs==close_divs else "MISMATCH"}')
print(f'<section>: {open_sections} open, {close_sections} close {"OK" if open_sections==close_sections else "MISMATCH"}')
print(f'Total: {len(c):,} chars, ~{c.count(chr(10)):,} lines')
