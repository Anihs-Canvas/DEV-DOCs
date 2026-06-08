html = open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','r',encoding='utf-8').read()

ch21_id = html.find('id="ch21"')
app_a_id = html.find('id="appendix-a"')
ch21 = html[ch21_id:app_a_id]

import re

# Find visual-summary position
vs_match = re.search(r'(<!--[^>]*Visual Summary[^>]*-->\s*)?<div class="visual-summary">.*?</div>\s*</div>\s*</div>', ch21, re.DOTALL)
qa_match = re.search(r'<div class="cka-exam-questions">', ch21)

if vs_match and qa_match:
    vs_start = ch21_id + vs_match.start()
    vs_end = ch21_id + vs_match.end()
    vs_text = html[vs_start:vs_end]
    
    qa_start = ch21_id + qa_match.start()
    
    # Check if visual-summary is AFTER Q&A
    if vs_match.start() > qa_match.start():
        # Remove visual-summary from current position
        html = html[:vs_start] + html[vs_end:]
        app_a_id = html.find('id="appendix-a"')
        
        # Find Q&A again (position may have shifted)
        qa_start2 = html.find('<div class="cka-exam-questions">', ch21_id)
        
        # Insert visual-summary BEFORE Q&A
        html = html[:qa_start2] + vs_text + '\n\n                ' + html[qa_start2:]
        
        with open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\helm.html','w',encoding='utf-8') as f:
            f.write(html)
        print("Ch21: Moved visual-summary before Q&A")
    else:
        print("Ch21: visual-summary already before Q&A")
else:
    print("Ch21: vs_match={}, qa_match={}".format(vs_match is not None, qa_match is not None))
