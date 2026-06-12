import re
c=open(r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\lfcs.html','r',encoding='utf-8').read()
answers=re.findall(r'<div class="eq-answer">(.*?)</div>', c, re.DOTALL)
print(f'Total answers: {len(answers)}')
for i,a in enumerate(answers[:3]):
    # Extract code from pre blocks
    codes = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', a, re.DOTALL)
    plain = re.findall(r'<p>(.*?)</p>', a, re.DOTALL)
    print(f'--- Answer {i+1} ---')
    if codes:
        print(f'Code: {codes[0][:150]}')
    if plain:
        print(f'Text: {plain[0][:150]}')
    print()
