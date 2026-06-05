import re
fp = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

issues = 0

for tag in ['article','section','div','pre','code','h3','h4','h5','ul','li','span','strong','p','table','thead','tbody','tr','td','th']:
    o = len(re.findall(f'<{tag}[ >]', c))
    cl = len(re.findall(f'</{tag}>', c))
    if o != cl:
        print(f'  ⚠ <{tag}> {o}/{cl}')
        issues += 1

nav = c[c.find('<nav'):c.find('</nav>')]
hrefs = re.findall(r'href="#([^"]+)"', nav)
main = c[c.find('<main'):]
ids = set(re.findall(r'id="([^"]+)"', main))
broken = [h for h in hrefs if h not in ids]
if broken:
    print(f'  ⚠ {len(broken)} broken anchors')
    issues += 1

mids = re.findall(r'id="([^"]+)"', main)
dups = {i for i in mids if mids.count(i) > 1}
if dups:
    print(f'  ⚠ Duplicate IDs: {sorted(dups)}')
    issues += 1

arts = c.split('<article')
below5 = sum(1 for ch in arts[1:] if (e:=ch.find('</article>'))!=-1 and ch[:e].count('<div class="example">')<5)
no_params = sum(1 for ch in arts[1:] if (e:=ch.find('</article>'))!=-1 and '<h4>Parameters</h4>' not in ch[:e])
no_return = sum(1 for ch in arts[1:] if (e:=ch.find('</article>'))!=-1 and '<h4>Return Value</h4>' not in ch[:e])
no_ctx = sum(1 for ch in arts[1:] if (e:=ch.find('</article>'))!=-1 and '📁 Context' not in ch[:e] and '📄 Context' not in ch[:e])
no_tip = sum(1 for ch in arts[1:] if (e:=ch.find('</article>'))!=-1 and '💡 LFCS Exam Tip' not in ch[:e])

for label, val in [('Below 5 ex',below5),('No Params',no_params),('No Return',no_return),('No Context',no_ctx),('No Tip',no_tip)]:
    if val:
        print(f'  ⚠ {label}: {val}')
        issues += 1

total = len(arts)-1
snips = c.count('📁 Directory Snippet')
ex_total = sum(ch[:ch.find('</article>')].count('<div class="example">') for ch in arts[1:] if ch.find('</article>')!=-1)

print()
print('=' * 50)
print(f'  Lines: {len(c.split(chr(10)))} | Articles: {total}')
print(f'  Sections: {c.count("<section")}/{c.count("</section>")}')
print(f'  Tags: {c.count("<article")}/{c.count("</article>")}')
print(f'  Sidebar: {len(hrefs)} links | Snippets: {snips} | Examples: {ex_total}')
if issues:
    print(f'\n  ⚠ {issues} issues found')
else:
    print('\n  ✅ ZERO ISSUES — DOCUMENT IS CLEAN')
