import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
print("Ch21 found:", 'id="ch21"' in html)
print("Total lines:", html.count('\n'))
for i in range(1,22):
    pat = r'<div\s+id="ch{}"'.format(i)
    if re.search(pat, html):
        print("Ch{}: OK".format(i))
    else:
        pos = html.find('id="ch{}"'.format(i))
        if pos >= 0:
            print("Ch{}: BROKEN - context: ...{}...".format(i, html[max(0,pos-15):pos+15]))
        else:
            print("Ch{}: NOT FOUND".format(i))
# Check appendix divs too
for app in ['a','b','c','d','e','f']:
    aid = 'id="appendix-{}"'.format(app)
    pat = r'<div\s+id="appendix-{}"'.format(app)
    if re.search(pat, html):
        print("App{}: OK".format(app.upper()))
    else:
        print("App{}: BROKEN".format(app.upper()))
