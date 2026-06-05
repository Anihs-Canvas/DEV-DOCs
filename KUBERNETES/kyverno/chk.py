with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\kyverno\linux_cli.html','r',encoding='utf-8') as f:
    html = f.read()

print(f"Sections: {html.count('<section')}/{html.count('</section>')}")
print(f"Articles: {html.count('<article')}/{html.count('</article>')}")
print(f"Main: {html.count('<main>')}/{html.count('</main>')}")
print(f"Lines: {len(html.splitlines())}")

import re
bad = re.findall(r'/lpj/(apps|data|frontend|src|postgres)[/\"]', html)
print(f"Non-official paths remaining: {bad if bad else 'NONE'}")
