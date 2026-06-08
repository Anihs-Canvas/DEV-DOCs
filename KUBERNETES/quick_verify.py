import re
html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()
for i in range(1,21):
    pat = r'<div\s+id="ch{}"'.format(i)
    if re.search(pat, html):
        print("Ch{}: OK".format(i))
    else:
        # Check if id exists at all
        pos = html.find('id="ch{}"'.format(i))
        if pos >= 0:
            ctx = html[max(0,pos-20):pos+20]
            print("Ch{}: BROKEN - context: ...{}...".format(i, repr(ctx)))
        else:
            print("Ch{}: NOT FOUND".format(i))
