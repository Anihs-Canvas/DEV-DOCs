import re

with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html','r',encoding='utf-8') as f:
    html = f.read()

# Shell section
sh_start = html.find('id="shell-scripting"')
sh_end = html.find('</section>', sh_start)
sh_html = html[sh_start:sh_end]

# Structural check: echo vs ls
ls_start = html.find('id="ls"'); ls_end = html.find('id="cd"', ls_start)
ls_html = html[ls_start:ls_end]
echo_start = html.find('id="echo"'); echo_end = html.find('id="printf"', echo_start)
echo_html = html[echo_start:echo_end]

checks = [('<h3>','h3'),('api-meta','meta'),('api-subtitle','subtitle'),('api-description','desc'),
          ('syntax-header','syntax'),('param-table','params'),('Return Value','retval'),
          ('📁 Context','context'),('Examples</h4>','examples'),('class="example"','blocks'),
          ('Scenario:','scenario'),('Command:','command'),('example-output','output'),
          ('📝 What happened','whathappened'),('💡 LFCS Exam Tip','tip')]
print("=== STRUCTURAL: ls vs echo ===")
for p,n in checks:
    ls_ok = p in ls_html; ec_ok = p in echo_html
    s = '✅' if ls_ok==ec_ok else '⚠️'
    print(f"  {n:18s} ls:{'✅' if ls_ok else '❌'} echo:{'✅' if ec_ok else '❌'} {s}")

# Tag balance
print(f"\n=== TAGS ===")
print(f"Sections: {html.count('<section')}/{html.count('</section>')}")
print(f"Articles: {html.count('<article')}/{html.count('</article>')}")

# Shell stats
ids = [a for a in re.findall(r'id="([^"]+)"', sh_html) if a != 'shell-scripting']
print(f"\n=== SHELL & SCRIPTING ===")
print(f"Articles: {len(ids)}")
print(f"Context: {sh_html.count('📁 Context')}, Tips: {sh_html.count('💡 LFCS Exam Tip')}")
print(f"Examples: {sh_html.count('class=\"example\"')}")

# Sidebar
sidebar = html[html.find('<aside'):html.find('</aside>')]
links = re.findall(r'href="#([^"]+)"', sidebar)
all_ids = set(re.findall(r'id="([^"]+)"', html))
missing = [l for l in links if l not in all_ids]
print(f"\nAnchors: {len(links)} links, {len(missing)} missing")
if missing:
    for m in missing: print(f"  ❌ {m}")

# .txt echo features
echo_features = ['echo -n', 'echo -e', 'echo "']
print("\n=== .txt echo features ===")
for f in echo_features:
    print(f"  {f:15s}: {'✅' if f in sh_html else '❌'}")

print(f"\nLines: {len(html.splitlines())}")
